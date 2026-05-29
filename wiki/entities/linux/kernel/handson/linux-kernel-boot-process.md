---
type: entity
tags: [linux-kernel, boot, bootloader, grub, multiboot, bios, uefi, real-mode, protected-mode, x86, kernel-loader]
created: 2026-05-29
sources: [handson-how-to-create-os-samypesse, handson-kernels-101-arjun, handson-brans-kernel-dev]
---

# Boot Process — x86 Boot Sequence

## 定义

x86 系统从加电到加载内核的完整引导过程，涵盖 BIOS/UEFI、 bootloader（GRUB）、保护模式切换、多核启动等阶段。理解 boot 过程是检测 bootkit/rootkit 的基础。

## 核心阶段

### 1. Reset Vector (0xFFFFFFF0)
```
Power on → CPU reset → jump to 0xFFFFFFF0 (ROM BIOS)
```
- 真实地址由硬件线路决定，不是 PC 寄存器
- 到达 BIOS ROM 入口点

### 2. BIOS POST + Boot Device Selection
- Power-On Self-Test (POST)
- 扫描启动设备（HDD/USB/NET）
- 加载 MBR (512 bytes) 到 0x7C00

### 3. MBR → Bootloader (GRUB)
```
MBR (512 bytes, at 0x7C00)
  → GRUB stage 1 (boot.img)
  → GRUB stage 2 (diskboot.img, core.img)
  → GRUB menu (grub.cfg)
```
- GRUB 识别文件系统（ext4, btrfs, etc）
- 读取 `/boot/grub/` 配置

### 4. Multiboot Specification
GRUB 按 Multiboot 标准加载内核：

```asm
section .multiboot
align 4
multiboot_header:
    dd 0x1BADB002    ; magic
    dd 0x00010003    ; flags (align + mem info)
    dd -(0x1BADB002 + 0x00010003)  ; checksum
```
- 内核镜像必须包含 multiboot header (0x1BADB002)
- GRUB 传递内核参数：boot device, memory map, VBE info

### 5. Real Mode → Protected Mode
```
16-bit real mode (BIOS calls, 0xFFFF0 reset vector)
  ↓  (GDT loaded, CR0.PE = 1)
32-bit protected mode (flat segment model)
  ↓  (long mode enable)
64-bit long mode (x86_64)
```

### 6. 内核加载地址
```
GRUB loads kernel at 0x100000 (1MB) — traditional
Modern: 0x200000 for kernel offset (PHYSICAL_ALIGN)
```

### 7. Kernel Entry Point
```c
// Linux kernel entry (arch/x86/kernel/head_64.S)
_start:
    lgdt gdt_descr
    mov %cr0, %eax
    or $0x1, %eax    // CR0.PE = 1 (protected mode)
    mov %eax, %cr0
    ljmp $0x10,$1f   // jump to 32-bit code segment
```

### Boot Parameters (Linux)
```
boot_params: kernel magic at 0x0000, 0x1BE (boot sector)
struct boot_params {
    char     splitable[0x1f1];
    unsigned short cl;
    unsigned long ebx;
    unsigned long edi;
    unsigned long esi;
    unsigned long eip;
} __attribute__((packed));
```

## Secure Boot
- **UEFI**: UEFI firmware → shim.efi → GRUB → kernel
- **签名验证**: kernel 镜像需要签名（UEFI Secure Boot）
- **MOK**: Machine Owner Key 可导入自定义签名

## NIDS 关联

- **Rootkit 检测**: Boot 过程被 hook 是 APT 常用手段（BIOS rootkit, MBR rootkit, GRUB password）
- **Bootkit**: 寄生在 MBR/GRUB 的恶意代码，先于 IDS 加载
- **UEFI Secure Boot**: 检测未签名驱动/内核模块
- **Boot 参数**: `/proc/cmdline` 可反映启动选项（IDS 可监控异常启动参数）

## 相关概念

- [[entities/os/os-concept]] — 操作系统概念（进程/内存/文件抽象）
- [[entities/linux/kernel/linux-kernel-syscall]] — 系统调用（内核就绪后第一条 syscall）
- [[entities/linux/kernel/virt-kvm]] — KVM 虚拟化（虚拟机 boot 过程）
- [[entities/linux/kernel/mm/linux-kernel-mm]] — 内存管理（boot 后初始化）
- [[entities/linux/safeos/safeos-architecture]] — SafeOS 架构

## 来源详情

- [[sources/handson-how-to-create-os-samypesse]] — Sammy Pesse 完整 OS 教程（最详细的 boot 过程）
- [[sources/handson-kernels-101-arjun]] — Arjun Sreedharan 最小 kernel 教程
- [[sources/handson-brans-kernel-dev]] — Bran 经典 kernel 教程
