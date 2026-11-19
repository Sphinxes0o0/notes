---
type: entity
tags: [nsm, network-security-monitoring, ids, ids-survey, security]
created:2026-06-08
sources: [paper-think-ebpf-for-kernel-security-monitoring-falco-at-apple]
---

# Network Security Monitoring (NSM)

## 定义

网络安全管理（NSM，Network Security Monitoring）由 Richard Bejtlich提出的安全方法论：通过持续收集网络流量数据（PCAP、流记录、IDS告警、HTTP日志等），对网络进行**检测-响应-取证**闭环。NSM强调"集合化监控"（collection-centric），与"入侵防御"（IPS）形成互补。

##关键要点

- **三个阶段**：检测（Detection）/响应（Response）/取证（Forensics）
- **三类数据源**：alert（IDS告警）/ full content（PCAP）/ session data（流记录）
- **工具链**：Snort/Suricata（IDS）+ Argus（流）+ tcpdump（PCAP）+ ELK（可视化）
- **Bejtlich原则**：监测 >阻塞、收集 > 控制
- **NTA（Network Traffic Analysis）**：NSM 的现代商业版（Gartner术语）
- **EDR + NDR**：端点检测响应 + 网络检测响应

##核心概念

- **PCAP retention**：保留原始包（取证核心）
- **NetFlow/sFlow**：流量画像（行为分析）
- **IDS signature**：基于已知模式的告警（Snort/Suricata规则）
- **anomaly detection**：基于统计/ML 的异常（无签名）
- **NSM console**：Bro/Zeek logs + ELK stack
- **threat hunting**：基于 NSM数据的主动威胁搜索
- **eBPF NSM**：Falco、Tracee（云原生 NSM）

## 相关页面

- [[entities/linux/snort3/network-monitoring]] —网络监控基础
- [[entities/linux/snort3/intrusion-detection-systems]] — IDS总览
- [[entities/linux/snort3/snort3-net-inspectors]] — Snort3 inspectors
- [[entities/security/network-intrusion-detection]] — NIDS综述
- [[sources/paper-think-ebpf-for-kernel-security-monitoring-falco-at-apple]] — Falco NSM
