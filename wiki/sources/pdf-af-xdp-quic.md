---
type: source
tags: [ebpf, xdp, af-xdp, quic, networking, bilibili]
source-type: pdf
created: 2026-05-23
sources: [pdf-af-xdp-quic]
title: "AF_XDP with QUIC Practice - Bilibili"
author: "Bilibili Network Protocol Team"
date: 2024
size: small
path: raw/github/notes/resources/docs/networking/bilibili_af_xdp_quic_practice.pdf
summary: "B站网络协议组的技术分享：使用 AF_XDP 技术优化 QUIC 网关收发包效率，减少 CPU 负载，实现在线视频 CDN 场景的降本增效"
---

# AF_XDP with QUIC Practice (Bilibili)

## 背景

B站自建视频 CDN 下行全量部署了基于 QUIC/HTTP/3 的网关服务。QUIC 较 TCP 有更好的 QoE/QoS 指标，但 UDP 收发包效率低，QUIC 协议栈复杂导致 CPU 负载更高。

## AF_XDP 技术

AF_XDP 是 Linux 内核中高性能数据包处理的地址族，结合 XDP 程序使用 `XDP_REDIRECT` + `bpf_redirect_map()` 将数据帧重定向到用户空间。

### 核心组件

- **AF_XDP Socket (xsk)** — 类似传统 socket，含 RX ring 和 TX ring
- **UMEM** — 用户空间分配的共享内存池（通过 mmap）
- **FILL ring** — 用户提供收包缓冲区地址
- **COMPLETION ring** — 内核返回发包完成状态

### 工作流程

1. 用户将收包地址填入 FILL ring
2. 内核消费 FILL ring，收包后将地址放入 xsk RX ring
3. 用户消费 RX ring 获取数据帧
4. xsk 绑定到特定网卡队列，接收数据通过 XDP_REDIRECT 重定向

## QUIC 网关优化

- **优化效果**：AF_XDP bypass 内核协议栈，大幅降低 UDP 收发包 CPU 开销
- **技术选型**：排除 DPU 方案，选择 AF_XDP（纯软件方案，无需特殊硬件）
- **生产部署**：B站视频 CDN 边缘节点

## 相关页面

- [[entities/linux/ebpf/ebpf-xdp]] — XDP 快速数据路径
- [[entities/linux/ebpf/ebpf-networking]] — TC 与 Cilium
- [[kernel-net-index]] — Linux 网络子系统
