# Linux 内核上下文切换机制分析

## 1. context_switch() - 主上下文切换函数

**文件**: `kernel/sched/core.c:5239-5302`

```c
static __always_inline struct rq *
context_switch(struct rq *rq, struct task_struct *prev,
	       struct task_struct *next, struct rq_flags *rf)
	__releases(__rq_lockp(rq))
{
	prepare_task_switch(rq, prev, next);

	arch_start_context_switch(prev);

	if (!next->mm) {				// to kernel
		enter_lazy_tlb(prev->active_mm, next);
		next->active_mm = prev->active_mm;
		if (prev->mm)
			mmgrab_lazy_tlb(prev->active_mm);
		else
			prev->active_mm = NULL;
	} else {					// to user
		membarrier_switch_mm(rq, prev->active_mm, next->mm);
		switch_mm_irqs_off(prev->active_mm, next->mm, next);
		lru_gen_use_mm(next->mm);

		if (!prev->mm) {
			rq->prev_mm = prev->active_mm;
			prev->active_mm = NULL;
		}
	}

	mm_cid_switch_to(prev, next);
	rseq_sched_switch_event(next);
	prepare_lock_switch(rq, next, rf);

	switch_to(prev, next, prev);
	barrier();

	return finish_task_switch(prev);
}
```

**关键点**:
- 处理内存管理单元 (MM) 切换
- 内核到内核: 使用 lazy TLB 模式
- 用户到用户/内核: 调用 `switch_mm_irqs_off()` 切换页表

---

## 2. prepare_task_switch() - 切换前准备

**文件**: `kernel/sched/core.c:5080-5091`

```c
static inline void
prepare_task_switch(struct rq *rq, struct task_struct *prev,
		    struct task_struct *next)
	__must_hold(__rq_lockp(rq))
{
	kcov_prepare_switch(prev);
	sched_info_switch(rq, prev, next);
	perf_event_task_sched_out(prev, next);
	fire_sched_out_preempt_notifiers(prev, next);
	kmap_local_sched_out();
	prepare_task(next);
	prepare_arch_switch(next);
}
```

---

## 3. finish_task_switch() - 切换后清理

**文件**: `kernel/sched/core.c:5112-5201`

```c
static struct rq *finish_task_switch(struct task_struct *prev)
	__releases(__rq_lockp(this_rq()))
{
	struct rq *rq = this_rq();
	struct mm_struct *mm = rq->prev_mm;
	unsigned int prev_state;

	if (WARN_ONCE(preempt_count() != 2*PREEMPT_DISABLE_OFFSET,
		      "corrupted preempt_count: %s/%d/0x%x\n",
		      current->comm, current->pid, preempt_count()))
		preempt_count_set(FORK_PREEMPT_COUNT);

	rq->prev_mm = NULL;

	prev_state = READ_ONCE(prev->__state);
	vtime_task_switch(prev);
	perf_event_task_sched_in(prev, current);
	finish_task(prev);
	tick_nohz_task_switch();
	finish_lock_switch(rq);
	finish_arch_post_lock_switch();
	kcov_finish_switch(current);
	kmap_local_sched_in();

	fire_sched_in_preempt_notifiers(current);

	if (mm) {
		membarrier_mm_sync_core_before_usermode(mm);
		mmdrop_lazy_tlb_sched(mm);
	}

	if (unlikely(prev_state == TASK_DEAD)) {
		if (prev->sched_class->task_dead)
			prev->sched_class->task_dead(prev);
		sched_ext_dead(prev);
		cgroup_task_dead(prev);
		put_task_stack(prev);
		put_task_struct_rcu_user(prev);
	}

	return rq;
}
```

---

## 4. __schedule() - 调度器主体

**文件**: `kernel/sched/core.c:6764-6922`

```c
static void __sched notrace __schedule(int sched_mode)
{
	struct task_struct *prev, *next;
	bool preempt = sched_mode > SM_NONE;
	bool is_switch = false;
	unsigned long *switch_count;
	unsigned int prev_state;
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

		if (!task_current_donor(rq, next))
			proxy_tag_curr(rq, next);

		++*switch_count;

		psi_account_irqtime(rq, prev, next);
		psi_sched_switch(prev, next, !task_on_rq_queued(prev) ||
					     prev->se.sched_delayed);

		trace_sched_switch(preempt, prev, next, prev_state);

		rq = context_switch(rq, prev, next, &rf);
	} else {
		if (!task_current_donor(rq, next))
			proxy_tag_curr(rq, next);

		rq_unpin_lock(rq, &rf);
		__balance_callbacks(rq, NULL);
		raw_spin_rq_unlock_irq(rq);
	}
	trace_sched_exit_tp(is_switch);
}
```

---

## 5. switch_to() 汇编实现

### 5.1 switch_to() 宏

**文件**: `arch/x86/include/asm/switch_to.h:49-52`

```c
#define switch_to(prev, next, last)					\
do {									\
	((last) = __switch_to_asm((prev), (next)));			\
} while (0)
```

### 5.2 __switch_to_asm() - 汇编层面的上下文切换

**文件**: `arch/x86/entry/entry_64.S:177-217`

```asm
SYM_FUNC_START(__switch_to_asm)
	ANNOTATE_NOENDBR
	pushq	%rbp
	pushq	%rbx
	pushq	%r12
	pushq	%r13
	pushq	%r14
	pushq	%r15

	/* switch stack */
	movq	TASK_threadsp(%rdi), %rsp
	movq	TASK_threadsp(%rsi), %rsp

#ifdef CONFIG_STACKPROTECTOR
	movq	TASK_stack_canary(%rsi), %rbx
	movq	%rbx, PER_CPU_VAR(__stack_chk_guard)
#endif

	FILL_RETURN_BUFFER %r12, RSB_CLEAR_LOOPS, X86_FEATURE_RSB_CTXSW

	popq	%r15
	popq	%r14
	popq	%r13
	popq	%r12
	popq	%rbx
	popq	%rbp

	jmp	__switch_to
SYM_FUNC_END(__switch_to_asm)
```

**保存的寄存器** (callee-saved):
- rbp, rbx, r12, r13, r14, r15
- rsp (通过 TASK_threadsp 存储在 task_struct->thread.sp)

### 5.3 __switch_to() - C 语言层面切换

**文件**: `arch/x86/kernel/process_64.c:610-670`

```c
__visible __notrace_funcgraph struct task_struct *
__switch_to(struct task_struct *prev_p, struct task_struct *next_p)
{
	struct thread_struct *prev = &prev_p->thread;
	struct thread_struct *next = &next_p->thread;
	int cpu = smp_processor_id();

	switch_fpu(prev_p, cpu);  // 切换 FPU 状态

	save_fsgs(prev_p);
	load_TLS(next, cpu);
	arch_end_context_switch(next_p);

	savesegment(es, prev->es);
	if (unlikely(next->es | prev->es))
		loadsegment(es, next->es);

	savesegment(ds, prev->ds);
	if (unlikely(next->ds | prev->ds))
		loadsegment(ds, next->ds);

	x86_fsgsbase_load(prev, next);
	x86_pkru_load(prev, next);

	raw_cpu_write(current_task, next_p);

	return prev_p;
}
```

**关键状态保存/恢复**:
1. **FPU/SSE 状态**: 通过 `switch_fpu()` 处理
2. **段寄存器**: fs, gs, ds, es
3. **TLS (Thread-Local Storage)**: 通过 `load_TLS()` 加载
4. **PKRU (Protection Keys)**: 通过 `x86_pkru_load()` 处理
5. **栈指针**: 在 `__switch_to_asm` 中通过 `TASK_threadsp` 切换

---

## 6. struct inactive_task_frame

**文件**: `arch/x86/include/asm/switch_to.h:23-42`

```c
struct inactive_task_frame {
#ifdef CONFIG_X86_64
	unsigned long r15;
	unsigned long r14;
	unsigned long r13;
	unsigned long r12;
#else
	unsigned long flags;
	unsigned long si;
	unsigned long di;
#endif
	unsigned long bx;

	unsigned long bp;
	unsigned long ret_addr;
};
```

---

## 7. struct rq (运行队列)

**文件**: `kernel/sched/sched.h:1124-1347`

```c
struct rq {
	unsigned int		nr_running;
#ifdef CONFIG_NUMA_BALANCING
	unsigned int		nr_numa_running;
	unsigned int		nr_preferred_running;
#endif
	unsigned int		ttwu_pending;
	unsigned long		cpu_capacity;

	struct task_struct __rcu *donor;
	struct task_struct __rcu *curr;
	struct task_struct	*idle;

	u64			nr_switches;
	raw_spinlock_t		__lock;

	struct cfs_rq		cfs;
	struct rt_rq		rt;
	struct dl_rq		dl;
	struct sched_dl_entity	fair_server;

	u64			clock_task;
	u64			clock_pelt;
	u64			clock;

	struct mm_struct	*prev_mm;

	int			cpu;
	int			online;

	atomic_t		nr_iowait;
};
```

---

## 8. 上下文切换流程总结

### 切换过程概述:

```
__schedule()
  │
  ├─> pick_next_task() 选择下一个任务
  ├─> 更新 rq->curr 指向新任务
  │
  └─> context_switch(rq, prev, next, &rf)
       │
       ├─> prepare_task_switch()
       ├─> MM 切换:
       │   ├─ 内核→内核: enter_lazy_tlb() + mmgrab_lazy_tlb()
       │   └─ 用户→用户: switch_mm_irqs_off() 切换页表
       │
       ├─> switch_to(prev, next, prev)
       │   ├─ __switch_to_asm(): 保存寄存器, 切换栈指针
       │   └─ __switch_to(): 切换 FPU, TLS, 段寄存器
       │
       └─> finish_task_switch(prev)
           ├─> mmdrop_lazy_tlb()
           ├─> 更新性能监控
           └─> 处理 TASK_DEAD 状态
```

### rq 字段更新:

| 字段 | 更新时机 | 说明 |
|------|---------|------|
| `rq->curr` | 切换前 | 指向当前运行的任务 |
| `rq->nr_switches` | 切换时 | 每次上下文切换递增 |
| `rq->prev_mm` | 切换时 | 保存前一个任务的 mm |
| `rq->clock*` | 切换前 | 更新调度时钟 |
| `rq->next_class` | 切换前 | 指向下一个任务的调度类 |

---

## 9. 状态保存/恢复总结

| 状态类型 | 保存位置 | 恢复位置 |
|---------|---------|---------|
| 通用寄存器 (rbx, rbp, r12-r15) | `__switch_to_asm` 栈帧 | `__switch_to_asm` 栈帧 |
| 栈指针 (rsp) | `task_struct->thread.sp` | `__switch_to_asm` |
| FPU/SSE/AVX 状态 | `task_struct->thread.fpu` | `switch_fpu()` |
| 段寄存器 (fs, gs, ds, es) | `task_struct->thread` | `__switch_to()` |
| TLS | `GDT/LDT` | `load_TLS()` |
| 页表/CR3 | `mm_struct->pgd` | `switch_mm_irqs_off()` |

---

## 10. 关键源码位置

| 函数 | 文件 | 行号 |
|------|------|------|
| context_switch | kernel/sched/core.c | 5239-5302 |
| prepare_task_switch | kernel/sched/core.c | 5080-5091 |
| finish_task_switch | kernel/sched/core.c | 5112-5201 |
| __schedule | kernel/sched/core.c | 6764-6922 |
| switch_to | arch/x86/include/asm/switch_to.h | 49-52 |
| __switch_to_asm | arch/x86/entry/entry_64.S | 177-217 |
| __switch_to | arch/x86/kernel/process_64.c | 610-670 |
| struct inactive_task_frame | arch/x86/include/asm/switch_to.h | 23-42 |
| struct rq | kernel/sched/sched.h | 1124-1347 |
