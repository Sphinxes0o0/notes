---
type: entity
tags: [networking, monitoring, observability, nsm, netflow, sflow]
created:2026-06-08
sources: [paper-netmap-interface-introduction]
---

# Network Monitoring

## 定义

网络监控（Network Monitoring）是通过被动观察网络流量来收集可见性数据（性能指标、安全事件、流量画像）的技术与方法论。包括流量镜像（port mirroring/TAP）、流量采集（NetFlow/sFlow/IPFIX）、包捕获（libpcap/nfqueue/AF_PACKET/XDP）、协议解析（Bro/Zeek、Snort）等多种手段，是运维和安全团队的"眼睛"。

##关键要点

- **三类数据源**：流（NetFlow/sFlow/IPFIX）+ 包（pcap/PCAP-NG）+ 元数据（CDP/LLDP/SNMP）
- **镜像方式**：Port mirroring（TAP/SPAN）、Active tap、In-line TAP
- **采集工具**：tcpdump、Wireshark、ntopng、Argus、Suricata
- **流记录**：5-tuple +字节/包计数 +持续时间 + TCP flag
- **实时分析**：ClickHouse + Grafana、流式处理（Kafka + Flink）
- **IDS/IPS**（侧载）：Snort/Suricata/Zeek协议解析+告警

##核心概念

- **NetFlow v5/v9/IPFIX**：Cisco主导的流格式，sampler按比例采样
- **sFlow**：随机采样（包级 +计数器级）
- **SPAN port**：交换机端口镜像（可能丢包）
- **Network TAP**：物理分光器（不丢包 + 单向）
- **libpcap**：跨平台包捕获库
- **AF_PACKET / XDP**：Linux 内核态高性能抓包
- **pcap-NG**：扩展 pcap格式（多接口 + 元数据）

## 相关页面

- [[entities/linux/snort3/network-security-monitoring]] — NSM安全监控
- [[entities/linux/snort3/snort3-net-inspectors]] — Snort3 net inspectors
- [[entities/linux/snort3/packet-capture]] —包捕获技术
- [[entities/linux/snort3/snort3-packet-processing]] — Snort3包处理
- [[sources/paper-netmap-interface-introduction]] — netmap高性能捕获
