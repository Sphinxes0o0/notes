Now I have a comprehensive understanding of the Linux kernel conntrack subsystem. Let me write the detailed analysis document.

Based on my thorough analysis of the Linux kernel conntrack subsystem source code, here is the comprehensive technical documentation:

# Linux Kernel Connection Tracking (Conntrack) Subsystem Analysis

## Table of Contents
1. [Core Conntrack Infrastructure](#1-core-conntrack-infrastructure)
2. [Conntrack Tuple](#2-conntrack-tuple)
3. [Connection States](#3-connection-states)
4. [Conntrack Zones](#4-conntrack-zones)
5. [NAT and Connection Tracking](#5-nat-and-connection-tracking)
6. [Conntrack Netlink Interface](#6-conntrack-netlink-interface)
7. [TCP Protocol Helper](#7-tcp-protocol-helper)
8. [UDP Protocol Helper](#8-udp-protocol-helper)
9. [Conntrack Expectations](#9-conntrack-expectations)
10. [Timeout and Cleanup](#10-timeout-and-cleanup)

---

## 1. Core Conntrack Infrastructure

### File: `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_core.c`

#### 1.1 `nf_conntrack_init_start()` (Line 2631)
**Purpose:** Early initialization of conntrack subsystem before network namespace setup.

**Key operations:**
- Initializes `nf_conntrack_generation` sequence counter with spinlock
- Initializes per-CPU conntrack locks array (`nf_conntrack_locks[]`) - 16 locks by default (line 2641-2642)
- Calculates hash table size based on available RAM (lines 2644-2663):
  - Default: `nr_pages * PAGE_SIZE / 16384` entries
  - Systems with >4GB RAM: 262144 buckets
  - Systems with >1GB RAM: 65536 buckets
  - Minimum: 1024 buckets
- Allocates conntrack hash table via `nf_ct_alloc_hashtable()` (line 2665)
- Sets `nf_conntrack_max` = `max_factor * htable_size` where max_factor defaults to 1 (line 2669)
- Creates kmem_cache for nf_conntrack objects with `SLAB_TYPESAFE_BY_RCU` flag (lines 2671-2674)
- Initializes expectation subsystem, helper subsystem, and protocol subsystems (lines 2678-2688)
- Starts garbage collection worker with initial delay of 1 second (line 2691)
- Registers BPF conntrack functionality (line 2693)

#### 1.2 `nf_conntrack_init_net()` (Line 2744)
**Purpose:** Per-network-namespace conntrack initialization.

**Key operations:**
- Sets `cnet->count` atomic to 0 (line 2751)
- Allocates per-CPU statistics via `alloc_percpu()` (line 2753)
- Initializes expectation pernet (line 2757)
- Initializes accounting, timestamp, event cache, and protocol pernet structures (lines 2761-2764)

#### 1.3 `nf_conntrack_hash_insert()` (Internal, Line 829)
**Purpose:** Inserts conntrack into hash table (both directions).

```c
static void __nf_conntrack_hash_insert(struct nf_conn *ct,
                                       unsigned int hash,
                                       unsigned int reply_hash)
{
    hlist_nulls_add_head_rcu(&ct->tuplehash[IP_CT_DIR_ORIGINAL].hnnode,
               &nf_conntrack_hash[hash]);
    hlist_nulls_add_head_rcu(&ct->tuplehash[IP_CT_DIR_REPLY].hnnode,
               &nf_conntrack_hash[reply_hash]);
}
```
Each conntrack is inserted TWICE - once for ORIGINAL direction, once for REPLY direction. This enables bidirectional lookups.

#### 1.4 `nf_conntrack_find_get()` (Line 803)
**Purpose:** Finds a conntrack entry by tuple and returns with reference held.

**Flow:**
1. Computes zone ID for ORIGINAL direction (line 807)
2. Calls `__nf_conntrack_find_get()` with raw hash (line 812)
3. If not found and zone differs for reply, tries reply direction (lines 818-821)
4. Releases RCU lock and returns (lines 823-824)

**Internal `__nf_conntrack_find_get()` (Line 774):**
1. Calls `____nf_conntrack_find()` to locate tuple hash (line 780)
2. If found, obtains reference via `refcount_inc_not_zero()` (line 786)
3. Re-validates tuple equality after refcount bump (line 790)
4. Returns NULL if tuple no longer matches or refcount failed

#### 1.5 `nf_ct_delete()` (Line 644)
**Purpose:** Marks conntrack as dying and removes from hash table.

**Flow:**
1. Sets `IPS_DYING_BIT` atomically (line 649)
2. Records stop timestamp if tracking enabled (lines 652-659)
3. Reports destroy event via netlink (line 661)
4. If event delivery fails, adds to event cache for retry (lines 661-673)
5. Calls `nf_ct_delete_from_lists()` which:
   - Destroys any helper state (line 624)
   - Calls `__nf_ct_delete_from_lists()` (line 627)
6. Decrements reference count (line 680)

#### 1.6 `__nf_conntrack_confirm()` (Line 1202)
**Purpose:** Confirms a conntrack (places it in hash table) after packet processing.

**Key steps:**
1. Only processes ORIGINAL direction packets (lines 1223-1224)
2. Double-locks the hash bucket pair using sequence count (lines 1229-1237)
3. Checks if already confirmed - returns NF_DROP if so (lines 1249-1253)
4. Validates extension area is still valid (lines 1256-1259)
5. Checks DYING flag (lines 1266-1269)
6. Scans for hash collisions in both directions (lines 1275-1295)
7. Updates timeout relative to confirmation time (line 1300)
8. Inserts into hash table via `__nf_conntrack_hash_insert()` (line 1308)
9. Sets IPS_CONFIRMED bit after insertion (line 1318)
10. Reports NEW or RELATE event (lines 1337-1338)

#### 1.7 Garbage Collection - `gc_worker()` (Line 1513)
**Purpose:** Periodic cleanup of expired conntrack entries.

**Algorithm:**
- Scans hash table buckets incrementally (lines 1525, 1619)
- Processes up to `GC_SCAN_EXPIRED_MAX` (64000) entries per run
- Uses adaptive interval based on average timeout (lines 1535-1536)
- For each entry:
  - If expired, calls `nf_ct_gc_expired()` which tries to kill (lines 1575-1578)
  - Computes next scan interval based on expiration delta (lines 1581-1583)
  - If table 95% full, attempts early drop of non-ASSURED connections (lines 1605-1608)
- Reschedules with adaptive delay (lines 1633-1648)

#### 1.8 `init_conntrack()` (Line 1758)
**Purpose:** Creates a new conntrack entry for unmatched packets.

**Flow:**
1. Inverts tuple to create reply tuple (line 1776)
2. Allocates conntrack via `__nf_conntrack_alloc()` (line 1780)
3. Adds synproxy extension if needed (line 1785)
4. Adds timeout extension from template (lines 1790-1794)
5. Adds accounting, timestamp, and labels extensions (lines 1796-1798)
6. Adds event cache extension (lines 1800-1809)
7. Checks for expecting connections (line 1813-1836):
   - If expectation found, sets IPS_EXPECTED_BIT
   - Copies helper, mark, secmark from master
8. If no expectation but template exists, assigns helper (line 1838)
9. Sets initial reference count to 1 (line 1851)
10. Returns tuple hash for the original direction (line 1859)

---

## 2. Conntrack Tuple

### File: `/Users/sphinx/github/linux/include/net/netfilter/nf_conntrack_tuple.h`

#### 2.1 `struct nf_conntrack_tuple` (Line 37)
```c
struct nf_conntrack_tuple {
    struct nf_conntrack_man src;  // Manipulatable source (addresses/ports)

    struct {
        union nf_inet_addr u3;    // Destination IP address
        union {
            __be16 all;
            struct { __be16 port; } tcp;
            struct { __be16 port; } udp;
            struct { u_int8_t type, code; } icmp;
            struct { __be16 port; } dccp;
            struct { __be16 port; } sctp;
            struct { __be16 key; } gre;
        } u;

        u_int8_t protonum;        // Protocol number (IPPROTO_*)
        struct { } __nfct_hash_offsetend;  // Hash calculation boundary
        u_int8_t dir;            // Direction (IP_CT_DIR_ORIGINAL or REPLY)
    } dst;
};
```

**Tuple hashing boundary:** `offsetofend(struct nf_conntrack_tuple, dst.__nfct_hash_offsetend)` - hash is computed only on source and fixed destination fields, NOT including direction.

#### 2.2 `struct nf_conntrack_tuple_mask` (Line 78)
```c
struct nf_conntrack_tuple_mask {
    struct {
        union nf_inet_addr u3;
        union nf_conntrack_man_proto u;
    } src;
};
```
Used for expectation matching with wildcards.

#### 2.3 `struct nf_conntrack_tuple_hash` (Line 122)
```c
struct nf_conntrack_tuple_hash {
    struct hlist_nulls_node hnnode;  // Hash chain linkage
    struct nf_conntrack_tuple tuple;  // The actual tuple
};
```

#### 2.4 Tuple Comparison Functions

**`nf_ct_tuple_equal()` (Line 143):**
```c
static inline bool nf_ct_tuple_equal(const struct nf_conntrack_tuple *t1,
                                     const struct nf_conntrack_tuple *t2)
{
    return __nf_ct_tuple_src_equal(t1, t2) &&
           __nf_ct_tuple_dst_equal(t1, t2);
}
```
Compares source (IP, port, l3num) and destination (IP, port, protonum).

**`nf_ct_tuple_src_equal()` (Line 127):**
Compares: `src.u3`, `src.u.all`, `src.l3num`

**`nf_ct_tuple_dst_equal()` (Line 135):**
Compares: `dst.u3`, `dst.u.all`, `dst.protonum`

**`nf_ct_tuple_mask_cmp()` (Line 182):**
Compares tuple against another tuple with mask - used for expectation matching.

#### 2.5 Tuple Hash Calculation

**`hash_conntrack_raw()` (Line 210, nf_conntrack_core.c):**
```c
static u32 hash_conntrack_raw(const struct nf_conntrack_tuple *tuple,
                              unsigned int zoneid,
                              const struct net *net)
{
    siphash_key_t key;
    get_random_once(&nf_conntrack_hash_rnd, sizeof(nf_conntrack_hash_rnd));
    key = nf_conntrack_hash_rnd;
    key.key[0] ^= zoneid;
    key.key[1] ^= net_hash_mix(net);
    return siphash((void *)tuple,
            offsetofend(struct nf_conntrack_tuple, dst.__nfct_hash_offsetend),
            &key);
}
```
Uses SipHash-2-4 with per-boot random key. Hash input includes zone ID and network namespace mix.

---

## 3. Connection States

### File: `/Users/sphinx/github/linux/include/uapi/linux/netfilter/nf_conntrack_common.h`

#### 3.1 `enum ip_conntrack_info` (Line 7)
```c
enum ip_conntrack_info {
    IP_CT_ESTABLISHED,      // Part of established connection
    IP_CT_RELATED,          // Related to existing connection or ICMP error
    IP_CT_NEW,              // New connection tracking entry
    IP_CT_IS_REPLY,         // Flag: >= this means reply direction
    IP_CT_ESTABLISHED_REPLY = IP_CT_ESTABLISHED + IP_CT_IS_REPLY,
    IP_CT_RELATED_REPLY = IP_CT_RELATED + IP_CT_IS_REPLY,
    IP_CT_NUMBER,
    IP_CT_UNTRACKED = 7,
};
```
Connection tracking info encodes both connection state AND direction. Direction is determined by `ctinfo % IP_CT_IS_REPLY`.

#### 3.2 `enum ip_conntrack_status` (Line 42)
**Status bits tracked in `nf_conn->status`:**

| Bit | Name | Description |
|-----|------|-------------|
| 0 | IPS_EXPECTED | Connection is expected by expectation |
| 1 | IPS_SEEN_REPLY | Seen packets in both directions |
| 2 | IPS_ASSURED | Connection is assured (seen reply, higher priority) |
| 3 | IPS_CONFIRMED | Entry is in hash table (packet left box) |
| 4 | IPS_SRC_NAT | Needs source NAT in original dir |
| 5 | IPS_DST_NAT | Needs destination NAT in original dir |
| 6 | IPS_SEQ_ADJUST | TCP sequence adjustment needed |
| 7 | IPS_SRC_NAT_DONE | Source NAT completed |
| 8 | IPS_DST_NAT_DONE | Destination NAT completed |
| 9 | IPS_DYING | Connection is dying (being deleted) |
| 10 | IPS_FIXED_TIMEOUT | Timeout is fixed, not adjustable |
| 11 | IPS_TEMPLATE | Template conntrack (for expectations) |
| 13 | IPS_HELPER | Helper explicitly attached |
| 14 | IPS_OFFLOAD | Offloaded to flow table |
| 15 | IPS_HW_OFFLOAD | Offloaded to hardware |

---

## 4. Conntrack Zones

### File: `/Users/sphinx/github/linux/include/linux/netfilter/nf_conntrack_zones_common.h`

#### 4.1 `struct nf_conntrack_zone` (Line 16)
```c
struct nf_conntrack_zone {
    u16 id;      // Zone identifier (0 = default)
    u8 flags;    // NF_CT_FLAG_MARK for mark-based zones
    u8 dir;      // Direction bits: NF_CT_ZONE_DIR_ORIG | NF_CT_ZONE_DIR_REPL
};
```

**Constants:**
- `NF_CT_DEFAULT_ZONE_ID` = 0
- `NF_CT_ZONE_DIR_ORIG` = (1 << IP_CT_DIR_ORIGINAL)
- `NF_CT_ZONE_DIR_REPL` = (1 << IP_CT_DIR_REPLY)
- `NF_CT_DEFAULT_ZONE_DIR` = (NF_CT_ZONE_DIR_ORIG | NF_CT_ZONE_DIR_REPL)
- `NF_CT_FLAG_MARK` = 1 (zone based on packet mark)

### File: `/Users/sphinx/github/linux/include/net/netfilter/nf_conntrack_zones.h`

#### 4.2 Zone Helper Functions

**`nf_ct_zone()` (Line 8):** Returns zone from conntrack.

**`nf_ct_zone_tmpl()` (Line 28):** Gets zone from template or skb mark if template has NF_CT_FLAG_MARK.

**`nf_ct_zone_id()` (Line 56):** Returns zone ID for a direction:
- If direction matches zone->dir, returns zone->id
- Otherwise returns NF_CT_DEFAULT_ZONE_ID (0)

**`nf_ct_zone_equal()` (Line 67):** Compares zones for two conntracks in a specific direction.

---

## 5. NAT and Connection Tracking

### File: `/Users/sphinx/github/linux/net/netfilter/nf_nat_core.c`

#### 5.1 `struct nf_nat_range2` (uapi/linux/netfilter/nf_nat.h)
```c
struct nf_nat_range2 {
    unsigned int flags;              // NF_NAT_RANGE_* flags
    union nf_inet_addr min_addr;    // Range start
    union nf_inet_addr max_addr;    // Range end
    union nf_conntrack_man_proto min_proto;  // Port range start
    union nf_conntrack_man_proto max_proto;  // Port range end
    union nf_conntrack_man_proto base_proto; // Base for port selection
};
```

**Range flags:**
- `NF_NAT_RANGE_MAP_IPS` - Remap IP addresses
- `NF_NAT_RANGE_PROTO_SPECIFIED` - Remap protocol (ports)
- `NF_NAT_RANGE_PROTO_RANDOM_ALL` - Full port randomization
- `NF_NAT_RANGE_PROTO_OFFSET` - Port offset from original
- `NF_NAT_RANGE_PERSISTENT` - Persistent NAT mapping

#### 5.2 `nf_nat_setup_info()` (Line 770)
**Purpose:** Sets up NAT for a connection.

**Flow:**
1. Rejects confirmed connections (line 779)
2. Inverts reply tuple to get current direction tuple (line 793)
3. Calls `get_unique_tuple()` to find available NAT binding (line 796)
4. If tuple changed:
   - Updates reply tuple in conntrack (line 802-803)
   - Sets IPS_SRC_NAT or IPS_DST_NAT bit (lines 806-809)
   - Adds sequence adjustment extension if needed (lines 811-813)
5. If source NAT, adds to by-source hash for consistent mapping (lines 816-827)
6. Sets IPS_SRC_NAT_DONE or IPS_DST_NAT_DONE (lines 830-833)

#### 5.3 `get_unique_tuple()` (Line 694)
**Purpose:** Finds a unique NAT tuple within the given range.

**Algorithm (three-step):**
1. **Step 1:** If source NAT and not full randomization, try original tuple first (lines 714-728)
2. **Step 2:** Select least-used IP/proto combination via `find_best_ips_proto()` (lines 730-732)
3. **Step 3:** Find unique protocol (port) tuple via `nf_nat_l4proto_unique_tuple()` (line 754)

#### 5.4 `nf_nat_packet()` (Line 866)
**Purpose:** Performs per-packet NAT manipulation.

**Flow:**
1. Determines NAT type from hook (line 871)
2. Inverts status bit for reply direction (lines 882-883)
3. If NAT bit is set, calls protocol-specific `nf_nat_manip_pkt()` (line 887)

#### 5.5 `hash_by_src()` (Line 151)
**Purpose:** Hash function for NAT by-source tracking.

```c
static unsigned int hash_by_src(const struct net *net,
                                const struct nf_conntrack_zone *zone,
                                const struct nf_conntrack_tuple *tuple)
{
    // ... combines: src address, net mix, protonum, zone ID
    return siphash(&combined, sizeof(combined), &nf_nat_hash_rnd);
}
```

#### 5.6 NAT Bysource Hash
The NAT bysource hash (`nf_nat_bysource`) enables:
- Consistent source NAT for related connections
- Finding existing mappings for new connections
- NAT helpers to locate original connection

---

## 6. Conntrack Netlink Interface

### File: `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_netlink.c`

#### 6.1 CTA (Conntrack Attributes) - `enum ctattr_type`

**Tuple attributes:**
- `CTA_TUPLE_ORIG` - Original direction tuple
- `CTA_TUPLE_REPLY` - Reply direction tuple
- `CTA_TUPLE_MASTER` - Master tuple (for expected connections)
- `CTA_TUPLE_IP` - L3 IP addresses nested
- `CTA_TUPLE_PROTO` - L4 protocol nested
- `CTA_TUPLE_ZONE` - Zone ID for this tuple

**Connection attributes:**
- `CTA_STATUS` - Connection status bits
- `CTA_PROTOINFO` - Protocol-specific info
- `CTA_TIMEOUT` - Current timeout value
- `CTA_MARK` - Connection mark
- `CTA_SECCTX` - Security context
- `CTA_HELP` - Helper info nested
- `CTA_NAT_SRC` - Source NAT configuration
- `CTA_NAT_DST` - Destination NAT configuration
- `CTA_ID` - Unique connection ID
- `CTA_USE` - Reference count
- `CTA_COUNTERS_ORIG` - Original direction packet/byte counts
- `CTA_COUNTERS_REPLY` - Reply direction packet/byte counts
- `CTA_TIMESTAMP_START` - Connection start time
- `CTA_TIMESTAMP_STOP` - Connection stop time
- `CTA_ZONE` - Connection zone
- `CTA_LABELS` - Connection labels
- `CTA_SYNPROXY` - Synproxy info

#### 6.2 `ctnetlink_create_conntrack()` (Line 2234)
**Purpose:** Creates a new conntrack entry from netlink attributes.

**Flow:**
1. Allocates conntrack via `nf_conntrack_alloc()` (line 2247)
2. Parses and attaches helper if CTA_HELP present (lines 2254-2301)
3. Sets up NAT if CTA_NAT_SRC/DST present (line 2303)
4. Adds extensions: accounting, timestamp, ecache, labels, seqadj, synproxy (lines 2307-2312)
5. Sets IPS_CONFIRMED (line 2315)
6. Sets timeout (line 2317-2318)
7. Sets status if CTA_STATUS present (line 2320-2324)
8. Sets sequence adjustment if present (lines 2326-2330)
9. Sets protocol info if CTA_PROTOINFO present (lines 2333-2337)
10. Sets synproxy if present (lines 2339-2343)
11. Sets mark if present (lines 2345-2348)
12. If CTA_TUPLE_MASTER present, links to master conntrack (lines 2351-2369)
13. Calls `nf_conntrack_hash_check_insert()` to add to table (line 2374)

#### 6.3 `ctnetlink_get_conntrack()` (Line 1667)
**Purpose:** Queries conntrack entries.

**Modes:**
- **DUMP mode:** Iterates all conntracks via `ctnetlink_dump_table()` (lines 1679-1687)
- **Single lookup:** Parses tuple, calls `nf_conntrack_find_get()`, returns single entry (lines 1690-1728)

#### 6.4 `ctnetlink_del_conntrack()` (Line 1614)
**Purpose:** Deletes conntrack entries.

**Flow:**
1. Parses zone (line 1625)
2. Parses tuple (lines 1629-1641)
3. If only tuple specified, does single deletion:
   - Finds via `nf_conntrack_find_get()` (line 1646)
   - Validates ID if CTA_ID provided (lines 1652-1659)
   - Calls `nf_ct_delete()` (line 1661)
4. If no tuple, flushes all entries matching filter via `ctnetlink_flush_conntrack()` (lines 1638-1640)

#### 6.5 `ctnetlink_conntrack_event()` (Line 744)
**Purpose:** Reports conntrack events to userspace listeners.

**Event types based on status changes:**
- `IPCT_NEW` / `IPCT_RELATED` -> `IPCTNL_MSG_CT_NEW` to `NFNLGRP_CONNTRACK_NEW`
- `IPCT_DESTROY` -> `IPCTNL_MSG_CT_DELETE` to `NFNLGRP_CONNTRACK_DESTROY`
- Others -> `IPCTNL_MSG_CT_NEW` to `NFNLGRP_CONNTRACK_UPDATE`

---

## 7. TCP Protocol Helper

### File: `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_proto_tcp.c`

#### 7.1 TCP Connection States (Line 37)
```c
static const char *const tcp_conntrack_names[] = {
    "NONE",       // 0: Initial state
    "SYN_SENT",   // 1: SYN sent, awaiting SYN+ACK
    "SYN_RECV",   // 2: SYN+ACK received
    "ESTABLISHED",// 3: ACK received, connection open
    "FIN_WAIT",   // 4: FIN received, closing
    "CLOSE_WAIT", // 5: ACK for FIN received
    "LAST_ACK",   // 6: FIN received, waiting last ACK
    "TIME_WAIT",  // 7: Connection closed, 2MSL wait
    "CLOSE",      // 8: RST received
    "SYN_SENT2",  // 9: SYN sent, simultaneous open
};
```

#### 7.2 TCP State Machine Matrix (Line 134)

**ORIGINAL Direction (packet -> server):**

| Current \ Packet | SYN | SYN+ACK | FIN | ACK | RST |
|-----------------|-----|---------|-----|-----|-----|
| NONE | SYN_SENT | IGNORE | INVALID | IGNORE | CLOSE |
| SYN_SENT | SYN_SENT (retrans) | IGNORE | INVALID | INVALID | CLOSE |
| SYN_RECV | IGNORE | SYN_RECV | FIN_WAIT | ESTABLISHED | CLOSE |
| ESTABLISHED | IGNORE | IGNORE | FIN_WAIT | ESTABLISHED | CLOSE |
| FIN_WAIT | LAST_ACK | IGNORE | FIN_WAIT | CLOSE_WAIT | CLOSE |
| CLOSE_WAIT | IGNORE | IGNORE | LAST_ACK | CLOSE_WAIT | CLOSE |
| LAST_ACK | IGNORE | IGNORE | LAST_ACK | TIME_WAIT | CLOSE |
| TIME_WAIT | SYN_SENT | IGNORE | CLOSE | TIME_WAIT | CLOSE |

**REPLY Direction (packet <- server):**

| Current \ Packet | SYN | SYN+ACK | FIN | ACK | RST |
|-----------------|-----|---------|-----|-----|-----|
| NONE | IGNORE | IGNORE | INVALID | INVALID | CLOSE |
| SYN_SENT | SYN_SENT2 | SYN_RECV | INVALID | IGNORE | CLOSE |
| SYN_RECV | IGNORE | IGNORE | FIN_WAIT | ESTABLISHED | CLOSE |
| ESTABLISHED | IGNORE | IGNORE | FIN_WAIT | ESTABLISHED | CLOSE |
| FIN_WAIT | IGNORE | IGNORE | LAST_ACK | CLOSE_WAIT | CLOSE |
| CLOSE_WAIT | IGNORE | IGNORE | LAST_ACK | CLOSE_WAIT | CLOSE |
| LAST_ACK | IGNORE | IGNORE | LAST_ACK | TIME_WAIT | CLOSE |
| TIME_WAIT | SYN_SENT | IGNORE | CLOSE | TIME_WAIT | CLOSE |

#### 7.3 TCP Timeout Values (Line 61)
```c
static const unsigned int tcp_timeouts[TCP_CONNTRACK_TIMEOUT_MAX] = {
    [TCP_CONNTRACK_SYN_SENT]    = 2 * 60 * HZ,     // 2 minutes
    [TCP_CONNTRACK_SYN_RECV]    = 60 * HZ,          // 60 seconds
    [TCP_CONNTRACK_ESTABLISHED]  = 5 * 24 * 60 * 60 * HZ, // 5 days
    [TCP_CONNTRACK_FIN_WAIT]   = 2 * 60 * HZ,      // 2 minutes
    [TCP_CONNTRACK_CLOSE_WAIT]   = 60 * HZ,          // 60 seconds
    [TCP_CONNTRACK_LAST_ACK]    = 30 * HZ,          // 30 seconds
    [TCP_CONNTRACK_TIME_WAIT]   = 2 * 60 * HZ,     // 2 minutes
    [TCP_CONNTRACK_CLOSE]       = 10 * HZ,          // 10 seconds
    [TCP_CONNTRACK_SYN_SENT2]   = 2 * 60 * HZ,     // 2 minutes
    [TCP_CONNTRACK_RETRANS]     = 5 * 60 * HZ,     // 5 minutes
    [TCP_CONNTRACK_UNACK]       = 5 * 60 * HZ,     // 5 minutes
};
```

#### 7.4 TCP Window Tracking (Line 455)

The TCP conntrack maintains state for both directions:

```c
struct ip_ct_tcp_state {
    u_int32_t td_end;      // Max of (seq + len)
    u_int32_t td_maxend;   // Max of (ack + max(win, 1))
    u_int32_t td_maxwin;   // Max window seen
    u_int32_t td_maxack;   // Max ack seen
    u_int8_t td_scale;     // Window scale factor
    u_int8_t flags;        // Options (SACK_PERM, WINDOW_SCALE, etc.)
};

struct ip_ct_tcp {
    struct ip_ct_tcp_state seen[2];  // Per direction
    u_int8_t state;                  // TCP_CONNTRACK_* state
    u_int8_t last_dir;               // Direction of last packet
    u_int8_t retrans;                // Retransmit count
    u_int8_t last_index;            // Last packet flags index
    u32 last_seq, last_ack;          // Last seq/ack values
    u32 last_end;                    // Last seq + len
    u16 last_win;                    // Last window
    u8 last_wscale, last_flags;      // For SYN tracking
};
```

**Validation bounds (from RFC 5937):**
- Upper data bound: `seq <= sender.td_maxend`
- Lower data bound: `seq + len >= sender.td_end - receiver.td_maxwin`
- Upper ACK bound: `sack <= receiver.td_end`
- Lower ACK bound: `sack >= receiver.td_end - MAXACKWINDOW`

#### 7.5 TCP Loose Tracking (`tcp_loose`) (Line 869)
When `tcp_loose=1` (default), conntrack can pick up existing connections that weren't tracked before. When `tcp_loose=0`, only strictly valid handshakes create connections.

#### 7.6 `tcp_in_window()` (Line 509)
Validates TCP packet sequence numbers against connection tracking state.

**Checks performed:**
1. Initialize sender state on first SYN (line 540-575)
2. Handle retransmitted SYN (line 576-594)
3. Validate sequence number bounds (lines 617-650)
4. Validate ACK number bounds (lines 652-655)
5. Check receive window (lines 657-667)
6. Update sender/receiver state (lines 673-698)
7. Detect retransmissions (lines 701-717)

---

## 8. UDP Protocol Helper

### File: `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_proto_udp.c`

#### 8.1 UDP States (Line 27)
```c
static const unsigned int udp_timeouts[UDP_CT_MAX] = {
    [UDP_CT_UNREPLIED] = 30 * HZ,   // 30 seconds - no reply seen
    [UDP_CT_REPLIED]   = 120 * HZ,  // 2 minutes - reply seen
};
```

#### 8.2 UDP State Tracking (Line 84)

UDP is connectionless, but conntrack tracks bidirectional communication:

**State Machine:**
- **UNREPLIED:** First packet seen, no reply yet
- **REPLIED:** Packets seen in both directions (becomes ASSURED)

**Logic:**
```c
if (status & IPS_SEEN_REPLY) {
    // After 2 seconds without stream_ts, use REPLIED timeout
    if (time_after(jiffies, ct->proto.udp.stream_ts)) {
        extra = timeouts[UDP_CT_REPLIED];
        stream = (status & IPS_ASSURED) == 0;  // Mark ASSURED if first stream
    }
    nf_ct_refresh_acct(ct, ctinfo, skb, extra);
    if (stream)
        set_bit(IPS_ASSURED_BIT, &ct->status);
} else {
    nf_ct_refresh_acct(ct, ctinfo, skb, timeouts[UDP_CT_UNREPLIED]);
}
```

---

## 9. Conntrack Expectations

### File: `/Users/sphinx/github/linux/net/netfilter/nf_conntrack_expect.c`

#### 9.1 `struct nf_conntrack_expect` (not fully shown, defined in header)
```c
struct nf_conntrack_expect {
    atomic_t use;                  // Reference count
    struct nf_conntrack_tuple tuple;      // Expected tuple
    struct nf_conntrack_tuple_mask mask;   // Wildcard mask
    struct nf_conntrack_helper *helper;    // Helper for this expectation
    struct nf_conn *master;               // Master connection
    struct net *net;                       // Network namespace
    struct nf_conntrack_zone zone;         // Zone
    unsigned int class;                   // Expectation class
    u_int8_t flags;                       // Flags
    struct timer_list timeout;             // Expiration timer
    struct rcu_head rcu;                  // RCU cleanup
    struct hlist_node lnode;              // Master's expectations list
    struct hlist_node hnode;              // Global expectation hash
    // NAT-related fields
    union nf_inet_addr saved_addr;
    union nf_conntrack_man_proto saved_proto;
    // Expectation function
    void (*expectfn)(struct nf_conn *new, struct nf_conntrack_expect *exp);
};
```

**Flags:**
- `NF_CT_EXPECT_PERMANENT` - Never expires
- `NF_CT_EXPECT_INACTIVE` - Inactive, don't match
- `NF_CT_EXPECT_USERSPACE` - Userspace expectation

#### 9.2 Expectation Hash (Line 35)
```c
unsigned int nf_ct_expect_hsize;  // Expectation hash size
struct hlist_head *nf_ct_expect_hash;  // Expectation hash table
```
Hash function: `nf_ct_expect_dst_hash()` (Line 83) - hashes by destination (tuple dst, protonum, net namespace).

#### 9.3 `nf_ct_expect_find_get()` (Line 154)
Finds expectation by tuple:
1. Computes destination hash (line 145)
2. Walks hash chain looking for matching expectation (lines 146-149)
3. Increments reference count if found (line 164)

#### 9.4 `nf_ct_find_expectation()` (Line 174)
Finds and consumes expectation when a matching packet arrives:
1. Looks up in hash (lines 188-195)
2. Skips inactive expectations (line 190)
3. Verifies master is confirmed (line 204)
4. Gets reference on master (lines 215-217)
5. If permanent or not unlinking, increments refcount (line 219-221)
6. Otherwise, deletes timer and unlinks (line 222-224)

#### 9.5 `nf_ct_expect_insert()` (Line 407)
Inserts new expectation:
1. Sets refcount to 2 (one for hash, one for timer) (line 416)
2. Sets up timeout timer with helper's policy or default (lines 418-425)
3. Adds to master's expectations list (line 427)
4. Adds to global expectation hash (line 430)
5. Increments expectation count (line 432)

#### 9.6 Expectation Matching

**`nf_ct_exp_equal()` (Line 110):**
```c
return nf_ct_tuple_mask_cmp(tuple, &i->tuple, &i->mask) &&
       net_eq(net, read_pnet(&i->net)) &&
       nf_ct_exp_zone_equal_any(i, zone);
```
Matches if: tuple matches expectation WITH mask applied, same namespace, same zone.

#### 9.7 Helper Expectations
Helpers like FTP, IRC DCC create expectations for related data connections:
- **FTP:** Expects inbound TCP connection to port 20 or high port
- **IRC DCC:** Expects inbound TCP connection for file transfer
- **TFTP:** Expects inbound UDP connection for data transfer

---

## 10. Timeout and Cleanup

### 10.1 Timeout System

**`nf_ct_expires()` (Line 293, nf_conntrack.h):**
```c
static inline unsigned long nf_ct_expires(const struct nf_conn *ct)
{
    s32 timeout = READ_ONCE(ct->timeout) - nfct_time_stamp;
    return max(timeout, 0);
}
```
Returns jiffies until expiration, 0 if already expired.

**`nf_ct_is_expired()` (Line 300):**
```c
static inline bool nf_ct_is_expired(const struct nf_conn *ct)
{
    return (__s32)(READ_ONCE(ct->timeout) - nfct_time_stamp) <= 0;
}
```

**`__nf_ct_refresh_acct()` (Line 2097, nf_conntrack_core.c):**
Updates timeout and does accounting:
1. Skips update if IPS_FIXED_TIMEOUT set (line 2103)
2. Adds current time stamp to relative timeout (line 2108)
3. Updates ct->timeout (line 2111)
4. Updates accounting counters (line 2114)

### 10.2 Cleanup System

**`nf_conntrack_cleanup_start()` (Line 2456):**
- Cleans up BPF resources
- Sets GC work exiting flag

**`nf_conntrack_cleanup_end()` (Line 2462):**
1. Cancels GC work (line 2665)
2. Frees hash table (line 2666)
3. Destroys protocol subsystems (lines 2668-2670)
4. Destroys kmem_cache (line 2672)

**`nf_conntrack_cleanup_net()` (Line 2479):**
Per-network-namespace cleanup for netns exit.

**`nf_ct_iterate_destroy()` (Line 2408):**
Destroys all conntracks during module exit:
1. Drops nf_hook for all netns (lines 2414-2420)
2. Waits for netns cleanup workers (line 2428)
3. Bumps extension generation ID (line 2437)
4. Iterates and deletes all entries (line 2439)
5. Waits for RCU (line 2447)

**`gc_worker()` Garbage Collection (Line 1513):**
- Scans hash table buckets
- Removes expired entries
- Early-drop when table is 95% full (priority: non-ASSURED, then ASSURED with `can_early_drop` returning true)

---

## Packet Flow Through Conntrack

### Ingress Path (via `nf_conntrack_in()` - Line 2010):

```
1. nf_ct_get(skb, &ctinfo)     -> Check if skb already has conntrack
2. If existing non-template   -> Return NF_ACCEPT (already tracked)
3. get_l4proto()               -> Extract L4 protocol from IP header
4. If ICMP/ICMPv6              -> Handle error messages specially
5. resolve_normal_ct()         -> Main lookup/creation:
   a. Build tuple from packet
   b. Try ORIGINAL direction lookup
   c. Try REPLY direction lookup
   d. If not found, create new via init_conntrack()
   e. Set ctinfo: NEW, RELATED, or ESTABLISHED
6. nf_conntrack_handle_packet() -> Protocol-specific processing:
   - TCP: tcp_packet() - state transition
   - UDP: udp_packet() - update timeouts
   - ICMP: icmp_packet() - handle error/reply
7. If ESTABLISHED and first reply -> Set IPS_SEEN_REPLY_BIT
8. __nf_conntrack_confirm()     -> Add to hash table (on first packet out)
9. Return verdict (NF_ACCEPT/NF_DROP)
```

### Key Data Structures Summary

| Structure | Purpose | Location |
|-----------|---------|----------|
| `nf_conn` | Full connection tracking entry | nf_conntrack.h:74 |
| `nf_conntrack_tuple` | Uniquely identifies a flow | nf_conntrack_tuple.h:37 |
| `nf_conntrack_tuple_hash` | Hash table entry with tuple | nf_conntrack_tuple.h:122 |
| `nf_conntrack_zone` | Isolation zone | nf_conntrack_zones_common.h:16 |
| `ip_ct_tcp` | TCP protocol state | nf_conntrack_tcp.h:17 |
| `nf_conntrack_expect` | Expected related connection | nf_conntrack_expect.h |
| `nf_nat_range2` | NAT address/port range | nf_nat.h |

---

## Hash Table Architecture

**Dual-hash insertion:** Each conntrack occupies TWO hash slots:
- Original direction tuple -> Original bucket
- Reply direction tuple -> Reply bucket

This enables:
1. O(1) lookup in either direction
2. Bidirectional state tracking
3. Efficient reply detection

**Locking strategy:** Uses 16 per-CPU spinlocks (`nf_conntrack_locks[]`) with a global "all locked" mode for hash resizing. Sequence counts detect concurrent resize operations.

---

This comprehensive analysis covers the Linux kernel conntrack subsystem's core components, data structures, state machines, and packet processing flows.