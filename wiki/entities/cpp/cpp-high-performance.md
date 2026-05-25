---
type: entity
tags: [cpp, performance, optimization, memory, templates, concurrency]
created: 2026-05-25
sources: [pdf-onedrive-batch1]
---

# C++ High Performance

## 定义
Björn Andrist & Viktor Sehr 著《C++ High Performance》第 2 版（Packt, 2020），讲解现代 C++（C++11/14/17）高性能编程：零成本抽象、内存管理、性能分析与优化、模板元编程、ranges、并发基础。

## 关键要点

### C++ 高性能哲学
- 零成本抽象（Zero-cost abstractions）：不为你不用的东西付出代价
- 值语义 vs 引用语义、const 正确性
- C++ 对比 C、Rust、Go、Java 的性能特点

### 内存管理
- 虚拟地址空间、内存页、堆 vs 栈
- 对象内存布局：对齐、padding、内存布局优化
- `new`/`delete` 运算符、placement new
- 智能指针：`unique_ptr`、`shared_ptr`、`weak_ptr`、small object optimization
- 自定义内存分配器（arena/池）、`std::pmr::memory_resource`

### 数据结构与算法性能
- `std::vector` vs `std::deque` vs `std::list` 的性能权衡
- `std::string_view`（避免字符串拷贝）、`std::span`（消除数组衰减）
- 平衡复杂度保证与开销、选择合适 API
- 并行数组（Structure of Arrays vs Array of Structures）

### Ranges 与 Views
- Ranges 库解决算法库局限性：组合性、惰性求值
- Range view 适配器：`transform_view`、`filter_view`、`take_view`
- View 是非拥有型范围、有复杂度保证、lazy evaluation

### 模板与泛型编程
- 模板元编程、类型特征（type traits）、`static_assert`
- `constexpr` 函数、编译时计算、`consteval` 立即函数
- `if constexpr` 编译时分支
- Concepts 约束：语义约束 vs 语法约束

### 并发基础
- 并发 vs 并行、共享内存与数据竞争
- `std::mutex`、`std::atomic` 基础
- 死锁避免策略、同步 vs 异步任务

### 编译期编程
- Template metaprogramming 基础
- 编译时 `if constexpr` 与类型计算
- Concepts 与 SFINAE

## 相关概念

- [[entities/cpp/cpp-perf-optimization]] — C++ 性能优化
- [[entities/cpp/cpp-memory-management]] — C++ 内存管理
- [[entities/cpp/constexpr]] — constexpr 编译时计算
- [[entities/cpp/cpp-stl-containers]] — STL 容器
- [[entities/cpp/concurrency]] — C++ 并发

## 来源详情

- [[pdf-onedrive-batch1]]
