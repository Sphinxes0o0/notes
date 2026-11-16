---
type: entity
tags: [c, programming-language, systems-programming, procedural, memory]
created: 2026-05-23
sources: [pdf-c-language]
---

# C Programming Language

## 定义

C 语言是由 Dennis Ritchie 在 1972 年于贝尔实验室开发的过程式编程语言，是 UNIX 操作系统的实现语言。C 语言以其高效、灵活和底层硬件访问能力成为系统编程的基石。ANSI C (C89) 和后续的 C99/C11 标准持续演进。

## 核心特性

### 类型系统

- 基本类型：char、int、float、double
- 派生类型：指针、数组、结构体 (struct)、联合体 (union)
- void 类型表示无类型
- C11 引入泛型表达式 (`_Generic`)

### 指针与内存管理

- 指针提供直接内存地址操作
- 数组名退化为指针
- 手动内存管理：`malloc()` / `free()`
- 指针算术与函数指针
- 无自动垃圾回收或 RAII

### 函数与程序结构

- 函数是 C 程序的基本组成单元
- 头文件 (.h) 与源文件 (.c) 分离
- 内部链接 (static) 与外部链接 (extern)
- C11 引入匿名结构和联合体

### 标准库

- I/O: `<stdio.h>` — printf/scanf/fopen/fread/fwrite
- 字符串: `<string.h>` — strlen/strcpy/strcmp
- 内存: `<stdlib.h>` — malloc/free/atoi/qsort/bsearch
- 数学: `<math.h>`
- C11 新增：`<stdatomic.h>` (原子操作)、`<threads.h>` (线程)

## C 与 C++ 的关系

- C++ 最初是 "C with Classes"，保持了对 C 的向后兼容
- C++ 引入了 OOP、异常、模板、RAII 等 C 不支持的机制
- Modern C (C11/C17) 引入了 C 特有的一些现代特性
- C 代码可以通过 `extern "C"` 在 C++ 中调用

## 相关概念

- [[entities/cpp/raii]] — C 手动管理与 C++ RAII 的对比
- [[entities/cpp/smart-pointers]] — C 原始指针 vs C++ 智能指针
- [[entities/cpp/cpp-stl-allocators]] — C 的 malloc/free 与 C++ 分配器体系
- [[entities/cpp/concurrency]] — C11 threads.h 与 C++ std::thread 对比
- [[sys-prog-index]] — 系统编程导航

## 来源详情

- [[sources/pdf-c-language]] — K&R C + C in a Nutshell
- [[sources/pdf-cpp-modern-books]] — Modern C (Jens Gustedt)
