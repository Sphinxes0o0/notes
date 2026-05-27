---
type: source
source-type: github
title: "m04-zero-cost — C++ Master: Zero-Cost Abstractions Mental Model"
author: "Sphinx Shi"
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m04-zero-cost/SKILL.md
summary: "C++ Master-level skill for zero-cost abstractions. Core question: When do we determine the type? Covers templates, concepts, CRTP, virtual functions, std::variant, and static vs dynamic polymorphism."
tags: [cpp, master, zero-cost, templates, polymorphism]
---

# m04-zero-cost — C++ Zero-Cost Abstractions

## 核心內容

**Core Question**: 何時確定類型？

- **編譯時 (Static)**: Templates, Concepts, CRTP — 零運行時開銷，代碼膨脹
- **運行時 (Dynamic)**: 虛函數，`std::any`，`std::variant` — 靈活，vtable 開銷

### Error → Design 映射

| 錯誤 | 設計問題 |
|------|----------|
| Template spew | 是否缺少 Concepts 約束？ |
| Linker error | 是否在 .cpp 中定義了模板？ |
| Object slicing | 是否將 Derived 賦值給 Base 值？ |
| Slow build | 是否過度使用模板/頭文件？ |

### 思維框架

1. **Is the set of types known at compile time?** Yes → Templates or `std::variant`. No → Inheritance.
2. **Do I need to store them in a list?** Homogeneous → `vector<T>`. Heterogeneous → `vector<unique_ptr<Base>>` or `variant<...>`.
3. **Does the interface match exactly?** Duck typing → Templates (Concepts). Strict hierarchy → Inheritance.

### Quick Reference

| Pattern | Dispatch | Cost | Use When |
|---------|----------|------|----------|
| `virtual` | Dynamic | Vtable + Cache miss | Plugins, Runtime extensions. |
| Template | Static | Code bloat | High perf, Type deduction. |
| `std::function` | Dynamic | Alloc + Indirect | Storing callbacks. |
| `std::variant` | Static branching | Branch switch | Closed set of types. |
| CRTP | Static | Zero | Static inheritance. |

## 相關 Entity

- [[entities/cpp/modern/modern-m04-zero-cost]]
- [[entities/cpp/modern/modern-m05-type-driven]]
- [[entities/cpp/modern/modern-m10-performance]]