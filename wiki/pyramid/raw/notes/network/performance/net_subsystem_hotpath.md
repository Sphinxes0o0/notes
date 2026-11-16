# Linux Kernel Networking Hot Path and Low-Level Mechanisms

## Table of Contents

1. [Softirq and NAPI](#1-softirq-and-napi)
2. [RCU (Read-Copy-Update) in Networking](#2-rcu-read-copy-update-in-networking)
3. [Per-CPU Variables](#3-per-cpu-variables)
4. [Memory Barriers and Ordering](#4-memory-barriers-and-ordering)
5. [Cache Line Optimization](#5-cache-line-optimization)
6. [Branch Prediction](#6-branch-prediction)
7. [Interrupt Coalescing](#7-interrupt-coalescing)

---

## 1. Softirq and NAPI

**File:** `/Users/sphinx/github/linux/net/core/dev.c`

### 1.1 `struct softnet_data` - Per-CPU Softirq State

**File:** `/Users/sphinx/github/linux/include/linux/netdevice.h`, lines 3516-3570

```c
struct softnet_data {
    struct list_head    poll_list;
    struct sk_buff_head process_queue;
    local_lock_t       process_queue_bh_lock;

    /* stats */
    unsigned int       processed;
    unsigned int       time_squeeze;
#ifdef CONFIG_RPS
    struct softnet_data *rps_ipi_list;
#endif
    unsigned int       received_rps;
    bool               in_net_rx_action;
    bool               in_napi_threaded_poll;

    /* written and read only by owning cpu: */
    struct netdev_xmit xmit;
#ifdef CONFIG_RPS
    unsigned int       input_queue_head ____cacheline_aligned_in_smp;
    unsigned int       input_queue_tail;
#endif
    struct sk_buff_head input_pkt_queue;

    struct napi_struct backlog;
};
```

**Declaration:** `/Users/sphinx/github/linux/net/core/dev.c`, line 462

```c
DEFINE_PER_CPU_ALIGNED(struct softnet_data, softnet_data) = {
    .process_queue_bh_lock = INIT_LOCAL_LOCK(process_queue_bh_lock),
};
```

Key design points:
- `DEFINE_PER_CPU_ALIGNED` ensures the structure is cache-line aligned per CPU
- `poll_list` links NAPI structs scheduled for polling
- `process_queue` holds incoming SKBs awaiting processing
- `input_pkt_queue` is the backlog queue for received packets
- `in_net_rx_action` flag tracks if net_rx_action is currently running on this CPU

### 1.2 `net_rx_action()` - Softirq Handler for Receive

**File:** `/Users/sphinx/github/linux/net/core/dev.c`, lines 7890-7956

```c
static __latent_entropy void net_rx_action(void)
{
    struct softnet_data *sd = this_cpu_ptr(&softnet_data);
    unsigned long time_limit = jiffies +
        usecs_to_jiffies(READ_ONCE(net_hotdata.netdev_budget_usecs));
    struct bpf_net_context __bpf_net_ctx, *bpf_net_ctx;
    int budget = READ_ONCE(net_hotdata.netdev_budget);
    LIST_HEAD(list);
    LIST_HEAD(repoll);

    bpf_net_ctx = bpf_net_ctx_set(&__bpf_net_ctx);
start:
    sd->in_net_rx_action = true;
    local_irq_disable();
    list_splice_init(&sd->poll_list, &list);
    local_irq_enable();

    for (;;) {
        struct napi_struct *n;

        skb_defer_free_flush();

        if (list_empty(&list)) {
            if (list_empty(&repoll)) {
                sd->in_net_rx_action = false;
                barrier();
                if (!list_empty(&sd->poll_list))
                    goto start;
                if (!sd_has_rps_ipi_waiting(sd))
                    goto end;
            }
            break;
        }

        n = list_first_entry(&list, struct napi_struct, poll_list);
        budget -= napi_poll(n, &repoll);

        if (unlikely(budget <= 0 || time_after_eq(jiffies, time_limit))) {
            WRITE_ONCE(sd->time_squeeze, sd->time_squeeze + 1);
            break;
        }
    }

    local_irq_disable();
    list_splice_tail_init(&sd->poll_list, &list);
    list_splice_tail(&repoll, &list);
    list_splice(&list, &sd->poll_list);
    if (!list_empty(&sd->poll_list))
        __raise_softirq_irqoff(NET_RX_SOFTIRQ);
    else
        sd->in_net_rx_action = false;

    net_rps_action_and_irq_enable(sd);
end:
    bpf_net_ctx_clear(bpf_net_ctx);
}
```

The softirq handler:
1. Sets `in_net_rx_action = true` to track execution context
2. Splices the per-CPU `poll_list` to a local list (safe from IRQ re-addition)
3. Iterates through scheduled NAPIs calling their `poll()` functions
4. Tracks `budget` (packet count) and `time_limit` (jiffies-based) to bound latency
5. Returns early if budget exhausted or time limit reached
6. Handles RPS (Remote Packet Steering) IPIs via `net_rps_action_and_irq_enable()`

### 1.3 `napi_schedule()` / `napi_disable()` - NAPI Enable/Disable

#### `__napi_schedule()` - Lines 6689-6696

```c
void __napi_schedule(struct napi_struct *n)
{
    unsigned long flags;

    local_irq_save(flags);
    ____napi_schedule(this_cpu_ptr(&softnet_data), n);
    local_irq_restore(flags);
}
```

#### `____napi_schedule()` - Lines 4942-4976

```c
static inline void ____napi_schedule(struct softnet_data *sd,
                    struct napi_struct *napi)
{
    struct task_struct *thread;

    lockdep_assert_irqs_disabled();

    if (test_bit(NAPI_STATE_THREADED, &napi->state)) {
        thread = READ_ONCE(napi->thread);
        if (thread) {
            if (use_backlog_threads() && thread == raw_cpu_read(backlog_napi))
                goto use_local_napi;

            set_bit(NAPI_STATE_SCHED_THREADED, &napi->state);
            wake_up_process(thread);
            return;
        }
    }

use_local_napi:
    list_add_tail(&napi->poll_list, &sd->poll_list);
    WRITE_ONCE(napi->list_owner, smp_processor_id());

    if (!sd->in_net_rx_action)
        raise_softirq_irqoff(NET_RX_SOFTIRQ);
}
```

### 1.4 `netif_receive_skb()` - Main Receive Entry

**File:** `/Users/sphinx/github/linux/net/core/dev.c`

#### `netif_receive_skb()` - Line 6433

```c
int netif_receive_skb(struct sk_buff *skb)
{
    int ret;
    trace_netif_receive_skb_entry(skb);
    ret = netif_receive_skb_internal(skb);
    trace_netif_receive_skb_exit(ret);
    return ret;
}
```

#### `__netif_receive_skb_core()` - Lines 5951-6050

Main receive processing function that:
- Validates packet headers
- Handles VLAN untagging
- Delivers to protocol handlers via `ptype_all` and `dev->ptype_all`
- Handles XDP programs via `do_xdp_generic()`

### 1.5 How NAPI Polls vs Interrupt-Driven Receive

**Interrupt-Driven Problems:**
- High interrupt rate under heavy load (packets per interrupt = 1)
- Interrupt overhead dominates CPU time
- Cache thrashing as CPU switches contexts rapidly

**NAPI Solution - Polling with Interrupt Coalescence:**

1. **Initial interrupt** signals packet arrival
2. Driver calls `napi_schedule()` to queue NAPI
3. Softirq `net_rx_action()` polls the device via `napi->poll()`
4. Device interrupt is disabled during polling
5. Polling continues until `budget` exhausted or `time_limit` reached
6. `napi_complete_done()` re-enables interrupts

### 1.6 `gro_normal_list()` - GRO Batch Completion

**File:** `/Users/sphinx/github/linux/include/net/gro.h`, lines 519-526

```c
static inline void gro_normal_list(struct gro_node *gro)
{
    if (!gro->rx_count)
        return;
    netif_receive_skb_list_internal(&gro->rx_list);
    INIT_LIST_HEAD(&gro->rx_list);
    gro->rx_count = 0;
}
```

GRO batches packets that don't need immediate processing and delivers them as a list for better throughput.

### 1.7 `process_backlog()` - Backlog Processing

**File:** `/Users/sphinx/github/linux/net/core/dev.c`, lines 6623-6680

This is the `poll()` function for the backlog NAPI that:
- Dequeues from `process_queue` (or splices from `input_pkt_queue`)
- Uses `local_lock_nested_bh` to protect the process queue
- Returns when `quota` packets processed or queue empty

---

## 2. RCU (Read-Copy-Update) in Networking

### 2.1 RCU Primitives

**File:** `/Users/sphinx/github/linux/include/linux/rcupdate.h`

```c
static inline void __rcu_read_lock(void)
{
    preempt_disable();
}

static inline void __rcu_read_unlock(void)
{
    if (IS_ENABLED(CONFIG_RCU_STRICT_GRACE_PERIOD))
        rcu_read_unlock_strict();
    preempt_enable();
}
```

### 2.2 RCU Usage in Conntrack - `nf_conntrack_find_get()`

**File:** `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_core.c`, lines 774-827

```c
struct nf_conntrack_tuple_hash *
nf_conntrack_find_get(struct net *net, const struct nf_conntrack_zone *zone,
              const struct nf_conntrack_tuple *tuple)
{
    unsigned int rid, zone_id = nf_ct_zone_id(zone, IP_CT_DIR_ORIGINAL);
    struct nf_conntrack_tuple_hash *thash;

    rcu_read_lock();

    thash = __nf_conntrack_find_get(net, zone, tuple,
                    hash_conntrack_raw(tuple, zone_id, net));

    if (thash)
        goto out_unlock;

    rid = nf_ct_zone_id(zone, IP_CT_DIR_REPLY);
    if (rid != zone_id)
        thash = __nf_conntrack_find_get(net, zone, tuple,
                        hash_conntrack_raw(tuple, rid, net));

out_unlock:
    rcu_read_unlock();
    return thash;
}
```

Key RCU usage pattern:
1. `rcu_read_lock()` held while traversing the conntrack hash
2. `refcount_inc_not_zero()` safely increments reference count
3. `smp_acquire__after_ctrl_dep()` provides acquire barrier after ctrl dependency
4. Tuple key is re-checked after refcount increment to ensure validity
5. `rcu_read_unlock()` releases the lock

### 2.3 RCU Grace Periods in Conntrack Garbage Collection

The conntrack subsystem uses `synchronize_rcu()` to wait for RCU grace periods before freeing conntrack entries. `call_rcu()` is used for deferred freeing after the grace period.

---

## 3. Per-CPU Variables

### 3.1 `DECLARE_PER_CPU()` / `DEFINE_PER_CPU()`

**Lines 110-114:**

```c
#define DECLARE_PER_CPU(type, name)                    \
    DECLARE_PER_CPU_SECTION(type, name, "")

#define DEFINE_PER_CPU(type, name)                    \
    DEFINE_PER_CPU_SECTION(type, name, "")
```

### 3.2 `DEFINE_PER_CPU_ALIGNED()` for Cache Line Alignment

```c
#define DEFINE_PER_CPU_ALIGNED(type, name)                \
    DEFINE_PER_CPU_SECTION(type, name, PER_CPU_ALIGNED_SECTION)    \
    ____cacheline_aligned
```

**Usage in networking** - `/Users/sphinx/github/linux/net/core/dev.c`, line 462:

```c
DEFINE_PER_CPU_ALIGNED(struct softnet_data, softnet_data) = {
    .process_queue_bh_lock = INIT_LOCAL_LOCK(process_queue_bh_lock),
};
```

### 3.3 `struct u64_stats_sync` - Synchronized 64-bit Counters

**File:** `/Users/sphinx/github/linux/include/linux/u64_stats_sync.h`

```c
struct u64_stats_sync {
#if BITS_PER_LONG == 32
    seqcount_t    seq;
#endif
};
```

**Usage pattern:**

```c
/* Writer (must hold exclusive access) */
u64_stats_update_begin(&stats->syncp);
u64_stats_add(&stats->bytes64, len);
u64_stats_inc(&stats->packets64);
u64_stats_update_end(&stats->syncp);

/* Reader (can be preempted, no locking required on 64-bit) */
do {
    start = u64_stats_fetch_begin(&stats->syncp);
    tbytes = u64_stats_read(&stats->bytes64);
    tpackets = u64_stats_read(&stats->packets64);
} while (u64_stats_fetch_retry(&stats->syncp, start));
```

---

## 4. Memory Barriers and Ordering

### 4.1 SMP Memory Barrier Definitions

**Lines 96-124:**

```c
#ifdef CONFIG_SMP
#ifndef smp_mb
#define smp_mb()    do { kcsan_mb(); __smp_mb(); } while (0)
#endif
#ifndef smp_rmb
#define smp_rmb()    do { kcsan_rmb(); __smp_rmb(); } while (0)
#endif
#ifndef smp_wmb
#define smp_wmb()    do { kcsan_wmb(); __smp_wmb(); } while (0)
#endif
#else
#define smp_mb()    barrier()
#endif
```

### 4.2 `smp_load_acquire()` / `smp_store_release()`

```c
#define __smp_store_release(p, v)                  \
do {                                    \
    compiletime_assert_atomic_type(*p);              \
    __smp_mb();                           \
    WRITE_ONCE(*p, v);                        \
} while (0)

#define __smp_load_acquire(p)                      \
({                                  \
    __unqual_scalar_typeof(*p) ___p1 = READ_ONCE(*p);       \
    compiletime_assert_atomic_type(*p);              \
    __smp_mb();                           \
    (typeof(*p))___p1;                       \
})
```

### 4.3 Memory Barriers in SKB

```c
if (!IS_ENABLED(CONFIG_DEBUG_NET) && likely(refcount_read(&skb->users) == 1))
    smp_rmb();
```

These barriers ensure that:
1. The refcount check is properly ordered with subsequent data accesses
2. No speculative re-ordering of loads/stores occurs around the critical section

### 4.4 Sequence Counting in Conntrack

In conntrack, sequence counting provides lockless readers:
1. **Writer**: Increments the sequence number before and after modifying shared state
2. **Reader**: Reads the sequence number before and after critical reads
3. If the sequence numbers match, the reader knows the data was consistent

---

## 5. Cache Line Optimization

### 5.1 `L1_CACHE_BYTES`

```c
#define L1_CACHE_ALIGN(x) __ALIGN_KERNEL(x, L1_CACHE_BYTES)
#define NET_SKB_PAD    max(32, L1_CACHE_BYTES)
```

### 5.2 `____cacheline_aligned_in_smp` in `struct sock`

**File:** `/Users/sphinx/github/linux/include/net/sock.h`, lines 401-497

The socket structure uses `__cacheline_group_begin/end` annotations to organize fields into cache-line groups:

```c
struct sock {
    __cacheline_group_begin(sock_write_rx);
    atomic_t        sk_drops;
    __s32           sk_peek_off;
    struct sk_buff_head sk_error_queue;
    struct sk_buff_head sk_receive_queue;
    __cacheline_group_end(sock_write_rx);

    __cacheline_group_begin(sock_read_rx);
    struct dst_entry __rcu *sk_rx_dst;
    int               sk_rx_dst_ifindex;
    __cacheline_group_end(sock_read_rx);

    __cacheline_group_begin(sock_write_rxtx);
    socket_lock_t       sk_lock;
    __cacheline_group_end(sock_write_rxtx);
};
```

### 5.3 Socket Lock Cache Line Bouncing - `sk_lock`

```c
static inline void lock_sock_fast(struct sock *sk)
{
    mutex_acquire(&sk->sk_lock.dep_map, 0, 0, _RET_IP_);
    spin_lock_bh(&sk->sk_lock.slock);
    sk->sk_lock.owned = 1;
}
```

The `sk_lock` combines:
- A spinlock (`sk_lock.slock`) for fast-path locking with BH disabled
- A mutex (`sk_lock.mutex`) for sleepable operations
- `owned` flag to track lock ownership state

### 5.4 `struct softnet_data` Cache Line Alignment

```c
unsigned int       input_queue_head ____cacheline_aligned_in_smp;
```

Fields accessed across CPUs (like `input_queue_head`) are explicitly aligned to prevent false sharing.

---

## 6. Branch Prediction

### 6.1 `likely()` / `unlikely()` Macros

```c
# define likely(x)    __branch_check__(x, 1, __builtin_constant_p(x))
# define unlikely(x)    __branch_check__(x, 0, __builtin_constant_p(x))

/* Default implementation */
# define likely(x)    __builtin_expect(!!(x), 1)
# define unlikely(x)    __builtin_expect(!!(x), 0)
```

### 6.2 Usage in Packet Processing

```c
if (likely(refcount_inc_not_zero(&ct->ct_general.use))) {
    smp_acquire__after_ctrl_dep();
    if (likely(nf_ct_key_equal(h, tuple, zone, net)))
        return h;
}
```

### 6.3 How These Affect CPU Branch Prediction

Modern CPUs use:
1. **Static branch prediction**: Uses the hint from compiled code
2. **Dynamic branch prediction**: Learns from runtime behavior via BTB (Branch Target Buffer)

The `__builtin_expect()` allows the compiler to:
1. Position code to minimize branch mispredictions
2. Optimize instruction cache placement
3. Enable better pipelining by reducing stalls

---

## 7. Interrupt Coalescing

### 7.1 `netif_napi_add_weight_locked()` - NAPI Registration

**Lines 7534-7578:**

```c
void netif_napi_add_weight_locked(struct net_device *dev,
                  struct napi_struct *napi,
                  int (*poll)(struct napi_struct *, int),
                  int weight)
{
    if (WARN_ON(test_and_set_bit(NAPI_STATE_LISTED, &napi->state)))
        return;

    INIT_LIST_HEAD(&napi->poll_list);
    INIT_HLIST_NODE(&napi->napi_hash_node);
    hrtimer_setup(&napi->timer, napi_watchdog, CLOCK_MONOTONIC, HRTIMER_MODE_REL_PINNED);
    gro_init(&napi->gro);
    napi->poll = poll;
    napi->weight = weight;
    napi->dev = dev;

    napi_set_defer_hard_irqs(napi, READ_ONCE(dev->napi_defer_hard_irqs));
    napi_set_gro_flush_timeout(napi, READ_ONCE(dev->gro_flush_timeout));
}
```

### 7.2 `napi_complete_done()` - End of Polling

**Lines 6750-6817:**

```c
bool napi_complete_done(struct napi_struct *n, int work_done)
{
    unsigned long flags, val, new, timeout = 0;
    bool ret = true;

    if (unlikely(n->state & (NAPIF_STATE_NPSVC | NAPIF_STATE_IN_BUSY_POLL)))
        return false;

    if (work_done) {
        if (n->gro.bitmask)
            timeout = napi_get_gro_flush_timeout(n);
        n->defer_hard_irqs_count = napi_get_defer_hard_irqs(n);
    }
    if (n->defer_hard_irqs_count > 0) {
        n->defer_hard_irqs_count--;
        timeout = napi_get_gro_flush_timeout(n);
        if (timeout)
            ret = false;
    }

    gro_flush_normal(&n->gro, !!timeout);

    /* ... state management ... */

    if (timeout)
        hrtimer_start(&n->timer, ns_to_ktime(timeout),
                  HRTIMER_MODE_REL_PINNED);
    return ret;
}
```

### 7.3 How Adaptive IRQ Coalescing Works

**NAPI Deferral Mechanism:**

1. **Deferred Hard IRQs (`defer_hard_irqs`):**
   - Set via `napi_set_defer_hard_irqs(napi, count)`
   - Each time `napi_complete_done()` is called with `work_done > 0`, the count is decremented
   - If count > 0 after decrement and a timeout is set, the function returns `false`
   - This causes the device to not re-enable interrupts immediately, batching more packets

2. **GRO Flush Timeout (`gro_flush_timeout`):**
   - After polling completes, a timer can be set
   - If packets arrive before the timer fires, they are merged via GRO
   - This further reduces interrupt frequency

---

## Summary

The Linux networking stack employs numerous low-level optimizations:

1. **NAPI** switches between interrupt and polling modes based on load, naturally coalescing interrupts
2. **RCU** provides lockless read access to shared data structures like conntrack tables
3. **Per-CPU variables** eliminate most locking for hot path statistics
4. **Memory barriers** ensure proper ordering without expensive locks
5. **Cache line alignment** prevents false sharing in both `struct sock` and `struct softnet_data`
6. **Branch prediction hints** (`likely`/`unlikely`) guide CPU pipeline optimization
7. **Adaptive IRQ coalescing** via NAPI deferral and GRO timeout dynamically adjusts interrupt rate
