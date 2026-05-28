# Linux io_uring 子系统文档索引

## 文档清单

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [io_uring_core.md](io_uring_core.md) | 核心架构: struct io_ring_ctx, SQ/CQ, 系统调用 | io_uring/io_uring.c |
| [io_uring_operations.md](io_uring_operations.md) | 操作码: 65个操作码, prep/issue 函数 | io_uring/rw.c, fs.c, net.c |
| [io_uring_memory.md](io_uring_memory.md) | 内存管理: MMAP, 固定缓冲区, kbuf, alloc_cache | io_uring/memmap.c, kbuf.c |
| [io_uring_features.md](io_uring_features.md) | 高级特性: Eventfd, Epoll, Cancel, Timeout, Futex | io_uring/eventfd.c, cancel.c |

---

## 1. io_uring 核心架构 (io_uring_core.md)

### 关键内容
- io_uring 概述 (相比 epoll/aio)
- struct io_ring_ctx: 环上下文
- struct io_rings: 共享环结构
- struct io_uring_sqe: 提交条目
- struct io_uring_cqe: 完成条目
- struct io_kiocb: 内核 I/O 控制块

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| io_uring_setup | io_uring.c:3104 |
| io_uring_enter | io_uring.c:2542 |
| io_uring_register | register.c:1020 |
| io_submit_sqes | io_uring.c:2008 |

---

## 2. io_uring 操作码 (io_uring_operations.md)

### 关键内容
- 65 个操作码 (IORING_OP_NOP 到 IORING_OP_URING_CMD128)
- 两阶段处理: prep() 准备 + issue() 执行
- 读写操作: READ, WRITE, READV, WRITEV, READ_FIXED, READ_MULTISHOT
- 文件系统: OPENAT, CLOSE, STATX, RENAMEAT, UNLINKAT
- 网络: ACCEPT, CONNECT, SENDMSG, RECVMSG, SEND, RECV
- Poll: POLL_ADD, POLL_REMOVE

### 关键数据结构
| 结构 | 说明 |
|------|------|
| io_uring_sqe | 提交队列条目 |
| io_issue_def | 操作属性定义 |
| io_kiocb | 内核 I/O 控制块 |

---

## 3. io_uring 内存管理 (io_uring_memory.md)

### 关键内容
- io_uring_mmap(): 内存映射
- 固定缓冲区: io_sqe_buffers_register()
- 缓冲区管理: io_buffer_list, io_ring_buffer_select()
- 分配缓存: io_alloc_cache
- Scatter-Gather: iovec 与 bio_vec 转换

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| io_uring_mmap | memmap.c:295 |
| io_sqe_buffers_register | rsrc.c:858 |
| io_ring_buffer_select | kbuf.c:192 |

---

## 4. io_uring 高级特性 (io_uring_features.md)

### 关键内容
- Eventfd 集成: io_eventfd_register/unregister
- Epoll 集成: IORING_OP_EPOLL_CTL/WAIT
- 取消操作: IORING_OP_ASYNC_CANCEL
- Futex: FUTEX_WAIT, FUTEX_WAKE, FUTEX_WAITV
- Timeout: IORING_OP_TIMEOUT, LINK_TIMEOUT
- 错误处理: CQE 错误码

### 关键函数
| 函数 | 文件:行号 |
|------|-----------|
| io_eventfd_signal | eventfd.c |
| io_cancel_req_match | cancel.c |
| io_futex_wait | futex.c |

---

## 架构总览

```
                    ┌─────────────────────────────────────────┐
                    │         用户空间                        │
                    │  ┌─────────────────────────────────┐ │
                    │  │  struct io_uring_sqe[] (SQ)     │ │
                    │  │  struct io_uring_cqe[] (CQ)     │ │
                    │  └─────────────────────────────────┘ │
                    └─────────────────┬───────────────────────┘
                                      │ mmap / 系统调用
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │         io_uring_setup()               │
                    │    创建 io_ring_ctx 和共享内存          │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │         io_uring_enter()                │
                    │   提交 SQE → 异步执行 → 完成 CQE       │
                    └─────────────────┬───────────────────────┘
                                      │
                    ┌─────────────────┴───────────────────────┐
                    ▼                                       ▼
        ┌─────────────────────┐               ┌─────────────────────┐
        │   io-wq 工作队列    │               │   Task Work 机制    │
        │  (异步执行)        │               │  (内核线程)        │
        └─────────────────────┘               └─────────────────────┘
```

---

## 操作执行流程

```
用户空间                    内核                          硬件
    │                         │                             │
    │  io_uring_enter()       │                             │
    │────────────────────────>│                             │
    │                         │                             │
    │  读取 SQ tail           │                             │
    │────────────────────────>│                             │
    │                         │                             │
    │                    io_submit_sqes()                   │
    │                    ┌─────────────────┐                │
    │                    │ prep_*()        │ ← 准备请求    │
    │                    │ issue_*()       │ ← 执行请求    │
    │                    └─────────────────┘                │
    │                         │                             │
    │                    异步执行...                        │
    │                         │                             │
    │                    写入 CQ head                       │
    │<────────────────────────│                             │
    │                         │                             │
```

---

## 关键源码位置

| 组件 | 文件路径 |
|------|----------|
| 核心 | io_uring/io_uring.c |
| 类型定义 | io_uring/io_uring_types.h |
| 头文件 | io_uring/io_uring.h |
| 读写操作 | io_uring/rw.c |
| 文件系统 | io_uring/fs.c |
| 网络 | io_uring/net.c |
| Poll | io_uring/poll.c |
| Eventfd | io_uring/eventfd.c |
| 取消 | io_uring/cancel.c |
| 内存映射 | io_uring/memmap.c |
| 缓冲区 | io_uring/kbuf.c |
| Timeout | io_uring/timeout.c |
| Futex | io_uring/futex.c |
