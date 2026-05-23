---
type: source
source-type: pdf
title: "Linux Kernel Books (2 books)"
author: "Daniel P. Bovet, Marco Cesati; Zhao Jiong"
date: 2026-05-23
size: large
path: raw/PDFs/books/深入理解Linuxkenrle.pdf, raw/PDFs/books/linux内核注释.pdf
summary: "2册Linux内核经典：Bovet & Cesati 深入理解Linux内核（2005全面内核架构分析）、赵炯 Linux内核0.12完全注释（2万字逐行注释早期内核源码）"
---

# Linux Kernel Books (2 books)

## Core Content

### 1. Understanding the Linux Kernel (Daniel P. Bovet, Marco Cesati, 944 pages)

The definitive guide to Linux kernel internals (v2.6 era), covering memory management, process scheduling, I/O, filesystems, and networking.

**Process Management:**
- Process descriptor (task_struct), process state machine, process lists
- Process switching: TSS, context_switch(), switch_to() macro
- Scheduling: CFS priors (O(1) scheduler), scheduling classes, SMP load balancing
- System calls: kernel entry/exit (syscall/sysret), parameter passing, synchronous/asynchronous

**Memory Management:**
- Address space: 4-level page tables (PGD/PUD/PMD/PTE), PAE, huge pages
- Process address space: mm_struct, VMA operations, page fault handler
- Physical memory: boot memory allocator, buddy system, SLAB/SLUB allocator
- Page frame reclaim: PFRA, LRU lists, kswapd, swap cache, OOM killer

**I/O System:**
- Block I/O: bio structure, request queue, elevator (I/O scheduler), CFQ/Deadline/Noop
- VFS: dentry/inode/file objects, superblock, page cache, writeback
- Device drivers: character/block/network devices, interrupt handling (top/bottom halves)

**Process Communication & Synchronization:**
- Kernel synchronization: spinlocks, read/write spinlocks, semaphores, RCU
- IPC: System V IPC, POSIX IPC, futex, mutex
- Signals: kernel signal handling, real-time signals

**Networking:**
- Network stack architecture: socket buffer (sk_buff), INET socket layer, TCP/UDP, IP routing
- Network devices: net_device, NAPI, traffic control (TC)

**Virtualization & Power Management:**
- SMP/NUMA architecture support
- Power management: cpuidle, cpufreq, ACPI

### 2. Linux Kernel 0.12 Complete Annotations (Zhao Jiong, 1016 pages)

A comprehensive line-by-line Chinese annotation of the Linux kernel v0.12 source code. Despite using an early version, the book covers the core design philosophy and fundamental mechanisms that persist in modern Linux.

**Background & Setup:**
- Linux kernel history: v0.01 to v0.12, reasons for choosing early version
- 80x86 protected mode: segmentation, paging, privilege levels, gates, TSS, IDT, GDT/LDT
- Assembly and C extensions used in kernel development: GNU as, inline assembly, __attribute__
- Kernel source tree layout: boot/, kernel/, mm/, fs/, net/, ipc/, lib/, include/, tools/

**Boot & Initialization:**
- BIOS → bootsect → setup → head → main() boot chain
- Real mode to protected mode transition
- System initialization: memory detection, interrupt setup, timing, buffer/cache init
- Process 0 (idle) creation and process 1 (init) forking

**Memory Management:**
- Segmentation-based memory management (v0.12 uses 386 segmentation)
- Memory page management: mem_map, get_free_page, free_page
- Memory allocation: malloc (first-fit), kmalloc
- Virtual memory management: do_no_page, do_wp_page

**Process & Scheduling:**
- Task structure (task_struct), NR_TASKS limit (64)
- Process scheduling: schedule(), counter-based time slice, priority
- Process creation: fork(), copy_process, execve()
- System call handler: _sys_call_table, int 0x80 handler

**File System (MINIX fs):**
- MINIX filesystem structure: superblock, inode bitmap, zone bitmap, inodes, data zones
- File operations: open, read, write, seek, close
- Buffer cache: buffer_head, LRU replacement, sync
- Pipe implementation: pipe mechanism, page-based pipe buffers

**Inter-Process Communication:**
- Signal handling: signal bitmap, signal handler dispatch
- System V IPC base (early implementation)
- Pipe-based IPC

**Device Drivers:**
- Character devices: tty, keyboard, console, serial
- Block devices: floppy, hard disk (hd), ramdisk
- Interrupt handler: IRQ registration, bottom halves (BH mechanism)

**Debugging & Experiments:**
- Kernel debugging: printk, BUG(), oops
- Bochs/QEMU emulation for kernel debugging
- Source-level debugging of v0.12 under emulators

## Key Quotes

- "The Linux kernel is a fascinating piece of software — complex yet logical, powerful yet portable" — Bovet & Cesati
- "This early kernel already contains the essence of Linux's working principles. Understanding v0.12 is the fastest path to mastering modern Linux internals." — Zhao Jiong

## Related Pages

- [[kernel-sched-index]] — Scheduler internals
- [[kernel-mm-index]] — Memory management internals
- [[kernel-io-index]] — I/O subsystem
- [[kernel-virt-index]] — KVM/Virtio virtualization
- [[kernel-net-index]] — Network subsystem
- [[kernel-subsystems-index]] — Locking, IPC, RCU, time
- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — Process scheduling
- [[entities/linux/kernel/locking/linux-kernel-locking-core]] — Kernel locking mechanisms
- [[entities/linux/kernel/ipc/linux-kernel-ipc-core]] — IPC subsystem
- [[entities/linux/kernel/block/linux-kernel-block-core]] — Block I/O layer
- [[os-index]] — Operating system fundamentals
- [[sys-prog-index]] — System programming
