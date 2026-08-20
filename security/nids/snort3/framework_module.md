---
title: "Snort3 Framework 模块架构分析"
description: "Framework 模块是 Snort3 的核心框架，提供了插件系统、模块管理、协议编解码、检查器等核心抽象。本文档详细分析 `framework/` 目录下的核心类和技术实现。"
---
# Snort3 Framework 模块架构分析

## 概述

Framework 模块是 Snort3 的核心框架，提供了插件系统、模块管理、协议编解码、检查器等核心抽象。本文档详细分析 `framework/` 目录下的核心类和技术实现。

## 文件清单

### 头文件 (framework/*.h)

| 文件 | 行数 | 功能 |
|------|------|------|
| base_api.h | 90 | 基础 API 定义，所有插件 API 的基类 |
| module.h | 262 | Module 类，配置管理的核心抽象 |
| inspector.h | 258 | Inspector 类，数据包检查器基类 |
| codec.h | 401 | Codec 类，协议编解码器基类 |
| parameter.h | 113 | Parameter 结构，配置参数定义 |
| value.h | 245 | Value 类，Lua 值封装 |
| ips_option.h | 196 | IpsOption 类，IPS 选项基类 |
| ips_action.h | 128 | IpsAction 类，IPS 动作基类 |
| cursor.h | 220 | Cursor 类，数据游标 |
| mpse.h | 152 | Mpse 类，多模式匹配引擎接口 |
| mp_data_bus.h | 224 | MPDataBus 类，多进程数据总线 |
| data_bus.h | 134 | DataBus 类，进程内数据总线 |
| connector.h | 196 | Connector 类，连接器抽象 |
| logger.h | 91 | Logger 类，日志抽象 |
| policy_selector.h | 99 | PolicySelector 类，策略选择器 |
| counts.h | 61 | 统计计数定义 |
| pig_pen.h | 84 | Inspector 引用计数管理 |
| tracer.h | 124 | 跟踪调试支持 |
| range.h | 62 | 范围验证 |
| so_rule.h | 75 | SO 规则支持 |
| act_info.h | 44 | 动作信息 |
| ips_info.h | 47 | IPS 信息 |
| lua_api.h | 47 | Lua API |
| pdu_section.h | 48 | PDU 分段 |
| endianness.h | 37 | 字节序处理 |
| decode_data.h | 172 | 解码数据 |
| plugins.h | 49 | 插件顶层头文件 |

### 实现文件 (framework/*.cc)

| 文件 | 行数 | 功能 |
|------|------|------|
| module.cc | 294 | Module 类实现 |
| inspector.cc | 170 | Inspector 类实现 |
| codec.cc | 223 | Codec 类实现 |
| parameter.cc | 1011 | Parameter 类实现 |
| value.cc | 628 | Value 类实现 |
| ips_option.cc | 260 | IpsOption 实现 |
| ips_action.cc | 109 | IpsAction 实现 |
| cursor.cc | 316 | Cursor 实现 |
| mpse.cc | 113 | Mpse 实现 |
| mp_data_bus.cc | 594 | MPDataBus 实现 |
| data_bus.cc | 225 | DataBus 实现 |
| mpse_batch.cc | 180 | MpseBatch 实现 |
| range.cc | 636 | Range 实现 |
| pig_pen.cc | 145 | PigPen 实现 |
| tracer.cc | 73 | Tracer 实现 |

## 核心类层次

### 1. BaseApi - 插件 API 基类

所有插件 API 的公共基类，定义在 `base_api.h:74-86`：

```cpp
struct BaseApi
{
    PlugType type;           // 插件类型
    uint32_t size;          // API 结构体大小
    uint32_t api_version;   // API 版本 ((BASE_API_VERSION << 16) | plugin-api-version)
    uint32_t version;       // 插件版本
    uint64_t features;      // 特性标志
    const char* options;    // API 选项
    const char* name;       // 插件名称
    const char* help;       // 帮助文本
    ModNewFunc mod_ctor;    // 模块构造函数
    ModDelFunc mod_dtor;    // 模块析构函数
};
```

**插件类型 (PlugType):**
```cpp
enum PlugType {
    PT_CODEC,           // 协议编解码器
    PT_INSPECTOR,       // 数据包检查器
    PT_IPS_ACTION,      // IPS 动作
    PT_IPS_OPTION,      // IPS 选项
    PT_SEARCH_ENGINE,    // 搜索/匹配引擎
    PT_SO_RULE,         // SO 规则
    PT_LOGGER,          // 日志器
    PT_CONNECTOR,       // 连接器
    PT_POLICY_SELECTOR,  // 策略选择器
    PT_MP_TRANSPORT,    // 多进程传输
    PT_TRACE,           // 跟踪
    PT_MAX
};
```

### 2. Module 类层次

Module 是配置管理的核心抽象，定义在 `module.h:77-259`：

```
Module - 配置模块基类
├── begin() - 开始配置节
├── end() - 结束配置节
├── set() - 设置参数值
├── get_commands() - 获取命令
├── get_rules() - 获取规则
├── get_pegs() - 获取统计点
├── get_counts() - 获取计数
├── get_profile() - 获取性能数据
├── sum_stats() - 汇总统计
├── show_stats() - 显示统计
├── reset_stats() - 重置统计
└── is_list() / is_table() - 类型检查
```

**关键函数签名：**

```cpp
// 配置回调
virtual bool begin(const char*, int, SnortConfig*);
virtual bool end(const char*, int, SnortConfig*);
virtual bool set(const char*, Value&, SnortConfig*);

// 统计相关
virtual PegCount* get_counts() const;
virtual void sum_stats(bool dump_stats);
virtual void show_stats();
virtual void reset_stats();
virtual void init_stats(bool new_thread=false);

// 元数据
virtual const Command* get_commands() const;
virtual const RuleMap* get_rules() const;
virtual const PegInfo* get_pegs() const;

// 名称和类型
const char* get_name() const;
bool is_table() const;
bool is_list() const;
Parameter::Type get_type() const;
```

### 3. Inspector 类层次

Inspector 是数据包处理的核心抽象，定义在 `inspector.h:73-209`：

```
Inspector - 数据包检查器基类
├── configure() - 配置检查器
├── tear_down() - 拆除检查器
├── tinit() - 线程初始化
├── tterm() - 线程终止
├── likes() - 过滤数据包
├── eval() - 处理数据包
├── clear() - 清理状态
├── get_buf() - 获取检查缓冲区
├── get_splitter() - 获取流分割器
└── is_control_channel() - 控制通道检查
```

**检查器类型 (InspectorType):**

```cpp
enum InspectorType {
    IT_PASSIVE,      // 仅配置，或数据消费者 (如 file_log, binder)
    IT_PACKET,       // 仅处理原始数据包 (如 normalize, capture)
    IT_STREAM,        // 流跟踪和重组 (如 ip, tcp, udp)
    IT_NETWORK,      // 无服务的包处理 (如 arp, bo)
    IT_SERVICE,      // 提取和分析服务 PDU (如 dce, http, ssl)
    IT_CONTROL,      // 检测前处理所有包 (如 appid)
    IT_PROBE,        // 检测后处理所有包 (如 perf_monitor, port_scan)
    IT_PROBE_FIRST,  // 检测前处理所有包 (如 packet_capture)
    IT_MAX
};
```

**关键函数签名：**

```cpp
// 主线程函数
virtual bool configure(SnortConfig*);
virtual void tear_down(SnortConfig*, bool shutdown);
virtual void show(const SnortConfig*) const;

// 线程本地函数
virtual void tinit();  // 分配线程本地资源
virtual void tterm();  // 清理线程本地资源

// 数据包处理函数
virtual bool likes(Packet*);  // 过滤
virtual void eval(Packet*);    // 处理
virtual void clear(Packet*);   // 清理

// 框架支持
virtual bool get_buf(InspectionBuffer::Type, Packet*, InspectionBuffer&);
virtual class StreamSplitter* get_splitter(bool to_server);
```

### 4. Codec 类层次

Codec 负责协议数据的编解码，定义在 `codec.h:244-371`：

```
Codec - 协议编解码器基类
├── decode() - 解码数据包
├── encode() - 编码数据包
├── update() - 更新校验和/长度
├── log() - 记录日志
├── format() - 格式化
├── get_data_link_type() - 获取 DLT
└── get_protocol_ids() - 获取协议 ID
```

**关键函数签名：**

```cpp
// 解码函数 - 纯虚函数
virtual bool decode(const RawData&, CodecData&, DecodeData&) = 0;

// 编码函数
virtual bool encode(const uint8_t* raw_in, const uint16_t raw_len,
    EncState&, Buffer&, Flow*);

// 更新函数
virtual void update(const ip::IpApi&, const EncodeFlags flags,
    uint8_t* raw_pkt, uint16_t lyr_len, uint32_t& updated_len);
```

### 5. IpsOption 类层次

IpsOption 是 IPS 检测选项的基类，定义在 `ips_option.h`：

```
IpsOption - IPS 选项基类
├── match() - 执行匹配
├── gets_buf() - 获取缓冲区
├── operator==() - 比较操作
└── get_dynamic_element() - 获取动态元素
```

### 6. IpsAction 类层次

IpsAction 是 IPS 动作的基类，定义在 `ips_action.h`：

```
IpsAction - IPS 动作基类
├── exec() - 执行动作
├── get_gid() - 获取生成器 ID
├── get_sid() - 获取签名 ID
└── get_priority() - 获取优先级
```

## 插件系统架构

### 插件加载流程

```
1. PluginManager::init() - 初始化插件管理器
2. PluginManager::load_plugins() - 加载插件
   ├── 加载静态插件
   ├── 加载动态插件 (.so 文件)
   └── 加载脚本生成的插件
3. 各子管理器使用插件 API 创建实例
   ├── CodecManager - 创建 Codec
   ├── IpsManager - 创建 IpsOption/IpsAction
   ├── InspectorManager - 创建 Inspector
   └── MpseManager - 创建搜索引擎
```

### PluginManager 类

定义在 `managers/plugin_manager.h`：

```cpp
class PluginManager {
public:
    // 初始化和加载
    static void init();
    static void load_plugins(const std::string& lib_paths);
    static void load_plugins(const snort::BaseApi**);
    static void reload_plugins(const char*, bool allow_missing_so_rules);

    // 模块管理
    static void add_module(snort::Module*);
    static snort::Module* get_module(const char*);

    // 查询
    static const snort::BaseApi* get_api(const char* name);
    static PlugType get_type(const char*);
    static const char* get_type_name(PlugType);

    // 实例化
    static void instantiate(snort::Module*, snort::SnortConfig*, const char* name);
    static void set_instantiated(const char* name);

    // 清理
    static void release_plugins();
    static void empty_trash();
};
```

### ModuleManager 类

定义在 `managers/module_manager.h`：

```cpp
class ModuleManager {
public:
    // 模块注册
    static void add_module(const Module*);
    static void set_defaults(Module*, SnortConfig*);

    // 加载
    static void load_params();
    static void load_commands(Shell*);
    static void load_rules(SnortConfig*);

    // 查询
    static void list_modules(const char* = nullptr);
    static void dump_modules();
    static void show_modules();
    static const struct Parameter* get_parameter(const char* table, const char* option);

    // 统计
    static void init_stats();
    static void dump_stats(const char* skip = nullptr, bool dynamic = false);
    static void reset_stats(SnortConfig*);
    static void accumulate(const SnortConfig*, const char* except = "snort");

    // 错误处理
    static void reset_errors();
    static unsigned get_errors();
};
```

### InspectorManager 类

定义在 `managers/inspector_manager.h`：

```cpp
class InspectorManager {
public:
    // 映射管理
    static void new_map();
    static void prepare_map();
    static void reconcile_map(SnortConfig*);
    static InspectorVector* get_map();

    // 配置
    static bool configure(SnortConfig*);
    static void prepare_inspectors(SnortConfig*);

    // 创建组
    static TrafficPig* create_traffic_group();
    static ServicePig* create_service_group();
    static GlobalPig* create_global_group();

    // 执行
    static void execute(Packet*);      // 执行检查
    static void probe(Packet*);        // 探测
    static void probe_first(Packet*);  // 优先探测

    // 查询
    static Inspector* get_binder();
    static Inspector* get_service_inspector(const SnortProtocolId);
    static Inspector* get_inspector(const char* key, Module::Usage);

    // 清理
    static void tear_down(SnortConfig*);
    static void cleanup();
};
```

## 关键代码片段

### 1. Module 配置流程 (module.h)

```cpp
class Module {
protected:
    // 构造函数
    Module(const char* name, const char* help);
    Module(const char* name, const char* help, const Parameter*, bool is_list = false);

public:
    // 配置回调 - 子类实现
    virtual bool begin(const char*, int, SnortConfig*);
    virtual bool set(const char*, Value&, SnortConfig*);
    virtual bool end(const char*, int, SnortConfig*);

    // 统计
    virtual PegCount* get_counts() const;
    virtual const PegInfo* get_pegs() const;
    virtual void sum_stats(bool dump_stats);
};
```

### 2. Inspector 数据包处理 (inspector.cc)

```cpp
bool Inspector::likes(Packet* p)
{
    // 默认实现：基于协议过滤
    const InspectApi* a = get_api();
    if (!a || !a->proto_bits)
        return true;

    return p->is_protos(a->proto_bits);
}

void Inspector::eval(Packet* p)
{
    // 默认空实现，子类覆盖
}
```

### 3. Codec 解码骨架 (codec.h)

```cpp
class Codec {
protected:
    Codec(const char* s) { name = s; }

public:
    // 纯虚函数 - 必须实现
    virtual bool decode(const RawData&, CodecData&, DecodeData&) = 0;

    // 可选实现
    virtual bool encode(const uint8_t*, const uint16_t, EncState&, Buffer&, Flow*);
    virtual void update(const ip::IpApi&, EncodeFlags, uint8_t*, uint16_t, uint32_t&);
    virtual void log(TextLog* const, const uint8_t*, const uint16_t);

    // 查询
    virtual void get_data_link_type(std::vector<int>&);
    virtual void get_protocol_ids(std::vector<ProtocolId>&);
};
```

### 4. Parameter 类型系统 (parameter.h)

```cpp
enum Type {
    PT_TABLE,      // 表格 (带命名键)
    PT_LIST,       // 列表 (数字索引)
    PT_DYNAMIC,    // 动态类型
    PT_BOOL,       // 布尔值
    PT_INT,        // 有符号整数
    PT_INTERVAL,   // 区间
    PT_REAL,       // 实数
    PT_PORT,       // 端口号
    PT_STRING,     // 字符串
    PT_SELECT,     // 选择 (枚举)
    PT_MULTI,      // 多选
    PT_ENUM,       // 字符串转无符号
    PT_MAC,        // MAC 地址
    PT_IP4,        // IPv4 地址
    PT_ADDR,       // IP 地址 (v4/v6)
    PT_BIT_LIST,   // 位列表
    PT_INT_LIST,   // 整数列表
    PT_ADDR_LIST,  // 地址列表
    PT_IMPLIED,    // 隐含值
    PT_STR_LIST,   // 字符串列表
    PT_DYNAMICS,   // 动态列表
    PT_MAX
};
```

### 5. InspectionBuffer 定义 (inspector.h)

```cpp
struct InspectionBuffer {
    enum Type {
        IBT_VBA,        // VBA 脚本
        IBT_JS_DATA,    // JavaScript 数据
        IBT_KEY,        // 密钥
        IBT_HEADER,     // 头部
        IBT_BODY,       // 主体
        IBT_MAX
    };

    const uint8_t* data;  // 缓冲区数据
    unsigned len;          // 数据长度
    bool is_accumulated;  // 是否累积
};
```

### 6. DataBus 发布订阅 (data_bus.h)

```cpp
class DataBus {
public:
    // 订阅
    template<typename T>
    void subscribe(const char* key, std::function<void(const T&)> handler);

    // 发布
    template<typename T>
    void publish(const char* key, const T& data);

    // 订阅基于 Packet 的事件
    template<typename T>
    void subscribe(const char* key, Packet*, std::function<void(const T&)> handler);
};
```

### 7. MPDataBus 多进程通信 (mp_data_bus.h)

```cpp
class MPDataBus {
public:
    // 多进程间通信
    void publish(unsigned procs, unsigned worker_id, const char* key, const uint8_t* data, unsigned len);

    // 处理收到的消息
    void process(unsigned id, std::function<void(const uint8_t*, unsigned)> handler);

    // 初始化
    void init(unsigned max_procs);
};
```

## 设计模式

### 1. 工厂模式

Module、Inspector、Codec 等都采用工厂模式创建实例：

```cpp
// 通过 Module 创建 Inspector
typedef Inspector* (* InspectNew)(Module*);
InspectNew ctor;  // InspectApi 中的构造函数指针

Inspector* inspector = api->ctor(module);
```

### 2. 模板方法模式

Module 的配置流程使用模板方法：

```cpp
// 调用顺序：begin() -> set()* -> end()
module->begin(name, idx, sc);
while (has_params())
    module->set(name, value, sc);
module->end(name, idx, sc);
```

### 3. 观察者模式

DataBus 实现发布-订阅机制：

```cpp
// 订阅
data_bus->subscribe("packet", [](const Packet* p) { ... });

// 发布
data_bus->publish("packet", packet);
```

### 4. 单例模式

SnortConfig 全局单例：

```cpp
SnortConfig::set_conf(sc);  // 设置全局配置
SnortConfig::get_conf();   // 获取全局配置
```

## 插件类型总览

| 类型 | 基类 | 管理器 | 用途 |
|------|------|--------|------|
| Codec | Codec | CodecManager | 协议编解码 |
| Inspector | Inspector | InspectorManager | 数据包检查 |
| IpsOption | IpsOption | IpsManager | 检测选项 |
| IpsAction | IpsAction | ActionManager | 检测动作 |
| SearchEngine | Mpse | MpseManager | 模式匹配 |
| Logger | Logger | EventManager | 日志输出 |
| Connector | Connector | ConnectorManager | 数据连接 |
| PolicySelector | PolicySelector | PolicySelectorManager | 策略选择 |
| MpTransport | MpTransport | MpTransportManager | 多进程传输 |

## 总结

Framework 模块是 Snort3 的核心架构：

1. **插件化设计**：通过 BaseApi 和类型化的插件接口实现高度可扩展
2. **Module 系统**：提供数据驱动的配置管理，支持 Lua 配置解析
3. **Inspector 抽象**：统一的数据包处理接口，支持多种检查器类型
4. **Codec 框架**：协议编解码的通用框架
5. **数据总线**：DataBus 和 MPDataBus 提供灵活的事件通信机制
6. **统计系统**：完整的 PegInfo 统计框架，支持多线程聚合
