---
type: index
tags: [linux-kernel, scheduler]
created: 2026-05-22
---

# Linux Kernel — Scheduler

> CFS scheduling, context switching, and load balancing

## Entities

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/linux/kernel/sched/linux-kernel-sched-core]] | Scheduler core: __schedule, pick_next_task, sched_class | linux-kernel, sched |
| [[entities/linux/kernel/sched/linux-kernel-sched-cfs]] | CFS: vruntime red-black tree, EEVDF, latency target | linux-kernel, sched, cfs |
| [[entities/linux/kernel/sched/linux-kernel-sched-context-switch]] | Context switch: switch_to, register save/restore, lazy TLB | linux-kernel, sched, context-switch |
| [[entities/linux/kernel/sched/linux-kernel-sched-load-balance]] | Load balancing: sched_domain, load_balance, idle balance | linux-kernel, sched, load-balance |

## Cross-References

- [[kernel-mm-index]] — Scheduler and MM interact on page fault paths and TLB shootdowns
- [[os-index]] — linux-scheduler bridges kernel scheduler with OS concepts
- [[kernel-block-index]] — IO scheduling interacts with CPU scheduling (blk-mq per-CPU queues)
