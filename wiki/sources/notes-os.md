---
type: source
source-type: github
title: "操作系统学习笔记"
author: "notes (github/notes)"
date: 2026-05-20
size: medium
path: raw/github/notes/os/
summary: "Linux 内核深度分析：VFS、调度器、SLUB 分配器、cgroups 架构详解"
tags: [linux, os]
sources: [notes-os]
created: 2026-05-20
---

# 操作系统学习笔记

## 核心内容

操作系统学习笔记，包含 Linux 内核开发指南和深度架构分析。

### Linux 内核深度分析

- **VFS**: dentry/inode 缓存、RCU 路径查找、页缓存管理
- **调度器**: CFS 红黑树、RT/Deadline 调度、负载均衡、PELT
- **SLUB 分配器**: sheaf 机制、cmpxchg16b、Buddy 系统
- **cgroups**: CSS 机制、v2 单层级、CPU/内存控制器

### 核心主题

- 页表管理与 TLB shootdown
- 内存回收算法 (VMSCAN)
- TCP 协议栈与网络收包流程
- 锁与同步机制 (RCU、内存顺序)

## 相关页面

- [[entities/os/linux-vfs]]
- [[entities/os/linux-scheduler]]
- [[entities/os/linux-memory-allocator]]
- [[entities/os/linux-cgroups]]
