# Linux RCU 子系统深度分析 R2

## 目录
1. [RCU 原理](#1-rcu-原理)
2. [Tree RCU 数据结构](#2-tree-rcu-数据结构)
3. [SRCU 实现](#3-srcu-实现)
4. [Sched RCU](#4-sched-rcu)
5. [rcu_barrier 全局同步](#5-rcu_barrier-全局同步)
6. [性能调优](#6-性能调优)
7. [知识点关联表格](#7-知识点关联表格)

---

## 1. RCU 原理

### 1.1 宽限期 (Grace Period) 检测算法

RCU 的核心是**宽限期检测算法**，通过 `gp_seq` 序列号追踪 grace period 的状态。

**关键源码**: `kernel/rcu/tree.c:1804-1998`

```c
// tree.c:1804 - 宽限期初始化
static noinline_for_stack bool rcu_gp_init(void)
{
    struct rcu_node *rnp = rcu_get_root();
    
    // 1. 设置 gp_seq 开始标志
    rcu_seq_start(&rcu_state.gp_seq);  // tree.c:1853
    
    // 2. 初始化所有 rcu_node 的 qsmask
    rcu_for_each_node_breadth_first(rnp) {  // tree.c:1954
        rnp->qsmask = rnp->qsmaskinit;  // tree.c:1959
        WRITE_ONCE(rnp->gp_seq, rcu_state.gp_seq);  // tree.c:1960
    }
}
```

**宽限期完成的判定条件** (`tree.c:2018-2019`):
```c
if (!READ_ONCE(rnp->qsmask) && !rcu_preempt_blocked_readers_cgp(rnp))
    return true;  // 宽限期完成
```

### 1.2 Quiescent State (静止状态)

Quiescent State 是 CPU 不处于 RCU 读临界区的状态。RCU 通过以下机制检测:

**核心函数**: `rcu_qs()` (`tree_plugin.h:298-309`)
```c
static void rcu_qs(void)
{
    if (__this_cpu_read(rcu_data.cpu_no_qs.b.norm)) {
        __this_cpu_write(rcu_data.cpu_no_qs.b.norm, false);  // 清除QS标志
        barrier();
        WRITE_ONCE(current->rcu_read_unlock_special.b.need_qs, false);
    }
}
```

**上下文切换时报告QS** (`tree_plugin.h:324-373`):
```c
void rcu_note_context_switch(bool preempt)
{
    struct rcu_data *rdp = this_cpu_ptr(&rcu_data);
    
    if (rcu_preempt_depth() > 0 && !t->rcu_read_unlock_special.b.blocked) {
        // 任务在RCU读临界区中被阻塞
        rcu_preempt_ctxt_queue(rnp, rdp);  // 加入阻塞队列
    }
    rcu_qs();  // 报告静止状态
}
```

### 1.3 写者延迟删除机制

RCU 的写者通过 `call_rcu()` 延迟回调的执行:

**核心源码**: `tree.c:3102-3157`
```c
static void __call_rcu_common(struct rcu_head *head, rcu_callback_t func, bool lazy_in)
{
    // 1. 添加回调到本地CPU的cblist
    if (unlikely(rcu_rdp_is_offloaded(rdp)))
        call_rcu_nocb(rdp, head, func, flags, lazy);  // NOCB模式
    else
        call_rcu_core(rdp, head, func, flags);  // 普通模式
}
```

**宽限期结束后批量执行回调** (`tree.c:2540-2598`):
```c
static void rcu_do_batch(struct rcu_data *rdp)
{
    // 提取已完成的回调
    rcu_segcblist_extract_done_cbs(&rdp->cblist, &rcl);
    
    // 执行回调
    while ((rhp = rcu_cblist_dequeue(&rcl))) {
        debug_rcu_head_unqueue(rhp);
        trace_rcu_invoke_callback(rcu_state.name, rhp);
        rhp->func(rhp);
    }
}
```

---

## 2. Tree RCU 数据结构

### 2.1 rcu_node 层次结构

**核心数据结构**: `tree.h:41-139`
```c
struct rcu_node {
    raw_spinlock_t __private lock;
    unsigned long gp_seq;           // 宽限期序列号
    unsigned long gp_seq_needed;    // 等待的下一个GP序列号
    unsigned long qsmask;           // 需要报告QS的CPU掩码
    unsigned long qsmaskinit;      // 初始qsmask值
    unsigned long expmask;          // 加速GP的CPU掩码
    
    struct list_head blkd_tasks;   // 阻塞的任务链表
    struct list_head *gp_tasks;    // 阻塞当前GP的任务
    struct list_head *exp_tasks;   // 阻塞当前加速GP的任务
    
    struct rcu_node *parent;       // 父节点
    int grplo, grphi;              // 管理的CPU范围
    u8 level;                      // 在树中的层级(0=根)
    
#ifdef CONFIG_RCU_NOCB_CPU
    struct swait_queue_head nocb_gp_wq[2];  // NOCB等待队列
#endif
};
```

### 2.2 rcu_state 全局状态

**核心源码**: `tree.h:351-438`
```c
struct rcu_state {
    struct rcu_node node[NUM_RCU_NODES];   // 层次结构的节点数组
    struct rcu_node *level[RCU_NUM_LVLS + 1];  // 每层起始指针
    
    unsigned long gp_seq;                  // 当前GP序列号
    struct task_struct *gp_kthread;        // GP管理线程
    struct swait_queue_head gp_wq;         // GP等待队列
    
    short gp_flags;                        // GP命令标志
    short gp_state;                        // GP状态机
    
    // rcu_barrier 相关
    struct mutex barrier_mutex;
    atomic_t barrier_cpu_count;
    struct completion barrier_completion;
    
    // 加速GP相关
    struct mutex exp_mutex;
    atomic_t expedited_need_qs;
};
```

### 2.3 rcu_data per-CPU 结构

**核心源码**: `tree.h:189-297`
```c
struct rcu_data {
    // 宽限期和QS处理
    unsigned long gp_seq;                  // 本地GP序列号跟踪
    unsigned long gp_seq_needed;           // 需要的GP序列号
    union rcu_noqs cpu_no_qs;             // CPU未报告QS标志
    bool core_needs_qs;                   // 核心等待QS
    
    // 回调链表
    struct rcu_segcblist cblist;          // 分段回调链表
    
    // NOCB支持
#ifdef CONFIG_RCU_NOCB_CPU
    struct swait_queue_head nocb_cb_wq;   // CB线程等待队列
    struct task_struct *nocb_gp_kthread;  // GP kthread
    struct task_struct *nocb_cb_kthread;  // CB kthread
    raw_spinlock_t nocb_lock;
    struct rcu_cblist nocb_bypass;        // 绕过队列
#endif
    
    struct rcu_node *mynode;              // 本地叶子节点
    int cpu;
};
```

### 2.4 Wakeup 机制

**NOCB唤醒**: `tree_nocb.h:202-241`
```c
static bool __wake_nocb_gp(struct rcu_data *rdp_gp, struct rcu_data *rdp,
                           unsigned long flags)
{
    bool needwake = false;
    
    nocb_defer_wakeup_cancel(rdp_gp);
    
    if (READ_ONCE(rdp_gp->nocb_gp_sleep)) {
        WRITE_ONCE(rdp_gp->nocb_gp_sleep, false);
        needwake = true;
    }
    raw_spin_unlock_irqrestore(&rdp_gp->nocb_gp_lock, flags);
    if (needwake)
        swake_up_one(&rdp_gp->nocb_gp_wq);  // 唤醒GP线程
    
    return needwake;
}
```

---

## 3. SRCU 实现

### 3.1 srcu_struct 结构

**核心源码**: `srcutree.c:89-112`
```c
static void init_srcu_struct_data(struct srcu_struct *ssp)
{
    for_each_possible_cpu(cpu) {
        sdp = per_cpu_ptr(ssp->sda, cpu);
        raw_spin_lock_init(&ACCESS_PRIVATE(sdp, lock));
        rcu_segcblist_init(&sdp->srcu_cblist);
        sdp->srcu_gp_seq_needed = ssp->srcu_sup->srcu_gp_seq;
        sdp->srcu_gp_seq_needed_exp = ssp->srcu_sup->srcu_gp_seq;
    }
}
```

### 3.2 srcu_read_lock/unlock 实现

**核心源码**: `srcutree.c:790-810`
```c
int __srcu_read_lock(struct srcu_struct *ssp)
{
    struct srcu_ctr __percpu *scp = READ_ONCE(ssp->srcu_ctrp);
    
    this_cpu_inc(scp->srcu_locks.counter);  // 增加当前索引的锁计数
    smp_mb(); /* B */  // 内存屏障防止泄漏临界区
    return __srcu_ptr_to_ctr(ssp, scp);
}

void __srcu_read_unlock(struct srcu_struct *ssp, int idx)
{
    smp_mb(); /* C */  // 内存屏障防止泄漏临界区
    this_cpu_inc(__srcu_ctr_to_ptr(ssp, idx)->srcu_unlocks.counter);
}
```

### 3.3 synchronize_srcu 链表操作

**核心源码**: `srcutree.c:1477-1498`
```c
static void __synchronize_srcu(struct srcu_struct *ssp, bool do_norm)
{
    struct rcu_synchronize rcu;
    
    srcu_lock_sync(&ssp->dep_map);  // 锁依赖检查
    
    if (rcu_scheduler_active == RCU_SCHEDULER_INACTIVE)
        return;
    might_sleep();
    check_init_srcu_struct(ssp);
    
    init_completion(&rcu.completion);
    init_rcu_head_on_stack(&rcu.head);
    
    // 排队回调并等待
    __call_srcu(ssp, &rcu.head, wakeme_after_rcu, do_norm);
    wait_for_completion(&rcu.completion);
    destroy_rcu_head_on_stack(&rcu.head);
}
```

**SRCU宽限期检测**: `srcutree.c:916-977`
```c
static void srcu_gp_end(struct srcu_struct *ssp)
{
    // 结束当前GP
    rcu_seq_end(&sup->srcu_gp_seq);
    
    // 遍历srcu_node树，触发回调
    srcu_for_each_node_breadth_first(ssp, snp) {
        cbs = (snp->srcu_have_cbs[idx] == gpseq);
        if (cbs)
            srcu_schedule_cbs_snp(ssp, snp, mask, cbdelay);
    }
    
    // 启动新GP如果需要
    if (!rcu_seq_state(gpseq) && ULONG_CMP_LT(gpseq, sup->srcu_gp_seq_needed))
        srcu_gp_start(ssp);
}
```

---

## 4. Sched RCU

### 4.1 synchronize_sched 区别

**Sched RCU** 专门用于调度器相关的RCU，确保所有抢占禁用区域和调度临界区完成。

**核心区别**:
- `synchronize_rcu()`: 等待所有普通RCU读临界区完成
- `synchronize_sched()`: 等待包括调度器临界区在内的所有临界区完成

**实现位置**: 在 PREEMPT_RCU 配置下，`synchronize_sched()` 等同于 `synchronize_rcu()`；在非 PREEMPT 配置下，由于 `rcu_read_lock_sched()` 映射到 `preempt_disable()`，两者行为相同。

### 4.2 RCU vs Preemptible RCU

**非抢占式 RCU** (`CONFIG_TREE_RCU`):
- `rcu_read_lock()` → `preempt_disable()`
- 读临界区不允许调度

**可抢占式 RCU** (`CONFIG_PREEMPT_RCU`):
- `rcu_read_lock()` → 增加 `rcu_read_lock_nesting`
- 读临界区可以调度，但调度时会延迟 GP 完成

**被阻塞任务的处理**: `tree_plugin.h:162-279`
```c
static void rcu_preempt_ctxt_queue(struct rcu_node *rnp, struct rcu_data *rdp)
{
    // 根据阻塞状态决定加入链表头部还是尾部
    switch (blkd_state) {
    case 0:
    case RCU_EXP_TASKS:
        list_add(&t->rcu_node_entry, &rnp->blkd_tasks);  // 头部
        break;
    default:
        list_add_tail(&t->rcu_node_entry, &rnp->blkd_tasks);  // 尾部
        break;
    }
    
    // 更新gp_tasks指针
    if (!rnp->gp_tasks && (blkd_state & RCU_GP_BLKD))
        WRITE_ONCE(rnp->gp_tasks, &t->rcu_node_entry);
}
```

---

## 5. rcu_barrier 全局同步

### 5.1 全局同步点

**核心源码**: `tree.c:3817-3900`
```c
void rcu_barrier(void)
{
    unsigned long s = rcu_seq_snap(&rcu_state.barrier_sequence);
    
    mutex_lock(&rcu_state.barrier_mutex);
    
    if (rcu_seq_done(&rcu_state.barrier_sequence, s))
        return;  // 已经被其他barrier完成
    
    raw_spin_lock_irqsave(&rcu_state.barrier_lock, flags);
    rcu_seq_start(&rcu_state.barrier_sequence);
    gseq = rcu_state.barrier_sequence;
    
    init_completion(&rcu_state.barrier_completion);
    atomic_set(&rcu_state.barrier_cpu_count, 2);
    raw_spin_unlock_irqrestore(&rcu_state.barrier_lock, flags);
    
    // 对每个有回调的CPU发送SMP调用
    for_each_possible_cpu(cpu) {
        rdp = per_cpu_ptr(&rcu_data, cpu);
        if (!rcu_segcblist_n_cbs(&rdp->cblist))
            continue;  // 无回调，跳过
        if (!rcu_rdp_cpu_online(rdp)) {
            rcu_barrier_entrain(rdp);  // 离线CPU直接入队
            continue;
        }
        smp_call_function_single(cpu, rcu_barrier_handler, ...);  // 在线CPU
    }
    
    // 等待所有barrier回调完成
    wait_for_completion(&rcu_state.barrier_completion);
}
```

### 5.2 Callback 链遍历

**回调处理**: `tree.c:3738-3749`
```c
static void rcu_barrier_callback(struct rcu_head *rhp)
{
    unsigned long s = rcu_state.barrier_sequence;
    
    rhp->next = rhp;  // 标记已调用
    if (atomic_dec_and_test(&rcu_state.barrier_cpu_count)) {
        complete(&rcu_state.barrier_completion);  // 最后一个，唤醒
    }
}
```

---

## 6. 性能调优

### 6.1 rcutree.use_arch墙面

**源码位置**: `tree.c:434-451`
```c
static ulong jiffies_till_first_fqs = IS_ENABLED(CONFIG_RCU_STRICT_GRACE_PERIOD) ? 0 : ULONG_MAX;
static ulong jiffies_till_next_fqs = ULONG_MAX;

static void adjust_jiffies_till_sched_qs(void)
{
    unsigned long j;
    
    j = READ_ONCE(jiffies_till_first_fqs) + 2 * READ_ONCE(jiffies_till_next_fqs);
    if (j < HZ / 10 + nr_cpu_ids / RCU_JIFFIES_FQS_DIV)
        j = HZ / 10 + nr_cpu_ids / RCU_JIFFIES_FQS_DIV;
}
```

### 6.2 CONFIG_RCU_NOCB_CPU

**NOCB模式**: 将回调处理从原CPUoffload到专用kthread，减少原CPU的RCU开销。

**核心配置**: `tree_nocb.h:16-18`
```c
#ifdef CONFIG_RCU_NOCB_CPU
static cpumask_var_t rcu_nocb_mask;  // 要offload的CPU掩码
static bool __read_mostly rcu_nocb_poll;  // 是否使用轮询模式
#endif
```

**启动参数**:
- `rcu_nocbs=<cpu-list>`: 指定offload的CPU
- `rcu_nocb_poll`: 使用轮询而非wakeup

### 6.3 rcu_softirq

**核心源码**: `tree.c:262-271`
```c
void rcu_softirq_qs(void)
{
    RCU_LOCKDEP_WARN(lock_is_held(&rcu_bh_lock_map) ||
                     lock_is_held(&rcu_lock_map) ||
                     lock_is_held(&rcu_sched_lock_map),
                     "Illegal rcu_softirq_qs() in RCU read-side critical section");
    rcu_qs();
    rcu_preempt_deferred_qs(current);
    rcu_tasks_qs(current, false);
}
```

**Softirq处理迁移** (`tree.c:115-118`):
```c
#ifndef CONFIG_PREEMPT_RT
module_param(use_softirq, bool, 0444);
#endif

// 如果use_softirq=false，回调由rcuc kthread处理
static bool use_softirq = !IS_ENABLED(CONFIG_PREEMPT_RT);
```

---

## 7. 知识点关联表格

| 概念 | 源码位置 | 行号 | 关键数据结构/函数 |
|------|---------|------|------------------|
| **Grace Period 检测** | tree.c | 1804-1998 | `rcu_gp_init()`, `gp_seq` |
| **Quiescent State** | tree_plugin.h | 298-309 | `rcu_qs()`, `cpu_no_qs` |
| **rcu_node 层次结构** | tree.h | 41-139 | `struct rcu_node` |
| **rcu_state 全局状态** | tree.h | 351-438 | `struct rcu_state` |
| **rcu_data per-CPU** | tree.h | 189-297 | `struct rcu_data` |
| **NOCB 机制** | tree_nocb.h | 16-799 | `nocb_gp_wait()`, `nocb_cb_wait()` |
| **SRCU 读锁** | srcutree.c | 790-810 | `__srcu_read_lock()`, `srcu_locks` |
| **SRCU 同步** | srcutree.c | 1477-1498 | `__synchronize_srcu()` |
| **rcu_barrier** | tree.c | 3817-3900 | `rcu_barrier()`, `barrier_callback()` |
| **synchronize_rcu** | tree.c | 3349-3385 | `synchronize_rcu()` |
| **回调批量处理** | tree.c | 2540-2598 | `rcu_do_batch()` |
| **写者延迟删除** | tree.c | 3102-3157 | `__call_rcu_common()` |
| **Wakeup 机制** | tree_nocb.h | 202-241 | `__wake_nocb_gp()` |
| **优先级提升** | tree_plugin.h | 1154-1325 | `rcu_boost()`, `boost_kthread_task` |
| **加速 GP** | tree_exp.h | 20-152 | `sync_exp_reset_tree()` |
| **抢占式 RCU** | tree_plugin.h | 162-279 | `rcu_preempt_ctxt_queue()` |
| **FQS 强制QS** | tree.c | 2028-2059 | `rcu_gp_fqs()` |
| **Segmented CBLIST** | rcu_segcblist.h | - | `struct rcu_segcblist` |

---

## 附录: 关键算法流程图

### Grace Period 检测流程

```
call_rcu() → 排队回调 → 启动GP
                              ↓
                      rcu_gp_init()
                              ↓
                 ┌───────────────────────┐
                 │  初始化所有rcu_node    │
                 │  qsmask = qsmaskinit  │
                 └───────────────────────┘
                              ↓
                      rcu_gp_fqs_loop()
                 ┌───────────────────────┐
                 │  force_qs_rnp()       │
                 │  检查每个CPU的QS       │
                 └───────────────────────┘
                              ↓
                 ┌───────────────────────┐
                 │  rnp->qsmask == 0 ?   │
                 │  无阻塞读者 ?         │
                 └───────────────────────┘
                              ↓
                      rcu_gp_cleanup()
                              ↓
                 ┌───────────────────────┐
                 │  更新gp_seq           │
                 │  唤醒等待者           │
                 │  触发rcu_do_batch()  │
                 └───────────────────────┘
```

### SRCU 读锁/解锁流程

```
srcu_read_lock()
       ↓
  获取当前索引(idx = srcu_ctrp & 1)
       ↓
  this_cpu_inc(srcu_locks[idx])  // 增加锁计数
       ↓
  smp_mb()  // 内存屏障
       ↓
  返回idx

srcu_read_unlock(idx)
       ↓
  smp_mb()  // 内存屏障
       ↓
  this_cpu_inc(srcu_unlocks[idx])  // 增加解锁计数
```
