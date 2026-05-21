---
type: entity
tags: [Linux, VFS, 文件系统, 内核]
created: 2026-05-20
sources: [notes-os]
---

# Linux VFS (Virtual File System)

## 定义

VFS 是 Linux 内核的核心子系统，为用户空间程序提供统一的文件系统接口，通过 dentry/inode/file 等抽象掩盖底层文件系统差异。

## 关键要点

- **RCU 路径查找**: 使用序列计数器 `d_seq` 检测并发修改，`__d_lookup_rcu()` 无锁查找
- **Dentry 缓存**: 哈希表加速查找，`dentry_lru` 链表管理回收，短文件名内联存储
- **Inode 缓存**: 哈希表管理 inode，`inode_lru` 回收，`iget()`/`iput()` 引用计数
- **Super Block**: `sget()` 查找或创建超级块，`super_operations` 定义文件系统回调
- **地址空间**: `address_space` 管理页缓存，`XArray` 存储页面，`i_mmap` 红黑树管理 VMA
- **锁层次**: namespace_sem → s_umount → inode->i_rwsem → inode->i_lock → dentry->d_lock
- **权限模型**: `inode_operations` 定义 create/lookup/link/unlink/mkdir 等操作
- **文件操作**: `file_operations` 定义 llseek/read/write/mmap/fsync 等操作

## 算法复杂度

| 操作 | 复杂度 |
|------|--------|
| RCU 缓存命中 | O(1) |
| 缓存未命中 | O(d)，d=路径深度 |
| Inode LRU 驱逐 | O(1) |

## 相关概念

- [[entities/os/linux-memory-allocator]] — 内存分配器支持 VFS (slub/dentry cache)
- [[entities/os/linux-scheduler]] — 调度器管理 VFS 进程
- [[entities/os/os-virtual-memory]] — 页缓存与虚拟内存紧密相关

## 来源详情

- [[sources/notes-os]]
