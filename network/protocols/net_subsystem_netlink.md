# Linux Kernel Netlink Protocol Implementation: Comprehensive Analysis

## Table of Contents

1. [Core Netlink Infrastructure](#1-core-netlink-infrastructure)
2. [Generic Netlink (genetlink)](#2-generic-netlink-genetlink)
3. [Netfilter Netlink (nfnetlink)](#3-netfilter-netlink-nfnetlink)
4. [Conntrack Netlink](#4-conntrack-netlink)
5. [Routing Netlink (rtnetlink)](#5-routing-netlink-rtnetlink)
6. [IPv6 Address Configuration (addrconf)](#6-ipv6-address-configuration-addrconf)

---

## 1. Core Netlink Infrastructure

### 1.1 struct nlmsghdr

**File:** `include/uapi/linux/netlink.h`

```c
struct nlmsghdr {
    __u32 nlmsg_len;      /* Length including header */
    __u16 nlmsg_type;     /* Message type (protocol-specific) */
    __u16 nlmsg_flags;    /* NLM_F_REQUEST, NLM_F_ACK, etc. */
    __u32 nlmsg_seq;      /* Sequence number */
    __u32 nlmsg_pid;      /* Sender portid (PID for userspace) */
};
```

### 1.2 struct netlink_sock

**File:** `net/netlink/af_netlink.h`, lines 24-52

```c
struct netlink_sock {
    struct sock         sk;           /* Must be first member */
    unsigned long       flags;
    u32                 portid;       /* Local portid (PID) */
    u32                 dst_portid;  /* Destination portid */
    u32                 dst_group;   /* Destination multicast group */
    u32                 subscriptions;
    u32                 ngroups;
    unsigned long       *groups;
    unsigned long       state;
    size_t              max_recvmsg_len;
    wait_queue_head_t   wait;
    bool                bound;
    bool                cb_running;
    int                 dump_done_errno;
    struct netlink_callback cb;
    struct mutex        nl_cb_mutex;
    void                (*netlink_rcv)(struct sk_buff *skb);
    int                 (*netlink_bind)(struct net *net, int group);
    void                (*netlink_unbind)(struct net *net, int group);
    void                (*netlink_release)(struct sock *sk, unsigned long *groups);
    struct module       *module;
    struct rhash_head   node;
    struct rcu_head     rcu;
};
```

### 1.3 netlink_skb_destructor()

**File:** `net/netlink/af_netlink.c`, lines 372-383

```c
static void netlink_skb_destructor(struct sk_buff *skb)
{
    if (is_vmalloc_addr(skb->head)) {
        if (!skb->cloned ||
            !atomic_dec_return(&(skb_shinfo(skb)->dataref)))
            vfree_atomic(skb->head);
        skb->head = NULL;
    }
    if (skb->sk != NULL)
        sock_rfree(skb);
}
```

Purpose: Frees vmalloc'd skb heads and accounts for socket memory.

### 1.4 netlink_skb_set_owner_r()

**File:** `net/netlink/af_netlink.c`, lines 385-391

```c
static void netlink_skb_set_owner_r(struct sk_buff *skb, struct sock *sk)
{
    WARN_ON(skb->sk != NULL);
    skb->sk = sk;
    skb->destructor = netlink_skb_destructor;
    sk_mem_charge(sk, skb->truesize);
}
```

### 1.5 netlink_insert()

**File:** `net/netlink/af_netlink.c`, lines 552-591

```c
static int netlink_insert(struct sock *sk, u32 portid)
{
    struct netlink_table *table = &nl_table[sk->sk_protocol];
    int err;

    lock_sock(sk);

    err = nlk_sk(sk)->portid == portid ? 0 : -EBUSY;
    if (nlk_sk(sk)->bound)
        goto err;

    WRITE_ONCE(nlk_sk(sk)->portid, portid);
    sock_hold(sk);

    err = __netlink_insert(table, sk);
    if (err) {
        if (unlikely(err == -EBUSY))
            err = -EOVERFLOW;
        if (err == -EEXIST)
            err = -EADDRINUSE;
        sock_put(sk);
        goto err;
    }

    smp_wmb();
    WRITE_ONCE(nlk_sk(sk)->bound, portid);

err:
    release_sock(sk);
    return err;
}
```

### 1.6 netlink_ack()

**File:** `net/netlink/af_netlink.c`, lines 2463-2522

```c
void netlink_ack(struct sk_buff *in_skb, struct nlmsghdr *nlh, int err,
             const struct netlink_ext_ack *extack)
{
    struct sk_buff *skb;
    struct nlmsghdr *rep;
    struct nlmsgerr *errmsg;
    size_t payload = sizeof(*errmsg);
    struct netlink_sock *nlk = nlk_sk(NETLINK_CB(in_skb).sk);
    unsigned int flags = 0;
    size_t tlvlen;

    /* Error messages get original request appended, unless capped */
    if (err && !test_bit(NETLINK_F_CAP_ACK, &nlk->flags))
        payload += nlmsg_len(nlh);
    else
        flags |= NLM_F_CAPPED;

    tlvlen = netlink_ack_tlv_len(nlk, err, extack);
    if (tlvlen)
        flags |= NLM_F_ACK_TLVS;

    skb = nlmsg_new(payload + tlvlen, GFP_KERNEL);
    // ... builds NLMSG_ERROR message with optional TLVs for extended ack ...
    nlmsg_unicast(in_skb->sk, skb, NETLINK_CB(in_skb).portid);
}
```

---

## 2. Generic Netlink (genetlink)

### 2.1 struct genlmsghdr

**File:** `include/uapi/linux/genetlink.h`

```c
struct genlmsghdr {
    __u8 cmd;      /* Family-specific command */
    __u8 version;  /* Family version */
    __u16 reserved; /* Must be 0 */
};
```

### 2.2 genl_register_family()

**File:** `net/netlink/genetlink.c`, lines 780-844

```c
int genl_register_family(struct genl_family *family)
{
    int err, i;
    int start = GENL_START_ALLOC, end = GENL_MAX_ID;

    err = genl_validate_ops(family);
    if (err)
        return err;

    genl_lock_all();  /* Takes cb_lock + genl_mutex */

    if (genl_family_find_byname(family->name)) {
        err = -EEXIST;
        goto errout_locked;
    }

    err = genl_sk_privs_alloc(family);
    if (err)
        goto errout_locked;

    /* Special cases for abused APIs */
    if (family == &genl_ctrl) {
        start = end = GENL_ID_CTRL;
    } else if (strcmp(family->name, "pmcraid") == 0) {
        start = end = GENL_ID_PMCRAID;
    } else if (strcmp(family->name, "VFS_DQUOT") == 0) {
        start = end = GENL_ID_VFS_DQUOT;
    }

    family->id = idr_alloc_cyclic(&genl_fam_idr, family, start, end + 1, GFP_KERNEL);
    if (family->id < 0) {
        err = family->id;
        goto errout_sk_privs_free;
    }

    err = genl_validate_assign_mc_groups(family);
    if (err)
        goto errout_remove;

    genl_unlock_all();

    genl_ctrl_event(CTRL_CMD_NEWFAMILY, family, NULL, 0);
    for (i = 0; i < family->n_mcgrps; i++)
        genl_ctrl_event(CTRL_CMD_NEWMCAST_GRP, family, &family->mcgrps[i],
                        family->mcgrp_offset + i);

    return 0;
```

### 2.3 genl_rcv_msg()

**File:** `net/netlink/genetlink.c`, lines 1198-1213

```c
static int genl_rcv_msg(struct sk_buff *skb, struct nlmsghdr *nlh,
            struct netlink_ext_ack *extack)
{
    const struct genl_family *family;
    int err;

    family = genl_family_find_byid(nlh->nlmsg_type);
    if (family == NULL)
        return -ENOENT;

    genl_op_lock(family);
    err = genl_family_rcv_msg(family, skb, nlh, extack);
    genl_op_unlock(family);

    return err;
}
```

---

## 3. Netfilter Netlink (nfnetlink)

### 3.1 struct nfgenmsg

**File:** `include/uapi/linux/netfilter/nfnetlink.h`

```c
struct nfgenmsg {
    __u8  nfgen_family;  /* AF_INET, AF_INET6, etc. */
    __u8  version;       /* nfnetlink version (always NFNETLINK_V0) */
    __be16 res_id;       /* Resource ID (e.g., NFNL_SUBSYS_*) */
};
```

### 3.2 nfnetlink_subsystem_register()

**File:** `net/netfilter/nfnetlink.c`, lines 116-135

```c
int nfnetlink_subsystem_register(const struct nfnetlink_subsystem *n)
{
    u8 cb_id;

    for (cb_id = 0; cb_id < n->cb_count; cb_id++)
        if (WARN_ON(n->cb[cb_id].attr_count > NFNL_MAX_ATTR_COUNT))
            return -EINVAL;

    nfnl_lock(n->subsys_id);
    if (table[n->subsys_id].subsys) {
        nfnl_unlock(n->subsys_id);
        return -EBUSY;
    }
    rcu_assign_pointer(table[n->subsys_id].subsys, n);
    nfnl_unlock(n->subsys_id);

    return 0;
}
```

### 3.3 nfnetlink_rcv_msg()

**File:** `net/netfilter/nfnetlink.c`, lines 216-314

Main netfilter netlink message dispatcher that:
1. Looks up subsystem by message type
2. Finds the callback for the operation
3. Parses attributes with nla_parse_deprecated()
4. Calls the callback (either RCU or mutex protected)

---

## 4. Conntrack Netlink

### 4.1 CTA_* Attributes

**File:** `net/netfilter/nf_conntrack_netlink.c`, lines 1556-1577

```c
static const struct nla_policy ct_nla_policy[CTA_MAX+1] = {
    [CTA_TUPLE_ORIG]    = { .type = NLA_NESTED },
    [CTA_TUPLE_REPLY]    = { .type = NLA_NESTED },
    [CTA_STATUS]         = { .type = NLA_U32 },
    [CTA_PROTO_INFO]    = { .type = NLA_NESTED },
    [CTA_HELP]          = { .type = NLA_NESTED },
    [CTA_NAT_SRC]       = { .type = NLA_NESTED },
    [CTA_TIMEOUT]       = { .type = NLA_U32 },
    [CTA_MARK]          = { .type = NLA_U32 },
    [CTA_SEQ_ADJ_ORIG]  = { .type = NLA_NESTED },
    [CTA_SEQ_ADJ_REPLY] = { .type = NLA_NESTED },
    [CTA_SYNPROXY]      = { .type = NLA_NESTED },
    [CTA_TUPLE_MASTER]  = { .type = NLA_NESTED },
    [CTA_ZONE]          = { .type = NLA_U16 },
    [CTA_MARK_MASK]     = { .type = NLA_U32 },
    [CTA_LABELS]        = { .type = NLA_BINARY,
                            .len = NF_CT_LABELS_MAX_SIZE },
    [CTA_LABELS_MASK]   = { .type = NLA_BINARY,
                            .len = NF_CT_LABELS_MAX_SIZE },
};
```

### 4.2 ctnetlink_create_conntrack()

**File:** `net/netfilter/nf_conntrack_netlink.c`, lines 2234-2390

Creates conntrack entries via netlink with:
- Tuple parsing (original and reply)
- Helper assignment
- NAT configuration
- Extension addition (acct, timestamp, ecache, labels, seqadj, synproxy)
- Timeout setting
- Hash table insertion

### 4.3 ctnetlink_del_conntrack()

**File:** `net/netfilter/nf_conntrack_netlink.c`, lines 1614-1665

Deletes conntrack entries by:
- Parsing zone
- Parsing tuple (original or reply direction)
- Looking up in hash table
- Calling `nf_ct_delete()`
- Reference counting cleanup

### 4.4 ctnetlink_dump_conntrack()

Dump implementation using netlink_dump_start with:
- `ctnetlink_start` - initialization
- `ctnetlink_dump_table` - per-entry dump
- `ctnetlink_done` - cleanup

### 4.5 Conntrack Zone Representation

**File:** `net/netfilter/nf_conntrack_netlink.c`, lines 1008-1013

```c
static int ctnetlink_parse_zone(const struct nlattr *attr,
                               struct nf_conntrack_zone *zone)
{
    if (!attr)
        zone->id = 0;
    else
        zone->id = ntohs(nla_get_be16(attr));
    zone->dir = NF_CT_DEFAULT_ZONE_DIR;
}
```

---

## 5. Routing Netlink (rtnetlink)

### 5.1 rtnl_lock() / rtnl_unlock()

**File:** `net/core/rtnetlink.c`, lines 78-158

```c
static DEFINE_MUTEX(rtnl_mutex);

void rtnl_lock(void)
{
    mutex_lock(&rtnl_mutex);
}

void __rtnl_unlock(void)
{
    struct sk_buff *head = defer_kfree_skb_list;
    defer_kfree_skb_list = NULL;
    WARN_ON(!list_empty(&net_todo_list));
    mutex_unlock(&rtnl_mutex);
    while (head) {
        struct sk_buff *next = head->next;
        kfree_skb(head);
        cond_resched();
        head = next;
    }
}

void rtnl_unlock(void)
{
    netdev_run_todo();
}
```

RTNL replaces the big kernel lock for network device operations.

### 5.2 struct ifinfomsg

**File:** `include/uapi/linux/if_link.h`

```c
struct ifinfomsg {
    unsigned char  ifi_family;  /* AF_UNSPEC or AF_BRIDGE */
    unsigned char  __ifi_pad;
    unsigned short ifi_type;    /* ARPHRD_* */
    int            ifi_index;   /* Interface index */
    unsigned int   ifi_flags;   /* IFF_* flags */
    unsigned int   ifi_change;  /* IFF_* change mask */
};
```

### 5.3 struct rtmsg

**File:** `include/uapi/linux/route.h`

```c
struct rtmsg {
    unsigned char  rtm_family;
    unsigned char  rtm_dst_len;   /* Destination prefix length */
    unsigned char  rtm_src_len;   /* Source prefix length */
    unsigned char  rtm_tos;       /* TOS filter */
    unsigned char  rtm_table;     /* Routing table ID */
    unsigned char  rtm_protocol;   /* Routing protocol */
    unsigned char  rtm_scope;     /* Routing scope */
    unsigned char  rtm_type;      /* Route type */
    unsigned int   rtm_flags;
};
```

### 5.4 rtnl_newlink()

**File:** `net/core/rtnetlink.c`, lines 3997-4119

Creates or modifies network interfaces:
1. Parses ifinfomsg and attributes
2. Looks up link kind and rtnl_link_ops
3. Calls `__rtnl_newlink()` for actual create/modify
4. Handles VRF, VLAN, bonding, etc. via linkinfo nested attributes

### 5.5 rtnl_dellink()

**File:** `net/core/rtnetlink.c`, lines 3556-3606

Deletes network interfaces by:
1. Parsing interface index or name
2. Calling `rtnl_delete_link()`
3. Handling group-level deletion

---

## 6. IPv6 Address Configuration (addrconf)

### 6.1 inet6_rtm_newaddr()

**File:** `net/ipv6/addrconf.c`, lines 4953-5091

Adds IPv6 addresses to interfaces:
1. Parses ifaddrmsg and IFA_* attributes
2. Extracts address prefix and peer address
3. Calls `inet6_addr_add()` under rtnl_net_lock

### 6.2 inet6_rtm_deladdr()

**File:** `net/ipv6/addrconf.c`, lines 4778-4809

Deletes IPv6 addresses by:
1. Parsing address prefix
2. Calling `inet6_addr_del()` under rtnl_net_lock

### 6.3 inet6_fill_ifaddr()

**File:** `net/ipv6/addrconf.c`, lines 5133-5209

Dumps IPv6 address information:
1. Calculates remaining lifetimes (preferred, valid)
2. Adds local and address attributes
3. Adds route priority and cacheinfo
4. Includes flags and protocol

### 6.4 addrconf_ifdown()

**File:** `net/ipv6/addrconf.c`, lines 3844-4016

Handles interface down events:
1. Disables IPv6 routing
2. Clears address hash table
3. Removes temporary addresses
4. Notifies and cleans up addresses
5. Destroys anycast and multicast addresses
6. Cleans up neighbour entries

---

## Summary

The Linux kernel Netlink implementation provides:

1. **Core Infrastructure**: Socket management, portid allocation, memory accounting, error reporting
2. **Generic Netlink**: Family registration, command dispatch, multicast group management
3. **Netfilter**: Subsystem registration, batched message processing, attribute parsing
4. **Conntrack**: Tuple-based conntrack creation/deletion, zone filtering, labels/marks
5. **Routing**: Device create/delete, link state, VF configuration for SR-IOV
6. **IPv6 addrconf**: Interface address lifecycle management, DAD, lifetime tracking

Key design patterns:
- RCU for lock-free reads where possible
- Per-subsystem mutexes for write serialization
- Memory charging for socket buffers
- Extended ACK for detailed error reporting
- Batch processing for efficiency
