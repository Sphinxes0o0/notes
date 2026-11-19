# Paper Reading: Bloom and XOR Filters for Intrusion Detection

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 6 |
| **标题** | Intrusion Detection Using Bloom and XOR Filters |
| **年份** | 2024 |
| **期刊** | Springer |

---

## 1. 研究背景

### 1.1 问题

- 高速网络检测需求
- 传统方法计算开销大
- 需要高效模式匹配

### 1.2 创新点

使用 Bloom Filter 和 XOR Filter 进行高效入侵检测。

---

## 2. 方法论

### 2.1 Bloom Filter

```
集合 S = {x1, x2, ..., xn}
    │
    ▼
m 位数组初始化为 0
    │
    ▼
对每个元素用 k 个哈希函数
    │
    ▼
检测: 查询各位是否都为1
```

**特点**:
- 空间效率高
- 可能假阳性
- 不可能假阴性

### 2.2 XOR Filter

类似 Bloom Filter，但使用 XOR 操作。

---

## 3. 主要贡献

1. 高效模式匹配
2. 低内存开销
3. 适合高速网络

---

## 4. 结论

Bloom/XOR Filter 提供了一种高效的 IDS 模式匹配方案。

---

*阅读时间: 2026-04-17*
