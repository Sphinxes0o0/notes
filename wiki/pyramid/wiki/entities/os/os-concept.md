---
type: entity
tags: [os, operating-system, silberschatz, textbook]
created: 2026-05-25
sources: [pdf-onedrive-batch1]
---

# Operating System Concepts

## 定义
Silberschatz, Galvin & Gagne 合著的经典操作系统教材（OS 原理），系统讲解进程管理、并发、同步、调度、内存、文件系统等核心概念。

## 关键要点

- **进程管理**: 进程状态机、 PCB、上下文切换、fork/exec
- **线程**: 用户线程 vs 内核线程、线程池模型
- **CPU 调度**: FCFS、 SJF、 RR、 多级反馈队列、 实时调度
- **进程同步**: 临界区、 互斥、 信号量、 监视器、 Peterson 算法
- **死锁**: 银行家算法、 死锁检测与恢复、 预防策略
- **内存管理**: 连续分配、 分页、 分段、 虚拟内存、 页面置换算法
- **文件系统**: 文件、 目录、 inode、 空闲空间管理、 顺序/随机访问
- **I/O 系统**: 设备调度、 缓冲、 缓存、 磁盘调度算法
- **虚拟化**: 虚拟机、 容器、 Docker、 hypervisor 架构

## 相关概念

- [[os-process-thread]] — 进程与线程
- [[os-virtual-memory]] — 虚拟内存
- [[os-io-model]] — I/O 模型
- [[linux-scheduler]] — Linux 调度器
- [[linux-memory-allocator]] — Linux 内存分配器
- [[linux-vfs]] — Linux VFS 文件系统

## 来源详情

- [[pdf-onedrive-batch1]]
