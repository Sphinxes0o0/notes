# VFS Superblock 管理

## 1. 模块架构

### 1.1 功能概述

Superblock 是文件系统的元数据结构，包含文件系统的整体信息（如块大小、总块数、 inode 数量等）。每个挂载的文件系统都有一个 super_block 结构。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `fs/super.c` | superblock 管理实现 |
| `include/linux/fs/super_types.h` | superblock 类型定义 |
| `include/linux/fs.h` | super_operations |
| `fs/sync.c` | 文件系统同步 |

## 2. 核心数据结构

### 2.1 struct super_block

```c
// include/linux/fs/super_types.h:132
struct super_block {
    struct list_head        s_list;         // 全局链表
    dev_t                   s_dev;          // 设备号
    unsigned char           s_blocksize_bits;
    unsigned long           s_blocksize;     // 块大小
    loff_t                  s_maxbytes;     // 最大文件大小
    struct file_system_type *s_type;       // 文件系统类型
    const struct super_operations *s_op;   // superblock 操作
    struct dentry           *s_root;        // 根目录 dentry
    struct rw_semaphore     s_umount;       // 卸载信号量
    int                     s_count;         // 引用计数
    atomic_t                s_active;        // 活跃计数
    unsigned long           s_flags;        // 挂载标志
    unsigned long           s_magic;        // 文件系统魔数
    void                    *s_fs_info;     // 文件系统私有数据
    struct block_device     *s_bdev;        // 块设备
    struct backing_dev_info *s_bdi;         // 回写设备信息
    struct list_head        s_inodes;       // inode 链表
    struct list_head        s_dirty;        // 脏 inode 链表
    struct list_head        s_io;           // 正在回写的 inode
    struct list_head        s_more_io;     // 更多 I/O
    struct list_lru         s_dentry_lru;   // dentry LRU
    struct list_lru         s_inode_lru;   // inode LRU
    // ...
};
```

### 2.2 struct super_operations

```c
// include/linux/fs/super_types.h:83
struct super_operations {
    struct inode *(*alloc_inode)(struct super_block *sb);
    void (*destroy_inode)(struct inode *inode);
    void (*free_inode)(struct inode *inode);
    void (*dirty_inode)(struct inode *inode, int flags);
    int (*write_inode)(struct inode *inode, struct writeback_control *wbc);
    int (*drop_inode)(struct inode *inode);
    void (*evict_inode)(struct inode *inode);
    void (*put_super)(struct super_block *sb);
    int (*sync_fs)(struct super_block *sb, int wait);
    int (*freeze_super)(struct super_block *sb, ...);
    int (*thaw_super)(struct super_block *sb, ...);
    int (*statfs)(struct dentry *dentry, struct kstatfs *kstatfs);
    void (*umount_begin)(struct super_block *sb);
    int (*show_options)(struct seq_file *seq, struct dentry *dentry);
    long (*nr_cached_objects)(struct super_block *sb,
                              struct shrink_control *sc);
    long (*free_cached_objects)(struct super_block *sb,
                                struct shrink_control *sc);
};
```

### 2.3 struct file_system_type

```c
// include/linux/fs.h:1400
struct file_system_type {
    const char *name;                   // 文件系统名称
    int fs_flags;                       // 文件系统标志
    int (*read_super)(struct super_block *sb, ...);
    struct file_system_type *next;      // 链表
    struct list_head fs_supers;         // superblock 链表
    struct lock_class_key s_lock_key;
    struct lock_class_key s_umount_key;
    // ...
};
```

## 3. Superblock 分配

### 3.1 alloc_super()

```c
// fs/super.c:200
static struct super_block *alloc_super(struct file_system_type *type,
                                       int user_flags)
{
    struct super_block *s = kzalloc(sizeof(struct super_block), GFP_USER);

    if (s) {
        // 初始化信号量
        init_rwsem(&s->s_umount);
        // 初始化锁
        spin_lock_init(&s->s_lock);
        // 初始化引用计数
        atomic_set(&s->s_active, 1);
        // 初始化 LRU
        list_lru_init(&s->s_dentry_lru);
        list_lru_init(&s->s_inode_lru);
        // 初始化链表
        INIT_LIST_HEAD(&s->s_inodes);
        INIT_LIST_HEAD(&s->s_dirty);
        INIT_LIST_HEAD(&s->s_io);
        // 设置文件系统类型
        s->s_type = type;
        s->s_flags = user_flags;
    }

    return s;
}
```

### 3.2 sget()

```c
// fs/super.c:300
struct super_block *sget(struct file_system_type *type,
                        int (*test)(struct super_block *, void *),
                        int (*set)(struct super_block *, void *),
                        int flags, void *data)
{
    struct super_block *s = NULL;
    struct super_block *old;
    int err;

    // 查找已存在的 superblock
    spin_lock(&sb_lock);
    list_for_each_entry(old, &type->fs_supers, s_instance) {
        if (!test(old, data))
            continue;

        if (user_flags && old->s_flags != user_flags)
            continue;

        // 增加引用计数
        if (!atomic_inc_not_zero(&old->s_active))
            continue;

        spin_unlock(&sb_lock);
        return old;
    }
    spin_unlock(&sb_lock);

    // 分配新的 superblock
    s = alloc_super(type, flags & ~MS_SUBMOUNT);
    if (!s)
        return ERR_PTR(-ENOMEM);

    err = set(s, data);
    if (err) {
        deactivate_super(s);
        return ERR_PTR(err);
    }

    // 加入全局链表
    spin_lock(&sb_lock);
    list_add_tail(&s->s_list, &type->fs_supers);
    spin_unlock(&sb_lock);

    return s;
}
```

## 4. Superblock 卸载

### 4.1 deactivate_locked_super()

```c
// fs/super.c:500
void deactivate_locked_super(struct super_block *s)
{
    struct file_system_type *fs = s->s_type;

    // 如果还有活跃引用，等待
    if (atomic_dec_and_test(&s->s_active)) {
        // 同步文件系统
        sync_filesystem(s);
        // 杀死所有 inode
        evict_inodes(s->s_root->d_sb);
        // 刷新脏数据
        sync_filesystem(s);
        // 调用文件系统的 put_super
        if (fs->put_super)
            fs->put_super(s);
        // 释放根 dentry
        dput(s->s_root);
        // 释放块设备
        blkdev_put(s->s_bdev, BDEVFS_TYPE);
    }
}
```

### 4.2 generic_shutdown_super()

```c
// fs/super.c:450
void generic_shutdown_super(struct super_block *sb)
{
    // 杀死所有 inode
    evict_inodes(sb);

    // 刷新并释放根 dentry
    if (sb->s_root) {
        dput(sb->s_root);
        sb->s_root = NULL;
    }

    // 调用文件系统的 put_super
    if (sb->s_op->put_super)
        sb->s_op->put_super(sb);

    // 从哈希表移除
    spin_lock(&sb_lock);
    hlist_del_init_rcu(&sb->s_instances);
    spin_unlock(&sb_lock);

    // 释放 s_umount 信号量
    up_write(&sb->s_umount);
}
```

## 5. Superblock 同步

### 5.1 sync_filesystem()

```c
// fs/sync.c:200
void sync_filesystem(struct super_block *sb)
{
    // 同步所有脏数据
    if (sb->s_op->sync_fs)
        sb->s_op->sync_fs(sb, 0);

    // 同步所有 inode
    sync_inodes_sb(sb);

    // 同步超级块
    if (sb->s_op->write_super && sb->s_dirt)
        sb->s_op->write_super(sb);
}
```

### 5.2 sync_inodes_sb()

```c
// fs/sync.c:250
void sync_inodes_sb(struct super_block *sb)
{
    struct inode *inode;

    spin_lock(&sb->s_inode_list_lock);
    list_for_each_entry(inode, &sb->s_inodes, i_sb_list) {
        if (inode->i_state & I_DIRTY)
            write_inode(inode, NULL);
    }
    spin_unlock(&sb->s_inode_list_lock);
}
```

## 6. Superblock 冻结

### 6.1 freeze_super()

```c
// fs/super.c:600
int freeze_super(struct super_block *sb)
{
    int ret;

    // 获取 s_umount 写锁
    down_write(&sb->s_umount);

    // 如果已经冻结，直接返回
    if (sb->s_writers.frozen >= SB_FREEZE_COMPLETE) {
        ret = -EBUSY;
        goto out;
    }

    // 同步文件系统
    sync_filesystem(sb);

    // 冻结
    ret = sb->s_op->freeze_super(sb, SB_FREEZE_WRITE);
    if (ret)
        goto out;

    // 等待所有进程退出
    sb->s_writers.frozen = SB_FREEZE_WRITE;
    wake_up(&sb->s_writer_wq);
    wait_event(sb->s_writer_wq, sb->s_writers.sumo_writes == 0);

    ret = sb->s_op->freeze_super(sb, SB_FREEZE_PAGEFAULT);
    if (ret)
        goto out;

    ret = sb->s_op->freeze_super(sb, SB_FREEZE_FS);
    if (ret)
        goto out;

    sb->s_writers.frozen = SB_FREEZE_COMPLETE;

out:
    up_write(&sb->s_umount);
    return ret;
}
```

### 6.2 thaw_super()

```c
// fs/super.c:650
int thaw_super(struct super_block *sb)
{
    int ret;

    down_write(&sb->s_umount);

    if (sb->s_writers.frozen < SB_FREEZE_COMPLETE) {
        ret = -EINVAL;
        goto out;
    }

    ret = sb->s_op->thaw_super(sb);
    if (ret)
        goto out;

    sb->s_writers.frozen = SB_UNFROZEN;
    wake_up(&sb->s_writer_wq);

out:
    up_write(&sb->s_umount);
    return ret;
}
```

## 7. Superblock 查找

### 7.1 get_super()

```c
// fs/super.c:150
struct super_block *get_super(struct block_device *bdev)
{
    struct super_block *s;

    // 遍历所有 superblock
    spin_lock(&sb_lock);
    list_for_each_entry(s, &super_blocks, s_list) {
        if (s->s_bdev == bdev) {
            // 增加引用计数
            if (atomic_inc_not_zero(&s->s_active))
                s->s_count++;
            spin_unlock(&sb_lock);
            return s;
        }
    }
    spin_unlock(&sb_lock);

    return NULL;
}
```

### 7.2 get_super_thawed()

```c
// fs/super.c:180
struct super_block *get_super_thawed(struct block_device *bdev)
{
    struct super_block *s = get_super(bdev);

    if (!s)
        return NULL;

    // 等待冻结完成
    wait_event(s->s_writer_wq, s->s_writers.frozen < SB_FREEZE_WRITE);

    return s;
}
```

## 8. Superblock LRU

### 8.1 super_cache_scan()

```c
// fs/super.c:800
static unsigned long super_cache_scan(struct shrink_control *sc)
{
    struct super_block *sb;
    unsigned long freed = 0;

    spin_lock(&sb_lock);
    list_for_each_entry(sb, &super_blocks, s_list) {
        struct dentry *dentry;

        // 尝试收缩 dentry LRU
        freed += list_lru_shrink_walk(&sb->s_dentry_lru, sc,
                                       &dentry_lru_isolate, NULL);

        // 如果已经满足要求，停止
        if (freed >= sc->nr_to_scan)
            break;
    }
    spin_unlock(&sb_lock);

    return freed;
}
```

## 9. 文件系统注册

### 9.1 register_filesystem()

```c
// fs/filesystem.c:100
int register_filesystem(struct file_system_type *fs)
{
    int res = 0;
    struct file_system_type *p;

    // 检查是否已注册
    list_for_each_entry(p, &file_systems, list) {
        if (strcmp(p->name, fs->name) == 0) {
            res = -EBUSY;
            goto out;
        }
    }

    // 加入链表
    list_add_tail(&fs->list, &file_systems);

out:
    return res;
}
```

### 9.2 unregister_filesystem()

```c
// fs/filesystem.c:150
int unregister_filesystem(struct file_system_type *fs)
{
    int res = 0;

    spin_lock(&file_systems_lock);
    if (!list_empty(&fs->fs_supers))
        res = -EBUSY;
    else
        list_del(&fs->list);
    spin_unlock(&file_systems_lock);

    return res;
}
```

## 10. 挂载流程

```
用户: mount("/dev/sda1", "/mnt", "ext4", MS_MGC_VAL, NULL)

内核路径:
1. do_mount()
   |
   2. do_new_mount()
      |
      3. vfs_kern_mount()
         |
      4. alloc_vfsmnt()
         |  分配 struct vfsmount
         |
      5. type->read_super() 或 get_sb_bdev()
         |  读取/创建 super_block
         |
      6. sget()
         |  查找或分配 superblock
         |
      7. ext4_fill_super()
         |  初始化 ext4 特定数据
         |
      8. set_anon_super()
         |  设置匿名 superblock
         |
      9. graft_tree()
         |  将 vfsmount 加入挂载树
```

## 11. Superblock 标志

```c
// include/linux/fs.h
#define MS_RDONLY       (1 << 0)    // 只读
#define MS_NOSUID       (1 << 1)    // 不执行 setuid
#define MS_NODEV        (1 << 2)    // 不允许访问设备
#define MS_NOEXEC       (1 << 3)    // 不允许执行
#define MS_SYNCHRONOUS  (1 << 4)    // 同步 I/O
#define MS_REMOUNT      (1 << 5)    // 重新挂载
#define MS_MANDLOCK     (1 << 6)    // 强制锁
#define MS_DIRSYNC      (1 << 7)    // 目录同步
#define MS_NOATIME      (1 << 10)   // 不更新 atime
#define MS_NODIRATIME   (1 << 11)   // 不更新目录 atime
#define MS_BIND         (1 << 12)   // 绑定挂载
#define MS_MOVE         (1 << 13)   // 移动挂载
#define MS_REC          (1 << 14)   // 递归
#define MS_SILENT       (1 << 15)   // 静默
```
