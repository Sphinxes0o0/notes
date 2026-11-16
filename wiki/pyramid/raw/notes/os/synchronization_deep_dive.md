# Linux 内核同步原语深度架构分析 v2

## 1. 概述

本文档是 Linux 内核同步原语的第二轮深度分析，重点关注 qspinlock 队列机制、内存屏障语义、RCU 宽限期实现、乐观自旋机制、以及各类锁的底层算法复杂度分析。

## 2. 内存屏障（Memory Barriers）

### 2.1 x86_64 内存模型

x86_64 使用 TSO（Total Store Order）内存模型：

1. Stores are globally visible in program order
2. Loads may be reordered (within certain constraints)
3. Locked instructions provide full barrier

关键保证：
- Store → Load 不会重排序（唯一的例外）
- SFENCE 针对 SF 指令（流存储）
- MFENCE 针对 LF 指令（流加载）
- LOCK prefix 提供完整内存屏障

### 2.2 内存屏障原语

```c
/**
 * 内存屏障类型
 */

/* 编译器屏障 - 防止编译器重排序 */
#define barrier() asm volatile("" ::: "memory")

/* 读屏障 - 保证屏障前的加载先于屏障后的加载 */
#define smp_rmb() do { } while (0)  // x86_64 上为空，因为 TSO

/* 写屏障 - 保证屏障前的存储先于屏障后的存储 */
#define smp_wmb() do { } while (0)  // x86_64 上为空，因为 TSO

/* 全屏障 - 保证所有操作按顺序执行 */
#define smp_mb() do { \
    asm volatile("lock; addl $0,0(%%esp)" ::: "memory"); \
} while (0)

/* 设备内存屏障 */
#define mb() asm volatile("mfence" ::: "memory")
#define rmb() asm volatile("lfence" ::: "memory")
#define wmb() asm volatile("sfence" ::: "memory")
```

### 2.3 内存屏障语义证明

定理：smp_mb() 在 x86_64 上通过 LOCK ADD 实现的内存屏障效果

证明：
1. LOCK prefix 使 CPU 发起一个 LOCK# 信号
2. LOCK# 信号强制所有加载和存储在总线上串行化
3. 这意味着屏障前的所有内存操作必须在屏障后的操作之前完成

因此：smp_mb() 提供了完全的内存排序保证

### 2.4 锁与内存序

```c
/*
 * 自旋锁的内存序保证：
 *
 * spin_lock(&lock):
 *   1. smp_mb() - 确保锁获取前的内存访问不会重排到获取后
 *   2. atomic_acquire() - 获取锁并建立获取语义
 *
 * spin_unlock(&lock):
 *   1. atomic_release() - 释放锁并建立释放语义
 *   2. smp_mb() - 确保释放前的内存访问不会重排到释放后
 *
 * 获取/释放语义：
 * - Acquire: 屏障后的所有读取都看到屏障前所有存储的结果
 * - Release: 屏障前的所有存储都在屏障后任何读取之前可见
 */

/* Mutex 获取 - 释放语义 */
static inline void mutex_lock(struct mutex *lock)
{
    atomic_long_add_acquire(&lock->owner, MUTEX_FLAG_WAITERS);
    // ... 等待逻辑 ...
}

/* Mutex 释放 - 释放语义 */
static inline void mutex_unlock(struct mutex *lock)
{
    atomic_long_sub_release(MUTEX_FLAG_WAITERS, &lock->owner);
}
```

## 3. 队列自旋锁（qspinlock）

### 3.1 qspinlock 架构

```c
/**
 * qspinlock - 队列自旋锁实现
 *
 * 锁值编码（32位）：
 *  Bits:  31                0
 *         [+---+----+--------+]
 *         | CN | PN |   LB   |
 *         +---+----+--------+
 *
 * CN (31:18) - 队列尾部 CPU 节点索引（14位）
 * PN (17:16) - pending 位（1位，表示有等待者正在自旋）
 * LB (15:00) - 锁位（1位，1=已锁定）
 *
 * 状态转换图：
 *
 *  无竞争: 0 → 1 (原子交换)
 *
 *  单等待者:
 *    0 → pending → locked → 0
 *    (1位锁 + 1位pending标记)
 *
 *  多等待者:
 *    _pending: 竞争导致原子设置 pending 位
 *    _locked: 第一个等待者释放，将锁传给下一个
 */
typedef struct qspinlock {
    atomic_t val;
} arch_spinlock_t;

/**
 * MCS 队列节点 - 每个等待 CPU 一个
 */
struct mcs_spinlock {
    struct mcs_spinlock *next;
    int locked;          // 0=等待锁, 1=获得锁
    int dummy;           // 填充对齐
};
```

### 3.2 获取锁流程

```c
/**
 * arch_spin_lock - 获取自旋锁
 * @lock: 锁指针
 *
 * 实现分四个阶段：
 * 1. 快速路径：单 CPU 获取（无竞争）
 * 2. pending 位设置：有其他等待者
 * 3. MCS 入队：真正进入队列
 * 4. MCS 等待：自旋等待前驱释放
 */
static inline void arch_spin_lock(arch_spinlock_t *lock)
{
    u32 val;

    /* 快速路径：尝试直接获取锁 */
    if (atomic_try_cmpxchg_acquire(&lock->val, &val, _Q_LOCKED_VAL))
        return;

    /* 慢速路径 */
    __arch_spin_lock(lock);
}

static __always_inline void __arch_spin_lock(arch_spinlock_t *lock)
{
    struct mcs_spinlock *node = this_cpu_ptr(&mcs_nodes[0]);
    u32 val;

    /* 无竞争检查 */
    if (atomic_read(&lock->val) == 0)
        goto trylock;

    /* 入队并自旋等待 */
    arch_mcs_spin_lock_contended(&lock->val, node);

trylock:
    /* 尝试获取锁 */
    for (;;) {
        val = atomic_read(&lock->val);
        if ((val & ~_Q_PENDING_MASK) == 0 &&
            atomic_try_cmpxchg_acquire(&lock->val, &val, val | _Q_LOCKED_VAL))
            return;
        cpu_relax();
    }
}

/**
 * arch_mcs_spin_lock_contended - MCS 入队自旋
 *
 * 核心思想：每个等待者创建一个 MCS 节点
 * 节点形成链表：CPU0 → CPU1 → CPU2 → ...
 * 只有队首节点自旋等待锁，其他节点等待前驱
 */
static __always_inline void
arch_mcs_spin_lock_contended(u32 *lock_addr, struct mcs_spinlock *node)
{
    struct mcs_spinlock *prev;
    int val;

    /* 设置当前节点为等待状态 */
    node->locked = 0;
    node->next = NULL;

    /* 获取前驱并链接 */
    prev = xchg(&per_cpu_ptr(&lock_addr, 1)->next, node);
    if (prev) {
        /* 有前驱，自旋等待前驱的 locked 变 1 */
        WRITE_ONCE(prev->next, node);
        arch_wait_for_lock(lock_addr, _Q_PENDING_VAL);
        while (!READ_ONCE(node->locked))
            cpu_relax();
    }

    /* 轮到我们，检查锁状态 */
    val = atomic_read((atomic_t *)lock_addr);
    if ((val & ~_Q_PENDING_MASK) != 0)
        goto wait;

    /* 锁空闲，尝试获取 */
    if (atomic_try_cmpxchg_acquire((atomic_t *)lock_addr, &val,
                                   val | _Q_LOCKED_VAL))
        return;

wait:
    while (!READ_ONCE(node->locked))
        cpu_relax();
}
```

### 3.3 释放锁流程

```c
/**
 * arch_spin_unlock - 释放自旋锁
 * @lock: 锁指针
 *
 * 释放逻辑：
 * 1. 清除锁位
 * 2. 如果有等待者，唤醒队首等待者
 */
static inline void arch_spin_unlock(arch_spinlock_t *lock)
{
    u32 val = atomic_read(&lock->val);

    /* 检查是否有 MCS 队列 */
    if (val & _Q_TAIL_MASK) {
        /* 有等待者，通过 MCS 链传递锁 */
        struct mcs_spinlock *next = READ_ONCE(per_cpu_ptr(&mcs_nodes[0])->next);
        if (next) {
            /* 唤醒下一个等待者 */
            smp_store_release(&next->locked, 1);
            return;
        }
    }

    /* 无等待者，直接释放 */
    atomic_set_release(&lock->val, 0);
}
```

### 3.4 qspinlock 性能分析

复杂度分析：
- 获取锁（无竞争）：O(1)
- 获取锁（单等待者）：O(1) + 自旋
- 获取锁（多等待者）：O(1) + 自旋

缓存行 bouncing 最小化：
- MCS 队列使用 per-CPU 节点
- 只有链表链接操作需要跨 CPU 通信
- 锁传递只需要单次缓存行传输

对比传统自旋锁：
- 传统自旋锁：所有竞争者都在同一缓存行上自旋 → 缓存行 bouncing
- qspinlock：每个 CPU 在自己的节点上自旋 → 无 bouncing

## 4. 互斥锁（Mutex）深入

### 4.1 互斥锁状态机

```c
/*
 * mutex owner 编码：
 *   0: 锁空闲
 *   current: 持有者线程指针
 *   MUTEX_FLAG_WAITERS: 有等待者标志
 *   MUTEX_FLAG_HANDOFF: 交接标志（用于饥饿避免）
 *
 * 状态转换：
 *
 *   [UNLOCKED] ──trylock──→ [LOCKED by self]
 *       ↑                          │
 *       │                          │
 *       └──────unlock──────────────┘
 *
 *   [LOCKED] ──wait──→ [LOCKED+WAITERS] ──wake──→ [LOCKED by waiter]
 *                              ↑                            │
 *                              └────────────────────────────┘
 *
 *   [LOCKED] ──handoff──→ [LOCKED+HANDOFF] ──wake──→ [LOCKED by waiter]
 */
```

### 4.2 乐观自旋（Optimistic Spinning）

```c
/**
 * osq_lock - 进入乐观自旋队列
 *
 * 原理：当锁持有者正在运行时，等待者自旋等待比阻塞更高效
 * 因为：
 * 1. 线程切换开销大（数微秒）
 * 2. 自旋等待只需几十个周期
 * 3. 锁持有时间通常很短
 */
static __always_inline bool osq_lock(struct optimistic_spin_queue *osq)
{
    struct optimistic_spin_node *node = this_cpu_ptr(osq->nodes);
    struct optimistic_spin_node *prev;
    int curr;

    node->locked = 0;
    node->next = NULL;

    /* 入队并获取前驱 */
    prev = xchg(&osq->tail, node);
    if (!prev) {
        /* 队列为空，我们直接获得锁 */
        return true;
    }

    /* 有前驱，链接并自旋 */
    WRITE_ONCE(prev->next, node);

    /* 自旋等待前驱释放或锁被交接 */
    while (!READ_ONCE(node->locked)) {
        if (need_resched())
            return false;
        cpu_relax();
    }

    return true;
}

/**
 * osq_unlock - 退出乐观自旋队列
 */
static __always_inline void osq_unlock(struct optimistic_spin_queue *osq)
{
    struct optimistic_spin_node *node = osq->tail;

    /* 标记自己为最后节点 */
    smp_store_release(&osq->tail, NULL);

    /* 如果队列只有我们，直接释放 */
    if (!READ_ONCE(node->next))
        return;

    /* 唤醒下一个等待者 */
    smp_store_release(&node->next->locked, 1);
}
```

### 4.3 饥饿避免

```c
/*
 * HANDOFF 机制解决饥饿问题：
 *
 * 问题：如果多个等待者竞争，锁可能总是被新来的自旋者获取
 * 解决：设置 HANDOFF 标志，将锁直接交给等待队列队首
 *
 * 实现：
 * 1. 等待者检测到锁被非公平获取
 * 2. 设置 MUTEX_FLAG_HANDOFF
 * 3. 解锁时发现 HANDOFF，直接唤醒等待者
 */
```

## 5. RCU（Read-Copy-Update）深入

### 5.1 RCU 内存模型

```
RCU 宽限期（Grace Period）概念：

┌─────────────────────────────────────────────────────────────┐
│                        Grace Period                          │
│  ───────────────────────────────────────────────────────→   │
│                                                              │
│  Writer: ──[W: old→new]────────────────[U: free old]──    │
│                                                              │
│  Reader0:      ──[R]───────────────────────────────[R]──    │
│                     ↓ wait for GP                            │
│                     ──────────────────────────────────────   │
│                                                              │
│  Reader1:           ──[R]───────────────────────────[R]──    │
│                                                              │
│  关键不变量：                                                   │
│  - GP 结束时，所有在 GP 开始前的读者必须已完成                   │
│  - 只有满足上述条件，旧数据才能安全释放                          │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 树形 RCU 实现

```c
/**
 * rcu_node - RCU 树的节点
 *
 * 每个节点对应一个 CPU 子树
 */
struct rcu_node {
    raw_spinlock_t lock;           // 保护该节点
    atomic_t qsmask;              // 需要同步的子节点位图
    atomic_t expmasks;           // 正在 expedited GP 的子节点
    struct rcu_node *parent;     // 父节点
    int grp_num;                 // 本节点在父节点中的序号
};

/**
 * rcu_state - RCU 全局状态
 */
struct rcu_state {
    struct rcu_node node[RCU_NUM_NODES];  // RCU 树节点
    int level;                           // 树深度
    struct rcu_data *rda;                // 每 CPU 数据
};

/**
 * rcu_data - 每 CPU RCU 数据
 */
struct rcu_data {
    /* GP 状态 */
    unsigned long gp_seq;               // 当前 GP 序列号
    unsigned long gp_wrap;             // 溢出计数
    struct rcu_node *mynode;          // 对应的树节点

    /* 等待的回调 */
    struct rcu_head *nxtlist;         // 等待调用的回调链表
    struct rcu_head **nxttail;       // 链表尾
    struct rcu_head *curlist;        // 当前正在等待的链表
    struct rcu_head **curtail;       // 当前链表尾
};
```

### 5.3 宽限期检测算法

```c
/**
 * rcu_gp_start - 开始新的宽限期
 *
 * 广播信号：设置所有叶子节点的 qsmask
 * 启动新一轮 GP 检测
 */
static void rcu_gp_start(struct rcu_state *rsp)
{
    int cpu;
    struct rcu_node *rnp;

    /* 标记所有叶子节点需要报告 */
    for_each_possible_cpu(cpu) {
        rnp = per_cpu_ptr(rsp->rda, cpu)->mynode;
        atomic_or(rnp->qsmask, rnp->grp_mask);
    }

    /* 增加 GP 序列号 */
    WRITE_ONCE(rsp->gp_seq, rsp->gp_seq + 1);
}

/**
 * rcu_gp_cleanup - 完成宽限期
 *
 * 条件：所有叶子节点都已完成（qsmask == 0）
 */
static void rcu_gp_cleanup(struct rcu_state *rsp)
{
    struct rcu_node *rnp0 = rsp->rda[0].mynode;
    struct rcu_node *rnp;

    /* 传播合并 qsmask */
    for (rnp = rnp0->parent; rnp != NULL; rnp = rnp->parent) {
        atomic_and(~rnp->qsmask, rnp->qsmask);
    }
}

/**
 * rcu_report_qs_rdp - CPU 报告完成
 *
 * 当 CPU 的 rcu_data 需要同步时调用
 * 设置叶子节点的对应位为 0
 */
static bool rcu_report_qs_rdp(struct rcu_data *rdp)
{
    struct rcu_node *rnp = rdp->mynode;

    /* 清除本 CPU 的位 */
    if (!atomic_and_return(~rdp->grpmask, &rnp->qsmask))
        return false;  // 还有其他需要同步的

    /* 传播到父节点 */
    rcu_report_parent_qs(rnp);
    return true;
}
```

### 5.4 RCU 回调执行

```c
/**
 * __call_rcu - 注册 RCU 回调
 *
 * 注册的回调在宽限期结束后被调用
 */
void __call_rcu(struct rcu_head *head, rcu_callback_t func,
               struct rcu_state *rsp)
{
    unsigned long flags;
    struct rcu_data *rdp = this_cpu_ptr(rsp->rda);

    head->func = func;
    head->next = NULL;

    local_irq_save(flags);
    *rdp->nxttail = head;
    rdp->nxttail = &head->next;

    /* 检查是否需要启动 GP */
    if (rcu_segcblist_n_cbs(&rdp->cblist) &&
        !rcu_gp_in_progress(rsp))
        rcu_gp_start();

    local_irq_restore(flags);
}

/**
 * rcu_core - 处理 RCU 回调
 *
 * 在软中断或调度中调用
 */
static void rcu_core(struct softirq_action *h)
{
    struct rcu_state *rsp = &rcu_state;

    /* 处理完成的回调 */
    if (rsp->nxtlist) {
        rcu_process_callbacks(rsp);
    }
}
```

## 6. 读写信号量深入

### 6.1 计数编码详解

```c
/*
 * rw_semaphore 计数布局（32位）：
 *
 *   Bits:  31                         0
 *         [+---------------------------+]
 *         |          count             |
 *         +---------------------------+
 *
 * 解码：
 *   count == RWSEM_LOCKED: 写锁持有（count = -1）
 *   count < 0: 写锁持有
 *   count > 0: 有 count 个读者持有锁
 *
 * 常量定义：
 */
#define RWSEM_UNLOCKED_VALUE       0
#define RWSEM_READER_BIAS          1
#define RWSEM_WRITER_BIAS       (-RWSEM_READER_BIAS)
#define RWSEM_LOCKED_VALUE     RWSEM_WRITER_BIAS

/*
 * 读者获取：
 *   count += RWSEM_READER_BIAS
 *   如果 count < 0，说明有写者，失败
 *
 * 写者获取：
 *   尝试将 count 从 0 原子地设为 RWSEM_LOCKED_VALUE
 *   如果失败，进入等待队列
 */
```

### 6.2 写者优先实现

```c
/**
 * rwsem_down_write_failed - 写者等待获取写锁
 *
 * 实现写者优先：
 * 1. 检查是否有写者在队首
 * 2. 如果有，自旋等待
 * 3. 如果没有，尝试获取锁
 */
static struct rw_semaphore *
__rwsem_down_write_failed(struct rw_semaphore *sem)
{
    struct rwsem_waiter waiter;
    struct rcu_head *head;

    /* 标记为写者 */
    waiter.task = current;
    waiter.type = RWSEM_WAITING_FOR_WRITE;

    /* 加入等待队列（队首） */
    raw_spin_lock(&sem->wait_lock);
    list_add_tail(&waiter.list, &sem->wait_list);

    /* 尝试唤醒前面的写者 */
    rwsem_mark_wake(sem, &wake_q);

    raw_spin_unlock(&sem->wait_lock);

    /* 睡眠等待 */
    while (true) {
        if (rwsem_try_write_lock(sem, &head))
            break;
        schedule();
        set_current_state(TASK_UNINTERRUPTIBLE);
    }

    return sem;
}
```

## 7. Seqlock 深入

### 7.1 Seqlock 原理

```c
/*
 * Seqlock 核心思想：
 *
 * 写者：获取序列号（奇数）→ 修改数据 → 释放序列号（偶数）
 * 读者：读取序列号 → 读取数据 → 再次读取序列号验证
 *
 * 如果两次序列号相同，说明读取期间没有写者
 */

/**
 * read_seqbegin - 开始读取
 *
 * 返回当前序列号
 */
static unsigned read_seqbegin(const seqcount_t *s)
{
    unsigned ret = READ_ONCE(s->sequence);
    return ret;
}

/**
 * read_seqretry - 验证读取结果
 *
 * 如果序列号变了，说明有写者介入，需要重试
 */
static bool read_seqretry(const seqcount_t *s, unsigned start)
{
    return READ_ONCE(s->sequence) != start;
}

/**
 * write_seqlock - 写者获取 seqlock
 */
static inline void write_seqlock(seqcount_t *s)
{
    raw_spin_lock(&s->lock);
    WRITE_ONCE(s->sequence, s->sequence + 1);
}

/**
 * write_sequnlock - 写者释放 seqlock
 */
static inline void write_sequnlock(seqcount_t *s)
{
    WRITE_ONCE(s->sequence, s->sequence + 1);
    raw_spin_unlock(&s->lock);
}
```

### 7.2 Seqlock 使用场景

```c
/*
 * 适合使用 seqlock 的场景：
 *
 * 1. 读多写少
 * 2. 写入不阻塞读取
 * 3. 写入时间短
 *
 * 典型使用：
 * - jiffies 更新
 * - 某些计时数据
 * - 路由表查找
 */

/* 示例：时间更新 */
struct { seqcount_t seq; struct timespec ts; } uptime = {
    .seq = SEQCNT_ZERO(uptime.seq),
    .ts = {0},
};

void update_uptime(void)
{
    write_seqlock(&uptime.seq);
    uptime.ts = current_kernel_time();
    write_sequnlock(&uptime.seq);
}

void get_uptime(struct timespec *ts)
{
    unsigned seq;
    do {
        seq = read_seqbegin(&uptime.seq);
        *ts = uptime.ts;
    } while (read_seqretry(&uptime.seq, seq));
}
```

## 8. 原子操作与 CAS

### 8.1 原子整数操作

```c
/**
 * atomic_t / atomic64_t
 *
 * 提供原子整数操作
 */

/* 基本操作 */
atomic_read(v)                    // 读取
atomic_set(v, i)                 // 设置
atomic_add(i, v)                 // 加
atomic_sub(i, v)                 // 减
atomic_inc(v) / atomic_dec(v)    // 增1/减1

/* 返回新值 */
atomic_add_return(i, v)          // 返回新值
atomic_inc_return(v)             // 返回新值

/* 修改操作 */
atomic_cmpxchg(v, old, new)     // CAS
atomic_xchg(v, new)             // 交换
atomic_fetch_add(i, v)          // 返回旧值
```

### 8.2 CAS 算法实现

```c
/**
 * atomic_try_cmpxchg - 尝试原子 CAS
 *
 * 如果 *ptr == old，则设置 *ptr = new
 * 返回 true 如果成功
 *
 * 实现：
 *   lock cmpxchg %rax, (%rdx)
 *   如果成功，ZF=1, %rax = old（期望值）
 *   如果失败，ZF=0, %rax = *ptr（实际值）
 */
static __always_inline bool
atomic_try_cmpxchg(atomic_t *v, int *old, int new)
{
    int r, o = *old;
    asm volatile(LOCK_PREFIX "cmpxchg %[new], %[v]"
                 : [v] "+m" (v->counter),
                   "=a" (r)
                 : [new] "r" (new),
                   "0" (o)
                 : "memory");
    *old = r;
    return r == o;
}
```

### 8.3 引用计数安全

```c
/*
 * refcount_t vs atomic_t 的区别：
 *
 * refcount_t 提供：
 * 1. 溢出检测（BUG_ON 当计数溢出）
 * 2. 饱和语义（REFCOUNT_SATURATED）
 * 3. 专门的 API 防止误用
 */

/**
 * refcount_inc - 增加引用计数
 *
 * 如果已经达到最大，返回 false
 */
static __always_inline void refcount_inc(refcount_t *r)
{
    if (unlikely(!refcount_add_not_zero(1, r)))
        refcount_warn_saturate(r, REFCOUNT_ADD_UAF);
}
```

## 9. 复杂度与性能分析

### 9.1 锁操作复杂度

| 锁类型 | 获取 | 释放 | 说明 |
|--------|------|------|------|
| spinlock | O(1) | O(1) | 无竞争时 |
| qspinlock | O(1) | O(1) | 含 MCS 入队 |
| mutex | O(1)* | O(1) | *可能睡眠 |
| rw_sem | O(1)* | O(1) | *可能睡眠 |
| seqlock | O(1) | O(1) | 读者 O(1)，写者 O(1) |
| RCU | O(1) | GP | 读者 O(1)，写者 O(GP) |

### 9.2 缓存行竞争

锁竞争导致的缓存行 bouncing：

**传统自旋锁：**
```
┌─────────┐         ┌─────────┐         ┌─────────┐
│ CPU 0   │◄───────►│  Lock   │◄───────►│ CPU 1   │
│ (写)    │ MESI    │ (1行)   │ MESI    │ (写)    │
└─────────┘         └─────────┘         └─────────┘
```
每次自旋都需要锁总线访问

**qspinlock：**
```
┌─────────┐         ┌─────────┐         ┌─────────┐
│ CPU 0   │         │ CPU 1   │         │ CPU 2   │
│ node[0] │────────►│ node[1] │────────►│ node[2] │
└─────────┘         └─────────┘         └─────────┘
```
每个 CPU 只在自己的节点上自旋

## 10. 参考资料

- `arch/x86/include/asm/spinlock.h` - 自旋锁实现
- `kernel/locking/mutex.c` - 互斥锁实现
- `kernel/rcu/tree.c` - RCU 树实现
- `kernel/locking/rwsem.c` - 读写信号量实现
- `include/linux/seqlock.h` - Seqlock 接口
- `include/linux/atomic.h` - 原子操作接口
- `Documentation/memory-barriers.txt` - 内存屏障文档
- Documentation/RCU/
- "Is Parallel Programming Hard?" - Paul McKenney
