---
type: entity
tags: [snort, ids-ips, intrusion-detection, intrusion-prevention, network-security]
created: 2026-05-27
sources: [github-snort3-framework]
---

# Snort3 Framework

## 定义

Snort3 的核心框架是一个模块化、可扩展的入侵检测/防御系统（IDS/IPS）架构，基于插件化的检查器（Inspector）和模块（Module）系统实现数据驱动的配置和运行时管理。

## 关键要点

### 1. 插件系统 (PlugInspector / PlugActor)

Snort3 采用统一的 **BaseApi** 机制管理所有插件类型，每类插件有独立的版本化 API：

| 插件类型 | API 版本宏 | 说明 |
|----------|-----------|------|
| Codec | `CDAPI_VERSION` | 协议编解码 (e.g., IP, TCP, UDP) |
| Inspector | `INSAPI_VERSION` | 包检查器，对应 Snort2 preprocessors |
| IpsOption | `IPSAPI_VERSION` | IPS 规则选项 (e.g., `content`, `offset`) |
| IpsAction | `ACTAPI_VERSION` | 自定义动作 (e.g., `alert`, `drop`) |
| Logger | `LOGAPI_VERSION` | 事件日志输出 |
| Connector | `CONNECTOR_API_VERSION` | 进程间通信 |
| Mpse | `SEAPI_VERSION` | 多模式搜索（快速模式匹配）|
| PolicySelector | `POLICY_SELECTOR_API_VERSION` | 策略选择 |
| SO Rule | `SOAPI_VERSION` | Shared Object 规则（自定义C++检测）|

**PlugInspector** — `Inspector` 类是主要的工作引擎：
- `configure(SnortConfig*)` — 主线程配置，返回验证状态
- `tinit() / tterm()` — 线程本地初始化/清理
- `eval(Packet*)` — 包处理主函数
- `likes(Packet*)` — 包过滤（决定是否进入 eval）
- `disable(SnortConfig*)` — 配置后检查是否需要禁用

**PlugActor** — `IpsOption` 类是规则选项的执行器：
- `eval(Cursor&, Packet*)` — 返回 `MATCH / NO_MATCH / NO_ALERT / FAILED_BIT`
- `action(Packet*)` — 执行动作（如 log、alert）
- `hash() / operator==` — 用于规则选项去重

### 2. Module 生命周期

**数据驱动配置流程：**

```
configure → start → [reload] → stop
```

| 阶段 | 方法 | 说明 |
|------|------|------|
| 配置 | `begin() / set() / end()` | Lua 配置解析，Module 存储数据构建组件 |
| 启动 | (内部) | 所有 Inspector::configure() 完成后才调用控制命令 |
| 重载 | `tear_down()` | Inspector 实例移除时调用 |
| 停止 | (内部) | 清理资源 |

**Module 类职责：**
- 管理配置参数 (`Parameter` 系统，支持 20+ 类型：INT, STRING, BOOL, ENUM, ADDR 等)
- 提供命令接口 (`Command` 结构，LuaCFunction 回调)
- 统计信息 (`PegInfo`: SUM/NOW/MAX 计数类型)
- 数据验证 (`RangeCheck`: EQ, NOT, LT, GT, LG, LEG 等范围检查)

**Module::Usage 枚举：**
```cpp
enum Usage { GLOBAL, CONTEXT, INSPECT, DETECT };
```

### 3. pig (Packet Inspection Graph / 报文处理线程)

`PigPen` 类是 Packet Processing Thread 的统一入口，提供：

**Inspector 查询：**
```cpp
static Inspector* get_binder();
static Inspector* get_file_inspector(const SnortConfig* = nullptr);
static Inspector* get_service_inspector(const SnortProtocolId);
static Inspector* get_service_inspector(const char* svc);
static Inspector* get_inspector(const char* key, bool dflt_only = false, const SnortConfig* = nullptr);
```

**运行时支持：**
```cpp
static bool snort_is_reloading();       // 检查是否在重载配置
static void install_oops_handler();     // 异常处理
static bool inspect_rebuilt(Packet*);   // 检测重建包
static uint64_t get_packet_number();   // 报文计数器
```

**Inspector 类型层次 (`InspectorType`)：**
```cpp
IT_PASSIVE   → 仅配置或数据消费 (e.g., binder, ftp_client)
IT_WIZARD    → 服务检查器猜测
IT_PACKET    → 原始包处理 (e.g., normalize, capture)
IT_STREAM    → 流跟踪和重组 (e.g., ip, tcp, udp)
IT_FIRST     → 新流首包 + 重载后首包
IT_NETWORK   → 无服务的包 (e.g., arp, bo)
IT_SERVICE   → 服务 PDU 提取分析 (e.g., dce, http, ssl)
IT_CONTROL   → 检测前处理所有包 (e.g., appid)
IT_PROBE     → 检测后处理 (e.g., perf_monitor, port_scan)
IT_FILE      → 文件识别
IT_PROBE_FIRST → 检测前处理 (e.g., packet_capture)
```

### 4. Shell 命令系统

Module 通过 `Command` 结构暴露 Lua shell 命令：

```cpp
struct Command
{
    const char* name;
    LuaCFunction func;           // Lua C function pointer
    const Parameter* params;     // 命令参数定义
    const char* help;
    bool can_run_in_parallel;    // 是否可与其他控制命令并行
};
```

**命令注册流程：**
1. Module 重载 `get_commands()` 返回 `Command*` 数组
2. Lua 解析器调用 `Command::get_arg_list()` 生成参数列表
3. Shell 执行函数，支持并行控制 (`can_run_in_parallel`)

**示例命令结构：**
```cpp
virtual const Command* get_commands() const override
{
    static const Command cmds[] = {
        { "command_name", lua_handler_function, param_table, "help text", false },
        { nullptr, nullptr, nullptr, nullptr, false }
    };
    return cmds;
}
```

### 5. DataBus 事件系统

框架内置发布-订阅机制用于组件间通信：

```cpp
// 订阅
static void subscribe(const PubKey&, unsigned id, DataHandler*);
static void subscribe_network(const PubKey&, unsigned id, DataHandler*);
static void subscribe_global(const PubKey&, unsigned id, DataHandler*, SnortConfig&);

// 发布
static void publish(unsigned pub_id, unsigned evt_id, DataEvent&, Flow* = nullptr);
```

**事件类型：** `BufferEvent`, `PacketEvent`, `BareDataEvent`

### 6. Cursor 系统

`Cursor` 类管理规则评估时的缓冲区指针：

```cpp
class SO_PUBLIC Cursor
{
    void set(const char* name, const uint8_t* buf, unsigned len, bool ext = false);
    unsigned get_pos() const;        // 当前位置
    unsigned length() const;        // 剩余长度
    bool add_pos(unsigned n);        // 前进
    bool set_pos(unsigned n);        // 跳转
    void set_delta(unsigned n);      // 循环偏移
};
```

**扩展缓冲区：** 支持分片数据流（如 HTTP chunked）的连续评估

### 7. MPDataBus 多进程数据总线

多进程环境下的事件同步系统：
- 基于 Ring Buffer 的事件队列
- Worker Thread 异步处理
- 支持事件序列化/反序列化
- Transport 层可插拔（默认 unix_transport）

## 相关概念

- [[intrusion-detection-system]] — IDS 基础概念
- [[network-security-monitoring]] — NSM 相关
- [[tcp-ip-protocol-stack]] — Snort3 协议解析依赖
- [[linux-kernel-networking]] — 网络包处理流程

## 来源详情

- [[github-snort3-framework]] — Snort3 源码框架分析
