---
type: source
source-type: web
title: "Kernels 101 — Let's Write a Kernel"
author: "Arjun Sreedharan"
date: 2014
size: small
path: https://arjunsreedharan.org/post/82710718100/kernels-101-lets-write-a-kernel
summary: "Minimal step-by-step tutorial writing a basic x86 kernel with GRUB, NASM assembly, and C — covers boot, protected mode, linker script, and VGA text output."
tags: [os-dev, kernel, boot, grub, multiboot, protected-mode, x86, nasm, assembly]
created: 2026-05-29
---

# Kernels 101 — Let's Write a Kernel

## 核心内容

### Boot Sequence (step-by-step)
1. Power on → CPU reset → jump to 0xFFFFFFF0 (reset vector)
2. BIOS POST → scan boot devices
3. Load GRUB stage 1 (MBR at 0x7C00) → stage 2
4. GRUB loads kernel at 0x100000
5. Jump to kernel entry

### Minimal Kernel
```c
/* kernel.c */
void kernel_main(void) {
    char *vga = (char*)0xb8000;
    vga[0] = 'H';
    vga[1] = 0x0f;  // white on black
    for(;;);  // halt
}
```

```asm
; boot.s — GRUB header + 32-bit protected mode entry
MBALIGN equ 1 << 0
MEMINFO equ 1 << 1
FLAGS   equ MBALIGN | MEMINFO
MAGIC   equ 0x1BADB002
CHECKSUM equ -(MAGIC + FLAGS)

section .multiboot
dd MAGIC, FLAGS, CHECKSUM

section .text
global _start
_start:
    cli
    mov eax, 0x10    ; GDT data segment
    mov ds, eax
    mov es, eax
    mov fs, eax
    mov gs, eax
    mov ebp, 0x90000
    mov esp, ebp
    call kernel_main
```

### Linker Script
```ld
OUTPUT_FORMAT("elf32-i386")
ENTRY(_start)
SECTIONS {
    . = 0x100000;
    .text : { *(.text) }
    .data : { *(.data) }
    .bss  : { *(.bss) }
}
```

## 独特优势

- **极简**：几百行代码理解全部流程
- **最清晰**：boot → kernel 单向流程，无多余复杂度
- **最小依赖**：NASM + GCC + GRUB

## NIDS 关联

- **Boot 理解** → BIOS/UEFI rootkit 检测
- **保护模式** → ring 0 特权级（IDS 内核模块运行在此级别）
- **VGA text** → 早期调试输出（理解内核日志系统）

## 来源详情

- **作者博客**: arjunsreedharan.org
- **相关**: [[entities/os/os-concept]] — 操作系统概念
