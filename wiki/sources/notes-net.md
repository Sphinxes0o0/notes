---
type: source
source-type: github
title: "Linux Kernel Net Subsystem Notes"
author: "Sphinx"
date: 2026-05-20
size: medium
path: raw/github/notes/net/
summary: "Linux 内核网络子系统深度分析：Socket Layer、sk_buff、Netdevice、Routing、Netfilter Hooks、TCP/UDP 协议实现"
tags: [linux-kernel, networking]
created: 2026-05-20
---

# Linux Kernel Net Subsystem Notes

## 核心内容

本笔记涵盖 Linux 内核网络子系统的完整分析：

- **Socket Layer**：`struct socket`、`struct sock`、socket 系统调用、sock_map_fd
- **sk_buff**：内存布局、skb_put/push/pull、克隆 vs 复制、分散/聚集 I/O
- **Netdevice**：`struct net_device`、NAPI 轮询、GRO、设备注册/注销
- **Routing**：FIB 查找、Trie 最长前缀匹配、dst_entry 缓存
- **Netfilter Hooks**：Hook 点、nf_hook_slow、iptables/nftables 规则遍历
- **TCP/UDP**：状态机、发送/接收路径、定时器管理

## 关键文件

| 文件 | 内容 |
|------|------|
| `net_deep_dive_r1.md` | 核心数据结构分析 |
| `net_socket_core.md` | Socket 层实现 |
| `net_tcp_ip.md` | TCP/IP 协议栈 |
| `net_netfilter.md` | Netfilter 框架 |
| `net_routing.md` | 路由子系统 |
| `net_skbuff.md` | sk_buff 内存管理 |

## 相关页面

- [[entities/linux/kernel/net/linux-kernel-net-subsystem]]
- [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework]]
- [[entities/linux/network/linux-network-protocols]]
