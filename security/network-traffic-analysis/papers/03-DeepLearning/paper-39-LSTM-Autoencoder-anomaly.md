# Paper Reading: LSTM Autoencoder for Anomaly Detection

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 39 |
| **标题** | Temporal Features Learning Using Autoencoder for Anomaly Detection in Network Traffic |
| **年份** | 2020 |
| **会议** | International Conference on Green Technology and Sustainable Development |

---

## 1. 研究背景

### 1.1 问题

- 网络流量时序特征重要
- 需要自动特征学习
- 标签数据稀缺

### 1.2 创新点

LSTM Autoencoder 学习时序特征进行异常检测。

---

## 2. 方法论

### 2.1 LSTM Autoencoder

```
输入序列
    │
    ▼
LSTM 编码器 → 潜在表示
    │
    ▼
LSTM 解码器 → 重构输出
    │
    ▼
异常分数 = 重构误差
```

### 2.2 半监督学习

- 仅用正常数据训练
- 重构误差判定异常

---

## 3. 数据集

- **ISCX-IDS-2012**

---

## 4. 主要贡献

1. 时序特征自动学习
2. 半监督异常检测
3. 高准确率

---

## 5. 结论

LSTM Autoencoder 有效捕捉网络流量的时序特征。

---

*阅读时间: 2026-04-17*
