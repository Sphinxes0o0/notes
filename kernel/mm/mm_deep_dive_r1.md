# Linux MM 子系统深度分析 R1

## 目录

1. [Buddy System (页面分配器)](#1-buddy-system-页面分配器)
2. [Slab Allocator (slub/slab/slob)](#2-slab-allocator)
3. [vmalloc (虚拟连续物理分散分配)](#3-vmalloc-虚拟连续物理分散分配)
4. [mmap (内存映射)](#4-mmap-内存映射)
5. [Page Cache (页缓存)](#5-page-cache-页缓存)
6. [知识点关联表格](#6-知识点关联表格)

---

## 1. Buddy System (页面分配器)

### 1.1 数据结构

#### struct free_area (mm/page_alloc.c:836, mmzone.h:138)

```c
struct free_area {
    struct list_head    free_list[MIGRATE_TYPES];  // 每种迁移类型一个链表
    unsigned long       nr_free;                   // 空闲页数量
};
```

关键点:
- `free_list[MIGRATE_TYPES]`: 按迁移类型组织空闲链表，支持 MIGRATE_UNMOVABLE、MIGRATE_MOVABLE、MIGRATE_RECLAIMABLE 等
- `nr_free`: 记录该阶(order)的总空闲页数
- 配合 struct zone 中的 `free_area[NR_PAGE_ORDERS]` 使用，实现多阶 buddy 系统

#### struct zone (mmzone.h:997)

```c
struct zone {
    // ...
    struct free_area    free_area[NR_PAGE_ORDERS];  // 最大支持 2^10=1024 页
    // ...
    spinlock_t          lock;                        // 保护 free_area
};
```

#### struct page (mm_types.h:79)

```c
struct page {
    memdesc_flags_t     flags;              // 页状态标志
    union {
        struct {                            // Page cache 和匿名页
            union {
                struct list_head lru;      // LRU链表
                struct list_head buddy_list; // Buddy系统链表
                struct list_head pcp_list;  // Per-CPU缓存链表
            };
            struct address_space *mapping;
            unsigned long private;          // Buddy系统中表示order
        };
        // ...
    };
    atomic_t        _mapcount;              // 映射计数
    atomic_t        _refcount;              // 引用计数
    // ...
};
```

### 1.2 alloc_pages() 分配流程

#### 核心函数调用链

```
alloc_pages()
  └── __alloc_pages_noprof()           (page_alloc.c:5279)
        └── __alloc_frozen_pages_noprof()
              └── __alloc_pages()      (page_alloc.c:5055)
                    └── __alloc_pages_slowpath()  (page_alloc.c:4710)
```

#### 快速路径 __alloc_pages (page_alloc.c:5055)

```c
static inline struct page *
__alloc_pages(gfp_t gfp, unsigned int order, int preferred_nid, nodemask_t *nodemask)
{
    struct page *page;
    
    // 1. 准备alloc_context
    if (!prepare_alloc_pages(gfp, order, preferred_nid, nodemask, &ac))
        return NULL;
        
    // 2. 尝试 Per-CPU 页缓存 (PCP)
    page = __rmqueue_pcplist(zone, order, migratetype, alloc_flags, pcp, list);
    if (page)
        return page;
        
    // 3. Buddy 系统分配
    page = __rmqueue(zone, order, migratetype, alloc_flags);
    return page;
}
```

### 1.3 Per-CPU Page Cache (PCP)

#### struct per_cpu_pages (page_alloc.c 概念)

PCP 是 order-0 页的 per-CPU 缓存，避免每次分配都访问 zone lock。

```c
// 分配路径: __rmqueue_pcplist (page_alloc.c:3336)
static struct page *__rmqueue_pcplist(struct zone *zone, unsigned int order,
        int migratetype, unsigned int alloc_flags, struct per_cpu_pages *pcp)
{
    // 从 per-CPU 列表中获取
    while (list_empty(&pcp->lists)) {
        // 列表空时，从 buddy 系统补充
        int count = rmqueue_bulk(zone, 0, pcp->batch, list, migratetype, alloc_flags);
        if (count == 0)
            break;
    }
    page = list_first_entry(list, struct page, pcp_list);
    list_del(&page->pcp_list);
    pcp->count--;
    return page;
}
```

### 1.4 Buddy 系统分配 - __rmqueue

#### rmqueue_bulk (page_alloc.c:2547)

```c
static int rmqueue_bulk(struct zone *zone, unsigned int order, unsigned int nr_pages,
        struct list_head *list, int migratetype, unsigned int alloc_flags)
{
    // 从 buddy 系统批量获取 order-0 页
    // 每获取一个页，可能触发 expand() 分割更高阶的块
}
```

### 1.5 split free page - expand() 算法

#### expand() 函数 (page_alloc.c:1732)

```c
static inline unsigned int expand(struct zone *zone, struct page *page, 
        int low, int high, int migratetype)
{
    unsigned int size = 1 << high;  // 当前阶的块大小
    
    while (high > low) {
        high--;
        size >>= 1;                 // 分割成一半
        
        // 设置 guard page (保留高位页作为 guard)
        if (set_page_guard(zone, &page[size], high))
            continue;
            
        // 将分割出的块加入 buddy 系统
        __add_to_free_list(&page[size], zone, high, migratetype, false);
        set_buddy_order(&page[size], high);
        nr_added += size;
    }
    return nr_added;
}
```

**算法分析**:
1. 当请求 order=N 的块但没有精确匹配时，尝试使用 order>M 的块分割
2. 从 order=M 的块开始，每次分割成两半:
   - 低地址的一半保留给更高阶请求
   - 高地址的一半继续分割或加入对应阶的 free_list
3. Guard page 用于检测越界访问和合并

#### page_del_and_expand (page_alloc.c:1760)

```c
static __always_inline void page_del_and_expand(struct zone *zone,
        struct page *page, int low, int high, int migratetype)
{
    int nr_pages = 1 << high;
    
    // 1. 从当前阶的 free_list 删除
    __del_page_from_free_list(page, zone, high, migratetype);
    
    // 2. 分割剩余部分，重新加入 buddy 系统
    nr_pages -= expand(zone, page, low, high, migratetype);
    
    // 3. 更新统计
    account_freepages(zone, -nr_pages, migratetype);
}
```

### 1.6 关键源码位置

| 函数/结构 | 文件位置 |
|-----------|----------|
| struct free_area | mmzone.h:138 |
| struct zone | mmzone.h:997 |
| __alloc_pages_noprof | page_alloc.c:5279 |
| __alloc_pages_slowpath | page_alloc.c:4710 |
| expand | page_alloc.c:1732 |
| __rmqueue_pcplist | page_alloc.c:3336 |
| rmqueue_bulk | page_alloc.c:2547 |

---

## 2. Slab Allocator

### 2.1 Slub/Slab/Slob 三代对比

| 特性 | Slab (早期) | Slob (嵌入式) | Slub (当前默认) |
|------|-------------|---------------|-----------------|
| 设计目标 | 通用 | 嵌入式/小系统 | 高性能/多核优化 |
| 管理方式 | 每个节点独立 slab 链表 | 简单链表 | Per-CPU partial sheaves |
| 锁竞争 | 较严重 | 轻微 | per-CPU freelist，减少锁 |
| 内存利用率 | 一般 | 最好 | 较好 |
| 代码复杂度 | 复杂 | 简单 | 中等 |

### 2.2 struct kmem_cache (slub.c:208)

```c
struct kmem_cache {
    struct kmem_cache_cpu __percpu *cpu_slab;   // Per-CPU 指针
    unsigned long           flags;                // 调试标志
    unsigned long           size;                 // 对象大小
    unsigned long           object_size;          // 原始对象大小
    struct kmem_cache_order_objects oo;          // 阶和对象数
    
    // Node 管理
    struct kmem_cache_node *node[MAX_NUMNODES];
    
    // 对象管理
    unsigned int            align;                // 对齐要求
    const char             *name;                  // 缓存名称
    struct list_head       list;                  // 全局缓存链表
    
    // Freelist
    unsigned int            offset;               // Freelist 偏移
    unsigned int            cpu_partial_length;   // Per-CPU sheaves 大小
    
    // ...
};
```

### 2.3 struct kmem_cache_node (slub.c:430)

```c
struct kmem_cache_node {
    spinlock_t          list_lock;
    unsigned long       nr_partial;       // 部分空闲 slab 数
    struct list_head    partial;          // 部分空闲 slab 链表
#ifdef CONFIG_SLUB_DEBUG
    atomic_long_t       nr_slabs;
    atomic_long_t       total_objects;
    struct list_head    full;             // 满 slab 链表
#endif
    struct node_barn   *barn;            // Per-CPU sheaves
};
```

### 2.4 Slub 分配核心流程

#### ___slab_alloc (slub.c:4374)

```c
static void *___slab_alloc(struct kmem_cache *s, gfp_t gfpflags, int node,
        unsigned long addr, unsigned int orig_size)
{
    bool allow_spin = gfpflags_allow_spinning(gfpflags);
    void *object;
    struct slab *slab;
    struct partial_context pc;
    
new_objects:
    pc.flags = gfpflags;
    
    // 1. 尝试从 per-CPU sheaves 获取
    object = get_from_partial(s, node, &pc);
    if (object)
        goto success;
        
    // 2. 分配新 slab
    slab = new_slab(s, pc.flags, node);
    if (unlikely(!slab)) {
        // 尝试回退逻辑...
        return NULL;
    }
    
    // 3. 从新 slab 分配
    if (IS_ENABLED(CONFIG_SLUB_TINY) || kmem_cache_debug(s)) {
        object = alloc_single_from_new_slab(s, slab, orig_size, gfpflags);
    } else {
        alloc_from_new_slab(s, slab, &object, 1, allow_spin);
    }
    
success:
    return object;
}
```

### 2.5 Per-CPU Partial Sheaves

Slub 使用 sheaves 机制管理 per-CPU 的部分空闲 slab:

```c
// slub.c 中的关键函数
static struct slab_sheaf *alloc_empty_sheaf(struct kmem_cache *s, gfp_t gfp);
static void sheaf_flush_main(struct kmem_cache *s);
static bool sheaf_try_flush_main(struct kmem_cache *s);
```

**Sheaves 设计**:
- 每个 CPU 维护多个 sheaf，每个 sheaf 包含一个部分空闲的 slab
- 减少锁竞争，提高分配效率
- 通过 `slub_percpu_sheaves` 结构管理

### 2.6 Freelist 管理

#### Freelist 编码 (slub.c:500)

```c
//Freelist 指针编码
static inline freeptr_t freelist_ptr_encode(const struct kmem_cache *s,
        void *ptr, unsigned int addr)
{
    unsigned int val = (unsigned int)addr;
    
    // 编码 freelist 指针，低位存储标志
    return (freeptr_t)((unsigned long)ptr | (val & s->cpu_partial_length));
}

static inline void *freelist_ptr_decode(const struct kmem_cache *s,
        freeptr_t ptr)
{
    return (void *)(ptr & ~((1UL << s->freeptr_offset) - 1));
}
```

#### Freelist 获取/设置 (slub.c:526)

```c
static inline void *get_freepointer(struct kmem_cache *s, void *object)
{
    return freelist_ptr_decode(s, *(freeptr_t *)(object + s->offset));
}

static inline void set_freepointer(struct kmem_cache *s, void *object, void *fp)
{
    *(freeptr_t *)(object + s->offset) = freelist_ptr_encode(s, fp, 0);
}
```

### 2.7 关键源码位置

| 函数/结构 | 文件位置 |
|-----------|----------|
| struct kmem_cache | slub.c:208 |
| struct kmem_cache_node | slub.c:430 |
| ___slab_alloc | slub.c:4374 |
| __slab_alloc_node | slub.c:4453 |
| alloc_from_new_slab | slub.c:4316 |
| get_from_partial | slub.c:3792 |
| new_slab | slub.c:3532 |

---

## 3. vmalloc (虚拟连续物理分散分配)

### 3.1 数据结构

#### struct vm_struct (vmalloc.h:52)

```c
struct vm_struct {
    union {
        struct vm_struct *next;     // 早期注册的 vm_areas
        struct llist_node llnode;   // 异步释放
    };
    
    void            *addr;          // 虚拟地址起始
    unsigned long    size;           // 总大小(含 guard page)
    unsigned long    flags;          // VM_IOREMAP, VM_ALLOC, VM_MAP 等
    struct page     **pages;         // 物理页指针数组
#ifdef CONFIG_HAVE_ARCH_HUGE_VMALLOC
    unsigned int     page_order;    // Huge page 阶
#endif
    unsigned int     nr_pages;       // 页数
    phys_addr_t      phys_addr;     // 物理地址(ioremap 用)
    const void      *caller;        // 调用者
    unsigned long    requested_size;  // 请求的大小
};
```

#### struct vmap_area (vmalloc.h:71)

```c
struct vmap_area {
    unsigned long    va_start;       // 虚拟地址起始
    unsigned long    va_end;         // 虚拟地址结束
    
    struct rb_node   rb_node;       // 地址排序的红黑树
    struct list_head list;           // 地址排序链表
    
    union {
        unsigned long subtree_max_size;  // 空闲树
        struct vm_struct *vm;            // 占用时指向 vm_struct
    };
    unsigned long    flags;         // 区域类型标志
};
```

### 3.2 分配流程

#### __vmalloc_node_range (vmalloc.c:3986)

```c
void *__vmalloc_node_range_noprof(unsigned long size, unsigned long align,
        unsigned long start, unsigned long end, gfp_t gfp_mask,
        pgprot_t prot, unsigned long vm_flags, int node, const void *caller)
{
    struct vm_struct *area;
    
again:
    // 1. 分配 vm_struct 和 vmap_area
    area = __get_vm_area_node(size, align, shift, VM_ALLOC |
              VM_UNINITIALIZED | vm_flags, start, end, node,
              gfp_mask, caller);
    if (!area) {
        // 失败处理...
        return NULL;
    }
    
    // 2. 分配物理页并映射
    ret = __vmalloc_area_node(area, gfp_mask);
    
    return ret;
}
```

#### __get_vm_area_node (vmalloc.c:3203)

```c
struct vm_struct *__get_vm_area_node(unsigned long size, unsigned long align,
        unsigned long shift, unsigned long flags, unsigned long start,
        unsigned long end, int node, gfp_t gfp_mask, const void *caller)
{
    struct vmap_area *va;
    struct vm_struct *area;
    
    area = kzalloc_node(sizeof(*area), gfp_mask & GFP_RECLAIM_MASK, node);
    
    // 分配 vmap_area
    va = alloc_vmap_area(size, align, start, end, node, gfp_mask, 0, area);
    
    return area;
}
```

### 3.3 vmap_area 管理 - 红黑树

#### alloc_vmap_area (vmalloc.c:2029)

```c
static struct vmap_area *alloc_vmap_area(unsigned long size,
        unsigned long align, unsigned long vstart, unsigned long vend,
        int node, gfp_t gfp_mask, unsigned long va_flags, struct vm_struct *vm)
{
    struct vmap_area *va;
    
    // 1. 从 per-node 缓存分配 va
    va = node_alloc(...);
    if (!va) {
        va = kmem_cache_alloc_node(vmap_area_cachep, gfp_mask, node);
    }
    
retry:
    // 2. 使用红黑树查找最佳匹配
    if (IS_ERR_VALUE(addr)) {
        addr = __alloc_vmap_area(&free_vmap_area_root, 
            &free_vmap_area_list, size, align, vstart, vend);
    }
    
    // 3. 初始化 va
    va->va_start = addr;
    va->va_end = addr + size;
    va->vm = area;
    
    return va;
}
```

#### __alloc_vmap_area (vmalloc.c:1837)

```c
static unsigned long __alloc_vmap_area(struct rb_root *root, 
        struct list_head *head, unsigned long size, unsigned long align,
        unsigned long vstart, unsigned long vend)
{
    struct vmap_area *va;
    
    // 1. 查找最小匹配
    va = find_vmap_lowest_match(root, size, align, vstart, adjust_search_size);
    if (unlikely(!va))
        return -ENOENT;
        
    // 2. 分割/分配
    nva_start_addr = va_alloc(va, root, head, size, align, vstart, vend);
    
    return nva_start_addr;
}
```

### 3.4 物理页分配与映射

#### __vmalloc_area_node (vmalloc.c:3827)

```c
static void *__vmalloc_area_node(struct vm_struct *area, gfp_t gfp_mask)
{
    // 1. 分配物理页数组
    area->pages = alloc_pages_array(area->nr_pages, gfp_mask);
    
    // 2. 分配每个物理页
    for (i = 0; i < area->nr_pages; i++) {
        area->pages[i] = alloc_page(gfp_mask);
    }
    
    // 3. 建立页表映射
    ret = vmap_pages_range(addr, addr + size, prot, area->pages, page_shift);
    
    return ret;
}
```

### 3.5 vmalloc_sync_all

vmalloc_sync_all 确保所有 CPU 的 TLB 和直接映射保持一致:

```c
// vmalloc.c 中的同步机制
void vm_unmap_aliases(void);  // 刷新 vmalloc 区域的别名映射

// 在 arch 特定代码中实现
// 例如: sync_core_before_usermode() 确保跨 CPU 可见性
```

### 3.6 关键源码位置

| 函数/结构 | 文件位置 |
|-----------|----------|
| struct vm_struct | vmalloc.h:52 |
| struct vmap_area | vmalloc.h:71 |
| __vmalloc_node_range_noprof | vmalloc.c:3986 |
| __get_vm_area_node | vmalloc.c:3203 |
| alloc_vmap_area | vmalloc.c:2029 |
| __alloc_vmap_area | vmalloc.c:1837 |
| __vmalloc_area_node | vmalloc.c:3827 |

---

## 4. mmap (内存映射)

### 4.1 数据结构

#### struct vm_area_struct (mm_types.h:913)

```c
struct vm_area_struct {
    union {
        struct {
            unsigned long vm_start;     // 起始地址 (包含)
            unsigned long vm_end;      // 结束地址 (不包含)
        };
        freeptr_t vm_freeptr;         // SLAB_TYPESAFE_BY_RCU
    };
    
    struct mm_struct         *vm_mm;      // 所属地址空间
    pgprot_t                 vm_page_prot; // 访问权限
    union {
        const vm_flags_t vm_flags;
        vma_flags_t flags;
    };
    
    // Anonymous VMA 链
    struct list_head        anon_vma_chain;  // 反向映射
    struct anon_vma        *anon_vma;
    
    // 操作函数
    const struct vm_operations_struct *vm_ops;
    
    // 文件映射信息
    unsigned long           vm_pgoff;        // 文件内偏移
    struct file           *vm_file;         // 文件指针
    void                  *vm_private_data; // 私有数据
};
```

### 4.2 do_mmap() 流程 (mmap.c:335)

```c
unsigned long do_mmap(struct file *file, unsigned long addr,
        unsigned long len, unsigned long prot, unsigned long flags,
        vm_flags_t vm_flags, unsigned long pgoff, unsigned long *populate,
        struct list_head *uf)
{
    struct mm_struct *mm = current->mm;
    
    // 1. 参数校验
    if (!len)
        return -EINVAL;
        
    // 2. PROT_READ -> PROT_EXEC 处理
    if ((prot & PROT_READ) && (current->personality & READ_IMPLIES_EXEC))
        if (!(file && path_noexec(&file->f_path)))
            vm_flags |= VM_EXEC;
            
    // 3. 计算对齐后的地址
    addr = calc_unmapped_area(file, pgoff, len, vm_flags);
    
    // 4. 尝试与相邻 VMA 合并
    vma = vma_merge_new_range(...);
    
    // 5. 分配新 VMA
    if (!vma) {
        vma = mmap_region(...);
    }
    
    return addr;
}
```

### 4.3 mmap_region 流程 (vma.c:2818)

```c
unsigned long mmap_region(struct file *file, unsigned long addr,
        unsigned long len, vm_flags_t vm_flags, unsigned long pgoff,
        struct list_head *uf)
{
    VMA_ITERATOR(vmi, mm, addr);
    MMAP_STATE(map, mm, &vmi, addr, len, pgoff, vm_flags, file);
    
    // 1. mmap_prepare 调用
    if (file && file->f_op->mmap_prepare)
        call_mmap_prepare(&map, &desc);
    
    // 2. 设置 VMA
    __mmap_setup(&map, &desc, uf);
    
    // 3. 尝试与相邻 VMA 合并
    if (map.prev || map.next) {
        vma = vma_merge_new_range(&vmg);
    }
    
    // 4. 分配新 VMA
    if (!vma) {
        error = __mmap_new_vma(&map, &vma);
        allocated_new = true;
    }
    
    // 5. 完成映射
    __mmap_complete(&map, vma);
    
    return addr;
}
```

### 4.4 find_vma() 实现 (mmap.c:902)

```c
struct vm_area_struct *find_vma(struct mm_struct *mm, unsigned long addr)
{
    unsigned long index = addr;
    
    mmap_assert_locked(mm);
    return mt_find(&mm->mm_mt, &index, ULONG_MAX);
}
```

使用 mm_mt (mt_tree) 进行快速查找，内部使用 VMA iterator。

### 4.5 mmap_lock 锁机制

#### 锁层级

```c
// mm/mmap.c 中的锁使用
mmap_read_lock(mm);      // 读锁，用于查找 VMA
mmap_write_lock(mm);     // 写锁，用于修改 VMA

// mmap_assert_locked(mm) 验证锁状态
```

#### 关键临界区

```c
// mmap.c:309 - do_mmap 要求写锁
// The caller must write-lock current->mm->mmap_lock.

unsigned long do_mmap(...)
{
    mmap_assert_write_locked(mm);
    // ...
}
```

### 4.6 关键源码位置

| 函数/结构 | 文件位置 |
|-----------|----------|
| struct vm_area_struct | mm_types.h:913 |
| do_mmap | mmap.c:335 |
| mmap_region | vma.c:2818 |
| __mmap_region | vma.c:2720 |
| find_vma | mmap.c:902 |
| find_vma_prev | mmap.c:925 |

---

## 5. Page Cache (页缓存)

### 5.1 数据结构

#### struct address_space (fs.h:470)

```c
struct address_space {
    struct inode        *host;              // 所属 inode
    struct xarray       i_pages;            // 页缓存 (原 radix_tree)
    struct rw_semaphore invalidate_lock;    // 失效保护锁
    gfp_t               gfp_mask;           // 分配掩码
    atomic_t            i_mmap_writable;    // 共享映射计数
    
    struct rb_root_cached i_mmap;          // 私有/共享映射树
    unsigned long       nrpages;           // 缓存页数
    pgoff_t             writeback_index;    // 回写起始位置
    
    const struct address_space_operations *a_ops;  // 文件操作
    unsigned long        flags;
    // ...
};
```

#### XArray (替代 Radix Tree)

Linux 6.x 使用 XArray 替代了传统的 radix_tree:

```c
// xas 操作示例 (filemap.c:851)
XA_STATE_ORDER(xas, &mapping->i_pages, index, folio_order(folio));

xas_lock_irq(&xas);
xas_for_each_conflict(&xas, entry) {
    // 处理冲突...
}
xas_store(&xas, folio);
xas_unlock_irq(&xas);
```

### 5.2 page_cache_delete (filemap.c:129)

```c
static void page_cache_delete(struct address_space *mapping,
        struct folio *folio, void *shadow)
{
    XA_STATE(xas, &mapping->i_pages, folio->index);
    long nr = 1;
    
    mapping_set_update(&xas, mapping);
    
    xas_set_order(&xas, folio->index, folio_order(folio));
    nr = folio_nr_pages(folio);
    
    VM_BUG_ON_FOLIO(!folio_test_locked(folio), folio);
    
    // 存储 shadow 用于 shadow memory
    xas_store(&xas, shadow);
    xas_init_marks(&xas);
    
    folio->mapping = NULL;
    mapping->nrpages -= nr;
}
```

### 5.3 filemap_fault 流程 (filemap.c:3512)

```c
vm_fault_t filemap_fault(struct vm_fault *vmf)
{
    struct file *file = vmf->vma->vm_file;
    struct address_space *mapping = file->f_mapping;
    struct inode *inode = mapping->host;
    pgoff_t max_idx, index = vmf->pgoff;
    struct folio *folio;
    vm_fault_t ret = 0;
    
    max_idx = DIV_ROUND_UP(i_size_read(inode), PAGE_SIZE);
    if (unlikely(index >= max_idx))
        return VM_FAULT_SIGBUS;
    
    // 1. 查找页缓存
    folio = filemap_get_folio(mapping, index);
    if (likely(!IS_ERR(folio))) {
        // 缓存命中
        if (!(vmf->flags & FAULT_FLAG_TRIED))
            fpin = do_async_mmap_readahead(vmf, folio);
        if (unlikely(!folio_test_uptodate(folio))) {
            filemap_invalidate_lock_shared(mapping);
            mapping_locked = true;
        }
    } else {
        // 2. 缓存未命中
        ret = filemap_fault_recheck_pte_none(vmf);
        if (unlikely(ret))
            return ret;
            
        // 触发同步 readahead
        fpin = do_sync_mmap_readahead(vmf);
        
retry_find:
        // 获取锁
        filemap_invalidate_lock_shared(mapping);
        mapping_locked = true;
        
        // 创建新 folio
        folio = __filemap_get_folio(mapping, index, 
            FGP_CREAT|FGP_FOR_MMAP, vmf->gfp_mask);
    }
    
    // 3. 填充页
    // ...
    
    return ret;
}
```

### 5.4 __filemap_add_folio (filemap.c:848)

```c
noinline int __filemap_add_folio(struct address_space *mapping,
        struct folio *folio, pgoff_t index, gfp_t gfp, void **shadowp)
{
    XA_STATE_ORDER(xas, &mapping->i_pages, index, folio_order(folio));
    
    mapping_set_update(&xas, mapping);
    folio_ref_add(folio, nr);
    folio->mapping = mapping;
    folio->index = xas.xa_index;
    
    for (;;) {
        xas_lock_irq(&xas);
        xas_for_each_conflict(&xas, entry) {
            // 处理冲突(大页/THP 等)
        }
        
        if (old) {
            // 分割大 entry
            if (order > 0 && order > forder) {
                // split handling
            }
        }
        
        // 存储 folio
        xas_store(&xas, folio);
        xas_unlock_irq(&xas);
    }
    
    __mod_node_page_state(page_pgdat(folio_page(folio, 0)),
        NR_FILE_PAGES, nr);
    if (folio_test_swapbacked(folio))
        __mod_lruvec_page_state(folio_page(folio, 0),
            NR_SHMEM, nr);
            
    return 1;
}
```

### 5.5 关键源码位置

| 函数/结构 | 文件位置 |
|-----------|----------|
| struct address_space | fs.h:470 |
| struct address_space_operations | fs.h:403 |
| page_cache_delete | filemap.c:129 |
| filemap_fault | filemap.c:3512 |
| __filemap_add_folio | filemap.c:848 |
| filemap_get_folio | filemap.c (搜索) |

---

## 6. 知识点关联表格

### 6.1 内存分配器层级关系

```
+----------------------------------------------------------+
|                    用户空间分配                           |
|  malloc() / new()                                        |
+----------------------------------------------------------+
          ↓
+----------------------------------------------------------+
|                    Slab Allocator (kmem_cache)           |
|  - kmalloc() / kmem_cache_alloc()                       |
|  - 适用于小对象分配 (< PAGE_SIZE)                        |
|  - 管理 struct kmem_cache, per-CPU sheaves              |
+----------------------------------------------------------+
          ↓
+----------------------------------------------------------+
|                    vmalloc                               |
|  - vmalloc() / vmap()                                   |
|  - 虚拟连续，物理分散                                     |
|  - 使用 vmap_area 红黑树管理虚拟地址                      |
+----------------------------------------------------------+
          ↓
+----------------------------------------------------------+
|                    Buddy System (page_alloc)             |
|  - alloc_pages() / __get_free_pages()                   |
|  - 物理页分配，order 0 ~ max_order                      |
|  - free_area[] 数组管理多阶空闲链表                       |
+----------------------------------------------------------+
          ↓
+----------------------------------------------------------+
|                    Per-CPU Page Cache (PCP)              |
|  - order-0 页的 per-CPU 缓存                            |
|  - 减少 zone->lock 竞争                                  |
+----------------------------------------------------------+
```

### 6.2 核心数据结构对照

| 功能模块 | 主要结构 | 关键字段 | 管理方式 |
|---------|---------|---------|---------|
| Buddy | free_area | free_list[], nr_free | 按 order 和 migratetype |
| Slub | kmem_cache | cpu_slab, node[] | per-CPU sheaves |
| vmalloc | vm_struct | addr, pages[], size | vmap_area 红黑树 |
| mmap | vm_area_struct | vm_start, vm_end, vm_ops | mt_find/VMA iterator |
| Page Cache | address_space | i_pages (xarray), nrpages | XArray |

### 6.3 分配路径对比

| 分配场景 | 入口函数 | 核心路径 | 文件位置 |
|---------|---------|---------|---------|
| 分配物理页 | alloc_pages() | __alloc_pages_noprof → __rmqueue | page_alloc.c:5279 |
| 分配小对象 | kmem_cache_alloc() | __slab_alloc_node → ___slab_alloc | slub.c:4453 |
| vmalloc | vmalloc() | __vmalloc_node_range → __get_vm_area_node | vmalloc.c:3986 |
| mmap | do_mmap() | mmap_region → __mmap_new_vma | mmap.c:335 |
| 页缓存读取 | filemap_fault() | filemap_get_folio → __filemap_add_folio | filemap.c:3512 |

### 6.4 锁机制总结

| 模块 | 锁类型 | 保护对象 | 关键函数 |
|------|--------|---------|---------|
| Buddy/Zone | spinlock_t | free_area, nr_free | spin_lock(&zone->lock) |
| Slub | per-CPU + spinlock | per-CPU sheaves, partial list | spin_lock_irqsave |
| vmalloc | spinlock | vmap_area rb_tree, free list | spin_lock(&free_vmap_area_lock) |
| mmap | mmap_lock (rw_semaphore) | vm_area_struct 链表/红黑树 | mmap_read/write_lock |
| Page Cache | invalidate_lock | address_space i_pages | down_read/write |

### 6.5 算法复杂度

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| Buddy 分配 | O(1) ~ O(阶数) | 查找对应 order 的 free_list |
| Buddy 释放+合并 | O(1) ~ O(阶数) | 检查 buddy 是否可合并 |
| Slub 分配 | O(1) ~ O(n) | per-CPU 缓存命中 O(1)，否则遍历 node |
| vmalloc | O(log V) | vmap_area 红黑树查找，V 为虚拟地址空间 |
| find_vma | O(log N) | VMA 红黑树/基数树查找，N 为 VMA 数量 |
| Page Cache 查询 | O(log M) | XArray 查找，M 为映射的页数 |

### 6.6 源码文件索引

| 文件 | 主要内容 | 行数 |
|------|---------|------|
| mm/page_alloc.c | Buddy System, Per-CPU Pages | 7856 |
| mm/slub.c | Slub Allocator 实现 | 9839 |
| mm/vmalloc.c | vmalloc 实现 | 5485 |
| mm/mmap.c | mmap 系统调用入口 | 1922 |
| mm/filemap.c | Page Cache 实现 | 4751 |
| include/linux/mmzone.h | Zone, free_area 结构定义 | - |
| include/linux/vmalloc.h | vm_struct, vmap_area 定义 | - |
| include/linux/mm_types.h | page, vm_area_struct 定义 | - |
| include/linux/fs.h | address_space 定义 | - |

---

## 总结

Linux MM 子系统是一个层次化的内存管理体系:

1. **Buddy System** 提供物理页分配基础，通过 `free_area[]` 数组支持多阶分配，配合 Per-CPU Page Cache 减少锁竞争

2. **Slab Allocator** 在 buddy 基础上提供小对象缓存，Slub 通过 per-CPU sheaves 机制优化多核性能

3. **vmalloc** 分配虚拟连续、物理分散的内存区域，使用 vmap_area 红黑树管理虚拟地址空间

4. **mmap** 通过 vm_area_struct 管理用户态虚拟内存区域，使用 mmap_lock 保护并发访问

5. **Page Cache** 基于 XArray 实现页缓存，提供文件映射的缓存管理和 page fault 处理能力

各子系统通过统一的锁机制、分配接口和统计框架协同工作，构成了 Linux 完整的内存管理解决方案。

---

*文档版本: R1*
*生成日期: 2026-04-26*
*源码版本: Linux Kernel (当前仓库版本)*
