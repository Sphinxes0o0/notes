---
type: index
tags: [cpp, cpp17, modern-cpp, skill-collection]
created: 2026-05-25
---

# Modern C++ Skills Index (C++17 + Master)

> C++17 功能技能 + Master 思維模型，共 42 個 entity（13 C++17 + 14 modern-m* + 15 c17-*）
>
> 來源: [[sources/cpp-modern-skills]]

## C++17 技能 (13 entities)

### 所有權與資源管理

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/cpp/modern/c17-01-ownership]] | C++17 Ownership: Move Semantics, RAII, Rule of 0/5, RVO, copy elision | cpp17, ownership |
| [[entities/cpp/modern/c17-02-resource]] | C++17 Smart Pointers: unique_ptr, shared_ptr, weak_ptr, make_unique, custom deleter | cpp17, resource |

### 類型系統

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/cpp/modern/c17-03-mutability]] | C++17 Const Correctness: const, mutable, logical/bitwise const, constexpr if, reference qualifiers | cpp17, mutability |
| [[entities/cpp/modern/c17-04-templates]] | C++17 Templates: SFINAE, enable_if, void_t, if constexpr, override/final, CTAD | cpp17, templates |
| [[entities/cpp/modern/c17-05-type-driven]] | C++17 Type-Driven Design: std::optional, std::variant, newtypes, type-state pattern, string_view | cpp17, type-driven |

### 錯誤處理與並發

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/cpp/modern/c17-06-error-handling]] | C++17 Error Handling: std::optional, std::error_code, noexcept, exception safety, exception_ptr | cpp17, error-handling |
| [[entities/cpp/modern/c17-07-concurrency]] | C++17 Concurrency: std::thread, scoped_lock, atomic, shared_mutex, condition_variable, memory_order | cpp17, concurrency |
| [[entities/cpp/modern/c17-13-domain-error]] | C++17 Domain Errors: Exception hierarchies, std::exception_ptr, nested_exception, error_code | cpp17, domain-errors |

### 領域建模與性能

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/cpp/modern/c17-09-domain]] | C++17 DDD: Value Objects, Entities, Aggregates, Repository pattern, Domain Events | cpp17, ddd |
| [[entities/cpp/modern/c17-10-performance]] | C++17 Performance: cache locality, string_view, reserve, PMR, SoA vs AoS, SSO | cpp17, performance |
| [[entities/cpp/modern/c17-11-ecosystem]] | C++17 Ecosystem: CMake, vcpkg, clang-tidy, ASan, TSan, UBSan, GTest | cpp17, ecosystem |
| [[entities/cpp/modern/c17-12-lifecycle]] | C++17 Lifecycle: RAII, Rule of 5/0, constructor, destructor, static init, magic statics | cpp17, lifecycle |

### 工具

| Entity | Description | Tags |
|--------|-------------|------|
| [[entities/cpp/modern/cpp-skill-creator]] | C++ Skill Creator: AI-driven skill generation from cppreference/docs/local headers | cpp, skill-creation |

## Master 思維模型 (15 entities)

| Entity | Core Question | Key Framework | Tags |
|--------|---------------|---------------|------|
| [[entities/cpp/modern/modern-m01-ownership]] | 誰擁有這個資源？ | Error → Design, Trace Up/Down | master, mental-model |
| [[entities/cpp/modern/modern-m02-resource]] | 多少個所有者？ | unique_ptr (90%), shared_ptr, weak_ptr | master, mental-model |
| [[entities/cpp/modern/modern-m03-mutability]] | 誰能改變狀態？ | Logical vs Bitwise const, mutable + mutex | master, mental-model |
| [[entities/cpp/modern/modern-m04-zero-cost]] | 何時確定類型？ | Static (template) vs Dynamic (virtual) | master, mental-model |
| [[entities/cpp/modern/modern-m05-type-driven]] | 能讓 bug 變編譯錯誤嗎？ | Strong types, phantom types, type-state | master, mental-model |
| [[entities/cpp/modern/modern-m06-error-handling]] | 錯誤可恢復嗎？ | optional vs expected vs throw vs assert | master, mental-model |
| [[entities/cpp/modern/modern-m07-concurrency]] | 線程如何通信？ | Shared state vs Coordination vs Tasks | master, mental-model |
| *(m08 skipped — not present in source)* | | | |
| [[entities/cpp/modern/modern-m09-domain]] | 身份還是值？ | Value Object vs Entity vs Aggregate | master, mental-model |
| [[entities/cpp/modern/modern-m10-performance]] | 數據在哪裡？ | Cache locality, allocations, measurement | master, mental-model |
| [[entities/cpp/modern/modern-m11-ecosystem]] | 如何構建維護？ | CMake + vcpkg + sanitizers | master, mental-model |
| [[entities/cpp/modern/modern-m12-lifecycle]] | 對象何時死亡？ | Stack vs Heap vs Static | master, mental-model |
| [[entities/cpp/modern/modern-m13-domain-error]] | 誰捕獲錯誤？ | Exception vs error_code hierarchy | master, mental-model |
| [[entities/cpp/modern/modern-m14-mental-model]] | 內存中發生了什麼？ | Value vs Reference vs Pointer | master, mental-model |
| [[entities/cpp/modern/modern-m15-anti-pattern]] | 這是 C 還是 C++？ | RAII vs malloc, unique_ptr vs new | master, mental-model |

## 交叉引用地圖

```
C++17 Ownership ──────────────────────────────→ move-semantics, raii
C++17 Resource ────────────────────────────────→ smart-pointers
C++17 Mutability ──────────────────────────────→ constexpr
C++17 Templates ───────────────────────────────→ variadic-templates, if-constexpr, cpp20-features
C++17 Type-Driven ────────────────────────────→ templates, c17-09-domain
C++17 Error-Handling ─────────────────────────→ c17-05-type-driven, c17-13-domain-error
C++17 Concurrency ────────────────────────────→ concurrency, cpp-memory-model
C++17 Domain ─────────────────────────────────→ c17-05-type-driven, templates
C++17 Performance ─────────────────────────────→ stl-containers, stl-string, cpp-perf-optimization
C++17 Ecosystem ───────────────────────────────→ cpp-safety
C++17 Lifecycle ────────────────────────────────→ raii, c17-01-ownership
C++17 Domain-Error ────────────────────────────→ c17-06-error-handling, c17-09-domain

Master Ownership ──────────────────────────────→ m02-resource, m12-lifecycle, m15-anti-pattern
Master Resource ────────────────────────────────→ m01-ownership, m15-anti-pattern
Master Mutability ──────────────────────────────→ m07-concurrency
Master Zero-Cost ───────────────────────────────→ c17-04-templates, c17-05-type-driven
Master Type-Driven ────────────────────────────→ m09-domain
Master Error-Handling ──────────────────────────→ m13-domain-error
Master Concurrency ────────────────────────────→ m03-mutability
Master Domain ─────────────────────────────────→ m05-type-driven
Master Performance ──────────────────────────────→ c17-11-ecosystem
Master Ecosystem ──────────────────────────────→ cpp-safety
Master Lifecycle ───────────────────────────────→ m01-ownership
Master Domain-Error ────────────────────────────→ m06-error-handling
Master Mental-Model ───────────────────────────→ m01-ownership, m15-anti-pattern
Master Anti-Pattern ────────────────────────────→ m01-ownership, m02-resource
```

## 與現有 C++ Entity 的關係

| 現有 Entity | 新技能覆蓋 |
|-------------|------------|
| [[entities/cpp/move-semantics]] | modern-m01-ownership, c17-01-ownership |
| [[entities/cpp/raii]] | modern-m01-ownership, modern-m12-lifecycle, c17-01-ownership, c17-12-lifecycle |
| [[entities/cpp/smart-pointers]] | modern-m02-resource, c17-02-resource |
| [[entities/cpp/constexpr]] | modern-m03-mutability, c17-03-mutability |
| [[entities/cpp/concurrency]] | modern-m07-concurrency, c17-07-concurrency |
| [[entities/cpp/variadic-templates]] | modern-m04-zero-cost, c17-04-templates |
| [[entities/cpp/if-constexpr]] | modern-m04-zero-cost, c17-04-templates |
| [[entities/cpp/cpp20-features]] | modern-m04-zero-cost, c17-04-templates (concepts C++20) |
| [[entities/cpp/cpp-stl-containers]] | modern-m10-performance, c17-10-performance |
| [[entities/cpp/cpp-stl-string]] | modern-m10-performance, c17-10-performance |
| [[entities/cpp/cpp-object-lifetime]] | modern-m12-lifecycle, c17-12-lifecycle |
| [[entities/cpp/cpp-safety]] | modern-m11-ecosystem, c17-11-ecosystem |
| [[entities/cpp/cpp-perf-optimization]] | modern-m10-performance, c17-10-performance |
| [[entities/cpp/cpp-templates]] | modern-m04-zero-cost, c17-04-templates |
| [[entities/cpp/cpp-memory-model]] | modern-m07-concurrency, c17-07-concurrency |

## 來源導航

| Source | 模塊 |
|--------|------|
| [[sources/github-modern-cpp-skills-m01]] | m01-ownership |
| [[sources/github-modern-cpp-skills-m02]] | m02-resource |
| [[sources/github-modern-cpp-skills-m03]] | m03-mutability |
| [[sources/github-modern-cpp-skills-m04]] | m04-zero-cost |
| [[sources/github-modern-cpp-skills-m05]] | m05-type-driven |
| [[sources/github-modern-cpp-skills-m06]] | m06-error-handling |
| [[sources/github-modern-cpp-skills-m07]] | m07-concurrency |
| *(m08 skipped)* | |
| [[sources/github-modern-cpp-skills-m09]] | m09-domain |
| [[sources/github-modern-cpp-skills-m10]] | m10-performance |
| [[sources/github-modern-cpp-skills-m11]] | m11-ecosystem |
| [[sources/github-modern-cpp-skills-m12]] | m12-lifecycle |
| [[sources/github-modern-cpp-skills-m13]] | m13-domain-error |
| [[sources/github-modern-cpp-skills-m14]] | m14-mental-model |
| [[sources/github-modern-cpp-skills-m15]] | m15-anti-pattern |

## Feature Reference Entities (15 entities from AnthonyCalandra/modern-cpp-features)

> Source: [[sources/github-modern-cpp-features]] — C++11/14/17/20/23 feature reference

| Entity | Coverage | Tags |
|--------|----------|------|
| [[entities/cpp/modern-cpp/cpp-auto-type-deduction]] | auto, decltype, decltype(auto), forwarding refs | cpp11, cpp14 |
| [[entities/cpp/modern-cpp/cpp-move-semantics]] | rvalue refs, std::move, std::forward, Rule of 5 | cpp11 |
| [[entities/cpp/modern-cpp/cpp-lambda-expressions]] | lambdas, generic lambdas, captures, mutable | cpp11, cpp14, cpp20 |
| [[entities/cpp/modern-cpp/cpp-smart-pointers]] | unique_ptr, shared_ptr, weak_ptr, make_unique | cpp11, cpp14, cpp20 |
| [[entities/cpp/modern-cpp/cpp-variadic-templates]] | parameter packs, fold expressions, integer_sequence | cpp11, cpp17 |
| [[entities/cpp/modern-cpp/cpp-constexpr]] | constexpr, consteval, constexpr if, constexpr virtual | cpp11, cpp14, cpp17, cpp20, cpp23 |
| [[entities/cpp/modern-cpp/cpp-concepts]] | requires, constraints, standard concepts library | cpp20 |
| [[entities/cpp/modern-cpp/cpp-structured-bindings]] | structured bindings, CTAD, std::tie, designated init | cpp17, cpp20 |
| [[entities/cpp/modern-cpp/cpp-coroutines]] | co_await, co_yield, co_return, stackless | cpp20 |
| [[entities/cpp/modern-cpp/cpp-attributes]] | [[entities/cpp/nodiscard]], [[likely]], [[deprecated]], noexcept | cpp11, cpp14, cpp17, cpp20, cpp23 |
| [[entities/cpp/modern-cpp/cpp-stl-optional-variant-any]] | std::variant, std::optional, std::any, std::expected | cpp17, cpp20, cpp23 |
| [[entities/cpp/modern-cpp/cpp-stl-functional]] | std::invoke, std::apply, std::bind_front, std::not_fn | cpp11, cpp17, cpp20 |
| [[entities/cpp/modern-cpp/cpp-stl-string-view]] | std::string_view, starts_with, ends_with, contains | cpp17, cpp20, cpp23 |
| [[entities/cpp/modern-cpp/cpp-stl-format-span]] | std::format, std::span, spanstream, out_ptr | cpp20, cpp23 |
| [[entities/cpp/modern-cpp/cpp-concurrency]] | std::thread, std::jthread, atomic, memory_order, locks | cpp11, cpp14, cpp17, cpp20 |

## Source

- [[sources/cpp-modern-skills]] - Modern C++ Skills source (28 skill files)
- [[sources/github-modern-cpp-features]] - AnthonyCalandra/modern-cpp-features (C++11-23, 100+ features)
