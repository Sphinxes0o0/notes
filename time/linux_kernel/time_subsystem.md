# Linux 内核时间子系统分析文档

## 目录

1. [时间基础](#1-时间基础)
2. [Tick 设备](#2-tick-设备)
3. [高精度定时器 hrtimer](#3-高精度定时器-hrtimer)
4. [Posix Timers](#4-posix-timers)
5. [Timekeeping 时间追踪](#5-timekeeping-时间追踪)
6. [时区处理](#6-时区处理)
7. [架构图](#7-架构图)

---

## 1. 时间基础

### 1.1 Jiffies 和 HZ

**源码位置**: `/Users/sphinx/github/linux/include/linux/jiffies.h`

Jiffies 是内核中表示时间的基本单位,是一个全局变量,每经过一个时钟滴答(Tick)增加 1。

```c
// include/linux/jiffies.h:85-86
extern u64 __cacheline_aligned_in_smp jiffies_64;
extern unsigned long volatile __cacheline_aligned_in_smp __jiffy_arch_data jiffies;
```

**HZ** 是每秒时钟中断的次数,由架构决定:

| HZ 值 | 适用场景 |
|-------|----------|
| 100 | 通用服务器 |
| 250 | 桌面系统 |
| 300 | 某些特定架构 |
| 1000 | 高精度需求(嵌入式) |

```c
// include/linux/jiffies.h:23-45
#if HZ >= 12 && HZ < 24
# define SHIFT_HZ	4
#elif HZ >= 24 && HZ < 48
# define SHIFT_HZ	5
// ... 更多HZ值定义
#endif
```

**TICK_USEC** 计算每次tick的微秒数:

```c
// include/linux/jiffies.h:64-65
#define TICK_USEC ((USEC_PER_SEC + HZ/2) / HZ)
#define USER_TICK_USEC ((1000000UL + USER_HZ/2) / USER_HZ)
```

**时间比较宏**:

```c
// include/linux/jiffies.h:127-130
#define time_after(a,b)		\
	(typecheck(unsigned long, a) && \
	 typecheck(unsigned long, b) && \
	 ((long)((b) - (a)) < 0))

#define time_before(a,b)	time_after(b,a)
```

### 1.2 时间结构体

**struct timespec** - 纳秒级精度:

```c
// include/linux/time.h:36-56 (struct tm 定义)
// include/uapi/linux/time.h 中的实际定义:
// struct timespec {
//     __kernel_time_t tv_sec;    /* 秒 */
//     long tv_nsec;              /* 纳秒 */
// };
```

**struct timeval** - 微秒级精度(较老):

```c
// include/uapi/linux/time.h
// struct timeval {
//     __kernel_time_t tv_sec;   /* 秒 */
//     __suseconds_t tv_usec;    /* 微秒 */
// };
```

**ktime_t** - 内核内部时间表示:

```c
// include/linux/ktime.h
// 64位整数,直接存储纳秒值
typedef s64 ktime_t;
```

**时间转换关系**:

```
CLOCK_REALTIME  ←→  CLOCK_MONOTONIC
     ↑                    ↑
  wall_to_monotonic 偏移
```

### 1.3 时间分辨率

| 组件 | 分辨率 | 源码位置 |
|------|--------|----------|
| jiffies | 1/HZ 秒 | jiffies.h |
| timespec | 1 纳秒 | time.h |
| timeval | 1 微秒 | time.h |
| ktime_t | 1 纳秒 | ktime.h |
| hrtimer | 1 纳秒(硬件支持) | hrtimer.c |
| TICK_NSEC | HZ对应的纳秒 | tick-internal.h |

```c
// kernel/time/hrtimer.c:58
#define HIGH_RES_NSEC		1
```

---

## 2. Tick 设备

### 2.1 tick_handle_periodic()

**源码位置**: `/Users/sphinx/github/linux/kernel/time/tick-common.c:108-146`

这是周期 tick 的主要处理函数:

```c
// tick-common.c:108-146
void tick_handle_periodic(struct clock_event_device *dev)
{
    int cpu = smp_processor_id();
    ktime_t next = dev->next_event;

    tick_periodic(cpu);  // 处理 tick 事件

    // 检查是否转换到 HIGHRES 或 NOHZ 模式
    if (IS_ENABLED(CONFIG_TICK_ONESHOT) && dev->event_handler != tick_handle_periodic)
        return;

    if (!clockevent_state_oneshot(dev))
        return;
    for (;;) {
        // 设置下一个周期事件
        next = ktime_add_ns(next, TICK_NSEC);

        if (!clockevents_program_event(dev, next, false))
            return;

        // 在 oneshot 模式下循环调用 tick_periodic
        if (timekeeping_valid_for_hres())
            tick_periodic(cpu);
    }
}
```

**tick_periodic()** 处理具体事务:

```c
// tick-common.c:86-103
static void tick_periodic(int cpu)
{
    if (READ_ONCE(tick_do_timer_cpu) == cpu) {
        raw_spin_lock(&jiffies_lock);
        write_seqcount_begin(&jiffies_seq);

        tick_next_period = ktime_add_ns(tick_next_period, TICK_NSEC);

        do_timer(1);           // 更新 jiffies
        write_seqcount_end(&jiffies_seq);
        raw_spin_unlock(&jiffies_lock);
        update_wall_time();    // 更新墙上时间
    }

    update_process_times(user_mode(get_irq_regs()));
    profile_tick(CPU_PROFILING);
}
```

### 2.2 NO_HZ / Dynamic Tick

**源码位置**: `/Users/sphinx/github/linux/kernel/time/tick-sched.c`

NO_HZ(也称 dynamic tick)允许 CPU 在空闲时停止周期 tick 以节省功耗。

**核心结构体 struct tick_sched**:

```c
// kernel/time/tick-sched.h:64-103
struct tick_sched {
    /* 通用标志 */
    unsigned long			flags;

    /* Tick 处理: jiffies 停滞检查 */
    unsigned int			stalled_jiffies;
    unsigned long			last_tick_jiffies;

    /* Tick 处理 */
    struct hrtimer			sched_timer;     // 调度定时器
    ktime_t				last_tick;       // 上一次 tick
    ktime_t				next_tick;       // 下一次 tick
    unsigned long			idle_jiffies;
    ktime_t				idle_waketime;
    unsigned int			got_idle_tick;

    /* 空闲入口 */
    seqcount_t			idle_sleeptime_seq;
    ktime_t				idle_entrytime;

    /* Tick 停止 */
    unsigned long			last_jiffies;
    u64				timer_expires_base;
    u64				timer_expires;
    u64				next_timer;
    ktime_t				idle_expires;
    unsigned long			idle_calls;
    unsigned long			idle_sleeps;

    /* 空闲退出 */
    ktime_t				idle_exittime;
    ktime_t				idle_sleeptime;
    ktime_t				iowait_sleeptime;

    /* 全动态 tick 处理 */
    atomic_t			tick_dep_mask;

    /* 时钟源变化通知 */
    unsigned long			check_clocks;
};
```

**Tick 标志位**:

```c
// tick-sched.h:17-31
#define TS_FLAG_INIDLE		BIT(0)    // CPU 处于 tick 空闲模式
#define TS_FLAG_STOPPED		BIT(1)    // 空闲 tick 已停止
#define TS_FLAG_IDLE_ACTIVE	BIT(2)    // 空闲 tick 正在执行
#define TS_FLAG_DO_TIMER_LAST	BIT(3)    // CPU 是最后一个执行 do_timer 的
#define TS_FLAG_NOHZ		BIT(4)    // NO_HZ 已启用
#define TS_FLAG_HIGHRES		BIT(5)    // 高精度 tick 模式
```

**NO_HZ 核心函数 - tick_nohz_handler()**:

```c
// kernel/time/tick-sched.c:306-334
static enum hrtimer_restart tick_nohz_handler(struct hrtimer *timer)
{
    struct tick_sched *ts = container_of(timer, struct tick_sched, sched_timer);
    struct pt_regs *regs = get_irq_regs();
    ktime_t now = ktime_get();

    tick_sched_do_timer(ts, now);  // 处理计时器

    if (regs)
        tick_sched_handle(ts, regs);  // 更新进程时间
    else
        ts->next_tick = 0;

    // 如果 tick 已停止则不重启
    if (unlikely(tick_sched_flag_test(ts, TS_FLAG_STOPPED)))
        return HRTIMER_NORESTART;

    hrtimer_forward(timer, now, TICK_NSEC);  // 转发到下一个 tick

    return HRTIMER_RESTART;
}
```

### 2.3 Tick 设备管理

**struct tick_device** - 每个 CPU 的 tick 设备:

```c
// kernel/time/tick-sched.h:12-15
struct tick_device {
    struct clock_event_device *evtdev;  // 事件设备
    enum tick_device_mode mode;          // PERODIC 或 ONESHOT
};

enum tick_device_mode {
    TICKDEV_MODE_PERIODIC,
    TICKDEV_MODE_ONESHOT,
};
```

**tick_do_timer_cpu** - 负责更新 jiffies 的 CPU:

```c
// tick-common.c:51
int tick_do_timer_cpu __read_mostly = TICK_DO_TIMER_BOOT;
```

---

## 3. 高精度定时器 hrtimer

### 3.1 hrtimer 结构体

**源码位置**: `/Users/sphinx/github/linux/include/linux/hrtimer_types.h:39-48`

```c
struct hrtimer {
    struct timerqueue_node		node;       // 定时器队列节点
    ktime_t				_softexpires; // 软过期时间
    enum hrtimer_restart		(*__private function)(struct hrtimer *); // 回调函数
    struct hrtimer_clock_base	*base;       // 所属时钟基准
    u8				state;        // 状态 (ENQUEUED, INACTIVE)
    u8				is_rel;       // 是否为相对时间
    u8				is_soft;      // 是否在软中断上下文执行
    u8				is_hard;      // 是否在硬中断上下文执行
};
```

**hrtimer_clock_base** - 每个 CPU 每种时钟的基础结构:

```c
// include/linux/hrtimer_defs.h:26-34
struct hrtimer_clock_base {
    struct hrtimer_cpu_base	*cpu_base;   // 指向 per-CPU 基准
    unsigned int		index;        // 基准索引
    clockid_t		clockid;      // 时钟 ID
    seqcount_raw_spinlock_t	seq;         // seqcount 保护
    struct hrtimer		*running;     // 当前运行的定时器
    struct timerqueue_head	active;      // 活跃定时器红黑树
    ktime_t			offset;       // 到单调时钟的偏移
};
```

**hrtimer_cpu_base** - per-CPU 的 hrtimer 基准:

```c
// include/linux/hrtimer_defs.h:81-107
struct hrtimer_cpu_base {
    raw_spinlock_t			lock;
    unsigned int			cpu;
    unsigned int			active_bases;      // 活跃基准位图
    unsigned int			clock_was_set_seq; // 时钟设置序列
    unsigned int			hres_active : 1;   // 高精度模式活跃
    unsigned int			in_hrtirq : 1;     // hrtimer 中断中
    unsigned int			hang_detected : 1; // 检测到挂起
    unsigned int			softirq_activated : 1;
    unsigned int			online : 1;
    ktime_t				expires_next;      // 下一个过期时间
    struct hrtimer			*next_timer;      // 下一个定时器
    ktime_t				softirq_expires_next;
    struct hrtimer			*softirq_next_timer;
    struct hrtimer_clock_base	clock_base[HRTIMER_MAX_CLOCK_BASES];
    call_single_data_t		csd;
};
```

**时钟基准类型枚举**:

```c
// include/linux/hrtimer_defs.h:36-46
enum hrtimer_base_type {
    HRTIMER_BASE_MONOTONIC,       // 单调时钟
    HRTIMER_BASE_REALTIME,        // 实时时钟
    HRTIMER_BASE_BOOTTIME,        // 启动时间
    HRTIMER_BASE_TAI,             // TAI 国际原子时
    HRTIMER_BASE_MONOTONIC_SOFT,  // 软中断版本
    HRTIMER_BASE_REALTIME_SOFT,
    HRTIMER_BASE_BOOTTIME_SOFT,
    HRTIMER_BASE_TAI_SOFT,
    HRTIMER_MAX_CLOCK_BASES,
};
```

**per-CPU hrtimer 基准初始化**:

```c
// kernel/time/hrtimer.c:80-119
DEFINE_PER_CPU(struct hrtimer_cpu_base, hrtimer_bases) =
{
    .lock = __RAW_SPIN_LOCK_UNLOCKED(hrtimer_bases.lock),
    .clock_base = {
        { .index = HRTIMER_BASE_MONOTONIC,  .clockid = CLOCK_MONOTONIC, },
        { .index = HRTIMER_BASE_REALTIME,   .clockid = CLOCK_REALTIME, },
        { .index = HRTIMER_BASE_BOOTTIME,   .clockid = CLOCK_BOOTTIME, },
        { .index = HRTIMER_BASE_TAI,        .clockid = CLOCK_TAI, },
        { .index = HRTIMER_BASE_MONOTONIC_SOFT, .clockid = CLOCK_MONOTONIC, },
        { .index = HRTIMER_BASE_REALTIME_SOFT,  .clockid = CLOCK_REALTIME, },
        { .index = HRTIMER_BASE_BOOTTIME_SOFT,  .clockid = CLOCK_BOOTTIME, },
        { .index = HRTIMER_BASE_TAI_SOFT,       .clockid = CLOCK_TAI, },
    },
    .csd = CSD_INIT(retrigger_next_event, NULL)
};
```

### 3.2 hrtimer_start() 启动定时器

**源码位置**: `/Users/sphinx/github/linux/kernel/time/hrtimer.c:1312-1335`

```c
// hrtimer.c:1312-1335
void hrtimer_start_range_ns(struct hrtimer *timer, ktime_t tim,
			    u64 delta_ns, const enum hrtimer_mode mode)
{
    struct hrtimer_clock_base *base;
    unsigned long flags;

    // 检查 SOFT/HARD 模式匹配
    if (!IS_ENABLED(CONFIG_PREEMPT_RT))
        WARN_ON_ONCE(!(mode & HRTIMER_MODE_SOFT) ^ !timer->is_soft);
    else
        WARN_ON_ONCE(!(mode & HRTIMER_MODE_HARD) ^ !timer->is_hard);

    base = lock_hrtimer_base(timer, &flags);

    if (__hrtimer_start_range_ns(timer, tim, delta_ns, mode, base))
        hrtimer_reprogram(timer, true);  // 重新编程硬件

    unlock_hrtimer_base(timer, &flags);
}
EXPORT_SYMBOL_GPL(hrtimer_start_range_ns);
```

**内部函数 __hrtimer_start_range_ns()**:

```c
// hrtimer.c:1218-1301
static int __hrtimer_start_range_ns(struct hrtimer *timer, ktime_t tim,
                                    u64 delta_ns, const enum hrtimer_mode mode,
                                    struct hrtimer_clock_base *base)
{
    struct hrtimer_cpu_base *this_cpu_base = this_cpu_ptr(&hrtimer_bases);
    struct hrtimer_clock_base *new_base;
    bool force_local, first;

    // 决定是否强制本地执行
    force_local = base->cpu_base == this_cpu_base;
    force_local &= base->cpu_base->next_timer == timer;
    force_local &= this_cpu_base->online;

    // 移除已存在的定时器
    remove_hrtimer(timer, base, true, force_local);

    // 处理相对时间
    if (mode & HRTIMER_MODE_REL)
        tim = ktime_add_safe(tim, __hrtimer_cb_get_time(base->clockid));

    tim = hrtimer_update_lowres(timer, tim, mode);
    hrtimer_set_expires_range_ns(timer, tim, delta_ns);

    // 切换定时器基准(如需要)
    if (!force_local) {
        new_base = switch_hrtimer_base(timer, base,
                                       mode & HRTIMER_MODE_PINNED);
    } else {
        new_base = base;
    }

    first = enqueue_hrtimer(timer, new_base, mode);
    if (!force_local) {
        if (hrtimer_base_is_online(this_cpu_base))
            return first;
        if (first) {
            smp_call_function_single_async(new_cpu_base->cpu, &new_cpu_base->csd);
        }
        return 0;
    }

    hrtimer_force_reprogram(new_base->cpu_base, 1);
    return 0;
}
```

### 3.3 hrtimer_run_pending() hrtimer 调度

**源码位置**: `/Users/sphinx/github/linux/kernel/time/hrtimer.c` (实际调用在 tick-sched.c)

hrtimer 通过 tick 调度,在以下流程中被调用:

```
tick_nohz_handler() 或 tick_periodic()
  └── hrtimer_run_queues()
        └── __hrtimer_run_queues()
              └── 遍历所有过期的 hrtimer 并执行回调
```

**__hrtimer_run_queues()** 处理过期定时器:

```c
// hrtimer.c 中的实现,核心逻辑:
// 遍历所有活跃的 clock_base
// 对每个 base 的红黑树中的过期定时器调用其回调函数
```

**定时器重新编程**:

```c
// hrtimer.c:660-687
static void __hrtimer_reprogram(struct hrtimer_cpu_base *cpu_base,
                                struct hrtimer *next_timer,
                                ktime_t expires_next)
{
    cpu_base->expires_next = expires_next;

    if (!hrtimer_hres_active(cpu_base) || cpu_base->hang_detected)
        return;

    tick_program_event(expires_next, 1);  // 编程下一个事件
}
```

---

## 4. Posix Timers

### 4.1 timer_create() 系统调用

**源码位置**: `/Users/sphinx/github/linux/kernel/time/posix-timers.c`

**k_itimer 结构体** - 内核中的 POSIX 定时器:

```c
// 实际定义在 posix-timers.c 中,核心字段:
struct k_itimer {
    struct list_head        list;           // 链表头
    spinlock_t              it_lock;         // 保护此结构
    clockid_t               it_clock;        // 时钟类型
    timer_t                 it_id;           // 定时器 ID
    int                     it_status;       // 状态
    s64                     it_overrun;      // 超限计数
    s64                     it_overrun_last; // 上次超限
    union {                                 // 定时器类型联合
        struct {
            struct hrtimer      timer;
        } real;
        struct { ... } cpu;
        struct { ... } sig;
    } it;
    struct callback_head    futex_state;
    // ...
};
```

**do_timer_create() 实现**:

```c
// posix-timers.c:458-510
static int do_timer_create(clockid_t which_clock, struct sigevent *event,
                           timer_t __user *created_timer_id)
{
    const struct k_clock *kc = clockid_to_kclock(which_clock);
    // ... 参数验证 ...

    new_timer = alloc_posix_timer();
    // ... 初始化 ...

    new_timer_id = posix_timer_add(new_timer, req_id);
    if (new_timer_id < 0) {
        posixtimer_free_timer(new_timer);
        return new_timer_id;
    }

    new_timer->it_clock = which_clock;
    new_timer->kclock = kc;
    // ...

    if (event->sigev_notify != SIGEV_NONE) {
        // 设置信号处理
    }

    return new_timer_id;
}
```

**时钟类型到 k_clock 的映射**:

```c
// posix-timers.c:57
static const struct k_clock * const posix_clocks[];
static const struct k_clock clock_realtime, clock_monotonic;
```

**k_clock 操作接口**:

```c
// kernel/time/posix-timers.h:10-37
struct k_clock {
    int	(*clock_getres)(const clockid_t which_clock, struct timespec64 *tp);
    int	(*clock_set)(const clockid_t which_clock, const struct timespec64 *tp);
    int	(*clock_get_timespec)(const clockid_t which_clock, struct timespec64 *tp);
    ktime_t	(*clock_get_ktime)(const clockid_t which_clock);
    int	(*clock_adj)(const clockid_t which_clock, struct __kernel_timex *tx);
    int	(*timer_create)(struct k_itimer *timer);
    int	(*nsleep)(const clockid_t which_clock, int flags, const struct timespec64 *);
    int	(*timer_set)(struct k_itimer *timr, int flags,
                         struct itimerspec64 *new_setting,
                         struct itimerspec64 *old_setting);
    int	(*timer_del)(struct k_itimer *timr);
    void	(*timer_get)(struct k_itimer *timr, struct itimerspec64 *cur_setting);
    void	(*timer_rearm)(struct k_itimer *timr);
    // ...
};
```

### 4.2 itimer 间隔定时器

**源码位置**: `/Users/sphinx/github/linux/kernel/time/itimer.c`

itimer 是传统的间隔定时器实现,与 POSIX  timers 共享底层机制:

```c
// itimer.c:29-45
static struct timespec64 itimer_get_remtime(struct hrtimer *timer)
{
    ktime_t rem = __hrtimer_get_remaining(timer, true);

    if (hrtimer_active(timer)) {
        if (rem <= 0)
            rem = NSEC_PER_USEC;
    } else
        rem = 0;

    return ktime_to_timespec64(rem);
}
```

**ITIMER 类型**:

```c
// itimer.c:81-86
switch (which) {
case ITIMER_REAL:    // 真实时间,发送 SIGALRM
case ITIMER_VIRTUAL: // 虚拟时间(用户 CPU 时间),发送 SIGVTALRM
case ITIMER_PROF:    // 剖析时间(用户+系统 CPU),发送 SIGPROF
}
```

**do_setitimer() 设置定时器**:

```c
// itimer.c:225-269
static int do_setitimer(int which, struct itimerspec64 *value,
                        struct itimerspec64 *ovalue)
{
    // ITIMER_REAL 使用 hrtimer 实现
    case ITIMER_REAL:
        timer = &tsk->signal->real_timer;
        // 启动 hrtimer
        hrtimer_start(timer, expires, HRTIMER_MODE_REL);
        break;
    // ITIMER_VIRTUAL/PROF 使用 CPU 定时器
}
```

### 4.3 clock_* 系统调用

**源码位置**: `/Users/sphinx/github/linux/kernel/time/posix-timers.c`

**clock_gettime()**:

```c
// posix-timers.c:187-196
static int posix_get_realtime_timespec(clockid_t which_clock, struct timespec64 *tp)
{
    ktime_get_real_ts64(tp);
    return 0;
}

static ktime_t posix_get_realtime_ktime(clockid_t which_clock)
{
    return ktime_get_real();
}
```

**clock_settime()**:

```c
// posix-timers.c:198-202
static int posix_clock_realtime_set(const clockid_t which_clock,
                                    const struct timespec64 *tp)
{
    return do_sys_settimeofday64(tp, NULL);
}
```

**clock_getres()**:

```c
// posix-timers.c:272-277
static int posix_get_hrtimer_res(clockid_t which_clock, struct timespec64 *tp)
{
    tp->tv_sec = 0;
    tp->tv_nsec = hrtimer_resolution;  // 通常为 1ns
    return 0;
}
```

---

## 5. Timekeeping 时间追踪

### 5.1 struct tk_core 时间追踪核心

**源码位置**: `/Users/sphinx/github/linux/kernel/time/timekeeping.c`

**tk_data 结构体**:

```c
// timekeeping.c:52-57
struct tk_data {
    seqcount_raw_spinlock_t	seq;
    struct timekeeper	timekeeper;
    struct timekeeper	shadow_timekeeper;
    raw_spinlock_t		lock;
} ____cacheline_aligned;

static struct tk_data timekeeper_data[TIMEKEEPERS_MAX];

// 核心时间追踪器
#define tk_core (timekeeper_data[TIMEKEEPER_CORE])
```

### 5.2 struct timekeeper

**源码位置**: `/Users/sphinx/github/linux/include/linux/timekeeper_internal.h:140-183`

```c
struct timekeeper {
    /* Cacheline 0 (与 seqcount 一起): */
    struct tk_read_base	tkr_mono;        // CLOCK_MONOTONIC 读取基准

    /* Cacheline 1: */
    u64			xtime_sec;        // CLOCK_REALTIME 秒数
    unsigned long	ktime_sec;        // CLOCK_MONOTONIC 秒数
    struct timespec64	wall_to_monotonic; // 实时到单调的偏移
    ktime_t		offs_real;        // 单调到实时的偏移
    ktime_t		offs_boot;        // 单调到启动的偏移
    union { ktime_t	offs_tai; ktime_t offs_aux; };
    u32			coarse_nsec;      // 粗粒度纳秒
    enum timekeeper_ids	id;              // 时间追踪器 ID

    /* Cacheline 2: */
    struct tk_read_base	tkr_raw;         // 原始时钟读取基准
    u64			raw_sec;          // 原始时钟秒数

    /* Cacheline 3-4 (内部变量): */
    unsigned int	clock_was_set_seq;
    u8			cs_was_changed_seq;
    u8			clock_valid;
    union { struct timespec64 monotonic_to_boot; struct timespec64 monotonic_to_aux; };

    u64			cycle_interval;   // 一个 NTP 周期的时钟周期数
    u64			xtime_interval;   // 一个 NTP 周期的纳秒数
    s64			xtime_remainder;  // 剩余纳秒
    u64			raw_interval;     // 原始周期

    ktime_t		next_leap_ktime;  // 下一次闰秒时间
    u64			ntp_tick;         // NTP tick 长度
    s64			ntp_error;        // NTP 误差
    u32			ntp_error_shift;  // NTP 误差位移
    u32			ntp_err_mult;     // NTP 误差乘数
    u32			skip_second_overflow;
    s32			tai_offset;       // UTC 到 TAI 的偏移
};
```

**tk_read_base** - NMI 安全的快速读取结构:

```c
// include/linux/timekeeper_internal.h:50-59
struct tk_read_base {
    struct clocksource	*clock;       // 当前使用的时钟源
    u64			mask;          // 位掩码
    u64			cycle_last;    // 上次读取的周期值
    u32			mult;          // NTP 调整后的乘数
    u32			shift;         // 位移值
    u64			xtime_nsec;    // 移位后的纳秒偏移
    ktime_t		base;          // 基准时间
    u64			base_real;     // 实时基准
};
```

### 5.3 update_wall_time() 更新墙上时间

**源码位置**: `/Users/sphinx/github/linux/kernel/time/timekeeping.c`

**timekeeping_forward_now()** - 将时间推进到当前:

```c
// timekeeping.c:765-785
static void timekeeping_forward_now(struct timekeeper *tk)
{
    u64 cycle_now, delta;

    cycle_now = tk_clock_read(&tk->tkr_mono);
    delta = clocksource_delta(cycle_now, tk->tkr_mono.cycle_last,
                              tk->tkr_mono.mask, tk->tkr_mono.clock->max_raw_delta);
    tk->tkr_mono.cycle_last = cycle_now;
    tk->tkr_raw.cycle_last  = cycle_now;

    // 更新 xtime_nsec
    while (delta > 0) {
        u64 max = tk->tkr_mono.clock->max_cycles;
        u64 incr = delta < max ? delta : max;

        tk->tkr_mono.xtime_nsec += incr * tk->tkr_mono.mult;
        tk->tkr_raw.xtime_nsec += incr * tk->tkr_raw.mult;
        tk_normalize_xtime(tk);
        delta -= incr;
    }
    tk_update_coarse_nsecs(tk);
}
```

**tk_normalize_xtime()** - 规范化 xtime:

```c
// timekeeping.c:190-200
static inline void tk_normalize_xtime(struct timekeeper *tk)
{
    while (tk->tkr_mono.xtime_nsec >= ((u64)NSEC_PER_SEC << tk->tkr_mono.shift)) {
        tk->tkr_mono.xtime_nsec -= (u64)NSEC_PER_SEC << tk->tkr_mono.shift;
        tk->xtime_sec++;
    }
    // 同样处理 raw
}
```

**快速时间获取函数**:

```c
// timekeeping.c:490-494
u64 ktime_get_mono_fast_ns(void)
{
    return __ktime_get_fast_ns(&tk_fast_mono);
}
EXPORT_SYMBOL_GPL(ktime_get_mono_fast_ns);

// timekeeping.c:502-505
u64 ktime_get_raw_fast_ns(void)
{
    return __ktime_get_fast_ns(&tk_fast_raw);
}
```

### 5.4 时钟源 (Clocksource)

**源码位置**: `/Users/sphinx/github/linux/kernel/time/clocksource.c`

时钟源是提供精确定时的时间源设备:

```c
// include/linux/clocksource.h 中的结构体
struct clocksource {
    u64 (*read)(struct clocksource *cs);     // 读取函数
    u64 mask;                                  // 位掩码
    u32 mult;                                  // 乘数 (cycles to ns)
    u32 shift;                                 // 位移 (ns to cycles)
    u64 max_idle_ns;                          // 最大空闲时间
    u64 max_cycles;                           // 最大周期数
    const char *name;                         // 名称
    struct list_head list;                    // 链表
    u64 cs_last;                              // 上次读取值
    u64 raw_time;                             // 原始时间
    // ...
};
```

---

## 6. 时区处理

### 6.1 sys_tz 时区结构

**源码位置**: `/Users/sphinx/github/linux/kernel/time/time.c`

```c
// time.c:50
struct timezone sys_tz;
EXPORT_SYMBOL(sys_tz);
```

**struct timezone 定义**:

```c
// include/linux/time.h
struct timezone {
    int tz_minuteswest;   // 相对于 UTC 西部的分钟数
    int tz_dsttime;       // 夏令时类型
};
```

### 6.2 do_sys_timezone() 获取时区

**源码位置**: `/Users/sphinx/github/linux/kernel/time/time.c`

实际上,时区通过 gettimeofday 系统调用获取:

```c
// time.c:140-156
SYSCALL_DEFINE2(gettimeofday, struct __kernel_old_timeval __user *, tv,
                struct timezone __user *, tz)
{
    if (likely(tv != NULL)) {
        struct timespec64 ts;
        ktime_get_real_ts64(&ts);
        if (put_user(ts.tv_sec, &tv->tv_sec) ||
            put_user(ts.tv_nsec / 1000, &tv->tv_usec))
            return -EFAULT;
    }
    if (unlikely(tz != NULL)) {
        if (copy_to_user(tz, &sys_tz, sizeof(sys_tz)))
            return -EFAULT;
    }
    return 0;
}
```

### 6.3 settimeofday 设置时间和时区

**源码位置**: `/Users/sphinx/github/linux/kernel/time/time.c:169-197`

```c
int do_sys_settimeofday64(const struct timespec64 *tv, const struct timezone *tz)
{
    static int firsttime = 1;
    int error = 0;

    if (tv && !timespec64_valid_settod(tv))
        return -EINVAL;

    error = security_settime64(tv, tz);
    if (error)
        return error;

    if (tz) {
        // 验证时区范围
        if (tz->tz_minuteswest > 15*60 || tz->tz_minuteswest < -15*60)
            return -EINVAL;

        sys_tz = *tz;                    // 更新系统时区
        update_vsyscall_tz();            // 更新 vsyscall
        if (firsttime) {
            firsttime = 0;
            if (!tv)
                timekeeping_warp_clock();
        }
    }
    if (tv)
        return do_settimeofday64(tv);
    return 0;
}
```

---

## 7. 架构图

### 7.1 时间子系统整体架构

```
+------------------------------------------------------------------+
|                         用户空间                                  |
+------------------------------------------------------------------+
|  clock_gettime()  |  timer_create()  |  gettimeofday()  | alarm()|
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                      系统调用接口 (syscalls)                      |
|  sys_clock_gettime | sys_timer_create | sys_gettimeofday | etc   |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                        Posix Timers 层                           |
|  +------------------+  +------------------+  +------------------+ |
|  |  clock_realtime  |  |  clock_monotonic |  |  clock_tai       | |
|  +------------------+  +------------------+  +------------------+ |
|  | k_itimer (定时器) |  | k_itimer (CPU)   |  | k_itimer (进程)  | |
|  +------------------+  +------------------+  +------------------+ |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                         hrtimer 层                               |
|  +------------------------------------------------------------+  |
|  |  struct hrtimer_cpu_base (per-CPU)                        |  |
|  |  +-------------------------------------------------------+|  |
|  |  | clock_base[HRTIMER_BASE_MONOTONIC]  -> 红黑树         ||  |
|  |  | clock_base[HRTIMER_BASE_REALTIME]   -> 红黑树         ||  |
|  |  | clock_base[HRTIMER_BASE_BOOTTIME]   -> 红黑树         ||  |
|  |  | clock_base[HRTIMER_BASE_TAI]        -> 红黑树         ||  |
|  |  +-------------------------------------------------------+|  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                      Timekeeping 层                             |
|  +------------------------------------------------------------+  |
|  |  struct timekeeper (核心时间追踪)                          |  |
|  |  +------------------------------------------------------+ |  |
|  |  | tkr_mono: CLOCK_MONOTONIC 读取基准                    | |  |
|  |  | tkr_raw:  CLOCK_MONOTONIC_RAW 读取基准                | |  |
|  |  | xtime_sec: 墙上时间(秒)                               | |  |
|  |  | wall_to_monotonic: 实时到单调的偏移                    | |  |
|  |  +------------------------------------------------------+ |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                        Tick 设备层                               |
|  +------------------------------------------------------------+  |
|  |  struct tick_device (per-CPU)                             |  |
|  |  +------------------------------------------------------+ |  |
|  |  | evtdev: clock_event_device (硬件事件设备)             | |  |
|  |  | mode: TICKDEV_MODE_PERIODIC / TICKDEV_MODE_ONESHOT   | |  |
|  |  +------------------------------------------------------+ |  |
|  +------------------------------------------------------------+  |
|  +------------------------------------------------------------+  |
|  |  struct tick_sched (per-CPU)                              |  |
|  |  +------------------------------------------------------+ |  |
|  |  | sched_timer: hrtimer (调度 tick)                      | |  |
|  |  | flags: TS_FLAG_STOPPED, TS_FLAG_NOHZ, TS_FLAG_HIGHRES| |  |
|  |  +------------------------------------------------------+ |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                      硬件/时钟源层                               |
|  +------------------------------------------------------------+  |
|  |  clock_event_device (per-CPU)                             |  |
|  |  +------------------------------------------------------+ |  |
|  |  | Local APIC / Global Timer / HPET / etc                | |  |
|  |  +------------------------------------------------------+ |  |
|  +------------------------------------------------------------+  |
|  +------------------------------------------------------------+  |
|  |  clocksource (全局)                                        |  |
|  |  +------------------------------------------------------+ |  |
|  |  | TSC / jiffies / clocksource_msm / etc                | |  |
|  |  +------------------------------------------------------+ |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

### 7.2 hrtimer 调度流程

```
                    定时器过期
                        |
                        v
        +---------------------------+
        | tick_handle_periodic()    |
        | 或 tick_nohz_handler()     |
        +---------------------------+
                        |
                        v
        +---------------------------+
        | hrtimer_interrupt()      |
        | (硬件中断处理)             |
        +---------------------------+
                        |
                        v
        +---------------------------+
        | __hrtimer_run_queues()   |
        +---------------------------+
                        |
            +-------------+-------------+
            |             |             |
            v             v             v
    +-----------+  +-----------+  +-----------+
    | MONOTONIC |  | REALTIME  |  | BOOTTIME  |
    | 红黑树    |  | 红黑树    |  | 红黑树     |
    +-----------+  +-----------+  +-----------+
            |             |             |
            v             v             v
    +-----------------------------------------+
    |  对每个过期的 hrtimer:                   |
    |    timer->function(timer)               |
    |    返回 HRTIMER_RESTART 或 HRTIMER_NORESTART |
    +-----------------------------------------+
                        |
                        v
        +---------------------------+
        | hrtimer_reprogram()       |
        | (如果需要,重编硬件)        |
        +---------------------------+
```

### 7.3 NTP 调整流程

```
+------------------+
|  second_overflow |
|  (每秒调用一次)   |
+------------------+
        |
        v
+------------------+
|  ntp_update_    |
|  frequency()     |
+------------------+
        |
        v
+------------------+     +------------------+
| 调整 tick_length  | --> | 更新 time_freq   |
| (tick 长度调整)   |     | (频率偏移)       |
+------------------+     +------------------+
        |
        v
+------------------+
|  timekeeping_    |
|  update_tai()    |
+------------------+
        |
        v
+------------------+
|  updateWallTime  |
|  (应用调整到 xtime)|
+------------------+
```

---

## 附录: 关键数据结构关系图

```
jiffies_64 ─────────────────────────────────────> 基础时间单位
    │
    │ tick_next_period (ktime)
    │
    ▼
tick_periodic() ────────────────────────────────> do_timer(1)
    │                                              │
    │                                              v
    │                                        jiffies_64++
    │
    v
update_wall_time() ─────────────────────────────> struct timekeeper
    │                                              │
    │ tkr_mono (tk_read_base)                      │
    │   ├── clock->read() ──────────────────────> clocksource
    │   ├── cycle_last                           │
    │   ├── mult, shift                          │
    │   └── xtime_nsec                           │
    │                                              │
    │ xtime_sec                                   │
    │ wall_to_monotonic ─────────────────────────> CLOCK_MONOTONIC
    │                                              │
    │ offs_real ─────────────────────────────────> CLOCK_REALTIME
    │ offs_boot ────────────────────────────────> CLOCK_BOOTTIME
    │ offs_tai  ─────────────────────────────────> CLOCK_TAI
    │
    v
struct tick_sched ───────────────────────────────> NO_HZ 控制
    │
    ├── sched_timer (hrtimer)
    │       │
    │       v
    │   tick_nohz_handler()
    │
    └── flags: TS_FLAG_STOPPED, TS_FLAG_NOHZ, TS_FLAG_HIGHRES

hrtimer_cpu_base (per-CPU) ────────────────────> 高精度定时器
    │
    ├── lock
    ├── clock_base[8]
    │       │
    │       ├── MONOTONIC ────> 红黑树 (active timers)
    │       ├── REALTIME
    │       ├── BOOTTIME
    │       ├── TAI
    │       └── _SOFT 变体
    │
    └── expires_next ────────────────────────────> 下一个过期时间
```

---

## 参考源码路径

| 组件 | 路径 |
|------|------|
| 核心时间追踪 | `/Users/sphinx/github/linux/kernel/time/timekeeping.c` |
| 时间追踪头文件 | `/Users/sphinx/github/linux/include/linux/timekeeper_internal.h` |
| hrtimer 实现 | `/Users/sphinx/github/linux/kernel/time/hrtimer.c` |
| hrtimer 类型 | `/Users/sphinx/github/linux/include/linux/hrtimer_defs.h` |
| hrtimer 类型 | `/Users/sphinx/github/linux/include/linux/hrtimer_types.h` |
| Tick 调度 | `/Users/sphinx/github/linux/kernel/time/tick-sched.c` |
| Tick 调度头文件 | `/Users/sphinx/github/linux/kernel/time/tick-sched.h` |
| Tick 通用 | `/Users/sphinx/github/linux/kernel/time/tick-common.c` |
| Tick 内部 | `/Users/sphinx/github/linux/kernel/time/tick-internal.h` |
| POSIX 定时器 | `/Users/sphinx/github/linux/kernel/time/posix-timers.c` |
| POSIX 定时器头 | `/Users/sphinx/github/linux/kernel/time/posix-timers.h` |
| itimer | `/Users/sphinx/github/linux/kernel/time/itimer.c` |
| 系统时间调用 | `/Users/sphinx/github/linux/kernel/time/time.c` |
| NTP | `/Users/sphinx/github/linux/kernel/time/ntp.c` |
| NTP 内部 | `/Users/sphinx/github/linux/kernel/time/ntp_internal.h` |
| 时钟源 | `/Users/sphinx/github/linux/kernel/time/clocksource.c` |
| jiffies | `/Users/sphinx/github/linux/include/linux/jiffies.h` |
| 时间头文件 | `/Users/sphinx/github/linux/include/linux/time.h` |

---

*文档生成日期: 2026-04-26*
*内核版本: Linux kernel master branch*
