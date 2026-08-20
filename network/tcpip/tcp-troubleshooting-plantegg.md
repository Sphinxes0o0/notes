---
title: "TCP疑难问题汇总"
description: "**Source:** https://plantegg.github.io/2021/02/14/TCP疑难问题案例汇总/"
---
# TCP疑难问题汇总

**Source:** https://plantegg.github.io/2021/02/14/TCP疑难问题案例汇总/
**NIDS Relevance:** ★★★★☆ (TCP连接异常检测的直接参考)

## 核心内容

### 主要章节
1. **服务无响应分析** — queue溢出、CLOSE_WAIT问题、TCP连接异常
2. **传输速度分析** — BDP (带宽延迟积)、RTT、delay ack影响
3. **TCP队列问题** — 半连接队列和全连接队列、somaxconn参数
4. **防火墙与Reset分析** — TTL、IP identification字段分析
5. **TCP参数** — Keepalive设置、连接超时配置
6. **诊断工具** — netstat、ss、tcpdump、WireShark/tshark

### 连接异常检测方法
- **TTL和IP identification字段运用**: 追踪来源、分析流量模式
- **CLOSE_WAIT状态监控**: 与somaxconn关联分析
- **Queue溢出检测**: 入侵指标

### Packet分析技术
- tcpdump抓取Unix Domain Socket
- tshark (WireShark CLI) 解析packet
- ss实时连接监控

### 网络流量分析
- 网络丢包调查
- Keepalive和reset packet检测
- "谁动了我的TCP连接"分析

### 诊断命令
- `netstat` timer states, keepalive解释
- `ss` socket statistics
- 网络流量追踪方法论

## NIDS Relevance
1. **Connection Anomaly**: CLOSE_WAIT超时、queue溢出是典型的入侵迹象
2. **Reset/Keepalive分析**: 检测异常的TCP状态转换
3. **TTL fingerprinting**: 追踪来源主机OS版本
4. **Queue监控**: 半连接队列爆满是SYN flood的典型症状

## 关联概念
-  — 网络深度笔记
-  — Snort3 flow tracking
