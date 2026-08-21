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