---
type: source
source-type: web
title: "Conntrack Design and Implementation in Linux Kernel"
author: "Arthur Chiao"
date: 2020
url: https://arthurchiao.art/blog/conntrack-design-and-implementation-zh/
summary: "Linux conntrack: netfilter hooks, tuple-based connection tracking, two-phase connection creation (new→confirm), NAT dependency, conntrack table sizing, and Cilium BPF-based alternative."
tags: [linux, networking, netfilter, conntrack, nat, kernel, nids]
created: 2026-05-28
---

# Conntrack Design and Implementation in Linux Kernel

## What is Connection Tracking?
Conntrack monitors and records connection states in a dedicated hash table database. It provides:
- Tuple extraction from packets to identify flows
- State database (creation time, packet/byte counts)
- Garbage collection for expired connections
- Service layer for NAT and firewalls

**Key distinction:** In conntrack, "connection" is based on **tuples** (unidirectional flows). UDP and ICMP (L3 protocols) also have connection records.

## Supported Protocols
TCP, UDP, ICMP, DCCP, SCTP, GRE

## Netfilter Architecture
5 hook points in protocol stack:
| Hook | Purpose |
|------|---------|
| `NF_IP_PRE_ROUTING` | After promiscuous drops, checksum verification |
| `NF_IP_LOCAL_IN` | Packet destined for this host |
| `NF_IP_FORWARD` | Packet destined for another interface |
| `NF_IP_LOCAL_OUT` | Packets from local processes |
| `NF_IP_POST_ROUTING` | Packets about to exit |

**Hook priority:** Conntrack > NAT > Packet Filtering

## Two-Phase Connection Creation

```
nf_conntrack_in() — create new connection record (unconfirmed)
       ↓
nf_conntrack_confirm() — move to confirmed list (POST_ROUTING/LOCAL_IN)
```

**Why two phases?** If packet gets dropped between creation and confirmation, we avoid lingering half-connection records. This accelerates GC.

## NAT Dependency
NAT is **independent** from conntrack but **relies on its results**. Without conntrack records, NAT cannot function.

## Key sysctl Parameters
```bash
net.netfilter.nf_conntrack_max = 1048576    # Table size
net.netfilter.nf_conntrack_buckets = 262144  # Hash size
net.netfilter.nf_conntrack_tcp_timeout_established = 21600  # 6 hours
```

Each entry ~320 bytes. 1M entries ≈ 320 MB.

## Common Problem: Table Full
**Symptoms:** Random connect timeouts (new connections only), TCP SYN silently dropped, kernel log: "nf_conntrack: table full, dropping packet"

**Solutions:**
1. Increase table size (memory cost)
2. Reduce GC timeout (established timeout from 5 days → 6 hours)

## Cilium Alternative
Cilium implements its own conntrack using **BPF hooks** instead of Netfilter (since v1.7.4, kernel 4.19+), enabling Kubernetes networking without Netfilter loaded.

## Related Pages
- [[entities/linux/kernel/netfilter-conntrack]] — Entity page
- [[entities/linux/network/netfilter-hooks]] — Netfilter hooks
- [[entities/linux/network/nat]] — NAT implementation
- [[entities/linux/ebpf/ebpf-networking]] — Cilium's BPF-based approach
