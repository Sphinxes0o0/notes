---
title: "Snort 3 · 附录 GW–HG"
description: "附录GW： 日志格式详解 — 附录HG： 字符串处理"
---

# Snort 3 · 附录 GW–HG

[返回总目录](../snort3_architecture_analysis)

## 附录GW： 日志格式详解 {#附录gw-日志格式详解}

### GW.1 Alert格式 {#gw-1-alert格式}

```
[{ "timestamp": "2026-04-10T15:30:45.123456Z",
   "event_type": "alert",
   "gid": 1,
   "sid": 1000001,
   "revision": 1,
   "classification": "Attempted Information Leak",
   "priority": 2,
   "src_ip": "192.168.1.100",
   "src_port": 54321,
   "dst_ip": "10.0.0.1",
   "dst_port": 80,
   "protocol": "TCP",
   "flow": {
       "start_time": "2026-04-10T15:30:40.000000Z",
       "pkts_to_server": 5,
       "pkts_to_client": 3,
       "bytes_to_server": 512,
       "bytes_to_client": 2048
   },
   "alert": {
       "message": "ET SCAN Potential SSH Scan",
       "category": "Attempted Information Leak"
   }
}]
```

### GW.2 日志字段说明 {#gw-2-日志字段说明}

| 字段 | 类型 | 描述 |
|------|------|------|
| timestamp | string | ISO 8601格式时间戳 |
| gid | uint32 | 生成器ID |
| sid | uint32 | 签名ID |
| revision | uint32 | 规则修订版本 |
| classification | string | 告警分类 |
| priority | uint32 | 优先级(1最高) |
| src_ip/dst_ip | string | 源/目标IP地址 |
| src_port/dst_port | uint32 | 源/目标端口 |
| protocol | string | 协议名称 |
| msg | string | 规则消息 |

---

## 附录GX： 协议分析器实现 {#附录gx-协议分析器实现}

### GX.1 自定义协议解析 {#gx-1-自定义协议解析}

```cpp
// protocols/custom/custom_protocol.h

class CustomProtocol {
public:
    // 协议标识符
    static constexpr uint32_t PROTOCOL_ID = 0x43555354;  // "CUST"
    
    // 头部结构
    struct Header {
        uint32_t magic;       // 0x43555354
        uint8_t version;      // 版本号
        uint8_t type;         // 消息类型
        uint16_t length;      // 载荷长度
        uint32_t seq;         // 序列号
        uint32_t checksum;    // 校验和
    };
    
    // 解析头部
    static bool parse_header(const uint8_t* data, size_t len, Header& hdr) {
        if (len < sizeof(Header))
            return false;
        
        memcpy(&hdr, data, sizeof(Header));
        
        // 验证魔数
        if (hdr.magic != PROTOCOL_ID)
            return false;
        
        // 验证版本
        if (hdr.version != 1)
            return false;
        
        return true;
    }
    
    // 计算校验和
    static uint32_t calculate_checksum(const uint8_t* data, size_t len) {
        uint32_t sum = 0;
        for (size_t i = 0; i < len; i++) {
            sum += data[i];
        }
        return sum;
    }
    
    // 验证校验和
    static bool verify_checksum(const Header& hdr, const uint8_t* payload) {
        uint32_t computed = calculate_checksum(payload, hdr.length);
        return computed == hdr.checksum;
    }
};
```

---

## 附录GY： 流量生成器 {#附录gy-流量生成器}

### GY.1 测试流量生成 {#gy-1-测试流量生成}

```cpp
// testing/traffic_generator.h

class TrafficGenerator {
public:
    // 生成TCP流量
    static void generate_tcp_flow(const char* src_ip, uint16_t src_port,
                                  const char* dst_ip, uint16_t dst_port) {
        // 发送SYN
        send_packet(src_ip, src_port, dst_ip, dst_port, TCP_SYN);
        
        // 等待SYN-ACK
        auto synack = receive_packet(timeout_ms);
        if (!validate_synack(synack))
            return;
        
        // 发送ACK
        send_packet(src_ip, src_port, dst_ip, dst_port, TCP_ACK);
        
        // 发送数据
        for (int i = 0; i < num_packets; i++) {
            send_packet(src_ip, src_port, dst_ip, dst_port, TCP_ACK | TCP_PSH, 
                       generate_payload(i));
        }
        
        // 发送FIN
        send_packet(src_ip, src_port, dst_ip, dst_port, TCP_FIN | TCP_ACK);
    }
    
    // 生成HTTP流量
    static void generate_http_traffic() {
        const char* http_request = 
            "GET /test.html HTTP/1.1\r\n"
            "Host: example.com\r\n"
            "User-Agent: SnortTest/1.0\r\n"
            "Accept: */*\r\n"
            "\r\n";
        
        send_tcp_packet(dst_ip, 80, http_request, strlen(http_request));
    }
    
    // 生成恶意流量
    static void generate_malicious_traffic(const char* pattern) {
        // 发送带有恶意模式的数据包
        std::vector<uint8_t> payload;
        payload.resize(1024);
        
        // 填充有害模式
        memcpy(payload.data(), pattern, strlen(pattern));
        
        send_tcp_packet(dst_ip, dst_port, 
                       reinterpret_cast<const char*>(payload.data()), 
                       payload.size());
    }
};
```

---

## 附录GZ： 基准测试 {#附录gz-基准测试}

### GZ.1 性能基准 {#gz-1-性能基准}

```cpp
// testing/benchmark.h

class Benchmark {
public:
    // 基准测试配置
    struct Config {
        uint64_t duration_sec = 60;     // 测试持续时间
        uint32_t packet_rate = 1000000; // 每秒包数
        uint16_t packet_size = 64;      // 包大小
        bool randomize = true;          // 随机化
    };
    
    // 运行基准测试
    BenchmarkResult run(const Config& config) {
        BenchmarkResult result;
        timeval start, end;
        
        gettimeofday(&start, nullptr);
        
        uint64_t start_packets = get_packet_count();
        uint64_t start_bytes = get_byte_count();
        
        // 生成流量
        generate_traffic(config);
        
        uint64_t end_packets = get_packet_count();
        uint64_t end_bytes = get_byte_count();
        
        gettimeofday(&end, nullptr);
        
        double elapsed = (end.tv_sec - start.tv_sec) + 
                        (end.tv_usec - start.tv_usec) / 1000000.0;
        
        result.packets_per_sec = (end_packets - start_packets) / elapsed;
        result.mbps = (end_bytes - start_bytes) * 8 / elapsed / 1000000.0;
        result.latency_avg = measure_avg_latency();
        result.latency_p99 = measure_p99_latency();
        result.drop_rate = calculate_drop_rate();
        
        return result;
    }
    
    // 打印结果
    void print_results(const BenchmarkResult& result) {
        printf("=== Benchmark Results ===\n");
        printf("Packets/sec: %.2f\n", result.packets_per_sec);
        printf("Throughput: %.2f Mbps\n", result.mbps);
        printf("Avg Latency: %.2f us\n", result.latency_avg);
        printf("P99 Latency: %.2f us\n", result.latency_p99);
        printf("Drop Rate: %.2f%%\n", result.drop_rate);
    }
    
    struct BenchmarkResult {
        double packets_per_sec;
        double mbps;
        double latency_avg;
        double latency_p99;
        double drop_rate;
    };
};
```

---

## 附录HA： 协议逆向工程 {#附录ha-协议逆向工程}

### HA.1 协议分析方法 {#ha-1-协议分析方法}

```cpp
// analysis/protocol_analyzer.h

class ProtocolAnalyzer {
public:
    // 捕获并分析协议
    void analyze_pcap(const char* pcap_file) {
        pcap_t* pcap = pcap_open(pcap_file);
        
        struct pcap_pkthdr* header;
        const uint8_t* packet;
        
        while (pcap_next_ex(pcap, &header, &packet) >= 0) {
            process_packet(header, packet);
        }
    }
    
    // 提取协议特征
    struct ProtocolFingerprint {
        std::vector<uint8_t> header_magic;
        std::vector<uint16_t> port_usage;
        std::map<std::string, double> byte_distribution;
        std::vector<std::string> common_patterns;
    };
    
    // 生成指纹
    ProtocolFingerprint generate_fingerprint() {
        ProtocolFingerprint fp;
        
        // 统计头部魔术字节
        for (auto& p : packets_) {
            if (p.size() >= 4) {
                fp.header_magic.push_back(p[0]);
                fp.header_magic.push_back(p[1]);
            }
        }
        
        // 统计端口使用
        for (auto& p : packets_) {
            if (is_tcp(p)) {
                uint16_t sport = get_tcp_src_port(p);
                fp.port_usage.push_back(sport);
            }
        }
        
        // 字节分布
        std::map<uint8_t, uint64_t> byte_counts;
        for (auto& p : packets_) {
            for (uint8_t b : p) {
                byte_counts[b]++;
            }
        }
        
        return fp;
    }
    
    // 自动检测协议
    ProtocolDetection detect_protocol(const uint8_t* data, size_t len) {
        ProtocolDetection result;
        
        // 检查魔术字节
        if (len >= 4 && memcmp(data, "HTTP", 4) == 0) {
            result.protocol = "HTTP";
            result.confidence = 0.95;
        }
        // 检查端口
        else if (is_known_port(get_port(data))) {
            result.protocol = lookup_port(get_port(data));
            result.confidence = 0.80;
        }
        // 检查模式
        else {
            auto matches = match_patterns(data, len);
            if (!matches.empty()) {
                result.protocol = matches[0].name;
                result.confidence = matches[0].score;
            }
        }
        
        return result;
    }
};
```

---

## 附录HB： 加密算法实现 {#附录hb-加密算法实现}

### HB.1 哈希函数 {#hb-1-哈希函数}

```cpp
// utils/hash.h

class HashFunctions {
public:
    // MD5
    static std::string md5(const uint8_t* data, size_t len) {
        md5_state_t state;
        md5_init(&state);
        md5_update(&state, data, len);
        md5_final(digest_, &state);
        return hex_encode(digest_, 16);
    }
    
    // SHA-256
    static std::string sha256(const uint8_t* data, size_t len) {
        sha256_state_t state;
        sha256_init(&state);
        sha256_update(&state, data, len);
        sha256_final(digest_, &state);
        return hex_encode(digest_, 32);
    }
    
    // MurmurHash3
    static uint32_t murmur3(const uint8_t* data, size_t len, uint32_t seed = 0) {
        const uint32_t c1 = 0xcc9e2d51;
        const uint32_t c2 = 0x1b873593;
        
        uint32_t h1 = seed;
        uint32_t k1 = 0;
        
        size_t nblocks = len / 4;
        
        for (size_t i = 0; i < nblocks; i++) {
            k1 = *(uint32_t*)(data + i * 4);
            
            k1 *= c1;
            k1 = ROTL32(k1, 15);
            k1 *= c2;
            
            h1 ^= k1;
            h1 = ROTL32(h1, 13);
            h1 = h1 * 5 + 0xe6546b64;
        }
        
        return h1;
    }
    
private:
    static constexpr uint32_t ROTL32(uint32_t x, int8_t r) {
        return (x << r) | (x >> (32 - r));
    }
};
```

### HB.2 对称加密 {#hb-2-对称加密}

```cpp
// utils/aes.h

class AESCipher {
public:
    // 初始化
    bool init(const uint8_t* key, size_t key_len, const uint8_t* iv = nullptr) {
        if (key_len != 16 && key_len != 24 && key_len != 32)
            return false;
        
        AES_set_encrypt_key(key, key_len * 8, &enc_key_);
        AES_set_decrypt_key(key, key_len * 8, &dec_key_);
        
        if (iv)
            memcpy(iv_, iv, 16);
        
        return true;
    }
    
    // CBC加密
    std::vector<uint8_t> encrypt_cbc(const uint8_t* plaintext, size_t len) {
        std::vector<uint8_t> ciphertext;
        ciphertext.resize(len + 16);  // 预留填充
        
        size_t padded_len = ((len + 15) / 16) * 16;
        uint8_t* padded = new uint8_t[padded_len];
        memcpy(padded, plaintext, len);
        
        // PKCS7填充
        uint8_t pad = padded_len - len;
        memset(padded + len, pad, pad);
        
        // 加密
        uint8_t iv_copy[16];
        memcpy(iv_copy, iv_, 16);
        
        for (size_t i = 0; i < padded_len; i += 16) {
            for (int j = 0; j < 16; j++)
                iv_copy[j] ^= padded[i + j];
            
            AES_encrypt(iv_copy, &ciphertext[i], &enc_key_);
            memcpy(iv_copy, &ciphertext[i], 16);
        }
        
        delete[] padded;
        return ciphertext;
    }
    
private:
    AES_KEY enc_key_;
    AES_KEY dec_key_;
    uint8_t iv_[16];
};
```

---

## 附录HC： 正则表达式引擎 {#附录hc-正则表达式引擎}

### HC.1 PCRE接口 {#hc-1-pcre接口}

```cpp
// utils/pcre.h

class PCRE {
public:
    // 编译正则表达式
    bool compile(const char* pattern, const char* options = nullptr) {
        const char* err;
        int erroffset;
        
        int opt = 0;
        if (options) {
            if (strchr(options, 'i')) opt |= PCRE_CASELESS;
            if (strchr(options, 'm')) opt |= PCRE_MULTILINE;
            if (strchr(options, 's')) opt |= PCRE_DOTALL;
        }
        
        re_ = pcre_compile(pattern, opt, &err, &erroffset, nullptr);
        if (!re_) {
            error_ = err;
            return false;
        }
        
        // Study
        extra_ = pcre_study(re_, 0, &err);
        
        return true;
    }
    
    // 执行匹配
    int match(const char* subject, size_t len,
              std::vector<std::pair<int, int>>& matches) {
        int rc = pcre_exec(re_, extra_, subject, len, 0, 0, 
                          ovec_, MAX_MATCHES * 2);
        
        if (rc < 0) {
            if (rc == PCRE_ERROR_NOMATCH)
                return 0;
            return -1;
        }
        
        matches.clear();
        for (int i = 0; i < rc; i++) {
            matches.emplace_back(ovec_[2*i], ovec_[2*i+1]);
        }
        
        return rc;
    }
    
    ~PCRE() {
        if (re_) pcre_free(re_);
        if (extra_) pcre_free(extra_);
    }
    
private:
    pcre* re_;
    pcre_extra* extra_;
    int ovec_[MAX_MATCHES * 2];
    std::string error_;
};
```

---

## 附录HD： 数据结构实现 {#附录hd-数据结构实现}

### HD.1 环形缓冲区 {#hd-1-环形缓冲区}

```cpp
// utils/ring_buffer.h

template<typename T>
class RingBuffer {
public:
    explicit RingBuffer(size_t capacity) 
        : capacity_(capacity), buffer_(new T[capacity]) {
        head_ = tail_ = 0;
        count_ = 0;
    }
    
    ~RingBuffer() { delete[] buffer_; }
    
    // 入队
    bool push(const T& item) {
        if (count_ == capacity_)
            return false;
        
        buffer_[tail_] = item;
        tail_ = (tail_ + 1) % capacity_;
        count_++;
        return true;
    }
    
    // 出队
    bool pop(T& item) {
        if (count_ == 0)
            return false;
        
        item = buffer_[head_];
        head_ = (head_ + 1) % capacity_;
        count_--;
        return true;
    }
    
    // 查看队首
    bool peek(T& item) const {
        if (count_ == 0)
            return false;
        
        item = buffer_[head_];
        return true;
    }
    
    // 大小
    size_t size() const { return count_; }
    
    // 是否满
    bool full() const { return count_ == capacity_; }
    
    // 是否空
    bool empty() const { return count_ == 0; }
    
private:
    size_t capacity_;
    T* buffer_;
    size_t head_;
    size_t tail_;
    size_t count_;
};
```

### HD.2 跳表 {#hd-2-跳表}

```cpp
// utils/skip_list.h

template<typename K, typename V>
class SkipList {
public:
    struct Node {
        K key;
        V value;
        int level;
        Node** forward;
    };
    
    SkipList(int max_level = 16) : max_level_(max_level) {
        level_ = 0;
        header_ = new Node();
        header_->forward = new Node*[max_level];
        for (int i = 0; i < max_level; i++)
            header_->forward[i] = nullptr;
    }
    
    // 插入
    void insert(const K& key, const V& value) {
        Node* update[max_level_];
        Node* current = header_;
        
        for (int i = level_ - 1; i >= 0; i--) {
            while (current->forward[i] && current->forward[i]->key < key)
                current = current->forward[i];
            update[i] = current;
        }
        
        int new_level = random_level();
        
        if (new_level > level_) {
            for (int i = level_; i < new_level; i++)
                update[i] = header_;
            level_ = new_level;
        }
        
        Node* new_node = new Node();
        new_node->key = key;
        new_node->value = value;
        new_node->level = new_level;
        new_node->forward = new Node*[new_level];
        
        for (int i = 0; i < new_level; i++)
            new_node->forward[i] = update[i]->forward[i];
        
        for (int i = 0; i < new_level; i++)
            update[i]->forward[i] = new_node;
    }
    
    // 查找
    V* find(const K& key) {
        Node* current = header_;
        
        for (int i = level_ - 1; i >= 0; i--) {
            while (current->forward[i] && current->forward[i]->key < key)
                current = current->forward[i];
        }
        
        current = current->forward[0];
        if (current && current->key == key)
            return &current->value;
        
        return nullptr;
    }
    
private:
    int level_;
    int max_level_;
    Node* header_;
};
```

---

## 附录HE： 时间处理 {#附录he-时间处理}

### HE.1 高精度计时 {#he-1-高精度计时}

```cpp
// time/high_resolution_timer.h

class HighResolutionTimer {
public:
    // 使用TSC寄存器
    static uint64_t rdtsc() {
        uint32_t lo, hi;
        __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
        return ((uint64_t)hi << 32) | lo;
    }
    
    // 使用clock_gettime
    static uint64_t get_time_ns() {
        struct timespec ts;
        clock_gettime(CLOCK_MONOTONIC, &ts);
        return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
    }
    
    // CPU频率
    static double get_cpu_frequency() {
        static double freq = 0;
        if (freq == 0) {
            uint64_t start = rdtsc();
            struct timespec ts = {1, 0};
            clock_gettime(CLOCK_MONOTONIC, &ts);
            uint64_t end = rdtsc();
            freq = (end - start) / 1.0e9;
        }
        return freq;
    }
    
    // 时间戳转字符串
    static std::string format_time(uint64_t timestamp_ns) {
        time_t sec = timestamp_ns / 1000000000ULL;
        struct tm* tm = localtime(&sec);
        
        char buf[64];
        strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", tm);
        
        uint32_t nanosec = timestamp_ns % 1000000000ULL;
        snprintf(buf + strlen(buf), 32, ".%09u", nanosec);
        
        return buf;
    }
};
```

---

## 附录HF： 网络工具函数 {#附录hf-网络工具函数}

### HF.1 IP地址操作 {#hf-1-ip地址操作}

```cpp
// utils/ip_utils.h

class IPUtils {
public:
    // 字符串转IP
    static uint32_t parse_ipv4(const char* str) {
        in_addr addr;
        inet_pton(AF_INET, str, &addr);
        return addr.s_addr;
    }
    
    // IP转字符串
    static std::string format_ipv4(uint32_t ip) {
        char buf[INET_ADDRSTRLEN];
        struct in_addr addr;
        addr.s_addr = ip;
        inet_ntop(AF_INET, &addr, buf, sizeof(buf));
        return buf;
    }
    
    // 检查IP是否在范围内
    static bool is_in_range(uint32_t ip, uint32_t start, uint32_t end) {
        return ip >= start && ip <= end;
    }
    
    // 检查IP是否为私有地址
    static bool is_private(uint32_t ip) {
        uint32_t n = ntohl(ip);
        return (n >= 0x0A000000 && n <= 0x0AFFFFFF) ||  // 10.0.0.0/8
               (n >= 0xAC100000 && n <= 0xAC1FFFFF) ||  // 172.16.0.0/12
               (n >= 0xC0A80000 && n <= 0xC0A8FFFF);   // 192.168.0.0/16
    }
    
    // 计算CIDR掩码
    static uint32_t cidr_to_mask(int cidr) {
        if (cidr == 0) return 0;
        return htonl(0xFFFFFFFF << (32 - cidr));
    }
    
    // 计算网络地址
    static uint32_t get_network(uint32_t ip, int cidr) {
        uint32_t mask = cidr_to_mask(cidr);
        return ip & mask;
    }
    
    // 检查子网包含关系
    static bool is_subnet_match(uint32_t ip, uint32_t subnet, int cidr) {
        uint32_t mask = cidr_to_mask(cidr);
        return (ip & mask) == (subnet & mask);
    }
};
```

---

## 附录HG： 字符串处理 {#附录hg-字符串处理}

### HG.1 字符串工具 {#hg-1-字符串工具}

```cpp
// utils/string_utils.h

class StringUtils {
public:
    // 分割字符串
    static std::vector<std::string> split(const std::string& s, char delimiter) {
        std::vector<std::string> tokens;
        std::stringstream ss(s);
        std::string token;
        
        while (std::getline(ss, token, delimiter))
            tokens.push_back(token);
        
        return tokens;
    }
    
    // 去除空白
    static std::string trim(const std::string& s) {
        auto start = s.begin();
        while (start != s.end() && std::isspace(*start))
            start++;
        
        auto end = s.end();
        while (end != start && std::isspace(*(end - 1)))
            end--;
        
        return std::string(start, end);
    }
    
    // 大小写转换
    static std::string to_lower(const std::string& s) {
        std::string result = s;
        std::transform(result.begin(), result.end(), result.begin(),
                      ::tolower);
        return result;
    }
    
    static std::string to_upper(const std::string& s) {
        std::string result = s;
        std::transform(result.begin(), result.end(), result.begin(),
                      ::toupper);
        return result;
    }
    
    // 十六进制编码
    static std::string hex_encode(const uint8_t* data, size_t len) {
        static const char hex[] = "0123456789abcdef";
        std::string result;
        result.reserve(len * 2);
        
        for (size_t i = 0; i < len; i++) {
            result += hex[data[i] >> 4];
            result += hex[data[i] & 0x0F];
        }
        
        return result;
    }
    
    // 十六进制解码
    static std::vector<uint8_t> hex_decode(const std::string& hex_str) {
        std::vector<uint8_t> result;
        result.reserve(hex_str.size() / 2);
        
        for (size_t i = 0; i < hex_str.size(); i += 2) {
            auto h2b = [](char c) -> uint8_t {
                if (c >= '0' && c <= '9') return c - '0';
                if (c >= 'a' && c <= 'f') return c - 'a' + 10;
                if (c >= 'A' && c <= 'F') return c - 'A' + 10;
                return 0;
            };
            
            result.push_back((h2b(hex_str[i]) << 4) | h2b(hex_str[i+1]));
        }
        
        return result;
    }
    
    // 模式匹配(wildcard)
    static bool wildcard_match(const std::string& pattern, const std::string& text) {
        size_t p = 0, t = 0;
        size_t star_idx = std::string::npos;
        size_t match_idx = std::string::npos;
        
        while (t < text.size()) {
            if (p < pattern.size() && (pattern[p] == '?' || pattern[p] == text[t])) {
                p++;
                t++;
            } else if (p < pattern.size() && pattern[p] == '*') {
                star_idx = p;
                match_idx = t;
                p++;
            } else if (star_idx != std::string::npos) {
                p = star_idx + 1;
                t = ++match_idx;
            } else {
                return false;
            }
        }
        
        while (p < pattern.size() && pattern[p] == '*')
            p++;
        
        return p == pattern.size();
    }
};
```

---
