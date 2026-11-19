---
type: entity
tags: [cpp, master, smart-pointers, resource-management, cycles]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# Master: C++ Smart Pointers Mental Model

## 核心問題

**這個資源需要多少個所有者？**

- **一個**: `std::unique_ptr`（90% 的情況）
- **多個**: `std::shared_ptr`
- **觀察者**: `std::weak_ptr`

## Error → Design Question

| 問題 | 設計問題 |
|------|----------|
| **內存泄漏（環）** | 是否有 `shared_ptr` 相互指向？環 = 泄漏 |
| **Dangling Pointer** | 是否存儲了 `weak_ptr` 或原始指針但檢查太晚？ |
| **Double Free** | 是否從一個原始指針創建了兩個 `unique_ptr`？ |
| **性能問題** | 是否不必要的拷貝 `shared_ptr`？（原子操作） |

## Thinking Prompt

1. **我能用 `unique_ptr` 嗎？**
   - 始終從這裡開始。它零開銷（大小 = 原始指針）
   - 它強制你思考所有權轉移（`std::move`）

2. **這是環嗎？**
   - Parent → Child (`shared_ptr`)
   - Child → Parent (`weak_ptr`)
   - 如果 Child 持有指向 Parent 的 `shared_ptr`，兩者永不死亡

3. **我需要自定義刪除器嗎？**
   - 管理 C-API（`FILE*`、`SDL_Surface*`）？
   - `unique_ptr<FILE, DeclType(&fclose)>` 完美處理

## Trace Up / Down

- **Trace Up**: "應用內存使用不斷增長但 Valgrind 沒有報告泄漏" → `shared_ptr` 環。可達內存在技術上"被擁有"，只是相互的 → 用 `weak_ptr` 打破環
- **Trace Down**: "我需要一個異構對象列表" → `std::vector<std::unique_ptr<Base>>`

## Quick Reference

| 模式 | 開銷 | 使用時機 |
|------|------|----------|
| **`make_unique`** | 零 | 創建新堆對象 |
| **`make_shared`** | 1 次分配 | 創建共享對象 |
| **`weak_ptr`** | Control Block | 打破環、緩存 |
| **`enable_shared_from_this`** | 零 | 需要在成員函數內使用 `shared_from_this()` |

## 相關概念

- [[entities/cpp/smart-pointers]] - 現有 Smart Pointers entity
- [[entities/cpp/modern/c17-02-resource]] - C++17 Smart Pointers 技能
- [[entities/cpp/modern/m01-ownership]] - Master: Ownership
- [[entities/cpp/modern/m15-anti-pattern]] - Master: Anti-Patterns（raw new/delete 是反模式）

## 來源詳情

- [[sources/cpp-modern-skills]] - m02-resource: unique_ptr, shared_ptr, weak_ptr, cycles, enable_shared_from_this
