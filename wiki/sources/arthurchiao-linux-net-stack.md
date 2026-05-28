---
type: source
source-type: web
title: "Linux Network Stack: Principles, Monitoring & Tuning"
author: "Arthur Chiao"
date: 2022
url: https://arthurchiao.art/blog/linux-net-stack-zh/
summary: "Linux 5.10 kernel network stack overview covering IRQ/softirq, RX/TX data paths, kernel protocol stack layers, BPF/XDP, and monitoring with Prometheus/Grafana."
tags: [linux, networking, kernel, network-stack, monitoring, ebpf, xdp]
created: 2026-05-28
---

# Linux Network Stack: Principles, Monitoring & Tuning

## Core Content

### Architecture
The "stack" encompasses the entire data path from NIC arrival through kernel protocol stack to user-space applications. Linux 5.10 kernel network stack covers:
- IRQ/softirq mechanisms
- RX/TX data paths
- Kernel protocol stack layers (L2 → L3 → L4)
- NIC drivers (Mellanox mlx5_core example)
- BPF/XDP technologies

### Monitoring Stack
Prometheus + Grafana for visualizing network metrics. The article applies 80/20 principle: most issues resolve quickly with basic monitoring, remaining cases require deep kernel network stack knowledge.

### Related Topics Covered
- Kubernetes networking: ServiceIP (L4 load balancing) and NetworkPolicy (L3/L4 access control)
- NIDS context: full packet path visibility is critical for detection

## Key Insight
Understanding the full network stack "opens new horizons" for addressing performance issues and implementing cloud-native networking solutions. This is a gateway article to a series covering RX implementation, TX implementation, and tuning guides.

## Related Pages
- [[entities/linux/network/net-stack-implementation-rx]] — RX implementation deep dive
- [[entities/linux/network/net-stack-tuning-rx]] — RX tuning guide
- [[entities/linux/kernel/irq-softirq]] — IRQ/softirq mechanics
- [[entities/linux/ebpf/ebpf-networking]] — BPF/XDP integration
- [[entities/linux/kernel/skbuff-deep-dive]] — sk_buff structure

## Images

![RX Pipeline Overview](attachments/arthurchiao/linux-net-stack/rx-overview.png)
*Figure: Linux Network Stack RX Overview — NIC to Socket path*

![DMA Ring Buffer](attachments/arthurchiao/linux-net-stack/dma-ringbuffer.png)
*Figure: DMA Ring Buffer — NIC writes packets directly to pre-allocated kernel memory*

![IRQ and NAPI Poll](attachments/arthurchiao/linux-net-stack/irq-and-napi-poll.png)
*Figure: IRQ and NAPI Poll Cycle — interrupt-driven + polling hybrid*

![NET_RX_SOFTIRQ Processing](attachments/arthurchiao/linux-net-stack/net_rx_action.png)
*Figure: net_rx_action() — softirq handler processing packets from ring buffer*

![CPU Schedule Threads](attachments/arthurchiao/linux-net-stack/cpu-schedule-threads.png)
*Figure: ksoftirqd per-CPU thread scheduling*

## Architecture Diagram

```mermaid
flowchart LR
    NIC[NIC Hardware] -->|DMA| RB[Ring Buffer<br/>pre-allocated sk_buffs]
    RB -->|Hard IRQ| ISR[ISR<br/>Top Half]
    ISR -->|raises softirq| KSOFT[ksoftirqd<br/>per-CPU thread]
    KSOFT -->|net_rx_action| NAPI[NAPI Poll<br/>batch processing]
    NAPI -->|GRO| L2[L2 Protocol<br/>eth_type_trans]
    L2 -->|skb| L3[L3/IP Protocol<br/>ip_rcv/ipv6_rcv]
    L3 -->|L4| UDP[UDP<br/>udp_rcv]
    UDP -->|deliver| SQ[Socket<br/>Receive Queue]

    subgraph "IRQ & NAPI Cycle"
        IRQ_HWM[New Packets<br/>trigger IRQs] -->|wake| NAPI
        NAPI -->|busy poll| NAPI
        NAPI -->|budget exhausted| KSOFT
    end
```
