# Libev 基础入门

> https://github.com/Sphinxes0o0/notes/issues/62

libev 是一个 C 语言编写的高性能事件循环库，采用 Reactor 模式，目标是"足够小、足够快"。
它把 select/poll/epoll/kqueue 等后端细节隐藏起来，向上层提供统一的 watcher/回调 API，用几行代码就能做出高并发、低延迟的网络服务或实时系统。

## 技术原理
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

### 2. 时间管理
定时器用四叉堆实现，父节点索引 (x-3-1)/4+3，缓存友好，插入/删除 O(log n)。
libev 保证"下一次 epoll_wait 的超时 ≤ 最近一个定时器剩余时间"，因此定时误差 <1 ms，不会漏事件。

#### 定时器示例
```c
// 创建定时器
struct ev_timer timer;
ev_timer_init(&timer, timer_cb, 2.0, 1.0); // 2秒后触发，每1秒重复
// 启动定时器
ev_timer_start(loop, &timer);
```

### 3. 后端自适应
- Linux 默认 epoll，可强制 EVBACKEND_SELECT
- BSD 用 kqueue
- Solaris 用 port
- 单例/多例两种编译模式任选

#### 后端配置示例
```c
// 强制使用 select 后端
struct ev_loop *loop = ev_loop_new(EVBACKEND_SELECT);
```

### 4. 优先级调度
每个 watcher 可设置 [-2,2] 优先级；同优先级按 FIFO 执行。
prepare/idle/check 三类内部 watcher 可用来插入"每次循环前后"的钩子。

## 核心机制深度解析
### 1. 事件处理流水线
1. **事件收集**：通过`ev_feed_event()`注入事件
2. **事件排队**：加入`loop->pending`队列
3. **事件分发**：根据优先级排序执行回调
4. **状态更新**：维护事件活跃状态

### 2. prepare/idle/check机制
```c
// 典型应用场景:
// prepare: 在每次循环前更新UI状态
// check:  在每次循环后进行日志统计
// idle:   在无事件时执行低优先级任务

// 示例：
struct ev_prepare prepare_w;
ev_prepare_init(&prepare_w, prepare_cb);
ev_prepare_start(loop, &prepare_w);
```

### 3. 线程安全模型
- 默认非线程安全
- 跨线程事件注入：使用`ev_async_send()`
- 多线程最佳实践：
  1. 每个线程独立事件循环
  2. 使用管道进行线程通信
  3. 避免共享watcher对象

### 4. 嵌套事件循环
```c
// 支持三种嵌套模式:
// 1. EV_EMBED_ONE: 嵌套单次
// 2. EV_EMBED_RECURSE: 递归嵌套
// 3. EV_EMBED_DETACH: 分离嵌套

// 示例：
struct ev_embed embed_w;
ev_embed_init(&embed_w, sub_loop);
ev_embed_start(main_loop, &embed_w);
```

## 高级特性
### 1. 信号处理扩展
```c
// 支持信号屏蔽:
sigset_t mask;
sigemptyset(&mask);
sigaddset(&mask, SIGINT);
ev_signal_set_mask(&mask);
```

### 2. 子进程监控
```c
// 支持四种监控模式:
// WFLAG_EXITED   - 进程正常退出
// WFLAG_SIGNALED - 被信号终止
// WFLAG_STOPPED  - 被暂停
// WFLAG_CONTINUED- 继续运行

// 示例：
struct ev_child child_w;
ev_child_init(&child_w, child_cb, pid, 0);
ev_child_start(loop, &child_w);
```

### 3. 性能调优参数
```c
// 可配置参数:
loop->io_blocktime = 10;  // IO阻塞时间上限
loop->timeout_blocktime = 5; // 超时阻塞时间
loop->backend_mintime = 1; // 后端最小等待时间
```

## 与其他库对比
| 特性          | libev      | libevent   | Boost.Asio |
|---------------|------------|------------|------------|
| 底层实现      | C          | C          | C++        |
| 跨平台支持    | 有限       | 完善       | 完善       |
| 线程安全      | 否         | 部分       | 是         |
| 性能          | 极致       | 良好       | 中等       |
| 功能丰富度    | 基础       | 完整       | 非常完整   |
| 内存占用      | 极低       | 低         | 高         |
| 活跃维护      | 偶尔       | 活跃       | 活跃       |
## 核心数据结构
### ev_loop 核心结构体
包含事件循环所有状态信息：
- `backend`：当前使用的后端类型
- `time`：当前时间戳
- `anfds`：文件描述符事件管理
- `timers`：定时器队列
- `pending`：待处理事件队列

### 事件类型
libev 支持以下事件类型：

#### 1. I/O 事件
```c
// 文件描述符事件（可读/可写）
ev_io
```

##### 示例：监听socket
```c
struct ev_io io;
int sock = socket(AF_INET, SOCK_STREAM, 0);
ev_io_init(&io, read_cb, sock, EV_READ);
ev_io_start(loop, &io);
```

#### 2. 文件监控
```c
// Linux inotify 接口
ev_stat
```

#### 3. 信号处理
```c
// 信号事件
ev_signal
```

##### 示例：处理SIGINT
```c
struct ev_signal signal;
ev_signal_init(&signal, signal_cb, SIGINT);
ev_signal_start(loop, &signal);
```

#### 4. 定时事件
```c
// 相对定时器
ev_timer

// 绝对定时器
ev_periodic
```

#### 5. 进程监控
```c
// 子进程状态变化
ev_child
```

#### 6. 其他特殊事件
```c
ev_fork        // fork事件
ev_cleanup     // event loop退出触发事件
ev_idle        // event loop空闲触发事件
ev_embed       // 嵌入另一个后台循环
ev_prepare     // event loop之前事件
ev_check       // event loop之后事件
ev_async       // 线程间异步事件
```

## 源码结构
### 事件管理机制
- (loop)->anfds ：维护所有fd事件
- (loop)->timers ：维护所有的定时器
- (loop)->periodics：周期性事件
- (loop)->prepares：loop启动前执行的事件

### 面向对象实现
采用宏定义实现C语言继承：
```c
// 基类watcher定义
#define EV_WATCHER(type) \
  int active; \
  int pending; \
  void (*callback)(struct ev_loop *, void *, int)

// 子类扩展
typedef struct ev_io {
  EV_WATCHER(ev_io);
  int fd;
  int events;
} ev_io;
```

## 典型应用场景
1. 高性能网络服务器
2. 实时系统事件处理
3. 多路复用I/O管理
4. 定时任务调度

## 性能优化建议
1. 优先使用系统默认后端（epoll/kqueue）
2. 合理设置定时器精度
3. 避免在回调中执行耗时操作
4. 使用优先级机制优化关键路径