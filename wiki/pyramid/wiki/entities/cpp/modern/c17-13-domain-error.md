---
type: entity
tags: [cpp, cpp17, domain-errors, exceptions, error-categories]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Domain Errors & Exception Hierarchies

## 定义

C++17 領域錯誤使用異常層次結構和系統錯誤碼表達。核心問題：**錯誤從哪裡來，誰應該處理它？**

```
std::exception
├── std::logic_error
│   ├── std::invalid_argument
│   ├── std::domain_error
│   ├── std::length_error
│   └── std::out_of_range
├── std::runtime_error
│   ├── std::range_error
│   ├── std::overflow_error
│   └── std::underflow_error
├── std::bad_alloc
└── std::bad_cast
```

## 關鍵要點

- **Exception Hierarchy**: `std::runtime_error` 用於運行時可檢測的錯誤
- **std::exception_ptr**: 異常傳輸（跨線程、跨上下文）
- **Nested Exceptions**: `std::throw_with_nested` 鏈接異常
- **std::error_code**: OS 錯誤碼，包裝 `errno`
- **std::variant<T, E>**: C++17 等價於 C++23 `std::expected`

## 代碼示例

```cpp
// 自定義異常層次結構
struct DomainError : std::exception {
    const char* what() const noexcept override { return "domain error"; }
};

struct InvalidInput : DomainError {
    std::string field_;
    explicit InvalidInput(std::string f) : field_(std::move(f)) {}
    const char* what() const noexcept override { return "invalid input"; }
};

// std::exception_ptr 傳輸異常
std::exception_ptr capture() {
    try {
        throw std::runtime_error("error");
    } catch (...) {
        return std::current_exception();
    }
}

// Nested exceptions
void inner() {
    try {
        throw std::runtime_error("inner error");
    } catch (...) {
        std::throw_with_nested(std::runtime_error("outer error"));
    }
}

// std::error_code
std::error_code open_file(const char* path) {
    FILE* f = fopen(path, "r");
    if (!f) {
        return std::error_code(errno, std::generic_category());
    }
    fclose(f);
    return std::error_code{};
}

// C++17: variant 作為 expected
using ParseResult = std::variant<int, std::string>;
ParseResult parse(const std::string& s) {
    try {
        return std::stoi(s);
    } catch (...) {
        return std::string{"parse error"};
    }
}
```

## 常見陷阱

- **按值捕獲**: `catch(std::exception e)` → 切片，應用 `catch(const std::exception& e)`
- **吞掉異常**: `catch(...) {}` 靜默忽略
- **析構函數拋出**: `~Widget() noexcept(false)` 危險

## 相關概念

- [[entities/cpp/modern/c17-06-error-handling]] - 通用錯誤處理機制
- [[entities/cpp/modern/c17-09-domain]] - DDD 中的領域事件
- [[entities/cpp/modern/m06-error-handling]] - Master: Error Handling
- [[entities/cpp/modern/m13-domain-error]] - Master: Domain Errors
- [[entities/cpp/modern/c17-13-domain-error]] - 自身交叉引用

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-13-domain-error: Exception hierarchies, std::exception_ptr, nested_exception, std::error_code
