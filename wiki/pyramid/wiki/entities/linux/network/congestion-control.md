---
type: entity
tags: [linux, networking, tcp, congestion-control, bbr, networking]
created: 2026-05-28
sources: [arthurchiao-bbr-paper]
---

# Congestion Control: BBR

## Definition

BBR (Bottleneck Bandwidth and Round-trip propagation time) is a congestion-based congestion control algorithm that measures bottleneck bandwidth (BtlBw) and round-trip propagation time (RTprop) to maintain zero bottleneck queue — outperforming loss-based algorithms in modern networks.

## Core Concepts

### Two Fundamental Parameters
- **RTprop**: Round-trip propagation time (path length/distance)
- **BtlBw**: Bottleneck bandwidth (narrowest pipe)
- **BDP = BtlBw × RTprop** (bandwidth-delay product)

### Three Operating Regions
| Region | Inflight | State |
|--------|----------|-------|
| App-limited | < BDP | Below BDP |
| Bandwidth-limited | = BDP | Optimal |
| Buffer-limited | > BDP | Causes bufferbloat |

### BBR State Machine
```
STARTUP → exponential probing (2/ln2 gain) to discover BtlBw
   ↓
DRAIN → inverse gain to drain startup queue
   ↓
PROBE_BW → 8-phase gain cycling (5/4, 3/4, 1,1,1,1,1,1)
   ↓
PROBE_RTT → periodic minimum-inflight probing (100ms every ~10s)
```

### Key Architecture
- **pacing_rate**: Primary control; matches bottleneck rate
- **cwnd_gain**: Set to 2×BDP to handle delayed/stretched ACKs
- **onAck()**: Updates RTprop/BtlBw estimates from ACK data

## Why BBR Excels
- **Sender-side only**: No protocol/receiver/network changes needed
- **Zero bottleneck queue**: Loss-based algorithms fill buffers (bufferbloat)
- **5% packet loss tolerance** vs CUBIC degrading at 0.1%
- YouTube: 53% median RTT reduction globally; 80% in developing regions

## Related Pages

- [[entities/linux/network/modern-lb-proxy]] — Load balancing context
- [[entities/linux/network/net-stack-implementation-rx]] — Where ACK processing occurs
- [[entities/linux/network/load-balancing]] — Backend congestion control
