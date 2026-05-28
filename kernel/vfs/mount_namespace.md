# VFS Mount Namespace

## 1. 模块架构

### 1.1 功能概述

Mount Namespace 允许每个进程拥有独立的挂载点视图。这是容器技术的基石之一，实现了进程间的文件系统隔离。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `fs/namespace.c` | mount namespace 实现 |
| `fs/pnode.c` | 挂载传播 |
| `include/linux/mount.h` | mount 结构定义 |
| `include/linux/nsproxy.h` | namespace proxy |

## 2. 核心数据结构

### 2.1 struct vfsmount

```c
// include/linux/mount.h:58
struct vfsmount {
    struct dentry           *mnt_root;         // 挂载树根目录
    struct super_block      *mnt_sb;          // 超级块
    int                     mnt_flags;        // 挂载标志
    struct mnt_idmap        *mnt_idmap;       // UID/GID 映射
    const struct seq_operations *mnt_seq_ops; // 序列号操作
    struct path             mnt_ex_mountpoint;// 导出挂载点
    // ...
};
```

### 2.2 struct mount

```c
// include/linux/mount.h:120
struct mount {
    struct hlist_node mnt_hash;
    struct mount      *mnt_parent;         // 父挂载
    struct dentry     *mnt_mountpoint;     // 挂载点 dentry
    struct vfsmount    mnt;
    struct list_head   mnt_mounts;         // 子挂载链表
    struct list_head   mnt_child;          // 兄弟链表
    int               mnt_id;              // 挂载 ID
    int               mnt_parent_id;       // 父挂载 ID
    unsigned long     mnt_flags;           // 挂载标志
    char              *mnt_devname;        // 设备名
    struct list_head   mnt_list;           // namespace 链表
    struct list_head   mnt_expire_list;    // 到期待删除链表
    struct list_head   mnt_share;          // 共享链表
    struct list_head   mnt_slave_list;     // 从属链表
    struct list_head   mnt_slave_entry;    // 从属条目
    struct mount       *mnt_master;        // 主挂载
    struct mnt_namespace *mnt_ns;         // 所属 namespace
    // ...
};
```

### 2.3 struct mnt_namespace

```c
// include/linux/mount.h:180
struct mnt_namespace {
    atomic_t                count;
    struct mount           *root;
    struct list_head        list;           // 挂载链表
    struct user_namespace   *user_ns;
    u64                     seq;            // 序列号
    wait_queue_head_t       poll;
    u64                     event;
};
```

### 2.4 挂载传播类型

```c
// include/linux/mount.h:30
#define CL_MAKE_SHARED               0x100000
#define CL_PRIVATE                   0x200000
#define CL_SLAVE                     0x400000
#define CL_SHARED_TO_SLAVE           0x800000
#define CL_UNBINDABLE               0x1000000
#define CL_MOVE                    (1 << 1)
#define CL_COPY                    (1 << 2)
#define CL_COPY_FLAGS               (CL_COPY | CL_MOVE)
```

## 3. 挂载传播

### 3.1 传播类型说明

| 类型 | 说明 |
|------|------|
| SHARED | 挂载点会在所有 namespace 间共享 |
| PRIVATE | 默认类型，不传播 |
| SLAVE | 从主挂载点接收挂载/卸载事件 |
| UNBINDABLE | 不能被绑定 |

### 3.2 propagate_mount()

```c
// fs/pnode.c:300
static void propagate_mount(struct mount *mnt)
{
    struct mount *parent = mnt->mnt_parent;
    struct mount *m;

    list_for_each_entry(m, &parent->mnt_share, mnt_share) {
        // 共享挂载：传播到所有共享成员
        clone_mnt(mnt, m, CL_MAKE_SHARED);
    }

    list_for_each_entry(m, &parent->mnt_slave_list, mnt_slave_entry) {
        // 从属挂载：传播到所有从属成员
        if (mnt->mnt_master == m->mnt_master)
            clone_mnt(mnt, m, CL_SLAVE);
    }
}
```

### 3.3 clone_mnt()

```c
// fs/pnode.c:100
static struct mount *clone_mnt(struct mount *old, struct mount *parent,
                              int flag)
{
    struct mount *mnt;

    // 分配新的 mount
    mnt = alloc_mnt(parent);
    if (!mnt)
        return ERR_PTR(-ENOMEM);

    // 复制 vfsmount
    mnt->mnt.mnt_flags = old->mnt.mnt_flags;
    mnt->mnt.mnt_sb = old->mnt.mnt_sb;
    mnt->mnt.mnt_root = old->mnt.mnt_root;
    mnt->mnt.mnt_parent = parent;

    // 设置传播类型
    if (flag & CL_MAKE_SHARED) {
        list_add(&mnt->mnt_share, &old->mnt_share);
        mnt->mnt_share = &mnt->mnt_share;
    }

    return mnt;
}
```

## 4. 挂载操作

### 4.1 do_mount()

```c
// fs/namespace.c:2000
long do_mount(const char *dev_name, const char *dir_name,
             const char *type_page, unsigned long flags, void *data_page)
{
    struct path path;
    int ret;

    // 解析路径
    ret = kern_path(dir_name, LOOKUP_FOLLOW, &path);
    if (ret)
        return ret;

    // 执行挂载
    ret = do_new_mount(&path, type_page, flags, dev_name, data_page);

    path_put(&path);
    return ret;
}
```

### 4.2 do_new_mount()

```c
// fs/namespace.c:1900
int do_new_mount(struct path *path, char *type, int flags,
                char *name, void *data)
{
    struct vfsmount *mnt;

    // 分配新的 vfsmount
    mnt = vfs_kern_mount(type, flags, name, data);
    if (IS_ERR(mnt))
        return PTR_ERR(mnt);

    // 将 vfsmount 挂载到路径
    return do_add_mount(mnt, path, MNTflags, NULL);
}
```

### 4.3 vfs_kern_mount()

```c
// fs/namespace.c:1500
struct vfsmount *vfs_kern_mount(struct file_system_type *type,
                                int flags, const char *name, void *data)
{
    struct mount *mnt;

    if (!type)
        return ERR_PTR(-ENODEV);

    // 分配 mount 结构
    mnt = alloc_vfsmnt(name);
    if (!mnt)
        return ERR_PTR(-ENOMEM);

    // 获取或创建 superblock
    if (type->read_super)
        mnt->mnt.mnt_sb = type->read_super(type, data, flags);
    else
        mnt->mnt.mnt_sb = get_sb(type, data);

    if (IS_ERR(mnt->mnt.mnt_sb)) {
        mnt_free_id(mnt);
        return ERR_CAST(mnt->mnt.mnt_sb);
    }

    // 初始化 vfsmount
    mnt->mnt.mnt_root = mnt->mnt.mnt_sb->s_root;
    mnt->mnt.mnt_mountpoint = mnt->mnt.mnt_root;

    return &mnt->mnt;
}
```

### 4.4 do_add_mount()

```c
// fs/namespace.c:1800
static int do_add_mount(struct vfsmount *newmnt, struct path *path,
                        int mnt_flags, struct mount *parent)
{
    int err;

    // 验证挂载点
    err = -EINVAL;
    if (!check_mnt(parent))
        goto unlock;

    // 创建挂载
    err = attach_recursive_mnt(newmnt, path, parent);
    if (err)
        goto unlock;

    // 添加到 namespace
    list_add_tail(&newmnt->mnt_instance, &current->nsproxy->mnt_ns->list);

unlock:
    return err;
}
```

## 5. 卸载操作

### 5.1 sys_umount()

```c
// fs/namespace.c:1600
long sys_umount(char __user *name, int flags)
{
    struct path path;
    int ret;

    ret = kern_path(name, LOOKUP_FOLLOW, &path);
    if (ret)
        return ret;

    ret = do_umount(&path.mnt, flags);

    path_put(&path);
    return ret;
}
```

### 5.2 do_umount()

```c
// fs/namespace.c:1550
int do_umount(struct vfsmount *mnt, int flags)
{
    struct mount *p;
    int ret;

    // 检查权限
    if (!capable(CAP_SYS_ADMIN))
        return -EPERM;

    // 获取 mount
    p = real_mount(mnt);

    // 如果有子挂载，不能卸载
    if (!list_empty(&p->mnt_mounts))
        return -EBUSY;

    // 如果是 busy 的，不能卸载
    if (!namespace_locked(mnt))
        return -EBUSY;

    // 执行卸载
    ret = umount_tree(p, flags);
    return ret;
}
```

### 5.3 umount_tree()

```c
// fs/namespace.c:1400
static int umount_tree(struct mount *mnt, int flags)
{
    LIST_HEAD(umount_list);
    struct mount *p;
    int ret = 0;

    // 收集要卸载的挂载
    collect_mounts(mnt, &umount_list);

    // 传播卸载到从属挂载
    propagate_umount(&umount_list);

    // 实际卸载
    list_for_each_entry(p, &umount_list, mnt_umount_list) {
        struct super_block *sb = p->mnt.mnt_sb;

        if (sb->s_op->umount_begin)
            sb->s_op->umount_begin(sb);

        shrink_dcache_for_umount(sb);
        evict_inodes(sb);

        if (sb->s_op->put_super)
            sb->s_op->put_super(sb);
    }

    return ret;
}
```

## 6. Namespace 复制

### 6.1 copy_namespace()

```c
// fs/namespace.c:2500
struct mnt_namespace *copy_namespace(unsigned long flags,
                                    struct user_namespace *user_ns,
                                    struct mnt_namespace *old_ns)
{
    struct mnt_namespace *ns;
    struct mount *old;
    struct mount *new;
    int ret;

    // 分配新的 namespace
    ns = create_mnt_ns(old_ns->root);
    if (IS_ERR(ns))
        return ns;

    // 复制所有挂载
    list_for_each_entry(old, &old_ns->list, mnt_list) {
        if (flags & CLONE_NS) {
            // 完全共享
            new = old;
        } else if (old->mnt.mnt_flags & MNT_SHARED) {
            // 复制共享挂载
            new = copy_tree(old, old->mnt_parent);
        } else {
            // 复制私有挂载
            new = copy_tree(old, NULL);
        }

        if (IS_ERR(new)) {
            put_mnt_ns(ns);
            return ERR_CAST(new);
        }

        list_add(&new->mnt_instance, &ns->list);
    }

    return ns;
}
```

### 6.2 copy_tree()

```c
// fs/pnode.c:200
static struct mount *copy_tree(struct mount *mnt, struct mount *parent)
{
    struct mount *child, *p;
    int ret;

    // 复制自己
    child = clone_mnt(mnt, parent, 0);
    if (IS_ERR(child))
        return child;

    // 递归复制子挂载
    list_for_each_entry(p, &mnt->mnt_mounts, mnt_child) {
        struct mount *copy = copy_tree(p, child);
        if (IS_ERR(copy))
            return copy;
    }

    return child;
}
```

## 7. pivot_root

### 7.1 sys_pivot_root()

```c
// fs/namespace.c:2200
long sys_pivot_root(const char __user *new_root, const char __user *put_old)
{
    struct path new_path, old_path;
    struct mount *new_mnt;
    int ret;

    // 获取新根路径
    ret = kern_path(new_root, LOOKUP_FOLLOW, &new_path);
    if (ret)
        return ret;

    // 获取旧根路径
    ret = kern_path(put_old, LOOKUP_FOLLOW, &old_path);
    if (ret)
        goto out1;

    // 执行 pivot_root
    ret = do_pivot_root(&new_path, &old_path);

    path_put(&old_path);
out1:
    path_put(&new_path);
    return ret;
}
```

### 7.2 do_pivot_root()

```c
// fs/namespace.c:2100
static int do_pivot_root(struct path *new_path, struct path *old_path)
{
    struct mount *old_mnt = real_mount(old_path->mnt);
    struct mount *new_mnt = real_mount(new_path->mnt);

    // 交换挂载点
    swap(&new_mnt->mnt.mnt_root, &old_mnt->mnt_root);

    // 更新父指针
    old_mnt->mnt.mnt_parent = new_mnt;
    old_mnt->mnt_mountpoint = new_path->dentry;

    return 0;
}
```

## 8. 挂载属性

### 8.1 MNT 标志

```c
// include/linux/mount.h:50
#define MNT_NOSUID      0x01   // 不执行 setuid
#define MNT_NODEV       0x02   // 不允许访问设备
#define MNT_NOEXEC      0x04   // 不允许执行
#define MNT_NOATIME     0x08   // 不更新访问时间
#define MNT_NODIRATIME  0x10   // 不更新目录访问时间
#define MNT_RELATIME    0x20   // 相对 atime
#define MNT_READONLY    0x40   // 只读
#define MNT_SHRINKABLE  0x100  // 可收缩
#define MNT_WRITE_HOLD  0x200  // 写持有
```

## 9. 挂载IDR管理

### 9.1 mnt_alloc_id()

```c
// fs/namespace.c:100
static int mnt_alloc_id(struct mount *mnt)
{
    int id;

    id = idr_alloc(&mnt_idr, mnt, 0, 0, GFP_KERNEL);
    if (id < 0)
        return id;

    mnt->mnt_id = id;
    return 0;
}
```

### 9.2 mnt_free_id()

```c
// fs/namespace.c:120
static void mnt_free_id(struct mount *mnt)
{
    idr_remove(&mnt_idr, mnt->mnt_id);
}
```

## 10. 挂载传播流程

```
创建共享挂载:
mount --bind /mnt/some/path /mnt/other/path

1. do_add_mount()
   |
2. attach_recursive_mnt()
   |
3. propagate_mount()
      |
      +---> 对于每个共享组中的成员
            clone_mnt(mnt, member, CL_MAKE_SHARED)
```

```
卸载传播:
umount /mnt/some/path

1. umount_tree()
   |
2. propagate_umount()
      |
      +---> 对于每个从属挂载
            递归卸载
```
