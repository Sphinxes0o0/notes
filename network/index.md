---
title: Network Notes
---

# 网络学习笔记

欢迎来到网络学习笔记部分！这里包含了我在学习网络协议和网络编程过程中的各种笔记和总结。

## 阅读路径（推荐顺序）

| 阶段 | 目录 | 定位 | 适合 |
|---|---|---|---|
| 入门 | [`tcpip/`](./tcpip/) + [`osi_phy_mac`](./osi_phy_mac.md) | 协议概念与原理 | 想理解协议本身 |
| 进阶 | [`linux_net-stack/`](./linux_net-stack/) | **译文集**（plantegg / arthurchiao.art / lsgxeva）—— 行业专家的网络栈全景文章 | 想看别人怎么写 |
| 实战 | [`linux_kernel/`](./linux_kernel/) | **源码级别拆解**（55 个子模块：Socket/TCP/UDP/Netfilter/Bridge/AF_XDP...） | 想看 Linux 实现 |
| 专题 | [`linux_netfilter/`](./linux_netfilter/) | **子系统深度**（Netfilter/conntrack/nftables） | 想钻特定子系统 |
| 调优 | [`performance/`](./performance/) | 性能与高级特性 | 想做性能优化 |

> **三个易混目录的快速区分**:
> - `linux_net-stack/` = 译文（转载） —— 不是自己的笔记
> - `linux_kernel/` = Linux 网络核心源码解析 —— 是自己的笔记，覆盖面广
> - `linux_netfilter/` = Netfilter 专项深入 —— 是自己的笔记，但只聚焦一个子系统

## Netfilter 主题在 3 处的区分

同样讲 Netfilter，仓库里有 3 个层次，从"零基础入门"到"源码逐行跟踪":

| 层次 | 位置 | 视角 | 适合 |
|---|---|---|---|
| 综合（中 · 概念）| [`linux_netfilter/netfilter_subsystem.md`](./linux_netfilter/netfilter_subsystem.md) | 中文综述：Hook 点 / Verdict / 协议族 / 数据包处理流程 | 入门 / 教学 |
| 综合（英 · 源码）| [`linux_netfilter/net_subsystem_netfilter.md`](./linux_netfilter/net_subsystem_netfilter.md) | 英文源码分析：含 `core.c` 行号 / 结构体定义 / hook 注册函数 | 想跳源码 |
| 源码概述 | [`linux_kernel/netfilter.md`](./linux_kernel/netfilter.md) | 在 linux_kernel/ 下的源码概述（292 行）| 看快速框架 |
| 单一组件 | [`core/net_subsystem_conntrack.md`](./core/net_subsystem_conntrack.md) | Conntrack（连接跟踪）单一组件深入（817 行）| 钻 conntrack 实现 |

> 建议阅读顺序：**概念** → **源码概述** → **conntrack 单一组件**，需要时再跳 `core.c` 行号。

## 主题交叉引用索引

同一个主题在 `network/` 下可能有多个文件，下面是几个跨子目录主题的快速定位。

### TCP 主题（11 个文件）

| 层次 | 位置 | 视角 |
|---|---|---|
| 协议概念 | [`tcpip/tcp.md`](./tcpip/tcp.md) | TCP 协议详解（中文概念） |
| TCP 选项 | [`tcpip/tcp-sack-dsack.md`](./tcpip/tcp-sack-dsack.md) | SACK / DSACK 实现 |
| 调试实战 | [`tcpip/tcp-troubleshooting-plantegg.md`](./tcpip/tcp-troubleshooting-plantegg.md) | 疑难问题汇总（plantegg 译文） |
| 调试实战 | [`tcpip/tcp-self-connection-plantegg.md`](./tcpip/tcp-self-connection-plantegg.md) | 自己连自己（plantegg 译文） |
| 子系统概述 | [`tcpip/net_subsystem_tcpip.md`](./tcpip/net_subsystem_tcpip.md) | TCP/IP 子系统（英） |
| 内核实现 | [`linux_kernel/ipv4_tcp.md`](./linux_kernel/ipv4_tcp.md) | IPv4 TCP 实现（中，概念） |
| 内核实现 | [`linux_kernel/net_tcp_ip.md`](./linux_kernel/net_tcp_ip.md) | TCP/IP 协议栈源码分析（中） |
| 内核实现 | [`linux_kernel/ipv6_tcp_udp.md`](./linux_kernel/ipv6_tcp_udp.md) | IPv6 TCP/UDP |
| Netfilter | [`linux_kernel/netfilter_tcpmss.md`](./linux_kernel/netfilter_tcpmss.md) | xt_TCPMSS |
| Netfilter | [`linux_netfilter/netfilter_tcp_deep_dive.md`](./linux_netfilter/netfilter_tcp_deep_dive.md) | TCP 深度源码分析（第二轮） |
| 性能 | [`performance/tcp-bypass-notes.md`](./performance/tcp-bypass-notes.md) | TCP Bypass 绕过方案 |
| 工具 | [`tools/tcpdump.md`](../tools/tcpdump.md) | tcpdump 使用指南 |

### Socket 主题（5 个文件）

| 层次 | 位置 | 视角 |
|---|---|---|
| 子系统概述 | [`core/net_subsystem_socket.md`](./core/net_subsystem_socket.md) | BSD Socket Layer Analysis（英，1606 行） |
| 概念 | [`linux_kernel/socket.md`](./linux_kernel/socket.md) | Socket 层 - 通用套接字层（中，510 行） |
| 系统调用 | [`linux_kernel/socket_syscall.md`](./linux_kernel/socket_syscall.md) | Socket 系统调用（279 行） |
| 源码分析 | [`linux_kernel/net_socket_core.md`](./linux_kernel/net_socket_core.md) | Socket Core 源码分析（780 行） |
| 特定类型 | [`linux_kernel/unix_socket.md`](./linux_kernel/unix_socket.md) | Unix Domain Socket（268 行） |

> `core/net_subsystem_socket.md` 与 `linux_kernel/net_socket_core.md` 内容有部分重叠但视角不同（英 vs 中 / 侧重不同结构体），不需要合并。

### 路由主题（6 个文件）

| 层次 | 位置 | 视角 |
|---|---|---|
| 子系统概述 | [`core/net_subsystem_routing.md`](./core/net_subsystem_routing.md) | Packet Routing + Neighbor（英，976 行） |
| 源码分析 | [`linux_kernel/net_routing.md`](./linux_kernel/net_routing.md) | IPv4 路由子系统分析（中，1092 行） |
| 数据结构 | [`linux_kernel/routing.md`](./linux_kernel/routing.md) | dst_entry 和路由缓存（402 行） |
| 概述 | [`linux_kernel/ipv4_routing.md`](./linux_kernel/ipv4_routing.md) | IPv4 路由子系统（191 行） |
| 数据结构 | [`linux_kernel/ipv4_fib.md`](./linux_kernel/ipv4_fib.md) | FIB 路由结构（235 行） |
| IPv6 | [`linux_kernel/ipv6_routing.md`](./linux_kernel/ipv6_routing.md) | IPv6 路由子系统（263 行） |

### IPv6 主题（5 个文件，都在 `linux_kernel/`）

| 子主题 | 位置 | 视角 |
|---|---|---|
| 协议栈 | [`ipv6_core.md`](./linux_kernel/ipv6_core.md) | IPv6 协议栈核心 |
| 地址管理 | [`ipv6_addrconf.md`](./linux_kernel/ipv6_addrconf.md) | SLAAC / DAD / 路由器发现 |
| 邻居发现 | [`ipv6_ndisc.md`](./linux_kernel/ipv6_ndisc.md) | NDisc（地址解析 / 重定向） |
| 路由 | [`ipv6_routing.md`](./linux_kernel/ipv6_routing.md) | IPv6 路由子系统 |
| 传输层 | [`ipv6_tcp_udp.md`](./linux_kernel/ipv6_tcp_udp.md) | TCP/UDP over IPv6 |

## 目录结构

### TCP/IP 协议栈
- [IP 协议](./tcpip/ip.md) - 网际协议详解
- [TCP 协议](./tcpip/tcp.md) - 传输控制协议详解

### Linux Netfilter
- [连接跟踪](./linux_netfilter/conntrack.md) - Linux 连接跟踪机制
- [连接跟踪垃圾回收](./linux_netfilter/conntrack_gc.md) - 连接跟踪的垃圾回收机制
- [nftables](./linux_netfilter/nftables.md) - Linux 下一代包过滤框架

## 学习目标

通过系统学习网络协议栈和 Linux 网络子系统，掌握：

1. **协议理解** - 深入理解 TCP/IP 协议栈的工作原理
2. **内核机制** - 掌握 Linux 网络子系统的核心机制
3. **性能优化** - 学习网络性能调优和问题排查
4. **实际应用** - 将理论知识应用到实际网络编程中