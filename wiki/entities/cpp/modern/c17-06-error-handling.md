---
type: entity
tags: [cpp, cpp17, error-handling, exceptions, noexcept]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Error Handling

## 定义

C++17 錯誤處理跨越多個機制，選擇基於錯誤是否可恢復。核心問題：**錯誤如何跨層傳播？**

| 場景 | 工具 | 為什麼 |
|------|------|--------|
| "無值"——常見可恢復 | `std::optional<T>` | 無異常的顯式空值 |
| "無值或錯誤消息" | `std::variant<T, std::error_code>` | 結構化錯誤 |
| 操作失敗——可恢復 | `std::error_code` | 標準化錯誤碼 |
| 編程錯誤/不變量違反 | `assert` / `static_assert` | 僅調試，發布版剝離 |
| 不可恢復（損壞） | `throw` 異常 | 無法繼續 |
| 析構函數失敗 | `std::terminate` 或 noexcept | 析構函數不能拋出 |

## 關鍵要點

- **std::error_code**: 標準化錯誤碼，支持自定義 error_category
- **noexcept**: 函數承諾不拋出，否則調用 `std::terminate`
- **Dynamic noexcept**: `void demo() noexcept(condition)`
- **Exception Safety Guarantees**: No-throw / Basic / Strong / No guarantee
- **std::exception_ptr**: 異常傳輸

## 代碼示例

```cpp
// std::error_code + 自定義 error_category
struct MyErrorCategory : std::error_category {
    const char* name() const noexcept override { return "myerror"; }
    std::string message(int ev) const override {
        switch (ev) {
            case 1: return "invalid input";
            case 2: return "timeout";
            default: return "unknown";
        }
    }
};

// noexcept — 函數承諾不拋出
void safe_function() noexcept {
    // 若拋出則 std::terminate
}

// Dynamic noexcept
template<typename T>
void move_if_noexcept(T& dst, T& src) noexcept(std::is_nothrow_move_constructible_v<T>) {
    dst = std::move(src);
}

// Strong exception safety: copy-and-swap
void assign(const Widget& other) {
    Widget tmp(other);      // 可能拋出
    tmp.data_.swap(data_);  // 無拋出 swap
}  // 若拷貝失敗，原對象不變

// std::exception_ptr 異常傳輸
std::exception_ptr transport_exception() {
    try {
        throw std::runtime_error("error in nested scope");
    } catch (...) {
        return std::current_exception();
    }
}
```

## 常見陷阱

- **析構函數拋出**: 棧展開時若有多個異常 → `std::terminate`
- **按值捕獲**: `catch(std::exception e)` → 對象切片，應用 `catch(const std::exception& e)`
- **吞掉異常**: `catch(...) {}` 靜默忽略錯誤

## 相關概念

- [[entities/cpp/modern/c17-05-type-driven]] - std::optional 是類型驅動錯誤處理
- [[entities/cpp/modern/c17-13-domain-error]] - 異常層次結構與系統錯誤
- [[entities/cpp/modern/m06-error-handling]] - Master: Error Handling
- [[entities/cpp/modern/m13-domain-error]] - Master: Domain Errors
- [[entities/cpp/modern/c17-06-error-handling]] - 自身交叉引用

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-06-error-handling: std::optional, std::error_code, noexcept, exception safety
