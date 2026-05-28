# Linux 内核 Block MultiQueue (blk-mq) 子系统分析

## 目录

1. [概述](#概述)
2. [blk-mq 与传统单队列的区别](#blk-mq-与传统单队列的区别)
3. [核心数据结构](#核心数据结构)
4. [blk_mq_ops 驱动操作接口](#blk_mq_ops-驱动操作接口)
5. [硬件队列 (hctx) 管理](#硬件队列-hctx-管理)
6. [标签管理 (tag)](#标签管理-tag)
7. [调度器集成](#调度器集成)
8. [请求提交路径](#请求提交路径)
9. [请求分发 (dispatch) 机制](#请求分发-dispatch-机制)

---

## 概述

Block MultiQueue (blk-mq) 是 Linux 内核块层的多队列实现，旨在支持现代高性能存储设备。传统的单队列块层设计无法有效利用多核 CPU 和支持并行操作的存储设备（如 NVMe SSD）。

**关键文件：**
- `/Users/sphinx/github/linux/block/blk-mq.c` - blk-mq 核心实现
- `/Users/sphinx/github/linux/block/blk-mq-tag.c` - 标签管理
- `/Users/sphinx/github/linux/include/linux/blk-mq.h` - 核心数据结构定义
- `/Users/sphinx/github/linux/block/blk-mq-sched.c` - 调度器接口实现
- `/Users/sphinx/github/linux/block/elevator.h` - 调度器操作接口

---

## blk-mq 与传统单队列的区别

### 传统单队列 (Legacy) 的局限性

```
传统块层架构：
                    应用
                      │
                      ▼
                 请求队列 (单队列)
                      │
           ┌─────────┴─────────┐
           ▼                   ▼
      调度器(单)          磁盘(单)
           │                   │
           └─────────┬─────────┘
                     ▼
                  磁盘驱动
```

问题：
- 所有 CPU 竞争单个请求队列锁
- 无法利用多核并行性
- 磁盘并发能力无法充分发挥

### blk-mq 多队列架构

```
blk-mq 架构：
                    应用
                      │
                      ▼
        ┌──────────────┴──────────────┐
        ▼              ▼              ▼
   软件队列0     软件队列1      软件队列N
   (per-cpu)    (per-cpu)     (per-cpu)
        │              │              │
        └──────────────┼──────────────┘
                       ▼
         ┌─────────────┴─────────────┐
         ▼              ▼              ▼
    硬件队列0      硬件队列1      硬件队列N
    (hctx)        (hctx)        (hctx)
         │              │              │
         └──────────────┼──────────────┘
                        ▼
                   磁盘驱动
```

**关键改进：**
- 每个 CPU 有独立的软件队列 (software queue)
- 支持多个硬件队列 (hardware queue)
- 大幅减少锁竞争
- 支持真正的并行 I/O

---

## 核心数据结构

### 1. struct blk_mq_hw_ctx (硬件队列上下文)

定义位置：`/Users/sphinx/github/linux/include/linux/blk-mq.h` 第 322-463 行

```c
/**
 * struct blk_mq_hw_ctx - State for a hardware queue facing the hardware block device
 */
struct blk_mq_hw_ctx {
    struct {
        spinlock_t      lock;           /* 保护 dispatch 列表 */
        struct list_head dispatch;      /* 已准备好分发的请求 */
        unsigned long   state;          /* BLK_MQ_S_* 状态标志 */
    } ____cacheline_aligned_in_smp;

    struct delayed_work   run_work;      /* 延迟运行工作项 */
    cpumask_var_t       cpumask;       /* 可用 CPU 掩码 */
    int                 next_cpu;       /* 轮转选择的下一个 CPU */
    int                 next_cpu_batch;

    unsigned long       flags;          /* BLK_MQ_F_* 标志 */
    void               *sched_data;     /* 调度器私有数据 */
    struct request_queue *queue;        /* 所属请求队列 */
    struct blk_flush_queue *fq;         /* flush 请求队列 */

    void               *driver_data;    /* 驱动私有数据 */

    struct sbitmap      ctx_map;        /* 软件队列位图 */

    struct blk_mq_ctx  *dispatch_from; /* 无调度器时使用的软件队列 */
    unsigned int        dispatch_busy;  /* EWMA 忙碌状态 */

    unsigned short      type;           /* HCTX_TYPE_* 队列类型 */
    unsigned short      nr_ctx;         /* 软件队列数量 */
    struct blk_mq_ctx **ctxs;           /* 软件队列数组 */

    struct blk_mq_tags *tags;           /* 驱动标签 */
    struct blk_mq_tags *sched_tags;    /* 调度器标签 */

    unsigned int        numa_node;      /* NUMA 节点 */
    unsigned int        queue_num;      /* 硬件队列索引 */

    atomic_t            nr_active;      /* 活跃请求数 */
    struct hlist_node   cpuhp_online;   /* CPU 热插拔在线节点 */
    struct hlist_node   cpuhp_dead;     /* CPU 热插拔离线节点 */
    struct kobject      kobj;           /* sysfs 内核对象 */
};
```

**队列类型 (hctx_type)：**

```c
enum hctx_type {
    HCTX_TYPE_DEFAULT,  /* 默认 I/O */
    HCTX_TYPE_READ,      /* 仅读 I/O */
    HCTX_TYPE_POLL,      /* 轮询 I/O */

    HCTX_MAX_TYPES,
};
```

### 2. struct blk_mq_tags (标签集合)

定义位置：`/Users/sphinx/github/linux/include/linux/blk-mq.h` 第 774-792 行

```c
struct blk_mq_tags {
    unsigned int nr_tags;           /* 总标签数 */
    unsigned int nr_reserved_tags; /* 保留标签数 */
    unsigned int active_queues;     /* 活跃队列计数 */

    struct sbitmap_queue bitmap_tags;   /* 普通请求标签位图 */
    struct sbitmap_queue breserved_tags;/* 保留标签位图 */

    struct request **rqs;           /* 请求指针数组 */
    struct request **static_rqs;    /* 静态请求数组 */
    struct list_head page_list;     /* 页面列表 */

    spinlock_t lock;                /* 保护位图 */
    struct rcu_head rcu_head;       /* RCU 回调 */
};
```

### 3. struct blk_mq_tag_set (标签集管理)

定义位置：`/Users/sphinx/github/linux/include/linux/blk-mq.h` 第 497-557 行

```c
struct blk_mq_tag_set {
    const struct blk_mq_ops  *ops;           /* 驱动操作接口 */
    struct blk_mq_queue_map   map[HCTX_MAX_TYPES]; /* CPU 到硬件队列映射 */
    unsigned int              nr_maps;        /* 映射数量 */
    unsigned int              nr_hw_queues;   /* 硬件队列数 */
    unsigned int              queue_depth;   /* 每队列深度 */
    unsigned int              reserved_tags;  /* 保留标签数 */
    unsigned int              cmd_size;      /* 额外命令大小 */
    int                       numa_node;     /* NUMA 节点 */
    unsigned int              timeout;       /* 请求超时 */
    unsigned int              flags;         /* BLK_MQ_F_* 标志 */

    void                     *driver_data;   /* 驱动私有数据 */
    struct blk_mq_tags      **tags;          /* 每硬件队列的标签集 */
    struct blk_mq_tags       *shared_tags;  /* 共享标签集 */
    struct mutex              tag_list_lock; /* 标签列表锁 */
    struct list_head         tag_list;      /* 使用此标签集的队列列表 */
    struct srcu_struct       *srcu;          /* 阻塞类型的 SRCU */
    struct srcu_struct        tags_srcu;     /* 延迟释放标签的 SRCU */
    struct rw_semaphore      update_nr_hwq_lock; /* 更新 nr_hw_queues 的锁 */
};
```

---

## blk_mq_ops 驱动操作接口

定义位置：`/Users/sphinx/github/linux/include/linux/blk-mq.h` 第 576-687 行

```c
struct blk_mq_ops {
    /**
     * queue_rq: 将新请求加入硬件队列
     */
    blk_status_t (*queue_rq)(struct blk_mq_hw_ctx *,
                 const struct blk_mq_queue_data *);

    /**
     * commit_rqs: 如果驱动使用 bd->last 判断何时提交请求
     */
    void (*commit_rqs)(struct blk_mq_hw_ctx *);

    /**
     * queue_rqs: 批量提交请求列表
     */
    void (*queue_rqs)(struct rq_list *rqlist);

    /**
     * get_budget/put_budget: 预算管理
     */
    int (*get_budget)(struct request_queue *);
    void (*put_budget)(struct request_queue *, int);

    /**
     * timeout: 请求超时处理
     */
    enum blk_eh_timer_return (*timeout)(struct request *);

    /**
     * poll: 轮询完成状态
     */
    int (*poll)(struct blk_mq_hw_ctx *, struct io_comp_batch *);

    /**
     * complete: 请求完成回调
     */
    void (*complete)(struct request *);

    /**
     * init_hctx/exit_hctx: 硬件队列初始化/退出
     */
    int (*init_hctx)(struct blk_mq_hw_ctx *, void *, unsigned int);
    void (*exit_hctx)(struct blk_mq_hw_ctx *, unsigned int);

    /**
     * init_request/exit_request: 请求初始化/退出
     */
    int (*init_request)(struct blk_mq_tag_set *set, struct request *,
                unsigned int, unsigned int);
    void (*exit_request)(struct blk_mq_tag_set *set, struct request *,
                 unsigned int);

    /**
     * cleanup_rq: 释放未完成的请求
     */
    void (*cleanup_rq)(struct request *);

    /**
     * busy: 返回队列是否忙碌
     */
    bool (*busy)(struct request_queue *);

    /**
     * map_queues: 自定义队列映射
     */
    void (*map_queues)(struct blk_mq_tag_set *set);
};
```

### 关键操作：queue_rq

```c
// blk-mq.c 第 2148 行
ret = q->mq_ops->queue_rq(hctx, &bd);
```

bd (blk_mq_queue_data) 结构：
```c
struct blk_mq_queue_data {
    struct request *rq;  /* 请求指针 */
    bool last;           /* 是否是队列中最后一个请求 */
};
```

---

## 硬件队列 (hctx) 管理

### 1. 初始化流程

**blk_mq_init_allocated_queue()** (`/Users/sphinx/github/linux/block/blk-mq.c` 第 4630-4678 行)：

```c
int blk_mq_init_allocated_queue(struct blk_mq_tag_set *set,
        struct request_queue *q)
{
    q->mq_ops = set->ops;           // 设置 MQ 操作
    q->tag_set = set;               // 设置标签集

    if (blk_mq_alloc_ctxs(q))       // 分配软件队列上下文
        goto err_exit;

    blk_mq_sysfs_init(q);           // 初始化 sysfs

    spin_lock_init(&q->unused_hctx_lock);
    blk_mq_realloc_hw_ctxs(set, q); // 重新分配硬件队列

    INIT_WORK(&q->timeout_work, blk_mq_timeout_work);
    blk_queue_rq_timeout(q, set->timeout ? set->timeout : 30 * HZ);

    q->nr_requests = set->queue_depth;
    q->async_depth = set->queue_depth;

    blk_mq_init_cpu_queues(q, set->nr_hw_queues);  // 初始化 CPU 队列
    blk_mq_map_swqueue(q);                         // 映射软件队列
    blk_mq_add_queue_tag_set(set, q);              // 添加到标签集

    return 0;
}
```

### 2. 硬件队列分配

**blk_mq_alloc_hctx()** (`/Users/sphinx/github/linux/block/blk-mq.c` 第 4026-4080 行)：

```c
static struct blk_mq_hw_ctx *
blk_mq_alloc_hctx(struct request_queue *q, struct blk_mq_tag_set *set,
           unsigned int hctx_idx)
{
    struct blk_mq_hw_ctx *hctx;
    gfp_t gfp = GFP_KERNEL | __GFP_NOWARN | __GFP_NORETRY;

    hctx = kzalloc_node(sizeof(*hctx), gfp, node);
    if (!hctx)
        return NULL;

    hctx->queue_num = hctx_idx;
    hctx->numa_node = set->numa_node;
    hctx->queue = q;
    hctx->tags = set->tags[hctx_idx];
    // ... 初始化其他字段
}
```

### 3. 队列运行管理

**blk_mq_run_hw_queue()** (`/Users/sphinx/github/linux/block/blk-mq.c` 第 2352-2393 行)：

```c
void blk_mq_run_hw_queue(struct blk_mq_hw_ctx *hctx, bool async)
{
    /* 检查队列是否应该运行 */
    if (!blk_mq_hw_queue_need_run(hctx))
        return;

    /* ... 触发调度 ... */
}
```

**blk_mq_hw_queue_need_run()** (`/Users/sphinx/github/linux/block/blk-mq.c` 第 2325-2350 行)：

```c
static inline bool blk_mq_hw_queue_need_run(struct blk_mq_hw_ctx *hctx)
{
    struct request_queue *q = hctx->queue;

    if (hctx->state & BLK_MQ_S_STOPPED)      // 已停止
        return false;
    if (blk_queue_quiesced(q))                // 已静默
        return false;
    // ...
    return true;
}
```

### 4. CPU 到硬件队列的映射

**blk_mq_map_queues()** (`/Users/sphinx/github/linux/block/blk-mq.c` 第 4759-4793 行)：

```c
static void blk_mq_update_queue_map(struct blk_mq_tag_set *set)
{
    // 设置默认队列数
    if (set->nr_maps == 1)
        set->map[HCTX_TYPE_DEFAULT].nr_queues = set->nr_hw_queues;

    if (set->ops->map_queues) {
        // 驱动自定义映射
        set->ops->map_queues(set);
    } else {
        // 默认轮转映射
        blk_mq_map_queues(&set->map[HCTX_TYPE_DEFAULT]);
    }
}
```

---

## 标签管理 (tag)

### 1. 共享标签 vs 每硬件队列标签

**共享标签模式** (`BLK_MQ_F_TAG_QUEUE_SHARED`)：

```c
// blk-mq-tag.c 第 51-67 行
void __blk_mq_tag_busy(struct blk_mq_hw_ctx *hctx)
{
    if (blk_mq_is_shared_tags(hctx->flags)) {
        struct request_queue *q = hctx->queue;
        // 设置队列级别的活跃标志
        if (test_bit(QUEUE_FLAG_HCTX_ACTIVE, &q->queue_flags) ||
            test_and_set_bit(QUEUE_FLAG_HCTX_ACTIVE, &q->queue_flags))
            return;
    } else {
        // 设置硬件队列级别的活跃标志
        if (test_bit(BLK_MQ_S_TAG_ACTIVE, &hctx->state) ||
            test_and_set_bit(BLK_MQ_S_TAG_ACTIVE, &hctx->state))
            return;
    }
    // ...
}
```

**关键区别：**
- **共享标签**：所有硬件队列共享一个标签池，需要跟踪 QUEUE_FLAG_HCTX_ACTIVE
- **独立标签**：每个硬件队列有自己的标签池，独立跟踪 BLK_MQ_S_TAG_ACTIVE

### 2. 标签分配

**blk_mq_get_tag()** (`/Users/sphinx/github/linux/block/blk-mq-tag.c` 第 137-226 行)：

```c
unsigned int blk_mq_get_tag(struct blk_mq_alloc_data *data)
{
    struct blk_mq_tags *tags = blk_mq_tags_from_data(data);
    struct sbitmap_queue *bt;
    // ...
    
    if (data->flags & BLK_MQ_REQ_RESERVED) {
        bt = &tags->breserved_tags;  // 保留标签
    } else {
        bt = &tags->bitmap_tags;      // 普通标签
    }

    tag = __blk_mq_get_tag(data, bt);
    if (tag != BLK_MQ_NO_TAG)
        goto found_tag;

    // 等待标签...
}
```

### 3. 标签集初始化

**blk_mq_init_tags()** (`/Users/sphinx/github/linux/block/blk-mq-tag.c` 第 550-583 行)：

```c
struct blk_mq_tags *blk_mq_init_tags(unsigned int total_tags,
        unsigned int reserved_tags, unsigned int flags, int node)
{
    unsigned int depth = total_tags - reserved_tags;
    bool round_robin = flags & BLK_MQ_F_TAG_RR;
    struct blk_mq_tags *tags;

    tags = kzalloc_node(sizeof(*tags), GFP_KERNEL, node);
    // 初始化位图队列
    bt_alloc(&tags->bitmap_tags, depth, round_robin, node);
    bt_alloc(&tags->breserved_tags, reserved_tags, round_robin, node);

    return tags;
}
```

---

## 调度器集成

### 1. elevator_mq_ops 接口

定义位置：`/Users/sphinx/github/linux/block/elevator.h` 第 57-84 行

```c
struct elevator_mq_ops {
    int (*init_sched)(struct request_queue *, struct elevator_queue *);
    void (*exit_sched)(struct elevator_queue *);
    int (*init_hctx)(struct blk_mq_hw_ctx *, unsigned int);
    void (*exit_hctx)(struct blk_mq_hw_ctx *, unsigned int);
    void (*depth_updated)(struct request_queue *);
    void *(*alloc_sched_data)(struct request_queue *);
    void (*free_sched_data)(void *);

    bool (*allow_merge)(struct request_queue *, struct request *, struct bio *);
    bool (*bio_merge)(struct request_queue *, struct bio *, unsigned int);
    int (*request_merge)(struct request_queue *q, struct request **, struct bio *);
    void (*request_merged)(struct request_queue *, struct request *, enum elv_merge);
    void (*requests_merged)(struct request_queue *, struct request *, struct request *);
    void (*limit_depth)(blk_opf_t, struct blk_mq_alloc_data *);
    void (*prepare_request)(struct request *);
    void (*finish_request)(struct request *);
    void (*insert_requests)(struct blk_mq_hw_ctx *hctx, struct list_head *list,
            blk_insert_t flags);
    struct request *(*dispatch_request)(struct blk_mq_hw_ctx *);
    bool (*has_work)(struct blk_mq_hw_ctx *);
    void (*completed_request)(struct request *, u64);
    void (*requeue_request)(struct request *);
    struct request *(*former_request)(struct request_queue *, struct request *);
    struct request *(*next_request)(struct request_queue *, struct request *);
    void (*init_icq)(struct io_cq *);
    void (*exit_icq)(struct io_cq *);
};
```

### 2. 调度器与 blk-mq 的交互

**blk_mq_insert_request()** (`/Users/sphinx/github/linux/block/blk-mq.c` 第 2623-2683 行)：

```c
static void blk_mq_insert_request(struct request *rq, blk_insert_t flags)
{
    struct request_queue *q = rq->q;
    struct blk_mq_ctx *ctx = rq->mq_ctx;
    struct blk_mq_hw_ctx *hctx = rq->mq_hctx;

    if (blk_rq_is_passthrough(rq)) {
        // 穿透请求直接加入 dispatch
        blk_mq_request_bypass_insert(rq, flags);
    } else if (req_op(rq) == REQ_OP_FLUSH) {
        // flush 请求加入 dispatch 队列头部
        blk_mq_request_bypass_insert(rq, BLK_MQ_INSERT_AT_HEAD);
    } else if (q->elevator) {
        // 有调度器，调用调度器插入接口
        list_add(&rq->queuelist, &list);
        q->elevator->type->ops.insert_requests(hctx, &list, flags);
    } else {
        // 无调度器，加入软件队列
        spin_lock(&ctx->lock);
        if (flags & BLK_MQ_INSERT_AT_HEAD)
            list_add(&rq->queuelist, &ctx->rq_lists[hctx->type]);
        else
            list_add_tail(&rq->queuelist, &ctx->rq_lists[hctx->type]);
        blk_mq_hctx_mark_pending(hctx, ctx);
        spin_unlock(&ctx->lock);
    }
}
```

### 3. 调度器分发请求

**__blk_mq_do_dispatch_sched()** (`/Users/sphinx/github/linux/block/blk-mq-sched.c` 第 85-174 行)：

```c
static int __blk_mq_do_dispatch_sched(struct blk_mq_hw_ctx *hctx)
{
    struct request_queue *q = hctx->queue;
    struct elevator_queue *e = q->elevator;
    // ...
    
    do {
        // 检查调度器是否有工作
        if (e->type->ops.has_work && !e->type->ops.has_work(hctx))
            break;

        // 从调度器获取请求
        rq = e->type->ops.dispatch_request(hctx);
        if (!rq) {
            // 没有请求可分发
            break;
        }

        list_add_tail(&rq->queuelist, &rq_list);
        count++;

        // 获取驱动标签
        if (!blk_mq_get_driver_tag(rq))
            break;
    } while (count < max_dispatch);

    // 分发请求列表
    dispatched = blk_mq_dispatch_rq_list(hctx, &rq_list, false);
}
```

### 4. 调度器调度入口

**blk_mq_sched_dispatch_requests()** (`/Users/sphinx/github/linux/block/blk-mq-sched.c` 第 317-333 行)：

```c
void blk_mq_sched_dispatch_requests(struct blk_mq_hw_ctx *hctx)
{
    struct request_queue *q = hctx->queue;

    if (unlikely(blk_mq_hctx_stopped(hctx) || blk_queue_quiesced(q)))
        return;

    if (__blk_mq_sched_dispatch_requests(hctx) == -EAGAIN) {
        if (__blk_mq_sched_dispatch_requests(hctx) == -EAGAIN)
            blk_mq_run_hw_queue(hctx, true);
    }
}
```

---

## 请求提交路径

### blk_mq_submit_bio() - 主要提交入口

**blk_mq_submit_bio()** (`/Users/sphinx/github/linux/block/blk-mq.c` 第 3141-3264 行)：

```c
void blk_mq_submit_bio(struct bio *bio)
{
    struct request_queue *q = bdev_get_queue(bio->bi_bdev);
    struct blk_plug *plug = current->plug;
    const int is_sync = op_is_sync(bio->bi_opf);
    struct blk_mq_hw_ctx *hctx;
    unsigned int nr_segs;
    struct request *rq;
    blk_status_t ret;

    // 1. 检查 plug 缓存的请求
    rq = blk_mq_peek_cached_request(plug, q, bio->bi_opf);

    // 2. 区域写入 plug 处理
    if (bio_zone_write_plugging(bio)) {
        nr_segs = bio->__bi_nr_segments;
        if (rq)
            blk_queue_exit(q);
        goto new_request;
    }

    // 3. 获取队列引用
    if (!rq) {
        if (unlikely(bio_queue_enter(bio)))
            return;
    }

    // 4. 检查对齐和轮询支持
    if (unlikely(bio_unaligned(bio, q))) {
        bio_io_error(bio);
        goto queue_exit;
    }

    // 5. 分割 bio 以符合限制
    bio = __bio_split_to_limits(bio, &q->limits, &nr_segs);
    if (!bio)
        goto queue_exit;

    // 6. 完整性准备
    if (!bio_integrity_prep(bio))
        goto queue_exit;

    blk_mq_bio_issue_init(q, bio);
    
    // 7. 尝试合并
    if (blk_mq_attempt_bio_merge(q, bio, nr_segs))
        goto queue_exit;

    // 8. 区域写入 plug
    if (bio_needs_zone_write_plugging(bio)) {
        if (blk_zone_plug_bio(bio, nr_segs))
            goto queue_exit;
    }

new_request:
    // 9. 获取或创建请求
    if (rq) {
        blk_mq_use_cached_rq(rq, plug, bio);
    } else {
        rq = blk_mq_get_new_requests(q, plug, bio);
        if (unlikely(!rq)) {
            // 处理无法获取请求的情况
            goto queue_exit;
        }
    }

    // 10. 跟踪 QoS
    rq_qos_track(q, rq, bio);

    // 11. 转换 bio 为请求
    blk_mq_bio_to_request(rq, bio, nr_segs);

    // 12. 加密密钥获取
    ret = blk_crypto_rq_get_keyslot(rq);
    if (ret != BLK_STS_OK) {
        bio->bi_status = ret;
        bio_endio(bio);
        blk_mq_free_request(rq);
        return;
    }

    // 13. flush 请求处理
    if (op_is_flush(bio->bi_opf) && blk_insert_flush(rq))
        return;

    // 14. 如果有 plug，加入 plug 列表
    if (plug) {
        blk_add_rq_to_plug(plug, rq);
        return;
    }

    // 15. 决定分发路径
    hctx = rq->mq_hctx;
    if ((rq->rq_flags & RQF_USE_SCHED) ||
        (hctx->dispatch_busy && (q->nr_hw_queues == 1 || !is_sync))) {
        // 使用调度器或插入后运行队列
        blk_mq_insert_request(rq, 0);
        blk_mq_run_hw_queue(hctx, true);
    } else {
        // 直接尝试发送
        blk_mq_run_dispatch_ops(q, blk_mq_try_issue_directly(hctx, rq));
    }
    return;

queue_exit:
    if (!rq)
        blk_queue_exit(q);
}
```

### 请求提交流程图

```
blk_mq_submit_bio()
       │
       ▼
┌─────────────────┐
│ 检查 plug 缓存   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ bio_split       │ ──► bio_io_error()
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ bio_integrity   │
│ _prep()         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ blk_mq_attempt  │
│ _bio_merge()    │ ──► 合并成功，退出
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 获取/创建请求    │
│ blk_mq_get_new  │
│ _requests()     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ blk_mq_bio_to   │
│ _request()      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ flush 请求?     │ ──► blk_insert_flush()
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ plug 缓存?      │ ──► blk_add_rq_to_plug()
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RQF_USE_SCHED   │ ──► blk_mq_insert_request()
│ 或 dispatch_busy│     + blk_mq_run_hw_queue()
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 直接发送         │
│ blk_mq_try_issue│
│ _directly()     │
└─────────────────┘
```

---

## 请求分发 (dispatch) 机制

### 1. 主分发函数

**blk_mq_dispatch_rq_list()** (`/Users/sphinx/github/linux/block/blk-mq.c` 第 2116-2242 行)：

```c
bool blk_mq_dispatch_rq_list(struct blk_mq_hw_ctx *hctx, struct list_head *list,
                 bool get_budget)
{
    enum prep_dispatch prep;
    struct request_queue *q = hctx->queue;
    struct request *rq;
    int queued;
    blk_status_t ret = BLK_STS_OK;
    bool needs_resource = false;

    if (list_empty(list))
        return false;

    queued = 0;
    do {
        struct blk_mq_queue_data bd;

        rq = list_first_entry(list, struct request, queuelist);
        WARN_ON_ONCE(hctx != rq->mq_hctx);
        
        // 预处理请求
        prep = blk_mq_prep_dispatch_rq(rq, get_budget);
        if (prep != PREP_DISPATCH_OK)
            break;

        list_del_init(&rq->queuelist);

        bd.rq = rq;
        bd.last = list_empty(list);

        // 调用驱动 queue_rq 回调
        ret = q->mq_ops->queue_rq(hctx, &bd);
        switch (ret) {
        case BLK_STS_OK:
            queued++;
            break;
        case BLK_STS_RESOURCE:
            needs_resource = true;
            fallthrough;
        case BLK_STS_DEV_RESOURCE:
            // 资源不足，保留请求用于后续重试
            blk_mq_handle_dev_resource(rq, list);
            goto out;
        default:
            blk_mq_end_request(rq, ret);
        }
    } while (!list_empty(list));

out:
    // 提交已发送的请求
    if (!list_empty(list) || ret != BLK_STS_OK)
        blk_mq_commit_rqs(hctx, queued, false);

    // 将未发送的请求保留在 dispatch 列表
    if (!list_empty(list)) {
        spin_lock(&hctx->lock);
        list_splice_tail_init(list, &hctx->dispatch);
        spin_unlock(&hctx->lock);

        // 可能需要重新运行队列
        needs_restart = blk_mq_sched_needs_restart(hctx);
        if (!needs_restart ||
            (no_tag && list_empty_careful(&hctx->dispatch_wait.entry)))
            blk_mq_run_hw_queue(hctx, true);
        else if (needs_resource)
            blk_mq_delay_run_hw_queue(hctx, BLK_MQ_RESOURCE_DELAY);
    }

    return true;
}
```

### 2. 分发决策流程

```
blk_mq_sched_dispatch_requests()
         │
         ▼
┌─────────────────────────┐
│ hctx 已停止或队列静默?   │ ──► 返回
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ __blk_mq_sched_dispatch │
│ _requests()             │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ dispatch 列表非空?      │
│ (之前未完成的请求)       │
└────────┬────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
   Yes       No
    │         │
    ▼         ▼
┌─────────┐  ┌─────────────────────────┐
│ 优先处理 │  │ 有调度器?               │
│ dispatch │  └────────┬────────────────┘
│ 列表     │           │
└────┬────┘      ┌─────┴─────┐
     │           ▼           ▼
     ▼          Yes         No
┌─────────────────────────┐
│ dispatch_rq_list()      │
│ (get_budget=true)       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ blk_mq_do_dispatch_sched│
│ 或                     │
│ blk_mq_do_dispatch_ctx  │
└─────────────────────────┘
```

### 3. 硬件队列轮转 CPU 选择

**blk_mq_hctx_next_cpu()** (`/Users/sphinx/github/linux/block/blk-mq.c` 第 2268-2299 行)：

```c
static int blk_mq_hctx_next_cpu(struct blk_mq_hw_ctx *hctx)
{
    bool tried = false;
    int next_cpu = hctx->next_cpu;

    if (hctx->queue->nr_hw_queues == 1 || blk_mq_hctx_empty_cpumask(hctx))
        return WORK_CPU_UNBOUND;

    if (--hctx->next_cpu_batch <= 0) {
select_cpu:
        next_cpu = cpumask_next_and(next_cpu, hctx->cpumask, cpu_online_mask);
        if (next_cpu >= nr_cpu_ids)
            next_cpu = blk_mq_first_mapped_cpu(hctx);
        hctx->next_cpu_batch = BLK_MQ_CPU_WORK_BATCH;
    }

    if (!cpu_online(next_cpu)) {
        if (!tried) {
            tried = true;
            goto select_cpu;
        }
        // 标记下次重新选择
        hctx->next_cpu = next_cpu;
        return WORK_CPU_UNBOUND;
    }

    hctx->next_cpu = next_cpu;
    return next_cpu;
}
```

---

## 总结

### blk-mq 的核心优势

1. **多核可扩展性**
   - 每个 CPU 有独立的软件队列
   - 大幅减少锁竞争

2. **硬件并行性**
   - 支持多个硬件队列
   - 充分利用 NVMe 等设备的并行能力

3. **灵活的调度集成**
   - 调度器接口完整
   - 支持多种调度算法 (deadline, cfq, bfq, kyber 等)

4. **资源管理**
   - 标签管理支持共享和独立模式
   - 预算 (budget) 系统控制队列深度

5. **向后兼容**
   - 传统单队列设备也可使用
   - 调度器可以逐步迁移

### 关键数据结构关系

```
request_queue
     │
     ├── mq_ops ──────────► blk_mq_ops (驱动回调)
     │
     ├── tag_set ─────────► blk_mq_tag_set (标签管理)
     │     │
     │     └── tags[] ────► blk_mq_tags (每 hctx 的标签)
     │     └── shared_tags ──► 共享标签
     │
     ├── elevator ─────────► elevator_queue
     │     │
     │     └── type ──────► elevator_type
     │           │
     │           └── ops ───► elevator_mq_ops (调度器回调)
     │
     ├── queue_hw_ctx[] ───► blk_mq_hw_ctx (硬件队列)
     │     │
     │     ├── tags ───────► blk_mq_tags
     │     ├── sched_tags ─► blk_mq_tags (调度器标签)
     │     │
     │     └── ctxs[] ─────► blk_mq_ctx (软件队列)
     │           │
     │           └── rq_lists[] ──► per-type 请求列表
     │
     └── ctxs[] ───────────► blk_mq_ctx (per-cpu 上下文)
```

---

*文档生成时间：2026-04-26*
*内核版本参考：Linux block layer*
