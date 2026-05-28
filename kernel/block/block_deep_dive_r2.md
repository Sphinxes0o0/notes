# Linux Block Layer 深度分析 R2

## 目录

1. [bio_alloc_bioset - bio_pool 内存池管理](#1-bio_alloc_bioset---bio_pool-内存池管理)
2. [blk_mq_tagset - Tag 分配管理](#2-blk_mq_tagset---tag-分配管理)
3. [Request Complete Flow - 请求完成流程](#3-request-complete-flow---请求完成流程)
4. [blk_mq_free_rq - Request 释放回 Tagset](#4-blk_mq_free_rq---request-释放回-tagset)
5. [blk_mq_rq_ctx_init - Request 初始化](#5-blk_mq_rq_ctx_init---request-初始化)
6. [Plug 机制 - blk_plug](#6-plug-机制---blk_plug)
7. [知识点关联表格](#7-知识点关联表格)

---

## 1. bio_alloc_bioset - bio_pool 内存池管理

### 1.1 数据结构图解

```
struct bio_set (include/linux/bio.h:671-697)
+-------------------------------------------------------------------+
| struct kmem_cache *bio_slab         # bio 对象的 slab 缓存         |
| unsigned int front_pad              # bio 前部填充字节数           |
| struct bio_alloc_cache __percpu *cache  # 每 CPU 缓存              |
+-------------------------------------------------------------------+
| mempool_t bio_pool                  # bio 内存池                   |
| mempool_t bvec_pool                 # bio_vec 内存池               |
+-------------------------------------------------------------------+
| unsigned int back_pad                # bio 后部填充字节数           |
| spinlock_t rescue_lock              #  rescue 锁                   |
| struct bio_list rescue_list         # rescue 链表                   |
| struct work_struct rescue_work      # rescue 工作项                 |
| struct workqueue_struct *rescue_workqueue  # rescue 工作队列       |
| struct hlist_node cpuhp_dead        # CPU 热插拔通知节点            |
+-------------------------------------------------------------------+

bio_alloc_cache (bio.c:30-35)
+-------------------------------------------------------------------+
| struct bio *free_list          # 常规 bio 自由链表                 |
| struct bio *free_list_irq      # 中断上下文 bio 自由链表           |
| unsigned int nr                # 常规链表上 bio 数量                |
| unsigned int nr_irq            # 中断链表上 bio 数量               |
+-------------------------------------------------------------------+
```

### 1.2 bioset_create / bioset_init

**源码位置**: `block/bio.c:1931-1974`

```c
int bioset_init(struct bio_set *bs,
		unsigned int pool_size,
		unsigned int front_pad,
		int flags)
{
    bs->front_pad = front_pad;
    if (flags & BIOSET_NEED_BVECS)
        bs->back_pad = BIO_INLINE_VECS * sizeof(struct bio_vec);
    else
        bs->back_pad = 0;

    spin_lock_init(&bs->rescue_lock);
    bio_list_init(&bs->rescue_list);
    INIT_WORK(&bs->rescue_work, bio_alloc_rescue);

    bs->bio_slab = bio_find_or_create_slab(bs);  // 行 1946
    if (!bs->bio_slab)
        return -ENOMEM;

    if (mempool_init_slab_pool(&bs->bio_pool, pool_size, bs->bio_slab))  // 行 1950
        goto bad;

    if ((flags & BIOSET_NEED_BVECS) &&
        biovec_init_pool(&bs->bvec_pool, pool_size))  // 行 1954
        goto bad;

    if (flags & BIOSET_NEED_RESCUER) {
        bs->rescue_workqueue = alloc_workqueue("bioset", ...);  // 行 1958
        if (!bs->rescue_workqueue)
            goto bad;
    }
    if (flags & BIOSET_PERCPU_CACHE) {
        bs->cache = alloc_percpu(struct bio_alloc_cache);  // 行 1964
        if (!bs->cache)
            goto bad;
        cpuhp_state_add_instance_nocalls(CPUHP_BIO_DEAD, &bs->cpuhp_dead);
    }
    return 0;
}
```

### 1.3 bio_alloc_bioset 分配流程

**源码位置**: `block/bio.c:549-635`

```
bio_alloc_bioset()
    |
    +-> 检查 bs->cache 是否存在且 nr_vecs <= BIO_INLINE_VECS
    |   +-> bio_alloc_percpu_cache() 尝试从 per-cpu 缓存分配
    |       +-> 从 cache->free_list 取出 bio
    |       +-> bio_init_inline() 初始化内联 bio
    |
    +-> 如果缓存分配失败
    |   +-> 检查 current->bio_list 是否有待处理的 bios
    |   +-> 如果有且 bs->rescue_workqueue 存在，清除 __GFP_DIRECT_RECLAIM
    |
    +-> mempool_alloc(&bs->bio_pool, gfp_mask) 分配 bio 内存
    |   +-> 如果分配失败且 gfp_mask 不同于 saved_gfp
    |       +-> punt_bios_to_rescuer(bs) 将阻塞的 bio 推向 rescue 线程
    |       +-> 使用原始 gfp_mask 重试
    |
    +-> 计算 bio 实际地址: bio = p + bs->front_pad
    |
    +-> 根据 nr_vecs 分配 bvec:
    |   +-> nr_vecs > BIO_INLINE_VECS: bvec_alloc() 分配
    |   +-> nr_vecs > 0: bio_init_inline() 使用内联 vec
    |   +-> nr_vecs == 0: bio_init() 无 vec
    |
    +-> bio->bi_pool = bs
    +-> return bio
```

### 1.4 bio_free 释放流程

**源码位置**: `block/bio.c:228-238`

```c
static void bio_free(struct bio *bio)
{
    struct bio_set *bs = bio->bi_pool;
    void *p = bio;

    WARN_ON_ONCE(!bs);

    bio_uninit(bio);  // 释放 cgroup、保护信息、加密上下文等
    bvec_free(&bs->bvec_pool, bio->bi_io_vec, bio->bi_max_vecs);  // 行 236
    mempool_free(p - bs->front_pad, &bs->bio_pool);  // 行 237
}
```

**关键算法**: 采用 mempool + slab 混合机制保证分配成功率:
- 正常情况: 从 slab 缓存快速分配
- 内存紧张: mempool 保留池提供保障
- rescue 机制: 防止死锁，栈式驱动场景下推送阻塞 bio

---

## 2. blk_mq_tagset - Tag 分配管理

### 2.1 数据结构图解

```
struct blk_mq_tag_set (include/linux/blk-mq.h:534-557)
+-------------------------------------------------------------------+
| const struct blk_mq_ops *ops          # 硬件队列操作回调           |
| struct blk_mq_queue_map map[HCTX_MAX_TYPES]  # ctx->hctx 映射      |
| unsigned int nr_maps                   # 映射类型数量               |
| unsigned int nr_hw_queues              # 硬件队列数                 |
| unsigned int queue_depth               # 每硬件队列深度              |
| unsigned int reserved_tags             # 保留标签数                 |
| unsigned int cmd_size                  # 每请求额外字节数           |
| int numa_node                          # NUMA 节点                 |
| unsigned int timeout                   # 请求超时时间(jiffies)       |
| unsigned int flags                     # BLK_MQ_F_* 标志            |
| void *driver_data                      # 驱动私有数据               |
+-------------------------------------------------------------------+
| struct blk_mq_tags **tags              # 每个 HW 队列的标签集      |
| struct blk_mq_tags *shared_tags        # 共享标签集                 |
| struct mutex tag_list_lock             # 标签列表锁                 |
| struct list_head tag_list              # 使用此 tag_set 的队列链表  |
| struct srcu_struct *srcu               # 阻塞队列的 SRCU            |
| struct srcu_struct tags_srcu           # 标签页链表释放的 SRCU      |
| struct rw_semaphore update_nr_hwq_lock # 更新 nr_hw_queues 锁     |
+-------------------------------------------------------------------+

struct blk_mq_tags (include/linux/blk-mq.h:774-792)
+-------------------------------------------------------------------+
| unsigned int nr_tags                 # 总标签数                    |
| unsigned int nr_reserved_tags        # 保留标签数                  |
| unsigned int active_queues           # 活跃队列计数                |
+-------------------------------------------------------------------+
| struct sbitmap_queue bitmap_tags      # 普通标签位图               |
| struct sbitmap_queue breserved_tags  # 保留标签位图               |
+-------------------------------------------------------------------+
| struct request **rqs                  # 标签->请求映射数组         |
| struct request **static_rqs           # 静态请求数组              |
| struct list_head page_list            # 请求页链表                 |
| spinlock_t lock                       # 清除 rqs[]引用的锁         |
| struct rcu_head rcu_head              # RCU 头                    |
+-------------------------------------------------------------------+
```

### 2.2 blk_mq_alloc_tag_set 分配流程

**源码位置**: `block/blk-mq.c:4843-4927`

```c
int blk_mq_alloc_tag_set(struct blk_mq_tag_set *set)
{
    int i, ret;

    // 行 4847-4865: 参数校验和调整
    BUILD_BUG_ON(BLK_MQ_MAX_DEPTH > 1 << BLK_MQ_UNIQUE_TAG_BITS);
    if (!set->nr_hw_queues || !set->queue_depth)
        return -EINVAL;
    if (set->queue_depth < set->reserved_tags + BLK_MQ_TAG_MIN)
        return -EINVAL;
    if (!set->ops->queue_rq)
        return -EINVAL;
    if (!set->ops->get_budget ^ !set->ops->put_budget)
        return -EINVAL;
    if (set->queue_depth > BLK_MQ_MAX_DEPTH)
        set->queue_depth = BLK_MQ_MAX_DEPTH;

    // 行 4868-4895: 初始化 SRCU 结构(如果需要阻塞)
    if (set->flags & BLK_MQ_F_BLOCKING) {
        set->srcu = kmalloc_obj(*set->srcu);
        ret = init_srcu_struct(set->srcu);
        if (ret) goto out_free_srcu;
    }
    ret = init_srcu_struct(&set->tags_srcu);  // 行 4896

    init_rwsem(&set->update_nr_hwq_lock);

    // 行 4903-4907: 分配 tags 指针数组
    set->tags = kcalloc_node(set->nr_hw_queues,
        sizeof(struct blk_mq_tags *), GFP_KERNEL, set->numa_node);

    // 行 4909-4916: 分配 ctx->hctx 映射数组
    for (i = 0; i < set->nr_maps; i++) {
        set->map[i].mq_map = kcalloc_node(nr_cpu_ids, ...);
        set->map[i].nr_queues = set->nr_hw_queues;
    }

    blk_mq_update_queue_map(set);  // 行 4918: 更新队列映射

    ret = blk_mq_alloc_set_map_and_rqs(set);  // 行 4920: 分配标签集和请求

    mutex_init(&set->tag_list_lock);
    INIT_LIST_HEAD(&set->tag_list);

    return 0;
}
```

### 2.3 标签分配核心算法

**blk_mq_get_tag** (block/blk-mq-tag.c)

```
标签分配使用 sbitmap_queue 进行管理:
- bitmap_tags: 普通标签池, nr_tags - nr_reserved_tags 个标签
- breserved_tags: 保留标签池, nr_reserved_tags 个标签

分配算法:
1. 调用 sbitmap_queue_get() 原子获取一个标签
2. 标签范围检查: tag < nr_tags
3. 如果硬件队列不活跃, 返回 BLK_MQ_NO_TAG
4. 更新 tags->rqs[tag] = rq
```

---

## 3. Request Complete Flow - 请求完成流程

### 3.1 完整流程图

```
blk_mq_complete_request(rq)                           [block/blk-mq.c:1353]
    |
    +-> blk_mq_complete_request_remote(rq)           [block/blk-mq.c:1319]
    |   +-> 如果在中断上下文:__blk_mq_complete_request_remote()
    |   |   +-> 调度到每 CPU CSD 上异步执行
    |   +-> 如果在当前 CPU: 返回 false
    |
    +-> 如果返回 false: rq->q->mq_ops->complete(rq) [驱动完成回调]

blk_mq_end_request(rq, error)                        [block/blk-mq.c:1176]
    |
    +-> blk_update_request(rq, error, blk_rq_bytes(rq))  [更新剩余字节数]
    |   +-> 如果还有剩余: 返回 true, BUG()
    |
    +-> __blk_mq_end_request(rq, error)              [block/blk-mq.c:1159]
        |
        +-> __blk_mq_end_request_acct(rq, now)       [block/blk-mq.c:1150]
        |   +-> blk_stat_add(rq, now)               # 统计信息
        |   +-> blk_mq_sched_completed_request(rq, now)  # IO 调度器完成
        |   +-> blk_account_io_done(rq, now)        # block 层统计
        |       +-> trace_block_io_done(req)        # 跟踪点
        |       +-> part_stat_inc(ios[sgrp])        # 分区统计
        |       +-> part_stat_add(nsecs[sgrp], ...) # 耗时统计
        |       +-> part_stat_local_dec(in_flight)  # 飞行中请求--
        |
        +-> blk_mq_finish_request(rq)                [block/blk-mq.c:782]
        |   +-> blk_zone_finish_request(rq)         # Zoned 设备处理
        |   +-> q->elevator->type->ops.finish_request(rq)  # 调度器后处理
        |
        +-> rq_qos_done(rq->q, rq)                  # QoS 完成
        |
        +-> rq->end_io(rq, error, NULL)?
        |   +-> 如果返回 RQ_END_IO_FREE: blk_mq_free_request(rq)
        |   +-> 否则: blk_mq_free_request(rq)
        |
        +-> blk_mq_free_request(rq)
```

### 3.2 blk_account_io_done 统计详解

**源码位置**: `block/blk-mq.c:1069-1089`

```c
static inline void blk_account_io_done(struct request *req, u64 now)
{
    trace_block_io_done(req);

    if ((req->rq_flags & (RQF_IO_STAT|RQF_FLUSH_SEQ)) == RQF_IO_STAT) {
        const int sgrp = op_stat_group(req_op(req));

        part_stat_lock();
        update_io_ticks(req->part, jiffies, true);
        part_stat_inc(req->part, ios[sgrp]);           // 增加 IO 计数
        part_stat_add(req->part, nsecs[sgrp],          // 增加耗时统计
                      now - req->start_time_ns);
        part_stat_local_dec(req->part,
                    in_flight[op_is_write(req_op(req))]); // 飞行中请求--
        part_stat_unlock();
    }
}
```

### 3.3 批量请求完成

**blk_mq_end_request_batch** (block/blk-mq.c:1197-1213)

支持批量完成请求，减少锁竞争:

```c
void blk_mq_end_request_batch(struct io_comp_batch *iob)
{
    int tags[TAG_COMP_BATCH], nr_tags = 0;
    struct request *rq;
    unsigned long long now = blk_time_get_ns();

    while ((rq = rq_list_pop(&iob->list)) != NULL) {
        if (blk_mq_need_time_stamp(rq))
            __blk_mq_end_request_acct(rq, now);
        blk_mq_finish_request(rq);
        tags[nr_tags++] = rq->tag;
        if (nr_tags == TAG_COMP_BATCH)
            break;
    }
    if (nr_tags)
        blk_mq_flush_tag_batch(hctx, tags, nr_tags);  // 批量放回标签
}
```

---

## 4. blk_mq_free_rq - Request 释放回 Tagset

### 4.1 释放流程图

```
blk_mq_free_request(rq)                              [block/blk-mq.c:820]
    |
    +-> blk_mq_finish_request(rq)                   [block/blk-mq.c:782]
    |   +-> blk_zone_finish_request(rq)
    |   +-> elevator->type->ops.finish_request(rq)
    |
    +-> rq_qos_done(q, rq)
    |
    +-> WRITE_ONCE(rq->state, MQ_RQ_IDLE)
    |
    +-> req_ref_put_and_test(rq)?
        +-> __blk_mq_free_request(rq)               [block/blk-mq.c:799]
            |
            +-> blk_crypto_free_request(rq)
            +-> blk_pm_mark_last_busy(rq)
            +-> rq->mq_hctx = NULL
            |
            +-> if (rq->tag != BLK_MQ_NO_TAG)
            |   +-> blk_mq_dec_active_requests(hctx)
            |   +-> blk_mq_put_tag(hctx->tags, ctx, rq->tag)  // 放回标签
            |
            +-> if (sched_tag != BLK_MQ_NO_TAG)
            |   +-> blk_mq_put_tag(hctx->sched_tags, ctx, sched_tag)
            |
            +-> blk_mq_sched_restart(hctx)           // 重启调度器
            |
            +-> blk_queue_exit(q)                   // 释放队列引用
```

### 4.2 blk_mq_put_tag 标签放回

**源码位置**: `block/blk-mq-tag.c:228-239`

```c
void blk_mq_put_tag(struct blk_mq_tags *tags, struct blk_mq_ctx *ctx,
                    unsigned int tag)
{
    if (!blk_mq_tag_is_reserved(tags, tag)) {
        const int real_tag = tag - tags->nr_reserved_tags;
        BUG_ON(real_tag >= tags->nr_tags);
        sbitmap_queue_clear(&tags->bitmap_tags, real_tag, ctx->cpu);  // 行 235
    } else {
        sbitmap_queue_clear(&tags->breserved_tags, tag, ctx->cpu);    // 行 237
    }
}
```

### 4.3 sbitmap_queue_clear 唤醒机制

```c
// block/blk-mq-tag.c:235-237
sbitmap_queue_clear(&tags->bitmap_tags, real_tag, ctx->cpu);

// 实现: 清除位图中的位，并唤醒等待该位图的任何等待者
// 这允许在 blk_mq_get_tag() 中阻塞的请求被唤醒
```

### 4.4 blk_mq_sched_restart 调度器重启

**源码位置**: `block/blk-mq.c:816`

```c
static void __blk_mq_free_request(struct request *rq)
{
    ...
    blk_mq_sched_restart(hctx);  // 行 816
    ...
}
```

该函数触发调度器重新尝试分配请求到硬件队列。

---

## 5. blk_mq_rq_ctx_init - Request 初始化

### 5.1 函数详解

**源码位置**: `block/blk-mq.c:410-461`

```c
static struct request *blk_mq_rq_ctx_init(struct blk_mq_alloc_data *data,
        struct blk_mq_tags *tags, unsigned int tag)
{
    struct blk_mq_ctx *ctx = data->ctx;
    struct blk_mq_hw_ctx *hctx = data->hctx;
    struct request_queue *q = data->q;
    struct request *rq = tags->static_rqs[tag];  // 行 416: 从静态数组获取

    // 基本字段初始化
    rq->q = q;
    rq->mq_ctx = ctx;
    rq->mq_hctx = hctx;
    rq->cmd_flags = data->cmd_flags;

    // PM 标志传递
    if (data->flags & BLK_MQ_REQ_PM)
        data->rq_flags |= RQF_PM;
    rq->rq_flags = data->rq_flags;

    // 标签设置: 普通标签 vs 调度器标签
    if (data->rq_flags & RQF_SCHED_TAGS) {
        rq->tag = BLK_MQ_NO_TAG;
        rq->internal_tag = tag;
    } else {
        rq->tag = tag;
        rq->internal_tag = BLK_MQ_NO_TAG;
    }
    rq->timeout = 0;

    rq->part = NULL;
    rq->io_start_time_ns = 0;
    rq->stats_sectors = 0;
    rq->nr_phys_segments = 0;
    rq->nr_integrity_segments = 0;
    rq->end_io = NULL;
    rq->end_io_data = NULL;

    blk_crypto_rq_set_defaults(rq);
    INIT_LIST_HEAD(&rq->queuelist);
    WRITE_ONCE(rq->deadline, 0);
    req_ref_set(rq, 1);  // 引用计数初始化为 1

    // 如果使用 IO 调度器, 执行额外初始化
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

### 5.2 批量请求初始化

**源码位置**: `block/blk-mq.c:463-499`

```c
static inline struct request *
__blk_mq_alloc_requests_batch(struct blk_mq_alloc_data *data)
{
    unsigned int tag, tag_offset;
    struct blk_mq_tags *tags;
    struct request *rq;
    unsigned long tag_mask;
    int i, nr = 0;

    do {
        tag_mask = blk_mq_get_tags(data, data->nr_tags - nr, &tag_offset);
        if (unlikely(!tag_mask)) {
            if (nr == 0) return NULL;
            break;
        }
        tags = blk_mq_tags_from_data(data);
        for (i = 0; tag_mask; i++) {
            if (!(tag_mask & (1UL << i)))
                continue;
            tag = tag_offset + i;
            prefetch(tags->static_rqs[tag]);  // 预取请求
            tag_mask &= ~(1UL << i);
            rq = blk_mq_rq_ctx_init(data, tags, tag);
            rq_list_add_head(data->cached_rqs, rq);  // 加入缓存链表
            nr++;
        }
    } while (data->nr_tags > nr);

    if (!(data->rq_flags & RQF_SCHED_TAGS))
        blk_mq_add_active_requests(data->hctx, nr);  // 增加活跃请求计数
    percpu_ref_get_many(&data->q->q_usage_counter, nr - 1);  // 引用计数
    data->nr_tags -= nr;

    return rq_list_pop(data->cached_rqs);  // 返回链表头
}
```

### 5.3 请求生命周期状态机

```
MQ_RQ_IDLE -> MQ_RQ_IN_FLIGHT -> MQ_RQ_COMPLETE
     ^              |                    |
     |              v                    v
     +-------- blk_mq_free_request ----+
```

---

## 6. Plug 机制 - blk_plug

### 6.1 数据结构

**源码位置**: `include/linux/blkdev.h:1172-1186`

```
struct blk_plug
+-------------------------------------------------------------------+
| struct rq_list mq_list            # 多队列请求链表                |
| struct rq_list cached_rqs        # 缓存请求链表(用于批量分配)     |
| u64 cur_ktime                     # 当前 ktime                   |
| unsigned short nr_ios             # IO 数量                      |
| unsigned short rq_count           # 请求计数                     |
| bool multiple_queues              # 是否来自多个队列              |
| bool has_elevator                 # 是否有 elevator 标签          |
| struct list_head cb_list          # MD unplug 回调链表            |
+-------------------------------------------------------------------+
```

### 6.2 Plug 机制工作原理

**核心思想**: 合并同一任务的顺序 I/O 请求,减少锁竞争

```
应用程序
    |
    v
submit_bio()
    |
    v
blk_mq_submit_bio()
    |
    v
struct blk_plug *plug = current->plug  // 获取当前任务的 plug
    |
    +-> 如果 plug 存在且可以合并
    |   +-> blk_add_rq_to_plug(plug, rq)  // 添加到 plug 链表
    |       +-> 检查是否超过 plug->rq_count >= blk_plug_max_rq_count()
    |       +-> 检查是否可以与 last 请求合并
    |       +-> 如果不能合并且超过阈值, 调用 blk_mq_flush_plug_list()
    |
    +-> 如果不能合并或需要立即处理
        +-> 走正常提交流程
```

### 6.3 blk_add_rq_to_plug 添加请求到 Plug

**源码位置**: `block/blk-mq.c:1408-1432`

```c
static void blk_add_rq_to_plug(struct blk_plug *plug, struct request *rq)
{
    struct request *last = rq_list_peek(&plug->mq_list);

    if (!plug->rq_count) {
        trace_block_plug(rq->q);  // 首次插入, 记录跟踪点
    } else if (plug->rq_count >= blk_plug_max_rq_count(plug) ||
               (!blk_queue_nomerges(rq->q) &&
                blk_rq_bytes(last) >= BLK_PLUG_FLUSH_SIZE)) {
        // 超过最大请求数或最后请求足够大, 刷新 plug
        blk_mq_flush_plug_list(plug, false);
        last = NULL;
        trace_block_plug(rq->q);
    }

    if (!plug->multiple_queues && last && last->q != rq->q)
        plug->multiple_queues = true;  // 标记多队列模式
    if (!plug->has_elevator && (rq->rq_flags & RQF_SCHED_TAGS))
        plug->has_elevator = true;    // 标记有 elevator 标签
    rq_list_add_tail(&plug->mq_list, rq);  // 添加到链表尾部
    plug->rq_count++;
}
```

### 6.4 blk_plug_max_rq_count 最大请求数

**源码位置**: `block/blk-mq.c:1401-1406`

```c
static inline unsigned short blk_plug_max_rq_count(struct blk_plug *plug)
{
    if (plug->multiple_queues)
        return BLK_MAX_REQUEST_COUNT * 2;  // 多队列: 64 * 2 = 128
    return BLK_MAX_REQUEST_COUNT;           // 单队列: 64
}
```

### 6.5 blk_mq_flush_plug_list 刷新 Plug

**源码位置**: `block/blk-mq.c:2969-2999`

```c
void blk_mq_flush_plug_list(struct blk_plug *plug, bool from_schedule)
{
    unsigned int depth;

    if (plug->rq_count == 0)  // 防止递归
        return;
    depth = plug->rq_count;
    plug->rq_count = 0;

    // 无 elevator 且非异步: 尝试批量分发
    if (!plug->has_elevator && !from_schedule) {
        if (plug->multiple_queues) {
            blk_mq_dispatch_multiple_queue_requests(&plug->mq_list);
            return;
        }
        blk_mq_dispatch_queue_requests(&plug->mq_list, depth);
        if (rq_list_empty(&plug->mq_list))
            return;
    }

    // 否则逐个分发
    do {
        blk_mq_dispatch_list(&plug->mq_list, from_schedule);
    } while (!rq_list_empty(&plug->mq_list));
}
```

### 6.6 blk_start_queue_async 异步队列启动

**blk_mq_run_hw_queue** (block/blk-mq.c:2352-2388)

```c
void blk_mq_run_hw_queue(struct blk_mq_hw_ctx *hctx, bool async)
{
    bool need_run;

    WARN_ON_ONCE(!async && in_interrupt());  // 非异步不能在中断上下文
    might_sleep_if(!async && hctx->flags & BLK_MQ_F_BLOCKING);

    need_run = blk_mq_hw_queue_need_run(hctx);  // 行 2363: 检查是否需要运行
    if (!need_run) {
        unsigned long flags;
        spin_lock_irqsave(&hctx->queue->queue_lock, flags);
        need_run = blk_mq_hw_queue_need_run(hctx);  // 再次检查
        spin_unlock_irqrestore(&hctx->queue->queue_lock, flags);
        if (!need_run)
            return;
    }

    // 异步或不在正确的 CPU 上: 延迟运行
    if (async || !cpumask_test_cpu(raw_smp_processor_id(), hctx->cpumask)) {
        blk_mq_delay_run_hw_queue(hctx, 0);  // 延迟 0 jiffies
        return;
    }

    // 同步运行: 调用调度器分发
    blk_mq_run_dispatch_ops(hctx->queue,
                blk_mq_sched_dispatch_requests(hctx));  // 行 2386-2387
}
```

**blk_mq_hw_queue_need_run** (block/blk-mq.c:2325-2341)

```c
static inline bool blk_mq_hw_queue_need_run(struct blk_mq_hw_ctx *hctx)
{
    bool need_run;

    __blk_mq_run_dispatch_ops(hctx->queue, false,
        need_run = !blk_queue_quiesced(hctx->queue) &&  // 队列未冻结
        blk_mq_hctx_has_pending(hctx));                  // 硬件队列有待处理请求
    return need_run;
}
```

---

## 7. 知识点关联表格

| 模块 | 核心结构体 | 核心函数 | 关键算法 | 源码位置 |
|------|-----------|---------|---------|---------|
| **bio 内存池** | `struct bio_set` | `bioset_init()` | mempool + slab 混合分配, rescue 机制防死锁 | `block/bio.c:1931` |
| | `struct bio_alloc_cache` | `bio_alloc_bioset()` | per-cpu 缓存加速, 前置填充对齐 | `block/bio.c:549` |
| | | `bio_free()` | mempool_free + bvec_free 释放 | `block/bio.c:228` |
| **tag set 管理** | `struct blk_mq_tag_set` | `blk_mq_alloc_tag_set()` | 参数校验, SRCU 初始化, tags 数组分配 | `block/blk-mq.c:4843` |
| | `struct blk_mq_tags` | `blk_mq_get_tag()` | sbitmap_queue 原子分配, active_queues 计数 | `block/blk-mq-tag.c:160` |
| | | `blk_mq_put_tag()` | sbitmap_queue_clear + 唤醒等待者 | `block/blk-mq-tag.c:228` |
| **请求完成** | `struct request` | `blk_mq_complete_request()` | 远程完成调度 vs 本地驱动回调 | `block/blk-mq.c:1353` |
| | | `blk_mq_end_request()` | blk_update_request + 统计更新 | `block/blk-mq.c:1176` |
| | | `blk_account_io_done()` | part_stat 统计, trace_block_io_done | `block/blk-mq.c:1069` |
| **请求释放** | - | `blk_mq_free_request()` | 引用计数检查, finish_request | `block/blk-mq.c:820` |
| | | `__blk_mq_free_request()` | put_tag + sched_restart + queue_exit | `block/blk-mq.c:799` |
| **请求初始化** | - | `blk_mq_rq_ctx_init()` | static_rqs 数组获取, 标签设置, elevator prepare | `block/blk-mq.c:410` |
| | | `__blk_mq_alloc_requests_batch()` | 批量标签获取 + 批量初始化 | `block/blk-mq.c:463` |
| **Plug 机制** | `struct blk_plug` | `blk_add_rq_to_plug()` | 合并检查, rq_count 阈值刷新 | `block/blk-mq.c:1408` |
| | | `blk_mq_flush_plug_list()` | 批量分发 vs 单个分发 | `block/blk-mq.c:2969` |
| | | `blk_mq_run_hw_queue()` | 队列运行条件检查, 异步/同步分发 | `block/blk-mq.c:2352` |
| | | `blk_mq_hw_queue_need_run()` | !quiesced && has_pending | `block/blk-mq.c:2325` |

### 关键调用链汇总

```
bio_alloc_bioset
  -> mempool_alloc (bio_pool)
  -> bvec_alloc (bvec_pool)
  -> bio_init

blk_mq_alloc_tag_set
  -> blk_mq_alloc_set_map_and_rqs
    -> blk_mq_alloc_rq_map
    -> blk_mq_alloc_rqs

blk_mq_submit_bio
  -> blk_mq_plug
  -> blk_add_rq_to_plug / blk_mq_sched_insert_request
  -> blk_mq_run_hw_queue

blk_mq_complete_request
  -> blk_mq_complete_request_remote / mq_ops->complete
  -> blk_mq_end_request
    -> __blk_mq_end_request
      -> blk_account_io_done
      -> blk_mq_finish_request
      -> blk_mq_free_request
        -> __blk_mq_free_request
          -> blk_mq_put_tag
          -> blk_mq_sched_restart
          -> blk_queue_exit
```

---

## 参考源码文件

| 文件 | 描述 |
|------|------|
| `block/bio.c` | bio 分配/释放, bio_set 管理 |
| `block/blk-mq.c` | blk-mq 核心: tag set, request 生命周期, plug 机制 |
| `block/blk-mq-tag.c` | 标签管理: 分配/释放/迭代 |
| `include/linux/bio.h` | bio_set, bio 结构定义 |
| `include/linux/blk-mq.h` | blk_mq_tag_set, blk_mq_tags, blk_mq_ops 定义 |
| `include/linux/blkdev.h` | blk_plug 结构定义 |

---

*文档版本: R2*
*生成时间: 2026-04-26*
*内核版本: Linux Block Layer (最新主线)*
