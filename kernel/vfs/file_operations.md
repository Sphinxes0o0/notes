# VFS File 操作

## 1. 模块架构

### 1.1 功能概述

File 结构是进程与文件之间的抽象接口。每个打开的文件描述符对应一个 file 结构，包含了文件的打开模式、当前位置和操作函数指针。

### 1.2 关键源文件

| 文件 | 作用 |
|-----|------|
| `fs/file.c` | 文件操作实现 |
| `fs/open.c` | 文件打开 |
| `fs/read_write.c` | 读写实现 |
| `include/linux/fs.h` | file 结构定义 |

## 2. 核心数据结构

### 2.1 struct file

```c
// include/linux/fs.h:1259
struct file {
    union {
        const struct file_operations *f_op;   // 文件操作
        const struct path *f_path;
    };
    struct address_space    *f_mapping;      // 地址空间
    void                    *private_data;   // 私有数据
    struct inode            *f_inode;         // 关联 inode
    unsigned int            f_flags;          // open 标志
    fmode_t                 f_mode;          // 文件模式
    loff_t                  f_pos;           // 文件位置
    struct fown_struct      *f_owner;        // 文件所有者
    const struct cred      *f_cred;         // 凭证
    struct path             f_path;           // 文件路径
    file_ref_t              f_ref;           // 引用计数
    // ...
};
```

### 2.2 struct file_operations

```c
// include/linux/fs.h:1926
struct file_operations {
    struct module           *owner;
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

## 3. 文件打开

### 3.1 do_sys_open()

```c
// fs/open.c:1000
long do_sys_open(int dfd, const char __user *filename, int flags, umode_t mode)
{
    struct open_flags op;
    struct open_how how;
    struct filename *tmp;
    int fd;

    // 解析 open flags
    build_open_how(flags, mode, &how);
    if (build_open_flags(flags, mode, &op))
        return -EINVAL;

    // 获取文件名
    tmp = getname(filename);
    if (IS_ERR(tmp))
        return PTR_ERR(tmp);

    // 打开文件
    fd = do_filp_open(dfd, tmp, &op);
    if (fd >= 0)
        fsnotify_open(tmp);

    putname(tmp);
    return fd;
}
```

### 3.2 do_filp_open()

```c
// fs/open.c:900
struct file *do_filp_open(int dfd, struct filename *pathname,
                          const struct open_flags *op)
{
    struct nameidata nd;
    struct file *filp;

    // 路径查找
    filp = path_lookupat(dfd, pathname->name, op->lookup_flags, &nd);
    if (IS_ERR(filp))
        return filp;

    // 打开文件
    return finish_open(filp, nd.path.dentry, NULL);
}
```

### 3.3 finish_open()

```c
// fs/open.c:600
struct file *finish_open(struct file *filp, struct dentry *dentry,
                         int (*open)(struct inode *, struct file *))
{
    struct inode *inode = dentry->d_inode;
    int error;

    if (IS_ERR(filp))
        return filp;

    // 设置 inode
    filp->f_inode = inode;
    filp->f_path.dentry = dentry;

    // 调用文件系统的 open
    if (inode->i_op->open)
        error = inode->i_op->open(inode, filp);
    else
        error = generic_file_open(inode, filp);

    if (error) {
        filp_close(filp, NULL);
        return ERR_PTR(error);
    }

    // 设置文件操作
    if (inode->i_fop)
        filp->f_op = inode->i_fop;

    return filp;
}
```

## 4. 文件读取

### 4.1 sys_read()

```c
// fs/read_write.c:400
ssize_t ksys_read(unsigned int fd, char __user *buf, size_t count)
{
    struct fd f = fdget_pos(fd);
    ssize_t ret;

    if (f.file) {
        ret = vfs_read(f.file, buf, count, &f.file->f_pos);
        fdput_pos(f);
    } else
        ret = -EBADF;

    return ret;
}
```

### 4.2 vfs_read()

```c
// fs/read_write.c:150
ssize_t vfs_read(struct file *file, char __user *buf, size_t count,
                  loff_t *pos)
{
    struct inode *inode = file_inode(file);
    ssize_t ret;

    if (!(file->f_mode & FMODE_READ))
        return -EBADF;
    if (count > MAX_RW_COUNT)
        count = MAX_RW_COUNT;

    if (file->f_op->read)
        ret = file->f_op->read(file, buf, count, pos);
    else if (file->f_op->read_iter)
        ret = new_sync_read(file, buf, count, pos);
    else
        ret = -EINVAL;

    if (ret > 0)
        fsnotify_access(file);

    return ret;
}
```

### 4.3 new_sync_read()

```c
// fs/read_write.c:100
static ssize_t new_sync_read(struct file *filp, char __user *buf,
                             size_t len, loff_t *ppos)
{
    struct kiocb kiocb;
    struct iov_iter iter;
    ssize_t ret;

    init_sync_kiocb(&kiocb, filp);
    iov_iter_init(&iter, ITER_DEST, buf, len, 0);
    ret = filp->f_op->read_iter(&kiocb, &iter);
    if (-EIOCBQUEUED == ret)
        ret = wait_on_sync_kiocb(&kiocb);
    *ppos = kiocb.ki_pos;
    return ret;
}
```

## 5. 文件写入

### 5.1 sys_write()

```c
// fs/read_write.c:450
ssize_t ksys_write(unsigned int fd, const char __user *buf, size_t count)
{
    struct fd f = fdget_pos(fd);
    ssize_t ret;

    if (f.file) {
        ret = vfs_write(f.file, buf, count, &f.file->f_pos);
        fdput_pos(f);
    } else
        ret = -EBADF;

    return ret;
}
```

### 5.2 vfs_write()

```c
// fs/read_write.c:200
ssize_t vfs_write(struct file *file, const char __user *buf,
                   size_t count, loff_t *pos)
{
    struct inode *inode = file_inode(file);
    ssize_t ret;

    if (!(file->f_mode & FMODE_WRITE))
        return -EBADF;
    if (count > MAX_RW_COUNT)
        count = MAX_RW_COUNT;

    if (file->f_op->write)
        ret = file->f_op->write(file, buf, count, pos);
    else if (file->f_op->write_iter)
        ret = new_sync_write(file, buf, count, pos);
    else
        ret = -EINVAL;

    if (ret > 0)
        fsnotify_modify(file);

    return ret;
}
```

## 6. 文件同步

### 6.1 sys_fsync()

```c
// fs/sync.c:100
int ksys_fsync(unsigned int fd, int datasync)
{
    struct fd f = fdget(fd);
    int ret;

    if (!f.file)
        return -EBADF;

    ret = vfs_fsync(f.file, datasync);
    fdput(f);
    return ret;
}
```

### 6.2 vfs_fsync()

```c
// fs/sync.c:60
int vfs_fsync(struct file *file, int datasync)
{
    struct inode *inode = file_inode(file);
    int err;

    err = filemap_write_and_wait(inode->i_mapping);
    if (err)
        return err;

    if (!file->f_op->fsync)
        return -EINVAL;

    return file->f_op->fsync(file, 0, LLONG_MAX, datasync);
}
```

## 7. 文件关闭

### 7.1 sys_close()

```c
// fs/open.c:1100
int ksys_close(unsigned int fd)
{
    struct fd f = fdget(fd);
    int ret;

    if (!f.file)
        return -EBADF;

    ret = close_fd_get_file(fd);
    if (!ret)
        return -EBADF;

    return filp_close(f.file, current->files);
}
```

### 7.2 filp_close()

```c
// fs/open.c:500
int filp_close(struct file *filp, fl_owner_t id)
{
    int retval = 0;

    if (!file_count(f.file))
        printk(KERN_ERR "VFS: Close: file count is 0\n");

    if (filp->f_op->flush)
        retval = filp->f_op->flush(filp, id);

    // 刷新并释放
    fput(filp);
    return retval;
}
```

### 7.3 fput()

```c
// fs/file_table.c:100
void fput(struct file *file)
{
    if (atomic_long_dec_and_test(&file->f_ref)) {
        struct task_struct *task = current;

        if (likely(!in_interrupt() && !(task->flags & PF_KTHREAD))) {
            init_task_work(&file->f_u.fu_rcuhead, ____fput);
            task_work_add(task, &file->f_u.fu_rcuhead, TWA_RESUME);
        } else
            __fput(file);
    }
}
```

## 8. 文件偏移

### 8.1 vfs_llseek()

```c
// fs/read_write.c:300
loff_t vfs_llseek(struct file *file, loff_t offset, int whence)
{
    if (!file->f_op->llseek)
        return -ESPIPE;

    return file->f_op->llseek(file, offset, whence);
}
```

### 8.2 generic_file_llseek()

```c
// mm/filemap.c:300
loff_t generic_file_llseek(struct file *file, loff_t offset, int whence)
{
    struct inode *inode = file_inode(file);
    loff_t ppos;

    switch (whence) {
    case SEEK_SET:
        ppos = offset;
        break;
    case SEEK_CUR:
        ppos = file->f_pos + offset;
        break;
    case SEEK_END:
        ppos = inode->i_size + offset;
        break;
    default:
        return -EINVAL;
    }

    if (ppos < 0)
        return -EINVAL;

    file->f_pos = ppos;
    return ppos;
}
```

## 9. 文件引用计数

### 9.1 fget()

```c
// fs/file_table.c:60
struct file *fget(unsigned int fd)
{
    struct file *file;

    rcu_read_lock();
    file = fcheck(fd);
    if (file) {
        if (!atomic_long_inc_not_zero(&file->f_ref))
            file = NULL;
    }
    rcu_read_unlock();

    return file;
}
```

### 9.2 fget_light()

```c
// fs/file_table.c:80
struct file *fget_light(unsigned int fd, int *fput_needed)
{
    struct file *file;

    *fput_needed = 0;
    file = fcheck(fd);
    if (!file)
        return NULL;

    if (!atomic_long_inc_not_zero(&file->f_ref))
        return NULL;

    *fput_needed = 1;
    return file;
}
```

## 10. 文件锁

### 10.1 struct file_lock

```c
// include/linux/fs.h:1800
struct file_lock {
    struct file_lock *fl_next;
    struct list_head fl_list;
    struct fasync_struct *fl_fasync;
    unsigned int fl_flags;
    unsigned char fl_type;
    unsigned int fl_pid;
    unsigned long fl_start;
    unsigned long fl_end;
    void (*fl_lmops)(struct file_lock *);
    union {
        struct nlm_lockowner *nlm_owner;
        void *fl_owner;
    } fl_u;
    struct file *fl_file;
    loff_t fl_posix;
};
```

### 10.2 flock()

```c
// fs/locks.c:500
int fcntl_setlk(unsigned int fd, unsigned int cmd, struct flock *lck)
{
    struct file *filp = fget(fd);
    struct inode *inode = file_inode(filp);
    struct file_lock *fl;
    int error;

    // 创建文件锁
    fl = locks_alloc_lock();
    if (!fl)
        return -ENOLCK;

    error = flock_to_posix_lock(filp, fl, lck);
    if (error)
        goto out;

    // 获取 inode 锁
    inode_lock(inode);

    // 应用锁
    error = vfs_setlk(inode, fl);

    inode_unlock(inode);

out:
    locks_free_lock(fl);
    return error;
}
```

## 11. 文件操作示例

### 11.1 ext4 文件操作

```c
// fs/ext4/file.c
const struct file_operations ext4_file_operations = {
    .llseek         = ext4_llseek,
    .read_iter      = ext4_file_read_iter,
    .write_iter     = ext4_file_write_iter,
    .unlocked_ioctl = ext4_ioctl,
    .mmap           = ext4_file_mmap,
    .open           = ext4_file_open,
    .release        = ext4_release_file,
    .fsync          = ext4_sync_file,
    .splice_read    = generic_file_splice_read,
    .splice_write   = iter_file_splice_write,
};
```

### 11.2 pipe 文件操作

```c
// fs/pipe.c
const struct file_operations pipefifo_fops = {
    .open           = fifo_open,
    .llseek         = no_llseek,
    .read_iter      = pipe_read_iter,
    .write_iter     = pipe_write_iter,
    .poll           = pipe_poll,
    .unlocked_ioctl = pipe_ioctl,
    .release        = pipe_release,
    .fasync         = pipe_fasync,
};
```
