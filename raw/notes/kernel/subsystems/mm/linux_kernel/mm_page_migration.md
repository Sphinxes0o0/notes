# MM 页面迁移 (Page Migration)

## 1. migrate_pages 核心函数

### 1.1 migrate_pages 入口
**文件**: `mm/migrate.c:2072-2167`

```c
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

    memset(&stats, 0, sizeof(stats));

    // 先处理 hugetlb
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
        if (nr_pages >= NR_MAX_BATCHED_MIGRATION)
            break;
    }

    // 批量迁移
    if (nr_pages >= NR_MAX_BATCHED_MIGRATION)
        list_cut_before(&folios, from, &folio2->lru);
    else
        list_splice_init(from, &folios);

    if (mode == MIGRATE_ASYNC)
        rc = migrate_pages_batch(&folios, get_new_folio, put_new_folio,
                private, mode, reason, &ret_folios,
                &split_folios, &stats,
                NR_MAX_MIGRATE_PAGES_RETRY);
    else
        rc = migrate_pages_sync(&folios, get_new_folio, put_new_folio,
                private, mode, reason, &ret_folios,
                &split_folios, &stats);

    // 重试逻辑
    if (list_empty(from))
        goto out;
    if (rc == -EAGAIN && mode != MIGRATE_ASYNC) {
        list_splice(&folios, from);
        goto again;
    }
    // ...
}
```

### 1.2 migrate_pages_batch
**文件**: `mm/migrate.c:1869-1996`

```c
static int migrate_pages_batch(struct list_head *folios,
        new_folio_t get_new_folio, free_folio_t put_new_folio,
        unsigned long private, enum migrate_mode mode, int reason,
        struct list_head *ret_folios, struct list_head *split_folios,
        struct migrate_pages_stats *stats, unsigned int retry_count)
{
    int rc = 0;
    struct folio *folio, *folio2;
    struct page *page;

    list_for_each_entry_safe(folio, folio2, folios, lru) {
        // 获取新页面
        new_folio = get_new_folio(folio, private);
        if (!new_folio) {
            list_move(&folio->lru, ret_folios);
            continue;
        }

        // 执行迁移
        rc = migrate_folio(folio, new_folio, mode);
        if (rc == MIGRATE_SUCCESS) {
            put_new_folio(new_folio, private);
            list_move(&folio->lru, ret_folios);
        } else if (rc == MIGRATE_SPLIT) {
            // 分割处理
            list_move(&folio->lru, split_folios);
        } else {
            // 失败，放回原链表
            list_move(&folio->lru, ret_folios);
        }
    }
    return rc;
}
```

## 2. migrate_folio 实现

### 2.1 migrate_folio
**文件**: `mm/migrate.c:1593-1650`

```c
int migrate_folio(struct folio *src, struct folio *dst, enum migrate_mode mode)
{
    int rc;

    // 文件系统实现
    if (src->mapping->a_ops->migrate_folio)
        return src->mapping->a_ops->migrate_folio(src, dst, mode);

    // 通用实现
    return migrate_folio_move(migrate_folio_copy, src, dst, mode);
}
```

### 2.2 migrate_folio_move
**文件**: `mm/migrate.c:1530-1580`

```c
static int migrate_folio_move(migrate_fn_t migrate_folio_copy,
                            struct folio *src, struct folio *dst,
                            enum migrate_mode mode)
{
    int rc;

    // 锁定两个页面
    folio_lock(src);
    folio_lock(dst);

    // 检查页面是否仍可迁移
    rc = migrate_folio_prepare(src, dst, mode);
    if (rc != MIGRATE_SUCCESS)
        goto out;

    // 复制内容
    rc = migrate_folio_copy(src, dst);
    if (rc != MIGRATE_SUCCESS)
        goto out;

    // 完成迁移
    rc = migrate_folio_done(src, dst, rc, mode);

out:
    folio_unlock(dst);
    folio_unlock(src);
    return rc;
}
```

### 2.3 migrate_folio_copy
**文件**: `mm/migrate.c:1400-1475`

```c
static int migrate_folio_copy(struct folio *src, struct folio *dst)
{
    copy_highpage folio_to_folio(dst, src);

    // 复制元数据
    dst->flags &= ~(1 << PG_dirty);
    dst->flags |= (src->flags & (1 << PG_dirty));

    // 复制 private 数据
    if (src->private)
        set_page_private(dst, page_private(src));

    return MIGRATE_SUCCESS;
}
```

## 3. copy_page 机制

### 3.1 copy_page
**文件**: `arch/x86/include/asm/copy_page.h`

```c
// x86_64 实现
void copy_page(void *to, void *from)
{
    asm volatile(
        "rep ; movsq"
        : "+D"(to), "+S"(from)
        : "c"(PAGE_SIZE / 8)
        : "memory"
    );
}
```

### 3.2 copy_mc_user_highpage
**文件**: `mm/memory-failure.c:500-550`

```c
size_t copy_mc_user_highpage(struct page *to, struct page *from,
                            unsigned long addr, struct vm_area_struct *vma)
{
    size_t rc;

    // 使用 copy_page 复制，带内存错误检测
    asm volatile(
        "1: movq %[size], %%rcx\n"
        "   rep movsb\n"
        "   xor %%rax, %%rax\n"
        "2:\n"
        _ASM_EXTABLE_TYPE_REG(1b, 2b, EX_TYPE_UACCESS_EC, %[rc])
        : [rc] "=r" (rc)
        : [size] "r" (PAGE_SIZE),
          "D" (page_to_virt(to)),
          "S" (page_to_virt(from))
        : "memory", "rcx", "rax"
    );

    return rc;
}
```

## 4. 页面重映射

### 4.1 remove_migration_ptes
**文件**: `mm/migrate.c:1200-1290`

```c
void remove_migration_ptes(struct folio *src, struct folio *dst, bool locked)
{
    struct rmap_walk_control rwc = {
        .rmap_one = remove_migration_pte,
        .arg = dst,
        .done = folio_not_mapped,
        .anon_lock = folio_lock_anon_vma_read,
    };

    if (locked)
        rmap_walk_locked(src, &rwc);
    else
        rmap_walk(src, &rwc);
}
```

### 4.2 remove_migration_pte
**文件**: `mm/migrate.c:1150-1195`

```c
static bool remove_migration_pte(struct folio *folio,
        struct vm_area_struct *vma, unsigned long addr, void *arg)
{
    struct folio *dst = arg;
    pte_t *pte;
    pte_t pteval;
    spinlock_t *ptl;

    pte = pte_offset_map_lock(vma->vm_mm, pmd, addr, &ptl);
    pteval = ptep_get(pte);

    // 恢复到原来的 PTE
    set_pte_at(vma->vm_mm, addr, pte, dst_pte);
    pte_unmap_unlock(pte, ptl);

    return true;
}
```

## 5. MIGRATE_TYPES 迁移类型

```c
// mm/migrate.c
enum migrate_mode {
    MIGRATE_ASYNC = 0,        // 异步迁移，不等待
    MIGRATE_SYNC_LIGHT,      // 轻量同步
    MIGRATE_SYNC,            // 完全同步
};

enum migrate_reason {
    MR_MEMORY_FAILURE,        // 内存错误
    MR_GIVE_DEMAND_PAGE,     // 按需页面
    MR_BALLOON_COMPACTION,   // Balloon 压缩
    MR_COMPACTION,           // Compaction
    MR_MEMPOLICY_MBIND,      // 内存策略
    MR_CMA,                  // CMA 分配
};
```

## 6. cma_alloc 集成

### 6.1 CMA 迁移
**文件**: `mm/cma.c`

CMA (Contiguous Memory Allocator) 用于分配连续大块内存，页面迁移是其核心机制。

### 6.2 migrate_to_from_cma
**文件**: `mm/migrate.c:2100-2150`

```c
// CMA 页面迁移回调
static int migrate_to_from_cma(struct page *page, void *private)
{
    struct migration_control *mc = private;
    struct folio *dst;

    // 分配新页面
    dst = alloc_folio(GFP_KERNEL, 0);
    if (!dst)
        return -ENOMEM;

    // 迁移内容
    return migrate_folio(page_folio(page), dst, MIGRATE_SYNC);
}
```

## 7. migrate_vma 机制

### 7.1 migrate_vma
**文件**: `mm/migrate.c:2300-2400`

```c
int migrate_vma(struct migrate_vma_ops *ops, struct vm_area_struct *vma,
                unsigned long *src, unsigned long *dst, unsigned long start,
                unsigned long end, void *private)
{
    struct migrate_vma m = {
        .vma = vma,
        .src = src,
        .dst = dst,
        .start = start,
        .end = end,
        .ops = ops,
        .private = private,
    };

    // 锁定页面
    migrate_vma_lock_pages(&m);

    // 执行迁移
    ops->migratepage(&m, src, dst);

    // 更新页表
    migrate_vma_update_pages(&m);

    // 解锁
    migrate_vma_unlock_pages(&m);

    return 0;
}
```

## 8. 锁依赖关系

```
migrate_pages()
    ↓
folio_lock(src) → folio_lock(dst)
    ↓
migrate_folio_prepare()
    ↓
migrate_folio_copy()
    ↓
folio_unlock(dst) → folio_unlock(src)
    ↓
remove_migration_ptes()
    ↓
rmap_walk_locked()
    ↓
remove_migration_pte()
    ↓
pte_offset_map_lock() → set_pte_at() → pte_unmap_unlock()
```

## 9. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| migrate_pages | mm/migrate.c | 2072 |
| migrate_pages_batch | mm/migrate.c | 1869 |
| migrate_folio | mm/migrate.c | 1593 |
| migrate_folio_move | mm/migrate.c | 1530 |
| migrate_folio_copy | mm/migrate.c | 1400 |
| remove_migration_ptes | mm/migrate.c | 1200 |
| remove_migration_pte | mm/migrate.c | 1150 |
| migrate_vma | mm/migrate.c | 2300 |
