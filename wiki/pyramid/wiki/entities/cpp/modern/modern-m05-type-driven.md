---
type: entity
tags: [cpp, master, type-driven, strong-types, type-safety]
created: 2026-05-27
sources: [github-modern-cpp-skills-m05]
---

# modern-m05-type-driven

## 定義

C++ 類型驅動設計的核心思維模型：**能否將這個 bug 變成編譯錯誤？**

## 核心問題

**能否將這個 bug 變成編譯錯誤？**

- **Primitive Obsession**: 用 `int` 表示 ID，用 `double` 表示金錢 — Bad
- **Strong Types**: `struct UserId`, `struct Money` — Good
- **Type State**: `Connection<OFF>` vs `Connection<ON>` — 狀態成為類型的一部分

## 關鍵要點

- 讓無效狀態在程序中不可表示
- 參數順序錯誤、單位混淆、狀態無效操作 — 這些都是類型系統可以消滅的 bug
- `enum class` 比 `enum` 更安全（無隱式 int 轉換）
- Phantom Type 通過模板標記狀態，不佔存儲空間
- User-defined literal 實現 `10_m`、`50_s` 這樣的單元安全
- Builder Pattern 的狀態變化通過返回不同類型來強制執行順序

## 常見錯誤映射

| 錯誤 | 設計問題 |
|------|----------|
| Swapped arguments | 是否把 `width` 傳給了 `height`？（用 Strong Types） |
| Invalid State | 是否在關閉的文件上調用了 `read()`？（用 Type State） |
| Unit confusion | 是否混淆了米和英尺？（用 `Dist<Meters>` 模板標籤） |

## 思維框架

1. **Is this `int` unique?** Yes → Wrap in `struct`. `struct UserId { int val; }` prevents `process(OrderId)`.
2. **Does valid usage depend on order?** Yes → Encode state in type. `Builder::port()` returns `BuilderWithPort`.
3. **Are units compatible?** No → Template tag. `Dist<Meters>` + `Dist<Feet>` cannot mix.

## 相關概念

- [[entities/cpp/modern/modern-m09-domain]] — DDD 與類型驅動設計一脈相承
- [[entities/cpp/modern/modern-m04-zero-cost]] — 模板是實現 Strong Types 的工具
- [[entities/cpp/modern/modern-m06-error-handling]] — `std::optional` 將"缺失"編碼為類型
- [[entities/cpp/modern/modern-m07-concurrency]] — 類型狀態可防止狀態機的並發bug
- [[entities/cpp/cpp20-features]] — Concepts 是類型約束的核心（C++20）

## Source

- [[sources/github-modern-cpp-skills-m05]]