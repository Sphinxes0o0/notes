---
title: "Snort 3 · 附录 C–L"
description: "附录C：事件和日志系统 — 附录L：流分割器 (Stream Splitter)"
---

# Snort 3 · 附录 C–L

[返回总目录](../snort3_architecture_analysis)

## 附录C：事件和日志系统 {#附录c-事件和日志系统}

### C.1 事件队列 {#c-1-事件队列}

```cpp
struct Event {
    uint32_t gid;         // 生成器ID
    uint32_t sid;         // 签名ID
    uint32_t revision;    // 修订版本
    uint32_t class_id;    // 分类ID
    uint32_t priority;    // 优先级
    const char* msg;      // 消息文本
};

// 事件生成
int queue_event(unsigned gid, unsigned sid);
int queue_event(const OptTreeNode* otn);
```

### C.2 日志动作 {#c-2-日志动作}

```cpp
enum IpsActionType {
    ACTION_ALERT,     // 告警
    ACTION_DROP,      // 丢弃
    ACTION_REJECT,    // 拒绝
    ACTION_SDROP,     // 静默丢弃
    ACTION_LOG,       // 记录
    ACTION_PASS,      // 通过
};

class IpsAction {
public:
    IpsActionType type;
    const char* name;
    virtual void exec(Packet*, Event*) = 0;
};
```

---

## 附录D：配置系统架构 {#附录d-配置系统架构}

### D.1 Module 配置流程 {#d-1-module-配置流程}

```cpp
// 配置流程
Lua配置 → Module::begin() → Module::set() → Module::end()
                                    ↓
                            IpsOption 实例化
                                    ↓
                            Inspector 配置
```

### D.2 SnortConfig 结构 {#d-2-snortconfig-结构}

```cpp
struct SnortConfig {
    // 规则配置
    GHash* otn_map;          // gid:sid → OptTreeNode
    GHash* sig_table;        // 签名表
    
    // 模块配置
    std::vector<Module*> modules;
    
    // 策略配置
    InspectorPolicy* inspection_policy;
    IpsPolicy* ips_policy;
    NetworkPolicy* network_policy;
    
    // DAQ配置
    SFDAQConfig* daq_config;
};
```

---

## 附录E：关键类层次结构 {#附录e-关键类层次结构}

```
snort::Module (基类)
├── HttpModule
├── TcpStreamModule
├── TcpNormalizerModule
├── IpsOptionsModule
└── ...

snort::Inspector (基类)
├── HttpInspect (IT_SERVICE)
├── TcpStreamInspector (IT_STREAM)
├── DnsInspector (IT_SERVICE)
├── SslInspector (IT_SERVICE)
├── Binder (IT_PASSIVE)
└── ...

snort::Codec (基类)
├── IPv4Codec
├── IPv6Codec
├── TcpCodec
├── UdpCodec
├── IcmpCodec
├── EthernetCodec
├── VlanCodec
└── ...

snort::Session (基类)
├── TcpSession
├── UdpSession
├── IcmpSession
└── SctpSession

snort::IpsOption (基类)
├── ContentOption
├── PcreOption
├── HttpBufferOption
├── HttpHeaderOption
├── HttpCookieOption
├── DnsResponseOption
└── ...
```

---

### 完整核心数据结构关系图 {#完整核心数据结构关系图}

```
┌─────────────────────────────────────────────────────────────────┐
│                         Packet                                  │
├─────────────────────────────────────────────────────────────────┤
│ flow: Flow*                    // 关联的流                       │
│ context: IpsContext*           // 检测上下文                     │
│ pkt: uint8_t*                // 原始数据包指针                   │
│ pktlen: uint32_t             // 原始数据包长度                   │
│ data: uint8_t*               // 有效载荷指针                     │
│ dsize: uint16_t              // 有效载荷大小                     │
│ proto_bits: uint32_t         // 协议标识位                       │
│ packet_flags: uint64_t        // 包标志                          │
│ ptrs: DecodeData             // 解码指针集                       │
│ layers: Layer*               // 协议层                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Flow                                    │
├─────────────────────────────────────────────────────────────────┤
│ key: FlowKey*                 // 5元组键                         │
│ session: Session*             // 会话对象                        │
│ flow_data: list<FlowData*>   // 流数据列表                       │
│ stats: FlowStats             // 统计信息                        │
│ state: uint32_t              // 流状态                          │
│ flags: uint32_t              // 流标志                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      IpsContext                                 │
├─────────────────────────────────────────────────────────────────┤
│ packet: Packet*               // 当前包                         │
│ searches: MpseBatch           // MPSE搜索批次                   │
│ file_data: DataPointer        // 检测数据缓冲                    │
│ alt_data: DataBuffer          // 替代缓冲                        │
│ buf: uint8_t*                // 检测缓冲区                      │
│ data: vector<IpsContextData*> // 上下文数据                      │
│ rpl: vector<Replacement>     // 替换内容                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    IpsOption (ContentOption)                     │
├─────────────────────────────────────────────────────────────────┤
│ config: ContentData*         // 配置数据                        │
│ eval(Cursor&, Packet*):      // 评估匹配                        │
│ hash() const: uint32_t       // 计算哈希                        │
│ operator==(const IpsOption&) // 比较                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 附录F：Binder和Wizard机制 {#附录f-binder和wizard机制}

### F.1 Binder检查器 {#f-1-binder检查器}

Binder是Snort 3中的关键组件，负责将检查器绑定到流。

```cpp
// network_inspectors/binder/binder.cc

class Binder : public Inspector {
public:
    Binder(BindModule*);
    ~Binder() override;
    
    void eval(Packet*) override;
    bool configure(SnortConfig*) override;
    
    // Binding配置结构
    struct Binding {
        // 匹配条件
        std::string service;          // 服务名
        uint16_t port;               // 端口
        IpAddress src_ip;           // 源IP
        IpAddress dst_ip;           // 目标IP
        ProtocolId proto;           // 协议
        BindWhen::Role role;        // 角色 (client/server)
        
        // 绑定的检查器
        std::string inspector;       // 检查器名称
        std::string binder_policy;  // 绑定策略
    };
};
```

**Binder 工作流程**：

```
Packet到达
    │
    ├── Binder::eval() 调用
    │   │
    │   ├── 查找匹配的Binding规则
    │   │   匹配条件：port, protocol, service, IP
    │   │
    │   ├── 获取对应的Service Inspector
    │   │   InspectorManager::get_service_inspector()
    │   │
    │   └── 将Inspector绑定到Flow
    │       flow.set_service_inspector()
    │
    └── 后续包直接使用绑定的Inspector
```

### F.2 Wizard服务检测 {#f-2-wizard服务检测}

Wizard用于自动检测未知端口上的服务协议。

```cpp
// service_inspectors/wizard/wizard.cc

class Wizard : public Inspector {
public:
    Wizard(WizardModule*);
    ~Wizard() override;
    
    void eval(Packet*) override;
    StreamSplitter* get_splitter(bool to_server) override;
    
    // 咒语检测
    bool cast_spell(Wand&, Flow*, const uint8_t*, unsigned, uint16_t&);
    
    // 魔法标记
    bool spellbind(const MagicPage*&, Flow*, const uint8_t*, unsigned, const MagicPage*&);
    
    // 诅咒绑定（用于DCE等协议）
    bool cursebind(const vector<CurseServiceTracker>&, Flow*, const uint8_t*, unsigned);
};

class MagicSplitter : public StreamSplitter {
    // 基于魔法的流分割器
    Status scan(Packet*, const uint8_t* data, uint32_t len,
                uint32_t flags, uint32_t* fp) override;
};
```

**Wizard 协议检测流程**：

```
数据包到达
    │
    ├── Wizard::eval()
    │   │
    │   ├── MagicSplitter::scan()
    │   │   │
    │   │   ├── 检查hex标记（十六进制模式）
    │   │   ├── 检查spell标记（ASCII模式）
    │   │   │
    │   │   └── 如果匹配到MagicPage:
    │   │       │
    │   │       ├── 设置服务协议
    │   │       └── 绑定对应的Inspector
    │   │
    │   └── 如果未匹配:
    │       继续尝试DCE等诅咒检测
    │
    └── 后续包使用检测到的服务
```

### F.3 支持的Wizard魔法 {#f-3-支持的wizard魔法}

```
wizard/
├── hexes.cc       // 十六进制模式定义
├── spells.cc      // ASCII模式定义
├── magic.cc/h    // 魔法匹配引擎
├── curse_book.cc/h // 诅咒书（DCE, etc）
│
├── ssl_curse.cc  // SSL/TLS检测
├── dce_curse.cc  // DCE-RPC检测
├── socks_curse.cc // SOCKS检测
├── mms_curse.cc  // MMS检测
└── opcua_curse.cc // OPC-UA检测
```

---

## 附录G：快速模式匹配 (MPSE) 深度解析 {#附录g-快速模式匹配-mpse-深度解析}

### G.1 MpseBatch 结构 {#g-1-mpsebatch-结构}

```cpp
// framework/mpse_batch.h

struct MpseBatch {
    // 批量搜索结构
    std::vector<MpsePattern> patterns;    // 模式列表
    std::vector<MpseResult> results;       // 结果列表
    
    void add_pattern(const uint8_t* pat, unsigned len, void* user);
    void execute(Mpse* engine);
};
```

### G.2 AC自动机原理 {#g-2-ac自动机原理}

```
Aho-Corasick自动机结构：

         ┌─────────────────────────────────────────┐
         │              根节点 (root)               │
         │           (空字符串前缀)                  │
         └────────────────┬────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            │ "a"                       │ "b"
            ▼                           ▼
    ┌───────────┐               ┌───────────┐
    │ 节点 "a"  │               │ 节点 "b"  │
    └─────┬─────┘               └─────┬─────┘
          │                           │
    ┌─────┴─────┐               ┌─────┴─────┐
    │ "b"       │ "c"           │ "a"       │ "c"
    ▼           ▼               ▼           ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ 节点 "ab" │ │ 节点 "ac" │ │ 节点 "ba" │ │ 节点 "bc" │
└───────────┘ └───────────┘ └───────────┘ └───────────┘

失败函数：每个节点有一个失败指针，指向最长后缀匹配
输出函数：每个节点可能输出多个匹配模式
```

### G.3 AC搜索算法 {#g-3-ac搜索算法}

```cpp
// search_engines/ac_full.cc

int AC_Full::search(const uint8_t* T, int n, MpseMatch match, void* context) {
    int state = 0;  // 当前状态
    
    for (int i = 0; i < n; i++) {
        // 获取下一个状态
        while (next[state][T[i]] == -1 && state != 0)
            state = fail[state];  // 失败函数跳转
            
        state = next[state][T[i]];
        
        // 检查输出（所有匹配的模式）
        for (int* out = output[state]; *out != -1; out++) {
            int pat_id = *out;
            int match_end = i;
            int match_start = i - pattern_len[pat_id] + 1;
            
            // 调用回调
            match(context, pat_id, match_start, match_end, nullptr);
        }
    }
    return 0;
}
```

### G.4 快速模式提取 {#g-4-快速模式提取}

```cpp
// 检测选项中，只有fast_pattern选项被提取到MPSE

bool PatternMatchData::can_be_fp() const {
    // 必须是肯定的（非否定）
    // 不能是相对的（relative content）
    // 不能有offset/depth限制
    // 必须是大小写不敏感或者没有字母
    
    if (flags & NO_FP)
        return false;
        
    if (is_relative())
        return false;
        
    if (is_negated())
        return false;
        
    return true;
}
```

---

## 附录H：检测选项类型 {#附录h-检测选项类型}

### H.1 主要IpsOption类型 {#h-1-主要ipsoption类型}

| 选项类型 | 类名 | 描述 |
|---------|------|------|
| content | `ContentOption` | 内容模式匹配 |
| pcre | `PcreOption` | PCRE正则表达式 |
| http_uri | `HttpBufferOption` | HTTP URI缓冲区 |
| http_header | `HttpHeaderOption` | HTTP头部 |
| http_cookie | `HttpCookieOption` | HTTP Cookie |
| http_body | `HttpBodyOption` | HTTP消息体 |
| dsize | `DsizeOption` | 数据大小 |
| flags | `FlagsOption` | TCP标志 |
| ttl | `TtlOption` | TTL值 |
| tos | `TosOption` | TOS值 |
| ip_id | `IpIdOption` | IP标识 |
| icmp_id | `IcmpIdOption` | ICMP标识 |
| seq | `SeqOption` | TCP序列号 |
| ack | `AckOption` | TCP确认号 |

### H.2 ContentOption 详细实现 {#h-2-contentoption-详细实现}

```cpp
// ips_options/ips_content.cc

class ContentOption : public IpsOption {
public:
    ContentOption(ContentData* c) : IpsOption(s_name, RULE_OPTION_TYPE_CONTENT)
    { config = c; }
    
    EvalStatus eval(Cursor& c, Packet* p) override {
        // 1. 获取缓冲区
        const uint8_t* buf = c.buffer();
        unsigned len = c.length();
        
        // 2. 应用偏移和深度
        unsigned start = config->offset;
        unsigned depth = config->depth;
        
        if (config->offset_var >= 0) {
            // 从字节提取变量获取偏移
            start = get_var_value(config->offset_var, p);
        }
        
        // 3. 搜索模式
        int match_pos = searcher->search(
            buf + start, 
            depth ? depth : len - start,
            config->pattern,
            config->pattern_size);
        
        if (match_pos < 0)
            return NO_MATCH;
            
        // 4. 检查否定
        if (config->pmd.is_negated())
            return NO_MATCH;
            
        // 5. 更新光标位置
        c.add_pos(match_pos + config->pattern_size);
        
        return MATCH;
    }
};
```

### H.3 PcreOption 实现 {#h-3-pcreoption-实现}

```cpp
// ips_options/ips_pcre.cc

class PcreOption : public IpsOption {
public:
    PcreOption(PcreData* d) : IpsOption("pcre", RULE_OPTION_TYPE_OTHER)
    { data = d; }
    
    EvalStatus eval(Cursor& c, Packet* p) override {
        // 使用PCRE2库进行正则匹配
        int rc = pcre2_match(
            data->re,           // 编译的正则
            (PCRE2_SPTR)c.buffer(),  // 要搜索的文本
            c.length(),        // 文本长度
            0,                 // 选项
            data->matches,     // 匹配结果
            data->code);       // 代码块
        
        if (rc < 0)
            return NO_MATCH;
            
        // 处理捕获组
        for (int i = 1; i < rc; i++) {
            // 处理捕获的子串
        }
        
        // 更新光标
        if (data->has_curl) {
            // 处理$变量（当前光标位置）
        }
        
        return MATCH;
    }
};
```

---

## 附录I：Pub/Sub事件系统 {#附录i-pub-sub事件系统}

### I.1 发布-订阅机制 {#i-1-发布-订阅机制}

```cpp
// framework/data_bus.h

class DataBus {
public:
    // 发布者注册
    static unsigned get_id(const PubKey&);
    
    // 订阅
    static void subscribe(const PubKey&, unsigned id, DataHandler*);
    static void subscribe_network(const PubKey&, unsigned id, DataHandler*);
    static void subscribe_global(const PubKey&, unsigned id, DataHandler*, SnortConfig&);
    
    // 发布
    static void publish(unsigned pub_id, unsigned evt_id, DataEvent&, Flow* = nullptr);
    
    // 发布到所有网络策略
    static void publish_to_all_network_policies(unsigned pub_id, unsigned evt_id);
};
```

### I.2 常用事件ID {#i-2-常用事件id}

```cpp
// pub_sub/ 目录下的事件定义

// AppId事件 (appid_events.h)
APPID_EVENT,          // 应用ID检测到

// HTTP事件 (http_events.h)
HTTP_REQUEST_HEADERS_EVENT,    // HTTP请求头
HTTP_REQUEST_BODY_EVENT,      // HTTP请求体
HTTP_RESPONSE_HEADERS_EVENT,  // HTTP响应头
HTTP_RESPONSE_BODY_EVENT,     // HTTP响应体

// DNS事件 (dns_events.h)
DNS_RESPONSE_EVENT,           // DNS响应

// 文件事件 (file_events.h)
FILE_EVENT,                  // 文件事件

// 检测事件 (detection_events.h)
DETECTION_EVENT,            // 检测事件
```

### I.3 DataHandler 实现 {#i-3-datahandler-实现}

```cpp
class DataHandler {
public:
    virtual void handle(DataEvent&, Flow*) { }
    const char* module_name;     // 模块名称
    
    // order: 1 = first, 0 = last
    unsigned order = 0;         // 处理顺序
};

// 使用示例
class MyHandler : public DataHandler {
public:
    MyHandler(const char* name) : DataHandler(name) { }
    
    void handle(DataEvent& evt, Flow* flow) override {
        // 处理事件
        const uint8_t* data = evt.get_data();
        unsigned len;
        data = evt.get_data(len);
        
        // ...
    }
};

// 订阅事件
DataHandler* handler = new MyHandler("my_module");
DataBus::subscribe(pub_key, event_id, handler);
```

---

## 附录J：Snort配置系统 {#附录j-snort配置系统}

### J.1 SnortConfig 结构 {#j-1-snortconfig-结构}

```cpp
// main/snort_config.h

struct SnortConfig {
    // 规则和签名
    GHash* otn_map;              // gid:sid → OptTreeNode
    GHash* sig_table;           // 签名表
    
    // 模块
    std::vector<Module*> modules; // 已配置的模块
    
    // 策略
    InspectionPolicy* inspection_policy;   // 检查策略
    IpsPolicy* ips_policy;                 // IPS策略
    NetworkPolicy* network_policy;         // 网络策略
    
    // DAQ
    SFDAQConfig* daq_config;   // DAQ配置
    
    // 标志
    uint32_t run_flags;          // 运行标志
    uint64_t pkt_cnt;           // 包计数限制
    uint64_t pkt_skip;          // 跳过的包数
    
    // BPF
    std::string bpf_filter;     // BPF过滤器
    
    // 线程
    unsigned num_threads;         // 线程数
    unsigned long thread_mask;   // CPU掩码
};
```

### J.2 策略层次结构 {#j-2-策略层次结构}

```
SnortConfig
├── NetworkPolicy (网络策略)
│   ├── 网络设置
│   ├── 规则过滤器
│   └── 预处理程序
│
├── InspectionPolicy (检查策略)
│   ├── Service Bindings
│   ├── HTTP Inspect
│   ├── DNS Inspect
│   └── ...
│
└── IpsPolicy (IPS策略)
    ├── 规则列表
    ├── 规则动作
    └── 事件阈值
```

### J.3 Lua配置示例 {#j-3-lua配置示例}

```lua
-- snort.lua

-- 全局配置
snort = {
    -- 日志目录
    logdir = "/var/log/snort",
    
    -- 接口配置
    interface = "eth0",
}

- 网络配置
network_policy = {
    id = 1,
    -- ...
}

-- 检查配置
inspection_policy = {
    name = "balanced",
    
    -- 服务检查器
    binders = {
        { type = "tcp", ports = "80", service = "http_inspect" },
        { type = "tcp", ports = "443", service = "ssl_inspect" },
    },
}

-- HTTP检查器配置
http_inspect = {
    request_depth = 6144,
    response_depth = 6144,
    -- ...
}
```

---

## 附录K：DAQ数据获取接口 {#附录k-daq数据获取接口}

### K.1 DAQ模块架构 {#k-1-daq模块架构}

DAQ (Data AcQuisition) 负责从网络接口或文件获取数据包。

```cpp
// packet_io/sfdaq.h

class SFDAQ {
public:
    // 加载和初始化
    static void load(const SFDAQConfig*);
    static void unload();
    
    // 实例管理
    static bool init(const SFDAQConfig*, unsigned total_instances);
    static bool init_instance(SFDAQInstance*, const std::string& bpf_string);
    static void term();
    
    // 统计
    static const DAQ_Stats_t* get_stats();
    
    // 能力查询
    static bool can_inject();
    static bool can_inject_raw();
    static bool can_replace();
    static bool can_run_unprivileged();
    
    // 包注入
    static int inject(DAQ_Msg_h, int rev, const uint8_t* buf, uint32_t len);
};
```

### K.2 SFDAQInstance 类 {#k-2-sfdaqinstance-类}

```cpp
// packet_io/sfdaq_instance.h

class SFDAQInstance {
public:
    SFDAQInstance(const char* source, unsigned id, const SFDAQConfig* config);
    ~SFDAQInstance();
    
    // 获取数据包
    DAQ_RecvStatus acquire(DAQ_Msg_h* msg, uint32_t timeout);
    int dispatch(DAQ_Msg_h msg);
    
    // 发送处置结果
    int final(DAQ_Msg_h msg, DAQ_Verdict verdict);
    
    // 注入数据包
    int inject(const uint8_t* pkt, uint32_t len, DAQ_PktHdr* hdr);
    
    // 能力查询
    bool can_start_unprivileged() const;
};
```

### K.3 DAQ消息结构 {#k-3-daq消息结构}

```cpp
// libdaq common.h

struct _daq_msg {
    DAQ_Msg_h header;
    const uint8_t* data;
    uint32_t len;
    DAQ_PktHdr_t* pkthdr;
};

struct DAQ_PktHdr_t {
    uint64_t ts;              // 时间戳
    uint32_t caplen;         // 捕获长度
    uint32_t pktlen;          // 原始长度
    int32_t if_idx;          // 接口索引
    int32_t rec_idx;         // 记录索引
    uint8_t flags;           // 标志
    uint8_t opaque;          // 扩展数据
};
```

### K.4 DAQ裁决 {#k-4-daq裁决}

```cpp
enum DAQ_Verdict {
    DAQ_VERDICT_PASS,      // 通过
    DAQ_VERDICT_BLOCK,     // 阻止
    DAQ_VERDICT_REPLACE,    // 替换
    DAQ_VERDICT_WHITELIST,  // 白名单
    DAQ_VERDICT_BLACKLIST,  // 黑名单
    DAQ_VERDICT_IGNORE,      // 忽略
    DAQ_VERDICT_RETRY,       // 重试
};
```

---

## 附录L：流分割器 (Stream Splitter) {#附录l-流分割器-stream-splitter}

### L.1 StreamSplitter 基类 {#l-1-streamsplitter-基类}

```cpp
// stream/stream_splitter.h

class StreamSplitter {
public:
    virtual ~StreamSplitter();
    
    // 扫描输入数据，返回需要flush的字节数
    virtual Status scan(Flow*, const uint8_t* data,
                       uint32_t len, uint32_t* consumed) = 0;
    
    // 准备重组
    virtual void reassemble(Flow*, uint64_t, const uint8_t*,
                           uint32_t, uint32_t, uint32_t);
    
    // 完成重组
    virtual bool finish(Flow*) { return true; }
    
    // 是否是PAF（Protocol Aware Flushing）
    virtual bool is_paf() { return false; }
    
    enum Status {
        NONE,    // 无事发生
        PARTIAL, // 部分数据
        READY    // PDU就绪
    };
};
```

### L.2 HTTP流分割器 {#l-2-http流分割器}

```cpp
// service_inspectors/http_inspect/http_stream_splitter.h

class HttpStreamSplitter : public HttpStreamSplitterBase {
public:
    HttpStreamSplitter(bool is_client_to_server, HttpInspect* my_inspector_);
    
    // PAF扫描
    Status scan(Flow*, const uint8_t* data, uint32_t length,
                uint32_t* flush_offset) override;
    
    // 重组
    const snort::StreamBuffer reassemble(Flow*, unsigned total,
        unsigned, const uint8_t* data, unsigned len,
        uint32_t flags, unsigned& copied) override;
    
    bool is_paf() override { return true; }
};

// PAF工作原理：
// 1. 扫描数据，找到消息边界
// 2. 返回READY状态和flush偏移
// 3. Stream调用reassemble()获取完整消息
```

---
