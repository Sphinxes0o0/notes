---
title: "Snort 3 · 协议检测与参考索引"
description: "附录MS：SIP检测模块详细分析 — 附录MJ：文档更新记录"
---

# Snort 3 · 协议检测与参考索引

[返回总目录](../snort3_architecture_analysis)

## 附录MS：SIP检测模块详细分析 {#附录ms-sip检测模块详细分析}

### MS.1 SipInspector类结构 {#ms-1-sipinspector类结构}

```cpp
class Sip : public Inspector {
    StreamSplitter* get_splitter(bool to_server)
        { return new SipSplitter(to_server); }
    bool is_control_channel() const { return true; }
};
```

**SipSplitter状态**:
```cpp
enum SshPafState {
    SIP_PAF_START_STATE,           // 继续直到LF
    SIP_PAF_CONTENT_LEN_CMD,       // 查找Content-Length头
    SIP_PAF_CONTENT_LEN_CONVERT,   // 解析字面长度
    SIP_PAF_BODY_SEARCH,          // 检查body开始
    SIP_PAF_FLUSH_STATE            // Content-Length到达时flush
};
```

### MS.2 SIP消息解析 {#ms-2-sip消息解析}

**支持的Method**:
INVITE, CANCEL, ACK, BYE, REGISTER, OPTIONS, REFER, SUBSCRIBE, UPDATE, JOIN, INFO, MESSAGE, NOTIFY, PRACK, PUBLISH, REPLACE

**Header字段**:
Via, From, To, Call-ID, CSeq, Contact, Authorization, Content-Type, Content-Length

### MS.3 对话跟踪 {#ms-3-对话跟踪}

**Dialog状态机**:
```cpp
SIP_DLG_CREATE = 1
SIP_DLG_INVITING = 2
SIP_DLG_EARLY = 3
SIP_DLG_AUTHENCATING = 4
SIP_DLG_ESTABLISHED = 5
SIP_DLG_REINVITING = 6
SIP_DLG_TERMINATING = 7
SIP_DLG_TERMINATED = 8
```

### MS.4 关键配置参数 {#ms-4-关键配置参数}

```lua
sip = {
    max_call_id_len = 256,
    max_contact_len = 256,
    max_content_len = 1024,
    max_dialogs = 4,
    max_from_len = 256,
    max_to_len = 256,
    max_uri_len = 256,
    max_via_len = 1024,
    methods = "invite cancel ack bye register options..."
}
```

---

## 附录MT：网络Inspector模块详细分析 {#附录mt-网络inspector模块详细分析}

### MT.1 ARP Spoof检测 {#mt-1-arp-spoof检测}

**类**: `ArpSpoof`

**检测事件(GID 112)**:
| Event | ID | 说明 |
|-------|-----|------|
| ARPSPOOF_UNICAST_ARP_REQUEST | 1 | 单播ARP请求 |
| ARPSPOOF_ETHERFRAME_ARP_MISMATCH_SRC | 2 | Ethernet/ARP源MAC不匹配 |
| ARPSPOOF_ETHERFRAME_ARP_MISMATCH_DST | 3 | Ethernet/ARP目标MAC不匹配 |
| ARPSPOOF_ARP_CACHE_OVERWRITE_ATTACK | 4 | ARP缓存覆盖攻击 |

**配置**:
```lua
arp_spoof = {
    hosts = {
        { ip = "10.10.10.10", mac = "29:a2:9a:29:a2:9a" }
    }
}
```

### MT.2 Normalizer模块 {#mt-2-normalizer模块}

**类**: `Normalizer`

**规范化功能**:
- IPv4: Trim frames, 清除DF/RF/TOS, 规范化TTL, 清除IP选项
- IPv6: 规范化hop limit, 清除选项
- ICMP4/ICMP6: 规范化echo request/reply codes
- TCP: ECN, reserved bits, urgent pointer, options, padding, trimming

**配置**:
```lua
normalizer = {
    ip4 = { base = true, df = true, ttl = true },
    tcp = { base = true, ecn = "packet", trim_syn = true },
    icmp4 = true,
    icmp6 = true
}
```

### MT.3 Packet Capture模块 {#mt-3-packet-capture模块}

**类**: `PacketCapture`

**功能**:
- 原始数据包转储(pcap格式)
- BPF过滤器支持
- 基于租户的过滤
- 内部数据包头检查

**配置**:
```lua
packet_capture = {
    enable = true,
    filter = "tcp",
    group = 0,
    capture_path = "/var/log/snort",
    max_packet_count = 10000
}
```

### MT.4 Perf Monitor模块 {#mt-4-perf-monitor模块}

**类**: `PerfMonitor`

**跟踪器类型**:
- BaseTracker: 基本性能指标
- CPUTracker: CPU使用率跟踪
- FlowTracker: Flow统计
- FlowIPTracker: 每IP flow跟踪

**配置**:
```lua
perf_monitor = {
    base = true,
    flow = true,
    flow_ip = true,
    cpu = true,
    format = "csv"
}
```

### MT.5 Reputation模块 {#mt-5-reputation模块}

**类**: `Reputation`

**功能**:
- IP信誉阻止/信任
- 支持blocklist和allowlist
- 嵌套IP检查(inner/outer/all)
- 内存映射文件处理

**配置**:
```lua
reputation = {
    blocklist = "blocklist.csv",
    allowlist = "allowlist.csv",
    memcap = 500,
    nested_ip = "inner",
    priority = "allowlist"
}
```

---

## 附录MU：分类阈值和检测系统 {#附录mu-分类阈值和检测系统}

### MU.1 事件阈值 (SFTHD) {#mu-1-事件阈值-sfthd}

**Threshold类型**:
| Type | Behavior |
|------|----------|
| THD_TYPE_LIMIT | 日志记录时间窗口内前N个事件 |
| THD_TYPE_THRESHOLD | N个事件后记录 |
| THD_TYPE_BOTH | 限制日志速率并要求阈值 |
| THD_TYPE_SUPPRESS | 从不记录(抑制) |
| THD_TYPE_DETECT | N次匹配后记录所有事件 |

### MU.2 Detection Filter {#mu-2-detection-filter}

**目的**: 规则级别的检测过滤器,控制在规则匹配时生成事件

**配置**:
```lua
detection_filter:
    gen_id 1, sig_id 2001,
    track by_src,
    count 100, seconds 60
```

### MU.3 Rate Filter {#mu-3-rate-filter}

**目的**: 基于速率的过滤,可临时更改规则动作

**Rate Filter状态**: FS_NEW, FS_OFF, FS_ON

**配置**:
```lua
rate_filter:
    gen_id 1, sig_id 2001,
    track by_src,
    count 100, seconds 60,
    timeout 10,
    new_action alert
```

### MU.4 检测流程 {#mu-4-检测流程}

```
数据包到达
     │
     ▼
DetectionEngine::inspect()
     │
     ▼
InspectorManager::execute()  -- Inspectors分析包
     │
     ▼
DetectionEngine::detect()
     │
     ▼
fp_full()  -- 快速模式匹配
     │
     ▼
fp_eval_rtn() -- 规则头检查
     │
     ▼
detection_option_tree_evaluate() -- 规则选项
     │
     ▼
fpLogEvent()
     │
     +---> RateFilter_Test() --> 可能更改动作
     │
     +---> sfthreshold_test() --> 过滤/抑制
     │
     ▼
DetectionEngine::log_events()
     │
     ▼
AlertLogger::log() -- 输出告警
```

---

## 附录MV：主线程和启动系统 {#附录mv-主线程和启动系统}

### MV.1 启动流程 {#mv-1-启动流程}

```
main()
   │
   ▼
Snort::setup()
   │
   ├── init_signals()
   ├── ThreadConfig::init()     -- hwloc/NUMA初始化
   ├── PluginManager::init()    -- 插件系统
   ├── DetectionEngine::init()  -- 检测引擎
   │
   ▼
parse_cmd_line()  -- 解析命令行
   │
   ▼
PluginManager::load_plugins()  -- 加载插件
   │
   ▼
ParseSnortConf()  -- 解析配置文件
   │
   ▼
InspectorManager::configure()  -- 配置inspectors
   │
   ▼
SFDAQ::init()  -- 初始化DAQ
```

### MV.2 Thread Configuration {#mv-2-thread-configuration}

**CpuSet**: hwloc拓扑CPU亲和性

**Watchdog监控**:
- 监控packet线程响应能力
- `watchdog_timer`秒无响应则中止
- `watchdog_min_thread_count`最小线程数

### MV.3 Signal处理 {#mv-3-signal处理}

```cpp
SIGHUP  -- reload-config
SIGUSR1 -- dump-stats
SIGUSR2 -- rotate-stats
SIGTERM -- 退出
SIGINT  -- 退出
```

### MV.4 SnortConfig关键成员 {#mv-4-snortconfig关键成员}

```cpp
struct SnortConfig {
    uint32_t run_flags;           // 运行模式标志
    SFDAQConfig* daq_config;     // DAQ配置
    PolicyMap* policy_map;       // 策略映射
    ThreadConfig* thread_config;  // 线程配置
    ProfilerConfig* profiler;    // 性能分析配置
    LatencyConfig* latency;      // 延迟配置
    MemoryConfig* memory;        // 内存配置
    uint32_t max_procs;         // 最大packet线程
};
```

### MV.5 Analyzer数据包处理循环 {#mv-5-analyzer数据包处理循环}

```cpp
void Analyzer::analyze()
{
    while (!exit_requested) {
        if (state != State::RUNNING) {
            handle_command();
            continue;
        }
        
        DAQ_RecvStatus rstat = process_messages();
        
        if (rstat == DAQ_RSTAT_TIMEOUT)
            idle();  // 空闲处理
    }
}
```

---

## 附录MW：alerter日志系统 {#附录mw-alerter日志系统}

### MW.1 日志格式 {#mw-1-日志格式}

| Module | 文件 | 格式 |
|--------|------|------|
| alert_fast | alert_fast.cc | 快速alert格式 |
| alert_full | alert_full.cc | 完整alert格式 |
| alert_csv | alert_csv.cc | CSV格式 |
| alert_json | alert_json.cc | JSON格式 |
| alert_syslog | alert_syslog.cc | Syslog输出 |
| unified2 | unified2.cc | Unified2二进制格式 |

### MW.2 Unified2事件结构 {#mw-2-unified2事件结构}

```cpp
struct Unified2Event {
    uint32_t type;           // 事件类型
    uint32_t length;        // 事件长度
    uint32_t sensor_id;
    uint32_t event_id;
    uint32_t event_second;
    uint32_t rule_gid;
    uint32_t rule_sid;
    uint32_t rule_rev;
    uint32_t rule_class;
    uint8_t priority;
    // ... IP/端口信息
};
```

### MW.3 PubSub事件系统 {#mw-3-pubsub事件系统}

**Detection事件**:
```cpp
IPS_LOGGING,       // IPS logger调用前
CONTEXT_LOGGING,   // 在IPS logger中
BUILTIN           // 内置事件加入事件队列
```

---

## 附录MX：Inspector框架 {#附录mx-inspector框架}

### MX.1 Inspector类型 {#mx-1-inspector类型}

```cpp
enum InspectorType {
    IT_PASSIVE,   // 仅配置,数据消费者
    IT_PACKET,    // 仅原始数据包
    IT_STREAM,    // Flow跟踪和重组
    IT_NETWORK,   // 无服务的 packets
    IT_SERVICE,   // Service PDU分析
    IT_CONTROL,   // 检测前处理
    IT_PROBE,     // 检测后处理
    IT_PROBE_FIRST
};
```

### MX.2 Module基类 {#mx-2-module基类}

```cpp
class Module {
    virtual bool begin(const char*, int, SnortConfig*);
    virtual bool end(const char*, int, SnortConfig*);
    virtual bool set(const char*, Value&, SnortConfig*);
    virtual const PegInfo* get_pegs() const;
    virtual const Command* get_commands() const;
};
```

### MX.3 Inspector类 {#mx-3-inspector类}

```cpp
class Inspector {
    virtual bool configure(SnortConfig*);
    virtual void tinit();              // 线程本地初始化
    virtual void tterm();              // 线程本地清理
    virtual bool likes(Packet*);       // 过滤数据包
    virtual void eval(Packet*);        // 处理数据包
    virtual bool get_buf(...);         // 缓冲区访问
    virtual StreamSplitter* get_splitter(bool);
};
```

---

## 附录MY：PUBSUB事件系统 {#附录my-pubsub事件系统}

### MY.1 DataBus {#my-1-databus}

```cpp
DataBus::publish(key, event);    // 发布事件
DataBus::subscribe(key, handler);  // 订阅事件
```

### MY.2 关键事件 {#my-2-关键事件}

| Event | 说明 |
|-------|------|
| IPS_LOGGING | IPS日志调用前 |
| DNS_PAYLOAD | DNS负载事件 |
| FILE_ID | 文件识别事件 |
| SSL_TLS_METADATA_EVENT | SSL/TLS元数据事件 |

---

## 附录MO：DCE/RPC检测模块详细分析 {#附录mo-dce-rpc检测模块详细分析}

### MO.1 主要inspector类 {#mo-1-主要inspector类}

| Inspector | 文件 | 用途 |
|-----------|------|------|
| `Dce2Tcp` | dce_tcp.cc | DCE/RPC over TCP |
| `Dce2SmbInspector` | dce_smb.cc | DCE/RPC over SMB (v1/v2) |
| `Dce2Udp` | dce_udp.cc | DCE/RPC over UDP |

### MO.2 DCE/RPC头部解析 {#mo-2-dce-rpc头部解析}

**连接导向头部** (dce_co.h):
```cpp
struct DceRpcCoHdr {
    DceRpcCoVersion pversion;     // 版本(5,0)
    uint8_t ptype;                // PDU类型
    uint8_t pfc_flags;           // FIRST_FRAG, LAST_FRAG
    uint8_t packed_drep[4];      // 数据表示(字节序)
    uint16_t frag_length;         // 片段长度
    uint16_t auth_length;        // 认证长度
    uint32_t call_id;           // 调用标识
};
```

**PDU类型**:
| 类型 | 名称 |
|------|------|
| 0 | REQUEST |
| 2 | RESPONSE |
| 11 | BIND |
| 12 | BIND_ACK |
| 14 | ALTER_CONTEXT |
| 15 | ALTER_CONTEXT_RESP |

### MO.3 SMB和TCP传输 {#mo-3-smb和tcp传输}

**SMB版本支持**:
- SMBv1: 44字节头部
- SMB2: `0xFE SMB` 头部, structure_size=64

**TCP PAF状态机**:
```cpp
enum DCE2_PafTcpStates {
    DCE2_PAF_TCP_STATES__0 = 0,  // Major version
    DCE2_PAF_TCP_STATES__1,      // Minor version
    DCE2_PAF_TCP_STATES__2,      // PDU type
    DCE2_PAF_TCP_STATES__3,      // Byte order
    // ...
    DCE2_PAF_TCP_STATES__9       // frag_length第二字节
};
```

### MO.4 接口和操作匹配 {#mo-4-接口和操作匹配}

**dce_iface规则选项**:
```lua
dce_iface:4b324fc8-1670-01d3-1278-5a47bf6ee188, version 1.0-2.0
```

**dce_opnum规则选项**:
```lua
dce_opnum:10-20  -- 操作号范围
```

### MO.5 关键配置参数 {#mo-5-关键配置参数}

```lua
dce2_smb = {
    policy = "Win2008",
    smb_max_chain = 3,
    smb_file_depth = 16384,
    memcap = 8388608
}
```

---

## 附录MP：SMTP检测模块详细分析 {#附录mp-smtp检测模块详细分析}

### MP.1 SmtpInspector类结构 {#mp-1-smtpinspector类结构}

```cpp
class Smtp : public Inspector {
    StreamSplitter* get_splitter(bool c2s)
        { return new SmtpSplitter(c2s, config->max_auth_command_line_len); }
    bool can_carve_files() const { return true; }
    bool can_start_tls() const { return true; }
};
```

**SMTP状态**:
```cpp
enum { STATE_CONNECT, STATE_COMMAND, STATE_DATA, STATE_BDATA,
       STATE_TLS_CLIENT_PEND, STATE_TLS_SERVER_PEND, STATE_TLS_DATA,
       STATE_AUTH, STATE_XEXCH50, STATE_UNKNOWN };
```

### MP.2 命令解析 {#mp-2-命令解析}

**命令搜索**: 使用MPSE进行高效命令匹配
```cpp
{ "AUTH", 4, CMD_AUTH, SMTP_CMD_TYPE_AUTH },
{ "DATA", 4, CMD_DATA, SMTP_CMD_TYPE_DATA },
{ "EHLO", 4, CMD_EHLO, SMTP_CMD_TYPE_NORMAL },
{ "STARTTLS", 8, CMD_STARTTLS, SMTP_CMD_TYPE_NORMAL },
```

### MP.3 MIME解析 {#mp-3-mime解析}

**MimeSession类**: 处理email解析
- 状态: `STATE_DATA_INIT`, `STATE_DATA_HEADER`, `STATE_DATA_BODY`, `STATE_MIME_HEADER`

**MIME边界检测**:
```cpp
enum MimeDataPafInfo {
    FINDING_BOUNDARY,  // 查找边界
    FOUND_FIRST,        // 找到第一个边界
    FOUND               // 完整边界找到
};
```

**解码类型**: Base64, Quoted-Printable, UUENCODE, Bit-encoded

### MP.4 关键配置参数 {#mp-4-关键配置参数}

```lua
smtp = {
    normalize = "none",           -- none, cmds, all
    max_command_line_len = 512,
    max_header_line_len = 1000,
    b64_decode_depth = -1,
    log_mailfrom = false,
    log_rcptto = false,
    xlink2state = "alert"         -- disable, alert, drop
}
```

---

## 附录MQ：FTP/Telnet检测模块详细分析 {#附录mq-ftp-telnet检测模块详细分析}

### MQ.1 主要inspector类 {#mq-1-主要inspector类}

| Inspector | 文件 | 用途 |
|-----------|------|------|
| `FtpClient` | ftp.cc | FTP客户端配置 |
| `FtpServer` | ftp.cc | FTP命令通道 |
| `Telnet` | telnet.cc | Telnet协议 |
| `FtpData` | ftp_data.cc | FTP数据通道 |

### MQ.2 FTP命令解析 {#mq-2-ftp命令解析}

**命令查找**: 使用KTrie数据结构
```cpp
typedef enum s_FTP_PARAM_TYPE {
    e_host_port,     // PORT命令 (h1,h2,h3,h4,p1,p2)
    e_long_host_port, // LPRT命令
    e_extd_host_port // EPRT/EPSV命令
} FTP_PARAM_TYPE;
```

### MQ.3 数据通道检测 {#mq-3-数据通道检测}

**数据通道状态机**:
```cpp
#define DATA_CHAN_PORT_CMD_ISSUED   0x01  // PORT/EPRT已发送
#define DATA_CHAN_PASV_CMD_ISSUED   0x04  // PASV/EPSV已发送
#define DATA_CHAN_XFER_CMD_ISSUED   0x10  // RETR/STOR已发送
```

### MQ.4 Telnet协商处理 {#mq-4-telnet协商处理}

**Telnet选项代码**:
```cpp
#define TNC_IAC  0xFF  // Interpret As Command
#define TNC_DO   0xFD
#define TNC_WILL 0xFB
#define TNC_SB   0xFA  // 子协商开始
#define TNC_SE   0xF0  // 子协商结束
```

### MQ.5 关键配置参数 {#mq-5-关键配置参数}

**FTP Server**:
```lua
ftp_server = {
    def_max_param_len = 100,
    data_chan = false,
    telnet_cmds = false,
    chk_str_fmt = {}
}
```

**FTP Client**:
```lua
ftp_client = {
    bounce = false,
    max_resp_len = -1,
    telnet_cmds = false
}
```

**Telnet**:
```lua
telnet = {
    ayt_attack_thresh = -1,
    normalize = false,
    check_encrypted = false
}
```

---

## 附录MR：SSH/POP/IMAP检测模块详细分析 {#附录mr-ssh-pop-imap检测模块详细分析}

### MR.1 SSH检测 {#mr-1-ssh检测}

**SshSplitter状态**:
```cpp
enum SshPafState {
    SSH_PAF_VER_EXCHANGE,   // Banner交换
    SSH_PAF_KEY_EXCHANGE,   // SSH2密钥交换
    SSH_PAF_ENCRYPTED       // 加密后
};
```

**SSH版本检测**:
- 最小Banner长度: 9字节
- 前缀: `"SSH-"`
- 支持: `1.x`, `2.0`, `1.99` (兼容性)

**加密流量处理**:
- 跟踪 `num_enc_pkts` 和 `num_client_bytes`
- 默认25个加密包后停止检测

**配置**:
```lua
ssh = {
    max_encrypted_packets = 25,
    max_client_bytes = 19600,
    max_server_version_len = 80
}
```

### MR.2 POP检测 {#mr-2-pop检测}

**PopSplitter**:
```cpp
enum PopExpectedResp {
    POP_PAF_SINGLE_LINE_STATE,   // +OK/-ERR
    POP_PAF_MULTI_LINE_STATE,   // 多行响应
    POP_PAF_DATA_STATE           // MIME数据
};
```

**命令到响应映射**:
| 命令 | 响应类型 |
|------|----------|
| CAPA, DELE, PASS, STAT | SINGLE_LINE |
| RETR, TOP | DATA_STATE |
| LIST | HAS_ARG |

### MR.3 IMAP检测 {#mr-3-imap检测}

**ImapSplitter**:
```cpp
enum ImapPafState {
    IMAP_PAF_REG_STATE,       // 默认
    IMAP_PAF_DATA_HEAD_STATE, // FETCH头部
    IMAP_PAF_DATA_LEN_STATE,  // 字面长度
    IMAP_PAF_DATA_STATE        // MIME数据
};
```

**MIME边界跟踪**:
- 解析 `{size}` 字面长度
- 跟踪括号嵌套

### MR.4 POP/IMAP MIME支持 {#mr-4-pop-imap-mime支持}

```lua
pop = {
    b64_decode_depth = -1,
    qp_decode_depth = -1,
    decompress_pdf = false
}

imap = {
    b64_decode_depth = -1,
    qp_decode_depth = -1,
    decompress_pdf = false
}
```

---

## 附录MI：附录索引 {#附录mi-附录索引}

### MI.1 主题索引 {#mi-1-主题索引}

| 主题 | 附录位置 |
|------|----------|
| Codec编解码器 | LX |
| TCP重组 | LY |
| 模式匹配算法 | LZ |
| Port Scan检测 | MA |
| 资源管理 | MB |
| HTTP检测 | ME |
| DNS检测 | MF |
| SSL/TLS检测 | MG |
| Binder/Wizard | MH |
| Stream TCP | MK |
| Flow管理 | ML |
| IpsAction/响应 | MM |
| DAQ接口 | MN |
| DCE/RPC | MO |
| SMTP | MP |
| FTP/Telnet | MQ |
| SSH/POP/IMAP | MR |
| SIP | MS |
| 网络Inspector(ARP/Normalizer) | MT |
| 分类阈值/检测系统 | MU |
| 主线程/启动系统 | MV |
| Alert日志系统 | MW |
| Inspector框架 | MX |
| PubSub事件系统 | MY |
| Stream UDP/ICMP/分片 | MZ |
| Packet数据结构 | NA |
| AppId应用识别 | NB |
| 规则解析系统 | NC |

### MI.2 源码文件索引 {#mi-2-源码文件索引}

| 功能 | 源文件 |
|------|--------|
| HTTP检测 | src/service_inspectors/http_inspect/*.cc |
| DNS检测 | src/network_inspectors/dns/*.cc |
| SSL/TLS检测 | src/service_inspectors/ssl/*.cc |
| Binder | src/network_inspectors/binder/*.cc |
| Wizard | src/service_inspectors/wizard/*.cc |
| Stream TCP | src/stream/tcp/*.cc |
| Flow管理 | src/flow/*.cc |
| IpsAction | src/actions/*.cc |
| DAQ | src/packet_io/*.cc, daqs/*.c |
| DCE/RPC | src/service_inspectors/dce_rpc/*.cc |
| SMTP | src/service_inspectors/smtp/*.cc |
| FTP/Telnet | src/service_inspectors/ftp_telnet/*.cc |
| SSH | src/service_inspectors/ssh/*.cc |
| POP/IMAP | src/service_inspectors/pop/*.cc, src/service_inspectors/imap/*.cc |
| SIP | src/service_inspectors/sip/*.cc |
| 网络Inspector | src/network_inspectors/arp_spoof/*.cc, normalize/*.cc, etc. |
| 检测系统 | src/detection/*.cc, src/filters/*.cc |
| 主程序 | src/main/*.cc |
| Alert日志 | src/loggers/*.cc |
| Stream UDP/ICMP | src/stream/udp/*.cc, src/stream/icmp/*.cc |
| IP分片 | src/stream/ip/*.cc |
| Packet结构 | src/protocols/packet.h |
| Codec框架 | src/framework/codec.h |
| AppId | src/network_inspectors/appid/*.cc |
| 规则解析 | src/parser/*.cc, src/detection/treenodes.h |

---

## 附录MJ：文档更新记录 {#附录mj-文档更新记录}

### MJ.1 更新历史 {#mj-1-更新历史}

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-04-10 | 22.0 | 初始版本 |
| 2026-04-11 | 23.0 | 新增Codec详细分析(LX) |
| 2026-04-11 | 23.0 | 新增TCP重组详细分析(LY) |
| 2026-04-11 | 23.0 | 新增模式匹配算法分析(LZ) |
| 2026-04-11 | 23.0 | 新增Port Scan检测分析(MA) |
| 2026-04-11 | 23.0 | 新增资源管理分析(MB) |
| 2026-04-11 | 24.0 | 新增HTTP检测分析(ME) |
| 2026-04-11 | 24.0 | 新增DNS检测分析(MF) |
| 2026-04-11 | 24.0 | 新增SSL/TLS检测分析(MG) |
| 2026-04-11 | 24.0 | 新增Binder/Wizard分析(MH) |
| 2026-04-11 | 25.0 | 新增Stream TCP分析(MK) |
| 2026-04-11 | 25.0 | 新增Flow管理分析(ML) |
| 2026-04-11 | 25.0 | 新增IpsAction/响应分析(MM) |
| 2026-04-11 | 25.0 | 新增DAQ接口分析(MN) |
| 2026-04-11 | 26.0 | 新增DCE/RPC分析(MO) |
| 2026-04-11 | 26.0 | 新增SMTP分析(MP) |
| 2026-04-11 | 26.0 | 新增FTP/Telnet分析(MQ) |
| 2026-04-11 | 26.0 | 新增SSH/POP/IMAP分析(MR) |
| 2026-04-11 | 27.0 | 新增SIP分析(MS) |
| 2026-04-11 | 27.0 | 新增网络Inspector分析(MT) |
| 2026-04-11 | 27.0 | 新增分类阈值/检测系统(MU) |
| 2026-04-11 | 27.0 | 新增主线程/启动系统(MV) |
| 2026-04-11 | 27.0 | 新增Alert日志系统(MW) |
| 2026-04-11 | 27.0 | 新增Inspector框架(MX) |
| 2026-04-11 | 27.0 | 新增PubSub事件系统(MY) |
| 2026-04-11 | 28.0 | 新增Stream UDP/ICMP/分片(MZ) |
| 2026-04-11 | 28.0 | 新增Packet数据结构(NA) |
| 2026-04-11 | 28.0 | 新增AppId应用识别(NB) |
| 2026-04-11 | 28.0 | 新增规则解析系统(NC) |

---

*文档完成 - Snort 3 源码架构分析文档*

