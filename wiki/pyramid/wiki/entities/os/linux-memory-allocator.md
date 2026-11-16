---
type: entity
tags: [linux-kernel, 内存分配器, slub, Buddy, 内核]
created: 2026-05-20
sources: [notes-os]
---

# Linux 内存分配器

## 定义

Linux 内存分配栈由 SLUB/SLAB（对象分配）和 Buddy System（页面分配）组成，SLUB 通过 sheaf 机制和 cmpxchg16b 实现无锁快速路径。

## 关键要点

- **Buddy System**: `__rmqueue()` 从高阶到低阶遍历空闲链表，`__free_one_page()` 递归合并伙伴页面（`buddy_pfn = pfn ^ (1 << order)`）
- **SLUB sheaf 机制**: per-CPU 的对象缓存，`__cmpxchg_double_slab()` 原子更新 freelist + counters（16字节对齐）
- **分配快速路径**: sheaf (main/spare) → cmpxchg → try_fill → swap → barn
- **分配器状态机**: Check Sheaf → Try Refill → Swap Main/Spare → Get from Barn → Allocate New Slab
- **VMSCAN 回收**: LRU 列表管理匿名/文件页面，`folio_batch` 批量回收，`refault_distance` 工作集检测
- **页表管理**: 四级页表遍历（PGD→PUD→PMD→PTE），`handle_pte_fault()` 处理缺页中断
- **TLB shootdown**: 多核间 TLB 同步，通过IPI中断通知其他CPU
- **RCU**: 读多写少场景的同步机制，`synchronize_rcu()` 等待 grace period
- **内存顺序**: x86_64 的 `smp_store_release` / `smp_load_acquire` / `cmpxchg_release`

## 算法复杂度

| 操作 | 复杂度 |
|------|--------|
| Buddy 分配 | O(log MAX_ORDER) |
| Buddy 释放+合并 | O(log MAX_ORDER) |
| SLUB 分配(快速) | O(1) amortized |
| CFS 入队 | O(log n) |

## 相关概念

- [[entities/os/linux-vfs]] — 内存分配器支持 VFS 的 dentry/inode cache
- [[entities/os/linux-scheduler]] — 内存压力触发页面回收与调度器交互
- [[entities/os/os-virtual-memory]] — 页表和虚拟内存是分配器的基础

## 来源详情

- [[sources/notes-os]]
