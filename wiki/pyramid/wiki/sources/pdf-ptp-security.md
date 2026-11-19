---
type: source
source-type: pdf
title: "PTPsec: Securing Precision Time Protocol Against Delay Attacks"
author: "Infocom Paper"
date: 2026-05-25
size: small
path: raw/PDFs/papers/
summary: "PTPsec — 基于IEEE 1588-2019的安全时间同步协议，抵御时间延迟攻击"
tags: [security, ptp, time-sync, ieee1588, delay-attack]
created: 2026-05-28
---

# PTPsec: Securing Precision Time Protocol Against Delay Attacks

## 核心内容

PTPsec是基于IEEE 1588-2019标准的安全时间同步协议，通过循环路径不对称性分析(Cyclic Path Asymmetry Analysis)检测和抵御针对PTP(精确时间协议)的时间延迟攻击。

## 关键要点

- **时间同步安全的重要性**: Smart Grids、TSN、5G网络依赖精确时间
- **PTPsec解决方案**: 路径不对称性分析检测延迟攻击
- **攻击模型**: 时间延迟攻击可导致目标时钟偏差

## 相关实体

- [[entities/linux/security/linux-security-ptpsec]] — Linux PTPsec 实现
