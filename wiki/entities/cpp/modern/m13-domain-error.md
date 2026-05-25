---
type: entity
tags: [cpp, master, domain-errors, exception-hierarchies, system-errors]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Domain Errors Mental Model

## 核心問題

**誰捕獲這個？**

- **Exception**: 繼承 `std::runtime_error`
- **System Error**: `std::error_code`（OS 代碼）

## Thinking Prompt

1. **這是領域事件嗎？**
   - `InsufficientFunds` 是異常類型

2. **它有上下文嗎？**
   - "File not found" 需要 "哪個文件？"
   - `struct FileError : std::runtime_error { std::filesystem::path p; ... }`

## Quick Reference

| 模式 | 使用場景 |
|------|----------|
| **`std::runtime_error`** | 大多數失敗的基礎 |
| **`std::logic_error`** | Bug（違反前置條件）|
| **`std::expected`** | 可見的失敗路徑 |

## 相關概念

- [[entities/cpp/modern/c17-06-error-handling]] - C++17 Error Handling 技能
- [[entities/cpp/modern/c17-13-domain-error]] - C++17 Domain Errors 技能
- [[entities/cpp/modern/m06-error-handling]] - Master: Error Handling

## 來源詳情

- [[sources/cpp-modern-skills]] - m13-domain-error: Exception hierarchies, system errors, expected
