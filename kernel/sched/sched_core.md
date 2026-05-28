# Linux 内核调度器核心结构与函数分析

## 1. 核心文件概述

| 文件路径 | 主要内容 |
|---------|---------|
| `kernel/sched/core.c` | 调度器核心函数：schedule(), __schedule(), pick_next_task() |
| `kernel/sched/sched.h` | CFS 调度器数据结构：struct cfs_rq, struct rq |
| `include/linux/sched.h` | task_struct, sched_entity, sched_class 定义 |
| `kernel/sched/fair.c` | CFS 具体实现：pick_next_task_fair(), pick_eevdf() |

---

## 2. schedule() 主函数

**文件**: `kernel/sched/core.c:6998-7011`

```c
asmlinkage __visible void __sched schedule(void)
{
	struct task_struct *tsk = current;

#ifdef CONFIG_RT_MUTEXES
	lockdep_assert(!tsk->sched_rt_mutex);
#endif

	if (!task_is_running(tsk))
		sched_submit_work(tsk);
	__schedule_loop(SM_NONE);
	sched_update_worker(tsk);
}
```

### 调度流程

1. 获取当前任务 `current`
2. 如果当前任务不在运行状态，调用 `sched_submit_work()` 处理工作提交
3. 进入调度循环 `__schedule_loop(SM_NONE)`
4. 更新 worker 状态

**内部调度循环** (core.c:6989-6996):

```c
static __always_inline void __schedule_loop(int sched_mode)
{
	do {
		preempt_disable();
		__schedule(sched_mode);
		sched_preempt_enable_no_resched();
	} while (need_resched());
}
```

---

## 3. __schedule() 核心调度函数

**文件**: `kernel/sched/core.c:6764-6922`

```c
static void __sched notrace __schedule(int sched_mode)
{
	struct task_struct *prev, *next;
	bool preempt = sched_mode > SM_NONE;
	bool is_switch = false;
	unsigned long *switch_count;
	unsigned long prev_state;
	struct rq_flags rf;
	struct rq *rq;
	int cpu;

	cpu = smp_processor_id();
	rq = cpu_rq(cpu);
	prev = rq->curr;

	schedule_debug(prev, preempt);

	local_irq_disable();
	rcu_note_context_switch(preempt);
	migrate_disable_switch(rq, prev);

	rq_lock(rq, &rf);
	smp_mb__after_spinlock();

	update_rq_clock(rq);

	switch_count = &prev->nivcsw;
	preempt = sched_mode == SM_PREEMPT;

	prev_state = READ_ONCE(prev->__state);
	if (sched_mode == SM_IDLE) {
		if (!rq->nr_running && !scx_enabled()) {
			next = prev;
			rq->next_class = &idle_sched_class;
			goto picked;
		}
	} else if (!preempt && prev_state) {
		try_to_block_task(rq, prev, &prev_state,
				  !task_is_blocked(prev));
		switch_count = &prev->nvcsw;
	}

pick_again:
	next = pick_next_task(rq, rq->donor, &rf);
	rq_set_donor(rq, next);
	rq->next_class = next->sched_class;
	if (unlikely(task_is_blocked(next))) {
		next = find_proxy_task(rq, next, &rf);
		if (!next)
			goto pick_again;
		if (next == rq->idle)
			goto keep_resched;
	}
picked:
	clear_tsk_need_resched(prev);
	clear_preempt_need_resched();
keep_resched:
	rq->last_seen_need_resched_ns = 0;

	is_switch = prev != next;
	if (likely(is_switch)) {
		rq->nr_switches++;
		RCU_INIT_POINTER(rq->curr, next);
		rq = context_switch(rq, prev, next, &rf);
	}
}
```

### __schedule() 关键决策点

1. **获取当前 CPU 的运行队列**: `rq = cpu_rq(cpu)`
2. **获取当前任务**: `prev = rq->curr`
3. **阻塞前任务处理**: 如果 prev_state 非零且非抢占模式，调用 `try_to_block_task()`
4. **选择下一个任务**: `next = pick_next_task(rq, rq->donor, &rf)`
5. **任务切换**: 如果 `prev != next`，执行 `context_switch()`

---

## 4. pick_next_task() 选择下一个任务

### __pick_next_task() 通用选择函数

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

### pick_next_task_fair() CFS 公平调度选择

**文件**: `kernel/sched/fair.c:8978-9057`

```c
struct task_struct *
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
	// ... 组调度处理
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

### pick_eevdf() 最早合格虚拟截止时间优先

**文件**: `kernel/sched/fair.c:1010-1079`

EEVDF (Earliest Eligible Virtual Deadline First) 算法:
- 检查 `cfs_rq->next` buddy (PICK_BUDDY 优化)
- 检查 `cfs_rq->curr` 是否在保护期内 (protect_slice)
- 返回红黑树最左边合格实体

---

## 5. sched_submit_work() 工作提交

**文件**: `kernel/sched/core.c:6940-6975`

```c
static inline void sched_submit_work(struct task_struct *tsk)
{
	unsigned int task_flags;

	task_flags = tsk->flags;
	if (task_flags & PF_WQ_WORKER)
		wq_worker_sleeping(tsk);
	else if (task_flags & PF_IO_WORKER)
		io_wq_worker_sleeping(tsk);

	blk_flush_plug(tsk->plug, true);
}
```

---

## 6. struct task_struct 关键字段

**文件**: `include/linux/sched.h:820-878`

```c
struct task_struct {
	struct thread_info		thread_info;
	unsigned int			__state;

	void				*stack;
	refcount_t			usage;
	unsigned int			flags;

	int				on_cpu;
	int				on_rq;

	int				prio;          /* 动态优先级 */
	int				static_prio;    /* 静态优先级 */
	int				normal_prio;    /* 正规优先级 */
	unsigned int			rt_priority;    /* RT 优先级 */

	struct sched_entity		se;             /* CFS 调度实体 */
	struct sched_rt_entity		rt;             /* RT 调度实体 */
	struct sched_dl_entity		dl;             /* Deadline 调度实体 */
	const struct sched_class	*sched_class;   /* 调度类指针 */

	unsigned int			policy;          /* 调度策略 */
};
```

### 调度策略定义

```c
#define SCHED_NORMAL		0   /* CFS 公平调度 */
#define SCHED_FIFO		1   /* 先进先出 RT */
#define SCHED_RR		2   /* 时间片轮转 RT */
#define SCHED_BATCH		3   /* 批处理调度 */
#define SCHED_IDLE		5   /* 空闲调度 */
#define SCHED_DEADLINE		6   /* Deadline 调度 */
```

---

## 7. struct sched_entity CFS 调度实体

**文件**: `include/linux/sched.h:575-621`

```c
struct sched_entity {
	struct load_weight		load;           /* 实体负载权重 */
	struct rb_node			run_node;       /* 红黑树节点 */
	u64				deadline;       /* EEVDF 截止时间 */
	u64				min_vruntime;   /* 最小虚拟运行时间 */
	u64				vruntime;       /* 虚拟运行时间 */

	struct list_head		group_node;     /* 组节点 */
	unsigned char			on_rq;          /* 是否在运行队列 */

	u64				exec_start;     /* 执行开始时间 */
	u64				sum_exec_runtime;   /* 累计执行时间 */
	u64				prev_sum_exec_runtime;
	u64				nr_migrations;

#ifdef CONFIG_FAIR_GROUP_SCHED
	int				depth;          /* 层级深度 */
	struct sched_entity		*parent;        /* 父实体 */
	struct cfs_rq			*cfs_rq;        /* 所属 CFS 运行队列 */
	struct cfs_rq			*my_q;          /* 拥有的运行队列 */
	unsigned long			runnable_weight;
#endif

	struct sched_avg		avg;
};
```

---

## 8. struct cfs_rq CFS 运行队列

**文件**: `kernel/sched/sched.h:678-772`

```c
struct cfs_rq {
	struct load_weight	load;               /* 总负载权重 */
	unsigned int		nr_queued;           /* 排队的任务数 */
	unsigned int		h_nr_queued;         /* SCHED_NORMAL 任务数 */

	s64			sum_w_vruntime;      /* 加权 vruntime 和 */
	u64			sum_weight;          /* 权重和 */

	struct rb_root_cached	tasks_timeline;     /* CFS 红黑树根 */

	struct sched_entity	*curr;              /* 当前运行的实体 */
	struct sched_entity	*next;              /* 下一个 buddy (优化) */

	struct sched_avg		avg;                /* PELT 负载跟踪 */

#ifdef CONFIG_FAIR_GROUP_SCHED
	struct rq			*rq;                /* 所属 CPU 运行队列 */
	struct task_group	*tg;                /* 拥有此队列的任务组 */
#endif
};
```

---

## 9. 调度决策流程图

```
schedule()
  └─> sched_submit_work()
      
  └─> __schedule_loop()
        └─> __schedule(SM_NONE)
              1. prev = rq->curr
              2. if (!preempt && prev_state)
                   try_to_block_task()
              3. pick_next_task()
                    ├─> if (all_fair) pick_next_task_fair()
                    │     └─> pick_eevdf()
                    └─> for_each_active_class(class)
                          └─> 遍历调度类选择任务
              4. if (prev != next)
                   context_switch()
```

---

## 10. 数据结构关系图

```
task_struct
    │
    ├── se: sched_entity
    │       ├── run_node ──► cfs_rq->tasks_timeline (红黑树)
    │       ├── vruntime (CFS 排序键)
    │       ├── cfs_rq ◄─── (反向指针)
    │       └── parent (组调度)
    │
    ├── rt: sched_rt_entity
    ├── dl: sched_dl_entity
    │
    └── sched_class ──► fair_sched_class / rt_sched_class / dl_sched_class

cfs_rq
    ├── tasks_timeline (红黑树根)
    ├── curr (当前运行实体)
    └── avg (PELT 负载跟踪)
```

---

## 11. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| schedule | kernel/sched/core.c | 6998-7011 |
| __schedule | kernel/sched/core.c | 6764-6922 |
| __pick_next_task | kernel/sched/core.c | 5909-5964 |
| pick_next_task_fair | kernel/sched/fair.c | 8978-9057 |
| pick_eevdf | kernel/sched/fair.c | 1010-1079 |
| sched_submit_work | kernel/sched/core.c | 6940-6975 |
| struct task_struct | include/linux/sched.h | 820-878 |
| struct sched_entity | include/linux/sched.h | 575-621 |
| struct cfs_rq | kernel/sched/sched.h | 678-772 |
