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

### 规则检测
- [01_detection](/security/nids/snort3/01_detection) - 检测框架核心
  - DetectionEngine: 检测引擎主类
  - IpsContext: 检测上下文(单包状态)
  - OptTreeNode/RuleTreeNode: 规则树节点
  - 快速模式匹配入口(fp_full/fp_partial)

- [02_ips_options](/security/nids/snort3/02_ips_options) - IPS检测选项
  - content: 字符串模式匹配(Boyer-Moore)
  - pcre: Perl兼容正则表达式(pcre2)
  - byte_test/byte_jump/byte_extract/byte_math: 字节操作
  - flow/flowbits: 流状态和标志位
  - flags/dsize: TCP标志位和载荷大小
  - 共70个选项实现

- [03_search_engines](/security/nids/snort3/03_search_engines) - 模式匹配引擎
  - AC_BNFA: Aho-Corasick Binary NFA(低内存)
  - Hyperscan: Intel正则引擎(高性能)
  - Mpse: 多模式搜索抽象接口

- [04_filters](/security/nids/snort3/04_filters) - 快速过滤模块
  - rate_filter: 速率过滤(动态规则动作)
  - sfthreshold: 阈值过滤(事件数限制)
  - detection_filter: 检测率过滤
  - Port/Service/Protocol预过滤

## 相关文档

- [Snort3 整体架构分析](/security/nids/snort3_architecture_analysis) - 完整架构概览
- [framework_module](/security/nids/snort3/framework_module) - 框架模块
- [main_module](/security/nids/snort3/main_module) - 主模块
