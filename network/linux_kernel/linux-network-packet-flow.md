---
title: "Linux Network Packet Flow"
---
# Linux Network Packet Flow

## RX Path (Receive)
1. NIC DMA → Ring Buffer (sk_buff pointers, not data)
2. NIC triggers hardware interrupt
3. IRQ handler sets NET_RX_SOFTIRQ, returns
4. ksoftirqd → `net_rx_action()` → driver poll function
5. Driver fetches frames from Ring Buffer → sk_buff
6. Protocol stack: `ip_rcv` → netfilter PREROUTING → `tcp_v4_rcv`/`udp_rcv`
7. Packet → socket receive queue
8. App woken via `sk_data_ready` callback

## TX Path (Send)
1. App `sendmsg` → `sk_write_queue`
2. TCP segmentation + header construction (`tcp_transmit_skb` clones skb)
3. IP layer routing (`ip_queue_xmit`) + fragmentation
4. netfilter hooks (POSTROUTING)
5. qdisc queue (`txqueuelen`)
6. Driver Ring Buffer TX
7. SoftIRQ (NET_TX_SOFTIRQ) for completion cleanup

## Key Data Structures
- **Ring Buffer**: FIFO between NIC and IP, contains sk_buff pointers
- **NAPI**: Poll-based batch processing, reduces interrupt overhead
- **sk_buff**: Socket kernel buffer, holds packet data + metadata through stack
- **SoftIRQ (ksoftirqd)**: Per-CPU threads handling deferred interrupt work

## Critical Tunables
| Parameter | Default | Purpose |
|-----------|---------|---------|
| `netdev_max_backlog` | 1000 | Per-CPU queue before protocol stack |
| `netdev_budget` | 300 | Max packets per softirq iteration |
| `txqueuelen` | 1000 | qdisc send queue length |

## Monitoring
- `/proc/net/softnet_stat`: Col2=dropped, Col3=time_squeeze (budget exhaustion)
- `ethtool -S`: rx_fifo_errors, rx_dropped, overruns
