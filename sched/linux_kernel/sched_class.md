# Linux 内核调度器类框架分析

## 1. struct sched_class 结构体定义

**文件**: `kernel/sched/sched.h`
**行号**: 2500-2661

```c
struct sched_class {

#ifdef CONFIG_UCLAMP_TASK
    int uclamp_enabled;
#endif

    /* 入队任务 */
    void (*enqueue_task) (struct rq *rq, struct task_struct *p, int flags);
    
    /* 出队任务 */
    bool (*dequeue_task) (struct rq *rq, struct task_struct *p, int flags);

    /* yield 相关 */
    void (*yield_task)   (struct rq *rq);
    bool (*yield_to_task)(struct rq *rq, struct task_struct *p);

    /* 抢占相关 */
    void (*wakeup_preempt)(struct rq *rq, struct task_struct *p, int flags);

    /* 负载均衡 */
    int (*balance)(struct rq *rq, struct task_struct *prev, struct rq_flags *rf);

    /* 选取任务 */
    struct task_struct *(*pick_task)(struct rq *rq, struct rq_flags *rf);
    struct task_struct *(*pick_next_task)(struct rq *rq, struct task_struct *prev,
                      struct rq_flags *rf);

    /* 任务切换 */
    void (*put_prev_task)(struct rq *rq, struct task_struct *p, struct task_struct *next);
    void (*set_next_task)(struct rq *rq, struct task_struct *p, bool first);

    /* 选择 CPU */
    int  (*select_task_rq)(struct task_struct *p, int task_cpu, int flags);

    /* 任务迁移 */
    void (*migrate_task_rq)(struct task_struct *p, int new_cpu);

    /* 任务唤醒后处理 */
    void (*task_woken)(struct rq *this_rq, struct task_struct *task);

    /* CPU 亲和性设置 */
    void (*set_cpus_allowed)(struct task_struct *p, struct affinity_context *ctx);

    /* CPU 状态变更 */
    void (*rq_online)(struct rq *rq);
    void (*rq_offline)(struct rq *rq);

    /* 查找可运行任务的 CPU */
    struct rq *(*find_lock_rq)(struct task_struct *p, struct rq *rq);

    /* 时钟tick处理 */
    void (*task_tick)(struct rq *rq, struct task_struct *p, int queued);
    void (*task_fork)(struct task_struct *p);
    void (*task_dead)(struct task_struct *p);

    /* 调度类切换钩子 */
    void (*switching_from)(struct rq *this_rq, struct task_struct *task);
    void (*switched_from) (struct rq *this_rq, struct task_struct *task);
    void (*switching_to)  (struct rq *this_rq, struct task_struct *task);
    void (*switched_to)   (struct rq *this_rq, struct task_struct *task);
    
    /* 优先级相关 */
    u64  (*get_prio)     (struct rq *this_rq, struct task_struct *task);
    void (*prio_changed) (struct rq *this_rq, struct task_struct *task, u64 oldprio);

    /* 负载权重调整 */
    void (*reweight_task)(struct rq *this_rq, struct task_struct *task,
                  const struct load_weight *lw);

    /* RR 间隔获取 */
    unsigned int (*get_rr_interval)(struct rq *rq, struct task_struct *task);

    /* 运行时统计更新 */
    void (*update_curr)(struct rq *rq);

#ifdef CONFIG_FAIR_GROUP_SCHED
    void (*task_change_group)(struct task_struct *p);
#endif

#ifdef CONFIG_SCHED_CORE
    int (*task_is_throttled)(struct task_struct *p, int cpu);
#endif
};
```

---

## 2. 调度类注册与优先级顺序

### 2.1 调度类定义宏

**文件**: `kernel/sched/sched.h`
**行号**: 2709-2712

```c
#define DEFINE_SCHED_CLASS(name) \
const struct sched_class name##_sched_class \
    __aligned(__alignof__(struct sched_class)) \
    __section("__" #name "_sched_class")
```

每个调度类被放置在独立的链接段中，通过 `__section__` 编译器属性实现。

### 2.2 调度类实例声明

**行号**: 2715-2722

```c
extern struct sched_class __sched_class_highest[];
extern struct sched_class __sched_class_lowest[];

extern const struct sched_class stop_sched_class;
extern const struct sched_class dl_sched_class;
extern const struct sched_class rt_sched_class;
extern const struct sched_class fair_sched_class;
extern const struct sched_class idle_sched_class;
```

### 2.3 链接脚本中的排序

**文件**: `include/asm-generic/vmlinux.lds.h`
**行号**: 153-162

```c
#define SCHED_DATA                \
    STRUCT_ALIGN();               \
    __sched_class_highest = .;    \
    *(__stop_sched_class)        \
    *(__dl_sched_class)           \
    *(__rt_sched_class)          \
    *(__fair_sched_class)        \
    *(__ext_sched_class)         \
    *(__idle_sched_class)        \
    __sched_class_lowest = .;
```

### 2.4 调度类优先级顺序

| 优先级 | 调度类 | 说明 |
|--------|--------|------|
| 最高 | stop_sched_class | 停止任务（用于 CPU 热插拔、负载均衡等） |
|  | dl_sched_class | 期限调度任务 |
|  | rt_sched_class | 实时任务（SCHED_FIFO/SCHED_RR） |
|  | fair_sched_class | 完全公平调度器（CFS）任务 |
|  | ext_sched_class | SCX BPF 调度器扩展（可选） |
| 最低 | idle_sched_class | 空闲任务（swapper） |

---

## 3. 各调度类实现

### 3.1 stop_sched_class

**文件**: `kernel/sched/stop_task.c:99-119`

```c
DEFINE_SCHED_CLASS(stop) = {
    .enqueue_task       = enqueue_task_stop,
    .dequeue_task       = dequeue_task_stop,
    .yield_task         = yield_task_stop,
    .wakeup_preempt     = wakeup_preempt_stop,
    .pick_task          = pick_task_stop,
    .put_prev_task      = put_prev_task_stop,
    .set_next_task      = set_next_task_stop,
    .balance            = balance_stop,
    .select_task_rq     = select_task_rq_stop,
    .set_cpus_allowed   = set_cpus_allowed_common,
    .task_tick          = task_tick_stop,
    .prio_changed       = prio_changed_stop,
    .switching_to       = switching_to_stop,
    .update_curr        = update_curr_stop,
};
```

### 3.2 dl_sched_class

**文件**: `kernel/sched/deadline.c:3406-3437`

```c
DEFINE_SCHED_CLASS(dl) = {
    .enqueue_task       = enqueue_task_dl,
    .dequeue_task       = dequeue_task_dl,
    .yield_task         = yield_task_dl,
    .wakeup_preempt     = wakeup_preempt_dl,
    .pick_task          = pick_task_dl,
    .put_prev_task      = put_prev_task_dl,
    .set_next_task      = set_next_task_dl,
    .balance            = balance_dl,
    .select_task_rq     = select_task_rq_dl,
    .migrate_task_rq    = migrate_task_rq_dl,
    .set_cpus_allowed   = set_cpus_allowed_dl,
    .rq_online          = rq_online_dl,
    .rq_offline         = rq_offline_dl,
    .task_woken         = task_woken_dl,
    .find_lock_rq       = find_lock_later_rq,
    .task_tick          = task_tick_dl,
    .task_fork          = task_fork_dl,
    .get_prio           = get_prio_dl,
    .prio_changed       = prio_changed_dl,
    .switched_from      = switched_from_dl,
    .switched_to        = switched_to_dl,
    .update_curr        = update_curr_dl,
};
```

### 3.3 rt_sched_class

**文件**: `kernel/sched/rt.c:2581-2611`

```c
DEFINE_SCHED_CLASS(rt) = {
    .enqueue_task       = enqueue_task_rt,
    .dequeue_task       = dequeue_task_rt,
    .yield_task         = yield_task_rt,
    .wakeup_preempt     = wakeup_preempt_rt,
    .pick_task          = pick_task_rt,
    .put_prev_task      = put_prev_task_rt,
    .set_next_task      = set_next_task_rt,
    .balance            = balance_rt,
    .select_task_rq     = select_task_rq_rt,
    .set_cpus_allowed   = set_cpus_allowed_common,
    .rq_online          = rq_online_rt,
    .rq_offline         = rq_offline_rt,
    .task_woken         = task_woken_rt,
    .switched_from      = switched_from_rt,
    .find_lock_rq       = find_lock_lowest_rq,
    .task_tick          = task_tick_rt,
    .get_rr_interval    = get_rr_interval_rt,
    .switched_to        = switched_to_rt,
    .prio_changed       = prio_changed_rt,
    .update_curr        = update_curr_rt,
};
```

### 3.4 fair_sched_class

**文件**: `kernel/sched/fair.c:13951-13980`

```c
DEFINE_SCHED_CLASS(fair) = {
    .enqueue_task       = enqueue_task_fair,
    .dequeue_task       = dequeue_task_fair,
    .yield_task         = yield_task_fair,
    .yield_to_task      = yield_to_task_fair,
    .wakeup_preempt     = wakeup_preempt_fair,
    .pick_task          = pick_task_fair,
    .pick_next_task     = pick_next_task_fair,
    .put_prev_task      = put_prev_task_fair,
    .set_next_task      = set_next_task_fair,
    .select_task_rq     = select_task_rq_fair,
    .migrate_task_rq    = migrate_task_rq_fair,
    .rq_online          = rq_online_fair,
    .rq_offline         = rq_offline_fair,
    .task_dead          = task_dead_fair,
    .set_cpus_allowed   = set_cpus_allowed_fair,
    .task_tick          = task_tick_fair,
    .task_fork          = task_task_fair,
    .reweight_task      = reweight_task_fair,
    .prio_changed       = prio_changed_fair,
    .switching_from     = switching_from_fair,
    .switched_from      = switched_from_fair,
    .switched_to        = switched_to_fair,
};
```

### 3.5 idle_sched_class

**文件**: `kernel/sched/idle.c:569-590`

```c
DEFINE_SCHED_CLASS(idle) = {
    .dequeue_task       = dequeue_task_idle,
    .wakeup_preempt     = wakeup_preempt_idle,
    .pick_task          = pick_task_idle,
    .put_prev_task      = put_prev_task_idle,
    .set_next_task      = set_next_task_idle,
    .balance            = balance_idle,
    .select_task_rq     = select_task_rq_idle,
    .set_cpus_allowed   = set_cpus_allowed_common,
    .task_tick          = task_tick_idle,
    .prio_changed       = prio_changed_idle,
    .switching_to       = switching_to_idle,
    .update_curr        = update_curr_idle,
};
```

---

## 4. pick_next_task 遍历逻辑

**文件**: `kernel/sched/core.c:5909-5964`

```c
static inline struct task_struct *
__pick_next_task(struct rq *rq, struct task_struct *prev, struct rq_flags *rf)
{
    const struct sched_class *class;
    struct task_struct *p;

    rq->dl_server = NULL;

    if (scx_enabled())
        goto restart;

    /* CFS 快速路径：只有公平任务时直接调用 */
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
    prev_balance(rq, prev, rf);

    /* 遍历所有活跃调度类，从高优先级到低优先级 */
    for_each_active_class(class) {
        if (class->pick_next_task) {
            p = class->pick_next_task(rq, prev, rf);
            if (unlikely(p == RETRY_TASK))
                goto restart;
            if (p)
                return p;
        } else {
            p = class->pick_task(rq, rf);
            if (unlikely(p == RETRY_TASK))
                goto restart;
            if (p) {
                put_prev_set_next_task(rq, prev, p);
                return p;
            }
        }
    }

    BUG();
}
```

### 迭代宏定义

**文件**: `kernel/sched/sched.h:2740-2752`

```c
#define for_class_range(class, _from, _to) \
    for (class = (_from); class < (_to); class++)

#define for_each_class(class) \
    for_class_range(class, __sched_class_highest, __sched_class_lowest)

#define for_active_class_range(class, _from, _to)               \
    for (class = (_from); class != (_to); class = next_active_class(class))

#define for_each_active_class(class)                    \
    for_active_class_range(class, __sched_class_highest, __sched_class_lowest)

#define sched_class_above(_a, _b)   ((_a) < (_b))
```

---

## 5. 调度类选择函数

**文件**: `kernel/sched/core.c:7254-7266`

```c
const struct sched_class *__setscheduler_class(int policy, int prio)
{
    if (dl_prio(prio))
        return &dl_sched_class;

    if (rt_prio(prio))
        return &rt_sched_class;

#ifdef CONFIG_SCHED_CLASS_EXT
    if (task_should_scx(policy))
        return &ext_sched_class;
#endif

    return &fair_sched_class;
}
```

---

## 6. 核心设计思想

### 6.1 可插拔调度器抽象

`sched_class` 结构体通过函数指针定义了调度器的完整行为接口：

| 类型 | 函数指针 | 用途 |
|------|----------|------|
| 任务队列 | `enqueue_task`, `dequeue_task` | 入队/出队管理 |
| 选取任务 | `pick_task`, `pick_next_task` | 核心调度决策 |
| 任务切换 | `put_prev_task`, `set_next_task` | 上下文切换支持 |
| 负载均衡 | `balance`, `find_lock_rq` | 多 CPU 负载均衡 |
| 事件处理 | `task_tick`, `task_woken`, `migrate_task_rq` | 各种调度事件 |

### 6.2 优先级比较

`sched_class_above(a, b)` 宏通过比较指针地址判断优先级。链接脚本保证高优先级调度类在低优先级之前，因此地址较小的类优先级更高。

---

## 7. 关键源码位置

| 组件 | 文件 | 行号 |
|------|------|------|
| struct sched_class | kernel/sched/sched.h | 2500-2661 |
| DEFINE_SCHED_CLASS | kernel/sched/sched.h | 2709-2712 |
| SCHED_DATA | include/asm-generic/vmlinux.lds.h | 153-162 |
| stop_sched_class | kernel/sched/stop_task.c | 99-119 |
| dl_sched_class | kernel/sched/deadline.c | 3406-3437 |
| rt_sched_class | kernel/sched/rt.c | 2581-2611 |
| fair_sched_class | kernel/sched/fair.c | 13951-13980 |
| idle_sched_class | kernel/sched/idle.c | 569-590 |
| __pick_next_task | kernel/sched/core.c | 5909-5964 |
| __setscheduler_class | kernel/sched/core.c | 7254-7266 |
