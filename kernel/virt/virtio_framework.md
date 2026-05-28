# Linux 内核 Virtio Para-virtualization 框架分析文档

## 目录

1. [概述](#1-概述)
2. [Virtio 核心数据结构](#2-virtio-核心数据结构)
3. [Virtio Ring 实现](#3-virtio-ring-实现)
4. [Virtio 设备发现与初始化](#4-virtio-设备发现与初始化)
5. [Virtio 设备状态机](#5-virtio-设备状态机)
6. [特征位 (Feature Bits)](#6-特征位-feature-bits)
7. [Virtqueue 操作流程](#7-virtqueue-操作流程)
8. [源码位置索引](#8-源码位置索引)

---

## 1. 概述

Virtio 是一个开放标准,定义了不同类型设备与驱动程序之间通信的协议。最初作为 hypervisor 实现的半虚拟化设备标准,现在已可用于任何符合规范的设备(真实或模拟)。

### 1.1 关键组件

```
virtio/
├── virtio.c          # 核心框架实现
├── virtio_ring.c     # 虚拟队列Ring实现
├── virtio_pci*.c     # PCI传输实现
├── virtio_mmio.c     # MMIO传输实现
└── virtio_config.c   # 配置接口
```

### 1.2 Virtio 架构

```
+------------------+     +------------------+
|   Guest OS       |     |   Host/Hypervisor|
|                  |     |                  |
| +--------------+ |     | +--------------+ |
| | Virtio Driver| |<--->| | Virtio Device| |
| +--------------+ |     | +--------------+ |
|        |        |     |        |        |
|        v        |     |        v        |
| +--------------+ |     | +--------------+ |
| | Virtqueue    | |     | | Virtqueue    | |
| +--------------+ |     | +--------------+ |
|        |        |     |        |        |
+--------|---------+     +--------|---------+
         |                       |
         v                       v
   Shared Memory (DMA accessible by both)
```

---

## 2. Virtio 核心数据结构

### 2.1 struct virtio_device

**文件**: `/Users/sphinx/github/linux/include/linux/virtio.h` (第 168-189 行)

```c
struct virtio_device {
    int index;                      // 设备唯一索引
    bool failed;                    // 失败状态标志
    bool config_core_enabled;       // 配置变化报告启用标志
    bool config_driver_disabled;     // 驱动禁用配置报告
    bool config_change_pending;      // 待处理的配置变更
    spinlock_t config_lock;         // 保护配置变更报告
    spinlock_t vqs_list_lock;       // 保护vqs列表
    struct device dev;              // 底层设备
    struct virtio_device_id id;      // 设备类型标识
    const struct virtio_config_ops *config;     // 配置操作接口
    const struct vringh_config_ops *vringh_config;
    const struct virtio_map_ops *map;
    struct list_head vqs;           // 虚拟队列链表
    VIRTIO_DECLARE_FEATURES(features);  // 特性位
    void *priv;                     // 驱动私有数据
    union virtio_map vmap;
#ifdef CONFIG_VIRTIO_DEBUG
    struct dentry *debugfs_dir;
    u64 debugfs_filter_features[VIRTIO_FEATURES_U64S];
#endif
};
```

### 2.2 struct virtqueue

**文件**: `/Users/sphinx/github/linux/include/linux/virtio.h` (第 19-44 行)

```c
struct virtqueue {
    struct list_head list;          // 设备虚拟队列链表
    void (*callback)(struct virtqueue *vq);  // 缓冲区消费回调
    const char *name;              // 队列名称(调试用)
    struct virtio_device *vdev;     // 所属virtio设备
    unsigned int index;            // 队列序号
    unsigned int num_free;         // 可用缓冲区数量
    unsigned int num_max;          // 设备支持最大数量
    bool reset;                    // 队列是否处于复位状态
    void *priv;                    // 队列实现私有数据
};
```

### 2.3 struct virtio_driver

**文件**: `/Users/sphinx/github/linux/include/linux/virtio.h` (第 222-264 行)

```c
struct virtio_driver {
    struct device_driver driver;    // 底层设备驱动
    const struct virtio_device_id *id_table;  // 支持的设备ID表
    const unsigned int *feature_table;        // 支持的特性位表
    unsigned int feature_table_size;           // 特性位表大小
    const unsigned int *feature_table_legacy; // 遗留模式特性位表
    unsigned int feature_table_size_legacy;   // 遗留特性位表大小
    int (*validate)(struct virtio_device *dev);  // 特性验证
    int (*probe)(struct virtio_device *dev);     // 设备探测
    void (*scan)(struct virtio_device *dev);     // 扫描(可选)
    void (*remove)(struct virtio_device *dev);   // 设备移除
    void (*config_changed)(struct virtio_device *dev);  // 配置变更回调
    int (*freeze)(struct virtio_device *dev);    // 冻结(挂起)
    int (*restore)(struct virtio_device *dev);   // 恢复(Resume)
    int (*reset_prepare)(struct virtio_device *dev);   // 复位准备
    int (*reset_done)(struct virtio_device *dev);       // 复位完成
    void (*shutdown)(struct virtio_device *dev);        // 关闭同步
};
```

### 2.4 struct virtio_config_ops

**文件**: `/Users/sphinx/github/linux/include/linux/virtio_config.h` (第 112-140 行)

```c
struct virtio_config_ops {
    void (*get)(struct virtio_device *vdev, unsigned offset,
                void *buf, unsigned len);           // 读取配置字段
    void (*set)(struct virtio_device *vdev, unsigned offset,
                const void *buf, unsigned len);     // 写入配置字段
    u32 (*generation)(struct virtio_device *vdev);  // 配置代数计数器
    u8 (*get_status)(struct virtio_device *vdev);   // 获取状态字节
    void (*set_status)(struct virtio_device *dev, u8 status);  // 设置状态字节
    void (*reset)(struct virtio_device *vdev);      // 复位设备
    int (*find_vqs)(struct virtio_device *vdev, unsigned int nvqs,
                    struct virtqueue *vqs[], struct virtqueue_info vqs_info[],
                    struct irq_affinity *desc);    // 查找虚拟队列
    void (*del_vqs)(struct virtio_device *);         // 删除虚拟队列
    void (*synchronize_cbs)(struct virtio_device *); // 同步回调
    u64 (*get_features)(struct virtio_device *vdev);    // 获取设备特性
    void (*get_extended_features)(struct virtio_device *vdev, u64 *features);
    int (*finalize_features)(struct virtio_device *vdev); // 完成特性协商
    const char *(*bus_name)(struct virtio_device *vdev);   // 总线名称
    int (*set_vq_affinity)(struct virtqueue *vq, const struct cpumask *cpu_mask);
    const struct cpumask *(*get_vq_affinity)(struct virtio_device *vdev, int index);
    bool (*get_shm_region)(struct virtio_device *vdev,
                           struct virtio_shm_region *region, u8 id);
    int (*disable_vq_and_reset)(struct virtqueue *vq);  // 禁用队列并复位
    int (*enable_vq_after_reset)(struct virtqueue *vq); // 复位后启用队列
};
```

---

## 3. Virtio Ring 实现

### 3.1 VRing 数据结构 (Split Ring)

**文件**: `/Users/sphinx/github/linux/include/uapi/linux/virtio_ring.h` (第 104-163 行)

```c
// 描述符结构 - 16字节,描述一个缓冲区
struct vring_desc {
    __virtio64 addr;      // 缓冲区地址(Guest物理地址)
    __virtio32 len;       // 缓冲区长度
    __virtio16 flags;     // 描述符标志
    __virtio16 next;      // 链中下一个描述符索引
};

// 可用环结构 - Guest填充,Host消费
struct vring_avail {
    __virtio16 flags;     // 标志(VRING_AVAIL_F_NO_INTERRUPT)
    __virtio16 idx;       // 环索引
    __virtio16 ring[];    // 可用描述符头数组
};

// 已用环元素结构
struct vring_used_elem {
    __virtio32 id;        // 使用的描述符链起始索引
    __virtio32 len;       // 描述符链总长度(写入的字节)
};

// 已用环结构 - Host填充,Guest消费
struct vring_used {
    __virtio16 flags;     // 标志(VRING_USED_F_NO_NOTIFY)
    __virtio16 idx;       // 环索引
    vring_used_elem_t ring[];  // 已用描述符数组
};

// 完整VRing结构
struct vring {
    unsigned int num;         // 描述符数量
    vring_desc_t *desc;       // 描述符数组
    vring_avail_t *avail;     // 可用环
    vring_used_t *used;       // 已用环
};
```

### 3.2 描述符链 (Descriptor Chain)

**文件**: `/Users/sphinx/github/linux/include/uapi/linux/virtio_ring.h` (第 37-42 行)

```
缓冲区类型标志:
- VRING_DESC_F_NEXT (1):    缓冲区通过next字段继续
- VRING_DESC_F_WRITE (2):    缓冲区是写密集型(否则只读)
- VRING_DESC_F_INDIRECT (4): 缓冲区包含描述符列表
```

** Descriptor Chain 示意图 **:

```
单个缓冲区链:
+--------+    +--------+    +--------+
| Desc 0 | -> | Desc 1 | -> | Desc 2 | -> NULL
+--------+    +--------+    +--------+
   |             |             |
   v             v             v
+--------+    +--------+    +--------+
| Buffer |    | Buffer |    | Buffer |
|  (S/G) |    |  (S/G) |    |  (S/G) |
+--------+    +--------+    +--------+

间接描述符:
+--------+
| Indirect|
|  Desc   | ---> 包含描述符数组的缓冲区
+--------+
```

### 3.3 vring_init - VRing 初始化

**文件**: `/Users/sphinx/github/linux/include/uapi/linux/virtio_ring.h` (第 196-204 行)

```c
static inline void vring_init(struct vring *vr, unsigned int num, void *p,
                              unsigned long align)
{
    vr->num = num;
    vr->desc = p;
    vr->avail = (struct vring_avail *)((char *)p + num * sizeof(struct vring_desc));
    vr->used = (void *)(((unsigned long)&vr->avail->ring[num] + sizeof(__virtio16)
        + align-1) & ~(align - 1));
}
```

**内存布局**:
```
+-------------------+
| vring_desc[num]  |  描述符数组
+-------------------+
| avail->flags      |  2字节
| avail->idx        |  2字节
| avail->ring[num]  |  2*num 字节
| used_event_idx    |  2字节
+-------------------+  (对齐到align边界)
| used->flags       |  2字节
| used->idx         |  2字节
| used->ring[]      |  8*num 字节
| avail_event_idx   |  2字节
+-------------------+
```

### 3.4 vring_size - 计算 VRing 大小

**文件**: `/Users/sphinx/github/linux/include/uapi/linux/virtio_ring.h` (第 206-211 行)

```c
static inline unsigned vring_size(unsigned int num, unsigned long align)
{
    return ((sizeof(struct vring_desc) * num + sizeof(__virtio16) * (3 + num)
             + align - 1) & ~(align - 1))
        + sizeof(__virtio16) * 3 + sizeof(struct vring_used_elem) * num;
}
```

### 3.5 struct vring_virtqueue

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_ring.c` (第 106-273 行)

```c
struct vring_virtqueue {
    struct virtqueue vq;           // 通用virtqueue

    bool use_map_api;             // 是否使用DMA API
    bool weak_barriers;           // 是否使用弱内存屏障
    bool broken;                  // 队列已损坏
    bool indirect;                // 支持间接描述符
    bool event;                  // 支持avail event idx

    enum vq_layout layout;        // 队列布局类型
    unsigned int free_head;       // 空闲描述符链表头
    struct used_entry {
        u32 id;
        u32 len;
    } batch_last;                // 批处理最后条目(IN_ORDER使用)

    unsigned int num_added;       // 添加的缓冲区计数
    u16 last_used_idx;            // 上次使用的索引
    u16 last_used;                // 上次使用的描述符ID
    bool event_triggered;         // 事件已触发标志

    union {
        struct vring_virtqueue_split split;    // Split Ring数据
        struct vring_virtqueue_packed packed;   // Packed Ring数据
    };

    bool (*notify)(struct virtqueue *vq);  // 通知回调
    bool we_own_ring;                // 是否拥有ring内存
    union virtio_map map;            // DMA映射信息
};
```

### 3.6 Packed Ring 结构

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_ring.c` (第 135-169 行)

```c
struct vring_virtqueue_packed {
    struct {
        unsigned int num;
        struct vring_packed_desc *desc;      // 描述符数组
        struct vring_packed_desc_event *driver;  // 驱动事件
        struct vring_packed_desc_event *device;  // 设备事件
    } vring;

    bool avail_wrap_counter;        // 可用环包装计数器
    u16 avail_used_flags;           // 可用已用标志
    u16 next_avail_idx;             // 下一可用索引
    u16 event_flags_shadow;         // 事件标志影子

    struct vring_desc_state_packed *desc_state;  // 描述符状态
    struct vring_desc_extra *desc_extra;         // 额外描述符信息

    dma_addr_t ring_dma_addr;      // Ring DMA地址
    dma_addr_t driver_event_dma_addr;
    dma_addr_t device_event_dma_addr;
    size_t ring_size_in_bytes;
    size_t event_size_in_bytes;
};

// 打包描述符事件结构
struct vring_packed_desc_event {
    __le16 off_wrap;   // 描述符环变化事件偏移/包装计数器
    __le16 flags;      // 描述符环变化事件标志
};

// 打包描述符
struct vring_packed_desc {
    __le64 addr;       // 缓冲区地址
    __le32 len;        // 缓冲区长度
    __le16 id;         // 描述符ID
    __le16 flags;      // 标志
};
```

---

## 4. Virtio 设备发现与初始化

### 4.1 驱动注册

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio.c` (第 449-458 行)

```c
int __register_virtio_driver(struct virtio_driver *driver, struct module *owner)
{
    BUG_ON(driver->feature_table_size && !driver->feature_table);
    driver->driver.bus = &virtio_bus;    // 绑定到virtio总线
    driver->driver.owner = owner;

    return driver_register(&driver->driver);
}
```

使用宏简化注册:
```c
#define register_virtio_driver(drv) \
    __register_virtio_driver(drv, THIS_MODULE)

#define module_virtio_driver(__virtio_driver) \
    module_driver(__virtio_driver, register_virtio_driver, \
            unregister_virtio_driver)
```

### 4.2 virtio_bus 总线定义

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio.c` (第 438-447 行)

```c
static const struct bus_type virtio_bus = {
    .name  = "virtio",
    .match = virtio_dev_match,           // 设备-驱动匹配
    .dev_groups = virtio_dev_groups,     // 设备属性组
    .uevent = virtio_uevent,            // 热插拔事件
    .probe = virtio_dev_probe,           // 设备探测
    .remove = virtio_dev_remove,         // 设备移除
    .irq_get_affinity = virtio_irq_get_affinity,
    .shutdown = virtio_dev_shutdown,     // 关闭回调
};
```

### 4.3 设备-驱动匹配

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio.c` (第 74-96 行)

```c
static int virtio_dev_match(struct device *_dv, const struct device_driver *_dr)
{
    unsigned int i;
    struct virtio_device *dev = dev_to_virtio(_dv);
    const struct virtio_device_id *ids;

    ids = drv_to_virtio(_dr)->id_table;
    for (i = 0; ids[i].device; i++)
        if (virtio_id_match(dev, &ids[i]))
            return 1;
    return 0;
}

static inline int virtio_id_match(const struct virtio_device *dev,
                  const struct virtio_device_id *id)
{
    // 检查设备ID和厂商ID是否匹配
    if (id->device != dev->id.device && id->device != VIRTIO_DEV_ANY_ID)
        return 0;
    return id->vendor == VIRTIO_DEV_ANY_ID || id->vendor == dev->id.vendor;
}
```

### 4.4 register_virtio_device - 设备注册

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio.c` (第 517-573 行)

```c
int register_virtio_device(struct virtio_device *dev)
{
    int err;

    dev->dev.bus = &virtio_bus;           // 设置总线
    device_initialize(&dev->dev);

    // 分配唯一设备索引
    err = ida_alloc(&virtio_index_ida, GFP_KERNEL);
    if (err < 0)
        goto out;

    dev->index = err;
    err = dev_set_name(&dev->dev, "virtio%u", dev->index);

    // 初始化OF节点(设备树)
    err = virtio_device_of_init(dev);

    spin_lock_init(&dev->config_lock);
    dev->config_driver_disabled = false;
    dev->config_core_enabled = false;
    dev->config_change_pending = false;

    INIT_LIST_HEAD(&dev->vqs);
    spin_lock_init(&dev->vqs_list_lock);

    // 复位设备(以防之前驱动搞乱了)
    virtio_reset_device(dev);

    // 确认已看到设备
    virtio_add_status(dev, VIRTIO_CONFIG_S_ACKNOWLEDGE);

    virtio_debug_device_init(dev);

    // 添加到总线,触发驱动探测
    err = device_add(&dev->dev);
    if (err)
        goto out_of_node_put;

    return 0;
    // ...错误处理
}
```

### 4.5 virtio_dev_probe - 设备探测

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio.c` (第 270-366 行)

```c
static int virtio_dev_probe(struct device *_d)
{
    int err, i;
    struct virtio_device *dev = dev_to_virtio(_d);
    struct virtio_driver *drv = drv_to_virtio(dev->dev.driver);
    u64 device_features[VIRTIO_FEATURES_U64S];
    u64 driver_features[VIRTIO_FEATURES_U64S];
    u64 driver_features_legacy;

    // 步骤1: 设置DRIVER状态
    virtio_add_status(dev, VIRTIO_CONFIG_S_DRIVER);

    // 步骤2: 获取设备支持的特性
    virtio_get_features(dev, device_features);

    // 步骤3: 构建驱动特性位图
    virtio_features_zero(driver_features);
    for (i = 0; i < drv->feature_table_size; i++) {
        unsigned int f = drv->feature_table[i];
        if (!WARN_ON_ONCE(f >= VIRTIO_FEATURES_BITS))
            virtio_features_set_bit(driver_features, f);
    }

    // 步骤4: 计算共同支持特性
    if (virtio_features_test_bit(device_features, VIRTIO_F_VERSION_1)) {
        for (i = 0; i < VIRTIO_FEATURES_U64S; ++i)
            dev->features_array[i] = driver_features[i] & device_features[i];
    } else {
        virtio_features_from_u64(dev->features_array,
                     driver_features_legacy & device_features[0]);
    }

    // 步骤5: 保留传输层特性位
    for (i = VIRTIO_TRANSPORT_F_START; i < VIRTIO_TRANSPORT_F_END; i++)
        if (virtio_features_test_bit(device_features, i))
            __virtio_set_bit(dev, i);

    // 步骤6: 完成特性协商
    err = dev->config->finalize_features(dev);

    // 步骤7: 驱动验证
    if (drv->validate) {
        err = drv->validate(dev);
        if (err)
            goto err;
    }

    // 步骤8: 检查特性OK
    err = virtio_features_ok(dev);
    if (err)
        goto err;

    // 步骤9: 调用驱动probe
    err = drv->probe(dev);
    if (err)
        goto err;

    // 步骤10: 设置DRIVER_OK
    if (!(dev->config->get_status(dev) & VIRTIO_CONFIG_S_DRIVER_OK))
        virtio_device_ready(dev);

    if (drv->scan)
        drv->scan(dev);

    virtio_config_core_enable(dev);

    return 0;

err:
    virtio_add_status(dev, VIRTIO_CONFIG_S_FAILED);
    return err;
}
```

---

## 5. Virtio 设备状态机

### 5.1 状态定义

**文件**: `/Users/sphinx/github/linux/include/uapi/linux/virtio_config.h` (第 36-46 行)

```c
/* 状态字节定义 - Guest报告进度并同步特性 */
#define VIRTIO_CONFIG_S_ACKNOWLEDGE    1  // 已看到设备
#define VIRTIO_CONFIG_S_DRIVER         2  // 已找到驱动
#define VIRTIO_CONFIG_S_DRIVER_OK      4  // 驱动配置完成
#define VIRTIO_CONFIG_S_FEATURES_OK    8  // 特性协商完成
#define VIRTIO_CONFIG_S_NEEDS_RESET    0x40  // 设备需要复位
#define VIRTIO_CONFIG_S_FAILED         0x80  // 放弃此设备
```

### 5.2 状态转换图

```
                      +-----------------+
                      | 未初始化        |
                      | (设备被发现)    |
                      +-----------------+
                              |
                              v
                      +-----------------+
            +---------| S_ACKNOWLEDGE   |
            |         +-----------------+
            |                   |
            |                   v
            |         +-----------------+
            |         | S_DRIVER        |
            |         | (驱动已绑定)     |
            |         +-----------------+
            |                   |
            |                   v
            |         +-----------------+
            |         | S_DRIVER_OK     |
   失败复位  |         | (驱动就绪)     |
   -------->+|         +-----------------+
            |                   |
            |                   v
            |         +-----------------+
            | +-------| S_FEATURES_OK   |
            | |       | (特性协商完成)  |
            | |       +-----------------+
            | |                 |
            | |     验证失败    v
            | |       +-----------------+
            | +------>| S_FAILED       |<-------+
            |         | (驱动失败)      |        |
            |         +-----------------+        |
            |                                   |
            +-----------------------------------+
                              |
                              v
                      +-----------------+
                      | S_NEEDS_RESET   |
                      | (设备需复位)    |
                      +-----------------+
```

### 5.3 virtio_add_status - 添加状态

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio.c` (第 196-201 行)

```c
void virtio_add_status(struct virtio_device *dev, unsigned int status)
{
    might_sleep();
    dev->config->set_status(dev, dev->config->get_status(dev) | status);
}
```

---

## 6. 特征位 (Feature Bits)

### 6.1 特性位定义

**文件**: `/Users/sphinx/github/linux/include/uapi/linux/virtio_config.h` (第 54-121 行)

```c
// 传输层特性范围 (保留给具体传输实现)
#define VIRTIO_TRANSPORT_F_START   28
#define VIRTIO_TRANSPORT_F_END     42

// 通用特性位
#ifndef VIRTIO_CONFIG_NO_LEGACY
#define VIRTIO_F_NOTIFY_ON_EMPTY   24  // 环空时通知
#define VIRTIO_F_ANY_LAYOUT        27  // 支持任意描述符布局
#endif

#define VIRTIO_F_VERSION_1         32  // v1.0兼容
#define VIRTIO_F_ACCESS_PLATFORM   33  // 平台DMA访问
#define VIRTIO_F_RING_PACKED       34  // 打包virtqueue布局
#define VIRTIO_F_IN_ORDER          35  // 按顺序使用缓冲区
#define VIRTIO_F_ORDER_PLATFORM     36  // 平台排序内存
#define VIRTIO_F_SR_IOV            37  // 支持SR-IOV
#define VIRTIO_F_NOTIFICATION_DATA 38  // 通知中传递额外数据
#define VIRTIO_F_NOTIF_CONFIG_DATA 39  // 通知配置数据
#define VIRTIO_F_RING_RESET        40  // 支持队列单独复位
#define VIRTIO_F_ADMIN_VQ          41  // 支持管理virtqueue

// Virtqueue特性位
#define VIRTIO_RING_F_INDIRECT_DESC 28  // 支持间接描述符
#define VIRTIO_RING_F_EVENT_IDX    29   // 支持事件索引
```

### 6.2 特性位操作

**文件**: `/Users/sphinx/github/linux/include/linux/virtio_config.h` (第 225-265 行)

```c
// 测试特性位
static inline bool __virtio_test_bit(const struct virtio_device *vdev,
                     unsigned int fbit)
{
    return virtio_features_test_bit(vdev->features_array, fbit);
}

// 设置特性位
static inline void __virtio_set_bit(struct virtio_device *vdev,
                       unsigned int fbit)
{
    virtio_features_set_bit(vdev->features_array, fbit);
}

// 清除特性位
static inline void __virtio_clear_bit(struct virtio_device *vdev,
                     unsigned int fbit)
{
    virtio_features_clear_bit(vdev->features_array, fbit);
}

// 检查设备是否有某特性
static inline bool virtio_has_feature(const struct virtio_device *vdev,
                      unsigned int fbit)
{
    if (fbit < VIRTIO_TRANSPORT_F_START)
        virtio_check_driver_offered_feature(vdev, fbit);

    return __virtio_test_bit(vdev, fbit);
}
```

### 6.3 vring_transport_features - 传输层特性

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_ring.c` (第 2525-2543 行)

```c
void vring_transport_features(struct virtio_device *vdev)
{
    unsigned int i;

    for (i = VIRTIO_TRANSPORT_F_START; i < VIRTIO_TRANSPORT_F_END; i++) {
        switch (i) {
        case VIRTIO_RING_F_INDIRECT_DESC:
            if (!virtio_has_feature(vdev, VIRTIO_RING_F_INDIRECT_DESC))
                break;
            /* 驱动支持间接描述符 */
            break;
        case VIRTIO_RING_F_EVENT_IDX:
            if (!virtio_has_feature(vdev, VIRTIO_RING_F_EVENT_IDX))
                break;
            /* 驱动支持事件索引 */
            break;
        case VIRTIO_F_VERSION_1:
            /* v1.0支持是必须的 */
            break;
        case VIRTIO_F_ACCESS_PLATFORM:
        case VIRTIO_F_RING_PACKED:
        case VIRTIO_F_IN_ORDER:
        case VIRTIO_F_ORDER_PLATFORM:
            /* 这些特性需要传输层支持 */
            break;
        default:
            /* 未知特性位 */
            break;
        }
    }
}
```

---

## 7. Virtqueue 操作流程

### 7.1 Virtqueue 创建流程

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_ring.c` (第 3260-3283 行)

```c
struct virtqueue *vring_create_virtqueue(
    unsigned int index,
    unsigned int num,
    unsigned int vring_align,
    struct virtio_device *vdev,
    bool weak_barriers,
    bool may_reduce_num,
    bool context,
    bool (*notify)(struct virtqueue *vq),
    void (*callback)(struct virtqueue *vq),
    const char *name)
{
    union virtio_map map = {.dma_dev = vdev->dev.parent};

    // 根据设备特性选择Packed或Split Ring
    if (virtio_has_feature(vdev, VIRTIO_F_RING_PACKED))
        return vring_create_virtqueue_packed(...);
    return vring_create_virtqueue_split(...);
}
```

### 7.2 virtqueue_add - 添加缓冲区

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_ring.c` (第 599-792 行)

**Split Ring 添加流程**:

```
1. 验证队列状态
   START_USE(vq)
   检查 vq->broken 状态

2. 检查可用空间
   if (vq->vq.num_free < descs_used)
       return -ENOSPC

3. 分配描述符
   - 如果使用间接描述符: alloc_indirect_split()
   - 否则: 使用 free_head 指向的空闲描述符

4. 填充描述符
   for (out_sgs):
       设置 VRING_DESC_F_NEXT 标志
       映射 DMA 地址
   for (in_sgs):
       设置 VRING_DESC_F_WRITE 标志
       映射 DMA 地址

5. 更新 free_head
   - IN_ORDER: free_head += descs_used
   - 非IN_ORDER: free_head = last_desc.next

6. 存储用户数据
   vq->split.desc_state[head].data = data

7. 添加到可用环
   avail = vq->split.avail_idx_shadow & (num - 1)
   vq->split.vring.avail->ring[avail] = head

8. 更新索引
   virtio_wmb()  // 内存屏障
   vq->split.avail_idx_shadow++
   vq->split.vring.avail->idx = avail_idx_shadow
   vq->num_added++

9. 可能触发 kick
   if (vq->num_added == (1 << 16) - 1)
       virtqueue_kick(&vq->vq)

   END_USE(vq)
```

### 7.3 virtqueue_get_buf - 获取完成缓冲区

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_ring.c` (第 917-972 行)

**Split Ring 获取流程**:

```
1. 验证队列状态
   START_USE(vq)
   检查 vq->broken 状态

2. 检查是否有已用缓冲区
   if (!more_used_split(vq))
       return NULL

3. 内存屏障
   virtio_rmb(vq->weak_barriers)

4. 获取已用环入口
   last_used = vq->last_used & (num - 1)
   i = vq->split.vring.used->ring[last_used].id
   len = vq->split.vring.used->ring[last_used].len

5. 验证描述符
   if (i >= num || !vq->split.desc_state[i].data)
       return NULL

6. 获取用户数据
   ret = vq->split.desc_state[i].data

7. 分离描述符
   detach_buf_split(vq, i, ctx)

8. 更新 last_used_idx
   vq->last_used_idx++

9. 更新事件索引(如果需要)
   if (!(avail_flags & VRING_AVAIL_F_NO_INTERRUPT))
       vring_used_event(vq->split.vring) = last_used_idx

10. END_USE(vq)
    return ret
```

### 7.4 virtqueue_kick - 通知Host

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_ring.c` (第 794-822 行)

```c
static bool virtqueue_kick_prepare_split(struct vring_virtqueue *vq)
{
    u16 new, old;
    bool needs_kick;

    START_USE(vq);

    // 确保新可用条目已暴露
    virtio_mb(vq->weak_barriers);

    old = vq->split.avail_idx_shadow - vq->num_added;
    new = vq->split.avail_idx_shadow;
    vq->num_added = 0;

    // 根据事件索引或标志判断是否需要kick
    if (vq->event) {
        needs_kick = vring_need_event(
            vring_avail_event(&vq->split.vring), new, old);
    } else {
        needs_kick = !(vq->split.vring.used->flags &
                VRING_USED_F_NO_NOTIFY);
    }

    END_USE(vq);
    return needs_kick;
}
```

### 7.5 vring_interrupt - 中断处理

**文件**: `/Users/sphinx/github/linux/drivers/virtio/virtio_ring.c` (第 3225-3258 行)

```c
irqreturn_t vring_interrupt(int irq, void *_vq)
{
    struct vring_virtqueue *vq = to_vvq(_vq);

    if (!more_used(vq)) {
        pr_debug("virtqueue callback with nothing new\n");
        return IRQ_NONE;
    }

    if (unlikely(vq->broken))
        return IRQ_HANDLED;

    data_race(vq->event_triggered = true);

    pr_debug("virtqueue callback for %p (%p)\n", vq, vq->vq.callback);

    // 调用驱动注册的回调函数
    if (vq->vq.callback)
        vq->vq.callback(&vq->vq);

    return IRQ_HANDLED;
}
```

### 7.6 操作时序图

```
Guest Driver                          Host Device
    |                                     |
    | ---- virtqueue_add_buf() ---------> |
    |       (填充描述符,更新avail)          |
    |                                     |
    | ---- virtqueue_kick() ------------> |
    |       (发送通知)                     |
    |                                     |
    |         [共享内存操作]                |
    |                                     |
    | <--- vring_interrupt() -------------
    |       (设备使用完缓冲区)              |
    |                                     |
    | ---- virtqueue_get_buf() ---------> |
    |       (获取已用缓冲区)                |
    |                                     |
```

---

## 8. 源码位置索引

### 8.1 核心文件

| 文件 | 描述 |
|------|------|
| `/drivers/virtio/virtio.c` | Virtio核心框架 |
| `/drivers/virtio/virtio_ring.c` | Virtqueue Ring实现 |
| `/include/linux/virtio.h` | Virtio核心数据结构 |
| `/include/linux/virtio_config.h` | 配置操作接口 |
| `/include/linux/virtio_ring.h` | Ring层接口 |
| `/include/uapi/linux/virtio_config.h` | 用户态配置定义 |
| `/include/uapi/linux/virtio_ring.h` | 用户态Ring定义 |
| `/include/uapi/linux/virtio_ids.h` | Virtio设备ID |

### 8.2 传输实现

| 文件 | 描述 |
|------|------|
| `/drivers/virtio/virtio_pci_common.c` | PCI传输公共代码 |
| `/drivers/virtio/virtio_pci_modern.c` | 现代PCI传输 |
| `/drivers/virtio/virtio_pci_legacy.c` | 遗留PCI传输 |
| `/drivers/virtio/virtio_mmio.c` | MMIO传输 |
| `/drivers/virtio/virtio_vdpa.c` | vDPA传输 |

### 8.3 关键函数索引

| 函数 | 位置 | 描述 |
|------|------|------|
| `register_virtio_driver()` | virtio.c:449 | 注册virtio驱动 |
| `register_virtio_device()` | virtio.c:517 | 注册virtio设备 |
| `virtio_dev_probe()` | virtio.c:270 | 设备探测 |
| `virtio_add_status()` | virtio.c:196 | 添加设备状态 |
| `vring_create_virtqueue()` | virtio_ring.c:3260 | 创建virtqueue |
| `virtqueue_add_split()` | virtio_ring.c:599 | 添加缓冲区(Split) |
| `virtqueue_add_packed()` | virtio_ring.c:1615 | 添加缓冲区(Packed) |
| `virtqueue_get_buf_ctx_split()` | virtio_ring.c:917 | 获取缓冲区(Split) |
| `virtqueue_get_buf_ctx_packed()` | virtio_ring.c:2161 | 获取缓冲区(Packed) |
| `vring_interrupt()` | virtio_ring.c:3225 | 中断处理 |

### 8.4 Virtio 设备ID

**文件**: `/include/uapi/linux/virtio_ids.h`

| ID | 设备类型 |
|----|---------|
| 1 | virtio-net |
| 2 | virtio-block |
| 3 | virtio-console |
| 4 | virtio-rng |
| 5 | virtio-balloon |
| 8 | virtio-scsi |
| 16 | virtio-gpu |
| 19 | virtio-vsock |
| 20 | virtio-crypto |
| 24 | virtio-mem |
| 26 | virtio-fs |

---

## 附录 A: vring_need_event 逻辑

**文件**: `/include/uapi/linux/virtio_ring.h` (第 219-227 行)

```c
static inline int vring_need_event(__u16 event_idx, __u16 new_idx, __u16 old)
{
    /*
     * 判断当索引从old增加到new_idx时,是否应该触发事件
     * event_idx: 其他 side 期望收到通知的索引
     * new_idx: 新索引
     * old: 旧索引
     */
    return (__u16)(new_idx - event_idx - 1) < (__u16)(new_idx - old);
}
```

---

## 附录 B: 内存屏障操作

**文件**: `/include/linux/virtio_ring.h` (第 26-48 行)

```c
// 多路复用内存屏障 - 根据weak_barriers选择
static inline void virtio_mb(bool weak_barriers)
{
    if (weak_barriers)
        virt_mb();    // 虚拟化友好的内存屏障
    else
        mb();         // 物理内存屏障
}

// 读屏障
static inline void virtio_rmb(bool weak_barriers)
{
    if (weak_barriers)
        virt_rmb();
    else
        dma_rmb();
}

// 写屏障
static inline void virtio_wmb(bool weak_barriers)
{
    if (weak_barriers)
        virt_wmb();
    else
        dma_wmb();
}
```

---

*文档生成时间: 2026-04-26*
*基于 Linux 内核源码分析*
