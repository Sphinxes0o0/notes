---
title: MPMC Ring Buffer 实现
description: 多生产者多消费者无锁环形缓冲区的 C++ 实现
---

# MPMC Ring Buffer

本目录收录多生产者多消费者（Multi-Producer Multi-Consumer, MPMC）无锁环形缓冲区的 C++ 实现，使用 `std::atomic` 与 cache-line padding 避免伪共享。

## 文件清单

| 文件 | 内容 |
|------|------|
| `mpmc_ringbuffer.h` | 头文件实现（单头文件包含） |
| `test.cc` | 简单的多线程功能测试 |

## 设计要点

- **无锁**：基于 `std::atomic` 的 `compare_exchange_weak`
- **避免伪共享**：使用 `alignas(64)` 进行 cache-line 对齐
- **定长容量**：使用模运算实现循环索引

## 使用示例

```cpp
#include "mpmc_ringbuffer.h"
MPMCRingBuffer<int, 1024> rb;
// 生产
rb.enqueue(42);
// 消费
int v;
if (rb.dequeue(v)) { /* got v */ }
```

## 编译与运行

```bash
g++ -std=c++17 -pthread test.cc -o test
./test
```
