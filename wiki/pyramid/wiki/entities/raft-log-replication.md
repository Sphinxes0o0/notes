---
type: entity
tags: [raft, consensus, log-replication, distributed-systems]
created: 2026-05-29
sources: []
---

# Raft Log Replication

## Definition

Raft replicates log entries from the leader to other cluster members using AppendEntries RPC. Once the leader confirms a majority of servers have written the entry, it is considered committed and can be applied to the state machine.

## Replication Process

1. **Client request**: Leader receives command, appends to local log
2. **Parallel RPC**: Leader broadcasts AppendEntries to all followers
3. **Follower processing**: Follower appends entries after consistency check
4. **Response**: Leader counts acknowledgments from majority
5. **Commit**: Leader marks entry committed, notifies followers, applies to state machine

### Log Consistency Check

Each AppendEntries includes `prevLogIndex` and `prevLogTerm`. Follower rejects if its log doesn't have an entry at `prevLogIndex` with matching `prevLogTerm`.

## Key Properties

- **Log compaction**: Snapshotting (like Chubby's Raft implementation)
- **Membership changes**: Joint consensus for adding/removing nodes
- **Linearizability**: Client-session semantics with `readIndex`

## Related Concepts

- [[raft-consensus]] — Raft consensus algorithm
- [[raft-leader-election]] — Leader election details
- [[paxos-consensus]] — Paxos algorithm
- [[distributed-systems]] — Distributed systems overview
