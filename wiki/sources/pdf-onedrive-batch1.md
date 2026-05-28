---
type: source
source-type: pdf
title: OneDrive Batch P — 5 PDFs (OS + C++)
author: Multiple
date: 2026-05-25
size: large
path: raw/PDFs/books/
summary: "Batch P: 2 OS textbooks (Operating System Concepts + 现代操作系统) + 3 C++ books (Concurrency in Action + High Performance + Templates 2nd Ed)"
created: 2026-05-25
tags: []
---
# OneDrive Batch P — 5 PDFs (OS + C++)

## 概述

Batch P 从 OneDrive ebooks 目录提取，共 5 个 PDF：2 个操作系统教材 + 3 个 C++ 技术书籍。

> **Note**: OneDrive 文件首次读取触发按需下载（streaming），大型 OS PDF（200MB+）未能完成 PyPDF2 文本提取。OS entity 页面基于书籍已知结构创建，内容覆盖操作系统经典主题。

## 来源列表

### OS 类（2 册）

| 书名 | 文件 | 状态 |
|------|------|------|
| Operating System Concepts (10th Ed) | Silberschatz, Galvin & Gagne | ⚠️ OneDrive streaming timeout — 基于结构创建 |
| 现代操作系统 原理与实现 | 中文操作系统教材 | ⚠️ OneDrive streaming timeout — 基于结构创建 |

### C++ 类（3 册）

| 书名 | 文件 | 状态 |
|------|------|------|
| C++ Concurrency in Action (2nd Ed) | Anthony Williams, Manning 2019 | ✅ PyPDF2 提取（97,918 chars / 50 pages）|
| C++ High Performance (2nd Ed) | Andrist & Sehr, Packt 2020 | ✅ PyPDF2 提取（76,465 chars / 50 pages）|
| C++ Templates (2nd Ed) | Vandevoorde, Josuttis & Gregor, Pearson 2018 | ✅ PyPDF2 提取（105,878 chars / 50 pages）|

## 核心内容

### Operating System Concepts
经典 OS 教材，Silberschatz 等人撰写：
- 进程管理、线程、CPU 调度（FCFS/SJF/RR/MFQ）
- 进程同步：临界区、互斥、信号量、监视器、死锁
- 内存管理：分页、分段、虚拟内存、页面置换
- 文件系统：inode、目录、空闲空间管理
- I/O 系统：设备调度、缓冲、磁盘调度

### 现代操作系统 原理与实现
中文 OS 教材：
- 操作系统架构、进程/线程模型
- 内存管理：虚拟内存、SLUB/Buddy 分配器
- 文件系统、VFS、I/O 子系统
- 链接与加载：ELF、GOT/PLT

### C++ Concurrency in Action (2nd Ed)
Anthony Williams（C++ 标准委员会成员）撰写：
- C++11/14/17 线程库：std::thread、std::mutex、std::atomic
- 内存模型：synchronizes-with、happens-before、memory_order
- Lock-free 数据结构：CAS、hazard pointers、ABA 问题
- 并行算法：C++17 execution policies
- 线程池与 work-stealing

### C++ High Performance (2nd Ed)
Andrist & Sehr 撰写：
- 零成本抽象哲学、C++ vs 其他语言性能对比
- 内存管理：arena、自定义分配器、small object optimization
- Ranges & Views：惰性求值、组合性
- 模板元编程：constexpr、if constexpr、Concepts
- 并发基础：mutex、atomic、避免死锁

### C++ Templates (2nd Ed)
Vandevoorde, Josuttis, Gregor 撰写（823 页模板权威指南）：
- 函数/类模板、模板参数推导
- 可变模板（variadic templates）与 fold expressions
- SFINAE、enable_if、模板元编程
- Move 语义与完美转发
- Concepts（C++20 先驱）
- 模板实践：链接模型、错误解读

## 关键引用

### C++ Concurrency in Action
> "This book is an in-depth guide to the concurrency and multithreading facilities from the new C++ Standard, from the basic usage of std::thread, std::mutex, and std::async, to the complexities of atomic operations and the memory model." — Anthony Williams

### C++ High Performance
> "C++ High Performance teaches you a C++ dialect for rapidly developing high-performance code. From C++11 onward, there has been a vast array of new features in both the C++ language and the C++ STL." — Ben Garney (Foreword)

## 相关页面

### OS Entities
- [[entities/os/os-concept]] — Operating System Concepts
- [[entities/os/modern-operating-system]] — 现代操作系统 原理与实现

### C++ Entities
- [[entities/cpp/cpp-concurrency-action]] — C++ Concurrency in Action
- [[entities/cpp/cpp-high-performance]] — C++ High Performance
- [[entities/cpp/cpp-templates-v2]] — C++ Templates 第二版

### Module Indexes
- [[os-index]] — Operating System 模块索引
- [[cpp-index]] — Modern C++ 模块索引

### Related Sources
- [[sources/pdf-concurrency-perf]] — 并发与并行编程 2 册（OSTEP + perfbook）
- [[sources/pdf-linux-kernel-books]] — Linux 内核 2 册
- [[sources/pdf-cpp-concurrency]] — C++ 并发编程 2 册合集
- [[sources/pdf-cpp-templates]] — C++ Templates 2nd Ed（已有单本源页）
