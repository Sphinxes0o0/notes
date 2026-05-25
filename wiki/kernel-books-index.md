---
type: index
tags: [linux, kernel, books, navigation]
created: 2026-05-25
---

# Linux/Kernel Books Index

> 本索引聚合所有 Linux/Kernel 相关的 PDF 书籍来源，按主题分类。
>
> Last updated: 2026-05-25 | Batch K ingest

---

## Linux Kernel Architecture

| 书名 | 作者 | 页数 | 来源 | 核心主题 |
|------|------|------|------|----------|
| 深入理解 Linux 内核 | Bovet & Cesati | 944 | [[sources/pdf-linux-kernel-books]] | 内存管理、进程调度、VFS、网络、I/O |
| Linux 内核 0.12 完全注释 | 赵炯 | 1016 | [[sources/pdf-linux-kernel-books]] | 内核 0.12 源码逐行注释，MINIX fs，早期设计 |

---

## Linux System Programming

| 书名 | 作者 | 页数 | 来源 | 核心主题 |
|------|------|------|------|----------|
| The Linux Programming Interface | Michael Kerrisk | 1556 | [[sources/pdf-the-linux-programming-interface]] | 500+ 系统调用，64章节，系统编程百科 |
| UNIX 环境高级编程（第三版） | Stevens & Rago | 822 | [[sources/pdf-unix-environment-advanced-programming]] | POSIX 标准，系统编程经典（扫描版）|

---

## Linux Network / Server Programming

| 书名 | 作者 | 页数 | 来源 | 核心主题 |
|------|------|------|------|----------|
| Linux 高性能服务器编程 | 游毓贵 | 363 | [[sources/pdf-linux-net-server]] | TCP/IP、I/O 模型、epoll、服务器架构 |
| Linux 多线程服务端编程：muduo | 陈硕 | 151 | [[sources/pdf-linux-net-server]] | one loop per thread，Reactor，muduo C++ 库 |
| LwIP 协议栈源码详解 | 老衲五木 | 99 | [[sources/pdf-linux-net-server]] | 嵌入式 TCP/IP，pbuf/netif/TCP 状态机 |

---

## Concurrency & Parallel Programming

| 书名 | 作者 | 页数 | 来源 | 核心主题 |
|------|------|------|------|----------|
| OSTEP Concurrency（线程与锁） | Arpaci-Dusseau | 22 | [[sources/pdf-concurrency-perf]] | 线程/锁/条件变量/信号量/死锁 |
| Is Parallel Programming Hard? (perfbook) | Paul E. McKenney | 601 | [[sources/pdf-concurrency-perf]] | RCU、无锁同步、内存屏障、内存模型 |

---

## Computer Systems (Foundational)

| 书名 | 作者 | 页数 | 来源 | 核心主题 |
|------|------|------|------|----------|
| Computer Systems: A Programmer's Perspective | Bryant & O'Hallaron | 1078 | [[sources/pdf-computer-systems-programmers-perspective]] | 机器码/缓存/虚拟内存/链接/并发，CS:APP |

---

## Key Entity Pages

> 由上述书籍内容提炼的核心概念页面

- [[entities/linux/virtual-memory-systems]] — 虚拟内存系统（CS:APP + TLPI）
- [[entities/linux/process-management-model]] — 进程与线程管理（TLPI + APUE）
- [[entities/linux/machine-code-programmers-perspective]] — 机器码与汇编（CS:APP）

---

## Kernel Subsystem Entities

> 各子系统详细 entity 页面（来自 notes/kernel 和内核注释）

**Memory Management:**
- [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]] — SLUB 分配器
- Page Fault — 缺页中断处理
- Swap — Swap 与页面回收
- Page Reclaim — kswapd/Multi-Gen LRU
- mmap — 虚拟内存区域（VMA/Maple Tree）

**Scheduler:**
- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — CFS/EEVDF 调度器
- CFS Scheduler — 完全公平调度
- Context Switch — 上下文切换
- Load Balance — SMP 负载均衡

**Block I/O:**
- [[entities/linux/kernel/block/linux-kernel-block-core]] — bio/request/gendisk
- blk-mq — blk-mq 多队列
- IO Scheduler — I/O 调度器（mq-deadline/BFQ）

**Networking:**
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — Socket/sk_buff/Netdevice
- Network Protocols — TCP/UDP/IP 协议实现
- [[kernel-net-index]] — 网络子系统索引

**Other Subsystems:**
- [[entities/linux/kernel/locking/linux-kernel-locking-core]] — spinlock/mutex/rwsem
- [[entities/linux/kernel/rcu/linux-kernel-rcu-core]] — RCU 同步
- [[entities/linux/kernel/ipc/linux-kernel-ipc-core]] — IPC（msg/sem/shm/mqueue）
- KVM — KVM 虚拟化
- io_uring — io_uring
- VFS — VFS（dentry/inode/file）

---

## Module Indexes

| Index | 描述 |
|-------|------|
| [[kernel-mm-index]] | 内存管理子系统（SLUB/页Cache/回收/mmap） |
| [[kernel-sched-index]] | CPU 调度子系统（CFS/上下文切换/负载均衡） |
| [[kernel-block-index]] | 块 I/O 子系统（bio/request/blk-mq） |
| [[kernel-net-index]] | 网络子系统（Socket/sk_buff/Netfilter/TCP） |
| [[kernel-subsystems-index]] | 内核其他子系统（Crypto/Locking/IPC/RCU/Time/Sound） |
| [[kernel-virt-index]] | 虚拟化（KVM/Virtio） |
| [[kernel-io-index]] | I/O 模型（io_uring/VFS） |
| [[os-index]] | 操作系统综合（进程/线程/内存/I/O） |
| [[sys-prog-index]] | 系统编程（C/Linux/工具/安全） |

---

## ARM Architecture

| 书名 | 作者 | 页数 | 来源 | 核心主题 |
|------|------|------|------|----------|
| DDI0388H Cortex-A9 TRM | ARM | - | [[sources/pdf-arm-architecture]] | Cortex-A9 技术参考手册 |
| DDI0487Fc ARMv8 ARM | ARM | - | [[sources/pdf-arm-architecture]] | ARMv8 架构参考手册 |
| ARM Architecture Reference (A-profile) | ARM | - | [[sources/pdf-arm-architecture]] | A-profile 架构手册 |
| 手机安全和可信应用开发指南：TrustZone与OP-TEE | - | - | [[sources/pdf-security-crypto-books-updated]] | TrustZone/OP-TEE/安全/SE |

---

## ARM Entities

| Entity | 描述 |
|--------|------|
| ARM Cortex-A9 TRM | Cortex-A9 微架构：超标量/双发射/NEON/VFPv3 |
| ARMv8-A Architecture | ARMv8-A (AArch64) 架构：异常级别/寄存器/指令集 |
| TrustZone/OP-TEE | TrustZone TEE + OP-TEE 安全可信执行环境 |
| Computer Architecture | 计算机体系结构：量化研究方法 (Hennessy & Patterson) |

---

← [[home|Back to Home]]
