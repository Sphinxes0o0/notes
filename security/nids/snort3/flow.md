# flow 模块 — 流管理

## 概述

`flow` 模块管理所有网络会话的生命周期,包括流缓存查找、创建、过期和删除。

## 文件清单

| 文件 | 行数 | 功能 |
|------|------|------|
| flow.h | 593 | Flow类定义 |
| flow.cc | 450 | Flow实现 |
| flow_key.h / .cc | ~100 / 429 | 流键定义与Hash |
| flow_cache.h | 183 | 流缓存管理 |
| flow_control.cc | 755 | 流控制器 |
| flow_data.cc | 150 | 流数据存储 |
| flow_stash.h | 172 | 流数据暂存 |
| expect_cache.cc | 475 | 预期流缓存 |
| ha.h / .cc | ~175 / 816 | 高可用性状态 |
| dump_flows.h / .cc | 117 / 309 | 流导出 |
| deferred_trust.cc | 76 | 延迟信任 |
| session.h | 126 | 会话接口 |
| prune_stats.h | ~150 | 剪枝统计 |

**flow总计: 约11045行**

## 类层次

```
Flow (会话主体)
├── 协议处理状态
├── 检测状态
├── 高可用性状态
└── 流数据存储(FlowDataStore)

FlowKey (流唯一标识)
├── IP地址 (src/dst, v4/v6)
├── 端口 (src/dst)
├── VLAN / MPLS
├── 租户ID
└── 协议类型

FlowCache (流缓存)
├── ZHash* hash_table      // 哈希表
├── FlowUniList* uni_flows // 单向流列表
└── FlowUniList* uni_ip_flows // 单向IP流

FlowControl (流控制器)
├── 管理所有协议的FlowCache
├── 处理流超时
└── 处理流剪枝

FlowHashKeyOps (Hash运算)
├── do_hash()             // 计算hash
└── key_compare()         // 键比较
```

## FlowKey 结构

```cpp
struct FlowKey {
    uint32_t ip_l[4];    // 较低IP地址 (IPv6)
    uint32_t ip_h[4];    // 较高IP地址 (IPv6)
    uint16_t port_l;      // 较低端口
    uint16_t port_h;      // 较高端口
    uint16_t vlan_tag;    // VLAN标签
    uint32_t mplsLabel;   // MPLS标签
    uint32_t addressSpaceId; // 地址空间ID
#ifndef DISABLE_TENANT_ID
    uint32_t tenant_id;   // 租户ID
#endif
    uint16_t group_l;     // 入口组
    uint16_t group_h;     // 出口组
    uint8_t ip_protocol;  // IP协议号
    uint8_t version;      // IP版本 (4/6)
    PktType pkt_type;    // 数据包类型

    bool init(const SnortConfig*, PktType, IpProtocol,
        const SfIp* srcIP, uint16_t srcPort,
        const SfIp* dstIP, uint16_t dstPort,
        uint16_t vlanId, uint32_t mplsId,
        uint32_t addrSpaceId, ...);
};
```

## Flow 状态机

```cpp
class Flow {
public:
    enum class FlowState : uint8_t {
        SETUP = 0,    // 创建中
        INSPECT = 1,  // 检测中
        BLOCK = 2,    // 阻止
        RESET = 3,    // 重置
        ALLOW = 4     // 允许
    };
};
```

## 核心函数

### FlowCache
```cpp
class FlowCache {
    snort::Flow* find(const snort::FlowKey*);    // 查找流
    snort::Flow* allocate(const snort::FlowKey*); // 分配新流
    bool release(snort::Flow*, PruneReason = PruneReason::NONE,
        bool do_cleanup = true);                  // 释放流

    unsigned prune_idle(time_t thetime,
        const snort::Flow* save_me);             // 清理空闲流
    unsigned prune_excess(const snort::Flow* save_me); // 超过限制时清理
    unsigned timeout(unsigned num_flows, time_t cur_time); // 超时处理
    unsigned purge();                             // 清空缓存
    unsigned get_count();                         // 获取流数量

    bool move_to_allowlist(snort::Flow* f);      // 移至白名单
};
```

### FlowKey Hash计算
```cpp
unsigned FlowHashKeyOps::do_hash(const unsigned char* k, int) {
    uint32_t a, b, c;
    a = b = c = hardener;

    const uint32_t* d = (const uint32_t*)k;

    // IPv6地址 + MPLS + 地址空间 + 租户ID + 端口 + 组 + VLAN
    // 使用32位掺混哈希(mixing)和最终化(finalize)

    mix(a, b, c);
    // ... 多轮混合
    finalize(a, b, c);
    return c;
}
```

### FlowData 存储
```cpp
class FlowData {
    unsigned id;              // 注册ID
    void* data;               // 用户数据
    StreamAppDataFree dtor;   // 析构函数

public:
    void set(FlowData*);
    FlowData* get(unsigned id) const;
    void erase(unsigned id);
    void call_handlers(Packet*, FlowDataHandlerType) const;
};
```

## 模块交互

```
packet_io (接收数据包)
    │
    ▼
codecs (协议解码)
    │
    ▼
┌─────────────────────────────────────────┐
│            Flow Module                    │
│  ┌─────────────────────────────────┐   │
│  │       FlowControl                 │   │
│  │  ┌─────────────────────────┐     │   │
│  │  │ FlowCache (per proto)   │     │   │
│  │  │  ├── FlowKey → Flow     │     │   │
│  │  │  └── LRU List           │     │   │
│  │  └─────────────────────────┘     │   │
│  │  ┌─────────────────────────┐     │   │
│  │  │ ExpectCache             │     │   │
│  │  └─────────────────────────┘     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
    │
    ▼
stream (TCP/IP重组)
    │
    ▼
detection (规则检测)
```

## Flow 查找流程

```cpp
Flow* FlowControl::get_flow(Packet* p) {
    // 1. 创建FlowKey
    FlowKey key;
    key.init(...);

    // 2. 查找缓存
    Flow* flow = flow_cache->find(&key);
    if (flow) return flow;

    // 3. 检查预期流
    flow = expect_cache->realize(&key);
    if (flow) return flow;

    // 4. 分配新流
    flow = flow_cache->allocate(&key);
    return flow;
}
```

## PruneReason 剪枝原因

```cpp
enum class PruneReason : uint8_t {
    NONE = 0,
    IDLE_MAX_FLOWS,         // 超过最大流数
    IDLE_PROTOCOL_TIMEOUT,   // 协议超时
    EXCESS,                 // 超过内存限制
    MEMCAP,                 // 内存上限
    HA,                     // 高可用同步
    STALE,                  // 陈旧连接
    STREAM_CLOSED,          // 流已关闭
    END_OF_FLOW             // 流结束
};
```

## LRU管理

```cpp
// 每个协议类型独立的LRU列表
constexpr uint8_t max_protocols = static_cast<uint8_t>(to_utype(PktType::MAX));
constexpr uint8_t allowlist_lru_index = max_protocols;  // 白名单LRU
constexpr uint8_t total_lru_count = max_protocols + 1;

// 流分类
enum PktType {
    NONE, IP, TCP, UDP, ICMP, FILE, PDU, USER, MAX
};

// 当缓存满时:
// 1. 尝试在各自协议的LRU中剪枝
// 2. 如果开启allowlist_excess,移动到白名单
// 3. 强制剪枝最旧的流
```

## 高可用性 (HA)

```cpp
class FlowHAState {
    uint8_t* state;         // 序列化状态
    uint32_t state_len;     // 状态长度
    struct timeval synced;   // 同步时间
};

// Flow同步流程:
// 1. Flow.set_ha_state() - 设置HA状态
// 2. FlowHAState.serialize() - 序列化
// 3. 传输到备份节点
// 4. FlowHAState.unserialize() - 反序列化
```
