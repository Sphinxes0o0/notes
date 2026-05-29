---
type: source
source-type: web
title: "Operating System in 1000 Lines of C"
author: "os6xx"
date: 2024
size: small
path: https://operating-system-in-1000-lines.vercel.app/zh/
summary: "Ultra-minimal RISC-V OS in ~1000 lines of C covering boot, heap, trap handling, context switching, paging, system calls, disk I/O, and a basic FAT-like filesystem."
tags: [os-dev, risc-v, kernel, c, 1000-lines, context-switch, paging, system-call, virtio, fat, heap-allocator]
created: 2026-05-29
---

# Operating System in 1000 Lines of C

## 核心内容

### Boot (RISC-V)
```c
// kernel start after OpenSBI
void kernel_main(void) {
    uart_puts("Hello OS");
    irq_enable();
    for (;;) wfi();  // wait for interrupt
}
```

### Trap Handling (CSR)
```c
// scause: trap cause, sepc: trap PC, stval: extra info
switch (scause) {
    case 2:  // illegal instruction
        uart_puts("illegal instruction");
        break;
    case 8:  // environment call from U-mode (syscall)
        do_syscall(scause);
        break;
}
```

### Context Switching (最核心代码)
```c
// 保存当前进程寄存器到 trapframe
struct trapframe {
    uint64_t sepc, sstatus, ra, sp, gp, tp, t0-t6, a0-a7;
    uint64_t sscratch;  // 内核栈指针
};

// switchto(pcb1) — 汇编切换栈并返回
void switchto(struct trapframe *from, struct trapframe *to);
```

### Sv39 Paging (RISC-V)
- 39-bit virtual address → 56-bit physical
- 4KB pages: 4-level page table (PG levels 0-3)
- PTE format: V(Valid) D(Dirty) R/W/X permission bits
- `satp` register: root page table physical address

### System Call
```c
// 用户程序触发 ecall (syscall in RISC-V)
#define SYS_WRITE 64
long sys_write(int fd, char *buf, size_t count) {
    if (fd == 1) uart_write(buf, count);  // stdout → UART
}
```

### File System (Simple FAT-like)
```c
struct fat32_fs {
    uint32_t fat_start;
    uint32_t data_start;
    uint32_t sector_size;
    uint32_t cluster_size;
};
```

### VirtIO Disk Driver
- VirtIO device → MMIO registers at fixed addresses
- 3-step handshake: status, feature negotiation, queue setup

## 独特优势

- **极简代码量**：整个 OS 可在 1000 行内读完
- **RISC-V 架构**：干净、文档完整的 ISA
- **完整功能**：boot → process → syscall → FS
- **中文教程**（URL 含 /zh/）

## NIDS 关联

- **上下文切换** → 理解进程间隔离（NIDS 检测进程切换）
- **系统调用** → IDS 检测异常 syscalls（`SYS_openat`, `SYS_execve`）
- **页表** → 虚拟内存隔离（IDS 沙箱利用分页）
- **VirtIO** → 虚拟机数据包 I/O（VirtIO-net 用于 VM 网络）
- **上下文切换** → 监控 `schedule()` 调用可发现提权行为

## 来源详情

- **在线阅读**: operating-system-in-1000-lines.vercel.app/zh/
- **相关**: [[entities/linux/kernel/linux-kernel-syscall]] — Linux syscall 机制
- **相关**: [[entities/linux/kernel/mm/linux-kernel-mm]] — 分页/内存管理
- **相关**: [[entities/linux/kernel/virt/linux-kernel-kvm]] — KVM 虚拟化（VirtIO 相关）
