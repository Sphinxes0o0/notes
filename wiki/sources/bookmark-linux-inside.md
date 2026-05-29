---
type: source
source-type: web
title: "Linux Inside"
author: "0xax"
date: 2026-05-28
size: medium
path: https://0xax.gitbooks.io/linux-insides/content/index.html
summary: "Linux内核入门书籍，涵盖启动、初始化、中断、系统调用、计时器、同步原语、内存管理、Cgroups等核心概念"
tags: [linux-kernel, boot, initialization, interrupt, system-call, memory-management, synchronization]
created: 2026-05-28
---

# Linux Inside

来源: [0xax.gitbooks.io/linux-insides](https://0xax.gitbooks.io/linux-insides/content/index.html) — Linux内核入门经典

## 核心内容

### 主要章节

| 章节 | 主题 |
|------|------|
| **Booting** | bootloader→kernel过渡、内核解压、KASLR |
| **Initialization** | 内核入口、调度器初始化、RCU初始化 |
| **Interrupts** | 中断处理、异常处理、NMI、softirq/tasklet/workqueue |
| **System Calls** | 系统调用机制、vsyscall/vDSO、程序执行 |
| **Timers** | clocksource、tick broadcast、dyntick、clockevents |
| **Synchronization** | spinlock、semaphore、mutex、RW semaphore、seqlock、RCU、lockdep |
| **Memory Management** | memblock、fixmap/ioremap、kmemcheck |
| **Cgroups** | Control Groups 控制组 |
| **Data Structures** | 链表、radix tree、bit arrays |
| **Theory** | paging、ELF64、inline assembly |

## 资源特点

- **入门友好**: 结构清晰，适合内核初学者建立全局视图
- **覆盖全面**: 从启动到核心子系统都有涉及
- **开源可读**: GitHub 上有对应源码仓库
- **持续更新**: 跟随内核版本演进

## 与现有资源的互补

- 覆盖 **boot/initialization** 阶段（notes-kernel 较少涉及）
- **Cgroups** 章节（notes-kernel 未深入）
- **Data Structures** 理论（通用算法层面）

## 相关页面

- [[wiki/kernel-subsystems-index]] — 内核子系统总览
- [[notes-kernel]] — Sphinx 内核笔记（源码级深度）
- [[bookmark-wowotech-linux-kernel]] — 蜗窝科技（ARM64/嵌入式视角）
- [[bookmark-linux-kernel-labs]] — Linux Kernel Labs（教学+实验）
- [[bookmark-linux-kernel-explorer]] — Kernel Explorer（交互式源码地图）
