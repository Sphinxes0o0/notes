---
type: entity
tags: [linux-kernel, scheduler, cfs, vruntime, eevdf]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel CFS Scheduler (完全公平调度器)

## 定义

CFS (Completely Fair Scheduler) 是 Linux 默认的调度器，通过红黑树按 vruntime 排序，保证每个任务获得公平的 CPU 时间。

## 关键要点

- **vruntime**: 虚拟运行时间，CFS 的核心调度键。计算公式: `vruntime += delta_exec * (NICE_0_LOAD / weight)`
- **EEVDF (Earliest Eligible Virtual Deadline First)**: 当前 CFS 使用的选择算法
- **lag**: 任务延迟，`lag_i = w_i * (V - v_i)`，lag >= 0 的任务才能被选中
- **sched_entity**: CFS 调度实体，包含 load、run_node (红黑树节点)、vruntime、deadline
- **cfs_rq**: CFS 运行队列，包含 tasks_timeline (红黑树根)、curr (当前运行实体)
- **calc_delta_fair()**: 计算实际运行时间转换为虚拟时间
- **pick_eevdf()**: EEVDF 选择算法，选择 deadline 最早的合格实体

## 调度决策

1. 检查 `cfs_rq->next` buddy (PICK_BUDDY 优化)
2. 检查 `cfs_rq->curr` 是否在保护期内
3. 返回红黑树最左边符合条件的节点

## 核心数据结构

### sched_entity
```c
struct sched_entity {
    struct load_weight load;    // 实体负载权重
    struct rb_node run_node;   // 红黑树节点
    u64 deadline;              // EEVDF 截止时间
    u64 vruntime;              // 虚拟运行时间
    unsigned char on_rq;       // 是否在运行队列上
    // ...
};
```

### cfs_rq
```c
struct cfs_rq {
    struct load_weight load;            // 队列总负载
    unsigned int nr_queued;             // 排队任务数
    struct rb_root_cached tasks_timeline; // CFS 红黑树根
    struct sched_entity *curr;          // 当前运行实体
    struct sched_entity *next;          // 下一个 buddy
    s64 sum_w_vruntime;               // 加权 vruntime 和
    // ...
};
```

## vruntime 计算

```c
// 实际运行时间转换为虚拟时间
delta_vruntime = delta_exec * (NICE_0_LOAD / task_weight)
// NICE_0_LOAD = 1024
// 高 nice 值 (低权重) 任务 vruntime 增长更快，获得更少 CPU 时间
```

## 相关概念

- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — 调度器核心框架
- [[entities/linux/kernel/sched/linux-kernel-sched-context-switch]] — 上下文切换涉及 CFS 实体入队/出队
- [[entities/linux/kernel/sched/linux-kernel-sched-load-balance]] — CFS 负载均衡

## 来源详情

- [[sources/github-sphinxes0o0-notes-kernel]] — sched_cfs.md
## Related Concepts

- [[entities/linux/kernel/time/linux-kernel-time-core]] — CFS依赖时间管理进行vruntime计算
