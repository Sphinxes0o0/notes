---
type: entity
tags: [cpp, modern-cpp]
created: 2026-05-20
sources: [pdf-cpp-modern-tutorial, pdf-cpp-concurrency]
---

# Concurrency (并发编程)

## 定义

C++11首次引入标准线程库`<thread>`，提供了跨平台的并发编程支持。包括线程管理（std::thread）、同步原语（mutex、condition_variable）、原子操作（std::atomic）和异步编程（std::future）。

## 关键要点

- **std::thread**：创建线程，可调用Lambda或函数对象
- **mutex系列**：std::mutex、std::lock_guard、std::unique_lock
- **condition_variable**：用于线程间通信，实现生产者-消费者模式
- **std::atomic**：原子类型，避免数据竞争
- **memory_order**：std::memory_order_relaxed/acquire/release/seq_cst
- **std::future/std::promise**：线程间返回值传递

## 代码示例

```cpp
// 创建线程
std::thread t([](){
    std::cout << "hello world." << std::endl;
});
t.join();

// mutex与lock_guard
std::mutex mtx;
std::lock_guard<std::mutex> lock(mtx);
// 临界区
} // 自动解锁

// 原子操作
std::atomic<int> counter{0};
counter.fetch_add(1, std::memory_order_relaxed);

// future与async
std::packaged_task<int()> task([](){ return 7; });
std::future<int> result = task.get_future();
std::thread(std::move(task)).detach();
result.wait();
```

## 相关概念
- [[entities/cpp/raii]] - lock_guard是RAII的并发应用
- [[entities/cpp/move-semantics]] - std::thread利用移动语义
- [[entities/cpp/smart-pointers]] - shared_ptr在线程间共享

## 来源详情
- [[sources/pdf-cpp-modern-tutorial]] - Chapter 7: 线程
- [[sources/pdf-cpp-concurrency]] — Concurrency with Modern C++ + C++ Concurrency in Action
- [[sources/pdf-cpp-modern-books]] — C++17 并行算法章节
