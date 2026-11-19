---
type: entity
tags: [linux, networking, network-stack, protocol-stack]
created: 2026-05-29
sources: [bookmark-sdn-guide]
---

# Linux Network Stack Overview

## Definition

The Linux network stack is the kernel's implementation of network protocol processing, from hardware interrupt handling through protocol parsing (Ethernet → IP → TCP/UDP) to socket API delivery. It spans the path from NIC driver to user-space sockets.

## Packet Path

```
NIC Hardware → Driver (DMA) → NAPI Poll → netif_receive_skb()
  → Protocol Layer (Ethernet → IP → TCP/UDP)
    → Socket Buffer (sk_buff) → User Space (recvmsg)
```

### Key Layers

| Layer | Component | Description |
|-------|-----------|-------------|
| 1 | NIC Driver | DMA, interrupts, NAPI polling |
| 2 | Network Core | netif_receive_skb, rx_handler |
| 3 | Protocol Stack | IP, TCP, UDP, SCTP |
| 4 | Socket Layer | BSD sockets, POSIX API |
| 5 | User Space | Application ( recvmsg / sendmsg ) |

## Alternative Paths

- **XDP**: Bypass most of stack, process at NIC level
- **AF_XDP**: Zero-copy path from NIC to user space
- **DPDK**: Kernel bypass for userspace packet processing

## Related Concepts

- [[linux-ebpf-xdp]] — eXpress Data Path (kernel bypass)
- [[kernel-bypass-dpdk]] — DPDK (full kernel bypass)
- [[load-balancing]] — Load balancing in the network stack

## Sources
- [[bookmark-sdn-guide]]
