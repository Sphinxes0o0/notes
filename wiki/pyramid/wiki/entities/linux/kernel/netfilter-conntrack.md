---
type: entity
tags: [linux, networking, netfilter, conntrack, kernel, nids, connection-tracking]
created:2026-06-08
sources: [arthurchiao-conntrack-design]
---

# Linux Netfilter Conntrack

## 定义

Linux conntrack（connection tracking）是 Netfilter 子系统中的连接状态追踪模块，基于网络元组（tuple：src/dst IP + port + protocol）跟踪双向 UDP/TCP/ICMP 流。conntrack 是 NAT、stateful firewall、有状态 QoS 的基础，被 iptables `state`/`conntrack` 模块广泛依赖。

##关键要点

- **连接表**：全局 hash table，per-netns独立；元组 hash决定桶位置
- **两阶段创建**：`nf_conntrack_in()` (NEW, unconfirmed) → `nf_conntrack_confirm()` (CONFIRMED)
- **超时机制**：TCP/UDP/ICMP各自超时；FIN/RST 后短期保留
- **NAT集成**：conntrack tuple 在 NAT 后被改写；reply tuple 自动反推
- **Cilium替代**：基于 eBPF 自实现 conntrack，绕过 netfilter（4.19+）

##核心概念

- `struct nf_conn` — 连接记录（包含 tuple、helper、timeout、nat_info）
- **协议扩展**：TCP / UDP / ICMP / GRE / SCTP / DCCP 每协议独立 tuple
- **期望连接（expect）**：FTP data channel、IRC DCC 等被动连接预建
- **conntrack helper**：ALG，应用层协议解析（FTP、SIP、SNMP）
- **调优 sysctl**：`nf_conntrack_max`、`nf_conntrack_buckets`、`tcp_timeout_*`
- **DDoS风险**：`table full, dropping packet` →静默丢包

## 相关页面

- [[entities/linux/network/nat]] — NAT依赖 conntrack
- [[entities/linux/network/netfilter-hooks]] —钩子点位置
- [[entities/linux/kernel/netfilter]] — Netfilter框架
- [[sources/arthurchiao-conntrack-design]] — 实现详解与图示
