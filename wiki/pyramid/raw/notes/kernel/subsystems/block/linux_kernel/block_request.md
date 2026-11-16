# Linux 内核 Block Layer 请求处理路径分析

## 1. 概述

Linux 内核 Block Layer 负责处理块设备 I/O 请求，其核心流程为：

```
bio_alloc() → submit_bio() → make_request_fn → request → dispatch → completion
```

### 1.1 关键源文件

| 文件路径 | 功能 |
|---------|------|
| `block/blk-core.c` | Block Layer 核心函数 |
| `block/blk-mq.c` | Multi-queue Block Layer 实现 |
| `block/blk-mq-sched.c` | I/O Scheduler 接口 |
| `block/blk-flush.c` | Flush 请求处理 |
| `block/blk-mq.h` | blk-mq 核心数据结构 |

---

## 2. bio 到 request 的转换

### 2.1 入口函数: `submit_bio_noacct()`

**文件**: `block/blk-core.c:728`

```c
void submit_bio_noacct_nocheck(struct bio *bio, bool split)
{
    blk_cgroup_bio_start(bio);

    if (!bio_flagged(bio, BIO_TRACE_COMPLETION)) {
        trace_block_bio_queue(bio);
        bio_set_flag(bio, BIO_TRACE_COMPLETION);
    }

    // 如果当前在 bio_list 中, 追加到列表
    if (current->bio_list) {
        if (split)
            bio_list_add_head(&current->bio_list[0], bio);
        else
            bio_list_add(&current->bio_list[0], bio);
    } else if (!bdev_test_flag(bio->bi_bdev, BD_HAS_SUBMIT_BIO)) {
        // MQ 设备路径
        __submit_bio_noacct_mq(bio);
    } else {
        // 传统设备路径
        __submit_bio_noacct(bio);
    }
}
```

### 2.2 `__submit_bio_noacct_mq()` - MQ 设备的 bio 提交

**文件**: `block/blk-core.c:715-726`

```c
static void __submit_bio_noacct_mq(struct bio *bio)
{
    struct bio_list bio_list[2] = { };

    current->bio_list = bio_list;

    do {
        __submit_bio(bio);  // 实际处理每个 bio
    } while ((bio = bio_list_pop(&bio_list[0])));

    current->bio_list = NULL;
}
```

### 2.3 `__submit_bio()` - bio 核心处理

**文件**: `block/blk-core.c:627-650`

```c
static void __submit_bio(struct bio *bio)
{
    /* 如果没有使用 plug, 在这里添加 plug 以缓存时间 */
    struct blk_plug plug;

    blk_start_plug(&plug);

    if (!bdev_test_flag(bio->bi_bdev, BD_HAS_SUBMIT_BIO)) {
        // MQ 设备: 调用 blk_mq_submit_bio()
        blk_mq_submit_bio(bio);
    } else if (likely(bio_queue_enter(bio) == 0)) {
        struct gendisk *disk = bio->bi_bdev->bd_disk;
    
        if ((bio->bi_opf & REQ_POLLED) &&
            !(disk->queue->limits.features & BLK_FEAT_POLL)) {
            bio->bi_status = BLK_STS_NOTSUPP;
            bio_endio(bio);
        } else {
            disk->fops->submit_bio(bio);  // 调用设备的 submit_bio
        }
        blk_queue_exit(disk->queue);
    }

    blk_finish_plug(&plug);
}
```

### 2.4 `blk_mq_submit_bio()` - MQ 设备的核心提交函数

**文件**: `block/blk-mq.c:3141-3264`

这是 bio 转换为 request 的核心函数:

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

    // 1. 检查 plug 中是否有缓存的 request
    rq = blk_mq_peek_cached_request(plug, q, bio->bi_opf);

    // 2. Zone write plugging 特殊处理
    if (bio_zone_write_plugging(bio)) {
        nr_segs = bio->__bi_nr_segments;
        if (rq)
            blk_queue_exit(q);
        goto new_request;
    }

    // 3. 获取队列引用计数
    if (!rq) {
        if (unlikely(bio_queue_enter(bio)))
            return;
    }

    // 4. 对齐检查和 poll 支持检查
    if (unlikely(bio_unaligned(bio, q))) {
        bio_io_error(bio);
        goto queue_exit;
    }

    if ((bio->bi_opf & REQ_POLLED) && !blk_mq_can_poll(q)) {
        bio->bi_status = BLK_STS_NOTSUPP;
        bio_endio(bio);
        goto queue_exit;
    }

    // 5. 分割 bio 以符合限制
    bio = __bio_split_to_limits(bio, &q->limits, &nr_segs);
    if (!bio)
        goto queue_exit;

    // 6. 完整性预检
    if (!bio_integrity_prep(bio))
        goto queue_exit;

    // 7. 初始化 bio 发行统计
    blk_mq_bio_issue_init(q, bio);

    // 8. 尝试与现有 request 合并
    if (blk_mq_attempt_bio_merge(q, bio, nr_segs))
        goto queue_exit;

    // 9. Zone write plugging 处理
    if (bio_needs_zone_write_plugging(bio)) {
        if (blk_zone_plug_bio(bio, nr_segs))
            goto queue_exit;
    }

new_request:
    // 10. 使用缓存的 request 或分配新的 request
    if (rq) {
        blk_mq_use_cached_rq(rq, plug, bio);
    } else {
        rq = blk_mq_get_new_requests(q, plug, bio);
        if (unlikely(!rq)) {
            if (bio->bi_opf & REQ_NOWAIT)
                bio_wouldblock_error(bio);
            goto queue_exit;
        }
    }

    trace_block_getrq(bio);
    rq_qos_track(q, rq, bio);

    // 11. 将 bio 转换为 request 结构
    blk_mq_bio_to_request(rq, bio, nr_segs);

    // 12. 加密密钥槽获取
    ret = blk_crypto_rq_get_keyslot(rq);
    if (ret != BLK_STS_OK) {
        bio->bi_status = ret;
        bio_endio(bio);
        blk_mq_free_request(rq);
        return;
    }

    // 13. Zone write plug 初始化
    if (bio_zone_write_plugging(bio))
        blk_zone_write_plug_init_request(rq);

    // 14. Flush 请求处理
    if (op_is_flush(bio->bi_opf) && blk_insert_flush(rq))
        return;

    // 15. 如果有 plug, 将 request 加入 plug 队列
    if (plug) {
        blk_add_rq_to_plug(plug, rq);
        return;
    }

    // 16. 没有 plug 时, 直接发行或插入调度器
    hctx = rq->mq_hctx;
    if ((rq->rq_flags & RQF_USE_SCHED) ||
        (hctx->dispatch_busy && (q->nr_hw_queues == 1 || !is_sync))) {
        blk_mq_insert_request(rq, 0);
        blk_mq_run_hw_queue(hctx, true);
    } else {
        blk_mq_run_dispatch_ops(q, blk_mq_try_issue_directly(hctx, rq));
    }
    return;

queue_exit:
    if (!rq)
        blk_queue_exit(q);
}
```

### 2.5 `blk_mq_get_new_requests()` - 分配新 request

**文件**: `block/blk-mq.c:3046-3075`

```c
static struct request *blk_mq_get_new_requests(struct request_queue *q,
                       struct blk_plug *plug,
                       struct bio *bio)
{
    struct blk_mq_alloc_data data = {
        .q      = q,
        .flags  = 0,
        .shallow_depth = 0,
        .cmd_flags = bio->bi_opf,
        .rq_flags = 0,
        .nr_tags = 1,
        .cached_rqs = NULL,
        .ctx    = NULL,
        .hctx   = NULL
    };
    struct request *rq;

    rq_qos_throttle(q, bio);

    // 从 plug 获取批量分配的 request
    if (plug) {
        data.nr_tags = plug->nr_ios;
        plug->nr_ios = 1;
        data.cached_rqs = &plug->cached_rqs;
    }

    rq = __blk_mq_alloc_requests(&data);
    if (unlikely(!rq))
        rq_qos_cleanup(q, bio);
    return rq;
}
```

### 2.6 `blk_mq_bio_to_request()` - bio 结构转换

**文件**: `block/blk-mq.c:2685-2708`

```c
static void blk_mq_bio_to_request(struct request *rq, struct bio *bio,
        unsigned int nr_segs)
{
    int err;

    if (bio->bi_opf & REQ_RAHEAD)
        rq->cmd_flags |= REQ_FAILFAST_MASK;

    rq->bio = rq->biotail = bio;
    rq->__sector = bio->bi_iter.bi_sector;
    rq->__data_len = bio->bi_iter.bi_size;
    rq->phys_gap_bit = bio->bi_bvec_gap_bit;

    rq->nr_phys_segments = nr_segs;
    if (bio_integrity(bio))
        rq->nr_integrity_segments = blk_rq_count_integrity_sg(rq->q, bio);

    /* This can't fail, since GFP_NOIO includes __GFP_DIRECT_RECLAIM. */
    err = blk_crypto_rq_bio_prep(rq, bio, GFP_NOIO);
    WARN_ON_ONCE(err);

    blk_account_io_start(rq);
}
```

---

## 3. Plug 机制与请求批处理

### 3.1 `blk_start_plug()` - 启动 plug

**文件**: `block/blk-core.c:1178-1181`

```c
void blk_start_plug(struct blk_plug *plug)
{
    blk_start_plug_nr_ios(plug, 1);
}
```

### 3.2 `blk_add_rq_to_plug()` - 将 request 加入 plug

**文件**: `block/blk-mq.c:1408-1432`

```c
static void blk_add_rq_to_plug(struct blk_plug *plug, struct request *rq)
{
    struct request *last = rq_list_peek(&plug->mq_list);

    if (!plug->rq_count) {
        trace_block_plug(rq->q);
    } else if (plug->rq_count >= blk_plug_max_rq_count(plug) ||
           (!blk_queue_nomerges(rq->q) &&
            blk_rq_bytes(last) >= BLK_PLUG_FLUSH_SIZE)) {
        // 超过阈值, 刷新 plug
        blk_mq_flush_plug_list(plug, false);
        last = NULL;
        trace_block_plug(rq->q);
    }

    if (!plug->multiple_queues && last && last->q != rq->q)
        plug->multiple_queues = true;
    
    if (!plug->has_elevator && (rq->rq_flags & RQF_SCHED_TAGS))
        plug->has_elevator = true;
    
    rq_list_add_tail(&plug->mq_list, rq);
    plug->rq_count++;
}
```

**Plug 刷新条件**:
- `plug->rq_count >= BLK_MAX_REQUEST_COUNT * 2` (多队列) 或 `BLK_MAX_REQUEST_COUNT` (单队列)
- 或者 `blk_rq_bytes(last) >= BLK_PLUG_FLUSH_SIZE` (通常 128KB)

### 3.3 `blk_finish_plug()` - 完成 plug

**文件**: `block/blk-core.c:1254-1260`

```c
void blk_finish_plug(struct blk_plug *plug)
{
    if (plug == current->plug) {
        __blk_flush_plug(plug, false);
        current->plug = NULL;
    }
}
```

### 3.4 `__blk_flush_plug()` - 刷新 plug

**文件**: `block/blk-core.c:1226-1242`

```c
void __blk_flush_plug(struct blk_plug *plug, bool from_schedule)
{
    if (!list_empty(&plug->cb_list))
        flush_plug_callbacks(plug, from_schedule);
    
    // 调用 blk_mq_flush_plug_list 处理排队的 request
    blk_mq_flush_plug_list(plug, from_schedule);
    
    // 释放缓存的 request
    if (unlikely(!rq_list_empty(&plug->cached_rqs)))
        blk_mq_free_plug_rqs(plug);

    plug->cur_ktime = 0;
    current->flags &= ~PF_BLOCK_TS;
}
```

### 3.5 `blk_mq_flush_plug_list()` - 批量处理 plug 中的 request

**文件**: `block/blk-mq.c:2969-2999`

```c
void blk_mq_flush_plug_list(struct blk_plug *plug, bool from_schedule)
{
    unsigned int depth;

    if (plug->rq_count == 0)
        return;
    depth = plug->rq_count;
    plug->rq_count = 0;

    // 无 elevator 且非调度触发: 尝试直接发行
    if (!plug->has_elevator && !from_schedule) {
        if (plug->multiple_queues) {
            blk_mq_dispatch_multiple_queue_requests(&plug->mq_list);
            return;
        }
        blk_mq_dispatch_queue_requests(&plug->mq_list, depth);
        if (rq_list_empty(&plug->mq_list))
            return;
    }

    // 通过调度器分发
    do {
        blk_mq_dispatch_list(&plug->mq_list, from_schedule);
    } while (!rq_list_empty(&plug->mq_list));
}
```

---

## 4. Request 调度与分发

### 4.1 `blk_mq_run_hw_queue()` - 运行硬件队列

**文件**: `block/blk-mq.c:2352-2388`

```c
void blk_mq_run_hw_queue(struct blk_mq_hw_ctx *hctx, bool async)
{
    bool need_run;

    WARN_ON_ONCE(!async && in_interrupt());
    might_sleep_if(!async && hctx->flags & BLK_MQ_F_BLOCKING);

    need_run = blk_mq_hw_queue_need_run(hctx);
    if (!need_run) {
        unsigned long flags;
        spin_lock_irqsave(&hctx->queue->queue_lock, flags);
        need_run = blk_mq_hw_queue_need_run(hctx);
        spin_unlock_irqrestore(&hctx->queue->queue_lock, flags);
        if (!need_run)
            return;
    }

    if (async || !cpumask_test_cpu(raw_smp_processor_id(), hctx->cpumask)) {
        blk_mq_delay_run_hw_queue(hctx, 0);
        return;
    }

    // 同步执行调度分发
    blk_mq_run_dispatch_ops(hctx->queue,
                blk_mq_sched_dispatch_requests(hctx));
}
```

### 4.2 `blk_mq_sched_dispatch_requests()` - Scheduler 分发入口

**文件**: `block/blk-mq-sched.c:317-333`

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

### 4.3 `__blk_mq_sched_dispatch_requests()` - 实际分发逻辑

**文件**: `block/blk-mq-sched.c:268-315`

```c
static int __blk_mq_sched_dispatch_requests(struct blk_mq_hw_ctx *hctx)
{
    bool need_dispatch = false;
    LIST_HEAD(rq_list);

    // 1. 首先处理 hctx->dispatch 列表中的残留请求
    if (!list_empty_careful(&hctx->dispatch)) {
        spin_lock(&hctx->lock);
        if (!list_empty(&hctx->dispatch))
            list_splice_init(&hctx->dispatch, &rq_list);
        spin_unlock(&hctx->lock);
    }

    // 2. 根据情况决定是否需要从调度器取请求
    if (!list_empty(&rq_list)) {
        blk_mq_sched_mark_restart_hctx(hctx);
        if (!blk_mq_dispatch_rq_list(hctx, &rq_list, true))
            return 0;
        need_dispatch = true;
    } else {
        need_dispatch = hctx->dispatch_busy;
    }

    // 3. 有 elevator 时, 使用调度器分发
    if (hctx->queue->elevator)
        return blk_mq_do_dispatch_sched(hctx);

    // 4. 队列忙碌时从 sw queue 逐个取出
    if (need_dispatch)
        return blk_mq_do_dispatch_ctx(hctx);
    
    // 5. 刷新忙碌的 ctx 并分发
    blk_mq_flush_busy_ctxs(hctx, &rq_list);
    blk_mq_dispatch_rq_list(hctx, &rq_list, true);
    return 0;
}
```

### 4.4 `blk_mq_dispatch_rq_list()` - 分发请求到设备驱动

**文件**: `block/blk-mq.c:2116-2240`

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
        
        // 预处理检查
        prep = blk_mq_prep_dispatch_rq(rq, get_budget);
        if (prep != PREP_DISPATCH_OK)
            break;

        list_del_init(&rq->queuelist);

        bd.rq = rq;
        bd.last = list_empty(list);

        // 调用驱动的 queue_rq 回调
        ret = q->mq_ops->queue_rq(hctx, &bd);
        switch (ret) {
        case BLK_STS_OK:
            queued++;
            break;
        case BLK_STS_RESOURCE:
            needs_resource = true;
            fallthrough;
        case BLK_STS_DEV_RESOURCE:
            blk_mq_handle_dev_resource(rq, list);
            goto out;
        default:
            blk_mq_end_request(rq, ret);
        }
    } while (!list_empty(list));

out:
    if (!list_empty(list) || ret != BLK_STS_OK)
        blk_mq_commit_rqs(hctx, queued, false);

    // 将未完成的请求放回 dispatch 列表
    if (!list_empty(list)) {
        bool needs_restart;
        bool no_tag = prep == PREP_DISPATCH_NO_TAG &&
            ((hctx->flags & BLK_MQ_F_TAG_QUEUE_SHARED) ||
            blk_mq_is_shared_tags(hctx->flags));

        if (!get_budget)
            blk_mq_release_budgets(q, list);

        spin_lock(&hctx->lock);
        list_splice_tail_init(list, &hctx->dispatch);
        spin_unlock(&hctx->lock);

        smp_mb();
        // 检查是否需要重新启动队列
        if (test_bit(BLK_MQ_S_SCHED_RESTART, &hctx->state))
            needs_restart = true;
        else
            needs_restart = no_tag;

        if (needs_restart)
            blk_mq_run_hw_queue(hctx, true);
    }

    return queued > 0;
}
```

### 4.5 `blk_mq_try_issue_directly()` - 直接发送请求

**文件**: `block/blk-mq.c:2768-2798`

```c
static void blk_mq_try_issue_directly(struct blk_mq_hw_ctx *hctx,
        struct request *rq)
{
    blk_status_t ret;

    if (blk_mq_hctx_stopped(hctx) || blk_queue_quiesced(rq->q)) {
        blk_mq_insert_request(rq, 0);
        blk_mq_run_hw_queue(hctx, false);
        return;
    }

    // 需要调度或无法获取 budget/tag 时, 插入调度器
    if ((rq->rq_flags & RQF_USE_SCHED) || !blk_mq_get_budget_and_tag(rq)) {
        blk_mq_insert_request(rq, 0);
        blk_mq_run_hw_queue(hctx, rq->cmd_flags & REQ_NOWAIT);
        return;
    }

    ret = __blk_mq_issue_directly(hctx, rq, true);
    switch (ret) {
    case BLK_STS_OK:
        break;
    case BLK_STS_RESOURCE:
    case BLK_STS_DEV_RESOURCE:
        blk_mq_request_bypass_insert(rq, 0);
        blk_mq_run_hw_queue(hctx, false);
        break;
    default:
        blk_mq_end_request(rq, ret);
        break;
    }
}
```

---

## 5. Request 插入调度器

### 5.1 `blk_mq_insert_request()` - 插入请求到调度器或 sw queue

**文件**: `block/blk-mq.c:2623-2680`

```c
static void blk_mq_insert_request(struct request *rq, blk_insert_t flags)
{
    struct request_queue *q = rq->q;
    struct blk_mq_ctx *ctx = rq->mq_ctx;
    struct blk_mq_hw_ctx *hctx = rq->mq_hctx;

    if (blk_rq_is_passthrough(rq)) {
        // Passthrough 请求直接加入 dispatch 队列
        blk_mq_request_bypass_insert(rq, flags);
    } else if (req_op(rq) == REQ_OP_FLUSH) {
        // Flush 请求加入 dispatch 队列头部
        blk_mq_request_bypass_insert(rq, BLK_MQ_INSERT_AT_HEAD);
    } else if (q->elevator) {
        // 有 elevator 时, 调用调度器的 insert_requests
        LIST_HEAD(list);
        WARN_ON_ONCE(rq->tag != BLK_MQ_NO_TAG);
        list_add(&rq->queuelist, &list);
        q->elevator->type->ops.insert_requests(hctx, &list, flags);
    } else {
        // 无 elevator 时, 加入 ctx 的 rq_lists
        trace_block_rq_insert(rq);
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

---

## 6. Flush 请求处理

### 6.1 `blk_insert_flush()` - 处理 flush 请求

**文件**: `block/blk-flush.c:384-454`

```c
bool blk_insert_flush(struct request *rq)
{
    struct request_queue *q = rq->q;
    struct blk_flush_queue *fq = blk_get_flush_queue(rq->mq_ctx);
    bool supports_fua = q->limits.features & BLK_FEAT_FUA;
    unsigned int policy = 0;

    /* FLUSH/FUA 请求不能合并 */
    WARN_ON_ONCE(rq->bio != rq->biotail);

    if (blk_rq_sectors(rq))
        policy |= REQ_FSEQ_DATA;

    // 检查需要的 flush 操作
    if (blk_queue_write_cache(q)) {
        if (rq->cmd_flags & REQ_PREFLUSH)
            policy |= REQ_FSEQ_PREFLUSH;
        if ((rq->cmd_flags & REQ_FUA) && !supports_fua)
            policy |= REQ_FSEQ_POSTFLUSH;
    }

    // 清除驱动不需要的标志
    rq->cmd_flags &= ~REQ_PREFLUSH;
    if (!supports_fua)
        rq->cmd_flags &= ~REQ_FUA;
    rq->cmd_flags |= REQ_SYNC;

    switch (policy) {
    case 0:
        // 空 flush, 直接完成
        blk_mq_end_request(rq, 0);
        return true;
    case REQ_FSEQ_DATA:
        // 有数据但不需要 flush, 正常处理
        return false;
    case REQ_FSEQ_DATA | REQ_FSEQ_POSTFLUSH:
        // 需要 post flush, 初始化 flush 字段
        blk_rq_init_flush(rq);
        rq->flush.seq |= REQ_FSEQ_PREFLUSH;
        spin_lock_irq(&fq->mq_flush_lock);
        fq->flush_data_in_flight++;
        spin_unlock_irq(&fq->mq_flush_lock);
        return false;
    default:
        // 启动 flush 状态机
        blk_rq_init_flush(rq);
        rq->flush.seq = REQ_FSEQ_PREFLUSH | REQ_FSEQ_DATA |
                REQ_FSEQ_POSTFLUSH;
        spin_lock_irq(&fq->mq_flush_lock);
        list_add_tail(&rq->queuelist, &fq->flush_queue);
        fq->flush_pending++;
        spin_unlock_irq(&fq->mq_flush_lock);
        blk_mq_delay_run_hw_queue(hctx, 0);
        return true;
    }
}
```

---

## 7. Request 完成处理

### 7.1 `blk_mq_complete_request()` - 完成请求入口

**文件**: `block/blk-mq.c:1353-1358`

```c
void blk_mq_complete_request(struct request *rq)
{
    if (!blk_mq_complete_request_remote(rq))
        rq->q->mq_ops->complete(rq);
}
```

### 7.2 `blk_mq_complete_request_remote()` - 远程完成

**文件**: `block/blk-mq.c:1319-1343`

```c
bool blk_mq_complete_request_remote(struct request *rq)
{
    WRITE_ONCE(rq->state, MQ_RQ_COMPLETE);

    // 单 ctx 映射或 polled 请求, 本地完成
    if ((rq->mq_hctx->nr_ctx == 1 &&
         rq->mq_ctx->cpu == raw_smp_processor_id()) ||
         rq->cmd_flags & REQ_POLLED)
        return false;

    // 需要 IPI 时发送IPI
    if (blk_mq_complete_need_ipi(rq)) {
        blk_mq_complete_send_ipi(rq);
        return true;
    }

    // 单硬件队列时 raise softirq
    if (rq->q->nr_hw_queues == 1) {
        blk_mq_raise_softirq(rq);
        return true;
    }
    return false;
}
```

### 7.3 完成机制: Softirq vs Callback

**完成路径选择**:

1. **本地完成** (返回 false):
   - 单硬件队列映射
   - Polled 请求
   - 在同一 CPU 且共享缓存

2. **IPI + Softirq 完成**:
   ```c
   static void __blk_mq_complete_request_remote(void *data)
   {
       __raise_softirq_irqoff(BLOCK_SOFTIRQ);
   }
   ```
   - 需要跨 CPU 完成时, 发送 IPI
   - 在目标 CPU 上 raise BLOCK_SOFTIRQ

3. **直接调用驱动 complete**:
   - `rq->q->mq_ops->complete(rq)` 由驱动实现

### 7.4 `__blk_mq_end_request()` - 结束请求

**文件**: `block/blk-mq.c:1159-1173`

```c
inline void __blk_mq_end_request(struct request *rq, blk_status_t error)
{
    if (blk_mq_need_time_stamp(rq))
        __blk_mq_end_request_acct(rq, blk_time_get_ns());

    blk_mq_finish_request(rq);

    if (rq->end_io) {
        rq_qos_done(rq->q, rq);
        if (rq->end_io(rq, error, NULL) == RQ_END_IO_FREE)
            blk_mq_free_request(rq);
    } else {
        blk_mq_free_request(rq);
    }
}
```

### 7.5 `blk_mq_end_request()` - 公开的结束接口

**文件**: `block/blk-mq.c:1176-1181`

```c
void blk_mq_end_request(struct request *rq, blk_status_t error)
{
    if (blk_update_request(rq, error, blk_rq_bytes(rq)))
        BUG();
    __blk_mq_end_request(rq, error);
}
```

---

## 8. 请求生命周期流程图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          BIO 提交阶段                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  submit_bio_noacct_nocheck()                                            │
│       │                                                                │
│       ├──> __submit_bio_noacct_mq()  [MQ 设备]                          │
│       │         │                                                       │
│       │         └──> __submit_bio()                                     │
│       │                    │                                            │
│       │                    └──> blk_mq_submit_bio()                     │
│       │                              │                                  │
│       │         ┌────────────────────┼────────────────────┐            │
│       │         │                    │                    │            │
│       │         ▼                    ▼                    ▼            │
│       │   [有 Plug]           [有 Scheduler]        [直接发行]          │
│       │         │                    │                    │            │
│       │         ▼                    ▼                    ▼            │
│       │   blk_add_rq_to_plug()  blk_mq_insert_request()  blk_mq_try_   │
│       │         │                    │              issue_directly()    │
│       │         ▼                    ▼                    │            │
│       │   blk_finish_plug()     blk_mq_run_hw_queue()    │            │
│       │         │                    │                    │            │
│       │         ▼                    ▼                    ▼            │
│       │   blk_mq_flush_plug_list()  blk_mq_sched_dispatch_requests()    │
│       │                    │                    │                       │
│       └────────────────────┼────────────────────┘                       │
│                            │                                             │
└────────────────────────────┼─────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          分发阶段                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  blk_mq_sched_dispatch_requests() / blk_mq_run_hw_queue()               │
│       │                                                                │
│       ├──> __blk_mq_sched_dispatch_requests()                          │
│       │         │                                                       │
│       │         ├──> [hctx->dispatch 有残留] ──> blk_mq_dispatch_rq_list│
│       │         │                                                         │
│       │         ├──> [有 elevator] ──> blk_mq_do_dispatch_sched()       │
│       │         │         │                                              │
│       │         │         └──> elevator->dispatch_request()            │
│       │         │                      │                                │
│       │         │                      ▼                                │
│       │         │         blk_mq_dispatch_rq_list()                      │
│       │         │                                                       │
│       │         └──> [无 elevator, 忙碌] ──> blk_mq_do_dispatch_ctx()    │
│       │                                           │                       │
│       │                                           ▼                       │
│       │                              blk_mq_dispatch_rq_list()            │
│       │                                                               │
│       └──> blk_mq_dispatch_rq_list()  [直接调用]                        │
│                    │                                                     │
│                    ▼                                                     │
│  q->mq_ops->queue_rq(hctx, &bd)  ←── 驱动回调                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          完成阶段                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  驱动完成回调                                                           │
│       │                                                                │
│       ▼                                                                │
│  blk_mq_complete_request(rq)                                           │
│       │                                                                │
│       ├──> [需要远程完成] ──> blk_mq_complete_request_remote()          │
│       │                           │                                    │
│       │                           ├──> [需要 IPI]                      │
│       │                           │         └──> blk_mq_complete_send_ipi()
│       │                           │                                          │
│       │                           └──> [单队列] ──> blk_mq_raise_softirq() │
│       │                                                              │
│       └──> [本地完成] ──> rq->q->mq_ops->complete(rq)                │
│                                                                         │
│  blk_mq_end_request()                                                  │
│       │                                                                │
│       └──> blk_update_request() → __blk_mq_end_request()               │
│                                  │                                      │
│                                  ├──> blk_mq_finish_request()          │
│                                  ├──> rq->end_io() [如果设置]           │
│                                  └──> blk_mq_free_request()            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 9. 关键数据结构

### 9.1 struct request

```c
struct request {
    struct request_queue *q;
    struct bio *bio;
    struct bio *biotail;
    
    sector_t __sector;        // 起始扇区
    unsigned int __data_len;  // 数据长度
    
    struct list_head queuelist;  // 队列链表节点
    
    struct blk_mq_ctx *mq_ctx;
    struct blk_mq_hw_ctx *mq_hctx;
    
    unsigned int cmd_flags;
    enum req_op op;
    
    int tag;
    int internal_tag;
    
    struct request *next_rq;  // 用于合并
    
    rq_end_io_fn *end_io;     // 完成回调
    
    // ... 其他字段
};
```

### 9.2 struct blk_plug

```c
struct blk_plug {
    struct rq_list mq_list;      // 请求列表
    unsigned int rq_count;       // 请求计数
    bool multiple_queues;        // 是否跨多队列
    bool has_elevator;           // 是否有 elevator 标记
    struct list_head cb_list;    // 回调列表
    unsigned long cur_ktime;    // 当前时间
    unsigned int nr_ios;        // 批量分配的请求数
    struct rq_list cached_rqs;   // 缓存的请求
};
```

---

## 10. 总结

### 10.1 请求处理关键路径

1. **Bio 提交**: `submit_bio()` → `blk_mq_submit_bio()`
2. **Request 分配**: `blk_mq_get_new_requests()` → `blk_mq_bio_to_request()`
3. **Plug 批处理**: `blk_add_rq_to_plug()` → `blk_finish_plug()` → `blk_mq_flush_plug_list()`
4. **Scheduler 插入**: `blk_mq_insert_request()` → `elevator->insert_requests()`
5. **Dispatch**: `blk_mq_run_hw_queue()` → `blk_mq_sched_dispatch_requests()` → `blk_mq_dispatch_rq_list()`
6. **完成**: `blk_mq_complete_request()` → `__blk_mq_end_request()` → `blk_mq_free_request()`

### 10.2 合并策略

- **Plug 级别合并**: `blk_add_rq_to_plug()` 检查 `BLK_PLUG_FLUSH_SIZE`
- **Scheduler 合并**: `blk_mq_sched_bio_merge()` 调用 elevator 的 `bio_merge`
- **驱动合并**: `blk_mq_attempt_bio_merge()` 尝试与硬件队列中的请求合并

### 10.3 完成机制

- **本地完成**: 同一 CPU 且共享缓存
- **Softirq 完成**: 单硬件队列, raise `BLOCK_SOFTIRQ`
- **IPI + Softirq**: 多硬件队列需要跨 CPU 完成
- **驱动回调**: 最终由 `rq->q->mq_ops->complete(rq)` 处理
