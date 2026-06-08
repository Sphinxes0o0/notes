---
type: entity
tags: [cpp, cpp11, modern-cpp, enums, type-safety]
created:2026-06-08
sources: [bookmark-effective-modern-cpp]
---

# C++11 Strongly-Typed Enums (enum class)

## 定义

C++11引入 `enum class`（强类型枚举，又称 scoped enum），相比传统 `enum` 提供三个核心改进：(1)强类型，不会隐式转换为 int；(2)作用域限定，枚举值不会泄漏到外层作用域；(3) 可显式指定底层类型（`enum class Color : uint8_t`），便于序列化与二进制布局控制。

##关键要点

- **强类型**：禁止 `Color c = Red;`（需 `Color c = Color::Red;`），禁止 `int i = Color::Red;`（需 `static_cast<int>(Color::Red)`）
- **作用域隔离**：`Color::Red`不会污染外层命名空间
- **底层类型可指定**：`enum class Code : uint8_t { OK =0, ERR =1 };`
- **前向声明友好**：`enum class Foo : int;`（需指定底层类型）
- **结构化绑定**：可与 `[[nodiscard]]`、`std::optional` 等结合

##核心概念

- **与传统 enum 对比**：传统 enum 是 int 别名，泄漏作用域，可隐式比较
- **switch 中的强类型**：`switch (color) { case Color::Red: ... }`编译期检查覆盖
- **bitset/optional集成**：`std::optional<Color>`、`std::bitset<8>` 用于 flags
- **指定底层类型**：用于 ABI稳定、POD序列化
- **与 unscoped enum 共存**：`enum` (unscoped)仍可用，但推荐 `enum class`
- **underlying_type trait**：`std::underlying_type_t<Color>`

## 相关页面

- [[entities/cpp/modern-cpp/cpp-attributes]] — C++11 属性
- [[entities/cpp/modern-cpp/cpp-structured-bindings]] — 结构化绑定枚举
- [[entities/cpp/modern-cpp/cpp-stl-optional-variant-any]] — optional/variant
- [[sources/bookmark-effective-modern-cpp]] — Effective Modern C++
