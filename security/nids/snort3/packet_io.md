---
title: "packet_io 模块 — 数据包捕获与发送 (DAQ封装)"
description: "`packet_io` 模块是 Snort3 与数据包采集抽象层(DAQ)的接口封装，负责数据包的接收、发送和控制。"
---
# packet_io 模块 — 数据包捕获与发送 (DAQ封装)

## 概述

`packet_io` 模块是 Snort3 与数据包采集抽象层(DAQ)的接口封装，负责数据包的接收、发送和控制。

## 文件清单

| 文件 | 行数 | 功能 |
|------|------|------|
| sfdaq.h / sfdaq.cc | 72 / ~200 | DAQ静态方法封装 |
| sfdaq_instance.h / sfdaq_instance.cc | 105 / ~435 | DAQ实例管理(单实例封装) |
| sfdaq_module.h / sfdaq_module.cc | 90 / ~298 | Snort Module接口 |
| sfdaq_config.h / sfdaq_config.cc | 85 / ~131 | DAQ配置管理 |
| active.h / active.cc | 237 / ~1054 | 数据包处理裁定(Verdict)管理 |
| trough.h / trough.cc | 88 / ~265 | 批量数据包缓冲队列 |
| packet_tracer.h / packet_tracer.cc | ~59 / ~908 | 数据包追踪 |
| packet_tracer_module.h / packet_tracer_module.cc | ~59 / ~242 | 追踪Module接口 |
| packet_constraints.h / packet_constraints.cc | 76 / ~292 | 数据包过滤约束 |

**总计: 约6056行**

## 类层次

```
SFDAQ (静态封装类)
├── load() / unload() — 动态加载DAQ模块
├── init() / term() — 初始化/终止
├── get_local_instance() — 获取线程本地实例
└── inject() / forwarding_packet() — 数据包注入

SFDAQInstance (DAQ实例封装)
├── init() — 初始化实例
├── start() / stop() / reload() — 生命周期管理
├── receive_messages() — 接收批量数据包
├── next_message() — 获取下一消息
├── inject() — 注入数据包
├── add_expected() — 添加预期流
└── get_tunnel_bypass() — 隧道旁路查询

SFDAQModule (Snort Module)
└── 实现 Module 接口，提供配置和统计

Active (裁定管理)
├── send_reset() / send_unreach() — 发送响应
├── send_data() / inject_data() — 数据发送
├── drop_packet() / daq_drop_packet() — 丢弃
├── block_session() / reset_session() / trust_session() — 会话控制
├── hold_packet() / cancel_packet_hold() — 延迟处理
└── queue() / execute() — 延迟动作执行
```

## 核心函数

### SFDAQ 静态方法
```cpp
static void load(const SFDAQConfig*);     // 加载DAQ模块
static void unload();                     // 卸载DAQ模块
static bool init(const SFDAQConfig*, unsigned total_instances);
static void term();
static SFDAQInstance* get_local_instance(); // 获取线程本地实例
static int inject(DAQ_Msg_h, int rev, const uint8_t* buf, uint32_t len);
static bool can_inject();                 // 是否支持注入
static bool can_inject_raw();             // 是否支持原始注入
```

### SFDAQInstance 实例方法
```cpp
bool init(DAQ_Config_h, const std::string& bpf_string);
DAQ_RecvStatus receive_messages(unsigned max_recv);
int finalize_message(DAQ_Msg_h msg, DAQ_Verdict verdict);
int inject(DAQ_Msg_h, int rev, const uint8_t* buf, uint32_t len);
bool add_expected(const Packet* ctrlPkt, const SfIp* cliIP, uint16_t cliPort,
    const SfIp* srvIP, uint16_t srvPort, IpProtocol, unsigned timeout_ms, unsigned flags);
```

### Active 裁定管理
```cpp
void send_reset(Packet*, EncodeFlags);           // 发送TCP RST
void send_unreach(Packet*, snort::UnreachResponse); // 发送ICMP不可达
void inject_data(Packet*, EncodeFlags, const uint8_t* buf, uint32_t len);
void drop_packet(const Packet*, bool force = false); // 丢弃数据包
void trust_session(Packet*, bool force = false);  // 信任会话
void block_session(Packet*, bool force = false); // 阻止会话
void hold_packet(const Packet*);                  // 持有数据包(IPS-inline)
void queue(snort::ActiveAction* a, snort::Packet* p); // 队列延迟动作
```

## DAQ Verdict 裁定

```cpp
enum ActiveStatus : uint8_t
{ AST_ALLOW, AST_CANT, AST_WOULD, AST_FORCE, AST_MAX };

enum ActiveActionType : uint8_t
{ ACT_TRUST, ACT_ALLOW, ACT_HOLD, ACT_RETRY, ACT_REWRITE,
  ACT_DROP, ACT_BLOCK, ACT_RESET, ACT_MAX };
```

## 模块交互

```
packet_io
    │
    ├──[接收]─► codec ──► flow/stream ──► detection
    │                              │
    │◄──[裁定]─────────────────────┘
    │
    └──[发送]─► DAQ (SFDAQInstance) ──► 网络接口
```

- **上游**: DAQ模块(pcap/afpacket/dpdkn等)提供原始数据包
- **下游**: codec解析协议, flow/stream管理会话状态
- **裁定**: Active类处理inline模式的延迟动作队列

## 关键数据结构

### DAQStats 统计
```cpp
struct DAQStats {
    PegCount pcaps;           // 总数据包数
    PegCount received;        // 接收数
    PegCount analyzed;        // 分析数
    PegCount dropped;         // 丢弃数
    PegCount filtered;        // 过滤数
    PegCount injected;        // 注入数
    PegCount verdicts[MAX_DAQ_VERDICT]; // 各裁定计数
};
```

### SFDAQConfig 配置
```cpp
struct SFDAQConfig {
    std::vector<std::string> module_dirs;  // DAQ模块目录
    std::stringdaq_type;                  // DAQ类型(pcap/afpacket/...)
    DAQ_Mode mode;                        // 模式(被动/内联/…)
    std::string bpf_string;               // BPF过滤表达式
    uint32_t batch_size;                  // 批量大小
};
```
