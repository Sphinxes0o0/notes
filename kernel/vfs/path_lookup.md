# VFS Path 查找 (namei)

## 1. 模块架构

### 1.1 功能概述

Path 查找是 VFS 将用户空间路径名（如 `/home/user/file`）转换为内核内部数据结构（dentry、inode）的过程。Linux 使用 RCU（Read-Copy-Update）机制加速查找。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `fs/namei.c` | 路径查找实现 |
| `fs/dcache.c` | dentry 缓存 |
| `include/linux/namei.h` | 路径查找接口 |
| `include/linux/dcache.h` | dentry 定义 |

## 2. 核心数据结构

### 2.1 struct nameidata

```c
// include/linux/namei.h:200
struct nameidata {
    struct path             path;           // 当前路径
    struct qstr             last;           // 最后一个路径分量
    struct inode            *inode;         // 当前 inode
    unsigned int            flags;          // 查找标志
    unsigned int            seq;            // RCU 序列号
    int                     last_type;      // 最后一个分量类型
    unsigned int            depth;          // 符号链接深度
    struct path             root;           // 根目录
    struct inode            *saved_dir;     // 保存的目录
    struct qstr             base;           // 基名
    void                    *page;          // 页缓存
    const char              *name;          // 路径名
    struct path             link;           // 符号链接路径
};
```

### 2.2 查找标志

```c
// include/linux/namei.h:50
#define LOOKUP_FIND            0x0001      // 查找模式
#define LOOKUP_CREATE          0x0002      // 创建模式
#define LOOKUP_EXCL           0x0004      // 排他创建
#define LOOKUP_RENAME_TARGET  0x0008      // 重命名目标
#define LOOKUP_RCU            0x0040      // RCU 模式
#define LOOKUP_NO_XDEV        0x0080      // 禁止跨设备
#define LOOKUP_NO_SYMLINKS    0x0100      // 禁止符号链接
#define LOOKUP_NO_MAGICLINKS  0x0200      // 禁止魔符号链接
#define LOOKUP_NO_EVAL        0x0400      // 禁止 FOLLOW
#define LOOKUP_BENEATH        0x0800      // 不能穿越起点
#define LOOKUP_IN_ROOT        0x1000      // 在根目录下
```

### 2.3 路径分量类型

```c
// include/linux/namei.h:30
enum {LAST_NORM, LAST_ROOT, LAST_DOT, LAST_DOTDOT, LAST_BIND};
```

## 3. 主要查找函数

### 3.1 kern_path()

```c
// fs/namei.c:1600
int kern_path(const char *name, unsigned int flags, struct path *path)
{
    struct path p;
    int ret;

    ret = path_lookupat(AT_FDCWD, name, flags | LOOKUP_FIND, &p);
    if (!ret)
        *path = p;
    return ret;
}
```

### 3.2 path_lookupat()

```c
// fs/namei.c:1400
static int path_lookupat(int dfd, const char *name,
                        unsigned int flags, struct nameidata *nd)
{
    struct path root = { .mnt = NULL, .dentry = NULL };

    // 设置根目录
    if (flags & LOOKUP_IN_ROOT)
        nd->root = root;
    else
        nd->root = current->fs->root;

    // 解析路径
    return link_path_walk(name, nd);
}
```

### 3.3 link_path_walk()

```c
// fs/namei.c:1450
static int link_path_walk(const char *name, struct nameidata *nd)
{
    struct path *path = &nd->path;
    struct qstr qstr;
    int err;

    // 如果是绝对路径，从根目录开始
    if (*name == '/') {
        set_root(nd);
        path->dentry = nd->root.dentry;
        path->mnt = nd->root.mnt;
        name++;
    }

    // 解析每个路径分量
    while (*name) {
        // 解析一个分量
        err = walk_component(nd, &qstr, &name);
        if (err)
            return err;
    }

    nd->path = *path;
    return 0;
}
```

## 4. 组件查找

### 4.1 walk_component()

```c
// fs/namei.c:1100
static int walk_component(struct nameidata *nd, struct qstr *qstr,
                          const char **name)
{
    struct path *path = &nd->path;
    struct inode *inode;
    int err;

    // 解析分量名称
    err = parse_name(nd, qstr, name);
    if (err)
        return err;

    // 查找 dentry
    err = lookup_fast(nd, qstr, path);
    if (err < 0)
        return err;

    inode = path->dentry->d_inode;

    // 检查符号链接
    if (d_is_symlink(path->dentry) && !(nd->flags & LOOKUP_NO_SYMLINKS))
        return step_into(nd, path);

    return 0;
}
```

### 4.2 lookup_fast()

```c
// fs/namei.c:800
static int lookup_fast(struct nameidata *nd, struct qstr *qstr,
                       struct path *path)
{
    struct dentry *dentry;
    struct inode *inode;
    unsigned int seq;

    // RCU 查找
    rcu_read_lock();
    dentry = __d_lookup_rcu(nd->path.dentry, qstr, &seq);
    if (!dentry) {
        rcu_read_unlock();
        goto slow_path;
    }

    // 验证序列号
    if (read_seqcount_retry(&dentry->d_seq, seq)) {
        rcu_read_unlock();
        goto slow_path;
    }

    // 获取引用
    path->mnt = nd->path.mnt;
    path->dentry = dentry;

    // 检查权限
    inode = dentry->d_inode;
    if (inode_permission(nd->idmap, inode, MAY_EXEC))
        return -EACCES;

    rcu_read_unlock();
    return 0;

slow_path:
    return lookup_slow(nd, qstr, path);
}
```

### 4.3 lookup_slow()

```c
// fs/namei.c:900
static int lookup_slow(struct nameidata *nd, struct qstr *qstr,
                       struct path *path)
{
    struct dentry *dentry;
    struct inode *inode;
    int err;

    // 使用目录的 inode 进行查找
    inode = nd->path.dentry->d_inode;

    // 获取目录锁
    inode_lock_shared(inode);

    // 调用文件系统的 lookup
    if (inode->i_op->lookup)
        dentry = inode->i_op->lookup(inode, NULL, qstr);
    else
        dentry = ERR_PTR(-ENOTDIR);

    inode_unlock_shared(inode);

    if (IS_ERR(dentry))
        return PTR_ERR(dentry);

    path->mnt = nd->path.mnt;
    path->dentry = dentry;

    return 0;
}
```

## 5. RCU 模式

### 5.1 RCU 查找优势

```
传统方式:
- 需要获取 d_lock (spinlock)
- 每次查找都有锁竞争
- 并发性能差

RCU 方式:
- 无锁查找
- 读取时不需要写者同步
- 高并发下性能优异
```

### 5.2 __d_lookup_rcu()

```c
// fs/dcache.c:420
struct dentry *__d_lookup_rcu(struct dentry *parent, struct qstr *name,
                              unsigned int *seq)
{
    struct dentry *dentry;
    unsigned int hash = name->hash;

    hlist_bl_for_each_entry_rcu(dentry, &d_hash(hash), d_hash) {
        if (dentry->d_parent != parent)
            continue;
        if (dentry->d_name.hash != hash)
            continue;
        if (!dentry_cmp(dentry, name))
            continue;
        *seq = read_seqcount(&dentry->d_seq);
        if (lockref_get_not_dead(&dentry->d_lockref))
            return dentry;
    }
    return NULL;
}
```

### 5.3 RCU 失败处理

```c
// 如果 RCU 查找失败或返回 NULL，fallback 到慢速路径
// 慢速路径会获取锁并执行标准查找
```

## 6. 符号链接处理

### 6.1 step_into()

```c
// fs/namei.c:1200
static int step_into(struct nameidata *nd, struct path *path)
{
    struct inode *inode = path->dentry->d_inode;

    // 检查是否是符号链接
    if (d_is_symlink(path->dentry)) {
        if (nd->flags & LOOKUP_NO_SYMLINKS)
            return -ELOOP;

        // 处理符号链接
        return walk_linked(nd, path);
    }

    // 更新当前路径
    nd->path = *path;
    nd->inode = inode;
    return 0;
}
```

### 6.2 walk_linked()

```c
// fs/namei.c:1250
static int walk_linked(struct nameidata *nd, struct path *path)
{
    struct path link = *path;
    int err;

    // 递归解析符号链接（限制深度防止循环）
    while (nd->depth < MAXSYMLINKS) {
        if (nd->flags & LOOKUP_NO_EVAL)
            return -ECHILD;

        // 获取符号链接目标
        err = nd->path.dentry->d_inode->i_op->follow_link(&link, nd);
        if (err)
            return err;

        // 继续解析新路径
        err = link_path_walk(nd, &link);
        if (err)
            return err;
    }

    return -ELOOP;
}
```

## 7. 路径解析流程图

```
                    用户调用 open("/home/user/file")
                                   |
                                   v
                    do_sys_open() -> do_filp_open()
                                   |
                                   v
                    path_lookupat(AT_FDCWD, "/home/user/file")
                                   |
                    +--------------+--------------+
                    |                              |
                    v                              v
            绝对路径?                         相对路径
                    |                              |
                    v                              v
            nd->path = root                  nd->path = cwd
                    |                              |
                    +--------------+--------------+
                                   |
                                   v
                    link_path_walk()
                    逐个分量解析:
                    1. "home" -> walk_component()
                    2. "user" -> walk_component()
                    3. "file" -> walk_component()
                                   |
                    +--------------+--------------+
                    |                              |
                    v                              v
              dentry 在缓存                    dentry 不在缓存
                    |                              |
                    v                              v
              lookup_fast()                  lookup_slow()
              (RCU 查找)                     (加锁查找)
                    |                              |
                    +--------------+--------------+
                                   |
                                   v
                    返回 struct path { dentry, mnt }
                                   |
                                   v
                    返回文件描述符 fd
```

## 8. 文件创建

### 8.1 do_filp_open()

```c
// fs/namei.c:1700
struct file *do_filp_open(int dfd, const char *pathname,
                          const struct open_flags *op)
{
    struct nameidata nd;
    int flags = op->lookup_flags;
    struct file *filp;

    // 路径查找
    filp = path_lookupat(dfd, pathname, flags, &nd);
    if (IS_ERR(filp))
        return filp;

    // 打开文件
    return finish_open(filp, nd.path.dentry, NULL);
}
```

### 8.2 vfs_create()

```c
// fs/namei.c:1800
int vfs_create(struct mnt_idmap *idmap, struct inode *dir,
               struct dentry *dentry, umode_t mode, bool excl)
{
    int error;

    if (IS_ERR(dentry))
        return PTR_ERR(dentry);

    error = dir->i_op->create(idmap, dir, dentry, mode, excl);
    if (!error)
        fsnotify_create(dir, dentry);

    return error;
}
```

## 9. 目录遍历

### 9.1 struct dir_context

```c
// include/linux/fs.h:1850
struct dir_context {
    const filldir_t actor;
    loff_t pos;
};
```

### 9.2 iterate_dir()

```c
// fs/namei.c:1900
int iterate_dir(struct file *file, struct dir_context *ctx)
{
    struct inode *inode = file_inode(file);

    if (IS_DEADDIR(inode))
        return -ENOENT;

    inode_lock_shared(inode);
    if (IS_AUTOMOUNT(inode))
        return -ENOENT;

    if (file->f_op->iterate_shared)
        ret = file->f_op->iterate_shared(file, ctx);
    else
        ret = file->f_op->iterate(file, ctx);

    inode_unlock_shared(inode);
    return ret;
}
```

## 10. 重命名

### 10.1 vfs_rename()

```c
// fs/namei.c:2000
int vfs_rename(struct mnt_idmap *idmap,
               struct inode *old_dir, struct dentry *old_dentry,
               struct inode *new_dir, struct dentry *new_dentry,
               unsigned int flags)
{
    int error;

    if (old_dentry->d_inode->i_flags & S_IMMUTABLE)
        return -EPERM;

    if ((old_dir != new_dir) && IS_DIRSYNC(old_dir))
        inode_sync_wait(old_dir);

    if (old_dir->i_op->rename)
        error = old_dir->i_op->rename(idmap, old_dir, old_dentry,
                                      new_dir, new_dentry, flags);
    else
        error = -EXDEV;

    return error;
}
```
