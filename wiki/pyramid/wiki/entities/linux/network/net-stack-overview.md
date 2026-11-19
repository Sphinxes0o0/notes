---
type: entity
tags: [linux, networking, kernel, network-stack, monitoring, architecture]
created: 2026-05-28
sources: [arthurchiao-linux-net-stack]
---

# Linux Network Stack Overview

## Definition

The Linux network stack encompasses the entire data path from NIC arrival through kernel protocol stack to user-space applications. Linux 5.10 kernel network stack covers IRQ/softirq mechanisms, RX/TX data paths, kernel protocol layers (L2→L3→L4), NIC drivers, and BPF/XDP.

## Key Architecture

### RX Path (simplified)
```
NIC → DMA ring buffer → Hard IRQ → Softirq (ksoftirqd)
  → NAPI poll → GRO → L2 (Ethernet) → L3 (IP) → L4 (TCP/UDP)
  → Socket receive queue → Application
```

### TX Path (simplified)
```
Application → Socket send queue → L4 (TCP/UDP) → L3 (IP) → L2 (Ethernet)
  → Softirq (net_tx_action) → NIC driver → DMA → NIC
```

## Core Components

| Component | Role |
|-----------|------|
| **Ring Buffer** | DMA-accessible circular queue; NIC writes packets directly |
| **NAPI** | Hybrid interrupt/polling; prevents IRQ storm under load |
| **GRO** | Generic Receive Offload; merges similar packets before protocol stack |
| **sk_buff** | Linux network buffer representation |
| **Netfilter** | Packet filtering, NAT, connection tracking hooks |

## Monitoring Stack
Prometheus + Grafana for visualizing network metrics. The 80/20 principle applies: most issues resolve quickly, remaining cases require deep kernel knowledge.

## Related Pages

- [[entities/linux/network/net-stack-implementation-rx]] — RX implementation deep dive
- [[entities/linux/network/net-stack-tuning-rx]] — RX tuning parameters
- [[entities/linux/kernel/irq-softirq]] — IRQ/softirq mechanics
- [[entities/linux/kernel/skbuff-deep-dive]] — sk_buff structure
- [[entities/linux/ebpf/ebpf-networking]] — BPF/XDP integration
