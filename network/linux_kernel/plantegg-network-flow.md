---
title: "plantegg: Linux Network Packet Flow"
description: "This is a Chinese blog post explaining Linux network stack packet flow in detail."
---
# plantegg: Linux Network Packet Flow

## Core Insight
This is a Chinese blog post explaining Linux network stack packet flow in detail.

## Key Topics
- Ring Buffer: FIFO between NIC and IP layer, contains sk_buff descriptors (pointers, not data)
- NAPI: Poll-based mechanism for batch packet processing under high load
- sk_buff: Fundamental socket kernel buffer data structure
- SoftIRQ (ksoftirqd): Per-CPU kernel threads handling deferred interrupt work
- DMA: Hardware logic for direct memory transfer without CPU

## Receive Path
NIC DMA → Ring Buffer → Hard IRQ → SoftIRQ → driver poll → net_rx_action → sk_buff → ip_rcv → netfilter → tcp_v4_rcv → socket queue

## Send Path
sendmsg → sk_write_queue → TCP segmentation → ip_queue_xmit → netfilter POSTROUTING → qdisc → Ring Buffer TX → SoftIRQ cleanup

## Important Parameters
- `netdev_max_backlog` (1000): Per-CPU queue before protocol stack
- `netdev_budget` (300): Max packets per softirq iteration
- `txqueuelen` (1000): qdisc send queue length
