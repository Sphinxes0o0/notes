# Linux VFS 子系统深度分析 R1

## 目录

1. [概述](#概述)
2. [inode 子系统](#1-inode-子系统)
   - [struct inode 数据结构](#11-struct-inode-数据结构)
   - [inode_init_always() 初始化流程](#12-inode_init_always-初始化流程)
   - [inode_owner_or_capable() 权限检查](#13-inode_owner_or_capable-权限检查)
   - [inode_operations 操作向量](#14-inode_operations-操作向量)
3. [dentry 子系统](#2-dentry-子系统)
   - [struct dentry 数据结构](#21-struct-dentry-数据结构)
   - [dcache 哈希表](#22-dcache-哈希表)
   - [d_lookup() 查找流程](#23-d_lookup-查找流程)
   - [d_add()/d_instantiate() 添加流程](#24-d_addd_instantiate-添加流程)
   - [目录项缓存回收机制](#25-目录项缓存回收机制)
4. [super_block 子系统](#3-super_block-子系统)
   - [struct super_block 数据结构](#31-struct-super_block-数据结构)
   - [super_operations 操作向量](#32-super_operations-操作向量)
   - [alloc_super() 创建流程](#33-alloc_super-创建流程)
   - [sget_fc() 超级块查找/创建](#34-sget_fc-超级块查找创建)
5. [file 子系统](#4-file-子系统)
   - [struct file 数据结构](#41-struct-file-数据结构)
   - [struct path 路径结构](#42-struct-path-路径结构)
   - [file_operations 文件操作](#43-file_operations-文件操作)
   - [fdtable 文件描述符表](#44-fdtable-文件描述符表)
   - [文件描述符分配](#45-文件描述符分配)
6. [address_space 子系统](#5-address_space-子系统)
   - [struct address_space 数据结构](#51-struct-address_space-数据结构)
   - [radix_tree/XArray 页缓存](#52-radix_treexarray-页缓存)
   - [writeback 写回机制](#53-writeback-写回机制)
7. [知识点关联表](#知识点关联表)

---

## 概述

Linux VFS (Virtual File System) 是内核中连接用户空间文件系统调用与具体文件系统的抽象层。它通过定义一组标准数据结构和操作接口，使得不同的文件系统（ext4、XFS、Btrfs、NFS、FUSE等）能够共存于同一个内核中。

VFS 的核心数据结构包括：
- **inode**: 表示文件系统中的单个文件/目录对象
- **dentry**: 表示目录项缓存中的条目，关联文件名和 inode
- **super_block**: 表示一个已挂载的文件系统
- **file**: 表示进程打开的文件实例
- **address_space**: 表示文件的页缓存结构

---

## 1. inode 子系统

### 1.1 struct inode 数据结构

**源码位置**: `include/linux/fs.h` 第 766-875 行

```c
struct inode {
    umode_t         i_mode;          // 文件类型与权限
    unsigned short  i_opflags;       // inode 操作标志
    unsigned int    i_flags;         // 文件系统标志
#ifdef CONFIG_FS_POSIX_ACL
    struct posix_acl *i_acl;
    struct posix_acl *i_default_acl;
#endif
    kuid_t          i_uid;          // 用户ID
    kgid_t          i_gid;          // 组ID

    const struct inode_operations *i_op;  // inode 操作向量
    struct super_block *i_sb;             // 所属超级块
    struct address_space *i_mapping;       // 页面缓存映射

    /* Stat 数据 */
    unsigned long   i_ino;           // inode 编号
    union {
        const unsigned int i_nlink;
        unsigned int __i_nlink;
    };
    dev_t           i_rdev;          // 设备号（针对设备文件）
    loff_t          i_size;         // 文件大小
    time64_t        i_atime_sec;    // 访问时间
    time64_t        i_mtime_sec;    // 修改时间
    time64_t        i_ctime_sec;    // 变更时间
    // ... 时间戳纳秒部分 ...

    spinlock_t      i_lock;         // 保护 i_blocks, i_bytes, i_size
    unsigned short  i_bytes;        // 文件块内剩余字节数
    u8              i_blkbits;      // 块大小位数
    blkcnt_t        i_blocks;       // 文件块数

    struct rw_semaphore i_rwsem;    // 读写信号量

    struct hlist_node i_hash;       // inode 哈希表链表
    struct list_head i_io_list;     // 写回链表
    struct list_head i_lru;          // LRU 链表
    struct list_head i_sb_list;     // 超级块链表
    union {
        struct hlist_head i_dentry; // 别名链表
        struct rcu_head   i_rcu;    // RCU 释放头
    };
    atomic64_t      i_version;      // 版本号
    atomic64_t      i_sequence;      // futex 用序列号
    atomic_t        i_count;        // 引用计数
    atomic_t        i_dio_count;    // 直接IO计数
    atomic_t        i_writecount;   // 写计数

    union {
        const struct file_operations *i_fop;  // 默认文件操作
        void (*free_inode)(struct inode *);   // 释放回调
    };
    struct address_space i_data;     // 页面缓存
    union {
        struct pipe_inode_info *i_pipe;  // 管道
        struct cdev *i_cdev;              // 字符设备
        char *i_link;                     // 符号链接
    };
#ifdef CONFIG_FSNOTIFY
    __u32           i_fsnotify_mask; // fsnotify 掩码
    struct fsnotify_mark_connector __rcu *i_fsnotify_marks;
#endif
    void            *i_private;      // 文件系统私有数据
};
```

**关键字段说明**:
- `i_ino`: inode 唯一标识符，在同一个 super_block 内唯一
- `i_count`: 引用计数，用于 inode 缓存管理
- `i_nlink`: 硬链接数量
- `i_op`: 指向文件系统特定的 inode_operations
- `i_mapping`: 指向 address_space，用于页缓存管理

### 1.2 inode_init_always() 初始化流程

**源码位置**: `fs/inode.c` 第 228-313 行

```c
int inode_init_always_gfp(struct super_block *sb, struct inode *inode, gfp_t gfp)
{
    static const struct inode_operations empty_iops;
    static const struct file_operations no_open_fops = {.open = no_open};
    struct address_space *const mapping = &inode->i_data;

    inode->i_sb = sb;
    inode->i_blkbits = sb->s_blocksize_bits;
    inode->i_flags = 0;
    inode_state_assign_raw(inode, 0);
    atomic64_set(&inode->i_sequence, 0);
    atomic_set(&inode->i_count, 1);
    inode->i_op = &empty_iops;
    inode->fop = &no_open_fops;
    inode->i_ino = 0;
    inode->__i_nlink = 1;
    inode->i_opflags = 0;
    
    // 设置扩展属性和 multigrain timestamps 标志
    if (sb->s_xattr)
        inode->i_opflags |= IOP_XATTR;
    if (sb->s_type->fs_flags & FS_MGTIME)
        inode->i_opflags |= IOP_MGTIME;

    // 初始化 UID/GID
    i_uid_write(inode, 0);
    i_gid_write(inode, 0);
    atomic_set(&inode->i_writecount, 0);
    inode->i_size = 0;
    inode->i_blocks = 0;
    inode->i_bytes = 0;

    // 初始化锁
    spin_lock_init(&inode->i_lock);
    lockdep_set_class(&inode->i_lock, &sb->s_type->i_lock_key);
    init_rwsem(&inode->i_rwsem);
    lockdep_set_class(&inode->i_rwsem, &sb->s_type->i_mutex_key);

    // 初始化 address_space
    mapping->a_ops = &empty_aops;
    mapping->host = inode;
    mapping->flags = 0;
    mapping_set_gfp_mask(mapping, GFP_HIGHUSER_MOVABLE);
    init_rwsem(&mapping->invalidate_lock);
    
    inode->i_private = NULL;
    inode->i_mapping = mapping;
    INIT_HLIST_HEAD(&inode->i_dentry);

    if (unlikely(security_inode_alloc(inode, gfp)))
        return -ENOMEM;

    this_cpu_inc(nr_inodes);
    return 0;
}
```

**初始化流程图解**:

```
alloc_inode()
    │
    ├── ops->alloc_inode(sb)  // 文件系统分配 inode
    │       或
    └── alloc_inode_sb(sb, inode_cachep, GFP_KERNEL)
            │
            └── inode_init_always(sb, inode)
                    │
                    ├── 设置 i_sb, i_blkbits
                    ├── 初始化状态标志 inode_state_assign_raw(inode, 0)
                    ├── 初始化原子变量 (i_count=1, i_sequence=0)
                    ├── 设置空操作向量 (&empty_iops, &no_open_fops)
                    ├── 初始化锁 (i_lock, i_rwsem)
                    ├── 初始化 address_space (i_data)
                    ├── 安全模块初始化 security_inode_alloc()
                    └── 增加 nr_inodes 计数器
```

### 1.3 inode_owner_or_capable() 权限检查

**源码位置**: `fs/inode.c` 第 2682-2710 行

```c
/**
 * inode_owner_or_capable - 检查当前任务对 inode 的权限
 * @idmap: mount 的 idmap
 * @inode: 被检查的 inode
 *
 * 如果当前进程在包含 inode owner uid 的命名空间中有 CAP_FOWNER 能力，
 * 或者拥有该文件（uid 匹配），返回 true。
 */
bool inode_owner_or_capable(struct mnt_idmap *idmap,
                            const struct inode *inode)
{
    vfsuid_t vfsuid;
    struct user_namespace *ns;

    // 将 inode 的 uid 根据 idmap 映射为 vfsuid
    vfsuid = i_uid_into_vfsuid(idmap, inode);
    
    // 检查当前 fsuid 是否匹配
    if (vfsuid_eq_kuid(vfsuid, current_fsuid()))
        return true;

    // 检查是否有 CAP_FOWNER 能力
    ns = current_user_ns();
    if (vfsuid_has_mapping(ns, vfsuid) && ns_capable(ns, CAP_FOWNER))
        return true;
        
    return false;
}
```

**权限检查逻辑**:

```
inode_owner_or_capable()
         │
         ├── i_uid_into_vfsuid(idmap, inode)
         │       将 inode 的 i_uid 根据 idmap 映射
         │
         ├── vfsuid == current_fsuid() ?
         │       ├─ 是 → return true (所有者)
         │       └─ 否 → 继续检查
         │
         └── ns_capable(CAP_FOWNER) ?
                 ├─ 是 → return true (有能力)
                 └─ 否 → return false (拒绝访问)
```

### 1.4 inode_operations 操作向量

**源码位置**: `include/linux/fs.h` 第 2001-2044 行

```c
struct inode_operations {
    // 目录查找
    struct dentry * (*lookup)(struct inode *, struct dentry *, unsigned int);
    
    // 符号链接获取
    const char * (*get_link)(struct dentry *, struct inode *, struct delayed_call *);
    
    // 权限检查
    int (*permission)(struct mnt_idmap *, struct inode *, int);
    
    // ACL 获取
    struct posix_acl * (*get_inode_acl)(struct inode *, int, bool);

    // 读链接
    int (*readlink)(struct dentry *, char __user *, int);

    // 创建文件
    int (*create)(struct mnt_idmap *, struct inode *, struct dentry *, umode_t, bool);
    
    // 硬链接
    int (*link)(struct dentry *, struct inode *, struct dentry *);
    
    // 删除
    int (*unlink)(struct inode *, struct dentry *);
    
    // 符号链接
    int (*symlink)(struct mnt_idmap *, struct inode *, struct dentry *, const char *);
    
    // 目录创建
    struct dentry *(*mkdir)(struct mnt_idmap *, struct inode *, struct dentry *, umode_t);
    
    // 目录删除
    int (*rmdir)(struct inode *, struct dentry *);
    
    // 设备节点创建
    int (*mknod)(struct mnt_idmap *, struct inode *, struct dentry *, umode_t, dev_t);
    
    // 重命名
    int (*rename)(struct mnt_idmap *, struct inode *, struct dentry *,
                  struct inode *, struct dentry *, unsigned int);
    
    // 属性设置
    int (*setattr)(struct mnt_idmap *, struct dentry *, struct iattr *);
    
    // 属性获取
    int (*getattr)(struct mnt_idmap *, const struct path *, struct kstat *, 
                   u32, unsigned int);
    
    // 扩展属性列表
    ssize_t (*listxattr)(struct dentry *, char *, size_t);
    
    // 文件区间信息
    int (*fiemap)(struct inode *, struct fiemap_extent_info *, u64 start, u64 len);
    
    // 时间更新
    int (*update_time)(struct inode *, enum fs_update_time type, unsigned int flags);
    
    // 原子打开
    int (*atomic_open)(struct inode *, struct dentry *, struct file *, 
                        unsigned open_flag, umode_t create_mode);
    
    // 临时文件
    int (*tmpfile)(struct mnt_idmap *, struct inode *, struct file *, umode_t);
    
    // ACL 操作
    struct posix_acl *(*get_acl)(struct mnt_idmap *, struct dentry *, int);
    int (*set_acl)(struct mnt_idmap *, struct dentry *, struct posix_acl *, int);
    
    // 文件属性
    int (*fileattr_set)(struct mnt_idmap *, struct dentry *, struct file_kattr *);
    int (*fileattr_get)(struct dentry *, struct file_kattr *);
};
```

---

## 2. dentry 子系统

### 2.1 struct dentry 数据结构

**源码位置**: `include/linux/dcache.h` 第 92-132 行

```c
struct dentry {
    /* RCU 查找触及的字段 */
    unsigned int            d_flags;          // 受 d_lock 保护
    seqcount_spinlock_t    d_seq;            // 每个 dentry 的序列锁
    struct hlist_bl_node    d_hash;           // 哈希链表
    struct dentry          *d_parent;         // 父目录
    union {
        struct qstr __d_name;                 // 仅供 fs/dcache.c 使用
        const struct qstr d_name;             // 正式的名称结构
    };
    struct inode           *d_inode;          // 关联的 inode，NULL 表示负 dentry

    union shortname_store   d_shortname;      // 短文件名存储

    const struct dentry_operations *d_op;     // dentry 操作向量
    struct super_block     *d_sb;             // 超级块
    unsigned long           d_time;           // d_revalidate 使用
    void                   *d_fsdata;        // 文件系统特定数据

    struct lockref          d_lockref;        // 锁和引用计数

    union {
        struct list_head    d_lru;            // LRU 链表
        wait_queue_head_t  *d_wait;           // 仅用于查找中的 dentry
    };
    struct hlist_node       d_sib;            // 父目录的子链表
    struct hlist_head       d_children;       // 我们的子目录

    union {
        struct hlist_node   d_alias;          // inode 别名链表
        struct hlist_bl_node d_in_lookup_hash; // 仅用于查找中的哈希
        struct rcu_head     d_rcu;            // RCU 释放
    } d_u;
};
```

**关键字段说明**:
- `d_flags`: 包含 DCACHE_DISCONNECTED、DCACHE_REFERENCED、DCACHE_LRU_LIST 等标志
- `d_seq`: 序列号，用于 RCU 查找中的 ABA 问题防护
- `d_inode`: 指向关联的 inode，NULL 表示这是一个负 dentry（文件不存在）
- `d_lockref`: 合并了自旋锁和引用计数 (lockref 结构)
- `d_lru`: 用于 LRU 缓存回收

### 2.2 dcache 哈希表

**源码位置**: `fs/dcache.c` 第 113-131 行

```c
static unsigned int d_hash_shift __ro_after_init __used;
static struct hlist_bl_head *dentry_hashtable __ro_after_init __used;

// 哈希函数
static inline struct hlist_bl_head *d_hash(unsigned long hashlen)
{
    return runtime_const_ptr(dentry_hashtable) +
        runtime_const_shift_right_32(hashlen, d_hash_shift);
}

// 正在查找的 dentry 的独立哈希表（避免与正常查找冲突）
#define IN_LOOKUP_SHIFT 10
static struct hlist_bl_head in_lookup_hashtable[1 << IN_LOOKUP_SHIFT];

static inline struct hlist_bl_head *in_lookup_hash(const struct dentry *parent,
                        unsigned int hash)
{
    hash += (unsigned long) parent / L1_CACHE_BYTES;
    return in_lookup_hashtable + hash_32(hash, IN_LOOKUP_SHIFT);
}
```

**dcache 哈希表结构图解**:

```
dentry_hashtable[]
    │
    ├── [0] ─→ dentry_A ─→ dentry_B
    ├── [1] ─→ dentry_C
    ├── [2] ─→ (empty)
    ├── ...
    └── [N] ─→ dentry_X

哈希计算: hash = full_name_hash(parent, name, len)
         bucket = hash & (d_hash_shift_mask)
```

### 2.3 d_lookup() 查找流程

**源码位置**: `fs/dcache.c` 第 2387-2471 行

```c
struct dentry *d_lookup(const struct dentry *parent, const struct qstr *name)
{
    struct dentry *dentry;
    unsigned seq;

    do {
        seq = read_seqbegin(&rename_lock);
        dentry = __d_lookup(parent, name);
        if (dentry)
            break;
    } while (read_seqretry(&rename_lock, seq));
    return dentry;
}

struct dentry *__d_lookup(const struct dentry *parent, const struct qstr *name)
{
    unsigned int hash = name->hash;
    struct hlist_bl_head *b = d_hash(hash);
    struct hlist_bl_node *node;
    struct dentry *found = NULL;
    struct dentry *dentry;

    rcu_read_lock();
    
    hlist_bl_for_each_entry_rcu(dentry, node, b, d_hash) {
        if (dentry->d_name.hash != hash)
            continue;

        spin_lock(&dentry->d_lock);
        if (dentry->d_parent != parent)
            goto next;
        if (d_unhashed(dentry))
            goto next;

        if (!d_same_name(dentry, parent, name))
            goto next;

        dentry->d_lockref.count++;
        found = dentry;
        spin_unlock(&dentry->d_lock);
        break;
next:
        spin_unlock(&dentry->d_lock);
    }
    rcu_read_unlock();

    return found;
}
```

**查找流程图解**:

```
d_lookup(parent, name)
    │
    ├── read_seqbegin(&rename_lock)  // 获取序列号
    │
    ├── __d_lookup(parent, name)
    │       │
    │       ├── 计算 hash = name->hash
    │       ├── 定位 bucket = d_hash(hash)
    │       │
    │       ├── rcu_read_lock()
    │       ├── 遍历哈希桶中的 dentry
    │       │       │
    │       │       ├── 检查 hash 是否匹配
    │       │       ├── 检查 d_parent 是否匹配
    │       │       ├── 检查是否已 unhashed
    │       │       ├── 检查名称是否相同 (d_same_name)
    │       │       │
    │       │       └── 匹配: 增加引用计数，返回
    │       │
    │       └── rcu_read_unlock()
    │
    ├── 检查序列号是否变化
    │       ├── 变化: 重试
    │       └── 不变: 返回结果
    │
    └── dput(dentry)  // 使用后释放
```

### 2.4 d_add()/d_instantiate() 添加流程

**源码位置**: `fs/dcache.c` 第 2786-2793 行 (d_add) 和第 2747-2775 行 (__d_add)

```c
void d_add(struct dentry *entry, struct inode *inode)
{
    if (inode) {
        security_d_instantiate(entry, inode);
        spin_lock(&inode->i_lock);
    }
    __d_add(entry, inode, NULL);
}

// __d_add 是实际添加的核心函数
static void __d_add(struct dentry *dentry, struct inode *inode, 
                    const struct dentry_operations *ops)
{
    wait_queue_head_t *d_wait;
    struct inode *dir = NULL;
    unsigned n;

    spin_lock(&dentry->d_lock);
    
    // 如果 dentry 正在被查找，等待查找完成
    if (unlikely(d_in_lookup(dentry))) {
        dir = dentry->d_parent->d_inode;
        n = start_dir_add(dir);
        d_wait = __d_lookup_unhash(dentry);
    }
    
    // 设置 dentry_operations
    if (unlikely(ops))
        d_set_d_op(dentry, ops);
    
    // 如果有 inode，建立关联
    if (inode) {
        unsigned add_flags = d_flags_for_inode(inode);
        hlist_add_head(&dentry->d_u.d_alias, &inode->i_dentry);
        raw_write_seqcount_begin(&dentry->d_seq);
        __d_set_inode_and_type(dentry, inode, add_flags);
        raw_write_seqcount_end(&dentry->d_seq);
        fsnotify_update_flags(dentry);
    }
    
    // 加入哈希表
    __d_rehash(dentry);
    
    // 完成目录添加
    if (dir)
        end_dir_add(dir, n, d_wait);
        
    spin_unlock(&dentry->d_lock);
    if (inode)
        spin_unlock(&inode->i_lock);
}
```

### 2.5 目录项缓存回收机制

**dcache LRU 链表管理**: `fs/dcache.c` 第 489-552 行

```c
// 添加到 LRU
static void d_lru_add(struct dentry *dentry)
{
    D_FLAG_VERIFY(dentry, 0);
    dentry->d_flags |= DCACHE_LRU_LIST;
    this_cpu_inc(nr_dentry_unused);
    if (d_is_negative(dentry))
        this_cpu_inc(nr_dentry_negative);
    list_lru_add_obj(&dentry->d_sb->s_dentry_lru, &dentry->d_lru);
}

// 从 LRU 移除
static void d_lru_del(struct dentry *dentry)
{
    D_FLAG_VERIFY(dentry, DCACHE_LRU_LIST);
    dentry->d_flags &= ~DCACHE_LRU_LIST;
    this_cpu_dec(nr_dentry_unused);
    if (d_is_negative(dentry))
        this_cpu_dec(nr_dentry_negative);
    list_lru_del_obj(&dentry->d_sb->s_dentry_lru, &dentry->d_lru);
}
```

**dput() 释放流程**: `fs/dcache.c` 第 918-929 行

```c
void dput(struct dentry *dentry)
{
    if (!dentry)
        return;
    might_sleep();
    rcu_read_lock();
    if (likely(fast_dput(dentry))) {    // 快速路径
        rcu_read_unlock();
        return;
    }
    finish_dput(dentry);                 // 慢速路径
}
```

**回收决策流程**:

```
dput(dentry)
    │
    ├── fast_dput() 快速路径
    │       │
    │       ├── lockref_put_return() 尝试减少引用
    │       │
    │       ├── ret < 0 ? → 获取锁，重试
    │       ├── ret > 0 ? → 仅最后一个引用，return true
    │       │
    │       └── ret == 0 (最后引用)
    │               ├── retain_dentry() 是否保留?
    │               │       ├─ DCACHE_DONTCACHE → 释放
    │               │       ├─ DCACHE_OP_DELETE → 调用 d_op->d_delete
    │               │       └─ 其他情况 → 加入 LRU
    │               │
    │               └── retain → return true
    │                   否则 → 获取锁，进入 finish_dput
    │
    └── finish_dput() 慢速路径
            │
            ├── lock_for_kill() 尝试锁定 inode
            ├── __dentry_kill() 执行实际删除
            └── 递归处理父目录
```

---

## 3. super_block 子系统

### 3.1 struct super_block 数据结构

**源码位置**: `include/linux/fs/super_types.h` 第 132-250 行

```c
struct super_block {
    struct list_head        s_list;          // 超级块链表 (必须在前)
    dev_t                   s_dev;           // 设备号
    unsigned char           s_blocksize_bits; // 块大小位数
    unsigned long           s_blocksize;      // 块大小
    loff_t                  s_maxbytes;       // 最大文件大小
    struct file_system_type *s_type;         // 文件系统类型
    const struct super_operations *s_op;      // 超级块操作

    const struct dquot_operations *dq_op;     // quota 操作
    const struct quotactl_ops *s_qcop;       // quota 控制操作
    const struct export_operations *s_export_op; // 导出操作

    unsigned long           s_flags;          // 挂载标志
    unsigned long           s_iflags;         // 内部标志
    unsigned long           s_magic;          // 文件系统幻数
    struct dentry          *s_root;           // 根目录 dentry

    struct rw_semaphore     s_umount;         // umount 信号量
    int                     s_count;          // 引用计数
    atomic_t                s_active;         // 活跃引用计数

#ifdef CONFIG_SECURITY
    void                   *s_security;       // 安全模块数据
#endif
    const struct xattr_handler *const *s_xattr; // 扩展属性

    // 文件系统特定数据
    void                   *s_fs_info;

    // 时间粒度
    u32                     s_time_gran;     // c/m/atime 粒度 (ns)
    time64_t                s_time_min;       // 时间最小值
    time64_t                s_time_max;       // 时间最大值

    // 备选根目录 (NFS)
    struct hlist_bl_head    s_roots;
    
    // 挂载点列表
    struct mount            *s_mounts;

    // 块设备
    struct block_device     *s_bdev;
    struct backing_dev_info *s_bdi;

    // 实例链表
    struct hlist_node       s_instances;

    // 配额信息
    struct quota_info       s_dquot;

    // 写者计数器
    struct sb_writers       s_writers;

    // UUID 和名称
    char                    s_id[32];         // 信息名称
    uuid_t                  s_uuid;           // UUID

    // 子类型
    const char             *s_subtype;

    // 默认 dentry 操作
    const struct dentry_operations *__s_d_op;

    // 每-superblock 的 shrinker
    struct shrinker         *s_shrink;

    // 删除计数
    atomic_long_t           s_remove_count;

    // 只读重挂载状态
    int                     s_readonly_remount;

    // 错误序列
    errseq_t                s_wb_err;

    // 用户命名空间
    struct user_namespace  *s_user_ns;
};
```

### 3.2 super_operations 操作向量

**源码位置**: `include/linux/fs/super_types.h` 第 83-130 行

```c
struct super_operations {
    // inode 分配/释放
    struct inode *(*alloc_inode)(struct super_block *sb);
    void (*destroy_inode)(struct inode *inode);
    void (*free_inode)(struct inode *inode);

    // inode 写回
    void (*dirty_inode)(struct inode *inode, int flags);
    int (*write_inode)(struct inode *inode, struct writeback_control *wbc);
    int (*drop_inode)(struct inode *inode);
    void (*evict_inode)(struct inode *inode);

    // 超级块操作
    void (*put_super)(struct super_block *sb);
    int (*sync_fs)(struct super_block *sb, int wait);
    int (*freeze_super)(struct super_block *sb, enum freeze_holder who,
                        const void *owner);
    int (*freeze_fs)(struct super_block *sb);
    int (*thaw_super)(struct super_block *sb, enum freeze_holder who,
                      const void *owner);
    int (*unfreeze_fs)(struct super_block *sb);

    // 文件系统统计
    int (*statfs)(struct dentry *dentry, struct kstatfs *kstatfs);
    void (*umount_begin)(struct super_block *sb);

    // 选项显示
    int (*show_options)(struct seq_file *seq, struct dentry *dentry);
    int (*show_devname)(struct seq_file *seq, struct dentry *dentry);
    int (*show_path)(struct seq_file *seq, struct dentry *dentry);
    int (*show_stats)(struct seq_file *seq, struct dentry *dentry);

    // Quota 操作
#ifdef CONFIG_QUOTA
    ssize_t (*quota_read)(struct super_block *sb, int type, char *data,
                          size_t len, loff_t off);
    ssize_t (*quota_write)(struct super_block *sb, int type,
                          const char *data, size_t len, loff_t off);
    struct dquot __rcu **(*get_dquots)(struct inode *inode);
#endif

    // 对象计数
    long (*nr_cached_objects)(struct super_block *sb, struct shrink_control *sc);
    long (*free_cached_objects)(struct super_block *sb, struct shrink_control *sc);

    // 设备操作
    int (*remove_bdev)(struct super_block *sb, struct block_device *bdev);
    void (*shutdown)(struct super_block *sb);

    // 错误报告
    void (*report_error)(const struct fserror_event *event);
};
```

### 3.3 alloc_super() 创建流程

**源码位置**: `fs/super.c` 第 317-400 行

```c
static struct super_block *alloc_super(struct file_system_type *type, int flags,
                       struct user_namespace *user_ns)
{
    struct super_block *s = kzalloc_obj(struct super_block);
    static const struct super_operations default_op;
    int i;

    if (!s)
        return NULL;

    // 初始化用户命名空间
    s->s_user_ns = get_user_ns(user_ns);
    
    // 初始化 umount 信号量
    init_rwsem(&s->s_umount);
    lockdep_set_class(&s->s_umount, &type->s_umount_key);

    // 安全模块分配
    if (security_sb_alloc(s))
        goto fail;

    // 初始化写者信号量
    for (i = 0; i < SB_FREEZE_LEVELS; i++) {
        if (__percpu_init_rwsem(&s->s_writers.rw_sem[i], ...))
            goto fail;
    }
    
    // 初始化块设备信息
    s->s_bdi = &noop_backing_dev_info;
    s->s_flags = flags;
    
    // 初始化链表头
    INIT_HLIST_NODE(&s->s_instances);
    INIT_HLIST_BL_HEAD(&s->s_roots);
    mutex_init(&s->s_sync_lock);
    INIT_LIST_HEAD(&s->s_inodes);
    spin_lock_init(&s->s_inode_list_lock);
    INIT_LIST_HEAD(&s->s_inodes_wb);
    spin_lock_init(&s->s_inode_wblist_lock);

    // 设置默认操作
    s->s_op = &default_op;
    s->s_maxbytes = MAX_NON_LFS;
    s->s_time_gran = 1000000000;  // 1秒
    s->s_time_min = TIME64_MIN;
    s->s_time_max = TIME64_MAX;

    // 初始化 shrinker
    s->s_shrink = shrinker_alloc(SHRINKER_NUMA_AWARE | SHRINKER_MEMCG_AWARE, ...);
    if (!s->s_shrink)
        goto fail;

    s->s_shrink->scan_objects = super_cache_scan;
    s->s_shrink->count_objects = super_cache_count;
    s->s_shrink->private_data = s;

    // 初始化 LRU 列表
    if (list_lru_init_memcg(&s->s_dentry_lru, s->s_shrink))
        goto fail;
    if (list_lru_init_memcg(&s->s_inode_lru, s->s_shrink))
        goto fail;

    s->s_min_writeback_pages = MIN_WRITEBACK_PAGES;
    return s;

fail:
    destroy_unused_super(s);
    return NULL;
}
```

### 3.4 sget_fc() 超级块查找/创建

**源码位置**: `fs/super.c` 第 734-799 行

```c
struct super_block *sget_fc(struct fs_context *fc,
                int (*test)(struct super_block *, struct fs_context *),
                int (*set)(struct super_block *, struct fs_context *))
{
    struct super_block *s = NULL;
    struct super_block *old;
    struct user_namespace *user_ns = fc->global ? &init_user_ns : fc->user_ns;
    int err;

retry:
    spin_lock(&sb_lock);
    
    // 查找已存在的超级块
    if (test) {
        hlist_for_each_entry(old, &fc->fs_type->fs_supers, s_instances) {
            if (test(old, fc))
                goto share_extant_sb;
        }
    }
    
    // 需要创建新的超级块
    if (!s) {
        spin_unlock(&sb_lock);
        s = alloc_super(fc->fs_type, fc->sb_flags, user_ns);
        if (!s)
            return ERR_PTR(-ENOMEM);
        goto retry;
    }

    // 初始化新超级块
    s->s_fs_info = fc->s_fs_info;
    err = set(s, fc);
    if (err) {
        s->s_fs_info = NULL;
        spin_unlock(&sb_lock);
        destroy_unused_super(s);
        return ERR_PTR(err);
    }
    
    // 设置文件系统类型
    s->s_type = fc->fs_type;
    s->s_iflags |= fc->s_iflags;
    strscpy(s->s_id, s->s_type->name, sizeof(s->s_id));
    
    // 加入全局链表
    list_add_tail(&s->s_list, &super_blocks);
    hlist_add_head(&s->s_instances, &s->s_type->fs_supers);
    spin_unlock(&sb_lock);
    
    get_filesystem(s->s_type);
    shrinker_register(s->s_shrink);
    return s;

share_extant_sb:
    // 复用已存在的超级块
    ...
}
```

**sget_fc 流程图解**:

```
sget_fc(fc, test, set)
    │
    ├── 检查用户命名空间权限
    │
    ├── spin_lock(&sb_lock)
    │
    ├── 遍历 fs_type->fs_supers 查找匹配
    │       │
    │       └── 找到匹配 (test() 返回 true)
    │               │
    │               ├── 检查 exclusive 标志
    │               ├── 检查用户命名空间
    │               │
    │               └── grab_super() 获取引用
    │
    ├── 未找到匹配
    │       │
    │       ├── alloc_super() 分配新超级块
    │       ├── set(s, fc) 调用文件系统设置回调
    │       ├── 设置 s_type, s_iflags
    │       │
    │       └── 加入全局链表
    │
    └── 返回超级块
```

---

## 4. file 子系统

### 4.1 struct file 数据结构

**源码位置**: `include/linux/fs.h` 第 1259-1300 行

```c
struct file {
    spinlock_t              f_lock;           // 保护 f_ep, f_flags
    fmode_t                 f_mode;           // FMODE_* 标志
    const struct file_operations *f_op;        // 文件操作
    struct address_space   *f_mapping;        // 页面缓存映射
    void                   *private_data;      // 文件系统私有数据
    struct inode           *f_inode;          // 缓存的 inode
    unsigned int            f_flags;          // open 标志
    unsigned int            f_iocb_flags;     // iocb 标志
    const struct cred      *f_cred;          // 创建者凭证
    struct fown_struct     *f_owner;          // 文件所有者

    union {
        const struct path   f_path;            // 路径 (只读访问)
        struct path        __f_path;          // 可写别名，仅在文件打开前使用
    };

    union {
        struct mutex        f_pos_lock;        // 文件位置锁 (目录和 FMODE_ATOMIC_POS)
        u64                 f_pipe;           // 管道专用
    };
    loff_t                  f_pos;            // 文件位置

#ifdef CONFIG_SECURITY
    void                   *f_security;        // LSM 安全上下文
#endif

    errseq_t                f_wb_err;         // 写回错误
    errseq_t                f_sb_err;         // 超级块错误

#ifdef CONFIG_EPOLL
    struct hlist_head      *f_ep;             // epoll 钩子链表
#endif

    union {
        struct callback_head f_task_work;      // 任务工作
        struct llist_node   f_llist;          // 
        struct file_ra_state f_ra;            // 预读状态
        freeptr_t           f_freeptr;        // SLAB_TYPESAFE_BY_RCU 指针
    };

    file_ref_t              f_ref;             // 引用计数
};
```

### 4.2 struct path 路径结构

**源码位置**: `include/linux/path.h`

```c
struct path {
    struct vfsmount *mnt;      // 挂载点
    struct dentry   *dentry;    // 目录项
};
```

### 4.3 file_operations 文件操作

**源码位置**: `include/linux/fs.h` 第 1926-1970 行

```c
struct file_operations {
    struct module           *owner;
    fop_flags_t              fop_flags;

    // 定位
    loff_t (*llseek)(struct file *, loff_t, int);

    // 读写
    ssize_t (*read)(struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write)(struct file *, const char __user *, size_t, loff_t *);
    
    // 迭代器读写
    ssize_t (*read_iter)(struct kiocb *, struct iov_iter *);
    ssize_t (*write_iter)(struct kiocb *, struct iov_iter *);

    // I/O 轮询
    int (*iopoll)(struct kiocb *, struct io_comp_batch *, unsigned int flags);
    
    // 目录迭代
    int (*iterate_shared)(struct file *, struct dir_context *);
    
    // 轮询
    __poll_t (*poll)(struct file *, struct poll_table_struct *);

    // IOCTL
    long (*unlocked_ioctl)(struct file *, unsigned int, unsigned long);
    long (*compat_ioctl)(struct file *, unsigned int, unsigned long);

    // 内存映射
    int (*mmap)(struct file *, struct vm_area_struct *);

    // 打开/释放
    int (*open)(struct inode *, struct file *);
    int (*flush)(struct file *, fl_owner_t id);
    int (*release)(struct inode *, struct file *);

    // 同步
    int (*fsync)(struct file *, loff_t, loff_t, int datasync);
    int (*fasync)(int, struct file *, int);

    // 文件锁
    int (*lock)(struct file *, int, struct file_lock *);

    // 获取未映射区域
    unsigned long (*get_unmapped_area)(struct file *, unsigned long, 
                                       unsigned long, unsigned long, unsigned long);

    // 文件锁
    int (*check_flags)(int);
    int (*flock)(struct file *, int, struct file_lock *);

    // 拼接操作
    ssize_t (*splice_write)(struct pipe_inode_info *, struct file *, loff_t *, 
                           size_t, unsigned int);
    ssize_t (*splice_read)(struct file *, loff_t *, struct pipe_inode_info *, 
                          size_t, unsigned int);

    // 租约
    int (*setlease)(struct file *, int, struct file_lease **, void **);

    // 预分配
    long (*fallocate)(struct file *, int mode, loff_t offset, loff_t len);

    // 文件复制
    ssize_t (*copy_file_range)(struct file *, loff_t, struct file *,
                               loff_t, size_t, unsigned int);
    
    // 范围重映射
    loff_t (*remap_file_range)(struct file *, loff_t, struct file *, loff_t,
                               loff_t, unsigned int);

    // fadvise
    int (*fadvise)(struct file *, loff_t, loff_t, int);

    // io_uring 命令
    int (*uring_cmd)(struct io_uring_cmd *, unsigned int);
    int (*uring_cmd_iopoll)(struct io_uring_cmd *, struct io_comp_batch *,
                           unsigned int);
};
```

### 4.4 fdtable 文件描述符表

**源码位置**: `include/linux/fdtable.h` 第 26-74 行

```c
struct fdtable {
    unsigned int max_fds;           // 最大文件描述符数
    struct file **fd;               // 文件指针数组 (指向 fdtab.fd)
    unsigned long *close_on_exec;   // exec 时关闭的标志位图
    unsigned long *open_fds;        // 打开的标志位图
    unsigned int next_fd;           // 下一个可用 fd
    
    struct callback_head rcu;        // RCU 头
};

struct files_struct {
    atomic_t count;                  // 引用计数
    struct fdtable __rcu *fdt;      //指向当前 fdtable
    struct fdtable fdtab;            // 基础的 fdtable

    // ...
};
```

### 4.5 文件描述符分配

**源码位置**: `fs/file.c` (内核文件描述符分配)

文件描述符分配使用 `alloc_fd()` 函数，流程如下：

```c
int alloc_fd(unsigned start, unsigned end, unsigned flags)
{
    struct files_struct *files = current->files;
    struct fdtable *fdt = files_fdtable(files);
    int fd;
    
    // 在位图中查找空闲位置
    fd = find_next_zero_bit(fdt->open_fds, fdt->max_fds, start);
    
    // 检查是否超出限制
    if (fd >= end)
        return -EMFILE;
        
    // 分配新的 fd
    if (fd >= fdt->max_fds) {
        // 需要扩展 fdtable
        fd = expand_fdtable(files, fd);
        if (IS_ERR_VALUE(fd))
            return fd;
    }
    
    // 设置标志位
    __set_open_fd(fd, fdt);
    if (flags & O_CLOEXEC)
        __set_close_on_exec(fd, fdt);
    else
        __clear_close_on_exec(fd, fdt);
    
    // 初始化 file * 为 NULL
    fdt->fd[fd] = NULL;
    
    // 更新 next_fd 提示
    if (fd > fdt->next_fd)
        fdt->next_fd = fd + 1;
        
    return fd;
}
```

---

## 5. address_space 子系统

### 5.1 struct address_space 数据结构

**源码位置**: `include/linux/fs.h` 第 449-490 行

```c
struct address_space {
    struct inode           *host;              // 所有者 inode
    struct xarray          i_pages;            // 页缓存 XArray
    struct rw_semaphore    invalidate_lock;    // 失效锁
    gfp_t                  gfp_mask;           // 内存分配标志
    atomic_t               i_mmap_writable;   // 可写映射计数

#ifdef CONFIG_READ_ONLY_THP_FOR_FS
    atomic_t               nr_thps;            // THP 数量
#endif

    struct rb_root_cached   i_mmap;            // 私有/共享映射树
    unsigned long           nrpages;           // 页数
    pgoff_t                 writeback_index;   // 写回起始位置
    const struct address_space_operations *a_ops; // 地址空间操作
    unsigned long           flags;             // 错误标志 (AS_*)
    errseq_t                wb_err;            // 最近错误
    spinlock_t              i_private_lock;    // 私有锁
    struct list_head        i_private_list;    // 私有链表
    struct rw_semaphore     i_mmap_rwsem;     // 映射读写信号量
    void                   *i_private_data;    // 私有数据
};
```

### 5.2 radix_tree/XArray 页缓存

Linux 内核使用 **XArray** (从 radix_tree 升级而来) 管理页缓存。

**关键结构**:

```c
// XArray 标记定义 (fs.h 第 497-500 行)
#define PAGECACHE_TAG_DIRTY     XA_MARK_0    // 脏页
#define PAGECACHE_TAG_WRITEBACK XA_MARK_1   // 正在写回
#define PAGECACHE_TAG_TOWRITE   XA_MARK_2   // 即将写回
```

**页面查找** (使用 find_get_page 等):

```c
struct page *find_get_page(struct address_space *mapping, pgoff_t offset)
{
    XA_STATE(xas, &mapping->i_pages, offset);
    struct page *page;

    rcu_read_lock();
    page = xas_load(&xas);
    if (page && !xa_is_value(page)) {
        if (page_ref_inc_not_zero(page))
            get_page(page);
        else
            page = NULL;
    }
    rcu_read_unlock();
    
    return page;
}
```

### 5.3 writeback 写回机制

**脏页写回流程**:

```
进程修改文件页
    │
    ├── mark_page_dirty(address_space, page)
    │       │
    │       ├── 设置页为脏 (PAGECACHE_TAG_DIRTY)
    │       │
    │       └── 将页加入到 inode->i_io_list
    │
    └── 定时或主动触发写回
            │
            ├── wakeup_flusher_threads() 唤醒 flusher
            │
            └── flusher 进程执行
                    │
                    ├── wb_writeback() 遍历脏 inode
                    │       │
                    │       └── writeback_sb_inodes()
                    │               │
                    │               └── do_writepages()
                    │                       │
                    │                       └── mapping->a_ops->writepages()
                    │
                    └── 写回完成后
                            │
                            ├── 清除 PAGECACHE_TAG_DIRTY
                            │
                            └── 更新 i_state
```

**writeback_control 结构** (用于控制写回):

```c
struct writeback_control {
    enum writeback_sync_modes sync_mode;      // 同步模式
    unsigned int nr_to_write;                  // 应写页数
    unsigned long pages_skipped;               // 跳过的页数
    
    /* for interoperability with data integrity interfaces */
    struct blk_plug *plug;
    
    /* If set, don't io schedule between pages */
    bool mood_for_requeue;
};
```

---

## 知识点关联表

| 概念 | 关键结构体 | 关键函数 | 源码位置 |
|------|-----------|---------|---------|
| **inode** | `struct inode` | `inode_init_always()` | `fs/inode.c:228` |
| | `inode_operations` | `inode_owner_or_capable()` | `fs/inode.c:2695` |
| **dentry** | `struct dentry` | `d_lookup()` | `fs/dcache.c:2387` |
| | `dentry_operations` | `d_add()` | `fs/dcache.c:2786` |
| | dcache 哈希表 | `__d_lookup()` | `fs/dcache.c:2417` |
| **super_block** | `struct super_block` | `alloc_super()` | `fs/super.c:317` |
| | `super_operations` | `sget_fc()` | `fs/super.c:734` |
| | | `generic_shutdown_super()` | `fs/super.c:618` |
| **file** | `struct file` | `alloc_empty_file()` | `fs/file_table.c:218` |
| | `file_operations` | `do_file_open()` | `fs/open.c` |
| | `fdtable` | `alloc_fd()` | `fs/file.c` |
| **address_space** | `struct address_space` | `find_get_page()` | `mm/filemap.c` |
| | XArray/radix_tree | `mapping->i_pages` | `include/linux/xarray.h` |
| | | `writeback_inode()` | `fs/fs-writeback.c` |

### 锁依赖关系表

| 锁类型 | 保护对象 | 层级关系 |
|-------|---------|---------|
| `inode->i_lock` | inode 状态、i_hash、i_io_list | 最内层 |
| `inode->i_rwsem` | inode 内容修改 | 依赖 i_lock |
| `sb->s_inode_list_lock` | super_block inode 链表 | 依赖 i_lock |
| `dentry->d_lock` | dentry 状态、d_lru | 最内层 |
| `sb->s_dentry_lru_lock` | dentry LRU | 依赖 d_lock |
| `sb->s_umount` | super_block 卸载 | 外层锁 |
| `rename_lock` | dcache 并发查找 | seqlock 机制 |
| `mapping->invalidate_lock` | address_space 内容失效 | 保护 i_mmap |

### 内存分配路径

```
用户空间 open()
    │
    └── do_file_open()
            │
            ├── alloc_empty_file()  // 分配 struct file
            │       │
            │       └── kmem_cache_alloc(filp_cachep, GFP_KERNEL)
            │
            ├── do_dentry_open()
            │       │
            │       └── f->f_op->open(inode, f)  // 调用文件系统
            │
            └── fdinstall()  // 安装到 fdtable
```

```
目录查找 path_lookupat()
    │
    └── link_path_walk()
            │
            ├── d_hash_and_lookup()  // 计算 hash 并查找
            │       │
            │       ├── full_name_hash()  // 计算哈希
            │       │
            │       └── d_lookup()  // 查找 dentry
            │               │
            │               └── __d_lookup()  // RCU 保护查找
            │
            └── step_into()
                    │
                    └── dget()  // 增加引用
```

---

## 参考源码文件

- **fs/inode.c**: inode 分配、释放、查找
- **fs/dcache.c**: dentry 缓存管理、哈希表操作
- **fs/super.c**: super_block 分配、挂载、卸载
- **fs/file_table.c**: file 结构分配
- **fs/internal.h**: VFS 内部函数声明
- **include/linux/fs.h**: 核心数据结构定义
- **include/linux/dcache.h**: dentry 相关定义
- **include/linux/fs/super_types.h**: super_block 和 super_operations
- **include/linux/fs/super.h**: super_block 辅助函数

---

*文档版本: R1*
*生成时间: 2026-04-26*
*分析基于: Linux Kernel VFS 子系统*
