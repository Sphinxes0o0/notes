---
type: source
source-type: bookmark
title: "Caturra's Blog — 性能/网络/Linux内核"
author: "Caturra"
url: "https://www.bluepuni.com/archives/"
summary: "高质量技术博客，涵盖C++性能优化、Linux内核机制（调度/内存/IO）、网络协议（TCP/packetdrill）和eBPF工作原理"
tags: [linux, networking, tcp, kernel, ebpf, cpp, performance]
created: 2026-05-28
---

# Caturra's Blog

## 核心内容

高质量技术博客，涵盖性能优化、Linux 内核、网络协议、C++ 等领域。

### 精选文章

#### Networking (网络)
| 日期 | 文章 | 主题 |
|------|------|------|
| 2024-05-15 | 使用packetdrill观测TCP backlog | TCP tuning |
| 2024-05-22 | 使用packetdrill观测TCP状态转移 | TCP internals |
| 2023-08-15 | RFC5681笔记，TCP Tahoe/TCP Reno | TCP congestion |
| 2024-06-06 | 实现一个内核态web服务器 | kernel networking |
| 2023-11-27 | 适配io_uring到std::execution | async networking |

#### Performance (性能)
| 日期 | 文章 | 主题 |
|------|------|------|
| 2024-01-23 | A Top-Down Method性能分析论文 | CPU微架构 |
| 2024-01-13 | LLVM-MCA静态性能分析 | 编译器分析 |
| 2024-01-25 | 浅谈系统性能工作流 | 性能方法论 |
| 2024-01-24 | 浅谈系统性能基本理论 | 理论基础 |
| 2024-08-08 | 浅读perfbook | 性能工程 |

#### Linux Kernel (Linux内核)
| 日期 | 文章 | 主题 |
|------|------|------|
| 2024-07-15 | Linux内核io_uring任务调度 | io_uring |
| 2024-07-07 | Linux内核ftrace实现 | tracing |
| 2024-06-26 | IO指标跟踪点 | iostat |
| 2024-08-04 | 抢占调度和nvcsw/nivcsw | scheduler |
| 2024-04-09 | Linux内存回收机制 | mm |
| 2024-04-15 | Linux中断机制 | interrupt |
| 2025-07-04 | Linux内核XArray | 数据结构 |

#### eBPF
| 日期 | 文章 | 主题 |
|------|------|------|
| 2024-06-17 | eBPF工作原理 | eBPF基础 |

#### C++ Optimization (C++优化)
| 日期 | 文章 | 主题 |
|------|------|------|
| 2020-11-08 | 通过滑动窗口来优化vector | SIMD优化 |
| 2021-02-17 | C++ std::sort流程分析 | 算法分析 |
| 2025-12-25 | SIMD字符集查找算法 | SIMD |
| 2025-10-19 | C++显式ILP实践 | 指令级并行 |
| 2025-09-19 | x86 REP_GOOD/ERMS/FSRS特性 | CPU特性 |

## 相关页面

- [[entities/linux/network/linux-network-protocols]] — TCP/UDP协议实现
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — Linux网络子系统
- [[entities/linux/ebpf/ebpf-networking]] — eBPF网络
- [[entities/cpp/cpp-perf-optimization]] — C++性能优化
