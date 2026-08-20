---
title: "Snort3 Detection Framework Core (detection/)"
description: "检测框架核心模块，负责规则引擎和事件链的完整生命周期管理。"
---
# Snort3 Detection Framework Core (detection/)

检测框架核心模块，负责规则引擎和事件链的完整生命周期管理。

## 文件清单与行数统计

| 文件 | 行数 | 功能描述 |
|------|------|----------|
| detect.h | 50 | 主检测循环钩子函数声明 |
| detect.cc | ~300 | 告警/日志回调执行 |
| detection_engine.h | 173 | 检测引擎主类声明 |
| detection_engine.cc | ~500 | 检测引擎实现 |
| fp_detect.h | 104 | 快速模式匹配入口 |
| fp_detect.cc | ~400 | 快速模式检测逻辑 |
| fp_create.h | 61 | 规则组编译接口 |
| fp_create.cc | ~600 | Fast Packet检测引擎创建 |
| fp_config.h/cc | ~200 | 快速模式配置 |
| fp_utils.h/cc | ~200 | 快速模式工具函数 |
| ips_context.h | 192 | 检测上下文(单包状态) |
| ips_context.cc | ~300 | 上下文生命周期管理 |
| ips_context_chain.h/cc | ~150 | 上下文链表管理 |
| ips_context_data.h/cc | ~100 | 上下文数据存储 |
| signature.h | 128 | 签名元数据(GID/SID/分类) |
| signature.cc | ~400 | 签名管理实现 |
| treenodes.h | 293 | RTN/OTN规则树节点 |
| treenodes.cc | ~400 | 规则树节点操作 |
| rules.h | 104 | 规则列表结构 |
| rules.cc | ~300 | 规则解析和管理 |
| detection_options.h | 231 | 选项树处理(公共检测选项优化) |
| detection_options.cc | ~500 | 选项树求值 |
| event_trace.h | 42 | 事件追踪接口 |
| event_trace.cc | ~200 | 事件追踪实现 |
| detection_module.h/cc | ~300 | 检测配置模块 |
| context_switcher.h/cc | ~100 | 检测上下文切换 |
| detection_buf.h | ~100 | 检测缓冲区管理 |
| pattern_match_data.h | ~50 | 模式匹配数据结构 |
| pcrm.h/cc | ~200 | PCRE正则模块 |
| regex_offload.h/cc | ~150 | 正则表达式卸载 |
| rtn_checks.h/cc | ~200 | RTN检查函数 |
| service_map.h/cc | ~100 | 服务映射 |
| sfrim.h/cc | ~100 | 规则匹配接口 |
| tag.h/cc | ~150 | 标签系统 |
| extract.h/cc | ~200 | 数据提取 |
| detect_trace.h/cc | ~150 | 检测追踪 |

**总计**: 约 7,000+ 行代码

---

## 核心类层次结构

```
IpsContext (检测上下文 - 单包状态容器)
├── Packet* packet
├── MpseBatch searches
├── IpsContextData*[max_ips_id]
├── FlowSnapshot flow
├── std::vector<MatchedBuffer> matched_buffers
└── Callback链表

DetectionEngine (检测引擎 - 单例模式)
├── IpsContext* context
├── static bool detect(Packet*, bool offload_ok)
├── static bool inspect(Packet*)
├── static IpsContext* get_context()
└── set_next_packet()/get_next_buffer()

OptTreeNode (规则体 - 每条规则一个)
├── SigInfo sigInfo
├── OptFpList* opt_func (选项函数链表)
├── RuleTreeNode** proto_nodes (按策略索引)
├── OtnState* state
└── detection_option_tree_root_t* option_tree

RuleTreeNode (规则头 - 头部匹配)
├── RuleFpList* rule_func
├── RuleHeader* header
├── sfip_var_t* sip/dip
├── PortObject* src/dst_portobject
└── SnortProtocolId

detection_option_tree_node_t (选项树节点)
├── eval_func_t evaluate
├── detection_option_tree_bud_t children[]
├── dot_node_state_t* state (每线程)
└── option_type_t type

OtnxMatchData (模式匹配结果)
├── MatchInfo* matchInfo
└── bool have_match
```

---

## 核心函数

### 检测入口

```cpp
// detection_engine.h:91
static bool detect(Packet*, bool offload_ok = false);
static bool inspect(Packet*);

// detection_engine.h:54-60
static IpsContext* get_context();
static Packet* set_next_packet(const Packet* parent = nullptr, Flow* flow = nullptr);
static uint8_t* get_next_buffer(unsigned& max);
```

### 快速模式检测

```cpp
// fp_detect.h:98-102
void fp_full(snort::Packet*);
void fp_partial(snort::Packet*);
void fp_complete(snort::Packet*, bool search = false);
void fp_eval_service_group(snort::Packet*, SnortProtocolId);
```

### 事件队列

```cpp
// detection_engine.h:94-95
static int queue_event(const OptTreeNode*);
static int queue_event(unsigned gid, unsigned sid);
```

### 规则组创建

```cpp
// fp_create.h:56-58
int fpCreateFastPacketDetection(snort::SnortConfig*);
void fpDeleteFastPacketDetection(snort::SnortConfig*);
void get_pattern_info(const PatternMatchData* pmd, ...);
```

---

## 代码片段

### 检测上下文设置

```cpp
// ips_context.h:58-71
class IpsContext {
public:
    using Callback = void(*)(IpsContext*);
    enum State { IDLE, BUSY, SUSPENDED };

    void setup();
    void clear();

    void set_context_data(unsigned id, IpsContextData*);
    IpsContextData* get_context_data(unsigned id) const;

    void snapshot_flow(Flow*);

    // 上下文链表 - 支持依赖链
    void link(IpsContext* next) {
        next->depends_on = this;
        next_to_process = next;
    }
};
```

### 检测引擎主循环

```cpp
// detection_engine.cc (伪代码)
bool DetectionEngine::detect(Packet* p, bool offload_ok) {
    IpsContext* ctx = get_context();
    ctx->packet = p;

    // 1. 预处理 - set_file_data
    set_file_data(get_file_data(ctx));

    // 2. 快速模式匹配
    fp_full(p);   // 完整检测
    // 或 fp_partial(p) // 部分检测

    // 3. 规则选项树求值
    for ( each matched_rule ) {
        detection_option_node_evaluate(option_tree, ...);
    }

    // 4. 事件入队
    queue_event(gid, sid);

    // 5. 后检测回调
    ctx->post_detection();

    return true;
}
```

### 选项树求值

```cpp
// detection_options.h:220-221
int detection_option_node_evaluate(
    const detection_option_tree_node_t*,
    detection_option_eval_data_t&,
    const class Cursor&);

// 优化：公共检测选项只求值一次
// tree节点共享机制 - 相同选项共享子树
```

---

## 模块交互

```
┌─────────────────────────────────────────────────────────────────┐
│                        Packet Ingress                           │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DetectionEngine::detect()                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. IpsContext::setup() - 初始化上下文                     │   │
│  │ 2. set_file_data() - 设置检测缓冲区                       │   │
│  │ 3. fp_full/partial() - 快速模式匹配                       │   │
│  │    └─► MpseBatch::search()                               │   │
│  │         └─► AcBnfa/Hyperscan search_engines              │   │
│  │ 4. detection_option_tree_evaluate() - 选项树求值          │   │
│  │    └─► ips_options (content/pcre/flow/...)               │   │
│  │ 5. queue_event() - 事件入队                               │   │
│  │ 6. post_detection() callbacks                            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   filters/      │    │  ips_options/   │    │ search_engines/ │
│ rate_filter    │    │  content        │    │ ac_bnfa         │
│ sfthreshold    │    │  pcre           │    │ hyperscan       │
│ detection_filter│    │  byte_test      │    │ acsmx2          │
└─────────────────┘    │  byte_jump      │    └─────────────────┘
                       │  flow          │
                       │  flags         │
                       │  dsize         │
                       │  ...           │
                       └─────────────────┘
```

### 与其他模块交互

| 交互模块 | 接口 | 描述 |
|----------|------|------|
| search_engines/ | Mpse::search() | 快速模式匹配 |
| ips_options/ | IpsOption::eval() | 选项求值 |
| filters/ | RateFilter_Test, sfthreshold_test | 阈值过滤 |
| framework/ | IpsAction | 事件动作 |
| events/ | SF_EVENTQ | 事件队列 |
| profiler/ | ProfileStats | 性能分析 |

---

## 检测流程时序

```
1.规则加载阶段
   fpCreateFastPacketDetection()
   └─► 编译规则组, 构建MPSE

2.数据包检测阶段
   DetectionEngine::detect(p)
   ├─► set_next_packet()        // 设置包上下文
   ├─► set_file_data()         // 设置检测缓冲
   ├─► fp_full(p)              // 快速模式匹配
   │   ├─► MpseBatch search    // MPSE批量搜索
   │   └─► fp_eval_option()    // 匹配后选项树求值
   ├─► detection_option_node_evaluate()  // 完整选项树求值
   ├─► queue_event()           // 事件入队
   └─► post_detection()         // 后检测回调

3.事件生成阶段
   CallAlertFuncs() / CallLogFuncs()
   └─► otn_trigger_actions()    // 触发签名动作
```

---

## 关键数据结构

### MatchInfo (fp_detect.h:71-77)

```cpp
struct MatchInfo {
    const OptTreeNode* MatchArray[MAX_EVENT_MATCH];  // 匹配事件数组
    unsigned iMatchCount;    // 匹配计数
    unsigned iMatchIndex;    // 最高优先级事件索引
    unsigned iMatchMaxLen;   // 最大模式长度
};
```

### detection_option_tree_node_t (detection_options.h:145-167)

```cpp
struct detection_option_tree_node_t : public detection_option_tree_bud_t {
    eval_func_t evaluate;       // 求值函数
    void* option_data;          // 选项数据
    dot_node_state_t* state;   // 每线程状态
    int is_relative;            // 是否相对偏移
    option_type_t option_type;  // 选项类型
};
```

### IpsContext状态机

```
IDLE ──► BUSY ──► SUSPENDED
  │         │           │
  │         │           └──► 等待offload完成
  │         │
  │         └──► 检测中
  │
  └──► 初始化/空闲状态
```
