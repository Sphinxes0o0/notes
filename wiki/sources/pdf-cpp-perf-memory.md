---
type: source
tags: [cpp, memory-management, performance, optimization, cpu-cache, allocators]
source-type: pdf
title: "C++ Performance & Memory Management Books (4 volumes)"
author: "Ayman Alheraki, Kurt Guntheroth, Patrice Roy, Wang Qi et al."
date: 2025
size: large
path: raw/PDFs/books/
summary: "四册 C++ 性能优化与内存管理书籍：现代 C++ 内存管理高级指南、C++性能优化指南、Packt C++ Memory Management、Cache 内存中文手册"
---

# C++ Performance & Memory Management Books

## 1. Advanced Memory Management in Modern C++

**作者**: Ayman Alheraki | **出版**: 2024 | **页数**: 119

面向 C++17 及以后标准的进阶内存管理专题手册，由 simplifycpp.org 出品。

### 核心主题
- 栈 vs 堆内存深度对比
- 原始指针到现代技术（C++17+）的演进
- 智能指针高级用法（自定义删除器、循环引用）
- std::unique_ptr、std::shared_ptr、std::weak_ptr 最佳实践
- RAII 与现代内存资源管理
- 自定义分配器模式

## 2. C++ 性能优化指南 (Optimized C++ 中文版)

**作者**: Kurt Guntheroth | **页数**: 310

C++ 性能优化经典著作中文版。系统性地介绍性能测量的方法论和七大优化策略。

### 核心主题
- Amdahl 定律与 90/10 法则
- 编译器优化（-O2/O3、LTO、PGO）
- 算法优化（O(n log n) vs O(n²)）
- 减少内存分配和拷贝
- 循环优化与代码外提
- 数据结构缓存友好性
- 并发优化
- Linux perf 工具链

## 3. C++ Memory Management (Packt)

**作者**: Patrice Roy | **出版**: 2025 | **页数**: 434

2025 年最新出版的 C++ 内存管理专著，从基础到高级系统性地讲解内存管理技术。

### 核心主题
- 内存管理基础与 C++ 抽象
- 栈内存、堆内存与静态存储
- RAII 与智能指针深度分析
- 自定义分配器与内存池
- 内存泄漏检测与预防
- 性能内存分析与调优

## 4. Cache 内存 (Cache Memory 中文手册)

**作者**: Wang Qi, Yang Xi, Zhu Yuhao 等 | **页数**: 111

中文社区编写的缓存内存技术手册，详细讲解 CPU Cache 架构、算法和编程优化。

### 核心主题
- Cache 基础架构（L1/L2/L3）
- Cache 一致性协议（MESI）
- Cache 替换策略
- 缓存友好编程
- 伪共享 (False Sharing)
- 多核场景下的缓存优化
- Intel/AMD 具体微架构缓存

## 相关页面

- [[entities/cpp/cpp-perf-optimization]] — C++ 性能优化（CPU cache、SIMD、profiling）
- [[entities/cpp/cpp-memory-management]] — C++ 内存管理概念
- [[entities/cpp/smart-pointers]] — 智能指针
- [[entities/cpp/raii]] — RAII 资源管理
- [[entities/cpp/cpp-stl-allocators]] — STL 分配器
- [[entities/cpp/move-semantics]] — 移动语义
- [[cpp-index]] — C++ 模块导航
