# Linux Sched 子系统深度分析 R1

> 内核版本: Linux 6.x (基于最新主线源码分析)
> 分析日期: 2026-04-26
> 源码路径: kernel/sched/{core.c, fair.c, rt.c, sched.h, topology.c}

---

## 目录

1. [调度器概述与架构](#1-调度器概述与架构)
2. [CFS 调度器深入分析](#2-cfs-调度器深入分析)
3. [RT 调度器深入分析](#3-rt-调度器深入分析)
4. [Load Balancing 机制](#4-load-balancing-机制)
5. [sched_domain 层级结构](#5-sched_domain-层级结构)
6. [pick_next_task 调度流程](#6-pick_next_task-调度流程)
7. [Per-CPU 机制](#7-per-cpu-机制)
8. [知识点关联表格](#8-知识点关联表格)

---

## 1. 调度器概述与架构

### 1.1 调度类优先级体系

Linux 内核调度器采用**调度类(Scheduling Class)**架构,不同调度类按优先级从高到低排列:

```c
// kernel/sched/sched.h:2718-2722
extern const struct sched_class stop_sched_class;      // 最高优先级 - stop machine
extern const struct sched_class dl_sched_class;       // Deadline 调度类
extern const struct sched_class rt_sched_class;        // Real-Time 调度类
extern const struct sched_class fair_sched_class;      // Completely Fair Scheduler (CFS)
extern const struct sched_class idle_sched_class;      // 最低优先级 - idle
```

**优先级顺序**: `stop_sched_class > dl_sched_class > rt_sched_class > fair_sched_class > idle_sched_class`

### 1.2 调度类结构定义

```c
// kernel/sched/sched.h:2500-2661
struct sched_class {
    const struct sched_class *next;  // 指向下一个调度类

    void (*enqueue_task)(struct rq *rq, struct task_struct *p, int flags);
    bool (*dequeue_task)(struct rq *rq, struct task_struct *p, int flags);
    
    // 核心调度函数
    int (*balance)(struct rq *rq, struct task_struct *prev, struct rq_flags *rf);
    struct task_struct *(*pick_task)(struct rq *rq, struct rq_flags *rf);
    struct task_struct *(*pick_next_task)(struct rq *rq, struct task_struct *prev,
                                          struct rq_flags *rf);
    
    void (*put_prev_task)(struct rq *rq, struct task_struct *p, struct task_struct *next);
    void (*set_next_task)(struct rq *rq, struct task_struct *p, bool first);
    
    int (*select_task_rq)(struct task_struct *p, int task_cpu, int flags);
    void (*task_tick)(struct rq *rq, struct task_struct *p, int queued);
    void (*update_curr)(struct rq *rq);  // 更新当前任务运行时间
    // ... 其他回调函数
};
```

### 1.3 调度类注册顺序(链接脚本决定)

调度类实例按**反向顺序**链接到内核,确保遍历时从高优先级到低优先级:

```c
// kernel/sched/core.c:5899-5902
for_active_class_range(class, start_class, &idle_sched_class) {
    if (class->balance && class->balance(rq, prev, rf))
        break;  // 找到高优先级可运行任务即停止
}
```

---

## 2. CFS 调度器深入分析

### 2.1 核心数据结构

#### 2.1.1 struct sched_entity (调度实体)

**定义位置**: `include/linux/sched.h:575-621`

```c
struct sched_entity {
    /* 负载权重 - 用于计算 vruntime */
    struct load_weight     load;
    struct rb_node         run_node;       // 红黑树节点
    
    /* EEVDF 调度相关 */
    u64             deadline;              // 截止时间(EEVDF)
    u64             min_vruntime;         // 子树最小虚拟运行时间
    u64             min_slice;            // 最小时间片
    u64             max_slice;            // 最大时间片

    struct list_head group_node;          // 任务组节点
    unsigned char   on_rq:1;              // 是否在运行队列上
    unsigned char   sched_delayed:1;      // 是否延迟调度
    unsigned char   rel_deadline:1;       // 相对截止时间标志
    unsigned char   custom_slice:1;       // 自定义时间片标志

    /* 运行时统计 */
    u64             exec_start;           // 本次运行开始时间
    u64             sum_exec_runtime;     // 累计运行时间
    u64             prev_sum_exec_runtime;// 上次累计运行时间(用于计算增量)
    
    /* 虚拟运行时间 - CFS 核心 */
    u64             vruntime;             // 虚拟运行时间
    s64             vlag;                 // 虚拟滞后(approximated virtual lag)
    u64             vprot;                // 保护性截止时间
    
    u64             slice;                // 分配的时间片
    
    u64             nr_migrations;        // 迁移次数

#ifdef CONFIG_FAIR_GROUP_SCHED
    int             depth;                // 在任务组层级中的深度
    struct sched_entity *parent;          // 父调度实体
    struct cfs_rq   *cfs_rq;             // 所属 CFS 运行队列
    struct cfs_rq   *my_q;               // 拥有的子运行队列
    unsigned long   runnable_weight;      // 可运行权重
#endif

    /* PELT (Per-Entity Load Tracking) */
    struct sched_avg avg;                 // 负载追踪平均值
};
```

#### 2.1.2 struct cfs_rq (CFS 运行队列)

**定义位置**: `kernel/sched/sched.h:678-760`

```c
struct cfs_rq {
    struct load_weight     load;              // 总负载权重
    unsigned int           nr_queued;         // 排队任务数
    unsigned int           h_nr_queued;        // SCHED_{NORMAL,BATCH,IDLE} 任务数
    unsigned int           h_nr_runnable;     // 可运行任务数
    unsigned int           h_nr_idle;         // IDLE 任务数

    /* 虚拟运行时间相关 */
    s64             sum_w_vruntime;          // 加权 vruntime 和
    u64             sum_weight;               // 权重和
    u64             zero_vruntime;           // 基准 vruntime

#ifdef CONFIG_SCHED_CORE
    unsigned int    forceidle_seq;            // 强制空闲序列号
    u64             zero_vruntime_fi;         // 强制空闲基准
#endif

    /* 红黑树 - 按 vruntime 排序 */
    struct rb_root_cached   tasks_timeline;   // 任务时间线

    /* 当前运行实体 */
    struct sched_entity     *curr;            // 当前正在运行的实体
    struct sched_entity     *next;            // 下一个将运行的实体(buddy)
    struct sched_entity     *last;            // 上次运行的实体
    struct sched_entity     *skip;            // 跳过的实体

    /* PELT 负载追踪 */
    struct sched_avg        avg;
    
    /* 已移除实体的统计 */
    struct {
        raw_spinlock_t  lock;
        int             nr;
        unsigned long   load_avg;
        unsigned long   util_avg;
        unsigned long   runnable_avg;
    } removed;

#ifdef CONFIG_FAIR_GROUP_SCHED
    u64             last_update_tg_load_avg;  // 上次更新任务组负载时间
    unsigned long   tg_load_avg_contrib;      // 任务组负载贡献
    long            propagate;                 // 传播标记
    long            prop_runnable_sum;        // 可运行时间和
    
    unsigned long   h_load;                  // 层级负载
    u64             last_h_load_update;       // 上次层级负载更新时间
    struct sched_entity *h_load_next;         // 下一层级负载实体

    struct rq       *rq;                     // 所属 CPU 运行队列
    int             on_list;                 // 是否在叶列表上
    struct list_head leaf_cfs_rq_list;        // 叶 CFS RQ 列表
    struct task_group *tg;                   // 拥有该运行队列的任务组
    int             idle;                    // 是否为 idle 组
#endif

#ifdef CONFIG_CFS_BANDWIDTH
    int             runtime_enabled;          // 带宽控制启用
    s64             runtime_remaining;        // 剩余带宽
    u64             throttled_pelt_idle;      // 节流 PELT idle 时间
#endif
};
```

#### 2.1.3 vruntime (虚拟运行时间) 算法

**vruntime** 是 CFS 调度的核心概念,用于实现"完全公平"调度。

**计算公式**:
```
vruntime += delta_exec * (NICE_0_LOAD / weight)
```

其中:
- `delta_exec`: 实际运行时间
- `weight`: 任务权重(nice 值决定)
- `NICE_0_LOAD`: 基准权重(1024)

**entity_key() 函数** - 计算实体键值:

```c
// kernel/sched/fair.c:607-610
static inline s64 entity_key(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    return vruntime_op(se->vruntime, "-", cfs_rq->zero_vruntime);
}
```

### 2.2 EEVDF 调度算法 (Earliest Eligible Virtual Deadline First)

Linux 6.x CFS 采用 **EEVDF** 调度算法,结合了 EDF(最早截止时间优先)和 CFS 的公平性。

#### 2.2.1 pick_eevdf() - EEVDF 选择算法

**位置**: `kernel/sched/fair.c:1081-1084` (外层) 和 `kernel/sched/fair.c:1010-1079` (内层)

```c
static struct sched_entity *__pick_eevdf(struct cfs_rq *cfs_rq, bool protect)
{
    struct rb_node *node = cfs_rq->tasks_timeline.rb_root.rb_node;
    struct sched_entity *se = __pick_first_entity(cfs_rq);  // 最左节点
    struct sched_entity *curr = cfs_rq->curr;
    struct sched_entity *best = NULL;

    /* 单任务优化 */
    if (cfs_rq->nr_queued == 1)
        return (curr && curr->on_rq) ? curr : se;

    /* PICK_BUDDY: 优先选择 next buddy */
    if (sched_feat(PICK_BUDDY) &&
        cfs_rq->next && entity_eligible(cfs_rq, cfs_rq->next)) {
        return cfs_rq->next;
    }

    /* 检查 current 是否符合条件 */
    if (curr && (!curr->on_rq || !entity_eligible(cfs_rq, curr)))
        curr = NULL;

    /* 保护当前任务的时间片 */
    if (curr && protect && protect_slice(curr))
        return curr;

    /* 选择最左节点(最小 vruntime)如果符合条件 */
    if (se && entity_eligible(cfs_rq, se)) {
        best = se;
        goto found;
    }

    /* 堆搜索寻找 EEVDF 实体 */
    while (node) {
        struct rb_node *left = node->rb_left;

        /* 左子树中符合 eligibility 的实体总是更好的选择 */
        if (left && vruntime_eligible(cfs_rq,
                __node_2_se(left)->min_vruntime)) {
            node = left;
            continue;
        }

        se = __node_2_se(node);

        if (entity_eligible(cfs_rq, se)) {
            best = se;
            break;
        }

        node = node->rb_right;
    }

found:
    /* 确保 current 不被选中如果它比 best 更早 */
    if (!best || (curr && entity_before(curr, best)))
        best = curr;

    return best;
}
```

#### 2.2.2 entity_eligible() - 实体 eligibility 检查

**位置**: `kernel/sched/fair.c:813-816`

```c
int entity_eligible(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    return vruntime_eligible(cfs_rq, se->vruntime);
}

// vruntime_eligible 检查 vruntime 是否满足条件
// kernel/sched/fair.c:797-811
static int vruntime_eligible(struct cfs_rq *cfs_rq, u64 vruntime)
{
    struct sched_entity *curr = cfs_rq->curr;
    s64 avg = 0, load = 0;

    if (!cfs_rq->sum_weight)
        return 1;

    // 计算平均 vruntime
    if (curr && curr->on_rq) {
        unsigned long w = scale_load_down(curr->load.weight);
        avg += entity_key(cfs_rq, curr) * w;
        load += w;
    }

    // avg_vruntime 返回 cfs_rq 的平均虚拟运行时间
    avg += avg_vruntime(cfs_rq) * cfs_rq->sum_weight;
    load += cfs_rq->sum_weight;

    // 比较: vruntime >= avg ? 
    return avg >= vruntime_op(vruntime, "-", cfs_rq->zero_vruntime) * load;
}
```

#### 2.2.3 pick_next_entity() - 选择下一个实体

**位置**: `kernel/sched/fair.c:5543-5556`

```c
static struct sched_entity *
pick_next_entity(struct rq *rq, struct cfs_rq *cfs_rq)
{
    struct sched_entity *se;

    se = pick_eevdf(cfs_rq);  // 调用 EEVDF 选择算法
    
    if (se->sched_delayed) {
        dequeue_entities(rq, se, DEQUEUE_SLEEP | DEQUEUE_DELAYED);
        return NULL;  // 延迟任务重新入队
    }
    
    return se;
}
```

### 2.3 pick_next_task_fair() - 公平调度器选择任务

**位置**: `kernel/sched/fair.c:8978-9057`

```c
struct task_struct *
pick_next_task_fair(struct rq *rq, struct task_struct *prev, struct rq_flags *rf)
{
    struct sched_entity *se;
    struct task_struct *p;
    int new_tasks;

again:
    p = pick_task_fair(rq, rf);  // 先快速选择
    if (!p)
        goto idle;
    se = &p->se;

#ifdef CONFIG_FAIR_GROUP_SCHED
    if (prev->sched_class != &fair_sched_class)
        goto simple;

    /* 组调度: 遍历任务组层级 */
    if (prev != p) {
        struct sched_entity *pse = &prev->se;
        struct cfs_rq *cfs_rq;

        while (!(cfs_rq = is_same_group(se, pse))) {
            int se_depth = se->depth;
            int pse_depth = pse->depth;

            if (se_depth <= pse_depth) {
                put_prev_entity(cfs_rq_of(pse), pse);
                pse = parent_entity(pse);
            }
            if (se_depth >= pse_depth) {
                set_next_entity(cfs_rq_of(se), se, true);
                se = parent_entity(se);
            }
        }

        put_prev_entity(cfs_rq, pse);
        set_next_entity(cfs_rq, se, true);
        __set_next_task_fair(rq, p, true);
    }

    return p;

simple:
#endif
    put_prev_set_next_task(rq, prev, p);
    return p;

idle:
    if (rf) {
        /* 如果没有公平任务,尝试空闲负载均衡 */
        new_tasks = sched_balance_newidle(rq, rf);

        if (new_tasks < 0)
            return RETRY_TASK;  // 重新调度

        if (new_tasks > 0)
            goto again;  // 有新任务,重新选择
    }

    return NULL;  // 确实没有任务
}
```

---

## 3. RT 调度器深入分析

### 3.1 RT 调度器核心数据结构

#### 3.1.1 struct rt_prio_array (优先级数组)

**位置**: `kernel/sched/sched.h:311-314`

```c
struct rt_prio_array {
    DECLARE_BITMAP(bitmap, MAX_RT_PRIO+1);  // 位图,快速查找非空优先级
    struct list_head queue[MAX_RT_PRIO];    // 每个优先级一个链表
};
```

#### 3.1.2 struct rt_rq (RT 运行队列)

**位置**: `kernel/sched/sched.h:831-858`

```c
struct rt_rq {
    struct rt_prio_array    active;          // 活动任务优先级数组
    unsigned int            rt_nr_running;    // RT 任务数量
    unsigned int            rr_nr_running;    // RR(轮转)任务数量
    
    struct {
        int     curr;   // 最高优先级 RT 任务
        int     next;   // 次高优先级
    } highest_prio;
    
    bool                    overloaded;       // 是否过载(有 >1 RT 任务)
    struct plist_head       pushable_tasks;  // 可推送的任务列表

    int                     rt_queued;        // RT 队列状态
    int                     rt_throttled;    // 是否被节流
    u64                     rt_time;         // 已消耗 RT 时间
    u64                     rt_runtime;       // 分配的 RT 时间片
    
    raw_spinlock_t          rt_runtime_lock; // 运行时锁

#ifdef CONFIG_RT_GROUP_SCHED
    unsigned int            rt_nr_boosted;   // 提升优先级任务数
    struct rq               *rq;             // 所属运行队列
#endif

#ifdef CONFIG_CGROUP_SCHED
    struct task_group       *tg;             // 任务组
#endif
};
```

#### 3.1.3 struct sched_rt_entity (RT 调度实体)

**位置**: `include/linux/sched.h:623-635`

```c
struct sched_rt_entity {
    struct list_head        run_list;        // 运行链表
    unsigned long           timeout;         // 超时时间
    unsigned long           watchdog_stamp;   // 看门狗时间戳
    unsigned int            time_slice;      // 时间片(SCHED_RR)
    unsigned short          on_rq:1;         // 是否在运行队列
    unsigned short          on_list:1;       // 是否在列表中

    struct sched_rt_entity  *back;           // 后向指针(用于链表)
#ifdef CONFIG_RT_GROUP_SCHED
    struct sched_rt_entity  *parent;        // 父实体
    struct rt_rq            *rt_rq;          // 所属 RT 运行队列
    struct rt_rq            *my_q;           // 拥有的子 RT 运行队列
#endif
};
```

### 3.2 RT 调度器核心函数

#### 3.2.1 pick_next_task_rt() - RT 任务选择

**位置**: `kernel/sched/rt.c:1689-1702`

```c
static struct task_struct *_pick_next_task_rt(struct rq *rq)
{
    struct sched_rt_entity *rt_se;
    struct rt_rq *rt_rq = &rq->rt;

    do {
        rt_se = pick_next_rt_entity(rt_rq);  // 选择下一个 RT 实体
        if (unlikely(!rt_se))
            return NULL;
        rt_rq = group_rt_rq(rt_se);         // 若是组调度,获取子组
    } while (rt_rq);

    return rt_task_of(rt_se);
}

static struct task_struct *pick_task_rt(struct rq *rq, struct rq_flags *rf)
{
    struct task_struct *p;

    if (!sched_rt_runnable(rq))  // 检查是否有 RT 任务可运行
        return NULL;

    p = _pick_next_task_rt(rq);
    return p;
}
```

#### 3.2.2 RT 调度类注册

**位置**: `kernel/sched/rt.c:2593-2602`

```c
const struct sched_class rt_sched_class = {
    .enqueue_task       = enqueue_task_rt,
    .dequeue_task       = dequeue_task_rt,
    .yield_task         = yield_task_rt,

    .pick_next_task     = pick_next_task_rt,
    .put_prev_task      = put_prev_task_rt,
    .set_next_task      = set_next_task_rt,

    .select_task_rq     = select_task_rq_rt,
    .balance            = balance_rt,
    .task_tick          = task_tick_rt,
    // ...
};
```

### 3.3 RT 任务抢占机制

#### 3.3.1 sched_rt_runtime - RT 运行时间限制

**位置**: `kernel/sched/rt.c:863-889`

```c
static int sched_rt_runtime_exceeded(struct rt_rq *rt_rq)
{
    u64 runtime = sched_rt_runtime(rt_rq);

    if (rt_rq->rt_throttled)
        return rt_rq_throttled(rt_rq);

    if (runtime >= sched_rt_period(rt_rq))
        return 0;  // 无限制

    balance_runtime(rt_rq);  // 尝试从其他组借取带宽
    
    runtime = sched_rt_runtime(rt_rq);
    if (runtime == RUNTIME_INF)
        return 0;

    if (rt_rq->rt_time > runtime) {  // 超出分配时间
        struct rt_bandwidth *rt_b = sched_rt_bandwidth(rt_rq);

        if (likely(rt_b->rt_runtime)) {
            rt_rq->rt_throttled = 1;  // 开始节流
            printk_deferred_once("sched: RT throttling activated\n");
        }
        return 1;
    }

    return 0;
}
```

#### 3.3.2 RT 带宽控制参数

**位置**: `kernel/sched/rt.c:24-25`

```c
int sysctl_sched_rt_period = 1000000;    // 1秒 = 1000000us
int sysctl_sched_rt_runtime = 950000;    // 0.95秒 = 950000us (95%)
```

**sysctl_sched_rt_runtime / sysctl_sched_rt_period** 控制 RT 任务可使用的 CPU 带宽比例,默认 95%。

#### 3.3.3 balance_rt - RT 负载均衡

**位置**: `kernel/sched/rt.c:1594-1611`

```c
static int balance_rt(struct rq *rq, struct task_struct *p, struct rq_flags *rf)
{
    if (!on_rt_rq(&p->rt) && need_pull_rt_task(rq, p)) {
        rq_unpin_lock(rq, rf);
        pull_rt_task(rq);  // 从其他 CPU 拉取 RT 任务
        rq_repin_lock(rq, rf);
    }

    return sched_rt_runnable(rq);  // 返回是否还有 RT 任务
}
```

---

## 4. Load Balancing 机制

### 4.1 负载均衡核心数据结构

#### 4.1.1 struct sg_lb_stats (调度组统计)

**位置**: `kernel/sched/fair.c:10032-10050`

```c
struct sg_lb_stats {
    unsigned long avg_load;           // 组内平均负载
    unsigned long group_load;         // 组总负载
    unsigned long group_capacity;    // 组总容量
    unsigned long group_util;        // 组总利用率
    unsigned long group_runnable;    // 组可运行时间和
    unsigned int  sum_nr_running;    // 组内运行任务总数
    unsigned int  sum_h_nr_running;  // 组内 CFS 任务数
    unsigned int  idle_cpus;         // 空闲 CPU 数量
    unsigned int  group_weight;      // 组内 CPU 数量
    enum group_type group_type;      // 组类型
    unsigned int  group_asym_packing; // 非对称包装标记
    unsigned int  group_smt_balance;  // SMT 平衡标记
    unsigned long group_misfit_task_load; // 错配任务负载
};
```

**group_type 枚举值**:
```c
enum group_type {
    group_has_spare = 0,   // 有空闲容量
    fully_busy,           // 完全忙碌
    group_misfit_task,     // 有任务与 CPU 容量不匹配
    group_asym_packing,    // 非对称容量-需优先处理
    group_imbalanced,      // 组内不平衡
    overloaded,           // 过载
};
```

#### 4.1.2 struct sd_lb_stats (调度域统计)

**位置**: `kernel/sched/fair.c:10055-10065`

```c
struct sd_lb_stats {
    struct sched_group *busiest;     // 最忙的调度组
    struct sched_group *local;       // 本地调度组
    unsigned long total_load;        // 域内总负载
    unsigned long total_capacity;    // 域内总容量
    unsigned long avg_load;          // 域内平均负载
    unsigned int prefer_sibling;    // 优先兄弟姐妹标记

    struct sg_lb_stats busiest_stat; // 最忙组统计
    struct sg_lb_stats local_stat;  // 本地组统计
};
```

### 4.2 update_sg_lb_stats() - 更新调度组统计

**位置**: `kernel/sched/fair.c:10463-10550`

```c
static inline void update_sg_lb_stats(struct lb_env *env,
                                      struct sd_lb_stats *sds,
                                      struct sched_group *group,
                                      struct sg_lb_stats *sgs,
                                      bool *sg_overloaded,
                                      bool *sg_overutilized)
{
    int i, nr_running, local_group, sd_flags = env->sd->flags;
    bool balancing_at_rd = !env->sd->parent;

    memset(sgs, 0, sizeof(*sgs));  // 清零统计

    local_group = group == sds->local;

    /* 遍历组内所有 CPU */
    for_each_cpu_and(i, sched_group_span(group), env->cpus) {
        struct rq *rq = cpu_rq(i);
        unsigned long load = cpu_load(rq);

        sgs->group_load += load;
        sgs->group_util += cpu_util_cfs(i);
        sgs->group_runnable += cpu_runnable(rq);
        sgs->sum_h_nr_running += rq->cfs.h_nr_runnable;

        nr_running = rq->nr_running;
        sgs->sum_nr_running += nr_running;

        /* 检查是否过载 */
        if (cpu_overutilized(i))
            *sg_overutilized = 1;

        /* 更新空闲 CPU 计数 */
        if (!nr_running && idle_cpu(i))
            sgs->idle_cpus++;
        
        // ... 更多统计更新
    }
}
```

### 4.3 sched_balance_find_src_group() - 找到最忙组

**位置**: `kernel/sched/fair.c:11409-11480`

```c
static struct sched_group *sched_balance_find_src_group(struct lb_env *env)
{
    struct sg_lb_stats *local, *busiest;
    struct sd_lb_stats sds;

    init_sd_lb_stats(&sds);

    /* 计算该层级的各种统计 */
    update_sd_lb_stats(env, &sds);

    /* 没有繁忙组 */
    if (!sds.busiest)
        goto out_balanced;

    busiest = &sds.busiest_stat;

    /* 错配任务优先处理 */
    if (busiest->group_type == group_misfit_task)
        goto force_balance;

    /* 检查根域是否过载 */
    if (!is_rd_overutilized(env->dst_rq->rd) &&
        rcu_dereference_all(env->dst_rq->rd->pd))
        goto out_balanced;

    /* 非对称容量处理 */
    if (busiest->group_type == group_asym_packing)
        goto force_balance;

    /* 组不平衡处理 */
    if (busiest->group_type == group_imbalanced)
        goto force_balance;

    local = &sds.local_stat;
    // ... 根据组类型决定是否需要迁移
}
```

### 4.4 sched_balance_rq() - 运行队列级负载均衡

**位置**: `kernel/sched/fair.c:11865-11925`

```c
static int sched_balance_rq(int this_cpu, struct rq *this_rq,
            struct sched_domain *sd, enum cpu_idle_type idle,
            int *continue_balancing)
{
    struct sched_group *group;
    struct rq *busiest;
    struct rq_flags rf;
    struct cpumask *cpus = this_cpu_cpumask_var_ptr(load_balance_mask);
    struct lb_env env = {
        .sd             = sd,
        .dst_cpu        = this_cpu,
        .dst_rq         = this_rq,
        .dst_grpmask    = group_balance_mask(sd->groups),
        .idle           = idle,
        .loop_break     = SCHED_NR_MIGRATE_BREAK,
        .cpus           = cpus,
    };

    // ...
    
    /* 找到源调度组 */
    group = sched_balance_find_src_group(&env);
    if (!group)
        goto out_balanced;

    /* 找到最忙 CPU */
    busiest = sched_balance_find_src_rq(&env, group);
    if (!busiest)
        goto out_balanced;

    env.src_cpu = busiest->cpu;
    env.src_rq = busiest;

    if (busiest->nr_running > 1) {
        /* 分离任务 */
        cur_ld_moved = detach_tasks(&env);
        
        if (cur_ld_moved) {
            attach_tasks(&env);  // 附加任务到目标
            ld_moved += cur_ld_moved;
        }
    }
    // ...
}
```

### 4.5 detach_tasks() - 分离任务

**位置**: `kernel/sched/fair.c` (在 load_balance 相关部分)

核心逻辑:
1. 遍历 busiest rq 上的任务
2. 检查任务是否可迁移
3. 计算迁移负载
4. 调用 move_task() 移动任务

---

## 5. sched_domain 层级结构

### 5.1 struct sched_domain (调度域)

**定义位置**: `include/linux/sched/topology.h:73-145`

```c
struct sched_domain {
    /* 层级结构 */
    struct sched_domain __rcu *parent;   // 父域(顶层为 NULL)
    struct sched_domain __rcu *child;   // 子域(底层为 NULL)
    struct sched_group *groups;         // 域内的调度组

    /* 平衡间隔参数 */
    unsigned long min_interval;          // 最小平衡间隔(ms)
    unsigned long max_interval;          // 最大平衡间隔(ms)
    unsigned int busy_factor;            // 忙碌时减少平衡的因子
    unsigned int imbalance_pct;          // 超过水位才开始平衡
    unsigned int cache_nice_tries;       // 保留热缓存任务的尝试次数
    unsigned int imb_numa_nr;            // 允许 NUMA 不平衡的任务数

    int nohz_idle;                      // NOHZ IDLE 状态
    int flags;                           // SD_* 标志
    int level;                           // 域层级(SD_LV_*)

    /* 运行时字段 */
    unsigned long last_balance;         // 上次平衡时间(jiffies)
    unsigned int balance_interval;        // 平衡间隔(ms)
    unsigned int nr_balance_failed;      // 平衡失败次数

    /* 统计信息 */
    unsigned int lb_count[CPU_MAX_IDLE_TYPES];
    unsigned int lb_failed[CPU_MAX_IDLE_TYPES];
    // ...
    
    /* 特定域共享数据 */
    struct sched_domain_shared *shared;

    /* 跨域信息 */
    unsigned int span_weight;            // 域覆盖的 CPU 数量
    unsigned long span[];                // 域覆盖的 CPU 掩码(变长)
};
```

### 5.2 struct sched_group (调度组)

**定义位置**: `kernel/sched/sched.h:2184-2202`

```c
struct sched_group {
    struct sched_group   *next;          // 循环链表下一个组
    atomic_t             ref;           // 引用计数

    unsigned int         group_weight;   // 组内 CPU 数量
    unsigned int         cores;          // 核心数
    struct sched_group_capacity *sgc;    // 组容量信息
    int                  asym_prefer_cpu; // 组内最高优先级 CPU
    int                  flags;         // 组标志

    unsigned long        cpumask[];     // 组覆盖的 CPU 掩码(变长)
};
```

### 5.3 sched_domain 标志 (SD_* Flags)

**定义位置**: `include/linux/sched/sd_flags.h`

```c
// 核心负载均衡标志
SD_FLAG(SD_BALANCE_NEWIDLE, SDF_SHARED_CHILD | SDF_NEEDS_GROUPS)  // 空闲时平衡
SD_FLAG(SD_BALANCE_EXEC, SDF_SHARED_CHILD | SDF_NEEDS_GROUPS)     // exec 时平衡
SD_FLAG(SD_BALANCE_FORK, SDF_SHARED_CHILD | SDF_NEEDS_GROUPS)     // fork 时平衡
SD_FLAG(SD_BALANCE_WAKE, SDF_SHARED_CHILD | SDF_NEEDS_GROUPS)     // wake 时平衡

// CPU 容量相关
SD_FLAG(SD_ASYM_CPUCAPACITY, SDF_SHARED_PARENT | SDF_NEEDS_GROUPS)  // 不对称容量
SD_FLAG(SD_ASYM_CPUCAPACITY_FULL, SDF_SHARED_PARENT | SDF_NEEDS_GROUPS) // 完全不对称

// 资源共享标志
SD_FLAG(SD_SHARE_CPUCAPACITY, SDF_SHARED_CHILD | SDF_NEEDS_GROUPS) // SMT 共享容量
SD_FLAG(SD_CLUSTER, SDF_NEEDS_GROUPS)     // 共享集群(L2/LLC)
SD_FLAG(SD_SHARE_LLC, SDF_SHARED_CHILD | SDF_NEEDS_GROUPS)        // 共享 LLC

// 其他标志
SD_FLAG(SD_SERIALIZE, SDF_SHARED_PARENT | SDF_NEEDS_GROUPS)  // 单实例平衡
SD_FLAG(SD_ASYM_PACKING, SDF_NEEDS_GROUPS)                   // 非对称包装
SD_FLAG(SD_PREFER_SIBLING, SDF_NEEDS_GROUPS)                 // 优先兄弟域
SD_FLAG(SD_NUMA, SDF_SHARED_PARENT | SDF_NEEDS_GROUPS)       // NUMA 平衡
```

### 5.4 典型 sched_domain 层级结构

```
                    +------------------+
                    |   SD_NUMA        |  NUMA 域 (跨节点)
                    |   span: 所有节点  |
                    +--------+---------+
                             |
                    +--------+---------+
                    |   SD_ASYM         |  非对称容量域
                    |   span: 所有核    |
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                                         |
+-------+---------+                     +---------+--------+
| SD_SHARE_LLC     |                     | SD_SHARE_LLC    |
| (LLC Domain)     |                     | (LLC Domain)    |
| span: 一个物理CPU |                     | span: 另一个CPU |
+-------+---------+                     +---------+--------+
        |                                         |
+ ------+------+                          +-------+------+
|    SMT     |                          |    SMT        |
| span: 4核  |                          | span: 4核     |
+------------+                          +---------------+
```

---

## 6. pick_next_task 调度流程

### 6.1 核心 pick_next_task

**位置**: `kernel/sched/core.c:6010-6070`

```c
static struct task_struct *
pick_next_task(struct rq *rq, struct task_struct *prev, struct rq_flags *rf)
{
    struct task_struct *next, *max;
    const struct cpumask *smt_mask;
    unsigned long cookie;
    // ...

    if (!sched_core_enabled(rq))
        return __pick_next_task(rq, prev, rf);  // 无 CORE SCHED,快速路径

    // CORE SCHED: 需要跨 CPU 选择
    // ... 核心调度逻辑(省略)...
}
```

### 6.2 __pick_next_task() - 快速路径

**位置**: `kernel/sched/core.c:5909-5963`

```c
static inline struct task_struct *
__pick_next_task(struct rq *rq, struct task_struct *prev, struct rq_flags *rf)
{
    const struct sched_class *class;
    struct task_struct *p;

    rq->dl_server = NULL;

    if (scx_enabled())  // SCX 调度器
        goto restart;

    /* CFS 优化: 如果所有任务都在公平类且无更高优先级任务 */
    if (likely(!sched_class_above(prev->sched_class, &fair_sched_class) &&
           rq->nr_running == rq->cfs.h_nr_queued)) {

        p = pick_next_task_fair(rq, prev, rf);
        if (unlikely(p == RETRY_TASK))
            goto restart;

        if (!p) {
            p = pick_task_idle(rq, rf);
            put_prev_set_next_task(rq, prev, p);
        }

        return p;
    }

restart:
    /* 遍历所有调度类,从高优先级到低优先级 */
    for_active_class_range(class, start_class, &idle_sched_class) {
        if (class->pick_task) {
            p = class->pick_task(rq, rf);
            if (p)
                return p;
        }
    }

    BUG();  // Idle 类应该总是有任务
}
```

### 6.3 pick_next_task 完整流程图

```
__schedule() 被调用
       |
       v
pick_next_task(rq, prev)
       |
       +---> sched_core_enabled? --No--> __pick_next_task()
       |                                     |
       | Yes                                v
       |                           CFS 优化检查:
       |                           prev->class <= fair_sched_class
       |                           && nr_running == cfs.h_nr_queued
       |                                     |
       |                            Yes      v
       |                    pick_next_task_fair() --> 返回任务
       |                            |
       |                            No
       |                            v
       +---> CORE SCHED 逻辑        for_active_class_range():
       | (复杂,省略)                  - dl_sched_class:pick_task_dl()
       |                              - rt_sched_class:pick_task_rt()
       |                              - fair_sched_class:pick_task_fair()
       |                              - idle_sched_class:pick_task_idle()
       |                                    |
       v                                    v
    返回选中的任务                    返回选中的任务
```

### 6.4 调度类优先级与 pick_next_task 关系

```c
// pick_task 回调函数指针 - 各类调度器实现
// kernel/sched/rt.c:1704-1714
pick_task_rt()       // RT 调度类

// kernel/sched/deadline.c:2602-2627  
pick_task_dl()       // Deadline 调度类

// kernel/sched/fair.c:8941-8971
pick_task_fair()     // Fair 调度类

// kernel/sched/idle.c (idle_sched_class)
pick_task_idle()     // Idle 调度类
```

---

## 7. Per-CPU 机制

### 7.1 struct rq (运行队列)

**定义位置**: `kernel/sched/sched.h:1124-1280`

```c
struct rq {
    /* 热路径字段 - 在 update_sg_lb_stats 中一起加载 */
    unsigned int        nr_running;      // 运行任务数
#ifdef CONFIG_NUMA_BALANCING
    unsigned int        nr_numa_running;
    unsigned int        nr_preferred_running;
#endif
    unsigned int        ttwu_pending;
    unsigned long       cpu_capacity;     // CPU 容量

    union {
        struct task_struct __rcu *donor;  // 调度上下文(Sched-Core)
        struct task_struct __rcu *curr;    // 当前执行上下文
    };
    struct task_struct  *idle;            // Idle 任务

    /* 锁 */
    raw_spinlock_t     __lock;

    /* 各调度类运行队列 */
    struct cfs_rq       cfs;              // CFS 运行队列
    struct rt_rq        rt;               // RT 运行队列
    struct dl_rq        dl;               // Deadline 运行队列

#ifdef CONFIG_SCHED_CLASS_EXT
    struct scx_rq       scx;              // SCX 运行队列
    struct sched_dl_entity ext_server;     // 外部服务器
#endif
    struct sched_dl_entity fair_server;    // 公平服务器

    /* 负载追踪 */
    struct sched_avg    avg_rt;           // RT 类平均负载
    struct sched_avg    avg_dl;           // DL 类平均负载
#ifdef CONFIG_HAVE_SCHED_AVG_IRQ
    struct sched_avg    avg_irq;          // IRQ 平均负载
#endif
#ifdef CONFIG_SCHED_HW_PRESSURE
    struct sched_avg    avg_hw;           // 硬件压力平均负载
#endif

    u64                 idle_stamp;       // 空闲开始时间戳
    u64                 avg_idle;        // 平均空闲时间
    
    /* CPU 容量相关 */
    int                 cpu;               // CPU 编号
    int                 online;           // 是否在线

    struct list_head    cfs_tasks;        // CFS 任务列表
};
```

### 7.2 cpu_load[] - CPU 负载追踪

**位置**: `kernel/sched/sched.h` (rq 结构中的负载统计)

CPU 负载通过 `cpu_load[]` 数组追踪,包含不同时间窗口的负载:

```c
// 实际定义在 rq 结构中,类似:
unsigned long cpu_load[5];  // 1min, 5min, 15min 等不同窗口
```

**负载计算函数** (kernel/sched/fair.c 等):

```c
static inline unsigned long cpu_load(struct rq *rq)
{
    return rq->cfs.load.weight;  // 基于 CFS 负载权重
}
```

### 7.3 cpu_capacity - CPU 容量

**位置**: `kernel/sched/sched.h:1139`

```c
unsigned long cpu_capacity;  // rq 结构中
```

**相关函数**:

```c
// kernel/sched/sched.h:3082-3098
#ifndef arch_scale_freq_capacity
/**
 * arch_scale_freq_capacity - get the frequency scale factor of a given CPU.
 * @cpu: the CPU in question.
 *
 * Return: the frequency scale factor normalized against SCHED_CAPACITY_SCALE
 */
unsigned long arch_scale_freq_capacity(int cpu)
{
    return SCHED_CAPACITY_SCALE;  // 默认返回最大容量
}
#endif

// 获取实际 CPU 容量
static inline unsigned long capacity_of(int cpu)
{
    return cpu_rq(cpu)->cpu_capacity * arch_scale_freq_capacity(cpu) 
           >> SCHED_CAPACITY_SHIFT;
}
```

### 7.4 arch_scale_cpu_capacity() - CPU 容量缩放

**位置**: `kernel/sched/sched.h`

```c
#ifndef arch_scale_cpu_capacity
static __always_inline unsigned long arch_scale_cpu_capacity(int cpu)
{
    return SCHED_CAPACITY_SCALE;  // 默认最大容量
}
#endif
```

**容量计算考虑因素**:
1. **基础容量**: 由 CPU 类型(SMT核、核心、NUMA节点)决定
2. **频率缩放**: `arch_scale_freq_capacity()` 返回当前频率相对于最大频率的比例
3. **实际容量**: `capacity = base_capacity * freq_scale`

---

## 8. 知识点关联表格

### 8.1 核心数据结构关联

| 数据结构 | 定义位置 | 用途 | 关键字段 |
|---------|---------|------|---------|
| `struct sched_entity` | `include/linux/sched.h:575` | CFS 调度实体 | `vruntime`, `deadline`, `load`, `run_node` |
| `struct cfs_rq` | `kernel/sched/sched.h:678` | CFS 运行队列 | `tasks_timeline`, `curr`, `nr_queued`, `avg` |
| `struct rt_rq` | `kernel/sched/sched.h:831` | RT 运行队列 | `active`, `rt_nr_running`, `highest_prio` |
| `struct sched_rt_entity` | `include/linux/sched.h:623` | RT 调度实体 | `run_list`, `time_slice`, `timeout` |
| `struct rq` | `kernel/sched/sched.h:1124` | CPU 运行队列 | `cfs`, `rt`, `dl`, `nr_running`, `cpu_capacity` |
| `struct sched_domain` | `include/linux/sched/topology.h:73` | 调度域 | `parent`, `child`, `groups`, `flags`, `span` |
| `struct sched_group` | `kernel/sched/sched.h:2184` | 调度组 | `next`, `sgc`, `group_weight`, `cpumask` |
| `struct sg_lb_stats` | `kernel/sched/fair.c:10032` | 组负载统计 | `group_load`, `group_util`, `idle_cpus` |
| `struct sd_lb_stats` | `kernel/sched/fair.c:10055` | 域负载统计 | `busiest`, `local`, `avg_load` |

### 8.2 核心函数调用链

| 功能 | 入口函数 | 调用路径 | 源码位置 |
|-----|---------|---------|---------|
| CFS 选择任务 | `pick_next_task_fair()` | `__pick_eevdf()` -> `entity_eligible()` | `kernel/sched/fair.c:8978` |
| RT 选择任务 | `pick_next_task_rt()` | `_pick_next_task_rt()` -> `pick_next_rt_entity()` | `kernel/sched/rt.c:1689` |
| DL 选择任务 | `pick_next_task_dl()` | `pick_next_dl_entity()` | `kernel/sched/deadline.c` |
| 主调度选择 | `pick_next_task()` | `__pick_next_task()` -> 遍历调度类 | `kernel/sched/core.c:6010` |
| 负载均衡 | `sched_balance_rq()` | `find_busiest_group()` -> `detach_tasks()` | `kernel/sched/fair.c:11865` |
| 组统计更新 | `update_sg_lb_stats()` | 被 `update_sd_lb_stats()` 调用 | `kernel/sched/fair.c:10463` |
| RT 带宽检查 | `sched_rt_runtime_exceeded()` | `update_curr_rt()` -> `sched_rt_runtime()` | `kernel/sched/rt.c:863` |

### 8.3 调度类优先级

| 优先级 | 调度类 | 调度策略 | pick_next_task | 主要应用 |
|-------|--------|---------|----------------|---------|
| 1 (最高) | `stop_sched_class` | SCHED_STOP | `pick_next_task_stop()` | 紧急任务,CPU 停止 |
| 2 | `dl_sched_class` | SCHED_DEADLINE | `pick_next_task_dl()` | 实时多媒体,硬实时 |
| 3 | `rt_sched_class` | SCHED_FIFO/SCHED_RR | `pick_next_task_rt()` | 实时控制,中断处理 |
| 4 | `fair_sched_class` | SCHED_NORMAL/SCHED_BATCH | `pick_next_task_fair()` | 普通任务,后台服务 |
| 5 (最低) | `idle_sched_class` | SCHED_IDLE | `pick_task_idle()` | 空闲时执行,省电 |

### 8.4 sched_domain 标志含义

| 标志 | 值 | 含义 | 典型应用场景 |
|-----|---|-----|-------------|
| `SD_BALANCE_NEWIDLE` | 0x0001 | 空闲时进行负载均衡 | CPU 即将进入 idle |
| `SD_BALANCE_EXEC` | 0x0002 | exec 时平衡 | 新程序启动 |
| `SD_BALANCE_FORK` | 0x0004 | fork 时平衡 | 新建进程 |
| `SD_BALANCE_WAKE` | 0x0008 | wake 时平衡 | 任务唤醒 |
| `SD_SHARE_CPUCAPACITY` | 0x0010 | SMT 核共享容量 | Intel Hyper-Threading |
| `SD_SHARE_LLC` | 0x0040 | 共享最后级缓存 | 多核处理器 |
| `SD_CLUSTER` | 0x0080 | 共享集群资源 | AMD CCX/NUMA |
| `SD_ASYM_CPUCAPACITY` | 0x0200 | 非对称容量 | big.LITTLE 处理器 |
| `SD_NUMA` | 0x2000 | NUMA 平衡 | 多节点服务器 |

### 8.5 关键算法与公式

| 概念 | 公式/算法 | 说明 |
|-----|----------|------|
| **vruntime 计算** | `vruntime += delta_exec * (NICE_0_LOAD / weight)` | CFS 公平性基础 |
| **entity_key** | `se->vruntime - cfs_rq->zero_vruntime` | 红黑树排序键 |
| **EEVDF 选择** | 最早 eligible 虚拟截止时间优先 | 当前 CFS 调度算法 |
| **CPU 容量** | `capacity = base_capacity * freq_scale` | 考虑频率的 CPU 处理能力 |
| **负载均衡条件** | `imbalance > imbalance_pct * capacity / 100` | 触发负载均衡的阈值 |
| **RT 带宽** | `runtime / period <= 95%` | RT 任务 CPU 时间上限 |

### 8.6 源码位置速查表

| 模块 | 文件 | 行号 | 主要内容 |
|-----|------|-----|---------|
| CFS 调度实体 | `include/linux/sched.h` | 575-621 | `struct sched_entity` |
| CFS 运行队列 | `kernel/sched/sched.h` | 678+ | `struct cfs_rq` |
| EEVDF 选择 | `kernel/sched/fair.c` | 1010-1079 | `__pick_eevdf()` |
| pick_next_entity | `kernel/sched/fair.c` | 5543-5556 | CFS 实体选择 |
| RT 运行队列 | `kernel/sched/sched.h` | 831-858 | `struct rt_rq` |
| RT 带宽检查 | `kernel/sched/rt.c` | 863-889 | `sched_rt_runtime_exceeded()` |
| 负载均衡主函数 | `kernel/sched/fair.c` | 11865-11925 | `sched_balance_rq()` |
| 组统计更新 | `kernel/sched/fair.c` | 10463-10550 | `update_sg_lb_stats()` |
| 调度域定义 | `include/linux/sched/topology.h` | 73-145 | `struct sched_domain` |
| 调度组定义 | `kernel/sched/sched.h` | 2184-2202 | `struct sched_group` |
| 标志定义 | `include/linux/sched/sd_flags.h` | 全文 | SD_* 枚举 |
| 运行队列 | `kernel/sched/sched.h` | 1124-1280 | `struct rq` |
| 主 pick_next_task | `kernel/sched/core.c` | 6010+ | `pick_next_task()` |
| __pick_next_task | `kernel/sched/core.c` | 5909-5963 | 快速路径选择 |

---

## 参考

1. **内核源码**: `/Users/sphinx/github/linux/kernel/sched/`
   - `core.c`: 核心调度,`pick_next_task`
   - `fair.c`: CFS 调度器实现
   - `rt.c`: RT 调度器实现
   - `sched.h`: 核心数据结构定义
   - `topology.c`: sched_domain 构建

2. **头文件**:
   - `include/linux/sched.h`: 任务和调度实体定义
   - `include/linux/sched/topology.h`: 调度域定义
   - `include/linux/sched/sd_flags.h`: 调度域标志

3. **文档**:
   - 内核文档: `Documentation/scheduler/`
   - 调度器设计: `sched-design.txt`(内核文档)

---

*本文档由 Claude Code 分析生成*
*版本: R1*
*日期: 2026-04-26*
