---
type: entity
tags: [linux, networking, tcp, congestion-control, aimd, slow-start, fast-retransmit, cubic, bbr]
created: 2026-05-28
sources: [ebook-systems-approach]
---

# TCP Congestion Control

## Definition

TCP congestion control is a sender-side mechanism that adjusts the rate at which a TCP sender injects packets into the network, based on observed network feedback (packet loss, ECN, RTT). Its goal is to avoid overwhelming intermediate links while achieving high utilization. It operates alongside TCP's **flow control** (receiver's advertised window) and is distinct from it.

## Core Mechanisms

### Additive Increase / Multiplicative Decrease (AIMD)

The fundamental feedback loop:
- **Additive Increase**: When an ACK is received and the network is not congested (no loss), increase `cwnd` (congestion window) by roughly 1 MSS (maximum segment size) per RTT — a linear increase
- **Multiplicative Decrease**: On a loss event (timeout or duplicate ACK), cut `cwnd` in half

This produces a **sawtooth** pattern: gradual ramp-up until loss, then abrupt halving.

**Key insight**: AIMD converges to fair bandwidth allocation where multiple flows share a bottleneck.

### Slow Start

When a TCP connection begins (or after a timeout), `cwnd` starts small (typically 1-10 MSS) and grows **exponentially**: each ACK received allows sending 2× what was acknowledged. This quickly discovers the available bandwidth without starting too aggressively.

**Slow start threshold (`ssthresh`)**: Once `cwnd` reaches `ssthresh`, TCP transitions to **congestion avoidance** (linear increase).

### Fast Retransmit and Fast Recovery

When 3 duplicate ACKs are received (indicating a packet was lost but later packets arrived), the sender:
1. **Fast Retransmit**: Immediately resends the missing segment without waiting for a timeout
2. **Fast Recovery**: Inflates `cwnd` to handle the gap; upon receiving the ACK for the retransmitted data, transitions back to congestion avoidance

This avoids the long timeout period when the network can still deliver data.

### TCP CUBIC

The default Linux congestion control algorithm (since 2.6.19). Uses a cubic function of elapsed time since last loss to set `cwnd`, achieving:
- Aggressive initial ramp-up (faster than classic TCP)
- Window plateau near the previous loss point (W_max)
- Smooth reduction in growth rate as you approach W_max

The cubic function's shape means CUBIC is less aggressive than classic TCP in steady state but can achieve higher throughput in high-BDP networks.

### TCP Reno vs NewReno vs CUBIC

| Algorithm | Behavior on partial loss (3 dupACK) | Behavior on timeout |
|-----------|-------------------------------------|---------------------|
| Reno | Halves cwnd, fast recovery | Restarts slow start from 1 MSS |
| NewReno | Same as Reno but can recover multiple packets per loss event | Same as Reno |
| CUBIC | cwnd = CUBIC function; timeout restarts from W_max × β | Slow start from reduced ssthresh |

## Advanced Congestion Control Algorithms

### ECN (Explicit Congestion Notification)

ECN allows routers to mark packets (using the IP ECN field and TCP ECE flag) instead of dropping them when congestion is imminent. The TCP sender reacts by reducing `cwnd` before packets are lost — reducing unnecessary retransmissions and queuing delay.

### DECbit / RED (Active Queue Management)

**Random Early Detection (RED)**: Router monitors average queue length and probabilistically drops packets before the queue is full. Goals: avoid global synchronization of TCP flows, reduce bias against bursty traffic, keep queues small.

**DECbit**: Set a bit in packet headers when average queue length exceeds threshold; senders interpret this as signal to reduce rate.

### BBR (Bottleneck Bandwidth and RTT)

BBR (see [[entities/linux/network/congestion-control]]) is a **model-based** approach: it builds a model of the bottleneck bandwidth (BtlBw) and round-trip propagation time (RTprop) and uses this to set the sending rate — targeting **zero queue** operation. This contrasts with loss-based algorithms (CUBIC, Reno) that interpret loss as congestion.

### DCTCP (Data Center TCP)

Designed for low-latency, high-BDP data center networks. Uses ECN marks more aggressively: the congestion window reduction is proportional to the fraction of marked packets, keeping queue lengths near zero even with many simultaneous flows.

## Related Pages

- [[entities/linux/network/congestion-control]] — BBR deep dive with Linux implementation details
- [[entities/linux/network/linux-network-protocols]] — Linux TCP stack: tcp_input.c, tcp_output.c implementations
- [[entities/linux/network/quality-of-service]] — AQM, queuing disciplines, relationship to congestion control
- [[sources/arthurchiao-bbr-paper]] — BBR paper analysis
- [[sources/reading-tcp-troubleshooting-plantegg]] — TCP 疑难问题: retransmit, queue overflow
- [[sources/reading-tcp-self-connection-plantegg]] — TCP self-connection edge case
