---
type: source
source-type: github
title: "Linux Network Notes"
author: "Sphinx"
date: 2026-05-20
size: large
path: raw/github/notes/network/
summary: "Linux 网络协议实现笔记：TCP/IP、IPv4/IPv6、BPF/XDP、桥接、路由、Netfilter、性能优化（hotpath、NAPI、GRO）"
tags: [linux-kernel, networking]
created: 2026-05-20
---

# Linux Network Notes

## 核心内容

### TCP/IP 协议栈
- `ip.md` — 网际协议详解
- `tcp.md` — 传输控制协议详解

### Linux Netfilter
- `conntrack.md` — Linux 连接跟踪机制
- `conntrack_gc.md` — 连接跟踪垃圾回收
- `nftables.md` — Linux 下一代包过滤框架

### 网络子系统核心 (linux_kernel/)
- Socket、sk_buff、net_device 详解
- IPv4/IPv6 核心实现
- TCP/UDP 传输协议
- 路由与 FIB
- BPF/XDP 高性能数据路径
- 桥接 (bridge)、Open vSwitch、DSA
- QoS 调度、page_pool

### 性能优化 (performance/)
- `net_subsystem_hotpath.md` — NAPI、RCU、Per-CPU、Cache Line、内存屏障
- `net_subsystem_advanced.md` — 高级特性
- `net_subsystem_kernel_tricks.md` — 内核技巧
- `net_subsystem_timers.md` — 定时器

### 协议分析 (protocols/, tcpip/)
- BPF 钩子、Netlink 接口
- RFC 实现

## 相关页面

- [[entities/linux/kernel/net/linux-kernel-net-subsystem]]
- [[entities/linux/kernel/netfilter/linux-kernel-netfilter-framework]]
- [[entities/linux/network/linux-network-protocols]]
