# Linux ARP Table Aging Mechanism

## Core Concept
Linux ARP table entries have 3 states: **delay → reachable → stale**. The stale state reduces ARP broadcasts.

## Three States
1. **delay**: Waiting before testing reachability
2. **reachable**: Confirmed reachable (within timeout)
3. **stale**: Timeout expired, but entry not deleted yet (reduces ARP overhead)

## Timeout Formula
```
Timeout = random(base_reachable_time/2, 3*base_reachable_time/2) + gc_stale_time
```

## Key Parameters
| Parameter | Purpose |
|-----------|---------|
| `gc_thresh1` | Min entries before GC runs (default: 128) |
| `base_reachable_time` | Base reachable timeout |
| `gc_stale_time` | How long stale entries live before GC |

## Key Insight
**arping** can refresh STALE→REACHABLE, but **ping** cannot. This is a GC time mechanism issue.

## Monitoring Commands
- `ip -s neigh` — Full ARP entry state transitions
- `ip neigh show` — Shows REACHABLE/STALE state
- `arp -a` — Shows entries but NOT state
