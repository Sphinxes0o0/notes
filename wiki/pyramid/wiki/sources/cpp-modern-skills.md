---
type: source
source-type: github
created: 2026-05-25
title: "Modern C++ Skills (C++17 + Master)"
author: "Sphinx Shi"
date: 2026-05-25
size: medium
path: raw/Modern-Cpp-Skills/
summary: "26 C++ skills covering C++17 features and Master-level concepts: ownership, resource management, mutability, templates, type-driven design, error handling, concurrency, DDD, performance, ecosystem, lifecycle, domain errors, mental models, anti-patterns, and AI-driven skill creation."
tags: [cpp, cpp17, modern-cpp, skill-collection]
---

# Modern C++ Skills (C++17 + Master)

## 概述

本來源包含 26 個 C++ 技能，分為兩層：

- **C++17 技能 (13個)**: 聚焦 C++17 具體技術和代碼模式
- **Master 技能 (15個)**: 聚焦思維模型、Error → Design 映射、Trace Up/Down 推理框架

## 來源結構

```
raw/Modern-Cpp-Skills/
├── c17-01-ownership/         # C++17: Move Semantics, RAII, Rule of 0/5
├── c17-02-resource/          # C++17: Smart Pointers (unique/shared/weak)
├── c17-03-mutability/        # C++17: Const Correctness, mutable, constexpr if
├── c17-04-templates/         # C++17: Templates, SFINAE, if constexpr, override/final
├── c17-05-type-driven/       # C++17: Type-Driven Design, newtypes, std::variant
├── c17-06-error-handling/    # C++17: std::optional, std::error_code, noexcept
├── c17-07-concurrency/       # C++17: std::thread, mutex, atomic, shared_mutex
├── c17-09-domain/            # C++17: DDD (Value Objects, Entities, Aggregates)
├── c17-10-performance/       # C++17: Cache locality, string_view, PMR, reserve
├── c17-11-ecosystem/         # C++17: CMake, vcpkg, clang-tidy, sanitizers
├── c17-12-lifecycle/         # C++17: RAII, Rule of 5/0, constructor, destructor
├── c17-13-domain-error/       # C++17: Exception hierarchies, std::exception_ptr
├── cpp-skill-creator/         # AI-driven C++ skill creation from docs/headers
├── m01-ownership/            # Master: Ownership mental model
├── m02-resource/             # Master: Smart Pointers mental model
├── m03-mutability/           # Master: Const correctness mental model
├── m04-zero-cost/            # Master: Templates vs Virtual polymorphism
├── m05-type-driven/          # Master: Type-Driven Design mental model
├── m06-error-handling/       # Master: Error handling mental model
├── m07-concurrency/          # Master: Concurrency mental model
├── m09-domain/               # Master: Domain modeling mental model
├── m10-performance/          # Master: Performance mental model
├── m11-ecosystem/            # Master: C++ ecosystem mental model
├── m12-lifecycle/            # Master: Lifecycle mental model
├── m13-domain-error/         # Master: Domain errors mental model
├── m14-mental-model/         # Master: Pointer/reference/UB mental model
├── m15-anti-pattern/         # Master: C++ anti-patterns
└── CLAUDE.md                 # Skill system documentation
```

## 核心內容

### C++17 技能棧

| 技能 | 主題 | 核心工具 |
|------|------|----------|
| c17-01-ownership | 所有權與移動語義 | unique_ptr, shared_ptr, Rule of 0/5 |
| c17-02-resource | 智能指針 | make_unique, make_shared, weak_ptr, custom deleter |
| c17-03-mutability | Const 正確性 | const, mutable, constexpr if, reference qualifiers |
| c17-04-templates | 模板與多態 | SFINAE, enable_if, void_t, if constexpr, override/final |
| c17-05-type-driven | 類型驅動設計 | std::optional, std::variant, newtypes, type-state |
| c17-06-error-handling | 錯誤處理 | std::optional, std::error_code, noexcept, exception safety |
| c17-07-concurrency | 並發 | std::thread, scoped_lock, atomic, shared_mutex |
| c17-09-domain | 領域驅動設計 | Value Object, Entity, Aggregate, Repository |
| c17-10-performance | 性能優化 | cache locality, string_view, reserve, PMR |
| c17-11-ecosystem | 工具生態 | CMake, vcpkg, clang-tidy, ASan, TSan, UBSan |
| c17-12-lifecycle | 生命周期 | RAII, Rule of 5/0, constructor, destructor, static init |
| c17-13-domain-error | 領域錯誤 | Exception hierarchy, std::exception_ptr, nested_exception |
| cpp-skill-creator | AI 技能創建 | /create-llms-for-skills, /create-skills-via-llms |

### Master 技能棧

| 技能 | 核心問題 | 關鍵框架 |
|------|----------|----------|
| m01-ownership | 誰擁有資源？ | Error → Design Question, Trace Up/Down |
| m02-resource | 多少個所有者？ | unique_ptr (90%), shared_ptr, weak_ptr |
| m03-mutability | 誰能改變狀態？ | Logical vs Bitwise const, mutable + mutex |
| m04-zero-cost | 何時確定類型？ | Static (template) vs Dynamic (virtual) dispatch |
| m05-type-driven | 能讓 bug 變編譯錯誤嗎？ | Strong types, phantom types, type-state |
| m06-error-handling | 錯誤可恢復嗎？ | optional vs expected vs throw vs assert |
| m07-concurrency | 線程如何通信？ | Shared state vs Coordination vs Tasks |
| m09-domain | 身份還是值？ | Value Object vs Entity vs Aggregate |
| m10-performance | 數據在哪裡？ | Cache locality, allocations, measurement |
| m11-ecosystem | 如何構建維護？ | CMake + vcpkg + sanitizers |
| m12-lifecycle | 對象何時死亡？ | Stack vs Heap vs Static |
| m13-domain-error | 誰捕獲錯誤？ | Exception vs error_code hierarchy |
| m14-mental-model | 內存中發生了什麼？ | Value vs Reference vs Pointer |
| m15-anti-pattern | 這是 C 還是 C++？ | RAII vs malloc, unique_ptr vs new |

## 關鍵引用

### 思維框架

**Error → Design Question**:
每個錯誤症狀映射到設計問題：
- Double Free → 誰擁有資源？
- Use After Free → 引用是否超出生命周期？
- Memory Leak → 析構函數在哪裡？

**Trace Up/Down**:
- Trace Up: 從錯誤向上追溯到設計問題
- Trace Down: 從意圖向下翻譯為代碼

**Core Question Pattern**:
每個技能以一個核心問題開始，引導思考方向。

### C++17 新特性亮點

- **if constexpr**: 編譯時分支，無 SFINAE 技巧
- **std::optional / std::variant**: 類型安全的錯誤表示
- **std::string_view / std::span**: 零拷貝視圖
- **std::shared_mutex**: C++17 讀者-寫者鎖
- **std::scoped_lock**: 死鎖free 多 mutex 鎖
- **CTAD**: 類模板參數推導
- **std::hardware_destructive_interference_size**: 緩存線衝突優化
- **inline variable**: C++17 頭文件定義

## 相關頁面

### Entity 頁面（新建）
- [[entities/cpp/modern/c17-01-ownership]] - C++17 Ownership
- [[entities/cpp/modern/c17-02-resource]] - C++17 Smart Pointers
- [[entities/cpp/modern/c17-03-mutability]] - C++17 Const Correctness
- [[entities/cpp/modern/c17-04-templates]] - C++17 Templates
- [[entities/cpp/modern/c17-05-type-driven]] - C++17 Type-Driven Design
- [[entities/cpp/modern/c17-06-error-handling]] - C++17 Error Handling
- [[entities/cpp/modern/c17-07-concurrency]] - C++17 Concurrency
- [[entities/cpp/modern/c17-09-domain]] - C++17 DDD
- [[entities/cpp/modern/c17-10-performance]] - C++17 Performance
- [[entities/cpp/modern/c17-11-ecosystem]] - C++17 Ecosystem
- [[entities/cpp/modern/c17-12-lifecycle]] - C++17 Lifecycle
- [[entities/cpp/modern/c17-13-domain-error]] - C++17 Domain Errors
- [[entities/cpp/modern/cpp-skill-creator]] - C++ Skill Creator
- [[entities/cpp/modern/m01-ownership]] - Master: Ownership
- [[entities/cpp/modern/m02-resource]] - Master: Resource
- [[entities/cpp/modern/m03-mutability]] - Master: Mutability
- [[entities/cpp/modern/m04-zero-cost]] - Master: Zero-Cost
- [[entities/cpp/modern/m05-type-driven]] - Master: Type-Driven
- [[entities/cpp/modern/m06-error-handling]] - Master: Error Handling
- [[entities/cpp/modern/m07-concurrency]] - Master: Concurrency
- [[entities/cpp/modern/m09-domain]] - Master: Domain
- [[entities/cpp/modern/m10-performance]] - Master: Performance
- [[entities/cpp/modern/m11-ecosystem]] - Master: Ecosystem
- [[entities/cpp/modern/m12-lifecycle]] - Master: Lifecycle
- [[entities/cpp/modern/m13-domain-error]] - Master: Domain Errors
- [[entities/cpp/modern/m14-mental-model]] - Master: Mental Models
- [[entities/cpp/modern/m15-anti-pattern]] - Master: Anti-Patterns

### 現有相關頁面
- [[entities/cpp/move-semantics]] - 移動語義核心（C++11）
- [[entities/cpp/raii]] - RAII 資源管理慣用法
- [[entities/cpp/smart-pointers]] - 智能指針
- [[entities/cpp/concurrency]] - C++ 並發編程
- [[entities/cpp/constexpr]] - constexpr 編譯時計算
- [[entities/cpp/if-constexpr]] - if constexpr 編譯時分支
- [[entities/cpp/variadic-templates]] - 模板變參
- [[entities/cpp/cpp20-features]] - C++20 新特性
- [[cpp-modern-index]] - 模塊導航頁
