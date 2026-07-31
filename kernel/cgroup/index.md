---
title: Linux Cgroups 资源控制子系统
---

# Linux Cgroups 资源控制子系统

本部分收录 Linux Cgroups 子系统的源码级分析，涵盖 CSS 状态对象、层级架构、控制器注册与任务迁移。

## 文档清单

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [cgroup_subsystem.md](cgroup_subsystem.md) | Cgroups 子系统：CSS、cgroup v2 层级、控制器资源跟踪、cgroupfs | kernel/cgroup/ |

## 主要内容

### 1. CSS（cgroup Subsys State）
- `struct cgroup_subsys_state`
- parent/child 链接
- 引用计数与释放

### 2. Cgroup v2 统一层级
- 单一层级 vs 多层级（v1）
- `cgroup_mkdir()` / `cgroup_rmdir()`
- `cgroup_attach_task()` / `cgroup_migrate()`

### 3. 控制器（Controllers）
- `struct cgroup_subsys`
- `cgroup_subsys_register()`
- cpu / memory / io / pids / freezer / devices

### 4. Cgroupfs 接口
- `cgroup_file_operations`
- `cgroup_file_write()` / `cgroup_file_read()`
- kernfs 后端

## 关键源码位置

| 组件 | 路径 |
|------|------|
| cgroup 核心 | kernel/cgroup/cgroup.c |
| cgroup v2 | kernel/cgroup/cgroup-v2.c |
| cgroupfs | kernel/cgroup/cgroupfs.c |
| css_set | kernel/cgroup/cgroup.c |
| 控制器注册 | kernel/cgroup/cgroup.c |

## 关联子系统

- **mm 内存控制器**: [`/kernel/mm/mm_memory_cgroup`](../mm/mm_memory_cgroup.md)
- **调度域**: `/kernel/sched/sched_load_balance`
- **I/O 控制器**: 通过 blk-throttle 实现