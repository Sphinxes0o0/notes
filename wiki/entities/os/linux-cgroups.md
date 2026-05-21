---
type: entity
tags: [Linux, cgroups, 资源限制, 容器]
created: 2026-05-20
sources: [notes-os]
---

# Linux Cgroups

## 定义

cgroups (control groups) 是 Linux 内核的资源限制机制，通过 CSS (cgroup_subsys_state) 跟踪进程资源使用，支持 CPU、内存、IO 等多种控制器。

## 关键要点

- **CSS 机制**: 每个 cgroup 的每个控制器一个 CSS 实例，`css_get/put()` 引用计数，`css_for_each_descendant_pre/post` 遍历后代
- **cgroup v2 单层级**: 统一树替代 v1 多层级，所有控制器在同一树中
- **CSS Set**: `css_set` 表示控制器 CSS 组合的哈希表，用于快速查找
- **任务迁移**: `cgroup_task_migrate()` 替换任务 CSS Set，通知控制器 `task_sleep/task_woken`
- **CPU 带宽控制**: `cpu.cfs_quota_us / cpu.cfs_period_us` 设置带宽上限
- **Memory 限制**: `memory.high/low/max` 触发异步回收，`memory.current` 实时使用量
- **cftype 伪文件**: `read/write/seq_show/poll` 操作定义 cgroupfs 文件行为
- **委托机制**: cgroup v2 支持子 cgroup 管理权限委托
- **线程模式**: 支持线程级 cgroup（`cgroup.threads`）

## 算法复杂度

| 操作 | 复杂度 |
|------|--------|
| CSS Set 查找 | O(1) average |
| 层级遍历 | O(n) |

## 相关概念

- [[entities/os/linux-scheduler]] — cgroups 的 cpu controller 影响 CFS 调度
- [[entities/os/linux-memory-allocator]] — cgroups 的 memory controller 限制内存使用

## 来源详情

- [[sources/github-notes-os]]
