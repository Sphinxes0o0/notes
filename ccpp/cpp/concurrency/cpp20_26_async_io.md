---
title: C++20 协程与 C++26 网络 sender/receiver 异步 I/O
date: 2026-06-04 10:00:00
tags:
    - cpp
    - cpp20
    - cpp26
    - coroutine
    - sender
    - receiver
    - execution
    - async-io
---

# C++20 协程与 C++26 网络 sender/receiver 异步 I/O

## 1. 背景 (Background)

C++ 异步 I/O 编程经历三代演化:

| 时代 | 模型 | 代表 API | 痛点 |
|---|---|---|---|
| C++98/11 | 回调 + 状态机 | libuv, raw socket callbacks | "回调地狱" |
| C++20 | 协程 (coroutines) | `co_await` / `co_yield` / `co_return` | 缺少统一组合子, 异步 I/O 各家自定义 |
| C++26 | sender/receiver | `std::execution` (P2300) | 编译器支持仍演进中, 教学资源稀缺 |

**为什么需要 sender/receiver 替代部分协程场景**: C++20 协程 `co_await` 是**显式 lazy + pull-based**, 但**没有统一的 sender 链式组合 API** (`then` / `sequence` / `when_all` 在协程里只能通过 task wrapper 模拟)。`std::execution` 提供了**完整的类型化组合子**, 与 Rust Future 哲学同源 (都是 Eric Niebler 推动), 但走"算法 + 显式 scheduler + 多个独立实现"路线。

## 2. C++20 协程核心机制 (Mechanism)

### 2.1 三关键字

```cpp
// co_await: 挂起点
task<int> fetch() {
    auto data = co_await async_read(socket);  // 挂起直到 data 就绪
    co_return process(data);
}

// co_yield: 生成器
generator<int> fib() {
    int a = 0, b = 1;
    while (true) {
        co_yield a;
        auto next = a + b;
        a = b;
        b = next;
    }
}

// co_return: 协程结束
task<void> cleanup() {
    co_await flush();
    co_return;  // 隐式 void
}
```

### 2.2 编译器展开: 协程是状态机

`co_await async_read(socket)` 实际由编译器生成:

```cpp
class fetch_task {
public:
    struct promise_type {
        fetch_task get_return_object() { return {handle_type::from_promise(*this)}; }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_value(int v) { result_ = v; }
        // awaiter 挂起逻辑
    };
    handle_type coro_;
};
```

**关键点**: 协程 = heap 分配的状态机 + 自定义 promise_type. 编译时**不是** 8MB 栈, 是几十到几百字节堆 (取决于局部变量).

### 2.3 Awaiter 接口

`co_await expr` 实际是 `expr.operator co_await()` (若有) 或 `expr` 本身 (若实现 `await_ready`/`await_suspend`/`await_resume`).

```cpp
struct awaitable {
    bool await_ready() const noexcept { return false; }  // 是否立即 ready
    void await_suspend(std::coroutine_handle<> h) { /* 挂起时注册 h */ }
    int await_resume() { /* 恢复时返回值 */ }
};
```

**`await_suspend` 三种返回** (C++20):
- `void`: 简单挂起, 调度器自己处理
- `bool`: `false` = 立即恢复, `true` = 真的挂起
- `std::coroutine_handle<>`: **对称转移** — 把控制权直接转给另一个协程, 比 `void` + resume 更高效 (少一次调度)

## 3. C++20 协程实战: 异步 TCP echo server

```cpp
// 简化版, 教学用
#include <coroutine>
#include <iostream>
#include <vector>

struct task {
    struct promise_type {
        task get_return_object() { return {std::coroutine_handle<promise_type>::from_promise(*this)}; }
        std::suspend_never initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        void return_void() {}
        void unhandled_exception() { std::terminate(); }
    };
    std::coroutine_handle<promise_type> h;
    void operator()() { h.resume(); }
};

task async_echo(int client_fd) {
    char buf[1024];
    while (true) {
        ssize_t n = co_await async_read_some(client_fd, buf, sizeof(buf));
        if (n <= 0) break;
        co_await async_write_some(client_fd, buf, n);
    }
    close(client_fd);
}
```

**注**: 真实生产用 `boost::asio` / `cppcoro` 库, 因为**C++20 标准库没提供 I/O awaiters** (只有 `<coroutine>` 提供协程机制, I/O 协程化由库实现). 这正是 C++26 sender/receiver 想要**直接放进标准**的动机.

## 4. C++26 std::execution (P2300) 核心模型

### 4.1 三大原语

```cpp
namespace std::execution {

template<class Sigs>
concept sender = /* Sigs 是类型化 completion signature */;

template<class R>
concept receiver = requires(R r, Sigs... sigs) {
    { r.set_value(...) };     // 成功
    { r.set_error(...) };      // 失败
    { r.set_stopped() };       // 取消
};

template<class S, class R>
auto connect(S&& s, R r) -> operation_state<S, R>;

template<class Op>
void start(Op& op);
}
```

**核心思想**: `sender` 是**值 + 完成方式**的类型化描述, `receiver` 是**消费端** (3 个 `set_*` 方法), `operation_state` 是连接两者的**惰性状态机**, `start` 触发执行. **一切都是 pull-based + lazy** — 跟 Rust Future 同源.

### 4.2 三大算法

```cpp
// 1. then: 链式变换
auto s1 = schedule(sched);                  // sender<Sigs(int)>
auto s2 = then(s1, [](int x) { return x * 2; });  // sender<Sigs(int)>

// 2. sequence: 串行 (sender1 输出当 sender2 输入)
auto s3 = sequence(then(s1, ...), then(s2, ...));

// 3. when_all: 并行 (等所有 sender 完成, 收集结果)
auto s4 = when_all(s1, s2, s3);
```

**类型化 completion signature** 是 C++26 sender/receiver 区别于"协程 + 各自 awaiter"的关键 — **编译器**知道 `s2` 输出 `int`, 不用运行时类型擦除.

### 4.3 Scheduler 与 ExecutionContext

```cpp
// 调度器: 提供"在此处执行"的能力
auto sched = std::execution::get_default_scheduler();  // runtime 默认
auto h = std::execution::get_thread_pool().get_scheduler();  // 显式线程池
auto sched2 = std::execution::get_system_thread_pool();      // 系统线程池

// 任何 sender 必须能 "schedule" 才能启动
auto s = schedule(sched);  // → 一个 sender, 启动后调用 set_value()
```

**C++20 协程没暴露 scheduler 概念**, 调度逻辑藏在 awaiter 实现里. C++26 sender/receiver 把 scheduler **显式化** — 这是**最大架构变化**.

## 5. 端到端例子: HTTP client 5 阶段 sender/receiver pipeline

**目标**: 用 sender/receiver 组合 5 个阶段 (TCP connect → 写 request → 读 status → 读 headers → 读 body), 全部类型化.

```cpp
// 注: 这是 P2300 风格, 实际编译器支持可能在 GCC 14+/Clang 19+ 实验中
#include <execution>
#include <iostream>
#include <string>
#include <vector>

namespace ex = std::execution;

// 阶段 1: TCP connect
auto connect_sender(std::string host, uint16_t port) {
    return ex::just(host, port) 
         | ex::then([](auto h, auto p) { return open_tcp(h, p); });
}

// 阶段 2: 写 HTTP request
auto write_request(int fd, std::string req) {
    return ex::just(fd, req)
         | ex::then([](int fd, std::string req) {
               write(fd, req.data(), req.size());
               return fd;
           });
}

// 阶段 3+4+5: 读 status + headers + body (简化为一次 read)
auto read_response(int fd) {
    return ex::just(fd)
         | ex::then([](int fd) {
               std::string resp;
               char buf[4096];
               ssize_t n;
               while ((n = read(fd, buf, sizeof(buf))) > 0) {
                   resp.append(buf, n);
               }
               return resp;
           });
}

// 组合 5 阶段
auto http_get(std::string host, uint16_t port, std::string path) {
    return ex::when_all(
        connect_sender(host, port),
        ex::just(path)
    )
    | ex::then([](int fd, std::string path) {
        return write_request(fd, "GET " + path + " HTTP/1.1\r\nHost: " + ...);
    })
    | ex::then([](int fd) {
        return read_response(fd);
    });
}

// 启动
int main() {
    auto sched = ex::get_system_thread_pool();
    auto s = http_get("example.com", 80, "/");
    auto [result] = ex::sync_wait(std::move(s)).value();
    std::cout << "Response: " << result << "\n";
}
```

**关键点**:
- 每个 `| ex::then(...)` 链**类型化**: 编译器验证 `int → int`, `int, string → string` 等
- `when_all` 自动并行: TCP connect 期间可以并行做 DNS / TLS 握手 (本文简化)
- `sync_wait` 阻塞当前线程等结果, **适合 main / 测试**, 不适合 server

## 6. Cancellation 显式化

**C++20 协程**: 取消是隐式的 — `destroy()` 协程时析构 promise + 局部变量, 协作式取消靠 awaiter 自己实现.
**C++26 sender/receiver**: 取消是 `set_stopped()` 显式信号, scheduler 决定如何传播.

```cpp
// 链式 cancellation
auto s = schedule(sched)
       | ex::then([] { return long_running_op(); })
       | ex::let_value([](auto v) { return another_op(v); })
       | ex::upon_stopped([] { std::cerr << "cancelled!\n"; });

// 外部触发: stop_source / stop_token
std::stop_source src;
auto fut = ex::start_detached(std::move(s), src.get_token());
// ... 后来
src.request_stop();  // 显式取消
```

**优势**: server 关闭时, 取消信号**显式传播**到所有 in-flight sender, 资源立即释放. C++20 协程做不到这种结构化并发 (structured concurrency) 模式.

## 7. 编译器支持现状 (Reality, 2026-06)

| 编译器 | std::execution | C++20 coroutine | 备注 |
|---|---|---|---|
| GCC 14+ | 实验 (`-fexperimental`?) | 稳定 | libstdc++ 部分支持 |
| Clang 19+ | 实验 | 稳定 | libc++ 跟进慢 |
| MSVC 19.38+ | 部分 | 稳定 | 微软主推, 已落地 |
| **stdexec (NVIDIA)** | **完整实现** | N/A | Eric Niebler + Michał Dominiak 维护, **参考实现** |
| libunifex (Meta) | 完整 | N/A | Facebook 早期 fork, 现在合并到 stdexec |
| boost::asio | 集成中 | 集成 (`co_spawn`) | Chris Kohlhoff 主导 |

**现实建议**: **生产代码**继续用 `boost::asio` (coroutine 支持完整, 跨平台). **学习/实验**用 **stdexec** (`github.com/NVIDIA/stdexec`, header-only) — 编译过 `g++ -std=c++23 -I stdexec/include -pthread`. **生产用 C++26 std::execution** 等 2027-2028 编译器稳定.

## 8. 与 Rust Future 对比

| 维度 | C++26 `std::execution` | Rust `Future` |
|---|---|---|
| 模型 | pull-based lazy, sender chain | pull-based lazy, await chain |
| Completion | 类型化 `completion_signature<Sigs...>` | `Poll<Output>` (二态) |
| Scheduler | 显式 `scheduler` 对象 | 隐式 `tokio::spawn` (runtime 拥有) |
| Cancellation | 显式 `set_stopped` + `stop_token` | 隐式 `Drop` |
| Pipeline 组合 | `then` / `sequence` / `when_all` 算法 | `.await` 链 / `FuturesExt` |
| 内存模型 | 编译期可优化 inline | 编译期 state machine |
| 多 impl | stdexec / libunifex / asio unifex / 编译器 std | tokio / async-std / smol (ecosystem) |
| 现状 | 2026 实验 | 2018+ stable |

**同源** — Eric Niebler 在 C++ 社区和 Rust 社区都推动了 pull-based async, 两套系统哲学一致. **差异**: Rust 走"语言 trait + 单一生态", C++ 走"算法 + 显式 scheduler + 多 impl".

## 9. 实践选择决策树 (TL;DR)

```
需要异步 I/O?
├─ 是 → 需要低延迟高并发 (10K+ 连接)?
│   ├─ 是 → std::execution (C++26, 用 stdexec header) 或 boost::asio
│   └─ 否 → boost::asio 协程 (成熟稳定)
└─ 否 → 用 std::thread + std::future 够用

需要取消传播?
├─ 是 → std::execution (显式 stop_token) > C++20 协程
└─ 否 → C++20 协程也够

需要跨编译器跨平台 (今天)?
├─ 是 → boost::asio (稳定 10+ 年)
└─ 否 → 任意新方案
```

## 10. 总结 (Interpretation)

- **C++20 协程**: 提供 `co_await` 机制, I/O awaiter 需第三方库 (asio). 取消隐式. 适合"我懂协程, 想要代码像同步一样写"
- **C++26 sender/receiver**: 类型化 completion, 显式 scheduler, 显式 cancellation, 算法组合丰富. 适合"我要大规模结构化并发, 协程不够"
- **2026 现状**: 编译器支持实验性, 主流生产仍 `boost::asio`. 学习曲线**陡峭** (P2300 邮件列表从 2019 讨论到 2024, 概念多)
- **个人推荐**: 项目跨平台稳定优先 → `boost::asio`. 新项目愿意等 1-2 年 → 学 stdexec + 等 C++26 编译器

---

## 引用 (References)

1. **P2300R10 — `std::execution`** (Eric Niebler, Michał Dominiak), 2024-10. <https://wg21.link/p2300r10>
2. **P2762R2 — Sender/Receiver 取消信号**, 2024. <https://wg21.link/p2762r2>
3. **stdexec 仓库 (NVIDIA)**: <https://github.com/NVIDIA/stdexec> — C++26 sender/receiver 参考实现
4. **libunifex 仓库 (Meta)**: <https://github.com/facebookexperimental/libunifex> — 早期 Meta 实现, 合并到 stdexec
5. **boost::asio 协程文档**: <https://www.boost.org/doc/libs/develop/doc/html/boost_asio/reference/coroutine.html> — 实战首选
6. **Gor Nishanov — "C++ Coroutines: Under the Covers"** (CppCon 2016). <https://www.youtube.com/watch?v=8C8NnE1Dg4A> — 协程机制最清晰讲解
7. **Lewis Baker — "C++20 Coroutines: Asymmetric Transfer"** (2019). <https://lewissbaker.github.io/2020/05/11/understanding_symmetric_transfer> — 对称转移细节
8. **Eric Niebler — "Asynchronous I/O in C++"** (CppCon 2024 keynote). <https://www.youtube.com/watch?v=dcIqYWxHRkw> — sender/receiver 思想
9. **C++23 Standard Draft N4910** (协程章节). <https://wg21.link/n4910>
10. **Chris Kohlhoff — "Asio"** 文档 + 协程设计. <https://think-async.com/>
