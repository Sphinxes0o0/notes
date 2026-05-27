# VFS 核心数据结构

## 1. 模块架构

### 1.1 功能概述

VFS 核心数据结构包括 super_block、inode、dentry、file 等，它们共同构成了 Linux 虚拟文件系统的基石。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `include/linux/fs.h` | 核心数据结构定义 |
| `include/linux/mount.h` | 挂载点结构 |
| `include/linux/dcache.h` | 目录项结构 |
| `include/linux/fs/super_types.h` | superblock 类型 |

## 2. struct super_block

### 2.1 定义

```c
// include/linux/fs/super_types.h:132
struct super_block {
    struct list_head        s_list;         // 全局链表
    dev_t                   s_dev;          // 设备号
    unsigned char           s_blocksize_bits;
    unsigned long           s_blocksize;
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
    struct list_lru         s_dentry_lru;   // dentry LRU
    struct list_lru         s_inode_lru;    // inode LRU
};
```

### 2.2 关键成员说明

| 成员 | 类型 | 用途 |
|------|------|------|
| `s_list` | `struct list_head` | 链接到全局 super_blocks 链表 |
| `s_root` | `struct dentry *` | 文件系统根目录的 dentry |
| `s_op` | `const struct super_operations *` | 指向 superblock 操作函数表 |
| `s_type` | `struct file_system_type *` | 文件系统类型描述符 |
| `s_count` | `int` | 引用计数 |
| `s_active` | `atomic_t` | 活跃引用计数 (mount 使用) |

## 3. struct inode

### 3.1 定义

```c
// include/linux/fs.h:766
struct inode {
    umode_t                 i_mode;        // 文件类型和权限
    unsigned short          i_opflags;
    kuid_t                 i_uid;          // 用户 ID
    kgid_t                 i_gid;          // 组 ID
    const struct inode_operations *i_op;   // inode 操作
    struct super_block      *i_sb;          // 所属超级块
    struct address_space    *i_mapping;    // 地址空间
    unsigned long           i_ino;          // inode 编号
    union {
        unsigned int        i_nlink;       // 硬链接计数
        atomic_t            i_dio_count;
    };
    dev_t                   i_rdev;        // 设备号
    loff_t                  i_size;         // 文件大小
    struct timespec64      i_atime;        // 访问时间
    struct timespec64      i_mtime;        // 修改时间
    struct timespec64      i_ctime;        // 状态改变时间
    struct timespec64      i_btime;        // 创建时间
    atomic_t                i_count;        // 引用计数
    atomic_t                i_dio_count;
    struct ext *i_ext;                    // 扩展属性
    struct list_head        i_dentry;      // dentry 别名链表
    unsigned long           i_state;
    struct inode *i_parent;              // 父 inode
    struct dentry *i_dentry;            // 主 dentry
    unsigned long           i_flags;
    struct file_lock_context *i_flctx;
    struct address_space    i_data;
    struct list_head        i_wb_list;
    // ...
};
```

### 3.2 inode 状态标志

```c
// include/linux/fs.h
enum {
    I_LOCK          = 0,
    I_NEW           = 1,
    I_DIRTY_INODE   = 2,
    I_DIRTY_PAGES   = 3,
    I_FREEING       = 4,
    I_CLEAR         = 5,
    I_SYNC         = 6,
};
```

## 4. struct dentry

### 4.1 定义

```c
// include/linux/dcache.h:92
struct dentry {
    unsigned int d_flags;                 // 标志
    seqcount_spinlock_t d_seq;          // RCU 序列号
    struct hlist_bl_node d_hash;         // 哈希链表节点
    struct dentry *d_parent;            // 父目录
    struct qstr d_name;                 // 文件名
    struct inode *d_inode;              // 关联的 inode
    const struct dentry_operations *d_op; // dentry 操作
    struct super_block *d_sb;            // 所属超级块
    struct lockref d_lockref;           // 锁和引用计数
    struct list_head d_lru;             // LRU 链表
    struct hlist_node d_sib;           // 同级节点
    struct hlist_head d_children;       // 子目录链表
    union {
        struct hlist_node d_alias;      // inode 别名
        struct rcu_head d_rcu;          // RCU 头
    } d_u;
};
```

### 4.2 dentry 状态

```c
// include/linux/dcache.h
#define DCACHE_ENTRY_TYPE        (7 << 19)
#define DCACHE_MISS_TYPE         (0 << 19)
#define DCACHE_DIRECTORY_TYPE    (2 << 19)
#define DCACHE_REGULAR_TYPE      (4 << 19)
#define DCACHE_SYMLINK_TYPE      (6 << 19)
#define DCACHE_LRU_LIST          BIT(18)
#define DCACHE_DISCONNECTED      BIT(5)
#define DCACHE_REFERENCED        BIT(6)
```

## 5. struct file

### 5.1 定义

```c
// include/linux/fs.h:1259
struct file {
    union {
        const struct file_operations *f_op;  // 文件操作
        const struct path *f_path;
    };
    struct address_space    *f_mapping;      // 地址空间
    void                    *private_data;  // 私有数据
    struct inode            *f_inode;        // 关联 inode
    unsigned int            f_flags;         // open 标志
    fmode_t                f_mode;           // 文件模式
    loff_t                  f_pos;           // 文件位置
    struct fown_struct      *f_owner;        // 文件所有者
    const struct cred      *f_cred;         // 凭证
    struct path             f_path;          // 文件路径
    file_ref_t              f_ref;           // 引用计数
    // ...
};
```

## 6. struct vfsmount

### 6.1 定义

```c
// include/linux/mount.h:58
struct vfsmount {
    struct dentry *mnt_root;              // 挂载树根目录
    struct super_block *mnt_sb;          // 超级块
    int mnt_flags;                       // 挂载标志
    struct mnt_idmap *mnt_idmap;         // UID/GID 映射
};
```

### 6.2 挂载标志

```c
#define MNT_NOSUID      0x01   // 不执行 setuid
#define MNT_NODEV       0x02   // 不允许访问设备
#define MNT_NOEXEC      0x04   // 不允许执行
#define MNT_NOATIME     0x08   // 不更新访问时间
#define MNT_NODIRATIME  0x10   // 不更新目录访问时间
#define MNT_RELATIME    0x20   // 相对 atime
#define MNT_READONLY    0x40   // 只读
```

## 7. 数据结构关系图

```
super_block
    |
    +-- s_root ──────> dentry (根目录)
    |                      |
    |                      +-- d_parent ──> dentry (父目录)
    |                      |
    |                      +-- d_inode ───> inode
    |
    +-- s_op ─────────> super_operations
    |
    +-- s_type ──────> file_system_type

inode
    |
    +-- i_sb ─────────> super_block
    |
    +-- i_op ─────────> inode_operations
    |
    +-- i_mapping ────> address_space
    |
    +-- i_dentry ─────> dentry (通过 d_alias)

file
    |
    +-- f_inode ──────> inode
    |
    +-- f_op ─────────> file_operations
    |
    +-- f_path ───────> path
                          |
                          +-- dentry
                          +-- vfsmount
```

## 8. 数据结构创建/销毁流程

### 8.1 super_block 创建

```c
// fs/super.c
struct super_block *alloc_super(struct file_system_type *type, ...)
{
    // 1. 分配内存
    s = kzalloc_obj(struct super_block);
    // 2. 初始化信号量和锁
    init_rwsem(&s->s_umount);
    // 3. 初始化 LRU 列表
    list_lru_init(&s->s_dentry_lru);
    list_lru_init(&s->s_inode_lru);
    // 4. 设置引用计数
    s->s_count = 1;
    atomic_set(&s->s_active, 1);
    return s;
}
```

### 8.2 inode 创建

```c
// fs/inode.c
struct inode *alloc_inode(struct super_block *sb)
{
    const struct super_operations *ops = sb->s_op;
    struct inode *inode;

    // 1. 优先使用文件系统特定的分配
    if (ops->alloc_inode)
        inode = ops->alloc_inode(sb);
    else
        inode = alloc_inode_sb(sb, inode_cachep, GFP_KERNEL);

    // 2. 初始化
    inode_init_always(sb, inode);

    return inode;
}
```

### 8.3 dentry 创建

```c
// fs/dcache.c
struct dentry *d_alloc(struct dentry *parent, const struct qstr *name)
{
    struct dentry *dentry;

    // 1. 从 slab 缓存分配
    dentry = kmem_cache_alloc(dentry_cache, GFP_KERNEL);

    // 2. 初始化
    dentry->d_name = name;
    dentry->d_parent = parent;
    dentry->d_inode = NULL;
    lockref_init(&dentry->d_lockref);

    return dentry;
}
```
