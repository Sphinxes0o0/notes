# Linux 内核 IPC (进程间通信) 子系统分析文档

## 目录

1. [概述](#1-概述)
2. [消息队列 (msg)](#2-消息队列-msg)
3. [信号量 (sem)](#3-信号量-sem)
4. [共享内存 (shm)](#4-共享内存-shm)
5. [POSIX 消息队列 (mqueue)](#5-posix-消息队列-mqueue)
6. [IPC 通用框架](#6-ipc-通用框架)
7. [架构图](#7-架构图)

---

## 1. 概述

Linux 内核的 IPC 子系统提供了多种进程间通信机制，包括：

- **消息队列 (Message Queues)** - SysV 消息队列
- **信号量 (Semaphores)** - SysV 信号量
- **共享内存 (Shared Memory)** - SysV 共享内存
- **POSIX 消息队列** - POSIX 标准消息队列

### 源码位置

| 组件 | 路径 |
|------|------|
| msg | `/Users/sphinx/github/linux/ipc/msg.c` |
| sem | `/Users/sphinx/github/linux/ipc/sem.c` |
| shm | `/Users/sphinx/github/linux/ipc/shm.c` |
| mqueue | `/Users/sphinx/github/linux/ipc/mqueue.c` |
| util | `/Users/sphinx/github/linux/ipc/util.c` |

### 核心数据结构

IPC 对象的基础结构 `kern_ipc_perm`（定义在 `include/linux/ipc.h`）:

```c
struct kern_ipc_perm {
    spinlock_t      lock;
    refcount_t      refcount;
    struct key      *key;          /* 键值 */
    kuid_t          uid;           /* 创建者 UID */
    kgid_t          gid;           /* 创建者 GID */
    kuid_t          cuid;          /* 创建者 EUID */
    kgid_t          cgid;          /* 创建者 EGID */
    umode_t         mode;          /* 权限位 */
    unsigned long   ipc64.perms;   /* 时间戳等 */
    struct idr      *idr;          /* IDR 树 */
    struct rcu_head rcu;           /* RCU 回调 */
    struct hlist_node khtnode;    /* 键值哈希表节点 */
    int             id;            /* IPC 标识符 */
    int             seq;           /* 序列号 */
    bool            deleted;       /* 是否已删除 */
};
```

### IPC ID 编码规则

IPC ID 包含两个独立数字：索引 (index) 和序列号 (sequence number)

```
默认模式 (15位索引, 16位序列号):
  bits  0-14: index (32k, 15 bits)
  bits 15-30: sequence number (64k, 16 bits)

扩展模式 (23位索引, 7位序列号):
  bits  0-23: index (16M, 24 bits)
  bits 24-30: sequence number (128, 7 bits)
```

### 通用锁定方案

```
rcu_read_lock()
    通过 idr 树查找 ipc object (kern_ipc_perm)
    - 执行初始检查 (能力、审计、权限等)
    - 执行只读操作 (如 INFO 命令)
    获取 ipc lock (kern_ipc_perm.lock) via ipc_lock_object()
        - 执行需要原子性的只读操作 (如 STAT 命令)
        - 执行数据更新 (SET, RMID 命令和特定操作)
    释放 ipc lock via ipc_unlock_object()
rcu_read_unlock()
```

---

## 2. 消息队列 (msg)

### 2.1 核心数据结构

#### msg_msg - 单条消息结构 (msg.c:48-63)

```c
struct msg_queue {
    struct kern_ipc_perm q_perm;      /* 权限结构 */
    time64_t         q_stime;          /* 最后 msgsnd 时间 */
    time64_t         q_rtime;          /* 最后 msgrcv 时间 */
    time64_t         q_ctime;          /* 最后改变时间 */
    unsigned long    q_cbytes;         /* 当前队列字节数 */
    unsigned long    q_qnum;           /* 队列消息数 */
    unsigned long    q_qbytes;         /* 最大字节数 */
    struct pid       *q_lspid;         /* 最后 msgsnd 的 pid */
    struct pid       *q_lrpid;         /* 最后接收的 pid */

    struct list_head q_messages;      /* 消息链表 */
    struct list_head q_receivers;     /* 等待接收的进程 */
    struct list_head q_senders;       /* 等待发送的进程 */
};
```

#### msg_msg - 单条消息结构

消息的实际结构定义在内核通用消息层 (include/linux/msg.h):

```c
struct msg_msg {
    struct list_head    m_list;        /* 消息链表 */
    long                m_type;        /* 消息类型 */
    size_t              m_ts;          /* 消息大小 */
    struct msg_msgseg   *next;         /* 下一段 (如果消息跨段) */
    /* 消息数据紧随其后 */
};
```

#### msg_receiver - 等待接收者

```c
struct msg_receiver {
    struct list_head    r_list;        /* 接收者链表 */
    struct task_struct  *r_tsk;        /* 等待进程 */
    int                 r_mode;        /* 搜索模式 */
    long                r_msgtype;     /* 消息类型 */
    long                r_maxsize;      /* 最大消息大小 */
    struct msg_msg      *r_msg;        /* 接收的消息 */
};
```

#### msg_sender - 等待发送者

```c
struct msg_sender {
    struct list_head    list;          /* 链表 */
    struct task_struct  *tsk;          /* 等待进程 */
    size_t              msgsz;         /* 消息大小 */
};
```

### 2.2 关键函数分析

#### newque() - 创建新消息队列 (msg.c:144-185)

```c
static int newque(struct ipc_namespace *ns, struct ipc_params *params)
{
    struct msg_queue *msq;
    int retval;
    key_t key = params->key;
    int msgflg = params->flg;

    msq = kmalloc_obj(*msq, GFP_KERNEL_ACCOUNT);  /* 分配队列 */
    if (unlikely(!msq))
        return -ENOMEM;

    msq->q_perm.mode = msgflg & S_IRWXUGO;
    msq->q_perm.key = key;
    msq->q_perm.security = NULL;
    retval = security_msg_queue_alloc(&msq->q_perm);  /* 安全模块分配 */
    // ... 初始化队列各字段 ...

    /* ipc_addid() 成功时会锁定 msq */
    retval = ipc_addid(&msg_ids(ns), &msq->q_perm, ns->msg_ctlmni);
    if (retval < 0) {
        ipc_rcu_putref(&msq->q_perm, msg_rcu_free);
        return retval;
    }

    ipc_unlock_object(&msq->q_perm);
    rcu_read_unlock();

    return msq->q_perm.id;
}
```

#### do_msgsnd() - 发送消息 (msg.c:848-959)

```c
static long do_msgsnd(int msqid, long mtype, void __user *mtext,
        size_t msgsz, int msgflg)
{
    // 1. 参数验证
    if (msgsz > ns->msg_ctlmax || (long) msgsz < 0 || msqid < 0)
        return -EINVAL;
    if (mtype < 1)
        return -EINVAL;

    // 2. 加载用户消息到内核
    msg = load_msg(mtext, msgsz);
    if (IS_ERR(msg))
        return PTR_ERR(msg);
    msg->m_type = mtype;
    msg->m_ts = msgsz;

    // 3. 获取消息队列
    rcu_read_lock();
    msq = msq_obtain_object_check(ns, msqid);
    ipc_lock_object(&msq->q_perm);

    // 4. 循环直到消息成功入队或阻塞
    for (;;) {
        // 权限检查
        if (ipcperms(ns, &msq->q_perm, S_IWUGO))
            goto out_unlock;

        // 检查队列是否已被删除
        if (!ipc_valid_object(&msq->q_perm)) {
            err = -EIDRM;
            goto out_unlock;
        }

        // 安全检查
        err = security_msg_queue_msgsnd(&msq->q_perm, msg, msgflg);
        if (err)
            goto out_unlock;

        // 检查队列是否有足够空间
        if (msg_fits_inqueue(msq, msgsz))
            break;

        // 队列满，需要等待
        if (msgflg & IPC_NOWAIT) {
            err = -EAGAIN;
            goto out_unlock;
        }

        // 将发送者加入等待队列并睡眠
        ss_add(msq, &s, msgsz);
        schedule();  // 调度其他进程
        // 醒来后重新检查...
    }

    // 5. 更新队列状态并可能直接传递给等待的接收者
    ipc_update_pid(&msq->q_lspid, task_tgid(current));
    msq->q_stime = ktime_get_real_seconds();

    if (!pipelined_send(msq, msg, &wake_q)) {
        /* 没有等待的接收者，消息入队 */
        list_add_tail(&msg->m_list, &msq->q_messages);
        msq->q_cbytes += msgsz;
        msq->q_qnum++;
        percpu_counter_add_local(&ns->percpu_msg_bytes, msgsz);
        percpu_counter_add_local(&ns->percpu_msg_hdrs, 1);
    }
    // ...
}
```

#### do_msgrcv() - 接收消息 (msg.c:1098-1262)

```c
static long do_msgrcv(int msqid, void __user *buf, size_t bufsz,
    long msgtyp, int msgflg,
    long (*msg_handler)(void __user *, struct msg_msg *, size_t))
{
    // 1. 转换接收模式
    mode = convert_mode(&msgtyp, msgflg);

    rcu_read_lock();
    msq = msq_obtain_object_check(ns, msqid);

    for (;;) {
        struct msg_receiver msr_d;

        // 权限检查
        if (ipcperms(ns, &msq->q_perm, S_IRUGO))
            goto out_unlock;

        ipc_lock_object(&msq->q_perm);

        // 查找匹配的消息
        msg = find_msg(msq, &msgtyp, mode);
        if (!IS_ERR(msg)) {
            // 找到消息
            if ((bufsz < msg->m_ts) && !(msgflg & MSG_NOERROR)) {
                msg = ERR_PTR(-E2BIG);
                goto out_unlock;
            }
            // 复制消息到用户空间
            if (msgflg & MSG_COPY) {
                msg = copy_msg(msg, copy);
                goto out_unlock;
            }

            // 从队列移除消息
            list_del(&msg->m_list);
            msq->q_qnum--;
            msq->q_rtime = ktime_get_real_seconds();
            ipc_update_pid(&msq->q_lrpid, task_tgid(current));
            msq->q_cbytes -= msg->m_ts;
            percpu_counter_sub_local(&ns->percpu_msg_bytes, msg->m_ts);
            percpu_counter_sub_local(&ns->percpu_msg_hdrs, 1);
            ss_wakeup(msq, &wake_q, false);
            goto out_unlock;
        }

        // 没有消息，等待
        if (msgflg & IPC_NOWAIT) {
            msg = ERR_PTR(-ENOMSG);
            goto out_unlock;
        }

        // 将接收者加入等待队列
        list_add_tail(&msr_d.r_list, &msq->q_receivers);
        msr_d.r_tsk = current;
        msr_d.r_msgtype = msgtyp;
        msr_d.r_mode = mode;
        __set_current_state(TASK_INTERRUPTIBLE);

        ipc_unlock_object(&msq->q_perm);
        rcu_read_unlock();
        schedule();  // 睡眠等待

        // 醒来后重新检查...
    }
}
```

### 2.3 消息搜索模式 (msg.c:794-814)

```c
#define SEARCH_ANY        1   /* 匹配任何类型 */
#define SEARCH_EQUAL      2   /* 精确匹配类型 */
#define SEARCH_NOTEQUAL   3   /* 不等于类型 */
#define SEARCH_LESSEQUAL  4   /* 小于等于类型 */
#define SEARCH_NUMBER     5   /* 按编号匹配 (用于 MSG_COPY) */

static int testmsg(struct msg_msg *msg, long type, int mode)
{
    switch (mode) {
    case SEARCH_ANY:
    case SEARCH_NUMBER:
        return 1;
    case SEARCH_LESSEQUAL:
        if (msg->m_type <= type)
            return 1;
        break;
    case SEARCH_EQUAL:
        if (msg->m_type == type)
            return 1;
        break;
    case SEARCH_NOTEQUAL:
        if (msg->m_type != type)
            return 1;
        break;
    }
    return 0;
}
```

### 2.4 管道化发送 (Pipelined Send)

当发送消息时，如果已有等待的接收者，消息会直接传递给他 (msg.c:816-846):

```c
static inline int pipelined_send(struct msg_queue *msq, struct msg_msg *msg,
                 struct wake_q_head *wake_q)
{
    struct msg_receiver *msr, *t;

    list_for_each_entry_safe(msr, t, &msq->q_receivers, r_list) {
        if (testmsg(msg, msr->r_msgtype, msr->r_mode) &&
            !security_msg_queue_msgrcv(&msq->q_perm, msg, msr->r_tsk,
                           msr->r_msgtype, msr->r_mode)) {

            list_del(&msr->r_list);
            if (msr->r_maxsize < msg->m_ts) {
                /* 缓冲区太小 */
                smp_store_release(&msr->r_msg, ERR_PTR(-E2BIG));
                wake_q_add(wake_q, msr->r_tsk);
            } else {
                /* 直接传递消息给接收者 */
                ipc_update_pid(&msq->q_lrpid, task_pid(msr->r_tsk));
                msq->q_rtime = ktime_get_real_seconds();
                smp_store_release(&msr->r_msg, msg);  /* 无需加锁 */
                wake_q_add(wake_q, msr->r_tsk);
                return 1;
            }
        }
    }
    return 0;  /* 没有等待的接收者，消息入队 */
}
```

---

## 3. 信号量 (sem)

### 3.1 核心数据结构

#### sem - 单个信号量 (sem.c:95-111)

```c
struct sem {
    int         semval;        /* 当前值 */
    struct pid  *sempid;       /* 最后修改的进程 PID */
    spinlock_t  lock;          /* 细粒度锁 */
    struct list_head pending_alter;  /* 等待修改的操作 */
    struct list_head pending_const;  /* 等待只读的操作 */
    time64_t    sem_otime;     /* 最后操作时间 */
};
```

#### sem_array - 信号量数组 (sem.c:114-127)

```c
struct sem_array {
    struct kern_ipc_perm  sem_perm;     /* 权限 */
    time64_t               sem_ctime;    /* 创建/最后修改时间 */
    struct list_head       pending_alter; /* 等待修改的操作 */
    struct list_head       pending_const; /* 等待只读的操作 */
    struct list_head       list_id;       /* 撤销请求链表 */
    int                    sem_nsems;     /* 信号量数量 */
    int                    complex_count; /* 复杂操作计数 */
    unsigned int           use_global_lock; /* 需要全局锁 */

    struct sem             sems[];         /* 信号量数组 */
};
```

#### sem_queue - 等待队列 (sem.c:130-141)

```c
struct sem_queue {
    struct list_head       list;          /* 队列链表 */
    struct task_struct     *sleeper;      /* 睡眠的进程 */
    struct sem_undo        *undo;         /* 撤销结构 */
    struct pid             *pid;          /* 请求进程 PID */
    int                    status;        /* 完成状态 */
    struct sembuf          *sops;         /* 操作数组 */
    struct sembuf          *blocking;     /* 阻塞的操作 */
    int                    nsops;         /* 操作数量 */
    bool                   alter;         /* 是否修改数组 */
    bool                   dupsop;        /* 是否有重复 sem_num */
};
```

#### sem_undo - 进程撤销结构 (sem.c:146-157)

```c
struct sem_undo {
    struct list_head   list_proc;   /* 进程链表 (RCU 保护) */
    struct rcu_head    rcu;         /* RCU 结构 */
    struct sem_undo_list *ulp;      /* 回指到 sem_undo_list */
    struct list_head   list_id;     /* 每个信号量数组的链表 */
    int                semid;       /* 信号量数组标识符 */
    short              semadj[];    /* 调整值数组 (每个信号量一个) */
};
```

### 3.2 信号量操作函数

#### perform_atomic_semop() - 原子信号量操作 (sem.c:719-784)

```c
static int perform_atomic_semop(struct sem_array *sma, struct sem_queue *q)
{
    // 第一次扫描：验证所有操作能否成功
    for (sop = sops; sop < sops + nsops; sop++) {
        curr = &sma->sems[sop->sem_num];
        sem_op = sop->sem_op;
        result = curr->semval;

        if (!sem_op && result)
            goto would_block;  /* 等待零操作但值非零 */

        result += sem_op;
        if (result < 0)
            goto would_block;  /* 会导致负值 */

        if (result > SEMVMX)
            return -ERANGE;  /* 超出最大值 */

        if (sop->sem_flg & SEM_UNDO) {
            int undo = un->semadj[sop->sem_num] - sem_op;
            if (undo < (-SEMAEM - 1) || undo > SEMAEM)
                return -ERANGE;  /* 撤销范围超出 */
        }
    }

    // 第二次扫描：执行实际操作
    for (sop = sops; sop < sops + nsops; sop++) {
        curr = &sma->sems[sop->sem_num];
        sem_op = sop->sem_op;

        if (sop->sem_flg & SEM_UNDO) {
            un->semadj[sop->sem_num] -= sem_op;
        }
        curr->semval += sem_op;
        ipc_update_pid(&curr->sempid, q->pid);
    }

    return 0;  /* 成功 */

would_block:
    q->blocking = sop;
    return sop->sem_flg & IPC_NOWAIT ? -EAGAIN : 1;
}
```

#### __do_semtimedop() - 带超时的信号量操作 (sem.c:1983-2220)

```c
long __do_semtimedop(int semid, struct sembuf *sops,
        unsigned nsops, const struct timespec64 *timeout,
        struct ipc_namespace *ns)
{
    // 1. 参数验证和预处理
    if (nsops < 1 || semid < 0)
        return -EINVAL;
    if (nsops > ns->sc_semopm)
        return -E2BIG;

    // 2. 分析操作类型
    for (sop = sops; sop < sops + nsops; sop++) {
        if (sop->sem_flg & SEM_UNDO)
            undos = true;
        if (sop->sem_op != 0)
            alter = true;
    }

    // 3. 获取/创建撤销结构
    if (undos) {
        un = find_alloc_undo(ns, semid);
        if (IS_ERR(un))
            return PTR_ERR(un);
    }

    // 4. 获取信号量数组并锁定
    sma = sem_obtain_object_check(ns, semid);
    locknum = sem_lock(sma, sops, nsops);

    // 5. 尝试执行原子操作
    error = perform_atomic_semop(sma, &queue);
    if (error == 0) {
        /* 成功 - 更新队列 */
        if (alter)
            do_smart_update(sma, sops, nsops, 1, &wake_q);
        else
            set_semotime(sma, sops);
        sem_unlock(sma, locknum);
        goto out;
    }
    if (error < 0)
        goto out_unlock;  /* 错误 */

    // 6. 需要睡眠等待
    /* 将操作加入相应队列 */
    if (nsops == 1) {
        if (alter)
            list_add_tail(&queue.list, &curr->pending_alter);
        else
            list_add_tail(&queue.list, &curr->pending_const);
    } else {
        /* 多操作需要合并到全局队列 */
        merge_queues(sma);
        if (alter)
            list_add_tail(&queue.list, &sma->pending_alter);
        else
            list_add_tail(&queue.list, &sma->pending_const);
        sma->complex_count++;
    }

    // 7. 睡眠循环
    do {
        __set_current_state(TASK_INTERRUPTIBLE);
        sem_unlock(sma, locknum);
        rcu_read_unlock();

        timed_out = !schedule_hrtimeout_range(exp, ...);

        rcu_read_lock();
        error = READ_ONCE(queue.status);
        if (error != -EINTR)
            goto out;

        locknum = sem_lock(sma, sops, nsops);
        /* 重新检查... */
    } while (error == -EINTR && !signal_pending(current));

    unlink_queue(sma, &queue);
out_unlock:
    sem_unlock(sma, locknum);
out:
    return error;
}
```

### 3.3 细粒度锁定策略 (sem.c:389-458)

```c
static inline int sem_lock(struct sem_array *sma, struct sembuf *sops, int nsops)
{
    // 单操作优化路径
    if (nsops != 1) {
        /* 复杂操作 - 获取全局锁 */
        ipc_lock_object(&sma->sem_perm);
        complexmode_enter(sma);
        return SEM_GLOBAL_LOCK;
    }

    idx = array_index_nospec(sops->sem_num, sma->sem_nsems);
    sem = &sma->sems[idx];

    // 快速路径：检查是否需要全局锁
    if (!READ_ONCE(sma->use_global_lock)) {
        spin_lock(&sem->lock);

        /* 再次检查 (内存屏障) */
        if (!smp_load_acquire(&sma->use_global_lock)) {
            return sops->sem_num;  /* 成功返回单个信号量索引 */
        }
        spin_unlock(&sem->lock);
    }

    /* 慢速路径：获取全局锁 */
    ipc_lock_object(&sma->sem_perm);
    if (sma->use_global_lock == 0) {
        spin_lock(&sem->lock);
        ipc_unlock_object(&sma->sem_perm);
        return sops->sem_num;
    }
    return SEM_GLOBAL_LOCK;
}
```

### 3.4 退出时撤销 (exit_sem) (sem.c:2335-2446)

进程退出时自动撤销其持有的信号量调整:

```c
void exit_sem(struct task_struct *tsk)
{
    struct sem_undo_list *ulp = tsk->sysvsem.undo_list;
    if (!ulp)
        return;

    for (;;) {
        /* 遍历所有撤销条目 */
        un = list_entry_rcu(ulp->list_proc.next, struct sem_undo, list_proc);
        if (&un->list_proc == &ulp->list_proc)
            break;

        sma = sem_obtain_object_check(ns, semid);
        sem_lock(sma, NULL, -1);

        /* 执行撤销调整 */
        for (i = 0; i < sma->sem_nsems; i++) {
            if (un->semadj[i]) {
                sem = &sma->sems[i];
                sem->semval += un->semadj[i];
                /* 限制范围 */
                if (sem->semval < 0)
                    sem->semval = 0;
                if (sem->semval > SEMVMX)
                    sem->semval = SEMVMX;
            }
        }
        /* 唤醒等待的进程 */
        do_smart_update(sma, NULL, 0, 1, &wake_q);
        sem_unlock(sma, -1);
        kvfree_rcu(un, rcu);
    }
}
```

---

## 4. 共享内存 (shm)

### 4.1 核心数据结构

#### shmid_kernel - 共享内存内核结构 (shm.c:54-79)

```c
struct shmid_kernel /* private to the kernel */
{
    struct kern_ipc_perm  shm_perm;     /* 权限结构 */
    struct file           *shm_file;     /* 关联的文件 */
    unsigned long         shm_nattch;    /* 当前附加计数 */
    unsigned long         shm_segsz;     /* 段大小 */
    time64_t             shm_atim;       /* 最后附加时间 */
    time64_t             shm_dtim;       /* 最后分离时间 */
    time64_t             shm_ctim;       /* 最后改变时间 */
    struct pid           *shm_cprid;     /* 创建者 PID */
    struct pid           *shm_lprid;     /* 最后操作者 PID */
    struct ucounts       *mlock_ucounts; /* mlock 计数 */
    struct task_struct   *shm_creator;   /* 创建者任务 */
    struct list_head     shm_clist;      /* 创建者链表 */
    struct ipc_namespace *ns;            /* 命名空间 */
};
```

#### shm_file_data - 共享内存文件数据 (shm.c:85-92)

```c
struct shm_file_data {
    int id;
    struct ipc_namespace *ns;
    struct file *file;
    const struct vm_operations_struct *vm_ops;
};
```

### 4.2 关键函数分析

#### newseg() - 创建新共享内存段 (shm.c:702-812)

```c
static int newseg(struct ipc_namespace *ns, struct ipc_params *params)
{
    key_t key = params->key;
    int shmflg = params->flg;
    size_t size = params->u.size;

    // 1. 参数验证
    if (size < SHMMIN || size > ns->shm_ctlmax)
        return -EINVAL;
    if (ns->shm_tot + numpages > ns->shm_ctlall)
        return -ENOSPC;

    // 2. 分配 shmid_kernel 结构
    shp = kmalloc_obj(*shp, GFP_KERNEL_ACCOUNT);

    // 3. 创建底层文件
    if (shmflg & SHM_HUGETLB) {
        /* 大页共享内存 */
        file = hugetlb_file_setup(name, hugesize, acctflag,
                HUGETLB_SHMFS_INODE, ...);
    } else {
        /* 传统共享内存 */
        file = shmem_kernel_file_setup(name, size, acctflag);
    }

    // 4. 初始化共享内存结构
    shp->shm_cprid = get_pid(task_tgid(current));
    shp->shm_lprid = NULL;
    shp->shm_atim = shp->shm_dtim = 0;
    shp->shm_ctim = ktime_get_real_seconds();
    shp->shm_segsz = size;
    shp->shm_nattch = 0;
    shp->shm_file = file;
    shp->shm_creator = current;

    // 5. 添加到 IPC 系统
    error = ipc_addid(&shm_ids(ns), &shp->shm_perm, ns->shm_ctlmni);

    task_lock(current);
    list_add(&shp->shm_clist, &current->sysvshm.shm_clist);
    task_unlock(current);

    file_inode(file)->i_ino = shp->shm_perm.id;  /* 便于 /proc/pid/maps 显示 */
    ns->shm_tot += numpages;
}
```

#### do_shmat() - 附加共享内存 (shm.c:1519-1691)

```c
long do_shmat(int shmid, char __user *shmaddr, int shmflg,
          ulong *raddr, unsigned long shmlba)
{
    // 1. 获取共享内存结构
    rcu_read_lock();
    shp = shm_obtain_object_check(ns, shmid);

    ipc_lock_object(&shp->shm_perm);

    // 2. 获取文件引用
    base = get_file(shp->shm_file);
    shp->shm_nattch++;
    size = i_size_read(file_inode(base));
    ipc_unlock_object(&shp->shm_perm);
    rcu_read_unlock();

    // 3. 创建文件副本用于映射
    sfd = kzalloc_obj(*sfd);
    file = alloc_file_clone(base, f_flags, ...);

    sfd->id = shp->shm_perm.id;
    sfd->ns = get_ipc_ns(ns);
    sfd->file = base;
    file->private_data = sfd;

    // 4. 执行 mmap
    addr = do_mmap(file, addr, size, prot, flags, 0, 0, ...);
    *raddr = addr;

    // 5. 更新附加计数
    down_write(&shm_ids(ns).rwsem);
    shp = shm_lock(ns, shmid);
    shp->shm_nattch--;

    if (shm_may_destroy(shp))
        shm_destroy(ns, shp);
    else
        shm_unlock(shp);
}
```

### 4.3 shmctl 操作 (shm.c:993-1041)

```c
static int shmctl_down(struct ipc_namespace *ns, int shmid, int cmd,
               struct shmid64_ds *shmid64)
{
    down_write(&shm_ids(ns).rwsem);
    rcu_read_lock();

    ipcp = ipcctl_obtain_check(ns, &shm_ids(ns), shmid, cmd, ...);
    shp = container_of(ipcp, struct shmid_kernel, shm_perm);

    switch (cmd) {
    case IPC_RMID:
        ipc_lock_object(&shp->shm_perm);
        do_shm_rmid(ns, ipcp);  /* 标记销毁或直接释放 */
        goto out_up;
    case IPC_SET:
        ipc_lock_object(&shp->shm_perm);
        err = ipc_update_perm(&shmid64->shm_perm, ipcp);
        if (err)
            goto out_unlock0;
        shp->shm_ctim = ktime_get_real_seconds();
        break;
    }
}
```

### 4.4 共享内存销毁逻辑

```c
static void do_shm_rmid(struct ipc_namespace *ns, struct kern_ipc_perm *ipcp)
{
    shp = container_of(ipcp, struct shmid_kernel, shm_perm);

    if (shp->shm_nattch) {
        /* 还有进程附加，标记为待销毁 */
        shp->shm_perm.mode |= SHM_DEST;
        ipc_set_key_private(&shm_ids(ns), &shp->shm_perm);
        shm_unlock(shp);
    } else
        /* 无附加，直接销毁 */
        shm_destroy(ns, shp);
}

static bool shm_may_destroy(struct shmid_kernel *shp)
{
    return (shp->shm_nattch == 0) &&
           (shp->ns->shm_rmid_forced ||
            (shp->shm_perm.mode & SHM_DEST));
}
```

---

## 5. POSIX 消息队列 (mqueue)

### 5.1 核心数据结构

#### mqueue_inode_info - mqueue inode 信息 (mqueue.c:133-155)

```c
struct mqueue_inode_info {
    spinlock_t            lock;           /* 保护此结构 */
    struct inode          vfs_inode;      /* VFS inode */
    wait_queue_head_t     wait_q;         /* 等待队列 */

    struct rb_root        msg_tree;       /* 消息红黑树 */
    struct rb_node        *msg_tree_rightmost;  /* 最右节点 */
    struct posix_msg_tree_node *node_cache;     /* 节点缓存 */

    struct mq_attr        attr;           /* 队列属性 */

    struct sigevent       notify;         /* 通知配置 */
    struct pid            *notify_owner;  /* 通知所有者 PID */
    u32                   notify_self_exec_id;
    struct user_namespace *notify_user_ns;
    struct sock           *notify_sock;   /* netlink 套接字 */
    struct sk_buff        *notify_cookie; /* 通知 cookie */

    /* 等待发送和接收的进程 */
    struct ext_wait_queue e_wait_q[2];   /* [0]=SEND, [1]=RECV */

    unsigned long         qsize;          /* 队列内存大小 */
};
```

#### posix_msg_tree_node - 消息树节点 (mqueue.c:60-64)

```c
struct posix_msg_tree_node {
    struct rb_node    rb_node;       /* 红黑树节点 */
    struct list_head  msg_list;      /* 同优先级的消息链表 */
    int               priority;      /* 优先级 */
};
```

#### ext_wait_queue - 等待队列条目 (mqueue.c:126-131)

```c
struct ext_wait_queue {
    struct task_struct *task;        /* 等待任务 */
    struct list_head   list;        /* 链表 */
    struct msg_msg     *msg;         /* 消息指针 */
    int                state;        /* STATE_NONE 或 STATE_READY */
};
```

### 5.2 消息插入和获取

#### msg_insert() - 插入消息到红黑树 (mqueue.c:190-230)

```c
static int msg_insert(struct msg_msg *msg, struct mqueue_inode_info *info)
{
    struct rb_node **p, *parent = NULL;
    struct posix_msg_tree_node *leaf;
    bool rightmost = true;

    p = &info->msg_tree.rb_node;
    while (*p) {
        parent = *p;
        leaf = rb_entry(parent, struct posix_msg_tree_node, rb_node);

        if (leaf->priority == msg->m_type)
            goto insert_msg;
        else if (msg->m_type < leaf->priority) {
            p = &(*p)->rb_left;
            rightmost = false;
        } else
            p = &(*p)->rb_right;
    }

    /* 需要新节点 */
    if (info->node_cache)
        leaf = info->node_cache;
    else
        leaf = kmalloc_obj(*leaf, GFP_ATOMIC);

    leaf->priority = msg->m_type;
    if (rightmost)
        info->msg_tree_rightmost = &leaf->rb_node;

    rb_link_node(&leaf->rb_node, parent, p);
    rb_insert_color(&leaf->rb_node, &info->msg_tree);

insert_msg:
    info->attr.mq_curmsgs++;
    info->qsize += msg->m_ts;
    list_add_tail(&msg->m_list, &leaf->msg_list);
    return 0;
}
```

#### msg_get() - 从队列获取消息 (mqueue.c:247-287)

```c
static inline struct msg_msg *msg_get(struct mqueue_inode_info *info)
{
    struct rb_node *parent = NULL;
    struct posix_msg_tree_node *leaf;
    struct msg_msg *msg;

try_again:
    /* 获取最右节点 (最高优先级) */
    parent = info->msg_tree_rightmost;
    if (!parent)
        return NULL;

    leaf = rb_entry(parent, struct posix_msg_tree_node, rb_node);
    if (unlikely(list_empty(&leaf->msg_list))) {
        /* 空节点，删除并重试 */
        msg_tree_erase(leaf, info);
        goto try_again;
    }

    msg = list_first_entry(&leaf->msg_list, struct msg_msg, m_list);
    list_del(&msg->m_list);
    if (list_empty(&leaf->msg_list))
        msg_tree_erase(leaf, info);

    info->attr.mq_curmsgs--;
    info->qsize -= msg->m_ts;
    return msg;
}
```

### 5.3 mq_open 实现 (mqueue.c:911-928)

```c
static int do_mq_open(const char __user *u_name, int oflag, umode_t mode,
              struct mq_attr *attr)
{
    struct vfsmount *mnt = current->nsproxy->ipc_ns->mq_mnt;
    int fd;

    CLASS(filename, name)(u_name);

    fd = mqueue_file_open(name, mnt, oflag, ...);
    return fd;
}

static struct file *mqueue_file_open(...)
{
    dentry = start_creating_noperm(mnt->mnt_root, &QSTR(name->name));
    ret = prepare_open(dentry, oflag, ro, mode, name, attr);

    if (!ret) {
        const struct path path = { .mnt = mnt, .dentry = dentry };
        file = dentry_open(&path, oflag, current_cred());
    }
    end_creating(dentry);
    return file;
}
```

### 5.4 管道化发送/接收

#### pipelined_send() - 直接传递消息给接收者 (mqueue.c:1010-1017)

```c
static inline void pipelined_send(struct wake_q_head *wake_q,
                  struct mqueue_inode_info *info,
                  struct msg_msg *message,
                  struct ext_wait_queue *receiver)
{
    receiver->msg = message;
    __pipelined_op(wake_q, info, receiver);
}

static inline void __pipelined_op(struct wake_q_head *wake_q,
                  struct mqueue_inode_info *info,
                  struct ext_wait_queue *this)
{
    list_del(&this->list);
    task = get_task_struct(this->task);

    /* 内存屏障确保状态设置在唤醒之前 */
    smp_store_release(&this->state, STATE_READY);
    wake_q_add_safe(wake_q, task);
}
```

#### pipelined_receive() - 直接从发送者获取消息 (mqueue.c:1021-1035)

```c
static inline void pipelined_receive(struct wake_q_head *wake_q,
                     struct mqueue_inode_info *info)
{
    struct ext_wait_queue *sender = wq_get_first_waiter(info, SEND);

    if (!sender) {
        wake_up_interruptible(&info->wait_q);
        return;
    }
    if (msg_insert(sender->msg, info))
        return;

    __pipelined_op(wake_q, info, sender);
}
```

### 5.5 通知机制 (mqueue.c:777-836)

```c
static void __do_notify(struct mqueue_inode_info *info)
{
    /* 当队列从空变为非空且有注册进程时调用 */
    if (info->notify_owner &&
        info->attr.mq_curmsgs == 1) {
        switch (info->notify.sigev_notify) {
        case SIGEV_NONE:
            break;
        case SIGEV_SIGNAL:
            /* 发送信号给注册进程 */
            do_send_sig_info(info->notify.sigev_signo, &sig_i, task, ...);
            break;
        case SIGEV_THREAD:
            /* 通过 netlink 通知 */
            netlink_sendskb(info->notify_sock, info->notify_cookie);
            break;
        }
        /* 通知后注销 */
        put_pid(info->notify_owner);
        put_user_ns(info->notify_user_ns);
        info->notify_owner = NULL;
    }
    wake_up(&info->wait_q);
}
```

---

## 6. IPC 通用框架

### 6.1 ipc_ops - IPC 操作向量 (util.h:105-109)

```c
struct ipc_ops {
    int (*getnew)(struct ipc_namespace *, struct ipc_params *);
    int (*associate)(struct kern_ipc_perm *, int);
    int (*more_checks)(struct kern_ipc_perm *, struct ipc_params *);
};
```

### 6.2 ipc_addid() - 添加 IPC 标识符 (util.c:278-327)

```c
int ipc_addid(struct ipc_ids *ids, struct kern_ipc_perm *new, int limit)
{
    kuid_t euid;
    kgid_t egid;
    int idx;

    /* 初始化引用计数 */
    refcount_set(&new->refcount, 1);

    if (limit > ipc_mni)
        limit = ipc_mni;
    if (ids->in_use >= limit)
        return -ENOSPC;

    idr_preload(GFP_KERNEL);
    spin_lock_init(&new->lock);
    rcu_read_lock();
    spin_lock(&new->lock);

    current_euid_egid(&euid, &egid);
    new->cuid = new->uid = euid;
    new->gid = new->cgid = egid;
    new->deleted = false;

    idx = ipc_idr_alloc(ids, new);
    idr_preload_end();

    if (idx >= 0 && new->key != IPC_PRIVATE) {
        err = rhashtable_insert_fast(&ids->key_ht, &new->khtnode,
                     ipc_kht_params);
        if (err < 0) {
            idr_remove(&ids->ipcs_idr, idx);
            idx = err;
        }
    }

    ids->in_use++;
    return idx;
}
```

### 6.3 ipc_rmid() - 移除 IPC 标识符 (util.c:497-512)

```c
void ipc_rmid(struct ipc_ids *ids, struct kern_ipc_perm *ipcp)
{
    int idx = ipcid_to_idx(ipcp->id);

    idr_remove(&ids->ipcs_idr, idx);
    ipc_kht_remove(ids, ipcp);
    ids->in_use--;
    ipcp->deleted = true;  /* 标记为已删除 */

    if (unlikely(idx == ids->max_idx)) {
        /* 更新最大索引 */
        idx = ids->max_idx - 1;
        if (idx >= 0)
            idx = ipc_search_maxidx(ids, idx);
        ids->max_idx = idx;
    }
}
```

### 6.4 ipcget() - 统一获取 IPC 对象 (util.c:670-677)

```c
int ipcget(struct ipc_namespace *ns, struct ipc_ids *ids,
        const struct ipc_ops *ops, struct ipc_params *params)
{
    if (params->key == IPC_PRIVATE)
        return ipcget_new(ns, ids, ops, params);  /* 创建新对象 */
    else
        return ipcget_public(ns, ids, ops, params);  /* 查找或创建 */
}
```

### 6.5 ipc_lock_object() - 锁定 IPC 对象 (util.h:208-211)

```c
static inline void ipc_lock_object(struct kern_ipc_perm *perm)
{
    spin_lock(&perm->lock);
}
```

### 6.6 ipc_obtain_object_idr() - 通过 IDR 获取对象 (util.c:626-636)

```c
struct kern_ipc_perm *ipc_obtain_object_idr(struct ipc_ids *ids, int id)
{
    struct kern_ipc_perm *out;
    int idx = ipcid_to_idx(id);

    out = idr_find(&ids->ipcs_idr, idx);
    if (!out)
        return ERR_PTR(-EINVAL);

    return out;
}
```

### 6.7 命名空间初始化

```c
void ipc_init_ids(struct ipc_ids *ids)
{
    ids->in_use = 0;
    ids->seq = 0;
    init_rwsem(&ids->rwsem);
    rhashtable_init(&ids->key_ht, &ipc_kht_params);
    idr_init(&ids->ipcs_idr);
    ids->max_idx = -1;
    ids->last_idx = -1;
}

static const struct rhashtable_params ipc_kht_params = {
    .head_offset    = offsetof(struct kern_ipc_perm, khtnode),
    .key_offset     = offsetof(struct kern_ipc_perm, key),
    .key_len        = sizeof_field(struct kern_ipc_perm, key),
    .automatic_shrinking = true,
};
```

---

## 7. 架构图

### 7.1 IPC 子系统整体架构

```
+------------------------------------------------------------------+
|                         用户空间                                  |
|  +------------+  +------------+  +------------+  +------------+  |
|  | msgget()  |  | semget()   |  | shmget()   |  | mq_open()  |  |
|  | msgsnd()  |  | semop()    |  | shmat()    |  | mq_send()  |  |
|  | msgrcv()  |  | semtimedop |  | shmdt()    |  | mq_receive |  |
|  | msgctl()  |  | semctl()   |  | shmctl()   |  | mq_notify  |  |
|  +------------+  +------------+  +------------+  +------------+  |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                    IPC 系统调用接口                               |
|  +------------+  +------------+  +------------+  +------------+  |
|  |  msg.c    |  |  sem.c    |  |  shm.c    |  | mqueue.c  |  |
|  +------------+  +------------+  +------------+  +------------+  |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                     IPC 通用框架 (util.c)                        |
|  +------------------------------------------------------------+  |
|  |  ipc_addid() | ipc_rmid() | ipcget() | ipc_lock_object() |  |
|  |  ipc_obtain_object_idr() | ipcperms() | ipc_update_perm() |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                       数据结构层                                 |
|  +------------------------------------------------------------+  |
|  |  struct kern_ipc_perm    |  struct ipc_ids  |  IDR 树       |  |
|  |  struct ipc_namespace    |  键值哈希表      |  RCU 机制     |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                      底层存储/文件系统                           |
|  +------------+  +------------+  +------------+  +------------+  |
|  |  消息链表  |  | 信号量数组 |  | shmem文件  |  | mqueuefs   |  |
|  |  (list)   |  | (sem[])   |  | (/dev/zero)|  | (ramfs)   |  |
|  +------------+  +------------+  +------------+  +------------+  |
+------------------------------------------------------------------+
```

### 7.2 消息队列架构

```
                    消息队列 (msg_queue)
                    +--------------------+
                    | q_perm             | <---- kern_ipc_perm
                    | q_messages         | ----> [msg_msg1] -> [msg_msg2] -> ...
                    | q_receivers        | ----> [msg_receiver1] -> ...
                    | q_senders          | ----> [msg_sender1] -> ...
                    | q_cbytes, q_qnum   |
                    +--------------------+
                              ^
                              |
        +---------------------+---------------------+
        |                     |                     |
   msgsnd()             msgrcv()               msgctl()
   (发送消息)           (接收消息)              (控制操作)
        |                     |                     |
        v                     v                     v
   do_msgsnd()           do_msgrcv()           msgctl_down()
        |                     |                     |
        v                     v                     v
   1. load_msg()        1. find_msg()         IPC_RMID: freeque()
   2. 检查队列空间       2. 权限检查            IPC_SET: 更新权限
   3. pipelined_send()  3. pipelined_send()   IPC_INFO: 返回信息
      或入队                或从队列取
   4. 唤醒接收者         4. 唤醒发送者
```

### 7.3 信号量架构

```
                    信号量数组 (sem_array)
                    +--------------------+
                    | sem_perm           | <---- kern_ipc_perm
                    | sems[]            | ----> [sem0] [sem1] [sem2] ...
                    |   .semval         |        |     |     |
                    |   .sempid        |        v     v     v
                    |   .pending_alter  |     等待操作链表
                    |   .pending_const  |
                    | pending_alter     | ----> [sem_queue] -> ...
                    | pending_const     | ----> [sem_queue] -> ...
                    | complex_count     |
                    +--------------------+
                              ^
                              |
        +---------------------+---------------------+
        |                     |                     |
   semop()                semtimedop()           semctl()
   (快速路径)             (带超时)               (控制操作)
        |                     |                     |
        v                     v                     v
   __do_semtimedop()      __do_semtimedop()     semctl_main()
        |                     |                     |           semctl_down()
        v                     v                     v                |
   sem_lock()            sem_lock()            读取/设置         IPC_RMID
   (单信号量快速锁)       (可能需要全局锁)       信号量值          IPC_SET
        |                     |                     |
        v                     v                     v
   perform_atomic_       合并到全局队列         唤醒等待进程
   semop()               睡眠等待               exit_sem() 撤销
```

### 7.4 共享内存架构

```
                    共享内存 (shmid_kernel)
                    +--------------------+
                    | shm_perm           | <---- kern_ipc_perm
                    | shm_file           | ----> struct file
                    | shm_nattch         |      (shmem_kernel_file_setup)
                    | shm_segsz          |            |
                    | shm_atim/dtim/ctim |            v
                    | shm_creator        |      底层 shmem 文件
                    +--------------------+      (页缓存/大页)
                              ^
                              |
        +---------------------+---------------------+
        |                     |                     |
   shmget()               shmat()                shmctl()
   (创建/获取)            (附加到地址空间)        (控制操作)
        |                     |                     |
        v                     v                     v
   newseg()               do_shmat()             shmctl_down()
        |                     |                     |
        v                     v                     v
   shmem_file_setup()     mmap()                 IPC_RMID: do_shm_rmid()
   hugetlb_file_setup()   创建 VMA               IPC_SET: 更新权限
   (大页支持)             更新 nattch             SHM_LOCK/UNLOCK
```

### 7.5 POSIX 消息队列架构

```
                    POSIX 消息队列文件系统
                    +--------------------+
                    | mqueue_inode_info  |
                    |   msg_tree (RB)    | ----> [节点1] --> [节点2]
                    |   node_cache       |            |
                    |   e_wait_q[SEND]   | ----> [ext_wait_queue]
                    |   e_wait_q[RECV]   | ----> [ext_wait_queue]
                    |   attr (mq_attr)   |
                    |   notify_*         |
                    +--------------------+
                              ^
                              |
        +---------------------+---------------------+
        |                     |                     |
   mq_open()              mq_send()              mq_receive()
   (打开队列)             (发送消息)              (接收消息)
        |                     |                     |
        v                     v                     v
   do_mq_open()           do_mq_timedsend()      do_mq_timedreceive()
        |                     |                     |
        v                     v                     v
   文件系统挂载           检查空间                 检查消息
   /dev/mqueue           pipelined_send()        pipelined_receive()
   dentry 创建              或入队                  或从队列取
                              |                     |
                              v                     v
                         唤醒接收者                唤醒发送者
```

### 7.6 锁定层次结构

```
                    锁定层次
                    =============

    层级 1: rwsem (ipc_ids.rwsem)
    - 创建/删除/遍历 IPC 对象时持有
    - 写锁: ipc_addid(), ipc_rmid()
    - 读锁: /proc/sysvipc/ 读取

    层级 2: spinlock (kern_ipc_perm.lock)
    - 单个 IPC 对象操作时持有
    - 通过 ipc_lock_object() 获取

    层级 3: 细粒度锁 (信号量特有)
    - sem->lock (单信号量锁)
    - 当 use_global_lock > 0 时需要全局锁

    RCU 保护:
    - 对象查找 (read-side)
    - 对象释放 (通过 call_rcu)
```

### 7.7 消息流 - 管道化操作

```
    发送者                               接收者
      |                                   |
      |  msgsnd()                         |
      |  +-------------------+             |
      |  | 检查队列空间      |             |
      |  | 满?               |             |
      |  +--------+----------+             |
      |           |                       |
      |          是                       |
      |           v                       |
      |  ss_add() 加入 q_senders          |
      |  schedule() 睡眠                  |
      |                                   |
      |                                   |  msgrcv()
      |                                   |  +----------------+
      |                                   |  | find_msg()    |
      |                                   |  | 没有消息?      |
      |                                   |  +-------+--------+
      |                                   |          |
      |                                   |         是
      |                                   |          v
      |                                   |  msr_add() 加入 q_receivers
      |                                   |  schedule() 睡眠
      |                                   |
      |<---- 唤醒 ----+------------------->|
      |                                   |
      |  再次检查空间                      |  再次检查消息
      |  +-------------------+            |  +----------------+
      |  | 空间足够?          |            |  | 找到匹配消息?   |
      |  +--------+----------+            |  +-------+--------+
      |           |                       |          |
      |          否                       |          是
      |           v                       |          v
      |  继续睡眠                  pipelined_send()
      |                         (直接传递消息引用)
      |                                   |  消息直接传递
      |                                   |  不经过队列
      v                                   v
```

---

## 附录: 关键常量

| 常量 | 描述 | 典型值 |
|------|------|--------|
| SEMVMX | 信号量最大值 | 32767 |
| SEMAEM | SEM_UNDO 最大值 | 16384 |
| SEMMSL | 每个信号量集的信号量数上限 | 32000 |
| SEMMNI | 系统信号量集数量上限 | 128 |
| SEMMNS | 系统信号量总数上限 | 32000 |
| SEMOPM | 每次 semop() 的最大操作数 | 1000 |
| MSGMAX | 单条消息最大字节数 | 8192 |
| MSGMNB | 单个队列最大字节数 | 16384 |
| MSGMNI | 系统消息队列数量上限 | 32000 |
| SHMMAX | 共享内存段最大大小 | 0x2000000 (32MB) |
| SHMMIN | 共享内存段最小大小 | 1 |
| SHMMNI | 系统共享内存段数量上限 | 4096 |
| SHMALL | 系统共享内存总大小上限 | 0x2000000 |

---

## 参考

- `/Users/sphinx/github/linux/ipc/msg.c` - 消息队列实现
- `/Users/sphinx/github/linux/ipc/sem.c` - 信号量实现
- `/Users/sphinx/github/linux/ipc/shm.c` - 共享内存实现
- `/Users/sphinx/github/linux/ipc/mqueue.c` - POSIX 消息队列实现
- `/Users/sphinx/github/linux/ipc/util.c` - IPC 通用框架
- `/Users/sphinx/github/linux/ipc/util.h` - IPC 通用框架头文件
- `include/linux/msg.h` - 消息结构定义
- `include/uapi/linux/msg.h` - 用户空间消息 API
- `include/uapi/linux/sem.h` - 用户空间信号量 API
- `include/uapi/linux/shm.h` - 用户空间共享内存 API
- `include/linux/ipc_namespace.h` - IPC 命名空间
