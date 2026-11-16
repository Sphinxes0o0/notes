---
type: entity
tags: [ids, ips, intrusion-detection, security, snort, suricata, zeek]
created:2026-06-08
sources: [github-snort3-service-inspectors]
---

# Intrusion Detection Systems (IDS/IPS)

## 定义

入侵检测系统（IDS）是监控网络流量或主机行为以识别恶意活动的安全系统。IDS分为 NIDS（Network IDS，如 Snort/Suricata/Zeek）和 HIDS（Host IDS，如 OSSEC/Wazuh）。IPS（Intrusion Prevention System）是 IDS 的主动版本，可在 inline模式下阻断恶意流量。

##关键要点

- **两类部署**：NIDS（网络层镜像）vs HIDS（主机日志/调用）
- **检测方法**：signature-based（Snort规则）+ anomaly-based（统计/ML）
- **NIDS代表**：Snort3（Sourcefire/Cisco）、Suricata（OISF）、Zeek/Bro（NSM）
- **IPS模式**：inline（TAP/分光器）可主动阻断；passive 仅告警
- **HIDS代表**：OSSEC、Wazuh、Samhain、fail2ban
- **现代扩展**：NDR（Network Detection + Response）+ XDR（跨域关联）

##核心概念

- **False Positive vs False Negative**：误报 vs漏报权衡
- **Rule tuning**：规则调优（disable noisy rules、thresholding）
- **Snort3**：插件化、C++17 重写、多线程 pig
- **Suricata**：多线程、HTTP/SSL/TLS协议级解码、lua JIT
- **Zeek**：脚本化（Bro policy）、协议解析 → conn.log / http.log
- **EVT/ETD**：事件/威胁关联（TheHive/MISP）
- **Inline vs Passive**：Bypass NIC、Cisco IPS bypass

## 相关页面

- [[entities/linux/snort3/snort3-framework]] — Snort3框架
- [[entities/linux/snort3/snort3-detection-engine]] — 检测引擎
- [[entities/linux/snort3/network-security-monitoring]] — NSM
- [[entities/linux/snort3/snort3-net-inspectors]] — net inspectors
- [[entities/security/network-intrusion-detection]] — NIDS综述
