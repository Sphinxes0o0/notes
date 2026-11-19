# Linux Kernel Time and Timer Infrastructure for Networking: Comprehensive Analysis

## Table of Contents

1. [Timer Wheel](#1-timer-wheel)
2. [High Resolution Timers](#2-high-resolution-timers)
3. [TCP Timer Infrastructure](#3-tcp-timer-infrastructure)
4. [Connection Tracking Timers](#4-connection-tracking-timers)
5. [NAPI Deferral Timers](#5-napi-deferral-timers)
6. [Timestamp Infrastructure](#6-timestamp-infrastructure)
7. [Interaction Between Jiffies and HRTimers](#7-interaction-between-jiffies-and-hrtimers)

---

## 1. Timer Wheel

### 1.1 struct timer_base

**File:** `kernel/time/timer.c`, lines 250-265

```c
struct timer_base {
    raw_spinlock_t        lock;
    struct timer_list     *running_timer;
#ifdef CONFIG_PREEMPT_RT
    spinlock_t            expiry_lock;
    atomic_t              timer_waiters;
#endif
    unsigned long         clk;           // Updated before enqueue, 1 offset ahead during expiry
    unsigned long         next_expiry;
    unsigned int          cpu;
    bool                  next_expiry_recalc;
    bool                  is_idle;
    bool                  timers_pending;
    DECLARE_BITMAP(pending_map, WHEEL_SIZE);
    struct hlist_head    vectors[WHEEL_SIZE];
}
```

### 1.2 Wheel Structure

The timer wheel uses **9 levels** with 64 buckets each (LVL_SIZE=64):
- **Level 0**: 1ms granularity (HZ=1000), range 0-63ms
- **Level 1**: 8ms granularity, range 64-511ms
- **Level 2**: 64ms granularity, range 512-4095ms
- **Level 8**: ~4 hours granularity, max ~12 days

### 1.3 __mod_timer()

**File:** `kernel/time/timer.c`, lines 1017-1142

The core timer modification function:
1. **Early exit optimization**: If timer is pending and new expires equals current, returns immediately
2. **Forward base clock**: `forward_timer_base(base)` syncs base->clk with jiffies
3. **Bucket index calculation**: `calc_wheel_index()` determines which wheel level/bucket
4. **Same bucket optimization**: If new timer lands in same bucket, just update expires
5. **CPU migration**: If base changes, sets `TIMER_MIGRATING` flag and updates CPU affinity

### 1.4 __run_timers()

**File:** `kernel/time/timer.c`, lines 2343-2375

```c
static inline void __run_timers(struct timer_base *base)
{
    // Runs while jiffies >= base->clk AND jiffies >= base->next_expiry
    while (time_after_eq(jiffies, base->clk) &&
           time_after_eq(jiffies, base->next_expiry)) {
        levels = collect_expired_timers(base, heads);
        base->clk++;  // Advance clock to avoid endless requeue
        timer_recalc_next_expiry(base);
        while (levels--)
            expire_timers(base, heads + levels);
    }
}
```

### 1.5 Timer Execution in Softirq Context

Timers execute in **softirq context** (TIMER_SOFTIRQ) via `run_timer_softirq()` (line 2400).

---

## 2. High Resolution Timers

### 2.1 struct hrtimer

**File:** `kernel/time/hrtimer.c`

```c
struct hrtimer {
    struct timerqueue_node node;   // rb_tree node for expiry ordering
    clockid_t          clockid;   // CLOCK_MONOTONIC, CLOCK_REALTIME, etc.
    enum hrtimer_mode  mode;      // ABS/REL, PINNED, SOFT/HARD
    ktime_t            expires;    // expiry time (ktime_t)
    ktime_t            softexpires; // earliest expiry with slack
    // ...
};
```

### 2.2 Clock Bases

**File:** `kernel/time/hrtimer.c`, lines 80-119

Per-CPU `hrtimer_bases` contains 8 clock bases:
- `HRTIMER_BASE_MONOTONIC` / `HRTIMER_BASE_MONOTONIC_SOFT`
- `HRTIMER_BASE_REALTIME` / `HRTIMER_BASE_REALTIME_SOFT`
- `HRTIMER_BASE_BOOTTIME` / `HRTIMER_BASE_BOOTTIME_SOFT`
- `HRTIMER_BASE_TAI` / `HRTIMER_BASE_TAI_SOFT`

The SOFT variants run in softirq context, HARD variants run in hard interrupt context.

### 2.3 hrtimer_run_softirq()

**File:** `kernel/time/hrtimer.c`, lines 1856-1873

```c
static __latent_entropy void hrtimer_run_softirq(void)
{
    hrtimer_cpu_base_lock_expiry(cpu_base);
    raw_spin_lock_irqsave(&cpu_base->lock, flags);
    now = hrtimer_update_base(cpu_base);
    __hrtimer_run_queues(cpu_base, now, flags, HRTIMER_ACTIVE_SOFT);
    cpu_base->softirq_activated = 0;
    hrtimer_update_softirq_timer(cpu_base, true);
    raw_spin_unlock_irqrestore(&cpu_base->lock, flags);
    hrtimer_cpu_base_unlock_expiry(cpu_base);
}
```

### 2.4 clock_was_set_delayed()

**File:** `kernel/time/hrtimer.c`, lines 997-999

```c
void clock_was_set_delayed(void)
{
    schedule_work(&hrtimer_work);  // Schedules clock_was_set_work
}
```

---

## 3. TCP Timer Infrastructure

### 3.1 Timer Types and Constants

**File:** `include/net/inet_connection_sock.h`, lines 146-150

```c
#define ICSK_TIME_RETRANS      1   // Retransmit timer
#define ICSK_TIME_DACK         2   // Delayed ack timer
#define ICSK_TIME_PROBE0       3   // Zero window probe timer
#define ICSK_TIME_LOSS_PROBE   5   // Tail loss probe timer
#define ICSK_TIME_REO_TIMEOUT  6   // Reordering timer
```

### 3.2 inet_connection_sock Timers

**File:** `include/net/inet_connection_sock.h`, lines 82-144

```c
struct inet_connection_sock {
    struct timer_list   icsk_delack_timer;    // Delayed ACK timer
    union {
        struct timer_list icsk_keepalive_timer;
        struct timer_list mptcp_tout_timer;
    };
    __u8   icsk_pending;     // Scheduled timer event
    __u8   icsk_backoff;    // Exponential backoff counter
    // ...
    struct {
        __u8   pending;      // ACK is pending
        __u8   quick;        // Quick ack count
        __u8   pingpong;     // Interactive session flag
        __u8   retry;
        __u32  ato:8;        // Predicted tick of soft clock
        // ...
    } icsk_ack;
};
```

### 3.3 inet_csk_reset_xmit_timer()

**File:** `include/net/inet_connection_sock.h`, lines 228-252

```c
static inline void inet_csk_reset_xmit_timer(struct sock *sk, const int what,
                         unsigned long when, const unsigned long max_when)
{
    struct inet_connection_sock *icsk = inet_csk(sk);

    if (when > max_when)
        when = max_when;

    when += jiffies;  // Convert relative to absolute

    if (what == ICSK_TIME_RETRANS || what == ICSK_TIME_PROBE0 ||
        what == ICSK_TIME_LOSS_PROBE || what == ICSK_TIME_REO_TIMEOUT) {
        smp_store_release(&icsk->icsk_pending, what);
        sk_reset_timer(sk, &sk->tcp_retransmit_timer, when);
    } else if (what == ICSK_TIME_DACK) {
        smp_store_release(&icsk->icsk_pending,
                  icsk->icsk_pending | ICSK_ACK_TIMER);
        sk_reset_timer(sk, &icsk->icsk_delack_timer, when);
    }
}
```

### 3.4 tcp_delack_timer_handler()

**File:** `net/ipv4/tcp_timer.c`, lines 308-348

Handles delayed ACK processing:
- Returns early if socket in CLOSE/LISTEN state
- Handles SACK compression if tp->compressed_ack set
- Inflates ATO on missed delayed ACKs
- Sends ACK via tcp_send_ack()

### 3.5 tcp_retransmit_timer()

**File:** `net/ipv4/tcp_timer.c`, lines 534-689

Key flow:
1. Handles Fast Open child sockets via `tcp_fastopen_synack_timer()`
2. Zero-window probe case: When receiver shrunk window to 0
3. Checks for timeout via `tcp_write_timeout()`
4. On retransmission:
   - Enters loss state (`tcp_enter_loss()`)
   - Doubles RTO with backoff
5. Resets timer with clamped RTO

### 3.6 tcp_write_timer_handler()

**File:** `net/ipv4/tcp_timer.c`, lines 694-727

Dispatches based on `icsk->icsk_pending`:
- `ICSK_TIME_REO_TIMEOUT` -> `tcp_rack_reo_timeout()`
- `ICSK_TIME_LOSS_PROBE` -> `tcp_send_loss_probe()`
- `ICSK_TIME_RETRANS` -> `tcp_retransmit_timer()`
- `ICSK_TIME_PROBE0` -> `tcp_probe_timer()`

### 3.7 tcp_keepalive_timer()

**File:** `net/ipv4/tcp_timer.c`, lines 779-866

- Checks `SOCK_KEEPOPEN` flag
- In FIN_WAIT2 + dead socket: triggers time_wait
- If probes exceeded (`icsk_probes_out >= keepalive_probes()`): sends RST
- Reschedules with `tcp_reset_keepalive_timer()`

### 3.8 tcp_init_xmit_timers()

**File:** `net/ipv4/tcp_timer.c`, lines 896-905

```c
void tcp_init_xmit_timers(struct sock *sk)
{
    inet_csk_init_xmit_timers(sk, &tcp_write_timer, &tcp_delack_timer,
                  &tcp_keepalive_timer);
    hrtimer_setup(&tcp_sk(sk)->pacing_timer, tcp_pace_kick, CLOCK_MONOTONIC,
              HRTIMER_MODE_ABS_PINNED_SOFT);
    hrtimer_setup(&tcp_sk(sk)->compressed_ack_timer, tcp_compressed_ack_kick,
              HRTIMER_MODE_REL_PINNED_SOFT);
}
```

Note: TCP uses both **JIFFIES-based timer wheel timers** (retransmit, delack, keepalive) AND **hrtimers** (pacing, compressed ACK kick).

---

## 4. Connection Tracking Timers

### 4.1 nf_ct_delete()

**File:** `net/netfilter/nf_conntrack_core.c`, lines 644-682

```c
bool nf_ct_delete(struct nf_conn *ct, u32 portid, int report)
{
    // Sets IPS_DYING_BIT to prevent reinsertion
    // If not yet in hash table: destroys helper, removes from lists
    // Calls __nf_ct_delete_from_lists() under local_bh_disable()
    // Adds to ecache dying list for event delivery
    // Drops reference via nf_ct_put()
}
```

### 4.2 __nf_ct_refresh_acct()

**File:** `net/netfilter/nf_conntrack_core.c`, lines 2097-2116

```c
void __nf_ct_refresh_acct(struct nf_conn *ct, enum ip_conntrack_info ctinfo,
              u32 extra_jiffies, unsigned int bytes)
{
    if (test_bit(IPS_FIXED_TIMEOUT_BIT, &ct->status))
        goto acct;

    if (nf_ct_is_confirmed(ct))
        extra_jiffies += nfct_time_stamp;  // Adds current jiffies reference

    if (READ_ONCE(ct->timeout) != extra_jiffies)
        WRITE_ONCE(ct->timeout, extra_jiffies);
acct:
    if (bytes)
        nf_ct_acct_update(ct, CTINFO2DIR(ctinfo), bytes);
}
```

Key insight: `ct->timeout` is an **absolute jiffies value** (not relative), calculated as `current_jiffies + timeout_delta`.

### 4.3 gc_worker()

**File:** `net/netfilter/nf_conntrack_core.c`, lines 1513-1649

Conntrack garbage collection via delayed work:
- Scans hash table buckets
- Calls `nf_ct_gc_expired()` for expired entries
- Implements early drop when 95% of max connections reached
- Adaptive interval calculation based on `avg_timeout`

---

## 5. NAPI Deferral Timers

### 5.1 struct napi_struct

**File:** `net/core/dev.c`, lines 381-410

```c
struct napi_struct {
    struct hrtimer     timer;              // Watchdog timer
    unsigned long      gro_flush_timeout;
    unsigned long      irq_suspend_timeout;
    u32                defer_hard_irqs_count;
    u32                defer_hard_irqs;
    // ...
};
```

### 5.2 napi_watchdog_timer()

**File:** `net/core/dev.c`, lines 7113-7128

```c
static enum hrtimer_restart napi_watchdog(struct hrtimer *timer)
{
    struct napi_struct *napi = container_of(timer, struct napi_struct, timer);

    if (!napi_disable_pending(napi) &&
        !test_and_set_bit(NAPI_STATE_SCHED, &napi->state)) {
        clear_bit(NAPI_STATE_PREFER_BUSY_POLL, &napi->state);
        __napi_schedule_irqoff(napi);
    }
    return HRTIMER_NORESTART;
}
```

### 5.3 gro_flush_timeout / defer_hard_irqs

**File:** `net/core/dev.c`, lines 6762-6775

```c
if (work_done) {
    if (n->gro.bitmask)
        timeout = napi_get_gro_flush_timeout(n);
    n->defer_hard_irqs_count = napi_get_defer_hard_irqs(n);
}
if (n->defer_hard_irqs_count > 0) {
    n->defer_hard_irqs_count--;
    timeout = napi_get_gro_flush_timeout(n);
    if (timeout)
        ret = false;  // Skip polling, let IRQ handle
}
```

These mechanisms allow:
1. **GRO flush timeout**: Batch GRO packets before passing up
2. **defer_hard_irqs**: Coalesce interrupts by deferring NAPI rearm

---

## 6. Timestamp Infrastructure

### 6.1 skb->tstamp

**File:** `include/linux/skbuff.h`, lines 779, 4374-4425

```c
// In struct sk_buff:
__u8    tstamp_type:2;  // See skb_tstamp_type enum
// ...
ktime_t tstamp;         // Time we arrived/left
```

### 6.2 skb_tstamp_type

**File:** `include/linux/skbuff.h`, lines 728-733

```c
enum skb_tstamp_type {
    SKB_CLOCK_REALTIME,
    SKB_CLOCK_MONOTONIC,
    SKB_CLOCK_TAI,
    __SKB_CLOCK_MAX = SKB_CLOCK_TAI,
};
```

### 6.3 __net_timestamp()

**File:** `include/linux/skbuff.h`, lines 4421-4425

```c
static inline void __net_timestamp(struct sk_buff *skb)
{
    skb->tstamp = ktime_get_real();
    skb->tstamp_type = SKB_CLOCK_REALTIME;
}
```

### 6.4 struct skb_shared_hwtstamps

**File:** `include/linux/skbuff.h`, lines 447-467

```c
struct skb_shared_hwtstamps {
    union {
        ktime_t hwtstamp;      // Hardware timestamp
        void   *netdev_data;   // Device-specific reference
    };
};
```

**Software timestamps** use `skb->tstamp` (ktime_t from `ktime_get_real()`).

**Hardware timestamps** use `skb_shinfo(skb)->hwtstamps` (filled by network driver).

---

## 7. Interaction Between Jiffies and HRTimers

### 7.1 Key Differences

| Aspect | Timer Wheel | HRTimers |
|--------|-------------|----------|
| Resolution | 1 jiffy (varies by HZ) | Nanoseconds (hardware dependent) |
| Context | Softirq | Hardirq or softirq |
| Ordering | Hash wheel O(1) | Red-black tree O(log n) |
| Use case | Network timeouts | Precise scheduling |

### 7.2 NOHZ Interaction

**File:** `kernel/time/timer.c`, lines 1928-1960

```c
static u64 cmp_next_hrtimer_event(u64 basem, u64 expires)
{
    u64 nextevt = hrtimer_get_next_event();

    if (expires <= nextevt)
        return expires;

    if (nextevt <= basem)
        return basem;  // If hrtimer already expired, fire tick now

    return DIV_ROUND_UP_ULL(nextevt, TICK_NSEC) * TICK_NSEC;
}
```

### 7.3 Softirq Processing Order

1. **hrtimer_run_queues()** called from `run_local_timers()` in tick interrupt
2. If soft hrtimers expired: raises `HRTIMER_SOFTIRQ`
3. `hrtimer_run_softirq()` processes SOFT bases
4. `run_timer_softirq()` processes timer wheel BASE_LOCAL, BASE_GLOBAL, BASE_DEF

### 7.4 Deferral Pattern

TCP timers use `bh_lock_sock()` and check `sock_owned_by_user()`:
- If socket owned by userspace: defer to `tcp_release_cb()` via `sk_tsq_flags`
- If not owned: execute handler directly

---

## Summary

The Linux kernel networking timer infrastructure is a sophisticated multi-layer system:

1. **Timer Wheel** provides O(1) jiffies-based timeouts ideal for network protocols where exact timing isn't critical but efficiency is paramount.

2. **HRTimers** provide nanosecond precision for rate limiting (pacing), compressed ACKs, and scenarios requiring accurate timing.

3. **TCP timers** use jiffies-based timers for retransmission, delayed ACK, and keepalive with exponential backoff. The `icsk_pending` field multiplexes multiple timer types onto one `struct timer_list`.

4. **Conntrack** uses absolute jiffies in `ct->timeout` and garbage collection via `delayed_work`, not per-connection timers.

5. **NAPI** uses hrtimers for watchdog and interrupt coalescing via `gro_flush_timeout` and `defer_hard_irqs`.

6. **Timestamps** distinguish software (`skb->tstamp` with `ktime_get_real()`) and hardware (`skb_shared_hwtstamps`) timestamps.

The interaction between layers uses:
- **Softirq context** for timer expiry to avoid priority inversion
- **Lock ordering**: `bh_lock_sock()` for socket protection
- **Deferral patterns**: When socket owned by userspace, timers defer via callback flags
- **NOHZ integration**: Timer wheel checks next hrtimer event to avoid missing precise timers
