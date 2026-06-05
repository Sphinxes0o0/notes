---
title: std::this_thread::yield 源码示例
description: std::this_thread::yield 提示调度器让出时间片的演示
---

# std::this_thread::yield

本目录收录 `std::this_thread::yield()` 的演示代码，对比"主动让出"与"自旋忙等"在调度器层面的差异。

## 文件清单

| 文件 | 内容 |
|------|------|
| `yield.cc` | `std::this_thread::yield()` 基础示例 |
| `yield_demo.cc` | 对比 yield 与忙等 |
| `no_yield_demo.cc` | 反例：自旋忙等的实现 |

## 关键点

- `std::this_thread::yield()` 提示操作系统调度器让出当前线程的 CPU 时间片
- 通常用于**自旋锁**或**忙等循环**中，避免独占 CPU
- 不是阻塞调用，调度器可能立刻再次调度该线程

## 编译与运行

```bash
g++ -std=c++17 -pthread yield.cc -o yield
./yield
```

## 进一步阅读

- [cppreference: std::this_thread::yield](https://en.cppreference.com/w/cpp/thread/yield)
