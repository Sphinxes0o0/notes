---
type: entity
tags: [snort, ids-ips, detection-engine, intrusion-detection, pattern-matching]
created: 2026-05-27
sources: [github-snort3-detection]
---

# Snort3 Detection Engine

## 定义

Snort3 的检测引擎是负责在网络流量中评估 IPS 规则的核心子系统。它管理检测上下文，通过快速模式匹配（fast pattern）选择候选规则组，然后对命中的规则进行完整的选项树评估，最终通过事件队列决定采取的动作（alert/drop/pass/log）。

## 关键子系统

### 1. DetectionEngine (`detection_engine.cc/h`)

**角色**：顶层协调器，管理检测上下文生命周期。

**关键类**：`snort::DetectionEngine`

| 方法 | 职责 |
|------|------|
| `inspect(Packet*)` | 主检测入口：probes inspectors → executes inspectors → calls `detect()` |
| `detect(Packet*, bool offload_ok)` | 启动快速模式评估，可能触发 offload |
| `set_next_packet(parent, flow)` | 为重建的 PDU 设置下一个检测上下文 |
| `queue_event(otn)` / `queue_event(gid, sid)` | 将事件加入事件队列 |
| `finish_inspect(Packet*, bool)` | 日志事件、应用延迟动作、清理上下文 |
| `offload(Packet*)` | 对大 PDU 启动正则 offload 异步处理 |
| `enable_content/disable_content(Packet*)` | 控制是否执行内容检测 |

**关键设计**：
- `IpsContext* context` — 每个包一个上下文，存储包数据、搜索状态、事件队列
- `offload_enabled` — 可选的 Hyperscan/AC 异步加速
- 与 `ContextSwitcher` 协作管理上下文链表（支持流重建的多 PDU 场景）

---

### 2. Fast Pattern Detection (`fp_detect.cc/h`)

**角色**：规则评估的第二阶段 — 快速模式匹配后的完整规则树评估。

**核心数据结构**：

```cpp
// 事件匹配信息（每种动作类型一组）
struct MatchInfo {
    const OptTreeNode* MatchArray[MAX_EVENT_MATCH];  // 最多100个
    unsigned iMatchCount;
    unsigned iMatchIndex;
    unsigned iMatchMaxLen;
};

// OtnxMatchData — 包含所有规则类型的匹配结果
struct OtnxMatchData {
    MatchInfo* matchInfo;  // 数组，大小 = num_rule_types (≤16)
    bool have_match;
};
```

**核心函数**：

| 函数 | 职责 |
|------|------|
| `fp_full(Packet*)` | 完整评估：partial search + complete search + non-fp rules |
| `fp_partial(Packet*)` | 快速模式搜索阶段，填充 stash |
| `fp_complete(Packet*, bool search)` | 处理 stash，完成检测，选择最终事件 |
| `fpEvalPacket(Packet*, FPTask)` | 根据协议类型选择规则组并评估 |
| `fpEvalHeaderSW(RuleGroup*, Packet*, ...)` | set-wise 评估：FP + non-FP |
| `fpFinalSelectEvent(OtnxMatchData*, Packet*)` | 从所有匹配中选择最高优先级事件 |
| `fpLogEvent(RTN*, OTN*, Packet*)` | 执行 rate filter、event filter、触发动作 |
| `fpAddMatch(OtnxMatchData*, OTN*)` | 将 OTN 添加到匹配队列 |
| `MpseStash::push/process()` | 批量收集 MPSE 匹配结果，支持去重 |

**评估流程**：
```
fpEvalPacket()
  ├── fpEvalHeaderSvc()     → 服务级规则组（基于 snort_protocol_id）
  ├── fpEvalHeaderTcp/Udp/Icmp/Ip()
  │     └── fpEvalHeaderSW(RuleGroup*, task=FP|NON_FP)
  │           ├── eval_fp()      → 快速模式搜索（MPSE batch）
  │           └── eval_nfp()     → 非快速模式规则（检测选项树直接评估）
  │                 └── detection_option_tree_evaluate()
  └── fpFinalSelectEvent()  → 排序 + 选取最终事件
```

**FPTask 枚举**：
```cpp
enum FPTask : uint8_t { FP = 1, NON_FP = 2 };
```

---

### 3. Detection Options Tree (`detection_options.cc/h`)

**角色**：管理每条规则的检测选项树（DAG），在快速模式命中后进行完整选项评估。

**核心数据结构**：

```cpp
// 节点状态（每包线程一个实例）
struct dot_node_state_t {
    int result;
    struct {
        struct timeval ts;
        uint64_t context_num;
        uint32_t rebuild_flag;
        uint16_t run_num;
        char result;
        char flowbit_failed;
    } last_check;
    void* conts;       // 连续信息
    uint64_t context_num;
    uint16_t run_num;
    hr_duration elapsed, elapsed_match, elapsed_no_match;
    uint64_t checks, disables;
    unsigned latency_timeouts, latency_suspends;
};

// 选项树节点
struct detection_option_tree_node_t : public detection_option_tree_bud_t {
    eval_func_t evaluate;      // 评估函数指针
    void* option_data;         // IpsOption 派生类实例
    dot_node_state_t* state;   // 每线程状态数组
    int is_relative;           // 是否相对偏移
    option_type_t option_type; // CONTENT/PCRE/FLOWBIT/LEAF等
};

// 选项树根节点
struct detection_option_tree_root_t : public detection_option_tree_bud_t {
    RuleLatencyState* latency_state;  // 每线程延迟状态
};
```

**节点类型**（`option_type_t`）：
- `RULE_OPTION_TYPE_LEAF_NODE` — 规则叶子（触发 fpAddMatch）
- `RULE_OPTION_TYPE_CONTENT` — content 匹配
- `RULE_OPTION_TYPE_PCRE` — PCRE 正则
- `RULE_OPTION_TYPE_FLOWBIT` — flowbits 设置/检查
- `RULE_OPTION_TYPE_OTHER` — 其他选项

**核心评估逻辑** `detection_option_node_evaluate()`：
1. **was_evaluated()** — 检查缓存，避免同一上下文重复评估
2. **match_rtn()** — 验证规则头部（IP/端口/协议匹配）
3. **match_node()** — 调用选项的 `evaluate()` 方法
4. **match_leaf()** — 叶子节点：执行 detection_filter → fpAddMatch
5. **match_flowbit()** — flowbit 专用处理
6. **子节点递归** — 按深度优先顺序评估所有子节点
7. **重试逻辑** — 对相对偏移选项支持在失败点重试

**哈希去重**：
- `DetectionOptionHash` — 单一选项去重（基于 `ips_option->hash()`）
- `DetectionOptionTreeHash` — 完整选项树去重（基于树结构哈希）
- 通过 `add_detection_option_tree()` 复用已有相同树

---

### 4. IpsContext (`ips_context.cc/h`)

**角色**：单个包的完整检测状态容器。

```cpp
class IpsContext {
    Packet* packet;           // 当前包
    Packet* wire_packet;      // 原始有线包
    DAQ_PktHdr_t* pkth;       // DAQ 包头
    uint8_t* buf;             // 包数据缓冲区 (Codec::PKT_MAX)

    const SnortConfig* conf;
    MpseBatch searches;       // MPSE 批量搜索状态
    MpseStash* stash;         // 匹配结果暂存
    OtnxMatchData* otnx;      // 规则匹配结果
    SF_EVENTQ* equeue;        // 事件队列

    DataPointer file_data;    // 文件数据
    DataBuffer alt_data;      // 替代缓冲区
    std::vector<Replacement> rpl;  // 替换操作
    std::vector<MatchedBuffer> matched_buffers;

    uint64_t context_num;     // 上下文序号（用于缓存验证）
    uint64_t packet_number;
    ActiveRules active_rules; // NONE / NON_CONTENT / CONTENT
    State state;              // IDLE / BUSY / SUSPENDED

    // 上下文链接（支持流重建）
    IpsContext* depends_on;
    IpsContext* next_to_process;
};
```

**上下文状态机**：
```
IDLE → BUSY (开始检测) → SUSPENDED (offload时) → IDLE (完成)
                      ↘ COMPLETED → 链接到 next_to_process
```

---

### 5. IPS Context Chain (`ips_context_chain.cc/h`)

**角色**：管理同一流上多个 IpsContext 的链表（重建场景）。

```cpp
class IpsContextChain : public std::list<IpsContext*> {
    // 链表头部是最新上下文，尾部是最早
    // 支持暂停/恢复链式处理
};
```

---

### 6. Port Rule Map / PCRM (`pcrm.cc/h`)

**角色**：基于端口的规则分组索引结构。

```cpp
struct PORT_RULE_MAP {
    int prmNumDstRules, prmNumSrcRules, prmNumGenericRules;
    RuleGroup* prmSrcPort[MAX_PORTS];   // 源端口索引
    RuleGroup* prmDstPort[MAX_PORTS];   // 目标端口索引
    RuleGroup* prmGeneric;               // any-any 规则组
};

// 查询接口
prmFindRuleGroupTcp(prm, dport, sport, &src, &dst, &gen);
prmFindRuleGroupUdp(prm, dport, sport, &src, &dst, &gen);
prmFindRuleGroupIp(prm, ip_proto, &ip_group, &gen);
prmFindRuleGroupIcmp(prm, type, &type_group, &gen);
```

---

### 7. Fast Pattern Config (`fp_config.cc/h`)

**角色**：快速模式配置参数。

```cpp
class FastPatternConfig {
    const MpseApi* search_api;           // 主搜索引擎（AC/Hyperscan等）
    const MpseApi* offload_search_api;   // offload 专用引擎
    unsigned max_queue_events = 5;       // 每规则类型最大事件数
    unsigned bleedover_port_limit = 1024;
    unsigned max_pattern_len;            // 模式截断长度
    unsigned queue_limit;                // MPSE stash 队列限制
    bool split_any_any;                  // any-any 规则是否独立分组
    bool dedup = true;                   // stash 去重
};
```

---

### 8. Rule Tree Nodes (`treenodes.cc/h`)

**RuleTreeNode (RTN)** — 规则头部，每规则每策略一个：
```cpp
struct RuleTreeNode {
    RuleFpList* rule_func;    // 头部检查函数链
    PortObject* src_portobject;
    PortObject* dst_portobject;
    SnortProtocolId snort_protocol_id;
    snort::IpsAction::Type action;
    uint8_t flags;            // ENABLED, ANY_SRC_PORT, ANY_DST_PORT, BIDIRECTIONAL...
};
```

**OptTreeNode (OTN)** — 规则体，每规则一个：
```cpp
struct OptTreeNode {
    SigInfo sigInfo;           // gid/sid/rev/message/classification
    OptFpList* opt_func;      // 选项函数链表
    OptFpList* normal_fp_only; // 普通快速模式选项
    OptFpList* offload_fp_only;
    THD_NODE* detection_filter; // 阈值/抑制过滤器
    TagData* tag;
    RuleTreeNode** proto_nodes; // 指向 RTN 的指针数组（按策略索引）
    OtnState* state;            // 每线程统计
    unsigned evalIndex;          // 规则类型评估顺序索引
    uint16_t longestPatternLen;
};
```

**OptFpList** — 规则选项链表节点：
```cpp
struct OptFpList {
    snort::IpsOption* ips_opt;       // 实际选项对象
    int (*OptTestFunc)(void*, Cursor&, Packet*);  // 旧式函数指针
    OptFpList* next;
    unsigned char isRelative;
    option_type_t type;
};
```

---

### 9. Fast Pattern Creation (`fp_create.cc/h`)

**角色**：规则编译时将 RTN/OTN 分配到端口规则组，创建 MPSE 实例。

**关键数据结构**：

```cpp
struct PMX {
    struct PatternMatchData* pmd;
    RULE_NODE rule_node;
};

struct NCListNode {  // negative content list
    PMX* pmx;
    NCListNode* next;
};
```

**核心函数**：
- `fpCreateFastPacketDetection(SnortConfig*)` — 构建所有规则组的 MPSE 索引
- `fpDeleteFastPacketDetection(SnortConfig*)` — 清理
- `get_pattern_info(PMD*, ...)` — 提取模式信息用于调试

---

### 10. Event Trace (`event_trace.cc/h`)

**角色**：检测事件的追踪日志。

```cpp
EventTrace_Log(p, otn, action);  // 记录事件到 PacketTracer
EventTrace_IsEnabled(conf);      // 检查是否启用
```

---

### 11. Detection Continuation (`detection_continuation.h`)

**角色**：支持检测暂停和恢复（当数据不完整时）。

```cpp
class Continuation {
    static void postpone<relative>(Cursor&, detection_option_tree_node_t&, eval_data&);
    static void recall(dot_node_state_t&, Packet*);
};
```

---

### 12. Detection Module (`detection_module.cc/h`)

**角色**：Snort 配置模块，定义 `detection` 配置命名空间。

**配置参数**：
| 参数 | 默认 | 说明 |
|------|------|------|
| `offload_limit` | 99999 | 触发 offload 的最小 PDU 大小 |
| `offload_threads` | 0 | 最大 offload 线程数 |
| `pcre_enable` | true | 启用 PCRE |
| `pcre_match_limit` | 1500 | PCRE 回溯限制 |
| `pcre_match_limit_recursion` | 1500 | PCRE 栈递归限制 |
| `enable_address_anomaly_checks` | false | 地址异常检查 |
| `max_continuations_per_flow` | 1024 | 每流最大继续数 |

---

### 13. Tag (`tag.cc/h`)

**角色**：`tag` 规则选项实现，在告警后记录后续流量。

```cpp
struct TagData {
    int tag_type;        // SESSION / HOST / HOST_SRC / HOST_DST
    int tag_metric;      // SECONDS / PACKETS / BYTES / UNLIMITED
    int tag_direction;   // 源或目标
    uint32_t tag_seconds, tag_packets, tag_bytes;
};

SetTags(Packet*, OptTreeNode*, eseq);  // 告警时设置标签
CheckTagList(Packet*, ...);             // 检查标签并触发日志
```

---

### 14. Regex Offload (`regex_offload.cc/h` + `sfrim.cc/h`)

**角色**：大 PDU 检测的异步 offload（Hyperscan 加速）。

```cpp
class RegexOffload {
    RegexOffload::put(Packet*);     // 提交 offload 任务
    RegexOffload::get(Packet*&);    // 获取完成结果
    RegexOffload::count();           // 待处理数量
    RegexOffload::available();       // 是否有空闲槽
    RegexOffload::stop();           // 停止 offload 线程
};
```

**启用条件**：`offload_limit < 99999` 且 `offload_threads > 0`

---

### 15. Service Map (`service_map.cc/h`)

**角色**：基于服务（SnortProtocolId）而非端口的规则分组索引。

```cpp
class ServiceMap {
    get_port_group(bool from_client, SnortProtocolId) → RuleGroup*;
};

sopgTable->get_port_group(from_client, snort_protocol_id);
```

---

### 16. Extract / Data Extraction (`extract.cc/h`)

**角色**：字节串提取工具，供 `byte_extract`/`string_extract` 规则选项使用。

```cpp
byte_extract(endianness, bytes_to_grab, ptr, start, end, &value);
string_extract(bytes_to_grab, base, ptr, start, end, &value);
extract_data(ByteData&, Cursor&, Packet*, &result_var);
```

---

## Rule Evaluation Pipeline（完整流程）

```
Packet 到达
    ↓
DetectionEngine::inspect(p)
    ├─ InspectorManager::probe_first(p)        // 预处理探针
    ├─ InspectorManager::execute(p)            // 执行所有 inspectors
    │     └─ 其中可能调用 DetectionEngine::disable_content() 等
    ├─ DetectionEngine::detect(p, offload_ok)  // 启动检测
    │     ├─ fp_full(p)                        // 完整检测
    │     │     ├─ fp_partial(p)               // 快速模式搜索
    │     │     │     └─ fpEvalPacket(FP)      // 遍历协议对应规则组
    │     │     │           ├─ fp_search()     // MPSE batch search
    │     │     │           └─ rule_tree_queue() // 收集匹配到 stash
    │     │     └─ fp_complete(p, true)
    │     │           ├─ stash->process()      // 处理所有 MPSE 匹配
    │     │           │     └─ rule_tree_match() // 触发选项树评估
    │     │           │           └─ detection_option_tree_evaluate()
    │     │           │                 ├─ was_evaluated() 缓存检查
    │     │           │                 ├─ match_rtn()     规则头检查
    │     │           │                 ├─ match_node()    选项评估
    │     │           │                 └─ match_leaf()    叶子：fpAddMatch()
    │     │           ├─ fpEvalPacket(NON_FP) // 非快速模式规则
    │     │           └─ fpFinalSelectEvent() // 选择最终事件
    │     └─ [可能 offload(Packet*) 挂起]
    └─ finish_inspect_with_latency(p)
          ├─ DetectionEngine::set_check_tags(p)
          ├─ check_tags(p)
          └─ InspectorManager::probe(p)
    ↓
DetectionEngine::finish_inspect(p, inspected)
    ├─ log_events(p)                          // 遍历事件队列，调用 fpLogEvent
    │     └─ fpLogEvent()
    │           ├─ RateFilter_Test()          // 速率过滤
    │           ├─ sfthreshold_test()          // 事件过滤/抑制
    │           ├─ otn->state.alerts++         // 统计
    │           ├─ IpsAction::exec()          // 执行动作（drop/pass/alert等）
    │           ├─ SetTags()                   // 设置标签
    │           └─ fpLogOther()               // 非规则动作（响应）
    ├─ apply_delayed_action()                  // 应用延迟的阻塞动作
    ├─ post_detection()                        // 调用注册的回调
    └─ clear_events()
```

## Detection Filter（阈值 + 抑制）

**Detection Filter**（`THD_NODE`）在 OTN 中定义，在叶子节点评估时执行：

```cpp
if ( otn->detection_filter )
    if ( detection_filter_test(otn->detection_filter, p) )
        return NO_MATCH;  // 阈值未达到，规则不匹配
```

**Event Filter / Suppression**（`sfthreshold`）在 `fpLogEvent()` 中执行：
```cpp
filterEvent = sfthreshold_test(gid, sid, src_ip, dst_ip, ts, policy_id);
if ( filterEvent < 0 || (filterEvent > 0 && !override) )
    return 1;  // 事件被抑制，仅执行 inline drop（如果有）
```

## Event Queue（事件队列）

每包事件队列 `SF_EVENTQ`，按规则类型（alert/drop/pass/log）分组，每组最多 `max_queue_events`（默认5）个事件。

**排序方式**：
- `SNORT_EVENTQ_PRIORITY` — 按 `sigInfo.priority` 升序（数字小优先）
- `SNORT_EVENTQ_CONTENT_LENGTH` — 按 `longestPatternLen` 降序（匹配内容长优先）

**`fpFinalSelectEvent()` 选取逻辑**：
1. 按规则类型顺序遍历（drop > alert > pass > log）
2. 同类型内按优先级/长度排序
3. 去重（同 OTN 多次匹配仅计一次）
4. 跳过已告警（同一流的 session alert 检查）
5. 调用 `queue_event(otn)` 加入全局事件队列

## 关键设计模式

### Set-wise Matching
不是逐条规则评估，而是按端口/协议分组后，先做快速模式批量匹配，再评估命中的规则组。减少无效规则评估。

### MPSE Batch Search
MPSE 支持批量搜索（`MpseBatch`），一个搜索调用返回多个规则的匹配结果，避免 N 次单独搜索。

### Stash & Dedup
`MpseStash` 收集 MPSE 匹配结果，支持流内去重（`dedup`），避免同一规则树重复评估。

### Context Chain
流重建时同一流有多个 IpsContext 通过 `depends_on`/`next_to_process` 链接，形成上下文链表。

### Detection Option Tree DAG
相同选项共享一个 `detection_option_tree_node_t`，通过哈希去重避免重复构建。

## 相关概念

- [[entities/linux/snort3/snort3-actions]] — 检测引擎执行动作（alert/drop/pass/log）
- [[entities/linux/snort3/snort3-ips-options]] — 检测选项树节点由检测引擎求值
- [[entities/linux/snort3/snort3-events-filters]] — 检测引擎通过事件队列输出结果
- [[entities/linux/snort3/snort3-flow]] — 检测上下文管理会话状态
- [[entities/linux/snort3/snort3-connectors]] — 数据导出动作通过 Connector 发送
- [[entities/linux/snort3/snort3-infrastructure]] — MemCapAllocator 等基础设施支持

## 来源详情

- [[github-snort3-detection]]
