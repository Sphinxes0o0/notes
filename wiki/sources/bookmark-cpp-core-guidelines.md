---
type: source
source-type: bookmark
title: "C++ Core Guidelines 中文版"
author: "Bjarne Stroustrup & Stroustrup; 译者: lynnboy"
date: 2024
size: medium
path: raw/github/lynnboy/CppCoreGuidelines-zh-CN
summary: "Bjarne Stroustrup 主导的 C++ 核心规范——关注类型安全、资源管理、内存安全、并发、高级架构，是 C++ 官方最佳实践指南。"
tags: [cpp, safety, guidelines, best-practices, type-safety]
---

# C++ Core Guidelines 中文版

## Overview

C++ Core Guidelines 是由 Bjarne Stroustrup 主导的官方 C++ 编程规范，汇聚了来自多个组织的多年设计工作。指南以现代 C++ (C++11/14/17/20) 为基础，目标是帮助开发者写出**静态类型安全、无泄漏**的代码。

> "Within C++ is a smaller, simpler, safer language struggling to get out."
> — Bjarne Stroustrup

## Core Content

### Focus Areas

| 领域 | 内容 |
|------|------|
| **Interfaces** | 类型安全的接口设计 |
| **Resource Management** | RAII、智能指针、unique_ptr/shared_ptr |
| **Memory Management** | 避免泄漏、悬空指针、缓冲区溢出 |
| **Concurrency** | 线程安全、无锁编程 |
| **Library Guidelines** | STL 扩展规范 |
| **Type Safety** | 静态类型检查、禁止裸类型 |

### Key Principles

1. **类型安全** — 优先使用 `std::variant`、`std::optional` 而非裸指针
2. **资源安全** — RAII，禁用 `new`/`delete`
3. **边界安全** — 使用 `span<T>` 而非裸指针+大小
4. **悬挂安全** — 避免 `T&` 而使用 `owner<T>*`
5. **T Gegnore** — 维持清晰度，不依赖未定义行为

### Tooling Integration

指南**设计为可被静态分析工具支持**：
- 违反规则时会被工具标记
- 每个规则都有编号（如 `C.80`）
- 工具可自动检查（clang-tidy、Coverity 等）

## 关键引用

### 资源管理规则

- **R.1**: 用 RAII 管理资源
- **R.2**: 裸指针不应拥有对象
- **R.3**: 裸类型只用于内部/历史兼容
- **R.5**: 优先使用 stack 对象
- **R.10**: `malloc`/`free` 只用于 C 互操作

### 接口规则

- **I.1**: 预条件检查
- **I.2**: 优先使用 `std::optional` 表示可选值
- **I.4**: 优先使用具名类型而非 `int`

## 相关页面

### Entity 页面
- [[entities/cpp/cpp-safety]] — C++ 安全相关实体
- [[entities/cpp/smart-pointers]] — 智能指针（RAII 实现）
- [[entities/cpp/raii]] — RAII 资源管理惯用法
- [[entities/cpp/cpp-memory-management]] — 内存管理

### Source 页面
- [[sources/bookmark-effective-modern-cpp]] — Effective Modern C++（配套阅读）
- [[sources/cpp-modern-skills]] — Modern C++ Skills（C++17）
