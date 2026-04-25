# Linux Kernel Networking Advanced Features Analysis

## Table of Contents

1. [GRO (Generic Receive Offload)](#1-gro-generic-receive-offload)
2. [GSO (Generic Segmentation Offload)](#2-gso-generic-segmentation-offload)
3. [Packet Timestamping](#3-packet-timestamping)
4. [cgroup_netprio (Priority Classification)](#4-cgroup_netprio-priority-classification)
5. [Network Namespace (netns)](#5-network-namespace-netns)
6. [Traffic Control (qdisc)](#6-traffic-control-qdisc)

---

## 1. GRO (Generic Receive Offload)

### Location: `net/core/gro.c` and `include/net/gro.h`

### 1.1 Core Functions

#### napi_gro_receive() / napi_gro_frags()

- **File**: `net/core/gro.c`
- `napi_gro_frags()` (line 763-774): Handles GRO for fragment-based packets, calls `napi_frags_skb()` to set up the SKB layout, then `dev_gro_receive()` for actual GRO processing.
- Entry points for NIC driver GRO receive paths.

#### struct napi_gro_cb - GRO Control Block

- **File**: `include/net/gro.h` (lines 17-98)
- Embedded in `skb->cb` (28 bytes total)
- Key fields:
  - `frag0` / `frag0_len` (lines 20-24): Virtual address and length of first fragment
  - `last` / `age` (lines 29-33): Used in slow path merge - pointer to last skb and jiffies when first packet was queued
  - `data_offset` (line 37): Current processing offset relative to skb->data
  - `flush` (line 40): Non-zero if packet cannot be merged
  - `count` (line 43): Number of segments aggregated
  - `proto` (line 46): Protocol type for GRO
  - `same_flow` (line 60): Whether packet may be of same flow
  - `csum_valid` / `csum_cnt` (lines 66-69): Checksum state tracking
  - `free` (line 72): Whether to free SKB (NAPI_GRO_FREE or NAPI_GRO_FREE_STOLEN_HEAD)
  - `recursion_counter` (line 81): GRO receive callback recursion depth

#### skb_gro_receive() - SKB Merging

- **File**: `net/core/gro.c` (lines 92-223)
- Handles merging of packets into aggregated flows
- Two merge paths:
  1. **Fast path** (frag_list): When `headlen <= offset`, merges page fragments directly (lines 126-157)
  2. **Slow path** (lines 186-222): Full SKB merge via `skb_list` chaining when head doesn't have enough space
- Validates:
  - `p->pp_recycle` must match (line 109) - page pool compatibility
  - Combined length must not exceed `netif_get_gro_max_size()` (line 112)
  - Legacy GRO max size check (lines 116-120)
- Updates `NAPI_GRO_CB(p)->count`, `p->data_len`, `p->truesize`, `p->len`

#### TCP GRO: tcp4_gro_receive() / tcp6_gro_receive()

- **File**: `net/ipv4/tcp_offload.c` (lines 419-440) and `net/ipv6/tcpv6_offload.c`
- `tcp4_gro_receive()` (line 419): Entry point for TCPv4 GRO
- `tcp_gro_receive()` (lines 286-367 in tcp_offload.c): Core TCP merging logic
  - Validates TCP flags, sequence numbers, ACK sequence
  - Checks `mss` compatibility with `gso_size`
  - Uses `gro_receive_network_flush()` to check IP-level header changes
  - Handles fragmentation list (fraglist) GRO (lines 330-341)
- `tcp_gro_complete()` (lines 369-386): Sets up GSO segments, checksum offsets
- `tcp4_gro_complete()` (lines 442-466): IPv4-specific completion, sets gso_type including SKB_GSO_TCPV4

#### UDP GRO: udp4_gro_receive() / udp6_gro_receive()

- **File**: `net/ipv4/udp_offload.c` (lines 877-906)
- `udp4_gro_receive()` (line 877): Validates UDP checksum, calls `udp_gro_receive()`
- `udp_gro_complete_segment()` (lines 908-923): Sets up UDP GSO segments with `SKB_GSO_UDP_L4` type
- Supports UDP tunnel offloads with `SKB_GSO_UDP_TUNNEL_CSUM` and `SKB_GSO_UDP_TUNNEL`

#### Flow Dissection in GRO - skb_flow_dissect()

- **File**: `net/core/flow_dissector.c` (lines 1057-onwards)
- `__skb_flow_dissect()` (line 1057): Main dissection function
- Extracts flow keys from packet headers for flow classification
- Supports protocols: IPv4/IPv6, TCP, UDP, ICMP, SCTP, GRE, MPLS, ARP, CFM, Batman, etc.
- Used in GRO to determine if packets can be merged (`gro_list_prepare()` in `net/core/gro.c` lines 343-385)

#### GRO Flush - napi_gro_flush()

- **File**: `include/net/gro.h` (lines 513-516)
- `napi_gro_flush()`: Inline wrapper around `gro_flush()` (line 505-511)
- `gro_flush()` (line 505): Checks bitmask, calls `__gro_flush()`
- `__gro_flush()` (lines 312-323 in gro.c): Iterates through hash buckets, completes SKBs in reverse age order
- `__gro_flush_chain()` (lines 290-305): Completes SKBs in a single chain, clears bitmask if empty

---

## 2. GSO (Generic Segmentation Offload)

### Location: `net/core/dev.c` and `net/core/gso.c`

### 2.1 dev_hard_start_xmit() - GSO Handling

- **File**: `net/core/dev.c` (lines 3894-3920)
- Main entry point for transmitting packets
- Iterates through SKB list (GSO can produce multiple segments)
- Calls `xmit_one()` for each segment
- Handles return of unsent packets via `skb->next` linking

### 2.2 skb_is_gso() - GSO SKB Detection

- **File**: `include/linux/skbuff.h` (line 5239-5242)
- Simple check: `return skb_shinfo(skb)->gso_size;`
- Non-zero `gso_size` indicates GSO packet
- Related helpers:
  - `skb_is_gso_v6()` (line 5245): Checks `SKB_GSO_TCPV6`
  - `skb_is_gso_sctp()` (line 5251): Checks `SKB_GSO_SCTP`
  - `skb_is_gso_tcp()` (line 5257): Checks `SKB_GSO_TCPV4 | SKB_GSO_TCPV6`

### 2.3 skb_gso_segment() - Segmenting GSO SKB

- **File**: `net/core/gso.c` (lines 88-131)
- `__skb_gso_segment()` (line 88): Main segmentation function
- `skb_needs_check()` (line 66): Determines if checksum verification needed
  - TX path: returns true if `ip_summed != CHECKSUM_PARTIAL && ip_summed != CHECKSUM_UNNECESSARY`
  - RX path: returns true if `ip_summed == CHECKSUM_NONE`
- Handles GSO partial features (lines 106-113): `NETIF_F_GSO_PARTIAL` support
- Calls `skb_mac_gso_segment()` (line 124) for actual protocol segmentation
- `skb_mac_gso_segment()` (lines 37-62 in gso.c): MAC layer segmentation, dispatches to protocol-specific handlers (TCPv4, TCPv6, SCTP, UDP, etc.)

### 2.4 UDP GSO - gso_size Works

- **File**: `include/linux/skbuff.h` and `net/ipv4/udp_offload.c`
- UDP GSO sets `gso_size` to maximum datagram payload size
- `SKB_GSO_UDP_L4` (line in `skb_shared_info::gso_type`): Indicates UDP GSO
- UDP segmentation creates multiple datagrams, each with `gso_size` payload
- Tunnel UDP GSO: `SKB_GSO_UDP_TUNNEL_CSUM` / `SKB_GSO_UDP_TUNNEL` for encapsulation
- `udp_gro_complete_segment()` (lines 908-923): Sets `gso_segs` count and `gso_type`

### 2.5 skb_gso_validate_mac_header() - GSO Header Validation

- **File**: `net/core/gso.c` (lines 259-272)
- `skb_gso_validate_mac_len()` (line 268): Validates MAC header length
- `skb_gso_validate_network_len()` (line 253): Validates network layer (L3) length
- `skb_gso_size_check()` (line 223): Core validation logic, handles `GSO_BY_FRAGS` case

---

## 3. Packet Timestamping

### Location: `net/core/timestamping.c` and `net/core/skbuff.c`

### 3.1 SO_TIMESTAMPING

- **File**: `include/uapi/linux/errqueue.h` (lines 46-77)
- `struct scm_timestamping` (lines 56-62): User-visible timestamp structure
  - `ts[3]`: Array of 3 timestamps (typically Software, Hardware HW->TX, Hardware HW->RX)
- `struct scm_timestamping64` (lines 64-66): 64-bit timestamp version
- Timestamp types (enum, lines 72-77):
  - `SCM_TSTAMP_SND`: Sender timestamp (driver/NIC or software)
  - `SCM_TSTAMP_SCHED`: Scheduled time (entered packet scheduler)
  - `SCM_TSTAMP_ACK`: ACK received from peer
  - `SCM_TSTAMP_COMPLETION`: TX completion

### 3.2 skb_tstamp_tx() - TX Timestamp

- **File**: `net/core/skbuff.c` (lines 5686-5748)
- `__skb_tstamp_tx()` (lines 5686-5748): Core TX timestamping function
  - Clones the original SKB for error queue delivery
  - Handles software timestamps, hardware timestamps, or both
  - Respects `SO_TIMESTAMPING_OPT_TSONLY` flag
  - Supports BPF timestamping (`SKBTX_BPF`)
  - Handles TCP timestamp option stats
- `skb_tstamp_tx()` (lines 5750-5756): Wrapper around `__skb_tstamp_tx()`
- `skb_tx_timestamp()` (lines 4720-4725 in skbuff.h): Driver hook for transmit timestamping

### 3.3 __net_timestamp() - Software Timestamp

- **File**: `include/linux/skbuff.h` (line 4421)
- `__net_timestamp()`: Sets `skb->tstamp` to current time (`ktime_get_real_ts()`)

### 3.4 Hardware Timestamping with SKBTX_HW_TSTAMP

- **File**: `net/core/timestamping.c` (lines 23-64)
- `skb_clone_tx_timestamp()` (lines 23-64): Clones SKB and requests hardware timestamp from PHY
  - Uses `mii_ts->txtstamp()` callback for hardware timestamping
  - Validates PHY device and classification via `ptp_classify_raw()`
- `skb_defer_rx_timestamp()` (lines 67-113): Handles receive-side hardware timestamp deferral

---

## 4. cgroup_netprio (Priority Classification)

### Location: `net/core/netprio_cgroup.c`

### 4.1 skb_update_prio() - Setting Packet Priority from cgroup

- **File**: `net/core/dev.c` (lines 4299-4322)
- Called during packet transmission to set `skb->priority` based on cgroup
- `skb_update_prio()` (line 4300):
  - Returns early if `skb->priority` already set
  - Gets `netprio_map` from device (line 4308)
  - Extracts socket's cgroup priority index via `sock_cgroup_prioidx()` (line 4315)
  - Maps `prioidx` to actual priority using `map->priomap[prioidx]` (line 4318)

### 4.2 sock_cgroup_prioidx()

- **File**: `include/linux/cgroup-defs.h` (lines 934-941)
- Returns `skcd->prioidx` for `CONFIG_CGROUP_NET_PRIO` enabled
- Default return value is 1 when disabled

### 4.3 netprio_prio() / netprio_set_prio()

- **File**: `net/core/netprio_cgroup.c` (lines 93-131)
- `netprio_prio()` (lines 93-101): Returns effective netprio for cgroup-device pair
- `netprio_set_prio()` (lines 112-131): Sets priority, extends priomap if needed
- `extend_netdev_table()` (lines 41-84): Dynamically expands device priomap

---

## 5. Network Namespace (netns)

### Location: `net/core/net_namespace.c` and `include/net/net_namespace.h`

### 5.1 struct net - Network Namespace Structure

- **File**: `include/net/net_namespace.h` (lines 62-200+)
- Core fields:
  - `refcount_t passive` (line 66): Reference counting
  - `struct list_head list` (line 77): Global namespace list
  - `unsigned int dev_base_seq` (line 71): Device list version
  - `u32 ifindex` (line 72): Unique interface index
  - `struct net_device *loopback_dev` (line 126): Loopback device reference
  - `struct sock *rtnl` (line 110): rtnetlink socket

- Per-subsystem containers (lines 131-196):
  - `struct netns_core core`: Core network settings
  - `struct netns_ipv4 ipv4`: IPv4 stack state
  - `struct netns_ipv6 ipv6`: IPv6 stack state
  - `struct netns_ct ct`: Connection tracking
  - `struct netns_nf nf`: Netfilter
  - `struct netns_xfrm xfrm`: IPsec
  - `struct netns_bpf bpf`: BPF state

### 5.2 Network Namespace Isolation

- **File**: `net/core/net_namespace.c`
- `setup_net()` (lines 436-465): Initializes new namespace
  - Calls `ops_init()` for each registered pernet subsystem
  - Adds to `net_namespace_list`
- `copy_net_ns()` (lines 549-596): Creates new namespace via `CLONE_NEWNET`
- `cleanup_net()` (lines 662-725): Cleanup workqueue function
  - Removes from namespace list
  - Calls `ops_exit_list()` for each subsystem
- `register_pernet_subsys()` (lines 1432-1440): Registers subsystem with init/exit callbacks

### 5.3 Namespace Isolation Mechanisms

- Routing table (`ipv4`, `ipv6`): Separate FIB tables per namespace
- Connection tracking (`ct`): Per-namespace conntrack tables
- Netfilter (`nf`): Per-namespace netfilter hooks and tables
- Network devices (`dev_by_index`): Per-namespace device index
- Socket lookup: `__inet_lookup()`, `__inet6_lookup()` search within namespace

---

## 6. Traffic Control (qdisc)

### Location: `net/sched/sch_generic.c` and `include/net/sch_generic.h`

### 6.1 struct Qdisc - Qdisc Structure

- **File**: `include/net/sch_generic.h` (lines 66-139)
- Core fields:
  - `enqueue()` / `dequeue()` / `peek()` function pointers (lines 67-70)
  - `flags` (line 71): TCQ_F_BUILTIN, TCQ_F_CAN_BYPASS, TCQ_F_NOLOCK, TCQ_F_OFFLOADED, etc.
  - `u32 limit` (line 93): Queue length limit
  - `const struct Qdisc_ops *ops` (line 94): Qdisc operations
  - `struct netdev_queue *dev_queue` (line 100): Associated device queue
  - `struct sk_buff_head gso_skb` (line 110): GSO/TSO requeue buffer
  - `struct sk_buff_head skb_bad_txq` (line 112): Bad TX queue for driver flow control
  - `struct qdisc_skb_head q` (line 117): Main packet queue

### 6.2 struct Qdisc_ops

- **File**: `include/net/sch_generic.h` (lines 304-340)
- Defines qdisc type operations:
  - `enqueue()` / `dequeue()` / `peek()` (lines 311-315)
  - `init()` / `reset()` / `destroy()` lifecycle (lines 317-320)
  - `change()` / `dump()` / `change_tx_queue_len()` (lines 321-330)
  - `owner` (line 339): Module reference

### 6.3 pfifo_fast - Default qdisc

- **File**: `net/sched/sch_generic.c` (lines 716-931)
- `pfifo_fast_priv` structure (lines 722-724): Contains 3 `skb_array` rings for priority bands
- `sch_default_prio2band[]` (lines 707-710): Maps `skb->priority` to band (0-2)
- `pfifo_fast_enqueue()` (lines 732-754): Enqueues based on priority band
- `pfifo_fast_dequeue()` (lines 756-795): Dequeues from highest priority non-empty band

### 6.4 qdisc_run() - Qdisc Processing

- **File**: `net/sched/sch_generic.c` (lines 415-431)
- `__qdisc_run()` (line 415): Main processing loop
  - Uses `quota = net_hotdata.dev_tx_weight` as budget
  - Calls `qdisc_restart()` until quota exhausted or queue empty
  - Sets `__QDISC_STATE_MISSED` if quota exceeded (for NOLOCK qdiscs)
  - Calls `__netif_schedule()` for re-scheduling
- `qdisc_restart()` (lines 393-413): Dequeues packet and calls `sch_direct_xmit()`

### 6.5 sch_direct_xmit() - Direct Transmission

- **File**: `net/sched/sch_generic.c` (lines 319-372)
- `sch_direct_xmit()` (line 319): Handles direct packet transmission
  - Validates GSO/checksum via `validate_xmit_skb_list()` (line 332)
  - Acquires `HARD_TX_LOCK` for device TX lock
  - Calls `dev_hard_start_xmit()` (line 347)
  - Requeues on `NETDEV_TX_BUSY` via `dev_requeue_skb()` (line 367)

### 6.6 skb_needs_check() - GSO/TSO Validation

- **File**: `net/core/gso.c` (lines 66-73)
- Returns true if checksum must be computed:
  - TX path: `ip_summed != CHECKSUM_PARTIAL && ip_summed != CHECKSUM_UNNECESSARY`
  - RX path: `ip_summed == CHECKSUM_NONE`
- Used in `__skb_gso_segment()` (line 93) to trigger `skb_warn_bad_offload()` on error

---

## Key Data Structures Summary

| Structure | File | Purpose |
|-----------|------|---------|
| `struct napi_gro_cb` | `include/net/gro.h:17-98` | GRO per-packet state |
| `struct Qdisc` | `include/net/sch_generic.h:66-139` | Packet scheduler descriptor |
| `struct Qdisc_ops` | `include/net/sch_generic.h:304-340` | Qdisc operation vectors |
| `struct net` | `include/net/net_namespace.h:62+` | Network namespace |
| `struct scm_timestamping` | `include/uapi/linux/errqueue.h:56-66` | Timestamp CMSG structure |

---

## Key Code Paths

### GRO Receive Path:
1. Driver calls `napi_gro_receive()` or `napi_gro_frags()`
2. `dev_gro_receive()` hashes by flow, calls protocol GRO handler
3. Protocol handler (e.g., `tcp4_gro_receive()`) merges or flushes
4. `gro_complete()` or `napi_frags_finish()` completes aggregation

### GSO Transmit Path:
1. `__dev_queue_xmit()` or `__dev_direct_xmit()` called
2. `validate_xmit_skb_list()` validates GSO/checksum
3. `sch_direct_xmit()` calls `dev_hard_start_xmit()`
4. `skb_gso_segment()` or driver segmentation splits packet
5. Each segment transmitted via `netdev_start_xmit()`

---

## References by Line Number

| Component | File | Key Lines |
|-----------|------|-----------|
| GRO core | `net/core/gro.c` | 92-223 (skb_gro_receive), 462-568 (dev_gro_receive) |
| TCP GRO | `net/ipv4/tcp_offload.c` | 286-367 (tcp_gro_receive), 419-440 (tcp4_gro_receive) |
| UDP GRO | `net/ipv4/udp_offload.c` | 877-906 (udp4_gro_receive) |
| GSO segment | `net/core/gso.c` | 66-131 (__skb_gso_segment) |
| Qdisc run | `net/sched/sch_generic.c` | 415-431 (__qdisc_run), 319-372 (sch_direct_xmit) |
| Timestamp TX | `net/core/skbuff.c` | 5686-5748 (__skb_tstamp_tx) |
| netns core | `net/core/net_namespace.c` | 436-465 (setup_net), 662-725 (cleanup_net) |
| cgroup prio | `net/core/netprio_cgroup.c` | 93-131 (netprio_prio/set_prio) |
| skb priority | `net/core/dev.c` | 4299-4322 (skb_update_prio) |
