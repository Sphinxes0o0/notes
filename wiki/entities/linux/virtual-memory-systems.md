---
type: entity
tags: [virtual-memory, operating-system, memory-management, linux]
created: 2026-05-25
sources: [pdf-computer-systems-programmers-perspective, pdf-the-linux-programming-interface, pdf-linux-kernel-books]
---

# Virtual Memory Systems

## 定义

虚拟内存是操作系统为每个进程提供的独立连续地址空间抽象，通过页表将虚拟地址翻译为物理地址，使得程序可以在比物理内存更大的地址空间中运行。

## 关键要点

### 地址翻译

- **虚拟地址 (VA)**：程序使用的逻辑地址，由 VPN（虚拟页号）+ 页内偏移（offset）组成
- **物理地址 (PA)**：CPU 实际访问的物理内存地址，由 PPN（物理页号）+ 页内偏移组成
- **页表 (Page Table)**：存储 VPN → PPN 映射的数组，每个进程有独立页表
- **多级页表**：Linux 使用四级页表（PML4/PGD/PUD/PMD/PTE），节省内存
- **TLB (Translation Lookaside Buffer)**：MMU 内置缓存，加速 VA → PA 翻译

### 页面 Fault 处理

- **Minor fault**：页在内存但不在页表（已被淘汰出 TLB）
- **Major fault**：页不在内存（被swap到磁盘），触发磁盘I/O
- **do_page_fault()**：Linux 内核的页fault处理函数
- **VM_FAULT_***：返回码表示fault类型和后续处理

### 交换空间 (Swap)

- 物理内存的后备存储：当物理页不足时，LRU 页被换出到 swap 分区
- **kswapd**：内核线程，负责页面回收（reclaim）
- **OOM Killer**：内存不足时杀死最占用内存的进程

### Linux 虚拟地址布局

典型用户空间布局（x86-64）：
```
0x0000000000000000 — [未映射]
0x004000000        — text (可执行代码)
0x006000000        — rodata (只读数据)
0x007000000        — data (已初始化全局变量)
0x008000000        — bss (未初始化，全0)
                    — heap (向上增长，brk())
                    — [mmap 匿名映射，向上增长]
                    — [共享库]
0x7fff0000000000   — stack (向下增长)
0x7fffffffffffffff — [未映射，内核空间]
```

### mmap 系统调用

- **匿名映射**：malloc() 底层使用，私有匿名映射用于堆分配
- **文件映射**：将文件直接映射到进程地址空间，read()/write() 无需系统调用
- **私有 vs 共享**：MAP_PRIVATE（COW）/ MAP_SHARED（直接同步到文件）

### 大页 (Huge Pages)

- **HugeTLB**：透明大页（THP）或显式 hugetlbfs
- 减少页表级数，降低 TLB miss 率
- 用于数据库等大内存工作负载

## 相关概念

- [[kernel-mm-index]] — Linux 内存管理子系统索引
- [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]] — SLUB 分配器
- [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]] — 缺页中断处理
- [[entities/linux/kernel/mm/linux-kernel-mm-mmap]] — mmap 虚拟内存区域
- [[os-index]] — 操作系统基础
- [[sys-prog-index]] — 系统编程

## 来源详情

- [[sources/pdf-computer-systems-programmers-perspective]] — CS:APP Ch9 虚拟内存
- [[sources/pdf-the-linux-programming-interface]] — TLPI Ch49-50 mmap/虚拟内存操作
- [[sources/pdf-linux-kernel-books]] — Bovet & Cesati 深入理解 Linux 内核：内存管理章节
