# Linux 内核 CFS（完全公平调度器）分析

## 1. 核心数据结构

### 1.1 struct sched_entity - 调度实体

**文件**: `include/linux/sched.h:575-621`

```c
struct sched_entity {
    struct load_weight        load;           // 实体负载权重
    struct rb_node            run_node;       // 红黑树节点
    u64             deadline;               // EEVDF 截止时间
    u64             min_vruntime;           // 最小虚拟运行时间
    u64             vruntime;               // 虚拟运行时间 (核心!)

    struct list_head        group_node;
    unsigned char            on_rq;          // 是否在运行队列上
    unsigned char            sched_delayed;   // 是否延迟调度

    u64             exec_start;             // 执行开始时间
    u64             sum_exec_runtime;       // 累计执行时间
    u64             prev_sum_exec_runtime;

#ifdef CONFIG_FAIR_GROUP_SCHED
    int              depth;
    struct sched_entity        *parent;       // 父实体
    struct cfs_rq              *cfs_rq;     // 所属 CFS 运行队列
    struct cfs_rq              *my_q;         // 拥有的运行队列
#endif

    struct sched_avg        avg;              // PELT 负载跟踪
};
```

### 1.2 struct cfs_rq - CFS 运行队列

**文件**: `kernel/sched/sched.h:678-772`

```c
struct cfs_rq {
    struct load_weight      load;               // 队列负载
    unsigned int            nr_queued;           // 队列中的实体数
    unsigned int            h_nr_queued;         // SCHED_NORMAL 任务数

    s64              sum_w_vruntime;            // 加权虚拟运行时间和
    u64              sum_weight;                // 权重和

    struct rb_root_cached   tasks_timeline;     // 按 vruntime 排序的红黑树

    struct sched_entity     *curr;              // 当前运行的实体
    struct sched_entity     *next;              // 下一个 buddy

    struct sched_avg        avg;                // PELT 负载平均
};
```

---

## 2. CFS 虚拟时间 (Virtual Time)

### 2.1 vruntime 计算 - calc_delta_fair()

**文件**: `kernel/sched/fair.c:290-296`

```c
static inline u64 calc_delta_fair(u64 delta, struct sched_entity *se)
{
    if (unlikely(se->load.weight != NICE_0_LOAD))
        delta = __calc_delta(delta, NICE_0_LOAD, &se->load);

    return delta;
}
```

**说明**: 对于 `NICE_0_LOAD` (默认权重 1024) 的任务，vruntime 等于实际运行时间；对于其他权重任务，根据权重进行调整。

### 2.2 vruntime 更新 - update_curr()

**文件**: `kernel/sched/fair.c:1286-1332`

```c
static void update_curr(struct cfs_rq *cfs_rq)
{
    struct sched_entity *curr = cfs_rq->curr;
    struct rq *rq = rq_of(cfs_rq);
    s64 delta_exec;

    if (unlikely(!curr))
        return;

    delta_exec = update_se(rq, curr);
    if (unlikely(delta_exec <= 0))
        return;

    curr->vruntime += calc_delta_fair(delta_exec, curr);
}
```

### 2.3 place_entity() - 新任务和睡眠-唤醒处理

**文件**: `kernel/sched/fair.c:5165-5270`

```c
place_entity(struct cfs_rq *cfs_rq, struct sched_entity *se, int flags)
{
    u64 vslice, vruntime = avg_vruntime(cfs_rq);
    s64 lag = 0;

    if (!se->custom_slice)
        se->slice = sysctl_sched_base_slice;
    vslice = calc_delta_fair(se->slice, se);

    // PLACE_LAG: 保持 lag 平衡
    if (sched_feat(PLACE_LAG) && cfs_rq->nr_queued && se->vlag) {
        lag = se->vlag;
        lag *= load + scale_load_down(se->load.weight);
        lag = div_s64(lag, load);
    }

    se->vruntime = vruntime - lag;

    // EEVDF: vd_i = ve_i + r_i/w_i
    se->deadline = se->vruntime + vslice;
}
```

---

## 3. 实体入队/出队 - rbtree 操作

### 3.1 __enqueue_entity() - 入队

**文件**: `kernel/sched/fair.c:914-921`

```c
static void __enqueue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    sum_w_vruntime_add(cfs_rq, se);
    se->min_vruntime = se->vruntime;
    se->min_slice = se->slice;
    rb_add_augmented_cached(&se->run_node, &cfs_rq->tasks_timeline,
                __entity_less, &min_vruntime_cb);
}
```

### 3.2 __dequeue_entity() - 出队

**文件**: `kernel/sched/fair.c:923-928`

```c
static void __dequeue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    rb_erase_augmented_cached(&se->run_node, &cfs_rq->tasks_timeline,
                  &min_vruntime_cb);
    sum_w_vruntime_sub(cfs_rq, se);
}
```

### 3.3 enqueue_entity() - 完整入队流程

**文件**: `kernel/sched/fair.c:5279-5320`

```c
enqueue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se, int flags)
{
    bool curr = cfs_rq->curr == se;

    if (curr)
        place_entity(cfs_rq, se, flags);

    update_curr(cfs_rq);
    update_load_avg(cfs_rq, se, UPDATE_TG | DO_ATTACH);
    se_update_runnable(se);
    update_cfs_group(se);

    if (!curr)
        place_entity(cfs_rq, se, flags);

    account_entity_enqueue(cfs_rq, se);
}
```

---

## 4. 选择下一个任务

### 4.1 pick_next_task_fair() - 主入口

**文件**: `kernel/sched/fair.c:8978-9057`

```c
pick_next_task_fair(struct rq *rq, struct task_struct *prev, struct rq_flags *rf)
{
    struct sched_entity *se;
    struct task_struct *p;
    int new_tasks;

again:
    p = pick_task_fair(rq, rf);
    if (!p)
        goto idle;
    se = &p->se;

#ifdef CONFIG_FAIR_GROUP_SCHED
    if (prev->sched_class != &fair_sched_class)
        goto simple;
    // ... 层次结构处理
simple:
#endif
    put_prev_set_next_task(rq, prev, p);
    return p;

idle:
    if (rf) {
        new_tasks = sched_balance_newidle(rq, rf);
        if (new_tasks < 0)
            return RETRY_TASK;
        if (new_tasks > 0)
            goto again;
    }

    return NULL;
}
```

### 4.2 pick_task_fair() - 选择实体

**文件**: `kernel/sched/fair.c:8941-8971`

```c
static struct task_struct *pick_task_fair(struct rq *rq, struct rq_flags *rf)
{
    struct sched_entity *se;
    struct cfs_rq *cfs_rq;
    struct task_struct *p;
    bool throttled;

again:
    cfs_rq = &rq->cfs;
    if (!cfs_rq->nr_queued)
        return NULL;

    throttled = false;

    do {
        if (cfs_rq->curr && cfs_rq->curr->on_rq)
            update_curr(cfs_rq);

        throttled |= check_cfs_rq_runtime(cfs_rq);

        se = pick_next_entity(rq, cfs_rq);
        if (!se)
            goto again;
        cfs_rq = group_cfs_rq(se);
    } while (cfs_rq);

    p = task_of(se);
    return p;
}
```

### 4.3 pick_next_entity() - EEVDF 选择

**文件**: `kernel/sched/fair.c:5542-5556`

```c
static struct sched_entity *
pick_next_entity(struct rq *rq, struct cfs_rq *cfs_rq)
{
    struct sched_entity *se;

    se = pick_eevdf(cfs_rq);
    if (se->sched_delayed) {
        dequeue_entities(rq, se, DEQUEUE_SLEEP | DEQUEUE_DELAYED);
        return NULL;
    }
    return se;
}
```

### 4.4 __pick_eevdf() - EEVDF 算法核心

**文件**: `kernel/sched/fair.c:1010-1079`

```c
static struct sched_entity *__pick_eevdf(struct cfs_rq *cfs_rq, bool protect)
{
    struct rb_node *node = cfs_rq->tasks_timeline.rb_root.rb_node;
    struct sched_entity *se = __pick_first_entity(cfs_rq);
    struct sched_entity *curr = cfs_rq->curr;
    struct sched_entity *best = NULL;

    // 单个实体优化
    if (cfs_rq->nr_queued == 1)
        return curr && curr->on_rq ? curr : se;

    // PICK_BUDDY: 优先选择 next buddy
    if (sched_feat(PICK_BUDDY) &&
        cfs_rq->next && entity_eligible(cfs_rq, cfs_rq->next)) {
        return cfs_rq->next;
    }

    // 如果当前任务不满足条件，清除
    if (curr && (!curr->on_rq || !entity_eligible(cfs_rq, curr)))
        curr = NULL;

    // 保护切片：当前任务在保护期内
    if (curr && protect && protect_slice(curr))
        return curr;

    // 选择最左侧实体（最小 deadline）
    if (se && entity_eligible(cfs_rq, se)) {
        best = se;
        goto found;
    }

    // ... 堆搜索找到 EEVDF 实体

found:
    if (!best || (curr && entity_before(curr, best)))
        best = curr;

    return best;
}
```

### 4.5 entity_eligible() - 实体是否符合调度条件

**文件**: `kernel/sched/fair.c:813-816`

```c
int entity_eligible(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    return vruntime_eligible(cfs_rq, se->vruntime);
}
```

---

## 5. put_prev_task_fair()

**文件**: `kernel/sched/fair.c:9077-9086`

```c
static void put_prev_task_fair(struct rq *rq, struct task_struct *prev, struct task_struct *next)
{
    struct sched_entity *se = &prev->se;
    struct cfs_rq *cfs_rq;

    for_each_sched_entity(se) {
        cfs_rq = cfs_rq_of(se);
        put_prev_entity(cfs_rq, se);
    }
}
```

### put_prev_entity()

**文件**: `kernel/sched/fair.c:5560-5581`

```c
static void put_prev_entity(struct cfs_rq *cfs_rq, struct sched_entity *prev)
{
    if (prev->on_rq)
        update_curr(cfs_rq);

    check_cfs_rq_runtime(cfs_rq);

    if (prev->on_rq) {
        update_stats_wait_start_fair(cfs_rq, prev);
        __enqueue_entity(cfs_rq, prev);
        update_load_avg(cfs_rq, prev, 0);
    }
    cfs_rq->curr = NULL;
}
```

---

## 6. 调度延迟和 Target Latency

### sysctl_sched_base_slice

**文件**: `kernel/sched/fair.c:79`

```c
unsigned int sysctl_sched_base_slice = 700000ULL;  // 700 微秒
```

### EEVDF 截止时间和 vruntime 的关系

**文件**: `kernel/sched/fair.c:1117-1140`

```c
static bool update_deadline(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    if (vruntime_cmp(se->vruntime, "<", se->deadline))
        return false;

    if (!se->custom_slice)
        se->slice = sysctl_sched_base_slice;

    // EEVDF: vd_i = ve_i + r_i / w_i
    se->deadline = se->vruntime + calc_delta_fair(se->slice, se);
    avg_vruntime(cfs_rq);

    return true;
}
```

---

## 7. CFS 核心概念总结

### 7.1 公平性保证

CFS 通过以下机制保证公平性:

1. **lag 跟踪**: `lag_i = w_i * (V - v_i)`，其中 `V` 是所有实体的加权平均虚拟时间
2. **实体合格性**: 只有 `lag >= 0` 的实体才能被选中
3. **加权平均**: 低权重任务（高 nice 值）的 vruntime 增长更快

### 7.2 EEVDF 选择算法

1. 检查 `cfs_rq->next` buddy (PICK_BUDDY 优化)
2. 检查 `cfs_rq->curr` 是否在保护期内
3. 返回红黑树最左边符合条件的节点

---

## 8. 关键代码路径

### 入队流程
```
enqueue_task_fair()
  └─> enqueue_entity()
        ├─> place_entity()
        ├─> update_curr()
        └─> __enqueue_entity()  // 插入红黑树
```

### 任务选择流程
```
pick_next_task_fair()
  └─> pick_task_fair()
        └─> pick_next_entity()
              └─> pick_eevdf()
```

---

## 9. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| struct sched_entity | include/linux/sched.h | 575-621 |
| struct cfs_rq | kernel/sched/sched.h | 678-772 |
| calc_delta_fair | kernel/sched/fair.c | 290-296 |
| update_curr | kernel/sched/fair.c | 1286-1332 |
| place_entity | kernel/sched/fair.c | 5165-5270 |
| __enqueue_entity | kernel/sched/fair.c | 914-921 |
| __dequeue_entity | kernel/sched/fair.c | 923-928 |
| enqueue_entity | kernel/sched/fair.c | 5279-5320 |
| pick_next_task_fair | kernel/sched/fair.c | 8978-9057 |
| pick_task_fair | kernel/sched/fair.c | 8941-8971 |
| pick_next_entity | kernel/sched/fair.c | 5542-5556 |
| __pick_eevdf | kernel/sched/fair.c | 1010-1079 |
| entity_eligible | kernel/sched/fair.c | 813-816 |
| put_prev_entity | kernel/sched/fair.c | 5560-5581 |
| sysctl_sched_base_slice | kernel/sched/fair.c | 79 |
