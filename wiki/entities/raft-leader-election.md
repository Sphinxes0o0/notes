---
type: entity
tags: [raft, consensus, leader-election, distributed-systems]
created: 2026-05-29
sources: []
---

# Raft Leader Election

## Definition

Raft uses a leader election mechanism based on randomized election timeouts and heartbeat messages. When a follower doesn't receive heartbeats from the leader within its timeout, it becomes a candidate and initiates a new election.

## Election Process

1. **Timeout**: Follower's election timer expires (randomized 150-300ms)
2. **Candidate state**: Follower increments term, votes for itself
3. **RequestVote RPC**: Broadcast to all servers
4. **Election outcome**:
   - **Majority vote** → Becomes leader
   - **Higher term found** → Reverts to follower
   - **No majority** → New election (split vote)

## Critical Properties

- **Election safety**: At most one leader per term
- **Leader append-only**: Leader never overwrites or deletes log entries
- **Log matching**: If entries match across servers, they have identical prefix

## Related Concepts

- [[raft-consensus]] — Raft consensus algorithm
- [[raft-log-replication]] — Log replication details
- [[paxos-consensus]] — Paxos (Raft's theoretical foundation)
- [[distributed-systems]] — Distributed systems overview
