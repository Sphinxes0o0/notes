---
type: entity
tags: [网络安全, IDS, 入侵检测, 机器学习, 深度学习]
created: 2026-05-25
sources: [notes-network-traffic-analysis]
---

# IDS + ML 综述 — 入侵检测机器学习

## 定义

网络入侵检测系统（IDS）结合机器学习/深度学习方法，自动识别恶意流量、DoS/DDoS、Botnet 等攻击的技术方向。

## 方法论全景

### 传统机器学习

| 方法 | 准确率 | 适用场景 |
|------|--------|----------|
| Random Forest | **99.85%** | TLS 加密流量分类 |
| SVM | 高 | Botnet C&C 检测 |
| Decision Tree | 中 | 移动端恶意软件 |
| KNN | 中 | 边缘设备轻量检测 |

### 深度学习入侵检测

| 方法 | 准确率 | 核心优势 |
|------|--------|----------|
| CNN-LSTM | 高 | 时空特征联合建模 |
| HCRNNIDS | 高 | Hybrid CNN-RNN 融合 |
| DNN+AntiRectifier | 高 | 改进激活函数 |
| Fast Neural IDS | 高 | 模块化神经网络，动态适应 |
| WNN | 中 | Weightless Neural Networks，轻量边缘 |
| Bloom/XOR Filters | 中 | 高效模式匹配 |

### 类别不平衡解决

**ADASYN + Tomek Links** 组合（Paper-01）：对少数类（攻击流量）进行过采样，对多数类欠采样，显著提升少数类检测率。

## 关键里程碑

- **2022**：Ensemble ML 99.85% — RF+XGB+LGBM，TLS 特征登顶
- **2024**：HCRNNIDS — Hybrid CNN-RNN 结构创新
- **2024**：Fast Neural IDS — 模块化 NN，动态环境适应
- **2026**：Botnet SVM — 高效 C&C 分类

## 实时检测挑战

多数研究未考虑高速网络实时性要求，eBPF/XDP 内核级方案（SmartX）是当前唯一兼顾精度和延迟的实用路线。

## 相关概念

- [[network-traffic-analysis]] — 网络流量分析总览
- [[encrypted-traffic-analysis]] — TLS 特征 + RF 高准确率方法
- [[traffic-deep-learning]] — CNN-LSTM/Attention 等深度学习模型
- [[kernel-bypass-dpdk]] — eBPF/XDP 实时 IDS 实现

## 来源详情

- [[notes-network-traffic-analysis]] — literature-review-2023-2026.md §1, method-comparison.md §3
