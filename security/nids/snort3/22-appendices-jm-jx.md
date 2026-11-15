---
title: "Snort 3 · 附录 JM–JX"
description: "附录JM： 核心数据结构 — 附录JX： 统计系统"
---

# Snort 3 · 附录 JM–JX

[返回总目录](../snort3_architecture_analysis)

## 附录JM： 核心数据结构 {#附录jm-核心数据结构}

### JM.1 DataBuffer {#jm-1-databuffer}

```cpp
// framework/data_buffer.h

class DataBuffer {
public:
    DataBuffer() = default;
    DataBuffer(const uint8_t* data, unsigned len) : data_(data), len_(len) {}
    
    // 数据访问
    const uint8_t* data() const { return data_; }
    uint8_t* data() { return const_cast<uint8_t*>(data_); }
    unsigned len() const { return len_; }
    
    // 边界检查
    bool starts_with(const uint8_t* s, unsigned n) const;
    bool equals(const uint8_t* s, unsigned n) const;
    
    // 长度设置
    void set_len(unsigned len) { len_ = len; }
    
    // 切片
    void slice(unsigned offset, unsigned n, const uint8_t** s, unsigned* n) const;
    
protected:
    const uint8_t* data_ = nullptr;
    unsigned len_ = 0;
};
```

### JM.2 Cursor {#jm-2-cursor}

```cpp
// framework/cursor.h

class Cursor {
public:
    explicit Cursor(const InspectionBuffer* buf);
    
    // 缓冲区
    const InspectionBuffer* get_buffer() const { return buf_; }
    
    // 位置
    unsigned get_pos() const { return pos_; }
    void set_pos(unsigned pos) { pos_ = pos; }
    void advance(unsigned n) { pos_ += n; }
    
    // 相对位置
    unsigned relative_pos(unsigned abs_pos) const;
    
    // 检查边界
    bool is_at_end() const;
    unsigned size() const;
    
    // 规范化
    void normalize();
    
    // 添加可选缓冲区
    void add_buffer(const InspectionBuffer* buf);
    
private:
    const InspectionBuffer* buf_ = nullptr;
    unsigned pos_ = 0;
    std::vector<const InspectionBuffer*> extras_;
};
```

### JM.3 FlowKey {#jm-3-flowkey}

```cpp
// flow/flow_key.h

struct FlowKey {
    // 5元组
    IpProtocol protocol;     // 协议
    SfIp src_ip;            // 源IP
    SfIp dst_ip;            // 目标IP
    uint16_t src_port;      // 源端口
    uint16_t dst_port;      // 目标端口
    
    // VLAN
    uint16_t vlan_id;
    
    // 地址族
    uint8_t ip_family;      // AF_INET or AF_INET6
    
    // 比较
    bool operator==(const FlowKey& other) const;
    bool operator!=(const FlowKey& other) const;
    
    // 哈希
    uint32_t hash() const;
    
    // 创建
    static FlowKey* create(IpProtocol, const SfIp*, uint16_t, 
                         const SfIp*, uint16_t);
    void destroy();
};

// Flow哈希表
class FlowHashTable {
public:
    FlowHashTable(size_t max_flows);
    ~FlowHashTable();
    
    Flow* find(const FlowKey*);
    Flow* add(Flow*);
    void remove(Flow*);
    
    size_t get_count() const { return count_; }
    size_t get_max() const { return max_; }
    
private:
    size_t max_;
    size_t count_;
    FlowKey** table_;
};
```

---

## 附录JN： 检测引擎核心 {#附录jn-检测引擎核心}

### JN.1 IpsContext {#jn-1-ipscontext}

```cpp
// detection/ips_context.h

class IpsContext {
public:
    explicit IpsContext(Packet*);
    ~IpsContext();
    
    // 复位
    void reset();
    
    // 规则匹配状态
    enum class RuleState {
        NO_MATCH,      // 未匹配
        MATCH,        // 匹配
        MATCH_NOT,    // 匹配但取反
        DETECTED      // 已检测到
    };
    
    // 获取/设置状态
    RuleState get_state() const { return state_; }
    void set_state(RuleState s) { state_ = s; }
    
    // 复制
    IpsContext* clone() const;
    
public:
    Packet* const packet;      // 数据包
    InspectionBuffer buffer;  // 检测缓冲区
    
    const OptTreeNode* otn;   // 当前规则
    const RuleMask* mask;     // 规则掩码
    
    Cursor cursor;            // 光标
    
    unsigned num_matches;     // 匹配数量
    
private:
    RuleState state_;
};

// 检测上下文管理器
class IpsContextManager {
public:
    static IpsContext* allocate();
    static void release(IpsContext*);
    static void release_all();
    
private:
    static std::vector<IpsContext*> pool_;
    static std::mutex mutex_;
};
```

### JN.2 DetectionEngine {#jn-2-detectionengine}

```cpp
// detection/detection_engine.h

class DetectionEngine {
public:
    // 开始检测
    static void begin(Packet*);
    
    // 结束检测
    static void end();
    
    // 执行检测
    static int detect(IpsPolicy*, Packet*);
    
    // 快速搜索
    static void fp_search(InspectionBuffer&, const DetectOptionCategory&);
    
    // 事件队列
    static void queue_event(uint32_t gid, uint32_t sid);
    static void queue_events(const Event&);
    
    // 获取上下文
    static IpsContext* get_context();
    static void set_context(IpsContext*);
    
    // 规则状态
    static int rule_state_match(const OptTreeNode*);
    
    // 初始化
    static void init();
    static void term();
    
    // 验证
    static bool validate();
    
    // 获取检测模块
    static DetectionModule* get_detection_module();
    
    // 流检查
    static bool flow_is_inspected(const Flow*);
    static void flow_set_inspected(Flow*);
};
```

---

## 附录JO： 选项评估 {#附录jo-选项评估}

### JO.1 IpsOption {#jo-1-ipsoption}

```cpp
// ips_options/ips_option.h

class IpsOption {
public:
    virtual ~IpsOption() = default;
    
    // 选项类型
    virtual OptionType get_type() const = 0;
    
    // 评估
    virtual int eval(Cursor&, Packet*, IpsContext*) = 0;
    
    // 数据
    virtual const void* get_data() const = 0;
    
    // 字节码生成
    virtual unsigned generate(ByteCode*) const;
    
    // 打印
    virtual void print() const = 0;
    
    // 匹配字符串
    virtual std::string to_string() const;
    
protected:
    IpsOption(OptionType t) : type_(t) {}
    
    OptionType type_;
};

// 选项类型
enum class OptionType {
    CONTENT,           // content
    PCRE,             // pcre
    HEADER,           // header
    PAYLOAD,         // payload
    FLOW,            // flow
    STICKY_BUFFER,   // sticky buffer
    FILE_DATA,       // file_data
    FILE_TYPE,       // file_type
    FILE_SIGNATURE,  // file signature
    BASE64_DECODE,   // base64_decode
    BASE64_CONTENT,  // base64_content
    REGEX,           // regex
    // ... 更多
};
```

### JO.2 ContentOption {#jo-2-contentoption}

```cpp
// ips_options/content.h

class ContentOption : public IpsOption {
public:
    ContentOption(const char* pattern, unsigned len, bool negated);
    
    OptionType get_type() const override { return OptionType::CONTENT; }
    
    int eval(Cursor& c, Packet* p, IpsContext* ctx) override;
    
    const void* get_data() const override { return pattern_; }
    
    void print() const override;
    
    // 模式信息
    const char* get_pattern() const { return pattern_; }
    unsigned get_length() const { return length_; }
    bool is_negated() const { return negated_; }
    
    // 搜索选项
    bool is_no_case() const { return flags_ & FLAG_NO_CASE; }
    bool is_raw() const { return flags_ & FLAG_RAW; }
    bool is_dce() const { return flags_ & FLAG_DCE; }
    
private:
    enum Flags {
        FLAG_NO_CASE = 0x01,
        FLAG_RAW = 0x02,
        FLAG_DCE = 0x04,
        FLAG_URI = 0x08,
        FLAG_NOCASE = 0x10
    };
    
    const char* pattern_;
    unsigned length_;
    uint16_t flags_;
    bool negated_;
};
```

---

## 附录JP： 规则编译 {#附录jp-规则编译}

### JP.1 规则树 {#jp-1-规则树}

```cpp
// detection/treenorm.h

// 规则头节点
class RuleHeadNode {
public:
    RuleType type;          // 规则类型
    PktType protocol;       // 协议
    bool bidirectional;     // 双向
    
    snort::SfIp src_ip;    // 源IP
    uint16_t src_port;     // 源端口
    
    snort::SfIp dst_ip;    // 目标IP
    uint16_t dst_port;     // 目标端口
    
    RuleTreeNode* right;   // 右侧树
    OptTreeNode* down;     // 向下链表
    
    uint32_t gid;          // 生成器ID
    uint32_t sid;          // 签名ID
    
    uint32_t flags;
    
    IpsAction::Type action; // 动作
};

// 选项树节点
class OptTreeNode {
public:
    OptTreeNode* next;     // 下一个选项
    
    IpsAction::Type action;
    
    uint32_t gid;          // 生成器ID
    uint32_t sid;          // 签名ID
    uint32_t revision;    // 修订版本
    
    RuleHeadNode* rtn;
    OptList* opts;
    
    ClassType* class_type;
    
    // 元数据
    struct {
        uint32_t priority;
        uint32_t gen_id;
        uint32_t sig_id;
        uint32_t rule_id;
        const char* message;
    } meta;
    
    uint32_t event_data[6];
};
```

### JP.2 规则编译流程 {#jp-2-规则编译流程}

```cpp
// detection/rule_compile.h

class RuleCompiler {
public:
    static bool compile(const char* rule, IpsPolicy*);
    
    // 编译规则头
    static bool compile_header(const char*, RuleHeadNode*);
    
    // 编译规则选项
    static bool compile_options(const char*, OptTreeNode*);
    
    // 添加到规则树
    static void add_rule(RuleHeadNode*, OptTreeNode*, IpsPolicy*);
    
private:
    // 解析辅助
    static bool parse_src_dst(const char*, snort::SfIp*, uint16_t*);
    static bool parse_port(const char*, uint16_t*, uint16_t*, bool&);
    static bool parse_action(const char*, IpsAction::Type&);
    static bool parse_protocol(const char*, PktType&);
};
```

---

## 附录JQ： 事件系统 {#附录jq-事件系统}

### JQ.1 EventQueue {#jq-1-eventqueue}

```cpp
// detection/event_queue.h

class EventQueue {
public:
    EventQueue() = default;
    
    // 添加事件
    void add(const Event& e);
    
    // 获取事件
    const Event* first() const { return events_.empty() ? nullptr : &events_.front(); }
    const Event* next() const;
    
    // 数量
    unsigned count() const { return events_.size(); }
    bool empty() const { return events_.empty(); }
    
    // 清空
    void clear() { events_.clear(); }
    
    // 限制
    void set_max_events(unsigned);
    unsigned get_max_events() const { return max_events_; }
    
    // 限制检查
    void prune(unsigned gid, unsigned sid);
    
private:
    std::vector<Event> events_;
    unsigned max_events_ = 12;
    unsigned num_added_ = 0;
};

// 事件结构
struct Event {
    uint32_t gid;       // 生成器ID
    uint32_t sid;       // 签名ID
    uint32_t revision;  // 修订版本
    uint32_t context_id;// 上下文ID
    
    uint32_t event_id;  // 事件ID
    uint32_t event_second; // 事件秒
    
    uint32_t sig_threshold; // 签名阈值
    uint32_t gen_threshold; // 生成器阈值
    
    IpsAction::Type action; // 动作
};
```

---

## 附录JR： Stream模块 {#附录jr-stream模块}

### JR.1 StreamSplitter {#jr-1-streamsplitter}

```cpp
// stream/stream_splitter.h

class StreamSplitter {
public:
    virtual ~StreamSplitter() = default;
    
    // 扫描数据
    virtual Status scan(Packet*, const uint8_t* data, uint32_t len,
                       uint32_t flags, uint32_t* fp) = 0;
    
    // 是否是PAF
    virtual bool is_paf() const { return false; }
    
    // 方向
    bool to_server() const { return direction_ == TO_SERVER; }
    bool to_client() const { return direction_ == TO_CLIENT; }
    
    // 刷新
    virtual void flush(Packet*) {}
    
protected:
    StreamSplitter(bool to_server) : direction_(to_server ? TO_SERVER : TO_CLIENT) {}
    
    enum Direction { TO_SERVER, TO_CLIENT };
    Direction direction_;
    
    uint32_t bytes_scanned = 0;
};

// PAF分割器
class PAFSplitter : public StreamSplitter {
public:
    PAFSplitter(bool to_server, uint32_t max);
    
    bool is_paf() const override { return true; }
    
    Status scan(Packet*, const uint8_t* data, uint32_t len,
               uint32_t flags, uint32_t* fp) override;
    
private:
    uint32_t max_;
};
```

---

## 附录JS： 协议辅助 {#附录js-协议辅助}

### JS.1 协议位操作 {#js-1-协议位操作}

```cpp
// protocol_ids.h

// 协议位定义
#define PROTO_BIT__ANY     0xFFFFFFFF
#define PROTO_BIT__IP     0x000001
#define PROTO_BIT__TCP    0x000002
#define PROTO_BIT__UDP    0x000004
#define PROTO_BIT__ICMP   0x000008
#define PROTO_BIT__USER   0x000010
#define PROTO_BIT__FILE   0x000020
#define PROTO_BIT__PDU    0x000040

// 组合
#define PROTO_BIT__ANY_IP (PROTO_BIT__IP | PROTO_BIT__TCP | PROTO_BIT__UDP | PROTO_BIT__ICMP)
#define PROTO_BIT__ANY_SSN (PROTO_BIT__ANY_IP | PROTO_BIT__PDU | PROTO_BIT__FILE | PROTO_BIT__USER)

// 协议名称
static inline const char* get_proto_name(PktType p) {
    switch (p) {
        case PktType::IP: return "IP";
        case PktType::TCP: return "TCP";
        case PktType::UDP: return "UDP";
        case PktType::ICMP: return "ICMP";
        case PktType::PROTO: return "PROTO";
        default: return "UNKNOWN";
    }
}
```

---

## 附录JT： 辅助工具 {#附录jt-辅助工具}

### JT.1 时间工具 {#jt-1-时间工具}

```cpp
// time/stopwatch.h

class Stopwatch {
public:
    Stopwatch() { start(); }
    
    void start() { gettimeofday(&start_, nullptr); }
    void stop() { gettimeofday(&end_, nullptr); }
    
    // 毫秒
    double msec() const {
        return (end_.tv_sec - start_.tv_sec) * 1000.0 +
               (end_.tv_usec - start_.tv_usec) / 1000.0;
    }
    
    // 微秒
    double usec() const {
        return (end_.tv_sec - start_.tv_sec) * 1000000.0 +
               (end_.tv_usec - start_.tv_usec);
    }
    
    // 秒
    double sec() const { return msec() / 1000.0; }
    
private:
    struct timeval start_, end_;
};

// 时间戳
class Timestamp {
public:
    Timestamp() : ts_() {}
    explicit Timestamp(struct timeval& t) : ts_(t) {}
    
    uint64_t time() const { return ts_.tv_sec; }
    uint64_t usec() const { return ts_.tv_usec; }
    
    static Timestamp current();
    
    bool operator<(const Timestamp& other) const {
        if (ts_.tv_sec != other.ts_.tv_sec)
            return ts_.tv_sec < other.ts_.tv_sec;
        return ts_.tv_usec < other.ts_.tv_usec;
    }
    
private:
    struct timeval ts_;
};
```

### JT.2 字符串工具 {#jt-2-字符串工具}

```cpp
// utils/string_util.h

class StringUtils {
public:
    // 字符串到整数
    static bool str_to_int(const char*, int&);
    static bool str_to_int(const char*, unsigned&);
    static bool str_to_int(const char*, int64_t&);
    
    // 字符串到布尔
    static bool str_to_bool(const char*, bool&);
    
    // 字符串分割
    static std::vector<std::string> split(const char*, char delim);
    
    // 字符串替换
    static std::string replace(const std::string&, const std::string&, 
                              const std::string&);
    
    // 大小写转换
    static void to_lower(std::string&);
    static void to_upper(std::string&);
    
    // 去除空白
    static std::string trim(const std::string&);
    
    // 格式化
    static std::string format(const char*, ...);
};
```

---

## 附录JU： 主程序流程 {#附录ju-主程序流程}

### JU.1 Snort类 {#ju-1-snort类}

```cpp
// main/snort.h

class Snort {
public:
    // 初始化
    static void setup(int, char**);
    
    // 清理
    static void cleanup();
    
    // 运行
    static int run();
    
    // 获取/设置配置
    static SnortConfig* get_conf();
    static void set_conf(SnortConfig*);
    
    // 版本
    static const char* get_version();
    static const char* get_version_full();
    
    // 信号处理
    static void signal_handler(int);
    
    // 退出
    static void exit(int);
    
private:
    static void parse_cmd_line(int, char**);
    static void init_signals();
    static void print_usage();
    static void print_version();
};
```

### JU.2 Pig类 {#ju-2-pig类}

```cpp
// main/pig.h

class Pig {
public:
    explicit Pig(SnortConfig*);
    ~Pig();
    
    void start();
    void stop();
    void wait();
    
    // 获取数据包
    Packet* receive();
    
    // 分析数据包
    void analyze(Packet*);
    
    // 处理完成
    void retire(Packet*);
    
    // 统计
    void stats();
    
    // 是否完成
    bool is_done() const;
    
private:
    SnortConfig* config_;
    Analyzer* analyzer_;
    ThreadQueue* packet_queue_;
    std::atomic<bool> done_;
};
```

---

## 附录JV： DAQ接口 {#附录jv-daq接口}

### JV.1 DAQ基础 {#jv-1-daq基础}

```cpp
// packet_io/sfdaq.h

class DAQ {
public:
    // 单例
    static DAQ& get();
    
    // 初始化
    int init(const char* type, const char* filter, unsigned threads);
    
    // 开始/停止
    int start();
    int stop();
    
    // 获取数据包
    int acquire(unsigned idx, Packet*&, struct timeval*);
    
    // 发送数据包
    int send(int idx, const uint8_t* buf, unsigned len, uint32_t flags);
    
    // 循环模式
    int loop(DAQLoopCallback, void*);
    
    // 中断
    int breakloop(unsigned idx);
    
    // 统计
    int get_stats(DAQStats*, unsigned);
    int reset_stats(unsigned);
    
    // 清理
    int term();
    
    // 消息
    int deliver(const uint8_t*, uint32_t, DAQ_PktHdr_t*);
    
private:
    DAQ() = default;
};
```

---

## 附录JW： 插件API {#附录jw-插件api}

### JW.1 插件API结构 {#jw-1-插件api结构}

```cpp
// framework/base_api.h

#define SNORT_PLUGIN_API_VERSION 2

struct BaseApi {
    PluginType type;           // 插件类型
    uint32_t api_version;     // API版本
    uint32_t plugin_version;  // 插件版本
    const char* name;         // 插件名称
    const char* help;         // 帮助
};

// Inspector插件API
struct InspectApi : BaseApi {
    InspectorType itype;       // Inspector类型
    uint32_t proto_bits;      // 协议位
    void* buffers;            // 缓冲区
    const char* service;      // 服务
    
    Inspector* (*ctor)(Module*);
    void (*dtor)(Inspector*);
    
    Session* (*ssn)(Flow*);
    void (*reset)(Flow*);
};

// Action插件API
struct ActionApi : BaseApi {
    IpsAction::Type type;      // 动作类型
    void (*exec)(Packet*, void*);
};

// Logger插件API
struct LoggerApi : BaseApi {
    void (*open)(void);
    void (*close)(void);
    void (*log)(const char*, va_list);
};
```

---

## 附录JX： 统计系统 {#附录jx-统计系统}

### JX.1 统计收集 {#jx-1-统计收集}

```cpp
// profiler/counts.h

class PegCount {
public:
    PegCount() = default;
    explicit PegCount(uint64_t v) : value(v) {}
    
    operator uint64_t() const { return value; }
    PegCount& operator=(uint64_t v) { value = v; return *this; }
    PegCount& operator+=(uint64_t v) { value += v; return *this; }
    PegCount& operator++() { ++value; return *this; }
    
private:
    uint64_t value = 0;
};

// 计数信息
struct PegInfo {
    CountType type;      // 计数类型
    const char* name;   // 名称
    const char* help;   // 帮助
};

enum class CountType {
    SUM,    // 累加
    MAX,    // 最大
    AVG,    // 平均
    EVENTS  // 事件
};

// 统计表
class Counts {
public:
    void update(unsigned, PegCount);
    PegCount get(unsigned) const;
    
    void reset();
    
    void dump(const char* name, const PegInfo*) const;
    
private:
    std::vector<PegCount> counts_;
};
```

---
