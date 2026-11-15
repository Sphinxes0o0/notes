---
title: "Snort 3 · 附录 BI–BY"
description: "附录BI：BitFlags位标志操作 — 附录BY：PubSub事件系统"
---

# Snort 3 · 附录 BI–BY

[返回总目录](../snort3_architecture_analysis)

## 附录BI：BitFlags位标志操作 {#附录bi-bitflags位标志操作}

### BI.1 PROTO_BIT协议位 {#bi-1-proto-bit协议位}

```cpp
// framework/decode_data.h

#define PROTO_BIT__IP      0x000001
#define PROTO_BIT__TCP    0x000002
#define PROTO_BIT__UDP    0x000004
#define PROTO_BIT__ICMP   0x000008
#define PROTO_BIT__USER   0x000010
#define PROTO_BIT__FILE   0x000020
#define PROTO_BIT__PDU    0x000040
#define PROTO_BIT__TEREDO  0x000080
#define PROTO_BIT__GTP    0x000100
#define PROTO_BIT__MPLS    0x000200
#define PROTO_BIT__VLAN    0x000400
#define PROTO_BIT__ETH     0x000800

// 组合标志
#define PROTO_BIT__ANY_IP (PROTO_BIT__IP | PROTO_BIT__TCP | PROTO_BIT__UDP | PROTO_BIT__ICMP)
#define PROTO_BIT__ANY_SSN (PROTO_BIT__ANY_IP | PROTO_BIT__PDU | PROTO_BIT__FILE | PROTO_BIT__USER)
```

---

## 附录BJ：Hash模块 {#附录bj-hash模块}

### BJ.1 Hash Table {#bj-1-hash-table}

```cpp
// hash/hash_main.h

class HashTable {
public:
    HashTable(unsigned n);
    ~HashTable();
    
    // 分配节点
    void* allocate();
    
    // 释放节点
    void deallocate(void*);
    
    // 查找
    void* lookup(const void* key, unsigned key_len) const;
    
    // 添加
    int add(void* node);
    
    // 移除
    int remove(const void* key, unsigned key_len);
};
```

### BJ.2 GHash {#bj-2-ghash}

```cpp
// hash/ghash.h

class GHash {
public:
    GHash(unsigned n, unsigned key_len, unsigned user_size, bool auto_free);
    ~GHash();
    
    // 添加
    int add(void* user);
    
    // 查找
    void* find(const void* key, bool* found = nullptr);
    
    // 移除
    int remove(const void* key);
    
    // 遍历
    void walk(int (*walker)(void*, void*), void* cookie);
};
```

---

## 附录BK：SMTP检测器 {#附录bk-smtp检测器}

### BK.1 SMTP检测器概述 {#bk-1-smtp检测器概述}

SMTP检测器(`src/service_inspectors/smtp/smtp.h`)负责分析SMTP流量，进行邮件过滤和检测。

### BK.2 主要结构 {#bk-2-主要结构}

```cpp
// smtp/smtp_module.h
class SMTPModule : public Inspector {
public:
    SMTPModule(const SnortConfig*);
    ~SMTPModule() override;
    
    void show_stats() override;
    void reset_stats() override;
    
    // 邮件命令验证
    bool validate_command(const char* cmd, size_t len);
    
    // 邮件头验证
    bool validate_header(const char* header);
};
```

### BK.3 SMTP命令处理 {#bk-3-smtp命令处理}

```cpp
// smtp/smtp.h
class SMTPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    StreamSplitter* get_splitter(bool to_server) override {
        return new SMTPStreamSplitter(to_server);
    }
    
private:
    void handle_command(Packet*, const uint8_t*, uint16_t);
    void handle_data(Packet*, const uint8_t*, uint16_t);
    
    SMTPModule* module;
    SMTPState* state;
};
```

---

## 附录BL：FTP/Telnet检测器 {#附录bl-ftp-telnet检测器}

### BL.1 FTP检测器架构 {#bl-1-ftp检测器架构}

FTP检测器处理FTP协议，支持主动和被动模式。

```cpp
// ftp/ftp.h
class FTPParser {
public:
    enum class State {
        WAIT_FOR_REPLY,
        WAIT_FOR_COMMAND,
        WAIT_FOR_DATA,
        WAIT_FOR_RESPONSE
    };
    
    void process(const uint8_t* data, uint16_t len);
    void handle_reply(const uint8_t* data, uint16_t len);
};

// FTP命令处理
enum class FTPCommand {
    USER,   // 用户名
    PASS,   // 密码
    ACCT,   // 账户
    CWD,    // 改变工作目录
    CDUP,   // 改变到父目录
    QUIT,   // 退出
    REIN,   // 重新初始化
    PORT,   // 主动模式端口
    PASV,   // 被动模式
    TYPE,   // 数据类型
    STRU,   // 文件结构
    MODE,   // 传输模式
    RETR,   // 检索文件
    STOR,   // 存储文件
    PWD,    // 打印工作目录
    LIST,   // 列表
    NLST,   // 名称列表
    SITE,   // 站点特定命令
    SYST,   // 系统信息
    STAT,   // 状态
    HELP,   // 帮助
    NOOP    // 无操作
};
```

---

## 附录BM：DNS检测器 {#附录bm-dns检测器}

### BM.1 DNS协议处理 {#bm-1-dns协议处理}

DNS检测器(`src/service_inspectors/dns/dns.h`)支持DNS查询和响应分析。

```cpp
// dns/dns.h
class DnsInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // DNS查询类型
    enum class QueryType {
        A = 1,        // IPv4地址
        NS = 2,       // 名称服务器
        CNAME = 5,    // 别名
        SOA = 6,      // 起始授权机构
        PTR = 12,     // 指针记录
        MX = 15,      // 邮件交换
        TXT = 16,     // 文本记录
        AAAA = 28,    // IPv6地址
        SRV = 33,     // 服务定位
        DNSKEY = 48,  // DNS密钥
        DS = 43       // 委托签名
    };
    
    // DNS响应码
    enum class ResponseCode {
        NOERROR = 0,    // 无错误
        FORMERR = 1,    // 格式错误
        SERVFAIL = 2,   // 服务器失败
        NXDOMAIN = 3,  // 域名不存在
        NOTIMP = 4,     // 未实现
        REFUSED = 5     // 查询被拒绝
    };
    
private:
    void process_query(const uint8_t* data, uint16_t len);
    void process_response(const uint8_t* data, uint16_t len);
    
    void parse_dns_name(const uint8_t*& ptr, char* dest, size_t max_len);
};
```

---

## 附录BN：SSL/TLS检测器 {#附录bn-ssl-tls检测器}

### BN.1 SSL/TLS状态机 {#bn-1-ssl-tls状态机}

SSL检测器追踪SSL握手过程，识别加密流量。

```cpp
// ssl/ssl.h
class SSLState {
public:
    enum class State : uint8_t {
        SERVER_HELLO,        // 服务器hello
        SERVER_CERT,         // 服务器证书
        SERVER_KEY_EX,       // 服务器密钥交换
        CERT_REQ,            // 证书请求
        SERVER_HELLO_DONE,   // 服务器hello完成
        CLIENT_CERT,         // 客户端证书
        CLIENT_KEY_EX,       // 客户端密钥交换
        CERT_VERIFY,         // 证书验证
        CHANGING_CIPHER_SPEC,// 密码规格变更
        APPLICATION_DATA,     // 应用数据
        CLIENT_ALERT,        // 客户端警告
        SERVER_ALERT,        // 服务器警告
        ERROR,               // 错误状态
        MAX_STATE
    };
    
    enum class ContentType : uint8_t {
        CHANGE_CIPHER_SPEC = 20,
        ALERT = 21,
        HANDSHAKE = 22,
        APPLICATION_DATA = 23
    };
    
    enum class HandshakeType : uint8_t {
        HELLO_REQUEST = 0,
        CLIENT_HELLO = 1,
        SERVER_HELLO = 2,
        CERTIFICATE = 11,
        SERVER_KEY_EXCHANGE = 12,
        CERTIFICATE_REQUEST = 13,
        SERVER_HELLO_DONE = 14,
        CERTIFICATE_VERIFY = 15,
        CLIENT_KEY_EXCHANGE = 16,
        FINISHED = 20
    };
};
```

---

## 附录BO：SIP检测器 {#附录bo-sip检测器}

### BO.1 SIP协议分析 {#bo-1-sip协议分析}

SIP检测器用于VoIP流量检测。

```cpp
// sip/sip.h
class SIPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // SIP方法
    enum class Method {
        INVITE,    // 发起会话
        ACK,       // 确认
        BYE,       // 终止会话
        CANCEL,    // 取消请求
        OPTIONS,   // 选项查询
        REGISTER,  // 注册
        PRACK,     // 可靠临时响应
        SUBSCRIBE, // 订阅
        NOTIFY,    // 通知
        INFO,      // 信息
        REFER,     // 参考
        MESSAGE,   // 消息
        UPDATE     // 更新
    };
    
private:
    void handle_request(Packet*, const char* method, const char* uri);
    void handle_response(Packet*, int status_code);
    void process_header(const char* name, const char* value);
};
```

---

## 附录BP：POP3/IMAP检测器 {#附录bp-pop3-imap检测器}

### BP.1 邮件检索协议 {#bp-1-邮件检索协议}

```cpp
// pop/pop.h
class POPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // POP3状态
    enum class State {
        AUTHORIZATION,   // 授权状态
        TRANSACTION,      // 事务状态
        UPDATE            // 更新状态
    };
    
private:
    State state = State::AUTHORIZATION;
};

// imap/imap.h
class IMAPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // IMAP状态
    enum class State {
        NOT_AUTHENTICATED,  // 未认证
        AUTHENTICATED,       // 已认证
        SELECTED,            // 已选择邮箱
        LOGOUT              // 登出
    };
    
    // IMAP命令
    enum class Command {
        LOGIN, AUTHENTICATE, LOGOUT,
        SELECT, EXAMINE, CREATE, DELETE,
        RENAME, SUBSCRIBE, UNSUBSCRIBE,
        LIST, LSUB, STATUS, APPEND,
        CHECK, CLOSE, EXPUNGE,
        SEARCH, FETCH, STORE, COPY,
        UID_COPY, UID_FETCH, UID_SEARCH, UID_STORE
    };
};
```

---

## 附录BQ：SSH检测器 {#附录bq-ssh检测器}

### BQ.1 SSH协议分析 {#bq-1-ssh协议分析}

```cpp
// ssh/ssh.h
class SSHInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // SSH消息类型
    enum class MessageType : uint8_t {
        DISCONNECT = 1,
        IGNORE = 2,
        UNIMPLEMENTED = 3,
        DEBUG = 4,
        SERVICE_REQUEST = 5,
        SERVICE_ACCEPT = 6
    };
    
    // SSH版本标识
    static constexpr const char* SSH_VERSION_STRING = "SSH-2.0-";
    
private:
    void process_protocol_version(const uint8_t* data, uint16_t len);
    void process_server_key_exchange(const uint8_t* data, uint16_t len);
};
```

---

## 附录BR：DNP3检测器 {#附录br-dnp3检测器}

### BR.1 DNP3协议支持 {#br-1-dnp3协议支持}

DNP3是用于SCADA系统的工业控制协议。

```cpp
// dnp3/dnp3.h
class DNP3Inspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // DNP3功能码
    enum class FunctionCode : uint8_t {
        READ = 1,
        WRITE = 2,
        SELECT = 3,
        OPERATE = 4,
        DIRECT_OPERATE = 5,
        RESPONSE = 129,
        UNSOLICITED_RESPONSE = 130
    };
    
    // DNP3对象组
    enum class ObjectGroup : uint16_t {
        GROUP_1 = 1,   // 二进制输入
        GROUP_2 = 2,   // 二进制输入变化
        GROUP_10 = 10, // 二进制输出
        GROUP_30 = 30, // 模拟输入
        GROUP_40 = 40  // 模拟输出
    };
};
```

---

## 附录BS：Base64编码处理 {#附录bs-base64编码处理}

### BS.1 Base64解码 {#bs-1-base64解码}

Snort 3提供Base64编码数据的解码支持。

```cpp
// utils/base64.h
class Base64 {
public:
    // 解码
    // @param input 要解码的Base64字符串
    // @param input_len 输入长度
    // @param output 输出缓冲区
    // @param output_len 输出缓冲区和实际解码长度
    // @return 解码是否成功
    static bool decode(const char* input, size_t input_len,
                       uint8_t* output, size_t* output_len);
    
    // 编码
    // @param input 输入数据
    // @param input_len 输入长度
    // @param output 输出缓冲区
    // @param output_len 输出缓冲区和实际编码长度
    static bool encode(const uint8_t* input, size_t input_len,
                       char* output, size_t* output_len);
    
    // Base64字符表
    static constexpr const char* CHARSET = 
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
};
```

### BS.2 使用示例 {#bs-2-使用示例}

```cpp
// 在规则选项中使用Base64解码
// content:"dXNlcj1ob3N0"; base64;

uint8_t decoded[256];
size_t decoded_len = sizeof(decoded);

if ( Base64::decode("dXNlcj1ob3N0", 16, decoded, &decoded_len) ) {
    // 处理解码后的数据
}
```

---

## 附录BT：Packet结构深度解析 {#附录bt-packet结构深度解析}

### BT.1 Packet数据结构 {#bt-1-packet数据结构}

```cpp
// protocols/packet.h

struct Packet : public DataBuffer {
    // 引用计数
    THASH_CLASS(atomic_t, ref_count);
    
    // 数据包属性
    struct PacketFlags {
        uint32_t is_encrypted : 1;         // 加密数据包
        uint32_t is_loopback : 1;          // 环回接口
        uint32_t is_eth_offset : 1;        // 以太网偏移
        uint32_t is_vlan : 1;              // VLAN标签
        uint32_t is_mpls : 1;              // MPLS标签
        uint32_t is_ip_checksum_disabled : 1; // IP校验和禁用
        uint32_t is_ttl_invalid : 1;       // TTL无效
        uint32_t packet_is_encrypted : 1;  // 数据包本身加密
        uint32_t inline_mode_drop : 1;      // 内联模式丢弃
        uint32_t rebuilt : 1;              // 重组数据包
        uint32_t pseudo : 1;               // 伪数据包
        uint32_t pseudo_type : 3;          // 伪包类型
        uint32_t log_generated : 1;         // 日志已生成
        uint32_t turn_off_action : 1;       // 关闭动作
        uint32_t action_set : 1;           // 动作已设置
        uint32_t xtrdbuf_locked : 1;        // 外部缓冲区锁定
    } pkt_flags;
    
    // 数据包类型
    PktType type;
    
    // 指针
    const uint8_t* data;          // 数据包数据指针
    uint16_t dsize;                 // 数据大小
    
    // 协议栈指针
    EtherHdr* ether;
    VLANHdr* vlan;
    MPLSHdr* mpls;
    IPHdr* ip_api;
    TCPHdr* tcph;
    UDPHdr* udph;
    ICMPHdr* icmph;
    
    // 流指针
    Flow* flow;
    
    // 隧道信息
    Packet* outer_pkt;  // 外部数据包（用于隧道）
    
    // DAQ元数据
    DAQ_PktHdr_t* pkth;
    
    // 时间戳
    struct timeval timestamp;
    
    // 应用层数据
    uint16_t app_id;
    void* app_data;
};
```

---

## 附录BU：Flow数据结构深度解析 {#附录bu-flow数据结构深度解析}

### BU.1 Flow结构详解 {#bu-1-flow结构详解}

```cpp
// flow/flow.h

class Flow : public HashTableNoLock::Node {
public:
    // 流状态
    enum State : uint8_t {
        FLOW_STATE_OPEN = 0,      // 开放
        FLOW_STATE_OPENING,       // 正在打开
        FLOW_STATE_ESTABLISHED,   // 已建立
        FLOW_STATE_CLOSING,       // 正在关闭
        FLOW_STATE_STATE_NONE     // 无状态
    };
    
    // 流方向
    enum Direction : uint8_t {
        SSN_DIR_NONE = 0,         // 无方向
        FROM_CLIENT = 1,           // 从客户端
        FROM_SERVER = 2,           // 从服务器
        BOTH_FLAGS = 3             // 双向
    };
    
    // 服务信息
    const char* service;          // 检测到的服务
    AppId app_id;                  // 应用ID
    
    // 会话信息
    class Session* session;       // 会话指针
    struct FlowKey* key;           // 流键
    
    // 协议信息
    IpApi ip_api;                  // IP地址信息
    uint16_t sport;                // 源端口
    uint16_t dport;                // 目标端口
    
    // 标志
    struct FlowFlags {
        uint32_t ssn_init : 1;         // 会话已初始化
        uint32_t turn_off : 1;         // 关闭会话
        uint32_t no_inspect : 1;       // 不检查
        uint32_t midstream : 1;        // 中途会话
        uint32_t ignore : 1;            // 忽略
        uint32_t replaced : 1;         // 已替换
        uint32_t client_init : 1;      // 客户端已初始化
        uint32_t server_init : 1;      // 服务器已初始化
        uint32_t established : 1;       // 已建立
        uint32_t svc_event_generated : 1; // 服务事件已生成
    } flags;
    
    // 用户数据
    FlowData* flow_data;           // 流数据链表
    
    // 时间戳
    struct timeval start_time;      // 开始时间
    struct timeval last_time;      // 最后时间
    
    // 统计
    uint64_t bytes;                // 总字节数
    uint64_t packets;              // 总包数
    
    // 过期标志
    bool expire_ttl = false;
    
    // 清理回调
    void (*callback)(Flow*);
    
    // 获取应用层协议ID
    AppId get_application_protocol_id() const;
    
    // 获取流方向
    Direction get_direction(const Packet*) const;
};
```

---

## 附录BV： IpsAction系统详解 {#附录bv-ipsaction系统详解}

### BV.1 Action基类 {#bv-1-action基类}

```cpp
// ips_actions/ips_action.h

class IpsAction {
public:
    virtual ~IpsAction() = default;
    
    // 执行动作
    virtual void exec(Packet*, PacketNotes*) = 0;
    
    // 获取动作名称
    virtual const char* get_name() const = 0;
    
    // 获取动作类型
    virtual IpsAction::Type get_type() const = 0;
    
    // 获取分类信息
    virtual bool get_classification(std::string&) const;
};

// Action类型
enum class Type {
    ALLOW,     // 允许
    DROP,      // 丢弃
    REJECT,    // 拒绝
    ALERT,     // 警报
    LOG,       // 日志
    BLOCK,     // 阻止
    ENABLE,    // 启用
    DISABLE    // 禁用
};
```

### BV.2 Action实现 {#bv-2-action实现}

```cpp
// ips_actions/active_action.h
class ActiveAction : public IpsAction {
public:
    ActiveAction(Type, const char* name, PacketDrop::DropReason = PacketDrop::NOT_SET);
    ~ActiveAction() override;
    
    void exec(Packet*, PacketNotes*) override;
    
    // 获取删除原因
    PacketDrop::DropReason get_drop_reason() const;
};
```

---

## 附录BW：DetectionEngine深度解析 {#附录bw-detectionengine深度解析}

### BW.1 检测流程 {#bw-1-检测流程}

```cpp
// detection/detection_engine.h

class DetectionEngine {
public:
    // 开始检测
    static void begin(Packet*);
    
    // 结束检测
    static void end();
    
    // 执行选项检测
    static int detect(IpsPolicy*, Packet*);
    
    // 快速模式匹配
    static void fp_search(InspectionBuffer&, const DetectOptionCategory&);
    
    // 获取模块
    static DetectionModule* get_detection_module();
    
    // 验证配置
    static bool validate();
};
```

### BW.2 检测上下文 {#bw-2-检测上下文}

```cpp
struct DetectionContext {
    IpsPolicy* ips_policy;     // IPS策略
    Packet* packet;             // 当前数据包
    InspectionBuffer buffer;    // 检测缓冲区
    
    // 检测选项
    OptTreeNode* otn;          // 选项树节点
    
    // 匹配状态
    bool match;                 // 是否匹配
};
```

---

## 附录BX：Module系统详解 {#附录bx-module系统详解}

### BX.1 Module基类 {#bx-1-module基类}

```cpp
// framework/module.h

class Module {
public:
    Module(const char* name, const char* help);
    virtual ~Module() = default;
    
    // 模块名称
    const char* get_name() const
    { return name; }
    
    // 获取参数
    virtual bool set(const char*, Value&, SnortConfig*) = 0;
    virtual bool begin(const char*, int, SnortConfig*) = 0;
    virtual bool end(const char*, int, SnortConfig*) = 0;
    
    // 统计数据
    virtual void show_stats() {}
    virtual void reset_stats() {}
    
    // 配置历史
    virtual HistoryList* get_history() const;
    
    // 参数列表
    virtual const Param* get_params() const = 0;
    
    // 级别
    virtual unsigned get_gid() const;
    virtual unsigned get_sid() const;
    
    // 模块数据
    void* get_data() const;
    void* get_mutable_data() const;
    void set_data(void*);
    
    // 权限
    bool is_privileged() const;
    bool is_exclusive() const;
};
```

### BX.2 模块注册 {#bx-2-模块注册}

```cpp
// 模块宏定义
#define MODULE(name, help, gid, sid) \
    class Module_##name : public Module { \
    public: \
        Module_##name() : Module(#name, help) { } \
        const char* get_name() const override { return #name; } \
        unsigned get_gid() const override { return gid; } \
        unsigned get_sid() const override { return sid; } \
        bool set(const char*, Value&, SnortConfig*) override; \
        bool begin(const char*, int, SnortConfig*) override; \
        bool end(const char*, int, SnortConfig*) override; \
    };
```

---

## 附录BY：PubSub事件系统 {#附录by-pubsub事件系统}

### BY.1 DataBus发布订阅 {#by-1-databus发布订阅}

```cpp
// pub_sub/data_bus.h

class DataBus {
public:
    // 订阅事件
    static void subscribe(unsigned id, EventHandler* handler);
    
    // 取消订阅
    static void unsubscribe(unsigned id, EventHandler* handler);
    
    // 发布事件
    static void publish(unsigned id, unsigned char* data);
    
    // 发布事件（带Packet）
    static void publish(unsigned id, Packet*);
    
    // 清除所有订阅
    static void clear();
};
```

### BY.2 事件处理 {#by-2-事件处理}

```cpp
// pub_sub/event_handler.h

class EventHandler {
public:
    virtual ~EventHandler() = default;
    
    // 处理事件
    virtual void handle(snort::Packet*) = 0;
    
    // 订阅者名称
    const char* get_name() const
    { return name; }
    
    // 订阅者ID
    unsigned get_id() const
    { return id; }
    
    // 订阅者数据
    void* get_data() const
    { return data; }
};
```

### BY.3 常见事件ID {#by-3-常见事件id}

```cpp
// pub_sub/intrinsic_event_ids.h

namespace IntrinsicEventIds {
    // 事件ID定义
    enum {
        FLOW_NO_SERVICE = 0,     // 无服务检测到
        FLOW_SOFTED,              // 流已编辑
        DEBUG_FLOW,               // 调试流
        ...
    };
    
    static constexpr unsigned intrinsic_pub_id = 0;
}
```

---
