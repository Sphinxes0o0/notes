---
title: C++ 原子操作与内存序
date: 2024-01-20 10:00:00
tags:
    - cpp
    - atomic
    - concurrency
---

## 1. 原子操作基础

### 1.1 什么是原子操作

原子操作（Atomic Operation）是指**不可中断的操作**，即在多线程环境中，该操作要么完全执行完成，要么完全不执行，不会出现部分执行的状态。原子操作保证了操作的**可见性**和**顺序性**，是实现无锁并发编程的基础。

```cpp
// 非原子操作 - 存在数据竞争
int counter = 0;
counter++;  // 读取、递增、写入三步操作，可能被其他线程打断

// 原子操作 - 三步合为一步
std::atomic<int> counter = 0;
counter++;  // 不可中断的单一操作
```

### 1.2 std::atomic 的使用

`std::atomic` 是 C++11 引入的原子类型封装模板，提供了线程安全的原子操作支持。

```cpp
#include <atomic>
#include <thread>
#include <iostream>

std::atomic<int> counter(0);  // 初始化为 0

void increment() {
    for (int i = 0; i < 10000; ++i) {
        counter.fetch_add(1);  // 原子递增
    }
}

int main() {
    std::thread t1(increment);
    std::thread t2(increment);

    t1.join();
    t2.join();

    std::cout << "Counter: " << counter.load() << std::endl;
    // 输出: Counter: 20000
    return 0;
}
```

### 1.3 基本的原子类型

`std::atomic` 对应多种特化版本，适用于不同场景：

| 类型 | 说明 |
|------|------|
| `std::atomic<bool>` | 原子布尔值 |
| `std::atomic<int>` | 原子整型 |
| `std::atomic<int*>` | 原子指针 |
| `std::atomic<float>` | 原子浮点型（C++20） |
| `std::atomic<std::shared_ptr<T>>` | 原子共享指针（C++20） |

```cpp
// 常用操作
std::atomic<int> value(10);

value.store(20);              // 原子写入
int old = value.load();      // 原子读取

int prev = value.fetch_add(5);   // 原子加法，返回旧值
int prev = value.fetch_sub(3);   // 原子减法，返回旧值
bool changed = value.compare_exchange_strong(expected, desired);  // CAS 操作
```

## 2. 内存序 (Memory Order)

内存序（Memory Order）定义了**多线程间内存访问的排序规则**，决定了原子操作如何影响其他线程对内存的观测。不同的内存序对性能有不同的影响，需要根据场景选择合适的内存序。

### 2.1 memory_order_relaxed

**松散内存序**：只保证操作的**原子性**，不保证操作顺序。编译器/CPU 可能对操作进行重排序。

```cpp
std::atomic<int> x(0);
std::atomic<int> y(0);

// 线程 1
void thread1() {
    x.store(1, std::memory_order_relaxed);  // A1
    y.store(1, std::memory_order_relaxed);  // A2
}

// 线程 2
void thread2() {
    // 可能观察到 y=1 但 x=0 的状态
    while (y.load(std::memory_order_relaxed) == 1) {
        std::cout << "x = " << x.load(std::memory_order_relaxed) << std::endl;
        break;
    }
}
```

**适用场景**：计数器递增等不需要同步其他内存的操作。

```cpp
std::atomic<int> counter(0);

// 多个线程可以安全地递增计数器
void increment() {
    counter.fetch_add(1, std::memory_order_relaxed);
}
```

### 2.2 memory_order_consume

**消费内存序**：当前线程中，所有**依赖该原子变量的操作**不会被重排到该操作之前。但对其他无关内存的访问仍可能被重排。

```cpp
std::atomic<int*> ptr;
int data;

void producer() {
    data = 100;
    ptr.store(&data, std::memory_order_release);
}

void consumer() {
    int* p = nullptr;
    while (!(p = ptr.load(std::memory_order_consume))) {
        std::this_thread::yield();
    }
    // p 依赖于 ptr，所以 data=100 的写入一定已经对当前线程可见
    std::cout << "data = " << *p << std::endl;
}
```

### 2.3 memory_order_acquire

**获取内存序**：当前线程中，所有内存读取和写入操作**不会重排到该操作之前**。常用于读取端（load）。

```cpp
std::atomic<bool> ready(false);
int data = 0;

// 生产者
void producer() {
    data = 100;
    ready.store(true, std::memory_order_release);
}

// 消费者
void consumer() {
    while (!ready.load(std::memory_order_acquire)) {
        std::this_thread::yield();
    }
    // data 一定等于 100
    std::cout << "data = " << data << std::endl;
}
```

### 2.4 memory_order_release

**释放内存序**：当前线程中，所有内存读取和写入操作**不会重排到该操作之后**。常用于写入端（store）。

### 2.5 memory_order_acq_rel

**获取-释放内存序**：同时具有 acquire 和 release 的语义。适用于 read-modify-write 操作。

```cpp
std::atomic<int> counter(0);

// 使用 fetch_sub，它是一个 read-modify-write 操作
int old = counter.fetch_sub(1, std::memory_order_acq_rel);
// old 是旧值，减 1 后的结果已写入
```

### 2.6 memory_order_seq_cst

**顺序一致性内存序**（默认）：最严格的内存序，保证**全局顺序一致性**。所有线程看到的操作顺序完全相同。

```cpp
std::atomic<int> x(0);
std::atomic<int> y(0);

// 线程 1
void thread1() {
    x.store(1, std::memory_order_seq_cst);
    y.store(1, std::memory_order_seq_cst);
}

// 线程 2
void thread2() {
    // 一定能观察到 x=1 和 y=1 的顺序一致
    while (y.load(std::memory_order_seq_cst) == 1) {
        std::cout << "x = " << x.load(std::memory_order_seq_cst) << std::endl;
        break;
    }
}
```

**适用场景**：需要严格顺序保证的场景，如锁的实现、复杂的数据结构同步。

## 3. 各内存序的应用场景

### 3.1 计数器递增 (relaxed)

对于简单的计数器，不需要观察其他变量，使用 `memory_order_relaxed` 可获得最佳性能。

```cpp
std::atomic<long long> counter{0};

void increment_counter() {
    // 无需同步其他操作，只保证 counter 的原子性
    counter.fetch_add(1, std::memory_order_relaxed);
}

void get_count() {
    // 只需要读取当前值
    long long count = counter.load(std::memory_order_relaxed);
}
```

### 3.2 标志同步 (acquire/release)

使用 `release` 和 `acquire` 配对实现线程间的同步，适用于**单例模式**、**消息传递**等场景。

```cpp
class Singleton {
private:
    static std::atomic<Singleton*> instance;
    static std::atomic<int> flag;

public:
    static Singleton* get_instance() {
        Singleton* tmp = instance.load(std::memory_order_acquire);
        if (tmp == nullptr) {
            // 模拟锁
            int expected = 0;
            while (!flag.compare_exchange_weak(expected, 1,
                std::memory_order_acq_rel,
                std::memory_order_relaxed)) {
                expected = 0;
                std::this_thread::yield();
            }

            tmp = instance.load(std::memory_order_acquire);
            if (tmp == nullptr) {
                tmp = new Singleton;
                instance.store(tmp, std::memory_order_release);
            }
            flag.store(0, std::memory_order_release);
        }
        return tmp;
    }
};

std::atomic<Singleton*> Singleton::instance{nullptr};
std::atomic<int> Singleton::flag{0};
```

### 3.3 严格顺序 (seq_cst)

对于需要全局顺序一致性的场景，如分布式系统中的事件日志、事务处理，必须使用 `seq_cst`。

```cpp
std::atomic<int> ticket(0);
std::atomic<int> turn(0);

int next_ticket() {
    return ticket.fetch_add(1, std::memory_order_seq_cst);
}

void await_turn(int my_turn) {
    while (turn.load(std::memory_order_seq_cst) < my_turn) {
        std::this_thread::yield();
    }
}

void release_turn() {
    turn.fetch_add(1, std::memory_order_seq_cst);
}

// 所有线程看到的 ticket 和 turn 顺序完全一致
```

## 4. 原子操作实战

### 4.1 原子计数器

实现一个高性能的原子计数器：

```cpp
#include <atomic>
#include <thread>
#include <vector>
#include <iostream>

class AtomicCounter {
private:
    std::atomic<uint64_t> count_{0};

public:
    void increment() {
        count_.fetch_add(1, std::memory_order_relaxed);
    }

    void decrement() {
        count_.fetch_sub(1, std::memory_order_relaxed);
    }

    uint64_t get() const {
        return count_.load(std::memory_order_relaxed);
    }

    uint64_t get_snapshot() const {
        return count_.load(std::memory_order_seq_cst);
    }
};

int main() {
    AtomicCounter counter;
    const int num_threads = 4;
    const int increments_per_thread = 1000000;

    std::vector<std::thread> threads;
    for (int i = 0; i < num_threads; ++i) {
        threads.emplace_back([&counter, increments_per_thread]() {
            for (int j = 0; j < increments_per_thread; ++j) {
                counter.increment();
            }
        });
    }

    for (auto& t : threads) {
        t.join();
    }

    std::cout << "Final count: " << counter.get() << std::endl;
    std::cout << "Expected: " << num_threads * increments_per_thread << std::endl;
    return 0;
}
```

### 4.2 锁的实现

使用原子操作实现一个简单的自旋锁：

```cpp
class SpinLock {
private:
    std::atomic<bool> lock_{false};

public:
    void lock() {
        bool expected = false;
        // CAS 循环直到获取锁
        while (!lock_.compare_exchange_weak(expected, true,
            std::memory_order_acquire,
            std::memory_order_relaxed)) {
            expected = false;  // 重置 expected
            std::this_thread::yield();  // 让出 CPU
        }
    }

    void unlock() {
        lock_.store(false, std::memory_order_release);
    }
};

// 使用 RAII 的锁守卫
class SpinLockGuard {
private:
    SpinLock& lock_;

public:
    explicit SpinLockGuard(SpinLock& lock) : lock_(lock) {
        lock_.lock();
    }

    ~SpinLockGuard() {
        lock_.unlock();
    }

    // 禁止拷贝和移动
    SpinLockGuard(const SpinLockGuard&) = delete;
    SpinLockGuard& operator=(const SpinLockGuard&) = delete;
};

// 使用示例
SpinLock spinlock;
int shared_data = 0;

void worker(int id) {
    for (int i = 0; i < 1000; ++i) {
        SpinLockGuard guard(spinlock);
        ++shared_data;
    }
}
```

### 4.3 无锁数据结构

实现一个简单的无锁栈（Treiber 栈）：

```cpp
#include <atomic>
#include <memory>

template <typename T>
class LockFreeStack {
private:
    struct Node {
        T data;
        Node* next;
        Node(const T& d) : data(d), next(nullptr) {}
    };

    std::atomic<Node*> head_{nullptr};

public:
    ~LockFreeStack() {
        while (head_.load() != nullptr) {
            Node* old_head = head_.load();
            head_.store(old_head->next);
            delete old_head;
        }
    }

    void push(const T& data) {
        Node* new_node = new Node(data);
        Node* old_head;
        do {
            old_head = head_.load(std::memory_order_relaxed);
            new_node->next = old_head;
        } while (!head_.compare_exchange_weak(old_head, new_node,
            std::memory_order_release,
            std::memory_order_relaxed));
    }

    bool pop(T& result) {
        Node* old_head;
        do {
            old_head = head_.load(std::memory_order_acquire);
            if (old_head == nullptr) {
                return false;
            }
        } while (!head_.compare_exchange_weak(old_head, old_head->next,
            std::memory_order_acquire,
            std::memory_order_relaxed));

        result = old_head->data;
        delete old_head;
        return true;
    }

    bool empty() const {
        return head_.load(std::memory_order_acquire) == nullptr;
    }
};

// 使用示例
LockFreeStack<int> stack;
stack.push(1);
stack.push(2);
stack.push(3);

int value;
while (stack.pop(value)) {
    std::cout << value << " ";  // 输出: 3 2 1
}
```

## 5. 常见问题

### 5.1 ABA 问题

ABA 问题是指：**线程 A 读取共享变量的值为 A，准备进行 CAS 操作时，线程 B 将值从 A 改为 B 再改回 A，线程 A 的 CAS 操作仍会成功**，但实际上共享变量已经被修改过。

```cpp
// ABA 问题示例
std::atomic<int> ptr(0);

void thread1() {
    int expected = ptr.load();
    // 此时 thread2 可能已经修改了 ptr 为其他值再改回
    // 但 thread1 仍认为 ptr 是 expected
    ptr.compare_exchange_strong(expected, 2);  // 可能产生问题
}

void thread2() {
    ptr.store(1);  // A -> B (1)
    ptr.store(0);  // B -> A (0)，thread1 不知道
}
```

**解决方案**：使用带标记的指针或双宽度 CAS。

```cpp
#include <atomic>

// 使用版本号解决 ABA 问题
struct TaggedPtr {
    int* ptr;
    unsigned int tag;

    TaggedPtr(int* p = nullptr, unsigned int t = 0) : ptr(p), tag(t) {}
};

class AtomicTaggedPtr {
private:
    std::atomic<uint64_t> combined_{0};

    static uint64_t pack(int* ptr, unsigned int tag) {
        return (reinterpret_cast<uint64_t>(ptr) << 32) | tag;
    }

    static std::pair<int*, unsigned int> unpack(uint64_t combined) {
        return {
            reinterpret_cast<int*>(combined >> 32),
            static_cast<unsigned int>(combined & 0xFFFFFFFF)
        };
    }

public:
    bool compare_exchange(int*& ptr, unsigned int& tag, int* new_ptr) {
        uint64_t expected = pack(ptr, tag);
        uint64_t desired = pack(new_ptr, tag + 1);
        if (combined_.compare_exchange_weak(expected, desired,
            std::memory_order_seq_cst,
            std::memory_order_seq_cst)) {
            return true;
        }
        auto [old_ptr, old_tag] = unpack(expected);
        ptr = old_ptr;
        tag = old_tag;
        return false;
    }
};
```

### 5.2 内存序错误导致的 bug

#### Bug 1: 过度放松导致数据不一致

```cpp
// 错误示例：使用 relaxed 导致 flag 在 data 之前被观察到
std::atomic<int> data{0};
std::atomic<bool> ready{false};

void producer() {
    data.store(100, std::memory_order_relaxed);  // 错误！
    ready.store(true, std::memory_order_relaxed);
}

void consumer() {
    if (ready.load(std::memory_order_relaxed)) {
        // data 可能还是 0
        std::cout << data.load(std::memory_order_relaxed);  // 未定义！
    }
}

// 修正：使用 release/acquire
void producer_fixed() {
    data.store(100, std::memory_order_release);  // 正确
    ready.store(true, std::memory_order_release);
}

void consumer_fixed() {
    if (ready.load(std::memory_order_acquire)) {
        std::cout << data.load(std::memory_order_acquire);  // 正确：100
    }
}
```

#### Bug 2: 锁的内存序错误

```cpp
// 错误示例：使用错误的内存序导致锁失效
class BrokenSpinLock {
    std::atomic<bool> lock_{false};

public:
    void lock() {
        bool expected = false;
        while (!lock_.compare_exchange_weak(expected, true,
            std::memory_order_relaxed,  // 错误！应该用 acquire
            std::memory_order_relaxed)) {
            expected = false;
        }
    }

    void unlock() {
        lock_.store(false, std::memory_order_relaxed);  // 错误！应该用 release
    }
};
```

#### Bug 3: 遗漏内存序导致可见性问题

```cpp
// 错误示例：store 默认是 seq_cst，但 load 使用 relaxed
std::atomic<int> shared_value{0};

void writer() {
    shared_value.store(42, std::memory_order_seq_cst);  // 严格顺序
}

void reader() {
    // 可能观察到旧值，因为 relaxed 不保证可见性
    int value = shared_value.load(std::memory_order_relaxed);
}

// 修正：保持一致的内存序
void reader_fixed() {
    int value = shared_value.load(std::memory_order_seq_cst);  // 或至少 acquire
}
```

## 6. 性能建议

| 场景 | 推荐内存序 | 原因 |
|------|-----------|------|
| 简单计数器 | `relaxed` | 性能最佳，无需同步 |
| 标志位/状态位 | `acquire/release` | 平衡性能和同步需求 |
| 需要立即可见 | `seq_cst` | 严格一致性保证 |
| 复杂同步 | `acq_rel` | 适合 read-modify-write |

```cpp
// 性能测试框架
#include <chrono>
#include <iostream>

template <typename Func>
void benchmark(const char* name, int iterations, Func&& func) {
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < iterations; ++i) {
        func();
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    std::cout << name << ": " << duration.count() << " us" << std::endl;
}

// 不同内存序的性能对比
std::atomic<int> counter{0};

void test_relaxed() {
    counter.fetch_add(1, std::memory_order_relaxed);
}

void test_seq_cst() {
    counter.fetch_add(1, std::memory_order_seq_cst);
}
```

## 7. 总结

| 内存序 | 保证程度 | 性能 | 典型应用 |
|--------|----------|------|----------|
| `relaxed` | 仅原子性 | 最高 | 计数器 |
| `consume` | 数据依赖顺序 | 高 | 依赖链 |
| `acquire` | 之前不重排 | 中 | 读取端同步 |
| `release` | 之后不重排 | 中 | 写入端同步 |
| `acq_rel` | 两端保证 | 中低 | RMW 操作 |
| `seq_cst` | 全局顺序 | 最低 | 严格一致性 |

**最佳实践**：
1. 优先使用默认的 `seq_cst`，确保正确性
2. 在性能关键路径上，根据实际需求选择合适的内存序
3. 使用 `acquire/release` 配对实现高效的同步
4. 避免过度放松内存序导致难以复现的 bug
5. 使用原子操作实现无锁数据结构，减少锁竞争
