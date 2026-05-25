# Paper Reading: VAE for Anomaly Detection in Network Traffic

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 42 |
| **标题** | Evaluation of feature learning for anomaly detection in network traffic |
| **年份** | 2020 |
| **期刊** | Evolving Systems |

---

## 1. 研究背景

### 1.1 问题

- 深度学习特征表示能力
- Autoencoder vs VAE
- 半监督异常检测

### 1.2 研究目标

比较 Autoencoder 和 VAE 在异常检测中的特征学习能力。

---

## 2. 方法论

### 2.1 Autoencoder

```
输入 → 编码器 → 潜在 → 解码器 → 输出
      重构误差 → 异常分数
```

### 2.2 Variational Autoencoder

```
输入 → 潜在分布 → 重构
      重构 + KL散度 → 异常分数
```

---

## 3. 实验设置

### 3.1 数据集

多个公开数据集：
- UNSW-NB15
- CICIDS2017
- NSL-KDD

---

## 4. 主要贡献

1. 系统性比较
2. 不同数据集评估
3. 半监督学习范式

---

## 5. 结论

VAE 在特征学习和异常检测方面表现良好。

---

*阅读时间: 2026-04-17*
