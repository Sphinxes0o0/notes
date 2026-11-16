---
type: entity
tags: [cpp, master, ownership, move-semantics, raii, mental-model]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Ownership Mental Model

## 核心問題

**誰擁有這個資源，是否需要移動？**

在 C++ 中，所有權是一種紀律，而不僅僅是編譯器檢查。

## Error → Design Question

| 編譯器/ sanitizer 錯誤 | 設計問題 |
|------------------------|----------|
| **Double Free** | 誰擁有這個？是否拷貝了原始指針？ |
| **Use After Free** | 引用是否超出了其所有者的生命周期？ |
| **Memory Leak** | 析構函數在哪裡調用？（是否用了 `new`？） |
| **Object Slicing** | 為什麼按值傳遞而不是指針/引用？ |
| **Moved-from usage** | 為什麼在 `std::move` 後仍然使用變量？ |

## Thinking Prompt

1. **它需要堆分配嗎？**
   - 不？→ 棧值 (Rule of Zero)
   - 需要？→ `std::unique_ptr` (Rule of Zero)
   - 不要寫析構函數，除非管理非 RAII 的 C handle

2. **這是 Transfer 還是 Copy？**
   - Transfer？→ `std::move`
   - Copy？→ 拷貝構造函數（多態對象用 clone() 模式）

3. **這是 View 嗎？**
   - 是？→ `std::string_view`、`std::span` 或 `const T&`
   - 除非轉移共享所有權，否則不要傳 `std::shared_ptr`

## Trace Up / Down

- **Trace Up** (診斷): "Segfault / Heap Corruption" → 存在管理資源的原始指針 (`T*`)？→ 包裝在 `unique_ptr` 或 `vector`
- **Trace Down** (實現): "我想把大對象傳給函數，然後再也不見它" → `void consume(BigThing t);` + `consume(std::move(thing));`

## Quick Reference

| 模式 | 開銷 | 使用時機 |
|------|------|----------|
| **Value (Stack)** | 零 | 默認選擇，中小型對象 |
| **`unique_ptr`** | 零 | 需要堆，獨占所有權 |
| **`shared_ptr`** | 原子 Inc/Dec | 環形圖或真正的共享所有權 |
| **`T&` (Ref)** | 零 | 參數傳遞（非空） |
| **`T*` (Ptr)** | 零 | 參數傳遞（可空） |
| **`std::move`** | 零 | 轉移所有權 |

## 相關概念

- [[entities/cpp/move-semantics]] - 移動語義核心
- [[entities/cpp/raii]] - RAII 資源管理
- [[entities/cpp/smart-pointers]] - Smart Pointers 實現
- [[entities/cpp/modern/c17-01-ownership]] - C++17 Ownership 技能
- [[entities/cpp/modern/m02-resource]] - Master: Resource Management
- [[entities/cpp/modern/m12-lifecycle]] - Master: Lifecycle
- [[entities/cpp/modern/m15-anti-pattern]] - Master: Anti-Patterns（new/delete 是反模式）

## 來源詳情

- [[sources/cpp-modern-skills]] - m01-ownership: Move Semantics, RAII, Reference Safety
