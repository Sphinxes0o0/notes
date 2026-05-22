---

type: entity
tags: [C, C++, 系统编程, 语言]
created: 2026-05-20


sources: [notes-ccpp, pdf-cpp-modern-tutorial, pdf-cpp-effective-stl]---

# C/C++ 系统编程

C/C++ 是系统编程的核心语言，提供了对底层硬件的直接控制能力。

## 定义

C 语言是一种过程式编程语言，以接近硬件的底层操作能力著称；C++ 在 C 基础上添加了面向对象、泛型编程等高级特性，成为最强大的系统级编程语言之一。

## 关键要点

### 内存模型

- **栈（Stack）**：后进先出（LIFO），自动分配/释放，存储局部变量、函数参数、返回地址；大小有限（~1MB）
- **堆（Heap）**：动态内存池，通过 `malloc`/`free` 手动管理，适合运行时确定大小的数据结构
- **静态/全局内存（Data Segment）**：`.data`（已初始化）和 `.bss`（未初始化），程序启动时分配，程序结束时释放
- **代码段（Text Segment）**：存储机器指令，只读

### 内存分配方式

| 方式 | 函数 | 特点 |
|------|------|------|
| 自动分配 | 局部变量声明 | 编译器管理，高效 |
| 静态分配 | `static`/全局变量 | 程序启动到结束 |
| 动态分配 | `malloc`/`calloc`/`realloc`/`free` | 灵活但需手动管理 |

### 常见内存问题

- **内存泄漏**：分配后未释放，指针丢失
- **悬空指针**：访问已释放内存
- **重复释放**：对同一块内存调用多次 `free`
- **缓冲区溢出**：读写超出分配区域
- **分配失败**：未检查 `malloc` 返回值

### C++ STL 容器

容器分类：序列容器（vector, deque, list）、容器适配器（stack, queue, priority_queue）、关联容器（set, map）、无序关联容器（unordered_set, unordered_map）。

| 容器 | 底层结构 | 随机访问 | 插入/删除 | 适用场景 |
|------|----------|----------|-----------|----------|
| vector | 动态数组 | O(1) | 尾部O(1) | 尾部操作多 |
| deque | 分块数组 | O(1) | 头尾O(1) | 双端操作 |
| list | 双向链表 | O(n) | O(1) | 高频修改 |
| unordered_map | 哈希表 | N/A | 平均O(1) | 快速查找 |
| map | 红黑树 | N/A | O(log n) | 有序遍历 |

### 迭代器

迭代器是 STL 的核心抽象，连接容器与算法。按能力分为 5 类：输入迭代器 → 输出迭代器 → 前向迭代器 → 双向迭代器 → 随机访问迭代器。

### C++ 设计模式：单例模式

单例模式确保类只有一个实例，提供全局访问点。C++ 实现方式包括：
- **饿汉式**：程序启动时创建，天然线程安全
- **懒汉式 + 双检锁**：延迟创建，线程安全
- **Meyer's Singleton**：C++11 推荐，简洁且线程安全

## 相关概念

- [[entities/sys]] — 系统编程基础（ELF、IPC）
- [[entities/security]] — 底层安全（内存漏洞）
- entities/linux — Linux 系统调用

## 来源详情

- github-notes-ccpp — C/C++ 学习笔记（内存管理、STL 容器、单例模式、编译过程）

### 现代C++特性 (C++11/14/17/20)

- [[entities/cpp/move-semantics]] — 移动语义与右值引用
- [[entities/cpp/smart-pointers]] — 智能指针（shared_ptr/unique_ptr/weak_ptr）
- [[entities/cpp/lambda-expressions]] — Lambda表达式与闭包
- [[entities/cpp/auto-type-deduction]] — auto与decltype类型推导
- [[entities/cpp/constexpr]] — constexpr编译时计算
- [[entities/cpp/raii]] — RAII资源管理惯用法
- [[entities/cpp/concurrency]] — C++并发编程（线程、原子操作）
- [[entities/cpp/variadic-templates]] — 模板变参与参数包展开
- [[entities/cpp/if-constexpr]] — if constexpr编译时分支
- [[entities/cpp/cpp20-features]] — C++20新特性（Concepts/Ranges/Coroutines）
