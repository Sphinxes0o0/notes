---
type: entity
tags: [c++, templates, metaprogramming, generics]
created: 2026-05-23
sources: [pdf-cpp-templates, pdf-cpp-templates-books]
---

# C++ Templates

## 定义

C++ 模板是一种编译时泛型编程机制，允许以类型参数化的方式编写函数和类，在编译时生成具体化的类型版本。C++ 模板支持特化、偏特化、变参模板、SFINAE、CRTP 等高级技术。

## 核心概念

### 函数模板与类模板

- **函数模板** — 以类型参数编写通用函数（如 `template<typename T> T max(T a, T b)`）
- **类模板** — 以类型参数编写通用容器/算法（如 `std::vector<T>`）

### 模板特化与偏特化

- **全特化 (Full Specialization)** — 为特定类型提供完全不同的实现
- **偏特化 (Partial Specialization)** — 为模板参数的部分属性提供特殊实现（仅类模板支持）

### 变参模板 (Variadic Templates, C++11)

- 任意数量和类型的模板参数：`template<typename... Args>`
- 参数包展开 (pack expansion)：`(args, ...)`
- 折叠表达式 (fold expressions, C++17)：`(args + ...)`

### SFINAE (Substitution Failure Is Not An Error)

- 模板参数替换失败时不会编译错误，而是从重载集合中移除该模板
- 用于编译时条件选择、类型特性检测
- C++20 Concepts 提供了更优雅的替代方案

### CRTP (Curiously Recurring Template Pattern)

- 派生类作为模板参数传入基类：`template<typename D> class Base`
- 实现静态多态、混入 (mixin) 模式

## 相关概念

- [[entities/cpp/variadic-templates]] — 变参模板与参数包展开
- [[entities/cpp/constexpr]] — constexpr 编译时计算
- [[entities/cpp/if-constexpr]] — 编译时条件分支
- [[entities/cpp/cpp-stl-algorithms]] — STL 算法与模板编程
- [[entities/cpp/cpp20-features]] — Concepts/Ranges 新特性

## 来源详情

- [[sources/pdf-cpp-templates]] — C++ Templates 2nd Edition (Vandevoorde, Josuttis, Gregor)
- [[sources/pdf-cpp-templates-books]] — C++ Templates 合集（含 Template Metaprogramming）
