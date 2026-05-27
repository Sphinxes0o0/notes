---
type: entity
tags: [cpp, master, anti-pattern, modernization, c-style]
created: 2026-05-27
sources: [github-modern-cpp-skills-m15]
---

# modern-m15-anti-pattern

## 定義

C++ 常見 Anti-Pattern 識別與修正的核心思維模型：**這是 C 還是 C++？**

## 核心問題

**這是 C 還是 C++？**

- **C-Style**: `malloc`, `free`, `(int)x`, `void*`
- **C++ Style**: `std::vector`, `std::unique_ptr`, `static_cast`, templates

## 關鍵要點

- `new T` → `make_unique<T>` (或 `make_shared<T>`)：消除內存洩漏
- `T*` ownership → `unique_ptr<T>`：明確所有權
- C-style cast `(T)ptr` → `static_cast<T>(ptr)`：精確控制轉換類型
- `#define` → `constexpr`：類型安全，編譯器理解
- `reinterpret_cast`：幾乎總是 UB 的信號，慎重使用
- Macros：難以重構，無類型檢查，調試困難
- 全局變量：隱藏依賴，難以測試，難以並發安全

## 常見錯誤映射

| 問題 | 設計問題 |
|------|----------|
| Hard to refactor | 是否在使用 Macros？ |
| Leak | 是否在使用 `new`？ |
| UB | 是否在使用 `reinterpret_cast`？ |

## 思維框架

1. **Can I delete this `new`?** Use `make_unique`.
2. **Can I remove this macro?** Use `constexpr` or templates.

## 相關概念

- [[entities/cpp/modern/modern-m01-ownership]] — `new`/`delete` 是所有權問題的核心
- [[entities/cpp/modern/modern-m02-resource]] — `unique_ptr` 消滅 `new`/`delete`
- [[entities/cpp/modern/modern-m12-lifecycle]] — 顯式 `delete` 是生命周期管理的陷阱
- [[entities/cpp/modern/modern-m14-mental-model]] — `void*` 缺乏類型信息
- [[entities/cpp/modern/modern-m06-error-handling]] — 異常處理 vs 返回碼
- [[entities/cpp/modern/modern-m10-performance]] — 手動內存管理 vs `std::vector`

## Source

- [[sources/github-modern-cpp-skills-m15]]