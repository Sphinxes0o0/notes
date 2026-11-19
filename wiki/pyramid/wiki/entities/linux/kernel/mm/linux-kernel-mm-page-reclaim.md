---
type: entity
tags: [linux-kernel, memory-management, lru, kswapd, reclaim]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel Page Reclaim Mechanism

## 定义

页面回收 (Page Reclaim) 是 Linux 内核释放物理内存的机制，包括 kswapd 后台回收和直接回收 (direct reclaim)。当内存压力达到低水位时，kswapd 被唤醒扫描 LRU 链表，将不活跃页面换出或释放。

## 关键要点

- **LRU (Least Recently Used)**: 链表组织非活跃/活跃、匿名/文件页面
- **Multi-Gen LRU (CONFIG_LRU_GEN)**: 替代传统 LRU，按代数追踪页面访问历史
- **kswapd**: 每个 NUMA 节点的后台守护线程，负责页面回收
- **watermark**: WMARK_MIN / WMARK_LOW / WMARK_HIGH 水位线控制回收触发
- **folio_check_references()**: 引用检查决定页面是激活、保持还是回收
- **Direct Reclaim**: 页面分配器在慢路径直接调用 shrink_zones()
- **swappiness**: 控制匿名页和文件页的回收倾向

## LRU 链表类型

| LRU 类型 | 说明 |
|----------|------|
| LRU_INACTIVE_ANON | 非活跃匿名页 |
| LRU_ACTIVE_ANON | 活跃匿名页 |
| LRU_INACTIVE_FILE | 非活跃文件页 |
| LRU_ACTIVE_FILE | 活跃文件页 |
| LRU_UNEVICTABLE | 不可回收页 (mlocked) |

## 回收流程

```
内存压力 → wakeup_kswapd() / 直接回收
    ↓
balance_pgdat() / shrink_zones()
    ↓
shrink_node() → shrink_node_memcgs()
    ↓
shrink_lruvec() → get_scan_count()
    ↓
shrink_list() → shrink_folio_list()
    ↓
folio_check_references() → 回收决策
```

## watermark 机制

```c
enum zone_watermarks {
    WMARK_MIN,   // 最小保留，用于 OOM 和原子分配
    WMARK_LOW,   // kswapd 唤醒阈值
    WMARK_HIGH,  // 区域"满"阈值，kswapd 停止
};
```

## 相关概念

- [[entities/linux/kernel/mm/linux-kernel-mm-swap]] — 回收的匿名页换出到 swap
- [[entities/linux/kernel/mm/linux-kernel-mm-slab-allocator]] — slab 分配器也参与内存回收
- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — kswapd 是特殊的内核线程

## 来源详情

- [[sources/notes-kernel]] — mm_page_reclaim.md
