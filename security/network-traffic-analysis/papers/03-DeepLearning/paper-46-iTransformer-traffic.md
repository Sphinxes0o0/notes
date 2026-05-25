# Paper Reading: iTransformer for Traffic Prediction

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 46 |
| **标题** | Transformer in Time Series for Traffic Prediction |
| **年份** | 2024 |

---

## 1. 研究背景

### 1.1 问题

- 时序预测在流量分析中重要
- 传统 RNN/LSTM 存在长依赖问题
- Transformer 提供并行化优势

### 1.2 创新点

iTransformer 倒置注意力机制。

---

## 2. 方法论

### 2.1 iTransformer 架构

```
输入时序
├── Variables (特征维度)
├── Timesteps (时间步)
└── Embedding
    │
    ▼
倒置注意力
├── 跨时间步注意力 → 捕获时序依赖
├── 前馈网络
└── 层归一化
    │
    ▼
预测头
    │
    ▼
流量预测
```

### 2.2 核心思想

- 将注意力应用于变量间关系
- 更好捕获多变量相关性
- 提升长期预测精度

---

## 3. 主要贡献

1. iTransformer 架构创新
2. 多变量时序预测
3. 长期依赖建模

---

## 4. 结论

iTransformer 在流量时序预测任务上表现优异。

---

*阅读时间: 2026-04-17*
