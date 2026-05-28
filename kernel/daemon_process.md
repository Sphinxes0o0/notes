---
title: 守护进程
---

# 守护进程

## 守护进程概念

### 什么是守护进程

守护进程（Daemon）是在后台运行的特殊进程，独立于控制终端，通常在系统启动时自动启动，负责提供系统服务或响应请求。

守护进程的生命周期很长，通常从系统启动一直运行到系统关闭。它们不需要用户登录即可运行，默默地在后台执行任务。

### 守护进程 vs 普通进程

| 特性 | 守护进程 | 普通进程 |
|------|----------|----------|
| 控制终端 | 无 | 可能关联终端 |
| 运行方式 | 后台运行 | 前台或后台 |
| 启动方式 | 系统启动/inetd/xinetd | 用户手动启动 |
| 输出 | 通常重定向到日志 | 可能输出到终端 |
| 会话关系 | 脱离原会话 | 可能属于某会话 |

### 常见的守护进程

- **sshd**：Secure Shell 守护进程，负责远程登录连接
- **httpd**：HTTP 服务器守护进程，提供 Web 服务
- **mysqld**：MySQL 数据库守护进程，管理数据库服务
- **systemd**：系统和服务管理器（现代 Linux 替代 init）
- **crond**：定时任务调度守护进程
- **rsyslogd**：系统日志守护进程

## 守护进程的特性

### 在后台运行

守护进程的核心特征是脱离控制终端运行。这意味着：

- 不会阻塞终端，终端关闭后进程继续运行
- 不受终端产生的信号（如 Ctrl+C）影响
- 标准输入、标准输出、标准错误需要特殊处理

### 脱离控制终端

守护进程通过以下方式脱离控制终端：

1. **成为会话首进程**（Session Leader）
2. **成为进程组组长**（Process Group Leader）
3. **关闭或重定向标准文件描述符**

当进程成为会话首进程时，它不再与任何控制终端关联。

### 独立会话和进程组

```
Session (SID: 1000)
├── Process Group Leader (PGID: 1000, PID: 1000) ← 终端控制进程
│   └── Terminal
└── Process Group (PGID: 1001)
    └── Daemon Process (PID: 2000, SID: 1000) ← 守护进程
```

守护进程通常：
- 创建新会话并成为该会话的首进程
- 创建新进程组并成为该进程组的组长
- 或者完全脱离任何进程组，独立存在

## 创建守护进程的步骤

### 标准流程

```
1. fork() 第一次
   └── 终止父进程，子进程继续
2. setsid() 创建新会话
   └── 子进程成为会话首进程和进程组组长
3. 改变工作目录
   └── 防止占用可卸载的文件系统
4. 关闭标准文件描述符
   └── 0, 1, 2 (/dev/null)
5. 第二次 fork() (可选)
   └── 防止误重新获取控制终端
```

### 第一次 fork

```c
pid_t pid = fork();

if (pid < 0) {
    // fork 失败
    perror("fork");
    exit(EXIT_FAILURE);
} else if (pid > 0) {
    // 父进程退出
    exit(EXIT_SUCCESS);
}

// 子进程继续运行
// 此时子进程继承了父进程的会话、进程组和控制终端
```

### setsid() 创建新会话

`setsid()` 函数创建一个新会话并成为会话首进程：

```c
if (setsid() < 0) {
    perror("setsid");
    exit(EXIT_FAILURE);
}
```

调用 `setsid()` 后：
- 当前进程成为新会话的会话首进程
- 当前进程成为新进程组的进程组组长
- 当前进程脱离任何控制终端

### 改变工作目录

将工作目录改变为根目录 `/` 或其他不会卸载的目录：

```c
if (chdir("/") < 0) {
    perror("chdir");
    exit(EXIT_FAILURE);
}
```

原因：如果不改变，当前的目录可能被卸载，导致守护进程无法访问。

### 关闭标准文件描述符

关闭标准输入、标准输出和标准错误，并将它们重定向到 `/dev/null`：

```c
int fd = open("/dev/null", O_RDWR);
if (fd < 0) {
    perror("open");
    exit(EXIT_FAILURE);
}

// 重定向标准输入
if (dup2(fd, STDIN_FILENO) < 0) {
    perror("dup2 stdin");
    exit(EXIT_FAILURE);
}

// 重定向标准输出
if (dup2(fd, STDOUT_FILENO) < 0) {
    perror("dup2 stdout");
    exit(EXIT_FAILURE);
}

// 重定向标准错误
if (dup2(fd, STDERR_FILENO) < 0) {
    perror("dup2 stderr");
    exit(EXIT_FAILURE);
}

if (fd > STDERR_FILENO) {
    close(fd);
}
```

这样任何尝试读取标准输入或写入标准输出/错误的代码都不会产生实际效果。

### 第二次 fork() (可选)

第二次 fork 是可选的，用于进一步确保守护进程不会重新获得控制终端：

```c
pid = fork();

if (pid < 0) {
    perror("fork");
    exit(EXIT_FAILURE);
} else if (pid > 0) {
    // 第一个子进程退出
    exit(EXIT_SUCCESS);
}

// 第二个子进程继续运行
// 此时即使获取控制终端，也只是另一个无关进程的终端
```

## 守护进程的实现代码

### 完整的 daemon() 函数实现

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>

int daemonize(void)
{
    pid_t pid;
    int fd;

    /* 第一次 fork */
    pid = fork();
    if (pid < 0) {
        perror("fork");
        return -1;
    }
    if (pid > 0) {
        /* 父进程退出 */
        exit(EXIT_SUCCESS);
    }

    /* 成为会话首进程 */
    if (setsid() < 0) {
        perror("setsid");
        return -1;
    }

    /* 忽略 SIGHUP 信号 */
    signal(SIGHUP, SIG_IGN);

    /* 第二次 fork */
    pid = fork();
    if (pid < 0) {
        perror("fork");
        return -1;
    }
    if (pid > 0) {
        /* 第一个子进程退出 */
        exit(EXIT_SUCCESS);
    }

    /* 改变工作目录到根目录 */
    if (chdir("/") < 0) {
        perror("chdir");
        return -1;
    }

    /* 关闭所有文件描述符 */
    for (fd = sysconf(_SC_OPEN_MAX); fd >= 0; fd--) {
        close(fd);
    }

    /* 将标准输入、输出、错误重定向到 /dev/null */
    fd = open("/dev/null", O_RDWR);
    if (fd < 0) {
        return -1;
    }

    dup2(fd, STDIN_FILENO);
    dup2(fd, STDOUT_FILENO);
    dup2(fd, STDERR_FILENO);

    if (fd > STDERR_FILENO) {
        close(fd);
    }

    return 0;
}
```

### 使用示例

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

int main(void)
{
    FILE *fp;

    /* 守护进程化 */
    if (daemonize() != 0) {
        fprintf(stderr, "Failed to daemonize\n");
        exit(EXIT_FAILURE);
    }

    /* 守护进程工作 */
    while (1) {
        sleep(30);

        /* 写入日志文件 */
        fp = fopen("/var/log/mydaemon.log", "a");
        if (fp != NULL) {
            time_t now = time(NULL);
            fprintf(fp, "Heartbeat at %s", ctime(&now));
            fclose(fp);
        }
    }

    return 0;
}
```

### 错误处理

守护进程实现中需要处理的错误情况：

| 操作 | 可能的错误 | 处理方式 |
|------|-------------|----------|
| fork() | EAGAIN, ENOMEM | 记录日志，优雅退出 |
| setsid() | EPERM | 进程已是会话首进程 |
| chdir() | EACCES, ENOENT | 使用备用目录 |
| open() | 各种文件系统错误 | 继续运行，不影响核心功能 |

### 注意事项

1. **信号处理**：守护进程应忽略所有不必要的信号，或设置合适的信号处理器
2. **文件创建权限**：使用 umask() 设置合适的文件创建掩码
3. **PID 文件**：创建 PID 文件便于管理（如 `/var/run/mydaemon.pid`）
4. **资源限制**：使用 setrlimit() 调整资源限制
5. **环境变量**：清理不必要环境变量

```c
/* 设置文件创建掩码 */
umask(0);

/* 创建 PID 文件 */
FILE *pidfp = fopen("/var/run/mydaemon.pid", "w");
if (pidfp) {
    fprintf(pidfp, "%d\n", getpid());
    fclose(pidfp);
}
```

## 守护进程的日志

### syslog 的使用

syslog 是 Unix 系统标准日志机制，守护进程通常使用 syslog 记录日志：

```c
#include <syslog.h>

int main(void)
{
    /* 打开日志 */
    openlog("mydaemon", LOG_PID | LOG_CONS, LOG_DAEMON);

    /* 记录不同级别的日志 */
    syslog(LOG_INFO, "Daemon started");
    syslog(LOG_WARNING, "This is a warning message");
    syslog(LOG_ERR, "This is an error message");
    syslog(LOG_DEBUG, "Debug information: value=%d", 42);

    /* 关闭日志 */
    closelog();

    return 0;
}
```

**日志级别**：

| 级别 | 名称 | 用途 |
|------|------|------|
| LOG_EMERG | 紧急 | 系统不可用 |
| LOG_ALERT | 警报 | 需要立即处理 |
| LOG_CRIT | 关键 | 严重情况 |
| LOG_ERR | 错误 | 错误情况 |
| LOG_WARNING | 警告 | 警告情况 |
| LOG_NOTICE | 通知 | 正常但重要 |
| LOG_INFO | 信息 | 信息消息 |
| LOG_DEBUG | 调试 | 调试消息 |

### 输出重定向

守护进程的输出重定向方式：

1. **重定向到 /dev/null**：完全丢弃输出
2. **重定向到文件**：将输出写入日志文件
3. **重定向到 syslog**：通过 syslog 记录

```c
/* 重定向到日志文件 */
int fd = open("/var/log/mydaemon.log",
              O_WRONLY | O_CREAT | O_APPEND, 0644);
if (fd >= 0) {
    dup2(fd, STDOUT_FILENO);
    dup2(fd, STDERR_FILENO);
    if (fd > STDERR_FILENO) {
        close(fd);
    }
}
```

### 完整的 syslog 守护进程示例

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <syslog.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/resource.h>

void sig_handler(int sig)
{
    if (sig == SIGTERM) {
        syslog(LOG_INFO, "Received SIGTERM, shutting down");
        closelog();
        exit(EXIT_SUCCESS);
    }
}

int daemonize(void)
{
    struct rlimit rl;
    pid_t pid;
    int fd;

    /* 清除文件创建掩码 */
    umask(0);

    /* 获取最大文件描述符数 */
    if (getrlimit(RLIMIT_NOFILE, &rl) < 0) {
        return -1;
    }

    /* 第一次 fork */
    pid = fork();
    if (pid < 0) {
        return -1;
    }
    if (pid > 0) {
        exit(EXIT_SUCCESS);
    }

    /* 成为会话首进程 */
    if (setsid() < 0) {
        return -1;
    }

    /* 忽略 SIGHUP */
    signal(SIGHUP, SIG_IGN);

    /* 第二次 fork */
    pid = fork();
    if (pid < 0) {
        return -1;
    }
    if (pid > 0) {
        exit(EXIT_SUCCESS);
    }

    /* 改变工作目录 */
    if (chdir("/") < 0) {
        return -1;
    }

    /* 关闭所有文件描述符 */
    if (rl.rlim_max == RLIM_INFINITY) {
        rl.rlim_max = 1024;
    }
    for (fd = 0; fd < rl.rlim_max; fd++) {
        close(fd);
    }

    /* 重定向标准描述符到 /dev/null */
    fd = open("/dev/null", O_RDWR);
    dup2(fd, STDIN_FILENO);
    dup2(fd, STDOUT_FILENO);
    dup2(fd, STDERR_FILENO);

    return 0;
}

int main(void)
{
    /* 设置信号处理器 */
    signal(SIGTERM, sig_handler);
    signal(SIGINT, sig_handler);

    /* 打开 syslog */
    openlog("mydaemon", LOG_PID | LOG_CONS, LOG_DAEMON);

    /* 守护进程化 */
    if (daemonize() < 0) {
        syslog(LOG_ERR, "Failed to daemonize");
        closelog();
        exit(EXIT_FAILURE);
    }

    syslog(LOG_INFO, "Daemon started, PID: %d", getpid());

    /* 主循环 */
    while (1) {
        sleep(60);
        syslog(LOG_DEBUG, "Heartbeat");
    }

    return 0;
}
```

## 总结

守护进程是 Linux 系统中重要的后台服务组件。创建守护进程的核心步骤包括：

1. 通过 `fork()` 创建子进程并终止父进程
2. 使用 `setsid()` 创建新会话，脱离控制终端
3. 改变工作目录到根目录，避免占用可卸载文件系统
4. 关闭或重定向标准文件描述符
5. （可选）第二次 `fork()` 防止重新获取控制终端

使用 syslog 进行日志记录是守护进程的标准做法，可以集中管理日志输出，便于系统管理和故障排查。
