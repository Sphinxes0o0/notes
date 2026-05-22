---

type: entity
tags: [安全, 网络扫描, 入侵检测, 监控]
created: 2026-05-20


sources: [notes-tools]---

# 安全工具（Security Tools）

安全工具涵盖网络扫描、入侵检测、运行时安全监控等领域。

## 定义

安全工具是用于网络侦察、漏洞发现、入侵检测、安全监控的专用软件，本笔记重点关注 Masscan（高速端口扫描）、Falco（云原生运行时安全）、Snort（网络入侵检测系统）的架构分析。

## 关键要点

### Masscan — 互联网规模高速端口扫描器

**设计目标**：单台机器以每秒 1000 万数据包的速度扫描整个互联网。

**核心技术**：

| 技术 | 说明 |
|------|------|
| 语言 | C，无外部依赖 |
| 并发模型 | 异步发送/接收线程对 |
| TCP/IP 栈 | 自定义用户态协议栈（绕过内核） |
| 随机化 | BlackRock Feistel 网络 + SipHash24 |
| 速率限制 | Token Bucket 算法（256 桶） |
| IPC | DPDK FreeBSD bufring 锁无关 Ring Buffer |

**SYN Cookie 机制**：发送时不记录，接收时通过 Cookie 验证。无状态设计，极致性能。

**BlackRock 算法**：将单调递增索引 [0, N) 映射为均匀随机的一一对应排列，可逆且高效（适合 10Mpps）。

**扫描流程**：
1. transmit_thread() 批量发送 SYN 包（BlackRock 随机化目标选择 + SYN Cookie）
2. receive_thread() 接收响应（preprocess_frame 解析帧 + 重新计算 Cookie 验证）
3. 协议分发处理（TCP SYN-ACK → 创建 TCB → OPEN；UDP → Banner 抓取）

**Banner 抓取**：支持 SSH1/2, HTTP, FTP, SSL, SMB, SMTP, POP3, IMAP4, VNC, RDP, MEMCACHED, NTP, SNMP 等。

**跨平台抽象**：通过 `#ifdef WIN32` / `#ifndef` 等预处理实现 Linux/Windows/macOS/FreeBSD 兼容。

### Falco — Kubernetes 运行时安全监控

基于规则的行为监控，检测容器/容器编排系统中的异常活动。

### Snort 3 — 网络入侵检测系统（NIDS）

规则驱动的网络流量分析，支持协议解码、内容匹配、缓冲区溢出检测等。

## 相关概念

- [[entities/sys]] — 网络协议栈基础
- [[entities/midware]] — SOME/IP 等车载协议的安全机制

## 来源详情

- github-notes-security — 安全工具笔记（Masscan、Falco、Snort 架构分析）
