# Snort3 内存管理、性能分析与目标策略

这三个模块提供了Snort3运行时的资源管理、性能监控和基于目标的主机策略能力。

## 1. 内存管理 (Memory)

### 1.1 MemoryCap 类

内存容量管理器,控制Snort的内存使用:

```cpp
class SO_PUBLIC MemoryCap
{
public:
    // 主线程函数
    static void init(unsigned num_threads);
    static void term();

    // 配置阶段 - 主线程
    static void set_heap_interface(HeapInterface*);
    static void set_pruner(PruneHandler);

    // 配置后 - 主线程
    static void start(const MemoryConfig&, PruneHandler);
    static void stop();
    static void print(bool verbose, bool init = false);

    // 数据包线程
    static void thread_init();
    static void thread_term();
    static void free_space();

    // 主线程和数据包线程
    static MemoryCounts& get_mem_stats();
    static void update_global_stats();

    // 关闭时
    static void update_pegs(PegCount*);

    static void dump_mem_stats(ControlConn*);
    static void heap_profile_config(bool enable, uint64_t sample_rate);
    static void dump_heap_profile(ControlConn*);
    static void show_heap_profile_config(ControlConn*);
};
```

### 1.2 内存统计

```cpp
struct MemoryCounts
{
    PegCount start_up_use;      // 启动时内存使用
    PegCount cur_in_use;        // 当前内存使用
    PegCount max_in_use;        // 峰值内存使用
    PegCount epochs;            // 内存周期数
    PegCount allocated;         // 分配次数
    PegCount deallocated;       // 释放次数
    PegCount reap_cycles;       // 回收周期
    PegCount reap_attempts;     // 回收尝试
    PegCount reap_failures;     // 回收失败
    PegCount reap_aborts;       // 回收中止
    PegCount reap_decrease;     // 回收减少量
    PegCount reap_increase;     // 回收增加量
    // 仅报告用
    PegCount app_all;           // 应用分配
    PegCount active;            // 活跃内存
    PegCount resident;          // 常驻内存
    PegCount retained;          // 保留内存
};
```

### 1.3 HeapInterface 接口

内存分配器需要实现此接口:

```cpp
class HeapInterface
{
public:
    virtual ~HeapInterface() { }

    virtual void main_init() = 0;
    virtual void thread_init() = 0;

    virtual void get_process_total(uint64_t& epoch, uint64_t& total,
        bool bump_epoch = true) = 0;
    virtual void get_thread_allocs(uint64_t& alloc, uint64_t& dealloc) = 0;

    virtual void print_stats(ControlConn*) { }
    virtual void get_aux_counts(uint64_t& app_all, uint64_t& active,
        uint64_t& resident, uint64_t& retained)
    { app_all = active = resident = retained = 0; }

    virtual void profile_config(bool, uint64_t) { }
    virtual void dump_profile(ControlConn*) { }
    virtual void show_profile_config(ControlConn*) { }

    static HeapInterface* get_instance();

protected:
    HeapInterface() { }
};
```

### 1.4 内存配置

```cpp
struct MemoryConfig
{
    unsigned num_threads;          // 线程数
    size_t max_capacity;           // 最大容量
    size_t per_thread_capacity;    // 每线程容量
    unsigned soft_memory_cap;       // 软上限
    unsigned hard_memory_cap;      // 硬上限
    unsigned min_free_per_thread;   // 每线程最小空闲
};
```

### 1.5 内存分配重载

`memory_overloads.h` 提供了operator new/delete的重载:

```cpp
void* operator new(std::size_t);
void* operator new[](std::size_t);
void* operator new(std::size_t, const std::nothrow_t&) noexcept;
void* operator new[](std::size_t, const std::nothrow_t&) noexcept;
void operator delete(void*) noexcept;
void operator delete[](void*) noexcept;
void operator delete(void*, std::nothrow_t&) noexcept;
void operator delete[](void*, std::nothrow_t&) noexcept;
void operator delete(void*, std::size_t) noexcept;
void operator delete[](void*, std::size_t) noexcept;
```

## 2. 性能分析 (Profiler)

### 2.1 Profiler 类

```cpp
class SO_PUBLIC Profiler
{
public:
    static void setup(SnortConfig*);
    static void clear(SnortConfig*);
    static void register_module(ProfilerNodeMap&, Module*);
    static void register_module(ProfilerNodeMap&, const char*, const char*, Module*);

    static ProfileStats* get_total_perf_stats();
    static ProfileStats* get_other_perf_stats();
    static void reset();
    static void show();
    static void compute();
    static void dump();
    static void smooth();

private:
    static void process_profile(Module*, ProfileStats&);
    static void consolidate(ProfilerNodeMap&, ProfileStats&);
};
```

### 2.2 ProfileStats 结构

```cpp
struct SO_PUBLIC ProfileStats
{
    TimeProfilerStats time;
    MemoryTracker memory;

    void reset()
    {
        time.reset();
        memory.reset();
    }

    void reset_time()
    { time.reset(); }

    bool operator==(const ProfileStats&) const;
    bool operator!=(const ProfileStats& rhs) const
    { return !(*this == rhs); }

    ProfileStats& operator+=(const ProfileStats&);
    ProfileStats& operator+=(const TimeProfilerStats&);
    ProfileStats& operator+=(const MemoryTracker&);
};
```

### 2.3 TimeProfilerStats

时间性能分析统计:

```cpp
struct SO_PUBLIC TimeProfilerStats
{
    hr_duration elapsed;      // 总耗时
    uint64_t checks;          // 检查次数
    mutable unsigned int ref_count;  // 引用计数

    void update(hr_duration delta)
    { elapsed += delta; ++checks; }

    void reset()
    { elapsed = 0_ticks; checks = 0; }

    bool is_active() const
    { return ( elapsed > CLOCK_ZERO ) || checks; }

    // 重入控制
    bool enter() const { return ref_count++ == 0; }
    bool exit() const { return --ref_count == 0; }
};
```

### 2.4 TimeProfilerConfig

```cpp
struct TimeProfilerConfig
{
    enum Sort
    {
        SORT_NONE = 0,
        SORT_CHECKS,       // 按检查次数排序
        SORT_AVG_CHECK,    // 按平均检查时间排序
        SORT_TOTAL_TIME    // 按总时间排序
    } sort = SORT_TOTAL_TIME;

    bool show = false;
    unsigned count = 0;
    int max_depth = -1;
};
```

### 2.5 ProfilerContext

```cpp
class TimeContext
{
public:
    TimeContext(ProfileStats&);
    ~TimeContext();

    void stop();
    void start();

private:
    hr_stopwatch sw;
    ProfileStats& stats;
    bool stopped;
};

class ProfileContext
{
public:
    ProfileContext(ProfileStats& ps) : stats(ps)
    { if (stats.time.enter()) stats.time.is_enabled() = true; }

    ~ProfileContext()
    { if (stats.time.exit()) stats.time.set_enabled(false); }

private:
    ProfileStats& stats;
};
```

### 2.6 RuleProfiler

规则性能分析:

```cpp
struct RuleProfilerConfig
{
    enum Sort
    {
        SORT_NONE = 0,
        SORT_CHECKS,
        SORT_MATCHES,
        SORT_NO_MATCHES,
        SORT_AVG_Ticks,
        SORT_TOTAL_Ticks
    } sort = SORT_TOTAL_TICKS;

    bool show = false;
    unsigned count = 0;
};
```

### 2.7 MemoryProfiler

内存性能分析:

```cpp
struct MemoryProfilerConfig
{
    bool show = false;
    int max_nodes = -1;
};

class MemoryTracker
{
public:
    void reset();
    void update(uint64_t mem, bool overwrite = false);

private:
    MemoryTrackerStats stats;
};
```

### 2.8 ProfilerNodes

```cpp
class ProfilerNode
{
public:
    const char* name;
    const char* parent_name;
    Module* module;
    ProfileStats stats;
    unsigned level;

    void reset();
    void aggregate(const ProfilerNode&);
};

class ProfilerNodeMap
{
public:
    void add(const char* name, const char* parent, Module*,
        unsigned level = 0);
    ProfilerNode* find(const char* name);

    void reset();
    void aggregate();

private:
    std::map<std::string, ProfilerNode*> nodes;
};
```

## 3. 目标策略 (Target Based)

### 3.1 协议引用

```cpp
using SnortProtocolId = uint16_t;

// 预定义协议
enum SnortProtocols : SnortProtocolId
{
    SNORT_PROTO_IP = 1,
    SNORT_PROTO_ICMP,
    SNORT_PROTO_TCP,
    SNORT_PROTO_UDP,
    SNORT_PROTO_FILE,
    SNORT_PROTO_MAX
};

constexpr SnortProtocolId UNKNOWN_PROTOCOL_ID = 0;
constexpr SnortProtocolId INVALID_PROTOCOL_ID = 0xffff;

// 辅助函数
inline bool is_network_protocol(SnortProtocolId proto)
{ return (proto >= SNORT_PROTO_IP and proto <= SNORT_PROTO_UDP); }

inline bool is_builtin_protocol(SnortProtocolId proto)
{ return proto < SNORT_PROTO_MAX; }

inline bool is_service_protocol(SnortProtocolId proto)
{ return proto > SNORT_PROTO_UDP; }
```

### 3.2 ProtocolReference 类

```cpp
class SO_PUBLIC ProtocolReference
{
public:
    ProtocolReference();
    ~ProtocolReference();

    SnortProtocolId get_count() const;
    const char* get_name(SnortProtocolId id) const;
    const char* get_name_sorted(SnortProtocolId id);

    SnortProtocolId add(const char* protocol);
    SnortProtocolId find(const char* protocol) const;

private:
    std::vector<const char*> id_map;
    std::vector<SnortProtocolId> ind_map;
    std::unordered_map<std::string, SnortProtocolId> ref_table;
    SnortProtocolId protocol_number = 0;
};
```

### 3.3 HostAttributesDescriptor

主机属性描述符:

```cpp
class HostServiceDescriptor
{
public:
    HostServiceDescriptor() = default;
    HostServiceDescriptor(uint16_t port, uint16_t protocol,
        SnortProtocolId spi, bool appid_service)
        : port(port), ipproto(protocol),
          snort_protocol_id(spi), appid_service(appid_service)
    { }

    uint16_t port = 0;
    uint16_t ipproto = 0;
    SnortProtocolId snort_protocol_id = UNKNOWN_PROTOCOL_ID;
    bool appid_service = false;
};

struct HostPolicyDescriptor
{
    uint8_t streamPolicy = 0;
    uint8_t fragPolicy = 0;
};

class HostAttributesDescriptor
{
public:
    bool update_service(uint16_t port, uint16_t protocol,
        SnortProtocolId, bool& updated, bool is_appid_service = false);
    void clear_appid_services();
    void get_host_attributes(uint16_t protocol, uint16_t port,
        HostAttriInfo*) const;
};
```

### 3.4 主机属性统计

```cpp
struct HostAttributeStats
{
    PegCount total_hosts = 0;
    PegCount hosts_pruned = 0;
    PegCount dynamic_host_adds = 0;
    PegCount dynamic_service_adds = 0;
    PegCount dynamic_service_updates = 0;
    PegCount service_list_overflows = 0;
};
```

### 3.5 LRU缓存

主机属性使用分段LRU缓存:

```cpp
typedef HostLruSegmentedCache<
    snort::SfIp,
    HostAttributesDescriptor,
    HostAttributesCacheKey> HostAttributesSegmentedCache;
```

### 3.6 HostAttributesManager

```cpp
class HostAttributesManager
{
public:
    static void initialize();
    static void terminate();

    static void configure(SnortConfig*);
    static void show();

    static void add_host(const char* hostIP);
    static void set_service(const SfIp*, uint16_t port, uint16_t proto,
        SnortProtocolId, bool is_appid_service);

    static bool get_host_attributes(const SfIp*, uint16_t protocol,
        uint16_t port, HostAttriInfo*);

    static void dump_cache();
    static void update_stats();
    static void release_resources();

private:
    static void load_hosts_file(const char* path);
    static void load_services_file(const char* path);
};
```

## 4. 文件清单

### Memory 模块

| 文件 | 行数 | 描述 |
|------|------|------|
| `memory_cap.h` | ~100 | MemoryCap类定义 |
| `memory_cap.cc` | ~300 | MemoryCap实现 |
| `memory_config.h` | ~50 | 内存配置 |
| `memory_module.cc` | ~150 | 配置模块 |
| `memory_overloads.h` | ~50 | new/delete重载 |
| `memory_overloads.cc` | ~350 | 重载实现 |
| `heap_interface.h` | ~60 | 堆接口定义 |
| `heap_interface.cc` | ~200 | 堆接口实现 |
| `memory_allocator.h/cc` | ~50 | 内存分配器 |

### Profiler 模块

| 文件 | 行数 | 描述 |
|------|------|------|
| `profiler.h` | ~30 | 主头文件 |
| `profiler.cc` | ~250 | 主实现 |
| `profiler_defs.h` | ~100 | 定义 |
| `profiler_impl.h` | ~70 | 实现接口 |
| `profiler_nodes.h` | ~100 | 性能节点 |
| `profiler_nodes.cc` | ~700 | 节点实现 |
| `profiler_module.cc` | ~500 | 模块 |
| `profiler_printer.h` | ~150 | 打印接口 |
| `time_profiler.h` | ~30 | 时间分析 |
| `time_profiler.cc` | ~500 | 时间分析实现 |
| `time_profiler_defs.h` | ~150 | 时间定义 |
| `rule_profiler.h` | ~100 | 规则分析 |
| `rule_profiler.cc` | ~600 | 规则分析实现 |
| `rule_profiler_defs.h` | ~100 | 规则定义 |
| `memory_profiler.h` | ~30 | 内存分析 |
| `memory_profiler.cc` | ~350 | 内存分析实现 |
| `memory_profiler_defs.h` | ~70 | 内存定义 |
| `memory_context.h` | ~50 | 内存上下文 |
| `memory_context.cc` | ~130 | 上下文实现 |

### Target Based 模块

| 文件 | 行数 | 描述 |
|------|------|------|
| `host_attributes.h` | ~150 | 主机属性 |
| `host_attributes.cc` | ~300 | 主机属性实现 |
| `snort_protocols.h` | ~100 | 协议引用 |
| `snort_protocols.cc` | ~130 | 协议实现 |
| `active_context.h` | ~60 | 活跃上下文 |
| `json_view.cc` | ~120 | JSON视图 |
| `table_view.cc` | ~150 | 表格视图 |

## 5. 架构关系

```
┌─────────────────────────────────────────────────────────────┐
│                      Snort3 Core                             │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│      Memory       │ │     Profiler      │ │   Target Based    │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
│  │ MemoryCap  │  │ │  │   Time     │  │ │  │  Protocol   │  │
│  │HeapInterface│ │ │  │  Profiler  │  │ │  │  Reference  │  │
│  └────────────┘  │ │  └────────────┘  │ │  └────────────┘  │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
│  │  Memory    │  │ │  │   Rule     │  │ │  │   Host     │  │
│  │ Overloads  │  │ │  │  Profiler  │  │ │  │ Attributes │  │
│  └────────────┘  │ │  └────────────┘  │ │  └────────────┘  │
│  ┌────────────┐  │ │  ┌────────────┐  │ │                  │
│  │  Memory    │  │ │  │  Memory    │  │ │                  │
│  │  Tracker   │  │ │  │  Profiler  │  │ │                  │
│  └────────────┘  │ │  └────────────┘  │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

## 6. 使用示例

### 6.1 配置内存限制

```cpp
// 配置内存限制
config hard_memory_cap: 4096
config soft_memory_cap: 2048
config per_thread_memory_cap: 256
```

### 6.2 启用性能分析

```cpp
// 启用时间性能分析
config profile_rules: print 10, sort total_ticks

// 启用内存性能分析
config profile_memory: show max_depth
```

### 6.3 使用ProfileContext

```cpp
void some_function()
{
    THREAD_LOCAL ProfileStats perfStats;
    ProfileContext context(perfStats);

    // 函数体
    // ...
} // 退出时自动更新性能统计
```

### 6.4 主机属性配置

```
# 定义主机属性文件
config attribute_table: filename /path/to/host_attrs.rules

# host_attrs.rules格式
host 192.168.1.100 services http:80/tcp, https:443/tcp
host 192.168.1.200 services ssh:22/tcp
```

## 7. 总结

这三个模块提供了Snort3的运行时支持:

1. **Memory模块**:
   - 控制内存使用量
   - 提供内存分配统计
   - 支持自定义堆接口
   - LRU缓存管理

2. **Profiler模块**:
   - 时间性能分析
   - 规则性能分析
   - 内存使用分析
   - 层次化性能数据

3. **Target Based模块**:
   - 协议ID管理
   - 主机属性存储
   - 服务识别
   - 基于主机的策略

这些模块共同支持Snort3的企业级部署和性能调优需求。
