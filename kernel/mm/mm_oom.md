# Linux Kernel OOM Killer 分析文档

## 目录

1. [概述](#1-概述)
2. [核心数据结构](#2-核心数据结构)
3. [out_of_memory 主函数和触发流程](#3-out_of_memory-主函数和触发流程)
4. [select_bad_process 选择最差进程](#4-select_bad_process-选择最差进程)
5. [oom_badness 评分算法](#5-oom_badness-评分算法)
6. [oom_kill_process 杀进程流程](#6-oom_kill_process-杀进程流程)
7. [oom_score_adj 机制](#7-oom_score_adj-机制)
8. [memcg OOM 处理](#8-memcg-oom-处理)
9. [OOM Reaper 异步回收](#9-oom-reaper-异步回收)
10. [不可杀进程检查](#10-不可杀进程检查)
11. [OOM Killer 完整流程图](#11-oom-killer-完整流程图)
12. [关键源码位置汇总](#12-关键源码位置汇总)

---

## 1. 概述

OOM Killer (Out of Memory Killer) 是 Linux 内核在物理内存和交换空间耗尽时，用于选择并杀死进程以释放内存的机制。

**设计目标**:
- 选择消耗内存最多的"最差"进程进行杀死
- 避免杀死关键系统进程 (init, kernel threads)
- 通过 oom_score_adj 允许用户调整进程优先级

---

## 2. 核心数据结构

### 2.1 oom_control 结构体

**位置**: `include/linux/oom.h` (第 28-54 行)

```c
struct oom_control {
    struct zonelist *zonelist;      // 用于确定 cpuset
    nodemask_t *nodemask;           // 用于确定 mempolicy
    struct mem_cgroup *memcg;       // global OOM 时为 NULL, memcg OOM 时指向对应 cgroup
    const gfp_t gfp_mask;           // 触发 OOM 的分配掩码
    const int order;                // 分配阶数, -1 表示 sysrq 触发
    unsigned long totalpages;        // 可用内存总页数
    struct task_struct *chosen;     // 选中的 victim 进程
    long chosen_points;             // 选中进程的评分
    enum oom_constraint constraint; // 约束类型
};
```

### 2.2 oom_constraint 枚举

**位置**: `include/linux/oom.h` (第 17-22 行)

```c
enum oom_constraint {
    CONSTRAINT_NONE,           // 无约束 (全局 OOM)
    CONSTRAINT_CPUSET,         // cpuset 限制
    CONSTRAINT_MEMORY_POLICY,  // NUMA mempolicy 限制
    CONSTRAINT_MEMCG,          // memcg 限制
};
```

### 2.3 oom_score_adj 值定义

**位置**: `include/uapi/linux/oom.h` (第 9-10 行)

| 常量 | 值 | 说明 |
|------|-----|------|
| OOM_SCORE_ADJ_MIN | -1000 | 禁止被 OOM Killer 杀死 |
| OOM_SCORE_ADJ_MAX | 1000 | 最大 OOM 评分调整值 |

---

## 3. out_of_memory 主函数和触发流程

### 3.1 函数签名

**位置**: `mm/oom_kill.c` (第 1119-1188 行)

```c
bool out_of_memory(struct oom_control *oc)
```

### 3.2 完整触发流程

```
__alloc_pages() (mm/page_alloc.c)
    ↓
alloc_pages_bulk_array() → 页面分配失败
    ↓
__alloc_pages_slowpath() (mm/page_alloc.c)
    ↓
out_of_memory() (mm/oom_kill.c)  ← 主入口
```

### 3.3 out_of_memory 详细逻辑 (第 1119-1188 行)

```c
bool out_of_memory(struct oom_control *oc)
{
    unsigned long freed = 0;

    // 1. 检查 OOM killer 是否被禁用
    if (oom_killer_disabled)
        return false;

    // 2. 通知链回调,允许其他模块释放内存
    if (!is_memcg_oom(oc)) {
        blocking_notifier_call_chain(&oom_notify_list, 0, &freed);
        if (freed > 0 && !is_sysrq_oom(oc))
            return true;  // 有其他模块释放了内存
    }

    // 3. 如果 current 即将退出,直接标记为 victim
    if (task_will_free_mem(current)) {
        mark_oom_victim(current);
        queue_oom_reaper(current);
        return true;
    }

    // 4. 如果不允许执行文件系统操作且非 memcg OOM,则返回
    if (!(oc->gfp_mask & __GFP_FS) && !is_memcg_oom(oc))
        return true;

    // 5. 确定约束类型并设置 totalpages
    oc->constraint = constrained_alloc(oc);
    if (oc->constraint != CONSTRAINT_MEMORY_POLICY)
        oc->nodemask = NULL;

    // 6. 检查是否需要 panic
    check_panic_on_oom(oc);

    // 7. 可选:杀死当前分配内存的进程
    if (!is_memcg_oom(oc) && sysctl_oom_kill_allocating_task &&
        current->mm && !oom_unkillable_task(current) &&
        oom_cpuset_eligible(current, oc) &&
        current->signal->oom_score_adj != OOM_SCORE_ADJ_MIN) {
        oc->chosen = current;
        oom_kill_process(oc, "Out of memory (oom_kill_allocating_task)");
        return true;
    }

    // 8. 选择最差进程
    select_bad_process(oc);

    // 9. 如果没有找到可杀死的进程
    if (!oc->chosen) {
        dump_header(oc);
        pr_warn("Out of memory and no killable processes...\n");
        if (!is_sysrq_oom(oc) && !is_memcg_oom(oc))
            panic("System is deadlocked on memory\n");
    }

    // 10. 杀死选中的进程
    if (oc->chosen && oc->chosen != (void *)-1UL)
        oom_kill_process(oc, !is_memcg_oom(oc) ? "Out of memory" :
                 "Memory cgroup out of memory");
    return !!oc->chosen;
}
```

---

## 4. select_bad_process 选择最差进程

**位置**: `mm/oom_kill.c` (第 365-380 行)

### 4.1 select_bad_process 函数

```c
static void select_bad_process(struct oom_control *oc)
{
    oc->chosen_points = LONG_MIN;

    // 根据是 memcg OOM 还是全局 OOM,选择不同的扫描方式
    if (is_memcg_oom(oc))
        mem_cgroup_scan_tasks(oc->memcg, oom_evaluate_task, oc);
    else {
        struct task_struct *p;

        rcu_read_lock();
        // 遍历所有进程,调用 oom_evaluate_task 评估
        for_each_process(p)
            if (oom_evaluate_task(p, oc))
                break;
        rcu_read_unlock();
    }
}
```

### 4.2 oom_evaluate_task 评估函数 (第 309-359 行)

```c
static int oom_evaluate_task(struct task_struct *task, void *arg)
{
    struct oom_control *oc = arg;
    long points;

    // 1. 跳过不可杀死的进程 (init, kernel threads)
    if (oom_unkillable_task(task))
        goto next;

    // 2. 检查 cpuset/mempolicy 限制
    if (!is_memcg_oom(oc) && !oom_cpuset_eligible(task, oc))
        goto next;

    // 3. 如果是 OOM victim,检查是否是 MMF_OOM_SKIP
    if (!is_sysrq_oom(oc) && tsk_is_oom_victim(task)) {
        if (mm_flags_test(MMF_OOM_SKIP, task->signal->oom_mm))
            goto next;
        goto abort;
    }

    // 4. 如果进程标记为 oom_task_origin,直接选中
    if (oom_task_origin(task)) {
        points = LONG_MAX;
        goto select;
    }

    // 5. 计算进程的 oom_badness 评分
    points = oom_badness(task, oc->totalpages);
    if (points == LONG_MIN || points < oc->chosen_points)
        goto next;

select:
    // 6. 选择该进程作为候选
    if (oc->chosen)
        put_task_struct(oc->chosen);
    get_task_struct(task);
    oc->chosen = task;
    oc->chosen_points = points;
next:
    return 0;
abort:
    // 扫描中止
    if (oc->chosen)
        put_task_struct(oc->chosen);
    oc->chosen = (void *)-1UL;
    return 1;
}
```

---

## 5. oom_badness 评分算法

**位置**: `mm/oom_kill.c` (第 202-240 行)

### 5.1 评分公式

```
points = (RSS + Swap + PageTables) + oom_score_adj * (totalpages / 1000)
```

### 5.2 oom_badness 函数详解

```c
long oom_badness(struct task_struct *p, unsigned long totalpages)
{
    long points;
    long adj;

    // 1. 不可杀进程检查
    if (oom_unkillable_task(p))
        return LONG_MIN;

    p = find_lock_task_mm(p);
    if (!p)
        return LONG_MIN;

    // 2. 检查 oom_score_adj 和特殊标记
    adj = (long)p->signal->oom_score_adj;
    if (adj == OOM_SCORE_ADJ_MIN ||          // -1000: 禁止杀死
            mm_flags_test(MMF_OOM_SKIP, p->mm) ||  // 已跳过
            in_vfork(p)) {                   // vfork 中
        task_unlock(p);
        return LONG_MIN;
    }

    // 3. 计算内存消耗 points
    //    RSS: 驻留内存页数
    //    MM_SWAPENTS: 交换条目数
    //    PageTables: 页表占用的内存
    points = get_mm_rss_sum(p->mm) + get_mm_counter_sum(p->mm, MM_SWAPENTS) +
        mm_pgtables_bytes(p->mm) / PAGE_SIZE;
    task_unlock(p);

    // 4. 将 oom_score_adj 转换为 points
    //    adj 范围 [-1000, 1000], 乘以 totalpages/1000
    adj *= totalpages / 1000;
    points += adj;

    return points;
}
```

### 5.3 内存消耗组件详解

| 组件 | 获取函数 | 说明 |
|------|----------|------|
| RSS | `get_mm_rss_sum(p->mm)` | 驻留内存页数 (Anonymous + File + Shmem) |
| Swap | `get_mm_counter_sum(p->mm, MM_SWAPENTS)` | 已使用的交换空间条目数 |
| PageTables | `mm_pgtables_bytes(p->mm) / PAGE_SIZE` | 页表占用的内存页数 |

### 5.4 评分示例

假设 totalpages = 100000 (约 400MB):

| 进程类型 | RSS | Swap | PageTables | oom_score_adj | 最终 points |
|----------|-----|------|------------|---------------|-------------|
| 普通进程 | 5000 | 100 | 50 | 0 | 5150 |
| 高优先级 | 5000 | 100 | 50 | 500 | 5150 + 50000 = 55150 |
| 受保护 | 5000 | 100 | 50 | -1000 | 5150 - 100000 = -94850 (不可杀) |

---

## 6. oom_kill_process 杀进程流程

**位置**: `mm/oom_kill.c` (第 1024-1070 行)

### 6.1 oom_kill_process 函数

```c
static void oom_kill_process(struct oom_control *oc, const char *message)
{
    struct task_struct *victim = oc->chosen;
    struct mem_cgroup *oom_group;

    // 1. 如果 victim 即将释放内存,只标记为 victim 并排队 OOM Reaper
    task_lock(victim);
    if (task_will_free_mem(victim)) {
        mark_oom_victim(victim);
        queue_oom_reaper(victim);
        task_unlock(victim);
        put_task_struct(victim);
        return;
    }
    task_unlock(victim);

    // 2. 打印 OOM 信息
    if (__ratelimit(&oom_rs)) {
        dump_header(oc);
        dump_oom_victim(oc, victim);
    }

    // 3. 获取 victim 所属的 memcg OOM 组
    oom_group = mem_cgroup_get_oom_group(victim, oc->memcg);

    // 4. 执行实际的杀死操作
    __oom_kill_process(victim, message);

    // 5. 如果需要,杀死整个 memcg OOM 组中的所有进程
    if (oom_group) {
        memcg_memory_event(oom_group, MEMCG_OOM_GROUP_KILL);
        mem_cgroup_print_oom_group(oom_group);
        mem_cgroup_scan_tasks(oom_group, oom_kill_memcg_member, (void *)message);
        mem_cgroup_put(oom_group);
    }
}
```

### 6.2 __oom_kill_process 核心杀死逻辑 (第 928-1008 行)

```c
static void __oom_kill_process(struct task_struct *victim, const char *message)
{
    struct task_struct *p;
    struct mm_struct *mm;
    bool can_oom_reap = true;

    // 1. 获取 victim 的 task_struct 并锁定其 mm
    p = find_lock_task_mm(victim);
    if (!p) {
        // victim 正在退出
        put_task_struct(victim);
        return;
    }

    // 2. 获取 mm 引用
    mm = victim->mm;
    mmgrab(mm);

    // 3. 统计事件
    count_vm_event(OOM_KILL);
    memcg_memory_event_mm(mm, MEMCG_OOM_KILL);

    // 4. 发送 SIGKILL 信号
    do_send_sig_info(SIGKILL, SEND_SIG_PRIV, victim, PIDTYPE_TGID);

    // 5. 标记为 OOM victim
    mark_oom_victim(victim);

    // 6. 打印详细信息
    pr_err("... Killed process %d (%s) total-vm:%lukB, ... oom_score_adj:%d\n", ...);

    // 7. 杀死所有共享该 mm 的其他线程组
    rcu_read_lock();
    for_each_process(p) {
        if (!process_shares_mm(p, mm))      // 不共享该 mm
            continue;
        if (same_thread_group(p, victim))   // 同一线程组
            continue;
        if (is_global_init(p)) {            // init 进程
            can_oom_reap = false;
            mm_flags_set(MMF_OOM_SKIP, mm);
            continue;
        }
        if (p->flags & PF_KTHREAD)         // 内核线程
            continue;
        do_send_sig_info(SIGKILL, SEND_SIG_PRIV, p, PIDTYPE_TGID);
    }
    rcu_read_unlock();

    // 8. 排队 OOM Reaper 异步回收
    if (can_oom_reap)
        queue_oom_reaper(victim);

    mmdrop(mm);
    put_task_struct(victim);
}
```

### 6.3 task_will_free_mem 检查 (第 881-926 行)

```c
static bool task_will_free_mem(struct task_struct *task)
{
    struct mm_struct *mm = task->mm;
    struct task_struct *p;
    bool ret = true;

    if (!mm)
        return false;

    // 检查 coredumping, exit, thread group empty 等状态
    if (!__task_will_free_mem(task))
        return false;

    // 检查是否已被 OOM Reaper 跳过
    if (mm_flags_test(MMF_OOM_SKIP, mm))
        return false;

    // 检查 mm_users 数量
    if (atomic_read(&mm->mm_users) <= 1)
        return true;

    // 检查所有共享该 mm 的进程是否都在退出
    rcu_read_lock();
    for_each_process(p) {
        if (!process_shares_mm(p, mm))
            continue;
        if (same_thread_group(task, p))
            continue;
        ret = __task_will_free_mem(p);
        if (!ret)
            break;
    }
    rcu_read_unlock();

    return ret;
}
```

---

## 7. oom_score_adj 机制

### 7.1 概述

`oom_score_adj` 是用户空间调整进程 OOM 评分的重要接口,范围 [-1000, 1000]:

- **-1000**: 完全禁止被 OOM Killer 杀死
- **0**: 默认值
- **正数**: 增加被杀死的机会
- **1000**: 最大权重

### 7.2 oom_score_adj 在评分中的应用

**位置**: `mm/oom_kill.c` (第 236-237 行)

```c
adj = (long)p->signal->oom_score_adj;
// adj 范围 [-1000, 1000]
adj *= totalpages / 1000;  // 归一化到 totalpages
points += adj;
```

### 7.3 oom_score_adj 写入接口

用户空间可通过以下接口修改:
- `/proc/<pid>/oom_score_adj` - 推荐使用 (范围 -1000 到 1000)
- `/proc/<pid>/oom_adj` - 传统接口 (范围 -16 到 15, -17 表示 OOM_DISABLE)

### 7.4 oom_unkillable_task 检查 (第 163-170 行)

```c
static bool oom_unkillable_task(struct task_struct *p)
{
    if (is_global_init(p))    // PID 1 的 init 进程
        return true;
    if (p->flags & PF_KTHREAD)  // 内核线程
        return true;
    return false;
}
```

### 7.5 MMF_OOM_SKIP 标记

**位置**: `include/linux/mm_types.h` (第 1894 行)

```c
#define MMF_OOM_SKIP  21  // mm is of no interest for the OOM killer
```

在以下情况设置:
- `exit_mmap()` 中 (进程退出时)
- `__oom_kill_process()` 中 (当 init 进程持有该 mm 时)
- `oom_reap_task()` 中 (OOM Reaper 完成或无法回收时)

---

## 8. memcg OOM 处理

### 8.1 memcg OOM 触发流程

```
mem_cgroup_charge() (mm/memcontrol.c)
    ↓
try_charge() → nr_retries 耗尽
    ↓
mem_cgroup_oom() (mm/memcontrol.c 第 1706-1723 行)
    ↓
mem_cgroup_out_of_memory() (mm/memcontrol.c)
    ↓
out_of_memory() (mm/oom_kill.c)
```

### 8.2 mem_cgroup_oom 函数 (mm/memcontrol.c 第 1706-1723 行)

```c
static bool mem_cgroup_oom(struct mem_cgroup *memcg, gfp_t mask, int order)
{
    bool locked, ret;

    // order 太大时不触发 OOM killer
    if (order > PAGE_ALLOC_COSTLY_ORDER)
        return false;

    memcg_memory_event(memcg, MEMCG_OOM);

    // 准备 OOM:锁定层级中的所有 memcg
    if (!memcg1_oom_prepare(memcg, &locked))
        return false;

    ret = mem_cgroup_out_of_memory(memcg, mask, order);

    memcg1_oom_finish(memcg, locked);

    return ret;
}
```

### 8.3 memcg OOM vs 全局 OOM 的区别

| 特性 | 全局 OOM | memcg OOM |
|------|----------|-----------|
| memcg 参数 | `oc->memcg = NULL` | `oc->memcg = 指向特定 cgroup` |
| 进程扫描范围 | 所有进程 | 只扫描属于该 memcg 的进程 |
| totalpages | `totalram_pages() + total_swap_pages` | `mem_cgroup_get_max(memcg)` |
| 约束类型 | CONSTRAINT_NONE/CPUSET/MEMPOLICY | CONSTRAINT_MEMCG |
| OOM 组 kill | 不支持 | 支持 (MEMCG_OOM_GROUP_KILL) |

### 8.4 mem_cgroup_get_oom_group (mm/memcontrol.c 第 1726 行起)

获取需要一起杀死的 memcg 组,用于 OOM_GROUP_KILL 特性。

---

## 9. OOM Reaper 异步回收

### 9.1 概述

OOM Reaper 是一个内核线程 (`oom_reaper`),专门负责异步回收 OOM victim 的内存,避免等待进程自然退出导致的长时间阻塞。

### 9.2 OOM Reaper 线程启动 (第 650-670 行)

```c
static int oom_reaper(void *unused)
{
    set_freezable();

    while (true) {
        struct task_struct *tsk = NULL;

        // 等待唤醒
        wait_event_freezable(oom_reaper_wait, oom_reaper_list != NULL);
        spin_lock_irq(&oom_reaper_lock);
        if (oom_reaper_list != NULL) {
            tsk = oom_reaper_list;
            oom_reaper_list = tsk->oom_reaper_list;
        }
        spin_unlock_irq(&oom_reaper_lock);

        if (tsk)
            oom_reap_task(tsk);  // 执行回收
    }

    return 0;
}
```

### 9.3 排队 OOM Reaper (第 702-712 行)

```c
#define OOM_REAPER_DELAY (2*HZ)  // 2 秒延迟

static void queue_oom_reaper(struct task_struct *tsk)
{
    // 检查是否已经排队
    if (mm_flags_test_and_set(MMF_OOM_REAP_QUEUED, tsk->signal->oom_mm))
        return;

    get_task_struct(tsk);
    timer_setup(&tsk->oom_reaper_timer, wake_oom_reaper, 0);
    tsk->oom_reaper_timer.expires = jiffies + OOM_REAPER_DELAY;
    add_timer(&tsk->oom_reaper_timer);
}
```

### 9.4 回收任务内存 (__oom_reap_task_mm, 第 516-570 行)

```c
static bool __oom_reap_task_mm(struct mm_struct *mm)
{
    struct vm_area_struct *vma;
    bool ret = true;
    MA_STATE(mas, &mm->mm_mt, ULONG_MAX, ULONG_MAX);

    // 1. 标记 mm 为不稳定
    mm_flags_set(MMF_UNSTABLE, mm);

    // 2. 遍历所有 VMA
    mas_for_each_rev(&mas, vma, 0) {
        // 跳过 hugepage 和 PFNMAP
        if (vma->vm_flags & (VM_HUGETLB|VM_PFNMAP))
            continue;

        // 只回收 anonymous 和非共享的 file-backed 页面
        if (vma_is_anonymous(vma) || !(vma->vm_flags & VM_SHARED)) {
            // 通知 mmu_notifier 并解除映射
            mmu_notifier_range_init(...);
            tlb_gather_mmu(&tlb, mm);
            unmap_page_range(&tlb, vma, range.start, range.end, NULL);
            tlb_finish_mmu(&tlb);
        }
    }

    return ret;
}
```

### 9.5 OOM Reaper 工作流程图

```
queue_oom_reaper()
    ↓
设置 MMF_OOM_REAP_QUEUED 标志
启动定时器 (2秒后触发)
    ↓
wake_oom_reaper() [定时器到期]
    ↓
加入 oom_reaper_list 链表
唤醒 oom_reaper 线程
    ↓
oom_reap_task()
    ↓
尝试获取 mmap_read_lock
    ↓
失败? → 重试 10 次 (间隔 100ms)
    ↓
成功 → 调用 __oom_reap_task_mm()
    ↓
设置 MMF_OOM_SKIP 标志
```

释放引用

---

## 10. 不可杀进程检查

### 10.1 oom_unkillable_task (第 163-170 行)

```c
static bool oom_unkillable_task(struct task_struct *p)
{
    if (is_global_init(p))        // PID 1
        return true;
    if (p->flags & PF_KTHREAD)   // 内核线程
        return true;
    return false;
}
```

### 10.2 其他跳过条件

除了 `oom_unkillable_task` 返回 true 的进程外,以下进程也会被跳过:

| 条件 | 位置 | 说明 |
|------|------|------|
| `oom_score_adj == OOM_SCORE_ADJ_MIN` | oom_badness (第 220 行) | 通过 `/proc` 标记为不可杀死 |
| `MMF_OOM_SKIP` | oom_evaluate_task (第 328 行) | 已完成回收或被跳过 |
| `in_vfork(p)` | oom_badness (第 222 行) | 正在 vfork |
| `is_global_init(p)` | __oom_kill_process (第 985 行) | init 进程持有 mm |
| `PF_KTHREAD` | __oom_kill_process (第 997 行) | 内核线程使用该 mm |

### 10.3 init 进程的特殊处理

init 进程 (PID 1) 是系统最关键的进程,即使在极端情况下也不会被直接杀死。但如果 init 进程持有一个 OOM victim 的 mm,会导致 `can_oom_reap = false`,跳过异步回收。

---

## 11. OOM Killer 完整流程图

```
+-----------------+
| __alloc_pages() |
| (页面分配失败)   |
+--------+--------+
         |
         v
+-----------------+
| out_of_memory() |  ← 主入口
+--------+--------+  mm/oom_kill.c:1119
         |
         +---> OOM Killer 已禁用? --是--> return false
         |
         +---> 通知链有内存释放? --是--> return true
         |
         +---> current 即将退出? --是--> mark_oom_victim() + queue_oom_reaper()
         |
         +---> !__GFP_FS && !memcg? --是--> return true
         |
         v
+-----------------+
| constrained_alloc() |  确定约束类型
+--------+--------+
         |
         v
+-----------------+
| check_panic_on_oom() |  检查是否需要 panic
+--------+--------+
         |
         v
+-----------------+
| sysctl_oom_kill_allocating_task? |
+--------+--------+
         |
    是   |   否
    v    |    v
杀死 current  |  select_bad_process()
         |         |
         |         v
         |  +-------------------+
         |  | memcg OOM?       |
         |  +-------------------+
         |       |
         |   是  |   否
         |    v  |   v
         |  mem_cgroup_  for_each_process()
         |  scan_tasks()  遍历所有进程
         |       |          |
         |       v          v
         |  oom_evaluate_task() 评估每个进程
         |       |
         |       +---> oom_unkillable_task()?
         |       |          |
         |       |     是   |   否
         |       |      v   |   v
         |       |    skip  | oom_badness()
         |       |          |     |
         |       |          |     +---> adj == OOM_SCORE_ADJ_MIN? --> LONG_MIN
         |       |          |     |
         |       |          |     +---> 计算 points = RSS + Swap + PageTables
         |       |          |     |
         |       |          |     +---> points += adj * totalpages / 1000
         |       |          |     |
         |       |          v     v
         |       +-----> 选择最高 points 的进程
         |                  |
         v                  v
+-----------------+  +------------------+
| oom_kill_process()|  | 没有可杀进程?    |
+--------+--------+  +------------------+
         |                   |
         v                   v
+-----------------+      panic()
| __oom_kill_process()|
+--------+--------+
         |
         +---> 发送 SIGKILL 给 victim
         |
         +---> mark_oom_victim() 标记为 OOM victim
         |
         +---> 杀死所有共享 mm 的其他线程组
         |
         +---> queue_oom_reaper() 排队异步回收
         |
         v
+------------------+
| memcg OOM_GROUP? |  --是--> 杀死整个组的进程
+--------+---------+
         |
         v
```

完成

---

## 12. 关键源码位置汇总

### 12.1 核心文件

| 文件 | 说明 |
|------|------|
| `mm/oom_kill.c` | OOM Killer 核心实现 |
| `include/linux/oom.h` | OOM Killer 核心数据结构 |
| `include/uapi/linux/oom.h` | 用户空间接口定义 |
| `mm/memcontrol.c` | memcg OOM 处理 |
| `mm/page_alloc.c` | OOM 触发入口 |

### 12.2 关键函数位置

| 函数 | 文件:行号 | 说明 |
|------|----------|------|
| `out_of_memory()` | mm/oom_kill.c:1119 | OOM Killer 主入口 |
| `select_bad_process()` | mm/oom_kill.c:365 | 选择最差进程 |
| `oom_evaluate_task()` | mm/oom_kill.c:309 | 评估单个进程 |
| `oom_badness()` | mm/oom_kill.c:202 | 计算进程 OOM 评分 |
| `oom_kill_process()` | mm/oom_kill.c:1024 | 杀死进程主函数 |
| `__oom_kill_process()` | mm/oom_kill.c:928 | 实际杀死进程 |
| `mark_oom_victim()` | mm/oom_kill.c:767 | 标记为 OOM victim |
| `oom_unkillable_task()` | mm/oom_kill.c:163 | 检查是否不可杀 |
| `task_will_free_mem()` | mm/oom_kill.c:881 | 检查是否将释放内存 |
| `queue_oom_reaper()` | mm/oom_kill.c:702 | 排队 OOM Reaper |
| `oom_reap_task_mm()` | mm/oom_kill.c:578 | OOM Reaper 回收 mm |
| `__oom_reap_task_mm()` | mm/oom_kill.c:516 | 实际执行内存回收 |
| `oom_reaper()` | mm/oom_kill.c:650 | OOM Reaper 线程 |
| `constrained_alloc()` | mm/oom_kill.c:252 | 确定约束类型 |
| `check_panic_on_oom()` | mm/oom_kill.c:1075 | 检查是否 panic |
| `mem_cgroup_oom()` | mm/memcontrol.c:1706 | memcg OOM 入口 |
| `mem_cgroup_out_of_memory()` | mm/memcontrol.c:1686 | memcg OOM 处理 |
| `find_lock_task_mm()` | mm/oom_kill.c:134 | 查找持有 mm 的任务 |

### 12.3 关键标志位

| 标志 | 文件:行号 | 说明 |
|------|----------|------|
| `MMF_OOM_SKIP` | include/linux/mm_types.h:1894 | mm 对 OOM Killer 不感兴趣 |
| `MMF_UNSTABLE` | include/linux/mm_types.h:1895 | mm 不稳定 (OOM Reaper 正在回收) |
| `MMF_OOM_REAP_QUEUED` | include/linux/mm_types.h:1900 | mm 已排队等待 OOM Reaper |

### 12.4 sysctl 参数

| 参数 | 位置 | 说明 |
|------|------|------|
| `panic_on_oom` | mm/oom_kill.c:56 | OOM 时是否 panic |
| `oom_kill_allocating_task` | mm/oom_kill.c:57 | 是否杀死当前分配进程 |
| `oom_dump_tasks` | mm/oom_kill.c:58 | 是否导出任务信息 |

---

## 参考

- Linux Kernel Source: `mm/oom_kill.c`, `include/linux/oom.h`
- Documentation: `Documentation/admin-guide/mm/oom_dumper.rst`
