---
type: entity
tags: [linux, networking, netfilter, nat, kernel, nids]
created:2026-06-08
sources: [arthurchiao-conntrack-design]
---

# Linux Netfilter NAT

## 定义

Linux Netfilter NAT 子系统实现网络地址转换（Network Address Translation），支持 SNAT（源地址转换，用于出站）、DNAT（目标地址转换，用于入站/端口转发）和 MASQUERADE（动态 SNAT，用于 PPP/拨号）等场景。NAT强依赖 conntrack提供的连接追踪表来匹配双向流。

##关键要点

- **NAT 表**：独立的 `nf_nat` 表，与 filter 表并列；通过 `iptables -t nat` 配置
- **conntrack依赖**：NAT 仅修改 conntrack记录中的地址/端口 tuple，转发决策由 conntrack + route共同决定
- **钩子点**：PREROUTING (DNAT)、POSTROUTING (SNAT/MASQUERADE)、LOCAL_OUT (SNAT)
- **扩展匹配**：`conntrack` 模块（`--ctorigsrc`, `--ctdst`）允许基于 conntrack状态匹配
- **Cilium替代**：eBPF-based NAT in Cilium1.7+，与 netfilter协同或完全替代

##核心概念

- `nf_nat_setup_info()` — 在 conntrack 创建/确认时初始化 NAT tuple
- **NAT 类型**：snat、dnat、balance、same、netmap、masquerade
- **tuple manipulation**：双向流分别修改 reply tuple（自动反推）
- **conntrack helper**：FTP/SIP/IRC ALG协议级 NAT跟踪
- **hairpin NAT**：内网主机互访时的回环 NAT（loopback）
- **nftables替代**：`nft add rule nat prerouting ...`取代 iptables

## 相关页面

- [[entities/linux/kernel/netfilter-conntrack]] — conntrack 实现
- [[entities/linux/network/netfilter-hooks]] —5 个 Netfilter钩子点
- [[entities/linux/network/net-stack-overview]] — Linux 网络栈总览
- [[sources/arthurchiao-conntrack-design]] — conntrack/NAT设计与实现
