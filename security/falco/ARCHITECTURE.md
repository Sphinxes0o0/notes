# Falco 架构与模块详细分析

> 基于代码深入分析的架构文档

---

## 目录

1. [项目概述](#1-项目概述)
2. [模块总览](#2-模块总览)
3. [app 模块 - 应用状态机](#3-app-模块---应用状态机)
4. [configuration 模块 - 配置管理](#4-configuration-模块---配置管理)
5. [outputs 模块 - 输出处理](#5-outputs-模块---输出处理)
6. [webserver 模块 - HTTP 服务](#6-webserver-模块---http-服务)
7. [stats_writer 模块 - 统计收集](#7-stats_writer-模块---统计收集)
8. [falco_engine 模块 - 核心引擎](#8-falco_engine-模块---核心引擎)
9. [rule_loader 模块 - 规则加载](#9-rule_loader-模块---规则加载)
10. [filter_ruleset 模块 - 规则集](#10-filter_ruleset-模块---规则集)
11. [filter_macro_resolver 模块 - 宏解析](#11-filter_macro_resolver-模块---宏解析)
12. [formats 模块 - 格式化](#12-formats-模块---格式化)
13. [模块关系图](#13-模块关系图)
14. [数据流](#14-数据流)
15. [附录 B: falcosecurity-libs 外部依赖分析](#附录-b-falcosecurity-libs-外部依赖分析)
16. [附录 C: falcosecurity-rules 规则子模块分析](#附录-c-falcosecurity-rules-规则子模块分析)
17. [附录 D: CMake 构建配置](#附录-d-cmake-构建配置)

---

## 1. 项目概述

**Falco** 是一个云原生运行时安全工具，使用 **C++** 编写，运行在 Linux 系统上。它用于实时检测和告警异常行为及潜在安全威胁，是 **CNCF** 的毕业项目。

| 属性 | 值 |
|------|-----|
| 编程语言 | C++ (userspace 代码) |
| 构建系统 | CMake 3.5.1+ |
| 许可证 | Apache 2.0 |
| 核心依赖 | `falcosecurity-libs` (libsinsp, libscap) |
| 支持平台 | Linux (x86_64, aarch64), macOS, Windows (实验性) |

---

## 2. 模块总览

### 2.1 顶级目录结构

| 目录 | 用途 |
|------|------|
| `userspace/falco/` | 主应用程序源码 |
| `userspace/falco/app/` | 应用状态机和动作 |
| `userspace/falco/outputs*.{h,cpp}` | 输出处理 |
| `userspace/falco/webserver.{h,cpp}` | HTTP 服务 |
| `userspace/falco/stats_writer.{h,cpp}` | 统计收集 |
| `userspace/falco/configuration.{h,cpp}` | 配置管理 |
| `userspace/engine/` | 规则引擎源码 |
| `userspace/engine/falco_engine.{h,cpp}` | 核心引擎 |
| `userspace/engine/rule_loader*.{h,cpp}` | 规则加载管道 |
| `userspace/engine/filter_ruleset.{h,cpp}` | 规则集接口 |
| `userspace/engine/evttype_index_ruleset.{h,cpp}` | 事件类型索引规则集 |
| `userspace/engine/filter_macro_resolver.{h,cpp}` | 宏解析器 |
| `userspace/engine/formats.{h,cpp}` | 输出格式化 |

### 2.2 核心模块依赖关系

```
┌─────────────────────────────────────────────────────────────────┐
│                         userspace/falco/                        │
├─────────────────────────────────────────────────────────────────┤
│  app/ (状态机)                                                  │
│    ├── configuration.{h,cpp}  ← YAML配置解析                    │
│    ├── outputs*.{h,cpp}      ← 事件输出                        │
│    ├── webserver.{h,cpp}    ← HTTP健康检查                     │
│    └── stats_writer.{h,cpp} ← 统计收集                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         userspace/engine/                       │
├─────────────────────────────────────────────────────────────────┤
│  falco_engine.{h,cpp}     ← 核心引擎                           │
│    ├── rule_loader/         ← YAML → AST → 可执行规则           │
│    ├── filter_ruleset/      ← 规则集接口                        │
│    │     └── evttype_index_ruleset  ← O(1)事件类型索引实现     │
│    ├── filter_macro_resolver ← 宏解析 (Visitor模式)             │
│    └── formats.{h,cpp}     ← 输出格式化                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      falcosecurity-libs                          │
│  (子模块: libsinsp, libscap)                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. app 模块 - 应用状态机

**文件路径**: `userspace/falco/app/`

### 3.1 核心文件

| 文件 | 行数 | 用途 |
|------|------|------|
| `app.h` | 34 | 应用入口声明 |
| `app.cpp` | 115 | 状态机实现 |
| `state.h` | 168 | 应用状态结构 |
| `run_result.h` | 82 | 操作结果类型 |
| `options.h` | 88 | 命令行选项 |
| `actions.h` | 62 | 32个动作声明 |
| `actions/*.cpp` | - | 动作实现 |

### 3.2 应用状态 (`state.h`)

```cpp
// state.h:45-165
struct state {
    std::string cmdline;                              // 行 73: 命令行
    falco::app::options options;                      // 行 74: 解析后的CLI选项
    std::atomic<bool> restart;                        // 行 76: 热重启标志
    std::shared_ptr<falco_configuration> config;     // 行 77: 配置
    std::shared_ptr<falco_outputs> outputs;          // 行 78: 输出处理器
    std::shared_ptr<falco_engine> engine;            // 行 79: 规则引擎
    std::vector<std::string> loaded_sources;         // 行 85: 已加载的事件源
    std::unordered_set<std::string> enabled_sources;  // 行 86: 已启用的事件源
    std::shared_ptr<sinsp> offline_inspector;        // 行 93: 离线检查器
    indexed_vector<source_info> source_infos;         // 行 97: 每个源的元数据
    falco_webserver webserver;                        // 行 114: HTTP服务器
    // ...
};
```

### 3.3 状态机 Run 步骤 (`app.cpp:56-85`)

按顺序执行 28 个动作：

| # | 动作 | 文件 | 用途 |
|---|------|------|------|
| 1 | `print_help` | `print_help.cpp` | 显示帮助 |
| 2 | `print_config_schema` | `print_config_schema.cpp` | 输出配置JSON Schema |
| 3 | `print_rule_schema` | `print_rule_schema.cpp` | 输出规则JSON Schema |
| 4 | `print_ignored_events` | `print_ignored_events.cpp` | 列出忽略的系统调用 |
| 5 | `print_syscall_events` | `print_syscall_events.cpp` | 列出所有系统调用事件 |
| 6 | `load_config` | `load_config.cpp` | 加载YAML配置 |
| 7 | `print_kernel_version` | `print_kernel_version.cpp` | 记录内核版本 |
| 8 | `print_version` | `print_version.cpp` | 显示版本信息 |
| 9 | `print_page_size` | `print_page_size.cpp` | 显示系统页大小 |
| 10 | `require_config_file` | `require_config_file.cpp` | 确保配置文件存在 |
| 11 | `print_plugin_info` | `print_plugin_info.cpp` | 显示插件信息 |
| 12 | `list_plugins` | `list_plugins.cpp` | 列出已加载插件 |
| 13 | `load_plugins` | `load_plugins.cpp` | 加载插件库 |
| 14 | `init_inspectors` | `init_inspectors.cpp` | 初始化检查器 |
| 15 | `init_falco_engine` | `init_falco_engine.cpp` | 初始化规则引擎 |
| 16 | `list_fields` | `list_fields.cpp` | 列出可用过滤字段 |
| 17 | `select_event_sources` | `select_event_sources.cpp` | 选择启用的源 |
| 18 | `validate_rules_files` | `validate_rules_files.cpp` | 验证规则文件 |
| 19 | `load_rules_files` | `load_rules_files.cpp` | 加载规则文件 |
| 20 | `print_support` | `print_support.cpp` | 输出支持信息 |
| 21 | `init_outputs` | `init_outputs.cpp` | 初始化输出 |
| 22 | `create_signal_handlers` | `create_signal_handlers.cpp` | 设置信号处理器 |
| 23 | `pidfile` | `pidfile.cpp` | 创建PID文件 |
| 24 | `configure_interesting_sets` | `configure_interesting_sets.cpp` | 配置系统调用集 |
| 25 | `configure_syscall_buffer_size` | `configure_syscall_buffer_size.cpp` | 设置缓冲区大小 |
| 26 | `configure_syscall_buffer_num` | `configure_syscall_buffer_num.cpp` | 设置缓冲区数量 |
| 27 | `start_webserver` | `start_webserver.cpp` | 启动Web服务器 |
| 28 | `process_events` | `process_events.cpp` | **主事件处理循环** |

### 3.4 Teardown 步骤 (`app.cpp:87-93`)

| # | 动作 | 用途 |
|---|------|------|
| 1 | `unregister_signal_handlers` | 恢复默认信号处理 |
| 2 | `stop_webserver` | 停止Web服务器 |
| 3 | `cleanup_outputs` | 刷新并清理输出 |
| 4 | `close_inspectors` | 关闭所有检查器 |

### 3.5 信号处理 (`signals.h`, `atomic_signal_handler.h`)

```cpp
// signals.h:27-29
extern atomic_signal_handler g_terminate_signal;     // SIGINT/SIGTERM
extern atomic_signal_handler g_restart_signal;        // SIGHUP
extern atomic_signal_handler g_reopen_outputs_signal; // SIGUSR1
```

**atomic_signal_handler** (`atomic_signal_handler.h:1-114`) 提供线程安全的信号处理，支持 exactly-once 执行语义。

---

## 4. configuration 模块 - 配置管理

**文件路径**: `userspace/falco/configuration.{h,cpp}`

### 4.1 文件信息

| 文件 | 行数 |
|------|------|
| `configuration.h` | 468 |
| `configuration.cpp` | 784 |

### 4.2 主类: `falco_configuration` (`configuration.h:50`)

### 4.3 嵌套配置结构体

#### `plugin_config` (行 52-57)
```cpp
struct plugin_config {
    std::string m_name;           // 插件名称
    std::string m_library_path;  // 插件库路径
    std::string m_init_config;   // 初始化配置 (JSON)
    std::string m_open_params;   // 打开参数
};
```

#### `webserver_config` (行 79-87)
```cpp
struct webserver_config {
    uint32_t m_threadiness = 0;                  // 线程数 (0=自动)
    uint32_t m_listen_port = 8765;               // 监听端口
    std::string m_listen_address = "0.0.0.0";   // 监听地址
    std::string m_k8s_healthz_endpoint = "/healthz"; // 健康检查端点
    bool m_ssl_enabled = false;                   // SSL启用
    std::string m_ssl_certificate;                 // SSL证书路径
    bool m_prometheus_metrics_enabled = false;   // Prometheus指标
};
```

#### `kmod_config` (行 64-67)
```cpp
struct kmod_config {
    int16_t m_buf_size_preset = 4;     // 缓冲区大小预设
    bool m_drop_failed_exit = false;     // 退出时丢弃
};
```

#### `modern_ebpf_config` (行 69-73)
```cpp
struct modern_ebpf_config {
    uint16_t m_cpus_for_each_buffer = 2;  // 每个缓冲区的CPU数
    int16_t m_buf_size_preset = 4;        // 缓冲区大小预设
    bool m_drop_failed_exit = false;       // 退出时丢弃
};
```

### 4.4 主要配置字段

| 字段 | 行 | 类型 | 用途 |
|------|-----|------|------|
| `m_loaded_configs_filenames` | 123 | `list<string>` | 已加载配置文件 |
| `m_rules_filenames` | 130 | `list<string>` | 规则文件列表 |
| `m_outputs` | 150 | `vector<outputs::config>` | 输出配置 |
| `m_json_output` | 144 | `bool` | JSON输出 |
| `m_log_level` | 149 | `string` | 日志级别 |
| `m_min_priority` | 154 | `priority_type` | 最低优先级 |
| `m_webserver_enabled` | 162 | `bool` | Web服务器启用 |
| `m_webserver_config` | 163 | `webserver_config` | Web服务器配置 |
| `m_plugins` | 193 | `vector<plugin_config>` | 插件配置 |
| `m_engine_mode` | 203 | `engine_kind_t` | 引擎类型 |

### 4.5 引擎类型枚举 (`configuration.h:43`)
```cpp
enum class engine_kind_t : uint8_t { 
    KMOD,        // 内核模块驱动
    MODERN_EBPF, // 现代eBPF驱动
    REPLAY,      // 捕获文件回放
    NODRIVER     // 无驱动 (禁用实时捕获)
};
```

### 4.6 主要配置加载逻辑 (`configuration.cpp`)

| 方法 | 行 | 功能 |
|------|-----|------|
| `init_from_file()` | 124-152 | 从文件加载主配置 |
| `merge_config_files()` | 162-220 | 合并多配置文件 |
| `load_yaml()` | 283-697 | 解析所有YAML配置键 |
| `load_engine_config()` | 233-281 | 加载引擎特定配置 |

### 4.7 配置选项表

| 类别 | 键 | 类型 | 默认值 |
|------|-----|------|--------|
| **输出** | `json_output` | bool | false |
| | `file_output.enabled` | bool | false |
| | `http_output.url` | string | (必需) |
| | `output_timeout` | uint32 | 2000 |
| | `rule_matching` | string | "first" |
| **Web服务器** | `webserver.enabled` | bool | false |
| | `webserver.listen_port` | uint32 | 8765 |
| | `webserver.prometheus_metrics_enabled` | bool | false |
| **引擎** | `engine.kind` | string | "kmod" |
| **捕获** | `capture.enabled` | bool | false |
| | `capture.mode` | string | "rules" |

---

## 5. outputs 模块 - 输出处理

**文件路径**: `userspace/falco/outputs*.{h,cpp}`

### 5.1 文件概览

| 文件 | 行数 | 用途 |
|------|------|------|
| `outputs.h` | 96 | 抽象基类 |
| `falco_outputs.h` | 134 | 主编排器类 |
| `falco_outputs.cpp` | 323 | 实现 |
| `outputs_stdout.{h,cpp}` | 32/36 | 标准输出 |
| `outputs_syslog.{h,cpp}` | 30/24 | 系统日志 |
| `outputs_file.{h,cpp}` | 41/52 | 文件输出 |
| `outputs_program.{h,cpp}` | 39/63 | 程序输出 |
| `outputs_http.{h,cpp}` | 43/133 | HTTP输出 |

### 5.2 类层次

```
abstract_output (outputs.h:58)
    ├── output_stdout
    ├── output_syslog
    ├── output_file
    ├── output_program
    └── output_http
    
falco_outputs (falco_outputs.h:41) - 主编排器
```

### 5.3 抽象基类 (`outputs.h:58-93`)

```cpp
class abstract_output {
public:
    virtual bool init(const config& oc, bool buffered, 
                      const std::string& hostname, bool json_output, 
                      std::string& err);              // 行 62-74
    virtual void output(const message* msg) = 0;     // 行 80: 纯虚
    virtual void reopen() {}                         // 行 83
    virtual void cleanup() {}                        // 行 86
};
```

### 5.4 消息结构 (`outputs.h:43-51`)

```cpp
struct message {
    uint64_t ts;                              // 时间戳
    falco_common::priority_type priority;    // 优先级
    std::string msg;                         // 格式化消息
    std::string rule;                        // 触发的规则名
    std::string source;                      // 事件源
    nlohmann::json fields;                  // 事件字段
    std::set<std::string> tags;             // 关联标签
};
```

### 5.5 `falco_outputs` 类 (`falco_outputs.h:41-134`)

```cpp
class falco_outputs {
public:
    // 事件处理
    void handle_event(sinsp_evt*, const std::string& rule, 
                      const std::string& source, 
                      falco_common::priority_type priority,
                      const std::string& format,
                      std::set<std::string>& tags,
                      extra_output_field_t& extra_fields);  // 行 62-68
    
    void handle_msg(uint64_t now, falco_common::priority_type priority,
                    const std::string& msg, const std::string& rule,
                    nlohmann::json& output_fields);        // 行 74-78
    
    void cleanup_outputs();  // 行 85
    void reopen_outputs();   // 行 91
    
private:
    tbb::concurrent_bounded_queue<ctrl_msg> m_queue;  // 行 122-123: TBB队列
    std::thread m_worker_thread;                        // 行 127: 工作线程
    std::atomic<uint64_t> m_outputs_queue_num_drops;    // 行 126: 丢弃计数
};
```

### 5.6 TBB 队列使用 (`falco_outputs.cpp:255-301`)

- **推入**: `push()` 方法 (行 255-269) 使用 `try_push()` 非阻塞推送
- **工作线程**: `worker()` 方法 (行 274-301) 从队列弹出消息并分发
- **控制消息**: `CTRL_MSG_STOP`, `CTRL_MSG_OUTPUT`, `CTRL_MSG_CLEANUP`, `CTRL_MSG_REOPEN`

### 5.7 输出实现对比

| 实现 | 配置选项 | 关键方法 |
|------|----------|----------|
| `output_stdout` | 无 | `std::cout << msg << "\n"` |
| `output_syslog` | 无 | `::syslog(priority, "%s", msg)` |
| `output_file` | `filename`, `keep_alive` | `ofstream::append` |
| `output_program` | `program`, `keep_alive` | `popen()` |
| `output_http` | `url`, `insecure`, `ca_cert`, `mtls` | `curl_easy_perform()` |

---

## 6. webserver 模块 - HTTP 服务

**文件路径**: `userspace/falco/webserver.{h,cpp}`

### 6.1 文件信息

| 文件 | 行数 |
|------|------|
| `webserver.h` | 50 |
| `webserver.cpp` | 116 |

### 6.2 类定义 (`webserver.h:32-50`)

```cpp
class falco_webserver {
public:
    falco_webserver() = default;
    virtual ~falco_webserver();
    
    virtual void start(const falco::app::state& state,
                      const falco_configuration::webserver_config& config);  // 行 40-41
    virtual void stop();                                                   // 行 42
    virtual void enable_prometheus_metrics(const falco::app::state& state); // 行 43

private:
    bool m_running = false;                          // 行 46
    std::unique_ptr<httplib::Server> m_server;     // 行 47
    std::thread m_server_thread;                    // 行 48
    std::atomic<bool> m_failed;                    // 行 49
};
```

### 6.3 端点

| 端点 | 路径 | 行 | 输出 |
|------|------|-----|------|
| 健康检查 | `/healthz` (可配置) | 48-52 | `{"status": "ok"}` |
| 版本信息 | `/versions` | 54-59 | JSON版本信息 |
| Prometheus指标 | `/metrics` | 104-112 | Prometheus文本格式 |

### 6.4 线程安全

| 机制 | 位置 | 用途 |
|------|------|------|
| `std::atomic<bool> m_failed` | webserver.h:49 | 跟踪服务器失败状态 |
| `m_running` 标志 | webserver.h:46 | 防止重复启动 |
| Move/Copy删除 | webserver.h:36-39 | 防止竞态 |
| 线程join | webserver.cpp:96-98 | 确保干净关闭 |

---

## 7. stats_writer 模块 - 统计收集

**文件路径**: `userspace/falco/stats_writer.{h,cpp}`

### 7.1 文件信息

| 定义 | 文件 | 行 |
|------|------|-----|
| `stats_writer` 类 | `stats_writer.h` | 38-167 |
| `collector` 内部类 | `stats_writer.h` | 51-93 |
| `msg` 结构体 | `stats_writer.h` | 132-143 |
| `worker()` | `stats_writer.cpp` | 230-275 |
| `collector::collect()` | `stats_writer.cpp` | 612-675 |

### 7.2 `stats_writer` 类 (`stats_writer.h:38-167`)

```cpp
class stats_writer {
public:
    class collector { /* ... */ };  // 行 51-93: 每个线程的收集器
    
    stats_writer(const std::shared_ptr<falco_outputs>& outputs,
                 const std::shared_ptr<const falco_configuration>& config,
                 const std::shared_ptr<const falco_engine>& engine);  // 行 108-110
    
    bool has_output() const { return m_initialized; }  // 行 115
    static bool init_ticker(uint32_t interval_msec, std::string& err);  // 行 123
    static ticker_t get_ticker();                      // 行 129

private:
    void worker() noexcept;              // 行 145
    void stop_worker();                 // 行 146
    void push(const msg& m);           // 行 147
    
    bool m_initialized = false;         // 行 149
    tbb::concurrent_bounded_queue<msg> m_queue;  // 行 154: TBB队列
    std::thread m_worker;               // 行 151: 工作线程
};
```

### 7.3 收集的指标

#### A. Falco包装器指标 (`get_metrics_output_fields_wrapper()`, 行 331-411)

| 指标 | 描述 |
|------|------|
| `evt.time` | 快照时间戳 |
| `falco.reload_ts` | Falco重载时间戳 |
| `falco.version` | Falco版本 |
| `falco.duration_sec` | 运行时长 |
| `scap.engine_name` | 驱动名称 |
| `falco.evts_rate_sec` | 用户空间事件处理速率 |
| `falco.num_evts` | 总事件数 |
| `falco.outputs_queue_num_drops` | 输出队列丢弃数 |

#### B. 额外指标 (`get_metrics_output_fields_additional()`, 行 413-610)

| 类别 | 指标 |
|------|------|
| 规则计数器 | `falco.rules.matches_total`, `falco.rules.<rule_name>` |
| Jemalloc统计 | `falco.jemalloc.<stat_name>_bytes` |
| Libs指标 | `scap.n_evts`, `scap.n_drops`, `scap.n_drops_perc` |

### 7.4 线程安全

| 机制 | 位置 | 用途 |
|------|------|------|
| `static atomic<ticker_t> s_timer` | stats_writer.cpp:44 | 跨线程安全计时器 |
| `tbb::concurrent_bounded_queue` | stats_writer.h:154 | 线程安全队列 |
| `collector` 非线程安全 | stats_writer.h:49注释 | 每线程独立实例 |

---

## 8. falco_engine 模块 - 核心引擎

**文件路径**: `userspace/engine/falco_engine.{h,cpp}`

### 8.1 文件信息

| 文件 | 行数 |
|------|------|
| `falco_engine.h` | 493 |
| `falco_engine.cpp` | 1012 |

### 8.2 主类: `falco_engine` (`falco_engine.h:45-493`)

### 8.3 公共方法一览

| 方法 | 行 | 签名 |
|------|-----|------|
| `load_rules` | 85-86 | `unique_ptr<load_result> load_rules(const string&, const string&)` |
| `enable_rule` (子串) | 97-99 | `void enable_rule(const string&, bool, const string& ruleset)` |
| `enable_rule_by_tag` | 125-127 | `void enable_rule_by_tag(const set<string>&, bool, const string&)` |
| `process_event` | 262-265 | `unique_ptr<vector<rule_result>> process_event(size_t, sinsp_evt*, uint16_t, rule_matching)` |
| `add_source` | 281-283 | `size_t add_source(const string&, shared_ptr<filter_factory>, shared_ptr<formatter_factory>)` |
| `set_min_priority` | 145 | `void set_min_priority(priority_type)` |
| `find_ruleset_id` | 153 | `uint16_t find_ruleset_id(const string&)` |
| `list_fields` | 66-69 | `void list_fields(const string&, bool, bool, output_format) const` |

### 8.4 内部字段 (`falco_engine.h:384-492`)

```cpp
indexed_vector<falco_source> m_sources;              // 行 386: 事件源
indexed_vector<falco_rule> m_rules;                  // 行 453: 所有规则
shared_ptr<rule_loader::reader> m_rule_reader;       // 行 454: 规则读取器
shared_ptr<rule_loader::collector> m_rule_collector;  // 行 455: 规则收集器
shared_ptr<rule_loader::compiler> m_rule_compiler;    // 行 456: 规则编译器
stats_manager m_rule_stats_manager;                   // 行 457: 统计管理器
uint16_t m_next_ruleset_id;                           // 行 459: 下一个规则集ID
map<string, uint16_t> m_known_rulesets;              // 行 460: 已知规则集
priority_type m_min_priority;                         // 行 461: 最低优先级
uint32_t m_sampling_ratio;                            // 行 485: 采样比
double m_sampling_multiplier;                          // 行 486: 采样乘数
```

### 8.5 `rule_result` 结构 (`falco_engine.h:225-236`)

```cpp
struct rule_result {
    sinsp_evt *evt;                           // 行 226
    std::string rule;                         // 行 227
    std::string source;                       // 行 228
    priority_type priority_num;               // 行 229
    std::string format;                       // 行 230
    std::set<std::string> exception_fields;  // 行 231
    std::set<std::string> tags;              // 行 232
    extra_output_field_t extra_output_fields; // 行 233
    bool capture;                             // 行 234
    uint64_t capture_duration_ns;            // 行 235
};
```

### 8.6 `priority_type` 枚举 (`falco_common.h:50-59`)

```cpp
enum priority_type {
    PRIORITY_EMERGENCY = 0,       // 最高
    PRIORITY_ALERT = 1,
    PRIORITY_CRITICAL = 2,
    PRIORITY_ERROR = 3,
    PRIORITY_WARNING = 4,
    PRIORITY_NOTICE = 5,
    PRIORITY_INFORMATIONAL = 6,
    PRIORITY_DEBUG = 7            // 最低
};
```

### 8.7 事件处理流程

```
process_event(source_idx, ev, ruleset_id, strategy)
    │
    ├─→ find_source(source_idx)     // O(1) 源查找
    │
    ├─→ should_drop_evt()           // 随机采样检查
    │                                  (使用 m_sampling_ratio, m_sampling_multiplier)
    │
    └─→ source->ruleset->run(ev, rules, ruleset_id)
            │
            └─→ evttype_index_ruleset::run_wrappers()
                    │
                    ├─→ O(1) 事件类型查找
                    │      m_filter_by_event_type[evt->get_type()]
                    │
                    └─→ 线性搜索过滤包装器
                            filter->run(evt)
```

---

## 9. rule_loader 模块 - 规则加载

**文件路径**: `userspace/engine/rule_loader*.{h,cpp}`

### 9.1 文件概览

| 文件 | 行数 |
|------|------|
| `rule_loader.h` | 546 |
| `rule_loader.cpp` | 548 |
| `rule_loader_reader.h` | 82 |
| `rule_loader_reader.cpp` | 1026 |
| `rule_loader_collector.h` | 111 |
| `rule_loader_collector.cpp` | 356 |
| `rule_loader_compiler.h` | 89 |
| `rule_loader_compiler.cpp` | 585 |

### 9.2 三阶段管道

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  rule_loader_    │ ──▶ │  rule_loader_     │ ──▶ │  rule_loader_    │
│  reader         │     │  collector         │     │  compiler        │
│                  │     │                  │     │                  │
│  YAML 解析       │     │  收集定义          │     │  编译为可执行格式  │
│  输出: info 结构  │     │  输出: indexed_vec │     │  输出: compile_out │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### 9.3 Reader 阶段 (`rule_loader_reader.cpp`)

**主要方法**: `read_item()` (行 443-965)

处理 YAML 项目类型:
- `required_engine_version` (行 455-483)
- `required_plugin_versions` (行 484-545)
- `list` (行 546-596)
- `macro` (行 597-653)
- `rule` (行 654-958)

### 9.4 Collector 阶段 (`rule_loader_collector.h:29-109`)

```cpp
class collector {
    // 状态
    indexed_vector<rule_info> m_rule_infos;    // 行 144
    indexed_vector<macro_info> m_macro_infos;   // 行 145
    indexed_vector<list_info> m_list_infos;     // 行 146
    
    // 定义方法
    void define(configuration&, engine_version_info&);  // 行 74
    void define(configuration&, list_info&);              // 行 76
    void define(configuration&, macro_info&);            // 行 77
    void define(configuration&, rule_info&);             // 行 78
    
    // 追加方法
    void append(configuration&, list_info&);              // 行 85
    void append(configuration&, macro_info&);            // 行 86
};
```

### 9.5 关键信息结构

#### `rule_info` (`rule_loader.h:482-509`)
```cpp
struct rule_info {
    context ctx;                          // 上下文
    context cond_ctx;                     // 条件上下文
    size_t index;                        // 索引
    size_t visibility;                    // 可见性
    std::string name;                    // 规则名
    std::string cond;                    // 条件表达式
    std::string source;                  // 事件源
    std::set<std::string> tags;         // 标签
    std::vector<rule_exception_info> exceptions;  // 例外
    priority_type priority;               // 优先级
    bool enabled;                        // 是否启用
};
```

#### `macro_info` (`rule_loader.h:421-435`)
```cpp
struct macro_info {
    context ctx;         // 上下文
    context cond_ctx;    // 条件上下文
    size_t index;
    size_t visibility;
    std::string name;
    std::string cond;   // 条件表达式
};
```

#### `list_info` (`rule_loader.h:403-416`)
```cpp
struct list_info {
    context ctx;
    size_t index;
    size_t visibility;
    std::string name;
    std::vector<std::string> items;  // 列表项
};
```

### 9.6 Compiler 阶段 (`rule_loader_compiler.cpp`)

**主方法**: `compile()` (行 557-585)
```cpp
void compiler::compile(configuration& cfg, 
                       const collector& col, 
                       compile_output& out) const {
    compile_list_infos(cfg, col, out.lists);           // 行 558
    compile_macros_infos(cfg, col, out.lists, out.macros);  // 行 559
    compile_rule_infos(cfg, col, out.lists, out.macros, out.rules);  // 行 560
}
```

**关键辅助方法**:
- `resolve_list()` (行 175-231) - 列表引用解析
- `resolve_macros()` (行 233-266) - 宏解析
- `parse_condition()` (行 269-289) - 条件解析

---

## 10. filter_ruleset 模块 - 规则集

**文件路径**: `userspace/engine/filter_ruleset.{h,cpp}`, `indexable_ruleset.{h}`, `evttype_index_ruleset.{h,cpp}`

### 10.1 文件概览

| 文件 | 行数 |
|------|------|
| `filter_ruleset.h` | 220 |
| `indexable_ruleset.h` | 373 |
| `evttype_index_ruleset.h` | 84 |
| `evttype_index_ruleset.cpp` | 86 |

### 10.2 类层次

```
filter_ruleset (抽象接口, filter_ruleset.h:32)
    └── indexable_ruleset<filter_wrapper> (模板基类, indexable_ruleset.h:46)
            └── evttype_index_ruleset (高性能实现, evttype_index_ruleset.h:43)
```

### 10.3 `filter_ruleset` 抽象接口 (`filter_ruleset.h:32-210`)

```cpp
class filter_ruleset {
    // 规则管理
    virtual void add(const falco_rule&, shared_ptr<sinsp_filter>, 
                    shared_ptr<expr>) = 0;  // 行 62-64
    virtual void clear() = 0;               // 行 94
    virtual void on_loading_complete() = 0; // 行 100
    
    // 事件处理
    virtual bool run(sinsp_evt*, falco_rule&, uint16_t) = 0;       // 行 110
    virtual bool run(sinsp_evt*, vector<falco_rule>&, uint16_t) = 0;  // 行 120
    
    // 启用/禁用
    virtual void enable(const string&, match_type, uint16_t) = 0;   // 行 165
    virtual void disable(const string&, match_type, uint16_t) = 0;  // 行 180
    virtual void enable_tags(const set<string>&, uint16_t) = 0;    // 行 193
    virtual void disable_tags(const set<string>&, uint16_t) = 0;   // 行 206
    
    // 查询
    virtual uint64_t enabled_count(uint16_t) = 0;                  // 行 126
    virtual libsinsp::events::set<ppm_sc_code> enabled_sc_codes(uint16_t) = 0;  // 行 143
    virtual libsinsp::events::set<ppm_event_code> enabled_event_codes(uint16_t) = 0;  // 行 150
};
```

### 10.4 `indexed_vector<T>` 模板 (`indexed_vector.h:28-122`)

O(1) 双重索引容器:

```cpp
template<typename T>
class indexed_vector {
    std::vector<T> m_entries;                               // 行 120: 线性存储
    std::unordered_map<std::string, size_t> m_index;       // 行 121: 字符串→索引映射
    
    virtual inline size_t insert(const T& entry, const string& index);  // 行 72-84
    virtual inline T* at(size_t id) const;                  // 行 90-95: O(1) 数字索引
    virtual inline T* at(const string& index) const;         // 行 101-107: O(1) 字符串索引
};
```

### 10.5 O(1) 事件类型索引

**`evttype_index_wrapper`** (`evttype_index_ruleset.h:31-41`)
```cpp
struct evttype_index_wrapper {
    falco_rule m_rule;                                    // 规则本身
    libsinsp::events::set<ppm_sc_code> m_sc_codes;       // 系统调用代码
    libsinsp::events::set<ppm_event_code> m_event_codes; // 事件代码
    shared_ptr<sinsp_filter> m_filter;                   // 编译后的过滤器
};
```

**事件类型索引** (`indexable_ruleset.h:236-251`)
```cpp
void add_filter(shared_ptr<filter_wrapper> wrap) {
    if(wrap->event_codes().empty()) {
        // 无事件代码 = 匹配所有事件
        add_wrapper_to_list(m_filter_all_event_types, wrap);
    } else {
        // 按事件类型索引
        for(auto &etype : wrap->event_codes()) {
            if(m_filter_by_event_type.size() <= etype) {
                m_filter_by_event_type.resize(etype + 1);
            }
            add_wrapper_to_list(m_filter_by_event_type[etype], wrap);
        }
    }
}
```

**O(1) 事件查找** (`indexable_ruleset.h:275-294`)
```cpp
bool run(indexable_ruleset &ruleset, sinsp_evt *evt, falco_rule &match) {
    // O(1) 查找: 直接数组访问
    if(evt->get_type() < m_filter_by_event_type.size() &&
       m_filter_by_event_type[evt->get_type()].size() > 0) {
        if(ruleset.run_wrappers(evt,
                                m_filter_by_event_type[evt->get_type()],
                                m_ruleset_id,
                                match)) {
            return true;
        }
    }
    // 回退到全事件过滤器
    // ...
}
```

---

## 11. filter_macro_resolver 模块 - 宏解析

**文件路径**: `userspace/engine/filter_macro_resolver.{h,cpp}`

### 11.1 文件信息

| 文件 | 行 |
|------|-----|
| `filter_macro_resolver.h` | 131 |
| `filter_macro_resolver.cpp` | 141 |

### 11.2 类定义 (`filter_macro_resolver.h:30-131`)

```cpp
class filter_macro_resolver {
public:
    bool run(shared_ptr<expr>& filter);                              // 行 42
    void set_macro(const string& name, 
                   const shared_ptr<expr>& macro);                  // 行 52-53
    
    // 获取解析结果
    const vector<value_info>& get_resolved_macros() const;  // 行 66
    const vector<value_info>& get_unknown_macros() const;   // 行 74
    const vector<value_info>& get_errors() const;           // 行 78

private:
    // 值信息: (名称, 位置) 对
    typedef pair<string, libsinsp::filter::ast::pos_info> value_info;  // 行 59
    
    // 宏定义: 名称 → AST
    typedef unordered_map<string, shared_ptr<expr>> macro_defs;  // 行 94
    
    // Visitor 实现
    struct visitor : public expr_visitor { /* ... */ };  // 行 97-125
    
    vector<value_info> m_errors;           // 错误
    vector<value_info> m_unknown_macros;   // 未解析的宏
    vector<value_info> m_resolved_macros;  // 已解析的宏
    macro_defs m_macros;                   // 宏定义
};
```

### 11.3 宏解析流程 (Visitor 模式)

**`run()` 方法** (行 23-35)
```cpp
bool run(shared_ptr<expr>& filter) {
    clear();                                    // 清除状态
    visitor v(m_errors, m_unknown_macros, m_resolved_macros, m_macros);
    filter->accept(&v);                        // 遍历 AST
    if(v.m_node_substitute) {
        filter = v.m_node_substitute;         // 应用替换
    }
    return !m_resolved_macros.empty();
}
```

**`visit(identifier_expr*)`** (行 112-141) - 关键解析逻辑
```
1. 在 m_macros 中查找标识符
2. 如果找到且不为空:
   a. 检查循环 (m_macros_path 中是否已存在)
   b. 如果有循环: 记录错误，标记为未知
   c. 否则: 克隆宏 AST，递归处理
   d. 记录到 resolved_macros
3. 如果未找到: 记录到 unknown_macros
```

---

## 12. formats 模块 - 格式化

**文件路径**: `userspace/engine/formats.{h,cpp}`

### 12.1 文件信息

| 文件 | 行 |
|------|-----|
| `formats.h` | 58 |
| `formats.cpp` | 197 |

### 12.2 类定义 (`formats.h:24-58`)

```cpp
class falco_formats {
public:
    falco_formats(shared_ptr<const falco_engine> engine,
                  bool json_include_output_property,
                  bool json_include_tags_property,
                  bool json_include_message_property,
                  bool json_include_output_fields_property,
                  bool time_format_iso_8601);  // 行 26-31
    
    // 格式化方法
    std::string format_event(sinsp_evt *evt, const std::string &rule, ...);  // 行 34-41
    std::string format_string(sinsp_evt *evt, const std::string &format, 
                              const std::string &source) const;  // 行 43-44
    std::map<std::string, std::string> get_field_values(sinsp_evt *evt, ...);  // 行 47-49

private:
    shared_ptr<const falco_engine> m_falco_engine;           // 行 51
    bool m_json_include_output_property;                     // 行 52
    bool m_json_include_tags_property;                       // 行 53
    bool m_json_include_message_property;                    // 行 54
    bool m_json_include_output_fields_property;              // 行 55
    bool m_time_format_iso_8601;                             // 行 56
};
```

### 12.3 格式化流程 (`format_event()`, 行 38-163)

1. **创建前缀格式** (行 49-54)
   - ISO8601: `"*%evt.time.iso8601: "`
   - 否则: `"*%evt.time: "`

2. **创建格式化器** (行 60-61)
   ```cpp
   auto prefix_formatter = m_falco_engine->create_formatter(source, prefix);
   auto message_formatter = m_falco_engine->create_formatter(source, output_format);
   ```

3. **格式化事件** (行 64-73)
   ```cpp
   prefix_formatter->tostring_withformat(evt, prefix, OF_NORMAL);
   message_formatter->tostring_withformat(evt, message, OF_NORMAL);
   ```

4. **JSON 输出** (行 75-158)
   - 构建 JSON 对象包含: `time`, `rule`, `priority`, `source`, `hostname`
   - 可选: `output`, `tags`, `message`, `output_fields`

### 12.4 格式字符串语法

- `*` 前缀: 标记字段应包含在 JSON `output_fields` 中
- 字段名: `%evt.time`, `%proc.name`, `%container.id`
- 示例: `"*%evt.time.iso8601: Critical"`, `"No *%proc.name in %container.id"`

---

## 13. 模块关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           main()                                         │
│                      falco.cpp:59                                       │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        app::run()                                       │
│                    app.cpp:56-106                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  Run Steps (28 actions):                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ load_config  │─▶│ load_plugins │─▶│init_inspectors│─▶│init_engine │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
│         │                                                      │        │
│         ▼                                                      ▼        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │select_sources│  │load_rules_   │  │ init_outputs │  │start_webserver│
│  │              │─▶│files         │─▶│              │─▶│             │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
│         │                                                      │        │
│         └──────────────────────────────────────────────────────┘        │
│                                 │                                       │
│                                 ▼                                       │
│                    ┌─────────────────────┐                             │
│                    │  process_events     │                             │
│                    │  (主事件处理循环)   │                             │
│                    └──────────┬──────────┘                             │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   sinsp         │  │  falco_engine   │  │  falco_outputs  │
│   (事件捕获)    │  │  (规则匹配)     │  │  (输出)         │
│  libsinsp       │  │                 │  │                 │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         │                    │                    │
         │         ┌──────────┴──────────┐        │
         │         │                     │        │
         │         ▼                     ▼        ▼
         │  ┌─────────────┐  ┌─────────────────────────┐
         │  │ rule_loader │  │    filter_ruleset      │
         │  │ (YAML→AST) │  │ (规则集管理)            │
         │  │             │  │                         │
         │  │ ┌───────┐  │  │ ┌───────────────────┐  │
         │  │ │reader │  │  │ │evttype_index_     │  │
         │  │ └───┬───┘  │  │ │ruleset (O(1查找) │  │
         │  │     ▼      │  │ └───────────────────┘  │
         │  │ ┌───────┐  │  │                         │
         │  │ │collector│ │  └─────────────────────────┘
         │  │ └───┬───┘  │            │
         │  │     ▼      │            ▼
         │  │ ┌───────┐  │  ┌─────────────────┐
         │  │ │compiler│  │  │filter_macro_   │
         │  │ └───────┘  │  │resolver        │
         │  └─────────────┘  └─────────────────┘
         │
         ▼
┌─────────────────┐
│   libscap       │
│   (内核接口)    │
└─────────────────┘
```

---

## 14. 数据流

### 14.1 事件处理数据流

```
┌─────────────────────────────────────────────────────────────────┐
│                      内核/事件源                                  │
│   (syscall, k8s_audit, 插件)                                   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    sinsp (inspector)                            │
│              事件捕获和预处理                                    │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ open() / next_event()                                  │   │
│  │ - open_kmod()        内核模块                          │   │
│  │ - open_modern_bpf()  现代 eBPF                         │   │
│  │ - open_nodriver()    无驱动                            │   │
│  │ - open_plugin()      插件源                            │   │
│  │ - open(capture_file) 离线回放                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      falco_engine                               │
│                                                              │
│  process_event(source_idx, evt, ruleset_id, strategy)         │
│         │                                                     │
│         ├─ find_source()  ──────────────────────▶ O(1) 查找    │
│         │                                                     │
│         ├─ should_drop_evt()  ─────────────────▶ 随机采样     │
│         │                                                     │
│         └─ ruleset->run()  ────────────────────▶ 规则匹配    │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ evttype_index_ruleset::run()                          │   │
│  │   │                                                   │   │
│  │   ├─ O(1) 事件类型查找:                               │   │
│  │   │   m_filter_by_event_type[evt->get_type()]        │   │
│  │   │                                                   │   │
│  │   └─ 线性搜索过滤器列表:                              │   │
│  │       for(wrap : wrappers) {                          │   │
│  │           if(wrap->m_filter->run(evt)) {              │   │
│  │               matches.push_back(wrap->m_rule);         │   │
│  │           }                                           │   │
│  │       }                                               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      falco_outputs                              │
│                                                              │
│  handle_event(evt, rule, source, priority, format, tags)      │
│         │                                                     │
│         ├─ falco_formats::format_event()  ─────────────────▶ │
│         │   格式化输出字符串或JSON                             │
│         │                                                     │
│         └─ push(ctrl_msg)  ──────────▶ TBB 并发队列           │
│                                          │                      │
│                                          ▼                      │
│                              ┌─────────────────────┐             │
│                              │  worker 线程       │             │
│                              │  (从队列弹出)      │             │
│                              └──────────┬──────────┘             │
│                                         │                        │
│                    ┌────────────────────┼────────────────────┐    │
│                    ▼                    ▼                    ▼    │
│           ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│           │ output_stdout│  │ output_syslog│  │ output_http  │  │
│           └──────────────┘  └──────────────┘  └──────────────┘  │
│           ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│           │ output_file  │  │output_program│  │   ...       │  │
│           └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 14.2 规则加载数据流

```
┌─────────────────────────────────────────────────────────────────┐
│                      YAML 规则文件                               │
│   - rules_file: [...]                                           │
│   - rule: { name: ..., condition: ..., output: ... }           │
│   - macro: { name: ..., condition: ... }                       │
│   - list: { name: ..., items: [...] }                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   rule_loader::reader                           │
│                 read_item()                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ YAML::Node ──▶ rule_info / macro_info / list_info      │    │
│  │              (带上下文 context)                         │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  rule_loader::collector                         │
│                 define() / append()                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ indexed_vector<rule_info>    m_rule_infos              │    │
│  │ indexed_vector<macro_info>   m_macro_infos            │    │
│  │ indexed_vector<list_info>   m_list_infos              │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  rule_loader::compiler                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ compile_list_infos()                                   │    │
│  │   list_info ──▶ falco_list (展开嵌套列表)              │    │
│  │                                                        │    │
│  │ compile_macros_infos()                                 │    │
│  │   macro_info ──▶ falco_macro                           │    │
│  │   1. parse_condition() → AST                            │    │
│  │   2. resolve_macros() (filter_macro_resolver)          │    │
│  │                                                        │    │
│  │ compile_rule_infos()                                   │    │
│  │   rule_info ──▶ falco_rule                             │    │
│  │   1. 构建异常条件                                       │    │
│  │   2. compile_condition() → sinsp_filter                │    │
│  │   3. 提取事件类型/SC代码                               │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      falco_engine                               │
│                                                              │
│  indexed_vector<falco_source> m_sources                       │
│  indexed_vector<falco_rule> m_rules                           │
│                                                              │
│  engine.add_source(name, factory, formatter, ruleset_factory) │
│         │                                                     │
│         └─▶ 创建 evttype_index_ruleset                       │
│                                                              │
│  load_rules() ──▶ 添加规则到规则集                             │
│         │                                                     │
│         └─▶ ruleset.add(rule, filter, condition_ast)          │
│                  │                                             │
│                  └─▶ 按事件类型索引:                           │
│                      m_filter_by_event_type[evt_type].push()   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 附录: 关键行号索引

### app 模块
| 定义 | 文件:行 |
|------|---------|
| `state` 结构体 | `state.h:45-165` |
| `run()` 方法 | `app.cpp:56-106` |
| `run_result` | `run_result.h:25-79` |
| `source_info` | `state.h:47-61` |

### configuration 模块
| 定义 | 文件:行 |
|------|---------|
| `falco_configuration` 类 | `configuration.h:50` |
| `plugin_config` | `configuration.h:52-57` |
| `webserver_config` | `configuration.h:79-87` |
| `engine_kind_t` | `configuration.h:43` |
| `load_yaml()` | `configuration.cpp:283-697` |

### outputs 模块
| 定义 | 文件:行 |
|------|---------|
| `abstract_output` | `outputs.h:58-93` |
| `falco_outputs` | `falco_outputs.h:41-134` |
| `message` 结构 | `outputs.h:43-51` |
| TBB 队列 | `falco_outputs.cpp:255-269` |

### falco_engine 模块
| 定义 | 文件:行 |
|------|---------|
| `falco_engine` 类 | `falco_engine.h:45-493` |
| `rule_result` | `falco_engine.h:225-236` |
| `priority_type` | `falco_common.h:50-59` |
| `process_event()` | `falco_engine.cpp:371-432` |

### rule_loader 模块
| 定义 | 文件:行 |
|------|---------|
| `rule_info` | `rule_loader.h:482-509` |
| `macro_info` | `rule_loader.h:421-435` |
| `list_info` | `rule_loader.h:403-416` |
| `reader::read_item()` | `rule_loader_reader.cpp:443-965` |
| `compiler::compile()` | `rule_loader_compiler.cpp:557-585` |

### filter_ruleset 模块
| 定义 | 文件:行 |
|------|---------|
| `filter_ruleset` | `filter_ruleset.h:32-210` |
| `indexable_ruleset` | `indexable_ruleset.h:46-372` |
| `evttype_index_ruleset` | `evttype_index_ruleset.h:43-71` |
| `indexed_vector` | `indexed_vector.h:28-122` |
| O(1) 事件查找 | `indexable_ruleset.h:275-294` |

### filter_macro_resolver 模块
| 定义 | 文件:行 |
|------|---------|
| `filter_macro_resolver` | `filter_macro_resolver.h:30-131` |
| `value_info` | `filter_macro_resolver.h:59` |
| `run()` | `filter_macro_resolver.cpp:23-35` |
| `visit(identifier_expr*)` | `filter_macro_resolver.cpp:112-141` |

### formats 模块
| 定义 | 文件:行 |
|------|---------|
| `falco_formats` | `formats.h:24-58` |
| `format_event()` | `formats.cpp:38-163` |
| 格式字符串语法 | `formats.cpp:49-73` |

---

*文档生成时间: 2026-04-26*
*基于 Falco 代码库深入分析*

---

## 附录 B: falcosecurity-libs 外部依赖分析

**位置**: 通过 CMake ExternalProject 引入，非本地源码

### B.1 libsinsp 使用分析

#### 主要头文件包含

| 头文件 | 用途 | 使用位置 |
|--------|------|----------|
| `<libsinsp/sinsp.h>` | 主检查器类、事件捕获 | `state.h:30`, `stats_writer.h:24`, `init_inspectors.cpp` |
| `<libsinsp/event.h>` | 事件类型和工具 | `options.h:20`, `event_formatter.cpp` |
| `<libsinsp/plugin.h>` | 插件接口和能力 | `falco_engine.cpp:36`, `load_plugins.cpp` |
| `<libsinsp/filter.h>` | 过滤器工厂和类 | `filter_ruleset.h:22-24` |
| `<libsinsp/filter/ast.h>` | 过滤器 AST 表达式 | `filter_ruleset.h:22` |
| `<libsinsp/events/sinsp_events.h>` | 事件集工具 | `filter_ruleset.h:24` |

#### sinsp 类使用

**Inspector 创建** (`init_inspectors.cpp:108-113`):
```cpp
if(is_capture_mode) {
    src_info->inspector = s.offline_inspector;
} else {
    src_info->inspector = std::make_shared<sinsp>(s.config->m_metrics_flags & METRICS_V2_STATE_COUNTERS);
}
```

**Inspector 配置** (`init_inspectors.cpp:29-51`):
```cpp
inspector->set_buffer_format(event_buffer_format);     // 行 35: 缓冲区格式
inspector->set_snaplen(s.config->m_falco_libs_snaplen);  // 行 41: 快照长度
inspector->set_dropfailed(true);                       // 行 47: 丢弃失败配置
inspector->set_hostname_and_port_resolution_mode(false); // 行 50: 主机名解析
```

**插件注册** (`load_plugins.cpp:46-50`):
```cpp
s.offline_inspector = std::make_shared<sinsp>();
auto plugin = s.offline_inspector->register_plugin(p.m_library_path);
```

#### ppm_sc_code 和 ppm_event_code 使用

**系统调用代码** (`evttype_index_ruleset.cpp:37`):
```cpp
wrap->m_sc_codes = libsinsp::filter::ast::ppm_sc_codes(condition.get());
```

**事件代码** (`evttype_index_ruleset.cpp:41-43`):
```cpp
wrap->m_event_codes = {ppm_event_code::PPME_PLUGINEVENT_E};
wrap->m_event_codes.insert(ppm_event_code::PPME_ASYNCEVENT_E);
```

**忽略的系统调用集** (`app.cpp:29-35`):
```cpp
libsinsp::events::set<ppm_sc_code> falco::app::ignored_sc_set() {
    return libsinsp::events::io_sc_set().diff(libsinsp::events::sinsp_state_sc_set());
}
```

#### sinsp_filter 和 sinsp_filter_factory 使用

**工厂创建** (`init_falco_engine.cpp:111-112`):
```cpp
auto filter_factory = std::make_shared<sinsp_filter_factory>(inspector, filterchecks);
auto formatter_factory = std::make_shared<sinsp_evt_formatter_factory>(inspector, filterchecks);
```

**规则编译** (`rule_loader_compiler.cpp:381-383`):
```cpp
sinsp_filter_compiler compiler(filter_factory, ast_out.get());
filter_out = compiler.compile();
```

### B.2 libscap 使用分析

#### 主要头文件

| 头文件 | 用途 | 使用位置 |
|--------|------|----------|
| `<libscap/strl.h>` | 字符串工具 | `stats_writer.cpp:32` |
| `<libscap/scap_vtable.h>` | scap 虚表接口 | `stats_writer.cpp:33` |

#### scap_stats 使用

**统计收集** (`event_drops.h:58,67`):
```cpp
bool perform_actions(uint64_t now, const scap_stats &delta, bool bpf_enabled);
scap_stats m_last_stats;
```

**机器信息** (`stats_writer.cpp:342-343`):
```cpp
const scap_agent_info* agent_info = inspector->get_agent_info();
const scap_machine_info* machine_info = inspector->get_machine_info();
```

### B.3 falco_engine 与 libsinsp 的关系

```
┌─────────────────────────────────────────────────────────────┐
│                     falco_engine                            │
│  - 管理规则和规则集                                        │
│  - 处理事件并匹配规则                                      │
│  - 使用 libsinsp 的工厂创建过滤器                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ add_source()
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    sinsp_filter_factory                     │
│  - 基于 inspector 创建过滤器工厂                            │
│  - 管理过滤器检查列表                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ create_filter()
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      sinsp_filter                            │
│  - 编译后的过滤器对象                                      │
│  - 用于匹配事件                                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ run(evt)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       sinsp_evt                            │
│  - 来自内核的事件                                          │
│  - 被过滤器评估                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 附录 C: falcosecurity-rules 规则子模块分析

**位置**: `submodules/falcosecurity-rules/`

### C.1 子模块结构

```
submodules/falcosecurity-rules/
├── registry.yaml           # 规则文件注册表
├── rules/
│   ├── falco_rules.yaml           # 主规则 (1265行)
│   ├── falco-incubating_rules.yaml # 孵化规则 (1306行)
│   └── falco-sandbox_rules.yaml   # 沙盒规则 (1974行)
├── archive/
│   └── falco-deprecated_rules.yaml # 已废弃规则
├── docs/
├── build/
├── proposals/
└── tools/
```

### C.2 registry.yaml - 规则文件注册

**文件**: `submodules/falcosecurity-rules/registry.yaml`

```yaml
rulesfiles:
  - name: falco-rules              # 主要规则
    path: rules/falco_rules.yaml
    license: apache-2.0
  - name: falco-incubating-rules  # 孵化规则
    path: rules/falco-incubating_rules.yaml
  - name: falco-sandbox-rules      # 沙盒规则
    path: rules/falco-sandbox_rules.yaml
  - name: falco-deprecated-rules   # 已废弃规则
    path: archive/falco-deprecated_rules.yaml
```

### C.3 规则文件结构

#### 头部声明

```yaml
- required_engine_version: 0.57.0    # 要求的 Falco 引擎版本

- required_plugin_versions:           # 要求的插件版本
    - name: container
      version: 0.4.0
```

#### 宏定义 (macro)

```yaml
- macro: open_write
  condition: (evt.type in (open,openat,openat2) and evt.is_open_write=true and fd.typechar='f' and fd.num>=0)

- macro: shell_procs
  condition: (proc.name in (shell_binaries))
```

#### 列表定义 (list)

```yaml
- list: shell_binaries
  items: [ash, bash, csh, ksh, sh, tcsh, zsh, dash]

- list: http_server_binaries
  items: [nginx, httpd, httpd-foregroun, lighttpd, apache, apache2]
```

#### 规则定义 (rule)

```yaml
- rule: Directory traversal monitored file read
  desc: >
    Web applications can be vulnerable to directory traversal attacks...
  condition: >
    (open_read or open_file_failed)
    and (etc_dir or user_ssh_directory or
         fd.name startswith /root/.ssh or
         fd.name contains "id_rsa")
    and directory_traversal
    and not proc.pname in (shell_binaries)
  enabled: true
  output: Read monitored file via directory traversal | file=%fd.name ...
  priority: WARNING
  tags: [maturity_stable, host, container, filesystem, mitre_credential_access, T1555]
```

### C.4 规则标签体系

**成熟度标签**:
- `maturity_stable` - 稳定规则
- `maturity_incubating` - 孵化中规则
- `maturity_sandbox` - 沙盒规则

**工作负载标签**:
- `host` - 主机级别
- `container` - 容器级别

**MITRE ATT&CK 标签**:
- `mitre_credential_access` - 凭证访问
- `mitre_execution` - 执行
- `mitre_persistence` - 持久化
- `T1555` - 来自密码存储的凭证

### C.5 关键宏和列表示例

| 名称 | 类型 | 用途 |
|------|------|------|
| `open_write` | macro | 文件写操作 |
| `open_read` | macro | 文件读操作 |
| `sensitive_files` | macro | 敏感文件模式 |
| `shell_binaries` | list | Shell 程序列表 |
| `http_server_binaries` | list | HTTP 服务器列表 |
| `package_mgmt_binaries` | list | 包管理程序列表 |
| `user_mgmt_binaries` | list | 用户管理程序列表 |

### C.6 官方规则统计

| 规则文件 | 行数 | 说明 |
|----------|------|------|
| `falco_rules.yaml` | 1265 | 主要检测规则 |
| `falco-incubating_rules.yaml` | 1306 | 新兴/测试规则 |
| `falco-sandbox_rules.yaml` | 1974 | 实验性规则 |
| **总计** | 4545 | |

---

## 附录 D: CMake 构建配置

**位置**: `cmake/modules/`

### D.1 关键 CMake 模块

| 模块 | 用途 |
|------|------|
| `falcosecurity-libs-repo/` | libs 仓库配置 |
| `falcosecurity-libs.cmake` | libs 依赖配置 |
| `driver-repo/` | 内核驱动配置 |
| `driver.cmake` | 驱动依赖配置 |
| `yaml-cpp.cmake` | YAML 解析库 |
| `njson.cmake` | JSON 库 |
| `cpp-httplib.cmake` | HTTP 服务器库 |
| `curl.cmake` | HTTP 客户端库 |
| `openssl.cmake` | SSL/TLS 库 |

### D.2 外部依赖关系

```
Falco Build
    ├── falcosecurity-libs (ExternalProject)
    │   ├── libsinsp (事件检查)
    │   └── libscap (捕获接口)
    ├── yaml-cpp (YAML 解析)
    ├── nlohmann/json (JSON 处理)
    ├── cpp-httplib (HTTP 服务器)
    ├── curl (HTTP 客户端)
    └── openssl (SSL/TLS)
```
