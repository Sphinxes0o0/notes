---
type: source
source-type: pdf
title: "Effective STL"
author: "Scott Meyers"
date: 2001-06-06
size: medium
path: raw/PDFs/books/Effective STL简体中文版.pdf
summary: "Scott Meyers STL 最佳实践：50条提升C++标准库使用效率的专家指南，涵盖容器、迭代器、算法、函数对象、字符串和分配器。"
tags: [cpp, stl, books]
created: 2026-05-21
---

# Effective STL

## 核心内容

Scott Meyers 所著《Effective STL》是 C++ 标准库使用的权威指南，提供了 50 条专家级建议，系统覆盖 STL 六大核心领域。

### 主要内容分布

**容器 (Items 1-10)**
- vector/string 优先于 deque/list
- 使用 reserve 避免重复分配
- 容器选择策略（连续存储 vs 节点存储）
- 关联容器的 lower_bound/upper_bound/equal_range
- set/multiset 中 erase 的安全性

**迭代器 (Items 11-15)**
- 迭代器类别与失效规则
- istreambuf_iterator 与 streambuf_iterator
- 容器适配器的迭代器支持

**算法 (Items 16-32)**
- 算法复杂度与选择
- remove/erase 惯用法
- sort 与稳定排序的选择
- 仿函数与函数适配器
- 查找算法的正确使用

**函数对象 (Items 33-40)**
- 仿函数与函数适配器
- equal_range 与排序容器
- 算法参数传递方式
- 自定义仿函数的设计

**字符串 (Items 41-43)**
- string 实现差异
- 避免非必要的 COW (Copy-On-Write)
- 临时对象的构造优化

**分配器 (Items 44-50)**
- 自定义分配器设计
- allocator_traits
- 状态化分配器
- 分配器与 shared_ptr

## 关键引用

> "If you don't think about which operations are invalidating your iterators, you're probably not using STL correctly."

## 相关页面
- [[entities/cpp/cpp-stl-containers]]
- [[entities/cpp/cpp-stl-algorithms]]
- [[entities/cpp/cpp-stl-iterators]]
- [[entities/cpp/cpp-stl-functors]]
- [[entities/cpp/cpp-stl-string]]
- [[entities/cpp/cpp-stl-allocators]]
