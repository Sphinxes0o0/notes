---
type: source
source-type: web
title: "Facebook XDP/eBPF Traffic Routing: From XDP to Socket"
author: "Arthur Chiao"
date: 2022
url: https://arthurchiao.art/blog/facebook-from-xdp-to-socket-zh/
summary: "Facebook's production XDP/eBPF infrastructure: Katran L4 load balancer with Maglev hashing, BPF socket operations for server_id embedding, zero-downtime releases via bpf_sk_reuseport."
tags: [linux, ebpf, xdp, networking, load-balancing, facebook, production]
created: 2026-05-28
---

# Facebook XDP/eBPF Traffic Routing Infrastructure

## Two-Stage Traffic Routing
1. **LB node → backend host**: L4 routing (Katran, XDP-based)
2. **Host internal**: kernel → sockets via BPF (L7)

## Key Technical Solutions

### 1. Stateless L4 Routing (Katran)
- XDP-based L4 load balancer using **Maglev hashing**
- **Problem**: Backend failures cause connection resets
- **Solution**: Embed `server_id` in TCP header via `BPF_PROG_TYPE_SOCK_OPS`

### 2. Zero-Downtime Releases
- Old approach: Graceful shutdown causes capacity loss
- BPF solution: `bpf_sk_reuseport` attaches to socket layer for packet routing
- Uses `BPF_MAP_TYPE_REUSEPORT_SOCKARRAY` to control traffic switching

## Technical Challenges Encountered
- CPU spikes from listening socket hashtable (only used `dst_port` as hash key)
- Fixed via kernel improvements

## Key Takeaways
- **Stateless routing**: No connection state sharing between LB nodes
- **BPF enables per-socket load balancing** without shared sockets between processes
- Supports both **TCP and UDP** (including QUIC)
- Production-scale eBPF for consistent routing and seamless deployments

## Architecture Pattern
```
XDP (NIC) → kernel protocol stack → BPF socket ops → application socket
                ↑
         Katran LB (Maglev)
```

## Related Pages
- [[entities/linux/ebpf/ebpf-networking]] — eBPF networking hook points
- [[entities/linux/ebpf/ebpf-xdp]] — XDP details
- [[entities/linux/network/load-balancing]] — Load balancing concepts
- [[entities/linux/network/modern-lb-proxy]] — Envoy, service mesh context

## Images

![Katran Traffic Infrastructure](attachments/arthurchiao/facebook-xdp-to-socket/traffic-infra-1.jpg)
*Figure: Katran L4 load balancer — XDP-based production load balancing at Facebook*

![Katran Performance](attachments/arthurchiao/facebook-xdp-to-socket/katran-perf.jpg)
*Figure: Katran vs IPVS — superior performance with Maglev hashing*

![Maglev Hashing Performance](attachments/arthurchiao/facebook-xdp-to-socket/maglev-perf.jpg)
*Figure: Maglev consistent hashing — minimal re-mapping during backend changes*

![BPF Socket Takeover](attachments/arthurchiao/facebook-xdp-to-socket/socket-takeover-1.jpg)
*Figure: BPF sk_reuseport — zero-downtime service deployment*

![BPF Map Structure](attachments/arthurchiao/facebook-xdp-to-socket/bpf-map-1.jpg)
*Figure: BPF sockhash map — stores socket references for fast lookup*

## Architecture Diagram

```mermaid
flowchart LR
    subgraph Client["Client"]
        C[TCP Connection]
    end

    subgraph LB["Katran L4 LB (XDP)"]
        XDP[XDP Program]
        MAGLEV[Maglev Hashing]
        SERVER_ID[Embed server_id<br/>in TCP header]
    end

    subgraph Backend["Backend Host"]
        BPF_SOCK[BPF Socket Ops<br/>sockops program]
        SOCKMAP[BPF Map<br/>sockhash]
        SK_MSG[sk_msg program<br/>msg_redirect_hash]
        APP[Application]
    end

    C -->|L4 routing| XDP
    XDP --> MAGLEV
    MAGLEV --> SERVER_ID
    SERVER_ID -->|forward| BPF_SOCK
    BPF_SOCK -->|store socket| SOCKMAP
    SK_MSG -->|lookup| SOCKMAP
    SK_MSG -->|bypass stack| APP

    style XDP fill:#c8e6c9
    style SOCKMAP fill:#bbdefb
```
