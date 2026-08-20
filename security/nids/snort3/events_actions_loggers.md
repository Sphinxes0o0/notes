---
title: "Snort3 事件系统、动作与日志 (Events, Actions & Loggers)"
description: "Snort3的事件系统负责管理检测事件的分发,动作系统提供灵活的响应机制,日志系统则负责事件和数据的输出。"
---
# Snort3 事件系统、动作与日志 (Events, Actions & Loggers)

Snort3的事件系统负责管理检测事件的分发,动作系统提供灵活的响应机制,日志系统则负责事件和数据的输出。

## 1. 事件系统 (Events)

### 1.1 Event 类

`Event`类封装了检测事件的所有信息:

```cpp
class SO_PUBLIC Event
{
public:
    Event();
    Event(uint32_t sec, uint32_t usec, const SigInfo&, const char** buffers,
        const char* action);
    Event(uint32_t sec, uint32_t usec, const SigInfo&, const char** buffers,
        const char* action, uint32_t ref);

    static uint16_t get_curr_seq_num();
    static uint16_t get_next_seq_num();
    static uint32_t get_next_event_id();

    uint32_t get_seconds() const;
    void get_timestamp(uint32_t& sec, uint32_t& usec) const;

    uint32_t get_event_id() const;
    uint32_t get_event_reference() const;

    const char** get_buffers() const;
    const char* get_action() const;

    uint32_t get_gid() const;      // 生成器ID
    uint32_t get_sid() const;      // 签名ID
    uint32_t get_rev() const;       // 修订版本

    void get_sig_ids(uint32_t& gid, uint32_t& sid, uint32_t& rev) const;

    const char* get_msg() const;
    const char* get_class_type() const;

    uint32_t get_class_id() const;
    uint32_t get_priority() const;

    // 获取规则引用
    bool get_reference(unsigned idx, const char*& name,
        const char*& id, const char*& url) const;

    // 获取目标信息
    bool get_target(bool& src) const;

private:
    const SigInfo& sig_info;
    const char* action = nullptr;
    const char** buffs_to_dump = nullptr;

    uint32_t ts_sec = 0;
    uint32_t ts_usec = 0;

    uint32_t event_id = 0;
    uint32_t event_reference = 0;
};
```

### 1.2 事件队列配置

```cpp
struct EventQueueConfig
{
    unsigned max_events;       // 最大事件数
    unsigned log_events;      // 日志事件数
    int order;                // 排序方式
    int process_all_events;   // 处理所有事件
};

#define SNORT_EVENTQ_PRIORITY    1   // 按优先级排序
#define SNORT_EVENTQ_CONTENT_LEN 2   // 按内容长度排序
```

### 1.3 事件节点

```cpp
struct EventNode
{
    const struct OptTreeNode* otn;  // 选项树节点
    const struct RuleTreeNode* rtn;  // 规则树节点
};
```

## 2. 动作系统 (Actions)

### 2.1 IpsAction 基类

```cpp
class SO_PUBLIC IpsAction
{
public:
    using Type = uint8_t;

    enum IpsActionPriority : uint16_t
    {
        IAP_OTHER = 1,
        IAP_LOG = 10,
        IAP_ALERT = 20,
        IAP_REWRITE = 30,
        IAP_DROP = 40,
        IAP_BLOCK = 50,
        IAP_REJECT = 60,
        IAP_PASS = 70,
        IAP_MAX = IAP_PASS
    };

public:
    virtual ~IpsAction() = default;

    const char* get_name() const { return name; }
    ActiveAction* get_active_action() const { return active_action; }

    virtual void exec(Packet*, const ActInfo&) = 0;
    virtual bool drops_traffic() { return false; }

    static std::string get_string(Type);
    static Type get_type(const char*);
    static Type get_max_types();
    static bool is_valid_action(Type);

protected:
    IpsAction(const char* s, ActiveAction* a)
    {
        active_action = a;
        name = s;
    }

private:
    const char* name;
    ActiveAction* active_action;
};
```

### 2.2 动作类型

| 动作 | 优先级 | 描述 | 丢弃流量 |
|------|--------|------|----------|
| `pass` | 70 | 跳过检测 | 否 |
| `reject` | 60 | 拒绝连接 | 是 |
| `block` | 50 | 阻止会话 | 是 |
| `drop` | 40 | 丢弃数据包 | 是 |
| `rewrite` | 30 | 重写数据 | 否 |
| `alert` | 20 | 生成警报 | 否 |
| `log` | 10 | 记录日志 | 否 |

### 2.3 AlertAction 实现

```cpp
class AlertAction : public IpsAction
{
public:
    AlertAction() : IpsAction(action_name, nullptr) { }

    void exec(Packet*, const ActInfo&) override;
};

void AlertAction::exec(Packet* p, const ActInfo& ai)
{
    alert(p, ai);           // 调用日志系统记录事件
    ++alert_stats.alert;    // 更新统计
}

static THREAD_LOCAL struct AlertStats
{
    PegCount alert;
} alert_stats;
```

### 2.4 BlockAction 实现

```cpp
class BlockAction : public IpsAction
{
public:
    BlockAction() : IpsAction(action_name, nullptr) { }

    void exec(Packet*, const ActInfo&) override;
    bool drops_traffic() override { return true; }
};

void BlockAction::exec(Packet* p, const ActInfo& ai)
{
    p->active->block_session(p);    // 阻止会话
    p->active->set_drop_reason("ips");

    alert(p, ai);                   // 同时记录事件
    ++block_stats.block;
}
```

### 2.5 其他动作实现

| 文件 | 动作 | 特性 |
|------|------|------|
| `act_alert.cc` | alert | 生成警报 |
| `act_block.cc` | block | 阻止会话 |
| `act_drop.cc` | drop | 丢弃数据包 |
| `act_pass.cc` | pass | 跳过检测 |
| `act_log.cc` | log | 记录日志 |
| `act_reject.cc` | reject | 拒绝连接(含TCP RST) |
| `act_react.cc` | react | 拒绝+通知 |
| `act_replace.cc` | replace | 替换内容 |
| `act_file_id.cc` | file_id | 文件标识 |

## 3. 日志系统 (Loggers)

### 3.1 Logger 基类

```cpp
class SO_PUBLIC Logger
{
public:
    virtual ~Logger() = default;

    virtual void open() { }
    virtual void close() { }
    virtual void reset() { }
    virtual void reload() { }

    virtual void alert(Packet*, const char*, const Event&) { }
    virtual void log(Packet*, const char*, Event*) { }

    void set_api(const LogApi* p) { api = p; }
    const LogApi* get_api() { return api; }

private:
    const LogApi* api = nullptr;
};
```

### 3.2 日志标志

```cpp
#define OUTPUT_TYPE_FLAG__NONE  0x0
#define OUTPUT_TYPE_FLAG__ALERT 0x1
#define OUTPUT_TYPE_FLAG__LOG   0x2
```

### 3.3 AlertFast 实现

快速警报日志格式:

```cpp
static THREAD_LOCAL TextLog* fast_log = nullptr;

#define S_NAME "alert_fast"
#define F_NAME S_NAME ".txt"

enum BuffersToOutput
{
    BUFFERS_NONE = 0,
    BUFFERS_RULE,         // 规则缓冲区
    BUFFERS_INSPECTOR,    // 检查器缓冲区
    BUFFERS_BOTH,         // 两者
};
```

### 3.4 AlertJson 实现

JSON格式警报:

```cpp
static void print_label(const Args& a, const char* label)
{
    if ( a.comma )
        TextLog_Print(json_log, ",");

    TextLog_Print(json_log, " \"%s\" : ", label);
}

static bool ff_action(const Args& a)
{
    print_label(a, "action");
    TextLog_Quote(json_log, a.pkt->active->get_action_string());
    return true;
}

static bool ff_app_id(const Args& a)
{
    if ( a.pkt->flow )
    {
        const char* app_name = appid_api.get_application_name(
            *a.pkt->flow, a.pkt->is_from_client());

        if ( app_name )
        {
            print_label(a, "app_id");
            TextLog_Quote(json_log, app_name);
        }
    }
    return true;
}
```

## 4. 日志输出模块

### 4.1 日志模块列表

| 模块 | 描述 | 输出格式 |
|------|------|----------|
| `alert_csv.cc` | CSV格式警报 | CSV |
| `alert_fast.cc` | 快速警报 | 文本 |
| `alert_full.cc` | 完整警报 | 文本 |
| `alert_json.cc` | JSON格式警报 | JSON |
| `alert_luajit.cc` | Lua脚本警报 | Lua |
| `alert_syslog.cc` | Syslog警报 | Syslog协议 |
| `alert_talos.cc` | Talos格式警报 | 特定格式 |
| `alert_unixsock.cc` | Unix Socket警报 | Unix Socket |
| `log_codecs.cc` | 编解码器日志 | 十六进制 |
| `log_hext.cc` | 十六进制文本日志 | 十六进制+ASCII |
| `log_pcap.cc` | PCAP格式日志 | PCAP |
| `unified2.cc` | Unified2格式 | 二进制 |

### 4.2 Unified2 日志

Unified2是最常用的日志格式:

```cpp
// Unified2记录类型
enum Unified2Type
{
    UNIFIED2_IDS_EVENT = 1,
    UNIFIED2_IDS_EVENT_V2 = 2,
    UNIFIED2_PACKET = 3,
    UNIFIED2_IDS_EVENT_IPV6 = 4,
    UNIFIED2_IDS_EVENT_V2_IPV6 = 5,
    UNIFIED2_EXTRA_DATA = 6,
    UNIFIED2_IDS_EVENT_IPV6_TUNNEL = 7,
    UNIFIED2_IDS_EVENT_V2_TUNNEL = 8,
};
```

## 5. 关键文件清单

### Events 模块 (~12KB)

| 文件 | 行数 | 描述 |
|------|------|------|
| `event.h` | 77 | Event类定义 |
| `event.cc` | ~150 | Event实现 |
| `event_queue.h` | 46 | 事件队列配置 |
| `event_queue.cc` | ~100 | 事件队列实现 |
| `sfeventq.h` | ~70 | SF事件队列 |
| `sfeventq.cc` | ~250 | SF事件队列实现 |

### Actions 模块 (~50KB)

| 文件 | 行数 | 描述 |
|------|------|------|
| `act_alert.cc` | ~80 | alert动作 |
| `act_block.cc` | ~80 | block动作 |
| `act_drop.cc` | ~100 | drop动作 |
| `act_pass.cc` | ~80 | pass动作 |
| `act_log.cc` | ~80 | log动作 |
| `act_reject.cc` | ~250 | reject动作 |
| `act_react.cc` | ~300 | react动作 |
| `act_replace.cc` | ~150 | replace动作 |
| `act_file_id.cc` | ~120 | file_id动作 |
| `actions_module.cc` | ~150 | 动作模块 |

### Loggers 模块 (~150KB)

| 文件 | 行数 | 描述 |
|------|------|------|
| `alert_fast.cc` | ~400 | 快速警报 |
| `alert_csv.cc` | ~500 | CSV警报 |
| `alert_full.cc` | ~200 | 完整警报 |
| `alert_json.cc` | ~700 | JSON警报 |
| `alert_syslog.cc` | ~300 | Syslog警报 |
| `alert_luajit.cc` | ~200 | Lua警报 |
| `log_pcap.cc` | ~300 | PCAP日志 |
| `log_hext.cc` | ~300 | 十六进制日志 |
| `unified2.cc` | ~1100 | Unified2日志 |

## 6. 架构关系

```
┌─────────────────────────────────────────────────────────────┐
│                    Detection Engine                          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    IPS Rules                            │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │ │
│  │  │  alert  │ │  drop   │ │  block  │ │  pass   │ │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Actions Framework                        │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ IpsAction                                                │ │
│  │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │ │
│  │ │Alert │ │Block │ │Drop  │ │Reject│ │Pass  │ │ │
│  │ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Events System                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ EventQueue                                             │ │
│  │ ├── Thresholding                                        │ │
│  │ └── Event Distribution                                 │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Loggers                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ alert_json│ │alert_csv │ │alert_fast│ │unified2  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │log_pcap │ │log_hext  │ │alert_syslog│ │alert_luajit│ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 7. 处理流程

### 7.1 事件生成流程

```cpp
// 检测引擎中生成事件
void DetectionEngine::match()
{
    // 创建事件
    Event event(sec, usec, sig_info, buffers, action);

    // 调用动作
    IpsAction* ips_action = rule.get_action();
    ips_action->exec(p, act_info);
}
```

### 7.2 动作执行流程

```cpp
void IpsAction::exec(Packet* p, const ActInfo& ai)
{
    // 执行动作特定逻辑
    switch (action_type)
    {
    case IAP_DROP:
        p->active->drop_session(p);
        // fall through
    case IAP_ALERT:
        alert(p, ai);  // 触发日志
        break;
    }
}
```

### 7.3 日志写入流程

```cpp
void Logger::alert(Packet* p, const char* msg, const Event& e)
{
    // 格式化事件信息
    char timestamp[TIMESTAMPSIZE];
    ts_print(e.get_timestamp(), timestamp);

    // 写入日志
    TextLog_Print(log, "%s [%s] [%s] %s\n",
        timestamp,
        e.get_msg(),
        classification[e.get_class_id()],
        packet_summary(p));
}
```

## 8. 配置示例

### 8.1 配置事件队列

```
config event_queue: max_events 8, log_events 3, order_events priority
```

### 8.2 配置日志输出

```
output alert_json: stdout
output unified2: filename snort.log
```

### 8.3 配置动作

```
# IPS规则示例
alert tcp any any -> any any (msg:"Suspicious"; content:"test"; react;)
drop tcp any any -> any 80 (msg:"Block HTTP"; content:"evil"; block;)
```

## 9. 总结

事件、动作和日志系统协同工作:

1. **事件系统** - 封装检测结果信息,包括签名ID、时间戳、分类等
2. **动作系统** - 定义对检测结果的响应方式(告警、阻断、丢弃等)
3. **日志系统** - 将事件和包数据输出到各种格式和目的地

这个三层架构提供了灵活的检测响应机制,支持从简单的日志记录到复杂的主动防御。
