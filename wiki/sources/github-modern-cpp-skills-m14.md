---
type: source
source-type: github
title: "m14-mental-model — C++ Master: Pointer vs Reference Mental Model"
author: "Sphinx Shi"
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m14-mental-model/SKILL.md
summary: "C++ Master-level skill for C++ mental models. Core question: What happens in memory? Covers value vs reference vs pointer, initialization, undefined behavior, and std::move semantics."
tags: [cpp, master, mental-model, pointer, reference, undefined-behavior]
---

# m14-mental-model — C++ Mental Models

## 核心內容

**Core Question**: 內存中發生了什麼？

- **Value**: 是否擁有這些字節？
- **Reference**: 是否是別名？
- **Pointer**: 是否可為空（需要檢查）？

### 思維框架

1. **Is it a copy or reference?** `auto x = y` (Copy). `auto& x = y` (Reference).
2. **Does it dangle?** Returning `&local` is always wrong.
3. **Is this UB?** Compiler assumes UB never happens — optimizations may break your code.

### Quick Reference

| Concept | Mental Model |
|---------|-------------|
| `T&` | Guaranteed Alias. |
| `T*` | Nullable Address (Requires check). |
| `std::move` | Cast to rvalue (Prepare to steal). |

## 相關 Entity

- [[entities/cpp/modern/modern-m14-mental-model]]
- [[entities/cpp/modern/modern-m01-ownership]]
- [[entities/cpp/modern/modern-m12-lifecycle]]