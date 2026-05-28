---
type: entity
tags: [snort3, ids-ips, flow-tracking, intrusion-detection]
created: 2026-05-27
sources: [github-snort3-flow-ips]
---

# Snort3 Flow Tracking

## 定义

Snort3 的 flow 模块负责追踪网络会话的生命周期，包括哈希表管理、超时淘汰、客户端/服务端角色识别、状态机转换。

## 关键要点

### Flow Hash Table

- **FlowCache** 是核心哈希表管理器，内部使用 **ZHash**（zero-copy hash）
- **LRU 列表**：每个协议类型（PktType）维护独立的 LRU 链表，外加一个 allowlist LRU（`allowlist_lru_index = max_protocols`）
- **FlowKey** 是哈希查找键，包含：IP 地址对（ip_l/ip_h）、端口对、MPLS label、tenant_id、vlan_tag、IP 协议号、packet type、version
- **哈希函数**：`FlowHashKeyOps::do_hash()` 使用 32-bit mix 算法处理 15 个 uint32_t 字段
- **Key 规范化**：`FlowKey::normalize()` 确保 IPv4 时较小 IP 总在 `ip_l`，相等时较小端口在 `port_l`，返回 `reversed` 标志

### Flow Key 字段

```
ip_l[4], ip_h[4]   - 低/高 IP 地址（IPv6 数组，IPv4 存末位）
port_l, port_h      - 低/高端口
mplsLabel           - MPLS label
tenant_id            - 租户 ID
addressSpaceId       - 地址空间 ID
vlan_tag             - VLAN tag
ip_protocol          - IP 协议（TCP/UDP/ICMP）
pkt_type             - 数据包类型
version              - IP 版本（4 或 6）
flags.group_used     - group 是否显著
```

### 超时机制

- **PruneReason** 枚举：EXCESS（缓存溢出）、UNI（单向流）、MEMCAP（内存上限）、STALE（陈旧）、IDLE_MAX_FLOWS、IDLE_PROTOCOL_TIMEOUT、STREAM_CLOSED、END_OF_FLOW
- **FlowCache::timeout()**：遍历所有 LRU 链表，淘汰 `idle_timeout` 到期的流
- **FlowCache::prune_idle()**：容量满时淘汰空闲流，每次最多清理 1 条（`cleanup_flows = 1`）
- **FlowCache::prune_excess()**：超过最大容量时淘汰，可选择移入 allowlist 而非删除
- **per-flow `expire_time`**：硬性过期时间戳，`expired()` 检查当前时间是否超过
- **配置结构** `FlowCacheConfig`：max_flows、pruning_timeout、prune_flows、allowlist_cache

### 方向追踪（客户端/服务端）

**角色字段**（`Flow` 类）：
```cpp
SfIp client_ip, server_ip;
uint16_t client_port, server_port;
int32_t client_intf, server_intf;
int16_t client_group, server_group;
```

**角色初始化**（`FlowControl`）：
- **TCP**：`init_roles_tcp()` — SYN-only → src 是 client；SYN-ACK → dst 是 client；其他 → 较高端口是 client
- **UDP**：`init_roles_udp()` — src 永远是 client，dst 永远是 server
- **IP**：`init_roles_ip()` — src 永远是 client，dst 永远是 server

**方向设置**：`flow->set_direction()` 在包上设置 `PKT_FROM_CLIENT` 或 `PKT_FROM_SERVER` 标志

**角色交换**：`flow->swap_roles()` 交换所有 client/server 字段并翻转 `client_initiated` 标志

### Flow 状态机

**FlowState 枚举**：`SETUP → INSPECT → BLOCK/RESET/ALLOW`

| 当前状态 | 条件 | 下一状态 | 动作 |
|---------|------|---------|------|
| SETUP | 新流 | ALLOW | Stream::stop_inspection() |
| SETUP | - | INSPECT | 继续检测 |
| INSPECT | - | INSPECT | 正常检测 |
| ALLOW | news | ALLOW | DetectionEngine::disable_all() |
| BLOCK | news | BLOCK | Stream::drop_traffic() |
| RESET | news | RESET | Stream::drop_traffic() + blocked_flow() |

**StreamState 标志**：`ESTABLISHED、DROP_CLIENT、DROP_SERVER、MIDSTREAM、TIMEDOUT、UNREACH、CLOSED、BLOCK_PENDING、RELEASING`

### 关键类关系

```
FlowControl
├── FlowCache
│   ├── ZHash（哈希表）
│   ├── FlowUniList（单向流链表）
│   └── Flow（会话数据）
│       ├── Session*（协议特定会话）
│       ├── Inspector* ssn_client / ssn_server
│       ├── FlowDataStore（inspector 状态存储）
│       ├── FlowStash（通用键值存储）
│       └── FlowHAState*（高可用状态）
├── ExpectCache（预期流追踪，FTP 数据通道等）
└── DeferredTrust（延迟信任决策）
```

**FlowDataStore**：存储 `std::vector<FlowData*>`，按 ID 排序，支持 EOF/retransmit 事件处理器

**FlowStash**：通用 KV 存储，支持 int32/uint32/string/对象，用于辅助 IP 追踪

**ExpectCache**：追踪预期流（如 FTP 主动模式数据通道），支持通配符（任一端口为 0）

**DeferredTrust**：延迟会话信任决策，状态机：OFF → ON → DEFERRING → DO_TRUST

### Flow 生命周期方法

| 方法 | 作用 |
|------|------|
| `init()` | 按数据包类型初始化流 |
| `flush()` | 刷新会话数据 |
| `reset()` | 重置会话状态 |
| `restart()` | 清除并重启流 |
| `clear()` | 完全清空，返回 SETUP 状态 |

### Session 抽象基类

`Session`（`session.h`）是协议特定会话的抽象基类（TCP/UDP/ICMP 等），关键方法：`setup()`、`process()`、`clear()`、`flush()`

## 相关概念

- [[entities/linux/snort3/snort3-ips-options]] — IPS 选项评估
- [[entities/linux/snort3/snort3-framework]] — Snort3 框架概览
- [[network-intrusion-detection]] — 入侵检测系统

## 来源详情

- [[github-snort3-flow-ips]]
