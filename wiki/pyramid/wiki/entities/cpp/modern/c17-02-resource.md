---
type: entity
tags: [cpp, cpp17, smart-pointers, resource-management]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Smart Pointers (Resource Management)

## 定义

C++17 智能指針通過 RAII 慣用法自動管理動態內存。核心問題：**誰擁有這個資源，何時銷毀？**

| 場景 | 指針類型 | 原因 |
|------|----------|------|
| 單一獨占所有者 | `std::unique_ptr<T>` | 零開銷，無引用計數 |
| 多個所有者 | `std::shared_ptr<T>` | 原子引用計數 |
| 觀察而非擁有 | `std::weak_ptr<T>` | 打破循環，依賴有效性檢查 |
| 已有其他所有者 | `T*`、`T&`、`std::span` | 非擁有視圖 |

## 關鍵要點

- **工廠函數**: 始終使用 `std::make_unique` / `std::make_shared`
- **unique_ptr**: 独占所有權，不可復制，可移動
- **shared_ptr**: 引用計數，共享所有權，需注意循環引用
- **weak_ptr**: 配合 shared_ptr 使用，不增加引用計數
- **自定義刪除器**: `unique_ptr<FILE, decltype(&fclose)>` 處理 C-API

## 代碼示例

```cpp
// shared_ptr 共享所有權
auto sp1 = std::make_shared<Widget>();
std::shared_ptr<Widget> sp2 = sp1;  // refcount = 2

// unique_ptr 轉移所有權
auto w = std::make_unique<Widget>();
take_ownership(std::move(w));  // w 現為 nullptr

// weak_ptr 打破循環
class Node {
public:
    std::shared_ptr<Node> next_;
    std::weak_ptr<Node> prev_;  // 非擁有 back-reference
};

// make_shared vs new — 偏好 make_shared
auto sp = std::make_shared<Widget>(args);  // 單次分配
std::shared_ptr<Widget> sp2(new Widget(args));  // 兩次分配
```

## 常見陷阱

- **循環 shared_ptr**: A→B 且 B→A 導致內存泄漏 → 使用 `weak_ptr`
- **Raw pointer 轉 shared_ptr**: `safe(std::shared_ptr<Widget>(raw))` 導致 double-free
- **unique_ptr → shared_ptr**: C++17 支持隱式轉換，但需 `std::move`

## 相關概念

- [[entities/cpp/smart-pointers]] - 現有智能指針 entity（shared_ptr/unique_ptr/weak_ptr）
- [[entities/cpp/raii]] - RAII 是智能指針的理論基礎
- [[entities/cpp/move-semantics]] - unique_ptr 利用移動語義轉移所有權
- [[entities/cpp/modern/c17-01-ownership]] - 所有權與移動語義
- [[entities/cpp/modern/c17-12-lifecycle]] - 生命周期與 Rule of 5/0

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-02-resource: unique_ptr, shared_ptr, weak_ptr, make_unique, make_shared
