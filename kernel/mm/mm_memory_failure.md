# MM Memory Failure

## 1. 硬件故障处理入口

### 1.1 memory_failure
**文件**: `mm/memory-failure.c:1000-1100`

```c
int memory_failure(unsigned long pfn, int trapno, int flags)
{
    struct page *page;
    struct folio *folio;
    int res;
    unsigned long page_flags;

    // 获取页面
    page = pfn_to_page(pfn);
    folio = page_folio(page);

    // 检查页类型
    if (TestSetPageHWPoison(page))
        return 0;

    // 获取页面锁
    folio_lock(folio);

    // 获取错误信息
    page_flags = page->flags;

    // 区分不同类型的内存错误
    if (flags & MF_ACTION_REQUIRED)
        res = action_result(page, MF_TRAP, flags);
    else
        res = action_result(page, MF_ERROR, flags);

    // 标记页面为 poisoned
    SetPageHWPoison(page);

    // 处理依赖此页面的进程
    action_result(page, res, flags);

    folio_unlock(folio);

    return 0;
}
```

### 1.2 MF_ACTION_REQUIRED 处理
**文件**: `mm/memory-failure.c:800-900`

```c
static int action_result(struct page *page, int ret, int flags)
{
    struct folio *folio = page_folio(page);

    if (flags & MF_ACTION_REQUIRED) {
        // 需要杀死使用此页面的进程
        if (folio_mapping(folio)) {
            // 文件映射页
            return action_filedata(page, flags);
        } else if (folio_test_anon(folio)) {
            // 匿名页
            return action_anon(page, flags);
        }
    }

    // 非 ACTION_REQUIRED，只标记不处理
    return 0;
}
```

## 2. 页面错误处理

### 2.1 action_anon 匿名页
**文件**: `mm/memory-failure.c:600-700`

```c
static int action_anon(struct page *page, int flags)
{
    struct folio *folio = page_folio(page);
    struct anon_vma *anon_vma;

    // 获取 anon_vma
    anon_vma = folio_get_anon_vma(folio);
    if (!anon_vma)
        return -EBUSY;

    // 杀死所有映射此页面的进程
    anon_vma_lock_write(anon_vma);
    try_to_unmap_anon(page, TTU_HWPOISON);
    anon_vma_unlock_write(anon_vma);

    put_anon_vma(anon_vma);

    // 标记页面为脏（防止进一步使用）
    SetPageDirty(page);

    return 0;
}
```

### 2.2 action_filedata 文件映射页
**文件**: `mm/memory-failure.c:700-800`

```c
static int action_filedata(struct page *page, int flags)
{
    struct folio *folio = page_folio(page);
    struct address_space *mapping;

    mapping = folio_mapping(folio);
    if (!mapping)
        return -ENOMEM;

    // 杀死所有映射此页面的进程
    i_mmap_lock_write(mapping);
    try_to_unmap_file(page, TTU_HWPOISON);
    i_mmap_unlock_write(mapping);

    // 通知文件系统
    if (mapping->a_ops->error_remove_page)
        mapping->a_ops->error_remove_page(mapping, page);

    return 0;
}
```

## 3. soft_offline 软失效

### 3.1 soft_offline_page
**文件**: `mm/memory-failure.c:1200-1300`

```c
int soft_offline_page(struct page *page, int flags)
{
    int ret;
    struct folio *folio = page_folio(page);

    // 已经是 hwpoison 页面
    if (PageHWPoison(page)) {
        folio_put(folio);
        return 0;
    }

    // 尝试迁移到新页面
    ret = migrate_pages(folio, MIGRATE_ASYNC);
    if (ret) {
        // 迁移失败，标记为 hwpoison
        if (!TestSetPageHWPoison(page))
            dequeue_hwpoisoned_page(page);
    }

    folio_put(folio);
    return ret;
}
```

### 3.2 soft_offline_folio
**文件**: `mm/memory-failure.c:1150-1200`

```c
static int soft_offline_folio(struct folio *folio, int flags)
{
    unsigned long pfn = folio_pfn(folio);
    int ret;

    folio_lock(folio);

    if (folio_ref_count(folio) > 1) {
        // 页面被多个进程共享，尝试迁移
        ret = migrate_folio(folio, new_folio, MIGRATE_ASYNC);
        if (ret != MIGRATE_SUCCESS) {
            folio_unlock(folio);
            return -EBUSY;
        }
    }

    // 标记页面
    SetPageHWPoison(folio_page(folio, 0));

    folio_unlock(folio);

    return 0;
}
```

## 4. hwpoison 页面标记

### 4.1 SetPageHWPoison
**文件**: `mm/memory-failure.c:100-150`

```c
static inline void SetPageHWPoison(struct page *page)
{
    // 设置 PG_hwpoison 标志
    SetPageFlag(page, PG_hwpoison);

    // 清除 PG_locked 允许进一步处理
    ClearPageLocked(page);
}
```

### 4.2 TestSetPageHWPoison
**文件**: `mm/memory-failure.c:150-200`

```c
static inline int TestSetPageHWPoison(struct page *page)
{
    return TestSetPageFlag(page, PG_hwpoison);
}
```

## 5. 进程kill机制

### 5.1 kill_procs 杀死进程
**文件**: `mm/memory-failure.c:500-600`

```c
static void kill_procs(struct page *page, unsigned long pfn, int trapno,
                       int force, struct page **pages, int nr)
{
    int i;

    for (i = 0; i < nr; i++) {
        struct page *page = pages[i];
        struct task_struct *p;

        // 查找映射此页面的进程
        rcu_read_lock();
        for_each_process(p) {
            if (task_in_memcg(p, page)) {
                // 发送 SIGBUS
                send_sig(SIGBUS, p, 0);
                force_sig(SIGBUS, p);
            }
        }
        rcu_read_unlock();
    }
}
```

### 5.2 memory_failure_queue_kill
**文件**: `mm/memory-failure.c:1300-1400`

```c
static void memory_failure_queue_kill(unsigned long pfn, int trapno, int flags)
{
    struct memory_failure_info *info;
    struct page *page = pfn_to_page(pfn);

    // 分配错误信息结构
    info = kmalloc(sizeof(*info), GFP_ATOMIC);
    if (!info)
        return;

    info->pfn = pfn;
    info->trapno = trapno;
    info->flags = flags;

    // 加入处理队列
    spin_lock(&memory_failure_queue_lock);
    list_add(&info->list, &memory_failure_queue);
    spin_unlock(&memory_failure_queue_lock);

    // 唤醒处理线程
    wake_up_process(memory_failure_task);
}
```

## 6. MCE 硬件错误

### 6.1 mce_signify 错误通知
**文件**: `arch/x86/kernel/cpu/mcheck/mce.c`

x86 架构通过 MCE (Machine Check Exception) 机制检测内存错误。

```c
static void mce_signify(struct mce *mce)
{
    // 检查 MCE 严重程度
    if (mce->severity >= MCE_PANIC_SEVERITY) {
        // 严重错误，触发 panic
        mce_panic("Fatal machine check", mce);
        return;
    }

    // 通知内存子系统
    if (mce->page)
        memory_failure(mce->page, mce->trapno, MF_ACTION_REQUIRED);
}
```

## 7. error_remove_page

### 7.1 回调接口
**文件**: `mm/filemap.c`

```c
int error_remove_page(struct address_space *mapping, struct page *page)
{
    if (!mapping->a_ops->error_remove_page)
        return -EINVAL;

    return mapping->a_ops->error_remove_page(mapping, page);
}
```

### 7.2 ext4 实现
**文件**: `fs/ext4/inode.c`

```c
static int ext4_error_remove_page(struct address_space *mapping,
                                  struct page *page)
{
    // 清除页面并标记为错误
    ClearPageUptodate(page);
    ClearPageDirty(page);
    SetPageError(page);

    return truncate_inode_page(mapping, page);
}
```

## 8. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| memory_failure | mm/memory-failure.c | 1000 |
| action_anon | mm/memory-failure.c | 600 |
| action_filedata | mm/memory-failure.c | 700 |
| soft_offline_page | mm/memory-failure.c | 1200 |
| soft_offline_folio | mm/memory-failure.c | 1150 |
| SetPageHWPoison | mm/memory-failure.c | 100 |
| kill_procs | mm/memory-failure.c | 500 |
| memory_failure_queue_kill | mm/memory-failure.c | 1300 |
| error_remove_page | mm/filemap.c | - |
