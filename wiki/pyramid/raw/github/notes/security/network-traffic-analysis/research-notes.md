# 研究笔记 | Research Notes

## 论文精读笔记

### Paper 1: SmartX Intelligent Sec (2024)
**链接**: https://arxiv.org/html/2410.20244v1

**核心贡献**:
- 结合 eBPF/XDP 实现高效数据包捕获（内核态）
- BiLSTM 用于网络威胁检测
- 实时原型系统展示

**技术栈**:
```
eBPF/XDP → Packet Filtering → BiLSTM Classifier → Threat Detection
```

**关键洞察**: eBPF 可以在内核态直接过滤恶意流量，避免将所有流量发送到用户态，减少开销。

---

### Paper 2: Mutated Traffic Detection and Recovery (2022)
**期刊**: Annals of Telecommunications

**核心贡献**:
- 检测流量混淆/变异技术
- 恢复原始流量特征

**方法**:
- Deep Learning 模型检测变异流量
- 去噪恢复原始流量

**结果**:
- 检测率 ~95%
- 恢复损失 < 3%

**威胁模型**: 攻击者使用流量变异（修改包大小、到达间隔）躲避检测

---

### Paper 3: TLS Features + Ensemble (2024)
**期刊**: Journal of Network and Systems Management

**核心贡献**:
- 提出新型 TLS 特征
- RF/LGBM/XGBoost 集成 → 94.85%
- RF + LSTM + BiLSTM + Self-Attention → 96.71%

**TLS 特征**:
- 密码套件使用模式
- TLS 扩展数量
- 证书特征（自签名检测）
- 握手时间特征

---

## 方法论总结

### Flow-based vs Packet-based

| 维度 | Flow-based | Packet-based |
|------|------------|--------------|
| 粒度 | 五元组聚合 | 逐包 |
| 存储 | 小 | 大 |
| 计算 | 低 | 高 |
| 信息量 | 中等 | 完整 |
| 实时性 | 好 | 差 |

### 采样问题

高速网络必须采样，常见采样率：
- 1/100 (100采样)
- 1/1000 (1000采样)

采样带来的挑战：
1. 稀有攻击可能被漏掉
2. 流量特征被稀释
3. 需要抗噪模型

解决方案：
- 异常检测而非监督学习
- 多尺度特征融合
- 集成多模型

---

## 开源项目参考

| 项目 | 链接 | 语言 |
|------|------|------|
| Zeek | https://github.com/zeek/zeek | C++ |
| Suricata | https://github.com/OISF/suricata | C |
| Moloch | https://github.com/ AOL/moloch | Node.js |
| Argus | https://github.com/axiomcyber/argus | C |
| Kitsune (ML for network intrusion) | https://github.com/ymirsky/Kitsune-py | Python |

---

## 关键词汇表

| 术语 | 解释 |
|------|------|
| DPI | Deep Packet Inspection，深度包检测 |
| IDS/IPS | Intrusion Detection/Prevention System |
| NIDS | Network-based Intrusion Detection System |
| NetFlow | Cisco 流量导出协议 |
| sFlow | 采样流量导出 |
| IPFIX | Internet Protocol Flow Information Export |
| eBPF | Extended Berkeley Packet Filter |
| XDP | Express Data Path |
| TLS | Transport Layer Security |
| SNI | Server Name Indication |
| BiLSTM | Bidirectional Long Short-Term Memory |
| ETA | Encrypted Traffic Analysis (Cisco) |
| Flow | 一组具有相同五元组的数据包 |
| Packets | 单个网络数据包 |
| Sampling Rate | 采样率，如 1/1000 |
| Flow Meter | 流量计量/导出代理 |

---

## 待深入方向

1. **eBPF + ML 集成** - 如何在 XDP 层做轻量检测
2. **对抗样本** - 流量混淆/变异检测
3. **轻量模型** - 边缘设备部署
4. **实时系统** - 在线学习 vs 批量学习
5. **可解释性** - 黑盒模型的可解释输出
