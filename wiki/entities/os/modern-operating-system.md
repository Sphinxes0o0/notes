---
type: entity
tags: [os, operating-system, chinese, virtualization, process, memory]
created: 2026-05-25
sources: [pdf-onedrive-batch1]
---

# 现代操作系统 原理与实现

## 定义
一本系统阐述操作系统原理与实现方法的中文教材，覆盖进程管理、内存管理、文件系统、I/O 子系统、虚拟化等核心主题。

## 关键要点

- **进程与线程**: 进程模型、线程实现、上下文切换、调度算法
- **内存管理**: 虚拟内存、页表机制、分页/分段、内存分配算法
- **文件系统**: VFS、inode/dentry、页缓存、顺序/随机 I/O
- **I/O 子系统**: 设备驱动模型、中断处理、缓冲区管理
- **进程同步**: 互斥锁、信号量、条件变量、经典同步问题
- **虚拟化**: 虚拟机监视器 (VMM)、容器技术、超visor 类型
- **调度**: 多级反馈队列、CFS、完全公平调度器
- **链接与加载**: ELF 格式、静态/动态链接、 PIC/GOT/PLT

## 相关概念

- [[os-process-thread]] — 进程与线程模型
- [[os-virtual-memory]] — 虚拟内存机制
- [[os-io-model]] — I/O 模型与 epoll
- [[os-linking-loading]] — ELF 链接与加载
- [[linux-scheduler]] — Linux CFS 调度器
- [[linux-memory-allocator]] — Linux 内存分配器

## 来源详情

- [[pdf-onedrive-batch1]]
