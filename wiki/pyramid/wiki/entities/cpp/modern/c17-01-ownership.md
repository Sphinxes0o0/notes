---
type: entity
tags: [cpp, cpp17, ownership, move-semantics, raii]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Ownership & Move Semantics

## 定义

C++17 中的所有权是通過類型系統強制執行的紀律。編譯器通過移動語義和生命周期規則執行所有權約束。核心問題：**誰擁有這個資源，是否需要移動？**

## 關鍵要點

- **Scope-bound**: 棧值 → RAII，無分配
- **Exclusive ownership**: `std::unique_ptr<T>` → 零開銷，無別名
- **Shared ownership**: `std::shared_ptr<T>` → 原子引用計數
- **Non-owning view**: `T&`、`T*`、`std::span`、`std::string_view` → 無所有權
- **Transfer on return**: 返回值 → RVO/NRVO C++17 保證
- **Rule of Zero**: 偏好 default/delete 所有特殊成員函數
- **Rule of Five**: 手動管理資源時需定義全部五個特殊函數

## 代碼示例

```cpp
// C++17 保證復制省略
std::vector<int> make_vec() {
    std::vector<int> v{1, 2, 3};
    return v;  // C++17: guaranteed elision
}

// unique_ptr 工廠函數
std::unique_ptr<Widget> make_widget() {
    auto p = std::make_unique<Widget>();
    return p;  // 自動移動，無需 std::move
}

// std::move 僅用於轉移後再返回
void consume(std::unique_ptr<Widget> w) { ... }
auto w = std::make_unique<Widget>();
consume(std::move(w));  // REQUIRED: w 已轉移
```

## 常見陷阱

- **Moving local and returning**: `std::move(p); return p;` → p 為 nullptr
- **const lvalue blocks move**: `const std::string s; std::move(s)` → 拷貝而非移動
- **Return by value of local**: 無需 `std::move`，依賴 RVO

## 相關概念

- [[entities/cpp/move-semantics]] - 移動語義核心：rvalue references、std::move、std::forward
- [[entities/cpp/raii]] - RAII：構造/析構函數自動管理資源
- [[entities/cpp/smart-pointers]] - unique_ptr/shared_ptr/weak_ptr 實現所有權
- [[entities/cpp/modern/c17-02-resource]] - Smart Pointers 詳解
- [[entities/cpp/modern/c17-12-lifecycle]] - 生命周期與 RAII

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-01-ownership: Move Semantics, RAII, Reference Safety
