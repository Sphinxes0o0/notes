---
type: entity
tags: [cpp, cpp17, const-correctness, mutability]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Const Correctness & Mutability

## 定义

C++17 中 `const` 是類型系統強制執行的契約。核心問題：**什麼可以改變，誰可以改變它？**

| 你想要 | 工具 | 說明 |
|--------|------|------|
| 參數不被修改 | `const T&` 或 `T&` | 偏好 `const T&` |
| 方法不修改對象 | `const` 方法 | Const 成員函數 |
| 邏輯上 const 但需緩存 | `mutable` + const 方法 | Logical const |
| 編譯時求值 | `constexpr` | C++17 可用 `if constexpr` |
| 運行時 const 決策 | `if constexpr` | C++17 |

## 關鍵要點

- **Bitwise const**: C++ 默認，`const` 關鍵字
- **Logical const**: 通過 `mutable` 實現緩存
- **Const overload**: `const T& get()` 和 `T& get()` 重載
- **Reference qualifiers**: `T& get() &` / `T get() &&` 區分 lvalue/rvalue
- **constexpr lambda**: C++17 支持

## 代碼示例

```cpp
class Widget {
    mutable int cache_access_count_ = 0;
    mutable std::string cached_value_;
    bool cache_valid_ = false;

public:
    // Const 成員函數：承諾不修改對象狀態
    const std::string& name() const {
        ++cache_access_count_;  // OK: mutable
        return name_;
    }
};

// Reference qualifiers — C++17
class Data {
    std::vector<int> data_;
public:
    std::vector<int>& get_data() & { return data_; }           // lvalue 調用
    std::vector<int> get_data() && { return std::move(data_); } // rvalue 調用
};

// constexpr if — C++17
template<typename T>
auto process(const T& val) {
    if constexpr (std::is_integral_v<T>) {
        return val * 2;
    } else if constexpr (std::is_floating_point_v<T>) {
        return val * 2.0;
    }
}
```

## 常見陷阱

- **const_cast 然後修改**: `const Widget* p; const_cast<Widget*>(p)->mutate()` → UB
- **Mutable + 多線程**: `mutable` 在多線程中需配合 `std::atomic` 或鎖
- **Non-const 隱藏 const 版本**: 兩個 get() 重載需明確意圖

## 相關概念

- [[entities/cpp/constexpr]] - constexpr 編譯時計算
- [[entities/cpp/modern/c17-04-templates]] - if constexpr 編譯時分支
- [[entities/cpp/modern/c17-05-type-driven]] - 類型驅動設計中的不可變性
- [[entities/cpp/modern/c17-03-mutability]] - Const correctness 與 mutable
- [[entities/cpp/modern/m03-mutability]] - Master: Mutability 思維模型

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-03-mutability: const, mutable, logical const, constexpr if
