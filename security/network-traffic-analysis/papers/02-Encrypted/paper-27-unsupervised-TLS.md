# Paper Reading: Unsupervised TLS Feature Learning for Malicious Traffic

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 27 |
| **标题** | Malicious encrypted traffic features extraction based on unsupervised feature adaptive learning |
| **年份** | 2022 |
| **期刊** | Journal of Computer Virology and Hacking |

---

## 1. 研究背景

### 1.1 问题

- 监督学习需要标注数据
- 标注成本高
- 新恶意软件缺乏标签

### 1.2 创新点

无监督特征自适应学习。

---

## 2. 方法论

### 2.1 无监督特征学习

```
未标注流量
    │
    ▼
自适应特征学习
├── 5-Tuple Masking
├── 特征重要性
└── 自动编码
    │
    ▼
恶意流量检测
```

### 2.2 5-Tuple Masking

- 保留关键特征
- 噪声增强

---

## 3. 实验结果

| 指标 | 结果 |
|------|------|
| 准确率 | 89.25% |

---

## 4. 结论

无监督方法可在无标注情况下检测恶意加密流量。

---

*阅读时间: 2026-04-17*
