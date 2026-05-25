---
title: Snort3 模块分析
---

# Snort3 数据包处理流水线

本节深入分析 Snort3 网络入侵检测系统的数据包处理流水线模块。

## 模块架构

Snort3 数据包处理流程:

```
DAQ (数据包采集)
    │
    ▼
packet_io (DAQ封装)
    │
    ▼
codecs (协议解码)
    │
    ▼
flow (流管理)
    │
    ▼
stream (TCP重组/IP分片)
    │
    ▼
detection (规则检测)
```

## 模块文档

### 数据包IO
- [packet_io](/security/nids/snort3/packet_io) - 数据包捕获发送 (DAQ封装)
  - SFDAQ/SFDAQInstance: DAQ实例封装
  - Active: 数据包裁定(Verdict)管理

### 协议解码
- [codecs](/security/nids/snort3/codecs) - 协议解码器
  - IPv4/IPv6/TCP/UDP/ICMP 等协议解码
  - IP分片重组 (Defrag)
  - 校验和计算

### 流管理
- [flow](/security/nids/snort3/flow) - 流管理
  - FlowKey: 流唯一标识
  - FlowCache: 流缓存(LRU)
  - FlowControl: 流量控制器

### TCP重组
- [stream](/security/nids/snort3/stream) - TCP流重组
  - StreamSplitter: 流分割器
  - PAF: 协议感知Flush
  - IP Defrag: IP分片重组

## 相关文档

- [Snort3 整体架构分析](/security/nids/snort3_architecture_analysis) - 完整架构概览
- [framework_module](/security/nids/snort3/framework_module) - 框架模块
- [main_module](/security/nids/snort3/main_module) - 主模块
