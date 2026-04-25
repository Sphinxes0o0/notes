# Linux Kernel Networking RFC Implementations

## Table of Contents
1. [TCP RFC Implementations](#1-tcp-rfc-implementations)
2. [BBR (Bottleneck Bandwidth and RTT) Paper Implementation](#2-bbr-bottleneck-bandwidth-and-rtt-paper-implementation)
3. [CUBIC Paper Implementation](#3-cubic-paper-implementation)
4. [DCTCP (Data Center TCP)](#4-dctcp-data-center-tcp)
5. [MPTCP (MultiPath TCP)](#5-mptcp-multipath-tcp)
6. [IP RFCs](#6-ip-rfcs)

---

## 1. TCP RFC Implementations

### 1.1 RFC 793 (TCP) - Core Protocol

#### 3-Way Handshake Implementation

The TCP 3-way handshake is implemented across several key functions:

**Connection Request Processing (SYN reception):**
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_input.c`
- Function: `tcp_conn_request()` at line 7640

```c
int tcp_conn_request(struct request_sock_ops *rsk_ops,
		     const struct tcp_request_sock_ops *af_ops,
		     struct sock *sk, struct sk_buff *skb)
// Lines 7640-7818
```

Key steps in the 3-way handshake:
1. **SYN received** (line 7200-7207): Listener processes incoming SYN
2. **SYN-ACK sent** (line 7798-7800): `af_ops->send_synack()` is called
3. **ACK received** (line 7268-7315): Connection transitions to ESTABLISHED state

**SYN-SENT State Processing (Active Open):**
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_input.c`
- Function: `tcp_rcv_synsent_state_process()` at line 6760
- Called from `tcp_rcv_state_process()` at line 7215

**Child Socket Creation:**
- File: `/Users/sphinx/github/linux/net/ipv4/tcp.c`
- Function: `tcp_create_openreq_child()` at line 549
- Creates the new socket after 3-way handshake completes

#### TCP State Machine

The TCP state machine is implemented in:
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_input.c`
- Function: `tcp_rcv_state_process()` at line 7170

**State transitions handled:**
- `TCP_CLOSE` (line 7180-7182)
- `TCP_LISTEN` (line 7184-7210)
- `TCP_SYN_SENT` (line 7212-7223)
- `TCP_SYN_RECV` (line 7269-7315)
- `TCP_FIN_WAIT1` (line 7317-7339)
- `TCP_FIN_WAIT2` (line 7340-7360)
- `TCP_TIME_WAIT` (handled in `/Users/sphinx/github/linux/net/ipv4/tcp.c`)

**Sequence Number Handling:**
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_minisocks.c`
- Function: `tcp_timewait_state_process()` at line 100
- PAWS (Protect Against Wrapped Sequence numbers) check at lines 109-130

#### TCP Sequence Numbers

- **snd_nxt**: Send next sequence number (`tcp_snd_nxt`)
- **snd_una**: Send unacknowledged (`tp->snd_una`)
- **rcv_nxt**: Receive next expected (`tp->rcv_nxt`)

---

### 1.2 RFC 5961 (TCP) - Blind Reset Attack Mitigation

RFC 5961 mitigates blind reset/injection attacks. The kernel implements this in:

#### Blind RST Mitigation
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_ipv4.c`
- Function: `tcp_v4_send_reset()` at line 740

Key security checks:
```c
// Line 761-763: Never send reset in response to a reset
if (th->rst)
    return;

// Line 768-769: Only send reset for local traffic or with valid route
if (!sk && skb_rtable(skb)->rt_type != RTN_LOCAL)
    return;
```

#### Blind SYN Attack Mitigation
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_input.c`
- Function: `tcp_conn_request()` at line 7640
- The function implements challenge ACK mechanism (line 7750-7754)

**mitigation for SYN blind attacks:**
- Line 7746: `isn = st.seq` - sequence number generation
- Lines 7730-7743: Check for proven connections before queueing

#### RST Attack Mitigation
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_ipv4.c`
- The `tcp_v4_send_reset()` function validates sequence numbers before sending RST
- Sequence validation ensures RST packets are only sent for valid connections

---

### 1.3 RFC 5962 (TCP) - Advanced ACK (TCP Authentication Option)

TCP-AO (Authentication Option) implementation for RFC 5962:

#### TCP-AO Implementation
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_ao.c`
- Key structures and functions:
  - `tcp_ao_info` structure for AO state
  - `tcp_ao_key` structure for cryptographic keys
  - `tcp_ao_transmit_skb()` at line 809
  - `tcp_ao_verify_hash()` at line 901

**TCP-AO matching for Authentication Option:**
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_input.c`
- Function: `tcp_parse_options()` processes TCP options including AO
- The kernel checks `TCP_AUTHENTICATION_OPTION` compliance at connection establishment

**Key Functions:**
- `tcp_v4_ao_lookup()` - Line 714 in tcp_ao.c
- `tcp_v4_ao_synack_hash()` - Line 680 in tcp_ao.c
- `tcp_ao_prepare_reset()` - Line 724 in tcp_ao.c

---

### 1.4 RFC 9293 (TCP) - Updated TCP Specification

RFC 9293 obsoletes RFC 793. Key differences implemented:

#### Extended Error Handling
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_ipv4.c`
- RST reason codes implemented at line 740
- `sk_rst_convert_drop_reason()` function for error mapping

#### Enhanced State Machine
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_input.c`
- `tcp_rcv_state_process()` handles all RFC 9293 states

#### RFC 9293 Compliance Features:
- **Sequence number validation** (lines 844-868 in tcp_input.c)
- **RST processing** with proper sequence checking
- **Time wait handling** improvements

---

### 1.5 RFC 5681 (Congestion Control) - RFC 2581 Update

Congestion control implementations follow RFC 5681:

#### Slow Start Implementation
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_cong.c`
- Function: `tcp_slow_start()` at line 456

```c
__bpf_kfunc u32 tcp_slow_start(struct tcp_sock *tp, u32 acked)
// Lines 456-465
// Increases cwnd by at most 2 * mss per ACK
```

**Implementation details:**
- Line 457: `cwnd += min(acked, 2 * mss)` - RFC 5681 compliant
- Exponential increase during slow start
- Controlled by `sysctl_tcp_slow_start_after_idle` (line 3544 in tcp_ipv4.c)

#### Congestion Avoidance Implementation
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_cong.c`
- Function: `tcp_cong_avoid_ai()` at line 470

```c
__bpf_kfunc void tcp_cong_avoid_ai(struct tcp_sock *tp, u32 w, u32 acked)
// Lines 470-488
// Increases cwnd linearly: cwnd += mss * mss / cwnd
```

**RFC 5681 compliant cwnd increase:**
- Line 506: `tcp_cong_avoid()` at line 3513 in tcp_input.c
- Called during ACK processing in `tcp_ack()` at line 3873

---

### 1.6 RFC 3517 (SACK - Selective Acknowledgment)

SACK block handling implementation:

#### SACK Processing
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_input.c`
- Function: `tcp_sacktag_walk()` at line 2092

```c
static struct sk_buff *tcp_sacktag_walk(struct sk_buff *skb, struct sock *sk,
					struct tcp_sack_block *next_dup,
					struct tcp_sacktag_state *state,
					u32 start_seq, u32 end_seq,
					bool dup_sack_in)
// Lines 2092-2163
```

**Key SACK functions:**
- `tcp_sacktag_write_queue()` at line 2220 - Main SACK processing
- `tcp_sacktag_bsearch()` at line 2165 - Binary search for SACK blocks
- `tcp_check_dsack()` at line 2481 - Duplicate SACK detection
- `tcp_match_skb_to_sack()` - Matches SKBs to SACK ranges

**SACK Block Structure:**
- File: `/Users/sphinx/github/linux/include/net/tcp.h`
- `struct tcp_sack_block` with start_seq and end_seq

**FACK (Forward Acknowledgment) Support:**
- `tcp_highest_sack_seq()` - Returns highest SACKed sequence
- `tcp_advance_highest_sack()` - Advances highest SACK pointer

---

### 1.7 RFC 7323 (TCP Window Scaling)

Window scaling implementation:

#### Window Scaling Factor
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_output.c`
- Function: `tcp_select_initial_window()` at line 229

```c
void tcp_select_initial_window(const struct sock *sk, int __space, __u32 mss,
			       __u32 *rcv_wnd, __u32 *__window_clamp,
			       int wscale_ok, __u8 *rcv_wscale,
			       __u32 init_rcv_wnd)
// Lines 229-275
```

**Window scaling implementation:**
- Line 262-269: Calculate receive window scaling factor
- Maximum scale factor: `TCP_MAX_WSCALE` (14 bits per RFC 7323)
- Scale factor stored in `tp->rx_opt.rcv_wscale`

**snd_wnd (Send Window) Handling:**
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_input.c`
- Line 7299: `tp->snd_wnd = ntohs(th->window) << tp->rx_opt.snd_wscale`
- Line 7076-7078: Initial window received from peer
- Line 7299: Scale applied when receiving

**Receive Window Updates:**
- `tcp_receive_window()` at line 3316 in tcp_output.c
- `__tcp_select_window()` - Returns scaled window

---

### 1.8 RFC 1323 (PAWS and Timestamps)

PAWS (Protect Against Wrapped Sequence numbers) and timestamps:

#### Timestamp Implementation
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_input.c`
- **ts_recent storage**: `tp->rx_opt.ts_recent` (line 6578)
- **ts_recent_stamp**: `tp->rx_opt.ts_recent_stamp` (timestamp of last update)

**Timestamp update functions:**
- `tcp_store_ts_recent()` at line 4076
- `__tcp_replace_ts_recent()` at line 4082
- `tcp_replace_ts_recent()` at line 4088

**PAWS Check:**
- `tcp_paws_check()` at line 6351
- `tcp_paws_reject()` - Rejects segments with old timestamps

**Timestamp option processing:**
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_input.c`
- Lines 7526: `req->ts_recent = rx_opt->saw_tstamp ? rx_opt->rcv_tsval : 0`
- Line 620-621 in tcp_minisocks.c: Sets ts_recent on child socket

**Timestamp in TIME_WAIT:**
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_minisocks.c`
- Lines 348-349: `tw_ts_recent` and `tw_ts_recent_stamp` preserved

**Timestamp Echo (tsecr):**
- File: `/Users/sphinx/github/linux/net/ipv4/tcp_output.c`
- Line 996: `opts->tsecr = tp->rx_opt.ts_recent`
- Line 1107: For SYNACK packets

---

## 2. BBR (Bottleneck Bandwidth and RTT) Paper Implementation

Paper: "BBR: Congestion-Based Congestion Control" (Cardwell et al., ACM Queue 2016)

### File Location
`/Users/sphinx/github/linux/net/ipv4/tcp_bbr.c`

### BBR State Machine

**State Transition Diagram (lines 17-46):**
```
STARTUP -> DRAIN -> PROBE_BW -> PROBE_RTT
  ^                       |           |
  |                       +-----------+---+
  +--------------------------------------+
```

**BBR Modes (lines 81-86):**
```c
enum bbr_mode {
    BBR_STARTUP,    /* ramp up sending rate rapidly to fill pipe */
    BBR_DRAIN,      /* drain any queue created during startup */
    BBR_PROBE_BW,   /* discover, share bw: pace around estimated bw */
    BBR_PROBE_RTT,  /* cut inflight to min to probe min_rtt */
};
```

### Bandwidth (BBR.bw) Tracking

**Structure (lines 89-128):**
```c
struct bbr {
    u32 min_rtt_us;          /* min RTT in min_rtt_win_sec window */
    u32 min_rtt_stamp;       /* timestamp of min_rtt_us */
    struct minmax bw;         /* Max recent delivery rate in pkts/uS << 24 */
    u32 rtt_cnt;             /* count of packet-timed rounds elapsed */
    // ... additional fields
};
```

**bw calculation (lines 215-228):**
- `bbr_max_bw()` - Returns windowed max bandwidth
- `bbr_bw()` - Returns estimated bandwidth (either lt_bw or max_bw)
- Uses `minmax` for tracking maximum delivery rate

### RTT (min_rtt) Tracking

**Function: `bbr_update_min_rtt()` at line 941:**
```c
static void bbr_update_min_rtt(struct sock *sk, const struct rate_sample *rs)
// Lines 941-985
```

- Window: `bbr_min_rtt_win_sec = 10` seconds (line 135)
- Updates `min_rtt_us` when new RTT sample is lower
- Transitions to PROBE_RTT mode when min_rtt expires (line 957-959)

### Pacing Rate Calculation

**Function: `bbr_bw_to_pacing_rate()` at line 256:**
```c
static unsigned long bbr_bw_to_pacing_rate(struct sock *sk, u32 bw, int gain)
// Lines 256-263
```

- Formula: `pacing_rate = bw * gain * mss`
- Applied in `bbr_set_pacing_rate()` at line 286

**Gains (lines 154-167):**
- `bbr_high_gain = 2.885` (2885/1000) for STARTUP
- `bbr_drain_gain = 0.347` (1000/2885) for DRAIN
- `bbr_cwnd_gain = 2.0` for steady-state cwnd
- PROBE_BW cycle: `[1.25, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]`

### BBR State Transitions

**STARTUP -> DRAIN (line 897-900):**
```c
if (bbr->mode == BBR_STARTUP && bbr_full_bw_reached(sk)) {
    bbr->mode = BBR_DRAIN;  /* drain queue we created */
```

**DRAIN -> PROBE_BW (line 902-905):**
```c
if (bbr->mode == BBR_DRAIN &&
    bbr_packets_in_net_at_edt(...) <= bbr_inflight(...))
    bbr_reset_probe_bw_mode(sk);  /* we estimate queue is drained */
```

**PROBE_BW Gain Cycling (lines 554-607):**
- `bbr_is_next_cycle_phase()` - Determines when to advance cycle
- `bbr_advance_cycle_phase()` - Advances pacing gain index
- Cycle length: 8 phases (CYCLE_LEN = 8)

**PROBE_RTT Mode (lines 908-979):**
- Enters when min_rtt not updated for 10 seconds
- Cwnd capped at `bbr_cwnd_min_target = 4` packets (line 175)
- Exits after 200ms (`bbr_probe_rtt_mode_ms`) and inflight <= 4 packets

### Cwnd Calculation

**Function: `bbr_set_cwnd()` at line 519:**
```c
static void bbr_set_cwnd(struct sock *sk, const struct rate_sample *rs,
			 u32 acked, u32 bw, u32 gain)
// Lines 519-555
```

- `target_cwnd = bbr_bdp(sk, bw, gain)` - Bandwidth-delay product
- `bbr_quantization_budget()` - Adds quantization overhead
- Minimum cwnd: `bbr_cwnd_min_target = 4` packets

### Long-Term Bandwidth Estimation (LT)

**Functions (lines 688-757):**
- `bbr_lt_bw_sampling()` - Samples delivery rate during loss intervals
- `bbr_lt_bw_interval_done()` - Determines if LT interval is complete
- Detects traffic policers (line 682 comment)

---

## 3. CUBIC Paper Implementation

Paper: "CUBIC: A New TCP-Friendly High-Speed TCP Variant" (Ha et al., ACM SIGOPS 2008)

### File Location
`/Users/sphinx/github/linux/net/ipv4/tcp_cubic.c`

### CUBIC Function Implementation

**Parameters (lines 34-63):**
```c
#define BICTCP_BETA_SCALE    1024  /* max_cwnd = snd_cwnd * beta */
#define BICTCP_HZ           10     /* 2^10 = 1024 */

// Default values:
beta = 717  /* = 717/1024 (0.7) */
bic_scale = 41
fast_convergence = 1
tcp_friendliness = 1
```

**CUBIC Update Function (lines 214-362):**
```c
static inline void bictcp_update(struct bictcp *ca, u32 cwnd, u32 acked)
```

**CUBIC Algorithm (lines 235-330):**
1. **Epoch start detection** (line 235-240): New congestion epoch
2. **K calculation** (line 247-249): Time to reach Wmax
   - `K = cubic_root((last_max_cwnd - cwnd) * cube_factor)`
3. **Target cwnd calculation** (lines 250-268):
   - `(t - K)^3` where t = time since epoch start
   - Cubic function for concave/convex profile
4. **TCP friendliness** (lines 306-329): Blend with Reno-style increase

### HyStart (Hybrid Slow Start)

**HyStart parameters (lines 55-58):**
```c
hystart = 1  /* enabled by default */
hystart_detect = HYSTART_ACK_TRAIN | HYSTART_DELAY
hystart_low_window = 16  /* cwnd threshold */
hystart_ack_delta_us = 2000  /* ack train detection */
```

**Detection Mechanisms:**
- **ACK Train** (HYSTART_ACK_TRAIN): Detects if ACK spacing < threshold
- **Delay** (HYSTART_DELAY): Detects RTT increase

**Functions:**
- `bictcp_hystart_reset()` at line 118
- `hystart_ack_delay()` at line 375
- `hystart_update()` at line 386

### CUBIC vs Reno Comparison

**TCP Friendliness (lines 50-53, 306-329):**
```c
tcp_friendliness = 1
```
- When enabled, CUBIC blends with Reno to remain TCP-friendly
- `ca->tcp_cwnd` estimates standard Reno cwnd

---

## 4. DCTCP (Data Center TCP)

Paper: "Data Center TCP (DCTCP)" (Alizadeh et al., ACM SIGCOMM 2010)

### File Location
`/Users/sphinx/github/linux/net/ipv4/tcp_dctcp.c`

### DCTCP Algorithm

**DCTCP Structure (lines 49-58):**
```c
struct dctcp {
    u32 old_delivered;
    u32 old_delivered_ce;
    u32 prior_rcv_nxt;
    u32 dctcp_alpha;      /* EWMA of ECN marked fraction */
    u32 next_seq;
    u32 ce_state;          /* Current CE state */
    u32 loss_cwnd;
    struct tcp_plb_state plb;
};
```

**Alpha Update (lines 127-170):**
```c
__bpf_kfunc static void dctcp_update_alpha(struct sock *sk, u32 flags)
// Lines 127-170
```

- `alpha = (1 - g) * alpha + g * ce_ratio`
- `g = 1/2^4` (shift_g = 4) by default
- `ce_ratio = delivered_ce / delivered` (fraction of ECN-marked packets)

**Cwnd Calculation (lines 118-125):**
```c
__bpf_kfunc static u32 dctcp_ssthresh(struct sock *sk)
{
    struct dctcp *ca = inet_csk_ca(sk);
    struct tcp_sock *tp = tcp_sk(sk);

    ca->loss_cwnd = tcp_snd_cwnd(tp);
    return max(tcp_snd_cwnd(tp) -
               ((tcp_snd_cwnd(tp) * ca->dctcp_alpha) >> 11U), 2U);
}
```

**Alpha max value:** `DCTCP_MAX_ALPHA = 1024` (line 47)

### ECN CE Codepoint Handling

**File:** `/Users/sphinx/github/linux/net/ipv4/tcp_dctcp.h`

```c
static inline void dctcp_ece_ack_cwr(struct sock *sk, u32 ce_state)
// Lines 4-10
```

- Called when ECE flag received (congestion experienced)
- Updates `ce_state` for tracking

**DCTCP State Machine (lines 183-214):**
```c
__bpf_kfunc static void dctcp_state(struct sock *sk, u8 new_state)
{
    struct dctcp *ca = inet_csk_ca(sk);

    if (new_state == TCP_CA_Loss)
        dctcp_react_to_loss(sk);
}
```

### PLB (Packet Loss Backoff) Integration

**PLB State (line 57):**
```c
struct tcp_plb_state plb;
```

**PLB Functions:**
- `tcp_plb_init()` - Initializes PLB state
- `tcp_plb_update_state()` - Updates based on CE ratio
- `tcp_plb_check_rehash()` - Checks if rehash is needed

---

## 5. MPTCP (MultiPath TCP)

### File Location
`/Users/sphinx/github/linux/net/mptcp/`

### Key Files:
- `protocol.c` - Main MPTCP protocol implementation
- `protocol.h` - Core data structures
- `subflow.c` - Subflow management
- `pm.c` - Path manager
- `options.c` - MPTCP options parsing

### MPTCP Option Types (protocol.h, lines 19-35)

```c
#define OPTION_MPTCP_MPC_SYN    BIT(0)  /* MP_CAPABLE with SYN */
#define OPTION_MPTCP_MPC_SYNACK BIT(1)  /* MP_CAPABLE with SYN-ACK */
#define OPTION_MPTCP_MPC_ACK    BIT(2)  /* MP_CAPABLE with ACK */
#define OPTION_MPTCP_MPJ_SYN    BIT(3)  /* MP_JOIN with SYN */
#define OPTION_MPTCP_MPJ_SYNACK BIT(4)  /* MP_JOIN with SYN-ACK */
#define OPTION_MPTCP_MPJ_ACK    BIT(5)  /* MP_JOIN with ACK */
#define OPTION_MPTCP_ADD_ADDR   BIT(6)  /* ADD_ADDR */
#define OPTION_MPTCP_RM_ADDR    BIT(7)  /* REMOVE_ADDR */
#define OPTION_MPTCP_DSS        BIT(11) /* DSS (Data Sequence Signal) */
```

### Subflow Context (protocol.h)

```c
struct mptcp_subflow_context {
    // ... subflow-specific fields
    u8  local_id;     /* Local address ID */
    u8  remote_id;    /* Remote address ID */
    // ...
};
```

### Subflow Management

**File:** `/Users/sphinx/github/linux/net/mptcp/pm_kernel.c`

**Address Selection Functions:**
- `fill_remote_addr()` at line 180 - Selects remote address for new subflow
- `fill_local_addresses_vec()` at line 619 - Selects local addresses
- `select_signal_address()` at line 149 - Selects address for signaling

**Subflow Creation:**
- `__mptcp_subflow_connect()` - Creates new subflow connection
- `mptcp_pm_create_subflow_or_signal_addr()` at line 329 - Manages subflow creation

**Path Manager Interface:**
- `mptcp_pm_nl_fully_established()` at line 433
- `mptcp_pm_nl_subflow_established()` at line 438
- `mptcp_pm_nl_add_addr_received()` at line 643

### DSS (Data Sequence Signal) Mapping

**MPTCP Data Sequence Number (DSN):**
- File: `/Users/sphinx/github/linux/net/mptcp/protocol.h`
- `struct mptcp_skb_cb` (lines 128-134):
```c
struct mptcp_skb_cb {
    u64 map_seq;    /* Data sequence number mapping */
    u64 end_seq;    /* End sequence of mapping */
    u32 offset;     /* Offset in data sequence space */
    u8  has_rxtstamp;
    u8  cant_coalesce;
};
```

### Subflow Scheduling

**File:** `/Users/sphinx/github/linux/net/mptcp/sched.c`

**Scheduling Algorithms:**
- Default: Round-robin among subflows
- `mptcp_sched_dequeue()` - Dequeues from selected subflow

---

## 6. IP RFCs

### 6.1 RFC 791 (IP) - Core Protocol

#### Fragmentation
- File: `/Users/sphinx/github/linux/net/ipv4/ip_fragment.c`
- Function: `ip_fragment()` at line 576

```c
static int ip_fragment(struct net *net, struct sock *sk, struct sk_buff *skb,
		       unsigned int mtu, int (*output)(struct net *, struct sock *, struct sk_buff *))
// Lines 576-...
```

**Defragmentation:**
- Function: `ip_defrag()` at line 473
- Queue structure: `struct ipq` (lines 61-69)

#### TTL Handling
- File: `/Users/sphinx/github/linux/net/ipv4/ip_output.c`
- Function: `ip_select_ttl()` at line 137

```c
static inline int ip_select_ttl(const struct inet_sock *inet,
				const struct dst_entry *dst)
{
    int ttl = READ_ONCE(inet->uc_ttl);
    if (ttl < 0)
        ttl = ip4_dst_hoplimit(dst);
    return ttl;
}
```

**TTL Setting (line 167):**
```c
iph->ttl = ip_select_ttl(inet, &rt->dst);
```

#### IP ID Field
- File: `/Users/sphinx/github/linux/net/ipv4/ip_fragment.c`
- Used for fragment reassembly identification
- `ipq.rid` field (line 67) tracks fragment ID

### 6.2 IP Options Handling
- File: `/Users/sphinx/github/linux/net/ipv4/ip_options.c`
- Parsed in `ip_options_compile()` and `ip_options_rcu_sock()`

### 6.3 Minimum TTL Enforcement
- File: `/Users/sphinx/github/linux/net/ipv4/ip_sockglue.c`
- `ip4_min_ttl` static key (line 890)
- Enforced at line 549-552 in tcp_ipv4.c:
```c
if (static_branch_unlikely(&ip4_min_ttl)) {
    if (unlikely(iph->ttl < READ_ONCE(inet_sk(sk)->min_ttl))) {
        __NET_INC_STATS(net, LINUX_MIB_TCPMINTTLDROP);
```

---

## Summary Table

| RFC/Paper | File | Key Functions |
|-----------|------|---------------|
| RFC 793 (TCP) | tcp_input.c, tcp.c, tcp_minisocks.c | tcp_conn_request(), tcp_rcv_state_process(), tcp_timewait_state_process() |
| RFC 5961 (TCP) | tcp_ipv4.c, tcp_input.c | tcp_v4_send_reset(), tcp_conn_request() |
| RFC 5962 (TCP-AO) | tcp_ao.c | tcp_ao_transmit_skb(), tcp_ao_verify_hash() |
| RFC 9293 (TCP) | tcp_ipv4.c, tcp_input.c | tcp_v4_send_reset(), tcp_rcv_state_process() |
| RFC 5681 (Congestion) | tcp_cong.c | tcp_slow_start(), tcp_cong_avoid_ai() |
| RFC 3517 (SACK) | tcp_input.c | tcp_sacktag_walk(), tcp_sacktag_write_queue() |
| RFC 7323 (Window Scaling) | tcp_output.c | tcp_select_initial_window(), tcp_select_window() |
| RFC 1323 (Timestamps) | tcp_input.c | tcp_store_ts_recent(), tcp_paws_check() |
| BBR | tcp_bbr.c | bbr_update_bw(), bbr_update_min_rtt(), bbr_set_cwnd() |
| CUBIC | tcp_cubic.c | bictcp_update(), hystart_update() |
| DCTCP | tcp_dctcp.c | dctcp_update_alpha(), dctcp_ssthresh() |
| MPTCP | mptcp/*.c | mptcp_subflow_connect(), mptcp_pm_*() |
| RFC 791 (IP) | ip_fragment.c, ip_output.c | ip_fragment(), ip_defrag(), ip_select_ttl() |
