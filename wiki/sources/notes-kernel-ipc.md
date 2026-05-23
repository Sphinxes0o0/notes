---
type: source
source-type: github
title: "Linux Kernel IPC Subsystem Notes"
author: "notes repo"
date: 2026-05-20
size: small
path: raw/github/notes/ipc/linux_kernel/
summary: "Linux内核IPC子系统：msg、sem、shm、mqueue消息队列、信号量、共享内存"
tags: [linux-kernel, ipc]
sources: [notes-kernel-ipc]
created: 2026-05-20
---

# Linux Kernel IPC Subsystem Notes

## 来源信息

- **路径**: raw/github/notes/ipc/linux_kernel/
- **文件数**: 3个文档（index + 2个分析文档）
- **类型**: 内核源码分析笔记

## 核心内容

- **ipc_subsystem.md**: msg、sem、shm、mqueue核心API
- **ipc_deep_dive_r1.md**: 消息算法、sem undo、shm mmap、mqueue

## 关键概念

- 消息队列: pipelined_send直接传递
- 信号量: perform_atomic_semop原子操作 + sem_undo退出撤销
- 共享内存: shm_nattch引用计数、hugetlb大页
- mqueue: 红黑树按优先级、通知机制SIGEV_*

## 相关页面
- [[entities/linux/kernel/ipc/linux-kernel-ipc-core]]
