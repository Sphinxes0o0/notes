# Linux Kernel BPF Networking Hooks: Comprehensive Analysis

## Table of Contents

1. [AF_XDP](#1-af_xdp)
2. [TC BPF](#2-tc-bpf)
3. [Sockmap](#3-sockmap)
4. [BPF_PROG_TYPE_XDP vs SCHED_CLS](#4-bpf_prog_type_xdp-vs-sched_cls)
5. [BPF Map Iteration](#5-bpf-map-iteration)

---

## 1. AF_XDP

### 1.1 struct xdp_sock

**File:** `include/net/xdp_sock.h`, line 48

`struct sock` **must** be the first member (critical layout requirement):

```c
struct xdp_sock {
    /* struct sock must be the first member of struct xdp_sock */
    struct sock sk;
    struct xsk_queue *rx ____cacheline_aligned_in_smp;
    struct net_device *dev;
    struct xdp_umem *umem;
    struct list_head flush_node;
    struct xsk_buff_pool *pool;
    u16 queue_id;
    bool zc;          // zero-copy mode
    bool sg;          // scatter-gather mode
    enum {
        XSK_READY = 0,
        XSK_BOUND,
        XSK_UNBOUND,
    } state;

    struct xsk_queue *tx ____cacheline_aligned_in_smp;
    struct list_head tx_list;
    u32 tx_budget_spent;

    /* Statistics */
    u64 rx_dropped;
    u64 rx_queue_full;

    /* Partial skb for packet building */
    struct sk_buff *skb;

    struct list_head map_list;
    spinlock_t map_list_lock;
    u32 max_tx_budget;
    struct mutex mutex;
    struct xsk_queue *fq_tmp; /* Fill ring tmp storage before bind */
    struct xsk_queue *cq_tmp; /* Completion ring tmp storage before bind */
};
```

### 1.2 struct xsk_buff_pool

**File:** `include/net/xsk_buff_pool.h`, lines 46-94

```c
struct xsk_buff_pool {
    /* Control path members first */
    struct device *dev;
    struct net_device *netdev;
    struct list_head xsk_tx_list;
    spinlock_t xsk_tx_list_lock;
    refcount_t users;
    struct xdp_umem *umem;
    struct work_struct work;
    spinlock_t rx_lock;
    struct list_head free_list;
    struct list_head xskb_list;
    u32 heads_cnt;
    u16 queue_id;

    /* Data path members as close to free_heads at the end as possible */
    struct xsk_queue *fq ____cacheline_aligned_in_smp;  // Fill queue
    struct xsk_queue *cq;                                // Completion queue
    dma_addr_t *dma_pages;
    struct xdp_buff_xsk *heads;
    struct xdp_desc *tx_descs;
    u64 chunk_mask;
    u64 addrs_cnt;
    u32 free_list_cnt;
    u32 dma_pages_cnt;
    u32 free_heads_cnt;
    u32 headroom;
    u32 chunk_size;
    u32 chunk_shift;
    u32 frame_len;
    u32 xdp_zc_max_segs;
    u8 tx_metadata_len;
    u8 cached_need_wakeup;
    bool uses_need_wakeup;
    bool unaligned;
    bool tx_sw_csum;
    void *addrs;
    spinlock_t cq_prod_lock;
    struct xdp_buff_xsk *free_heads[];
};
```

### 1.3 struct xdp_buff_xsk

**File:** `include/net/xsk_buff_pool.h`, lines 25-32

```c
struct xdp_buff_xsk {
    struct xdp_buff xdp;
    u8 cb[XSK_PRIV_MAX];
    dma_addr_t dma;
    dma_addr_t frame_dma;
    struct xsk_buff_pool *pool;
    struct list_head list_node;
} __aligned_largest;
```

### 1.4 xsk_sendmsg() Path

**File:** `net/xdp/xsk.c`

**xsk_sendmsg()** (lines 1062-1071):
```c
static int xsk_sendmsg(struct socket *sock, struct msghdr *m, size_t total_len)
{
    int ret;
    rcu_read_lock();
    ret = __xsk_sendmsg(sock, m, total_len);
    rcu_read_unlock();
    return ret;
}
```

**__xsk_sendmsg()** (lines 1031-1060):
```c
static int __xsk_sendmsg(struct socket *sock, struct msghdr *m, size_t total_len)
{
    bool need_wait = !(m->msg_flags & MSG_DONTWAIT);
    struct sock *sk = sock->sk;
    struct xdp_sock *xs = xdp_sk(sk);
    struct xsk_buff_pool *pool;
    int err;

    err = xsk_check_common(xs);
    if (err)
        return err;
    if (unlikely(need_wait))
        return -EOPNOTSUPP;
    if (unlikely(!xs->tx))
        return -ENOBUFS;

    if (sk_can_busy_loop(sk))
        sk_busy_loop(sk, 1);

    if (xs->zc && xsk_no_wakeup(sk))
        return 0;

    pool = xs->pool;
    if (pool->cached_need_wakeup & XDP_WAKEUP_TX) {
        if (xs->zc)
            return xsk_wakeup(xs, XDP_WAKEUP_TX);
        return xsk_generic_xmit(sk);  // Copy mode path
    }
    return 0;
}
```

**__xsk_generic_xmit()** (lines 908-995) - the copy-mode Tx path:
- Iterates through TX descriptors via `xskq_cons_peek_desc()`
- Builds SKBs via `xsk_build_skb()` (line 946)
- Handles backpressure via completion queue reservation (line 940)
- Returns `NETDEV_TX_BUSY` on congestion (line 963)

### 1.5 xsk_recvmsg() Path

**xsk_recvmsg()** (lines 1099-1108):
```c
static int xsk_recvmsg(struct socket *sock, struct msghdr *m, size_t len, int flags)
{
    int ret;
    rcu_read_lock();
    ret = __xsk_recvmsg(sock, m, len, flags);
    rcu_read_unlock();
    return ret;
}
```

**__xsk_recvmsg()** (lines 1073-1097) - primarily triggers wakeup for Rx processing:
```c
static int __xsk_recvmsg(struct socket *sock, struct msghdr *m, size_t len, int flags)
{
    // ... validation ...
    if (xsk_no_wakeup(sk))
        return 0;
    if (xs->pool->cached_need_wakeup & XDP_WAKEUP_RX && xs->zc)
        return xsk_wakeup(xs, XDP_WAKEUP_RX);  // Trigger NAPI poll
    return 0;
}
```

### 1.6 xdp_umem_reg Validation

**File:** `net/xdp/xdp_umem.c`, lines 158-247

```c
static int xdp_umem_reg(struct xdp_umem *umem, struct xdp_umem_reg *mr)
{
    bool unaligned_chunks = mr->flags & XDP_UMEM_UNALIGNED_CHUNK_FLAG;
    u32 chunk_size = mr->chunk_size, headroom = mr->headroom;
    // ...

    // Chunk size constraints (line 167)
    if (chunk_size < XDP_UMEM_MIN_CHUNK_SIZE || chunk_size > PAGE_SIZE)
        return -EINVAL;

    // Alignment constraints (line 180)
    if (!unaligned_chunks && !is_power_of_2(chunk_size))
        return -EINVAL;

    // Headroom validation (line 206)
    if (headroom > chunk_size - XDP_PACKET_HEADROOM -
                   SKB_DATA_ALIGN(sizeof(struct skb_shared_info)) - 128)
        return -EINVAL;

    // tx_metadata_len validation (line 211)
    if (mr->tx_metadata_len >= 256 || mr->tx_metadata_len % 8)
        return -EINVAL;
}
```

### 1.7 struct xdp_umem

**File:** `include/net/xdp_sock.h`, lines 23-39

```c
struct xdp_umem {
    void *addrs;
    u64 size;
    u32 headroom;
    u32 chunk_size;
    u32 chunks;
    u32 npgs;
    struct user_struct *user;
    refcount_t users;
    u8 flags;
    u8 tx_metadata_len;
    bool zc;
    struct page **pgs;
    int id;
    struct list_head xsk_dma_list;
    struct work_struct work;
};
```

### 1.8 Zero-Copy vs Copy Mode Implementation

**Zero-copy receive path** (`__xsk_rcv_zc`, lines 146-161):
```c
static int __xsk_rcv_zc(struct xdp_sock *xs, struct xdp_buff_xsk *xskb, u32 len, u32 flags)
{
    u64 addr;
    int err;
    addr = xp_get_handle(xskb, xskb->pool);  // Get buffer address
    err = xskq_prod_reserve_desc(xs->rx, addr, len, flags);  // Enqueue to RX ring
    if (err) {
        xs->rx_queue_full++;
        return err;
    }
    xp_release(xskb);  // Release buffer back to pool
    return 0;
}
```

**Copy mode receive path** (`__xsk_rcv()`, lines 240-306):
- Allocates new `xdp_buff` from pool via `xsk_buff_alloc()` (line 256)
- Copies data via `memcpy()` (line 261)
- Uses `__xsk_rcv_zc()` to enqueue

**Zero-copy transmit** (`xsk_build_skb_zerocopy()`, lines 720-800):
- Reuses the UMEM buffer directly, no copy
- Maps UMEM pages into SKB via `skb_fill_page_desc()` (line 786)
- Sets `xsk_destruct_skb` as destructor (line 653)

### 1.9 Fill Ring and Completion Ring Setup

**Fill Ring (fq)**: Supplies buffers to the driver for Rx
- Created via `XDP_UMEM_FILL_RING` setsockopt (line 1553)
- Stored in `xs->fq_tmp` before bind, moved to `pool->fq` at bind time (line 1434)

**Completion Ring (cq)**: Signals buffer completion after Tx
- Created via `XDP_UMEM_COMPLETION_RING` setsockopt (line 1554)
- Stored in `xs->cq_tmp` before bind, moved to `pool->cq` at bind time (line 1435)

### 1.10 Need Wakeup Mechanism

**File:** `net/xdp/xsk.c`, lines 46-98

```c
void xsk_set_rx_need_wakeup(struct xsk_buff_pool *pool)
{
    if (pool->cached_need_wakeup & XDP_WAKEUP_RX)
        return;
    pool->fq->ring->flags |= XDP_RING_NEED_WAKEUP;  // Set flag
    pool->cached_need_wakeup |= XDP_WAKEUP_RX;
}

void xsk_set_tx_need_wakeup(struct xsk_buff_pool *pool)
{
    // Sets flag on ALL sockets sharing the pool
    list_for_each_entry_rcu(xs, &pool->xsk_tx_list, tx_list) {
        xs->tx->ring->flags |= XDP_RING_NEED_WAKEUP;
    }
    pool->cached_need_wakeup |= XDP_WAKEUP_TX;
}
```

---

## 2. TC BPF

### 2.1 struct cls_bpf_prog

**File:** `net/sched/cls_bpf.c`, lines 38-52

```c
struct cls_bpf_prog {
    struct bpf_prog *filter;
    struct list_head link;
    struct tcf_result res;
    bool exts_integrated;      // Direct-action mode flag
    u32 gen_flags;
    unsigned int in_hw_count;
    struct tcf_exts exts;
    u32 handle;
    u16 bpf_num_ops;
    struct sock_filter *bpf_ops;  // Classic BPF ops
    const char *bpf_name;
    struct tcf_proto *tp;
    struct rcu_work rwork;
};
```

### 2.2 cls_bpf_classify() - Packet Classification

**File:** `net/sched/cls_bpf.c`, lines 81-136

```c
TC_INDIRECT_SCOPE int cls_bpf_classify(struct sk_buff *skb,
                                       const struct tcf_proto *tp,
                                       struct tcf_result *res)
{
    struct cls_bpf_head *head = rcu_dereference_bh(tp->root);
    bool at_ingress = skb_at_tc_ingress(skb);
    struct cls_bpf_prog *prog;
    int ret = -1;

    list_for_each_entry_rcu(prog, &head->plist, link) {
        int filter_res;

        qdisc_skb_cb(skb)->tc_classid = prog->res.classid;

        if (tc_skip_sw(prog->gen_flags)) {
            filter_res = prog->exts_integrated ? TC_ACT_UNSPEC : 0;
        } else if (at_ingress) {
            /* Push L2 header before BPF execution */
            __skb_push(skb, skb->mac_len);
            filter_res = bpf_prog_run_data_pointers(prog->filter, skb);
            __skb_pull(skb, skb->mac_len);  // Restore
        } else {
            filter_res = bpf_prog_run_data_pointers(prog->filter, skb);
        }

        if (prog->exts_integrated) {
            // DIRECT-ACTION MODE: BPF return code is final action
            res->class = 0;
            res->classid = TC_H_MAJ(prog->res.classid) |
                          qdisc_skb_cb(skb)->tc_classid;
            ret = cls_bpf_exec_opcode(filter_res);
            if (ret == TC_ACT_UNSPEC)
                continue;  // Try next classifier
            break;
        }

        if (filter_res == 0)
            continue;  // No match, try next
        if (filter_res != -1) {
            res->class = 0;
            res->classid = filter_res;  // Use filter result as classid
        } else {
            *res = prog->res;  // Use programmed result
        }

        ret = tcf_exts_exec(skb, &prog->exts, res);  // Execute actions
        if (ret < 0)
            continue;
        break;
    }
    return ret;
}
```

### 2.3 Direct-Action Mode

**File:** `net/sched/cls_bpf.c`, lines 473-478

When `TCA_BPF_FLAG_ACT_DIRECT` is set, `exts_integrated` is true:

```c
if (bpf_flags & TCA_BPF_FLAG_ACT_DIRECT)
    have_exts = bpf_flags & TCA_BPF_FLAG_ACT_DIRECT;
```

When `exts_integrated` is true, the BPF program return code is treated as the final TC action directly, skipping action extension execution (lines 108-116).

### 2.4 TCA_BPF_FLAG_ACT_DIRECT

Direct-action mode means the BPF program's return code is used directly as the TC action, bypassing the traditional classifier→action chain.

---

## 3. Sockmap

### 3.1 struct bpf_stab

**File:** `net/core/sock_map.c`, lines 17-22

```c
struct bpf_stab {
    struct bpf_map map;
    struct sock **sks;            // Array of socket pointers
    struct sk_psock_progs progs;   // Attached BPF programs
    spinlock_t lock;               // Synchronizes map updates
};
```

### 3.2 sock_map_redirect()

**bpf_sk_redirect_map()** (filter.c lines 645-661):
```c
BPF_CALL_4(bpf_sk_redirect_map, struct sk_buff *, skb,
           struct bpf_map *, map, u32, key, u64, flags)
{
    struct sock *sk;

    if (unlikely(flags & ~(BPF_F_INGRESS)))
        return SK_DROP;

    sk = __sock_map_lookup_elem(map, key);  // Lookup socket in map
    if (unlikely(!sk || !sock_map_redirect_allowed(sk)))
        return SK_DROP;
    if ((flags & BPF_F_INGRESS) && sk_is_vsock(sk))
        return SK_DROP;

    skb_bpf_set_redir(skb, sk, flags & BPF_F_INGRESS);  // Set redirect target
    return SK_PASS;
}
```

### 3.3 sk_msg_redirect()

**bpf_msg_redirect_map()** (sock_map.c lines 673-692):
```c
BPF_CALL_4(bpf_msg_redirect_map, struct sk_msg *, msg,
           struct bpf_map *, map, u32, key, u64, flags)
{
    struct sock *sk;

    if (unlikely(flags & ~(BPF_F_INGRESS)))
        return SK_DROP;

    sk = __sock_map_lookup_elem(map, key);
    if (unlikely(!sk || !sock_map_redirect_allowed(sk)))
        return SK_DROP;
    if (!(flags & BPF_F_INGRESS) && !sk_is_tcp(sk))
        return SK_DROP;  // MSG_PEEK handling for TCP
    if (sk_is_vsock(sk))
        return SK_DROP;

    msg->flags = flags;
    msg->sk_redir = sk;  // Store redirect target in msg
    return SK_PASS;
}
```

### 3.4 sock_map_redirect_allowed()

**File:** `net/core/sock_map.c`, lines 528-534

```c
static bool sock_map_redirect_allowed(const struct sock *sk)
{
    if (sk_is_tcp(sk))
        return sk->sk_state != TCP_LISTEN;  // TCP: must be connected
    else
        return sk->sk_state == TCP_ESTABLISHED;  // UDP: must be established
}
```

### 3.5 struct sk_psock

**File:** `include/linux/skmsg.h`, lines 83-124

```c
struct sk_psock {
    struct sock *sk;
    struct sock *sk_redir;
    u32 apply_bytes;
    u32 cork_bytes;
    u32 eval;
    bool redir_ingress;
    struct sk_msg *cork;
    struct sk_psock_progs progs;
#if IS_ENABLED(CONFIG_BPF_STREAM_PARSER)
    struct strparser strp;
    u32 copied_seq;
    u32 ingress_bytes;
#endif
    struct sk_buff_head ingress_skb;   // SKB-based ingress queue
    struct list_head ingress_msg;      // MSG-based ingress queue
    spinlock_t ingress_lock;
    u32 msg_tot_len;
    unsigned long state;
    struct list_head link;
    spinlock_t link_lock;
    refcount_t refcnt;
    void (*saved_unhash)(struct sock *sk);
    void (*saved_destroy)(struct sock *sk);
    void (*saved_close)(struct sock *sk, long timeout);
    void (*saved_write_space)(struct sock *sk);
    void (*saved_data_ready)(struct sock *sk);
    int (*psock_update_sk_prot)(struct sock *sk, struct sk_psock *psock, bool restore);
    struct proto *sk_proto;
    // ...
};
```

---

## 4. BPF_PROG_TYPE_XDP vs SCHED_CLS

### 4.1 xdp_do_redirect()

**File:** `net/core/filter.c`, lines 4509-4521

```c
int xdp_do_redirect(struct net_device *dev, struct xdp_buff *xdp,
                    const struct bpf_prog *xdp_prog)
{
    struct bpf_redirect_info *ri = bpf_net_ctx_get_ri();
    enum bpf_map_type map_type = ri->map_type;

    if (map_type == BPF_MAP_TYPE_XSKMAP)
        return __xdp_do_redirect_xsk(ri, dev, xdp, xdp_prog);

    return __xdp_do_redirect_frame(ri, dev, xdp_convert_buff_to_frame(xdp),
                                   xdp_prog);
}
```

### 4.2 xdp_buff vs sk_buff

| Aspect | xdp_buff | sk_buff |
|--------|----------|---------|
| Memory | DMA-mapped, zero-copy capable | Complex L2-L4 header tracking |
| Pointers | `data`, `data_end`, `data_meta` | `mac_len`, `network_header`, `transport_header` |
| Context | Early in Rx path | Throughout entire stack |
| Refcount | Simple | Complex with destructor chain |

### 4.3 XDP Metadata Kfuncs

**File:** `net/core/xdp.c`, lines 903-962

- `bpf_xdp_metadata_rx_timestamp()` - returns `-EOPNOTSUPP` by default
- `bpf_xdp_metadata_rx_hash()` - returns `-EOPNOTSUPP` by default
- `bpf_xdp_metadata_rx_vlan_tag()` - returns `-EOPNOTSUPP` by default

Drivers implement these to expose hardware metadata.

---

## 5. BPF Map Iteration

### 5.1 sock_map_get_next_key()

**File:** `net/core/sock_map.c`, lines 455-468

```c
static int sock_map_get_next_key(struct bpf_map *map, void *key, void *next)
{
    struct bpf_stab *stab = container_of(map, struct bpf_stab, map);
    u32 i = key ? *(u32 *)key : U32_MAX;
    u32 *key_next = next;

    if (i == stab->map.max_entries - 1)
        return -ENOENT;
    if (i >= stab->map.max_entries)
        *key_next = 0;
    else
        *key_next = i + 1;
    return 0;
}
```

### 5.2 sock_hash_get_next_key()

**File:** `net/core/sock_map.c`, lines 1056-1094

Hash-based iteration: finds next bucket if key is NULL, then follows hash chain via `hlist_entry_safe()`.

---

## Summary

| Structure | Location | Purpose |
|-----------|----------|---------|
| `struct xdp_sock` | include/net/xdp_sock.h:48 | AF_XDP socket in kernel |
| `struct xsk_buff_pool` | include/net/xsk_buff_pool.h:46 | XSK buffer management |
| `struct xdp_buff_xsk` | include/net/xsk_buff_pool.h:25 | XSK-specific xdp_buff extension |
| `struct xsk_queue` | net/xdp/xsk_queue.h:40 | Ring buffer (RX/TX/Fill/Completion) |
| `struct xdp_umem` | include/net/xdp_sock.h:23 | UMEM region for XSK |
| `struct cls_bpf_prog` | net/sched/cls_bpf.c:38 | TC cls_bpf classifier instance |
| `struct bpf_stab` | net/core/sock_map.c:17 | SOCKMAP (array-based) |
| `struct bpf_shtab` | net/core/sock_map.c:858 | SOCKHASH (hash-based) |
| `struct sk_psock` | include/linux/skmsg.h:83 | Socket BPF state wrapper |
| `struct sk_msg` | include/linux/skmsg.h:43 | MSG-based socket data |
