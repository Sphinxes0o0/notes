---
title: System Programming Notes
---

# 系统编程学习笔记

欢迎来到系统编程学习笔记部分！这里包含了我在学习系统编程和底层开发过程中的各种笔记和总结。

## 目录结构

### 设计模式
- [单例模式](./design_pattern/singleton.md) - 单例设计模式的实现和应用

### 系统编程基础
- [ELF 文件格式](./fundamentals/elf.md) - 可执行文件格式详解
- [Linux 系统编程](./fundamentals/linux_system_programming.md) - Linux 系统编程基础

### 进程间通信 (IPC)
- [Linux IPC](./ipc/linux_ipc.md) - Linux 进程间通信机制总览
- [共享内存](./ipc/shm/shm.md) - 共享内存 IPC 机制
- [邮箱机制](./ipc/mailbox/lwip_mailbox.md) - 邮箱式 IPC 实现

### 安全工具
- [Masscan](/security/masscan/ARCHITECTURE) - 互联网规模高速端口扫描器
- [Falco](/security/falco/ARCHITECTURE) - 云原生运行时安全工具

## 学习目标

通过系统学习系统编程，掌握：

1. **底层机制** - 理解操作系统底层运行机制
2. **系统调用** - 掌握系统调用的使用和实现
3. **进程管理** - 学习进程创建、通信和同步
4. **内存管理** - 理解内存分配和管理策略
5. **文件操作** - 掌握文件 I/O 和文件系统操作
6. **网络编程** - 学习网络编程和协议实现

## 实践项目

- **共享内存哈希表** - 基于共享内存的并发哈希表实现
- **邮箱通信** - 轻量级进程间通信机制
- **系统工具** - 各种系统编程工具和实用程序
