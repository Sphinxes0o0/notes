---
type: entity
tags: [linux, networking, tuning, ethtool, sysctl, rss, rps, gro, softirq]
created: 2026-05-28
sources: [arthurchiao-linux-net-stack-tuning-rx]
---

# Network Stack RX Tuning

## Definition

Comprehensive ethtool and sysctl tuning parameters for Linux kernel 5.10 network RX path: IRQ coalescing, RSS, RPS, RFS, GRO, softirq budget, and CPU power state settings.

## Key Tuning Parameters

### Driver (ethtool)
| Command | Purpose | Key Settings |
|---------|---------|--------------|
| `ethtool -l/-L` | RX queue quantity | `rx N` or `combined N` |
| `ethtool -g/-G` | RX ring buffer size | Larger = fewer drops under high PPS |
| `ethtool -x/-X` | RSS weights | `equal N` or `weight w1 w2...` |
| `ethtool -c/-C` | Interrupt coalescing | `adaptive-rx on` for latency/throughput trade-off |
| `ethtool -k/-K` | Offloads | `gro on`, `ntuple on` |

### Softirq (sysctl)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `netdev_budget` | 300 | Max packets per softirq cycle |
| `netdev_budget_usecs` | 2000 | Max CPU time per softirq cycle |
| `dev_weight` | 64 | Backlog poll loop weight |

### Socket Buffers
- `rmem_max`: Socket receive buffer max (critical for QUIC/high-throughput)
- `netdev_max_backlog`: Backlog queue size (default 1000)

### CPU Power State
Disable power saving for consistent latency:
```bash
AMD_pstat=disable idle=poll noohz=off iommu=pt
```

## Monitoring
- `/proc/softirqs` — Soft interrupt distribution
- `/proc/net/softnet_stat` — Per-CPU network processing stats
- `ethtool -S <device>` — Device statistics

## Key Insight
No universal configuration — tune based on workload. Always establish monitoring before tuning.

## Related Pages

- [[entities/linux/network/net-stack-implementation-rx]] — RX implementation
- [[entities/linux/kernel/irq-softirq]] — Softirq mechanics
- [[entities/linux/kernel/cpu-power-management]] — CPU power state impact
- [[entities/linux/ebpf/ebpf-networking]] — XDP/BPF integration points
