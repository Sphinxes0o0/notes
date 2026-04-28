# Linux Block Layer 深度分析 R1

## 目录

1. [bio 结构详解](#1-bio-结构详解)
2. [request 与 request_queue](#2-request-与-request_queue)
3. [blk-mq 多队列机制](#3-blk-mq-多队列机制)
4. [I/O Scheduler 分析](#4-io-scheduler-分析)
5. [GenHD 与 Partitions](#5-gendisk-与-partitions)
6. [知识点关联表格](#6-知识点关联表格)

---

## 1. bio 结构详解

### 1.1 struct bio 内存布局

**源码位置**: `/Users/sphinx/github/linux/include/linux/blk_types.h` (第 210-287 行)

```c
struct bio {
    struct bio      *bi_next;           /* 请求队列链表指针 */
    struct block_device *bi_bdev;       /* 指向块设备 */
    blk_opf_t       bi_opf;            /* 低8位: REQ_OP, 高24位: req_flags */
    unsigned short  bi_flags;          /* BIO_* 标志位 */
    unsigned short  bi_ioprio;         /* I/O优先级 */
    enum rw_hint    bi_write_hint;     /* 写入提示 */
    u8              bi_write_stream;   /* 写入流ID */
    blk_status_t    bi_status;         /* 操作状态 (BLK_STS_*) */
    u8              bi_bvec_gap_bit;   /* bvec间隙位 */
    atomic_t         __bi_remaining;    /* 链式bio剩余计数 */
    
    /* 实际 vec 列表, 通过 bio_reset() 保留 */
    struct bio_vec  *bi_io_vec;        /* bio_vec 数组指针 */
    struct bvec_iter bi_iter;          /* 迭代器, 跟踪当前进度 */
    
    union {
        blk_qc_t     bi_cookie;        /* polled bios 用 */
        unsigned int __bi_nr_segments; /* zoned writes 用 */
    };
    
    bio_end_io_t   *bi_end_io;        /*  completion 回调函数 */
    void           *bi_private;        /* 私有数据 */
    
#ifdef CONFIG_BLK_CGROUP
    struct blkcg_gq *bi_blkg;         /* cgroup 关联 */
    u64             issue_time_ns;    /* bio 发放时间 */
#endif
    
    unsigned short  bi_vcnt;           /* 已使用的 bio_vec 数量 */
    unsigned short  bi_max_vecs;       /* bi_io_vec 数组大小 */
    atomic_t         __bi_cnt;         /* 引用计数 */
    struct bio_set  *bi_pool;         /* bio_set 内存池 */
};
```

**关键布局特性**:
- `bi_io_vec` 和 `bi_iter` 是 bio 的核心数据结构
- `BIO_RESET_BYTES` (offsetof(struct bio, bi_max_vecs)) 之前的字段在 `bio_reset()` 时会被清零
- 内联 bio_vec 可通过 `bio_inline_vecs()` 宏获取 (第 293-296 行)

### 1.2 struct bio_vec 与 bvec_iter

**源码位置**: `/Users/sphinx/github/linux/include/linux/bvec.h`

```c
struct bio_vec {
    struct page *bv_page;      /* 内存页 */
    unsigned int bv_len;       /* 段长度 */
    unsigned int bv_offset;    /* 页内偏移 */
};

struct bvec_iter {
    sector_t bi_sector;        /* 当前扇区 (8字节) */
    unsigned int bi_size;      /* 剩余字节数 */
    unsigned int bi_idx;       /* 当前 bio_vec 索引 */
    unsigned int bi_bvec_done;/* 当前 bio_vec 内已处理字节 */
};
```

### 1.3 bi_end_io 回调机制

**源码位置**: `/Users/sphinx/github/linux/block/bio.c` (第 1749-1793 行)

```c
void bio_endio(struct bio *bio)
{
again:
    if (!bio_remaining_done(bio))    /* 处理链式 bio */
        return;
    if (!bio_integrity_endio(bio))   /* 处理完整性校验 */
        return;

    blk_zone_bio_endio(bio);         /* 分区写优化 */
    rq_qos_done_bio(bio);           /* QoS 完成处理 */

    /* 链式 bio 处理 */
    if (bio->bi_end_io == bio_chain_endio) {
        bio = __bio_chain_endio(bio);
        goto again;
    }

#ifdef CONFIG_BLK_CGROUP
    if (bio->bi_blkg) {
        blkg_put(bio->bi_blkg);     /* 释放 cgroup 引用 */
        bio->bi_blkg = NULL;
    }
#endif

    if (bio->bi_end_io)
        bio->bi_end_io(bio);         /* 调用用户回调 */
}
```

**回调触发流程**:
1. 设备驱动完成 I/O 后调用 `bio_endio()`
2. 如果是链式 bio (`BIO_CHAIN`)，等待所有子 bio 完成
3. 调用 `bi_end_io()` 回调通知上层

---

## 2. request 与 request_queue

### 2.1 struct request 结构

**源码位置**: `/Users/sphinx/github/linux/include/linux/blk-mq.h` (第 105-219 行)

```c
struct request {
    struct request_queue *q;          /* 所属队列 */
    struct blk_mq_ctx *mq_ctx;      /* 软件队列上下文 */
    struct blk_mq_hw_ctx *mq_hctx;  /* 硬件队列上下文 */
    
    blk_opf_t cmd_flags;             /* 操作类型和标志 */
    req_flags_t rq_flags;           /* 请求标志 (RQF_*) */
    
    int tag;                        /* 硬件队列 tag */
    int internal_tag;               /* 内部 tag (调度器用) */
    
    unsigned int timeout;           /* 超时时间 */
    unsigned int __data_len;       /* 总数据长度 (字节) */
    sector_t __sector;              /* 当前扇区位置 */
    
    struct bio *bio;                /* 关联的 bio 链表头 */
    struct bio *biotail;            /* 关联的 bio 链表尾 */
    
    union {
        struct list_head queuelist; /* 队列链表 */
        struct request *rq_next;    /* 下一个请求 */
    };
    
    struct block_device *part;      /* 目标分区 */
    
    /* 状态与引用计数 */
    enum mq_rq_state state;
    atomic_t ref;
    
    unsigned long deadline;         /* 截止时间 (用于调度) */
    
    union {
        struct hlist_node hash;    /* 合并哈希表节点 */
        struct llist_node ipi_list; /* 软中断完成链表 */
    };
    
    union {
        struct rb_node rb_node;     /* 调度器红黑树节点 */
        struct bio_vec special_vec; /* 特殊负载向量 */
    };
    
    /* IO调度器私有数据 */
    struct {
        struct io_cq *icq;
        void *priv[2];
    } elv;
    
    /* flush 状态机 */
    struct {
        unsigned int seq;
        rq_end_io_fn *saved_end_io;
    } flush;
    
    u64 fifo_time;                  /* FIFO 时间戳 */
    rq_end_io_fn *end_io;          /* 完成回调 */
    void *end_io_data;
};
```

### 2.2 struct request_queue

**源码位置**: `/Users/sphinx/github/linux/include/linux/blkdev.h` (第 478-650 行)

```c
struct request_queue {
    void *queuedata;                 /* 驱动私有数据 */
    struct elevator_queue *elevator; /* IO调度器 */
    const struct blk_mq_ops *mq_ops; /* blk-mq 操作集 */
    
    struct blk_mq_ctx __percpu *queue_ctx; /* 每CPU软件队列 */
    unsigned long queue_flags;     /* 队列标志 */
    
    unsigned int rq_timeout;       /* 请求超时 */
    unsigned int queue_depth;      /* 队列深度 */
    
    refcount_t refs;               /* 引用计数 */
    
    unsigned int nr_hw_queues;     /* 硬件队列数 */
    struct blk_mq_hw_ctx * __rcu *queue_hw_ctx; /* 硬件队列数组 */
    
    struct percpu_ref q_usage_counter; /* 使用计数 (freeze机制) */
    
    struct gendisk *disk;          /* 关联的 gendisk */
    
    struct queue_limits limits;    /* 队列限制参数 */
    
    atomic_t pm_only;              /* PM 计数 */
    struct blk_queue_stats *stats; /* 统计信息 */
    struct rq_qos *rq_qos;        /* RQ QoS 层 */
    
    int id;                       /* 队列ID */
    unsigned int nr_requests;     /* 最大请求数 */
    
    struct timer_list timeout;     /* 超时定时器 */
    struct work_struct timeout_work;
    
    struct blk_flush_queue *fq;   /* flush 队列 */
    
    struct mutex elevator_lock;    /* 调度器切换锁 */
    struct mutex sysfs_lock;
    struct mutex limits_lock;
    
    struct list_head unused_hctx_list; /* 未使用的hctx列表 */
};
```

### 2.3 请求生命周期

**请求生命周期图解**:

```
bio_submit()
    ↓
submit_bio() [blk-core.c:916]
    ↓
submit_bio_noacct() [blk-core.c:780]
    ↓
blk_throtl_bio() → submit_bio_noacct_nocheck()
    ↓
__submit_bio_noacct_mq() / __submit_bio_noacct()
    ↓
blk_mq_submit_bio()
    ↓
blk_mq_sched_insert_request()
    ↓
    ├─→ elv_may_queue() [调度器决定]
    ├─→ blk_mq_rq_ctx_init() [初始化request]
    └─→ blk_mq_insert_requests()
            ↓
        blk_mq_run_hw_queue() [触发硬件队列]
            ↓
        blk_mq_sched_dispatch_requests() [调度器dispatch]
            ↓
        hctx->ops->queue_rq() [驱动回调]
            ↓
        blk_mq_end_request() [完成]
```

---

## 3. blk-mq 多队列机制

### 3.1 blk_mq_hw_ctx 硬件队列上下文

**源码位置**: `/Users/sphinx/github/linux/include/linux/blk-mq.h` (第 318-463 行)

```c
struct blk_mq_hw_ctx {
    struct {
        spinlock_t lock;               /* 保护 dispatch 列表 */
        struct list_head dispatch;      /* 就绪分发链表 */
        unsigned long state;           /* BLK_MQ_S_* 状态 */
    } ____cacheline_aligned_in_smp;
    
    struct delayed_work run_work;     /* 延迟运行工作 */
    cpumask_var_t cpumask;            /* 可用CPU掩码 */
    int next_cpu;                     /* 下一CPU (RR选择) */
    int next_cpu_batch;
    
    unsigned long flags;              /* BLK_MQ_F_* 标志 */
    void *sched_data;                /* 调度器私有数据 */
    struct request_queue *queue;      /* 所属队列 */
    struct blk_flush_queue *fq;       /* flush队列 */
    void *driver_data;               /* 驱动私有数据 */
    
    struct sbitmap ctx_map;           /* 软件队列位图 */
    
    struct blk_mq_ctx *dispatch_from; /* 分发源软件队列 */
    unsigned int dispatch_busy;      /* 分发忙碌度 (EWMA) */
    
    unsigned short type;              /* HCTX_TYPE_* 队列类型 */
    unsigned short nr_ctx;           /* 软件队列数 */
    struct blk_mq_ctx **ctxs;        /* 软件队列数组 */
    
    struct blk_mq_tags *tags;         /* 驱动tag集 */
    struct blk_mq_tags *sched_tags;  /* 调度器tag集 */
    
    unsigned int queue_num;           /* 队列编号 */
    atomic_t nr_active;              /* 活跃请求数 */
};
```

### 3.2 blk_mq_init 初始化流程

**源码位置**: `/Users/sphinx/github/linux/block/blk-mq.c` (第 4630-4679 行)

```c
int blk_mq_init_allocated_queue(struct blk_mq_tag_set *set,
        struct request_queue *q)
{
    q->mq_ops = set->ops;           // 设置操作集
    
    q->tag_set = set;                // 关联tag_set
    
    if (blk_mq_alloc_ctxs(q))        // 分配软件队列
        goto err_exit;
    
    blk_mq_sysfs_init(q);            // 初始化sysfs
    
    blk_mq_realloc_hw_ctxs(set, q);  // 分配硬件队列
    
    if (!q->nr_hw_queues)
        goto err_hctxs;
    
    blk_mq_init_cpu_queues(q, set->nr_hw_queues);  // 初始化CPU队列
    blk_mq_map_swqueue(q);           // 映射软硬件队列
    blk_mq_add_queue_tag_set(set, q); // 添加到tag_set列表
    
    return 0;
}
```

**关键初始化步骤**:
1. `blk_mq_alloc_ctxs()` - 分配 per-CPU 软件队列
2. `blk_mq_realloc_hw_ctxs()` - 分配硬件队列数组
3. `blk_mq_init_cpu_queues()` - 初始化软件队列结构
4. `blk_mq_map_swqueue()` - 建立 CPU 到硬件队列的映射

### 3.3 blk_mq_run_hw_queues 触发分发

**源码位置**: `/Users/sphinx/github/linux/block/blk-mq.c` (第 2417-2438 行)

```c
void blk_mq_run_hw_queues(struct request_queue *q, bool async)
{
    struct blk_mq_hw_ctx *hctx, *sq_hctx;
    unsigned long i;

    sq_hctx = NULL;
    if (blk_queue_sq_sched(q))
        sq_hctx = blk_mq_get_sq_hctx(q);
    
    queue_for_each_hw_ctx(q, hctx, i) {
        if (blk_mq_hctx_stopped(hctx))
            continue;
        /*
         * 对于单队列风格的调度器, 只从首选hctx分发
         * 或者当hctx有bypass请求(dispatch列表非空)时分发
         */
        if (!sq_hctx || sq_hctx == hctx ||
            !list_empty_careful(&hctx->dispatch))
            blk_mq_run_hw_queue(hctx, async);
    }
}
```

### 3.4 软硬中断分离与 hctx->dispatch

**dispatch 机制核心**:

```c
// blk-mq.c 核心分发逻辑
static void blk_mq_sched_dispatch_requests(struct blk_mq_hw_ctx *hctx)
{
    struct request_queue *q = hctx->queue;
    bool needs_run;

    // 1. 首先处理 dispatch 链表 (bypass 的请求)
    if (!list_empty(&hctx->dispatch)) {
        blk_mq_bypass_dispatch(hctx);
        if (list_empty(&hctx->dispatch))
            return;
    }

    // 2. 从 IO 调度器获取请求
    if (hctx->type == HCTX_TYPE_POLL)
        blk_mq_dispatch_poll_list(hctx);
    else
        blk_mq_sched_dispatch_rq(hctx);
}
```

**软硬中断分离实现**:
- **硬中断 (Hard IRQ)**: `blk_mq_irq_handler()` → 标记 `ctx_map` 位图
- **软中断 (Soft IRQ)**: `blk_mq_softirq_done()` → 处理完成
- **异步**: `blk_mq_run_hw_queue(..., true)` → `delayed_work`

---

## 4. I/O Scheduler 分析

### 4.1 elevator 核心结构

**源码位置**: `/Users/sphinx/github/linux/block/elevator.h`

```c
struct elevator_type {
    const char *elevator_name;      /* 调度器名称 */
    const char *elevator_alias;     /* 别名 */
    const struct elv_fs_entry *elevator_attrs; /* sysfs属性 */
    struct elv_operations ops;      /* 操作函数集 */
    struct list_head list;          /* 全局链表 */
    
    unsigned int icq_size;          /* io_cq 大小 */
    unsigned int icq_align;         /* 对齐要求 */
    char icq_cache_name[...];      /* slab 缓存名 */
    struct kmem_cache *icq_cache;  /* io_cq 缓存 */
};
```

### 4.2 mq-deadline 算法分析

**源码位置**: `/Users/sphinx/github/linux/block/mq-deadline.c`

**核心数据结构**:
```c
struct deadline_data {
    struct list_head dispatch;          /* 分发链表 */
    struct dd_per_prio per_prio[DD_PRIO_COUNT]; /* 每优先级数据 */
    
    enum dd_data_dir last_dir;          /* 上次方向 */
    unsigned int batching;              /* 批处理计数 */
    unsigned int starved;              /* 饥饿计数 */
    
    int fifo_expire[DD_DIR_COUNT];     /* FIFO过期时间 */
    int fifo_batch;                    /* 批大小 */
    int writes_starved;                 /* 写饥饿阈值 */
    int front_merges;                   /* 前向合并开关 */
};

struct dd_per_prio {
    struct rb_root sort_list[DD_DIR_COUNT];  /* 排序红黑树 */
    struct list_head fifo_list[DD_DIR_COUNT]; /* FIFO链表 */
    sector_t latest_pos[DD_DIR_COUNT];       /* 最新位置 */
    struct io_stats_per_prio stats;
};
```

**调度算法**:
1. **读优先**: 默认 `read_expire = HZ/2`, `write_expire = 5*HZ`
2. **写饥饿控制**: `writes_starved = 2` (读可连续饥饿写的次数)
3. **批处理**: `fifo_batch = 16` (单次分发的最大请求数)
4. **优先级**: RT > BE > IDLE (实时 > 最佳努力 > 空闲)

### 4.3 BFQ (Budget Fair Queueing) 算法

**源码位置**: `/Users/sphinx/github/linux/block/bfq-iosched.c`

**核心概念**:
- **预算分配**: BFQ 按扇区数分配预算, 而非时间片
- **权重提升**: 交互式任务获得更高权重
- **B-WF2Q+**: 内部调度器保证按预算比例分配带宽

**关键参数**:
```c
static const u64 bfq_fifo_expire[2] = { NSEC_PER_SEC/4, NSEC_PER_SEC/8 };
static const int bfq_back_max = 16 * 1024;     /* KiB */
static const int bfq_back_penalty = 2;
static u64 bfq_slice_idle = NSEC_PER_SEC / 125;
static const int bfq_default_max_budget = 16 * 1024; /* 扇区 */
static const int bfq_async_charge_factor = 3;
```

### 4.4 算法对比表

| 特性 | mq-deadline | BFQ | Kyber |
|------|-------------|-----|-------|
| **调度基础** | 过期时间/FIFO | 预算比例 | 延迟目标 |
| **优先级** | 3级(RT/BE/IDLE) | 权重值 | 2级(RT/BE) |
| **饥饿控制** | writes_starved | 预算上限 | 延迟阈值 |
| **顺序优化** | 批处理 | slice_idle | batch |
| **适用场景** | 通用/SSD | 桌面/多媒体 | NVMe |

### 4.5 elv_may_queue 钩子

**源码位置**: `/Users/sphinx/github/linux/block/elevator.c` (第 60-69 行)

```c
static bool elv_iosched_allow_bio_merge(struct request *rq, struct bio *bio)
{
    struct request_queue *q = rq->q;
    struct elevator_queue *e = q->elevator;

    if (e->type->ops.allow_merge)
        return e->type->ops.allow_merge(q, rq, bio);

    return true;
}
```

**调度器合并决策钩子**:
- `allow_merge`: 允许 bio 合并到 request
- `request_merge`: 哈希查找后向合并
- `requests_merged`: 合并后回调

---

## 5. GenDisk 与 Partitions

### 5.1 struct gendisk

**源码位置**: `/Users/sphinx/github/linux/include/linux/blkdev.h` (第 144-225 行)

```c
struct gendisk {
    int major;                      /* 主设备号 */
    int first_minor;                /* 首个次设备号 */
    int minors;                     /* 支持的分区数 */
    
    char disk_name[DISK_NAME_LEN];  /* 磁盘名称 */
    
    struct xarray part_tbl;         /* 分区表 xarray */
    struct block_device *part0;      /* 整个磁盘 (0号分区) */
    
    const struct block_device_operations *fops; /* 块设备操作 */
    struct request_queue *queue;     /* 请求队列 */
    void *private_data;              /* 驱动私有数据 */
    
    struct bio_set bio_split;        /* bio split 内存池 */
    
    int flags;                       /* GENHD_FL_* 标志 */
#define GD_NEED_PART_SCAN      0
#define GD_READ_ONLY           1
#define GD_DEAD                2
#define GD_NATIVE_CAPACITY     3
#define GD_ADDED               4
#define GD_SUPPRESS_PART_SCAN  5
#define GD_OWNS_QUEUE          6
    
    struct timer_rand_state *random;
    struct disk_events *ev;
    
#ifdef CONFIG_BLK_DEV_ZONED
    unsigned int nr_zones;
    unsigned int zone_capacity;
    u8 __rcu *zones_cond;
#endif
};
```

### 5.2 partition 表结构

**分区数组管理**:
```c
// 使用 xarray 存储分区
struct xarray part_tbl;  // 分区表

// 添加分区流程 [partitions/core.c:294-405]
static struct block_device *add_partition(struct gendisk *disk, int partno,
        sector_t start, sector_t len, int flags,
        struct partition_meta_info *info)
{
    // 1. 分配 bdev
    bdev = bdev_alloc(disk, partno);
    
    // 2. 设置起始扇区和大小
    bdev->bd_start_sect = start;
    bdev_set_nr_sectors(bdev, len);
    
    // 3. 注册设备
    xa_insert(&disk->part_tbl, partno, bdev, GFP_KERNEL);
    bdev_add(bdev, devt);
}
```

### 5.3 add_disk() 注册流程

**源码位置**: `/Users/sphinx/github/linux/block/genhd.c` (第 585-612 行)

```c
int __must_check add_disk_fwnode(...)
{
    // __add_disk() 完成实际注册
    ret = __add_disk(parent, disk, groups, fwnode);
    
    if (!ret)
        add_disk_final(disk);  // 扫描分区表
    
    return ret;
}

static void add_disk_final(struct gendisk *disk)
{
    // 添加 part0 到设备模型
    bdev_add(disk->part0, ddev->devt);
    
    // 扫描分区
    if (get_capacity(disk) && disk_has_partscan(disk))
        disk_scan_partitions(disk, BLK_OPEN_READ);
    
    // 发送 uevent
    disk_uevent(disk, KOBJ_ADD);
}
```

**完整注册流程**:
```
alloc_disk()           → 分配 gendisk 结构
blk_alloc_queue()      → 分配 request_queue
device_add_disk()      → 注册到设备模型
    └─ add_disk_fwnode()
           ├─ __add_disk()
           │     ├─ blk_register_queue()
           │     ├─ bdi_register()
           │     └─ 设置 GD_OWNS_QUEUE
           └─ add_disk_final()
                 ├─ bdev_add(part0)
                 ├─ disk_scan_partitions()
                 │     └─ check_partition() → 各分区解析器
                 └─ disk_uevent(KOBJ_ADD)
```

### 5.4 分区扫描 (check_partition)

**源码位置**: `/Users/sphinx/github/linux/block/partitions/core.c`

```c
static int (*const check_part[])(struct parsed_partitions *) = {
#ifdef CONFIG_EFI_PARTITION
    efi_partition,          /* GPT */
#endif
#ifdef CONFIG_MSDOS_PARTITION
    msdos_partition,        /* MBR/DOS */
#endif
    // ... 其他分区格式
};

// 扫描入口
check_partition(disk)
    → iterate check_part[]  // 尝试各分区解析器
        → efi_partition()   // GPT
        → msdos_partition() // MBR
```

---

## 6. 知识点关联表格

### 6.1 核心数据结构关联

| 结构体 | 文件位置 | 关键字段 | 关联结构 |
|--------|----------|----------|----------|
| `struct bio` | blk_types.h:210 | bi_io_vec, bi_iter, bi_end_io | block_device, bio_set |
| `struct bio_vec` | bvec.h | bv_page, bv_len, bv_offset | bio |
| `struct request` | blk-mq.h:105 | q, mq_ctx, mq_hctx, end_io | request_queue, blk_mq_ctx |
| `struct request_queue` | blkdev.h:478 | elevator, mq_ops, queue_hw_ctx | gendisk, blk_mq_hw_ctx |
| `struct blk_mq_hw_ctx` | blk-mq.h:322 | dispatch, lock, tags | request_queue, blk_mq_ctx |
| `struct blk_mq_ctx` | blk-mq.h | rq_lists, index_hw | request_queue, blk_mq_hw_ctx |
| `struct gendisk` | blkdev.h:144 | part_tbl, queue, fops | request_queue, block_device |
| `struct block_device` | blk_types.h:41 | bd_disk, bd_queue, bd_start_sect | gendisk, request_queue |

### 6.2 函数调用路径

| 路径 | 源文件:行号 | 功能描述 |
|------|-------------|----------|
| submit_bio → submit_bio_noacct | blk-core.c:916→780 | bio 提交入口 |
| submit_bio_noacct → blk_mq_submit_bio | blk-core.c:884 | 转向 blk-mq 处理 |
| blk_mq_submit_bio → blk_mq_sched_insert_request | blk-mq.c | 请求插入调度器 |
| blk_mq_sched_insert_request → elv_may_queue | elevator.c:60 | 调度器合并决策 |
| blk_mq_run_hw_queue → blk_mq_sched_dispatch_requests | blk-mq.c:2387 | 触发硬件分发 |
| blk_mq_sched_dispatch_requests → hctx->ops->queue_rq | blk-mq.c (驱动) | 驱动处理请求 |
| bio_endio | bio.c:1749 | 完成回调触发 |

### 6.3 关键枚举与常量

| 枚举/常量 | 定义位置 | 说明 |
|-----------|----------|------|
| `REQ_OP_READ/WRITE/FLUSH...` | blk_types.h:347 | 请求操作类型 |
| `BLK_STS_OK/TIMEOUT/NOSPC...` | blk_types.h:98 | 块设备状态码 |
| `RQF_STARTED/MERGED/IO_STAT...` | blk-mq.h:34 | 请求标志 |
| `BLK_MQ_S_STOPPED/INACTIVE...` | blk-mq.h:719 | 硬件队列状态 |
| `HCTX_TYPE_DEFAULT/READ/POLL` | blk-mq.h:488 | 硬件队列类型 |
| `DD_RT_PRIO/BE_PRIO/IDLE_PRIO` | mq-deadline.c:48 | deadline 优先级 |

### 6.4 内存分配关键函数

| 函数 | 源文件 | 功能 |
|------|--------|------|
| `bio_alloc_bioset()` | bio.c:549 | 分配 bio + bio_vec |
| `bio_alloc_clone()` | bio.c:905 | 克隆 bio |
| `blk_mq_alloc_request()` | blk-mq.c | 分配 request |
| `blk_mq_rq_ctx_init()` | blk-mq.c:410 | 初始化 request |
| `bdev_alloc()` | blk.h | 分配 block_device |

### 6.5 同步机制

| 机制 | 作用域 | 用途 |
|------|--------|------|
| `hctx->lock` (spinlock) | 硬件队列 | 保护 dispatch 链表 |
| `q->queue_lock` (spinlock) | 请求队列 | 通用队列保护 |
| `q->elevator_lock` (mutex) | 请求队列 | 调度器切换保护 |
| `disk->open_mutex` | gendisk | open/close 同步 |
| `q->mq_freeze_lock` | 请求队列 | freeze 计数保护 |
| `percpu_ref q_usage_counter` | 请求队列 | 引用计数/freeze |

### 6.6 调度器算法特性

| 调度器 | 源码文件 | 核心算法 | 特色功能 |
|--------|----------|----------|----------|
| mq-deadline | mq-deadline.c | 过期时间 + FIFO | 前向合并, 优先级支持 |
| BFQ | bfq-iosched.c | B-WF2Q+ 预算分配 | 低延迟, 权重提升, cgroup |
| Kyber | kyber-iosched.c | 延迟目标控制 | 2级调度, sync/async分离 |

---

## 附录: 关键源码行号索引

| 源码文件 | 关键行号 | 内容 |
|----------|----------|------|
| blk_types.h | 210-287 | struct bio 定义 |
| blk_types.h | 347-379 | enum req_op 定义 |
| blkdev.h | 144-225 | struct gendisk |
| blkdev.h | 478-650 | struct request_queue |
| blk-mq.h | 105-219 | struct request |
| blk-mq.h | 322-463 | struct blk_mq_hw_ctx |
| bio.c | 549-636 | bio_alloc_bioset() |
| bio.c | 1749-1793 | bio_endio() |
| blk-mq.c | 2344-2389 | blk_mq_run_hw_queue() |
| blk-mq.c | 4630-4679 | blk_mq_init_allocated_queue() |
| blk-core.c | 780-892 | submit_bio_noacct() |
| blk-core.c | 916-927 | submit_bio() |
| elevator.c | 268-314 | elv_merge() |
| mq-deadline.c | 30-39 | 参数常量 |
| mq-deadline.c | 81-104 | deadline_data 结构 |
| bfq-iosched.c | 165-218 | BFQ 参数常量 |
| genhd.c | 585-612 | add_disk_fwnode() |
| genhd.c | 1446-1506 | __alloc_disk_node() |
| partitions/core.c | 92-175 | check_partition() |
| partitions/core.c | 294-405 | add_partition() |

---

**文档版本**: R1  
**分析日期**: 2026-04-26  
**源码目录**: /Users/sphinx/github/linux  
**关键源码文件**:
- `block/blk-core.c` - 块设备核心
- `block/blk-mq.c` - 多队列块设备
- `block/bio.c` - bio 管理
- `block/elevator.c` - IO调度器框架
- `block/genhd.c` - 磁盘管理
- `block/partitions/core.c` - 分区扫描
- `include/linux/blk_types.h` - 类型定义
- `include/linux/blkdev.h` - 设备接口
- `include/linux/blk-mq.h` - MQ接口
