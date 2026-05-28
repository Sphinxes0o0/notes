# Linux 内核 Virtio 传输层与设备驱动详细分析

## 目录

1. [Virtio 架构概述](#1-virtio-架构概述)
2. [Virtio PCI 传输层](#2-virtio-pci-传输层)
3. [Virtio MMIO 传输层](#3-virtio-mmio-传输层)
4. [Virtio 气球驱动](#4-virtio-气球驱动)
5. [Virtio 内存驱动](#5-virtio-内存驱动)
6. [Virtio 输入设备驱动](#6-virtio-输入设备驱动)
7. [vDPA (vhost Data Path Acceleration)](#7-vdpa-vhost-data-path-acceleration)
8. [架构图](#8-架构图)

---

## 1. Virtio 架构概述

Virtio 是 Linux 内核中用于虚拟化环境的标准化 I/O 虚拟化框架。它采用 frontend/backend 架构，允许客户机操作系统与宿主机之间通过共享内存进行高效通信。

### 1.1 Virtio 核心组件

```
+------------------+     Virtio Ring     +------------------+
|   Guest OS      | <-----------------> |   Host (QEMU)   |
|  Virtio Driver  |                     |  Virtio Backend  |
+------------------+                     +------------------+
```

### 1.2 源码位置

| 组件 | 路径 |
|------|------|
| Virtio PCI 传输 | `/Users/sphinx/github/linux/drivers/virtio/virtio_pci_common.c` |
| Virtio MMIO 传输 | `/Users/sphinx/github/linux/drivers/virtio/virtio_mmio.c` |
| Virtio 气球驱动 | `/Users/sphinx/github/linux/drivers/virtio/virtio_balloon.c` |
| Virtio 内存驱动 | `/Users/sphinx/github/linux/drivers/virtio/virtio_mem.c` |
| Virtio 输入设备 | `/Users/sphinx/github/linux/drivers/virtio/virtio_input.c` |
| Virtio vDPA | `/Users/sphinx/github/linux/drivers/virtio/virtio_vdpa.c` |

---

## 2. Virtio PCI 传输层

**源文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_pci_common.c`

### 2.1 核心数据结构

#### `struct virtio_pci_device` (virtio_pci_common.h:60-112)

```c
struct virtio_pci_device {
    struct virtio_device vdev;         // 通用 virtio 设备结构
    struct pci_dev *pci_dev;           // 底层 PCI 设备

    union {
        struct virtio_pci_legacy_device ldev;  // 传统 Virtio 1.0 设备
        struct virtio_pci_modern_device mdev;  // 现代 Virtio 1.0+ 设备
    };

    bool is_legacy;                    // 标志是否为传统模式

    /* ISR (中断状态寄存器) - 用于读取和清除中断 */
    u8 __iomem *isr;

    /* Virtqueue 列表 - 用于 IRQ 分发 */
    spinlock_t lock;
    struct list_head virtqueues;        // 活跃的 virtqueue 列表
    struct list_head slow_virtqueues;  // 慢速路径 virtqueue 列表

    /* 所有 virtqueue 信息数组 */
    struct virtio_pci_vq_info **vqs;

    /* 管理队列 (Admin VQ) - Virtio 1.0+ */
    struct virtio_pci_admin_vq admin_vq;

    /* MSI-X 中断支持 */
    int msix_enabled;
    int intx_enabled;
    cpumask_var_t *msix_affinity_masks;
    char (*msix_names)[256];
    unsigned int msix_vectors;
    unsigned int msix_used_vectors;
    bool per_vq_vectors;

    /* Virtqueue 设置/删除回调 */
    struct virtqueue *(*setup_vq)(...);
    void (*del_vq)(struct virtio_pci_vq_info *info);
    u16 (*config_vector)(struct virtio_pci_device *vp_dev, u16 vector);
    int (*avq_index)(struct virtio_device *vdev, u16 *index, u16 *num);
};
```

#### `struct virtio_pci_vq_info` (virtio_pci_common.h:34-43)

```c
struct virtio_pci_vq_info {
    struct virtqueue *vq;              // 实际的 virtqueue
    struct list_head node;             // 链表节点
    unsigned int msix_vector;          // MSI-X 向量号
};
```

### 2.2 PCI 设备发现与探测

**virtio_pci_probe()** (行 679-740):

设备探测主要流程:

```c
static int virtio_pci_probe(struct pci_dev *pci_dev,
                            const struct pci_device_id *id)
{
    struct virtio_pci_device *vp_dev, *reg_dev = NULL;
    int rc;

    // 1. 分配 virtio_pci_device 结构
    vp_dev = kzalloc_obj(struct virtio_pci_device);
    if (!vp_dev)
        return -ENOMEM;

    pci_set_drvdata(pci_dev, vp_dev);
    vp_dev->vdev.dev.parent = &pci_dev->dev;
    vp_dev->vdev.dev.release = virtio_pci_release_dev;
    vp_dev->pci_dev = pci_dev;
    INIT_LIST_HEAD(&vp_dev->virtqueues);
    INIT_LIST_HEAD(&vp_dev->slow_virtqueues);
    spin_lock_init(&vp_dev->lock);

    // 2. 使能 PCI 设备
    rc = pci_enable_device(pci_dev);
    if (rc)
        goto err_enable_device;

    // 3. 根据 force_legacy 参数选择现代或传统模式
    if (force_legacy) {
        // 先尝试传统模式
        rc = virtio_pci_legacy_probe(vp_dev);
        // 如果失败，尝试现代模式
        if (rc == -ENODEV || rc == -ENOMEM)
            rc = virtio_pci_modern_probe(vp_dev);
        if (rc)
            goto err_probe;
    } else {
        // 先尝试现代模式
        rc = virtio_pci_modern_probe(vp_dev);
        if (rc == -ENODEV)
            rc = virtio_pci_legacy_probe(vp_dev);
        if (rc)
            goto err_probe;
    }

    pci_set_master(pci_dev);

    // 4. 注册 virtio 设备
    rc = register_virtio_device(&vp_dev->vdev);
    reg_dev = vp_dev;
    if (rc)
        goto err_register;

    return 0;

err_register:
    if (vp_dev->is_legacy)
        virtio_pci_legacy_remove(vp_dev);
    else
        virtio_pci_modern_remove(vp_dev);
err_probe:
    pci_disable_device(pci_dev);
err_enable_device:
    if (reg_dev)
        put_device(&vp_dev->vdev.dev);
    else
        kfree(vp_dev);
    return rc;
}
```

### 2.3 中断处理

**vp_interrupt()** (行 106-124):

```c
static irqreturn_t vp_interrupt(int irq, void *opaque)
{
    struct virtio_pci_device *vp_dev = opaque;
    u8 isr;

    // 读取 ISR 寄存器 (兼有清除中断的作用)
    isr = ioread8(vp_dev->isr);

    /* It's definitely not us if the ISR was not high */
    if (!isr)
        return IRQ_NONE;

    /* Configuration change?  Tell driver if it wants to know. */
    if (isr & VIRTIO_PCI_ISR_CONFIG)
        vp_config_changed(irq, opaque);

    return vp_vring_interrupt(irq, opaque);
}
```

**vp_config_changed()** (行 73-80):

```c
static irqreturn_t vp_config_changed(int irq, void *opaque)
{
    struct virtio_pci_device *vp_dev = opaque;

    virtio_config_changed(&vp_dev->vdev);
    vp_vring_slow_path_interrupt(irq, vp_dev);
    return IRQ_HANDLED;
}
```

**vp_vring_interrupt()** (行 83-98):

```c
static irqreturn_t vp_vring_interrupt(int irq, void *opaque)
{
    struct virtio_pci_device *vp_dev = opaque;
    struct virtio_pci_vq_info *info;
    irqreturn_t ret = IRQ_NONE;
    unsigned long flags;

    spin_lock_irqsave(&vp_dev->lock, flags);
    list_for_each_entry(info, &vp_dev->virtqueues, node) {
        if (vring_interrupt(irq, info->vq) == IRQ_HANDLED)
            ret = IRQ_HANDLED;
    }
    spin_unlock_irqrestore(&vp_dev->lock, flags);

    return ret;
}
```

### 2.4 MSI-X 向量分配

**vp_request_msix_vectors()** (行 126-196):

```c
static int vp_request_msix_vectors(struct virtio_device *vdev, int nvectors,
                                  bool per_vq_vectors, struct irq_affinity *desc)
{
    struct virtio_pci_device *vp_dev = to_vp_device(vdev);
    const char *name = dev_name(&vp_dev->vdev.dev);
    unsigned int flags = PCI_IRQ_MSIX;
    unsigned int i, v;
    int err = -ENOMEM;

    vp_dev->msix_vectors = nvectors;

    // 分配 MSI-X 名称和亲和性掩码数组
    vp_dev->msix_names = kmalloc_objs(*vp_dev->msix_names, nvectors);
    if (!vp_dev->msix_names)
        goto error;

    vp_dev->msix_affinity_masks = kzalloc_objs(*vp_dev->msix_affinity_masks, nvectors);
    if (!vp_dev->msix_affinity_masks)
        goto error;

    for (i = 0; i < nvectors; ++i)
        if (!alloc_cpumask_var(&vp_dev->msix_affinity_masks[i], GFP_KERNEL))
            goto error;

    if (!per_vq_vectors)
        desc = NULL;

    if (desc) {
        flags |= PCI_IRQ_AFFINITY;
        desc->pre_vectors++; /* virtio config vector */
    }

    // 分配 MSI-X 中断向量
    err = pci_alloc_irq_vectors_affinity(vp_dev->pci_dev, nvectors,
                                         nvectors, flags, desc, desc);
    if (err < 0)
        goto error;
    vp_dev->msix_enabled = 1;

    // 设置配置中断向量
    v = vp_dev->msix_used_vectors;
    snprintf(vp_dev->msix_names[v], sizeof *vp_dev->msix_names, "%s-config", name);
    err = request_irq(pci_irq_vector(vp_dev->pci_dev, v),
                      vp_config_changed, 0, vp_dev->msix_names[v], vp_dev);
    if (err)
        goto error;
    ++vp_dev->msix_used_vectors;

    v = vp_dev->config_vector(vp_dev, v);
    if (v == VIRTIO_MSI_NO_VECTOR) {
        err = -EBUSY;
        goto error;
    }

    // 设置共享队列向量
    if (!per_vq_vectors) {
        v = vp_dev->msix_used_vectors;
        snprintf(vp_dev->msix_names[v], sizeof *vp_dev->msix_names, "%s-virtqueues", name);
        err = request_irq(pci_irq_vector(vp_dev->pci_dev, v),
                          vp_vring_interrupt, 0, vp_dev->msix_names[v], vp_dev);
        if (err)
            goto error;
        ++vp_dev->msix_used_vectors;
    }
    return 0;
error:
    return err;
}
```

### 2.5 Virtqueue 配置

**vp_find_vqs()** (行 515-543):

```c
int vp_find_vqs(struct virtio_device *vdev, unsigned int nvqs,
                struct virtqueue *vqs[], struct virtqueue_info vqs_info[],
                struct irq_affinity *desc)
{
    int err;

    // 策略 1: 每个队列一个 MSI-X 向量
    err = vp_find_vqs_msix(vdev, nvqs, vqs, vqs_info,
                           VP_VQ_VECTOR_POLICY_EACH, desc);
    if (!err) return 0;

    // 策略 2: 配置中断专用向量，队列共享一个向量
    err = vp_find_vqs_msix(vdev, nvqs, vqs, vqs_info,
                           VP_VQ_VECTOR_POLICY_SHARED_SLOW, desc);
    if (!err) return 0;

    // 策略 3: 所有中断共享一个向量
    err = vp_find_vqs_msix(vdev, nvqs, vqs, vqs_info,
                           VP_VQ_VECTOR_POLICY_SHARED, desc);
    if (!err) return 0;

    // 策略 4: 回退到 INTX 中断
    if (!(to_vp_device(vdev)->pci_dev->irq))
        return err;
    return vp_find_vqs_intx(vdev, nvqs, vqs, vqs_info);
}
```

**vp_setup_vq()** (行 203-242):

```c
static struct virtqueue *vp_setup_vq(struct virtio_device *vdev, unsigned int index,
                                    void (*callback)(struct virtqueue *vq),
                                    const char *name, bool ctx,
                                    u16 msix_vec,
                                    struct virtio_pci_vq_info **p_info)
{
    struct virtio_pci_device *vp_dev = to_vp_device(vdev);
    struct virtio_pci_vq_info *info = kmalloc_obj(*info);
    struct virtqueue *vq;
    unsigned long flags;

    if (!info)
        return ERR_PTR(-ENOMEM);

    vq = vp_dev->setup_vq(vp_dev, info, index, callback, name, ctx, msix_vec);
    if (IS_ERR(vq))
        goto out_info;

    info->vq = vq;
    if (callback) {
        spin_lock_irqsave(&vp_dev->lock, flags);
        if (!vp_is_slow_path_vector(msix_vec))
            list_add(&info->node, &vp_dev->virtqueues);
        else
            list_add(&info->node, &vp_dev->slow_virtqueues);
        spin_unlock_irqrestore(&vp_dev->lock, flags);
    } else {
        INIT_LIST_HEAD(&info->node);
    }

    *p_info = info;
    return vq;

out_info:
    kfree(info);
    return vq;
}
```

---

## 3. Virtio MMIO 传输层

**源文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_mmio.c`

### 3.1 核心数据结构

#### `struct virtio_mmio_device` (行 84-90)

```c
struct virtio_mmio_device {
    struct virtio_device vdev;         // 通用 virtio 设备结构
    struct platform_device *pdev;       // 平台设备

    void __iomem *base;                // 寄存器基地址
    unsigned long version;              // 设备版本 (1=传统 或 2=现代)
};
```

### 3.2 MMIO 寄存器映射

| 偏移 | 寄存器名 | 说明 |
|------|----------|------|
| 0x00 | VIRTIO_MMIO_MAGIC_VALUE | 魔法值 'virt' (0x74726976) |
| 0x04 | VIRTIO_MMIO_VERSION | 版本号 (1=传统, 2=现代) |
| 0x08 | VIRTIO_MMIO_DEVICE_ID | 设备 ID |
| 0x0C | VIRTIO_MMIO_VENDOR_ID | 厂商 ID |
| 0x20 | VIRTIO_MMIO_DEVICE_FEATURES | 设备特性 |
| 0x24 | VIRTIO_MMIO_DEVICE_FEATURES_SEL | 设备特性选择器 |
| 0x30 | VIRTIO_MMIO_DRIVER_FEATURES | 驱动特性 |
| 0x34 | VIRTIO_MMIO_DRIVER_FEATURES_SEL | 驱动特性选择器 |
| 0x70 | VIRTIO_MMIO_QUEUE_SEL | 队列选择器 |
| 0x80 | VIRTIO_MMIO_QUEUE_NUM_MAX | 最大队列数 |
| 0x84 | VIRTIO_MMIO_QUEUE_NUM | 当前队列数 |
| 0x100 | VIRTIO_MMIO_QUEUE_NOTIFY | 队列通知 |
| 0x110 | VIRTIO_MMIO_STATUS | 设备状态 |
| 0x200+ | VIRTIO_MMIO_CONFIG | 设备特定配置空间 |

### 3.3 MMIO 探测流程

**virtio_mmio_probe()** (行 572-651):

```c
static int virtio_mmio_probe(struct platform_device *pdev)
{
    struct virtio_mmio_device *vm_dev;
    unsigned long magic;
    int rc;

    vm_dev = kzalloc_obj(*vm_dev);
    if (!vm_dev)
        return -ENOMEM;

    vm_dev->vdev.dev.parent = &pdev->dev;
    vm_dev->vdev.dev.release = virtio_mmio_release_dev;
    vm_dev->vdev.config = &virtio_mmio_config_ops;
    vm_dev->pdev = pdev;

    // 1. 映射 MMIO 寄存器空间
    vm_dev->base = devm_platform_ioremap_resource(pdev, 0);
    if (IS_ERR(vm_dev->base)) {
        rc = PTR_ERR(vm_dev->base);
        goto free_vm_dev;
    }

    // 2. 检查魔法值
    magic = readl(vm_dev->base + VIRTIO_MMIO_MAGIC_VALUE);
    if (magic != ('v' | 'i' << 8 | 'r' << 16 | 't' << 24)) {
        dev_warn(&pdev->dev, "Wrong magic value 0x%08lx!\n", magic);
        rc = -ENODEV;
        goto free_vm_dev;
    }

    // 3. 检查版本 (支持 1 和 2)
    vm_dev->version = readl(vm_dev->base + VIRTIO_MMIO_VERSION);
    if (vm_dev->version < 1 || vm_dev->version > 2) {
        dev_err(&pdev->dev, "Version %ld not supported!\n", vm_dev->version);
        rc = -ENXIO;
        goto free_vm_dev;
    }

    // 4. 读取设备 ID
    vm_dev->vdev.id.device = readl(vm_dev->base + VIRTIO_MMIO_DEVICE_ID);
    if (vm_dev->vdev.id.device == 0) {
        // ID 为 0 是无效占位设备
        rc = -ENODEV;
        goto free_vm_dev;
    }
    vm_dev->vdev.id.vendor = readl(vm_dev->base + VIRTIO_MMIO_VENDOR_ID);

    // 5. 设置 DMA 掩码
    if (vm_dev->version == 1) {
        writel(PAGE_SIZE, vm_dev->base + VIRTIO_MMIO_GUEST_PAGE_SIZE);
        rc = dma_set_mask(&pdev->dev, DMA_BIT_MASK(64));
        if (!rc)
            dma_set_coherent_mask(&pdev->dev, DMA_BIT_MASK(32 + PAGE_SHIFT));
    } else {
        rc = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(64));
    }
    if (rc)
        rc = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(32));

    platform_set_drvdata(pdev, vm_dev);

    // 6. 注册 virtio 设备
    rc = register_virtio_device(&vm_dev->vdev);
    if (rc)
        put_device(&vm_dev->vdev.dev);

    return rc;

free_vm_dev:
    kfree(vm_dev);
    return rc;
}
```

### 3.4 中断处理

**vm_interrupt()** (行 285-307):

```c
static irqreturn_t vm_interrupt(int irq, void *opaque)
{
    struct virtio_mmio_device *vm_dev = opaque;
    struct virtqueue *vq;
    unsigned long status;
    irqreturn_t ret = IRQ_NONE;

    // 读取并清除中断状态
    status = readl(vm_dev->base + VIRTIO_MMIO_INTERRUPT_STATUS);
    writel(status, vm_dev->base + VIRTIO_MMIO_INTERRUPT_ACK);

    // 配置改变中断
    if (unlikely(status & VIRTIO_MMIO_INT_CONFIG)) {
        virtio_config_changed(&vm_dev->vdev);
        ret = IRQ_HANDLED;
    }

    // 虚拟队列中断
    if (likely(status & VIRTIO_MMIO_INT_VRING)) {
        virtio_device_for_each_vq(&vm_dev->vdev, vq)
            ret |= vring_interrupt(irq, vq);
    }

    return ret;
}
```

### 3.5 MMIO Virtqueue 设置

**vm_setup_vq()** (行 346-444):

```c
static struct virtqueue *vm_setup_vq(struct virtio_device *vdev, unsigned int index,
                                    void (*callback)(struct virtqueue *vq),
                                    const char *name, bool ctx)
{
    struct virtio_mmio_device *vm_dev = to_virtio_mmio_device(vdev);
    bool (*notify)(struct virtqueue *vq);
    struct virtqueue *vq;
    unsigned int num;
    int err;

    // 选择通知数据方式
    if (__virtio_test_bit(vdev, VIRTIO_F_NOTIFICATION_DATA))
        notify = vm_notify_with_data;
    else
        notify = vm_notify;

    if (!name)
        return NULL;

    // 1. 选择队列
    writel(index, vm_dev->base + VIRTIO_MMIO_QUEUE_SEL);

    // 2. 检查队列是否可用
    if (readl(vm_dev->base + (vm_dev->version == 1 ?
            VIRTIO_MMIO_QUEUE_PFN : VIRTIO_MMIO_QUEUE_READY))) {
        err = -ENOENT;
        goto error_available;
    }

    // 3. 获取队列最大大小
    num = readl(vm_dev->base + VIRTIO_MMIO_QUEUE_NUM_MAX);
    if (num == 0) {
        err = -ENOENT;
        goto error_new_virtqueue;
    }

    // 4. 创建 vring
    vq = vring_create_virtqueue(index, num, VIRTIO_MMIO_VRING_ALIGN, vdev,
                                true, true, ctx, notify, callback, name);
    if (!vq) {
        err = -ENOMEM;
        goto error_new_virtqueue;
    }

    vq->num_max = num;

    // 5. 激活队列
    writel(virtqueue_get_vring_size(vq), vm_dev->base + VIRTIO_MMIO_QUEUE_NUM);

    // 6. 根据版本配置队列地址
    if (vm_dev->version == 1) {
        u64 q_pfn = virtqueue_get_desc_addr(vq) >> PAGE_SHIFT;
        if (q_pfn >> 32) {
            err = -E2BIG;
            goto error_bad_pfn;
        }
        writel(PAGE_SIZE, vm_dev->base + VIRTIO_MMIO_QUEUE_ALIGN);
        writel(q_pfn, vm_dev->base + VIRTIO_MMIO_QUEUE_PFN);
    } else {
        u64 addr;
        addr = virtqueue_get_desc_addr(vq);
        writel((u32)addr, vm_dev->base + VIRTIO_MMIO_QUEUE_DESC_LOW);
        writel((u32)(addr >> 32), vm_dev->base + VIRTIO_MMIO_QUEUE_DESC_HIGH);

        addr = virtqueue_get_avail_addr(vq);
        writel((u32)addr, vm_dev->base + VIRTIO_MMIO_QUEUE_AVAIL_LOW);
        writel((u32)(addr >> 32), vm_dev->base + VIRTIO_MMIO_QUEUE_AVAIL_HIGH);

        addr = virtqueue_get_used_addr(vq);
        writel((u32)addr, vm_dev->base + VIRTIO_MMIO_QUEUE_USED_LOW);
        writel((u32)(addr >> 32), vm_dev->base + VIRTIO_MMIO_QUEUE_USED_HIGH);

        writel(1, vm_dev->base + VIRTIO_MMIO_QUEUE_READY);
    }

    return vq;

error_bad_pfn:
    vring_del_virtqueue(vq);
error_new_virtqueue:
    if (vm_dev->version == 1) {
        writel(0, vm_dev->base + VIRTIO_MMIO_QUEUE_PFN);
    } else {
        writel(0, vm_dev->base + VIRTIO_MMIO_QUEUE_READY);
    }
error_available:
    return ERR_PTR(err);
}
```

---

## 4. Virtio 气球驱动

**源文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_balloon.c`

### 4.1 概述

Virtio 气球驱动允许宿主机通过增减客户机内存来动态管理内存。气球被客户机操作系统视为一个特殊的内存块，可以被"充气"(inflate)来回收内存，或"放气"(deflate)来归还内存。

### 4.2 核心数据结构

#### `struct virtio_balloon` (行 55-127)

```c
struct virtio_balloon {
    struct virtio_device *vdev;

    /* 四个 virtqueue: inflate, deflate, stats, free_page */
    struct virtqueue *inflate_vq, *deflate_vq;
    struct virtqueue *stats_vq, *free_page_vq;

    /* 工作队列 */
    struct workqueue_struct *balloon_wq;
    struct work_struct report_free_page_work;
    struct work_struct update_balloon_stats_work;
    struct work_struct update_balloon_size_work;

    /* 同步锁 */
    spinlock_t stop_update_lock;
    bool stop_update;
    unsigned long config_read_bitmap;

    /* 气球页计数 */
    unsigned int num_pages;

    /* Balloon 设备信息 */
    struct balloon_dev_info vb_dev_info;

    /* 互斥锁 */
    struct mutex balloon_lock;

    /* PFN 数组 - 发送给宿主机 */
    unsigned int num_pfns;
    __virtio32 pfns[VIRTIO_BALLOON_ARRAY_PFNS_MAX];  // 最大 256

    /* 统计信息 */
    struct virtio_balloon_stat stats[VIRTIO_BALLOON_S_NR];

    /* Shrinker 用于内存回收 */
    struct shrinker *shrinker;

    /* OOM 通知器 */
    struct notifier_block oom_nb;

    /* Free page reporting */
    struct virtqueue *reporting_vq;
    struct page_reporting_dev_info pr_dev_info;
};
```

### 4.3 Virtqueue 类型 (行 42-49)

```c
enum virtio_balloon_vq {
    VIRTIO_BALLOON_VQ_INFLATE,      // 充气队列 - 回收内存页
    VIRTIO_BALLOON_VQ_DEFLATE,      // 放气队列 - 归还内存页
    VIRTIO_BALLOON_VQ_STATS,        // 统计队列 - 接收宿主机统计请求
    VIRTIO_BALLOON_VQ_FREE_PAGE,    // 空闲页队列 - 报告空闲页
    VIRTIO_BALLOON_VQ_REPORTING,    // 页面报告队列
    VIRTIO_BALLOON_VQ_MAX
};
```

### 4.4 气球充气 (fill_balloon)

**fill_balloon()** (行 242-288):

```c
static unsigned int fill_balloon(struct virtio_balloon *vb, size_t num)
{
    unsigned int num_allocated_pages;
    struct page *page, *next;
    unsigned int num_pfns;
    LIST_HEAD(pages);

    // 限制为数组大小
    num = min(num, ARRAY_SIZE(vb->pfns));

    // 分配 balloon 页
    for (num_pfns = 0; num_pfns < num;
         num_pfns += VIRTIO_BALLOON_PAGES_PER_PAGE) {
        page = balloon_page_alloc();  // 从 balloon 页池分配
        if (!page) {
            dev_info_ratelimited(&vb->vdev->dev,
                                 "Out of puff! Can't get %u pages\n",
                                 VIRTIO_BALLOON_PAGES_PER_PAGE);
            msleep(200);  // 等待后重试
            break;
        }
        list_add(&page->lru, &pages);
    }

    mutex_lock(&vb->balloon_lock);

    vb->num_pfns = 0;

    // 将页加入 balloon 并设置 PFN
    list_for_each_entry_safe(page, next, &pages, lru) {
        list_del(&page->lru);
        balloon_page_enqueue(&vb->vb_dev_info, page);

        set_page_pfns(vb, vb->pfns + vb->num_pfns, page);
        vb->num_pages += VIRTIO_BALLOON_PAGES_PER_PAGE;
        vb->num_pfns += VIRTIO_BALLOON_PAGES_PER_PAGE;
    }

    num_allocated_pages = vb->num_pfns;

    // 通知宿主机
    if (vb->num_pfns != 0)
        tell_host(vb, vb->inflate_vq);

    mutex_unlock(&vb->balloon_lock);
    return num_allocated_pages;
}
```

### 4.5 气球放气 (leak_balloon)

**leak_balloon()** (行 301-335):

```c
static unsigned int leak_balloon(struct virtio_balloon *vb, size_t num)
{
    unsigned int num_freed_pages;
    struct page *page;
    struct balloon_dev_info *vb_dev_info = &vb->vb_dev_info;
    LIST_HEAD(pages);

    num = min(num, ARRAY_SIZE(vb->pfns));

    mutex_lock(&vb->balloon_lock);

    // 从 balloon 中取出页
    for (vb->num_pfns = 0; vb->num_pfns < num;
         vb->num_pfns += VIRTIO_BALLOON_PAGES_PER_PAGE) {
        page = balloon_page_dequeue(vb_dev_info);
        if (!page)
            break;
        set_page_pfns(vb, vb->pfns + vb->num_pfns, page);
        list_add(&page->lru, &pages);
        vb->num_pages -= VIRTIO_BALLOON_PAGES_PER_PAGE;
    }

    num_freed_pages = vb->num_pfns;

    // 通知宿主机释放这些页
    if (vb->num_pfns != 0)
        tell_host(vb, vb->deflate_vq);

    // 将页返还给系统
    release_pages_balloon(vb, &pages);
    mutex_unlock(&vb->balloon_lock);
    return num_freed_pages;
}
```

### 4.6 宿主机通信 (tell_host)

**tell_host()** (行 183-197):

```c
static void tell_host(struct virtio_balloon *vb, struct virtqueue *vq)
{
    struct scatterlist sg;
    unsigned int len;

    sg_init_one(&sg, vb->pfns, sizeof(vb->pfns[0]) * vb->num_pfns);

    // 添加输出缓冲区并通知宿主机
    virtqueue_add_outbuf(vq, &sg, 1, vb, GFP_KERNEL);
    virtqueue_kick(vq);

    // 等待宿主机确认
    wait_event(vb->acked, virtqueue_get_buf(vq, &len));
}
```

**balloon_ack()** (行 176-181):

```c
static void balloon_ack(struct virtqueue *vq)
{
    struct virtio_balloon *vb = vq->vdev->priv;

    wake_up(&vb->acked);
}
```

### 4.7 设备探测

**virtballoon_probe()** (行 919-1079):

```c
static int virtballoon_probe(struct virtio_device *vdev)
{
    struct virtio_balloon *vb;
    int err;

    if (!vdev->config->get) {
        dev_err(&vdev->dev, "%s failure: config access disabled\n", __func__);
        return -EINVAL;
    }

    vdev->priv = vb = kzalloc_obj(*vb);
    if (!vb)
        return -ENOMEM;

    // 初始化工作队列
    INIT_WORK(&vb->update_balloon_stats_work, update_balloon_stats_func);
    INIT_WORK(&vb->update_balloon_size_work, update_balloon_size_func);
    spin_lock_init(&vb->stop_update_lock);
    mutex_init(&vb->balloon_lock);
    init_waitqueue_head(&vb->acked);
    vb->vdev = vdev;

    balloon_devinfo_init(&vb->vb_dev_info);

    // 初始化虚拟队列
    err = init_vqs(vb);
    if (err)
        goto out_free_vb;

    // 配置 deflate on OOM
    if (!virtio_has_feature(vb->vdev, VIRTIO_BALLOON_F_DEFLATE_ON_OOM))
        vb->vb_dev_info.adjust_managed_page_count = true;

#ifdef CONFIG_BALLOON_MIGRATION
    vb->vb_dev_info.migratepage = virtballoon_migratepage;
#endif

    // 注册内存回收器 (如果支持 FREE_PAGE_HINT)
    if (virtio_has_feature(vdev, VIRTIO_BALLOON_F_FREE_PAGE_HINT)) {
        if (virtqueue_get_vring_size(vb->free_page_vq) < 2) {
            err = -ENOSPC;
            goto out_del_vqs;
        }
        vb->balloon_wq = alloc_workqueue("balloon-wq",
                    WQ_FREEZABLE | WQ_CPU_INTENSIVE | WQ_PERCPU, 0);
        if (!vb->balloon_wq) {
            err = -ENOMEM;
            goto out_del_vqs;
        }
        INIT_WORK(&vb->report_free_page_work, report_free_page_func);
        vb->cmd_id_received_cache = VIRTIO_BALLOON_CMD_ID_STOP;
        vb->cmd_id_active = cpu_to_virtio32(vb->vdev, VIRTIO_BALLOON_CMD_ID_STOP);
        vb->cmd_id_stop = cpu_to_virtio32(vb->vdev, VIRTIO_BALLOON_CMD_ID_STOP);
        spin_lock_init(&vb->free_page_list_lock);
        INIT_LIST_HEAD(&vb->free_page_list);
        err = virtio_balloon_register_shrinker(vb);
        if (err)
            goto out_del_balloon_wq;
    }

    // 注册 OOM 通知器 (如果支持 DEFLATE_ON_OOM)
    if (virtio_has_feature(vb->vdev, VIRTIO_BALLOON_F_DEFLATE_ON_OOM)) {
        vb->oom_nb.notifier_call = virtio_balloon_oom_notify;
        vb->oom_nb.priority = VIRTIO_BALLOON_OOM_NOTIFY_PRIORITY;
        err = register_oom_notifier(&vb->oom_nb);
        if (err < 0)
            goto out_unregister_shrinker;
    }

    // 配置页面报告
    vb->pr_dev_info.report = virtballoon_free_page_report;
    if (virtio_has_feature(vb->vdev, VIRTIO_BALLOON_F_REPORTING)) {
        unsigned int capacity;
        capacity = virtqueue_get_vring_size(vb->reporting_vq);
        if (capacity < PAGE_REPORTING_CAPACITY) {
            err = -ENOSPC;
            goto out_unregister_oom;
        }
        err = page_reporting_register(&vb->pr_dev_info);
        if (err)
            goto out_unregister_oom;
    }

    spin_lock_init(&vb->wakeup_lock);
    device_set_wakeup_capable(&vb->vdev->dev, true);

    virtio_device_ready(vdev);

    if (towards_target(vb))
        virtballoon_changed(vdev);

    return 0;

out_unregister_oom:
    if (virtio_has_feature(vb->vdev, VIRTIO_BALLOON_F_DEFLATE_ON_OOM))
        unregister_oom_notifier(&vb->oom_nb);
out_unregister_shrinker:
    if (virtio_has_feature(vb->vdev, VIRTIO_BALLOON_F_FREE_PAGE_HINT))
        virtio_balloon_unregister_shrinker(vb);
out_del_balloon_wq:
    if (virtio_has_feature(vdev, VIRTIO_BALLOON_F_FREE_PAGE_HINT))
        destroy_workqueue(vb->balloon_wq);
out_del_vqs:
    vdev->config->del_vqs(vdev);
out_free_vb:
    kfree(vb);
    return err;
}
```

---

## 5. Virtio 内存驱动

**源文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_mem.c`

### 5.1 概述

Virtio 内存驱动 (`virtio-mem`) 支持内存热插拔，允许在运行时动态添加或移除内存。支持两种工作模式：

- **子块模式 (SBM)**: Linux 内存块由多个子块组成
- **大块模式 (BBM)**: 大块覆盖多个 Linux 内存块

### 5.2 核心数据结构

#### `struct virtio_mem` (行 102-271)

```c
struct virtio_mem {
    struct virtio_device *vdev;

    /* 是否需要先拔除所有内存 */
    bool unplug_all_required;

    /* 工作队列 - 处理插入/拔除请求 */
    struct work_struct wq;
    atomic_t wq_active;
    atomic_t config_changed;

    /* Virtqueue */
    struct virtqueue *vq;

    /* 等待主机响应 */
    wait_queue_head_t host_resp;

    /* 请求和响应结构 */
    struct virtio_mem_req req;
    struct virtio_mem_resp resp;

    /* 设备配置 */
    uint64_t plugged_size;         // 当前插入大小
    uint64_t requested_size;       // 请求的大小
    uint64_t device_block_size;   // 设备块大小
    int nid;                      // NUMA 节点 ID
    uint64_t addr;                // 物理起始地址
    uint64_t region_size;         // 区域大小
    uint64_t usable_region_size;  // 可用区域大小

    /* 内存组 ID */
    int mgid;

    /* 离线内存阈值 - 防止 OOM */
    atomic64_t offline_size;
    uint64_t offline_threshold;

    /* 操作模式: SBM (子块模式) 或 BBM (大块模式) */
    bool in_sbm;

    union {
        struct {
            /* 子块模式 (SBM) */
            unsigned long first_mb_id;
            unsigned long last_usable_mb_id;
            unsigned long next_mb_id;
            uint64_t sb_size;              // 子块大小
            uint32_t sbs_per_mb;          // 每个内存块的子块数
            unsigned long mb_count[VIRTIO_MEM_SBM_MB_COUNT];
            uint8_t *mb_states;           // 内存块状态数组
            unsigned long *sb_states;      // 子块状态位图
        } sbm;
        struct {
            /* 大块模式 (BBM) */
            unsigned long first_bb_id;
            unsigned long last_usable_bb_id;
            unsigned long next_bb_id;
            unsigned long bb_count[VIRTIO_MEM_BBM_BB_COUNT];
            uint8_t *bb_states;
            uint64_t bb_size;              // 大块大小
        } bbm;
    };

    /* 同步 */
    struct mutex hotplug_mutex;
    bool hotplug_active;

    /* 错误状态 */
    bool broken;

    /* 驱动移除标志 */
    spinlock_t removal_lock;
    bool removing;

    /* 重试定时器 */
    struct hrtimer retry_timer;
    unsigned int retry_timer_ms;

    /* 内存通知器 */
    struct notifier_block memory_notifier;

    /* 休眠通知器 */
    struct notifier_block pm_notifier;
};
```

### 5.3 内存块状态 (SBM 模式) (行 67-85)

```c
enum virtio_mem_sbm_mb_state {
    VIRTIO_MEM_SBM_MB_UNUSED = 0,           // 未使用，可重用
    VIRTIO_MEM_SBM_MB_PLUGGED,               // 已插入，未添加到 Linux
    VIRTIO_MEM_SBM_MB_OFFLINE,               // 已插入，已添加，离线
    VIRTIO_MEM_SBM_MB_OFFLINE_PARTIAL,      // 部分插入，已添加，离线
    VIRTIO_MEM_SBM_MB_KERNEL,               // 已插入，已添加，已在线 (内核区)
    VIRTIO_MEM_SBM_MB_KERNEL_PARTIAL,       // 部分插入，已添加，已在线
    VIRTIO_MEM_SBM_MB_MOVABLE,              // 已插入，已添加，已在线 (可移动区)
    VIRTIO_MEM_SBM_MB_MOVABLE_PARTIAL,      // 部分插入，已添加，已在线
    VIRTIO_MEM_SBM_MB_COUNT
};
```

### 5.4 添加内存

**virtio_mem_add_memory()** (行 636-667):

```c
static int virtio_mem_add_memory(struct virtio_mem *vm, uint64_t addr, uint64_t size)
{
    int rc;

    // 分配资源名称
    if (!vm->resource_name) {
        vm->resource_name = kstrdup_const("System RAM (virtio_mem)", GFP_KERNEL);
        if (!vm->resource_name)
            return -ENOMEM;
    }

    dev_dbg(&vm->vdev->dev, "adding memory: 0x%llx - 0x%llx\n",
            addr, addr + size - 1);

    // 更新离线内存计数
    atomic64_add(size, &vm->offline_size);

    // 调用 Linux 内存热插拔接口
    rc = add_memory_driver_managed(vm->mgid, addr, size, vm->resource_name,
                                  MHP_MERGE_RESOURCE | MHP_NID_IS_MGID);
    if (rc) {
        atomic64_sub(size, &vm->offline_size);
        dev_warn(&vm->vdev->dev, "adding memory failed: %d\n", rc);
    }
    return rc;
}
```

### 5.5 移除内存

**virtio_mem_remove_memory()** (行 700-719):

```c
static int virtio_mem_remove_memory(struct virtio_mem *vm, uint64_t addr, uint64_t size)
{
    int rc;

    dev_dbg(&vm->vdev->dev, "removing memory: 0x%llx - 0x%llx\n",
            addr, addr + size - 1);

    // 调用 Linux 内存热插拔移除接口
    rc = remove_memory(addr, size);
    if (!rc) {
        // 成功，减去离线内存计数
        atomic64_sub(size, &vm->offline_size);
        // 重试挂起的拔除操作
        virtio_mem_retry(vm);
    } else {
        dev_dbg(&vm->vdev->dev, "removing memory failed: %d\n", rc);
    }
    return rc;
}
```

### 5.6 发送请求到宿主机

**virtio_mem_send_request()** (行 1389-1417):

```c
static uint64_t virtio_mem_send_request(struct virtio_mem *vm,
                                        const struct virtio_mem_req *req)
{
    struct scatterlist *sgs[2], sg_req, sg_resp;
    unsigned int len;
    int rc;

    // 复制请求到栈缓冲区
    vm->req = *req;

    // out: buffer for request
    sg_init_one(&sg_req, &vm->req, sizeof(vm->req));
    sgs[0] = &sg_req;

    // in: buffer for response
    sg_init_one(&sg_resp, &vm->resp, sizeof(vm->resp));
    sgs[1] = &sg_resp;

    rc = virtqueue_add_sgs(vm->vq, sgs, 1, 1, vm, GFP_KERNEL);
    if (rc < 0)
        return rc;

    virtqueue_kick(vm->vq);

    // 等待宿主机响应
    wait_event(vm->host_resp, virtqueue_get_buf(vm->vq, &len));

    return virtio16_to_cpu(vm->vdev, vm->resp.type);
}
```

### 5.7 工作队列处理

**virtio_mem_run_wq()** (行 2415-2502):

```c
static void virtio_mem_run_wq(struct work_struct *work)
{
    struct virtio_mem *vm = container_of(work, struct virtio_mem, wq);
    uint64_t diff;
    int rc;

    if (vm->broken)
        return;

    atomic_set(&vm->wq_active, 1);

retry:
    // 首先处理卸载所有内存请求
    if (vm->unplug_all_required)
        rc = virtio_mem_send_unplug_all_request(vm);

    // 处理配置更改
    if (atomic_read(&vm->config_changed)) {
        atomic_set(&vm->config_changed, 0);
        virtio_mem_refresh_config(vm);
    }

    // 清理挂起的操作
    if (!rc)
        rc = virtio_mem_cleanup_pending_mb(vm);

    // 根据请求大小执行插入或移除
    if (!rc && vm->requested_size != vm->plugged_size) {
        if (vm->requested_size > vm->plugged_size) {
            diff = vm->requested_size - vm->plugged_size;
            rc = virtio_mem_plug_request(vm, diff);
        } else {
            diff = vm->plugged_size - vm->requested_size;
            rc = virtio_mem_unplug_request(vm, diff);
        }
    }

    // 根据错误类型处理重试
    switch (rc) {
    case 0:
        vm->retry_timer_ms = VIRTIO_MEM_RETRY_TIMER_MIN_MS;
        break;
    case -ENOSPC:
        // 无法添加更多内存
        break;
    case -ETXTBSY:
    case -EBUSY:
        // 宿主机忙或内存忙，延迟重试
        hrtimer_start(&vm->retry_timer, ms_to_ktime(vm->retry_timer_ms),
                      HRTIMER_MODE_REL);
        break;
    case -EAGAIN:
        // 立即重试
        goto retry;
    default:
        // 未知错误，标记设备损坏
        vm->broken = true;
    }

    atomic_set(&vm->wq_active, 0);
}
```

### 5.8 设备探测

**virtio_mem_probe()** (行 2935-2982):

```c
static int virtio_mem_probe(struct virtio_device *vdev)
{
    struct virtio_mem *vm;
    int rc;

    BUILD_BUG_ON(sizeof(struct virtio_mem_req) != 24);
    BUILD_BUG_ON(sizeof(struct virtio_mem_resp) != 10);

    vdev->priv = vm = kzalloc_obj(*vm);
    if (!vm)
        return -ENOMEM;

    init_waitqueue_head(&vm->host_resp);
    vm->vdev = vdev;
    INIT_WORK(&vm->wq, virtio_mem_run_wq);
    mutex_init(&vm->hotplug_mutex);
    INIT_LIST_HEAD(&vm->next);
    spin_lock_init(&vm->removal_lock);
    hrtimer_setup(&vm->retry_timer, virtio_mem_timer_expired, CLOCK_MONOTONIC,
                  HRTIMER_MODE_REL);
    vm->retry_timer_ms = VIRTIO_MEM_RETRY_TIMER_MIN_MS;
    vm->in_kdump = is_kdump_kernel();

    // 注册虚拟队列
    rc = virtio_mem_init_vq(vm);
    if (rc)
        goto out_free_vm;

    // 初始化设备
    rc = virtio_mem_init(vm);
    if (rc)
        goto out_del_vq;

    // 触发初始配置更新
    if (!vm->in_kdump) {
        atomic_set(&vm->config_changed, 1);
        queue_work(system_freezable_wq, &vm->wq);
    }

    return 0;

out_del_vq:
    vdev->config->del_vqs(vdev);
out_free_vm:
    kfree(vm);
    vdev->priv = NULL;
    return rc;
}
```

---

## 6. Virtio 输入设备驱动

**源文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_input.c`

### 6.1 概述

Virtio 输入设备驱动允许客户机使用宿主机提供的输入设备 (键盘、鼠标、触摸屏等)。

### 6.2 核心数据结构

#### `struct virtio_input` (行 13-25)

```c
struct virtio_input {
    struct virtio_device *vdev;
    struct input_dev *idev;           // Linux input device

    char name[64];
    char serial[64];
    char phys[64];

    /* 两个 virtqueue */
    struct virtqueue *evt;             // 事件队列 (设备->内核)
    struct virtqueue *sts;             // 状态队列 (内核->设备)

    /* 事件缓冲区 */
    struct virtio_input_event evts[64];

    spinlock_t lock;
    bool ready;
};
```

### 6.3 事件处理流程

**virtinput_recv_events()** (行 36-57):

```c
static void virtinput_recv_events(struct virtqueue *vq)
{
    struct virtio_input *vi = vq->vdev->priv;
    struct virtio_input_event *event;
    unsigned long flags;
    unsigned int len;

    spin_lock_irqsave(&vi->lock, flags);
    if (vi->ready) {
        // 从 virtqueue 获取事件
        while ((event = virtqueue_get_buf(vi->evt, &len)) != NULL) {
            spin_unlock_irqrestore(&vi->lock, flags);
            // 报告 input 事件
            input_event(vi->idev,
                        le16_to_cpu(event->type),
                        le16_to_cpu(event->code),
                        le32_to_cpu(event->value));
            spin_lock_irqsave(&vi->lock, flags);
            // 回收缓冲区
            virtinput_queue_evtbuf(vi, event);
        }
        virtqueue_kick(vq);
    }
    spin_unlock_irqrestore(&vi->lock, flags);
}
```

**virtinput_send_status()** (行 63-107):

用于将状态变更 (如 LED) 发送到宿主机:

```c
static int virtinput_send_status(struct virtio_input *vi, u16 type, u16 code, s32 value)
{
    struct virtio_input_event *stsbuf;
    struct scatterlist sg[1];
    unsigned long flags;
    int rc;

    // 跳过 MSC_TIMESTAMP 以避免某些触摸设备的循环问题
    if (vi->idev->mt && type == EV_MSC && code == MSC_TIMESTAMP)
        return 0;

    stsbuf = kzalloc_obj(*stsbuf, GFP_ATOMIC);
    if (!stsbuf)
        return -ENOMEM;

    stsbuf->type  = cpu_to_le16(type);
    stsbuf->code  = cpu_to_le16(code);
    stsbuf->value = cpu_to_le32(value);

    sg_init_one(sg, stsbuf, sizeof(*stsbuf));

    spin_lock_irqsave(&vi->lock, flags);
    if (vi->ready) {
        // 添加输出缓冲区
        rc = virtqueue_add_outbuf(vi->sts, sg, 1, stsbuf, GFP_ATOMIC);
        virtqueue_kick(vi->sts);
    } else {
        rc = -ENODEV;
    }
    spin_unlock_irqrestore(&vi->lock, flags);

    if (rc != 0)
        kfree(stsbuf);
    return rc;
}
```

### 6.4 配置读取

**virtinput_cfg_bits()** (行 141-173):

```c
static void virtinput_cfg_bits(struct virtio_input *vi, int select, int subsel,
                               unsigned long *bits, unsigned int bitcount)
{
    unsigned int bit;
    u8 *virtio_bits;
    u8 bytes;

    bytes = virtinput_cfg_select(vi, select, subsel);
    if (!bytes)
        return;

    if (bitcount > bytes * 8)
        bitcount = bytes * 8;

    virtio_bits = kzalloc(bytes, GFP_KERNEL);
    if (!virtio_bits)
        return;

    // 从配置空间读取位图
    virtio_cread_bytes(vi->vdev, offsetof(struct virtio_input_config, u.bitmap),
                        virtio_bits, bytes);

    for (bit = 0; bit < bitcount; bit++) {
        if (virtio_bits[bit / 8] & (1 << (bit % 8)))
            __set_bit(bit, bits);
    }
    kfree(virtio_bits);

    if (select == VIRTIO_INPUT_CFG_EV_BITS)
        __set_bit(subsel, vi->idev->evbit);
}
```

### 6.5 探测流程

**virtinput_probe()** (行 222-341):

```c
static int virtinput_probe(struct virtio_device *vdev)
{
    struct virtio_input *vi;
    unsigned long flags;
    size_t size;
    int abs, err, nslots;

    if (!virtio_has_feature(vdev, VIRTIO_F_VERSION_1))
        return -ENODEV;

    vi = kzalloc_obj(*vi);
    if (!vi)
        return -ENOMEM;

    vdev->priv = vi;
    vi->vdev = vdev;
    spin_lock_init(&vi->lock);

    // 1. 初始化 virtqueue
    err = virtinput_init_vqs(vi);
    if (err)
        goto err_init_vq;

    // 2. 分配 input device
    vi->idev = input_allocate_device();
    if (!vi->idev) {
        err = -ENOMEM;
        goto err_input_alloc;
    }

    input_set_drvdata(vi->idev, vi);

    // 3. 读取设备信息 (名称、序列号)
    size = virtinput_cfg_select(vi, VIRTIO_INPUT_CFG_ID_NAME, 0);
    virtio_cread_bytes(vi->vdev, offsetof(struct virtio_input_config, u.string),
                       vi->name, min(size, sizeof(vi->name)));

    size = virtinput_cfg_select(vi, VIRTIO_INPUT_CFG_ID_SERIAL, 0);
    virtio_cread_bytes(vi->vdev, offsetof(struct virtio_input_config, u.string),
                       vi->serial, min(size, sizeof(vi->serial)));

    snprintf(vi->phys, sizeof(vi->phys), "virtio%d/input0", vdev->index);
    vi->idev->name = vi->name;
    vi->idev->phys = vi->phys;
    vi->idev->uniq = vi->serial;

    // 4. 读取设备 IDs
    size = virtinput_cfg_select(vi, VIRTIO_INPUT_CFG_ID_DEVIDS, 0);
    if (size >= sizeof(struct virtio_input_devids)) {
        virtio_cread_le(vi->vdev, struct virtio_input_config,
                        u.ids.bustype, &vi->idev->id.bustype);
        // ... 其他 IDs
    } else {
        vi->idev->id.bustype = BUS_VIRTUAL;
    }

    // 5. 读取支持的 event bits
    virtinput_cfg_bits(vi, VIRTIO_INPUT_CFG_PROP_BITS, 0, vi->idev->propbit, INPUT_PROP_CNT);
    size = virtinput_cfg_select(vi, VIRTIO_INPUT_CFG_EV_BITS, EV_REP, ...);
    if (size)
        __set_bit(EV_REP, vi->idev->evbit);

    vi->idev->dev.parent = &vdev->dev;
    vi->idev->event = virtinput_status;

    // 6. 读取按键/绝对坐标等支持位
    virtinput_cfg_bits(vi, VIRTIO_INPUT_CFG_EV_BITS, EV_KEY, vi->idev->keybit, KEY_CNT);
    virtinput_cfg_bits(vi, VIRTIO_INPUT_CFG_EV_BITS, EV_ABS, vi->idev->absbit, ABS_CNT);
    // ... 其他事件类型

    // 7. 读取绝对坐标参数
    if (test_bit(EV_ABS, vi->idev->evbit)) {
        for (abs = 0; abs < ABS_CNT; abs++) {
            if (!test_bit(abs, vi->idev->absbit))
                continue;
            virtinput_cfg_abs(vi, abs);
        }

        // 初始化多点触控槽
        if (test_bit(ABS_MT_SLOT, vi->idev->absbit)) {
            nslots = input_abs_get_max(vi->idev, ABS_MT_SLOT) + 1;
            err = input_mt_init_slots(vi->idev, nslots, 0);
            if (err)
                goto err_mt_init_slots;
        }
    }

    virtio_device_ready(vdev);
    vi->ready = true;

    err = input_register_device(vi->idev);
    if (err)
        goto err_input_register;

    virtinput_fill_evt(vi);
    return 0;

err_input_register:
    spin_lock_irqsave(&vi->lock, flags);
    vi->ready = false;
    spin_unlock_irqrestore(&vi->lock, flags);
err_mt_init_slots:
    input_free_device(vi->idev);
err_input_alloc:
    vdev->config->del_vqs(vdev);
err_init_vq:
    kfree(vi);
    return err;
}
```

---

## 7. vDPA (vhost Data Path Acceleration)

**源文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_vdpa.c`

### 7.1 概述

vDPA (vhost Data Path Acceleration) 允许在用户空间实现 virtio 设备的数据路径，通过内核中的 `vdpa` 总线进行管理。

### 7.2 核心数据结构

#### `struct virtio_vdpa_device` (行 27-31)

```c
struct virtio_vdpa_device {
    struct virtio_device vdev;        // 通用 virtio 设备
    struct vdpa_device *vdpa;         // vDPA 设备
    u64 features;                     // 缓存的特性
};
```

### 7.3 vDPA 操作接口

**virtio_vdpa_config_ops** (行 433-447):

```c
static const struct virtio_config_ops virtio_vdpa_config_ops = {
    .get                 = virtio_vdpa_get,
    .set                 = virtio_vdpa_set,
    .generation          = virtio_vdpa_generation,
    .get_status          = virtio_vdpa_get_status,
    .set_status          = virtio_vdpa_set_status,
    .reset               = virtio_vdpa_reset,
    .find_vqs            = virtio_vdpa_find_vqs,
    .del_vqs             = virtio_vdpa_del_vqs,
    .get_features        = virtio_vdpa_get_features,
    .finalize_features   = virtio_vdpa_finalize_features,
    .bus_name            = virtio_vdpa_bus_name,
    .set_vq_affinity     = virtio_vdpa_set_vq_affinity,
    .get_vq_affinity     = virtio_vdpa_get_vq_affinity,
};
```

### 7.4 Virtqueue 设置

**virtio_vdpa_setup_vq()** (行 130-244):

```c
static struct virtqueue *
virtio_vdpa_setup_vq(struct virtio_device *vdev, unsigned int index,
                     void (*callback)(struct virtqueue *vq),
                     const char *name, bool ctx)
{
    struct vdpa_device *vdpa = vd_get_vdpa(vdev);
    const struct vdpa_config_ops *ops = vdpa->config;
    bool (*notify)(struct virtqueue *vq) = virtio_vdpa_notify;
    struct virtqueue *vq;
    u64 desc_addr, driver_addr, device_addr;
    union virtio_map map = {0};
    struct vdpa_vq_state state = {0};
    u32 align, max_num, min_num = 1;
    bool may_reduce_num = true;
    int err;

    if (!name)
        return NULL;

    if (index >= vdpa->nvqs)
        return ERR_PTR(-ENOENT);

    // 检查 NOTIFICATION_DATA 特性
    if (__virtio_test_bit(vdev, VIRTIO_F_NOTIFICATION_DATA)) {
        if (ops->kick_vq_with_data)
            notify = virtio_vdpa_notify_with_data;
        else
            __virtio_clear_bit(vdev, VIRTIO_F_NOTIFICATION_DATA);
    }

    // 队列不应该已经设置
    if (ops->get_vq_ready(vdpa, index))
        return ERR_PTR(-ENOENT);

    // 获取队列大小
    if (ops->get_vq_size)
        max_num = ops->get_vq_size(vdpa, index);
    else
        max_num = ops->vdpa_vq_num_max(vdpa);

    if (max_num == 0) {
        err = -ENOENT;
        goto error_new_virtqueue;
    }

    if (ops->get_vq_num_min)
        min_num = ops->get_vq_num_min(vdpa);

    may_reduce_num = (max_num != min_num);

    // 获取对齐和内存映射信息
    align = ops->get_vq_align(vdpa);

    if (ops->get_vq_map)
        map = ops->get_vq_map(vdpa, index);
    else
        map = vdpa_get_map(vdpa);

    // 创建 vring
    vq = vring_create_virtqueue_map(index, max_num, align, vdev,
                                    true, may_reduce_num, ctx,
                                    notify, callback, name, map);
    if (!vq) {
        err = -ENOMEM;
        goto error_new_virtqueue;
    }

    if (index == 0)
        vdev->vmap = map;

    vq->num_max = max_num;

    // 设置队列回调
    cb.callback = callback ? virtio_vdpa_virtqueue_cb : NULL;
    cb.private = vq;
    ops->set_vq_cb(vdpa, index, &cb);
    ops->set_vq_num(vdpa, index, virtqueue_get_vring_size(vq));

    // 设置队列地址
    desc_addr = virtqueue_get_desc_addr(vq);
    driver_addr = virtqueue_get_avail_addr(vq);
    device_addr = virtqueue_get_used_addr(vq);

    if (ops->set_vq_address(vdpa, index, desc_addr, driver_addr, device_addr)) {
        err = -EINVAL;
        goto err_vq;
    }

    // 设置队列状态 (如果是 packed vring)
    if (virtio_has_feature(vdev, VIRTIO_F_RING_PACKED)) {
        struct vdpa_vq_state_packed *s = &state.packed;
        s->last_avail_counter = 1;
        s->last_avail_idx = 0;
        s->last_used_counter = 1;
        s->last_used_idx = 0;
    }
    err = ops->set_vq_state(vdpa, index, &state);
    if (err)
        goto err_vq;

    ops->set_vq_ready(vdpa, index, 1);

    return vq;

err_vq:
    vring_del_virtqueue(vq);
error_new_virtqueue:
    ops->set_vq_ready(vdpa, index, 0);
    return ERR_PTR(err);
}
```

### 7.5 探测流程

**virtio_vdpa_probe()** (行 459-496):

```c
static int virtio_vdpa_probe(struct vdpa_device *vdpa)
{
    const struct vdpa_config_ops *ops = vdpa->config;
    struct virtio_vdpa_device *vd_dev, *reg_dev = NULL;
    int ret = -EINVAL;

    vd_dev = kzalloc_obj(*vd_dev);
    if (!vd_dev)
        return -ENOMEM;

    vd_dev->vdev.dev.parent = vdpa->map ? &vdpa->dev : vdpa_get_map(vdpa).dma_dev;
    vd_dev->vdev.dev.release = virtio_vdpa_release_dev;
    vd_dev->vdev.config = &virtio_vdpa_config_ops;
    vd_dev->vdev.map = vdpa->map;
    vd_dev->vdpa = vdpa;

    // 获取设备 ID
    vd_dev->vdev.id.device = ops->get_device_id(vdpa);
    if (vd_dev->vdev.id.device == 0)
        goto err;

    vd_dev->vdev.id.vendor = ops->get_vendor_id(vdpa);

    // 注册 virtio 设备
    ret = register_virtio_device(&vd_dev->vdev);
    reg_dev = vd_dev;
    if (ret)
        goto err;

    // 设置驱动数据
    vdpa_set_drvdata(vdpa, vd_dev);

    return 0;

err:
    if (reg_dev)
        put_device(&vd_dev->vdev.dev);
    else
        kfree(vd_dev);
    return ret;
}
```

---

## 8. 架构图

### 8.1 Virtio 整体架构

```
+----------------------------------------------------------------------+
|                           用户空间应用程序                             |
+----------------------------------------------------------------------+
|                          Virtio 设备驱动                              |
|  +----------+  +----------+  +----------+  +----------+  +----------+ |
|  | virtio-  |  | virtio-  |  | virtio-  |  | virtio-  |  | virtio-  | |
|  | balloon  |  |   net    |  |   blk    |  |  input   |  |   mem    | |
|  +----+-----+  +----+-----+  +----+-----+  +----+-----+  +----+-----+ |
+-------+-------------+-------------+-------------+-------------+--------+
        |             |             |             |             |
  -----v-------------v-------------v-------------v-------------v-----
  |                      Virtio 核心层 (virtio.c)                 |
  |     register_virtio_device() / virtio_device_ready()        |
  |     virtio_find_vqs() / virtio_reset_device()               |
  +---------------------------+----------------------------------+
                              |
  +---------------------------v----------------------------------+
  |                   Virtio 传输层                               |
  |  +---------------------+    +---------------------+          |
  |  | virtio_pci_         |    | virtio_mmio_       |          |
  |  | common.c            |    | .c                 |          |
  |  | (PCIe)              |    | (MMIO)             |          |
  |  +---------------------+    +---------------------+          |
  |  +---------------------+    +---------------------+          |
  |  | virtio_vdpa.c       |    | virtio_scsi.c      |          |
  |  | (vDPA)              |    | (SCSI 传输)        |          |
  |  +---------------------+    +---------------------+          |
  +---------------------------+----------------------------------+
                              |
         +--------------------+--------------------+
         |                    |                    |
  +------v------+      +------v------+      +------v------+
  |   PCI/PCIe  |      |    MMIO     |      |    vDPA    |
  |   总线       |      |   寄存器    |      |   用户空间  |
  +------+------+      +------+------+      +------+------+
         |                    |                    |
  +------v------+      +------v------+      +------v------+
  |   QEMU     |      | ARM/ARM64  |      |  用户空间   |
  |   KVM      |      | 平台设备   |      |  vhost-    |
  |   模拟器   |      |            |      |  user      |
  +------------+      +------------+      +-------------+
```

### 8.2 Virtqueue 中断处理流程

```
+----------------------------------------------------------------+
|                      MSI-X / INTx 中断                         |
+-------------------------------+--------------------------------+
                                |
                         +------v------+
                         | vp_interrupt |
                         | vm_interrupt |
                         +------+------+
                                |
                                +-> ioread8(isr) 读取 ISR
                                |
                                +-> [ISR & VIRTIO_PCI_ISR_CONFIG]
                                |   +-> vp_config_changed()
                                |
                                +-> [ISR & VIRTIO_PCI_ISR_VRING]
                                    +-> vp_vring_interrupt()
                                               |
                                               +-> list_for_each_entry(info, &virtqueues)
                                                       |
                                                       +-> vring_interrupt(irq, info->vq)
                                                                  |
                                                                  +-> virtqueue_interrupt()
                                                                             |
                                                                             +-> vq->callback(vq)
```

### 8.3 Virtio 气球驱动数据流

```
+---------------+     +-------------------+     +----------------+
|  宿主机/QEMU  |     |   客户机 Linux     |     |    物理内存    |
|               |     |                   |     |                |
|   气球设备    |     |   virtio_balloon   |     |    内存页     |
|               |<--->|      驱动          |<--->|                |
+---------------+     +-------------------+     +----------------+
        |                    |                        ^
        |                    |                        |
        |  inflate_vq       |  deflate_vq           |
        |<---- pfns list ---|------------------------+
        |                    |
        |  num_pages 更新    |
        |------------------->|
```

### 8.4 Virtio 内存热插拔架构

```
+----------------------------------------------------------------+
|                      客户机 Linux 内核                          |
+----------------------------------------------------------------+
|  +----------------------------------------------------------+  |
|  |                    virtio_mem 驱动                        |  |
|  |                                                          |  |
|  |   virtio_mem_add_memory()  ----> add_memory_driver_managed()|
|  |          |                                    |            |  |
|  |          |                        +-----------+----------+  |  |
|  |          |                        |                  |    |  |
|  |          |                   memory block       memory block  |  |
|  |          |                        |                  |    |  |
|  |          |                   onlined to          offline  |  |
|  +----------+------------------------+------------------+-----+  |
|             |                        |                  |        |
+-------------+------------------------+------------------+--------+
              |                        |                  |
              |  virtqueue             |  内存块状态      |
              |<-----------------------+------------------+
              |
+-------------+------------------------------------------+
              |                                          |
  +-----------v------------+    +---------------------+  |
  |        QEMU/KVM        |    |    宿主机内存        |  |
  |                        |    |                     |  |
  |    内存区域            |    |   可动态分配/        |  |
  |    (region_size)       |    |   释放的内存         |  |
  |                        |    |                     |  |
  +------------------------+    +---------------------+  |
+-------------------------------------------------------------+
```

### 8.5 vDPA 架构

```
+----------------------------------------------------------------+
|                       用户空间应用程序                           |
+----------------------------------------------------------------+
|  +--------------------+         +--------------------+          |
|  |   vhost-user      |         |   vhost-vdpa      |          |
|  |   守护进程        |         |   守护进程        |          |
|  |   (DPDK, etc.)   |         |                   |          |
|  +---------+---------+         +---------+---------+          |
|            |                               |                    |
|            |         vdpa bus              |                    |
|            +---------------+---------------+                    |
|                            |                                    |
+----------------------------+------------------------------------+
|                            |                                    |
|  +------------------------v--------------------------------+  |
|  |                   virtio_vdpa 驱动                      |  |
|  |                   (virtio_vdpa.c)                       |  |
|  |                                                        |  |
|  |   struct virtio_vdpa_device {                         |  |
|  |       struct virtio_device vdev;                       |  |
|  |       struct vdpa_device *vdpa;                       |  |
|  |   };                                                  |  |
|  |                                                        |  |
|  |   virtio_vdpa_setup_vq()  --->  ops->set_vq_address()|  |
|  |   virtio_vdpa_find_vqs()  --->  ops->set_vq_ready() |  |
|  +---------------------------+----------------------------+  |
+-------------------------------+-------------------------------+
|                               |                               |
|                    +----------v----------+                   |
|                    |    vdpa bus driver  |                   |
|                    |   (vdpa_sim, etc.) |                   |
|                    +---------------------+                   |
+---------------------------------------------------------------+
```

---

## 参考文件

| 文件路径 | 描述 |
|---------|------|
| `/Users/sphinx/github/linux/drivers/virtio/virtio_pci_common.c` | Virtio PCI 传输层实现 |
| `/Users/sphinx/github/linux/drivers/virtio/virtio_pci_common.h` | PCI 传输层头文件 |
| `/Users/sphinx/github/linux/drivers/virtio/virtio_mmio.c` | Virtio MMIO 传输层实现 |
| `/Users/sphinx/github/linux/drivers/virtio/virtio_balloon.c` | 气球驱动实现 |
| `/Users/sphinx/github/linux/drivers/virtio/virtio_mem.c` | 内存热插拔驱动实现 |
| `/Users/sphinx/github/linux/drivers/virtio/virtio_input.c` | 输入设备驱动实现 |
| `/Users/sphinx/github/linux/drivers/virtio/virtio_vdpa.c` | vDPA 传输层实现 |
