---
type: index
tags: [operating-system, linux]
created: 2026-05-22
---

# Operating System Fundamentals

> Process/thread model, virtual memory, I/O paradigms, Linux-specific subsystems

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/os/os-linking-loading]] | Linking and loading: ELF format, static/dynamic linking, PIC, GOT/PLT | os, linking, elf |
| [[entities/os/os-process-thread]] | Process and thread: resource allocation, state machine, context switching | os, process, thread |
| [[entities/os/os-virtual-memory]] | Virtual memory: page tables, MMU, page faults, swap | os, virtual-memory |
| [[entities/os/os-io-model]] | I/O models: select/poll/epoll, blocking/non-blocking, sync/async | os, io-model |
| [[entities/os/linux-vfs]] | Linux VFS: dentry/inode cache, RCU path lookup, page cache | linux, vfs |
| [[entities/os/linux-scheduler]] | Linux scheduler: CFS, RT, Deadline, load balancing | linux, scheduler |
| [[entities/os/linux-memory-allocator]] | Linux memory allocator: SLUB/Buddy, sheaf mechanism, cmpxchg16b | linux, memory |
| [[entities/os/linux-cgroups]] | Linux cgroups: CSS mechanism, v2 single hierarchy, CPU/memory controllers | linux, cgroups |
| [[entities/os/os-concept]] | Operating System Concepts (Silberschatz): CPU scheduling, process sync, deadlock, memory, filesystems | os, textbook |
| [[entities/os/modern-operating-system]] | 现代操作系统 原理与实现: OS principles, virtualization, memory management, I/O | os, chinese |

## Cross-References

- [[entities/linux/kernel/index#scheduler]] — Deep-dive into scheduler internals
- [[entities/linux/kernel/index#memory-management]] — Deep-dive into memory management internals
- [[entities/linux/kernel/index#io-uring--vfs]] — Deep-dive into VFS and io_uring
- [[entities/linux/kernel/index]] — Locking and IPC are core OS subsystems
- [[synthesis/topic-os-fundamentals]] — OS fundamentals synthesis combining all above
