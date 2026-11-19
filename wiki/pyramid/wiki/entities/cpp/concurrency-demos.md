---
type: entity
tags: [C++, 并发, 无锁编程, 内存序, future]
created: 2026-05-25
sources: [notes-ccpp-concurrency]
---

# C++ 并发编程实战

## 定义

本页面汇集 C++ 并发编程的实战演示代码，覆盖无锁数据结构、内存序、async 编程、多线程生命周期管理等核心主题。

## 核心演示主题

### 1. MPMC 无锁环形缓冲区

多生产者多消费者（Multi-Producer Multi-Consumer）无锁队列，基于 CAS 和内存序实现。

**关键设计：**
- `alignas(64)` 避免 head/tail 竞争（False Sharing）
- 2^N 容量用 mask 优化模运算
- push：CAS tail → `release`（写入对消费者可见）
- pop：CAS head → `acquire`（读取到最新值）

### 2. 内存序演示（mem_order_demo.cc）

三种内存序的对比实验：

```cpp
enum class Mode { RELAXED, SEQ_CST, ACQ_REL };

// RELAXED: data == 42 的断言可能失败
// ACQ_REL: release/acquire 配对，同步亲缘线程
// SEQ_CST: 全局顺序一致，最严格
```

### 3. std::future / std::promise

```cpp
void worker(std::promise<int> p) {
    p.set_value(42);
}
std::promise<int> promise;
auto future = promise.get_future();
std::thread t(worker, std::move(promise));
int value = future.get(); // 阻塞等待
```

### 4. std::async 并行求和

```cpp
template <typename RandomIt>
int parallel_sum(RandomIt beg, RandomIt end) {
    if (len < 1000) return std::accumulate(beg, end, 0);
    auto handle = std::async(std::launch::async, parallel_sum, mid, end);
    return parallel_sum(beg, mid) + handle.get();
}
```

### 5. 线程局部 atexit（multithread_atexit.c）

- **atexit 在注册线程退出时调用**，非主线程专属
- **LIFO 顺序**：后注册的先调用
- 子线程可注册自己的 atexit 回调，程序退出时在对应线程调用

### 6. yield 让出调度

- `std::this_thread::yield()` 提示调度器让出 CPU 时间片
- 忙等待轮询场景配合使用

## 相关概念

- [[notes-ccpp-concurrency]] — 源码来源（future/promise/async, mpmc_ringbuffer, memory_order）
- [[cpp-concurrency]] — C++ 并发编程语言层面的抽象（`std::thread`、`std::mutex`、`std::condition_variable`）
- [[cpp-stl-containers]] — STL 容器的线程安全注意事项

## 来源详情

- [[notes-ccpp-concurrency]]
