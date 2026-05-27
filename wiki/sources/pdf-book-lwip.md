---
type: source
source-type: pdf
title: "LwIP 协议栈源码详解"
author: "老衲五木（UESTC）"
date: 2018
size: small
path: raw/PDFs/books/LwIP 协议栈源码详解.pdf
summary: "UESTC老衲五木，LwIP轻量级TCP/IP协议栈源码学习笔记，覆盖内存/ARP/IP/TCP/API层"
---

# LwIP 协议栈源码详解

## 核心内容

UESTC 老衲五木的 LwIP 协议栈学习笔记，覆盖：

- **内存管理**：堆管理、内存池
- **底层网络接口**：netif、驱动接口
- **ARP 层**：地址解析协议
- **IP 层**：IPv4/IPv6 处理
- **TCP 层**：拥塞控制、滑动窗口、连接状态机
- **Socket API 层**：顺序编程接口

## 关键要点

- 重点讲解 LwIP 最常用部分（TCP 为主），不覆盖 UDP/DHCP/DNS/IGMP/SNMP/PPP
- 四个月学习笔记整理，适合作为 LwIP 源码阅读指南
- 轻量级嵌入式 TCP/IP 协议栈的典型实现参考

## 相关页面
- [[pdf-book-linux-high-perf-server]]
- [[pdf-book-linux-multi-thread-server]]
- [[pdf-book-ebpf-basics]]