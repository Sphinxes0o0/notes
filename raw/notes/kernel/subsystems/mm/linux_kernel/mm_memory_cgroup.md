# MM Memory Cgroup

## 1. mem_cgroup 结构

### 1.1 struct mem_cgroup
**文件**: `mm/memcontrol.h:600-800`

```c
struct mem_cgroup {
    struct cgroup_subsys_state css;
    struct mem_cgroup_lruvec __lruvec;
    struct lruvec_stat __lruvec_stat;
    atomic_long_t memory_events_local[VM_EVENTS_MAX];
    unsigned long flags;

    /* 内存限制 */
    struct memory_limit {
        atomic64_t usage;
        atomic64_t soft_limit;
        u64 high;
        u64 max;
        u64 oom;
    } memory;

    /* Swap 限制 */
    struct memory_limit swap;

    /* 统计信息 */
    struct memcg_memory_data __memcg_data;
    struct lru_gen_folio *lrugen;

    /* 层级结构 */
    struct list_head children;
    struct mem_cgroup *parent;

    /* OOM 相关 */
    wait_queue_head_t oom_waitq;
    struct oom_control oom;
};
```

### 1.2 memory_stat 统计
**文件**: `mm/memcontrol.c:2000-2100`

```c
enum memcg_memory_event {
    MEMCG_LOW,
    MEMCG_HIGH,
    MEMCG_MAX,
    MEMCG_OOM,
    MEMCG_SWAP_HIGH,
    MEMCG_SWAP_MAX,
    MEMCG_SWAP_OOM,
};

enum memcg_stat_item {
    MEMCG_CACHE,
    MEMCG_RSS,
    MEMCG_RSS_HUGE,
    MEMCG_SHMEM,
    MEMCG_SHMEM_HUGE,
    MEMCG_FILE,
    MEMCG_FILE_HUGE,
    MEMCG_PGPGIN,
    MEMCG_PGPGOUT,
    MEMCG_PGFAULT,
    MEMCG_PGMAJFAULT,
    // ...
};
```

## 2. 内存计费

### 2.1 mem_cgroup_charge
**文件**: `mm/memcontrol.c:3500-3600`

```c
int mem_cgroup_charge(struct folio *folio, struct mm_struct *mm,
                      gfp_t gfp)
{
    struct mem_cgroup *memcg;
    int ret;

    memcg = get_mem_cgroup_from_mm(mm);
    if (memcg == root_mem_cgroup)
        return 0;

    ret = try_charge(memcg, gfp, folio_nr_pages(folio));
    if (ret)
        return ret;

    // 设置 folio->memcg_data
    folio->memcg_data = (unsigned long)memcg;

    return 0;
}
```

### 2.2 try_charge
**文件**: `mm/memcontrol.c:3200-3350`

```c
int try_charge(struct mem_cgroup *memcg, gfp_t gfp_mask,
                unsigned int nr_pages)
{
    unsigned int batch = MGC_CHARGE_BATCH;
    struct mem_cgroup *memcg_over_se;
    bool maybe_oom;
    int ret;

    // 检查是否超过 high 限制
    if (consume_charge(memcg, nr_pages))
        return 0;

    // 超过限制，尝试回收
    ret = reclaim_charge(memcg, gfp_mask, nr_pages);
    if (ret == 0)
        return 0;

    // 回收失败，可能 OOM
    maybe_oom = !memcg->oom_lock.waiters;

    if (memcg->memory.max == PAGE_COUNTER_MAX)
        goto force_retry;

    // 检查 high 限制
    if (consume_charge(memcg, nr_pages))
        return 0;

    // 触发 memory.high 事件
    memcg_memory_event(memcg, MEMCG_HIGH);

force_retry:
    if (maybe_oom) {
        // 唤醒 OOM killer
        mem_cgroup_oom(memcg, gfp_mask, 0);
    }

    return -ENOMEM;
}
```

## 3. 内存回收

### 3.1 memcg_reclaim
**文件**: `mm/vmscan.c:5500-5600`

```c
static int memcg_reclaim(struct mem_cgroup *memcg, int nr_to_reclaim,
                         unsigned long *nr_reclaimed)
{
    struct scan_control sc = {
        .nr_to_reclaim = nr_to_reclaim,
        .gfp_mask = GFP_KERNEL,
        .may_writepage = 1,
        .may_unmap = 1,
        .may_swap = 1,
        .target_mem_cgroup = memcg,
    };

    return try_to_free_mem_cgroup_pages(memcg, &sc, nr_reclaimed);
}
```

### 3.2 try_to_free_mem_cgroup_pages
**文件**: `mm/vmscan.c:5450-5500`

```c
int try_to_free_mem_cgroup_pages(struct mem_cgroup *memcg,
                                 struct scan_control *sc,
                                 unsigned long *nr_reclaimed)
{
    struct zonelist *zonelist = &NODE_DATA(numa_node_id())->node_zonelists[ZONELIST_FALLBACK];

    sc->nr_reclaimed = 0;

    // 执行回收
    do {
        shrink_node_memcgs(zonelist, sc);
    } while (sc->nr_reclaimed < sc->nr_to_reclaim &&
             sc->priority >= 0);

    *nr_reclaimed = sc->nr_reclaimed;
    return sc->nr_reclaimed >= sc->nr_to_reclaim ? 0 : -EAGAIN;
}
```

## 4. Memory Pressure

### 4.1 memory_pressure_handle
**文件**: `mm/memcontrol.c:4000-4100`

```c
static void memory_pressure_handle(struct mem_cgroup *memcg)
{
    u64 current, min, low;
    u64 pressure;

    // 计算内存压力
    current = atomic64_read(&memcg->memory.usage);
    min = atomic64_read(&memcg->memory.min);
    low = atomic64_read(&memcg->memory.soft_limit);

    if (current < low)
        return;

    // 计算压力百分比
    if (low > min)
        pressure = (current - min) * 100 / (low - min);
    else
        pressure = 100;

    // 通知用户空间
    cgroup_file_notify(&memcg->events_local[MEMCG_LOW]);
}
```

### 4.2 cgroup 压力通知
**文件**: `kernel/cgroup/cgroup-util.c`

cgroup v2 的 memory.pressure 接口通过 cgroup 事件机制实现。

## 5. OOM 处理

### 5.1 mem_cgroup_oom
**文件**: `mm/memcontrol.c:1706-1723`

```c
static bool mem_cgroup_oom(struct mem_cgroup *memcg, gfp_t mask, int order)
{
    if (order > PAGE_ALLOC_COSTLY_ORDER)
        return false;

    memcg_memory_event(memcg, MEMCG_OOM);

    if (!memcg1_oom_prepare(memcg, &locked))
        return false;

    ret = mem_cgroup_out_of_memory(memcg, mask, order);

    memcg1_oom_finish(memcg, locked);

    return ret;
}
```

### 5.2 mem_cgroup_out_of_memory
**文件**: `mm/memcontrol.c:1673-1700`

```c
static bool mem_cgroup_out_of_memory(struct mem_cgroup *memcg,
                                     gfp_t gfp_mask, int order)
{
    struct oom_control oc = {
        .zonelist = NULL,
        .nodemask = NULL,
        .memcg = memcg,
        .gfp_mask = gfp_mask,
        .order = order,
    };
    bool ret = true;

    if (mutex_lock_killable(&oom_lock))
        return true;

    // 检查 margin
    if (mem_cgroup_margin(memcg) >= (1 << order))
        goto unlock;

    ret = out_of_memory(&oc);

unlock:
    mutex_unlock(&oom_lock);
    return ret;
}
```

## 6. 软限制回收

### 6.1 memcg1_soft_limit_reclaim
**文件**: `mm/vmscan.c:5700-5800`

```c
unsigned long memcg1_soft_limit_reclaim(struct mem_cgroup *memcg,
                                        int priority, unsigned long *nr_scanned)
{
    unsigned long nr_reclaimed = 0;
    unsigned long try_age = 1;
    unsigned long max_size;

    // 获取软限制
    max_size = atomic64_read(&memcg->memory.soft_limit);

    // 如果当前使用量小于软限制，不需要回收
    if (atomic64_read(&memcg->memory.usage) < max_size)
        return 0;

    // 扫描 LRU 进行回收
    while (nr_reclaimed < try_age) {
        // 回收操作
        // ...
    }

    return nr_reclaimed;
}
```

## 7. 层级限制继承

```c
// 子 cgroup 继承父 cgroup 的限制
static void memcg_update_limits(struct mem_cgroup *memcg)
{
    struct mem_cgroup *parent = memcg->parent;

    if (parent) {
        // 子 cgroup 的 max 不能超过父
        if (memcg->memory.max > parent->memory.max)
            memcg->memory.max = parent->memory.max;

        // 子 cgroup 的 soft_limit 不能超过 max
        if (memcg->memory.soft_limit > memcg->memory.max)
            memcg->memory.soft_limit = memcg->memory.max;
    }
}
```

## 8. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| mem_cgroup_charge | mm/memcontrol.c | 3500 |
| try_charge | mm/memcontrol.c | 3200 |
| memcg_reclaim | mm/vmscan.c | 5500 |
| try_to_free_mem_cgroup_pages | mm/vmscan.c | 5450 |
| mem_cgroup_oom | mm/memcontrol.c | 1706 |
| mem_cgroup_out_of_memory | mm/memcontrol.c | 1673 |
| memcg1_soft_limit_reclaim | mm/vmscan.c | 5700 |
