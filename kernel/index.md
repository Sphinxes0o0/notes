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
| [OpenBMC](openbmc/) | BMC 管理相关技术 |

## 深度分析索引（deep_dive）

> 多个子系统存在多份「深度分析」文件，它们按视角互补，不是重复：
> - **顶层 `*_deep_dive.md`（v2）** = 跨切面架构/算法深度（RCU、锁协议、算法复杂度）
> - **子目录 `*_deep_dive_r1`** = 子系统全景（数据结构定义）
> - **子目录 `*_deep_dive_r2`** = 子系统内某个主题深入（函数/算法源码）

各子系统分类：

### 内存管理 (MM)

| 文件 | 视角 | 体量 |
|---|---|---|
| [`mm_deep_dive_r1.md`](./mm/mm_deep_dive_r1.md) | R1 全景：Buddy / Slab / vmalloc / mmap / Page Cache | 1009 行 |
| [`mm_deep_dive_r2.md`](./mm/mm_deep_dive_r2.md) | R2 深入：SLUB Freelist / kfree / Folio / Compaction / Sheaves | 1113 行 |
| [`mm/mm_allocator_r0.md`](./mm/mm_allocator_r0.md) | 跨子系统：MM/锁/调度/网络 7 领域源码（远端重命名自 slub_allocator_deep_dive.md） | 1094 行 |

### 虚拟文件系统 (VFS)

| 文件 | 视角 | 体量 |
|---|---|---|
| [`vfs_deep_dive.md`](./vfs_deep_dive.md) | v2 架构：RCU 路径查找 / 锁协议 / 算法复杂度 | 1122 行 |
| [`vfs/vfs_deep_dive_r1.md`](./vfs/vfs_deep_dive_r1.md) | R1 数据结构：inode / dentry / super_block / file / address_space | 1405 行 |
| [`vfs/vfs_deep_dive_r2.md`](./vfs/vfs_deep_dive_r2.md) | R2 操作集：inode_operations / super_operations / file_operations | 985 行 |

### 块设备层 (Block)

| 文件 | 视角 | 体量 |
|---|---|---|
| [`block_io_deep_dive.md`](./block_io_deep_dive.md) | v2 架构：blk-mq / Bio-Request / 调度 / 写回 / blk-cgroup | 1003 行 |
| [`block/block_deep_dive_r1.md`](./block/block_deep_dive_r1.md) | R1 数据结构：bio / request / blk-mq / Scheduler / GenDisk | 768 行 |
| [`block/block_deep_dive_r2.md`](./block/block_deep_dive_r2.md) | R2 函数流程：bio_alloc / blk_mq_tagset / Plug 机制 | 799 行 |

### 调度器 (Sched)

| 文件 | 视角 | 体量 |
|---|---|---|
| [`scheduler_deep_dive.md`](./scheduler_deep_dive.md) | v2 架构：runqueue / CFS / RT / DL / 负载均衡 / PELT | 916 行 |
| [`sched/sched_deep_dive_r1.md`](./sched/sched_deep_dive_r1.md) | R1 全景：调度类 / CFS / RT / sched_domain / Per-CPU | 1303 行 |
| [`sched/sched_deep_dive_r2.md`](./sched/sched_deep_dive_r2.md) | R2 深入：pick_eevdf / calc_delta_fair / update_curr / NUMA | 882 行 |

### 同步机制 (Locking)

| 文件 | 视角 | 体量 |
|---|---|---|
| [`synchronization_deep_dive.md`](./synchronization_deep_dive.md) | v2 架构：qspinlock / 内存屏障 / RCU 宽限期 / 乐观自旋 | 853 行 |
| [`locking/locking_deep_dive_r2.md`](./locking/locking_deep_dive_r2.md) | R2 深入：锁实现源码 | 771 行 |

### 时间管理 (Time)

| 文件 | 视角 | 体量 |
|---|---|---|
| [`timekeeping_deep_dive.md`](./timekeeping_deep_dive.md) | v2 架构：NTP / hrtimer / 时钟事件 / vDSO | 823 行 |
| [`time/time_deep_dive_r1.md`](./time/time_deep_dive_r1.md) | R1 全景：时间子系统 | 1205 行 |

### 其他子系统

| 子系统 | 文件 | 视角 |
|---|---|---|
| RCU | [`rcu/rcu_deep_dive_r2.md`](./rcu/rcu_deep_dive_r2.md) | R2 深入（548 行） |
| IPC | [`ipc/ipc_deep_dive_r1.md`](./ipc/ipc_deep_dive_r1.md) | R1 全景（1778 行） |
| io_uring | [`io_uring/io_uring_deep_dive_r1.md`](./io_uring/io_uring_deep_dive_r1.md) | R1 全景（524 行） |
| 加密 | [`crypto/crypto_deep_dive_r1.md`](./crypto/crypto_deep_dive_r1.md) | R1 全景（810 行） |
| 通用库 | [`lib/lib_deep_dive_r2.md`](./lib/lib_deep_dive_r2.md) | R2 深入（980 行） |
| 音频 | [`sound/sound_deep_dive_r1.md`](./sound/sound_deep_dive_r1.md) | R1 全景（1442 行） |
| 音频 | [`sound/sound_deep_dive_r2.md`](./sound/sound_deep_dive_r2.md) | R2 深入（1023 行） |
| 虚拟化 | [`virt/virt_deep_dive_r1.md`](./virt/virt_deep_dive_r1.md) | R1 全景（936 行） |
| 虚拟化 | [`virt/virt_deep_dive_r2.md`](./virt/virt_deep_dive_r2.md) | R2 深入（1055 行） |
| Cgroups | [`cgroups_deep_dive.md`](./cgroups_deep_dive.md) | v2 架构（897 行）— kernel 下无 cgroups 子目录，挂在顶层 |

### 网络 & 安全 deep_dive（位于其他目录）

| 文件 | 视角 | 体量 |
|---|---|---|
| [`network/linux_kernel/net_deep_dive_r1.md`](../network/linux_kernel/net_deep_dive_r1.md) | Net R1 全景：Socket / sk_buff / 路由 / Netfilter / TCP-UDP | 455 行 |
| [`network/linux_netfilter/netfilter_deep_dive_r1.md`](../network/linux_netfilter/netfilter_deep_dive_r1.md) | Netfilter R1：Conntrack / NAT / Xtables | 899 行 |
| [`network/linux_netfilter/netfilter_deep_dive_r2.md`](../network/linux_netfilter/netfilter_deep_dive_r2.md) | Netfilter R2：nf_tables 深入 | 901 行 |
| [`network/linux_netfilter/netfilter_tcp_deep_dive.md`](../network/linux_netfilter/netfilter_tcp_deep_dive.md) | 网络协议栈 R2（Conntrack/NAT/TCP 综合） | 964 行 |
| [`network/network_stack_deep_dive.md`](../network/network_stack_deep_dive.md) | 网络栈 v2 架构 | 929 行 |
| [`security/linux_kernel/security_deep_dive_r1.md`](../security/linux_kernel/security_deep_dive_r1.md) | Security R1 全景 | 1148 行 |
| [`security/linux_kernel/security_deep_dive_r2.md`](../security/linux_kernel/security_deep_dive_r2.md) | Security R2 深入 | 1279 行 |
