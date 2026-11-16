# Paper Reading: CNN-LSTM Hybrid Network for Traffic Classification

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 35 |
| **标题** | Traffic Classification Based on CNN-LSTM Hybrid Network |
| **年份** | 2022 |
| **期刊** | Springer |

---

## 1. 研究背景

### 1.1 问题

- 流量分类需要时空特征
- CNN 提取局部空间特征
- LSTM 建模时序依赖

### 1.2 挑战

- 单模型难以捕获双重特征
- 流量数据高维复杂

---

## 2. 方法论

### 2.1 CNN-LSTM 架构

```
流量序列
    │
    ▼
CNN 卷积层
├── 1D 卷积
├── 池化层
└── 局部特征
    │
    ▼
Reshape
    │
    ▼
LSTM 层
├── 双层 LSTM
├── 时序依赖
└── 上下文建模
    │
    ▼
全连接 + Softmax
    │
    ▼
分类结果
```

### 2.2 核心思想

- CNN 提取包级别的局部模式
- LSTM 捕获流级别的时序关系
- 双重特征融合

---

## 3. 主要贡献

1. 时空特征联合学习
2. 端到端训练
3. 适用于多种流量分类任务

---

## 4. 结论

CNN-LSTM 混合网络有效结合空间和时间特征，提升分类准确率。

---

*阅读时间: 2026-04-17*
