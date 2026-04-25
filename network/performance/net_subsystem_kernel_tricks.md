
Based on my thorough research of the Linux kernel networking codebase, I will now compile a comprehensive document covering these advanced implementation techniques.

# Linux Kernel Networking "Black Magic" - Advanced Implementation Techniques

## 1. BPF/XDP (Express Data Path)

### BPF Filter Attachment to Sockets (`BPF_CGROUP_RUN_PROG_*`)

BPF programs are attached to sockets via cgroup hooks defined in `/Users/sphinx/github/linux/include/linux/bpf-cgroup.h`:

```c
// Lines 191-201
#define BPF_CGROUP_RUN_PROG_INET_INGRESS(sk, skb)                          \
({                                                                          \
    int __ret = 0;                                                          \
    if (cgroup_bpf_enabled(CGROUP_INET_INGRESS) &&                          \
        cgroup_bpf_sock_enabled(sk, CGROUP_INET_INGRESS) && sk &&            \
        sk_fullsock(sk))                                                     \
        __ret = __cgroup_bpf_run_filter_skb(sk, skb,                        \
                                            CGROUP_INET_INGRESS);           \
    __ret;                                                                  \
})
```

The attachment flow in `/Users/sphinx/github/linux/net/core/filter.c` (lines 134-178):
```c
int sk_filter_trim_cap(struct sock *sk, struct sk_buff *skb,
                       unsigned int cap, enum skb_drop_reason *reason)
{
    int err;
    struct sk_filter *filter;
    
    // Check pfmemalloc reserves
    if (skb_pfmemalloc(skb) && !sock_flag(sk, SOCK_MEMALLOC)) {
        NET_INC_STATS(sock_net(sk), LINUX_MIB_PFMEMALLOCDROP);
        *reason = SKB_DROP_REASON_PFMEMALLOC;
        return -ENOMEM;
    }
    
    // Run cgroup BPF ingress filter
    err = BPF_CGROUP_RUN_PROG_INET_INGRESS(sk, skb);
    if (err) {
        *reason = SKB_DROP_REASON_SOCKET_FILTER;
        return err;
    }
    
    // Run security hook
    err = security_sock_rcv_skb(sk, skb);
    if (err) {
        *reason = SKB_DROP_REASON_SECURITY_HOOK;
        return err;
    }
    
    // Run socket filter
    rcu_read_lock();
    filter = rcu_dereference(sk->sk_filter);
    if (filter) {
        struct sock *save_sk = skb->sk;
        unsigned int pkt_len;
        
        skb->sk = sk;
        pkt_len = bpf_prog_run_save_cb(filter->prog, skb);
        skb->sk = save_sk;
        err = pkt_len ? pskb_trim(skb, max(cap, pkt_len)) : -EPERM;
        if (err)
            *reason = SKB_DROP_REASON_SOCKET_FILTER;
    }
    rcu_read_unlock();
    
    return err;
}
```

### XDP Processing Hooks

XDP actions are defined in `/Users/sphinx/github/linux/include/net/xdp.h` and processed in `/Users/sphinx/github/linux/net/core/xdp.c`:

**XDP Actions:**
- `XDP_REDIRECT` - Redirect packet to another interface or map
- `XDP_PASS` - Pass packet up the kernel stack
- `XDP_DROP` - Drop packet

**xdp_buff structure** (lines 86-107):
```c
struct xdp_buff {
    void *data;
    void *data_end;
    void *data_meta;
    void *data_hard_start;
    struct xdp_rxq_info *rxq;
    struct xdp_txq_info *txq;
    union {
        struct {
            u32 frame_sz;    /* frame size to deduce data_hard_end/tailroom */
            u32 flags;       /* supported values defined in xdp_buff_flags */
        };
#ifdef __LITTLE_ENDIAN
        u64 frame_sz_flags_init;
#endif
    };
};
```

**xdp_frame structure** (lines 294-306):
```c
struct xdp_frame {
    void *data;
    u32 len;
    u32 headroom;
    u32 metasize;
    enum xdp_mem_type mem_type:32;
    struct net_device *dev_rx;
    u32 frame_sz;
    u32 flags;
};
```

### bpf_redirect() Implementation

From `/Users/sphinx/github/linux/net/core/filter.c` (lines 2549-2560):
```c
BPF_CALL_2(bpf_redirect, u32, ifindex, u64, flags)
{
    struct bpf_redirect_info *ri = bpf_net_ctx_get_ri();
    
    if (unlikely(flags & (~(BPF_F_INGRESS) | BPF_F_REDIRECT_INTERNAL)))
        return TC_ACT_SHOT;
    
    ri->flags = flags;
    ri->tgt_index = ifindex;
    
    return TC_ACT_REDIRECT;
}
```

The redirect logic branches to different paths based on device type (lines 2199-2206):
```c
static int __bpf_redirect(struct sk_buff *skb, struct net_device *dev, u32 flags)
{
    if (dev_is_mac_header_xmit(dev))
        return __bpf_redirect_common(skb, dev, flags);
    else
        return __bpf_redirect_no_mac(skb, dev, flags);
}
```

### Building SKB from XDP Buffer

From `/Users/sphinx/github/linux/net/core/xdp.c` (lines 633-673):
```c
struct sk_buff *xdp_build_skb_from_buff(const struct xdp_buff *xdp)
{
    const struct xdp_rxq_info *rxq = xdp->rxq;
    const struct skb_shared_info *sinfo;
    struct sk_buff *skb;
    u32 nr_frags = 0;
    int metalen;
    
    if (unlikely(xdp_buff_has_frags(xdp))) {
        sinfo = xdp_get_shared_info_from_buff(xdp);
        nr_frags = sinfo->nr_frags;
    }
    
    skb = napi_build_skb(xdp->data_hard_start, xdp->frame_sz);
    if (unlikely(!skb))
        return NULL;
    
    skb_reserve(skb, xdp->data - xdp->data_hard_start);
    __skb_put(skb, xdp->data_end - xdp->data);
    
    metalen = xdp->data - xdp->data_meta;
    if (metalen > 0)
        skb_metadata_set(skb, metalen);
    
    if (rxq->mem.type == MEM_TYPE_PAGE_POOL)
        skb_mark_for_recycle(skb);
    
    skb_record_rx_queue(skb, rxq->queue_index);
    
    if (unlikely(nr_frags)) {
        u32 tsize;
        tsize = sinfo->xdp_frags_truesize ? : nr_frags * xdp->frame_sz;
        xdp_update_skb_frags_info(skb, nr_frags, sinfo->xdp_frags_size,
                                  tsize, xdp_buff_get_skb_flags(xdp));
    }
    
    skb->protocol = eth_type_trans(skb, rxq->dev);
    
    return skb;
}
```

---

## 2. Batch I/O

### netif_receive_skb_batch()

From `/Users/sphinx/github/linux/net/core/dev.c` (lines 6213-6271):

The batch receive processes packets through `__netif_receive_skb_list_core()` which groups packets by protocol type for efficient delivery:

```c
static void __netif_receive_skb_list_core(struct list_head *head, bool pfmemalloc)
{
    struct packet_type *pt_curr = NULL;
    struct net_device *od_curr = NULL;
    struct sk_buff *skb, *next;
    LIST_HEAD(sublist);
    
    list_for_each_entry_safe(skb, next, head, list) {
        struct net_device *orig_dev = skb->dev;
        struct packet_type *pt_prev = NULL;
        
        skb_list_del_init(skb);
        __netif_receive_skb_core(&skb, pfmemalloc, &pt_prev);
        if (!pt_prev)
            continue;
        if (pt_curr != pt_prev || od_curr != orig_dev) {
            __netif_receive_skb_list_ptype(&sublist, pt_curr, od_curr);
            INIT_LIST_HEAD(&sublist);
            pt_curr = pt_prev;
            od_curr = orig_dev;
        }
        list_add_tail(&skb->list, &sublist);
    }
    
    __netif_receive_skb_list_ptype(&sublist, pt_curr, od_curr);
}
```

The `netif_receive_skb_list_internal()` function (lines 6385-6416) handles RPS (Receive Packet Steering) and defers timestamps before processing:

```c
void netif_receive_skb_list_internal(struct list_head *head)
{
    struct sk_buff *skb, *next;
    LIST_HEAD(sublist);
    
    list_for_each_entry_safe(skb, next, head, list) {
        net_timestamp_check(...);
        skb_list_del_init(skb);
        if (!skb_defer_rx_timestamp(skb))
            list_add_tail(&skb->list, &sublist);
    }
    list_splice_init(&sublist, head);
    
    rcu_read_lock();
#ifdef CONFIG_RPS
    if (static_branch_unlikely(&rps_needed)) {
        list_for_each_entry_safe(skb, next, head, list) {
            int cpu = get_rps_cpu(skb->dev, skb, &rflow);
            if (cpu >= 0) {
                skb_list_del_init(skb);
                enqueue_to_backlog(skb, cpu, &rflow->last_qtail);
            }
        }
    }
#endif
    __netif_receive_skb_list(head);
    rcu_read_unlock();
}
```

---

## 3. Lock-free Structures

### Lock-free Socket Queues

From `/Users/sphinx/github/linux/net/core/sock.c` (lines 2438-2462), the socket receive queue initialization:

```c
static void sk_init_common(struct sock *sk)
{
    skb_queue_head_init(&sk->sk_receive_queue);
    skb_queue_head_init(&sk->sk_write_queue);
    skb_queue_head_init(&sk->sk_error_queue);
    
    rwlock_init(&sk->sk_callback_lock);
    lockdep_set_class_and_name(&sk->sk_receive_queue.lock,
            af_rlock_keys + sk->sk_family, ...);
    // ...
}
```

The receive queue operations (lines 488-520):
```c
int __sock_queue_rcv_skb(struct sock *sk, struct sk_buff *skb)
{
    unsigned long flags;
    struct sk_buff_head *list = &sk->sk_receive_queue;
    
    if (atomic_read(&sk->sk_rmem_alloc) >= READ_ONCE(sk->sk_rcvbuf)) {
        sk_drops_inc(sk);
        trace_sock_rcvqueue_full(sk, skb);
        return -ENOMEM;
    }
    
    if (!sk_rmem_schedule(sk, skb, skb->truesize)) {
        sk_drops_inc(sk);
        return -ENOBUFS;
    }
    
    skb->dev = NULL;
    skb_set_owner_r(skb, sk);
    skb_dst_force(skb);
    
    spin_lock_irqsave(&list->lock, flags);
    sock_skb_set_dropcount(sk, skb);
    __skb_queue_tail(list, skb);
    spin_unlock_irqrestore(&list->lock, flags);
    
    if (!sock_flag(sk, SOCK_DEAD))
        sk->sk_data_ready(sk);
    return 0;
}
```

### RCU in Conntrack Hash Table

From `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_core.c` (lines 638, 833-835, 2593), conntrack uses `hlist_nulls_add_head_rcu()` for lock-free insertion:

```c
// Inserting to dying list (line 638)
hlist_nulls_add_head_rcu(&ct->tuplehash[IP_CT_DIR_ORIGINAL].hnnode,
                         &cnet->ecache.dying_list);

// Hash table resize rehashing (lines 2591-2593)
bucket = __hash_conntrack(nf_ct_net(ct), &h->tuple, zone_id, hashsize);
hlist_nulls_add_head_rcu(&h->hnnode, &hash[bucket]);
```

The nulls-head RCU API provides:
- `hlist_nulls_add_head_rcu()` - RCU-safe addition to hash list
- `hlist_nulls_del_rcu()` - RCU-safe deletion
- Sequence counter protection for hash table resize

---

## 4. Zero-copy Techniques

### skb_splice_bits()

From `/Users/sphinx/github/linux/net/core/skbuff.c` (lines 3196-3276):

**Core splice function** (lines 3196-3248):
```c
static bool __skb_splice_bits(struct sk_buff *skb, struct pipe_inode_info *pipe,
                              unsigned int *offset, unsigned int *len,
                              struct splice_pipe_desc *spd, struct sock *sk)
{
    struct sk_buff *iter;
    int seg;
    
    // Map the linear part
    if (__splice_segment(virt_to_page(skb->data),
                         (unsigned long) skb->data & (PAGE_SIZE - 1),
                         skb_headlen(skb),
                         offset, len, spd,
                         skb_head_is_locked(skb), sk))
        return true;
    
    // Map the fragments
    if (!skb_frags_readable(skb))
        return false;
    
    for (seg = 0; seg < skb_shinfo(skb)->nr_frags; seg++) {
        const skb_frag_t *f = &skb_shinfo(skb)->frags[seg];
        
        if (WARN_ON_ONCE(!skb_frag_page(f)))
            return false;
        
        if (__splice_segment(skb_frag_page(f),
                             skb_frag_off(f), skb_frag_size(f),
                             offset, len, spd, false, sk))
            return true;
    }
    
    skb_walk_frags(skb, iter) {
        if (*offset >= iter->len) {
            *offset -= iter->len;
            continue;
        }
        if (__skb_splice_bits(iter, pipe, offset, len, spd, sk))
            return true;
    }
    
    return false;
}
```

**Main splice function** (lines 3254-3275):
```c
int skb_splice_bits(struct sk_buff *skb, struct sock *sk, unsigned int offset,
                    struct pipe_inode_info *pipe, unsigned int tlen,
                    unsigned int flags)
{
    struct partial_page partial[MAX_SKB_FRAGS];
    struct page *pages[MAX_SKB_FRAGS];
    struct splice_pipe_desc spd = {
        .pages = pages,
        .partial = partial,
        .nr_pages_max = MAX_SKB_FRAGS,
        .ops = &nosteal_pipe_buf_ops,
        .spd_release = sock_spd_release,
    };
    int ret = 0;
    
    __skb_splice_bits(skb, pipe, &offset, &tlen, &spd, sk);
    
    if (spd.nr_pages)
        ret = splice_to_pipe(pipe, &spd);
    
    return ret;
}
```

The key optimization: when `skb->head_frag` is set, the linear part can be spliced without copying because the page is not shared.

### io_uring Integration

From `/Users/sphinx/github/linux/io_uring/cmd_net.c`, the io_uring socket command interface handles zero-copy operations:

```c
static inline int io_uring_cmd_getsockopt(struct socket *sock,
                                          struct io_uring_cmd *cmd,
                                          unsigned int issue_flags)
{
    const struct io_uring_sqe *sqe = cmd->sqe;
    // ... processes socket options via do_sock_getsockopt()
}

static int io_uring_cmd_timestamp(struct socket *sock,
                                  struct io_uring_cmd *cmd,
                                  unsigned int issue_flags)
{
    struct sock *sk = sock->sk;
    struct sk_buff_head *q = &sk->sk_error_queue;
    // Processes TX timestamps from error queue
}
```

---

## 5. Page Pool

### Page Pool Structure

From `/Users/sphinx/github/linux/include/net/page_pool/types.h` (lines 167-253):

```c
struct page_pool {
    struct page_pool_params_fast p;
    
    int cpuid;
    u32 pages_state_hold_cnt;
    
    bool has_init_callback:1;
    bool dma_map:1;
    bool dma_sync:1;
    bool dma_sync_for_cpu:1;
    
    __cacheline_group_begin_aligned(frag, PAGE_POOL_FRAG_GROUP_ALIGN);
    long frag_users;
    netmem_ref frag_page;
    unsigned int frag_offset;
    __cacheline_group_end_aligned(frag, PAGE_POOL_FRAG_GROUP_ALIGN);
    
    struct delayed_work release_dw;
    void (*disconnect)(void *pool);
    unsigned long defer_start;
    unsigned long defer_warn;
    
    /* Allocation cache - NAPI-protected for lockless operation */
    struct pp_alloc_cache alloc ____cacheline_aligned_in_smp;
    
    /* ptr_ring for remote CPU recycling */
    struct ptr_ring ring;
    
    void *mp_priv;
    const struct memory_provider_ops *mp_ops;
    
    struct xarray dma_mapped;
    atomic_t pages_state_release_cnt;
    refcount_t user_cnt;
    u64 destroy_cnt;
    
    struct page_pool_params_slow slow;
    struct {
        struct hlist_node list;
        ktime_t detach_time;
        u32 id;
    } user;
};
```

### Page Pool Recycling

From `/Users/sphinx/github/linux/net/core/page_pool.c` (lines 780-799):

```c
static bool page_pool_recycle_in_ring(struct page_pool *pool, netmem_ref netmem)
{
    bool in_softirq, ret;
    
    in_softirq = page_pool_producer_lock(pool);
    ret = !__ptr_ring_produce(&pool->ring, (__force void *)netmem);
    if (ret)
        recycle_stat_inc(pool, ring);
    page_pool_producer_unlock(pool, in_softirq);
    
    return ret;
}
```

### XDP Return Path

From `/Users/sphinx/github/linux/net/core/xdp.c` (lines 433-462):

```c
void __xdp_return(netmem_ref netmem, enum xdp_mem_type mem_type,
                  bool napi_direct, struct xdp_buff *xdp)
{
    switch (mem_type) {
    case MEM_TYPE_PAGE_POOL:
        netmem = netmem_compound_head(netmem);
        if (napi_direct && xdp_return_frame_no_direct())
            napi_direct = false;
        page_pool_put_full_netmem(netmem_get_pp(netmem), netmem,
                                  napi_direct);
        break;
    case MEM_TYPE_PAGE_SHARED:
        page_frag_free(__netmem_address(netmem));
        break;
    case MEM_TYPE_PAGE_ORDER0:
        put_page(__netmem_to_page(netmem));
        break;
    case MEM_TYPE_XSK_BUFF_POOL:
        xsk_buff_free(xdp);
        break;
    }
}
```

The bulk return API (lines 509-536) batches page returns to improve cache locality:
```c
void xdp_return_frame_bulk(struct xdp_frame *xdpf, struct xdp_frame_bulk *bq)
{
    if (xdpf->mem_type != MEM_TYPE_PAGE_POOL) {
        xdp_return_frame(xdpf);
        return;
    }
    
    if (bq->count == XDP_BULK_QUEUE_SIZE)
        xdp_flush_frame_bulk(bq);
    
    if (unlikely(xdp_frame_has_frags(xdpf))) {
        struct skb_shared_info *sinfo;
        int i;
        
        sinfo = xdp_get_shared_info_from_frame(xdpf);
        for (i = 0; i < sinfo->nr_frags; i++) {
            skb_frag_t *frag = &sinfo->frags[i];
            bq->q[bq->count++] = skb_frag_netmem(frag);
            if (bq->count == XDP_BULK_QUEUE_SIZE)
                xdp_flush_frame_bulk(bq);
        }
    }
    bq->q[bq->count++] = virt_to_netmem(xdpf->data);
}
```

---

## 6. SKB Cloning Optimization

### Three Cloning Functions Compared

From `/Users/sphinx/github/linux/net/core/skbuff.c`:

**1. skb_clone()** (lines 2098-2125) - Shares data, creates new SKB structure:
```c
struct sk_buff *skb_clone(struct sk_buff *skb, gfp_t gfp_mask)
{
    struct sk_buff_fclones *fclones = container_of(skb,
                                                   struct sk_buff_fclones, skb1);
    struct sk_buff *n;
    
    if (skb_orphan_frags(skb, gfp_mask))
        return NULL;
    
    if (skb->fclone == SKB_FCLONE_ORIG &&
        refcount_read(&fclones->fclone_ref) == 1) {
        // Fast path: use pre-allocated clone
        n = &fclones->skb2;
        refcount_set(&fclones->fclone_ref, 2);
        n->fclone = SKB_FCLONE_CLONE;
    } else {
        // Slow path: allocate new clone
        if (skb_pfmemalloc(skb))
            gfp_mask |= __GFP_MEMALLOC;
        
        n = kmem_cache_alloc(net_hotdata.skbuff_cache, gfp_mask);
        if (!n)
            return NULL;
        
        n->fclone = SKB_FCLONE_UNAVAILABLE;
    }
    
    return __skb_clone(n, skb);
}
```

**2. pskb_copy()** (via `__pskb_copy_fclone()`, lines 2226-2271) - Private head data, shared fragments:
```c
struct sk_buff *__pskb_copy_fclone(struct sk_buff *skb, int headroom,
                                    gfp_t gfp_mask, bool fclone)
{
    unsigned int size = skb_headlen(skb) + headroom;
    int flags = skb_alloc_rx_flag(skb) | (fclone ? SKB_ALLOC_FCLONE : 0);
    struct sk_buff *n = __alloc_skb(size, gfp_mask, flags, NUMA_NO_NODE);
    
    if (!n)
        goto out;
    
    skb_reserve(n, headroom);
    skb_put(n, skb_headlen(skb));
    skb_copy_from_linear_data(skb, n->data, n->len);
    
    n->truesize += skb->data_len;
    n->data_len  = skb->data_len;
    n->len       = skb->len;
    
    // Fragments are shared and refcounted
    if (skb_shinfo(skb)->nr_frags) {
        int i;
        // ... handles orphan frags and copies fragment references
        for (i = 0; i < skb_shinfo(skb)->nr_frags; i++) {
            skb_shinfo(n)->frags[i] = skb_shinfo(skb)->frags[i];
            skb_frag_ref(skb, i);
        }
        skb_shinfo(n)->nr_frags = i;
    }
    
    if (skb_has_frag_list(skb)) {
        skb_shinfo(n)->frag_list = skb_shinfo(skb)->frag_list;
        skb_clone_fraglist(n);
    }
    
    skb_copy_header(n, skb);
out:
    return n;
}
```

**3. skb_copy()** (lines 2178-2207) - Complete private copy of both head and data:
```c
struct sk_buff *skb_copy(const struct sk_buff *skb, gfp_t gfp_mask)
{
    struct sk_buff *n;
    unsigned int size;
    int headerlen;
    
    if (!skb_frags_readable(skb))
        return NULL;
    
    headerlen = skb_headroom(skb);
    size = skb_end_offset(skb) + skb->data_len;
    n = __alloc_skb(size, gfp_mask, skb_alloc_rx_flag(skb), NUMA_NO_NODE);
    if (!n)
        return NULL;
    
    skb_reserve(n, headerlen);
    skb_put(n, skb->len);
    
    BUG_ON(skb_copy_bits(skb, -headerlen, n->head, headerlen + skb->len));
    
    skb_copy_header(n, skb);
    return n;
}
```

### __skb_clone() Internal

From `/Users/sphinx/github/linux/net/core/skbuff.c` (lines 1608-1639):
```c
static struct sk_buff *__skb_clone(struct sk_buff *n, struct sk_buff *skb)
{
#define C(x) n->x = skb->x
    
    n->next = n->prev = NULL;
    n->sk = NULL;
    __copy_skb_header(n, skb);
    
    C(len);
    C(data_len);
    C(mac_len);
    n->hdr_len = skb->nohdr ? skb_headroom(skb) : skb->hdr_len;
    n->cloned = 1;
    n->nohdr = 0;
    n->peeked = 0;
    C(pfmemalloc);
    C(pp_recycle);
    n->destructor = NULL;
    C(tail);
    C(end);
    C(head);
    C(head_frag);
    C(data);
    C(truesize);
    refcount_set(&n->users, 1);
    
    atomic_inc(&(skb_shinfo(skb)->dataref));
    skb->cloned = 1;
    
    return n;
#undef C
}
```

---

## 7. Memory Reclamation

### Forward Allocation and Scheduling

From `/Users/sphinx/github/linux/net/core/sock.c` (lines 3395-3449):

**__sk_mem_schedule()** (lines 3404-3413) - Pre-allocates memory:
```c
int __sk_mem_schedule(struct sock *sk, int size, int kind)
{
    int ret, amt = sk_mem_pages(size);
    
    sk_forward_alloc_add(sk, amt << PAGE_SHIFT);
    ret = __sk_mem_raise_allocated(sk, size, amt, kind);
    if (!ret)
        sk_forward_alloc_add(sk, -(amt << PAGE_SHIFT));
    return ret;
}
```

**__sk_mem_reclaim()** (lines 3443-3448) - Reclaims forward-allocated memory:
```c
void __sk_mem_reclaim(struct sock *sk, int amount)
{
    amount >>= PAGE_SHIFT;
    sk_forward_alloc_add(sk, -(amount << PAGE_SHIFT));
    __sk_mem_reduce_allocated(sk, amount);
}
```

### sk_rmem_schedule()

From `/Users/sphinx/github/linux/net/core/skbuff.c`, memory scheduling integrates with the socket receive queue:

```c
// In __sock_queue_rcv_skb() (line 499):
if (!sk_rmem_schedule(sk, skb, skb->truesize)) {
    sk_drops_inc(sk);
    return -ENOBUFS;
}
```

### Memory Pressure Handling

From `/Users/sphinx/github/linux/net/core/sock.c` (lines 3271-3364), the `__sk_mem_raise_allocated()` function:

```c
int __sk_mem_raise_allocated(struct sock *sk, int size, int amt, int kind)
{
    bool memcg_enabled = false, charged = false;
    struct proto *prot = sk->sk_prot;
    long allocated = 0;
    
    if (!sk->sk_bypass_prot_mem) {
        sk_memory_allocated_add(sk, amt);
        allocated = sk_memory_allocated(sk);
    }
    
    if (mem_cgroup_sk_enabled(sk)) {
        memcg_enabled = true;
        charged = mem_cgroup_sk_charge(sk, amt, gfp_memcg_charge());
        if (!charged)
            goto suppress_allocation;
    }
    
    if (!allocated)
        return 1;
    
    /* Under limit */
    if (allocated <= sk_prot_mem_limits(sk, 0)) {
        sk_leave_memory_pressure(sk);
        return 1;
    }
    
    /* Under pressure */
    if (allocated > sk_prot_mem_limits(sk, 1))
        sk_enter_memory_pressure(sk);
    
    /* Over hard limit */
    if (allocated > sk_prot_mem_limits(sk, 2))
        goto suppress_allocation;
    
    // ... additional heuristics for TCP stream sockets
}
```

### TCP vs UDP Memory Management

**TCP** uses `sk_wmem_queued` for write buffer accounting and implements:
- Stream socket moderation (`sk_stream_moderate_sndbuf`)
- Per-socket send buffer limits

**UDP** uses:
- `refcount_read(&sk->sk_wmem_alloc)` for atomic memory tracking
- No send buffer moderation like TCP

---

## Summary

These Linux kernel networking optimizations represent years of performance engineering:

| Technique | Key Benefit | Primary Files |
|-----------|-------------|---------------|
| BPF/XDP | Kernel bypass for fast packet processing | `filter.c`, `xdp.c` |
| Batch I/O | Reduced per-packet overhead | `dev.c` |
| Lock-free queues | Reduced contention on multi-core | `sock.c`, `nf_conntrack_core.c` |
| Zero-copy splice | No data copies between SKB and pipe | `skbuff.c`, `socket.c` |
| Page pool | DMA-coherent page recycling | `page_pool.c` |
| SKB cloning | Fast vs deep copy tradeoffs | `skbuff.c` |
| Memory reclamation | Proactive memory management | `sock.c` |

Each technique involves careful tradeoffs between code complexity, memory usage, and processing latency.