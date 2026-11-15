---
title: "Snort 3 · 数据结构与插件开发"
description: "总结 — 附录B：编解码器架构"
---

# Snort 3 · 数据结构与插件开发

[返回总目录](../snort3_architecture_analysis)

## 总结 {#总结}

这种架构使得 Snort 3 具有良好的可扩展性，用户可以通过编写插件来添加新的协议支持、检测功能或输出格式。

---

## 附录：关键数据结构详解 {#附录-关键数据结构详解}

### A.1 Packet 结构 (src/protocols/packet.h) {#a-1-packet-结构-src-protocols-packet-h}

**职责**：表示一个网络数据包，包含所有协议层信息

```cpp
struct Packet {
    Flow* flow;                       // 关联的流
    uint64_t packet_flags;             // 包标志 (PKT_*)
    uint32_t proto_bits;              // 协议标识位
    
    // 数据指针
    const uint8_t* pkt;               // 原始数据包指针
    uint32_t pktlen = 0;              // 原始数据包长度
    const uint8_t* data;              // 有效载荷指针
    uint16_t dsize;                    // 有效载荷大小
    
    // 解码信息
    DecodeData ptrs;                   // 便捷指针集
    Layer* layers;                     // 解码的封装层
    
    // 检测上下文
    IpsContext* context;               // 检测上下文
    
    // 元数据
    const DAQ_PktHdr_t* pkth;         // DAQ数据包头
    PseudoPacketType pseudo_type;     // 伪包类型
    
    // 标志位定义
    #define PKT_REBUILT_FRAG    0x00000001  // 分片重组包
    #define PKT_REBUILT_STREAM  0x00000002  // 流重组包
    #define PKT_STREAM_EST      0x00000008  // 来自已建立流
    #define PKT_FROM_CLIENT     0x00000080  // 来自客户端
    #define PKT_FROM_SERVER     0x00000040  // 来自服务器
    #define PKT_PSEUDO         0x00020000  // 伪包
    // ... 更多标志
    
    // 类型查询方法
    bool is_tcp() const;              // 是否TCP
    bool is_udp() const;              // 是否UDP
    bool is_icmp() const;             // 是否ICMP
    bool is_ip4() const;              // 是否IPv4
    bool is_ip6() const;              // 是否IPv6
    bool is_from_client() const;      // 是否来自客户端
    bool is_rebuilt() const;          // 是否重组包
};
```

### A.2 Flow 结构 (src/flow/flow.h) {#a-2-flow-结构-src-flow-flow-h}

**职责**：表示一个网络会话，跟踪所有相关状态

```cpp
class Flow {
public:
    FlowKey* key;                     // 流键（5元组）
    uint32_t state;                   // 流状态
    uint32_t flags;                   // 流标志
    
    // 统计信息
    FlowStats stats;                  // 字节/包计数
    
    // 流数据管理
    std::list<FlowData*> flow_data;   // FlowData列表
    
    // 会话跟踪
    Session* session;                 // 会话对象
    
    // 流重组
    uint8_t* reassembled_data;        // 重组数据
    unsigned reassembled_len;         // 重组长度
    
    // 流标志位
    #define SSNFLAG_SEEN_CLIENT    0x00000001
    #define SSNFLAG_SEEN_SERVER    0x00000002
    #define SSNFLAG_ESTABLISHED    0x00000004
    #define SSNFLAG_MIDSTREAM      0x00000008
    #define SSNFLAG_DROP_CLIENT    0x00010000
    #define SSNFLAG_DROP_SERVER    0x00020000
    // ... 更多标志
    
    // 方法
    void set_state(unsigned);         // 设置状态
    void update_stats(uint64_t, uint64_t);  // 更新统计
    void add_flow_data(FlowData*);   // 添加流数据
    FlowData* get_flow_data(unsigned id);  // 获取流数据
};
```

### A.3 IpsContext 结构 (src/detection/ips_context.h) {#a-3-ipscontext-结构-src-detection-ips-context-h}

**职责**：保存检测上下文，包含检测所需的所有状态

```cpp
class IpsContext {
public:
    enum State { IDLE, BUSY, SUSPENDED };
    
    // 上下文数据管理
    void set_context_data(unsigned id, IpsContextData*);
    IpsContextData* get_context_data(unsigned id) const;
    
    // 包引用
    Packet* packet = nullptr;         // 当前包
    Packet* wire_packet = nullptr;    // 原始数据包
    Packet* encode_packet = nullptr;  // 编码包
    
    // 检测缓冲
    uint8_t* buf = nullptr;          // 检测缓冲区
    
    // 替代数据
    DetectionBuffer alt_data;         // 替代缓冲区
    
    // 替换内容
    std::vector<Replacement> rpl;    // 替换内容列表
    
    // 流快照
    FlowSnapshot flow;                // 流状态快照
    
    // 上下文链接（用于依赖检测）
    void link(IpsContext* next);      // 链接下一个上下文
    void unlink();                    // 取消链接
    IpsContext* dependencies() const; // 获取依赖
    IpsContext* next() const;        // 获取下一个
    
    // 回调管理
    void register_post_callback(Callback callback);
    void post_detection();            // 检测后处理
    
    // 状态管理
    void disable_detection();         // 禁用检测
    void disable_inspection();        // 禁用检查
};
```

### A.4 Cursor 结构 (src/framework/cursor.h) {#a-4-cursor-结构-src-framework-cursor-h}

**职责**：在签名评估期间提供对当前缓冲区的访问

```cpp
class Cursor {
public:
    // 缓冲区设置
    void set(const char* s, const uint8_t* b, unsigned n, bool ext = false);
    void set(const char* s, uint64_t id, const uint8_t* b, unsigned n, bool ext = false);
    
    // 位置操作
    bool add_pos(unsigned n);        // 增加位置
    bool set_pos(unsigned n);        // 设置位置
    
    // 缓冲区查询
    const uint8_t* buffer() const;   // 获取缓冲区
    unsigned size() const;           // 获取大小
    unsigned length() const;         // 剩余长度
    unsigned get_pos() const;        // 获取当前位置
    const uint8_t* start() const;    // 获取起始指针
    const uint8_t* endo() const;     // 获取结束指针
    
    // 扩展数据
    bool awaiting_data() const;      // 是否等待更多数据
    void set_accumulation(bool);     // 设置累积标志
    
    // 缓冲区标识
    uint64_t id() const;            // 获取缓冲区ID
    const char* get_name() const;    // 获取缓冲区名称
    
private:
    unsigned buf_size = 0;          // 缓冲区大小
    unsigned current_pos = 0;        // 当前位置
    unsigned delta = 0;              // 循环偏移
    unsigned file_pos = 0;           // 文件位置
    const uint8_t* buf = nullptr;    // 缓冲区指针
    const char* name = nullptr;      // 缓冲区名称
    uint64_t buf_id = 0;            // 缓冲区ID
    bool extensible = false;         // 是否可扩展
    bool is_accumulated = false;     // 是否累积
};
```

### A.5 IpsOption 结构 (src/framework/ips_option.h) {#a-5-ipsoption-结构-src-framework-ips-option-h}

**职责**：IPS规则选项的基类，所有检测选项都继承自此类

```cpp
class IpsOption {
public:
    enum EvalStatus { NO_MATCH, MATCH, NO_ALERT, FAILED_BIT };
    
    // 哈希和比较（主线程）
    virtual uint32_t hash() const;
    virtual bool operator==(const IpsOption&) const;
    
    // 检测评估（数据包线程）
    virtual EvalStatus eval(Cursor&, Packet*);
    
    // 光标操作
    virtual bool is_relative();       // 是否相对匹配
    virtual CursorActionType get_cursor_type() const;
    
    // 快速模式选项
    virtual PatternMatchData* get_pattern(SnortProtocolId, RuleDirection = RULE_WO_DIR);
    
    // 选项类型
    option_type_t get_type() const;
    const char* get_name() const;
    
    // PDU区段
    virtual section_flags get_pdu_section(bool to_server) const;
    
protected:
    IpsOption(const char* s, option_type_t t = RULE_OPTION_TYPE_OTHER);
    
private:
    const char* name;
    option_type_t type;
};

// IpsApi - 规则选项插件API
struct IpsApi {
    BaseApi base;
    RuleOptType type;                 // 选项类型
    int max_per_rule;               // 每规则最大实例数
    unsigned protos;                 // 协议位掩码
    
    IpsApiFunc pinit;               // 插件初始化
    IpsApiFunc pterm;               // 插件清理
    IpsNewFunc ctor;               // 创建选项实例
    IpsDelFunc dtor;               // 销毁选项实例
};
```

### A.6 DetectionEngine 检测流程详解 {#a-6-detectionengine-检测流程详解}

```
DetectionEngine::detect(Packet*)
    │
    ├── 1. 获取/创建检测上下文
    │   IpsContext* context = get_context();
    │
    ├── 2. 设置包信息
    │   context->packet = packet;
    │   context->wire_packet = packet;
    │
    ├── 3. 准备检测缓冲区
    │   set_file_data(dp);  // 设置要检测的数据
    │
    ├── 4. 快速模式匹配
    │   Mpse::search() - AC/BNFA/Hyperscan
    │   │
    │   └── 对每个匹配的模式:
    │       │
    │       ├── 5. 规则选项评估
    │       │   IpsOption::eval(Cursor, Packet)
    │       │   │
    │       │   └── 对每个选项:
    │       │       content_opt->eval()   // content匹配
    │       │       pcre_opt->eval()     // PCRE匹配
    │       │       http_opt->eval()     // HTTP选项
    │       │       ...
    │       │
    │       ├── 6. 规则动作检查
    │       │   alert, drop, reject, pass, log
    │       │
    │       └── 7. 事件生成
    │           queue_event(gid, sid)
    │
    └── 8. 完成检测
        finish_inspect(packet, inspected);
```

### A.7 Content选项实现 (ips_content.cc) {#a-7-content选项实现-ips-content-cc}

```cpp
class ContentOption : public IpsOption {
    ContentOption(ContentData* c) : IpsOption(s_name, RULE_OPTION_TYPE_CONTENT)
    { config = c; }
    
    uint32_t hash() const override;
    bool operator==(const IpsOption&) const override;
    
    CursorActionType get_cursor_type() const override
    { return CAT_ADJUST; }  // 调整光标位置
    
    bool is_relative() override
    { return config->pmd.is_relative(); }
    
    EvalStatus eval(Cursor&, Packet*) override;
};

struct ContentData {
    PatternMatchData pmd;            // 模式匹配数据
    LiteralSearch* searcher;         // 搜索引擎
    int8_t offset_var;              // 偏移变量
    int8_t depth_var;               // 深度变量
    unsigned match_delta;            // 最大跳转距离
};

// Content匹配评估过程：
// 1. 如果设置了偏移/深度，提取变量值
// 2. 在缓冲区中搜索模式
// 3. 如果匹配，检查否字
// 4. 更新光标位置
// 5. 返回 MATCH/NO_MATCH
```

### A.8 HTTP检查器架构 (http_inspect/) {#a-8-http检查器架构-http-inspect}

HTTP检查器是Snort 3中最复杂的服务检查器之一：

```
http_inspect/
├── http_inspect.cc/h       # 主检查器类
├── http_module.cc/h        # 配置模块
├── http_flow_data.cc/h     # 流数据
├── http_transaction.cc/h   # HTTP事务
├── http_msg_*.cc/h         # 消息处理
│   ├── http_msg_request.cc/h   # 请求解析
│   ├── http_msg_status.cc/h     # 状态解析
│   ├── http_msg_header.cc/h     # 头部解析
│   ├── http_msg_body.cc/h       # 消息体解析
│   └── http_msg_trailer.cc/h    # 尾部解析
├── http_cutter.cc/h        # 消息切割
├── http_uri.cc/h           # URI解析
├── http_uri_norm.cc/h      # URI规范化
├── http_js_norm.cc/h       # JavaScript规范化
├── ips_http.cc/h           # HTTP规则选项
└── http_stream_splitter.cc/h  # 流分割器

HttpInspect 类层次：
HttpInspect (IT_SERVICE)
├── HttpStreamSplitter (StreamSplitter)
├── HTTP请求处理
│   ├── 解析请求行
│   ├── 解析头部
│   ├── 解析消息体
│   └── 规范化数据
└── HTTP响应处理
    ├── 解析状态行
    ├── 解析头部
    ├── 解析消息体
    └── 规范化数据

关键缓冲区类型：
- http_request_line    // 请求行
- http_status_line     // 状态行
- http_request_line    // 请求头
- http_response_header // 响应头
- http_cookie         // Cookie
- http_raw_uri         // 原始URI
- http_normalized_uri  // 规范化URI
- http_body            // 消息体
- http_raw_body        // 原始消息体
```

---

## TCP流跟踪架构详解 {#tcp流跟踪架构详解}

### A.9 Session 类层次结构 {#a-9-session-类层次结构}

```
Session (抽象基类)
├── TcpSession           // TCP会话跟踪
├── UdpSession          // UDP会话跟踪
├── Icmpsession         // ICMP会话跟踪
└── SctpSession         // SCTP会话跟踪
```

**Session 基类** (src/flow/session.h)：
```cpp
class Session {
public:
    virtual ~Session();
    
    // 会话设置和清理
    virtual bool setup(Packet*) = 0;
    virtual void restart(Packet* p) = 0;
    virtual bool precheck(Packet* p) = 0;
    virtual int process(Packet*) = 0;
    virtual void clear() = 0;
    virtual void cleanup(Packet* = nullptr) = 0;
    
    // 流分割器
    virtual void set_splitter(bool, StreamSplitter*) = 0;
    virtual StreamSplitter* get_splitter(bool) = 0;
    
    // 重组
    virtual void flush() = 0;
    virtual void flush_client(Packet*) = 0;
    virtual void flush_server(Packet*) = 0;
    
    // 告警
    virtual bool add_alert(Packet*, uint32_t gid, uint32_t sid) = 0;
    virtual bool check_alerted(Packet*, uint32_t gid, uint32_t sid) = 0;
};
```

### A.10 TcpStreamTracker 状态机 {#a-10-tcpstreamtracker-状态机}

TCP流跟踪器维护TCP连接的状态：

```cpp
class TcpStreamTracker {
    enum TcpState : uint8_t {
        TCP_LISTEN,        // 等待连接
        TCP_SYN_SENT,      // 已发送SYN
        TCP_SYN_RECV,      // 收到SYN
        TCP_ESTABLISHED,   // 连接已建立
        TCP_MID_STREAM_SENT,   // 中途开始
        TCP_MID_STREAM_RECV,   // 中途接收
        TCP_FIN_WAIT1,     // FIN等待1
        TCP_FIN_WAIT2,     // FIN等待2
        TCP_CLOSE_WAIT,     // 关闭等待
        TCP_CLOSING,       // 关闭中
        TCP_LAST_ACK,      // 最后ACK
        TCP_TIME_WAIT,     // 时间等待
        TCP_CLOSED,        // 已关闭
        TCP_STATE_NONE,
        TCP_MAX_STATES
    };
    
    enum TcpEvent : uint8_t {
        TCP_SYN_SENT_EVENT,
        TCP_SYN_ACK_SENT_EVENT,
        TCP_ACK_SENT_EVENT,
        TCP_DATA_SEG_SENT_EVENT,
        TCP_FIN_SENT_EVENT,
        TCP_RST_SENT_EVENT,
        // ... 更多事件
    };
};
```

### A.11 TCP重组器架构 {#a-11-tcp重组器架构}

```
TcpReassembler
├── TcpReassemblySegments  // 重组段管理
│   ├── TcpSegmentNode    // 段节点
│   └── TcpSegmentDescriptor // 段描述符
├── TcpOverlapResolver    // 重叠处理
├── TcpNormalizer         // TCP规范化
└── FlushMgr             //  Flush管理
```

**关键功能**：
- 顺序/乱序段处理
- 重叠数据解析
- TCP规范化（去除冗余数据）
- PAF（Protocol Awareness Flush）

### A.12 Stream Splitter 接口 {#a-12-stream-splitter-接口}

流分割器用于将数据流分割成逻辑PDU：

```cpp
class StreamSplitter {
public:
    virtual ~StreamSplitter();
    
    // 扫描输入数据
    virtual Status scan(Flow*, const uint8_t* data, 
                       uint32_t len, uint32_t* consumed) = 0;
    
    // 重组
    virtual void reassemble(Flow*, uint64_t, const uint8_t*,
                           uint32_t, uint32_t, uint32_t);
    
    // 完成
    virtual bool finish(Flow*) { return true; }
    
    // 是否为PAF
    virtual bool is_paf() { return false; }
    
    enum Status { NONE, PARTIAL, READY };
};
```

---

## 规则匹配深度解析 {#规则匹配深度解析}

### A.13 规则编译流程 {#a-13-规则编译流程}

```
规则文本 (snort.lua / .rules)
    │
    ▼
Parser (parser/)
    │
    ├── 解析规则头 (action, protocol, IP, port)
    │
    └── 解析规则选项 (content, pcre, http_*)
    │
    ▼
OptTreeNode 创建
    │
    ├── IpsOption 实例化
    ├── PatternMatchData 填充
    └── Fast Pattern 提取
    │
    ▼
规则注册到 SnortConfig
    │
    ▼
OTN_MAP (gid:sid → OptTreeNode)
```

### A.14 快速模式匹配器 (MPSE) {#a-14-快速模式匹配器-mpse}

快速模式匹配使用多模式匹配算法：

```cpp
class Mpse {
    // 添加模式
    virtual int add_pattern(
        const uint8_t* pat, unsigned len,
        const PatternDescriptor&, void* user) = 0;
    
    // 编译模式
    virtual int prep_patterns(SnortConfig*) = 0;
    
    // 搜索单个缓冲区
    virtual int search(
        const uint8_t* T, int n,
        MpseMatch, void* context,
        int* current_state) = 0;
    
    // 搜索所有缓冲区
    virtual void search(MpseBatch&, MpseType);
};

// 匹配回调函数类型
typedef void (*MpseMatch)(
    void* context, int id, int start, int end, void* data);
```

### A.15 AC自动机实现 (ac_full.cc) {#a-15-ac自动机实现-ac-full-cc}

AC（Aho-Corasick）自动机是Snort 3中最常用的快速模式匹配算法：

```
AC结构：
├── 状态节点（每个节点代表一个前缀）
├── 失败函数（匹配失败时跳转）
├── 输出函数（匹配成功时输出）
└── 转移函数（字符转移）

搜索过程：
1. 从根节点开始
2. 对于每个输入字符：
   - 沿转移函数前进
   - 沿失败函数回溯并检查输出
3. 所有匹配的模式被记录
```

### A.16 Content匹配详细流程 {#a-16-content匹配详细流程}

```
DetectionEngine::detect()
    │
    ├── 1. 设置检测缓冲区
    │   DetectionEngine::set_file_data()
    │
    ├── 2. 获取快速模式
    │   fp_detect() → get_fp_buf()
    │
    ├── 3. 执行MPSE搜索
    │   mpse->search()
    │   │
    │   └── 对每个匹配:
    │       │
    │       ├── 4. 获取OptTreeNode
    │       │   fp_match_to_otn()
    │       │
    │       ├── 5. 评估规则选项
    │       │   fp_eval_option()
    │       │   │
    │       │   └── IpsOption::eval()
    │       │       │
    │       │       └── ContentOption::eval()
    │       │           │
    │       │           ├── 获取偏移/深度
    │       │           ├── 搜索模式
    │       │           ├── 检查否字
    │       │           └── 更新光标
    │       │
    │       └── 6. 检查否定匹配
    │           如果所有选项都匹配：
    │               生成事件
    │
    └── 7. 完成检测
        finish_inspect()
```

---

## 插件开发指南 {#插件开发指南}

### A.17 创建自定义Inspector {#a-17-创建自定义inspector}

1. **定义Inspector类**：

```cpp
// my_inspector.h
class MyInspector : public Inspector {
public:
    MyInspector(const MyParaList* params);
    ~MyInspector() override;
    
    // 配置
    bool configure(SnortConfig*) override;
    
    // 包处理
    bool likes(Packet*) override;
    void eval(Packet*) override;
    
    // 数据获取
    bool get_buf(const char* key, Packet*, InspectionBuffer&) override;
    
    // 流分割器
    StreamSplitter* get_splitter(bool to_server) override;
};
```

2. **定义InspectApi**：

```cpp
// my_inspector.cc
static Inspector* ctor(Module* m) {
    MyParaList* p = get_my_params(m);
    return new MyInspector(p);
}

static void dtor(Inspector* p) {
    delete p;
}

static const InspectApi my_api = {
    {
        IPT_NETWORK,           // 类型
        "my_inspector",       // 名称
        ITID_VERSION,          // API版本
    },
    // ...
    (InspectNew)ctor,
    (InspectDelFunc)dtor,
};
```

3. **注册插件**：

```cpp
// 在插件初始化时
void PluginInit() {
    PluginManager::add_plugin(&my_api.base);
}
```

### A.18 创建自定义IpsOption {#a-18-创建自定义ipsoption}

1. **定义选项类**：

```cpp
class MyOption : public IpsOption {
public:
    MyOption(ContentData* c) : IpsOption(s_name, RULE_OPTION_TYPE_CONTENT)
    { config = c; }
    
    uint32_t hash() const override;
    bool operator==(const IpsOption&) const override;
    
    EvalStatus eval(Cursor&, Packet*) override;
    
    CursorActionType get_cursor_type() const override
    { return CAT_ADJUST; }
};
```

2. **实现评估逻辑**：

```cpp
IpsOption::EvalStatus MyOption::eval(Cursor& c, Packet* p) {
    // 获取数据
    const uint8_t* data = c.buffer();
    unsigned size = c.length();
    
    // 执行匹配
    if (match(data, size, config)) {
        // 更新光标
        c.add_pos(config->pattern_size);
        return MATCH;
    }
    return NO_MATCH;
}
```

---

## 总结 {#总结-1}

Snort 3 的架构设计体现了现代网络安全设备的关键原则：

1. **模块化设计**：所有核心组件（检查器、编解码器、搜索引擎）都是可插拔的
2. **数据流抽象**：通过 Packet、Flow、IpsContext、Cursor 等结构管理复杂的状态
3. **发布-订阅模式**：通过 DataBus 实现组件间松耦合通信
4. **多线程支持**：Analyzer 在独立线程中运行，支持并行数据包处理
5. **灵活的配置**：通过 Module 和 Lua 配置系统，支持运行时重载

### 核心数据结构关系图 {#核心数据结构关系图}

```
Packet
├── flow: Flow*                    // 关联的流
├── context: IpsContext*           // 检测上下文
├── ptrs: DecodeData              // 解码指针
└── layers: Layer*                // 协议层

Flow
├── key: FlowKey*                 // 5元组键
├── session: Session*             // 会话对象
├── flow_data: list<FlowData*>   // 流数据列表
└── stats: FlowStats              // 统计信息

IpsContext
├── packet: Packet*               // 当前包
├── searches: MpseBatch           // MPSE搜索
├── file_data: DataPointer        // 检测数据
├── alt_data: DataBuffer          // 替代缓冲
└── data: vector<IpsContextData*> // 上下文数据

IpsOption (ContentOption, PcreOption, HttpOption...)
├── eval(): 评估选项匹配
├── hash(): 计算哈希值
└── operator==(): 选项比较
```

---

## 附录B：编解码器架构 {#附录b-编解码器架构}

### B.1 Codec模块结构 {#b-1-codec模块结构}

```
codecs/
├── codec_module.cc/h     // CodecModule - 编解码器配置模块
├── codec_api.cc/h       // CodecApi - 编解码器插件API
├── ip/
│   ├── cd_ipv4.cc/h     // IPv4解码器
│   ├── cd_ipv6.cc/h     // IPv6解码器
│   ├── cd_tcp.cc/h      // TCP解码器
│   ├── cd_udp.cc/h      // UDP解码器
│   ├── cd_icmp4.cc/h    // ICMPv4解码器
│   ├── cd_icmp6.cc/h    // ICMPv6解码器
│   ├── cd_frag.cc/h     // IP分片重组
│   ├── cd_gre.cc/h      // GRE解码器
│   └── cd_esp.cc/h      // ESP解码器
├── link/
│   ├── cd_ethernet.cc   // 以太网解码器
│   ├── cd_vlan.cc/h     // VLAN解码器
│   ├── cd_mpls.cc/h     // MPLS解码器
│   └── cd_ppp.cc/h      // PPP解码器
└── misc/
    ├── cd_bad_proto.cc   // 未知协议处理
    └── ...
```

### B.2 DecodeData 结构 {#b-2-decodedata-结构}

```cpp
struct DecodeData {
    // 传输层指针
    const snort::tcp::TCPHdr* tcph = nullptr;
    const snort::udp::UDPHdr* udph = nullptr;
    const snort::icmp::ICMPHdr* icmph = nullptr;
    
    // 端口
    uint16_t sp = 0;    // 源端口
    uint16_t dp = 0;    // 目的端口
    
    // 解码信息
    uint32_t decode_flags = 0;   // 解码标志
    PktType type = PktType::NONE;  // 数据包类型
    
    // IP API
    snort::ip::IpApi ip_api;
    
    // MPLS头
    snort::mpls::MplsHdr mplsHdr = {};
};

// 协议位掩码
#define PROTO_BIT__TCP    0x000002
#define PROTO_BIT__UDP    0x000004
#define PROTO_BIT__ICMP   0x000008

// 解码标志
enum DecodeFlags {
    DECODE_ERR_CKSUM_IP =   0x00000001,
    DECODE_ERR_CKSUM_TCP =  0x00000002,
    DECODE_FRAG =           0x00000040,  // 分片包
    DECODE_DF =             0x00000100,  // 不分片
};
```

### B.3 IpApi 结构 {#b-3-ipapi-结构}

```cpp
namespace snort { namespace ip {

class IpApi {
public:
    void set_ip4(const IP4Hdr*);
    void set_ip6(const IP6Hdr*);
    
    bool is_ip4() const;
    bool is_ip6() const;
    bool is_ip() const;
    
    const SfIp* get_src() const;
    const SfIp* get_dst() const;
    
    uint8_t get_ttl() const;
    bool has_options() const;
};

}}
```

### B.4 Packet 协议层指针 {#b-4-packet-协议层指针}

```cpp
// protocols/packet.h
struct Packet {
    Flow* flow;                       // 关联的流
    uint64_t packet_flags;            // 包标志
    uint32_t proto_bits;             // 协议标识
    
    const uint8_t* pkt;             // 原始数据包
    uint32_t pktlen;                // 原始长度
    const uint8_t* data;            // 有效载荷
    uint16_t dsize;                 // 有效载荷大小
    
    DecodeData ptrs;                 // 解码指针
    Layer* layers;                   // 协议层
    
    // 便捷方法
    bool is_tcp() const;
    bool is_udp() const;
    bool is_icmp() const;
    bool is_ip4() const;
    bool is_ip6() const;
};
```

---
