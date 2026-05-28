---
type: source
source-type: github
title: "Snort3 Runtime Source"
author: "Cisco"
date: 2024-01-01
size: large
path: ~/workspace/github/snort3/src/
summary: "Snort3 runtime subsystems: managers (30), memory (12), profiler (30), latency (16), trace (15)"
---

# Snort3 Runtime Source

## 核心内容

分析 Snort3 `src/managers/`、`src/memory/`、`src/profiler/`、`src/latency/`、`src/trace/` 五个目录的源代码。

## 关键文件索引

### Managers（src/managers/ — 30文件）

| 文件 | 类型 | 描述 |
|---|---|---|
| `plugin_manager.cc/h` | 核心 | 集中式插件加载器；版本校验；API路由到各Manager |
| `inspector_manager.cc/h` | 核心 | Inspector工厂；二维索引（GLOBAL/CONTEXT/INSPECT × IT_NETWORK等） |
| `module_manager.cc/h` | 核心 | Module工厂；解析时创建，运行时提供参数表 |
| `ips_manager.cc/h` | 核心 | IPS选项插件工厂 |
| `codec_manager.cc/h` | 核心 | 协议解码器工厂 |
| `action_manager.cc/h` | 核心 | IPS动作工厂 |
| `mpse_manager.cc/h` | 核心 | 多模式搜索引擎工厂 |
| `event_manager.cc/h` | 核心 | 日志插件工厂 |
| `connector_manager.cc/h` | 核心 | Connector工厂 |
| `policy_selector_manager.cc/h` | 核心 | 多租户策略选择器 |
| `mp_transport_manager.cc/h` | 核心 | 多进程传输工厂 |
| `script_manager.cc/h` | 核心 | Lua脚本插件工厂 |
| `so_manager.cc/h` | 核心 | SO规则压缩/解压/加载器 |
| `coreinit.lua` | 配置 | 内置模块默认值 |

### Memory（src/memory/ — 12文件）

| 文件 | 类型 | 描述 |
|---|---|---|
| `memory_cap.cc/h` | 核心 | Memcap限制器；超限拒绝分配 |
| `memory_allocator.h` | 核心 | 分配器接口（仅MEMORY_PROFILER时编译） |
| `memory_module.cc/h` | 配置 | `memory`模块配置参数 |
| `memory_overloads.cc/h` | 核心 | 全局new/delete重载 |
| `heap_interface.cc/h` | 核心 | 堆接口抽象层 |

### Profiler（src/profiler/ — 30文件）

| 文件 | 类型 | 描述 |
|---|---|---|
| `time_profiler.cc/h` | 核心 | 模块时间profiler；TimeContext RAII |
| `time_profiler_defs.h` | 核心 | TimeProfilerStats结构；重入检测 |
| `memory_profiler.cc/h` | 核心 | 内存分配profiler |
| `rule_profiler.cc/h` | 核心 | 规则级profiler；checks/matches/alerts统计 |
| `profiler_nodes.cc/h` | 核心 | 性能数据树节点 |
| `profiler_tree_builder.cc/h` | 核心 | 从节点构建可打印树 |
| `profiler_printer.cc/h` | 核心 | ASCII表格打印框架 |
| `profiler_stats_table.cc/h` | 核心 | 统计表字段定义 |
| `table_view.cc/h` | 输出 | ASCII规则profiler表 |
| `json_view.cc/h` | 输出 | JSON规则profiler输出 |
| `profiler_module.cc/h` | 配置 | `profile-rules`/`profile-modules`模块 |

### Latency（src/latency/ — 16文件）

| 文件 | 类型 | 描述 |
|---|---|---|
| `packet_latency.cc/h` | 核心 | 包延迟监控；栈式计时器；fastpath支持 |
| `rule_latency.cc/h` | 核心 | 规则延迟监控；suspend/reenable机制 |
| `latency_module.cc/h` | 配置 | `latency`模块（GID=134事件） |
| `latency_timer.h` | 核心 | LatencyTimer模板 |
| `latency_stats.h` | 统计 | LatencyStats PegCount结构 |
| `packet_latency_config.h` | 配置 | PacketLatencyConfig |
| `rule_latency_config.h` | 配置 | RuleLatencyConfig |
| `rule_latency_state.h` | 状态 | RuleLatencyState（per-instance） |

### Trace（src/trace/ — 15文件）

| 文件 | 类型 | 描述 |
|---|---|---|
| `trace.cc/h` | 核心 | TraceLogger基类；日志输出接口 |
| `trace_api.cc/h` | 核心 | 运行时trace API |
| `trace_loggers.cc/h` | 核心 | Console/File/Syslog Logger实现 |
| `trace_module.cc/h` | 配置 | `trace`模块 |
| `trace_parser.cc/h` | 配置 | trace配置字符串解析 |
| `trace_swap.cc/h` | 核心 | 热更新（原子swap，无需加锁） |
| `trace_config.cc/h` | 配置 | TraceConfig结构 |

## 架构图

```
PluginManager (加载入口)
    │
    ├──> InspectorManager ──> Inspector (GLOBAL/CONTEXT/INSPECT)
    ├──> ModuleManager ──> Module
    ├──> IpsManager ──> IpsOption
    ├──> CodecManager ──> Codec
    ├──> ActionManager ──> IpsAction
    ├──> MpseManager ──> Mpse (搜索算法)
    ├──> EventManager ──> Logger
    ├──> ConnectorManager ──> Connector
    ├──> PolicySelectorManager ──> PolicySelector
    ├──> MPTransportManager ──> MPTransport
    ├──> ScriptManager ──> Lua脚本
    └──> SoManager ──> SO规则 (zlib+XOR压缩)

运行时可观测性:
    ├── Profiler ── TimeContext/MemoryContext/RuleContext
    ├── Latency ── PacketLatency/RuleLatency (栈式计时器)
    └── Trace ── TraceLogger (per-thread, 热更新)
```

## 配置接口

```bash
# Memory
--memory caps=1073741824

# Profiler
--profile-rules=total_time,100,5
--profile-modules=checks,50,3

# Latency
--latency packet max_time=500,fastpath=true
--latency rule max_time=500,suspend=true,suspend_threshold=5

# Trace
--trace "module_name:level"
```

## 事件ID（GID=134）

| SID | 事件 | 触发条件 |
|---|---|---|
| 1 | `rule tree suspended` | 规则评估连续超时达到threshold |
| 2 | `rule tree re-enabled` | 挂起超时后自动恢复 |
| 3 | `packet fastpathed` | 包处理超时且启用fastpath |

## 相关页面

- [[snort3-runtime]] — 运行时系统实体页
- [[snort3-stream-analysis]] — Stream TCP重组
- [[entities/linux/snort3/snort3-detection-engine]] — 规则检测引擎
