---
type: source
source-type: pdf-book
title: "Professional C++ 第6版"
author: "Marc Gregoire（陈晓伟 译）"
date: 2024-11-22
size: large
path: raw/PDFs/books/Professional-C++-6ed-zh-20241122.pdf
summary: "Professional C++ 第6版（1247页）：系统讲解 C++ 现代特性，从语言基础到工程实践，覆盖 C++20 modules/concepts/coroutines/_ranges，附编译环境配置与完整源代码。"
tags: [cpp, cpp20, cpp17, modern-cpp, professional, oop, stl]
created: 2026-05-27
---

# Professional C++ 第6版

> 原书：Professional C++ 6th Edition, Marc Gregoire（Wiley）
> 译者：陈晓伟，1247页

## 核心内容

### Part I — C++ 基础与标准库（第1-6章）
- **C++ 基础速成**（第1章）：Hello World → import std（C++20）、命名空间、字面量、变量、操作符、枚举、结构体、条件语句、三向比较（`<=>`）、函数
- **类和对象**（第5章）：OOP 思想、类定义、对象、成员访问控制
- **深入理解 C++ 类型**（第6章）：引用 vs 指针、const、constexpr

### Part II — C++ 标准库（第7-13章）
- **字符串与正则**（第7章）
- **I/O**（第13章）：流的概念、文件系统库（C++17 `std::filesystem`）

### Part III — 面向对象编程原则（第14-17章）
- **继承**（第14章）：公有/保护/私有继承，虚函数，多态
- **模板**（第16章）：类模板、函数模板、特化
- **容器与迭代器**（第18章）：STL 容器分类、迭代器失效

### Part IV — C++20 新特性（高级章节）
- **Modules**（C++20）：`import std;` 取代头文件
- **Concepts & Ranges**
- **Coroutines**：协程基础
- **六边形架构**（Hexagonal Architecture）

### Part V — 工程实践
- **设计模式**（GoF）：工厂、策略、装饰器等
- **异常处理**：RAII、自动资源管理
- **并发**：`std::jthread`、`latch`、`barrier`、`atomic`
- **测试**：单元测试与集成测试

## 关键主题

| 主题 | 覆盖内容 |
|------|----------|
| C++20 Modules | `import std;` 标准模块，消除头文件依赖 |
| 智能指针 | `unique_ptr`/`shared_ptr`/`weak_ptr` |
| 并发 | `jthread`、`latch`、`atomic` |
| Ranges | 组合式算法链 |
| Coroutines | `co_await`/`co_yield` |
| 最佳实践 | RAII、Rule of Zero/Three/Five |

## 编译环境
- **Microsoft Visual C++ 2022**
- **GCC**（Clang/LLVM 兼容）
- 配套源码：https://github.com/Professional-CPP/edition-6

## 相关页面

### C++ Books
- [[sources/pdf-book-21st-century-cpp]] — Bjarne 现代 C++ 理念
- [[sources/pdf-book-cpp17]] — C++17 标准详解
- [[sources/pdf-book-cpp-templates-v2]] — 模板第二版（Vandevoorde）
- [[sources/pdf-book-concurrency-modern-cpp]] — 并发编程（Grimm）
- [[sources/pdf-book-effective-stl]] — Effective STL
- [[sources/pdf-cpp-modern-books]] — Modern C++ 书籍合集
- [[sources/pdf-cpp-templates-books]] — C++ 模板书籍合集

### Module Indexes
- [[cpp-index]] — C++ 模块索引