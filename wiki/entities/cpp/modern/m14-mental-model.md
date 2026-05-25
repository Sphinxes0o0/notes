---
type: entity
tags: [cpp, master, mental-model, pointer, reference, undefined-behavior]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Mental Models

## 核心問題

**內存中發生了什麼？**

- **Value**: 它是否擁有自己的字節？
- **Reference**: 它是別名嗎？
- **Pointer**: 它可空嗎？

## Thinking Prompt

1. **這是拷貝還是引用？**
   - `auto x = y`（拷貝）
   - `auto& x = y`（引用）

2. **它是否 dangling？**
   - 返回 `&local` 總是錯誤的

## Quick Reference

| 概念 | 思維模型 |
|------|----------|
| **`T&`** | 保證別名 |
| **`T*`** | 可空地址（需要檢查）|
| **`std::move`** | 轉換為 rvalue（準備竊取）|

## 相關概念

- [[entities/cpp/modern/m01-ownership]] - Master: Ownership
- [[entities/cpp/modern/m15-anti-pattern]] - Master: Anti-Patterns
- [[entities/cpp/modern/m05-type-driven]] - Master: Type-Driven Design

## 來源詳情

- [[sources/cpp-modern-skills]] - m14-mental-model: Pointer vs Reference, Initialization, Undefined Behavior
