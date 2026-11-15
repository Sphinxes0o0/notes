---
title: "Snort 3 · Inspector、协议与规则解析"
description: "附录MM：IpsAction和响应处理详细分析 — 附录NC：规则解析系统"
---

# Snort 3 · Inspector、协议与规则解析

[返回总目录](../snort3_architecture_analysis)

## 附录MM：IpsAction和响应处理详细分析 {#附录mm-ipsaction和响应处理详细分析}

### MM.1 Action类型 {#mm-1-action类型}

```cpp
enum IpsActionPriority {
    IAP_OTHER = 1,
    IAP_LOG = 10,
    IAP_ALERT = 20,
    IAP_REWRITE = 30,
    IAP_DROP = 40,
    IAP_BLOCK = 50,
    IAP_REJECT = 60,
    IAP_PASS = 70
};
```

| Action | 文件 | 行为 |
|--------|------|------|
| alert | act_alert.cc | 日志并生成告警 |
| log | act_log.cc | 仅日志 |
| pass | act_pass.cc | 标记跳过检查 |
| drop | act_drop.cc | 丢弃数据包并告警 |
| block | act_block.cc | 阻止会话 |
| reject | act_reject.cc | 发送TCP RST或ICMP不可达 |
| react | act_react.cc | 发送HTTP禁止页面并重置 |
| replace | act_replace.cc | 覆盖数据包内容 |

### MM.2 Active响应接口 {#mm-2-active响应接口}

```cpp
class Active {
    void send_reset(Packet*, EncodeFlags);        // 发送TCP RST
    void send_unreach(Packet*, UnreachResponse); // 发送ICMP不可达
    void kill_session(Packet*, EncodeFlags);     // 杀死会话
    void queue(ActiveAction*, Packet*);          // 队列延迟动作
};
```

**ICMP不可达类型**:
```cpp
enum UnreachResponse { NET, HOST, PORT, FWD, HOST_PREC, PREC_CUT };
```

### MM.3 主要规则选项 {#mm-3-主要规则选项}

| 选项 | 文件 | 用途 |
|------|------|------|
| content | ips_content.cc | 基本模式匹配(Boyer-Moore) |
| pcre | ips_pcre.cc | PCRE正则表达式 |
| flow | ips_flow.cc | 会话状态检查 |
| flowbits | ips_flowbits.cc | 布尔标志管理 |
| byte_test | ips_byte_test.cc | 提取并比较字节 |
| byte_jump | ips_byte_jump.cc | 提取字节并移动光标 |
| detection_filter | ips_detection_filter.cc | 速率阈值 |
| http_* | ips_http_*.cc | HTTP相关匹配 |

### MM.4 Fast Pattern {#mm-4-fast-pattern}

```cpp
content:"abc", fast_pattern;  // 快速模式用于MPM
content:"abc", fast_pattern_only;  // 仅MPM，不用于规则评估
```

### MM.5 规则评估流程 {#mm-5-规则评估流程}

```
数据包
   │
   ▼
DetectionEngine::detect()
   │
   ├── 快速模式匹配 (MPM/AC)
   │     │
   │     ▼
   │    候选规则
   │
   ├── 规则选项评估
   │     ├── content (Boyer-Moore)
   │     ├── pcre (正则)
   │     ├── flow (会话状态)
   │     └── ...
   │
   └── IpsAction::exec()
         │
         ▼
       告警/丢弃/阻止/重置
```

---

## 附录MN：DAQ接口详细分析 {#附录mn-daq接口详细分析}

### MN.1 DAQ模块API {#mn-1-daq模块api}

**DAQ实例** (SFDAQInstance):
```cpp
class SFDAQInstance {
    std::string input_spec;          // 输入规范
    uint32_t instance_id;
    DAQ_Instance_h instance;         // DAQ实例句柄
    DAQ_Msg_h* daq_msgs;           // 消息批次
    uint32_t batch_size;             // 每批次消息数
};
```

### MN.2 数据包获取模式 {#mn-2-数据包获取模式}

```cpp
enum SFDAQMode {
    SFDAQ_MODE_UNSET,
    SFDAQ_MODE_PASSIVE,   // 被动嗅探
    SFDAQ_MODE_INLINE,    // 在线部署
    SFDAQ_MODE_READ_FILE, // 从文件读取
};
```

### MN.3 消息类型 {#mn-3-消息类型}

- `DAQ_MSG_TYPE_PACKET` - 常规数据包
- `DAQ_MSG_TYPE_SOF` - Flow开始
- `DAQ_MSG_TYPE_EOF` - Flow结束

### MN.4 DAQ与Snort接口 {#mn-4-daq与snort接口}

**数据包处理流程**:
```
Analyzer::analyze()
   │
   ▼
process_messages()
   │  daq_instance->receive_messages()
   │
   ▼
process_daq_pkt_msg()
   │  PacketManager::decode()
   │  process_packet()
   │
   ▼
post_process_daq_pkt_msg()
   │  distill_verdict()
   │
   ▼
daq_instance->finalize_message()  // 应用判决
```

### MN.5 判决类型 {#mn-5-判决类型}

- `DAQ_VERDICT_PASS` - 允许
- `DAQ_VERDICT_BLOCK` - 阻止
- `DAQ_VERDICT_REPLACE` - 替换
- `DAQ_VERDICT_WHITELIST` - 白名单
- `DAQ_VERDICT_BLACKLIST` - 黑名单
- `DAQ_VERDICT_IGNORE` - 忽略

### MN.6 关键配置参数 {#mn-6-关键配置参数}

```lua
daq = {
    snaplen = 1518,        -- 最大抓包长度
    batch_size = 64,       -- 每批次消息数
    module_dirs = {},       -- DAQ模块目录
    inputs = {},           -- 输入源
    modules = {}           -- DAQ模块配置
}
```

### MN.7 内置DAQ模块 {#mn-7-内置daq模块}

| 模块 | 类型 | 说明 |
|------|------|------|
| daq_file | 文件 | 从文件/pcap读取 |
| daq_hext | 文本 | Hex/text格式数据 |

---

## 附录ME：HTTP Inspect模块详细分析 {#附录me-http-inspect模块详细分析}

### ME.1 HttpInspect类结构 {#me-1-httpinspect类结构}

**文件**: `src/service_inspectors/http_inspect/http_inspect.h`

```cpp
class HttpInspect : public HttpInspectBase {
    HttpStreamSplitter splitter[2] = { { true, this }, { false, this } };  // C2S & S2C
    const HttpParaList* const params;
    ScriptFinder* script_finder = nullptr;
    // Extra data callbacks
    const uint32_t xtra_trueip_id;
    const uint32_t xtra_uri_id;
    const uint32_t xtra_host_id;
    const uint32_t xtra_jsnorm_id;
};
```

### ME.2 HTTP消息解析 {#me-2-http消息解析}

**消息类型状态机** (http_common.h):
```cpp
enum SectionType {
    SEC_REQUEST = 2, SEC_STATUS, SEC_HEADER, SEC_BODY_CL, SEC_BODY_CHUNK,
    SEC_TRAILER, SEC_BODY_OLD, SEC_BODY_HX
};
```

**解析流程**:
- `SEC_REQUEST` → `HttpMsgRequest` (解析方法、URI、版本)
- `SEC_STATUS` → `HttpMsgStatus` (解析状态码、原因短语)
- `SEC_HEADER` → `HttpMsgHeader` (解析头部)
- `SEC_BODY_CL` → `HttpMsgBodyCl` (Content-Length body)
- `SEC_BODY_CHUNK` → `HttpMsgBodyChunk` (Chunked body)
- `SEC_TRAILER` → `HttpMsgTrailer` (尾部，处理RFC 7230禁止的头)

### ME.3 缓冲区类型 {#me-3-缓冲区类型}

```cpp
enum HTTP_RULE_OPT {
    HTTP_BUFFER_URI, HTTP_BUFFER_RAW_URI, HTTP_BUFFER_RAW_HEADER,
    HTTP_BUFFER_HEADER, HTTP_BUFFER_COOKIE, HTTP_BUFFER_RAW_COOKIE,
    HTTP_BUFFER_CLIENT_BODY, HTTP_BUFFER_RAW_BODY, HTTP_BUFFER_METHOD,
    HTTP_BUFFER_STAT_CODE, HTTP_BUFFER_STAT_MSG, HTTP_BUFFER_TRUE_IP,
    HTTP_BUFFER_VERSION, HTTP_BUFFER_USER_AGENT_STR, HTTP_BUFFER_REFERER_STR,
    BUFFER_JS_DATA, BUFFER_VBA_DATA,
    HTTP_BUFFER_DECODED_URI, HTTP_BUFFER_REQUEST_SIZE, HTTP_BUFFER_RESPONSE_SIZE
};
```

### ME.4 URI规范化 {#me-4-uri规范化}

**规范化步骤** (http_uri_norm.cc):
1. **Percent解码** - `%HH` 转换为原始字节
2. **UTF-8处理** - 多字节UTF-8序列处理
3. **双解码** - IIS双编码输入
4. **字符替换** - 反斜杠转斜杠、加号转空格
5. **路径简化** - 解析 `/./` 和 `/../`

**配置参数** (http_module.h):
```cpp
struct UriParam {
    bool percent_u = false;           // %u编码
    bool utf8 = true;                // UTF-8解码
    bool iis_double_decode = true;    // IIS双解码
    int oversize_dir_length = 300;    // 目录遍历告警阈值
    bool simplify_path = true;        // 路径简化
};
```

### ME.5 JavaScript规范化 {#me-5-javascript规范化}

**js_normalize()** (http_js_norm.cc):
1. 搜索 `<SCRIPT` 标签
2. 识别脚本类型 (JavaScript/ECMAScript/VBScript)
3. 解码JavaScript内容
4. 跟踪混淆告警

**配置**:
```cpp
struct JsNormParam {
    bool normalize_javascript = false;
    int max_javascript_whitespaces = 200;
};
```

### ME.6 流分割器集成 {#me-6-流分割器集成}

**HttpStreamSplitter** (is_paf() = true):
- `scan()` - 调用cutter处理数据
- `reassemble()` - 合并部分数据为完整section
- 支持PAF (Protocol Aware Flushing)

### ME.7 关键配置参数 {#me-7-关键配置参数}

```lua
http_inspect = {
    request_depth = 6144,           -- 请求深度
    response_depth = 6144,          -- 响应深度
    maximum_headers = 200,          -- 最大头数量
    maximum_pipelined_requests = 99, -- 最大管道请求
    unzip = true,                   -- GZIP/DEFLATE解压
    normalize_utf = true,            -- UTF-8规范化
    decompress_pdf = false,
    decompress_swf = false,
    decompress_zip = false,
    decompress_vba = false
}
```

---

## 附录MF：DNS检测模块详细分析 {#附录mf-dns检测模块详细分析}

### MF.1 DnsInspector类结构 {#mf-1-dnsinspector类结构}

```cpp
class Dns : public snort::Inspector {
    const DnsConfig* config = nullptr;
    static unsigned pub_id;
};
```

### MF.2 DNS消息解析 {#mf-2-dns消息解析}

**DNS头部结构** (dns.h):
```cpp
struct DNSHdr {
    uint16_t id = 0;
    uint16_t flags = 0;       // QR, OPCODE, AA, TC, RD, RA, Z, RCODE
    uint16_t questions = 0;
    uint16_t answers = 0;
    uint16_t authorities = 0;
    uint16_t additionals = 0;
};
```

**解析流程**:
- `ParseDNSHeader()` - 12字节头部解析
- `ParseDNSQuestion()` - 问题段解析
- `ParseDNSName()` - DNS名称解析(支持压缩指针)

### MF.3 记录类型处理 {#mf-3-记录类型处理}

| 类型 | 值 | 解码 |
|------|-----|------|
| A | 0x0001 | IPv4地址(4字节) |
| AAAA | 0x001C | IPv6地址(16字节) |
| CNAME | 0x0005 | 域名 |
| MX | 0x000F | 优先级+域名 |
| PTR | 0x000C | 域名 |
| TXT | 0x0010 | 长度前缀字符串 |
| SOA | 0x0006 | 域名 |
| NS | 0x0002 | 域名 |
| SRV | 0x0021 | 目标域名 |
| OPT | 0x0029 | EDNS0 (DO标志) |
| DS | 0x002B | 算法+摘要类型 |
| DNSKEY | 0x0030 | 算法 |

### MF.4 TCP/UDP处理 {#mf-4-tcp-udp处理}

**UDP处理**:
- 事务ID跟踪 (`add_to_udp_flow()` / `is_in_udp_flow()`)
- 最大UDP净荷: `MAX_UDP_PAYLOAD = 0x1FFF`

**TCP处理**:
- `DnsSplitter` - 2字节长度前缀
- 支持PAF (Protocol Aware Flushing)
- 支持多个DNS事务在单个TCP连接中

### MF.5 DNS over HTTP/QUIC {#mf-5-dns-over-http-quic}

跟踪统计:
- `dns_over_udp` / `dns_over_tcp`
- `dns_over_http1` / `dns_over_http2` / `dns_over_http3`
- `dns_over_quic`

### MF.6 缓冲区类型和事件 {#mf-6-缓冲区类型和事件}

**事件类型**:
```cpp
struct DnsEventIds {
    DNS_RESPONSE_DATA,  // FqdnTtl和IP映射
    DNS_RESPONSE,       // 完整DNS响应信息
};
```

### MF.7 关键配置 {#mf-7-关键配置}

```lua
dns = {
    publish_response = false  -- 启用DNS响应解析和事件发布
}
```

---

## 附录MG：SSL/TLS检测模块详细分析 {#附录mg-ssl-tls检测模块详细分析}

### MG.1 SslInspector类结构 {#mg-1-sslinspector类结构}

```cpp
class Ssl : public Inspector {
    SSL_PROTO_CONF* config;
    // 两个方向各一个splitter
    StreamSplitter* get_splitter(bool c2s) override
        { return new SslSplitter(c2s); }
};
```

### MG.2 SSL/TLS握手解析 {#mg-2-ssl-tls握手解析}

**入口**: `SSL_decode()` (ssl.cc)

**版本检测**:
- SSLv2: `pkt[0] & 0x80` 或 `pkt[0] & 0x40`
- TLS: 第一个字节 `0x16` 和第二个字节 `0x03`

**握手类型**:
| 类型 | 名称 | 标志 |
|------|------|------|
| 1 | CLIENT_HELLO | `SSL_CLIENT_HELLO_FLAG` |
| 2 | SERVER_HELLO | `SSL_SERVER_HELLO_FLAG` |
| 11 | CERTIFICATE | `SSL_CERTIFICATE_FLAG` |
| 12 | SERVER_KEYX | `SSL_SERVER_KEYX_FLAG` |
| 16 | CLIENT_KEYX | `SSL_CLIENT_KEYX_FLAG` |

### MG.3 会话状态标志 {#mg-3-会话状态标志}

```cpp
#define SSL_CHANGE_CIPHER_FLAG    0x00000001
#define SSL_ALERT_FLAG           0x00000002
#define SSL_CLIENT_HELLO_FLAG    0x00000008
#define SSL_SERVER_HELLO_FLAG    0x00000010
#define SSL_CERTIFICATE_FLAG     0x00000020
#define SSL_SERVER_KEYX_FLAG     0x00000040
#define SSL_CLIENT_KEYX_FLAG     0x00000080
#define SSL_ENCRYPTED_FLAG       0x01000000
```

### MG.4 证书解析 {#mg-4-证书解析}

使用OpenSSL提取:
- **Subject Info**: CN, Organizational Unit
- **Issuer Info**: RFC 2253格式
- **SNI**: 从Client Hello扩展提取host_name

### MG.5 Heartbleed检测 {#mg-5-heartbleed检测}

```cpp
case SSL_HEARTBEAT_REC:
    if (heartbeat->type == SSL_HEARTBEAT_REQUEST) {
        if (hblen > max_hb_len)
            *alert_flags = SSL_ALERT_HEARTBLEED_REQUEST;
    }
```

### MG.6 加密流量处理 {#mg-6-加密流量处理}

```cpp
if (SSLPP_is_encrypted(config, ssn_flags | new_flags, packet)) {
    if (!config->max_heartbeat_len) {
        Stream::stop_inspection(packet->flow, ...);
    }
}
```

### MG.7 关键配置 {#mg-7-关键配置}

```lua
ssl = {
    trust_servers = false,           -- 信任服务器证书
    max_heartbeat_length = 0         -- 0=禁用heartbleed检测
}
```

**IPS选项**:
- `ssl_version`: `sslv2`, `sslv3`, `tls1.0`, `tls1.1`, `tls1.2`
- `ssl_state`: `client_hello`, `server_hello`, `client_keyx`, `server_keyx`

---

## 附录MH：Binder和Wizard服务检测 {#附录mh-binder和wizard服务检测}

### MH.1 Binder绑定规则 {#mh-1-binder绑定规则}

**BindWhen结构** (binding.h):
```cpp
struct BindWhen {
    PolicyId ips_id;
    unsigned protos;              // 协议位掩码
    Role role;                   // BR_CLIENT, BR_SERVER, BR_EITHER
    std::string svc;             // 服务名
    sfip_var_t* src_nets;      // 源网络
    sfip_var_t* dst_nets;      // 目标网络
    PortBitSet src_ports;       // 源端口
    PortBitSet dst_ports;       // 目标端口
    // ...
};
```

**BindUse结构**:
```cpp
struct BindUse {
    enum Action { BA_RESET, BA_BLOCK, BA_ALLOW, BA_INSPECT };
    enum What { BW_NONE, BW_PASSIVE, BW_CLIENT, BW_SERVER, BW_STREAM, BW_WIZARD, BW_GADGET };
    std::string svc;
    std::string type;
    std::string name;
    Action action;
    What what;
    Inspector* inspector;
};
```

### MH.2 Wizard服务检测 {#mh-2-wizard服务检测}

**检测方法**:

| 方法 | 类型 | 语法 |
|------|------|------|
| **Spells** | 文本模式 | `*` 匹配任意 |
| **Hexes** | 二进制模式 | `?` 匹配1字节, `\|FF\|` 匹配0xFF |
| **Curses** | 状态机 | 协议结构验证 |

### MH.3 支持的Curses {#mh-3-支持的curses}

| Curse | 服务 | 说明 |
|-------|------|------|
| `dce_udp` | dcerpc | DCE/RPC over UDP |
| `dce_tcp` | dcerpc | DCE/RPC over TCP |
| `dce_smb` | netbios-ssn | SMB/DCE-RPC over SMB |
| `mms` | mms | IEC 61850 MMS协议 |
| `opcua` | opcua | OPC统一架构 |
| `s7commplus` | s7commplus | Siemens S7Comm Plus |
| `socks` | socks | SOCKS代理(v4, v4a, v5) |
| `sslv2` | ssl | SSLv2 Client Hello |

### MH.4 服务检测流程 {#mh-4-服务检测流程}

```
数据包到达
     │
     ▼
Binder::handle_flow_setup()
     │
     ▼
get_bindings() - 评估所有绑定
     │
     ▼
check_all() - 验证BindWhen条件
     │
     ▼
stuff.apply_*() - 应用到flow
     │
     ▼
如果wizard被设置:
     │
     ▼
MagicSplitter::scan() - 流数据扫描
     │
     ▼
Wizard::cast_spell() - 尝试hex/spell/curse检测
     │
     ▼
如果匹配:
     │
     ▼
flow.set_service() - 设置服务
flow.set_gadget() - 设置服务inspector
```

### MH.5 配置示例 {#mh-5-配置示例}

```lua
binder = {
    -- Wizard捕获未知服务
    { when = { proto = tcp, role = any }, use = { type = wizard } }
    -- 已知服务绑定
    { when = { proto = tcp, ports = 22 }, use = { type = ssh } }
    { when = { proto = tcp, ports = 80 }, use = { type = http } }
    { when = { proto = tcp, ports = 443 }, use = { type = ssl } }
}

wizard = {
    max_search_depth = 8192,
    curses = { "dce_smb", "dce_tcp", "dce_udp", "mms", "opcua", "s7commplus", "socks", "sslv2" }
}
```

---

## 附录MZ：Stream UDP/ICMP和IP分片重组 {#附录mz-stream-udp-icmp和ip分片重组}

### MZ.1 Stream UDP模块 {#mz-1-stream-udp模块}

**UdpSession类** (stream/udp/udp_session.h):
```cpp
class UdpSession : public Session {
    uint32_t payload_bytes_seen_client = 0;
    uint32_t payload_bytes_seen_server = 0;
    // 无重组 - UDP是数据报协议
};
```

**关键特性**:
- 跟踪双向有效载荷字节数
- 发布 `StreamEventIds::UDP_BIDIRECTIONAL` 事件
- 会话超时: 默认30秒

### MZ.2 Stream ICMP模块 {#mz-2-stream-icmp模块}

**IcmpSession类** (stream/icmp/icmp_session.h):
```cpp
class IcmpSession : public Session {
    uint8_t echo_count = 0;
    // 处理ICMP不可达消息,标记相关会话为dead
};
```

**关键特性**:
- 处理ICMP不可达消息中的嵌入协议
- 查找原始会话并标记为不可达
- 会话超时: 默认60秒

### MZ.3 IP分片重组 (Defrag) {#mz-3-ip分片重组-defrag}

**FragTracker结构** (stream/ip/ip_session.h):
```cpp
struct FragTracker {
    uint16_t frag_flags;        // FRAG_GOT_FIRST, FRAG_GOT_LAST等
    uint32_t frag_bytes;        // 累积字节数
    uint32_t calculated_size;   // 预期总大小
    Fragment* fraglist;          // 分片链表
    uint8_t frag_policy;        // 重组策略
};
```

**重组策略** (stream/ip/stream_ip.h):
```cpp
enum { FRAG_POLICY_FIRST, FRAG_POLICY_LINUX, FRAG_POLICY_BSD,
       FRAG_POLICY_BSD_RIGHT, FRAG_POLICY_LAST, FRAG_POLICY_WINDOWS,
       FRAG_POLICY_SOLARIS };
```

**重叠处理**:
- FIRST/LINUX/WINDOWS: 新分片移动,旧分片截断
- BSD_RIGHT/LAST: 旧分片保留,新分片截断

**关键方法**:
```cpp
Defrag::process()        // 主入口
Defrag::insert()         // 插入分片,处理重叠
Defrag::FragRebuild()    // 重建完整数据包
```

**配置参数**:
```lua
stream_ip = {
    max_frags = 8192,           -- 最大同时分片数
    max_overlaps = 0,           -- 每数据报最大重叠(0=无限)
    min_frag_length = 0,        -- 分片最小长度
    policy = "linux",           -- 重组策略
    session_timeout = 60
}
```

---

## 附录NA：Packet数据结构和Codec框架 {#附录na-packet数据结构和codec框架}

### NA.1 Packet结构 (protocols/packet.h) {#na-1-packet结构-protocols-packet-h}

```cpp
struct Packet {
    Flow* flow;                    // 会话跟踪引用
    uint64_t packet_flags;       // 数据包标志位
    const DAQ_PktHdr_t* pkth;   // DAQ数据包头
    const uint8_t* pkt;          // 原始数据包
    uint32_t pktlen;             // 原始长度
    const uint8_t* data;        // 净荷指针
    uint16_t dsize;              // 净荷大小
    DecodeData ptrs;             // 解码信息
    Layer* layers;               // 解码层数组
    uint8_t num_layers;         // 层数量
    IpProtocol ip_proto_next;   // 下一层协议
};
```

**关键Packet Flags**:
```cpp
PKT_REBUILT_FRAG    = 0x00000001  // 重组的分片
PKT_REBUILT_STREAM  = 0x00000002  // 重组的流
PKT_STREAM_EST      = 0x00000008  // 来自已建立会话
PKT_FROM_SERVER     = 0x00000040  // 来自服务器
PKT_FROM_CLIENT     = 0x00000080  // 来自客户端
```

### NA.2 DecodeData结构 (framework/decode_data.h) {#na-2-decodedata结构-framework-decode-data-h}

```cpp
struct DecodeData {
    const snort::tcp::TCPHdr* tcph = nullptr;
    const snort::udp::UDPHdr* udph = nullptr;
    const snort::icmp::ICMPHdr* icmph = nullptr;
    uint16_t sp = 0;              // 源端口
    uint16_t dp = 0;              // 目标端口
    PktType type = PktType::NONE;
    snort::ip::IpApi ip_api;
};
```

### NA.3 CodecData结构 (framework/codec.h) {#na-3-codecdata结构-framework-codec-h}

```cpp
struct CodecData {
    ProtocolId next_prot_id;      // 下一层协议
    uint16_t lyr_len = 0;       // 当前层有效长度
    uint16_t invalid_bytes = 0; // 层间无效字节
    uint32_t proto_bits = 0;    // 协议位掩码
    uint8_t ip_layer_cnt = 0;
    bool tunnel_bypass = false;
};
```

### NA.4 Codec基类 (framework/codec.h) {#na-4-codec基类-framework-codec-h}

```cpp
class Codec {
    virtual bool decode(const RawData&, CodecData&, DecodeData&) = 0;
    virtual bool encode(...);
    virtual void update(...);
    virtual void log(TextLog*, const uint8_t*, uint16_t);
};
```

**Codec链式调用流程**:
```
PacketManager::decode()
    │
    ▼
while (codec->decode(raw, codec_data, ptrs)) {
    push_layer();           // 添加解码层
    p->proto_bits |= ...;  // 更新协议位
    raw.len -= ...;        // 缩小缓冲区
    raw.data += ...;       // 移动指针
}
    │
    ▼
p->data = raw.data;       // 设置净荷
p->dsize = raw.len;       // 设置净荷大小
```

### NA.5 Layer结构 (protocols/layer.h) {#na-5-layer结构-protocols-layer-h}

```cpp
struct Layer {
    const uint8_t* start;     // 层起始指针
    ProtocolId prot_id;       // 协议ID
    uint16_t length;         // 层长度
};
```

---

## 附录NB：AppId应用识别模块 {#附录nb-appid应用识别模块}

### NB.1 AppId类结构 {#nb-1-appid类结构}

**AppIdInspector** (network_inspectors/appid/):
```cpp
class AppIdInspector : public Inspector {
    AppIdSession* session;  // 应用识别会话
};
```

**AppIdSession** (appid_session.h):
```cpp
class AppIdSession {
    ServiceDetector* service_detector;
    ClientDetector* client_detector;
    AppIdSessionApi api;  // 公共API
};
```

### NB.2 应用识别流程 {#nb-2-应用识别流程}

```
do_application_discovery()
    │
    ├── do_pre_discovery()      -- 会话设置
    ├── do_discovery()          -- 核心识别
    │     ├── do_port_based_discovery()    -- 端口识别
    │     ├── do_host_port_based_discovery() -- 主机/端口缓存
    │     └── detect_on_first_pkt()        -- 首包检测
    └── do_post_discovery()     -- 事件发布
```

### NB.3 AppInfo表 {#nb-3-appinfo表}

**AppInfoTableEntry** (app_info_table.h):
```cpp
class AppInfoTableEntry {
    AppId appId;              // 主App ID
    uint32_t serviceId;       // 服务组件ID
    uint32_t clientId;        // 客户端组件ID
    uint32_t payloadId;       // 净荷组件ID
    char* app_name;           // 人类可读名称
};
```

**App ID范围**:
- SF_APPID_BUILDIN_MAX = 30000 (内置)
- SF_APPID_CSD_MIN = 1000000 (客户端/服务端检测器)
- SF_APPID_DYNAMIC_MIN = 2000000 (动态)

### NB.4 内置检测器 {#nb-4-内置检测器}

**Service Detectors** (service_plugins/):
- service_ssl.cc - HTTPS/SSL检测
- service_dns.cc - DNS检测
- service_ftp.cc - FTP检测
- service_ssh.cc - SSH检测

**Client Detectors** (client_plugins/):
- client_app_rtp.cc - RTP客户端
- client_app_vnc.cc - VNC客户端

### NB.5 DNS应用识别 {#nb-5-dns应用识别}

**DnsSession** (appid_dns_session.h):
```cpp
class AppIdDnsSession {
    uint8_t state;           // DNS_GOT_QUERY|RESPONSE
    uint16_t id;             // DNS事务ID
    uint16_t record_type;    // 记录类型(A, AAAA等)
    bool doh;               // DNS-over-HTTPS标志
};
```

### NB.6 关键配置 {#nb-6-关键配置}

```lua
appid = {
    app_detector_dir = "/path/to/detectors",
    tp_appid_path = "/path/to/tp/lib",
    tp_appid_config = "/path/to/config",
    memcap = 1048576,
    log_stats = false
}
```

---

## 附录NC：规则解析系统 {#附录nc-规则解析系统}

### NC.1 规则结构 {#nc-1-规则结构}

```
alert tcp $HOME_NET any -> $EXTERNAL_NET $HTTP_PORTS
(msg:"..."; content:"foo"; ...)
^-----^  ^---^  ^------^  ^  ^------------^  ^--------^
action  proto  src_nets   dir  dst_nets      rule body
```

### NC.2 解析流程 {#nc-2-解析流程}

```
parse_rule_init()      -- 初始化
     │
     ▼
parse_rule_type()     -- 解析动作
     │
     ▼
parse_rule_proto()    -- 解析协议
     │
     ▼
parse_rule_nets()     -- 解析IP
     │
     ▼
parse_rule_ports()    -- 解析端口
     │
     ▼
parse_rule_dir()      -- 解析方向
     │
     ▼
parse_rule_opt_*()    -- 解析规则选项
     │
     ▼
addRtnToOtn()        -- 链接RTN和OTN
```

### NC.3 RuleTreeNode (RTN) {#nc-3-ruletreenode-rtn}

```cpp
struct RuleTreeNode {
    RuleFpList* rule_func;     // 匹配函数列表
    sfip_var_t* sip;          // 源IP变量
    sfip_var_t* dip;          // 目标IP变量
    PortObject* src_portobject;
    PortObject* dst_portobject;
    snort::IpsAction::Type action;
};
```

### NC.4 OptTreeNode (OTN) {#nc-4-opttreenode-otn}

```cpp
struct OptTreeNode {
    SigInfo sigInfo;           // gid, sid, rev, msg
    OptFpList* opt_func;      // 检测选项函数列表
    THD_NODE* detection_filter;
    PatternMatchData* fp_content;  // 快速模式数据
    unsigned evalIndex;        // 评估顺序
};
```

### NC.5 Fast Pattern {#nc-5-fast-pattern}

**PatternMatchData** (pattern_match_data.h):
```cpp
struct PatternMatchData {
    const char* pattern_buf;
    unsigned pattern_size;
    int offset, depth;
    uint16_t flags;  // NEGATED, NO_CASE, FAST_PAT, NO_FP等
};
```

**Fast Pattern选择** (fp_utils.cc):
- 优先显式标记的 `fast_pattern`
- 优先非否定内容
- 优先更长模式

### NC.6 规则排序 {#nc-6-规则排序}

**规则分组**:
- 按端口分组到端口表
- Any-any规则放到 `*_any` 端口对象
- 双向规则添加到两个方向

### NC.7 关键配置 {#nc-7-关键配置}

```lua
fast_pattern = {
    inspect_stream_insert = true,
    split_any_any = false,
    max_queue_events = 5,
    bleedover_port_limit = 1024
}
```

---
