---
type: entity
tags: [cpp, memory-management, allocators, smart-pointers, raii, memory-pool, performance]
created: 2026-05-23
sources: [pdf-cpp-perf-memory, pdf-cpp-modern-books]
---

# C++ Memory Management

## 定义

C++ 内存管理是控制对象生命周期和内存分配的机制集合。从 C 的原始指针和 malloc/free，到现代 C++ 的智能指针、RAII 和自定义分配器，C++ 提供了多层次的内存管理方案。

## 存储区域

| 区域 | 分配方式 | 生命周期 | 示例 |
|------|----------|----------|------|
| 栈 (Stack) | 自动分配 | 作用域结束时 | 局部变量 |
| 堆 (Heap) | 动态分配 | 手动或智能指针控制 | `new`/`make_shared` |
| 静态存储 | 程序启动/加载时 | 整个程序生命周期 | 全局/static 变量 |
| 自由存储 | 动态分配 | 开发者控制 | `malloc/free` 分配的内存 |

## 内存管理技术

### 原始指针与智能指针

- **原始指针** (`T*`) — 直接内存访问，无自动生命周期管理
- **std::unique_ptr** — 独占所有权，移动语义，零开销
- **std::shared_ptr** — 共享所有权，引用计数，控制块
- **std::weak_ptr** — 弱引用，打破循环引用

### RAII (Resource Acquisition Is Initialization)

- 构造函数获取资源，析构函数释放资源
- 异常安全：栈展开自动调用析构函数
- 是智能指针、互斥锁、文件句柄的基础机制

### 自定义分配器

- STL 容器支持自定义分配器 (`Allocator` 概念)
- 内存池 (memory pool) — 预分配大块，避免频繁系统调用
- 区域分配器 (arena allocator) — 一次性释放整块
- 栈分配器 (stack allocator) — LIFO 模式

### 缓存优化

- 缓存行 (cache line, 64 bytes) 对齐
- 避免伪共享 (false sharing) — 使用 `std::hardware_destructive_interference_size`
- 数据局部性 (data locality) — SoA vs AoS 布局
- 预取 (prefetching) 与写合并 (write-combining)

### 内存泄漏检测

- AddressSanitizer (ASan) — 编译时插桩
- Valgrind (Memcheck) — 运行时二进制分析
- 智能指针消除绝大多数泄漏

## 相关概念

- [[entities/cpp/smart-pointers]] — 智能指针详解
- [[entities/cpp/raii]] — RAII 资源管理
- [[entities/cpp/cpp-stl-allocators]] — STL 分配器机制
- [[entities/cpp/move-semantics]] — 移动语义减少拷贝
- [[entities/cpp/cpp-perf-optimization]] — 性能优化中的内存考量
- [[entities/c/c-language]] — C 语言手动内存管理

## 来源详情

- [[sources/pdf-cpp-perf-memory]] — 性能与内存管理 4 册
- [[sources/pdf-cpp-modern-books]] — Modern C++ 书籍的内存章节
