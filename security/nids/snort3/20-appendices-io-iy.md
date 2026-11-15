---
title: "Snort 3 · 附录 IO–IY"
description: "附录IO： 定时器实现 — 附录IY： 日志记录系统"
---

# Snort 3 · 附录 IO–IY

[返回总目录](../snort3_architecture_analysis)

## 附录IO： 定时器实现 {#附录io-定时器实现}

### IO.1 最小堆定时器 {#io-1-最小堆定时器}

```cpp
// utils/timer_heap.h

class TimerHeap {
public:
    struct Timer {
        uint64_t expires;      // 到期时间
        std::function<void()> callback;
        bool periodic;        // 是否周期定时器
        uint64_t interval;    // 周期间隔
        
        bool operator<(const Timer& other) const {
            return expires > other.expires;  // 最小堆
        }
    };
    
    void add(uint64_t after_ms, std::function<void()> cb, 
             bool periodic = false, uint64_t interval = 0) {
        Timer timer;
        timer.expires = get_time_ms() + after_ms;
        timer.callback = std::move(cb);
        timer.periodic = periodic;
        timer.interval = interval;
        
        heap_.push(timer);
    }
    
    // 执行到期的定时器
    void execute() {
        uint64_t now = get_time_ms();
        
        while (!heap_.empty() && heap_.top().expires <= now) {
            Timer timer = heap_.top();
            heap_.pop();
            
            timer.callback();
            
            if (timer.periodic) {
                timer.expires = now + timer.interval;
                heap_.push(timer);
            }
        }
    }
    
    // 获取下次到期时间
    uint64_t next_expiry() const {
        return heap_.empty() ? UINT64_MAX : heap_.top().expires;
    }
    
private:
    std::vector<Timer> heap_;
    
    static uint64_t get_time_ms() {
        struct timeval tv;
        gettimeofday(&tv, nullptr);
        return (uint64_t)tv.tv_sec * 1000 + tv.tv_usec / 1000;
    }
};
```

---

## 附录IP： 缓存实现 {#附录ip-缓存实现}

### IP.1 LRU缓存 {#ip-1-lru缓存}

```cpp
// utils/lru_cache.h

template<typename K, typename V>
class LRUCache {
public:
    explicit LRUCache(size_t capacity) : capacity_(capacity) {}
    
    void put(const K& key, const V& value) {
        auto it = cache_.find(key);
        if (it != cache_.end()) {
            // 更新存在的项
            it->second->second = value;
            move_to_front(it->second);
            return;
        }
        
        // 新项
        if (cache_.size() >= capacity_) {
            // 删除最旧的
            cache_.erase(end_->second.first);
            if (end_)
                end_ = end_->prev;
        }
        
        auto* node = new Node{key, value, front_, nullptr};
        if (front_)
            front_->prev = node;
        front_ = node;
        if (!end_)
            end_ = node;
        
        cache_[key] = node;
    }
    
    V* get(const K& key) {
        auto it = cache_.find(key);
        if (it == cache_.end())
            return nullptr;
        
        move_to_front(it->second);
        return &it->second->second;
    }
    
private:
    struct Node {
        K first;
        V second;
        Node* prev;
        Node* next;
    };
    
    void move_to_front(Node* node) {
        if (node == front_)
            return;
        
        // 从当前位置移除
        if (node->prev)
            node->prev->next = node->next;
        if (node->next)
            node->next->prev = node->prev;
        if (node == end_)
            end_ = node->prev;
        
        // 移到front
        node->prev = nullptr;
        node->next = front_;
        if (front_)
            front_->prev = node;
        front_ = node;
        
        if (!end_)
            end_ = node;
    }
    
    size_t capacity_;
    std::unordered_map<K, Node*> cache_;
    Node* front_ = nullptr;
    Node* end_ = nullptr;
};
```

---

## 附录IQ： 序列化框架 {#附录iq-序列化框架}

### IQ.1 简单二进制序列化 {#iq-1-简单二进制序列化}

```cpp
// utils/serializer.h

class Serializer {
public:
    // 添加各种类型
    void add_uint8(uint8_t v) { buf_.push_back(v); }
    void add_uint16(uint16_t v) { 
        buf_.push_back(v & 0xFF);
        buf_.push_back((v >> 8) & 0xFF);
    }
    void add_uint32(uint32_t v) {
        for (int i = 0; i < 4; i++)
            buf_.push_back((v >> (i * 8)) & 0xFF);
    }
    void add_bytes(const uint8_t* data, size_t len) {
        buf_.insert(buf_.end(), data, data + len);
    }
    
    const std::vector<uint8_t>& data() const { return buf_; }
    size_t size() const { return buf_.size(); }
    void clear() { buf_.clear(); }
    
private:
    std::vector<uint8_t> buf_;
};

class Deserializer {
public:
    explicit Deserializer(const uint8_t* data, size_t len) 
        : data_(data), len_(len), pos_(0) {}
    
    uint8_t get_uint8() {
        return data_[pos_++];
    }
    
    uint16_t get_uint16() {
        uint16_t v = data_[pos_] | (data_[pos_ + 1] << 8);
        pos_ += 2;
        return v;
    }
    
    uint32_t get_uint32() {
        uint32_t v = 0;
        for (int i = 0; i < 4; i++)
            v |= (uint32_t)data_[pos_ + i] << (i * 8);
        pos_ += 4;
        return v;
    }
    
    void get_bytes(uint8_t* out, size_t len) {
        memcpy(out, data_ + pos_, len);
        pos_ += len;
    }
    
    bool ok() const { return pos_ <= len_; }
    size_t pos() const { return pos_; }
    
private:
    const uint8_t* data_;
    size_t len_;
    size_t pos_;
};
```

---

## 附录IR： 插件接口定义 {#附录ir-插件接口定义}

### IR.1 插件类型 {#ir-1-插件类型}

```cpp
// framework/plugin.h

// 插件类型枚举
enum class PluginType : uint8_t {
    INSPECTOR = 0,     // 数据包检查器
    CODEC = 1,         // 协议编解码器
    IPS_OPTION = 2,    // IPS规则选项
    LOGGER = 3,        // 日志输出
    ACTION = 4,        // 检测动作
    SEARCH_ENGINE = 5, // 搜索引擎
    MPSE = 6          // 多模式搜索引擎
};

// 插件基础API
struct BaseApi {
    PluginType type;           // 插件类型
    uint32_t api_version;     // API版本
    uint32_t plugin_version;   // 插件版本
    const char* name;         // 插件名称
    const char* help;         // 帮助信息
};

// Inspector插件API
struct InspectApi : BaseApi {
    InspectorType itype;       // Inspector类型
    uint32_t proto_bits;      // 支持的协议
    void* buffers;            // 缓冲区
    const char* service;      // 服务类型
    
    // 构造函数和析构函数
    Inspector* (*ctor)(Module*);
    void (*dtor)(Inspector*);
    
    // 会话回调
    Session* (*ssn)(Flow*);
    void (*reset)(Flow*);
};
```

### IR.2 插件加载 {#ir-2-插件加载}

```cpp
// managers/plugin_manager.cc

void PluginManager::load_plugin(const char* path) {
    // 加载动态库
    void* handle = dlopen(path, RTLD_NOW);
    if (!handle) {
        ErrorMessage("Failed to load plugin: %s\n", dlerror());
        return;
    }
    
    // 获取插件API
    const char* sym = "snort_plugins";
    const BaseApi** api = reinterpret_cast<const BaseApi**>(
        dlsym(handle, sym));
    
    if (!api || !*api) {
        ErrorMessage("Invalid plugin API: %s\n", path);
        dlclose(handle);
        return;
    }
    
    // 注册插件
    for (int i = 0; api[i]; i++) {
        PluginInfo info;
        info.api = api[i];
        info.handle = handle;
        
        plugins_[{info.api->type, info.api->name}] = info;
        
        DebugMessage("Loaded plugin: %s (%s)\n", 
                    info.api->name, 
                    plugin_type_name(info.api->type));
    }
}

Inspector* PluginManager::create_inspector(
    PluginType type, const char* name, Module* mod) {
    
    auto key = std::make_pair(type, name);
    auto it = plugins_.find(key);
    
    if (it == plugins_.end())
        return nullptr;
    
    const InspectApi* api = 
        reinterpret_cast<const InspectApi*>(it->second.api);
    
    return api->ctor(mod);
}
```

---

## 附录IS： 单元测试框架 {#附录is-单元测试框架}

### IS.1 简单测试框架 {#is-1-简单测试框架}

```cpp
// testing/test.h

#define TEST_ASSERT_TRUE(cond) \
    if (!(cond)) { \
        printf("FAIL: %s:%d: %s\n", __FILE__, __LINE__, #cond); \
        return false; \
    }

#define TEST_ASSERT_FALSE(cond) \
    TEST_ASSERT_TRUE(!(cond))

#define TEST_ASSERT_EQ(a, b) \
    if ((a) != (b)) { \
        printf("FAIL: %s:%d: %s == %s (%ld != %ld)\n", \
               __FILE__, __LINE__, #a, #b, (long)(a), (long)(b)); \
        return false; \
    }

#define TEST_ASSERT_NE(a, b) \
    if ((a) == (b)) { \
        printf("FAIL: %s:%d: %s != %s\n", \
               __FILE__, __LINE__, #a, #b); \
        return false; \
    }

#define TEST_ASSERT_STREQ(a, b) \
    if (strcmp(a, b) != 0) { \
        printf("FAIL: %s:%d: %s == %s (\"%s\" != \"%s\")\n", \
               __FILE__, __LINE__, #a, #b, a, b); \
        return false; \
    }

// 测试套件
class TestSuite {
public:
    virtual ~TestSuite() = default;
    virtual const char* name() const = 0;
    virtual bool run() = 0;
    
    int passed() const { return passed_; }
    int failed() const { return failed_; }
    
protected:
    int passed_ = 0;
    int failed_ = 0;
};

// 测试运行器
class TestRunner {
public:
    void add(TestSuite* suite) {
        suites_.push_back(suite);
    }
    
    int run_all() {
        int total_passed = 0;
        int total_failed = 0;
        
        for (auto* suite : suites_) {
            printf("Running %s...\n", suite->name());
            if (suite->run()) {
                total_passed += suite->passed();
                total_failed += suite->failed();
            } else {
                total_failed += suite->passed() + suite->failed();
            }
        }
        
        printf("\n=== Results ===\n");
        printf("Passed: %d\n", total_passed);
        printf("Failed: %d\n", total_failed);
        
        return total_failed;
    }
    
private:
    std::vector<TestSuite*> suites_;
};

// 测试套件示例
class PacketTestSuite : public TestSuite {
public:
    const char* name() const override { return "Packet"; }
    
    bool run() override {
        RUN_TEST(TestPacketDecode);
        RUN_TEST(TestPacketFlow);
        RUN_TEST(TestPacketFlags);
        return true;
    }
    
    bool TestPacketDecode() {
        uint8_t raw[] = { /* ... */ };
        Packet p;
        // ...
        TEST_ASSERT_EQ(p.type, PktType::TCP);
        return true;
    }
};

#define RUN_TEST(t) \
    do { \
        printf("  %s...", #t); \
        if (t()) { \
            printf("PASS\n"); \
            passed_++; \
        } else { \
            printf("FAIL\n"); \
            failed_++; \
        } \
    } while(0)
```

---

## 附录IT： 基准测试框架 {#附录it-基准测试框架}

### IT.1 性能基准 {#it-1-性能基准}

```cpp
// testing/benchmark.h

class Benchmark {
public:
    struct Result {
        double ops_per_sec;
        double avg_ns_per_op;
        double stddev;
        double min;
        double max;
    };
    
    // 运行基准测试
    template<typename Func>
    Result run(const char* name, Func f, int iterations = 1000000) {
        std::vector<double> times;
        times.reserve(iterations);
        
        // 预热
        for (int i = 0; i < 1000; i++)
            f();
        
        // 计时
        for (int i = 0; i < iterations; i++) {
            uint64_t start = get_cycles();
            f();
            uint64_t end = get_cycles();
            times.push_back(end - start);
        }
        
        // 计算统计
        Result r;
        double sum = 0, sum_sq = 0;
        r.min = times[0];
        r.max = times[0];
        
        for (double t : times) {
            sum += t;
            sum_sq += t * t;
            r.min = std::min(r.min, t);
            r.max = std::max(r.max, t);
        }
        
        double mean = sum / times.size();
        r.avg_ns_per_op = mean / cpu_freq_ghz_;
        r.ops_per_sec = 1.0 / (r.avg_ns_per_op / 1e9);
        r.stddev = sqrt(sum_sq / times.size() - mean * mean);
        
        printf("%s: %.2f Mops/s (%.2f ns/op)\n", 
               name, r.ops_per_sec / 1e6, r.avg_ns_per_op);
        
        return r;
    }
    
private:
    static uint64_t get_cycles() {
        uint32_t lo, hi;
        __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
        return ((uint64_t)hi << 32) | lo;
    }
    
    double cpu_freq_ghz_ = 3.0;  // 需要校准
};

// 使用
void benchmark_ac_search() {
    Benchmark bench;
    
    bench.run("AC search (short pattern)", []() {
        ac_search(text, text_len, patterns, num_patterns);
    });
    
    bench.run("AC search (long pattern)", []() {
        ac_search(text_long, text_len_long, patterns_long, num_patterns_long);
    });
}
```

---

## 附录IU： 集成测试 {#附录iu-集成测试}

### IU.1 端到端测试 {#iu-1-端到端测试}

```cpp
// testing/integration_test.h

class IntegrationTest {
public:
    IntegrationTest() {
        // 创建测试配置
        config_ = new SnortConfig();
        config_->setup_test();
    }
    
    ~IntegrationTest() {
        delete config_;
    }
    
    // 运行数据包
    bool send_packet(const uint8_t* raw, size_t len) {
        Packet p;
        p.decode(raw, len);
        
        // 处理数据包
        InspectorManager::process(&p);
        
        return true;
    }
    
    // 发送原始数据
    bool send_raw(uint32_t src_ip, uint16_t src_port,
                  uint32_t dst_ip, uint16_t dst_port,
                  const uint8_t* data, size_t len) {
        // 构建数据包
        uint8_t pkt[1024];
        // ... 构建TCP/IP头 ...
        
        return send_packet(pkt, constructed_len);
    }
    
    // 发送HTTP请求
    bool send_http_request(const char* host, const char* path) {
        char req[1024];
        snprintf(req, sizeof(req),
            "GET %s HTTP/1.1\r\n"
            "Host: %s\r\n"
            "\r\n",
            path, host);
        
        return send_raw(0xC0A80101, 12345, 0xC0A80102, 80,
                       (uint8_t*)req, strlen(req));
    }
    
    // 检查告警
    bool has_alert(uint32_t gid, uint32_t sid) {
        // 检查告警队列
        return AlertQueue::has(gid, sid);
    }
    
    // 获取告警计数
    int get_alert_count(uint32_t gid, uint32_t sid) {
        return AlertQueue::count(gid, sid);
    }
    
private:
    SnortConfig* config_;
};

// 测试用例
void test_http_detection() {
    IntegrationTest test;
    
    // 发送正常HTTP请求
    test.send_http_request("example.com", "/");
    
    // 不应该有告警
    assert(test.get_alert_count(1, 1000001) == 0);
    
    // 发送恶意HTTP请求
    test.send_http_request("evil.com", "/exploit");
    
    // 应该有告警
    assert(test.get_alert_count(1, 1000002) == 1);
}
```

---

## 附录IV： 压力测试 {#附录iv-压力测试}

### IV.1 洪泛测试 {#iv-1-洪泛测试}

```cpp
// testing/flood_test.h

class FloodTest {
public:
    FloodTest(const char* target_ip, uint16_t port)
        : target_ip_(target_ip), port_(port) {}
    
    // TCP SYN洪泛
    void tcp_syn_flood(int duration_sec, int rate) {
        Socket sock;
        sock.create_tcp();
        sock.set_nonblocking();
        
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port_);
        inet_pton(AF_INET, target_ip_.c_str(), &addr.sin_addr);
        
        auto start = std::chrono::steady_clock::now();
        int sent = 0;
        
        while (std::chrono::steady_clock::now() - start 
               < std::chrono::seconds(duration_sec)) {
            connect(sock.fd(), (struct sockaddr*)&addr, sizeof(addr));
            sent++;
            
            if (sent % rate == 0)
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
        
        printf("TCP SYN flood: %d packets sent\n", sent);
    }
    
    // UDP洪泛
    void udp_flood(int duration_sec, int packet_size) {
        Socket sock;
        sock.create_udp();
        
        struct sockaddr_in addr;
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port_);
        inet_pton(AF_INET, target_ip_.c_str(), &addr.sin_addr);
        
        std::vector<uint8_t> payload(packet_size, 0xFF);
        
        auto start = std::chrono::steady_clock::now();
        int sent = 0;
        
        while (std::chrono::steady_clock::now() - start 
               < std::chrono::seconds(duration_sec)) {
            sendto(sock.fd(), payload.data(), payload.size(), 0,
                   (struct sockaddr*)&addr, sizeof(addr));
            sent++;
        }
        
        printf("UDP flood: %d packets sent\n", sent);
    }
    
private:
    std::string target_ip_;
    uint16_t port_;
};
```

---

## 附录IW： 模糊测试 {#附录iw-模糊测试}

### IW.1 协议模糊测试 {#iw-1-协议模糊测试}

```cpp
// testing/fuzz_test.h

class ProtocolFuzzer {
public:
    ProtocolFuzzer() : rng_(std::random_device{}()) {}
    
    // 模糊测试TCP协议
    void fuzz_tcp(uint32_t num_iterations) {
        for (uint32_t i = 0; i < num_iterations; i++) {
            // 生成随机TCP数据包
            std::vector<uint8_t> pkt = generate_random_tcp_packet();
            
            // 发送数据包
            Packet p;
            try {
                p.decode(pkt.data(), pkt.size());
                InspectorManager::process(&p);
            } catch (const std::exception& e) {
                printf("Crash at iteration %u: %s\n", i, e.what());
                save_crash_input(pkt);
            }
        }
    }
    
    // 生成随机TCP包
    std::vector<uint8_t> generate_random_tcp_packet() {
        std::vector<uint8_t> pkt(64 + rng_() % 128);
        
        // IP头
        pkt[0] = 0x45;  // IPv4, 20字节头
        // ... 更多IP字段 ...
        
        // TCP头
        uint16_t sport = rng_() % 65536;
        uint16_t dport = rng_() % 65536;
        // ... 设置TCP字段 ...
        
        // 随机载荷
        for (size_t i = 40; i < pkt.size(); i++)
            pkt[i] = rng_() & 0xFF;
        
        return pkt;
    }
    
    // 保存崩溃输入
    void save_crash_input(const std::vector<uint8_t>& pkt) {
        static int crash_num = 0;
        char filename[64];
        snprintf(filename, sizeof(filename), "crash_%d.bin", crash_num++);
        
        FILE* f = fopen(filename, "wb");
        fwrite(pkt.data(), 1, pkt.size(), f);
        fclose(f);
        
        printf("Crash input saved to %s\n", filename);
    }
    
private:
    std::mt19937 rng_;
};
```

---

## 附录IX： 配置验证 {#附录ix-配置验证}

### IX.1 配置检查器 {#ix-1-配置检查器}

```cpp
// config/config_validator.h

class ConfigValidator {
public:
    // 检查所有配置项
    bool validate(const SnortConfig* config) {
        bool ok = true;
        
        ok &= check_home_net(config);
        ok &= check_rules(config);
        ok &= check_inspectors(config);
        ok &= check_actions(config);
        ok &= check_network_config(config);
        ok &= check_performance_settings(config);
        
        return ok;
    }
    
    // 检查HOME_NET
    bool check_home_net(const SnortConfig* config) {
        if (config->get_home_net().empty()) {
            ErrorMessage("HOME_NET not configured\n");
            return false;
        }
        return true;
    }
    
    // 检查规则语法
    bool check_rules(const SnortConfig* config) {
        auto rules = config->get_rules();
        
        for (const auto& rule : rules) {
            if (!validate_rule_syntax(rule)) {
                ErrorMessage("Invalid rule: %s\n", rule.c_str());
                return false;
            }
        }
        return true;
    }
    
    // 检查端口冲突
    bool check_port_conflicts(const SnortConfig* config) {
        std::map<uint16_t, std::string> port_to_service;
        
        for (const auto& svc : config->get_services()) {
            for (uint16_t port : svc.ports) {
                auto it = port_to_service.find(port);
                if (it != port_to_service.end() && it->second != svc.name) {
                    ErrorMessage("Port %d conflict: %s vs %s\n",
                        port, it->second.c_str(), svc.name.c_str());
                    return false;
                }
                port_to_service[port] = svc.name;
            }
        }
        return true;
    }
    
private:
    std::vector<std::string> errors_;
};
```

---

## 附录IY： 日志记录系统 {#附录iy-日志记录系统}

### IY.1 分级日志 {#iy-1-分级日志}

```cpp
// loggers/logger.h

class Logger {
public:
    enum class Level : uint8_t {
        TRACE = 0,
        DEBUG = 1,
        INFO = 2,
        WARN = 3,
        ERROR = 4,
        FATAL = 5
    };
    
    static Logger& instance() {
        static Logger inst;
        return inst;
    }
    
    void set_level(Level level) { min_level_ = level; }
    
    void log(Level level, const char* file, int line,
             const char* fmt, ...) {
        if (level < min_level_)
            return;
        
        char buf[1024];
        va_list args;
        va_start(args, fmt);
        vsnprintf(buf, sizeof(buf), fmt, args);
        va_end(args);
        
        fprintf(stderr, "[%s] %s:%d: %s\n",
                level_str(level), file, line, buf);
    }
    
    const char* level_str(Level level) {
        const char* names[] = {"TRACE", "DEBUG", "INFO", 
                              "WARN", "ERROR", "FATAL"};
        return names[static_cast<int>(level)];
    }
    
private:
    Logger() : min_level_(Level::INFO) {}
    Level min_level_;
};

#define LOG_TRACE(fmt, ...) \
    Logger::instance().log(Logger::Level::TRACE, \
        __FILE__, __LINE__, fmt, ##__VA_ARGS__)

#define LOG_DEBUG(fmt, ...) \
    Logger::instance().log(Logger::Level::DEBUG, \
        __FILE__, __LINE__, fmt, ##__VA_ARGS__)

#define LOG_INFO(fmt, ...) \
    Logger::instance().log(Logger::Level::INFO, \
        __FILE__, __LINE__, fmt, ##__VA_ARGS__)

#define LOG_WARN(fmt, ...) \
    Logger::instance().log(Logger::Level::WARN, \
        __FILE__, __LINE__, fmt, ##__VA_ARGS__)

#define LOG_ERROR(fmt, ...) \
    Logger::instance().log(Logger::Level::ERROR, \
        __FILE__, __LINE__, fmt, ##__VA_ARGS__)
```

---
