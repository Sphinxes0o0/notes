# Linux 内核 Virtio Ring 实现深入分析

## 目录

1. [概述](#1-概述)
2. [Split Virtqueue Ring (传统实现)](#2-split-virtqueue-ring-传统实现)
3. [Packed Ring (现代实现)](#3-packed-ring-现代实现)
4. [关键算法详解](#4-关键算法详解)
5. [中断与通知机制](#5-中断与通知机制)
6. [DMA 和内存屏障](#6-dma-和内存屏障)
7. [数据结构关系图](#7-数据结构关系图)
8. [总结与对比](#8-总结与对比)

---

## 1. 概述

Virtio Ring 是 Virtio 虚拟化框架的核心组件,负责在 guest 和 host 之间高效传输数据。本文基于 Linux 内核源码 `/Users/sphinx/github/linux/drivers/virtio/virtio_ring.c` 进行深入分析。

### 1.1 源码位置

| 文件 | 说明 |
|------|------|
| `/Users/sphinx/github/linux/drivers/virtio/virtio_ring.c` | 主要实现 (约 3600 行) |
| `/Users/sphinx/github/linux/include/linux/virtio_ring.h` | 内核内部接口 |
| `/Users/sphinx/github/linux/include/uapi/linux/virtio_ring.h` | 用户空间 API 结构定义 |

### 1.2 Virtio Ring 类型

```c
enum vq_layout {
    VQ_LAYOUT_SPLIT = 0,        // Split Ring
    VQ_LAYOUT_PACKED,           // Packed Ring
    VQ_LAYOUT_SPLIT_IN_ORDER,   // Split Ring (按顺序)
    VQ_LAYOUT_PACKED_IN_ORDER,  // Packed Ring (按顺序)
};
```

### 1.3 核心数据结构

```c
// drivers/virtio/virtio_ring.c:192
struct vring_virtqueue {
    struct virtqueue vq;
    bool use_map_api;           // 是否使用 DMA API
    bool weak_barriers;         // 是否使用弱屏障
    bool broken;                // 队列是否损坏
    bool indirect;              // 支持间接描述符
    bool event;                 // 支持事件索引
    enum vq_layout layout;      // 环类型
    unsigned int free_head;      // 空闲描述符头
    // ...
    union {
        struct vring_virtqueue_split split;
        struct vring_virtqueue_packed packed;
    };
    bool (*notify)(struct virtqueue *vq);
    union virtio_map map;
};
```

---

## 2. Split Virtqueue Ring (传统实现)

### 2.1 核心数据结构

#### 2.1.1 struct vring_desc (描述符)

定义于 `include/uapi/linux/virtio_ring.h:104`:

```c
struct vring_desc {
    __virtio64 addr;      // 缓冲区地址 (guest 物理地址)
    __virtio32 len;       // 缓冲区长度
    __virtio16 flags;     // 描述符标志
    __virtio16 next;      // 链中下一个描述符索引
};
// 长度: 16 字节, 16 字节对齐
```

**标志位** (定义于 `include/uapi/linux/virtio_ring.h:37-42`):

| 标志 | 值 | 说明 |
|------|-----|------|
| `VRING_DESC_F_NEXT` | 1 | 缓冲区通过 next 字段继续 |
| `VRING_DESC_F_WRITE` | 2 | 缓冲区是只写的 (否则只读) |
| `VRING_DESC_F_INDIRECT` | 4 | 缓冲区包含描述符列表 |

#### 2.1.2 struct vring_avail (可用环)

```c
// include/uapi/linux/virtio_ring.h:111
struct vring_avail {
    __virtio16 flags;     // 标志 (如 VRING_AVAIL_F_NO_INTERRUPT)
    __virtio16 idx;       // 下一个可用环条目索引
    __virtio16 ring[];    // 可用描述符头数组
};
```

#### 2.1.3 struct vring_used (已用环)

```c
// include/uapi/linux/virtio_ring.h:118-132
struct vring_used_elem {
    __virtio32 id;        // 使用的描述符链起始索引
    __virtio32 len;       // 写入的总长度
};

struct vring_used {
    __virtio16 flags;     // 标志 (如 VRING_USED_F_NO_NOTIFY)
    __virtio16 idx;       // 下一个已用环条目索引
    vring_used_elem_t ring[];
};
```

#### 2.1.4 struct vring (完整环)

```c
// include/uapi/linux/virtio_ring.h:155
struct vring {
    unsigned int num;
    vring_desc_t *desc;       // 描述符数组
    vring_avail_t *avail;     // 可用环
    vring_used_t *used;       // 已用环
};
```

### 2.2 Split Ring 内存布局

```
内存布局 (Virtio 1.0 前传统布局):

struct vring {
    struct vring_desc desc[num];     // 描述符表

    struct vring_avail avail;        // 可用环
        - flags
        - idx
        - ring[num]                   // 可用描述符索引

    char pad[];                       // 对齐填充

    struct vring_used used;           // 已用环
        - flags
        - idx
        - ring[num]                   // 已用元素
        - avail_event_idx             // 事件索引 (在 used->ring[num] 位置)
};
```

**对齐要求** (定义于 `include/uapi/linux/virtio_ring.h:86-91`):

| 元素 | 对齐大小 |
|------|----------|
| VRING_DESC_ALIGN_SIZE | 16 字节 |
| VRING_AVAIL_ALIGN_SIZE | 2 字节 |
| VRING_USED_ALIGN_SIZE | 4 字节 |

### 2.3 描述符链机制

Split Ring 使用描述符链来描述分散的缓冲区。一个链由多个描述符组成,每个描述符包含:

1. `addr`: 缓冲区物理地址
2. `len`: 缓冲区长度
3. `flags`: 标志 (F_NEXT, F_WRITE, F_INDIRECT)
4. `next`: 链中下一个描述符的索引

**示例** - 散列表描述符链:

```
desc[0]: {addr=0x1000, len=100, flags=NEXT, next=1}
desc[1]: {addr=0x2000, len=200, flags=NEXT, next=2}
desc[2]: {addr=0x3000, len=300, flags=WRITE, next=0}
```

### 2.4 Split Ring 内部状态结构

```c
// drivers/virtio/virtio_ring.c:77
struct vring_desc_state_split {
    void *data;               // 回调数据
    struct vring_desc *indir_desc;  // 间接描述符表
    u32 total_in_len;         // 总输入长度
};

// drivers/virtio/virtio_ring.c:99
struct vring_desc_extra {
    dma_addr_t addr;          // DMA 地址
    u32 len;                  // 长度
    u16 flags;                // 标志
    u16 next;                 // 下一个描述符索引
};

// drivers/virtio/virtio_ring.c:106
struct vring_virtqueue_split {
    struct vring vring;                   // 实际内存布局
    u16 avail_flags_shadow;               // avail->flags 的缓存值
    u16 avail_idx_shadow;                 // avail->idx 的缓存值
    struct vring_desc_state_split *desc_state;  // 每描述符状态
    struct vring_desc_extra *desc_extra;         // 每描述符额外信息
    dma_addr_t queue_dma_addr;            // DMA 地址
    size_t queue_size_in_bytes;           // 队列大小
    u32 vring_align;                      // 对齐要求
    bool may_reduce_num;                  // 是否可减少描述符数量
};
```

### 2.5 avail_event / used_event 通知机制

Split Ring 使用两个事件索引来协调通知:

1. **avail_event** (`vring_used_event`): Guest 写入,通知 Host 它期望中断的 avail 索引
2. **used_event**: Host 写入,通知 Guest 它期望中断的 used 索引

```c
// include/uapi/linux/virtio_ring.h:193-194
#define vring_used_event(vr) ((vr)->avail->ring[(vr)->num])
#define vring_avail_event(vr) (*(__virtio16 *)&(vr)->used->ring[(vr)->num])
```

**vring_need_event 函数** (`include/uapi/linux/virtio_ring.h:219`):

```c
static inline int vring_need_event(__u16 event_idx, __u16 new_idx, __u16 old)
{
    // 判断是否需要触发事件
    return (__u16)(new_idx - event_idx - 1) < (__u16)(new_idx - old);
}
```

---

## 3. Packed Ring (现代实现)

### 3.1 Packed Ring vs Split Ring 区别

| 特性 | Split Ring | Packed Ring |
|------|------------|-------------|
| 描述符数量 | 3 个独立数组 | 单个描述符数组 |
| 内存布局 | 分散在 3 个区域 | 紧凑的单一区域 |
| 描述符大小 | 16 字节 | 16 字节 |
| 缓冲环 | avail 和 used 分开 | 使用 flags 表示状态 |
| Wrap Counter | 无 | 有 (15 位) |
| 缓存效率 | 较低 | 较高 |
| 复杂度 | 较低 | 较高 |

### 3.2 核心数据结构

#### 3.2.1 struct vring_packed_desc (压缩描述符)

定义于 `include/uapi/linux/virtio_ring.h:236`:

```c
struct vring_packed_desc {
    __le64 addr;      // 缓冲区地址
    __le32 len;       // 缓冲区长度
    __le16 id;        // 缓冲区 ID
    __le16 flags;     // 标志
};
// 长度: 16 字节
```

**标志位** (定义于 `include/uapi/linux/virtio_ring.h:45-49`):

| 标志 | 位 | 说明 |
|------|-----|------|
| `VRING_PACKED_DESC_F_AVAIL` | 7 | 可用标志位 |
| `VRING_PACKED_DESC_F_USED` | 15 | 已用标志位 |

#### 3.2.2 struct vring_packed_desc_event (事件结构)

```c
// include/uapi/linux/virtio_ring.h:229
struct vring_packed_desc_event {
    __le16 off_wrap;  // 描述符环改变事件偏移/换行计数器
    __le16 flags;     // 事件标志
};
```

**事件标志** (定义于 `include/uapi/linux/virtio_ring.h:60-69`):

| 标志 | 值 | 说明 |
|------|-----|------|
| `VRING_PACKED_EVENT_FLAG_ENABLE` | 0x0 | 使能事件 |
| `VRING_PACKED_EVENT_FLAG_DISABLE` | 0x1 | 禁用事件 |
| `VRING_PACKED_EVENT_FLAG_DESC` | 0x2 | 针对特定描述符的事件 |

### 3.3 Packed Ring 内存布局

```
Packed Ring 内存布局:

+------------------+
| Descriptor Ring  |  num × struct vring_packed_desc (16 字节 each)
| (desc[])         |
+------------------+
| Driver Event     |  struct vring_packed_desc_event
| (driver)         |
+------------------+
| Device Event     |  struct vring_packed_desc_event
| (device)         |
+------------------+
```

### 3.4 包装描述符算法 (Wrap Counter)

Packed Ring 使用 **wrap counter** 来区分可用和已用描述符:

```c
// drivers/virtio/virtio_ring.c:1428-1431
static bool packed_used_wrap_counter(u16 last_used_idx)
{
    return !!(last_used_idx & (1 << VRING_PACKED_EVENT_F_WRAP_CTR));
}

// VRING_PACKED_EVENT_F_WRAP_CTR = 15
```

**描述符可用性判断** (`drivers/virtio/virtio_ring.c:2036-2047`):

```c
static inline bool is_used_desc_packed(const struct vring_virtqueue *vq,
                                       u16 idx, bool used_wrap_counter)
{
    bool avail, used;
    u16 flags;

    flags = le16_to_cpu(vq->packed.vring.desc[idx].flags);
    avail = !!(flags & (1 << VRING_PACKED_DESC_F_AVAIL));
    used = !!(flags & (1 << VRING_PACKED_DESC_F_USED));

    // 描述符被认为是"已使用"当且仅当 avail == used == used_wrap_counter
    return avail == used && used == used_wrap_counter;
}
```

### 3.5 Packed Ring 内部状态结构

```c
// drivers/virtio/virtio_ring.c:87
struct vring_desc_state_packed {
    void *data;                   // 回调数据
    struct vring_packed_desc *indir_desc;  // 间接描述符
    u16 num;                      // 描述符列表长度
    u16 last;                     // 列表中最后一个描述符状态
    u32 total_in_len;             // 总输入长度
};

// drivers/virtio/virtio_ring.c:135
struct vring_virtqueue_packed {
    struct {
        unsigned int num;
        struct vring_packed_desc *desc;
        struct vring_packed_desc_event *driver;
        struct vring_packed_desc_event *device;
    } vring;

    bool avail_wrap_counter;      // 可用换行计数器
    u16 avail_used_flags;         // 可用已用标志
    u16 next_avail_idx;          // 下一个可用描述符索引
    u16 event_flags_shadow;       // 事件标志缓存
    struct vring_desc_state_packed *desc_state;
    struct vring_desc_extra *desc_extra;
    dma_addr_t ring_dma_addr;
    dma_addr_t driver_event_dma_addr;
    dma_addr_t device_event_dma_addr;
    size_t ring_size_in_bytes;
    size_t event_size_in_bytes;
};
```

---

## 4. 关键算法详解

### 4.1 virtqueue_add_split() - 添加缓冲区 (Split)

位置: `drivers/virtio/virtio_ring.c:599-792`

**函数签名**:

```c
static inline int virtqueue_add_split(struct vring_virtqueue *vq,
                                      struct scatterlist *sgs[],
                                      unsigned int total_sg,
                                      unsigned int out_sgs,
                                      unsigned int in_sgs,
                                      void *data,
                                      void *ctx,
                                      bool premapped,
                                      gfp_t gfp,
                                      unsigned long attr)
```

**算法流程**:

```
1. START_USE(vq) - 开始使用 virtqueue,检查重入

2. 检查错误条件:
   - data != NULL
   - ctx 为空或无 indirect 支持
   - vq 未损坏
   - total_sg > 0

3. 获取空闲描述符头:
   head = vq->free_head

4. 决定是否使用间接描述符:
   if (virtqueue_use_indirect(vq, total_sg))
       desc = alloc_indirect_split(vq, total_sg, gfp)
   else
       desc = vq->split.vring.desc

5. 遍历所有 scatter-gather 列表,填充描述符:
   for (每个 scatterlist sg) {
       - 映射 DMA 地址: vring_map_one_sg()
       - 设置标志: NEXT(如果不是最后一个), WRITE(如果是输入缓冲区)
       - 填充描述符: virtqueue_add_desc_split()
   }

6. 如果使用间接描述符:
   - 映射间接表 DMA
   - 在头描述符中设置 INDIRECT 标志

7. 更新空闲描述符计数:
   vq->vq.num_free -= descs_used

8. 更新 free_head:
   if (virtqueue_is_in_order(vq))
       vq->free_head += descs_used
   else if (indirect)
       vq->free_head = vq->split.desc_extra[head].next
   else
       vq->free_head = i

9. 保存状态:
   vq->split.desc_state[head].data = data
   vq->split.desc_state[head].indir_desc = ctx 或 desc

10. 添加到可用环:
    avail = vq->split.avail_idx_shadow & (vq->split.vring.num - 1)
    vq->split.vring.avail->ring[avail] = head

11. 内存屏障 + 更新索引:
    virtio_wmb(vq->weak_barriers)
    vq->split.avail_idx_shadow++
    vq->split.vring.avail->idx = avail_idx_shadow
    vq->num_added++

12. 如果添加太多,自动 kick:
    if (vq->num_added == (1 << 16) - 1)
        virtqueue_kick(&vq->vq)
```

### 4.2 virtqueue_add_packed() - 添加缓冲区 (Packed)

位置: `drivers/virtio/virtio_ring.c:1615-1771`

**核心差异 (与 Split 对比)**:

```c
// 1. 使用 avail_used_flags 而非独立的 avail 和 used
head_flags = flags;
desc[i].flags = flags;

// 2. Wrap counter 处理
if (++i >= vq->packed.vring.num) {
    i = 0;
    vq->packed.avail_used_flags ^=
        1 << VRING_PACKED_DESC_F_AVAIL |
        1 << VRING_PACKED_DESC_F_USED;
}

// 3. 换行处理
if (i <= head)
    vq->packed.avail_wrap_counter ^= 1;

// 4. 内存屏障后才设置头描述符标志
virtio_wmb(vq->weak_barriers)
vq->packed.vring.desc[head].flags = head_flags;
```

### 4.3 virtqueue_get_buf_ctx() - 获取完成缓冲区

#### Split 版本 (`drivers/virtio/virtio_ring.c:917-972`):

```c
static void *virtqueue_get_buf_ctx_split(struct vring_virtqueue *vq,
                                         unsigned int *len,
                                         void **ctx)
{
    // 1. 检查是否有已用缓冲区
    if (!more_used_split(vq))
        return NULL;

    // 2. 读取内存屏障
    virtio_rmb(vq->weak_barriers);

    // 3. 获取已用环条目
    last_used = vq->last_used_idx & (vq->split.vring.num - 1);
    i = vq->split.vring.used->ring[last_used].id;
    *len = vq->split.vring.used->ring[last_used].len;

    // 4. 验证描述符
    if (i >= vq->split.vring.num || !vq->split.desc_state[i].data)
        return NULL;

    // 5. 保存返回值
    ret = vq->split.desc_state[i].data;

    // 6. 分离缓冲区
    detach_buf_split(vq, i, ctx);

    // 7. 更新 last_used_idx
    vq->last_used_idx++;

    // 8. 更新事件索引
    if (!(vq->split.avail_flags_shadow & VRING_AVAIL_F_NO_INTERRUPT))
        virtio_store_mb(vq->weak_barriers,
                        &vring_used_event(&vq->split.vring),
                        cpu_to_virtio16(vq->vq.vdev, vq->last_used_idx));

    return ret;
}
```

#### Packed 版本 (`drivers/virtio/virtio_ring.c:2161-2211`):

```c
static void *virtqueue_get_buf_ctx_packed(struct vring_virtqueue *vq,
                                          unsigned int *len,
                                          void **ctx)
{
    // 1. 检查是否有已用缓冲区
    if (!more_used_packed(vq))
        return NULL;

    // 2. 读取内存屏障
    virtio_rmb(vq->weak_barriers);

    // 3. 解析 last_used_idx
    last_used_idx = READ_ONCE(vq->last_used_idx);
    used_wrap_counter = packed_used_wrap_counter(last_used_idx);
    last_used = packed_last_used(last_used_idx);

    // 4. 获取描述符
    id = le16_to_cpu(vq->packed.vring.desc[last_used].id);
    *len = le32_to_cpu(vq->packed.vring.desc[last_used].len);

    // 5. 验证
    if (id >= num || !vq->packed.desc_state[id].data)
        return NULL;

    // 6. 保存返回值
    ret = vq->packed.desc_state[id].data;

    // 7. 分离缓冲区
    detach_buf_packed(vq, id, ctx);

    // 8. 更新 last_used_idx
    update_last_used_idx_packed(vq, id, last_used, used_wrap_counter);

    return ret;
}
```

### 4.4 virtqueue_kick() - 通知前端

位置: `drivers/virtio/virtio_ring.c:3002-3062`

**两阶段 kick 机制**:

```c
// 第一阶段: virtqueue_kick_prepare
bool virtqueue_kick_prepare(struct virtqueue *_vq)
{
    struct vring_virtqueue *vq = to_vvq(_vq);
    return VIRTQUEUE_CALL(vq, kick_prepare);
}

// virtqueue_kick_prepare_split (drivers/virtio/virtio_ring.c:794-822)
static bool virtqueue_kick_prepare_split(struct vring_virtqueue *vq)
{
    u16 new, old;
    bool needs_kick;

    virtio_mb(vq->weak_barriers);

    old = vq->split.avail_idx_shadow - vq->num_added;
    new = vq->split.avail_idx_shadow;
    vq->num_added = 0;

    if (vq->event) {
        // 使用事件索引,调用 vring_need_event
        needs_kick = vring_need_event(
            virtio16_to_cpu(vq->vq.vdev, vring_avail_event(&vq->split.vring)),
            new, old);
    } else {
        // 检查 NO_NOTIFY 标志
        needs_kick = !(vq->split.vring.used->flags &
            cpu_to_virtio16(vq->vq.vdev, VRING_USED_F_NO_NOTIFY));
    }
    return needs_kick;
}

// 第二阶段: virtqueue_notify
bool virtqueue_notify(struct virtqueue *_vq)
{
    struct vring_virtqueue *vq = to_vvq(_vq);

    if (unlikely(vq->broken))
        return false;

    if (!vq->notify(_vq)) {
        vq->broken = true;
        return false;
    }
    return true;
}

// 完整 kick
bool virtqueue_kick(struct virtqueue *vq)
{
    if (virtqueue_kick_prepare(vq))
        return virtqueue_notify(vq);
    return true;
}
```

### 4.5 virtqueue_detach_unused_buf() - 分离未用缓冲区

#### Split 版本 (`drivers/virtio/virtio_ring.c:1125-1150`):

```c
static void *virtqueue_detach_unused_buf_split(struct vring_virtqueue *vq)
{
    unsigned int i;
    void *buf;

    for (i = 0; i < vq->split.vring.num; i++) {
        if (!vq->split.desc_state[i].data)
            continue;

        buf = vq->split.desc_state[i].data;

        if (virtqueue_is_in_order(vq))
            detach_buf_split_in_order(vq, i, NULL);
        else
            detach_buf_split(vq, i, NULL);

        vq->split.avail_idx_shadow--;
        vq->split.vring.avail->idx = cpu_to_virtio16(vq->vq.vdev,
                vq->split.avail_idx_shadow);
        return buf;
    }
    BUG_ON(vq->vq.num_free != vq->split.vring.num);
    return NULL;
}
```

#### Packed 版本 (`drivers/virtio/virtio_ring.c:2321-2345`):

```c
static void *virtqueue_detach_unused_buf_packed(struct vring_virtqueue *vq)
{
    unsigned int i;
    void *buf;

    for (i = 0; i < vq->packed.vring.num; i++) {
        if (!vq->packed.desc_state[i].data)
            continue;

        buf = vq->packed.desc_state[i].data;

        if (virtqueue_is_in_order(vq))
            detach_buf_packed_in_order(vq, i, NULL);
        else
            detach_buf_packed(vq, i, NULL);
        return buf;
    }
    BUG_ON(vq->vq.num_free != vq->packed.vring.num);
    return NULL;
}
```

---

## 5. 中断与通知机制

### 5.1 vring_interrupt() - 中断处理

位置: `drivers/virtio/virtio_ring.c:3229-3258`

```c
irqreturn_t vring_interrupt(int irq, void *_vq)
{
    struct vring_virtqueue *vq = to_vvq(_vq);

    // 1. 检查是否有更多已用缓冲区
    if (!more_used(vq)) {
        pr_debug("virtqueue interrupt with no work for %p\n", vq);
        return IRQ_NONE;
    }

    // 2. 检查队列是否损坏
    if (unlikely(vq->broken)) {
#ifdef CONFIG_VIRTIO_HARDEN_NOTIFICATION
        return IRQ_NONE;
#else
        return IRQ_HANDLED;
#endif
    }

    // 3. 设置事件触发标志
    if (vq->event)
        vq->event_triggered = true;

    // 4. 调用回调函数
    pr_debug("virtqueue callback for %p (%p)\n", vq, vq->vq.callback);
    if (vq->vq.callback)
        vq->vq.callback(&vq->vq);

    return IRQ_HANDLED;
}
```

### 5.2 通知机制流程

```
Guest 添加缓冲区到 virtqueue:
1. virtqueue_add_*()
2. 更新 avail ring (Split) 或 desc flags (Packed)
3. virtio_wmb() - 内存屏障
4. 更新 avail->idx (Split) 或 desc[head].flags (Packed)
5. virtqueue_kick()
6. virtqueue_kick_prepare_*() - 检查是否需要通知
7. virtqueue_notify() - 调用 vq->notify()

Host 处理并返回:
1. 读取 descriptor
2. 处理 I/O
3. 更新 used ring (Split) 或 desc flags (Packed)
4. 发送中断
5. Guest vring_interrupt() 被调用
6. virtqueue_get_buf_*() 获取结果
```

### 5.3 virtio_finalize_features() - 特征最终化

位置: `drivers/virtio/virtio_ring.c:3505-3533`

```c
void vring_transport_features(struct virtio_device *vdev)
{
    unsigned int i;

    for (i = VIRTIO_TRANSPORT_F_START; i < VIRTIO_TRANSPORT_F_END; i++) {
        switch (i) {
        case VIRTIO_RING_F_INDIRECT_DESC:
            // 支持间接描述符
            break;
        case VIRTIO_RING_F_EVENT_IDX:
            // 支持事件索引
            break;
        case VIRTIO_F_VERSION_1:
            // Virtio 1.0
            break;
        case VIRTIO_F_ACCESS_PLATFORM:
            // 平台访问
            break;
        case VIRTIO_F_RING_PACKED:
            // Packed Ring
            break;
        case VIRTIO_F_ORDER_PLATFORM:
            // 平台排序
            break;
        case VIRTIO_F_NOTIFICATION_DATA:
            // 通知数据
            break;
        case VIRTIO_F_IN_ORDER:
            // 按顺序
            break;
        default:
            // 不支持的特征位被清除
            __virtio_clear_bit(vdev, i);
        }
    }
}
```

---

## 6. DMA 和内存屏障

### 6.1 内存屏障 (Memory Barrier)

定义于 `include/linux/virtio_ring.h:26-58`:

```c
// 通用内存屏障
static inline void virtio_mb(bool weak_barriers)
{
    if (weak_barriers)
        virt_mb();
    else
        mb();
}

// 读取屏障
static inline void virtio_rmb(bool weak_barriers)
{
    if (weak_barriers)
        virt_rmb();
    else
        dma_rmb();
}

// 写入屏障
static inline void virtio_wmb(bool weak_barriers)
{
    if (weak_barriers)
        virt_wmb();
    else
        dma_wmb();
}

// 存储-加载屏障
#define virtio_store_mb(weak_barriers, p, v) \
do { \
    if (weak_barriers) { \
        virt_store_mb(*p, v); \
    } else { \
        WRITE_ONCE(*p, v); \
        mb(); \
    } \
} while (0)
```

**屏障使用场景**:

| 函数 | 使用屏障 | 目的 |
|------|----------|------|
| `virtqueue_add_*()` | `virtio_wmb()` | 确保描述符在更新 avail->idx 之前可见 |
| `virtqueue_get_buf_*()` | `virtio_rmb()` | 确保在读取缓冲区数据前看到 used->idx 更新 |
| `virtqueue_kick_prepare_*()` | `virtio_mb()` | 确保暴露可用数组条目后再检查事件 |

### 6.2 DMA 映射

#### vring_map_one_sg() - 映射单个 scatterlist

位置: `drivers/virtio/virtio_ring.c:446-482`:

```c
static int vring_map_one_sg(const struct vring_virtqueue *vq,
                            struct scatterlist *sg,
                            enum dma_data_direction direction,
                            dma_addr_t *addr, u32 *len,
                            bool premapped, unsigned long attr)
{
    if (premapped) {
        // 预映射: 直接使用 sg 中的 DMA 地址
        *addr = sg_dma_address(sg);
        *len = sg_dma_len(sg);
        return 0;
    }

    *len = sg->length;

    if (!vq->use_map_api) {
        // 不使用 DMA API: 使用物理地址
        kmsan_handle_dma(sg_phys(sg), sg->length, direction);
        *addr = (dma_addr_t)sg_phys(sg);
        return 0;
    }

    // 使用 DMA API 映射
    *addr = virtqueue_map_page_attrs(&vq->vq, sg_page(sg),
                                     sg->offset, sg->length,
                                     direction, attr);
    return vring_mapping_error(vq, *addr) ? -ENOMEM : 0;
}
```

#### vring_unmap_one_split() - 取消映射 (Split)

位置: `drivers/virtio/virtio_ring.c:520-542`:

```c
static unsigned int vring_unmap_one_split(const struct vring_virtqueue *vq,
                                          struct vring_desc_extra *extra)
{
    u16 flags;

    flags = extra->flags;

    // 间接描述符或不需 unmap
    if (flags & VRING_DESC_F_INDIRECT) {
        if (!vq->use_map_api)
            goto out;
    } else if (!vring_need_unmap_buffer(vq, extra))
        goto out;

    // 执行 unmap
    virtqueue_unmap_page_attrs(&vq->vq,
                              extra->addr, extra->len,
                              (flags & VRING_DESC_F_WRITE) ?
                                  DMA_FROM_DEVICE : DMA_TO_DEVICE,
                              0);
out:
    return extra->next;
}
```

#### vring_unmap_extra_packed() - 取消映射 (Packed)

位置: `drivers/virtio/virtio_ring.c:1438-1456`:

```c
static void vring_unmap_extra_packed(const struct vring_virtqueue *vq,
                                     const struct vring_desc_extra *extra)
{
    u16 flags;

    flags = extra->flags;

    if (flags & VRING_DESC_F_INDIRECT) {
        if (!vq->use_map_api)
            return;
    } else if (!vring_need_unmap_buffer(vq, extra))
        return;

    virtqueue_unmap_page_attrs(&vq->vq,
                              extra->addr, extra->len,
                              (flags & VRING_DESC_F_WRITE) ?
                                  DMA_FROM_DEVICE : DMA_TO_DEVICE,
                              0);
}
```

### 6.3 DMA API 选择

位置: `drivers/virtio/virtio_ring.c:333-351`:

```c
static bool vring_use_map_api(const struct virtio_device *vdev)
{
    // 如果没有 DMA quirk,使用 DMA API
    if (!virtio_has_dma_quirk(vdev))
        return true;

    // Xen domain 特殊处理
    if (xen_domain())
        return true;

    return false;
}
```

### 6.4 缓存一致性

**直接映射模式** (`vring_alloc_queue`):

```c
static void *vring_alloc_queue(struct virtio_device *vdev, size_t size,
                               dma_addr_t *map_handle, gfp_t flag,
                               union virtio_map map)
{
    if (vring_use_map_api(vdev)) {
        // 使用 DMA API 分配一致映射
        return virtqueue_map_alloc_coherent(vdev, map, size,
                                            map_handle, flag);
    } else {
        // 使用页分配器
        void *queue = alloc_pages_exact(PAGE_ALIGN(size), flag);
        if (queue) {
            phys_addr_t phys_addr = virt_to_phys(queue);
            *map_handle = (dma_addr_t)phys_addr;
        }
        return queue;
    }
}
```

---

## 7. 数据结构关系图

### 7.1 Split Ring 整体结构

```
Split Ring 数据结构关系:

                    vring_virtqueue
                           |
           +---------------+---------------+
           |                               |
    struct virtqueue                  vring_virtqueue_split
           |                               |
    - callback                       - vring vring
    - vdev                                |   +--- desc (vring_desc[])
    - name                                |   +--- avail (vring_avail)
    - index                               |   +--- used (vring_used)
           |                               |
           |                    - avail_flags_shadow
           |                    - avail_idx_shadow
           |                    - desc_state[]
           |                    - desc_extra[]
           |
    - use_map_api
    - weak_barriers
    - broken
    - indirect
    - event
    - layout
    - free_head
    - num_added
    - last_used_idx
    - notify()
    - map
```

### 7.2 Packed Ring 整体结构

```
Packed Ring 数据结构关系:

                    vring_virtqueue
                           |
           +---------------+---------------+
           |                               |
    struct virtqueue                  vring_virtqueue_packed
           |                               |
    - callback                       - vring
           |                                |   +--- num
    - vdev                                |   +--- desc (vring_packed_desc[])
           |                                |   +--- driver (event)
    - name                                |   +--- device (event)
           |                               |
    - index                        - avail_wrap_counter
           |                        - avail_used_flags
           |                        - next_avail_idx
           |                        - event_flags_shadow
           |                        - desc_state[]
           |                        - desc_extra[]
           |
    - use_map_api
    - weak_barriers
    - broken
    - indirect
    - event
    - layout
    - free_head
    - num_added
    - last_used_idx
    - notify()
    - map
```

### 7.3 描述符状态管理

```
Split Ring 描述符状态:

desc_state[] 和 desc_extra[] 与 desc[] 一一对应:

desc[i] <---> desc_state[i] <---> desc_extra[i]
   |              |                  |
   v              v                  v
描述符         用户数据           DMA/标志信息
   |              |                  |
   +---- next ----+---- next -------+
```

### 7.4 添加缓冲区到 Split Ring 流程

```
添加缓冲区 (Split):

1. virtqueue_add_split()
   |
   +-> 检查 num_free >= descs_used
   |
   +-> alloc_indirect_split() 或使用直接描述符
   |
   +-> 填充描述符表:
   |     desc[head] --> desc[head+1] --> ... --> desc[head+n-1]
   |
   +-> 更新 free_head
   |
   +-> avail->ring[avail_idx % num] = head
   |
   +-> virtio_wmb()
   |
   +-> avail->idx++
```

### 7.5 添加缓冲区到 Packed Ring 流程

```
添加缓冲区 (Packed):

1. virtqueue_add_packed()
   |
   +-> 检查 num_free >= descs_used
   |
   +-> 设置 desc[i]:
   |     desc[i].addr = buffer_addr
   |     desc[i].len = buffer_len
   |     desc[i].id = head (buffer id)
   |     desc[i].flags = avail_used_flags | NEXT | WRITE
   |
   +-> 更新 avail_used_flags (翻转 AVAIL/USED 位)
   |
   +-> i++ (循环)
   |
   +-> 如果 i >= num, 重置 i=0 并翻转 wrap counter
   |
   +-> 更新 wrap counter
   |
   +-> 更新 next_avail_idx = i
   |
   +-> virtio_wmb()
   |
   +-> desc[head].flags = head_flags (使能)
```

---

## 8. 总结与对比

### 8.1 Split vs Packed 特性对比

| 特性 | Split Ring | Packed Ring |
|------|------------|-------------|
| **引入版本** | Virtio 0.9 (2009) | Virtio 1.0 (2015) |
| **内存布局** | 3 个独立区域 | 单一紧凑区域 |
| **缓存效率** | 较低 (需要访问 3 个缓存行) | 较高 (单一缓存行) |
| **复杂度** | 简单 | 复杂 (wrap counter) |
| **硬件需求** | 较低 | 需要较强内存序支持 |
| **间接描述符** | 支持 | 支持 |
| **事件索引** | 支持 | 支持 |
| **IN_ORDER** | 支持 | 支持 |

### 8.2 关键设计决策

1. **描述符状态分离**: `desc_state[]` 和 `desc_extra[]` 与实际描述符数组分离,简化内存管理

2. **avail_idx_shadow**: 缓存 avail->idx 避免每次都读取 MMIO

3. **weak_barriers**: 根据平台特性选择合适的内存屏障

4. **两阶段 kick**: `kick_prepare()` 和 `notify()` 分离,允许批处理通知

5. **event_triggered**: 优化减少不必要的中断禁用

### 8.3 代码组织

```c
// 操作函数指针表
static const struct virtqueue_ops split_ops = {
    .add = virtqueue_add_split,
    .get = virtqueue_get_buf_ctx_split,
    .kick_prepare = virtqueue_kick_prepare_split,
    .disable_cb = virtqueue_disable_cb_split,
    .enable_cb_delayed = virtqueue_enable_cb_delayed_split,
    .enable_cb_prepare = virtqueue_enable_cb_prepare_split,
    .poll = virtqueue_poll_split,
    .detach_unused_buf = virtqueue_detach_unused_buf_split,
    .more_used = more_used_split,
    .resize = virtqueue_resize_split,
    .reset = virtqueue_reset_split,
};

// VIRTQUEUE_CALL 宏根据 layout 选择操作集
#define VIRTQUEUE_CALL(vq, op, ...) \
    ({ \
        switch (vq->layout) { \
        case VQ_LAYOUT_SPLIT: \
            ret = split_ops.op(vq, ##__VA_ARGS__); \
            break; \
        case VQ_LAYOUT_PACKED: \
            ret = packed_ops.op(vq, ##__VA_ARGS__); \
            break; \
        ... \
        } \
        ret; \
    })
```

### 8.4 性能优化建议

1. **使用 IN_ORDER**: 如果设备支持,使用按顺序处理模式可减少状态管理开销

2. **预映射缓冲区**: 使用 `virtqueue_add_*_premapped` 减少 DMA 映射开销

3. **批处理**: 累积多个缓冲区后再 kick,减少通知次数

4. **回调优化**: 使用 `virtqueue_enable_cb_delayed` 延迟启用回调,减少中断

---

## 参考代码位置汇总

| 功能 | 文件位置 |
|------|----------|
| Split Ring 添加 | `drivers/virtio/virtio_ring.c:599` |
| Packed Ring 添加 | `drivers/virtio/virtio_ring.c:1615` |
| Split Ring 获取 | `drivers/virtio/virtio_ring.c:917` |
| Packed Ring 获取 | `drivers/virtio/virtio_ring.c:2161` |
| 中断处理 | `drivers/virtio/virtio_ring.c:3229` |
| DMA 映射 | `drivers/virtio/virtio_ring.c:446` |
| 内存屏障 | `include/linux/virtio_ring.h:26` |
| 环创建 (Split) | `drivers/virtio/virtio_ring.c:1357` |
| 环创建 (Packed) | `drivers/virtio/virtio_ring.c:2577` |
| 特征最终化 | `drivers/virtio/virtio_ring.c:3505` |
| 用户空间 API | `include/uapi/linux/virtio_ring.h` |

---

*文档生成日期: 2026-04-26*
*内核版本: Linux (master branch)*
