---
type: source
tags: [cpp, templates, metaprogramming, generics]
source-type: pdf
title: "C++ Templates 2nd Edition"
author: "David Vandevoorde, Nicolai M. Josuttis, Douglas Gregor"
date: 2017
size: large
path: raw/github/notes/resources/docs/cpp/C++模板_第二版.pdf
summary: "C++ 模板权威指南第二版（中文翻译），涵盖模板核心概念、特化/偏特化、变参模板、SFINAE、CRTP、模板与设计、C++11/14/17 模板新特性"
---

# C++ Templates 2nd Edition

## 概要

本书是 C++ 模板领域的权威参考书和教程。第一版出版约 15 年前，第二版针对 Modern C++（C++11/14/17）进行了全面更新。

## 核心内容

### 模板基础
- 函数模板与类模板
- 模板参数推导
- 重载解析规则
- 友元与模板

### 深入模板技术
- 特化与偏特化
- 两阶段查找 (Two-Phase Lookup)
- 变参模板 (Variadic Templates)
- 移入语义与完美转发中的模板应用
- SFINAE（替换失败非错误）

### 模板与设计
- CRTP (Curiously Recurring Template Pattern)
- 策略类 (Policy Classes) 与特性类 (Traits)
- 模板混入 (Template Mixins)
- 元编程 (Template Metaprogramming)

### Modern C++ 模板新特性
- 别名模板 (Alias Templates, C++11)
- 变量模板 (Variable Templates, C++14)
- if constexpr (C++17)
- 折叠表达式 (Fold Expressions, C++17)
- Concepts (C++20)

## 相关页面

- [[entities/cpp/cpp-templates]] — C++ 模板概念页
- [[entities/cpp/variadic-templates]] — 变参模板
- [[entities/cpp/constexpr]] — constexpr 编译时计算
- [[entities/cpp/cpp20-features]] — Concepts/Ranges/Coroutines
- [[cpp-index]] — C++ 模块导航
