# Linux 内核实时(RT)调度器分析

## 1. RT调度器核心数据结构 (kernel/sched/rt.c)

### 1.1 struct rt_rq (运行队列)

**文件**: `kernel/sched/sched.h:831-858`

```c
struct rt_rq {
    struct rt_prio_array  active;           // 优先级队列
    unsigned int          rt_nr_running;     // RT任务数量
    unsigned int          rr_nr_running;     // RR任务数量
    struct {
        int  curr;  /* 最高优先级RT任务 */
        int  next;  /* 次高优先级 */
    } highest_prio;
    bool                  overloaded;         // 是否过载(有多任务等待)
    struct plist_head     pushable_tasks;    // 可迁移的RT任务链表

    int                   rt_queued;

#ifdef CONFIG_RT_GROUP_SCHED
    int                   rt_throttled;      // 是否被节流
    u64                   rt_time;           // 已消耗RT时间
    u64                   rt_runtime;        // 分配的RT时间配额
    raw_spinlock_t        rt_runtime_lock;
    unsigned int          rt_nr_boosted;
    struct rq             *rq;
#endif
};
```

### 1.2 struct rt_prio_array (优先级数组)

**文件**: `kernel/sched/sched.h:311-314`

```c
struct rt_prio_array {
    DECLARE_BITMAP(bitmap, MAX_RT_PRIO+1); /* 优先级位图 */
    struct list_head queue[MAX_RT_PRIO];    /* 每个优先级的任务链表 */
};
```

**O(1)选择原理**: `sched_find_first_bit()` 能在常数时间内找到最高优先级的已占用队列。

### 1.3 struct sched_rt_entity

**文件**: `include/linux/sched.h:623-639`

```c
struct sched_rt_entity {
    struct list_head   run_list;        // 运行链表节点
    unsigned long     timeout;         // 超时时间
    unsigned long     watchdog_stamp;
    unsigned int      time_slice;       // SCHED_RR时间片
    unsigned short    on_rq;
    unsigned short    on_list;

    struct sched_rt_entity *back;
#ifdef CONFIG_RT_GROUP_SCHED
    struct sched_rt_entity *parent;
    struct rt_rq           *rt_rq;
    struct rt_rq           *my_q;
#endif
};
```

## 2. 核心函数实现

### 2.1 enqueue_task_rt() - 入队操作

**文件**: `kernel/sched/rt.c:1431-1448`

```c
static void
enqueue_task_rt(struct rq *rq, struct task_struct *p, int flags)
{
    struct sched_rt_entity *rt_se = &p->rt;

    if (flags & ENQUEUE_WAKEUP)
        rt_se->timeout = 0;

    check_schedstat_required();
    update_stats_wait_start_rt(rt_rq_of_se(rt_se), rt_se);

    enqueue_rt_entity(rt_se, flags);

    if (task_is_blocked(p))
        return;

    if (!task_current(rq, p) && p->nr_cpus_allowed > 1)
        enqueue_pushable_task(rq, p);
}
```

### 2.2 pick_next_task_rt() - 任务选择

**文件**: `kernel/sched/rt.c:1671-1701`

```c
static struct sched_rt_entity *pick_next_rt_entity(struct rt_rq *rt_rq)
{
    struct rt_prio_array *array = &rt_rq->active;
    struct sched_rt_entity *next = NULL;
    struct list_head *queue;
    int idx;

    idx = sched_find_first_bit(array->bitmap);  // O(1)找到最高优先级
    BUG_ON(idx >= MAX_RT_PRIO);

    queue = array->queue + idx;
    if (WARN_ON_ONCE(list_empty(queue)))
        return NULL;
    next = list_entry(queue->next, struct sched_rt_entity, run_list);

    return next;
}

static struct task_struct *_pick_next_task_rt(struct rq *rq)
{
    struct sched_rt_entity *rt_se;
    struct rt_rq *rt_rq  = &rq->rt;

    do {
        rt_se = pick_next_rt_entity(rt_rq);
        if (unlikely(!rt_se))
            return NULL;
        rt_rq = group_rt_rq(rt_se);
    } while (rt_rq);

    return rt_task_of(rt_se);
}
```

### 2.3 push_rt_task() - 推送任务(抢占式迁移)

**文件**: `kernel/sched/rt.c:1939-1961`

```c
static int push_rt_task(struct rq *rq, bool pull)
{
    struct task_struct *next_task;
    struct rq *lowest_rq;
    int ret = 0;

    if (!rq->rt.overloaded)
        return 0;

    next_task = pick_next_pushable_task(rq);
    if (!next_task)
        return 0;

retry:
    /*
     * 如果next_task比当前running任务优先级更高,
     * 直接重调度当前CPU
     */
    if (unlikely(next_task->prio < rq->donor->prio)) {
        resched_curr(rq);
        return 0;
    }
    // ... 迁移逻辑
}
```

### 2.4 pull_rt_task() - 拉取任务

**文件**: `kernel/sched/rt.c:2240-2260`

```c
static void pull_rt_task(struct rq *this_rq)
{
    int this_cpu = this_rq->cpu, cpu;
    bool resched = false;
    struct task_struct *p, *push_task;
    struct rq *src_rq;
    int rt_overload_count = rt_overloaded(this_rq);

    if (likely(!rt_overload_count))
        return;

    smp_rmb();

    /* 如果是唯一的过载CPU，什么都不做 */
    if (rt_overload_count == 1 &&
        cpumask_test_cpu(this_rq->cpu, this_rq->rd->rto_mask))
        return;
    // ... 从其他CPU迁移RT任务的逻辑
}
```

## 3. RT调度策略

### 3.1 策略定义

**文件**: `include/uapi/linux/sched.h:115-120`

```c
#define SCHED_NORMAL     0  // CFS调度
#define SCHED_FIFO       1  // 先进先出，无时间片
#define SCHED_RR         2  // 轮转，有时间片
#define SCHED_BATCH      3  // 批处理
#define SCHED_IDLE       5  // 空闲
#define SCHED_DEADLINE   6  // 截止时间优先
#define SCHED_EXT        7  // 扩展调度器(SCX)
```

### 3.2 SCHED_FIFO vs SCHED_RR

| 特性 | SCHED_FIFO | SCHED_RR |
|------|------------|----------|
| 时间片 | 无穷大(直到阻塞) | 有限时间片(sched_rr_timeslice) |
| 同优先级 | 按入队顺序 | 轮转执行 |
| 抢占 | 可被更高优先级抢占 | 可被更高优先级抢占 |
| 时间片耗尽 | 不发生 | 重新入队尾部 |

**时间片管理** (`kernel/sched/rt.c:2530-2552`):

```c
if (p->policy != SCHED_RR)
    return;

if (--p->rt.time_slice)
    return;

p->rt.time_slice = sched_rr_timeslice;

/*
 * 如果不是唯一任务，重新入队到队列尾部
 */
for_each_sched_rt_entity(rt_se) {
    if (rt_se->run_list.prev != rt_se->run_list.next) {
        requeue_task_rt(rq, p, 0);
        resched_curr(rq);
        return;
    }
}
```

## 4. RT节流机制 (RT-throttling)

### 4.1 核心参数

**文件**: `kernel/sched/rt.c:24-50`

```c
int sysctl_sched_rt_runtime = 950000;  // 默认95%
/*
 * /proc/sys/kernel/sched_rt_period_us: 周期(默认1ms = 1000000us)
 * /proc/sys/kernel/sched_rt_runtime_us: 运行时长(默认950000us)
 *
 * 例如: 1秒周期内，RT任务最多运行0.95秒
 */
```

### 4.2 带宽控制函数

**文件**: `kernel/sched/rt.c:863-889`

```c
static int sched_rt_runtime_exceeded(struct rt_rq *rt_rq)
{
    u64 runtime = sched_rt_runtime(rt_rq);

    if (rt_rq->rt_throttled)
        return rt_rq_throttled(rt_rq);

    if (runtime >= sched_rt_period(rt_rq))
        return 0;

    balance_runtime(rt_rq);
    runtime = sched_rt_runtime(rt_rq);
    if (runtime == RUNTIME_INF)
        return 0;

    if (rt_rq->rt_time > runtime) {
        struct rt_bandwidth *rt_b = sched_rt_bandwidth(rt_rq);

        if (likely(rt_b->rt_runtime)) {
            rt_rq->rt_throttled = 1;
            printk_deferred_once("sched: RT throttling activated\n");
        }
        return 1;
    }
    return 0;
}
```

### 4.3 update_curr_rt() - 时间记账

**文件**: `kernel/sched/rt.c:974-1007`

```c
static void update_curr_rt(struct rq *rq)
{
    struct task_struct *donor = rq->donor;
    s64 delta_exec;

    if (donor->sched_class != &rt_sched_class)
        return;

    delta_exec = update_curr_common(rq);
    if (unlikely(delta_exec <= 0))
        return;

#ifdef CONFIG_RT_GROUP_SCHED
    struct sched_rt_entity *rt_se = &donor->rt;

    if (!rt_bandwidth_enabled())
        return;

    for_each_sched_rt_entity(rt_se) {
        struct rt_rq *rt_rq = rt_rq_of_se(rt_se);
        int exceeded;

        if (sched_rt_runtime(rt_rq) != RUNTIME_INF) {
            raw_spin_lock(&rt_rq->rt_runtime_lock);
            rt_rq->rt_time += delta_exec;
            exceeded = sched_rt_runtime_exceeded(rt_rq);
            if (exceeded)
                resched_curr(rq);
            raw_spin_unlock(&rt_rq->rt_runtime_lock);
            if (exceeded)
                do_start_rt_bandwidth(sched_rt_bandwidth(rt_rq));
        }
    }
#endif
}
```

## 5. Deadline调度器 (kernel/sched/deadline.c)

### 5.1 struct sched_dl_entity

**文件**: `include/linux/sched.h:644-749`

```c
struct sched_dl_entity {
    struct rb_node  rb_node;

    /* 原始调度参数 */
    u64  dl_runtime;  /* 每个实例最大运行时间 */
    u64  dl_deadline; /* 每个实例的相对截止时间 */
    u64  dl_period;   /* 两个实例的间隔(周期) */
    u64  dl_bw;       /* dl_runtime / dl_period (带宽) */
    u64  dl_density;  /* dl_runtime / dl_deadline */

    /* 实际调度参数 - 执行期间持续更新 */
    s64  runtime;     /* 本实例剩余运行时间(可能<0表示超限) */
    u64  deadline;    /* 本实例绝对截止时间 */
    unsigned int flags;

    /* 标志位 */
    bool dl_throttled;  /* 运行时耗尽，需要等待补充 */
    bool dl_yielded;     /* 任务在消耗完运行时前放弃CPU */
    bool dl_non_contending; /* 任务阻塞但还未从running_bw移除 */

    struct hrtimer dl_timer;         /* 运行时补充计时器 */
    struct hrtimer inactive_timer;   /* 非活跃计时器 */

    bool dl_server;  /* 是否为DL服务器 */
    struct task_struct *(*server_start)(struct sched_dl_entity *);
    void (*server_stop)(struct sched_dl_entity *);

#ifdef CONFIG_RT_MUTEXES
    struct sched_dl_entity *pi_se;   /* 继承的PI实体 */
#endif
};
```

### 5.2 enqueue_task_dl()

**文件**: `kernel/sched/deadline.c:2292-2336`

```c
static void enqueue_task_dl(struct rq *rq, struct task_struct *p, int flags)
{
    if (is_dl_boosted(&p->dl)) {
        if (p->dl.dl_throttled) {
            cancel_replenish_timer(&p->dl);
            p->dl.dl_throttled = 0;
        }
    } else if (!dl_prio(p->normal_prio)) {
        p->dl.dl_throttled = 0;
        if (!(flags & ENQUEUE_REPLENISH))
            printk_deferred_once("sched: DL de-boosted task PID %d: REPLENISH flag missing\n",
                         task_pid_nr(p));
        return;
    }
    // ... 入队逻辑
}
```

### 5.3 pick_next_task_dl()

**文件**: `kernel/sched/deadline.c:2602-2627`

```c
static struct task_struct *__pick_task_dl(struct rq *rq, struct rq_flags *rf)
{
    struct sched_dl_entity *dl_se;
    struct dl_rq *dl_rq = &rq->dl;
    struct task_struct *p;

again:
    if (!sched_dl_runnable(rq))
        return NULL;

    dl_se = pick_next_dl_entity(dl_rq);  // 从红黑树取最左节点
    WARN_ON_ONCE(!dl_se);

    if (dl_server(dl_se)) {
        p = dl_se->server_pick_task(dl_se, rf);
        if (!p) {
            dl_server_stop(dl_se);
            goto again;
        }
        rq->dl_server = dl_se;
    } else {
        p = dl_task_of(dl_se);
    }

    return p;
}
```

## 6. RT与CFS的核心区别

### 6.1 设计理念对比

| 特性 | RT调度器 | CFS调度器 |
|------|----------|-----------|
| **调度目标** | 优先级保证 | 公平性 |
| **数据结构** | 优先级位图+链表 | 红黑树(基于vruntime) |
| **选择算法** | O(1) - `sched_find_first_bit()` | O(log n) - 红黑树最左节点 |
| **时间片** | 可选(SCHED_RR有) | 动态计算 |
| **饥饿问题** | 可能(低优先级) | 不可能(完全公平) |
| **延迟保证** | 硬实时 | 软实时 |

### 6.2 优先级位图O(1)选择原理

**文件**: `kernel/sched/rt.c:1678`

```c
idx = sched_find_first_bit(array->bitmap);
```

**工作原理**:
1. 每个优先级对应bitmap中的一位
2. `sched_find_first_bit()` 使用硬件指令或快速算法找到首个置位
3. 直接用idx访问对应的queue数组

### 6.3 dl_rq (Deadline运行队列)

**文件**: `kernel/sched/sched.h:866-882`

```c
struct dl_rq {
    struct rb_root_cached root;  /* 按deadline排序的红黑树 */
    unsigned int dl_nr_running;

    struct {
        u64 curr;  /* 当前运行任务的deadline */
        u64 next;  /* 最早ready任务的deadline */
    } earliest_dl;
};
```

## 7. 调度类注册

**RT调度类** (`kernel/sched/rt.c:2582-2617`):

```c
static const struct sched_class rt_sched_class = {
    .enqueue_task       = enqueue_task_rt,
    .dequeue_task       = dequeue_task_rt,
    .yield_task         = yield_task_rt,
    .wakeup_preempt     = wakeup_preempt_rt,
    .pick_task          = pick_task_rt,
    .put_prev_task      = put_prev_task_rt,
    .set_next_task      = set_next_task_rt,
    .balance            = balance_rt,
    .select_task_rq     = select_task_rq_rt,
    .get_rr_interval    = get_rr_interval_rt,
    .update_curr        = update_curr_rt,
};
```

**Deadline调度类** (`kernel/sched/deadline.c:3407-3438`):

```c
static const struct sched_class dl_sched_class = {
    .enqueue_task       = enqueue_task_dl,
    .dequeue_task       = dequeue_dl_entity,
    .yield_task         = yield_dl,
    .wakeup_preempt     = wakeup_preempt_dl,
    .pick_task          = pick_task_dl,
    .put_prev_task      = put_prev_task_dl,
    .set_next_task      = set_next_task_dl,
    .balance            = balance_dl,
    .select_task_rq     = select_task_rq_dl,
    .migrate_task_rq    = migrate_task_rq_dl,
    .task_tick          = task_tick_dl,
    .task_fork          = task_fork_dl,
    .get_prio           = get_prio_dl,
    .update_curr        = update_curr_dl,
};
```

---

## 8. 关键源码位置

| 组件 | 文件 | 行号 |
|------|------|------|
| struct rt_rq | kernel/sched/sched.h | 831-858 |
| struct rt_prio_array | kernel/sched/sched.h | 311-314 |
| struct sched_rt_entity | include/linux/sched.h | 623-639 |
| enqueue_task_rt | kernel/sched/rt.c | 1431-1448 |
| pick_next_task_rt | kernel/sched/rt.c | 1671-1701 |
| push_rt_task | kernel/sched/rt.c | 1939-1961 |
| pull_rt_task | kernel/sched/rt.c | 2240-2260 |
| sched_rt_runtime_exceeded | kernel/sched/rt.c | 863-889 |
| update_curr_rt | kernel/sched/rt.c | 974-1007 |
| struct sched_dl_entity | include/linux/sched.h | 644-749 |
| enqueue_task_dl | kernel/sched/deadline.c | 2292-2336 |
| pick_next_task_dl | kernel/sched/deadline.c | 2602-2627 |
| rt_sched_class | kernel/sched/rt.c | 2582-2617 |
| dl_sched_class | kernel/sched/deadline.c | 3407-3438 |
