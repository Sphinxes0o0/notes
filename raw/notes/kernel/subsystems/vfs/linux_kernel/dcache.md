# VFS Dentry 缓存

## 1. 模块架构

### 1.1 功能概述

Dentry (目录项) 缓存是 VFS 用来加速路径名解析的核心机制。通过缓存最近使用的 dentry 对象，减少对底层文件系统的访问。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `fs/dcache.c` | dentry 缓存实现 |
| `include/linux/dcache.h` | dentry 结构定义 |
| `fs/dcache_internal.h` | 内部接口 |

## 2. 核心数据结构

### 2.1 struct dentry

```c
// include/linux/dcache.h:92
struct dentry {
    unsigned int            d_flags;          // 标志
    seqcount_spinlock_t     d_seq;            // RCU 序列号
    struct hlist_bl_node    d_hash;           // 哈希链表节点
    struct dentry          *d_parent;         // 父目录
    struct qstr             d_name;           // 文件名
    struct inode           *d_inode;          // 关联的 inode
    const struct dentry_operations *d_op;      // dentry 操作
    struct super_block      *d_sb;            // 所属超级块
    struct lockref          d_lockref;       // 锁和引用计数
    struct list_head        d_lru;           // LRU 链表
    struct hlist_node       d_sib;            // 同级节点
    struct hlist_head       d_children;       // 子目录链表
    union {
        struct hlist_node   d_alias;          // inode 别名
        struct rcu_head     d_rcu;            // RCU 头
    } d_u;
};
```

### 2.2 struct qstr (文件名结构)

```c
// include/linux/dcache.h:42
struct qstr {
    unsigned int            hash;             // 文件名哈希值
    unsigned int            len;              // 文件名长度
    const unsigned char     *name;            // 文件名字符串
};
```

### 2.3 struct dentry_operations

```c
// include/linux/dcache.h:151
struct dentry_operations {
    int (*d_revalidate)(struct dentry *dentry, unsigned int flags);
    int (*d_weak_revalidate)(struct dentry *dentry, unsigned int flags);
    int (*d_hash)(const struct dentry *parent, struct qstr *name);
    int (*d_compare)(const struct dentry *parent, unsigned int len,
                     const char *str, const struct qstr *name);
    int (*d_delete)(const struct dentry *dentry);
    void (*d_release)(struct dentry *dentry);
    void (*d_prune)(struct dentry *dentry);
    void (*d_iput)(struct dentry *dentry, struct inode *inode);
    char *(*d_dname)(struct dentry *dentry, char *buffer, int buflen);
    struct vfsmount *(*d_automount)(struct path *path);
    int (*d_manage)(const struct path *path, bool rcu_walk);
    struct dentry *(*d_real)(struct dentry *dentry,
                             enum d_real_type type);
};
```

## 3. Dentry 哈希表

### 3.1 全局哈希表

```c
// fs/dcache.c:100
static struct hlist_bl_head *dentry_hashtable __read_mostly;
// 哈希表大小，由 DENTS_HASH_SIZE 决定
static inline struct hlist_bl_head *d_hash(unsigned int hash)
{
    return dentry_hashtable + (hash % d_hash_mask);
}
```

### 3.2 哈希函数

```c
// fs/dcache.c:200
static inline unsigned int d_hash_and_lookup(struct dentry *parent,
                                             struct qstr *name)
{
    unsigned int hash = full_name_hash(parent, name->name, name->len);
    name->hash = hash;
    return hash;
}
```

## 4. Dentry 缓存查找

### 4.1 d_lookup()

```c
// fs/dcache.c:450
struct dentry *d_lookup(struct dentry *parent, struct qstr *name)
{
    struct dentry *dentry;
    unsigned int hash = d_hash_and_lookup(parent, name);

    rcu_read_lock();
    hlist_bl_for_each_entry_rcu(dentry, &d_hash(hash), d_hash) {
        if (dentry->d_parent != parent)
            continue;
        if (dentry->d_name.hash != hash)
            continue;
        if (!dentry_cmp(dentry, name))
            continue;
        // 找到匹配的 dentry，增加引用计数
        spin_lock(&dentry->d_lock);
        if (!dentry->d_lockref.count)
            goto release;
        if (!lockref_get_not_dead(&dentry->d_lockref))
            goto release;
        spin_unlock(&dentry->d_lock);
        rcu_read_unlock();
        return dentry;
release:
        spin_unlock(&dentry->d_lock);
    }
    rcu_read_unlock();
    return NULL;
}
```

### 4.2 __d_lookup()

```c
// fs/dcache.c:420
struct dentry *__d_lookup(struct dentry *parent, struct qstr *name)
{
    struct dentry *dentry;
    unsigned int hash = name->hash;

    hlist_bl_for_each_entry_rcu(dentry, &d_hash(hash), d_hash) {
        if (dentry->d_parent != parent)
            continue;
        if (dentry->d_name.hash != hash)
            continue;
        if (!dentry_cmp(dentry, name))
            return dentry;
    }
    return NULL;
}
```

## 5. Dentry 创建与删除

### 5.1 d_alloc()

```c
// fs/dcache.c:280
struct dentry *d_alloc(struct dentry *parent, const struct qstr *name)
{
    struct dentry *dentry;

    // 从 slab 缓存分配
    dentry = kmem_cache_alloc(dentry_cache, GFP_KERNEL);
    if (!dentry)
        return NULL;

    // 初始化
    dentry->d_name = *name;
    dentry->d_parent = dget_parent(parent);
    dentry->d_inode = NULL;
    lockref_init(&dentry->d_lockref);

    // 加入父目录的 children 链表
    spin_lock(&parent->d_lock);
    hlist_add_head(&dentry->d_sib, &parent->d_children);
    spin_unlock(&parent->d_lock);

    // 加入全局哈希表
    d_hash_lock();
    hlist_bl_add_head_rcu(&dentry->d_hash, &d_hash(d_hash_and_lookup(parent, name)));
    d_hash_unlock();

    return dentry;
}
```

### 5.2 d_instantiate()

```c
// fs/dcache.c:320
void d_instantiate(struct dentry *dentry, struct inode *inode)
{
    spin_lock(&dentry->d_lock);
    WARN_ON(dentry->d_inode);
    dentry->d_inode = inode;
    if (inode)
        hlist_add_head(&dentry->d_alias, &inode->i_dentry);
    spin_unlock(&dentry->d_lock);
}
```

### 5.3 d_add()

```c
// fs/dcache.c:360
struct dentry *d_add(struct dentry *dentry, struct inode *inode)
{
    d_instantiate(dentry, inode);
    if (inode) {
        struct dentry *alias;
        spin_lock(&inode->i_lock);
        hlist_for_each_entry(alias, &inode->i_dentry, d_alias) {
            if (alias->d_flags & DCACHE_DISCONNECTED)
                continue;
            // 同一 inode 只能有一个连接的 dentry
        }
        spin_unlock(&inode->i_lock);
    }
    return dentry;
}
```

## 6. LRU 缓存

### 6.1 LRU 链表初始化

```c
// fs/dcache.c:150
void dcache_init(void)
{
    // 初始化全局 LRU 链表
    list_lru_init(&dentry_lru);
}
```

### 6.2 dentry_lru_isolate()

```c
// fs/dcache.c:600
static enum lru_status dentry_lru_isolate(struct list_head *item,
                                          struct list_lru_one *lru,
                                          spinlock_t *lru_lock,
                                          void *arg)
{
    struct dentry *dentry = container_of(item, struct dentry, d_lru);

    if (!spin_trylock(&dentry->d_lock))
        return LRU_ROTATE;

    if (dentry->d_lockref.count > 0) {
        spin_unlock(&dentry->d_lock);
        return LRU_SKIP;
    }

    // 从 LRU 和哈希表中移除
    list_del_init(&dentry->d_lru);
    hlist_bl_del_rcu(&dentry->d_hash);

    spin_unlock(&dentry->d_lock);

    // 释放 dentry
    kmem_cache_free(dentry_cache, dentry);

    return LRU_REMOVED;
}
```

## 7. RCU 机制

### 7.1 RCU 查找

```c
// fs/dcache.c:500
static struct dentry *d_lookup_rcu(struct dentry *parent, struct qstr *name)
{
    struct dentry *dentry;
    unsigned int hash = name->hash;

    rcu_read_lock();
    hlist_bl_for_each_entry_rcu(dentry, &d_hash(hash), d_hash) {
        if (dentry->d_parent != parent)
            continue;
        if (dentry->d_name.hash != hash)
            continue;
        if (!dentry_cmp(dentry, name))
            continue;
        // 检查是否正在被删除
        if (READ_ONCE(dentry->d_lockref.count) == 0)
            continue;
        return dentry;
    }
    rcu_read_unlock();
    return NULL;
}
```

### 7.2 RCU 延迟释放

```c
// fs/dcache.c:550
static void __d_free(struct rcu_head *head)
{
    struct dentry *dentry = container_of(head, struct dentry, d_u.d_rcu);
    kmem_cache_free(dentry_cache, dentry);
}
```

## 8. Lockref 机制

### 8.1 struct lockref

```c
// include/linux/lockref.h:30
struct lockref {
    union {
        struct {
            spinlock_t          lock;
            int                 count;
        };
        struct rwuqueued_spinlock key;
    };
};
```

### 8.2 lockref_get_not_dead()

```c
// lib/lockref.c:100
int lockref_get_not_dead(struct lockref *lockref)
{
    int ret;

    spin_lock(&lockref->lock);
    if (lockref->count > 0) {
        lockref->count++;
        ret = 1;
    } else {
        ret = 0;
    }
    spin_unlock(&lockref->lock);

    return ret;
}
```

## 9. 路径名解析流程

### 9.1 link_path_walk()

```c
// fs/namei.c:1500
static int link_path_walk(struct nameidata *nd, struct qstr *name)
{
    struct dentry *dentry;
    int err;

    // 查找目录
    dentry = lookup_hash(name, nd->path.dentry);
    if (IS_ERR(dentry))
        return PTR_ERR(dentry);

    // 检查是否为符号链接
    if (dentry->d_inode->i_opflags & IOP_NOFOLLOW)
        return -ENOENT;

    // 如果是符号链接，解析
    if (d_is_symlink(dentry))
        return step_into(nd, dentry);

    return 0;
}
```

## 10. Dentry 状态标志

```c
// include/linux/dcache.h:140
#define DCACHE_ENTRY_TYPE        (7 << 19)
#define DCACHE_MISS_TYPE         (0 << 19)
#define DCACHE_DIRECTORY_TYPE    (2 << 19)
#define DCACHE_REGULAR_TYPE      (4 << 19)
#define DCACHE_SYMLINK_TYPE      (6 << 19)
#define DCACHE_LRU_LIST          BIT(18)
#define DCACHE_DISCONNECTED      BIT(5)
#define DCACHE_REFERENCED        BIT(6)
#define DCACHE_DENTRY_KILLED     BIT(20)
```

## 11. 使用示例

### 11.1 典型查找流程

```c
// 用户空间路径查找
// open("/home/user/file", O_RDONLY);

struct path path;
int error;

error = kern_path("/home/user/file", 0, &path);
// 1. 解析 "/" -> 根目录 dentry
// 2. 查找 "home" -> dentry 缓存或文件系统
// 3. 查找 "user" -> dentry 缓存或文件系统
// 4. 查找 "file" -> dentry 缓存或文件系统
// 5. 返回最终 path
```

### 11.2 自动挂载点

```c
// fs/dcache.c:1800
static struct vfsmount *d_automount(struct path *path)
{
    struct vfsmount *mnt;
    struct dentry *dentry = path->dentry;

    if (!dentry->d_op->d_automount)
        return ERR_PTR(-EINVAL);

    mnt = dentry->d_op->d_automount(path);
    if (IS_ERR(mnt))
        return mnt;

    // 添加到挂载点
    return mnt;
}
```
