---
type: source
source-type: bookmark
title: "Effective Modern C++ 中文版"
author: "Scott Meyers; 译者: cntransgroup"
date: 2024
size: medium
path: raw/github/cntransgroup/EffectiveModernCppChinese
summary: "Scott Meyers Effective Modern C++ (C++11/14) 的中文翻译，42个条款覆盖移动语义、完美转发、lambda、并发、智能指针等核心最佳实践。"
tags: [cpp, modern-cpp, best-practices, effective-cpp, translation]
---

# Effective Modern C++ 中文版

## Overview

Scott Meyers 著《Effective Modern C++》中文翻译，由 cntransgroup 翻译。42 个条款覆盖 C++11/14 的最重要特性，是理解现代 C++ 最佳实践的必读之作。

## Core Content

### 9 Major Categories

| 类别 | 条款数 | 核心主题 |
|------|--------|----------|
| **类型推导** | ~6 | `auto`、decltype、SFINAE |
| **移动语义** | ~5 | `std::move`、`std::forward`、RVO |
| **完美转发** | ~4 | 引用折叠、通用引用 |
| **lambda 表达式** | ~4 | capture、init-capture、`std::function` |
| **并发** | ~5 | `std::atomic`、volatile、内存模型 |
| **智能指针** | ~4 | `unique_ptr`、`shared_ptr`、`weak_ptr` |
| **右值引用** | ~3 | 值类别、`std::move` |
| **unique_ptr** | ~3 | 独占所有权、定制删除器 |
| **shared_ptr** | ~4 | 引用计数、线程安全、make_shared |

### Key Takeaways

**Item 17:** 理解 `std::move` 和 `std::forward`
- `std::move` 无条件转换为右值
- `std::forward` 仅在条件满足时转换
- 两者都是函数，不是移动操作

**Item 20:** 优先使用 `std::make_unique` 和 `std::make_shared`
- 异常安全
- 避免 `new` 的重复错误
- `make_shared` 性能更好（控制块合并）

**Item 21:** 优先使用 `std::make_unique` 而非 `std::make_shared`
- `shared_ptr` 影响删除器设计
- `unique_ptr` 更轻量

**Item 25:** 限制源文件为默认模板参数
- SFINAE vs Concepts
- 隐式 vs 显式模板参数

**Item 34:** 优先使用 lambda 而非 `std::bind`
- lambda 可读性更好
- `std::bind` 在 C++14 前有用

## 相关页面

### Entity 页面
- [[entities/cpp/move-semantics]] — 移动语义核心
- [[entities/cpp/smart-pointers]] — 智能指针
- [[entities/cpp/lambda-expressions]] — Lambda 表达式
- [[entities/cpp/auto-type-deduction]] — auto 类型推导
- [[entities/cpp/concurrency]] — C++ 并发

### Source 页面
- [[sources/bookmark-cpp-core-guidelines]] — C++ Core Guidelines（配套规范）
- [[sources/cpp-modern-skills]] — Modern C++ Skills（技能层面）
