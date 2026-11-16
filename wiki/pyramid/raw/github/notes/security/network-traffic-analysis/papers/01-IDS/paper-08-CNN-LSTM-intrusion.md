# Paper Reading: CNN-LSTM for Network Intrusion Detection

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 8 |
| **标题** | Deep Learning Network Intrusion Detection Based on Network Traffic |
| **年份** | 2022 |
| **期刊** | Springer |

---

## 1. 研究背景

### 1.1 问题

传统入侵检测面临挑战：
- 特征工程复杂
- 泛化能力差
- 难以检测新型攻击

### 1.2 解决方案

结合 CNN 和 LSTM 的深度学习方法。

---

## 2. 方法论

### 2.1 混合架构

```
输入流量
    │
    ▼
CNN 层 ──→ 空间特征提取
    │
    ▼
LSTM 层 ──→ 时序依赖建模
    │
    ▼
分类输出
```

### 2.2 数据集

- **UNSW-NB15**
- **NLS-KDD**

---

## 3. 实验结果

| 数据集 | 准确率 |
|--------|--------|
| UNSW-NB15 | 高 |
| NLS-KDD | 高 |

---

## 4. 关键洞察

- CNN 捕捉流的局部特征
- LSTM 建模时序关系
- 两者结合提升性能

---

## 5. 结论

CNN-LSTM 混合模型有效提升入侵检测性能。

---

*阅读时间: 2026-04-17*
