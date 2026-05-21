---
type: entity
tags: [操作系统, 虚拟内存, 页表, MMU]
created: 2026-05-20
sources: [notes-os-fundamentals]
---

# 虚拟内存

## 定义

虚拟内存通过页表将进程的虚拟地址空间映射到物理内存，支持按需分页（page-on-demand）和页面置换（swap），解决内存不足和进程隔离问题。

## 关键要点

- **虚拟地址空间**: 64bit CPU 可寻址 2^64，操作系统限制进程使用几十到几百 EB
- **页/帧分离**: 虚拟内存分页（Page），物理内存分帧（Frame），Page 大小通常等于 Frame 大小（4K）
- **页表结构**: Page → Frame 映射，条目包含 Present/Absent 位、Protection、Reference、Dirty、Caching、Frame Number
- **MMU**: 内存管理单元，CPU 内嵌硬件完成地址转换，缓存 TLB 加速
- **多级页表**: 解决大地址空间页表膨胀问题（4级：PGD→PUD→PMD→PTE）
- **缺页中断**: `handle_pte_fault()` 处理 demand-zero、file-mmap、anonymous、swap-in、COW
- **Swap 机制**: 页面换出到磁盘，`page_in` 时重新加载
- **大页面**: 2MB/1GB 大页（HugePages）减少 TLB miss

## 虚拟地址转换流程

1. 通过虚拟地址计算 Page 编号
2. 查页表（MMU 自动或软件遍历）找到 Frame 编号
3. 物理地址 = Frame 基址 + 页内偏移

## 相关概念

- [[entities/os/linux-memory-allocator]] —Buddy/SLUB 分配物理页面
- [[entities/os/linux-scheduler]] — 页面回收与调度器交互
- [[entities/os/os-process-thread]] — 进程拥有独立虚拟地址空间

## 来源详情

- [[sources/notes-os-fundamentals]]
## Related Concepts

- [[entities/os/linux-vfs]] — 页缓存是VFS与虚拟内存的交汇点
