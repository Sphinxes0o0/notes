---
title: 协程
---

# 协程

## 1. 协程概念

### 1.1 什么是协程

协程（Coroutine）是一种用户态的轻量级线程，也称为"协作式程序"或"非抢占式多任务"。与传统的线程不同，协程的调度完全由程序员控制，而不是由操作系统内核进行抢占式调度。

协程的核心思想是：在执行过程中，可以主动暂停执行并将控制权交给其他协程，之后再恢复执行。这种暂停和恢复的机制被称为"上下文切换"，但这个切换完全在用户态完成，不需要内核参与。

```cpp
// 协程的基本概念
void coroutine_example() {
    std::cout << "Step 1" << std::endl;
    co_await std::suspend_always{};  // 暂停协程
    std::cout << "Step 2" << std::endl;
    co_await std::suspend_always{};  // 再次暂停
    std::cout << "Step 3" << std::endl;
}
```

### 1.2 协程 vs 线程

| 特性 | 协程 | 线程 |
|------|------|------|
| 调度方式 | 协作式（协程主动让出） | 抢占式（内核强制调度） |
| 上下文切换 | 用户态，速度快（微秒级） | 内核态，有开销（毫秒级） |
| 并行性 | 单线程内模拟并发 | 真正的并行执行 |
| 资源消耗 | 极低 | 较高（栈空间、线程描述符） |
| 复杂度 | 需要程序员控制流程 | 内核自动管理 |
| 确定性 | 执行顺序确定 | 执行顺序不确定 |

```cpp
// 线程示例：执行顺序不确定
void thread_func() {
    std::cout << "Thread" << std::endl;
}

int main() {
    std::thread t1(thread_func);
    std::thread t2(thread_func);
    t1.join();
    t2.join();
    // 输出顺序可能不同
}

// 协程示例：执行顺序确定
void coroutine_func(std::coroutine_handle<> h) {
    std::cout << "Coroutine" << std::endl;
    h.resume();  // 显式恢复另一个协程
}
```

### 1.3 协程 vs 进程

| 特性 | 协程 | 进程 |
|------|------|------|
| 调度实体 | 用户态线程 | 操作系统调度单位 |
| 地址空间 | 共享同一进程的地址空间 | 独立的地址空间 |
| 通信方式 | 直接内存访问、队列 | 进程间通信（IPC） |
| 创建开销 | 极低（仅分配栈帧） | 较高（复制页表、文件描述符等） |
| 隔离性 | 无隔离，共享资源 | 完全隔离 |
| 上下文大小 | 几十字节到几KB | 几MB（栈空间） |

## 2. 协程的特点

### 2.1 用户态调度

协程的调度完全在用户态完成，不需要进入内核态。这意味着：

- 调度开销极低，可以频繁进行
- 不需要系统调用，避免了用户态/内核态切换的开销
- 可以精确控制调度时机

```cpp
// 用户态调度示例
class Scheduler {
    std::vector<std::coroutine_handle<>> ready_queue;

public:
    void schedule(std::coroutine_handle<> h) {
        ready_queue.push_back(h);
    }

    void run() {
        while (!ready_queue.empty()) {
            auto h = ready_queue.back();
            ready_queue.pop_back();
            h.resume();  // 用户态直接恢复协程
        }
    }
};
```

### 2.2 非抢占式

协程是协作式调度的，不会被强制中断。只有当协程主动调用 `co_await`、`co_yield` 或 `co_return` 时，控制权才会被让出。

```cpp
// 非抢占式调度示例
task process_data() {
    // 协程会一直执行到这里
    auto data = co_await fetch_data();  // 让出控制权

    // 处理完成后再次让出
    co_await process(data);  // 让出控制权

    // 最后返回结果
    co_return result;
}
```

### 2.3 保存/恢复执行上下文

协程在暂停时需要保存完整的执行上下文，包括：

- 程序计数器（PC）/指令指针
- 栈指针（SP）
- 寄存器集合
- 协程的局部变量状态

```cpp
// C++20 协程上下文保存示例
struct saved_state {
    void* rsp;      // 栈指针
    void* rip;      // 指令指针
    f Register;     // 浮点寄存器
    // ... 其他寄存器
};

// 编译器自动生成状态保存代码
task my_coroutine() {
    int local_var = 42;  // 协程局部变量被保存
    co_await suspend_always{};
    // 恢复时 local_var 的值被还原
}
```

## 3. 协程的分类

### 3.1 对称协程 vs 非对称协程

**对称协程**：所有协程地位平等，任何协程都可以直接切换到任何其他协程。

```cpp
// 对称协程模型
void symmetric_coroutine(Scheduler& sched) {
    std::cout << "A" << std::endl;
    sched.transfer_to(sched.next());  // 直接切换到下一个协程
    std::cout << "A resumed" << std::endl;
}
```

**非对称协程**：协程之间存在调用者和被调用者的关系，形成类似函数调用的层次结构。

```cpp
// 非对称协程模型（类似调用）
void asymmetric_caller() {
    std::cout << "Caller start" << std::endl;
    co_await suspend_always{};  // 暂停，等待被调用者返回
    std::cout << "Caller resumed" << std::endl;
}

void asymmetric_callee() {
    std::cout << "Callee" << std::endl;
    // 显式恢复调用者
}
```

### 3.2 有栈 vs 无栈协程

**有栈协程（Stackful Coroutine）**：每个协程都有独立的栈空间，可以进行深层函数调用。

```cpp
// boost.coroutine2 有栈协程示例
#include <boost/coroutine2/all.hpp>

void cooperative(boost::coroutines::asymmetric_coroutine<int>::pull_type& source) {
    for (int value : source) {
        std::cout << value << std::endl;
    }
}

void main() {
    boost::coroutines::asymmetric_coroutine<int>::push_type sink(cooperative);
    for (int i = 0; i < 5; ++i) {
        sink(i);  // 推送数据到协程
    }
}
```

**无栈协程（Stackless Coroutine）**：协程没有独立栈，只能在函数顶层暂停，不能在子函数中暂停。

```cpp
// C++20 无栈协程示例
task my_task() {
    // 可以在子函数中 co_await，但协程本身没有独立栈
    auto result = co_await async_operation();
    co_return result;
}

// Python yield 无栈协程示例
def my_generator():
    yield 1
    yield 2
    yield 3

gen = my_generator()
print(next(gen))  # 1
print(next(gen))  # 2
```

### 3.3 常见实现示例

#### ucontext（POSIX）

```cpp
#define _XOPEN_SOURCE 700
#include <ucontext.h>

char stack[16384];

void coroutine_func(int value) {
    std::cout << "Coroutine: " << value << std::endl;
}

int main() {
    ucontext_t context, main_context;

    getcontext(&context);
    context.uc_stack.ss_sp = stack;
    context.uc_stack.ss_size = sizeof(stack);
    context.uc_link = &main_context;

    makecontext(&context, (void(*)(void))coroutine_func, 1, 42);

    swapcontext(&main_context, &context);
    std::cout << "Back to main" << std::endl;

    return 0;
}
```

#### boost.coroutine

```cpp
#include <boost/coroutine2/all.hpp>
#include <iostream>

void fiber(boost::coroutines::asymmetric_coroutine<int>::pull_type& source) {
    for (int value : source) {
        std::cout << "Fiber received: " << value << std::endl;
    }
}

int main() {
    boost::coroutines::asymmetric_coroutine<int>::push_type push(fiber);
    for (int i = 1; i <= 3; ++i) {
        push(i);
    }
    return 0;
}
```

#### goroutine（Go）

```go
// Go 语言协程示例
package main

import (
    "fmt"
    "time"
)

func worker(id int) {
    for i := 0; i < 5; i++ {
        fmt.Printf("Worker %d: %d\n", id, i)
        time.Sleep(time.Millisecond * 100)
    }
}

func main() {
    // 创建多个 goroutine
    for i := 1; i <= 3; i++ {
        go worker(i)
    }

    // 等待协程完成
    time.Sleep(time.Second)
}
```

#### Python yield

```python
# Python 生成器/协程示例
def my_coroutine():
    value = yield "Ready"
    while value is not None:
        value = yield value * 2

coro = my_coroutine()
print(next(coro))        # 发送初始值，获取 "Ready"
print(coro.send(10))     # 发送 10，得到 20
print(coro.send(5))      # 发送 5，得到 10
coro.close()
```

## 4. C++ 协程

### 4.1 C++20 coroutine 关键字

C++20 引入了以下关键字支持协程：

- `co_await`：暂停协程，等待表达式完成
- `co_yield`：暂停协程并返回值（类似 yield）
- `co_return`：协程返回（隐式生成 return 语句）

```cpp
// C++20 协程头文件
#include <coroutine>

// 基本协程函数
std::coroutine_handle<> my_coroutine() {
    std::cout << "Start" << std::endl;
    co_await std::suspend_always{};
    std::cout << "Middle" << std::endl;
    co_await std::suspend_always{};
    std::cout << "End" << std::endl;
}
```

### 4.2 co_await, co_yield, co_return

```cpp
// co_await 示例：等待异步操作
struct awaitable {
    bool await_ready() const { return false; }
    void await_suspend(std::coroutine_handle<> h) {
        // 异步操作完成后的回调
    }
    int await_resume() { return 42; }
};

task get_value() {
    int result = co_await awaitable{};
    co_return result;
}

// co_yield 示例：生成值
struct generator {
    struct promise_type {
        int current_value;

        generator get_return_object() {
            return generator{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_always initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_void() {}
        std::suspend_always yield_value(int value) {
            current_value = value;
            return {};
        }
    };

    std::coroutine_handle<promise_type> handle;
    explicit generator(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~generator() { if (handle) handle.destroy(); }

    int value() const { return handle.promise().current_value; }
    void next() { handle.resume(); }
};

generator fibonacci() {
    int a = 0, b = 1;
    while (true) {
        co_yield a;
        int next = a + b;
        a = b;
        b = next;
    }
}

// co_return 示例：返回值
struct return_object {
    struct promise_type {
        int value;
        promise_type() : value(0) {}

        return_object get_return_object() {
            return return_object{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }
        void return_value(int v) { value = v; }
    };

    std::coroutine_handle<promise_type> handle;
    explicit return_object(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~return_object() { if (handle) handle.destroy(); }
    int get() { return handle.promise().value; }
};

return_object compute() {
    co_return 42;
}
```

### 4.3 std::coroutine_handle

`std::coroutine_handle` 是 C++20 协程的核心类型，用于控制协程的生命周期。

```cpp
#include <coroutine>
#include <iostream>

// 基本用法
void basic_usage() {
    std::coroutine_handle<> h = std::coroutine_handle<>::from_address(nullptr);

    if (h) {
        h.resume();  // 恢复协程执行
        h.destroy();  // 销毁协程
    }
}

// promise_type 自定义
struct Task {
    struct promise_type {
        Task get_return_object() {
            return Task{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_void() {}
        void unhandled_exception() { std::terminate(); }
    };

    std::coroutine_handle<promise_type> handle;
    explicit Task(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~Task() { if (handle) handle.destroy(); }

    bool resume() {
        if (!handle.done()) {
            handle.resume();
            return true;
        }
        return false;
    }
};

Task my_task() {
    std::cout << "Task running" << std::endl;
    co_return;
}

int main() {
    Task t = my_task();
    t.resume();
    return 0;
}
```

## 5. 协程的使用场景

### 5.1 异步 I/O

协程是处理异步 I/O 的理想选择，可以在等待 I/O 时让出 CPU，提高并发性能。

```cpp
// 异步 I/O 协程示例
struct async_file {
    std::coroutine_handle<> resume_handle;

    bool await_ready() { return false; }

    void await_suspend(std::coroutine_handle<> h) {
        resume_handle = h;
        // 发起异步读取操作
        // 完成时调用 resume_handle.resume()
    }

    std::string await_resume() {
        return read_result;
    }
};

async_file read_file_async(const char* path) {
    async_file file;
    // 异步读取文件
    co_return file;
}

task process_files() {
    // 并发读取多个文件
    auto file1 = read_file_async("file1.txt");
    auto file2 = read_file_async("file2.txt");
    auto file3 = read_file_async("file3.txt");

    std::string content1 = co_await file1;
    std::string content2 = co_await file2;
    std::string content3 = co_await file3;

    co_return process(content1, content2, content3);
}
```

### 5.2 协程池

协程池可以复用协程，避免频繁创建和销毁协程的开销。

```cpp
// 协程池实现
class CoroutinePool {
    std::vector<std::coroutine_handle<>> pool;
    std::queue<std::coroutine_handle<>> waiting;
    size_t max_size;

public:
    explicit CoroutinePool(size_t size) : max_size(size) {
        // 预创建协程
        for (size_t i = 0; i < size; ++i) {
            pool.push_back(create_idle_coroutine());
        }
    }

    template<typename F>
    auto submit(F&& func) -> decltype(func()) {
        auto task = create_task_coroutine(std::forward<F>(func));

        if (pool.empty()) {
            // 没有空闲协程，加入等待队列
            waiting.push(std::coroutine_handle<>::from_promise(task.handle.promise()));
        }

        return task;
    }

    void recycle(std::coroutine_handle<> h) {
        if (!waiting.empty()) {
            auto next = waiting.front();
            waiting.pop();
            next.resume();
        } else {
            pool.push_back(h);
        }
    }
};
```

### 5.3 状态机

协程天然适合实现状态机，每个 `co_await` 都可以是状态转换点。

```cpp
// 协程实现状态机
enum class State { IDLE, CONNECTING, CONNECTED, DISCONNECTED };

task connection_manager() {
    State state = State::IDLE;

    while (true) {
        switch (state) {
        case State::IDLE:
            std::cout << "Idle, waiting for connection request" << std::endl;
            co_await wait_for_connection_request();
            state = State::CONNECTING;
            break;

        case State::CONNECTING:
            std::cout << "Connecting..." << std::endl;
            co_await establish_connection();
            state = State::CONNECTED;
            break;

        case State::CONNECTED:
            std::cout << "Connected, waiting for data or disconnect" << std::endl;
            co_await wait_for_event();
            state = State::DISCONNECTED;
            break;

        case State::DISCONNECTED:
            std::cout << "Disconnected, cleaning up" << std::endl;
            co_await cleanup();
            state = State::IDLE;
            break;
        }
    }
}
```

## 参考资料

- C++20 Standard Draft (N4861)
- boost.coroutine2 Documentation
- Go Language Specification
- "Understanding the Linux Kernel" - Coroutines and Cooperative Multitasking
