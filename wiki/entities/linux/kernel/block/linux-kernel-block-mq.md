---
type: entity
tags: [linux-kernel, block-layer, multi-queue, blk-mq, hctx]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel Block MultiQueue (blk-mq)

## 定义

blk-mq (Block MultiQueue) 是 Linux 为现代多核 CPU 和高速存储设备 (NVMe SSD) 设计的块层多队列实现。每个 CPU 有独立的软件队列，多个硬件队列并行处理 I/O，大幅减少锁竞争。

## 关键要点

- **Per-CPU 软件队列**: 每个 CPU 有独立的 `blk_mq_ctx`，包含 rq_lists[]
- **硬件队列 (hctx)**: 每个硬件队列有独立的 dispatch 列表和标签集
- **blk_mq_hw_ctx**: 硬件队列上下文，核心字段包括 tags、sched_tags、queue_rq 回调
- **blk_mq_tags**: 标签管理，每个请求分配唯一标签用于跟踪
- **blk_mq_submit_bio()**: Multi-Queue 提交入口，做合并检查后转换为 request
- **blk_mq_ops**: 驱动操作接口，核心是 queue_rq 回调
- **调度器集成**: 通过 elevator_mq_ops 与 I/O 调度器交互

## 架构

```
应用
  ↓
Per-CPU 软件队列 (blk_mq_ctx → rq_lists[])
  ↓
硬件队列 (blk_mq_hw_ctx)
  ↓
磁盘驱动 (queue_rq 回调)
  ↓
NVMe / SSD / HDD
```

## 核心数据结构

### blk_mq_hw_ctx
```c
struct blk_mq_hw_ctx {
    spinlock_t lock;
    struct list_head dispatch;      // 待分发请求列表
    struct sbitmap ctx_map;        // 软件队列位图
    struct blk_mq_tags *tags;    // 请求标签
    struct blk_mq_tags *sched_tags; // 调度器标签
    struct request_queue *queue;  // 所属请求队列
    const struct blk_mq_ops *ops; // 驱动操作
    unsigned short type;          // HCTX_TYPE_xxx
    unsigned int nr_ctx;         // 软件队列数量
    struct blk_mq_ctx **ctxs;    // 软件队列数组
    // ...
};
```

### blk_mq_ops
```c
struct blk_mq_ops {
    blk_status_t (*queue_rq)(struct blk_mq_hw_ctx *,
                 const struct blk_mq_queue_data *); // 核心回调
    int (*get_budget)(struct request_queue *);
    void (*put_budget)(struct request_queue *, int);
    int (*timeout)(struct request *);
    int (*poll)(struct blk_mq_hw_ctx *, struct io_comp_batch *);
    void (*complete)(struct request *);
    // ...
};
```

## 请求提交流程

```
blk_mq_submit_bio()
    ↓
blk_mq_peek_cached_request() — 检查 plug 缓存
    ↓
__bio_split_to_limits() — 分割 bio
    ↓
blk_mq_attempt_bio_merge() — 尝试合并
    ↓
blk_mq_get_new_requests() — 获取标签，分配 request
    ↓
blk_mq_bio_to_request() — 转换 bio → request
    ↓
blk_add_rq_to_plug() / blk_mq_try_issue_directly()
```

## 相关概念

- [[entities/linux/kernel/block/linux-kernel-block-core]] — 块层核心数据结构
- [[entities/linux/kernel/block/linux-kernel-block-scheduler]] — I/O 调度器集成

## 来源详情

- [[sources/github-sphinxes0o0-notes-kernel]] — block_mq.md
## Related Concepts

- [[entities/linux/kernel/virt/linux-kernel-virt-kvm]] — KVM虚拟机块设备后端
