# Linux MM 子系统深度分析 R2

## 目录

1. [SLUB Freelist 机制](#1-slub-freelist-机制)
2. [kfree 与 __slab_free 快速路径](#2-kfree-与-__slab_free-快速路径)
3. [kmem_cache_alloc 分配流程](#3-kmem_cache_alloc-分配流程)
4. [Folio 生命周期管理](#4-folio-生命周期管理)
5. [内存压缩 (Compaction)](#5-内存压缩-compaction)
6. [Per-CPU Sheaves 设计](#6-per-cpu-sheaves-设计)
7. [知识点关联表](#7-知识点关联表)

---

## 1. SLUB Freelist 机制

### 1.1 数据结构概览

SLUB (SLAB Under用具) 是 Linux 内核的 slab 分配器,相比 SLAB 具有更低的开销和更好的扩展性。

```c
// mm/slub.c 第 396-425 行
struct node_barn {
    spinlock_t lock;
    struct list_head sheaves_full;   // 满sheaves链表
    struct list_head sheaves_empty;  // 空sheaves链表
    unsigned int nr_full;
    unsigned int nr_empty;
};

struct slab_sheaf {
    union {
        struct rcu_head rcu_head;
        struct list_head barn_list;
        struct {
            unsigned int capacity;
            bool pfmemalloc;
        };
    };
    struct kmem_cache *cache;
    unsigned int size;
    int node;
    void *objects[];  // 可变长度对象数组
};

struct slub_percpu_sheaves {
    local_trylock_t lock;
    struct slab_sheaf *main;      // 主sheaf,永不为NULL
    struct slab_sheaf *spare;     // 备用sheaf
    struct slab_sheaf *rcu_free; // RCU延迟释放sheaf
};
```

### 1.2 Freelist 指针编码

```c
// mm/slub.c 第 500-511 行
static inline freeptr_t freelist_ptr_encode(const struct kmem_cache *s,
                        void *ptr, unsigned long ptr_addr)
{
    unsigned long encoded;
#ifdef CONFIG_SLAB_FREELIST_HARDENED
    // 硬编码:ptr ^ random ^ swab(ptr_addr) 防止 freelist 被篡改
    encoded = (unsigned long)ptr ^ s->random ^ swab(ptr_addr);
#else
    encoded = (unsigned long)ptr;
#endif
    return (freeptr_t){.v = encoded};
}
```

Freelist 指针通过 `freelist_ptr_encode()` 进行编码,支持两种模式:
- **安全模式 (CONFIG_SLAB_FREELIST_HARDENED)**: 使用随机数和指针地址进行 XOR 编码
- **普通模式**: 直接存储指针值

### 1.3 Slab 状态转换

```
                    ┌──────────────────────────────────────────┐
                    │           Partial Slab                     │
                    │  (freelist != NULL, inuse < objects)    │
                    └─────────────────┬────────────────────────┘
                                      │ __slab_free (last object)
                                      ▼
┌──────────────────────────────────────────┐       ┌───────────────────────────┐
│            Full Slab                      │       │     Empty Slab            │
│  (freelist == NULL, inuse == objects)   │◄─────│ (freelist == NULL,        │
│  不在任何链表中                           │ discard│  inuse == 0)              │
└──────────────────────────────────────────┘  slab └───────────────────────────┘
         ▲
         │ __slab_free (first object from full)
         │
┌────────┴──────────────────────────────────────────┐
│            Frozen Slab                            │
│  (frozen = 1, consistency check failed)           │
│  永不分配,对象泄漏而非修改可能损坏的freelist        │
└───────────────────────────────────────────────────┘
```

### 1.4 page->freelist 与 cpu_partial

```c
// mm/slub.c 第 5499-5511 行
// __slab_free() 核心逻辑
do {
    old.freelist = slab->freelist;
    old.counters = slab->counters;
    was_full = (old.freelist == NULL);
    
    set_freepointer(s, tail, old.freelist);  // 构建新freelist
    new.freelist = head;
    new.counters = old.counters;
    new.inuse -= cnt;
    
    // slab变空或变满时需要修改partial链表
    if (!new.inuse || was_full) {
        n = get_node(s, slab_nid(slab));
        spin_lock_irqsave(&n->list_lock, flags);
        on_node_partial = slab_test_node_partial(slab);
    }
} while (!slab_update_freelist(s, slab, &old, &new, "__slab_free"));
```

---

## 2. kfree 与 __slab_free 快速路径

### 2.1 kfree() 调用链

```c
// mm/slub.c 第 6462-6484 行
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
        // 大型kmalloc对象
        free_large_kmalloc(page, (void *)object);
        return;
    }
    
    s = slab->slab_cache;
    slab_free(s, slab, x, _RET_IP_);
}
```

### 2.2 slab_free() 快速路径

```c
// mm/slub.c 第 6158-6176 行
static __fastpath_inline
void slab_free(struct kmem_cache *s, struct slab *slab, void *object,
           unsigned long addr)
{
    memcg_slab_free_hook(s, slab, &object, 1);
    alloc_tagging_slab_free_hook(s, slab, &object, 1);
    
    if (unlikely(!slab_free_hook(s, object, slab_want_init_on_free(s), false)))
        return;  // 被KASAN/KFENCE延迟释放
    
    // 快速路径:本地节点 + 非pfmemalloc -> 尝试per-CPU sheaves
    if (likely(!IS_ENABLED(CONFIG_NUMA) || slab_nid(slab) == numa_mem_id())
        && likely(!slab_test_pfmemalloc(slab))) {
        if (likely(free_to_pcs(s, object, true)))
            return;  // 成功放入sheaf
    }
    
    // 慢速路径:需要修改slab
    __slab_free(s, slab, object, object, 1, addr);
    stat(s, FREE_SLOWPATH);
}
```

### 2.3 free_to_pcs() Per-CPU Sheaf 快速释放

```c
// mm/slub.c 第 5763-5787 行
static __fastpath_inline
bool free_to_pcs(struct kmem_cache *s, void *object, bool allow_spin)
{
    struct slub_percpu_sheaves *pcs;
    
    if (!local_trylock(&s->cpu_sheaves->lock))
        return false;  // 获取本地锁失败
    
    pcs = this_cpu_ptr(s->cpu_sheaves);
    
    if (unlikely(pcs->main->size == s->sheaf_capacity)) {
        // main shea已满,尝试替换
        pcs = __pcs_replace_full_main(s, pcs, allow_spin);
        if (unlikely(!pcs))
            return false;
    }
    
    pcs->main->objects[pcs->main->size++] = object;
    
    local_unlock(&s->cpu_sheaves->lock);
    stat(s, FREE_FASTPATH);
    return true;
}
```

### 2.4 __slab_free() 慢速路径

```c
// mm/slub.c 第 5470-5574 行
static void __slab_free(struct kmem_cache *s, struct slab *slab,
            void *head, void *tail, int cnt,
            unsigned long addr)
{
    bool was_full;
    struct freelist_counters old, new;
    struct kmem_cache_node *n = NULL;
    unsigned long flags;
    bool on_node_partial;
    
    if (IS_ENABLED(CONFIG_SLUB_TINY) || kmem_cache_debug(s)) {
        free_to_partial_list(s, slab, head, tail, cnt, addr);
        return;
    }
    
    // 使用cmpxchg原子更新freelist
    do {
        if (unlikely(n)) {
            spin_unlock_irqrestore(&n->list_lock, flags);
            n = NULL;
        }
        
        old.freelist = slab->freelist;
        old.counters = slab->counters;
        was_full = (old.freelist == NULL);
        
        set_freepointer(s, tail, old.freelist);
        new.freelist = head;
        new.counters = old.counters;
        new.inuse -= cnt;
        
        // 需要修改partial链表?
        if (!new.inuse || was_full) {
            n = get_node(s, slab_nid(slab));
            spin_lock_irqsave(&n->list_lock, flags);
            on_node_partial = slab_test_node_partial(slab);
        }
    } while (!slab_update_freelist(s, slab, &old, &new, "__slab_free"));
    
    // 处理slab变空的情况
    if (unlikely(!new.inuse && n->nr_partial >= s->min_partial))
        goto slab_empty;
    
    // 添加到partial链表
    if (unlikely(was_full)) {
        add_partial(n, slab, ADD_TO_TAIL);
        stat(s, FREE_ADD_PARTIAL);
    }
    
    return;
    
slab_empty:
    // slab完全为空,从partial链表移除并释放
    if (likely(!was_full)) {
        remove_partial(n, slab);
        stat(s, FREE_REMOVE_PARTIAL);
    }
    spin_unlock_irqrestore(&n->list_lock, flags);
    stat(s, FREE_SLAB);
    discard_slab(s, slab);
}
```

### 2.5 kmem_cache_open / create_cache

```c
// mm/slab_common.c 第 232-264 行
static struct kmem_cache *create_cache(const char *name,
                       unsigned int object_size,
                       struct kmem_cache_args *args,
                       slab_flags_t flags)
{
    struct kmem_cache *s;
    int err;
    
    err = -ENOMEM;
    s = kmem_cache_zalloc(kmem_cache, GFP_KERNEL);  // 从boot缓存分配
    if (!s)
        goto out;
    err = do_kmem_cache_create(s, name, object_size, args, flags);
    if (err)
        goto out_free_cache;
    
    s->refcount = 1;
    list_add(&s->list, &slab_caches);
    return s;
    
out_free_cache:
    kmem_cache_free(kmem_cache, s);
out:
    return ERR_PTR(err);
}
```

---

## 3. kmem_cache_alloc 分配流程

### 3.1 slab_alloc_node() 快速路径

```c
// mm/slub.c 第 4837-4869 行
static __fastpath_inline void *slab_alloc_node(struct kmem_cache *s, 
    struct list_lru *lru, gfp_t gfpflags, int node, 
    unsigned long addr, size_t orig_size)
{
    void *object;
    bool init = false;
    
    s = slab_pre_alloc_hook(s, gfpflags);
    if (unlikely(!s))
        return NULL;
    
    object = kfence_alloc(s, orig_size, gfpflags);  // KFENCE分配
    if (unlikely(object))
        goto out;
    
    // 首先尝试从per-CPU sheaves分配
    object = alloc_from_pcs(s, gfpflags, node);
    
    if (!object)
        // sheaves为空,走慢速路径
        object = __slab_alloc_node(s, gfpflags, node, addr, orig_size);
    
    maybe_wipe_obj_freeptr(s, object);
    init = slab_want_init_on_alloc(gfpflags, s);
    
out:
    slab_post_alloc_hook(s, lru, gfpflags, 1, &object, init, orig_size);
    return object;
}
```

### 3.2 alloc_from_pcs() Per-CPU Sheaf 快速分配

```c
// mm/slub.c 第 4671-4744 行
static __fastpath_inline
void *alloc_from_pcs(struct kmem_cache *s, gfp_t gfp, int node)
{
    struct slub_percpu_sheaves *pcs;
    bool node_requested;
    void *object;
    
    node_requested = IS_ENABLED(CONFIG_NUMA) && node != NUMA_NO_NODE;
    
    // 节点不匹配时快速失败
    if (unlikely(node_requested && node != numa_mem_id())) {
        stat(s, ALLOC_NODE_MISMATCH);
        return NULL;
    }
    
    if (!local_trylock(&s->cpu_sheaves->lock))
        return NULL;
    
    pcs = this_cpu_ptr(s->cpu_sheaves);
    
    // sheaves为空,尝试替换
    if (unlikely(pcs->main->size == 0)) {
        pcs = __pcs_replace_empty_main(s, pcs, gfp);
        if (unlikely(!pcs))
            return NULL;
    }
    
    object = pcs->main->objects[pcs->main->size - 1];
    
    // 节点验证
    if (unlikely(node_requested)) {
        if (page_to_nid(virt_to_page(object)) != node) {
            local_unlock(&s->cpu_sheaves->lock);
            stat(s, ALLOC_NODE_MISMATCH);
            return NULL;
        }
    }
    
    pcs->main->size--;
    
    local_unlock(&s->cpu_sheaves->lock);
    stat(s, ALLOC_FASTPATH);
    return object;
}
```

### 3.3 __slab_alloc_node() 慢速路径

```c
// mm/slub.c 第 4374-4451 行
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
    pc.orig_size = orig_size;
    
    // 优先尝试目标节点的partial slab
    if (unlikely(node != NUMA_NO_NODE && !(gfpflags & __GFP_THISNODE)
             && try_thisnode)) {
        if (unlikely(!allow_spin))
            pc.flags = gfpflags | __GFP_THISNODE;
        else
            pc.flags = GFP_NOWAIT | __GFP_THISNODE;
    }
    
    object = get_from_partial(s, node, &pc);
    if (object)
        goto success;
    
    // 分配新的slab
    slab = new_slab(s, pc.flags, node);
    
    if (unlikely(!slab)) {
        if (node != NUMA_NO_NODE && !(gfpflags & __GFP_THISNODE)
            && try_thisnode) {
            try_thisnode = false;
            goto new_objects;
        }
        slab_out_of_memory(s, gfpflags, node);
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
    
    return object;
}
```

### 3.4 gfpflags_to_policy (内存分配策略)

注:在较新内核版本中,`gfpflags_to_policy` 已被重构或更名。GFP标志到内存策略的映射主要通过以下方式处理:

```c
// mm/slub.c 第 4678-4698 行 (alloc_from_pcs NUMA处理)
#ifdef CONFIG_NUMA
if (static_branch_unlikely(&strict_numa) &&
         node == NUMA_NO_NODE) {
    struct mempolicy *mpol = current->mempolicy;
    
    if (mpol) {
        if (mpol->mode != MPOL_BIND ||
                !node_isset(numa_mem_id(), mpol->nodes))
            node = mempolicy_slab_node();
    }
}
#endif
```

GFP标志映射关系:
- `__GFP_THISNODE` -> 强制本地节点分配
- `GFP_KERNEL` -> 可回收,可阻塞
- `GFP_ATOMIC` -> 不可睡眠,高优先级
- `GFP_NOWAIT` -> 不等待,不重试

---

## 4. Folio 生命周期管理

### 4.1 Folio 分配 (folio_alloc)

```c
// mm/page_alloc.c 第 5291-5298 行
struct folio *__folio_alloc_noprof(gfp_t gfp, unsigned int order, int preferred_nid,
        nodemask_t *nodemask)
{
    struct page *page = __alloc_pages_noprof(gfp | __GFP_COMP, order,
                    preferred_nid, nodemask);
    return page_rmappable_folio(page);
}
EXPORT_SYMBOL(__folio_alloc_noprof);
```

Folio 分配核心路径:
```
folio_alloc()
    └─> __folio_alloc()
            └─> __alloc_pages()
                    └─> get_page_from_freelist()
                    └─> __alloc_pages_slowpath()
                            └─> compaction_alloc()  // 内存压缩
```

### 4.2 folio_add_new_anon_rmap() 匿名映射

```c
// mm/rmap.c 第 1636-1675 行
void folio_add_new_anon_rmap(struct folio *folio, struct vm_area_struct *vma,
        unsigned long address, rmap_t flags)
{
    const bool exclusive = flags & RMAP_EXCLUSIVE;
    int nr = 1, nr_pmdmapped = 0;
    
    VM_WARN_ON_FOLIO(folio_test_hugetlb(folio), folio);
    VM_WARN_ON_FOLIO(!exclusive && !folio_test_locked(folio), folio);
    
    // 设置swapbacked标志
    if (!folio_test_swapbacked(folio) && !(vma->vm_flags & VM_DROPPABLE))
        __folio_set_swapbacked(folio);
    __folio_set_anon(folio, vma, address, exclusive);
    
    if (likely(!folio_test_large(folio))) {
        atomic_set(&folio->_mapcount, 0);  // mapcount从-1变为0
        if (exclusive)
            SetPageAnonExclusive(&folio->page);
    } else if (!folio_test_pmd_mappable(folio)) {
        // THP:逐页设置
        int i;
        nr = folio_large_nr_pages(folio);
        for (i = 0; i < nr; i++) {
            struct page *page = folio_page(folio, i);
            if (IS_ENABLED(CONFIG_PAGE_MAPCOUNT))
                atomic_set(&page->_mapcount, 0);
            if (exclusive)
                SetPageAnonExclusive(page);
        }
    }
}
```

### 4.3 Folio 释放

Folio 释放分为多种情况:

```c
// mm/swap_state.c 第 380-390 行
bool folio_free_swap(struct folio *folio)
{
    bool ret = false;
    
    spin_lock_irq(&folio->mapping->i_pages.lock);
    if (!folio_test_swapcache(folio) || !folio_test_dirty(folio))
        goto out;
    
    // 清除swap缓存中的脏标志
    ret = delete_from_swap_cache(folio);
out:
    spin_unlock_irq(&folio->mapping->i_pages.lock);
    return ret;
}
```

Folio 释放流程:
```
folio_free()
    ├─> folio_remove_rmap()      // 移除反向映射
    ├─> folio_release()          // 释放页引用
    └─> free_pages_prepared()   // 返回buddy系统
```

### 4.4 Folio 生命周期状态机

```
                    ┌─────────────┐
                    │   Folio     │
                    │  Allocated  │
                    └──────┬──────┘
                           │ folio_add_new_anon_rmap()
                           ▼
                    ┌─────────────┐
                    │   Anon      │
                    │   Folio     │
                    └──────┬──────┘
                           │ folio_free() / swapout
                           ▼
                    ┌─────────────┐
                    │  Swap       │
                    │  Folio      │
                    └──────┬──────┘
                           │ folio_free_swap()
                           ▼
                    ┌─────────────┐
                    │   Buddy     │
                    │   System    │
                    └─────────────┘
```

---

## 5. 内存压缩 (Compaction)

### 5.1 compact_zone() 主流程

```c
// mm/compaction.c 第 2510-2720 行
static enum compact_result
compact_zone(struct compact_control *cc, struct capture_control *capc)
{
    enum compact_result ret;
    unsigned long start_pfn = cc->zone->zone_start_pfn;
    unsigned long end_pfn = zone_end_pfn(cc->zone);
    unsigned long last_migrated_pfn;
    const bool sync = cc->mode != MIGRATE_ASYNC;
    
    // 初始化
    cc->total_migrate_scanned = 0;
    cc->total_free_scanned = 0;
    cc->nr_migratepages = 0;
    cc->nr_freepages = 0;
    
    cc->migratetype = gfp_migratetype(cc->gfp_mask);
    
    // 检查是否适合压缩
    ret = compaction_suit_allocation_order(cc->zone, cc->order, ...);
    if (ret != COMPACT_CONTINUE)
        return ret;
    
    // 设置扫描起点
    cc->migrate_pfn = cc->zone->compact_cached_migrate_pfn[sync];
    cc->free_pfn = cc->zone->compact_cached_free_pfn;
    
    trace_mm_compaction_begin(cc, start_pfn, end_pfn, sync);
    
    lru_add_drain();
    
    // 主压缩循环
    while ((ret = compact_finished(cc)) == COMPACT_CONTINUE) {
        // 1. 隔离可迁移页面
        switch (isolate_migratepages(cc)) {
        case ISOLATE_ABORT:
            ret = COMPACT_CONTENDED;
            goto out;
        case ISOLATE_NONE:
            goto check_drain;
        case ISOLATE_SUCCESS:
            update_cached = false;
        }
        
        // 2. 迁移页面
        nr_migratepages = cc->nr_migratepages;
        err = migrate_pages(&cc->migratepages, compaction_alloc,
                compaction_free, (unsigned long)cc, cc->mode,
                MR_COMPACTION, &nr_succeeded);
        
        trace_mm_compaction_migratepages(nr_migratepages, nr_succeeded);
        
        // 3. 处理失败
        if (err) {
            putback_movable_pages(&cc->migratepages);
            if (err == -ENOMEM && !compact_scanners_met(cc)) {
                ret = COMPACT_CONTENDED;
                goto out;
            }
        }
    }
    
out:
    return ret;
}
```

### 5.2 compaction_alloc() 分配回调

```c
// mm/compaction.c 第 1797-1848 行
static struct folio *compaction_alloc_noprof(struct folio *src, unsigned long data)
{
    struct compact_control *cc = (struct compact_control *)data;
    struct folio *dst;
    int order = folio_order(src);
    bool has_isolated_pages = false;
    int start_order;
    struct page *freepage;
    unsigned long size;
    
again:
    // 从freepages列表中寻找合适大小的页面
    for (start_order = order; start_order < NR_PAGE_ORDERS; start_order++)
        if (!list_empty(&cc->freepages[start_order]))
            break;
    
    // 列表为空,尝试隔离更多页面
    if (start_order == NR_PAGE_ORDERS) {
        if (has_isolated_pages)
            return NULL;
        isolate_freepages(cc);
        has_isolated_pages = true;
        goto again;
    }
    
    freepage = list_first_entry(&cc->freepages[start_order], struct page, lru);
    size = 1 << start_order;
    
    list_del(&freepage->lru);
    
    // 分割大块为请求大小
    while (start_order > order) {
        start_order--;
        size >>= 1;
        list_add(&freepage[size].lru, &cc->freepages[start_order]);
        set_page_private(&freepage[size], start_order);
    }
    dst = (struct folio *)freepage;
    
    post_alloc_hook(&dst->page, order, __GFP_MOVABLE);
    set_page_refcounted(&dst->page);
    if (order)
        prep_compound_page(&dst->page, order);
    
    cc->nr_freepages -= 1 << order;
    cc->nr_migratepages -= 1 << order;
    return page_rmappable_folio(&dst->page);
}
```

### 5.3 migrate_pages() 页面迁移

```c
// mm/migrate.c 第 2072-2115 行
int migrate_pages(struct list_head *from, new_folio_t get_new_folio,
        free_folio_t put_new_folio, unsigned long private,
        enum migrate_mode mode, int reason, unsigned int *ret_succeeded)
{
    int rc, rc_gather;
    int nr_pages;
    struct folio *folio, *folio2;
    LIST_HEAD(folios);
    LIST_HEAD(ret_folios);
    LIST_HEAD(split_folios);
    struct migrate_pages_stats stats;
    
    trace_mm_migrate_pages_start(mode, reason);
    
    memset(&stats, 0, sizeof(stats));
    
    // 先处理巨页
    rc_gather = migrate_hugetlbs(from, get_new_folio, put_new_folio, private,
                     mode, reason, &stats, &ret_folios);
    if (rc_gather < 0)
        goto out;
    
again:
    nr_pages = 0;
    list_for_each_entry_safe(folio, folio2, from, lru) {
        if (folio_test_hugetlb(folio)) {
            list_move_tail(&folio->lru, &ret_folios);
            continue;
        }
        
        nr_pages += folio_nr_pages(folio);
        
        // 核心迁移逻辑
        rc = folio_migrate(folio, get_new_folio, put_new_folio, private, mode);
        
        if (rc == MIGRATEPAGE_SUCCESS)
            continue;
        
        // 处理迁移失败
        ...
    }
    
out:
    return rc;
}
```

### 5.4 内存压缩流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    compact_zone()                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  初始化:设置migrate_pfn, free_pfn扫描边界         │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  while(compact_finished() == COMPACT_CONTINUE)    │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │  isolate_migratepages()                       │ │   │
│  │  │  - 扫描migrate_pfn开始的页面                   │ │   │
│  │  │  - 隔离LRU上的可迁移页面                       │ │   │
│  │  │  - 加入migratepages链表                        │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  │                          │                           │   │
│  │                          ▼                           │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │  migrate_pages(migratepages,                   │ │   │
│  │  │           compaction_alloc,                    │ │   │
│  │  │           compaction_free, cc, ...)            │ │   │
│  │  │  - 为每个页面分配新页面(compaction_alloc)      │ │   │
│  │  │  - 复制内容到新页面                            │ │   │
│  │  │  - 更新页表映射                               │ │   │
│  │  │  - 释放旧页面(compaction_free)                │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  │                          │                           │   │
│  │                          ▼                           │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │  isolate_freepages()                          │ │   │
│  │  │  - 扫描free_pfn                              │ │   │
│  │  │  - 从伙伴系统隔离空闲页面                     │ │   │
│  │  │  - 加入freepages链表                         │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  compact_finished() 检查完成条件                    │   │
│  │  - migrate_pfn >= free_pfn (扫描器相遇)            │   │
│  │  - 找到足够大的空闲页面                             │   │
│  │  - 扫描完成                                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Per-CPU Sheaves 设计

### 6.1 Sheaf 数据结构

```c
// mm/slub.c 第 404-425 行
struct slab_sheaf {
    union {
        struct rcu_head rcu_head;       // RCU延迟释放头
        struct list_head barn_list;      // 链表节点
        struct {
            unsigned int capacity;       // 容量
            bool pfmemalloc;             // 是否来自pfmemalloc
        };
    };
    struct kmem_cache *cache;            // 所属缓存
    unsigned int size;                   // 当前对象数
    int node;                            // NUMA节点(RCU sheaf使用)
    void *objects[];                     // 对象指针数组
};

struct slub_percpu_sheaves {
    local_trylock_t lock;               // 本地锁(仅禁用抢占)
    struct slab_sheaf *main;            // 主sheaf,永不为NULL
    struct slab_sheaf *spare;            // 备用sheaf(空的或满的)
    struct slab_sheaf *rcu_free;         // RCU批量释放sheaf
};
```

### 6.2 Sheaf 状态机

```
┌────────────────────────────────────────────────────────────────────┐
│                    Per-CPU Sheaf 状态机                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Main      │◄──►│   Spare     │    │  RCU_Free   │          │
│  │  Sheaf      │ swap│  Sheaf      │    │  Sheaf      │          │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘          │
│         │                   │                   │                 │
│         │ main->size == 0  │ spare->size > 0   │ size == cap     │
│         │     或           │                   │                 │
│         │ main->size ==   │                   │                 │
│         │ sheaf_capacity   │                   ▼                 │
│         │                 │          ┌─────────────────┐         │
│         │                 │          │ call_rcu()     │         │
│         │                 │          │ rcu_free_sheaf │         │
│         │                 │          └─────────────────┘         │
│         │                 │                                       │
│         ▼                 ▼                                       │
│  ┌─────────────────────────────────────────────┐                  │
│  │           __pcs_replace_empty_main()        │                  │
│  │  1. spare非空 -> swap(main, spare)         │                  │
│  │  2. spare为空 -> 从barn获取empty sheaf    │                  │
│  │  3. barn为空   -> 分配新sheaf              │                  │
│  │  4. 从new slab填充sheaf                    │                  │
│  └─────────────────────────────────────────────┘                  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 6.3 allocate_slab() 分配新 Slab

```c
// mm/slub.c 第 3455-3530 行
static struct slab *allocate_slab(struct kmem_cache *s, gfp_t flags, int node)
{
    bool allow_spin = gfpflags_allow_spinning(flags);
    struct slab *slab;
    struct kmem_cache_order_objects oo = s->oo;
    gfp_t alloc_gfp;
    void *start, *p, *next;
    int idx;
    bool shuffle;
    
    flags &= gfp_allowed_mask;
    flags |= s->allocflags;
    
    // 初始分配失败时降低order
    alloc_gfp = (flags | __GFP_NOWARN | __GFP_NORETRY) & ~__GFP_NOFAIL;
    if ((alloc_gfp & __GFP_DIRECT_RECLAIM) && oo_order(oo) > oo_order(s->min))
        alloc_gfp = (alloc_gfp | __GFP_NOMEMALLOC) & ~__GFP_RECLAIM;
    
    // 尝试分配slab页面
    slab = alloc_slab_page(alloc_gfp, node, oo, allow_spin);
    if (unlikely(!slab)) {
        oo = s->min;
        alloc_gfp = flags;
        slab = alloc_slab_page(alloc_gfp, node, oo, allow_spin);
        if (unlikely(!slab))
            return NULL;
        stat(s, ORDER_FALLBACK);
    }
    
    slab->objects = oo_objects(oo);
    slab->inuse = 0;
    slab->frozen = 0;
    slab->slab_cache = s;
    
    kasan_poison_slab(slab);
    
    start = slab_address(slab);
    setup_slab_debug(s, slab, start);
    init_slab_obj_exts(slab);
    alloc_slab_obj_exts_early(s, slab);
    account_slab(slab, oo_order(oo), s, flags);
    
    // 随机化freelist顺序
    shuffle = shuffle_freelist(s, slab, allow_spin);
    
    if (!shuffle) {
        // 线性初始化freelist
        start = fixup_red_left(s, start);
        start = setup_object(s, start);
        slab->freelist = start;
        for (idx = 0, p = start; idx < slab->objects - 1; idx++) {
            next = p + s->size;
            next = setup_object(s, next);
            set_freepointer(s, p, next);
            p = next;
        }
        set_freepointer(s, p, NULL);
    }
    
    return slab;
}
```

### 6.4 put_cpu_slab / allocate_slab 协作

注意:在当前 SLUB 实现中,没有直接的 `put_cpu_slab()` 函数。slab 通过以下方式返回到系统:

```c
// mm/slub.c 第 3576-3590 行
static void free_slab(struct kmem_cache *s, struct slab *slab)
{
    if (kmem_cache_debug_flags(s, SLAB_CONSISTENCY_CHECKS)) {
        // 检查slab完整性
        slab_pad_check(s, slab);
        for_each_object(p, s, slab_address(slab), slab->objects)
            check_object(s, slab, p, SLUB_RED_INACTIVE);
    }
    
    if (unlikely(s->flags & SLAB_TYPESAFE_BY_RCU))
        call_rcu(&slab->rcu_head, rcu_free_slab);
    else
        __free_slab(s, slab, true);
}

// mm/slub.c 第 3543-3558 行
static void __free_slab(struct kmem_cache *s, struct slab *slab, bool allow_spin)
{
    struct page *page = slab_page(slab);
    int order = compound_order(page);
    
    __slab_clear_pfmemalloc(slab);
    page->mapping = NULL;
    __ClearPageSlab(page);
    mm_account_reclaimed_pages(1 << order);
    unaccount_slab(slab, order, s, allow_spin);
    if (allow_spin)
        free_frozen_pages(page, order);
    else
        free_frozen_pages_nolock(page, order);
}
```

---

## 7. 知识点关联表

| 模块 | 关键函数 | 行号 | 核心机制 |
|------|----------|------|----------|
| **SLUB Freelist** | `freelist_ptr_encode()` | 500-511 | Freelist指针XOR编码防篡改 |
| | `slab_update_freelist()` | 632-695 | cmpxchg原子更新freelist |
| | `__slab_free()` | 5470-5574 | 慢速路径,维护partial链表 |
| **kfree** | `slab_free()` | 6158-6176 | 快速路径->per-CPU sheaf |
| | `free_to_pcs()` | 5763-5787 | Per-CPU sheaf快速释放 |
| | `kmem_cache_free()` | 6275-6296 | 公共接口 |
| **kmem_cache_alloc** | `slab_alloc_node()` | 4837-4869 | 主分配函数 |
| | `alloc_from_pcs()` | 4671-4744 | Per-CPU sheaf快速分配 |
| | `___slab_alloc()` | 4374-4451 | 慢速路径,partial链表/slab分配 |
| **Folio Lifecycle** | `__folio_alloc_noprof()` | 5291-5298 | Folio分配 |
| | `folio_add_new_anon_rmap()` | 1636-1675 | 匿名映射添加 |
| | `folio_free_swap()` | 1876-1880 | Swap缓存释放 |
| **Compaction** | `compact_zone()` | 2511-2720 | 区域压缩主循环 |
| | `compaction_alloc()` | 1845-1848 | 压缩分配回调 |
| | `migrate_pages()` | 2072-2115 | 页面迁移核心 |
| | `isolate_migratepages_block()` | 837-1308 | 页面隔离 |
| **Per-CPU Sheaves** | `slab_sheaf` 结构 | 404-418 | Sheaf数据结构 |
| | `slub_percpu_sheaves` 结构 | 420-425 | Per-CPU sheaves容器 |
| | `allocate_slab()` | 3455-3530 | 新slab分配 |
| | `free_slab()` | 3576-3590 | Slab释放 |

### 7.1 调用关系图

```
kfree(object)
    └─> slab_free(s, slab, object, addr)
            ├─> free_to_pcs()          [快速路径]
            │       └─> __pcs_replace_full_main()
            │               └─> barn_replace_full_sheaf()
            └─> __slab_free()          [慢速路径]
                    └─> slab_update_freelist()
                            └─> add_partial() / remove_partial()

kmem_cache_alloc(s, gfp)
    └─> slab_alloc_node(s, NULL, gfp, NUMA_NO_NODE, ip, size)
            ├─> alloc_from_pcs()        [快速路径]
            │       └─> __pcs_replace_empty_main()
            │               └─> barn_replace_empty_sheaf()
            └─> __slab_alloc_node()    [慢速路径]
                    ├─> get_from_partial()
                    └─> new_slab()
                            └─> allocate_slab()

compact_zone(cc)
    └─> isolate_migratepages()
    └─> migrate_pages(migratepages, compaction_alloc, ...)
            └─> compaction_alloc()
                    └─> isolate_freepages()  [当freepages不足时]
```

### 7.2 关键数据结构关系

```
kmem_cache
    ├─> cpu_sheaves [percpu] ──> slub_percpu_sheaves
    │                           ├─> main (slab_sheaf) ──> objects[]
    │                           ├─> spare (slab_sheaf)
    │                           └─> rcu_free (slab_sheaf)
    │
    ├─> node[] ──> kmem_cache_node
    │             ├─> partial (list) ──> slab
    │             ├─> barn ──> node_barn
    │             │           ├─> sheaves_full
    │             │           └─> sheaves_empty
    │             └─> list_lock
    │
    └─> slab (page) ──> freelist指针链
              ├─> objects (对象数)
              ├─> inuse (已使用数)
              └─> frozen (是否冻结)
```

### 7.3 内存分配标志(GFP)速查

| 标志 | 含义 | 使用场景 |
|------|------|----------|
| `GFP_KERNEL` | 普通分配,可睡眠,可回收 | 常规内核内存分配 |
| `GFP_ATOMIC` | 原子分配,不可睡眠 | 中断处理,spinlock上下文 |
| `GFP_NOWAIT` | 不等待,不重试 | 快速路径,不能失败 |
| `GFP_NOIO` | 不触发IO | 避免递归文件系统 |
| `GFP_NOFS` | 不触发文件系统调用 | 避免递归 |
| `__GFP_THISNODE` | 强制本地节点 | NUMA亲密性 |
| `__GFP_DIRECT_RECLAIM` | 允许直接回收 | 内存压力时回收 |
| `__GFP_KSWAPD_RECLAIM` | 允许kswapd回收 | 后台回收 |

---

本文档基于 Linux kernel 6.x 源码分析,涵盖了 SLUB 分配器的 freelist 机制、per-CPU sheaves、folio 生命周期、内存压缩等核心子系统的深度设计。