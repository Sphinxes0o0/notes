# Linux Kernel Packet Routing and Neighbor Subsystem Documentation

## Table of Contents
1. [Routing Table Infrastructure](#1-routing-table-infrastructure)
2. [Destination Entry (dst)](#2-destination-entry-dst)
3. [Neighbour Table](#3-neighbour-table)
4. [ARP Protocol](#4-arp-protocol)
5. [FIB Rules](#5-fib-rules)
6. [Packet Output Path](#6-packet-output-path)
7. [Packet Input Path](#7-packet-input-path)

---

## 1. Routing Table Infrastructure

The Linux kernel IPv4 routing subsystem uses a Forwarding Information Base (FIB) implemented as an LC-trie (Level Compression Trie) data structure for efficient longest-prefix matching.

### Core Files
- `/Users/sphinx/github/linux/net/ipv4/fib_trie.c` - LC-trie implementation
- `/Users/sphinx/github/linux/net/ipv4/fib_frontend.c` - FIB frontend with policy routing
- `/Users/sphinx/github/linux/net/ipv4/route.c` - IPv4 routing table implementation
- `/Users/sphinx/github/linux/include/net/ip_fib.h` - Core FIB structures and declarations
- `/Users/sphinx/github/linux/include/net/route.h` - Route structures and declarations

### Key Data Structures

#### struct key_vector (fib_trie.c:121)
```c
struct key_vector {
    t_key key;
    unsigned char pos;        /* 2log(KEYLENGTH) bits needed */
    unsigned char bits;       /* 2log(KEYLENGTH) bits needed */
    unsigned char slen;
    union {
        /* This list pointer if valid if (pos | bits) == 0 (LEAF) */
        struct hlist_head leaf;
        /* This array is valid if (pos | bits) > 0 (TNODE) */
        DECLARE_FLEX_ARRAY(struct key_vector __rcu *, tnode);
    };
};
```

**Fields explained:**
- `key`: The prefix/trie key value
- `pos`: Starting position of key bits in trie (0 = root)
- `bits`: Number of bits represented by this node
- `slen`: Max key length for leaves in this subtrie
- `leaf`: Valid when (pos | bits) == 0, hlist of fib_alias entries
- `tnode`: Valid when (pos | bits) > 0, array of child pointers

#### struct trie (fib_trie.c:167)
```c
struct trie {
    struct key_vector kv[1];
#ifdef CONFIG_IP_FIB_TRIE_STATS
    struct trie_use_stats __percpu *stats;
#endif
};
```

Root of the LC-trie. `kv[0]` is the root key_vector.

#### struct fib_table (ip_fib.h:257)
```c
struct fib_table {
    struct hlist_node   tb_hlist;
    u32                 tb_id;
    int                 tb_num_default;
    struct rcu_head     rcu;
    unsigned long       *tb_data;
    unsigned long       __data[];
};
```

**Fields:**
- `tb_id`: Table identifier (RT_TABLE_LOCAL=255, RT_TABLE_MAIN=254, RT_TABLE_DEFAULT=253, or custom)
- `tb_num_default`: Number of default routes in table
- `tb_data`: Pointer to trie structure
- `__data[]`: Flexible array holding the actual trie

#### struct fib_result (ip_fib.h:173)
```c
struct fib_result {
    __be32          prefix;
    unsigned char   prefixlen;
    unsigned char   nh_sel;
    unsigned char   type;
    unsigned char   scope;
    u32             tclassid;
    dscp_t          dscp;
    struct fib_nh_common   *nhc;
    struct fib_info        *fi;
    struct fib_table       *table;
    struct hlist_head      *fa_head;
};
```

**Fields:**
- `prefix`: The matched prefix address
- `prefixlen`: Length of matched prefix in bits
- `nh_sel`: Selected next hop index
- `type`: Route type (RTN_UNICAST, RTN_LOCAL, RTN_BROADCAST, etc.)
- `scope`: Route scope (RT_SCOPE_UNIVERSE, RT_SCOPE_LINK, etc.)
- `tclassid`: Traffic class ID for packet classification
- `nhc`: Pointer to next hop common structure
- `fi`: Full fib_info with metrics
- `table`: Pointer to fib_table this result came from

#### struct rtable (route.h:57)
```c
struct rtable {
    struct dst_entry    dst;
    int                 rt_genid;
    unsigned int        rt_flags;
    __u16               rt_type;
    __u8                rt_is_input;
    __u8                rt_uses_gateway;
    int                 rt_iif;
    u8                  rt_gw_family;
    union {
        __be32          rt_gw4;
        struct in6_addr rt_gw6;
    };
    u32                 rt_mtu_locked:1,
                        rt_pmtu:31;
};
```

**Fields:**
- `dst`: Embedded dst_entry (MUST be first)
- `rt_genid`: Generation ID for cache invalidation
- `rt_flags`: Route flags (RTCF_xxx)
- `rt_type`: Route type (RTN_xxx)
- `rt_is_input`: 1 if this is an input route
- `rt_uses_gateway`: 1 if route uses a gateway
- `rt_iif`: Input interface index
- `rt_gw_family`: Address family of gateway
- `rt_gw4`: IPv4 gateway address
- `rt_gw6`: IPv6 gateway address
- `rt_mtu_locked`: 1 if MTU is locked
- `rt_pmtu`: Path MTU value

#### struct fib_nh_common (ip_fib.h:83)
```c
struct fib_nh_common {
    struct net_device   *nhc_dev;
    netdevice_tracker   nhc_dev_tracker;
    int                 nhc_oif;
    unsigned char       nhc_scope;
    u8                  nhc_family;
    u8                  nhc_gw_family;
    unsigned char       nhc_flags;
    struct lwtunnel_state *nhc_lwtstate;
    union {
        __be32          ipv4;
        struct in6_addr ipv6;
    } nhc_gw;
    int                 nhc_weight;
    atomic_t            nhc_upper_bound;
    struct rtable __rcu * __percpu *nhc_pcpu_rth_output;
    struct rtable __rcu     *nhc_rth_input;
    struct fnhe_hash_bucket __rcu *nhc_exceptions;
};
```

**Fields:**
- `nhc_dev`: Output network device
- `nhc_oif`: Output interface index
- `nhc_scope`: Next hop scope
- `nhc_family`: Address family (AF_INET or AF_INET6)
- `nhc_gw_family`: Gateway address family
- `nhc_flags`: Next hop flags (NHF_xxx)
- `nhc_gw`: Gateway address (union for IPv4/IPv6)
- `nhc_weight`: Weight for ECMP routing
- `nhc_upper_bound`: Upper bound for this nexthop
- `nhc_pcpu_rth_output`: Per-CPU cached output routes (for performance)
- `nhc_rth_input`: Cached input route
- `nhc_exceptions`: Hash table for PMTU exceptions

### Key Functions

#### fib_table_lookup (fib_trie.c:1420)
```c
int fib_table_lookup(struct fib_table *tb, const struct flowi4 *flp,
                     struct fib_result *res, int fib_flags)
```

The core lookup function implementing longest-prefix match using the LC-trie:

**Algorithm (3 steps):**
1. **Step 1 - Travel to trie**: Start at root, follow bits to find longest prefix match
2. **Step 2 - Backtrack**: Begin backtracking from leaf to find longest matching prefix
3. **Step 3 - Process leaf**: Find matching fib_alias entries with appropriate scope/type

**Key implementation details:**
- Line 1447: Computes current key from flowi4 (daddr)
- Lines 1460-1490: Traverse trie based on key bits using `tnode_get_child()`
- Lines 1496-1540: Backtrack and collect leaves
- Lines 1546-1600: Find best matching fib_alias based on TOS and priority
- Lines 1606-1630: Check if result should be used (scope validation)

#### fib_lookup (fib_frontend.c:374 - inlined)
```c
static inline int fib_lookup(struct net *net, struct flowi4 *flp,
                             struct fib_result *res, unsigned int flags)
```

High-level lookup that handles policy routing:
- Calls `__fib_lookup` when custom rules exist
- Otherwise directly queries fib_main and fib_default tables

#### __fib_lookup (fib_frontend.c:84)
```c
int __fib_lookup(struct net *net, struct flowi4 *flp,
                 struct fib_result *res, unsigned int flags)
```

**Flow:**
1. Invoked with `l3mdev_update_flow` for L3 master device flow updates
2. Calls `fib_rules_lookup` to traverse policy rules
3. Returns `-ENETUNREACH` on lookup failure (error code translation from `-ESRCH`)

#### ip_route_output_key_hash (route.c:2691)
```c
struct rtable *ip_route_output_key_hash(struct net *net, struct flowi4 *fl4,
                                        const struct sk_buff *skb)
```

**Flow:**
1. Sets `flowi4_iif = LOOPBACK_IFINDEX`
2. Handles `FLOWI_FLAG_ANYSRC` for source address selection
3. Calls `ip_route_output_key_hash_rcu` under RCU lock
4. Returns cached dst_entry via `skb_dst()` or creates new rtable

#### ip_route_input_slow (route.c:2263)
```c
ip_route_input_slow(struct sk_buff *skb, __be32 daddr, __be32 saddr,
                    dscp_t dscp, struct net_device *dev,
                    struct fib_result *res)
```

**Flow:**
1. Validates source and destination addresses
2. Handles martian address detection
3. Calls `fib_lookup` to find matching routes
4. Handles broadcast, multicast, and local delivery cases
5. Sets up dst_entry on skb

**Key validation:**
- Lines 2100-2120: Martian address check (bogons)
- Lines 2125-2145: Multicast routing check
- Lines 2150-2180: Sets up flowi4 for FIB lookup

#### fib_insert_node (fib_trie.c:1104)
Adds new nodes to the trie structure with automatic rebalancing using inflate/halve/collapse operations.

#### trie_rebalance (fib_trie.c:1098)
Maintains LC-trie balance after insertions. Called after `fib_insert_node()`.

---

## 2. Destination Entry (dst)

The destination cache provides protocol-independent caching of routing decisions with reference counting and metrics.

### Core Files
- `/Users/sphinx/github/linux/net/core/dst.c` - Protocol-independent destination cache
- `/Users/sphinx/github/linux/include/net/dst.h` - dst_entry structure and operations

### Key Data Structures

#### struct dst_entry (dst.h:26)
```c
struct dst_entry {
    union {
        struct net_device       *dev;
        struct net_device __rcu *dev_rcu;
    };
    struct dst_ops              *ops;
    unsigned long               _metrics;
    unsigned long               expires;
#ifdef CONFIG_XFRM
    struct xfrm_state           *xfrm;
#else
    void                        *__pad1;
#endif
    int                         (*input)(struct sk_buff *);
    int                         (*output)(struct net *net, struct sock *sk, struct sk_buff *skb);
    unsigned short              flags;
#define DST_NOXFRM       0x0002
#define DST_NOPOLICY     0x0004
#define DST_NOCOUNT      0x0008
#define DST_FAKE_RTABLE  0x0010
#define DST_XFRM_TUNNEL  0x0020
#define DST_XFRM_QUEUE   0x0040
#define DST_METADATA     0x0080
    short                       obsolete;
#define DST_OBSOLETE_NONE       0
#define DST_OBSOLETE_DEAD       2
#define DST_OBSOLETE_FORCE_CHK -1
#define DST_OBSOLETE_KILL      -2
    unsigned short              header_len;
    unsigned short              trailer_len;
    rcuref_t                    __rcuref;
    int                         __use;
    unsigned long               lastuse;
    struct rcu_head             rcu_head;
    short                       error;
    short                       __pad;
    __u32                       tclassid;
    struct lwtunnel_state       *lwtstate;
    netdevice_tracker           dev_tracker;
    struct list_head            rt_uncached;
    struct uncached_list        *rt_uncached_list;
};
```

**Fields explained:**
- `dev`: Network device (old style, direct pointer)
- `dev_rcu`: Network device (new style, RCU protected)
- `ops`: Operations vector for this dst type
- `_metrics`: Cached metrics (RTAX_xxx values packed into unsigned long)
- `expires`: Expiration time (jiffies)
- `xfrm`: IPSec state (if CONFIG_XFRM)
- `input`: Input function pointer (ip_rcv, ip6_rcv, etc.)
- `output`: Output function pointer (ip_output, ip6_output, etc.)
- `flags`: DST_xxx flags
- `obsolete`: Obsolescence state
- `header_len`: Header length (for GSO)
- `trailer_len`: Trailer length
- `__rcuref`: RCU reference count
- `__use`: Use count
- `lastuse`: Last use timestamp
- `error`: Last error code
- `tclassid`: Traffic class ID for classification
- `lwtstate`: Lightweight tunnel state
- `rt_uncached`: Link to uncached list for cleanup

#### struct dst_metrics (dst.h:100)
```c
struct dst_metrics {
    u32         metrics[RTAX_MAX];
    refcount_t  refcnt;
} __aligned(4);
```

Metrics array indexed by RTAX_xxx (RTAX_MTU, RTAX_WINDOW, RTAX_RTT, etc.).

### Key Functions

#### dst_alloc (dst.c:80)
```c
struct dst_entry *dst_alloc(struct dst_ops *ops, struct net_device *dev,
                            int initial_obsolete, unsigned short flags)
```

**Flow:**
1. Allocates dst_entry from kmem_cache (`dst_cache` slab)
2. Triggers garbage collection if `ops->gc` exists and threshold exceeded
3. Initializes dst with `dst_init()`

#### dst_init (dst.c:47)
```c
void dst_init(struct dst_entry *dst, struct dst_ops *ops,
              struct net_device *dev, int initial_obsolete,
              unsigned short flags)
```

**Initialization:**
1. Sets device reference with `netdev_hold()`
2. Sets up default metrics from `dst_default_metrics`
3. Initializes input/output to `dst_discard()`/`dst_discard_out()`
4. Sets initial obsolete state

#### dst_release (dst.c:166)
```c
void dst_release(struct dst_entry *dst)
```

**Flow:**
1. Decrements reference count using `rcuref_put()`
2. Triggers deferred destruction via `call_rcu_hurry()` when refcount reaches zero
3. Handles metadata dst cache cleanup

**Memory ordering:**
- Uses `smp_mb__after_rcu_dereference` before decrement

#### dst_dev_put (dst.c:145)
```c
void dst_dev_put(struct dst_entry *dst)
```

**Flow:**
1. Marks dst as DEAD via `WRITE_ONCE(dst->obsolete, DST_OBSOLETE_DEAD)`
2. Calls `dst->ops->ifdown()` if defined
3. Replaces device with blackhole_netdev

#### dst_output (dst.h:468)
```c
static inline int dst_output(struct net *net, struct sock *sk, struct sk_buff *skb)
```

Indirect call to `ip6_output` or `ip_output` based on dst protocol family.

#### dst_input (dst.h:478)
```c
static inline int dst_input(struct sk_buff *skb)
```

Indirect call to `ip6_input` or `ip_local_deliver` based on dst protocol family.

---

## 3. Neighbour Table

The neighbour subsystem provides L2 address resolution and caching for various address families.

### Core Files
- `/Users/sphinx/github/linux/net/core/neighbour.c` - Generic neighbour cache implementation

### Neighbour States (NUD_*)
```
NUD_NONE         = 0x00  No state information
NUD_INCOMPLETE   = 0x01  Address resolution in progress
NUD_REACHABLE    = 0x02  Valid L2 address, recently verified
NUD_STALE        = 0x04  Valid L2 address but possibly outdated
NUD_DELAY        = 0x08  Waiting for timers before probing
NUD_PROBE        = 0x10  Probing for a valid L2 address
NUD_FAILED       = 0x20  Address resolution failed
NUD_NOARP        = 0x40  No L2 address resolution needed
NUD_PERMANENT    = 0x80  Static entry, never expires
```

### Key Data Structures

#### struct neighbour (include/net/neighbour.h)
```c
struct neighbour {
    struct neighbour __rcu *next;
    struct hlist_node gc_list;
    struct hlist_node hash_bucket;
    struct net_device *dev;
    unsigned char primary_key[];
    // ... more fields
};
```

Key fields (not exhaustive):
- `dev`: Network device
- `primary_key[]`: Protocol address (e.g., IPv4 address)
- `lladdr`: L2 address
- `lladdr_len`: L2 address length
- `type`: NUD_xxx state
- `flags`: NTF_xxx flags
- `output`: Output function (neigh_resolve_output, neigh_direct_output, etc.)
- `constructor`: Constructor function
- `timer`: State machine timer
- `lock`: Spinlock protecting state

#### struct neigh_table (include/net/neighbour.h)
```c
struct neigh_table {
    int family;
    unsigned int key_len;
    unsigned int protocol;
    unsigned int (*hash)(const void *pkey, const struct net_device *dev);
    bool (*key_eq)(const struct neighbour *neigh, const void *pkey);
    int (*constructor)(struct neighbour *neigh);
    int (*pconstructor)(struct neighbour *neigh);
    void (*pdestructor)(struct neighbour *neigh);
    void (*proxy_redo)(struct neighbour *neigh);
    char *id;
    struct neigh_parms parms;
    struct pneigh_entry __rcu **phash_buckets;
    unsigned int hash_rnd;
    struct hw_pci_ops *pci_ops;
    struct list_head managed_list;
    unsigned int min_weak_purge_time;
    unsigned int max_weak_purge_time;
    size_t pkey_len;
    struct callback_head rcu;
    struct neigh_hash_table __rcu *nht;
    struct deferred_split_ops *split;
};
```

### Key Functions

#### neigh_lookup (neighbour.c:625)
```c
struct neighbour *neigh_lookup(struct neigh_table *tbl, const void *pkey,
                              struct net_device *dev)
```

**Flow:**
1. Computes hash: `tbl->hash(pkey, dev)`
2. Looks up in hash bucket
3. For each entry in bucket, checks `tbl->key_eq(neigh, pkey)`
4. Increments reference count if found
5. Returns neighbour or NULL

**Locking:** Called with RCU read lock held (or BH disabled).

#### __neigh_create (neighbour.c:738)
```c
struct neighbour *__neigh_create(struct neigh_table *tbl, const void *pkey,
                                 struct net_device *dev, struct neighbour *n,
                                 bool exempt_from_gc, bool want_ref)
```

**Flow:**
1. Calls `___neigh_create()` for actual allocation
2. Sets initial state to `NUD_NONE`
3. If `want_ref`, caller holds reference
4. Returns new neighbour

#### neigh_resolve_output (neighbour.c:1600)
```c
int neigh_resolve_output(struct neighbour *neigh, struct sk_buff *skb)
```

**Flow:**
1. Acquires neigh->lock
2. Checks state:
   - `NUD_CONNECTED`: calls `neigh->ops->solicit()` to send ARP request
   - `NUD_STALE`: updates to `NUD_DELAY`, starts timer
   - `NUD_DELAY`: waits for timer
   - `NUD_INCOMPLETE`: queues packet in arp_q
3. On success, calls `neigh->ops->output()` to send
4. Returns 0 on success, negative error on failure

#### neigh_update (neighbour.c:1542)
```c
int neigh_update(struct neighbour *neigh, const u8 *lladdr, u8 new,
                 u32 flags, pid_t pid)
```

**Flow:**
1. Takes neigh->lock
2. Updates lladdr if provided
3. Calls `__neigh_update()` to handle state machine transitions
4. Releases lock

#### __neigh_update (neighbour.c:1375)
Internal state machine transition function. Handles:
- Validates state transitions
- Updates reachability time
- Calls notifiers
- Triggers timer for state changes

---

## 4. ARP Protocol

ARP (Address Resolution Protocol) handles IPv4 address-to-L2 address resolution.

### Core Files
- `/Users/sphinx/github/linux/net/ipv4/arp.c` - ARP protocol implementation

### Key Functions

#### arp_solicit (arp.c:334)
```c
static void arp_solicit(struct neighbour *neigh, struct sk_buff *skb)
```

**Flow:**
1. Called when neighbour state is NUD_NONE, NUD_STALE, or NUD_DELAY
2. Allocates ARP request packet
3. Sends via `arp_send()`
4. Updates neigh state to NUD_INCOMPLETE

**Packet construction:**
- Source MAC: device MAC or 0 for probe
- Source IP: `ip_hdr(skb)->saddr` or device IP for gratuitous ARP
- Target IP: neigh->primary_key (target protocol address)

#### arp_rcv (arp.c:968)
```c
static int arp_rcv(struct sk_buff *skb, struct net_device *dev,
                    struct packet_type *pt, struct net_device *orig_dev)
```

**Flow:**
1. Validates ARP packet (length, hardware type, protocol type)
2. Passes to `arp_process()` for handling

**Validation:**
- Checks `dev->flags & IFF_NOARP`
- Validates ARP header length
- Checks hardware type matches device

#### arp_process (arp.c:703)
```c
static int arp_process(struct net *net, struct sock *sk, struct sk_buff *skb)
```

**Flow:**
1. Parses ARP header (ar_op, ar_sha, ar_sip, ar_tip, etc.)
2. Creates/updates neighbour entry via `__neigh_update()`
3. For ARP requests: generates ARP reply via `arp_send()` if not proxy ARP
4. For ARP replies: updates neighbour directly to NUD_REACHABLE
5. Handles proxy ARP:
   - Checks `arp_tbl.proxy_queue` for pending proxies
   - Calls `pneigh_lookup()` for proxy entries

#### arp_tbl (arp.c:153)
Global `struct neigh_table` instance for ARP:

```c
static struct neigh_table arp_tbl = {
    .family = AF_INET,
    .key_len = 4,           /* IPv4 addresses are 4 bytes */
    .protocol = htons(ETH_P_IP),
    .hash = arp_hash,
    .key_eq = __arp_key_eq,
    .constructor = arp_constructor,
    .pconstructor = pneigh_constructor,
    .pdestructor = pneigh_destructor,
    .proxy_redo = parp_redo,
    .id = "arp_cache",
    .parms = {
        .table = NEIGH_ARP_TABLE,
        .reachable_time = 30 * HZ,
        .data = {
            [NEIGH_VAR_MCAST_PROBES] = 3,
            [NEIGH_VAR_MCAST_RETRANS_TIME] = 1000,
            [NEIGH_VAR_UCAST_PROBES] = 3,
            [NEIGH_VAR_RETRANS_TIME] = 1000,
            [NEIGH_VAR_DELAY_PROBE_TIME] = 5 * HZ,
            [NEIGH_VAR_INTERVAL] = 30 * HZ,
            [NEIGH_VAR_GC_STALETIME] = 60 * HZ,
            [NEIGH_VAR_MCAST_REACHABLE_TIME] = 30 * HZ,
            [NEIGH_VAR_APP_PROBES] = 0,
            [NEIGH_VAR_UCAST_SOLICIT] = 0,
            [NEIGH_VAR_MCAST_SOLICIT] = 0,
            [NEIGH_VAR_ANYCAST_DELAY] = HZ / 2,
            [NEIGH_VAR_PROXY_DELAY] = (8 * HZ) / 10,
            [NEIGH_VAR_PROXY_QLEN] = 64,
            [NEIGH_VAR_LOCKTIME] = HZ / 2,
        },
    },
};
```

---

## 5. FIB Rules

FIB rules implement policy routing by allowing routing decisions based on criteria beyond just the destination address.

### Core Files
- `/Users/sphinx/github/linux/net/ipv4/fib_rules.c` - IPv4 FIB rules implementation

### Key Data Structures

#### struct fib4_rule (fib_rules.c:36)
```c
struct fib4_rule {
    struct fib_rule      common;
    u8                   dst_len;
    u8                   src_len;
    dscp_t               dscp;
    dscp_t               dscp_mask;
    u8                   dscp_full:1;     /* DSCP or TOS selector */
    __be32               src;
    __be32               srcmask;
    __be32               dst;
    __be32               dstmask;
#ifdef CONFIG_IP_ROUTE_CLASSID
    u32                  tclassid;
#endif
};
```

**Fields:**
- `common`: Common fib_rule fields (priority, action, table, ifname, etc.)
- `dst_len`: Destination prefix length
- `src_len`: Source prefix length
- `dscp`: DSCP value for matching
- `dscp_mask`: DSCP mask
- `src`: Source address prefix
- `srcmask`: Source address mask (e.g., 0xFFFFFF00 for /24)
- `dst`: Destination address prefix
- `dstmask`: Destination address mask

### Key Functions

#### fib4_rule_action (fib_rules.c:111)
```c
INDIRECT_CALLABLE_SCOPE int fib4_rule_action(struct fib_rule *rule,
                                              struct flowi *flp, int flags,
                                              struct fib_lookup_arg *arg)
```

**Flow:**
1. Executes rule action:
   - `FR_ACT_TO_TBL`: Look up in specified table
   - `FR_ACT_UNREACHABLE`: Return -ENETUNREACH
   - `FR_ACT_PROHIBIT`: Return -EACCES
   - `FR_ACT_BLACKHOLE`: Return -EINVAL
2. For TO_TBL: calls `fib_table_lookup()` with matched table
3. Returns result in `arg->result`

#### fib4_rule_match (fib_rules.c:180)
```c
INDIRECT_CALLABLE_SCOPE int fib4_rule_match(struct fib_rule *rule,
                                             struct flowi *fl, int flags)
```

**Match criteria:**
1. Source address prefix match (if `src_len > 0`)
2. Destination address prefix match (if `dst_len > 0`)
3. DSCP/TOS match (if configured)
4. Protocol match (if configured)
5. Input interface match (if `ifname` set)
6. Output interface match (if `ifname` set)

Returns 1 on match, 0 on no match.

#### fib_rules_lookup (fib_rules.c - registered operation)

High-level rules traversal:
1. Iterates through rules in priority order (lowest first)
2. Calls `fib4_rule_match()` for each rule
3. Executes action via `fib4_rule_action()` on match
4. Returns lookup result in `fib_lookup_arg`

#### fib4_rules_init (fib_rules.c:503)
```c
int __net_init fib4_rules_init(struct net *net)
```

**Default rules registered:**
- `RT_TABLE_LOCAL` (priority 0): Local addresses
- `RT_TABLE_MAIN` (priority 0x7FFE = 32766): Main routing table
- `RT_TABLE_DEFAULT` (priority 0x7FFF = 32767): Default routes

---

## 6. Packet Output Path

### Core Files
- `/Users/sphinx/github/linux/net/ipv4/ip_output.c` - IP packet output handling

### Key Functions

#### ip_output (ip_output.c:428)
```c
int ip_output(struct net *net, struct sock *sk, struct sk_buff *skb)
```

**Flow:**
1. Gets output device via `skb_dst_dev_rcu(skb)`
2. Sets `skb->dev = dev`
3. Sets `skb->protocol = htons(ETH_P_IP)`
4. Calls `NF_HOOK_COND(NFPROTO_IPV4, NF_INET_POST_ROUTING, ...)` for netfilter
5. On NF_HOOK success, calls `ip_finish_output()`
6. On NF_HOOK failure, returns verdict

#### __ip_queue_xmit (ip_output.c:463)
```c
int __ip_queue_xmit(struct sock *sk, struct sk_buff *skb, struct flowi *fl,
                    __u8 tos)
```

**Flow (called by ip_queue_xmit):**
1. Looks up route via `ip_route_output_flow()` (or uses cached dst)
2. Sets IP identification (`ip_select_ident()`)
3. Sets fragment flags if needed
4. Sets TTL via `ip_select_ttl()`
5. Calls `ip_send_skb()` to output

#### ip_finish_output2 (ip_output.c:200)
```c
static int ip_finish_output2(struct net *net, struct sock *sk, struct sk_buff *skb)
```

**Flow:**
1. Gets destination from `skb_dst(skb)`
2. Gets route: `rt = dst_rtable(dst)`
3. Gets gateway: `rt->rt_gw4` or from header
4. Calls `ip_neigh_for_gw()` to resolve neighbour
5. If neighbour is ready, calls `neigh->output()` to send
6. If neighbour is unresolved, calls `neigh->ops->solicit()` to ARP and queues packet

#### ip_finish_output (ip_output.c varies)
Handles final output processing:
- IP options processing
- Checksum computation
- Device MTU checks and fragmentation via `ip_fragment()`

---

## 7. Packet Input Path

### Core Files
- `/Users/sphinx/github/linux/net/ipv4/ip_input.c` - IP packet input handling

### Key Functions

#### ip_rcv (ip_input.c:564)
```c
int ip_rcv(struct sk_buff *skb, struct net_device *dev, struct packet_type *pt,
           struct net_device *orig_dev)
```

**Flow:**
1. Validates IP header (version, length, checksum)
2. Handles IP options
3. Calls `NF_HOOK(NFPROTO_IPV4, NF_INET_PRE_ROUTING, ...)` for netfilter
4. On hook success, calls `ip_rcv_finish()`
5. On hook failure, returns verdict

**Validation:**
- Checks `iph->version == 4`
- Validates header length
- Validates IP checksum
- Checks `ip_fast_csum()`

#### ip_rcv_finish (ip_input.c:439)
```c
static int ip_rcv_finish(struct net *net, struct sock *sk, struct sk_buff *skb)
```

**Flow:**
1. Sets up network header if not set
2. Handles IP options
3. Calls `ip_route_input()` to perform routing lookup
4. Routes to appropriate handler:
   - Local delivery: `ip_local_deliver()`
   - Forwarding: `ip_forward()`

#### ip_local_deliver (ip_input.c:250)
```c
int ip_local_deliver(struct sk_buff *skb)
```

**Flow:**
1. Handles fragmentation via `ip_defrag()`
2. Calls `ip_local_deliver_finish()` to deliver to transport layer

#### ip_local_deliver_finish (ip_input.c varies)

**Protocol demultiplexing:**
- `IPPROTO_ICMP` -> `icmp_rcv()`
- `IPPROTO_TCP` -> `tcp_v4_rcv()`
- `IPPROTO_UDP` -> `udp_rcv()`
- `IPPROTO_IGMP` -> `igmp_rcv()`
- etc.

#### ip_route_input (called from ip_rcv_finish)
Performs routing lookup for incoming packets:
1. Sets up `flowi4` structure with packet parameters
2. Calls `fib_lookup()` or `ip_route_input_slow()`
3. Determines if packet is for local delivery or forwarding
4. Sets dst_entry on skb via `skb_dst_set(skb, dst)`

---

## Summary of Code Locations

| Component | File | Key Function | Line |
|-----------|------|-------------|------|
| LC-trie lookup | fib_trie.c | fib_table_lookup | 1420 |
| Trie structure | fib_trie.c | struct trie | 167 |
| Key vector | fib_trie.c | struct key_vector | 121 |
| FIB frontend | fib_frontend.c | fib_lookup (inline) | 374 |
| __fib_lookup | fib_frontend.c | __fib_lookup | 84 |
| Output route | route.c | ip_route_output_key_hash | 2691 |
| Input route | route.c | ip_route_input_slow | 2263 |
| dst_entry | dst.h | struct dst_entry | 26 |
| dst_alloc | dst.c | dst_alloc | 80 |
| dst_output | dst.h | dst_output (inline) | 468 |
| neigh_lookup | neighbour.c | neigh_lookup | 625 |
| __neigh_create | neighbour.c | __neigh_create | 738 |
| neigh_resolve_output | neighbour.c | neigh_resolve_output | 1600 |
| neigh_update | neighbour.c | neigh_update | 1542 |
| arp_solicit | arp.c | arp_solicit | 334 |
| arp_rcv | arp.c | arp_rcv | 968 |
| arp_process | arp.c | arp_process | 703 |
| arp_tbl | arp.c | arp_tbl | 153 |
| fib4_rule_action | fib_rules.c | fib4_rule_action | 111 |
| fib4_rule_match | fib_rules.c | fib4_rule_match | 180 |
| ip_output | ip_output.c | ip_output | 428 |
| __ip_queue_xmit | ip_output.c | __ip_queue_xmit | 463 |
| ip_finish_output2 | ip_output.c | ip_finish_output2 | 200 |
| ip_rcv | ip_input.c | ip_rcv | 564 |
| ip_rcv_finish | ip_input.c | ip_rcv_finish | 439 |
| ip_local_deliver | ip_input.c | ip_local_deliver | 250 |

---

## Interaction Flow Summary

### Packet Input Flow
```
ip_rcv()
  -> ip_rcv_core()  [validation]
  -> NF_HOOK(PRE_ROUTING)
  -> ip_rcv_finish()
       -> ip_route_input()
            -> fib_lookup() or ip_route_input_slow()
                 |
                       [if local delivery]
                 ip_local_deliver()
                      -> ip_defrag() [if fragmented]
                      -> ip_local_deliver_finish()
                           -> TCP/UDP/ICMP demux
                           
                       [if forwarding]
                 ip_forward()
                      -> ip_finish_output2()
                           -> neigh_resolve_output() [ARP]
                                -> L2 transmit
```

### Packet Output Flow
```
ip_queue_xmit() / tcp_v4_send_syn()
  -> __ip_queue_xmit()
       -> ip_route_output_flow()
       -> ip_select_ident()
       -> ip_send_skb()
  -> ip_output()
       -> NF_HOOK(POST_ROUTING)
       -> ip_finish_output()
            -> ip_finish_output2()
                 -> ip_neigh_for_gw()
                      -> neigh_resolve_output()
                           -> L2 transmit
```

### Route Lookup Flow
```
fib_lookup(net, fl4, res)
     |
     v
[custom rules exist?] 
  YES -> __fib_lookup()
            -> fib_rules_lookup()
                 -> iterate rules by priority
                      -> fib4_rule_match() [match criteria]
                           YES -> fib4_rule_action()
                                    -> fib_table_lookup(table, ...)
                                    -> return result in arg
  NO  -> fib_table_lookup(tb_main, ...)
              -> [miss] -> fib_table_lookup(tb_default, ...)
     |
     v
fib_result populated:
  - prefix, prefixlen
  - type (RTN_UNICAST, RTN_LOCAL, etc.)
  - scope
  - fib_nh_common *nhc
  - fib_info *fi
```

### Neighbour State Machine
```
                  +--> NUD_STALE --+
                  |                |
NUD_NONE ----> NUD_INCOMPLETE --> NUD_REACHABLE <--+
   ^                |                 |            |
   |                |                 v            |
   |                |            NUD_DELAY ---->---+
   |                |                |
   |                v                v
   |            NUD_PROBE ---------+
   |                |
   +----------- NUD_FAILED
```
