---
type: source
source-type: pdf
title: Threads and Locks
author: Chris Phoon
date: 2020
size: small
path: raw/PDFs/books/threads-locks.pdf
summary: C++ 多线程与锁速查：mutex/condition_variable/future/原子操作/死锁避免
created: 2020
tags: []
---
# Threads and Locks

## 核心内容

- **std::thread**：创建、join/detach、move、参数传递
- **互斥量**：mutex/recursive_mutex/timed_mutex/shared_mutex
- **条件变量**：condition_variable/wait/notify_one/notify_all、虚假唤醒
- **Future/Promise**：std::async、launch::async/deferred、get()
- **原子操作**：atomic、memory_order、fetch_add/sub/cmpxchg
- **RAII 锁**：lock_guard、unique_lock、shared_lock
- **死锁避免**：层次锁、避免嵌套、lock ordering

## 相关页面
- [[pdf-book-concurrency-modern-cpp]]
- [[pdf-book-cpp-concurrency-guide]]
- [[pdf-book-concurrency-perf]]