# Linux Kernel TCP Congestion Control: Comprehensive Analysis

## Table of Contents

1. [Congestion Control Infrastructure](#1-congestion-control-infrastructure)
2. [CUBIC](#2-cubic)
3. [BBR](#3-bbr)
4. [DCTCP](#4-dctcp)
5. [TCP Reno](#5-tcp-reno)
6. [Highspeed TCP](#6-highspeed-tcp)
7. [TCP Vegas](#7-tcp-vegas)
8. [TCP Illinois](#8-tcp-illinois)
9. [TCP Hybla](#9-tcp-hybla)
10. [YeAH-TCP](#10-yeah-tcp)

---

## 1. Congestion Control Infrastructure

### 1.1 struct tcp_congestion_ops

**File:** `include/net/tcp.h`, lines 1275-1334

```c
struct tcp_congestion_ops {
    /* A CC must provide ONE of either: */
    void (*cong_avoid)(struct sock *sk, u32 ack, u32 acked);  // "classic" response
    void (*cong_control)(struct sock *sk, u32 ack, int flag,    // "custom" response
                         const struct rate_sample *rs);

    u32 (*ssthresh)(struct sock *sk);        // return slow start threshold
    void (*set_state)(struct sock *sk, u8 new_state);          // optional
    void (*cwnd_event)(struct sock *sk, enum tcp_ca_event ev); // optional
    void (*in_ack_event)(struct sock *sk, u32 flags);          // optional
    void (*pkts_acked)(struct sock *sk, const struct ack_sample *sample); // optional
    u32 (*min_tso_segs)(struct sock *sk);    // optional
    u32 (*undo_cwnd)(struct sock *sk);       // required
    u32 (*sndbuf_expand)(struct sock *sk);   // optional

    size_t (*get_info)(...);                 // optional
    char name[TCP_CA_NAME_MAX];
    struct module *owner;
    struct list_head list;
    u32 key;
    u32 flags;
    void (*init)(struct sock *sk);           // optional
    void (*release)(struct sock *sk);        // optional
};
```

### 1.2 Registration

**File:** `net/ipv4/tcp_cong.c`

**register_congestion_control()** (lines 93-115):
1. Validates the algorithm (must have ssthresh, undo_cwnd, and either cong_avoid or cong_control)
2. Generates a hash key from the algorithm name
3. Adds to the global tcp_cong_list under spinlock protection

### 1.3 Helper Functions

**tcp_slow_start()** (lines 456-464):
```c
// Slow start: increase cwnd by 1 for each ACK, but cap at ssthresh
u32 tcp_slow_start(struct tcp_sock *tp, u32 acked)
{
    u32 cwnd = min(tcp_snd_cwnd(tp) + acked, tp->snd_ssthresh);
    acked -= cwnd - tcp_snd_cwnd(tp);
    tcp_snd_cwnd_set(tp, min(cwnd, tp->snd_cwnd_clamp));
    return acked;  // returns leftover acks for CA phase
}
```

**tcp_cong_avoid_ai()** (lines 470-486):
```c
// Additive Increase: cwnd += 1/cwnd for each packet ACKed (Jacobson's algorithm)
void tcp_cong_avoid_ai(struct tcp_sock *tp, u32 w, u32 acked)
{
    if (tp->snd_cwnd_cnt >= w) {
        tp->snd_cwnd_cnt = 0;
        tcp_snd_cwnd_set(tp, tcp_snd_cwnd(tp) + 1);
    }
    tp->snd_cwnd_cnt += acked;
    if (tp->snd_cwnd_cnt >= w) {
        u32 delta = tp->snd_cwnd_cnt / w;
        tp->snd_cwnd_cnt -= delta * w;
        tcp_snd_cwnd_set(tp, tcp_snd_cwnd(tp) + delta);
    }
    tcp_snd_cwnd_set(tp, min(tcp_snd_cwnd(tp), tp->snd_cwnd_clamp));
}
```

### 1.4 Key tcp_sock Fields

| Field | Type | Usage |
|-------|------|-------|
| `snd_cwnd` | u32 | Congestion window size |
| `snd_ssthresh` | u32 | Slow start threshold |
| `snd_cwnd_cnt` | u32 | Credits accumulated for AI |
| `snd_cwnd_clamp` | u32 | Maximum cwnd cap |
| `delivered` | u32 | Total packets delivered |
| `delivered_ce` | u32 | ECE-marked packets delivered |
| `srtt_us` | u32 | Smoothed RTT (<<3) |

---

## 2. CUBIC

### 2.1 Overview

CUBIC (RFC 8312) uses a cubic function to achieve more aggressive growth at large window sizes while maintaining Reno-like fairness at small window sizes. It integrates HyStart for early loss detection during slow start.

### 2.2 struct bictcp

**File:** `net/ipv4/tcp_cubic.c`, lines 86-105

```c
struct bictcp {
    u32  cnt;              /* increase cwnd by 1 after cnt ACKs */
    u32  last_max_cwnd;    /* last maximum snd_cwnd (Wmax) */
    u32  last_cwnd;        /* the last snd_cwnd */
    u32  last_time;        /* time when updated last_cwnd */
    u32  bic_origin_point; /* origin point of bic function */
    u32  bic_K;            /* time to origin point from epoch start */
    u32  delay_min;        /* min delay (usec) */
    u32  epoch_start;      /* beginning of an epoch */
    u32  ack_cnt;          /* number of acks */
    u32  tcp_cwnd;        /* estimated tcp cwnd for friendliness */
    u8   sample_cnt;       /* number of RTT samples */
    u8   found;            /* exit point found? (HyStart) */
    u32  round_start;      /* beginning of each round */
    u32  end_seq;          /* end_seq of the round */
    u32  last_ack;         /* last time ack spacing was close */
    u32  curr_rtt;         /* minimum rtt of current round */
};
```

### 2.3 Constants (RFC 8312 derivation)

- **Beta = 0.7** (717/1024): Multiplicative decrease factor
- **C = 0.4**: Cubic scaling constant
- **BICTCP_BETA_SCALE = 1024**: Fixed-point scaling

### 2.4 cubic_root() Algorithm

**File:** `net/ipv4/tcp_cubic.c`, lines 167-209

CUBIC requires computing the cubic root of a 64-bit value. Uses a table lookup followed by Newton-Raphson iteration.

### 2.5 bictcp_update() - The Cubic Function

**File:** `net/ipv4/tcp_cubic.c`, lines 214-322

The core CUBIC algorithm computes the target window size:

```c
static inline void bictcp_update(struct bictcp *ca, u32 cwnd, u32 acked)
{
    // Epoch management
    if (ca->epoch_start == 0) {
        ca->epoch_start = tcp_jiffies32;
        ca->ack_cnt = acked;
        ca->tcp_cwnd = cwnd;

        if (ca->last_max_cwnd <= cwnd) {
            ca->bic_K = 0;
            ca->bic_origin_point = cwnd;
        } else {
            // K = cubic_root((Wmax - cwnd) * rtt / C)
            ca->bic_K = cubic_root(cube_factor * (ca->last_max_cwnd - cwnd));
            ca->bic_origin_point = ca->last_max_cwnd;
        }
    }

    // CUBIC function: W(t) = C * (t - K)^3 + Wmax
    t = (tcp_jiffies32 - ca->epoch_start) + (delay_min in jiffies);
    t <<= BICTCP_HZ;
    do_div(t, HZ);

    if (t < ca->bic_K)
        offs = ca->bic_K - t;
    else
        offs = t - ca->bic_K;

    // delta = C * offs^3 / rtt
    delta = (cube_rtt_scale * offs * offs * offs) >> (10 + 3*BICTCP_HZ);

    if (t < ca->bic_K)
        bic_target = ca->bic_origin_point - delta;
    else
        bic_target = ca->bic_origin_point + delta;

    // cnt = cwnd / (bic_target - cwnd)
    if (bic_target > cwnd)
        ca->cnt = cwnd / (bic_target - cwnd);
    else
        ca->cnt = 100 * cwnd;
}
```

### 2.6 Mathematical Foundation

The cubic function is designed such that:
1. At small cwnd (near origin): aggressive growth similar to Reno
2. At large cwnd: polynomial growth that fills the pipe without overshooting
3. The cubic shape ensures that the window reaches Wmax and then decreases smoothly

---

## 3. BBR

### 3.1 Core Philosophy

BBR (Bottleneck Bandwidth and RTT) is a **model-based** congestion control that explicitly models the network path. It does NOT use loss as a congestion signal. Instead, it measures:
- **Bandwidth (bw)**: Maximum delivery rate
- **Minimum RTT (min_rtt)**: Base propagation delay

### 3.2 struct bbr

**File:** `net/ipv4/tcp_bbr.c`, lines 89-128

```c
struct bbr {
    u32  min_rtt_us;           /* min RTT in min_rtt_win_sec window */
    u32  min_rtt_stamp;       /* timestamp of min_rtt_us */
    u32  probe_rtt_done_stamp; /* end time for BBR_PROBE_RTT mode */
    struct minmax bw;         /* Max recent delivery rate (pkts/uS << 24) */
    u32  rtt_cnt;             /* count of packet-timed rounds */
    u32  next_rtt_delivered;  /* delivered at end of round */
    u64  cycle_mstamp;        /* time of this cycle phase start */

    // Mode and state flags (packed into 32 bits)
    u32  mode:3;              /* BBR_STARTUP/DRAIN/PROBE_BW/PROBE_RTT */
    u32  prev_ca_state:3;
    u32  packet_conservation:1;
    u32  round_start:1;
    u32  idle_restart:1;
    u32  probe_rtt_round_done:1;
    u32  lt_is_sampling:1;
    u32  lt_rtt_cnt:7;
    u32  lt_use_bw:1;

    u32  lt_bw;               /* LT est delivery rate */
    u32  lt_last_delivered;
    u32  lt_last_stamp;
    u32  lt_last_lost;

    u32  pacing_gain:10;      /* current pacing gain */
    u32  cwnd_gain:10;        /* current cwnd gain */
    u32  full_bw_reached:1;
    u32  full_bw_cnt:2;
    u32  cycle_idx:3;
    u32  has_seen_rtt:1;

    u32  prior_cwnd;
    u32  full_bw;
};
```

### 3.3 Key Constants

```c
BBR_UNIT = 256  // Fixed-point scaling
bbr_high_gain = BBR_UNIT * 2885 / 1000 + 1  // ≈ 2.89 (doubles per RTT in startup)
bbr_drain_gain = BBR_UNIT * 1000 / 2885      // ≈ 0.35 (drains queue)
bbr_cwnd_gain = BBR_UNIT * 2                  // = 2.0 (steady-state cwnd gain)
bbr_pacing_gain[] = {1.25, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0}  // PROBE_BW cycle
bbr_probe_rtt_mode_ms = 200  // Time spent in PROBE_RTT
```

### 3.4 State Machine

```
STARTUP → DRAIN → PROBE_BW ↔ PROBE_RTT
   ↑         ↓         ↑           ↓
   └─────────┴─────────┴───────────┘
```

### 3.5 bbr_init()

**File:** `net/ipv4/tcp_bbr.c`, lines 1039-1079

```c
__bpf_kfunc static void bbr_init(struct sock *sk)
{
    bbr->prior_cwnd = 0;
    tp->snd_ssthresh = TCP_INFINITE_SSTHRESH;
    bbr->rtt_cnt = 0;
    bbr->min_rtt_us = tcp_min_rtt(tp);
    bbr->min_rtt_stamp = tcp_jiffies32;

    minmax_reset(&bbr->bw, 0, 0);

    bbr->full_bw_reached = 0;
    bbr->full_bw = 0;
    bbr->full_bw_cnt = 0;

    bbr_reset_startup_mode(sk);

    cmpxchg(&sk->sk_pacing_status, SK_PACING_NONE, SK_PACING_NEEDED);
}
```

### 3.6 Gain Settings by Mode

| Mode | pacing_gain | cwnd_gain | Purpose |
|------|-------------|-----------|---------|
| STARTUP | 2.89 | 2.89 | Double per RTT until pipe full |
| DRAIN | 0.35 | 2.89 | Drain queue created in startup |
| PROBE_BW | cycle [1.25,0.75,1,...] | 2.0 | Discover/share bandwidth |
| PROBE_RTT | 1.0 | 1.0 | Measure true min_rtt |

---

## 4. DCTCP

### 4.1 Overview

DCTCP (Data Center TCP) uses ECN marks to get multi-bit congestion feedback. It maintains an estimate of the fraction of bytes that experienced congestion.

### 4.2 struct dctcp

**File:** `net/ipv4/tcp_dctcp.c`, lines 49-58

```c
struct dctcp {
    u32 old_delivered;       /* delivered at start of measurement period */
    u32 old_delivered_ce;   /* CE-marked packets delivered */
    u32 prior_rcv_nxt;       /* rcv_nxt at ECN event */
    u32 dctcp_alpha;         /* congestion estimate (0-1024) */
    u32 next_seq;            /* sequence number for RTT boundary */
    u32 ce_state;            /* Current CE state (0 or 1) */
    u32 loss_cwnd;           /* cwnd at loss for undo */
    struct tcp_plb_state plb; /* Probabilistic Latency Billing (PLB) */
};
```

### 4.3 Mathematical Formula

```
alpha_new = (1 - g) * alpha_old + g * F
where:
  g = 1/2^dctcp_shift_g (default g = 1/16)
  F = delivered_ce / delivered (fraction marked)
```

### 4.4 DCTCP vs Standard TCP

| Scenario | Standard TCP | DCTCP |
|----------|-------------|-------|
| Mild congestion (1% marks) | No reaction | cwnd *= (1 - 0.005) |
| Moderate congestion (10% marks) | Linear decrease | cwnd *= (1 - 0.05) |
| Severe congestion (50% marks) | cwnd halved | cwnd *= (1 - 0.25) |

---

## 5. TCP Reno

### 5.1 The Algorithm

**File:** `net/ipv4/tcp_cong.c`, lines 496-511

```c
__bpf_kfunc void tcp_reno_cong_avoid(struct sock *sk, u32 ack, u32 acked)
{
    if (!tcp_is_cwnd_limited(sk))
        return;

    if (tcp_in_slow_start(tp)) {
        acked = tcp_slow_start(tp, acked);
        if (!acked)
            return;
    }
    tcp_cong_avoid_ai(tp, tcp_snd_cwnd(tp), acked);
}
```

### 5.2 Slow Start vs Congestion Avoidance

- **Slow Start**: cwnd doubles per RTT (exponential)
- **CA**: cwnd += 1/cwnd per ACK (linear)
- **Loss**: cwnd = cwnd / 2 (multiplicative decrease)

---

## 6. Highspeed TCP

### 6.1 Overview

RFC 3649 HighSpeed TCP modifies the AIMD parameters for high-bandwidth paths. Standard TCP's 0.5 multiplicative decrease is too conservative for paths with large bandwidth-delay products.

### 6.2 hstcp_aimd_vals Table

**File:** `net/ipv4/tcp_highspeed.c`, lines 16-92

The table contains 92 entries of (cwnd, md) pairs transitioning from:
- **Low cwnd (< 38)**: Standard TCP (a=1, md=0.5)
- **High cwnd (> 60000)**: Aggressive (a≈30, md≈0.1)

---

## 7. TCP Vegas

### 7.1 Overview

Vegas (1994) was one of the first delay-based congestion control algorithms. It detects congestion by measuring the difference between actual throughput and expected throughput based on RTT.

### 7.2 The Core Algorithm

```c
// Expected cwnd = (actual rate) * baseRTT
target_cwnd = tcp_snd_cwnd(tp) * vegas->baseRTT / rtt;

// Diff represents queueing delay
diff = tcp_snd_cwnd(tp) * (rtt - vegas->baseRTT) / vegas->baseRTT;
```

**Decision Logic:**
- diff > beta: decrease cwnd (too fast)
- diff < alpha: increase cwnd (can send faster)
- alpha <= diff <= beta: just right

### 7.3 Why Vegas Doesn't Work Well

1. **Competing fairly**: Vegas reduces cwnd when RTT increases, but loss-based algorithms increase cwnd until loss. This makes Vegas "lose" bandwidth to Reno.
2. **Queuing delay sensitivity**: Small RTT variations can cause incorrect decisions.

---

## 8. TCP Illinois

### 8.1 Overview

Illinois (2008) is a delay-based algorithm that uses a convex window growth function. It adapts alpha and beta based on RTT measurements.

### 8.2 Adaptive Parameters

- **Low delay (uncongested)**: alpha=10, beta=0.125 → aggressive increase, gentle decrease
- **High delay (congested)**: alpha=0.3, beta=0.5 → conservative increase, steep decrease

---

## 9. TCP Hybla

### 9.1 Overview

Hybla is designed for satellite networks and other heterogeneous networks with high latency. It compensates for long RTTs by scaling the congestion control parameters.

### 9.2 rho Parameter

```c
// rho = current_rtt / reference_rtt (scaled by 8)
// rtt0 = reference RTT (default 25ms)
ca->rho_3ls = max_t(u32, tp->srtt_us / (rtt0 * USEC_PER_MSEC), 8U);
```

For a reference RTT of 25ms:
- **rho = 1**: Connection matches reference → standard TCP behavior
- **rho = 4**: 100ms RTT (satellite) → increments are 16x larger
- **rho = 8**: 200ms RTT → increments are 64x larger

---

## 10. YeAH-TCP

### 10.1 Overview

YeAH (Yet another Highspeed TCP) combines ideas from Reno, Vegas, and HighSpeed. It uses a "fake low RTT" detection to decide when to use aggressive vs. conservative increase.

### 10.2 Key Parameters

- `TCP_YEAH_ALPHA = 80`: Queue threshold for reduction
- `TCP_YEAH_GAMMA = 1`: Queue reduction per RTT
- `TCP_YEAH_DELTA = 3`: Log fraction removed on loss (cwnd >> 3)

---

## Summary

| Algorithm | Type | Key Signal | File |
|-----------|------|------------|------|
| Reno | Loss-based | Packet loss | tcp_cong.c |
| CUBIC | Loss-based | Packet loss (cubic function) | tcp_cubic.c |
| BBR | Model-based | Bandwidth + RTT | tcp_bbr.c |
| DCTCP | ECN-based | ECN marks | tcp_dctcp.c |
| Vegas | Delay-based | RTT difference | tcp_vegas.c |
| Illinois | Delay-based | RTT gradient | tcp_illinois.c |
| Hybla | Delay-based | RTT scaling | tcp_hybla.c |
| Highspeed | Loss-based | High cwnd tables | tcp_highspeed.c |
| YeAH | Hybrid | Queue + loss | tcp_yeah.c |
