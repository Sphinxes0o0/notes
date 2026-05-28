---
type: source
source-type: pdf
title: "PTPsec: Securing PTP Against Time Delay Attacks (INFOCOM 2024)"
author: Andreas Finkenzeller, Oliver Butowski, Emanuel Regnath, Mohammad Hamad, Sebastian Steinhorst
date: 2024
size: medium
path: raw/PDFs/papers/2024-INFOCOM-PTPsec.pdf
summary: "INFOCOM 2024: 利用循环路径不对称分析检测和缓解IEEE 1588 PTP时间同步协议中的微秒级延迟攻击"
tags: [security, ptp, ieee1588, time-sync, tsn, smart-grid, delay-attack]
created: 2024
---
# PTPsec: Securing PTP Against Time Delay Attacks

## 核心内容

**Authors:** Andreas Finkenzeller, Oliver Butowski, Emanuel Regnath, Mohammad Hamad, Sebastian Steinhorst | IEEE INFOCOM 2024

### 背景

PTP (Precision Time Protocol, IEEE 1588) 是智能电网、TSN（时间敏感网络）、5G 同步等场景的核心时间同步协议，支持微秒级精度。PTP 假设双向路径延迟对称，但该假设在面对恶意攻击时并不成立。

### 攻击模型

- **静态延迟攻击** — 攻击者通过延长光纤、注入额外延迟等方式引入恒定不对称延迟，导致时钟偏移恒定值
- **增量延迟攻击** — 延迟逐渐增加，使时钟缓慢漂移（更难检测，比静态攻击更隐蔽）

### PTPsec 方案

**核心创新：** 利用网络冗余路径进行循环 RTT 测量，检测并补偿路径不对称。

1. **Meas 消息** — PTPsec 新引入的测量消息，通过冗余路径往返
2. **循环 RTT 测量** — Sync 消息通过被监控路径 P0（主路径），Meas 消息通过可信路径 P1（冗余路径）
3. **路径不对称计算** — 两轮 RTT 测量值推导当前路径不对称系数 α
4. **延迟补偿** — 根据 α 值动态调整时钟偏移计算

**关键技术：**
- 冗余路径发现算法（支持任意网络拓扑）
- 与 IEEE 1588-2019 Annex P（四管齐下安全框架）集成
- 硬件测试验证平台（支持微秒级精确攻击注入）

### 实验结果

- 所有攻击场景可被可靠检测
- 静态和增量延迟攻击均可缓解
- 检测时间最小化，精度达微秒级

### 相关工作对比

| 方案 | 检测能力 | 缓解能力 | 适用场景 |
|------|---------|---------|---------|
| PTPsec | 全部攻击 | 完整缓解 | 冗余路径网络 |
| IEEE 1588-2019 Annex P | 依赖硬件时间戳 | 部分缓解 | 安全扩展场景 |
| 传统 PTP | 无 | 无 | 基础同步 |

## 关键引用

> "Delay attacks exploit and violate the protocol's assumption of symmetric path delays by maliciously introducing unidirectional delays into the network."

> "PTPsec is the first protocol that efficiently detects and mitigates time delay attacks."

## 相关页面

- [[security-index]] — 安全模块入口
- [[kernel-protocols-index]] — 网络协议与物理层
- [[entities/linux/ebpf/ebpf-security]] — eBPF 网络安全监控
- [[sources/notes-net]] — Linux 网络子系统
- [[sources/notes-security]] — 安全工具笔记
