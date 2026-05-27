# Linux 内核 IPC 子系统深度分析文档

**版本**: R1
**源码版本**: Linux Kernel Latest (master branch)
**分析日期**: 2026-04-26

---

## 目录

1. [消息队列算法](#1-消息队列算法)
2. [信号量 Undo 机制](#2-信号量-undo-机制)
3. [共享内存 mmap](#3-共享内存-mmap)
4. [POSIX mqueue 通知](#4-posix-mqueue-通知)
5. [IPC 通用框架](#5-ipc-通用框架)
6. [性能优化](#6-性能优化)

---

## 1. 消息队列算法

### 1.1 msg_queue 结构与链表组织

**文件**: `/Users/sphinx/github/linux/ipc/msg.c`

```c
// 行 49-63: msg_queue 结构定义
struct msg_queue {
    struct kern_ipc_perm q_perm;      // IPC 权限基础结构
    time64_t q_stime;                  // 最后 msgsnd 时间
    time64_t q_rtime;                  // 最后 msgrcv 时间
    time64_t q_ctime;                  // 最后改变时间
    unsigned long q_cbytes;            // 队列当前字节数
    unsigned long q_qnum;              // 队列消息数
    unsigned long q_qbytes;            // 队列最大字节数
    struct pid *q_lspid;               // 最后发送进程 PID
    struct pid *q_lrpid;               // 最后接收进程 PID

    struct list_head q_messages;       // 消息链表头 (行 60)
    struct list_head q_receivers;      // 等待接收的进程链表 (行 61)
    struct list_head q_senders;        // 等待发送的进程链表 (行 62)
} __randomize_layout;
```

**数据结构关系图**:

```
msg_queue
+-------------------+
| kern_ipc_perm     |  (内含 spinlock, key, id, refcount, deleted)
+-------------------+
| q_stime/q_rtime   |  时间戳
+-------------------+
| q_cbytes/q_qnum   |  队列统计
+-------------------+
| q_lspid/q_lrpid   |  PID 追踪
+-------------------+
| q_messages        |-----> [msg_msg] <----> [msg_msg] <----> ...
| q_receivers       |-----> [msg_receiver] <----> [msg_receiver]
| q_senders         |-----> [msg_sender] <----> [msg_sender]
+-------------------+
```

**关键设计决策**:
- 消息队列使用**双向链表**存储消息 (`list_head`)
- 接收者和发送者分别使用独立的等待队列
- `__randomize_layout` 属性防止缓冲区溢出攻击

### 1.2 msgsnd() 完整流程

**函数**: `do_msgsnd()` (行 848-959)

```c
// 行 848-959: msgsnd 核心逻辑
long do_msgsnd(int msqid, long mtype, void __user *mtext, size_t msgsz, int msgflg)
{
    struct msg_queue *msq;
    struct msg_msg *msg;
    int err;
    struct ipc_namespace *ns;
    DEFINE_WAKE_Q(wake_q);

    ns = current->nsproxy->ipc_ns;

    // ========== 1. 参数验证 ==========
    // 行 859-862: 基本参数检查
    if (msgsz > ns->msg_ctlmax || (long) msgsz < 0 || msqid < 0)
        return -EINVAL;
    if (mtype < 1)  // POSIX 要求 mtype 必须 > 0
        return -EINVAL;

    // ========== 2. 消息复制 ==========
    // 行 864-869: 从用户空间复制消息
    msg = load_msg(mtext, msgsz);  // 使用 copy_from_user 复制消息
    if (IS_ERR(msg))
        return PTR_ERR(msg);
    msg->m_type = mtype;           // 设置消息类型
    msg->m_ts = msgsz;             // 设置消息大小

    // ========== 3. RCU 保护查找 ==========
    // 行 871-876: 获取消息队列
    rcu_read_lock();
    msq = msq_obtain_object_check(ns, msqid);
    if (IS_ERR(msq)) {
        err = PTR_ERR(msq);
        goto out_unlock1;
    }

    // ========== 4. 锁定对象 ==========
    // 行 878: 获取自旋锁
    ipc_lock_object(&msq->q_perm);

    // ========== 5. 主循环: 等待队列可用空间 ==========
    // 行 880-934: 等待可用空间或 IPC_NOWAIT
    for (;;) {
        struct msg_sender s;

        // 安全检查: 权限验证
        err = -EACCES;
        if (ipcperms(ns, &msq->q_perm, S_IWUGO))
            goto out_unlock0;

        // 检查队列是否被删除 (RMID 竞态)
        if (!ipc_valid_object(&msq->q_perm)) {
            err = -EIDRM;
            goto out_unlock0;
        }

        // 安全检查: SELinux 验证
        err = security_msg_queue_msgsnd(&msq->q_perm, msg, msgflg);
        if (err)
            goto out_unlock0;

        // 检查队列是否有足够空间
        if (msg_fits_inqueue(msq, msgsz))  // 行 897
            break;

        // 队列满: 根据 msgflg 决定阻塞或返回
        if (msgflg & IPC_NOWAIT) {
            err = -EAGAIN;
            goto out_unlock0;
        }

        // ========== 6. 阻塞等待: 添加到发送者队列 ==========
        // 行 906-933: 准备阻塞
        ss_add(msq, &s, msgsz);  // 添加到 q_senders

        // 获取引用防止 use-after-free
        if (!ipc_rcu_getref(&msq->q_perm)) {
            err = -EIDRM;
            goto out_unlock0;
        }

        // 释放锁并调度
        ipc_unlock_object(&msq->q_perm);
        rcu_read_unlock();
        schedule();  // 让出 CPU

        // 重新获取锁
        rcu_read_lock();
        ipc_lock_object(&msq->q_perm);
        ipc_rcu_putref(&msq->q_perm, msg_rcu_free);

        // 竞态检查: 队列是否在等待期间被删除
        if (!ipc_valid_object(&msq->q_perm)) {
            err = -EIDRM;
            goto out_unlock0;
        }
        ss_del(&s);  // 从等待队列移除

        // 信号打断检查
        if (signal_pending(current)) {
            err = -ERESTARTNOHAND;
            goto out_unlock0;
        }
    }

    // ========== 7. 更新队列状态 ==========
    // 行 936-946: 发送消息
    ipc_update_pid(&msq->q_lspid, task_tgid(current));
    msq->q_stime = ktime_get_real_seconds();

    // ========== 8. 管道化发送优化 ==========
    // 行 939-946: pipelined_send 或直接入队
    if (!pipelined_send(msq, msg, &wake_q)) {
        // 没有等待的接收者，直接添加到队列
        list_add_tail(&msg->m_list, &msq->q_messages);
        msq->q_cbytes += msgsz;
        msq->q_qnum++;
        percpu_counter_add_local(&ns->percpu_msg_bytes, msgsz);
        percpu_counter_add_local(&ns->percpu_msg_hdrs, 1);
    }

    err = 0;
    msg = NULL;  // 避免在 out_unlock 中释放

out_unlock0:
    ipc_unlock_object(&msq->q_perm);
    wake_up_q(&wake_q);  // 唤醒等待的接收者
out_unlock1:
    rcu_read_unlock();
    if (msg != NULL)
        free_msg(msg);
    return err;
}
```

**msgsnd() 算法流程图**:

```
                    msgsnd() 开始
                         |
                         v
                 +---------------+
                 | 参数验证      |
                 | mtype >= 1    |
                 | msgsz <= max  |
                 +---------------+
                         |
                         v
                 +---------------+
                 | load_msg()    |  <-- 复制用户空间消息
                 +---------------+
                         |
                         v
                 +---------------+
                 | rcu_read_lock |
                 | 获取 msq      |
                 +---------------+
                         |
                         v
                 +---------------+
                 | ipc_lock()    |
                 +---------------+
                         |
                         v
              +------------------+
              | 队列有空间?      |
              +------------------+
                /              \
               No               Yes
               /                 \
              v                   v
        +------------+      +----------------+
        | IPC_NOWAIT |      | pipelined_send |
        | ?          |      +----------------+
        +------------+            |
          /      \               v
         /        \        +---------------+
        /          \       | 有等待接收者?  |
       No          Yes     +---------------+
       /            \       /            \
      /              \     No            Yes
     v                v     /              \
+------------+        |      v                v
| ss_add()   |        |  +--------+    +--------+
| 阻塞发送者  |        |  | 入队   |    | 直接传递|
+------------+        |  +--------+    | 消息    |
     |                |      |          +--------+
     v                |      v                |
   schedule()         |   __do_notify()         |
     |                |      |                 |
     v                |      v                 v
   唤醒后            |   wake_up_q()      接收者获取
 重新检查            |                     消息并返回
     |                |
     v                v
```

### 1.3 msgrcv() 完整流程

**函数**: `do_msgrcv()` (行 1098-1262)

```c
// 行 1098-1262: msgrcv 核心逻辑
static long do_msgrcv(int msqid, void __user *buf, size_t bufsz,
                      long msgtyp, int msgflg,
                      long (*msg_handler)(void __user *, struct msg_msg *, size_t))
{
    int mode;
    struct msg_queue *msq;
    struct ipc_namespace *ns;
    struct msg_msg *msg, *copy = NULL;
    DEFINE_WAKE_Q(wake_q);

    ns = current->nsproxy->ipc_ns;

    // ========== 1. 参数验证 ==========
    // 行 1109-1110
    if (msqid < 0 || (long) bufsz < 0)
        return -EINVAL;

    // ========== 2. 消息复制模式 (checkpoint/restore) ==========
    // 行 1112-1118
    if (msgflg & MSG_COPY) {
        if ((msgflg & MSG_EXCEPT) || !(msgflg & IPC_NOWAIT))
            return -EINVAL;
        copy = prepare_copy(buf, min_t(size_t, bufsz, ns->msg_ctlmax));
        if (IS_ERR(copy))
            return PTR_ERR(copy);
    }

    // ========== 3. 模式转换 ==========
    // 行 1119: 将 msgflg 转换为内部搜索模式
    mode = convert_mode(&msgtyp, msgflg);
    // convert_mode 逻辑 (行 1002-1024):
    // - msgtyp = 0         -> SEARCH_ANY (获取任意消息)
    // - msgtyp > 0         -> SEARCH_EQUAL (匹配类型)
    // - msgtyp < 0         -> SEARCH_LESSEQUAL (类型 <= |msgtyp|)
    // - msgflg & MSG_EXCEPT -> SEARCH_NOTEQUAL (类型不匹配)

    // ========== 4. RCU 保护获取队列 ==========
    // 行 1121-1127
    rcu_read_lock();
    msq = msq_obtain_object_check(ns, msqid);
    if (IS_ERR(msq)) {
        rcu_read_unlock();
        free_copy(copy);
        return PTR_ERR(msq);
    }

    // ========== 5. 主循环 ==========
    // 行 1129-1246
    for (;;) {
        struct msg_receiver msr_d;

        // 权限检查
        msg = ERR_PTR(-EACCES);
        if (ipcperms(ns, &msq->q_perm, S_IRUGO))
            goto out_unlock1;

        ipc_lock_object(&msq->q_perm);

        // 队列被删除检查
        if (!ipc_valid_object(&msq->q_perm)) {
            msg = ERR_PTR(-EIDRM);
            goto out_unlock0;
        }

        // ========== 6. 查找匹配消息 ==========
        // 行 1144: find_msg 遍历链表查找
        msg = find_msg(msq, &msgtyp, mode);
        if (!IS_ERR(msg)) {
            // ========== 找到消息 ==========
            // 行 1150-1153: 消息太大处理
            if ((bufsz < msg->m_ts) && !(msgflg & MSG_NOERROR)) {
                msg = ERR_PTR(-E2BIG);
                goto out_unlock0;
            }

            // ========== MSG_COPY 模式处理 ==========
            // 行 1158-1161: 复制消息而非取出
            if (msgflg & MSG_COPY) {
                msg = copy_msg(msg, copy);
                goto out_unlock0;
            }

            // ========== 7. 从队列移除消息 ==========
            // 行 1163-1169
            list_del(&msg->m_list);      // 从 q_messages 移除
            msq->q_qnum--;               // 消息数 -1
            msq->q_rtime = ktime_get_real_seconds();
            ipc_update_pid(&msq->q_lrpid, task_tgid(current));
            msq->q_cbytes -= msg->m_ts;  // 字节数减少
            percpu_counter_sub_local(&ns->percpu_msg_bytes, msg->m_ts);
            percpu_counter_sub_local(&ns->percpu_msg_hdrs, 1);

            // 唤醒等待的发送者
            ss_wakeup(msq, &wake_q, false);
            goto out_unlock0;
        }

        // ========== 没有可用消息 ==========
        // 行 1175-1179
        if (msgflg & IPC_NOWAIT) {
            msg = ERR_PTR(-ENOMSG);
            goto out_unlock0;
        }

        // ========== 8. 阻塞等待: 添加到接收者队列 ==========
        // 行 1181-1194
        list_add_tail(&msr_d.r_list, &msq->q_receivers);
        msr_d.r_tsk = current;
        msr_d.r_msgtype = msgtyp;
        msr_d.r_mode = mode;
        if (msgflg & MSG_NOERROR)
            msr_d.r_maxsize = INT_MAX;
        else
            msr_d.r_maxsize = bufsz;

        // 使用 store-release 防止竞态
        WRITE_ONCE(msr_d.r_msg, ERR_PTR(-EAGAIN));
        __set_current_state(TASK_INTERRUPTIBLE);

        // ========== 9. 释放锁并调度 ==========
        ipc_unlock_object(&msq->q_perm);
        rcu_read_unlock();
        schedule();

        // ========== 10. 唤醒后处理 ==========
        // 行 1209-1246: Lockless Receive 优化
        rcu_read_lock();

        // 使用 load-acquire 读取消息指针
        msg = READ_ONCE(msr_d.r_msg);
        if (msg != ERR_PTR(-EAGAIN)) {
            // 通过管道化发送收到了消息
            smp_acquire__after_ctrl_dep();
            goto out_unlock1;
        }

        // 再次获取锁检查
        ipc_lock_object(&msq->q_perm);
        msg = READ_ONCE(msr_d.r_msg);
        if (msg != ERR_PTR(-EAGAIN))
            goto out_unlock0;

        // 信号打断
        list_del(&msr_d.r_list);
        if (signal_pending(current)) {
            msg = ERR_PTR(-ERESTARTNOHAND);
            goto out_unlock0;
        }
    }

out_unlock0:
    ipc_unlock_object(&msq->q_perm);
    wake_up_q(&wake_q);
out_unlock1:
    rcu_read_unlock();
    if (IS_ERR(msg)) {
        free_copy(copy);
        return PTR_ERR(msg);
    }

    // ========== 11. 复制消息到用户空间 ==========
    bufsz = msg_handler(buf, msg, bufsz);  // 调用 do_msg_fill
    free_msg(msg);
    return bufsz;
}
```

### 1.4 msg_msg 结构 (单消息 vs 多消息)

**文件**: `/Users/sphinx/github/linux/include/linux/msg.h`

```c
// 消息结构 - 变长结构
struct msg_msg {
    struct list_head m_list;    // 链表节点 (用于连接同一队列中的消息)
    long m_type;                // 消息类型 (必须 > 0)
    size_t m_ts;                // 消息文本大小
    struct msg_msgseg *next;   // 下一段 (用于大消息)  <-- 关键!
    /* the actual message follows immediately */
};
```

**大消息分段存储**:

```
简单消息 (m_ts <= DATALEN_MSG):
+------------------+
| struct msg_msg   |
| m_list           |
| m_type = 1       |
| m_ts = 100       |
| next = NULL      |
+------------------+
| 消息数据 (100B)  |
+------------------+

大消息 (m_ts > DATALEN_MSG):
+------------------+     +------------------+
| struct msg_msg   | --> | struct msg_msgseg|
| m_list           |     | next = NULL      |
| m_type = 1       |     +------------------+
| m_ts = 4000      |     | 消息数据段 1     |
| next = 0x...     |     | (约 4000 - 消息头)|
+------------------+     +------------------+
| 消息数据第一段   |
| (DATALEN_MSG B)  |
+------------------+
```

**关键设计**: Linux 使用链表将大消息分成多个段，每段包含实际消息数据。这允许消息大小超过单块内存限制。

### 1.5 管道化发送优化 (Pipelined Send/Receive)

**函数**: `pipelined_send()` (msg.c 行 816-846)

**概念**: 当发送者发现没有等待的接收者时，消息被放入队列。但如果发送时**已有接收者在等待**，则可以跳过队列，直接传递消息。

```c
// 行 816-846: 管道化发送
static inline int pipelined_send(struct msg_queue *msq, struct msg_msg *msg,
                                 struct wake_q_head *wake_q)
{
    struct msg_receiver *msr, *t;

    // 遍历所有等待的接收者
    list_for_each_entry_safe(msr, t, &msq->q_receivers, r_list) {
        // 类型匹配检查
        if (testmsg(msg, msr->r_msgtype, msr->r_mode) &&
            !security_msg_queue_msgrcv(&msq->q_perm, msg, msr->r_tsk,
                                        msr->r_msgtype, msr->r_mode)) {

            list_del(&msr->r_list);  // 从等待队列移除

            if (msr->r_maxsize < msg->m_ts) {
                // 接收者缓冲区太小，返回错误
                smp_store_release(&msr->r_msg, ERR_PTR(-E2BIG));
                wake_q_add(wake_q, msr->r_tsk);
            } else {
                // 直接传递消息指针
                ipc_update_pid(&msq->q_lrpid, task_pid(msr->r_tsk));
                msq->q_rtime = ktime_get_real_seconds();
                smp_store_release(&msr->r_msg, msg);  // 使用 store-release
                wake_q_add(wake_q, msr->r_tsk);
                return 1;  // 成功
            }
        }
    }
    return 0;  // 没有找到匹配的接收者
}
```

**时序图**:

```
普通路径 (无等待接收者):
  发送者                      队列                        接收者
    |                          |                          |
    |---- msgsnd() ----------->|                          |
    |     (消息入队)          |                          |
    |                          |                          |
    |                          |<--- msgrcv() -----------|
    |                          |     (从队列取消息)       |
    |                          |                          |

管道化路径 (有等待接收者):
  发送者                      队列                        接收者
    |                          |                          |
    |<---- msgrcv() ---------- |     (注册为等待接收者)   |
    |                          |                          |
    |---- msgsnd() -----------+------------------------>|
    |     (直接传递消息)       |     (唤醒)               |
    |                          |                          |
```

---

## 2. 信号量 Undo 机制

### 2.1 sem_undo 结构 (进程级别撤销)

**文件**: `/Users/sphinx/github/linux/ipc/sem.c`

```c
// 行 146-157: sem_undo 结构
struct sem_undo {
    struct list_head list_proc;   // 进程内所有 undo 项的链表 (RCU 保护)
    struct rcu_head rcu;          // RCU 头
    struct sem_undo_list *ulp;   // 指向拥有者的 undo_list
    struct list_head list_id;     // 同一信号量数组的所有 undo 项
    int semid;                   // 信号量数组 ID
    short semadj[];              // 调整值数组 (变长, 每个信号量一个)
};

// 行 162-166: sem_undo_list 结构
struct sem_undo_list {
    refcount_t refcnt;           // 引用计数
    spinlock_t lock;             // 保护 list_proc
    struct list_head list_proc;  // 进程的所有 sem_undo
};
```

**数据结构关系图**:

```
进程 task_struct
+-----------------+
| sysvsem         |
| .undo_list -----+------> sem_undo_list
+-----------------+          +------------------+
                           | refcnt = 2       |
                           | lock (spinlock)  |
                           +------------------+
                           | list_proc        |
                           +------------------+
                                  |
                                  v
                    +-------------+-------------+------------------+
                    |             |             |                  |
                    v             v             v                  v
              sem_undo       sem_undo       sem_undo           sem_undo
              semid=100       semid=200       semid=300           ...
              semadj=[-1]     semadj=[0,1]   semadj=[2,-1,0]
                    |             |             |
                    v             v             v
              sem_array      sem_array      sem_array
              (id=100)       (id=200)       (id=300)
```

**关键特性**:
- `semadj[]` 是变长数组，大小等于信号量数组中信号量的个数
- 每个 undo 项记录**相对于操作前的调整值**
- 进程退出时 (`exit_sem()`) 自动应用所有 undo

### 2.2 semadjmax 限制

**定义位置**: `/Users/sphinx/github/linux/include/linux/sem.h`

```c
// 限制值
#define SEMVMX  32767   // 单个信号量值的最大值
#define SEMAEM  (SEMVMX)  // undo 调整的最大绝对值
```

**在 perform_atomic_semop 中的检查** (sem.c 行 674-680):

```c
if (sop->sem_flg & SEM_UNDO) {
    int undo = un->semadj[sop->sem_num] - sem_op;
    // Exceeding the undo range is an error.
    if (undo < (-SEMAEM - 1) || undo > SEMAEM)  // 行 677-678
        goto out_of_range;
    un->semadj[sop->sem_num] = undo;
}
```

**语义**: 每个信号量的 undo 值被限制在 `[-SEMAEM, SEMAEM]` 范围内。这防止了：
1. 资源泄漏 (值过大无法回退)
2. 信号量值溢出 (负值超过限制)

### 2.3 semop() 原子性保证

**函数**: `__do_semtimedop()` (行 1983-2220)

**原子性机制**:

```c
// 行 1983-2220: __do_semtimedop 核心逻辑
long __do_semtimedop(int semid, struct sembuf *sops, unsigned nsops,
                     const struct timespec64 *timeout, struct ipc_namespace *ns)
{
    // ...
    bool undos = false, alter = false, dupsop = false;

    // ========== 1. 操作预处理 ==========
    // 行 2012-2033: 分析所有操作
    for (sop = sops; sop < sops + nsops; sop++) {
        if (sop->sem_flg & SEM_UNDO)
            undos = true;        // 标记需要 undo
        if (sop->sem_op != 0)
            alter = true;        // 标记修改操作
    }

    // ========== 2. 查找/分配 undo 结构 ==========
    // 行 2035-2045
    if (undos) {
        un = find_alloc_undo(ns, semid);  // 懒分配
        if (IS_ERR(un)) {
            error = PTR_ERR(un);
            goto out;
        }
    }

    // ========== 3. 获取信号量数组 ==========
    // 行 2047-2052
    sma = sem_obtain_object_check(ns, semid);
    if (IS_ERR(sma)) {
        rcu_read_unlock();
        error = PTR_ERR(sma);
        goto out;
    }

    // ========== 4. 权限检查 ==========
    // 行 2060-2064

    // ========== 5. 锁定信号量 ==========
    // 行 2073: sem_lock 实现细粒度锁定
    locknum = sem_lock(sma, sops, nsops);

    // ========== 6. 原子执行所有操作 ==========
    // 行 2101: perform_atomic_semop 一次性执行
    error = perform_atomic_semop(sma, &queue);

    if (error == 0) {
        // 成功: 更新并返回
        // ...
        goto out;
    }

    // error > 0: 需要阻塞
    // error < 0: 错误

    // ========== 7. 阻塞等待 ==========
    // 行 2127-2211
    // 添加到等待队列，调用 schedule()
}
```

**sem_lock 细粒度锁定** (行 389-458):

```c
// 行 389-458: 自旋锁锁定策略
static inline int sem_lock(struct sem_array *sma, struct sembuf *sops, int nsops)
{
    // ========== 快速路径: 单操作 ==========
    if (nsops == 1) {
        // 行 404-431: 只锁定特定信号量
        idx = array_index_nospec(sops->sem_num, sma->sem_nsems);
        sem = &sma->sems[idx];

        if (!READ_ONCE(sma->use_global_lock)) {
            spin_lock(&sem->lock);  // 只锁一个信号量
            if (!smp_load_acquire(&sma->use_global_lock)) {
                return sops->sem_num;  // 成功
            }
            spin_unlock(&sem->lock);
        }
    }

    // ========== 慢速路径: 全局锁 ==========
    // 行 433-457
    ipc_lock_object(&sma->sem_perm);  // 锁整个数组
    complexmode_enter(sma);           // 进入复杂模式
    return SEM_GLOBAL_LOCK;
}
```

### 2.4 退出时 sem_cleanup() 流程

**函数**: `exit_sem()` (行 2335-2446)

```c
// 行 2335-2446: 进程退出时自动清理
void exit_sem(struct task_struct *tsk)
{
    struct sem_undo_list *ulp;

    // ========== 1. 获取并清理 undo_list ==========
    // 行 2337-2345
    ulp = tsk->sysvsem.undo_list;
    if (!ulp)
        return;
    tsk->sysvsem.undo_list = NULL;

    // 如果还有其它线程共享此 undo_list，减少引用
    if (!refcount_dec_and_test(&ulp->refcnt))
        return;  // 还有其它使用者

    // ========== 2. 遍历所有 undo 项 ==========
    // 行 2347-2444
    for (;;) {
        struct sem_array *sma;
        struct sem_undo *un;
        int semid, i;
        DEFINE_WAKE_Q(wake_q);

        cond_resched();  // 允许调度

        rcu_read_lock();

        // 获取下一个 undo 项
        un = list_entry_rcu(ulp->list_proc.next, struct sem_undo, list_proc);

        // 检查是否已处理完所有项
        if (&un->list_proc == &ulp->list_proc) {
            spin_lock(&ulp->lock);
            spin_unlock(&ulp->lock);
            rcu_read_unlock();
            break;
        }

        semid = un->semid;
        spin_unlock(&ulp->lock);

        // ========== 3. 获取信号量数组 ==========
        sma = sem_obtain_object_check(tsk->nsproxy->ipc_ns, semid);
        if (IS_ERR(sma)) {
            rcu_read_unlock();
            continue;  // 数组已被删除
        }

        sem_lock(sma, NULL, -1);  // 锁定数组

        // ========== 4. 应用 undo 值 ==========
        // 行 2412-2436: 对每个信号量应用调整
        for (i = 0; i < sma->sem_nsems; i++) {
            struct sem *semaphore = &sma->sems[i];
            if (un->semadj[i]) {
                semaphore->semval += un->semadj[i];
                // 限制在 [0, SEMVMX] 范围内
                if (semaphore->semval < 0)
                    semaphore->semval = 0;
                if (semaphore->semval > SEMVMX)
                    semaphore->semval = SEMVMX;
            }
        }

        // ========== 5. 唤醒等待进程 ==========
        do_smart_update(sma, NULL, 0, 1, &wake_q);

        sem_unlock(sma, -1);
        rcu_read_unlock();
        wake_up_q(&wake_q);

        kvfree_rcu(un, rcu);  // 释放 undo 结构
    }

    kfree(ulp);  // 释放 undo_list
}
```

**关键特性**:
- 进程退出时自动应用所有未完成的信号量调整
- undo 值被限制在 `[-SEMAEM, SEMAEM]` 范围内
- 可能唤醒其他等待该信号量的进程

### 2.5 与 mutex deadlock 关系

**潜在死锁场景**:

```c
// 场景 1: 循环等待
// 进程 A                    进程 B
// semop(sem[0], -1)         semop(sem[1], -1)
// semop(sem[1], +1) BLOCK   semop(sem[0], +1) BLOCK

// 场景 2: 信号量与 mutex 混用
// 线程 1: lock(mutex) -> semop() -> unlock(mutex) [semop 阻塞]
// 线程 2: lock(mutex) BLOCK [线程1 持有 mutex]

// Linux 的缓解措施:
1. sem_undo 限制 (SEMAEM) 防止极端情况
2. 不提供死锁检测 (性能考虑)
3. 建议使用 semtimedop() 带超时
```

---

## 3. 共享内存 mmap

### 3.1 shmid_kernel 完整结构

**文件**: `/Users/sphinx/github/linux/ipc/shm.c`

```c
// 行 54-79: shmid_kernel 结构
struct shmid_kernel {
    struct kern_ipc_perm shm_perm;     // IPC 权限基础结构
    struct file *shm_file;            // 底层文件 (tmpfs/hugetlbfs)
    unsigned long shm_nattch;          // 当前 attach 数量
    unsigned long shm_segsz;           // 段大小 (字节)
    time64_t shm_atim;                 // 最后 attach 时间
    time64_t shm_dtim;                 // 最后 detach 时间
    time64_t shm_ctim;                 // 最后改变时间
    struct pid *shm_cprid;             // 创建者 PID
    struct pid *shm_lprid;             // 最后操作者 PID
    struct ucounts *mlock_ucounts;     // mlock 账户信息

    // 创建者信息 (用于跟踪)
    struct task_struct *shm_creator;   // 创建者任务
    struct list_head shm_clist;        // 创建者列表节点
    struct ipc_namespace *ns;           // 所属命名空间
} __randomize_layout;
```

**关键字段说明**:
- `shm_file`: 指向实际存储的 `struct file*`，可以是 `tmpfs` 或 `hugetlbfs`
- `shm_nattch`: attach 计数，用于判断是否可以销毁
- `shm_creator`: 记录创建者，用于 `exit_shm()` 清理孤儿段

### 3.2 shmat() 系统调用流程

**函数**: `do_shmat()` (行 1519-1691)

```c
// 行 1519-1691: shmat 核心逻辑
long do_shmat(int shmid, char __user *shmaddr, int shmflg,
              ulong *raddr, unsigned long shmlba)
{
    // ========== 1. 参数处理 ==========
    // 行 1535-1560
    if (shmid < 0)
        goto out;

    // 地址对齐处理
    if (addr) {
        if (addr & (shmlba - 1)) {
            if (shmflg & SHM_RND)
                addr &= ~(shmlba - 1);  // 向下对齐
            else
                goto out;  // 地址必须对齐
        }
        flags |= MAP_FIXED;  // 使用固定地址
    }

    // ========== 2. 权限和模式 ==========
    // 行 1562-1574
    if (shmflg & SHM_RDONLY) {
        prot = PROT_READ;
        acc_mode = S_IRUGO;
        f_flags = O_RDONLY;
    } else {
        prot = PROT_READ | PROT_WRITE;
        acc_mode = S_IRUGO | S_IWUGO;
        f_flags = O_RDWR;
    }

    // ========== 3. 获取共享内存段 ==========
    // 行 1580-1603
    ns = current->nsproxy->ipc_ns;
    rcu_read_lock();
    shp = shm_obtain_object_check(ns, shmid);

    // ========== 4. 创建 file 引用 ==========
    // 行 1614-1636
    base = get_file(shp->shm_file);  // 增加引用
    shp->shm_nattch++;               // attach 数 +1

    // ========== 5. 分配 shm_file_data ==========
    // 行 1621-1642
    sfd = kzalloc_obj(*sfd);
    sfd->id = shp->shm_perm.id;
    sfd->ns = get_ipc_ns(ns);
    sfd->file = base;
    file->private_data = sfd;

    // ========== 6. 执行 mmap ==========
    // 行 1648-1670
    if (mmap_write_lock_killable(current->mm))
        goto out_fput;

    // 检查地址冲突
    if (addr && !(shmflg & SHM_REMAP)) {
        if (addr + size < addr)  // 溢出检查
            goto invalid;
        if (find_vma_intersection(current->mm, addr, addr + size))
            goto invalid;
    }

    // 执行实际的内存映射
    addr = do_mmap(file, addr, size, prot, flags, 0, 0, &populate, NULL);
    *raddr = addr;  // 返回映射地址

invalid:
    mmap_write_unlock(current->mm);
    if (populate)
        mm_populate(addr, populate);

    // ========== 7. 清理 ==========
    // 行 1675-1684
    down_write(&shm_ids(ns).rwsem);
    shp = shm_lock(ns, shmid);
    shp->shm_nattch--;  // attach 数 -1
    if (shm_may_destroy(shp))
        shm_destroy(ns, shp);
    else
        shm_unlock(shp);
    up_write(&shm_ids(ns).rwsem);
}
```

### 3.3 shm_lock() 锁定机制

**函数**: `shm_lock()` (行 193-223)

```c
// 行 193-223: shm_lock 实现
static inline struct shmid_kernel *shm_lock(struct ipc_namespace *ns, int id)
{
    struct kern_ipc_perm *ipcp;

    rcu_read_lock();
    ipcp = ipc_obtain_object_idr(&shm_ids(ns), id);
    if (IS_ERR(ipcp))
        goto err;

    ipc_lock_object(ipcp);  // 获取自旋锁

    // 竞态检查: RMID 可能已释放
    if (ipc_valid_object(ipcp)) {
        return container_of(ipcp, struct shmid_kernel, shm_perm);
    }

    ipc_unlock_object(ipcp);
    ipcp = ERR_PTR(-EIDRM);
err:
    rcu_read_unlock();
    return ERR_CAST(ipcp);
}
```

**关键设计**: 使用 `ipc_valid_object()` 检查 `deleted` 标志，防止使用已删除的 IPC 对象。

### 3.4 内存映射页错误处理

**函数**: `shm_fault()` (行 540-546)

```c
// 行 540-546: 页错误处理
static vm_fault_t shm_fault(struct vm_fault *vmf)
{
    struct file *file = vmf->vma->vm_file;
    struct shm_file_data *sfd = shm_file_data(file);

    // 委托给底层文件系统的 fault 处理
    return sfd->vm_ops->fault(vmf);
}
```

**页错误处理流程**:

```
进程访问共享内存页
        |
        v
    +-----------+
    | pagefault |
    +-----------+
        |
        v
    +-----------+
    | shm_fault |  <-- vm_operations_struct.fault
    +-----------+
        |
        v
    +-----------+     +------------+
    | tmpfs     | or  | hugetlbfs |
    | fault     |     | fault      |
    +-----------+     +------------+
        |
        v
    +-----------+
    | 分配页     |
    +-----------+
```

### 3.5 hugetlbfs 支持

**创建 huge page 共享内存** (shm.c 行 741-756):

```c
if (shmflg & SHM_HUGETLB) {
    struct hstate *hs;
    size_t hugesize;

    // 获取指定大小的 hstate
    hs = hstate_sizelog((shmflg >> SHM_HUGE_SHIFT) & SHM_HUGE_MASK);
    if (!hs) {
        error = -EINVAL;
        goto no_file;
    }

    hugesize = ALIGN(size, huge_page_size(hs));

    // 使用 hugetlb_file_setup 创建
    file = hugetlb_file_setup(name, hugesize, acctflag,
            HUGETLB_SHMFS_INODE, (shmflg >> SHM_HUGE_SHIFT) & SHM_HUGE_MASK);
} else {
    file = shmem_kernel_file_setup(name, size, acctflag);
}
```

**shm_file_data 结构** (行 85-92):

```c
struct shm_file_data {
    int id;                           // shmid
    struct ipc_namespace *ns;         // 命名空间
    struct file *file;                // 底层文件
    const struct vm_operations_struct *vm_ops;  // VM 操作
};
```

---

## 4. POSIX mqueue 通知

### 4.1 struct mqueue_inode_info 完整结构

**文件**: `/Users/sphinx/github/linux/ipc/mqueue.c`

```c
// 行 133-155: mqueue_inode_info 结构
struct mqueue_inode_info {
    spinlock_t lock;                  // 保护此结构
    struct inode vfs_inode;           // VFS inode
    wait_queue_head_t wait_q;         // 通用等待队列 (用于 poll)

    // 消息红黑树 (按优先级组织)
    struct rb_root msg_tree;          // 消息树根
    struct rb_node *msg_tree_rightmost;  // 最右侧节点 (最高优先级)
    struct posix_msg_tree_node *node_cache;  // 节点缓存

    struct mq_attr attr;              // 队列属性

    // 通知机制
    struct sigevent notify;           // 通知配置
    struct pid *notify_owner;         // 已注册通知的进程
    u32 notify_self_exec_id;          // exec ID 检测
    struct user_namespace *notify_user_ns;  // 用户命名空间
    struct sock *notify_sock;         // netlink socket (SIGEV_THREAD)
    struct sk_buff *notify_cookie;    // cookie (SIGEV_THREAD)

    // 等待队列 (发送和接收)
    struct ext_wait_queue e_wait_q[2];  // [0]=SEND, [1]=RECV

    unsigned long qsize;              // 队列总大小 (字节)
};
```

**数据结构关系图**:

```
mqueue_inode_info
+--------------------------------+
| lock (spinlock)                |
+--------------------------------+
| vfs_inode                      |
+--------------------------------+
| wait_q (poll 用)               |
+--------------------------------+
| msg_tree (红黑树)              |
|    |                           |
|    +-- rb_node (按 m_type)     |
|        +-- [msg_list]          |
|        +-- [msg_list]          |
+--------------------------------+
| node_cache                     |
+--------------------------------+
| attr (mq_maxmsg, mq_msgsize)   |
+--------------------------------+
| notify 配置                    |
|  +-- sigevent                  |
|  +-- notify_owner (PID)        |
|  +-- notify_sock (netlink)     |
+--------------------------------+
| e_wait_q[2]                    |
|  +-- [0] SEND:  ext_wait_queue |
|  +-- [1] RECV:  ext_wait_queue |
+--------------------------------+
| qsize                          |
+--------------------------------+
```

### 4.2 消息红黑树 vs 等待队列

**消息红黑树组织** (行 190-230):

```c
// 行 60-64: posix_msg_tree_node
struct posix_msg_tree_node {
    struct rb_node rb_node;          // 红黑树节点
    struct list_head msg_list;       // 同优先级消息链表
    int priority;                    // 消息优先级
};

// 行 190-230: msg_insert - 插入消息到红黑树
static int msg_insert(struct msg_msg *msg, struct mqueue_inode_info *info)
{
    struct rb_node **p, *parent = NULL;
    struct posix_msg_tree_node *leaf;
    bool rightmost = true;

    p = &info->msg_tree.rb_node;

    // 查找匹配的优先级节点
    while (*p) {
        parent = *p;
        leaf = rb_entry(parent, struct posix_msg_tree_node, rb_node);

        if (likely(leaf->priority == msg->m_type))
            goto insert_msg;
        else if (msg->m_type < leaf->priority) {
            p = &(*p)->rb_left;
            rightmost = false;
        } else
            p = &(*p)->rb_right;
    }

    // 需要新节点: 尝试使用缓存
    if (info->node_cache) {
        leaf = info->node_cache;
        info->node_cache = NULL;
    } else {
        leaf = kmalloc_obj(*leaf, GFP_ATOMIC);
        if (!leaf)
            return -ENOMEM;
        INIT_LIST_HEAD(&leaf->msg_list);
    }
    leaf->priority = msg->m_type;

    // 更新最右侧指针
    if (rightmost)
        info->msg_tree_rightmost = &leaf->rb_node;

    // 插入红黑树
    rb_link_node(&leaf->rb_node, parent, p);
    rb_insert_color(&leaf->rb_node, &info->msg_tree);

insert_msg:
    info->attr.mq_curmsgs++;
    info->qsize += msg->m_ts;
    list_add_tail(&msg->m_list, &leaf->msg_list);
    return 0;
}
```

**消息获取** (行 247-287):

```c
// 行 247-287: msg_get - 获取最高优先级消息
static inline struct msg_msg *msg_get(struct mqueue_inode_info *info)
{
    struct rb_node *parent = NULL;
    struct posix_msg_tree_node *leaf;
    struct msg_msg *msg;

try_again:
    // 从最右侧获取 (最高优先级)
    parent = info->msg_tree_rightmost;
    if (!parent) {
        // 异常处理
        return NULL;
    }

    leaf = rb_entry(parent, struct posix_msg_tree_node, rb_node);

    // 获取消息
    if (unlikely(list_empty(&leaf->msg_list))) {
        msg_tree_erase(leaf, info);
        goto try_again;
    }

    msg = list_first_entry(&leaf->msg_list, struct msg_msg, m_list);
    list_del(&msg->m_list);

    // 如果链表空，删除叶子节点
    if (list_empty(&leaf->msg_list)) {
        msg_tree_erase(leaf, info);
    }

    info->attr.mq_curmsgs--;
    info->qsize -= msg->m_ts;
    return msg;
}
```

**ext_wait_queue 结构** (行 126-131):

```c
// 行 126-131: 等待队列条目
struct ext_wait_queue {
    struct task_struct *task;         // 等待的任务
    struct list_head list;           // 链表节点
    struct msg_msg *msg;             // 消息指针 (用于管道化)
    int state;                       // STATE_NONE 或 STATE_READY
};
```

### 4.3 通知机制 (SIGEV_NONE, SIGEV_SIGNAL, SIGEV_THREAD)

**do_mq_notify()** (行 1266-1373):

```c
// 行 1266-1373: mq_notify 实现
static int do_mq_notify(mqd_t mqdes, const struct sigevent *notification)
{
    // ========== 1. 参数验证 ==========
    // 行 1278-1282
    if (notification != NULL) {
        if (notification->sigev_notify != SIGEV_NONE &&
            notification->sigev_notify != SIGEV_SIGNAL &&
            notification->sigev_notify != SIGEV_THREAD)
            return -EINVAL;

        if (notification->sigev_notify == SIGEV_SIGNAL &&
            !valid_signal(notification->sigev_signo))
            return -EINVAL;

        // SIGEV_THREAD: 创建 netlink socket
        if (notification->sigev_notify == SIGEV_THREAD) {
            nc = alloc_skb(NOTIFY_COOKIE_LEN, GFP_KERNEL);
            // ... 复制 cookie 到 skb
            sock = netlink_getsockbyfd(notification->sigev_signo);
            // ... 附加 socket
        }
    }

    // ========== 2. 获取 inode ==========
    // 行 1321-1332
    CLASS(fd, f)(mqdes);
    inode = file_inode(fd_file(f));
    info = MQUEUE_I(inode);

    // ========== 3. 设置或清除通知 ==========
    // 行 1334-1368
    spin_lock(&info->lock);

    if (notification == NULL) {
        // 清除通知注册
        if (info->notify_owner == task_tgid(current))
            remove_notification(info);
    } else if (info->notify_owner != NULL) {
        // 已有注册
        ret = -EBUSY;
    } else {
        // 注册新通知
        switch (notification->sigev_notify) {
        case SIGEV_NONE:
            info->notify.sigev_notify = SIGEV_NONE;
            break;
        case SIGEV_THREAD:
            info->notify_sock = sock;
            info->notify_cookie = nc;
            sock = NULL;  // 避免在 out 释放
            nc = NULL;
            info->notify.sigev_notify = SIGEV_THREAD;
            break;
        case SIGEV_SIGNAL:
            info->notify.sigev_signo = notification->sigev_signo;
            info->notify.sigev_value = notification->sigev_value;
            info->notify.sigev_notify = SIGEV_SIGNAL;
            info->notify_self_exec_id = current->self_exec_id;
            break;
        }

        info->notify_owner = get_pid(task_tgid(current));
        info->notify_user_ns = get_user_ns(current_user_ns());
    }

    spin_unlock(&info->lock);
}
```

**通知触发** `__do_notify()` (行 777-836):

```c
// 行 777-836: 通知触发
static void __do_notify(struct mqueue_inode_info *info)
{
    // 仅当: 有注册进程 且 队列从空变为非空
    if (info->notify_owner &&
        info->attr.mq_curmsgs == 1) {

        switch (info->notify.sigev_notify) {
        case SIGEV_NONE:
            break;  // 无操作

        case SIGEV_SIGNAL: {
            struct kernel_siginfo sig_i;
            // 设置 si_code = SI_MESGQ (内核生成)
            sig_i.si_signo = info->notify.sigev_signo;
            sig_i.si_value = info->notify.sigev_value;
            sig_i.si_code = SI_MESGQ;
            sig_i.si_pid = task_tgid_nr_ns(current, ...);
            sig_i.si_uid = from_kuid_munged(info->notify_user_ns, current_uid());

            // 查找任务并发送信号
            task = pid_task(info->notify_owner, PIDTYPE_TGID);
            if (task && task->self_exec_id == info->notify_self_exec_id)
                do_send_sig_info(info->notify.sigev_signo, &sig_i, task, PIDTYPE_TGID);
            break;
        }

        case SIGEV_THREAD:
            // 通过 netlink 发送 cookie
            set_cookie(info->notify_cookie, NOTIFY_WOKENUP);
            netlink_sendskb(info->notify_sock, info->notify_cookie);
            break;
        }

        // 通知后自动注销
        put_pid(info->notify_owner);
        put_user_ns(info->notify_user_ns);
        info->notify_owner = NULL;
        info->notify_user_ns = NULL;
    }

    wake_up(&info->wait_q);  // 唤醒 poll
}
```

### 4.4 mq_notify() 流程

**mq_notify 完整时序图**:

```
                    进程 A                        消息队列                    进程 B
                        |                            |                          |
                        |<---- mq_open() ----------|                          |
                        |                            |                          |
                        |<---- mq_notify() ---------|  [注册 SIGEV_SIGNAL]     |
                        |                            |                          |
                        |                            |<--- mq_send() ------------|
                        |                            |   (队列从空变为非空)      |
                        |                            |                          |
                        |---- __do_notify() ------->|                          |
                        |   (发送 SIGUSR1)         |                          |
                        |                            |                          |
                        |                            |                          |
                        |                            |<--- mq_receive() -------|
                        |                            |                          |
```

**关键设计**:
1. 通知**一次性**: 触发后自动注销
2. 竞态处理: 使用 `self_exec_id` 防止发送到已 exec 的进程
3. SI_MESGQ: 特殊的 si_code，标识来自 POSIX mqueue

---

## 5. IPC 通用框架

### 5.1 ipc_rcu (RCU 保护)

**文件**: `/Users/sphinx/github/linux/ipc/util.c`

```c
// 行 528-540: ipc_rcu 引用计数
bool ipc_rcu_getref(struct kern_ipc_perm *ptr)
{
    return refcount_inc_not_zero(&ptr->refcount);
}

void ipc_rcu_putref(struct kern_ipc_perm *ptr,
                    void (*func)(struct rcu_head *head))
{
    if (!refcount_dec_and_test(&ptr->refcount))
        return;

    call_rcu(&ptr->rcu, func);  // 延迟释放
}
```

**RCU 释放流程**:

```
ipc_rcu_putref()
      |
      v
refcount_dec_and_test() == true?
      |
      +-- No --> 返回, 不释放
      |
      +-- Yes --> call_rcu() 调度释放
                            |
                            v
                    稍后调用 func()
                    (通常 kfree)
```

**使用场景**:
- `msg_rcu_free()` (msg.c 行 128-135): 释放消息队列
- `shm_rcu_free()` (shm.c 行 231-239): 释放共享内存
- `sem_rcu_free()` (sem.c 行 323-330): 释放信号量数组

### 5.2 ipc_obtain_object_idr()

**函数**: `ipc_obtain_object_idr()` (util.c 行 626-636)

```c
// 行 626-636: IDR 获取对象
struct kern_ipc_perm *ipc_obtain_object_idr(struct ipc_ids *ids, int id)
{
    struct kern_ipc_perm *out;
    int idx = ipcid_to_idx(id);  // 从 ID 提取索引

    out = idr_find(&ids->ipcs_idr, idx);  // IDR 查找
    if (!out)
        return ERR_PTR(-EINVAL);

    return out;
}
```

### 5.3 ipc_addid() idr 分配

**函数**: `ipc_addid()` (util.c 行 278-327)

```c
// 行 278-327: 添加 IPC ID
int ipc_addid(struct ipc_ids *ids, struct kern_ipc_perm *new, int limit)
{
    kuid_t euid;
    kgid_t egid;
    int idx, err;

    // ========== 1. 初始化引用计数 ==========
    refcount_set(&new->refcount, 1);  // 行 285

    // ========== 2. 限额检查 ==========
    if (limit > ipc_mni)
        limit = ipc_mni;
    if (ids->in_use >= limit)
        return -ENOSPC;

    // ========== 3. 分配 IDR 索引 ==========
    // 行 293-261
    idr_preload(GFP_KERNEL);
    spin_lock_init(&new->lock);  // 初始化自旋锁

    rcu_read_lock();
    spin_lock(&new->lock);

    // 获取当前用户身份
    current_euid_egid(&euid, &egid);
    new->cuid = new->uid = euid;
    new->gid = new->cgid = egid;
    new->deleted = false;

    // 分配索引
    idx = ipc_idr_alloc(ids, new);

    // ========== 4. 添加到 key 哈希表 ==========
    // 行 308-315
    if (idx >= 0 && new->key != IPC_PRIVATE) {
        err = rhashtable_insert_fast(&ids->key_ht, &new->khtnode,
                                     ipc_kht_params);
        if (err < 0) {
            idr_remove(&ids->ipcs_idr, idx);
            idx = err;
        }
    }

    if (idx < 0) {
        new->deleted = true;
        spin_unlock(&new->lock);
        rcu_read_unlock();
        return idx;
    }

    ids->in_use++;
    if (idx > ids->max_idx)
        ids->max_idx = idx;
    return idx;  // 返回时已锁定
}
```

**IDR 分配算法**: 使用循环分配 (idr_alloc_cyclic) 尽量复用已释放的 ID

### 5.4 ipc_lock() 读写锁

**文件**: `/Users/sphinx/github/linux/ipc/util.h`

```c
// 行 208-227: ipc_lock/unlock 辅助函数
static inline void ipc_lock_object(struct kern_ipc_perm *perm)
{
    spin_lock(&perm->lock);
}

static inline void ipc_unlock_object(struct kern_ipc_perm *perm)
{
    spin_unlock(&perm->lock);
}

static inline void ipc_unlock(struct kern_ipc_perm *perm)
{
    ipc_unlock_object(perm);
    rcu_read_unlock();  // 配合 ipc_lock 使用
}
```

**锁层次结构**:

```
1. ipc_ids.rwsem (读写信号量)
   - 创建/删除/迭代时需要写锁
   - 读取时需要读锁

2. kern_ipc_perm.lock (自旋锁)
   - 每个 IPC 对象一个
   - 操作对象内部数据时锁定
```

**锁定规则**:
- `ipc_findkey()`: 需要 `ids->rwsem` (写锁)
- `ipc_obtain_object_idr()`: 只需 RCU read lock
- `ipc_lock_object()`: 需要先有 RCU read lock

---

## 6. 性能优化

### 6.1 预分配消息池

**POSIX mqueue 节点缓存** (mqueue.c 行 1090-1102):

```c
// 在 do_mq_timedsend 中
if (!info->node_cache)
    new_leaf = kmalloc_obj(*new_leaf);

spin_lock(&info->lock);

if (!info->node_cache && new_leaf) {
    // 保存预分配节点到缓存
    INIT_LIST_HEAD(&new_leaf->msg_list);
    info->node_cache = new_leaf;
    new_leaf = NULL;
} else {
    kfree(new_leaf);  // 释放多余的预分配
}
```

**设计意图**:
- 避免在持有锁时进行 GFP_ATOMIC 分配
- 预分配一个 `posix_msg_tree_node` 备用
- 如果在锁外分配失败，使用缓存

### 6.2 RCU 在 ipc 结构的应用

**RCU 使用模式**:

```c
// 1. 获取对象 (读操作)
rcu_read_lock();
ipcp = ipc_obtain_object_idr(&msg_ids(ns), id);
if (IS_ERR(ipcp))
    goto out;
ipc_lock_object(ipcp);
// ... 使用对象 ...
ipc_unlock_object(ipcp);
rcu_read_unlock();

// 2. 删除对象
ipc_rmid(&ids, ipcp);
// 此时对象被标记为 deleted，但可能仍有引用

// 3. 释放对象 (通过 call_rcu)
void msg_rcu_free(struct rcu_head *head)
{
    // 只有在所有 RCU 读者完成后才执行
    kfree(msq);
}
```

**内存屏障保证**:

```c
// 写者: 删除并标记
ipc_rmid():
    idr_remove(...);
    ipcp->deleted = true;  // RELEASE

// 读者: 检查有效性
if (ipc_valid_object(ipcp))  // ACQUIRE + 检查
    // 对象有效
```

### 6.3 Lockfree 算法

**mqueue 管道化操作** (mqueue.c 行 993-1005):

```c
// 行 993-1005: 管道化操作
static inline void __pipelined_op(struct wake_q_head *wake_q,
                                  struct mqueue_inode_info *info,
                                  struct ext_wait_queue *this)
{
    struct task_struct *task;

    list_del(&this->list);
    task = get_task_struct(this->task);

    // 使用 store-release 设置状态
    smp_store_release(&this->state, STATE_READY);
    wake_q_add_safe(wake_q, task);
}
```

**关键 lockfree 技术**:
1. `smp_store_release`: 确保在设置状态前所有数据可见
2. `READ_ONCE` + `smp_acquire__after_ctrl_dep`: 确保在读取数据后获得状态
3. `wake_q_add_safe`: 安全的无锁唤醒

### 6.4 slab 缓存优化

**mqueue inode 缓存** (mqueue.c 行 1647-1651):

```c
// 行 1647-1651: 创建 slab 缓存
mqueue_inode_cachep = kmem_cache_create("mqueue_inode_cache",
        sizeof(struct mqueue_inode_info), 0,
        SLAB_HWCACHE_ALIGN | SLAB_ACCOUNT, init_once);
```

**slab 优化特性**:
- `SLAB_HWCACHE_ALIGN`: 按 CPU 缓存行对齐，减少伪共享
- `SLAB_ACCOUNT`: 计入进程内存使用 (memory cgroup)
- 预热 `init_once`: 初始化时预分配一些对象

---

## 附录 A: 数据结构关系总图

```
IPC 对象层次结构
========================

struct kern_ipc_perm (所有 IPC 对象的基础)
+--------------------------------------------------+
| refcount_t refcount    // 引用计数               |
| spinlock_t lock        // 保护此结构            |
| bool deleted           // 是否已删除             |
| key_t key              // 用户提供的键           |
| int id                 // 系统分配的 ID          |
| int seq                // 序列号 (防 ID 重用)   |
| struct rcu_head rcu    // RCU 延迟释放           |
| struct rhash_head khtnode  // 哈希表节点         |
+--------------------------------------------------+

        |                        |                        |
        v                        v                        v
+-------------+          +-------------+          +-------------+
| msg_queue   |          | sem_array   |          | shmid_kernel|
| (消息队列)  |          | (信号量数组)|          | (共享内存)  |
+-------------+          +-------------+          +-------------+
| q_messages  |          | sems[]      |          | shm_file    |
| q_receivers |          | pending_*   |          | shm_nattch  |
| q_senders   |          | list_id    |          | shm_creator |
+-------------+          +-------------+          +-------------+
                                  |
                                  v
                          +-------------+
                          | sem_undo    |
                          | semadj[]    |
                          +-------------+

POSIX mqueue (独立实现)
+--------------------------------+
| mqueue_inode_info              |
+--------------------------------+
| msg_tree (红黑树)              |
| e_wait_q[2] (等待队列)        |
| notify_owner (通知注册)        |
+--------------------------------+
```

---

## 附录 B: 关键锁规则总结

| 操作 | 需要的锁 |
|------|----------|
| 创建 IPC 对象 | `ids->rwsem` (写) |
| 删除 IPC 对象 | `ids->rwsem` (写) + `ipcp->lock` |
| 获取 IPC 对象 (查找) | RCU read lock |
| 修改 IPC 对象内容 | `ipcp->lock` |
| 迭代 /proc/sysvipc | `ids->rwsem` (读) |
| semop() 快速路径 | `sem->lock` (单个信号量) |
| semop() 慢速路径 | `sma->sem_perm.lock` (整个数组) |

---

## 附录 C: 源码位置索引

| 文件 | 功能 |
|------|------|
| `/Users/sphinx/github/linux/ipc/msg.c` | System V 消息队列 |
| `/Users/sphinx/github/linux/ipc/sem.c` | System V 信号量 |
| `/Users/sphinx/github/linux/ipc/shm.c` | System V 共享内存 |
| `/Users/sphinx/github/linux/ipc/mqueue.c` | POSIX 消息队列 |
| `/Users/sphinx/github/linux/ipc/util.c` | IPC 通用框架 |
| `/Users/sphinx/github/linux/ipc/util.h` | IPC 通用框架头文件 |

---

**文档结束**
