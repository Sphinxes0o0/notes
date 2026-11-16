---
type: entity
tags: [linux-kernel, block-layer, bio, request, gendisk]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel Block Layer Core

## 定义

块设备层 (Block Layer) 是 Linux 存储栈的核心，负责接收上层 I/O 请求、组织调度、向下提交给存储设备。主要数据结构包括 bio (I/O 提交单元)、request (调度单元)、request_queue、gendisk。

## 关键要点

- **bio**: I/O 提交单元，包含 bi_opf (操作类型)、bi_iter (迭代器)、bi_io_vec (页向量)
- **request**: 调度单元，从 bio 转换而来，包含 cmd_flags、__sector、__data_len
- **request_queue**: 请求队列，管理 bio → request 的转换和调度
- **gendisk**: 通用磁盘结构，包含 part_tbl (分区表)、queue (请求队列)、fops (操作函数)
- **block_device**: 块设备/分区表示，bd_disk 指向所属 gendisk
- **__submit_bio()**: Bio 提交入口，分发到 blk_mq_submit_bio() 或传统路径

## Bio 到 Request 提交流程

```
submit_bio()
    ↓
submit_bio_noacct()
    ↓
__submit_bio()
    ├─[BD_HAS_SUBMIT_BIO not set]→ blk_mq_submit_bio()
    │                                    ├─> blk_mq_bio_to_request()
    │                                    └─> blk_mq_insert_request()
    │
    └─[BD_HAS_SUBMIT_BIO set]→ disk->fops->submit_bio()
```

## 核心数据结构

### bio
```c
struct bio {
    struct block_device *bi_bdev;
    blk_opf_t bi_opf;              // 操作类型 + 标志
    struct bvec_iter bi_iter;       // 迭代器 (sector, size, idx)
    struct bio_vec *bi_io_vec;     // 物理页向量数组
    blk_status_t bi_status;         // 完成状态
    bio_end_io_t *bi_end_io;       // 完成回调
    // ...
};
```

### request
```c
struct request {
    struct request_queue *q;
    blk_opf_t cmd_flags;           // 命令标志
    unsigned int __data_len;       // 数据长度
    sector_t __sector;             // 起始扇区
    struct bio *bio, *biotail;     // 关联的 bio 链表
    struct blk_mq_ctx *mq_ctx;     // 软件队列上下文
    struct blk_mq_hw_ctx *mq_hctx; // 硬件队列上下文
    // ...
};
```

### gendisk
```c
struct gendisk {
    int major, first_minor, minors;
    struct xarray part_tbl;        // 分区表
    struct block_device *part0;    // 整个磁盘
    struct request_queue *queue;   // 请求队列
    const struct block_device_operations *fops;  // 操作函数
    // ...
};
```

## 相关概念

- [[entities/linux/kernel/block/linux-kernel-block-mq]] — Multi-Queue 块层实现
- [[entities/linux/kernel/block/linux-kernel-block-scheduler]] — I/O 调度器框架
- [[entities/linux/kernel/mm/linux-kernel-mm-swap]] — swap 设备是块设备

## 来源详情

- [[sources/notes-kernel]] — block_core.md
