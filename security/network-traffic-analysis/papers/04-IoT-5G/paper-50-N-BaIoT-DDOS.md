# Paper Reading: DDOS Intrusion Detection - N-BaIoT Dataset

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 50 |
| **标题** | DDOS Intrusion Detection with Machine Learning Models: N-BaIoT Data Set |
| **年份** | 2023 |
| **会议** | International Conference on AI and Applied Mathematics |

---

## 1. 研究背景

### 1.1 N-BaIoT 数据集

N-BaIoT 是专门为 IoT 设备创建的入侵检测数据集：
- 采集自真实 IoT 设备
- 包含正常流量和攻击流量
- 多种攻击类型

### 1.2 数据集特点

| 特点 | 说明 |
|------|------|
| 设备多样性 | 多个 IoT 设备 |
| 攻击类型 | Mirai, BASH, etc. |
| 标注完整 | 详细攻击标签 |

---

## 2. 方法论

### 2.1 检测流程

```
原始流量 → 预处理 → 特征提取 → ML 分类 → 攻击检测
```

### 2.2 评估指标

| 指标 | 结果 |
|------|------|
| 准确率 | 高 |
| 误报率 | 低 |

---

## 3. 结论

N-BaIoT 数据集为 IoT DDoS 检测研究提供了重要基准。

---

*阅读时间: 2026-04-17*
