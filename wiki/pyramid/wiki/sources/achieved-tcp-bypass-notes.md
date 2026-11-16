---
type: source
source-type: bookmark
title: "TCP Bypass Notes"
author: "Shi Shougang"
date: 2016
url: "https://wiki.dreamrunner.org/public_html/Low_Latency_Programming/TCP-Bypass-Notes.html"
summary: "超低延迟网络技术：TCP Bypass技术（RDMA/iWARP/RoCE/InfiniBand）与零拷贝、DMA、网卡优化技术"
tags: [linux, networking, tcp, low-latency, rdma, infiniband, iwarp]
created: 2026-05-28
---

# TCP Bypass Notes

## 核心内容

### 为什么需要Bypass TCP/IP

Kernel TCP/IP提供：错误检测纠正、顺序传输、流量/拥塞控制。但在HFT（高频交易）等超低延迟场景下，传统TCP/IP开销过大。

### Zero Copy（零拷贝）

- 使用DMA直接从文件缓冲池传输到网络
- 消除用户态-内核态数据拷贝
- **主流实现仅限 file-to-socket 传输**

### NIC优化技术

| 技术 | 作用 | 权衡 |
|------|------|------|
| **Interrupt Coalescing** | 减少CPU负载 | 增加延迟 |
| **NAPI** | 高负载时轮询，空闲时中断 | 批处理效率 |
| **Scatter-Gather** | DMA跨多内存块传输 | 支持分散数据 |
| **RSS** | 多CPU分发接收处理 | 负载均衡 |
| **Offloads** | TCP分片、校验和、Large Receive | 减轻CPU负担 |

### Five Bypass方案

1. **iWARP** — RDMA over Ethernet（基于TCP）
2. **RoCE** — Converged Enhanced Ethernet（无损网络）
3. **InfiniBand** — 融合互联
4. **Open-MX** — Myricom API
5. **GAMMA** — Genoa Active Message Machine

所有方案均基于 **OFED (Open Fabrics Enterprise Distribution)** 软件栈。

### Bypass的局限性

- 仅限Layer 2网络（无法跨IP路由）
- Ethernet本身无可靠传输保证
- 广播扩展性差（超过~1024地址）
- 命名空间和扩展性问题仍存在

## 关键引用

> "TCP/IP provides: error detection/correction, in-order delivery, flow/congestion control. Replacement requires alternatives to these functions."

> "Ethernet provides no guaranteed delivery and faces broadcast issues beyond ~1024 addresses."

## 相关页面

- [[entities/linux/network/net-stack-deep-dive]] — Linux网络栈全路径
- [[entities/linux/network/linux-network-protocols]] — TCP协议实现
- [[entities/linux/ebpf/ebpf-networking]] — eBPF网络（现代内核可扩展性方案）
