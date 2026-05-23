---
type: entity
tags: [networking, kernel-bypass, dpdk, performance, packet-processing]
created: 2026-05-23
sources: [pdf-cpp-perf-engineering]
---

# Kernel Bypass for High-Speed Packet Processing

## Definition

Kernel bypass is a set of techniques that allow network packet processing to occur without involving the operating system kernel's networking stack. By moving packet I/O to user space, kernel bypass eliminates context switches, interrupt overhead, and protocol processing that limit throughput to ~1 Mpps on standard Linux, enabling 10-80 Mpps on similar hardware.

## Motivation

Standard Linux network stack overhead per packet:
- NIC → Driver → L2 → L3 → L4 → Application
- Each packet traverses interrupt handlers, socket buffer allocation, multiple protocol layers
- At 10G/40G/100G line rates, per-packet overhead becomes the bottleneck
- Applications requiring wire-speed throughput: software routers, firewalls, load balancers, NFV, AI inference networking

## Key Approaches

### 1. User-Space Packet Processing (DPDK)
**Data Plane Development Kit (DPDK):**
- **Poll-mode drivers (PMD):** Instead of interrupt-driven RX, applications poll NIC receive queues in a tight loop
- **Hugepages:** 2MB/1GB pages reduce TLB misses for large packet buffers
- **NUMA-aware:** Memory and threads bound to specific sockets for local memory access
- **Lockless rings:** Multi-producer/multi-consumer rings for inter-core communication
- **Userspace I/O (UIO/vfio):** Direct NIC register access from user space

| Feature | DPDK | Netmap |
|---------|------|--------|
| Approach | Poll-mode drivers | Memory-mapped NIC buffers |
| Performance | 10-80 Mpps | 10-20 Mpps |
| Complexity | High | Low |
| Features | Full framework | Lightweight |

### 2. User-Space Network Stacks (mTCP)
Full TCP/IP protocol stack implemented in user space, often combined with DPDK or Netmap for packet I/O:
- Eliminates kernel TCP/IP overhead
- Enables application-specific protocol optimizations
- Challenges: full API compatibility, integration with existing applications

### 3. In-Kernel Bypass (XDP/eBPF)
XDP (eXpress Data Path) attaches BPF programs at the NIC driver level — not a true bypass but avoids full stack traversal:
- Runs before `sk_buff` allocation
- Enables early packet filtering, forwarding, or dropping
- 10-20 Mpps achievable

## Trending Topics
- **SmartNICs:** Offload bypass processing to NIC hardware
- **Programmable switches (P4):** Protocol-independent packet processing
- **RDMA (InfiniBand/RoCE/iWARP):** Direct memory access between machines, bypassing both CPUs for data movement
- **DLSlime:** Point-to-point RDMA transfer for AI inference — one-sided semantics avoid CPU involvement

## Related Concepts
- [[entities/cpp/cpp-perf-optimization]] — CPU cache optimization, memory hierarchy awareness
- [[entities/cpp/cpp-llm-inference]] — LLM inference networking (RDMA for KV Cache transfer)

## Sources
- [[sources/pdf-cpp-perf-engineering]] — Kernel bypass theory slides
