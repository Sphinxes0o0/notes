# Paper Reading: ANN for DDoS Attack Detection

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 13 |
| **标题** | DDoS Attack Detection Using Artificial Neural Network |
| **年份** | 2021 |
| **会议** | International Conference on Springer |

---

## 1. 研究背景

### 1.1 DDoS 威胁

- 分布式拒绝服务攻击
- 消耗目标资源
- 常见网络威胁

### 1.2 检测挑战

- 流量模式多样
- 快速响应需求
- 误报率控制

---

## 2. 方法论

### 2.1 ANN 架构

```
输入特征
    │
    ▼
神经网络
├── 输入层
├── 隐藏层
└── 输出层
    │
    ▼
DDoS / Normal
```

### 2.2 特征选择

| 特征 | 说明 |
|------|------|
| 流量速率 | 包/秒 |
| 连接数 | 源IP数 |
| 协议分布 | TCP/UDP/ICMP |

---

## 3. 结论

ANN 是检测 DDoS 攻击的有效工具。

---

*阅读时间: 2026-04-17*
