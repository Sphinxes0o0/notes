---
type: entity
tags: [linux, networking, kernel, napi, softirq, gro, rss, rps, network-stack]
created: 2026-05-28
sources: [arthurchiao-linux-net-stack-implementation-rx]
---

# Network Stack RX Implementation

## Definition

Detailed Linux kernel 5.10 network RX path implementation from NIC to socket receive queue. Uses Mellanox ConnectX-4/5 NICs (mlx5_core driver) as reference.

## 9-Stage RX Pipeline

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

## Key Technical Concepts

### Ring Buffer (DMA)
Circular queue where NIC writes incoming packets directly to pre-allocated kernel memory. Avoids CPU involvement during initial copy.

### NAPI (New API)
Hybrid interrupt-driven + polling approach:
- When active: batch-receives without IRQ generation
- Between polls: new packets trigger interrupts to restart cycle
- Prevents IRQ storm under high load

### GRO (Generic Receive Offloading)
Software packet merging — combines similar packets before protocol stack delivery. Reduces CPU overhead for bulk transfers.

### Packet Distribution
| Mechanism | Type | Description |
|-----------|------|-------------|
| **RSS** | Hardware | Hardware queues per CPU |
| **RPS** | Software | Software redistribution |
| **RFS** | Software | Flow-aware steering |

### Monitoring
`/proc/net/softnet_stat` column `time_squeeze`: indicates softirq budget exhausted but packets remain in ring buffer.

## Related Pages

- [[entities/linux/network/net-stack-tuning-rx]] — Tuning parameters
- [[entities/linux/network/net-stack-overview]] — High-level overview
- [[entities/linux/kernel/irq-softirq]] — Softirq mechanics
- [[entities/linux/kernel/skbuff-deep-dive]] — sk_buff structure
- [[entities/linux/kernel/linux-kernel-net-subsystem]] — Kernel network subsystem
