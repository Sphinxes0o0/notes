---
type: entity
tags: [linux-kernel, scheduler, context-switch, switch-to]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel Context Switch

## 定义

上下文切换 (Context Switch) 是 CPU 从一个任务切换到另一个任务的过程，包括保存原任务状态和恢复新任务状态。核心函数是 `context_switch()` 和 `switch_to()` 宏。

## 关键要点

- **context_switch()**: 调度器选择下一个任务后调用，负责 MM 切换和调用 switch_to()
- **switch_to()**: x86 汇编宏，通过 `__switch_to_asm()` 保存/恢复寄存器
- **__switch_to()**: C 语言层面切换 FPU、TLS、段寄存器等
- **rq (run queue)**: 每个 CPU 一个，包含 cfs_rq、rt_rq、dl_rq、curr 等
- **prepare_task_switch() / finish_task_switch()**: 切换前后钩子
- **MM 切换**: 用户空间切换时调用 `switch_mm_irqs_off()` 切换页表；内核空间使用 lazy TLB

## 完整流程

```
__schedule()
    ↓
pick_next_task() → 选择下一个任务
    ↓
context_switch(rq, prev, next, &rf)
    ├─> prepare_task_switch()
    ├─> MM 切换:
    │     ├─ 内核→内核: enter_lazy_tlb()
    │     └─ 用户→用户: switch_mm_irqs_off() 切换 CR3/页表
    ├─> switch_to(prev, next, prev)
    │     ├─ __switch_to_asm(): 保存寄存器到 prev->thread.sp
    │     └─ __switch_to(): 切换 FPU/TLS/段寄存器
    └─> finish_task_switch(prev)
```

## 状态保存/恢复

| 状态类型 | 保存位置 | 恢复位置 |
|---------|---------|---------|
| 通用寄存器 (rbx, rbp, r12-r15) | `__switch_to_asm` 栈帧 | `__switch_to_asm` 栈帧 |
| 栈指针 (rsp) | `task_struct->thread.sp` | `__switch_to_asm` |
| FPU/SSE/AVX | `task_struct->thread.fpu` | `switch_fpu()` |
| 段寄存器 (fs, gs, ds, es) | `task_struct->thread` | `__switch_to()` |
| TLS | GDT/LDT | `load_TLS()` |
| 页表/CR3 | `mm_struct->pgd` | `switch_mm_irqs_off()` |

## 核心数据结构

### rq (运行队列)
```c
struct rq {
    unsigned int nr_running;        // 运行任务数
    struct task_struct __rcu *curr; // 当前任务
    struct task_struct *idle;      // idle 任务
    struct cfs_rq cfs;             // CFS 运行队列
    struct rt_rq rt;               // RT 运行队列
    struct dl_rq dl;               // Deadline 运行队列
    u64 clock_task;                // 调度时钟
    // ...
};
```

## 相关概念

- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — schedule() 调用 context_switch()
- [[entities/linux/kernel/sched/linux-kernel-sched-cfs]] — CFS 实体入队/出队

## 来源详情

- [[sources/notes-kernel]] — sched_context_switch.md
