Based on my thorough analysis of the Linux kernel TCP/IP protocol stack source code, here is the comprehensive research document:

# Linux Kernel TCP/IP Protocol Stack Analysis

## Table of Contents
1. [IP Protocol Layer](#1-ip-protocol-layer)
2. [TCP Protocol](#2-tcp-protocol)
3. [TCP State Machine](#3-tcp-state-machine)
4. [TCP Congestion Control](#4-tcp-congestion-control)
5. [TCP Timer Infrastructure](#5-tcp-timer-infrastructure)
6. [UDP Protocol](#6-udp-protocol)
7. [Network Header Access](#7-network-header-access)

---

## 1. IP Protocol Layer

### 1.1 `struct iphdr` - IP Header Structure

**Location:** `/Users/sphinx/github/linux/include/uapi/linux/ip.h` (lines 87-109)

```c
struct iphdr {
#if defined(__LITTLE_ENDIAN_BITFIELD)
    __u8    ihl:4,
            version:4;
#elif defined (__BIG_ENDIAN_BITFIELD)
    __u8    version:4,
            ihl:4;
#endif
    __u8    tos;            // Type of Service
    __be16  tot_len;        // Total length
    __be16  id;             // Identification
    __be16  frag_off;       // Fragment offset with flags
    __u8    ttl;            // Time to Live
    __u8    protocol;       // Protocol (TCP/UDP/ICMP)
    __sum16 check;          // Header checksum
    __be32  saddr;          // Source address
    __be32  daddr;          // Destination address
    /* The options start here. */
};
```

**Field Descriptions:**
- `version`: IP version (4 for IPv4)
- `ihl`: Internet Header Length, number of 32-bit words
- `tos`: Type of Service, includes DSCP (6 bits) and ECN (2 bits)
- `tot_len`: Total length of the datagram (header + data)
- `id`: Unique identifier for fragmentation reassembly
- `frag_off`: Fragment offset (13 bits) plus flags (MF, DF)
- `ttl`: Time to Live, decremented by each router
- `protocol`: Next layer protocol (IPPROTO_TCP=6, IPPROTO_UDP=17)
- `check`: IP header checksum for error detection
- `saddr/daddr`: Source and destination IPv4 addresses

### 1.2 `struct rtable` - Routing Table Entry

**Location:** `/Users/sphinx/github/linux/include/net/route.h` (lines 57-78)

```c
struct rtable {
    struct dst_entry    dst;        // Destination entry (must be first)
    int                 rt_genid;   // Routing generation ID
    unsigned int        rt_flags;   // Route flags (RTCF_xxx)
    __u16               rt_type;    // Route type (RTN_xxx)
    __u8                rt_is_input;    // Is input route
    __u8                rt_uses_gateway; // Uses gateway
    int                 rt_iif;          // Input interface index
    u8                  rt_gw_family;     // Address family of gateway
    union {
        __be32          rt_gw4;          // IPv4 gateway
        struct in6_addr rt_gw6;           // IPv6 gateway
    };
    u32                 rt_mtu_locked:1,  // MTU is locked
                        rt_pmtu:31;       // Path MTU
};
```

### 1.3 `ip_output()` - IP Packet Output Path

**Location:** `/Users/sphinx/github/linux/net/ipv4/ip_output.c` (lines 428-444)

```c
int ip_output(struct net *net, struct sock *sk, struct sk_buff *skb)
{
    struct net_device *dev, *indev = skb->dev;
    int ret_val;

    rcu_read_lock();
    dev = skb_dst_dev_rcu(skb);
    skb->dev = dev;
    skb->protocol = htons(ETH_P_IP);

    ret_val = NF_HOOK_COND(NFPROTO_IPV4, NF_INET_POST_ROUTING,
                net, sk, skb, indev, dev,
                ip_finish_output,
                !(IPCB(skb)->flags & IPSKB_REROUTED));
    rcu_read_unlock();
    return ret_val;
}
```

**Call Chain for IP Output:**
1. `ip_output()` - Entry point for local packets
2. `NF_HOOK_COND()` - Netfilter POST_ROUTING hook
3. `ip_finish_output()` - BPF cgroup egress check
4. `__ip_finish_output()` - Fragmentation/GSO handling
5. `ip_finish_output_gso()` or `ip_fragment()` - Segmentation
6. `ip_finish_output2()` - Layer 2 header preparation
7. `dst_output()` - Actual device transmission

### 1.4 `ip_rcv()` - IP Packet Input

**Location:** `/Users/sphinx/github/linux/net/ipv4/ip_input.c` (lines 564-576)

```c
int ip_rcv(struct sk_buff *skb, struct net_device *dev, struct packet_type *pt,
       struct net_device *orig_dev)
{
    struct net *net = dev_net(dev);

    skb = ip_rcv_core(skb, net);
    if (skb == NULL)
        return NET_RX_DROP;

    return NF_HOOK(NFPROTO_IPV4, NF_INET_PRE_ROUTING,
               net, NULL, skb, dev, NULL,
               ip_rcv_finish);
}
```

**Input Processing Chain:**
1. `ip_rcv()` - Packet received from network device
2. `ip_rcv_core()` - Validates IP header, checksums, version
3. `NF_HOOK()` - Netfilter PRE_ROUTING hook
4. `ip_rcv_finish()` - Routing decision
5. `ip_route_input_noref()` - Forward or local delivery
6. `ip_protocol_deliver_rcu()` - Demultiplex to protocol handler

### 1.5 `ip_fragment()` - IP Fragmentation

**Location:** `/Users/sphinx/github/linux/net/ipv4/ip_output.c` (lines 576-596)

```c
static int ip_fragment(struct net *net, struct sock *sk, struct sk_buff *skb,
               unsigned int mtu,
               int (*output)(struct net *, struct sock *, struct sk_buff *))
{
    struct iphdr *iph = ip_hdr(skb);

    if ((iph->frag_off & htons(IP_DF)) == 0)
        return ip_do_fragment(net, sk, skb, output);

    if (unlikely(!skb->ignore_df ||
                 (IPCB(skb)->frag_max_size &&
                  IPCB(skb)->frag_max_size > mtu))) {
        IP_INC_STATS(net, IPSTATS_MIB_FRAGFAILS);
        icmp_send(skb, ICMP_DEST_UNREACH, ICMP_FRAG_NEEDED, htonl(mtu));
        kfree_skb(skb);
        return -EMSGSIZE;
    }

    return ip_do_fragment(net, sk, skb, output);
}
```

**Key Points:**
- Respects DF (Don't Fragment) flag
- Calls `ip_do_fragment()` for actual fragmentation
- Sends ICMP Fragmentation Needed if DF is set and packet is too large

---

## 2. TCP Protocol

### 2.1 `struct tcphdr` - TCP Header Structure

**Location:** `/Users/sphinx/github/linux/include/uapi/linux/tcp.h` (lines 25-60)

```c
struct tcphdr {
    __be16  source;         // Source port
    __be16  dest;           // Destination port
    __be32  seq;            // Sequence number
    __be32  ack_seq;        // Acknowledgment number
#if defined(__LITTLE_ENDIAN_BITFIELD)
    __u16   ae:1,           // NS (Nonce Sum) - ECN
            res1:3,
            doff:4,          // Data offset (header length)
            fin:1,           // FIN flag
            syn:1,            // SYN flag
            rst:1,            // RST flag
            psh:1,            // PSH flag
            ack:1,            // ACK flag
            urg:1,            // URG flag
            ece:1,            // ECN Echo
            cwr:1;            // Congestion Window Reduced
#elif defined(__BIG_ENDIAN_BITFIELD)
    __u16   doff:4,
            res1:3,
            ae:1,
            cwr:1,
            ece:1,
            urg:1,
            ack:1,
            psh:1,
            rst:1,
            syn:1,
            fin:1;
#endif
    __be16  window;         // Receive window
    __sum16 check;           // Checksum
    __be16  urg_ptr;         // Urgent pointer
};
```

### 2.2 `struct tcp_sock` - TCP Socket Data

**Location:** `/Users/sphinx/github/linux/include/linux/tcp.h` (lines 197-527)

This is the main TCP socket structure, extending `inet_connection_sock`. Key fields:

**TX Read-Mostly Hotpath Cache Lines:**
```c
u32     max_window;        // Maximal window ever seen from peer
u32     rcv_ssthresh;       // Current window clamp
u32     reordering;         // Packet reordering metric
u32     notsent_lowat;      // TCP_NOTSENT_LOWAT
u16     gso_segs;           // Max number of segs per GSO packet
struct sk_buff *retransmit_skb_hint; // Retransmit queue hint
```

**TXRX Read-Mostly Hotpath Cache Lines:**
```c
u32     tsoffset;           // Timestamp offset
u32     snd_wnd;            // Window we expect to receive
u32     mss_cache;          // Cached effective MSS
u32     snd_cwnd;           // Sending congestion window
u32     prr_out;            // Total pkts sent during Recovery
u32     lost_out;           // Lost packets
u32     sacked_out;         // SACK'd packets
u16     tcp_header_len;     // Bytes of tcp header to send
u8      scaling_ratio;      // See tcp_win_from_space()
```

**Key Sequence/State Fields:**
```c
u32     rcv_nxt;           // What we want to receive next
u32     snd_nxt;            // Next sequence we send
u32     snd_una;           // First byte we want an ack for
u32     window_clamp;       // Maximal window to advertise
u32     srtt_us;           // Smoothed RTT << 3 in usecs
u32     packets_out;        // Packets in flight
```

**Congestion Control Fields:**
```c
u32     snd_ssthresh;       // Slow start threshold
u32     snd_cwnd_cnt;       // Linear increase counter
u32     snd_cwnd_clamp;     // Max snd_cwnd allowed
```

### 2.3 `struct tcp_request_sock` - TCP SYN Cookies

**Location:** `/Users/sphinx/github/linux/include/linux/tcp.h` (lines 150-182)

```c
struct tcp_request_sock {
    struct inet_request_sock  req;          // Base request sock
    const struct tcp_request_sock_ops *af_specific;
    u64             snt_synack;          // First SYNACK sent time
    bool            tfo_listener;          // Is Fast Open listener
    bool            is_mptcp;              // Is MPTCP
    bool            req_usec_ts;           // Use usec timestamps
#if IS_ENABLED(CONFIG_MPTCP)
    bool            drop_req;
#endif
    u32             txhash;               // TX hash for routing
    u32             rcv_isn;              // Received initial seq
    u32             snt_isn;              // Sent initial seq
    u32             ts_off;               // Timestamp offset
    u32             snt_tsval_first;       // First TSval sent
    u32             snt_tsval_last;        // Last TSval sent
    u32             last_oow_ack_time;     // Last SYNACK time
    u32             rcv_nxt;              // ACK# from SYNACK
    u8              syn_tos;              // SYN TOS
    bool            accecn_ok;            // AccECN OK
    u8              syn_ect_snt:2,        // SYN ECT sent
                    syn_ect_rcv:2,        // SYN ECT received
                    accecn_fail_mode:4;
    u8              saw_accecn_opt:2;      // Saw AccECN option
#ifdef CONFIG_TCP_AO
    u8              ao_keyid;              // TCP-AO key ID
    u8              ao_rcv_next;          // TCP-AO receive next
    bool            used_tcp_ao;          // Using TCP-AO
#endif
};
```

### 2.4 `tcp_v4_connect()` - TCP Connection Initiation

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_ipv4.c` (lines 222-320)

```c
int tcp_v4_connect(struct sock *sk, struct sockaddr_unsized *uaddr, int addr_len)
{
    struct sockaddr_in *usin = (struct sockaddr_in *)uaddr;
    struct inet_timewait_death_row *tcp_death_row;
    struct inet_sock *inet = inet_sk(sk);
    struct tcp_sock *tp = tcp_sk(sk);
    // ... variable declarations ...

    if (addr_len < sizeof(struct sockaddr_in))
        return -EINVAL;

    if (usin->sin_family != AF_INET)
        return -EAFNOSUPPORT;

    nexthop = daddr = usin->sin_addr.s_addr;
    // ... IP options handling ...

    // Route lookup for connection
    rt = ip_route_connect(fl4, nexthop, inet->inet_saddr,
                  sk->sk_bound_dev_if, IPPROTO_TCP, orig_sport,
                  orig_dport, sk);
    if (IS_ERR(rt)) {
        err = PTR_ERR(rt);
        if (err == -ENETUNREACH)
            IP_INC_STATS(net, IPSTATS_MIB_OUTNOROUTES);
        return err;
    }

    // ... address setup ...
    
    tcp_set_state(sk, TCP_SYN_SENT);  // Set state to SYN_SENT
    err = inet_hash_connect(tcp_death_row, sk);  // Add to hash tables
    
    // ... port/route setup ...
    
    // Build and send SYN
    err = tcp_connect(sk);  // Called to send the SYN packet
    
    return err;
}
```

**Connection Initiation Call Chain:**
1. `tcp_v4_connect()` - IPv4 connect entry point
2. `ip_route_connect()` - Routing table lookup
3. `tcp_set_state(TCP_SYN_SENT)` - Set socket state
4. `inet_hash_connect()` - Add to connection hash table
5. `tcp_connect()` - Build and transmit SYN

### 2.5 `tcp_sendmsg()` - TCP Send Path

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp.c` (lines 1460-1469)

```c
int tcp_sendmsg(struct sock *sk, struct msghdr *msg, size_t size)
{
    int ret;

    lock_sock(sk);
    ret = tcp_sendmsg_locked(sk, msg, size);
    release_sock(sk);

    return ret;
}
EXPORT_SYMBOL(tcp_sendmsg);
```

**Core send logic in `tcp_sendmsg_locked()` (lines 1130-1468):**

**Call Chain for TCP Send:**
1. `tcp_sendmsg()` - Acquires socket lock, calls locked version
2. `tcp_sendmsg_locked()` - Main send logic
3. `tcp_write_queue_tail()` - Get last skb in write queue
4. `tcp_mss()` - Calculate MSS for path
5. `tcp_push()` - Push data to network (with Nagle algorithm check)
6. `tcp_transmit_skb()` - Build and send TCP packet
7. `__tcp_transmit_skb()` - Actual transmission
8. `ip_queue_xmit()` - IP layer output
9. `ip_output()` - Network device output

### 2.6 `tcp_recvmsg()` - TCP Receive Path

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp.c` (lines 2965-2994)

```c
int tcp_recvmsg(struct sock *sk, struct msghdr *msg, size_t len, int flags,
        int *addr_len)
{
    int cmsg_flags = 0, ret;
    struct scm_timestamping_internal tss;

    if (unlikely(flags & MSG_ERRQUEUE))
        return inet_recv_error(sk, msg, len, addr_len);

    if (sk_can_busy_loop(sk) &&
        skb_queue_empty_lockless(&sk->sk_receive_queue) &&
        sk->sk_state == TCP_ESTABLISHED)
        sk_busy_loop(sk, flags & MSG_DONTWAIT);

    lock_sock(sk);
    ret = tcp_recvmsg_locked(sk, msg, len, flags, &tss, &cmsg_flags);
    release_sock(sk);
    // ... timestamp/INQ handling ...
    return ret;
}
EXPORT_IPV6_MOD(tcp_recvmsg);
```

**Receive Call Chain:**
1. `tcp_recvmsg()` - Entry point
2. `tcp_recvmsg_locked()` - Core receive logic
3. `skb_queue_empty_lockless()` - Check receive queue
4. `__skb_recv_udp()` (or TCP equivalent) - Dequeue from receive queue
5. `tcp_cleanup_rbuf()` - Window update, ACK generation

### 2.7 `tcp_rcv_state_process()` - TCP State Machine Processing

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_input.c` (lines 7170-7367)

```c
tcp_rcv_state_process(struct sock *sk, struct sk_buff *skb)
{
    struct tcp_sock *tp = tcp_sk(sk);
    struct inet_connection_sock *icsk = inet_csk(sk);
    const struct tcphdr *th = tcp_hdr(skb);
    struct request_sock *req;
    int queued = 0;

    switch (sk->sk_state) {
    case TCP_CLOSE:
        goto discard;

    case TCP_LISTEN:
        // Handle incoming connection request
        if (th->syn) {
            // Process SYN
            icsk->icsk_af_ops->conn_request(sk, skb);
            consume_skb(skb);
            return 0;
        }
        goto discard;

    case TCP_SYN_SENT:
        // Handle SYN response (for active open)
        queued = tcp_rcv_synsent_state_process(sk, skb, th);
        if (queued >= 0)
            return queued;
        // Fall through for further processing
    }

    // Established state processing
    // ... TCP established handling ...
    
    switch (sk->sk_state) {
    case TCP_SYN_RECV:
        // Complete three-way handshake
        tcp_set_state(sk, TCP_ESTABLISHED);
        // ... complete setup ...
        break;

    case TCP_FIN_WAIT1:
        // ... FIN handling ...
        tcp_set_state(sk, TCP_FIN_WAIT2);
        break;
        
    // ... other states ...
    }
}
```

**State Processing by State:**
- **TCP_CLOSE**: Drop packet
- **TCP_LISTEN**: Handle incoming SYN, rst, ack
- **TCP_SYN_SENT**: Process SYNACK response
- **TCP_ESTABLISHED**: Normal data transfer processing
- **TCP_FIN_WAIT1/2**: Handle incoming FIN
- **TCP_CLOSE_WAIT**: Handle close request
- **TCP_CLOSING/LAST_ACK/TIME_WAIT**: Connection close states

### 2.8 `tcp_transmit_skb()` - SKB Transmission

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_output.c` (lines 1708-1713)

```c
static int tcp_transmit_skb(struct sock *sk, struct sk_buff *skb, int clone_it,
                gfp_t gfp_mask)
{
    return __tcp_transmit_skb(sk, skb, clone_it, gfp_mask,
                  tcp_sk(sk)->rcv_nxt);
}
```

**`__tcp_transmit_skb()` (lines 1512-1705) Key Operations:**
1. Clone SKB if needed (line 1532-1540)
2. Set delivery time stamps
3. Build TCP header with options
4. Compute checksum
5. Call `ip_queue_xmit()` for IP layer output

---

## 3. TCP State Machine

### 3.1 TCP States

**Location:** `/Users/sphinx/github/linux/include/net/tcp_states.h` (lines 12-28)

```c
enum {
    TCP_ESTABLISHED = 1,    // Connection established
    TCP_SYN_SENT,           // Sent connection request
    TCP_SYN_RECV,           // Received request, sent ack
    TCP_FIN_WAIT1,          // Closed, waiting for FIN
    TCP_FIN_WAIT2,          // Waiting for remote FIN
    TCP_TIME_WAIT,          // Timeout after close
    TCP_CLOSE,              // Socket closed
    TCP_CLOSE_WAIT,         // Remote closed, waiting close
    TCP_LAST_ACK,          // Final ack before close
    TCP_LISTEN,            // Listening for connections
    TCP_CLOSING,           // Simultaneous close
    TCP_NEW_SYN_RECV,       // Fast SYN cookie handling
    TCP_BOUND_INACTIVE,     // Pseudo-state for inet_diag
    TCP_MAX_STATES
};
```

### 3.2 State Transition Actions

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp.c` (lines 2997-3065)

```c
void tcp_set_state(struct sock *sk, int state)
{
    int oldstate = sk->sk_state;

    // BPF notification if enabled
    if (BPF_SOCK_OPS_TEST_FLAG(tcp_sk(sk), BPF_SOCK_OPS_STATE_CB_FLAG))
        tcp_call_bpf_2arg(sk, BPF_SOCK_OPS_STATE_CB, oldstate, state);

    switch (state) {
    case TCP_ESTABLISHED:
        if (oldstate != TCP_ESTABLISHED)
            TCP_INC_STATS(sock_net(sk), TCP_MIB_CURRESTAB);
        break;
    case TCP_CLOSE_WAIT:
        if (oldstate == TCP_SYN_RECV)
            TCP_INC_STATS(sock_net(sk), TCP_MIB_CURRESTAB);
        break;
    case TCP_CLOSE:
        // Cleanup socket resources
        sk->sk_prot->unhash(sk);
        if (inet_csk(sk)->icsk_bind_hash &&
            !(sk->sk_userlocks & SOCK_BINDPORT_LOCK))
            inet_put_port(sk);
        fallthrough;
    default:
        if (oldstate == TCP_ESTABLISHED || oldstate == TCP_CLOSE_WAIT)
            TCP_DEC_STATS(sock_net(sk), TCP_MIB_CURRESTAB);
    }

    inet_sk_state_store(sk, state);
}
```

### 3.3 `tcp_fin()` - FIN Processing

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_input.c` (lines 4947-4999)

```c
void tcp_fin(struct sock *sk)
{
    struct tcp_sock *tp = tcp_sk(sk);

    inet_csk_schedule_ack(sk);
    WRITE_ONCE(sk->sk_shutdown, sk->sk_shutdown | RCV_SHUTDOWN);
    sock_set_flag(sk, SOCK_DONE);

    switch (sk->sk_state) {
    case TCP_SYN_RECV:
    case TCP_ESTABLISHED:
        // Move to CLOSE_WAIT
        tcp_set_state(sk, TCP_CLOSE_WAIT);
        inet_csk_enter_pingpong_mode(sk);
        break;

    case TCP_CLOSE_WAIT:
    case TCP_CLOSING:
        // Already in close state, ignore duplicate FIN
        break;

    case TCP_LAST_ACK:
        // Remain in LAST_ACK
        break;

    case TCP_FIN_WAIT1:
        // Simultaneous close - ack and enter CLOSING
        tcp_send_ack(sk);
        tcp_set_state(sk, TCP_CLOSING);
        break;

    case TCP_FIN_WAIT2:
        // Remote initiated close - enter TIME_WAIT
        tcp_set_state(sk, TCP_TIME_WAIT);
        tcp_time_wait(sk, TCP_TIME_WAIT, TCP_FIN_TIMEOUT);
        break;
    }
}
```

### 3.4 `tcp_reset()` - Connection Reset

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_input.c` (lines 4905-4931)

```c
void tcp_reset(struct sock *sk, struct sk_buff *skb)
{
    int err;

    trace_tcp_receive_reset(sk);

    if (sk_is_mptcp(sk))
        mptcp_incoming_options(sk, skb);

    switch (sk->sk_state) {
    case TCP_SYN_SENT:
        err = ECONNREFUSED;    // Connection refused
        break;
    case TCP_CLOSE_WAIT:
        err = EPIPE;            // Broken pipe
        break;
    case TCP_CLOSE:
        return;                 // Already closed, ignore
    default:
        err = ECONNRESET;       // Connection reset
    }
    tcp_done_with_error(sk, err);
}
```

---

## 4. TCP Congestion Control

### 4.1 `struct tcp_congestion_ops` - Congestion Control Interface

**Location:** `/Users/sphinx/github/linux/include/net/tcp.h` (lines 1275-1334)

```c
struct tcp_congestion_ops {
    // A CC must provide either cong_avoid OR cong_control
    
    // (a) "classic" response - calculate new cwnd
    void (*cong_avoid)(struct sock *sk, u32 ack, u32 acked);
    
    // (b) "custom" response - custom congestion control
    void (*cong_control)(struct sock *sk, u32 ack, int flag, 
                         const struct rate_sample *rs);

    // return slow start threshold (required)
    u32 (*ssthresh)(struct sock *sk);

    // call before changing ca_state (optional)
    void (*set_state)(struct sock *sk, u8 new_state);

    // call when cwnd event occurs (optional)
    void (*cwnd_event)(struct sock *sk, enum tcp_ca_event ev);

    // call when ack arrives (optional)
    void (*in_ack_event)(struct sock *sk, u32 flags);

    // hook for packet ack accounting (optional)
    void (*pkts_acked)(struct sock *sk, const struct ack_sample *sample);

    // override sysctl_tcp_min_tso_segs (optional)
    u32 (*min_tso_segs)(struct sock *sk);

    // new value of cwnd after loss (required)
    u32  (*undo_cwnd)(struct sock *sk);

    // returns sndbuf expand multiplier (optional)
    u32 (*sndbuf_expand)(struct sock *sk);

    // get info for inet_diag (optional)
    size_t (*get_info)(struct sock *sk, u32 ext, int *attr,
               union tcp_cc_info *info);

    char            name[TCP_CA_NAME_MAX];
    struct module    *owner;
    struct list_head list;
    u32             key;
    u32             flags;

    // initialize private data (optional)
    void (*init)(struct sock *sk);
    
    // cleanup private data (optional)
    void (*release)(struct sock *sk);
} ____cacheline_aligned_in_smp;
```

### 4.2 Core Congestion Control Functions

**`tcp_slow_start()` - Slow Start Algorithm**

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_cong.c` (lines 456-464)

```c
__bpf_kfunc u32 tcp_slow_start(struct tcp_sock *tp, u32 acked)
{
    u32 cwnd = min(tcp_snd_cwnd(tp) + acked, tp->snd_ssthresh);

    acked -= cwnd - tcp_snd_cwnd(tp);
    tcp_snd_cwnd_set(tp, min(cwnd, tp->snd_cwnd_clamp));

    return acked;
}
```

**Algorithm:**
- Increases cwnd by `acked` packets per ACK (exponential growth)
- Stops at `snd_ssthresh` threshold
- Each ACK during slow start roughly doubles cwnd

**`tcp_cong_avoid_ai()` - Congestion Avoidance**

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_cong.c` (lines 470-479)

```c
__bpf_kfunc void tcp_cong_avoid_ai(struct tcp_sock *tp, u32 w, u32 acked)
{
    if (tp->snd_cwnd_cnt >= w) {
        tp->snd_cwnd_cnt = 0;
        tcp_snd_cwnd_set(tp, tcp_snd_cwnd(tp) + 1);
    }

    tp->snd_cwnd_cnt += acked;
    if (tp->snd_cwnd_cnt >= w) {
        u32 delta = tp->snd_cwnd_cnt / w;
        tcp_snd_cwnd_set(tp, tcp_snd_cwnd(tp) + delta);
        tp->snd_cwnd_cnt -= delta * w;
    }
}
```

**Algorithm:**
- Linear cwnd increase: adds ~1 MSS per RTT
- Accumulates "credits" in `snd_cwnd_cnt`
- When credits reach threshold `w`, increment cwnd by 1

**`tcp_reno_cong_avoid()` - Reno-style Congestion Avoidance**

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_cong.c` (lines 496-511)

```c
__bpf_kfunc void tcp_reno_cong_avoid(struct sock *sk, u32 ack, u32 acked)
{
    struct tcp_sock *tp = tcp_sk(sk);

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

### 4.3 TCP Congestion States

**Location:** `/Users/sphinx/github/linux/include/uapi/linux/tcp.h` (lines 194-227)

```c
enum tcp_ca_state {
    TCP_CA_Open = 0,         // Normal operation, no problems
    TCP_CA_Disorder = 1,      // Received dupACKs or SACKs
    TCP_CA_CWR = 2,            // Congestion window reduced (ECN)
    TCP_CA_Recovery = 3,      // Fast recovery (retransmitting)
    TCP_CA_Loss = 4           // Loss recovery (RTO timeout)
};
```

### 4.4 CUBIC Implementation

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_cubic.c`

Key functions:
- `cubictcp_cong_avoid()` (lines 324-339) - CUBIC congestion avoidance
- `cubictcp_recalc_ssthresh()` (lines 341-352) - Update ssthresh
- `cubictcp_undo_cwnd()` - Undo cwnd after loss

### 4.5 BBR Implementation

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_bbr.c`

BBR (Bottleneck Bandwidth and RTT) is a model-based congestion control that:
- Tracks bottleneck bandwidth (BBR.bw)
- Tracks minimum RTT (BBR.min_rtt)
- Calculates pacing rate and cwnd based on these

---

## 5. TCP Timer Infrastructure

### 5.1 Timer Types

**Location:** `/Users/sphinx/github/linux/include/net/tcp.h`

**Timer Initialization** (line 898 in tcp_timer.c):
```c
inet_csk_init_xmit_timers(sk, &tcp_write_timer, &tcp_delack_timer,
              &tcp_keepalive_timer);
```

**Timer Types:**
1. **Write Timer (Retransmit Timer)** - ICSK_TIME_RETRANS
2. **Delayed ACK Timer** - ICSK_TIME_DACK
3. **Keepalive Timer** - ICSK_TIME_KEEPALIVE
4. **Time Probe Timer** - ICSK_TIME_PROBE0 (zero window probe)
5. **Loss Probe Timer** - ICSK_TIME_LOSS_PROBE
6. **Reordering Timer** - ICSK_TIME_REO_TIMEOUT

### 5.2 `tcp_reset_xmit_timer()` - Timer Setup

**Location:** `/Users/sphinx/github/linux/include/net/tcp.h` (lines 1571-1580)

```c
static inline void tcp_reset_xmit_timer(struct sock *sk,
                    const int what,
                    unsigned long when,
                    bool pace_delay)
{
    if (pace_delay)
        when += tcp_pacing_delay(sk);
    inet_csk_reset_xmit_timer(sk, what, when,
                  tcp_rto_max(sk));
}
```

**Usage:**
- Sets/resets various TCP timers
- `when` is the timeout value
- `pace_delay` adds pacing delay if enabled
- Calls `inet_csk_reset_xmit_timer()` which is in inet_connection_sock.c

### 5.3 Delayed ACK Timer (`tcp_delack_timer`)

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_timer.c` (lines 360-386)

```c
static void tcp_delack_timer(struct timer_list *t)
{
    struct inet_connection_sock *icsk = timer_container_of(icsk, t, 
                                          icsk_delack_timer);
    struct sock *sk = &icsk->icsk_inet.sk;

    if (!(smp_load_acquire(&icsk->icsk_ack.pending) & ICSK_ACK_TIMER) &&
        !READ_ONCE(tcp_sk(sk)->compressed_ack))
        goto out;

    bh_lock_sock(sk);
    if (!sock_owned_by_user(sk)) {
        tcp_delack_timer_handler(sk);
    } else {
        // Defer to tcp_release_cb
        if (!test_and_set_bit(TCP_DELACK_TIMER_DEFERRED, 
                             &sk->sk_tsq_flags))
            sock_hold(sk);
    }
    bh_unlock_sock(sk);
out:
    sock_put(sk);
}
```

**Purpose:** Implements delayed ACK - waits up to `TCP_DELACK_MAX` (typically 40ms) for data to piggyback ACK on.

### 5.4 Retransmit Timer (`tcp_retransmit_timer`)

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_timer.c` (lines 534-727)

```c
void tcp_retransmit_timer(struct sock *sk)
{
    struct tcp_sock *tp = tcp_sk(sk);
    struct inet_connection_sock *icsk = inet_csk(sk);
    struct request_sock *req;
    struct sk_buff *skb;

    req = rcu_dereference_protected(tp->fastopen_rsk, ...);
    if (req) {
        // Fast Open SYN retransmit
        tcp_fastopen_synack_timer(sk, req);
        return;
    }
    
    // ... handle various timer events ...
    switch (icsk->icsk_pending) {
    case ICSK_TIME_REO_TIMEOUT:
        tcp_rack_reo_timeout(sk);  // Reordering timeout
        break;
    case ICSK_TIME_LOSS_PROBE:
        tcp_send_loss_probe(sk);    // Tail loss probe
        break;
    case ICSK_TIME_RETRANS:
        tcp_retransmit_timer(sk);   // RTO retransmission
        break;
    case ICSK_TIME_PROBE0:
        tcp_probe_timer(sk);        // Window probe
        break;
    }
}
```

**RTO Calculation:**
- `icsk_rto` = Retransmission Timeout
- Base RTO from smoothed RTT (`srtt_us >> 3`)
- Backoff on each retransmission: `min(rto * 2^backoff, rto_max)`

### 5.5 Keepalive Timer (`tcp_keepalive_timer`)

**Location:** `/Users/sphinx/github/linux/net/ipv4/tcp_timer.c` (lines 779-850)

```c
static void tcp_keepalive_timer(struct timer_list *t)
{
    struct inet_connection_sock *icsk = timer_container_of(icsk, t,
                                          icsk_keepalive_timer);
    struct sock *sk = &icsk->icsk_inet.sk;
    struct tcp_sock *tp = tcp_sk(sk);
    u32 elapsed;

    bh_lock_sock(sk);
    if (sock_owned_by_user(sk)) {
        tcp_reset_keepalive_timer(sk, HZ/20);
        goto out;
    }

    if (sk->sk_state == TCP_CLOSE)
        goto out;

    // Check keepalive time elapsed
    elapsed = tcp_time_keepalive_expire(tp);
    if (elapsed >= READ_ONCE(tp->keepalive_time)) {
        // Send keepalive probe
        if (tcp_write_probe(sk) <= 0)
            // Reschedule
            tcp_reset_keepalive_timer(sk, ...);
    }
    out:
    bh_unlock_sock(sk);
}
```

**Purpose:** Detects dead connections by sending empty ACK probes after period of inactivity.

---

## 6. UDP Protocol

### 6.1 `struct udphdr` - UDP Header Structure

**Location:** `/Users/sphinx/github/linux/include/uapi/linux/udp.h` (lines 23-28)

```c
struct udphdr {
    __be16  source;         // Source port
    __be16  dest;           // Destination port
    __be16  len;            // UDP length (header + data)
    __sum16 check;          // Checksum (0 if no checksum)
};
```

### 6.2 `struct udp_sock` - UDP Socket Structure

**Location:** `/Users/sphinx/github/linux/include/linux/udp.h` (lines 53-120)

```c
struct udp_sock {
    struct inet_sock inet;   // Must be first member

#define udp_port_hash       inet.sk.__sk_common.skc_u16hashes[0]
#define udp_portaddr_hash   inet.sk.__sk_common.skc_u16hashes[1]
#define udp_portaddr_node   inet.sk.__sk_common.skc_portaddr_node

    unsigned long   udp_flags;

    int             pending;         // Any pending frames?
    __u8            encap_type;      // Encapsulation type

#if !IS_ENABLED(CONFIG_BASE_SMALL)
    __u16           udp_lrpa_hash;   // 4-tuple hash
    struct hlist_nulls_node udp_lrpa_node;
#endif

    __u16           len;             // Total length of pending frames
    __u16           gso_size;        // GSO segment size

    // UDP-Lite specific
    __u16           pcslen;          // Checksum coverage length
    __u16           pcrlen;          // Partial checksum length

    // Encapsulation handlers
    int (*encap_rcv)(struct sock *sk, struct sk_buff *skb);
    void (*encap_err_rcv)(struct sock *sk, struct sk_buff *skb, 
                         int err, __be16 port, u32 info, u8 *payload);
    int (*encap_err_lookup)(struct sock *sk, struct sk_buff *skb);
    void (*encap_destroy)(struct sock *sk);

    // GRO functions
    struct sk_buff *(*gro_receive)(struct sock *sk, struct list_head *head,
                       struct sk_buff *skb);
    int (*gro_complete)(struct sock *sk, struct sk_buff *skb, int nhoff);

    struct udp_prod_queue *udp_prod_queue;
    struct sk_buff_head    reader_queue;  // Fast path recv queue
    int                   forward_deficit;
    int                   forward_threshold;
    bool                  peeking_with_offset;
    struct hlist_node      tunnel_list;
    struct numa_drop_counters drop_counters;
};
```

### 6.3 `udp_sendmsg()` - UDP Send Path

**Location:** `/Users/sphinx/github/linux/net/ipv4/udp.c` (lines 1270-1400)

```c
int udp_sendmsg(struct sock *sk, struct msghdr *msg, size_t len)
{
    // ... variable setup ...
    
    // Check message size
    if (len > 0xFFFF)
        return -EMSGSIZE;

    // Get destination address
    if (msg->msg_name) {
        usin = msg->msg_name;
        daddr = usin->sin_addr.s_addr;
        dport = usin->sin_port;
    }
    
    // Setup flowi4 for routing
    fl4 = &inet->cork.fl.u.ip4;
    rt = ip_route_output(net, daddr, saddr, tos, oif);
    
    // Build UDP header
    skb = ip_make_skb(sk, fl4, getfrag, from, len, 
                       transhdrlen, ipc, &rt, msg->msg_flags);
    
    // Send
    err = ip_send_skb(net, skb);
}
```

### 6.4 `udp_recvmsg()` - UDP Receive Path

**Location:** `/Users/sphinx/github/net/ipv4/udp.c` (lines 2073-2150)

```c
int udp_recvmsg(struct sock *sk, struct msghdr *msg, size_t len, int flags,
        int *addr_len)
{
    struct inet_sock *inet = inet_sk(sk);
    struct sk_buff *skb;
    unsigned int ulen, copied;
    int off, err, peeking = flags & MSG_PEEK;
    bool checksum_valid = false;

    if (flags & MSG_ERRQUEUE)
        return ip_recv_error(sk, msg, len, addr_len);

try_again:
    off = sk_peek_offset(sk, flags);
    skb = __skb_recv_udp(sk, flags, &off, &err);
    if (!skb)
        return err;

    ulen = udp_skb_len(skb);
    copied = len;
    if (copied > ulen - off)
        copied = ulen - off;
    else if (copied < ulen)
        msg->msg_flags |= MSG_TRUNC;

    // Copy data to user
    err = skb_copy_datagram_msg(skb, off, msg, copied);
}
```

---

## 7. Network Header Access

### 7.1 `struct inet_sock` - INET Socket Extension

**Location:** `/Users/sphinx/github/linux/include/net/inet_sock.h` (lines 198-251)

```c
struct inet_sock {
    struct sock     sk;              // Must be first (base sock)
#if IS_ENABLED(CONFIG_IPV6)
    struct ipv6_pinfo *pinet6;
    struct ipv6_fl_socklist __rcu *ipv6_fl_list;
#endif

    // Socket demultiplex comparisons on incoming packets
#define inet_daddr       sk.__sk_common.skc_daddr
#define inet_rcv_saddr   sk.__sk_common.skc_rcv_saddr
#define inet_dport       sk.__sk_common.skc_dport
#define inet_num         sk.__sk_common.skc_num

    unsigned long    inet_flags;
    __be32          inet_saddr;     // Sending source
    __s16           uc_ttl;         // Unicast TTL
    __be16          inet_sport;      // Source port
    struct ip_options_rcu __rcu *inet_opt;  // IP options
    atomic_t        inet_id;         // ID counter for DF packets

    __u8            tos;            // TOS
    __u8            min_ttl;
    __u8            mc_ttl;          // Multicast TTL
    __u8            pmtudisc;       // Path MTU discovery mode
    __u8            rcv_tos;
    __u8            convert_csum;
    int             uc_index;       // Unicast device index
    int             mc_index;       // Multicast device index
    __be32          mc_addr;        // Multicast address
    u32             local_port_range;    // Port range

    struct ip_mc_socklist __rcu *mc_list;
    struct inet_cork_full cork;      // IP corking information
};
```

### 7.2 `inet_sk()` - Access inet_sock from sock

**Location:** `/Users/sphinx/github/linux/include/net/inet_sock.h` (line 362)

```c
#define inet_sk(ptr) container_of_const(ptr, struct inet_sock, sk)
```

**Usage:**
```c
struct sock *sk;        // Generic socket
struct inet_sock *inet; // INET-specific extension

inet = inet_sk(sk);     // Get INET socket from generic
```

### 7.3 Device Header Handling (Ethernet)

**Key Functions:**

1. **`ip_finish_output2()`** (ip_output.c lines 200-247):
```c
static int ip_finish_output2(struct net *net, struct sock *sk, struct sk_buff *skb)
{
    struct dst_entry *dst = skb_dst(skb);
    struct rtable *rt = dst_rtable(dst);
    struct net_device *dev = dst_dev(dst);
    unsigned int hh_len = LL_RESERVED_SPACE(dev);
    struct neighbour *neigh;
    bool is_v6gw = false;

    // Ensure headroom for L2 header
    if (unlikely(skb_headroom(skb) < hh_len && dev->header_ops)) {
        skb = skb_expand_head(skb, hh_len);
        if (!skb)
            return -ENOMEM;
    }

    // Resolve next-hop MAC address
    neigh = ip_neigh_for_gw(rt, skb, &is_v6gw);
    if (!IS_ERR(neigh)) {
        sock_confirm_neigh(skb, neigh);
        res = neigh_output(neigh, skb, is_v6gw);
        rcu_read_unlock();
        return res;
    }
    // ... error handling ...
}
```

2. **`ip_neigh_for_gw()`** (route.h lines 412-428):
```c
static inline struct neighbour *ip_neigh_for_gw(struct rtable *rt,
                        struct sk_buff *skb,
                        bool *is_v6gw)
{
    struct net_device *dev = rt->dst.dev;
    struct neighbour *neigh;

    if (likely(rt->rt_gw_family == AF_INET)) {
        neigh = ip_neigh_gw4(dev, rt->rt_gw4);
    } else if (rt->rt_gw_family == AF_INET6) {
        neigh = ip_neigh_gw6(dev, &rt->rt_gw6);
        *is_v6gw = true;
    } else {
        neigh = ip_neigh_gw4(dev, ip_hdr(skb)->daddr);
    }
    return neigh;
}
```

**Ethernet Header Resolution:**
- Uses ARP (Address Resolution Protocol) for IPv4
- Neighbor table caches MAC addresses
- `neigh_output()` calls device's header_ops to build Ethernet header

---

## Key Call Chains Summary

### TCP Connect Call Chain
```
tcp_v4_connect()
  -> ip_route_connect()
  -> tcp_set_state(TCP_SYN_SENT)
  -> inet_hash_connect()
  -> tcp_connect()
    -> tcp_transmit_skb()
      -> __tcp_transmit_skb()
        -> ip_queue_xmit()
          -> ip_output()
```

### TCP Receive Call Chain (Established)
```
ip_rcv()
  -> ip_rcv_core()
  -> NF_HOOK(PRE_ROUTING)
  -> ip_rcv_finish()
  -> ip_route_input()
  -> tcp_v4_rcv()
    -> tcp_rcv_state_process()
      -> tcp_ack()          // Process ACK
      -> tcp_data_snd_check() // Check send window
```

### TCP Send Call Chain
```
tcp_sendmsg()
  -> tcp_sendmsg_locked()
    -> tcp_write_queue_tail()
    -> tcp_mss()
    -> tcp_push()
      -> tcp_transmit_skb()
        -> __tcp_transmit_skb()
          -> ip_queue_xmit()
            -> ip_output()
```

---

## File Reference Summary

| File | Purpose |
|------|---------|
| `/Users/sphinx/github/linux/net/ipv4/ip_output.c` | IP packet output, fragmentation |
| `/Users/sphinx/github/linux/net/ipv4/ip_input.c` | IP packet input, reassembly |
| `/Users/sphinx/github/linux/net/ipv4/tcp_output.c` | TCP output, transmission, retransmission |
| `/Users/sphinx/github/linux/net/ipv4/tcp_input.c` | TCP input processing, ACK handling |
| `/Users/sphinx/github/linux/net/ipv4/tcp.c` | TCP core, state machine, send/recvmsg |
| `/Users/sphinx/github/linux/net/ipv4/tcp_timer.c` | TCP timers (retransmit, keepalive, delayed ACK) |
| `/Users/sphinx/github/linux/net/ipv4/tcp_cong.c` | Congestion control core (Reno) |
| `/Users/sphinx/github/linux/net/ipv4/tcp_cubic.c` | CUBIC congestion control |
| `/Users/sphinx/github/linux/net/ipv4/udp.c` | UDP protocol implementation |
| `/Users/sphinx/github/linux/include/uapi/linux/ip.h` | IP header struct definition |
| `/Users/sphinx/github/linux/include/uapi/linux/tcp.h` | TCP header struct definition |
| `/Users/sphinx/github/linux/include/uapi/linux/udp.h` | UDP header struct definition |
| `/Users/sphinx/github/linux/include/linux/tcp.h` | tcp_sock, tcp_request_sock definitions |
| `/Users/sphinx/github/linux/include/linux/udp.h` | udp_sock definition |
| `/Users/sphinx/github/linux/include/net/inet_sock.h` | inet_sock definition |
| `/Users/sphinx/github/linux/include/net/tcp.h` | TCP function declarations, timer inline funcs |
| `/Users/sphinx/github/linux/include/net/route.h` | rtable definition |
| `/Users/sphinx/github/linux/include/net/tcp_states.h` | TCP state enum |

This document provides a comprehensive analysis of the Linux kernel TCP/IP protocol stack implementation based on the actual source code.