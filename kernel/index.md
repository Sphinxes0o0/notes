---
layout: page
title: Linux 内核深度分析
description: Linux 内核各子系统的深入分析笔记
---

# Linux 内核深度分析

本部分收录 Linux 内核各子系统的深入分析笔记。

## 子系统列表

| 子系统 | 描述 |
|---|---|
| [内存管理 (mm)](../kernel/mm/) | 内存分配、映射、回收、OOM 处理等 |
| [虚拟文件系统 (VFS)](../kernel/vfs/) | 文件系统抽象层、inode、dentry、superblock 等 |
| [块设备层 (block)](../kernel/block/) | 通用块层、I/O 调度器、多队列块层等 |
| [网络子系统 ↗](../network/linux_kernel/) | Socket、TCP/IP、Netfilter、路由等（内容位于 `/network/linux_kernel/`，内核侧边栏保留入口） |
| [Netfilter ↗](../network/linux_netfilter/) | 包过滤、连接跟踪、NAT 等（内容位于 `/network/linux_netfilter/`） |
| [调度器 (sched)](../kernel/sched/) | CFS、实时调度、负载均衡等 |
| [同步机制 (locking)](../kernel/locking/) | 各种锁机制 |
| [RCU](../kernel/rcu/) | Read-Copy-Update 同步机制 |
| [时间管理 (time)](../kernel/time/) | 时间戳、定时器、时间统计等 |
| [进程间通信 (ipc)](../kernel/ipc/) | 消息队列、信号量、共享内存等 |
| [I/O Uring](../kernel/io_uring/) | 异步 I/O 接口 |
| [加密子系统 (crypto)](../kernel/crypto/) | 加密算法框架 |
| [通用库 (lib)](../kernel/lib/) | 内核通用库函数 |
| [音频子系统 (sound)](../kernel/sound/) | ALSA、音频驱动框架 |
| [虚拟化 (virt)](../kernel/virt/) | KVM、Virtio 虚拟化技术 |
| [eBPF](../kernel/ebpf/ebpf) | eBPF 虚拟机、工作原理、AF_XDP 等 |
| [OpenBMC](../openbmc/) | BMC 管理相关技术 |
