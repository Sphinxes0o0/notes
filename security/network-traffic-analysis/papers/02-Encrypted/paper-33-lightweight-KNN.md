# Paper Reading: Lightweight Encrypted Traffic Classification

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 33 |
| **标题** | A Lightweight Encrypted Network Traffic Classification Method Based on Protocol Field and K-Nearest Neighbor |
| **年份** | 2022 |
| **期刊** | Springer |

---

## 1. 研究背景

### 1.1 问题

- 资源受限环境
- 需要轻量级方法
- 实时分类需求

### 1.2 创新点

协议字段 + KNN 轻量级方法。

---

## 2. 方法论

### 2.1 协议字段特征

```
协议字段:
├── IP Header
├── TCP Header
└── TLS Handshake
```

### 2.2 KNN 分类

```
特征 → KNN → 分类
    │
    └── K近邻投票
```

---

## 3. 轻量级优势

| 优势 | 说明 |
|------|------|
| 计算高效 | 简单算法 |
| 内存低 | 存储样本少 |
| 实时性 | 快速推理 |

---

## 4. 结论

轻量级方法适用于资源受限场景。

---

*阅读时间: 2026-04-17*
