---
type: entity
tags: [cpp, concurrency, multithreading, atomic, mutex, future, thread-pool]
created: 2026-05-25
sources: [pdf-onedrive-batch1]
---

# C++ Concurrency in Action

## 定义
Anthony Williams 著《C++ Concurrency in Action》第 2 版（ Manning, 2019），C++11/14/17 线程库的权威指南，涵盖 std::thread、std::mutex、std::atomic、std::future、lock-free 数据结构、并行算法。

## 关键要点

### 线程管理
- `std::thread` 创建与管理线程、 join/detach、线程 ID
- 线程函数传参、所有权转移、运行时线程数选择

### 数据共享与同步
- 竞争条件与 race condition 的危害
- `std::mutex` 互斥锁、 `std::unique_lock` 灵活锁、 `std::lock()` 避免死锁
- 死锁四条件、预防策略（一次性获取所有锁、按序加锁）
- `std::condition_variable` 条件变量、线程安全队列实现
- `std::recursive_mutex` 递归锁

###  futures 与一次性事件
- `std::async` 异步任务、返回值自动通过 future 传递
- `std::promise` 与 `std::future` 配对、异常保存
- `std::shared_future` 多线程等待同一事件

### C++ 内存模型与原子操作
- 内存位置、对象与并发修改顺序
- `std::atomic` 原子类型、 memory_order_seq_cst / acquire / release
- synchronizes-with 与 happens-before 关系
- 释放序列（release sequence）

### Lock-Free 数据结构
- 无锁 vs wait-free vs lock-based 定义
- 线程安全栈：CAS 实现、 hazard pointers 内存回收
- 线程安全队列：基于节点的 CAS 操作
- ABA 问题识别与处理

### 并行算法设计
- Amdahl 定律、加速比评估
- `std::execution::par` / `seq` / `unseq` / `par_unseq` 执行策略
- `std::for_each`、`std::find`、`std::partial_sum` 并行实现
- 异常安全、数据分区策略

### 高级线程管理
- 线程池：简单实现、任务队列、无锁队列、work-stealing
- 线程中断机制：interrupt points、 interruption_token

### 测试与调试
- 并发 bug 类型：unwanted blocking、race condition
- 多线程代码测试技术、竞争条件压力测试

## 相关概念

- [[entities/cpp/concurrency]] — C++ 并发基础
- [[entities/cpp/cpp-memory-model]] — C++ 内存模型
- [[entities/cpp/smart-pointers]] — 智能指针（线程安全）
- [[entities/cpp/cpp-stl-containers]] — STL 容器与并发
- [[synthesis/topic-os-fundamentals]] — OS 基础综合

## 来源详情

- [[pdf-onedrive-batch1]]
