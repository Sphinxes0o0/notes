---
type: source
source-type: github
title: "C++ 并发编程实战笔记"
date: 2026-05-25
path: raw/github/notes/ccpp/concurrency/
summary: "C++ 并发编程实战演示代码：MPMC 无锁环形缓冲区、内存序演示、std::future/promise/async、线程局部退出处理、多线程 atexit"
---

# C++ 并发编程实战笔记

## 核心内容

**代码演示文件：**

| 目录 | 文件 | 主题 |
|------|------|------|
| mpmc_ringbuffer/ | mpmc_ringbuffer.h | MPMC 无锁环形缓冲区（CAS + memory_order）|
| memory_order/ | mem_order_demo.cc | C++ 内存序演示（relaxed/acq_rel/seq_cst）|
| future/ | future.cc, promise.cc, shared_future.cc, async.cc | std::future/promise/shared_future/std::async |
| multithreads/ | multithread_atexit.c | 线程局部 atexit 回调（LIFO 顺序）|
| yield/ | yield.cc, no_yield_demo.cc | CPU yield 让出调度演示 |
| - | get_id.cc, sleep_utils.cc | 线程 ID / sleep 工具 |

## MPMC 环形缓冲区

```cpp
template <typename T, size_t N>
class MPMCRingBuffer {
    alignas(64) std::atomic<size_t> head_ {0};
    alignas(64) std::atomic<size_t> tail_ {0};
    T buffer_[N];
    // CAS push/pop，memory_order_acquire/release 防重排
};
```
- **64 字节对齐**：避免 False Sharing（head/tail 落在同一 cache line）
- **2^N 容量**：mask 替代模运算
- **push**：CAS tail → release 确保写入对消费者可见
- **pop**：CAS head → acquire 确保读取到最新值

## 内存序演示

```cpp
// producer
data = 42;
ready.store(true, std::memory_order_release); // release: 之前的写对消费者可见

// consumer
while (!ready.load(std::memory_order_acquire)); // acquire: 看到 release 后的所有写
assert(data == 42);
```

- **relaxed**：无同步，仅保证原子性
- **acquire/release**：配对使用，同步亲缘线程间内存
- **seq_cst**：全局顺序一致（最严格，默认）

## 相关概念

- [[concurrency-demos]] — C++ 并发编程演示实体页

## 来源详情

- **来源路径**: `raw/github/notes/ccpp/concurrency/`
- **代码文件**: mpmc_ringbuffer.h, mem_order_demo.cc, future/*.cc, multithread_atexit.c 等
- **领域**: C++ 并发、无锁数据结构、内存模型、async 编程
