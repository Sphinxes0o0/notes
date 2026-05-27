---
type: source
created: 2026-05-22
source-type: github
title: "Sphinx 网络深度笔记 — Netfilter, Routing, skbuff, OSI/PHY/MAC, Network Stack Deep Dive"
date: 2026-05-22
size: medium
path: raw/notes/net/linux_kernel/ + raw/notes/network/
summary: "合并来自 notes/net 和 notes/network 的剩余网络深度分析文档，涵盖 skbuff 内存管理、Netfilter/iptables/nftables、IPv4 路由 Trie、PHY/MAC 物理层架构、Conntrack 连接跟踪、Socket 层架构和网络栈全路径分析。"
tags: [networking, linux-kernel, netfilter]
sources: [notes-net-deep]
---

# Notes Net Deep — 网络子系统深度分析

## 核心内容

本来源聚合了 Sphinx 技术笔记仓库中尚未被 ingest 的网络相关深度分析文档，分为两大目录：

### raw/notes/net/linux_kernel/ (内核网络)

| 文档 | 内容 |
|------|------|
| `net_skbuff.md` | sk_buff 结构体、head/data/tail/end 四指针布局、alloc_skb/netdev_alloc_skb、skb_clone/skb_copy、kfree_skb 释放链、dataref 引用计数（16位分割）、分散/聚集 I/O（frags[] + frag_list）、linearize 过程（__pskb_pull_tail）、pskb_expand_head 重分配、destructor 机制 |
| `net_netfilter.md` | nf_hook_ops 钩子注册、nf_register_net_hook/nf_unregister_net_hook、nf_hook_slow 遍历执行、ipt_do_table 规则匹配（IP头→matches→target）、ipt_entry/ipt_replace 规则结构、nf_nat_packet NAT 操作、nft_do_chain 字节码虚拟机 |
| `net_routing.md` | fib_result/fib_info/rtable/fib_table 核心结构、fib_lookup 通用查找接口、fib_table_lookup Trie 最长前缀匹配（travel→backtrack→process leaf 三步算法）、ip_route_output_key_hash 输出路由、ip_route_input_rcu 输入路由、fib_rules_lookup 策略路由 |
| `index.md` | Net/ 子系统文档索引与架构总览图（VFS→协议层→skbuff→Netfilter→路由→设备层） |
| `net_deep_dive_r1.md` | R1 深度分析：Socket Layer（socket/sock 结构）、sk_buff、Netdevice、Routing、Netfilter Hooks、TCP/UDP 协议实现，含数据结构关联表和核心函数调用链总表 |

### raw/notes/network/ (网络原理与协议)

| 文档 | 内容 |
|------|------|
| `osi_phy_mac.md` | OSI 物理层与 MAC 层架构：MII/SMI 接口、PHY（PCS/PMA/PMD/MDI 子层）、MAC+LLC 子层、固件 vs 驱动分工、DMA→MAC→PHY 硬件数据流 |
| `core/net_subsystem_socket.md` | BSD Socket Layer 详细分析：socket/sock/sock_common 结构、proto_ops/proto 操作表、sock_alloc/inet_create/inet_bind 流程、sendmsg/recvmsg 路径、socket file operations |
| `core/net_subsystem_routing.md` | 路由子系统深度分析：LC-trie（key_vector + trie 数据结构）、fib_table_lookup 三步算法详解、dst_entry 通用目标缓存（dst_alloc/dst_release/dst_output）、Neighbour Table（ARP，NUD_* 状态机）、neigh_lookup 哈希查找 |
| `core/net_subsystem_conntrack.md` | 连接跟踪子系统：nf_conntrack_tuple 五元组、nf_conntrack_hash_insert 双向插入、nf_conntrack_find_get 查找、init_conntrack 创建新连接、gc_worker 垃圾回收、TCP/UDP 协议 helper 状态机、NAT setup_info/get_unique_tuple/nf_nat_packet |
| `network_stack_deep_dive.md` | 网络栈全路径分析 v2：Socket 创建全流程、TCP 状态机/拥塞控制/Jacobson RTT 估计、UDP send/recv、IP 路由/分片重组、sk_buff 布局与 skb_put/push/pull 操作、Netfilter 钩子架构、iptables 四表五链 |

## 关键引用

- 所有文档基于 Linux Kernel 最新源码分析，包含精确的源码文件位置和行号
- sk_buff 的 head/data/tail/end 四指针布局是理解网络数据包处理的基础
- Netfilter 的 nf_hook_slow 是包过滤的核心执行引擎
- fib_table_lookup 的 LC-trie 实现是最长前缀匹配的经典算法
- Conntrack 的双向哈希插入（ORIGINAL + REPLY）支持双向查找

## 相关页面

- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — 已 ingest 的网络子系统概览
- [[entities/linux/kernel/net/skbuff-deep-dive]] — SKB 内存管理深度分析
- [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework]] — Netfilter 框架
- [[entities/linux/network/linux-network-protocols]] — 协议层实现
- [[entities/linux/network/osi-physical-layer]] — PHY/MAC 物理层
- [[entities/linux/network/net-stack-deep-dive]] — 网络栈全路径分析
- [[sources/notes-network-fundamentals]] — 网络基础笔记
- [[sources/notes-netfilter]] — Netfilter 深度分析
