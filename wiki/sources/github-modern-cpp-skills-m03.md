---
type: source
source-type: github
title: "m03-mutability — C++ Master: Const Correctness Mental Model"
author: "Sphinx Shi"
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m03-mutability/SKILL.md
summary: "C++ Master-level skill for mutability and const correctness. Core question: Who is allowed to change this state? Covers const, mutable, logical vs bitwise const, and thread-safe mutable."
tags: [cpp, master, mutability, const-correctness]
---

# m03-mutability — C++ Const Correctness & Mutability

## 核心內容

**Core Question**: 誰被允許改變這個狀態？

C++ 默認為 **Mutable**。必須主動選擇安全：
- **API Contract**: `const` 方法承諾不改變可見狀態
- **Physical Constness**: 編譯器確保比特位不改變
- **Logical Constness**: `mutable` 改變隱藏狀態（緩存）於 `const` 方法中

### Error → Design 映射

| 錯誤 | 設計問題 |
|------|----------|
| Discarded qualifiers | 是否在 `const` 函數中修改了成員數據？ |
| Data Race | `mutable` 字段是否從多線程修改而未加鎖？ |
| Iterator Invalidation | 讀取容器時是否同時在修改？ |

### 思維框架

1. **Should this be `const`?** Variables: Yes. Methods: Yes unless it must modify state.
2. **Is internal state 'invariant' or 'cache'?** Cache → `mutable` + `std::mutex`. State → non-const method.
3. **Is it thread-safe?** `const` methods imply safe concurrent reads. `mutable` members MUST be protected.

### Quick Reference

| Keyword | Meaning | Use When |
|---------|---------|----------|
| `const` | Read-only access | Parameters, local vars, getters. |
| `constexpr` | Compile-time constant | Constants, array sizes. |
| `mutable` | Modifiable in const | Caches, Mutexes within a class. |
| `std::mutex` | Exclusive Lock | Protecting mutable state. |
| `std::shared_mutex` | Read/Write Lock | Rare updates, frequent reads. |

## 相關 Entity

- [[entities/cpp/modern/modern-m03-mutability]]
- [[entities/cpp/modern/modern-m07-concurrency]]
- [[entities/cpp/constexpr]]