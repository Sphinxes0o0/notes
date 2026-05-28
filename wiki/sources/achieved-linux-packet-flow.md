---
type: source
source-type: bookmark
title: "网络包的流转 — plantegg"
author: "plantegg"
date: 2019-05-24
url: "https://plantegg.github.io/2019/05/24/网络包的流转/"
summary: "Linux网络包从网卡DMA到socket队列的完整流转路径，详细分析Ring Buffer、NAPI、sk_buff、SoftIRQ各环节"
tags: [linux, networking, kernel, packet-flow, napi, skbuff, softirq]
created: 2026-05-28
---

# 网络包的流转 — plantegg

## 核心内容

### 关键数据结构

| 结构 | 作用 | 位置 |
|------|------|------|
| **Ring Buffer** | NIC与IP层之间的FIFO队列，含sk_buff指针 | DMA环形缓冲区 |
| **sk_buff** | Socket kernel buffer，贯穿栈的 packet data + metadata | 核心数据结构 |
| **NAPI** | 高负载时轮询批处理，空闲时中断 | 替代传统中断驱动 |
| **SoftIRQ (ksoftirqd)** | 每CPU内核线程处理延迟中断工作 | 软中断处理 |

### 接收路径（RX）

```
1. NIC DMA → Ring Buffer内存（sk_buff指针）
2. NIC触发硬件中断
3. 中断处理程序设置 NET_RX_SOFTIRQ 标志
4. ksoftirqd 执行 net_rx_action()
5. 驱动从 Ring Buffer 取帧 → sk_buff
6. 协议栈处理：ip_rcv → netfilter PREROUTING → tcp_v4_rcv/udp_rcv
7. 数据包放入 socket 接收队列
8. 应用通过 sk_data_ready 回调被唤醒
```

### 发送路径（TX）

```
1. 应用 sendmsg → sk_write_queue
2. TCP分片 + 头部构造（tcp_transmit_skb 克隆 skb）
3. IP层路由（ip_queue_xmit）+ 分片
4. netfilter hooks（POSTROUTING）
5. qdisc 队列（txqueuelen）
6. 驱动 Ring Buffer TX
7. SoftIRQ（NET_TX_SOFTIRQ）ACK后清理
```

### 关键可调参数

| 参数 | 默认值 | 作用 |
|------|--------|------|
| `netdev_max_backlog` | 1000 | 协议栈前每CPU队列 |
| `netdev_budget` | 300 | 每次softirq最大处理包数 |
| `txqueuelen` | 1000 | qdisc发送队列长度 |
| `tcp_rmem/tcp_wmem` | varies | TCP收/发缓冲区大小 |

### 监控点

- `/proc/net/softnet_stat`: Column 2=dropped, Column 3=time_squeeze
- `ethtool -S`: rx_fifo_errors, rx_dropped, overruns
- `netstat -sn`: 因socket buffer满而丢弃的包

## 关键引用

> "Ring Buffer 是 NIC 和 IP 层之间的 FIFO 队列，包含的是 sk_buff 描述符指针，不是实际数据"

> "SoftIRQ (ksoftirqd) 是每CPU内核线程，处理延迟中断工作。硬中断在同一CPU触发软中断。"

## 相关页面

- [[entities/linux/network/net-stack-deep-dive]] — 网络栈全路径深度分析
- [[entities/linux/kernel/net/linux-kernel-net-subsystem]] — 网络子系统框架
- [[entities/linux/kernel/net/skbuff-deep-dive]] — SKB内存管理详解
- [[entities/linux/network/linux-network-protocols]] — TCP/UDP协议实现
