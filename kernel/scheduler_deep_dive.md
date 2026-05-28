# Linux 调度器深度架构分析 v2

## 1. 概述

本文档是 Linux 调度器的第二轮深度分析，重点关注 CFS 红黑树算法细节、调度类层次结构、运行队列（runqueue）锁协议、负载均衡算法、调度域（scheduling domains）、以及实时调度（RT/Deadline）的实现细节。

## 2. 运行队列（runqueue）架构

### 2.1 RQ 结构

```c
/**
 * struct rq - 运行队列
 *
 * 每个 CPU 一个rq，持有该 CPU 上所有可运行进程
 */
struct rq {
    /* 锁 - 保护整个 rq */
    raw_spinlock_t lock;
    unsigned int nr_running;        // 可运行进程数
    unsigned long cpu_load[CPU_LOAD_IDX_MAX];  // CPU 负载
    unsigned long last_load_update_tick;

    /* 当前运行的进程 */
    struct task_struct *curr;
    struct task_struct *idle;
    struct mm_struct *prev_mm;

    /* 各调度类的运行队列 */
    struct cfs_rq cfs;              // CFS 队列
    struct rt_rq rt;                // RT 队列
    struct dl_rq dl;                // Deadline 队列

    /* 调度类指针（用于 pick_next_task） */
    const struct sched_class *sched_class;

    /* 时钟和时间 */
    u64 clock;                     // rq 时钟
    u64 clock_task;                // 任务时间

    /* 统计 */
    atomic_t nr_iowait;            // 等待 I/O 的进程数

    /* 负载跟踪 */
    struct sched_avg avg;           // CPU 平均负载

    /* 频率调度 */
    unsigned long cpu_capacity;
    unsigned long cpu_capacity_orig;

    /* 迁移相关 */
    struct balance_callback *balance_callback;

#ifdef CONFIG_SCHED_CORE
    struct sched_core_mask core_cookie;
    unsigned char idle_balance;
#endif
} __randomize_layout;
```

### 2.2 调度类层次

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Scheduling Class Hierarchy                           │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                sched_class (抽象基类)                          │  │
│  │  const struct sched_class *next;                            │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│         ┌────────────────────┼────────────────────┐                   │
│         ▼                    ▼                    ▼                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│  │     DL      │    │     RT      │    │     CFS     │           │
│  │ (Deadline)  │    │ (Real-Time) │    │   (Fair)    │           │
│  │  最高优先级 │    │             │    │             │           │
│  └─────────────┘    └─────────────┘    └─────────────┘           │
│                                                              │       │
│                                                              ▼       │
│                                                   ┌─────────────┐   │
│                                                   │   IDLE      │   │
│                                                   │ (最低优先级) │   │
│                                                   └─────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

调度顺序（优先级从高到低）：
1. stop_sched_class - 停止/迁移线程
2. dl_sched_class - Deadline 调度类
3. rt_sched_class - 实时调度类
4. fair_sched_class - 完全公平调度类
5. idle_sched_class - 空闲调度类
```

### 2.3 调度类操作

```c
/**
 * sched_class - 调度类操作函数集
 */
struct sched_class {
    const struct sched_class *next;

    /* 入队/出队 */
    void (*enqueue_task)(struct rq *rq, struct task_struct *p, int flags);
    void (*dequeue_task)(struct rq *rq, struct task_struct *p, int flags);

    /* 选择下一个任务 */
    struct task_struct *(*pick_next_task)(struct rq *rq,
                                         struct task_struct *prev,
                                         struct rq_flags *rf);

    /* 任务切换 */
    void (*put_prev_task)(struct rq *rq, struct task_struct *prev);
    void (*set_curr_task)(struct rq *rq);

    /* 任务唤醒 */
    void (*task_woken)(struct rq *rq, struct task_struct *p);

    /* 统计 */
    void (*update_curr)(struct rq *rq);

    /* 负载均衡 */
    void (*load_balance)(struct rq *rq);

    /* 切换调度类 */
    void (*switched_from)(struct rq *rq, struct task_struct *p);
    void (*switched_to)(struct rq *rq, struct task_struct *p);
};
```

## 3. CFS 深入实现

### 3.1 红黑树操作

```c
/**
 * __enqueue_entity - 将实体加入红黑树
 *
 * 插入算法：
 * 1. 从根开始，找到正确的插入位置
 * 2. 保持红黑树的平衡性质
 * 3. 着色为红色（默认）
 */
static void __enqueue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    struct rb_node **link = &cfs_rq->tasks_timeline.rb_root.rb_node;
    struct rb_node *parent = NULL;
    struct sched_entity *entry;
    bool leftmost = true;

    /* 查找插入位置 */
    while (*link) {
        parent = *link;
        entry = __node_2_se(parent);

        /* 比较 vruntime：左子树 < 右子树 */
        if (se->vruntime < entry->vruntime)
            link = &parent->rb_left;
        else {
            link = &parent->rb_right;
            leftmost = false;
        }
    }

    /* 插入节点 */
    rb_add_cached(&se->run_node, parent, leftmost);

    /* 如果是最左节点，更新 min_vruntime */
    if (leftmost)
        cfs_rq->min_vruntime = se->vruntime;
}

/**
 * __dequeue_entity - 从红黑树移除实体
 */
static void __dequeue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    /* 从红黑树删除 */
    rb_erase_cached(&se->run_node, &cfs_rq->tasks_timeline);
}

/**
 * pick_next_entity - 选择下一个实体
 *
 * 总是选择最左节点（最小 vruntime）
 */
static struct sched_entity *pick_next_entity(struct cfs_rq *cfs_rq)
{
    struct rb_node *left = rbs_first(&cfs_rq->tasks_timeline);

    if (!left)
        return NULL;

    return __node_2_se(left);
}
```

### 3.2 vruntime 与权重

```c
/**
 * calc_delta_fair - 计算公平的 delta
 *
 * 公式：delta_fair = delta * NICE_0_LOAD / weight
 *
 * 这确保：
 * - 高权重（低 nice）进程获得更多 CPU 时间
 * - 低权重（高 nice）进程获得更少 CPU 时间
 */
static inline u64 calc_delta_fair(u64 delta, struct sched_entity *se)
{
    if (se->load.weight == NICE_0_LOAD)
        return delta;

    return (u64)delta * NICE_0_LOAD / se->load.weight;
}

/**
 * 权重转换表
 *
 * nice 值到权重的转换：
 * nice = -20 → weight = 1024 * 1.2^20 ≈ 102400
 * nice =  0 → weight = 1024
 * nice = +19 → weight = 1024 * 1.2^-19 ≈ 8
 *
 * effective_load = weight * runnable
 */
static const int sched_prio_to_weight[40] = {
 /* -20 */     88761, 71755, 56483, 46273, 36291,
 /* -15 */     29154, 23254, 18705, 14949, 11916,
 /* -10 */      9548,  7620,  6100,  4904,  3906,
 /*  -5 */      3121,  2501,  1991,  1586,  1277,
 /*   0 */      1024,   820,   655,   526,   423,
 /*   5 */       335,   272,   215,   172,   137,
 /*  10 */       110,    87,    70,    56,    45,
 /*  15 */        36,    29,    23,    18,    15,
};
```

### 3.3 实体入队/出队

```c
/**
 * enqueue_entity - 入队实体
 *
 * @cfs_rq: CFS 运行队列
 * @se: 调度实体
 * @flags: 入队标志
 *
 * 流程：
 * 1. 更新当前执行时间
 * 2. 更新 vruntime
 * 3. 更新负载统计
 * 4. 插入红黑树
 */
static void
enqueue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se, int flags)
{
    /* 更新当前实体的执行时间 */
    if (flags & ENQUEUE_WAKEUP)
        update_curr(cfs_rq);

    /* 更新负载跟踪 */
    update_load_avg(cfs_rq, se, flags);

    /* 更新统计 */
    account_entity_enqueue(cfs_rq, se);

    /* 插入红黑树 */
    __enqueue_entity(cfs_rq, se);

    se->on_rq = 1;
}

/**
 * dequeue_entity - 出队实体
 */
static void
dequeue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se, int flags)
{
    /* 更新负载统计 */
    update_load_avg(cfs_rq, se, flags);

    /* 更新统计 */
    account_entity_dequeue(cfs_rq, se);

    /* 从红黑树删除 */
    __dequeue_entity(cfs_rq, se);

    se->on_rq = 0;
}
```

### 3.4 最小时间片保证

```c
/*
 * 最小/最大时间片保证
 *
 * CFS 不使用固定时间片，而是：
 * 1. 每个进程根据其权重获得比例 CPU 时间
 * 2. 最小时间片：sched_min_granularity_ns（默认 0.75ms）
 * 3. 最大时间片：sched_latency_ns（默认 6ms）
 *
 * 计算公式：
 * slice = latency / nr_running
 * slice = max(slice, min_granularity)
 */
static u64 __sched_min_granularity(unsigned int nr_running)
{
    return div_u64(sched_latency, nr_running);
}

static u64 max_vruntime(u64 min_vruntime, u64 vruntime)
{
    s64 delta = (s64)(vruntime - min_vruntime);
    if (delta > 0)
        min_vruntime = vruntime;
    return min_vruntime;
}
```

## 4. 实时调度（RT）

### 4.1 RT 调度类

```c
/**
 * rt_rq - 实时运行队列
 *
 * 使用简单的优先级数组
 */
struct rt_rq {
    struct rt_prio_array {
        unsigned long bitmap[BITMAP_SIZE];
        struct list_head queue[MAX_RT_PRIO];
    } active;

    unsigned int rt_nr_running;     // RT 进程数
    unsigned int rr_nr_running;     // RR 进程数

    u64 rt_throttled_clock;
    unsigned int rt_throttled;
};

/**
 * RT 调度策略
 *
 * SCHED_FIFO:
 * - 相同优先级的 FIFO 顺序
 * - 无时间片限制，运行直到阻塞
 *
 * SCHED_RR:
 * - 相同优先级的轮转调度
 * - 有时间片限制
 */
```

### 4.2 RT 调度算法

```c
/**
 * pick_next_task_rt - 选择下一个 RT 任务
 *
 * 总是选择最高优先级的任务
 */
static struct task_struct *
pick_next_task_rt(struct rq *rq, struct task_struct *prev, struct rq_flags *rf)
{
    struct task_struct *p;
    struct rt_rq *rt_rq = &rq->rt;

    /* 找到最高优先级 */
    int highest_prio = sched_find_first_bit(rt_rq->active.bitmap);

    /* 从该优先级的队列取任务 */
    p = list_entry(rt_rq->active.queue[highest_prio].next,
                   struct task_struct, se);

    return p;
}

/**
 * enqueue_task_rt - RT 任务入队
 */
static void enqueue_task_rt(struct rq *rq, struct task_struct *p, int flags)
{
    struct rt_rq *rt_rq = &rq->rt;

    /* 加入对应优先级队列 */
    list_add_tail(&p->se.run_list, &rt_rq->active.queue[p->rt_priority]);

    /* 设置优先级位图 */
    __set_bit(p->rt_priority, rt_rq->active.bitmap);

    rt_rq->rt_nr_running++;
}
```

## 5. Deadline 调度

### 5.1 Deadline 调度类

```c
/**
 * dl_rq - Deadline 运行队列
 *
 * 使用红黑树按绝对截止时间排序
 */
struct dl_rq {
    struct rb_root_broken root;            // 按 deadline 排序
    struct rb_node *rb_leftmost;           // 最近截止时间

    unsigned long dl_nr_running;           // Deadline 任务数
};

/**
 * sched_entity 中的 DEADLINE 字段
 *
 * @deadline: 绝对截止时间
 * @runtime: 总运行时间预算
 * @period: 周期
 *
 * 调度算法（GEDF）：
 * - 按 deadline - runtime 排序（earliest deadline first）
 * - 保证：对于每个任务，满足 runtime / period 的比例
 */
```

### 5.2 Deadline 调度算法

```c
/**
 * pick_next_task_dl - 选择下一个 Deadline 任务
 *
 * EDF（Earliest Deadline First）：
 * 总是选择 deadline 最早的任务
 */
static struct task_struct *
pick_next_task_dl(struct rq *rq, struct task_struct *prev, struct rq_flags *rf)
{
    struct sched_entity *se;
    struct dl_rq *dl_rq = &rq->dl;

    if (!dl_rq->dl_nr_running)
        return NULL;

    /* 总是选择最左节点（最早 deadline） */
    se = __pick_next_entity(dl_rq);
    return task_of(se);
}

/**
 * enqueue_task_dl - Deadline 任务入队
 */
static void enqueue_task_dl(struct rq *rq, struct task_struct *p, int flags)
{
    struct dl_rq *dl_rq = &rq->dl;
    struct sched_entity *se = &p->se;

    /* 按 deadline 插入红黑树 */
    __enqueue_entity(dl_rq, se);

    dl_rq->dl_nr_running++;
}
```

## 6. 负载均衡

### 6.1 调度域（Scheduling Domains）

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Scheduling Domains                                   │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  SD_ROOT (Domain 0) - 可能是 NUMA 级别                         │  │
│  │  ┌─────────────────────────────────────────────────────┐   │  │
│  │  │  SD_LV0 (CPU Domain) - 可能是 Core 级别              │   │  │
│  │  │  ┌─────────────────────────────────────────────┐   │   │  │
│  │  │  │  SD_LV1 (Thread Domain) - SMT 级别        │   │   │  │
│  │  │  └─────────────────────────────────────────────┘   │   │  │
│  │  └─────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 调度域结构

```c
/**
 * sched_domain - 调度域
 *
 * 描述一组 CPU 之间的调度关系
 */
struct sched_domain {
    /* 域级别 */
    int level;

    /* 域的 CPU 掩码 */
    struct cpumask *span;
    struct cpumask *child_span;
    struct cpumask *parent_span;

    /* 组调度 */
    struct sched_domain_shared *shared;

    /* 组信息 */
    struct sched_group *groups;

    /* 负载均衡标志 */
    unsigned long flags;

    /* 最低/最高 CPU */
    int min_cpu;
    int max_cpu;

    /* 步进（stride）*/
    int stride;

    /* 层数 */
    int num_level;
};

/**
 * sched_group - 调度组
 *
 * 域内的 CPU 组，用于组调度
 */
struct sched_group {
    unsigned long group_weight;       // 组权重
    unsigned int group_capacity;     // 组容量
    unsigned long tdflags;           // 负载均衡标志
    unsigned long last_balance;       // 上次均衡时间
    unsigned int busy_factor;        // 繁忙因子
    unsigned int imbalance_pct;      // 不平衡百分比

    struct rq *rq[0];               // 组内的运行队列
};
```

### 6.3 负载均衡算法

```c
/**
 * load_balance - 执行负载均衡
 *
 * @rq: 本地运行队列
 * @sd: 调度域
 * @idle: 是否空闲状态
 *
 * 算法：
 * 1. 找到最繁忙的组/CPU
 * 2. 从繁忙侧迁移进程到本地
 */
static int load_balance(int cpu, struct rq *rq,
                      struct sched_domain *sd, int *continue_balancing)
{
    struct sched_group *group;
    unsigned long max_load;
    int领;

    /* 找到最繁忙的组 */
    group = find_busiest_group(sd, cpu, &max_load, &imbalance);

    /* 如果不需要均衡，退出 */
    if (!imbalance)
        return 0;

    /* 从最繁忙的组迁移进程 */
    return migrate_tasks(rq, group, cpu, &imbalance);
}

/**
 * find_busiest_group - 找到最繁忙的组
 */
static struct sched_group *find_busiest_group(struct sched_domain *sd, int cpu,
                                            unsigned long *max_load,
                                            unsigned long *imbalance)
{
    struct sched_group *busiest = NULL;
    unsigned long max_load_per_cpu = 0;
    unsigned long this_load = 0;
    unsigned long this_capacity = 0;

    /* 遍历所有组 */
    for_each_cpu(cpu, sched_domain_span(sd)) {
        unsigned long load = cpu_load(cpu);
        unsigned long capacity = cpu_capacity(cpu);

        /* 计算负载比率 */
        if (load * capacity > max_load_per_cpu * this_capacity) {
            max_load_per_cpu = load;
            busiest = group;
            this_load = load;
            this_capacity = capacity;
        }
    }

    *max_load = max_load_per_cpu;
    *imbalance = (max_load_per_cpu - this_load) / 2;
    return busiest;
}
```

### 6.4 迁移机制

```c
/**
 * migrate_tasks - 迁移任务
 *
 * 从源 CPU 迁移任务到本地 CPU
 */
static int migrate_tasks(struct rq *rq, struct sched_group *group,
                        int dest_cpu, unsigned long *imbalance)
{
    struct task_struct *p;
    unsigned long util = 0;
    int detached = 0;

    /* 遍历源 CPU 上的任务 */
    for_each_cpu(cpu, sched_group_span(group)) {
        struct rq *src_rq = cpu_rq(cpu);

        /* 获取可迁移的任务 */
        p = pick_task_to_migrate(src_rq);
        if (!p)
            continue;

        /* 检查是否应该迁移 */
        if (p->nr_cpus_allowed == 1)
            continue;

        /* 迁移任务 */
        detach_task(p, src_rq, rq, dest_cpu);
        util += task_util(p);
        detached++;

        /* 达到均衡，停止 */
        if (util >= *imbalance)
            break;
    }

    return detached;
}
```

## 7. 调度策略与优先级

### 7.1 调度策略

```c
/*
 * 调度策略
 *
 * SCHED_NORMAL/SCHED_BATCH/SCHED_IDLE: CFS
 * SCHED_FIFO/SCHED_RR: 实时调度
 * SCHED_DEADLINE: Deadline 调度
 */
#define SCHED_NORMAL    0
#define SCHED_BATCH     3
#define SCHED_IDLE      5
#define SCHED_FIFO      1
#define SCHED_RR        2
#define SCHED_DEADLINE  6

/*
 * nice 值范围：-20 到 +19
 * 对应权重：sched_prio_to_weight
 */

/*
 * 实时优先级范围：1 到 MAX_RT_PRIO-1（默认 1-99）
 * nice 值映射到：MAX_RT_PRIO 到 MAX_RT_PRIO+40-1（100-139）
 */
```

### 7.2 调度类切换

```c
/**
 * check_switch_to_fair - 检查是否应该切换到 CFS
 *
 * 从 RT 切换到 CFS 的条件：
 * 1. RT 任务耗尽时间片
 * 2. RT 任务睡眠
 * 3. RT 任务显式 yield
 */
static void check_switch_to_fair(struct rq *rq, struct task_struct *prev)
{
    struct sched_entity *se = &prev->se;

    /* 如果 prev 是 RT 任务，切换 */
    if (prev->sched_class == &rt_sched_class)
        switched_from_rto(rq, prev);
}

/**
 * switched_from_rt - 从 RT 切换出来
 */
static void switched_from_rt(struct rq *rq, struct task_struct *p)
{
    /* 重新计算 vruntime */
    se->vruntime = max_vruntime(se->vruntime, cfs_rq->min_vruntime);

    /* 加入 CFS 队列 */
    enqueue_task_fair(rq, p, ENQUEUE_INITIAL);
}
```

## 8. PELT（Per-Entity Load Tracking）

### 8.1 PELT 原理

```c
/**
 * sched_avg - 调度实体负载跟踪
 *
 * 追踪实体的可运行负载，用于：
 * 1. 负载均衡
 * 2. 调度决策
 * 3. 能耗管理
 */
struct sched_avg {
    u64 last_update_time;    // 上次更新时间
    u64 load_sum;            // 负载总和
    u32 util_sum;            // 利用率总和
    u32 period_contrib;      // 周期贡献

    unsigned long load_avg;  // 移动平均值
    unsigned long util_avg;  // 利用率平均值
    long margin;             // 误差边界
};

/*
 * 负载计算公式（指数移动平均）：
 *
 * load(t) = (1 - weight) * load(t-1) + weight * runnable
 *
 * 其中 weight = 1 / (1 + lag)
 * lag 默认是 1024 (约 1.5 个周期)
 */
```

### 8.2 负载更新

```c
/**
 * ___update_load_avg - 更新负载统计
 *
 * @now: 当前时间
 * @decayed: 是否进行衰减
 */
static __always_inline int
___update_load_avg(u64 now, int cpu, struct sched_avg *sa,
                  unsigned long weight, struct sched_group *sg, int decayed)
{
    u64 delta, periods;
    u64 scale_cpu = arch_scale_cpu_capacity(cpu);

    /* 计算时间差 */
    delta = now - sa->last_update_time;
    delta >>= 10;  // 除以 1024

    if (!delta)
        return 0;

    /* 计算经过的完整周期数 */
    periods = delta / 1024;
    delta %= 1024;

    /* 应用周期贡献的衰减 */
    if (periods) {
        sa->load_sum = decay_load(sa->load_sum, periods);
        sa->util_sum = decay_load(sa->util_sum, periods);
    }

    /* 添加当前窗口的贡献 */
    sa->load_sum += weight * delta;
    sa->util_sum += scale_cpu * delta;

    return decayed;
}
```

## 9. 调度器核心流程

### 9.1 schedule 主循环

```c
/**
 * __schedule - 调度器主函数
 *
 * 在以下情况被调用：
 * 1. 进程阻塞（主动调度）
 * 2. 时间片耗尽（时钟中断）
 * 3. 调度需要（负载均衡）
 */
static void __sched notrace __schedule(bool preempt)
{
    struct rq *rq = this_rq_lock();
    struct task_struct *prev, *next;
    unsigned long *switch_count = &prev->nivcsw;

    /* 清除 TIF_NEED_RESCHED */
    sched_preempt_disable_no_rcu();

    /* 更新时钟 */
    prev->last_sched_time = sched_clock();
    rq_clock(rq);

    /* 触发调度点 */
    sched_tick_remote(rq);

    /* 更新负载统计 */
    update_rq_clock(rq);
    update_cfs_shares(rq);

    /* 选择下一个任务 */
    next = pick_next_task(rq, prev, &rf);

    /* 切换上下文 */
    if (!(prev->state & (TASK_DEAD | TASK_WAKEKILL)))
        sched_preempt_enable_no_rcu();

    if (likely(prev != next)) {
        /* 上下文切换 */
        rq->nr_switches++;
        rq->curr = next;
        ++*switch_count;

        trace_sched_switch(preempt, prev, next);

        /* 架构特定的上下文切换 */
        switch_mm_irqs_off(prev->active_mm, next->active_mm, next);

        /* 切换到新任务 */
        raw_spin_rq_unlock_irq(rq);
        cpu_switch_to(prev, next);
    } else {
        raw_spin_rq_unlock_irq(rq);
    }

    sched_preempt_enable_no_rcu();
}

/**
 * pick_next_task - 选择下一个任务
 *
 * 从最高优先级调度类开始尝试
 */
static inline struct task_struct *
pick_next_task(struct rq *rq, struct task_struct *prev, struct rq_flags *rf)
{
    const struct sched_class *class;
    struct task_struct *p;

    /* 如果所有任务都在 CFS，可能使用快速路径 */
    if (likely(prev->sched_class == &fair_sched_class &&
               rq->nr_running == rq->cfs.h_nr_running)) {
        p = fair_sched_class.pick_next_task(rq, prev, rf);
        if (likely(p))
            return p;
    }

    /* 遍历所有调度类 */
    for_each_class(class) {
        p = class->pick_next_task(rq, prev, rf);
        if (p)
            return p;
    }

    BUG();  // 不应该到达这里
}
```

### 9.2 调度延迟

```c
/*
 * 调度延迟（sched_latency_ns）
 *
 * 定义：在所有进程都获得一次 CPU 之前允许经过的时间
 * 默认值：6ms
 *
 * 计算：
 * latency = nr_running * slice
 * slice = max(latency / nr_running, min_granularity)
 *
 * 如果进程太多，超过 sched_min_granularity * nr_running > latency
 * 则增加 latency
 */
unsigned int sysctl_sched_latency = 6000000ULL;  // 6ms
unsigned int sysctl_sched_min_granularity = 750000ULL;  // 0.75ms
unsigned int sysctl_sched_max_granularity = 1000000ULL;  // 1ms
```

## 10. 参考资料

- `kernel/sched/core.c` - 调度器核心
- `kernel/sched/fair.c` - CFS 实现
- `kernel/sched/rt.c` - RT 调度类
- `kernel/sched/deadline.c` - Deadline 调度类
- `kernel/sched/idle.c` - IDLE 调度类
- `kernel/sched/sched.h` - 调度器头文件
- `include/linux/sched.h` - 调度相关结构
- `kernel/sched/topology.c` - 调度域拓扑
- `kernel/sched/loadavg.c` - 负载计算
- Documentation/scheduler/
- Documentation/scheduler/sched-domains.txt
