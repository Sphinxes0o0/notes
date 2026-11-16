---
type: entity
tags: [cpp, modern-cpp]
created: 2026-05-20
sources: [pdf-cpp-modern-tutorial]
---

# RAII (Resource Acquisition Is Initialization)

## 定义

RAII是C++的核心编程惯用法，通过对象的构造/析构函数自动管理资源（内存、文件锁、socket等）。资源在构造函数中获取，在析构函数中释放，确保异常安全且无泄漏。

## 关键要点

- **核心思想**：将资源绑定到对象生命周期
- **智能指针**：std::unique_ptr、std::shared_ptr是RAII的典型实现
- **lock_guard**：C++11 mutex的RAII封装
- **异常安全**：栈展开时自动释放资源
- **=C++17**：`=default`显式 defaulted 构造函数，`=delete`禁止某些操作

## 代码示例

```cpp
// lock_guard的RAII行为
std::mutex mtx;
void critical_section(int change_v) {
    std::lock_guard<std::mutex> lock(mtx); // 获取锁
    v = change_v;
} // lock析构，自动释放锁

// =default和=delete
class Magic {
public:
    Magic() = default; // 显式默认构造
    Magic& operator=(const Magic&) = delete; // 禁止拷贝赋值
    Magic(int magic_number);
};

// 智能指针的RAII
auto p = std::make_unique<int>(10);
// unique_ptr析构时自动delete
```

## 相关概念
- [[entities/cpp/smart-pointers]] - 智能指针是RAII的典型应用
- [[entities/cpp/concurrency]] - lock_guard/lock对mutex的RAII封装
- [[entities/cpp/move-semantics]] - 移动语义与RAII结合

## 来源详情
- [[sources/pdf-cpp-modern-tutorial]] - Chapter 5.1: RAII惯用法
