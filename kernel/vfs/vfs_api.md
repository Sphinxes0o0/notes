# VFS 抽象层 API

## 1. 模块架构

### 1.1 功能概述

VFS 通过六种主要 `*_operations` 函数表结构为具体文件系统提供统一接口。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `include/linux/fs.h` | 核心操作定义 |
| `include/linux/fs/super_types.h` | super_operations |
| `include/linux/dcache.h` | dentry_operations |
| `include/linux/exportfs.h` | export_operations |

## 2. struct super_operations

### 2.1 定义

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
    long (*nr_cached_objects)(struct super_block *sb, struct shrink_control *sc);
    long (*free_cached_objects)(struct super_block *sb, struct shrink_control *sc);
};
```

### 2.2 关键回调

| 回调 | 用途 |
|------|------|
| `alloc_inode` | 为文件系统分配新 inode |
| `evict_inode` | 从内存中清除 inode |
| `write_inode` | 将 inode 写回磁盘 |
| `put_super` | 卸载时释放 superblock |
| `sync_fs` | 同步文件系统元数据 |

## 3. struct inode_operations

### 3.1 定义

```c
// include/linux/fs.h:2001
struct inode_operations {
    struct dentry *(*lookup)(struct inode *dir, struct dentry *dentry,
                             unsigned int flags);
    const char *(*get_link)(struct dentry *, struct inode *,
                           struct delayed_call *);
    int (*permission)(struct mnt_idmap *idmap, struct inode *inode, int mask);
    struct posix_acl *(*get_acl)(struct mnt_idmap *idmap,
                                  struct dentry *dentry, int type);
    int (*create)(struct mnt_idmap *idmap, struct inode *dir,
                  struct dentry *dentry, umode_t mode, bool excl);
    int (*link)(struct dentry *old_dentry, struct inode *dir,
                struct dentry *dentry);
    int (*unlink)(struct inode *dir, struct dentry *dentry);
    int (*symlink)(struct mnt_idmap *idmap, struct inode *dir,
                   struct dentry *dentry, const char *oldname);
    struct dentry *(*mkdir)(struct mnt_idmap *idmap, struct inode *dir,
                            struct dentry *dentry, umode_t mode);
    int (*rmdir)(struct inode *dir, struct dentry *dentry);
    int (*mknod)(struct mnt_idmap *idmap, struct inode *dir,
                 struct dentry *dentry, umode_t mode, dev_t dev);
    int (*rename)(struct mnt_idmap *idmap, struct inode *old_dir,
                 struct dentry *old_dentry, struct inode *new_dir,
                 struct dentry *new_dentry, unsigned int flags);
    int (*setattr)(struct mnt_idmap *idmap, struct dentry *dentry,
                   struct iattr *attr);
    int (*getattr)(struct mnt_idmap *idmap, const struct path *path,
                   struct kstat *stat, u32 request_mask,
                   unsigned int flags);
    ssize_t (*listxattr)(struct dentry *dentry, char *list, size_t size);
    int (*atomic_open)(struct inode *dir, struct dentry *dentry,
                       struct file *file, unsigned open_flag, umode_t create_mode);
    int (*tmpfile)(struct mnt_idmap *idmap, struct inode *dir,
                   struct file *file, umode_t mode);
};
```

### 3.2 关键回调

| 回调 | 用途 |
|------|------|
| `lookup` | 目录查找，返回匹配的 dentry |
| `create` | 创建普通文件 |
| `mkdir` | 创建目录 |
| `unlink` | 删除文件 |
| `rename` | 重命名/移动 |
| `permission` | 权限检查 |

## 4. struct file_operations

### 4.1 定义

```c
// include/linux/fs.h:1926
struct file_operations {
    struct module *owner;
    loff_t (*llseek)(struct file *filp, loff_t offset, int whence);
    ssize_t (*read)(struct file *filp, char __user *buf,
                     size_t count, loff_t *pos);
    ssize_t (*write)(struct file *filp, const char __user *buf,
                      size_t count, loff_t *pos);
    ssize_t (*read_iter)(struct kiocb *iocb, struct iov_iter *to);
    ssize_t (*write_iter)(struct kiocb *iocb, struct iov_iter *from);
    int (*iterate_shared)(struct file *filp, struct dir_context *ctx);
    __poll_t (*poll)(struct file *filp, struct poll_table_struct *pt);
    long (*unlocked_ioctl)(struct file *filp, unsigned int cmd,
                           unsigned long arg);
    long (*compat_ioctl)(struct file *filp, unsigned int cmd,
                         unsigned long arg);
    int (*mmap)(struct file *filp, struct vm_area_struct *vma);
    int (*open)(struct inode *inode, struct file *filp);
    int (*flush)(struct file *filp, fl_owner_t id);
    int (*release)(struct inode *inode, struct file *filp);
    int (*fsync)(struct file *filp, loff_t start, loff_t end,
                 int datasync);
    int (*fasync)(int fd, struct file *filp, int on);
    ssize_t (*splice_read)(struct file *in, loff_t *ppos,
                           struct pipe_inode_info *pipe,
                           size_t len, unsigned int flags);
    ssize_t (*splice_write)(struct pipe_inode_info *pipe,
                             struct file *out, loff_t *ppos,
                             size_t len, unsigned int flags);
    int (*setlease)(struct file *filp, long arg, struct file_lease **lease,
                    void **priv);
    long (*fallocate)(struct file *filp, int mode, loff_t offset,
                      loff_t len);
    ssize_t (*copy_file_range)(struct file *file_in, loff_t pos_in,
                               struct file *file_out, loff_t pos_out,
                               size_t len, unsigned int flags);
};
```

### 4.2 关键回调

| 回调 | 用途 |
|------|------|
| `llseek` | 文件定位 |
| `read`/`read_iter` | 读数据 |
| `write`/`write_iter` | 写数据 |
| `open` | 打开文件 |
| `release` | 关闭文件 |
| `fsync` | 同步到磁盘 |

## 5. struct address_space_operations

### 5.1 定义

```c
// include/linux/fs.h:403
struct address_space_operations {
    int (*read_folio)(struct file *filp, struct folio *folio);
    int (*writepages)(struct address_space *mapping,
                      struct writeback_control *wbc);
    bool (*dirty_folio)(struct address_space *mapping, struct folio *folio);
    void (*readahead)(struct readahead_control *rac);
    int (*write_begin)(struct kiocb *iocb, struct address_space *mapping,
                       loff_t pos, unsigned len,
                       struct folio **folio_ret, void **private_ret);
    int (*write_end)(struct kiocb *iocb, struct address_space *mapping,
                     loff_t pos, unsigned copied, unsigned len,
                     struct folio *folio, void *private);
    sector_t (*bmap)(struct address_space *mapping, sector_t block);
    void (*invalidate_folio)(struct folio *folio, size_t offset,
                              size_t length);
    bool (*release_folio)(struct folio *folio, gfp_t gfp_mask);
    void (*free_folio)(struct folio *folio);
    ssize_t (*direct_IO)(struct kiocb *iocb, struct iov_iter *iter);
    int (*migrate_folio)(struct address_space *mapping,
                         struct folio *dst, struct folio *src,
                         enum migrate_mode mode);
    int (*launder_folio)(struct folio *folio);
    bool (*is_partially_uptodate)(struct folio *folio,
                                   size_t from, size_t count);
    int (*error_remove_folio)(struct address_space *mapping,
                              struct folio *folio);
};
```

### 5.2 关键回调

| 回调 | 用途 |
|------|------|
| `read_folio` | 读取文件页到缓存 |
| `write_begin/end` | 写操作准备和完成 |
| `writepages` | 批量写回脏页 |
| `bmap` | 逻辑块到物理块映射 |
| `direct_IO` | 直接 I/O (绕过缓存) |

## 6. struct dentry_operations

### 6.1 定义

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

### 6.2 关键回调

| 回调 | 用途 |
|------|------|
| `d_revalidate` | 重新验证 dentry 有效性 |
| `d_hash`/`d_compare` | 文件名哈希和比较 |
| `d_delete` | 引用归零时调用 |
| `d_iput` | 解除 dentry 与 inode 关联 |
| `d_automount` | 自动挂载触发 |

## 7. struct export_operations

### 7.1 定义

```c
// include/linux/exportfs.h:281
struct export_operations {
    int (*encode_fh)(struct inode *inode, __u32 *fh, int *max_len,
                    struct inode *parent);
    struct dentry *(*fh_to_dentry)(struct super_block *sb, struct fid *fid,
                                   int fh_len, int fh_type);
    struct dentry *(*fh_to_parent)(struct super_block *sb, struct fid *fid,
                                   int fh_len, int fh_type);
    int (*get_name)(struct dentry *parent, char *name,
                    struct dentry *child);
    struct dentry *(*get_parent)(struct dentry *dentry);
    int (*commit_metadata)(struct inode *inode);
};
```

## 8. 使用示例

### 8.1 ext4 文件系统操作设置

```c
// fs/ext4/super.c
static const struct super_operations ext4_sops = {
    .alloc_inode    = ext4_alloc_inode,
    .destroy_inode   = ext4_destroy_inode,
    .write_inode    = ext4_write_inode,
    .evict_inode    = ext4_evict_inode,
    .put_super      = ext4_put_super,
    .sync_fs        = ext4_sync_fs,
    .statfs         = ext4_statfs,
    .show_options   = ext4_show_options,
};

// fs/ext4/namei.c
static const struct inode_operations ext4_dir_inode_operations = {
    .create         = ext4_create,
    .lookup         = ext4_lookup,
    .link           = ext4_link,
    .unlink         = ext4_unlink,
    .symlink        = ext4_symlink,
    .mkdir          = ext4_mkdir,
    .rmdir          = ext4_rmdir,
    .rename         = ext4_rename2,
    .setattr        = ext4_setattr,
    .getattr        = ext4_getattr,
    .listxattr      = ext4_listxattr,
    .get_acl        = ext4_get_acl,
    .set_acl        = ext4_set_acl,
};
```

### 8.2 VFS 调用示例

```c
// VFS 调用 inode_operations->lookup
// fs/namei.c
static int lookup_fast(struct nameidata *nd)
{
    struct dentry *dentry;

    dentry = d_lookup(nd->path.dentry, &nd->last);
    if (dentry)
        return 0;

    // 调用文件系统 lookup
    inode = nd->path.dentry->d_inode;
    return inode->i_op->lookup(inode, dentry, nd->flags);
}
```
