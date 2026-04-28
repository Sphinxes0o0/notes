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
| [内存管理 (mm)](../mm/) | 内存分配、映射、回收、OOM 处理等 |
| [虚拟文件系统 (VFS)](../vfs/) | 文件系统抽象层、inode、dentry、superblock 等 |
| [块设备层 (block)](../block/) | 通用块层、I/O 调度器、多队列块层等 |
| [网络子系统](../net/) | Socket、TCP/IP、Netfilter、路由等 |
| [Netfilter](../netfilter/) | 包过滤、连接跟踪、NAT 等 |
| [调度器 (sched)](../sched/) | CFS、实时调度、负载均衡等 |
| [同步机制 (locking)](../locking/) | 各种锁机制 |
| [RCU](../rcu/) | Read-Copy-Update 同步机制 |
| [时间管理 (time)](../time/) | 时间戳、定时器、时间统计等 |
| [进程间通信 (ipc)](../ipc/) | 消息队列、信号量、共享内存等 |
| [I/O Uring](../io_uring/) | 异步 I/O 接口 |
| [加密子系统 (crypto)](../crypto/) | 加密算法框架 |
| [通用库 (lib)](../lib/) | 内核通用库函数 |
| [音频子系统 (sound)](../sound/) | ALSA、音频驱动框架 |
| [虚拟化 (virt)](../virt/) | KVM、Virtio 虚拟化技术 |
| [OpenBMC](../openbmc/) | BMC 管理相关技术 |
