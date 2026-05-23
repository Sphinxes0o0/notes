---
type: source
source-type: github
tags: [system-programming, linux]
path: raw/github/notes/sys/
sources: [notes-sys]
created: 2026-05-22
---

# 系统编程笔记

## Overview

系统编程学习笔记，涵盖 TTY/Shell/Console 终端体系、ELF 文件格式、Linux 进程间通信（IPC）机制。深入分析终端设备驱动、Shell 会话生命周期、ELF 编译链接流程、管道/mmap/信号等 IPC 机制。

## Key Topics

- **TTY/Shell/Console 体系**：
  - TTY 演化：电传打字机 → Unix 终端设备 → 伪终端（PTY）
  - PTY 架构：ptmx master 与 pts/X slave 多路复用
  - Shell 类型：sh、bash、zsh、fish 及生命周期管理
  - Console 与 TTY 的区别：物理直连 vs 软件模拟
- **ELF 文件格式**：Header、Program Header Table、Section Header Table；.text/.rodata/.data/.bss 等关键 Section；readelf/objdump/nm 工具链
- **Linux IPC**：管道（匿名/FIFO）、mmap、信号、消息队列、共享内存、信号量；Socket 网络通信
- **设计模式**：单例模式（饿汉/懒汉双检锁/Meyer's Singleton）

## Related Entities

- [[entities/sys]] — 系统编程实体页（ELF、IPC、设计模式详解）
- [[entities/cpp]] — C/C++ 语言基础
