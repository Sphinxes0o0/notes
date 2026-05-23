---
type: source
source-type: github
title: "Sphinx 技术笔记 - Linux 内核"
author: Sphinxes0o0
date: 2026-05-20
size: medium
path: raw/github/notes/
summary: Linux 内核各子系统深度分析笔记，包含 mm、sched、block、VFS、网络、虚拟化等
tags: [linux-kernel]
sources: [notes-kernel]
created: 2026-05-20
---

# Sphinx 技术笔记 - Linux 内核

来源: [github.com/Sphinxes0o0/notes](https://github.com/Sphinxes0o0/notes) — Linux 内核深度分析笔记

## 子系统概览

| 子系统 | 描述 | Entity 页面 |
|--------|-------|-------------|
| MM: SLUB Allocator | slab 内存分配器 | [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]] |
| MM: Page Fault | 缺页中断处理 | [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]] |
| MM: Swap | Swap 交换子系统 | [[entities/linux/kernel/mm/linux-kernel-mm-swap]] |
| MM: Page Reclaim | 页面回收机制 | [[entities/linux/kernel/mm/linux-kernel-mm-page-reclaim]] |
| MM: Memory Mapping | mmap 内存映射 | [[entities/linux/kernel/mm/linux-kernel-mm-mmap]] |
| Sched: Core | 调度器核心 | [[entities/linux/kernel/sched/linux-kernel-sched-core]] |
| Sched: CFS | CFS 完全公平调度器 | [[entities/linux/kernel/sched/linux-kernel-sched-cfs]] |
| Sched: Context Switch | 上下文切换 | [[entities/linux/kernel/sched/linux-kernel-sched-context-switch]] |
| Sched: Load Balance | 负载均衡 | [[entities/linux/kernel/sched/linux-kernel-sched-load-balance]] |
| Block: Core | 块设备层核心 | [[entities/linux/kernel/block/linux-kernel-block-core]] |
| Block: MultiQueue | blk-mq 多队列 | [[entities/linux/kernel/block/linux-kernel-block-mq]] |
| Block: I/O Scheduler | I/O 调度器 | [[entities/linux/kernel/block/linux-kernel-block-scheduler]] |

## 源文件索引

### 内存管理 (mm/)

- `raw/github/notes/kernel/mm/linux_kernel/index.md` — MM 子系统总览
- `raw/github/notes/mm/linux_kernel/mm_allocator.md` — SLUB 分配器
- `raw/github/notes/mm/linux_kernel/mm_page_fault.md` — 缺页中断
- `raw/github/notes/mm/linux_kernel/mm_swap.md` — Swap 子系统
- `raw/github/notes/mm/linux_kernel/mm_page_reclaim.md` — 页面回收
- `raw/github/notes/mm/linux_kernel/mm_mmap.md` — mmap 内存映射
- `raw/github/notes/mm/linux_kernel/mm_core_structs.md` — 核心数据结构
- `raw/github/notes/mm/linux_kernel/mm_deep_dive_r1.md` — 深度分析 R1
- `raw/github/notes/mm/linux_kernel/mm_deep_dive_r2.md` — 深度分析 R2

### 调度器 (sched/)

- `raw/github/notes/kernel/sched/linux_kernel/index.md` — Sched 子系统总览
- `raw/github/notes/sched/linux_kernel/sched_core.md` — 调度器核心
- `raw/github/notes/sched/linux_kernel/sched_cfs.md` — CFS 调度器
- `raw/github/notes/sched/linux_kernel/sched_context_switch.md` — 上下文切换
- `raw/github/notes/sched/linux_kernel/sched_load_balance.md` — 负载均衡
- `raw/github/notes/sched/linux_kernel/sched_class.md` — 调度类框架
- `raw/github/notes/sched/linux_kernel/sched_rt.md` — RT 调度器
- `raw/github/notes/sched/linux_kernel/sched_deep_dive_r1.md` — 深度分析 R1

### 块设备层 (block/)

- `raw/github/notes/kernel/block/linux_kernel/index.md` — Block 子系统总览
- `raw/github/notes/block/linux_kernel/block_core.md` — 块设备核心结构
- `raw/github/notes/block/linux_kernel/block_mq.md` — MultiQueue
- `raw/github/notes/block/linux_kernel/block_scheduler.md` — I/O 调度器
- `raw/github/notes/block/linux_kernel/block_request.md` — Request 处理
- `raw/github/notes/block/linux_kernel/block_genhd.md` — GenHD 和分区
- `raw/github/notes/block/linux_kernel/block_deep_dive_r1.md` — 深度分析 R1
- `raw/github/notes/block/linux_kernel/block_deep_dive_r2.md` — 深度分析 R2

## 相关概念

- [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]]
- [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]]
- [[entities/linux/kernel/mm/linux-kernel-mm-swap]]
- [[entities/linux/kernel/mm/linux-kernel-mm-page-reclaim]]
- [[entities/linux/kernel/mm/linux-kernel-mm-mmap]]
- [[entities/linux/kernel/sched/linux-kernel-sched-core]]
- [[entities/linux/kernel/sched/linux-kernel-sched-cfs]]
- [[entities/linux/kernel/sched/linux-kernel-sched-context-switch]]
- [[entities/linux/kernel/sched/linux-kernel-sched-load-balance]]
- [[entities/linux/kernel/block/linux-kernel-block-core]]
- [[entities/linux/kernel/block/linux-kernel-block-mq]]
- [[entities/linux/kernel/block/linux-kernel-block-scheduler]]
