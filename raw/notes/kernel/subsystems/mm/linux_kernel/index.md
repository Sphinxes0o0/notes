# Linux 内核 MM (Memory Management) 子系统深度分析

## 概述

本文档是 Linux 内核 MM (Memory Management) 子系统的全面深度分析，涵盖从页面分配到回收的完整架构。

## 目录结构

### 核心框架
- [MM 核心数据结构](./mm_core_structs.md)
- [MM 内存分配器](./mm_allocator.md)
- [MM 页面回收机制](./mm_page_reclaim.md)

### 内存管理
- [MM 缺页中断处理](./mm_page_fault.md)
- [MM 内存映射](./mm_mmap.md)
- [MM 交换空间](./mm_swap.md)
- [MM OOM Killer](./mm_oom.md)

## MM 架构

```
用户空间
    |
    v
系统调用 (malloc, mmap, brk, ...)
    |
    v
MM 子系统
    |
    +---> 页面分配 (page_alloc.c)
    |           |
    |           +---> __alloc_pages()
    |           +---> get_page_from_freelist()
    |           +---> SLUB (kmalloc/slub.c)
    |
    +---> 缺页中断 (memory.c)
    |           |
    |           +---> handle_mm_fault()
    |           +---> do_anonymous_page()
    |           +---> do_fault()
    |           +---> do_swap_page()
    |           +---> do_wp_page() (COW)
    |
    +---> 页面回收 (vmscan.c)
    |           |
    |           +---> kswapd (后台)
    |           +---> shrink_lruvec()
    |           +---> folio_check_references()
    |
    +---> Swap (swapfile.c, swap_state.c)
    |           |
    |           +---> swap_in / swap_out
    |           +---> swap cache
    |
    +---> OOM Killer (oom_kill.c)
    |           |
    |           +---> out_of_memory()
    |           +---> oom_badness()
    |
    v
页表 (PTE/PMD/PUD/PGD)
    |
    v
物理内存 (DRAM/PMEM)
```

## 核心概念

### 内存区域 (Zone)
| 区域 | 说明 |
|------|------|
| ZONE_DMA | 适用于 DMA 的低内存 |
| ZONE_DMA32 | 32位 DMA 可访问 |
| ZONE_NORMAL | 直接映射的内核内存 |
| ZONE_HIGHMEM | 高端内存 (32位) |
| ZONE_MOVABLE | 可移动页区域 |

### GFP 标志
| 标志 | 说明 |
|------|------|
| GFP_KERNEL | 内核普通分配，可等待 |
| GFP_ATOMIC | 原子分配，不能等待 |
| GFP_USER | 用户空间分配 |
| GFP_HIGHUSER | 高用户优先级 |

### 页面状态
| 状态 | 说明 |
|------|------|
| PG_locked | 页面被锁定 |
| PG_dirty | 页面有未刷新的修改 |
| PG_active | 页面在 active LRU |
| PG_referenced | 页面被访问过 |
| PG_swapbacked | 页面有 swap 后备 |

## 任务统计

| 类别 | 数量 |
|-----|-----|
| 核心框架 | 3 |
| 内存管理 | 4 |
| **总计** | **7** |

## 来源

本分析基于 Linux 内核 6.8+ 源码。

## 深度分析

- [mm_deep_dive_r1.md](mm_deep_dive_r1.md) - 深度分析 R1: Buddy, Slab, vmalloc, mmap, PageCache
- [mm_deep_dive_r2.md](mm_deep_dive_r2.md) - 深度分析 R2: SLUB Freelist, kfree/slab_free, kmem_cache_alloc, Folio, Compaction, Per-CPU Sheaves
