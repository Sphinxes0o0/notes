---
title: 块任务与实时迁移
---

# 块任务与实时迁移分析

## BlockJob 结构

```c
struct BlockJob {
    Job job;                          // 基础作业

    BlockBackend *blk;                // 块设备后端
    BdrvChild *children;             // 子节点

    BlockJobType *job_type;          // 作业类型
    void *opaque;                    // 私有数据
};

// 状态机
// CREATED → RUNNING → COMMITTING/ABORTING → FINISHED
```

## BackupBlockJob

```c
// block/backup.c
struct BackupBlockJob {
    BlockJob common;
    BlockDriverState *source_bs;    // 源设备
    BlockDriverState *target_bs;    // 目标设备
    BdrvDirtyBitmap *sync_bitmap;   // 同步位图
    MirrorSyncMode sync_mode;        // 同步模式
    BitmapSyncMode bitmap_mode;      // 位图同步模式
    BlockCopyState *bcs;            // 块复制状态
};

// 同步模式
enum MirrorSyncMode {
    MIRROR_SYNC_MODE_NONE,          // 无同步
    MIRROR_SYNC_MODE_TOP,           // 顶层
    MIRROR_SYNC_MODE_BITMAP,        // 位图
    MIRROR_SYNC_MODE_FULL,          // 完全同步
};
```

## MirrorBlockJob

```c
// block/mirror.c
struct MirrorBlockJob {
    BlockJob common;
    BlockBackend *target;            // 目标后端
    BdrvDirtyBitmap *dirty_bitmap;  // 脏位图
    unsigned long *cow_bitmap;       // COW 区域追踪
    unsigned long *in_flight_bitmap; // 飞行中位图
    QSIMPLEQ_HEAD(, MirrorBuffer) buf_free; // 缓冲区池
};
```

## CommitBlockJob

```c
// block/commit.c
struct CommitBlockJob {
    BlockJob common;
    BlockDriverState *commit_top_bs; // 中间层
    BlockBackend *top, *base;
    BlockDriverState *base_bs;
};
```

## Dirty Bitmap

```c
// block/dirty-bitmap.c
struct BdrvDirtyBitmap {
    BlockDriverState *bs;            // 关联的块设备
    HBitmap *bitmap;                 // 核心位图实现
    bool busy;                       // 正在被迭代器使用
    BdrvDirtyBitmap *successor;     // 用于渐进式位图
    char *name;                      // 名称
    int64_t size;                   // 大小
    bool disabled;                  // 已禁用
    bool readonly;                   // 只读
    bool persistent;                 // 可持久化
    bool inconsistent;               // 损坏/无效
};
```

## 块复制 API

```c
// block/block-copy.c
struct BlockCopyState {
    BdrvChild *source;              // 源
    BdrvChild *target;              // 目标
    BdrvDirtyBitmap *copy_bitmap;  // 复制位图
};

BlockCopyState *block_copy_state_new(...);
void block_copy_async();
void block_copy_call_finished();
void block_copy_call_succeeded();
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `job.c` | 作业框架 |
| `backup.c` | 备份块作业 |
| `mirror.c` | 镜像块作业 |
| `commit.c` | 提交块作业 |
| `block-copy.c` | 并行块复制 API |
| `dirty-bitmap.c` | 脏位图跟踪 |
