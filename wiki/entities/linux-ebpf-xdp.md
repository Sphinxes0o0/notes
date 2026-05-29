---
type: entity
tags: [linux, ebpf, xdp, networking, high-performance]
created: 2026-05-29
sources: [bookmark-sdn-guide]
---

# XDP (eXpress Data Path)

## Definition

XDP (eXpress Data Path) is an eBPF-based programmable data path in the Linux kernel (added in Linux 4.8) that runs BPF programs at the earliest possible point in the networking stack — before memory allocation (sk_buff allocation), before protocol stack processing — enabling extremely high-performance packet processing at millions of packets per second per CPU core.

## Key Characteristics

### Performance Advantages
- **Early execution**: Runs before sk_buff allocation, directly on DMA buffer
- **No memory allocation in fast path**: Reduces latency dramatically
- **Chip-to-chip DMA**: Direct packet buffer access without copying
- **Batching support**: Process multiple packets per invocation

### Program Types
- `XDP_PASS` — Pass packet up the stack
- `XDP_DROP` — Drop packet (DDoS mitigation, firewall)
- `XDP_REDIRECT` — Redirect to another interface or AF_XDP socket
- `XDP_TX` — Transmit on same interface (bump-on-wire)

### Architecture

```
NIC DMA → XDP Program (eBPF) → [XDP_DROP | XDP_PASS | XDP_REDIRECT | XDP_TX]
```

## Related Concepts

- [[linux-ebpf-overview]] — eBPF fundamentals
- [[linux-network-tc-ebpf-direct-action]] — TC Direct Action (often used with XDP)
- [[kernel-bypass-dpdk]] — DPDK (alternative kernel bypass solution)
- [[load-balancing]] — L4 load balancing using XDP

## Sources
- [[bookmark-sdn-guide]] — SDN Guide eBPF/XDP section
