---
type: entity
tags: [cpp, history, language-design, standards]
created: 2026-05-25
sources: [pdf-cpp-slides]
---

# Bjarne Stroustrup — C++ at 40: Success & Future Evolution

## 定义
Bjarne Stroustrup 2025年中国峰会的演讲，回顾C++ 40年成功经验，阐述设计原则与C++26未来演进方向（Profiles、模块、概念）。

## 关键要点

### 设计原则：直接在代码中表达思想
- **核心理念**：代码即思想的直接表达 — 数学（张量/多项式）、工程（矩阵/傅里叶）、图形学、金融、电信等
- **优秀设计原则**：灵活静态类型系统、可扩展性、零开销、最少显式类型转换、资源管理（防止泄漏）、错误处理保证、灵活并发支持
- "唯一的限制是你的想象力" — 代价合理，大多数优秀软件是无形的

### 历史演进与规模
- **1980年代**：C with Classes (带构造/析构函数的类)，Simula风格抽象 + C硬件操作
- **C++98**：异常、模板、STL、命名空间
- **C++11**：并发、lambda、auto、shared_ptr、tuple、regex、constexpr
- **C++14**：variadic templates、generic lambda
- **C++17**：模板参数推导
- **C++20**：概念、协程、模块、ranges、日历、span、format
- **2025年**：全球约1630万C++开发者，4年内增长72%（每年近20%），新增约700万开发者

### 稳定性与演进的平衡
- **稳定性**：过去运行良好的代码现在依然运行良好
- **演进**：通常今天可以做得更好
- **C++ Profiles**：管理数十年积累复杂性的计划，为不同场景提供安全的子语言

### 当代C++关键特性
- 带构造函数和析构函数的类（资源管理基础）
- 模板与概念（泛型接口规范）
- 模块（编译速度与封装）
- Lambda表达式（函数对象生成）
- constexpr/consteval（编译期计算）
- 并发支持与并行算法

### 演讲者
- **Bjarne Stroustrup**，哥伦比亚大学，C++之父，著《The C++ Programming Language》

## 相关概念
- [[entities/cpp/cpp20-features]] — C++20 concepts/modules/coroutines
- [[entities/cpp/constexpr]] — 编译期计算
- [[entities/cpp/smart-pointers]] — 资源管理
- [[entities/cpp/raii]] — 构造/析构与资源管理

## 来源详情
- [[sources/pdf-cpp-slides]] — Bjarne C++ at 40, CPP-Summit China 2025
