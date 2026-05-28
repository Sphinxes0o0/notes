---
type: source
source-type: web
title: "BBR: Congestion-Based Congestion Control (Paper Summary)"
author: "Arthur Chiao (translation of ACM 2017 paper)"
date: 2022
url: https://arthurchiao.art/blog/bbr-paper-zh/
summary: "BBR congestion control algorithm: measures bottleneck bandwidth (BtlBw) and round-trip propagation time (RTprop) to maintain zero bottleneck queue, outperforming loss-based algorithms in modern networks."
tags: [linux, networking, tcp, congestion-control, bbr, networking]
created: 2026-05-28
---

# BBR: Congestion-Based Congestion Control

## Core Problem
Previous TCP congestion control used **packet loss as congestion indicator** — valid in 1980s but outdated. Modern networks experience packet loss without actual congestion.

## Two Fundamental Parameters
- **RTprop**: Round-trip propagation time (path length/distance)
- **BtlBw**: Bottleneck bandwidth (narrowest pipe)
- **BDP = BtlBw × RTprop** (bandwidth-delay product)

## Three Operating Regions
Based on inflight data:
1. **App-limited**: below BDP
2. **Bandwidth-limited**: at BDP (optimal)
3. **Buffer-limited**: above BDP (causes bufferbloat)

## BBR State Machine

```
STARTUP → exponential probing (2/ln2 gain) to discover BtlBw
   ↓
DRAIN → inverse gain to drain startup queue
   ↓
PROBE_BW → 8-phase gain cycling (5/4, 3/4, 1,1,1,1,1,1)
   ↓
PROBE_RTT → periodic minimum-inflight probing (100ms every ~10s)
```

## Key Architecture
- **pacing_rate**: Primary control; matches bottleneck rate
- **cwnd_gain**: Set to 2×BDP to handle delayed/stretched ACKs
- **onAck()**: Updates RTprop/BtlBw estimates from ACK data
- **send()**: Controls pacing based on estimates

**Key insight:** RTprop and BtlBw **cannot be measured simultaneously** (uncertainty principle). Solution: sequential gain cycling.

## Why BBR Excels
- Runs only on **sender side** — no protocol/receiver/network changes needed
- Maintains **zero bottleneck queue** (loss-based fills buffers)
- B4 WAN: 2–25× throughput improvement; 133× with receiver buffer tuning
- YouTube: 53% median RTT reduction globally; 80% in developing regions
- **5% packet loss tolerance** vs CUBIC degrading at 0.1%

## Related Pages
- [[entities/linux/network/congestion-control]] — Entity page
- [[entities/linux/network/tcp-congestion-control]] — TCP congestion control overview
- [[entities/linux/network/net-stack-implementation-rx]] — Where ACK processing happens
