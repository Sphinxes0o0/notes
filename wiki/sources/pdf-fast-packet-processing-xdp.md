---
type: source
tags: []
created: 2026-05-26source-type: pdf
title: "Fast Packet Processing using eBPF and XDP"
author: "Unknown"
date: 2020
size: medium
path: raw/PDFs/papers/Fast-Packet-Processing-using-eBPF-and-XDP.pdf
summary: "Technical deep-dive into XDP (eXpress Data Path) — eBPF's high-performance packet processing hook — covering architecture, use cases, and performance benchmarks."
created: 2026-05-27
---

# Fast Packet Processing using eBPF and XDP

## Core Content

A technical exploration of XDP (eXpress Data Path) — a Linux kernel feature that runs eBPF programs at the earliest possible point in the networking stack, before the kernel's main packet processing infrastructure.

### XDP Architecture

- **Hook Point**: XDP runs in the NIC driver's receive interrupt context — before the kernel allocates an `sk_buff`, before any routing decisions, before netfilter/iptables. This is as early as it gets.
- **Execution Path**: NIC interrupt → XDP program (eBPF) → decision (DROP/PASS/REDIRECT/TX) → (if PASS) normal kernel networking stack.
- **eBPF Program Type**: `BPF_PROG_TYPE_XDP`. Receives a raw `xdp_md` context with pointers to the packet data.
- **Actions**:
  - `XDP_DROP`: Drop the packet. Used for DDoS mitigation, firewalling, rate limiting.
  - `XDP_PASS`: Pass to the normal kernel stack. The packet is converted to an skb.
  - `XDP_REDIRECT`: Redirect to another interface (including virtual devices like veth, tun) or to a socket.
  - `XDP_TX`: Transmit on the same interface (useful for reflection/loopback scenarios).
- **Zero-Copy**: With supported NIC drivers (most modern Intel, Mellanox, etc.), XDP can access packet data without copying — DMA directly into eBPF-accessible memory.

### Performance

- **Numbers**: 10-100 Gbps line rate packet processing on commodity x86 servers. 10-100 million packets per second (Mpps) depending on hardware.
- **Latency**: Sub-microsecond per-packet processing overhead. No context switch to userspace required.
- **vs iptables**: iptables processes packets at ~2-5 Mpps per core. XDP processes at 10-100 Mpps per core — a 10-50x improvement.
- **CPU Efficiency**: XDP programs are I/O bound (NIC DMA) not CPU bound. Scales linearly with NIC queue count.

### Use Cases

- **DDoS Mitigation**: Load-balanced, distributed XDP-based scrubbing farms (e.g., Cloudflare's Gatebot).
- **Packet Filtering/Firewall**: Bare-metal firewalls (e.g., OpenVSwitch with XDP backend).
- **Load Balancing**: XDP-based L4 load balancers (e.g., Katran from Meta).
- **Telemetry/Monitoring**: Passive packet sampling without disrupting data path (e.g., Facebook's Katran, Cilium's Hubble).
- **tc (Traffic Control) Hook**: Beyond XDP, eBPF programs can also attach at the `tc` (traffic control) ingress/egress hooks, which operate after the skb is allocated — a complementary hook point for different use cases.

### Key Findings

- XDP is the fastest software data plane available in Linux — beating iptables, DPDK, and most userspace packet processing frameworks.
- The combination of XDP (early hook) + tc egress (post-routing hook) provides a complete packet processing pipeline.
- eBPF's verifier ensures XDP programs are safe — no kernel panics from malicious XDP code.

## Source Details

- **Path**: raw/PDFs/papers/Fast-Packet-Processing-using-eBPF-and-XDP.pdf
- **Size**: 1.4 MB
- **Domain**: Networking, XDP, high-performance packet processing, Linux