# Paper Reading: GraphDapp - GNN for Decentralized App Identification

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 31 |
| **标题** | GraphDapp: Accurate Decentralized Application Identification via Encrypted Traffic Analysis using Graph Neural Networks |
| **年份** | 2021 |
| **期刊** | IEEE Transactions on Information Forensics and Security (TIFS) |

---

## 1. 研究背景

### 1.1 问题

- 去中心化应用 (DApp) 识别困难
- 加密流量增加分析难度
- 传统方法不适用

### 1.2 创新点

使用图神经网络 (GNN) 分析加密流量。

---

## 2. 方法论

### 2.1 图表示

```
网络流量 → 图结构
├── 节点: IP地址/设备
└── 边: 流量连接
```

### 2.2 GNN 架构

```
图输入
    │
    ▼
图卷积层
├── 节点特征更新
├── 消息传递
└── 聚合邻居信息
    │
    ▼
分类器 → DApp 识别
```

---

## 3. 主要贡献

1. 首次将 GNN 用于 DApp 识别
2. 利用图结构信息
3. 高准确率

---

## 4. 结论

GNN 有效捕捉加密流量中的图结构信息。

---

*阅读时间: 2026-04-17*
