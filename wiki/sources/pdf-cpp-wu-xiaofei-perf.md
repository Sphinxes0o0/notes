---
type: source
source-type: pdf
title: 高性能C/C++系统性能优化 从理论到实践
author: 吴晓飞 (阿里云RDS MySQL内核负责人)
date: 2024
size: small
path: raw/PDFs/slides/吴晓飞_高性能CC++系统性能优化 从理论到实践.pdf
summary: 吴晓飞：PolarDB TPCC登顶性能优化实战，从理论到工具的完整性能优化方法论
tags: [cpp, performance, optimization, polar-db, mysql, linux, cpp-slides]
created: 2024
---
# 高性能C/C++系统性能优化：从理论到实践

## 核心内容

**Author:** 吴晓飞（阿里云RDS MySQL内核负责人）| 2024

### 目录结构

1. **性能优化的理论支持**
2. **性能分析的工具支持**
3. **性能优化实战——以PolarDB TPCC为例**

### 理论支持

- **Amdahl定律**：并行化收益受串行部分限制
- **Little定律**：在系统稳定状态下，并发数 = 吞吐量 × 响应时间
- **缓存友好设计**：数据局部性、cache line对齐、预取
- **CPU流水线**：分支预测失败代价、分支折叠

### 工具支持

- **perf**：CPU周期分析、cache miss、branch miss
- **火焰图(FlameGraph)**：Off-CPU时间可视化
- **BPF/bcc**：动态追踪，零开销可观测性
- **Valgrind/Cachegrind**：模拟cache行为

### PolarDB TPCC优化案例

- InnoDB buffer pool锁竞争优化
- Redo log写入优化（批量合并）
- 索引扫描优化（延迟物化）

## 相关页面
- [[entities/cpp/cpp-perf-optimization]] — C++性能优化
- [[entities/cpp/cpp-memory-management]] — 内存性能
- [[kernel-subsystems-index]] — Linux内核子系统（性能相关）
- [[cpp-index]] — Modern C++ 模块索引