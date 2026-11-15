---
title: "Snort 3 · 附录 DL–EE"
description: "附录DL： SNMP检测器 — 附录EE： 线程局部存储"
---

# Snort 3 · 附录 DL–EE

[返回总目录](../snort3_architecture_analysis)

## 附录DL： SNMP检测器 {#附录dl-snmp检测器}

### DL.1 SNMP处理 {#dl-1-snmp处理}

```cpp
// snmp/snmp.h
class SNMPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // SNMP版本
    enum class Version : uint8_t {
        V1 = 0,
        V2C = 1,
        V2U = 2,
        V3 = 3
    };
    
    // SNMP PDU类型
    enum class PDUType : uint8_t {
        GET_REQUEST = 0,
        GET_NEXT_REQUEST = 1,
        GET_RESPONSE = 2,
        SET_REQUEST = 3,
        TRAP = 4,
        GET_BULK_REQUEST = 5,
        INFORM_REQUEST = 6,
        V2_TRAP = 7,
        REPORT = 8
    };
    
    // SNMP对象标识符
    struct OID {
        uint32_t* oid;  // OID值
        uint32_t len;   // OID长度
    };
};
```

---

## 附录DM： SSH检测器 {#附录dm-ssh检测器}

### DM.1 SSH协议握手 {#dm-1-ssh协议握手}

```cpp
// ssh/ssh.h
class SSHInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // SSH消息码
    enum class MessageCode : uint8_t {
        SSH_MSG_DISCONNECT = 1,
        SSH_MSG_IGNORE = 2,
        SSH_MSG_UNIMPLEMENTED = 3,
        SSH_MSG_DEBUG = 4,
        SSH_MSG_SERVICE_REQUEST = 5,
        SSH_MSG_SERVICE_ACCEPT = 6
    };
    
    // SSH密钥交换算法
    enum class KexAlgorithm {
        DIFFIE_HELLMAN_GROUP1_SHA1,
        DIFFIE_HELLMAN_GROUP14_SHA1,
        DIFFIE_HELLMAN_GROUP14_SHA256,
        ECDH_SHA2_NISTP256,
        ECDH_SHA2_NISTP384,
        ECDH_SHA2_NISTP521
    };
    
    // 服务器密钥算法
    enum class ServerKeyAlgorithm {
        SSH_RSA,
        SSH_DSS,
        ECDSA_NISTP256,
        ECDSA_NISTP384,
        ECDSA_NISTP521,
        ED25519
    };
};
```

---

## 附录DN： SMB检测器 {#附录dn-smb检测器}

### DN.1 SMB协议处理 {#dn-1-smb协议处理}

```cpp
// smb/smb.h
class SMBInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // SMB命令
    enum class SMBCommand : uint8_t {
        SMB_COM_CREATE_DIRECTORY = 0x00,
        SMB_COM_DELETE_DIRECTORY = 0x01,
        SMB_COM_OPEN = 0x02,
        SMB_COM_CREATE = 0x03,
        SMB_COM_CLOSE = 0x04,
        SMB_COM_FLUSH = 0x05,
        SMB_COM_DELETE = 0x06,
        SMB_COM_RENAME = 0x07,
        SMB_COM_QUERY_INFORMATION = 0x08,
        SMB_COM_SET_INFORMATION = 0x09,
        SMB_COM_READ = 0x0A,
        SMB_COM_WRITE = 0x0B,
        SMB_COM_LOCK_BYTE_RANGE = 0x0C,
        SMB_COM_UNLOCK_BYTE_RANGE = 0x0D,
        SMB_COM_CREATE_TEMPORARY = 0x17,
        SMB_COM_CREATE_NEW = 0x12
    };
    
    // SMB2命令
    enum class SMB2Command : uint16_t {
        SMB2_NEGOTIATE = 0x0000,
        SMB2_SESSION_SETUP = 0x0001,
        SMB2_LOGOFF = 0x0002,
        SMB2_TREE_CONNECT = 0x0003,
        SMB2_TREE_DISCONNECT = 0x0004,
        SMB2_CREATE = 0x0005,
        SMB2_CLOSE = 0x0006,
        SMB2_READ = 0x0008,
        SMB2_WRITE = 0x0009
    };
    
private:
    void process_smb1(Packet*, const uint8_t*, uint16_t);
    void process_smb2(Packet*, const uint8_t*, uint16_t);
};
```

---

## 附录DO： DCERPC检测器 {#附录do-dcerpc检测器}

### DO.1 DCERPC协议 {#do-1-dcerpc协议}

```cpp
// dcerpc/dcerpc.h
class DCERPCInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // DCERPC版本
    enum class Version : uint8_t {
        V4 = 4,
        V5 = 5
    };
    
    // DCERPC PDU类型
    enum class PDUType : uint8_t {
        REQUEST = 0,
        RESPONSE = 2,
        FAULT = 3,
        WORKING = 4,
        NOCALL = 5,
        REJECT = 6,
        ACK = 7,
        CL_CAN_CALL = 8,
        CANCEL_ACK = 9,
        BIND = 11,
        BIND_ACK = 12,
        BIND_NAK = 13,
        ALTER_CONTEXT = 14,
        ALTER_CONTEXT_RESP = 15
    };
    
    // UUID结构
    struct UUID {
        uint32_t data1;
        uint16_t data2;
        uint16_t data3;
        uint8_t data4[8];
    };
};
```

---

## 附录DP： POP3检测器详解 {#附录dp-pop3检测器详解}

### DP.1 POP3会话状态 {#dp-1-pop3会话状态}

```cpp
// pop/pop.h
class POPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // POP3状态机
    enum class State : uint8_t {
        AUTHORIZATION = 0,  // 授权状态
        TRANSACTION = 1,     // 事务状态
        UPDATE = 2           // 更新状态
    };
    
    // POP3命令
    enum class Command {
        USER,       // 用户名
        PASS,       // 密码
        QUIT,       // 退出
        STAT,       // 状态
        LIST,       // 列表
        RETR,       // 检索
        DELE,       // 删除
        NOOP,       // 无操作
        TOP,        // 顶部
        UIDL        // 唯一标识列表
    };
    
    // 邮件处理
    void process_command(const uint8_t*, uint16_t);
    void process_response(const uint8_t*, uint16_t);
    
    State state = State::AUTHORIZATION;
    uint32_t num_messages = 0;
    uint64_t total_size = 0;
};
```

---

## 附录DQ： IMAP检测器详解 {#附录dq-imap检测器详解}

### DQ.1 IMAP邮箱处理 {#dq-1-imap邮箱处理}

```cpp
// imap/imap.h
class IMAPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // IMAP状态机
    enum class State : uint8_t {
        NOT_AUTHENTICATED = 0,  // 未认证
        AUTHENTICATED = 1,       // 已认证
        SELECTED = 2,            // 已选择邮箱
        LOGOUT = 3               // 登出
    };
    
    // IMAP响应
    enum class ResponseType {
        TAGGED,      // 带标签响应
        UNTAGGED,    // 无标签响应
        CONTINUATION // 继续请求
    };
    
    // 邮件处理
    void process_command(const uint8_t*, uint16_t);
    void process_response(const uint8_t*, uint16_t);
    
    State state = State::NOT_AUTHENTICATED;
    char* selected_mailbox = nullptr;
    uint32_t num_messages = 0;
};
```

---

## 附录DR： RDP检测器 {#附录dr-rdp检测器}

### DR.1 RDP协议 {#dr-1-rdp协议}

```cpp
// rdp/rdp.h
class RDPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // RDP连接阶段
    enum class Phase {
        CONNECTION_INITIAL,      // 初始连接
        CONNECTION_SECURITY,     // 安全连接
        LAYER_SETUP,             // 层设置
        CHANNEL_CONNECT,         // 通道连接
        DATA_TRANSFER            // 数据传输
    };
    
    // RDP通知类型
    enum class Notification {
        demand_active = 33,
        respond_demand_active = 36,
        logon = 38,
        logon_error = 39,
        defer_update = 100
    };
};
```

---

## 附录DS： Kerberos检测器 {#附录ds-kerberos检测器}

### DS.1 Kerberos协议 {#ds-1-kerberos协议}

```cpp
// kerberos/kerberos.h
class KerberosInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // Kerberos消息类型
    enum class MessageType {
        AS_REQ = 10,    // 认证服务请求
        AS_REP = 11,    // 认证服务响应
        TGS_REQ = 12,   // 票据授予服务请求
        TGS_REP = 13,   // 票据授予服务响应
        AP_REQ = 14,    // 应用请求
        AP_REP = 15,    // 应用响应
        KRB_ERROR = 30  // KRB错误
    };
    
    // Kerberos标志
    enum class Flags : uint32_t {
        FORWARDABLE = 0x40000000,
        FORWARDED = 0x20000000,
        PROXIABLE = 0x10000000,
        PROXY = 0x08000000,
        ALLOW_POSTDATE = 0x04000000,
        POSTDATED = 0x02000000,
        INVALID = 0x01000000,
        RENEWABLE = 0x00800000,
        INITIAL = 0x00400000,
        PRE_AUTHENT = 0x00200000,
        HW_AUTHENT = 0x00100000
    };
};
```

---

## 附录DT： NetBIOS检测器 {#附录dt-netbios检测器}

### DT.1 NetBIOS会话服务 {#dt-1-netbios会话服务}

```cpp
// netbios/netbios.h
class NetBIOSInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // NetBIOS会话服务消息类型
    enum class SessionType : uint8_t {
        SESSION_MESSAGE = 0x00,
        SESSION_REQUEST = 0x81,
        POSITIVE_SESSION_RESPONSE = 0x82,
        NEGATIVE_SESSION_RESPONSE = 0x83,
        RETARGET_RESPONSE = 0x84,
        SESSION_KEEP_ALIVE = 0x85
    };
    
    // NetBIOS名字编码
    // NetBIOS names are 16 bytes, padded with spaces
    // First byte is name length
    struct NetBIOSName {
        uint8_t name_length;     // 名称长度(通常0x20)
        uint8_t name[32];        // 压缩的NetBIOS名称
        uint8_t scope_id[];      // 作用域ID
    };
};
```

---

## 附录DU： UUCP检测器 {#附录du-uucp检测器}

### DU.1 UUCP协议 {#du-1-uucp协议}

```cpp
// uucp/uucp.h
class UUCPInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // UUCP命令
    enum class Command : uint8_t {
        SNDMSG = 'h',   // 发送消息
        HLINE = 'y',    // 主机行
        HNAME = 'Y',    // 主机名
        SFILE = 'f',    // 发送文件
        RFILE = 'c',    // 接收文件
        STAT = 's',     // 状态
        HALT = 'x',     // 停止
        SHELL = 'S',    // Shell命令
        EXEC = 'E'      // 执行
    };
};
```

---

## 附录DV： Quake检测器 {#附录dv-quake检测器}

### DV.1 Quake游戏协议 {#dv-1-quake游戏协议}

```cpp
// quake/quake.h
class QuakeInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // Quake服务器查询
    enum class QueryType : uint8_t {
        INFO = 0x02,           // 服务器信息
        PLAYERS = 0x0D,        // 玩家列表
        RULES = 0x0E            // 规则
    };
    
    // Quake协议版本
    enum class Protocol : uint8_t {
        QUAKE1 = 15,
        QUAKE2 = 16,
        QUAKE3 = 17
    };
};
```

---

## 附录DW： Teamspeak检测器 {#附录dw-teamspeak检测器}

### DW.1 TeamSpeak协议 {#dw-1-teamspeak协议}

```cpp
// teamspeak/teamspeak.h
class TeamspeakInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // TeamSpeak命令类型
    enum class CommandType : uint8_t {
        LOGIN = 0x05,
        SELECT_SERVER = 0x07,
        CREATE_CHANNEL = 0x08,
        DELETE_CHANNEL = 0x09,
        CHAT_MESSAGE = 0x0A,
        WHISPER = 0x0B
    };
};
```

---

## 附录DX： DNS检测器详解 {#附录dx-dns检测器详解}

### DX.1 DNS深入分析 {#dx-1-dns深入分析}

```cpp
// dns/dns.h - 完整DNS处理

class DNSInspector : public Inspector {
public:
    void eval(Packet*) override;
    StreamSplitter* get_splitter(bool to_server) override;
    
    // DNS查询/响应处理
    void process_dns(Packet*, const uint8_t*, uint16_t);
    
    // DNS资源记录类型
    enum class RecordType : uint16_t {
        A = 1,              // IPv4地址
        NS = 2,             // 权威名称服务器
        MD = 3,             // 邮件目的地
        MF = 4,             // 邮件转发器
        CNAME = 5,          // 规范名称
        SOA = 6,            // 起始授权
        MB = 7,             // 邮件邮箱
        MG = 8,             // 邮件组
        MR = 9,             // 邮件重命名
        NULL_RR = 10,       // 空记录
        WKS = 11,           // 已知服务
        PTR = 12,           // 指针
        HINFO = 13,         // 主机信息
        MINFO = 14,         // 邮箱信息
        MX = 15,            // 邮件交换
        TXT = 16,           // 文本
        AAAA = 28,          // IPv6地址
        SRV = 33,           // 服务定位
        DNSKEY = 48,        // DNS密钥
        DS = 43,            // 委托签名
        RRSIG = 46,         // 资源记录签名
        NSEC = 47,          // 下一安全
        NSEC3 = 50,         // NSEC第3版
        NSEC3PARAM = 51      // NSEC3参数
    };
    
    // DNS操作码
    enum class OpCode : uint8_t {
        QUERY = 0,          // 标准查询
        IQUERY = 1,         // 反向查询
        STATUS = 2,         // 状态查询
        NOTIFY = 4,         // 通知
        UPDATE = 5          // 动态更新
    };
    
    // DNS响应码
    enum class ResponseCode : uint8_t {
        NOERROR = 0,        // 无错误
        FORMERR = 1,        // 格式错误
        SERVFAIL = 2,       // 服务器失败
        NXDOMAIN = 3,       // 域名不存在
        NOTIMP = 4,         // 未实现
        REFUSED = 5,        // 查询拒绝
        YXDOMAIN = 6,       // 域名存在
        YXRRSET = 7,        // 资源记录集存在
        NXRRSET = 8,        // 资源记录集不存在
        NOTAUTH = 9,        // 服务器不在授权区
        NOTZONE = 10        // 名称不在区中
    };
    
    // DNS头结构
    struct DNSHeader {
        uint16_t id;        // 事务ID
        uint16_t flags;     // 标志
        uint16_t qdcount;   // 问题数
        uint16_t ancount;   // 回答资源记录数
        uint16_t nscount;   // 权威资源记录数
        uint16_t arcount;   // 附加资源记录数
    };
    
    // DNS问题结构
    struct DNSQuestion {
        uint16_t qtype;    // 查询类型
        uint16_t qclass;   // 查询类
        // 名称紧随其后
    };
    
    // DNS资源记录结构
    struct DNSResourceRecord {
        uint16_t type;      // 类型
        uint16_t rclass;   // 类
        uint32_t ttl;      // 生存时间
        uint16_t rdlength; // 资源数据长度
        uint8_t* rdata;   // 资源数据
    };
    
private:
    void parse_query(const uint8_t*&, uint16_t&);
    void parse_response(const uint8_t*&, uint16_t&);
    void parse_name(const uint8_t*&, uint16_t&, char*, size_t);
    void check_dns_threshold(Packet*, uint16_t);
    
    // DNS配置
    DNSModule* module;
    uint16_t sessions;
    uint16_t max_sessions;
};
```

---

## 附录DY： 模块引用关系图 {#附录dy-模块引用关系图}

### DY.1 核心模块依赖 {#dy-1-核心模块依赖}

```
┌─────────────────────────────────────────────────────────────────┐
│                     Snort Main (main.cc)                         │
├─────────────────────────────────────────────────────────────────┤
│                         Pig                                      │
│    ┌──────────────────────────────────────────────────────────┐ │
│    │                    Analyzer                               │ │
│    │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │ │
│    │  │ Inspector  │  │ Inspector │  │ Inspector  │  ...     │ │
│    │  │  (IT_NET)  │  │  (IT_SVC)  │  │ (IT_STRM)  │          │ │
│    │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘          │ │
│    │        │               │               │                  │ │
│    │        └───────────────┼───────────────┘                  │ │
│    │                        ▼                                  │ │
│    │              ┌────────────────────┐                       │ │
│    │              │ InspectorManager   │                       │ │
│    │              └─────────┬──────────┘                       │ │
│    │                        │                                   │ │
│    │         ┌──────────────┼──────────────┐                    │ │
│    │         ▼              ▼              ▼                    │ │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │ │
│    │  │  Codec   │  │ Module   │  │  Plugin  │                   │ │
│    │  │ Manager  │  │ Manager  │  │ Manager  │                   │ │
│    │  └──────────┘  └──────────┘  └──────────┘                   │ │
│    │         │              │              │                    │ │
│    └─────────┼──────────────┼──────────────┼────────────────────┘ │
│              │              │              │                      │
│              ▼              ▼              ▼                      │
│    ┌────────────────────────────────────────────────────────────┐│
│    │                    Detection Engine                         ││
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    ││
│    │  │  Action  │  │   Log   │  │ Filter   │  │ Search   │    ││
│    │  │ Manager  │  │ Manager │  │ Manager  │  │ Engine   │    ││
│    │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    ││
│    └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 附录DZ： 关键类层次结构 {#附录dz-关键类层次结构}

### DZ.1 Inspector类层次 {#dz-1-inspector类层次}

```
Inspector (framework/inspector.h)
├── NetworkInspector (网络层检查器)
│   ├── Binder (服务绑定)
│   ├── Wizard (自动服务检测)
│   ├── ARPInspector
│   ├── GREInspector
│   ├── ICMPInspector
│   ├── IPLayer (IP层)
│   └── MPLSInspector
│
├── ServiceInspector (服务检查器)
│   ├── HTTPInspector
│   ├── DNSInspector
│   ├── SMTPInspector
│   ├── FTPInspector
│   ├── SSHInspector
│   ├── SSLInspector
│   ├── SMBInspector
│   ├── DCERPCInspector
│   ├── SIPInspector
│   ├── RDPInspector
│   ├── IRCInspector
│   ├── KerberosInspector
│   ├── RadiusInspector
│   └── DHCPInspector
│
├── StreamInspector (流检查器)
│   ├── TcpStreamInspector
│   └── UdpStreamInspector
│
├── PacketInspector (数据包检查器)
│   ├── FragmentInspector (分片重组)
│   └── Reassembler (重组器)
│
└── ControlInspector (控制检查器)
```

### DZ.2 Session类层次 {#dz-2-session类层次}

```
Session (flow/session.h)
├── TcpSession (stream/tcp/tcp_session.h)
│   ├── TcpStreamTracker
│   │   ├── TcpReassembler
│   │   ├── TcpReassemblySegments
│   │   └── TcpAlerts
│   └── TcpStateMachine
│
├── UdpSession (flow/udp/udp_session.h)
│
└── GtpSession (gtp/gtp_session.h)
```

---

## 附录EA： 规则选项链 {#附录ea-规则选项链}

### EA.1 选项链表结构 {#ea-1-选项链表结构}

```cpp
// detection/treenorm.h

// 选项链表
struct OptList {
    OptList* next;          // 下一个选项
    IpsOption* ips_option;  // IPS选项
    PatternMatchData* pmd;  // 模式匹配数据
};

// IPS选项
class IpsOption {
public:
    virtual ~IpsOption() = default;
    
    // 选项类型
    virtual OptionType get_type() const = 0;
    
    // 评估选项
    virtual int eval(Cursor&, Packet*, IpsContext*) = 0;
    
    // 获取选项数据
    virtual const void* get_data() const = 0;
    
    // 打印选项
    virtual void print() const = 0;
    
    // 字节码
    virtual unsigned generate(ByteCode*) const;
};

// 选项类型枚举
enum class OptionType {
    CONTENT,       // 内容匹配
    PCRE,          // 正则表达式
    HEADER,        // 头部检查
    PAYLOAD,      // 载荷检查
    FLOW,         // 流检查
    STICKY_BUFFER, // 粘性缓冲区
    FILE_DATA,    // 文件数据
    REGEX,        // 正则
    ...
};
```

---

## 附录EB： 编码和解码流程 {#附录eb-编码和解码流程}

### EB.1 数据包解码流程 {#eb-1-数据包解码流程}

```cpp
// codecs/ip/codec_ip.h

class IPV4Codec : public Codec {
public:
    const char* get_name() const override
    { return "IPv4"; }
    
    bool decode(Packet* p, const uint8_t* raw_pkt, uint16_t len, CodecData* cd) override {
        // 检查最小长度
        if (len < IP_HEADER_MIN_LEN)
            return false;
        
        // 解析IP头
        const IPHdr* ip = reinterpret_cast<const IPHdr*>(raw_pkt);
        
        // 验证版本
        if (ip->get_version() != 4)
            return false;
        
        // 验证头部长度
        uint8_t ihl = ip->get_hlen();
        if (ihl < 5 || len < ihl * 4)
            return false;
        
        // 验证总长度
        uint16_t total_len = ip->get_length();
        if (total_len > len)
            return false;
        
        // 设置数据包信息
        p->ip_api.set_ip4(ip);
        p->ip4h = ip;
        
        // 继续解析上层协议
        const uint8_t* next = raw_pkt + ihl * 4;
        uint16_t left = len - ihl * 4;
        
        // 调用下一层解码器
        cd->proto_bits |= PROTO_BIT__IP;
        return decode_next(next, left, cd, p, ip->get_protocol());
    }
    
    uint16_t get_type() const override { return PktType::IP; }
    uint16_t get_hdr_len() const override { return IP_HEADER_MIN_LEN; }
};
```

---

## 附录EC： 模式匹配流程 {#附录ec-模式匹配流程}

### EC.1 快速模式匹配 {#ec-1-快速模式匹配}

```cpp
// detection/fp_detect.h

class FpDetect {
public:
    // 构造函数
    FpDetect(const SnortConfig*);
    ~FpDetect();
    
    // 执行快速模式匹配
    int detect(Packet*, Mpse*, DetectionContext*);
    
    // 获取匹配数量
    unsigned get_match_count() const
    { return match_count; }
    
private:
    // 清理匹配的规则
    void clean_match_list();
    
    // 评估匹配的规则
    int eval_rules(Packet*, DetectionContext*);
    
    // 处理content匹配
    int process_match(OptTreeNode* otn, Packet*, DetectionContext*);
    
    // 规则队列
    std::vector<OptTreeNode*> match_queue;
    unsigned match_count;
    const SnortConfig* config;
};
```

---

## 附录ED： 内存布局 {#附录ed-内存布局}

### ED.1 Packet内存布局 {#ed-1-packet内存布局}

```
┌─────────────────────────────────────────────────────────────────┐
│                        Packet Structure                          │
├─────────────────────────────────────────────────────────────────┤
│  Packet (protocols/packet.h)                                     │
│  ├── DataBuffer (基类)                                          │
│  │   ├── uint8_t* data                                         │
│  │   └── unsigned len                                           │
│  ├── PacketFlags pkt_flags                                       │
│  ├── PktType type                                               │
│  ├── const uint8_t* data                                         │
│  ├── uint16_t dsize                                              │
│  ├── EtherHdr* ether                                             │
│  ├── VLANHdr* vlan                                               │
│  ├── MPLSHdr* mpls                                               │
│  ├── IPHdr* ip_api                                               │
│  ├── TCPHdr* tcph                                               │
│  ├── UDPHdr* udph                                               │
│  ├── ICMPHdr* icmph                                             │
│  ├── Flow* flow                                                 │
│  ├── Packet* outer_pkt                                           │
│  ├── DAQ_PktHdr_t* pkth                                         │
│  ├── struct timeval timestamp                                    │
│  ├── uint16_t app_id                                             │
│  └── void* app_data                                              │
├─────────────────────────────────────────────────────────────────┤
│  协议头解析后，各层指针指向data缓冲区中的相应位置                   │
│  ┌─────────┬─────────┬─────────┬─────────┬────────────────────┐│
│  │ Ethernet│   IP    │   TCP   │  Payload│                    ││
│  │  Header │  Header │  Header │        │                    ││
│  └─────────┴─────────┴─────────┴─────────┴────────────────────┘│
│  ▲                                                        ▲     │
│  │                                                        │     │
│  ether                                                 p->data    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 附录EE： 线程局部存储 {#附录ee-线程局部存储}

### EE.1 TLS实现 {#ee-1-tls实现}

```cpp
// utils/thread.h

// 线程局部存储宏
#ifdef HAVE___THREAD
    #define THREAD_LOCAL __thread
#elif defined(HAVE_THREAD_LOCAL)
    #define THREAD_LOCAL thread_local
#else
    #error "No thread local storage support"
#endif

// 使用示例
// THREAD_LOCAL ProfileStats wizPerfStats;
// THREAD_LOCAL WizStats tstats;

// 原子操作模板
template<typename T>
class Atomic {
public:
    T load() const volatile {
        return __atomic_load_n(&value, __ATOMIC_ACQUIRE);
    }
    
    void store(T val) volatile {
        __atomic_store_n(&value, val, __ATOMIC_RELEASE);
    }
    
    T fetch_add(T val) volatile {
        return __atomic_fetch_add(&value, val, __ATOMIC_ACQ_REL);
    }
    
    bool compare_exchange(T& expected, T desired) volatile {
        return __atomic_compare_exchange_n(&value, &expected, desired,
            false, __ATOMIC_ACQ_REL, __ATOMIC_ACQUIRE);
    }
};
```

---
