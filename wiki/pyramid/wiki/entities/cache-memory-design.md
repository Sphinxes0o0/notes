---
type: entity
tags: [computer-architecture, cache-memory, memory-hierarchy, performance]
created: 2026-05-27
sources: [pdf-cache-memory-architectural-design]
---

# Cache Memory 架构设计

## 定义

CPU 处理器与主存储器之间的快速存储层次（通常 L1/L2/L3），用于缓存最近使用的数据和指令，弥合 CPU 速度与主存访问延迟之间的巨大差距（L1 ~1ns vs DRAM ~60-120ns）。

## 关键要点

### Cache 结构
- **Cache Line / Block**：最小访问单元（通常 64 字节）
- **Tag / Index / Offset**：地址分解用于 Cache 查找
- **相联度**：直接映射（1-way）、组相联（N-way）、全相联
- **Bank & Port**：多 Port 需复制 Tag 阵列，Bank Conflict 影响带宽

### Cache 层级
- **L1 I-Cache / D-Cache**：每个核心私有，~32KB，~4 cycle 延迟
- **L2 Cache**：每个核心私有或共享，~256KB，~12 cycle 延迟
- **L3 Cache**：多个核心共享，~8MB，~30-50 cycle 延迟

### TLB（Translation Lookaside Buffer）
- 虚拟地址到物理地址转换的缓存
- 经典教科书：TLB Miss ~5%；实际：30-60%（大页、匿名映射场景）
- TLB Shootdown：多核修改页表时的同步开销

### 写策略
- **Write-Through (WT)**：每次写同时写主存，一致性好但带宽开销大
- **Write-Back (WB)**：替换时写回，开销小但复杂
- **Write-Allocate / No-Write-Allocate**：缺失时的写策略选择
- **WC / UC**：Memory-Mapped I/O 使用 Uncacheable 模式

### 一致性协议
- **MESI**：Modified / Exclusive / Shared / Invalid
- **MOESI**：AMD 增加 Owned 状态，支持 dirty 数据直接转移
- **RFO（Read for Ownership）**：写操作前必须获取独占权
- **Snooping vs Directory**：广播式 vs 目录式，适用于不同规模

### 性能优化
- **3C 缺失分类**：Compulsory / Capacity / Conflict
- **伪共享（False Sharing）**：不同核访问同一 Cache Line 不同字段
- **Cache 友好代码**：数据对齐、SoA vs AoS 布局、跨行访问避免
- **预取**：硬件（启发式/跨度）vs 软件（prefetch 指令）

## 来源

- [[sources/pdf-cache-memory-architectural-design]] — Cache Memory 架构设计（中文原创，111页）
- [[sources/pdf-computer-systems-programmers-perspective]] — CS:APP 内存层级与缓存山
- [[sources/pdf-arm-architecture]] — ARMv8 体系结构参考手册（L1/L2/L3 Cache 实现）
- [[entities/cpp/cpp-perf-optimization]] — C++ 性能优化（Cache 感知编程）
- [[entities/linux/kernel/index#memory-management]] — 内核内存管理子系统