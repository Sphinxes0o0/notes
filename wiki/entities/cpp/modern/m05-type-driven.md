---
type: entity
tags: [cpp, master, type-driven-design, strong-types, phantom-types]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Type-Driven Design Mental Model

## 核心問題

**我能讓這個 bug 成為編譯錯誤嗎？**

- **Primitive Obsession**: 用 `int` 表示 ID，用 `double` 表示金錢。壞
- **Strong Types**: `struct UserId`、`struct Money`。好
- **Type State**: `Connection<OFF>` vs `Connection<ON>`

## Error → Design Question

| 問題 | 設計問題 |
|------|----------|
| **Swapped arguments** | 是否把 `width` 傳給了 `height`？（使用強類型） |
| **Invalid State** | 是否在關閉的文件上調用了 `read()`？（使用類型狀態） |
| **Unit confusion** | 是否混合了米和英尺？（使用 `std::chrono` 風格的單位） |

## Thinking Prompt

1. **這個 `int` 是唯一的嗎？**
   - 是？→ 包裝在 `struct`
   - `struct UserId { int val; };` 防止 `process(OrderId)`

2. **有效使用是否依賴於順序？**
   - 是？→ 在類型中編碼狀態
   - `Builder::port()` 返回 `BuilderWithPort`

3. **單位是否兼容？**
   - 否？→ 模板標籤。`Dist<Meters>` + `Dist<Feet>`

## Trace Up / Down

- **Trace Up**: "火箭因公制和英制混淆而墜毀" → `double calculate_trajectory(double dist)` 接受任何數字 → `Dist<Meters> calculate(Dist<Meters> d)`。如果你傳英尺，編譯失敗
- **Trace Down**: "確保文件在讀取前已打開" → `File<Open> f = File<Closed>().open(); f.read();`

## Quick Reference

| 模式 | 開銷 | 使用時機 |
|------|------|----------|
| **Struct Wrapper** | 零 | 不同的 ID、坐標 |
| **Enum Class** | 零 | 類型安全標誌（無隱式 int 轉換） |
| **Phantom Type** | 零 | 跟踪狀態而不存儲 |
| **User Literal** | 零 | `10_m`、`50_s` |

## 相關概念

- [[entities/cpp/modern/c17-05-type-driven]] - C++17 Type-Driven Design 技能
- [[entities/cpp/modern/c17-04-templates]] - 模板支持強類型實現
- [[entities/cpp/modern/m09-domain]] - Master: Domain Modeling（Entity vs Value Object）
- [[entities/cpp/modern/m14-mental-model]] - Master: Mental Models

## 來源詳情

- [[sources/cpp-modern-skills]] - m05-type-driven: Strong types, phantom types, type state pattern, builder pattern
