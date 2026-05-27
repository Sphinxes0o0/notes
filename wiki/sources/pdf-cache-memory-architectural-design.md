---
type: source
source-type: pdf
title: "Cache Memory 架构设计"
author: "王奇, 杨希, 朱宇皓, 朱彦海 (中文原创)"
date: 2026-05-27
size: medium
path: raw/PDFs/books/CacheMemory.pdf
summary: "中文原创 Cache Memory 深度分析（111页），涵盖 x86/Power/UltraSPARC Alpha 四类处理器 Cache 架构：存储层次、TLB、Cache 结构、预取、写策略、一致性协议、带宽优化"
tags: [computer-architecture, cache-memory, memory-hierarchy, performance, books]
created: 2026-05-27
sources: []
---

# Cache Memory 架构设计

## 概述

中文原创 Cache Memory 系统深度分析（111页），以 Intel x86 (Sandy Bridge EP)、Power、UltraSPARC、Alpha 四款 Tier-1 处理器为实例，系统讲解 Cache 架构设计与实现。不同于教科书式内容，本文从工业界视角出发，揭示 Cache 设计的工程权衡与实际挑战。

---

## 核心内容

### 第1章 Cache 的思考

**Memory Hierarchy 背景：**
- Cache Memory 位于 Memory Hierarchy 最顶端（L1/L2/L3），CPU 访问数据时优先命中 Cache
- 主存储器访问延时 ~60-120ns，SRAM ~1ns；即使工艺提升，CPU 主频增长远超主存带宽增长（"主存不是越来越快，是越变越胖"）
- Cache 核心作用：弥合 CPU 速度与主存访问速度之间的 Gap

**Cache 设计复杂度：**
- 狭义 Cache（CPU Cache）的设计复杂度远超广义 Cache（CDN、数据库 Buffer Pool 等）
- Cache Memory 是整个处理器系统中最复杂的部件之一

### 第2章 TLB（Translation Lookaside Buffer）

**TLB Miss Rate 研究演变：**
- 经典教科书：TLB Miss Rate 平均 ~5%，某些情况 <1%
- 近年研究：许多应用中 TLB Miss Rate 高达 30~60%
- 驱动因素：大页（Huge Pages）、匿名映射、NUMA 系统

**TLB 结构与优化：**
- L1 TLB、DTLB/ITLB 分离设计
- TLB Shootdown 机制：多核修改页表时的同步开销
- ASID（Address Space ID）避免全局 TLB Flush

### 第3章 Cache 结构（内部架构）

**Cache Block 索引与寻址：**
- Index 位定位 Cache Set，Tag 位比较判断命中
- CLN（Cache Line Number）/ CCL（Cache Coherency Line）概念
- Way（路数）决定相联度：直接映射（1-way）、组相联、N-way

**Bank 与 Port 设计：**
- 2-Ports Cache 设计需复制 Tag 阵列，带来同步开销
- Bank Conflict 问题与互连拓扑（Share Bus / Ring-Bus）
- x86 的分离式 I-Cache / D-Cache 设计

### 第4章 Cache 预取（Prefetch）

**软件预取：**
- `prefetch` 指令：hint-based，非强制
- 预取距离、预取度（degree）选择
- 预取失效场景：指针追逐、分支不确定、数据相关

**硬件预取：**
- 启发式预取：相邻行预取（Adjacent Line Prefetch）
- 跨度预取（Strided Prefetch）：检测等间隔访问模式
- 预取带宽争用：预取消耗内存带宽可能影响主请求

### 第5章 Cache 写策略

**Write-Through vs Write-Back：**
- WT：每次写同时写主存，一致性好但带宽开销大
- WB：仅在 Cache Line 替换时写回，开销大但性能好
- 现代处理器 L1 通常 WT，L2/L3 WB

**Write-Allocation：**
- Write-Allocate（写命中但不在 Cache → 先调入再写）
- No-Write-Allocate（直接写主存）
- 通常 Write-Back 配合 Write-Allocate，Write-Through 配合 No-Write-Allocate

**WC（Write-Combining） 与 UC（Uncacheable）：**
- MMIORegion 使用 UC 模式，绕过 Cache
- WC 模式合并多次写操作，减少总线事务

### 第6章 Cache 一致性（Coherency）

**MESI / MOESI 协议：**
- Modified：Cache Line 已被修改，与主存不一致
- Exclusive：Cache Line 干净且唯一
- Shared：多个处理器持有干净副本
- Invalid：Cache Line 无效
- AMD 增加 Owned 状态（MOESI）：允许 dirty 数据直接转移

**Write Serialization：**
- RFO（Read for Ownership）：写操作前必须获得独占权
- 使用 Cache Coherent Protocol 和 Bus Transaction 实现
- Ring-Bus 互连中的 Write Serialization 实现更复杂

**Snooping vs Directory：**
- Snooping：广播式，所有节点监听总线（适合小规模）
- Directory：目录式，分布式维护共享状态（适合大规模 NUMA）

### 第7章 Cache 性能与带宽

**Cache 带宽分析：**
- 读带宽 vs 写带宽的不对称性
- 多核共享 L3 的带宽争用（Ring-Bus 带宽瓶颈）
- 内存控制器位置（Integrated vs Off-package）

**Cache Miss 分类（3C）：**
- Compulsory Miss（强制缺失）：首次访问
- Capacity Miss（容量缺失）：工作集超过 Cache 大小
- Conflict Miss（冲突缺失）：相联度不足导致同组竞争

**优化策略：**
- 数据对齐：避免跨 Cache Line 访问
- 数据布局：Array of Structures (AoS) vs Structure of Arrays (SoA)
- 伪共享（False Sharing）避免：不同核访问同一 Cache Line 不同字段

### 第8章 Cache 与微架构

**μops 流水中的 Cache 访问：**
- 指令流水线中 Cache 访问的时序影响
- Load-Use 延迟：L1 Hit ~4 cycles, L2 Hit ~12 cycles, L3 Hit ~30-50 cycles
- 分支预测与 Cache 预取的协同

**Inner / Outer Cache 概念：**
- Inner Cache：微架构内部（如 Sandy Bridge 的 L1 + L2）
- Outer Cache：微架构外部（历史上 L3 位于片外）
- Modern 趋势：L3 通常也在片内但位于不同核共享区域

---

## 关键引用

- Chen, X. et al. "A Study of Memory Performance on NUMA Systems" — TLB Miss Rate 30-60% 数据来源
- Intel SDM Vol.3 — x86 Cache/MTRR 规范
- AMD Software Optimization Guide — Bulldozer Microarchitecture Cache 设计

## 相关页面

- [[sources/pdf-computer-systems-programmers-perspective]] — CS:APP 缓存层级与内存山
- [[sources/pdf-cpp-perf-books]] — C++ 性能优化（Cache 友好代码）
- [[kernel-subsystems-index]] — 内核子系统（内存管理）
- [[entities/os/os-memory-management]] — 操作系统内存管理
- [[arm-index]] — ARM 体系结构（Cache 实现）
- [[sys-prog-index]] — 系统编程（Cache 感知编程）