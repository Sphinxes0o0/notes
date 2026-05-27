# Linux 块设备子系统 (block/) 文档索引

## 文档清单

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [block_core.md](block_core.md) | Block 核心结构: bio, request, request_queue, gendisk | block/blk-core.c, blk-mq.c |
| [block_mq.md](block_mq.md) | MultiQueue 提交路径: blk_mq_submit_bio, hctx, tag | block/blk-mq.c |
| [block_request.md](block_request.md) | Request 处理: 分配, 合并, 分发, 完成 | block/blk-mq.c |
| [block_scheduler.md](block_scheduler.md) | I/O Scheduler: elevator, mq-deadline, bfq | block/elevator.c |
| [block_genhd.md](block_genhd.md) | GenHD 和分区: alloc_disk, add_partition, MSDOS/GPT | block/genhd.c |
| [block_deep_dive_r1.md](block_deep_dive_r1.md) | 深度分析 R1: bio结构, blk-mq, request生命周期, I/O scheduler | block/ |
| [block_deep_dive_r2.md](block_deep_dive_r2.md) | 深度分析 R2: blk_mq_submit_bio, blk_mq_alloc_request, blk_mq_start_request, blk_mq_complete_request | block/ |

---

## 1. Block 核心数据结构 (block_core.md)

### 关键内容
- `struct bio`: I/O 提交单元，包含 bi_opf, bi_iter, bi_io_vec
- `struct request`: 调度单元，包含 cmd_flags, __sector, __data_len
- `struct request_queue`: 请求队列管理
- `struct block_device`: 块设备/分区表示
- `struct gendisk`: 通用磁盘结构
- `__submit_bio()`: Bio 提交入口
- `blk_mq_submit_bio()`: Multi-queue 提交

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| __submit_bio | block/blk-core.c:627-650 |
| blk_mq_submit_bio | block/blk-mq.c:3141-3264 |
| blk_mq_bio_to_request | block/blk-mq.c:2685-2705 |

---

## 2. MultiQueue (block_mq.md)

### 关键内容
- `struct blk_mq_hw_ctx`: 硬件队列，每硬件队列一个
- `struct blk_mq_ctx`: Per-CPU 软件队列
- `struct blk_mq_tags`: 标签管理
- `blk_mq_submit_bio()`: Multi-queue 提交主入口
- `blk_mq_try_issue_directly()`: 直接发行
- `blk_mq_run_hw_queue()`: 运行硬件队列
- 调度器集成接口

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| blk_mq_submit_bio | block/blk-mq.c:3141-3264 |
| blk_mq_try_issue_directly | block/blk-mq.c:2345-2400 |
| blk_mq_insert_request | block/blk-mq.c:2295-2340 |
| blk_mq_run_hw_queue | block/blk-mq.c:1850-1920 |
| blk_mq_complete_request | block/blk-mq.c:1740-1790 |

---

## 3. Request 处理 (block_request.md)

### 关键内容
- `struct request`: cmd_flags, rq_flags, timeout, deadline
- Request 分配: `blk_mq_alloc_rq()`
- Request 合并: `blk_try_merge()`, `blk_mq_attempt_bio_merge()`
- Request 分发: `__blk_mq_dispatch_rq_list()`
- Request 完成: `blk_mq_complete_request()`, `blk_mq_end_request()`
- Request 超时处理

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| blk_mq_alloc_rq | block/blk-mq.c:2555-2600 |
| blk_mq_attempt_bio_merge | block/blk-mq.c:3085-3140 |
| blk_try_merge | block/blk-merge.c:40-80 |
| __blk_mq_dispatch_rq_list | block/blk-mq.c:1950-2100 |

---

## 4. I/O Scheduler (block_scheduler.md)

### 关键内容
- `struct elevator_type`: 调度器类型定义
- `struct elevator_queue`: 调度器队列
- mq-deadline: 最后期限调度器
- bfq: Budget Fair Queueing 调度器
- dispatch 钩子: `dd_dispatch_request()`, `bfq_dispatch_request()`
- 调度器切换

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| elevator_init_fn | block/elevator.c | 450-500 |
| dd_dispatch_request | block/mq-deadline.c | 300-350 |
| bfq_dispatch_request | block/bfq-iosched.c | 2500-2600 |

---

## 5. GenHD 和分区 (block_genhd.md)

### 关键内容
- `struct gendisk`: major, minors, part_tbl, queue, fops
- `struct block_device_operations`: open, release, ioctl
- `alloc_disk()`: 磁盘分配
- `device_add_disk()`: 磁盘注册
- `add_partition()`: 分区添加
- MSDOS/MBR 分区表解析
- GPT 分区表解析

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| alloc_disk | block/genhd.c | 650-690 |
| device_add_disk | block/genhd.c | 700-780 |
| add_partition | block/partitions/core.c | 100-200 |
| rescan_partitions | block/partitions/core.c | 300-400 |
| msdos_partition | block/partitions/msdos.c | 50-150 |
| gpt_partition | block/partitions/efi.c | 100-200 |

---

## 架构总览

```
                    ┌─────────────────────────────────────────┐
                    │         用户空间进程                     │
                    └─────────────────┬───────────────────────┘
                                      │
                                      │ write()/read()
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │      submit_bio() / submit_bio_noacct() │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────────┐
                    ▼                                       ▼
        ┌───────────────────────┐               ┌───────────────────────┐
        │   传统设备路径         │               │    blk_mq_submit_bio() │
        │  __submit_bio()       │               │    (Multi-Queue)       │
        │  disk->fops->submit  │               └──────────┬──────────────┘
        └───────────────────────┘                          │
                                                              ▼
                                                ┌───────────────────────┐
                                                │  blk_mq_bio_to_request │
                                                └──────────┬──────────────┘
                                                          │
                                          ┌───────────────┴───────────────┐
                                          ▼                               ▼
                              ┌─────────────────────┐       ┌─────────────────────┐
                              │  blk_mq_insert_request│       │ blk_add_rq_to_plug  │
                              │  (调度器队列)        │       │ (批量 plug)         │
                              └──────────┬──────────┘       └─────────────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │ __blk_mq_dispatch   │
                              │ _rq_list()          │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │  hctx->queue_rq()   │
                              │  (硬件队列回调)      │
                              └─────────────────────┘


gendisk 结构:
┌─────────────────────────────────────────┐
│ struct gendisk                          │
│  ├── major, first_minor, minors         │
│  ├── part_tbl (xa_array) ──► 分区表    │
│  ├── queue ──► request_queue            │
│  ├── fops ──► block_device_operations  │
│  └── part0 ──► 整个磁盘 block_device   │
└─────────────────────────────────────────┘
```

---

## Bio → Request → Dispatch 完整路径

```
submit_bio()
    │
    ▼
submit_bio_noacct()
    │
    ▼
__submit_bio()
    │
    ├─[BD_HAS_SUBMIT_BIO not set]─> blk_mq_submit_bio()
    │                                    │
    │                                    ├─> blk_mq_peek_cached_request()
    │                                    ├─> bio_queue_enter()
    │                                    ├─> __bio_split_to_limits()
    │                                    ├─> bio_integrity_prep()
    │                                    ├─> blk_mq_attempt_bio_merge()
    │                                    ├─> blk_mq_get_new_requests()
    │                                    │     └─> blk_mq_get_request()
    │                                    ├─> blk_mq_bio_to_request()
    │                                    └─> blk_add_rq_to_plug() / 直接分发
    │
    └─[BD_HAS_SUBMIT_BIO set]────> disk->fops->submit_bio()
```
