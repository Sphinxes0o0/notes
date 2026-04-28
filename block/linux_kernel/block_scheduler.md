# Linux 内核块I/O调度器框架分析

## 1. 概述

Linux内核的块I/O调度器框架（Elevator Framework）是内核子系统，负责对块设备上的I/O请求进行排序和调度，以优化磁盘吞吐量和响应时间。

### 核心文件

| 文件 | 路径 | 描述 |
|------|------|------|
| elevator.h | block/elevator.h | 核心数据结构和接口定义 |
| elevator.c | block/elevator.c | 调度器框架核心实现 |
| blk-mq-sched.c | block/blk-mq-sched.c | blk-mq调度框架 |
| mq-deadline.c | block/mq-deadline.c | deadline调度器实现 |
| bfq-iosched.c | block/bfq-iosched.c | BFQ调度器实现 |

---

## 2. 核心数据结构

### 2.1 struct elevator_type

**文件**: `/Users/sphinx/github/linux/block/elevator.h`
**行号**: 97-119

```c
struct elevator_type
{
    /* managed by elevator core */
    struct kmem_cache *icq_cache;

    /* fields provided by elevator implementation */
    struct elevator_mq_ops ops;  // 调度器操作函数集

    size_t icq_size;            /* see iocontext.h */
    size_t icq_align;           /* ditto */
    const struct elv_fs_entry *elevator_attrs;
    const char *elevator_name;  // 调度器名称，如 "bfq", "mq-deadline"
    const char *elevator_alias; // 别名，如 "deadline"
    struct module *elevator_owner;
#ifdef CONFIG_BLK_DEBUG_FS
    const struct blk_mq_debugfs_attr *queue_debugfs_attrs;
    const struct blk_mq_debugfs_attr *hctx_debugfs_attrs;
#endif

    /* managed by elevator core */
    char icq_cache_name[ELV_NAME_MAX + 6];
    struct list_head list;
};
```

### 2.2 struct elevator_mq_ops

**文件**: `/Users/sphinx/github/linux/block/elevator.h`
**行号**: 57-84

```c
struct elevator_mq_ops {
    int (*init_sched)(struct request_queue *, struct elevator_queue *);  // 初始化调度器
    void (*exit_sched)(struct elevator_queue *);                        // 退出调度器
    int (*init_hctx)(struct blk_mq_hw_ctx *, unsigned int);             // 初始化硬件队列
    void (*exit_hctx)(struct blk_mq_hw_ctx *, unsigned int);            // 退出硬件队列
    void (*depth_updated)(struct request_queue *);                      // 深度更新
    void *(*alloc_sched_data)(struct request_queue *);                  // 分配调度数据
    void (*free_sched_data)(void *);                                   // 释放调度数据

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
    struct request *(*dispatch_request)(struct blk_mq_hw_ctx *);  // 分发请求 - 核心函数
    bool (*has_work)(struct blk_mq_hw_ctx *);
    void (*completed_request)(struct request *, u64);
    void (*requeue_request)(struct request *);
    struct request *(*former_request)(struct request_queue *, struct request *);
    struct request *(*next_request)(struct request_queue *, struct request *);
    void (*init_icq)(struct io_cq *);
    void (*exit_icq)(struct io_cq *);
};
```

### 2.3 struct elevator_queue

**文件**: `/Users/sphinx/github/linux/block/elevator.h`
**行号**: 146-155

```c
struct elevator_queue
{
    struct elevator_type *type;     // 调度器类型
    struct elevator_tags *et;       // 调度器标签
    void *elevator_data;           // 调度器私有数据
    struct kobject kobj;
    struct mutex sysfs_lock;
    unsigned long flags;
    DECLARE_HASHTABLE(hash, ELV_HASH_BITS);
};
```

---

## 3. Elevator框架与Block层挂钩

### 3.1 调度器初始化流程

**文件**: `/Users/sphinx/github/linux/block/elevator.c`
**行号**: 729-760 (elevator_set_default)

```c
void elevator_set_default(struct request_queue *q)
{
    struct elv_change_ctx ctx = {
        .name = "mq-deadline",  // 默认调度器
        .no_uevent = true,
    };
    // ...
    ctx.type = elevator_find_get(ctx.name);
    if ((q->nr_hw_queues == 1 ||
            blk_mq_is_shared_tags(q->tag_set->flags))) {
        err = elevator_change(q, &ctx);
        // ...
    }
}
```

### 3.2 调度器切换

**文件**: `/Users/sphinx/github/linux/block/elevator.c`
**行号**: 562-607

```c
static int elevator_switch(struct request_queue *q, struct elv_change_ctx *ctx)
{
    struct elevator_type *new_e = NULL;
    
    WARN_ON_ONCE(q->mq_freeze_depth == 0);
    lockdep_assert_held(&q->elevator_lock);

    if (strncmp(ctx->name, "none", 4)) {
        new_e = elevator_find_get(ctx->name);  // 获取调度器类型
        if (!new_e)
            return -EINVAL;
    }

    blk_mq_quiesce_queue(q);

    if (q->elevator) {
        ctx->old = q->elevator;
        elevator_exit(q);  // 退出旧调度器
    }

    if (new_e) {
        ret = blk_mq_init_sched(q, new_e, &ctx->res);  // 初始化新调度器
        // ...
    } else {
        // "none"调度器 - 直接走软件队列，无排序
        blk_queue_flag_clear(QUEUE_FLAG_SQ_SCHED, q);
        q->elevator = NULL;
        q->nr_requests = q->tag_set->queue_depth;
        q->async_depth = q->tag_set->queue_depth;
    }
    // ...
}
```

### 3.3 blk_mq调度框架主分发函数

**文件**: `/Users/sphinx/github/linux/block/blk-mq-sched.c`
**行号**: 268-315

```c
static int __blk_mq_sched_dispatch_requests(struct blk_mq_hw_ctx *hctx)
{
    bool need_dispatch = false;
    LIST_HEAD(rq_list);

    // 1. 首先处理已在dispatch list上的请求
    if (!list_empty_careful(&hctx->dispatch)) {
        spin_lock(&hctx->lock);
        if (!list_empty(&hctx->dispatch))
            list_splice_init(&hctx->dispatch, &rq_list);
        spin_unlock(&hctx->lock);
    }

    // 2. 如果有残留请求，分发之
    if (!list_empty(&rq_list)) {
        blk_mq_sched_mark_restart_hctx(hctx);
        if (!blk_mq_dispatch_rq_list(hctx, &rq_list, true))
            return 0;
        need_dispatch = true;
    } else {
        need_dispatch = hctx->dispatch_busy;
    }

    // 3. 调用调度器的dispatch_request
    if (hctx->queue->elevator)
        return blk_mq_do_dispatch_sched(hctx);  // 有调度器

    // 4. 无调度器时直接走软件队列
    if (need_dispatch)
        return blk_mq_do_dispatch_ctx(hctx);
    blk_mq_flush_busy_ctxs(hctx, &rq_list);
    blk_mq_dispatch_rq_list(hctx, &rq_list, true);
    return 0;
}
```

---

## 4. mq-deadline调度器

**文件**: `/Users/sphinx/github/linux/block/mq-deadline.c`

### 4.1 核心数据结构

```c
// 行号: 73-79
struct dd_per_prio {
    struct rb_root sort_list[DD_DIR_COUNT];   // 按sector排序的红黑树
    struct list_head fifo_list[DD_DIR_COUNT]; // 按FIFO时间排序的链表
    sector_t latest_pos[DD_DIR_COUNT];         // 最近分发的位置
    struct io_stats_per_prio stats;
};

// 行号: 81-104
struct deadline_data {
    struct list_head dispatch;              // 待分发队列
    struct dd_per_prio per_prio[DD_PRIO_COUNT];  // 3种优先级: RT, BE, IDLE

    enum dd_data_dir last_dir;              // 上次分发的方向
    unsigned int batching;                  // 连续批次计数
    unsigned int starved;                   // 读饥饿计数

    int fifo_expire[DD_DIR_COUNT];         // 过期时间
    int fifo_batch;
    int writes_starved;
    int front_merges;
    int prio_aging_expire;

    spinlock_t lock;
};
```

### 4.2 deadline调度器注册

**文件**: `/Users/sphinx/github/linux/block/mq-deadline.c`
**行号**: 985-1012

```c
static struct elevator_type mq_deadline = {
    .ops = {
        .depth_updated      = dd_depth_updated,
        .limit_depth        = dd_limit_depth,
        .insert_requests   = dd_insert_requests,
        .dispatch_request   = dd_dispatch_request,   // 核心分发函数
        .prepare_request    = dd_prepare_request,
        .finish_request     = dd_finish_request,
        .next_request       = elv_rb_latter_request,
        .former_request     = elv_rb_former_request,
        .bio_merge          = dd_bio_merge,
        .request_merge      = dd_request_merge,
        .requests_merged    = dd_merged_requests,
        .request_merged     = dd_request_merged,
        .has_work           = dd_has_work,
        .init_sched         = dd_init_sched,
        .exit_sched         = dd_exit_sched,
    },
    .elevator_attrs = deadline_attrs,
    .elevator_name = "mq-deadline",
    .elevator_alias = "deadline",
    .elevator_owner = THIS_MODULE,
};
```

### 4.3 deadline_dispatch_requests() - 分发请求

**文件**: `/Users/sphinx/github/linux/block/mq-deadline.c`
**行号**: 452-486

```c
static struct request *dd_dispatch_request(struct blk_mq_hw_ctx *hctx)
{
    struct deadline_data *dd = hctx->queue->elevator->elevator_data;
    const unsigned long now = jiffies;
    struct request *rq;
    enum dd_prio prio;

    spin_lock(&dd->lock);

    // 1. 优先处理已标记分发的请求
    if (!list_empty(&dd->dispatch)) {
        rq = list_first_entry(&dd->dispatch, struct request, queuelist);
        list_del_init(&rq->queuelist);
        dd_start_request(dd, rq_data_dir(rq), rq);
        goto unlock;
    }

    // 2. 检查优先级老化请求
    rq = dd_dispatch_prio_aged_requests(dd, now);
    if (rq)
        goto unlock;

    // 3. 按优先级顺序分发请求
    for (prio = 0; prio <= DD_PRIO_MAX; prio++) {
        rq = __dd_dispatch_request(dd, &dd->per_prio[prio], now);
        if (rq || dd_queued(dd, prio))
            break;
    }

unlock:
    spin_unlock(&dd->lock);
    return rq;
}
```

### 4.4 __dd_dispatch_request() - 实际选择请求

**文件**: `/Users/sphinx/github/linux/block/mq-deadline.c`
**行号**: 325-414

```c
static struct request *__dd_dispatch_request(struct deadline_data *dd,
                         struct dd_per_prio *per_prio,
                         unsigned long latest_start)
{
    struct request *rq, *next_rq;
    enum dd_data_dir data_dir;

    lockdep_assert_held(&dd->lock);

    // 1. 批次处理：继续分发同一方向的请求
    rq = deadline_next_request(dd, per_prio, dd->last_dir);
    if (rq && dd->batching < dd->fifo_batch) {
        data_dir = rq_data_dir(rq);
        goto dispatch_request;
    }

    // 2. 选择数据方向（读或写）
    if (!list_empty(&per_prio->fifo_list[DD_READ])) {
        if (deadline_fifo_request(dd, per_prio, DD_WRITE) &&
            (dd->starved++ >= dd->writes_starved))
            goto dispatch_writes;
        data_dir = DD_READ;
        goto dispatch_find_request;
    }

    if (!list_empty(&per_prio->fifo_list[DD_WRITE])) {
dispatch_writes:
        dd->starved = 0;
        data_dir = DD_WRITE;
        goto dispatch_find_request;
    }

    return NULL;

dispatch_find_request:
    // 3. 查找最佳请求
    next_rq = deadline_next_request(dd, per_prio, data_dir);
    if (deadline_check_fifo(per_prio, data_dir) || !next_rq) {
        // 过期或无更高sector请求，从FIFO取最早的
        rq = deadline_fifo_request(dd, per_prio, data_dir);
    } else {
        // 继续从当前位置分发
        rq = next_rq;
    }

    if (!rq)
        return NULL;

    dd->last_dir = data_dir;
    dd->batching = 0;

dispatch_request:
    if (started_after(dd, rq, latest_start))
        return NULL;

    dd->batching++;
    deadline_move_request(dd, per_prio, rq);
    return dd_start_request(dd, data_dir, rq);
}
```

### 4.5 deadline算法特点

1. **per-device queues**: 所有硬件队列共享同一个deadline_data结构
2. **三种优先级**: RT (实时), BE (最佳效果), IDLE (空闲)
3. **读写分离**: 读请求默认优先，写请求可配置饥饿上限
4. **过期机制**: 基于FIFO时间的过期检查，确保延迟 bound
5. **Sector排序**: 红黑树按sector位置排序，优化磁盘寻道

---

## 5. BFQ (Budget Fair Queueing) 调度器

**文件**: `/Users/sphinx/github/linux/block/bfq-iosched.c`

### 5.1 调度器注册

**文件**: `/Users/sphinx/github/linux/block/bfq-iosched.c`
**行号**: 7593-7620

```c
static struct elevator_type iosched_bfq_mq = {
    .ops = {
        .limit_depth         = bfq_limit_depth,
        .prepare_request     = bfq_prepare_request,
        .requeue_request     = bfq_finish_requeue_request,
        .finish_request      = bfq_finish_request,
        .exit_icq            = bfq_exit_icq,
        .insert_requests     = bfq_insert_requests,
        .dispatch_request    = bfq_dispatch_request,  // 核心分发
        .next_request        = elv_rb_latter_request,
        .former_request      = elv_rb_former_request,
        .allow_merge         = bfq_allow_bio_merge,
        .bio_merge           = bfq_bio_merge,
        .request_merge       = bfq_request_merge,
        .requests_merged     = bfq_requests_merged,
        .request_merged      = bfq_request_merged,
        .has_work            = bfq_has_work,
        .depth_updated       = bfq_depth_updated,
        .init_sched          = bfq_init_queue,
        .exit_sched          = bfq_exit_queue,
    },
    .icq_size = sizeof(struct bfq_io_cq),
    .icq_align = __alignof__(struct bfq_io_cq),
    .elevator_attrs = bfq_attrs,
    .elevator_name = "bfq",
    .elevator_owner = THIS_MODULE,
};
```

### 5.2 bfq_dispatch_request()

**文件**: `/Users/sphinx/github/linux/block/bfq-iosched.c`
**行号**: 5297-5321

```c
static struct request *bfq_dispatch_request(struct blk_mq_hw_ctx *hctx)
{
    struct bfq_data *bfqd = hctx->queue->elevator->elevator_data;
    struct request *rq;
    struct bfq_queue *in_serv_queue;
    bool waiting_rq, idle_timer_disabled = false;

    spin_lock_irq(&bfqd->lock);

    in_serv_queue = bfqd->in_service_queue;
    waiting_rq = in_serv_queue && bfq_bfqq_wait_request(in_serv_queue);

    rq = __bfq_dispatch_request(hctx);  // 调用实际分发逻辑
    if (in_serv_queue == bfqd->in_service_queue) {
        idle_timer_disabled =
            waiting_rq && !bfq_bfqq_wait_request(in_serv_queue);
    }

    spin_unlock_irq(&bfqd->lock);
    bfq_update_dispatch_stats(hctx->queue, rq,
            idle_timer_disabled ? in_serv_queue : NULL,
                idle_timer_disabled);

    return rq;
}
```

### 5.3 __bfq_dispatch_request() - 实际分发

**文件**: `/Users/sphinx/github/linux/block/bfq-iosched.c`
**行号**: 5156-5243

```c
static struct request *__bfq_dispatch_request(struct blk_mq_hw_ctx *hctx)
{
    struct bfq_data *bfqd = hctx->queue->elevator->elevator_data;
    struct request *rq = NULL;
    struct bfq_queue *bfqq = NULL;

    // 1. 优先处理已在dispatch队列的请求
    if (!list_empty(&bfqd->dispatch)) {
        rq = list_first_entry(&bfqd->dispatch, struct request, queuelist);
        list_del_init(&rq->queuelist);
        bfqq = RQ_BFQQ(rq);
        if (bfqq) {
            bfqq->dispatched++;
            goto inc_in_driver_start_rq;
        }
        goto start_rq;
    }

    // 2. 无忙碌队列则退出
    if (bfq_tot_busy_queues(bfqd) == 0)
        goto exit;

    // 3. 严格保证模式下单请求
    if (bfqd->strict_guarantees && bfqd->tot_rq_in_driver > 0)
        goto exit;

    // 4. 选择队列
    bfqq = bfq_select_queue(bfqd);
    if (!bfqq)
        goto exit;

    // 5. 从选中的队列分发请求
    rq = bfq_dispatch_rq_from_bfqq(bfqd, bfqq);

    if (rq) {
inc_in_driver_start_rq:
        bfqd->rq_in_driver[bfqq->actuator_idx]++;
        bfqd->tot_rq_in_driver++;
start_rq:
        rq->rq_flags |= RQF_STARTED;
    }
exit:
    return rq;
}
```

### 5.4 bfq_select_queue() - 队列选择

**文件**: `/Users/sphinx/github/linux/block/bfq-iosched.c`
**行号**: 4798-5040

```c
static struct bfq_queue *bfq_select_queue(struct bfq_data *bfqd)
{
    struct bfq_queue *bfqq, *inject_bfqq;
    struct request *next_rq;
    enum bfqq_expiration reason = BFQQE_BUDGET_TIMEOUT;

    bfqq = bfqd->in_service_queue;
    if (!bfqq)
        goto new_queue;

    // 检查是否需要过期当前队列
    if (bfq_may_expire_for_budg_timeout(bfqq) &&
        !bfq_bfqq_must_idle(bfqq))
        goto expire;

    // 检查是否需要注入
    inject_bfqq = bfq_find_bfqq_for_underused_actuator(bfqd);
    if (inject_bfqq && inject_bfqq != bfqq)
        return inject_bfqq;

    next_rq = bfqq->next_rq;
    
    // 有足够budget则继续服务
    if (next_rq) {
        if (bfq_serv_to_charge(next_rq, bfqq) >
            bfq_bfqq_budget_left(bfqq)) {
            reason = BFQQE_BUDGET_EXHAUSTED;
            goto expire;
        } else {
            // 禁用idle timer
            if (bfq_bfqq_wait_request(bfqq)) {
                bfq_clear_bfqq_wait_request(bfqq);
                hrtimer_try_to_cancel(&bfqd->idle_slice_timer);
            }
            goto keep_queue;
        }
    }

    // 无请求时检查是否应该idle
    if (bfq_bfqq_wait_request(bfqq) ||
        (bfqq->dispatched != 0 && bfq_better_to_idle(bfqq))) {
        // 处理waker队列、同步IO注入等
        // ...
        return bfqq;  // 保持当前队列
    }

expire:
    // 过期当前队列，选择新队列
    bfq_bfqq_expire(bfqd, bfqq, reason);

new_queue:
    // 选择新队列（基于公平、权重）
    bfqq = bfq_select_queue(bfqd);
    // ...
}
```

### 5.5 BFQ算法特点

1. **预算公平队列**: 每个队列有预算(budget)，按预算比例分配带宽
2. **多Actuator支持**: 支持多执行器NVMe设备
3. **队列层次结构**: 支持cgroup集成(BFQ_GROUP_IOSCHED)
4. **设备空闲**: 支持设备idle以省电
5. **注入机制**: 可从其他队列注入请求以提高吞吐量
6. **严格保证模式**: 单请求模式确保调度顺序

---

## 6. none (noop) 调度器

**文件**: `/Users/sphinx/github/linux/block/elevator.c`

"none"调度器实际上不是一个真正的调度器，而是一种禁用调度的模式。

### 6.1 none模式处理

**文件**: `/Users/sphinx/github/linux/block/elevator.c`
**行号**: 570-594

```c
static int elevator_switch(struct request_queue *q, struct elv_change_ctx *ctx)
{
    // ...
    if (strncmp(ctx->name, "none", 4)) {
        new_e = elevator_find_get(ctx->name);
        if (!new_e)
            return -EINVAL;
    }
    // ...
    if (new_e) {
        ret = blk_mq_init_sched(q, new_e, &ctx->res);
        if (ret)
            goto out_unfreeze;
        ctx->new = q->elevator;
    } else {
        // "none"模式：清除调度标志，不使用elevator
        blk_queue_flag_clear(QUEUE_FLAG_SQ_SCHED, q);
        q->elevator = NULL;  // 无调度器
        q->nr_requests = q->tag_set->queue_depth;
        q->async_depth = q->tag_set->queue_depth;
    }
    // ...
}
```

### 6.2 无调度器时的分发路径

**文件**: `/Users/sphinx/github/linux/block/blk-mq-sched.c`
**行号**: 306-314

```c
if (hctx->queue->elevator)
    return blk_mq_do_dispatch_sched(hctx);

// 无调度器时直接走软件队列轮询
if (need_dispatch)
    return blk_mq_do_dispatch_ctx(hctx);
blk_mq_flush_busy_ctxs(hctx, &rq_list);
blk_mq_dispatch_rq_list(hctx, &rq_list, true);
```

---

## 7. 调度算法对比

| 特性 | mq-deadline | bfq | none |
|------|-------------|-----|------|
| **调度策略** | 过期时间 + Sector排序 | 预算公平 | 无（ FIFO） |
| **优先级** | 3级(RT/BE/IDLE) | 多级(cgroup) | 无 |
| **延迟保证** | 有(基于过期) | 有(基于预算) | 无 |
| **吞吐量优化** | 顺序读写 | 公平带宽 | 最大吞吐量 |
| **适用场景** | 通用、SSD、NVMe | 桌面、交互、低延迟 | 高速存储、直接访问 |

---

## 8. 关键函数调用关系

```
blk_mq_sched_dispatch_requests()      [blk-mq-sched.c:317]
  └── __blk_mq_sched_dispatch_requests()  [blk-mq-sched.c:268]
        ├── list_splice_init(&hctx->dispatch)  // 处理已分发队列
        └── blk_mq_do_dispatch_sched()    [blk-mq-sched.c:176]
              └── __blk_mq_do_dispatch_sched()  [blk-mq-sched.c:85]
                    └── e->type->ops.dispatch_request()  // 调用调度器分发
                          ├── dd_dispatch_request()      [mq-deadline.c:452]
                          │     ├── dd_dispatch_prio_aged_requests()
                          │     └── __dd_dispatch_request()
                          │           ├── deadline_fifo_request()
                          │           ├── deadline_next_request()
                          │           └── deadline_check_fifo()
                          │
                          └── bfq_dispatch_request()      [bfq-iosched.c:5297]
                                └── __bfq_dispatch_request()
                                      ├── bfq_select_queue()
                                      └── bfq_dispatch_rq_from_bfqq()
```

---

## 9. 参考文档

- `/Users/sphinx/github/linux/block/elevator.h` - 核心结构定义
- `/Users/sphinx/github/linux/block/elevator.c` - 框架实现
- `/Users/sphinx/github/linux/block/blk-mq-sched.c` - blk-mq调度框架
- `/Users/sphinx/github/linux/block/mq-deadline.c` - Deadline调度器
- `/Users/sphinx/github/linux/block/bfq-iosched.c` - BFQ调度器
- Documentation/block/deadline-iosched.rst
