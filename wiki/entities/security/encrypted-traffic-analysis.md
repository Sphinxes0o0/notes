---
type: entity
tags: [网络安全, 加密流量, TLS, 隐私]
created: 2026-05-25
sources: [notes-network-traffic-analysis]
---

# 加密流量分析 — TLS 侧信道

## 定义

TLS/HTTPS 普及使传统 DPI（深度包检测）失效，研究转向**无需解密的侧信道分析方法**：通过 TLS 握手元数据、数据包长度/时序模式等特征识别流量类型和恶意行为。

## Cisco ETA 方法

Encrypted Traffic Analytics 使用三项特征：
1. 连接的初始数据包（TLS ClientHello）
2. 数据包长度和时间序列
3. 流内 payload 字节分布

## TLS 特征工程

### 必需特征
- TLS 版本、密码套件、证书是否自签名

### 推荐特征
- **JA3/JA4 指纹**：TLS 握手特征拼接后 MD5/SHA256
- TLS 扩展类型（椭圆曲线、签名算法等）
- 握手时间间隔
- 包长度统计（均值、方差、最大、最小）

### 恶意流量识别发现
- 恶意软件使用**较少的 TLS 扩展和密码套件**
- 常用**自签名证书**
- 证书链不完整

## 方法对比

| 方法 | 准确率 | 说明 |
|------|--------|------|
| **TLS + RF** | **99.85%** | 65个TLS特征 + Random Forest（Paper-26）|
| RF+LGBM+XGB | 94.85% | 集成学习方法 |
| BiLSTM+Attention | 96.71% | 多阶段融合（Paper-22）|
| FlowSpectrum | 99.2% | 光谱分析（无需 TLS 特征）|
| 无监督特征学习 | 89.25% | 自适应学习，无需标签 |

## 加密流量分类

- **非 VPN 流量**：FlowSpectrum 达 99.2%
- **VPN 流量**：ISCX-VPN2016 数据集，BiLSTM+Attention 效果最佳
- **Tor 匿名流量**：Deep Fingerprinting (2018 CNN)

## 相关概念

- [[network-traffic-analysis]] — 加密流量分析是核心子方向
- [[ids-ml-survey]] — TLS特征+RF 方法也在 IDS 领域应用
- [[traffic-deep-learning]] — BiLSTM/Attention 等深度学习方法

## 来源详情

- [[notes-network-traffic-analysis]] — literature-review-2023-2026.md §2, method-comparison.md §4
