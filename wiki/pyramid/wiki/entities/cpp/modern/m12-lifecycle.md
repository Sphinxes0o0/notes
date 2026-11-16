---
type: entity
tags: [cpp, master, lifecycle, raii, destructors, static-initialization]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Resource Lifecycle Mental Model

## 核心問題

**這個何時死亡？**

- **Stack**: 作用域結束 `}`
- **Heap**: 當 `delete`（或智能指針 drop）發生時
- **Static**: 程序退出時（反向初始化順序）

## Error → Design Question

| 問題 | 設計問題 |
|------|----------|
| **Resource Leak** | 是否手動 `open()` 而沒有包裝類？ |
| **Use After Free** | 是否在 lambda/線程中捕獲了局部變量的引用？ |
| **Static Fiasco** | 是否 statics 相互依賴？（使用 Meyers Singleton）|

## Thinking Prompt

1. **它有析構函數嗎？**
   - 是 → RAII。好
   - 否 → 包裝它

2. **它拷貝嗎？**
   - `FILE*` 不能拷貝。刪除拷貝構造函數

## Quick Reference

| 模式 | 使用場景 |
|------|----------|
| **RAII Wrapper** | `FileHandle`、`LockGuard` |
| **Scope Guard** | `std::scope_exit`（清理回調）|
| **Rule of 5** | Copy/Move/Destructor 實現邏輯 |

## 相關概念

- [[entities/cpp/raii]] - 現有 RAII entity
- [[entities/cpp/modern/c17-01-ownership]] - 所有權與 RAII
- [[entities/cpp/modern/c17-12-lifecycle]] - C++17 Lifecycle 技能
- [[entities/cpp/modern/m01-ownership]] - Master: Ownership

## 來源詳情

- [[sources/cpp-modern-skills]] - m12-lifecycle: RAII, destructors, static initialization, rule of 5
