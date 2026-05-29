---
type: source
source-type: web
title: "Linux Kernel Module Programming Guide"
author: "Peter Jay Salzman, Michael Burian, Ori Pomerantz (sysprog21 fork)"
date: 2024
size: large
path: https://sysprog21.github.io/lkmpg/
summary: "Comprehensive hands-on guide to writing Linux kernel modules (loadable kernel objects), covering character drivers, syscalls, interrupts, memory management, and hardware drivers for Linux v5.10+."
tags: [linux-kernel, kernel-module, device-driver, character-device, syscall, interrupt, memory-allocation, sync-primitives, pci, usb, gpio, sysfs, debugfs]
created: 2026-05-29
---

# Linux Kernel Module Programming Guide

## 核心内容

**模块类型与生命周期:**

```c
#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("...");
MODULE_DESCRIPTION("...");

static int __init my_init(void) { return 0; }
static void __exit my_exit(void) { }

module_init(my_init);
module_exit(my_exit);
```

### Part 1 — Getting Started
- Kernel headers: `apt install linux-headers-$(uname -r)`
- Build system: Kbuild (`obj-m`, `KDIR`, `M=` modules)
- `insmod`/`rmmod` — module load/unload
- `modinfo` — module metadata
- Hello World: `printk(KERN_INFO "...")`

### Part 2 — Character Device Drivers
- `struct cdev` + `file_operations`
- `register_chrdev_region()` / `alloc_chrdev_region()`
- `cdev_init()`, `cdev_add()`, `cdev_del()`
- `inode`, `file` structs — per-open vs per-device state
- ioctl: `long (*unlocked_ioctl)(struct file *, unsigned int, unsigned long)`

### Part 3 — /proc, sysfs, debugfs
- `/proc` read/write: `proc_create()`, `proc_remove()`
- sysfs: `struct kobject`, `struct attribute_group`
- debugfs: `debugfs_create_file()`, `debugfs_create_dir()`

### Part 4 — System Calls
- `/proc/sys/kernel/syscall` (not hookable directly in production kernels)
- EBPF approach for syscall tracing
- `SYSCALL_DEFINE*n` macros

### Part 5 — Synchronization
```c
spin_lock_irqsave(&lock, flags);    // spinlock
mutex_lock(&mutex);                  // mutex
down_read(&rwsem->down_read);       // rwsem
atomic_inc(&counter);                // atomic_t
```

### Part 6 — Memory Allocation
```c
kmalloc(size, GFP_KERNEL);           // slab, ≤PAGE_SIZE
vmalloc(size);                       // vmalloc area, non-contiguous
alloc_pages(...);                    // individual pages
kzalloc(...);                        // zeroed kmalloc
```

### Part 7 — User-Kernel Data Transfer
```c
copy_from_user(dst, src, n);
copy_to_user(dst, src, n);
get_user(val, ptr);
put_user(val, ptr);
```

### Part 8 — Hardware Integration
- **GPIO**: `gpio_request()`, `gpio_direction_input()`, `gpio_get_value()`
- **IRQ**: `request_irq()`, `free_irq()`, `tasklet_init()`, `INIT_WORK()`
- **PCI**: `pci_register_driver()`, `pci_enable_device()`
- **USB**: `usb_register()`, `usb_submit_urb()`
- **Block**: `blk_mq_alloc_disk()`, `blk_execute_rq()`
- **Network**: `struct net_device`, `struct packet_type`

## NIDS 关联

- **字符设备 + ioctl** → 自定义数据包捕获接口（如 `/dev/nids`）
- **中断处理** → 硬件数据包到达的中断驱动处理
- **内存分配** → 高性能缓冲区管理（`kmalloc`/`vmalloc`）
- **同步原语** → 多核 NIDS 并行处理时的竞态控制
- **DMA** → 零拷贝数据包 I/O
- **sysfs/proc** → IDS 指标内省（`/proc/net/dev`, `/sys/class/net/`）

## 来源详情

- **原始维护者**: sysprog21 (modern fork for kernel v5.10+)
- **许可证**: Open Software License
- **测试环境**: QEMU (推荐，安全测试内核模块)
- **相关**: [[entities/linux/kernel/linux-kernel-syscall]] — syscall 接口
- **相关**: [[entities/linux/kernel/mm/linux-kernel-mm]] — 内存管理
- **相关**: [[entities/linux/kernel/linux-kernel-vfs-core]] — 字符设备/VFS
