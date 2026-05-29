---
type: entity
tags: [linux, kernel, memory-management, mm]
created: 2026-05-29
sources: [handson-lkmpg, handson-os-in-1000-lines]
---

# Linux Kernel Memory Management (MM)

## Definition

Linux kernel memory management (MM) subsystem handles physical and virtual memory allocation, page frame management, memory mapping, swap, and page reclaim — providing the foundation for kernel and user-space memory operations.

## Key Sub-Systems

- [[linux-kernel-mm-page-fault]] — Page fault handling and virtual memory mapping
- [[linux-kernel-mm-mmap]] — Memory mapping and VMA management
- [[linux-kernel-mm-swap]] — Swap space management
- [[linux-kernel-mm-page-reclaim]] — LRU page reclaim (kswapd)
- [[linux-kernel-mm-slab-allocator]] — Slab/SLUB allocator for kernel objects

## Related Concepts

- [[linux-kernel-sched]] — Scheduling (uses MM for stack allocation)
- [[kernel-bypass-dpdk]] — DPDK (alternative to kernel MM for packet buffers)

## Sources
- LKMPG (Linux Kernel Module Programming Guide)
- Operating Systems in 1000 Lines
