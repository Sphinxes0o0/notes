---
type: entity
tags: [snort3, intrusion-detection, network-security, packet-processing, rule-engine, memory-management, profiling, latency-monitoring, tracing]
created: 2026-05-27
sources: [github-snort3-runtime]
---

# Snort3 Runtime Systems

## 定义

Snort3 运行时核心子系统，包括 **管理器 (Managers)**、**内存 (Memory)**、**性能分析 (Profiler)**、**延迟监控 (Latency)**、**追踪 (Trace)** 五大模块。它们共同构成 Snort3 的运行时基础设施。

## 关键子系统

### 1. Managers（管理器系统）

**职责：** 插件生命周期管理 + 运行时对象工厂。

| Manager | 工厂对象 | 说明 |
|---|---|---|
| `PluginManager` | 所有插件 | 集中式插件加载（静态/动态/.so）、版本校验、API路由 |
| `InspectorManager` | `Inspector` | 包处理inspector实例化，支持GLOBAL/CONTEXT/INSPECT三种Usage |
| `ModuleManager` | `Module` | 配置模块管理，解析时创建，运行时提供参数表 |
| `IpsManager` | Ips选项 | IPS规则选项插件 |
| `CodecManager` | Codec | 协议解码器 |
| `ActionManager` | IpsAction | 告警/日志等响应动作 |
| `MpseManager` | Mpse | 多模式搜索算法引擎（AC等） |
| `EventManager` | Logger | 日志输出 |
| `ConnectorManager` | Connector | 数据连接器 |
| `PolicySelectorManager` | PolicySelector | 多租户策略选择 |
| `MPTransportManager` | MPTransport | 多进程传输 |
| `ScriptManager` | Lua脚本 | Lua插件（IpsOption/Logger） |
| `SoManager` | SO规则 | Shared Object规则编译/解压/加载 |

**关键设计模式：**
- 所有Manager都是**静态单例**（全局函数表），通过`add_plugin()`累积API
- 实例化时机：配置阶段`instantiate()`，不是加载阶段
- SO规则使用**zlib压缩 + XOR混淆**存储，运行时解密展开
- Inspector查询支持按`Usage`+`InspectorType`二维索引（GLOBAL/CONTEXT/INSPECT × IT_NETWORK/IT_STREAM/IT_SERVICE等）

**文件：** `src/managers/`（30文件）

### 2. Memory（内存系统）

**职责：** 内存分配管控 + memcap限制 + 可选profiler集成。

**核心组件：**

| 文件 | 职责 |
|---|---|
| `memory_cap.[h|cc]` | Memcap限制器：跟踪已分配字节数，超限则拒绝分配并告警 |
| `memory_allocator.h` | 分配器接口（`allocate()`/`deallocate()`），仅在`ENABLE_MEMORY_PROFILER`时编译 |
| `memory_module.[h|cc]` | 配置模块：`memory`命令行参数（cap、overload基础等） |
| `memory_overloads.[h|cc]` | 全局`new`/`delete`重载，可选集成profiler |
| `heap_interface.[h|cc]` | 堆接口抽象层 |

**Memcap机制：**
```cpp
// 全局已分配字节跟踪
static THREAD_LOCAL uint64_t allocated = 0;

// allocate时检查：allocated + req > cap → 拒绝
// deallocate时：allocated -= sz
```

**配置选项（`memory`模块）：**
- `caps` — 内存上限（字节）
- `overload_basic` — 是否启用基础重载

**文件：** `src/memory/`（12文件）

### 3. Profiler（性能分析系统）

**职责：** 运行时性能数据采集 + 多维度排序/输出。

**三种独立Profiler：**

#### 3a. Time Profiler
- 跟踪模块调用层级（父/子关系）
- `TimeContext` RAII wrapper自动计时，支持pause/resume
- `TimeExclude` 排除特定代码段不计入父时间
- 支持重入检测（`ref_count`）
- 排序维度：`checks` / `avg_check` / `total_time`

#### 3b. Memory Profiler
- 跟踪`new`/`delete`调用次数和字节数
- `MemoryContext` RAII wrapper
- 支持按allocation site记录（`active_context`）

#### 3c. Rule Profiler
- 按规则（GID:SID）统计检查次数、匹配次数、告警数、耗时
- 支持规则超时/挂起统计
- 两种输出视图：`table_view`（ASCII表）和`json_view`

**公共基础设施：**
- `profiler_nodes.[h|cc]` — 性能数据树节点
- `profiler_tree_builder.[h|cc]` — 从节点构建可打印树
- `profiler_printer.[h|cc]` — 表格打印框架
- `profiler_stats_table.[h|cc]` — ASCII统计表

**配置：**
```
--profile-rules=sort,count,max_depth  # 规则profiler
--profile-modules=sort,count,max_depth  # 模块profiler
```

**文件：** `src/profiler/`（30文件）

### 4. Latency（延迟监控系统）

**职责：** 检测包处理和规则评估是否超时，提供fastpath或suspend机制。

#### 4a. Packet Latency
- **栈式计时器**：每个packet context可嵌套push/pop
- `max_time`（默认500μs）：超时阈值
- `fastpath`模式：超时包直接跳过深度检测
- 超时时触发GID=134, SID=3事件
- 统计：`total_packets`、`total_usecs`、`max_usecs`、`packet_timeouts`

#### 4b. Rule Latency
- **栈式计时器**：规则树评估嵌套
- `max_time`（默认500μs）：单次规则评估超时
- `suspend`模式：连续超时达`threshold`次后挂起规则树
- `max_suspend_time`（默认30s）：挂起后自动恢复
- 超时时触发GID=134, SID=1（suspended）或SID=2（reenabled）事件
- 统计：`total_rule_evals`、`rule_eval_timeouts`、`rule_tree_enables`

**RuleLatencyState**（per-instance）：
```cpp
struct RuleLatencyState {
    hr_time suspend_time;  // 开始挂起时间
    unsigned timeouts = 0;  // 连续超时计数
    bool suspended = false;
    void enable();   // 重置计数器，取消挂起
    void suspend();  // 标记挂起
};
```

**文件：** `src/latency/`（16文件）

### 5. Trace（日志追踪系统）

**职责：** 运行时trace日志，支持trace level过滤、logga输出。

**架构：**

```
TraceLogger (基类)
  └── ConsoleLogger   — 输出到stdout
  └── FileLogger      — 输出到文件
  └── SyslogLogger    — 输出到syslog

TraceLoggerFactory — 每线程创建一个logger实例
TraceModule        — 配置模块（trace命令行参数）
TraceParser        — 解析trace配置字符串
TraceSwap          — 热更新trace配置（无需重启）
```

**日志输出API：**
```cpp
trace_logg(TRACE_LEVEL_INFO, trace, "format %d", args...);
// 或
debug_logf(trace, packet, "format %s\n", ...);
```

**TraceConstraints**（约束过滤）：
```cpp
struct TraceConstraints {
    uint8_t not_empty_flag;
    uint8_t ip_proto_mask;
    uint8_t ip_proto_match;
    uint8_t src_port_match;
    uint8_t dst_port_match;
    // 5-tuple级别精细过滤
};
```

**热更新机制（`trace_swap`）：** 配置变更时通过原子swap切换，无需加锁。

**文件：** `src/trace/`（15文件）

## 关键交叉引用

- [[snort3-stream]] — TCP重组依赖InspectorManager的stream inspector
- [[entities/linux/snort3/snort3-detection-engine]] — 规则评估使用Rule Profiler + Rule Latency
- [[snort3-packet-processing]] — Packet Latency在最外层包处理context中push/pop
- [[snort3-mempool]] — Memory系统与Flow缓存共享memcap配置
- [[snort3-inspectors]] — Inspector生命周期由InspectorManager管理

## 来源详情

- [[github-snort3-runtime]]
