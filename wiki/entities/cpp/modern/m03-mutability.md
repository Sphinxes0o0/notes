---
type: entity
tags: [cpp, master, mutability, const-correctness, thread-safety]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Mutability Mental Model

## 核心問題

**誰允許改變這個狀態？**

C++ 默認為 **Mutable**。你必須通過 `const` 主動選擇安全。

- **API Contract**: `const` 方法承諾不改變可見狀態
- **Physical Constness**: 編譯器確保位不變
- **Logical Constness**: 使用 `mutable` 改變隱藏狀態（如緩存）

## Error → Design Question

| 問題 | 設計問題 |
|------|----------|
| **Discarded qualifiers** | 是否在 `const` 函數中試圖修改成員數據？ |
| **Data Race** | 是否在沒有鎖定的情況下從多個線程修改 `mutable` 字段？ |
| **Iterator Invalidation** | 是否在修改容器的同時讀取它？ |

## Thinking Prompt

1. **這應該是 `const` 嗎？**
   - 變量：是的，默認為 `const` 或 `constexpr`
   - 方法：是的，除非它必須修改狀態
   - 指針：`const T*`（指向 const 的指針）vs `T* const`（const 指針）

2. **內部狀態是 'invariant' 還是 'cache'？**
   - Cache/Memoization？→ 使用 `mutable` + `std::mutex`
   - 實際狀態？→ 非 const 方法

3. **它是線程安全的嗎？**
   - `const` 方法意味著並發讀者是安全的
   - `mutable` 成員在 `const` 方法中必須受同步保護

## Trace Up / Down

- **Trace Up**: "多線程應用中的未定義行為" → `const` 方法在沒有鎖的情況下修改了 `mutable` 緩存，假設 `const` 意味著安全 → 添加 `std::mutex`
- **Trace Down**: "我需要一個線程安全的查找表" → `std::shared_mutex` 允許多讀者（`shared_lock`）和單寫者（`unique_lock`）

## Quick Reference

| 關鍵字 | 含義 | 使用時機 |
|--------|------|----------|
| **`const`** | 只讀訪問 | 參數、局部變量、getter |
| **`constexpr`** | 編譯時常數 | 常量、數組大小 |
| **`mutable`** | 在 const 方法中可修改 | 緩存、類內 mutex |
| **`std::mutex`** | 獨占鎖 | 保護可變狀態 |
| **`std::shared_mutex`** | 讀/寫鎖 | 罕見更新、頻繁讀取 |

## 相關概念

- [[entities/cpp/constexpr]] - constexpr 編譯時計算
- [[entities/cpp/modern/c17-03-mutability]] - C++17 Const Correctness 技能
- [[entities/cpp/modern/c17-07-concurrency]] - C++17 Concurrency（mutable + 線程安全）
- [[entities/cpp/modern/m07-concurrency]] - Master: Concurrency

## 來源詳情

- [[sources/cpp-modern-skills]] - m03-mutability: const, mutable, logical vs bitwise const, data race, mutex
