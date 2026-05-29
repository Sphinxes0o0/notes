---
type: entity
tags: [security, ptp, time-sync, ntp, ieee1588, delay-attack, infocom, gnss]
created: 2026-05-25
sources: [pdf-ptp-security]
---

# PTPsec: Securing Precision Time Protocol Against Delay Attacks

## 定义
PTPsec是基于IEEE 1588-2019标准的安全时间同步协议，通过循环路径不对称性分析(Cyclic Path Asymmetry Analysis)检测和抵御针对PTP(精确时间协议)的时间延迟攻击。

## 关键要点

### 背景：时间同步安全的重要性
- **关键基础设施依赖精确时间**: Smart Grids、TSN (Time-Sensitive Networking)、5G网络
- **PTP在可信环境下可实现高精度**: 亚微秒级同步
- **当前威胁**: 时间延迟攻击(time delay attacks)可导致目标时钟偏差，破坏依赖时间的服务

### PTPsec解决方案
**Cyclic Path Asymmetry Analysis (循环路径不对称性分析)**:
1. 在任意网络中寻找冗余路径
2. 利用冗余路径测量路径不对称性
3. 检测同步路径上的不对称异常 → 识别延迟攻击
4. 提出安全PTP协议(PTPsec)实现

### 优势 vs 现有方案
- 缺乏与PTP协议的适当集成
- 缺乏可扩展性
- 缺乏微秒级精度的可靠评估
- PTPsec填补以上空白

### 实现验证
- 硬件测试平台（含攻击者模拟器）
- 攻击者可执行静态延迟攻击(static delay attacks)
- 在真实硬件上验证微秒级精度检测

## 相关概念
- [[entities/linux/kernel/index]] — Linux内核时间子系统
- [[security-index]] — 安全模块总览
- [[sources/pdf-ptp-security]] — PTPsec原始论文来源

## 来源
- [[sources/pdf-ptp-security]] — INFOCOM 2024论文: PTPsec: Securing the Precision Time Protocol Against Time Delay Attacks


## Related
- [[entities/linux/security/linux-security-observability-ebpf]]
- [[entities/linux/security/bulletproof-tls-pki]]
- [[entities/linux/security/openssl-tls-library]]
