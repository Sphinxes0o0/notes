# Linux SLUB 分配器深度源码分析 (第二轮)

## 深入 Buddy 系统核心算法

### 1.1 Buddy 合并算法的数学证明

Buddy 系统的核心是**地址对齐合并**。让我们分析合并条件：

```c
/*
 * 合并条件：
 * 1. 两个页面是相邻的 (pfn + (1 << order) == buddy_pfn)
 * 2. 伙伴页面也是自由的 (PageBuddy(buddy))
 * 3. 伙伴的阶数相同 (buddy_order == order)
 * 4. 迁移类型兼容
 */
static inline void __free_one_page(struct page *page,
        unsigned long pfn, struct zone *zone, unsigned int order,
        int migratetype, fpi_t fpi_flags)
{
    unsigned long buddy_pfn;
    struct page *buddy;

    while (order < MAX_PAGE_ORDER) {
        /* 计算伙伴页面地址 */
        buddy_pfn = __find_buddy_pfn(pfn, order);
        buddy = page + (buddy_pfn - pfn);

        /* 伙伴阶数必须相同 */
        VM_BUG_ON_PAGE(buddy_order(buddy) != order, buddy);

        /* 检查是否可以合并 */
        if (!page_is_guard(buddy) &&
            buddy_migratetype(buddy) == migratetype &&
            PageBuddy(buddy)) {
            /* 合并：删除伙伴，加入到更高阶链表 */
            __del_page_from_free_list(buddy, zone, order, migratetype);
            combined_pfn = buddy_pfn & pfn;
            page = page + (combined_pfn - pfn);
            pfn = combined_pfn;
            order++;
        } else {
            break;
        }
    }
}
```

**数学性质：**
```
给定页面 pfn = 0x1000 (4KB aligned), order = 0 (1页)

伙伴计算: buddy_pfn = pfn ^ (1 << order)
         = 0x1000 ^ 0x1 = 0x1001 (相邻页面)

当 order = 1 (2页):
buddy_pfn = 0x1000 ^ 0x2 = 0x1002
页面 0x1000-0x1001 的伙伴是 0x1002-0x1003

递归合并形成二叉树结构：
        [0x0000 - 0x7FFF] (order 15)
           /              \
    [0x0000-0x3FFF]    [0x4000-0x7FFF] (order 14)
        /      \            /      \
    ...        ...        ...        ...
```

### 1.2 Buddy 分配算法的反向追踪

```c
/*
 * __rmqueue 核心分配函数
 * 关键点：从高阶到低阶遍历，寻找最佳匹配
 */
static __always_inline struct page *
__rmqueue(struct zone *zone, unsigned int order, int migratetype,
          unsigned int alloc_flags)
{
    struct page *page;

retry:
    /* 1. 尝试从 requested order 开始分配 */
    for (current_order = order; current_order < MAX_PAGE_ORDER; current_order++) {
        area = &zone->free_area[current_order];

        /* 2. 查找匹配的空闲页面 */
        page = list_first_entry_or_null(
            &area->free_list[migratetype],
            struct page, buddy_list);

        if (page) {
            /* 找到！删除并可能分割 */
            list_del(&page->buddy_list);
            area->nr_free--;

            /* 3. 如果需要分割（从更高阶获取） */
            if (current_order != order)
                page = split_free_page(page, current_order - order, order);

            if (page)
                return page;
        }
    }

    /* 4. 回退到其他迁移类型 */
    if (fallback_migratetype != migratetype) {
        migratetype = fallback_migratetype;
        goto retry;
    }

    return NULL;
}
```

**Expand 算法（分割高阶页面）:**
```
分配 order=2 (4页) 但只有 order=4 (16页)：

初始: [0x0000-0x000F] (16页, order=4)

Step 1: 分割为两个 order=3 (8页)
  [0x0000-0x0007] [0x0008-0x000F]

Step 2: 取第一个 order=3, 分割为两个 order=2 (4页)
  [0x0000-0x0003] [0x0004-0x0007] [0x0008-0x000F]

Step 3: 取第一个 order=2, 分割为两个 order=1 (2页)
  [0x0000-0x0001] [0x0002-0x0003] [0x0004-0x0007] [0x0008-0x000F]

Step 4: 取第一个 order=1, 分割为两个 order=0 (1页)
  [0x0000] [0x0001] [0x0002-0x0003] [0x0004-0x0007] [0x0008-0x000F]

最终分配: 0x0000 (4页)
剩余: 0x0001 (1页), 0x0002-0x0003 (2页), 0x0004-0x0007 (4页), 0x0008-0x000F (8页)
```

---

## 深入 SLUB 分配器核心机制

### 2.1 Sheaf 机制的本质

SLUB 的 sheaf 是 per-CPU 的对象缓存，替代了早期 SLAB 的 per-CPU array。

```c
/*
 * Sheaf 是 SLUB 的核心创新
 * 每个 CPU 有两个 sheaf: main 和 spare
 */
struct slub_percpu_sheaves {
    local_lock_t lock;  // 仅禁用抢占，不使用原子操作
    struct slab_sheaf {
        void **freelist;           // 空闲对象链表
        unsigned long counters;     // 计数器 (inuse, objects, frozen)
    } main, spare;
};
```

**为什么使用 cmpxchg 而不是锁：**

```c
/*
 * __cmpxchg_double 是 SLUB 的核心原子操作
 * 它同时原子地更新 freelist 和 counters
 *
 * 原理：freelist 和 counters 在内存中必须连续且对齐
 * x86_64: cmpxchg16b 支持 16 字节双操作数原子比较交换
 */
static inline bool __cmpxchg_double_slab(struct slab *slab,
        void **freelist_old, unsigned long counters_old,
        void **freelist_new, unsigned long counters_new,
        const char *n)
{
    bool ret;

    asm volatile(LOCK_PREFIX "cmpxchg16b %2\n\t"
        "setz %1"
        : "=a" (freelist_old), "=q" (ret), "+m" (slab->freelist),
          "+m" (slab->counters)
        : "b" (freelist_new), "c" (counters_new),
          "a" (freelist_old), "d" (counters_old));

    return ret;
}
```

### 2.2 分配快速路径的完整实现

```c
/*
 * kmem_cache_alloc - SLUB 快速路径
 *
 * 优化流程:
 * 1. 检查 sheaf 是否有空间
 * 2. 使用 cmpxchg 原子获取对象
 * 3. 失败则尝试 refill
 * 4. 最后回退到 barn
 */
static __always_inline void *
__kmem_cache_alloc_node(struct kmem_cache *s, gfp_t gfpflags, int node)
{
    void *ret;

    if (likely(cache_has_sheaves(s))) {
        struct slub_percpu_sheaf *pcss = this_cpu_ptr(s->cpu_sheaves);
        struct slab_sheaf *sheaf = &pcss->main;

        /* 快速路径：直接从 sheaf 分配 */
        ret = __kmem_cache_alloc_from_sheaf(s, sheaf, gfpflags);
        if (likely(ret))
            return ret;

        /* sheaf 耗尽，交换并重新填充 */
        if (try_fill_main(pcss, s, gfpflags))
            return __kmem_cache_alloc_from_sheaf(s, &pcss->main, gfpflags);

        /* 尝试从 spare 获取 */
        if (pcss->spare) {
            swap(pcss->main, pcss->spare);
            ret = __kmem_cache_alloc_from_sheaf(s, &pcss->main, gfpflags);
            if (likely(ret))
                return ret;
        }

        /* 最后回退：从 barn 获取 */
        return __kmem_cache_alloc_from_barn(s, gfpflags);
    }

    /* 无 sheaf 的缓存：回退到慢路径 */
    return slab_alloc(s, gfpflags, _RET_IP_);
}
```

### 2.3 cmpxchg 双操作的核心价值

```c
/*
 * Slab 布局 - 关键是对齐和连续性
 *
 * struct slab {
 *     memdesc_flags_t flags;
 *     struct kmem_cache *slab_cache;
 *     union {
 *         struct {
 *             struct list_head slab_list;
 *             void *freelist;           <-- 8 bytes
 *             union {
 *                 unsigned long counters;  <-- 8 bytes
 *                 struct {            <-- 两个 8 字节必须连续！
 *                     unsigned inuse:16;
 *                     unsigned objects:15;
 *                     unsigned frozen:1;
 *                 };
 *             };
 *         };
 *     };
 * };
 *
 * freelist (8字节) + counters (8字节) = 16字节 = cmpxchg16b 操作数大小
 */
```

### 2.4 分配器状态机

```
┌────────────────────────────────────────────────────────────────┐
│                 SLUB Object Allocation State Machine                │
│                                                                   │
│   [Start]                                                        │
│      │                                                           │
│      ▼                                                           │
│   ┌─────────────────┐                                           │
│   │ Check Sheaf     │──── Has Objects? ────► [Return Object]      │
│   │ (main)         │      Yes                                   │
│   └────────┬────────┘                                           │
│            │ No                                                 │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ Try Refill Main │──── Success? ─────► [Retry Sheaf]         │
│   └────────┬────────┘      Yes                                   │
│            │ No                                                 │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ Swap Main/Spare │──── Spare exists? ──► [Try Alloc]         │
│   └────────┬────────┘      Yes                                   │
│            │ No                                                 │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ Get from Barn   │──── Success? ─────► [Return Object]        │
│   │ (slow path)    │      Yes                                   │
│   └────────┬────────┘                                           │
│            │ No                                                 │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ Allocate New    │──── Success? ─────► [Init & Return]        │
│   │ Slab           │      Yes                                   │
│   └────────┬────────┘                                           │
│            │ No                                                 │
│            ▼                                                    │
│       [Return NULL / OOM]                                       │
└────────────────────────────────────────────────────────────────┘
```

---

## 深入内存回收 (VMSCAN) 算法

### 3.1 LRU 列表结构与 pagevec

```c
/*
 * Per-CPU LRU 页面向量
 * 用于批量回收，减少锁竞争
 */
struct pagevec {
    unsigned long nr;          // 当前页面数
    unsigned long cold;        // 冷/热页面
    struct page *pages[PAGEVEC_SIZE];  // 页面指针数组
};

/*
 * LRU 列表定义
 * 关键洞察：anon 和 file 分离实现更好的回收策略
 */
enum lru_list {
    LRU_INACTIVE_ANON = 0,    // 非活跃匿名页面
    LRU_ACTIVE_ANON,          // 活跃匿名页面
    LRU_INACTIVE_FILE,        // 非活跃文件页面
    LRU_ACTIVE_FILE,          // 活跃文件页面
    LRU_UNEVICTABLE,          // 不可驱逐页面 (mlocked)
    NR_LRU_LISTS
};
```

### 3.2 folio 冻结 ( folio_batch )

```c
/*
 * folio_batch - 批量处理 folio
 * 减少函数调用开销，提高缓存命中率
 */
struct folio_batch {
    unsigned long nr;          // 当前 folio 数
    unsigned long expire;      // 批次过期时间
    struct folio *folios[];
};

/*
 * 典型批量回收流程
 * 1. 从 LRU 批量获取页面
 * 2. 尝试批量映射/解映射
 * 3. 批量写回
 * 4. 批量释放
 */
static unsigned int shrink_folio_list(struct folio_batch *folio_list,
                                     struct scan_control *sc)
{
    LIST_HEAD(ret_folios);
    unsigned int nr_reclaimed = 0;

    for (folio_batch_init(&fb); fb.nr; folio_batch_clear(&fb)) {
        struct folio *folio = fb.folios[i];

        /* 锁定 folio */
        if (!folio_trylock(folio))
            continue;

        /* 检查是否可回收 */
        if (folio_test_dirty(folio) && folio_mapping(folio)) {
            /* 尝试写回 */
            folio_unlock(folio);
            continue;
        }

        /* 从 LRU 移除 */
        if (folio_isolate_lru(folio)) {
            nr_reclaimed += folio_put_back_lru(folio);
        } else {
            folio_unlock(folio);
        }
    }

    return nr_reclaimed;
}
```

### 3.3 工作集检测的 refault distance 算法

```c
/*
 * 工作集检测算法
 *
 * 核心概念：refault_distance = eviction_time - last_access_time
 *
 * 如果 distance < threshold → 页面仍在工作集
 * 如果 distance > threshold → 页面已被替换
 */
struct work_set {
    atomic_long_t refaults[ANON_AND_FILE];    // 重新入队计数
    atomic_long_t activations[ANON_AND_FILE];  // 激活计数
};

static unsigned long refault_distance(struct folio *folio)
{
    unsigned long evictions, activations;

    evictions = atomic_long_read(&folio->eviction_time);
    activations = atomic_long_read(&folio->last_fault_time);

    if (evictions == 0)
        return ULONG_MAX;

    return activations - evictions;
}

static void update_work_set(struct folio *folio, bool activate)
{
    if (activate) {
        atomic_long_inc(&work_set.activations[folio_is_anon(folio)]);
        folio->last_fault_time = jiffies;
    } else {
        folio->eviction_time = jiffies;
        atomic_long_inc(&work_set.refaults[folio_is_anon(folio)]);
    }
}
```

---

## 深入页表管理

### 4.1 四级页表遍历

```c
/*
 * 页表遍历核心宏
 * 页表级别: PGD → PUD → PMD → PTE
 */
#define pgd_offset(mm, address) \
    ((mm)->pgd + pgd_index(address))

#define pud_offset(pgd, address) \
    ((pud_t *)pgd_page_vaddr(*(pgd)) + pud_index(address))

#define pmd_offset(pud, address) \
    ((pmd_t *)pud_page_vaddr(*(pud)) + pmd_index(address))

#define pte_offset_kernel(pmd, address) \
    ((pte_t *)pmd_page_vaddr(*(pmd)) + pte_index(address))

/*
 * 页表查找流程 (x86_64 48-bit VA)
 *
 * 虚拟地址位分解:
 * [63:48]  符号扩展 (47:47)
 * [47:39]  PGD 索引 (9 bits)
 * [38:30]  PUD 索引 (9 bits)
 * [29:21]  PMD 索引 (9 bits)
 * [20:12]  PTE 索引 (9 bits)
 * [11:0]   页面偏移 (12 bits)
 */
```

### 4.2 页面错误处理完整流程

```c
/*
 * handle_pte_fault - 页面错误处理核心
 *
 * 页面错误类型:
 * 1. 初次访问 (demand zero)
 * 2. 文件映射 (mmap)
 * 3. 匿名映射 (堆/栈)
 * 4. 交换 (swap in)
 * 5. COW (copy-on-write)
 */
static vm_fault_t handle_pte_fault(struct vm_fault *vmf)
{
    pte_t entry;

    /* 1. 获取 PTE 指针 */
    vmf->pte = pte_offset_map(vmf->pmd, vmf->address);
    entry = *vmf->pte;

    /* 2. 页面不存在 */
    if (!pte_present(entry)) {
        if (pte_none(entry)) {
            /* 匿名页面或文件映射 */
            if (vmf->vma->vm_ops->fault)
                return vmf->vma->vm_ops->fault(vmf);
            return do_anonymous_page(vmf);
        }

        /* 页面被换出到 swap */
        if (pte_swap(entry))
            return do_swap_page(vmf);

        /* COW 页面 */
        if (is_cow_mapping(vma->vm_flags) && pte_write(entry))
            return do_wp_page(vmf);
    }

    /* 3. 写访问但页面只读 */
    if (vmf->flags & FAULT_FLAG_WRITE) {
        if (!pte_write(entry))
            return do_wp_page(vmf);
        pte_mkwrite(entry);
    }

    /* 4. 更新 accessed 和 dirty 位 */
    if (vmf->flags & FAULT_FLAG_WRITE)
        pte_mkdirty(entry);
    else
        pte_mkyoung(entry);

    /* 5. 更新 PTE */
    set_pte_at(vmf->mm, vmf->address, vmf->pte, entry);
    update_mmu_cache(vma, vmf->address, vmf->pte);

    return VM_FAULT_NOPAGE;
}
```

### 4.3 TLB shootdown 机制

```c
/*
 * TLB shootdown - 多核间 TLB 同步
 *
 * 当一个 CPU 修改了页表，其他 CPU 的 TLB 缓存需要失效
 */
void flush_tlb_mm(struct mm_struct *mm)
{
    cpumask_var_t mask;
    int cpu;

    /* 1. 获取需要刷新的 CPU 掩码 */
    cpumask_clear(mask);
    for_each_online_cpu(cpu) {
        if (cpu == smp_processor_id())
            continue;
        if (cpumask_test_cpu(cpu, mm_cpumask(mm)))
            cpumask_set_cpu(cpu, mask);
    }

    /* 2. 发送 IPI 中断 */
    if (!cpumask_empty(mask)) {
        smp_call_function_many(mask, flush_tlb_func, mm, 1);
    }

    /* 3. 本地 TLB 刷新 */
    local_flush_tlb();
}

/*
 * TLB 刷新优化
 *
 * 1. 单页面刷新: flush_tlb_page(vma, address)
 * 2. 范围刷新: flush_tlb_range(vma, start, end)
 * 3. 全部刷新: flush_tlb_all()
 */
```

---

## 深入锁与同步机制

### 5.1 Per-CPU 数据结构的锁优化

```c
/*
 * Per-CPU 数据结构的同步模式
 *
 * 模式1: 仅禁用抢占 (local_lock)
 *   - 用于短暂操作，不需要原子性
 *   - 例: percpu sheaves
 *
 * 模式2: Per-CPU 锁
 *   - 每个 CPU 有自己的锁
 *   - 用于需要保护的操作
 *
 * 模式3: RCU (Read-Copy-Update)
 *   - 读多写少场景
 *   - 例: 路由表查找
 */
struct slub_percpu_sheaves {
    local_lock_t lock;  // 编译时禁用抢占
};

/*
 * local_lock 使用示例
 */
static inline void *alloc_from_sheaf(struct kmem_cache *s)
{
    void *obj;

    local_lock(&s->cpu_sheaves->lock);
    obj = sheaf->freelist;
    sheaf->freelist = *(void **)obj;
    local_unlock(&s->cpu_sheaves->lock);

    return obj;
}
```

### 5.2 RCU 在内核中的典型应用

```c
/*
 * RCU (Read-Copy-Update) 核心概念
 *
 * 写操作:
 * 1. 复制并修改数据
 * 2. 等待所有 RCU 读临界区结束 (grace period)
 * 3. 释放旧数据
 *
 * 读操作:
 * 1. 进入 RCU 读临界区 (rcu_read_lock)
 * 2. 访问数据
 * 3. 离开 RCU 读临界区 (rcu_read_unlock)
 */
struct list_head {
    struct list_head *next, *prev;
};

/* RCU 保护的链表遍历 */
static inline void list_add_rcu(struct list_head *new, struct list_head *head)
{
    new->next = head->next;
    new->prev = head->prev;
    rcu_assign_pointer(head->next, new);
    new->next->prev = new;
}

/* RCU 遍历 */
rcu_read_lock();
list_for_each_entry_rcu(pos, head, member) {
    /* 安全访问 */
}
rcu_read_unlock();

/* 延迟释放 */
void free_obj(struct rcu_head *head)
{
    kfree(container_of(head, struct obj, rcu_head));
}

call_rcu(&obj->rcu_head, free_obj);
```

### 5.3 内存顺序与原子操作

```c
/*
 * 内存顺序模型 (x86_64)
 *
 * 编译器和 CPU 可能会重新排序内存访问
 * 不同的内存顺序提供不同的保证
 */
struct foo {
    int a;
    int b;
};

/* 示例：store 操作 */
void write_example(struct foo *f)
{
    /* 1. STORE (无保证) */
    f->a = 1;                    // store a

    /* 2. STORE with release (禁止重排序到之前) */
    smp_store_release(&f->a, 1);

    /* 3. STORE with seq_cst (完全顺序) */
    ACCESS_ONCE(f->a) = 1;      // seq_cst store
}

/* 示例：load 操作 */
int read_example(struct foo *f)
{
    int a, b;

    /* 1. LOAD (无保证) */
    a = f->a;                   // load a

    /* 2. LOAD with acquire (禁止重排序到之后) */
    a = smp_load_acquire(&f->a);

    /* 3. LOAD with seq_cst (完全顺序) */
    a = READ_ONCE(f->a);       // seq_cst load

    return a + b;
}

/*
 * 典型使用场景
 *
 * 1. cmpxchg_release: 用于实现 SLUB 的 freelist 更新
 *    - release 保证 freelist 指针更新在计数器更新之前
 *
 * 2. smp_load_acquire: 用于读取共享状态
 *    - acquire 保证后续读取看到之前的所有写入
 */
```

---

## 深入 CPU 调度算法

### 6.1 CFS 虚拟时间计算细节

```c
/*
 * vruntime 计算 - CFS 核心
 *
 * 公式: vruntime += delta_exec * (NICE_0_LOAD / weight)
 *
 * 这意味着：
 * - nice=0 的任务，vruntime 增长 = 实际运行时间
 * - nice=-20 (最高优先级)，weight 是 nice=0 的 4 倍
 *   vruntime 增长 = 实际时间 * (1024/4100) ≈ 1/4
 *   所以相同实际运行时间，vruntime 增长更慢
 * - nice=+19 (最低优先级)，weight 是 nice=0 的 1/16
 *   vruntime 增长 = 实际时间 * (1024/64) = 16 倍
 *   所以相同实际运行时间，vruntime 增长更快
 */

/*
 * load_weight 结构
 */
struct load_weight {
    unsigned long weight;       // 任务权重
    u32 inv_weight;           // 权重的倒数 (用于除法优化)
};

/*
 * delta_exec 计算
 */
static inline u64 calc_delta_fair(u64 delta_exec, struct sched_entity *se)
{
    if (se->load.weight != NICE_0_LOAD) {
        /* 非标准权重：乘以 (NICE_0_LOAD / weight) */
        return mul_u64_u32_div(delta_exec,
                               NICE_0_LOAD,
                               se->load.weight);
    }
    return delta_exec;
}
```

### 6.2 红黑树操作复杂度

```c
/*
 * CFS 红黑树 - O(log n) 操作
 *
 * 插入/删除: O(log n)，其中 n 是运行队列中的任务数
 * 查找最左节点: O(1) (因为缓存了最左节点)
 *
 * 关键优化：缓存 next 和 last 节点
 */
struct cfs_rq {
    struct rb_root_cached tasks_timeline;  // 红黑树根 + 最左缓存
    struct sched_entity *curr;            // 当前运行实体
    struct sched_entity *next;             // 下一个 (优化)
    struct sched_entity *last;            // 上一个 (优化)
    struct sched_entity *skip;             // 跳过 (用于负载均衡)
};

/*
 * pick_next_entity - 选择下一个调度实体
 */
static struct sched_entity *pick_next_entity(struct cfs_rq *cfs_rq,
                                            struct sched_entity *curr)
{
    struct sched_entity *left = __pick_first_entity(cfs_rq);

    /* 检查是否可以被抢占 */
    if (cfs_rq->nr_running == 1 && left && curr &&
        entity_before(curr, left)) {
        /* 当前任务仍在运行，使用它 */
        return curr;
    }

    return left;
}

/*
 * enqueue_entity - 入队
 *
 * 1. 更新 vruntime
 * 2. 插入红黑树
 * 3. 更新统计信息
 */
static void enqueue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se,
                           int flags)
{
    /* 更新虚拟时间 */
    update_curr(cfs_rq);

    /* 如果实体不在队列，更新 vruntime */
    if (se->on_rq == 0)
        se->vruntime += cfs_rq->min_vruntime;

    /* 插入红黑树 */
    __enqueue_entity(cfs_rq, se);
    se->on_rq = 1;

    /* 更新统计 */
    update_load_avg(cfs_rq, se, UPDATE_TG);
}
```

### 6.3 负载均衡的数学建模

```c
/*
 * 负载均衡算法
 *
 * 目标：保持各 CPU 负载均衡
 *
 * 关键概念：
 * 1. load = weight * running_time / period
 * 2. imbalance = 目标负载差
 * 3. 迁移阈值：只有当 imbalance 超过阈值时才迁移
 */

/*
 * 计算运行队列负载
 */
static unsigned long cfs_rq_load_avg(struct cfs_rq *cfs_rq)
{
    return cfs_rq->avg.load_avg;
}

/*
 * 计算 CPU 间的负载差
 */
static long cpu_load_diff(struct cpu_cpu_similarity *c)
{
    long load = c->dst_cpu_load - c->src_cpu_load;
    long imb = c->imbalance;

    /* 考虑容量差异 */
    return (load * SCHED_CAPACITY_SCALE) /
           (c->dst_cpu_capacity + c->src_cpu_capacity / 2);
}

/*
 * 判断是否需要均衡
 *
 * 只有当目标 CPU 有显著空闲容量时才迁移
 */
static bool need_balance(struct lb_env *env)
{
    struct sched_group *group = env->sd->groups;

    /* 计算组的平均负载 */
    unsigned long avg_load = group->avg_load;

    /* 判断是否可以接收任务 */
    return avg_load < env->sd->min_capacity;
}
```

---

## 深入网络协议栈

### 7.1 TCP 三次握手状态机实现

```c
/*
 * TCP 状态转换
 *
 * LISTEN → SYN_SENT → ESTABLISHED
 *
 * 关键代码路径：
 */
static int tcp_v4_conn_request(struct sock *sk, struct sk_buff *skb)
{
    struct tcp_sock *tp = tcp_sk(sk);

    /* 1. 分配 request_sock */
    req = inet_reqsk_alloc(&tcp_request_sock_ops);
    if (!req)
        return 0;

    /* 2. 初始化 SYN cookie */
    tcp_reqsk_deschedule(req);

    /* 3. 设置初始序列号 */
    tcp_rsk(req)->snt_isn = tcp_skb_timestamp(skb);

    /* 4. 发送 SYN+ACK */
    tcp_v4_send_synack(sk, skb, req);

    return 0;
}

/*
 * TCP 握手完成
 */
static int tcp_rcv_synsent_state_process(struct sock *sk,
                                          struct sk_buff *skb,
                                          const struct tcphdr *th)
{
    struct tcp_sock *tp = tcp_sk(sk);

    if (th->ack) {
        /* 收到 ACK，三次握手完成 */
        tcp_finish_connect(sk, skb);
    } else {
        /* 收到 SYN，转到 SYN_RCVD 状态 */
        tcp_set_state(sk, TCP_SYN_RECV);
    }
}
```

### 7.2 TCP 拥塞控制算法

```c
/*
 * TCP 拥塞控制
 *
 * 核心概念：
 * 1. cwnd (拥塞窗口) - 发送方可以发送的未确认字节数
 * 2. ssthresh (慢启动阈值) - 决定使用哪种算法
 * 3. 拥塞算法：Reno, Cubic, BBR 等
 */

/*
 * 慢启动算法
 *
 * 每次 RTT，cwnd 加倍
 * 直到 cwnd >= ssthresh
 */
void tcp_slow_start(struct tcp_sock *tp)
{
    int inc = tp->snd_cwnd_cnt;  // ACK 计数

    if (tp->snd_ssthresh < TCP_INFINITE_SSTHRESH) {
        /* 指数增长 */
        inc = min(inc, tp->snd_ssthresh);
        tp->snd_cwnd += inc;
        tp->snd_cwnd_cnt = 0;
    }
}

/*
 * 拥塞避免算法
 *
 * 每次 RTT，cwnd 加 1
 */
void tcp_cong_avoid(struct tcp_sock *tp)
{
    if (tp->snd_cwnd < tp->snd_ssthresh) {
        /* 慢启动 */
        tcp_slow_start(tp);
    } else {
        /* 线性增长 */
        tcp_reno_ai(tp);
    }
}

/*
 * 丢包检测后的处理
 */
void tcp_enter_loss(struct sock *sk)
{
    struct tcp_sock *tp = tcp_sk(sk);

    /* 1. 减小 ssthresh */
    tp->snd_ssthresh = tcp_fackets_before(tp->snd_una) / 2;

    /* 2. 减小 cwnd */
    tp->snd_cwnd = tp->snd_ssthresh;

    /* 3. 进入恢复状态 */
    tcp_set_ca_state(sk, TCP_CA_Loss);
}
```

### 7.3 Socket 缓冲区 (sk_buff) 管理

```c
/*
 * sk_buff 结构 - 网络数据包表示
 *
 * 关键设计：
 * 1. 分层结构：MAC header, IP header, TCP header, data
 * 2. 零拷贝支持：共享数据区域
 * 3. 线性/非线性数据分离
 */
struct sk_buff {
    unsigned int len;           // 数据总长度
    __u32       hash;          // 流量哈希

    struct sk_buff *next;       // SKB 链表
    struct sk_buff *prev;

    struct sock *sk;            // 所属 socket
    struct net_device *dev;    // 网络设备

    /* 头部信息 */
    __u16 protocol;           // 协议类型
    __u8  ip_summed;          // checksum 状态

    /* 时间戳 */
    struct skb_mstamp skb_mstamp;

    /* 线性数据区域 */
    unsigned char *head;       // 缓冲区开始
    unsigned char *data;        // 数据开始
    unsigned char *tail;       // 数据结束
    unsigned char *end;        // 缓冲区结束

    /* 分片信息 */
    struct sk_buff *frag_list;  // 分片链表
    struct skb_shared_info *skb_shinfo;
};

/*
 * 克隆 SKB (用于转发)
 *
 * 共享数据区域，只复制元数据
 */
static struct sk_buff *skb_clone(struct sk_buff *skb, gfp_t gfp)
{
    struct sk_buff *n;

    n = kmem_cache_alloc(skbuff_cache, gfp);
    if (!n)
        return NULL;

    /* 复制 SKB 头 */
    memcpy(n, skb, sizeof(struct sk_buff));

    /* 增加引用计数 */
    refcount_set(&n->users, 1);

    /* 共享数据区域 */
    n->cloned = 1;

    return n;
}

/*
 * 追加数据到 SKB
 */
static unsigned char *skb_put(struct sk_buff *skb, unsigned int len)
{
    unsigned char *tmp = skb->tail;

    skb->tail += len;
    skb->len += len;

    return tmp;
}
```

---

## 附录：核心算法复杂度总结

| 操作 | 算法 | 时间复杂度 |
|------|------|----------|
| Buddy 分配 | 空闲链表遍历 | O(log MAX_ORDER) |
| Buddy 释放 + 合并 | 递归伙伴查找 | O(log MAX_ORDER) |
| SLUB 分配 (fast) | cmpxchg | O(1) amortized |
| SLUB 分配 (slow) | barn 查找 | O(1) |
| CFS 入队 | 红黑树插入 | O(log n) |
| CFS 选取下一个 | 取最左节点 | O(1) |
| 页面错误处理 | 页表遍历 | O(4) 固定 |
| TCP 连接查找 | 哈希表 | O(1) average |
| LRU 回收 | 批量扫描 | O(batch_size) |

---

## 参考代码路径

| 文件 | 功能 |
|------|------|
| `mm/page_alloc.c` | Buddy 分配器核心 |
| `mm/slub.c` | SLUB 分配器核心 |
| `mm/vmscan.c` | 页面回收 |
| `mm/memory.c` | 页面错误处理 |
| `net/ipv4/tcp_ipv4.c` | TCP 实现 |
| `net/core/skbuff.c` | SKB 管理 |
| `kernel/sched/fair.c` | CFS 调度器 |
