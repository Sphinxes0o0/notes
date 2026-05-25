# Paper Reading: IDS Robustness Evaluation

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 58 |
| **标题** | Towards Evaluating the Robustness of Deep Intrusion Detection Models |
| **年份** | 2024 |
| **期刊** | Springer |

---

## 1. 研究背景

### 1.1 问题

- 深度学习 IDS 易受攻击
- 对抗样本威胁
- 需要评估鲁棒性

---

## 2. 方法论

### 2.1 鲁棒性评估框架

```
深度 IDS 模型
    │
    ▼
对抗攻击测试
├── FGSM
├── PGD
└── Carlini-Wagner
    │
    ▼
鲁棒性评估
```

---

## 3. 主要贡献

1. 系统性鲁棒性评估
2. 多种攻击方法
3. 防御建议

---

## 4. 结论

深度 IDS 需要增强对抗鲁棒性。

---

## 5. 增强方法

- 对抗训练
- 防御蒸馏
- 输入验证

---

*阅读时间: 2026-04-17*
