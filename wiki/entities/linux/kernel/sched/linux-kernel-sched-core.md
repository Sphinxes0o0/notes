---
type: entity
tags: [linux-kernel, scheduler, schedule, task]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel Scheduler Core

## 定义

调度器决定哪个任务在哪个 CPU 上运行。`schedule()` 是主动调度的入口，`__schedule()` 是核心函数，`pick_next_task()` 选择下一个运行的任务。

## 关键要点

- **schedule()**: 主动调度入口，调用 `__schedule_loop()`
- **__schedule()**: 调度核心，禁用中断、选择下一个任务、执行 context_switch()
- **pick_next_task()**: 按调度类优先级遍历，选择最高优先级任务
- **调度类优先级**: stop > dl > rt > fair > idle
- **task_struct**: 描述每个任务，包含 __state、prio、se (CFS)、sched_class

## 调度决策流程

```
schedule()
    ↓
sched_submit_work()
    ↓
__schedule_loop()
    └─> __schedule(SM_NONE)
          1. prev = rq->curr
          2. if (!preempt && prev_state) → try_to_block_task()
          3. next = pick_next_task()
          4. if (prev != next) → context_switch()
```

## 调度策略

| 策略 | 说明 |
|------|------|
| SCHED_NORMAL | CFS 公平调度 (SCHED_BATCH, SCHED_IDLE) |
| SCHED_FIFO | 实时先进先出，无时间片 |
| SCHED_RR | 实时轮转，有时间片 |
| SCHED_DEADLINE | EDF 最早截止时间优先 |

## task_struct 关键字段

```c
struct task_struct {
    unsigned int __state;        // 任务状态
    int prio;                   // 动态优先级
    int static_prio;             // 静态优先级
    int normal_prio;             // 正规优先级
    unsigned int rt_priority;     // RT 优先级

    struct sched_entity se;      // CFS 调度实体
    struct sched_rt_entity rt;   // RT 调度实体
    struct sched_dl_entity dl;   // Deadline 调度实体
    const struct sched_class *sched_class;  // 调度类指针
    unsigned int policy;         // 调度策略
    // ...
};
```

## 相关概念

- [[entities/linux/kernel/sched/linux-kernel-sched-cfs]] — CFS 调度器实现
- [[entities/linux/kernel/sched/linux-kernel-sched-context-switch]] — context_switch() 执行 CPU 切换
- [[entities/linux/kernel/sched/linux-kernel-sched-load-balance]] — 多 CPU 间负载均衡

## 来源详情

- [[sources/github-sphinxes0o0-notes-kernel]] — sched_core.md
## Related Concepts

- [[entities/linux/kernel/time/linux-kernel-time-core]] — 时间管理是调度器的核心依赖
- [[entities/linux/kernel/rcu/linux-kernel-rcu-core]] — RCU用于调度器数据保护
- [[entities/linux/kernel/virt/linux-kernel-virt-kvm]] — vCPU调度是KVM虚拟化的核心
