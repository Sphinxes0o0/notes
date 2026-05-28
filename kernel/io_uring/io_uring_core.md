# Linux Kernel io_uring 子系统核心架构分析

## 目录

1. [io_uring 概述](#1-io_uring-概述)
2. [核心数据结构](#2-核心数据结构)
3. [系统调用接口](#3-系统调用接口)
4. [SQ/CQ 机制](#4-sqcq-机制)
5. [文件描述符管理](#5-文件描述符管理)
6. [异步执行机制](#6-异步执行机制)
7. [架构图](#7-架构图)

---

## 1. io_uring 概述

### 1.1 什么是 io_uring

io_uring 是 Linux kernel 5.1 引入的高性能异步 I/O 接口，由 Jens Axboe 开发。它通过共享内存的环形队列（Ring Buffer）实现用户态与内核态之间的高效通信，显著降低了系统调用的开销。

**源码位置**: `/Users/sphinx/github/linux/io_uring/io_uring.c`

### 1.2 解决的问题

相比传统的 epoll/aio，io_uring 解决了以下问题：

| 特性 | epoll | aio (glibc) | io_uring |
|------|-------|-------------|----------|
| 异步 I/O | 仅支持网络/文件描述符监控 | 仅支持磁盘 I/O | 支持所有 I/O 类型 |
| 系统调用次数 | 每次操作需多次 syscall | 每次操作需多次 syscall | 批量提交，减少 syscall |
| 轮询方式 | 用户轮询 | 内核轮询 | 零轮询（支持 SQPOLL） |
| 内存拷贝 | 多次 | 多次 | 共享内存，无拷贝 |
| 功能完整性 | 有限 | 有限 | 完整文件系统支持 |

### 1.3 核心概念

```
┌─────────────────────────────────────────────────────────────┐
│                      用户态进程                              │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │  Submission Queue│        │ Completion Queue │           │
│  │     (SQ)         │  ──►   │     (CQ)         │           │
│  │  用户写入 SQE    │         │  内核写入 CQE    │           │
│  └─────────────────┘         └─────────────────┘            │
└─────────────────────────────────────────────────────────────┘
           │                                  ▲
           │        mmap 共享内存             │
           ▼                                  │
┌─────────────────────────────────────────────────────────────┐
│                      内核态                                  │
│  ┌─────────────────────────────────────────────────┐        │
│  │              io_ring_ctx (环上下文)              │        │
│  │  - 持有 SQ/CQ 环的元数据                        │        │
│  │  - 管理文件描述符表                             │        │
│  │  - 处理请求的生命周期                           │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

**SQ (Submission Queue)**: 用户态向内核提交请求的队列
**CQ (Completion Queue)**: 内核向用户态返回完成事件的队列

---

## 2. 核心数据结构

### 2.1 struct io_ring_ctx - 环上下文

**定义位置**: `/Users/sphinx/github/linux/include/linux/io_uring_types.h:271`

```c
struct io_ring_ctx {
    /* const or read-mostly hot data - 常量/只读热数据 */
    struct {
        unsigned int        flags;              // 环标志 (IORING_SETUP_*)
        unsigned int        drain_next: 1;
        unsigned int        op_restricted: 1;
        unsigned int        reg_restricted: 1;
        // ... 更多标志位

        struct task_struct  *submitter_task;   // 提交者任务
        struct io_rings     *rings;            // 共享内存中的环
        struct percpu_ref   refs;              // 引用计数
        // ...
    } ____cacheline_aligned_in_smp;

    /* submission data - 提交数据 */
    struct {
        struct mutex        uring_lock;        // 环锁，保护提交

        u32             *sq_array;             // SQ索引数组
        struct io_uring_sqe *sq_sqes;          // SQE数组
        unsigned        cached_sq_head;        // 缓存的SQ头
        unsigned        sq_entries;            // SQ条目数

        struct io_file_table   file_table;     // 文件描述符表
        struct io_rsrc_data    buf_table;      // 缓冲区表
        struct io_submit_state submit_state;    // 提交状态
        // ...
    } ____cacheline_aligned_in_smp;

    /* completion data - 完成数据 */
    struct {
        struct io_uring_cqe *cqe_cached;       // 缓存的CQE指针
        struct io_uring_cqe *cqe_sentinel;     // CQE缓存结束位置
        unsigned        cached_cq_tail;        // 缓存的CQ尾
        unsigned        cq_entries;            // CQ条目数
        // ...
    } ____cacheline_aligned_in_smp;

    spinlock_t        completion_lock;         // 完成锁
    struct list_head  cq_overflow_list;        // CQ溢出列表
    // ...
};
```

**关键字段说明**:
- `flags`: 控制环的行为（如 IOPOLL, SQPOLL, R_DISABLED 等）
- `rings`: 指向 mmap 共享内存区域的指针
- `uring_lock`: 保护提交过程的重入锁
- `sq_array`: SQE 索引数组，存储实际 SQE 的位置
- `file_table`: 固定文件描述符表

### 2.2 struct io_rings - 共享环结构

**定义位置**: `/Users/sphinx/github/linux/include/linux/io_uring_types.h:151`

```c
struct io_rings {
    /* 内核控制 SQ head 和 CQ tail，用户控制 SQ tail 和 CQ head */
    struct io_uring     sq, cq;

    /* 位掩码 (ring_entries - 1)，用于索引包装 */
    u32         sq_ring_mask, cq_ring_mask;
    /* 环大小 (2的幂) */
    u32         sq_ring_entries, cq_ring_entries;

    /* 被丢弃的无效条目数 (内核写) */
    u32         sq_dropped;

    /* 运行时 SQ 标志 (内核写) */
    atomic_t    sq_flags;
    /* 运行时 CQ 标志 (用户写) */
    u32         cq_flags;

    /* 因 CQ 满而丢失的完成事件数 (内核写) */
    u32         cq_overflow;

    /* 完成事件环缓冲区 */
    struct io_uring_cqe   cqes[] ____cacheline_aligned_in_smp;
};
```

### 2.3 struct io_uring_sqe - 提交队列条目

**定义位置**: `/Users/sphinx/github/linux/include/uapi/linux/io_uring.h:30`

```c
struct io_uring_sqe {
    __u8    opcode;         /* 操作类型 (IORING_OP_*) */
    __u8    flags;          /* IOSQE_* 标志 */
    __u16   ioprio;         /* 请求优先级 */
    __s32   fd;             /* 文件描述符 */

    union {
        __u64  off;         /* 文件偏移 或 第二个地址 */
        __u64  addr2;
        struct {
            __u32 cmd_op;
            __u32 __pad1;
        };
    };

    union {
        __u64  addr;        /* 缓冲区地址 或 iovecs 指针 */
        __u64  splice_off_in;
        struct {
            __u32 level;
            __u32 optname;
        };
    };

    __u32   len;            /* 缓冲区大小或 iovec 数量 */

    union {
        __u32  rw_flags;    /* 读写标志 */
        __u32  fsync_flags;
        __u32  poll_events;
        // ... 更多标志联合
    };

    __u64   user_data;      /* 用户数据，回传至 CQE */

    union {
        __u16 buf_index;    /* 固定缓冲区索引 */
        __u16 buf_group;   /* 缓冲区组 ID */
    } __attribute__((packed));

    __u16   personality;    /* 安全上下文 personality */

    union {
        __s32  splice_fd_in;       /* splice 源fd */
        __u32  file_index;         /* 直接描述符索引 */
        __u32  optlen;             /* options 长度 */
        // ...
    };

    union {
        struct {
            __u64 addr3;
            __u64 __pad2[1];
        };
        __u64 attr_ptr;            /* 属性指针 */
        __u64 optval;              /* option 值 */
        __u8  cmd[0];             /* 128字节 SQE 的命令数据 */
    };
};
```

**SQE 标志** (`/Users/sphinx/github/linux/include/uapi/linux/io_uring.h:151`):
```c
#define IOSQE_FIXED_FILE     (1U << 0)   /* 使用固定文件描述符 */
#define IOSQE_IO_DRAIN       (1U << 1)   /* 排空后执行 */
#define IOSQE_IO_LINK        (1U << 2)   /* 链接下一个 SQE */
#define IOSQE_IO_HARDLINK    (1U << 3)   /* 硬链接 */
#define IOSQE_ASYNC          (1U << 4)   /* 总是异步执行 */
#define IOSQE_BUFFER_SELECT  (1U << 5)   /* 从组中选择缓冲区 */
#define IOSQE_CQE_SKIP_SUCCESS (1U << 6) /* 成功时不发布 CQE */
```

### 2.4 struct io_uring_cqe - 完成队列条目

**定义位置**: `/Users/sphinx/github/linux/include/uapi/linux/io_uring.h:493`

```c
struct io_uring_cqe {
    __u64   user_data;      /* 关联的 SQE user_data */
    __s32   res;            /* 结果码 (类似 syscall 返回值) */
    __u32   flags;          /* CQE 标志 */

    /* 如果使用 IORING_SETUP_CQE32，此处为额外数据 */
    __u64   big_cqe[];
};
```

**CQE 标志** (`/Users/sphinx/github/linux/include/uapi/linux/io_uring.h:531`):
```c
#define IORING_CQE_F_BUFFER  (1U << 0)   /* 上16位是缓冲区ID */
#define IORING_CQE_F_MORE    (1U << 1)   /* SQE 将产生更多 CQE */
#define IORING_CQE_F_SOCK_NONEMPTY (1U << 2) /* socket  recv 还有数据 */
#define IORING_CQE_F_NOTIF   (1U << 3)   /* 通知 CQE */
#define IORING_CQE_F_BUF_MORE (1U << 4)  /* 缓冲区还有更多数据 */
#define IORING_CQE_F_SKIP    (1U << 5)   /* 跳过此 CQE */
#define IORING_CQE_F_32      (1U << 15) /* 32字节 CQE 模式 */
```

### 2.5 struct io_kiocb - 内核 I/O 控制块

**定义位置**: `/Users/sphinx/github/linux/include/linux/io_uring_types.h:688`

```c
struct io_kiocb {
    union {
        struct file     *file;      /* 关联的文件 */
        struct io_cmd_data cmd;     /* 命令数据 */
    };

    u8              opcode;         /* 操作码 */
    u8              iopoll_completed;
    u16             buf_index;      /* 缓冲区索引 */

    unsigned        nr_tw;

    /* REQ_F_* 标志 */
    io_req_flags_t      flags;

    struct io_cqe      cqe;        /* 完成的 CQE 数据 */

    struct io_ring_ctx *ctx;        /* 环上下文 */
    struct io_uring_task *tctx;     /* 任务上下文 */

    union {
        struct io_buffer  *kbuf;   /* 选中的缓冲区 */
        struct io_rsrc_node *buf_node;
    };

    union {
        struct io_wq_work_node  comp_list; /* 链表节点 */
        __poll_t                apoll_events;
    };

    struct io_rsrc_node    *file_node;
    atomic_t                refs;
    bool                    cancel_seq_set;

    union {
        struct io_task_work    io_task_work;
        u64                    iopoll_start;
    };

    union {
        struct hlist_node  hash_node;
        struct list_head   iopoll_node;
        struct rcu_head    rcu_head;
    };

    struct async_poll      *apoll;       /* 异步轮询状态 */
    void                   *async_data;  /* 异步操作数据 */
    atomic_t                poll_refs;
    struct io_kiocb        *link;        /* 链接的请求 */
    const struct cred      *creds;       /* 凭证 */
    struct io_wq_work      work;         /* 工作队列项 */

    struct io_big_cqe {
        u64 extra1;
        u64 extra2;
    } big_cqe;
};
```

---

## 3. 系统调用接口

io_uring 提供三个主要系统调用。

### 3.1 io_uring_setup() - 创建 io_uring 实例

**源码位置**: `/Users/sphinx/github/linux/io_uring/io_uring.c:3104`

```c
SYSCALL_DEFINE2(io_uring_setup, u32, entries,
        struct io_uring_params __user *, params)
{
    int ret;

    ret = io_uring_allowed();
    if (ret)
        return ret;

    return io_uring_setup(entries, params);
}
```

**核心流程** (`io_uring_create` at line 2934):

1. **参数验证和预处理** (`io_prepare_config` at line 2864):
   - 检查 flags 合法性 (`io_uring_sanitise_params`)
   - 填充参数 (`io_uring_fill_params`): 设置 sq_entries, cq_entries
   - 计算环大小 (`rings_size`)

2. **分配环上下文** (`io_ring_ctx_alloc` at line 223):
   - 分配 `struct io_ring_ctx`
   - 初始化各种锁、列表、缓存
   - 分配取消哈希表

3. **分配共享内存** (`io_allocate_scq_urings` at line 2687):
   - 创建 SQ 和 CQ 环内存区域
   - 初始化 `io_rings` 结构

4. **创建匿名 inode 文件** (`io_uring_get_file` at line 2751):
   ```c
   return anon_inode_create_getfile("[io_uring]", &io_uring_fops, ctx,
                   O_RDWR | O_CLOEXEC, NULL);
   ```

5. **设置 SQ 轮询线程** (如果设置了 `IORING_SETUP_SQPOLL`):
   - 创建内核线程处理 SQ
   - 调用 `io_sq_offload_create`

### 3.2 io_uring_enter() - 提交请求和获取完成

**源码位置**: `/Users/sphinx/github/linux/io_uring/io_uring.c:2542`

```c
SYSCALL_DEFINE6(io_uring_enter, unsigned int, fd, u32, to_submit,
        u32, min_complete, u32, flags, const void __user *, argp,
        size_t, argsz)
{
    // ... 获取文件和支持轮询的处理
    ctx = file->private_data;

    // SQPOLL 模式处理
    if (ctx->flags & IORING_SETUP_SQPOLL) {
        if (flags & IORING_ENTER_SQ_WAKEUP)
            wake_up(&ctx->sq_data->wait);
        if (flags & IORING_ENTER_SQ_WAIT)
            io_sqpoll_wait_sq(ctx);
        ret = to_submit;
    } else if (to_submit) {
        // 正常提交模式
        ret = io_uring_add_tctx_node(ctx);
        mutex_lock(&ctx->uring_lock);
        ret = io_submit_sqes(ctx, to_submit);
        mutex_unlock(&ctx->uring_lock);
    }

    // 获取完成事件
    if (flags & IORING_ENTER_GETEVENTS) {
        if (ctx->syscall_iopoll)
            ret2 = io_iopoll_check(ctx, min_complete);
        else
            ret2 = io_cqring_wait(ctx, min_complete, flags, &ext_arg);
    }
}
```

**关键参数**:
- `fd`: io_uring 文件描述符
- `to_submit`: 要提交的 SQE 数量
- `min_complete`: 等待完成的最小数量
- `flags`: 控制标志 (`IORING_ENTER_*`)
- `argp`: 扩展参数指针

### 3.3 io_uring_register() - 注册资源

**源码位置**: `/Users/sphinx/github/linux/io_uring/register.c:1020`

```c
SYSCALL_DEFINE4(io_uring_register, unsigned int, fd, unsigned int, opcode,
        void __user *, arg, unsigned int, nr_args)
{
    struct io_ring_ctx *ctx;
    long ret = -EBADF;
    struct file *file;

    use_registered_ring = !!(opcode & IORING_REGISTER_USE_REGISTERED_RING);
    opcode &= ~IORING_REGISTER_USE_REGISTERED_RING;

    if (opcode >= IORING_REGISTER_LAST)
        return -EINVAL;

    file = io_uring_register_get_file(fd, use_registered_ring);
    if (IS_ERR(file))
        return PTR_ERR(file);
    ctx = file->private_data;

    mutex_lock(&ctx->uring_lock);
    ret = __io_uring_register(ctx, opcode, arg, nr_args);
    mutex_unlock(&ctx->uring_lock);

    fput(file);
    return ret;
}
```

**主要注册操作**:

| Opcode | 功能 |
|--------|------|
| `IORING_REGISTER_BUFFERS` | 注册缓冲区 |
| `IORING_REGISTER_FILES` | 注册文件描述符 |
| `IORING_REGISTER_EVENTFD` | 注册 eventfd 用于完成通知 |
| `IORING_REGISTER_FILES_UPDATE` | 更新已注册的文件 |
| `IORING_REGISTER_RESTRICTIONS` | 设置操作限制 |
| `IORING_REGISTER_PROBE` | 探测支持的操作 |
| `IORING_REGISTER_PBUF_RING` | 注册提供缓冲区环 |
| `IORING_REGISTER_CLOCK` | 注册时钟源 |

---

## 4. SQ/CQ 机制

### 4.1 共享内存布局

```
┌────────────────────────────────────────────────────────────────┐
│                    mmap 区域                                   │
├────────────────────────────────────────────────────────────────┤
│  struct io_rings (共用体 sq/cq head/tail)                      │
│  ├─ sq.head, sq.tail                                          │
│  ├─ cq.head, cq.tail                                          │
│  ├─ sq_ring_mask, cq_ring_mask                                │
│  ├─ sq_ring_entries, cq_ring_entries                         │
│  ├─ sq_dropped, sq_flags, cq_flags, cq_overflow              │
│  └─ cqes[] (CQE 数组)                                         │
├────────────────────────────────────────────────────────────────┤
│  sq_array[] (u32 索引数组，仅当 !IORING_SETUP_NO_SQARRAY)     │
├────────────────────────────────────────────────────────────────┤
│  sq_sqes[] (struct io_uring_sqe 数组)                         │
└────────────────────────────────────────────────────────────────┘
```

**mmap 偏移量** (`/Users/sphinx/github/linux/include/uapi/linux/io_uring.h:544`):
```c
#define IORING_OFF_SQ_RING       0ULL      // SQ 环基地址
#define IORING_OFF_CQ_RING       0x8000000ULL // CQ 环基地址
#define IORING_OFF_SQES          0x10000000ULL // SQE 数组基地址
#define IORING_OFF_PBUF_RING     0x80000000ULL // 提供缓冲区环
```

### 4.2 提交流程 (Submission)

**源码位置**: `/Users/sphinx/github/linux/io_uring/io_uring.c:2008`

```c
int io_submit_sqes(struct io_ring_ctx *ctx, unsigned int nr)
    __must_hold(&ctx->uring_lock)
{
    unsigned int entries;
    unsigned int left;
    int ret;

    // 获取 SQ 中的可用条目数
    entries = __io_sqring_entries(ctx);
    entries = min(nr, entries);

    ret = left = entries;
    io_get_task_refs(left);                    // 获取任务引用
    io_submit_state_start(&ctx->submit_state, left);

    do {
        const struct io_uring_sqe *sqe;
        struct io_kiocb *req;

        // 分配请求结构
        if (!io_alloc_req(ctx, &req))
            break;

        // 获取下一个 SQE
        if (!io_get_sqe(ctx, &sqe)) {
            io_req_add_to_cache(req, ctx);
            break;
        }

        // 初始化并提交 SQE
        if (io_submit_sqe(ctx, req, sqe, &left))
            break;

    } while (--left);

    io_submit_state_end(ctx);
    io_commit_sqring(ctx);                    // 提交 SQ head
    return ret;
}
```

**SQE 获取** (`io_get_sqe` at line 1976):
```c
static bool io_get_sqe(struct io_ring_ctx *ctx, const struct io_uring_sqe **sqe)
{
    unsigned mask = ctx->sq_entries - 1;
    unsigned head = ctx->cached_sq_head++ & mask;

    // 从 sq_array 获取索引（如果不是 NO_SQARRAY 模式）
    if (static_branch_unlikely(&io_key_has_sqarray.key) &&
        (!(ctx->flags & IORING_SETUP_NO_SQARRAY))) {
        head = READ_ONCE(ctx->sq_array[head]);
        if (unlikely(head >= ctx->sq_entries)) {
            WRITE_ONCE(ctx->rings->sq_dropped,
                   READ_ONCE(ctx->rings->sq_dropped) + 1);
            return false;
        }
    }

    // 获取 SQE 指针（支持 SQE128 模式）
    if (ctx->flags & IORING_SETUP_SQE128)
        head <<= 1;
    *sqe = &ctx->sq_sqes[head];
    return true;
}
```

### 4.3 完成流程 (Completion)

**CQE 获取** (`io_get_cqe` at line 279 in `io_uring.h`):
```c
static inline bool io_get_cqe(struct io_ring_ctx *ctx, struct io_uring_cqe **ret,
                bool cqe32)
{
    return io_get_cqe_overflow(ctx, ret, false, cqe32);
}
```

**CQE 填充** (`io_fill_cqe_req` at line 294 in `io_uring.h`):
```c
static __always_inline bool io_fill_cqe_req(struct io_ring_ctx *ctx,
                        struct io_kiocb *req)
{
    bool is_cqe32 = req->cqe.flags & IORING_CQE_F_32;
    struct io_uring_cqe *cqe;

    if (unlikely(!io_get_cqe(ctx, &cqe, is_cqe32)))
        return false;

    memcpy(cqe, &req->cqe, sizeof(*cqe));
    if (ctx->flags & IORING_SETUP_CQE32 || is_cqe32) {
        memcpy(cqe->big_cqe, &req->big_cqe, sizeof(*cqe));
        memset(&req->big_cqe, 0, sizeof(req->big_cqe));
    }

    return true;
}
```

### 4.4 内存屏障与同步

io_uring 使用特定的内存屏障确保用户态和内核态之间的数据一致性：

**关键同步点**:

1. **SQ 提交** (用户态写 SQ tail 后):
   - 应用需要 `smp_wmb()` 在写 SQ tail 之前
   - 内核使用 `smp_load_acquire()` 读 tail

2. **CQ 完成** (内核写 CQE 后):
   - 内核使用 `smp_store_release()` 写 CQ tail
   - 应用使用 `smp_rmb()` 在读 CQ tail 之后

3. **SQPOLL 模式**:
   - 应用更新 SQ tail 后需要 `smp_mb()`
   - 然后检查 `IORING_SQ_NEED_WAKEUP` 标志

---

## 5. 文件描述符管理

### 5.1 io_uring_get_fd() / io_uring_release()

io_uring 使用匿名 inode 作为文件描述符，文件操作定义在 `io_uring_fops`：

**源码位置**: `/Users/sphinx/github/linux/io_uring/io_uring.c:2669`

```c
static const struct file_operations io_uring_fops = {
    .release    = io_uring_release,
    .mmap       = io_uring_mmap,
    .get_unmapped_area = io_uring_get_unmapped_area,
    .poll       = io_uring_poll,
    .show_fdinfo = io_uring_show_fdinfo,
};
```

### 5.2 固定文件描述符表

**struct io_file_table** (`/Users/sphinx/github/linux/include/linux/io_uring_types.h:65`):
```c
struct io_file_table {
    struct io_rsrc_data data;
    unsigned long *bitmap;
    unsigned int alloc_hint;
};
```

**注册文件** (`io_register_files` at `register.c`):
- 通过 `IORING_REGISTER_FILES` 注册一组文件描述符
- 文件存储在 `ctx->file_table` 中
- 使用 `IOSQE_FIXED_FILE` 标志引用

**获取固定文件** (`io_file_get_fixed` at line 187 in `io_uring.h`):
```c
struct file *io_file_get_fixed(struct io_kiocb *req, int fd,
                   unsigned issue_flags);
```

---

## 6. 异步执行机制

### 6.1 io-wq 工作队列

io_uring 使用 `io-wq` 处理阻塞 I/O 操作：

**源码位置**: `/Users/sphinx/github/linux/io_uring/io-wq.c`

```c
// 提交到 io-wq (io_queue_iowq at line 406 in io_uring.c)
static void io_queue_iowq(struct io_kiocb *req)
{
    struct io_uring_task *tctx = req->tctx;

    if ((current->flags & PF_KTHREAD) || !tctx->io_wq) {
        io_req_task_queue_fail(req, -ECANCELED);
        return;
    }

    io_prep_async_link(req);
    io_wq_enqueue(tctx->io_wq, &req->work);
}
```

### 6.2 Task Work

Task Work 用于在进程上下文执行异步完成处理：

**io_req_task_work_add** (`tw.c`):
- 将请求的 task_work 函数添加到当前任务的 task_work 列表
- 下次系统调用返回或异常处理时执行

### 6.3 SQPOLL 模式

**源码位置**: `/Users/sphinx/github/linux/io_uring/sqpoll.c`

当设置 `IORING_SETUP_SQPOLL` 标志时：

```c
// io_sq_thread (sqpoll.c line ~300)
static int io_sq_thread(void *data)
{
    struct io_sq_data *sqd = data;
    // ...

    while (!kthread_should_stop()) {
        // 检查是否有待处理的 SQE
        if (io_sqring_entries(ctx) > 0) {
            // 处理提交
            mutex_lock(&ctx->uring_lock);
            io_submit_sqes(ctx, -1);
            mutex_unlock(&ctx->uring_lock);
        }

        // 空闲时等待
        if (list_empty(&ctx->iopoll_list))
            schedule_timeout_idle(ctx->sq_thread_idle);
    }
}
```

---

## 7. 架构图

### 7.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                           用户态应用                                  │
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    liburing (用户库)                         │   │
│   │  - io_uring_queue_init()                                    │   │
│   │  - io_uring_submit_sqes()                                   │   │
│   │  - io_uring_wait_cqes()                                     │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              │ 系统调用 (io_uring_setup/enter/register) │
│                              ▼                                      │
└─────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│                           内核态 io_uring                           │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    io_ring_ctx (环上下文)                     │   │
│  │                                                               │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │   │
│  │  │  uring_lock │  │completion_ │  │   file_table       │   │   │
│  │  │   (Mutex)   │  │   lock     │  │  (固定FD表)        │   │   │
│  │  └────────────┘  │   (Spin)    │  └────────────────────┘   │   │
│  │                   └────────────┘                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │   │
│  │  │  sq_data   │  │  io_wq     │  │   submit_state     │   │   │
│  │  │(SQPOLL)    │  │(异步工作队列)│  │  (提交状态)        │   │   │
│  │  └────────────┘  └────────────┘  └────────────────────┘   │   │
│  │                                                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    mmap 共享内存                              │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │                  struct io_rings                       │  │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────────────────┐   │  │   │
│  │  │  │ sq head │  │ cq tail │  │      cqes[]         │   │  │   │
│  │  │  │ sq tail │  │ cq head │  │   (CQE 数组)        │   │  │   │
│  │  │  └─────────┘  └─────────┘  └─────────────────────┘   │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │              sq_sqes[] (SQE 数组)                      │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │              sq_array[] (索引数组)                     │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    I/O 操作处理                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │   │
│  │  │   rw.c   │ │ poll.c   │ │ net.c    │ │ uring_cmd.c │   │   │
│  │  │  读写操作 │ │ 轮询操作  │ │ 网络操作   │ │  Uring命令  │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 请求处理流程

```
用户态                           内核态
  │                                │
  │ ┌──────────────────────────┐   │
  │ │ 1. 填写 SQE              │   │
  │ │    - opcode = READ       │   │
  │ │    - fd = 5              │   │
  │ │    - addr = buf_ptr      │   │
  │ │    - len = 1024          │   │
  │ └────────────┬─────────────┘   │
  │              │                 │
  │              ▼                 │
  │ ┌──────────────────────────┐   │
  │ │ 2. 更新 sq.tail          │   │
  │ │    (smp_wmb() 屏障)      │   │
  │ └────────────┬─────────────┘   │
  │              │                 │
  │              │ io_uring_enter()│
  │              ▼                 │
  │ ┌──────────────────────────┐   │
  │ │ 3. 内核读取 sq.tail      │   │
  │ │    (smp_load_acquire)   │   │
  │ └────────────┬─────────────┘   │
  │              │                 │
  │              ▼                 │
  │ ┌──────────────────────────┐   │
  │ │ 4. io_submit_sqes()      │   │
  │ │    - 分配 io_kiocb      │   │
  │ │    - 初始化请求          │   │
  │ │    - 调用 file->ops->   │   │
  │ │      read_iter()        │   │
  │ └────────────┬─────────────┘   │
  │              │                 │
  │              ▼                 │
  │ ┌──────────────────────────┐   │
  │ │ 5. 阻塞操作 → io-wq     │   │
  │ │    (如果需要)            │   │
  │ └────────────┬─────────────┘   │
  │              │                 │
  │              ▼                 │
  │ ┌──────────────────────────┐   │
  │ │ 6. 完成处理               │   │
  │ │    - 填充 CQE            │   │
  │ │    - 写 cq.tail          │   │
  │ │    - (smp_store_release)│   │
  │ └────────────┬─────────────┘   │
  │              │                 │
  │              │ io_uring_enter()│
  │              │ (GETEVENTS)    │
  │              ▼                 │
  │ ┌──────────────────────────┐   │
  │ │ 7. 读取 cq.head          │   │
  │ │    返回完成数             │   │
  │ └────────────┬─────────────┘   │
  │              │                 │
  │              ▼                 │
  │ ┌──────────────────────────┐   │
  │ │ 8. 应用读取 CQE           │   │
  │ │    - res = read 结果     │   │
  │ │    - user_data 匹配      │   │
  │ └──────────────────────────┘   │
  ▼                                ▼
```

### 7.3 支持的操作码

**源码位置**: `/Users/sphinx/github/linux/include/uapi/linux/io_uring.h:253`

```c
enum io_uring_op {
    IORING_OP_NOP,              // 0: 空操作
    IORING_OP_READV,            // 1: 分散/聚集读取
    IORING_OP_WRITEV,           // 2: 分散/聚集写入
    IORING_OP_FSYNC,            // 3: 文件同步
    IORING_OP_READ_FIXED,       // 4: 使用固定缓冲区的读取
    IORING_OP_WRITE_FIXED,      // 5: 使用固定缓冲区的写入
    IORING_OP_POLL_ADD,         // 6: 添加轮询
    IORING_OP_POLL_REMOVE,      // 7: 移除轮询
    IORING_OP_SYNC_FILE_RANGE,  // 8: 同步文件区域
    IORING_OP_SENDMSG,          // 9: 发送消息
    IORING_OP_RECVMSG,          // 10: 接收消息
    IORING_OP_TIMEOUT,          // 11: 超时
    IORING_OP_TIMEOUT_REMOVE,   // 12: 移除超时
    IORING_OP_ACCEPT,           // 13: 接受连接
    IORING_OP_ASYNC_CANCEL,     // 14: 异步取消
    IORING_OP_LINK_TIMEOUT,     // 15: 链接超时
    IORING_OP_CONNECT,          // 16: 连接
    IORING_OP_FALLOCATE,        // 17: 分配空间
    IORING_OP_OPENAT,           // 18: 打开文件
    IORING_OP_CLOSE,            // 19: 关闭文件
    IORING_OP_FILES_UPDATE,     // 20: 更新文件描述符
    IORING_OP_STATX,            // 21: 文件状态
    IORING_OP_READ,             // 22: 读取
    IORING_OP_WRITE,            // 23: 写入
    IORING_OP_FADVISE,          // 24: 文件预读
    IORING_OP_MADVISE,          // 25: 内存建议
    IORING_OP_SEND,             // 26: 发送
    IORING_OP_RECV,             // 27: 接收
    IORING_OP_OPENAT2,          // 28: 打开文件 (openat2)
    IORING_OP_EPOLL_CTL,        // 29: EPOLL 控制
    IORING_OP_SPLICE,           // 30: 拼接
    IORING_OP_PROVIDE_BUFFERS,  // 31: 提供缓冲区
    IORING_OP_REMOVE_BUFFERS,   // 32: 移除缓冲区
    IORING_OP_TEE,              // 33: 管道复制
    IORING_OP_SHUTDOWN,         // 34: 关闭
    IORING_OP_RENAMEAT,         // 35: 重命名
    IORING_OP_UNLINKAT,         // 36: 删除链接
    // ... 更多操作
    IORING_OP_LAST,             // 最后操作码
};
```

---

## 参考代码位置

| 文件 | 说明 |
|------|------|
| `/Users/sphinx/github/linux/io_uring/io_uring.c` | 核心实现 |
| `/Users/sphinx/github/linux/io_uring/io_uring.h` | 内部头文件 |
| `/Users/sphinx/github/linux/include/linux/io_uring_types.h` | 内核类型定义 |
| `/Users/sphinx/github/linux/include/uapi/linux/io_uring.h` | 用户API定义 |
| `/Users/sphinx/github/linux/io_uring/register.c` | 注册系统调用 |
| `/Users/sphinx/github/linux/io_uring/rw.c` | 读写操作 |
| `/Users/sphinx/github/linux/io_uring/sqpoll.c` | SQ轮询线程 |
| `/Users/sphinx/github/linux/io_uring/tctx.c` | 任务上下文 |
| `/Users/sphinx/github/linux/io_uring/poll.c` | 轮询操作 |
| `/Users/sphinx/github/linux/io_uring/net.c` | 网络操作 |
| `/Users/sphinx/github/linux/io_uring/uring_cmd.c` | Uring命令 |

---

*文档生成时间: 2026-04-26*
*基于 Linux Kernel 源码分析*
