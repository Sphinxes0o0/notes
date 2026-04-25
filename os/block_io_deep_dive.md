# Linux Block I/O 子系统深度架构分析 v2

## 1. 概述

本文档是 Linux Block I/O 子系统的第二轮深度分析，重点关注 blk-mq 多队列机制、请求分配与标签管理、调度算法细节、bio/request 合并机制、以及写回控制等核心实现。

## 2. blk-mq 多队列架构

### 2.1 多队列设计原理

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      blk-mq Multi-Queue Architecture                      │
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────┐     │
│   │                Per-CPU Software Queues (blk_mq_ctx)          │     │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │     │
│   │  │ CPU 0   │ │ CPU 1   │ │ CPU 2   │ │ CPU N   │           │     │
│   │  │ ctx[0]  │ │ ctx[1]  │ │ ctx[2]  │ │ ctx[N]  │           │     │
│   │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │     │
│   └───────┼───────────┼───────────┼───────────┼─────────────────┘     │
│           │           │           │           │                           │
│           └───────────┴─────┬─────┴───────────┘                           │
│                             │                                             │
│   ┌─────────────────────────┼─────────────────────────────────────────┐ │
│   │              Hardware Queue Mapping (blk_mq_map_queues)            │ │
│   │  Context → Hardware Queue 映射策略                                 │ │
│   │  1. 1:1 映射（低队列数）                                         │ │
│   │  2. N:1 映射（高队列数，多CPU共享）                               │ │
│   └─────────────────────────┼─────────────────────────────────────────┘ │
│                             │                                             │
│   ┌─────────────────────────┼─────────────────────────────────────────┐ │
│   │                Per-HW Hardware Queues (blk_mq_hw_ctx)            │ │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐               │ │
│   │  │ hctx[0] │ │ hctx[1] │ │ hctx[2] │ │ hctx[M] │               │ │
│   │  │ dispatch│ │ dispatch│ │ dispatch│ │ dispatch│               │ │
│   │  │  queue  │ │  queue  │ │  queue  │ │  queue  │               │ │
│   │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘               │ │
│   └───────┼───────────┼───────────┼───────────┼─────────────────────┘ │
│           │           │           │           │                           │
└───────────┼───────────┼───────────┼───────────┼───────────────────────────┘
            │           │           │           │
            ▼           ▼           ▼           ▼
        ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
        │ NVMe  │   │ SCSI  │   │  IDE  │   │ ...   │
        │ Queue │   │ Queue │   │ Queue │   │       │
        └───────┘   └───────┘   └───────┘   └───────┘
```

### 2.2 核心数据结构

```c
/**
 * blk_mq_ctx - Per-CPU software queue context
 *
 * 每个 CPU 一个实例，接收该 CPU 产生的 I/O 请求
 */
struct blk_mq_ctx {
    struct request_queue    *queue;          // 关联的请求队列
    spinlock_t              lock;             // 保护本地队列
    unsigned int            cpu;             // CPU ID

    /* 软件队列中的请求 */
    struct list_head        rq_list;         // 准备好的请求列表

    /* 映射到硬件队列的索引 */
    unsigned int            index_hw;        // 该 ctx 在 hctx 中的索引

    struct blk_mq_ctxs      *ctxs;
};

/**
 * blk_mq_hw_ctx - Per-hardware queue context
 *
 * 直接映射到硬件提交队列
 */
struct blk_mq_hw_ctx {
    struct request_queue    *queue;          // 关联的请求队列
    unsigned int            queue_num;       // 队列编号

    /* 硬件队列状态 */
    spinlock_t              lock;
    struct list_head        dispatch;        // 正在派发的请求队列
    unsigned long           state;           // HW queue state flags

    /* 标签管理 */
    struct blk_mq_tags      *tags;           // 调度标签
    struct blk_mq_tags      *sched_tags;     // 调度器标签

    /* 等待队列 */
    wait_queue_entry_t      dispatch_wait;
    int                     dispatch_wait_active;

    /* CPU 亲和性 */
    cpumask_var_t           cpumask;         // 允许的 CPU mask
    int                     next_cpu;        // 下一个用于派发的 CPU
    int                     next_cpu_batch;

    /* sbitmap 用于跟踪哪些 ctx 有待处理的请求 */
    struct sbitmap          ctx_map;         // ctx 位图

    /* I/O 完成处理 */
    struct blk_mq_ctx       **ctxs;          // 指向 per-cpu ctx 数组
    unsigned int            nr_ctx;          // ctx 数量

    struct blk_mq_inflight  *inflight;       // 正在进行的请求
} __percpu;
```

### 2.3 请求分配流程

```c
/**
 * __blk_mq_alloc_requests - 分配请求
 * @data: 分配数据上下文
 *
 * 分配算法：
 * 1. 获取当前 CPU 的 ctx
 * 2. 根据 cmd_flags 映射到对应的 hctx
 * 3. 从 hctx 的标签分配器获取标签
 * 4. 初始化 request 结构
 */
static struct request *__blk_mq_alloc_requests(struct blk_mq_alloc_data *data)
{
    struct request_queue *q = data->q;
    struct request *rq;

    /* 获取当前 CPU 的 ctx */
    data->ctx = blk_mq_get_ctx(q);

    /* 映射到硬件队列 */
    data->hctx = blk_mq_map_queue(data->cmd_flags, data->ctx);

    /* 限制深度（调度器相关） */
    blk_mq_limit_depth(data);

    /* 批量分配优化 */
    if (data->nr_tags > 1) {
        rq = __blk_mq_alloc_requests_batch(data);
        if (rq)
            return rq;
        data->nr_tags = 1;
    }

    /* 单个分配 */
    tag = blk_mq_get_tag(data);
    if (tag == BLK_MQ_NO_TAG) {
        if (data->flags & BLK_MQ_REQ_NOWAIT)
            return NULL;
        /* 睡眠等待标签 */
        msleep(3);
        goto retry;
    }

    rq = blk_mq_rq_ctx_init(data, blk_mq_tags_from_data(data), tag);
    return rq;
}

/**
 * blk_mq_rq_ctx_init - 初始化 request
 *
 * 初始化步骤：
 * 1. 设置 q, mq_ctx, mq_hctx
 * 2. 设置 cmd_flags 和 rq_flags
 * 3. 分配标签（tag 或 internal_tag）
 * 4. 初始化链表节点
 * 5. 设置引用计数为 1
 */
static struct request *blk_mq_rq_ctx_init(struct blk_mq_alloc_data *data,
        struct blk_mq_tags *tags, unsigned int tag)
{
    struct blk_mq_ctx *ctx = data->ctx;
    struct blk_mq_hw_ctx *hctx = data->hctx;
    struct request_queue *q = data->q;
    struct request *rq = tags->static_rqs[tag];

    rq->q = q;
    rq->mq_ctx = ctx;
    rq->mq_hctx = hctx;
    rq->cmd_flags = data->cmd_flags;

    /* 设置标签 */
    if (data->rq_flags & RQF_SCHED_TAGS) {
        rq->tag = BLK_MQ_NO_TAG;
        rq->internal_tag = tag;
    } else {
        rq->tag = tag;
        rq->internal_tag = BLK_MQ_NO_TAG;
    }

    rq->part = NULL;
    rq->io_start_time_ns = 0;
    rq->stats_sectors = 0;
    rq->nr_phys_segments = 0;

    /* 初始化链表 */
    INIT_LIST_HEAD(&rq->queuelist);

    /* 设置引用计数 */
    req_ref_set(rq, 1);

    /* 调度器准备 */
    if (rq->rq_flags & RQF_USE_SCHED) {
        struct elevator_queue *e = data->q->elevator;
        INIT_HLIST_NODE(&rq->hash);
        RB_CLEAR_NODE(&rq->rb_node);
        if (e->type->ops.prepare_request)
            e->type->ops.prepare_request(rq);
    }

    return rq;
}
```

### 2.4 标签管理（Tag Management）

```c
/**
 * blk_mq_tags - 标签分配器
 *
 * 支持两种标签：
 * 1. 调度标签（sched_tags）- 用于 I/O 调度器管理
 * 2. 请求标签（tags）- 直接派发到硬件
 */
struct blk_mq_tags {
    unsigned int            nr_tags;         // 总标签数
    unsigned int            nr_reserved_tags; // 保留标签数

    /* 标签位图 */
    struct sbitmap_queue    bitmap_tags;     // 可用标签
    struct sbitmap_queue   breserved_tags;  // 保留标签

    /* 静态 request 数组（预分配） */
    struct request          **static_rqs;
    struct request          **zs旺; // 错误，应该删除

    /* 活跃请求计数 */
    atomic_t                active_queues;
};
```

## 3. Bio 到 Request 的转换

### 3.1 submit_bio 流程

```c
/**
 * submit_bio - 提交 bio 到块层
 * @bio: bio 结构
 *
 * 流程：
 * 1. 设置 bio 发行时间
 * 2. 调用 __submit_bio
 * 3. 如果是同步 I/O，可能阻塞等待
 */
void submit_bio(struct bio *bio)
{
    /* 设置发行时间（用于 cgroup 统计） */
    blk_account_io_start(bio);

    /* 转换为当前 cgroup */
    bio = bio_batch_convert(bio);

    /* 提交 bio */
    __submit_bio(bio);

    /* 同步 I/O 等待 */
    if (bio_op(bio) == REQ_OP_READ && !op_is_flush(bio->bi_opf)) {
        bio_wait_endio(bio);
    }
}

/**
 * __submit_bio - 实际提交逻辑
 *
 * 关键步骤：
 * 1. 分区重映射（partition remap）
 * 2. cgroup 限流检查
 * 3. 转换为 request 或直接派发
 */
static void __submit_bio(struct bio *bio)
{
    struct block_device *bdev = bio->bi_bdev;
    struct request_queue *q = bdev->bd_queue;

    /* 分区重映射 - 将分区偏移加到起始扇区 */
    bio = blk_partition_remap(bio);

    /* 检查 cgroup 限流 */
    if (blk_cgroup_bio_start(q, bio))
        return;

    /* 转换为 request 并派发 */
    blk_mq_submit_bio(bio);
}
```

### 3.2 blk_mq_submit_bio

```c
/**
 * blk_mq_submit_bio - 将 bio 转换为 request 并提交
 * @bio: bio
 *
 * 核心流程：
 * 1. 查找/创建 request
 * 2. 尝试与现有 request 合并
 * 3. 插入调度队列或直接派发
 */
void blk_mq_submit_bio(struct bio *bio)
{
    struct request_queue *q = bdev->bd_queue;
    struct blk_mq_ctx *ctx;
    struct blk_mq_hw_ctx *hctx;
    struct request *rq;

    /* 分配请求 */
    rq = blk_mq_alloc_request(q, bio_op(bio), 0);
    if (!rq)
        return;

    /* 设置 request 关联的 bio */
    rq->bio = rq->biotail = bio;
    bio->bi_next = NULL;

    /* 更新统计 */
    blk_account_io_start(bio);

    /* 尝试合并到现有 request */
    if (blk_mq_attempt_bio_merge(q, rq, bio))
        return;

    /* 插入调度队列 */
    blk_mq_sched_insert_request(rq, true, true, true);
}
```

### 3.3 Bio 合并机制

```c
/**
 * blk_mq_attempt_bio_merge - 尝试将 bio 合并到现有 request
 * @q: 请求队列
 * @rq: 目标 request
 * @bio: 要合并的 bio
 *
 * 合并条件：
 * 1. 连续扇区（rq->sector + rq->nr_sectors == bio->bi_iter.bi_sector）
 * 2. 相同方向（读写）
 * 3. 兼容的标志
 */
bool blk_mq_attempt_bio_merge(struct request_queue *q, struct request *rq,
                              struct bio *bio)
{
    /* 检查是否可以合并 */
    if (!blk_rq_merge_ok(rq, bio))
        return false;

    /* 检查调度器是否允许合并 */
    if (!elv_bio_merge_ok(rq->q->elevator, rq, bio))
        return false;

    /* 执行合并 */
    switch (blk_try_merge(rq, bio)) {
    case ELEVATOR_BACK_MERGE:
        if (bio_attempt_back_merge(rq, bio))
            return true;
        break;
    case ELEVATOR_FRONT_MERGE:
        if (bio_attempt_front_merge(rq, bio))
            return true;
        break;
    case ELEVATOR_DISCARD_MERGE:
        if (bio_attempt_discard_merge(rq, bio))
            return true;
        break;
    default:
        return false;
    }
    return false;
}

/**
 * bio_attempt_back_merge - 后向合并
 *
 * 将 bio 合并到 request 的末尾（更高扇区地址）
 */
static bool bio_attempt_back_merge(struct request *rq, struct bio *bio)
{
    if (!blk_rq_segment_merge_ok(rq, bio))
        return false;

    /* 更新 request 长度 */
    rq->__data_len += bio->bi_iter.bi_size;

    /* 链接 bio */
    bio->bi_next = rq->bio;
    rq->bio = bio;

    /* 更新统计 */
    rq->nr_phys_segments = bio_phys_segments(rq->q, rq);

    return true;
}
```

## 4. I/O 调度器架构

### 4.1 调度器抽象

```c
/**
 * elevator_type - I/O 调度器类型
 *
 * 定义调度器的元数据和操作函数集
 */
struct elevator_type {
    /* 调度器名称 */
    const char *elevator_name;
    const char *elevator_alias;
    const struct elv_iosched_ops {
        /* 请求插入 */
        int (*elevator_add_req_fn)(struct request_queue *, struct request *);

        /* 合并检查 */
        bool (*elevator_merge_fn)(struct request_queue *,
                                   struct request **, struct bio *);

        /* 合并请求 */
        void (*elevator_merge_req_fn)(struct request_queue *,
                                      struct request *, struct request *);

        /* 取出一个请求派发 */
        struct request *(*elevator_dispatch_fn)(struct request_queue *, bool);

        /* 完成请求 */
        void (*elevator_completed_req_fn)(struct request_queue *,
                                          struct request *);

        /* 队列空闲 */
        void (*elevator_queue_empty_fn)(struct request_queue *);

        /* 允许合并 */
        bool (*elevator_allow_merge_fn)(struct request_queue *,
                                        struct request *, struct bio *);

        /* 限制深度 */
        void (*limit_depth_fn)(blk_opf_t, struct blk_mq_alloc_data *);
    } ops;
};
```

### 4.2 MQ-Deadline 调度器

```c
/**
 * deadline调度器数据结构
 *
 * 使用四种队列：
 * 1. 读请求队列（按扇区排序）
 * 2. 写请求队列（按扇区排序）
 * 3. 读 FIFO（按到期时间排序）
 * 4. 写 FIFO（按到期时间排序）
 */
struct deadline_data {
    /* 排序队列（红黑树） */
    struct rb_root_broken read_fifo;    // 读请求红黑树（按扇区）
    struct rb_root_broken write_fifo;    // 写请求红黑树

    /* 到期队列（链表） */
    struct list_head read_list;         // 读请求链表（FIFO）
    struct list_head write_list;        // 写请求链表（FIFO）

    /* 当前处理的请求 */
    struct request *next_rq[2];          // [0]=read, [1]=write

    /* 统计 */
    unsigned int read_cnt;              // 读请求计数
    unsigned int write_cnt;             // 写请求计数
    unsigned int read_fifo_cnt;         // 读 FIFO 计数
    unsigned int write_fifo_cnt;        // 写 FIFO 计数

    /* 参数 */
    unsigned int fifo_expire[2];        // FIFO 到期时间（ms）
    unsigned int fifo_batch;            // 批量大小
    unsigned int write_starved;         // 写饥饿阈值
};

/**
 * dd_dispatch - deadline 派发函数
 *
 * 派发策略：
 * 1. 优先处理到期的读请求
 * 2. 其次处理到期的写请求
 * 3. 然后处理读请求（按扇区顺序）
 * 4. 最后处理写请求（按扇区顺序）
 * 5. 交替处理读写以避免饥饿
 */
static struct request *dd_dispatch(struct request_queue *q, bool force)
{
    struct deadline_data *dd = q->elevator->elevator_data;
    struct request *rq;

    /* 检查是否有到期的请求 */
    rq = deadline_check_fifo(dd, READ);
    if (rq && (force || blk_mq_get_hctx_type(rq->cmd_flags) == HCTX_TYPE_POLL))
        goto done;

    rq = deadline_check_fifo(dd, WRITE);
    if (rq)
        goto done;

    /* 从排序队列取请求 */
    rq = deadline_dispatch_requests(dd, force);
done:
    if (rq)
        blk_mq_sched_dispatch_request(rq);
    return rq;
}

/**
 * deadline_check_fifo - 检查 FIFO 中是否有到期的请求
 */
static struct request *deadline_check_fifo(struct deadline_data *dd, int data_dir)
{
    struct list_head *fifo = &dd->fifo_list[data_dir];

    if (list_empty(fifo))
        return NULL;

    /* 获取队列中最早的请求 */
    struct request *rq = list_entry(fifo->next, struct request, queuelist);

    /* 检查是否到期 */
    if (time_after(jiffies, rq->deadline)) {
        /* 将请求移到队列末尾 */
        list_move_tail(&rq->queuelist, fifo);
        return rq;
    }

    return NULL;
}
```

### 4.3 BFQ 调度器

BFQ（Budget Fair Queuing）是一种提供延迟保证的调度器：

```c
/**
 * bfq_data - BFQ 调度器数据
 *
 * 核心概念：
 * 1. Budget：每次派发的扇区数预算
 * 2. Queue：每个进程的 I/O 队列
 * 3. Entity：调度实体（可以是 queue 或 group）
 */
struct bfq_data {
    /* 活跃实体（红黑树，按公平性键排序） */
    struct rb_root_broken active_tree;
    struct rb_root_broken idle_tree;

    /* 当前服务的实体 */
    struct bfq_entity *in_service_entity;

    /* 预算管理 */
    unsigned long bfq_max_budget;       // 最大预算
    unsigned long bfq_timeout;          // 超时时间

    /* 统计 */
    unsigned long total_requests;       // 总请求数
    unsigned long total_sectors;        // 总扇区数
};

/**
 * bfq_dispatch - BFQ 派发
 *
 * 派发策略：
 * 1. 选择当前预算内最多请求的队列
 * 2. 如果队列预算耗尽或空闲，选择新队列
 * 3. 维护公平性（通过 VR 算法）
 */
static struct request *bfq_dispatch(struct request_queue *q, bool force)
{
    struct bfq_data *bfqd = q->elevator->elevator_data;
    struct bfq_entity *entity;

    /* 获取下一个实体 */
    entity = bfq_pick_next_entity(bfqd);
    if (!entity)
        return NULL;

    /* 取出请求 */
    return bfq_get_request(entity);
}
```

### 4.4 CFQ 调度器（传统）

```c
/**
 * cfq_data - CFQ 调度器数据
 *
 * 使用时间片轮转：
 * 1. 每个进程一个 cfqq
 * 2. 时间片内该进程的请求派发
 * 3. 时间片结束切换到下一个进程
 */
struct cfq_data {
    /* 调度队列 */
    struct cfq_rb_root service_tree;    // 服务树（按虚拟时间排序）

    /* 当前进程队列 */
    struct cfq_queue *active_queue;
    struct cfq_io_context *active_cic;

    /* 时间片管理 */
    unsigned long cfq_slice_async;       // 异步时间片
    unsigned long cfq_slice_idle;        // 空闲时间片
    unsigned long cfq_slice_sync;       // 同步时间片
    unsigned long cfq_slice[2];         // 当前时间片

    /* 公平调度参数 */
    unsigned long cfq_target_latency;    // 目标延迟
    unsigned long cfq_latency;          // 延迟系数
};
```

## 5. Request 派发与完成

### 5.1 派发流程

```c
/**
 * blk_mq_sched_insert_request - 插入请求到调度队列
 * @rq: 请求
 * @at_head: 是否插入队首
 * @run_queue: 是否立即派发
 * @async: 是否异步
 */
void blk_mq_sched_insert_request(struct request *rq, bool at_head,
                                bool run_queue, bool async)
{
    struct request_queue *q = rq->q;
    struct elevator_queue *e = q->elevator;

    /* 从 blk_mq_ctx 移除（如果还在） */
    blk_mq_request_bypass_insert(rq, at_head ? 0 : BLK_MQ_INSERT_AT_HEAD);

    if (run_queue) {
        /* 派发请求 */
        blk_mq_run_hw_queue(rq->mq_hctx, async);
    }
}

/**
 * blk_mq_run_hw_queue - 运行硬件队列
 * @hctx: 硬件队列
 * @async: 是否异步
 */
void blk_mq_run_hw_queue(struct blk_mq_hw_ctx *hctx, bool async)
{
    /* 如果已经在运行，跳过 */
    if (!async)
        blk_mq_hctx_mark_pending(hctx, blk_mq_get_ctx(hctx->queue));

    blk_mq_dispatch_rq_list(hctx, NULL, 0);
}

/**
 * blk_mq_dispatch_rq_list - 派发请求列表
 * @hctx: 硬件队列
 * @rq_list: 请求列表（NULL 表示从调度器获取）
 * @flags: 派发标志
 */
blk_status_t blk_mq_dispatch_rq_list(struct blk_mq_hw_ctx *hctx,
                                     struct list_head *rq_list,
                                     unsigned int flags)
{
    struct request_queue *q = hctx->queue;
    blk_status_t ret = BLK_STS_OK;

    /* 获取待派发的请求列表 */
    if (!rq_list || list_empty(rq_list))
        rq_list = blk_mq_dequeue_from_hctx(hctx);

    /* 分派给硬件 */
    do {
        struct request *rq;
        struct blk_mq_queue_data bd = {
            .list = rq_list,
            .eject = false,
        };

        ret = q->mq_ops->queue_rq(hctx, &bd);

        if (ret != BLK_STS_OK) {
            /* 硬件队列满或错误，停止派发 */
            break;
        }
    } while (!list_empty(rq_list));

    return ret;
}
```

### 5.2 请求完成

```c
/**
 * blk_complete_request - 完成请求
 *
 * 完成处理：
 * 1. 调用 bio 完成回调
 * 2. 更新统计
 * 3. 释放请求到标签池
 */
static void blk_complete_request(struct request *req)
{
    struct bio *bio = req->bio;
    const bool is_flush = (req->rq_flags & RQF_FLUSH_SEQ) != 0;

    /* 更新统计 */
    trace_block_rq_complete(req, BLK_STS_OK, blk_rq_bytes(req));

    if (!bio)
        return;

    /* 完整性检查（如果启用） */
    if (blk_integrity_rq(req) && req_op(req) == REQ_OP_READ)
        blk_integrity_complete(req, blk_rq_bytes(req));

    /* 完成所有 bio */
    do {
        struct bio *next = bio->bi_next;
        bio_clear_flag(bio, BIO_TRACE_COMPLETION);
        bio_endio(bio);
        bio = next;
    } while (bio);
}

/**
 * blk_update_request - 部分完成请求
 * @req: 请求
 * @error: 错误状态
 * @nr_bytes: 完成的字节数
 *
 * 返回：是否还有剩余数据
 */
bool blk_update_request(struct request *req, blk_status_t error,
                       unsigned int nr_bytes)
{
    int total_bytes = 0;

    trace_block_rq_complete(req, error, nr_bytes);

    /* 遍历 bio 并完成 */
    while (req->bio) {
        struct bio *bio = req->bio;
        unsigned bio_bytes = min(bio->bi_iter.bi_size, nr_bytes);

        if (unlikely(error))
            bio->bi_status = error;

        /* 处理完整的 bio */
        if (bio_bytes == bio->bi_iter.bi_size) {
            req->bio = bio->bi_next;
        } else {
            /* 部分完成，更新偏移 */
            bio_advance(bio, bio_bytes);
        }

        total_bytes += bio_bytes;
        nr_bytes -= bio_bytes;

        if (!nr_bytes)
            break;
    }

    /* 更新请求长度 */
    req->__data_len -= total_bytes;

    return req->__data_len != 0;
}
```

## 6. 写回控制（Writeback Throttling）

### 6.1 wbt 架构

```c
/**
 * struct rq_wb - 写回节流数据
 *
 * 监控写回 I/O 延迟，在延迟过高时进行限流
 */
struct rq_wb {
    /* 延迟追踪 */
    struct wb_stat *stat;                // 每 CPU 统计
    unsigned long min_lat_nsec;          // 最小目标延迟
    unsigned long max_lat_nsec;          // 最大允许延迟

    /* 令牌桶 */
    struct token_bucket {
        unsigned long rate;              // 速率（bytes/sec）
        unsigned long burst;             // 突发量
        atomic64_t tokens;              // 当前令牌数
    } read_bkt, write_bkt;

    /* 拥塞状态 */
    atomic_t congestion;
};

/**
 * wbt_wait - 等待令牌或拥塞缓解
 * @q: 请求队列
 * @rw: 读写方向
 *
 * 限流策略：
 * 1. 检查令牌桶是否有足够令牌
 * 2. 检查是否处于拥塞状态
 * 3. 等待直到满足条件
 */
void wbt_wait(struct request_queue *q, blk_opf_t opf)
{
    struct rq_wb *wb = q->rq_wb;

    if (!wb)
        return;

    /* 检查拥塞状态 */
    if (atomic_read(&wb->congestion))
        wbt_estimate_latency(wb);
}
```

### 6.2 延迟估算

```c
/**
 * wbt_estimate_latency - 估算写回延迟
 *
 * 使用指数移动平均估算：
 * latency = α * new_sample + (1-α) * old_latency
 */
static void wbt_estimate_latency(struct rq_wb *wb)
{
    struct wb_stat *s = get_wb_stat(wb);
    unsigned long lat;

    /* 计算平均延迟 */
    lat = wb->latency;

    /* 更新拥塞状态 */
    if (lat > wb->max_lat_nsec)
        atomic_set(&wb->congestion, 1);
    else if (lat < wb->min_lat_nsec)
        atomic_set(&wb->congestion, 0);
}
```

## 7. blk-cgroup 资源控制

### 7.1 cgroup 集成架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    blk-cgroup Architecture                            │
│                                                                     │
│  ┌─────────────────┐                                                │
│  │   blkcg_gq      │  ←  每个 cgroup + 设备一个实例                  │
│  │  (blkio_group) │                                                │
│  └────────┬────────┘                                                │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐    ┌─────────────────┐                        │
│  │   blkg_policy_data │  │  blkg_rw_stat   │                        │
│  │   (per-policy)    │  │  (读写统计)      │                        │
│  └────────┬────────┘    └─────────────────┘                        │
│           │                                                          │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │  throtl_data     │  ←  I/O 限流策略                              │
│  │  (节流)          │                                                │
│  └─────────────────┘                                                │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 I/O 带宽控制

```c
/**
 * struct throtl_data - 节流数据
 *
 * 使用令牌桶算法进行带宽控制
 */
struct throtl_data {
    /* 每设备每 cgroup 的限制 */
    struct throtl_grp *root_group;
    struct rq_stats   *stats;

    /* 读/写限制 */
    struct throtl_service_queue service_queue;

    /* 节流阈值 */
    unsigned long throtl_ts;             // 上次检查时间
};

/**
 * throtl_charge - 收费（扣除配额）
 * @tg: throtl group
 * @bytes: 字节数
 * @rw: 读写方向
 */
static bool throtl_charge(struct throtl_grp *tg, unsigned int bytes,
                         struct blkg_policy_data *pd)
{
    struct throtl_data *td = pd_to_td(pd);

    /* 检查是否超过限制 */
    if (tg->bytes[READ] + bytes > tg->bps[READ] * LIMIT_WINDOW)
        return false;

    if (tg->bytes[WRITE] + bytes > tg->bps[WRITE] * LIMIT_WINDOW)
        return false;

    /* 扣除配额 */
    tg->bytes[READ] += bytes;
    tg->bytes[WRITE] += bytes;
    return true;
}
```

## 8. 核心算法分析

### 8.1 调度算法复杂度

| 调度器 | 入队复杂度 | 取出复杂度 | 空间复杂度 |
|--------|-----------|-----------|-----------|
| noop | O(1) | O(1) | O(n) |
| deadline | O(log n) | O(1)* | O(n) |
| cfq | O(log n) | O(1) | O(n) |
| bfq | O(log n) | O(log n) | O(n) |
| mq-deadline | O(log n) | O(1)* | O(n) |

*注：到期检查是 O(1)，但排序队列取出是 O(log n)

### 8.2 合并算法

```c
/*
 * 合并窗口算法：
 *
 * bio 可以合并到 request 的条件：
 * 1. 扇区连续：bio_sector == rq->sector + rq->nr_sectors (后合并)
 * 2. 扇区连续：bio_sector + bio_sectors == rq->sector (前合并)
 * 3. 类型相同：都是读或都是写
 * 4. 标志兼容：没有冲突的标志
 *
 * 合并收益：
 * - 减少硬件命令数量
 * - 提高顺序性，提升磁盘吞吐量
 */
```

### 8.3 内存屏障与并发

```c
/*
 * blk-mq 关键内存序：
 *
 * 1. request 分配：
 *    - 标签分配使用 per-cpu 缓存
 *    - 释放使用 RCU 延迟
 *
 * 2. dispatch 队列：
 *    - 使用 spinlock 保护
 *    - 派发时内存屏障确保请求可见
 *
 * 3. 完成回调：
 *    - bio_endio 可能在中断上下文
 *    - 需要适当的内存屏障
 */
```

## 9. 参考资料

- `block/blk-mq.c` - 多队列块层实现
- `block/blk-core.c` - 块层核心
- `block/elevator.c` - I/O 调度器框架
- `block/cfq-iosched.c` - CFQ 调度器
- `block/mq-deadline.c` - Deadline 调度器
- `block/bfq-iosched.c` - BFQ 调度器
- `include/linux/blkdev.h` - 块设备接口
- `include/linux/blk-mq.h` - blk-mq 接口
- `include/linux/blk-cgroup.h` - cgroup 接口
- Documentation/block/
- "Linux Block I/O Layer" - kernel documentation
