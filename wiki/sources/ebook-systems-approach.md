---
type: source
source-type: ebook
title: "Computer Networks: A Systems Approach"
author: "Larry Peterson & Bruce Davie"
date: 2024
size: medium
path: raw/bookmarks/ebooks/systems-approach/
summary: "Foundational networking textbook covering layered architecture, switching, IP/TCP/UDP, congestion control, routing, SDN, and network security. 61 chapters, 225 diagrams."
---

# Computer Networks: A Systems Approach

## 核心内容

Peterson & Davie 所著经典网络教材，基于"系统方法"——强调组件交互与全局视角，而非孤立协议细节。最新版 6.2 涵盖云化、SDN、QUIC、BBR 等现代主题。

## 核心内容

### Chapter 1: Foundation
- **Layering & Protocols**: 协议图、封装、多路复用/解复用
- **OSI 7层模型**: 物理→数据链路→网络→传输→会话→表示→应用
- **Internet Architecture**: TCP/IP 架构，hourglass 窄腰设计哲学（IP 为中心）
- **Performance**: 带宽、延迟、吞吐量、排队论基础

### Chapter 2: Direct Links
- **Encoding/Framing**: NRZ, Manchester, 4B/5B, HDLC
- **Error Detection**: CRC, Hamming Code
- **Ethernet**: CSMA/CD, 帧格式, 交换机学习
- **Wireless**: 802.11, CSMA/CA

### Chapter 3: Internetworking
- **Switching**: Datagram / Virtual Circuit / Source Routing
- **IP**: Best-effort datagram, fragmentation/reassembly, 全局层次寻址
- **Subnetting/CIDR**: 可变长子网掩码，路由聚合
- **ARP/DHCP/ICMP**: 地址解析、动态配置、错误报告
- **Routing**: Distance-Vector (RIP), Link-State (OSPF), 转发表 vs 路由表
- **SDN**: 控制平面与数据平面分离，OpenFlow，网络操作系统

### Chapter 5: End-to-End Protocols
- **UDP**: 无连接数据报，简单解复用
- **TCP**: 可靠字节流，三次握手/四次挥手，滑动窗口，自适应重传
- **QUIC**: 用户空间 UDP 多路复用
- **RPC**: SunRPC, gRPC
- **RTP**: 实时传输协议

### Chapter 6: Congestion Control
- **Queuing Disciplines**: FIFO, Fair Queuing
- **TCP Congestion Control**: AIMD, Slow Start, Fast Retransmit/Recovery
- **Advanced CC**: ECN, RED, DCTCP, **BBR**
- **QoS**: Integrated Services (RSVP), Differentiated Services (EF/AF)

### Chapter 7: End-to-End Data
- **Serialization**: JSON, Protocol Buffers
- **HTTP Adaptive Streaming**: HLS, DASH
- **CDN & Caching**

### Chapter 8: Network Security
- **Threats & Trust**: 攻击面分析
- **Cryptography**: 对称加密 (AES), 公钥加密 (RSA), Authenticator/MAC
- **Key Distribution**: PKI, Diffie-Hellman
- **Authentication**: Needham-Schroeder, Kerberos
- **Systems**: TLS/SSL, IPsec, 802.11i, PGP, SSH, **Firewalls**

## 关键引用

### Hourglass Architecture
> "IP serves as the focal point — it defines a common method for exchanging packets among a wide collection of networks. Above IP there can be arbitrarily many transport protocols; below IP, arbitrarily many network technologies."

### Control Plane vs Data Plane
> "The control plane corresponds to the background processing required to control the network (e.g., running OSPF). The data plane corresponds to the per-packet processing required to move packets from input port to output port."

### BBR Congestion Control
> "BBR (Bottleneck Bandwidth and Round-trip propagation time) measures two fundamental parameters — BtlBw and RTprop — to maintain zero bottleneck queue."

## 相关页面

### Entities
- [[entities/linux/network/internet-architecture]] — IP, subnetting, CIDR, ARP, DHCP, tunnels
- [[entities/linux/network/network-switching]] — Datagram, virtual circuit, switching fabrics
- [[entities/linux/network/tcp-congestion-control]] — TCP CC: AIMD, slow start, fast retransmit, CUBIC
- [[entities/linux/network/quality-of-service]] — QoS, queuing disciplines, AQM, DiffServ
- [[entities/linux/network/sdn-networks]] — SDN, OpenFlow, control/data plane separation
- [[entities/linux/network/network-virtualization-security]] — VPN, tunneling, TLS/IPsec/firewalls
- [[entities/linux/network/congestion-control]] — BBR deep dive (existing)
- [[entities/linux/network/linux-network-protocols]] — Linux TCP/UDP/IP/BPF/XDP 实现

### Source Cross-References
- [[sources/arthurchiao-linux-net-stack]] — Linux 网络栈总览
- [[sources/arthurchiao-bbr-paper]] — BBR 论文解析
- [[sources/arthurchiao-tc-da-mode]] — TC eBPF direct-action (data plane)
- [[sources/reading-tcp-troubleshooting-plantegg]] — TCP 疑难问题
- [[sources/reading-linux-advanced-routing-tc]] — Linux 高级路由 & TC
- [[sources/reading-linux-tc-traffic-control]] — Linux TC 流量控制
