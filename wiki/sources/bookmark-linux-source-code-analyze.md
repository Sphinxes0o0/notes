---
type: source
source-type: github
title: "Linux内核源码分析 by liexusong"
author: "liexusong"
date: 2026-05-28
size: medium
path: https://github.com/liexusong/linux-source-code-analyze
summary: "60+文档覆盖进程管理、内存、文件系统、网络、容器、epoll、iowait、HugePages、eBPF、ptrace、workqueue等"
tags: [linux-kernel, source-code, process-management, memory-management, filesystem, networking, containers, ebpf]
created: 2026-05-28
---

# Linux内核源码分析

来源: [github.com/liexusong/linux-source-code-analyze](https://github.com/liexusong/linux-source-code-analyze) — 1.6k stars, 356 forks

## 核心内容

### 9大主题板块

| 分类 | 话题 |
|------|------|
| **进程管理** | 进程管理、O(1)调度器、CFS调度器 |
| **同步机制** | 并发保护、等待队列、seqlock、RCU |
| **内存管理** | 物理内存、buddy系统、slab、mmap、swap、vmalloc、COW、zero-copy |
| **中断处理** | 硬件中断、软件中断、系统调用 |
| **文件系统** | VFS、MINIX、块层、直接I/O、native AIO、inotify |
| **网络协议栈** | Socket、Unix domain、TUN/TAP、LVS、ARP、IP、UDP、TCP、bridge |
| **进程间通信** | 消息队列、信号量、共享内存 |
| **容器技术** | Namespace、CGroup、OverlayFS |
| **高级专题** | Epoll、iowait、HugePages、eBPF、ptrace、workqueue |

## 资源特点

- **Star最多**: 1.6k stars，最受欢迎的中文内核源码分析项目
- **话题最广**: 60+文档，覆盖面极广
- **中文优先**: 适合中文读者深入理解内核
- **新增eBPF**: 包含 eBPF 专题

## 关键亮点

### NIDS 相关重点

| 话题 | 相关性 |
|------|--------|
| **Epoll** | 高性能网络事件监控，IDS核心 |
| **Netfilter** | 包过滤连接跟踪 |
| **TUN/TAP** | 报文捕获/注入 |
| **TCP/UDP协议栈** | 协议解析 |
| **eBPF** | XDP/TC钩子，IDS新范式 |
| **iowait** | 存储I/O对网络延迟影响 |
| **workqueue** | 异步任务处理 |

## 相关页面

- [[notes-kernel]] — Sphinx 内核笔记（更多细分话题）
- [[bookmark-wowotech-linux-kernel]] — 蜗窝科技（ARM64视角）
- [[bookmark-linux-kernel-labs]] — Linux Kernel Labs（教学+实验）
- [[wiki/kernel-net-index]] — 网络子系统索引
- [[wiki/ebpf-index]] — eBPF生态索引
