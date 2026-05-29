---
type: entity
tags: [linux-kernel, vfs, filesystem]
created: 2026-05-20
sources: [github-notes-vfs-core-structs, github-notes-vfs-api, github-notes-vfs-path-lookup, github-notes-vfs-dcache, github-notes-vfs-inode]
---

# Linux Kernel VFS (Virtual File System)

VFS 是 Linux 内核的虚拟文件系统层，为不同具体文件系统（ext4、XFS、Btrfs 等）提供统一抽象接口。

## 定义

VFS 是 Linux 内核的文件系统抽象层，通过定义标准数据结构（inode、dentry、super_block、file）和操作接口（`*_operations` 函数表），使用户空间程序无需感知底层文件系统差异。

## 关键要点

### 核心数据结构

**struct super_block**: 文件系统实例
- `s_list`: 全局 super_blocks 链表节点
- `s_root`: 根目录 dentry
- `s_op`: superblock 操作函数表
- `s_type`: 文件系统类型描述符
- `s_fs_info`: 文件系统私有数据

**struct inode**: 文件元数据
- `i_ino`: inode 编号
- `i_mode`: 文件类型和权限
- `i_op`: inode 操作函数表
- `i_mapping`: 关联的 address_space
- `i_size`: 文件大小
- 时间戳: i_atime / i_mtime / i_ctime / i_btime

**struct dentry**: 目录项（路径分量）
- `d_name`: 文件名 (qstr)
- `d_inode`: 关联的 inode
- `d_parent`: 父目录 dentry
- `d_flags`: DCACHE_* 状态标志
- RCU 序列号 `d_seq` 用于无锁查找

**struct file**: 打开的文件实例
- `f_op`: file_operations 函数表
- `f_inode`: 关联 inode
- `f_pos`: 文件位置
- `f_flags`: open 标志
- `f_mapping`: 地址空间

**struct vfsmount**: 挂载点
- `mnt_root`: 挂载树根 dentry
- `mnt_sb`: 所属 super_block
- `mnt_flags`: 挂载标志 (MNT_NOSUID, MNT_NOEXEC 等)

### 六种 Operations 接口

| 接口 | 核心回调 | 源码位置 |
|------|---------|---------|
| `super_operations` | alloc_inode, evict_inode, write_inode, put_super | `fs/super.c` |
| `inode_operations` | lookup, create, mkdir, unlink, rename | `fs/namei.c` |
| `file_operations` | read, write, llseek, open, release, fsync | `fs/file.c` |
| `address_space_operations` | read_folio, write_begin, writepages, direct_IO | `fs/buffer.c` |
| `dentry_operations` | d_revalidate, d_hash, d_compare, d_iput | `fs/dcache.c` |
| `export_operations` | encode_fh, fh_to_dentry, get_parent | `fs/exportfs.c` |

### Path 查找 (namei)

- `struct nameidata`: 路径查找上下文
- `link_path_walk()`: 逐分量解析路径
- `lookup_fast()`: RCU 无锁查找 dentry 缓存
- `lookup_slow()`: 慢速路径，加锁后调用文件系统 lookup
- `__d_lookup_rcu()`: RCU 查找的核心实现
- 符号链接处理: `walk_linked()` + depth 防止循环

### Path 查找标志

- `LOOKUP_FIND`: 查找模式
- `LOOKUP_CREATE`: 创建模式
- `LOOKUP_RCU`: RCU 模式无锁查找
- `LOOKUP_NO_SYMLINKS`: 禁止跟随符号链接
- `LOOKUP_NO_XDEV`: 禁止跨设备
- `LOOKUP_BENEATH`: 不能穿越起点

### Dcache (Dentry Cache)

- 全局 dentry 哈希表加速路径查找
- `d_lookup()`: 快速缓存查找
- LRU 链表: dentry 回收
- DCACHE_ENTRY_TYPE: 区分目录/普通文件/符号链接

### 文件操作流程

```
open("/home/user/file")
  → do_sys_open()
  → do_filp_open()
  → path_lookupat()       // VFS namei 查找
  → finish_open()         // 调用 f_op->open()
  → 返回 struct file *
```

### VFS 架构图

```
系统调用 (sys_open, sys_read, sys_write)
    ↓
VFS 层
    ├─ Path 查找 (namei.c)
    │     └─ dcache (目录项缓存)
    ├─ File 操作 (file.c)
    │     └─ dentry_open()
    ├─ Superblock (super.c)
    └─ Mount Namespace (namespace.c)
    ↓
具体文件系统 (ext4, xfs, btrfs...)
    ↓
块设备层
```

### 关键源码文件

| 文件 | 作用 |
|------|------|
| `fs/namei.c` | 路径查找 namei 实现 |
| `fs/dcache.c` | Dentry 缓存管理 |
| `fs/inode.c` | Inode 分配和回收 |
| `fs/file.c` | File 操作 |
| `fs/super.c` | Superblock 管理 |
| `fs/buffer.c` | Buffer cache 和 address_space |
| `fs/namespace.c` | Mount namespace |
| `fs/exec.c` / `binfmt_*.c` | 程序加载 (exec) |

## 相关概念

- [[entities/linux/kernel/block/linux-kernel-block-core]]: VFS 的下一层，块设备 I/O 栈
- [[entities/linux/kernel/mm/linux-kernel-mm-page-fault]]: 文件页缓存的页错误处理
- [[entities/linux/kernel/linux-kernel-io-uring-core]]: io_uring 操作最终调用 VFS 的 file_operations
- [[entities/linux/kernel/sched/linux-kernel-sched-load-balance]]: VFS inode 的 i_count 引用计数影响 inode 回收调度
- [[entities/linux/kernel/linux-kernel-syscall]]: 系统调用（VFS 是 syscall 的底层实现基础，socket() 等通过 VFS 分配 fd）

## 来源详情

- `raw/github/notes/vfs/linux_kernel/vfs_core_structs.md`
- `raw/github/notes/vfs/linux_kernel/vfs_api.md`
- `raw/github/notes/vfs/linux_kernel/path_lookup.md`
- `raw/github/notes/vfs/linux_kernel/dcache.md`
- `raw/github/notes/vfs/linux_kernel/inode.md`
- `raw/github/notes/vfs/linux_kernel/superblock.md`
- `raw/github/notes/vfs/linux_kernel/buffer_cache.md`
- `raw/github/notes/vfs/linux_kernel/exec_binfmt.md`
- `raw/github/notes/vfs/linux_kernel/mount_namespace.md`
## Related Concepts

- [[entities/linux/kernel/linux-kernel-sound-core]] — ALSA设备节点通过VFS暴露
