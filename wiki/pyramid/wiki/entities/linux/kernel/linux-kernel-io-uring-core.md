---
type: entity
tags: [linux-kernel, async-io, io-subsystem]
created: 2026-05-20
sources: [github-notes-io-uring-core, github-notes-io-uring-operations, github-notes-io-uring-memory, github-notes-io-uring-features, handson-io-uring-shuveb]
---

# Linux Kernel io_uring

io_uring 是 Linux 5.1 引入的高性能异步 I/O 接口，通过共享内存的环形队列实现用户态与内核态之间的高效通信。

## 定义

io_uring 通过 mmap 共享 SQ（提交队列）和 CQ（完成队列），支持批量提交和零轮询，显著降低系统调用开销。

## 关键要点

### 核心数据结构

- **struct io_ring_ctx**: 环上下文，管理所有环状态和资源
- **struct io_rings**: 共享内存结构，包含 sq/cq head/tail 和 cqes[]
- **struct io_uring_sqe**: 提交队列条目，64字节，描述一个 I/O 请求
- **struct io_uring_cqe**: 完成队列条目，16字节，返回执行结果
- **struct io_kiocb**: 内核 I/O 控制块，管理请求生命周期

### 系统调用

- `io_uring_setup(entries, params)`: 创建 io_uring 实例，分配环内存
- `io_uring_enter(fd, to_submit, min_complete, flags)`: 提交 SQE + 等待 CQE
- `io_uring_register(fd, opcode, arg, nr_args)`: 注册缓冲区、文件描述符、eventfd

### SQ/CQ 机制

- 用户写入 SQE → 更新 sq.tail → 调用 io_uring_enter()
- 内核读取 sq.tail → 执行 I/O → 写入 CQE → 更新 cq.tail
- 内存屏障: `smp_wmb()` (SQ) / `smp_store_release()` (CQ)
- SQPOLL 模式: 内核线程轮询 SQ，消除用户-内核切换

### 操作码 (65 个)

- **I/O**: READ, WRITE, READV, WRITEV, READ_FIXED, WRITE_FIXED
- **文件系统**: OPENAT, CLOSE, STATX, RENAMEAT, UNLINKAT
- **网络**: ACCEPT, CONNECT, SENDMSG, RECVMSG, SEND, RECV
- **Poll**: POLL_ADD, POLL_REMOVE
- **高级**: ASYNC_CANCEL, TIMEOUT, LINK_TIMEOUT, FUTEX_WAIT

### SQE 标志

- `IOSQE_FIXED_FILE`: 使用固定文件描述符表
- `IOSQE_IO_DRAIN`: 前序请求排空后执行
- `IOSQE_IO_LINK`: 链接下一个 SQE（链式请求）
- `IOSQE_ASYNC`: 总是异步执行
- `IOSQE_BUFFER_SELECT`: 从缓冲区组选择缓冲区

### 内存管理

- `io_sqe_buffers_register()`: 注册用户缓冲区为固定缓冲区
- `io_ring_buffer_select()`: 从提供缓冲区环中选择
- `io_alloc_cache`: 小型对象分配缓存
- Scatter-Gather: iovec 与 bio_vec 转换

### 异步执行

- **io-wq**: 工作队列，处理阻塞 I/O
- **Task Work**: 在进程上下文执行异步完成回调
- **Task Cancel**: `IORING_OP_ASYNC_CANCEL` 取消待处理请求

### 高级特性

- **Eventfd 集成**: `io_eventfd_signal()` 通过 eventfd 通知完成
- **Epoll 集成**: `IORING_OP_EPOLL_CTL/WAIT` 与 epoll 配合
- **Timeout**: `IORING_OP_TIMEOUT`, `LINK_TIMEOUT`
- **Futex**: `FUTEX_WAIT`, `FUTEX_WAKE`, `FUTEX_WAITV`

### 相比 epoll/aio 的优势

| 特性 | epoll | aio | io_uring |
|------|-------|-----|----------|
| 异步 I/O | 仅监控 | 仅磁盘 I/O | 所有类型 |
| syscall 次数 | 多次/操作 | 多次/操作 | 批量提交 |
| 轮询方式 | 用户轮询 | 内核轮询 | 零轮询 (SQPOLL) |
| 内存拷贝 | 多次 | 多次 | 共享内存 |

### 关键源码文件

| 文件 | 作用 |
|------|------|
| `io_uring/io_uring.c` | 核心：setup/enter、提交/完成 |
| `io_uring/rw.c` | 读写操作 |
| `io_uring/fs.c` | 文件系统操作 |
| `io_uring/net.c` | 网络操作 |
| `io_uring/poll.c` | Poll 操作 |
| `io_uring/memmap.c` | 内存映射 |
| `io_uring/kbuf.c` | 缓冲区管理 |
| `io_uring/cancel.c` | 取消操作 |

## 相关概念

- [[entities/linux/kernel/block/linux-kernel-block-core]]: io_uring 读写操作最终可能落到块设备
- [[entities/linux/kernel/linux-kernel-vfs-core]]: VFS 层操作（file_operations）是 io_uring 操作的目标
- [[entities/linux/kernel/block/linux-kernel-block-mq]]: 多队列块设备（io_uring 的底层 I/O 路径）

## 来源详情

- `raw/github/notes/io_uring/linux_kernel/io_uring_core.md`
- `raw/github/notes/io_uring/linux_kernel/io_uring_operations.md`
- `raw/github/notes/io_uring/linux_kernel/io_uring_memory.md`
- `raw/github/notes/io_uring/linux_kernel/io_uring_features.md`
