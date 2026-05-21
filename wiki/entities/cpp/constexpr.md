---
type: entity
tags: [cpp, modern-cpp]
created: 2026-05-20
sources: [pdf-cpp-modern-tutorial]
---

# Constexpr (编译时计算)

## 定义

`constexpr`是C++11引入的关键字，用于指定常量表达式。constexpr函数可以在编译期求值（当参数为常量表达式时），从而实现真正的编译时计算，提升运行时性能。

## 关键要点

- **C++11 constexpr**：限制较多，函数体只能一条return语句
- **C++14放宽限制**：constexpr函数可以包含更多语句（循环、分支等）
- **constexpr变量**：必须在编译期确定值
- **constexpr vs const**：const仅表示只读，编译期不一定求值
- **constexpr与模板结合**：实现编译期计算器

## 代码示例

```cpp
// C++11 constexpr
constexpr int len_foo_constexpr() {
    return 5;
}
char arr_6[len_foo_constexpr() + 1]; // OK，编译期确定大小

// C++14 constexpr（支持循环）
constexpr int fibonacci(const int n) {
    if(n == 1) return 1;
    if(n == 2) return 1;
    return fibonacci(n-1) + fibonacci(n-2);
}

// constexpr变量
constexpr int len_2_constexpr = 1 + 2 + 3;
char arr_4[len_2_constexpr]; // OK

// constexpr Lambda（C++17）
auto add = [](auto x, auto y) constexpr { return x + y; };
```

## 相关概念
- [[entities/cpp/auto-type-deduction]] - auto与constexpr的结合
- [[entities/cpp/if-constexpr]] - if constexpr编译时分支
- [[entities/cpp/variadic-templates]] - 模板变参与constexpr

## 来源详情
- [[sources/pdf-modern-cpp-tutorial]] - Chapter 2.1: constexpr
