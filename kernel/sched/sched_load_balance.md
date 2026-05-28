# Linux 内核调度器负载均衡分析

## 1. 核心数据结构

### 1.1 struct sched_domain - 调度域结构

**文件**: `include/linux/sched/topology.h:73-151`

```c
struct sched_domain {
    struct sched_domain __rcu *parent;    /* 顶级域必须为空终止 */
    struct sched_domain __rcu *child;     /* 底部域必须为空终止 */
    struct sched_group *groups;           /* 域的平衡组 */
    unsigned long min_interval;           /* 最小平衡间隔ms */
    unsigned long max_interval;           /* 最大平衡间隔ms */
    unsigned int busy_factor;             /* 忙时减少平衡因子 */
    unsigned int imbalance_pct;          /* 水印之前不平衡 */

    int nohz_idle;                       /* NOHZ IDLE状态 */
    int flags;                            /* SD_*标志 */
    int level;                            /* 域级别 */

    unsigned long last_balance;           /* 初始化为jiffies */
    unsigned int balance_interval;        /* 初始化为1，单位ms */
    unsigned int nr_balance_failed;      /* 初始化为0 */

    unsigned int span_weight;
    unsigned long span[];
};
```

### 1.2 struct sched_group - 调度组结构

**文件**: `kernel/sched/sched.h:2184-2202`

```c
struct sched_group {
    struct sched_group *next;            /* 必须是循环链表 */
    atomic_t ref;

    unsigned int group_weight;
    unsigned int cores;
    struct sched_group_capacity *sgc;
    int asym_prefer_cpu;                 /* 组中最高优先级的CPU */
    int flags;

    unsigned long cpumask[];
};

struct sched_group_capacity {
    atomic_t ref;
    unsigned long capacity;              /* 组的CPU容量 */
    unsigned long min_capacity;          /* 组中最小每CPU容量 */
    unsigned long max_capacity;          /* 组中最大每CPU容量 */
    unsigned long cpumask[];             /* 平衡掩码 */
};
```

---

## 2. 调度域层次结构

### 2.1 default_topology

**文件**: `kernel/sched/topology.c:1789-1803`

```c
static struct sched_domain_topology_level default_topology[] = {
#ifdef CONFIG_SCHED_SMT
    SDTL_INIT(tl_smt_mask, cpu_smt_flags, SMT),
#endif
#ifdef CONFIG_SCHED_CLUSTER
    SDTL_INIT(tl_cls_mask, cpu_cluster_flags, CLS),
#endif
#ifdef CONFIG_SCHED_MC
    SDTL_INIT(tl_mc_mask, cpu_core_flags, MC),
#endif
    SDTL_INIT(tl_pkg_mask, NULL, PKG),
    { NULL, },
};
```

**调度域层次 (从底向上)**:
1. **SMT** - 同一物理CPU上的逻辑核心，共享CPU容量
2. **CLS** - 共享LLC缓存的CPU组
3. **MC** - 同一物理包中的核心
4. **PKG** - 整个物理CPU包
5. **NUMA** - 跨节点平衡

---

## 3. 负载均衡核心函数

### 3.1 detach_tasks() - 任务分离

**文件**: `kernel/sched/fair.c:9648-9781`

```c
static int detach_tasks(struct lb_env *env)
{
    struct list_head *tasks = &env->src_rq->cfs_tasks;
    unsigned long util, load;
    struct task_struct *p;
    int detached = 0;

    if (env->src_rq->nr_running <= 1) {
        env->flags &= ~LBF_ALL_PINNED;
        return 0;
    }

    if (env->imbalance <= 0)
        return 0;

    while (!list_empty(tasks)) {
        p = list_last_entry(tasks, struct task_struct, se.group_node);
        if (!can_migrate_task(p, env))
            goto next;

        switch (env->migration_type) {
        case migrate_load:
            load = max_t(unsigned long, task_h_load(p), 1);
            if (shr_bound(load, env->sd->nr_balance_failed) > env->imbalance)
                goto next;
            env->imbalance -= load;
            break;
        }

        detach_task(p, env);
        list_add(&p->se.group_node, &env->tasks);
        detached++;

        if (env->idle == CPU_NEWLY_IDLE)
            break;
        if (env->imbalance <= 0)
            break;
next:
        list_move(&p->se.group_node, tasks);
    }
    return detached;
}
```

### 3.2 attach_tasks() - 任务附加

**文件**: `kernel/sched/fair.c:9813-9830`

```c
static void attach_tasks(struct lb_env *env)
{
    struct list_head *tasks = &env->tasks;
    struct task_struct *p;
    struct rq_flags rf;

    rq_lock(env->dst_rq, &rf);
    update_rq_clock(env->dst_rq);

    while (!list_empty(tasks)) {
        p = list_first_entry(tasks, struct task_struct, se.group_node);
        list_del_init(&p->se.group_node);
        attach_task(env->dst_rq, p);
    }

    rq_unlock(env->dst_rq, &rf);
}
```

### 3.3 sched_balance_rq() - 核心负载均衡函数

**文件**: `kernel/sched/fair.c:11865-12149`

```c
static int sched_balance_rq(int this_cpu, struct rq *this_rq,
            struct sched_domain *sd, enum cpu_idle_type idle,
            int *continue_balancing)
{
    int ld_moved, cur_ld_moved;
    struct sched_domain *sd_parent = sd->parent;
    struct sched_group *group;
    struct rq *busiest;

    for_each_domain(this_cpu, sd) {
        if (!should_we_balance(&env))
            goto out_balanced;

        group = sched_balance_find_src_group(&env);
        busiest = sched_balance_find_src_rq(&env, group);

        env.loop_max = min(sysctl_sched_nr_migrate, busiest->nr_running);

more_balance:
        rq_lock_irqsave(busiest, &rf);
        update_rq_clock(busiest);
        cur_ld_moved = detach_tasks(&env);
        rq_unlock(busiest, &rf);

        if (cur_ld_moved) {
            attach_tasks(&env);
            ld_moved += cur_ld_moved;
        }

        if (env.flags & LBF_NEED_BREAK)
            goto more_balance;

        if (need_active_balance(&env)) {
            stop_one_cpu_nowait(cpu_of(busiest),
                active_load_balance_cpu_stop, busiest,
                &busiest->active_balance_work);
        }
    }
}
```

### 3.4 sched_balance_find_src_group() - 查找最繁忙组

**文件**: `kernel/sched/fair.c:11409-11541`

```c
static struct sched_group *sched_balance_find_src_group(struct lb_env *env)
{
    struct sg_lb_stats *local, *busiest;
    struct sd_lb_stats sds;

    init_sd_lb_stats(&sds);
    update_sd_lb_stats(env, &sds);

    if (!sds.busiest)
        goto out_balanced;

    busiest = &sds.busiest_stat;

    if (busiest->group_type == group_misfit_task)
        goto force_balance;

    if (busiest->group_type == group_asym_packing)
        goto force_balance;

    if (busiest->group_type == group_imbalanced)
        goto force_balance;

    local = &sds.local_stat;
    if (local->group_type > busiest->group_type)
        goto out_balanced;
    // ...
}
```

### 3.5 sched_balance_find_src_rq() - 查找最繁忙CPU

**文件**: `kernel/sched/fair.c:11547-11680`

```c
static struct rq *sched_balance_find_src_rq(struct lb_env *env,
                     struct sched_group *group)
{
    struct rq *busiest = NULL, *rq;
    unsigned long busiest_util = 0, busiest_load = 0;

    for_each_cpu_and(i, sched_group_span(group), env->cpus) {
        rq = cpu_rq(i);
        nr_running = rq->cfs.h_nr_runnable;
        if (!nr_running)
            continue;

        capacity = capacity_of(i);

        switch (env->migration_type) {
        case migrate_load:
            load = cpu_load(rq);
            if (load * busiest_capacity > busiest_load * capacity) {
                busiest_load = load;
                busiest_capacity = capacity;
                busiest = rq;
            }
            break;
        }
    }
    return busiest;
}
```

---

## 4. 负载均衡触发时机

### 4.1 周期性负载均衡

**文件**: `kernel/sched/fair.c:13066-13092`

```c
static __latent_entropy void sched_balance_softirq(void)
{
    struct rq *this_rq = this_rq();
    enum cpu_idle_type idle = this_rq->idle_balance;

    if (nohz_idle_balance(this_rq, idle))
        return;

    sched_balance_update_blocked_averages(this_rq->cpu);
    sched_balance_domains(this_rq, idle);
}
```

### 4.2 NEWIDLE 负载均衡 - CPU即将idle时

**文件**: `kernel/sched/fair.c:12922-13064`

```c
static int sched_balance_newidle(struct rq *this_rq, struct rq_flags *rf)
{
    int this_cpu = this_rq->cpu;
    int pulled_task = 0;
    struct sched_domain *sd;

    this_rq->idle_stamp = rq_clock(this_rq);

    sd = rcu_dereference_sched_domain(this_rq->sd);
    if (!sd)
        goto out;

    if (!get_rd_overloaded(this_rq->rd) ||
        this_rq->avg_idle < sd->max_newidle_lb_cost) {
        goto out;
    }

    for_each_domain(this_cpu, sd) {
        if (sd->flags & SD_BALANCE_NEWIDLE) {
            pulled_task = sched_balance_rq(this_cpu, this_rq,
                               sd, CPU_NEWLY_IDLE,
                               &continue_balancing);
            if (pulled_task || !continue_balancing)
                break;
        }
    }
    // ...
}
```

### 4.3 sched_balance_domains() - 遍历域进行平衡

**文件**: `kernel/sched/fair.c:12331-12401`

```c
static void sched_balance_domains(struct rq *rq, enum cpu_idle_type idle)
{
    int continue_balancing = 1;
    int cpu = rq->cpu;
    unsigned long interval;
    struct sched_domain *sd;

    rcu_read_lock();
    for_each_domain(cpu, sd) {
        interval = get_sd_balance_interval(sd, busy);
        if (time_after_eq(jiffies, sd->last_balance + interval)) {
            if (sched_balance_rq(cpu, rq, sd, idle, &continue_balancing)) {
                idle = idle_cpu(cpu);
                busy = !idle && !sched_idle_cpu(cpu);
            }
            sd->last_balance = jiffies;
        }
    }
    rcu_read_unlock();
}
```

---

## 5. 组类型 (group_type)

**文件**: `kernel/sched/fair.c:9276-9310`

```c
enum group_type {
    group_has_spare = 0,      /* 组有备用容量 */
    group_fully_busy,          /* 组完全使用 */
    group_misfit_task,         /* 任务不适合当前CPU容量 */
    group_smt_balance,         /* 平衡繁忙的SMT组 */
    group_asym_packing,        /* SD_ASYM_PACKING */
    group_imbalanced,          /* 由于亲和性约束导致不平衡 */
    group_overloaded           /* CPU过载 */
};
```

---

## 6. 负载均衡决策流程

```
schedule()
  └─> sched_balance_newidle() [CPU_IDLE]
  └─> sched_balance_domains()
       └─> for_each_domain(cpu, sd)
            └─> sched_balance_rq()
                  ├─> sched_balance_find_src_group()
                  │     └─> update_sd_lb_stats()
                  │     └─> calculate_imbalance()
                  └─> sched_balance_find_src_rq()
                        └─> detach_tasks()
                        └─> attach_tasks()
```

---

## 7. 调度域标志 (SD_*)

| 标志 | 描述 |
|------|------|
| `SD_BALANCE_NEWIDLE` | CPU即将idle时平衡 |
| `SD_BALANCE_EXEC` | exec时平衡 |
| `SD_BALANCE_FORK` | fork/clone时平衡 |
| `SD_BALANCE_WAKE` | wakeup时平衡 |
| `SD_WAKE_AFFINE` | 考虑在唤醒CPU上放置任务 |
| `SD_ASYM_CPUCAPACITY` | 成员有不同的CPU容量 |
| `SD_SHARE_CPUCAPACITY` | 成员共享CPU容量(SMT) |
| `SD_NUMA` | 跨节点平衡 |

---

## 8. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| detach_tasks | kernel/sched/fair.c | 9648-9781 |
| attach_tasks | kernel/sched/fair.c | 9813-9830 |
| sched_balance_rq | kernel/sched/fair.c | 11865-12149 |
| sched_balance_find_src_group | kernel/sched/fair.c | 11409-11541 |
| sched_balance_find_src_rq | kernel/sched/fair.c | 11547-11680 |
| sched_balance_newidle | kernel/sched/fair.c | 12922-13064 |
| sched_balance_domains | kernel/sched/fair.c | 12331-12401 |
| struct sched_domain | include/linux/sched/topology.h | 73-151 |
| struct sched_group | kernel/sched/sched.h | 2184-2202 |
| default_topology | kernel/sched/topology.c | 1789-1803 |
