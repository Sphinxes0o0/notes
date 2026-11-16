---
type: entity
tags: [cpp, master, domain-modeling, ddd, entity-value-object]
created: 2026-05-27
sources: [github-modern-cpp-skills-m09]
---

# modern-m09-domain

## 定義

C++ 領域驅動設計的核心思維模型：**這是身份還是值？**

## 核心問題

**身份還是值？**

- **Value Object**: 由屬性定義 (`Color`, `Money`) — 比較相等性，可拷貝
- **Entity**: 由身份定義 (`User`, `Socket`) — 由 ID 判等，通常不可拷貝

## 關鍵要點

- 值對象用 `struct` + `operator<=>` (C++20)
- 實體用 `class` + Deleted Copy + ID field
- 聚合根（Aggregate Root）通過 `std::vector` 或 `unique_ptr` 擁有子對象
- Repository 模式用純虛接口 (`virtual ... = 0`) 定義數據訪問抽象
- Pimpl  idiom 避免頭文件泄露實現細節
- 公開成員變量允許無效狀態，違反不變量

## 常見錯誤映射

| 錯誤 | 設計問題 |
|------|----------|
| Data Inconsistency | 公共字段是否允許無效狀態？ |
| Object Slicing | 是否按值傳遞了多態實體？ |
| Header Hell | 是否泄露了實現細節？（用 Pimpl） |

## 思維框架

1. **Is it copyable?** Yes → Value Type (Rule of Zero, defaults). No → Entity (Delete copy ctor, enable move).
2. **Does it have invariants?** Yes → `class` with private data + public methods. No → `struct` (POD).
3. **Does it own others?** Aggregate Root → Owns children via `std::vector` / `unique_ptr`.

## 相關概念

- [[entities/cpp/modern/modern-m05-type-driven]] — 類型驅動設計與 DDD 一脈相承
- [[entities/cpp/modern/modern-m01-ownership]] — 實體的所有權由聚合根管理
- [[entities/cpp/modern/modern-m04-zero-cost]] — 值對象適合用模板靜態多態
- [[entities/cpp/modern/modern-m02-resource]] — 資源所有權是 DDD 聚合的核心
- [[entities/cpp/modern/modern-m12-lifecycle]] — 對象生命周期由 DDD 邊界定義
- [[entities/cpp/modern/modern-m06-error-handling]] — 領域事件是一種錯誤處理策略

## Source

- [[sources/github-modern-cpp-skills-m09]]