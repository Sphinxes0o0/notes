---
type: entity
tags: [cpp, master, anti-patterns, c-style, raw-pointers]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Anti-Patterns

## 核心問題

**這是 C 還是 C++？**

- **C-Style**: `malloc`、`free`、`(int)x`、`void*`
- **C++ Style**: `std::vector`、`std::unique_ptr`、`static_cast`、模板

## Error → Design Question

| 問題 | 設計問題 |
|------|----------|
| **Hard to refactor** | 是否使用宏？ |
| **Leak** | 是否使用 `new`？ |
| **UB** | 是否使用 `reinterpret_cast`？ |

## Thinking Prompt

1. **我能刪除這個 `new` 嗎？**
   - 使用 `make_unique`

2. **我能移除這個宏嗎？**
   - 使用 `constexpr` 或模板

## Quick Reference

| 反模式 | 現代修復 |
|--------|----------|
| **`new T`** | **`make_unique<T>`** |
| **`T*` ownership** | **`unique_ptr<T>`** |
| **`(T)ptr`** | **`static_cast<T>(ptr)`** |
| **`#define`** | **`constexpr`** |

## 相關概念

- [[entities/cpp/modern/m01-ownership]] - Master: Ownership（new/delete 是所有權問題）
- [[entities/cpp/modern/m14-mental-model]] - Master: Mental Models
- [[entities/cpp/modern/m02-resource]] - Master: Resource Management（raw pointer 是資源問題）

## 來源詳情

- [[sources/cpp-modern-skills]] - m15-anti-pattern: global variables, new/delete, C-style cast, macros, void*
