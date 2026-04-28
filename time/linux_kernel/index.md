# Linux Time 子系统文档索引

## 文档

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [time_subsystem.md](time_subsystem.md) | 时间子系统: tick, hrtimer, timekeeping, posix-timers | kernel/time/ |
| [time_deep_dive_r1.md](time_deep_dive_r1.md) | 深度分析 R1: tick_device, timekeeper, NTP, hrtimer | kernel/time/ |

---

## 主要内容

### 1. 时间基础
- jiffies 和 HZ
- struct timespec / struct timeval

### 2. Tick 设备
- tick_handle_periodic()
- NO_HZ / Dynamic Tick
- struct tick_sched

### 3. 高精度定时器 (hrtimer)
- struct hrtimer
- hrtimer_start()
- hrtimer_cpu_base

### 4. Posix Timers
- timer_create()
- itimer
- clock_* syscall

### 5. Timekeeping
- struct tk_core
- struct timekeeper
- update_wall_time()

---

## 关键源码位置

| 组件 | 路径 |
|------|------|
| tick | kernel/time/tick-*.c |
| hrtimer | kernel/time/hrtimer.c |
| timekeeping | kernel/time/timekeeping.c |
| posix-timers | kernel/time/posix-timers.c |
