---
type: source
source-type: web
title: "Linux Network Stack RX Implementation Deep Dive"
author: "Arthur Chiao"
date: 2022
url: https://arthurchiao.art/blog/linux-net-stack-implementation-rx-zh/
summary: "Detailed Linux kernel 5.10 RX path implementation using Mellanox ConnectX-4/5 NICs: NAPI, DMA ring buffer, softirq, GRO, RSS/RPS/RFS packet distribution, and 9-stage RX pipeline."
tags: [linux, networking, kernel, napi, softirq, gro, rss, rps, network-stack]
created: 2026-05-28
---

# Linux Network Stack RX Implementation Deep Dive

## 9-Stage RX Pipeline (NIC → Socket)

```
1. Driver initialization (NAPI poll registration)
2. NIC packet arrival
3. DMA transfer to kernel ring buffer
4. Hardware IRQ triggering (when NAPI not active)
5. Softirq scheduling to ksoftirqd thread
6. NAPI poll executing to drain ring buffer
7. L2 protocol processing
8. L3/IP protocol handling
9. L4/UDP delivery to socket receive queue
```

## Core Technical Concepts

### Ring Buffer (DMA)
Circular queue where NIC writes incoming packets directly to pre-allocated kernel memory. Avoids CPU involvement during initial copy.

### NAPI (New API)
Hybrid interrupt-driven + polling approach:
- When active: batch-receives packets without IRQ generation
- Between polls: new packets trigger interrupts to restart cycle
- Prevents IRQ storm under high load

### Softirq Processing
- `ksoftirqd` per-CPU threads execute `net_rx_action()`
- Budget limits: `netdev_budget` (default 300 packets), `netdev_budget_usecs` (default 2ms)
- `time_squeeze` counter in `/proc/net/softnet_stat` = ring still has packets but budget exhausted

### GRO (Generic Receive Offloading)
Software packet merging — combines similar packets before protocol stack delivery. Reduces CPU overhead for bulk transfers.

### Packet Distribution Mechanisms
| Mechanism | Type | Description |
|-----------|------|-------------|
| **RSS** | Hardware | Hardware queues per CPU |
| **RPS** | Software | Software redistribution |
| **RFS** | Software | Flow-aware steering |

## Key Monitoring Metric
`/proc/net/softnet_stat` column `time_squeeze`: indicates when softirq budget exhausted but packets remain in ring buffer — a tuning trigger.

## Related Pages
- [[entities/linux/network/net-stack-tuning-rx]] — Tuning parameters
- [[entities/linux/network/net-stack-overview]] — Stack overview
- [[entities/linux/kernel/irq-softirq]] — Softirq mechanics
- [[entities/linux/kernel/skbuff-deep-dive]] — sk_buff structure
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — Kernel network subsystem

## Images

![9-Stage RX Pipeline Overview](attachments/arthurchiao/linux-net-stack-implementation-rx/rx-overview.png)
*Figure: 9-Stage RX Pipeline from NIC to Socket*

![DMA Ring Buffer](attachments/arthurchiao/linux-net-stack-implementation-rx/dma-ringbuffer.png)
*Figure: DMA Ring Buffer — circular queue where NIC writes incoming packets*

![NAPI and GRO Receive](attachments/arthurchiao/linux-net-stack-implementation-rx/napi_gro_receive.png)
*Figure: NAPI poll cycle with GRO (Generic Receive Offloading)*

![L3 Processing Stack](attachments/arthurchiao/linux-net-stack-implementation-rx/l3-processing-stack.png)
*Figure: L3/IP Protocol processing stack*

![UDP Receive](attachments/arthurchiao/linux-net-stack-implementation-rx/uu_udp4_lib_rcv.png)
*Figure: UDP delivery path to socket receive queue*

## 9-Stage RX Pipeline Architecture

```mermaid
flowchart TD
    subgraph Stage1["Stage 1: Driver Init"]
        NAPI[NAPI Poll<br/>Registration]
    end

    subgraph Stage2_4["Stages 2-4: Packet Arrival"]
        PACKET[Packet Arrival<br/>at NIC]
        DMA[ DMA Transfer to<br/>Ring Buffer]
        IRQ[Hard IRQ<br/>Triggered]
    end

    subgraph Stage5_6["Stages 5-6: Softirq Processing"]
        SCHED[Schedule<br/>ksoftirqd]
        POLL[NAPI Poll<br/>Executes]
    end

    subgraph Stage7_9["Stages 7-9: Protocol Stack"]
        L2[L2 Protocol<br/>Processing]
        L3[L3/IP<br/>Handling]
        L4[L4/UDP<br/>Delivery]
    end

    SQ[Socket<br/>Receive Queue]

    NAPI --> PACKET
    PACKET --> DMA
    DMA --> IRQ
    IRQ --> SCHED
    SCHED --> POLL
    POLL --> L2
    L2 --> L3
    L3 --> L4
    L4 --> SQ

    style Stage1 fill:#e1f5fe
    style Stage2_4 fill:#fff3e0
    style Stage5_6 fill:#e8f5e9
    style Stage7_9 fill:#f3e5f5
```
