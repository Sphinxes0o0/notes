---
title: "TCP Bypass Notes"
description: "Kernel TCP/IP provides: error detection, in-order delivery, flow/congestion control. Bypass alternatives needed for ultra-low-latency (HFT, trading systems)."
---
# TCP Bypass Notes

## Why Bypass TCP/IP?
Kernel TCP/IP provides: error detection, in-order delivery, flow/congestion control. Bypass alternatives needed for ultra-low-latency (HFT, trading systems).

## Zero-Copy
- Uses DMA to transfer data directly from file buffer cache to network
- Eliminates user-kernel data copies
- Mainstream implementation: file-to-socket transfers only

## NIC Optimizations
- **Interrupt coalescing**: Reduces CPU load but increases latency
- **NAPI**: Poll under high load, return to interrupts when idle
- **Scatter-gather**: DMA across multiple memory blocks
- **RSS**: Distribute RX across multiple CPUs
- **Offloads**: TCP segmentation, checksum, Large Receive

## Four Bypass Options
1. **iWARP** — RDMA over Ethernet
2. **RoCE (Converged Ethernet)** — Data Centre Enhanced Ethernet
3. **InfiniBand** — Converged interconnect
4. **Open-MX** — Myricom API
5. **GAMMA** — Genoa Active Message Machine

All operate within OFED (Open Fabrics Enterprise Distribution) stack.

## Limitations
- Dropping IP only works on Layer 2 networks
- Ethernet has no guaranteed delivery
- Broadcast issues beyond ~1024 addresses
- Namespace and scalability concerns remain
