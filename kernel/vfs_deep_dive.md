# Linux VFS (Virtual File System) 深度架构分析 v2

## 1. 概述

VFS（Virtual File System）是 Linux 内核的核心子系统，为用户空间程序提供统一的文件系统接口。本文档是第二轮深度分析，重点关注 RCU 并发机制、锁协议、算法复杂度证明、地址空间操作等核心实现细节。

**核心数据结构：**
- `struct inode` - 索引节点（文件元数据）
- `struct dentry` - 目录项（路径名缓存）
- `struct file` - 打开的文件描述符
- `struct super_block` - 超级块（文件系统元数据）
- `struct address_space` - 地址空间（页缓存）

## 2. RCU 路径查找机制

### 2.1 RCU 概述与内存屏障

Linux VFS 使用 RCU（Read-Copy-Update）优化路径查找，避免锁竞争：

```c
/*
 * RCU 查找的关键特性：
 * 1. 读者无锁，不阻塞
 * 2. 写者复制修改，避免锁
 * 3. 延迟释放旧数据（grace period）
 */
```

**序列计数器验证（Sequence Counter）：**

```c
/*
 * dentry->d_seq 是一个序列计数器，每次修改 dentry 时递增
 * 读取者通过检查序列号是否变化来检测并发修改
 *
 * 读取模式：
 *   do {
 *       seq = read_seqcount_begin(&dentry->d_seq);
 *       // 读取 dentry 字段
 *   } while (read_seqcount_retry(&dentry->d_seq, seq));
 *
 * 写者模式（修改 dentry 时）：
 *   write_seqcount_begin(&dentry->d_seq);
 *   // 修改字段
 *   write_seqcount_end(&dentry->d_seq);
 */
```

### 2.2 __d_lookup_rcu 深入实现

```c
/**
 * __d_lookup_rcu - RCU 模式下的 dentry 查找
 * @parent: 父目录 dentry
 * @name: 要查找的名字
 * @seq: 返回的序列号
 *
 * 返回：找到返回 dentry 指针，未找到返回 NULL
 * 注意：返回的 dentry 可能正在被删除，调用者必须验证
 */
struct dentry *__d_lookup_rcu(const struct dentry *parent,
                              const struct qstr *name,
                              unsigned *seq)
{
    unsigned int hash = name->hash;
    struct hlist_bl_head *b = d_hash(hashlen_hash(parent->d_name.hash_len + hash));
    struct hlist_bl_node *n;

    hlist_bl_for_each_entry_rcu(dentry, n, b, d_hash) {
        /* 序列号验证：检测并发修改 */
        *seq = read_seqcount_begin(&dentry->d_seq);

        /* 哈希长度验证（快速排除） */
        if (dentry->d_name.hash_len != name->hash_len)
            continue;

        /* 名称匹配 */
        if (dentry_cmp(dentry, name->name, name->len))
            continue;

        /* 父目录验证 */
        if (READ_ONCE(dentry->d_parent) != parent)
            continue;

        /* 返回前再次验证序列号（检测 lookup 期间的修改） */
        if (read_seqcount_retry(&dentry->d_seq, *seq))
            continue;

        return dentry;
    }
    return NULL;
}
```

### 2.3 try_to_unlazy 机制

当 RCU 查找失败或需要修改时，切换到引用模式：

```c
/**
 * try_to_unlazy - 从 RCU 模式转换到引用模式
 * @nd: nameidata
 *
 * 转换过程：
 * 1. legitimize_links() - 使符号链接目标有效
 * 2. legitimize_path() - 使当前路径有效
 * 3. legitimize_root() - 使根目录有效
 * 4. leave_rcu() - 退出 RCU 模式
 */
static bool try_to_unlazy(struct nameidata *nd)
{
    struct dentry *parent = nd->path.dentry;

    /* 检查是否是 cached 查找 */
    if (unlikely(nd->flags & LOOKUP_CACHED)) {
        drop_links(nd);
        nd->depth = 0;
        goto out1;
    }

    /* 使符号链接链接目标有效 */
    if (unlikely(nd->depth && !legitimize_links(nd)))
        goto out1;

    /* 使当前路径有效 */
    if (unlikely(!legitimize_path(nd, &nd->path, nd->seq)))
        goto out;

    /* 使根目录有效 */
    if (unlikely(!legitimize_root(nd)))
        goto out;

    /* 退出 RCU 模式 */
    leave_rcu(nd);
    return true;

out1:
    nd->path.mnt = NULL;
    nd->path.dentry = NULL;
out:
    leave_rcu(nd);
    return false;
}
```

### 2.4 并发安全性证明

**定理**：RCU 路径查找返回正确结果或报告失败。

**证明**：
1. **无锁读取**：读者不使用锁，仅依赖序列计数器验证
2. **序列号检测**：若查找期间有写者修改，序列号会变化
3. **重试机制**：检测到并发修改时返回错误，调用者降级到慢速路径
4. **内存屏障**：write_seqcount_* 包含完整内存屏障，保证修改可见性

## 3. Dentry 缓存深入分析

### 3.1 Dentry 哈希算法

```c
/**
 * d_hash - 计算 dentry 在哈希表中的位置
 * @hashlen: 组合的 hash 和 length
 *
 * 哈希函数设计：
 * - 使用 hashlen 而非单独的 hash 提高缓存命中率
 * - 移位操作避免取模（2^n 哈希表大小）
 * - 父目录地址作为 salt 防止哈希碰撞攻击
 */
static inline struct hlist_bl_head *d_hash(unsigned long hashlen)
{
    return dentry_hashtable +
        runtime_const_shift_right_32(hashlen, d_hash_shift);
}

/*
 * hashlen 计算：
 * hashlen = (hash << 32) | len
 * 组合存储减少内存访问
 */
static inline unsigned long hashlen_string(const struct dentry *base,
                                           const char *name)
{
    unsigned long hash = init_name_hash(base);
    while (*name)
        hash = partial_name_hash(*name++, hash);
    return hashlen_create(hash, name - base);
}
```

### 3.2 Dentry 分配与初始化

```c
/**
 * __d_alloc - 分配 dentry
 * @sb: 超级块
 * @name: 文件名
 *
 * 分配策略：
 * 1. 从 per-sb LRU cache 分配（减少 NUMA 跨节点访问）
 * 2. 短文件名使用内联存储（DNAME_INLINE_LEN）
 * 3. 长文件名使用外部 kmalloc 分配
 */
static struct dentry *__d_alloc(struct super_block *sb, const struct qstr *name)
{
    struct dentry *dentry;
    char *dname;

    /* 从 LRU cache 分配，优先本地节点 */
    dentry = kmem_cache_alloc_lru(dentry_cache, &sb->s_dentry_lru,
                                  GFP_KERNEL);
    if (!dentry)
        return NULL;

    /* 初始化内联名称空间 */
    dentry->d_shortname.string[DNAME_INLINE_LEN-1] = 0;

    if (unlikely(!name)) {
        name = &slash_name;
        dname = dentry->d_shortname.string;
    } else if (name->len > DNAME_INLINE_LEN-1) {
        /* 长文件名：外部分配 */
        size_t size = offsetof(struct external_name, name[1]);
        struct external_name *p = kmalloc(size + name->len,
                                          GFP_KERNEL_ACCOUNT | __GFP_RECLAIMABLE);
        if (!p) {
            kmem_cache_free(dentry_cache, dentry);
            return NULL;
        }
        atomic_set(&p->count, 1);
        dname = p->name;
    } else {
        dname = dentry->d_shortname.string;
    }

    /* 复制名称 */
    dentry->__d_name.len = name->len;
    dentry->__d_name.hash = name->hash;
    memcpy(dname, name->name, name->len);
    dname[name->len] = 0;

    /* 存储指针（释放屏障） */
    smp_store_release(&dentry->__d_name.name, dname);

    /* 初始化锁和序列号 */
    dentry->d_flags = 0;
    lockref_init(&dentry->d_lockref);
    seqcount_spinlock_init(&dentry->d_seq, &dentry->d_lock);
    dentry->d_inode = NULL;
    dentry->d_parent = dentry;
    dentry->d_sb = sb;
    dentry->d_op = sb->__s_d_op;

    /* 初始化链表 */
    INIT_HLIST_BL_NODE(&dentry->d_hash);
    INIT_LIST_HEAD(&dentry->d_lru);
    INIT_HLIST_HEAD(&dentry->d_children);
    INIT_HLIST_NODE(&dentry->d_u.d_alias);
    INIT_HLIST_NODE(&dentry->d_sib);

    /* 文件系统特定初始化 */
    if (dentry->d_op && dentry->d_op->d_init) {
        int err = dentry->d_op->d_init(dentry);
        if (err) {
            if (dname_external(dentry))
                kfree(external_name(dentry));
            kmem_cache_free(dentry_cache, dentry);
            return NULL;
        }
    }

    /* 更新统计 */
    this_cpu_inc(nr_dentry);

    return dentry;
}
```

### 3.3 Dentry 回收与 LRU

```c
/**
 * __dentry_kill - 删除 dentry
 * @dentry: 要删除的 dentry
 *
 * 删除协议：
 * 1. 从父目录移除
 * 2. 从哈希表移除
 * 3. 从 LRU 移除
 * 4. 减少引用计数
 */
static void __dentry_kill(struct dentry *dentry)
{
    struct dentry *parent = dentry->d_parent;

    /* 获取锁顺序：父 -> 子 */
    spin_lock(&parent->d_lock);
    spin_lock_nested(&dentry->d_lock, DENTRY_D_LOCK_NESTED);

    /* 从 LRU 移除 */
    d_lru_del(dentry);

    /* 从哈希表移除 */
    hlist_bl_del(&dentry->d_hash);

    /* 减少引用计数 */
    lockref_put(&dentry->d_lockref);

    spin_unlock(&dentry->d_lock);
    spin_unlock(&parent->d_lock);

    /* 释放引用 */
    dput(dentry);
}
```

### 3.4 Dentry 锁层级

```
锁顺序（从高到低）：
┌──────────────────────────────────────────────────────────────┐
│ 1. inode->i_lock (保护 inode 字段)                           │
│    ↓                                                          │
│ 2. dentry->d_lock (保护 dentry 字段)                         │
│    ↓                                                          │
│ 3. sb->s_dentry_lru_lock (保护 LRU 列表)                    │
│    ↓                                                          │
│ 4. dcache_hash_bucket lock (保护哈希桶)                      │
└──────────────────────────────────────────────────────────────┘
```

注意：如果存在祖先关系
dentry->d_parent->...->d_parent->d_lock
    ↓
    dentry->d_lock

## 4. Inode 缓存深入分析

### 4.1 Inode 哈希表

```c
static unsigned int i_hash_mask __ro_after_init;
static unsigned int i_hash_shift __ro_after_init;
static struct hlist_head *inode_hashtable __ro_after_init;
static __cacheline_aligned_in_smp DEFINE_SPINLOCK(inode_hash_lock);

/**
 * hash - 计算 inode 哈希值
 * @sb: 超级块
 * @hashval: inode 号
 *
 * 哈希函数：使用 GOLDEN_RATIO_PRIME 混合哈希
 */
static unsigned long hash(struct super_block *sb, unsigned long hashval)
{
    unsigned long tmp;

    /* 第一步：混合 super_block 指针和 inode 号 */
    tmp = (hashval * (unsigned long)sb) ^ (GOLDEN_RATIO_PRIME + hashval) /
            L1_CACHE_BYTES;

    /* 第二步：最终混合 */
    tmp = tmp ^ ((tmp ^ GOLDEN_RATIO_PRIME) >> i_hash_shift);

    return tmp & i_hash_mask;
}

/**
 * __insert_inode_hash - 将 inode 加入哈希表
 * @inode: inode
 * @hashval: inode 号
 */
void __insert_inode_hash(struct inode *inode, unsigned long hashval)
{
    struct hlist_head *b = inode_hashtable + hash(inode->i_sb, hashval);

    spin_lock(&inode_hash_lock);
    spin_lock(&inode->i_lock);
    hlist_add_head_rcu(&inode->i_hash, b);
    spin_unlock(&inode->i_lock);
    spin_unlock(&inode_hash_lock);
}
```

### 4.2 Inode 分配与初始化

```c
/**
 * inode_init_once - 初始化 slab 缓存中的 inode
 * @inode: inode 指针
 *
 * 仅初始化幂等字段，允许重复初始化
 */
void inode_init_once(struct inode *inode)
{
    memset(inode, 0, sizeof(*inode));

    /* 初始化哈希节点 */
    INIT_HLIST_NODE(&inode->i_hash);

    /* 初始化链表 */
    INIT_LIST_HEAD(&inode->i_devices);
    INIT_LIST_HEAD(&inode->i_io_list);
    INIT_LIST_HEAD(&inode->i_wb_list);
    INIT_LIST_HEAD(&inode->i_lru);
    INIT_LIST_HEAD(&inode->i_sb_list);

    /* 初始化地址空间 */
    __address_space_init_once(&inode->i_data);

    /* 初始化大小顺序锁 */
    i_size_ordered_init(inode);
}

/**
 * address_space_init_once - 初始化地址空间
 * @mapping: 地址空间
 */
static void __address_space_init_once(struct address_space *mapping)
{
    /* 初始化 XArray，支持中断锁和账户 */
    xa_init_flags(&mapping->i_pages, XA_FLAGS_LOCK_IRQ | XA_FLAGS_ACCOUNT);

    /* 初始化映射锁 */
    init_rwsem(&mapping->i_mmap_rwsem);

    /* 初始化私有数据链表 */
    INIT_LIST_HEAD(&mapping->i_private_list);
    spin_lock_init(&mapping->i_private_lock);

    /* 初始化红黑树 */
    mapping->i_mmap = RB_ROOT_CACHED;
}
```

### 4.3 Inode LRU 回收

```c
/**
 * inode_lru_list_add - 将 inode 加入 LRU
 * @inode: inode
 *
 * 条件：inode 必须满足以下所有条件才能加入 LRU
 * 1. 不脏（无 I_DIRTY_* 标志）
 * 2. 不在释放中（无 I_FREEING/I_WILL_FREE）
 * 3. 引用计数为 0
 * 4. 超级块活跃（SB_ACTIVE）
 * 5. 可收缩（mapping_shrinkable）
 */
static void __inode_lru_list_add(struct inode *inode, bool rotate)
{
    lockdep_assert_held(&inode->i_lock);

    /* 检查 inode 状态 */
    if (inode_state_read(inode) &
        (I_DIRTY_ALL | I_SYNC | I_FREEING | I_WILL_FREE))
        return;

    /* 检查引用计数 */
    if (icount_read(inode))
        return;

    /* 检查超级块活跃状态 */
    if (!(inode->i_sb->s_flags & SB_ACTIVE))
        return;

    /* 检查是否可收缩 */
    if (!mapping_shrinkable(&inode->i_data))
        return;

    /* 加入 LRU 并更新统计 */
    if (list_lru_add_obj(&inode->i_sb->s_inode_lru, &inode->i_lru))
        this_cpu_inc(nr_unused);
    else if (rotate)
        inode_state_set(inode, I_REFERENCED);
}
```

### 4.4 Inode 引用计数管理

```c
/**
 * ihold - 增加 inode 引用
 * @inode: inode
 *
 * 警告：如果引用计数已经是 0，会触发警告
 * 这是故意的，用于检测使用已释放 inode 的 bug
 */
void ihold(struct inode *inode)
{
    WARN_ON(atomic_inc_return(&inode->i_count) < 2);
}

/**
 * iput - 释放 inode 引用
 * @inode: inode
 *
 * 释放协议：
 * 1. 减少引用计数
 * 2. 如果计数为 0：
 *    a. 从 LRU 移除（如果不脏）
 *    b. 调用文件系统销毁回调
 *    c. 释放到 slab
 */
void iput(struct inode *inode)
{
    if (atomic_dec_and_lock(&inode->i_count, &inode->i_lock)) {
        /* 从 LRU 移除 */
        if (!(inode->i_state & (I_DIRTY_ALL | I_FREEING | I_CLEAR)))
            inode_lru_del(inode);

        /* 检查是否可以释放 */
        if (inode->i_nlink)
            goto out;

        /* 标记正在释放 */
        inode->i_state |= I_FREEING;

        /* 调用文件系统钩子 */
        if (inode->i_op->destroy_inode)
            inode->i_op->destroy_inode(inode);
        else
            inode_free(inode);
        return;
    }
out:
    spin_unlock(&inode->i_lock);
}
```

## 5. 地址空间与页缓存

### 5.1 address_space 结构

```c
/**
 * struct address_space - 页缓存管理结构
 * @i_pages: XArray 存储页面
 * @i_mmap: 红黑树管理映射的 VMA
 * @i_mmap_rwsem: 保护 i_mmap 的读写信号量
 * @i_mmap_lock: 保护 i_mmap 的自旋锁
 * @i_private_data: 文件系统私有数据
 * @i_private_lock: 保护私有数据
 * @wb: 写回控制
 */
struct address_space {
    XArray(i_pages);                      /* 页面存储 */
    struct rw_semaphore i_mmap_rwsem;    /* mmap 读写锁 */
    spinlock_t i_mmap_lock;               /* mmap 自旋锁 */
    struct rb_root_cached i_mmap;        /* 映射的红黑树 */
    struct list_head i_private_list;     /* 私有数据链表 */
    spinlock_t i_private_lock;            /* 私有数据锁 */
    const struct address_space_operations *a_ops; /* 操作函数集 */
    unsigned int i_mapping_flags;         /* 标志 */
    unsigned long truncate_offset;        /* 截断偏移 */
    atomic_t i_writeback_count;          /* 写回计数 */
    struct rw_hint i_write_hint;         /* 写提示 */
    atomic_t i_read_hint;                /* 读提示 */
} __randomize_layout;
```

### 5.2 XArray 页表

```c
/**
 * 页缓存查找（使用 XArray）
 *
 * 查找流程：
 * 1. xa_load() 在 XArray 中查找页
 * 2. 如果找到，检查页状态
 * 3. 如果未找到，返回 NULL
 */
struct page *find_get_page(struct address_space *mapping, unsigned long index)
{
    XArray *xa = &mapping->i_pages;
    Page *page;

    rcu_read_lock();
    page = xa_load(xa, index);
    if (page && !xa_is_value(page)) {
        if (page_ref_inc_not_zero(page))
            get_page(page);
        else
            page = NULL;
    }
    rcu_read_unlock();

    return page;
}

/**
 * add_to_page_cache_locked - 将页加入页缓存
 * @page: 页
 * @mapping: 地址空间
 * @index: 索引
 * @gfp: 分配标志
 */
int add_to_page_cache_locked(struct page *page,
                             struct address_space *mapping,
                             unsigned long index, gfp_t gfp)
{
    XArray *xa = &mapping->i_pages;
    int error;

    error = xa_err(xa_store(xa, index, page, gfp));
    if (!error)
        page->mapping = mapping;
    return error;
}
```

### 5.3 写回机制

```c
/**
 * write_inode - 写回 inode
 * @inode: inode
 * @wbc: 写回控制
 *
 * 写回触发路径：
 * 1. 显式 sync/fsync
 * 2. 定期写回（flusher 线程）
 * 3. 内存压力回收
 */
int write_inode(struct inode *inode, struct writeback_control *wbc)
{
    int err;

    if (inode->i_sb->s_op->write_inode) {
        err = inode->i_sb->s_op->write_inode(inode, wbc);
        if (wbc->sync_mode == WB_SYNC_ALL)
            err = 0;
    }
    return err;
}

/**
 * inode_forget - 忘记 inode 的脏页
 * @inode: inode
 *
 * 在某些文件系统操作（如 truncate）时调用
 */
void inode_forget(struct inode *inode)
{
    struct address_space *mapping = inode->i_mapping;

    spin_lock(&mapping->i_mmap_lock);
    /* 清除所有私有映射 */
    unmap_mapping_pages(mapping, 0, LLONG_MAX, 0);
    spin_unlock(&mapping->i_mmap_lock);
}
```

## 6. 路径查找算法详解

### 6.1 lookup_fast 快速路径

```c
/**
 * lookup_fast - RCU 快速查找
 * @nd: nameidata
 *
 * 快速路径：RCU 无锁查找 + 序列号验证
 *
 * 返回值：
 * - 成功：dentry 指针（RCU 模式或引用模式）
 * - 未找到：NULL
 * - 错误：ERR_PTR
 */
static struct dentry *lookup_fast(struct nameidata *nd)
{
    struct dentry *dentry, *parent = nd->path.dentry;
    int status = 1;

    if (nd->flags & LOOKUP_RCU) {
        /* RCU 模式 */
        dentry = __d_lookup_rcu(parent, &nd->last, &nd->next_seq);
        if (unlikely(!dentry)) {
            if (!try_to_unlazy(nd))
                return ERR_PTR(-ECHILD);
            return NULL;
        }

        /* 验证父目录未被修改 */
        if (read_seqcount_retry(&parent->d_seq, nd->seq))
            return ERR_PTR(-ECHILD);

        /* 文件系统特定验证 */
        status = d_revalidate(nd->inode, &nd->last, dentry, nd->flags);
        if (likely(status > 0))
            return dentry;

        /* 降级到引用模式 */
        if (!try_to_unlazy_next(nd, dentry))
            return ERR_PTR(-ECHILD);
    } else {
        /* 引用模式 */
        dentry = __d_lookup(parent, &nd->last);
        if (unlikely(!dentry))
            return NULL;
        status = d_revalidate(nd->inode, &nd->last, dentry, nd->flags);
    }

    /* 处理无效或错误 */
    if (unlikely(status <= 0)) {
        if (!status)
            d_invalidate(dentry);
        dput(dentry);
        return ERR_PTR(status);
    }
    return dentry;
}
```

### 6.2 __lookup_slow 慢速路径

```c
/**
 * __lookup_slow - 慢速查找（需要加锁）
 * @name: 要查找的名字
 * @dir: 父目录
 * @flags: 查找标志
 *
 * 触发条件：
 * 1. RCU 查找失败
 * 2. d_revalidate 返回 <= 0
 * 3. 并发创建/删除
 */
static struct dentry *__lookup_slow(const struct qstr *name,
                                    struct dentry *dir,
                                    unsigned int flags)
{
    struct dentry *dentry, *old;
    struct inode *inode = dir->d_inode;
    DECLARE_WAIT_QUEUE_HEAD_ONSTACK(wq);

    /* 目录已删除 */
    if (unlikely(IS_DEADDIR(inode)))
        return ERR_PTR(-ENOENT);

again:
    /* 分配并行查找的 dentry */
    dentry = d_alloc_parallel(dir, name, &wq);
    if (IS_ERR(dentry))
        return dentry;

    /* 检查是否正在被其他查找创建 */
    if (unlikely(!d_in_lookup(dentry))) {
        /* 已有 dentry，验证 */
        int error = d_revalidate(inode, name, dentry, flags);
        if (unlikely(error <= 0)) {
            if (!error) {
                d_invalidate(dentry);
                dput(dentry);
                goto again;
            }
            dput(dentry);
            dentry = ERR_PTR(error);
        }
    } else {
        /* 正在被创建，等待 */
        old = inode->i_op->lookup(inode, dentry, flags);
        d_lookup_done(dentry);
        if (unlikely(old)) {
            dput(dentry);
            dentry = old;
        }
    }
    return dentry;
}
```

## 7. 文件系统锁协议

### 7.1 完整锁层次

```
┌────────────────────────────────────────────────────────────────┐
│                     VFS 锁层次（从高到低）                       │
├────────────────────────────────────────────────────────────────┤
│ 1. namespace_sem (rw_semaphore)                                │
│    保护：挂载命名空间修改                                        │
│                                                                │
│ 2. sb->s_umount (rw_semaphore)                                 │
│    保护：超级块卸载                                              │
│                                                                │
│ 3. inode->i_rwsem (rw_semaphore)                               │
│    保护：inode 操作（创建/删除/重命名）                          │
│                                                                │
│ 4. sb->s_inode_list_lock (spinlock)                            │
│    保护：inode 链表                                             │
│                                                                │
│ 5. inode->i_lock (spinlock)                                     │
│    保护：inode 状态、哈希、IO 列表                              │
│                                                                │
│ 6. dentry->d_lock (spinlock)                                   │
│    保护：dentry 字段                                            │
│                                                                │
│ 7. sb->s_dentry_lru_lock (spinlock)                            │
│    保护：dentry LRU 列表                                        │
│                                                                │
│ 8. dcache_hash_bucket lock (spinlock)                          │
│    保护：dentry 哈希桶                                          │
└────────────────────────────────────────────────────────────────┘
```

### 7.2 inode 互斥锁子类

```c
/**
 * inode 互斥锁子类，用于避免死锁
 */
enum inode_i_mutex_lock_class {
    I_MUTEX_NORMAL,      // 普通文件操作
    I_MUTEX_PARENT,      // 锁定父目录（用于创建/删除）
    I_MUTEX_CHILD,       // 锁定子项（用于重命名）
    I_MUTEX_XATTR,       // 扩展属性操作
    I_MUTEX_NONDIR2,     // 非目录重命名
    I_MUTEX_PARENT2,     // 双目录重命名
};

/**
 * inode_lock_nested - 带子类的 inode 锁定
 */
static inline void inode_lock_nested(struct inode *inode, unsigned subclass)
{
    down_write_nested(&inode->i_rwsem, subclass);
}
```

### 7.3 rename_lock 序列锁

```c
/**
 * rename_lock - 保护重命名操作
 *
 * 用于避免重命名和查找之间的竞争
 * 不是完整的锁，而是一个序列锁
 * 读者通过序列号检测并发修改
 */
DEFINE_SEQLOCK(rename_lock);

/* 使用方式 */
unsigned int seq;
do {
    seq = read_seqbegin(&rename_lock);
    // 执行需要保护的查找
} while (read_seqretry(&rename_lock, seq));
```

## 8. Super Block 操作详解

### 8.1 超级块分配

```c
/**
 * sget - 获取或创建超级块
 * @type: 文件系统类型
 * @test: 测试回调
 * @set: 设置回调
 * @flags: 挂载标志
 * @data: 私有数据
 *
 * 返回：超级块指针
 */
struct super_block *sget(struct file_system_type *type,
                        int (*test)(struct super_block *, void *),
                        int (*set)(struct super_block *, void *),
                        int flags, void *data)
{
    struct super_block *sb, *p;

    /* 查找已存在的超级块 */
    spin_lock(&sb_lock);
    list_for_each_entry(p, &type->fs_supers, s_instance) {
        if (test(p, data)) {
            if (flags & MS_SHARED)
                get_group_info(p->s_info);
            else
                get_filesystem(p->s_type);
            spin_unlock(&sb_lock);
            return p;
        }
    }
    spin_unlock(&sb_lock);

    /* 分配新超级块 */
    sb = alloc_super(type, flags);
    if (sb) {
        sb->s_id = kasprintf(GFP_KERNEL, "%s-%d", type->name,
                            atomic_inc_return(&sb_unique));

        /* 调用文件系统初始化 */
        down_write(&sb->s_umount);
        error = set(sb, data);
        if (error) {
            up_write(&sb->s_umount);
            goto fail;
        }

        /* 加入全局链表 */
        spin_lock(&sb_lock);
        list_add_tail(&sb->s_list, &all_super_blocks);
        spin_unlock(&sb_lock);
    }
    return sb;
fail:
    kfree(sb->s_id);
    kmem_cache_free(supers_cache, sb);
    return ERR_PTR(error);
}
```

### 8.2 超级块操作函数集

```c
struct super_operations {
    /* inode 分配/销毁 */
    struct inode *(*alloc_inode)(struct super_block *sb);
    void (*destroy_inode)(struct inode *);
    void (*free_inode)(struct inode *);

    /* inode 脏写回 */
    void (*dirty_inode)(struct inode *, int flags);
    int (*write_inode)(struct inode *, struct writeback_control *wbc);

    /* 超级块操作 */
    int (*sync_fs)(struct super_block *sb, int wait);
    int (*freeze_super)(struct super_block *sb);
    int (*freeze_fs)(struct super_block *sb);
    int (*thaw_super)(struct super_block *sb);
    int (*unfreeze_fs)(struct super_block *sb);

    /* 挂载/卸载 */
    void (*put_super)(struct super_block *);
    int (*remount_fs)(struct super_block *, int *, char *);

    /* statfs */
    int (*statfs)(struct dentry *, struct kstatfs *);

    /* 持久化选项 */
    int (*show_options)(struct seq_file *, struct dentry *);
    int (*show_devname)(struct seq_file *, struct dentry *);

    /* Quota */
    const struct quotactl_ops *s_qcop;
};
```

## 9. 文件系统操作函数集

### 9.1 inode_operations

```c
struct inode_operations {
    /* 创建/删除 */
    int (*create)(struct inode *, struct dentry *, umode_t, bool);
    struct dentry *(*lookup)(struct inode *, struct dentry *, unsigned int);
    int (*link)(struct dentry *, struct inode *, struct dentry *);
    int (*unlink)(struct inode *, struct dentry *);
    int (*symlink)(struct inode *, struct dentry *, const char *);
    int (*mkdir)(struct inode *, struct dentry *, umode_t);
    int (*rmdir)(struct inode *, struct dentry *);
    int (*mknod)(struct inode *, struct dentry *, umode_t, dev_t);

    /* 重命名 */
    int (*rename)(struct inode *, struct dentry *,
                  struct inode *, struct dentry *, unsigned int);

    /* 权限检查 */
    int (*permission)(struct mnt_idmap *, struct inode *, int);

    /* ACL */
    int (*get_acl)(struct inode *, int, bool);
    int (*set_acl)(struct mnt_idmap *, struct inode *, int,
                   struct posix_acl *, void *);

    /* 时间戳更新 */
    int (*update_time)(struct inode *, struct timespec64 *, int);

    /* 文件变更通知 */
    __poll_t (*renamex)(struct inode *, struct dentry *, unsigned int);
};
```

### 9.2 file_operations

```c
struct file_operations {
    /* 定位 */
    loff_t (*llseek)(struct file *, loff_t, int);

    /* 同步读写 */
    ssize_t (*read)(struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write)(struct file *, const char __user *, size_t, loff_t *);

    /* 异步 I/O */
    ssize_t (*read_iter)(struct kiocb *, struct iov_iter *);
    ssize_t (*write_iter)(struct kiocb *, struct iov_iter *);

    /* 目录迭代 */
    int (*iterate)(struct file *, struct dir_context *);
    int (*iterate_shared)(struct file *, struct dir_context *);

    /* 文件操作 */
    int (*open)(struct inode *, struct file *);
    int (*flush)(struct file *, fl_owner_t id);
    int (*release)(struct inode *, struct file *);
    int (*fsync)(struct file *, loff_t, loff_t, int);
    int (*fsync_range)(struct file *, loff_t, loff_t, int);

    /* 锁 */
    int (*lock)(struct file *, int, struct file_lock *);
    int (*flock)(struct file *, int, struct file_lock *);

    /* I/O 多路复用 */
    __poll_t (*poll)(struct file *, struct poll_table_struct *);

    /* 内存映射 */
    int (*mmap)(struct file *, struct vm_area_struct *);

    /* 缓存操作 */
    int (*flush)(struct file *, fl_owner_t);
};
```

## 10. 核心算法复杂度分析

### 10.1 路径查找复杂度

| 场景 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| 缓存命中（RCU） | O(1) | O(1) |
| 缓存未命中 | O(d) | O(1) |
| 完全遍历 | O(n) | O(d) |

其中：
- d = 路径深度
- n = 目录中的文件数

### 10.2 Dentry 哈希表查找

```c
/*
 * 假设：哈希表大小 = 2^k
 * 期望链长度 = n / 2^k
 * 查找复杂度 = O(1 + 期望链长度)
 *
 * 当 n = dentry 数量，负载因子 α = n / m (m = 桶数)
 * 期望查找长度 = O(1 + α)
 *
 * Linux 动态调整哈希表大小，保持 α 在合理范围
 */
```

### 10.3 Inode LRU 驱逐

```c
/*
 * LRU 驱逐算法：
 * 1. 按 inode->i_sb 分组
 * 2. 每组按 LRU 顺序驱逐
 * 3. 使用 list_lru 实现，支持 NUMA
 *
 * 复杂度：
 * - 查找：O(1) 从链表尾部获取
 * - 移动：O(1) 链表操作
 * - 销毁：文件系统特定
 */
```

## 11. 内存屏障与并发

### 11.1 关键内存屏障

```c
/*
 * 1. d_seq 序列计数器
 *    write_seqcount_begin/end 包含完整内存屏障
 *    保证之前的写操作对之后的读者可见
 *
 * 2. smp_store_release / smp_load_acquire
 *    用于 dentry->d_name 存储/加载
 *    保证名称长度和内容的顺序访问
 *
 * 3. xa_store/xa_load
 *    XArray 内部使用锁或 RCU 保证顺序
 */
```

### 11.2 RCU Grace Period

```c
/*
 * RCU 宽限期（Grace Period）保证：
 *
 * 1. 读者在 RCU 读临界区内，不会看到旧数据
 * 2. 写者修改完成后，之前的读者全部退出，才能释放旧数据
 * 3. 使用 call_rcu() 或 synchronize_rcu() 实现
 *
 * synchronize_rcu() 等待所有进行中的读者完成
 * call_rcu() 回调在宽限期后执行
 */
```

## 12. 参考资料

- `fs/dcache.c` - Dentry 缓存实现
- `fs/namei.c` - 路径查找实现
- `fs/inode.c` - Inode 缓存实现
- `fs/super.c` - 超级块管理
- `include/linux/dcache.h` - Dentry 接口
- `include/linux/fs.h` - VFS 核心定义
- Documentation/filesystems/vfs.rst
- Documentation/filesystems/path-lookup.txt
- "Understanding the Linux Kernel" - Bovet & Cesati
- "Linux Kernel Development" - Robert Love
