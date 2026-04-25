# Linux 时间管理系统深度架构分析 v2

## 1. 概述

本文档是 Linux 时间管理系统的第二轮深度分析，重点关注 NTP 时间同步算法、时间源选择机制、高分辨率定时器（hrtimer）的红黑树实现、时钟事件框架、以及 vDSO 加速等核心实现细节。

## 2. 时间源（Clocksource）深入

### 2.1 时间源架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Clocksource Architecture                            │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Clocksource Registry (clocksource_list)          │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │  │
│  │  │   TSC   │ │  HPET   │ │  ACPI   │ │ ARM CPS │           │  │
│  │  │ (x86)   │ │ (legacy)│ │ PM Timer │ │  arch   │           │  │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │  │
│  └───────┼───────────┼───────────┼───────────┼───────────────────┘  │
│          │           │           │           │                          │
│          └───────────┴─────┬─────┴───────────┘                          │
│                            │                                           │
│                            ▼                                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │          cur_clocksource (当前最佳时间源)                        │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  cs->read() → cycles_to_ns() → nanoseconds           │  │  │
│  │  │  Rating system: TSC(350) > HPET(250) > ACPI(200)     │  │  │
│  │  └───────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Cycle 到 Nanosecond 转换

```c
/**
 * cycle_to_nsec_safe - 安全转换（处理溢出）
 *
 * 使用 128 位中间结果避免 64 位溢出
 */
static inline u64 cycle_to_nsec_safe(u64 cycles, u32 mult, u32 shift,
                                    u64 max_cycles)
{
    u64 max_ns = (u64)U64_MAX / mult;
    u64 ns, tmp;

    if (likely(cycles < max_cycles))
        return (cycles * mult) >> shift;

    /* 溢出处理：分段计算 */
    ns = max_cycles * mult >> shift;
    cycles -= max_cycles;
    tmp = cycles * mult >> shift;
    if (ns > (u64)-1 - tmp)  /* overflow check */
        return ns + tmp + (max_cycles - cycles) * mult >> shift;
    return ns + tmp;
}

/**
 * clocksource_delta - 计算两次读取的差值
 *
 * 处理计数器回绕（wraparound）
 */
static inline u64 clocksource_delta(u64 t1, u64 t0, u64 mask)
{
    return (t1 - t0) & mask;
}
```

### 2.3 时间源选择算法

```c
/**
 * __clocksource_register_scale - 注册新的时间源
 *
 * 选择标准：
 * 1. rating 越高越优先
 * 2. 相同 rating 选择精度更高的
 */
int __clocksource_register_scale(struct clocksource *cs, u32 scale, u32 freq)
{
    /* 计算 mult 和 shift */
    clocksource_compute_mult(cs, freq, MAX_FREQ);
    cs->max_idle_ns = clocksource_max_deferment(cs);

    /* 加入全局链表 */
    mutex_lock(&clocksource_mutex);
    list_add(&cs->list, &clocksource_list);

    /* 可能需要选择新的时间源 */
    clocksource_select(false);
    mutex_unlock(&clocksource_mutex);
    return 0;
}

/**
 * clocksource_select - 选择最佳时间源
 *
 * 算法：遍历所有注册的时间源，选择 rating 最高的
 */
static void clocksource_select(bool force)
{
    struct clocksource *cs, *best = cur_clocksource;

    list_for_each_entry(cs, &clocksource_list, list) {
        if (cs->rating > best->rating)
            best = cs;
    }

    if (best != cur_clocksource || force) {
        cur_clocksource = best;
        /* 通知注册表更新 */
        clocksource_update_fallback_cs();
    }
}
```

## 3. Timekeeping 深入

### 3.1 双缓冲序列计数

```c
/**
 * tk_read_base - 时间读取基准结构
 *
 * 使用序列计数实现无锁读取（double buffering）
 */
struct tk_read_base {
    cycle_t cycle_last;          // 上次更新的周期值
    u64 mask;                   // 掩码
    u32 mult;                   // 乘数
    u32 shift;                 // 移位
    u64 xtime_nsec;            // 纳秒累计（用于生成 xtime）
    u64 base_ns;               // 基础纳秒值
};

/**
 * tk_fast - 快速读取结构
 *
 * 读取时使用 seqcount_latch：
 * - 写入线程更新 base[0]，然后更新序列号
 * - 写入线程更新 base[1]，然后更新序列号
 * - 读取线程读取序列号，然后读取对应的 base
 * - 读取线程再次检查序列号，如果变了就重试
 */
struct tk_fast {
    seqcount_latch_t    seq;
    struct tk_read_base base[2];
};

/**
 * ktime_get_fast_ns - 快速获取单调时间
 *
 * NMI 安全实现
 */
static inline u64 ktime_get_fast_ns(void)
{
    struct tk_fast *tkf = &tk_fast_mono;
    struct tk_read_base *base;
    unsigned int seq;
    u64 now;

    do {
        seq = raw_read_seqcount_latch(&tkf->seq);
        base = &tkf->base[seq & 1];

        /* 计算当前时间 */
        now = base->base_ns;
        now += clocksource_delta(current_clocksource(),
                               base->cycle_last,
                               base->mask) * base->mult >> base->shift;
    } while (read_seqcount_latch_retry(&tkf->seq, seq));

    return now;
}
```

### 3.2 NTP 时间调整

```c
/**
 * ntp_tick_length - 获取 NTP tick 长度
 *
 * NTP 调整后的真实 tick 长度
 */
static inline s64 ntp_tick_length(void)
{
    return ntpinterval + ntpphase;
}

/**
 * second_overflow - 秒进位处理
 *
 * 每秒调用一次，处理：
 * 1. NTP 频率调整累积
 * 2. 时间溢出处理
 */
static void second_overflow(struct timekeeper *tk)
{
    s64 nsec, remainder;

    /* 累加一秒的纳秒数 */
    nsec = tk->tkr_mono.xtime_nsec;

    /* 添加 NTP 调整 */
    nsec += ntp_tick_length();

    /* 处理进位 */
    while (nsec >= (NSEC_PER_SEC << tk->tkr_mono.shift)) {
        nsec -= NSEC_PER_SEC << tk->tkr_mono.shift;
        tk->seconds++;
    }

    /* 检查是否需要同步 xtime */
    if (unlikely(tk->xtime.tv_sec != tk->seconds)) {
        tk->xtime.tv_sec = tk->seconds;
        tk->xtime.tv_nsec = nsec >> tk->tkr_mono.shift;
    }

    /* 更新 monotonic 时间 */
    tk->wall_to_monotonic.tv_sec = tk->wall_to_monotonic.tv_sec;
}
```

### 3.3 时间更新流程

```c
/**
 * update_wall_time - 更新墙上时间
 *
 * 在每个时钟滴答调用
 * 更新 tk_core 结构
 */
void update_wall_time(void)
{
    struct timekeeper *tk = &tk_core;
    cycle_t offset;
    int shift = tk->tkr_mono.shift;
    unsigned long flags;

    write_seqlock_irqsave(&tk->lock, flags);

    /* 读取当前周期数 */
    offset = clocksource_delta(
        clocksource_read(tk->clock),
        tk->tkr_mono.cycle_last,
        tk->tkr_mono.mask);

    /* 转换为纳秒并累加 */
    tk->tkr_mono.xtime_nsec += offset * tk->tkr_mono.mult;

    /* 处理进位 */
    while (tk->tkr_mono.xtime_nsec >=
           (NSEC_PER_SEC << shift)) {
        tk->tkr_mono.xtime_nsec -= NSEC_PER_SEC << shift;
        tk->seconds++;
    }

    /* 更新 xtime 和其他时间 */
    second_overflow(tk);

    /* 更新快速读取缓存 */
    update_fast_timekeeper(tk, &tk_fast_mono, tk->tkr_mono);
    update_fast_timekeeper(tk, &tk_fast_raw, tk->tkr_raw);

    write_sequnlock_irqrestore(&tk->lock, flags);
}
```

## 4. 高分辨率定时器（hrtimer）

### 4.1 hrtimer 架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    hrtimer Architecture                                │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              per-cpu hrtimer_bases                            │  │
│  │                                                               │  │
│  │  ┌──────────────────┐    ┌──────────────────┐                │  │
│  │  │ hrtimer_base    │    │ hrtimer_base    │                │  │
│  │  │ (CLOCK_REALTIME)│    │ (CLOCK_MONOTONIC)│                │  │
│  │  │                 │    │                 │                │  │
│  │  │  cpu_base.rb    │    │  cpu_base.rb    │                │  │
│  │  │   (红黑树)      │    │   (红黑树)      │                │  │
│  │  │                 │    │                 │                │  │
│  │  │  expires_next   │    │  expires_next   │                │  │
│  │  └──────────────────┘    └──────────────────┘                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Red-Black Tree                              │  │
│  │                                                               │  │
│  │         expires (绝对时间，按顺序排列)                         │  │
│  │                                                               │  │
│  │              ┌───┐                                           │  │
│  │           ┌──┤300├──┐                                        │  │
│  │           │  └───┘  │  │                                        │  │
│  │        ┌──┤500├──┐ └──┤800├──┐                               │  │
│  │        │  └───┘  │    │  └───┘  │                               │  │
│  │     ┌──┤600├──┐  │    │       └──┤900├──┐                      │  │
│  │     │  └───┘  │  │    │          └───┘  │                      │  │
│  └─────┴─────────┴──┴────────────────────┴────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 hrtimer 数据结构

```c
/**
 * hrtimer - 高分辨率定时器
 */
struct hrtimer {
    struct timerqueue_node   node;      // 红黑树节点
    ktime_t                 expires;    // 过期时间（绝对时间）
    ktime_t                 softexpires; // 软过期时间（允许提前一点触发）
    enum hrtimer_restart (*function)(struct hrtimer *);
    struct hrtimer_clock_base *base;
    u8                      state;
    u8                      is_rel;
    u8                      is_soft;
    u8                      is_hard;
};

/**
 * hrtimer_clock_base - 每 CPU 每 clockid 的定时器基准
 */
struct hrtimer_clock_base {
    struct hrtimer_cpu_base *cpu_base;
    clockid_t               clockid;
    struct timerqueue_head  active;
    ktime_t                 expires_next;  // 下一个过期时间
    ktime_t                 offset;        // 与单调时间的偏移
};

/**
 * hrtimer_cpu_base - 每 CPU 的定时器基准
 */
struct hrtimer_cpu_base {
    raw_spinlock_t          lock;
    unsigned int            cpu;
    unsigned int            active_bases;
    unsigned int            nr_events;
    unsigned long           expires_next;  // 全局下一个过期时间
    struct hrtimer_clock_base clock_base[HRTIMER_MAX_CLOCK_BASES];
};
```

### 4.3 定时器入队算法

```c
/**
 * __hrtimer_start_range_ns - 启动定时器
 *
 * 1. 计算绝对过期时间
 * 2. 插入红黑树（按过期时间排序）
 * 3. 如果是最近的定时器，更新基准的 expires_next
 * 4. 如果需要，重新编程硬件定时器
 */
void __hrtimer_start_range_ns(struct hrtimer *timer,
                             ktime_t tim, u64 delta_ns,
                             const enum hrtimer_mode mode,
                             bool wakeup)
{
    struct hrtimer_clock_base *base;
    struct hrtimer_cpu_base *cpu_base;
    unsigned long flags;

    base = lock_hrtimer_base(timer, &flags);

    /* 转换为绝对时间 */
    tim = hrtimer_expires_remaining(timer, tim, mode);

    /* 插入红黑树 */
    timerqueue_add(&base->active, &timer->node);

    /* 更新基准的 expires_next */
    if (!base->cpu_base->active_bases ||
        tim < hrtimer_get_expires_first(base))
        hrtimer_update_next_timer(base);

    raw_spin_unlock_irqrestore(&cpu_base->lock, flags);

    /* 重新编程硬件定时器 */
    if (wakeup)
        hrtimer_reprogram(timer, base);
}

/**
 * timerqueue_add - 插入到红黑树
 *
 * 树按过期时间排序，最早过期的在最左边
 */
static bool timerqueue_add(struct timerqueue_head *head,
                          struct timerqueue_node *node)
{
    struct timerqueue_node *p;
    struct timerqueue_head *h = head;

    /* 找到插入位置 */
    p = rb_prev(&node->node);
    if (p && timerqueue_iterates_right(p, node, &h->head))
        p = rb_next(p);

    if (p) {
        if (p->next == NULL)
            h->head.rb_right = &node->node;
        else
            p->next = &node->node;
        node->next = NULL;
    } else {
        h->head.rb_left = &node->node;
        node->next = h->head.rb_left;
        h->head.rb_left = NULL;
    }

    rb_insert_color_cached(&node->node, &h->head, p == NULL);
    return true;
}
```

### 4.4 定时器到期处理

```c
/**
 * __hrtimer_run_queues - 运行到期的定时器
 *
 * 在时钟中断或 hrtimer softirq 中调用
 */
void __hrtimer_run_queues(struct hrtimer_cpu_base *cpu_base,
                          ktime_t now)
{
    struct timerqueue_node *node;
    struct hrtimer_clock_base *base;

    /* 遍历所有激活的基准 */
    for (each_active_base(base, cpu_base)) {
        /* 检查是否有到期的定时器 */
        if (!timerqueue_iterates(&base->active, node, now))
            continue;

        /* 运行到期的定时器 */
        while (node && ktime_before(node->expires, now)) {
            struct hrtimer *timer;

            timer = container_of(node, struct hrtimer, node);

            /* 移除定时器 */
            timerqueue_del(&base->active, node);

            /* 清除状态 */
            hrtimer_set_state(timer, HRTIMER_STATE_CALLBACK);

            /* 调用回调 */
            restart = timer->function(timer);

            /* 处理重启动 */
            if (restart != HRTIMER_NORESTART)
                hrtimer_reprogram(timer, base);
        }
    }
}

/**
 * hrtimer_interrupt - 硬件定时器中断处理
 *
 * 读取硬件计时器，确定到期时间，重新编程
 */
void hrtimer_interrupt(struct clock_event_device *dev)
{
    struct hrtimer_cpu_base *cpu_base = this_cpu_ptr(&hrtimer_bases);
    ktime_t expires_next, now;
    int nr_retries;
    int nr_expires;

    raw_spin_lock(&cpu_base->lock);

    /* 读取当前时间 */
    now = tick programmable ? clockevents_device.read() : ktime_get();

    expires_next = cpu_base->expires_next;

    /* 运行到期的定时器 */
    nr_retries = 0;
    do {
        __hrtimer_run_queues(cpu_base, now);
        now = ktime_get();
        nr_retries++;
    } while (ktime_before(now, expires_next) && nr_retries < 10);

    /* 重新编程下一次中断 */
    if (expires_next > now)
        clockevents_program_event(expires_next);
    else
        tick_program_event(now, 1);

    raw_spin_unlock(&cpu_base->lock);
}
```

## 5. 时钟事件框架

### 5.1 clockevent 设备

```c
/**
 * clock_event_device - 时钟事件设备
 *
 * 提供定时器中断功能
 */
struct clock_event_device {
    const char          *name;
    unsigned int        features;
    unsigned long       min_delta_ns;
    unsigned long       max_delta_ns;
    unsigned long       mult;
    unsigned long       shift;
    void               (*set_mode)(enum clock_event_mode mode,
                                   struct clock_event_device *);
    int                (*set_next_event)(unsigned long evt,
                                        struct clock_event_device *);
    ktime_t            (*get_cycles)(void);
    void               (*broadcast)(const struct cpumask *mask);
    struct list_head   list;
    enum clock_event_mode  mode;
    struct clock_event_device *(*dev);
    int                    rating;
    int                    irq;
    int                    cpu;
    struct timerqueue_head   cpumask;
};
```

### 5.2 动态时钟事件

```c
/**
 * tick_check_new_device - 检查新设备
 *
 * 决定是否使用新的时钟事件设备
 */
int tick_check_new_device(struct clock_event_device *newdev)
{
    struct clock_event_device *curdev;
    struct tick_device *td;

    td = &per_cpu(tick_cpu_device, newdev->cpu);
    curdev = td->evtdev;

    /* 决定是否切换设备 */
    if (!tick_check_percpu(curdev, newdev))
        return NOTIFY_DONE;

    /* 比较 rating */
    if (curdev && curdev->rating >= newdev->rating)
        return NOTIFY_DONE;

    /* 注册新设备 */
    clockevents_exchange_device(curdev, newdev);
    tick_setup_device(td, newdev, newdev->cpu);

    return NOTIFY_STOP;
}

/**
 * tick_setup_device - 设置时钟事件设备
 */
void tick_setup_device(struct tick_device *td,
                      struct clock_event_device *newdev,
                      int cpu)
{
    /* 设置模式回调 */
    newdev->mode = CLOCK_EVT_MODE_SHUTDOWN;

    if (td->mode == CLOCK_EVT_MODE_PERIODIC)
        tick_setup_periodic(newdev, 0);
    else
        tick_setup_oneshot(newdev);
}
```

## 6. vDSO 时间接口

### 6.1 vDSO 概述

```
┌─────────────────────────────────────────────────────────────────────┐
│                    vDSO Time Interface                               │
│                                                                      │
│  用户空间                                                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  clock_gettime(CLOCK_REALTIME) → vsyscall → vDSO            │  │
│  │  gettimeofday() → vDSO                                       │  │
│  │  time() → vDSO                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  内核空间                                                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  vdso_data (共享内存)                                         │  │
│  │  - cycle_last, mask, mult, shift (用于计算)                  │  │
│  │  - xtime_sec, xtime_nsec (墙上时间)                         │  │
│  │  - seq (序列号，用于无锁读取)                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 vDSO 数据结构

```c
/**
 * vdso_data - vDSO 共享数据
 *
 * 通过 vsyscall/vDSO 映射到用户空间
 */
struct vdso_data {
    u32 seq;                    // 序列号（用于无锁读取）
    s64 clock_mode;             // 时钟模式
    u64 cycle_last;            // 上次读取的周期数
    u64 mask;                   // 掩码
    u32 mult;                   // 乘数
    u32 shift;                  // 移位
    /*墙上时间*/
    u64 xtime_sec;             // 秒
    u64 xtime_nsec;            // 纳秒
    u64 wall_to_mono_sec;      // 墙上到单调的偏移
    u64 monotonic_sec;          // 单调时间秒
    u64 monotonic_nsec;         // 单调时间纳秒
};

/**
 * __vdso_clock_gettime - vDSO 实现
 *
 * 在用户空间执行，无系统调用开销
 */
static __always_inline notrace u64
__vdso_clock_gettime(clockid_t clock)
{
    const struct vdso_data *vd = __arch_get_vdso_data();
    u64 cycles, last, mask, mult, shift;
    u32 seq;
    u64 ns;

    /* 无锁读取 */
    do {
        seq = READ_ONCE(vd->seq);
        cycles = __arch_get_hw_counter(vd->clock_mode);
        last = vd->cycle_last;
        mask = vd->mask;
        mult = vd->mult;
        shift = vd->shift;
        ns = vd->xtime_nsec;
    } while (unlikely(READ_ONCE(vd->seq) != seq));

    /* 计算时间增量 */
    ns += (cycles - last) * mult >> shift;

    return ns;
}
```

## 7. 定时器wheel（低分辨率定时器）

### 7.1 定时器wheel结构

```c
/*
 * 定时器 wheel 使用 5 级链表数组：
 * 每一级覆盖不同的时间范围
 *
 * TV1 (bits 0-4): 256 个桶，每个 1 jiffy
 * TV2 (bits 5-7): 64 个桶，每个 256 jiffies
 * TV3 (bits 8-10): 64 个桶，每个 16K jiffies
 * TV4 (bits 11-13): 64 个桶，每个 1M jiffies
 * TV5 (bits 14+): 64 个桶，每个 64M jiffies
 *
 * 级联（Cascade）：
 * 当 TV1 的一个桶到期后，需要将后续的定时器级联到 TV2
 * 以此类推
 */

#define TVN_BITS 6
#define TVR_BITS 8
#define TVN_SIZE (1 << TVN_BITS)      // 64
#define TVR_SIZE (1 << TVR_BITS)      // 256

struct tvec {
    struct tvec_root tv1;           // 256 个桶
    struct tvec_base *tv2[64];
    struct tvec_base *tv3[64];
    struct tvec_base *tv4[64];
    struct tvec_base *tv5[64];
};

struct tvec_root {
    struct timer_list *vec[TVR_SIZE];
};

struct tvec_base {
    struct timer_list *running_timer;
    unsigned long timer_jiffies;
    struct tvec_root tv1;
    /* ... 其他 TV 数组 ... */
    int cpu;
    struct tvec_base *base;
};
```

### 7.2 定时器到期处理

```c
/**
 * run_timer_softirq - 软中断中的定时器处理
 */
static void run_timer_softirq(struct softirq_action *h)
{
    struct timer_base *base = this_cpu_ptr(&timer_bases[BASE_STD]);

    /* 处理到期的定时器 */
    __run_timers(base);
}

/**
 * __run_timers - 运行定时器
 *
 * 处理所有到期的定时器
 */
static inline void __run_timers(struct timer_base *base)
{
    spin_lock_irqsave(&base->lock, flags);

    while (time_after_eq(jiffies, base->timer_jiffies)) {
        struct timer_list *timer;

        /* 级联处理 */
        if (!cascade(base, &base->tv2, INDEX(0)))
            cascade(base, &base->tv3, INDEX(1));

        /* 获取当前 jiffies 对应的链表 */
        __run_timer(base);
    }

    spin_unlock_irqrestore(&base->lock, flags);
}
```

## 8. 时间相关系统调用

### 8.1 setitimer 实现

```c
/**
 * do_setitimer - 设置间隔定时器
 */
int do_setitimer(int which, struct itimerspec64 *new,
                struct itimerspec64 *old)
{
    struct hrtimer *timer;
    ktime_t expires;

    timer = &current->it[which].itimer;

    /* 计算新的过期时间 */
    expires = timespec64_to_ktime(new->it_value);

    /* 启动 hrtimer */
    hrtimer_start(timer, expires, HRTIMER_MODE_REL);

    return 0;
}
```

## 9. 核心算法分析

### 9.1 时间复杂度

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| ktime_get_fast_ns | O(1) | vDSO/序列计数 |
| clocksource_read | O(1) | 硬件读取 |
| hrtimer_start | O(log n) | 红黑树插入 |
| hrtimer_expire | O(log n) | 红黑树删除 |
| timer_wheel cascade | O(1) amortized | 摊销 |

### 9.2 精度分析

```
时间源精度（x86）：
- TSC: 1-100ns（取决于 CPU）
- HPET: ~100ns
- ACPI PM: ~1μs

hrtimer 精度：
- 受时钟事件硬件限制
- 通常 ~1μs 到 ~1ms

定时器 wheel 精度：
- 受 jiffies 精度限制
- 通常 1ms 到 10ms（CONFIG_HZ 设置）
```

## 10. 参考资料

- `kernel/time/timekeeping.c` - 时间记录实现
- `kernel/time/clocksource.c` - 时钟源管理
- `kernel/time/hrtimer.c` - 高分辨率定时器
- `kernel/time/timer.c` - 低分辨率定时器 wheel
- `kernel/time/clockevents.c` - 时钟事件框架
- `include/linux/timekeeper.h` - timekeeper 接口
- `include/linux/hrtimer.h` - hrtimer 接口
- `include/linux/clocksource.h` - clocksource 接口
- Documentation/timers/
- Documentation/time/
