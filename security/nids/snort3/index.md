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

### 网络检查器
- [network_inspectors](/security/nids/snort3/network_inspectors) - 网络层检查器
  - binder: 流量绑定与服务识别
  - port_scan: 端口扫描检测
  - arp_spoof: ARP欺骗检测
  - normalize: 数据包规范化
  - perf_monitor: 性能监控
  - reputation: IP信誉评估
  - rna: 响应网络分析
  - appid: 应用识别

### 应用层检查器
- [service_inspectors](/security/nids/snort3/service_inspectors) - 应用层协议分析
  - http_inspect: HTTP协议分析与检测
  - dns: DNS协议分析
  - smtp/ftp_telnet/ssh/ssl: 邮件/文件传输/远程访问/加密
  - dce_rpc: DCE/RPC协议分析
  - sip: VoIP协议分析
  - wizard: 协议自动检测

### 连接器与侧信道
- [connectors_and_side_channel](/security/nids/snort3/connectors_and_side_channel) - 通信机制
  - TcpConnector: TCP连接器
  - FileConnector: 文件连接器
  - UnixDomainConnector: Unix域Socket连接器
  - SideChannel: 带外通信框架

### 事件、动作与日志
- [events_actions_loggers](/security/nids/snort3/events_actions_loggers) - 响应与输出
  - Event: 事件封装
  - IpsAction: 动作系统(alert/drop/block/reject/pass)
  - Logger: 日志输出(alert_json/alert_csv/unified2)

### 内存管理与性能分析
- [memory_profiler_target_based](/security/nids/snort3/memory_profiler_target_based) - 资源管理
  - MemoryCap: 内存容量管理
  - Profiler: 时间/规则/内存性能分析
  - HostAttributes: 目标主机属性策略

## 相关文档

- [Snort3 整体架构分析](/security/nids/snort3_architecture_analysis) - 完整架构概览
- [framework_module](/security/nids/snort3/framework_module) - 框架模块
- [main_module](/security/nids/snort3/main_module) - 主模块
