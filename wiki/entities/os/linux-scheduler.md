---
type: entity
tags: [linux-kernel, 调度器, cfs, 进程管理]
created: 2026-05-20
sources: [notes-os]
---

# Linux 进程调度器

## 定义

Linux 调度器通过分层调度类（Deadline → RT → CFS → Idle）管理进程执行，CFS 以虚拟时间为基础实现完全公平调度。

## 关键要点

- **调度类层次**: `stop_sched_class` → `dl_sched_class` → `rt_sched_class` → `fair_sched_class` → `idle_sched_class`
- **CFS 红黑树**: 按 `vruntime` 排序，`pick_next_entity()` 始终选最左节点（O(1)），入队 O(log n)
- **vruntime 计算**: `delta_fair = delta * NICE_0_LOAD / weight`，nice 值决定权重
- **调度延迟**: `sched_latency_ns`（默认 6ms），`slice = latency / nr_running`
- **实时调度**: RT 使用优先级位图数组，SCHED_FIFO/SCHED_RR；Deadline 使用 EDF 红黑树
- **负载均衡**: `load_balance()` 在调度域内迁移任务，`find_busiest_group()` 找最繁忙组
- **PELT**: Per-Entity Load Tracking，指数移动平均跟踪负载
- **上下文切换**: `__schedule()` → `pick_next_task()` → `switch_mm_irqs_off()` → `cpu_switch_to()`

## 算法复杂度

| 操作 | 复杂度 |
|------|--------|
| CFS 入队 | O(log n) |
| CFS 选取下一个 | O(1) |
| RT 选取下一个 | O(1) |
| 负载均衡 | O(n) 遍历调度域 |

## 相关概念

- [[entities/os/os-process-thread]] — 调度器调度的是线程
- [[entities/os/linux-cgroups]] — cgroups 的 cpu controller 限制 CFS 带宽
- [[entities/os/linux-memory-allocator]] — 调度器与内存回收（VMSCAN）交互

## 来源详情

- [[sources/notes-os]]
## Related Concepts

- [[entities/os/os-io-model]] — I/O多路复用影响进程调度
