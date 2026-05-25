---
type: entity
tags: [cpp, templates, metaprogramming, sfinae, variadic, concepts, crtp]
created: 2026-05-25
sources: [pdf-onedrive-batch1]
---

# C++ Templates 第二版

## 定义
David Vandevoorde, Nicolai M. Josuttis, Douglas Gregor 著《C++ Templates》第 2 版（Pearson, 2018，823 页），C++ 模板的完整指南，涵盖函数/类模板、非类型参数、可变模板、SFINAE、模板元编程、Concepts、C++11/14/17 标准演进。

## 关键要点

### 模板基础
- 函数模板：两阶段翻译（解析 vs 实例化）
- 模板参数推导：按值传递 vs 按引用传递、自动类型推导
- 默认模板参数、重载函数模板
- 模板参数推导上下文（deduction guide）

### 类模板
- 类模板声明与成员函数实现
- 部分特例化（partial specialization）
- 类模板参数推导（CTAD）
- 模板化聚合类型（Templatized aggregates）

### 非类型模板参数
- 整数、指针、模板模板参数作为非类型参数
- `auto` 作为非类型参数类型（C++17）

### 可变模板（Variadic Templates）
- 参数包展开（parameter pack expansion）
- `sizeof...` 运算符
- Fold expressions（C++17）：二元 fold、一元 fold
- 可变类模板与可变表达式

### 模板 trick 细节
- `typename` 关键字的使用场景
- 零初始化（value initialization）
- 成员模板、`.template` 构造
- 原始数组和字符串字面量模板
- 变量模板（variable templates）
- 模板模板参数（template template parameters）

### Move 语义与 `enable_if`
- 完美转发（perfect forwarding）、`std::forward`
- 特殊成员函数模板
- `std::enable_if` 禁用模板
- Concepts 简化 `enable_if` 表达式

### 编译期编程
- 模板元编程：编译时计算
- `constexpr` 函数：编译时求值 vs 运行时求值
- SFINAE 机制：替换失败非错误（Substitution Failure Is Not An Error）
- `static_assert` 编译时断言
- 编译时 `if constexpr`

### 按值还是按引用传递？
- 按值传递：拷贝语义、移动语义
- 按引用传递：`const T&`、`T&`、转发引用 `T&&`
- `std::ref()` 和 `std::cref()`
- 字符串字面量与原始数组特殊处理

### 实践中的模板
- 包含模型（Inclusion model）与链接错误
- 模板出现在头文件的必要性
- 预编译头（PCH）
- 错误信息解读

### 泛型库
- Callable：函数对象、lambda、`std::function`
- `std::pair` / `std::tuple` 的使用
- Variadic 表达式展开

## 相关概念

- [[entities/cpp/cpp-templates]] — C++ 模板（泛指）
- [[entities/cpp/variadic-templates]] — 可变模板
- [[entities/cpp/constexpr]] — constexpr 编译时求值
- [[entities/cpp/if-constexpr]] — if constexpr 分支
- [[entities/cpp/concepts]] — C++20 Concepts（待创建）

## 来源详情

- [[pdf-onedrive-batch1]]
