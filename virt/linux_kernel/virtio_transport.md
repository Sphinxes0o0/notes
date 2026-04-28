# Linux 内核 Virtio 传输层实现深入分析

## 目录

1. [概述](#1-概述)
2. [Virtio 核心数据结构](#2-virtio-核心数据结构)
3. [Virtio PCI 传输层](#3-virtio-pci-传输层)
4. [Virtio MMIO 传输层](#4-virtio-mmio-传输层)
5. [virtio_config_ops 接口](#5-virtio_config_ops-接口)
6. [设备发现与枚举](#6-设备发现与枚举)
7. [中断和通知机制](#7-中断和通知机制)
8. [架构图](#8-架构图)

---

## 1. 概述

Virtio 是一种通用的虚拟化 I/O 访客-主机通信框架,定义了主机和访客之间交换数据的高级机制。Linux 内核实现了两种主要的 Virtio 传输层:

| 传输层 | 源码位置 | 用途 |
|--------|----------|------|
| PCI 传输 | `drivers/virtio/virtio_pci_common.c` | QEMU/KVM 等虚拟化环境 |
| MMIO 传输 | `drivers/virtio/virtio_mmio.c` | ARM/ARM64 平台设备 |

### 1.1 源码文件清单

```
drivers/virtio/
├── virtio_pci_common.c      # PCI 传输公共代码
├── virtio_pci_common.h       # PCI 传输头文件
├── virtio_pci_modern.c       # Virtio 1.0 Modern PCI 设备支持
├── virtio_pci_modern_dev.c   # Modern PCI 设备操作函数
├── virtio_pci_legacy.c       # Legacy PCI 设备支持
├── virtio_pci_legacy_dev.c   # Legacy PCI 设备操作函数
├── virtio_mmio.c             # MMIO 传输层实现
└── virtio.c                  # 核心 virtio 总线驱动

include/linux/
├── virtio.h                  # Virtio 核心头文件
├── virtio_config.h           # 配置操作接口
├── virtio_pci.h              # PCI 传输头文件
├── virtio_pci_modern.h       # Modern PCI 头文件
├── virtio_pci_legacy.h      # Legacy PCI 头文件

include/uapi/linux/
├── virtio_mmio.h             # MMIO 寄存器定义
└── virtio_pci.h             # PCI 配置结构定义
```

---

## 2. Virtio 核心数据结构

### 2.1 virtio_device 结构体

**位置**: `include/linux/virtio.h:168-189`

```c
struct virtio_device {
    int index;                              // 总线上唯一位置
    bool failed;                            // 失败标志
    bool config_core_enabled;               // 配置更改报告已启用
    bool config_driver_disabled;            // 驱动禁用配置更改报告
    bool config_change_pending;             // 待处理的配置更改
    spinlock_t config_lock;                 // 保护配置更改
    spinlock_t vqs_list_lock;               // 保护 vqs 列表
    struct device dev;                       // 底层设备
    struct virtio_device_id id;              // 设备类型标识
    const struct virtio_config_ops *config;  // 配置操作接口
    const struct vringh_config_ops *vringh_config;
    const struct virtio_map_ops *map;
    struct list_head vqs;                   // 虚拟队列列表
    VIRTIO_DECLARE_FEATURES(features);      // 特性位
    void *priv;                             // 驱动私有数据
    union virtio_map vmap;
};
```

### 2.2 virtqueue 结构体

**位置**: `include/linux/virtio.h:19-44`

```c
struct virtqueue {
    struct list_head list;           // 设备虚拟队列链
    void (*callback)(struct virtqueue *vq);  // 缓冲区消耗回调
    const char *name;                // 队列名称(调试用)
    struct virtio_device *vdev;       // 所属设备
    unsigned int index;               // 队列编号
    unsigned int num_free;            // 可用元素数
    unsigned int num_max;             // 设备支持最大元素数
    bool reset;                       // 队列是否处于复位状态
    void *priv;                      // 传输层私有数据
};
```

### 2.3 virtio_config_ops 接口

**位置**: `include/linux/virtio_config.h:112-140`

```c
struct virtio_config_ops {
    void (*get)(struct virtio_device *vdev, unsigned offset,
                void *buf, unsigned len);           // 读取配置字段
    void (*set)(struct virtio_device *vdev, unsigned offset,
                const void *buf, unsigned len);     // 写入配置字段
    u32 (*generation)(struct virtio_device *vdev);  // 获取配置代际
    u8 (*get_status)(struct virtio_device *vdev);   // 获取设备状态
    void (*set_status)(struct virtio_device *vdev, u8 status); // 设置设备状态
    void (*reset)(struct virtio_device *vdev);      // 重置设备
    int (*find_vqs)(struct virtio_device *vdev, unsigned int nvqs,
                    struct virtqueue *vqs[],
                    struct virtqueue_info vqs_info[],
                    struct irq_affinity *desc);     // 查找虚拟队列
    void (*del_vqs)(struct virtio_device *);        // 删除虚拟队列
    void (*synchronize_cbs)(struct virtio_device *); // 同步回调
    u64 (*get_features)(struct virtio_device *vdev); // 获取设备特性
    void (*get_extended_features)(struct virtio_device *vdev, u64 *features);
    int (*finalize_features)(struct virtio_device *vdev); // 完成特性协商
    const char *(*bus_name)(struct virtio_device *vdev);  // 总线名称
    int (*set_vq_affinity)(struct virtqueue *vq,
                           const struct cpumask *cpu_mask); // 设置队列亲和性
    const struct cpumask *(*get_vq_affinity)(struct virtio_device *vdev,
                                              int index);    // 获取队列亲和性
    bool (*get_shm_region)(struct virtio_device *vdev,
                           struct virtio_shm_region *region, u8 id); // 获取共享内存区
    int (*disable_vq_and_reset)(struct virtqueue *vq);   // 禁用队列并重置
    int (*enable_vq_after_reset)(struct virtqueue *vq);   // 重置后启用队列
};
```

---

## 3. Virtio PCI 传输层

### 3.1 整体架构

PCI 传输层支持两种设备模式:

1. **Legacy 模式**: 兼容 Virtio 0.9 和更早版本,使用 IO 端口访问
2. **Modern 模式**: Virtio 1.0 规范,使用内存映射 I/O 和 PCI capability 结构

### 3.2 核心数据结构

#### virtio_pci_device 结构体

**位置**: `drivers/virtio/virtio_pci_common.h:60-112`

```c
struct virtio_pci_device {
    struct virtio_device vdev;              // 继承 virtio_device
    struct pci_dev *pci_dev;                 // 底层 PCI 设备
    union {
        struct virtio_pci_legacy_device ldev;   // Legacy 设备
        struct virtio_pci_modern_device mdev;   // Modern 设备
    };
    bool is_legacy;                         // 是否为 Legacy 模式

    u8 __iomem *isr;                        // ISR 寄存器地址

    spinlock_t lock;                         // 保护队列列表
    struct list_head virtqueues;             // 快速路径队列
    struct list_head slow_virtqueues;        // 慢速路径队列

    struct virtio_pci_vq_info **vqs;        // 队列信息数组

    struct virtio_pci_admin_vq admin_vq;    // 管理队列(Virtio 1.0)

    /* MSI-X 支持 */
    int msix_enabled;
    int intx_enabled;
    cpumask_var_t *msix_affinity_masks;
    char (*msix_names)[256];
    unsigned int msix_vectors;
    unsigned int msix_used_vectors;
    bool per_vq_vectors;                    // 每队列独立向量

    /* 传输层回调函数 */
    struct virtqueue *(*setup_vq)(...);
    void (*del_vq)(struct virtio_pci_vq_info *info);
    u16 (*config_vector)(struct virtio_pci_device *vp_dev, u16 vector);
    int (*avq_index)(struct virtio_device *vdev, u16 *index, u16 *num);
};
```

#### virtio_pci_modern_device 结构体

**位置**: `include/linux/virtio_pci_modern.h:31-52`

```c
struct virtio_pci_modern_device {
    struct pci_dev *pci_dev;

    struct virtio_pci_common_cfg __iomem *common;  // 公共配置寄存器
    void __iomem *device;                          // 设备特定配置
    void __iomem *notify_base;                     // 通知基址
    resource_size_t notify_pa;                     // 通知物理地址
    u8 __iomem *isr;                              // ISR 寄存器

    size_t notify_len;
    size_t device_len;
    size_t common_len;

    int notify_map_cap;

    u32 notify_offset_multiplier;                 // 通知偏移乘数
    int modern_bars;                              // BAR 掩码
    struct virtio_device_id id;

    int (*device_id_check)(struct pci_dev *pdev);
    u64 dma_mask;
};
```

### 3.3 PCI 配置结构 (Virtio 1.0 Modern)

**位置**: `include/uapi/linux/virtio_pci.h:158-196`

```c
/* Virtio PCI Capability 结构 */
struct virtio_pci_cap {
    __u8 cap_vndr;     // PCI_CAP_ID_VNDR
    __u8 cap_next;     // 下一个 capability 指针
    __u8 cap_len;      // capability 长度
    __u8 cfg_type;     // 配置类型
    __u8 bar;          // BAR 编号
    __u8 id;           // 多个同类 capability 的 ID
    __u8 padding[2];
    __le32 offset;     // 在 BAR 中的偏移
    __le32 length;     // 结构长度
};

/* Capability 类型 */
#define VIRTIO_PCI_CAP_COMMON_CFG        1  // 公共配置
#define VIRTIO_PCI_CAP_NOTIFY_CFG        2  // 通知配置
#define VIRTIO_PCI_CAP_ISR_CFG           3  // ISR 访问
#define VIRTIO_PCI_CAP_DEVICE_CFG        4  // 设备特定配置
#define VIRTIO_PCI_CAP_PCI_CFG           5  // PCI 配置访问
#define VIRTIO_PCI_CAP_SHARED_MEMORY_CFG 8 // 共享内存

/* 公共配置寄存器 */
struct virtio_pci_common_cfg {
    /* 整个设备 */
    __le32 device_feature_select;
    __le32 device_feature;
    __le32 guest_feature_select;
    __le32 guest_feature;
    __le16 msix_config;
    __le16 num_queues;
    __u8 device_status;
    __u8 config_generation;

    /* 特定虚拟队列 */
    __le16 queue_select;
    __le16 queue_size;
    __le16 queue_msix_vector;
    __le16 queue_enable;
    __le16 queue_notify_off;
    __le32 queue_desc_lo;
    __le32 queue_desc_hi;
    __le32 queue_avail_lo;
    __le32 queue_avail_hi;
    __le32 queue_used_lo;
    __le32 queue_used_hi;
};

/* Modern 额外字段 */
struct virtio_pci_modern_common_cfg {
    struct virtio_pci_common_cfg cfg;
    __le16 queue_notify_data;   // 通知数据
    __le16 queue_reset;         // 队列重置
    __le16 admin_queue_index;   // 管理队列索引
    __le16 admin_queue_num;     // 管理队列数量
};
```

### 3.4 vp_find_capability 函数

**位置**: `drivers/virtio/virtio_pci_modern_dev.c:114-143`

```c
static inline int virtio_pci_find_capability(struct pci_dev *dev, u8 cfg_type,
                                            u32 ioresource_types, int *bars)
{
    int pos;

    // 遍历所有 Vendor Capability
    for (pos = pci_find_capability(dev, PCI_CAP_ID_VNDR);
         pos > 0;
         pos = pci_find_next_capability(dev, pos, PCI_CAP_ID_VNDR)) {
        u8 type, bar;
        pci_read_config_byte(dev, pos + offsetof(struct virtio_pci_cap, cfg_type), &type);
        pci_read_config_byte(dev, pos + offsetof(struct virtio_pci_cap, bar), &bar);

        // 忽略保留 BAR 值
        if (bar >= PCI_STD_NUM_BARS)
            continue;

        // 匹配类型且 BAR 有效
        if (type == cfg_type) {
            if (pci_resource_len(dev, bar) &&
                pci_resource_flags(dev, bar) & ioresource_types) {
                *bars |= (1 << bar);
                return pos;  // 返回 capability 位置
            }
        }
    }
    return 0;
}
```

**功能**: 遍历 PCI capability 链表,查找指定类型的 Virtio capability。

### 3.5 PCI 设备探测流程

**位置**: `drivers/virtio/virtio_pci_common.c:679-740`

```c
static int virtio_pci_probe(struct pci_dev *pci_dev,
                           const struct pci_device_id *id)
{
    struct virtio_pci_device *vp_dev;
    int rc;

    // 分配设备结构
    vp_dev = kzalloc_obj(struct virtio_pci_device);
    if (!vp_dev)
        return -ENOMEM;

    pci_set_drvdata(pci_dev, vp_dev);
    vp_dev->vdev.dev.parent = &pci_dev->dev;
    vp_dev->pci_dev = pci_dev;
    INIT_LIST_HEAD(&vp_dev->virtqueues);
    INIT_LIST_HEAD(&vp_dev->slow_virtqueues);
    spin_lock_init(&vp_dev->lock);

    // 启用 PCI 设备
    rc = pci_enable_device(pci_dev);
    if (rc)
        goto err_enable_device;

    // 根据 force_legacy 参数决定探测顺序
    if (force_legacy) {
        // 先尝试 Legacy 模式
        rc = virtio_pci_legacy_probe(vp_dev);
        // 如果失败,尝试 Modern 模式
        if (rc == -ENODEV || rc == -ENOMEM)
            rc = virtio_pci_modern_probe(vp_dev);
    } else {
        // 先尝试 Modern 模式
        rc = virtio_pci_modern_probe(vp_dev);
        if (rc == -ENODEV)
            rc = virtio_pci_legacy_probe(vp_dev);
    }

    pci_set_master(pci_dev);

    // 注册 virtio 设备
    rc = register_virtio_device(&vp_dev->vdev);
    ...
}
```

### 3.6 Modern PCI 探测详解

**位置**: `drivers/virtio/virtio_pci_modern_dev.c:223-369`

```c
int vp_modern_probe(struct virtio_pci_modern_device *mdev)
{
    struct pci_dev *pci_dev = mdev->pci_dev;
    int err, common, isr, notify, device;

    // 确定设备 ID
    if (mdev->device_id_check) {
        devid = mdev->device_id_check(pci_dev);
        mdev->id.device = devid;
    } else {
        // 现代设备: PCI device ID - 0x1040
        mdev->id.device = pci_dev->device - 0x1040;
    }
    mdev->id.vendor = pci_dev->subsystem_vendor;

    // 查找必要的能力结构
    common = virtio_pci_find_capability(pci_dev, VIRTIO_PCI_CAP_COMMON_CFG, ...);
    isr = virtio_pci_find_capability(pci_dev, VIRTIO_PCI_CAP_ISR_CFG, ...);
    notify = virtio_pci_find_capability(pci_dev, VIRTIO_PCI_CAP_NOTIFY_CFG, ...);

    // 映射能力结构
    mdev->common = vp_modern_map_capability(mdev, common, ...);
    mdev->isr = vp_modern_map_capability(mdev, isr, ...);

    // 读取通知偏移乘数
    pci_read_config_dword(pci_dev, notify + offsetof(...notify_off_multiplier),
                          &mdev->notify_offset_multiplier);

    // 映射通知区域
    if (notify_length + notify_offset <= PAGE_SIZE)
        mdev->notify_base = vp_modern_map_capability(mdev, notify, ...);

    // 映射设备特定配置(可选)
    device = virtio_pci_find_capability(pci_dev, VIRTIO_PCI_CAP_DEVICE_CFG, ...);
    if (device)
        mdev->device = vp_modern_map_capability(mdev, device, ...);

    return 0;
}
```

### 3.7 MSI/MSI-X 中断配置

**位置**: `drivers/virtio/virtio_pci_common.c:126-196`

```c
static int vp_request_msix_vectors(struct virtio_device *vdev, int nvectors,
                                  bool per_vq_vectors, struct irq_affinity *desc)
{
    struct virtio_pci_device *vp_dev = to_vp_device(vdev);

    vp_dev->msix_vectors = nvectors;

    // 分配 MSI-X 向量
    err = pci_alloc_irq_vectors_affinity(vp_dev->pci_dev, nvectors,
                                          nvectors, flags, desc);
    if (err < 0)
        goto error;
    vp_dev->msix_enabled = 1;

    // 配置向量
    v = vp_dev->msix_used_vectors;
    snprintf(vp_dev->msix_names[v], ..., "%s-config", name);
    err = request_irq(pci_irq_vector(vp_dev->pci_dev, v),
                      vp_config_changed, 0, vp_dev->msix_names[v], vp_dev);

    // 设置配置向量
    v = vp_dev->config_vector(vp_dev, v);

    // 如果不是每队列独立向量,共享一个中断
    if (!per_vq_vectors) {
        v = vp_dev->msix_used_vectors;
        err = request_irq(pci_irq_vector(vp_dev->pci_dev, v),
                          vp_vring_interrupt, 0, ...);
    }
}
```

### 3.8 中断处理流程

**位置**: `drivers/virtio/virtio_pci_common.c:106-124`

```c
static irqreturn_t vp_interrupt(int irq, void *opaque)
{
    struct virtio_pci_device *vp_dev = opaque;
    u8 isr;

    // 读取 ISR(同时清除中断)
    isr = ioread8(vp_dev->isr);

    if (!isr)
        return IRQ_NONE;

    // 配置更改中断
    if (isr & VIRTIO_PCI_ISR_CONFIG)
        vp_config_changed(irq, opaque);

    // 虚拟队列中断
    return vp_vring_interrupt(irq, opaque);
}
```

---

## 4. Virtio MMIO 传输层

### 4.1 MMIO 寄存器映射

**位置**: `include/uapi/linux/virtio_mmio.h`

| 偏移 | 名称 | 描述 | 访问 |
|------|------|------|------|
| 0x000 | VIRTIO_MMIO_MAGIC_VALUE | 魔数("virt") | RO |
| 0x004 | VIRTIO_MMIO_VERSION | 版本号 | RO |
| 0x008 | VIRTIO_MMIO_DEVICE_ID | 设备 ID | RO |
| 0x00C | VIRTIO_MMIO_VENDOR_ID | 厂商 ID | RO |
| 0x010 | VIRTIO_MMIO_DEVICE_FEATURES | 设备特性 | RO |
| 0x014 | VIRTIO_MMIO_DEVICE_FEATURES_SEL | 特性选择 | WO |
| 0x020 | VIRTIO_MMIO_DRIVER_FEATURES | 驱动特性 | WO |
| 0x024 | VIRTIO_MMIO_DRIVER_FEATURES_SEL | 驱动特性选择 | WO |
| 0x030 | VIRTIO_MMIO_QUEUE_SEL | 队列选择 | WO |
| 0x034 | VIRTIO_MMIO_QUEUE_NUM_MAX | 队列最大数量 | RO |
| 0x038 | VIRTIO_MMIO_QUEUE_NUM | 队列数量 | WO |
| 0x044 | VIRTIO_MMIO_QUEUE_READY | 队列就绪 | RW |
| 0x050 | VIRTIO_MMIO_QUEUE_NOTIFY | 队列通知 | WO |
| 0x060 | VIRTIO_MMIO_INTERRUPT_STATUS | 中断状态 | RO |
| 0x064 | VIRTIO_MMIO_INTERRUPT_ACK | 中断确认 | WO |
| 0x070 | VIRTIO_MMIO_STATUS | 设备状态 | RW |
| 0x080-0x0A4 | QUEUE_DESC/AVAIL/USED | 队列地址 | RW |
| 0x100 | VIRTIO_MMIO_CONFIG | 配置空间 | RW |

### 4.2 virtio_mmio_device 结构体

**位置**: `drivers/virtio/virtio_mmio.c:84-90`

```c
struct virtio_mmio_device {
    struct virtio_device vdev;          // 继承 virtio_device
    struct platform_device *pdev;         // 底层平台设备

    void __iomem *base;                 // MMIO 基址
    unsigned long version;              // 设备版本(1 或 2)
};
```

### 4.3 MMIO 设备探测

**位置**: `drivers/virtio/virtio_mmio.c:572-651`

```c
static int virtio_mmio_probe(struct platform_device *pdev)
{
    struct virtio_mmio_device *vm_dev;
    unsigned long magic;
    int rc;

    // 分配设备结构
    vm_dev = kzalloc_obj(*vm_dev);

    vm_dev->vdev.dev.parent = &pdev->dev;
    vm_dev->vdev.config = &virtio_mmio_config_ops;
    vm_dev->pdev = pdev;

    // 映射 MMIO 区域
    vm_dev->base = devm_platform_ioremap_resource(pdev, 0);

    // 验证魔数
    magic = readl(vm_dev->base + VIRTIO_MMIO_MAGIC_VALUE);
    if (magic != ('v' | 'i' << 8 | 'r' << 16 | 't' << 24)) {
        rc = -ENODEV;
        goto free_vm_dev;
    }

    // 检查版本
    vm_dev->version = readl(vm_dev->base + VIRTIO_MMIO_VERSION);
    if (vm_dev->version < 1 || vm_dev->version > 2) {
        rc = -ENXIO;
        goto free_vm_dev;
    }

    // 读取设备 ID
    vm_dev->vdev.id.device = readl(vm_dev->base + VIRTIO_MMIO_DEVICE_ID);
    if (vm_dev->vdev.id.device == 0) {
        // ID 为 0 是空占位设备
        rc = -ENODEV;
        goto free_vm_dev;
    }
    vm_dev->vdev.id.vendor = readl(vm_dev->base + VIRTIO_MMIO_VENDOR_ID);

    // 设置 DMA 掩码
    if (vm_dev->version == 1)
        dma_set_mask(&pdev->dev, DMA_BIT_MASK(32 + PAGE_SHIFT));
    else
        dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(64));

    // 注册设备
    rc = register_virtio_device(&vm_dev->vdev);
}
```

### 4.4 MMIO 中断处理

**位置**: `drivers/virtio/virtio_mmio.c:285-307`

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

    // 配置更改中断
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

### 4.5 MMIO 虚拟队列设置

**位置**: `drivers/virtio/virtio_mmio.c:346-443`

```c
static struct virtqueue *vm_setup_vq(struct virtio_device *vdev, unsigned int index,
                                    void (*callback)(struct virtqueue *vq),
                                    const char *name, bool ctx)
{
    struct virtio_mmio_device *vm_dev = to_virtio_mmio_device(vdev);
    struct virtqueue *vq;
    unsigned int num;

    // 选择队列
    writel(index, vm_dev->base + VIRTIO_MMIO_QUEUE_SEL);

    // 检查队列是否可用
    if (readl(vm_dev->base + VIRTIO_MMIO_QUEUE_READY)) {
        err = -ENOENT;
        goto error_available;
    }

    // 获取最大队列大小
    num = readl(vm_dev->base + VIRTIO_MMIO_QUEUE_NUM_MAX);
    if (num == 0) {
        err = -ENOENT;
        goto error_new_virtqueue;
    }

    // 创建 vring
    vq = vring_create_virtqueue(index, num, VIRTIO_MMIO_VRING_ALIGN, vdev,
                                 true, true, ctx, notify, callback, name);

    // 设置队列大小
    writel(virtqueue_get_vring_size(vq), vm_dev->base + VIRTIO_MMIO_QUEUE_NUM);

    if (vm_dev->version == 1) {
        // Legacy: 使用 PFN
        u64 q_pfn = virtqueue_get_desc_addr(vq) >> PAGE_SHIFT;
        writel(PAGE_SIZE, vm_dev->base + VIRTIO_MMIO_QUEUE_ALIGN);
        writel(q_pfn, vm_dev->base + VIRTIO_MMIO_QUEUE_PFN);
    } else {
        // Modern: 使用分离的地址
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
}
```

---

## 5. virtio_config_ops 接口

### 5.1 配置操作接口实现

#### PCI Modern 配置操作

**位置**: `drivers/virtio/virtio_pci_modern.c:1227-1265`

```c
static const struct virtio_config_ops virtio_pci_config_ops = {
    .get            = vp_get,           // 读取配置
    .set            = vp_set,           // 写入配置
    .generation     = vp_generation,    // 获取代际
    .get_status     = vp_get_status,    // 获取状态
    .set_status     = vp_set_status,    // 设置状态
    .reset          = vp_reset,         // 重置设备
    .find_vqs       = vp_modern_find_vqs,   // 查找队列
    .del_vqs        = vp_del_vqs,       // 删除队列
    .synchronize_cbs = vp_synchronize_vectors,
    .get_extended_features = vp_get_features,
    .finalize_features = vp_finalize_features,
    .bus_name       = vp_bus_name,
    .set_vq_affinity = vp_set_vq_affinity,
    .get_vq_affinity = vp_get_vq_affinity,
    .get_shm_region  = vp_get_shm_region,
    .disable_vq_and_reset = vp_modern_disable_vq_and_reset,
    .enable_vq_after_reset = vp_modern_enable_vq_after_reset,
};
```

#### MMIO 配置操作

**位置**: `drivers/virtio/virtio_mmio.c:522-536`

```c
static const struct virtio_config_ops virtio_mmio_config_ops = {
    .get            = vm_get,
    .set            = vm_set,
    .generation     = vm_generation,
    .get_status     = vm_get_status,
    .set_status     = vm_set_status,
    .reset          = vm_reset,
    .find_vqs       = vm_find_vqs,
    .del_vqs        = vm_del_vqs,
    .get_features   = vm_get_features,
    .finalize_features = vm_finalize_features,
    .bus_name       = vm_bus_name,
    .get_shm_region = vm_get_shm_region,
    .synchronize_cbs = vm_synchronize_cbs,
};
```

### 5.2 get() 实现示例

**位置**: `drivers/virtio/virtio_pci_modern.c:446-480`

```c
static void vp_get(struct virtio_device *vdev, unsigned int offset,
                   void *buf, unsigned int len)
{
    struct virtio_pci_device *vp_dev = to_vp_device(vdev);
    struct virtio_pci_modern_device *mdev = &vp_dev->mdev;
    void __iomem *device = mdev->device;
    u8 b;
    __le16 w;
    __le32 l;

    BUG_ON(offset + len > mdev->device_len);

    switch (len) {
    case 1:
        b = ioread8(device + offset);
        memcpy(buf, &b, sizeof b);
        break;
    case 2:
        w = cpu_to_le16(ioread16(device + offset));
        memcpy(buf, &w, sizeof w);
        break;
    case 4:
        l = cpu_to_le32(ioread32(device + offset));
        memcpy(buf, &l, sizeof l);
        break;
    case 8:
        l = cpu_to_le32(ioread32(device + offset));
        memcpy(buf, &l, sizeof l);
        l = cpu_to_le32(ioread32(device + offset + sizeof l));
        memcpy(buf + sizeof l, &l, sizeof l);
        break;
    default:
        BUG();
    }
}
```

### 5.3 find_vqs() 实现

**位置**: `drivers/virtio/virtio_pci_common.c:514-543`

```c
int vp_find_vqs(struct virtio_device *vdev, unsigned int nvqs,
                struct virtqueue *vqs[], struct virtqueue_info vqs_info[],
                struct irq_affinity *desc)
{
    int err;

    // 尝试方案 1: MSI-X,每队列独立向量
    err = vp_find_vqs_msix(vdev, nvqs, vqs, vqs_info,
                           VP_VQ_VECTOR_POLICY_EACH, desc);
    if (!err)
        return 0;

    // 方案 2: MSI-X,共享慢速路径向量
    err = vp_find_vqs_msix(vdev, nvqs, vqs, vqs_info,
                           VP_VQ_VECTOR_POLICY_SHARED_SLOW, desc);
    if (!err)
        return 0;

    // 方案 3: MSI-X,全部共享
    err = vp_find_vqs_msix(vdev, nvqs, vqs, vqs_info,
                           VP_VQ_VECTOR_POLICY_SHARED, desc);
    if (!err)
        return 0;

    // 方案 4: 传统 INTX 中断
    return vp_find_vqs_intx(vdev, nvqs, vqs, vqs_info);
}
```

---

## 6. 设备发现与枚举

### 6.1 Virtio 总线注册

**位置**: `drivers/virtio/virtio.c:709-727`

```c
static int virtio_init(void)
{
    // 注册 virtio 总线
    if (bus_register(&virtio_bus) != 0)
        panic("virtio bus registration failed");

    virtio_debug_init();
    return 0;
}
core_initcall(virtio_init);
```

**virtio_bus 定义** (`drivers/virtio/virtio.c:438-447`):

```c
static const struct bus_type virtio_bus = {
    .name       = "virtio",
    .match      = virtio_dev_match,    // 设备-驱动匹配
    .dev_groups = virtio_dev_groups,
    .uevent     = virtio_uevent,
    .probe      = virtio_dev_probe,    // 设备探测
    .remove     = virtio_dev_remove,   // 设备移除
    .irq_get_affinity = virtio_irq_get_affinity,
    .shutdown   = virtio_dev_shutdown,
};
```

### 6.2 Virtio 设备注册

**位置**: `drivers/virtio/virtio.c:517-572`

```c
int register_virtio_device(struct virtio_device *dev)
{
    int err;

    dev->dev.bus = &virtio_bus;
    device_initialize(&dev->dev);

    // 分配唯一设备索引
    err = ida_alloc(&virtio_index_ida, GFP_KERNEL);
    dev->index = err;
    dev_set_name(&dev->dev, "virtio%u", dev->index);

    // 初始化锁和列表
    spin_lock_init(&dev->config_lock);
    dev->config_driver_disabled = false;
    dev->config_core_enabled = false;
    dev->config_change_pending = false;
    INIT_LIST_HEAD(&dev->vqs);
    spin_lock_init(&dev->vqs_list_lock);

    // 重置设备
    virtio_reset_device(dev);

    // 确认设备存在
    virtio_add_status(dev, VIRTIO_CONFIG_S_ACKNOWLEDGE);

    // 添加设备到总线
    err = device_add(&dev->dev);
    return err;
}
```

### 6.3 PCI 设备枚举

**位置**: `drivers/virtio/virtio_pci_common.c:661-664`

```c
static const struct pci_device_id virtio_pci_id_table[] = {
    { PCI_DEVICE(PCI_VENDOR_ID_REDHAT_QUMRANET, PCI_ANY_ID) },
    { 0 }
};

MODULE_DEVICE_TABLE(pci, virtio_pci_id_table);
```

**探测流程**:

1. PCI 子系统调用 `virtio_pci_probe()`
2. 分配 `virtio_pci_device` 结构
3. 启用 PCI 设备
4. 尝试 Modern 模式探测 (`virtio_pci_modern_probe`)
5. 如果失败,尝试 Legacy 模式探测 (`virtio_pci_legacy_probe`)
6. 调用 `register_virtio_device()` 注册设备

### 6.4 平台设备枚举 (Device Tree)

**位置**: `drivers/virtio/virtio_mmio.c:786-798`

```c
static const struct of_device_id virtio_mmio_match[] = {
    { .compatible = "virtio,mmio", },
    {},
};
MODULE_DEVICE_TABLE(of, virtio_mmio_match);

#ifdef CONFIG_ACPI
static const struct acpi_device_id virtio_mmio_acpi_match[] = {
    { "LNRO0005", },
    { }
};
MODULE_DEVICE_TABLE(acpi, virtio_mmio_acpi_match);
#endif
```

**Device Tree 示例**:

```dts
virtio_block@1e000 {
    compatible = "virtio,mmio";
    reg = <0x1e000 0x100>;
    interrupts = <42>;
};
```

---

## 7. 中断和通知机制

### 7.1 MSI/MSI-X 中断配置

#### 分配 MSI-X 向量

**位置**: `drivers/virtio/virtio_pci_common.c:126-196`

```c
static int vp_request_msix_vectors(struct virtio_device *vdev, int nvectors,
                                  bool per_vq_vectors, struct irq_affinity *desc)
{
    struct virtio_pci_device *vp_dev = to_vp_device(vdev);

    // 分配 MSI-X 向量
    err = pci_alloc_irq_vectors_affinity(vp_dev->pci_dev, nvectors,
                                         nvectors, PCI_IRQ_MSIX | PCI_IRQ_AFFINITY, desc);

    // 配置中断处理
    // 向量 0: 配置更改中断
    // 向量 1+: 虚拟队列中断(可选每队列独立)
}
```

### 7.2 通知机制

#### PCI Modern 通知

**位置**: `drivers/virtio/virtio_pci_common.c:51-57`

```c
bool vp_notify(struct virtqueue *vq)
{
    // 写入队列索引到通知寄存器
    iowrite16(vq->index, (void __iomem *)vq->priv);
    return true;
}

static bool vp_notify_with_data(struct virtqueue *vq)
{
    u32 data = vring_notification_data(vq);
    iowrite32(data, (void __iomem *)vq->priv);
    return true;
}
```

#### MMIO 通知

**位置**: `drivers/virtio/virtio_mmio.c:264-282`

```c
static bool vm_notify(struct virtqueue *vq)
{
    struct virtio_mmio_device *vm_dev = to_virtio_mmio_device(vq->vdev);

    // 写入队列选择器到通知寄存器
    writel(vq->index, vm_dev->base + VIRTIO_MMIO_QUEUE_NOTIFY);
    return true;
}

static bool vm_notify_with_data(struct virtqueue *vq)
{
    struct virtio_mmio_device *vm_dev = to_virtio_mmio_device(vq->vdev);
    u32 data = vring_notification_data(vq);

    writel(data, vm_dev->base + VIRTIO_MMIO_QUEUE_NOTIFY);
    return true;
}
```

### 7.3 共享内存区域

**位置**: `drivers/virtio/virtio_pci_modern.c:781-878`

```c
static int virtio_pci_find_shm_cap(struct pci_dev *dev, u8 required_id,
                                   u8 *bar, u64 *offset, u64 *len)
{
    // 遍历 VIRTIO_PCI_CAP_SHARED_MEMORY_CFG 类型 capability
    for (pos = pci_find_capability(dev, PCI_CAP_ID_VNDR); pos > 0;
         pos = pci_find_next_capability(dev, pos, PCI_CAP_ID_VNDR)) {
        // 读取并验证 capability
        // 返回 BAR、偏移和长度
    }
}

static bool vp_get_shm_region(struct virtio_device *vdev,
                              struct virtio_shm_region *region, u8 id)
{
    struct virtio_pci_device *vp_dev = to_vp_device(vdev);
    struct pci_dev *pci_dev = vp_dev->pci_dev;
    u8 bar;
    u64 offset, len;

    if (!virtio_pci_find_shm_cap(pci_dev, id, &bar, &offset, &len))
        return false;

    region->len = len;
    region->addr = pci_resource_start(pci_dev, bar) + offset;
    return true;
}
```

---

## 8. 架构图

### 8.1 Virtio 传输层整体架构

```
+------------------------------------------------------------------+
|                         Guest OS                                  |
|                                                                  |
|  +----------------------+    +----------------------+            |
|  |     virtio-blk      |    |     virtio-net       |            |
|  +---------+------------+    +---------+------------+            |
|            |                          |                          |
|            v                          v                          |
|  +------------------------------------------------------------+  |
|  |              virtio_config_ops                             |  |
|  |  +------------+  +------------+  +-------------+           |  |
|  |  | PCI Modern |  | PCI Legacy |  |    MMIO     |           |  |
|  |  +-----+------+  +-----+------+  +------+------+           |  |
|  +------------------------------------------------------------+  |
|            |                |                |                  |
|            v                v                v                  |
|  +------------+    +------------+    +------------+             |
|  | virtio_pci |    | virtio_pci |    | virtio_mmio|             |
|  | _modern.c  |    | _legacy.c  |    |    .c      |             |
|  +------------+    +------------+    +------------+             |
|            |                |                |                  |
|            v                v                v                  |
|  +------------------------------------------------------------+  |
|  |                     virtio.c                              |  |
|  |              (Virtio Bus Driver)                         |  |
|  +------------------------------------------------------------+  |
|                              |                                   |
+------------------------------|-----------------------------------+
                               |
                    +----------v----------+
                    |    Hardware/        |
                    |    Hypervisor       |
                    |    (QEMU/VFIO)      |
                    +---------------------+
```

### 8.2 PCI Modern 设备结构

```
+------------------+        +------------------+
|   PCI Bus Layer  |        |    pci_driver   |
+--------+---------+        +--------+---------+
         |                           |
         v                           v
+------------------+        +------------------+
| virtio_pci_dev   |        | virtio_pci_driver|
| (probe/remove)   |<------>| (id_table)       |
+--------+---------+        +------------------+
         |
         v
+------------------+        +------------------+
| virtio_pci_      |        | virtio_pci_      |
| modern_device     |        | modern_device    |
| (struct)         |        | (operations)     |
+--------+---------+        +--------+---------+
         |                           |
         +------------+---------------+
                      |
                      v
         +------------------------+
         | virtio_pci_common_cfg |
         | (MMIO Registers)       |
         +------------------------+
                      |
                      v
         +------------------------+
         | virtio_pci_modern_    |
         | common_cfg fields     |
         +------------------------+
```

### 8.3 中断处理流程

```
+------------------+     +------------------+     +------------------+
|   HW Interrupt  | --> |   PCI/MSI-X      | --> |  vring_interrupt |
|   (队列/配置)    |     |   Controller     |     |  ()              |
+------------------+     +------------------+     +--------+---------+
                                                            |
                         +----------------------------------+
                         |              v                   |
               +---------v---------+    +---------v---------+
               | virtqueue callback |    | virtqueue callback|
               | (blk/rng/scsi...) |    | (net/balloon...)  |
               +-------------------+    +------------------+
```

### 8.4 Virtio 设备探测时序图

```
Guest Driver          Virtio Layer          PCI Layer          HW/QEMU
    |                     |                     |                 |
    |                     |                     |                 |
    |---pci_register_driver-->                  |                 |
    |                     |---pci_bus_add_dev-->|                 |
    |                     |<----probe callback--|                 |
    |                     |                     |                 |
    |                     |--pci_enable_device->|                 |
    |                     |<--rc----------------|                 |
    |                     |                     |                 |
    |                     |--virtio_pci_modern_probe->           |
    |                     |<--查找 CAPABILITYs---|<--PCI config---|
    |                     |                     |                 |
    |                     |--ioremap BARs------>|                 |
    |                     |                     |                 |
    |                     |--register_virtio_device->             |
    |                     |<--设备添加到 bus----|                 |
    |                     |                     |                 |
    |---virtio_dev_probe--|                     |                 |
    |---get_features----->|--->                 |                 |
    |<--device_features---|                     |                 |
    |---validate_features|                     |                 |
    |---finalize_features|                     |                 |
    |---find_vqs--------->|--->                 |                 |
    |<--返回 virtqueue----|                     |                 |
    |---set_status(DRIVER_OK)                  |                 |
    |                     |                     |                 |
```

---

## 附录 A: 关键代码位置索引

| 功能 | 文件 | 行号 |
|------|------|------|
| virtio_device 定义 | `include/linux/virtio.h` | 168-189 |
| virtqueue 定义 | `include/linux/virtio.h` | 19-44 |
| virtio_config_ops 定义 | `include/linux/virtio_config.h` | 112-140 |
| PCI 探测主函数 | `drivers/virtio/virtio_pci_common.c` | 679-740 |
| Modern 探测 | `drivers/virtio/virtio_pci_modern_dev.c` | 223-369 |
| Legacy 探测 | `drivers/virtio/virtio_pci_legacy_dev.c` | 16-62 |
| MSI-X 配置 | `drivers/virtio/virtio_pci_common.c` | 126-196 |
| find_vqs 实现 | `drivers/virtio/virtio_pci_common.c` | 514-543 |
| MMIO 探测 | `drivers/virtio/virtio_mmio.c` | 572-651 |
| MMIO 中断 | `drivers/virtio/virtio_mmio.c` | 285-307 |
| 总线注册 | `drivers/virtio/virtio.c` | 709-727 |
| 设备注册 | `drivers/virtio/virtio.c` | 517-572 |

---

## 附录 B: 特性位说明

| 特性位 | 值 | 描述 |
|-------|---|------|
| VIRTIO_F_VERSION_1 | 32 | 设备符合 Virtio 1.0 规范 |
| VIRTIO_F_RING_RESET | 33 | 支持队列重置 |
| VIRTIO_F_SR_IOV | 34 | 支持 SR-IOV |
| VIRTIO_F_ADMIN_VQ | 40 | 支持管理队列 |
| VIRTIO_F_NOTIFICATION_DATA | 58 | 通知包含额外数据 |
| VIRTIO_F_ACCESS_PLATFORM | 33 | 需要平台 DMA 访问 |

---

*文档版本: 1.0*
*生成日期: 2026-04-26*
*分析基于: Linux kernel master branch*
