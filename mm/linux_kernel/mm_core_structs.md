# Linux Kernel 内存管理核心结构体

本文档描述 Linux 内核内存管理子系统（mm）的核心数据结构。

---

## 1. struct page (include/linux/mm_types.h)

物理页描述符，每个物理页对应一个 struct page 结构体。

### 结构体定义

```c
// include/linux/mm_types.h:79-222
struct page {
    memdesc_flags_t flags;              /* 原子标志，可能异步更新 */

    union {
        struct {                        /* Page cache 和匿名页面 */
            union {
                struct list_head lru;          /* LRU 列表 */
                struct list_head buddy_list;   /* 或空闲页 */
                struct list_head pcp_list;      /* PCP 列表 */
                struct llist_node pcp_llist;
            };
            struct address_space *mapping;     /* 映射到的地址空间 */
            union {
                pgoff_t __folio_index;         /* 在 mapping 中的偏移 */
                unsigned long share;            /* fsdax 共享计数 */
            };
            unsigned long private;              /* 私有数据 */
        };
        struct {                        /* page_pool 用于网络栈 */
            unsigned long pp_magic;
            struct page_pool *pp;
            unsigned long _pp_mapping_pad;
            unsigned long dma_addr;
            atomic_long_t pp_ref_count;
        };
        struct {                        /* 复合页的尾页 */
            unsigned long compound_head;        /* 置位 Bit 0 */
        };
        struct {                        /* ZONE_DEVICE 页面 */
            void *_unused_pgmap_compound_head;
            void *zone_device_data;
        };

        struct rcu_head rcu_head;              /* RCU 释放 */
    };

    union {                         /* 4 字节 */
        unsigned int page_type;              /* 页面类型（对于有类型的 folios）*/
        atomic_t _mapcount;                  /* 映射计数，用于 RMAP */
    };

    atomic_t _refcount;                      /* 引用计数，禁止直接使用 */

#ifdef CONFIG_MEMCG
    unsigned long memcg_data;
#elif defined(CONFIG_SLAB_OBJ_EXT)
    unsigned long _unused_slab_obj_exts;
#endif

#if defined(WANT_PAGE_VIRTUAL)
    void *virtual;                           /* 内核虚拟地址（highmem 时为 NULL）*/
#endif

#ifdef LAST_CPUPID_NOT_IN_PAGE_FLAGS
    int _last_cpupid;
#endif

#ifdef CONFIG_KMSAN
    struct page *kmsan_shadow;
    struct page *kmsan_origin;
#endif
} _struct_page_alignment;
```

### 关键特性

- **对齐**: `_struct_page_alignment` 确保结构体按双字对齐（`CONFIG_HAVE_ALIGNED_STRUCT_PAGE`）
- **内存布局**: 第一个 word 的 bit 0 被 `PageTail()` 占用，其他用户不能使用
- **SLUB 兼容性**: 使用 `cmpxchg_double()` 原子更新 freelist 和计数器

### 页面标志 (PG_*)

定义于 `include/linux/page-flags.h:94-128`：

| 标志 | 说明 |
|------|------|
| `PG_locked` | 页面被锁定，不可访问 |
| `PG_writeback` | 页面正在写回 |
| `PG_referenced` | 页面被引用过 |
| `PG_uptodate` | 页面数据是最新的 |
| `PG_dirty` | 页面脏（需要写回）|
| `PG_lru` | 页面在 LRU 列表上 |
| `PG_head` | 是复合页的首页 |
| `PG_waiters` | 页面有等待者 |
| `PG_active` | 页面活跃（在活跃 LRU 上）|
| `PG_workingset` | 页面在工作集里 |
| `PG_reserved` | 保留页（内核特殊页面）|
| `PG_private` | 私有数据（fs 私有）|
| `PG_reclaim` | 即将被回收 |
| `PG_swapbacked` | 有 swap 支撑 |
| `PG_unevictable` | 不可回收（mlocked）|
| `PG_mlocked` | 被 mlock() 锁定 |
| `PG_hwpoison` | 硬件损坏页 |
| `PG_young` | 页面刚被访问过 |
| `PG_idle` | 页面空闲 |

---

## 2. enum zone_type (include/linux/mmzone.h)

内存区域类型枚举，定义内存区域的种类。

### 枚举定义

```c
// include/linux/mmzone.h:784-873
enum zone_type {
#ifdef CONFIG_ZONE_DMA
    ZONE_DMA,           /* DMA 兼容内存（传统设备）*/
#endif
#ifdef CONFIG_ZONE_DMA32
    ZONE_DMA32,         /* 32-bit DMA 兼容内存 */
#endif
    ZONE_NORMAL,        /* 正常可寻址内存，直接映射到内核 */
#ifdef CONFIG_HIGHMEM
    ZONE_HIGHMEM,      /* 高端内存，需要动态映射 */
#endif
    ZONE_MOVABLE,       /* 可移动页面区域（用于内存热插拔）*/
#ifdef CONFIG_ZONE_DEVICE
    ZONE_DEVICE,        /* 设备映射内存（持久内存、GPU）*/
#endif
    __MAX_NR_ZONES     /* 区域数量上限 */
};
```

### 区域说明

| 区域 | 说明 |
|------|------|
| `ZONE_DMA` | 适用于老式 ISA 设备的 DMA 兼容区域 |
| `ZONE_DMA32` | 32-bit DMA 设备可访问的区域 |
| `ZONE_NORMAL` | 内核直接映射的线性地址区域 |
| `ZONE_HIGHMEM` | 32-bit 系统的高内存区域，需要临时映射 |
| `ZONE_MOVABLE` | 通过内存热插拔创建的可移动页面区域 |
| `ZONE_DEVICE` | 设备驱动映射的内存（PMEM、GPU 等）|

---

## 3. enum migratetype (include/linux/mmzone.h)

页面迁移类型枚举，控制页面的分配和回收行为。

### 枚举定义

```c
// include/linux/mmzone.h:64-90
enum migratetype {
    MIGRATE_UNMOVABLE,      /* 不可移动页面（内核分配）*/
    MIGRATE_MOVABLE,        /* 可移动页面（用户空间）*/
    MIGRATE_RECLAIMABLE,    /* 可回收页面（可回收但不能直接移动）*/
    MIGRATE_PCPTYPES,       /* PCP 列表上的迁移类型数量 */
    MIGRATE_HIGHATOMIC = MIGRATE_PCPTYPES,
#ifdef CONFIG_CMA
    MIGRATE_CMA,            /* CMA 区域专用 */
    __MIGRATE_TYPE_END = MIGRATE_CMA,
#else
    __MIGRATE_TYPE_END = MIGRATE_HIGHATOMIC,
#endif
#ifdef CONFIG_MEMORY_ISOLATION
    MIGRATE_ISOLATE,        /* 隔离区域，不能分配 */
#endif
    MIGRATE_TYPES           /* 迁移类型总数 */
};
```

### 迁移类型说明

| 类型 | 说明 |
|------|------|
| `MIGRATE_UNMOVABLE` | 内核分配的页面，不能移动（如 kmalloc）|
| `MIGRATE_MOVABLE` | 用户空间分配的页面，可以移动（如 malloc）|
| `MIGRATE_RECLAIMABLE` | 可以回收但不适合移动的页面 |
| `MIGRATE_CMA` | CMA（连续内存分配器）区域 |
| `MIGRATE_ISOLATE` | 用于内存隔离的伪类型 |

---

## 4. struct zone (include/linux/mmzone.h)

内存区域结构体，每个 ZONE_* 对应一个 zone 结构体。

### 结构体定义

```c
// include/linux/mmzone.h:879-1060
struct zone {
    /* 大部分只读字段 */

    /* 区域水印，通过 *_wmark_pages(zone) 宏访问 */
    unsigned long _watermark[NR_WMARK];
    unsigned long watermark_boost;          /* 水印提升值 */

    unsigned long nr_reserved_highatomic;   /* 保留的高原子页面数 */
    unsigned long nr_free_highatomic;        /* 空闲的高原子页面数 */

    /* 低端区域的内存保留数，防止低区域 OOM */
    long lowmem_reserve[MAX_NR_ZONES];

#ifdef CONFIG_NUMA
    int node;                              /* NUMA 节点 ID */
#endif
    struct pglist_data *zone_pgdat;         /* 所属的节点 */
    struct per_cpu_pages __percpu *per_cpu_pageset;  /* 每 CPU 页面集 */
    struct per_cpu_zonestat __percpu *per_cpu_zonestats;

    int pageset_high_min;                   /* 页面集高阈值最小值 */
    int pageset_high_max;                   /* 页面集高阈值最大值 */
    int pageset_batch;                      /* 批量大小 */

#ifndef CONFIG_SPARSEMEM
    unsigned long *pageblock_flags;        /* pageblock 标志（SPARSEMEM 除外）*/
#endif

    unsigned long zone_start_pfn;          /* 区域起始页帧号 */

    /* 区域页面统计 */
    atomic_long_t managed_pages;            /* 伙伴系统管理的页面数 */
    unsigned long spanned_pages;            /* 区域总页数（含空洞）*/
    unsigned long present_pages;            /* 实际存在的页面数 */
#if defined(CONFIG_MEMORY_HOTPLUG)
    unsigned long present_early_pages;     /* 早期存在的页面数 */
#endif
#ifdef CONFIG_CMA
    unsigned long cma_pages;               /* CMA 使用的页面数 */
#endif

    const char *name;                      /* 区域名称 */

#ifdef CONFIG_MEMORY_ISOLATION
    unsigned long nr_isolate_pageblock;    /* 隔离的 pageblock 数量 */
#endif

#ifdef CONFIG_MEMORY_HOTPLUG
    seqlock_t span_seqlock;                /* 跨度序列锁 */
#endif

    int initialized;                       /* 是否已初始化 */

    /* 页面分配器使用的写密集字段 */
    CACHELINE_PADDING(_pad1_);

    /* 不同大小的空闲区域 */
    struct free_area free_area[NR_PAGE_ORDERS];

#ifdef CONFIG_UNACCEPTED_MEMORY
    struct list_head unaccepted_pages;     /* 待接受的页面 */
    struct work_struct unaccepted_cleanup; /* 清理工作 */
#endif

    unsigned long flags;                   /* 区域标志 */

    spinlock_t lock;                       /* 主要保护 free_area */

    struct llist_head trylock_free_pages;  /* 下次尝试锁定时释放的页面 */

    CACHELINE_PADDING(_pad2_);

    unsigned long percpu_drift_mark;       /* 每 CPU 计数器漂移标记 */

#if defined CONFIG_COMPACTION || defined CONFIG_CMA
    unsigned long compact_cached_free_pfn;     /* 空闲扫描起始位置 */
    unsigned long compact_cached_migrate_pfn[ASYNC_AND_SYNC];  /* 迁移扫描起始位置 */
    unsigned long compact_init_migrate_pfn;
    unsigned long compact_init_free_pfn;
#endif

#ifdef CONFIG_COMPACTION
    unsigned int compact_considered;        /* 压缩考虑次数 */
    unsigned int compact_defer_shift;       /* 延迟 shift */
    int compact_order_failed;               /* 最小失败阶数 */
#endif

#if defined CONFIG_COMPACTION || defined CONFIG_CMA
    bool compact_blockskip_flush;           /* 是否清除跳过块 */
#endif

    bool contiguous;                       /* 连续标志 */

    CACHELINE_PADDING(_pad3_);

    /* 区域统计 */
    atomic_long_t vm_stat[NR_VM_ZONE_STAT_ITEMS];
    atomic_long_t vm_numa_event[NR_VM_NUMA_EVENT_ITEMS];
} ____cacheline_internodealigned_in_smp;
```

### 水印类型 (enum zone_watermarks)

```c
// include/linux/mmzone.h:708-714
enum zone_watermarks {
    WMARK_MIN,     /* 最小水印，内存枯竭时触发回收 */
    WMARK_LOW,     /* 低水印，触发 kswapd 醒来 */
    WMARK_HIGH,    /* 高水印，kswapd 停止 */
    WMARK_PROMO,   /* 提升水印，用于页面提升 */
    NR_WMARK
};
```

### 区域标志 (enum zone_flags)

```c
// include/linux/mmzone.h:1069-1075
enum zone_flags {
    ZONE_BOOSTED_WATERMARK,     /* 区域最近提升了水印 */
    ZONE_RECLAIM_ACTIVE,        /* kswapd 可能在扫描该区域 */
    ZONE_BELOW_HIGH,            /* 区域低于高水印 */
};
```

### 关键宏

```c
// include/linux/mmzone.h:1077-1096
static inline unsigned long wmark_pages(const struct zone *z, enum zone_watermarks w)
{
    return z->_watermark[w] + z->watermark_boost;
}

static inline unsigned long min_wmark_pages(const struct zone *z)
    { return wmark_pages(z, WMARK_MIN); }

static inline unsigned long low_wmark_pages(const struct zone *z)
    { return wmark_pages(z, WMARK_LOW); }

static inline unsigned long high_wmark_pages(const struct zone *z)
    { return wmark_pages(z, WMARK_HIGH); }
```

---

## 5. struct pglist_data (include/linux/mmzone.h)

NUMA 节点描述符，每个 NUMA 节点有一个。

### 结构体定义

```c
// include/linux/mmzone.h:1381-1521
typedef struct pglist_data {
    /* 本节点的区域列表 */
    struct zone node_zones[MAX_NR_ZONES];          /* 本节点所有区域 */

    /* 节点区域列表（包含所有节点的区域）*/
    struct zonelist node_zonelists[MAX_ZONELISTS];

    int nr_zones;                                  /* 本节点已填充的区域数 */

#ifdef CONFIG_FLATMEM
    struct page *node_mem_map;                    /* 节点页面映射 */
#ifdef CONFIG_PAGE_EXTENSION
    struct page_ext *node_page_ext;                /* 页面扩展 */
#endif
#endif

#if defined(CONFIG_MEMORY_HOTPLUG) || defined(CONFIG_DEFERRED_STRUCT_PAGE_INIT)
    spinlock_t node_size_lock;                     /* 保护节点大小 */
#endif

    unsigned long node_start_pfn;                  /* 节点起始页帧号 */
    unsigned long node_present_pages;              /* 物理页面总数 */
    unsigned long node_spanned_pages;              /* 物理页面范围（含空洞）*/
    int node_id;                                   /* 节点 ID */

    wait_queue_head_t kswapd_wait;                /* kswapd 等待队列 */
    wait_queue_head_t pfmemalloc_wait;             /* pfmemalloc 等待队列 */

    wait_queue_head_t reclaim_wait[NR_VMSCAN_THROTTLE];

    atomic_t nr_writeback_throttled;               /* 写回节流的任务数 */
    unsigned long nr_reclaim_start;                 /* 节流开始时的页面数 */

#ifdef CONFIG_MEMORY_HOTPLUG
    struct mutex kswapd_lock;
#endif
    struct task_struct *kswapd;                     /* kswapd 进程 */
    int kswapd_order;
    enum zone_type kswapd_highest_zoneidx;

    atomic_t kswapd_failures;                      /* 回收失败次数 */

#ifdef CONFIG_COMPACTION
    int kcompactd_max_order;
    enum zone_type kcompactd_highest_zoneidx;
    wait_queue_head_t kcompactd_wait;
    struct task_struct *kcompactd;
    bool proactive_compact_trigger;
#endif

    unsigned long totalreserve_pages;               /* 保留页面数 */

#ifdef CONFIG_NUMA
    unsigned long min_unmapped_pages;               /* 最小未映射页面数 */
    unsigned long min_slab_pages;                   /* 最小 slab 页面数 */
#endif

    CACHELINE_PADDING(_pad1_);

#ifdef CONFIG_DEFERRED_STRUCT_PAGE_INIT
    unsigned long first_deferred_pfn;               /* 延迟初始化起始 pfn */
#endif

#ifdef CONFIG_TRANSPARENT_HUGEPAGE
    struct deferred_split deferred_split_queue;     /* THP 延迟分离队列 */
#endif

#ifdef CONFIG_NUMA_BALANCING
    unsigned int nbp_rl_start;                    /* 促进速率限制起始时间 */
    unsigned long nbp_rl_nr_cand;                  /* 促进候选页面数 */
    unsigned int nbp_threshold;                    /* 促进阈值 */
    unsigned int nbp_th_start;                     /* 阈值调整起始时间 */
    unsigned long nbp_th_nr_cand;                  /* 阈值调整候选数 */
#endif

    /* 页面回收扫描器常用字段 */
    struct lruvec __lruvec;                        /* LRU 向量 */

    unsigned long flags;                           /* 节点标志 */

#ifdef CONFIG_LRU_GEN
    struct lru_gen_mm_walk mm_walk;               /* kswapd MM 遍历数据 */
    struct lru_gen_memcg memcg_lru;                /* LRU gen memcg 列表 */
#endif

    CACHELINE_PADDING(_pad2_);

    /* 每节点 vmstats */
    struct per_cpu_nodestat __percpu *per_cpu_nodestats;
    atomic_long_t vm_stat[NR_VM_NODE_STAT_ITEMS];

#ifdef CONFIG_NUMA
    struct memory_tier __rcu *memtier;             /* 内存层级 */
#endif

#ifdef CONFIG_MEMORY_FAILURE
    struct memory_failure_stats mf_stats;          /* 内存故障统计 */
#endif
} pg_data_t;
```

### 节点标志 (enum pgdat_flags)

```c
// include/linux/mmzone.h:1062-1067
enum pgdat_flags {
    PGDAT_WRITEBACK,       /* 回收扫描最近发现许多写回页面 */
    PGDAT_RECLAIM_LOCKED,  /* 防止并发回收 */
};
```

---

## 6. struct lruvec (include/linux/mmzone.h)

LRU（最近最少使用）向量，管理页面的 LRU 列表。

### 结构体定义

```c
// include/linux/mmzone.h:669-698
struct lruvec {
    struct list_head lists[NR_LRU_LISTS];         /* LRU 列表数组 */
    spinlock_t lru_lock;                           /* 保护 LRU 列表的锁 */

    /* 跟踪回收一种 LRU（文件或匿名）的成本 */
    unsigned long anon_cost;                       /* 匿名页面回收成本 */
    unsigned long file_cost;                       /* 文件页面回收成本 */

    atomic_long_t nonresident_age;                 /* 非驻留年龄 */

    unsigned long refaults[ANON_AND_FILE];         /* 上次回收周期的回填数 */

    unsigned long flags;                            /* lruvec 状态标志 */

#ifdef CONFIG_LRU_GEN
    struct lru_gen_folio lrugen;                  /* 按代数划分的可回收页面 */

#ifdef CONFIG_LRU_GEN_WALKS_MMU
    struct lru_gen_mm_state mm_state;              /* 并发遍历 lru_gen_mm_list */
#endif
#endif

#ifdef CONFIG_MEMCG
    struct pglist_data *pgdat;                     /* 指向节点数据 */
#endif

    struct zswap_lruvec_state zswap_lruvec_state;
};
```

### LRU 列表枚举 (enum lru_list)

```c
// include/linux/mmzone.h:316-323
enum lru_list {
    LRU_INACTIVE_ANON = LRU_BASE,      /* 非活跃匿名页面 */
    LRU_ACTIVE_ANON = LRU_BASE + LRU_ACTIVE,  /* 活跃匿名页面 */
    LRU_INACTIVE_FILE = LRU_BASE + LRU_FILE, /* 非活跃文件页面 */
    LRU_ACTIVE_FILE = LRU_BASE + LRU_FILE + LRU_ACTIVE, /* 活跃文件页面 */
    LRU_UNEVICTABLE,                   /* 不可回收页面 */
    NR_LRU_LISTS
};
```

### LRU 向量标志 (enum lruvec_flags)

```c
// include/linux/mmzone.h:351-367
enum lruvec_flags {
    /* cgroup 回收设置的标志 */
    LRUVEC_CGROUP_CONGESTED,
    /* kswapd 节点级回收设置的标志 */
    LRUVEC_NODE_CONGESTED,
};
```

---

## 7. struct free_area (include/linux/mmzone.h)

空闲区域结构体，用于伙伴系统分配器。

### 结构体定义

```c
// include/linux/mmzone.h:138-141
struct free_area {
    struct list_head free_list[MIGRATE_TYPES];  /* 每种迁移类型一个链表 */
    unsigned long nr_free;                      /* 空闲页面总数 */
};
```

### 说明

- `free_list`: 按迁移类型分组的空闲页面链表
- `nr_free`: 该阶（order）空闲页面的总数量
- 伙伴系统为每个 order 维护一个 `free_area` 结构

---

## 8. struct per_cpu_pages (include/linux/mmzone.h)

每 CPU 页面缓存结构体，用于减少区域锁竞争。

### 结构体定义

```c
// include/linux/mmzone.h:744-760
struct per_cpu_pages {
    spinlock_t lock;            /* 保护 lists 字段 */
    int count;                  /* 列表中的页面数 */
    int high;                   /* 高水印，需要清空 */
    int high_min;               /* 最小高水印 */
    int high_max;               /* 最大高水印 */
    int batch;                  /* 伙伴系统添加/删除的块大小 */
    u8 flags;                   /* 受 pcp->lock 保护 */
    u8 alloc_factor;            /* 分配时的批量缩放因子 */

#ifdef CONFIG_NUMA
    u8 expire;                  /* 为 0 时，远程页面集被清空 */
#endif
    short free_count;          /* 连续空闲计数 */

    /* 页面列表，每种迁移类型一个 */
    struct list_head lists[NR_PCP_LISTS];
} ____cacheline_aligned_in_smp;
```

### PCP 列表数量

```c
// include/linux/mmzone.h:721-727
#ifdef CONFIG_TRANSPARENT_HUGEPAGE
#define NR_PCP_THP 2           /* THP 用 2 个列表 */
#else
#define NR_PCP_THP 0
#endif
#define NR_LOWORDER_PCP_LISTS (MIGRATE_PCPTYPES * (PAGE_ALLOC_COSTLY_ORDER + 1))
#define NR_PCP_LISTS (NR_LOWORDER_PCP_LISTS + NR_PCP_THP)
```

### PCP 标志

```c
// include/linux/mmzone.h:741-742
#define PCPF_PREV_FREE_HIGH_ORDER   BIT(0)  /* 上次释放了高阶页面 */
#define PCPF_FREE_HIGH_BATCH        BIT(1)  /* 保留批量页面 */
```

---

## 9. 多代 LRU (CONFIG_LRU_GEN)

### struct lru_gen_folio

```c
// include/linux/mmzone.h:490-518
struct lru_gen_folio {
    unsigned long max_seq;                          /* 最年轻代数 */
    unsigned long min_seq[ANON_AND_FILE];           /* 最老代数（匿名/文件分开）*/
    unsigned long timestamps[MAX_NR_GENS];           /* 每代的创建时间 */

    struct list_head folios[MAX_NR_GENS][ANON_AND_FILE][MAX_NR_ZONES];
                                                  /* 多代 LRU 列表 */
    long nr_pages[MAX_NR_GENS][ANON_AND_FILE][MAX_NR_ZONES];
                                                  /* 每代页面数（最终一致）*/

    unsigned long avg_refaulted[ANON_AND_FILE][MAX_NR_TIERS];
                                                  /* 回填指数移动平均 */
    unsigned long avg_total[ANON_AND_FILE][MAX_NR_TIERS];
                                                  /* 驱逐+保护指数移动平均 */

    unsigned long protected[NR_HIST_GENS][ANON_AND_FILE][MAX_NR_TIERS];
                                                  /* 受保护的页面数 */

    atomic_long_t evicted[NR_HIST_GENS][ANON_AND_FILE][MAX_NR_TIERS];
    atomic_long_t refaulted[NR_HIST_GENS][ANON_AND_FILE][MAX_NR_TIERS];

    bool enabled;                                   /* 多代 LRU 是否启用 */
    u8 gen;                                         /* memcg 代 */
    u8 seg;                                         /* 列表段 */
    struct hlist_nulls_node list;                   /* 节点链表 */
};
```

### 代数和层级常量

```c
// include/linux/mmzone.h:398-399
#define MIN_NR_GENS  2U                              /* 最少代数 */
#define MAX_NR_GENS  4U                              /* 最多代数 */

// include/linux/mmzone.h:421
#define MAX_NR_TIERS 4U                              /* 最大层级数 */
```

---

## 10. 页面分配关键常量

```c
// include/linux/mmzone.h:29-34
#ifndef CONFIG_ARCH_FORCE_MAX_ORDER
#define MAX_PAGE_ORDER 10                         /* 最大分配阶 */
#else
#define MAX_PAGE_ORDER CONFIG_ARCH_FORCE_MAX_ORDER
#endif
#define MAX_ORDER_NR_PAGES (1 << MAX_PAGE_ORDER)
#define NR_PAGE_ORDERS (MAX_PAGE_ORDER + 1)

// include/linux/mmzone.h:62
#define PAGE_ALLOC_COSTLY_ORDER 3                /* 代价昂贵的分配阶 */

// include/linux/mmzone.h:1138
#define MAX_ZONES_PER_ZONELIST (MAX_NUMNODES * MAX_NR_ZONES)
```

---

## 11. 统计项枚举

### enum zone_stat_item

```c
// include/linux/mmzone.h:159-179
enum zone_stat_item {
    NR_FREE_PAGES,
    NR_FREE_PAGES_BLOCKS,
    NR_ZONE_LRU_BASE,
    NR_ZONE_INACTIVE_ANON = NR_ZONE_LRU_BASE,
    NR_ZONE_ACTIVE_ANON,
    NR_ZONE_INACTIVE_FILE,
    NR_ZONE_ACTIVE_FILE,
    NR_ZONE_UNEVICTABLE,
    NR_ZONE_WRITE_PENDING,
    NR_MLOCK,
#if IS_ENABLED(CONFIG_ZSMALLOC)
    NR_ZSPAGES,
#endif
    NR_FREE_CMA_PAGES,
#ifdef CONFIG_UNACCEPTED_MEMORY
    NR_UNACCEPTED,
#endif
    NR_VM_ZONE_STAT_ITEMS
};
```

### enum node_stat_item

```c
// include/linux/mmzone.h:181-264
enum node_stat_item {
    NR_LRU_BASE,
    NR_INACTIVE_ANON = NR_LRU_BASE,
    NR_ACTIVE_ANON,
    NR_INACTIVE_FILE,
    NR_ACTIVE_FILE,
    NR_UNEVICTABLE,
    NR_SLAB_RECLAIMABLE_B,
    NR_SLAB_UNRECLAIMABLE_B,
    NR_ISOLATED_ANON,
    NR_ISOLATED_FILE,
    WORKINGSET_NODES,
    WORKINGSET_REFAULT_BASE,
    WORKINGSET_REFAULT_ANON = WORKINGSET_REFAULT_BASE,
    WORKINGSET_REFAULT_FILE,
    WORKINGSET_ACTIVATE_BASE,
    WORKINGSET_ACTIVATE_ANON = WORKINGSET_ACTIVATE_BASE,
    WORKINGSET_ACTIVATE_FILE,
    WORKINGSET_RESTORE_BASE,
    WORKINGSET_RESTORE_ANON = WORKINGSET_RESTORE_BASE,
    WORKINGSET_RESTORE_FILE,
    WORKINGSET_NODERECLAIM,
    NR_ANON_MAPPED,
    NR_FILE_MAPPED,
    NR_FILE_PAGES,
    NR_FILE_DIRTY,
    NR_WRITEBACK,
    NR_SHMEM,
    NR_SHMEM_THPS,
    NR_SHMEM_PMDMAPPED,
    NR_FILE_THPS,
    NR_FILE_PMDMAPPED,
    NR_ANON_THPS,
    NR_VMSCAN_WRITE,
    NR_VMSCAN_IMMEDIATE,
    NR_DIRTIED,
    NR_WRITTEN,
    NR_THROTTLED_WRITTEN,
    NR_KERNEL_MISC_RECLAIMABLE,
    NR_FOLL_PIN_ACQUIRED,
    NR_FOLL_PIN_RELEASED,
    NR_KERNEL_STACK_KB,
#ifdef CONFIG_SHADOW_CALL_STACK
    NR_KERNEL_SCS_KB,
#endif
    NR_PAGETABLE,
    NR_SECONDARY_PAGETABLE,
#ifdef CONFIG_IOMMU_SUPPORT
    NR_IOMMU_PAGES,
#endif
#ifdef CONFIG_SWAP
    NR_SWAPCACHE,
#endif
#ifdef CONFIG_NUMA_BALANCING
    PGPROMOTE_SUCCESS,
    PGPROMOTE_CANDIDATE,
    PGPROMOTE_CANDIDATE_NRL,
#endif
    PGDEMOTE_KSWAPD,
    PGDEMOTE_DIRECT,
    PGDEMOTE_KHUGEPAGED,
    PGDEMOTE_PROACTIVE,
#ifdef CONFIG_HUGETLB_PAGE
    NR_HUGETLB,
#endif
    NR_BALLOON_PAGES,
    NR_KERNEL_FILE_PAGES,
    NR_VM_NODE_STAT_ITEMS
};
```

---

## 12. 页面标志布局

页面标志在 `page->flags` 中的布局（`include/linux/page-flags-layout.h`）:

```
| SECTION | NODE | ZONE | LAST_CPUPID | ... | FLAGS |
```

各字段宽度由配置决定：
- `ZONES_WIDTH`: 区域数量（1-3 bits）
- `NODES_WIDTH`: 节点 ID（通常 6 bits on 64-bit）
- `SECTIONS_WIDTH`: 稀疏内存段（SPARSEMEM 配置）
- `LAST_CPUPID_SHIFT`: 最后 CPU/PID（NUMA balancing 配置）
- `LRU_GEN_WIDTH`: 多代 LRU 代号
- `LRU_REFS_WIDTH`: LRU 引用层级

---

## 总结

内存管理子系统的核心数据结构形成以下层次：

```
pg_data_t (NUMA节点)
  ├── zone (节点中的区域: DMA/NORMAL/HIGHMEM/MOVABLE/DEVICE)
  │     ├── free_area[] (伙伴系统空闲区域，每阶一个)
  │     └── per_cpu_pages (每CPU页面缓存)
  └── lruvec (LRU页面管理)
        ├── lists[] (LRU列表: 活跃/非活跃/匿名/文件)
        └── lru_gen_folio (多代LRU，可选)
```

每个物理页面通过 `struct page` 描述，并可通过 `page_zonenum()` 获取所在区域。
