---
type: entity
tags: [linux-kernel, memory-management, swap, anon-page]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel Swap Subsystem

## 定义

Swap 子系统负责将不活跃的匿名页面换出到磁盘，以释放物理内存。当物理内存不足时，kswapd 守护线程和直接回收路径会将被淘汰的页面写入 swap 设备。

## 关键要点

- **swap_info_struct**: 描述每个 swap 设备/文件，包含 swap_map、cluster_info、extent_root
- **swp_entry_t**: 软件 PTE 编码，`val = (type << SWP_TYPE_SHIFT) | offset`
- **Swap Cluster**: SWAPFILE_CLUSTER=256 页为单位管理 swap 空间
- **Swap Cache**: XA Tree 存储 swap slot → folio 的映射，加速 swap-in
- **swapin_readahead**: 换入时预读，支持基于 cluster 或 VMA 的预读策略
- **swapon/swapoff**: 系统调用，启用/禁用 swap 空间
- **zswap**: 内核压缩内存作为 swap 的缓存

## Swap 工作流程

### Swap-out
```
页面回收选择匿名页
    ↓
folio_alloc_swap() — 分配 swap slot
    ↓
加入 swap cache
    ↓
swap_writepage() — 写入 swap 设备
    ↓
更新 PTE 为 swp_entry
```

### Swap-in
```
缺页中断发现 swap entry
    ↓
do_swap_page()
    ↓
检查 swap cache
    ↓
swapin_readahead() — 可选预读
    ↓
swap_readpage() — 从 swap 设备读取
    ↓
映射页面到虚拟地址
```

## 核心数据结构

### swap_info_struct
```c
struct swap_info_struct {
    unsigned char *swap_map;      // 每个 slot 的使用计数
    struct swap_cluster_info *cluster_info;  // cluster 管理
    struct list_head free_clusters;   // 空闲 cluster 链表
    struct block_device *bdev;   // 底层块设备
    // ...
};
```

### swp_entry_t
```c
typedef struct { unsigned long val; } swp_entry_t;
// val = (type << SWP_TYPE_SHIFT) | offset
// SWP_TYPE_SHIFT = 59 - 5 = 54 (MAX_SWAPFILES=32)
```

## 相关概念

- [[entities/linux/kernel/mm/linux-kernel-mm-page-reclaim]] — 页面回收触发 swap-out
- [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]] — do_swap_page 处理 swap 换入
- [[entities/linux/kernel/block/linux-kernel-block-core]] — swap 设备是块设备

## 来源详情

- [[sources/notes-kernel]] — mm_swap.md
