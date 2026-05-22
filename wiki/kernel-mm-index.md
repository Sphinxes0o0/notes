---
type: index
tags: [linux-kernel, memory-management]
created: 2026-05-22
---

# Linux Kernel — Memory Management

> SLUB allocator, page fault handling, swap, and virtual memory layout

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]] | SLUB: sheaf/cmpxchg16b, freelist, per-CPU cache | linux-kernel, mm, slab |
| [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]] | Page fault: do_page_fault, handle_mm_fault, anon/file VMA | linux-kernel, mm, paging |
| [[entities/linux/kernel/mm/linux-kernel-mm-swap]] | Swap: swap_cache XA tree, kswapd, Multi-Gen LRU | linux-kernel, mm, swap |
| [[entities/linux/kernel/mm/linux-kernel-mm-page-reclaim]] | Page reclaim: LRU, refault distance, working set | linux-kernel, mm, reclaim |
| [[entities/linux/kernel/mm/linux-kernel-mm-mmap]] | mmap: VMA, Maple Tree, vm_area_struct | linux-kernel, mm, mmap |

## Cross-References

- [[os-index]] — Virtual memory concepts bridge kernel MM and OS-level understanding
- [[kernel-sched-index]] — MM and scheduler interact during context switch and page fault handling
- [[kernel-block-index]] — Page reclaim interacts with block device I/O
