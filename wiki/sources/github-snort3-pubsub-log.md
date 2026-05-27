---
type: source
source-type: github
title: "Snort3 pub_sub + Protocols + Log — 源码分析"
author: "Cisco / Snort Team"
date: 2026-05-27
size: medium
path: ~/workspace/github/snort3/src/pub_sub/ ~/workspace/github/snort3/src/protocols/ ~/workspace/github/snort3/src/log/ ~/workspace/github/snort3/src/loggers/
summary: "Snort3 DataBus 发布-订阅事件系统、协议头定义、网络包解析架构、日志框架与 12 种输出插件的完整源码分析"
---

# Snort3 pub_sub / Protocols / Log 源码分析

## 核心文件列表

### pub_sub/ (61 files)

| 文件 | 关键内容 |
|------|---------|
| `dns_events.h/cc` | DNS 响应数据事件（IP、FQDN、TTL） |
| `http_events.h/cc` | HTTP 头部/元数据（Cookie、URI、Method） |
| `http_body_event.h/cc` | HTTP 请求/响应 body 分块 |
| `http_transaction_end_event.h/cc` | HTTP 事务结束事件 |
| `ssl_events.h` | SSL/TLS 元数据（SNI、CN、版本、密码套件） |
| `ssh_events.h/cc` | SSH 状态机、算法协商 |
| `sip_events.h/cc` | SIP 对话、会话、媒体数据 |
| `ftp_events.h` | FTP 请求/响应、被动模式端口 |
| `detection_events.h/cc` | IPS 规则事件（规则消息、引用） |
| `appid_events.h` | 应用 ID 变化追踪（bitset 模式） |
| `daq_message_event.h` | DAQ SOF/EOF 消息事件 |
| `file_events.h` | 文件指纹、签名、 verdict 事件 |
| `intrinsic_event_ids.h` | 内置事件 ID（Packet/Flow/Thread/SSL） |
| `data_decrypt_event.h` | TLS 解密数据事件 |
| `dhcp_events.h` | DHCP 地址分配、选项 55/60 |

### protocols/ (39 files)

| 文件 | 关键内容 |
|------|---------|
| `protocol_ids.h` | 所有协议 ID 枚举（IpProtocol + ProtocolId） |
| `packet.h` | Packet 结构体 — 解码后数据包 |
| `packet_manager.h/cc` | Codec 调度、decode/encode 主入口 |
| `layer.h/cc` | 包层抽象（Layer 数组） |
| `ip.h/ip.cc` | IpApi — IPv4/IPv6 统一访问接口 |
| `ipv4.h` | IPv4 头结构 |
| `ipv6.h` | IPv6 头 + 扩展头（Fragment、Routing） |
| `tcp.h` | TCP 头结构 |
| `udp.h` | UDP 头结构 |
| `icmp4.h` | ICMPv4 头（含嵌入 IP） |
| `icmp6.h` | ICMPv6 头 + NDP 选项 |
| `eth.h` | Ethernet 头 |
| `vlan.h` | 802.1Q VLAN tag |
| `mpls.h` | MPLS 标签 |
| `arp.h` | ARP 头 |
| `tcp_options.h/cc` | TCP 选项迭代器 |
| `ipv4_options.h/cc` | IPv4 选项迭代器 |
| `ssl.h/ssl.cc` | SSL/TLS 记录解析（SSLv2/SSLv3/TLS 1.0-1.3） |
| `geneve.h` | GENEVE 隧道头（RFC 8926） |
| `gre.h` | GRE 隧道头 |
| `teredo.h` | Teredo IPv6 隧道 |
| `eapol.h` | 802.1X EAPOL |

### log/ (19 files)

| 文件 | 关键内容 |
|------|---------|
| `log.h/cc` | 日志宏（LogMessage/WarningMessage/ErrorMessage） |
| `batched_logger.h/cc` | 线程本地批量日志 → 无锁环形队列 → 后台写线程 |
| `text_log.h/cc` | 缓冲文本流（文件滚动、大小上限） |
| `obfuscator.h/cc` | 数据脱敏（offset-length 块集合） |
| `messages.h/cc` | ConfigLogger 格式化配置输出 |
| `log_text.cc` | 包数据文本日志（HexAsciiLayout） |
| `log_stats.h/cc` | Snort 统计信息 |
| `unified2.h` | Unified2 二进制格式定义 |
| `u2_packet.h/cc` | Unified2 pseudo-header 生成 |

### loggers/ (14 files)

| 文件 | 关键内容 |
|------|---------|
| `loggers.h` | Logger 基类 + API 注册 |
| `loggers.cc` | load_loggers() 插件加载 |
| `alert_csv.cc` | CSV 格式告警（52 种可选字段） |
| `alert_json.cc` | JSON 格式告警 |
| `alert_fast.cc` | 简洁文本告警 + 包数据 dump |
| `alert_full.cc` | 完整告警（含所有包头） |
| `alert_syslog.cc` | syslog 输出 |
| `alert_luajit.cc` | Lua JIT 脚本输出 |
| `alert_talos.cc` | Talos 彩色控制台格式 |
| `alert_unixsock.cc` | UNIX 域 socket 二进制输出 |
| `log_pcap.cc` | tcpdump 兼容 PCAP 文件 |
| `log_codecs.cc` | 按层协议诊断日志 |
| `log_hext.cc` | DAQ hext 十六进制格式 |
| `unified2.cc` | Unified2 二进制格式（barnyard2 兼容） |

---

## 架构设计要点

### DataBus 发布-订阅机制

每个发布者定义 `PubKey` + `EventIds` 枚举：

```cpp
// 例：DNS 事件
struct DnsEventIds {
    enum : unsigned { DNS_RESPONSE_DATA, DNS_RESPONSE, num_ids };
};
const snort::PubKey { "dns", DnsEventIds::num_ids };

// 发布事件
DnsResponseEvent event(session, packet);
pub_sub.publish(dns_pub_key, DnsEventIds::DNS_RESPONSE, &event);
```

订阅者通过 DataBus 注册回调函数。所有事件继承 `snort::DataEvent`，提供 `get_packet()` 统一接口。

### Packet 解析流程

```
PacketManager::decode()
  → Codec::decode() 每层协议
  → push_layer() 注册到 Packet.layers[]
  → IpApi::set_inner_ip_api() / set_outer_ip_api() 导航 IP 头
  → proto_bits 更新协议标记位
  → ip_proto_next 记录 IP 之后的首个传输层协议
```

IPv6 扩展头（HopByHop、DstOptions、Routing、Fragment、Auth、ESP）解析后仍在 layers 中，但不改变 `ip_proto_next`。

### 批量日志架构

```
LogMessage()
  → BatchedLogger::log()
  → ThreadLocal LogBuffer (阈值 8KB 或 10ms)
  → LogBatch 进入无锁环形队列 (8192 slots)
  → writer_thread_func 后台线程
  → syslog() 或 fwrite()
  → PCRE2 过滤 "Y" 前缀 PacketTracer 消息
```

### Logger 插件系统

所有 Logger 继承 `Logger` 基类，通过 `LogApi`（含 `PT_LOGGER`）注册。输出类型分 `OUTPUT_TYPE_FLAG__ALERT` 和 `OUTPUT_TYPE_FLAG__LOG`，部分插件两者兼有（unified2）。

---

## 关键数据结构

### Packet 结构

```cpp
struct Packet {
    Flow* flow;
    uint32_t packet_flags;     // PKT_* 标记
    uint32_t proto_bits;       // PROTO_BIT__* 协议位图
    uint16_t alt_dsize;        // 检测 size 限制
    uint8_t num_layers;        // 解码层数
    IpProtocol ip_proto_next;  // IP 后的首个传输协议

    const DAQ_PktHdr_t* pkth;
    const uint8_t* pkt;
    uint32_t pktlen;
    const uint8_t* data;       // payload 指针
    uint16_t dsize;            // payload 大小

    DecodeData ptrs;           // 便捷指针集合
    Layer* layers;             // 解码层数组
};
```

### Layer 结构

```cpp
struct Layer {
    const uint8_t* start;     // 层起始指针
    ProtocolId prot_id;       // 协议 ID
    uint16_t length;          // 层长度
};
```

### TextLog 滚动

- `maxBuf`: 内存缓冲区大小（默认 stdout 用 300KB）
- `maxFile`: 文件大小上限（滚动时重命名 + 时间戳后缀）
- `is_critical`: 是否关键文件（关键文件不允许写失败）

### Obfuscator 脱敏

```cpp
// 按 (offset, length) 块集合脱敏
struct ObfuscatorBlock { uint32_t offset; uint32_t length; };
// 'X' 字符填充
// 支持多 buffer key（std::unordered_map<std::string, ObSet>）
```

---

## 相关页面

- [[snort3-pubsub-log]] — 实体页面
- [[snort3-framework]] — 框架层（DataBus 基类）
- [[snort3-codecs]] — Codec 协议解析
- [[snort3-stream]] — Stream 流重组
- [[snort3-detection-engine]] — 检测引擎
- [[intrusion-detection-system]] — IDS 概念
