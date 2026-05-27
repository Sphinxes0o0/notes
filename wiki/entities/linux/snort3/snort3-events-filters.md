---
type: entity
tags: [snort3, ids, ips, events, filtering, host-tracking]
created: 2026-05-27
sources: [github-snort3-events-filters]
---

# Snort3 Events & Filters

## 事件队列 (Event Queue)

### 核心结构

`SF_EVENTQ` 是一个环形预分配队列，基于双向链表节点 + 事件内存池：

```cpp
struct SF_EVENTQ_NODE { void* event; SF_EVENTQ_NODE* prev; SF_EVENTQ_NODE* next; };

struct SF_EVENTQ {
    SF_EVENTQ_NODE* head;          // 队列头
    SF_EVENTQ_NODE* last;         // 最低优先级节点
    SF_EVENTQ_NODE* node_mem;     // 预分配节点内存池
    char* event_mem;               // 预分配事件内存池
    char* reserve_event;           // 溢出时优先级比较的临时slot
    int max_nodes;                 // 最大节点数 (memcap)
    int log_nodes;                 // 触发日志的阈值
    int cur_nodes;                 // 当前节点数
    int cur_events;                // 累计事件数
    unsigned fails;                 // 因内存耗尽丢弃的事件计数
};
```

### Memcap 机制

- `sfeventq_new(max_nodes, log_nodes, event_size)` 预分配 `max_nodes` 个节点 + 事件槽
- 当队列满时，新事件与 `last`（最低优先级）比较：
  - 新事件优先级更高 → 覆盖 `last`，新事件入队
  - 否则丢弃新事件
- `reserve_event` 允许在不破坏现有节点的情况下做优先级比较

### 事件类 (Event)

```cpp
class Event {
    uint32_t ts_sec, ts_usec;     // 时间戳
    uint32_t event_id;             // 全局唯一事件ID
    uint32_t event_reference;      // 关联事件引用 (e.g., 标记包的源事件)
    const SigInfo& sig_info;      // 签名信息 (gid/sid/rev/msg/priority)
    const char* action;            // 触发时的动作
    const char** buffs_to_dump;    // 要dump的缓冲区
};
```

### 事件队列配置

```cpp
struct EventQueueConfig {
    unsigned max_events;           // 队列最大事件数
    unsigned log_events;           // 日志输出事件数
    int order;                    // SNORT_EVENTQ_PRIORITY 或 SNORT_EVENTQ_CONTENT_LEN
    int process_all_events;
};
```

### 事件流程

```
Packet → Detection Engine → Rule Matching → Event Queue (栈式多队列)
                                              ↓
                               sfeventq_action() 对最高优先级事件调用日志回调
```

- 重建包/负载处理前 push，处理后 pop
- Wire packet 事件保留在高层队列

---

## 主机追踪 (Host Tracker)

### 架构

- **Segmented LRU Cache**：`HostCacheSegmented` 将缓存分段，每段独立加锁，减少高并发竞争
- **Memcap Tracking**：`LruCacheSharedMemcap` 用 `atomic<size_t>` 跟踪当前内存使用
- **Custom Allocators**：STL 容器内的内存分配通过 `CacheAlloc` 回调更新缓存 accounting
- **Purgatory Pattern**：被驱逐的 `HostTracker` 不会立即析构，而是先调用 `remove_flows()` 再释放

### 段索引计算

```cpp
// XOR-based hash 分布到 2^N 个段
result ^= bytes[i];
return result & (segment_count - 1);  // 快速取模 (segment_count 必须是 2 的幂)
```

### 主机数据模型

```cpp
HostTracker {
    // 身份
    std::vector<HostMac> macs;                    // MAC地址 (带TTL/primary标志)
    std::vector<NetProto_t> network_protos;       // Layer 3 协议
    std::vector<XProto_t> xport_protos;           // Layer 4 协议

    // 应用层
    std::vector<HostApplication> services;         // TCP/UDP 服务 (port/proto/appid/hits)
    std::vector<HostClient> clients;               // 客户端应用 (id/version/service)

    // 指纹
    std::set<uint32_t> tcp_fpids;                 // TCP 协议指纹
    std::set<uint32_t> udp_fpids;                 // UDP 协议指纹
    std::set<uint32_t> smb_fpids;                 // SMB 指纹
    std::set<uint32_t> cpe_fpids;                // CPE 指纹
    std::vector<DeviceFingerprint> ua_fps;        // User-Agent 指纹

    // 设备类型
    enum HostType { HOST_TYPE_HOST, HOST_TYPE_ROUTER, HOST_TYPE_BRIDGE,
                    HOST_TYPE_NAT, HOST_TYPE_LB };
};
```

### 应用追踪 (HostApplication)

```cpp
struct HostApplication {
    Port port;
    IpProtocol proto;
    AppId appid;
    bool inferred_appid;
    uint32_t hits;                                // 命中次数
    uint32_t last_seen;
    char user[INFO_SIZE];                         // 已登录用户名
    std::vector<HostApplicationInfo> info;         // 供应商/版本信息
    PayloadVector payloads;                      // 应用载荷
};
```

### 可见性 (Visibility)

所有追踪对象（service/client/payload）支持 `visibility = false` 标记：
- 控制删除（control delete）时，被标记的对象不会被真正删除
- 避免误删正在使用的引用

---

## 过滤器框架 (Filter Framework)

### 三层过滤架构

| 层级 | 过滤器 | 作用时机 | 能做什么 |
|------|--------|----------|----------|
| 1 | **Detection Filter** | 规则匹配最后一步 | 控制是否生成事件 |
| 2 | **Rate Filter** | 事件生成后 | 改变规则动作 (alert→drop) |
| 3 | **Event Filter** | 事件入队后 | 控制是否记录日志 |

### Detection Filter

规则匹配的最终关卡，基于简单计数阈值：

```cpp
struct DetectionFilterConfig {
    unsigned memcap;
    int count;     // 阈值
    int enabled;
};
```

### Rate Filter

按速率跟踪事件，超阈值后**修改动作**：

```cpp
enum SFRF_TRACK { SFRF_TRACK_BY_NONE, SFRF_TRACK_BY_SRC, SFRF_TRACK_BY_DST, SFRF_TRACK_BY_RULE };

enum FilterState { FS_NEW, FS_OFF, FS_ON, FS_MAX };

struct tSFRFConfigNode {
    SFRF_TRACK tracking;           // 跟踪方式
    std::atomic<unsigned> count;  // 当前计数
    snort::IpsAction::Type newAction;  // 替换动作
    unsigned timeout;             // 恢复到原始动作的时长
    time_t seconds;               // 采样周期
};
```

状态转换：`FS_NEW → FS_OFF (正常) → FS_ON (超阈值) → [timeout后] → FS_OFF`

### Event Filter (Threshold)

事件入队后控制日志输出：

```cpp
enum THD_TYPE {
    THD_TYPE_LIMIT,      // 记录前N个事件
    THD_TYPE_THRESHOLD,  // 每N个事件记录一次
    THD_TYPE_BOTH,        // N个事件后记录一次，然后抑制
    THD_TYPE_SUPPRESS,   // 完全抑制
    THD_TYPE_DETECT      // 仅用于检测跟踪
};

enum THD_TRK { THD_TRK_NONE, THD_TRK_SRC, THD_TRK_DST };
```

### 阈值节点 (THD_NODE)

```cpp
struct THD_NODE {
    unsigned gen_id, sig_id;
    int tracking;                    // THD_TRK_SRC 或 THD_TRK_DST
    int type;                       // THD_TYPE_* 之一
    int priority;                   // 优先级 (多个threshold时按序匹配)
    int count;                      // 触发阈值
    uint64_t seconds;               // 时间窗口
    sfip_var_t* ip_address;         // suppression 的IP过滤
};
```

### BPF/Pcap 过滤器

BPF 过滤**不在** `filters/` 目录——那是**packet filter**（包过滤），在 Snort3 的数据采集层实现。`filters/` 目录是**detection/event/rate filtering**（检测过滤）。

---

## 关键设计模式

### 栈式多队列

Snort 使用多个 `SF_EVENTQ` 实例组成的栈：push/pop 机制让重建包处理过程中的事件不会混入 wire packet 事件。

### 内存限额 (Memcap)

所有组件（eventq、host_cache、rate_filter、threshold）都有独立的 memcap：
- 超过时按优先级淘汰，而非直接拒绝
- 计数 `fails` 字段记录因内存耗尽的丢弃数

### 自定义分配器链

`CacheAlloc<T>` → `HostCacheAllocIp<T>` → `CacheInterface` → `LruCacheSharedMemcap::update()`

每个 STL 容器增长时，allocator 回调 cache 的 `update(int)` 动态调整内存计数。

---

## 相关概念

- [[snort3-framework]] — 框架总览
- [[snort3-actions]] — 动作系统
- [[snort3-flow]] — Flow/会话追踪
- [[snort3-ips-options]] — IPS 选项

## 来源

- [[github-snort3-events-filters]]
