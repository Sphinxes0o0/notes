---
title: "stream 模块 — TCP流重组与状态跟踪"
description: "`stream` 模块负责TCP流重组、IP分片重组、会话状态管理，以及协议感知Flush(PAF)。"
---
# stream 模块 — TCP流重组与状态跟踪

## 概述

`stream` 模块负责TCP流重组、IP分片重组、会话状态管理，以及协议感知Flush(PAF)。

## 文件清单

### 基础流模块 (base/)

| 文件 | 行数 | 功能 |
|------|------|------|
| stream_base.cc | ~453 | 流基础实现 |
| stream_module.cc | 678 | Snort Module |
| stream_ha.cc | 284 | 高可用性同步 |
| stream_ha.h | 64 | HA接口 |
| stream_module.h | 233 | Module接口 |

### TCP流追踪 (tcp/)

| 文件 | 行数 | 功能 |
|------|------|------|
| tcp_stream_tracker.h / .cc | ~400 | TCP会话追踪 |
| tcp_stream.h | ~200 | TCP流接口 |
| held_packet_queue.h / .cc | ~150 | 持有数据包队列 |

### IP分片重组 (ip/)

| 文件 | 行数 | 功能 |
|------|------|------|
| ip_defrag.h / .cc | 70 / 2022 | IP分片重组 |
| stream_ip.h / .cc | 70 / 192 | IP流追踪 |
| ip_session.h / .cc | 97 / 292 | IP会话 |
| ip_ha.h / .cc | 50 / 66 | IP高可用性 |
| ip_module.h / .cc | ~130 / 204 | IP Module |

### PAF (协议感知Flush)

| 文件 | 行数 | 功能 |
|------|------|------|
| paf.h | 87 | PAF状态和函数 |
| flush_bucket.cc | 124 | Flush桶管理 |
| pafng.h | 112 | PAF配置 |

**stream总计: 约25064行**

## 类层次

```
StreamSplitter (流分割器基类)
├── AtomSplitter       // 定长分割
├── LogSplitter        // 日志分割
└── StopAndWaitSplitter // 停等分割

StreamSplitter::Status
├── ABORT   // 中止
├── START   // 开始
├── SEARCH  // 搜索中
├── FLUSH   // 刷新
├── LIMIT   // 限制
├── LIMITED // 已限制
└── STOP    // 停止

PAF_State (协议感知Flush状态)
├── seq    // 流光标
├── pos    // 最后刷新位置
├── fpt    // 当前刷新点
├── tot    // 总刷新字节
└── paf    // 扫描状态
```

## 核心函数

### StreamSplitter 接口
```cpp
class SO_PUBLIC StreamSplitter {
public:
    enum Status { ABORT, START, SEARCH, FLUSH, LIMIT, LIMITED, STOP };

    // 扫描数据,返回刷新点
    virtual Status scan(
        Packet*,
        const uint8_t* data,    // 到达的有序数据
        uint32_t len,           // 数据长度
        uint32_t flags,         // 方向标志
        uint32_t* fp            // 刷新点(偏移)
    ) = 0;

    // 结束扫描
    virtual bool finish(Flow*);

    // 重组
    virtual const StreamBuffer reassemble(
        Flow*, unsigned total, unsigned offset,
        const uint8_t* data, unsigned len,
        uint32_t flags, unsigned& copied);

    virtual bool is_paf();      // 是否PAF
    virtual unsigned max(Flow*); // 最大缓存
};
```

### PAF 函数
```cpp
void* paf_new(unsigned max);      // 创建PAF配置
void paf_delete(void*);            // 释放配置
void paf_setup(PAF_State*);        // 会话开始时调用
void paf_reset(PAF_State*);       // 重新扫描时调用
void paf_clear(PAF_State*);       // 会话结束时调用
void paf_initialize(PAF_State*, uint32_t seq);
int32_t paf_check(StreamSplitter*, PAF_State*, Packet*,
    const uint8_t* data, uint32_t len, uint32_t total,
    uint32_t seq, uint32_t* flags);
```

### IP分片重组
```cpp
class Defrag {
    Defrag(FragEngine&);

    bool configure(snort::SnortConfig*);
    void process(snort::Packet*, FragTracker*);
    void cleanup(FragTracker*);

private:
    int insert(snort::Packet*, FragTracker*, FragEngine*);
    int add_frag_node(...);
    int dup_frag_node(...);
    int expired(snort::Packet*, FragTracker*, FragEngine*);
};
```

## 模块交互

```
packet_io
    │
    ▼
codecs (IP/TCP解码)
    │
    ▼
┌─────────────────────────────────────────┐
│           Stream Module                  │
│  ┌───────────┐  ┌──────────────────┐   │
│  │ IP Defrag │  │ TCP Stream Track │   │
│  └─────┬─────┘  └────────┬─────────┘   │
│        │                   │             │
│        ▼                   ▼             │
│  ┌───────────┐  ┌──────────────────┐   │
│  │ IP Session│  │  PAF + Splitter │   │
│  └───────────┘  └──────────────────┘   │
└─────────────────────────────────────────┘
    │
    ▼
detection (规则检测)
```

## TCP会话状态

```cpp
// Session Flags (ssn_flags)
#define SSNFLAG_SEEN_CLIENT         0x00000001  // 见过客户端
#define SSNFLAG_SEEN_SERVER         0x00000002  // 见过服务器
#define SSNFLAG_ESTABLISHED         0x00000004  // 连接已建立
#define SSNFLAG_MIDSTREAM           0x00000008  // 中途接入
#define SSNFLAG_ECN_CLIENT_QUERY    0x00000010  // ECN客户端查询
#define SSNFLAG_ECN_SERVER_REPLY    0x00000020  // ECN服务器回复
#define SSNFLAG_CLIENT_FIN          0x00000040  // 客户端FIN
#define SSNFLAG_SERVER_FIN          0x00000080  // 服务器FIN
#define SSNFLAG_DROP_CLIENT         0x00010000  // 丢弃客户端数据
#define SSNFLAG_DROP_SERVER         0x00020000  // 丢弃服务器数据

// Stream States
#define STREAM_STATE_NONE              0x0000
#define STREAM_STATE_ESTABLISHED       0x0001
#define STREAM_STATE_DROP_CLIENT       0x0002
#define STREAM_STATE_DROP_SERVER       0x0004
#define STREAM_STATE_MIDSTREAM         0x0008
#define STREAM_STATE_TIMEDOUT          0x0010
#define STREAM_STATE_CLOSED            0x0040
```

## PAF 协议感知Flush

PAF通过分析协议边界来确定刷新点,避免跨PDU切割数据:

```cpp
// PAF扫描状态机
paf_check():
    ├── SEARCH: 扫描查找协议边界
    ├── FLUSH:  在指定偏移刷新
    ├── LIMIT:  达到最大缓存限制刷新
    └── STOP:   停止扫描

// PAF标志
struct PAF_State {
    uint32_t seq;   // 流序列号光标
    uint32_t pos;   // 最后刷新位置
    uint32_t fpt;   // 当前刷新点
    uint32_t tot;   // 总刷新字节
    Status   paf;   // 扫描状态
};
```

## 统计指标

```cpp
const PegInfo base_pegs[] = {
    { CountType::SUM, "flows", "total sessions" },
    { CountType::SUM, "total_prunes", "total sessions pruned" },
    { CountType::SUM, "excess_prunes", "sessions pruned due to excess" },
    { CountType::NOW, "current_flows", "current number of flows in cache" },
    { CountType::SUM, "tcp_timeout_prunes", "TCP flows pruned due to timeout" },
    { CountType::SUM, "tcp_memcap_prunes", "TCP flows pruned due to memcap" },
    // ...
};
```
