---
title: "Snort3 应用层检查器 (Service Inspectors)"
description: "应用层检查器负责分析网络流量的应用层协议内容,是Snort3检测引擎的核心组件。"
---
# Snort3 应用层检查器 (Service Inspectors)

应用层检查器负责分析网络流量的应用层协议内容,是Snort3检测引擎的核心组件。

## 1. 概述

**代码规模**: 约 143,260 行代码

**子模块列表**:
| 模块 | 描述 |
|------|------|
| `http_inspect` | HTTP协议分析与检测 |
| `http2_inspect` | HTTP/2协议分析 |
| `dns` | DNS协议分析 |
| `smtp` | SMTP邮件协议分析 |
| `ftp_telnet` | FTP/Telnet协议分析 |
| `ssh` | SSH协议分析 |
| `ssl` | SSL/TLS协议分析 |
| `dce_rpc` | DCE/RPC协议分析 |
| `dnp3` | DNP3工业控制协议 |
| `modbus` | Modbus工业协议 |
| `sip` | SIP VoIP协议 |
| `imap` | IMAP邮件协议 |
| `pop` | POP3邮件协议 |
| `gtp` | GTP协议 |
| `iec104` | IEC 60870-5-104电力协议 |
| `mms` | MMS工业协议 |
| `opcua` | OPC UA协议 |
| `s7commplus` | S7commplus工业协议 |
| `socks` | SOCKS代理协议 |
| `cip` | CIP工业协议 |
| `netflow` | NetFlow分析 |
| `wizard` | 协议自动检测 |
| `back_orifice` | Back Orifice检测 |
| `tlv_pdu` | TLV PDU处理 |
| `rpc_decode` | RPC解码 |

## 2. HTTP Inspect

HTTP检查器是最大最复杂的应用层检查器。

### 2.1 类层次

```cpp
class HttpInspect : public HttpInspectBase
{
public:
    HttpInspect(const HttpParaList* params_);
    ~HttpInspect() override;

    bool get_buf(snort::InspectionBuffer::Type ibt, snort::Packet* p,
        snort::InspectionBuffer& b) override;
    bool get_buf(unsigned id, snort::Packet* p,
        snort::InspectionBuffer& b) override;

    HttpStreamSplitter* get_splitter(bool is_client_to_server) override
    { return &splitter[is_client_to_server ? HttpCommon::SRC_CLIENT
                                          : HttpCommon::SRC_SERVER]; }

    bool can_carve_files() const override { return true; }
    bool can_start_tls() const override { return true; }

    static snort::PduSection get_latest_is(const snort::Packet* p);
    static HttpCommon::SourceId get_latest_src(const snort::Packet* p);

private:
    HttpStreamSplitter splitter[2];
    // ...
};
```

### 2.2 核心缓冲区类型

```cpp
enum class HttpBufferId
{
    HTTP_BUFFER_STAT,      // 统计信息
    HTTP_BUFFER_METHOD,    // HTTP方法
    HTTP_BUFFER_URI,       // 请求URI
    HTTP_BUFFER_HEADER,    // 请求/响应头
    HTTP_BUFFER_COOKIE,    // Cookie头
    HTTP_BUFFER_BODY,      // 请求/响应体
    HTTP_BUFFER_RAW,       // 原始数据
    // ...
};
```

### 2.3 关键文件

| 文件 | 行数 | 描述 |
|------|------|------|
| `http_inspect.cc` | ~3500 | 主实现 |
| `http_inspect.h` | ~200 | 类定义 |
| `http_module.cc` | ~1500 | 配置模块 |
| `http_stream_splitter.cc` | ~800 | 流分割器 |
| `http_field.cc` | ~500 | 字段处理 |
| `http_enum.cc` | ~400 | 枚举定义 |
| `http_buffer_info.cc` | ~400 | 缓冲区信息 |

## 3. DNS 检查器

### 3.1 DNS 头部结构

```cpp
struct DNSHdr
{
    uint16_t id = 0;
    uint16_t flags = 0;
    uint16_t questions = 0;
    uint16_t answers = 0;
    uint16_t authorities = 0;
    uint16_t additionals = 0;
};

// 标志位定义
#define DNS_HDR_FLAG_REPLY_CODE_MASK        0x000F
#define DNS_HDR_FLAG_RESPONSE               0x8000
#define DNS_HDR_FLAG_TRUNCATED             0x0200
#define DNS_HDR_FLAG_AUTHORITATIVE         0x0400
#define DNS_HDR_FLAG_RECURSION_DESIRED     0x0100
#define DNS_HDR_FLAG_RECURSION_AVAIL       0x0080
```

### 3.2 DNS 资源记录类型

```cpp
#define DNS_RR_TYPE_A                       0x0001
#define DNS_RR_TYPE_NS                      0x0002
#define DNS_RR_TYPE_CNAME                   0x0005
#define DNS_RR_TYPE_SOA                     0x0006
#define DNS_RR_TYPE_PTR                     0x000C
#define DNS_RR_TYPE_HINFO                   0x000D
#define DNS_RR_TYPE_MX                      0x000F
#define DNS_RR_TYPE_TXT                     0x0010
#define DNS_RR_TYPE_AAAA                    0x001C
#define DNS_RR_TYPE_SRV                     0x0021
#define DNS_RR_TYPE_TLSA                    0x0034
```

### 3.3 关键文件

| 文件 | 行数 | 描述 |
|------|------|------|
| `dns.cc` | ~1200 | 主实现 |
| `dns.h` | ~500 | 头文件和结构 |
| `dns_module.cc` | ~500 | 配置模块 |

## 4. SMTP 检查器

### 4.1 SMTP 状态机

```cpp
// SMTP会话状态
#define STATE_CONNECT          0
#define STATE_COMMAND          1   // 命令状态
#define STATE_DATA             2   // 数据状态
#define STATE_BDATA            3   // 二进制数据状态
#define STATE_TLS_CLIENT_PEND  4   // 等待STARTTLS
#define STATE_TLS_SERVER_PEND  5   // 服务器等待TLS
#define STATE_TLS_DATA         6   // TLS加密数据
#define STATE_AUTH             7   // 认证状态

// MIME数据子状态
#define STATE_DATA_INIT        0
#define STATE_DATA_HEADER      1   // 头部分析
#define STATE_DATA_BODY        2   // 正文分析
#define STATE_MIME_HEADER      3   // MIME头
```

### 4.2 SMTP 标志位

```cpp
// 会话标志
#define SMTP_FLAG_GOT_MAIL_CMD               0x00000001
#define SMTP_FLAG_GOT_RCPT_CMD               0x00000002
#define SMTP_FLAG_BDAT                       0x00001000
#define SMTP_FLAG_ABORT                      0x00002000
#define SMTP_FLAG_XLINK2STATE_ALERTED        0x00000002
```

## 5. SSL/TLS 检查器

### 5.1 SSL 会话数据结构

```cpp
class SslFlowData : public SslBaseFlowData
{
public:
    SslFlowData(const snort::Flow* flow, snort::Inspector*,
        const SSLData* = nullptr);
    ~SslFlowData() override;

    SSLData& get_session() override { return session; }
    TLSConnectionData& get_tls_connection_data()
    { return tls_connection_data; }

private:
    SSLData session;
    TLSConnectionData tls_connection_data;
};
```

### 5.2 SSL 元数据事件

```cpp
class SslMetadataEvent : public SslTlsMetadataBaseEvent
{
public:
    SslMetadataEvent(const TLSConnectionData& conn_data)
        : tls_connection_data(conn_data) { }

    int32_t get_version() const override;
    int32_t get_curve() const override;
    int32_t get_cipher() const override;
    const std::string& get_server_name() const override;
    const std::string& get_subject() const override;
    const std::string& get_issuer() const override;
};
```

## 6. SSH 检查器

### 6.1 SSH 状态标志

```cpp
// 会话状态标志
#define SSH_FLG_CLEAR                       0x0
#define SSH_FLG_CLIENT_IDSTRING_SEEN        0x1
#define SSH_FLG_SERV_IDSTRING_SEEN          0x2
#define SSH_FLG_SERV_PKEY_SEEN              0x4
#define SSH_FLG_CLIENT_SKEY_SEEN            0x8
#define SSH_FLG_CLIENT_KEXINIT_SEEN         0x10
#define SSH_FLG_SERV_KEXINIT_SEEN          0x20
#define SSH_FLG_KEXDH_INIT_SEEN            0x40
#define SSH_FLG_KEXDH_REPLY_SEEN           0x80
#define SSH_FLG_CLIENT_NEWKEYS_SEEN        0x1000
#define SSH_FLG_SESS_ENCRYPTED             0x2000
```

### 6.2 协议版本检测

```cpp
// 自动检测宏
#define SSH_FLG_BOTH_IDSTRING_SEEN \
    (SSH_FLG_CLIENT_IDSTRING_SEEN | SSH_FLG_SERV_IDSTRING_SEEN)

#define SSH_FLG_V2_KEXINIT_DONE \
    (SSH_FLG_CLIENT_KEXINIT_SEEN | SSH_FLG_SERV_KEXINIT_SEEN)
```

## 7. FTP/Telnet 检查器

### 7.1 FTP 客户端结构

```cpp
struct FTP_CLIENT_REQ
{
    const char* cmd_line;
    unsigned int cmd_line_size;

    const char* cmd_begin;
    const char* cmd_end;
    unsigned int cmd_size;

    const char* param_begin;
    const char* param_end;
    unsigned int param_size;

    const char* pipeline_req;
};

struct FTP_CLIENT
{
    FTP_CLIENT_REQ request;
    int (* state)(void*, unsigned char, int);
};
```

### 7.2 子模块列表

| 文件 | 描述 |
|------|------|
| `ftp_client.h` | FTP客户端分析 |
| `ftp_server.h` | FTP服务器分析 |
| `ftp_cmd_lookup.h` | FTP命令查找 |
| `ftp_bounce_lookup.h` | FTP bounce攻击检测 |
| `telnet.h` | Telnet协议分析 |

## 8. DCE/RPC 检查器

### 8.1 DCE/RPC over TCP

```cpp
class DCE2_TcpInspector : public snort::Inspector
{
public:
    DCE2_TcpInspector(DceTcpModule*);
    ~DCE2_TcpInspector() override;

    void eval(snort::Packet*) override;

private:
    DceTcpModule* module;
    // ...
};

// 统计数据结构
struct dce2TcpStats
{
    PegCount events;
    PegCount co_pdus;
    PegCount co_bind;
    PegCount co_bind_ack;
    PegCount co_request;
    PegCount co_response;
    PegCount co_cancel;
    PegCount co_fault;
    // ...
};
```

### 8.2 自动检测

```cpp
inline bool DCE2_TcpAutodetect(snort::Packet* p)
{
    if (p->dsize >= sizeof(DceRpcCoHdr))
    {
        const DceRpcCoHdr* co_hdr = (const DceRpcCoHdr*)p->data;

        if ((DceRpcCoVersMaj(co_hdr) == DCERPC_PROTO_MAJOR_VERS__5)
            && (DceRpcCoVersMin(co_hdr) == DCERPC_PROTO_MINOR_VERS__0)
            && ...)
        {
            return true;
        }
    }
    return false;
}
```

## 9. 协议检测向导 (Wizard)

Wizard模块用于自动检测未知流量对应的协议。

### 9.1 Wizard 类结构

```cpp
class Wizard
{
public:
    Wizard();
    ~Wizard();

    void clear();
    void process(Packet*);

    static void init_service_prototype(const char*, unsigned,
        Inspector* = nullptr);

private:
    void check_dce(Packet*);
    void check_ssh(Packet*);
    void check_ssl(Packet*);
    void check_dns(Packet*);
    void check_smtp(Packet*);
    void check_imap(Packet*);
    void check_pop(Packet*);
    void check_ftp(Packet*);
    void check Sip(Packet*);
    void check_s7commplus(Packet*);

    unsigned subtype;
    // ...
};
```

## 10. 核心模式: 流分割器

每个应用层检查器实现 `StreamSplitter` 接口进行流重组:

```cpp
class HttpStreamSplitter : public snort::StreamSplitter
{
public:
    HttpStreamSplitter(bool is_client_to_server,
        HttpParaList* params);
    ~HttpStreamSplitter() override;

    StreamStatus scan(snort::Packet*, const uint8_t* data,
        uint32_t length, uint32_t not_inspected, uint32_t остаток,
        bool is_reassembled) override;

    bool finish(snort::Flow*) override;
    void reset_state() override;
    void reassemble_reset() override;

private:
    bool scan_pipeline_client(const uint8_t*, uint32_t,
        uint32_t*, uint32_t*);
    // ...
};
```

## 11. 关键文件清单

| 模块 | 主文件 | 行数 |
|------|--------|------|
| HTTP | `http_inspect.cc` | ~3500 |
| HTTP2 | `http2_inspect.cc` | ~3000 |
| DNS | `dns.cc` | ~1200 |
| SMTP | `smtp.cc` | ~2000 |
| FTP/Telnet | `ftp_telnet.cc` | ~2000 |
| SSH | `ssh.cc` | ~1200 |
| SSL | `ssl.cc` | ~2500 |
| DCE/RPC | `dce_rpc.cc` | ~3000 |
| SIP | `sip.cc` | ~2000 |
| Wizard | `wizard.cc` | ~1500 |

## 12. 与其他模块的关系

```
┌─────────────────────────────────────────────────────────────┐
│                   Network Inspectors                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Binder  │ │PortScan  │ │ ARP Spoof│ │   RNA   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Service Inspectors                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │HTTP Inspect│ │   DNS   │ │   SMTP   │ │    SSL   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  DCE/RPC  │ │   SSH   │ │   SIP   │ │  Wizard  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Detection Engine                          │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              IPS Rules / Detection Plugins              │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 13. 总结

应用层检查器特点:

1. **协议专用性** - 每个检查器针对特定应用层协议
2. **状态追踪** - 维护协议会话状态(如HTTP请求/响应状态机)
3. **流重组** - 实现StreamSplitter接口进行TCP流重组
4. **事件发布** - 通过Pub/Sub发布协议元数据事件
5. **缓冲区管理** - 提供标准化的InspectionBuffer接口

主要检测能力:
- 协议异常和格式错误
- 协议特定攻击(如HTTP攻击、DNS隧道)
- 应用层命令/控制通信
- 敏感数据泄露
