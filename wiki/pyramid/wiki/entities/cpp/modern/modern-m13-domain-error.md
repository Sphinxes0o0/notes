---
type: entity
tags: [cpp, master, domain-error, exception-hierarchy]
created: 2026-05-27
sources: [github-modern-cpp-skills-m13]
---

# modern-m13-domain-error

## 定義

C++ 領域錯誤處理的核心思維模型：**誰來捕獲這個錯誤？**

## 核心問題

**誰來捕獲這個？**

- **Exception**: 繼承 `std::runtime_error`
- **System Error**: `std::error_code` (OS codes)

## 關鍵要點

- 領域錯誤（如 `InsufficientFunds`）是業務邏輯的異常，用異常類型表示
- 異常需要上下文時，定義子類：`struct FileError : std::runtime_error { std::filesystem::path p; }`
- `std::runtime_error`：大多數失敗的基類
- `std::logic_error`：程序員錯誤（違反前條件），即 bug
- `std::expected`：可見的失敗路徑，不依賴異常機制
- 異常層次結構讓捕獲者可以精確控制：只 catch 需要處理的類型

## 思維框架

1. **Is it a domain event?** `InsufficientFunds` is an exception type.
2. **Does it have context?** "File not found" needs "Which file?" → `struct FileError : std::runtime_error { path p; }`

## 相關概念

- [[entities/cpp/modern/modern-m06-error-handling]] — 領域錯誤是錯誤處理的一個子集
- [[entities/cpp/modern/modern-m09-domain]] — DDD 中的領域事件是一種錯誤表示
- [[entities/cpp/modern/modern-m12-lifecycle]] — 異常棧展開期間析構函數的行為
- [[entities/cpp/modern/modern-m05-type-driven]] — `std::expected` 將錯誤編碼為類型

## Source

- [[sources/github-modern-cpp-skills-m13]]