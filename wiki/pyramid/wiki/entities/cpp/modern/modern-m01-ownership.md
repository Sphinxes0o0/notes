---
type: entity
tags: [cpp, master, ownership, move-semantics, raii]
created: 2026-05-27
sources: [github-modern-cpp-skills-m01]
---

# modern-m01-ownership

## 定義

C++ 資源所有權與移動語義的核心思維模型：**誰擁有這個資源，是否需要轉移？**

## 核心問題

**誰擁有這個資源，是否需要轉移？**

- **Scope-bound?** → Stack (RAII)
- **Exclusive?** → `std::unique_ptr`
- **Shared?** → `std::shared_ptr`
- **View?** → `T*` 或 `T&` (non-owning)

## 關鍵要點

- C++ 所有權是一種約定，而非編譯器強制
- 從原始指針遷移到智能指針是消除內存洩漏的核心手段
- `std::move` 僅轉移所有權，不做任何複製
- 移動後的對象處於"有效但未指定狀態"，不應再使用
- 複製構造和移動構造的選擇決定了語義：Copy = 複製，Move = 轉移

## 常見錯誤映射

| 錯誤 | 設計問題 |
|------|----------|
| Double Free | 誰擁有資源？是否複製了原始指針？ |
| Use After Free | 引用是否超出了其所有者的生命周期？ |
| Memory Leak | 析構函數在哪裡被調用？是否用了 `new`？ |
| Object Slicing | 為什麼按值傳遞而不是指針/引用？ |
| Moved-from usage | 為什麼在 `std::move` 後還訪問該變量？ |

## 思維框架

1. **Does it need heap?** No → Stack (Rule of Zero). Yes → `unique_ptr`. Never write destructor unless managing non-RAII C handle.
2. **Transfer or Copy?** Transfer → `std::move`. Copy → Copy Constructor.
3. **Is it a view?** Yes → `string_view`, `span`, or `const T&`. Never pass `shared_ptr` for views.

## 相關概念

- [[entities/cpp/modern/modern-m02-resource]] — Smart Pointers 是所有權的具體實現
- [[entities/cpp/modern/modern-m12-lifecycle]] — 對象何時死亡是所有權的時間維度
- [[entities/cpp/modern/modern-m15-anti-pattern]] — `new`/`malloc` 是所有權問題的根源
- [[entities/cpp/modern/modern-m07-concurrency]] — 並發中所有權共享需要特別注意
- [[entities/cpp/raii]] — RAII 是所有權約定的基石
- [[entities/cpp/move-semantics]] — 移動語義是所有權轉移的核心機制

## Source

- [[sources/github-modern-cpp-skills-m01]]