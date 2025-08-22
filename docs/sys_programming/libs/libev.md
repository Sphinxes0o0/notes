# Libev 基础入门

> https://github.com/Sphinxes0o0/notes/issues/62

libev 是一个 C 语言编写的高性能事件循环库，采用 Reactor 模式，目标是"足够小、足够快"。
它把 select/poll/epoll/kqueue 等后端细节隐藏起来，向上层提供统一的 watcher/回调 API，用几行代码就能做出高并发、低延迟的网络服务或实时系统。

---

## 设计理念与适用场景

libev 旨在提供一个轻量级、高性能的事件驱动框架，适用于对性能和资源占用敏感的场景。其设计理念包括：

- **小巧精干**：核心库尽量保持精简，减少不必要的功能和依赖。
- **高性能**：通过高效的 I/O 多路复用和定时器机制，提供低延迟和高并发的事件处理能力。
- **灵活可扩展**：支持自定义 watcher 和后端，满足特定应用场景的需求。

适用场景包括：

- 高性能网络服务器
- 实时数据处理
- 低延迟高并发的 I/O 密集型应用

---

## 安装与集成

### 1. 安装
```sh
# Ubuntu/Debian
sudo apt-get install libev-dev

# macOS (Homebrew)
brew install libev

# 源码编译
wget http://dist.schmorp.de/libev/Attic/libev-4.33.tar.gz
tar zxvf libev-4.33.tar.gz
cd libev-4.33
./configure && make && sudo make install
```

### 2. 集成到项目
- 头文件：`#include <ev.h>`
- 链接库：`-lev`

---

## 快速入门示例

```c
#include <ev.h>
#include <stdio.h>

static void timer_cb(EV_P_ ev_timer *w, int revents) {
    puts("timeout!");
    ev_break(EV_A_ EVBREAK_ALL);
}

int main(void) {
    struct ev_loop *loop = EV_DEFAULT;
    ev_timer timeout_watcher;
    ev_timer_init(&timeout_watcher, timer_cb, 2.0, 0.);
    ev_timer_start(loop, &timeout_watcher);
    ev_run(loop, 0);
    return 0;
}
```
- 2 秒后打印 "timeout!" 并退出事件循环。

---

## 事件类型与回调签名

| 类型         | 结构体         | 典型用途         | 回调签名                                      |
|--------------|----------------|------------------|-----------------------------------------------|
| I/O          | ev_io          | fd可读/可写      | void cb(struct ev_loop *, ev_io *, int)       |
| 定时器       | ev_timer       | 相对定时         | void cb(struct ev_loop *, ev_timer *, int)    |
| 周期定时     | ev_periodic    | 绝对/周期定时    | void cb(struct ev_loop *, ev_periodic *, int) |
| 信号         | ev_signal      | 信号处理         | void cb(struct ev_loop *, ev_signal *, int)   |
| 子进程       | ev_child       | 进程监控         | void cb(struct ev_loop *, ev_child *, int)    |
| 文件监控     | ev_stat        | 文件变化         | void cb(struct ev_loop *, ev_stat *, int)     |
| 线程异步     | ev_async       | 跨线程通知       | void cb(struct ev_loop *, ev_async *, int)    |
| 空闲         | ev_idle        | 空闲时回调       | void cb(struct ev_loop *, ev_idle *, int)     |
| 循环前/后    | ev_prepare/check| 循环前/后钩子   | void cb(struct ev_loop *, ev_prepare *, int)  |

- `revents` 参数指示事件类型（如 EV_READ、EV_WRITE 等）。

---

## 核心原理与机制
### 1. 事件循环（Event Loop）
ev_run() → 计算下一次最早超时 → 多路复用等待（epoll/kqueue…）→ 将就绪 fd 或超时事件推入 pending 队列 → 按优先级顺序执行回调 → 循环继续。

#### 循环状态机
```c
// 状态机流转
EV_LOOP (初始化) → EV_RUN (运行) → EV_BREAK (退出)
// 支持两种退出模式:
// EVBREAK_ONE: 退出单个循环迭代
// EVBREAK_ALL: 彻底退出事件循环
```

#### 执行流程详解
1. 初始化事件循环：`struct ev_loop *loop = EV_DEFAULT_UC_;
2. 注册 watcher：绑定事件类型和回调函数
3. 进入循环：`ev_run(loop, 0);`
4. 事件处理：根据事件类型执行对应回调

### 2. 时间管理
定时器用四叉堆实现，父节点索引 (x-3-1)/4+3，缓存友好，插入/删除 O(log n)。
libev 保证"下一次 epoll_wait 的超时 ≤ 最近一个定时器剩余时间"，因此定时误差 <1 ms，不会漏事件。

#### 四叉堆特性
- 子节点索引：4*i+3, 4*i+4, 4*i+5, 4*i+6
- 局部性优化：相邻节点在内存中连续存储
- 时间复杂度：
  - 插入 O(log₄n)
  - 删除 O(log₄n)
  - 查找 O(1)

### 3. 后端比较
| 特性          | epoll      | kqueue     | select     |
|---------------|------------|------------|------------|
| 并发量        | 10K+       | 10K+       | <1K        |
| 性能          | O(1)       | O(1)       | O(n)       |
| 内存占用      | 中等       | 高         | 低         |
| 功能丰富度    | 高         | 高         | 低         |
| 可移植性      | Linux      | BSD        | 全平台     |

### 4. 优先级调度
#### 优先级传播机制
```c
// 优先级继承规则:
// 1. 新事件默认优先级0
// 2. 高优先级事件可抢占低优先级回调
// 3. 同优先级FIFO执行
// 4. prepare/check事件优先级自动设为-2
```

---

## 技术原理细节
### 事件循环流程
1. **初始化**：设置循环状态，初始化时间戳，创建后端句柄。
2. **注册事件**：将 watcher 加入到对应的事件队列（如 I/O 队列、定时器队列）。
3. **进入循环**：调用 `ev_run()` 进入事件循环。
4. **事件等待**：根据最早超时或就绪事件，调用 epoll/kqueue 等后端接口等待事件。
5. **事件分发**：将就绪的事件从 pending 队列中取出，调用对应的回调函数处理事件。
6. **状态更新**：更新事件和循环的状态，如时间戳、事件活跃状态等。
7. **循环结束**：根据退出条件，决定是否退出事件循环。

### Watcher 优先级与调度
- 每个 watcher 默认优先级为 0，范围为 [-2, 2]。
- 高优先级 watcher 可抢占低优先级 watcher 的执行。
- 同一优先级的 watcher 按照 FIFO 顺序执行。
- `prepare` 和 `check` 类型的 watcher 优先级自动设为 -2，优先级最低。

### 后端自适应与配置
- libev 会根据平台和编译选项自动选择最优的后端实现，如 epoll、kqueue 或 select。
- 用户也可以手动指定后端，如下例强制使用 select 后端：
```c
struct ev_loop *loop = ev_loop_new(EVBACKEND_SELECT);
```

---

## 源码结构分析

### 1. 核心数据结构

#### `struct ev_loop`

```c
struct ev_loop {
    unsigned int backend_fd;  // 后端 fd (epoll/kqueue)
    unsigned int flags;       // 循环标志
    ev_tstamp     now;         // 当前时间
    // ... 其他成员 ...
};
```

- 包含事件循环的所有状态信息，如后端 fd、时间戳、watcher 队列等。

#### `struct ev_watcher`

```c
typedef struct ev_watcher {
    EV_WATCHER_LIST_FIELDS  // 链表字段
    void *data;             // 用户数据
    ev_watcher_cb cb;       // 回调函数
    int active;             // 是否 active
    int pending;            // 是否 pending
    // ... 其他成员 ...
} ev_watcher;
```

- 所有 watcher 类型的基类，包含回调函数、用户数据、状态标志等。

### 2. 后端实现

- libev 通过条件编译选择最优后端实现。
- 常见后端：epoll (Linux)、kqueue (BSD)、select (通用)。
- 后端 API 封装在 `ev_epoll.c`、`ev_kqueue.c` 等文件中。

### 3. 源码目录结构

```
libev/
├── ev.c          # 核心事件循环
├── ev_epoll.c    # epoll 后端
├── ev_kqueue.c   # kqueue 后端
├── ev_select.c   # select 后端
├── ev_timer.c    # 定时器 watcher
├── ev_io.c       # I/O watcher
├── ev_signal.c   # 信号 watcher
├── ...           # 其他 watcher
└── configure.ac  # 编译配置
```

---

## 内部数据结构与算法

### 1. 四叉堆（Timer Wheel）

- libev 使用四叉堆实现定时器队列，父节点索引 `(x-3-1)/4+3`。
- 优点：缓存友好，插入/删除 O(log₄n)。

### 2. Pending 队列

- 用于存放就绪事件，按优先级排序。
- 事件循环从 pending 队列中取出事件并执行回调。

### 3. I/O 多路复用

- 使用 epoll/kqueue/select 等系统调用监听 fd 就绪状态。
- 就绪 fd 对应的事件被推入 pending 队列。

---

## 高级用法

### 1. Embed Watcher

- 允许在一个事件循环中嵌入另一个事件循环。
- 典型应用：模块化、插件化。

```c
struct ev_embed embed_w;
ev_embed_init(&embed_w, sub_loop);
ev_embed_start(main_loop, &embed_w);
```

### 2. Fork Watcher

- 用于在 fork() 后重新初始化事件循环。
- 保证子进程事件循环正常工作。

```c
struct ev_fork fork_w;
ev_fork_init(&fork_w, fork_cb);
ev_fork_start(loop, &fork_w);
```

### 3. Async Watcher

- 用于跨线程事件通知。
- 线程 A 调用 `ev_async_send()`，线程 B 的 async watcher 收到通知。

```c
ev_async async_w;
ev_async_init(&async_w, async_cb);
ev_async_start(loop, &async_w);

// 线程 A
ev_async_send(async_w.loop, &async_w);
```

---

## 扩展与定制

### 1. 自定义 Watcher

- 可通过 `ev_watcher_init()` 创建自定义 watcher 类型。
- 需要手动管理 watcher 的状态和事件。

### 2. 自定义后端

- 可实现自定义后端，替换 libev 默认的 epoll/kqueue/select。
- 需要实现 `ev_io_poll()`、`ev_timer_poll()` 等接口。

---

## Benchmark 与性能测试

- libev 官方提供 benchmark 工具，可测试不同场景下的性能。
- 常见指标：事件吞吐量、延迟、CPU 占用。
- 可通过调整参数优化性能，如调整定时器精度、调整后端策略等。

---

## 与其他库对比

| 特性          | libev      | libevent   | libuv       |
|---------------|------------|------------|-------------|
| 底层实现      | C          | C          | C           |
| 跨平台支持    | 有限       | 完善       | 完善        |
| 线程安全      | 否         | 部分       | 是          |
| 性能          | 极致       | 良好       | 良好        |
| 功能丰富度    | 基础       | 完整       | 非常完整    |
| 内存占用      | 极低       | 低         | 中等        |
| 活跃维护      | 偶尔       | 活跃       | 活跃        |
| 学习曲线      | 简单       | 中等       | 复杂        |

---

## 常见陷阱与调试建议

### 1. 回调未触发？
- 检查 watcher 是否已正确 start。
- 检查 fd 是否处于非阻塞模式（I/O watcher）。
- 检查事件循环是否已启动（`ev_run`）。

### 2. 如何调试事件循环？
- 可通过 `EV_VERIFY=3` 环境变量启用内部一致性检查。
- 使用 `ev_set_allocator` 自定义内存分配，便于内存调试。
- watcher 结构体的 `active` 字段可判断是否已注册。

### 3. 多线程场景
- 每个线程独立 loop，避免跨线程操作同一 watcher。
- 跨线程事件注入用 `ev_async`。

### 4. 性能调优
- watcher 数量大时，优先用 epoll/kqueue 后端。
- 定时器数量多时，合理设置精度，避免过多短周期定时器。

---

## 典型应用场景
1. 高性能网络服务器
2. 实时系统事件处理
3. 多路复用I/O管理
4. 定时任务调度

---

## 性能优化建议
- 针对特定场景调整 libev 参数，如定时器精度、后端策略等。
- 使用高效的 I/O 多路复用后端，如 epoll 或 kqueue。
- 减少不必要的事件触发和回调，优化事件处理逻辑。

---

## I/O Watcher 详解

### 1. I/O 事件类型

- `EV_READ`：文件描述符可读。
- `EV_WRITE`：文件描述符可写。

### 2. I/O 回调函数

```c
void io_cb(struct ev_loop *loop, ev_io *w, int revents) {
    if (revents & EV_READ) {
        // 处理读事件
    }
    if (revents & EV_WRITE) {
        // 处理写事件
    }
}
```

### 3. 缓冲区管理

- libev 不负责缓冲区管理，需要用户自行维护。
- 推荐使用循环缓冲区或动态缓冲区，避免内存拷贝。

### 4. 示例：TCP Echo Server

```c
#include <ev.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define PORT 8080
#define BUFFER_SIZE 1024

struct client_data {
    int fd;
    ev_io io_watcher;
    char buffer[BUFFER_SIZE];
    int buffer_len;
};

void read_cb(struct ev_loop *loop, ev_io *watcher, int revents) {
    struct client_data *client = (struct client_data*) watcher->data;
    int fd = client->fd;
    ssize_t bytes_read;

    bytes_read = recv(fd, client->buffer + client->buffer_len, BUFFER_SIZE - client->buffer_len, 0);
    if (bytes_read < 0) {
        perror("recv");
        goto error;
    }

    if (bytes_read == 0) {
        printf("Client disconnected\n");
        goto error;
    }

    client->buffer_len += bytes_read;
    printf("Received %zd bytes from client %d\n", bytes_read, fd);

    // Echo back the data
    send(fd, client->buffer, client->buffer_len, 0);
    client->buffer_len = 0; // Reset buffer

    return;

error:
    ev_io_stop(loop, watcher);
    close(fd);
    free(client);
}

void accept_cb(struct ev_loop *loop, ev_io *watcher, int revents) {
    int server_fd = watcher->fd;
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    int client_fd;

    client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_len);
    if (client_fd < 0) {
        perror("accept");
        return;
    }

    printf("Accepted new connection %d\n", client_fd);

    // Set non-blocking
    int flags = fcntl(client_fd, F_GETFL, 0);
    fcntl(client_fd, F_SETFL, flags | O_NONBLOCK);

    struct client_data *client = malloc(sizeof(struct client_data));
    if (!client) {
        perror("malloc");
        close(client_fd);
        return;
    }
    client->fd = client_fd;
    client->buffer_len = 0;

    ev_io_init(&client->io_watcher, read_cb, client_fd, EV_READ);
    client->io_watcher.data = client;
    ev_io_start(loop, &client->io_watcher);
}

int main() {
    struct ev_loop *loop = EV_DEFAULT;
    int server_fd;
    struct sockaddr_in server_addr;

    // Create socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return 1;
    }

    // Set non-blocking
    int flags = fcntl(server_fd, F_GETFL, 0);
    fcntl(server_fd, F_SETFL, flags | O_NONBLOCK);

    // Bind
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind");
        close(server_fd);
        return 1;
    }

    // Listen
    if (listen(server_fd, 10) < 0) {
        perror("listen");
        close(server_fd);
        return 1;
    }

    printf("Listening on port %d\n", PORT);

    ev_io accept_watcher;
    ev_io_init(&accept_watcher, accept_cb, server_fd, EV_READ);
    ev_io_start(loop, &accept_watcher);

    ev_run(loop, 0);

    close(server_fd);
    return 0;
}
```

## 定时器 Watcher 详解

### 1. 定时器精度控制

- libev 的定时器精度受限于事件循环的调度粒度。
- 可以通过调整 `loop->backend_mintime` 属性来控制定时器精度。

### 2. 动态调整定时器

- 可以使用 `ev_timer_again()` 函数动态调整定时器的超时时间。

### 3. 示例：动态定时器

```c
#include <ev.h>
#include <stdio.h>

struct timer_data {
    ev_timer timer_watcher;
    double timeout;
};

void timer_cb(struct ev_loop *loop, ev_timer *watcher, int revents) {
    struct timer_data *data = (struct timer_data*) watcher->data;
    printf("Timer fired with timeout %f\n", data->timeout);

    // Change the timeout for the next iteration
    data->timeout += 1.0;
    ev_timer_again(loop, watcher);
}

int main() {
    struct ev_loop *loop = EV_DEFAULT;
    struct timer_data *data = malloc(sizeof(struct timer_data));
    data->timeout = 2.0;

    ev_timer_init(&data->timer_watcher, timer_cb, data->timeout, 0.0);
    data->timer_watcher.data = data;
    ev_timer_start(loop, &data->timer_watcher);

    ev_run(loop, 0);

    free(data);
    return 0;
}
```

## 信号处理 Watcher 详解

### 1. 信号屏蔽

- 在多线程环境下，需要使用 `sigprocmask()` 函数屏蔽信号，避免信号被多个线程同时处理。

### 2. 信号传递

- 可以使用 `pthread_sigmask()` 函数将信号传递给指定的线程。

### 3. 示例：信号处理

```c
#include <ev.h>
#include <stdio.h>
#include <signal.h>
#include <pthread.h>

void signal_cb(struct ev_loop *loop, ev_signal *watcher, int revents) {
    printf("Signal %d received\n", watcher->signum);
    ev_break(loop, EVBREAK_ALL);
}

int main() {
    struct ev_loop *loop = EV_DEFAULT;
    ev_signal signal_watcher;

    // Initialize and start a signal watcher for SIGINT
    ev_signal_init(&signal_watcher, signal_cb, SIGINT);
    ev_signal_start(loop, &signal_watcher);

    printf("Waiting for SIGINT...\n");
    ev_run(loop, 0);

    printf("Exiting...\n");
    return 0;
}
```

## 子进程 Watcher 详解

### 1. 使用场景

- 进程池：使用多个子进程并发处理任务。
- 任务队列：将任务放入队列，由子进程异步处理。

### 2. 示例：子进程监控

```c
#include <ev.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

void child_cb(struct ev_loop *loop, ev_child *watcher, int revents) {
    printf("Child process %d exited with status %d\n", watcher->rpid, watcher->rstatus);
    ev_break(loop, EVBREAK_ALL);
}

int main() {
    struct ev_loop *loop = EV_DEFAULT;
    ev_child child_watcher;
    pid_t pid;

    pid = fork();
    if (pid == 0) {
        // Child process
        printf("Child process started\n");
        sleep(2);
        printf("Child process exiting\n");
        exit(0);
    } else if (pid > 0) {
        // Parent process
        ev_child_init(&child_watcher, child_cb, pid, 0);
        ev_child_start(loop, &child_watcher);

        printf("Parent process waiting for child to exit\n");
        ev_run(loop, 0);

        printf("Parent process exiting\n");
    } else {
        perror("fork");
        return 1;
    }

    return 0;
}
```

## 多线程环境下的 Libev

### 1. 线程安全

- libev 本身不是线程安全的，需要在多线程环境下进行特殊处理。

### 2. 数据同步

- 多个线程不能同时访问同一个 `ev_loop` 实例。
- 可以使用互斥锁或条件变量进行数据同步。

### 3. 示例：多线程 Libev

```c
#include <ev.h>
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

struct thread_data {
    struct ev_loop *loop;
    int id;
};

void *thread_cb(void *arg) {
    struct thread_data *data = (struct thread_data*) arg;
    struct ev_loop *loop = data->loop;
    int id = data->id;

    printf("Thread %d started\n", id);

    ev_run(loop, 0);

    printf("Thread %d exiting\n", id);
    return NULL;
}

int main() {
    pthread_t thread1, thread2;
    struct thread_data data1, data2;

    // Create event loops for each thread
    data1.loop = ev_loop_new(0);
    data1.id = 1;
    data2.loop = ev_loop_new(0);
    data2.id = 2;

    // Create threads
    pthread_create(&thread1, NULL, thread_cb, &data1);
    pthread_create(&thread2, NULL, thread_cb, &data2);

    // Wait for threads to finish
    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    // Free event loops
    ev_loop_destroy(data1.loop);
    ev_loop_destroy(data2.loop);

    return 0;
}
```

## 常见问题与解决方案

### 1. 内存泄漏

- 检查是否正确释放了 watcher 和回调函数中分配的内存。
- 使用内存分析工具检测内存泄漏。

### 2. 死锁

- 避免在回调函数中调用阻塞操作。
- 使用非阻塞 I/O 和定时器来避免死锁。

### 3. 事件丢失

- 检查文件描述符是否设置为非阻塞模式。
- 检查事件循环是否正常运行。

---

## 深入分析

### 1. 事件循环机制

- **事件收集**：libev 通过 `ev_feed_event()` 函数将外部事件注入到事件循环中。
- **事件分发**：libev 根据事件类型将事件分发到不同的 watcher 队列中。
- **事件处理**：libev 从 watcher 队列中取出事件，调用对应的回调函数处理事件。

### 2. I/O 多路复用机制

- **epoll**：Linux 平台下的高性能 I/O 多路复用机制，支持边缘触发和水平触发。
- **kqueue**：BSD 平台下的高性能 I/O 多路复用机制，支持事件过滤和事件通知。
- **select**：通用 I/O 多路复用机制，支持跨平台，但性能较低。

### 3. 定时器机制

- **四叉堆**：libev 使用四叉堆实现定时器队列，父节点索引 `(x-3-1)/4+3`。
- **精度控制**：libev 允许用户通过调整 `loop->backend_mintime` 属性来控制定时器精度。

### 4. 信号处理机制

- **信号屏蔽**：libev 允许用户使用 `sigprocmask()` 函数屏蔽信号，避免信号被多个线程同时处理。
- **信号传递**：libev 允许用户使用 `pthread_sigmask()` 函数将信号传递给指定的线程。

### 5. 多线程机制

- **线程安全**：libev 本身不是线程安全的，需要在多线程环境下进行特殊处理。
- **数据同步**：libev 建议用户使用互斥锁或条件变量进行数据同步，避免多个线程同时访问同一个 `ev_loop` 实例。

## 实现分析

### 1. 事件循环实现

- `ev_run()` 函数是 libev 的核心函数，负责驱动整个事件循环。
- `ev_run()` 函数首先调用 `ev_backend_poll()` 函数等待事件，然后调用 `ev_invoke_pending()` 函数处理就绪事件。

### 2. I/O 多路复用实现

- `ev_epoll.c`、`ev_kqueue.c`、`ev_select.c` 文件分别实现了 epoll、kqueue、select 等 I/O 多路复用机制。
- 这些文件都实现了 `ev_io_poll()` 函数，负责监听文件描述符的就绪状态。

### 3. 定时器实现

- `ev_timer.c` 文件实现了定时器 watcher。
- `ev_timer_init()` 函数负责初始化定时器 watcher，`ev_timer_start()` 函数负责启动定时器 watcher。

### 4. 信号处理实现

- `ev_signal.c` 文件实现了信号 watcher。
- `ev_signal_init()` 函数负责初始化信号 watcher，`ev_signal_start()` 函数负责启动信号 watcher。

### 5. 多线程实现

- libev 本身没有提供多线程支持，需要在多线程环境下进行特殊处理。
- 可以使用 `pthread_create()` 函数创建线程，然后为每个线程创建一个独立的 `ev_loop` 实例。

## 性能测试和优化

### 1. Benchmark 工具

- libev 官方提供 benchmark 工具，可测试不同场景下的性能。
- 常见指标：事件吞吐量、延迟、CPU 占用。

### 2. 性能瓶颈分析

- 使用性能分析工具，如 gprof、perf 等，分析 libev 的性能瓶颈。
- 常见瓶颈：I/O 多路复用、定时器精度、内存分配等。

### 3. 性能优化方法

- 针对特定场景调整 libev 参数，如定时器精度、后端策略等。
- 使用高效的 I/O 多路复用后端，如 epoll 或 kqueue。
- 减少不必要的事件触发和回调，优化事件处理逻辑。
- 避免在回调函数中执行耗时操作，尽量使用异步操作。
- 使用内存池或对象池，减少内存分配和释放的开销。

---

## 参考资料

- [libev 官方文档](http://software.schmorp.de/pkg/libev.html)
- [libev 源码 GitHub 镜像](https://github.com/enki/libev)
- [libev vs libevent 性能对比](https://libev.schmorp.de/bench.html)
- [libev 中文教程](https://github.com/ithewei/libev-learn)