# Linux io_uring 子系统深度分析 R1

## 目录
1. [概述](#1-概述)
2. [SQ/CQ Ring 核心数据结构](#2-sqcq-ring-核心数据结构)
3. [Submission Queue Entry (SQE)](#3-submission-queue-entry-sqe)
4. [Completion Queue Entry (CQE)](#4-completion-queue-entry-cqe)
5. [io_uring_setup 系统调用](#5-io_uring_setup-系统调用)
6. [io_uring_enter 系统调用](#6-io_uring_enter-系统调用)
7. [Polling 模式](#7-polling-模式)
8. [Fixed File Table](#8-fixed-file-table)
9. [Linked Requests 链接请求](#9-linked-requests-链接请求)
10. [知识点关联表](#10-知识点关联表)

---

## 1. 概述

io_uring 是 Linux 内核提供的高性能异步 I/O 接口，首次引入于 5.1 内核。其核心设计通过共享内存的 Ring Buffer 实现用户态与内核态之间的高效通信。

**核心源码位置**:
- `/Users/sphinx/github/linux/io_uring/io_uring.c` - 核心实现
- `/Users/sphinx/github/linux/io_uring/rw.c` - 读写操作
- `/Users/sphinx/github/linux/io_uring/net.c` - 网络操作
- `/Users/sphinx/github/linux/io_uring/timeout.c` - 超时处理
- `/Users/sphinx/github/linux/include/uapi/linux/io_uring.h` - UAPI 数据结构

---

## 2. SQ/CQ Ring 核心数据结构

### 2.1 struct io_rings - 共享环缓冲区

**源码位置**: `/Users/sphinx/github/linux/include/linux/io_uring_types.h:151-220`

```c
struct io_rings {
    struct io_uring sq, cq;              // SQ 和 CQ 的 head/tail
    u32 sq_ring_mask, cq_ring_mask;       // 掩码 (entries - 1)
    u32 sq_ring_entries, cq_ring_entries; // 环大小
    u32 sq_dropped;                       // 丢弃的 SQE 数量
    atomic_t sq_flags;                    // 运行时 SQ 标志
    u32 cq_flags;                         // 运行时 CQ 标志
    u32 cq_overflow;                      // CQ 溢出计数
    struct io_uring_cqe cqes[];          // CQE 数组 (cache-line 对齐)
};
```

### 2.2 struct io_ring_ctx - Ring 上下文

**源码位置**: `/Users/sphinx/github/linux/include/linux/io_uring_types.h:271-491`

```c
struct io_ring_ctx {
    /* const or read-mostly hot data */
    struct {
        unsigned int flags;              // IORING_SETUP_* 标志
        struct task_struct *submitter_task;
        struct io_rings *rings;          // 共享内存指针
        struct percpu_ref refs;            // 引用计数
        unsigned sq_thread_idle;           // SQ 线程空闲超时
    };

    /* submission data */
    struct {
        struct mutex uring_lock;         // 保护环的锁
        u32 *sq_array;                   // SQ 索引数组
        struct io_uring_sqe *sq_sqes;   // SQE 数组
        unsigned cached_sq_head;
        unsigned sq_entries;
        struct io_file_table file_table;  // 固定文件表
        struct io_rsrc_data buf_table;   // 固定缓冲区表
        struct list_head iopoll_list;     // IOPOLL 列表
    };

    /* completion data */
    struct {
        struct io_uring_cqe *cqe_cached;
        struct io_uring_cqe *cqe_sentinel;
        unsigned cached_cq_tail;
        unsigned cq_entries;
    };

    /* timeouts */
    struct {
        raw_spinlock_t timeout_lock;
        struct list_head timeout_list;
        struct list_head ltimeout_list;
    };

    spinlock_t completion_lock;
    struct list_head cq_overflow_list;
};
```

---

## 3. Submission Queue Entry (SQE)

### 3.1 struct io_uring_sqe - 64 字节结构

**源码位置**: `/Users/sphinx/github/linux/include/uapi/linux/io_uring.h:30-118`

```c
struct io_uring_sqe {
    __u8    opcode;      /* IORING_OP_* 操作码 */
    __u8    flags;       /* IOSQE_* 标志 */
    __u16   ioprio;      /* I/O 优先级 */
    __s32   fd;          /* 文件描述符 */
    union {
        __u64 off;       /* 偏移量 */
        __u64 addr2;     /* 第二个地址 */
        struct { __u32 cmd_op; __u32 __pad1; };
    };
    union {
        __u64 addr;      /* 缓冲区地址或 iovecs */
        __u64 splice_off_in;
        struct { __u32 level; __u32 optname; };
    };
    __u32 len;           /* 缓冲区大小或 iovec 数量 */
    union {
        __u32 rw_flags;          /* 读写标志 */
        __u32 fsync_flags;       /* fsync 标志 */
        __u32 poll_events;       /* poll 事件 */
        __u32 timeout_flags;
        __u32 accept_flags;
        __u32 cancel_flags;
    };
    __u64 user_data;     /* 用户数据,会在 CQE 中返回 */
    union {
        __u16 buf_index;    /* 固定缓冲区索引 */
        __u16 buf_group;    /* 缓冲区组 ID */
    };
    __u16 personality;    /* 权限配置 */
    union {
        __s32 splice_fd_in;
        __u32 file_index;
    };
};
```

### 3.2 SQE 标志 (sqe->flags)

| 标志 | 位 | 说明 |
|------|-----|------|
| `IOSQE_FIXED_FILE` | bit 0 | 使用固定文件表中的文件 |
| `IOSQE_IO_DRAIN` | bit 1 | 等待Inflight I/O完成后执行 |
| `IOSQE_IO_LINK` | bit 2 | 链接下一个SQE形成链 |
| `IOSQE_IO_HARDLINK` | bit 3 | 强制链接,不因错误断开 |
| `IOSQE_ASYNC` | bit 4 | 强制异步执行 |
| `IOSQE_BUFFER_SELECT` | bit 5 | 从缓冲区组选择缓冲区 |

### 3.3 操作码 (IORING_OP_*)

```c
enum io_uring_op {
    IORING_OP_NOP,                 // 0  无操作
    IORING_OP_READV,               // 1  分散读
    IORING_OP_WRITEV,              // 2  分散写
    IORING_OP_FSYNC,              // 3  文件同步
    IORING_OP_READ_FIXED,         // 4  固定缓冲区读
    IORING_OP_WRITE_FIXED,        // 5  固定缓冲区写
    IORING_OP_POLL_ADD,           // 6  Poll 添加
    IORING_OP_TIMEOUT,           // 11 超时
    IORING_OP_ACCEPT,             // 13 接受连接
    IORING_OP_ASYNC_CANCEL,       // 14 异步取消
    IORING_OP_LINK_TIMEOUT,        // 15 链接超时
    IORING_OP_CONNECT,            // 16 连接
    IORING_OP_READ,               // 22 读操作
    IORING_OP_WRITE,              // 23 写操作
    IORING_OP_LAST,
};
```

---

## 4. Completion Queue Entry (CQE)

### 4.1 struct io_uring_cqe

**源码位置**: `/Users/sphinx/github/linux/include/uapi/linux/io_uring.h:493-503`

```c
struct io_uring_cqe {
    __u64 user_data;    /* SQE 中设置的用户数据 */
    __s32 res;         /* 操作结果 (类似系统调用返回值) */
    __u32 flags;       /* CQE 标志 */
};
```

### 4.2 CQE 标志 (cqe->flags)

| 标志 | 说明 |
|------|------|
| `IORING_CQE_F_BUFFER` | 上 16 位是缓冲区 ID |
| `IORING_CQE_F_MORE` | 同一个 SQE 会产生更多 CQE |
| `IORING_CQE_F_NOTIF` | 通知 CQE (用于 SEND_ZC) |

---

## 5. io_uring_setup 系统调用

### 5.1 函数签名

**源码位置**: `/Users/sphinx/github/linux/io_uring/io_uring.c:3104-3114`

```c
SYSCALL_DEFINE2(io_uring_setup, u32, entries, struct io_uring_params __user *, params)
{
    ret = io_uring_allowed();
    if (ret) return ret;
    return io_uring_setup(entries, params);
}
```

### 5.2 io_uring_create 核心流程

**源码位置**: `/Users/sphinx/github/linux/io_uring/io_uring.c:2934-3058`

```c
static __cold int io_uring_create(struct io_ctx_config *config)
{
    struct io_uring_params *p = &config->p;
    struct io_ring_ctx *ctx;
    struct file *file;
    
    // 1. 准备配置
    ret = io_prepare_config(config);
    
    // 2. 分配 ring context
    ctx = io_ring_ctx_alloc(p);
    
    // 3. 设置时钟
    ctx->clockid = CLOCK_MONOTONIC;
    
    // 4. 设置 IOPOLL 模式
    if (ctx->flags & IORING_SETUP_IOPOLL)
        ctx->syscall_iopoll = 1;
    
    // 5. 分配共享内存环
    ret = io_allocate_scq_urings(ctx, config);
    
    // 6. 创建 SQ POLL 线程 (如果启用)
    ret = io_sq_offload_create(ctx, p);
    
    // 7. 获取 anon inode file
    file = io_uring_get_file(ctx);
    
    // 8. 添加到 task context
    ret = __io_uring_add_tctx_node(ctx);
    
    // 9. 安装 fd
    ret = io_uring_install_fd(file);
    
    return ret;
}
```

---

## 6. io_uring_enter 系统调用

### 6.1 函数签名

**源码位置**: `/Users/sphinx/github/linux/io_uring/io_uring.c:2542-2667`

```c
SYSCALL_DEFINE6(io_uring_enter, unsigned int, fd, u32, to_submit,
    u32, min_complete, u32, flags, const void __user *, argp, size_t argsz)
{
    struct io_ring_ctx *ctx;
    struct file *file;
    
    // 1. 获取 ring file
    if (flags & IORING_ENTER_REGISTERED_RING) {
        file = tctx->registered_rings[fd];
    } else {
        file = fget(fd);
    }
    ctx = file->private_data;
    
    // 2. SQPOLL 模式处理
    if (ctx->flags & IORING_SETUP_SQPOLL) {
        if (flags & IORING_ENTER_SQ_WAKEUP)
            wake_up(&ctx->sq_data->wait);
        return to_submit;
    }
    
    // 3. 提交 SQE
    if (to_submit) {
        mutex_lock(&ctx->uring_lock);
        ret = io_submit_sqes(ctx, to_submit);
        mutex_unlock(&ctx->uring_lock);
    }
    
    // 4. 等待完成
    if (flags & IORING_ENTER_GETEVENTS) {
        if (ctx->syscall_iopoll) {
            ret2 = io_iopoll_check(ctx, min_complete);
        } else {
            ret2 = io_cqring_wait(ctx, min_complete, flags, &ext_arg);
        }
    }
    
    return ret;
}
```

### 6.2 io_submit_sqes - 批量提交

**源码位置**: `/Users/sphinx/github/linux/io_uring/io_uring.c:2008-2062`

```c
int io_submit_sqes(struct io_ring_ctx *ctx, unsigned int nr)
{
    unsigned int entries;
    unsigned int left;
    int ret;
    
    entries = min(nr, entries);
    if (unlikely(!entries)) return 0;
    
    ret = left = entries;
    io_get_task_refs(left);
    io_submit_state_start(&ctx->submit_state, left);
    
    do {
        struct io_kiocb *req;
        
        if (unlikely(!io_alloc_req(ctx, &req))) break;
        if (unlikely(!io_get_sqe(ctx, &sqe))) {
            io_req_add_to_cache(req, ctx);
            break;
        }
        if (unlikely(io_submit_sqe(ctx, req, sqe, &left) &&
            !(ctx->flags & IORING_SETUP_SUBMIT_ALL))) {
            left--;
            break;
        }
    } while (--left);
    
    io_commit_sqring(ctx);
    return ret;
}
```

---

## 7. Polling 模式

### 7.1 IOPOLL 模式设置

当设置 `IORING_SETUP_IOPOLL` 且不是 `SQPOLL` 时:
```c
ctx->syscall_iopoll = 1;
```

### 7.2 io_iopoll_check - I/O 轮询检查

**源码位置**: `/Users/sphinx/github/linux/io_uring/io_uring.c:1188-1259`

```c
static int io_iopoll_check(struct io_ring_ctx *ctx, unsigned int min_events)
{
    unsigned int nr_events = 0;
    min_events = min(min_events, ctx->cq_entries);
    
    if (io_cqring_events(ctx)) return 0;
    
    do {
        if (list_empty(&ctx->iopoll_list) || io_task_work_pending(ctx)) {
            (void) io_run_local_work_locked(ctx, min_events);
        }
        
        ret = io_do_iopoll(ctx, !min_events);
        if (unlikely(ret < 0)) return ret;
        if (task_sigpending(current)) return -EINTR;
        if (need_resched()) break;
        
        nr_events += ret;
    } while (nr_events < min_events);
    
    return 0;
}
```

---

## 8. Fixed File Table

### 8.1 struct io_file_table

**源码位置**: `/Users/sphinx/github/linux/include/linux/io_uring_types.h:65-69`

```c
struct io_file_table {
    struct io_rsrc_data data;     // 资源数据
    unsigned long *bitmap;         // 文件槽位位图
    unsigned int alloc_hint;       // 分配提示
};
```

### 8.2 使用固定文件 (IOSQE_FIXED_FILE)

**源码位置**: `/Users/sphinx/github/linux/io_uring/filetable.c:62-85`

```c
static int io_install_fixed_file(struct io_ring_ctx *ctx, struct file *file, u32 slot_index)
{
    struct io_rsrc_node *node;
    
    if (io_is_uring_fops(file)) return -EBADF;
    if (!ctx->file_table.data.nr) return -ENXIO;
    if (slot_index >= ctx->file_table.data.nr) return -EINVAL;
    
    node = io_rsrc_node_alloc(ctx, IORING_RSRC_FILE);
    if (!node) return -ENOMEM;
    
    if (!io_reset_rsrc_node(ctx, &ctx->file_table.data, slot_index))
        io_file_bitmap_set(&ctx->file_table, slot_index);
    
    ctx->file_table.data.nodes[slot_index] = node;
    io_fixed_file_set(node, file);
    return 0;
}
```

---

## 9. Linked Requests 链接请求

### 9.1 链接标志

```c
#define IOSQE_IO_LINK       (1U << 2)  /* 链接下一个 sqe */
#define IOSQE_IO_HARDLINK   (1U << 3)  /* 强制链接 */
```

### 9.2 链接超时处理

**源码位置**: `/Users/sphinx/github/linux/io_uring/timeout.c:350-422`

```c
static enum hrtimer_restart io_link_timeout_fn(struct hrtimer *timer)
{
    struct io_timeout_data *data = container_of(timer, struct io_timeout_data, timer);
    struct io_kiocb *req = data->req;
    
    req->flags |= REQ_F_LINK_TIMEOUT;
    io_disarm_next(req);
    io_req_complete_defer(req);
    
    return HRTIMER_NORESTART;
}
```

---

## 10. 知识点关联表

### 10.1 核心数据结构关系

| 数据结构 | 位置 | 用途 |
|----------|------|------|
| `struct io_uring_sqe` | uapi/io_uring.h:30-118 | SQE,64字节,描述操作 |
| `struct io_uring_cqe` | uapi/io_uring.h:493-503 | CQE,完成事件 |
| `struct io_rings` | io_uring_types.h:151-220 | 共享内存环 |
| `struct io_ring_ctx` | io_uring_types.h:271-491 | Ring 上下文 |
| `struct io_kiocb` | io_uring_types.h:688-770 | 内核请求控制块 |
| `struct io_file_table` | io_uring_types.h:65-69 | 固定文件表 |

### 10.2 系统调用流程

| 阶段 | 函数 | 位置 | 说明 |
|------|------|------|------|
| 创建 | `io_uring_setup()` | io_uring.c:3104 | 创建 ring |
| 创建 | `io_uring_create()` | io_uring.c:2934 | 核心创建逻辑 |
| 提交 | `io_uring_enter()` | io_uring.c:2542 | 提交和等待 |
| 提交 | `io_submit_sqes()` | io_uring.c:2008 | 批量提交 SQE |
| 完成 | `io_cqring_wait()` | wait.c:188 | 等待 CQE |
| 完成 | `io_iopoll_check()` | io_uring.c:1188 | IOPOLL 轮询 |

### 10.3 操作码与处理函数映射

| 操作码 | prep 函数 | issue 函数 | 位置 |
|--------|-----------|------------|------|
| `IORING_OP_READ` | `io_prep_read` | `io_read` | rw.c |
| `IORING_OP_WRITE` | `io_prep_write` | `io_write` | rw.c |
| `IORING_OP_READV` | `io_prep_readv` | `io_read` | rw.c |
| `IORING_OP_SENDMSG` | `io_sendmsg_prep` | `io_sendmsg` | net.c |
| `IORING_OP_RECVMSG` | `io_recvmsg_prep` | `io_recvmsg` | net.c |
| `IORING_OP_TIMEOUT` | `io_timeout_prep` | `io_timeout` | timeout.c |
| `IORING_OP_ACCEPT` | `io_accept_prep` | `io_accept` | net.c |

### 10.4 关键内存偏移

```c
#define IORING_OFF_SQ_RING       0ULL        // SQ 环偏移
#define IORING_OFF_CQ_RING      0x8000000ULL // CQ 环偏移
#define IORING_OFF_SQES         0x10000000ULL // SQE 数组偏移
```

---

## 总结

io_uring 是 Linux 内核迄今为止最复杂的子系统之一，其设计核心包括:

1. **无锁设计**: 通过 Ring Buffer 实现用户态与内核态的高效通信,最小化锁竞争
2. **批量操作**: 支持批量提交和批量完成,提高吞吐量
3. **灵活的资源管理**: Fixed File Table 和固定缓冲区减少每次操作的开销
4. **多种工作模式**: 支持轮询模式、内核轮询线程、异步执行等多种配置
5. **链接请求**: 支持操作链和超时控制,实现复杂的工作流

---

**文档版本**: R1  
**分析源码版本**: Linux Kernel (latest)  
**生成时间**: 2026-04-27
