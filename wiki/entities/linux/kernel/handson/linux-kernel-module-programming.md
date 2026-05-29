---
type: entity
tags: [linux-kernel, kernel-module, device-driver, character-device, block-device, syscall, interrupt, memory-allocation, sync-primitives, gpio, pci, usb, sysfs, debugfs]
created: 2026-05-29
sources: [handson-lkmpg]
---

# Linux Kernel Module Programming (LKMPG)

## 定义

Linux 内核模块是可动态加载/卸载的代码扩展，运行在内核态（ring 0），扩展内核功能而不需要重启或重新编译。模块编程是 Linux 驱动开发和内核功能扩展的核心技术。

## 核心概念

### 模块结构

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("...");
MODULE_DESCRIPTION("...");

static int __init my_init(void) {
    printk(KERN_INFO "module loaded\n");
    return 0;
}

static void __exit my_exit(void) {
    printk(KERN_INFO "module unloaded\n");
}

module_init(my_init);
module_exit(my_exit);
```

### 字符设备驱动

```c
// 注册
alloc_chrdev_region(&dev, 0, 1, "mydev");
cdev_init(&cdev, &fops);
cdev_add(&cdev, dev, 1);

// file_operations
struct file_operations fops = {
    .owner = THIS_MODULE,
    .read = my_read,
    .write = my_write,
    .unlocked_ioctl = my_ioctl,
    .mmap = my_mmap,
};
```

### 同步原语

| 原语 | 适用场景 |
|------|---------|
| `spin_lock` | 中断上下文，不可睡眠 |
| `mutex` | 进程上下文，长临界区 |
| `rwsem` | 读多写少场景 |
| `rcu` | 读多写少，极低开销 |
| `atomic_t` | 计数器 |
| `completion` | 双向同步 |

### 内存分配

```c
kmalloc(size, GFP_KERNEL);   // slab allocator, ≤PAGE_SIZE
kzalloc(...);                // zeroed
vmalloc(size);               // non-contiguous, larger
alloc_pages(...);            // 物理页
```

### 中断处理

```c
// 顶半部
request_irq(irq_num, handler, IRQF_SHARED, "mydev", dev);

// 底半部机制
tasklet_init(&tasklet, tasklet_handler, data);
INIT_WORK(&work, work_handler);
schedule_work(&work);
```

### 用户-内核数据传递

```c
copy_from_user(dst, src, n);
copy_to_user(dst, src, n);
get_user(val, ptr);    // 单变量
put_user(val, ptr);
```

## NIDS 关联

- **字符设备 + ioctl** → 自定义数据包捕获接口（绕过标准 socket API）
- **sysfs** → IDS 暴露指标（`/sys/class/net/eth0/statistics/`）
- **内存分配** → 高性能数据包缓冲区管理（`kmalloc`/`vmalloc`）
- **DMA** → 零拷贝数据包 I/O（网卡 DMA 直接到内存）
- **中断处理** → 硬件数据包到达的中断驱动通知
- **同步原语** → 多核 NIDS 并行处理时的竞态控制

## 相关概念

- [[entities/linux/kernel/linux-kernel-syscall]] — 系统调用（模块与用户态通信）
- [[entities/linux/kernel/mm/linux-kernel-mm]] — 内核内存管理
- [[entities/linux/kernel/linux-kernel-vfs-core]] — VFS 层（字符设备属于 VFS）
- [[entities/linux/kernel/net]] — 网络子系统
- [[entities/linux/safeos/safeos-nsv]] — SafeOS NSv（用户态网络栈，内核模块通信）
- [[entities/linux/snort3/snort3]] — Snort3 IDS（可加载内核模块用于抓包）

## 来源详情

- [[sources/handson-lkmpg]] — Linux Kernel Module Programming Guide (sysprog21 fork)
