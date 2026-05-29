---
type: entity
tags: [linux, ebpf, beginner, architecture]
created: 2026-05-29
sources: [bookmark-sdn-guide, pdf-ebpf-basics]
---

# eBPF Overview

## Definition

eBPF (extended Berkeley Packet Filter) is a Linux kernel technology (3.18+) that enables sandboxed programs to run in kernel space with native execution speed, attached to configurable hook points. It evolved from classic BPF (network packet filtering) into a general-purpose in-kernel compute platform.

## eBPF vs XDP

| Feature | eBPF (general) | XDP |
|---------|----------------|-----|
| Hook point | Various (kprobes, tracepoints, etc.) | Earliest at NIC driver |
| sk_buff | Already allocated | Not yet allocated |
| Use case | Observability, tracing, security | High-speed packet processing |
| Performance | Moderate overhead | Near-wire speed |

## Key Components

- **BPF Verifier** — Static analysis of BPF programs before loading
- **eBPF Maps** — Key-value store for program state
- **Helper Functions** — Kernel-exposed functions callable from BPF
- **XDP** — eBPF for networking at the NIC level

## Related Concepts

- [[linux-ebpf-xdp]] — XDP (eBPF for high-speed networking)
- [[linux-network-tc-ebpf-direct-action]] — TC Direct Action mode
- [[linux-ebpf-security]] — eBPF for security enforcement

## Sources
- [[bookmark-sdn-guide]]
- [[pdf-ebpf-basics]]
