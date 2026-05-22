---
type: index
tags: [linux-kernel, async-io, vfs]
created: 2026-05-22
---

# Linux Kernel — I/O (io_uring + VFS)

> High-performance async I/O subsystem and the virtual filesystem abstraction layer

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/io_uring/linux-kernel-io-uring-core]] | io_uring: high-performance async I/O, SQ/CQ rings, 65 opcodes, mmap shared memory, io-wq | linux-kernel, async-io |
| [[entities/linux/kernel/vfs/linux-kernel-vfs-core]] | VFS: inode/dentry/super_block/file, namei path lookup, dcache, 6 operation interfaces | linux-kernel, vfs, filesystem |

## Cross-References

- [[kernel-virt-index]] — io_uring handles Virtio disk I/O; VFS sits beneath KVM guest filesystems
- [[kernel-block-index]] — io_uring and VFS both interface with the block layer via bio/request
- [[os-index]] — VFS is the OS-level filesystem abstraction; linux-vfs entity bridges both
