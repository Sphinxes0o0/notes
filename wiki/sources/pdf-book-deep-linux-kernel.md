---
type: source
source-type: pdf
title: 深入理解 Linux 内核
author: Robert Love
date: 2005
size: small
path: raw/PDFs/books/深入理解Linuxkenrle.pdf
summary: Linux 内核设计原理：调度/内存/文件系统/进程/中断的系统级分析
created: 2005
tags: [linux]
---
# 深入理解 Linux 内核

## 核心内容

- **调度器**：CFS 原理、调度类、负载计算、 SMP load balance
- **内存管理**：页表结构、kmalloc、vmalloc、memory zone
- **进程管理**：fork/exec/wait、task_struct、命名空间
- **文件系统**：VFS superblock/inode/dentry、page cache、writeback
- **同步原语**：spinlock/rcu/semaphore/mutex 与适用场景
- **中断与异常**：IRQ、软中断、tasklet、workqueue

## 相关页面
- [[pdf-book-linux-kernel-commentary]]
- [[pdf-linux-kernel-books]]
- [[pdf-bpf-rethinking-linux-kernel]]