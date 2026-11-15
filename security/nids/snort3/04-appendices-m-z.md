---
title: "Snort 3 · 附录 M–Z"
description: "附录M：正则表达式卸载 — 附录Z：核心流程时序图"
---

# Snort 3 · 附录 M–Z

[返回总目录](../snort3_architecture_analysis)

## 附录M：正则表达式卸载 {#附录m-正则表达式卸载}

### M.1 Hyperscan搜索引擎 {#m-1-hyperscan搜索引擎}

Intel Hyperscan是高性能正则表达式引擎：

```cpp
// search_engines/hyperscan.cc

class Hyperscan : public Mpse {
public:
    Hyperscan();
    ~Hyperscan() override;
    
    // 添加模式
    int add_pattern(const uint8_t* pat, unsigned len,
                   const PatternDescriptor&, void* user) override;
    
    // 编译模式
    int prep_patterns(SnortConfig*) override;
    
    // 搜索
    int search(const uint8_t* T, int n, MpseMatch,
               void* context, int* current_state) override;
};
```

### M.2 正则请求处理 {#m-2-正则请求处理}

```cpp
// detection/regex_offload.h

class RegexRequest {
public:
    // 正则编译
    int compile(const char* pattern, int options);
    
    // 执行匹配
    int match(const uint8_t* text, unsigned len);
    
    // 释放资源
    void free();
};
```

---

## 附录N：文件处理和MIME {#附录n-文件处理和mime}

### N.1 文件处理流程 {#n-1-文件处理流程}

```
数据包
    │
    ├── 文件识别 (file_id inspector)
    │   │
    │   ├── 基于扩展名识别
    │   ├── 基于MIME类型识别
    │   └── 基于文件头magic字节识别
    │
    ├── 文件分段 (file_process)
    │   │
    │   ├── 分段传输处理
    │   └── 累积文件数据
    │
    ├── 文件重组 (file_reassemble)
    │   │
    │   └── 重组分段的文件
    │
    └── 文件检测 (file_inspect)
        │
        ├── 文件签名匹配 (SHA256, MD5)
        ├── 文件类型检测
        └── 敏感数据过滤 (SDF)
```

### N.2 Mime处理 {#n-2-mime处理}

```cpp
// mime/目录

class MimeDecoder {
public:
    // Base64解码
    int decode_base64(const uint8_t* in, unsigned len,
                     uint8_t* out, unsigned* out_len);
    
    // Quoted-Printable解码
    int decode_qp(const uint8_t* in, unsigned len,
                  uint8_t* out, unsigned* out_len);
    
    // UU编码解码
    int decode_uu(const uint8_t* in, unsigned len,
                  uint8_t* out, unsigned* out_len);
};
```

---

## 附录O：主循环和处理流程 {#附录o-主循环和处理流程}

### O.1 Snort主函数流程 {#o-1-snort主函数流程}

```cpp
// main.cc

int main(int argc, char* argv[]) {
    // 1. 初始化
    Snort::setup(argc, argv);
    
    // 2. 创建Analyzer线程
    for each packet thread:
        Pig::prep(source);  // 准备
        Pig::start();       // 启动
        
    // 3. 等待线程完成
    while (!exit_requested) {
        // 处理命令
        // 统计输出
        sleep(1);
    }
    
    // 4. 清理
    Snort::cleanup();
}
```

### O.2 Analyzer处理循环 {#o-2-analyzer处理循环}

```cpp
// main/analyzer.cc

void Analyzer::analyze() {
    while (!exit_requested) {
        // 获取数据包
        DAQ_RecvStatus status = instance->acquire(&msg, timeout);
        
        if (status == DAQ_SUCCESS) {
            // 处理消息
            process_daq_msg(msg, false);
            
            // 完成处理
            finalize_daq_message(msg, verdict);
        }
        else if (status == DAQ_RETRY) {
            // 重试队列处理
            process_retry_queue();
        }
        else {
            // 空闲处理
            idle();
        }
    }
}
```

### O.3 包处理流程 {#o-3-包处理流程}

```cpp
// main/analyzer.cc

void Analyzer::process_daq_pkt_msg(DAQ_Msg_h msg, bool retry) {
    // 1. 获取数据包
    Packet* p = new Packet();
    p->pkth = daq_msg.pkth;
    p->pkt = daq_msg.data;
    p->pktlen = daq_msg.len;
    
    // 2. 协议解码
    PacketManager::decode(p);
    
    // 3. 检查器处理
    InspectorManager::execute(p);
    
    // 4. 检测
    DetectionEngine::detect(p);
    
    // 5. 后处理
    post_process_packet(p);
}
```

---

## 附录P：内存管理和对象池 {#附录p-内存管理和对象池}

### P.1 内存分配接口 {#p-1-内存分配接口}

```cpp
// memory/memory_cap.h

class MemoryCap {
public:
    // 分配内存
    static void* allocate(size_t);
    
    // 释放内存
    static void deallocate(void*);
    
    // 获取统计
    static uint64_t get_allocated();
    static uint64_t get_in_use();
    
    // 设置限制
    static void set_limit(uint64_t);
};
```

### P.2 Flow缓存 {#p-2-flow缓存}

```cpp
// flow/flow_cache.h

class FlowCache {
public:
    FlowCache(unsigned max_flows);
    ~FlowCache();
    
    // 获取Flow
    Flow* find(const FlowKey*);
    Flow* allocate();
    
    // 归还Flow
    void release(Flow*);
    
    // 统计
    uint64_t get_count() const;
    uint64_t get_max() const;
    
    // 修剪过期Flow
    void prune();
    
private:
    std::unordered_map<FlowKey*, Flow*> flows;
    std::list<Flow*> lru_list;  // LRU列表
    unsigned max_flows;
};
```

---

## 附录Q：多线程和线程本地存储 {#附录q-多线程和线程本地存储}

### Q.1 线程本地存储宏 {#q-1-线程本地存储宏}

```cpp
// main/thread.h

#define THREAD_LOCAL thread_local

// 使用示例：
THREAD_LOCAL ProfileStats contentPerfStats;
THREAD_LOCAL const snort::Trace* http_trace;
THREAD_LOCAL unsigned instance_id;
```

### Q.2 线程配置 {#q-2-线程配置}

```cpp
// main/thread_config.h

class ThreadConfig {
public:
    static unsigned get_instance_count();
    static unsigned get_instance_id();
    
    // CPU亲和性
    static void set_cpu_affinity(cpu_set_t*);
    static cpu_set_t* get_cpu_affinity();
};
```

### Q.3 上下文切换 {#q-3-上下文切换}

```cpp
// detection/context_switcher.h

class ContextSwitcher {
public:
    // 保存上下文
    static void save(snort::IpsContext*);
    
    // 恢复上下文
    static void restore(snort::IpsContext*);
    
    // 切换上下文
    static void switch_to(snort::IpsContext*);
};
```

---

## 附录R：HA高可用性 {#附录r-ha高可用性}

### R.1 高可用性状态 {#r-1-高可用性状态}

```cpp
// flow/ha.h

class FlowHAState {
public:
    // 序列化状态
    uint8_t* serialize(uint32_t& len);
    
    // 反序列化状态
    bool deserialize(const uint8_t*, uint32_t len);
    
    // 获取流键
    const FlowKey* get_key() const;
    
    // 获取时间戳
    uint64_t get_timestamp() const;
};
```

### R.2 HA模块 {#r-2-ha模块}

```cpp
// flow/ha_module.h

class HAModule : public snort::Module {
public:
    HAModule();
    ~HAModule() override;
    
    // 发送状态更新
    void send_update(Flow*, FlowHAState*);
    
    // 接收状态更新
    bool receive_update(Flow**, FlowHAState**);
};
```

---

## 附录S：追踪和调试 {#附录s-追踪和调试}

### S.1 追踪系统 {#s-1-追踪系统}

```cpp
// trace/trace_api.h

class Trace {
public:
    const char* module;
    unsigned level;
    const char* name;
};

class TraceApi {
public:
    // 获取追踪对象
    static const snort::Trace* get_trace(const char* module);
    
    // 设置追踪级别
    static void set_trace(const char* module, unsigned level);
};
```

### S.2 包追踪器 {#s-2-包追踪器}

```cpp
// packet_io/packet_tracer.h

class PacketTracer {
public:
    // 记录追踪信息
    void log(const char* fmt, ...);
    
    // 记录检查器
    void log_inspector(const char* name, bool result);
    
    // 记录规则匹配
    void log_rule_match(const OptTreeNode* otn);
    
    // 输出追踪
    void dump(FILE*);
};
```

---

## 附录T：时间处理 {#附录t-时间处理}

### T.1 时钟定义 {#t-1-时钟定义}

```cpp
// time/clock_defs.h

typedef uint64_t Timestamp;

// 时间比较
bool operator<(const Timestamp&, const Timestamp&);
bool operator>(const Timestamp&, const Timestamp&);

// 时间运算
Timestamp operator+(const Timestamp&, uint64_t ms);
Timestamp operator-(const Timestamp&, uint64_t ms);
```

### T.2 周期性任务 {#t-2-周期性任务}

```cpp
// time/periodic.h

class PeriodicCheck {
public:
    // 构造函数
    PeriodicCheck(uint64_t interval_ms, Callback func);
    
    // 检查是否应该执行
    bool check(const Timestamp& now);
    
    // 执行回调
    void execute();
};
```

---

## 附录U：搜索引擎比较 {#附录u-搜索引擎比较}

| 搜索引擎 | 特点 | 适用场景 |
|---------|------|---------|
| AC (ac_full) | AC自动机，全匹配 | 通用模式匹配 |
| AC-BNFA (ac_bnfa) | 非确定性AC自动机 | 内存受限环境 |
| ACSMX2 (acsmx2) | 多模式扩展 | 大量模式 |
| Hyperscan | Intel优化，支持复杂模式 | 高性能需求 |
| LowMem | 低内存模式 | 嵌入式系统 |

---

## 附录V：常见规则选项详解 {#附录v-常见规则选项详解}

### V.1 content选项 {#v-1-content选项}

```lua
-- 基础语法
content: "pattern";
content: "pattern", nocase;
content: "pattern", fast_pattern;

-- 带偏移/深度
content: "pattern", offset 10, depth 100;

-- 相对匹配
content: "pattern1"; content: "pattern2", relative;

-- 否定匹配
content: !"pattern";
```

### V.2 http_cookie选项 {#v-2-http-cookie选项}

```lua
-- 匹配HTTP Cookie头
http_cookie;

-- 否定匹配
http_cookie: "session_id",nocase;

-- 大小写不敏感
http_cookie: "user", nocase;
```

### V.3 pcre选项 {#v-3-pcre选项}

```lua
-- 基本PCRE
pcre: "/pattern/is";

-- 带标志
-- i: 大小写不敏感
-- s: 点号匹配换行
-- m: 多行模式

-- 带缓冲区选择
pcre: "/\/admin\/.*\.php$/R";
-- R = http_uri缓冲区
```

---

## 附录W：开发示例 {#附录w-开发示例}

### W.1 创建简单的Inspector {#w-1-创建简单的inspector}

```cpp
// my_inspector.cc

#include "framework/inspector.h"
#include "framework/module.h"

class MyInspector : public Inspector {
public:
    MyInspector() = default;
    ~MyInspector() override = default;
    
    // 配置
    bool configure(SnortConfig*) override { return true; }
    
    // 检查包
    void eval(Packet* p) override {
        if (p->is_tcp()) {
            // 检测逻辑
            if (detect_attack(p)) {
                DetectionEngine::queue_event(1, 1001);
            }
        }
    }
    
    bool detect_attack(Packet* p) {
        // 具体检测逻辑
        return false;
    }
};

// 模块
class MyModule : public Module {
public:
    MyModule() : Module("my_inspector", "My inspector") {
        // 参数定义
    }
    
    bool begin(const char*, int, SnortConfig*) override { return true; }
    bool set(const char*, Value&, SnortConfig*) override { return true; }
};

// API
static const InspectApi my_api = {
    {
        IPT_NETWORK,
        "my_inspector",
        (API_VERSION << 16),
    },
    // ... 其他字段
    (InspectNew*)ctor,
    (InspectDelFunc*)dtor,
};
```

---

## 文档总结 {#文档总结}

本文档全面分析了Snort 3的源码架构，包含以下主要内容：

### 核心概念 {#核心概念}
1. **系统架构**：分层设计，从DAQ到检测的完整数据流
2. **插件系统**：Inspector、Codec、Mpse、Logger等插件类型
3. **检测引擎**：从规则解析到模式匹配的全流程
4. **数据结构**：Packet、Flow、IpsContext、Cursor等核心结构

### 关键组件 {#关键组件}
1. **Analyzer**：数据包获取和处理循环
2. **Inspector**：核心检查器（网络、服务、流等）
3. **Codec**：协议编解码
4. **DetectionEngine**：规则匹配引擎
5. **Binder**：检查器绑定
6. **Wizard**：服务自动检测

### 高级特性 {#高级特性}
1. **流重组**：TCP/UDP流跟踪和重组
2. **快速模式匹配**：AC、Hyperscan等算法
3. **发布-订阅**：组件间松耦合通信
4. **多线程**：线程本地存储和上下文切换
5. **配置系统**：Lua配置和策略管理
6. **高可用性**：状态同步和故障恢复

### 文件位置 {#文件位置}
- 文档：`docs/snort3_architecture_analysis.md`
- 源码：`src/`目录
- 配置：`snort.lua`

---

## 附录X：检测引擎深度解析 {#附录x-检测引擎深度解析}

### X.1 DetectionEngine 完整检测流程 {#x-1-detectionengine-完整检测流程}

```cpp
// detection/detection_engine.cc

bool DetectionEngine::detect(Packet* p, bool offload_ok) {
    // 1. 获取检测上下文
    IpsContext* context = get_context();
    context->packet = p;
    
    // 2. 准备检测缓冲区
    context->buf = p->data;
    
    // 3. 清空事件队列
    context->equeue->clear();
    
    // 4. 初始化匹配信息
    init_match_info(context);
    
    // 5. 检查是否启用卸载
    if (offload_ok && offload_enabled) {
        if (do_offload(p))
            return false;  // 卸载异步执行
    }
    
    // 6. 执行快速模式匹配
    fp_full(p);
    
    // 7. 完成检测
    finish_inspect(p, true);
    
    return true;
}
```

### X.2 fp_full 快速模式检测 {#x-2-fp-full-快速模式检测}

```cpp
// detection/fp_detect.cc

void fp_full(Packet* p) {
    // 1. 获取包的协议位
    uint32_t proto_bits = p->proto_bits;
    
    // 2. 遍历所有规则类型
    for (i = 0; i < num_rule_types; i++) {
        // 3. 获取规则组
        MpseGroup* group = get_group(proto_bits, i);
        
        if (!group)
            continue;
            
        // 4. 检查是否有fast pattern匹配
        if (group->has_fp_match()) {
            // 5. 获取匹配的模式
            auto matches = group->get_fp_matches();
            
            // 6. 对每个匹配进行规则评估
            for (auto match : matches) {
                // 7. 评估规则选项
                fp_eval_option(match.otn, p);
            }
        }
    }
}
```

### X.3 fp_eval_option 规则选项评估 {#x-3-fp-eval-option-规则选项评估}

```cpp
// detection/fp_detect.cc

int fp_eval_option(void* void_otn, Cursor& c, Packet* p) {
    OptTreeNode* otn = (OptTreeNode*)void_otn;
    
    // 1. 获取RTN
    RuleTreeNode* rtn = get_rtn(otn);
    
    // 2. 检查协议匹配
    if (!rtn->proto_match(p))
        return 0;
    
    // 3. 获取选项节点
    OptTreeNode* curr_otn = otn;
    
    // 4. 遍历所有选项
    while (curr_otn) {
        IpsOption* opt = curr_otn->option;
        
        // 5. 评估选项
        EvalStatus status = opt->eval(c, p);
        
        if (status == NO_MATCH) {
            return 0;  // 规则不匹配
        }
        
        curr_otn = curr_otn->next;
    }
    
    // 6. 规则匹配，生成事件
    fpLogEvent(rtn, otn, p);
    
    return 1;
}
```

### X.4 事件过滤和速率限制 {#x-4-事件过滤和速率限制}

```cpp
// detection/fp_detect.cc - fpLogEvent 详解

int fpLogEvent(const RuleTreeNode* rtn, const OptTreeNode* otn, Packet* p) {
    int action, rateAction, filterEvent;
    
    // 1. 速率过滤测试
    rateAction = RateFilter_Test(otn, p);
    
    // 2. 获取最终动作
    action = (rateAction >= 0) ? rateAction : rtn->action;
    
    // 3. 事件过滤测试
    filterEvent = sfthreshold_test(
        otn->sigInfo.gid, otn->sigInfo.sid,
        p->ptrs.ip_api.get_src(), p->ptrs.ip_api.get_dst(),
        p->pkth->ts.tv_sec, policy_id);
    
    // 4. 检查是否需要记录
    if (filterEvent < 0) {
        IpsAction* act = get_ips_policy()->action[action];
        act->exec(p, ...);  // 执行动作（drop, reject等）
        return 1;
    }
    
    // 5. 记录事件
    CallAlertFuncs(p, otn, rtn);
    
    return 1;
}
```

### X.5 规则选项链表结构 {#x-5-规则选项链表结构}

```cpp
// detection/treenodes.h

struct OptTreeNode {
    // 签名信息
    SigInfo sigInfo;
    
    // 规则选项
    IpsOption* option;
    OptTreeNode* next;      // 下一个选项
    OptTreeNode* prev;      // 上一个选项
    
    // 规则类型
    int type;
    
    // 协议信息
    int protocol;
    
    // 否定标志
    bool negated;
    
    // 统计信息
    struct {
        uint64_t matches;
        uint64_t checks;
    } stats;
};
```

---

## 附录Y：规则编译详解 {#附录y-规则编译详解}

### Y.1 规则编译流程 {#y-1-规则编译流程}

```
规则文本
    │
    ▼
Parser::parse_rule()
    │
    ├── 解析规则头
    │   ├── action (alert, drop, pass, ...)
    │   ├── protocol (tcp, udp, icmp, ip)
    │   ├── src_ip, src_port
    │   └── dst_ip, dst_port
    │
    ├── 创建RuleTreeNode (RTN)
    │
    └── 解析规则选项
        │
        ├── 创建OptTreeNode (OTN)
        │
        ├── IpsOption::hash()
        │
        └── IpsOption::operator==()
        
    │
    ▼
SnortConfig::add_rule()
    │
    ├── 注册到otn_map
    │
    ├── 编译fast pattern
    │
    └── 注册到规则组
```

### Y.2 规则组结构 {#y-2-规则组结构}

```cpp
// detection/pcrm.h

class MpseGroup {
public:
    // 协议位掩码
    uint32_t proto_mask;
    
    // fast pattern规则列表
    std::vector<OptTreeNode*> fp_list;
    
    // 非fast pattern规则列表
    std::vector<OptTreeNode*> nfp_list;
    
    // MPSE搜索引擎
    Mpse* mpse;
    
    // 添加规则
    void add_rule(OptTreeNode* otn, bool is_fp);
    
    // 编译
    void compile();
};
```

### Y.3 快速模式提取 {#y-3-快速模式提取}

```cpp
// detection/fp_create.cc

void FastPatternConfig::extract_fp(OptTreeNode* otn) {
    // 1. 遍历选项
    for (OptTreeNode* curr = otn; curr; curr = curr->next) {
        IpsOption* opt = curr->option;
        
        // 2. 获取pattern
        PatternMatchData* pm = opt->get_pattern(protocol);
        
        if (!pm)
            continue;
            
        // 3. 检查是否可以作为fast pattern
        if (!pm->can_be_fp())
            continue;
            
        // 4. 设置fast pattern
        pm->set_fast_pattern();
        
        // 5. 添加到fast pattern列表
        fp_list.push_back(otn);
        
        return;
    }
}
```

---

## 附录Z：核心流程时序图 {#附录z-核心流程时序图}

### Z.1 完整数据包处理时序 {#z-1-完整数据包处理时序}

```
┌──────────┐     ┌──────────┐     ┌──────────────┐     ┌─────────────┐
│   DAQ   │     │ Analyzer │     │   Packet     │     │ Inspector   │
│         │     │          │     │   Manager    │     │  Manager    │
└────┬─────┘     └────┬─────┘     └──────┬───────┘     └──────┬──────┘
     │                │                │                   │
     │ acquire()     │                │                   │
     │──────────────>│                │                   │
     │                │                │                   │
     │                │ process()      │                   │
     │                │──────────────>│                   │
     │                │                │                   │
     │                │                │ decode()         │
     │                │                │──────────────────>│
     │                │                │                   │
     │                │                │    InspectorManager::
     │                │                │    execute()     │
     │                │                │──────────────────>│
     │                │                │                   │
     │                │                │      eval(Packet*)
     │                │                │                   │
     │                │                │                   │
     │                │                │      DetectionEngine::
     │                │                │      detect()
     │                │                │──────────────────>│
     │                │                │                   │
     │                │                │         fp_full()
     │                │                │                   │
     │                │                │    ┌────────────┴────────┐
     │                │                │    │  MPSE::search()      │
     │                │                │    │  AC/Hyperscan        │
     │                │                │    └────────────┬────────┘
     │                │                │                   │
     │                │                │      fp_eval_option()
     │                │                │                   │
     │                │                │      fpLogEvent()
     │                │                │                   │
     │                │<───────────────│                   │
     │                │                │                   │
     │ final(verdict)  │                │                   │
     │<───────────────│                │                   │
     │                │                │                   │
```

### Z.2 TCP流处理时序 {#z-2-tcp流处理时序}

```
┌────────┐     ┌──────────┐     ┌────────────┐     ┌──────────────┐
│ Packet │     │   TCP    │     │   Stream   │     │   Service   │
│        │     │ Session  │     │Reassembler │     │  Inspector   │
└───┬────┘     └────┬─────┘     └─────┬──────┘     └──────┬───────┘
    │                │                │                   │
    │ eval()         │                │                   │
    │───────────────>│                │                   │
    │                │                │                   │
    │  precheck()    │                │                   │
    │                │                │                   │
    │                │  process()     │                   │
    │                │───────────────>│                   │
    │                │                │                   │
    │                │  Segment处理   │                   │
    │                │                │                   │
    │                │  顺序检查      │                   │
    │                │  重叠处理      │                   │
    │                │                │                   │
    │                │  reassemble()  │                   │
    │                │────────────────>│                   │
    │                │                │                   │
    │                │  Flush PDU    │                   │
    │                │                │                   │
    │                │                │  Service Detection│
    │                │                │──────────────────>│
    │                │                │                   │
    │                │                │                   │
```

### Z.3 规则匹配时序 {#z-3-规则匹配时序}

```
┌────────────┐     ┌────────────┐     ┌────────────┐     ┌────────────┐
│  Packet   │     │Detection  │     │   MPSE     │     │   Rule    │
│           │     │  Engine   │     │           │     │   Tree    │
└─────┬─────┘     └─────┬─────┘     └─────┬─────┘     └─────┬─────┘
      │                  │                  │                  │
      │ detect()         │                  │                  │
      │────────────────>│                  │                  │
      │                  │                  │                  │
      │ fp_full()        │                  │                  │
      │──────────────────>│                  │                  │
      │                  │                  │                  │
      │ get_group()      │                  │                  │
      │─────────────────────────────────────>│                  │
      │                  │                  │                  │
      │ mpse->search()   │                  │                  │
      │─────────────────────────────────────>│                  │
      │                  │                  │                  │
      │  Match Callback  │                  │                  │
      │<─────────────────────────────────────│                  │
      │                  │                  │                  │
      │ fp_eval_option() │                  │                  │
      │─────────────────────────────────────>│                  │
      │                  │                  │                  │
      │  IpsOption::eval()                  │                  │
      │─────────────────────────────────────>│                  │
      │                  │                  │                  │
      │  MATCH/NO_MATCH │                  │                  │
      │<─────────────────────────────────────│                  │
      │                  │                  │                  │
      │ fpLogEvent()     │                  │                  │
      │                  │                  │                  │
```

---
