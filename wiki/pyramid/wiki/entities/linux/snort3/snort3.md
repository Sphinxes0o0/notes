---
type: entity
tags: [snort, ids, ips, intrusion-detection, network-security]
created: 2026-05-28
sources: [github-snort3-framework]
---

# Snort3

## 定义

Snort3 是一个模块化、可扩展的开源网络入侵检测/防御系统（IDS/IPS），基于插件化架构实现协议解析、规则匹配和告警日志功能。

## 核心组件

- **Detection Engine**: 快速模式匹配 (MPSE)、Detection Option Tree
- **Codecs**: 协议解析 (Ethernet, IP, TCP, UDP, etc.)
- **Inspectors**: 包检查器 (对应 Snort2 的 preprocessors)
- **Actions**: 动作系统 (alert, log, drop, block, reject)
- **Connectors**: 进程间通信 (file/tcp/unixdomain connector)

## 相关概念

- [[entities/linux/snort3/snort3-framework]] — Snort3 核心框架
- [[entities/linux/snort3/snort3-detection-engine]] — 检测引擎
- [[entities/linux/snort3/snort3-codecs]] — 协议编解码
- [[entities/security/intrusion-detection-system]] — 入侵检测系统概述
