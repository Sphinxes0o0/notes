# Paper Reading: FS-Net - Flow Sequence Network

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 32 |
| **标题** | FS-Net: A Flow Sequence Network for Encrypted Traffic Classification |
| **年份** | 2019 |
| **会议** | IEEE INFOCOM |

---

## 1. 研究背景

### 1.1 问题

- 加密流量分类困难
- 传统方法依赖 payload
- 需要新的序列建模方法

### 1.2 创新点

流序列网络 (FS-Net) 进行端到端学习。

---

## 2. 方法论

### 2.1 序列建模

```
流序列 → FS-Net → 分类

核心:
├── 序列编码
├── 时序特征
└── 端到端学习
```

---

## 3. 实验结果

| 方法 | 准确率 |
|------|---------|
| FS-Net | 高 |

---

## 4. 结论

FS-Net 证明了序列建模在加密流量分类中的有效性。

---

*阅读时间: 2026-04-17*
