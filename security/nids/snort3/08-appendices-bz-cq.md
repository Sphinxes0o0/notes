---
title: "Snort 3 · 附录 BZ–CQ"
description: "附录BZ：配置系统详解 — 附录CQ：DAta AcQuisition (DAQ)"
---

# Snort 3 · 附录 BZ–CQ

[返回总目录](../snort3_architecture_analysis)

## 附录BZ：配置系统详解 {#附录bz-配置系统详解}

### BZ.1 SnortConfig结构 {#bz-1-snortconfig结构}

```cpp
// main/snort_config.h

class SnortConfig {
public:
    SnortConfig();
    ~SnortConfig();
    
    // 活动策略
    IpsPolicy* get_ips_policy() const;
    void set_ips_policy(IpsPolicy*);
    
    // 流量管理
    FlowConfig* get_flow_config() const;
    
    // 检测配置
    DetectionConfig* get_detection_config() const;
    
    // 插件管理
    PluginManager* get_plugin_manager() const;
    InspectorManager* get_inspector_manager() const;
    ModuleManager* get_module_manager() const;
    
    // 搜索引擎
    MpseManager* get_mpse_manager() const;
    
    // 日志
    LoggerManager* get_logger_manager() const;
    
    // 行为配置
    bool get_inline_mode() const;
    void set_inline_mode(bool);
    
    // 事件处理
    AlertThresh* get_alert_thresholds() const;
    
private:
    // 各种配置...
    IpsPolicy* ips_policy = nullptr;
    FlowConfig* flow_config = nullptr;
    DetectionConfig* detection_config = nullptr;
    PluginManager* plugin_manager = nullptr;
    InspectorManager* inspector_manager = nullptr;
    ModuleManager* module_manager = nullptr;
    // ...
};
```

---

## 附录CA：网络接口定义 {#附录ca-网络接口定义}

### CA.1 网络层协议处理 {#ca-1-网络层协议处理}

```cpp
// protocols/ipapi.h

class IpApi {
public:
    // 源和目标地址
    struct {
        uint32_t src_ip;
        uint32_t dst_ip;
    } ip32;
    
    // 获取地址族
    IpProtocol get_protocol() const
    { return protocol; }
    
    // 检查IPv4/IPv6
    bool is_ip6() const
    { return ver == 6; }
    
    // TTL相关
    uint8_t ttl() const
    { return ip4.ttl; }
    
    // TOS相关
    uint8_t tos() const
    { return ip4.tos; }
    
    // 长度
    uint16_t length() const
    { return ip4.len; }
    
private:
    uint8_t ver;      // 版本
    IpProtocol protocol; // 协议
};
```

---

## 附录CB：时间处理 {#附录cb-时间处理}

### CB.1 时间获取 {#cb-1-时间获取}

```cpp
// time/stopwatch.h

class Stopwatch {
public:
    // 开始计时
    void start()
    { gettimeofday(&start_time, nullptr); }
    
    // 停止计时
    void stop()
    { gettimeofday(&end_time, nullptr); }
    
    // 获取经过的时间（微秒）
    uint64_t elapsed() const {
        return (end_time.tv_sec - start_time.tv_sec) * 1000000 +
               (end_time.tv_usec - start_time.tv_usec);
    }
    
    // 获取经过的时间（毫秒）
    uint64_t elapsed_ms() const {
        return elapsed() / 1000;
    }
    
    // 获取当前时间
    static struct timeval get_time() {
        struct timeval tv;
        gettimeofday(&tv, nullptr);
        return tv;
    }
};
```

---

## 附录CC：内存管理 {#附录cc-内存管理}

### CC.1 内存池 {#cc-1-内存池}

```cpp
// memory/memory_cap.h

class MemoryCap {
public:
    // 获取单例实例
    static MemoryCap& get_instance();
    
    // 检查是否超过限制
    bool check(size_t) const;
    
    // 分配内存
    void* allocate(size_t);
    
    // 释放内存
    void deallocate(void*);
    
    // 获取已使用内存
    size_t get_used() const
    { return used; }
    
    // 获取最大内存
    size_t get_max() const
    { return max; }
    
    // 获取统计信息
    struct MemoryStats {
        size_t total_alloc;
        size_t total_free;
        size_t active_alloc;
        size_t total_requests;
        size_t failed_requests;
    };
};
```

---

## 附录CD：原子操作 {#附录cd-原子操作}

### CD.1 原子变量 {#cd-1-原子变量}

```cpp
// utils/atomic.h

template<typename T>
class Atomic {
public:
    Atomic() : value() {}
    Atomic(T val) : value(val) {}
    
    // 加载
    T load() const volatile {
        return __atomic_load_n(&value, __ATOMIC_ACQUIRE);
    }
    
    // 存储
    void store(T val) volatile {
        __atomic_store_n(&value, val, __ATOMIC_RELEASE);
    }
    
    // 增加
    T fetch_add(T val) volatile {
        return __atomic_fetch_add(&value, val, __ATOMIC_ACQ_REL);
    }
    
    // 比较交换
    bool compare_exchange(T& expected, T desired) volatile {
        return __atomic_compare_exchange_n(&value, &expected, desired,
            false, __ATOMIC_ACQ_REL, __ATOMIC_ACQUIRE);
    }
    
private:
    T value;
};
```

---

## 附录CE：正则表达式引擎 {#附录ce-正则表达式引擎}

### CE.1 正则表达式接口 {#ce-1-正则表达式接口}

```cpp
// search_engines/re.h

class Regex {
public:
    // 构造函数
    Regex(const char*, unsigned, unsigned&);
    ~Regex();
    
    // 执行匹配
    int match(const char*, unsigned, unsigned,
              unsigned*, unsigned*, unsigned*);
    
    // 获取信息
    unsigned get_pattern_length() const
    { return pattern_len; }
    
    // 错误信息
    const char* get_error() const
    { return err_buf; }
    
    // 最大状态数
    static unsigned max_states();
};
```

---

## 附录CF：文件系统处理 {#附录cf-文件系统处理}

### CF.1 文件处理 {#cf-1-文件处理}

```cpp
// file_processing/file_table.h

class FileProcessor {
public:
    // 设置文件处理配置
    void setup(uint32_t file_type_count, uint32_t file_signature_count);
    
    // 处理文件数据
    void process(Packet*, uint8_t* data, uint16_t size, uint16_t ftype, uint32_t file_id);
    
    // 获取文件类型
    int16_t get_type_from_bytes(const uint8_t* data, uint16_t size);
    
    // 获取文件签名
    int16_t get_signature_from_bytes(const uint8_t* data, uint16_t size, uint16_t type);
    
    // 设置文件处理选项
    void set_options(uint32_t file_mask, uint32_t file_depth, bool enable_type);
};
```

### CF.2 MIME解码 {#cf-2-mime解码}

```cpp
// file_processing/mime_processing/file_mime.h

class FileMime {
public:
    // 解析MIME数据
    void process_mime_data(const uint8_t* data, uint16_t size,
                           bool is_b64, bool is_qp, bool is_i;
    
    // 获取解码后的数据
    const uint8_t* get_decoded_data() const
    { return decoded_buffer; }
    
    // 获取解码后数据长度
    uint16_t get_decoded_data_length() const
    { return decoded_data_len; }
};
```

---

## 附录CG：缓冲区管理 {#附录cg-缓冲区管理}

### CG.1 InspectionBuffer {#cg-1-inspectionbuffer}

```cpp
// framework/inspection_buffer.h

class InspectionBuffer {
public:
    InspectionBuffer();
    ~InspectionBuffer();
    
    // 初始化
    void init(unsigned);
    void init(unsigned, const uint8_t*, unsigned);
    
    // 清理
    void clear();
    
    // 数据指针
    const uint8_t* data() const
    { return data_; }
    
    // 数据长度
    unsigned length() const
    { return len; }
    
    // 可修改指针
    uint8_t* data()
    { return data_; }
    
    // 设置数据
    void set(const uint8_t* d, unsigned n);
    
    // 偏移
    void offset(unsigned o)
    { ofs = o; }
    
    unsigned offset() const
    { return ofs; }
    
    // 重新使用缓冲区
    void reuse();
    
private:
    uint8_t* data_;     // 数据指针
    unsigned len;       // 数据长度
    unsigned ofs;       // 偏移量
    unsigned buf_size;  // 缓冲区大小
    bool owner;         // 是否拥有数据
};
```

---

## 附录CH：性能分析 {#附录ch-性能分析}

### CH.1 性能统计 {#ch-1-性能统计}

```cpp
// profiler/profiler.h

struct ProfileStats {
    // 模块名称
    const char* name;
    
    // 时间统计
    uint64_t ticks;           // 总时钟周期
    uint64_t elapsed;          // 经过时间
    
    // 计数
    uint64_t calls;            // 调用次数
    
    // 最大值
    uint64_t max_ticks;        // 最大时钟周期
    uint64_t max_per_inspect;  // 每次检查最大
    
    // 百分比
    double pct_of_total;       // 占总量百分比
    double pct_of_parent;      // 占父百分比
    
    // 内存统计
    size_t mem_size;           // 内存大小
    size_t total_mem_size;     // 总内存大小
    
    // 构造函数
    ProfileStats(const char* n);
};

// 配置
struct ProfileConfig {
    bool enabled;              // 是否启用
    bool summary;              // 是否输出摘要
    unsigned long long aggregate_threshold; // 聚合阈值
};
```

### CH.2 Profile宏 {#ch-2-profile宏}

```cpp
// profiler/profiler.h

#define Profile profile __attribute__((cleanup(auto_cleanup_profile)))

class AutoProfile {
public:
    AutoProfile(ProfileStats*);
    ~AutoProfile();
};
```

---

## 附录CI：追踪系统 {#附录ci-追踪系统}

### CI.1 追踪配置 {#ci-1-追踪配置}

```cpp
// trace/trace_api.h

// 追踪级别
enum class TraceLevel : uint8_t {
    NONE = 0,
    MIN = 1,
    MID = 2,
    MAX = 3
};

// 追踪选项
struct TraceOptions {
    const char* module_name;  // 模块名称
    TraceLevel level;          // 追踪级别
    uint8_t trace_type;        // 追踪类型
    bool checksum_drop;        // 校验和丢弃
    bool decode;               // 解码
    bool log;                  // 日志
};
```

### CI.2 追踪宏 {#ci-2-追踪宏}

```cpp
// trace/trace.h

#define trace_register(module, api) ...

#define trace_logf(trace, pkt, ...) \
    do { \
        if (trace) \
            trace_log(trace, pkt, __VA_ARGS__); \
    } while(0)
```

---

## 附录CJ：主循环流程 {#附录cj-主循环流程}

### CJ.1 Snort主循环 {#cj-1-snort主循环}

```cpp
// main.cc 主要处理流程

int main(int argc, char* argv[]) {
    // 初始化
    Snort::setup(argc, argv);
    
    // 创建数据包分析器
    Pig pig(config);
    
    // 运行分析
    pig.start();
    
    // 主循环
    while ( !pig.is_done() ) {
        Packet* p = pig.receive();
        
        if ( p ) {
            pig.analyze(p);
            pig.retire(p);
        }
    }
    
    // 清理
    pig.shutdown();
    
    Snort::cleanup();
    
    return 0;
}
```

### CJ.2 Analyzer处理 {#cj-2-analyzer处理}

```cpp
// main/analyzer.h

class Analyzer {
public:
    explicit Analyzer(snort::SnortConfig*);
    ~Analyzer();
    
    void start();
    void stop();
    
    // 接收数据包
    Packet* receive();
    
    // 分析数据包
    void analyze(Packet*);
    
    // 处理完成
    void retire(Packet*);
    
    // 是否完成
    bool is_done() const;
    
    // 获取统计
    void stats();
};
```

---

## 附录CK：规则选项数据结构 {#附录ck-规则选项数据结构}

### CK.1 OptTreeNode {#ck-1-opttreenode}

```cpp
// detection/treenorm.h

class OptTreeNode {
public:
    // 链表指针
    OptTreeNode* next;
    
    // 规则动作
    IpsAction::Type action;
    
    // 分类信息
    uint32_t gid;           // 生成器ID
    uint32_t sid;           // 签名ID
    uint32_t revision;      // 修订版本
    
    // 规则头
    RuleHeadNode* rhn;
    
    // 规则选项
    OptList* opts;
    
    // 分类
    ClassType* class_type;
    
    // 报警元数据
    struct {
        uint32_t priority;
        uint32_t gen_id;
        uint32_t sig_id;
        uint32_t rule_id;
        const char* message;
    } meta;
    
    // 事件数据
    uint32_t event_data[6];
};
```

### CK.2 RuleHeadNode {#ck-2-ruleheadnode}

```cpp
// detection/treenorm.h

class RuleHeadNode {
public:
    // 规则头类型
    RuleType type;              // PASS, ACTIVE, DROP, ALERT, LOG
    
    // 协议
    PktType protocol;
    
    // 方向
    bool bidirectional;         // 双向
    
    // 源和目标
    snort::SfIp src_ip;
    uint16_t src_port;
    
    snort::SfIp dst_ip;
    uint16_t dst_port;
    
    // 操作
    uint32_t flags;
    
    // 报警信息
    uint32_t gid;
    uint32_t sid;
};
```

---

## 附录CL：Codec系统 {#附录cl-codec系统}

### CL.1 Codec基类 {#cl-1-codec基类}

```cpp
// framework/codec.h

class Codec {
public:
    virtual ~Codec() = default;
    
    // 名称
    virtual const char* get_name() const = 0;
    
    // 解码
    virtual bool decode(Packet*, const uint8_t*, uint16_t, CodecData*) = 0;
    
    // 编码
    virtual void encode(Packet*, uint8_t*, uint16_t*, uint32_t*) {}
    
    // 更新长度
    virtual void update_length(Packet*, uint8_t*, uint16_t) {}
    
    // 获取下一层
    virtual void get_data(char*, uint16_t*) {}
    
    // 是否启用了日志
    virtual bool is_enabled() const
    { return enabled; }
    
    // 启用/禁用
    void enable()
    { enabled = true; }
    
    void disable()
    { enabled = false; }
    
    // 类型
    virtual uint16_t get_type() const = 0;
    virtual uint16_t get_hdr_len() const = 0;
    
    // 标志
    uint32_t get_flags() const
    { return flags; }
    
protected:
    bool enabled = true;
    uint32_t flags = 0;
};
```

---

## 附录CM：日志系统 {#附录cm-日志系统}

### CM.1 日志管理器 {#cm-1-日志管理器}

```cpp
// loggers/logger_manager.h

class LoggerManager {
public:
    LoggerManager();
    ~LoggerManager();
    
    // 添加日志输出
    void add_logger(const char* name, Logger* logger);
    
    // 记录日志
    void log(Packet*, const char* msg, uint16_t len);
    
    // 刷新日志
    void flush();
    
    // 获取日志
    Logger* get_logger(const char* name) const;
    
    // 统计
    void show_stats() const;
};
```

### CM.2 日志输出 {#cm-2-日志输出}

```cpp
// loggers/alert_func.h

class AlertOutput {
public:
    virtual ~AlertOutput() = default;
    
    // 输出报警
    virtual void alert(Packet*, uint32_t, uint32_t) = 0;
};
```

---

## 附录CN：过滤器系统 {#附录cn-过滤器系统}

### CN.1 检测过滤器 {#cn-1-检测过滤器}

```cpp
// filters/sf_filter.h

class DetectionFilter {
public:
    // 检测阈值类型
    enum class Type : uint8_t {
        LIMIT,      // 限制
        THRESHOLD,  // 阈值
        BOTH,       // 两者
        NOTSYNC     // 不同步
    };
    
    // 类型
    enum class CountType : uint8_t {
        SECONDS,
        PACKETS
    };
    
    // 应用到
    void apply(Packet*, const RuleHeadNode*);
    
    // 检查
    bool check(Packet*, const RuleHeadNode*);
};
```

### CN.2 速率限制过滤器 {#cn-2-速率限制过滤器}

```cpp
// filters/rate_filter.h

class RateFilter {
public:
    // 速率限制类型
    enum class RateType : uint8_t {
        ABSOLUTE,   // 绝对
        THRESHOLD,  // 阈值
        BOTH,       // 两者
        NOTSYNC     // 不同步
    };
    
    // 速率
    enum class Rate : uint8_t {
        SECOND,
        MINUTE,
        HOUR,
        SECONDARY
    };
    
    // 应用
    void apply(Packet*, IpsAction::Type, uint32_t, uint32_t);
};
```

---

## 附录CO：网络地址处理 {#附录co-网络地址处理}

### CO.1 IP地址表示 {#co-1-ip地址表示}

```cpp
// utils/sfip.h

class SfIp {
public:
    // 构造函数
    SfIp();
    SfIp(const char*);
    SfIp(const SfIp&);
    
    // 设置地址
    int set(const char*);
    int set(const uint8_t*, unsigned);
    
    // 获取原始数据
    const uint8_t* get_ip6_ptr() const;
    uint32_t ip32() const;
    
    // 比较
    bool operator==(const SfIp&) const;
    bool operator!=(const SfIp&) const;
    bool operator<(const SfIp&) const;
    
    // 检查IPv4/IPv6
    bool is_ip4() const;
    bool is_ip6() const;
    
    // 掩码操作
    int apply_mask(const SfIp&);
};
```

---

## 附录CP：端口处理 {#附录cp-端口处理}

### CP.1 端口定义 {#cp-1-端口定义}

```cpp
// utils/port.h

class Port {
public:
    // 端口类型
    enum class Type : uint8_t {
        ANY,        // 任意端口
        SPECIFIC,   // 特定端口
        RANGE,      // 端口范围
        NEGATED     // 取反
    };
    
    // 构造函数
    Port();
    Port(uint16_t port, Type t = Type::SPECIFIC);
    Port(uint16_t lo, uint16_t hi);
    
    // 类型
    Type type;
    
    // 端口值
    uint16_t port;
    uint16_t lo_port;
    uint16_t hi_port;
    
    // 检查端口
    bool contains(uint16_t p) const;
    bool contains(const Port&) const;
    
    // 操作符
    bool operator==(const Port&) const;
    bool operator!=(const Port&) const;
};
```

---

## 附录CQ：DAta AcQuisition (DAQ) {#附录cq-data-acquisition-daq}

### CQ.1 DAQ模块接口 {#cq-1-daq模块接口}

```cpp
// packet_io/sfdaq.h

class DAQ {
public:
    // 获取DAQ实例
    static DAQ& get();
    
    // 初始化
    int init(const char* type, const char* filter, unsigned threads);
    
    // 开始获取
    int start();
    
    // 停止获取
    int stop();
    
    // 获取数据包
    int acquire(unsigned idx, Packet*&, struct timeval*);
    
    // 发送数据包
    int send(int idx, const uint8_t* buf, unsigned len, uint32_t flags);
    
    // 循环模式
    int loop(DAQLoopCallback, void*);
    
    // 清理
    int term();
};
```

### CQ.2 DAQ消息类型 {#cq-2-daq消息类型}

```cpp
enum DAQMsgType {
    DAQ_MSG_LOAD = 0,       // 加载模块
    DAQ_MSG_CONFIG,          // 配置模块
    DAQ_MSG_START,           // 开始
    DAQ_MSG_STOP,            // 停止
    DAQ_MSG_ACQUIRE,         // 获取数据包
    DAQ_MSG_INJECT,          // 注入数据包
    DAQ_MSG_BREAKLOOP,       // 退出循环
    DAQ_MSG_GET_STATS,       // 获取统计
    DAQ_MSG_RESET_STATS,     // 重置统计
    DAQ_MSG_MSG_SIZE,        // 消息大小
    DAQ_MSG_INPUT_SPEC       // 输入规范
};
```

---
