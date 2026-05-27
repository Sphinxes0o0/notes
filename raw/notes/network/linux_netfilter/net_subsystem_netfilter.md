# Linux Kernel Netfilter Subsystem Analysis

## Table of Contents
1. [Core Hook Infrastructure](#1-core-hook-infrastructure)
2. [iptables/xtables](#2-iptablesxtables)
3. [nf_tables](#3-nf_tables)
4. [Conntrack Integration](#4-conntrack-integration)
5. [Specific Match/Target Modules](#5-specific-matchtarget-modules)
6. [Key Data Structures](#6-key-data-structures)

---

## 1. Core Hook Infrastructure

### Location: `/Users/sphinx/github/linux/net/netfilter/core.c`

#### nf_hook_state Structure (line 78 in `/Users/sphinx/github/linux/include/linux/netfilter.h`)
```c
struct nf_hook_state {
    u8 hook;              // Hook number (e.g., NF_INET_PRE_ROUTING)
    u8 pf;                // Protocol family (e.g., NFPROTO_IPV4)
    struct net_device *in;    // Input device
    struct net_device *out;   // Output device
    struct sock *sk;          // Socket (if any)
    struct net *net;          // Network namespace
    int (*okfn)(struct net *, struct sock *, struct sk_buff *);  // Continue function
};
```

#### nf_hook_ops Structure (line 98 in `/Users/sphinx/github/linux/include/linux/netfilter.h`)
```c
struct nf_hook_ops {
    struct list_head list;     // List entry for registration
    struct rcu_head rcu;      // RCU for safe deletion
    
    /* User fills in from here down. */
    nf_hookfn *hook;          // Hook function callback
    struct net_device *dev;   // Device for NETDEV hooks
    void *priv;               // Private data passed to hook
    u8 pf;                    // Protocol family
    enum nf_hook_ops_type hook_ops_type:8;  // Hook type (NF_HOOK_OP_*)
    unsigned int hooknum;      // Hook number (NF_INET_*)
    int priority;             // Hook priority (lower = earlier)
};
```

#### nf_hook_entries Structure (line 123 in `/Users/sphinx/github/linux/include/linux/netfilter.h`)
```c
struct nf_hook_entries {
    u16 num_hook_entries;      // Number of registered hooks
    struct nf_hook_entry hooks[];  // Array of hook entries
    
    /* trailer: pointers to original orig_ops of each hook,
     * followed by rcu_head and scratch space used for freeing */
};
```

#### nf_hook_entry Structure (line 113 in `/Users/sphinx/github/linux/include/linux/netfilter.h`)
```c
struct nf_hook_entry {
    nf_hookfn *hook;           // Hook function pointer
    void *priv;               // Private data for the hook
};
```

### Hook Registration Functions

#### nf_register_net_hook() - Line 554 in `/Users/sphinx/github/linux/net/netfilter/core.c`
```c
int nf_register_net_hook(struct net *net, const struct nf_hook_ops *reg)
```
- **Purpose**: Register a single netfilter hook
- **Parameters**:
  - `net`: Network namespace
  - `reg`: Hook operations structure
- **Behavior**:
  1. For `NFPROTO_INET` family, hooks are registered for both IPv4 and IPv6 (unless `NF_INET_INGRESS`)
  2. Calls `__nf_register_net_hook()` to perform actual registration
  3. On failure, rolls back IPv6 registration if IPv4 succeeded
- **Returns**: 0 on success, negative errno on failure

#### nf_unregister_net_hook() - Line 526 in `/Users/sphinx/github/linux/net/netfilter/core.c`
```c
void nf_unregister_net_hook(struct net *net, const struct nf_hook_ops *reg)
```
- **Purpose**: Unregister a netfilter hook
- **Behavior**:
  1. Handles `NFPROTO_INET` by unregistering from both protocol families
  2. Calls `__nf_unregister_net_hook()` for actual removal

#### __nf_register_net_hook() - Line 393 in `/Users/sphinx/github/linux/net/netfilter/core.c`
```c
static int __nf_register_net_hook(struct net *net, int pf,
                                  const struct nf_hook_ops *reg)
```
- **Purpose**: Internal function to register a hook for a specific protocol family
- **Behavior**:
  1. Validates hook parameters based on protocol family
  2. Gets pointer to hook head via `nf_hook_entry_head()`
  3. Acquires `nf_hook_mutex`
  4. Grows hook entries array via `nf_hook_entries_grow()`
  5. Validates and assigns new hook entries
  6. Updates static keys for jump label optimization
  7. Frees old entries after RCU grace period

#### __nf_unregister_net_hook() - Line 485 in `/Users/sphinx/github/linux/net/netfilter/core.c`
```c
static void __nf_unregister_net_hook(struct net *net, int pf,
                                    const struct nf_hook_ops *reg)
```
- **Purpose**: Internal function to unregister a hook
- **Behavior**:
  1. Locates hook entry via `nf_hook_entry_head()`
  2. Removes hook or replaces with dummy (accept_all) to maintain ordering
  3. Shrinks hook array if possible via `__nf_hook_entries_try_shrink()`
  4. Triggers `nf_queue_nf_hook_drop()` for queue cleanup

### Hook Entry Growth/Sizing

#### nf_hook_entries_grow() - Line 100 in `/Users/sphinx/github/linux/net/netfilter/core.c`
```c
static struct nf_hook_entries *
nf_hook_entries_grow(const struct nf_hook_entries *old,
                     const struct nf_hook_ops *reg)
```
- **Purpose**: Add a new hook to the hook entries array
- **Behavior**:
  1. Counts existing non-dummy hooks
  2. Checks BPF hook type priority constraints (line 128-130)
  3. Allocates new array with size = old + 1
  4. Inserts new hook maintaining priority order (ascending)
  5. BPF hooks at same priority as existing BPF hook are rejected
- **Returns**: New hook entries or ERR_PTR on failure

#### __nf_hook_entries_try_shrink() - Line 231 in `/Users/sphinx/github/linux/net/netfilter/core.c`
```c
static void *__nf_hook_entries_try_shrink(struct nf_hook_entries *old,
                                          struct nf_hook_entries __rcu **pp)
```
- **Purpose**: Shrink hook array after unregistration
- **Behavior**:
  1. Counts dummy hooks (removed but placeholder)
  2. If all removed, returns NULL to clear entirely
  3. Otherwise allocates smaller array and copies live hooks
  4. Returns old entries to be freed after RCU grace period

### Hook Traversal

#### nf_hook_slow() - Line 616 in `/Users/sphinx/github/linux/net/netfilter/core.c`
```c
int nf_hook_slow(struct sk_buff *skb, struct nf_hook_state *state,
                 const struct nf_hook_entries *e, unsigned int s)
```
- **Purpose**: Slow path hook invocation - iterates through all hooks
- **Parameters**:
  - `skb`: Packet buffer
  - `state`: Hook execution state
  - `e`: Hook entries array
  - `s`: Starting index
- **Behavior**:
  1. Iterates from index `s` to `e->num_hook_entries`
  2. Calls each hook via `nf_hook_entry_hookfn()`
  3. Processes verdict:
     - `NF_ACCEPT`: Continue to next hook
     - `NF_DROP`: Free skb, return error
     - `NF_QUEUE`: Queue to userspace via `nf_queue()`
     - `NF_STOLEN`: Packet consumed by hook
  4. Returns 1 if packet should continue to `okfn()`

#### nf_hook_entry_hookfn() - Line 155 in `/Users/sphinx/github/linux/include/linux/netfilter.h`
```c
static inline int
nf_hook_entry_hookfn(const struct nf_hook_entry *entry, struct sk_buff *skb,
                     struct nf_hook_state *state)
{
    return entry->hook(entry->priv, skb, state);
}
```

### Hook Priority Ordering

Hooks are ordered by ascending priority (lower number = higher priority):
- Priority is set in `nf_hook_ops.priority`
- New hooks are inserted before hooks with lower priority (higher number)
- Common priorities (defined in headers):
  - `NF_IP_PRI_FIRST`: -100
  - `NF_IP_PRI_CONNTRACK`: -200 (Conntrack runs first)
  - `NF_IP_PRI_MANGLE`: -150
  - `NF_IP_PRI_NAT_DST`: -100
  - `NF_IP_PRI_FILTER`: 0 (Standard filter)
  - `NF_IP_PRI_SECURITY`: 50
  - `NF_IP_PRI_NAT_SRC`: 100

### Hook Head Lookup

#### nf_hook_entry_head() - Line 275 in `/Users/sphinx/github/linux/net/netfilter/core.c`
```c
static struct nf_hook_entries __rcu **
nf_hook_entry_head(struct net *net, int pf, unsigned int hooknum,
                   struct net_device *dev)
```
- **Purpose**: Find the hook entries array for a given protocol family/hook
- **Behavior**: Switches on protocol family:
  - `NFPROTO_NETDEV`: Direct device hooks
  - `NFPROTO_ARP`: ARP hooks
  - `NFPROTO_BRIDGE`: Bridge hooks
  - `NFPROTO_INET`: Ingress hooks or dual IPv4/IPv6
  - `NFPROTO_IPV4`: IPv4 hooks
  - `NFPROTO_IPV6`: IPv6 hooks

---

## 2. iptables/xtables

### Location: `/Users/sphinx/github/linux/net/netfilter/x_tables.c`

### xt_table Structure (line 213 in `/Users/sphinx/github/linux/include/linux/netfilter/x_tables.h`)
```c
struct xt_table {
    struct list_head list;        // List of registered tables
    unsigned int valid_hooks;     // Bitmask of valid hook points
    struct xt_table_info *private; // Table entries (kernel internal)
    struct nf_hook_ops *ops;      // Hook ops for registration
    struct module *me;            // Owner module
    u_int8_t af;                  // Address family (NFPROTO_*)
    int priority;                 // Priority for hook ordering
    const char name[XT_TABLE_MAXNAMELEN];  // Table name
};
```

### xt_table_info Structure (line 238 in `/Users/sphinx/github/linux/include/linux/netfilter/x_tables.h`)
```c
struct xt_table_info {
    unsigned int size;            // Total size of entries
    unsigned int number;          // Number of entries
    unsigned int initial_entries; // Initial entry count
    unsigned int hook_entry[NF_INET_NUMHOOKS];  // Entry points per hook
    unsigned int underflow[NF_INET_NUMHOOKS];   // Underflow points
    unsigned int stacksize;       // Jump stack size
    void ***jumpstack;            // Jump stack for subchain calls
    unsigned char entries[];       // Rule entries blob
};
```

### xt_match Structure (line 132 in `/Users/sphinx/github/linux/include/linux/netfilter/x_tables.h`)
```c
struct xt_match {
    struct list_head list;         // Registration list
    const char name[XT_EXTENSION_MAXNAMELEN];  // Match name
    u_int8_t revision;            // Revision number
    
    bool (*match)(const struct sk_buff *skb,
                  struct xt_action_param *);   // Match function
    
    int (*checkentry)(const struct xt_mtchk_param *);  // Validation
    void (*destroy)(const struct xt_mtdtor_param *);   // Cleanup
    
    struct module *me;            // Owner module
    const char *table;           // Required table (or NULL)
    unsigned int matchsize;       // Size of match data
    unsigned int usersize;        // Userspace size
    unsigned int hooks;           // Hook bitmask
    unsigned short proto;         // Protocol (or 0 for all)
    unsigned short family;        // Address family
};
```

### xt_target Structure (line 172 in `/Users/sphinx/github/linux/include/linux/netfilter/x_tables.h`)
```c
struct xt_target {
    struct list_head list;
    const char name[XT_EXTENSION_MAXNAMELEN];
    u_int8_t revision;
    
    // Target function: returns verdict (NF_ACCEPT, NF_DROP, etc.)
    unsigned int (*target)(struct sk_buff *skb,
                          const struct xt_action_param *);
    
    int (*checkentry)(const struct xt_tgchk_param *);  // Validation
    void (*destroy)(const struct xt_tgdtor_param *);   // Cleanup
    
    struct module *me;
    const char *table;
    unsigned int targetsize;      // Size of target data
    unsigned int usersize;       // Userspace size
    unsigned int hooks;           // Hook bitmask
    unsigned short proto;
    unsigned short family;
};
```

### Entry Structures (Userspace/Kernel ABI)

#### xt_entry_match (line 11 in `/Users/sphinx/github/linux/include/uapi/linux/netfilter/x_tables.h`)
```c
struct xt_entry_match {
    union {
        struct {
            __u16 match_size;    // Total size of entry
            char name[XT_EXTENSION_MAXNAMELEN];  // Match name
            __u8 revision;       // Revision
        } user;
        struct {
            __u16 match_size;
            struct xt_match *match;  // Kernel internal
        } kernel;
        __u16 match_size;        // Total length
    } u;
    unsigned char data[];        // Match-specific data
};
```

#### xt_entry_target (line 34 in `/Users/sphinx/github/linux/include/uapi/linux/netfilter/x_tables.h`)
```c
struct xt_entry_target {
    union {
        struct {
            __u16 target_size;
            char name[XT_EXTENSION_MAXNAMELEN];
            __u8 revision;
        } user;
        struct {
            __u16 target_size;
            struct xt_target *target;  // Kernel internal
        } kernel;
        __u16 target_size;
    } u;
    unsigned char data[0];       // Target-specific data
};
```

### Match/Target Registration

#### xt_register_match() - Line 139 in `/Users/sphinx/github/linux/net/netfilter/x_tables.c`
```c
int xt_register_match(struct xt_match *match)
{
    u_int8_t af = match->family;
    mutex_lock(&xt[af].mutex);
    list_add(&match->list, &xt[af].match);
    mutex_unlock(&xt[af].mutex);
    return 0;
}
```

#### xt_register_target() - Line 89 in `/Users/sphinx/github/linux/net/netfilter/x_tables.c`
```c
int xt_register_target(struct xt_target *target)
{
    u_int8_t af = target->family;
    mutex_lock(&xt[af].mutex);
    list_add(&target->list, &xt[af].target);
    mutex_unlock(&xt[af].mutex);
    return 0;
}
```

#### xt_find_match() - Line 197 in `/Users/sphinx/github/linux/net/netfilter/x_tables.c`
```c
struct xt_match *xt_find_match(u8 af, const char *name, u8 revision)
```
- Finds a match by name and revision
- Returns with refcount held on success
- Falls back to `NFPROTO_UNSPEC` for family-independent matches

#### xt_find_target() - Line 246 in `/Users/sphinx/github/linux/net/netfilter/x_tables.c`
```c
static struct xt_target *xt_find_target(u8 af, const char *name, u8 revision)
```
- Similar to `xt_find_match()` but for targets

### Validation Functions

#### xt_check_match() - Line 480 in `/Users/sphinx/github/linux/net/netfilter/x_tables.c`
```c
int xt_check_match(struct xt_mtchk_param *par,
                   unsigned int size, u16 proto, bool inv_proto)
```
- Validates match size alignment
- Checks table constraints
- Verifies protocol match
- Validates hook mask

#### xt_check_target() - Line ~520 in `/Users/sphinx/github/linux/net/netfilter/x_tables.c`
```c
int xt_check_target(struct xt_tgchk_param *par,
                    unsigned int size, u16 proto, bool inv_proto)
```
- Similar validation for targets

### Translation from iptables Syntax to Kernel Structures

1. **Userspace iptables** sends netlink messages with rule specifications
2. **Kernel** receives via `ipt_do_table()` (in ip_tables.c)
3. For each entry:
   - Matches are validated and iterated
   - Target is checked and executed
   - Verdict determines packet fate

---

## 3. nf_tables

### Location: `/Users/sphinx/github/linux/net/netfilter/nf_tables_api.c`

### nft_table Structure (line 1311 in `/Users/sphinx/github/linux/include/net/netfilter/nf_tables.h`)
```c
struct nft_table {
    struct list_head list;           // Table list
    struct rhltable chains_ht;       // Chain hash table
    struct list_head chains;         // Chain list
    struct list_head sets;           // Sets in table
    struct list_head objects;        // Stateful objects
    struct list_head flowtables;     // Flow tables
    u64 hgenerator;                  // Handle generator state
    u64 handle;                      // Table handle
    u32 use;                         // Reference count
    u16 family:6;                    // Address family
    u16 flags:8;                     // Table flags
    u16 genmask:2;                   // Generation mask
    u32 nlpid;                       // Netlink port ID
    char *name;                      // Table name
    u16 udlen;                       // User data length
    u8 *udata;                       // User data
    u8 validate_state;                // Validation state
};
```

### nft_chain Structure (line 1142 in `/Users/sphinx/github/linux/include/net/netfilter/nf_tables.h`)
```c
struct nft_chain {
    struct nft_rule_blob __rcu *blob_gen_0;  // Current generation rules
    struct nft_rule_blob __rcu *blob_gen_1;  // Next generation rules
    struct list_head rules;                   // Rule list
    struct list_head list;                    // Table chain list
    struct rhlist_head rhlhead;               // Hash list head
    struct nft_table *table;                  // Parent table
    u64 handle;                               // Chain handle
    u32 use;                                  // Reference count
    u8 flags:5;                               // Chain flags
    u8 bound:1;                              // Bound to rule
    u8 genmask:2;                            // Generation mask
    char *name;                              // Chain name
    u16 udlen;                               // User data length
    u8 *udata;                               // User data
    struct nft_rule_blob *blob_next;         // Commit phase pointer
    struct nft_chain_validate_state vstate;   // Validation state
};
```

### nft_base_chain Structure (line 1244 in `/Users/sphinx/github/linux/include/net/netfilter/nf_tables.h`)
```c
struct nft_base_chain {
    struct nf_hook_ops ops;                  // Netfilter hook ops
    struct list_head hook_list;              // Hook list for netdev
    const struct nft_chain_type *type;      // Chain type
    u8 policy;                               // Default policy
    u8 flags;                                // Flags
    struct nft_stats __percpu *stats;       // Per-CPU stats
    struct nft_chain chain;                  // Base chain
    struct flow_block flow_block;            // Flow block for offload
};
```

### nft_rule Structure (line 1002 in `/Users/sphinx/github/linux/include/net/netfilter/nf_tables.h`)
```c
struct nft_rule {
    struct list_head list;
    u64 handle:42;          // Rule handle
    u64 genmask:2;          // Generation mask
    u64 dlen:12;            // Data length
    u64 udata:1;            // Has user data
    unsigned char data[];    // Expression data
};
```

### nft_rule_blob Structure (line 1093 in `/Users/sphinx/github/linux/include/net/netfilter/nf_tables.h`)
```c
struct nft_rule_blob {
    unsigned long size;
    unsigned char data[];    // Rule data (nft_rule_dp array)
};
```

### nft_rule_dp Structure (line 1073 in `/Users/sphinx/github/linux/include/net/netfilter/nf_tables.h`)
```c
struct nft_rule_dp {
    u64 is_last:1;           // Last rule marker
    u64 dlen:12;             // Data length
    u64 handle:42;           // Handle for tracing
    unsigned char data[];    // Expression data
};
```

### nft_do_chain() - Line 249 in `/Users/sphinx/github/linux/net/netfilter/nf_tables_core.c`

```c
unsigned int nft_do_chain(struct nft_pktinfo *pkt, void *priv)
{
    const struct nft_chain *chain = priv, *basechain = chain;
    const struct net *net = nft_net(pkt);
    const struct nft_expr *expr, *last;
    const struct nft_rule_dp *rule;
    struct nft_regs regs;
    unsigned int stackptr = 0;
    struct nft_jumpstack jumpstack[NFT_JUMP_STACK_SIZE];
    bool genbit = READ_ONCE(net->nft.gencursor);
    struct nft_rule_blob *blob;
    struct nft_traceinfo info;
```
- **Purpose**: Main packet processing function for nf_tables
- **Behavior**:
  1. Selects generation (blob_gen_0 or blob_gen_1) based on `gencursor`
  2. Iterates through rules in the chain
  3. For each rule, evaluates expressions:
     - Fast path: `nft_cmp_fast_eval`, `nft_cmp16_fast_eval`, `nft_bitwise_fast_eval`, `nft_payload_fast_eval`
     - Slow path: `expr_call_ops_eval()` for complex expressions
  4. Handles verdicts:
     - `NFT_BREAK`: Continue to next rule
     - `NFT_CONTINUE`: Continue rule evaluation
     - `NFT_JUMP`: Push current position, jump to subchain
     - `NFT_GOTO`: Jump to subchain without saving position
     - `NFT_RETURN`: Return from subchain
  5. Uses jumpstack for NFT_JUMP (max depth: `NFT_JUMP_STACK_SIZE` = 16)
  6. Returns final verdict to caller

### Transaction Model

The transaction model in nf_tables allows atomic rule updates:

1. **Preparation Phase** (`NFT_TRANS_PREPARE`):
   - New rules/chains are created
   - Modifications stored in `nft_trans` structures
   - Added to `commit_list`

2. **Commit Phase** (`NFT_TRANS_COMMIT`):
   - Generation cursor switches (blob_gen_0 <-> blob_gen_1)
   - New structures become active
   - Old structures marked for cleanup

3. **Release Phase** (`NFT_TRANS_RELEASE`):
   - Old generation structures freed after RCU grace period

#### nft_trans_alloc() - Line 178 in `/Users/sphinx/github/linux/net/netfilter/nf_tables_api.c`
```c
static struct nft_trans *nft_trans_alloc(const struct nft_ctx *ctx,
                                         int msg_type, u32 size)
{
    struct nft_trans *trans;
    trans = kzalloc(size, GFP_KERNEL);
    // Initialize transaction
    INIT_LIST_HEAD(&trans->list);
    trans->msg_type = msg_type;
    trans->net = ctx->net;
    trans->table = ctx->table;
    // ...
    return trans;
}
```

### Flow Table Registration

#### nft_register_flowtable_ops() - Line 8920 in `/Users/sphinx/github/linux/net/netfilter/nf_tables_api.c`
```c
static int nft_register_flowtable_ops(struct net *net,
                                      struct nft_flowtable *flowtable,
                                      struct nft_hook *hook)
```
- Registers flow table hooks with netfilter core
- Sets up hardware offload path if available

---

## 4. Conntrack Integration

### Location: `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_netlink.c`

### ctnetlink_create_conntrack() - Line 2234 in `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_netlink.c`

```c
static struct nf_conn *
ctnetlink_create_conntrack(struct net *net,
                           const struct nf_conntrack_zone *zone,
                           const struct nlattr * const cda[],
                           struct nf_conntrack_tuple *otuple,
                           struct nf_conntrack_tuple *rtuple,
                           u8 u3)
{
    struct nf_conn *ct;
    int err = -EINVAL;
    struct nf_conntrack_helper *helper;
    struct nf_conn_tstamp *tstamp;
    u64 timeout;

    ct = nf_conntrack_alloc(net, zone, otuple, rtuple, GFP_ATOMIC);
    if (IS_ERR(ct))
        return ERR_PTR(-ENOMEM);
```
- **Purpose**: Create a new conntrack entry via ctnetlink
- **Behavior**:
  1. Allocates conntrack via `nf_conntrack_alloc()`
  2. Parses helper info if present
  3. Sets up NAT if configured
  4. Adds extensions (acct, timestamp, labels, seqadj, synproxy)
  5. Sets timeout from netlink attribute
  6. Inserts into hash table via `nf_conntrack_hash_check_insert()`

### ctnetlink_get_conntrack() - Line 1667 in `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_netlink.c`

```c
static int ctnetlink_get_conntrack(struct sk_buff *skb,
                                   const struct nfnl_info *info,
                                   const struct nlattr * const cda[])
```
- **Purpose**: Get conntrack entries via ctnetlink
- **Behavior**:
  1. Parses tuple attributes
  2. Looks up conntrack by tuple
  3. Dumps conntrack state to netlink message

### nf_ct_put() - Line 34 in `/Users/sphinx/github/linux/include/linux/netfilter/nf_conntrack_common.h`

```c
static inline void nf_ct_put(struct nf_conntrack *nfct)
{
    WARN_ON(!refcount_read(&nfct->use));
    if (nfct)
        nf_conntrack_put(nfct);
}
```
- **Purpose**: Release reference to conntrack
- **Behavior**: Wrapper around `nf_conntrack_put()` with sanity check

---

## 5. Specific Match/Target Modules

### xt_DSCP.c - DSCP Marking

**Location**: `/Users/sphinx/github/linux/net/netfilter/xt_DSCP.c`

#### xt_dscp_info Structure (from `/Users/sphinx/github/linux/include/uapi/linux/netfilter/xt_dscp.h`)
```c
struct xt_dscp_info {
    __u8 dscp;     // DSCP value to match/mark
    __u8 invert;   // Invert match
};

struct xt_tos_match_info {
    __u8 tos_mask;
    __u8 tos_value;
    __u8 invert;
};
```

#### dscp_mt() - Line 24 in `/Users/sphinx/github/linux/net/netfilter/xt_DSCP.c`
```c
static bool
dscp_mt(const struct sk_buff *skb, struct xt_action_param *par)
{
    const struct xt_dscp_info *info = par->matchinfo;
    u_int8_t dscp = ipv4_get_dsfield(ip_hdr(skb)) >> XT_DSCP_SHIFT;
    
    return (dscp == info->dscp) ^ !!info->invert;
}
```
- Extracts DSCP from IPv4 header
- Compares with match info
- XORs with invert flag for result

#### dscp_mt6() - Line 33 in `/Users/sphinx/github/linux/net/netfilter/xt_DSCP.c`
```c
static bool
dscp_mt6(const struct sk_buff *skb, struct xt_action_param *par)
{
    const struct xt_dscp_info *info = par->matchinfo;
    u_int8_t dscp = ipv6_get_dsfield(ipv6_hdr(skb)) >> XT_DSCP_SHIFT;
    
    return (dscp == info->dscp) ^ !!info->invert;
}
```
- Same as above but for IPv6

#### dscp_mt_check() - Line 42 in `/Users/sphinx/github/linux/net/netfilter/xt_DSCP.c`
```c
static int dscp_mt_check(const struct xt_mtchk_param *par)
{
    const struct xt_dscp_info *info = par->matchinfo;
    
    if (info->dscp > XT_DSCP_MAX)
        return -EDOM;  // Domain error
    
    return 0;
}
```
- Validates DSCP value is within valid range (0-63)

---

### xt_HL.c - Hop Limit Modification

**Location**: `/Users/sphinx/github/linux/net/netfilter/xt_HL.c`

#### Hop Limit Match for IPv4 (ttl_mt) - Line 25
```c
static bool ttl_mt(const struct sk_buff *skb, struct xt_action_param *par)
{
    const struct ipt_ttl_info *info = par->matchinfo;
    const u8 ttl = ip_hdr(skb)->ttl;
    
    switch (info->mode) {
    case IPT_TTL_EQ:  return ttl == info->ttl;
    case IPT_TTL_NE:  return ttl != info->ttl;
    case IPT_TTL_LT:  return ttl < info->ttl;
    case IPT_TTL_GT:  return ttl > info->ttl;
    }
    return false;
}
```

#### Hop Limit Match for IPv6 (hl_mt6) - Line 44
```c
static bool hl_mt6(const struct sk_buff *skb, struct xt_action_param *par)
{
    const struct ip6t_hl_info *info = par->matchinfo;
    const struct ipv6hdr *ip6h = ipv6_hdr(skb);
    
    switch (info->mode) {
    case IP6T_HL_EQ:  return ip6h->hop_limit == info->hop_limit;
    case IP6T_HL_NE:  return ip6h->hop_limit != info->hop_limit;
    case IP6T_HL_LT:  return ip6h->hop_limit < info->hop_limit;
    case IP6T_HL_GT:  return ip6h->hop_limit > info->hop_limit;
    }
    return false;
}
```

#### Match Registration - Line 63
```c
static struct xt_match hl_mt_reg[] __read_mostly = {
    {
        .name       = "ttl",
        .revision   = 0,
        .family     = NFPROTO_IPV4,
        .match      = ttl_mt,
        .matchsize  = sizeof(struct ipt_ttl_info),
        .me         = THIS_MODULE,
    },
    {
        .name       = "hl",
        .revision   = 0,
        .family     = NFPROTO_IPV6,
        .match      = hl_mt6,
        .matchsize  = sizeof(struct ip6t_hl_info),
        .me         = THIS_MODULE,
    },
};
```

---

### xt_RATEEST.c - Rate Estimation

**Location**: `/Users/sphinx/github/linux/net/netfilter/xt_RATEEST.c`

#### Rate Estimation Match - Line 14
```c
static bool
xt_rateest_mt(const struct sk_buff *skb, struct xt_action_param *par)
{
    const struct xt_rateest_match_info *info = par->matchinfo;
    struct gnet_stats_rate_est64 sample = {0};
    u_int32_t bps1, bps2, pps1, pps2;
    bool ret = true;
    
    gen_estimator_read(&info->est1->rate_est, &sample);
    
    if (info->flags & XT_RATEEST_MATCH_DELTA) {
        bps1 = info->bps1 >= sample.bps ? info->bps1 - sample.bps : 0;
        pps1 = info->pps1 >= sample.pps ? info->pps1 - sample.pps : 0;
    } else {
        bps1 = sample.bps;
        pps1 = sample.pps;
    }
```
- Reads rate estimation statistics from first estimator
- Optionally computes delta (difference from stored value)

#### xt_rateest_mt_checkentry() - Line 72
```c
static int xt_rateest_mt_checkentry(const struct xt_mtchk_param *par)
{
    struct xt_rateest_match_info *info = par->matchinfo;
    struct xt_rateest *est1, *est2;
    
    // Validates flags, mode, and name lengths
    // Looks up rate estimators by name
    est1 = xt_rateest_lookup(par->net, info->name1);
    est2 = xt_rateest_lookup(par->net, info->name2);
    
    info->est1 = est1;
    info->est2 = est2;
    return 0;
}
```

---

### xt_TCPMSS.c - TCP MSS Clamping

**Location**: `/Users/sphinx/github/linux/net/netfilter/xt_TCPMSS.c`

#### TCP MSS Match - Line 24
```c
static bool
tcpmss_mt(const struct sk_buff *skb, struct xt_action_param *par)
{
    const struct xt_tcpmss_match_info *info = par->matchinfo;
    const struct tcphdr *th;
    struct tcphdr _tcph;
    const u_int8_t *op;
    u8 _opt[15 * 4 - sizeof(_tcph)];
    unsigned int i, optlen;
    
    th = skb_header_pointer(skb, par->thoff, sizeof(_tcph), &_tcph);
    if (th == NULL)
        goto dropit;
    
    if (th->doff*4 < sizeof(*th))
        goto dropit;
    
    optlen = th->doff*4 - sizeof(*th);
    if (!optlen)
        goto out;
    
    op = skb_header_pointer(skb, par->thoff + sizeof(*th), optlen, _opt);
    if (op == NULL)
        goto dropit;
    
    for (i = 0; i < optlen; ) {
        if (op[i] == TCPOPT_MSS
            && (optlen - i) >= TCPOLEN_MSS
            && op[i+1] == TCPOLEN_MSS) {
            u_int16_t mssval;
            mssval = (op[i+2] << 8) | op[i+3];
            
            return (mssval >= info->mss_min &&
                    mssval <= info->mss_max) ^ info->invert;
        }
        if (op[i] < 2 || i == optlen - 1)
            i++;
        else
            i += op[i+1] ? : 1;
    }
out:
    return info->invert;

dropit:
    par->hotdrop = true;
    return false;
}
```
- Parses TCP options looking for MSS option (kind=2, len=4)
- Extracts MSS value from options
- Compares against min/max range

---

### xt_MARK.c - MARK Target

**Location**: `/Users/sphinx/github/linux/include/uapi/linux/netfilter/xt_MARK.h`

```c
struct xt_mark_tginfo2 {
    __u32 mark, mask;   // Mark value and mask
};

struct xt_mark_mtinfo1 {
    __u32 mark, mask;
    __u8 invert;
};
```

The actual implementation is typically in `net/netfilter/xt_mark.c` which:
- For match: Compares `skb->mark` with `info->mark` masked by `info->mask`
- For target: Sets `skb->mark` using formula: `(skb->mark & ~mask) | (mark & mask)`

---

## 6. Key Data Structures

### struct sk_buff - Packet Buffer

**Location**: `/Users/sphinx/github/linux/include/linux/skbuff.h`

Key netfilter-relevant fields:

```c
struct sk_buff {
    /* Netfilter related fields (when CONFIG_NF_CONNTRACK): */
    unsigned long _nfct;           // Connection tracking info
    
    /* Network header offset */
    unsigned int network_header;   // Offset to network header
    unsigned int transport_header; // Offset to transport header
    unsigned int mac_header;      // Offset to MAC header
    
    /* Packet marks */
    __u32 mark;                   // Skb mark (used by fwmark, etc.)
    
    /* Transfer type */
    __u16 tc_index;               // Traffic control index
    
    /* VLAN */
    __u16 vlan_proto;             // VLAN protocol
    __u16 vlan_tci;               // VLAN TCI
    
    /* Checksum */
    __sum16 csum;                 // Checksum
    __u8 ip_summed;               // Checksum status (CHECKSUM_*)
    
    /* Network namespace */
    struct net *skb_net;         // Network namespace
    
    /* Other key fields */
    struct sock *sk;              // Socket
    struct net_device *dev;      // Device
    struct sk_buff *next;         // Queue next
    struct sk_buff *prev;        // Queue prev
    
    // ... many more fields
};
```

Key accessor functions:
- `skb_network_header(skb)` - Get network layer header
- `skb_transport_header(skb)` - Get transport layer header
- `skb_mac_header(skb)` - Get MAC header
- `skb_mac_header_was_set(skb)` - Check if MAC header is set
- `skb_vlan_tag_get(skb)` - Get VLAN tag

### struct net_device - Network Device

**Location**: `/Users/sphinx/github/linux/include/linux/netdevice.h`

Key netfilter-relevant fields:

```c
struct net_device {
    char name[IFNAMSIZ];          // Device name
    unsigned long flags;          // IFF_* flags
    unsigned int features;        // NETIF_F_* features
    
    /* Netfilter hooks on this device */
#ifdef CONFIG_NETFILTER_INGRESS
    struct nf_hook_entries __rcu *nf_hooks_ingress;
#endif
#ifdef CONFIG_NETFILTER_EGRESS
    struct nf_hook_entries __rcu *nf_hooks_egress;
#endif
    
    /* Device chain */
    struct list_head napi_list;   // NAPI poll list
    
    // ... many more fields
};
```

### struct net - Network Namespace

**Location**: `/Users/sphinx/github/linux/include/net/net_namespace.h`

Key netfilter-relevant fields:

```c
struct net {
    /* Per-namespace netfilter hooks */
    struct netns_nf nf;
    
    /* nftables state */
    struct netns_nft nft;
    
    // ... many more fields
};
```

The `netns_nf` structure contains:
```c
struct netns_nf {
    struct nf_hook_entries __rcu *hooks_ipv4[NF_INET_NUMHOOKS];
    struct nf_hook_entries __rcu *hooks_ipv6[NF_INET_NUMHOOKS];
#ifdef CONFIG_NETFILTER_FAMILY_ARP
    struct nf_hook_entries __rcu *hooks_arp[NF_INET_NUMHOOKS];
#endif
#ifdef CONFIG_NETFILTER_FAMILY_BRIDGE
    struct nf_hook_entries __rcu *hooks_bridge[NF_INET_NUMHOOKS];
#endif
    struct proc_dir_entry *proc_netfilter;
};
```

### struct flowi - Flow Identity

**Location**: `/Users/sphinx/github/linux/include/net/flow.h`

```c
struct flowi {
    __u8 flowic_oif;             // Output interface
    __u8 flowic_iif;             // Input interface
    __u8 flowic_tos;             // Type of service
    __u8 flowic_scope;           // Scope
    __u8 flowic_proto;           // Protocol
    __u8 flowic_mark;            // Firewall mark
    __u16 flowic_padding;        // Padding
    union nf_inet_addr flowic_u; // Addresses (IPv4 or IPv6)
    struct flowic_tunnel flowic_tunnel;  // Tunnel info
    // ... additional fields
};
```

---

## Call Chains - Packet Flow Through Hooks

### IPv4 Packet Ingress Flow

```
1. NIC Driver receives packet
   -> netif_rx() or netif_receive_skb()

2. IP Stack prerouting
   -> ip_rcv()
   -> ip_rcv_finish()
   -> ip_local_deliver()
   -> ip_local_deliver_finish()

3. Netfilter PREROUTING Hook (NF_INET_PRE_ROUTING)
   -> nf_hook(INET, PRE_ROUTING, net, sk, skb, dev, NULL, ip_local_deliver)
   -> For IPv4: net->nf.hooks_ipv4[NF_INET_PRE_ROUTING]
   -> nf_hook_slow() iterates hooks
   -> If NF_HOOK_COND returns 1, continue to ip_local_deliver()

4. Conntrack (if enabled, priority -200)
   -> nf_conntrack_in() (PREROUTING)
   -> Creates/updates connection tracking entry
   -> Sets skb->_nfct

5. NAT (if enabled, priority -100)
   -> nf_nat_pre_routing() (PREROUTING)
   -> Performs NAT translation

6. Mangle table PREROUTING (priority -150)
   -> iptable_mangle PRE_ROUTING

7. Filter/Destination NAT
   -> Remaining hooks in PREROUTING

8. Routing decision
   -> ip_route_input() or ip_route_input_slow()
   -> Determines local delivery or forward

9a. LOCAL IN (for local delivery):
    -> ip_local_deliver()
    -> NF_INET_LOCAL_IN hook
    -> Filter INPUT chain
    -> Transport layer (TCP/UDP)

9b. FORWARD (for forwarding):
    -> ip_forward()
    -> ip_forward_finish()
    -> NF_INET_FORWARD hook
    -> Filter FORWARD chain
    -> ip_output()
    -> NF_INET_POST_ROUTING hook
```

### nf_tables Packet Flow

```
1. Hook registered via nft_register_flowtable_ops()
   or nf_register_net_hook()

2. Packet enters nft_do_chain()

3. For each rule in chain:
   a. For each expression:
      - Fast eval: nft_cmp_fast_eval, nft_bitwise_fast_eval
      - Slow eval: expr->ops->eval()
      
   b. If expr returns verdict != NFT_CONTINUE:
      - NFT_BREAK: Skip to next rule
      - NFT_JUMP: Push position, jump to subchain
      - NFT_GOTO: Jump to subchain
      - NFT_RETURN: Pop from stack or return
      - Verdict (NF_ACCEPT, NF_DROP, etc.): Return

4. If no rule matches:
   - Return chain policy (NF_ACCEPT or NF_DROP)

5. Update stats if enabled
```

### Extension Registration Call Chain

```
1. Module init
   -> xt_register_matches() or xt_register_targets()

2. xt_register_match():
   mutex_lock(&xt[af].mutex)
   list_add(&match->list, &xt[af].match)
   mutex_unlock(&xt[af].mutex)

3. At rule insertion time:
   -> xt_find_match() or xt_find_target()
   -> try_module_get(match->me)

4. Match/target checked and called:
   -> match->match() or target->target()
```

---

## Hook Priority Summary (IPv4)

| Priority | Component |
|----------|-----------|
| -300 | NF_IP_PRI_FIRST |
| -200 | NF_IP_PRI_CONNTRACK (Conntrack) |
| -150 | NF_IP_PRI_MANGLE (mangle table PREROUTING) |
| -100 | NF_IP_PRI_NAT_DST (DNAT) |
| 0 | NF_IP_PRI_FILTER (filter) |
| 50 | NF_IP_PRI_SECURITY (SELinux) |
| 100 | NF_IP_PRI_NAT_SRC (SNAT) |
| 200 | NF_IP_PRI_LAST |

---

## Key Files Summary

| File | Purpose |
|------|---------|
| `/Users/sphinx/github/linux/net/netfilter/core.c` | Core hook infrastructure |
| `/Users/sphinx/github/linux/net/netfilter/x_tables.c` | xtables backend |
| `/Users/sphinx/github/linux/net/netfilter/nf_tables_api.c` | nf_tables API |
| `/Users/sphinx/github/linux/net/netfilter/nf_tables_core.c` | nf_tables core (nft_do_chain) |
| `/Users/sphinx/github/linux/net/netfilter/nf_tables_trace.c` | nf_tables tracing |
| `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_netlink.c` | Conntrack netlink interface |
| `/Users/sphinx/github/linux/net/netfilter/xt_DSCP.c` | DSCP match |
| `/Users/sphinx/github/linux/net/netfilter/xt_HL.c` | Hop Limit match |
| `/Users/sphinx/github/linux/net/netfilter/xt_RATEEST.c` | Rate estimation match |
| `/Users/sphinx/github/linux/net/netfilter/xt_TCPMSS.c` | TCP MSS match |
| `/Users/sphinx/github/linux/include/linux/netfilter.h` | Core netfilter definitions |
| `/Users/sphinx/github/linux/include/linux/netfilter/x_tables.h` | xtables definitions |
| `/Users/sphinx/github/linux/include/net/netfilter/nf_tables.h` | nf_tables kernel API |
| `/Users/sphinx/github/linux/include/uapi/linux/netfilter/nf_tables.h` | nf_tables userspace ABI |
| `/Users/sphinx/github/linux/include/linux/skbuff.h` | sk_buff definition |

---

## End of Analysis
