---
type: entity
tags: [linux, networking, qos, queuing, aqm, scheduling, diffserv, intserv, rsvp, ecn]
created: 2026-05-28
sources: [ebook-systems-approach]
---

# Quality of Service (QoS)

## Definition

Quality of Service refers to the ability of a network to provide differentiated treatment to specific traffic flows, offering guarantees (or bounded probabilistic guarantees) of bandwidth, latency, jitter, and packet loss — beyond the best-effort default. Required for real-time applications like VoIP, video conferencing, and online gaming.

## Queuing Disciplines

A **queuing discipline (qdisc)** sits at a network interface's output and determines which packet to transmit next when the send queue has multiple packets.

### FIFO (First-In, First-Out)

The simplest discipline: packets are transmitted in arrival order. All traffic competes equally; no differentiation.

**Problem**: A single bandwidth-intensive flow can starve all other traffic.

### Fair Queuing (FQ)

FQ processes each flow's packets in a round-robin fashion, ensuring no single flow dominates the link. **Bit-by-bit FQ** achieves perfect fairness but is complex to implement.

**Stochastic Fair Queuing (SFQ)**: Hashes flow 5-tuples into a fixed number of buckets; each bucket is serviced round-robin. Low hardware cost but collisions possible.

**Deficit Round Robin (DRR)**: Accounts for variable packet sizes; more accurate fairness than simple round-robin.

### Class-Based Queuing (CBQ)

Hierarchical link sharing: traffic is divided into classes (e.g., by destination, protocol, DSCP). Each class gets a guaranteed minimum bandwidth and may borrow from idle classes.

## Active Queue Management (AQM)

AQM manages the **packets waiting in queues** (the queue before transmission), as opposed to scheduling which decides transmission order.

### RED (Random Early Detection)

Monitors **average queue length** (exponentially weighted moving average). Two thresholds:
- Below `min_threshold`: no drops
- Above `max_threshold`: drop all new arrivals
- Between the two: drop probability increases linearly with avg queue length

**Goal**: Keep the queue small enough to absorb bursts but large enough for link utilization. Prevents global synchronization (many TCP flows simultaneously reducing rates).

### ECN (Explicit Congestion Notification)

Instead of dropping packets, ECN-capable routers set the **ECN bit** in the IP header and the **ECE flag** in the TCP header to signal congestion. The TCP sender reduces `cwnd` before loss occurs. Requires both the router and both TCP endpoints to be ECN-capable.

**Benefit over RED**: Zero packet loss for ECN-capable traffic; lower latency for interactive flows.

## QoS Architecture

### Integrated Services (IntServ)

Flow-based QoS with **per-flow reservation** using RSVP (Resource Reservation Protocol). Each router along the path reserves resources (bandwidth, buffer) for the flow.

**Limitation**: Does not scale — requires router state for every flow; impractical for the public Internet.

### Differentiated Services (DiffServ)

Class-based QoS using the **DSCP field** (6 bits) in the IP Type of Service byte. Packets are classified and marked at the network edge; core routers simply apply **Per-Hop Behaviors (PHBs)** based on DSCP.

**EF (Expedited Forwarding)**: Low-loss, low-latency, low-jitter — suitable for VoIP. Typically mapped to a priority queue with strict rate guarantee.

**AF (Assured Forwarding)**: Four classes × three drop precedences. Gives better-than-best-effort service with differentiated drop probability under congestion.

**Problem**: Without policing at the network edge, misbehaving flows can abuse their class; no hard guarantees.

## NIDS-Relevant Points

- **QoS as evasion vector**: Attackers can mark their traffic as EF (low-latency queue) to bypass inspection or gain bandwidth advantage.
- **Queue management at IDS tap points**: If an IDS is inline with a QoS-enabled link, its own processing latency may cause it to be perceived as a congestion point, triggering ECN marks.
- **Per-flow state in firewalls/NIDS**: Connection tracking and per-flow statistics are analogous to IntServ reservations — scaling concern is the same.
- See [[sources/reading-linux-tc-traffic-control]] for NIDS testing with `netem`/`tbf` qdiscs.

## Related Pages

- [[entities/linux/network/tcp-congestion-control]] — Relationship between congestion control and QoS
- [[entities/linux/network/congestion-control]] — BBR targeting zero queue
- [[sources/reading-linux-advanced-routing-tc]] — Linux TC qdisc/netem for QoS
- [[sources/reading-linux-tc-traffic-control]] — NIDS testing with traffic control tools
