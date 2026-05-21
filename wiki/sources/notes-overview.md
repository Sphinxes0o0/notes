---
type: source
source-type: github
path: raw/github/notes/
title: "notes — Sphinx 技术笔记"
owner: Sphinxes0o0
repo: notes
branch: main
snapshot_sha: 4272d9ccbce282b7cf434c4dbfcb64b125577b67
date: 2026-05-20
url: https://github.com/Sphinxes0o0/notes
summary: "个人技术知识库：Linux 内核各子系统深度分析、QEMU 虚拟化、C/C++、操作系统、网络、数据结构与设计模式"
topics: [linux-kernel, cpp, os, networking, virtualization, qemu, data-structures, design-patterns]
tags: [general]
created: 2026-05-20
---

# notes — Sphinx 技术笔记

> 来源：[[sources/github-sphinxes0o0-notes]]
> 快照：`4272d9c`

## 概述

个人技术知识库，30+ 个子目录，涵盖 Linux 内核、QEMU 虚拟化、C/C++、操作系统基础、数据结构等。

## 核心模块

### Linux 内核子系统
- entity-linux-kernel — 内核总览
- **mm/** — 内存管理（buddy/slub allocator, VMA, swap, page fault, reclaim, compaction, migration, OOM, memcg）
- **sched/** — 进程调度（CFS, RT, load balance, context switch）
- **block/** — 块设备层（bio, request, blk-mq, IO scheduler）
- **net/** + **netfilter/** — 网络栈与防火墙
- **virt/** — KVM 虚拟化（vCPU, MMU, memory, interrupt, virtio）
- **io_uring/** — 异步 IO 引擎
- **rcu/** + **locking/** — 同步与锁机制
- **vfs/** — 虚拟文件系统
- **time/** + **sound/** + **crypto/** — 其他子系统

### QEMU
- QOM 对象模型、内存/CPU 模拟、block 层、热迁移、网络核心、QAPI、VNC

### 编程 & 基础
- **ccpp/** — C/C++ 深入
- **os/** + **os_fundamentals/** — 操作系统理论与实践
- **sys/** — 系统编程（ELF, IPC, 设计模式 C++ 实现）
- **datastructure/** — 数据结构与算法
- **design_patterns/** — GoF 23 种设计模式
- **network_fundamentals/** — 网络基础

### 其他
- **security/** — 安全工具
- **midware/** — 汽车中间件
- **interview/** — 面试准备
- **openbmc/** — OpenBMC

## 待 Ingest

以下模块尚未处理：

- [ ] kernel/ 各子系统 → entities/linux-kernel/
- [ ] qemu/ → entities/qemu/
- [ ] os/ + os_fundamentals/ → entities/os/
- [ ] ccpp/ → entities/cpp/
- [ ] datastructure/ + design_patterns/
- [ ] network/ + netfilter/
