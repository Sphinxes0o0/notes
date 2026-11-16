---
type: entity
tags: [cpp, cpp17, templates, sfinae, if-constexpr, polymorphism]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Templates & Polymorphism

## 定义

C++17 模板提供編譯時多態性，零開銷。核心問題：**你需要編譯時多態（模板）還是運行時多態（virtual）？**

| 場景 | 工具 | 為什麼 |
|------|------|--------|
| 同算法不同類型 | Template | 代碼生成 |
| 約束模板參數 | SFINAE / `enable_if` | 防止錯誤實例化 |
| 編譯時類型分支 | `if constexpr` | 編譯時 if |
| 運行時多態 | Virtual function | 動態分派 |
| 防止覆蓋 | `final` specifier | C++11 |
| 確保覆蓋 | `override` specifier | C++11 |

> **注意**: C++20 `concepts` 在 C++17 中不可用。C++17 使用 SFINAE + `enable_if` + type traits 進行約束。

## 關鍵要點

- **Variable templates**: `template<typename T> constexpr bool is_integral_v = ...`
- **CTAD**: `std::vector v{1, 2, 3}` → 推導為 `std::vector<int>`
- **SFINAE**: `std::enable_if_t<condition, ReturnType>`
- **void_t SFINAE**: 結構化 SFINAE 檢測成員存在性
- **if constexpr**: C++17 編譯時分支
- **override/final**: 虛函數安全

## 代碼示例

```cpp
// SFINAE: 只對整數類型啟用
template<typename T>
auto square(T val) -> std::enable_if_t<std::is_integral_v<T>, T> {
    return val * val;
}

// void_t SFINAE: 檢測成員存在性
template<typename T, typename = void>
struct has_size : std::false_type {};

template<typename T>
struct has_size<T, std::void_t<decltype(std::declval<T>().size())>>
    : std::true_type {};

// if constexpr — C++17
template<typename T>
void describe(const T& val) {
    if constexpr (std::is_integral_v<T>) {
        std::cout << "integral: " << val << "\n";
    } else if constexpr (std::is_floating_point_v<T>) {
        std::cout << "floating: " << val << "\n";
    } else {
        std::cout << "other\n";
    }
}

// override / final
struct Base {
    virtual void draw() const {}
    virtual ~Base() = default;
};
struct Derived : Base {
    void draw() const override {}  // 簽名不匹配則編譯錯誤
};
struct FinalWidget {
    virtual void render() final {}  // 禁止 further override
};
```

## 模板 vs Virtual

| 方面 | Template | Virtual |
|------|----------|---------|
| 解析時機 | 編譯時 | 運行時 |
| 開銷 | 零（內聯） | Vtable 查找 |
| 靈活性 | 編譯時已知類型 | 運行時已知類型 |
| 代碼大小 | 可能膨脹 | 單一 vtable |
| 成員訪問 | 直接 | 通過 vptr |

## 常見陷阱

- **SFINAE vs static_assert**: SFINAE 在聲明級別約束，static_assert 在實例化級別
- **Virtual destructor**: 多態類必須有虛析構函數
- **ODR-violating templates**: 模板定義在 hpp 而非 cpp

## 相關概念

- [[entities/cpp/variadic-templates]] - 模板變參與參數包展開
- [[entities/cpp/if-constexpr]] - if constexpr 編譯時分支
- [[entities/cpp/cpp20-features]] - C++20 Concepts（更高級的約束機制）
- [[entities/cpp/modern/m04-zero-cost]] - Master: Zero-Cost Abstractions（模板 vs virtual）
- [[entities/cpp/modern/c17-05-type-driven]] - 類型驅動設計

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-04-templates: SFINAE, enable_if, if constexpr, override, final
