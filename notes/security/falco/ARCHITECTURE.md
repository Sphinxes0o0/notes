# Falco 代码架构分析文档

## 1. 项目概述

### 1.1 项目定位

Falco 是一个云原生的运行时安全项目，作为 Kubernetes 的威胁检测引擎发挥作用。它通过监控系统调用(syscalls)和事件流，实时检测异常行为和安全威胁。

**核心定位**: 容器和 Kubernetes 环境下的运行时安全监控与威胁检测

### 1.2 核心功能

1. **系统调用监控**: 通过 KMOD (Kernel Module)、MODERN_EBPF (eBPF probe) 或插件驱动采集系统事件
2. **规则引擎**: 灵活可扩展的规则定义系统，支持 YAML 格式规则文件
3. **告警输出**: 多输出渠道支持 (stdout, file, syslog, program, http)
4. **插件机制**: 支持第三方插件扩展事件源和字段提取能力
5. **配置热加载**: 支持配置文件变更自动重载和规则动态更新
6. **指标采集**: 完整的 Prometheus 指标暴露和统计信息收集

### 1.3 技术选型原因

| 技术选型 | 选择原因 |
|---------|---------|
| **C++ (userspace)** | 高性能、低延迟，满足实时事件处理需求 |
| **libsinsp (falcosecurity-libs)** | 成熟的事件采集和处理库，提供 sinsp inspector |
| **TBB concurrent_queue** | 高效的多生产者单消费者队列实现 |
| **yaml-cpp** | YAML 配置文件解析 |
| **nlohmann/json** | JSON 处理，用于规则格式和指标输出 |
| **eBPF** | 现代内核级事件采集，可编程、低开销 |
| **libscap/libspp** | 系统层面事件捕获库 |

---

## 2. 目录结构

```
falco/
├── userspace/
│   ├── engine/                    # 核心规则引擎
│   │   ├── falco_engine.h/cpp    # 引擎主入口
│   │   ├── falco_common.h       # 公共定义(优先级、规则匹配策略)
│   │   ├── falco_source.h        # 事件源结构
│   │   ├── falco_rule.h         # 规则结构定义
│   │   ├── filter_ruleset.h     # 规则集接口
│   │   ├── evttype_index_ruleset.h/cpp  # 事件类型索引规则集
│   │   ├── indexable_ruleset.h  # 可索引规则集模板
│   │   ├── indexed_vector.h      # O(1)索引向量
│   │   ├── rule_loader.h        # 规则加载器
│   │   ├── rule_loader_collector.h   # 规则收集器
│   │   ├── rule_loader_compiler.h   # 规则编译器
│   │   ├── rule_loader_compile_output.h  # 编译输出
│   │   ├── rule_loader_reader.h # 规则读取器
│   │   ├── filter_macro_resolver.h  # 宏解析器
│   │   ├── formats.h/cpp        # 格式化输出
│   │   ├── field_formatter.h    # 字段格式化器
│   │   └── ...其他辅助类
│   │
│   └── falco/                    # 主应用程序
│       ├── falco.cpp            # main()入口
│       ├── app/                 # 应用状态机
│       │   ├── app.h/cpp        # 应用主逻辑
│       │   ├── state.h          # 应用状态结构
│       │   ├── options.h        # 命令行选项
│       │   ├── run_result.h     # 运行结果封装
│       │   ├── signals.h        # 信号处理声明
│       │   ├── restart_handler.h # 热重启处理器
│       │   ├── actions/         # 具体操作实现
│       │   │   ├── actions.h    # 所有操作声明
│       │   │   ├── process_events.cpp  # 事件处理循环
│       │   │   ├── init_inspectors.cpp # 采集器初始化
│       │   │   ├── helpers.h/cpp # 辅助函数
│       │   │   └── ...其他action文件
│       │   └── ...
│       ├── configuration.h/cpp   # 配置管理
│       ├── falco_outputs.h/cpp  # 输出模块
│       ├── outputs.h            # 输出抽象基类
│       ├── outputs_file/stdout/syslog/program/http.cpp  # 具体输出实现
│       ├── event_drops.h/cpp   # 事件丢弃管理
│       ├── stats_writer.h/cpp   # 统计信息写入
│       ├── webserver.h/cpp     # 健康检查和指标HTTP服务
│       ├── watchdog.h           # 超时看门狗
│       ├── falco_semaphore.h   # 信号量实现
│       └── atomic_signal_handler.h  # 原子信号处理
│
├── config/                       # 配置文件
│   └── falco.yaml.defaults      # 默认配置
├── rules -> submodules/falcosecurity-rules/rules  # 规则链接
└── cmake/, CMakeLists.txt       # 构建配置
```

---

## 3. 核心模块深度分析

### 3.1 驱动接口 (KMOD/eBPF)

**架构概述**:
- Falco 不直接采集事件，而是委托给 **falcosecurity-libs** (libsinsp/libscap)
- 支持多种驱动模式: `kmod`, `modern_ebpf`, `nodriver`, `replay`

**关键文件**: `falco/app/actions/helpers_inspector.cpp`

```cpp
// 驱动选择逻辑
if(s.is_nodriver()) {
    inspector->open_nodriver();
} else if(s.is_modern_ebpf()) {
    inspector->open_modern_bpf(s.syscall_buffer_bytes_size,
                              s.config->m_modern_ebpf.m_cpus_for_each_buffer,
                              true,
                              s.selected_sc_set);
} else {  // KMOD (default)
    inspector->open_kmod(s.syscall_buffer_bytes_size, s.selected_sc_set);
}
```

**Syscall Buffer 配置**:
- `syscall_buffer_bytes_size`: 缓冲区大小
- `modern_ebpf.m_cpus_for_each_buffer`: 每个buffer对应的CPU数
- `selected_sc_set`: 预筛选的系统调用集合

### 3.2 规则引擎

#### 3.2.1 规则加载流程 (rule_loader)

**关键组件**:

1. **rule_loader::reader** (`rule_loader_reader.h`)
   - 读取 YAML 格式规则文件
   - 解析 rules, macros, lists, required_engine_version, required_plugin_versions

2. **rule_loader::collector** (`rule_loader_collector.h`)
   - 收集解析后的规则定义
   - 管理 `indexed_vector<rule_info>`, `indexed_vector<macro_info>`, `indexed_vector<list_info>`
   - 支持增量定义和覆盖

3. **rule_loader::compiler** (`rule_loader_compiler.h`)
   - 编译规则：宏展开、列表展开、异常处理
   - 调用 `filter_macro_resolver` 解析宏引用
   - 生成最终的 `compile_output` (包含编译后的 falco_rule)

**规则加载序列图**:
```
load_rules_files()
  -> falco_engine.load_rules()
    -> rule_loader.reader.read()      // 解析YAML
    -> rule_loader.collector.define() // 收集定义
    -> rule_loader.compiler.compile() // 编译
    -> ruleset.add_compile_output() // 添加到规则集
```

#### 3.2.2 filter_ruleset 和 evttype_index_ruleset

**filter_ruleset** 是规则集接口，定义:
- `add()` - 添加规则
- `enable()/disable()` - 启用/禁用规则
- `run()` - 事件匹配
- `enabled_sc_codes()/enabled_event_codes()` - 获取事件类型集合

**evttype_index_ruleset** 是高性能实现:

```cpp
// evttype_index_ruleset::add()
void evttype_index_ruleset::add(const falco_rule &rule,
                                 std::shared_ptr<sinsp_filter> filter,
                                 std::shared_ptr<libsinsp::filter::ast::expr> condition) {
    auto wrap = std::make_shared<evttype_index_wrapper>();
    wrap->m_rule = rule;
    wrap->m_filter = filter;
    if(rule.source == falco_common::syscall_source) {
        // 从AST提取系统调用代码和事件代码
        wrap->m_sc_codes = libsinsp::filter::ast::ppm_sc_codes(condition.get());
        wrap->m_event_codes = libsinsp::filter::ast::ppm_event_codes(condition.get());
    }
    add_wrapper(wrap);
}
```

**性能优化**: 通过 `ppm_sc_codes` 和 `ppm_event_codes` 从规则条件表达式中提取事件类型，构建索引，实现 O(1) 事件类型查找。

#### 3.2.3 indexable_ruleset 模板

`indexable_ruleset<filter_wrapper>` 是规则集的核心模板类:

```cpp
// 内部类 ruleset_filters
class ruleset_filters {
    // 按事件类型索引的过滤器向量
    std::vector<filter_wrapper_list> m_filter_by_event_type;
    // 适用于所有事件类型的过滤器
    filter_wrapper_list m_filter_all_event_types;
    // 所有过滤器集合
    std::set<std::shared_ptr<filter_wrapper>> m_filters;
};
```

**事件匹配流程**:
```cpp
bool run(indexable_ruleset &ruleset, sinsp_evt *evt, falco_rule &match) {
    // 1. 首先尝试事件类型特定过滤器
    if(evt->get_type() < m_filter_by_event_type.size() &&
       m_filter_by_event_type[evt->get_type()].size() > 0) {
        if(ruleset.run_wrappers(evt, m_filter_by_event_type[evt->get_type()], ...)) {
            return true;
        }
    }
    // 2. 然后尝试通用过滤器
    if(m_filter_all_event_types.size() > 0) {
        if(ruleset.run_wrappers(evt, m_filter_all_event_types, ...)) {
            return true;
        }
    }
    return false;
}
```

### 3.3 事件处理 (do_inspect / sinsp)

**主事件循环** (`process_events.cpp`):

```cpp
static falco::app::run_result do_inspect(
        falco::app::state& s,
        std::shared_ptr<sinsp> inspector,
        const std::string& source,
        ...) {
    inspector->start_capture();

    while(1) {
        rc = inspector->next(&ev);

        if(rc == SCAP_TIMEOUT) { /* 超时处理 */ continue; }
        if(rc == SCAP_FILTERED_EVENT) { continue; }
        if(rc == SCAP_EOF) { break; }
        if(rc != SCAP_SUCCESS) { return fatal(inspector->getlasterr()); }

        // 信号处理 (SIGINT/SIGHUP/SIGUSR1)
        if(falco::app::g_terminate_signal.triggered()) { /* 退出 */ break; }
        if(falco::app::g_restart_signal.triggered()) { /* 重启 */ break; }
        if(falco::app::g_reopen_outputs_signal.triggered()) { /* 重新打开输出 */ }

        // 丢包检测
        if(check_drops_and_timeouts && !sdropmgr.process_event(inspector, ev)) {
            return fatal("Drop manager internal error");
        }

        // 规则匹配
        auto res = s.engine->process_event(source_engine_idx, ev, s.config->m_rule_matching);
        if(res != nullptr) {
            for(auto& rule_res : *res) {
                // 输出告警
                s.outputs->handle_event(rule_res.evt, rule_res.rule, ...);
                // 捕获处理
                if(s.config->m_capture_enabled) { /* 写scap文件 */ }
            }
        }
    }
}
```

**多源事件处理**:
- 支持多个事件源并行处理 (syscall + plugin sources)
- 每个源有独立的 inspector 线程
- 使用 `falco::semaphore` 同步

### 3.4 输出模块 (falco_outputs 多生产者单消费者)

**架构**:

```
handle_event() / handle_msg()
        |
        v
   try_push() to concurrent_bounded_queue
        |
        v
   worker_thread (单消费者)
        |
        v
   process_msg() -> outputs[i]->output()
                    (file, stdout, syslog, program, http)
```

**关键设计**:

```cpp
class falco_outputs {
    // TBB 有界队列作为多生产者-单消费者通道
    typedef tbb::concurrent_bounded_queue<ctrl_msg> falco_outputs_cbq;
    falco_outputs_cbq m_queue;

    // 单个工作线程
    std::thread m_worker_thread;

    // 控制消息类型
    enum ctrl_msg_type {
        CTRL_MSG_STOP = 0,
        CTRL_MSG_OUTPUT = 1,
        CTRL_MSG_CLEANUP = 2,
        CTRL_MSG_REOPEN = 3,
    };
};
```

**超时保护**: 使用 `watchdog<T>` 模板监控每个输出的处理时间

```cpp
void falco_outputs::worker() noexcept {
    watchdog<std::string> wd;
    wd.start([&](const std::string &payload) {
        falco_logger::log(falco_logger::level::CRIT,
                          "\"" + payload + "\" output timeout\n");
    });

    ctrl_msg cmsg;
    do {
        m_queue.pop(cmsg);  // 阻塞等待
        for(const auto &o : m_outputs) {
            wd.set_timeout(timeout, o->get_name());
            process_msg(o.get(), cmsg);
        }
    } while(cmsg.type != CTRL_MSG_STOP);
}
```

### 3.5 配置管理 (configuration)

**配置加载流程**:

```cpp
falco_configuration::init_from_file()
    -> load_from_file()           // 加载主配置
    -> merge_config_files()       // 合并include文件
    -> init_cmdline_options()     // 处理命令行 -o 选项
    -> load_yaml()                // 解析到结构体
```

**配置结构** (`configuration.h`):
- `engine_kind_t m_engine_mode`: kmod/modern_ebpf/replay/nodriver
- `kmod_config`, `modern_ebpf_config`: 驱动特定配置
- `webserver_config`: HTTP服务器配置
- `rule_selection_config`: 规则选择 (enable/disable by tag/rule)
- `append_output_config`: 输出追加配置
- `plugin_config`: 插件配置

**热加载**: 通过 `restart_handler` 监控配置文件变化

### 3.6 信号处理和状态机

**三种原子信号处理器**:

```cpp
// signals.h
extern atomic_signal_handler g_terminate_signal;   // SIGINT/SIGTERM
extern atomic_signal_handler g_restart_signal;     // SIGHUP
extern atomic_signal_handler g_reopen_outputs_signal;  // SIGUSR1
```

**atomic_signal_handler** 实现 (基于 std::atomic + std::mutex):

```cpp
class atomic_signal_handler {
    std::mutex m_mtx;
    std::atomic<bool> m_triggered{false};  // 信号已触发
    std::atomic<bool> m_handled{false};   // 信号已处理

    // 确保handle()回调只执行一次
    bool handle(std::function<void()> f) {
        if(triggered() && !handled()) {
            std::unique_lock<std::mutex> lock(m_mtx);
            if(!handled()) {
                f();
                m_handled.store(true, std::memory_order_seq_cst);
                return true;
            }
        }
        return false;
    }
};
```

**应用状态机** (`app.cpp`):

```cpp
// 运行步骤
std::list<app_action> const run_steps = {
    print_help, print_config_schema, print_rule_schema,  // 辅助信息
    load_config,           // 加载配置
    print_kernel_version, print_version, print_page_size,  // 版本信息
    require_config_file,   // 确保配置文件存在
    print_plugin_info, list_plugins,  // 插件信息
    load_plugins,          // 加载插件
    init_inspectors,       // 初始化采集器
    init_falco_engine,     // 初始化引擎
    list_fields,           // 列出字段
    select_event_sources,  // 选择事件源
    validate_rules_files,   // 验证规则
    load_rules_files,      // 加载规则
    print_support,         // 支持信息
    init_outputs,          // 初始化输出
    create_signal_handlers,  // 创建信号处理器
    pidfile,               // 写pid文件
    configure_interesting_sets,  // 配置系统调用集合
    configure_syscall_buffer_size,  // 配置缓冲区大小
    configure_syscall_buffer_num,   // 配置缓冲区数量
    start_webserver,       // 启动Web服务器
    process_events,         // 处理事件 (主要循环)
};

// 清理步骤
std::list<app_action> const teardown_steps = {
    unregister_signal_handlers,
    stop_webserver,
    cleanup_outputs,
    close_inspectors,
};
```

---

## 4. 关键数据结构

### 4.1 应用状态 (state)

```cpp
struct state {
    std::string cmdline;                          // 命令行
    falco::app::options options;                  // 解析后的选项
    std::atomic<bool> restart = false;            // 重启标志

    std::shared_ptr<falco_configuration> config;  // 配置
    std::shared_ptr<falco_outputs> outputs;       // 输出模块
    std::shared_ptr<falco_engine> engine;         // 规则引擎

    std::vector<std::string> loaded_sources;      // 已加载的事件源
    std::unordered_set<std::string> enabled_sources;  // 已启用的事件源

    std::shared_ptr<sinsp> offline_inspector;      // 离线采集器 (replay模式)

    indexed_vector<source_info> source_infos;      // 每个源的信息
    indexed_vector<falco_configuration::plugin_config> plugin_configs;  // 插件配置

    libsinsp::events::set<ppm_sc_code> selected_sc_set;  // 选中的系统调用
    uint64_t syscall_buffer_bytes_size;            // 系统调用缓冲区大小

    std::shared_ptr<restart_handler> restarter;   // 重启处理器

#if defined(__linux__) && !defined(__EMSCRIPTEN__) && !defined(MINIMAL_BUILD)
    falco_webserver webserver;                    // Web服务器
#endif
    std::function<void()> on_inspectors_opened;   // 采集器打开后的回调
};
```

### 4.2 falco_source

```cpp
struct falco_source {
    std::string name;                              // 源名称 (如 "syscall")
    std::shared_ptr<filter_ruleset> ruleset;       // 规则集
    std::shared_ptr<filter_ruleset_factory> ruleset_factory;  // 规则集工厂
    std::shared_ptr<sinsp_filter_factory> filter_factory;     // 过滤器工厂
    std::shared_ptr<sinsp_evt_formatter_factory> formatter_factory;  // 格式化工厂

    mutable std::vector<falco_rule> m_rules;        // 匹配的规则 (输出用)
};
```

### 4.3 falco_rule

```cpp
struct falco_rule {
    std::size_t id;                                // 规则ID
    std::string source;                             // 事件源
    std::string name;                              // 规则名
    std::string description;                       // 描述
    std::string output;                            // 输出格式
    extra_output_field_t extra_output_fields;      // 额外输出字段
    std::set<std::string> tags;                    // 标签
    std::set<std::string> exception_fields;        // 异常字段
    falco_common::priority_type priority;          // 优先级
    bool capture;                                   // 是否捕获
    uint32_t capture_duration;                     // 捕获持续时间
    std::shared_ptr<libsinsp::filter::ast::expr> condition;  // 条件AST
    std::shared_ptr<sinsp_filter> filter;          // 编译后的过滤器
};
```

### 4.4 rule_loader 相关结构

```cpp
// 规则信息
struct rule_info {
    context ctx, cond_ctx, output_ctx;
    size_t index, visibility;
    bool unknown_source;
    std::string name, cond, source, desc, output;
    std::set<std::string> tags;
    std::vector<rule_exception_info> exceptions;
    falco_common::priority_type priority;
    bool capture;
    uint32_t capture_duration;
    bool enabled, warn_evttypes, skip_if_unknown_filter;
};

// 宏信息
struct macro_info {
    context ctx, cond_ctx;
    size_t index, visibility;
    std::string name, cond;
};

// 列表信息
struct list_info {
    context ctx;
    size_t index, visibility;
    std::string name;
    std::vector<std::string> items;
};

// 异常条目
struct rule_exception_info::entry {
    bool is_list;
    std::string item;
    std::vector<entry> items;
};
```

### 4.5 evttype_index_wrapper

```cpp
struct evttype_index_wrapper {
    const std::string &name() { return m_rule.name; }
    const std::set<std::string> &tags() { return m_rule.tags; }
    const libsinsp::events::set<ppm_sc_code> &sc_codes() { return m_sc_codes; }
    const libsinsp::events::set<ppm_event_code> &event_codes() { return m_event_codes; }

    falco_rule m_rule;
    libsinsp::events::set<ppm_sc_code> m_sc_codes;    // 系统调用代码集合
    libsinsp::events::set<ppm_event_code> m_event_codes;  // 事件代码集合
    std::shared_ptr<sinsp_filter> m_filter;
};
```

---

## 5. 代码流程

### 5.1 启动到事件处理完整流程

```
main()
  |
  v
falco_run(argc, argv, restart)
  |
  v
falco::app::run()
  |
  +-> run_steps (按顺序执行)
  |   |
  |   +-> load_config          : 加载 falco.yaml
  |   +-> load_plugins         : 加载插件 (通过 libsinsp)
  |   +-> init_inspectors      : 初始化 sinsp 采集器
  |   +-> init_falco_engine    : 初始化规则引擎
  |   +-> load_rules_files      : 加载和编译规则
  |   +-> init_outputs         : 初始化输出模块 (启动worker线程)
  |   +-> create_signal_handlers : 注册信号处理器
  |   +-> configure_interesting_sets : 配置系统调用集合
  |   +-> start_webserver      : 启动HTTP健康检查服务器
  |   +-> process_events       : 事件处理主循环
  |
  +-> teardown_steps
      |
      +-> unregister_signal_handlers
      +-> stop_webserver
      +-> cleanup_outputs
      +-> close_inspectors
```

### 5.2 事件处理流程图

```
inspector->next(&ev)  返回 sinsp_evt*
        |
        v
   检查信号 (SIGINT/SIGHUP/SIGUSR1)
        |
        v
   syscall_evt_drop_mgr.process_event()  丢包检测
        |
        v
   falco_engine.process_event(source_idx, ev, ruleset_id)
        |
        +-> should_drop_evt()  采样判断
        |
        v
   ruleset->run(ev, matches, ruleset_id)
        |
        +-> 根据 ev->get_type() 查找 m_filter_by_event_type[index]
        |   |
        |   v
        |   evttype_index_ruleset::run_wrappers()
        |       |
        |       v
        |   wrap->m_filter->run(evt)  // 线性遍历
        |
        v
   对于每个匹配的 rule:
        |
        v
   outputs->handle_event()
        |
        v
   push(ctrl_msg) to TBB queue
        |
        v
   worker_thread 消费队列
        |
        v
   outputs[i]->output()  (多路输出)
```

---

## 6. 模块间依赖关系

```
                    +-----------------+
                    |    main()       |
                    |   falco.cpp    |
                    +--------|--------+
                             |
                             v
                    +-----------------+
                    |  falco::app    |
                    |    ::run()     |
                    +--------|--------+
                             |
        +---------------------+---------------------+
        |                     |                     |
        v                     v                     v
+---------------+    +----------------+    +----------------+
| configuration |    |  falco_engine  |    |  falco_outputs |
+---------------+    +----------------+    +----------------+
        |                     |                     |
        |                     |                     | (TBB queue)
        |                     |                     |
        v                     v                     v
+---------------+    +----------------+    +----------------+
|  yaml_helper  |    |  rule_loader   |    | abstract_output|
+---------------+    +----------------+    | (file/stdout/ |
        |                     |            |  syslog/http/ |
        |                     |            |   program)    |
        |                     |            +---------------+
        v                     v
+---------------+    +----------------+
|  rule_loader  |    | filter_ruleset |
| - reader      |    |    (iface)     |
| - collector   |    +--------|--------+
| - compiler    |             |
+---------------+             v
                    +--------------------+
                    | evttype_index_    |
                    | ruleset           |
                    +--------------------+
                             |
                             v
                    +--------------------+
                    | indexable_ruleset |
                    |   (template)      |
                    +--------------------+

    +----------------------------------------------------+
    |                    libsinsp                        |
    |  (from falcosecurity-libs submodule)              |
    +----------------------------------------------------+
    |  sinsp - 主Inspector类                             |
    |  sinsp_filter - 事件过滤器                         |
    |  sinsp_evt - 事件                                 |
    |  sinsp_plugin - 插件接口                           |
    +----------------------------------------------------+
```

---

## 7. 性能优化

### 7.1 事件类型索引

**原理**: 从规则条件表达式 AST 中提取 `ppm_sc_code` 和 `ppm_event_code`，构建索引

```cpp
// 从条件表达式提取事件类型
wrap->m_sc_codes = libsinsp::filter::ast::ppm_sc_codes(condition.get());
wrap->m_event_codes = libsinsp::filter::ast::ppm_event_codes(condition.get());

// 添加到索引
void add_filter(std::shared_ptr<filter_wrapper> wrap) {
    if(wrap->event_codes().empty()) {
        // 无特定事件类型 -> 通用过滤器
        add_wrapper_to_list(m_filter_all_event_types, wrap);
    } else {
        // 按事件类型索引
        for(auto &etype : wrap->event_codes()) {
            m_filter_by_event_type.resize(etype + 1);
            add_wrapper_to_list(m_filter_by_event_type[etype], wrap);
        }
    }
}
```

**效果**: 事件到达时，根据 `evt->get_type()` 直接索引，避免遍历所有规则

### 7.2 采样机制

```cpp
// should_drop_evt() in falco_engine
inline bool falco_engine::should_drop_evt() const {
    if(m_sampling_multiplier == 0) return false;  // 禁用采样
    if(m_sampling_ratio == 1) return false;        // 采样率=1不采样

    double coin = (random() * (1.0 / RAND_MAX));
    return (coin >= (1.0 / (m_sampling_multiplier * m_sampling_ratio)));
}
```

**采样率和采样乘数**:
- `sampling_ratio`: 外部因素（如内核丢包）影响的采样率
- `sampling_multiplier`: 额外的Falco层采样放大因子

### 7.3 批量处理和捕获

```cpp
// 规则匹配后
if(s.config->m_capture_enabled) {
    // 根据规则决定是否捕获
    if(capture_mode_t::RULES == s.config->m_capture_mode && rule_res.capture) {
        capture = true;
    }
    // 计算捕获截止时间
    auto evt_deadline_ts = ev->get_ts() +
        (rule_res.capture_duration_ns > 0 ? rule_res.capture_duration_ns
                                           : s.config->m_capture_default_duration_ns);
}

// 启动scap文件写入
if(capture && dump_started_ts == 0) {
    dumper->open(inspector.get(), generate_scap_file_path(...), true);
    dump_started_ts = ev->get_ts();
}

// 保存事件
if(dump_started_ts != 0) {
    dumper->dump(ev);
    if(ev->get_ts() > dump_deadline_ts) {
        dumper->flush();
        dumper->close();
        dump_started_ts = 0;
    }
}
```

### 7.4 系统调用集合预筛选

```cpp
// configure_interesting_sets
libsinsp::events::set<ppm_sc_code> falco::app::ignored_sc_set() {
    // 忽略高吞吐量的I/O syscall
    return libsinsp::events::io_sc_set().diff(libsinsp::events::sinsp_state_sc_set());
}
```

---

## 8. 插件机制

### 8.1 插件类型

Falco 插件有以下能力 (capabilities):
- `CAP_SOURCING`: 事件源插件，可生成事件流
- `CAP_EXTRACTION`: 字段提取插件，提供额外字段
- `CAP_PARSING`: 事件解析插件
- `CAP_ASYNC`: 异步事件插件

### 8.2 插件加载流程

```cpp
// init_inspectors.cpp
for(const auto& p : all_plugins) {
    std::shared_ptr<sinsp_plugin> plugin = nullptr;

    // 判断插件是否适合当前源
    bool is_input = (p->caps() & CAP_SOURCING) &&
                    ((p->id() != 0 && src == p->event_source()) ||
                     (p->id() == 0 && src == falco_common::syscall_source));

    if(is_input) {
        plugin = src_info->inspector->register_plugin(config->m_library_path);
    }

    if(plugin && (p->caps() & CAP_EXTRACTION)) {
        // 添加插件字段到 filterchecks
        filterchecks.add_filter_check(sinsp_plugin::new_filtercheck(plugin));
    }
}
```

### 8.3 插件在规则中的应用

```cpp
// 插件可提供:
// 1. 新的事件源 (CAP_SOURCING with id != 0)
// 2. 新字段 (CAP_EXTRACTION)
// 3. 异步事件 (CAP_ASYNC)
//
// 规则中可以引用这些字段和事件源
```

---

## 9. 代码亮点和设计模式

### 9.1 命令模式 + 状态机

应用主逻辑采用命令模式:

```cpp
typedef std::function<falco::app::run_result(falco::app::state&)> app_action;

std::list<app_action> const run_steps = {
    print_help, load_config, load_plugins, ...
};

// 执行
for(const auto& func : run_steps) {
    res = falco::app::run_result::merge(res, func(s));
    if(!res.proceed) break;
}
```

**优点**:
- 每个 action 独立，易于测试和维护
- 可插拔，可以添加/移除步骤
- 错误处理统一 (run_result)

### 9.2 模板方法模式

`indexable_ruleset<filter_wrapper>` 是模板方法模式的体现:

```cpp
template<class filter_wrapper>
class indexable_ruleset : public filter_ruleset {
    // 子类实现抽象方法
    virtual bool run_wrappers(sinsp_evt *evt, ...) = 0;

    // 通用逻辑
    bool run(sinsp_evt *evt, falco_rule &match, uint16_t ruleset_id) override {
        // 索引查找
        return m_rulesets[ruleset_id]->run(*this, evt, match);
    }
};
```

### 9.3 单生产者-多消费者队列

输出模块使用 TBB `concurrent_bounded_queue`:

```cpp
typedef tbb::concurrent_bounded_queue<ctrl_msg> falco_outputs_cbq;
falco_outputs_cbq m_queue;

// 生产者 (多线程)
void push(const ctrl_msg &cmsg) {
    if(!m_queue.try_push(cmsg)) {
        m_outputs_queue_num_drops++;  // 队列满丢包计数
    }
}

// 消费者 (单线程)
void worker() noexcept {
    ctrl_msg cmsg;
    do {
        m_queue.pop(cmsg);  // 阻塞
        for(const auto &o : m_outputs) {
            process_msg(o.get(), cmsg);
        }
    } while(cmsg.type != CTRL_MSG_STOP);
}
```

### 9.4 原子信号处理

确保信号处理在多线程环境中只执行一次:

```cpp
class atomic_signal_handler {
    // trigger() 可从信号处理程序调用
    // handle() 在主循环中调用
    bool handle(std::function<void()> f) {
        if(triggered() && !handled()) {
            std::unique_lock<std::mutex> lock(m_mtx);
            if(!handled()) {
                f();
                m_handled.store(true);
                return true;
            }
        }
        return false;
    }
};
```

### 9.5 indexed_vector - O(1) 双重索引

```cpp
template<typename T>
class indexed_vector {
    std::vector<T> m_entries;                    // 数值索引
    std::unordered_map<std::string, size_t> m_index;  // 字符串索引

    size_t insert(const T& entry, const std::string& index) {
        auto prev = m_index.find(index);
        if(prev != m_index.end()) {
            m_entries[prev->second] = entry;
            return prev->second;
        }
        size_t id = m_entries.size();
        m_entries.push_back(entry);
        m_index[index] = id;
        return id;
    }

    T* at(size_t id) const { ... }  // O(1)
    T* at(const std::string& index) const { ... }  // O(1)
};
```

### 9.6 watchdog 模板 - 超时监控

```cpp
template<typename _T>
class watchdog {
    void start(std::function<void(_T)> cb, std::chrono::milliseconds resolution);
    void set_timeout(std::chrono::milliseconds timeout, _T payload);
    void cancel_timeout();
};
```

用于监控输出处理和worker线程的阻塞情况。

### 9.7 观察者模式 - restart_handler

```cpp
class restart_handler {
    using on_check_t = std::function<bool()>;
    on_check_t m_on_check;

    void watcher_loop() noexcept {
        // 监控文件变化
        int fd = inotify_init();
        inotify_add_watch(fd, path, IN_MODIFY);

        while(!m_stop) {
            read(fd, ...);
            if(event && m_on_check()) {
                trigger();  // 触发重启
            }
        }
    }
};
```

---

## 10. 总结

Falco 的架构设计体现了以下特点:

1. **模块化**: 清晰的层次划分 (driver -> inspector -> engine -> outputs)
2. **高性能**: 事件类型索引、采样机制、TBB并发队列
3. **可扩展**: 插件机制、支持多种驱动
4. **可靠性**: 信号处理、watchdog超时、丢包检测
5. **易维护**: 命令模式、模板方法、清晰的数据结构

核心事件流: `驱动采集 → sinsp解析 → 规则引擎匹配 → 输出模块格式化 → 多路输出`

---

**文档版本**: 1.0
**分析日期**: 2026-04-11
**基于代码**: falco master branch
