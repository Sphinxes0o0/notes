# Paper Reading: WNN-Based Network Intrusion Detection

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 04 |
| **标题** | A WNN-Based Approach for Network Intrusion Detection |
| **年份** | 2022 |
| **期刊** | Springer |

---

## 1. 研究背景

### 1.1 问题

- 传统 IDS 误报率高
- 计算复杂度高
- 实时性需求

### 1.2 Weightless Neural Networks

- 无权重神经网络
- 查表式计算
- 低资源消耗

---

## 2. 方法论

### 2.1 WNN 结构

```
输入特征
    │
    ▼
RAM 节点阵列
├── 地址解码
├── 模式存储
└── 多数投票
    │
    ▼
分类输出
```

### 2.2 优势

- 高效查表运算
- 适合硬件实现
- 可并行处理

---

## 3. 实验结果

- CIC-IDS 数据集评估
- 优于传统神经网络

---

## 4. 结论

WNN 为 IDS 提供轻量级解决方案。

---

*阅读时间: 2026-04-17*
