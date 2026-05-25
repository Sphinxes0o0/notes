---
type: entity
tags: [cpp, master, error-handling, exceptions, expected, contracts]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Error Handling Mental Model

## 核心問題

**這個錯誤可恢復嗎？**

- **Yes (Local)**: `std::expected` 或返回碼
- **Yes (Distant)**: 異常 (`throw`)
- **No (Bug)**: `assert` 或 `std::terminate`

## Error → Design Question

| 問題 | 設計問題 |
|------|----------|
| **Uncaught Exception** | 是否忘記了 catch，或在 `noexcept` 中拋出？ |
| **Silent Failure** | 是否忽略了返回碼？（使用 `[[nodiscard]]`） |
| **Destructor Throw** | 從不在析構函數中拋出（`std::terminate`）|

## Thinking Prompt

1. **缺席有效嗎？**
   - 是？→ `std::optional<T>`

2. **調用者需要詳細信息嗎？**
   - 是？→ `std::expected<T, E>` 或 Exception
   - 否？→ `bool` 或 `std::optional`

3. **這是邏輯錯誤（Bug）嗎？**
   - 是？→ `assert()` 或 `std::terminate()`

## Trace Up / Down

- **Trace Up**: "程序以 'terminate called recursively' 中止" → 異常在棧展開期間被拋出（在析構函數中）→ 修復析構函數。確保 RAII 清理是 `noexcept`

## Quick Reference

| 機制 | 開銷（成功） | 開銷（失敗）| 使用時機 |
|------|--------------|------------|----------|
| **`std::optional`** | 分支 | 分支 | 返回可能為空 |
| **`std::expected`** | 分支 | 分支 | 可恢復錯誤（解析）|
| **Exception** | 零 | 巨大 | 罕見 IO/資源錯誤 |
| **Assert** | 零（發布版）| 中止 | 邏輯錯誤 / 不變量 |

## 相關概念

- [[entities/cpp/modern/c17-06-error-handling]] - C++17 Error Handling 技能
- [[entities/cpp/modern/c17-13-domain-error]] - C++17 Domain Errors 技能
- [[entities/cpp/modern/m13-domain-error]] - Master: Domain Errors
- [[entities/cpp/modern/c17-05-type-driven]] - std::optional 是類型驅動錯誤處理的例子

## 來源詳情

- [[sources/cpp-modern-skills]] - m06-error-handling: exceptions, try-catch, noexcept, std::expected, error codes, assert
