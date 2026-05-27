---
type: source
source-type: github
title: "m07-concurrency — C++ Master: Concurrency Mental Model"
author: "Sphinx Shi"
date: 2026-05-27
size: small
path: raw/Modern-Cpp-Skills/m07-concurrency/SKILL.md
summary: "C++ Master-level skill for concurrency. Core question: How do threads communicate? Covers std::thread, jthread, atomic, mutex, deadlock, race condition, memory model, and C++20 coroutines."
tags: [cpp, master, concurrency, threads, atomic]
---

# m07-concurrency — C++ Concurrency

## 核心內容

**Core Question**: 線程如何通信？

- **Shared State**: Mutexes (`std::mutex`) 或 Atomics (`std::atomic`)
- **Coordination**: Condition Variables (`std::condition_variable`) 或 Latches/Semaphores (C++20)
- **Tasks**: `std::async` 或 Coroutines (C++20)

### Error → Design 映射

| 問題 | 設計問題 |
|------|----------|
| Data Race | 兩個線程訪問內存是否沒有 Happens-Before 邊？ |
| Deadlock | 是否線程 A 鎖了 mutex B 再鎖 A，而另一線程鎖了 A 再鎖 B？ |
| False Sharing | 獨立的 atomic 是否位於同一緩存線？ |
| Live Lock | 線程是否在空轉而無實質進展？ |

### 思維框架

1. **Do I need a thread?** Short task → `std::async` 或 Thread Pool. Long background → `std::jthread`.
2. **Is it shared state?** Yes → Protect with `std::mutex`. Is it small/primitive? → `std::atomic`.
3. **Locks or Atomics?** Logic requiring multiple steps → Mutex. Simple flag/counter → Atomic.

### Quick Reference

| Tool | C++ Version | Use When |
|------|-----------|----------|
| `std::jthread` | C++20 | Standard thread (auto-join). |
| `std::atomic` | C++11 | Lock-free counters/flags. |
| `std::mutex` | C++11 | Locking critical sections. |
| `std::shared_mutex` | C++17 | Read-heavy workloads. |
| `std::latch` | C++20 | Waiting for N tasks to start. |
| `co_await` | C++20 | Async I/O (requires library). |

## 相關 Entity

- [[entities/cpp/modern/modern-m07-concurrency]]
- [[entities/cpp/modern/modern-m03-mutability]]
- [[entities/cpp/concurrency]]