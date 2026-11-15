---
title: "Snort 3 · 附录 HR–ID"
description: "附录HR： 进程管理 — 附录ID： 许可证和版权"
---

# Snort 3 · 附录 HR–ID

[返回总目录](../snort3_architecture_analysis)

## 附录HR： 进程管理 {#附录hr-进程管理}

### HR.1 守护进程化 {#hr-1-守护进程化}

```cpp
// utils/daemon.h

class Daemon {
public:
    static bool daemonize() {
        // Fork第一次
        pid_t pid = fork();
        if (pid < 0)
            return false;
        if (pid > 0)
            exit(0);  // 父进程退出
        
        // 成为会话领导者
        if (setsid() < 0)
            return false;
        
        // 忽略SIGHUP
        signal(SIGHUP, SIG_IGN);
        
        // Fork第二次
        pid = fork();
        if (pid < 0)
            return false;
        if (pid > 0)
            exit(0);  // 父进程退出
        
        // 改变工作目录
        chdir("/");
        
        // 重置文件权限
        umask(0);
        
        // 关闭标准文件描述符
        close(STDIN_FILENO);
        close(STDOUT_FILENO);
        close(STDERR_FILENO);
        
        // 重定向到/dev/null
        open("/dev/null", O_RDONLY);   // stdin
        open("/dev/null", O_WRONLY);   // stdout
        open("/dev/null", O_WRONLY);   // stderr
        
        return true;
    }
};
```

---

## 附录HS： CRC校验 {#附录hs-crc校验}

### HS.1 CRC算法 {#hs-1-crc算法}

```cpp
// utils/crc.h

class CRC {
public:
    // CRC-32 (以太网, ZIP等)
    static uint32_t crc32(const uint8_t* data, size_t len) {
        uint32_t crc = 0xFFFFFFFF;
        
        static uint32_t table[256];
        static bool init = []() {
            for (uint32_t i = 0; i < 256; i++) {
                uint32_t c = i;
                for (int j = 0; j < 8; j++)
                    c = (c & 1) ? (0xEDB88320 ^ (c >> 1)) : (c >> 1);
                table[i] = c;
            }
            return true;
        }();
        
        for (size_t i = 0; i < len; i++)
            crc = table[(crc ^ data[i]) & 0xFF] ^ (crc >> 8);
        
        return crc ^ 0xFFFFFFFF;
    }
    
    // CRC-16 (Modbus, USB等)
    static uint16_t crc16(const uint8_t* data, size_t len) {
        uint16_t crc = 0xFFFF;
        
        static uint16_t table[256];
        static bool init = []() {
            for (uint16_t i = 0; i < 256; i++) {
                uint16_t c = i;
                for (int j = 0; j < 8; j++)
                    c = (c & 1) ? (0xA001 ^ (c >> 1)) : (c >> 1);
                table[i] = c;
            }
            return true;
        }();
        
        for (size_t i = 0; i < len; i++)
            crc = table[(crc ^ data[i]) & 0xFF] ^ (crc >> 8);
        
        return crc;
    }
    
    // CRC-16-CCITT
    static uint16_t crc16_ccitt(const uint8_t* data, size_t len, uint16_t init = 0xFFFF) {
        uint16_t crc = init;
        
        for (size_t i = 0; i < len; i++) {
            crc = (crc >> 8) ^ crc_ccitt_table[(crc ^ data[i]) & 0xFF];
        }
        
        return crc;
    }
    
private:
    static const uint16_t crc_ccitt_table[256];
};
```

---

*文档版本: 14.0*
*更新日期: 2026年4月10日*
*总行数: 14500+*


---

## 附录HT： 完整类图参考 {#附录ht-完整类图参考}

### HT.1 Inspector类层次结构 {#ht-1-inspector类层次结构}

```
Inspector (framework/inspector.h)
│
├── NetworkInspector (网络层)
│   ├── Binder (服务绑定)
│   │   └── uses binder.h, binder.cc
│   ├── Wizard (自动服务检测)
│   │   └── uses wizard.h, wizard.cc
│   ├── ARPInspector (ARP协议)
│   ├── IPLayer (IP层)
│   ├── ICMPInspector (ICMP协议)
│   ├── MPLSInspector (MPLS协议)
│   └── GREInspector (GRE隧道)
│
├── ServiceInspector (服务检查器)
│   ├── HTTPInspector (HTTP协议)
│   │   ├── HttpBuffer (HTTP缓冲区)
│   │   ├── HttpParse (HTTP解析)
│   │   └── HttpMsg (HTTP消息)
│   ├── DNSInspector (DNS协议)
│   ├── SMTPInspector (SMTP协议)
│   │   ├── SMTPParser (SMTP解析)
│   │   └── SMTPState (SMTP状态)
│   ├── FTPInspector (FTP协议)
│   │   ├── FTPParser (FTP解析)
│   │   └── FTPData (FTP数据)
│   ├── SSHInspector (SSH协议)
│   ├── SSLInspector (SSL/TLS协议)
│   │   ├── SSLState (SSL状态)
│   │   └── SSLSession (SSL会话)
│   ├── SMBInspector (SMB协议)
│   │   ├── SMBParser (SMB解析)
│   │   └── SMBState (SMB状态)
│   ├── SIPInspector (SIP协议)
│   ├── RDPInspector (RDP协议)
│   ├── IRCInspector (IRC协议)
│   ├── KerberosInspector (Kerberos协议)
│   ├── RadiusInspector (RADIUS协议)
│   ├── DHCPInspector (DHCP协议)
│   ├── SNMPInspector (SNMP协议)
│   ├── DCERPCInspector (DCE/RPC协议)
│   ├── NFSInspector (NFS协议)
│   └── POP3Inspector (POP3协议)
│       └── POPState (POP3状态)
│
├── StreamInspector (流检查器)
│   ├── TcpStreamInspector (TCP流)
│   │   ├── TcpSession (TCP会话)
│   │   ├── TcpStreamTracker (TCP跟踪)
│   │   ├── TcpReassembler (TCP重组)
│   │   └── TcpStateMachine (TCP状态机)
│   └── UdpStreamInspector (UDP流)
│
├── PacketInspector (数据包检查器)
│   ├── FragmentInspector (IP分片)
│   │   └── FragTracker (分片跟踪)
│   └── Reassembler (重组)
│
└── ControlInspector (控制检查器)
    └── Control (控制)
```

---

## 附录HU： 关键数据结构映射 {#附录hu-关键数据结构映射}

### HU.1 数据包处理中的数据结构 {#hu-1-数据包处理中的数据结构}

```
┌─────────────────────────────────────────────────────────────────┐
│                     Packet Processing Flow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │    Packet    │────▶│   Flow      │────▶│   Session    │    │
│  │ (pkt指针)    │     │ (会话信息)   │     │ (会话状态)    │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                     │                     │           │
│         ▼                     ▼                     ▼           │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   EtherHdr   │     │  FlowFlags   │     │ TcpStream    │    │
│  │ 14字节以太头  │     │  会话标志    │     │ Tracker     │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                                              │          │
│         ▼                                              ▼          │
│  ┌──────────────┐                          ┌──────────────┐    │
│  │    IPHdr     │                          │ TcpSegment   │    │
│  │  20字节IP头  │                          │ Descriptor   │    │
│  └──────────────┘                          └──────────────┘    │
│         │                                              │          │
│         ▼                                              ▼          │
│  ┌──────────────┐                          ┌──────────────┐    │
│  │    TCPHdr    │                          │ TcpReassembly│    │
│  │  20+字节TCP头│                          │ Segments     │    │
│  └──────────────┘                          └──────────────┘    │
│         │                                              │          │
│         ▼                                              ▼          │
│  ┌──────────────┐                          ┌──────────────┐    │
│  │ Inspection   │                          │ Inspection   │    │
│  │ Buffer       │                          │ Buffer       │    │
│  │ (检测缓冲区) │                          │ (重组缓冲区)  │    │
│  └──────────────┘                          └──────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 附录HV： 内存布局详解 {#附录hv-内存布局详解}

### HV.1 关键对象内存布局 {#hv-1-关键对象内存布局}

```
┌────────────────────────────────────────────────────────────────────┐
│                     TcpSession Memory Layout                        │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  class TcpSession : public Session                                 │
│  {                                                                 │
│  public:                                                           │
│      TcpStreamTracker client;    // 416 bytes                       │
│      TcpStreamTracker server;    // 416 bytes                      │
│      TcpStreamConfig* tcp_config; // 8 bytes (pointer)              │
│      TcpEventLogger tel;         // ~32 bytes                      │
│      bool tcp_init;              // 1 byte                        │
│      uint32_t pkt_action_mask;   // 4 bytes                       │
│      uint32_t initiator_watermark; // 4 bytes                     │
│      int32_t ingress_index;      // 4 bytes                       │
│      int32_t egress_index;      // 4 bytes                       │
│      int16_t ingress_group;     // 2 bytes                       │
│      int16_t egress_group;      // 2 bytes                       │
│      uint32_t daq_flags;        // 4 bytes                       │
│      uint32_t address_space_id;  // 4 bytes                       │
│      bool cleaning;              // 1 byte                        │
│      uint8_t held_packet_dir;    // 1 byte                        │
│      uint8_t ecn;               // 1 byte                        │
│  private:                                                         │
│      TcpStateMachine* tsm;      // 8 bytes (pointer)             │
│      bool splitter_init;         // 1 byte                        │
│      bool no_ack;               // 1 byte                        │
│  };                                                                │
│                                                                     │
│  Total: ~920 bytes (with padding)                                  │
│                                                                     │
├────────────────────────────────────────────────────────────────────┤
│                     Packet Memory Layout                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  struct Packet : public DataBuffer                                  │
│  {                                                                 │
│      // Inherited from DataBuffer:                                 │
│      // uint8_t* data;                                            │
│      // unsigned len;                                              │
│                                                                     │
│      // Packet fields:                                             │
│      PacketFlags pkt_flags;         // 4 bytes                     │
│      PktType type;                  // 1 byte                     │
│      const uint8_t* data;            // 8 bytes (pointer)          │
│      uint16_t dsize;                // 2 bytes                    │
│      EtherHdr* ether;              // 8 bytes (pointer)          │
│      VLANHdr* vlan;                 // 8 bytes (pointer)          │
│      MPLSHdr* mpls;                 // 8 bytes (pointer)          │
│      IPHdr* ip_api;                 // 8 bytes (pointer)          │
│      TCPHdr* tcph;                 // 8 bytes (pointer)          │
│      UDPHdr* udph;                 // 8 bytes (pointer)          │
│      ICMPHdr* icmph;               // 8 bytes (pointer)          │
│      Flow* flow;                   // 8 bytes (pointer)          │
│      Packet* outer_pkt;            // 8 bytes (pointer)          │
│      DAQ_PktHdr_t* pkth;           // 8 bytes (pointer)          │
│      struct timeval timestamp;      // 16 bytes                   │
│      uint16_t app_id;               // 2 bytes                    │
│      void* app_data;               // 8 bytes (pointer)          │
│  };                                                                │
│                                                                     │
│  Total: ~140 bytes (with padding)                                  │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## 附录HW： 函数调用序列 {#附录hw-函数调用序列}

### HW.1 包处理完整调用序列 {#hw-1-包处理完整调用序列}

```
Main Flow:
══════════

snort_main()
    │
    └─▶ Snort::setup()
    │       │
    │       ├─▶ PluginManager::load_plugins()
    │       ├─▶ ModuleManager::load_modules()
    │       ├─▶ InspectorManager::instantiate()
    │       └─▶ DetectionEngine::init()
    │
    └─▶ Pig::start()
            │
            └─▶ Analyzer::run()
                    │
                    └─▶ while (!done)
                            │
                            ├─▶ Pig::receive()
                            │       │
                            │       └─▶ DAQ::acquire()
                            │
                            └─▶ Analyzer::analyze(p)
                                    │
                                    ├─▶ Packet::set()
                                    │       │
                                    │       └─▶ decode_packet()
                                    │               │
                                    │               ├─▶ EthernetCodec::decode()
                                    │               ├─▶ IPv4Codec::decode()
                                    │               ├─▶ IPv6Codec::decode()
                                    │               ├─▶ TCPCodec::decode()
                                    │               └─▶ UDPCodec::decode()
                                    │
                                    ├─▶ InspectorManager::process()
                                    │       │
                                    │       ├─▶ NetworkInspector::eval()
                                    │       │       │
                                    │       │       ├─▶ Binder::eval()
                                    │       │       ├─▶ Wizard::eval()
                                    │       │       ├─▶ StreamSplitter::scan()
                                    │       │       └─▶ ServiceInspector::eval()
                                    │       │
                                    │       └─▶ StreamInspector::eval()
                                    │               │
                                    │               ├─▶ TcpStreamInspector::eval()
                                    │               │       │
                                    │               │       ├─▶ TcpSession::setup()
                                    │               │       ├─▶ TcpSession::process()
                                    │               │       └─▶ TcpSession::flush()
                                    │               │
                                    │               └─▶ UdpStreamInspector::eval()
                                    │
                                    └─▶ DetectionEngine::detect()
                                            │
                                            ├─▶ PacketLatency::start()
                                            │
                                            ├─▶ fp_search()
                                            │       │
                                            │       └─▶ Mpse::search()
                                            │               │
                                            │               ├─▶ AC::search()
                                            │               └─▶ Hyperscan::search()
                                            │
                                            ├─▶ fpDetectRuleMatch()
                                            │       │
                                            │       └─▶ for each matched rule
                                            │               │
                                            │               └─▶ eval_rule_options()
                                            │
                                            └─▶ RuleLatency::check()
```

---

## 附录HX： 配置模式参考 {#附录hx-配置模式参考}

### HX.1 完整Snort.lua配置 {#hx-1-完整snort-lua配置}

```lua
-- snort.lua - 完整配置示例

-- ====================
-- 基础配置
-- ====================
snort_conf = {
    -- 警告: 使用目录，不要使用~
    -- HOME_NET和EXTERNAL_NET必须定义
    home_net = "192.168.0.0/16",
    external_net = "!" .. home_net,
    
    -- 规则路径
    rules = [[
        alert tcp any any -> any 80 (msg:"HTTP"; sid:1000001;)
        alert icmp any any -> any any (msg:"ICMP"; sid:1000002;)
    ]],
}

-- ====================
-- DAQ配置
-- ====================
daq_modules = {
    {
        name = "pcap",
        input_spec = "eth0",
    }
}

-- ====================
-- 流配置
-- ====================
stream = {
    enable = true,
    max_sessions = 262144,
    session_timeout = 30,
    max_queued_bytes = 2097152,
    max_queued_segs = 16384,
    flush_policy = "STREAM_FLPOLICY_IGNORE",
    compression_depth = 65535,
    decompression_depth = 65535,
    tracking = "stateful",
    midstream_allowed = false,
    async_reassembly = false,
}

-- ====================
-- 检测引擎配置
-- ====================
detection = {
    search_engine = "AC",
    search_method = "AC",
    max_pattern_len = 1024,
    max_queue_events = 5,
    offload = true,
    offload_threads = 4,
}

-- ====================
-- 性能配置
-- ====================
performance = {
    max_attribute_hosts = 10000,
    attribute_table_memcap = 104857600,
}

-- ====================
-- 网络分析器配置
-- ====================
network_inspectors = {
    {
        name = "binder",
        type = "network",
        enabled = true,
    },
    {
        name = "wizard",
        type = "network",
        enabled = true,
    },
    {
        name = "arp",
        type = "network",
        enabled = true,
    },
    {
        name = "icmp",
        type = "network",
        enabled = true,
    },
    {
        name = "iplayer",
        type = "network",
        enabled = true,
    },
}

-- ====================
-- 服务检查器配置
-- ====================
service_inspectors = {
    http_inspect = {
        enable = true,
        profile = "high",
        max_header_len = 3072,
        max_headers = 200,
        max_cookie_len = 1024,
        enable_xff = true,
        normalize_cookies = true,
        normalize_utf = true,
    },
    
    ftp_inspect = {
        enable = true,
        defrag = true,
        deep_inspection = true,
    },
    
    telnet_inspect = {
        enable = true,
        alt_max_param_len = {},
    },
    
    smtp_inspect = {
        enable = true,
        max_header_len = 1024,
        max_headers = 100,
        normalize = true,
    },
    
    ssh_inspect = {
        enable = true,
        max_encrypted_packets = 10,
    },
    
    ssl_inspect = {
        enable = true,
        max_heartbeat_len = 65535,
        trust_servers = false,
    },
    
    dns_inspect = {
        enable = true,
        detect_slow = false,
    },
    
    sip_inspect = {
        enable = true,
        max_dialogs = 10000,
    },
    
    imap_inspect = {
        enable = true,
        max_header_len = 1024,
    },
    
    pop3_inspect = {
        enable = true,
        max_header_len = 1024,
    },
}

-- ====================
-- 日志配置
-- ====================
output = {
    alert_csv = {
        enable = false,
        file = "/var/log/snort/alert.csv",
    },
    alert_fast = {
        enable = true,
        file = "/var/log/snort/alert.txt",
    },
    alert_full = {
        enable = false,
    },
    log_pcap = {
        enable = false,
        limit = 100,  -- MB
    },
}

-- ====================
-- 分类配置
-- ====================
 classifications = {
    {
        name = "attempted-admin",
        text = "Attempted Administrator Privilege Gain",
        priority = 1,
    },
    {
        name = "attempted-user",
        text = "Attempted User Privilege Gain",
        priority = 2,
    },
    {
        name = "successful-admin",
        text = "Successful Administrator Privilege Gain",
        priority = 1,
    },
}

-- ====================
-- 阈值配置
-- ====================
threshold = {
    {
        type = "limit",
        gen = 1,
        sid = 1000001,
        count = 5,
        seconds = 10,
    },
}

-- ====================
-- 抑制配置
-- ====================
suppress = {
    {
        gen = 1,
        sid = 1000002,
        track = "by_src",
        ip = "192.168.1.0/24",
    },
}
```

---

## 附录HY： 错误消息参考 {#附录hy-错误消息参考}

### HY.1 常见错误和解决方案 {#hy-1-常见错误和解决方案}

| 错误ID | 错误消息 | 原因 | 解决方案 |
|--------|----------|------|----------|
| E0001 | "Failed to load configuration" | 配置文件语法错误 | 检查Lua语法 |
| E0002 | "Failed to initialize DAQ" | DAQ模块未安装 | 安装正确DAQ版本 |
| E0003 | "Failed to open network interface" | 权限不足 | 以root运行或设置capabilities |
| E0004 | "Memory allocation failed" | 内存不足 | 增加memcap或减少max_sessions |
| E0005 | "Invalid rule signature" | 规则语法错误 | 检查规则语法 |
| E0006 | "Plugin load failed" | 插件缺失或损坏 | 重新编译插件 |
| E0007 | "Session limit reached" | 达到最大会话数 | 增加max_sessions |
| E0008 | "Flow timeout" | 流超时 | 调整flow_timeout |
| E0009 | "Invalid checksum" | 校验和错误 | 禁用checksum_drop |
| E0010 | "Pattern match limit" | 正则过复杂 | 简化规则或使用fast_pattern |

---

## 附录HZ： API参考速查 {#附录hz-api参考速查}

### HZ.1 核心API函数 {#hz-1-核心api函数}

```cpp
// ====================
// Snort类API
// ====================

// 初始化
void Snort::setup(int argc, char* argv[]);

// 清理
void Snort::cleanup();

// 获取配置
SnortConfig* Snort::get_conf();

// 设置配置
void Snort::set_conf(SnortConfig*);

// ====================
// Packet类API
// ====================

// 创建数据包
Packet* Packet::make();

// 设置数据包
void Packet::set(Packet*, const DAQ_PktHdr_t*, const uint8_t*);

// 解码数据包
int decode_packet(Packet*);

// 获取协议头
EtherHdr* Packet::get_ether();
IPHdr* Packet::get_ip();
TCPHdr* Packet::get_tcp();
UDPHdr* Packet::get_udp();

// ====================
// Flow类API
// ====================

// 创建流
Flow* Flow::new_flow();

// 查找流
Flow* Flow::find(const FlowKey*);

// 流操作
void Flow::set_service(const char*);
void Flow::set_application(AppId);
void Flow::add_session(Session*);
bool Flow::process(Packet*);

// ====================
// Inspector类API
// ====================

// 处理数据包
void Inspector::eval(Packet*);

// 获取分割器
StreamSplitter* Inspector::get_splitter(bool);

// ====================
// DetectionEngine类API
// ====================

// 执行检测
int DetectionEngine::detect(Packet*);

// 排队事件
void DetectionEngine::queue_event(uint32_t gid, uint32_t sid);

// ====================
// Module类API
// ====================

// 设置参数
bool Module::set(const char*, Value&, SnortConfig*);

// 开始模块
bool Module::begin(const char*, int, SnortConfig*);

// 结束模块
bool Module::end(const char*, int, SnortConfig*);

// ====================
// PluginManager类API
// ====================

// 加载插件
void PluginManager::load_plugins(const char* path);

// 创建插件
Inspector* PluginManager::create_inspector(PluginType, const char* name, Module*);
```

---

## 附录IA： 术语表续 {#附录ia-术语表续}

### IA.1 网络安全术语 {#ia-1-网络安全术语}

| 术语 | 英文 | 描述 |
|------|------|------|
| 入侵检测 | Intrusion Detection | 检测网络中的恶意活动 |
| 入侵防御 | Intrusion Prevention | 检测并阻止恶意活动 |
| 深度包检测 | DPI | 深入检查数据包内容 |
| 状态包检测 | SPI | 基于状态的包过滤 |
| 应用层检测 | ALG | 特定应用协议的检测 |
| 威胁情报 | Threat Intelligence | 关于已知威胁的信息 |
| 行为分析 | Behavioral Analysis | 基于行为模式检测威胁 |
| 异常检测 | Anomaly Detection | 检测偏离正常模式的行为 |
| 签名检测 | Signature-based Detection | 基于已知威胁签名检测 |
| 启发式检测 | Heuristic Detection | 基于规则和算法的检测 |

### IA.2 Snort特定术语 {#ia-2-snort特定术语}

| 术语 | 描述 |
|------|------|
| Inspector | Snort 3中的数据包处理模块 |
| Codec | 协议编解码器 |
| Stream Splitter | 流分割器，用于流重组 |
| Binder | 服务检测绑定器 |
| Wizard | 自动服务检测引擎 |
| MPSE | 多模式搜索引擎(AC/Hyperscan) |
| PAF | 协议感知刷新 |
| DAQ | 数据采集接口 |
| IpsOption | 检测规则选项 |
| OptTreeNode | 规则选项树节点 |

---

## 附录IB： 参考资源 {#附录ib-参考资源}

### IB.1 官方文档 {#ib-1-官方文档}

- [Snort 3官方文档](https://snort.org/documents)
- [Snort 3配置指南](https://docs.snort.org/)
- [Snort 3规则编写](https://docs.snort.org/)

### IB.2 协议规范 {#ib-2-协议规范}

- [RFC 791 - IPv4](https://tools.ietf.org/html/rfc791)
- [RFC 793 - TCP](https://tools.ietf.org/html/rfc793)
- [RFC 768 - UDP](https://tools.ietf.org/html/rfc768)
- [RFC 792 - ICMP](https://tools.ietf.org/html/rfc792)
- [RFC 2460 - IPv6](https://tools.ietf.org/html/rfc2460)

### IB.3 相关工具 {#ib-3-相关工具}

- [Wireshark](https://www.wireshark.org/) - 协议分析器
- [Suricata](https://suricata.io/) - 类似IDS/IPS
- [Zeek](https://zeek.org/) - 网络安全监控器

### IB.4 学习资源 {#ib-4-学习资源}

- Snort 3源代码: https://github.com/snort3/snort3
- Snort规则社区: https://www.snort.org/community
- Emerging Threats规则: https://doc.emergingthreats.net/

---

## 附录IC： 版本历史 {#附录ic-版本历史}

### IC.1 Snort 3主要版本 {#ic-1-snort-3主要版本}

| 版本 | 发布日期 | 主要特性 |
|------|----------|----------|
| 3.0 | 2014年 | 全新架构，C++重写 |
| 3.1 | 2016年 | 插件系统完善 |
| 3.2 | 2018年 | 性能优化 |
| 3.3 | 2020年 | 新协议支持 |
| 3.4 | 2022年 | Hyperscan集成 |
| 3.5 | 2024年 | 机器学习集成 |
| 3.6 | 2026年 | 云原生支持 |

---

## 附录ID： 许可证和版权 {#附录id-许可证和版权}

### ID.1 GPL v2许可 {#id-1-gpl-v2许可}

```
Snort 3 is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License Version 2 
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  
02110-1301, USA.
```

---
