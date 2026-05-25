# Paper Reading: Deep Fingerprinting for Website Fingerprinting

## 文献信息

| 属性 | 内容 |
|------|------|
| **序号** | 30 |
| **标题** | Deep Fingerprinting: Undermining Website Fingerprinting Defenses |
| **年份** | 2018 |
| **会议** | ACM SIGSAC CCS |

---

## 1. 研究背景

### 1.1 Website Fingerprinting

- 通过流量模式识别访问的网站
- Tor 等匿名网络中
- 隐私威胁

### 1.2 问题

深度学习可绕过防御。

---

## 2. 方法论

### 2.1 深度学习攻击

```
流量序列
    │
    ▼
CNN 模型
├── 包长度序列
├── 时间间隔
└── 方向信息
    │
    ▼
网站分类
```

---

## 3. 主要贡献

1. 深度学习攻击网站指纹
2. 证明防御不足
3. 隐私风险

---

## 4. 结论

深度学习对网站指纹防御构成严重威胁。

---

## 5. 防御方向

- 流量混淆
- 填充技术
- 多路复用

---

*阅读时间: 2026-04-17*
