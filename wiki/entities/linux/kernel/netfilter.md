---
type: entity
tags: [linux-kernel, networking, netfilter, iptables, nftables, conntrack, nat, firewall]
created: 2026-05-20
sources: [notes-netfilter, notes-net]
---

# Linux Kernel Netfilter Framework (Netfilter 框架)

## 定义

Netfilter 是 Linux 内核提供的数据包过滤和修改框架，通过在网络协议栈关键路径插入可编程"钩子"实现包处理、防火墙、NAT 等功能。

## 关键要点

### Hook 点 (Netfilter Hooks)

```
                                    NF_INET_POST_ROUTING
                                    ^
                                    |
+------------+    +--------+    +------+    +------+    +-----------+    +------------+
| NF_INET_   | -> |  Routing | -> | PREROUTING | -> | FORWARD | -> | POSTROUTING| -> |
| LOCAL_OUT  |    +--------+    +------+     |    +------+    +-----------+    |
+------------+                             |                              |
                                          v                              v
                                    +-------------+              +----------------+
                                    | NF_INET_   |              | NF_INET_       |
                                    | LOCAL_IN    |              | POST_ROUTING   |
                                    +-------------+              +----------------+
```

| Hook 点 | 时机 | 典型用途 |
|---------|------|----------|
| `NF_INET_LOCAL_OUT` | 本机发出，路由查找前 | 本机防火墙 OUTPUT |
| `NF_INET_PRE_ROUTING` | 接收后，路由查找前 | DNAT |
| `NF_INET_FORWARD` | 转发场景 | 转发防火墙 |
| `NF_INET_POST_ROUTING` | 发送前 | SNAT |
| `NF_INET_LOCAL_IN` | 目的地是本机 | 本机防火墙 INPUT |

### 核心数据结构

| 结构体 | 位置 | 用途 |
|--------|------|------|
| `struct nf_hook_ops` | `include/linux/netfilter.h:98` | 钩子函数注册 |
| `struct nf_hook_entries` | `include/linux/netfilter.h` | 钩子链表 |
| `struct nf_conn` | `include/net/netfilter/nf_conntrack.h:74` | 连接跟踪条目 |
| `struct ipt_entry` | `include/uapi/linux/netfilter_ipv4/ip_tables.h:106` | iptables 规则 |

### Hook 注册/执行 (net/netfilter/core.c)

- `nf_register_net_hook()`：注册单个钩子（支持 NFPROTO_INET 同时注册 IPv4/IPv6）
- `nf_hook_entries_grow()`：将新钩子添加到链表
- `nf_hook_slow()`：遍历所有钩子，根据 verdict（NF_ACCEPT/DROP/QUEUE/STOLEN）处理

### iptables (xtables)

- `ipt_do_table()`：规则遍历，IP 头匹配 → matches 扩展 → target 动作
- **表**：filter（过滤）、nat（地址转换）、mangle（修改标记）、raw（绕过连接跟踪）
- **xt_entry_match / xt_entry_target**：可加载扩展模块
- 线性规则遍历，大规则集性能下降

### nftables (新一代规则引擎)

- **Table → Chain → Rule → Expression** 层次结构
- `nft_do_chain()`：字节码虚拟机解释执行表达式序列
- **NFT_CONTINUE/NFT_BREAK/NFT_JUMP/NFT_GOTO/NFT_RETURN**：流程控制
- **PIPAPO 算法**：高性能集合查找，支持 AVX2 加速
- 事务模型：规则原子更新，避免中间状态安全空窗
- 多协议族：inet（IPv4+IPv6混合）、ip、ip6、arp、bridge、netdev

### Connection Tracking (连接跟踪)

- **状态**：NEW、ESTABLISHED、RELATED、INVALID
- **五元组**：(src_addr, dst_addr, src_port, dst_port, protocol)
- `nf_conntrack_in()` → `resolve_normal_ct()` → 查找/创建连接
- 哈希表：基于 siphash 的高性能查找
- TCP 状态机跟踪、SYN-SENT/SYN-RECV/ESTABLISHED 等
- **期望连接 (Expectation)**：FTP DATA、ICMP 错误等 RELATED 连接

### NAT (网络地址转换)

- `NF_NAT_MANIP_SRC`（SNAT）/ `NF_NAT_MANIP_DST`（DNAT）
- HOOK2MANIP 映射：PRE_ROUTING→DNAT，POST_ROUTING→SNAT
- `nf_nat_packet()` → `nf_nat_manip_pkt()`：IP 头修改 + 校验和更新
- 端口分配：`get_random_u16()` 随机，冲突重试最多 128 次

### 用户态库

| 库 | 用途 |
|----|------|
| libmnl | 底层 Netlink 通信 |
| libnftnl | nftables 对象操作 |
| libnftables | 高级封装，解析 nft 语法 |
| libnetfilter_queue | NFQUEUE 用户空间包处理 |
| libnetfilter_conntrack | 连接跟踪表访问 |

### 性能优化

- **分段锁 (Sliding Locks)**：`nf_conntrack_locks[4096]` 减少哈希桶锁竞争
- **RCU + SLAB_TYPESAFE_BY_RCU**：允许宽限期回收对象重用
- **哈希预计算**：reply 方向哈希在确认时缓存
- **Per-CPU 统计**：`u64_stats_sync` 保护 64 位计数器

## 源码关键位置

| 文件 | 行号 | 内容 |
|------|------|------|
| `net/netfilter/core.c` | 554 | `nf_register_net_hook()` |
| `net/netfilter/core.c` | 616 | `nf_hook_slow()` |
| `net/ipv4/netfilter/ip_tables.c` | 222 | `ipt_do_table()` |
| `net/netfilter/nf_tables_core.c` | 249 | `nft_do_chain()` |
| `net/netfilter/nf_conntrack_core.c` | 63 | `nf_conntrack_hash` |
| `net/netfilter/nf_nat_core.c` | 866 | `nf_nat_packet()` |

## 相关概念

- [[entities/linux/kernel/net]] — 网络子系统整体架构
- [[entities/linux/network/linux-network-protocols]] — 协议层与 conntrack 集成

## 来源详情

- [[sources/notes-netfilter]] — Netfilter 深度分析 R1/R2
- [[sources/notes-network-fundamentals]] — Linux Net 子系统分析
- github-notes-network-linux-netfilter-conntrack — conntrack 详解
- github-notes-network-linux-netfilter-nftables — nftables 架构
