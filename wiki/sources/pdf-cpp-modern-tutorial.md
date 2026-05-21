---
type: source
source-type: pdf
title: "Modern C++ Tutorial (C++11/14/17/20)"
author: "Changkun (hi[at]changkun.de)"
date: 2024-06-01
size: medium
path: raw/PDFs/books/modern-cpp-tutorial-zh-cn.pdf
summary: "现代C++教程，系统讲解C++11/14/17/20核心特性：Lambda、智能指针、RAII、并发、Move语义、模板变参、if constexpr等"
tags: [cpp, modern-cpp, programming]
created: 2026-05-20
---

# Modern C++ Tutorial (C++11/14/17/20)

## 核心内容

本书系统介绍了现代C++（C++11/14/17/20）的核心特性，共10章：

1. **现代C++简介** - C++11/14/17/20概述，与C的对比
2. **核心语言特性** - nullptr、constexpr、auto/decltype、if constexpr、Range-for、统一初始化、委托构造、override/final、=default/=delete、作用域枚举
3. **Lambda表达式** - Lambda语法、捕获、std::function、std::bind、值类别（左值/右值/xvalue/prvalue）、Move语义、std::move、std::forward
4. **容器** - std::array、std::forward_list、unordered容器（std::unordered_map等）、std::tuple
5. **智能指针与RAII** - RAII惯用法、std::shared_ptr、std::unique_ptr、std::weak_ptr
6. **正则表达式** - std::regex基本用法
7. **线程** - std::thread、mutex、lock_guard、unique_lock、future/packaged_task、condition_variable、原子操作与memory_order
8. **文件系统** - std::filesystem
9. **其他特性** - long long int、noexcept、字面量运算符、alignof/alignas
10. **C++20新特性** - Concepts、Modules、Coroutines、Ranges（部分TODO）

## 关键引用

### Move语义核心代码
```cpp
A(A&& a) : pointer(a.pointer) {
    a.pointer = nullptr;
}
```

### RAII与智能指针
```cpp
auto pointer = std::make_shared<int>(10);
auto pointer2 = pointer; // 引用计数+1
std::unique_ptr<int> p = std::make_unique<int>(10);
```

### Lambda表达式
```cpp
auto add = [v1 = 1, v2 = std::move(important)](int x, int y) -> int {
    return x + y + v1 + (*v2);
};
```

### 线程与原子操作
```cpp
std::atomic<int> counter{0};
counter.fetch_add(1, std::memory_order_relaxed);
```

## 相关页面
- [[entities/cpp/move-semantics]] - Move语义与右值引用
- [[entities/cpp/smart-pointers]] - 智能指针与RAII
- [[entities/cpp/lambda-expressions]] - Lambda表达式
- [[entities/cpp/auto-type-deduction]] - auto与decltype类型推导
- [[entities/cpp/constexpr]] - constexpr编译时计算
- [[entities/cpp/concurrency]] - C++并发编程
- [[entities/cpp/raii]] - RAII资源管理惯用法
- [[entities/cpp/variadic-templates]] - 模板变参
- [[entities/cpp/if-constexpr]] - if constexpr编译时分支
- [[entities/cpp/cpp20-features]] - C++20新特性
