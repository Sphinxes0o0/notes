---
type: entity
tags: [Linux内核, 时间管理, hrtimer, tick, timekeeping, posix-timers]
created: 2026-05-20
sources: [notes-overview-kernel-time]
---

# Linux Kernel Time Subsystem

## 定义

Linux内核时间管理子系统，负责系统时钟维护、定时器管理（jiffies、hrtimer、tick_device）、时间统计（timekeeping）和POSIX定时器接口，为内核和用户空间提供精确的时间测量和定时事件服务。

## 关键要点

### 时间基础

- **jiffies**: 全局时钟滴答计数器，频率由HZ定义
- **struct timespec**: 秒+纳秒（常用）
- **struct timeval**: 秒+微秒

### Tick设备

**周期Tick**:
- tick_handle_periodic(): 周期中断处理
- 维护进程时间片、调度器负载

**Dynamic Tick (NO_HZ)**:
- 按需tick，减少功耗
- tick_nohz_idle_stop(): 空闲时停止tick
- tick_nohz_restart(): 唤醒时恢复

**struct tick_sched**: per-CPU tick调度状态

### 高精度定时器 (hrtimer)

**特性**:
- 纳秒级精度（相比jiffies的毫秒级）
- 基于红黑树管理（O(log n)查找）
- 支持绝对时间和相对时间

**核心结构**:
- hrtimer: 定时器实例
- hrtimer_cpu_base: per-CPU hrtimer管理

**关键API**:
- hrtimer_start(): 启动定时器
- hrtimer_cancel(): 取消定时器
- hrtimer_expires_rem(): 剩余时间

### Timekeeping

**核心结构**:
- tk_core: timekeeping全局状态
- timekeeper: per-CPU时间状态

**功能**:
- update_wall_time(): 更新墙上时间
- 维护xtime（真实时间）和monotonic时间

**NTP同步**:
- 网络时间协议校正
- 调整tick频率补偿时钟漂移

### Posix Timers

**接口**:
- timer_create(): 创建定时器
- timer_settime(): 设置时间
- timer_gettime(): 获取剩余时间
- timer_delete(): 删除定时器

**类型**:
- ITIMER_REAL: 真实时间
- ITIMER_VIRTUAL: 进程用户态时间
- ITIMER_PROF: 进程用户+内核态时间

**clock_* syscall**:
- clock_gettime()
- clock_settime()
- clock_getres()

### 源码位置

| 组件 | 路径 |
|------|------|
| tick | kernel/time/tick-*.c |
| hrtimer | kernel/time/hrtimer.c |
| timekeeping | kernel/time/timekeeping.c |
| posix-timers | kernel/time/posix-timers.c |

## 相关概念
- [[entities/linux/kernel/sched/linux-kernel-sched-core]] — 调度器与时间片
- [[entities/linux/kernel/sched/linux-kernel-sched-cfs]] — CFS与vruntime

## 来源详情
- [[sources/github-sphinxes0o0-notes-kernel-time]]
