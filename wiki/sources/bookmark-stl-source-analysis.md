---
type: source
source-type: bookmark
title: "STL 源码分析 (SGI STL 3.0)"
author: "FunctionDou"
date: 2024
size: medium
path: raw/github/FunctionDou/STL
summary: "系统化分析 SGI STL 3.0 源码——6大部分：空间配置器、迭代器、容器（序列/关联）、算法、函数对象、适配器，52个markdown文件，揭示 STL 内部实现细节。"
tags: [cpp, STL, source-code, implementation, template]
---

# STL 源码分析 (SGI STL 3.0)

## Overview

系统化分析 SGI STL 3.0 源码的仓库，按 6 大部分组织，深入剖析 STL 容器、算法、迭代器的内部实现。不同于一般 STL 教程只讲**用法**，本资源揭示**实现原理**，展示 C++ 模板元编程的巅峰技巧。

## Core Content

### Six Major Sections

| 部分 | 内容 | 关键实现 |
|------|------|----------|
| **空间配置器 (Allocators)** | `alloc` 分级配置器 | 一级/二级配置器，内存池 |
| **迭代器 (Iterators)** | iterator traits, iterator adapters | `__type_traits`, `advance`, `distance` |
| **序列容器** | vector, list, deque | 扩容策略、节点结构 |
| **关联容器** | set, map, multiset, multimap | RB-tree 实现 |
| **无序容器** | unordered_set, unordered_map | hashtable 实现 |
| **算法** | copy, rotate, sort | `__copy_traits`, 分治策略 |

### Key Topics Covered

**容器实现细节：**
- `vector`: 1.5x 或 2x 扩容策略，`capacity()` vs `size()`
- `list`: 双向环链表， sentinel node
- `deque`: 分段数组，map 控制块
- `stack`/`queue`: 默认基于 deque
- `heap`: binary heap，父子节点关系
- `RB-tree`: 红黑树旋转、颜色调整、插入删除
- `hashtable`: 负载因子、重哈希、`__next_prime`

**算法实现细节：**
- `copy`: 随机访问 vs 双向 vs 单向迭代器的不同实现
- `rotate`: 两步翻转算法（gcd 分解）
- `__iter_swap`: 依赖迭代器类型的方法

**函数对象：**
- `unary_function`/`binary_function`
- `plus`/`minus`/`equal_to` 等标准函数对象
- `not1`/`not2` 适配器

## 为什么重要

STL 源码是 C++ 模板元编程的百科全书：
- **traits 技术**: 编译期类型萃取
- **SFINAE**: 模板特化选择
- **adapter 模式**: 函数适配器实现
- **内存池**: 避免碎片化

## 相关页面

### Entity 页面
- [[entities/cpp/cpp-stl-containers]] — STL 容器（用法）
- [[entities/cpp/cpp-stl-algorithms]] — STL 算法（用法）
- [[entities/cpp/cpp-stl-iterators]] — STL 迭代器（用法）
- [[entities/cpp/cpp-stl-allocators]] — STL 分配器
- [[entities/cpp/cpp-stl-string]] — string 实现
- [[entities/cpp/cpp-stl-functors]] — 函数对象
- [[entities/cpp/cpp-templates]] — 模板基础

### Source 页面
- [[sources/bookmark-cpp-template-tutorial]] — C++ Template Tutorial（配套）
