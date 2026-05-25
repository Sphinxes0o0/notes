---
type: entity
tags: [cpp, master, domain-modeling, ddd, entity, value-object, aggregate]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Domain Modeling Mental Model

## 核心問題

**身份還是值？**

- **Value Object**: 由屬性定義（`Color`、`Money`）。相等性通過比較。不可拷貝
- **Entity**: 由身份定義（`User`、`Socket`）。相等性通過 ID。不可拷貝（通常）

## Error → Design Question

| 問題 | 設計問題 |
|------|----------|
| **Data Inconsistency** | 公共字段是否允許無效狀態？ |
| **Object Slicing** | 是否按值傳遞多態 Entities？ |
| **Header Hell** | 是否洩露了實現細節？（使用 Pimpl）|

## Thinking Prompt

1. **它可拷貝嗎？**
   - 是？→ 值類型（Rule of Zero，defaults）
   - 否？→ Entity（刪除拷貝構造函數，啟用移動）

2. **它有不變量嗎？**
   - 是？→ `class` + 私有數據 + 公共方法
   - 否？→ `struct` (POD)

3. **它擁有其他對象嗎？**
   - Aggregate Root？→ 通過 `std::vector` / `unique_ptr` 擁有子節點

## Trace Up / Down

- **Trace Down**: "User 有 Name 和 Address" → `class User` (Entity) 包含 `Name` (Value) 和 `Address` (Value)

## Quick Reference

| 模式 | C++ 實現 |
|------|----------|
| **Value Object** | `struct` + `operator<=>` |
| **Entity** | `class` + 刪除拷貝 + ID 字段 |
| **Repository** | 純虛擬接口 (`virtual ... = 0`) |
| **Aggregate** | 擁有子節點的父類 |

## 相關概念

- [[entities/cpp/modern/c17-09-domain]] - C++17 DDD 技能
- [[entities/cpp/modern/c17-05-type-driven]] - Type-Driven Design
- [[entities/cpp/modern/m05-type-driven]] - Master: Type-Driven Design

## 來源詳情

- [[sources/cpp-modern-skills]] - m09-domain: Entity, Value Object, Aggregate, Repository, Pimpl, Invariant
