---
type: entity
tags: [cpp, master, error-handling, exceptions, expected]
created: 2026-05-27
sources: [github-modern-cpp-skills-m06]
---

# modern-m06-error-handling

## 定義

C++ 錯誤處理的核心思維模型：**這個錯誤可恢復嗎？**

## 核心問題

**這個錯誤可恢復嗎？**

- **Yes (Local)**: `std::expected<T, E>` 或返回碼
- **Yes (Distant)**: 異常 (`throw`)
- **No (Bug)**: `assert` 或 `std::terminate`

## 關鍵要點

- `std::optional<T>`：值可能缺失（不承擔錯誤信息）
- `std::expected<T, E>`：值可能缺失且需要承載錯誤信息（C++23）
- Exception：對罕見 IO/資源錯誤，happy path 零開銷
- Assert：邏輯錯誤/不變量，Release 模式無開銷
- `[[nodiscard]]`：強制檢查返回值，防止靜默失敗
- **千萬別在 destructor 中拋異常** — 導致 `std::terminate`

## 常見錯誤映射

| 錯誤 | 設計問題 |
|------|----------|
| Uncaught Exception | 是否忘記了 catch，或在 `noexcept` 中拋出？ |
| Silent Failure | 是否忽視了返回碼？（用 `[[nodiscard]]`） |
| Destructor Throw | 是否在析構函數中拋出異常？ |

## 思維框架

1. **Is absence valid?** Yes → `std::optional<T>`.
2. **Does caller need details?** Yes → `std::expected<T, E>` or Exception. No → `bool` or `std::optional`.
3. **Is it a logic error (bug)?** Yes → `assert()` or `std::terminate()`. Do not throw for bugs.

## 相關概念

- [[entities/cpp/modern/modern-m13-domain-error]] — 領域錯誤是錯誤處理的特定場景
- [[entities/cpp/modern/modern-m12-lifecycle]] — 析構函數中的錯誤處理約束
- [[entities/cpp/modern/modern-m03-mutability]] — `noexcept` 是 const 方法的承諾
- [[entities/cpp/modern/modern-m05-type-driven]] — `std::expected` 將錯誤編碼為類型
- [[entities/cpp/modern/modern-m14-mental-model]] — 異常的語義是棧展開

## Source

- [[sources/github-modern-cpp-skills-m06]]