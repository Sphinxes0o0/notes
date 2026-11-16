---
type: entity
tags: [linux, networking, netfilter, hooks, kernel, packet-processing]
created:2026-06-08
sources: [arthurchiao-conntrack-design]
---

# Netfilter Hook Points

## 定义

Linux Netfilter 在网络栈的5 个关键位置注册钩子（hook points），允许内核模块（filter / NAT / conntrack 等）在包经过这些点时检查、修改、丢弃或排队数据包。钩子点是 iptables/nftables规则、conntrack、NAT 等所有功能的底层基础设施。

##关键要点

- **5 个钩子点**：`NF_INET_PRE_ROUTING`、`NF_INET_LOCAL_IN`、`NF_INET_FORWARD`、`NF_INET_LOCAL_OUT`、`NF_INET_POST_ROUTING`
- **注册 API**：`nf_register_net_hook()`（per-namespace），优先级决定调用顺序
- **返回值**：`NF_ACCEPT` / `NF_DROP` / `NF_STOLEN` / `NF_QUEUE` / `NF_REPEAT`
- **IPv4 vs IPv6**：分别走 `NF_INET_*`；bridge 有独立 `NF_BR_*`钩子
- **每条路径都穿过钩子**：入站（PREROUTING→LOCAL_IN）、转发（PREROUTING→FORWARD→POSTROUTING）、出站（LOCAL_OUT→POSTROUTING）

##核心概念

- **PREROUTING**：DNAT、conntrack (new)
- **LOCAL_IN**：filter INPUT、conntrack (confirm)
- **FORWARD**：filter FORWARD、bridge 网桥
- **LOCAL_OUT**：filter OUTPUT、conntrack (new for local-originated)
- **POSTROUTING**：SNAT、conntrack (confirm)、MASQUERADE
- **hook优先级**：`NF_IP_PRI_*`（filter < NAT < conntrack）
- **netns隔离**：每个 network namespace独立的钩子链

## 相关页面

- [[entities/linux/network/nat]] — NAT 子系统
- [[entities/linux/kernel/netfilter-conntrack]] — conntrack 实现
- [[entities/linux/kernel/netfilter]] — Netfilter 子系统总览
- [[sources/arthurchiao-conntrack-design]] —钩子点流程图
