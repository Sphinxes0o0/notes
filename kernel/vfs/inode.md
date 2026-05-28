# VFS Inode 管理

## 1. 模块架构

### 1.1 功能概述

Inode (索引节点) 是 VFS 表示文件的核心数据结构。每个文件在内存中对应一个 inode，包含了文件的元数据和数据块的映射信息。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `fs/inode.c` | inode 管理实现 |
| `include/linux/fs.h` | inode 结构定义 |
| `include/linux/fs/super_types.h` | super_operations |
| `mm/page-writeback.c` | 页面回写 |

## 2. 核心数据结构

### 2.1 struct inode

```c
// include/linux/fs.h:766
struct inode {
    umode_t                 i_mode;        // 文件类型和权限
    unsigned short          i_opflags;
    kuid_t                  i_uid;          // 用户 ID
    kgid_t                  i_gid;          // 组 ID
    const struct inode_operations *i_op;    // inode 操作
    struct super_block      *i_sb;          // 所属超级块
    struct address_space    *i_mapping;     // 地址空间
    unsigned long           i_ino;          // inode 编号
    union {
        unsigned int        i_nlink;         // 硬链接计数
        atomic_t            i_dio_count;
    };
    dev_t                   i_rdev;         // 设备号
    loff_t                  i_size;         // 文件大小
    struct timespec64      i_atime;         // 访问时间
    struct timespec64      i_mtime;         // 修改时间
    struct timespec64      i_ctime;         // 状态改变时间
    struct timespec64      i_btime;         // 创建时间
    atomic_t                i_count;         // 引用计数
    atomic_t                i_dio_count;
    struct ext *i_ext;                     // 扩展属性
    struct list_head        i_dentry;       // dentry 别名链表
    unsigned long           i_state;
    struct inode            *i_parent;       // 父 inode
    struct dentry           *i_dentry;      // 主 dentry
    unsigned long           i_flags;
    struct file_lock_context *i_flctx;
    struct address_space    i_data;
    struct list_head        i_wb_list;
    // ...
};
```

### 2.2 inode 状态标志

```c
// include/linux/fs.h:102
enum {
    I_LOCK          = 0,        // inode 正在被使用
    I_NEW           = 1,        // inode 正在创建
    I_DIRTY_INODE   = 2,        // inode 需要写回
    I_DIRTY_PAGES   = 3,        // inode 的页面脏
    I_FREEING       = 4,        // inode 正在释放
    I_CLEAR         = 5,        // inode 正在清除
    I_SYNC         = 6,        // inode 正在同步
};
```

## 3. Inode 分配

### 3.1 alloc_inode()

```c
// fs/inode.c:267
struct inode *alloc_inode(struct super_block *sb)
{
    const struct super_operations *ops = sb->s_op;
    struct inode *inode;

    // 优先使用文件系统特定的分配
    if (ops->alloc_inode)
        inode = ops->alloc_inode(sb);
    else
        inode = alloc_inode_sb(sb, inode_cachep, GFP_KERNEL);

    if (!inode)
        return NULL;

    // 初始化
    inode_init_always(sb, inode);

    return inode;
}
```

### 3.2 inode_init_always()

```c
// fs/inode.c:200
void inode_init_always(struct super_block *sb, struct inode *inode)
{
    inode->i_sb = sb;
    inode->i_blkbits = sb->s_blocksize_bits;
    inode->i_flags = 0;
    atomic_set(&inode->i_count, 1);
    inode->i_nlink = 1;
    inode->i_op = NULL;
    inode->i_fop = NULL;
    inode->i_opflags = 0;

    // 初始化 address_space
    inode->i_mapping = &inode->i_data;
    address_space_init_once(inode->i_mapping);

    // 初始化时间
    inode->i_atime = inode->i_mtime = inode->i_ctime = current_time(inode);

    // 初始化锁
    spin_lock_init(&inode->i_lock);
    init_rwsem(&inode->i_rwsem);

    // 初始化 LRU
    list_lru_init(&inode->i_lru);
}
```

## 4. Inode 查找

### 4.1 iunique()

```c
// fs/inode.c:450
struct inode *iunique(struct super_block *sb, unsigned int id)
{
    struct inode *inode;

    spin_lock(&inode_hash_lock);
    inode = find_inode_fast(sb, &id);
    if (inode) {
        atomic_inc(&inode->i_count);
        spin_unlock(&inode_hash_lock);
    } else {
        spin_unlock(&inode_hash_lock);
        inode = NULL;
    }

    return inode;
}
```

### 4.2 find_inode_fast()

```c
// fs/inode.c:420
static struct inode *find_inode_fast(struct super_block *sb,
                                     unsigned int *hash)
{
    struct inode *inode;

    rcu_read_lock();
    hlist_for_each_entry_rcu(inode, &inode_hashtable[hash], i_hash) {
        if (inode->i_sb != sb)
            continue;
        if (!atomic_inc_not_zero(&inode->i_count))
            continue;
        spin_unlock(&inode->i_lock);
        rcu_read_unlock();
        return inode;
    }
    rcu_read_unlock();
    return NULL;
}
```

## 5. Inode 引用计数

### 5.1 ihold()

```c
// fs/inode.c:500
void ihold(struct inode *inode)
{
    WARN_ON(atomic_inc_return(&inode->i_count) <= 1);
}
```

### 5.2 iput()

```c
// fs/inode.c:550
void iput(struct inode *inode)
{
    if (!inode)
        return;

    drop_inode(inode);
}
```

### 5.3 drop_inode()

```c
// fs/inode.c:530
static void drop_inode(struct inode *inode)
{
    // 调用文件系统特定的 drop_inode
    if (inode->i_op->drop_inode)
        inode->i_op->drop_inode(inode);
    else
        generic_drop_inode(inode);
}
```

### 5.4 generic_drop_inode()

```c
// fs/inode.c:100
void generic_drop_inode(struct inode *inode)
{
    // 如果没有硬链接，立即删除
    if (!inode->i_nlink)
        evict(inode);
    else
        iput(inode);
}
```

## 6. Inode 释放

### 6.1 evict_inode()

```c
// fs/inode.c:600
void evict_inode(struct inode *inode)
{
    const struct super_operations *ops = inode->i_sb->s_op;

    // 调用文件系统特定的 evict
    if (ops->evict_inode) {
        ops->evict_inode(inode);
    } else {
        // 默认实现
        truncate_inode_pages_final(&inode->i_data);
        invalidate_inode_buffers(inode);
    }

    // 如果是脏的，写回
    if (!is_bad_inode(inode))
        write_inode(inode, NULL);

    // 从 LRU 移除
    list_lru_del(&inode->i_lru);

    // 从 inode 哈希表移除
    spin_lock(&inode_hash_lock);
    hlist_del_init(&inode->i_hash);
    spin_unlock(&inode_hash_lock);

    // 清除 inode
    clear_inode(inode);
}
```

### 6.2 clear_inode()

```c
// fs/inode.c:650
void clear_inode(struct inode *inode)
{
    // 移除页面缓存
    truncate_inode_pages_final(&inode->i_data);

    // 移除 inode
    if (inode->i_op->destroy_inode)
        inode->i_op->destroy_inode(inode);
    else
        kmem_cache_free(inode_cachep, inode);
}
```

## 7. Inode 同步

### 7.1 write_inode()

```c
// fs/inode.c:700
int write_inode(struct inode *inode, struct writeback_control *wbc)
{
    const struct super_operations *ops = inode->i_sb->s_op;
    int err;

    if (!ops->write_inode)
        return 0;

    err = ops->write_inode(inode, wbc);
    if (wbc->sync_mode == WB_SYNC_ALL)
        inode_sync_wait(inode);

    return err;
}
```

### 7.2 inode_sync_wait()

```c
// fs/inode.c:720
static void inode_sync_wait(struct inode *inode)
{
    DEFINE_WAIT(wait);

    spin_lock(&inode->i_lock);
    while (inode->i_state & I_SYNC) {
        prepare_to_wait(&inode->i_wb_wait, &wait, TASK_UNINTERRUPTIBLE);
        spin_unlock(&inode->i_lock);
        schedule();
        spin_lock(&inode->i_lock);
    }
    finish_wait(&inode->i_wb_wait, &wait);
    spin_unlock(&inode->i_lock);
}
```

## 8. Inode LRU

### 8.1 inode_lru_isolate()

```c
// fs/inode.c:800
static enum lru_status inode_lru_isolate(struct list_head *item,
                                          struct list_lru_one *lru,
                                          spinlock_t *lru_lock,
                                          void *arg)
{
    struct inode *inode = container_of(item, struct inode, i_lru);

    if (!spin_trylock(&inode->i_lock))
        return LRU_ROTATE;

    if (atomic_read(&inode->i_count))
        goto out;

    if (inode->i_state & (I_NEW | I_FREEING | I_WILL_FREE))
        goto out;

    // 从 LRU 移除
    list_del_init(&inode->i_lru);

    // 标记正在释放
    inode->i_state |= I_FREEING;

    spin_unlock(&inode->i_lock);
    return LRU_REMOVED;

out:
    spin_unlock(&inode->i_lock);
    return LRU_SKIP;
}
```

### 8.2 prune_icache_sb()

```c
// fs/inode.c:850
static unsigned long prune_icache_sb(struct super_block *sb,
                                     struct shrink_control *sc)
{
    unsigned long nr_pruned;

    nr_pruned = list_lru_shrink_walk(&sb->s_inode_lru, sc,
                                      inode_lru_isolate, NULL);

    return nr_pruned;
}
```

## 9. Inode 哈希表

### 9.1 inode_hashtable

```c
// fs/inode.c:50
static struct hlist_head *inode_hashtable __read_mostly;
static unsigned int inode_hash_mask __read_mostly;
```

### 9.2 inode_hash()

```c
// fs/inode.c:60
static inline unsigned long inode_hash(struct super_block *sb,
                                       unsigned long ino)
{
    return (ino + (unsigned long)sb) & inode_hash_mask;
}
```

## 10. Inode 时间更新

### 10.1 atime/mtime/ctime

```c
// fs/inode.c:300
void touch_atime(struct path *path)
{
    struct inode *inode = path->dentry->d_inode;

    if (!sb_rdonly(inode->i_sb)) {
        struct timespec64 now = current_time(inode);
        if (!timespec64_equal(&inode->i_atime, &now)) {
            inode->i_atime = now;
            mark_inode_dirty(inode);
        }
    }
}
```

### 10.2 inode_set_mtime()

```c
// fs/inode.c:350
void inode_set_mtime(struct inode *inode, struct timespec64 time)
{
    inode->i_mtime = time;
    if (!inode->i_op->set_mtime)
        mark_inode_dirty(inode);
}
```

## 11. Inode 权限检查

### 11.1 inode_permission()

```c
// fs/inode.c:950
int inode_permission(struct mnt_idmap *idmap,
                     struct inode *inode, int mask)
{
    if (!inode->i_op->permission)
        return generic_permission(idmap, inode, mask);

    return inode->i_op->permission(idmap, inode, mask);
}
```

### 11.2 generic_permission()

```c
// fs/inode.c:1000
int generic_permission(struct mnt_idmap *idmap,
                       struct inode *inode, int mask)
{
    kuid_t uid = i_uid_into_kuid(idmap, inode);
    kgid_t gid = i_gid_into_kgid(idmap, inode);
    umode_t mode = inode->i_mode;

    // 检查 owner
    if (uid_eq(current_fsuid(), uid))
        mode >>= 6;
    else if (in_group_p(gid))
        mode >>= 3;

    // 检查是否有请求的权限
    if ((mode & mask & (MAY_READ | MAY_WRITE | MAY_EXEC)) == mask)
        return 0;

    return -EACCES;
}
```

## 12. Inode 创建流程

```
用户: open("/tmp/test", O_CREAT | O_WRONLY)

内核路径:
1. do_sys_open()
   |
   2. do_filp_open()
      |
      3. path_lookupat()
         |  查找父目录 "/tmp"
         |  创建子 dentry "test"
         |
      4. vfs_create()
         |
         5. inode->i_op->create()
            |  ext4_create()
            |  创建新的 inode
            |
         6. d_instantiate()
            |  将 inode 与 dentry 关联
```
