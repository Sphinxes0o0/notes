---
type: source
source-type: bookmark
title: "C++ Concurrency in Action 第2版 (Web版)"
author: "Anthony Williams; Web版: downdemo"
date: 2024
size: medium
path: raw/github/downdemo/Cpp-Concurrency-in-Action-2ed
summary: "C++11/14/17 多线程编程权威指南 Web 版，含 C++20 新特性（jthread、semaphore、barrier）补充，补充 OS 基础与跨语言对比。"
tags: [cpp, concurrency, multithreading, atomic, mutex, future]
---

# C++ Concurrency in Action 第2版 (Web版)

## Overview

Anthony Williams 著《C++ Concurrency in Action》第2版的 Web 版本，由 downdemo 维护，包含额外的 C++20 特性补充和跨语言对比表（vs Boost/POSIX/Java）。

## Core Content

### Thread Support Library (C++11/14/17/20)

| 头文件 | 关键类型 |
|--------|----------|
| `<thread>` | `std::thread`, `std::jthread` |
| `<stop_token>` | `std::stop_token`, `std::stop_source` |
| `<mutex>` | `std::mutex`, `std::recursive_mutex` |
| `<shared_mutex>` | `std::shared_mutex`, `std::shared_lock` |
| `<condition_variable>` | `std::condition_variable(_any)` |
| `<semaphore>` | `std::counting_semaphore`, `std::binary_semaphore` |
| `<barrier>` | `std::barrier`, `std::flex_barrier` |
| `<latch>` | `std::latch` |
| `<future>` | `std::promise`, `std::future`, `std::shared_future` |
| `<atomic>` | `std::atomic<T>` |
| `<execution>` | `std::execution::par`, `seq`, `unseq`, `par_unseq` |

### 跨语言对比表

| 特性 | C++11 | Boost | POSIX | Java |
|------|-------|-------|-------|------|
| Thread | `std::thread` | `boost::thread` | pthread | `java.lang.Thread` |
| Mutex | `std::mutex` | `boost::mutex` | pthread_mutex | `synchronized` |
| Future | `std::future` | `boost::future` | N/A | `java.util.concurrent.Future` |
| Atomic | `std::atomic` | `boost::atomic` | C11 atomics | `java.util.concurrent.atomic` |

### 补充的 C++20 特性

- **`std::jthread`**: 自动 join 的线程，支持 `stop_token`
- **`std::counting_semaphore`**: 信号量（最多 N 个并发）
- **`std::barrier`**: 屏障同步
- **`std::latch`**: 一次性栅栏
- **`std::atomic<std::shared_ptr<T>>`**: 原子 shared_ptr

## 相关页面

### Entity 页面
- [[entities/cpp/cpp-concurrency-action]] — C++ Concurrency in Action（PDF 版）
- [[entities/cpp/concurrency]] — C++ 并发基础
- [[entities/cpp/cpp-memory-model]] — C++ 内存模型

### Source 页面
- [[sources/cpp-modern-skills]] — Modern C++ Skills（c17-07-concurrency）
