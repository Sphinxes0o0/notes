---
type: source
source-type: github
title: "Snort3 Service Inspectors Source"
author: "Cisco Talos (源作者), Open Source Community"
date: 2026-05-27
size: medium
path: ~/workspace/github/snort3/src/service_inspectors/
summary: "Snort3 IDS 服务层协议解析器源码（504文件），实现 HTTP/2/SSL/DNS/SMB 等协议的端口无关深度检测。"
---

# Snort3 Service Inspectors 源码分析

## 概述

**源码路径**：`~/workspace/github/snort3/src/service_inspectors/`
**文件数量**：504 文件，30 个子目录
**功能**：实现 Snort3 的服务层协议解析（Service Inspection），每个协议对应独立 Inspector 模块。

## 核心文件

| 文件 | 作用 |
|------|------|
| `service_inspectors.h` | Service Inspector 基类定义 |
| `service_inspectors.cc` | 插件注册入口（`load_service_inspectors()`） |
| `wizard/wizard.cc` | 端口无关协议识别引擎 |
| `wizard/hexes.cc` | 二进制模式匹配（HexBook） |
| `wizard/spells.cc` | 文本模式匹配（SpellBook） |
| `wizard/curse_book.h` | Curse 状态机算法注册 |

## 插件注册架构

### InspectApi 结构

```cpp
// 位置：framework/inspector.h
struct InspectApi {
    BaseApi base;              // 名称、类型、版本
    InspectorType type;       // IT_SERVICE / IT_WIZARD / IT_STREAM
    uint32_t proto_bits;      // PROTO_BIT__TCP 等协议标志
    const char** buffers;      // 导出的缓冲区名称
    const char* service;       // 服务名（"http", "dns" 等）
    InspectFunc pinit;         // 插件初始化
    InspectFunc pterm;         // 插件终止
    InspectFunc tinit;         // 线程初始化
    InspectFunc tterm;         // 线程终止
    InspectNew ctor;           // Inspector 构造器
    InspectDelFunc dtor;      // Inspector 析构器
    InspectSsnFunc ssn;       // 会话创建器
    InspectFunc reset;        // 统计重置
};
```

### 静态注册示例

```cpp
// service_inspectors.cc
const BaseApi* service_inspectors[] = {
#ifdef STATIC_INSPECTORS
    sin_bo,       // Back Orifice
    sin_ftp_client,
    sin_ftp_server,
    // ... 更多静态链接的 inspector
#endif
    nullptr
};

void load_service_inspectors() {
    PluginManager::load_plugins(service_inspectors);
    PluginManager::load_plugins(sin_dns);
    PluginManager::load_plugins(sin_http);
    // ...
}
```

## HTTP Inspector

### 目录结构

```
http_inspect/
├── http_inspect.h              # 主类定义
├── http_flow_data.h            # FlowData（99 files）
├── http_stream_splitter.h      # Stream 分片器
├── http_module.h               # 配置模块
├── http_buf_init.cc            # 缓冲区初始化
├── http_contexts.cc            # HTTP 上下文管理
├── http_events.cc              # 事件生成
├── http_media.cc               # 媒体类型处理
├── http_msg.cc                 # 消息解析
├── http_msg_head.cc            # 头部解析
├── http_msg_body.cc            # Body 解析
└── http_george.cc              # 检测引擎
```

### 类层次

```cpp
// http_inspect_base.h
class HttpInspectBase : public snort::Inspector {
public:
    virtual HttpCommon::SectionType get_type_expected(
        snort::Flow* flow, HttpCommon::SourceId source_id) const = 0;
    virtual void eval(snort::Packet*, HttpCommon::SourceId,
        const uint8_t* data, uint16_t dsize) = 0;
    virtual bool get_buf(InspectionBuffer::Type, snort::Packet*,
        InspectionBuffer&) = 0;
};

// http_inspect.h
class HttpInspect : public HttpInspectBase {
    HttpStreamSplitter splitter[2];  // [0]=client, [1]=server
    const HttpParaList* const params;
};
```

### FlowData

```cpp
// http_flow_data.h
class HttpFlowData : public snort::FlowData {
public:
    static unsigned inspector_id;
    // 追踪请求/响应状态、头部、编码等
};
```

## DNS Inspector

### 目录结构

```
dns/
├── dns.h                       # 主类定义
├── dns_flow_data.h             # FlowData
├── dns_module.h                # 配置模块
├── dns_splitter.h              # TCP 分片器
├── dns_events.cc               # 事件
├── dns_udp.cc                  # UDP 处理
└── dns_parse.cc                # 解析逻辑
```

### 类定义

```cpp
// dns.h
class Dns : public snort::Inspector {
public:
    Dns(DnsModule*);
    void eval(snort::Packet*) override;
    StreamSplitter* get_splitter(bool) override;
    bool supports_no_ips() const override { return true; }
};

// DNS over TCP FlowData
class DnsFlowData : public snort::FlowData {
    static unsigned inspector_id;
    DNSData session;
};

// DNS over UDP FlowData
class DnsUdpFlowData : public snort::FlowData {
    static unsigned inspector_id;
    std::set<uint16_t> trans_ids;  // 事务 ID 追踪
};
```

## SSL Inspector

### 目录结构

```
ssl/
├── ssl_inspector.h             # 主类
├── ssl_flow_data.h             # FlowData
├── ssl_module.h                # 配置模块
├── ssl_states.cc               # 状态机
├── ssl_handlers.cc             # 握手处理
└── ssl_events.cc               # 事件
```

### 类定义

```cpp
// ssl_inspector.h
class SslFlowData : public SslBaseFlowData {
public:
    SSLData& get_session() override { return session; }
private:
    SSLData session;
    TLSConnectionData tls_connection_data;
};
```

## DCE/RPC Inspector (SMB/TCP/UDP)

### 目录结构

```
dce_rpc/
├── dce_smb.h                   # SMB 传输
├── dce_tcp.h                   # TCP 传输
├── dce_udp.h                   # UDP 传输
├── dce_common.h                # 公共逻辑
├── dce_paf.h                   # PAF 辅助
├── dce_smb_module.h            # SMB 配置
├── dce_tcp_module.h            # TCP 配置
└── dce_smb_data.cc             # SMB 数据处理
```

### FlowData

```cpp
// dce_smb.h
class Dce2SmbFlowData : public snort::FlowData {
public:
    static unsigned inspector_id;
    DCE2_SmbVersion smb_version;
    void* dce2_smb_session_data;
};
```

## Wizard 服务发现

### 目录结构

```
wizard/
├── wizard.cc                   # 主逻辑
├── wizard.h                    # Wizard / MagicSplitter 类
├── hexes.cc                    # HexBook 实现
├── spells.cc                   # SpellBook 实现
├── curse_book.cc               # CurseBook 实现
├── curse_book.h                # curse 算法注册
└── tests/                      # 单元测试
```

### 检测流程

```cpp
// wizard.cc - MagicSplitter::scan()
Status scan(Packet*, const uint8_t* data, uint32_t len,
    uint32_t flags, uint32_t* fp) override {
    // 1. 尝试 hex 模式匹配
    if (wizard->cast_spell(data, len, &service, wand.hexes))
        goto done;

    // 2. 尝试 spell 模式匹配
    if (wizard->cast_spell(data, len, &service, wand.spells))
        goto done;

    // 3. 尝试 curse 算法
    if (wizard->curse(data, len, service, wand.curses))
        goto done;

    // 4. 未匹配
    return SEARCH;
done:
    flow->service = service;
    return STOP;
}
```

### 支持的 Curse 算法

| 算法 | 协议 |
|------|------|
| `ssl_v2_curse()` | SSLv2 |
| `dce_tcp_curse()` | DCE/RPC over TCP |
| `dce_smb_curse()` | DCE/RPC over SMB |
| `dce_udp_curse()` | DCE/RPC over UDP |
| `mms_curse()` | MMS 工业协议 |
| `opcua_curse()` | OPC UA |
| `s7commplus_curse()` | S7commplus |

## 其他服务 Inspector

| 目录 | 服务 | 说明 |
|------|------|------|
| `ftp_telnet/` | FTP | 客户端/服务端/数据通道 |
| `smtp/` | SMTP | 邮件协议 |
| `sip/` | SIP | VoIP 信令 |
| `ssh/` | SSH | 安全外壳 |
| `pop/` | POP3 | 邮件收取 |
| `imap/` | IMAP4 | 邮件访问 |
| `netflow/` | NetFlow | 流量统计 |
| `cip/` | CIP | 工业协议 |
| `dnp3/` | DNP3 | SCADA 协议 |
| `gtp/` | GTP | 3G 隧道协议 |
| `iec104/` | IEC 60870-5-104 | 电力协议 |
| `mms/` | MMS | 制造消息服务 |
| `modbus/` | Modbus | 工业协议 |
| `opcua/` | OPC UA | 工业互操作 |
| `rpc_decode/` | RPC | RPC 解析 |
| `s7commplus/` | S7commplus | 西门子 PLC |
| `tlv_pdu/` | TLV PDU | 通用 TLV 解析 |
| `back_orifice/` | Back Orifice | 远程控制 |

## Flow 数据流

```
Packet 到达
    ↓
MagicSplitter::scan()  ← Wizard 检测协议
    ↓
Flow.service 设置（"http", "dns" 等）
    ↓
Binder 绑定对应 Inspector
    ↓
Inspector::eval() 处理
    ↓
FlowData 存储/读取会话状态
```

## 关键模式

### 1. FlowData 静态 ID 注册

```cpp
// 模块初始化时
void HttpFlowData::init() {
    inspector_id = snort::FlowData::create_flow_data_id();
}

// 访问时
HttpFlowData* hd = static_cast<HttpFlowData*>(
    flow->get_flow_data(HttpFlowData::inspector_id));
```

### 2. Stream Splitter PAF

```cpp
// 返回 flush 偏移量
Status scan(Packet*, const uint8_t* data, uint32_t len,
    uint32_t flags, uint32_t* fp) override {
    // 检测到请求完整 → *fp = 请求结束偏移
    *fp = request_end;
    return FLUSH;
}

bool is_paf() override { return true; }
```

### 3. Module-Inspector 配对

```cpp
// Module 负责配置
class HttpModule : public snort::Module {
    bool set(const char*, snort::Value&, snort::SnortConfig*) override;
    HttpParaList* get_data();
};

// Inspector 使用 Module 配置
HttpInspect::configure(snort::SnortConfig* config) {
    HttpModule* mod = (HttpModule*)
        snort::ModuleManager::get_module("http_inspect");
    params = mod->get_data();
}
```

## 相关页面

- [[snort3-service-inspectors]] - Service Inspector 架构概念
- [[snort3-wizard]] - Wizard 服务发现详解
- [[snort3-architecture]] - 整体架构
