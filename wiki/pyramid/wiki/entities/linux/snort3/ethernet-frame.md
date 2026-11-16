---
type: entity
tags: [networking, ethernet, frame, l2, protocol, packet-format]
created:2026-06-08
sources: [github-snort3-codecs]
---

# Ethernet II Frame

## 定义

Ethernet II帧（又称 DIX帧）是 IEEE802.3之前/并存的最常见以太网帧格式，由目的 MAC（6字节）+源 MAC（6字节）+ EtherType（2字节）+ Payload（46-1500字节）+ FCS（4字节）组成。EtherType >1500标识上层协议（如0x0800 = IPv4、0x86DD = IPv6、0x0806 = ARP）。

##关键要点

- **最小帧64字节**：14字节头 +46字节 payload +4字节 FCS
- **最大帧1518字节**（无 VLAN）/1522（VLAN tag）/9022（Jumbo Frame）
- **MAC 地址**：48 位，前24 位 OUI（厂商），后24 位 NIC序列
- **广播**：`FF:FF:FF:FF:FF:FF`
- **VLAN (802.1Q)**：4字节插入（TPID0x8100 + TCI）
- **MTU**：1500 默认，影响 IP 分片

##核心概念

- **EtherType**：标识上层协议，常见0x0800 IPv4 /0x0806 ARP /0x86DD IPv6 /0x8864 PPPoE
- **FCS（CRC-32）**：帧校验序列，检测物理层错误
- **Preamble + SFD**：物理层前导码（7字节1010... +1字节10101011）
- **Jumbo Frame**：>1500字节（如9000），数据中心优化
- **Promiscuous mode**：网卡接收所有帧（sniffer模式）
- **Packet Codec**：Snort3 codec 按 EtherType 分派到 IP/ARP/IPv6 decoder

## 相关页面

- [[entities/linux/snort3/snort3-codecs]] — Snort3 Codec
- [[entities/linux/snort3/snort3-packet-processing]] — 包处理
- [[entities/linux/network/net-stack-overview]] — 网络栈
- [[entities/linux/network/osi-physical-layer]] — OSI物理层
