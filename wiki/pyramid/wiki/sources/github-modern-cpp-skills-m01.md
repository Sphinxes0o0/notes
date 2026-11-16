---
type: source
source-type: github
title: "m01-ownership — C++ Master: Ownership Mental Model"
author: Sphinx Shi
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m01-ownership/SKILL.md
summary: "C++ Master-level skill for ownership, move semantics, and RAII. Core question: Who owns this resource and does it need to move? Includes Error → Design mapping and Trace Up/Down framework."
tags: [cpp, master, ownership, move-semantics, raii]
created: 2026-05-27
---
# m01-ownership — C++ Ownership & Move Semantics

## 核心內容

**Core Question**: 誰擁有這個資源，是否需要轉移？

C++ 所有權是一種約定而非編譯器強制：
- **Scope-bound?** → Stack (RAII)
- **Exclusive?** → `std::unique_ptr`
- **Shared?** → `std::shared_ptr`
- **View?** → `T*` 或 `T&` (non-owning)

### Error → Design 映射

| 錯誤 | 設計問題 |
|------|----------|
| Double Free | 誰擁有資源？是否複製了原始指針？ |
| Use After Free | 引用是否超出所有者生命周期？ |
| Memory Leak | 析構函數在哪裡被調用？是否用了 `new`？ |
| Object Slicing | 為什麼按值傳遞而不是指針/引用？ |

### 思維框架

1. **Does it need heap?** No → Stack (Rule of Zero). Yes → `unique_ptr`.
2. **Transfer or Copy?** Transfer → `std::move`. Copy → Copy Constructor.
3. **Is it a view?** Yes → `string_view`, `span`, or `const T&`.

### Quick Reference

| Pattern | Cost | Use When |
|---------|------|----------|
| Value (Stack) | Zero | Default choice. Small/Medium objects. |
| `unique_ptr` | Zero | Heap needed. Exclusive ownership. |
| `shared_ptr` | Atomic Inc/Dec | Cyclic graph or true shared ownership. |
| `T&` (Ref) | Zero | Parameter passing (non-null). |
| `T*` (Ptr) | Zero | Parameter passing (nullable). |
| `std::move` | Zero | Transferring ownership. |

## 相關 Entity

- [[entities/cpp/modern/modern-m01-ownership]]
- [[entities/cpp/modern/modern-m02-resource]]
- [[entities/cpp/modern/modern-m12-lifecycle]]
- [[entities/cpp/modern/modern-m15-anti-pattern]]