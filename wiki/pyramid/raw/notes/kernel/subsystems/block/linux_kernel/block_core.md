# Linux 内核 Block Layer 核心数据结构与函数

## 1. Bio 提交路径

### __submit_bio() - Bio 提交

**文件**: `block/blk-core.c:627-650`

```c
static void __submit_bio(struct bio *bio)
{
	struct blk_plug plug;

	blk_start_plug(&plug);

	if (!bdev_test_flag(bio->bi_bdev, BD_HAS_SUBMIT_BIO)) {
		blk_mq_submit_bio(bio);
	} else if (likely(bio_queue_enter(bio) == 0)) {
		struct gendisk *disk = bio->bi_bdev->bd_disk;
	
		if ((bio->bi_opf & REQ_POLLED) &&
		    !(disk->queue->limits.features & BLK_FEAT_POLL)) {
			bio->bi_status = BLK_STS_NOTSUPP;
			bio_endio(bio);
		} else {
			disk->fops->submit_bio(bio);
		}
		blk_queue_exit(disk->queue);
	}

	blk_finish_plug(&plug);
}
```

---

## 2. struct bio

**文件**: `include/linux/blk_types.h:210-287`

```c
struct bio {
	struct bio		*bi_next;	/* request queue link */
	struct block_device	*bi_bdev;
	blk_opf_t		bi_opf;		/* REQ_OP + req_flags */
	unsigned short		bi_flags;
	unsigned short		bi_ioprio;
	enum rw_hint		bi_write_hint;
	u8			bi_write_stream;
	blk_status_t		bi_status;

	atomic_t		__bi_remaining;

	struct bio_vec		*bi_io_vec;
	struct bvec_iter	bi_iter;

	union {
		blk_qc_t		bi_cookie;
		unsigned int		__bi_nr_segments;
	};
	bio_end_io_t		*bi_end_io;
	void			*bi_private;

	struct bio_set		*bi_pool;

	unsigned short		bi_vcnt;	/* # of bio_vec's */
	unsigned short		bi_max_vecs;
	atomic_t		__bi_cnt;
};
```

**关键字段**:
- `bi_opf`: 操作类型 (REQ_OP_READ, REQ_OP_WRITE 等) 和标志
- `bi_iter`: 迭代器，包含 `bi_sector`, `bi_size`, `bi_idx`, `bi_bvec_done`
- `bi_io_vec`: 物理页向量数组
- `bi_status`: I/O 完成状态

---

## 3. struct block_device

**文件**: `include/linux/blkdev.h:41-82`

```c
struct block_device {
	sector_t		bd_start_sect;
	sector_t		bd_nr_sectors;
	struct gendisk *	bd_disk;
	struct request_queue *	bd_queue;
	struct disk_stats __percpu *bd_stats;
	unsigned long		bd_stamp;
	atomic_t		__bd_flags;

	dev_t			bd_dev;
	struct address_space	*bd_mapping;
	atomic_t		bd_openers;
	spinlock_t		bd_size_lock;
	void *			bd_claiming;
	void *			bd_holder;
	struct kobject		*bd_holder_dir;
	int			bd_holders;
	struct partition_meta_info *bd_meta_info;
	struct device		bd_device;
};
```

---

## 4. struct gendisk

**文件**: `include/linux/blkdev.h:144-225`

```c
struct gendisk {
	int			major;
	int			first_minor;
	int			minors;
	char			disk_name[DISK_NAME_LEN];

	struct xarray		part_tbl;
	struct block_device	*part0;

	const struct block_device_operations *fops;
	struct request_queue	*queue;
	void			*private_data;

	int			flags;
#define GD_NEED_PART_SCAN		0
#define GD_READ_ONLY			1
#define GD_DEAD				2

	struct mutex		open_mutex;
	unsigned		open_partitions;
	struct backing_dev_info	*bdi;
	struct timer_rand_state	*random;
	struct disk_events	*ev;

	int			node_id;
	struct badblocks	*bb;
};
```

---

## 5. struct request_queue

**文件**: `include/linux/blkdev.h:478-650`

```c
struct request_queue {
	void			*queuedata;
	struct elevator_queue	*elevator;

	const struct blk_mq_ops	*mq_ops;

	struct blk_mq_ctx __percpu	*queue_ctx;

	unsigned long		queue_flags;

	unsigned int		rq_timeout;
	unsigned int		queue_depth;

	refcount_t		refs;

	unsigned int		nr_hw_queues;
	struct blk_mq_hw_ctx * __rcu *queue_hw_ctx;

	struct percpu_ref	q_usage_counter;

	struct gendisk		*disk;

	struct queue_limits	limits;

	int			id;
	unsigned int		nr_requests;
	unsigned int		async_depth;

	struct blk_flush_queue	*fq;
	struct list_head	flush_list;
};
```

---

## 6. struct request

**文件**: `include/linux/blk-mq.h:105-219`

```c
struct request {
	struct request_queue	*q;
	struct blk_mq_ctx	*mq_ctx;
	struct blk_mq_hw_ctx	*mq_hctx;

	blk_opf_t		cmd_flags;
	req_flags_t		rq_flags;

	int			tag;
	int			internal_tag;

	unsigned int		timeout;

	unsigned int		__data_len;
	sector_t		__sector;

	struct bio		*bio;
	struct bio		*biotail;

	union {
		struct list_head	queuelist;
		struct request		*rq_next;
	};

	struct block_device	*part;

	enum mq_rq_state	state;
	atomic_t		ref;

	unsigned long		deadline;

	union {
		struct hlist_node	hash;
		struct llist_node	ipi_list;
	};

	union {
		struct rb_node		rb_node;
		struct bio_vec		special_vec;
	};

	struct {
		struct io_cq		*icq;
		void			*priv[2];
	} elv;

	rq_end_io_fn		*end_io;
	void			*end_io_data;
};
```

---

## 7. blk_mq_submit_bio() - Multi-queue 提交

**文件**: `block/blk-mq.c:3141-3264`

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

	rq = blk_mq_peek_cached_request(plug, q, bio->bi_opf);

	if (bio_zone_write_plugging(bio)) {
		nr_segs = bio->__bi_nr_segments;
		if (rq)
			blk_queue_exit(q);
		goto new_request;
	}

	if (!rq) {
		if (unlikely(bio_queue_enter(bio)))
			return;
	}

	if (unlikely(bio_unaligned(bio, q))) {
		bio_io_error(bio);
		goto queue_exit;
	}

	bio = __bio_split_to_limits(bio, &q->limits, &nr_segs);
	if (!bio)
		goto queue_exit;

	if (!bio_integrity_prep(bio))
		goto queue_exit;

	blk_mq_bio_issue_init(q, bio);
	if (blk_mq_attempt_bio_merge(q, bio, nr_segs))
		goto queue_exit;

new_request:
	if (rq) {
		blk_mq_use_cached_rq(rq, plug, bio);
	} else {
		rq = blk_mq_get_new_requests(q, plug, bio);
	}

	blk_mq_bio_to_request(rq, bio, nr_segs);

	if (plug) {
		blk_add_rq_to_plug(plug, rq);
		return;
	}

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

---

## 8. blk_mq_bio_to_request()

**文件**: `block/blk-mq.c:2685-2705`

```c
static void blk_mq_bio_to_request(struct request *rq, struct bio *bio,
		unsigned int nr_segs)
{
	if (bio->bi_opf & REQ_RAHEAD)
		rq->cmd_flags |= REQ_FAILFAST_MASK;

	rq->bio = rq->biotail = bio;
	rq->__sector = bio->bi_iter.bi_sector;
	rq->__data_len = bio->bi_iter.bi_size;
	rq->nr_phys_segments = nr_segs;

	err = blk_crypto_rq_bio_prep(rq, bio, GFP_NOIO);
	WARN_ON_ONCE(err);
}
```

---

## 9. 数据结构关系

```
+----------------+      +------------------+      +-------------------+
|     Bio        |      |     Request      |      |  Request_Queue   |
+----------------+      +------------------+      +-------------------+
| bi_bdev        |----->| q                |<-----| elevator           |
| bi_opf         |      | cmd_flags        |      | mq_ops            |
| bi_iter        |      | __sector         |      | queue_hw_ctx[]    |
| bi_io_vec[]    |      | __data_len       |      | nr_hw_queues      |
| bi_status      |      | bio, biotail     |----->| nr_requests       |
+----------------+      | mq_ctx           |      +-------------------+
                         | mq_hctx          |
                         +------------------+
```

---

## 10. Bio 到 Request 提交流程

```
submit_bio()
    │
    v
submit_bio_noacct()
    │
    v
__submit_bio()
    │
    ├─[BD_HAS_SUBMIT_BIO not set]─> blk_mq_submit_bio()
    │                                        │
    │                                        v
    │                                 blk_mq_bio_to_request()
    │                                        │
    │                                        v
    │                                 blk_mq_insert_request() /
    │                                 blk_mq_try_issue_directly()
    │
    └─[BD_HAS_SUBMIT_BIO set]────> disk->fops->submit_bio()
```

---

## 11. 关键源码位置

| 结构体/函数 | 文件 | 行号 |
|-------------|------|------|
| struct bio | include/linux/blk_types.h | 210-287 |
| struct request | include/linux/blk-mq.h | 105-219 |
| struct request_queue | include/linux/blkdev.h | 478-650 |
| struct block_device | include/linux/blkdev.h | 41-82 |
| struct gendisk | include/linux/blkdev.h | 144-225 |
| __submit_bio | block/blk-core.c | 627-650 |
| blk_mq_submit_bio | block/blk-mq.c | 3141-3264 |
| blk_mq_bio_to_request | block/blk-mq.c | 2685-2705 |
