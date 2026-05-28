---
type: source
source-type: pdf
title: To Be or Not to Be - On Object Lifetime
author: 吴咏炜 (Wu Yongwei)
date: 2024
size: small
path: raw/PDFs/slides/吴咏炜To Be or Not to Be - On Object Lifetime.pdf
summary: 吴咏炜：C++对象生命周期深度解析，placement new、RAII、内存映射、对象状态管理
tags: [cpp, object-lifetime, placement-new, raii, memory, cpp-slides]
created: 2024
---
# To Be or Not to Be — On Object Lifetime

## 核心内容

**Author:** 吴咏炜 | 2024 C++大会

### 对象生命周期的三种状态

```cpp
class Obj {
public:
  Obj();
  ~Obj();
  void init();
  void cleanup();
private:
  // 数据成员
};
Obj* ptr = (Obj*)mmap(...);
ptr->init();
// 开始使用 *ptr
ptr->cleanup();
munmap(ptr, sizeof(Obj));
```

### 核心议题

1. **Placement new** — 在预分配内存上构造对象
2. **显式析构函数调用** — `ptr->~Obj()` vs 隐式析构
3. **对象状态机** — Constructed/Initialized/Active/Cleaned-up/Destroyed
4. **RAII 的边界** — 谁拥有资源，谁负责释放
5. **未初始化内存的危险** — 使用已移动/已析构对象的 UB

### 关键模式

- **手动内存管理**：mmap/munmap + placement new，显式 init/cleanup
- **对象池**：预分配对象集合，重用而非分配/释放
- **生命周期注解**：[[entities/cpp/nodiscard]]、[[maybe_unused]] 辅助编译器检查

## 关键引用

> "To be, or not to be — that is the question." (Shakespeare, Hamlet)

## 相关页面
- [[entities/cpp/cpp-object-lifetime]] — C++对象生命周期
- [[entities/cpp/raii]] — RAII资源管理惯用语
- [[entities/cpp/smart-pointers]] — 智能指针
- [[cpp-index]] — Modern C++ 模块索引