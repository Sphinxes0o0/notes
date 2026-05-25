---
type: entity
tags: [cpp, master, zero-cost-abstractions, templates, polymorphism, concepts]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Zero-Cost Abstractions

## 核心問題

**我們何時確定類型？**

- **編譯時** (Static): 模板、Concepts、CRTP。零運行時開銷，更大的二進制
- **運行時** (Dynamic): 虛函數、`std::any`、`std::variant`。靈活，vtable 開銷

## Error → Design Question

| 問題 | 設計問題 |
|------|----------|
| **Template spew** | 是否缺少 Concepts 約束？ |
| **Linker error** | 是否在 .cpp 而不是 .h 中定義模板？ |
| **Object slicing** | 是否將 Derived 賦值給 Base 值？ |
| **Slow build** | 是否過度使用頭文件/模板？ |

## Thinking Prompt

1. **類型集在編譯時已知嗎？**
   - 是？→ 模板或 `std::variant`
   - 否？→ 繼承（虛函數）

2. **我需要將它們存儲在列表中嗎？**
   - 同質？→ `std::vector<T>`
   - 異質？→ `std::vector<std::unique_ptr<Base>>` 或 `std::vector<std::variant<...>>`

3. **接口是否完全匹配？**
   - 需要 Duck typing？→ 模板（Concepts）
   - 嚴格層次結構？→ 繼承

## Trace Up / Down

- **Trace Up**: "緊密循環中虛函數調用太慢" → 間接分支預測失誤 → 如果類型已知，切換到靜態多態（CRTP 或模板）
- **Trace Down**: "我想要一個接受任何有 `.draw()` 方法的函數" → `void render(Drawable auto& item) { item.draw(); }` (C++20)

## Quick Reference

| 模式 | 分派 | 開銷 | 使用時機 |
|------|------|------|----------|
| **`virtual`** | 動態 | Vtable + 緩存未命中 | 插件、運行時擴展 |
| **Template** | 靜態 | 代碼膨脹 | 高性能、類型推導 |
| **`std::function`** | 動態 | 分配 + 間接 | 存儲回調 |
| **`std::variant`** | 靜態分支 | 分支 switch | 封閉類型集 |
| **CRTP** | 靜態 | 零 | 靜態繼承 |

## 相關概念

- [[entities/cpp/variadic-templates]] - 模板變參
- [[entities/cpp/cpp20-features]] - C++20 Concepts（比 SFINAE 更清晰）
- [[entities/cpp/modern/c17-04-templates]] - C++17 Templates 技能
- [[entities/cpp/modern/c17-05-type-driven]] - 類型驅動設計

## 來源詳情

- [[sources/cpp-modern-skills]] - m04-zero-cost: Templates, Concepts, Virtual, CRTP, static vs dynamic polymorphism
