# Linux Kernel 页面回收机制分析

本文档分析 Linux 内核的页面回收（Page Reclaim）机制，基于 mm/vmscan.c 及相关文件。

---

## 1. LRU 链表结构和类型

### 1.1 LRU 链表定义

**源码位置**: `include/linux/mmzone.h` 第 316-323 行

```c
enum lru_list {
    LRU_INACTIVE_ANON = LRU_BASE,        // 0: 非活跃匿名页
    LRU_ACTIVE_ANON = LRU_BASE + LRU_ACTIVE,  // 1: 活跃匿名页
    LRU_INACTIVE_FILE = LRU_BASE + LRU_FILE,  // 2: 非活跃文件页
    LRU_ACTIVE_FILE = LRU_BASE + LRU_FILE + LRU_ACTIVE,  // 3: 活跃文件页
    LRU_UNEVICTABLE,                     // 4: 不可回收页
    NR_LRU_LISTS                         // 5: LRU 链表总数
};
```

其中:
- `LRU_BASE = 0`
- `LRU_ACTIVE = 1`
- `LRU_FILE = 2`

### 1.2 LRU 链表组织

**struct lruvec** (`include/linux/mmzone.h` 第 669-698 行):
```c
struct lruvec {
    struct list_head        lists[NR_LRU_LISTS];  // 5个LRU链表
    spinlock_t              lru_lock;              // 保护LRU链表的锁
    unsigned long           anon_cost;             // 匿名页回收成本
    unsigned long           file_cost;              // 文件页回收成本
    atomic_long_t           nonresident_age;       // 非驻留年龄
    unsigned long           refaults[ANON_AND_FILE]; // 上次回收周期的回填数
    unsigned long           flags;                 // lruvec状态标志
#ifdef CONFIG_LRU_GEN
    struct lru_gen_folio    lrugen;                // Multi-Gen LRU
#endif
    ...
};
```

### 1.3 LRU 页面判断

**folio_lru_list()** (`include/linux/mm_inline.h` 第 87-101 行):
```c
static __always_inline enum lru_list folio_lru_list(const struct folio *folio)
{
    if (folio_test_unevictable(folio))
        return LRU_UNEVICTABLE;

    lru = folio_is_file_lru(folio) ? LRU_INACTIVE_FILE : LRU_INACTIVE_ANON;
    if (folio_test_active(folio))
        lru += LRU_ACTIVE;

    return lru;
}
```

**folio_is_file_lru()** (`include/linux/mm_inline.h` 第 28-31 行):
```c
static inline int folio_is_file_lru(const struct folio *folio)
{
    return !folio_test_swapbacked(folio);
}
```

### 1.4 Multi-Gen LRU 结构

**struct lru_gen_folio** (`include/linux/mmzone.h` 第 490-518 行):
```c
struct lru_gen_folio {
    unsigned long max_seq;    // 最年轻代序号
    unsigned long min_seq[ANON_AND_FILE];  // 最老代序号（分别追踪anon和file）
    unsigned long timestamps[MAX_NR_GENS];  // 每代的创建时间
    struct list_head folios[MAX_NR_GENS][ANON_AND_FILE][MAX_NR_ZONES];
    long nr_pages[MAX_NR_GENS][ANON_AND_FILE][MAX_NR_ZONES];
    unsigned long avg_refaulted[ANON_AND_FILE][MAX_NR_TIERS];
    unsigned long avg_total[ANON_AND_FILE][MAX_NR_TIERS];
    atomic_long_t evicted[NR_HIST_GENS][ANON_AND_FILE][MAX_NR_TIERS];
    atomic_long_t refaulted[NR_HIST_GENS][ANON_AND_FILE][MAX_NR_TIERS];
    bool enabled;
    ...
};
```

- `MIN_NR_GENS = 2` (最少需要2代来实现"第二次机会"算法)
- `MAX_NR_GENS = 4` (最大支持4代)

---

## 2. kswapd 守护线程和唤醒条件

### 2.1 kswapd 线程初始化

**kswapd_run()** (`mm/vmscan.c` 第 7474-7492 行):
```c
void __meminit kswapd_run(int nid)
{
    pg_data_t *pgdat = NODE_DATA(nid);

    pgdat_kswapd_lock(pgdat);
    if (!pgdat->kswapd) {
        pgdat->kswapd = kthread_create_on_node(kswapd, pgdat, nid, "kswapd%d", nid);
        if (IS_ERR(pgdat->kswapd)) {
            pr_err("Failed to start kswapd on node %d\n", nid);
            BUG_ON(system_state < SYSTEM_RUNNING);
            pgdat->kswapd = NULL;
        } else {
            wake_up_process(pgdat->kswapd);
        }
    }
    pgdat_kswapd_unlock(pgdat);
}
```

### 2.2 kswapd 线程主循环

**kswapd()** (`mm/vmscan.c` 第 7280-7358 行):
```c
static int kswapd(void *p)
{
    unsigned int alloc_order, reclaim_order;
    unsigned int highest_zoneidx = MAX_NR_ZONES - 1;
    pg_data_t *pgdat = (pg_data_t *)p;

    tsk->flags |= PF_MEMALLOC | PF_KSWAPD;

    for (;;) {
        ...
        kswapd_try_to_sleep(pgdat, alloc_order, reclaim_order, highest_zoneidx);
        ...
        reclaim_order = pgdat->kswapd_order;
        highest_zoneidx = kswapd_highest_zoneidx(pgdat, highest_zoneidx);

        if (!try_to_sleep(pgdat, reclaim_order, highest_zoneidx))
            continue;

        balance_pgdat(pgdat, reclaim_order, highest_zoneidx);
    }
}
```

### 2.3 唤醒条件

**wakeup_kswapd()** (`mm/vmscan.c` 第 7361-7404 行):
```c
void wakeup_kswapd(struct zone *zone, gfp_t gfp_flags, int order,
           enum zone_type highest_zoneidx)
{
    pg_data_t *pgdat;

    if (!managed_zone(zone))
        return;

    if (!cpuset_zone_allowed(zone, gfp_flags))
        return;

    pgdat = zone->zone_pgdat;

    // 更新kswapd要处理的最高zone和order
    if (READ_ONCE(pgdat->kswapd_order) < order)
        WRITE_ONCE(pgdat->kswapd_order, order);

    // 检查节点是否"无望"(hopeless)
    if (kswapd_test_hopeless(pgdat) ||
        (pgdat_balanced(pgdat, order, highest_zoneidx) &&
         !pgdat_watermark_boosted(pgdat, highest_zoneidx))) {
        // 如果有足够内存但需要高阶分配，唤醒kcompactd
        if (!(gfp_flags & __GFP_DIRECT_RECLAIM))
            wakeup_kcompactd(pgdat, order, highest_zoneidx);
        return;
    }

    wake_up_interruptible(&pgdat->kswapd_wait);
}
```

**唤醒触发点**:
1. 页面分配器在 `__alloc_pages_slowpath()` (mm/page_alloc.c) 中检测到低水位
2. 显式调用 `wakeup_kswapd()`
3. 页面分配请求无法在当前节点满足时

### 2.4 kswapd 睡眠条件

**prepare_kswapd_sleep()** (mm/page_alloc.c): 检查所有托管zone是否达到高水位

---

## 3. balance_pgdat 和 shrink_node 函数

### 3.1 balance_pgdat - kswapd 主回收逻辑

**balance_pgdat()** (`mm/vmscan.c` 第 6950-7166 行):

这是 kswapd 的主函数，负责平衡节点内存:

```c
static int balance_pgdat(pg_data_t *pgdat, int order, int highest_zoneidx)
{
    struct scan_control sc = {
        .gfp_mask = GFP_KERNEL,
        .order = order,
        .may_unmap = 1,
    };

restart:
    set_reclaim_active(pgdat, highest_zoneidx);
    sc.priority = DEF_PRIORITY;  // 12

    do {
        unsigned long nr_reclaimed = sc.nr_reclaimed;

        sc.reclaim_idx = highest_zoneidx;

        // 检查节点是否已平衡
        balanced = pgdat_balanced(pgdat, sc.order, highest_zoneidx);
        if (!balanced && nr_boost_reclaim)
            goto restart;

        if (!nr_boost_reclaim && balanced)
            goto out;  // 平衡则退出

        // 后台老化，给页面被访问的机会
        kswapd_age_node(pgdat, &sc);

        // 软限制回收
        nr_soft_reclaimed = memcg1_soft_limit_reclaim(...);
        sc.nr_reclaimed += nr_soft_reclaimed;

        // 实际执行回收
        if (kswapd_shrink_node(pgdat, &sc))
            raise_priority = false;

        // 检查优先级是否需要提升
        if (raise_priority || !nr_reclaimed)
            sc.priority--;

    } while (sc.priority >= 1);

out:
    clear_reclaim_active(pgdat, highest_zoneidx);
    return sc.order;
}
```

**关键流程**:
1. 从优先级 12 开始扫描
2. 每次循环扫描 1/2^priority 比例的LRU
3. 调用 `kswapd_shrink_node()` 执行实际回收
4. 如果进度不足，降低优先级继续扫描
5. 最多循环到优先级 0

### 3.2 shrink_node - 节点回收核心

**shrink_node()** (`mm/vmscan.c` 第 6039-6147 行):

```c
static void shrink_node(pg_data_t *pgdat, struct scan_control *sc)
{
    unsigned long nr_reclaimed, nr_scanned, nr_node_reclaimed;
    struct lruvec *target_lruvec;

    if (lru_gen_enabled() && root_reclaim(sc)) {
        lru_gen_shrink_node(pgdat, sc);
        return;
    }

    target_lruvec = mem_cgroup_lruvec(sc->target_mem_cgroup, pgdat);

again:
    memset(&sc->nr, 0, sizeof(sc->nr));
    nr_reclaimed = sc->nr_reclaimed;
    nr_scanned = sc->nr_scanned;

    prepare_scan_control(pgdat, sc);

    // 回收各memcg的LRU
    shrink_node_memcgs(pgdat, sc);

    flush_reclaim_state(sc);
    nr_node_reclaimed = sc->nr_reclaimed - nr_reclaimed;

    // 标记拥塞节点
    if (sc->nr.dirty && sc->nr.dirty == sc->nr.congested) {
        if (cgroup_reclaim(sc))
            set_bit(LRUVEC_CGROUP_CONGESTED, &target_lruvec->flags);
        if (current_is_kswapd())
            set_bit(LRUVEC_NODE_CONGESTED, &target_lruvec->flags);
    }

    // 直接回收时，如果节点拥塞则进行节流
    if (!current_is_kswapd() && current_may_throttle() && ...)
        reclaim_throttle(pgdat, VMSCAN_THROTTLE_CONGESTED);

    // 判断是否需要继续回收
    if (should_continue_reclaim(pgdat, nr_node_reclaimed, sc))
        goto again;
}
```

### 3.3 shrink_zones - 直接回收入口

**shrink_zones()** (`mm/vmscan.c` 第 6221-6311 行):
```c
static void shrink_zones(struct zonelist *zonelist, struct scan_control *sc)
{
    struct zoneref *z;
    struct zone *zone;

    for_each_zone_zonelist_nodemask(zone, z, zonelist,
                    sc->reclaim_idx, sc->nodemask) {
        if (!cgroup_reclaim(sc)) {
            if (!cpuset_zone_allowed(zone, GFP_KERNEL | __GFP_HARDWALL))
                continue;
            // 检查是否需要压缩
            if (IS_ENABLED(CONFIG_COMPACTION) && sc->order > PAGE_ALLOC_COSTLY_ORDER
                && compaction_ready(zone, sc)) {
                sc->compaction_ready = true;
                continue;
            }
        }

        // 执行节点回收
        shrink_node(zone->zone_pgdat, sc);
    }
}
```

---

## 4. shrink_lruvec 和 get_scan_count

### 4.1 shrink_lruvec - LRU向量回收

**shrink_lruvec()** (`mm/vmscan.c` 第 5772-5871 行):

```c
static void shrink_lruvec(struct lruvec *lruvec, struct scan_control *sc)
{
    unsigned long nr[NR_LRU_LISTS];
    unsigned long targets[NR_LRU_LISTS];
    unsigned long nr_to_scan;
    enum lru_list lru;
    unsigned long nr_reclaimed = 0;
    unsigned long nr_to_reclaim = sc->nr_to_reclaim;
    bool proportional_reclaim;
    struct blk_plug plug;

    // Multi-Gen LRU使用独立路径
    if (lru_gen_enabled() && !root_reclaim(sc)) {
        lru_gen_shrink_lruvec(lruvec, sc);
        return;
    }

    // 获取各类LRU的扫描数量
    get_scan_count(lruvec, sc, nr);
    memcpy(targets, nr, sizeof(nr));

    // 判断是否启用比例回收
    proportional_reclaim = (!cgroup_reclaim(sc) && !current_is_kswapd() &&
                    sc->priority == DEF_PRIORITY);

    blk_start_plug(&plug);
    while (nr[LRU_INACTIVE_ANON] || nr[LRU_ACTIVE_FILE] || nr[LRU_INACTIVE_FILE]) {
        for_each_evictable_lru(lru) {
            if (nr[lru]) {
                nr_to_scan = min(nr[lru], SWAP_CLUSTER_MAX);
                nr[lru] -= nr_to_scan;
                nr_reclaimed += shrink_list(lru, nr_to_scan, lruvec, sc);
            }
        }

        cond_resched();

        // 检查是否达到回收目标
        if (nr_reclaimed < nr_to_reclaim || proportional_reclaim)
            continue;

        // 比例调整：当一种LRU扫描完时，减少另一种的扫描量
        ...
    }
    blk_finish_plug(&plug);
}
```

### 4.2 get_scan_count - 决定扫描数量

**get_scan_count()** (`mm/vmscan.c` 第 2527-2641 行):

```c
static void get_scan_count(struct lruvec *lruvec, struct scan_control *sc,
               unsigned long *nr)
{
    struct pglist_data *pgdat = lruvec_pgdat(lruvec);
    struct mem_cgroup *memcg = lruvec_memcg(lruvec);
    int swappiness = sc_swappiness(sc, memcg);
    u64 fraction[ANON_AND_FILE];
    u64 denominator = 0;
    enum scan_balance scan_balance;

    // 没有swap空间，只扫描文件页
    if (!sc->may_swap || !can_reclaim_anon_pages(memcg, pgdat->node_id, sc)) {
        scan_balance = SCAN_FILE;
        goto out;
    }

    // 严重OOM时，两者等量扫描
    if (!sc->priority && swappiness) {
        scan_balance = SCAN_EQUAL;
        goto out;
    }

    // 文件页过少，强制扫描匿名页
    if (sc->file_is_tiny) {
        scan_balance = SCAN_ANON;
        goto out;
    }

    // 缓存调整模式，只扫描文件
    if (sc->cache_trim_mode) {
        scan_balance = SCAN_FILE;
        goto out;
    }

    // 正常情况：按比例计算
    scan_balance = SCAN_FRACT;
    calculate_pressure_balance(sc, swappiness, fraction, &denominator);

out:
    for_each_evictable_lru(lru) {
        bool file = is_file_lru(lru);
        unsigned long lruvec_size;
        unsigned long scan;

        lruvec_size = lruvec_lru_size(lruvec, lru, sc->reclaim_idx);
        scan = apply_proportional_protection(memcg, sc, lruvec_size);
        scan >>= sc->priority;  // 按优先级缩放

        switch (scan_balance) {
        case SCAN_EQUAL:
            break;
        case SCAN_FRACT:
            // 按swappiness比例分配
            scan = div64_u64(scan * fraction[file], denominator);
            break;
        case SCAN_FILE:
        case SCAN_ANON:
            if ((scan_balance == SCAN_FILE) != file)
                scan = 0;
            break;
        }
        nr[lru] = scan;
    }
}
```

### 4.3 shrink_list - 实际列表回收

**shrink_list()** (`mm/vmscan.c` 第 2249-2261 行):
```c
static unsigned long shrink_list(enum lru_list lru, unsigned long nr_to_scan,
                 struct lruvec *lruvec, struct scan_control *sc)
{
    // 活跃列表：尝试降级或保持
    if (is_active_lru(lru)) {
        if (sc->may_deactivate & (1 << is_file_lru(lru)))
            shrink_active_list(nr_to_scan, lruvec, sc, lru);
        else
            sc->skipped_deactivate = 1;
        return 0;
    }

    // 非活跃列表：实际回收
    return shrink_inactive_list(nr_to_scan, lruvec, sc, lru);
}
```

---

## 5. shrink_folio_list 页面回收决策

### 5.1 函数签名

**shrink_folio_list()** (`mm/vmscan.c` 第 1083-1082 行):
```c
static unsigned int shrink_folio_list(struct list_head *folio_list,
        struct pglist_data *pgdat, struct scan_control *sc,
        struct reclaim_stat *stat, bool ignore_references,
        struct mem_cgroup *memcg)
```

### 5.2 回收决策流程

```
入口
  |
  v
folio_trylock(folio) --> [失败]--> keep
  |
  v
folio_evictable(folio)? --> [否]--> activate_locked
  |
  v
sc->may_unmap && folio_mapped(folio) --> [不可unmap且已映射]--> keep_locked
  |
  v
folio_test_writeback(folio)? --> [是]--> 等待写回或激活
  |
  v
folio_check_references(folio, sc) --> [引用检查]
  |                              |
  +--> FOLIOREF_ACTIVATE -----> activate_locked
  +--> FOLIOREF_KEEP ---------> keep_locked
  +--> FOLIOREF_RECLAIM -----> 尝试回收
  +--> FOLIOREF_RECLAIM_CLEAN-> 尝试回收
  |
  v
[匿名页] --> folio_test_swapbacked?
  |
  +--> [有swap] --> 分配swap空间
  +--> [无swap] --> 尝试demote或激活
  |
  v
[文件页] --> 尝试写回或直接回收
  |
  v
释放页面 --> free_folios
```

### 5.3 关键决策点

** folio_check_references()** (`mm/vmscan.c` 第 883-951 行):
```c
static enum folio_references folio_check_references(struct folio *folio,
                          struct scan_control *sc)
{
    int referenced_ptes, referenced_folio;
    vm_flags_t vm_flags;

    referenced_ptes = folio_referenced(folio, 1, sc->target_mem_cgroup, &vm_flags);

    // VM_LOCKED页面移到不可回收列表
    if (vm_flags & VM_LOCKED)
        return FOLIOREF_ACTIVATE;

    // rmap锁争用
    if (referenced_ptes == -1)
        return FOLIOREF_KEEP;

    // Multi-Gen LRU
    if (lru_gen_enabled()) {
        if (!referenced_ptes)
            return FOLIOREF_RECLAIM;
        return lru_gen_set_refs(folio) ? FOLIOREF_ACTIVATE : FOLIOREF_KEEP;
    }

    referenced_folio = folio_test_clear_referenced(folio);

    if (referenced_ptes) {
        // 清除引用位后，如果页面被映射多次或已有引用标记，则激活
        folio_set_referenced(folio);
        if (referenced_folio || referenced_ptes > 1)
            return FOLIOREF_ACTIVATE;

        // 可执行文件页首次访问即激活
        if ((vm_flags & VM_EXEC) && folio_is_file_lru(folio))
            return FOLIOREF_ACTIVATE;

        return FOLIOREF_KEEP;
    }

    // 干净的文件页可回收
    if (referenced_folio && folio_is_file_lru(folio))
        return FOLIOREF_RECLAIM_CLEAN;

    return FOLIOREF_RECLAIM;
}
```

### 5.4 回流判断 (Writeback)

**folio_check_dirty_writeback()** (`mm/vmscan.c` 第 953-984 行):
- 检查页面的 `PG_dirty` 和 `PG_writeback` 标志
- 如果是匿名页或非swapbacked的匿名页，忽略dirty/writeback状态
- 文件页的dirty/writeback状态由文件系统验证

---

## 6. folio_check_references 引用检查

### 6.1 引用来源

页面引用来自两个途径:

1. **Page Table引用** (`referenced_ptes`):
   - 通过页表的访问
   - 由 `folio_referenced()` 检查页表项中的 accessed bit

2. **Page引用位** (`referenced_folio`):
   - 页面自身的 `PG_referenced` 标志
   - 由 `folio_test_clear_referenced()` 清除并返回原值

### 6.2 Multi-Gen LRU的引用处理

当 `lru_gen_enabled()` 时:
```c
if (lru_gen_enabled()) {
    if (!referenced_ptes)
        return FOLIOREF_RECLAIM;
    return lru_gen_set_refs(folio) ? FOLIOREF_ACTIVATE : FOLIOREF_KEEP;
}
```

### 6.3 传统LRU的引用处理

**引用决策表**:

| referenced_ptes | referenced_folio | VM_EXEC | 文件页? | 返回值 |
|-----------------|-----------------|---------|---------|--------|
| >1               | -               | -       | -       | ACTIVATE |
| 1                | true            | -       | -       | ACTIVATE |
| 1                | false           | true    | file    | ACTIVATE |
| 1                | false           | -       | -       | KEEP |
| 0                | true            | -       | file    | RECLAIM_CLEAN |
| 0                | -               | -       | -       | RECLAIM |

---

## 7. 直接回收 (Direct Reclaim) vs kswapd

### 7.1 触发路径对比

| 特性 | 直接回收 | kswapd |
|------|---------|--------|
| 触发方式 | 页面分配器在`__alloc_pages_slowpath()`中调用 | 内存压力导致`wakeup_kswapd()`唤醒 |
| 调用栈 | `try_to_free_pages()` -> `shrink_zones()` | `balance_pgdat()` -> `kswapd_shrink_node()` |
| 运行上下文 | 进程上下文（可能睡眠） | 内核线程（kswapd进程） |
| 扫描优先级 | 从当前优先级递减 | 从DEF_PRIORITY(12)开始递减 |
| 内存分配标志 | `GFP_KERNEL \| __GFP_DIRECT_RECLAIM` | `GFP_KERNEL` |
| 回收上限 | 达到`nr_to_reclaim`后停止 | 达到高水位后停止 |

### 7.2 直接回收入口

**do_try_to_free_pages()** (`mm/vmscan.c` 第 6344-6439 行):
```c
static unsigned long do_try_to_free_pages(struct zonelist *zonelist,
                      struct scan_control *sc)
{
    int initial_priority = sc->priority;

retry:
    delayacct_freepages_start();

    do {
        vmpressure_prio(sc->gfp_mask, sc->target_mem_cgroup, sc->priority);
        sc->nr_scanned = 0;
        shrink_zones(zonelist, sc);

        if (sc->nr_reclaimed >= sc->nr_to_reclaim)
            break;

        if (sc->compaction_ready)
            break;
    } while (--sc->priority >= 0);

    delayacct_freepages_end();

    // 首次遍历后仍无进展，尝试完整遍历
    if (!sc->memcg_full_walk) {
        sc->priority = initial_priority;
        sc->memcg_full_walk = 1;
        goto retry;
    }

    // 尝试强制降级
    if (sc->skipped_deactivate) {
        sc->priority = initial_priority;
        sc->force_deactivate = 1;
        sc->skipped_deactivate = 0;
        goto retry;
    }

    // 尝试突破memcg保护
    if (sc->memcg_low_skipped) {
        sc->priority = initial_priority;
        sc->memcg_low_reclaim = 1;
        sc->memcg_low_skipped = 0;
        goto retry;
    }

    return sc->nr_reclaimed;
}
```

### 7.3 主要区别

1. **优先级衰减**:
   - 直接回收：可能从用户指定优先级开始
   - kswapd：始终从DEF_PRIORITY(12)开始

2. **进度追踪**:
   - kswapd：使用 `pgdat->kswapd_failures` 追踪连续失败
   - 直接回收：使用 `sc->nr_reclaimed >= sc->nr_to_reclaim` 判断成功

3. **节流处理**:
   - 直接回收：在 `reclaim_throttle()` 中等待
   - kswapd：不会节流，继续尝试

4. **memcg遍历**:
   - 直接回收：支持部分遍历（`partial`）和完整遍历（`full_walk`）
   - kswapd：始终完整遍历

---

## 8. Multi-Gen LRU 机制

### 8.1 设计目标

Multi-Gen LRU (`CONFIG_LRU_GEN`) 旨在解决传统LRU的几个问题:
1. 扫描整个LRU寻找冷页面导致的缓存污染
2. 无法利用历史的refault信息做决策
3. 页面在活跃/非活跃间的硬切换

### 8.2 核心数据结构

**struct lru_gen_folio** (见第1.4节)

**代数(Generation)管理**:
```c
// 增加代数序号
max_seq++: 新页面加入最新代数

// 回收最老代数
min_seq[type]++: 标记最老代为可回收
```

### 8.3 页面代数计算

**lru_gen_folio_seq()** (`include/linux/mm_inline.h` 第 220-252 行):
```c
static inline unsigned long lru_gen_folio_seq(const struct lruvec *lruvec,
                          const struct folio *folio,
                          bool reclaiming)
{
    int gen;
    int type = folio_is_file_lru(folio);
    const struct lru_gen_folio *lrugen = &lruvec->lrugen;

    if (folio_test_active(folio))
        gen = MIN_NR_GENS - folio_test_workingset(folio);
    else if (reclaiming)
        gen = MAX_NR_GENS;
    else if ((!folio_is_file_lru(folio) && !folio_test_swapcache(folio)) ||
         (folio_test_reclaim(folio) &&
          (folio_test_dirty(folio) || folio_test_writeback(folio))))
        gen = MIN_NR_GENS;
    else
        gen = MAX_NR_GENS - folio_test_workingset(folio);

    return max(READ_ONCE(lrugen->max_seq) - gen + 1,
           READ_ONCE(lrugen->min_seq[type]));
}
```

### 8.4 回收流程

**lru_gen_shrink_node()** (`mm/vmscan.c` 第 5038-5078 行):
```c
static void lru_gen_shrink_node(struct pglist_data *pgdat, struct scan_control *sc)
{
    ...
    lru_add_drain();
    blk_start_plug(&plug);

    set_mm_walk(pgdat, sc->proactive);
    set_initial_priority(pgdat, sc);

    if (current_is_kswapd())
        sc->nr_reclaimed = 0;

    if (mem_cgroup_disabled())
        shrink_one(&pgdat->__lruvec, sc);
    else
        shrink_many(pgdat, sc);

    if (current_is_kswapd())
        sc->nr_reclaimed += reclaimed;

    clear_mm_walk();
    blk_finish_plug(&plug);
}
```

### 8.5 Aging (老化)

**lru_gen_age_node()** (`mm/vmscan.c` 第 4154-4188 行):
```c
static void lru_gen_age_node(struct pglist_data *pgdat, struct scan_control *sc)
{
    unsigned long min_ttl = READ_ONCE(lru_gen_min_ttl);
    bool reclaimable = !min_ttl;

    set_initial_priority(pgdat, sc);

    memcg = mem_cgroup_iter(NULL, NULL, NULL);
    do {
        struct lruvec *lruvec = mem_cgroup_lruvec(memcg, pgdat);
        mem_cgroup_calculate_protection(NULL, memcg);

        if (!reclaimable)
            reclaimable = lruvec_is_reclaimable(lruvec, sc, min_ttl);
    } while ((memcg = mem_cgroup_iter(NULL, memcg, NULL)));

    // 如果所有代数都年轻于min_ttl，触发OOM
    if (!reclaimable && mutex_trylock(&oom_lock)) {
        struct oom_control oc = { .gfp_mask = sc->gfp_mask, };
        out_of_memory(&oc);
        mutex_unlock(&oom_lock);
    }
}
```

### 8.6 rmap反馈

**lru_gen_look_around()** (`mm/vmscan.c` 第 4201-4252 行):
- 当回收扫描一个页面时，检查相邻PTE
- 热点页面被提升(Promotion)到更年轻的代数
- 高效扫描时，将PMD条目加入Bloom过滤器

### 8.7 Tier机制

页面按访问次数分为多个tier:
- `MAX_NR_TIERS = 4`
- Tier 0: N=0,1 (首次/第二次访问)
- Tier MAX_NR_TIERS-1: MAX (PG_workingset)

```c
static inline int lru_tier_from_refs(int refs, bool workingset)
{
    return workingset ? MAX_NR_TIERS - 1 : order_base_2(refs);
}
```

---

## 关键函数调用图

```
页面分配失败
    |
    v
wakeup_kswapd() [kswapd被唤醒]
    |
    v                    直接回收路径
kswapd()                 |
    |                 try_to_free_pages()
    v                    |
balance_pgdat() -----> shrink_zones()
    |                    |
    v                    v
kswapd_shrink_node()  shrink_node()
    |                    |
    v                    v
shrink_node_memcgs() ---> shrink_node_memcgs()
    |                    |
    v                    v
shrink_lruvec() --------> shrink_lruvec()
    |                    |
    +--> get_scan_count() (计算anon/file扫描比例)
    |
    v
shrink_list() ---> [is_active_lru?]
    |                    |
    +--> [是]----> shrink_active_list()
    |
    +--> [否]----> shrink_inactive_list()
                           |
                           v
                    shrink_folio_list()
                           |
                           +--> folio_check_references()
                           |
                           +--> [回收决策]
```

---

## 源码位置汇总

| 函数/结构 | 文件 | 行号 |
|----------|------|------|
| enum lru_list | include/linux/mmzone.h | 316-323 |
| struct lruvec | include/linux/mmzone.h | 669-698 |
| struct lru_gen_folio | include/linux/mmzone.h | 490-518 |
| folio_lru_list() | include/linux/mm_inline.h | 87-101 |
| folio_is_file_lru() | include/linux/mm_inline.h | 28-31 |
| wakeup_kswapd() | mm/vmscan.c | 7361-7404 |
| kswapd() | mm/vmscan.c | 7280-7358 |
| balance_pgdat() | mm/vmscan.c | 6950-7166 |
| shrink_node() | mm/vmscan.c | 6039-6147 |
| shrink_zones() | mm/vmscan.c | 6221-6311 |
| shrink_lruvec() | mm/vmscan.c | 5772-5871 |
| get_scan_count() | mm/vmscan.c | 2527-2641 |
| shrink_list() | mm/vmscan.c | 2249-2261 |
| shrink_folio_list() | mm/vmscan.c | 1083-1082+ |
| folio_check_references() | mm/vmscan.c | 883-951 |
| do_try_to_free_pages() | mm/vmscan.c | 6344-6439 |
| lru_gen_shrink_node() | mm/vmscan.c | 5038-5078 |
| lru_gen_age_node() | mm/vmscan.c | 4154-4188 |
| lru_gen_look_around() | mm/vmscan.c | 4201-4252 |
