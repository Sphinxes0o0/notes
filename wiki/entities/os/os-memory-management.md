---
type: entity
tags: [os, memory-management, virtual-memory, paging, kernel, architecture]
created:2026-06-08
sources: [pdf-cache-memory-architectural-design]
---

# OS Memory Management

## 定义

操作系统内存管理（OS Memory Management）是 OS 内核的核心子系统，负责虚拟地址到物理地址的映射、内存分配与回收、页面置换、内存保护与共享。从单级页表到多级页表、从连续分配到伙伴系统（buddy allocator）、从 FIFO 到 LRU置换算法，是 OS设计的核心基础。

##关键要点

- **虚拟内存**：MMU + 页表提供进程独立地址空间 +内存保护
- **分页机制**：固定大小页（4KB /2MB /1GB hugepage）+ 多级页表（4 级 x86-64）
- **分配策略**：连续分配（first-fit / best-fit / worst-fit）+ 非连续（伙伴系统 + slab）
- **页面置换**：FIFO、LRU、Clock、二次机会、LFU、ARC
- **swap**：内存不足时把不活跃页换出到磁盘

##核心概念

- **page table**：虚拟页 →物理页框映射（CR3 / PGD/PUD/PMD/PTE）
- **TLB**：MMU 内置 cache，缓存最近虚拟→物理翻译
- **buddy allocator**：按2 的幂次合并/拆分空闲页框，减少碎片
- **slab allocator**：内核对象缓存（kmalloc-128 等）
- **LRU variants**：Active/Inactive lists、unmapped pages、working set
- **memory cgroup**：容器内存限额（`memory.limit_in_bytes`）

## 相关页面

- [[entities/cache-memory-design]] — Cache层次结构
- [[entities/memory-hierarchy]] —存储层次
- [[entities/os/os-virtual-memory]] —虚拟内存详解
- [[entities/os/linux-memory-allocator]] — Linux内存分配器
