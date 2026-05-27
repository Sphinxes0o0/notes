# Linux 内核 RCU (Read-Copy-Update) 子系统分析文档

## 目录

1. [RCU 概述](#1-rcu-概述)
2. [核心数据结构](#2-核心数据结构)
3. [同步机制](#3-同步机制)
4. [读取端 API](#4-读取端-api)
5. [SRCU (Sleepable RCU)](#5-srcu-sleepable-rcu)
6. [RCU 回调机制](#6-rcu-回调机制)
7. [RCU 架构图](#7-rcu-架构图)

---

## 1. RCU 概述

### 1.1 RCU 原理

RCU (Read-Copy-Update) 是 Linux 内核中一种高性能的同步机制，设计用于允许多个读者并发访问共享数据，同时确保写者能够安全地进行更新。

**核心思想**：
- 读者（Reader）：不需要获取锁即可访问数据，通过 `rcu_read_lock()` 和 `rcu_read_unlock()` 标记读临界区
- 写者（Writer）：在更新数据时，先复制一份副本进行修改，等待所有正在进行的读操作完成后，再将新版本替换旧版本
- 宽限期（Grace Period）：所有在 Grace Period 开始前启动的读者必须全部完成，RCU 才能回收旧数据

**关键特性**：
- 无锁读取：读者不需要任何原子操作或内存屏障（取决于架构）
- 写者延迟删除：确保所有旧读者完成后才释放资源
- 高可扩展性：读操作不涉及全局竞争

### 1.2 读临界区

```c
// 位置: kernel/rcu/tree_plugin.h, 第 412-421 行
void __rcu_read_lock(void)
{
    rcu_preempt_read_enter();
    if (IS_ENABLED(CONFIG_PROVE_LOCKING))
        WARN_ON_ONCE(rcu_preempt_depth() > RCU_NEST_PMAX);
    if (IS_ENABLED(CONFIG_RCU_STRICT_GRACE_PERIOD) && rcu_state.gp_kthread)
        WRITE_ONCE(current->rcu_read_unlock_special.b.need_qs, true);
    barrier();  // 临界区入口后的屏障
}
```

```c
// 位置: kernel/rcu/tree_plugin.h, 第 430-446 行
void __rcu_read_unlock(void)
{
    struct task_struct *t = current;

    barrier();  // 临界区出口前的屏障
    if (rcu_preempt_read_exit() == 0) {
        barrier();  // 临界区退出后检查 .s
        if (unlikely(READ_ONCE(t->rcu_read_unlock_special.s)))
            rcu_read_unlock_special(t);
    }
    if (IS_ENABLED(CONFIG_PROVE_LOCKING)) {
        int rrln = rcu_preempt_depth();
        WARN_ON_ONCE(rrln < 0 || rrln > RCU_NEST_PMAX);
    }
}
```

### 1.3 写端同步

写端通过 `synchronize_rcu()` 等待所有正在进行的读临界区完成：

```c
// 位置: kernel/rcu/tree.c, 第 3349-3386 行
void synchronize_rcu(void)
{
    unsigned long flags;
    struct rcu_node *rnp;

    RCU_LOCKDEP_WARN(lock_is_held(&rcu_bh_lock_map) ||
             lock_is_held(&rcu_lock_map) ||
             lock_is_held(&rcu_sched_lock_map),
             "Illegal synchronize_rcu() in RCU read-side critical section");
    if (!rcu_blocking_is_gp()) {
        if (rcu_gp_is_expedited())
            synchronize_rcu_expedited();
        else
            synchronize_rcu_normal();
        return;
    }
    // ... 单一 CPU 优化路径
}
```

---

## 2. 核心数据结构

### 2.1 struct rcu_head

RCU 头结构，用于 RCU 回调函数的排队。

```c
// 位置: include/linux/rcupdate.h
struct rcu_head {
    struct rcu_head *next;
    rcu_callback_t func;
};
```

**说明**：
- `next`：指向下一个 RCU 头的指针，用于构建回调链表
- `func`：回调函数指针，在宽限期结束后被调用

### 2.2 struct rcu_data

Per-CPU 数据结构，存储每个 CPU 的 RCU 状态。

```c
// 位置: kernel/rcu/tree.h, 第 188-297 行
struct rcu_data {
    /* 1) 静默状态和宽限期处理 */
    unsigned long   gp_seq;         // 跟踪 rsp->gp_seq 计数器
    unsigned long   gp_seq_needed;  // 跟踪最远的未来 GP 请求
    union rcu_noqs  cpu_no_qs;      // 此 CPU 尚未完成的 QS
    bool            core_needs_qs;  // 核心等待静默状态
    bool            beenonline;      // CPU 至少上线过一次
    struct rcu_node *mynode;       // 层次结构的叶节点

    /* 2) 批处理 */
    struct rcu_segcblist cblist;    // 分段回调链表

    /* 3) dynticks 接口 */
    int  watching_snap;             // 每个 GP 的 dynticks 跟踪
    bool rcu_need_heavy_qs;         // GP 过旧，需要重型静默状态
    bool rcu_urgent_qs;             // GP 过旧需要轻型静默状态

    /* 4) rcu_barrier(), OOM 回调和加速 */
    unsigned long barrier_seq_snap;
    struct rcu_head barrier_head;

    /* 5) 回调卸载 (NOCB) */
#ifdef CONFIG_RCU_NOCB_CPU
    struct swait_queue_head nocb_cb_wq;
    struct task_struct *nocb_gp_kthread;
    // ... 更多 NOCB 字段
#endif

    /* 6) RCU 优先级提升 */
    struct task_struct *rcu_cpu_kthread_task;

    /* 7) 诊断数据，包括 RCU CPU 停顿警告 */
    unsigned int softirq_snap;
    struct irq_work rcu_iw;
    bool rcu_iw_pending;

    long lazy_len;                   // 缓冲的 lazy 回调长度
    int cpu;
};
```

### 2.3 struct rcu_node

RCU 层次结构中的节点，用于管理宽限期检测。

```c
// 位置: kernel/rcu/tree.h, 第 41-139 行
struct rcu_node {
    raw_spinlock_t __private lock;
    unsigned long gp_seq;           // 跟踪 rsp->gp_seq
    unsigned long gp_seq_needed;    // 跟踪最远的未来 GP 请求
    unsigned long completedqs;      // 此节点所有 QSes 完成
    unsigned long qsmask;          // 需要切换以使当前 GP 继续的 CPU 或组
    unsigned long qsmaskinit;
    unsigned long qsmaskinitnext;
    unsigned long expmask;         // 需要检查以允许当前加速 GP 完成的 CPU
    unsigned long expmaskinit;
    unsigned long expmaskinitnext;
    int      grplo;                // 此处最低编号的 CPU
    int      grphi;                // 此处最高编号的 CPU
    u8       grpnum;               // 上一级的组号
    u8       level;                // 根节点为 0
    bool     wait_blkd_tasks;      // 是否需要等待阻止的任务
    struct rcu_node *parent;
    struct list_head blkd_tasks;   // 在 RCU 读临界区中阻止的任务
    struct list_head *gp_tasks;    // 指向阻止当前 GP 的第一个任务的指针
    struct list_head *exp_tasks;   // 指向阻止当前加速 GP 的第一个任务的指针
    struct rt_mutex boost_mtx;      // 用于优先级提升的互斥锁
    struct task_struct *boost_kthread_task;
#ifdef CONFIG_RCU_NOCB_CPU
    struct swait_queue_head nocb_gp_wq[2];
#endif
} ____cacheline_internodealigned_in_smp;
```

### 2.4 struct rcu_state

全局 RCU 状态，包括节点层次结构。

```c
// 位置: kernel/rcu/tree.h, 第 351-438 行
struct rcu_state {
    struct rcu_node node[NUM_RCU_NODES];    // 层次结构
    struct rcu_node *level[RCU_NUM_LVLS + 1]; // 层次级别
    int ncpus;                              // 到目前为止看到的 CPU 数
    int n_online_cpus;                      // 在线 CPU 数

    unsigned long gp_seq ____cacheline_internodealigned_in_smp;
    unsigned long gp_max;                   // 最大 GP 持续时间
    struct task_struct *gp_kthread;         // 宽限期任务
    struct swait_queue_head gp_wq;          // GP 任务等待队列
    short gp_flags;                         // GP 任务的命令
    short gp_state;                         // GP 任务睡眠状态

    struct mutex barrier_mutex;             // 保护 barrier 字段
    atomic_t barrier_cpu_count;             // 等待的 CPU 数
    struct completion barrier_completion;    // barrier 结束时唤醒
    unsigned long barrier_sequence;

    struct mutex exp_mutex;                 // 序列化加速 GP
    struct mutex exp_wake_mutex;            // 序列化唤醒
    unsigned long expedited_sequence;        // 取号
    atomic_t expedited_need_qs;             // 剩余需要检查的 CPU 数
    struct swait_queue_head expedited_wq;   // 等待检查

    unsigned long jiffies_force_qs;         // 调用 force_quiescent_state() 的时间
    unsigned long n_force_qs;               // force_quiescent_state() 的调用次数
    unsigned long gp_start;                 // GP 开始时间
    unsigned long gp_end;                   // 上次 GP 结束时间

    const char *name;                       // 结构名称
    char abbr;                              // 缩写名称

    // synchronize_rcu() 部分
    struct llist_head srs_next;             // 请求 GP 的用户
    struct llist_node *srs_wait_tail;      // 等待 GP 的用户
    struct llist_node *srs_done_tail;       // 准备好给 GP 的用户
};
```

---

## 3. 同步机制

### 3.1 synchronize_rcu()

等待所有预存在的 RCU 读临界区完成。

```c
// 位置: kernel/rcu/tree.c, 第 3349-3386 行
/**
 * synchronize_rcu - 等待一个宽限期过去
 *
 * 控制将在一个完整宽限期过去后返回给调用者，
 * 也就是说在所有当前执行的 RCU 读临界区完成之后。
 * 但请注意，从 synchronize_rcu() 返回后，
 * 调用者可能与新的 RCU 读临界区并发执行。
 */
void synchronize_rcu(void)
{
    unsigned long flags;
    struct rcu_node *rnp;

    RCU_LOCKDEP_WARN(lock_is_held(&rcu_bh_lock_map) ||
             lock_is_held(&rcu_lock_map) ||
             lock_is_held(&rcu_sched_lock_map),
             "Illegal synchronize_rcu() in RCU read-side critical section");
    if (!rcu_blocking_is_gp()) {
        if (rcu_gp_is_expedited())
            synchronize_rcu_expedited();
        else
            synchronize_rcu_normal();
        return;
    }
    // 单一 CPU 优化路径...
}
```

### 3.2 call_rcu()

将回调排队以便在宽限期结束后调用。

```c
// 位置: kernel/rcu/tree.c, 第 3249-3253 行
/**
 * call_rcu() - 排队一个回调以便在宽限期后调用
 * @head: 用于排队 RCU 回调的结构
 * @func: 宽限期后要调用的函数
 *
 * 回调函数将在一个完整 RCU 宽限期过去后的某个时间调用，
 * 也就是说在所有预存在的 RCU 读临界区完成之后。
 */
void call_rcu(struct rcu_head *head, rcu_callback_t func)
{
    __call_rcu_common(head, func, enable_rcu_lazy);
}
```

### 3.3 __call_rcu_common()

`call_rcu()` 的核心实现。

```c
// 位置: kernel/rcu/tree.c, 第 3102-3160 行
__call_rcu_common(struct rcu_head *head, rcu_callback_t func, bool lazy_in)
{
    // ... 调试检查和懒加载处理
    if (debug_rcu_head_queue(head)) {
        // 可能的重复 call_rcu()，泄漏回调
        WRITE_ONCE(head->func, srcu_leak_callback);
        WARN_ONCE(1, "call_rcu(): Leaked duplicate callback\n");
        return;
    }
    head->func = func;
    // ... 回调排队逻辑
}
```

### 3.4 rcu_barrier()

等待所有进行中的 `call_rcu()` 回调完成。

```c
// 位置: kernel/rcu/tree.c
/**
 * rcu_barrier() - 等待所有进行中的 call_rcu() 回调完成
 */
void rcu_barrier(void)
{
    // 实现细节：遍历所有 CPU，为每个 CPU 排队一个特殊的 barrier 回调
    // 只有当所有回调都完成后，barrier 才返回
}
```

### 3.5 宽限期状态机

```c
// 位置: kernel/rcu/tree.h, 第 445-454 行
/* rcu_state 结构 gp_state 字段的值 */
#define RCU_GP_IDLE     0   // 初始状态，没有 GP 进行中
#define RCU_GP_WAIT_GPS 1   // 等待宽限期开始
#define RCU_GP_DONE_GPS 2   // 宽限期开始等待完成
#define RCU_GP_ONOFF    3   // 宽限期初始化热插拔
#define RCU_GP_INIT     4   // 宽限期初始化
#define RCU_GP_WAIT_FQS 5   // 等待强制静默状态时间
#define RCU_GP_DOING_FQS 6  // 等待强制静默状态时间完成
#define RCU_GP_CLEANUP  7   // 宽限期清理开始
#define RCU_GP_CLEANED  8   // 宽限期清理完成
```

---

## 4. 读取端 API

### 4.1 rcu_read_lock()

标记 RCU 读临界区的开始。

```c
// 位置: kernel/rcu/tree_plugin.h, 第 412-421 行
/**
 * __rcu_read_lock() - RCU 可抢占实现的 rcu_read_lock()
 * 只是增加 ->rcu_read_lock_nesting，共享状态将在阻塞时更新
 */
void __rcu_read_lock(void)
{
    rcu_preempt_read_enter();
    if (IS_ENABLED(CONFIG_PROVE_LOCKING))
        WARN_ON_ONCE(rcu_preempt_depth() > RCU_NEST_PMAX);
    if (IS_ENABLED(CONFIG_RCU_STRICT_GRACE_PERIOD) && rcu_state.gp_kthread)
        WRITE_ONCE(current->rcu_read_unlock_special.b.need_qs, true);
    barrier();  /* 临界区入口后的屏障 */
}
```

### 4.2 rcu_read_unlock()

标记 RCU 读临界区的结束。

```c
// 位置: kernel/rcu/tree_plugin.h, 第 430-446 行
/**
 * __rcu_read_unlock() - RCU 可抢占实现的 rcu_read_unlock()
 * 递减 ->rcu_read_lock_nesting。如果结果为零（最外层 rcu_read_unlock()）
 * 且 ->rcu_read_unlock_special 非零，
 * 则调用 rcu_read_unlock_special() 进行清理
 */
void __rcu_read_unlock(void)
{
    struct task_struct *t = current;

    barrier();  // 临界区出口前的屏障
    if (rcu_preempt_read_exit() == 0) {
        barrier();  // 临界区退出后检查 .s
        if (unlikely(READ_ONCE(t->rcu_read_unlock_special.s)))
            rcu_read_unlock_special(t);
    }
    // ... 调试检查
}
```

### 4.3 rcu_dereference()

安全地解引用 RCU 保护的指针。

```c
// 位置: include/linux/rcupdate.h
/**
 * rcu_dereference() - 解引用 RCU 保护的指针
 * @p: 要解引用的指针
 *
 * 在 RCU 读临界区内使用，确保看到被保护数据的正确顺序。
 * 这个宏使用内存屏障来防止编译器和 CPU 的优化。
 */
#define rcu_dereference(p) \
    rcu_dereference_check(p, __UNIQUE_RCU(rcu_read_lock_held))

/* 典型用法 */
struct my_data *p;
rcu_read_lock();
p = rcu_dereference(global_ptr);
// ... 读取 p 指向的数据 ...
rcu_read_unlock();
```

### 4.4 rcu_dereference_check()

带条件检查的 RCU 解引用。

```c
// 位置: include/linux/rcupdate.h
#define rcu_dereference_check(p, c) \
    __rcu_dereference_check((p), (c) || rcu_read_lock_held_const(), \
                __UNIQUE_RCU(__rcu))
```

---

## 5. SRCU (Sleepable RCU)

### 5.1 SRCU 概述

SRCU 是一种允许在读临界区中睡眠的 RCU 变体，适用于需要在读操作中睡眠的场景。

**与普通 RCU 的区别**：
- 读临界区可以睡眠
- 每个 SRCU 结构有自己独立的 grace period 域
- 需要显式初始化和清理

### 5.2 核心数据结构

```c
// 位置: include/linux/srcu.h
struct srcu_struct {
    unsigned int __user *srcu_ctrp;  // 当前指针
    struct srcu_data __percpu *sda;  // per-CPU 数据
    struct srcu_usage *srcu_sup;     // SRCU 顶级状态
    int srcu_reader_flavor;          // 读者风格
    // ... 更多字段
};
```

### 5.3 srcu_read_lock/unlock

```c
// 位置: kernel/rcu/srcutree.c, 第 790-798 行
/**
 * __srcu_read_lock() - 在指定的 srcu_struct 中获取 SRCU 读锁
 * @ssp: 要获取读锁的 srcu_struct
 *
 * 返回一个保证为非负的索引，必须传递给匹配的 __srcu_read_unlock()
 */
int __srcu_read_lock(struct srcu_struct *ssp)
{
    struct srcu_ctr __percpu *scp = READ_ONCE(ssp->srcu_ctrp);

    this_cpu_inc(scp->srcu_locks.counter);
    smp_mb(); /* B */  /* 避免泄漏临界区 */
    return __srcu_ptr_to_ctr(ssp, scp);
}
```

```c
// 位置: kernel/rcu/srcutree.c, 第 805-810 行
/**
 * __srcu_read_unlock() - 释放指定的 srcu_struct 的 SRCU 读锁
 * @ssp: 要释放读锁的 srcu_struct
 * @idx: 之前 __srcu_read_lock() 返回的索引
 */
void __srcu_read_unlock(struct srcu_struct *ssp, int idx)
{
    smp_mb(); /* C */  /* 避免泄漏临界区 */
    this_cpu_inc(__srcu_ctr_to_ptr(ssp, idx)->srcu_unlocks.counter);
}
```

### 5.4 synchronize_srcu()

等待 SRCU 读临界区完成。

```c
// 位置: kernel/rcu/srcutree.c, 第 1477-1507 行
static void __synchronize_srcu(struct srcu_struct *ssp, bool do_norm)
{
    struct rcu_synchronize rcu;

    srcu_lock_sync(&ssp->dep_map);

    RCU_LOCKDEP_WARN(lock_is_held(ssp) ||
             lock_is_held(&rcu_bh_lock_map) ||
             lock_is_held(&rcu_lock_map) ||
             lock_is_held(&rcu_sched_lock_map),
             "Illegal synchronize_srcu() in same-type SRCU (or in RCU) read-side critical section");

    if (rcu_scheduler_active == RCU_SCHEDULER_INACTIVE)
        return;
    might_sleep();
    check_init_srcu_struct(ssp);
    init_completion(&rcu.completion);
    init_rcu_head_on_stack(&rcu.head);
    __call_srcu(ssp, &rcu.head, wakeme_after_rcu, do_norm);
    wait_for_completion(&rcu.completion);
    destroy_rcu_head_on_stack(&rcu.head);

    smp_mb(); /* 确保后续代码在 SRCU 宽限期之后排序 */
}
```

### 5.5 call_srcu()

排队 SRCU 回调。

```c
// 位置: kernel/rcu/srcutree.c, 第 1467-1472 行
/**
 * call_srcu() - 排队一个回调以便在 SRCU 宽限期后调用
 * @ssp: 排队回调的 srcu_struct
 * @rhp: 用于排队 SRCU 回调的结构
 * @func: SRCU 宽限期后要调用的函数
 */
void call_srcu(struct srcu_struct *ssp, struct rcu_head *rhp,
           rcu_callback_t func)
{
    __call_srcu(ssp, rhp, func, true);
}
```

---

## 6. RCU 回调机制

### 6.1 rcu_process_callbacks()

调用已经通过宽限期的 RCU 回调。

```c
// 位置: kernel/rcu/tree.c, 第 2540-2686 行
/**
 * rcu_do_batch() - 调用已经通过宽限期的 RCU 回调
 * @rdp: 正在处理的 per-CPU 数据
 *
 * 调用已经等待完宽限期的回调函数。
 * 限制为 rdp->blimit 指定的数量。
 */
static void rcu_do_batch(struct rcu_data *rdp)
{
    long bl;
    long count = 0;
    unsigned long flags;
    struct rcu_cblist rcl = RCU_CBLIST_INITIALIZER(rcl);
    struct rcu_head *rhp;
    // ...

    /* 如果没有准备好的回调，直接返回 */
    if (!rcu_segcblist_ready_cbs(&rdp->cblist)) {
        // ...
        return;
    }

    // 提取准备好的回调链表
    rcu_nocb_lock_irqsave(rdp, flags);
    rcu_segcblist_extract_done_cbs(&rdp->cblist, &rcl);
    // ...
    rcu_nocb_unlock_irqrestore(rdp, flags);

    /* 调用回调 */
    tick_dep_set_task(current, TICK_DEP_BIT_RCU);
    rhp = rcu_cblist_dequeue(&rcl);

    for (; rhp; rhp = rcu_cblist_dequeue(&rcl)) {
        rcu_callback_t f;

        count++;
        debug_rcu_head_unqueue(rhp);
        rcu_lock_acquire(&rcu_callback_map);
        trace_rcu_invoke_callback(rcu_state.name, rhp);

        f = rhp->func;
        debug_rcu_head_callback(rhp);
        WRITE_ONCE(rhp->func, (rcu_callback_t)0L);
        f(rhp);  // 调用实际的回调函数

        rcu_lock_release(&rcu_callback_map);
        // ... 批次限制检查
    }
    // ...
}
```

### 6.2 __call_rcu()

回调排队的核心实现。

```c
// 位置: kernel/rcu/tree.c, 第 3102-3160 行
__call_rcu_common(struct rcu_head *head, rcu_callback_t func, bool lazy_in)
{
    unsigned long flags;
    struct rcu_data *rdp;
    bool is_sync_call = func == wakeme_after_rcu;

    // 调试检查
    if (debug_rcu_head_queue(head)) {
        WRITE_ONCE(head->func, srcu_leak_callback);
        WARN_ONCE(1, "call_rcu(): Leaked duplicate callback\n");
        return;
    }

    head->func = func;
    // ...

    local_irq_save(flags);
    rdp = this_cpu_ptr(&rcu_data);

    // NOCB 处理
    if (rcu_segcblist_is_offloaded(&rdp->cblist)) {
        call_rcu_nocb(rdp, head, func, flags, lazy);
        return;
    }

    // 核心 RCU 处理
    call_rcu_core(rdp, head, func, flags);
    local_irq_restore(flags);
}
```

### 6.3 RCU 回调链表结构

```c
// 位置: kernel/rcu/rcu_segcblist.h
struct rcu_segcblist {
    struct rcu_head *head;       // 链表头
    struct rcu_head **tail;      // 链表尾指针
    unsigned long gp_seq[RCU_CBLIST_NSEGS];  // 每段的 GP 序列号
    // ...
};
```

回调链表分为多个段，每个段对应不同的 GP 状态：
- RCU_DONE_TAIL：已完成等待的回调
- RCU_WAIT_TAIL：等待中的回调
- RCU_NEXT_READY_TAIL：准备好但尚未被 GP 接纳
- RCU_NEXT_TAIL：最新排队的回调

---

## 7. RCU 架构图

### 7.1 RCU 系统整体架构

```
+------------------------------------------------------------------+
|                         RCU 系统架构                              |
+------------------------------------------------------------------+

    +------------------+       +------------------+       +------------------+
    |   读者线程 A     |       |   读者线程 B     |       |   读者线程 C     |
    +--------+---------+       +--------+---------+       +--------+---------+
             |                         |                         |
             v                         v                         v
    +------------------------------------------------------------------+
    |                      RCU 读临界区                                |
    |  rcu_read_lock() --> [访问 RCU 保护的数据] --> rcu_read_unlock() |
    +------------------------------------------------------------------+
                                        |
                                        | 多个读者可以同时持有锁
                                        | 无锁读取，高并发
                                        v
    +------------------------------------------------------------------+
    |                      RCU 写者                                   |
    |                                                                  |
    |  1. 复制副本                                                    |
    |  2. 修改副本                                                    |
    |  3. call_rcu() 或 synchronize_rcu()                            |
    |                                                                  |
    +------------------------------------------------------------------+
                                        |
                                        | 等待宽限期结束
                                        v
    +------------------------------------------------------------------+
    |                      宽限期检测                                 |
    |                                                                  |
    |  +------------+     +------------+     +------------+            |
    |  |  CPU 0     |     |  CPU 1     |     |  CPU N     |            |
    |  |  rcu_data  |     |  rcu_data  | ... |  rcu_data  |            |
    |  +----+-------+     +----+-------+     +----+-------+            |
    |       |                   |                   |                    |
    |       +---------+---------+---------+--------+                   |
    |                 |                                           |
    |                 v                                           |
    |         +----------------+                                  |
    |         |   rcu_node 0   | (根节点)                          |
    |         +-------+--------+                                  |
    |                 |                                           |
    |       +---------+---------+                                |
    |       |                   |                                 |
    |       v                   v                                 |
    |  +--------+          +--------+                             |
    |  |rcu_node|          |rcu_node|  (中间节点)                 |
    |  +--------+          +--------+                             |
    |       |                   |                                  |
    |       +---------+---------+                                  |
    |                 |                                           |
    |                 v                                           |
    |         +----------------+                                  |
    |         |   rcu_state    |                                  |
    |         |  (全局状态)     |                                  |
    |         +----------------+                                  |
    |                                                                  |
    +------------------------------------------------------------------+
                                        |
                                        | 宽限期结束
                                        v
    +------------------------------------------------------------------+
    |                      回调执行                                   |
    |                                                                  |
    |  rcu_do_batch() --> 调用回调函数 (func)                        |
    |                                                                  |
    +------------------------------------------------------------------+

+------------------------------------------------------------------+
|                         RCU 状态值                                 |
+------------------------------------------------------------------+
| RCU_GP_IDLE      = 0  | 初始状态，无 GP 进行                      |
| RCU_GP_WAIT_GPS  = 1  | 等待 GP 开始                               |
| RCU_GP_DONE_GPS  = 2  | GP 开始等待完成                           |
| RCU_GP_ONOFF     = 3  | GP 初始化热插拔                            |
| RCU_GP_INIT      = 4  | GP 初始化                                  |
| RCU_GP_WAIT_FQS  = 5  | 等待强制静默状态                           |
| RCU_GP_DOING_FQS = 6  | 执行强制静默状态                           |
| RCU_GP_CLEANUP   = 7  | GP 清理开始                               |
| RCU_GP_CLEANED   = 8  | GP 清理完成                               |
+------------------------------------------------------------------+
```

### 7.2 RCU 层次结构树（Tree RCU）

```
+------------------+      RCU_NUM_LVLS = 3 示例
|    Root Node     |
|   (rcu_node 0)   |        Level 0 (根)
+--------+---------+
         |
         +--------+---------+
         |                    |
         v                    v
+--------------+     +--------------+
|   Level 1    |     |   Level 1    |
|  rcu_node 1  |     |  rcu_node 2  |
+--------------+     +--------------+
         |                    |
         +--------+---------+---------+
         |              |              |
         v              v              v
+-----------+  +-----------+  +-----------+
|  Level 2  |  |  Level 2  |  |  Level 2  |
| rcu_node 3|  | rcu_node 4|  | rcu_node 5|
+-----------+  +-----------+  +-----------+
     |              |              |
     |   +----+     |      +----+ |
     |   |CPU0|     |      |CPU7| |
     |   +----+     |      +----+ |
     |              |              |
     +---------+----+-----=--------+
               |
               v
        Per-CPU rcu_data
```

### 7.3 SRCU 架构

```
+------------------------------------------------------------------+
|                         SRCU 架构                                 |
+------------------------------------------------------------------+

    +------------------+       +------------------+
    |   读者线程 A     |       |   读者线程 B     |
    +--------+---------+       +--------+---------+
             |                           |
             v                           v
    +------------------------------------------------------------------+
    |                    SRCU 读临界区                                |
    |                                                                  |
    |  idx = srcu_read_lock(&my_srcu);                               |
    |  // ... 访问受 SRCU 保护的数据 ...                              |
    |  srcu_read_unlock(&my_srcu, idx);                              |
    |                                                                  |
    +------------------------------------------------------------------+
                                        |
                                        | 每个 srcu_struct 有独立的 GP
                                        v
    +------------------------------------------------------------------+
    |                    srcu_struct                                  |
    |                                                                  |
    |  +------------------+                                          |
    |  |   srcu_usage     |  (全局顶级状态)                           |
    |  |  srcu_gp_seq     |                                          |
    |  |  srcu_gp_seq_needed                                      |
    |  +--------+---------+                                         |
    |           |                                                    |
    |           v                                                    |
    |  +------------------+                                         |
    |  |   srcu_node 树   |  (层次结构)                              |
    |  +--------+---------+                                         |
    |           |                                                    |
    |           v                                                    |
    |  +------------------+                                         |
    |  |   srcu_data      |  (Per-CPU)                              |
    |  |  srcu_ctrs[2]    |  // 两个索引：0 和 1                     |
    |  |  srcu_locks      |                                          |
    |  |  srcu_unlocks    |                                          |
    |  +------------------+                                         |
    +------------------------------------------------------------------+

+------------------------------------------------------------------+
|                    SRCU 双索引机制                                 |
+------------------------------------------------------------------+

    索引 0 计数                      索引 1 计数
    +------------------+              +------------------+
    | CPU0: srcu_locks[0] |          | CPU0: srcu_locks[1] |
    | CPU1: srcu_locks[0] |          | CPU1: srcu_locks[1] |
    | ...               |          | ...               |
    +------------------+              +------------------+
            |                                  |
            | 宽限期等待所有                 | 宽限期等待所有
            | 索引 0 的锁计数                | 索引 1 的锁计数
            | 变为零                         | 变为零
            v                                  v
    +------------------------------------------------------------------+
    |                     synchronize_srcu()                           |
    |                                                                  |
    |  1. 检查索引 0 的锁计数 == 索引 0 的解锁计数                   |
    |  2. 如果相等，翻转 srcu_ctrp 到索引 1                          |
    |  3. 等待索引 1 的锁计数 == 索引 1 的解锁计数                   |
    |  4. 宽限期结束                                                  |
    +------------------------------------------------------------------+
```

### 7.4 宽限期检测流程

```
+------------------------------------------------------------------+
|                    宽限期检测流程                                 |
+------------------------------------------------------------------+

1. 写者调用 synchronize_rcu() 或 call_rcu()

2. RCU GP 任务开始新的宽限期：
   +------------------+
   |  rcu_gp_init()   |
   |  设置 RCU_GP_INIT |
   +------------------+
           |
           v
   +------------------+
   |  rcu_gp_fqs()    |  (强制静默状态)
   |  遍历所有节点    |
   |  检查 qsmask     |
   +------------------+
           |
           v
   +------------------+
   |  rcu_gp_cleanup()|
   |  结束宽限期      |
   |  更新 gp_seq     |
   +------------------+
           |
           v

3. CPU 报告静默状态：
   +------------------+
   |  rcu_qs()        |  (在 rcu_note_context_switch 中调用)
   |  标记 cpu_no_qs  |
   +------------------+
           |
           v

4. 合并静默状态：
   +------------------+
   | rcu_report_qs_rdp()|
   | 更新 rcu_node    |
   | qsmask 清除      |
   +------------------+

5. 宽限期完成：
   - 所有 cpu_no_qs 清除
   - 所有 qsmask 为零
   - 回调可以执行
```

### 7.5 内存排序保证

```
+------------------------------------------------------------------+
|                    RCU 内存排序保证                               |
+------------------------------------------------------------------+

    CPU 0 (写者)                          CPU 1 (读者)
         |                                     |
         |  p = new_node;                      |
         |  rcu_assign_pointer(ptr, p);        |
         |                                     |
         |                        +----------------------+
         |                        | rcu_read_lock();    |
         |                        | r = rcu_dereference(ptr);
         |                        | // 看到 new_node    |
         |                        +----------------------+
         |                                     |
         v                                     v

    内存屏障序列：
    1. rcu_assign_pointer() 包含写入内存屏障 (wmb)
    2. rcu_dereference() 包含读取内存屏障 (rmb)
    3. 这些屏障确保：
       - 所有在 rcu_assign_pointer() 之前的内存写入
         对 rcu_dereference() 之后的读取可见
       - 即，写者对数据的修改对读者可见
```

---

## 附录 A：关键文件位置

| 文件 | 描述 |
|------|------|
| `/kernel/rcu/tree.c` | Tree RCU 主要实现 |
| `/kernel/rcu/tree.h` | Tree RCU 内部头文件 |
| `/kernel/rcu/tree_plugin.h` | 可抢占 RCU 实现 |
| `/kernel/rcu/rcupdate.c` | RCU 公共 API |
| `/kernel/rcu/srcutree.c` | SRCU 主要实现 |
| `/kernel/rcu/update.c` | RCU 更新 API |
| `/include/linux/rcupdate.h` | RCU 用户空间头文件 |
| `/include/linux/srcu.h` | SRCU 用户空间头文件 |

## 附录 B：配置选项

| 选项 | 描述 |
|------|------|
| `CONFIG_TREE_RCU` | 启用 Tree RCU |
| `CONFIG_PREEMPT_RCU` | 启用可抢占 RCU |
| `CONFIG_TINY_RCU` | 启用精简 RCU (单 CPU) |
| `CONFIG_SRCU` | 启用 SRCU |
| `CONFIG_TREE_SRCU` | 启用 Tree SRCU |
| `CONFIG_RCU_NOCB_CPU` | 启用 RCU 回调卸载 |

## 附录 C：调试接口

| 接口 | 描述 |
|------|------|
| `rcu_read_lock_held()` | 检查是否在 RCU 读临界区 |
| `synchronize_rcu()` | 同步等待宽限期 |
| `get_state_synchronize_rcu()` | 获取宽限期状态快照 |
| `poll_state_synchronize_rcu()` | 轮询宽限期是否完成 |
| `rcu_barrier()` | 等待所有回调完成 |

---

*文档生成时间：2026-04-26*
*基于 Linux 内核源码分析*
