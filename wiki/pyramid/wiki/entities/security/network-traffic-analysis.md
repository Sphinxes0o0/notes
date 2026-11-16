---
type: entity
tags: [网络安全, 流量分析, IDS, NIDS]
created: 2026-05-25
sources: [notes-network-traffic-analysis]
---

# 网络流量分析

## 定义

通过对网络数据包或流（5-Tuple 聚合：Src IP、Dst IP、Src Port、Dst Port、Protocol）进行监控、分析和建模，实现入侵检测、流量分类、异常发现等安全目标的技术领域。

## 分析粒度

| 方法 | 描述 | 优缺点 |
|------|------|--------|
| **Packet-based** | 分析每个独立数据包 | 详细信息，计算开销大 |
| **Flow-based** | 分析五元组聚合流数据 | 高效，适合大规模 |
| **NetFlow/sFlow** | 路由器导出流统计 | 轻量，但信息有限 |

## 核心技术方向

### 1. 入侵检测系统（IDS）

- **HIDS**：基于主机
- **NIDS**：基于网络（传统规则匹配 → ML/DL 智能检测）

### 2. 加密流量检测

- TLS/HTTPS 普及使 DPI 失效
- 侧信道分析：数据包长度/时序模式、TLS 握手元数据（JA3/JA4 指纹）

### 3. 深度学习方法

- CNN：空间特征（FlowSpectrum 一维表示）
- LSTM/BiLSTM：时序依赖
- AutoEncoder：异常检测/半监督
- Transformer/GNN：多尺度融合

## 常用数据集

| 数据集 | 场景 |
|--------|------|
| CICIDS2017/2018 | 通用 IDS |
| ISCXVPN2016 | VPN 流量分类 |
| ISCXTor2016 | Tor 匿名流量 |
| UNSW-NB15 | 现代网络流量 |
| N-BaIoT | IoT 安全 |

## 相关概念

- [[ids-ml-survey]] — IDS 深度学习/ML 方法综述，覆盖 CNN-LSTM/HCRNNIDS/Fast Neural IDS
- [[encrypted-traffic-analysis]] — 加密流量 TLS 特征分析 + Random Forest 99.85%
- [[traffic-deep-learning]] — CNN/LSTM/AutoEncoder/Transformer/GNN 在流量分析中的应用
- [[kernel-bypass-dpdk]] — eBPF/XDP 内核级实时检测，与本领域交叉

## 来源详情

- [[notes-network-traffic-analysis]]
