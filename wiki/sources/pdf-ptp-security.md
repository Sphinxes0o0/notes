---
type: source
tags: [network-security, ptp, time-sync, smart-grid, tsn]
created: 2026-05-23
sources:
title: "PTPsec: Securing PTP Against Time Delay Attacks Using Cyclic Path Asymmetry Analysis"
author: "Andreas Finkenzeller, Oliver Butowski, Emanuel Regnath, Mohammad Hamad, Sebastian Steinhorst"
date: 2024
size: medium
path: raw/PDFs/papers/2024-INFOCOM-PTPsec.pdf
summary: "IEEE INFOCOM 2024论文：基于循环路径不对称分析的PTP时间同步防时间延迟攻击协议 PTPsec，利用冗余路径的RTT测量检测和缓解微秒级延迟攻击"
---

# PTPsec: Precision Time Protocol Security

## 核心内容

PTP (IEEE 1588) 是智能电网、TSN、5G 网络等微秒级时间同步的关键协议。PTP 假设路径延迟对称，但时间延迟攻击（恶意引入单向延迟）可导致时钟偏移而不被检测。

### 攻击模型

- **静态延迟攻击** — 攻击者通过延长光纤等方式引入恒定不对称延迟
- **增量延迟攻击** — 延迟逐渐增加，使时钟缓慢漂移（更隐蔽）

### PTPsec 方案

**核心创新：** 利用网络冗余路径进行循环 RTT 测量，检测并补偿路径不对称。

1. **Meas 消息** — PTPsec 新引入的测量消息，通过冗余路径往返
2. **循环 RTT 测量** — Sync 消息通过被攻击路径 P0（主路径），Meas 消息通过可信路径 P1（冗余路径）
3. **路径不对称计算** — 两轮 RTT 测量值推导当前路径不对称 α
4. **延迟补偿** — 根据 α 值调整时钟偏移计算

**关键技术：**
- 冗余路径发现算法（任意网络拓扑）
- 与 IEEE 1588-2019 Annex P（四管齐下安全框架）集成
- 硬件测试验证平台（支持微秒级精确攻击注入）

### 实验结果

- 所有攻击场景可被可靠检测
- 静态和增量延迟攻击均可缓解
- 检测时间最小化，精度达微秒级

## 关键引用

> "Delay attacks exploit and violate the protocol's assumption of symmetric path delays by maliciously introducing unidirectional delays into the network."

> "PTPsec is the first protocol that efficiently detects and mitigates time delay attacks."

## 相关页面

- [[kernel-protocols-index]] — 网络协议与物理层
- [[entities/linux/ebpf/ebpf-security]] — 网络安全监控
- [[sources/notes-security]] — 安全工具笔记
