---
type: source
source-type: github
title: "Build Your Own STL in One Weekend"
author: "parallel101"
date: 2024-01-01
summary: "C++新手教学项目，手把手实现STL核心组件：function/unique_ptr/vector/list/optional/map/shared_ptr/variant"
path: raw/github/parallel101/stl1weekend
---

# Build Your Own STL in One Weekend

## 核心内容

9节课，每课实现一个STL组件：

| Lesson | Topic | 关键实现 |
|--------|-------|---------|
| 1 | `std::function` | 类型擦除（Type Erasure）、调用约定 |
| 2 | `std::unique_ptr` | RAII、独占所有权、移动语义 |
| 3 | `std::array` | 固定大小数组、栈分配 |
| 4 | `std::vector` | 动态数组、扩容策略、迭代器失效 |
| 5 | `std::list` | 双向链表、迭代器 |
| 6 | `std::optional` | 可空类型、placement new |
| 7 | `std::map` / `std::set` | 红黑树（RB-tree）、旋转着色、迭代器 |
| 8 | `std::shared_ptr` | 引用计数、删除器 |
| 9 | `std::variant` |  visitation 模式、类型安全联合体 |

### 核心理念
- **可读性优先于性能**：代码面向教学，而非最优实现
- 配合 B 站视频教程使用
- 强调「知其然更知其所以然」

### 关键概念
- **Type Erasure**：`std::function` 通过类型擦除实现泛型调用
- **RAII + Smart Pointers**：`unique_ptr` 独占、`shared_ptr` 共享
- **Red-Black Tree**：`std::map`/`std::set` 的底层实现，5条红黑约束
- **Iterator Pattern**：容器与算法解耦的关键抽象
- **Placement New**：`optional`/`variant` 的内存布局技术
- **Perfect Forwarding**：`make_unique`/`make_shared` 的参数转发

## 相关页面

- [[cpp-stl-containers]] — STL 容器全景：vector/list/deque/set/map
- [[cpp-stl-iterators]] — 迭代器抽象与失效规则
- [[cpp-stl-allocators]] — 容器内存分配机制
- [[cpp-templates]] — 模板元编程是 STL 的基石
- [[smart-pointers]] — unique_ptr / shared_ptr / weak_ptr

## 来源详情

- GitHub: [parallel101/stl1weekend](https://github.com/parallel101/stl1weekend)
- 视频：B 站配套教程
- 语言：C++ (99.5%), CMake
