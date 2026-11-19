# Linux 内核 io_uring 子系统高级特性分析

## 目录

1. [概述](#概述)
2. [Eventfd 集成](#1-eventfd-集成)
3. [Epoll 集成](#2-epoll-集成)
4. [取消操作 (Cancel)](#3-取消操作-cancel)
5. [通知机制 (Notification)](#4-通知机制-notification)
6. [Futex 支持](#5-futex-支持)
7. [Timeout 操作](#6-timeout-操作)
8. [错误处理](#7-错误处理)
9. [总结](#总结)

---

## 概述

io_uring 是 Linux 内核的高性能异步 I/O 子系统，提供了统一的高效接口来执行 I/O 操作。本文档分析其高级功能，包括事件通知、取消机制、超时处理和 futex 支持等。

**源码位置:**
- Eventfd: `/Users/sphinx/github/linux/io_uring/eventfd.c`
- Epoll: `/Users/sphinx/github/linux/io_uring/epoll.c`
- Futex: `/Users/sphinx/github/linux/io_uring/futex.c`
- Cancel: `/Users/sphinx/github/linux/io_uring/cancel.c`
- Notification: `/Users/sphinx/github/linux/io_uring/notif.c`
- Timeout: `/Users/sphinx/github/linux/io_uring/timeout.c`

---

## 1. Eventfd 集成

### 1.1 核心数据结构

```c
// io_uring/epoll.c, 第14-22行
struct io_ev_fd {
    struct eventfd_ctx	*cq_ev_fd;      // eventfd 上下文
    unsigned int	eventfd_async;  // 异步标志
    unsigned		last_cq_tail;    // 上次 CQ 尾位置
    refcount_t		refs;           // 引用计数
    atomic_t		ops;            // 操作标志位
    struct rcu_head	rcu;
};
```

### 1.2 注册 Eventfd

**IORING_REGISTER_EVENTFD** 注册一个 eventfd 用于 CQ 完成通知:

```c
// io_uring/epoll.c, 第119-156行
int io_eventfd_register(struct io_ring_ctx *ctx, void __user *arg,
                        unsigned int eventfd_async)
{
    struct io_ev_fd *ev_fd;
    __s32 __user *fds = arg;
    int fd;

    // 检查是否已注册
    ev_fd = rcu_dereference_protected(ctx->io_ev_fd,
                    lockdep_is_held(&ctx->uring_lock));
    if (ev_fd)
        return -EBUSY;

    if (copy_from_user(&fd, fds, sizeof(*fds)))
        return -EFAULT;

    ev_fd = kmalloc_obj(*ev_fd);
    if (!ev_fd)
        return -ENOMEM;

    // 获取 eventfd 上下文
    ev_fd->cq_ev_fd = eventfd_ctx_fdget(fd);
    if (IS_ERR(ev_fd->cq_ev_fd)) {
        int ret = PTR_ERR(ev_fd->cq_ev_fd);
        kfree(ev_fd);
        return ret;
    }

    spin_lock(&ctx->completion_lock);
    ev_fd->last_cq_tail = ctx->cached_cq_tail;
    spin_unlock(&ctx->completion_lock);

    ev_fd->eventfd_async = eventfd_async;
    ctx->has_evfd = true;
    refcount_set(&ev_fd->refs, 1);
    atomic_set(&ev_fd->ops, 0);
    rcu_assign_pointer(ctx->io_ev_fd, ev_fd);
    return 0;
}
```

### 1.3 注销 Eventfd

**IORING_UNREGISTER_EVENTFD** 注销 eventfd:

```c
// io_uring/epoll.c, 第158-172行
int io_eventfd_unregister(struct io_ring_ctx *ctx)
{
    struct io_ev_fd *ev_fd;

    ev_fd = rcu_dereference_protected(ctx->io_ev_fd,
                    lockdep_is_held(&ctx->uring_lock));
    if (ev_fd) {
        ctx->has_evfd = false;
        rcu_assign_pointer(ctx->io_ev_fd, NULL);
        io_eventfd_put(ev_fd);  // 延迟释放
        return 0;
    }

    return -ENXIO;
}
```

### 1.4 Eventfd 信号机制

#### 信号触发逻辑

```c
// io_uring/epoll.c, 第75-117行
void io_eventfd_signal(struct io_ring_ctx *ctx, bool cqe_event)
{
    bool skip = false;
    struct io_ev_fd *ev_fd;
    struct io_rings *rings;

    rcu_read_lock();
    rings = rcu_dereference(ctx->rings_rcu);
    if (!rings)
        goto out;
    if (READ_ONCE(rings->cq_flags) & IORING_CQ_EVENTFD_DISABLED)
        goto out;
    ev_fd = rcu_dereference(ctx->io_ev_fd);
    if (!ev_fd)
        goto out;

    // 检查是否应该触发
    if (!io_eventfd_trigger(ev_fd) || !refcount_inc_not_zero(&ev_fd->refs))
        goto out;

    if (cqe_event) {
        // 避免重复信号
        spin_lock(&ctx->completion_lock);
        skip = ctx->cached_cq_tail == ev_fd->last_cq_tail;
        ev_fd->last_cq_tail = ctx->cached_cq_tail;
        spin_unlock(&ctx->completion_lock);
    }

    if (skip || __io_eventfd_signal(ev_fd))
        io_eventfd_put(ev_fd);
out:
    rcu_read_unlock();
}
```

#### 异步触发判断

```c
// io_uring/epoll.c, 第66-73行
/*
 * 触发条件: eventfd_async 未设置, 或者设置了但调用者是异步 worker
 */
static bool io_eventfd_trigger(struct io_ev_fd *ev_fd)
{
    return !ev_fd->eventfd_async || io_wq_current_is_worker();
}
```

#### 原子信号操作

```c
// io_uring/epoll.c, 第53-64行
static bool __io_eventfd_signal(struct io_ev_fd *ev_fd)
{
    if (eventfd_signal_allowed()) {
        eventfd_signal_mask(ev_fd->cq_ev_fd, EPOLL_URING_WAKE);
        return true;
    }
    // 信号被禁止, 使用原子操作延迟信号
    if (!atomic_fetch_or(BIT(IO_EVENTFD_OP_SIGNAL_BIT), &ev_fd->ops)) {
        call_rcu_hurry(&ev_fd->rcu, io_eventfd_do_signal);
        return false;
    }
    return true;
}
```

### 1.5 Wakeup 机制流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                     CQ Event 发布                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              io_eventfd_signal(ctx, true)                      │
│  - 检查 rings->cq_flags & IORING_CQ_EVENTFD_DISABLED            │
│  - 检查 eventfd_async 标志                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              __io_eventfd_signal()                              │
│  - eventfd_signal_allowed() 检查                               │
│    ├─ 允许: 直接 eventfd_signal_mask()                         │
│    └─ 禁止: 原子设置 BIT 并延迟调用 call_rcu()                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              eventfd_signal()                                  │
│  - 增加 eventfd 计数器                                           │
│  - 唤醒等待的 poll/select/epoll                                │
└─────────────────────────────────────────────────────────────────┘
```

### 1.6 IORING_REGISTER_EVENTFD_ASYNC

```c
// io_uring/epoll.c 中通过 eventfd_async 参数控制
// eventfd_async = 1: 允许异步 worker 触发 eventfd
// eventfd_async = 0: 只允许同步提交触发 eventfd
```

---

## 2. Epoll 集成

### 2.1 Epoll 控制操作 (IORING_OP_EPOLL_CTL)

```c
// io_uring/epoll.c, 第15-21行
struct io_epoll {
    struct file	*file;
    int		epfd;      // epoll 文件描述符
    int		op;        // 操作类型 (EPOLL_CTL_ADD/DEL/MOD)
    int		fd;        // 目标文件描述符
    struct epoll_event	event;  // epoll 事件
};
```

#### 准备阶段

```c
// io_uring/epoll.c, 第29-49行
int io_epoll_ctl_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    struct io_epoll *epoll = io_kiocb_to_cmd(req, struct io_epoll);

    if (sqe->buf_index || sqe->splice_fd_in)
        return -EINVAL;

    epoll->epfd = READ_ONCE(sqe->fd);
    epoll->op = READ_ONCE(sqe->len);
    epoll->fd = READ_ONCE(sqe->off);

    if (ep_op_has_event(epoll->op)) {
        struct epoll_event __user *ev;
        ev = u64_to_user_ptr(READ_ONCE(sqe->addr));
        if (copy_from_user(&epoll->event, ev, sizeof(*ev)))
            return -EFAULT;
    }

    return 0;
}
```

#### 执行阶段

```c
// io_uring/epoll.c, 第51-65行
int io_epoll_ctl(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_epoll *ie = io_kiocb_to_cmd(req, struct io_epoll);
    int ret;
    bool force_nonblock = issue_flags & IO_URING_F_NONBLOCK;

    ret = do_epoll_ctl(ie->epfd, ie->op, ie->fd, &ie->event, force_nonblock);
    if (force_nonblock && ret == -EAGAIN)
        return -EAGAIN;

    if (ret < 0)
        req_set_fail(req);
    io_req_set_res(req, ret, 0);
    return IOU_COMPLETE;
}
```

### 2.2 Epoll Wait 操作 (IORING_OP_EPOLL_WAIT)

```c
// io_uring/epoll.c, 第23-27行
struct io_epoll_wait {
    struct file	*file;
    int		maxevents;
    struct epoll_event __user *events;
};
```

#### 准备阶段

```c
// io_uring/epoll.c, 第67-77行
int io_epoll_wait_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    struct io_epoll_wait *iew = io_kiocb_to_cmd(req, struct io_epoll_wait);

    if (sqe->off || sqe->rw_flags || sqe->buf_index || sqe->splice_fd_in)
        return -EINVAL;

    iew->maxevents = READ_ONCE(sqe->len);
    iew->events = u64_to_user_ptr(READ_ONCE(sqe->addr));
    return 0;
}
```

#### 执行阶段

```c
// io_uring/epoll.c, 第79-92行
int io_epoll_wait(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_epoll_wait *iew = io_kiocb_to_cmd(req, struct io_epoll_wait);
    int ret;

    ret = epoll_sendevents(req->file, iew->events, iew->maxevents);
    if (ret == 0)
        return -EAGAIN;
    if (ret < 0)
        req_set_fail(req);

    io_req_set_res(req, ret, 0);
    return IOU_COMPLETE;
}
```

### 2.3 与传统 Epoll 的差异

| 特性 | 传统 Epoll | io_uring Epoll |
|------|------------|----------------|
| **调用方式** | 系统调用 (epoll_ctl/ epoll_wait) | SQE 提交 |
| **等待方式** | 阻塞/非阻塞 | 始终非阻塞, 返回 -EAGAIN |
| **事件触发** | Level/Edge | Level |
| **多路复用** | 单独系统调用 | 与其他操作统一提交 |
| **异步支持** | 否 | 是 (IOSQE_ASYNC) |
| **资源释放** | close(fd) | ring 关闭时自动清理 |

---

## 3. 取消操作 (Cancel)

### 3.1 取消操作码

**IORING_OP_ASYNC_CANCEL** 用于取消正在等待的异步操作。

### 3.2 取消标志定义

```c
// io_uring/cancel.c, 第32-34行
#define CANCEL_FLAGS (IORING_ASYNC_CANCEL_ALL | IORING_ASYNC_CANCEL_FD | \
             IORING_ASYNC_CANCEL_ANY | IORING_ASYNC_CANCEL_FD_FIXED | \
             IORING_ASYNC_CANCEL_USERDATA | IORING_ASYNC_CANCEL_OP)
```

| 标志 | 说明 |
|------|------|
| IORING_ASYNC_CANCEL_ALL | 取消所有匹配请求 |
| IORING_ASYNC_CANCEL_FD | 按文件描述符取消 |
| IORING_ASYNC_CANCEL_ANY | 取消任意匹配请求 |
| IORING_ASYNC_CANCEL_FD_FIXED | FD 是固定文件描述符 |
| IORING_ASYNC_CANCEL_USERDATA | 按 user_data 取消 |
| IORING_ASYNC_CANCEL_OP | 按操作码取消 |

### 3.3 取消匹配逻辑

```c
// io_uring/cancel.c, 第39-68行
bool io_cancel_req_match(struct io_kiocb *req, struct io_cancel_data *cd)
{
    bool match_user_data = cd->flags & IORING_ASYNC_CANCEL_USERDATA;

    if (req->ctx != cd->ctx)
        return false;

    // 默认按 user_data 匹配
    if (!(cd->flags & (IORING_ASYNC_CANCEL_FD | IORING_ASYNC_CANCEL_OP)))
        match_user_data = true;

    // FD 匹配
    if (cd->flags & IORING_ASYNC_CANCEL_FD) {
        if (req->file != cd->file)
            return false;
    }
    // 操作码匹配
    if (cd->flags & IORING_ASYNC_CANCEL_OP) {
        if (req->opcode != cd->opcode)
            return false;
    }
    // user_data 匹配
    if (match_user_data && req->cqe.user_data != cd->data)
        return false;
    // 序列匹配 (用于 CANCEL_ALL)
    if (cd->flags & IORING_ASYNC_CANCEL_ALL) {
check_seq:
        if (io_cancel_match_sequence(req, cd->seq))
            return false;
    }

    return true;
}
```

### 3.4 通用取消流程

```c
// io_uring/cancel.c, 第105-138行
int io_try_cancel(struct io_uring_task *tctx, struct io_cancel_data *cd,
          unsigned issue_flags)
{
    struct io_ring_ctx *ctx = cd->ctx;
    int ret;

    // 1. 尝试取消 io_wq 中的请求
    ret = io_async_cancel_one(tctx, cd);
    if (!ret)
        return 0;

    // 2. 尝试取消 poll 请求
    ret = io_poll_cancel(ctx, cd, issue_flags);
    if (ret != -ENOENT)
        return ret;

    // 3. 尝试取消 waitid 请求
    ret = io_waitid_cancel(ctx, cd, issue_flags);
    if (ret != -ENOENT)
        return ret;

    // 4. 尝试取消 futex 请求
    ret = io_futex_cancel(ctx, cd, issue_flags);
    if (ret != -ENOENT)
        return ret;

    // 5. 尝试取消 timeout 请求
    spin_lock(&ctx->completion_lock);
    ret = io_timeout_cancel(ctx, cd);
    spin_unlock(&ctx->completion_lock);
    return ret;
}
```

### 3.5 取消异步操作

```c
// io_uring/cancel.c, 第140-165行
int io_async_cancel_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    struct io_cancel *cancel = io_kiocb_to_cmd(req, struct io_cancel);

    if (unlikely(req->flags & REQ_F_BUFFER_SELECT))
        return -EINVAL;
    if (sqe->off || sqe->splice_fd_in)
        return -EINVAL;

    cancel->addr = READ_ONCE(sqe->addr);
    cancel->flags = READ_ONCE(sqe->cancel_flags);
    if (cancel->flags & ~CANCEL_FLAGS)
        return -EINVAL;
    if (cancel->flags & IORING_ASYNC_CANCEL_FD) {
        if (cancel->flags & IORING_ASYNC_CANCEL_ANY)
            return -EINVAL;
        cancel->fd = READ_ONCE(sqe->fd);
    }
    if (cancel->flags & IORING_ASYNC_CANCEL_OP) {
        if (cancel->flags & IORING_ASYNC_CANCEL_ANY)
            return -EINVAL;
        cancel->opcode = READ_ONCE(sqe->len);
    }

    return 0;
}
```

### 3.6 同步取消 API

**IORING_REGISTER_SYNC_CANCEL** 提供同步取消接口:

```c
// io_uring/cancel.c, 第261-348行
int io_sync_cancel(struct io_ring_ctx *ctx, void __user *arg)
    __must_hold(&ctx->uring_lock)
{
    struct io_cancel_data cd = {
        .ctx = ctx,
        .seq = atomic_inc_return(&ctx->cancel_seq),
    };
    ktime_t timeout = KTIME_MAX;
    struct io_uring_sync_cancel_reg sc;
    struct file *file = NULL;
    DEFINE_WAIT(wait);
    int ret, i;

    if (copy_from_user(&sc, arg, sizeof(sc)))
        return -EFAULT;
    if (sc.flags & ~CANCEL_FLAGS)
        return -EINVAL;

    cd.data = sc.addr;
    cd.flags = sc.flags;
    cd.opcode = sc.opcode;

    // 快速路径: 立即尝试取消
    if ((cd.flags & IORING_ASYNC_CANCEL_FD) &&
       !(cd.flags & IORING_ASYNC_CANCEL_FD_FIXED)) {
        file = fget(sc.fd);
        if (!file)
            return -EBADF;
        cd.file = file;
    }

    ret = __io_sync_cancel(current->io_uring, &cd, sc.fd);

    // 已找到并取消
    if (ret != -EALREADY)
        goto out;

    // 慢速路径: 等待取消完成
    if (sc.timeout.tv_sec != -1UL || sc.timeout.tv_nsec != -1UL) {
        struct timespec64 ts = {
            .tv_sec = sc.timeout.tv_sec,
            .tv_nsec = sc.timeout.tv_nsec
        };
        timeout = ktime_add_ns(timespec64_to_ktime(ts), ktime_get_ns());
    }

    do {
        cd.seq = atomic_inc_return(&ctx->cancel_seq);
        prepare_to_wait(&ctx->cq_wait, &wait, TASK_INTERRUPTIBLE);
        ret = __io_sync_cancel(current->io_uring, &cd, sc.fd);
        mutex_unlock(&ctx->uring_lock);
        if (ret != -EALREADY)
            break;
        ret = io_run_task_work_sig(ctx);
        if (ret < 0)
            break;
        ret = schedule_hrtimeout(&timeout, HRTIMER_MODE_ABS);
        if (!ret) {
            ret = -ETIME;
            break;
        }
        mutex_lock(&ctx->uring_lock);
    } while (1);

    finish_wait(&ctx->cq_wait, &wait);
    mutex_lock(&ctx->uring_lock);

    if (ret == -ENOENT || ret > 0)
        ret = 0;
out:
    if (file)
        fput(file);
    return ret;
}
```

### 3.7 取消条件判断

```c
// io_uring/cancel.c, 第70-76行
static bool io_cancel_cb(struct io_wq_work *work, void *data)
{
    struct io_kiocb *req = container_of(work, struct io_kiocb, work);
    struct io_cancel_data *cd = data;

    return io_cancel_req_match(req, cd);
}
```

---

## 4. 通知机制 (Notification)

### 4.1 通知数据结构

```c
// io_uring/notif.h, 第13-24行
struct io_notif_data {
    struct file		*file;
    struct ubuf_info	uarg;           // 用户缓冲区信息

    struct io_notif_data	*next;    // 链表下一节点
    struct io_notif_data	*head;    // 链表头

    unsigned		account_pages;
    bool			zc_report;   // 零拷贝报告
    bool			zc_used;     // 零拷贝已使用
    bool			zc_copied;   // 零拷贝已复制
};
```

### 4.2 零拷贝发送完成回调

```c
// io_uring/eventfd.c, 第43-68行
void io_tx_ubuf_complete(struct sk_buff *skb, struct ubuf_info *uarg,
                 bool success)
{
    struct io_notif_data *nd = container_of(uarg, struct io_notif_data, uarg);
    struct io_kiocb *notif = cmd_to_io_kiocb(nd);
    unsigned tw_flags;

    // 处理零拷贝状态报告
    if (nd->zc_report) {
        if (success && !nd->zc_used && skb)
            WRITE_ONCE(nd->zc_used, true);
        else if (!success && !nd->zc_copied)
            WRITE_ONCE(nd->zc_copied, true);
    }

    // 引用计数归零时才完成
    if (!refcount_dec_and_test(&uarg->refcnt))
        return;

    // 处理链表
    if (nd->head != nd) {
        io_tx_ubuf_complete(skb, &nd->head->uarg, success);
        return;
    }

    tw_flags = nd->next ? 0 : IOU_F_TWQ_LAZY_WAKE;
    notif->io_task_work.func = io_notif_tw_complete;
    __io_req_task_work_add(notif, tw_flags);
}
```

### 4.3 通知完成处理

```c
// io_uring/eventfd.c, 第15-41行
static void io_notif_tw_complete(struct io_tw_req tw_req, io_tw_token_t tw)
{
    struct io_kiocb *notif = tw_req.req;
    struct io_notif_data *nd = io_notif_to_data(notif);
    struct io_ring_ctx *ctx = notif->ctx;

    lockdep_assert_held(&ctx->uring_lock);

    do {
        notif = cmd_to_io_kiocb(nd);

        if (WARN_ON_ONCE(ctx != notif->ctx))
            return;
        lockdep_assert(refcount_read(&nd->uarg.refcnt) == 0);

        // 处理零拷贝使用报告
        if (unlikely(nd->zc_report) && (nd->zc_copied || !nd->zc_used))
            notif->cqe.res |= IORING_NOTIF_USAGE_ZC_COPIED;

        // 释放账户内存
        if (nd->account_pages && notif->ctx->user) {
            __io_unaccount_mem(notif->ctx->user, nd->account_pages);
            nd->account_pages = 0;
        }

        nd = nd->next;
        io_req_task_complete((struct io_tw_req){notif}, tw);
    } while (nd);
}
```

### 4.4 通知分配

```c
// io_uring/eventfd.c, 第114-141行
struct io_kiocb *io_alloc_notif(struct io_ring_ctx *ctx)
    __must_hold(&ctx->uring_lock)
{
    struct io_kiocb *notif;
    struct io_notif_data *nd;

    if (unlikely(!io_alloc_req(ctx, &notif)))
        return NULL;
    notif->ctx = ctx;
    notif->opcode = IORING_OP_NOP;
    notif->flags = 0;
    notif->file = NULL;
    notif->tctx = current->io_uring;
    io_get_task_refs(1);
    notif->file_node = NULL;
    notif->buf_node = NULL;

    nd = io_notif_to_data(notif);
    nd->zc_report = false;
    nd->account_pages = 0;
    nd->next = NULL;
    nd->head = nd;

    nd->uarg.flags = IO_NOTIF_UBUF_FLAGS;
    nd->uarg.ops = &io_ubuf_ops;
    refcount_set(&nd->uarg.refcnt, 1);
    return notif;
}
```

### 4.5 零拷贝标志

```c
// include/uapi/linux/io_uring.h, 第438-444行
/*
 * send/sendmsg 和 recv/recvmsg 标志 (sqe->ioprio)
 *
 * IORING_SEND_ZC_REPORT_USAGE: 请求在 cqe.res 中报告零拷贝使用情况
 */
#define IORING_NOTIF_USAGE_ZC_COPIED    (1U << 31)
```

---

## 5. Futex 支持

### 5.1 Futex 数据结构

```c
// io_uring/futex.c, 第15-33行
struct io_futex {
    struct file	*file;
    void __user	*uaddr;           // futex 地址
    unsigned long	futex_val;     // 期望值
    unsigned long	futex_mask;    // mask
    u32		futex_flags;       // 标志
    unsigned int	futex_nr;       // futex 数量 (用于 waitv)
    bool		futexv_unqueued;
};

struct io_futex_data {
    struct futex_q	q;
    struct io_kiocb	*req;
};

struct io_futexv_data {
    unsigned long		owned;
    struct futex_vector	futexv[];
};
```

### 5.2 Futex 操作码

| 操作码 | 说明 |
|--------|------|
| IORING_OP_FUTEX_WAIT | 等待 futex |
| IORING_OP_FUTEX_WAKE | 唤醒等待者 |
| IORING_OP_FUTEX_WAITV | 等待多个 futex |

### 5.3 Futex 等待操作

```c
// io_uring/futex.c, 第274-317行
int io_futex_wait(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_futex *iof = io_kiocb_to_cmd(req, struct io_futex);
    struct io_ring_ctx *ctx = req->ctx;
    struct io_futex_data *ifd = NULL;
    int ret;

    if (!iof->futex_mask) {
        ret = -EINVAL;
        goto done;
    }

    io_ring_submit_lock(ctx, issue_flags);
    ifd = io_cache_alloc(&ctx->futex_cache, GFP_NOWAIT);
    if (!ifd) {
        ret = -ENOMEM;
        goto done_unlock;
    }

    req->flags |= REQ_F_ASYNC_DATA;
    req->async_data = ifd;
    ifd->q = futex_q_init;
    ifd->q.bitset = iof->futex_mask;
    ifd->q.wake = io_futex_wake_fn;
    ifd->req = req;

    ret = futex_wait_setup(iof->uaddr, iof->futex_val, iof->futex_flags,
                   &ifd->q, NULL, NULL);
    if (!ret) {
        hlist_add_head(&req->hash_node, &ctx->futex_list);
        io_ring_submit_unlock(ctx, issue_flags);
        return IOU_ISSUE_SKIP_COMPLETE;
    }

done_unlock:
    io_ring_submit_unlock(ctx, issue_flags);
done:
    if (ret < 0)
        req_set_fail(req);
    io_req_set_res(req, ret, 0);
    io_req_async_data_free(req);
    return IOU_COMPLETE;
}
```

### 5.4 Futex Wake 操作

```c
// io_uring/futex.c, 第319-334行
int io_futex_wake(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_futex *iof = io_kiocb_to_cmd(req, struct io_futex);
    int ret;

    /*
     * 严格标志 - 确保唤醒 0 个 futex 返回 0 结果
     * 参见 commit 43adf8449510 ("futex: FLAGS_STRICT")
     */
    ret = futex_wake(iof->uaddr, FLAGS_STRICT | iof->futex_flags,
             iof->futex_val, iof->futex_mask);
    if (ret < 0)
        req_set_fail(req);
    io_req_set_res(req, ret, 0);
    return IOU_COMPLETE;
}
```

### 5.5 Futex Waitv 操作

```c
// io_uring/futex.c, 第221-272行
int io_futexv_wait(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_futex *iof = io_kiocb_to_cmd(req, struct io_futex);
    struct io_futexv_data *ifd = req->async_data;
    struct io_ring_ctx *ctx = req->ctx;
    int ret, woken = -1;

    io_ring_submit_lock(ctx, issue_flags);

    ret = futex_wait_multiple_setup(ifd->futexv, iof->futex_nr, &woken);

    if (unlikely(ret < 0)) {
        io_ring_submit_unlock(ctx, issue_flags);
        req_set_fail(req);
        io_req_set_res(req, ret, 0);
        io_req_async_data_free(req);
        return IOU_COMPLETE;
    }

    if (!ret) {
        // 成功设置等待, 任务状态不可运行
        __set_current_state(TASK_RUNNING);
        hlist_add_head(&req->hash_node, &ctx->futex_list);
    } else {
        // 等待期间被唤醒
        iof->futexv_unqueued = 1;
        if (woken != -1)
            io_req_set_res(req, woken, 0);
    }

    io_ring_submit_unlock(ctx, issue_flags);
    return IOU_ISSUE_SKIP_COMPLETE;
}
```

### 5.6 Futex 取消

```c
// io_uring/futex.c, 第92-113行
static bool __io_futex_cancel(struct io_kiocb *req)
{
    /* futex wake 已完成或正在进行 */
    if (req->opcode == IORING_OP_FUTEX_WAIT) {
        struct io_futex_data *ifd = req->async_data;

        if (!futex_unqueue(&ifd->q))
            return false;
        req->io_task_work.func = io_futex_complete;
    } else {
        struct io_futexv_data *ifd = req->async_data;

        if (!io_futexv_claim(ifd))
            return false;
        req->io_task_work.func = io_futexv_complete;
    }

    hlist_del_init(&req->hash_node);
    io_req_set_res(req, -ECANCELED, 0);
    io_req_task_work_add(req);
    return true;
}
```

### 5.7 Futex 缓存管理

```c
// io_uring/futex.c, 第37-46行
bool io_futex_cache_init(struct io_ring_ctx *ctx)
{
    return io_alloc_cache_init(&ctx->futex_cache, IO_FUTEX_ALLOC_CACHE_MAX,
                sizeof(struct io_futex_data), 0);
}

void io_futex_cache_free(struct io_ring_ctx *ctx)
{
    io_alloc_cache_free(&ctx->futex_cache, kfree);
}
```

---

## 6. Timeout 操作

### 6.1 Timeout 数据结构

```c
// io_uring/timeout.c, 第16-36行
struct io_timeout {
    struct file	*file;
    u32		off;           // 事件计数偏移
    u32		target_seq;    // 目标序列号
    u32		repeats;       // 重复次数 (multishot)
    struct list_head	list;
    struct io_kiocb	*head;      // 链接超时头
    struct io_kiocb	*prev;      // 前一个链接
};

struct io_timeout_rem {
    struct file	*file;
    u64		addr;
    struct timespec64	ts;
    u32		flags;
    bool	ltimeout;
};

struct io_timeout_data {
    struct io_kiocb	*req;
    struct hrtimer	timer;
    struct timespec64	ts;
    enum hrtimer_mode	mode;
    u32		flags;
};
```

### 6.2 Timeout 标志

```c
// include/uapi/linux/io_uring.h, 第343-353行
#define IORING_TIMEOUT_ABS		(1U << 0)    // 绝对时间
#define IORING_TIMEOUT_UPDATE		(1U << 1)    // 更新超时
#define IORING_TIMEOUT_BOOTTIME		(1U << 2)    // 从启动时间开始
#define IORING_TIMEOUT_REALTIME	(1U << 3)    // 从实时时钟
#define IORING_LINK_TIMEOUT_UPDATE	(1U << 4)    // 更新链接超时
#define IORING_TIMEOUT_ETIME_SUCCESS	(1U << 5)    // 超时视为成功
#define IORING_TIMEOUT_MULTISHOT	(1U << 6)    // 多重射击模式
#define IORING_TIMEOUT_CLOCK_MASK	(IORING_TIMEOUT_BOOTTIME | IORING_TIMEOUT_REALTIME)
#define IORING_TIMEOUT_UPDATE_MASK	(IORING_TIMEOUT_UPDATE | IORING_LINK_TIMEOUT_UPDATE)
```

### 6.3 基本 Timeout 操作

```c
// io_uring/timeout.c, 第595-643行
int io_timeout(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_timeout *timeout = io_kiocb_to_cmd(req, struct io_timeout);
    struct io_ring_ctx *ctx = req->ctx;
    struct io_timeout_data *data = req->async_data;
    struct list_head *entry;
    u32 tail, off = timeout->off;

    raw_spin_lock_irq(&ctx->timeout_lock);

    // 无序列超时 - 纯超时请求
    if (io_is_timeout_noseq(req)) {
        entry = ctx->timeout_list.prev;
        goto add;
    }

    // 计算目标序列号
    tail = data_race(ctx->cached_cq_tail) - atomic_read(&ctx->cq_timeouts);
    timeout->target_seq = tail + off;

    // 插入排序, 确保最早超时的在最前面
    list_for_each_prev(entry, &ctx->timeout_list) {
        struct io_timeout *nextt = list_entry(entry, struct io_timeout, list);
        struct io_kiocb *nxt = cmd_to_io_kiocb(nextt);

        if (io_is_timeout_noseq(nxt))
            continue;
        if (off >= nextt->target_seq - tail)
            break;
    }
add:
    list_add(&timeout->list, entry);
    hrtimer_start(&data->timer, timespec64_to_ktime(data->ts), data->mode);
    raw_spin_unlock_irq(&ctx->timeout_lock);
    return IOU_ISSUE_SKIP_COMPLETE;
}
```

### 6.4 Link Timeout (链接超时)

链接超时用于限制一组链接操作的总执行时间:

```c
// io_uring/timeout.c, 第590-593行
int io_link_timeout_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)
{
    return __io_timeout_prep(req, sqe, true);
}

// io_uring/timeout.c, 第568-578行
if (is_timeout_link) {
    struct io_submit_link *link = &req->ctx->submit_state.link;

    if (!link->head)
        return -EINVAL;
    if (link->last->opcode == IORING_OP_LINK_TIMEOUT)
        return -EINVAL;
    timeout->head = link->last;
    link->last->flags |= REQ_F_ARM_LTIMEOUT;
    hrtimer_setup(&data->timer, io_link_timeout_fn, io_timeout_get_clock(data),
              data->mode);
}
```

### 6.5 链接超时回调

```c
// io_uring/timeout.c, 第350-379行
static enum hrtimer_restart io_link_timeout_fn(struct hrtimer *timer)
{
    struct io_timeout_data *data = container_of(timer,
                        struct io_timeout_data, timer);
    struct io_kiocb *prev, *req = data->req;
    struct io_timeout *timeout = io_kiocb_to_cmd(req, struct io_timeout);
    struct io_ring_ctx *ctx = req->ctx;
    unsigned long flags;

    raw_spin_lock_irqsave(&ctx->timeout_lock, flags);
    prev = timeout->head;
    timeout->head = NULL;

    if (prev) {
        io_remove_next_linked(prev);
        if (!req_ref_inc_not_zero(prev))
            prev = NULL;
    }
    list_del(&timeout->list);
    timeout->prev = prev;
    raw_spin_unlock_irqrestore(&ctx->timeout_lock, flags);

    req->io_task_work.func = io_req_task_link_timeout;
    io_req_task_work_add(req);
    return HRTIMER_NORESTART;
}
```

### 6.6 链接超时任务处理

```c
// io_uring/timeout.c, 第323-348行
static void io_req_task_link_timeout(struct io_tw_req tw_req, io_tw_token_t tw)
{
    struct io_kiocb *req = tw_req.req;
    struct io_timeout *timeout = io_kiocb_to_cmd(req, struct io_timeout);
    struct io_kiocb *prev = timeout->prev;
    int ret;

    if (prev) {
        if (!tw.cancel) {
            struct io_cancel_data cd = {
                .ctx = req->ctx,
                .data = prev->cqe.user_data,
            };
            ret = io_try_cancel(req->tctx, &cd, 0);
        } else {
            ret = -ECANCELED;
        }
        io_req_set_res(req, ret ?: -ETIME, 0);
        io_req_task_complete(tw_req, tw);
        io_put_req(prev);
    } else {
        io_req_set_res(req, -ETIME, 0);
        io_req_task_complete(tw_req, tw);
    }
}
```

### 6.7 Timeout 移除/更新

```c
// io_uring/timeout.c, 第486-513行
int io_timeout_remove(struct io_kiocb *req, unsigned int issue_flags)
{
    struct io_timeout_rem *tr = io_kiocb_to_cmd(req, struct io_timeout_rem);
    struct io_ring_ctx *ctx = req->ctx;
    int ret;

    if (!(tr->flags & IORING_TIMEOUT_UPDATE)) {
        // 移除超时
        struct io_cancel_data cd = { .ctx = ctx, .data = tr->addr, };
        spin_lock(&ctx->completion_lock);
        ret = io_timeout_cancel(ctx, &cd);
        spin_unlock(&ctx->completion_lock);
    } else {
        // 更新超时
        enum hrtimer_mode mode = io_translate_timeout_mode(tr->flags);
        raw_spin_lock_irq(&ctx->timeout_lock);
        if (tr->ltimeout)
            ret = io_linked_timeout_update(ctx, tr->addr, &tr->ts, mode);
        else
            ret = io_timeout_update(ctx, tr->addr, &tr->ts, mode);
        raw_spin_unlock_irq(&ctx->timeout_lock);
    }

    if (ret < 0)
        req_set_fail(req);
    io_req_set_res(req, ret, 0);
    return IOU_COMPLETE;
}
```

### 6.8 Timeout 刷新

```c
// io_uring/timeout.c, 第126-159行
__cold void io_flush_timeouts(struct io_ring_ctx *ctx)
{
    struct io_timeout *timeout, *tmp;
    LIST_HEAD(list);
    u32 seq;

    raw_spin_lock_irq(&ctx->timeout_lock);
    seq = READ_ONCE(ctx->cached_cq_tail) - atomic_read(&ctx->cq_timeouts);

    list_for_each_entry_safe(timeout, tmp, &ctx->timeout_list, list) {
        struct io_kiocb *req = cmd_to_io_kiocb(timeout);
        u32 events_needed, events_got;

        if (io_is_timeout_noseq(req))
            break;

        events_needed = timeout->target_seq - ctx->cq_last_tm_flush;
        events_got = seq - ctx->cq_last_tm_flush;
        if (events_got < events_needed)
            break;

        io_kill_timeout(req, &list);
    }
    ctx->cq_last_tm_flush = seq;
    raw_spin_unlock_irq(&ctx->timeout_lock);
    io_flush_killed_timeouts(&list, 0);
}
```

### 6.9 Timeout 流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                   SQE: IORING_OP_TIMEOUT                        │
│  - addr: timespec 结构指针                                       │
│  - off: 事件计数 (0 表示无序列)                                  │
│  - timeout_flags: ABS/BOOTTIME/REALTIME/MULTISHOT              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 io_timeout_prep()                               │
│  - 分配 io_timeout_data                                         │
│  - 设置 hrtimer                                                 │
│  - 如果是链接超时, 标记 REQ_F_ARM_LTIMEOUT                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   io_timeout()                                  │
│  - 计算 target_seq = tail + off                                 │
│  - 按超时时间插入排序                                            │
│  - 启动 hrtimer                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               hrtimer 到期 → io_timeout_fn()                  │
│  - 设置 -ETIME 结果                                              │
│  - 添加到 task_work                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. 错误处理

### 7.1 CQE 结果码

```c
// include/uapi/linux/io_uring.h, 第492-503行
struct io_uring_cqe {
    __u64	user_data;    // sqe->user_data 值
    __s32	res;          // 结果码 (类似系统调用返回值)
    __u32	flags;        // 标志

    __u64 big_cqe[];      // CQE32 模式下的扩展数据
};
```

### 7.2 CQE 标志

```c
// include/uapi/linux/io_uring.h, 第505-537行
#define IORING_CQE_F_BUFFER		(1U << 0)   // 上 16 位是 buffer ID
#define IORING_CQE_F_MORE		(1U << 1)   // 还有更多 CQE
#define IORING_CQE_F_SOCK_NONEMPTY	(1U << 2)   // socket 还有数据
#define IORING_CQE_F_NOTIF		(1U << 3)   // 通知 CQE
#define IORING_CQE_F_BUF_MORE		(1U << 4)   // buffer 还有更多数据
#define IORING_CQE_F_SKIP		(1U << 5)   // 跳过此 CQE
#define IORING_CQE_F_32			(1U << 15)  // 32 字节 CQE
```

### 7.3 常见错误码

| 错误码 | 说明 | 常见场景 |
|--------|------|----------|
| 0 | 成功 | 正常完成 |
| -EINVAL | 无效参数 | 参数错误 |
| -EFAULT | 段错误 | 内存访问错误 |
| -EBADF | 错误文件描述符 | FD 不存在 |
| -EAGAIN | 资源临时不可用 | 非阻塞操作需要重试 |
| -EINTR | 系统调用被中断 | 信号中断 |
| -ECANCELED | 操作已取消 | 被取消 |
| -ETIME | 超时 | Timeout 过期 |
| -ENOENT | 找不到 | 资源不存在 |
| -ENOMEM | 内存不足 | 内存分配失败 |
| -EALREADY | 已在处理中 | 取消时操作正在完成 |
| -ENFILE | 文件表满 | 达到文件描述符限制 |

### 7.4 错误设置宏

```c
// io_uring/io_uring.h, 第318-325行
static inline void req_set_fail(struct io_kiocb *req)
{
    req->flags |= REQ_F_FAIL;
    if (req->flags & REQ_F_CQE_SKIP) {
        req->flags &= ~REQ_F_CQE_SKIP;
        req->flags |= REQ_F_SKIP_LINK_CQES;
    }
}
```

### 7.5 结果设置宏

```c
// io_uring/io_uring.h, 第327-331行
static inline void io_req_set_res(struct io_kiocb *req, s32 res, u32 cflags)
{
    req->cqe.res = res;
    req->cqe.flags = cflags;
}
```

### 7.6 错误处理流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      操作执行                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ret < 0?                                      │
│    ├─ 是 → req_set_fail(req)                                   │
│    └─ 否 → 成功                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              io_req_set_res(req, ret, flags)                   │
│  - 设置 cqe.res = 系统错误码                                     │
│  - 设置 cqe.flags                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              IOU_COMPLETE / IOU_ISSUE_SKIP_COMPLETE            │
│  - 返回用户空间                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.7 errno 映射

io_uring 的 CQE.res 直接使用内核错误码 (负值), 用户空间需要转换为正值:

```c
// liburing 中的典型转换
if (cqe->res < 0) {
    errno = -cqe->res;
    // 处理错误
} else {
    // 使用返回值
}
```

---

## 8. 总结

### 8.1 特性总览

| 功能 | 操作码 | 说明 |
|------|--------|------|
| Eventfd 注册 | IORING_REGISTER_EVENTFD | CQ 完成通知 |
| Eventfd 异步 | IORING_REGISTER_EVENTFD_ASYNC | 允许异步 worker 触发 |
| Epoll 控制 | IORING_OP_EPOLL_CTL | 替代 epoll_ctl |
| Epoll 等待 | IORING_OP_EPOLL_WAIT | 替代 epoll_wait |
| 异步取消 | IORING_OP_ASYNC_CANCEL | 取消待处理请求 |
| 同步取消 | IORING_REGISTER_SYNC_CANCEL | 同步取消 API |
| Futex 等待 | IORING_OP_FUTEX_WAIT | 等待单个 futex |
| Futex 唤醒 | IORING_OP_FUTEX_WAKE | 唤醒 futex 等待者 |
| Futex 等待多个 | IORING_OP_FUTEX_WAITV | 等待多个 futex |
| 超时 | IORING_OP_TIMEOUT | 单次或多重射击超时 |
| 链接超时 | IORING_OP_LINK_TIMEOUT | 限制链接操作时间 |
| 超时移除 | IORING_OP_TIMEOUT_REMOVE | 移除/更新超时 |

### 8.2 设计要点

1. **零拷贝通知**: 通过 `io_notif_data` 结构支持零拷贝网络通知
2. **高精度定时器**: 使用 hrtimer 实现微秒级超时精度
3. **灵活的取消机制**: 支持多种匹配条件的异步/同步取消
4. **任务工作队列**: 所有完成通过 task_work 机制处理
5. **RCU 优化**: eventfd 使用 RCU 机制减少锁竞争

### 8.3 性能优化

1. **缓存分配**: futex 和 timeout 使用专用缓存减少分配开销
2. **延迟信号**: eventfd 使用原子操作避免信号风暴
3. **批量处理**: 支持多重射击操作减少系统调用次数
4. **锁优化**: 使用 RCU 和局部锁减少全局竞争
