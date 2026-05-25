# Snort3 快速过滤模块 (filters/)

快速过滤模块负责在检测前/后对流量进行过滤,包括基于端口/服务的规则组过滤、速率限制和事件阈值控制。

## 文件清单与行数统计

| 文件 | 行数 | 功能描述 |
|------|------|----------|
| detection_filter.cc/h | ~200 | **检测过滤器** - 基于事件速率 |
| rate_filter.cc/h | ~400 | **速率过滤器** - 动态规则动作 |
| sfthreshold.cc/h | ~300 | **阈值过滤** - 事件计数限制 |
| sfrf.cc/h | ~200 | **SF_RATE_FILTER** - 速率追踪 |
| sfthd.cc/h | ~300 | **SF_THRESHOLD** - 阈值管理 |
| sfthreshold.h | 51 | 阈值配置接口 |
| rate_filter.h | 43 | 速率过滤接口 |

**总计**: 约 1,700+ 行代码

---

## 类层次结构

```cpp
// 速率过滤
RateFilterConfig (rate_filter.h)
├── tSFRFConfigNode* config
├── SF_RF_DATA* rate_data
└── 速率过滤规则链表

tSFRFConfigNode (sfrf.h)
├── uint8_t tracking;        // src_ip / dst_ip
├── uint8_t count;           // 计数阈值
├── uint8_t seconds;         // 时间窗口(秒)
├── uint8_t new_action;      // 新的动作
├── uint32_t timeout;        // 超时(秒)
└── tSFRFConfigNode* next

// 阈值过滤
ThresholdConfig (sfthreshold.h)
├── ThresholdObjects* thd_objs
├── unsigned memcap
└── int enabled

ThresholdObjects (sfthd.h)
├── thd_obj* local_thd_obj
├── thd_obj* global_thd_obj
└── gen_hash* gen_thash

// 检测过滤
DetectionFilterConfig (detection_filter.cc)
├── uint8_t track;           // src/dst/both
├── uint8_t count
├── uint16_t seconds
└── uint8_t new_action
```

---

## 核心过滤器

### 1. 速率过滤器 (Rate Filter)

动态修改规则动作,基于流量速率。

```cpp
// rate_filter.h:35-42
RateFilterConfig* RateFilter_ConfigNew();
void RateFilter_ConfigFree(RateFilterConfig*);
void RateFilter_Cleanup();
int RateFilter_Create(snort::SnortConfig*, RateFilterConfig*, tSFRFConfigNode*);
int RateFilter_Test(const OptTreeNode*, snort::Packet*);
```

**配置结构**:
```cpp
// sfrf.h
struct tSFRFConfigNode {
    uint8_t tracking;     // TRACK_BY_SRC | TRACK_BY_DST
    uint8_t count;       // 事件数阈值
    uint8_t seconds;     // 时间窗口(秒)
    uint8_t new_action;  // 应用于匹配流的新动作
    uint32_t timeout;    // 抑制超时(秒)

    tSFRFConfigNode* next;
};

// sfrf.cc:60-70
struct SF_RF_DATA {
    SFIPRec* ip;                // 追踪的IP
    uint8_t rate_count;         // 当前计数
    uint8_t rate_last_time;     // 上次时间戳
    uint8_t new_action;         // 新动作
    uint32_t timeout;           // 超时值
    uint32_t gen_id;            // 规则GID
    uint32_t sig_id;            // 规则SID
    uint32_t tracking;          // 追踪类型
};
```

**规则示例**:
```
alert tcp any any -> any 80 (msg:"DoS";
  content:"GET"; rate_filter: track src_ip, count 100, seconds 10, new_action drop, timeout 60;)
```

### 2. 阈值过滤 (Threshold)

限制事件生成速率,防止告警风暴。

```cpp
// sfthreshold.h:40-47
ThresholdConfig* ThresholdConfigNew();
void ThresholdConfigFree(ThresholdConfig*);
int sfthreshold_create(snort::SnortConfig*, ThresholdConfig*, THDX_STRUCT*, PolicyId);
int sfthreshold_test(unsigned gid, unsigned sid,
    const snort::SfIp*, const snort::SfIp*, long curtime, PolicyId);
```

**阈值类型** (sfthd.h):
```cpp
enum THD_TYPE {
    THD_TYPE_LIMIT,     // 固定时间窗口内限制事件数
    THD_TYPE_THRESHOLD, // 超过阈值才告警
    THD_TYPE_BOTH,      // 限制+阈值组合
    THD_TYPE_DETECT     // 检测模式
};

enum THD_TRACK {
    THD_TRACK_BY_SRC,   // 按源IP追踪
    THD_TRACK_BY_DST,   // 按目标IP追踪
    THD_TRACK_BY_BOTH   // 双向追踪
};
```

**规则示例**:
```
# 类型1: limit - 每60秒最多1次告警
alert tcp any any -> any 22 (msg:"SSH Brute Force";
  content:"Failed"; threshold: type limit, track by_src, count 5, seconds 60;)

# 类型2: threshold - 每事件都检查阈值
alert tcp any any -> any 23 (msg:"Login Success";
  threshold: type threshold, track by_dst, count 1, seconds 0;)

# 类型3: both - 超过阈值后限制速率
alert icmp any any -> any any (msg:"PING";
  threshold: type both, track by_src, count 5, seconds 60;)
```

### 3. 检测过滤器 (Detection Filter)

基于检测速率的过滤,在检测引擎内部实现。

```cpp
// detection_filter.cc
// 嵌入式检测率过滤,与规则关联
// 在选项树评估后执行
```

---

## 快速过滤机制 (规则组预过滤)

### Port/Service过滤

规则加载时按端口和服务分组,检测时快速跳过不匹配的规则组。

```cpp
// detection/ports/port_group.h
struct PortObject {
    PortFunc* func;           // 检查函数
    sfip_var_t* ip_list;      // IP列表
    void* data;                // 规则组数据
    int proto;                 // 协议
};

struct PortGroup {
    PortObject* src_port;
    PortObject* dst_port;
    RuleTreeNode* rtn;         // 匹配的RTN
};
```

### Protocol过滤

```cpp
// detection/fp_detect.h:101
void fp_eval_service_group(snort::Packet*, SnortProtocolId);
// 根据SnortProtocolId选择规则组
```

### gen_id/sid过滤

```cpp
// signature.h:85-89
struct OtnKey {
    uint32_t gid;    // Generator ID
    uint32_t sid;    // Signature ID
};

// 规则状态查询
// detection/signature.cc
OptTreeNode* OtnLookup(snort::GHash*, uint32_t gid, uint32_t sid);
```

---

## 过滤流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    规则加载阶段                                  │
├─────────────────────────────────────────────────────────────────┤
│ 1. fpCreateFastPacketDetection()                                │
│    └─► 按端口/服务/IP分组规则                                    │
│    └─► 编译快速模式规则组                                        │
│    └─► 初始化阈值/速率过滤器                                      │
│        ├─► ThresholdConfig                                      │
│        └─► RateFilterConfig                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    数据包检测阶段                                │
├─────────────────────────────────────────────────────────────────┤
│ 2. DetectionEngine::detect()                                     │
│    └─► fp_full(packet)                                          │
│        ├─► 1. PortGroup Lookup    // 快速端口匹配                │
│        ├─► 2. Service Lookup     // 服务识别                    │
│        ├─► 3. MpseBatch Search   // 模式匹配                    │
│        │                                                    │
│        │  // 匹配后处理                                       │
│        ├─► 4. RateFilter_Test()   // 速率过滤                  │
│        │    └─► 通过则应用新动作                              │
│        ├─► 5. detection_option_tree_evaluate()  // 选项树     │
│        │                                                    │
│        │  // 事件生成                                         │
│        ├─► 6. sfthreshold_test()  // 阈值检查                 │
│        │    └─► 通过则进入事件队列                             │
│        └─► 7. queue_event()        // 事件入队                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    事件输出阶段                                  │
├─────────────────────────────────────────────────────────────────┤
│ 3. CallAlertFuncs() / CallLogFuncs()                            │
│    └─► 输出事件到日志系统                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 阈值/速率数据结构

### ThresholdObject (sfthd.h)

```cpp
// sfthd.h:140-160
struct thd_obj {
    THD_ENTRY* thd;           // 阈值条目数组
    unsigned int thd_count;    // 条目数
    unsigned int mem_usage;    // 内存使用
};

struct thd_entry {
    struct in6_addr ip;        // 源/目标IP
    uint64_t check_ts;        // 上次检查时间
    uint32_t gid;             // Generator ID
    uint32_t sid;             // Signature ID
    uint8_t tracking;         // 追踪类型
    int32_t seconds;          // 时间窗口
    uint8_t count;            // 当前计数
    uint8_t new_count;        // 新计数
    uint8_t expires;          // 过期标志
};
```

### RateFilterData (sfrf.h)

```cpp
// sfrf.h:80-95
struct _SF_RF_DATA {
    SFIPRec* ip;
    uint8_t rate_count;
    uint8_t rate_last_time;
    uint8_t new_action;
    uint32_t timeout;
    uint32_t gen_id;
    uint32_t sig_id;
    uint32_t tracking;
    _SF_RF_DATA* next;
};
```

---

## 模块交互

```
┌─────────────────────────────────────────────────────────────────┐
│                     DetectionEngine                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  fp_full(packet)                                         │   │
│  │  ├─► PortGroup Lookup  (ports/)                         │   │
│  │  ├─► Mpse::search()     (search_engines/)               │   │
│  │  ├─► RateFilter_Test()   (filters/rate_filter)          │   │
│  │  ├─► detection_option_tree_evaluate() (detection/)     │   │
│  │  └─► sfthreshold_test()  (filters/sfthreshold)          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ rate_filter   │     │ sfthreshold   │     │ detection_filter│
│ 动态规则动作   │     │ 事件率限制     │     │ 检测率过滤     │
└───────────────┘     └───────────────┘     └───────────────┘
```

---

## 配置接口

### 规则配置

```
# 阈值配置 (snort.conf)
# rate_filter config memcap <bytes>
# threshold config gen_id <gid>, sig_id <sid>, type <type>, track <by_src|by_dst>, count <n>, seconds <n>

# 检测过滤配置
# detection_filter config memcap <bytes>
```

### 规则选项

```
rate_filter: track <by_src|by_dst>, count <n>, seconds <n>, new_action <alert|drop|...>, timeout <n>
threshold: type <limit|threshold|both>, track <by_src|by_dst>, count <n>, seconds <n>
```
