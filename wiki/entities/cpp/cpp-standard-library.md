---
type: entity
tags: [cpp, stl, standard-library, containers, algorithms, iterators]
created:2026-06-08
sources: [pdf-book-c-in-a-nutshell, bookmark-modern-cpp-programming]
---

# C++ Standard Library (STL Overview)

## 定义

C++ 标准库（Standard Library）是随 C++ 标准发布的官方库集合，其中最核心的部分是 STL（Standard Template Library）：容器（containers）、算法（algorithms）、迭代器（iterators）、函数对象（function objects）、适配器（adapters）。此外还包括字符串、流、线程、文件系统、智能指针、正则表达式、chrono、optional/variant/any 等 C++11/14/17/20引入的新组件。

##关键要点

- **六大组件**：容器、算法、迭代器、函数对象、适配器、分配器
- **泛型**：基于模板实现类型无关（编译期多态，无运行时开销）
- **头文件组织**：`<vector>`、`<algorithm>`、`<memory>`、`<thread>`、`<filesystem>` 等
- **实现参考**：libstdc++ (GCC)、libc++ (Clang/LLVM)、MSVC STL
- **与 C 标准库关系**：C 标准库函数保留 `<cstdio>`、`<cstdlib>` 等 C++包装版本

##核心概念

- **Sequence containers**：vector、list、deque、array、forward_list
- **Associative**：set/map（有序RB-tree）、unordered_set/map（hash）
- **Iterator categories**：input/output/forward/bidirectional/random_access
- **Allocator-aware**：自定义分配器（`std::allocator` 接口）
- **Ranges (C++20)**：`std::views::filter`、`std::views::transform`延迟视图
- **`<chrono>`**：时间库（duration、time_point、clock）
- **`<format>` (C++20)**：类型安全的字符串格式化

## 相关页面

- [[entities/cpp/cpp-stl-containers]] —容器详解
- [[entities/cpp/cpp-stl-algorithms]] — 算法详解
- [[entities/cpp/cpp-stl-iterators]] —迭代器
- [[entities/cpp/cpp-stl-allocators]] —分配器
- [[entities/cpp/cpp-templates]] —模板基础
- [[entities/cpp/modern-cpp/cpp-stl-format-span]] — C++20 format
