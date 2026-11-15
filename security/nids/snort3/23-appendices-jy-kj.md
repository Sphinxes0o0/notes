---
title: "Snort 3 · 附录 JY–KJ"
description: "附录JY： 日志系统 — 附录KJ： 其他重要模块"
---

# Snort 3 · 附录 JY–KJ

[返回总目录](../snort3_architecture_analysis)

## 附录JY： 日志系统 {#附录jy-日志系统}

### JY.1 AlertLog {#jy-1-alertlog}

```cpp
// loggers/alert_log.h

class AlertLog {
public:
    AlertLog();
    ~AlertLog();
    
    // 打开/关闭
    bool open(const char* dir, const char* base);
    void close();
    
    // 记录
    void log(Packet*, const char* message, const Event*);
    
    // 刷新
    void flush();
    
    // 文件描述符
    int get_fd() const { return fd_; }
    
private:
    char filename_[256];
    int fd_ = -1;
    FILE* file_ = nullptr;
};

// 快速日志
class AlertFast {
public:
    AlertFast();
    void log(Packet*, const Event*);
    
    void open(const char* file);
    void close();
    
private:
    FILE* file_;
    std::mutex mutex_;
};
```

---

## 附录JZ： 过滤器 {#附录jz-过滤器}

### JZ.1 RateFilter {#jz-1-ratefilter}

```cpp
// filters/rate_filter.h

class RateFilter {
public:
    // 应用速率限制
    void apply(Packet*, IpsAction::Type, uint32_t, uint32_t);
    
    // 检查是否限制
    bool is_filtered(uint32_t, uint32_t) const;
    
    // 配置
    void set_rate(uint32_t r) { rate_ = r; }
    void set_timeout(uint32_t t) { timeout_ = t; }
    
    enum class RateType : uint8_t {
        ABSOLUTE,   // 绝对
        THRESHOLD,  // 阈值
        BOTH,       // 两者
        NOTSYNC     // 不同步
    };
    
    enum class Track : uint8_t {
        BY_SRC,    // 按源
        BY_DST,    // 按目标
        BY_RULE    // 按规则
    };
    
private:
    RateType type_ = RateType::THRESHOLD;
    Track track_ = Track::BY_SRC;
    uint32_t rate_ = 0;
    uint32_t timeout_ = 0;
    uint32_t count_ = 0;
    time_t first_ = 0;
};
```

---

## 附录KA： 整理完成 {#附录ka-整理完成}

### KA.1 文档索引 {#ka-1-文档索引}

```
本Snort 3源码架构分析文档包含以下章节:

第一部分: 架构概述
├── 1. 概述和特性
├── 2. 整体架构
└── 3. 核心组件

第二部分: 核心数据结构
├── 4. Packet结构
├── 5. Flow结构
└── 6. 检测相关结构

第三部分: 模块详解
├── 7. Inspector系统
├── 8. Manager系统
└── 9. 各类型Inspector

第四部分: 附录 (A-Z, AA-KA)
├── A-E: 基础架构
├── F-I: Binder, Wizard, MPSE, PubSub
├── J-N: 配置, DAQ, 流分割器, 文件处理
├── O-Q: 主循环, 内存, 多线程
├── R-Z: 高可用, 调试, 规则编译
├── AA-AM: Actions, Latency, 协议检测器
├── AN-GZ: 过滤器, 测试, 工具类
├── HA-JZ: 类图, 设计模式, 运维
└── KA: 文档索引
```

---

*文档最终版本: 18.0*
*最终更新: 2026年4月10日*
*总行数: 19500+*

*本文档全面分析了Snort 3的源码架构，涵盖核心框架、协议处理、检测机制、配置系统和扩展接口等全部关键内容，深入到函数和结构体级别。*


---

## 附录KB： 源文件组织 {#附录kb-源文件组织}

### KB.1 完整目录结构 {#kb-1-完整目录结构}

```
src/
├── main/                    # 主程序入口
│   ├── main.cc             # main()函数
│   ├── snort.cc            # Snort类实现
│   ├── snort.h             # Snort类定义
│   ├── pig.cc              # Pig数据包处理协调
│   ├── pig.h
│   ├── analyzer.cc         # Analyzer类
│   ├── analyzer.h
│   ├── thread.cc          # 线程管理
│   └── thread.h
│
├── framework/              # 核心框架
│   ├── inspector.h          # Inspector基类
│   ├── inspector.cc
│   ├── codec.h            # Codec基类
│   ├── codec.cc
│   ├── module.h           # Module基类
│   ├── module.cc
│   ├── cursor.h           # Cursor光标
│   ├── cursor.cc
│   ├── data_buffer.h     # DataBuffer
│   ├── decode_data.h      # 解码数据
│   ├── ips_context.h      # 检测上下文
│   ├── ips_option.h       # IPS选项基类
│   ├── ips_manager.cc     # IPS管理器
│   ├── plugin.h           # 插件接口
│   └── pub_sub.h          # 发布订阅
│
├── detection/              # 检测引擎
│   ├── detection_engine.cc # 检测引擎
│   ├── detection_engine.h
│   ├── fp_detect.cc       # 快速模式检测
│   ├── fp_detect.h
│   ├── treenorm.h         # 规则树
│   ├── rule_compile.cc    # 规则编译
│   ├── rule_parser.y      # 规则语法分析(Bison)
│   ├── event_queue.cc     # 事件队列
│   ├── event_queue.h
│   ├── ips_context.cc      # 检测上下文实现
│   └── ...
│
├── ips_options/            # IPS规则选项
│   ├── ips_option.h
│   ├── content.cc         # content选项
│   ├── content.h
│   ├── pcre.cc           # pcre选项
│   ├── pcre.h
│   ├── flow.cc           # flow选项
│   ├── flow.h
│   ├── http_buffer.cc    # http_buffer选项
│   └── ...
│
├── codecs/                  # 协议编解码器
│   ├── codec.cc
│   ├── codec.h
│   ├── eth/              # 以太网
│   │   ├── eth_codec.cc
│   │   └── eth_codec.h
│   ├── ip/               # IP
│   │   ├── ip4_codec.cc
│   │   ├── ip4_codec.h
│   │   ├── ip6_codec.cc
│   │   └── ip6_codec.h
│   ├── tcp/              # TCP
│   │   ├── tcp_codec.cc
│   │   └── tcp_codec.h
│   ├── udp/              # UDP
│   └── icmp/             # ICMP
│
├── service_inspectors/     # 服务检查器
│   ├── http_inspect/      # HTTP
│   │   ├── http_enum.h   # HTTP枚举
│   │   ├── http_field.h  # 字段
│   │   ├── http_module.cc
│   │   ├── http_parm.h
│   │   ├── http_parse.cc
│   │   ├── http_parse.h
│   │   ├── http_profiler.cc
│   │   ├── http_profiler.h
│   │   ├── http_split.cc
│   │   ├── http_split.h
│   │   ├── http_table.h
│   │   ├── http_util.cc
│   │   ├── http_util.h
│   │   └── http_ips.cc
│   ├── smtp/             # SMTP
│   ├── dns/              # DNS
│   ├── ftp/              # FTP
│   ├── ssh/              # SSH
│   ├── ssl/              # SSL/TLS
│   ├── sip/              # SIP
│   └── ...
│
├── network_inspectors/     # 网络检查器
│   ├── binder/           # 服务绑定
│   │   ├── binder.cc
│   │   ├── binder.h
│   │   ├── binder_ips.cc
│   │   ├── binder_inspect.cc
│   │   ├── binder_module.cc
│   │   └── binder_module.h
│   ├── wizard/           # 自动服务检测
│   │   ├── wizard.cc
│   │   ├── wizard.h
│   │   ├── wizard_module.cc
│   │   ├── curse_book.cc
│   │   ├── curse_book.h
│   │   ├── magic_book.cc
│   │   ├── magic_book.h
│   │   ├── curse.cc
│   │   └── curse.h
│   ├── arp/              # ARP
│   ├── icmp/             # ICMP
│   └── ...
│
├── stream/                 # 流处理
│   ├── stream.cc
│   ├── stream.h
│   ├── stream_splitter.h
│   ├── stream_buffer.h
│   ├── tcp/               # TCP流
│   │   ├── tcp_stream_session.cc
│   │   ├── tcp_stream_session.h
│   │   ├── tcp_stream_tracker.cc
│   │   ├── tcp_stream_tracker.h
│   │   ├── tcp_reassembler.cc
│   │   ├── tcp_reassembler.h
│   │   ├── tcp_segment_node.h
│   │   ├── tcp_normalizers.cc
│   │   ├── tcp_normalizers.h
│   │   ├── tcp_state_machine.cc
│   │   ├── tcp_state_machine.h
│   │   ├── tcp_module.cc
│   │   └── tcp_module.h
│   └── udp/               # UDP流
│
├── flow/                   # 流管理
│   ├── flow.cc
│   ├── flow.h
│   ├── flow_key.cc
│   ├── flow_key.h
│   ├── flow_cache.cc
│   ├── flow_cache.h
│   ├── session.cc
│   ├── session.h
│   ├── session_manager.cc
│   └── session_manager.h
│
├── managers/               # 管理器
│   ├── inspector_manager.cc
│   ├── inspector_manager.h
│   ├── module_manager.cc
│   ├── module_manager.h
│   ├── plugin_manager.cc
│   └── plugin_manager.h
│
├── packet_io/             # 数据包I/O
│   ├── sfdaq.cc
│   ├── sfdaq.h
│   ├── daq.cc
│   ├── daq.h
│   └── ...
│
├── loggers/               # 日志输出
│   ├── alert_csv.cc
│   ├── alert_fast.cc
│   ├── alert_full.cc
│   ├── log_codec.cc
│   └── ...
│
├── actions/               # 响应动作
│   ├── ips_action.cc
│   ├── ips_action.h
│   ├── active_action.cc
│   └── ...
│
├── pub_sub/              # 发布订阅
│   ├── data_bus.cc
│   ├── data_bus.h
│   ├── event_handler.h
│   └── ...
│
├── memory/               # 内存管理
│   ├── memory.cc
│   ├── memory_cap.cc
│   ├── memory_pool.cc
│   └── ...
│
├── utils/                # 工具函数
│   ├── string_util.cc
│   ├── string_util.h
│   ├── ip_util.cc
│   ├── ip_util.h
│   ├── malloc.cc
│   └── ...
│
├── time/                 # 时间处理
│   ├── stopwatch.cc
│   └── stopwatch.h
│
├── profiler/             # 性能分析
│   ├── profiler.cc
│   ├── profiler.h
│   └── ...
│
├── filters/              # 过滤器
│   ├── rate_filter.cc
│   └── ...
│
└── protocols/            # 协议定义
    ├── packet.h
    ├── eth.h
    ├── vlan.h
    ├── mpls.h
    ├── ip.h
    ├── ipv6.h
    ├── tcp.h
    ├── udp.h
    ├── icmp.h
    └── ...
```

---

## 附录KC： 头文件依赖关系 {#附录kc-头文件依赖关系}

### KC.1 核心依赖图 {#kc-1-核心依赖图}

```
                    ┌──────────────┐
                    │   packet.h   │
                    └──────┬───────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │   flow.h  │   │   Flow    │   │  Decode   │
    │           │   │  Session  │   │   Data    │
    └─────┬─────┘   └─────┬─────┘   └───────────┘
          │                 │
          │          ┌──────┴──────┐
          │          │             │
          ▼          ▼             ▼
    ┌─────────────────────────────┐
    │      Inspector (framework)    │
    └──────────┬──────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐
│Stream │ │Service│ │Network│
│Inspector│Inspector│Inspector│
└───┬───┘ └───┬───┘ └───┬───┘
    │         │         │
    └─────────┼─────────┘
              │
              ▼
    ┌─────────────────┐
    │ DetectionEngine │
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐     ┌─────────┐
│  MPSE   │     │IpsOption│
│(AC/Hyperscan)│   │  Tree   │
└─────────┘     └─────────┘
```

---

## 附录KD： 编译系统 {#附录kd-编译系统}

### KD.1 CMakeLists结构 {#kd-1-cmakelists结构}

```cmake
# 主CMakeLists.txt
cmake_minimum_required(VERSION 3.10)
project(Snort3)

# 检测系统
enable_language(C CXX ASM)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找依赖
find_package(Threads REQUIRED)
find_package(DAQ REQUIRED)

# 编译选项
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

# 子目录
add_subdirectory(src/framework)
add_subdirectory(src/codecs)
add_subdirectory(src/detection)
add_subdirectory(src/stream)
add_subdirectory(src/service_inspectors)
add_subdirectory(src/network_inspectors)
add_subdirectory(src/managers)
add_subdirectory(src/loggers)
add_subdirectory(src/actions)

# 可执行文件
add_executable(snort 
    src/main/main.cc
    src/main/snort.cc
    src/main/pig.cc
    src/main/analyzer.cc
)

target_link_libraries(snort 
    framework
    detection
    ips_options
    codecs
    stream
    managers
    ${DAQ_LIBRARIES}
    Threads::Threads
)
```

---

## 附录KE： 宏定义参考 {#附录ke-宏定义参考}

### KE.1 常用宏 {#ke-1-常用宏}

```cpp
// 通用宏
#define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define ALIGN(x, a) (((x) + ((a) - 1)) & ~((a) - 1))

// 线程本地存储
#define THREAD_LOCAL __thread

// 编译期检查
#define STATIC_ASSERT(x) static_assert((x), #x)

// 装饰器
#define UNUSED(x) (void)(x)
#define LIKELY(x) __builtin_expect(!!(x), 1)
#define UNLIKELY(x) __builtin_expect(!!(x), 0)

// 字节序
#define SWAP_BYTES_16(x) ((uint16_t)(((x) & 0x00FF) << 8) | ((x) & 0xFF00) >> 8))
#define NTOHS(x) ntohs(x)
#define HTONS(x) htons(x)
#define HTONL(x) htonl(x)

// 协议位操作
#define SET_PROTO_BIT(bits, bit) ((bits) |= (bit))
#define CLEAR_PROTO_BIT(bits, bit) ((bits) &= ~(bit))
#define IS_PROTO_SET(bits, bit) (((bits) & (bit)) != 0)

// 调试
#define DEBUGMSG(fmt, ...) fprintf(stderr, fmt, ##__VA_ARGS__)
```

---

## 附录KF： 常量定义 {#附录kf-常量定义}

### KF.1 协议常量 {#kf-1-协议常量}

```cpp
// 协议号
enum IpProtocol : uint8_t {
    IP_PROTO_ICMP = 1,
    IP_PROTO_TCP = 6,
    IP_PROTO_UDP = 17,
    IP_PROTO_ICMPV6 = 58,
    IP_PROTO_GRE = 47,
    IP_PROTO_ESP = 50,
    IP_PROTO_AH = 51,
    IP_PROTO_OSPF = 89,
    IP_PROTO_PIM = 103,
    IP_PROTO_SCTP = 132
};

// 端口号
enum {
    PORT_HTTP = 80,
    PORT_HTTPS = 443,
    PORT_SMTP = 25,
    PORT_DNS = 53,
    PORT_SSH = 22,
    PORT_FTP = 21,
    PORT_TELNET = 23,
    PORT_SNMP = 161,
    PORT_SYSLOG = 514
};

// 以太网类型
enum EtherType : uint16_t {
    ETHERTYPE_IP = 0x0800,
    ETHERTYPE_IPV6 = 0x86DD,
    ETHERTYPE_ARP = 0x0806,
    ETHERTYPE_VLAN = 0x8100,
    ETHERTYPE_MPLS = 0x8847,
    ETHERTYPE_PPPOE = 0x8864
};
```

### KF.2 检测常量 {#kf-2-检测常量}

```cpp
// 默认配置值
enum {
    DEFAULT_MAX_SESSIONS = 262144,
    DEFAULT_SESSION_TIMEOUT = 30,
    DEFAULT_STREAM_MEMCAP = 1073741824,  // 1GB
    DEFAULT_FLOW_MEMCAP = 536870912,     // 512MB
    DEFAULT_MAX_PATTERN_LEN = 1024,
    DEFAULT_MAX_QUEUE_EVENTS = 5,
    DEFAULT_MAX_ATTRIBUTE_HOSTS = 10000
};

// 流跟踪状态
enum FlowState {
    FLOW_STATE_OPEN = 0,
    FLOW_STATE_OPENING,
    FLOW_STATE_ESTABLISHED,
    FLOW_STATE_CLOSING,
    FLOW_STATE_STATE_NONE
};

// TCP状态
enum TcpState {
    TCP_LISTEN,
    TCP_SYN_SENT,
    TCP_SYN_RECV,
    TCP_ESTABLISHED,
    TCP_MID_STREAM_SENT,
    TCP_MID_STREAM_RECV,
    TCP_FIN_WAIT1,
    TCP_FIN_WAIT2,
    TCP_CLOSE_WAIT,
    TCP_CLOSING,
    TCP_LAST_ACK,
    TCP_TIME_WAIT,
    TCP_CLOSED,
    TCP_STATE_NONE
};
```

---

## 附录KG： 错误码 {#附录kg-错误码}

### KG.1 错误定义 {#kg-1-错误定义}

```cpp
// 错误码
enum ErrorCode : int {
    SUCCESS = 0,
    FAILURE = -1,
    INVALID_ARG = -2,
    NULL_PTR = -3,
    OUT_OF_MEMORY = -4,
    BUFFER_TOO_SMALL = -5,
    
    // 配置错误
    CONFIG_ERROR = -100,
    CONFIG_NOT_FOUND = -101,
    CONFIG_INVALID = -102,
    
    // 协议错误
    DECODE_ERROR = -200,
    DECODE_INVALID = -201,
    DECODE_TRUNCATED = -202,
    
    // 检测错误
    DETECT_ERROR = -300,
    DETECT_TIMEOUT = -301,
    
    // 流错误
    STREAM_ERROR = -400,
    STREAM_INVALID_SEQ = -401,
    STREAM_TIMEOUT = -402
};

// 错误处理宏
#define RETURN_ERROR(code) do { error_code = (code); return false; } while(0)
#define CHECK_NULL(p) do { if (!(p)) RETURN_ERROR(NULL_PTR); } while(0)
```

---

## 附录KH： 完整API速查 {#附录kh-完整api速查}

### KH.1 核心类API {#kh-1-核心类api}

```cpp
// ==================
// Snort类API
// ==================
class Snort {
    static void setup(int argc, char* argv[]);
    static void cleanup();
    static SnortConfig* get_conf();
    static void set_conf(SnortConfig*);
    static const char* get_version();
};

// ==================
// Packet类API
// ==================
class Packet {
    void set(const DAQ_PktHdr_t*, const uint8_t*);
    EtherHdr* get_ether() const;
    IPHdr* get_ip() const;
    TCPHdr* get_tcp() const;
    UDPHdr* get_udp() const;
    bool is_tcp() const;
    bool is_udp() const;
    bool is_icmp() const;
};

// ==================
// Flow类API
// ==================
class Flow {
    void set_service(const char*);
    void set_application(AppId);
    Session* get_session() const;
    void set_session(Session*);
    bool process(Packet*);
    void clear();
};

// ==================
// Inspector类API
// ==================
class Inspector {
    virtual void eval(Packet*) = 0;
    virtual StreamSplitter* get_splitter(bool);
    virtual bool configure(SnortConfig*);
    virtual void show_stats();
    virtual void tinit();
    virtual void tterm();
};

// ==================
// StreamSplitter类API
// ==================
class StreamSplitter {
    virtual Status scan(Packet*, const uint8_t* data, uint32_t len,
                       uint32_t flags, uint32_t* fp) = 0;
    virtual bool is_paf() const;
    bool to_server() const;
    bool to_client() const;
};

// ==================
// DetectionEngine类API
// ==================
class DetectionEngine {
    static void begin(Packet*);
    static int detect(IpsPolicy*, Packet*);
    static void queue_event(uint32_t gid, uint32_t sid);
    static IpsContext* get_context();
};

// ==================
// Module类API
// ==================
class Module {
    virtual bool set(const char*, Value&, SnortConfig*) = 0;
    virtual bool begin(const char*, int, SnortConfig*) = 0;
    virtual bool end(const char*, int, SnortConfig*) = 0;
    virtual const Param* get_params() const = 0;
    const char* get_name() const;
    void* get_data() const;
};
```

---

## 附录KI： 版本信息 {#附录ki-版本信息}

### KI.1 版本常量 {#ki-1-版本常量}

```cpp
// 版本定义
#define SNORT_VERSION "3.5.0.0"
#define SNORT_VERSION_MAJOR 3
#define SNORT_VERSION_MINOR 5
#define SNORT_VERSION_PATCH 0
#define SNORT_VERSION_BUILD 0

#define SNORT_BUILD_DATE __DATE__
#define SNORT_BUILD_TIME __TIME__

// 特性标志
#define HAVE_HYPERSCAN 1
#define HAVE_LZMA 1
#define HAVE_LZMA_SHA 1
#define HAVE_DAQ 1
#define HAVE_DAQ_PCAP 1

// 协议版本
#define SUPPORTED_DAQ_VERSION 3
#define SUPPORTED_SNORT_IDS_API_VERSION 5
```

---

*附录完成 - 文档版本: 19.0*
*最终更新: 2026年4月10日*
*总行数: 20500+*

*本文档是Snort 3源码架构分析的最终版本，涵盖了系统的所有主要组件、数据结构、接口和实现细节。*


---

## 附录KJ： 其他重要模块 {#附录kj-其他重要模块}

### KJ.1 Host Tracker {#kj-1-host-tracker}

```cpp
// host_tracker/host_cache.h

// 主机追踪器 - 追踪主机的属性和状态
class HostCache {
public:
    // 查找主机
    Host* find(const SfIp* ip);
    
    // 添加主机
    void add(Host* host);
    
    // 移除主机
    void remove(const SfIp* ip);
    
    // 获取主机的应用协议信息
    AppId get_app_id(const SfIp* ip) const;
    
    // 获取主机情报
    const char* get_intel(const SfIp* ip) const;
};

// Host结构
struct Host {
    SfIp ip;                 // IP地址
    uint32_t last_seen;     // 最后见到的 时间
    uint16_t frag_count;     // 分片数量
    bool frag_flag;         // 分片标志
    
    // 服务信息
    std::map<uint16_t, ServiceInfo> services;
    
    // 应用ID
    AppId app_id;
    
    // 情报数据
    const char* intel;
};
```

### KJ.2 JS Normalization {#kj-2-js-normalization}

```cpp
// js_norm/js_norm.h

// JavaScript规范化 - 用于检测恶意JavaScript
class JsNorm {
public:
    // 规范化JavaScript
    void normalize(const uint8_t* data, unsigned len, 
                  uint8_t* out, unsigned* out_len);
    
    // 检测混淆
    bool detect_obfuscation(const uint8_t* data, unsigned len);
    
    // 解码字符串
    std::string decode_string(const char* str, unsigned len);
    
    // 提取变量
    void extract_variables(const uint8_t* data, unsigned len,
                         std::vector<std::string>& vars);
    
    // JS混淆技术
    enum class ObfuscationType {
        HEX_ENCODING,       // hex编码
        UNICODE_ESCAPE,    // unicode转义
        STRING_CONCAT,     // 字符串拼接
        COMMENT_REMOVAL,    // 注释移除
        WHITESPACE_REMOVAL  // 空白移除
    };
};
```

### KJ.3 Decompression {#kj-3-decompression}

```cpp
// decompress/decomp.h

// 压缩数据解压
class Decompressor {
public:
    // 解压数据
    bool decompress(const uint8_t* in, unsigned in_len,
                   uint8_t* out, unsigned* out_len);
    
    // 检测压缩类型
    CompressionType detect(const uint8_t* data, unsigned len);
    
    // 支持的压缩类型
    enum class CompressionType {
        NONE,
        GZIP,
        DEFLATE,
        LZMA,
        BZIP2
    };
};

// GZIP解压
class GzipDecompressor : public Decompressor {
public:
    bool decompress(const uint8_t* in, unsigned in_len,
                   uint8_t* out, unsigned* out_len) override;
};

// LZMA解压
class LzmaDecompressor : public Decompressor {
public:
    bool decompress(const uint8_t* in, unsigned in_len,
                   uint8_t* out, unsigned* out_len) override;
};
```

### KJ.4 File API {#kj-4-file-api}

```cpp
// file_api/file.h

// 文件处理API
class File {
public:
    // 文件处理配置
    void setup(uint32_t file_type_count, uint32_t sig_count);
    
    // 处理文件数据
    void process(const uint8_t* data, uint16_t size, 
                uint16_t ftype, uint32_t file_id);
    
    // 设置处理选项
    void set_options(uint32_t mask, int32_t depth, bool type_enabled);
    
    // 获取文件类型
    int16_t get_type_from_bytes(const uint8_t* data, uint16_t size);
    
    // 获取文件签名
    int16_t get_signature_from_bytes(const uint8_t* data, 
                                    uint16_t size, uint16_t type);
    
    // 文件发现
    bool file_found(const uint8_t* data, uint16_t size,
                   bool is_end, uint32_t* file_id);
};

// 文件签名
struct FileSignature {
    uint16_t type;           // 文件类型
    const char* magic;       // 魔术字节
    size_t offset;           // 偏移
    size_t length;          // 长度
    const char* name;       // 签名名称
};
```

### KJ.5 Payload Injector {#kj-5-payload-injector}

```cpp
// payload_injector/payload_injector.h

// 载荷注入器 - 用于在检测到威胁时注入响应
class PayloadInjector {
public:
    // 注入载荷
    bool inject(Packet* p, const uint8_t* payload, unsigned len);
    
    // 注入TCP reset
    bool inject_tcp_reset(Packet* p);
    
    // 注入ICMP unreachable
    bool inject_icmp_unreachable(Packet* p);
    
    // 设置注入模式
    void set_mode(InjectionMode mode);
    
    enum class InjectionMode {
        DISABLED,     // 禁用
        ASYNC,       // 异步注入
        INLINE       // 内联注入
    };
};
```

### KJ.6 Side Channel {#kj-6-side-channel}

```cpp
// side_channel/side_channel.h

// 侧信道 - 用于与其他安全工具通信
class SideChannel {
public:
    // 初始化
    bool init(unsigned id, const char* path);
    
    // 发送消息
    bool send(const uint8_t* msg, unsigned len);
    
    // 接收消息
    bool recv(uint8_t* msg, unsigned* len, unsigned timeout_ms);
    
    // 注册处理器
    void register_handler(uint32_t type, MessageHandler* handler);
    
    // 消息处理
    typedef void (*MessageHandler)(const uint8_t*, unsigned);
};

// 侧信道消息类型
enum class SideChannelMsgType : uint32_t {
    ALERT = 1,          // 告警消息
    BLOCK_IP = 2,        // 阻止IP
    QUARANTINE = 3,      // 隔离
    UPDATE_RULES = 4,    // 更新规则
    STATUS = 5           // 状态查询
};
```

### KJ.7 Trace {#kj-7-trace}

```cpp
// trace/trace.h

// 追踪系统 - 用于调试和诊断
class Trace {
public:
    // 初始化追踪
    static void init();
    
    // 设置追踪级别
    static void set_level(const char* module, TraceLevel level);
    
    // 追踪输出
    static void log(const char* module, TraceLevel level,
                  const char* fmt, ...);
    
    enum class TraceLevel : uint8_t {
        NONE = 0,
        ERROR = 1,
        WARNING = 2,
        INFO = 3,
        DEBUG = 4,
        VERBOSE = 5
    };
};

// 追踪宏
#define trace_init() Trace::init()
#define trace_set_level(mod, lvl) Trace::set_level(mod, lvl)
#define trace_log(mod, lvl, fmt, ...) \
    Trace::log(mod, lvl, fmt, ##__VA_ARGS__)
```

---
