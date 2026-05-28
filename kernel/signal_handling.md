---
title: Linux 信号机制
date: 2026-04-28
tags:
    - Linux
    - Signal
    - Process
    - IPC
---

# Linux 信号机制

信号是 Unix/Linux 系统中一种重要的进程间通信机制，用于通知进程发生了某种事件。本文深入分析 Linux 信号机制的实现原理、使用方法和最佳实践。

## 1. 信号概述

### 1.1 什么是信号

信号（Signal）是一种异步通信机制，用于通知进程发生了某种事件。当进程收到信号时，操作系统会中断进程的正常执行流程，转而调用信号处理函数。

```
进程执行流程：
┌─────────────────────────────────────────────────────┐
│  正常执行  ──→  收到信号  ──→  信号处理  ──→  恢复执行  │
└─────────────────────────────────────────────────────┘
```

### 1.2 信号的特点

- **异步性**：信号可以在任何时刻发送给进程，无需预先约定
- **简短性**：信号通常只携带很少的信息（信号编号）
- **即时性**：信号处理是立即发生的（除非被阻塞）
- **软件中断**：信号本质上是一种软件中断机制

### 1.3 常见信号列表

| 信号编号 | 信号名称 | 默认动作 | 说明 |
|---------|---------|---------|------|
| 1 | SIGHUP | 终止 | 终端连接断开 |
| 2 | SIGINT | 终止 | 键盘中断 (Ctrl+C) |
| 3 | SIGQUIT | 终止 + core | 键盘退出 (Ctrl+\) |
| 9 | SIGKILL | 终止 | 强制终止（不可捕获） |
| 15 | SIGTERM | 终止 | 优雅终止（可捕获） |
| 17 | SIGCHLD | 忽略 | 子进程终止 |
| 18 | SIGCONT | 继续 | 继续执行已停止的进程 |
| 19 | SIGSTOP | 停止 | 停止进程（不可捕获） |
| 20 | SIGTSTP | 停止 | 终端停止 (Ctrl+Z) |

## 2. 信号类型

### 2.1 标准信号（1-31）

标准信号也称为"不可靠信号"，因为它们不支持排队，如果多个相同信号在阻塞期间发生，信号只会交付一次。

```c
/*
 * 标准信号（POSIX 定义）
 * 编号 1-31，每个信号都有默认处理动作
 */

typedef enum {
    SIGHUP    = 1,    // 终端挂起
    SIGINT    = 2,    // 终端中断
    SIGQUIT   = 3,    // 终端退出
    SIGILL    = 4,    // 非法指令
    SIGTRAP   = 5,    // 跟踪/断点陷阱
    SIGABRT   = 6,    // abort() 发送
    SIGBUS    = 7,    // 总线错误
    SIGFPE    = 8,    // 浮点异常
    SIGKILL   = 9,    // 强制终止
    SIGUSR1   = 10,   // 用户定义信号1
    SIGSEGV   = 11,   // 段错误
    SIGUSR2   = 12,   // 用户定义信号2
    SIGPIPE   = 13,   // 管道破裂
    SIGALRM   = 14,   // alarm() 超时
    SIGTERM   = 15,   // 优雅终止
    SIGSTKFLT = 16,   // 栈错误
    SIGCHLD   = 17,   // 子进程状态改变
    SIGCONT   = 18,   // 继续执行
    SIGSTOP   = 19,   // 停止进程
    SIGTSTP   = 20,   // 终端停止
    SIGTTIN   = 21,   // 后台读控制终端
    SIGTTOU   = 22,   // 后台写控制终端
    SIGURG    = 23,   // 紧急数据到达
    SIGXCPU   = 24,   // CPU 时间限制
    SIGXFSZ   = 25,   // 文件大小限制
    SIGVTALRM = 26,   // 虚拟定时器
    SIGPROF   = 27,   // profile 定时器
    SIGWINCH  = 28,   // 窗口大小改变
    SIGIO     = 29,   // I/O 可用
    SIGPWR    = 30,   // 电源故障
    SIGSYS    = 31    // 非法系统调用
} signal_t;
```

### 2.2 实时信号（34-64）

实时信号是可靠信号，支持排队，可以区分多次发送。实时信号的编号越小优先级越高。

```c
/*
 * 实时信号（POSIX RT 扩展）
 * 编号 34-64，支持排队，不丢失
 */

#define SIGRTMIN  34
#define SIGRTMAX  64

/*
 * 实时信号的特点：
 * 1. 支持排队，不会丢失
 * 2. 多个相同信号可以累积
 * 3. 信号按发送顺序交付
 * 4. 附加信息可以通过 sigaction() 的 siginfo_t 传递
 */
```

### 2.3 信号处理行为

信号有三种处理方式：

```c
/*
 * 信号处理的三种方式
 */

typedef void (*sighandler_t)(int);

// 1. 捕获信号 - 自定义处理函数
sighandler_t signal(int signum, sighandler_t handler);

// 2. 忽略信号 - 设置为 SIG_IGN
signal(SIGINT, SIG_IGN);  // 忽略 Ctrl+C

// 3. 默认处理 - 设置为 SIG_DFL
signal(SIGINT, SIG_DFL);  // 使用默认处理
```

## 3. 信号处理函数

### 3.1 signal() 函数

`signal()` 是最基本的信号处理函数，但存在可移植性问题。

```c
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

/*
 * signal() 函数的局限性：
 * - 不同系统对 signal() 的语义定义不同
 * - 处理函数可能在信号处理后被重置为默认行为
 * - 不支持信号掩码、不会阻塞新信号
 */

/* 简单的信号处理函数 */
void sigint_handler(int signum)
{
    printf("收到信号 %d (SIGINT)\n", signum);
    /* 注意：这里不应使用 printf，应使用 async-signal-safe 函数 */
}

int main(void)
{
    /* 设置 SIGINT 处理函数 */
    if (signal(SIGINT, sigint_handler) == SIG_ERR) {
        perror("signal");
        exit(EXIT_FAILURE);
    }

    /* 无限循环 */
    while (1) {
        pause();  /* 等待信号 */
    }

    return 0;
}
```

### 3.2 sigaction() 函数

`sigaction()` 是更可靠、更可移植的信号处理函数。

```c
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/*
 * sigaction() 结构
 */
struct sigaction {
    void     (*sa_handler)(int);   // 信号处理函数
    void     (*sa_sigaction)(int, siginfo_t *, void *);  // 扩展处理函数
    sigset_t sa_mask;              // 处理中要阻塞的信号
    int      sa_flags;             // 标志位
    void     (*sa_restorer)(void); // 保留，不使用
};

/* 推荐的信号处理函数（使用 siginfo_t） */
void sigaction_handler(int signum, siginfo_t *info, void *context)
{
    /*
     * siginfo_t 包含丰富的信息：
     * - si_signo: 信号编号
     * - si_code: 信号来源
     * - si_pid: 发送信号的进程 ID
     * - si_uid: 发送信号的进程用户 ID
     * - si_addr: 故障地址（对于 SIGSEGV 等）
     * - si_value: 附加数据（对于实时信号）
     */
    printf("收到信号 %d，来自进程 %d (UID: %d)\n",
           info->si_signo, info->si_pid, info->si_uid);
}

int main(void)
{
    struct sigaction sa;

    /* 初始化 */
    sa.sa_handler = sigaction_handler;  /* 使用处理函数 */
    sigemptyset(&sa.sa_mask);            /* 不阻塞额外信号 */
    sa.sa_flags = 0;                     /* 默认行为 */

    /* 设置 SIGTERM 处理 */
    if (sigaction(SIGTERM, &sa, NULL) == -1) {
        perror("sigaction");
        exit(EXIT_FAILURE);
    }

    /* 持续运行 */
    while (1) {
        pause();
    }

    return 0;
}
```

### 3.3 可重入函数问题

信号处理函数必须使用**异步信号安全**（async-signal-safe）函数。

```c
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

/*
 * 危险操作：以下函数在信号处理函数中不可使用
 *
 * - printf(), fprintf() - 可能导致死锁或数据竞争
 * - malloc(), free() - 可能导致堆损坏
 * - 大多数 libc 函数
 *
 * 安全操作：使用 write() 而非 printf()
 */

/* 线程安全的方式记录日志 */
void safe_signal_handler(int signum)
{
    const char *msg = "信号处理中...\n";
    /*
     * write() 是异步信号安全的
     * STDERR_FILENO = 2
     */
    write(STDERR_FILENO, msg, strlen(msg));
}

/*
 * 使用 sigaction() 的 SA_SIGINFO 标志
 * 可以传递更多上下文信息
 */
void extended_handler(int signum, siginfo_t *info, void *context)
{
    char buf[256];
    int len;

    /*
     * 注意：即使使用 sigaction，也要避免调用非信号安全函数
     * 这里使用 write() 而不是 printf()
     */
    len = snprintf(buf, sizeof(buf),
                   "收到信号 %d，附加数据: %d\n",
                   signum, info->si_value.sival_int);

    if (len > 0) {
        write(STDOUT_FILENO, buf, len);
    }
}
```

## 4. 信号与进程

### 4.1 信号如何通知进程

```
信号传递流程：

  进程 A                           进程 B
    │                                │
    │  ── kill(pid, SIGTERM) ────→  │
    │                                │
    │           内核                  │
    │    ┌─────────────────┐        │
    │    │  目标进程 B 的   │        │
    │    │  信号队列/pending│        │
    │    └─────────────────┘        │
    │                                │
    ↓                                ↓
```

### 4.2 信号的默认处理

每个信号都有默认处理动作：

```c
/*
 * 默认处理动作（man 7 signal）
 */
typedef enum {
    SIG_DFL,  // 默认动作
    SIG_IGN   // 忽略信号
} sighandler_t;

/*
 * 各信号的默认动作：
 *
 * SIGTERM   → 终止进程
 * SIGKILL   → 终止进程（无法捕获或忽略）
 * SIGSTOP   → 停止进程（无法捕获或忽略）
 * SIGCHLD   → 忽略（子进程结束时通知）
 * SIGCONT   → 继续执行
 * 其他大多数 → 终止进程
 */
```

### 4.3 信号的捕获和忽略

```c
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/*
 * 捕获信号示例
 */
int g_shutdown = 0;

void shutdown_handler(int signum)
{
    g_shutdown = 1;
}

int main(void)
{
    struct sigaction sa;

    /* 设置优雅关闭处理 */
    sa.sa_handler = shutdown_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;  /* 不使用 SA_RESTART，否则可能中断某些系统调用 */

    if (sigaction(SIGTERM, &sa, NULL) == -1) {
        perror("sigaction");
        return 1;
    }

    /* 忽略 SIGINT（Ctrl+C），使用 SIGTERM 关闭 */
    signal(SIGINT, SIG_IGN);

    printf("进程 %d 运行中，发送 SIGTERM 终止...\n", getpid());

    while (!g_shutdown) {
        /* 业务逻辑 */
        sleep(1);
    }

    printf("收到 SIGTERM，优雅关闭...\n");
    return 0;
}
```

## 5. 实际示例

### 5.1 处理 SIGTERM 优雅退出

```c
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdbool.h>
#include <string.h>

/*
 * 优雅退出模式
 */
static volatile sig_atomic_t g_running = true;
static const char *g_config_file = "/tmp/app.conf";

void handle_terminate(int signum)
{
    /* 使用 write() 而不是 printf() - 信号安全 */
    const char msg[] = "\n收到终止信号，开始优雅关闭...\n";
    write(STDOUT_FILENO, msg, sizeof(msg) - 1);
    g_running = false;
}

void handle_reload(int signum)
{
    const char msg[] = "\n收到重载信号，重新加载配置...\n";
    write(STDOUT_FILENO, msg, sizeof(msg) - 1);

    /*
     * 重新加载配置
     * 这里仅示意，实际应读取 g_config_file
     */
}

int main(void)
{
    struct sigaction sa_term, sa_hup;

    /* 设置 SIGTERM 处理 */
    sa_term.sa_handler = handle_terminate;
    sigemptyset(&sa_term.sa_mask);
    sa_term.sa_flags = 0;  /* 不自动重启系统调用 */

    /* 设置 SIGHUP 处理（常用于重载配置） */
    sa_hup.sa_handler = handle_reload;
    sigemptyset(&sa_hup.sa_mask);
    sa_hup.sa_flags = 0;

    sigaction(SIGTERM, &sa_term, NULL);
    sigaction(SIGHUP, &sa_hup, NULL);

    /* 忽略 SIGINT，让 SIGTERM 处理关闭 */
    signal(SIGINT, SIG_IGN);

    printf("服务启动 (PID: %d)\n", getpid());
    printf("发送 SIGTERM 进行优雅关闭\n");

    while (g_running) {
        /* 模拟业务逻辑 */
        sleep(1);
    }

    printf("资源清理完成，退出\n");
    return 0;
}
```

### 5.2 处理 SIGCHLD

```c
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>

/*
 * SIGCHLD 处理 - 避免僵尸进程
 */
void sigchld_handler(int signum)
{
    int saved_errno = errno;  /* 保存 errno */
    pid_t pid;
    int status;

    /*
     * 循环处理所有已结束的子进程
     * 使用 waitpid(-1) 而非 wait() 处理多个子进程
     */
    while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
        if (WIFEXITED(status)) {
            printf("子进程 %d 正常退出，退出码: %d\n",
                   pid, WEXITSTATUS(status));
        } else if (WIFSIGNALED(status)) {
            printf("子进程 %d 被信号 %d 终止\n",
                   pid, WTERMSIG(status));
        }
    }

    errno = saved_errno;  /* 恢复 errno */
}

int main(void)
{
    struct sigaction sa;

    /* 设置 SIGCHLD 处理 */
    sa.sa_handler = sigchld_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART | SA_NOCLDSTOP;  /* 重启系统调用，忽略停止的子进程 */

    if (sigaction(SIGCHLD, &sa, NULL) == -1) {
        perror("sigaction");
        return 1;
    }

    /* 创建子进程 */
    pid_t pid = fork();

    if (pid == 0) {
        /* 子进程 */
        printf("子进程 (PID: %d) 执行任务...\n", getpid());
        sleep(2);
        printf("子进程完成\n");
        return 42;
    } else if (pid > 0) {
        /* 父进程 */
        printf("父进程 (PID: %d) 创建子进程 %d\n", getpid(), pid);

        /* 父进程可以继续做其他事情 */
        sleep(5);

        printf("父进程结束\n");
    } else {
        perror("fork");
        return 1;
    }

    return 0;
}
```

### 5.3 超时处理（alarm）

```c
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/*
 * alarm() 实现超时机制
 */
static volatile sig_atomic_t g_alarm_triggered = 0;

void alarm_handler(int signum)
{
    g_alarm_triggered = 1;
}

/*
 * 带超时的读取操作
 * 返回值：0=超时，>0=成功读取的字节数
 */
ssize_t read_with_timeout(int fd, void *buf, size_t len, unsigned int timeout_sec)
{
    ssize_t n;
    struct sigaction sa;
    sigset_t mask, oldmask;

    /* 设置 alarm 处理 */
    sa.sa_handler = alarm_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGALRM, &sa, NULL);

    /* 阻塞 SIGALRM */
    sigemptyset(&mask);
    sigaddset(&mask, SIGALRM);
    sigprocmask(SIG_BLOCK, &mask, &oldmask);

    /* 重置标志并设置闹钟 */
    g_alarm_triggered = 0;
    alarm(timeout_sec);

    /* 执行读取 */
    n = read(fd, buf, len);

    /* 获取 alarm 剩余时间并取消 */
    unsigned int remaining = alarm(0);

    /* 恢复信号掩码 */
    sigprocmask(SIG_SETMASK, &oldmask, NULL);

    /* 如果超时，返回 -1 */
    if (g_alarm_triggered) {
        errno = ETIMEDOUT;
        return -1;
    }

    /* 如果 alarm 剩余时间小于设置的timeout，说明之前的 alarm 触发了
       但此时已经读取成功（较少见） */

    return n;
}

int main(void)
{
    char buf[256];

    printf("5秒后模拟超时...\n");

    /* 模拟一个会超时的读取（从空管道读取） */
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        perror("pipe");
        return 1;
    }

    /* 关闭写端，只从读端读取（会阻塞直到写端写入或关闭） */
    close(pipefd[1]);

    ssize_t n = read_with_timeout(pipefd[0], buf, sizeof(buf), 3);

    if (n == -1) {
        printf("读取超时！\n");
    } else {
        printf("读取到 %zd 字节\n", n);
    }

    close(pipefd[0]);
    return 0;
}
```

## 6. 线程中的信号处理

### 6.1 信号掩码

每个线程都有独立的信号掩码，可以阻塞某些信号。

```c
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>

/*
 * 线程中的信号处理
 * 每个线程有自己的信号掩码
 */

/* 工作线程专用信号 */
static sigset_t worker_mask;

void *worker_thread(void *arg)
{
    int sig;
    int id = *(int *)arg;

    printf("工作线程 %d: 开始运行\n", id);

    /*
     * 在工作线程中，只处理特定的信号
     * 阻塞所有其他信号
     */
    if (sigprocmask(SIG_SETMASK, &worker_mask, NULL) == -1) {
        perror("sigprocmask");
        return NULL;
    }

    printf("工作线程 %d: 信号掩码已设置\n", id);

    /* 模拟长时间运行的任务 */
    for (int i = 0; i < 5; i++) {
        sleep(1);
        printf("工作线程 %d: 运行中 (%d/5)\n", id, i + 1);
    }

    printf("工作线程 %d: 完成\n", id);
    return NULL;
}

int main(void)
{
    pthread_t tid1, tid2;
    int id1 = 1, id2 = 2;

    /* 设置工作线程的信号掩码：阻塞 SIGINT 和 SIGTERM */
    sigemptyset(&worker_mask);
    sigaddset(&worker_mask, SIGINT);
    sigaddset(&worker_mask, SIGTERM);

    /* 创建工作线程 */
    if (pthread_create(&tid1, NULL, worker_thread, &id1) != 0) {
        perror("pthread_create");
        return 1;
    }

    if (pthread_create(&tid2, NULL, worker_thread, &id2) != 0) {
        perror("pthread_create");
        return 1;
    }

    /*
     * 主线程接收信号
     * 工作线程不响应 SIGINT/SIGTERM
     */
    printf("主线程: 工作线程正在运行，可发送 SIGINT/SIGTERM\n");
    printf("主线程: 等待工作线程结束...\n");

    pthread_join(tid1, NULL);
    pthread_join(tid2, NULL);

    printf("主线程: 所有工作线程结束\n");
    return 0;
}
```

### 6.2 线程 vs 进程

```c
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/wait.h>

/*
 * 信号在多线程和多进程中的行为差异
 */

/*
 * 关键区别：
 *
 * 线程模型：
 * - 信号作用于整个进程
 * - 任意线程可能收到信号
 * - 使用 pthread_sigmask() 管理信号掩码
 * - sigwait() 可同步等待信号
 *
 * 进程模型：
 * - 信号直接发送给进程
 * - 由特定进程（组）处理
 * - 使用 sigprocmask() 管理信号掩码
 */

/* 多线程信号处理演示 */
void *signal_handler_thread(void *arg)
{
    sigset_t mask;
    int sig;

    sigemptyset(&mask);
    sigaddset(&mask, SIGUSR1);

    /*
     * 同步等待信号（仅在专门线程中）
     * 注意：信号必须先被阻塞（pthread_sigmask）
     */
    while (1) {
        int ret = sigwait(&mask, &sig);
        if (ret == 0 && sig == SIGUSR1) {
            printf("信号处理线程: 收到 SIGUSR1\n");
        }
    }

    return NULL;
}

void async_signal_handler(int signum)
{
    /*
     * 异步信号处理函数
     * 注意：必须使用异步信号安全的函数
     */
    if (signum == SIGUSR1) {
        const char msg[] = "异步收到 SIGUSR1\n";
        write(STDOUT_FILENO, msg, sizeof(msg) - 1);
    }
}

int main_thread_example(void)
{
    pthread_t tid;
    sigset_t mask;

    /* 阻塞 SIGUSR1（主线程和所有子线程都会继承） */
    sigemptyset(&mask);
    sigaddset(&mask, SIGUSR1);
    if (pthread_sigmask(SIG_BLOCK, &mask, NULL) != 0) {
        perror("pthread_sigmask");
        return 1;
    }

    /* 创建信号处理线程 */
    if (pthread_create(&tid, NULL, signal_handler_thread, NULL) != 0) {
        perror("pthread_create");
        return 1;
    }

    printf("主线程: 发送 SIGUSR1 到进程\n");
    sleep(1);
    kill(getpid(), SIGUSR1);  /* 发送信号到进程 */

    pthread_join(tid, NULL);
    return 0;
}
```

## 7. 最佳实践

### 7.1 信号安全函数

```c
/*
 * 只能在信号处理函数中调用的函数（部分列表）：
 *
 * _exit()          - 退出进程
 * close()          - 关闭文件描述符
 * exec()           - 执行新程序
 * fcntl()          - 文件控制操作
 * getpid()         - 获取进程 ID
 * kill()           - 发送信号
 * mkdir()          - 创建目录
 * open()           - 打开文件
 * pipe()           - 创建管道
 * read()           - 读取数据
 * rename()         - 重命名文件
 * rmdir()          - 删除目录
 * signal()         - 设置信号处理（BSD 语义）
 * sleep()          - 睡眠（可能不保证）
 * unlink()         - 删除文件
 * wait()           - 等待子进程
 * write()          - 写入数据
 *
 * 不可重入函数（不应在信号处理函数中使用）：
 * - malloc(), free()
 * - printf(), fprintf(), sprintf()
 * - 大多数 libc 函数
 */

/*
 * 安全的做法：使用 self-pipe trick
 */
static int signal_fd[2];

void signal_handler(int signum)
{
    /* 写入一个字节到 pipe，通知主循环 */
    char byte = (char)signum;
    write(signal_fd[1], &byte, 1);
}

void setup_self_pipe(void)
{
    pipe(signal_fd);

    /* 设置信号处理 */
    struct sigaction sa;
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGTERM, &sa, NULL);

    /* 设置为非阻塞 */
    fcntl(signal_fd[0], F_SETFL, O_NONBLOCK);
}

void event_loop(void)
{
    char byte;
    fd_set readfds;

    while (1) {
        FD_ZERO(&readfds);
        FD_SET(signal_fd[0], &readfds);

        /* 使用 select 监控信号 pipe 和其他 fd */
        int ret = select(signal_fd[0] + 1, &readfds, NULL, NULL, NULL);

        if (ret > 0 && FD_ISSET(signal_fd[0], &readfds)) {
            /* 读取并处理信号 */
            read(signal_fd[0], &byte, 1);
            /* 在这里处理信号，使用 printf 等安全函数 */
            printf("收到信号 %d\n", byte);
        }
    }
}
```

## 8. 参考资料

- `man 7 signal` - 信号机制总览
- `man 2 signal` - 系统调用 signal
- `man 2 sigaction` - 系统调用 sigaction
- `man 2 kill` - 发送信号
- `man 2 pause` - 等待信号
- `man 2 alarm` - 设置闹钟
- POSIX.1-2017 标准
