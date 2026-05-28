# Linux 内核时间子系统深度分析文档 R1

## 目录

1. [Tick Device 子系统](#1-tick-device-子系统)
2. [Clockevent 设备](#2-clockevent-设备)
3. [Timekeeping 核心](#3-timekeeping-核心)
4. [Hrtimer 调度](#4-hrtimer-调度)
5. [Posix Timer 机制](#5-posix-timer-机制)
6. [性能优化](#6-性能优化)

---

## 1. Tick Device 子系统

### 1.1 tick_device 结构详解

**文件位置**: `/Users/sphinx/github/linux/kernel/time/tick-sched.h`

```c
enum tick_device_mode {
    TICKDEV_MODE_PERIODIC,    // 周期模式
    TICKDEV_MODE_ONESHOT,     // 单次触发模式
};

struct tick_device {
    struct clock_event_device *evtdev;  // 指向 clock event 设备
    enum tick_device_mode mode;         // 设备模式
};
```

**关键特性**:
- 每个 CPU 有一个 `tick_device` 实例 (`DEFINE_PER_CPU(struct tick_device, tick_cpu_device)`)
- `evtdev` 指向该 CPU 的时钟事件设备
- `mode` 决定是周期模式还是单次触发模式

### 1.2 tick_sched 结构与动态 tick

**文件位置**: `/Users/sphinx/github/linux/kernel/time/tick-sched.h` 第 33-103 行

```c
struct tick_sched {
    /* 状态标志 - TS_FLAG_* */
    unsigned long           flags;

    /* jiffies 失速检测 */
    unsigned int           stalled_jiffies;
    unsigned long          last_tick_jiffies;

    /* 调度定时器 - 用于 NOHZ 模式 */
    struct hrtimer         sched_timer;    // 周期性 tick 的 hrtimer 模拟
    ktime_t                last_tick;      // 上一次 tick 时间
    ktime_t                next_tick;      // 下一次 tick 时间

    /* Idle 时间统计 */
    unsigned long          idle_jiffies;
    ktime_t                idle_waketime;
    unsigned int           got_idle_tick;

    /* Tick 停止相关 */
    unsigned long          last_jiffies;
    u64                     timer_expires_base;
    u64                     timer_expires;
    u64                     next_timer;
    ktime_t                 idle_expires;

    /* Idle 退出统计 */
    ktime_t                idle_exittime;
    ktime_t                idle_sleeptime;
    ktime_t                iowait_sleeptime;

    /* NOHZ_FULL 支持 */
    atomic_t               tick_dep_mask;  // Tick 依赖掩码

    /* 时钟源变化通知 */
    unsigned long          check_clocks;
};
```

**状态标志 (TS_FLAG_*)**:
```c
#define TS_FLAG_INIDLE       BIT(0)  // CPU 处于 idle 模式
#define TS_FLAG_STOPPED      BIT(1)  // Tick 已停止
#define TS_FLAG_IDLE_ACTIVE BIT(2)  // Idle tick 已激活
#define TS_FLAG_DO_TIMER_LAST BIT(3) // 最后执行 do_timer 的 CPU
#define TS_FLAG_NOHZ        BIT(4)  // NO_HZ 已启用
#define TS_FLAG_HIGHRES     BIT(5)  // 高精度 tick 模式
```

### 1.3 tick_handle_periodic vs tick_handle_periodic_broadcast

**tick_handle_periodic** (`tick-common.c` 第 108-146 行):

```c
void tick_handle_periodic(struct clock_event_device *dev)
{
    int cpu = smp_processor_id();
    ktime_t next = dev->next_event;

    tick_periodic(cpu);  // 处理周期 tick

    // 如果切换到 HIGHRES/NOHZ 模式,直接返回
    if (IS_ENABLED(CONFIG_TICK_ONESHOT) && dev->event_handler != tick_handle_periodic)
        return;

    if (!clockevent_state_oneshot(dev))
        return;

    // Oneshot 模式:重新编程下一个事件
    for (;;) {
        next = ktime_add_ns(next, TICK_NSEC);
        if (!clockevents_program_event(dev, next, false))
            return;
        // 防止硬件时钟源无效导致的无限循环
        if (timekeeping_valid_for_hres())
            tick_periodic(cpu);
    }
}
```

**核心流程**:
1. 调用 `tick_periodic()` 处理周期 tick
2. 检查是否切换到其他模式
3. 在 ONESHOT 模式下循环重新编程

### 1.4 NO_HZ vs HIGH_RES_TICK

**NO_HZ (动态 tick)**:

在 `tick-sched.c` 中实现,核心函数:

```c
// tick-sched.c 第 922-998 行
static ktime_t tick_nohz_next_event(struct tick_sched *ts, int cpu)
{
    u64 basemono, next_tick, delta, expires;
    unsigned long basejiff;
    int tick_cpu;

    basemono = get_jiffies_update(&basejiff);
    ts->last_jiffies = basejiff;
    ts->timer_expires_base = basemono;

    // 检查是否需要保持 tick (RCU、架构、irq_work 请求)
    if (rcu_needs_cpu() || arch_needs_cpu() ||
        irq_work_needs_cpu() || local_timer_softirq_pending()) {
        next_tick = basemono + TICK_NSEC;
    } else {
        // 获取下一个定时器中断时间
        next_tick = get_next_timer_interrupt(basejiff, basemono);
        ts->next_timer = next_tick;
    }

    // 根据 tick 依赖决定是否停止 tick
    delta = next_tick - basemono;
    if (delta <= (u64)TICK_NSEC) {
        if (!tick_sched_flag_test(ts, TS_FLAG_STOPPED)) {
            ts->timer_expires = 0;
            goto out;
        }
    }

    // 限制最大延迟
    delta = timekeeping_max_deferment();
    tick_cpu = READ_ONCE(tick_do_timer_cpu);
    if (tick_cpu != cpu &&
        (tick_cpu != TICK_DO_TIMER_NONE || !tick_sched_flag_test(ts, TS_FLAG_DO_TIMER_LAST)))
        delta = KTIME_MAX;

    // 计算过期时间
    expires = basemono + delta;
    ts->timer_expires = min_t(u64, expires, next_tick);

out:
    return ts->timer_expires;
}
```

**HIGH_RES_TICK (高精度 tick)**:

在 `hrtimer.c` 中实现,核心函数 `hrtimer_switch_to_hres()`:

```c
// hrtimer.c 第 738-753 行
static void hrtimer_switch_to_hres(void)
{
    struct hrtimer_cpu_base *base = this_cpu_ptr(&hrtimer_bases);

    if (tick_init_highres()) {  // 切换到高精度模式
        pr_warn("Could not switch to high resolution mode on CPU %u\n",
                base->cpu);
        return;
    }
    base->hres_active = 1;  // 标记高精度模式活跃
    hrtimer_resolution = HIGH_RES_NSEC;

    tick_setup_sched_timer(true);  // 设置调度定时器
    retrigger_next_event(NULL);    // 重新触发下一个事件
}
```

---

## 2. Clockevent 设备

### 2.1 struct clock_event_device 完整字段

**文件位置**: `/Users/sphinx/github/linux/include/linux/clockchips.h` 第 100-132 行

```c
struct clock_event_device {
    // 事件处理回调
    void            (*event_handler)(struct clock_event_device *);

    // 设置下一个事件的函数指针
    int             (*set_next_event)(unsigned long evt, struct clock_event_device *);
    int             (*set_next_ktime)(ktime_t expires, struct clock_event_device *);

    // 下一个事件时间(ktime 格式)
    ktime_t         next_event;

    // 最小/最大 delta (纳秒)
    u64             max_delta_ns;   // 最大延迟
    u64             min_delta_ns;   // 最小延迟

    // 乘数和移位因子 (用于 scaled math)
    u32             mult;           // 纳秒转 cycles 的乘数
    u32             shift;          // 纳秒转 cycles 的除数 (2^shift)

    // 当前状态
    enum clock_event_state state_use_accessors;

    // 特性标志
    unsigned int    features;

    // 重试计数
    unsigned long   retries;

    // 状态切换回调
    int             (*set_state_periodic)(struct clock_event_device *);
    int             (*set_state_oneshot)(struct clock_event_device *);
    int             (*set_state_oneshot_stopped)(struct clock_event_device *);
    int             (*set_state_shutdown)(struct clock_event_device *);
    int             (*tick_resume)(struct clock_event_device *);

    // 广播函数
    void            (*broadcast)(const struct cpumask *mask);

    // 挂起/恢复回调
    void            (*suspend)(struct clock_event_device *);
    void            (*resume)(struct clock_event_device *);

    // Tick 值范围
    unsigned long   min_delta_ticks;
    unsigned long   max_delta_ticks;

    // 设备信息
    const char      *name;
    int             rating;         // 设备评分,用于选择最佳设备
    int             irq;            // IRQ 号
    int             bound_on;       // 绑定的 CPU
    const struct cpumask *cpumask;  // 支持的 CPU 掩码

    // 链表头
    struct list_head        list;
    struct module          *owner;
};
```

**设备状态枚举** (`clockchips.h` 第 35-41 行):
```c
enum clock_event_state {
    CLOCK_EVT_STATE_DETACHED,      // 未使用
    CLOCK_EVT_STATE_SHUTDOWN,     // 关闭
    CLOCK_EVT_STATE_PERIODIC,     // 周期模式
    CLOCK_EVT_STATE_ONESHOT,      // 单次触发
    CLOCK_EVT_STATE_ONESHOT_STOPPED, // 单次触发已停止
};
```

**设备特性** (`clockchips.h` 第 46-57 行):
```c
#define CLOCK_EVT_FEAT_PERIODIC    0x000001  // 支持周期模式
#define CLOCK_EVT_FEAT_ONESHOT     0x000002  // 支持单次触发
#define CLOCK_EVT_FEAT_KTIME       0x000004  // 支持直接 ktime 设置
#define CLOCK_EVT_FEAT_C3STOP      0x000008  // C3 停止时需要广播
#define CLOCK_EVT_FEAT_DUMMY       0x000010  // 虚拟设备
```

### 2.2 clockevents_register_device() 注册流程

**文件位置**: `/Users/sphinx/github/linux/kernel/time/clockevents.c` 第 451-476 行

```c
void clockevents_register_device(struct clock_event_device *dev)
{
    unsigned long flags;

    // 1. 初始化状态为 DETACHED
    clockevent_set_state(dev, CLOCK_EVT_STATE_DETACHED);

    // 2. 如果没有设置 cpumask,默认为当前 CPU
    if (!dev->cpumask) {
        WARN_ON(num_possible_cpus() > 1);
        dev->cpumask = cpumask_of(smp_processor_id());
    }

    // 3. 防止 cpumask 设置为 cpu_all_mask
    if (dev->cpumask == cpu_all_mask) {
        dev->cpumask = cpu_possible_mask;
    }

    raw_spin_lock_irqsave(&clockevents_lock, flags);

    // 4. 添加到全局设备链表
    list_add(&dev->list, &clockevent_devices);

    // 5. 检查是否可以替换当前 CPU 的 tick 设备
    tick_check_new_device(dev);

    // 6. 处理被释放的设备
    clockevents_notify_released();

    raw_spin_unlock_irqrestore(&clockevents_lock, flags);
}
```

**关键数据结构**:
```c
static LIST_HEAD(clockevent_devices);      // 已注册设备链表
static LIST_HEAD(clockevents_released);    // 已释放设备链表
static DEFINE_RAW_SPINLOCK(clockevents_lock);  // 保护链表
```

### 2.3 tickdev 模式 vs clockevent芯片模式

**tickdev 模式** (Tick Device 模式):
- 由内核软件管理 tick,使用 clockevent 设备的单次触发能力
- 每次到期后重新编程
- 支持 NO_HZ 和动态 tick

**clockevent芯片模式**:
- 硬件自己管理周期中断
- 内核只负责设置周期频率
- 不能动态调整 tick 间隔

---

## 3. Timekeeping 核心

### 3.1 struct timekeeper 完整结构

**文件位置**: `/Users/sphinx/github/linux/include/linux/timekeeper_internal.h` 第 140-183 行

```c
struct timekeeper {
    /* Cacheline 0 (与 seqcount 一起) */
    struct tk_read_base    tkr_mono;        // CLOCK_MONOTONIC 读取基址

    /* Cacheline 1 */
    u64             xtime_sec;              // CLOCK_REALTIME 秒数
    unsigned long   ktime_sec;              // CLOCK_MONOTONIC 秒数
    struct timespec64 wall_to_monotonic;   // Realtime 到 Monotonic 的偏移
    ktime_t         offs_real;             // Monotonic -> Realtime 偏移
    ktime_t         offs_boot;             // Monotonic -> Boottime 偏移
    union {
        ktime_t     offs_tai;               // Monotonic -> TAI 偏移
        ktime_t     offs_aux;               // Monotonic -> AUX 偏移
    };
    u32             coarse_nsec;            // 粗粒度时间纳秒部分
    enum timekeeper_ids id;                // Timekeeper ID

    /* Cacheline 2 */
    struct tk_read_base    tkr_raw;         // CLOCK_MONOTONIC_RAW 读取基址
    u64             raw_sec;                // Raw 时间秒数

    /* Cacheline 3-4 (内部变量) */
    unsigned int    clock_was_set_seq;     // clock_was_set 事件序列号
    u8              cs_was_changed_seq;    // 时钟源变更序列号
    u8              clock_valid;            // 时钟有效标志

    union {
        struct timespec64 monotonic_to_boot;
        struct timespec64 monotonic_to_aux;
    };

    u64             cycle_interval;         // 一个 NTP 周期的时钟周期数
    u64             xtime_interval;         // 一个 NTP 周期的纳秒数(移位后)
    s64             xtime_remainder;        // 剩余未分配的纳秒
    u64             raw_interval;           // Raw 时间间隔

    ktime_t         next_leap_ktime;       // 下一次闰秒时间
    u64             ntp_tick;              // NTP tick 长度
    s64             ntp_error;             // NTP 累积误差
    u32             ntp_error_shift;       // 误差移位转换
    u32             ntp_err_mult;          // 误差乘数
    u32             skip_second_overflow;   // 跳过第二次溢出标志
    s32             tai_offset;            // UTC 到 TAI 的偏移
};
```

**tk_read_base 结构** (`timekeeper_internal.h` 第 50-59 行):
```c
struct tk_read_base {
    struct clocksource  *clock;             // 当前使用的时钟源
    u64                 mask;                // 两补码减法的掩码
    u64                 cycle_last;          // 上次读取的时钟周期值
    u32                 mult;                // (NTP 调整后的)乘数
    u32                 shift;               // 移位值
    u64                 xtime_nsec;          // 移位的纳秒偏移
    ktime_t             base;                // 读取基址(纳秒)
    u64                 base_real;           // CLOCK_REALTIME 的纳秒基址
};
```

### 3.2 tk_core vs timekeeper 关系

**文件位置**: `/Users/sphinx/github/linux/kernel/time/timekeeping.c` 第 52-62 行

```c
struct tk_data {
    seqcount_raw_spinlock_t     seq;           // 序列计数器
    struct timekeeper           timekeeper;     // 主 timekeeper
    struct timekeeper           shadow_timekeeper; // 影子 timekeeper
    raw_spinlock_t              lock;           // 保护锁
} ____cacheline_aligned;

static struct tk_data timekeeper_data[TIMEKEEPERS_MAX];

/* 核心 timekeeper - 全局访问点 */
#define tk_core (timekeeper_data[TIMEKEEPER_CORE])
```

**设计模式 - Shadow Timekeeper**:
1. 所有更新先写入 `shadow_timekeeper`
2. 验证通过后才拷贝到 `timekeeper`
3. 这样读者可以无锁访问 `timekeeper`,写入时才加锁

### 3.3 update_wall_time() 详细流程

**文件位置**: `/Users/sphinx/github/linux/kernel/time/timekeeping.c` 第 2388-2398 行

```c
void update_wall_time(void)
{
    if (timekeeping_advance(TK_ADV_TICK))
        clock_was_set_delayed();
    tk_aux_advance();
}
```

**核心更新流程** (`__timekeeping_advance`, 第 2321-2380 行):

```c
static bool __timekeeping_advance(struct tk_data *tkd, enum timekeeping_adv_mode mode)
{
    struct timekeeper *tk = &tkd->shadow_timekeeper;
    struct timekeeper *real_tk = &tkd->timekeeper;
    unsigned int clock_set = 0;
    int shift = 0, maxshift;
    u64 offset, orig_offset;

    // 如果 timekeeping 已挂起,直接返回
    if (unlikely(timekeeping_suspended))
        return false;

    // 读取当前时钟源周期增量
    offset = clocksource_delta(tk_clock_read(&tk->tkr_mono),
                              tk->tkr_mono.cycle_last, tk->tkr_mono.mask,
                              tk->tkr_mono.clock->max_raw_delta);
    orig_offset = offset;

    // 如果没有超过一个周期,无事可做
    if (offset < real_tk->cycle_interval && mode == TK_ADV_TICK)
        return false;

    // 对数累积 - 一次性累积多个周期
    shift = ilog2(offset) - ilog2(tk->cycle_interval);
    shift = max(0, shift);
    maxshift = (64 - (ilog2(ntp_tick_length(tk->id)) + 1)) - 1;
    shift = min(shift, maxshift);

    while (offset >= tk->cycle_interval) {
        offset = logarithmic_accumulation(tk, offset, shift, &clock_set);
        if (offset < tk->cycle_interval<<shift)
            shift--;
    }

    // 调整乘数以纠正 NTP 误差
    timekeeping_adjust(tk, offset);

    // 确保 xtime_nsec 不超过 NSEC_PER_SEC
    clock_set |= accumulate_nsecs_to_secs(tk);

    // 如果有原始偏移更新,更新粗粒度时钟
    if (orig_offset != offset)
        tk_update_coarse_nsecs(tk);

    // 从 shadow 拷贝到 real timekeeper
    timekeeping_update_from_shadow(tkd, clock_set);

    return !!clock_set;
}
```

### 3.4 NTP 调整机制

**ntp_tick_length** 返回每个 tick 的精确长度,考虑 NTP 调整:

```c
// ntp_internal.h 第 8 行
extern u64 ntp_tick_length(unsigned int tkid);
```

**NTP 调整流程** (`timekeeping_adjust`, 第 2172-2225 行):

```c
static void timekeeping_adjust(struct timekeeper *tk, s64 offset)
{
    u64 ntp_tl = ntp_tick_length(tk->id);
    u32 mult;

    // 从 ntp_tick_length 获取当前的 tick 长度
    if (likely(tk->ntp_tick == ntp_tl)) {
        mult = tk->tkr_mono.mult - tk->ntp_err_mult;
    } else {
        tk->ntp_tick = ntp_tl;
        mult = div64_u64((tk->ntp_tick >> tk->ntp_error_shift) -
                         tk->xtime_remainder, tk->cycle_interval);
    }

    // NTP 误差修正
    tk->ntp_err_mult = tk->ntp_error > 0 ? 1 : 0;
    mult += tk->ntp_err_mult;

    // 应用调整
    timekeeping_apply_adjustment(tk, offset, mult - tk->tkr_mono.mult);
}
```

---

## 4. Hrtimer 调度

### 4.1 hrtimer_cpu_base 层次结构

**文件位置**: `/Users/sphinx/github/linux/include/linux/hrtimer_defs.h` 第 81-107 行

```c
struct hrtimer_cpu_base {
    raw_spinlock_t          lock;           // 保护锁
    unsigned int            cpu;             // CPU 编号
    unsigned int            active_bases;    // 有活跃定时器的基址位域
    unsigned int            clock_was_set_seq; // clock_was_set 序列号

    // 状态标志
    unsigned int            hres_active     : 1,  // 高精度模式活跃
                            in_hrtirq       : 1,  // 正在执行 hrtimer 中断
                            hang_detected   : 1,  // 检测到中断挂起
                            softirq_activated : 1, // 软中断已激活
                            online          : 1;  // CPU 在线

#ifdef CONFIG_HIGH_RES_TIMERS
    unsigned int            nr_events;      // 中断事件总数
    unsigned short          nr_retries;     // 重试次数
    unsigned short          nr_hangs;       // 挂起次数
    unsigned int            max_hang_time;  // 最大挂起时间
#endif

#ifdef CONFIG_PREEMPT_RT
    spinlock_t              softirq_expiry_lock; // 软中断到期锁
    atomic_t                timer_waiters;       // 等待定时器的数量
#endif

    ktime_t                 expires_next;    // 下一个事件时间(绝对时间)
    struct hrtimer          *next_timer;    // 下一个到期的定时器
    ktime_t                 softirq_expires_next; // 软中断下一个到期时间
    struct hrtimer          *softirq_next_timer; // 软中断下一个到期定时器

    struct hrtimer_clock_base clock_base[HRTIMER_MAX_CLOCK_BASES]; // 时钟基址数组
    call_single_data_t      csd;            // 跨 CPU 调用数据
};
```

**hrtimer_clock_base 结构** (`hrtimer_defs.h` 第 26-34 行):
```c
struct hrtimer_clock_base {
    struct hrtimer_cpu_base *cpu_base;      // 指向父 CPU 基址
    unsigned int            index;           // 基址索引
    clockid_t              clockid;         // 时钟 ID
    seqcount_raw_spinlock_t seq;            // 序列计数器
    struct hrtimer         *running;         // 当前运行的定时器
    struct timerqueue_head  active;          // 活跃定时器红黑树
    ktime_t                 offset;         // 到 monotonic 的偏移
};
```

**时钟基址类型** (`hrtimer_defs.h` 第 36-46 行):
```c
enum hrtimer_base_type {
    HRTIMER_BASE_MONOTONIC,      // CLOCK_MONOTONIC
    HRTIMER_BASE_REALTIME,      // CLOCK_REALTIME
    HRTIMER_BASE_BOOTTIME,     // CLOCK_BOOTTIME
    HRTIMER_BASE_TAI,          // CLOCK_TAI
    HRTIMER_BASE_MONOTONIC_SOFT, // CLOCK_MONOTONIC (软中断)
    HRTIMER_BASE_REALTIME_SOFT,  // CLOCK_REALTIME (软中断)
    HRTIMER_BASE_BOOTTIME_SOFT, // CLOCK_BOOTTIME (软中断)
    HRTIMER_BASE_TAI_SOFT,     // CLOCK_TAI (软中断)
    HRTIMER_MAX_CLOCK_BASES,
};
```

### 4.2 红黑树 vs 链表组织

**定时器队列** - 使用 `timerqueue_head` (红黑树):

```c
// 每个 hrtimer_clock_base 有一个 active 队列
struct timerqueue_head {
    struct rb_root_cached   head;  // 红黑树根节点
    struct rb_node          *leftmost; // 最左侧节点(最近到期)
};
```

**定时器节点** - `timerqueue_node`:
```c
struct timerqueue_node {
    struct rb_node          node;   // 红黑树节点
    ktime_t                 expires; // 到期时间
};
```

**hrtimer 结构** (关键字段):
```c
struct hrtimer {
    struct timerqueue_node  node;           // 队列节点(包含 expires)
    ktime_t                 _softexpires;   // 软到期时间
    clockid_t               clock_base->clockid; // 时钟 ID
    enum hrtimer_mode       _sexpires;     // 模式
    const void              *function;     // 回调函数
    // ... 其他字段
};
```

### 4.3 hrtimer_interrupt() 详细流程

**文件位置**: `/Users/sphinx/github/linux/kernel/time/hrtimer.c` (通过 tick 调用)

核心流程在 `__run_hrtimer` 中实现:

```c
// 伪代码表示流程
static void __run_hrtimer(struct hrtimer_cpu_base *base,
                         struct hrtimer_clock_base *clock_base,
                         struct hrtimer *timer,
                         ktime_t *now)
{
    // 1. 标记正在运行
    base->running = timer;

    // 2. 从红黑树中移除
    __remove_hrtimer(timer, clock_base, HRTIMER_STATE_INACTIVE, 0);

    // 3. 清除 ENQUEUED 状态
    timer->state &= ~HRTIMER_STATE_ENQUEUED;

    // 4. 调用回调函数
    fn = timer->function;
    restart = fn(timer);

    // 5. 处理重复定时器
    if (restart != HRTIMER_NORESTART) {
        // 重新入队
        enqueue_hrtimer(timer, clock_base, mode);
    }

    // 6. 清除运行标记
    base->running = NULL;
}
```

### 4.4 定时器迁移 (migration)

**文件位置**: `/Users/sphinx/github/linux/kernel/time/hrtimer.c` 第 250-297 行

```c
static inline struct hrtimer_clock_base *
switch_hrtimer_base(struct hrtimer *timer, struct hrtimer_clock_base *base,
                    int pinned)
{
    struct hrtimer_cpu_base *new_cpu_base, *this_cpu_base;
    struct hrtimer_clock_base *new_base;
    int basenum = base->index;

    this_cpu_base = this_cpu_ptr(&hrtimer_bases);

    // 获取目标 CPU 基址
    new_cpu_base = get_target_base(this_cpu_base, pinned);

new_base = &new_cpu_base->clock_base[basenum];

    if (base != new_base) {
        // 检查定时器是否正在运行
        if (unlikely(hrtimer_callback_running(timer)))
            return base;  // 正在运行,不能迁移

        // 切换到迁移基址
        WRITE_ONCE(timer->base, &migration_base);
        raw_spin_unlock(&base->cpu_base->lock);
        raw_spin_lock(&new_base->cpu_base->lock);

        // 检查目标是否合适
        if (!hrtimer_suitable_target(timer, new_base, new_cpu_base,
                                     this_cpu_base)) {
            raw_spin_unlock(&new_base->cpu_base->lock);
            raw_spin_lock(&base->cpu_base->lock);
            new_cpu_base = this_cpu_base;
            WRITE_ONCE(timer->base, base);
            goto again;
        }
        WRITE_ONCE(timer->base, new_base);
    } else {
        if (!hrtimer_suitable_target(...)) {
            new_cpu_base = this_cpu_base;
            goto again;
        }
    }
    return new_base;
}
```

---

## 5. Posix Timer 机制

### 5.1 struct k_itimer 完整结构

**文件位置**: `/Users/sphinx/github/linux/include/linux/posix-timers.h` 第 186-223 行

```c
struct k_itimer {
    /* 第一个缓存行 - 只读字段 */
    struct hlist_node       t_hash;          // 哈希表节点
    struct hlist_node       list;             // 信号定时器列表节点
    timer_t                 it_id;            // 定时器 ID
    clockid_t               it_clock;        // 时钟类型
    int                     it_sigev_notify; // 信号通知方式
    enum pid_type           it_pid_type;      // PID 类型
    struct signal_struct    *it_signal;      // 所属信号结构
    const struct k_clock    *kclock;         // 时钟处理函数集

    /* 第二个缓存行 - 频繁修改的字段 */
    spinlock_t              it_lock;         // 保护锁
    int                     it_status;        // 定时器状态
    bool                    it_sig_periodic;  // 周期信号标志
    s64                     it_overrun;       // 超限计数
    s64                     it_overrun_last;  // 上次超限计数
    unsigned int            it_signal_seq;    // 信号序列号
    unsigned int            it_sigqueue_seq;  // sigqueue 序列号
    ktime_t                 it_interval;     // 间隔时间

    struct hlist_node       ignored_list;     // 被忽略的定时器列表
    union {
        struct pid           *it_pid;         // 目标进程 PID
        struct task_struct   *it_process;     // 目标任务
    };
    struct sigqueue         sigq;             // 内嵌的 sigqueue
    rcuref_t                rcuref;          // 引用计数

    union {
        struct {
            struct hrtimer  timer;           // 实时定时器
        } real;
        struct cpu_timer      cpu;            // CPU 定时器
        struct {
            struct alarm    alarmtimer;      // 闹钟定时器
        } alarm;
    } it;

    struct rcu_head         rcu;               // RCU 头
};
```

**定时器状态**:
```c
enum {
    POSIX_TIMER_DISARMED,       // 已 disarm
    POSIX_TIMER_ARMED,           // 已激活
    POSIX_TIMER_REQUEUE_PENDING, // 等待重新排队
};
```

### 5.2 ITIMER_REAL vs ITIMER_VIRTUAL vs ITIMER_PROF

这些通过 `struct cpu_timer` 实现:

```c
struct cpu_timer {
    struct timerqueue_node    node;           // 定时器队列节点
    struct timerqueue_head    *head;           // 所属队列头
    struct pid                *pid;           // 目标 PID
    struct list_head          elist;          // 到期列表
    bool                      firing;         // 正在触发
    bool                      nanosleep;      // 用于 nanosleep
    struct task_struct __rcu *handling;       // 处理定时器的任务
};
```

**ITIMER_REAL** (`ITIMER_REAL`):
- 使用 `k_itimer.it.real.timer` (hrtimer)
- 基于 `CLOCK_REALTIME`
- 到期发送 `SIGALRM`

**ITIMER_VIRTUAL** (`ITIMER_VIRTUAL`):
- 使用 `cpu_timer` 结构
- 基于 `CLOCK_PROCESS_CPUTIME_ID`
- 只计算进程用户态时间
- 到期发送 `SIGVTALRM`

**ITIMER_PROF** (`ITIMER_PROF`):
- 使用 `cpu_timer` 结构
- 基于 `CLOCK_PROCESS_CPUTIME_ID`
- 计算进程用户态和内核态时间
- 到期发送 `SIGPROF`

### 5.3 timer_create() syscall 流程

**文件位置**: `/Users/sphinx/github/linux/kernel/time/posix-timers.c` 第 566-578 行

```c
SYSCALL_DEFINE3(timer_create, const clockid_t, which_clock,
                struct sigevent __user *, timer_event_spec,
                timer_t __user *, created_timer_id)
{
    if (timer_event_spec) {
        sigevent_t event;
        if (copy_from_user(&event, timer_event_spec, sizeof(event)))
            return -EFAULT;
        return do_timer_create(which_clock, &event, created_timer_id);
    }
    return do_timer_create(which_clock, NULL, created_timer_id);
}
```

**do_timer_create** 流程 (`posix-timers.c` 第 458-564 行):

```c
static int do_timer_create(clockid_t which_clock, struct sigevent *event,
                           timer_t __user *created_timer_id)
{
    const struct k_clock *kc = clockid_to_kclock(which_clock);
    struct k_itimer *new_timer;
    int error, new_timer_id;

    // 1. 分配定时器结构
    new_timer = alloc_posix_timer();
    if (!new_timer)
        return -EAGAIN;

    spin_lock_init(&new_timer->it_lock);

    // 2. 添加到哈希表
    new_timer_id = posix_timer_add(new_timer, TIMER_ANY_ID);
    if (new_timer_id < 0) {
        posixtimer_free_timer(new_timer);
        return new_timer_id;
    }

    // 3. 初始化定时器字段
    new_timer->it_clock = which_clock;
    new_timer->kclock = kc;
    new_timer->it_overrun = -1LL;

    // 4. 设置信号通知
    if (event) {
        new_timer->it_pid = get_pid(good_sigevent(event));
        new_timer->it_sigev_notify = event->sigev_notify;
        // ... 设置 sigq info
    } else {
        new_timer->it_sigev_notify = SIGEV_SIGNAL;
        // ... 默认设置
    }

    // 5. 拷贝 timer_id 到用户空间
    if (copy_to_user(created_timer_id, &new_timer_id, sizeof(new_timer_id))) {
        error = -EFAULT;
        goto out;
    }

    // 6. 调用时钟特定的创建回调
    error = kc->timer_create(new_timer);
    if (error)
        goto out;

    // 7. 完成初始化,设置 it_signal
    scoped_guard (spinlock_irq, &new_timer->it_lock) {
        guard(spinlock)(&current->sighand->siglock);
        WRITE_ONCE(new_timer->it_signal, current->signal);
        hlist_add_head_rcu(&new_timer->list, &current->signal->posix_timers);
    }

    return 0;
out:
    posix_timer_unhash_and_free(new_timer);
    return error;
}
```

### 5.4 信号派发机制

**定时器到期处理** (`posix-timers.c` 第 367-374 行):

```c
static enum hrtimer_restart posix_timer_fn(struct hrtimer *timer)
{
    struct k_itimer *timr = container_of(timer, struct k_itimer, it.real.timer);

    guard(spinlock_irqsave)(&timr->it_lock);
    posix_timer_queue_signal(timr);
    return HRTIMER_NORESTART;
}
```

**信号队列函数** (`posix-timers.c` 第 349-358 行):

```c
void posix_timer_queue_signal(struct k_itimer *timr)
{
    lockdep_assert_held(&timr->it_lock);

    if (!posixtimer_valid(timr))
        return;

    timr->it_status = timr->it_interval ?
                       POSIX_TIMER_REQUEUE_PENDING : POSIX_TIMER_DISARMED;
    posixtimer_send_sigqueue(timr);
}
```

---

## 6. 性能优化

### 6.1 时间戳缓存

**tk_fast - NMI 安全的时间读取** (`timekeeping.c` 第 96-107 行):

```c
struct tk_fast {
    seqcount_latch_t    seq;      // 序列计数器(闩锁)
    struct tk_read_base base[2];  // 双缓冲区
};
```

**Latch 技术** - 避免 NMI 中读取不一致:

```c
static void update_fast_timekeeper(const struct tk_read_base *tkr,
                                  struct tk_fast *tkf)
{
    struct tk_read_base *base = tkf->base;

    // 强制读者使用 base[1]
    write_seqcount_latch_begin(&tkf->seq);

    // 更新 base[0]
    memcpy(base, tkr, sizeof(*base));

    // 强制读者使用 base[0]
    write_seqcount_latch(&tkf->seq);

    // 更新 base[1]
    memcpy(base + 1, base, sizeof(*base));

    write_seqcount_latch_end(&tkf->seq);
}
```

**快速读取函数** (`timekeeping.c` 第 442-456 行):

```c
static __always_inline u64 __ktime_get_fast_ns(struct tk_fast *tkf)
{
    struct tk_read_base *tkr;
    unsigned int seq;
    u64 now;

    do {
        seq = read_seqcount_latch(&tkf->seq);
        tkr = tkf->base + (seq & 0x01);
        now = ktime_to_ns(tkr->base);
        now += timekeeping_get_ns(tkr);
    } while (read_seqcount_latch_retry(&tkf->seq, seq));

    return now;
}
```

### 6.2 批量处理

**logarithmic_accumulation** - 对数累积 (`timekeeping.c` 第 2283-2315 行):

```c
static u64 logarithmic_accumulation(struct timekeeper *tk, u64 offset,
                                    u32 shift, unsigned int *clock_set)
{
    u64 interval = tk->cycle_interval << shift;
    u64 snsec_per_sec;

    if (offset < interval)
        return offset;

    // 累积一个移位间隔
    offset -= interval;
    tk->tkr_mono.cycle_last += interval;
    tk->tkr_raw.cycle_last  += interval;

    tk->tkr_mono.xtime_nsec += tk->xtime_interval << shift;
    *clock_set |= accumulate_nsecs_to_secs(tk);

    // 累积原始时间
    tk->tkr_raw.xtime_nsec += tk->raw_interval << shift;
    // ...

    return offset;
}
```

### 6.3 RCU 在 timekeeping 中的应用

**定时器哈希表** (`posix-timers.c` 第 42-55 行):

```c
struct timer_hash_bucket {
    spinlock_t          lock;
    struct hlist_head   head;
};

static struct {
    struct timer_hash_bucket *buckets;
    unsigned long       mask;
    struct kmem_cache   *cache;
} __timer_data;
```

**RCU 保护的查找** (`posix-timers.c` 第 89-101 行):

```c
static struct k_itimer *posix_timer_by_id(timer_t id)
{
    struct signal_struct *sig = current->signal;
    struct timer_hash_bucket *bucket = hash_bucket(sig, id);
    struct k_itimer *timer;

    hlist_for_each_entry_rcu(timer, &bucket->head, t_hash) {
        if ((READ_ONCE(timer->it_signal) == sig) && (timer->it_id == id))
            return timer;
    }
    return NULL;
}
```

**定时器释放使用 RCU** (`posix-timers.c` 第 439 行):

```c
void posixtimer_free_timer(struct k_itimer *tmr)
{
    put_pid(tmr->it_pid);
    if (tmr->sigq.ucounts)
        dec_rlimit_put_ucounts(tmr->sigq.ucounts, UCOUNT_RLIMIT_SIGPENDING);
    kfree_rcu(tmr, rcu);  // RCU 延迟释放
}
```

---

## 数据结构关系图

```
+------------------+     +---------------------+
| tick_device      |     | clock_event_device  |
+------------------+     +---------------------+
| evtdev    -------+---->| event_handler       |
| mode            |     | set_next_event      |
+------------------+     | next_event         |
                         | mult/shift         |
                         | features           |
                         +---------------------+
                                ^
                                |
                    tick_check_new_device()
                                |
                         +---------------------+
                         | tick_sched          |
                         +---------------------+
                         | sched_timer (hrtimer)
                         | flags               |
                         | idle_jiffies       |
                         +---------------------+
                                ^
                                |
                    tick_nohz_next_event()
                                |
                         +---------------------+
                         | timekeeper          |
                         +---------------------+
                         | tkr_mono           |
                         | xtime_sec          |
                         | wall_to_monotonic  |
                         | offs_real/boot/tai|
                         | ntp_tick           |
                         +---------------------+
                                ^
                                |
                         update_wall_time()
                                |
                         +---------------------+
                         | clocksource         |
                         +---------------------+
```

---

## 关键算法流程图

### tick 周期处理流程

```
tick_handle_periodic()
        |
        v
tick_periodic(cpu)
        |
        +-- do_timer(1)  ---> update_wall_time()
        |                       |
        |                       v
        |                 __timekeeping_advance()
        |                       |
        |                       v
        |                 logarithmic_accumulation()
        |                       |
        |                       v
        |                 timekeeping_adjust()
        |                       |
        |                       v
        |                 accumulate_nsecs_to_secs()
        |
        +-- update_process_times()
        |         |
        |         v
        +-- profile_tick()
```

### hrtimer 中断处理流程

```
hrtimer_interrupt()
        |
        v
__run_hrtimer()
        |
        +-- 1. __remove_hrtimer() - 从红黑树移除
        |
        +-- 2. 调用回调函数 fn(timer)
        |
        +-- 3. 如果返回 HRTIMER_RESTART,重新入队
        |
        v
hrtimer_force_reprogram()
        |
        v
__hrtimer_reprogram()
        |
        v
tick_program_event()
```

---

## 参考文件列表

| 文件 | 描述 |
|------|------|
| `kernel/time/tick-common.c` | Tick 设备基础管理 |
| `kernel/time/tick-sched.c` | NO_HZ 和动态 tick 实现 |
| `kernel/time/tick-sched.h` | tick_sched 结构定义 |
| `kernel/time/clockevents.c` | Clockevent 设备管理 |
| `kernel/time/timekeeping.c` | Timekeeping 核心实现 |
| `kernel/time/timekeeping.h` | timekeeping 内部接口 |
| `include/linux/timekeeper_internal.h` | timekeeper 结构定义 |
| `kernel/time/hrtimer.c` | Hrtimer 实现 |
| `include/linux/hrtimer_defs.h` | hrtimer 核心结构定义 |
| `kernel/time/posix-timers.c` | POSIX 定时器实现 |
| `include/linux/posix-timers.h` | k_itimer 结构定义 |
| `include/linux/clockchips.h` | clock_event_device 定义 |

---

*文档版本: R1*
*生成日期: 2026-04-26*
