---
type: source
source-type: github
title: 网络流量分析文献综述
date: 2026-05-25
path: raw/github/notes/security/network-traffic-analysis/
summary: 网络流量分析研究方向调研（62篇论文）：IDS/异常检测、加密流量分析、深度学习方法、IoT/5G流量、eBPF实时检测
created: 2026-05-25
tags: []
---
# 网络流量分析文献综述

## 核心内容

基于 62 篇论文的网络流量分析领域全面综述，涵盖 2017-2026 年技术演进。

**5 篇核心文档：**

| 文档 | 主题 |
|------|------|
| README.md | 研究概述、核心技术方向、主要文献、工具/数据集 |
| literature-review-2023-2026.md | 详尽文献综述（按方向分类：IDS/加密流量/DL/IoT/对抗/SDN）|
| research-timeline.md | 技术演进时间线（4个时代：传统ML→DL崛起→融合创新→实时智能）|
| method-comparison.md | 方法对比矩阵（流量分类/异常检测/入侵检测/加密流量/实时检测）|
| quick-reference.md | 快速参考指南（场景选择/数据集/特征工程/代码模板）|

## 技术演进路线

```
2017-2019 传统ML时代：SVM, RF, DT，特征工程为核心
2020-2021 DL崛起时代：CNN, LSTM, AutoEncoder, Attention
2022-2023 融合创新时代：eBPF/XDP, GNN, Transformer, GAN
2024-2026 实时智能时代：大模型, 联邦学习, 可解释AI, eBPF+BiLSTM
```

## 准确率里程碑

- **99.85%** — TLS特征+Random Forest（2022）
- **99.2%** — FlowSpectrum 光谱分析（2023）
- **97.13%** — 深度学习 Raw Traffic Botnet 检测（2022）
- **96.71%** — BiLSTM+Attention 加密流量（2024）

## 核心方法论

- **TLS 特征工程**：JA3/JA4 指纹、密码套件、证书特征、握手时间
- **深度学习方法**：CNN（空间）、LSTM/BiLSTM（时序）、AutoEncoder（异常）、Attention/GNN（图/多尺度）
- **实时检测**：eBPF/XDP 内核级捕获 + BiLSTM 分类（SmartX，2024）
- **类别不平衡**：ADASYN + Tomek Links 组合
- **加密流量**：无需解密的 TLS 元数据侧信道分析

## 来源详情

- **来源路径**: `raw/github/notes/security/network-traffic-analysis/`
- **文档数量**: 5 篇核心文档 + papers/ 子目录（62篇论文分析）
- **领域**: 网络安全、入侵检测、流量分类、深度学习、加密流量分析
