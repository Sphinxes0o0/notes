# Paper Reading: DNN with AntiRectifier for Intrusion Detection

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 10 |
| **标题** | Intrusion Detection Using Deep Neural Network with AntiRectifier Layer |
| **年份** | 2024 |
| **期刊** | Springer |

---

## 1. 研究背景

### 1.1 问题

- 传统激活函数局限性
- 需要更高效的特征学习
- ReLU 梯度消失问题

### 1.2 创新点

引入 AntiRectifier 激活函数改进 DNN。

---

## 2. 方法论

### 2.1 AntiRectifier 激活

```
AntiRectifier(x) = x * sigmoid(x)

特点:
├── 避免梯度消失
├── 保留负值信息
└── 更好的梯度流
```

### 2.2 DNN 架构

```
输入 → Dense层 → AntiRectifier → ... → Softmax → 输出
```

---

## 3. 主要贡献

1. 提出 AntiRectifier 激活函数
2. 改进 IDS 性能
3. 更好的特征学习

---

## 4. 结论

AntiRectifier 激活函数有效提升入侵检测性能。

---

*阅读时间: 2026-04-17*
