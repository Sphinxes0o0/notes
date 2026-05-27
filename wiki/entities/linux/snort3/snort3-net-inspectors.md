---
type: entity
tags: [snort3, network-inspector, intrusion-detection, network-inspectors, packet-io]
created: 2026-05-27
sources: [github-snort3, github-snort3-net-inspectors]
---

# Snort3 网络 inspectors 架构

## 架构概览

Snort3 采用**插件化 inspector 系统**，通过 `PluginManager::load_plugins()` 动态加载。Inspectors 是数据包处理管道的核心单元。

### 核心基类

**Inspector 基类** (`framework/inspector.h`)：
```cpp
class Inspector {
    virtual bool configure(SnortConfig*);
    virtual void eval(Packet*);
    virtual bool likes(Packet*);   // 过滤器
    virtual void tinit/tterm();    // 线程本地初始化
};
```

**Module 基类** (`framework/module.h`)：配置管理，处理 `begin/set/end` 生命周期。

### Inspector 类型体系

| Type | 用途 | 示例 |
|------|------|------|
| `IT_NETWORK` | 处理原始数据包 | arp_spoof |
| `IT_STREAM` | 流追踪/分片重组 | stream_ip, stream_tcp |
| `IT_SERVICE` | 应用层协议分析 | http, ssl, dns |
| `IT_PACKET` | 数据包级规范化 | normalize |
| `IT_WIZARD` | 服务猜测 | service_wizard |
| `IT_BINDER` | 流量绑定协调器 | binder |
| `IT_CONTROL` | 检测前处理 | appid |
| `IT_PROBE` | 检测后处理 | perf_monitor, port_scan |

### 协议位标志

```cpp
PROTO_BIT__IP | PROTO_BIT__TCP | PROTO_BIT__UDP | PROTO_BIT__ICMP | PROTO_BIT__ARP
```

每个 inspector 通过 `proto_bits` 声明关注的协议。

---

## 核心组件

### Binder — 流量绑定协调器

`network_inspectors/binder/binder.cc` 是 inspector 管道的**中央调度器**：

- 维护 `bindings[]` 规则表
- 根据五元组 + 服务 + 角色选择 inspector
- 通过 DataBus 订阅流状态事件
- 支持 `BA_RESET`, `BA_BLOCK`, `BA_ALLOW`, `BA_INSPECT` 动作

### DataBus — 组件间通信

`framework/data_bus.h` 实现发布/订阅模式：

```cpp
DataBus::publish(stream_pub_id, StreamEventIds::IP_BIDIRECTIONAL, p);
DataBus::subscribe(intrinsic_pub_key, IntrinsicEventIds::FLOW_STATE_SETUP, handler);
```

---

## 关键 Inspectors

### ARP Spoof Inspector

- **路径**: `network_inspectors/arp_spoof/`
- **类型**: `IT_NETWORK`, `PROTO_BIT__ARP`
- **功能**: 检测 ARP 缓存投毒
  - 检查单播 ARP 请求
  - 验证 Ethernet MAC 与 ARP MAC 匹配
  - 使用用户配置的 IP→MAC 映射表

### Stream-IP Inspector

- **路径**: `stream/ip/stream_ip.cc`
- **类型**: `IT_STREAM`, `PROTO_BIT__ICMP | PROTO_BIT__IP`
- **功能**: IP 分片重组
  - `Defrag` 类处理实际重组
  - `IpSession::process()` 管理分片跟踪
  - 通过 DataBus 发布双向流事件

### Normalizer Inspector

- **路径**: `network_inspectors/normalize/`
- **类型**: `IT_PACKET`, `PROTO_BIT__ANY_IP`
- **功能**: 数据包规范化
  - IP4/IP6 TTL 规范化
  - TCP 选项/窗口规范化
  - ICMP 规范化

### 无独立 ICMP Inspector

ICMP 由 Stream-IP 统一处理（跟踪 ICMP  flows），Codec 层负责解析。

---

## Packet I/O 架构

`packet_io/` 目录实现 DAQ（Data Acquisition）抽象层：

### 分层结构

```
Wire → DAQ Module → SFDAQInstance → SFDAQ → Packet Processing
```

### 核心组件

| 组件 | 文件 | 职责 |
|------|------|------|
| `SFDAQ` | `sfdaq.h/cc` | 全局 DAQ 操作（load/unload/init/term） |
| `SFDAQInstance` | `sfdaq_instance.h/cc` | 每线程 DAQ 实例，批量收包 |
| `SFDAQConfig` | `sfdaq_config.h/cc` | DAQ 配置（模块、输入、batch_size） |
| `Active` | `active.h/cc` | 主动响应（drop/reset/block/inject） |
| `PacketTracer` | `packet_tracer.h/cc` | 调试追踪 |
| `Trough` | `trough.h/cc` | 包源发现（pcap 文件/接口） |

### 包处理流程

```
1. Trough::setup()         发现包源
2. SFDAQ::init()           初始化 DAQ
3. SFDAQInstance::start()  开始收包
4. receive_messages()      批量接收（默认64个/批）
5. next_message()          遍历批次
6. Codec 解码              协议解析
7. Inspector 管道         数据包检查
8. Active::execute()       执行主动响应
9. finalize_message()      返回 verdict 给 DAQ
```

### Verdict 类型

```cpp
DAQ_VERDICT_PASS | DAQ_VERDICT_BLOCK | DAQ_VERDICT_REPLACE |
DAQ_VERDICT_WHITELIST | DAQ_VERDICT_BLACKLIST | DAQ_VERDICT_IGNORE
```

### 隧道协议支持

SFDAQInstance 通过 `daq_tunnel_mask` 跟踪支持的隧道协议：
GTP, TEREDO, VXLAN, GRE, 4in4, 6in4, 4in6, 6in6, MPLS, GENEVE

---

## Inspector 标准模式

```cpp
// 1. API 定义
static const InspectApi as_api = {
    { PT_INSPECTOR, sizeof(InspectApi), INSAPI_VERSION, ... },
    IT_NETWORK,              // type
    PROTO_BIT__ARP,         // proto_bits
    nullptr,                // buffers
    nullptr,                // service
    nullptr, nullptr,       // pinit, pterm
    nullptr, nullptr,       // tinit, tterm
    as_ctor,                // constructor
    as_dtor,                // destructor
    nullptr,                // ssn
    nullptr,                // reset
};

// 2. 插件导出
const BaseApi* nin_arp_spoof[] = { &as_api.base, nullptr };
```

---

## 相关概念

- [[snort3]]
- [[intrusion-detection-system]]
- [[packet-capture]]
- [[network-security-monitoring]]
- [[stream-reassembly]]

## 来源详情

- [[github-snort3-net-inspectors]] — 源代码分析
