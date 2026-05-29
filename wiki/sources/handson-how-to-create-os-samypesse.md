---
type: source
source-type: web
title: "How to Create an Operating System"
author: "Sammy Pesse"
date: 2024
size: medium
path: https://samypesse.gitbook.io/how-to-create-an-operating-system
summary: "A complete online book teaching how to build a UNIX-like OS in C++ from scratch, covering boot process, protected mode, kernel, shell, and extensibility."
tags: [os-dev, kernel, boot, bootloader, grub, multiboot, protected-mode, x86, c++, unix, shell]
created: 2026-05-29
---

# How to Create an Operating System

## 核心内容

### Boot Process (最深度的教程之一)
1. **Reset vector** 0xFFFFFFF0 → BIOS POST
2. **BIOS** selects boot device → loads MBR (512 bytes) at 0x7C00
3. **GRUB** (Multiboot-compliant) loads kernel at 0x100000
4. **Real mode** (16-bit) → **Protected mode** (32-bit) transition
5. **GDT** setup: code segment, data segment, stack

```asm
; boot.s — 16-bit real mode entry
section .text
global _start
_start:
    cli
    mov ax, 0x10    ; data segment selector
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x90000
    jmp $            ; halt
```

### Multiboot Header (GRUB compatibility)
```asm
section .multiboot
align 4
multiboot_header:
    dd 0x1BADB002    ; magic
    dd 0x00000003    ; flags (align + mem info)
    dd -(0x1BADB002 + 0x00000003) ; checksum
```

### Kernel (C++)
```cpp
extern "C" void kernel_main() {
    // VGA text mode: 0xb8000, 80×25, 16 colors
    volatile uint16_t* vga = (uint16_t*)0xb8000;
    vga[0] = (15 << 8) | 'H';  // white 'H'
}
```

### Linker Script (ELF)
```ld
ENTRY(_start)
SECTIONS {
    .text 0x100000 : { *(.text) }
    .data : { *(.data) }
    .bss  : { *(.bss) }
}
```

## 独特优势

- **最详细的 boot 过程**：从 reset vector 到 GRUB 到保护模式
- **多格式**：PDF、Mobi、ePub 可下载
- **UNIX 导向**：目标是可用 shell 而非仅显示文字
- **完整源码 GitHub**: 每个章节独立 commit

## NIDS 关联

- **Boot 过程** → 早期启动阶段威胁检测（rootkit 在 boot 链注入）
- **保护模式** → 理解 ring 0/3 特权级别（恶意内核模块在 ring 0）
- **GRUB 安全** → Secure Boot 链验证（UEFI 安全启动）
- **固件/VGA** → 理解硬件初始化对 IDS 监控范围的影响

## 来源详情

- **GitHub**: `SamyPesse/how-to-create-an-operating-system`
- **相关**: [[entities/linux/kernel/syscall/linux-kernel-syscall]] — syscall 接口
- **相关**: [[entities/os/os-concept]] — 操作系统概念
