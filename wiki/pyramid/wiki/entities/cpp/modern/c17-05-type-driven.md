---
type: entity
tags: [cpp, cpp17, type-driven-design, strong-types, domain-modeling]
created: 2026-05-25
sources: [cpp-modern-skills]
---

# C++17 Type-Driven Design

## 定义

類型驅動設計使用類型系統使非法狀態不可表示。核心問題：**錯誤狀態能夠被表示嗎？**

| 工具 | 用途 | 示例 |
|------|------|------|
| `std::optional<T>` | 可空值 | `optional<int>` vs `int*` |
| `std::variant<A, B>` | Sum type | `variant<int, Error>` |
| `std::string_view` | 非擁有字符串 | 零拷貝子串 |
| `std::span<T>` | 非擁有範圍 | 零拷貝緩衝區視圖 |
| Newtype wrapper | 強類型 | `struct Meter { double v; };` |
| `std::integral_constant` | Tag type | 編譯時分派 |

## 關鍵要點

- **Newtypes**: 防止單位混合（如 Meter vs Feet）
- **Strong ID**: `template<typename Tag> struct StrongId { int value; }`
- **Type-State Pattern**: 狀態編碼為類型
- **std::variant**: Sum type + `std::visit` 模式匹配
- **string_view/span**: 零拷貝視圖，生命周期依附原字符串

## 代碼示例

```cpp
// Newtype: 防止單位混淆
struct Meter { double value; };
struct Feet { double value; };
Meter operator+(Meter a, Meter b) { return Meter{a.value + b.value}; }
// Meter + Feet 編譯錯誤

// Strong ID: 類型安全標識符
template<typename Tag>
struct StrongId { int value; explicit StrongId(int v) : value(v) {} };
using UserId = StrongId<struct UserTag>;
using OrderId = StrongId<struct OrderTag>;
// UserId(1) == OrderId(1) 編譯錯誤

// std::variant Sum Type
using Result = std::variant<int, std::string>;
Result divide(int a, int b) {
    if (b == 0) return std::string{"division by zero"};
    return a / b;
}
void handle(Result r) {
    if (auto* val = std::get_if<int>(&r)) {
        std::cout << "success: " << *val << "\n";
    } else {
        std::cout << "error: " << std::get<std::string>(r) << "\n";
    }
}

// Type-State Pattern
struct Connecting {};
struct Connected {};
template<typename State>
class Connection {
    State state_;
public:
    template<typename S = State>
    auto connect() -> std::enable_if_t<std::is_same_v<S, Connecting>, Connection<Connected>>;
};

// string_view: 零拷貝字符串視圖
size_t count_lines(std::string_view sv) {
    return std::count(sv.begin(), sv.end(), '\n');
}
```

## 常見陷阱

- **Optional 過度使用**: `std::optional<int> get_count()` → count_ 始終有效
- **Variant 過多 alternatives**: 超過 10 種 type 的 variant 難以維護
- **string_view 臨時對象**: `return std::string_view` 持有局部 string 的視圖

## 相關概念

- [[entities/cpp/modern/c17-04-templates]] - 模板是類型驅動設計的底層支撐
- [[entities/cpp/modern/c17-09-domain]] - DDD: Value Objects, Entities, Aggregates
- [[entities/cpp/modern/m05-type-driven]] - Master: Type-Driven Design
- [[entities/cpp/modern/m09-domain]] - Master: Domain Modeling
- [[entities/cpp/modern/c17-05-type-driven]] - 自身交叉引用（Type-State Pattern）

## 來源詳情

- [[sources/cpp-modern-skills]] - c17-05-type-driven: std::optional, std::variant, newtypes, type-state
