---
type: entity
tags: [linux-kernel, memory-management, page-fault, vma]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel Page Fault Handling

## 定义

缺页中断 (Page Fault) 是 CPU 访问虚拟地址时在页表中找不到有效映射或权限不足时触发的异常，由 Linux 内核的 `do_page_fault()` 处理。

## 缺页中断分类

| 类型 | 说明 | 触发条件 |
|------|------|----------|
| Minor Fault | 页表项不存在，但页面已在内存 | 匿名页面未映射、文件缓存未映射 |
| Major Fault | 页面不在内存中 | 需要从磁盘读取（swap in、文件读取） |
| Protection Fault | 权限不足 | 写只读页面、COW 等 |

## 关键要点

- **do_page_fault()**: x86 架构入口，位于 `arch/x86/mm/fault.c`
- **handle_mm_fault()**: 架构无关的内存管理层入口
- **handle_pte_fault()**: PTE 层处理，分发到 do_anonymous_page / do_fault / do_swap_page / do_wp_page
- **vm_area_struct (VMA)**: 描述进程地址空间中的一个区间，包含 vm_flags、vm_ops 等
- **COW (Copy-On-Write)**: 延迟复制技术，多进程共享页面时标记为只读，写时触发复制
- **vm_operations_struct**: 文件系统通过 fault 回调处理文件映射缺页

## 完整流程

```
CPU 执行指令访问虚拟地址
    ↓
MMU 查找页表，页面不存在/权限不足
    ↓
#PF 异常触发 (exc_page_fault)
    ↓
handle_page_fault()
    ↓
地址属于内核空间? ──Yes──> do_kern_addr_fault()
    │No
    ↓
do_user_addr_fault()
    ↓
查找 VMA → handle_mm_fault()
    ↓
__handle_mm_fault() → handle_pte_fault()
    ↓
┌─────────────────────────────────────────┐
│ pmd_none? → do_pte_missing()           │
│   ├─ vma_is_anonymous → do_anonymous_page() │
│   └─ !vma_is_anonymous → do_fault()    │
│ pte_present? → N → do_swap_page()      │
│ FAULT_FLAG_WRITE && !pte_write → do_wp_page() │
└─────────────────────────────────────────┘
```

## 核心数据结构

### vm_fault
```c
struct vm_fault {
    struct vm_area_struct *vma;     // 目标 VMA
    unsigned long address;          // 故障虚拟地址
    unsigned int flags;            // FAULT_FLAG_xxx
    pmd_t *pmd, pud_t *pud;       // 页表项指针
    pte_t orig_pte;                // 故障时刻的 PTE 值
    struct page *page;             // 返回的页面
    // ...
};
```

### vm_operations_struct (文件系统回调)
```c
struct vm_operations_struct {
    vm_fault_t (*fault)(struct vm_fault *vmf);        // 缺页处理
    vm_fault_t (*page_mkwrite)(struct vm_fault *vmf); // 页面即将可写
    // ...
};
```

## 相关概念

- [[entities/linux/kernel/mm/linux-kernel-mm-mmap]] — VMA 管理是缺页中断的基础
- [[entities/linux/kernel/mm/linux-kernel-mm-swap]] — do_swap_page 处理 swap 空间换入
- [[entities/linux/kernel/sched/linux-kernel-sched-context-switch]] — 上下文切换涉及页表切换

## 来源详情

- [[sources/github-sphinxes0o0-notes-kernel]] — mm_page_fault.md
