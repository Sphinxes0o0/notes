---
type: source
source-type: web
title: "Linux内核教学"
author: "Linux Kernel Labs"
date: 2026-05-28
size: medium
path: https://linux-kernel-labs-zh.xyz/index.html
summary: "Linux内核教学课程，包含理论+实验，覆盖内存管理、进程调度、系统调用、 interrupt、lock、VM等"
tags: [linux-kernel, course, tutorial, memory-management, scheduling, system-call, interrupt, locking, vm]
created: 2026-05-28
---

# Linux内核教学

来源: [linux-kernel-labs-zh.xyz](https://linux-kernel-labs-zh.xyz/index.html) — 中文内核教学课程

## 核心内容

### 课程结构

| 模块 | 内容 |
|------|------|
| **理论** | 内核概念、架构、内存管理基础 |
| **内存管理** | 物理/虚拟内存、分配器、mmap |
| **进程调度** | 调度算法、上下文切换、负载均衡 |
| **系统调用** | 用户/内核接口、参数传递 |
| **中断处理** | 硬中断/软中断、异常处理 |
| **同步原语** | spinlock、semaphore、mutex、RCU |
| **虚拟内存** | 页表、mmu、swap |

### 实验环节

每个模块配有实验代码和指导，加深对内核机制的理解。

## 资源特点

- **教学导向**: 理论与实践结合
- **中文内容**: 中文内核教学资源
- **结构化**: 适合系统学习而非零散参考
- **实验驱动**: 强调动手实践

## 与现有资源互补

- 补充 notes-kernel 缺少的 **实验环节**
- 比 Linux Inside 更适合 **系统学习路径**

## 相关页面

- [[wiki/kernel-mm-index]] — 内存管理索引
- [[wiki/kernel-sched-index]] — 调度器索引
- [[wiki/kernel-subsystems-index]] — 内核子系统总览
- [[wiki/sources/bookmark-linux-inside]] — Linux Inside（理论为主）
- [[wiki/sources/notes-kernel]] — Sphinx 内核笔记（源码深度）
