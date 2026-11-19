---
type: entity
tags: [linux, ebpf, traffic-control, networking, tc]
created: 2026-05-29
sources: [bookmark-sdn-guide]
---

# TC Direct Action Mode

## Definition

TC (Traffic Control) Direct Action (DA) mode is a Linux kernel networking feature where an eBPF program attached to a network interface's TC (traffic control) hook can process packets and directly invoke packet actions (drop, redirect, etc.) without requiring a separate action in the TC action chain. It is commonly used together with XDP for flexible packet processing pipelines.

## How It Works

```
NIC → XDP (early) → [drop/pass/redirect] → TC (DA mode) → [drop/redirect/etc.]
```

### Comparison with Traditional TC

| Aspect | Traditional TC | TC Direct Action |
|--------|----------------|------------------|
| Classification | `fw`, `u32`, `flower` classifiers | eBPF classifier |
| Action | Separate action in chain | Direct in program |
| XDP combination | Not combined | Works with XDP pipeline |
| Flexibility | Limited | Full eBPF expressiveness |

## Use Cases

- **XDP + TC pipeline**: XDP handles early processing, TC DA handles post-classification actions
- **Multi-buffer XDP**: TC DA processes packets that XDP couldn't handle in single buffer
- **Advanced queuing**: Complex scheduling with eBPF classification

## Related Concepts

- [[linux-ebpf-xdp]] — XDP (works before TC in pipeline)
- [[linux-ebpf-overview]] — eBPF fundamentals
- [[load-balancing]] — Load balancing using eBPF/TC

## Sources
- [[bookmark-sdn-guide]] — SDN Guide eBPF/TC section
