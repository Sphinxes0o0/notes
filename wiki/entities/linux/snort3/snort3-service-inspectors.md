---
type: entity
tags: [IDS, intrusion-detection, snort, network-security, service-inspection]
created: 2026-05-27
sources: [github-snort3-service-inspectors]
---

# Snort3 Service Inspectors

## 定义

Snort3 的 **Service Inspectors** 是基于插件架构的协议解析模块，每个服务协议（HTTP、DNS、SSL 等）对应独立的 Inspector，实现端口无关的深度包检测。

## 核心架构

### 插件注册机制

Service Inspectors 通过 `InspectApi` 结构体向 Snort3 框架注册（`service_inspectors.cc`）：

```cpp
static const InspectApi wiz_api =
{
    { PT_INSPECTOR, sizeof(InspectApi), INSAPI_VERSION, ... },
    IT_WIZARD,           // InspectorType
    PROTO_BIT__ANY_PDU,
    nullptr,             // buffers
    "http",              // service name
    mod_ctor,            // module constructor
    wiz_ctor,            // inspector constructor
    wiz_dtor,
    nullptr,             // session creator
    nullptr              // reset
};
```

### Inspector 类型体系

| Type | 用途 |
|------|------|
| `IT_SERVICE` | 服务 PDU 提取和分析（主要类型） |
| `IT_WIZARD` | 协议识别（端口无关服务发现） |
| `IT_STREAM` | 流追踪和分片重组 |
| `IT_PACKET` | 仅处理原始数据包 |
| `IT_CONTROL` | 检测前处理所有数据包 |

### 基类继承

```
Inspector (framework/inspector.h)
  └── HttpInspectBase (abstract)
          └── HttpInspect (HTTP/1.x)
  └── Dns (DNS)
  └── Ssl (SSL/TLS)
  └── Dce2Tcp / Dce2Smb (DCE/RPC over TCP/SMB)
```

## 服务发现机制

### Wizard - 端口无关协议识别

`wizard/` 模块使用三种检测方法：

| 方法 | 描述 | 示例 |
|------|------|------|
| **Hex Patterns** | 二进制模式匹配（`HexBook`） | `\x80 ?? ?? ??` |
| **Spell Patterns** | 文本模式匹配（`SpellBook`） | `GET /index.html HTTP/1.1` |
| **Curse Algorithms** | 状态机协议检测 | SSLv2, DCE/RPC, MMS, OPC UA |

**检测流程**：
1. `MagicSplitter::scan()` 接收原始数据
2. 依次尝试：hex → spell → curse
3. 匹配成功 → `flow->service = service_name` → 返回 `STOP`
4. 达最大深度 → 返回 `ABORT`

### Cursee 算法示例

```cpp
typedef bool (* curse_alg)(const uint8_t* data, unsigned len, CurseTracker*);

// 注册的 curse 算法
ssl_v2_curse()      // SSLv2 检测
dce_tcp_curse()     // DCE/RPC over TCP
dce_smb_curse()     // DCE/RPC over SMB
dce_udp_curse()     // DCE/RPC over UDP
mms_curse()         // MMS 工业协议
opcua_curse()       // OPC UA
s7commplus_curse()  // S7commplus
```

## Flow 数据管理

### Flow 类结构

`flow/flow.h` 中的 Flow 对象存储：

```cpp
class Flow {
    // 指向服务处理器的指针
    Inspector* ssn_client = nullptr;   // 客户端 inspector
    Inspector* ssn_server = nullptr;   // 服务端 inspector
    Inspector* clouseau = nullptr;      // 服务识别器（wizard）
    Inspector* gadget = nullptr;      // 服务处理器

    SnortProtocolId snort_protocol_id;
    FlowDataStore flow_data;           // FlowData 存储
    FlowStash stash;                   // 键值存储
};
```

### FlowData 模式

每个 Inspector 定义自己的 `FlowData` 子类，使用**静态 ID** 注册：

```cpp
class HttpFlowData : public snort::FlowData {
public:
    static unsigned inspector_id;
    static void init() {
        inspector_id = snort::FlowData::create_flow_data_id();
    }
    // ... 状态追踪字段
};
```

**访问模式**：
```cpp
DnsFlowData* flow_data =
    (DnsFlowData*) flow->get_flow_data(DnsFlowData::inspector_id);
```

## 关键服务 Inspector

### HTTP Inspector (`http_inspect/`)

- **类层次**：`HttpInspectBase` → `HttpInspect`
- **FlowData**：`HttpFlowData`（追踪请求/响应状态）
- **Stream Splitter**：`HttpStreamSplitter`（PAF 启用）
- **功能**：请求行解析、头部检测、编码处理、文件提取、TLS 启动

### HTTP2 Inspector (`http2_inspect/`)

- 独立的 HTTP/2 协议解析器
- 支持 HPACK 头部压缩

### DNS Inspector (`dns/`)

- **FlowData**：`DnsFlowData`（TCP）、`DnsUdpFlowData`（UDP）
- **Splitter**：基于长度的 DNS over TCP 分片器
- **支持 no-ips 模式**：可在禁用 IPS 时工作

### SSL/TLS Inspector (`ssl/`)

- **FlowData**：`SslFlowData`、`TLSConnectionData`
- 追踪 SSL 会话、证书信息、TLS 版本

### DCE/RPC Inspector (`dce_rpc/`)

支持多种传输层：
- **SMB**：`Dce2SmbFlowData`
- **TCP**：`Dce2TcpFlowData`
- **UDP**：`Dce2UdpFlowData`

检测 SMB 版本、DCE/RPC PDU 分割

### Wizard (`wizard/`)

- **核心检测引擎**
- `MagicSplitter` 实现 PAF（Protocol Awareness Flag）
- 支持 30+ 协议模式

## Stream Splitter 模式

分片重组器负责流式数据缓冲和协议边界识别：

```cpp
class StreamSplitter {
public:
    enum Status { ABORT, START, SEARCH, FLUSH, LIMIT, STOP };
    virtual Status scan(Packet*, const uint8_t* data,
        uint32_t len, uint32_t flags, uint32_t* fp) = 0;
    virtual bool is_paf();  // Protocol Awareness Flag
};
```

**PAF**：启用后，分片器返回 `flush_offset` 告诉 stream TCP 何时应该 flush 数据。

## Binder 绑定机制

`network_inspectors/binder/` 将 `flow->service` 字符串映射到对应 Inspector：

```cpp
// Flow 设置 service 后
flow->service = "http";
// Binder 查找 "http" → 绑定 HttpInspect
```

## 目录结构

```
service_inspectors/
├── http_inspect/      # HTTP/1.x (99 files)
├── http2_inspect/     # HTTP/2 (72 files)
├── ssl/               # SSL/TLS (15 files)
├── dns/               # DNS (15 files)
├── dce_rpc/           # DCE/RPC + SMB (64 files)
├── wizard/            # 服务发现 (14 files)
├── ftp_telnet/        # FTP (40 files)
├── smtp/              # SMTP (17 files)
├── sip/               # SIP (24 files)
├── ssh/               # SSH (12 files)
└── [其他协议...]       # POP, IMAP, NetFlow, CIP, DNP3, GTP...
```

## 相关概念

- [[snort3-architecture]] - Snort3 整体架构
- [[snort3-wizard]] - 服务发现引擎详解
- [[intrusion-detection-systems]] - IDS 基础
- [[network-monitoring]] - 网络监控

## 来源详情

- [[github-snort3-service-inspectors]] - 源码分析
