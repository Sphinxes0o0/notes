---
title: "Snort 3 · 附录 KK–LB"
description: "附录KK： 配置文件详解 — 附录LB： 规则选项类型"
---

# Snort 3 · 附录 KK–LB

[返回总目录](../snort3_architecture_analysis)

## 附录KK： 配置文件详解 {#附录kk-配置文件详解}

### KK.1 snort.lua结构 {#kk-1-snort-lua结构}

```lua
-- snort.lua配置文件结构

-- ==================== --
-- 1. 基础配置
-- ====================
{
    -- 网络配置
    home_net = "192.168.0.0/16",
    external_net = "!" .. home_net,
    
    -- 规则路径
    rules = [[
        alert tcp any any -> any 80 (msg:"HTTP"; sid:1000001;)
    ]],
}

-- ==================== --
-- 2. 处理器配置
-- ====================
preprocessors = {
    -- 流预处理器
    stream = {
        enable = true,
        tracking = "stateful",
    },
    
    -- 告警预处理
    alert = {
        enable = true,
    },
}

-- ==================== --
-- 3. 检查器配置
-- ====================
inspectors = {
    -- HTTP检查器
    http_inspect = {
        enable = true,
        profile = "high",
    },
    
    -- SMTP检查器
    smtp = {
        enable = true,
    },
}

-- ==================== --
-- 4. 输出配置
-- ====================
output = {
    -- 告警输出
    alert_fast = {
        enable = true,
        file = "/var/log/snort/alert.txt",
    },
}
```

### KK.2 配置合并 {#kk-2-配置合并}

```cpp
// 配置合并规则

// 规则:
// 1. 表(table)用merge覆盖，不存在则创建
// 2. 数组(array)用append扩展
// 3. 标量(scalar)用新值覆盖旧值
// 4. nil删除键

-- 示例:
-- base.lua:
config = { a = 1, b = 2 }

-- overlay.lua:
config = { b = 3, c = 4 }

-- 结果:
-- { a = 1, b = 3, c = 4 }
```

---

## 附录KL： 性能调优参数 {#附录kl-性能调优参数}

### KL.1 系统参数 {#kl-1-系统参数}

```bash
# /etc/sysctl.conf

# 网络内存
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864

# 文件描述符
fs.file-max = 2097152

# 内存
vm.swappiness = 10
vm.dirty_ratio = 60
vm.dirty_background_ratio = 5
```

### KL.2 Snort参数 {#kl-2-snort参数}

```lua
-- 性能调优配置
stream = {
    max_queued_bytes = 8388608,
    max_queued_segs = 32768,
}

detection = {
    search_method = "ac",
    max_pattern_len = 1024,
}

memory = {
    memcap = 4294967296,
}
```

---

## 附录KM： 安全加固清单 {#附录km-安全加固清单}

### KM.1 系统加固 {#km-1-系统加固}

```bash
# 1. 用户权限
useradd -r -s /sbin/nologin snort
chown -R snort:snort /var/log/snort
chmod -R 700 /var/log/snort

# 2. 文件权限
chmod 600 /etc/snort/snort.lua
chmod 600 /etc/snort/rules/*.rules
chmod 700 /usr/bin/snort

# 3. 能力
setcap cap_net_raw,cap_net_admin=eip /usr/bin/snort

# 4. seccomp
snort --seccomp
```

---

## 附录KN： 故障排查指南 {#附录kn-故障排查指南}

### KN.1 常见问题 {#kn-1-常见问题}

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 启动失败 | 配置文件错误 | snort -T 检查 |
| 包丢失严重 | 性能不足 | 调整preprocessor_memcap |
| 内存持续增长 | 内存泄漏 | 更新版本/报告bug |
| 规则不匹配 | 规则错误 | 检查规则语法 |
| CPU占用高 | 规则复杂 | 优化规则，使用fast_pattern |

### KN.2 诊断命令 {#kn-2-诊断命令}

```bash
# 配置验证
snort -c /etc/snort/snort.lua -T

# 详细输出
snort -c /etc/snort/snort.lua -v -v -v -i eth0

# 规则调试
snort -c /etc/snort/snort.lua --rule-profile

# 统计信息
snort -c /etc/snort/snort.lua --stat

# 内存跟踪
valgrind --leak-check=full snort -c snort.lua -i eth0
```

---

## 附录KO： 参考资料 {#附录ko-参考资料}

### KO.1 官方资源 {#ko-1-官方资源}

- 官方网站: https://www.snort.org
- 文档: https://snort.org/documents
- 社区: https://www.snort.org/community
- 源代码: https://github.com/snort3/snort3

### KO.2 协议规范 {#ko-2-协议规范}

- RFC 791 - IPv4
- RFC 793 - TCP
- RFC 768 - UDP
- RFC 2460 - IPv6
- RFC 792 - ICMP

### KO.3 学习路径 {#ko-3-学习路径}

1. 入门: 阅读官方文档，运行基本配置
2. 进阶: 理解架构，编写规则
3. 高级: 开发自定义Inspector
4. 专家: 性能优化，内核集成

---

*文档最终版本: 20.0*
*最终更新: 2026年4月10日*
*总行数: 21000+*

*本文档是Snort 3源码架构分析的完整版本，涵盖架构设计、模块实现、数据结构、协议处理、检测机制、配置系统和运维工具等全部核心内容，深入到函数和结构体级别。*


---

## 附录KP： 协议处理器映射 {#附录kp-协议处理器映射}

### KP.1 端口到服务映射 {#kp-1-端口到服务映射}

```cpp
// ports/port_table.h

// 端口到检查器的标准映射
static const PortTableEntry standard_port_table[] = {
    // HTTP服务
    { 80, "http", "http_inspect" },
    { 443, "https", "ssl" },
    { 8080, "http", "http_inspect" },
    { 8443, "https", "ssl" },
    
    // 邮件服务
    { 25, "smtp", "smtp" },
    { 110, "pop3", "pop3" },
    { 143, "imap", "imap" },
    
    // 文件传输
    { 20, "ftp", "ftp" },
    { 21, "ftp", "ftp" },
    { 22, "ssh", "ssh" },
    { 23, "telnet", "telnet" },
    
    // 数据库
    { 3306, "mysql", nullptr },
    { 5432, "postgresql", nullptr },
    { 1433, "mssql", nullptr },
    
    // 其他
    { 53, "dns", "dns" },
    { 67, "dhcp", "dhcp" },
    { 161, "snmp", "snmp" },
    { 514, "syslog", nullptr },
};

// 端口表结构
struct PortTableEntry {
    uint16_t port;           // 端口号
    const char* service;     // 服务名称
    const char* inspector;    // 检查器名称
};

// 端口列表
struct PortList {
    uint16_t ports[16];       // 端口列表
    unsigned count;           // 端口数量
    bool any;                 // 是否任意端口
    bool negated;             // 是否取反
};
```

---

## 附录KQ： 事件处理 {#附录kq-事件处理}

### KQ.1 Intrinsic事件 {#kq-1-intrinsic事件}

```cpp
// pub_sub/intrinsic_event_ids.h

// 内部事件ID定义
namespace IntrinsicEventIds {
    enum {
        FLOW_NO_SERVICE = 0,     // 流未检测到服务
        FLOW_SOFTED,           // 流被软编辑
        DEBUG_FLOW,            // 流调试
        FLOW_NEW,              // 新流创建
        FLOW_DELETE,           // 流删除
        PACKET_DETAINED,       // 数据包被扣留
        DETECTION_ALERT,       // 检测告警
    };
}

// 发布事件
class DataBus {
public:
    // 发布事件
    static void publish(unsigned id, Packet* p) {
        // 查找所有订阅者并调用其处理函数
    }
    
    // 订阅事件
    static void subscribe(unsigned id, EventHandler* handler) {
        subscribers_[id].push_back(handler);
    }
    
    // 取消订阅
    static void unsubscribe(unsigned id, EventHandler* handler) {
        // 从订阅者列表中移除
    }
};
```

---

## 附录KR： 属性表 {#附录kr-属性表}

### KR.1 主机属性 {#kr-1-主机属性}

```cpp
// host_tracker/host_attributes.h

// 主机属性表 - 存储主机的已知属性
class HostAttributes {
public:
    // 添加主机属性
    void add_attribute(const SfIp* ip, const HostAttribute& attr);
    
    // 获取主机属性
    const HostAttribute* get_attribute(const SfIp* ip) const;
    
    // 主机属性结构
    struct HostAttribute {
        // 服务信息
        struct ServiceInfo {
            uint16_t port;           // 端口
            IpProtocol protocol;    // 协议
            const char* service;    // 服务名称
            const char* application; // 应用
        };
        
        std::vector<ServiceInfo> services;  // 服务列表
        
        // 操作系统信息
        struct OsInfo {
            const char* name;       // OS名称
            const char* version;    // 版本
            const char* cpe;        // CPE标识
        };
        
        OsInfo os_info;
        
        // 协议信息
        std::map<uint16_t, const char*> protocols;
    };
};
```

---

## 附录KS： 规则动作系统 {#附录ks-规则动作系统}

### KS.1 动作类型 {#ks-1-动作类型}

```cpp
// actions/ips_action.h

// 规则动作
namespace IpsAction {
    enum Type {
        ALLOW,     // 允许通过
        DROP,      // 丢弃
        REJECT,    // 拒绝连接
        ALERT,     // 报警
        LOG,       // 记录日志
        BLOCK,     // 阻止
        ENABLE,    // 启用
        DISABLE    // 禁用
    };
}

// 动作信息
struct ActionInfo {
    const char* name;      // 动作名称
    const char* help;     // 帮助信息
    uint32_t flags;       // 标志
};

// 动作注册表
class ActionRegistry {
public:
    static ActionRegistry& get() {
        static ActionRegistry instance;
        return instance;
    }
    
    void register_action(Type type, const ActionInfo& info) {
        actions_[type] = info;
    }
    
    const ActionInfo* get_action(Type type) const {
        return &actions_[type];
    }
    
private:
    std::map<Type, ActionInfo> actions_;
};
```

---

## 附录KT： 规范化策略 {#附录kt-规范化策略}

### KT.1 TCP规范化 {#kt-1-tcp规范化}

```cpp
// stream/tcp/tcp_normalizers.h

// TCP规范化策略
struct TcpNormalizerPolicy {
    // 数据包规范化选项
    bool drop_invalid = false;       // 丢弃无效数据包
    bool drop_obselete = false;     // 丢弃过时数据包
    bool drop_frags = false;       // 丢弃分片
    bool block_unisigned = false;   // 阻止无符号数据
    bool block_rfc1323 = false;     // 阻止RFC1323
    bool trim_syn = false;          // 修剪SYN
    bool trim_rst = false;         // 修剪RST
    bool trim_mid = false;         // 修剪中间数据
    bool trim_win = false;         // 修剪窗口
    bool trim_ood = false;         // 修剪乱序
    bool require_3way = false;      // 要求三次握手
    
    // 规范化方法
    enum class TrimMethod {
        TRIM_NONE,     // 不修剪
        TRIM_MAX,      // 修剪到最大
        TRIM_MIN       // 修剪到最小
    };
};

// 数据包规范化器
class TcpNormalizer {
public:
    // 规范化数据包
    bool normalize_packet(Packet* p);
    
    // 规范化序列号
    bool normalize_seq(Packet* p, uint32_t seq);
    
    // 规范化选项
    uint8_t normalize_options(uint8_t* opts, uint16_t len);
};
```

---

## 附录KU： 协议识别 {#附录ku-协议识别}

### KU.1 应用协议识别流程 {#ku-1-应用协议识别流程}

```cpp
// network_inspectors/wizard/wizard.cc

// 服务检测流程
class Wizard {
public:
    // 检测服务
    bool detect_service(Packet* p, Flow* f) {
        // 1. 检查已知端口
        const char* service = lookup_port_service(p->dst_port);
        if (service) {
            f->service = service;
            return true;
        }
        
        // 2. 使用魔术字节匹配
        if (match_magic_bytes(f, p->data, p->dsize)) {
            return true;
        }
        
        // 3. 使用协议特征匹配
        if (match_protocol_patterns(f, p->data, p->dsize)) {
            return true;
        }
        
        // 4. 无法识别
        return false;
    }
    
private:
    // 魔术字节数据库
    MagicBook* c2s_hexes_;   // 客户端到服务端
    MagicBook* s2c_hexes_;   // 服务端到客户端
    
    // 协议特征数据库
    MagicBook* c2s_spells_;  // 客户端到服务端
    MagicBook* s2c_spells_;  // 服务端到客户端
    
    // Curse跟踪器(用于复杂协议)
    std::vector<CurseTracker*> curse_trackers_;
};

// 魔术字节匹配
bool Wizard::match_magic_bytes(Flow* f, const uint8_t* data, unsigned len) {
    for (const auto& magic : magic_database_) {
        if (match_pattern(magic.pattern, data, len)) {
            f->service = magic.service;
            return true;
        }
    }
    return false;
}
```

---

## 附录KV： 检测选项链 {#附录kv-检测选项链}

### KV.1 选项评估顺序 {#kv-1-选项评估顺序}

```cpp
// detection/treenorm.h

// 检测选项链表
struct OptList {
    OptList* next;           // 下一个选项
    IpsOption* ips_option;   // IPS选项
    PatternMatchData* pmd;  // 模式匹配数据
};

// 选项树评估
class OptionTreeEvaluator {
public:
    // 评估选项树
    int eval(OptList* list, Cursor& c, Packet* p, IpsContext* ctx) {
        OptList* curr = list;
        bool short_circuit = true;
        
        while (curr) {
            // 评估单个选项
            int result = curr->ips_option->eval(c, p, ctx);
            
            // 处理结果
            if (result == 0) {
                // 选项不匹配
                return 0;
            }
            
            // 检查是否为取反匹配
            if (result < 0) {
                // 取反 - 如果原始匹配则最终不匹配
                short_circuit = false;
            }
            
            curr = curr->next;
        }
        
        return short_circuit ? 1 : -1;
    }
};
```

---

## 附录KW： 正则表达式处理 {#附录kw-正则表达式处理}

### KW.1 PCRE引擎 {#kw-1-pcre引擎}

```cpp
// ips_options/pcre.h

// PCRE选项实现
class PcreOption : public IpsOption {
public:
    PcreOption(const char* pattern, const char* options);
    
    OptionType get_type() const override { return OptionType::PCRE; }
    
    int eval(Cursor& c, Packet* p, IpsContext* ctx) override;
    
    const void* get_data() const override { return pattern_; }
    
    void print() const override;
    
    // PCRE编译标志
    enum PcreFlags {
        CASE_INSENSITIVE = 0x01,
        MULTILINE = 0x02,
        DOTALL = 0x04,
        EXTENDED = 0x08,
        ANCHORED = 0x10,
        DOLLAR_ENDONLY = 0x20
    };
    
private:
    pcre* re_;              // 编译后的正则
    pcre_extra* study_;    // 学习信息
    const char* pattern_;  // 原始模式
    const char* options_;  // 选项字符串
    int ovec_[30];         // 匹配位置数组
};
```

---

## 附录KX： 快速模式匹配 {#附录kx-快速模式匹配}

### KX.1 AC自动机 {#kx-1-ac自动机}

```cpp
// search_engines/ac/ac.h

// Aho-Corasick自动机实现
class AC {
public:
    AC();
    ~AC();
    
    // 添加模式
    void add_pattern(const uint8_t* pat, unsigned len, unsigned id);
    
    // 初始化构建
    void init();
    
    // 搜索
    int search(const uint8_t* text, unsigned len,
              unsigned* matches, unsigned max_matches);
    
    // 获取统计
    unsigned get_pattern_count() const { return num_patterns_; }
    unsigned get_node_count() const { return num_nodes_; }
    
private:
    // 节点结构
    struct Node {
        Node* next[256];   // 下一个节点指针数组
        Node* fail;       // 失败函数指针
        unsigned output;   // 输出标志
        unsigned id;      // 模式ID
    };
    
    Node* root_;               // 根节点
    unsigned num_patterns_;   // 模式数量
    unsigned num_nodes_;      // 节点数量
};
```

---

## 附录KY： 分片重组 {#附录ky-分片重组}

### KY.1 IP分片处理 {#ky-1-ip分片处理}

```cpp
// network_inspectors/frag/frag.h

// 分片重组器
class FragmentRewriter {
public:
    // 处理分片
    bool process_fragment(Packet* p, uint32_t ip_id, 
                        uint32_t src_ip, uint32_t dst_ip);
    
    // 重组完整数据包
    Packet* reassemble(const FlowKey* key);
    
    // 清理过期分片
    void purge_expired();
    
private:
    // 分片缓存
    struct FragmentCache {
        struct FragmentNode {
            uint32_t seq;           // 序列号
            uint16_t len;           // 长度
            uint8_t* data;          // 数据
            struct timeval tv;      // 时间戳
            FragmentNode* next;     // 下一个
        };
        
        FlowKey key;               // 流键
        uint32_t src_ip;          // 源IP
        uint32_t dst_ip;          // 目标IP
        uint16_t ip_id;           // IP标识
        FragmentNode* fragments;  // 分片链表
        uint32_t total_len;      // 总长度
        uint8_t flags;            // 标志
    };
    
    std::map<FlowKey, FragmentCache*> cache_;
};
```

---

## 附录KZ： 日志格式 {#附录kz-日志格式}

### KZ.1 日志类型 {#kz-1-日志类型}

```cpp
// loggers/alert_fast.h

// 快速告警格式
class AlertFast {
public:
    AlertFast();
    ~AlertFast();
    
    void open(const char* path);
    void close();
    
    // 写告警
    void write(const Packet* p, const char* msg, uint32_t gid, uint32_t sid);
    
    // 格式: timestamp GID:SID:REV msg Protocol Src -> Dst
    // 示例: 04/10-15:30:45.123456 1:1000001:1 HTTP GET 192.168.1.1:12345 -> 192.168.1.2:80
};

// CSV告警格式
class AlertCSV {
public:
    void write(const Packet* p, const Event* e);
    
    // CSV字段: timestamp,gid,sid,rev,msg,src_ip,src_port,dst_ip,dst_port,proto,priority
};
```

---

## 附录LA： 端口列表处理 {#附录la-端口列表处理}

### LA.1 端口列表解析 {#la-1-端口列表解析}

```cpp
// ports/port_object.h

// 端口对象
class PortObject {
public:
    // 从字符串解析
    static PortObject* parse(const char* str);
    
    // 端口范围
    struct Range {
        uint16_t lo;    // 低端
        uint16_t hi;    // 高端
    };
    
    // 检查端口是否匹配
    bool contains(uint16_t port) const;
    
    // 获取端口列表
    const std::vector<Range>& get_ranges() const { return ranges_; }
    
    // 是否任意端口
    bool is_any() const { return flags_ & FLAG_ANY; }
    
    // 是否取反
    bool is_negated() const { return flags_ & FLAG_NEGATED; }
    
private:
    std::vector<Range> ranges_;
    uint8_t flags_;
    
    enum Flags {
        FLAG_ANY = 0x01,
        FLAG_NEGATED = 0x02
    };
};

// 端口列表
class PortObjectList {
public:
    void add(PortObject* port_obj);
    void remove(const PortObject* port_obj);
    
    bool contains(uint16_t port) const;
    
private:
    std::vector<PortObject*> ports_;
};
```

---

## 附录LB： 规则选项类型 {#附录lb-规则选项类型}

### LB.1 支持的选项 {#lb-1-支持的选项}

```cpp
// ips_options/ips_option.h

// 规则选项类型
enum class OptionType {
    // 内容匹配
    CONTENT,           // content
    RAW_CONTENT,       // rawbytes
    
    // 正则
    PCRE,             // pcre
    
    // 协议字段
    TCP_FLAGS,        // tcp_flags
    ICMP_TYPE,       // icmp_type
    ICMP_CODE,       // icmp_code
    IP_PROTO,        // ip_proto
    
    // 流选项
    FLOW,            // flow
    FLOWbits,        // flowbits
    
    // 字节操作
    BYTE_TEST,       // byte_test
    BYTE_JUMP,       // byte_jump
    BYTE_EXTRACT,    // byte_extract
    
    // 距离/偏移
    DISTANCE,        // distance
    OFFSET,          // offset
    WITHIN,          // within
    
    // HTTP选项
    HTTP_METHOD,     // http_method
    HTTP_URI,        // http_uri
    HTTP_HEADER,     // http_header
    HTTP_COOKIE,     // http_cookie
    HTTP_BODY,       // http_body
    HTTP_STAT_CODE,  // http_stat_code
    HTTP_STAT_MSG,    // http_stat_msg
    
    // 文件选项
    FILE_DATA,       // file_data
    FILE_TYPE,       // file_type
    FILE_SIGNATURE,  // file_signature
    
    // 特殊选项
    STICKY_BUFFER,  // sticky_buffer
    DETECTION_FILTER, // detection_filter
    THRESHOLD,        // threshold
    METADATA,         // metadata
    SID,              // sid
    GID,              // gid
    REV,              // rev
    MSG,              // msg
    CLASSTYPE,        // classtype
    PRIORITY,         // priority
    REFERENCE,        // reference
};
```

---
