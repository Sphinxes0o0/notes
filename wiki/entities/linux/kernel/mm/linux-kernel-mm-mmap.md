---
type: entity
tags: [linux-kernel, memory-management, mmap, vma, address-space]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel Memory Mapping (mmap)

## 定义

mmap 是将文件或匿名内存映射到进程虚拟地址空间的系统调用。内核通过 vm_area_struct (VMA) 管理这些映射，VMA 存储在 mm_struct 的 Maple Tree 中。

## 关键要点

- **do_mmap()**: 创建内存映射的核心函数，计算 vm_flags 并调用 mmap_region()
- **vm_area_struct (VMA)**: 描述进程地址空间中的一个连续区间，包含 [vm_start, vm_end)
- **vm_flags**: VMA 标志，如 VM_READ、VM_WRITE、VM_EXEC、VM_SHARED、VM_LOCKED
- **Maple Tree**: 替代红黑树管理 VMA，支持更快的查找和范围查询
- **brk/sbrk**: 调整堆末端，系统调用 munmap 释放映射
- **mlock/munlock**: 锁定映射到内存，防止换出
- **vm_unmapped_area()**: 在地址空间中查找合适的未映射区域

## 内存布局 (64位进程)

```
0xFFFFFFFFFFFFFFFF  Kernel Space
                    ↓
0x00007FFFFFFFFFFF  User Space End
                    ↓
    [Stack]         ← 向下增长
    ↓
    [Memory Mapping Area (mmap)]
    ↓
    [Heap]          ← 向上增长 (brk)
    ↓
    [BSS]
    [Data]
    [Text]
0x0000000000400000
0x0000000000000000  Null Pointer Page
```

## VMA 关键字段

```c
struct vm_area_struct {
    unsigned long vm_start;       // 起始地址
    unsigned long vm_end;         // 结束地址
    struct mm_struct *vm_mm;     // 所属地址空间
    pgprot_t vm_page_prot;       // 访问权限
    vm_flags_t vm_flags;         // VMA 标志
    const struct vm_operations_struct *vm_ops;  // 操作回调
    struct file *vm_file;        // 映射的文件
    unsigned long vm_pgoff;      // 文件内偏移
    // ...
};
```

## 系统调用

| 系统调用 | 功能 |
|---------|------|
| mmap | 创建内存映射 |
| munmap | 释放映射 |
| mremap | 重新映射 |
| brk | 调整堆大小 |
| mlock/munlock | 锁定/解锁内存 |
| mprotect | 修改保护位 |

## 相关概念

- [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]] — mmap 创建的映射通过缺页中断分配物理页
- [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]] — 内核内部也使用 mmap 分配大块内存

## 来源详情

- [[sources/github-sphinxes0o0-notes-kernel]] — mm_mmap.md
## Related Concepts

- [[entities/linux/kernel/ipc/linux-kernel-ipc-core]] — 共享内存是IPC的重要机制
