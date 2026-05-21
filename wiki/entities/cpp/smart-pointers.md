---
type: entity
tags: [cpp, modern-cpp]
created: 2026-05-20
sources: [pdf-cpp-modern-tutorial]
---

# Smart Pointers (智能指针)

## 定义

C++11引入的智能指针通过RAII惯用法自动管理动态内存，有效防止内存泄漏。std::unique_ptr实现独占所有权，std::shared_ptr实现共享所有权，std::weak_ptr解决循环引用问题。

## 关键要点

- **std::shared_ptr**：引用计数，共享所有权，需注意循环引用
- **std::unique_ptr**：独占所有权，不可复制，可移动
- **std::weak_ptr**：配合shared_ptr使用，不增加引用计数，用于解决循环引用
- **std::make_shared / std::make_unique**：安全的创建智能指针方式
- **get()/reset()/use_count()**：shared_ptr的常用操作

## 代码示例

```cpp
// shared_ptr使用
auto pointer = std::make_shared<int>(10);
auto pointer2 = pointer; // 引用计数变为2
std::cout << pointer.use_count() << std::endl; // 2

// unique_ptr使用（C++14）
auto p = std::make_unique<int>(10);
auto p2 = std::move(p); // 所有权转移，p变为空

// weak_ptr解决循环引用
struct B;
struct A {
    std::shared_ptr<B> pointer;
};
struct B {
    std::weak_ptr<A> pointer; // 使用weak_ptr避免循环引用
};
```

## 相关概念
- [[entities/cpp/raii]] - RAII是智能指针的理论基础
- [[entities/cpp/move-semantics]] - unique_ptr利用移动语义转移所有权
- [[entities/cpp/cpp20-features]] - C++20的std::enable_shared_from_this增强

## 来源详情
- [[sources/pdf-modern-cpp-tutorial]] - Chapter 5: 智能指针与RAII
