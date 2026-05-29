---
type: entity
tags: [linux, networking, arp, neighbor, ndisc, routing]
created: 2026-05-28
sources: [achieved-arp-table-aging]
---

# Linux ARP/Neighbor 表老化机制

## 定义

Linux 内核通过 **邻居子系统（Neighbor Subsystem）** 维护 ARP 缓存表，将 IP 地址解析为 MAC 地址。条目经历三个状态：delay → reachable → stale，通过延迟删除和垃圾回收减少 ARP 广播开销。

## 三状态机制

| 状态 | 含义 | 触发条件 |
|------|------|----------|
| **delay** | 等待测试可达性 | 刚收到邻居的包 |
| **reachable** | 确认可达（在超时内） | 收到邻居的确认 |
| **stale** | 超时但条目未删除 | reachable 状态超时 |

### 为什么需要 stale 状态

**核心目的**：减少网络中 ARP 交互的开销，尽量减少 ARP 请求。

条目进入 stale 状态后：
- 若收到邻居的包 → 立即转为 reachable
- 若未收到 → 发起 ARP 交互，最终可能置为 failed

## 老化时间计算

```
Timeout = random(base_reachable_time/2, 3*base_reachable_time/2) + gc_stale_time
```

条目被置为 invalid 状态后，等待 gc 时间回收删除。

## 关键参数

| 参数 | 位置 | 默认值 | 说明 |
|------|------|--------|------|
| `gc_thresh1` | `/proc/sys/net/ipv4/neigh/<dev>/` | 128 | GC 运行的最小条目数，低于此值 GC 不工作 |
| `base_reachable_time` | 同上 | — | 基础可达超时 |
| `gc_stale_time` | 同上 | — | stale 条目在被 GC 前的存活时间 |

### gc_thresh1 的作用

```bash
# 存在于 ARP 高速缓存中的最少个数
# 如果少于这个数，垃圾收集器将不会运行
echo 128 > /proc/sys/net/ipv4/neigh/default/gc_thresh1
```

**陷阱**：`gc_thresh1=0` 会导致 ARP 老化机制异常，因为 GC 永远不会运行。

## 重要发现

| 操作 | 能否刷新 STALE→REACHABLE |
|------|-------------------------|
| `arping` | ✅ 可以 |
| `ping` | ❌ 不能 |

**根因**：ping 使用标准 ICMP，不触发邻居状态转换；arping 发送 ARP 请求，强制刷新。

## 诊断命令

```bash
# 查看完整 ARP 条目变化流程（含状态转换）
ip -s neigh

# 查看缓存状态 (REACHABLE/STALE/FAILED)
ip neigh show

# 查看 ARP 缓存（不显示状态）
arp -a

# 查看时间参数
cat /proc/sys/net/ipv4/neigh/eth0/base_reachable_time
cat /proc/sys/net/ipv4/neigh/eth0/gc_stale_time
```

## 相关概念

- [[entities/linux/network/net-stack-deep-dive]] — 网络栈全路径（neigh_resolve_output 位置）
- [[entities/linux/network/linux-network-protocols]] — IPv4 路由与邻居查找
- [[entities/linux/kernel/net]] — 网络子系统框架
- [[entities/linux/kernel/netfilter]] — Netfilter 钩子（PREROUTING/POSTROUTING 与邻居子系统交互）

## 来源详情

- [[sources/achieved-arp-table-aging]] — lsgxeva cnblogs: Linux中arp表的老化机制
