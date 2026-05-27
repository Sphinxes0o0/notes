---
type: source
source-type: pdf
title: "LwIP 协议栈源码详解"
author: "黄志洪, 廖文杰"
date: 2017
size: small
path: raw/PDFs/books/LwIP 协议栈源码详解.pdf
summary: "LwIP 轻量级 TCP/IP 协议栈源码分析：内存管理/网络接口/RAW API/线程模型"
---

# LwIP 协议栈源码详解

## 核心内容

- **整体架构**：协议分层、内存池、链表管理
- **网络接口**：netif 结构、驱动绑定、ARP/以太网帧处理
- **IP 层**：IP 转发、ICMP、分片重组
- **TCP/UDP**：状态机、滑动窗口、拥塞控制、RTT 计算
- **RAW API**：回调驱动编程模型、无操作系统使用方式
- **线程模型**：tcpip_thread、socket API 封装
- **内存管理**：pbuf 池、mem_heap/mem_pool

## 相关页面
- [[pdf-linux-net-server]]
- [[pdf-fast-packet-processing-xdp]]
- [[pdf-xdp-fast-packet]]