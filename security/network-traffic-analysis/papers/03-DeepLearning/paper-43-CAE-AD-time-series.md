# Paper Reading: CAE-AD - Contrastive Autoencoder for Time Series Anomaly Detection

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 43 |
| **标题** | Contrastive autoencoder for anomaly detection in multivariate time series |
| **年份** | 2022 |
| **期刊** | Information Sciences |

---

## 1. 研究背景

### 1.1 问题

- 多变量时序异常检测
- 工业系统监控
- 捕捉时序依赖

### 1.2 创新点

对比自编码器 (Contrastive Autoencoder)。

---

## 2. 方法论

### 2.1 对比学习

```
正样本对: 相近时间点
负样本对: 远离时间点

目标: 拉近正样本，推开负样本
```

### 2.2 CAE-AD 架构

```
输入 → 编码器 → 潜在 → 解码器 → 输出
    │                    │
    └──── 对比损失 ◄─────┘
```

---

## 3. 结论

对比自编码器有效捕捉多变量时序的异常模式。

---

*阅读时间: 2026-04-17*
