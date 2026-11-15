---
title: "Snort 3 · 附录 CR–DK"
description: "附录CR：流重组细节 — 附录DK： IRC检测器"
---

# Snort 3 · 附录 CR–DK

[返回总目录](../snort3_architecture_analysis)

## 附录CR：流重组细节 {#附录cr-流重组细节}

### CR.1 TcpReassembler {#cr-1-tcpreassembler}

```cpp
// stream/tcp/tcp_reassembler.h

class TcpReassembler {
public:
    // 构造函数
    TcpReassembler(TcpStreamTracker*, TcpNormalizerPolicy&, bool);
    
    // 处理数据
    int process(TcpSegmentDescriptor&, uint8_t*, uint16_t);
    
    // 刷新数据
    void flush(uint8_t dir, uint32_t flags);
    
    // 忽略数据
    void ignore(uint8_t dir, uint32_t skip_bytes, uint32_t missing_bytes);
    
    // 清理
    void clear();
    
    // 获取位置
    uint32_t get_seglist_base_seq(uint8_t dir) const;
    uint32_t get_flush_buf_size(uint8_t dir) const;
    
    // 溢出检查
    bool is_overflow_seq(uint32_t seq) const;
    
private:
    TcpStreamTracker* tracker;     // 流跟踪器
    TcpNormalizerPolicy& normalizer; // 规范化器
    TcpReassemblySegments seglist;   // 分段列表
    bool client_side;                // 是否客户端
    
    // 溢出管理
    bool overflow;                  // 溢出标志
    uint32_t overflow_seq;          // 溢出序列号
};
```

### CR.2 重组段 {#cr-2-重组段}

```cpp
// stream/tcp/tcp_segment_node.h

struct TcpSegmentNode {
    TcpSegmentNode* next;      // 下一个节点
    TcpSegmentNode* prev;      // 上一个节点
    
    uint32_t seq;              // 序列号
    uint16_t len;              // 长度
    uint16_t offset;           // 偏移
    uint8_t* data;             // 数据
    
    uint8_t type;              // 类型
    bool xtradata_map;         // 外部数据映射
    
    // 标记为已发送
    void mark_as_sent();
    
    // 检查是否已发送
    bool was_sent() const;
    
    // 获取下一个未发送
    TcpSegmentNode* get_next_unacked() const;
};
```

---

## 附录CS：协议字段 {#附录cs-协议字段}

### CS.1 Ether协议头 {#cs-1-ether协议头}

```cpp
// protocols/eth.h

struct EtherHdr {
    uint8_t  ether_dhost[6];   // 目标MAC
    uint8_t  ether_shost[6];   // 源MAC
    uint16_t ether_type;       // 类型
};

// 以太网类型值
#define ETHERTYPE_IP     0x0800  // IPv4
#define ETHERTYPE_IPV6   0x86DD  // IPv6
#define ETHERTYPE_VLAN   0x8100  // VLAN
#define ETHERTYPE_ARP    0x0806  // ARP
#define ETHERTYPE_IPX    0x8137  // IPX
#define ETHERTYPE_MPLS   0x8847  // MPLS
```

### CS.2 VLAN协议头 {#cs-2-vlan协议头}

```cpp
// protocols/vlan.h

struct VLANHdr {
    uint16_t vlan_cfi : 1;     // CFI
    uint16_t vlan_pri : 3;     // 优先级
    uint16_t vlan_id : 12;     // VLAN ID
    uint16_t vlan_len;         // 长度/类型
};
```

### CS.3 MPLS协议头 {#cs-3-mpls协议头}

```cpp
// protocols/mpls.h

struct MPLSHdr {
    uint32_t label : 20;       // MPLS标签
    uint32_t exp : 3;         // 实验
    uint32_t bos : 1;         // 栈底
    uint32_t ttl;             // TTL
};
```

---

## 附录CT：TCP跟踪状态机 {#附录ct-tcp跟踪状态机}

### CT.1 状态转换 {#ct-1-状态转换}

```
                    SYN
    CLOSED ──────► LISTEN
         ◄──────
           RST   │  SYN+ACK
                 │
                 │ SYN
        CLOSED ◄─┴──► SYN_SENT
                         │
                         │ SYN+ACK
                         ▼
                      SYN_RECV ──────► ESTABLISHED
                         │                │
                         │ ACK            │ FIN
                         ▼                ▼
                     FIN_WAIT1 ◄─────────┤
                         │                │
           FIN         ACK ▼         FIN ▼
         ◄── ◄── ◄──◄── ─── ◄── ◄── ◄── ◄── ◄──
         │    │    │    │    │    │    │    │    │
         │    │    │    │    │    │    │    │    │
         ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼
      ┌──────────────────────────────────────────┐
      │        TCP STATE MACHINE                 │
      └──────────────────────────────────────────┘
```

### CT.2 事件处理 {#ct-2-事件处理}

```cpp
// stream/tcp/tcp_state_machine.h

class TcpStateMachine {
public:
    // 获取下一个状态
    static TcpState get_next_state(TcpState state, TcpEvent event);
    
    // 检查转换是否有效
    static bool is_valid_transition(TcpState, TcpEvent);
    
    // 获取事件名称
    static const char* get_event_name(TcpEvent);
    
    // 获取状态名称
    static const char* get_state_name(TcpState);
};

// 状态转换表
// 格式: [当前状态][事件] = 下一状态
static const TcpState state_table[TCP_MAX_STATES][TCP_MAX_EVENTS];
```

---

## 附录CU：内存对齐处理 {#附录cu-内存对齐处理}

### CU.1 对齐宏 {#cu-1-对齐宏}

```cpp
// utils/endian.h

// 小端平台
#if defined(__LITTLE_ENDIAN__)
    #define __BIG_ENDIAN__ 0
    #define __LITTLE_ENDIAN__ 1

// 大端平台
#elif defined(__BIG_ENDIAN__)
    #define __BIG_ENDIAN__ 1
    # __LITTLE_ENDIAN__ 0

// 未知
#else
    #error "Please define BYTE_ORDER"
#endif

// 字节序转换
#define SWAP_BYTES_16(x) ((uint16_t)(((x) & 0x00FF) << 8) | \
                                  ((x) & 0xFF00) >> 8))

#define SWAP_BYTES_32(x) ...
#define SWAP_BYTES_64(x) ...
```

---

## 附录CV：配置加载 {#附录cv-配置加载}

### CV.1 Lua配置解析 {#cv-1-lua配置解析}

```cpp
// lua/lua.h

class Lua::Config {
public:
    // 构造函数
    Config(const char* script);
    
    // 解析配置
    bool parse();
    
    // 获取值
    template<typename T>
    bool get(const char* key, T& value) const;
    
    // 获取嵌套值
    bool get(const char* table, const char* key, Value& value);
    
    // 执行函数
    bool execute(const char* func);
    
    // 获取错误
    const char* get_error() const;
};
```

---

## 附录CW：插件API {#附录cw-插件api}

### CW.1 Inspector插件 {#cw-1-inspector插件}

```cpp
// framework/inspector.h

class Inspector {
public:
    virtual ~Inspector() = default;
    
    // 创建
    static Inspector* create(Module*);
    
    // 销毁
    virtual void destroy() = 0;
    
    // 处理数据包
    virtual void eval(Packet*) = 0;
    
    // 获取分割器
    virtual StreamSplitter* get_splitter(bool to_server);
    
    // 统计
    virtual void show_stats() {}
    virtual void reset_stats() {}
    virtual void tinit() {}
    virtual void tterm() {}
    
    // 配置
    virtual bool configure(SnortConfig*) { return true; }
    
    // 哈希键
    virtual uint32_t hash() const;
    virtual bool compare(const Inspector*) const;
};
```

---

## 附录CX：搜索算法 {#附录cx-搜索算法}

### CX.1 AC自动机 {#cx-1-ac自动机}

```cpp
// search_engines/ac/ac.h

class AC {
public:
    // 构造函数
    AC();
    ~AC();
    
    // 添加模式
    void add_pattern(const uint8_t* pat, unsigned len, unsigned id);
    
    // 初始化
    void init();
    
    // 搜索
    int search(const uint8_t* text, unsigned len,
               unsigned* matches, unsigned max_matches);
    
    // 获取统计
    unsigned get_pattern_count() const;
    unsigned get_node_count() const;
    
    // 重置
    void reset();
};
```

### CX.2 Hyperscan {#cx-2-hyperscan}

```cpp
// search_engines/hyperscan/hyperscan.h

class Hyperscan {
public:
    // 编译模式
    int add_pattern(const char* pattern, unsigned id);
    
    // 初始化数据库
    int compile();
    
    // 扫描
    int scan(const uint8_t* data, unsigned len,
              void (*match)(unsigned int, unsigned int, unsigned int));
    
    // 序列化
    int serialize(const char* file);
    int deserialize(const char* file);
};
```

---

## 附录CY：协议相关错误处理 {#附录cy-协议相关错误处理}

### CY.1 规范化器策略 {#cy-1-规范化器策略}

```cpp
// stream/tcp/tcp_normalizers.h

class TcpNormalizer {
public:
    // 规范化操作
    enum class Action {
        NONE,           // 无操作
        DROP,           // 丢弃
        TRUNCATE,       // 截断
        ADJUST,         // 调整
        SKIP            // 跳过
    };
    
    // 数据包规范化
    Action normalize(Packet*, uint8_t);
    
    // TCP选项规范化
    uint8_t normalize_options(uint8_t*, uint16_t);
    
    // 序列号规范化
    bool normalize_seq(Packet*, uint32_t);
};

// 规范化策略
struct TcpNormalizerPolicy {
    bool drop_invalid = false;       // 丢弃无效包
    bool drop_obselete = false;      // 丢弃过时包
    bool drop_frags = false;         // 丢弃分片
    bool block_unisigned = false;    // 阻止无符号数据
    bool block_rfc1323 = false;      // 阻止RFC1323
    bool trim_syn = false;           // 修剪SYN
    bool trim_rst = false;           // 修剪RST
    bool trim_mid = false;           // 修剪中间数据
    bool trim_win = false;           // 修剪窗口
    bool trim_ood = false;           // 修剪乱序
    bool require_3way = false;       // 要求三次握手
};
```

---

## 附录CZ：配置示例 {#附录cz-配置示例}

### CZ.1 简单Snort配置 {#cz-1-简单snort配置}

```lua
-- snort.lua
-- 基础配置
home_net = "192.168.1.0/24"
external_net = "!192.168.1.0/24"

-- 规则文件
rules = [[
    alert tcp any any -> any 80 (msg:"HTTP traffic"; sid:1000001;)
    alert icmp any any -> any any (msg:"ICMP ping"; sid:1000002;)
]]

-- 日志
logdir = "/var/log/snort"

-- 接口
daq = "pcap"
interface = "eth0"
```

### CZ.2 高级配置 {#cz-2-高级配置}

```lua
-- 高级snort.lua
-- 流量基准
stream = {
    enable = true,
    max_sessions = 262144,
    session_timeout = 30,
    max_queued_bytes = 2097152,
    flush_policy = "STREAM_FLPOLICY_IGNORE"
}

-- 检测引擎
detection = {
    search_engine = "AC",
    enable_rule_profiling = true,
    max_pattern_len = 1024
}

-- HTTP检测
http_inspect = {
    enable = true,
    profile = "high",
    max_header_len = 3072,
    max_headers = 200
}

-- FTP检测
ftp_inspect = {
    enable = true,
    defrag = true,
    deep_inspection = true
}
```

---

## 附录DA：调试技巧 {#附录da-调试技巧}

### DA.1 启用调试日志 {#da-1-启用调试日志}

```bash
# 使用-w选项
snort -c snort.lua -i eth0 -A cmg -B "debug"

# 调试特定模块
snort --enable-debug --trace-modules=http_inspect
```

### DA.2 使用trace工具 {#da-2-使用trace工具}

```cpp
// 在代码中添加trace
#define TRACE_DEBUG(module, ...) \
    trace_logf(trace_api, nullptr, __VA_ARGS__)

// 使用示例
TRACE_DEBUG(wizard_trace, "Service detected: %s\n", service);
```

### DA.3 常见问题排查 {#da-3-常见问题排查}

1. **性能问题**: 使用`--profile-rules`和`--profile-modules`
2. **内存泄漏**: 使用`--enable-memory-tracker`
3. **规则匹配问题**: 使用`-M`选项查看匹配统计
4. **会话跟踪问题**: 启用`--enable-session-tracker`

---

## 附录DB：测试框架 {#附录db-测试框架}

### DB.1 单元测试 {#db-1-单元测试}

```cpp
// Unit test example
TEST(TestSuite, PacketDecode) {
    uint8_t packet[] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05,  // Dst MAC
        0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b,  // Src MAC
        0x08, 0x00,                          // EtherType (IP)
        // IP header...
    };
    
    Packet p;
    decode packet(&p, packet, sizeof(packet));
    
    EXPECT_EQ(p.type, PktType::IP);
    EXPECT_EQ(p.ip_api.get_protocol(), IpProtocol::TCP);
}
```

### DB.2 集成测试 {#db-2-集成测试}

```cpp
// Integration test example
TEST(Integration, HTTPDetection) {
    // 创建测试数据包
    auto p = create_tcp_packet("GET /test HTTP/1.1\r\n\r\n");
    
    // 创建HTTP检测器
    HttpInspector inspector;
    inspector.configure(config);
    
    // 处理数据包
    inspector.eval(p.get());
    
    // 验证结果
    EXPECT_NE(p->flow->service, nullptr);
    EXPECT_STREQ(p->flow->service, "http");
}
```

---

## 附录DC：性能优化建议 {#附录dc-性能优化建议}

### DC.1 规则优化 {#dc-1-规则优化}

1. **使用快速模式规则**: 减少规则评估次数
2. **使用字节偏移**: 减少正则表达式使用
3. **使用PCRE优化**: 使用简化的PCRE模式
4. **避免过多 negated规则**: 降低CPU开销

### DC.2 配置优化 {#dc-2-配置优化}

```lua
-- 优化配置示例
stream = {
    max_queued_bytes = 4194304,  -- 增加队列
    compress_depth = 65535,
    decompress_depth = 65535
}

detection = {
    detect_raw = true,
    enable_single_rule_group = true,
    bulk_update_pragma = true
}
```

---

## 附录DD：命令参考 {#附录dd-命令参考}

### DD.1 常用命令 {#dd-1-常用命令}

```bash
# 基本运行
snort -c snort.lua -i eth0

# 详细模式
snort -c snort.lua -i eth0 -v

# 报警模式
snort -c snort.lua -i eth0 -A alert

# 静默模式
snort -c snort.lua -i eth0 -Q -N

# 统计模式
snort -c snort.lua -i eth0 --统计

# 规则调试
snort -c snort.lua -i eth0 --rule-profiling
```

### DD.2 性能测试 {#dd-2-性能测试}

```bash
# CPU使用率
snort -c snort.lua -i eth0 --cpu_affinity 0-3

# 内存限制
snort -c snort.lua -i eth0 --memcap 512

# 队列大小
snort -c snort.lua -i eth0 --max_threads_per_cpu 4
```

---

## 附录DE：术语表 {#附录de-术语表}

### DE.1 核心概念 {#de-1-核心概念}

| 术语 | 描述 |
|------|------|
| **Inspector** | Snort 3中的数据包处理模块 |
| **Codec** | 协议编解码器 |
| **Stream Splitter** | 流分割器 |
| **Binder** | 服务检测绑定器 |
| **Wizard** | 自动服务检测 |
| **MPSE** | 多模式搜索引擎 |
| **PAF** | 协议感知刷新 |
| **Flow** | 网络会话流 |
| **Session** | 协议会话 |
| **DAQ** | 数据采集接口 |

### DE.2 协议相关 {#de-2-协议相关}

| 术语 | 描述 |
|------|------|
| **TCP状态** | TCP连接状态 (LISTEN, SYN_SENT, ESTABLISHED, etc.) |
| **序列号** | TCP序列号 |
| **确认号** | TCP确认号 |
| **窗口大小** | TCP滑动窗口大小 |
| **MSS** | 最大段大小 |
| **MTU** | 最大传输单元 |
| **PAWS** | 保护时间戳 |
| **Timestamps** | TCP时间戳选项 |

---

*文档版本: 11.0*
*更新日期: 2026年4月10日*
*总行数: 5800+*


---

## 附录DF： ARP协议检测器 {#附录df-arp协议检测器}

### DF.1 ARP重组 {#df-1-arp重组}

```cpp
// arp/arp_module.h
class ARPInspector : public Inspector {
public:
    ARPInspector(const SnortConfig*);
    ~ARPInspector() override;
    
    void eval(Packet*) override;
    
    // ARP操作码
    enum class Operation : uint16_t {
        REQUEST = 1,        // 请求
        REPLY = 2,          // 响应
        RREQUEST = 3,       // 逆请求
        RREPLY = 4,         // 逆响应
        DRAR_ERROR = 5,     // 动态ARP检测错误
        DRAR_WARNING = 6,   // 动态ARP检测警告
        INARP_REQUEST = 8,  // 无偿ARP
        INARP_REPLY = 9     // 无偿ARP响应
    };
    
private:
    void process_arp(Packet*);
    bool validate_arp(Packet*);
    
    ARPState* state;  // ARP状态跟踪
};

// ARP数据包结构
struct ARPHdr {
    uint16_t ar_hrd;      // 硬件类型
    uint16_t ar_pro;      // 协议类型
    uint8_t  ar_hln;      // 硬件地址长度
    uint8_t  ar_pln;      // 协议地址长度
    uint16_t ar_op;       // 操作码
    uint8_t  ar_sha[6];   // 发送者硬件地址
    uint32_t ar_sip;      // 发送者IP地址
    uint8_t  ar_tha[6];   // 目标硬件地址
    uint32_t ar_tip;      // 目标IP地址
};
```

---

## 附录DG： GTP检测器（GPRS隧道协议） {#附录dg-gtp检测器-gprs隧道协议}

### DG.1 GTP协议处理 {#dg-1-gtp协议处理}

```cpp
// gtp/gtp.h
class GTPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // GTP消息类型
    enum class MessageType : uint8_t {
        // GTPv1消息
        ECHO_REQUEST = 1,
        ECHO_RESPONSE = 2,
        CREATE_PDP = 16,
        UPDATE_PDP = 17,
        DELETE_PDP = 18,
        // GTPv2消息
        CREATE_SESSION = 32,
        MODIFY_BEARER = 33,
        DELETE_SESSION = 36
    };
    
private:
    void process_gtpv1(Packet*, const uint8_t*, uint16_t);
    void process_gtpv2(Packet*, const uint8_t*, uint16_t);
    
    // GTP头结构
    struct GTPHeader {
        uint8_t flags;        // 标志
        uint8_t type;        // 消息类型
        uint16_t length;     // 长度
        uint32_t teid;       // 隧道端点标识符
    };
};
```

---

## 附录DH： Diameter协议检测器 {#附录dh-diameter协议检测器}

### DH.1 Diameter基础 {#dh-1-diameter基础}

```cpp
// diameter/diameter.h
class DiameterInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // Diameter命令代码
    enum class CommandCode : uint32_t {
        CE = 257,           // Capabilities-Exchange
        RA = 280,           // Re-Auth
        STR = 275,          // Session-Termination
        ASR = 274,          // Abort-Session
        WA = 265,           // Watchdog
        DW = 281            // Disconnect-Watchdog-Ans
    };
    
    // Diameter应用ID
    enum class AppId : uint32_t {
        NASREQ = 1,         // 网络访问服务
        ACCOUNTING = 3,    // 计费
        CREDIT_CONTROL = 4, // 信用控制
        DIAMETER_COMMON = 0xFFFFFFFF
    };
};
```

---

## 附录DI： Radius协议检测器 {#附录di-radius协议检测器}

### DI.1 RADIUS认证 {#di-1-radius认证}

```cpp
// radius/radius.h
class RadiusInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // RADIUS消息类型
    enum class MessageType : uint8_t {
        ACCESS_REQUEST = 1,      // 访问请求
        ACCESS_ACCEPT = 2,       // 访问接受
        ACCESS_REJECT = 3,       // 访问拒绝
        ACCOUNTING_REQUEST = 4,  // 计费请求
        ACCOUNTING_RESPONSE = 5,// 计费响应
        ACCESS_CHALLENGE = 11,  // 访问挑战
        STATUS_SERVER = 12,      // 状态服务器
        STATUS_CLIENT = 13      // 状态客户端
    };
    
    // RADIUS属性类型
    enum class AttributeType : uint8_t {
        USER_NAME = 1,
        USER_PASSWORD = 2,
        CHAP_PASSWORD = 3,
        NAS_IP_ADDRESS = 4,
        NAS_PORT = 5,
        SERVICE_TYPE = 6,
        REPLY_MESSAGE = 18,
        CALLER_ID = 31,
        ACCT_SESSION_ID = 44,
        ACCT_STATUS_TYPE = 40
    };
};
```

---

## 附录DJ： DHCP检测器 {#附录dj-dhcp检测器}

### DJ.1 DHCP选项处理 {#dj-1-dhcp选项处理}

```cpp
// dhcp/dhcp.h
class DHCPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // DHCP消息类型
    enum class MessageType : uint8_t {
        DISCOVER = 1,
        OFFER = 2,
        REQUEST = 3,
        DECLINE = 4,
        ACK = 5,
        NAK = 6,
        RELEASE = 7,
        INFORM = 8
    };
    
    // DHCP选项
    enum class Option : uint8_t {
        SUBNET_MASK = 1,
        ROUTER = 3,
        DNS_SERVER = 6,
        HOST_NAME = 12,
        DOMAIN_NAME = 15,
        BROADCAST_ADDR = 28,
        TIME_SERVER = 4,
        MESSAGE_TYPE = 53,
        SERVER_ID = 54,
        PARAM_REQUEST = 55,
        RENEWAL_TIME = 58,
        REBINDING_TIME = 59,
        END = 255
    };
    
private:
    void process_options(const uint8_t*, uint16_t);
    DHCPState* state;
};
```

---

## 附录DK： IRC检测器 {#附录dk-irc检测器}

### DK.1 IRC协议分析 {#dk-1-irc协议分析}

```cpp
// irc/irc.h
class IRCInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // IRC消息类型
    enum class IRCCommand {
        NICK,           // 昵称
        USER,           // 用户
        JOIN,           // 加入频道
        PART,           // 离开频道
        QUIT,           // 退出
        PRIVMSG,        // 私信
        NOTICE,         // 通知
        TOPIC,          // 主题
        NAMES,          // 用户列表
        LIST,           // 频道列表
        KICK,           // 踢出
        INVITE,         // 邀请
        MODE,           // 模式
        PING,           // Ping
        PONG,           // Pong
        AWAY,           // 离开
        DCC             // 直接客户端连接
    };
    
    // DCC跟踪
    struct DCCConnection {
        uint32_t src_ip;
        uint32_t dst_ip;
        uint16_t src_port;
        uint16_t dst_port;
        uint64_t bytes_sent;
        uint64_t bytes_expected;
        char* filename;
    };
};
```

---
