# Linux io_uring 子系统操作码 (Opcode) 实现分析

## 目录

1. [概述](#概述)
2. [操作码定义](#操作码定义)
3. [核心数据结构](#核心数据结构)
4. [操作码映射表](#操作码映射表)
5. [NOP 操作](#nop-操作)
6. [读写操作](#读写操作)
7. [文件系统操作](#文件系统操作)
8. [网络操作](#网络操作)
9. [Poll 操作](#poll-操作)
10. [操作执行流程](#操作执行流程)

---

## 概述

io_uring 是 Linux 内核的高性能异步 I/O 接口,核心文件位于 `/Users/sphinx/github/linux/io_uring/` 目录。

### 源码文件结构

| 文件 | 功能 |
|------|------|
| `opdef.c` | 操作码定义和映射表 |
| `opdef.h` | 操作描述结构体定义 |
| `nop.c` | NOP 操作实现 |
| `rw.c` | 读写操作实现 |
| `fs.c` | 文件系统操作实现 |
| `net.c` | 网络操作实现 |
| `poll.c` | Poll 操作实现 |

---

## 操作码定义

### io_uring_op 枚举 (include/uapi/linux/io_uring.h:253-322)

```c
enum io_uring_op {
    IORING_OP_NOP,                 // 0: 空操作
    IORING_OP_READV,               // 1: 矢量读
    IORING_OP_WRITEV,              // 2: 矢量写
    IORING_OP_FSYNC,               // 3: 文件同步
    IORING_OP_READ_FIXED,          // 4: 固定缓冲区读
    IORING_OP_WRITE_FIXED,         // 5: 固定缓冲区写
    IORING_OP_POLL_ADD,            // 6: 添加 poll
    IORING_OP_POLL_REMOVE,         // 7: 移除 poll
    IORING_OP_SYNC_FILE_RANGE,     // 8: 同步文件区域
    IORING_OP_SENDMSG,             // 9: 发送消息
    IORING_OP_RECVMSG,             // 10: 接收消息
    IORING_OP_TIMEOUT,             // 11: 超时
    IORING_OP_TIMEOUT_REMOVE,      // 12: 移除超时
    IORING_OP_ACCEPT,              // 13: 接受连接
    IORING_OP_ASYNC_CANCEL,        // 14: 异步取消
    IORING_OP_LINK_TIMEOUT,        // 15: 链接超时
    IORING_OP_CONNECT,            // 16: 连接
    IORING_OP_FALLOCATE,          // 17: 分配空间
    IORING_OP_OPENAT,              // 18: 打开文件
    IORING_OP_CLOSE,               // 19: 关闭文件
    IORING_OP_FILES_UPDATE,        // 20: 更新文件表
    IORING_OP_STATX,               // 21: 文件状态
    IORING_OP_READ,                // 22: 读
    IORING_OP_WRITE,               // 23: 写
    IORING_OP_FADVISE,             // 24: 文件建议
    IORING_OP_MADVISE,             // 25: 内存建议
    IORING_OP_SEND,                // 26: 发送
    IORING_OP_RECV,                // 27: 接收
    IORING_OP_OPENAT2,             // 28: 打开文件 (openat2)
    IORING_OP_EPOLL_CTL,           // 29: epoll 控制
    IORING_OP_SPLICE,              // 30: 拼接
    IORING_OP_PROVIDE_BUFFERS,     // 31: 提供缓冲区
    IORING_OP_REMOVE_BUFFERS,      // 32: 移除缓冲区
    IORING_OP_TEE,                 // 33: 管道复制
    IORING_OP_SHUTDOWN,            // 34: 关闭
    IORING_OP_RENAMEAT,            // 35: 重命名
    IORING_OP_UNLINKAT,            // 36: 删除链接
    IORING_OP_MKDIRAT,             // 37: 创建目录
    IORING_OP_SYMLINKAT,           // 38: 创建符号链接
    IORING_OP_LINKAT,              // 39: 创建硬链接
    IORING_OP_MSG_RING,            // 40: 消息环
    IORING_OP_FSETXATTR,           // 41: 设置扩展属性
    IORING_OP_SETXATTR,            // 42: 设置扩展属性
    IORING_OP_FGETXATTR,           // 43: 获取扩展属性
    IORING_OP_GETXATTR,            // 44: 获取扩展属性
    IORING_OP_SOCKET,              // 45: 创建套接字
    IORING_OP_URING_CMD,           // 46: uring 命令
    IORING_OP_SEND_ZC,             // 47: 零复制发送
    IORING_OP_SENDMSG_ZC,          // 48: 零复制发送消息
    IORING_OP_READ_MULTISHOT,      // 49: 多重射击读
    IORING_OP_WAITID,              // 50: 等待 ID
    IORING_OP_FUTEX_WAIT,          // 51: futex 等待
    IORING_OP_FUTEX_WAKE,          // 52: futex 唤醒
    IORING_OP_FUTEX_WAITV,         // 53: futex 多等待
    IORING_OP_FIXED_FD_INSTALL,    // 54: 固定 fd 安装
    IORING_OP_FTRUNCATE,           // 55: 截断文件
    IORING_OP_BIND,                // 56: 绑定
    IORING_OP_LISTEN,              // 57: 监听
    IORING_OP_RECV_ZC,             // 58: 零复制接收
    IORING_OP_EPOLL_WAIT,          // 59: epoll 等待
    IORING_OP_READV_FIXED,         // 60: 固定矢量读
    IORING_OP_WRITEV_FIXED,        // 61: 固定矢量写
    IORING_OP_PIPE,                // 62: 创建管道
    IORING_OP_NOP128,              // 63: 128字节 NOP
    IORING_OP_URING_CMD128,        // 64: 128字节 uring 命令
    IORING_OP_LAST,                // 65: 操作码数量
};
```

---

## 核心数据结构

### struct io_uring_sqe (include/uapi/linux/io_uring.h:30-118)

Submission Queue Entry (提交队列条目),用户空间提交请求的主要数据结构:

```c
struct io_uring_sqe {
    __u8    opcode;      /* 操作码类型 */
    __u8    flags;      /* IOSQE_ 标志 */
    __u16   ioprio;     /* 请求优先级 */
    __s32   fd;         /* 文件描述符 */
    union {
        __u64 off;      /* 文件偏移 */
        __u64 addr2;
        struct { __u32 cmd_op; __u32 __pad1; };
    };
    union {
        __u64 addr;     /* 缓冲区指针或 iovecs */
        __u64 splice_off_in;
        struct { __u32 level; __u32 optname; };
    };
    __u32   len;        /* 缓冲区大小或 iovec 数量 */
    union { ... };      /* 各种操作特定的标志 */
    __u64   user_data;  /* 完成时回传的数据 */
    union { __u16 buf_index; __u16 buf_group; };
    __u16   personality;
    union { ... };      /* splice_fd_in, file_index 等 */
    union { ... };      /* addr3, attr_ptr 等 */
};
```

### struct io_issue_def (io_uring/opdef.h:7-44)

定义操作的执行属性:

```c
struct io_issue_def {
    unsigned needs_file : 1;       /* 需要 req->file 已分配 */
    unsigned plug : 1;             /* 应该阻塞 plug */
    unsigned ioprio : 1;           /* 支持 ioprio */
    unsigned iopoll : 1;           /* 支持 iopoll */
    unsigned buffer_select : 1;    /* 支持缓冲区选择 */
    unsigned hash_reg_file : 1;    /* 普通文件哈希工作队列插入 */
    unsigned unbound_nonreg_file : 1; /* 非普通文件无限工作队列 */
    unsigned pollin : 1;           /* 支持轮询读 */
    unsigned pollout : 1;          /* 支持轮询写 */
    unsigned poll_exclusive : 1;   /* 轮询互斥 */
    unsigned audit_skip : 1;       /* 跳过审计 */
    unsigned iopoll_queue : 1;     /* 必须放入 iopoll 列表 */
    unsigned vectored : 1;         /* 矢量操作码 */
    unsigned is_128 : 1;           /* 128字节 SQE */
    unsigned short async_size;      /* 异步数据大小 */
    unsigned short filter_pdu_size; /* BPF 过滤 PDU 大小 */
    int (*issue)(struct io_kiocb *, unsigned int);  /* 执行函数 */
    int (*prep)(struct io_kiocb *, const struct io_uring_sqe *); /* 准备函数 */
    void (*filter_populate)(struct io_uring_bpf_ctx *, struct io_kiocb *);
};
```

### struct io_cold_def (io_uring/opdef.h:46-52)

定义操作的冷路径属性(清理和失败处理):

```c
struct io_cold_def {
    const char *name;              /* 操作名称 */
    void (*sqe_copy)(struct io_kiocb *);
    void (*cleanup)(struct io_kiocb *);  /* 清理函数 */
    void (*fail)(struct io_kiocb *);     /* 失败处理函数 */
};
```

### struct io_kiocb (include/linux/io_uring_types.h:688+)

io_uring 的请求控制块,嵌入了具体操作的数据结构:

```c
struct io_kiocb {
    struct file *file;             /* 关联的文件 */
    u8 opcode;                     /* 操作码 */
    u8 issue_flags;                /* 发行标志 */
    struct io_ring_ctx *ctx;       /* 环形缓冲区上下文 */
    struct io_kiocb *link;         /* 链接的请求 */
    struct list_head comp_list;     /* 完成列表 */
    union { ... };                  /* cmd 数据,嵌入操作特定结构 */
    __u64 user_data;               /* 用户数据 */
    struct io_uring_cqe cqe;       /* 完成队列条目 */
    unsigned int flags;            /* 请求标志 */
    __u16 buf_index;               /* 缓冲区索引 */
    struct async_poll *apoll;      /* 异步轮询数据 */
    void *async_data;              /* 异步操作数据 */
    struct io_tw_req io_task_work; /* 任务工作 */
    /* ... 其他字段 */
};
```

---

## 操作码映射表

### io_issue_defs 数组 (io_uring/opdef.c:54-602)

操作码到处理函数的映射数组,每个条目包含:

1. **prep 函数**: 准备阶段,从 SQE 提取参数
2. **issue 函数**: 执行阶段,实际执行操作

#### 读操作相关条目

```c
// opdef.c:61-75
[IORING_OP_READV] = {
    .needs_file        = 1,
    .unbound_nonreg_file = 1,
    .pollin            = 1,
    .buffer_select     = 1,
    .plug              = 1,
    .audit_skip        = 1,
    .ioprio            = 1,
    .iopoll            = 1,
    .iopoll_queue      = 1,
    .vectored          = 1,
    .async_size        = sizeof(struct io_async_rw),
    .prep              = io_prep_readv,
    .issue             = io_read,
},
```

#### 写操作相关条目

```c
// opdef.c:76-90
[IORING_OP_WRITEV] = {
    .needs_file        = 1,
    .hash_reg_file     = 1,
    .unbound_nonreg_file = 1,
    .pollout           = 1,
    .plug              = 1,
    .audit_skip        = 1,
    .ioprio            = 1,
    .iopoll            = 1,
    .iopoll_queue      = 1,
    .vectored          = 1,
    .async_size        = sizeof(struct io_async_rw),
    .prep              = io_prep_writev,
    .issue             = io_write,
},
```

### io_cold_defs 数组 (io_uring/opdef.c:604-860)

操作码到名称和清理函数的映射:

```c
// opdef.c:608-612
[IORING_OP_READV] = {
    .name      = "READV",
    .cleanup   = io_readv_writev_cleanup,
    .fail      = io_rw_fail,
},
```

### io_uring_get_opcode() 函数 (io_uring/opdef.c:862-867)

根据操作码获取操作名称:

```c
const char *io_uring_get_opcode(u8 opcode)
{
    if (opcode < IORING_OP_LAST)
        return io_cold_defs[opcode].name;
    return "INVALID";
}
```

### io_uring_op_supported() 函数 (io_uring/opdef.c:869-875)

检查操作码是否支持:

```c
bool io_uring_op_supported(u8 opcode)
{
    if (opcode < IORING_OP_LAST &&
        io_issue_defs[opcode].prep != io_eopnotsupp_prep)
        return true;
    return false;
}
```

### io_uring_optable_init() 函数 (io_uring/opdef.c:877-890)

初始化操作码表,验证所有操作码都已正确定义:

```c
void __init io_uring_optable_init(void)
{
    int i;

    BUILD_BUG_ON(ARRAY_SIZE(io_cold_defs) != IORING_OP_LAST);
    BUILD_BUG_ON(ARRAY_SIZE(io_issue_defs) != IORING_OP_LAST);

    for (i = 0; i < ARRAY_SIZE(io_issue_defs); i++) {
        BUG_ON(!io_issue_defs[i].prep);
        if (io_issue_defs[i].prep != io_eopnotsupp_prep)
            BUG_ON(!io_issue_defs[i].issue);
        WARN_ON_ONCE(!io_cold_defs[i].name);
    }
}
```

---

## NOP 操作

### io_nop 结构体 (io_uring/nop.c:14-22)

```c
struct io_nop {
    struct file *file;             /* NOTE: kiocb has file as first member */
    int result;                     /* 结果 */
    int fd;                         /* 文件描述符 */
    unsigned int flags;             /* NOP 标志 */
    __u64 extra1;                  /* 额外数据1 (CQE32) */
    __u64 extra2;                  /* 额外数据2 (CQE32) */
};
```

### NOP 标志 (io_uring/nop.c:24-26)

```c
#define NOP_FLAGS (IORING_NOP_INJECT_RESULT | IORING_NOP_FIXED_FILE | \
                   IORING_NOP_FIXED_BUFFER | IORING_NOP_FILE | \
                   IORING_NOP_TW | IORING_NOP_CQE32)
```

| 标志 | 功能 |
|------|------|
| `IORING_NOP_INJECT_RESULT` | 注入 SQE 中的结果 |
| `IORING_NOP_FIXED_FILE` | 使用固定文件 |
| `IORING_NOP_FIXED_BUFFER` | 使用固定缓冲区 |
| `IORING_NOP_FILE` | 使用文件描述符 |
| `IORING_NOP_TW` | 使用任务工作 |
| `IORING_NOP_CQE32` | 使用 32 字节 CQE |

### io_nop_prep() 准备函数 (io_uring/nop.c:28-55)

从 SQE 提取参数:

```c
int io_nop_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    struct io_nop *nop = io_kiocb_to_cmd(req, struct io_nop);

    nop->flags = READ_ONCE(sqe->nop_flags);
    if (nop->flags & ~NOP_FLAGS)
        return -EINVAL;

    if (nop->flags & IORING_NOP_INJECT_RESULT)
        nop->result = READ_ONCE(sqe->len);
    else
        nop->result = 0;
    // ... 处理其他标志
    return 0;
}
```

### io_nop() 执行函数 (io_uring/nop.c:57-91)

执行 NOP 操作:

```c
int io_nop(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_nop *nop = io_kiocb_to_cmd(req, struct io_nop);
    int ret = nop->result;

    // 处理文件标志
    if (nop->flags & IORING_NOP_FILE) {
        if (nop->flags & IORING_NOP_FIXED_FILE) {
            req->file = io_file_get_fixed(req, nop->fd, issue_flags);
            req->flags |= REQ_F_FIXED_FILE;
        } else {
            req->file = io_file_get_normal(req, nop->fd);
        }
        if (!req->file) {
            ret = -EBADF;
            goto done;
        }
    }
    // 处理固定缓冲区
    if (nop->flags & IORING_NOP_FIXED_BUFFER) {
        if (!io_find_buf_node(req, issue_flags))
            ret = -EFAULT;
    }
done:
    if (ret < 0)
        req_set_fail(req);
    // 设置结果
    if (nop->flags & IORING_NOP_CQE32)
        io_req_set_res32(req, nop->result, 0, nop->extra1, nop->extra2);
    else
        io_req_set_res(req, nop->result, 0);
    // 处理任务工作
    if (nop->flags & IORING_NOP_TW) {
        req->io_task_work.func = io_req_task_complete;
        io_req_task_work_add(req);
        return IOU_ISSUE_SKIP_COMPLETE;
    }
    return IOU_COMPLETE;
}
```

---

## 读写操作

### io_rw 结构体 (io_uring/rw.c:30-36)

```c
struct io_rw {
    struct kiocb kiocb;            /* 内嵌的 kiocb */
    u64 addr;                      /* 缓冲区地址 */
    u32 len;                       /* 缓冲区长度 */
    rwf_t flags;                   /* 读/写标志 */
};
```

### 读操作流程

#### io_prep_read() 准备函数 (io_uring/rw.c:335-338)

```c
int io_prep_read(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    return io_prep_rw(req, sqe, ITER_DEST);  // ITER_DEST = 读操作
}
```

#### io_prep_rw() 通用准备函数 (io_uring/rw.c:323-333)

```c
static int io_prep_rw(struct io_kiocb *req, const struct io_uring_sqe *sqe, int ddir)
{
    int ret;
    ret = __io_prep_rw(req, sqe, ddir);      // 提取参数
    if (unlikely(ret))
        return ret;
    return io_rw_do_import(req, ddir);        // 导入缓冲区
}
```

#### __io_prep_rw() 核心准备函数 (io_uring/rw.c:259-311)

```c
static int __io_prep_rw(struct io_kiocb *req, const struct io_uring_sqe *sqe, int ddir)
{
    struct io_rw *rw = io_kiocb_to_cmd(req, struct io_rw);
    struct io_async_rw *io;
    // 分配异步数据
    if (io_rw_alloc_async(req))
        return -ENOMEM;
    io = req->async_data;

    rw->kiocb.ki_pos = READ_ONCE(sqe->off);  // 文件偏移
    req->buf_index = READ_ONCE(sqe->buf_index);
    io->buf_group = req->buf_index;

    // 处理优先级
    ioprio = READ_ONCE(sqe->ioprio);
    if (ioprio) {
        ret = ioprio_check_cap(ioprio);
        if (ret) return ret;
        rw->kiocb.ki_ioprio = ioprio;
    } else {
        rw->kiocb.ki_ioprio = get_current_ioprio();
    }

    // 设置完成回调
    if (req->ctx->flags & IORING_SETUP_IOPOLL)
        rw->kiocb.ki_complete = io_complete_rw_iopoll;
    else
        rw->kiocb.ki_complete = io_complete_rw;

    rw->addr = READ_ONCE(sqe->addr);
    rw->len = READ_ONCE(sqe->len);
    rw->flags = (__force rwf_t) READ_ONCE(sqe->rw_flags);

    // 处理属性 (如 PI)
    attr_type_mask = READ_ONCE(sqe->attr_type_mask);
    if (attr_type_mask) {
        if (attr_type_mask != IORING_RW_ATTR_FLAG_PI)
            return -EINVAL;
        return io_prep_rw_pi(req, rw, ddir, attr_ptr, attr_type_mask);
    }
    return 0;
}
```

#### io_read() 执行函数 (io_uring/rw.c:1026-1038)

```c
int io_read(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_br_sel sel = { };
    int ret;

    ret = __io_read(req, &sel, issue_flags);
    if (ret >= 0)
        return kiocb_done(req, ret, &sel, issue_flags);

    if (req->flags & REQ_F_BUFFERS_COMMIT)
        io_kbuf_recycle(req, sel.buf_list, issue_flags);
    return ret;
}
```

#### __io_read() 核心读取逻辑 (io_uring/rw.c:911-1024)

```c
static int __io_read(struct io_kiocb *req, struct io_br_sel *sel,
                     unsigned int issue_flags)
{
    bool force_nonblock = issue_flags & IO_URING_F_NONBLOCK;
    struct io_rw *rw = io_kiocb_to_cmd(req, struct io_rw);
    struct io_async_rw *io = req->async_data;
    struct kiocb *kiocb = &rw->kiocb;
    ssize_t ret;

    // 1. 导入缓冲区
    if (req->flags & REQ_F_IMPORT_BUFFER) {
        ret = io_rw_import_reg_vec(req, io, ITER_DEST, issue_flags);
        if (unlikely(ret)) return ret;
    } else if (io_do_buffer_select(req)) {
        ret = io_import_rw_buffer(ITER_DEST, req, io, sel, issue_flags);
        if (unlikely(ret < 0)) return ret;
    }

    // 2. 初始化文件
    ret = io_rw_init_file(req, FMODE_READ, READ);
    if (unlikely(ret)) return ret;
    req->cqe.res = iov_iter_count(&io->iter);

    // 3. 设置非阻塞标志
    if (force_nonblock) {
        if (!io_file_supports_nowait(req, EPOLLIN))
            return -EAGAIN;
        kiocb->ki_flags |= IOCB_NOWAIT;
    } else {
        kiocb->ki_flags &= ~IOCB_NOWAIT;
    }

    // 4. 验证区域
    ppos = io_kiocb_update_pos(req);
    ret = rw_verify_area(READ, req->file, ppos, req->cqe.res);
    if (unlikely(ret)) return ret;

    // 5. 执行读操作
    ret = io_iter_do_read(rw, &io->iter);

    // 6. 处理重试
    if (ret == -EAGAIN) {
        if (io_file_can_poll(req)) return -EAGAIN;
        if (!force_nonblock && ...) goto done;
        if (req->flags & REQ_F_NOWAIT) goto done;
        ret = 0;
    } else if (ret == -EIOCBQUEUED) {
        return IOU_ISSUE_SKIP_COMPLETE;
    }
    // ... 处理部分读和重试逻辑
done:
    return ret;
}
```

### 写操作流程

#### io_prep_write() 准备函数 (io_uring/rw.c:340-343)

```c
int io_prep_write(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    return io_prep_rw(req, sqe, ITER_SOURCE);  // ITER_SOURCE = 写操作
}
```

#### io_write() 执行函数 (io_uring/rw.c:1126-1220)

```c
int io_write(struct io_kiocb *req, unsigned int issue_flags)
{
    bool force_nonblock = issue_flags & IO_URING_F_NONBLOCK;
    struct io_rw *rw = io_kiocb_to_cmd(req, struct io_rw);
    struct io_async_rw *io = req->async_data;
    struct kiocb *kiocb = &rw->kiocb;
    ssize_t ret, ret2;
    loff_t *ppos;

    // 1. 导入缓冲区
    if (req->flags & REQ_F_IMPORT_BUFFER) {
        ret = io_rw_import_reg_vec(req, io, ITER_SOURCE, issue_flags);
        if (unlikely(ret)) return ret;
    }

    // 2. 初始化文件
    ret = io_rw_init_file(req, FMODE_WRITE, WRITE);
    if (unlikely(ret)) return ret;
    req->cqe.res = iov_iter_count(&io->iter);

    // 3. 设置非阻塞和写标志
    if (force_nonblock) {
        if (!io_file_supports_nowait(req, EPOLLOUT))
            goto ret_eagain;
        kiocb->ki_flags |= IOCB_NOWAIT;
    } else {
        kiocb->ki_flags &= ~IOCB_NOWAIT;
    }

    ppos = io_kiocb_update_pos(req);
    ret = rw_verify_area(WRITE, req->file, ppos, req->cqe.res);
    if (unlikely(ret)) return ret;

    // 4. 开始写操作
    if (!io_kiocb_start_write(req, kiocb))
        return -EAGAIN;
    kiocb->ki_flags |= IOCB_WRITE;

    // 5. 执行写操作
    if (likely(req->file->f_op->write_iter))
        ret2 = req->file->f_op->write_iter(kiocb, &io->iter);
    else if (req->file->f_op->write)
        ret2 = loop_rw_iter(WRITE, rw, &io->iter);
    else
        ret2 = -EINVAL;

    // 6. 处理完成
    return kiocb_done(req, ret2, NULL, issue_flags);
}
```

### 矢量读写 (readv/writev)

#### io_prep_readv() (io_uring/rw.c:363-366)

```c
int io_prep_readv(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    return io_prep_rwv(req, sqe, ITER_DEST);
}
```

#### io_prep_rwv() (io_uring/rw.c:345-361)

```c
static int io_prep_rwv(struct io_kiocb *req, const struct io_uring_sqe *sqe, int ddir)
{
    int ret;
    ret = io_prep_rw(req, sqe, ddir);
    if (unlikely(ret)) return ret;
    if (!(req->flags & REQ_F_BUFFER_SELECT))
        return 0;
    return io_iov_buffer_select_prep(req);
}
```

### 固定缓冲区读写 (READ_FIXED/WRITE_FIXED)

#### io_init_rw_fixed() (io_uring/rw.c:373-387)

```c
static int io_init_rw_fixed(struct io_kiocb *req, unsigned int issue_flags, int ddir)
{
    struct io_rw *rw = io_kiocb_to_cmd(req, struct io_rw);
    struct io_async_rw *io = req->async_data;
    int ret;

    if (io->bytes_done) return 0;

    ret = io_import_reg_buf(req, &io->iter, rw->addr, rw->len, ddir, issue_flags);
    iov_iter_save_state(&io->iter, &io->iter_state);
    return ret;
}
```

### 多重射击读 (READ_MULTISHOT)

#### io_read_mshot_prep() (io_uring/rw.c:450-468)

```c
int io_read_mshot_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    struct io_rw *rw = io_kiocb_to_cmd(req, struct io_rw);
    int ret;

    if (!(req->flags & REQ_F_BUFFER_SELECT))
        return -EINVAL;

    ret = __io_prep_rw(req, sqe, ITER_DEST);
    if (unlikely(ret)) return ret;

    if (rw->addr || rw->len) return -EINVAL;

    req->flags |= REQ_F_APOLL_MULTISHOT;
    return 0;
}
```

---

## 文件系统操作

### fs.c 操作码映射

```c
// opdef.c:223-228
[IORING_OP_OPENAT] = {
    .filter_pdu_size = sizeof_field(struct io_uring_bpf_ctx, open),
    .prep    = io_openat_prep,
    .issue    = io_openat,
    .filter_populate = io_openat_bpf_populate,
},

// opdef.c:229-232
[IORING_OP_CLOSE] = {
    .prep    = io_close_prep,
    .issue    = io_close,
},

// opdef.c:239-243
[IORING_OP_STATX] = {
    .audit_skip = 1,
    .prep    = io_statx_prep,
    .issue    = io_statx,
},
```

### OPENAT 操作

#### io_openat_prep() (fs.c 中定义,引用在 opdef.c)

```c
// 准备函数签名
int io_openat_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe);
int io_openat(struct io_kiocb *req, unsigned int issue_flags);
```

### CLOSE 操作

```c
// opdef.c:229-232
[IORING_OP_CLOSE] = {
    .prep    = io_close_prep,
    .issue    = io_close,
},
```

### STATX 操作

```c
// opdef.c:239-243
[IORING_OP_STATX] = {
    .audit_skip = 1,
    .prep    = io_statx_prep,
    .issue    = io_statx,
},
```

### 文件系统操作结构体 (io_uring/fs.c)

```c
struct io_rename {
    struct file *file;
    int old_dfd;
    int new_dfd;
    struct delayed_filename oldpath;
    struct delayed_filename newpath;
    int flags;
};

struct io_unlink {
    struct file *file;
    int dfd;
    int flags;
    struct delayed_filename filename;
};

struct io_mkdir {
    struct file *file;
    int dfd;
    umode_t mode;
    struct delayed_filename filename;
};

struct io_link {
    struct file *file;
    int old_dfd;
    int new_dfd;
    struct delayed_filename oldpath;
    struct delayed_filename newpath;
    int flags;
};
```

### io_renameat_prep() 示例 (io_uring/fs.c:50-80)

```c
int io_renameat_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    struct io_rename *ren = io_kiocb_to_cmd(req, struct io_rename);
    const char __user *oldf, *newf;
    int err;

    if (sqe->buf_index || sqe->splice_fd_in)
        return -EINVAL;
    if (unlikely(req->flags & REQ_F_FIXED_FILE))
        return -EBADF;

    ren->old_dfd = READ_ONCE(sqe->fd);
    oldf = u64_to_user_ptr(READ_ONCE(sqe->addr));
    newf = u64_to_user_ptr(READ_ONCE(sqe->addr2));
    ren->new_dfd = READ_ONCE(sqe->len);
    ren->flags = READ_ONCE(sqe->rename_flags);

    err = delayed_getname(&ren->oldpath, oldf);
    if (unlikely(err)) return err;

    err = delayed_getname(&ren->newpath, newf);
    if (unlikely(err)) {
        dismiss_delayed_filename(&ren->oldpath);
        return err;
    }

    req->flags |= REQ_F_NEED_CLEANUP;
    req->flags |= REQ_F_FORCE_ASYNC;
    return 0;
}
```

---

## 网络操作

### net.c 操作码映射

```c
// opdef.c:142-154
[IORING_OP_SENDMSG] = {
    .needs_file = 1,
    .unbound_nonreg_file = 1,
    .pollout = 1,
    .ioprio = 1,
#if defined(CONFIG_NET)
    .async_size = sizeof(struct io_async_msghdr),
    .prep = io_sendmsg_prep,
    .issue = io_sendmsg,
#else
    .prep = io_eopnotsupp_prep,
#endif
},

// opdef.c:155-168
[IORING_OP_RECVMSG] = {
    .needs_file = 1,
    .unbound_nonreg_file = 1,
    .pollin = 1,
    .buffer_select = 1,
    .ioprio = 1,
#if defined(CONFIG_NET)
    .async_size = sizeof(struct io_async_msghdr),
    .prep = io_recvmsg_prep,
    .issue = io_recvmsg,
#else
    .prep = io_eopnotsupp_prep,
#endif
},

// opdef.c:181-193
[IORING_OP_ACCEPT] = {
    .needs_file = 1,
    .unbound_nonreg_file = 1,
    .pollin = 1,
    .poll_exclusive = 1,
    .ioprio = 1,
#if defined(CONFIG_NET)
    .prep = io_accept_prep,
    .issue = io_accept,
#else
    .prep = io_eopnotsupp_prep,
#endif
},

// opdef.c:205-216
[IORING_OP_CONNECT] = {
    .needs_file = 1,
    .unbound_nonreg_file = 1,
    .pollout = 1,
#if defined(CONFIG_NET)
    .async_size = sizeof(struct io_async_msghdr),
    .prep = io_connect_prep,
    .issue = io_connect,
#else
    .prep = io_eopnotsupp_prep,
#endif
},
```

### 网络操作结构体 (io_uring/net.c)

```c
struct io_shutdown {
    struct file *file;
    int how;
};

struct io_accept {
    struct file *file;
    struct sockaddr __user *addr;
    int __user *addr_len;
    int flags;
    int iou_flags;
    u32 file_slot;
    unsigned long nofile;
};

struct io_socket {
    struct file *file;
    int domain;
    int type;
    int protocol;
    int flags;
    u32 file_slot;
    unsigned long nofile;
};

struct io_connect {
    struct file *file;
    struct sockaddr __user *addr;
    int addr_len;
    bool in_progress;
    bool seen_econnaborted;
};

struct io_sr_msg {
    struct file *file;
    union {
        struct compat_msghdr __user *umsg_compat;
        struct user_msghdr __user *umsg;
        void __user *buf;
    };
    int len;
    unsigned done_io;
    unsigned msg_flags;
    unsigned nr_multishot_loops;
    u16 flags;
    u16 buf_group;
    unsigned mshot_len;
    unsigned mshot_total_len;
    void __user *msg_control;
    struct io_kiocb *notif;
};
```

### ACCEPT 操作

#### io_accept_prep() (io_uring/net.c:1615-1647)

```c
int io_accept_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    struct io_accept *accept = io_kiocb_to_cmd(req, struct io_accept);

    if (sqe->len || sqe->buf_index)
        return -EINVAL;

    accept->addr = u64_to_user_ptr(READ_ONCE(sqe->addr));
    accept->addr_len = u64_to_user_ptr(READ_ONCE(sqe->addr2));
    accept->flags = READ_ONCE(sqe->accept_flags);
    accept->nofile = rlimit(RLIMIT_NOFILE);
    accept->iou_flags = READ_ONCE(sqe->ioprio);
    if (accept->iou_flags & ~ACCEPT_FLAGS)
        return -EINVAL;

    accept->file_slot = READ_ONCE(sqe->file_index);
    if (accept->file_slot) {
        if (accept->flags & SOCK_CLOEXEC)
            return -EINVAL;
        if (accept->iou_flags & IORING_ACCEPT_MULTISHOT &&
            accept->file_slot != IORING_FILE_INDEX_ALLOC)
            return -EINVAL;
    }
    // ... 更多标志检查
    if (accept->iou_flags & IORING_ACCEPT_MULTISHOT)
        req->flags |= REQ_F_APOLL_MULTISHOT;
    if (accept->iou_flags & IORING_ACCEPT_DONTWAIT)
        req->flags |= REQ_F_NOWAIT;
    return 0;
}
```

#### io_accept() (io_uring/net.c:1649-1708)

```c
int io_accept(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_accept *accept = io_kiocb_to_cmd(req, struct io_accept);
    bool force_nonblock = issue_flags & IO_URING_F_NONBLOCK;
    bool fixed = !!accept->file_slot;
    struct proto_accept_arg arg = {
        .flags = force_nonblock ? O_NONBLOCK : 0,
    };
    struct file *file;
    unsigned cflags;
    int ret, fd;

    if (!(req->flags & REQ_F_POLLED) &&
        accept->iou_flags & IORING_ACCEPT_POLL_FIRST)
        return -EAGAIN;

retry:
    if (!fixed) {
        fd = __get_unused_fd_flags(accept->flags, accept->nofile);
        if (unlikely(fd < 0)) return fd;
    }
    arg.err = 0;
    arg.is_empty = -1;
    file = do_accept(req->file, &arg, accept->addr, accept->addr_len,
                     accept->flags);
    if (IS_ERR(file)) {
        if (!fixed) put_unused_fd(fd);
        ret = PTR_ERR(file);
        if (ret == -EAGAIN && force_nonblock &&
            !(accept->iou_flags & IORING_ACCEPT_DONTWAIT))
            return IOU_RETRY;
        if (ret == -ERESTARTSYS) ret = -EINTR;
    } else if (!fixed) {
        fd_install(fd, file);
        ret = fd;
    } else {
        ret = io_fixed_fd_install(req, issue_flags, file, accept->file_slot);
    }

    cflags = 0;
    if (!arg.is_empty) cflags |= IORING_CQE_F_SOCK_NONEMPTY;

    if (ret >= 0 && (req->flags & REQ_F_APOLL_MULTISHOT) &&
        io_req_post_cqe(req, ret, cflags | IORING_CQE_F_MORE)) {
        if (cflags & IORING_CQE_F_SOCK_NONEMPTY || arg.is_empty == -1)
            goto retry;
        return IOU_RETRY;
    }

    io_req_set_res(req, ret, cflags);
    if (ret < 0) req_set_fail(req);
    return IOU_COMPLETE;
}
```

### CONNECT 操作

#### io_connect_prep() (io_uring/net.c:1773-1790)

```c
int io_connect_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    struct io_connect *conn = io_kiocb_to_cmd(req, struct io_connect);
    struct io_async_msghdr *io;

    if (sqe->len || sqe->buf_index || sqe->rw_flags || sqe->splice_fd_in)
        return -EINVAL;

    conn->addr = u64_to_user_ptr(READ_ONCE(sqe->addr));
    conn->addr_len = READ_ONCE(sqe->addr2);
    conn->in_progress = conn->seen_econnaborted = false;

    io = io_msg_alloc_async(req);
    if (unlikely(!io)) return -ENOMEM;

    return move_addr_to_kernel(conn->addr, conn->addr_len, &io->addr);
}
```

#### io_connect() (io_uring/net.c:1792-1842)

```c
int io_connect(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_connect *connect = io_kiocb_to_cmd(req, struct io_connect);
    struct io_async_msghdr *io = req->async_data;
    unsigned file_flags;
    int ret;
    bool force_nonblock = issue_flags & IO_URING_F_NONBLOCK;

    if (connect->in_progress) {
        struct poll_table_struct pt = { ._key = EPOLLERR };
        if (vfs_poll(req->file, &pt) & EPOLLERR)
            goto get_sock_err;
    }

    file_flags = force_nonblock ? O_NONBLOCK : 0;
    ret = __sys_connect_file(req->file, &io->addr, connect->addr_len, file_flags);

    if ((ret == -EAGAIN || ret == -EINPROGRESS || ret == -ECONNABORTED)
        && force_nonblock) {
        if (ret == -EINPROGRESS)
            connect->in_progress = true;
        else if (ret == -ECONNABORTED) {
            if (connect->seen_econnaborted) goto out;
            connect->seen_econnaborted = true;
        }
        return -EAGAIN;
    }
    if (connect->in_progress) {
        if (ret == -EBADFD || ret == -EISCONN) {
get_sock_err:
            ret = sock_error(sock_from_file(req->file)->sk);
        }
    }
    if (ret == -ERESTARTSYS) ret = -EINTR;
out:
    if (ret < 0) req_set_fail(req);
    io_req_msg_cleanup(req, issue_flags);
    io_req_set_res(req, ret, 0);
    return IOU_COMPLETE;
}
```

### SEND/RECV 操作

#### io_sendmsg_prep() (io_uring/net.c:418-451)

```c
int io_sendmsg_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    struct io_sr_msg *sr = io_kiocb_to_cmd(req, struct io_sr_msg);

    sr->done_io = 0;
    sr->len = READ_ONCE(sqe->len);
    if (unlikely(sr->len < 0)) return -EINVAL;
    sr->flags = READ_ONCE(sqe->ioprio);
    if (sr->flags & ~SENDMSG_FLAGS) return -EINVAL;
    sr->msg_flags = READ_ONCE(sqe->msg_flags) | MSG_NOSIGNAL;
    if (sr->msg_flags & MSG_DONTWAIT) req->flags |= REQ_F_NOWAIT;
    if (req->flags & REQ_F_BUFFER_SELECT) sr->buf_group = req->buf_index;
    if (sr->flags & IORING_RECVSEND_BUNDLE) {
        if (req->opcode == IORING_OP_SENDMSG) return -EINVAL;
        sr->msg_flags |= MSG_WAITALL;
        req->flags |= REQ_F_MULTISHOT;
    }
    if (io_is_compat(req->ctx)) sr->msg_flags |= MSG_CMSG_COMPAT;

    if (unlikely(!io_msg_alloc_async(req))) return -ENOMEM;
    if (req->opcode != IORING_OP_SENDMSG) return io_send_setup(req, sqe);
    if (unlikely(sqe->addr2 || sqe->file_index)) return -EINVAL;
    return io_sendmsg_setup(req, sqe);
}
```

#### io_sendmsg() (io_uring/net.c:545-592)

```c
int io_sendmsg(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_sr_msg *sr = io_kiocb_to_cmd(req, struct io_sr_msg);
    struct io_async_msghdr *kmsg = req->async_data;
    struct socket *sock;
    unsigned flags;
    int min_ret = 0;
    int ret;

    sock = sock_from_file(req->file);
    if (unlikely(!sock)) return -ENOTSOCK;

    if (!(req->flags & REQ_F_POLLED) && (sr->flags & IORING_RECVSEND_POLL_FIRST))
        return -EAGAIN;

    flags = sr->msg_flags;
    if (issue_flags & IO_URING_F_NONBLOCK) flags |= MSG_DONTWAIT;
    if (flags & MSG_WAITALL)
        min_ret = iov_iter_count(&kmsg->msg.msg_iter);

    kmsg->msg.msg_control_user = sr->msg_control;
    ret = __sys_sendmsg_sock(sock, &kmsg->msg, flags);

    if (ret < min_ret) {
        if (ret == -EAGAIN && (issue_flags & IO_URING_F_NONBLOCK)) return -EAGAIN;
        if (ret > 0 && io_net_retry(sock, flags)) {
            kmsg->msg.msg_controllen = 0;
            kmsg->msg.msg_control = NULL;
            sr->done_io += ret;
            return -EAGAIN;
        }
        if (ret == -ERESTARTSYS) ret = -EINTR;
        req_set_fail(req);
    }
    io_req_msg_cleanup(req, issue_flags);
    if (ret >= 0) ret += sr->done_io;
    else if (sr->done_io) ret = sr->done_io;
    io_req_set_res(req, ret, 0);
    return IOU_COMPLETE;
}
```

---

## Poll 操作

### poll.c 操作码映射

```c
// opdef.c:124-130
[IORING_OP_POLL_ADD] = {
    .needs_file = 1,
    .unbound_nonreg_file = 1,
    .audit_skip = 1,
    .prep = io_poll_add_prep,
    .issue = io_poll_add,
},

// opdef.c:131-135
[IORING_OP_POLL_REMOVE] = {
    .audit_skip = 1,
    .prep = io_poll_remove_prep,
    .issue = io_poll_remove,
},
```

### Poll 操作结构体 (io_uring/poll.c)

```c
struct io_poll_update {
    struct file *file;
    u64 old_user_data;
    u64 new_user_data;
    __poll_t events;
    bool update_events;
    bool update_user_data;
};

struct io_poll_table {
    struct poll_table_struct pt;
    struct io_kiocb *req;
    int nr_entries;
    int error;
    bool owning;
    __poll_t result_mask;
};
```

### io_poll_add_prep() (io_uring/poll.c:879-894)

```c
int io_poll_add_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    struct io_poll *poll = io_kiocb_to_cmd(req, struct io_poll);
    u32 flags;

    if (sqe->buf_index || sqe->off || sqe->addr)
        return -EINVAL;
    flags = READ_ONCE(sqe->len);
    if (flags & ~IORING_POLL_ADD_MULTI) return -EINVAL;
    if ((flags & IORING_POLL_ADD_MULTI) && (req->flags & REQ_F_CQE_SKIP))
        return -EINVAL;

    poll->events = io_poll_parse_events(sqe, flags);
    return 0;
}
```

### io_poll_add() (io_uring/poll.c:896-910)

```c
int io_poll_add(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_poll *poll = io_kiocb_to_cmd(req, struct io_poll);
    struct io_poll_table ipt;
    int ret;

    ipt.pt._qproc = io_poll_queue_proc;

    ret = __io_arm_poll_handler(req, poll, &ipt, poll->events, issue_flags);
    if (ret > 0) {
        io_req_set_res(req, ipt.result_mask, 0);
        return IOU_COMPLETE;
    }
    return ret ?: IOU_ISSUE_SKIP_COMPLETE;
}
```

### __io_arm_poll_handler() (io_uring/poll.c:548-631)

核心轮询处理函数:

```c
static int __io_arm_poll_handler(struct io_kiocb *req,
                                struct io_poll *poll,
                                struct io_poll_table *ipt,
                                __poll_t mask,
                                unsigned issue_flags)
{
    INIT_HLIST_NODE(&req->hash_node);
    io_init_poll_iocb(poll, mask);
    poll->file = req->file;
    req->apoll_events = poll->events;

    ipt->pt._key = mask;
    ipt->req = req;
    ipt->error = 0;
    ipt->nr_entries = 0;
    ipt->owning = issue_flags & IO_URING_F_UNLOCKED;
    atomic_set(&req->poll_refs, (int)ipt->owning);

    if (poll->events & EPOLLEXCLUSIVE)
        req->flags |= REQ_F_POLL_NO_LAZY;

    mask = vfs_poll(req->file, &ipt->pt) & poll->events;

    if (unlikely(ipt->error || !ipt->nr_entries)) {
        io_poll_remove_entries(req);
        if (!io_poll_can_finish_inline(req, ipt)) {
            io_poll_mark_cancelled(req);
            return 0;
        } else if (mask && (poll->events & EPOLLET)) {
            ipt->result_mask = mask;
            return 1;
        }
        return ipt->error ?: -EINVAL;
    }

    if (mask && ((poll->events & (EPOLLET|EPOLLONESHOT)) == (EPOLLET|EPOLLONESHOT))) {
        if (!io_poll_can_finish_inline(req, ipt)) {
            io_poll_add_hash(req, issue_flags);
            return 0;
        }
        io_poll_remove_entries(req);
        ipt->result_mask = mask;
        return 1;
    }

    io_poll_add_hash(req, issue_flags);

    if (mask && (poll->events & EPOLLET) && io_poll_can_finish_inline(req, ipt)) {
        __io_poll_execute(req, mask);
        return 0;
    }
    io_napi_add(req);

    if (ipt->owning) {
        if (atomic_cmpxchg(&req->poll_refs, 1, 0) != 1)
            __io_poll_execute(req, 0);
    }
    return 0;
}
```

### io_poll_remove() (io_uring/poll.c:912-968)

```c
int io_poll_remove(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_poll_update *poll_update = io_kiocb_to_cmd(req, struct io_poll_update);
    struct io_ring_ctx *ctx = req->ctx;
    struct io_cancel_data cd = { .ctx = ctx, .data = poll_update->old_user_data, };
    struct io_kiocb *preq;
    int ret2, ret = 0;

    io_ring_submit_lock(ctx, issue_flags);
    preq = io_poll_find(ctx, true, &cd);
    ret2 = io_poll_disarm(preq);
    if (ret2) { ret = ret2; goto out; }
    if (WARN_ON_ONCE(preq->opcode != IORING_OP_POLL_ADD)) { ret = -EFAULT; goto out; }

    if (poll_update->update_events || poll_update->update_user_data) {
        if (poll_update->update_events) {
            struct io_poll *poll = io_kiocb_to_cmd(preq, struct io_poll);
            poll->events &= ~0xffff;
            poll->events |= poll_update->events & 0xffff;
            poll->events |= IO_POLL_UNMASK;
        }
        if (poll_update->update_user_data)
            preq->cqe.user_data = poll_update->new_user_data;

        ret2 = io_poll_add(preq, issue_flags & ~IO_URING_F_UNLOCKED);
        if (ret2 == IOU_ISSUE_SKIP_COMPLETE) goto out;
        else if (ret2 == IOU_COMPLETE) goto complete;
    }

    io_req_set_res(preq, -ECANCELED, 0);
complete:
    if (preq->cqe.res < 0) req_set_fail(preq);
    preq->io_task_work.func = io_req_task_complete;
    io_req_task_work_add(preq);
out:
    io_ring_submit_unlock(ctx, issue_flags);
    if (ret < 0) { req_set_fail(req); return ret; }
    io_req_set_res(req, ret, 0);
    return IOU_COMPLETE;
}
```

---

## 操作执行流程

### 整体架构图

```
用户空间                              内核空间
+--------+                           +------------------+
|        |  io_uring_enter()        |                  |
|  SQE   | +---------------------> |  io_submit_sqes() |
|  Ring  |                           |                  |
+--------+                           +------------------+
                                          |
                                          v
                                 +------------------+
                                 |  获取空闲 req    |
                                 +------------------+
                                          |
                                          v
                                 +------------------+
                                 |  io_issue_defs   |
                                 |  [opcode].prep()  |
                                 +------------------+
                                          |
                                          v
                                 +------------------+
                                 |  文件/资源获取   |
                                 +------------------+
                                          |
                                          v
                                 +------------------+
                                 |  io_issue_defs   |
                                 |  [opcode].issue()|
                                 +------------------+
                                          |
                    +---------------------+---------------------+
                    |                     |                     |
                    v                     v                     v
           +----------------+    +----------------+    +----------------+
           | IOU_COMPLETE   |    |IOU_ISSUE_SKIP  |    | IOU_RETRY      |
           | 同步完成      |    |_COMPLETE       |    | 异步重试       |
           +----------------+    +----------------+    +----------------+
                    |                     |                     |
                    v                     v                     v
           +----------------------------------------------------+
           |              完成任务队列 (Task Work)               |
           +----------------------------------------------------+
                    |                     |                     |
                    v                     v                     v
           +----------------+    +----------------+    +----------------+
           | io_req_set_res |    | 放入 io-wq   |    | 放入轮询列表   |
           | 设置结果       |    | 异步执行      |    | 等待事件       |
           +----------------+    +----------------+    +----------------+
                                          |                     |
                                          v                     v
                                 +----------------+    +----------------+
                                 | io_wq_submit   |    |  事件触发     |
                                 | _work()        |    |  重新执行     |
                                 +----------------+    +----------------+
                                          |                     |
                                          +----------+----------+
                                                     |
                                                     v
                                            +----------------+
                                            |  CQE 写入 CQ  |
                                            +----------------+
                                                     |
                                                     v
                                            +----------------+
                                            |  用户空间读取 |
                                            +----------------+
```

### 操作执行返回值

| 返回值 | 含义 |
|--------|------|
| `IOU_COMPLETE` | 操作同步完成,CQE 已准备好 |
| `IOU_ISSUE_SKIP_COMPLETE` | 跳过立即完成,等待任务工作处理 |
| `IOU_RETRY` | 需要重试,操作被推迟 |
| `IOU_REQUEUE` | 请求重新排队 |
| 负值 | 错误码,操作失败 |

### io_submit_sqes() 函数

主要入口函数 (io_uring/io_uring.c):

```c
int io_submit_sqes(struct io_ring_ctx *ctx, unsigned int nr)
{
    // 提交多个 SQE
}
```

### 执行标志 (issue_flags)

```c
enum io_uring_cmd_flags {
    IO_URING_F_COMPLETE_DEFER = 1,   /* 延迟完成 */
    IO_URING_F_UNLOCKED = 2,          /* 解锁执行 */
    IO_URING_F_MULTISHOT = 4,         /* 多重射击 */
    IO_URING_F_IOWQ = 8,              /* io-wq 执行 */
    IO_URING_F_INLINE = 16,           /* 内联执行 */
};
```

### 异步操作处理

当 `issue()` 函数返回 `IOU_ISSUE_SKIP_COMPLETE` 时,请求会被:

1. **放入 io-wq 队列**: 通过 `io_req_queue_iowq()`
2. **放入任务工作队列**: 通过 `io_req_task_work_add()`
3. **放入轮询列表**: 对于 iopoll 操作

---

## 总结

io_uring 的操作码实现采用了两阶段处理模式:

1. **准备阶段 (prep)**: 从用户空间的 SQE 提取参数,进行初步验证
2. **执行阶段 (issue)**: 实际执行操作,处理同步/异步完成

每个操作码在 `io_issue_defs[]` 数组中有对应的条目,定义了:
- 是否需要文件描述符
- 是否支持轮询
- 异步数据大小
- prep 和 issue 函数指针

这种设计使得添加新的操作码变得简单,只需在数组中添加条目并实现对应的 prep/issue 函数即可。

---

**文档信息**

- 分析版本: Linux Kernel master 分支
- 源码路径: `/Users/sphinx/github/linux/io_uring/`
- 头文件路径: `/Users/sphinx/github/linux/include/uapi/linux/io_uring.h`
- 类型定义: `/Users/sphinx/github/linux/include/linux/io_uring_types.h`
