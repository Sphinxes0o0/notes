# Paper Reading: ML + DL Hybrid IDS

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 09 |
| **标题** | Enhancing Intrusion Detection System Using Machine Learning and Deep Learning |
| **年份** | 2024 |
| **期刊** | Springer |

---

## 1. 研究背景

### 1.1 问题

- 单一模型难以应对复杂攻击
- 机器学习 vs 深度学习各有优劣
- 需要融合两种方法

---

## 2. 方法论

### 2.1 混合架构

```
输入流量
    │
    ├──► 传统 ML 模块
    │    ├── RF
    │    ├── XGBoost
    │    └── SVM
    │
    └──► 深度学习模块
         ├── CNN
         ├── LSTM
         └── Transformer
              │
              ▼
         集成融合层
              │
              ▼
         最终决策
```

### 2.2 融合策略

- Stacking 元学习
- 加权投票
- 特征级融合

---

## 3. 主要贡献

1. ML + DL 融合框架
2. 多层次特征提取
3. 泛化能力提升

---

## 4. 结论

混合方法优于单一模型，提升检测精度和鲁棒性。

---

*阅读时间: 2026-04-17*
