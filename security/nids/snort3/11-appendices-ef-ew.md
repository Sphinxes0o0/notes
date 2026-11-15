---
title: "Snort 3 · 附录 EF–EW"
description: "附录EF： 对象池 — 附录EW： 规则语法"
---

# Snort 3 · 附录 EF–EW

[返回总目录](../snort3_architecture_analysis)

## 附录EF： 对象池 {#附录ef-对象池}

### EF.1 内存池分配 {#ef-1-内存池分配}

```cpp
// memory/memory_pool.h

class MemoryPool {
public:
    // 创建内存池
    MemoryPool(size_t item_size, unsigned num_items);
    ~MemoryPool();
    
    // 分配
    void* allocate();
    
    // 释放
    void deallocate(void*);
    
    // 检查可用
    unsigned available() const
    { return free_list.size(); }
    
    // 检查已用
    unsigned used() const
    { return num_items - free_list.size(); }
    
private:
    size_t item_size;              // 项大小
    unsigned num_items;            // 项数量
    std::vector<void*> free_list; // 空闲列表
    void* memory_block;            // 内存块
};

// 对象池模板
template<typename T>
class ObjectPool {
public:
    T* allocate() {
        void* p = pool.allocate();
        return new (p) T();
    }
    
    void deallocate(T* p) {
        p->~T();
        pool.deallocate(p);
    }
    
private:
    MemoryPool pool;
};
```

---

## 附录EG： 事件日志系统 {#附录eg-事件日志系统}

### EG.1 事件记录 {#eg-1-事件记录}

```cpp
// loggers/event_throttle.h

class EventThrottle {
public:
    // 初始化
    void init(unsigned max_events, unsigned window_sec);
    
    // 检查是否可以记录
    bool can_log(uint32_t gid, uint32_t sid);
    
    // 记录事件
    void log_event(uint32_t gid, uint32_t sid);
    
    // 重置
    void reset();
    
private:
    // 事件键
    struct EventKey {
        uint32_t gid;
        uint32_t sid;
        
        bool operator<(const EventKey& other) const {
            return gid < other.gid || (gid == other.gid && sid < other.sid);
        }
    };
    
    // 事件统计
    struct EventStats {
        unsigned count;
        timeval first;
        timeval last;
    };
    
    std::map<EventKey, EventStats> event_map;
    unsigned max_events;
    unsigned window_sec;
};
```

---

## 附录EH： 延迟监控 {#附录eh-延迟监控}

### EH.1 包延迟追踪 {#eh-1-包延迟追踪}

```cpp
// latency/packet_latency.h

class PacketLatency {
public:
    // 开始计时
    void start(Packet* p) {
        p->pkt_time = get_time();
    }
    
    // 检查超时
    bool check(Packet* p, unsigned max_ms) {
        uint64_t elapsed = get_time() - p->pkt_time;
        return elapsed > max_ms;
    }
    
    // 获取时间
    static uint64_t get_time() {
        timeval tv;
        gettimeofday(&tv, nullptr);
        return (uint64_t)tv.tv_sec * 1000 + tv.tv_usec / 1000;
    }
};

// 规则延迟追踪
class RuleLatency {
public:
    // 开始规则评估计时
    void start_rule_eval() {
        rule_start = PacketLatency::get_time();
    }
    
    // 检查规则评估延迟
    bool check_rule_latency(unsigned max_ms) {
        uint64_t elapsed = PacketLatency::get_time() - rule_start;
        return elapsed > max_ms;
    }
    
    // 规则级别延迟
    enum class Level : uint8_t {
        NONE,
        LOW,
        MEDIUM,
        HIGH
    };
    
    Level level = Level::NONE;
    
private:
    uint64_t rule_start;
};
```

---

## 附录EI： 配置合并 {#附录ei-配置合并}

### EI.1 多配置文件处理 {#ei-1-多配置文件处理}

```cpp
// main/config_merger.h

class ConfigMerger {
public:
    // 合并两个配置
    static bool merge(SnortConfig* base, const SnortConfig* overlay);
    
    // 合并特定模块
    static bool merge_module(Module*, const Value&);
    
    // 合并检测器配置
    static bool merge_detection(const DetectionConfig*);
    
    // 合并流配置
    static bool merge_flow(const FlowConfig*);
    
    // 合并规则
    static bool merge_rules(SnortConfig*);
    
private:
    // 递归合并表
    static bool merge_table(const Lua::Config* base, const Lua::Config* overlay);
    
    // 应用覆盖
    static bool apply_overlay(const char* path, const Value&);
};
```

---

## 附录EJ： 数据流图 {#附录ej-数据流图}

### EJ.1 包处理数据流 {#ej-1-包处理数据流}

```
                    ┌─────────────────┐
                    │    Packet* p    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Pig::analyze  │
                    │    (receive)    │
                    └────────┬────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Analyzer::analyze()                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 1. DAQ获取数据包                                              │ │
│  │ 2. pkt = Packet::make()  // 创建Packet对象                    │ │
│  │ 3. decode_packet(pkt)     // 协议解码                         │ │
│  │ 4. process(pkt)           // 处理数据包                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    InspectorManager::process()                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ for each Inspector in inspectors:                          │ │
│  │     if Inspector.type == IT_PACKET:                         │ │
│  │         Inspector.eval(pkt)                                 │ │
│  │     else if Inspector.type == IT_STREAM:                   │ │
│  │         Inspector.eval(pkt)                                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      DetectionEngine::detect()                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 1. Packet latency check                                     │ │
│  │ 2. fp_search() - Fast pattern search                       │ │
│  │ 3. for each matched rule:                                   │ │
│  │ 4.     eval_rule_options(rule, pkt)                         │ │
│  │ 5.     if all options match:                                │ │
│  │ 6.         generate event                                   │ │
│  │ 7. Rule latency check                                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                     ActionExecutor::execute()                      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 1. for each Action in actions:                              │ │
│  │ 2.     Action.exec(pkt)                                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 附录EK： 时序图 - TCP会话建立 {#附录ek-时序图-tcp会话建立}

### EK.1 三次握手检测 {#ek-1-三次握手检测}

```
Client                              Server
  │                                    │
  │ ──── SYN (seq=x) ─────────────────▶│
  │        │                           │
  │        │ TcpSession::init_session  │
  │        │ on_syn_recv()             │
  │        ▼                           │
  │   TCP_SYN_SENT ────────────────────│
  │                                    │
  │ ◀──── SYN+ACK (seq=y, ack=x+1) ───│
  │        │                           │
  │        │ TcpSession::init_session │
  │        │ on_synack_recv()          │
  │        ▼                           │
  │   TCP_SYN_RECV ◀───────────────────│
  │                                    │
  │ ──── ACK (seq=x+1, ack=y+1) ─────▶│
  │        │                           │
  │        │ TcpStreamTracker::        │
  │        │ update_on_3whs_ack()      │
  │        ▼                           │
  │   TCP_ESTABLISHED ─────────────────│
  │                                    │
  │        Session Established          │
  │                                    │
```

---

## 附录EL： 流重组时序 {#附录el-流重组时序}

### EL.1 TCP数据重组流程 {#el-1-tcp数据重组流程}

```
Packet                       Reassembler                    StreamTracker
  │                              │                                │
  │ ── TCP Data Segment ───────▶│                                │
  │      (seq=n, len=L)         │                                │
  │                              │                                │
  │                              │ TcpReassembler::process()      │
  │                              │   │                            │
  │                              │   ├─ validate_seq()            │
  │                              │   ├─ check_overlap()          │
  │                              │   └─ add_to_seglist()         │
  │                              │                                │
  │                              │ TcpStreamTracker::             │
  │                              │   update_tracker_*()           │
  │                              │                                │
  │                              │          ┌────────────────┐    │
  │                              │          │ TcpSegmentNode │    │
  │                              │          │ seq=n          │    │
  │                              │          │ len=L          │    │
  │                              │          │ data=...       │    │
  │                              │          └───────┬────────┘    │
  │                              │                  │              │
  │                              │                  ▼              │
  │                              │   ┌────────────────────────┐   │
  │                              │   │ TcpReassemblySegments │   │
  │                              │   │ (sorted by seq)       │   │
  │                              │   └────────────────────────┘   │
  │                              │                                │
  │                              │ FlushPolicy triggered          │
  │                              │                                │
  │ ◀── Reassembled Data ───────│                                │
  │      (continuous buffer)     │                                │
  │                              │                                │
```

---

## 附录EM： 规则匹配时序 {#附录em-规则匹配时序}

### EM.1 完整检测流程 {#em-1-完整检测流程}

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Rule Matching Flow                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. fp_prealloc()                                                       │
│     ├── Allocate detection context                                       │
│     ├── Initialize cursor                                                │
│     └── Setup rule state                                                │
│                                                                          │
│  2. fp_evade_lru_cache()                                                │
│     └── Evict old entries from LRU cache                                │
│                                                                          │
│  3. fp_normalize()                                                       │
│     ├── Normalize payload                                                │
│     └── Apply normalization transforms                                  │
│                                                                          │
│  4. rule_group_build()                                                  │
│     └── Build rule groups from opt trees                                │
│                                                                          │
│  5. fp_search()  ◀── Fast Pattern Search                              │
│     ├── mpse_search()                                                    │
│     │   └── AC/Hyperscan pattern match                                  │
│     │                                                                    │
│     ├── for each match:                                                 │
│     │   ├── queue_match()                                               │
│     │   └── add_match()                                                 │
│     │                                                                    │
│     └── return match_count                                              │
│                                                                          │
│  6. fpDetectRuleMatch()  ◀── Rule Evaluation                          │
│     │                                                                    │
│     ├── for each queued match:                                          │
│     │   │                                                                │
│     │   ├── rule_state_match()                                         │
│     │   │   └── Check rule state (enabled, etc)                         │
│     │   │                                                                │
│     │   ├── ips_rule_match()                                            │
│     │   │   │                                                            │
│     │   │   ├── option_tree_evaluate()                                  │
│     │   │   │   │                                                        │
│     │   │   │   ├── for each option in tree:                           │
│     │   │   │   │   └── ips_option->eval()                              │
│     │   │   │   │                                                        │
│     │   │   │   └── return (all options matched)                        │
│     │   │   │                                                            │
│     │   │   └── detection_module->non_max_scale_check()                  │
│     │   │                                                                │
│     │   └── rule_util_generate_event()                                  │
│     │       └── Create detection event                                  │
│     │                                                                    │
│     └── fp_finalize()                                                    │
│         └── Free detection context                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 附录EN： 插件生命周期 {#附录en-插件生命周期}

### EN.1 Inspector插件加载 {#en-1-inspector插件加载}

```cpp
// managers/plugin_manager.h

class PluginManager {
public:
    // 初始化插件系统
    static void init();
    
    // 加载插件
    static void load_plugins(const char* path);
    
    // 加载单个插件
    static void load_plugin(const char* path);
    
    // 创建插件
    static Inspector* create_inspector(PluginType, const char* name, Module*);
    
    // 获取插件
    static Plugin* get_plugin(PluginType, const char* name);
    
    // 插件类型
    enum class PluginType {
        INSPECTOR,
        CODEC,
        IPS_OPTION,
        LOG,
        ACTION,
        SEARCH_ENGINE,
        MPSE
    };
    
    // 插件信息
    struct Plugin {
        PluginType type;
        const char* name;
        void* handle;      // 动态库句柄
        void* (*ctor)();  // 构造函数
        void (*dtor)(void*);
    };
};
```

---

## 附录EO： 消息类型注册 {#附录eo-消息类型注册}

### EO.1 PubSub消息类型 {#eo-1-pubsub消息类型}

```cpp
// pub_sub/message_ids.h

namespace MessageId {
    // 消息类型
    enum {
        // 内部消息 (IntrinsicEventIds)
        FLOW_NO_SERVICE = 0,
        FLOW_SOFTED,
        DEBUG_FLOW,
        
        // 数据包消息
        PACKET_DETAINED,
        PACKET_REINJECT,
        
        // 流消息
        FLOW_NEW,
        FLOW_DELETE,
        FLOW_STATE_CHANGE,
        
        // 检测消息
        DETECTION_ALERT,
        DETECTION_MATCH,
        
        // 统计消息
        STATS_UPDATE,
        
        // 自定义消息...
    };
}

// 发布消息
DataBus::publish(MESSAGE_ID, packet);

// 订阅消息
class MyHandler : public EventHandler {
public:
    void handle(Packet* p) override {
        // 处理消息
    }
};

DataBus::subscribe(MESSAGE_ID, new MyHandler());
```

---

## 附录EP： 错误处理 {#附录ep-错误处理}

### EP.1 错误码定义 {#ep-1-错误码定义}

```cpp
// utils/error.h

// 错误码
enum class ErrorCode {
    SUCCESS = 0,
    
    // 通用错误
    FAILURE = -1,
    INVALID_ARG = -2,
    NULL_PTR = -3,
    OUT_OF_RANGE = -4,
    OUT_OF_MEMORY = -5,
    BUFFER_TOO_SMALL = -6,
    
    // 配置错误
    CONFIG_INVALID = -100,
    CONFIG_NOT_FOUND = -101,
    CONFIG_SYNTAX_ERROR = -102,
    CONFIG_DUPLICATE = -103,
    
    // 协议错误
    DECODE_ERROR = -200,
    DECODE_INVALID_HEADER = -201,
    DECODE_TRUNCATED = -202,
    DECODE_BAD_LENGTH = -203,
    
    // 检测错误
    DETECT_ERROR = -300,
    DETECT_TIMEOUT = -301,
    DETECT_LATENCY = -302,
    
    // 流错误
    STREAM_ERROR = -400,
    STREAM_INVALID_SEQ = -401,
    STREAM_REASSEMBLY = -402,
    STREAM_TIMEOUT = -403
};

// 错误处理宏
#define THROW_ERROR(code) throw Error(code, __FILE__, __LINE__)
#define TRY try {
#define CATCH } catch (const Error& e) {
#define END_TRY }
```

---

## 附录EQ： 统计信息 {#附录eq-统计信息}

### EQ.1 统计收集 {#eq-1-统计收集}

```cpp
// profiler/perf_stats.h

class PerfStats {
public:
    // 包统计
    struct PacketStats {
        uint64_t total_pkts;         // 总包数
        uint64_t total_bytes;        // 总字节数
        uint64_t filtered_pkts;      // 过滤包数
        uint64_t dropped_pkts;       // 丢弃包数
        uint64_t blocked_pkts;        // 阻止包数
    };
    
    // 协议统计
    struct ProtoStats {
        uint64_t tcp_pkts;           // TCP包数
        uint64_t udp_pkts;           // UDP包数
        uint64_t icmp_pkts;          // ICMP包数
        uint64_t other_pkts;          // 其他包数
    };
    
    // 检测统计
    struct DetectStats {
        uint64_t alerts;              // 报警数
        uint64_t matches;             // 匹配数
        uint64_t latency_drops;       // 延迟丢弃
        uint64_t rule_matches;        // 规则匹配
    };
    
    // 流统计
    struct StreamStats {
        uint64_t sessions;            // 会话数
        uint64_t expired;             // 过期会话
        uint64_t created;             // 创建会话
        uint64_t memory;              // 内存使用
    };
    
    // 获取所有统计
    static void get_all(PacketStats&, ProtoStats&, DetectStats&, StreamStats&);
    
    // 打印统计
    static void print();
    
    // 重置统计
    static void reset();
};
```

---

## 附录ER： 配置验证 {#附录er-配置验证}

### ER.1 配置文件检查 {#er-1-配置文件检查}

```cpp
// main/config_validation.h

class ConfigValidator {
public:
    // 验证配置
    static bool validate(const SnortConfig*);
    
    // 验证规则
    static bool validate_rules(const SnortConfig*);
    
    // 验证检测器
    static bool validate_inspectors(const SnortConfig*);
    
    // 验证动作
    static bool validate_actions(const SnortConfig*);
    
    // 验证网络配置
    static bool validate_network(const SnortConfig*);
    
    // 检查端口冲突
    static bool check_port_conflicts(const SnortConfig*);
    
    // 检查规则冲突
    static bool check_rule_conflicts(const SnortConfig*);
    
private:
    static bool validate_binding(const InspectorBinding*);
    static bool validate_wizard(const WizardConfig*);
    static bool validate_binder(const BinderConfig*);
};
```

---

## 附录ES： 性能分析工具 {#附录es-性能分析工具}

### ES.1 Profiler使用 {#es-1-profiler使用}

```cpp
// profiler/perf_counters.h

// 性能计数器宏
#define PERF_START(name) \
    do { \
        if (perf_enabled) { \
            perf_start(name); \
        } \
    } while(0)

#define PERF_END(name) \
    do { \
        if (perf_enabled) { \
            perf_end(name); \
        } \
    } while(0)

// 性能统计输出
void perf_print(ProfileStats* stats) {
    printf("Module: %s\n", stats->name);
    printf("  Calls: %lu\n", stats->calls);
    printf("  Total Ticks: %lu\n", stats->ticks);
    printf("  Elapsed Time: %lu ms\n", stats->elapsed);
    printf("  Avg Time: %lu ns\n", stats->ticks / stats->calls);
    printf("  %% of Total: %.2f%%\n", stats->pct_of_total);
}

// 分析报告生成
void perf_report() {
    ProfileStats* root = get_root_stats();
    print_profile_tree(root, 0);
}
```

---

## 附录ET： 编译配置 {#附录et-编译配置}

### ET.1 构建系统 {#et-1-构建系统}

```cmake
# CMakeLists.txt 示例

# 最小版本
cmake_minimum_required(VERSION 3.10)

# 项目名称
project(Snort3)

# C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 编译选项
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_compile_options(-g -O0 -DDEBUG)
else()
    add_compile_options(-O3 -DNDEBUG)
endif()

# 警告
add_compile_options(-Wall -Wextra -Wpedantic)

# 查找依赖
find_package(Threads REQUIRED)
find_package(DAQ REQUIRED)

# 子目录
add_subdirectory(src/framework)
add_subdirectory(src/codecs)
add_subdirectory(src/detection)
add_subdirectory(src/stream)
add_subdirectory(src/service_inspectors)

# 插件目录
add_subdirectory/plugins)
```

---

## 附录EU： 调试技术 {#附录eu-调试技术}

### EU.1 GDB调试 {#eu-1-gdb调试}

```bash
# 启动调试
gdb --args ./snort -c snort.lua -i eth0

# 设置断点
(gdb) break TcpSession::process
(gdb) break HttpInspector::eval
(gdb) break detection_engine::detect

# 查看变量
(gdb) print *p
(gdb) print *flow
(gdb) print this->state

# 条件断点
(gdb) break TcpSession::process if flow->service == 0

# 单步执行
(gdb) next
(gdb) step
(gdb) continue

# 堆栈跟踪
(gdb) bt
(gdb) frame 3

# 查看内存
(gdb) x/100x pkt->data
(gdb) x/s pkt->data

# 线程
(gdb) info threads
(gdb) thread 2
```

### EU.2 Valgrind内存检测 {#eu-2-valgrind内存检测}

```bash
# 内存泄漏检测
valgrind --leak-check=full ./snort -c snort.lua -i eth0

# 性能分析
valgrind --tool=callgrind ./snort -c snort.lua -i eth0
kcachegrind callgrind.out.*

# 线程检查
valgrind --tool=helgrind ./snort -c snort.lua -i eth0
```

---

## 附录EV： 常用命令选项 {#附录ev-常用命令选项}

### EV.1 Snort命令行 {#ev-1-snort命令行}

```bash
# 基本运行
snort -c snort.lua -i eth0

# 详细输出
snort -c snort.lua -i eth0 -v

# 报警模式
snort -c snort.lua -i eth0 -A alert    # 标准报警
snort -c snort.lua -i eth0 -A cmg     # 完全报警
snort -c snort.lua -i eth0 -A fast    # 快速报警
snort -c snort.lua -i eth0 -A none    # 无报警

# 内联模式
snort -c snort.lua -i eth0 -Q --enable-inline

# 规则调试
snort -c snort.lua -i eth0 --rule-profile
snort -c snort.lua -i eth0 --rule-profiling

# 性能分析
snort -c snort.lua -i eth0 --profile-rules
snort -c snort.lua -i eth0 --profile-modules

# 统计信息
snort -c snort.lua -i eth0 --stat

# 只读取pcap
snort -c snort.lua -r capture.pcap

# 输出到文件
snort -c snort.lua -i eth0 -L pcap -l /var/log/snort
```

---

## 附录EW： 规则语法 {#附录ew-规则语法}

### EW.1 规则格式 {#ew-1-规则格式}

```bash
# 基本格式
<action> <protocol> <source> <source_port> <direction> <dest> <dest_port> (msg:"<message>"; content:"<pattern>"; sid:<id>;)

# 动作
alert    # 报警并记录
log      # 仅记录
pass     # 忽略
drop     # 丢弃并记录
reject   # 拒绝并记录
sdrop    # 静默丢弃

# 协议
tcp, udp, icmp, ip, http, ftp, smtp, etc.

# 方向
->  # 从源到目标
<>  # 双向

# 例子
alert tcp any any -> any 80 (msg:"HTTP Request"; content:"GET"; http_method; sid:1000001;)
alert tcp any any -> any 443 (msg:"HTTPS Traffic"; ssl_state; sid:1000002;)
alert icmp any any -> any any (msg:"ICMP Ping"; icmp_type:8; sid:1000003;)
```

### EW.2 规则选项 {#ew-2-规则选项}

```bash
# 内容匹配
content:"pattern";           # 原始内容
content:"pattern"; nocase;   # 不区分大小写
content:"pattern"; offset:10;  # 偏移
content:"pattern"; depth:20;    # 深度
content:"pattern"; distance:5;  # 距离
content:"pattern"; within:30;   # 范围内

# 正则表达式
pcre:"/regex/is";           # 正则匹配

# 协议字段
http_method;    # HTTP方法
http_uri;       # HTTP URI
http_header;    # HTTP头部
http_cookie;    # HTTP cookie
http_body;      # HTTP body

# 流匹配
flow:established;        # 已建立的流
flow:to_server;          # 到服务器
flow:from_client;         # 从客户端

# 文件和MIME
file_data;        # 文件数据
base64_decode;    # Base64解码
base64_content;   # Base64内容

# 字节操作
byte_test:4,=,0x1234;    # 字节测试
byte_jump:2,0;           # 字节跳转
```

---

*文档版本: 12.0*
*更新日期: 2026年4月10日*
*总行数: 9500+*


---
