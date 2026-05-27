---
type: entity
tags: [cpp, master, mutability, const-correctness, concurrency]
created: 2026-05-27
sources: [github-modern-cpp-skills-m03]
---

# modern-m03-mutability

## 定義

C++ Const 正確性與可變性的核心思維模型：**誰被允許改變這個狀態？**

## 核心問題

**誰被允許改變這個狀態？**

C++ 默認是 **Mutable**。你必須主動選擇安全：
- **API Contract**: `const` 方法承諾不改變可見狀態
- **Physical Constness**: 編譯器確保比特位不改變
- **Logical Constness**: 用 `mutable` 改變隱藏狀態（如緩存）於 `const` 方法中

## 關鍵要點

- 變量默認用 `const`，方法默認加 `const` 限定
- `mutable` 成員在 `const` 方法中可以被修改，通常用於緩存/memoization
- `mutable` + 多線程 = 必須加鎖，否則數據競爭
- `const` 方法天然線程安全（讀者），但 `mutable` 成員需要 `std::mutex` 保護
- `std::shared_mutex` 實現讀者-寫者鎖：`shared_lock` 多讀，`unique_lock` 單寫

## 常見錯誤映射

| 錯誤 | 設計問題 |
|------|----------|
| Discarded qualifiers | 是否在 `const` 函數中修改了成員數據？ |
| Data Race | `mutable` 字段是否從多線程修改而未加鎖？ |
| Iterator Invalidation | 讀取容器時是否同時在修改？ |

## 思維框架

1. **Should this be `const`?** Variables: Yes. Methods: Yes unless it must modify state.
2. **Is internal state 'invariant' or 'cache'?** Cache → `mutable` + `std::mutex`. State → non-const method.
3. **Is it thread-safe?** `const` methods imply safe concurrent reads. `mutable` members MUST be protected.

## 相關概念

- [[entities/cpp/modern/modern-m07-concurrency]] — `mutable` 在並發語境下需要 mutex
- [[entities/cpp/modern/modern-m02-resource]] — `std::mutex` 是可變狀態的資源
- [[entities/cpp/constexpr]] — `constexpr` 是編譯期不可變性
- [[entities/cpp/modern/modern-m14-mental-model]] — 內存視圖：值與引用的區別
- [[entities/cpp/concurrency]] — C++ 並發編程的完整棧

## Source

- [[sources/github-modern-cpp-skills-m03]]