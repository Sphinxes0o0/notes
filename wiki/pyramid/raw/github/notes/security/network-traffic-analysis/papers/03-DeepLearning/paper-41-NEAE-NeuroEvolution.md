# Paper Reading: NEAE - NeuroEvolution AutoEncoder for Anomaly Detection

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 41 |
| **标题** | NEAE: NeuroEvolution AutoEncoder for anomaly detection in internet traffic data |
| **年份** | 2023 |
| **期刊** | The Journal of Supercomputing |

---

## 1. 研究背景

### 1.1 问题

- 网络流量异常检测重要
- 传统方法难以捕捉复杂模式
- 需要自动特征学习

### 1.2 创新

结合神经进化算法和自编码器。

---

## 2. 方法论

### 2.1 神经进化 AutoEncoder

```
输入数据
    │
    ▼
NeuroEvolution
├── 进化算法优化网络结构
└── 自动确定架构参数
    │
    ▼
AutoEncoder
├── 编码器 → 潜在表示
└── 解码器 → 重构输出
    │
    ▼
异常检测
└── 重构误差 → 异常分数
```

### 2.2 进化优化

- 自动网络结构搜索
- 参数优化
- 避免手动调参

---

## 3. 实验结果

| 指标 | 表现 |
|------|------|
| 异常检测 | 有效 |
| 自动化 | 高 |

---

## 4. 主要贡献

1. 神经进化自动确定网络结构
2. 端到端异常检测
3. 减少人工干预

---

## 5. 结论

NEAE 通过进化算法自动优化自编码器结构，实现有效的网络流量异常检测。

---

*阅读时间: 2026-04-17*
