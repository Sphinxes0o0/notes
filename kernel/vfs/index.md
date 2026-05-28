# Linux 内核 VFS 子系统深度分析

## 概述

本文档是 Linux 内核 VFS (Virtual File System) 的全面深度分析，涵盖从系统调用到具体文件系统的完整架构。

## 目录结构

### 核心框架
- [VFS 核心数据结构](./vfs_core_structs.md)
- [VFS 抽象层 API](./vfs_api.md)
- [Dentry 缓存](./dcache.md)
- [Inode 管理](./inode.md)
- [Path 查找](./path_lookup.md)

### 文件操作
- [File 操作](./file_operations.md)
- [Buffer Cache](./buffer_cache.md)
- [Superblock 管理](./superblock.md)
- [Mount Namespace](./mount_namespace.md)

### 程序加载
- [Exec 与 Binfmt](./exec_binfmt.md)

### 具体文件系统
- [Ext4 文件系统](https://www.kernel.org/doc/html/latest/filesystems/ext4/) (外部链接)

## VFS 架构

```
用户空间
    |
    v
系统调用 (sys_open, sys_read, sys_write, ...)
    |
    v
VFS 层
    |
    +---> Path 查找 (namei.c)
    |           |
    |           +---> dcache (目录项缓存)
    |           +---> inode (索引节点)
    |
    +---> File 操作 (file.c, open.c)
    |           |
    |           +---> dentry_open()
    |           +---> fget/fput (引用计数)
    |
    +---> Superblock (super.c)
    |           |
    |           +---> alloc_super()
    |           +---> sget() / put_super()
    |
    +---> Mount Namespace (namespace.c)
    |           |
    |           +---> copy_tree() / umount_tree()
    |
    v
具体文件系统 (ext4, xfs, btrfs, ...)
    |
    v
块设备层
```

## 任务统计

| 类别 | 数量 |
|-----|-----|
| 核心框架 | 5 |
| 文件操作 | 5 |
| 程序加载 | 1 |
| **总计** | **11** |

## 来源

本分析基于 Linux 内核源码。

## 深度分析

- [vfs_deep_dive_r1.md](vfs_deep_dive_r1.md) - 深度分析 R1: inode, dentry, super_block, file, address_space
- [vfs_deep_dive_r2.md](vfs_deep_dive_r2.md) - 深度分析 R2: inode_operations, vfs_write, truncate, pagecache, address_space_operations
