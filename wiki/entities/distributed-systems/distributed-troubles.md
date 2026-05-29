---
type: entity
tags: [distributed-systems, troubleshooting, failure, debugging]
created: 2026-05-29
sources: [book-ddia]
---

# Distributed System Troubleshooting

## Definition

Distributed system troubleshooting covers the diagnosis and resolution of failures, performance issues, and anomalies that arise in distributed computing environments — including network partitions, clock skew, race conditions, and cascade failures.

## Common Failure Modes

### Network Issues
- **Partition**: Network split — nodes can't communicate but are running
- **Latency spike**: High network delay affecting consensus/replication
- **Reordering**: Packet reordering causing protocol confusion

### Clock/Timing Issues
- **Clock skew**: Physical clock divergence between nodes
- **Lost updates**: Concurrent writes without proper synchronization
- **Phantom reads**: Stale data served from replica

### Cascade Failures
- **Thundering herd**: All clients reconnecting after one failure
- **Amplification**: Small issue causing large cascade

## Diagnosis Tools

- **Distributed tracing**: Zipkin, Jaeger, OpenTelemetry
- **Consistency checkers**: Sequence numbers, vector clocks
- **Network partition simulation**: Chaos engineering (e.g., Chaos Monkey)

## Related Concepts

- [[distributed-systems]] — Overview
- [[distributed-consensus]] — Consensus fault tolerance
- [[raft-consensus]] — Raft algorithm
- [[paxos-consensus]] — Paxos algorithm

## Sources
- [[book-ddia]] — Designing Data-Intensive Applications
