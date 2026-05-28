---
type: entity
tags: [snort3, intrusion-detection, pub-sub, network-protocols, logging, linux]
created: 2026-05-27
sources: [github-snort3-pubsub-log]
---

# Snort3 pub_sub / Protocols / Log

## 定义

Snort3 的 **DataBus 发布-订阅系统**（pub_sub）提供进程内事件通信框架，各检测模块通过发布事件（DNS 响应、HTTP body、SSL 元数据等）供其他模块消费。**protocols/** 定义从链路层到应用层的所有协议头结构。**log/** 实现日志基础设施（批量日志、文本日志、脱敏）。**loggers/** 实现 12 种输出插件（CSV、JSON、syslog、PCAP、Unified2 等）。

## 关键要点

### DataBus 事件发布-订阅

- 每个协议域定义 `PubKey`（名称 + 事件数量）和 `EventIds` 枚举
- 事件对象继承 `snort::DataEvent`，提供 `get_packet()` 统一接口
- 发布：`pub_sub.publish(pub_key, event_id, &event)`
- 订阅：DataBus 注册回调函数
- 支持事件：DNS、HTTP（头/body/事务结束）、SSL/TLS、SIP、SSH、FTP、DHCP、应用ID、文件事件、DAQ 消息等

### 协议解析架构

- `PacketManager::decode()` 是解码主入口，调度 `Codec` 插件逐层解析
- `Packet.layers[]` 数组存储每层解码结果（从内层到外层）
- `IpApi` 提供 IPv4/IPv6 统一访问接口，自动处理 IPv6 扩展头链
- `proto_bits` 位图标记已解析的协议，`ip_proto_next` 记录 IP 后的首个传输层协议
- 支持协议：Ethernet、802.1Q VLAN、MPLS、ARP、IPv4/IPv6、TCP、UDP、ICMP、ICMPv6、NDP、GRE、ESP、GENEVE、VXLAN、Teredo、802.11 WLAN、Token Ring、CDP、BPDU、EAPOL、SSL/TLS 等

### 批量日志系统

- 线程本地 `LogBuffer`（阈值 8KB 或 10ms），批量写入避免锁竞争
- 无锁 `BatchQueue` 环形缓冲区（8192 slots）连接前台日志线程和后台写线程
- 后台写线程支持 PCRE2 过滤（"Y" 前缀停止 trace）和 syslog 输出
- `TextLog` 提供缓冲 FILE I/O，支持文件大小滚动（重命名 + 时间戳）

### 脱敏（Obfuscator）

- 按 `(offset, length)` 块集合标记敏感区域，用 'X' 字符填充
- 支持多 buffer key（HTTP body、payload 等分别管理）
- `LogIpAddrs()` 自动对源/目的 IP 脱敏

### Logger 插件体系

- 12 种 Logger 插件，通过 `LogApi`（`PT_LOGGER`）注册
- 基类 `Logger` 定义 `open()/close()/alert()/log()` 接口
- 输出类型：`OUTPUT_TYPE_FLAG__ALERT`（告警）和 `OUTPUT_TYPE_FLAG__LOG`（日志），部分插件两者兼有
- 支持格式：CSV、JSON、简洁文本、完整文本、syslog、Lua JIT 脚本、彩色控制台、UNIX socket、PCAP、hext（十六进制）、Unified2 二进制

### Unified2 二进制格式

- type 114（`UNIFIED2_EVENT3`）包含：event_id、规则 gid:sid:rev、分类、优先级、策略 ID、IP 地址（IPv4/IPv6）、端口、VLAN、MPLS、应用名、HTTP 元数据
- legacy 模式兼容 barnyard2，生成 type 104/105（IPv4/IPv6 事件）
- `U2PseudoHeader` 为纯数据报文生成伪造的 Ethernet/IP/TCP 头

## 相关概念

- [[entities/linux/snort3/snort3-framework]] — DataBus 基类所在框架层
- [[entities/linux/snort3/snort3-codecs]] — Codec 协议解析（PacketManager 调度）
- [[snort3-stream]] — Stream 流重组（flow 跟踪）
- [[entities/linux/snort3/snort3-detection-engine]] — 检测引擎（规则匹配）
- [[entities/linux/snort3/snort3-events-filters]] — 事件与过滤器系统
- [[intrusion-detection-system]] — IDS 概念
- [[linux-network-protocols]] — Linux 网络协议栈
