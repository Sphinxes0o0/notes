---
type: source
source-type: github
title: "m15-anti-pattern — C++ Master: Anti-Patterns Mental Model"
author: "Sphinx Shi"
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m15-anti-pattern/SKILL.md
summary: "C++ Master-level skill for anti-patterns. Core question: Is this C or C++? Covers new/delete elimination, RAII, static_cast, constexpr vs macros, global variables, and reinterpret_cast avoidance."
tags: [cpp, master, anti-pattern, modernization, c-style]
---

# m15-anti-pattern — C++ Anti-Patterns

## 核心內容

**Core Question**: 這是 C 還是 C++？

- **C-Style**: `malloc`, `free`, `(int)x`, `void*`
- **C++ Style**: `std::vector`, `std::unique_ptr`, `static_cast`, templates

### Error → Design 映射

| 問題 | 設計問題 |
|------|----------|
| Hard to refactor | 是否在使用 Macros？ |
| Leak | 是否在使用 `new`？ |
| UB | 是否在使用 `reinterpret_cast`？ |

### 思維框架

1. **Can I delete this `new`?** Use `make_unique`.
2. **Can I remove this macro?** Use `constexpr` or templates.

### Quick Reference

| Anti-Pattern | Modern Fix |
|--------------|-----------|
| `new T` | `make_unique<T>` |
| `T*` ownership | `unique_ptr<T>` |
| `(T)ptr` | `static_cast<T>(ptr)` |
| `#define` | `constexpr` |

## 相關 Entity

- [[entities/cpp/modern/modern-m15-anti-pattern]]
- [[entities/cpp/modern/modern-m01-ownership]]
- [[entities/cpp/modern/modern-m02-resource]]
- [[entities/cpp/modern/modern-m12-lifecycle]]