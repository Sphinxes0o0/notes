# Linux Kernel Memory Allocator Analysis

## Table of Contents

1. [SLUB Allocator](#1-slub-allocator)
   - [struct kmem_cache](#11-struct-kmem_cache)
   - [struct kmem_cache_node](#12-struct-kmem_cache_node)
   - [struct slab](#13-struct-slab)
   - [Sheaves/Barn Mechanism](#14-sheavesbarn-mechanism)
2. [GFP Flags](#2-gfp-flags)
3. [kmalloc/kfree Implementation](#3-kmallockfree-implementation)
4. [Page Allocation](#4-page-allocation)
   - [`__alloc_pages_noprof`](#41-__alloc_pages_noprof)
   - [`get_page_from_freelist`](#42-get_page_from_freelist)
5. [Watermark Mechanism](#5-watermark-mechanism)

---

## 1. SLUB Allocator

### 1.1 struct kmem_cache

Location: `mm/slab.h` (lines 197-251)

```c
struct kmem_cache {
    struct slub_percpu_sheaves __percpu *cpu_sheaves;
    /* Used for retrieving partial slabs, etc. */
    slab_flags_t flags;
    unsigned long min_partial;
    unsigned int size;           /* Object size including metadata */
    unsigned int object_size;    /* Object size without metadata */
    struct reciprocal_value reciprocal_size;
    unsigned int offset;        /* Free pointer offset */
    unsigned int sheaf_capacity;
    struct kmem_cache_order_objects oo;

    /* Allocation and freeing of slabs */
    struct kmem_cache_order_objects min;
    gfp_t allocflags;           /* gfp flags to use on each alloc */
    int refcount;               /* Refcount for slab cache destroy */
    void (*ctor)(void *object); /* Object constructor */
    unsigned int inuse;         /* Offset to metadata */
    unsigned int align;          /* Alignment */
    unsigned int red_left_pad;   /* Left redzone padding size */
    const char *name;           /* Name (only for display!) */
    struct list_head list;      /* List of slab caches */
#ifdef CONFIG_SYSFS
    struct kobject kobj;        /* For sysfs */
#endif
#ifdef CONFIG_SLAB_FREELIST_HARDENED
    unsigned long random;
#endif

#ifdef CONFIG_NUMA
    /*
     * Defragmentation by allocating from a remote node.
     */
    unsigned int remote_node_defrag_ratio;
#endif

#ifdef CONFIG_SLAB_FREELIST_RANDOM
    unsigned int *random_seq;
#endif

#ifdef CONFIG_KASAN_GENERIC
    struct kasan_cache kasan_info;
#endif

#ifdef CONFIG_HARDENED_USERCOPY
    unsigned int useroffset;    /* Usercopy region offset */
    unsigned int usersize;       /* Usercopy region size */
#endif

#ifdef CONFIG_SLUB_STATS
    struct kmem_cache_stats __percpu *cpu_stats;
#endif

    struct kmem_cache_node *node[MAX_NUMNODES];
};
```

Key fields:
- `cpu_sheaves`: Per-CPU sheaves for fast allocation (lines 198)
- `size`: Total object size including metadata (line 202)
- `object_size`: Actual object size (line 203)
- `oo`: Order and number of objects in a slab (line 207)
- `min`: Minimum order for slab allocation (line 210)
- `node[]`: Per-node kmem_cache_node structures (line 250)

### 1.2 struct kmem_cache_node

Location: `mm/slub.c` (lines 430-440)

```c
struct kmem_cache_node {
    spinlock_t list_lock;
    unsigned long nr_partial;
    struct list_head partial;
#ifdef CONFIG_SLUB_DEBUG
    atomic_long_t nr_slabs;
    atomic_long_t total_objects;
    struct list_head full;
#endif
    struct node_barn *barn;
};
```

Key fields:
- `nr_partial`: Number of partial slabs (line 432)
- `partial`: List head for partial slabs (line 433)
- `barn`: Node-level barn for managing sheaves (line 439)

### 1.3 struct slab

Location: `mm/slab.h` (lines 74-92)

```c
/* Reuses the bits in struct page */
struct slab {
    memdesc_flags_t flags;

    struct kmem_cache *slab_cache;
    union {
        struct {
            struct list_head slab_list;
            /* Double-word boundary */
            struct freelist_counters;
        };
        struct rcu_head rcu_head;
    };

    unsigned int __page_type;
    atomic_t __page_refcount;
#ifdef CONFIG_SLAB_OBJ_EXT
    unsigned long obj_exts;
#endif
};
```

The `freelist_counters` structure (lines 41-71):
```c
struct freelist_counters {
    union {
        struct {
            void *freelist;
            union {
                unsigned long counters;
                struct {
                    unsigned inuse:16;
                    unsigned objects:15;
                    unsigned frozen:1;
#ifdef CONFIG_64BIT
                    unsigned int stride;
#endif
                };
            };
        };
#ifdef system_has_freelist_aba
        freelist_full_t freelist_counters;
#endif
    };
};
```

### 1.4 Sheaves/Barn Mechanism

#### struct slab_sheaf

Location: `mm/slub.c` (lines 404-418)

```c
struct slab_sheaf {
    union {
        struct rcu_head rcu_head;
        struct list_head barn_list;
        /* only used for prefilled sheafs */
        struct {
            unsigned int capacity;
            bool pfmemalloc;
        };
    };
    struct kmem_cache *cache;
    unsigned int size;
    int node; /* only used for rcu_sheaf */
    void *objects[];
};
```

#### struct slub_percpu_sheaves

Location: `mm/slub.c` (lines 420-425)

```c
struct slub_percpu_sheaves {
    local_trylock_t lock;
    struct slab_sheaf *main;    /* never NULL when unlocked */
    struct slab_sheaf *spare;   /* empty or full, may be NULL */
    struct slab_sheaf *rcu_free; /* for batching kfree_rcu() */
};
```

#### struct node_barn

Location: `mm/slub.c` (lines 396-402)

```c
struct node_barn {
    spinlock_t lock;
    struct list_head sheaves_full;
    struct list_head sheaves_empty;
    unsigned int nr_full;
    unsigned int nr_empty;
};
```

#### Sheaf/Barn Overview

The sheaves/barn mechanism is SLUB's optimization for managing slabs at the per-CPU and per-node level:

1. **Per-CPU Sheaves** (`slub_percpu_sheaves`):
   - `main`: Primary sheaf containing free objects (always valid when unlocked)
   - `spare`: Empty or full sheaf for备用
   - `rcu_free`: For batching kfree_rcu() operations

2. **Node Barn** (`node_barn`):
   - `sheaves_full`: List of full sheaves at node level
   - `sheaves_empty`: List of empty sheaves at node level
   - Provides node-level slab management for NUMA systems

3. **Allocation Flow** (mm/slub.c):
   - `alloc_from_pcs()` (line 2864): Fast path - allocate from per-CPU sheaves
   - `___slab_alloc()` (line 4374): Slow path - allocate from partial slabs or new slabs
   - `barn_get_empty_sheaf()` (line 3086): Get empty sheaf from barn
   - `barn_put_full_sheaf()` (line 3130): Put full sheaf into barn

---

## 2. GFP Flags

Location: `include/linux/gfp_types.h` and `include/linux/gfp.h`

### GFP Flag Definitions

Location: `include/linux/gfp_types.h` (lines 26-100)

```c
enum {
    ___GFP_DMA_BIT,
    ___GFP_HIGHMEM_BIT,
    ___GFP_DMA32_BIT,
    ___GFP_MOVABLE_BIT,
    ___GFP_RECLAIMABLE_BIT,
    ___GFP_HIGH_BIT,
    ___GFP_IO_BIT,
    ___GFP_FS_BIT,
    ___GFP_ZERO_BIT,
    ___GFP_UNUSED_BIT,
    ___GFP_DIRECT_RECLAIM_BIT,
    ___GFP_KSWAPD_RECLAIM_BIT,
    ___GFP_WRITE_BIT,
    ___GFP_NOWARN_BIT,
    ___GFP_RETRY_MAYFAIL_BIT,
    ___GFP_NOFAIL_BIT,
    ___GFP_NORETRY_BIT,
    ___GFP_MEMALLOC_BIT,
    ___GFP_COMP_BIT,
    ___GFP_NOMEMALLOC_BIT,
    ___GFP_HARDWALL_BIT,
    ___GFP_THISNODE_BIT,
    ___GFP_ACCOUNT_BIT,
    ___GFP_ZEROTAGS_BIT,
    ___GFP_NO_OBJ_EXT_BIT,
    ___GFP_LAST_BIT
};
```

### Zone Modifiers

| Flag | Description |
|------|-------------|
| `__GFP_DMA` | Allocate from ZONE_DMA |
| `__GFP_HIGHMEM` | Allocate from ZONE_HIGHMEM |
| `__GFP_DMA32` | Allocate from ZONE_DMA32 |
| `__GFP_MOVABLE` | Page can be moved by migration |

### Watermark Modifiers

| Flag | Description |
|------|-------------|
| `__GFP_HIGH` | High priority, access emergency reserves |
| `__GFP_MEMALLOC` | Allow access to all memory reserves |
| `__GFP_NOMEMALLOC` | Forbid access to emergency reserves |

### Reclaim Modifiers

| Flag | Description |
|------|-------------|
| `__GFP_IO` | Can start physical I/O |
| `__GFP_FS` | Can call down to filesystem |
| `__GFP_DIRECT_RECLAIM` | Caller may enter direct reclaim |
| `__GFP_KSWAPD_RECLAIM` | Wake kswapd when below low watermark |
| `__GFP_RECLAIM` | Shorthand for direct + kswapd reclaim |
| `__GFP_NORETRY` | Only lightweight reclaim, no OOM |
| `__GFP_RETRY_MAYFAIL` | Retry if progress is made |
| `__GFP_NOFAIL` | Must retry infinitely |

### Action Modifiers

| Flag | Description |
|------|-------------|
| `__GFP_NOWARN` | Suppress allocation failure reports |
| `__GFP_COMP` | Address compound page metadata |
| `__GFP_ZERO` | Return zeroed page on success |
| `__GFP_ZEROTAGS` | Zero memory tags |

### Common GFP Combinations

Location: `include/linux/gfp_types.h` (lines 376-389)

```c
#define GFP_ATOMIC    (__GFP_HIGH|__GFP_KSWAPD_RECLAIM)
#define GFP_KERNEL    (__GFP_RECLAIM | __GFP_IO | __GFP_FS)
#define GFP_KERNEL_ACCOUNT (GFP_KERNEL | __GFP_ACCOUNT)
#define GFP_NOWAIT    (__GFP_KSWAPD_RECLAIM | __GFP_NOWARN)
#define GFP_NOIO      (__GFP_RECLAIM)
#define GFP_NOFS      (__GFP_RECLAIM | __GFP_IO)
#define GFP_USER      (__GFP_RECLAIM | __GFP_IO | __GFP_FS | __GFP_HARDWALL)
#define GFP_DMA       __GFP_DMA
#define GFP_DMA32     __GFP_DMA32
#define GFP_HIGHUSER  (GFP_USER | __GFP_HIGHMEM)
#define GFP_HIGHUSER_MOVABLE (GFP_HIGHUSER | __GFP_MOVABLE | __GFP_SKIP_KASAN)
```

---

## 3. kmalloc/kfree Implementation

### kmalloc

Location: `mm/slub.c` (lines 5270-5274)

```c
void *__kmalloc_noprof(size_t size, gfp_t flags)
{
    return __do_kmalloc_node(size, NULL, flags, NUMA_NO_NODE, _RET_IP_);
}
EXPORT_SYMBOL(__kmalloc_noprof);
```

The internal implementation `__do_kmalloc_node` (lines 5240-5263):

```c
static __always_inline
void *__do_kmalloc_node(size_t size, kmem_buckets *b, gfp_t flags, int node,
                        unsigned long caller)
{
    struct kmem_cache *s;
    void *ret;

    if (unlikely(size > KMALLOC_MAX_CACHE_SIZE)) {
        ret = __kmalloc_large_node_noprof(size, flags, node);
        trace_kmalloc(caller, ret, size,
                      PAGE_SIZE << get_order(size), flags, node);
        return ret;
    }

    if (unlikely(!size))
        return ZERO_SIZE_PTR;

    s = kmalloc_slab(size, b, flags, caller);

    ret = slab_alloc_node(s, NULL, flags, node, caller, size);
    ret = kasan_kmalloc(s, ret, size, flags);
    trace_kmalloc(caller, ret, size, s->size, flags, node);
    return ret;
}
```

### slab_alloc_node (Fast Path)

Location: `mm/slub.c` (lines 4837-4869)

```c
static __fastpath_inline void *slab_alloc_node(struct kmem_cache *s,
    struct list_lru *lru, gfp_t gfpflags, int node,
    unsigned long addr, size_t orig_size)
{
    void *object;
    bool init = false;

    s = slab_pre_alloc_hook(s, gfpflags);
    if (unlikely(!s))
        return NULL;

    object = kfence_alloc(s, orig_size, gfpflags);
    if (unlikely(object))
        goto out;

    object = alloc_from_pcs(s, gfpflags, node);  // Fast path from per-CPU sheaves

    if (!object)
        object = __slab_alloc_node(s, gfpflags, node, addr, orig_size);  // Slow path

    maybe_wipe_obj_freeptr(s, object);
    init = slab_want_init_on_alloc(gfpflags, s);

out:
    slab_post_alloc_hook(s, lru, gfpflags, 1, &object, init, orig_size);

    return object;
}
```

### ___slab_alloc (Slow Path)

Location: `mm/slub.c` (lines 4374-4449)

```c
static void *___slab_alloc(struct kmem_cache *s, gfp_t gfpflags, int node,
                           unsigned long addr, unsigned int orig_size)
{
    bool allow_spin = gfpflags_allow_spinning(gfpflags);
    void *object;
    struct slab *slab;
    struct partial_context pc;
    bool try_thisnode = true;

    stat(s, ALLOC_SLOWPATH);

new_objects:
    pc.flags = gfpflags;
    // ... node preference handling ...

    object = get_from_partial(s, node, &pc);  // Try partial slabs first
    if (object)
        goto success;

    slab = new_slab(s, pc.flags, node);  // Allocate new slab

    if (unlikely(!slab)) {
        // ... fallback handling ...
        return NULL;
    }

    stat(s, ALLOC_SLAB);

    if (IS_ENABLED(CONFIG_SLUB_TINY) || kmem_cache_debug(s)) {
        object = alloc_single_from_new_slab(s, slab, orig_size, gfpflags);
        if (likely(object))
            goto success;
    } else {
        alloc_from_new_slab(s, slab, &object, 1, allow_spin);
        if (likely(object))
            return object;
    }

    if (allow_spin)
        goto new_objects;

    return NULL;

success:
    if (kmem_cache_debug_flags(s, SLAB_STORE_USER))
        set_track(s, object, TRACK_ALLOC, addr, gfpflags);
    // ...
}
```

### kfree

Location: `mm/slub.c` (lines 6462-6485)

```c
void kfree(const void *object)
{
    struct page *page;
    struct slab *slab;
    struct kmem_cache *s;
    void *x = (void *)object;

    trace_kfree(_RET_IP_, object);

    if (unlikely(ZERO_OR_NULL_PTR(object)))
        return;

    page = virt_to_page(object);
    slab = page_slab(page);
    if (!slab) {
        /* kmalloc_nolock() doesn't support large kmalloc */
        free_large_kmalloc(page, (void *)object);
        return;
    }

    s = slab->slab_cache;
    slab_free(s, slab, x, _RET_IP_);
}
EXPORT_SYMBOL(kfree);
```

### slab_free

Location: `mm/slub.c` (lines 5970+)

The `slab_free` function handles freeing objects back to the slab:

1. Calls `kasan_slab_free()` for KASAN tracking
2. Calls `memcg_slab_free_hook()` for memory cgroup accounting
3. Returns object to the freelist via `__slab_free()` or `slab_free_head()`

---

## 4. Page Allocation

### 4.1 __alloc_pages_noprof

Location: `mm/page_alloc.c` (lines 5279-5288)

```c
struct page *__alloc_pages_noprof(gfp_t gfp, unsigned int order,
        int preferred_nid, nodemask_t *nodemask)
{
    struct page *page;

    page = __alloc_frozen_pages_noprof(gfp, order, preferred_nid, nodemask);
    if (page)
        set_page_refcounted(page);
    return page;
}
EXPORT_SYMBOL(__alloc_pages_noprof);
```

### __alloc_frozen_pages_noprof (Core Allocator)

Location: `mm/page_alloc.c` (lines 5214-5277)

```c
struct page *__alloc_frozen_pages_noprof(gfp_t gfp, unsigned int order,
        int preferred_nid, nodemask_t *nodemask)
{
    struct page *page;
    unsigned int alloc_flags = ALLOC_WMARK_LOW;
    gfp_t alloc_gfp;
    struct alloc_context ac = {};

    if (WARN_ON_ONCE_GFP(order > MAX_PAGE_ORDER, gfp))
        return NULL;

    gfp &= gfp_allowed_mask;
    gfp = current_gfp_context(gfp);
    alloc_gfp = gfp;

    if (!prepare_alloc_pages(gfp, order, preferred_nid, nodemask, &ac,
                            &alloc_gfp, &alloc_flags))
        return NULL;

    alloc_flags |= alloc_flags_nofragment(zonelist_zone(ac.preferred_zoneref), gfp);

    /* First allocation attempt */
    page = get_page_from_freelist(alloc_gfp, order, alloc_flags, &ac);
    if (likely(page))
        goto out;

    alloc_gfp = gfp;
    ac.spread_dirty_pages = false;
    ac.nodemask = nodemask;

    page = __alloc_pages_slowpath(alloc_gfp, order, &ac);

out:
    if (memcg_kmem_online() && (gfp & __GFP_ACCOUNT) && page &&
        unlikely(__memcg_kmem_charge_page(page, gfp, order) != 0)) {
        free_frozen_pages(page, order);
        page = NULL;
    }

    trace_mm_page_alloc(page, order, alloc_gfp, ac.migratetype);
    kmsan_alloc_page(page, order, alloc_gfp);

    return page;
}
```

### 4.2 get_page_from_freelist

Location: `mm/page_alloc.c` (lines 3808-3985)

```c
static struct page *
get_page_from_freelist(gfp_t gfp_mask, unsigned int order, int alloc_flags,
                      const struct alloc_context *ac)
{
    struct zoneref *z;
    struct zone *zone;
    struct pglist_data *last_pgdat = NULL;
    bool last_pgdat_dirty_ok = false;
    bool no_fallback;
    bool skip_kswapd_nodes = nr_online_nodes > 1;
    bool skipped_kswapd_nodes = false;

retry:
    /*
     * Scan zonelist, looking for a zone with enough free.
     */
    no_fallback = alloc_flags & ALLOC_NOFRAGMENT;
    z = ac->preferred_zoneref;
    for_next_zone_zonelist_nodemask(zone, z, ac->highest_zoneidx, ac->nodemask) {
        struct page *page;
        unsigned long mark;

        // ... cpuset checks ...

        if (ac->spread_dirty_pages) {
            // ... dirty page balancing ...
        }

        // ... nofragment handling ...

        if (skip_kswapd_nodes &&
            !waitqueue_active(&zone->zone_pgdat->kswapd_wait)) {
            skipped_kswapd_nodes = true;
            continue;
        }

        cond_accept_memory(zone, order, alloc_flags);

        /*
         * Check if below high watermark
         */
        if (test_bit(ZONE_BELOW_HIGH, &zone->flags))
            goto check_alloc_wmark;

        mark = high_wmark_pages(zone);
        if (zone_watermark_fast(zone, order, mark,
                               ac->highest_zoneidx, alloc_flags,
                               gfp_mask))
            goto try_this_zone;
        else
            set_bit(ZONE_BELOW_HIGH, &zone->flags);

check_alloc_wmark:
        mark = wmark_pages(zone, alloc_flags & ALLOC_WMARK_MASK);
        if (!zone_watermark_fast(zone, order, mark,
                                ac->highest_zoneidx, alloc_flags,
                                gfp_mask)) {
            // ... reclaim handling ...
            if (alloc_flags & ALLOC_NO_WATERMARKS)
                goto try_this_zone;

            if (!node_reclaim_enabled() ||
                !zone_allows_reclaim(zonelist_zone(ac->preferred_zoneref), zone))
                continue;

            ret = node_reclaim(zone->zone_pgdat, gfp_mask, order);
            // ... handle reclaim result ...
        }

try_this_zone:
        page = rmqueue(zonelist_zone(ac->preferred_zoneref), zone, order,
                      gfp_mask, alloc_flags, ac->migratetype);
        if (page) {
            prep_new_page(page, order, gfp_mask, alloc_flags);
            // ... high atomic pageblock reservation ...
            return page;
        }
        // ... retry logic ...
    }

    // ... final fallback handling ...
}
```

### Allocation Flow Summary

```
__alloc_pages()
  └── __alloc_pages_noprof()
        └── __alloc_frozen_pages_noprof()
              ├── prepare_alloc_pages()         # Setup alloc_context
              ├── get_page_from_freelist()      # Fast path
              │     └── rmqueue()              # Get page from buddy
              └── __alloc_pages_slowpath()     # Slow path (reclaim/compact)
                    ├── Try direct compaction
                    ├── Try direct reclaim
                    └── Wake kswapd and retry
```

### __alloc_pages_slowpath

Location: `mm/page_alloc.c` (lines 4710-4853)

Handles slow path allocation including:
- Direct compaction for high-order allocations
- Direct reclaim when memory is low
- Wake kswapd and wait for page balancing
- OOM killer invocation as last resort

---

## 5. Watermark Mechanism

### Watermark Levels

Location: `include/linux/mmzone.h` (lines 708-713)

```c
enum zone_watermarks {
    WMARK_MIN,
    WMARK_LOW,
    WMARK_HIGH,
    WMARK_PROMO,
    NR_WMARK
};
```

### Zone Watermark Storage

Location: `include/linux/mmzone.h` (line 883)

```c
struct zone {
    /* Read-mostly fields */

    /* zone watermarks, access with *_wmark_pages(zone) macros */
    unsigned long _watermark[NR_WMARK];
    unsigned long watermark_boost;
    // ...
};
```

### Watermark Access Functions

Location: `include/linux/mmzone.h` (lines 1077-1110)

```c
static inline unsigned long wmark_pages(const struct zone *z,
                                        enum zone_watermarks w)
{
    return z->_watermark[w] + z->watermark_boost;
}

static inline unsigned long min_wmark_pages(const struct zone *z)
{
    return wmark_pages(z, WMARK_MIN);
}

static inline unsigned long low_wmark_pages(const struct zone *z)
{
    return wmark_pages(z, WMARK_LOW);
}

static inline unsigned long high_wmark_pages(const struct zone *z)
{
    return wmark_pages(z, WMARK_HIGH);
}
```

### Watermark Check

Location: `mm/page_alloc.c` (lines 3680-3730)

```c
bool zone_watermark_ok(struct zone *z, unsigned int order, unsigned long mark,
                      int highest_zoneidx, unsigned int alloc_flags)
{
    return __zone_watermark_ok(z, order, mark, highest_zoneidx, alloc_flags,
                               zone_page_state(z, NR_FREE_PAGES));
}

static inline bool zone_watermark_fast(struct zone *z, unsigned int order,
                unsigned long mark, int highest_zoneidx,
                unsigned int alloc_flags, gfp_t gfp_mask)
{
    long free_pages;

    free_pages = zone_page_state(z, NR_FREE_PAGES);

    /* Fast check for order-0 only */
    if (!order) {
        long usable_free;
        long reserved;

        usable_free = free_pages;
        reserved = __zone_watermark_unusable_free(z, 0, alloc_flags);

        usable_free -= min(usable_free, reserved);
        if (usable_free > mark + z->lowmem_reserve[highest_zoneidx])
            return true;
    }

    if (__zone_watermark_ok(z, order, mark, highest_zoneidx, alloc_flags,
                           free_pages))
        return true;

    // ... watermark boost handling for __GFP_HIGH ...
    return false;
}
```

### __zone_watermark_ok

Location: `mm/page_alloc.c` (lines 3602-3678)

```c
bool __zone_watermark_ok(struct zone *z, unsigned int order, unsigned long mark,
                        int highest_zoneidx, unsigned int alloc_flags,
                        long free_pages)
{
    long min = mark;

    free_pages -= __zone_watermark_unusable_free(z, order, alloc_flags);

    if (unlikely(alloc_flags & ALLOC_RESERVES)) {
        /* __GFP_HIGH allows access to 50% of the min reserve */
        if (alloc_flags & ALLOC_MIN_RESERVE) {
            min -= min / 2;
            if (alloc_flags & ALLOC_NON_BLOCK)
                min -= min / 4;
        }
        if (alloc_flags & ALLOC_OOM)
            min -= min / 2;
    }

    /* Check order-0 watermark */
    if (free_pages <= min + z->lowmem_reserve[highest_zoneidx])
        return false;

    /* If order-0, watermark is fine */
    if (!order)
        return true;

    /* For high-order, check suitable pages exist */
    for (o = order; o < NR_PAGE_ORDERS; o++) {
        struct free_area *area = &z->free_area[o];
        int mt;

        if (!area->nr_free)
            continue;

        for (mt = 0; mt < MIGRATE_PCPTYPES; mt++) {
            if (!free_area_empty(area, mt))
                return true;
        }
        // ... CMA and HIGHATOMIC handling ...
    }
    return false;
}
```

### Watermark Levels Meaning

| Level | Purpose |
|-------|---------|
| `WMARK_MIN` | Minimum reserve; used for OOM and atomic allocations |
| `WMARK_LOW` | Kswapd wakeup threshold; triggers page reclaim |
| `WMARK_HIGH` | Zone is "full enough"; kswapd stops |
| `WMARK_PROMO` | Promotion threshold for demotion |

### Allocation Flags to Watermarks

Location: `mm/internal.h` (lines 1347-1349)

```c
#define ALLOC_WMARK_MIN     WMARK_MIN
#define ALLOC_WMARK_LOW     WMARK_LOW
#define ALLOC_WMARK_HIGH    WMARK_HIGH
```

The `ALLOC_WMARK_MASK` is used to select which watermark to check based on allocation context.

---

## Source File Summary

| File | Description |
|------|-------------|
| `mm/slab.h` | SLAB/SLUB common definitions |
| `mm/slub.c` | SLUB allocator implementation |
| `mm/slab_common.c` | Common slab allocator code (kmalloc, kfree) |
| `mm/page_alloc.c` | Page allocator (buddy system) |
| `include/linux/gfp.h` | GFP flags interface |
| `include/linux/gfp_types.h` | GFP flag definitions |
| `include/linux/mmzone.h` | Zone and watermark structures |

---

## Key Data Structures Relationship

```
kmem_cache (per-cache)
    ├── cpu_sheaves (per-CPU) → slab_sheaf → objects[]
    ├── node[] → kmem_cache_node (per-node)
    │              ├── partial list → slab
    │              └── barn → slab_sheaf (full/empty)
    └── slab (allocated from buddy)
           └── objects[]
```

---

## Key Functions

### Fast Path Allocation
- `alloc_from_pcs()` - mm/slub.c:2864
- `slab_alloc_node()` - mm/slub.c:4837

### Slow Path Allocation
- `___slab_alloc()` - mm/slub.c:4374
- `get_from_partial()` - mm/slub.c:1646
- `new_slab()` - mm/slub.c:2012

### Page Allocation
- `__alloc_pages_noprof()` - mm/page_alloc.c:5279
- `get_page_from_freelist()` - mm/page_alloc.c:3808
- `rmqueue()` - mm/page_alloc.c (buddy allocator)

### Memory Freeing
- `kfree()` - mm/slub.c:6462
- `slab_free()` - mm/slub.c:5970
- `__kmem_cache_free()` - mm/slub.c:6600+
