---
title: "Snort 3 · 附录 EX–FH"
description: "附录EX： HiSF检测器 — 附录FH： MQTT检测器"
---

# Snort 3 · 附录 EX–FH

[返回总目录](../snort3_architecture_analysis)

## 附录EX： HiSF检测器 {#附录ex-hisf检测器}

### EX.1 HiSF协议分析 {#ex-1-hisf协议分析}

```cpp
// hisf/hisf.h
class HisfInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // HiSF消息类型
    enum class MessageType : uint8_t {
        HELLO = 0x01,
        HEARTBEAT = 0x02,
        DATA = 0x03,
        GOODBYE = 0x04
    };
    
    // 连接状态
    enum class State : uint8_t {
        INIT,
        CONNECTED,
        ACTIVE,
        CLOSING
    };
    
private:
    State state = State::INIT;
    uint32_t session_id = 0;
    uint64_t last_heartbeat = 0;
};
```

---

## 附录EY： IEC 61850检测器 {#附录ey-iec-61850检测器}

### EY.1 电力自动化协议 {#ey-1-电力自动化协议}

```cpp
// iec61850/iec61850.h
class IEC61850Inspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // IEC 61850 APDU类型
    enum class APDUType : uint8_t {
        INITIATE = 0x01,
        GETDATA = 0x02,
        SETDATA = 0x03,
        DATACHANGE = 0x04,
        READ = 0x05,
        WRITE = 0x06,
        DIRECT = 0x07
    };
    
    // 服务类型
    enum class ServiceType : uint16_t {
        GET_DATA = 0x0001,
        SET_DATA = 0x0002,
        CREATE_DATASET = 0x0003,
        DELETE_DATASET = 0x0004,
        GET_DATA_SET = 0x0005
    };
};
```

---

## 附录EZ： Modbus检测器 {#附录ez-modbus检测器}

### EZ.1 Modbus TCP协议 {#ez-1-modbus-tcp协议}

```cpp
// modbus/modbus.h
class ModbusInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // Modbus功能码
    enum class FunctionCode : uint8_t {
        READ_COILS = 0x01,
        READ_DISCRETE_INPUTS = 0x02,
        READ_HOLDING_REGS = 0x03,
        READ_INPUT_REGS = 0x04,
        WRITE_SINGLE_COIL = 0x05,
        WRITE_SINGLE_REG = 0x06,
        WRITE_MULTIPLE_COILS = 0x0F,
        WRITE_MULTIPLE_REGS = 0x10,
        READ_FILE_RECORD = 0x14,
        WRITE_FILE_RECORD = 0x15,
        READ_EXCEPTION_STATUS = 0x07,
        DIAGNOSTIC = 0x08,
        GET_COM_EVENTS = 0x0B,
        REPORT_SLAVE_ID = 0x11
    };
    
    // Modbus异常码
    enum class ExceptionCode : uint8_t {
        ILLEGAL_FUNCTION = 0x01,
        ILLEGAL_DATA_ADDRESS = 0x02,
        ILLEGAL_DATA_VALUE = 0x03,
        SLAVE_DEVICE_FAILURE = 0x04,
        ACKNOWLEDGE = 0x05,
        SLAVE_BUSY = 0x06,
        MEMORY_PARITY_ERROR = 0x08,
        GATEWAY_PATH = 0x0A,
        GATEWAY_TARGET = 0x0B
    };
    
    // Modbus头结构
    struct MBAPHeader {
        uint16_t transaction_id;  // 事务ID
        uint16_t protocol_id;     // 协议ID (0 = Modbus)
        uint16_t length;         // 长度
        uint8_t unit_id;        // 单元ID
    };
};
```

---

## 附录FA： DNP3检测器详解 {#附录fa-dnp3检测器详解}

### FA.1 DNP3协议深度分析 {#fa-1-dnp3协议深度分析}

```cpp
// dnp3/dnp3.h

class DNP3Inspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // DNP3链路层功能码
    enum class LinkFunction : uint8_t {
        RESET_LINK = 0x09,
        TEST_LINK = 0x0B,
        CONFIRMED_USER_DATA = 0x0C,
        UNCONFIRMED_USER_DATA = 0x04,
        REQUEST_LINK_STATUS = 0x09
    };
    
    // DNP3传输层功能码
    enum class TransportFunction : uint8_t {
        FIRST = 0x04,
        LAST = 0x03,
        NEXT = 0x07
    };
    
    // DNP3应用层功能码
    enum class ApplicationFunction : uint16_t {
        CONFIRM = 0x0000,
        READ = 0x0001,
        WRITE = 0x0002,
        SELECT = 0x0003,
        OPERATE = 0x0004,
        DIRECT_OPERATE = 0x0005,
        DIRECT_OPERATE_NR = 0x0006,
        IMMEDIATE_FREEZE = 0x0007,
        IMMEDIATE_FREEZE_NR = 0x0008,
        FREEZE_CLEAR = 0x0009,
        FREEZE_CLEAR_NR = 0x000A,
        FREEZE_AT_TIME = 0x000B,
        FREEZE_AT_TIME_NR = 0x000C,
        CHANGE_INDEX = 0x000D,
        VAR_DIR_OK = 0x000E,
        ASSIGN_CLASS = 0x000F,
        DELAY_MEASURE = 0x0011,
        RECORD_CURRENT_TIME = 0x0012,
        TIME_SYNC = 0x0013,
        ENABLE_UNSOLICITED = 0x0014,
        DISABLE_UNSOLICITED = 0x0015,
        ASSIGN_MASTER = 0x0017,
        UNDEFINED = 0xFFFF
    };
    
    // DNP3对象组
    enum class ObjectGroup : uint16_t {
        GROUP_1 = 0x01,     // 二进制输入
        GROUP_2 = 0x02,     // 二进制输入变化
        GROUP_3 = 0x03,     // 二进制输出
        GROUP_4 = 0x04,     // 二进制输出变化
        GROUP_10 = 0x0A,    // 二进制输出状态
        GROUP_11 = 0x0B,    // 二进制输出命令
        GROUP_30 = 0x1E,    // 模拟输入
        GROUP_31 = 0x1F,    // 模拟输入变化
        GROUP_40 = 0x28,    // 模拟输出
        GROUP_41 = 0x29     // 模拟输出状态
    };
    
    // DNP3内部指示标志
    struct InternalIndicators {
        uint16_t all_stations : 1;       // 所有站
        uint16_t class1_events : 1;      // 1类事件
        uint16_t class2_events : 1;     // 2类事件
        uint16_t class3_events : 1;      // 3类事件
        uint16_t time_sync : 1;         // 时间同步
        uint16_t local_control : 1;     // 本地控制
        uint16_t device_trouble : 1;     // 设备故障
        uint16_t device_restart : 1;    // 设备重启
        uint16_t no_func_code : 1;      // 无功能码
        uint16_t unknown_object : 1;    // 未知对象
        uint16_t no_range : 1;          // 无范围
        uint16_t transaction_overflow : 1; // 事务溢出
        uint16_t buffer_overflow : 1;   // 缓冲区溢出
        uint16_t unknown_func_code : 1;  // 未知功能码
        uint16_t unknown_transport : 1; // 未知传输
    };
};
```

---

## 附录FB： GTP检测器详解 {#附录fb-gtp检测器详解}

### FB.1 GTP协议深度分析 {#fb-1-gtp协议深度分析}

```cpp
// gtp/gtp.h

class GTPInspector : public Inspector {
public:
    void eval(Packet*) override;
    StreamSplitter* get_splitter(bool) override;
    
    // GTP消息类型
    enum class MessageType : uint8_t {
        // GTPv1消息
        ECHO_REQUEST = 1,
        ECHO_RESPONSE = 2,
        VERSION_NOT_SUPPORTED = 3,
        CREATE_PDP_CONTEXT = 16,
        UPDATE_PDP_CONTEXT = 17,
        DELETE_PDP_CONTEXT = 18,
        CREATE_PDP_CONTEXT_ACK = 19,
        UPDATE_PDP_CONTEXT_ACK = 20,
        DELETE_PDP_CONTEXT_ACK = 21,
        ERROR_INDICATION = 26,
        TEARDOWN_INDICATION = 27,
        FORWARD_PDP_CONTEXT_ACK = 30,
        // GTPv2消息
        CREATE_SESSION = 32,
        MODIFY_BEARER = 33,
        DELETE_SESSION = 36,
        CHANGE_NOTIFICATION = 37,
        MODIFY_BEARER_ACK = 34,
        DELETE_SESSION_ACK = 38,
        CREATE_BEARER = 32,
        BEARER_RESOURCE = 33
    };
    
    // GTPv1头结构
    struct GTPv1Header {
        uint8_t flags;        // 标志 (3位版本 + 1位PT + 1位reserved + 1位SNN + 1位E + 1位S)
        uint8_t type;         // 消息类型
        uint16_t length;      // 长度
        uint32_t teid;        // 隧道端点标识符
    };
    
    // GTPv2头结构
    struct GTPv2Header {
        uint8_t flags;        // 标志
        uint8_t type;         // 消息类型
        uint16_t length;      // 长度
    };
    
    // IE类型
    enum class InformationElement : uint16_t {
        IE_IMSI = 1,
        IE_CAUSE = 2,
        IE_RECOVERY = 3,
        IE_STARTT = 0x0D,
        IE_APN = 0x14,
        IE_RAI = 0x19,
        IE_TLAID = 0x1A,
        IE_PTMSI = 0x1B,
        IE_PTMSI_SIG = 0x1C,
        IE_MSISDN = 0x1D,
        IE_rau_old = 0x1E,
        IE_TEID = 0x10,
        IE_TEID_CONTROL = 0x11,
        IE_TEID_DATA1 = 0x12,
        IE_TEID_DATA2 = 0x13,
        IE_NSAPI = 0x14,
        IE_BEARER_ID = 0x15,
        IE_END_USER_ADDRESS = 0x80,
        IE_PROTOCOL_OPTIONS = 0x81,
        IE_PCO = 0x82
    };
    
private:
    void process_gtpv1(Packet*, const uint8_t*, uint16_t);
    void process_gtpv2(Packet*, const uint8_t*, uint16_t);
    void process_ie(const uint8_t*&, uint16_t&);
    
    GTPState* state;
};
```

---

## 附录FC： SIP检测器详解 {#附录fc-sip检测器详解}

### FC.1 SIP协议深度分析 {#fc-1-sip协议深度分析}

```cpp
// sip/sip.h

class SIPInspector : public Inspector {
public:
    void eval(Packet*) override;
    StreamSplitter* get_splitter(bool to_server) override {
        return new SIPSplitter(to_server);
    }
    
    // SIP方法
    enum class Method : uint16_t {
        INVITE = 0x495C4956,    // "INVITE"
        ACK = 0x4B4341,        // "ACK"
        BYE = 0x594542,         // "BYE"
        CANCEL = 0x4C414E43,   // "CANCEL"
        OPTIONS = 0x534F4C55,   // "OPTIONS"
        REGISTER = 0x47455245,  // "REGISTER"
        PRACK = 0x41524350,    // "PRACK"
        SUBSCRIBE = 0x42555353, // "SUBSCRIBE"
        NOTIFY = 0x5946544F,   // "NOTIFY"
        INFO = 0x494E464F,     // "INFO"
        REFER = 0x46524552,    // "REFER"
        MESSAGE = 0x47414D45,  // "MESSAGE"
        UPDATE = 0x44505544,   // "UPDATE"
        PUBLISH = 0x424C5500,  // "PUBLISH"
        DO = 0x00000044,       // "DO"
        HINFO = 0x494E4848     // "HINFO"
    };
    
    // SIP响应码
    enum class ResponseCode {
        TRYING = 100,
        RINGING = 180,
        CALL_IS_BEING_FORWARDED = 181,
        QUEUED = 182,
        SESSION_PROGRESS = 183,
        OK = 200,
        ACCEPTED = 202,
        NO_NOTIFICATION = 204,
        MULTIPLE_CHOICES = 300,
        MOVED_PERMANENTLY = 301,
        MOVED_TEMPORARILY = 302,
        USE_PROXY = 305,
        ALTERNATIVE_SERVICE = 380,
        BAD_REQUEST = 400,
        UNAUTHORIZED = 401,
        PAYMENT_REQUIRED = 402,
        FORBIDDEN = 403,
        NOT_FOUND = 404,
        METHOD_NOT_ALLOWED = 405,
        NOT_ACCEPTABLE = 406,
        PROXY_AUTH_REQUIRED = 407,
        REQUEST_TIMEOUT = 408,
        GONE = 410,
        REQUEST_ENTITY_TOO_LARGE = 413,
        REQUEST_URI_TOO_LARGE = 414,
        UNSUPPORTED_URI = 415,
        BAD_EXTENSION = 420,
        EXTENSION_REQUIRED = 421,
        INTERVAL_TOO_BRIEF = 423,
        TEMPORARILY_UNAVAILABLE = 480,
        CALL_OR_TRANSACTION = 481,
        BUSY_HERE = 486,
        REQUEST_TERMINATED = 487,
        NOT_ACCEPTABLE_HERE = 488,
        BAD_EVENT = 489,
        REQUEST_UPDATED = 490,
        REQUEST_PENDING = 491,
        UNDISCLOSED_REQUIRED = 493,
        INTERVAL_TOO_BRIEF = 494,
        SERVER_INTERNAL_ERROR = 500,
        NOT_IMPLEMENTED = 501,
        BAD_GATEWAY = 502,
        SERVICE_UNAVAILABLE = 503,
        SERVER_TIMEOUT = 504,
        VERSION_NOT_SUPPORTED = 505,
        MESSAGE_TOO_BARGE = 513,
        PRECONDITION_FAILURE = 580
    };
    
    // SIP头字段
    enum class HeaderField : uint8_t {
        FROM,
        TO,
        VIA,
        CONTACT,
        MAX_FORWARDS,
        USER_AGENT,
        SERVER,
        CONTENT_LENGTH,
        CONTENT_TYPE,
        CALL_ID,
        CSEQ,
        ALLOW,
        SUPPORTED,
        UNSUPPORTED,
        EXPIRES,
        DATE,
        WARNING,
        AUTHENTICATION
    };
    
    // SIP会话状态
    struct SIPState {
        Method method;
        uint32_t cseq;
        char* call_id;
        char* from_tag;
        char* to_tag;
        char* branch;
        uint8_t transaction_type; // INVITE或NON-INVITE
        uint16_t port;
    };
    
private:
    void process_invite(Packet*, const uint8_t*, uint16_t);
    void process_response(Packet*, const uint8_t*, uint16_t);
    void process_sdp(Packet*, const uint8_t*, uint16_t);
    bool validate_sip_uri(const char*);
    
    SIPModule* module;
    std::unordered_map<std::string, SIPState*> sessions;
};
```

---

## 附录FD： RPC检测器 {#附录fd-rpc检测器}

### FD.1 RPC协议处理 {#fd-1-rpc协议处理}

```cpp
// rpc/rpc.h

class RPCInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // RPC消息类型
    enum class MsgType : uint32_t {
        CALL = 0,
        REPLY = 1
    };
    
    // RPC认证类型
    enum class AuthType : uint32_t {
        NONE = 0,
        UNIX = 1,
        SHORT = 2,
        DES = 3,
        GSS = 6
    };
    
    // RPC程序号
    enum class Program : uint32_t {
        PORTMAP = 100000,
        MOUNT = 100005,
        NFS = 100003,
        NLM = 100021,
        STATD = 100024,
        NIS = 100029
    };
    
    // RPC程序版本
    enum class Version : uint32_t {
        PORTMAP_V2 = 2,
        PORTMAP_V3 = 3,
        NFS_V2 = 2,
        NFS_V3 = 3,
        NFS_V4 = 4,
        MOUNT_V1 = 1,
        MOUNT_V3 = 3
    };
    
    // RPC调用结构
    struct RPCCall {
        uint32_t xid;           // 事务ID
        MsgType msg_type;        // 消息类型
        uint32_t rpc_version;   // RPC版本
        uint32_t program;       // 程序号
        uint32_t version;       // 版本号
        uint32_t procedure;     // 过程号
        AuthType cred_flavor;   // 认证类型
        uint32_t cred_length;   // 认证长度
        AuthType verflavor;     // 验证类型
    };
    
    // NFS过程号
    enum class NFSProcedure : uint32_t {
        NULL = 0,
        GETATTR = 1,
        SETATTR = 2,
        LOOKUP = 3,
        ACCESS = 4,
        READLINK = 5,
        READ = 6,
        WRITE = 8,
        CREATE = 9,
        MKDIR = 10,
        SYMLINK = 11,
        REMOVE = 12,
        RMDIR = 13,
        RENAME = 14,
        LINK = 15,
        READDIR = 16,
        READDIRPLUS = 17,
        FSSTAT = 18,
        FSINFO = 19,
        PATHCONF = 20,
        COMMIT = 21
    };
};
```

---

## 附录FE： SMB检测器详解 {#附录fe-smb检测器详解}

### FE.1 SMB协议深度分析 {#fe-1-smb协议深度分析}

```cpp
// smb/smb.h

class SMBInspector : public Inspector {
public:
    void eval(Packet*) override;
    StreamSplitter* get_splitter(bool) override;
    
    // SMB命令 (SMB1)
    enum class SMB1Command : uint8_t {
        NEGOTIATE = 0x72,
        SESSION_SETUP_ANDX = 0x73,
        TREE_CONNECT_ANDX = 0x75,
        TREE_DISCONNECT = 0x71,
        LOGOFF_ANDX = 0x74,
        NT_CREATE_ANDX = 0xA2,
        NT_TRANSACT = 0xA5,
        TRANS = 0x25,
        TRANS2 = 0x32,
        OPEN_ANDX = 0x2D,
        READ_ANDX = 0x2E,
        WRITE_ANDX = 0x2F,
        CLOSE = 0x04,
        TREE_CONNECT = 0x70
    };
    
    // SMB2命令
    enum class SMB2Command : uint16_t {
        NEGOTIATE = 0x0000,
        SESSION_SETUP = 0x0001,
        LOGOFF = 0x0002,
        TREE_CONNECT = 0x0003,
        TREE_DISCONNECT = 0x0004,
        CREATE = 0x0005,
        CLOSE = 0x0006,
        FLUSH = 0x0007,
        READ = 0x0008,
        WRITE = 0x0009,
        RENAME = 0x000A,
        DELETE = 0x000D,
        CREATE_DIRECTORY = 0x000E,
        EMPTY_DIRECTORY = 0x0F,
        FIND_FIRST = 0x0011
    };
    
    // SMB访问模式
    enum class AccessMode : uint16_t {
        OPEN_EXISTING = 0,
        CREATE_NEW = 1,
        OPEN_ALWAYS = 2,
        TRUNCATE_EXISTING = 3
    };
    
    // SMB分享类型
    enum class ShareType : uint8_t {
        DISK = 0x01,
        PIPE = 0x02,
        PRINTER = 0x03
    };
    
    // SMB管道状态
    enum class PipeState : uint8_t {
        DISCONNECTED = 0x01,
        LISTENING = 0x02,
        CONNECTED = 0x03,
        REMOTE = 0x04
    };
    
    // SMB2标志
    struct SMB2Flags {
        uint32_t server_to_redir : 1;
        uint32_t async_command : 1;
        uint32_t persistent_reserve : 1;
        uint32_t scatter_gather : 1;
    };
    
    // SMB会话状态
    struct SMBState {
        uint64_t session_id;
        uint16_t tree_id;
        uint32_t max_read_size;
        uint32_t max_write_size;
        uint16_t dialect;
        uint8_t share_type;
        bool signed_session;
    };
    
private:
    void process_smb1(Packet*, const uint8_t*, uint16_t);
    void process_smb2(Packet*, const uint8_t*, uint16_t);
    void process_negotiate(Packet*, const uint8_t*, uint16_t);
    void process_session_setup(Packet*, const uint8_t*, uint16_t);
    void process_tree_connect(Packet*, const uint8_t*, uint16_t);
    void process_nt_transact(Packet*, const uint8_t*, uint16_t);
    void process_trans2(Packet*, const uint8_t*, uint16_t);
    
    SMBModule* module;
    std::unordered_map<uint64_t, SMBState*> sessions;
};
```

---

## 附录FF： HTTP/2检测器 {#附录ff-http-2检测器}

### FF.1 HTTP/2协议处理 {#ff-1-http-2协议处理}

```cpp
// http2/http2.h

class HTTP2Inspector : public Inspector {
public:
    void eval(Packet*) override;
    StreamSplitter* get_splitter(bool) override;
    
    // HTTP/2设置ID
    enum class SettingID : uint16_t {
        HEADER_TABLE_SIZE = 0x01,
        ENABLE_PUSH = 0x02,
        MAX_CONCURRENT_STREAMS = 0x03,
        INITIAL_WINDOW_SIZE = 0x04,
        MAX_FRAME_SIZE = 0x05,
        MAX_HEADER_LIST_SIZE = 0x06
    };
    
    // HTTP/2帧类型
    enum class FrameType : uint8_t {
        DATA = 0x00,
        HEADERS = 0x01,
        PRIORITY = 0x02,
        RST_STREAM = 0x03,
        SETTINGS = 0x04,
        PING = 0x06,
        GOAWAY = 0x07,
        WINDOW_UPDATE = 0x08,
        CONTINUATION = 0x09
    };
    
    // HTTP/2错误码
    enum class ErrorCode : uint32_t {
        NO_ERROR = 0x00,
        PROTOCOL_ERROR = 0x01,
        INTERNAL_ERROR = 0x02,
        FLOW_CONTROL_ERROR = 0x03,
        SETTINGS_TIMEOUT = 0x04,
        STREAM_CLOSED = 0x05,
        FRAME_SIZE_ERROR = 0x06,
        REFUSED_STREAM = 0x07,
        CANCEL = 0x08,
        COMPRESSION_ERROR = 0x09,
        CONNECT_ERROR = 0x0A,
        ENHANCE_YOUR_CALM = 0x0B,
        INADEQUATE_SECURITY = 0x0C,
        HTTP_1_1_REQUIRED = 0x0D
    };
    
    // HTTP/2流状态
    enum class StreamState : uint8_t {
        IDLE,
        OPEN,
        RESERVED_LOCAL,
        RESERVED_REMOTE,
        HALF_CLOSED_LOCAL,
        HALF_CLOSED_REMOTE,
        CLOSED
    };
    
    // HTTP/2帧结构
    struct HTTP2Frame {
        uint32_t length : 24;    // 长度
        uint8_t type;            // 类型
        uint8_t flags;           // 标志
        uint32_t stream_id : 31; // 流ID
    };
    
    // HTTP/2流
    struct HTTP2Stream {
        uint32_t stream_id;
        StreamState state;
        std::string method;
        std::string uri;
        std::map<std::string, std::string> headers;
        uint32_t window_size;
    };
    
    // HPACK头部压缩
    class HPACK {
    public:
        // 动态表操作
        void add_entry(const uint8_t*, size_t);
        
        // 解码头部
        bool decode_header(const uint8_t*&, size_t&, std::string&, std::string&);
        
        // 索引查找
        int lookup_static_table(uint8_t);
        int lookup_dynamic_table(uint8_t);
        
    private:
        std::vector<std::pair<std::string, std::string>> dynamic_table;
        size_t max_dynamic_table_size;
    };
    
private:
    void process_frame(Packet*, const HTTP2Frame*, const uint8_t*, uint16_t);
    void process_headers(Packet*, uint32_t, const uint8_t*, uint16_t);
    void process_data(Packet*, uint32_t, const uint8_t*, uint16_t);
    void process_settings(Packet*, const uint8_t*, uint16_t);
    void process_rst_stream(Packet*, const uint8_t*, uint16_t);
    void process_ping(Packet*, const uint8_t*, uint16_t);
    void process_goaway(Packet*, const uint8_t*, uint16_t);
    
    HTTP2Module* module;
    HPACK hpack_decoder;
    std::unordered_map<uint32_t, HTTP2Stream*> streams;
    uint32_t advertised_max_frame_size = 16384;
};
```

---

## 附录FG： WebSocket检测器 {#附录fg-websocket检测器}

### FG.1 WebSocket协议 {#fg-1-websocket协议}

```cpp
// websocket/websocket.h

class WebSocketInspector : public Inspector {
public:
    void eval(Packet*) override;
    
    // WebSocket操作码
    enum class OpCode : uint8_t {
        CONTINUATION = 0x00,
        TEXT = 0x01,
        BINARY = 0x02,
        CLOSE = 0x08,
        PING = 0x09,
        PONG = 0x0A
    };
    
    // WebSocket状态
    enum class State : uint8_t {
        CONNECTING,
        OPEN,
        CLOSING,
        CLOSED
    };
    
    // WebSocket帧结构
    struct Frame {
        uint8_t opcode : 4;
        uint8_t rsv3 : 1;
        uint8_t rsv2 : 1;
        uint8_t rsv1 : 1;
        uint8_t fin : 1;
        uint8_t mask : 1;
        uint8_t payload_len : 7;
        uint64_t extended_payload_len : 63;
        uint8_t masking_key[4];
    };
    
    // WebSocket握手
    struct Handshake {
        std::string key;
        std::string version;
        std::string protocol;
        std::string extensions;
    };
    
private:
    State state = State::CONNECTING;
    Handshake handshake;
    std::deque<std::vector<uint8_t>> message_queue;
};
```

---

## 附录FH： MQTT检测器 {#附录fh-mqtt检测器}

### FH.1 MQTT协议分析 {#fh-1-mqtt协议分析}

```cpp
// mqtt/mqtt.h

class MQTTInspector : public Inspector {
public:
    void eval(Packet*) override;
    StreamSplitter* get_splitter(bool) override;
    
    // MQTT消息类型
    enum class MessageType : uint8_t {
        CONNECT = 1,
        CONNACK = 2,
        PUBLISH = 3,
        PUBACK = 4,
        PUBREC = 5,
        PUBREL = 6,
        PUBCOMP = 7,
        SUBSCRIBE = 8,
        SUBACK = 9,
        UNSUBSCRIBE = 10,
        UNSUBACK = 11,
        PINGREQ = 12,
        PINGRESP = 13,
        DISCONNECT = 14,
        AUTH = 15
    };
    
    // MQTT协议版本
    enum class ProtocolLevel : uint8_t {
        V3_1 = 4,
        V3_1_1 = 5,
        V5 = 5
    };
    
    // MQTT连接标志
    struct ConnectFlags {
        uint8_t clean_session : 1;
        uint8_t will_flag : 1;
        uint8_t will_qos : 2;
        uint8_t will_retain : 1;
        uint8_t password : 1;
        uint8_t username : 1;
    };
    
    // MQTT QoS级别
    enum class QoS : uint8_t {
        AT_MOST_ONCE = 0,   // 最多一次
        AT_LEAST_ONCE = 1,  // 至少一次
        EXACTLY_ONCE = 2    // 恰好一次
    };
    
    // MQTT状态
    struct MQTTState {
        ProtocolLevel protocol_level;
        std::string client_id;
        std::string username;
        std::string will_topic;
        std::string will_message;
        uint16_t keep_alive;
        QoS will_qos;
        bool clean_session;
        bool connected;
    };
    
private:
    void process_connect(Packet*, const uint8_t*, uint16_t);
    void process_connack(Packet*, const uint8_t*, uint16_t);
    void process_publish(Packet*, const uint8_t*, uint16_t);
    void process_subscribe(Packet*, const uint8_t*, uint16_t);
    void process_unsubscribe(Packet*, const uint8_t*, uint16_t);
    bool validate_topic(const char*, size_t);
    
    MQTTModule* module;
    std::unordered_map<std::string, MQTTState*> sessions;
};
```

---
