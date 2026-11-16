---
type: entity
tags: [snort3, memory, memory-pool, allocator, performance]
created:2026-06-08
sources: [github-snort3-runtime]
---

# Snort3 Memory Pool (SFL_MEM)

## 定义

Snort3内存池（Memory Pool）是通过 `SF_MEM_API`抽象的统一内存分配层，针对包处理路径上的高频小对象分配（如 Packet、Flow、检测上下文）进行预分配+复用，避免 `malloc/free` 的性能波动与碎片。Snort3 默认使用基于 jemalloc/glibc malloc + memcap限制的实现。

##关键要点

- **`SF_MEM_API` 版本化抽象**：`SF_MEMAPI_VERSION v2`
- **Memcap限制**：`memory_cap` 模块跟踪已分配字节数，超限拒绝分配
- **per-thread local pool**：减少多线程分配竞争
- **Packet 对象池**：预创建 Packet 对象循环使用，包处理热路径零分配
- **Flow hash table**：conntrack-style 流表（`FlowCache`）
- **配套 Profiler**：可选 memory profiler跟踪每分配点

##核心概念

- **`PacketPool`**：全局 Packet 对象池，包结束时 `put_back()`
- **memory_cap.c**：memcap跟踪（`allocated` 全局 thread-local计数器）
- **memory_overloads**：全局 `new`/`delete`重载，可选集成 profiler
- **memory_module**：配置模块（`memory.cap`、`memory.overload_basic`）
- **heap_interface**：堆抽象层（封装 jemalloc）
- **配置开关**：`--enable-memory-profiler`（编译期）

## 相关页面

- [[entities/linux/snort3/snort3-runtime]] —运行时系统
- [[entities/linux/snort3/snort3-framework]] —框架
- [[entities/linux/snort3/snort3-infrastructure]] —基础设施
- [[entities/linux/snort3/snort3-flow]] — Flow 流表
