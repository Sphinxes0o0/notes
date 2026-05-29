---
type: source
source-type: web
title: "Linux性能优化实战"
author: "lianglianglee"
date: 2023-01-01
size: medium
path: https://learn.lianglianglee.com/专栏/Linux性能优化实战
summary: "Linux性能优化：CPU/内存/磁盘IO/网络perf工具链(perf/bpftrace/top/vmstat/iostat/sar/tcpdump/ss)及典型瓶颈场景"
nids-relevance: 4
---

# Linux性能优化实战

## 核心内容

### 性能优化维度

| 维度 | 内容 |
|------|------|
| **CPU** | 热点分析、调度优化、上下文切换 |
| **内存** | 缓存命中率、OOM分析、SLUB/SLAB |
| **磁盘IO** | IOPS、吞吐量、blk-mq |
| **网络** | TCP参数、拥塞控制、软中断 |

### 性能工具链

| 工具 | 用途 |
|------|------|
| `perf` | CPU profiling,热点分析,branch prediction |
| `bpftrace` | 动态内核追踪,任意位置probe |
| `top/htop` | 进程/线程监控,CPU/内存使用 |
| `vmstat` | 虚拟内存统计,swap in/out |
| `iostat` | 磁盘IO统计,IOPS/吞吐量 |
| `sar` | 系统活动报告,历史数据分析 |
| `tcpdump` | 网络包抓取,协议分析 |
| `ss` | Socket统计,连接状态分析 |
| `bcc/tools` | eBPF性能分析工具集 |

### 典型问题场景

| 症状 | 根因 | 排查工具 |
|------|------|----------|
| CPU 100%但吞吐低 | 锁竞争/IO阻塞 | perf top, strace |
| 内存泄漏 | 堆外内存泄漏 | bpftrace, pmaps |
| 网络延迟高 | TCP参数/拥塞控制 | ss, tcpdump |
| 软中断不均衡 | RSS/RPS配置 | /proc/interrupts |

### NIDS Relevance

1. **性能瓶颈定位**: NIDS丢包通常因CPU/内存/网络瓶颈，用perf/bpftrace定位
2. **软中断优化**: 网络包处理依赖softirq，优化RX/TX平衡
3. **TCP参数调优**: net.core.somaxconn、net.ipv4.tcp_max_syn_backlog等影响NIDS连接处理
4. **eBPF观测**: bpftrace/bcc工具可实时观测NIDS数据包处理路径
5. **缓存优化**: NIDS flow table缓存命中率影响检测性能

## 相关页面

- [[arthurchiao-linux-net-stack]] — Linux网络栈概览
- [[arthurchiao-linux-irq-softirq]] — IRQ/softirq机制
- [[reading-software-performance-deep-thinking]] — 软件性能理论
- [[wiki/entities/kernel-bypass-dpdk]] — Kernel bypass性能提升
