---
type: entity
tags: [linux-kernel, scheduler, load-balance, sched-domain]
created: 2026-05-20
sources: [notes-overview-kernel]
---

# Linux Kernel Scheduler Load Balancing

## 定义

负载均衡 (Load Balancing) 在多 CPU 间分散任务，提高整体系统吞吐量和资源利用率。Linux 通过调度域 (sched_domain) 的层次结构实现跨 CPU、跨缓存、跨节点的负载均衡。

## 关键要点

- **sched_domain**: 调度域，定义一组 CPU 之间的平衡边界
- **sched_group**: 调度组，一组 CPU 的容量信息
- **detach_tasks()**: 从源 CPU 分离任务
- **attach_tasks()**: 将任务附加到目标 CPU
- **sched_balance_rq()**: 核心均衡函数，遍历域执行均衡
- **NEWIDLE 均衡**: CPU 即将 idle 时触发，从其他 CPU 拉取任务
- **周期性均衡**: 定时器触发，在调度软中断中执行
- **调度域层次**: SMT → CLS → MC → PKG → NUMA

## 调度域层次

```
SMT (超线程) → 同一物理核心的逻辑 CPU
    ↓
CLS (Cluster) → 共享 LLC 缓存的 CPU 组
    ↓
MC (Multi-Core) → 同一 CPU 封装内的核心
    ↓
PKG (Package) → 整个物理 CPU
    ↓
NUMA → 跨 NUMA 节点
```

## 负载均衡触发时机

| 触发方式 | 说明 |
|---------|------|
| NEWIDLE | CPU 即将 idle，从其他 CPU 拉取任务 |
| 周期性 | sched_balance_softirq 定时执行 |
| WAKE | 任务唤醒时，检查是否在合适 CPU 运行 |
| FORK/EXEC | fork 或 exec 时检查均衡 |

## 核心数据结构

### sched_domain
```c
struct sched_domain {
    struct sched_domain __rcu *parent;   // 父域
    struct sched_domain __rcu *child;    // 子域
    struct sched_group *groups;          // 平衡组
    unsigned long min_interval;        // 最小平衡间隔
    unsigned long max_interval;         // 最大平衡间隔
    unsigned int busy_factor;           // 忙时减少平衡
    unsigned int imbalance_pct;         // 不平衡阈值
    int flags;                          // SD_* 标志
    // ...
};
```

### sched_group
```c
struct sched_group {
    atomic_t ref;                  // 引用计数
    unsigned int group_weight;     // 组权重
    struct sched_group_capacity *sgc; // 组容量
    unsigned long cpumask[];       // 组内 CPU 掩码
};
```

## 组类型 (group_type)

| 类型 | 说明 |
|------|------|
| group_has_spare | 有备用容量 |
| group_fully_busy | 完全使用 |
| group_misfit_task | 任务不适合当前 CPU 容量 |
| group_overloaded | CPU 过载 |

## 相关概念

- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — 调度器核心框架
- [[entities/linux/kernel/sched/linux-kernel-sched-cfs]] — CFS 任务迁移

## 来源详情

- [[sources/notes-kernel]] — sched_load_balance.md
