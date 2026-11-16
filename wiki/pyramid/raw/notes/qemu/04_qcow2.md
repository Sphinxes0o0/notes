---
title: QCOW2 格式实现
---

# QCOW2 格式实现分析

## L1/L2 表结构

```c
#define L1E_SIZE 8                      // L1 条目 = 8 字节
#define L2E_SIZE_NORMAL 8              // 普通 L2 条目 = 8 字节
#define L2E_SIZE_EXTENDED 16           // 扩展 L2 条目 = 16 字节

// L2 条目标志
#define QCOW_OFLAG_COPIED (1ULL << 63)     // 引用计数 == 1 优化
#define QCOW_OFLAG_COMPRESSED (1ULL << 62) // 压缩簇
```

## BDRVQcow2State 关键字段

```c
struct BDRVQcow2State {
    int64_t l1_table_offset;           // L1 表磁盘偏移
    uint64_t *l1_table;                // 内存中的 L1 表
    int l1_size;                       // L1 条目数量

    int l2_bits;                       // L2 表位数
    int l2_size;                       // L2 表大小
    Qcow2Cache *l2_table_cache;        // L2 表缓存
    Qcow2Cache *refcount_block_cache;  // 引用计数缓存

    uint64_t *refcount_table;          // 引用计数表
    int refcount_table_size;           // 引用计数表大小
};
```

## 簇类型

```c
enum QCow2ClusterType {
    QCOW2_CLUSTER_UNALLOCATED,     // 未分配
    QCOW2_CLUSTER_ZERO_PLAIN,      // 读取为零，未分配
    QCOW2_CLUSTER_ZERO_ALLOC,      // 已分配，读取为零
    QCOW2_CLUSTER_NORMAL,          // 正常分配的数据
    QCOW2_CLUSTER_COMPRESSED,      // 压缩数据
};
```

## 引用计数管理

### 引用计数编码

- 可变长度编码: 1, 2, 4, 8, 16 位每条目
- `get_refcount_ro0` 到 `get_refcount_ro6` 不同宽度读取

### 核心函数

```c
// qcow2-refcount.c
update_refcount()                    // 核心引用计数更新
qcow2_alloc_clusters()              // 分配簇
qcow2_free_clusters()               // 释放簇
```

## 快照

```c
struct QCowSnapshot {
    uint64_t l1_table_offset;       // L1 表偏移
    int l1_size;                    // L1 大小
    uint64_t vm_state_size;         // VM 状态大小
    uint32_t date_sec;              // 秒级时间戳
    uint32_t date_nsec;             // 纳秒级时间戳
    uint64_t vm_clock_nsec;         // VM 时钟
    char *name;                     // 快照名称
    char *id_str;                   // 快照 ID
};
```

## 压缩

```c
#define QCOW2_COMPRESSED_SECTOR_SIZE 512U

// 压缩簇描述符存储在 L2 条目中
// QCOW_OFLAG_COMPRESSED 标志标记压缩簇
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `qcow2.c` | QCOW2 驱动, L1/L2 表管理 |
| `qcow2-refcount.c` | 引用计数管理 |
| `qcow2-cluster.c` | 簇分配 |
| `qcow2-snapshot.c` | 快照处理 |
