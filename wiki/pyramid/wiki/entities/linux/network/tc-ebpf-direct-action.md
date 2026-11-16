---
type: entity
tags: [linux, ebpf, tc, networking, traffic-control, cilium, clsact]
created: 2026-05-28
sources: [arthurchiao-tc-da-mode]
---

# TC eBPF Direct-Action Mode

## Definition

TC (Traffic Control) direct-action (da) mode allows eBPF classifiers to return action verdicts (`TC_ACT_OK`, `TC_ACT_SHOT`) directly instead of classids, eliminating the need for separate action modules. Introduced in kernel 4.4.

## Traditional TC Architecture
- **qdisc**: Queueing discipline for traffic shaping
- **class**: User-defined traffic categories
- **classifier (filter)**: Matches packets, dispatches to classes
- **action**: Operations on packets (drop, allow, mirror)

Classic classifiers return **classids**, actions return operation codes (`TC_ACT_SHOT`, `TC_ACT_OK`).

## Direct-Action Problem
Classic `classifier + action` pattern requires two separate steps. For "match + act" operations (e.g., drop packets from specific IPs), this introduces unnecessary overhead.

## Direct-Action Solution
The `direct-action` flag tells TC subsystem to interpret eBPF classifier return value as **action code** instead of classid.

### Action Verdicts
| Return | Value | Meaning |
|--------|-------|---------|
| `TC_ACT_OK` | 0 | Allow packet |
| `TC_ACT_SHOT` | 2 | Drop packet |
| `TC_ACT_RECLASSIFY` | 1 | Reclassify |

## clsact Qdisc
Added in kernel 4.5, `clsact` is a super-set of ingress qdisc supporting direct-action on **both ingress and egress** without queuing.

```bash
tc qdisc add dev eth0 clsact
tc filter add dev eth0 ingress bpf direct-action obj foo.o sec .text
```

## Related Pages

- [[entities/linux/ebpf/ebpf-networking]] — TC + eBPF context
- [[entities/linux/ebpf/ebpf-xdp]] — XDP comparison
- [[entities/linux/network/net-stack-implementation-rx]] — Where TC hooks are called
