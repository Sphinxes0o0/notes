---
type: index
tags: [linux-kernel, block-device]
created: 2026-05-22
---

# Linux Kernel — Block Layer

> Block device framework, multi-queue support, and I/O schedulers

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/block/linux-kernel-block-core]] | Block layer: bio/request/gendisk, block_device | linux-kernel, block |
| [[entities/linux/kernel/block/linux-kernel-block-mq]] | blk-mq: hctx/tags, software queue, hardware queue | linux-kernel, block, mq |
| [[entities/linux/kernel/block/linux-kernel-block-scheduler]] | IO schedulers: mq-deadline, BFQ, elevator | linux-kernel, block, scheduler |
| [[entities/lsm-tree]] | LSM-tree: Log Structured Merge Tree，写优化存储结构，LevelDB/RocksDB核心 | storage, LSM-tree, key-value |
| [[entities/sstable]] | SSTable: Sorted String Table磁盘格式，Data/Filter/Index Block，Compaction合并 | storage, SSTable, LevelDB |

## Cross-References

- [[kernel-io-index]] — Block layer is the underlying target for io_uring and VFS operations
- [[kernel-sched-index]] — blk-mq per-CPU queues interact with scheduler load balancing
- [[kernel-virt-index]] — Virtio-blk is the paravirtual block device for KVM guests
- [[qemu-index]] — QEMU block layer (QCOW2, BDS graph) emulates storage devices
