---
type: entity
tags: [linux-kernel, memory-management, slub, allocator]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel SLUB Allocator

## 定义

SLUB (SLAB Unreclaimable Bugfix) 是 Linux 内核的 slab 内存分配器，是 SLAB 的改进版本，负责中小型内存对象的分配。

## 关键要点

- **Per-CPU Sheaves**: 快速路径使用 per-CPU sheaves 管理空闲对象，避免锁竞争
- **Node Barn**: 每个 NUMA 节点有自己的 barn，管理满/空 sheaves
- **struct kmem_cache**: 每个缓存描述一种对象类型，包含 cpu_sheaves、node[]、size 等字段
- **struct slab**: 内存页框，内含多个对象，通过 freelist 指针串联
- **Fast Path**: `alloc_from_pcs()` → `slab_alloc_node()` → 从 per-CPU sheaves 分配
- **Slow Path**: `___slab_alloc()` → `get_from_partial()` 或 `new_slab()`
- **GFP Flags**: GFP_KERNEL、GFP_ATOMIC 等标志控制分配行为和回收策略

## 核心数据结构

### kmem_cache 结构
```c
struct kmem_cache {
    struct slub_percpu_sheaves __percpu *cpu_sheaves;  // Per-CPU sheaves
    unsigned int size;           // 对象大小（含元数据）
    unsigned int object_size;    // 实际对象大小
    struct kmem_cache_order_objects oo;  // slab 阶数和对象数
    struct kmem_cache_node *node[MAX_NUMNODES];  // Per-node 节点
    // ...
};
```

### Sheaf 机制
```c
struct slab_sheaf {
    void *objects[];  // 空闲对象数组
    unsigned int capacity;
    struct kmem_cache *cache;
};

struct slub_percpu_sheaves {
    struct slab_sheaf *main;    // 主 sheaf
    struct slab_sheaf *spare;   // 备用 sheaf
    struct slab_sheaf *rcu_free;  // RCU 批量释放
};
```

## 分配路径

```
kmalloc()
  └─> __do_kmalloc_node()
        ├─> size > KMALLOC_MAX_CACHE_SIZE → __kmalloc_large_node()
        └─> kmalloc_slab() → slab_alloc_node()
              ├─> alloc_from_pcs()  // Fast path: per-CPU sheaves
              └─> __slab_alloc_node()  // Slow path
                    ├─> get_from_partial()  // 尝试 partial slab
                    └─> new_slab()  // 分配新 slab
```

## 相关概念

- [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]] — 页面分配用于满足缺页中断
- [[entities/linux/kernel/mm/linux-kernel-mm-page-reclaim]] — 内存回收涉及 slab 对象回收
- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — 调度器使用 kmalloc 分配 task_struct

## 来源详情

- [[sources/github-sphinxes0o0-notes-kernel]] — mm_allocator.md
