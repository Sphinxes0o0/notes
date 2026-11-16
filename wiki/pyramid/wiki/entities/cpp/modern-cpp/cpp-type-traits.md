---
type: entity
tags: [cpp, templates, type-traits, metaprogramming, modern-cpp, sfinae]
created:2026-06-08
sources: [pdf-book-cpp-templates-v2, bookmark-effective-modern-cpp]
---

# C++ Type Traits

## 定义

C++ Type Traits 是 `<type_traits>`头文件提供的编译期类型萃取工具集，允许在模板元编程中查询/修改类型属性（`is_integral`、`is_same`、`remove_reference`等）。Type Traits 是 STL模板实现的核心机制（如 `std::advance` 通过 `iterator_category` trait编译期分派），也是 SFINAE、concepts 的底层基石。

##关键要点

- **类型分类**：`is_integral`、`is_floating_point`、`is_array`、`is_pointer`、`is_class` 等
- **类型关系**：`is_same`、`is_base_of`、`is_convertible`
- **类型变换**：`remove_reference`、`add_const`、`decay`、`conditional`
- **编译期值**：`integral_constant<bool, value>`、`bool_constant`
- **C++17 `void_t`**：SFINAE探测表达式合法性
- **C++20 concepts**：上层抽象，底层仍用 traits

##核心概念

- **`std::enable_if`**：SFINAE工具，根据条件选择重载
- **`if constexpr`**：C++17编译期分支，简化 SFINAE
- **`std::declval`**：在不构造对象的情况下获取引用类型（用于 trait表达式）
- **`iterator_traits`**：STL 算法通过它获取 `iterator_category`、`value_type` 等
- **`std::void_t<...>`**：探测成员存在性
- **C++20 Concepts**：`template<typename T> concept Integral = std::is_integral_v<T>;`
- **检测 idiom**：`is_detected`、`detected_t` 等 C++17 检测库

## 相关页面

- [[entities/cpp/cpp-templates]] —模板基础
- [[entities/cpp/cpp-templates-v2]] —模板进阶
- [[entities/cpp/modern-cpp/cpp-concepts]] — Concepts
- [[entities/cpp/modern-cpp/cpp-constexpr]] — constexpr
- [[entities/cpp/modern-cpp/cpp-stl-optional-variant-any]] — 类型擦除
- [[sources/pdf-book-cpp-templates-v2]] — C++ Templates2nd
