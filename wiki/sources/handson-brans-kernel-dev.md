---
type: source
source-type: web
title: "Brans Kernel Development Tutorial"
author: "Brandon F."
date: 2014
size: small
path: http://www.osdever.net/tutorials/view/brans-kernel-development-tutorial
summary: "Classic step-by-step bare-metal kernel tutorial covering boot, GDT, IDT, IRQ, paging, heap, VFS, and userland — x86, NASM + C."
tags: [os-dev, kernel, boot, gdt, idt, irq, paging, vfs, heap, userland, x86, nasm]
created: 2026-05-29
---

# Brans Kernel Development Tutorial

## 核心内容

### Topics Covered
1. **Bare Bones** — minimal kernel skeleton
2. **VGA Text Mode** — 0xb8000, color codes
3. **GDT** — Global Descriptor Table (code/data segments, TSS)
4. **IDT** — Interrupt Descriptor Table (exceptions, IRQs)
5. **IRQs** — Programmable Interrupt Controller (PIC) setup
6. **Paging** — 4KB pages, page tables, `cr3` register
7. **Heap** — `malloc`/`free` for kernel
8. **VFS** — Virtual File System layer (file abstraction)
9. **Userland** — user mode processes, syscalls

### GDT Setup
```c
struct gdt_entry {
    uint16_t limit_low;
    uint16_t base_low;
    uint8_t  base_mid;
    uint8_t  access;
    uint8_t  granularity;
    uint8_t  base_high;
} __attribute__((packed));

// GDT pointer for lgdt instruction
struct gdt_ptr {
    uint16_t limit;
    uint32_t base;
} __attribute__((packed));
```

### IDT Entry
```c
struct idt_entry {
    uint16_t base_low;
    uint16_t sel;
    uint8_t  zero;
    uint8_t  flags;
    uint16_t base_high;
} __attribute__((packed));
```

### Paging
```c
// 32-bit paging: 4KB pages
// Page directory (1024 entries) → page table (1024 entries) → 4KB frame
// CR3 → page directory physical address
__asm__ __volatile__ ("mov %0, %%cr3" : : "r"(page_dir));
__asm__ __volatile__ ("mov %%cr0, %%eax; or $0x80000000, %%eax; mov %%eax, %%cr0");
```

### VFS (Unique to this tutorial)
```c
struct file {
    char filename[128];
    uint32_t size;
    void (*open)(void);
    void (*close)(void);
    int (*read)(int fd, void *buf, int n);
    int (*write)(int fd, const void *buf, int n);
};
```

## 独特优势

- **VFS 覆盖**：大多数 minimal kernel 教程忽略文件系统抽象
- **GDT/IDT 完整**：segmentation 和 interrupts 完整设置
- **经典参考资料**：大量 OS dev 社区教程受其影响

## NIDS 关联

- **VFS** → IDS 可能通过 hook VFS 进行文件完整性监控
- **IDT/IRQ** → 硬件中断是数据包到达的底层机制
- **分页** → 理解 VM 隔离是 IDS 沙箱的基础
- **GDT/TSS** → 任务切换监控（`SYSENTER`/`SYSCALL` 相关）

## 来源详情

- **来源**: osdever.net
- **相关**: [[entities/os/os-concept]] — 操作系统概念
- **相关**: [[entities/linux/kernel/vfs/linux-kernel-vfs-core]] — Linux VFS
