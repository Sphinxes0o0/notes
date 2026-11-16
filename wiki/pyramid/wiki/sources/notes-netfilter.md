---
type: source
source-type: github
title: "Linux Kernel Netfilter Notes"
author: "Sphinx"
date: 2026-05-20
size: medium
path: raw/notes/netfilter/
summary: "Linux Netfilter/iptables/nftables/conntrack 深度分析：Hook 机制、连接跟踪、NAT、xtables、nftables 表达式、PIPAPO 算法"
tags: [linux-kernel, networking]
sources: [notes-netfilter]
created: 2026-05-20
---

# Linux Kernel Netfilter Notes

## 核心内容

- **Netfilter Hooks**：PREROUTING/INPUT/FORWARD/OUTPUT/POSTROUTING、Ingress
- **Hook 机制**：`struct nf_hook_ops`、`nf_hook_entries_grow()`、`nf_hook_slow()`
- **Connection Tracking**：NEW/ESTABLISHED/RELATED/INVALID 状态、五元组、Conntrack 哈希表
- **iptables**：filter/nat/mangle/raw 表、`ipt_do_table()`、match 和 target 扩展
- **nftables**：Table → Chain → Rule → Expression、`nft_do_chain()` 字节码执行
- **NAT**：SNAT/DNAT、Hook2MANIP 映射、端口分配
- **Xtables**：`xt_register_table()`、`xt_entry_match`/`xt_entry_target`

## 关键文件

| 文件 | 内容 |
|------|------|
| `netfilter_deep_dive_r1.md` | 连接跟踪、NAT、xtables |
| `netfilter_deep_dive_r2.md` | nf_tables、nft_chain_hook、PIPAPO |
| `netfilter_subsystem.md` | 子系统总览 |

## 相关页面

- [[entities/linux/kernel/netfilter]]
- [[entities/linux/kernel/net]]
- [[entities/linux/network/linux-network-protocols]]
