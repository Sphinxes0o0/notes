---
type: source
source-type: github
tags: [security, tools]
path: raw/github/notes/security/
created: 2026-05-22
---

# 安全工具笔记

## Overview

安全工具架构分析笔记，涵盖 Masscan（高速端口扫描器）、Falco（Kubernetes 运行时安全监控）、Snort 3（网络入侵检测系统）。重点分析各工具的架构设计、核心算法和实现机制。

## Key Topics

- **Masscan**：互联网规模高速端口扫描器
  - 性能：单台机器可达 1000 万 pps
  - 架构：异步发送/接收线程对，自定义用户态 TCP/IP 协议栈
  - 随机化：BlackRock Feistel 网络 + SipHash24
  - 速率控制：Token Bucket 算法（256 桶）
  - SYN Cookie 机制：无状态验证
  - Banner 抓取：SSH、HTTP、SSL、SMB 等多协议
- **Falco**：Kubernetes 云原生运行时安全监控，基于规则检测异常行为
- **Snort 3**：网络入侵检测系统（NIDS），规则驱动，支持协议解码、内容匹配、缓冲区溢出检测

## Related Entities

- [[entities/security]] — 安全工具实体页（Masscan、Falco、Snort 架构详解）
- [[entities/sys]] — 网络协议栈基础
