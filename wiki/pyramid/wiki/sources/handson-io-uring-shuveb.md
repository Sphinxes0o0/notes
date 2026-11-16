---
type: source
source-type: web
title: "io_uring Tutorial"
author: "Shuveb Hussain"
date: 2024
size: medium
path: https://shuveb.github.io/io-uring-web-app/
summary: "Deep-dive tutorial series on Linux io_uring async I/O interface — covers submission/completion queues, polling modes, zero-copy, and performance characteristics."
tags: [linux-kernel, io-uring, async-io, syscall, zero-copy, polling, high-performance, linux-5.1+]
created: 2026-05-29
---

# io_uring Tutorial

## 核心内容

### 传统 System Call Overhead
```
read(fd, buf, 4096) → user → kernel → copy to buf → return
(每次调用都有 user/kernel 切换 + 数据复制开销)
```

### io_uring Architecture
```
App                    Kernel
  |                        |
  |  [SQE: read opcode]    |
  |  [SQE: write opcode]   |
  |  [SQE: fsync opcode]    |
  |  ────────────────────────→ SQ (Submission Queue, mmap'd)
  |                        |
  |                        | (kernel processes)
  |                        |
  |  ←──────────────────────  [CQE: result]  [CQE: result]
  |  [CQE: result]           CQ (Completion Queue, mmap'd)
  |
```

### Submission Queue Entry (SQE) — 32 bytes
```c
struct io_uring_sqe {
    __u8    opcode;      // IORING_OP_READ, IORING_OP_WRITE, etc.
    __u8    flags;      // IOSQE_FIXED_FILE, IOSQE_ASYNC, etc.
    __u16   ioprio;
    __u32   fd;
    __u64   off;        // file offset
    __u64   addr;       // buffer pointer
    __u32   len;        // buffer length
    union { __u32 rw_flags; ... };
    __u64   user_data;  // app tag to match CQE
    __u16   buf_index;  // for fixed buffers
    __u64   pad[2];
};
```

### Completion Queue Entry (CQE) — 16 bytes
```c
struct io_uring_cqe {
    __u64 user_data;  // copy of SQE's user_data
    __s32 res;        // syscall return value
    __u32 flags;
};
```

### Ring Setup
```c
// 基础 setup
struct io_uring ring;
io_uring_queue_init(32, &ring, 0);

// 提交请求
struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
io_uring_prep_read(sqe, fd, buf, sizeof(buf), 0);
io_uring_submit(&ring);

// 收集结果
struct io_uring_cqe *cqe;
io_uring_wait_cqe(&ring, &cqe);
printf("result: %d\n", cqe->res);
io_uring_cqe_seen(&ring, cqe);
```

### Polling Modes

**MMAP (default)** — mmap SQ/CQ rings:
```c
// Ring at fixed offset in process mmap area
```

**SQPOLL (Kernel Polling)** — kernel polls SQ without app syscalls:
```c
io_uring_params params = { .flags = IORING_SETUP_SQPOLL };
// Kernel thread continuously polls SQ, no syscall needed to submit
```

**IORING_SETUP_SQPOLL + IORING_SETUP_SQPOLL_FIXED**:
- Zero syscall overhead for submission
- Kernel thread busy-polling SQ ring
- Good for high-throughput workloads

### Zero-Copy (Fixed Buffers)
```c
// Register buffer once
io_uring_register_buffers(&ring, bufs, nbufs);

// Use registered buffer (no copy, no syscall overhead)
struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
io_uring_prep_read_fixed(sqe, fd, buf, 4096, off, buf_index);
```

### Linked Requests
```c
// Chain: read → write (write uses read result)
sqe->flags |= IOSQE_IO_LINK;
io_uring_submit(&ring);
```

## NIDS 关联

- **零拷贝** → 高性能数据包捕获（`recvmsg` 可通过 io_uring 零拷贝）
- **SQPOLL 模式** → 低延迟包处理（毫秒级响应）
- **批量请求** → 批量包检查减少 syscall 开销
- **多系统调用链接** → 批量数据包 I/O 操作
- **替代 epoll** → 在 io_uring 上构建高性能 IDS event loop

## 来源详情

- **作者博客**: shuveb.github.io
- **原文**: linuxjournal.com 连载
- **相关**: [[entities/linux/kernel/linux-kernel-io-uring-core]] — Linux io_uring 核心
- **相关**: [[entities/linux/kernel/linux-kernel-syscall]] — syscall 机制
