---
type: source
source-type: github
title: "m12-lifecycle — C++ Master: Lifecycle Mental Model"
author: Sphinx Shi
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m12-lifecycle/SKILL.md
summary: "C++ Master-level skill for object lifecycle. Core question: When does this die? Covers Stack vs Heap vs Static, RAII, destructors, Rule of 5, static initialization order fiasco, and Meyers Singleton."
tags: [cpp, master, lifecycle, raii, rule-of-5]
created: 2026-05-27
---
# m12-lifecycle — C++ Resource Lifecycle

## 核心內容

**Core Question**: 對象何時死亡？

- **Stack**: 到達 `}` 作用域末尾
- **Heap**: 當 `delete`（或智能指針釋放）發生
- **Static**: 程序退出時（反向初始化順序）

### Error → Design 映射

| 錯誤 | 設計問題 |
|------|----------|
| Resource Leak | 是否手動 `open()` 而沒有封裝類？ |
| Use After Free | 是否在 lambda/線程中捕獲了局部變量的引用？ |
| Static Fiasco | 靜態對象是否相互依賴？（用 Meyers Singleton） |

### 思維框架

1. **Does it have a destructor?** Yes → RAII. Good. No → Wrap it.
2. **Does it copy?** `FILE*` cannot copy. Delete copy constructor.
3. **Use after free?** Never capture reference to local in lambda/thread.

### Quick Reference

| Pattern | Use Case |
|---------|----------|
| RAII Wrapper | `FileHandle`, `LockGuard`. |
| Scope Guard | `std::scope_exit` (Cleanup callback). |
| Rule of 5 | Copy/Move/Destructor implementation logic. |

## 相關 Entity

- [[entities/cpp/modern/modern-m12-lifecycle]]
- [[entities/cpp/modern/modern-m01-ownership]]
- [[entities/cpp/modern/modern-m07-concurrency]]
- [[entities/cpp/raii]]