# 3.3 Linux 内核网络框架

## 概述

Linux 内核网络框架是整个 Linux 网络协议栈的核心，它管理着数据包从网卡到用户空间应用程序的整个流程。

## Netfilter 钩子

Netfilter 在网络协议栈埋下了 5 个钩子，用来干预 Linux 网络通信：

- **PREROUTING**：数据包进入协议栈即触发，用于修改目标 IP（DNAT）
- **FORWARD**：数据包不发给本机时触发，本机作为路由器中转处理
- **INPUT**：数据包发给本机时触发，处理发往本机的包
- **OUTPUT**：本地进程处理后、IP 路由前触发，可限制本机访问
- **POSTROUTING**：数据包出协议栈前触发，用于源地址转换（SNAT）

## 连接跟踪

conntrack（连接跟踪）模块监控 Linux 内核中的通信状态，不仅跟踪 TCP 连接，还跟踪 UDP、ICMP 等其他连接类型。

## 相关章节

- [3.3.1 Netfilter 的 5 个钩子](./netfilter.html)
- [3.3.2 数据包过滤工具 iptables](./iptables.html)
- [3.3.3 连接跟踪模块 conntrack](./conntrack.html)
