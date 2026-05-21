---
type: entity
tags: [cpp, modern-cpp, cpp20]
created: 2026-05-20
sources: [pdf-cpp-modern-tutorial]
---

# C++20 Features (C++20新特性)

## 定义

C++20是继C++11以来最大的特性更新，引入了Concepts（概念）、Modules（模块）、Coroutines（协程）、Ranges（范围）等革命性特性，大幅提升了C++的表达能力和安全性。

## 关键要点

- **Concepts（概念）**：编译期约束模板参数类型，提供更清晰的错误信息和接口规范
- **Modules（模块）**：替代头文件，减少编译依赖和提升编译速度
- **Coroutines（协程）**：轻量级协同多任务，suspend/resume机制
- **Ranges（范围）**：统一管道式操作容器，替代STL算法
- **其他特性**：std::format、span、jthread、原子引用

## 代码示例

```cpp
// Concepts示例
template<typename T>
requires Sortable<T> // Sortable概念约束
void sort(T& c);

// 简写形式
template<Sortable T>
void sort(T& c);

// Ranges示例（C++20）
#include <ranges>
std::vector<int> v = {1, 2, 3, 4, 5};
auto result = v | std::views::filter([](int n) { return n % 2 == 0; })
                 | std::views::transform([](int n) { return n * 2; });

// Coroutines示例（伪代码）
task<void> async_read() {
    co_await something_async();
    co_return;
}
```

## 相关概念
- [[entities/cpp/constexpr]] - constexpr的计算能力增强
- [[entities/cpp/if-constexpr]] - if constexpr的完善
- [[entities/cpp/concurrency]] - jthread等并发增强
- [[entities/cpp/lambda-expressions]] - Lambda的改进

## 来源详情
- [[sources/pdf-cpp-modern-tutorial]] - Chapter 10: C++20新特性
