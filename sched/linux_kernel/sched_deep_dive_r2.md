# Linux Sched 子系统深度分析 R2

## 目录

1. [概述](#概述)
2. [pick_eevdf 详细算法](#pick_eevdf-详细算法)
3. [calc_delta_fair 算法分析](#calc_delta_fair-算法分析)
4. [update_curr 更新机制](#update_curr-更新机制)
5. [enqueue_entity 入队流程](#enqueue_entity-入队流程)
6. [dequeue_entity 出队流程](#dequeue_entity-出队流程)
7. [NUMA 感知调度](#numa-感知调度)
8. [知识点关联表格](#知识点关联表格)

---

## 概述

本文档深入分析 Linux kernel CFS (Completely Fair Scheduler) 调度器的核心算法实现，基于 `kernel/sched/fair.c` 源码。EEVDF (Early Eligible Virtual Deadline First) 调度器是当前内核默认的调度策略，其核心思想是通过虚拟运行时间 (vruntime) 和 deadline 来保证调度的公平性。

---

## 1. pick_eevdf 详细算法

### 1.1 核心数据结构

```c
// kernel/sched/fair.c:1010-1079
static struct sched_entity *__pick_eevdf(struct cfs_rq *cfs_rq, bool protect)
{
    struct rb_node *node = cfs_rq->tasks_timeline.rb_root.rb_node;
    struct sched_entity *se = __pick_first_entity(cfs_rq);
    struct sched_entity *curr = cfs_rq->curr;
    struct sched_entity *best = NULL;
    // ...
}
```

EEVDF 使用红黑树 (`tasks_timeline`) 存储所有可运行实体，树按照 **deadline** 排序，但同时通过 `min_vruntime` 维护堆属性：

```c
// kernel/sched/fair.c:908-909
RB_DECLARE_CALLBACKS(static, min_vruntime_cb, struct sched_entity,
             run_node, min_vruntime, min_vruntime_update);

// kernel/sched/fair.c:1006
// 树维护: se->min_vruntime = min(se->vruntime, se->{left,right}->min_vruntime)
```

### 1.2 Lag 计算公式

Lag 定义了任务实际获得的服务时间与理想服务时间的偏差：

```c
// kernel/sched/fair.c:622-624
// Lag 定义: lag_i = S - s_i = w_i * (V - v_i)
//
// 其中:
//   S  = 理想服务时间
//   s_i = 任务实际服务时间
//   w_i = 任务权重 (与 nice 值相关)
//   V   = 虚拟时间 (加权平均)
//   v_i = 任务虚拟运行时间
```

### 1.3 entity_key() 函数

```c
// kernel/sched/fair.c:607-609
static inline s64 entity_key(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    return vruntime_op(se->vruntime, "-", cfs_rq->zero_vruntime);
    // 即: se->vruntime - cfs_rq->zero_vruntime
}
```

`entity_key` 计算实体虚拟运行时间相对于 `zero_vruntime` 的偏移量。由于 `zero_vruntime` 追踪所有任务的平均虚拟运行时间：

```c
// kernel/sched/fair.c:636-638
// V = (\Sum v_i * w_i) / \Sum w_i = (\Sum v_i * w_i) / W
//
// 其中: W = cfs_rq->sum_weight
//       sum_w_vruntime = \Sum (v_i - v0) * w_i
//       zero_vruntime = v0
```

### 1.4 v_i - w_i * V 排序

EEVDF 的选择算法核心思想：**选择具有最小 "有效虚拟 deadline" 的实体**。

Deadline 计算公式 (第 1131-1133 行):
```c
// EEVDF: vd_i = ve_i + r_i / w_i
se->deadline = se->vruntime + calc_delta_fair(se->slice, se);
```

### 1.5 pick_eevdf 算法流程

```c
// kernel/sched/fair.c:1010-1079
static struct sched_entity *__pick_eevdf(struct cfs_rq *cfs_rq, bool protect)
{
    // 步骤 1: 如果只有一个实体，直接返回
    if (cfs_rq->nr_queued == 1)
        return curr && curr->on_rq ? curr : se;

    // 步骤 2: 检查 next buddy (PICK_BUDDY 特性)
    if (sched_feat(PICK_BUDDY) &&
        cfs_rq->next && entity_eligible(cfs_rq, cfs_rq->next)) {
        return cfs_rq->next;  // next buddy 永远不会延迟
    }

    // 步骤 3: 检查 current 是否符合条件
    if (curr && (!curr->on_rq || !entity_eligible(cfs_rq, curr)))
        curr = NULL;

    // 步骤 4: 如果 curr 正在运行且受保护，直接返回
    if (curr && protect && protect_slice(curr))
        return curr;

    // 步骤 5: 如果最左实体符合条件，直接返回
    if (se && entity_eligible(cfs_rq, se)) {
        best = se;
        goto found;
    }

    // 步骤 6: 红黑树剪枝搜索
    // 利用 min_vruntime 剪枝: 如果左子树的 min_vruntime 符合条件，则整个左子树都符合
    while (node) {
        struct rb_node *left = node->rb_left;

        if (left && vruntime_eligible(cfs_rq,
                    __node_2_se(left)->min_vruntime)) {
            node = left;  // 左子树有符合条件的实体
            continue;
        }

        se = __node_2_se(node);

        if (entity_eligible(cfs_rq, se)) {
            best = se;
            break;  // 找到符合条件的实体
        }

        node = node->rb_right;  // 搜索右子树
    }

found:
    // 步骤 7: 最终选择 (deadline 最早者)
    if (!best || (curr && entity_before(curr, best)))
        best = curr;

    return best;
}
```

### 1.6 vruntime_eligible 判定

```c
// kernel/sched/fair.c:797-811
static int vruntime_eligible(struct cfs_rq *cfs_rq, u64 vruntime)
{
    struct sched_entity *curr = cfs_rq->curr;
    s64 avg = cfs_rq->sum_w_vruntime;
    long load = cfs_rq->sum_weight;

    if (curr && curr->on_rq) {
        unsigned long weight = scale_load_down(curr->load.weight);
        avg += entity_key(cfs_rq, curr) * weight;
        load += weight;
    }

    // 判定条件: avg >= (vruntime - zero_vruntime) * load
    // 即: V >= v_i (lag >= 0)
    return avg >= vruntime_op(vruntime, "-", cfs_rq->zero_vruntime) * load;
}
```

**核心概念**: 实体只有在 `lag >= 0` (即获得了应有的服务时间) 时才是 eligible 的。

---

## 2. calc_delta_fair 算法分析

### 2.1 函数定义

```c
// kernel/sched/fair.c:290-296
static inline u64 calc_delta_fair(u64 delta, struct sched_entity *se)
{
    if (unlikely(se->load.weight != NICE_0_LOAD))
        delta = __calc_delta(delta, NICE_0_LOAD, &se->load);

    return delta;
}
```

### 2.2 权重与 delta 计算

`calc_delta_fair` 的核心功能是**根据任务权重调整 delta 时间**。

```c
// kernel/sched/fair.c:256-285
static u64 __calc_delta(u64 delta_exec, unsigned long weight, struct load_weight *lw)
{
    u64 fact = scale_load_down(weight);
    u32  shift = WMULT_SHIFT;
    int  fs;

    // NICE_0_LOAD = 1024
    if (unlikely(weight == NICE_0_LOAD))
        return delta_exec;

    // fact = weight / NICE_0_LOAD
    fact = div64_u64(fact << WMULT_SHIFT, lw->inv_weight);
    // 或者: fact = weight * (2^19) / NICE_0_LOAD

    // 计算右移位数
    fs = fls(weight >> NICE_0_LOAD);
    if (fs)
        shift -= fs;

    // 最终: delta * weight / NICE_0_LOAD
    return mul_u64_u32_shr(delta_exec, fact, shift);
}
```

### 2.3 nlmp 与 prandom_fudge

在当前代码中，`nlmp` (nice load multiplier perspective) 和 `prandom_fudge` 是在计算权重调整时的辅助概念。实际的计算通过 `__calc_delta` 完成。

**核心公式**:
```
delta_fair = delta * NICE_0_LOAD / weight = delta / (weight / NICE_0_LOAD)
```

这意味着:
- **高优先级任务 (大 weight)**: `delta_fair < delta`，获得更多 CPU 时间
- **低优先级任务 (小 weight)**: `delta_fair > delta`，获得更少 CPU 时间

### 2.4 vruntime 累加

```c
// kernel/sched/fair.c:1306
curr->vruntime += calc_delta_fair(delta_exec, curr);
```

每次任务运行 `delta_exec` 时间后，其 `vruntime` 增加量为 `calc_delta_fair(delta_exec, curr)`。由于 `calc_delta_fair` 考虑了权重:

- 相同物理运行时间，高权重任务 `vruntime` 增长更慢
- 这保证了**虚拟时间上的公平性**: 不同权重的任务获得相等的 "虚拟服务时间"

---

## 3. update_curr 更新机制

### 3.1 函数入口

```c
// kernel/sched/fair.c:1286-1332
static void update_curr(struct cfs_rq *cfs_rq)
{
    struct sched_entity *curr = cfs_rq->curr;
    struct rq *rq = rq_of(cfs_rq);
    s64 delta_exec;
    bool resched;

    if (unlikely(!curr))
        return;

    delta_exec = update_se(rq, curr);
    if (unlikely(delta_exec <= 0))
        return;

    // 更新当前任务的虚拟运行时间
    curr->vruntime += calc_delta_fair(delta_exec, curr);
    resched = update_deadline(cfs_rq, curr);

    // 公平服务器时间更新
    if (entity_is_task(curr)) {
        dl_server_update(&rq->fair_server, delta_exec);
    }

    account_cfs_rq_runtime(cfs_rq, delta_exec);

    if (cfs_rq->nr_queued == 1)
        return;

    if (resched || !protect_slice(curr)) {
        resched_curr_lazy(rq);
        clear_buddies(cfs_rq, curr);
    }
}
```

### 3.2 min_vruntime 维护

`min_vruntime` 通过红黑树 augmented callback 自动维护：

```c
// kernel/sched/fair.c:882-904
// se->min_vruntime = min(se->vruntime, se->{left,right}->min_vruntime)

static inline bool min_vruntime_update(struct sched_entity *se, bool exit)
{
    u64 old_min_vruntime = se->min_vruntime;
    struct rb_node *node = &se->run_node;

    se->min_vruntime = se->vruntime;
    __min_vruntime_update(se, node->rb_right);
    __min_vruntime_update(se, node->rb_left);

    // ...
}

static inline void __min_vruntime_update(struct sched_entity *se, struct rb_node *node)
{
    // 递归更新 min_vruntime
}
```

### 3.3 sysctl_sched_child_runs_first

当前内核版本中，`sysctl_sched_child_runs_first` 主要在 fork 时通过 `place_entity` 处理：

```c
// kernel/sched/fair.c:5165-5270
static void place_entity(struct cfs_rq *cfs_rq, struct sched_entity *se, int flags)
{
    u64 vslice, vruntime = avg_vruntime(cfs_rq);
    s64 lag = 0;

    if (!se->custom_slice)
        se->slice = sysctl_sched_base_slice;
    vslice = calc_delta_fair(se->slice, se);

    // PLACE_LAG 特性：保持 lag 约束
    if (sched_feat(PLACE_LAG) && cfs_rq->nr_queued && se->vlag) {
        // 调整 lag 以保持公平性
        lag = se->vlag;
        load = cfs_rq->sum_weight;
        if (curr && curr->on_rq)
            load += scale_load_down(curr->load.weight);

        lag *= load + scale_load_down(se->load.weight);
        lag = div_s64(lag, load);
    }

    se->vruntime = vruntime - lag;

    // 新任务初始 deadline 调整
    if (sched_feat(PLACE_DEADLINE_INITIAL) && (flags & ENQUEUE_INITIAL))
        vslice /= 2;  // 新任务从半 slice 开始，便于融入调度循环

    // EEVDF: vd_i = ve_i + r_i / w_i
    se->deadline = se->vruntime + vslice;
}
```

### 3.4 update_deadline 检查

```c
// kernel/sched/fair.c:1117-1140
static bool update_deadline(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    // 如果 vruntime < deadline，无需更新
    if (vruntime_cmp(se->vruntime, "<", se->deadline))
        return false;

    // 更新 slice (如果不是自定义 slice)
    if (!se->custom_slice)
        se->slice = sysctl_sched_base_slice;

    // EEVDF: 重新计算 deadline
    // vd_i = ve_i + r_i / w_i
    se->deadline = se->vruntime + calc_delta_fair(se->slice, se);
    avg_vruntime(cfs_rq);  // 更新平均虚拟时间

    return true;  // 需要重新调度
}
```

---

## 4. enqueue_entity 入队流程

### 4.1 函数入口

```c
// kernel/sched/fair.c:5279-5342
enqueue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se, int flags)
{
    bool curr = cfs_rq->curr == se;

    // 如果是当前任务，先调整 vruntime
    if (curr)
        place_entity(cfs_rq, se, flags);

    update_curr(cfs_rq);

    // 更新负载统计
    update_load_avg(cfs_rq, se, UPDATE_TG | DO_ATTACH);
    se_update_runnable(se);
    update_cfs_group(se);

    // 如果不是当前任务，再次调整 vruntime
    if (!curr)
        place_entity(cfs_rq, se, flags);

    account_entity_enqueue(cfs_rq, se);

    if (flags & ENQUEUE_MIGRATED)
        se->exec_start = 0;

    update_stats_enqueue_fair(cfs_rq, se, flags);

    // 插入红黑树
    if (!curr)
        __enqueue_entity(cfs_rq, se);

    se->on_rq = 1;

    if (cfs_rq->nr_queued == 1) {
        check_enqueue_throttle(cfs_rq);
        list_add_leaf_cfs_rq(cfs_rq);
    }
}
```

### 4.2 __enqueue_entity 红黑树插入

```c
// kernel/sched/fair.c:914-921
static void __enqueue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    // 更新加权虚拟时间累加器
    sum_w_vruntime_add(cfs_rq, se);

    // 初始化 min_vruntime 和 min_slice
    se->min_vruntime = se->vruntime;
    se->min_slice = se->slice;

    // 插入红黑树 (按 deadline 排序)
    rb_add_augmented_cached(&se->run_node, &cfs_rq->tasks_timeline,
                __entity_less, &min_vruntime_cb);
}
```

### 4.3 place_entity 虚拟时间调整

```c
// kernel/sched/fair.c:5165-5270
place_entity(struct cfs_rq *cfs_rq, struct sched_entity *se, int flags)
{
    u64 vslice, vruntime = avg_vruntime(cfs_rq);
    s64 lag = 0;

    // 计算虚拟 slice
    if (!se->custom_slice)
        se->slice = sysctl_sched_base_slice;
    vslice = calc_delta_fair(se->slice, se);

    // Lag 保持算法 (PLACE_LAG)
    // 当添加/删除任务时，需要调整以保持 lag 约束
    if (sched_feat(PLACE_LAG) && cfs_rq->nr_queued && se->vlag) {
        lag = se->vlag;
        load = cfs_rq->sum_weight;
        if (curr && curr->on_rq)
            load += scale_load_down(curr->load.weight);

        // 调整 lag 以保持系统公平性
        lag *= load + scale_load_down(se->load.weight);
        lag = div_s64(lag, load);
    }

    // 计算新任务的 vruntime
    // v_i = V - lag_i (lag_i >= 0 时任务有资格运行)
    se->vruntime = vruntime - lag;

    // REL_DEADLINE 处理
    if (se->rel_deadline) {
        se->deadline += se->vruntime;
        se->rel_deadline = 0;
        return;
    }

    // 新任务初始半 slice
    if (sched_feat(PLACE_DEADLINE_INITIAL) && (flags & ENQUEUE_INITIAL))
        vslice /= 2;

    // EEVDF: deadline = vruntime + vslice
    se->deadline = se->vruntime + vslice;
}
```

### 4.4 Lag 保持数学推导

当添加新任务时，为了保持系统 lag 守恒：

```c
// 添加实体后的加权平均:
// V' = (W*V + w_i*(V - vl_i)) / (W + w_i)
//     = V - w_i*vl_i / (W + w_i)

// 添加后的实际 lag:
// vl'_i = V' - v_i
//        = V - w_i*vl_i / (W + w_i) - (V - vl_i)
//        = vl_i - w_i*vl_i / (W + w_i)

// 要保持 vl'_i 不变，需要:
// vl_i = (W + w_i) * vl'_i / W
```

---

## 5. dequeue_entity 出队流程

### 5.1 函数入口

```c
// kernel/sched/fair.c:5410-5489
dequeue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se, int flags)
{
    bool sleep = flags & DEQUEUE_SLEEP;
    int action = UPDATE_TG;

    update_curr(cfs_rq);           // 先更新当前时间
    clear_buddies(cfs_rq, se);     // 清除 buddy 标记

    // DELAY_DEQUEUE 特性
    if (flags & DEQUEUE_DELAYED) {
        WARN_ON_ONCE(!se->sched_delayed);
    } else {
        bool delay = sleep;
        if (flags & (DEQUEUE_SPECIAL | DEQUEUE_THROTTLE))
            delay = false;

        // 如果任务不符合条件且启用了延迟出队
        if (sched_feat(DELAY_DEQUEUE) && delay &&
            !entity_eligible(cfs_rq, se)) {
            update_load_avg(cfs_rq, se, 0);
            set_delayed(se);  // 标记为延迟，不真正出队
            return false;
        }
    }

    // 分离负载统计
    if (entity_is_task(se) && task_on_rq_migrating(task_of(se)))
        action |= DO_DETACH;

    update_load_avg(cfs_rq, se, action);
    se_update_runnable(se);

    update_stats_dequeue_fair(cfs_rq, se, flags);

    // 更新实体 lag
    update_entity_lag(cfs_rq, se);

    // PLACE_REL_DEADLINE 处理
    if (sched_feat(PLACE_REL_DEADLINE) && !sleep) {
        se->deadline -= se->vruntime;
        se->rel_deadline = 1;
    }

    // 从红黑树移除
    if (se != cfs_rq->curr)
        __dequeue_entity(cfs_rq, se);
    se->on_rq = 0;

    account_entity_dequeue(cfs_rq, se);
    return_cfs_rq_runtime(cfs_rq);
    update_cfs_group(se);

    if (flags & DEQUEUE_DELAYED)
        finish_delayed_dequeue_entity(se);

    // ...
    return true;
}
```

### 5.2 __dequeue_entity 红黑树移除

```c
// kernel/sched/fair.c:923-928
static void __dequeue_entity(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    // 从红黑树移除
    rb_erase_augmented_cached(&se->run_node, &cfs_rq->tasks_timeline,
                  &min_vruntime_cb);

    // 从加权虚拟时间累加器移除
    sum_w_vruntime_sub(cfs_rq, se);
}
```

### 5.3 update_entity_lag 权重继承

```c
// kernel/sched/fair.c:767-778
static void update_entity_lag(struct cfs_rq *cfs_rq, struct sched_entity *se)
{
    u64 max_slice = cfs_rq_max_slice(cfs_rq) + TICK_NSEC;
    s64 vlag, limit;

    WARN_ON_ONCE(!se->on_rq);

    // vlag = avg_vruntime - se->vruntime
    vlag = avg_vruntime(cfs_rq) - se->vruntime;

    // 限制 vlag 范围
    // EEVDF 稳态约束: -r_max < lag < max(r_max, q)
    limit = calc_delta_fair(max_slice, se);
    se->vlag = clamp(vlag, -limit, limit);
}
```

### 5.4 DELAY_DEQUEUE 机制

当 `sched_feat(DELAY_DEQUEUE)` 启用时，不符合条件的任务会被标记为 `sched_delayed` 而不是立即出队：

```c
// kernel/sched/fair.c:5363-5380
static void set_delayed(struct sched_entity *se)
{
    se->sched_delayed = 1;

    if (!entity_is_task(se))
        return;

    // 减少 h_nr_runnable 计数
    for_each_sched_entity(se) {
        struct cfs_rq *cfs_rq = cfs_rq_of(se);
        cfs_rq->h_nr_runnable--;
    }
}
```

延迟出队的任务会在合适的时机通过 `finish_delayed_dequeue_entity` 完成出队：

```c
// kernel/sched/fair.c:5402-5407
static inline void finish_delayed_dequeue_entity(struct sched_entity *se)
{
    clear_delayed(se);
    if (sched_feat(DELAY_ZERO) && se->vlag > 0)
        se->vlag = 0;  // 可选的 lag 清零优化
}
```

---

## 6. NUMA 感知调度

### 6.1 task_numa_placement 核心函数

```c
// kernel/sched/fair.c:2952-3064
static void task_numa_placement(struct task_struct *p)
{
    int seq, nid, max_nid = NUMA_NO_NODE;
    unsigned long max_faults = 0;
    unsigned long fault_types[2] = { 0, 0 };
    unsigned long total_faults;
    u64 runtime, period;
    spinlock_t *group_lock = NULL;
    struct numa_group *ng;

    // 读取当前扫描序列号
    seq = READ_ONCE(p->mm->numa_scan_seq);
    if (p->numa_scan_seq == seq)
        return;  // 已扫描，无更新
    p->numa_scan_seq = seq;

    // 获取任务运行时间和周期
    total_faults = p->numa_faults_locality[0] + p->numa_faults_locality[1];
    runtime = numa_get_avg_runtime(p, &period);

    // 处理 NUMA group 锁
    ng = deref_curr_numa_group(p);
    if (ng) {
        group_lock = &ng->lock;
        spin_lock_irq(group_lock);
    }

    // 遍历所有在线节点，查找最大 fault 数
    for_each_online_node(nid) {
        unsigned long faults = 0, group_faults = 0;
        int priv;

        for (priv = 0; priv < NR_NUMA_HINT_FAULT_TYPES; priv++) {
            long diff, f_diff, f_weight;

            // 获取 fault 缓冲区索引
            mem_idx = task_faults_idx(NUMA_MEM, nid, priv);
            membuf_idx = task_faults_idx(NUMA_MEMBUF, nid, priv);
            cpu_idx = task_faults_idx(NUMA_CPU, nid, priv);
            cpubuf_idx = task_faults_idx(NUMA_CPUBUF, nid, priv);

            // 衰减旧 fault，累加新 fault
            diff = p->numa_faults[membuf_idx] - p->numa_faults[mem_idx] / 2;
            fault_types[priv] += p->numa_faults[membuf_idx];
            p->numa_faults[membuf_idx] = 0;

            // 计算 fault 权重 (根据 CPU 使用时间归一化)
            f_weight = div64_u64(runtime << 16, period + 1);
            f_weight = (f_weight * p->numa_faults[cpubuf_idx]) / (total_faults + 1);
            f_diff = f_weight - p->numa_faults[cpu_idx] / 2;

            p->numa_faults[mem_idx] += diff;
            p->numa_faults[cpu_idx] += f_diff;
            faults += p->numa_faults[mem_idx];
            p->total_numa_faults += diff;

            // NUMA group 统计更新
            if (ng) {
                ng->faults[mem_idx] += diff;
                ng->faults[cpu_idx] += f_diff;
                ng->total_faults += diff;
                group_faults += ng->faults[mem_idx];
            }
        }

        // 更新最大 fault 节点
        if (!ng) {
            if (faults > max_faults) {
                max_faults = faults;
                max_nid = nid;
            }
        } else if (group_faults > max_faults) {
            max_faults = group_faults;
            max_nid = nid;
        }
    }

    // 转换为可用的 CPU 节点
    max_nid = numa_nearest_node(max_nid, N_CPU);

    // 更新 preferred group nid
    if (ng) {
        numa_group_count_active_nodes(ng);
        spin_unlock_irq(group_lock);
        max_nid = preferred_group_nid(p, max_nid);
    }

    // 设置新的 preferred node
    if (max_faults) {
        if (max_nid != p->numa_preferred_nid)
            sched_setnuma(p, max_nid);
    }

    // 更新扫描周期
    update_task_scan_period(p, fault_types[0], fault_types[1]);
}
```

### 6.2 NUMA Fault 类型

NUMA hinting fault 有两种类型：

```c
// 两种 fault 类型:
// NUMA_MEM - 内存访问 fault
// NUMA_CPU - CPU 访问 fault (访问其他节点内存)
```

### 6.3 Fault 权重计算

```c
// 根据任务运行时间归一化 fault 数量
f_weight = (runtime << 16) / (period + 1)
f_weight = f_weight * numa_faults[cpubuf_idx] / (total_faults + 1)
```

这确保了：
- CPU 密集型任务的 fault 权重更高
- 短时间任务的 fault 权重较低

### 6.4 NUMA 调度决策流程

```
task_numa_placement() 执行流程:

1. 获取当前扫描序列号
   |
2. 计算归一化运行时间和周期
   |
3. 遍历所有在线节点
   |  ├── 累加每种 fault 类型的数量
   |  ├── 计算 fault 权重
   |  └── 更新最大 fault 节点
   |
4. 处理 NUMA group
   |  ├── 统计 group 总 fault
   |  └── 计算 preferred group nid
   |
5. 更新任务的 numa_preferred_nid
   |
6. 调整扫描周期
```

### 6.5 numa_hint_fault_latency

```c
// kernel/sched/fair.c:1920
static int numa_hint_fault_latency(struct folio *folio)
{
    // 计算 folio 访问延迟
    // 用于判断是否应该迁移任务到访问的节点
}
```

---

## 知识点关联表格

| 概念 | 源码位置 | 核心公式/逻辑 | 作用 |
|------|----------|---------------|------|
| **pick_eevdf** | fair.c:1010-1079 | 选择 deadline 最小的 eligible 实体 | 选择下一个运行任务 |
| **entity_key** | fair.c:607-609 | `vruntime - zero_vruntime` | 计算实体相对于平均的位置 |
| **vruntime_eligible** | fair.c:797-811 | `avg >= (v_i - v0) * W` | 判断 lag >= 0 |
| **calc_delta_fair** | fair.c:290-296 | `delta * NICE_0_LOAD / weight` | 根据权重调整时间分配 |
| **update_curr** | fair.c:1286-1332 | `vruntime += calc_delta_fair()` | 更新当前任务的虚拟时间 |
| **update_deadline** | fair.c:1117-1140 | `deadline = vruntime + slice/weight` | EEVDF deadline 重计算 |
| **avg_vruntime** | fair.c:715-749 | `V = (\Sum v_i*w_i) / W` | 计算系统平均虚拟时间 |
| **place_entity** | fair.c:5165-5270 | `vruntime = V - lag` | 新任务/出队任务的 vruntime 调整 |
| **__enqueue_entity** | fair.c:914-921 | `sum_w_vruntime_add()` | 红黑树插入并更新统计 |
| **__dequeue_entity** | fair.c:923-928 | `sum_w_vruntime_sub()` | 红黑树移除并更新统计 |
| **update_entity_lag** | fair.c:767-778 | `vlag = V - v_i` clamped | 计算并限制 lag 范围 |
| **task_numa_placement** | fair.c:2952-3064 | 统计每个节点的 fault 数 | NUMA 感知任务放置 |
| **min_vruntime** | fair.c:882-909 | `min(vruntime, children's min_vruntime)` | 红黑树剪枝加速 |
| **entity_before** | fair.c:582-590 | `deadline_a < deadline_b` | 按 deadline 排序比较 |

### 关键数据结构关系

```
cfs_rq (CFS 运行队列)
|
|-- tasks_timeline (红黑树, 按 deadline 排序)
|   |
|   +-- sched_entity
|       |-- vruntime: 虚拟运行时间
|       |-- deadline: EEVDF 截止时间 (vruntime + slice/weight)
|       |-- min_vruntime: 子树最小 vruntime
|       |-- min_slice: 子树最小 slice
|       |-- slice: 时间片长度
|       |-- vlag: 虚拟 lag (V - v_i)
|       +-- load.weight: 任务权重 (nice 值相关)
|
|-- sum_w_vruntime: \Sum (v_i - v0) * w_i
|-- sum_weight: \Sum w_i
|-- zero_vruntime: v0 (基准虚拟时间)
|-- min_vruntime: 全队列最小 vruntime
|
+-- curr: 当前运行的 sched_entity
```

### EEVDF 调度核心公式

1. **虚拟时间增长**: `v_i += delta / w_i`
2. **Deadline 计算**: `d_i = v_i + r_i / w_i`
3. **Lag 定义**: `lag_i = w_i * (V - v_i)`
4. **选择条件**: `lag_i >= 0` (即 `v_i <= V`)
5. **加权平均**: `V = (\Sum v_i*w_i) / (\Sum w_i)`

---

## 参考源码文件

- `kernel/sched/fair.c` - CFS 调度器实现 (主要分析文件)
- `kernel/sched/sched.h` - 调度器数据结构定义
- `kernel/sched/core.c` - 调度器核心函数

---

*文档版本: R2*
*分析基于: Linux kernel master branch*
