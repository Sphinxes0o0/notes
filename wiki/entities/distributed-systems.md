---
type: entity
tags: [distributed-systems, distributed-computing, architecture]
created: 2026-05-29
sources: [bookmark-hld-handbook, book-ddia]
---

# Distributed Systems

## Definition

Distributed systems is the field of study about multiple independent computers that appear to users as a single coherent system — coordinating through message passing, sharing nothing, and dealing with partial failures.

## Key Challenge Areas

- **[[distributed-consensus]]** — Paxos, Raft, Byzantine fault tolerance
- **[[distributed-transactions]]** — ACID, 2PC, Sagas
- **[[distributed-replication]]** — Leader-based, multi-leader, leaderless
- **[[distributed-partitioning]]** — Sharding strategies, consistent hashing

## Core Properties

- **Consistency vs Availability** (CAP theorem)
- **Failure Detection** — Heartbeats, phi accrual detector
- **Time in Distributed Systems** — Lamport clocks, vector clocks, TrueTime

## Related Concepts

- [[raft-consensus]] — Raft consensus algorithm
- [[paxos-consensus]] — Paxos consensus algorithm
- [[service-mesh]] — Service mesh for distributed service communication
- [[load-balancing]] — Load balancing in distributed systems

## Sources
- [[bookmark-hld-handbook]] — System Design resources
- [[book-ddia]] — Designing Data-Intensive Applications
