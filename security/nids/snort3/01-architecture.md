---
title: "Snort 3 · 架构与数据包流程"
description: "概述 — 模块详解"
---

# Snort 3 · 架构与数据包流程

[返回总目录](../snort3_architecture_analysis)

## 概述 {#概述}

Snort 3 是下一代 Snort IPS（入侵预防系统），是一个用 C++ 编写的开源网络入侵检测/预防系统。与 Snort 2.x 相比，Snort 3 采用了全新的架构设计，主要特性包括：

- **多线程数据包处理**：支持多个数据包处理线程
- **共享配置和属性表**：所有线程共享统一配置
- **可插拔架构**：核心组件可替换
- **自动服务检测**：支持无端口配置的服务检测
- **脚本化配置**：使用 Lua 进行配置和脚本编写

---

## 整体架构 {#整体架构}

### 2.1 系统层次结构 {#_2-1-系统层次结构}

```
┌─────────────────────────────────────────────────────────────────┐
│                        Snort Main                                │
│                     (src/main.cc)                                │
├─────────────────────────────────────────────────────────────────┤
│                      Analyzer                                    │
│              (Packet Processing Thread)                          │
├─────────────────────────────────────────────────────────────────┤
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│    │  Inspector  │  │  Inspector  │  │  Inspector  │  ...     │
│    │   (IT_NET)  │  │   (IT_SVC)  │  │   (IT_STRM) │           │
│    └─────────────┘  └─────────────┘  └─────────────┘           │
├─────────────────────────────────────────────────────────────────┤
│                    InspectorManager                              │
├─────────────────────────────────────────────────────────────────┤
│      ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│      │  Codec   │    │  Codec   │    │  Codec   │   ...      │
│      └──────────┘    └──────────┘    └──────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                      Detection Engine                            │
├─────────────────────────────────────────────────────────────────┤
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│   │  Action  │   │   Log    │   │ Filter   │   │Search Eng│   │
│   └──────────┘   └──────────┘   └──────────┘   └──────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 主要目录结构 {#_2-2-主要目录结构}

```
src/
├── main/           # 主程序入口，Snort类，配置管理
├── packet_io/      # 数据包获取接口（DAQ）
├── framework/      # 框架基础：Inspector, Codec, Module基类
├── codecs/         # 协议编解码器
├── detection/      # 检测引擎，规则匹配
├── service_inspectors/  # 服务检查器（HTTP, DNS, SSL等）
├── network_inspectors/   # 网络层检查器
├── stream/         # 流重组和状态跟踪
├── flow/           # 流管理和状态
├── filters/        # 过滤器（速率过滤，检测过滤）
├── actions/        # 响应动作
├── loggers/        # 日志输出
├── protocols/      # 协议定义
├── ips_options/    # IPS规则选项
├── search_engines/ # 模式匹配搜索引擎
├── pub_sub/        # 发布-订阅框架
├── managers/       # 插件/模块管理器
├── helpers/        # 辅助工具
├── utils/          # 通用工具函数
├── memory/         # 内存管理
├── time/           # 时间处理
├── profiler/       # 性能分析
└── trace/          # 追踪调试
```

---

## 核心组件 {#核心组件}

### 3.1 Snort 类 (src/main/snort.h) {#_3-1-snort-类-src-main-snort-h}

**职责**：系统级初始化、清理和配置管理

**关键结构**：

```cpp
class Snort {
public:
    static void setup(int argc, char* argv[]);    // 初始化
    static bool drop_privileges();                  // 降权
    static void cleanup();                          // 清理
    static bool exit_requested();                   // 请求退出
    static bool is_reloading();                     // 配置重载中
    
    static void prepare_reload();                   // 准备重载
    static SnortConfig* get_reload_config(const char* fname);  // 获取新配置
};
```

### 3.2 Analyzer 类 (src/main/analyzer.h) {#_3-2-analyzer-类-src-main-analyzer-h}

**职责**：数据包获取和处理循环，在独立线程中运行

**关键结构**：

```cpp
class Analyzer {
public:
    enum class State {
        NEW, INITIALIZED, STARTED, RUNNING, 
        PAUSED, STOPPED, FAILED
    };
    
    Analyzer(SFDAQInstance*, unsigned id, const char* source, 
             uint64_t msg_cnt = 0, const uint32_t retry_timeout = 200);
    
    void run(bool paused = false);    // 运行分析循环
    void start();                      // 启动
    void stop();                       // 停止
    void pause();                      // 暂停
    void resume(uint64_t msg_cnt);     // 恢复
    
    void execute(AnalyzerCommand*);    // 执行命令
    void process_rebuilt_packet(Packet*, const DAQ_PktHdr_t*, 
                                const uint8_t* pkt, uint32_t pktlen);  // 处理重组包
};
```

**数据包处理流程**：

1. `run()` 调用 `analyze()` 进入主循环
2. `process_messages()` 从 DAQ 获取数据包
3. `process_daq_pkt_msg()` 处理单个数据包
4. `post_process_packet()` 后处理（包括包重组）
5. `finalize_daq_message()` 发送处置结果

### 3.3 Inspector 类 (src/framework/inspector.h) {#_3-3-inspector-类-src-framework-inspector-h}

**职责**：所有检查器的基类，是 Snort 3 的核心工作组件

**类型枚举**：

```cpp
enum InspectorType {
    IT_PASSIVE,   // 仅配置，或数据消费者（file_log, binder）
    IT_PACKET,    // 仅处理原始包（normalize, capture）
    IT_STREAM,    // 流跟踪和重组（ip, tcp, udp）
    IT_NETWORK,   // 处理无服务的包（arp, bo）
    IT_SERVICE,   // 提取和分析服务PDU（dce, http, ssl）
    IT_CONTROL,   // 检测前处理所有包（appid）
    IT_PROBE,     // 检测后处理所有包（perf_monitor, port_scan）
    IT_PROBE_FIRST // 检测前处理所有包（packet_capture）
};
```

**关键虚函数**：

```cpp
class Inspector {
    virtual ~Inspector();
    
    // 配置阶段
    virtual bool configure(SnortConfig*);     // 配置检查器
    virtual void tear_down(SnortConfig*, bool); // 清理
    
    // 线程初始化
    virtual void tinit();    // 分配线程局部数据
    virtual void tterm();    // 清理
    
    // 包处理
    virtual bool likes(Packet*);   // 筛选包
    virtual void eval(Packet*);    // 处理包
    virtual void clear(Packet*);   // 清理流数据
    
    // 数据获取
    virtual bool get_buf(InspectionBuffer::Type, Packet*, InspectionBuffer&);
    virtual bool get_buf(const char* key, Packet*, InspectionBuffer&);
    
    // 服务检测
    virtual class StreamSplitter* get_splitter(bool to_server);
};
```

### 3.4 Codec 类 (src/framework/codec.h) {#_3-4-codec-类-src-framework-codec-h}

**职责**：协议编解码，将原始字节流转换为协议数据结构

**关键结构**：

```cpp
class Codec {
    // 编解码接口
    virtual bool decode(const RawData&, CodecData&, DecodeData&) = 0;
    virtual bool encode(const uint8_t* raw_in, const uint16_t raw_len,
                       EncState&, Buffer&, Flow*) = 0;
    virtual void update(const ip::IpApi&, EncodeFlags, uint8_t* raw_pkt,
                       uint16_t lyr_len, uint32_t& updated_len);
    
    // 日志
    virtual void log(TextLog* const, const uint8_t* raw_pkt, 
                     const uint16_t lyr_len);
};
```

**RawData 结构**：

```cpp
struct RawData {
    const struct _daq_msg* daq_msg;  // DAQ消息
    const uint8_t* data;              // 原始数据
    uint32_t len;                     // 数据长度
};
```

**CodecData 结构**：

```cpp
struct CodecData {
    const SnortConfig* conf;
    ProtocolId next_prot_id;         // 下一层协议ID
    uint16_t lyr_len = 0;            // 当前层有效长度
    uint16_t invalid_bytes = 0;       // 无效字节数
    uint32_t proto_bits = 0;         // 协议标识
    uint16_t codec_flags = 0;        // 编解码标志
    uint8_t ip_layer_cnt = 0;        // IP层计数
    // ...
};
```

### 3.5 Module 类 (src/framework/module.h) {#_3-5-module-类-src-framework-module-h}

**职责**：配置管理模块，每个检查器对应一个模块用于参数配置

**关键结构**：

```cpp
class Module {
    // 配置接口
    virtual bool begin(const char*, int, SnortConfig*);  // 开始列表/表
    virtual bool end(const char*, int, SnortConfig*);    // 结束列表/表
    virtual bool set(const char*, Value&, SnortConfig*); // 设置参数
    
    // 统计信息
    virtual PegCount* get_counts() const;               // 获取计数
    virtual ProfileStats* get_profile() const;           // 获取性能统计
    
    // 规则信息
    virtual const RuleMap* get_rules() const;             // 获取规则映射
    virtual const PegInfo* get_pegs() const;             // 获取计数信息
};
```

---

## 数据包处理流程 {#数据包处理流程}

### 4.1 完整数据包处理流程 {#_4-1-完整数据包处理流程}

```
┌──────────────────────────────────────────────────────────────────┐
│                        DAQ (Data AcQuisition)                    │
│              获取原始数据包 (pcap, afpacket, etc.)                │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Analyzer::analyze()                       │
│                     主数据包处理循环                               │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                     SFDAQInstance::acquire()                      │
│                        获取下一个数据包                             │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                    PacketManager::process()                       │
│                    协议解码和包管理                                │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
                    ┌─────────────────────────────────┐
                    │      Codec::decode() 循环       │
                    │   (Ethernet → IP → TCP/UDP ...) │
                    └─────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                      InspectorManager::execute()                  │
│                      检查器执行                                    │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              IT_PROBE_FIRST (e.g., packet_capture)               │
│                  检测前探针处理                                   │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              IT_CONTROL (e.g., appid)                            │
│                    控制通道处理                                   │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              IT_STREAM (tcp, ip, udp)                            │
│                    流重组和跟踪                                   │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              IT_NETWORK (arp, bo)                                │
│                   网络层处理                                      │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              IT_SERVICE (http, dns, ssl)                         │
│                   服务检测和处理                                  │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                 DetectionEngine::detect()                        │
│                      规则检测                                     │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              IT_PROBE (perf_monitor, port_scan)                  │
│                   检测后探针处理                                  │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                       动作执行                                    │
│              (alert, log, drop, reject, etc.)                    │
└─────────────────────────────────┬────────────────────────────────┘
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                       DAQ Verdict                                │
│                  (PACKET, DROP, IGNORE, etc.)                    │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 协议解码流程 {#_4-2-协议解码流程}

```
Raw Packet Bytes
       │
       ▼
┌──────────────────┐
│   Ethernet Codec │
│  (DLT_EN10MB)    │
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│    VLAN Codec    │  (optional)
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│    MPLS Codec    │  (optional)
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│   IPv4/IPv6 Codec │
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│  IP Options Codec │  (optional)
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│    TCP/UDP Codec  │
└────────┬─────────┘
         │ Decode
         ▼
┌──────────────────┐
│   Application    │
│   Protocol Codec │
│ (HTTP, DNS, ...) │
└──────────────────┘
```

---

## 插件系统 {#插件系统}

### 5.1 插件类型 {#_5-1-插件类型}

Snort 3 采用插件化架构，支持以下插件类型：

| 插件类型 | 基类 | 描述 | API版本 |
|---------|------|------|--------|
| Inspector | `Inspector` | 检查器插件 | `INSAPI_VERSION` |
| Codec | `Codec` | 协议编解码器 | `CDAPI_VERSION` |
| Logger | `Logger` | 日志输出 | `LOGAPI_VERSION` |
| IpsOption | `IpsOption` | IPS规则选项 | `IPSAPI_VERSION` |
| Action | `IpsAction` | 响应动作 | `ACTAPI_VERSION` |
| Mpse | `Mpse` | 模式搜索引擎 | `SEAPI_VERSION` |
| Connector | `Connector` | 连接器 | `CONNAPI_VERSION` |

### 5.2 插件API结构 {#_5-2-插件api结构}

```cpp
// Inspector API (framework/inspector.h)
struct InspectApi {
    BaseApi base;                    // 基础API（名称、类型等）
    InspectorType type;              // 检查器类型
    uint32_t proto_bits;             // 协议标识
    
    const char** buffers;            // 导出缓冲区列表
    const char* service;             // 服务名称
    
    InspectFunc pinit;               // 插件初始化
    InspectFunc pterm;               // 插件清理
    InspectFunc tinit;               // 线程初始化
    InspectFunc tterm;               // 线程清理
    InspectNew ctor;                 // 创建检查器实例
    InspectDelFunc dtor;             // 销毁检查器实例
    InspectSsnFunc ssn;              // 获取会话跟踪器
    InspectFunc reset;              // 重置统计
};

// Codec API (framework/codec.h)
struct CodecApi {
    BaseApi base;
    
    CdAuxFunc pinit;                 // 插件初始化
    CdAuxFunc pterm;                 // 插件清理
    CdAuxFunc tinit;                 // 线程初始化
    CdAuxFunc tterm;                 // 线程清理
    
    CdNewFunc ctor;                  // 创建解码器实例
    CdDelFunc dtor;                  // 销毁解码器实例
};

// Mpse API (framework/mpse.h)
struct MpseApi {
    BaseApi base;
    
    void (*pinit)();                 // 插件初始化
    void (*pterm)();                // 插件清理
    void (*tinit)();                // 线程初始化
    void (*tterm)();               // 线程清理
    
    Mpse* (*ctor)(SnortConfig*);    // 创建搜索引擎实例
    void (*dtor)(Mpse*);            // 销毁实例
};
```

### 5.3 插件加载流程 {#_5-3-插件加载流程}

```
Snort::setup()
    │
    ▼
PluginManager::load_plugins()
    │
    ├── 加载静态插件
    └── 加载动态插件 (.so 文件)
    │
    ▼
ModuleManager::load_modules()
    │
    ▼
InspectorManager::new_map()
    │
    ▼
配置解析 (snort.lua)
    │
    ▼
Module::begin()/set()/end()  配置每个模块
    │
    ▼
InspectorManager::configure()  配置每个检查器
    │
    ▼
InspectorManager::prepare_inspectors()  准备检查器
```

---

## 检测系统 {#检测系统}

### 6.1 DetectionEngine (src/detection/detection_engine.h) {#_6-1-detectionengine-src-detection-detection-engine-h}

**职责**：管理检测上下文，执行规则匹配

**关键结构**：

```cpp
class DetectionEngine {
public:
    static void init();                      // 初始化
    static void thread_init();                // 线程初始化
    static void thread_term();                // 线程清理
    
    static Packet* set_next_packet(const Packet* parent, Flow* flow);
    static uint8_t* get_next_buffer(unsigned& max);
    
    static void enable_offload();            // 启用卸载
    static bool offload(Packet*);            // 卸载检测
    static void onload(Flow*);               // 加载结果
    
    static bool detect(Packet*, bool offload_ok = false);
    static bool inspect(Packet*);
    
    static int queue_event(const OptTreeNode*);
    static int queue_event(unsigned gid, unsigned sid);
    
    static void set_data(unsigned id, IpsContextData*);
    static IpsContextData* get_data(unsigned id);
};
```

### 6.2 规则匹配流程 {#_6-2-规则匹配流程}

```
DetectionEngine::detect()
    │
    ├── 准备检测上下文 (IpsContext)
    │
    ├── 应用预处理选项 (preprocessors)
    │
    ├── 快速模式匹配 (Fast Pattern Matcher)
    │   └── 使用 MPSE (AC, BNFA, Hyperscan)
    │
    ├── 对每个匹配的模式:
    │   ├── 评估规则选项
    │   └── 检查否定匹配
    │
    ├── 规则动作评估
    │   ├── alert: 生成告警
    │   ├── drop: 丢弃并告警
    │   ├── reject: 拒绝连接
    │   ├── log: 仅记录
    │   └── pass: 跳过
    │
    └── 事件排队 (Event Queue)
```

### 6.3 IpsContext (src/detection/ips_context.h) {#_6-3-ipscontext-src-detection-ips-context-h}

**职责**：保存检测上下文，包含检测所需的所有状态

```cpp
class IpsContext {
public:
    struct ActiveRules {
        // 活动的规则状态
    };
    
    void set_data(unsigned id, IpsContextData*);
    IpsContextData* get_data(unsigned id);
    
    // 替代缓冲区管理
    void set_file_data(const DataPointer&);
    const DataPointer& get_file_data() const;
    
    // 替换内容
    void add_replacement(const std::string&, unsigned);
    bool get_replacement(std::string&, unsigned&);
};
```

### 6.4 搜索引擎 (src/search_engines/) {#_6-4-搜索引擎-src-search-engines}

Snort 3 支持多种模式匹配算法：

| 搜索引擎 | 文件 | 描述 |
|---------|------|------|
| AC (Aho-Corasick) | `ac_full.cc` | AC自动机，全匹配模式 |
| AC-BNFA | `ac_bnfa.cc` | AC二元范式，非确定性自动机 |
| ACSMX2 | `acsmx2.cc` | AC多模式扩展 |
| Hyperscan | `hyperscan.cc` | Intel Hyperscan，支持复杂模式 |

**Mpse 类接口**：

```cpp
class Mpse {
    virtual int add_pattern(
        const uint8_t* pat, unsigned len, 
        const PatternDescriptor&, void* user) = 0;
    
    virtual int prep_patterns(SnortConfig*) = 0;
    
    virtual int search(
        const uint8_t* T, int n, MpseMatch, 
        void* context, int* current_state) = 0;
};
```

---

## 关键数据结构 {#关键数据结构}

### 7.1 Packet 结构 (src/main/packet.h) {#_7-1-packet-结构-src-main-packet-h}

**职责**：表示一个网络数据包，包含所有协议层信息

```cpp
struct Packet {
    const uint8_t* data;              // 原始数据包指针
    uint16_t dsize;                    // 数据大小
    
    // 协议层指针
    const ETHERHdr* ethh;             // Ethernet头
    const VLANHdr* vlanh;              // VLAN头
    const IP4Hdr* ip4h;               // IPv4头
    const IP6Hdr* ip6h;               // IPv6头
    const TCPHdr* tcph;               // TCP头
    const UDPHdr* udph;               // UDP头
    const ICMPHdr* icmph;             // ICMP头
    
    // 指针辅助函数
    const uint8_t* transport_data;    // 传输层数据
    const uint8_t* payload_data;      // 应用层数据
    
    // 流信息
    Flow* flow;                        // 关联的流
    FlowKey* flow_key;                // 流键
    
    // 上下文
    IpsContext* context;              // 检测上下文
    
    // 统计和标志
    uint16_t proto_bits;             // 协议标识
    uint8_t num_layers;              // 层数
    
    // 时间戳
    struct timeval ts;               // 时间戳
};
```

### 7.2 Flow 结构 (src/flow/flow.h) {#_7-2-flow-结构-src-flow-flow-h}

**职责**：表示一个网络会话，跟踪所有相关状态

```cpp
class Flow {
public:
    // 流键（5元组）
    FlowKey* key;                    // 源/目的IP，端口，协议
    
    // 协议状态
    uint32_t state;                  // 流状态
    uint32_t flags;                  // 流标志
    
    // 统计
    FlowStats stats;                 // 字节/包计数
    
    // 流数据列表
    std::list<FlowData*> flow_data;  // FlowData列表
    
    // 会话跟踪器
    Session* session;                // 会话对象
    
    // 流重组
    uint8_t* reassembled_data;       // 重组数据
    unsigned reassembled_len;        // 重组长度
    
    // 高可用性
    FlowHAState* ha_state;           // HA状态
    
    // 方法
    void set_state(unsigned);        // 设置状态
    void update_stats(uint64_t, uint64_t);  // 更新统计
    void add_flow_data(FlowData*);   // 添加流数据
    FlowData* get_flow_data(unsigned id);  // 获取流数据
};
```

**流状态标志**：

```cpp
#define SSNFLAG_SEEN_CLIENT         0x00000001
#define SSNFLAG_SEEN_SERVER         0x00000002
#define SSNFLAG_ESTABLISHED        0x00000004
#define SSNFLAG_MIDSTREAM          0x00000008
#define SSNFLAG_ECN_CLIENT_QUERY   0x00000010
#define SSNFLAG_CLIENT_FIN         0x00000040
#define SSNFLAG_SERVER_FIN         0x00000080
#define SSNFLAG_TIMEDOUT           0x00001000
#define SSNFLAG_RESET              0x00004000
#define SSNFLAG_DROP_CLIENT        0x00010000
#define SSNFLAG_DROP_SERVER        0x00020000
```

### 7.3 FlowData 结构 (src/flow/flow_data.h) {#_7-3-flowdata-结构-src-flow-flow-data-h}

**职责**：存储与特定流关联的检查器数据

```cpp
class FlowData {
public:
    FlowData(unsigned id, void* data) 
        : id(id), data(data) {}
    
    unsigned get_id() const { return id; }
    void* get_data() const { return data; }
    
private:
    unsigned id;                     // 数据ID（对应检查器）
    void* data;                      // 实际数据
};
```

### 7.4 InspectionBuffer 结构 (src/framework/inspector.h) {#_7-4-inspectionbuffer-结构-src-framework-inspector-h}

**职责**：在规则评估期间传递检测缓冲区

```cpp
struct InspectionBuffer {
    enum Type {
        IBT_VBA,                    // VBA脚本数据
        IBT_JS_DATA,                // JavaScript数据
        IBT_KEY,                    // 密钥
        IBT_HEADER,                  // 头部
        IBT_BODY,                   // 主体
        IBT_MAX
    };
    
    const uint8_t* data;            // 缓冲区数据
    unsigned len;                    // 数据长度
    bool is_accumulated = false;     // 是否累积数据
};
```

---

## 模块详解 {#模块详解}

### 8.1 InspectorManager (src/managers/inspector_manager.h) {#_8-1-inspectormanager-src-managers-inspector-manager-h}

**职责**：管理所有检查器的创建、配置和执行

**关键函数**：

```cpp
class InspectorManager {
    // 创建和销毁
    static void new_map();           // 创建新检查器映射
    static void clear();              // 清空所有检查器
    static void tear_down(SnortConfig*);  // 清理指定配置
    
    // 配置
    static bool configure(SnortConfig*);  // 配置所有检查器
    static void prepare_inspectors(SnortConfig*);  // 准备检查器
    
    // 执行
    static void execute(Packet*);     // 执行主检查流程
    static void probe(Packet*);      // 执行IT_PROBE类型
    static void probe_first(Packet*); // 执行IT_PROBE_FIRST类型
    
    // 获取检查器
    static Inspector* get_inspector(const char* key, Module::Usage);
    static Inspector* get_service_inspector(const SnortProtocolId);
    static Inspector* get_binder();  // 获取绑定器
};
```

### 8.2 ModuleManager (src/managers/module_manager.h) {#_8-2-modulemanager-src-managers-module-manager-h}

**职责**：管理所有模块的加载和配置

**关键函数**：

```cpp
class ModuleManager {
    static void load_modules();      // 加载所有模块
    static void unload_modules();     // 卸载所有模块
    
    static Module* get_module(const char*);  // 获取模块
    static void add_module(Module*); // 添加模块
    
    static bool configure(SnortConfig*, lua_State*);  // 配置
};
```

### 8.3 PluginManager (src/managers/plugin_manager.h) {#_8-3-pluginmanager-src-managers-plugin-manager-h}

**职责**：管理插件的加载和访问

```cpp
class PluginManager {
    static void load_plugins();       // 加载所有插件
    static void unload_plugins();      // 卸载所有插件
    
    // 获取插件
    static void* get_plugin(unsigned type, const char* name);
    static void* get_first_plugin(unsigned type);
    
    // 注册插件
    static void add_plugin(Plugin*);
    static void remove_plugin(Plugin*);
};
```

### 8.4 Stream 模块 (src/stream/) {#_8-4-stream-模块-src-stream}

**职责**：TCP流重组和状态跟踪

```
src/stream/
├── stream.cc/h              # 主Stream模块
├── stream_splitter.cc/h    # 流分割器
├── stream_udp.cc/h         # UDP流处理
├── stream_icmp.cc/h        # ICMP流处理
├── stream_ip.cc/h          # IP分片重组
└── tcp/
    ├── tcp_module.cc/h     # TCP模块
    ├── tcp_stream.cc/h     # TCP流跟踪
    ├── tcp_reassembly.cc/h # TCP重组
    └── tcp_norm.cc/h       # TCP规范化
```

**StreamSplitter 类**：

```cpp
class StreamSplitter {
public:
    virtual ~StreamSplitter();
    
    // 扫描输入数据，返回需要的数据字节数
    virtual Status scan(Flow*, const uint8_t* data, 
                       uint32_t len, uint32_t* consumed) = 0;
    
    // 准备重组
    virtual void reassemble(Flow*, uint64_t, const uint8_t*,
                           uint32_t, uint32_t, uint32_t);
    
    // 是否需要flush
    virtual bool finish(Flow*) { return true; }
};
```

### 8.5 网络检查器 (src/network_inspectors/) {#_8-5-网络检查器-src-network-inspectors}

```
src/network_inspectors/
├── arp/                    # ARP检查器
├── bo/                     # Back Orifice检查器
├── classified/            # 分类引擎
├── dce/                    # DCE/RPC检查器
├── dns/                    # DNS检查器
├── file_id/               # 文件识别
├── ftp/                    # FTP检查器
├── gtp/                    # GTP检查器
├── http2_inspect/          # HTTP2检查器
├── http_inspect/           # HTTP检查器
├── icmp/                   # ICMP检查器
├── imap/                   # IMAP检查器
├── ip/                     # IP检查器
├── mms/                    # MMS检查器
├── modbus/                 # Modbus检查器
├── netflow/                # NetFlow检查器
├── normalize/              # 规范化
├── pdf_norm/               # PDF规范化
├── pop/                    # POP检查器
├── port_scan/              # 端口扫描检测
├── pptp/                   # PPTP检查器
├── radius/                 # RADIUS检查器
├── reprec/                 # 信誉度
├── rna/                    # RNA (反应式网络应用)
├── rpc_decode/             # RPC解码
├── sdf/                    # 敏感数据过滤
├── sip/                    # SIP检查器
├── smtp/                   # SMTP检查器
├── snort/                  # 主检查器
├── ssh/                    # SSH检查器
├── ssl/                    # SSL/TLS检查器
├── sunrpc/                 # SunRPC检查器
├── tftp/                   # TFTP检查器
└── wizard/                 # 服务向导
```

### 8.6 发布-订阅框架 (src/framework/data_bus.h) {#_8-6-发布-订阅框架-src-framework-data-bus-h}

**职责**：组件间松耦合通信

```cpp
class DataBus {
    // 发布者注册
    static unsigned get_id(const PubKey&);
    
    // 订阅
    static void subscribe(const PubKey&, unsigned id, DataHandler*);
    static void subscribe_network(const PubKey&, unsigned id, DataHandler*);
    static void subscribe_global(const PubKey&, unsigned id, DataHandler*, SnortConfig&);
    
    // 发布
    static void publish(unsigned pub_id, unsigned evt_id, 
                       DataEvent&, Flow* = nullptr);
    static void publish(unsigned pub_id, unsigned evt_id, 
                       const uint8_t*, unsigned, Flow* = nullptr);
    static void publish(unsigned pub_id, unsigned evt_id, 
                       Packet*, Flow* = nullptr);
};
```

**PubKey 结构**：

```cpp
struct PubKey {
    const char* publisher;           // 发布者名称
    unsigned num_events;             // 事件数量
};
```

### 8.7 IPS选项 (src/ips_options/) {#_8-7-ips选项-src-ips-options}

IPS选项是规则中可用的匹配条件，包括：

```
src/ips_options/
├── ips_content.cc/h       # content选项（模式匹配）
├── ips_pcre.cc/h         # pcre选项（正则表达式）
├── ips_byte_test.cc/h    # byte_test选项
├── ips_byte_jump.cc/h    # byte_jump选项
├── ips_flow.cc/h         # flow选项
├── ips_flowbits.cc/h     # flowbits选项
├── ips_seq.cc/h          # seq选项
├── ips_ack.cc/h          # ack选项
├── ips_window.cc/h       # window选项
├── ips_icmp_id.cc/h      # icmp_id选项
├── ips_icmp_seq.cc/h     # icmp_seq选项
├── ips_ip_id.cc/h        # ip_id选项
├── ips_ip_option.cc/h    # ip_option选项
├── ips_dsize.cc/h        # dsize选项
├── ips_flags.cc/h        # flags选项
├── ips_itype.cc/h        # itype选项
├── ips_icode.cc/h        # icode选项
├── ips_ttl.cc/h          # ttl选项
├── ips_tos.cc/h          // tos选项
├── ips_proto.cc/h        // proto选项
├── ips_same.cc/h         // sameip选项
├── ips_ip_proto.cc/h     // ip_proto选项
├── ips_regex.cc/h        // regex选项
├── ips_base64.cc/h       // base64_decode选项
├── ips_base64_data.cc/h  // base64_data选项
├── ips_paf.cc/h          // paf高校选项
```

---
