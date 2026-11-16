# Paper Reading: BiLSTM + Self-Attention for Encrypted Malicious Traffic Detection (96.71%)

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 22 |
| **标题** | Enhanced Malicious Traffic Detection Using TLS Features and Multi-class Classifier Ensemble with Self-Attention |
| **年份** | 2024 |
| **期刊** | Journal of Network and Systems Management |
| **方法** | RF + LSTM + BiLSTM + Self-Attention |

---

## 1. 研究背景

### 1.1 问题

恶意软件使用 TLS 加密其通信以躲避检测：
- 传统方法无法检测加密恶意流量
- 需要在不解密的情况下识别恶意流量

### 1.2 创新点

在 RF + LSTM + BiLSTM 基础上引入 **Self-Attention** 机制提升性能。

---

## 2. 方法论

### 2.1 模型架构

```
输入: TLS 特征
    │
    ▼
┌─────────────────────────────────────────┐
│  Random Forest 特征提取                  │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  LSTM 序列建模                          │
│  └── 时序依赖                           │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  BiLSTM 双向上下文                       │
│  └── 前向 + 后向信息                     │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  Self-Attention                         │
│  └── 关键特征聚焦                        │
└─────────────────────────────────────────┘
    │
    ▼
分类输出
```

### 2.2 Self-Attention 机制

```
Attention(Q, K, V) = softmax(QK^T / √d) V

作用:
├── 聚焦重要特征
├── 捕获长距离依赖
└── 增强模型可解释性
```

---

## 3. 实验结果

| 模型 | 准确率 |
|------|---------|
| RF only | 94.85% |
| RF + LSTM | 95.5% |
| RF + LSTM + BiLSTM | 96.0% |
| **RF + LSTM + BiLSTM + Attention** | **96.71%** |

---

## 4. TLS 特征

- JA3/JA4 指纹
- 密码套件
- TLS 扩展
- 证书特征

---

## 5. 结论

引入 Self-Attention 机制进一步提升了检测准确率至 96.71%，证明注意力机制在加密流量分析中的价值。

---

*阅读时间: 2026-04-17*
