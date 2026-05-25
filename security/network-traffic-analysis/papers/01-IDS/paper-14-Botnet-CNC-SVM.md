# Paper Reading: Botnet Detection via C&C Session Classification

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 14 |
| **标题** | Botnet Traffic Detection Techniques by C&C Session Classification Using SVM |
| **年份** | 2026 |
| **期刊** | Springer |

---

## 1. 研究背景

### 1.1 Botnet C&C 特点

- 命令控制通道特殊
- 行为模式可识别
- 检测关键

### 1.2 研究发现

C&C 会话具有独特特征：
- 定时心跳
- 特定协议
- 行为模式

---

## 2. 方法论

### 2.1 会话分类

```
流量数据 → 会话提取 → 特征向量 → SVM → Botnet/Normal

特征:
├── 包长度直方图
├── 时间间隔
└── 协议特征
```

### 2.2 SVM 分类器

- 高维特征空间
- 最大间隔分类
- 95% 准确率

---

## 3. 主要贡献

1. C&C 会话特征分析
2. 包长度直方图向量
3. SVM 高准确率

---

## 4. 结论

C&C 会话分类是检测僵尸网络的有效方法。

---

*阅读时间: 2026-04-17*
