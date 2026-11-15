---
title: "Snort 3 · 附录 AA–AN"
description: "附录AA：Actions系统详解 — 附录AN：Port Scan检测器"
---

# Snort 3 · 附录 AA–AN

[返回总目录](../snort3_architecture_analysis)

## 附录AA：Actions系统详解 {#附录aa-actions系统详解}

### AA.1 IpsAction 基类 {#aa-1-ipsaction-基类}

```cpp
// framework/ips_action.h

class IpsAction {
public:
    enum IpsActionPriority {
        IAP_OTHER = 1,
        IAP_LOG = 10,
        IAP_ALERT = 20,
        IAP_REWRITE = 30,
        IAP_DROP = 40,
        IAP_BLOCK = 50,
        IAP_REJECT = 60,
        IAP_PASS = 70,
        IAP_MAX = IAP_PASS
    };
    
    virtual ~IpsAction() = default;
    
    // 执行动作
    virtual void exec(Packet*, const ActInfo&) = 0;
    
    // 是否丢弃流量
    virtual bool drops_traffic() { return false; }
    
    // 辅助方法
    void pass();
    void log(Packet*, const ActInfo&);
    void alert(Packet*, const ActInfo&);
    
protected:
    IpsAction(const char* s, ActiveAction* a) {
        name = s;
        active_action = a;
    }
    
    const char* name;
    ActiveAction* active_action;
};

// Action API
struct ActionApi {
    BaseApi base;
    IpsAction::IpsActionPriority priority;
    ActNewFunc ctor;
    ActDelFunc dtor;
};
```

### AA.2 ActionsModule {#aa-2-actionsmodule}

```cpp
// actions/actions_module.h

class ActionsModule : public snort::Module {
public:
    ActionsModule() : Module("ips_actions", "aggregate action counters") { }
    
    Usage get_usage() const override { return GLOBAL; }
    
    void add_action(std::string module_name, const PegInfo* pegs);
    PegCount* get_counts() const override;
    const PegInfo* get_pegs() const override;
    
    bool is_aggregator() const override { return true; }
};
```

### AA.3 ActiveAction 类 {#aa-3-activeaction-类}

```cpp
// packet_io/active_action.h

class ActiveAction {
public:
    enum Action {
        ACT_NONE,     // 无动作
        ACT_MODIFY,   // 修改
        ACT_DROP,     // 丢弃
        ACT_BLOCK,    // 阻止
        ACT_REPLACE,  // 替换
        ACT_ALERT,    // 告警
        ACT_LOG,      // 日志
        ACT_PASS,     // 通过
        ACT_MAX
    };
    
    // 获取动作
    Action get_action() const { return action; }
    
    // 是否需要阻止
    bool would_block() const;
    
    // 是否会丢弃
    bool would_drop() const;
    
    // 能否部分阻止会话
    bool can_partial_block_session() const;
    
    // 排队动作
    static void queue(ActiveAction*, Packet*);
};
```

### AA.4 规则动作优先级 {#aa-4-规则动作优先级}

```
┌─────────────────────────────────────────────────────┐
│              IpsAction 优先级                        │
├─────────────────────────────────────────────────────┤
│  IAP_PASS = 70        │  通过 (最高)               │
│  IAP_REJECT = 60      │  拒绝                      │
│  IAP_BLOCK = 50      │  阻止                      │
│  IAP_DROP = 40       │  丢弃                      │
│  IAP_REWRITE = 30    │  重写                      │
│  IAP_ALERT = 20      │  告警                      │
│  IAP_LOG = 10        │  日志                      │
│  IAP_OTHER = 1        │  其他 (最低)              │
└─────────────────────────────────────────────────────┘
```

---

## 附录AB：Latency延迟管理 {#附录ab-latency延迟管理}

### AB.1 PacketLatency {#ab-1-packetlatency}

```cpp
// latency/packet_latency.h

class PacketLatency {
public:
    // 推入延迟追踪
    static void push();
    
    // 弹出并检查延迟
    static void pop(const snort::Packet*);
    
    // 快速路径（跳过延迟检查）
    static bool fastpath();
    
    // 线程终止
    static void tterm();
    
    // RAII上下文
    class Context {
    public:
        Context(const snort::Packet* p) { PacketLatency::push(); }
        ~Context() { PacketLatency::pop(p); }
    };
};
```

### AB.2 RuleLatency {#ab-2-rulelatency}

```cpp
// latency/rule_latency.h

class RuleLatency {
public:
    // 检查规则延迟
    static bool check(const OptTreeNode* otn, Cursor& c, Packet* p);
    
    // 重置统计
    static void reset();
    
    // 获取统计
    static void get_stats(uint64_t& ticks, uint64_t& checks, uint64_t& matches);
};
```

### AB.3 延迟阈值配置 {#ab-3-延迟阈值配置}

```lua
-- snort.lua
(latency --
    packet_max_time = 500    -- 包处理最大时间（毫秒）
    rule_max_time = 1000    -- 单条规则最大时间（毫秒）
    packet_inject = true    -- 是否注入包
    rule_log = true         -- 是否记录规则延迟
)
```

---

## 附录AC：DNS检测器详解 {#附录ac-dns检测器详解}

### AC.1 DNS头部结构 {#ac-1-dns头部结构}

```cpp
// service_inspectors/dns/dns.h

struct DNSHdr {
    uint16_t id = 0;           // 事务ID
    uint16_t flags = 0;        // 标志
    uint16_t questions = 0;   // 问题数
    uint16_t answers = 0;      // 回答数
    uint16_t authorities = 0;  // 权威数
    uint16_t additionals = 0;  // 附加数
};

// DNS标志
#define DNS_HDR_FLAG_RESPONSE       0x8000  // 响应
#define DNS_HDR_FLAG_TRUNCATED    0x0200  // 截断
#define DNS_HDR_FLAG_RECURSION_DESIRED 0x0100  // 递归请求
#define DNS_HDR_FLAG_RECURSION_AVAIL 0x0080  // 递归可用
#define DNS_HDR_FLAG_AUTHORITATIVE 0x0400  // 权威回答
```

### AC.2 DNS资源记录类型 {#ac-2-dns资源记录类型}

```cpp
#define DNS_RR_TYPE_A        0x0001   // IPv4地址
#define DNS_RR_TYPE_NS      0x0002   // 域名服务器
#define DNS_RR_TYPE_CNAME   0x0005   // 别名
#define DNS_RR_TYPE_SOA     0x0006   // 授权开始
#define DNS_RR_TYPE_PTR     0x000C   // 指针记录
#define DNS_RR_TYPE_MX      0x000F   // 邮件交换
#define DNS_RR_TYPE_TXT     0x0010   // 文本记录
#define DNS_RR_TYPE_AAAA    0x001C   // IPv6地址
#define DNS_RR_TYPE_SRV     0x0023   // 服务定位
#define DNS_RR_TYPE_ANY     0x00FF   // 任意类型
```

### AC.3 DNS检测器流程 {#ac-3-dns检测器流程}

```cpp
class DnsInspector : public Inspector {
public:
    DnsInspector(DnsModule*);
    ~DnsInspector() override;
    
    void eval(Packet*) override;
    StreamSplitter* get_splitter(bool to_server) override;
    
    // DNS消息解析
    bool parse_dns_message(const uint8_t* data, unsigned len);
    
    // 验证DNS响应
    bool validate_response(const DNSHdr* hdr);
};
```

---

## 附录AD：SMTP检测器 {#附录ad-smtp检测器}

### AD.1 SMTP命令 {#ad-1-smtp命令}

```cpp
// service_inspectors/smtp/smtp_module.h

enum SMTPCommand {
    SMTP_COMMAND_NONE,
    SMTP_COMMANDHELO,   // 0x01
    SMTP_COMMAND_EHLO,
    SMTP_COMMAND_TLS,
    SMTP_COMMAND_AUTH,
    SMTP_COMMAND_USER,
    SMTP_COMMAND_PASS,
    SMTP_COMMAND_ACCT,
    SMTP_COMMAND_REST,
    SMTP_COMMAND_NOOP,
    SMTP_COMMAND_QUIT,
    SMTP_COMMAND_RSET,
    SMTP_COMMAND_DATA,
    SMTP_COMMAND_BDAT,
    SMTP_COMMAND_XEXCH50,
    SMTP_COMMAND_ETRN,
    SMTP_COMMAND_OTHERS,
    SMTP_COMMAND_MAX
};
```

### AD.2 SMTP标志 {#ad-2-smtp标志}

```cpp
#define SMTP_FLAG_NEXT_MODE               0x00000001
#define SMTP_FLAG_ABORT_MODE             0x00000002
#define SMTP_FLAGcommand_VALID           0x00000004
#define SMTP_FLAG_IN_DATA_MODE          0x00000008
#define SMTP_FLAG_PIPELINING            0x00000010
#define SMTP_FLAG_CHUNKING              0x00000020
#define SMTP_FLAG_AUTH_ENABLE           0x00000040
#define SMTP_COMMAND_XEXCH50_DATA_SIZE  0x00000080
#define SMTP_FLAG_MAILfrom_NEXT         0x00000100
#define SMTP_FLAG_RCPTto_NEXT          0x00000200
#define SMTP_FLAG_FOLDING               0x00000400
#define SMTP_FLAG_XAUTH                0x00000800
```

---

## 附录AE：FTP/Telnet检测器 {#附录ae-ftp-telnet检测器}

### AE.1 FTP命令 {#ae-1-ftp命令}

```cpp
// service_inspectors/ftp_telnet/ftp.h

enum FTPCommand {
    FTP_CMD_USER = 0,
    FTP_CMD_PASS,
    FTP_CMD_ACCT,
    FTP_CMD_CWD,
    FTP_CMD_CDUP,
    FTP_CMD_SMNT,
    FTP_CMD_QUIT,
    FTP_CMD_REIN,
    FTP_CMD_PORT,
    FTP_CMD_EPRT,
    FTP_CMD_PASV,
    FTP_CMD_EPSV,
    FTP_CMD_TYPE,
    FTP_CMD_STRU,
    FTP_CMD_MODE,
    FTP_CMD_RETR,
    FTP_CMD_STOR,
    FTP_CMD_STOU,
    FTP_CMD_APPE,
    FTP_CMD_ALLO,
    FTP_CMD_REST,
    FTP_CMD_RNFR,
    FTP_CMD_RNTO,
    FTP_CMD_ABOR,
    FTP_CMD_DELE,
    FTP_CMD_RMD,
    FTP_CMD_MKD,
    FTP_CMD_PWD,
    FTP_CMD_LIST,
    FTP_CMD_NLST,
    FTP_CMD_SITE,
    FTP_CMD_SYSTEM,
    FTP_CMD_NOOP,
    FTP_CMD_FEAT,
    FTP_CMD_OPTS,
    FTP_CMD_SIZE,
    FTP_CMD_STAT,
    FTP_CMD_HELP,
    FTP_CMD_MODE_Z,
    FTP_CMD_COMPRESS,
    FTP_CMD_XDEL,
    FTP_CMD_XMKD,
    FTP_CMD_XPWD,
    FTP_CMD_XRMD,
    FTP_CMD_XCWD,
    FTP_CMD_XMKD,
    FTP_CMD_MAX
};
```

### AE.2 FTP响应码 {#ae-2-ftp响应码}

```cpp
// FTP响应码分类
#define FTP_RESPONSE_1xx   0x0100  // 积极完成
#define FTP_RESPONSE_2xx   0x0200  // 成功
#define FTP_RESPONSE_3xx   0x0300  // 中间成功
#define FTP_RESPONSE_4xx   0x0400  // 临时失败
#define FTP_RESPONSE_5xx   0x0500  // 永久失败
```

---

## 附录AF：Active响应 {#附录af-active响应}

### AF.1 Active类 {#af-1-active类}

```cpp
// packet_io/active.h

class Active {
public:
    enum Action {
        ACT_NONE,
        ACT_DROP,       // 丢弃包
        ACT_BLOCK,      // 阻止连接
        ACT_RESET,      // 重置连接
        ACT_MODIFY,     // 修改包
        ACT_MAX
    };
    
    // 发送重置
    void send_reset(uint8_t direction, Packet* p);
    
    // 发送数据
    void send_data(uint8_t direction, Packet* p, const uint8_t* data, uint16_t len);
    
    // 丢弃数据包
    void drop_packet(Packet* p);
    
    // 取消激活
    void cancel(Packet* p);
    
    // 检查是否可以注入
    bool can_inject() const;
    
    // 是否是有效动作
    bool is_active() const;
};
```

### AF.2 Active::send_reset 实现 {#af-2-active-send-reset-实现}

```cpp
void Active::send_reset(uint8_t direction, Packet* p) {
    if (!can_inject())
        return;
        
    // 构建TCP RST包
    // 根据direction（客户端/服务器）设置源和目标
    
    // 注入RST包
    inject(verdict, raw_packet, len);
}
```

---

## 附录AG：文件处理详解 {#附录ag-文件处理详解}

### AG.1 FileIdentifier {#ag-1-fileidentifier}

```cpp
// file_api/file_identifier.h

class FileIdentifier {
public:
    // 从文件扩展名获取ID
    SnortFileId get_file_type_id(const char* extension);
    
    // 从MIME类型获取ID
    SnortFileId get_file_type_id_from_mime(const char* mime_type);
    
    // 从magic字节获取ID
    SnortFileId get_file_type_id_from_data(const uint8_t* data, uint32_t len);
};
```

### AG.2 FileCache {#ag-2-filecache}

```cpp
// file_api/file_cache.h

class FileCache {
public:
    // 查找文件
    File* find(const FileKey* key);
    
    // 添加文件
    void add(File* file);
    
    // 移除文件
    void remove(const FileKey* key);
    
    // 获取文件数量
    uint64_t get_file_count() const;
};
```

### AG.3 FileConfig {#ag-3-fileconfig}

```c

struct FileConfig {
    // 文件处理开关
    bool file_mask = true;       // 启用文件处理
    bool file_swf_depth = 0;   // SWF解压深度
    bool file_pdf_depth = 0;    // PDF解压深度
    bool file_identify = true; // 启用文件识别
    bool file_size_depth = 0;   // 文件大小限制
};
```

---

## 附录AH：Filter过滤器详解 {#附录ah-filter过滤器详解}

### AH.1 RateFilter {#ah-1-ratefilter}

```cpp
// filters/rate_filter.h

enum RateFilterMode {
    RATE_FILTER_DISABLE,   // 禁用
    RATE_FILTER_DROP,      // 丢弃
    RATE_FILTER_ALERT,     // 告警
    RATE_FILTER_LOG,       // 日志
    RATE_FILTER_MAX
};

struct RateFilterConfig {
    RateFilterMode mode;
    uint32_t count;        // 阈值
    uint32_t seconds;      // 时间窗口（秒）
    uint32_t timeout;      // 超时时间
    uint8_t track;         // 跟踪对象（by_src/by_dst）
};
```

### AH.2 DetectionFilter {#ah-2-detectionfilter}

```cpp
// filters/detection_filter.h

struct DetectionFilterConfig {
    uint32_t count;       // 检测计数
    uint32_t seconds;     // 时间窗口
    bool no_alert;        // 是否不告警
    TrackBy track;         // 跟踪对象
};
```

---

## 附录AI：Snort协议ID {#附录ai-snort协议id}

### AI.1 ProtocolId 枚举 {#ai-1-protocolid-枚举}

```cpp
// protocols/protocol_ids.h

enum ProtocolId : uint32_t {
    UNKNOWN_PROTOCOL_ID = 0,
    
    // IP协议
    IPPROTO_ICMP = 1,
    IPPROTO_TCP = 6,
    IPPROTO_UDP = 17,
    IPPROTO_IP = 252,
    
    // 应用协议
    PROTO_DNS = 300,
    PROTO_FTP = 301,
    PROTO_HTTP = 302,
    PROTO_SMTP = 303,
    PROTO_SSH = 304,
    PROTO_TLS = 305,
    PROTO_SMB = 306,
    PROTO_DCERPC = 307,
    PROTO_RPC = 308,
    PROTO_SIP = 309,
    PROTO_RTP = 310,
    PROTO_RTMP = 311,
    PROTO_HTTP2 = 312,
    PROTO_MQTT = 313,
    // ...
};
```

### AI.2 SnortProtocolId 用途 {#ai-2-snortprotocolid-用途}

SnortProtocolId 用于在Snort内部唯一标识协议，用于：
- 绑定检查器到流
- 注册协议缓冲区
- 快速模式匹配分组

---

## 附录AJ：主要源目录详解 {#附录aj-主要源目录详解}

### AJ.1 源码目录结构 {#aj-1-源码目录结构}

```
src/
├── main/                 # 主程序入口
│   ├── main.cc           # 主函数
│   ├── snort.cc/h        # Snort类
│   ├── snort_config.cc/h # 配置管理
│   ├── analyzer.cc/h     # 数据包分析器
│   ├── thread.cc/h       # 线程管理
│   └── ...
│
├── detection/            # 检测引擎核心
│   ├── detection_engine.cc/h  # 检测引擎
│   ├── fp_detect.cc/h    # 快速模式检测
│   ├── fp_create.cc/h    # 规则创建
│   ├── ips_context.cc/h  # 检测上下文
│   ├── treenodes.cc/h    # 规则树节点
│   └── ...
│
├── framework/           # 框架基类
│   ├── inspector.cc/h    # Inspector基类
│   ├── codec.cc/h       # Codec基类
│   ├── module.cc/h      # Module基类
│   ├── ips_option.cc/h  # IpsOption基类
│   └── ...
│
├── service_inspectors/   # 服务检查器
│   ├── http_inspect/     # HTTP检查器
│   ├── ssl/              # SSL/TLS检查器
│   ├── dns/              # DNS检查器
│   ├── smtp/             # SMTP检查器
│   ├── ftp_telnet/       # FTP/Telnet检查器
│   └── ...
│
├── network_inspectors/    # 网络检查器
│   ├── binder/           # 绑定器
│   ├── stream/          # 流处理
│   ├── normalize/       # 规范化
│   ├── port_scan/       # 端口扫描
│   └── ...
│
├── codecs/              # 协议编解码器
│   ├── ip/              # IP系列编解码器
│   ├── link/            # 链路层编解码器
│   └── ...
│
├── stream/              # 流重组核心
│   ├── tcp/             # TCP流处理
│   ├── udp.cc/h         # UDP流处理
│   ├── stream_splitter.cc/h  # 流分割器基类
│   └── ...
│
├── ips_options/         # IPS规则选项
│   ├── ips_content.cc/h # content选项
│   ├── ips_pcre.cc/h   # pcre选项
│   └── ...
│
├── pub_sub/            # 发布-订阅框架
│   ├── appid_events.cc/h
│   ├── http_events.cc/h
│   └── ...
│
├── loggers/            # 日志输出
│   ├── alert_fast.cc/h
│   ├── alert_sf.cc/h
│   └── ...
│
├── actions/            # 响应动作
│   ├── alert.cc
│   ├── drop.cc
│   ├── reject.cc
│   └── ...
│
├── filters/            # 过滤器
│   ├── rate_filter.cc/h
│   └── ...
│
├── file_api/          # 文件处理API
│   ├── file_cache.cc/h
│   ├── file_identifier.cc/h
│   └── ...
│
├── packet_io/         # 数据包IO
│   ├── sfdaq.cc/h     # DAQ接口
│   ├── active.cc/h    # 主动响应
│   └── ...
│
├── parser/            # 配置解析
│   ├── parse.cc/h
│   ├── parse_rule.cc/h
│   └── ...
│
├── managers/          # 管理器
│   ├── inspector_manager.cc/h
│   ├── module_manager.cc/h
│   ├── plugin_manager.cc/h
│   └── codec_manager.cc/h
│
├── helpers/           # 辅助工具
│   ├── ring.cc/h      # 环形缓冲区
│   └── ...
│
├── hash/              # 哈希表实现
│   ├── hash_main.cc/h
│   ├── hash_main.h
│   └── ...
│
├── protocols/         # 协议定义
│   ├── packet.h
│   ├── ip.h
│   ├── tcp.h
│   ├── udp.h
│   └── ...
│
├── time/              # 时间处理
│   ├── clock.cc/h
│   └── ...
│
├── trace/             # 追踪系统
│   ├── trace.cc/h
│   └── ...
│
├── profiler/          # 性能分析
│   ├── profiler.cc/h
│   └── ...
│
├── memory/           # 内存管理
│   └── memory_cap.cc/h
│
└── utils/            # 通用工具
    ├── util.cc/h
    └── ...
```

---

## 附录AK：常用配置示例 {#附录ak-常用配置示例}

### AK.1 基本snort.lua配置 {#ak-1-基本snort-lua配置}

```lua
-- 基本配置
snort = {
    { { pcap = "eth0" } },
    { -- Note: each { } is a packet processor instance
        {
            stats = { }
        }
    }
}

-- 日志
alert_fast = { file = true }

-- 网络配置
network = { }

-- 检查策略
inspection_policy = {
    {
        name = "balance",
        -- 绑定器配置
        binders = {
            { when = { proto = "tcp", ports = "80,443" }, use = { type = "http_inspect" } },
            { when = { proto = "tcp", ports = "25" }, use = { type = "smtp" } },
            { when = { proto = "dns" }, use = { type = "dns" } },
        }
    }
}

-- 网络策略
network_policy = {
    { id = 1, filters = "alert_fast" }
}

-- HTTP检查器
http_inspect = {
    request_depth = 6144,
    response_depth = 6144,
    normalize_cookies = true,
}

-- SSL检查器
ssl_inspect = {
    enable_mime = true,
    max_mime_depth = 8192,
}
```

### AK.2 规则示例 {#ak-2-规则示例}

```lua
-- 检测规则
local rules = [[
# 基础content匹配
alert tcp any any -> any any (msg:"TEST"; content:"test"; sid:1000001;)

# HTTP检测
alert http any any -> any any (msg:"SQL Injection"; content:"SELECT"; http_uri; sid:1000002;)

# 检测特定端口
alert tcp any any -> any 80 (msg:"Port 80"; sid:1000003;)

# 带fast_pattern
alert tcp any any -> any any (msg:"Malware"; content:"malware.exe"; fast_pattern; sid:1000004;)

# PCRE正则
alert tcp any any -> any any (msg:"Suspicious URL"; pcre:"/\/admin\/login\.php$/U"; sid:1000005;)

# 速率限制
alert tcp any any -> any any (msg:"DoS"; content:"flood"; rate_filter:track by_src, count 100, seconds 5; sid:1000006;)
]]

-- 加载规则
rules = { rules }
```

---

## 附录AL：调试和问题排查 {#附录al-调试和问题排查}

### AL.1 常用调试命令 {#al-1-常用调试命令}

```bash
# 查看帮助
snort --help

# 查看模块帮助
snort --help-module http_inspect

# 查看配置
snort -c snort.lua --dump-config

# 查看规则
snort -c snort.lua --dump-rules

# 跟踪调试
snort -c snort.lua -T -v --trace

# 抓包测试
snort -c snort.lua -r test.pcap -A console

# 性能测试
snort -c snort.lua -r test.pcap --perfmon-file perf.txt
```

### AL.2 常见问题 {#al-2-常见问题}

| 问题 | 原因 | 解决方法 |
|-----|------|---------|
| 规则不匹配 | fast_pattern未设置 | 添加`fast_pattern`选项 |
| 性能问题 | 规则过多 | 使用分类规则 |
| 内存占用高 | FlowCache过大 | 调整`flow_cache_size` |
| 丢包 | 线程不足 | 增加packet_threads |
| 配置错误 | Lua语法错误 | 使用`snort -T`验证 |

---

## 附录AM：术语表 {#附录am-术语表}

| 术语 | 含义 |
|-----|------|
| Inspector | 检查器，Snort3核心处理组件 |
| Codec | 协议编解码器 |
| MPSE | 多模式搜索引擎 |
| OTN | 规则树节点 (OptTreeNode) |
| RTN | 规则类型节点 (RuleTreeNode) |
| Binder | 将检查器绑定到流的组件 |
| Wizard | 自动服务检测组件 |
| PAF | 协议感知Flush |
| DAQ | 数据获取接口 |
| FlowKey | 流5元组键 |
| IpsContext | 检测上下文 |

---

## 附录AN：Port Scan检测器 {#附录an-port-scan检测器}

### AN.1 PortScan配置 {#an-1-portscan配置}

```cpp
// network_inspectors/port_scan/port_scan.h

class PortScanModule : public snort::Module {
public:
    // 扫描类型
    enum class ScanType {
        NONE,
        TCP_SYN,
        TCP_ACK,
        TCP_SYN_ACK,
        TCP_FIN,
        TCP_NULL,
        TCP_XMAS,
        UDP,
        ICMP,
        OPEN_PORT,
        ALL
    };
    
    // 配置参数
    struct PortScanConfig {
        uint32_t proto;           // 协议
        uint32_t scan_type;     // 扫描类型
        uint32_t sense_level;   // 检测级别
        uint32_t watch_ip;      // 监视IP
        uint32_t ignore_ip;     // 忽略IP
    };
};
```

### AN.2 扫描检测逻辑 {#an-2-扫描检测逻辑}

```cpp
class PortScan : public Inspector {
public:
    void eval(Packet*) override;
    
    // 记录扫描
    void log_scan(const Packet*);
    
    // 检查是否应忽略
    bool should_ignore(const sfip_var_t*);
};
```

---
