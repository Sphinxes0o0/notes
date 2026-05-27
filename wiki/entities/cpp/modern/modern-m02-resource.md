---
type: entity
tags: [cpp, master, resource, smart-pointers]
created: 2026-05-27
sources: [github-modern-cpp-skills-m02]
---

# modern-m02-resource

## 定義

C++ 智能指針資源管理的核心思維模型：**這個資源有多少個所有者？**

## 核心問題

**這個資源有多少個所有者？**

- **One**: `std::unique_ptr` (90% of cases) — 零開銷，大小等於原始指針
- **Many**: `std::shared_ptr` — 原子引用計數，每次拷貝有開銷
- **Observer**: `std::weak_ptr` — 不影響引用計數，用於打破循環或緩存

## 關鍵要點

- 90% 的場景應該用 `unique_ptr`
- `unique_ptr` 強制思考所有權轉移，催生正確的 API 設計
- `shared_ptr` 循環是隱式內存洩漏：內存"技术上owned"，只是互相無法釋放
- `weak_ptr` 三個用途：打破循環、實現緩存、安全的觀察者模式
- `make_unique` / `make_shared` 是創建智能指針的首選方式
- 自定義刪除器可用於管理 C-API 資源 (`FILE*`, `SDL_Surface*`)

## 常見錯誤映射

| 錯誤 | 設計問題 |
|------|----------|
| Memory Leak (Cycles) | `shared_ptr` 是否形成了循環引用？ |
| Dangling Pointer | `weak_ptr` 是否在使用前檢查了 `lock()`？ |
| Double Free | 是否有兩個 `unique_ptr` 來自同一原始指針？ |
| 性能問題 | 是否不必要的拷貝了 `shared_ptr`？（原子操作開銷） |

## 思維框架

1. **Can I use `unique_ptr`?** Always start here. Zero overhead.
2. **Is this a cycle?** Parent → Child (`shared_ptr`) + Child → Parent (`weak_ptr`).
3. **Do I need a custom deleter?** Managing C-API? Use `unique_ptr<FILE, decltype(&fclose)>`.

## 相關概念

- [[entities/cpp/modern/modern-m01-ownership]] — 所有權是智能指針的理論基礎
- [[entities/cpp/modern/modern-m15-anti-pattern]] — `new` 是智能指針要消滅的 anti-pattern
- [[entities/cpp/modern/modern-m09-domain]] — DDD 中 aggregate root 使用 `shared_ptr` 管理子對象
- [[entities/cpp/smart-pointers]] — 智能指針的詳細技術實現
- [[entities/cpp/raii]] — RAII 是智能指針的原理

## Source

- [[sources/github-modern-cpp-skills-m02]]