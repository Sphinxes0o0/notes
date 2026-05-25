# Paper Reading: ML Algorithm Performance Study for Traffic Anomaly Detection

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 05 |
| **标题** | Network Traffic Anomalies Detection Using Machine Learning Algorithm: A Performance Study |
| **年份** | 2022 |
| **期刊** | Springer |

---

## 1. 研究背景

### 1.1 问题

- 网络流量异常多样
- 需要评估 ML 算法性能
- 实际部署需求

---

## 2. 方法论

### 2.1 比较算法

```
监督学习
├── 决策树 (DT)
├── 随机森林 (RF)
├── 支持向量机 (SVM)
├── K 近邻 (KNN)
└── 朴素贝叶斯 (NB)

无监督学习
├── K-Means
├── DBSCAN
└── Isolation Forest
```

### 2.2 评估指标

- 准确率 (Accuracy)
- 精确率 (Precision)
- 召回率 (Recall)
- F1 分数
- 训练时间

---

## 3. 实验结果

| 算法 | 准确率 | 训练时间 |
|------|--------|----------|
| Random Forest | 高 | 中等 |
| SVM | 中高 | 较长 |
| Decision Tree | 中 | 快 |
| KNN | 中 | 快 |

---

## 4. 结论

RF 在多数场景表现最佳，需根据实际需求选择算法。

---

*阅读时间: 2026-04-17*
