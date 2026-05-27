---
type: source
source-type: github
title: "m02-resource — C++ Master: Smart Pointers Mental Model"
author: "Sphinx Shi"
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m02-resource/SKILL.md
summary: "C++ Master-level skill for smart pointers. Core question: How many owners does this resource have? Covers unique_ptr (90%), shared_ptr, weak_ptr, make_unique, custom deleters, and cycle detection."
tags: [cpp, master, resource, smart-pointers]
---

# m02-resource — C++ Smart Pointers

## 核心內容

**Core Question**: 這個資源有多少個所有者？

- **One**: `std::unique_ptr` (90% of cases)
- **Many**: `std::shared_ptr`
- **Observer**: `std::weak_ptr`

### Error → Design 映射

| 錯誤 | 設計問題 |
|------|----------|
| Memory Leak (Cycles) | `shared_ptr` 是否形成循環引用？ |
| Dangling Pointer | `weak_ptr` 使用前是否檢查了 `lock()`？ |
| Double Free | 是否有兩個 `unique_ptr` 來自同一原始指針？ |
| 性能問題 | 是否不必要拷貝了 `shared_ptr`？ |

### 思維框架

1. **Can I use `unique_ptr`?** Always start here. Zero overhead.
2. **Is this a cycle?** Parent → Child (`shared_ptr`) + Child → Parent (`weak_ptr`).
3. **Do I need a custom deleter?** Managing C-API? `unique_ptr<FILE, decltype(&fclose)>`.

### Quick Reference

| Pattern | Cost | Use When |
|---------|------|----------|
| `make_unique` | Zero | Creating new heap objects. |
| `make_shared` | 1 Alloc | Creating access-controlled shared objects. |
| `weak_ptr` | Control Block | Breaking cycles, Caching. |
| `enable_shared_from_this` | Zero | Need `shared_from_this()` inside member function. |

## 相關 Entity

- [[entities/cpp/modern/modern-m02-resource]]
- [[entities/cpp/modern/modern-m01-ownership]]
- [[entities/cpp/modern/modern-m15-anti-pattern]]