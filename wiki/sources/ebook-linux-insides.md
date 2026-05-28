---
type: source
source-type: ebook
title: "Linux Insides 中文版"
author: "0xax (原文), 中文翻译社区"
date: 2026-05-28
size: large
path: raw/bookmarks/ebooks/linux-insides/
summary: "Linux内核入门经典书籍，涵盖引导、初始化、中断、系统调用、计时器、同步原语、内存管理、Cgroups、数据结构等核心概念（22/59章节可用）"
tags: [linux-kernel, boot, initialization, interrupt, system-call, timers, synchronization, memory-management, cgroups]
created: 2026-05-28
---

# Linux Insides 中文版

来源: [xinqiu.gitbooks.io/linux-insides-cn](https://xinqiu.gitbooks.io/linux-insides-cn/) — 0xAX 著

## 抓取概况

- **总章节数**: 59
- **成功抓取**: 22 (37%)
- **原文**: github.com/0xAX/linux-insides

## 可用章节

### Booting (引导) - 3/5
| # | 标题 | 文件 |
|---|------|------|
| 1 | 从引导加载程序内核 | 01-bootstrapping-1.md |
| 2 | 在内核安装代码的第一步 | 02-bootstrapping-2.md |
| 3 | 视频模式初始化和转换到保护模式 | 03-bootstrapping-3.md |

### Initialization (初始化) - 3/10
| # | 标题 | 文件 |
|---|------|------|
| 2 | 早期的中断和异常控制 | 07-init-2.md |
| 3 | 在到达内核入口之前最后的准备 | 08-init-3.md |
| 4 | 内核入口 - start_kernel | 09-init-4.md |

### Interrupts (中断) - 5/10
| # | 标题 | 文件 |
|---|------|------|
| 1 | 中断和中断处理第一部分 | 16-interrupts-1.md |
| 3 | 初步中断处理 | 18-interrupts-3.md |
| 8 | IRQs的非早期初始化 | 23-interrupts-8.md |
| 10 | 最后一部分 | 25-interrupts-10.md |

### SysCall (系统调用) - 2/5
| # | 标题 | 文件 |
|---|------|------|
| 2 | Linux内核如何处理系统调用 | 27-syscall-2.md |
| 4 | Linux内核如何运行程序 | 29-syscall-4.md |

### Timers (定时器) - 2/7
| # | 标题 | 文件 |
|---|------|------|
| 4 | 定时器介绍 | 34-timers-4.md |
| 5 | Clockevents框架简介 | 35-timers-5.md |

### SyncPrim (同步原语) - 2/8
| # | 标题 | 文件 |
|---|------|------|
| 1 | 自旋锁简介 | 38-sync-1.md |
| 2 | 队列自旋锁 | 39-sync-2.md |

### MM (内存管理) - 1/3
| # | 标题 | 文件 |
|---|------|------|
| 3 | kmemcheck | 43-mm-3.md |

### Concepts (概念) - 3/4
| # | 标题 | 文件 |
|---|------|------|
| 2 | CPU掩码 | 46-concepts-2.md |
| 3 | initcall机制 | 47-concepts-3.md |
| 4 | Linux内核的通知链 | 48-concepts-4.md |

### Theory (理论) - 1/5
| # | 标题 | 文件 |
|---|------|------|
| 3 | 內联汇编 | 54-inline-asm.md |

### Misc (杂项) - 1/5
| # | 标题 | 文件 |
|---|------|------|
| 4 | 用户空间的程序启动过程 | 58-misc-4.md |

## 核心内容摘要

### 引导与初始化 (Booting/Initialization)
- **实模式→保护模式**: BIOS POST → MBR → GRUB → 实模式到保护模式过渡
- **内核解压**: KASLR, relocatable kernel
- **start_kernel**: 调度器初始化、RCU 初始化、initcall 机制

### 中断处理 (Interrupts)
- **IDT (中断描述符表)**: 中断门/陷阱门/任务门
- **中断处理流程**: 保存上下文 → 分发 → 处理 → 恢复
- **软中断 (Softirq)**: Timer softirq, NET softirq, Tasklet
- **Per-CPU 中断栈**: IRQ_STACK_SIZE, irq_stack_union

### 系统调用 (SysCall)
- **sys_call_table**: 数组实现，arch/x86/entry/syscall_64.c
- **IA32_LSTAR MSR**: syscall 入口点寄存器
- **entry_SYSCALL_64**: 用户→内核切换，SWAPGS, 保存寄存器
- **返回**: USERGS_SYSRET64 → swapgs + sysretq

### 定时器 (Timers)
- **jiffies**: 系统节拍计数器
- **tvec_base**: per-CPU 动态定时器基数 (tv1-tv5 级联)
- **clockevents**: 动态定时器框架
- **tick broadcast**: NO_HZ 模式下跨 CPU 时钟广播

### 同步原语 (Synchronization)
- **Spinlock**: ticket spinlock (基于 ticket 的排队自旋锁)
- **QSpinlock**: 队列自旋锁 (CONFIG_QUEUED_SPINLOCKS)
- **Per-CPU 变量**: __per_cpu_offset, percpu 变量机制

### 其他概念
- **CPU masks**: 操作系统管理 CPU 集合的位图
- **通知链 (Notifier Chain)**: 内核模块间事件通知机制
- **initcall**: 内核初始化时的函数调用层次

## 与现有资源的互补

- 覆盖 **boot/initialization** 阶段（notes-kernel 较少涉及）
- **Cgroups** 章节（notes-kernel 未深入）
- **Data Structures** 理论（通用算法层面）

## 相关页面

- [[wiki/sources/bookmark-linux-inside]] — Linux Inside bookmark 源
- [[wiki/kernel-subsystems-index]] — 内核子系统总览
- [[wiki/sources/notes-kernel]] — Sphinx 内核笔记（源码级深度）
- [[wiki/sources/bookmark-wowotech-linux-kernel]] — 蜗窝科技（ARM64/嵌入式视角）

## Related Concepts

- [[entities/linux/kernel/vfs/linux-kernel-vfs-core]] — VFS (系统调用接口)
- [[entities/linux/kernel/locking/linux-kernel-locking-core]] — 锁原语 (同步原语)
- [[entities/linux/kernel/time/linux-kernel-time-core]] — 时间管理 (定时器)
- [[entities/linux/kernel/rcu/linux-kernel-rcu-core]] — RCU (同步原语)
- [[entities/linux/kernel/smp/linux-kernel-smp]] — SMP 多核 (per-CPU 变量、CPU masks)
- [[entities/linux/kernel/syscall/linux-kernel-syscall]] — 系统调用机制 (entry_SYSCALL_64, sys_call_table)
