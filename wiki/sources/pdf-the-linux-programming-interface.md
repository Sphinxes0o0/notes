---
type: source
source-type: pdf
title: "The Linux Programming Interface"
author: "Michael Kerrisk"
date: 2010
size: large
path: raw/PDFs/books/The Linux Programming Interface.pdf
summary: "Michael Kerrisk 编写，1556页Linux/UNIX系统编程权威手册，覆盖500+系统调用和库函数，200+示例程序，是Linux系统编程的百科全书"
tags: [linux, unix, system-programming, syscalls, books]
created: 2026-05-25
sources: [pdf-linux-kernel-books, pdf-linux-sysprog]
---

# The Linux Programming Interface

## Core Content

### Overview

Michael Kerrisk 的权威 Linux/UNIX 系统编程手册，1556页，是 Linux 系统编程领域最全面的参考书。Kerrisk 本人维护 Linux man-pages 项目，因此本书对系统调用的描述与实际 Linux 内核行为高度一致。

**统计：**
- 1556 页
- 64 章 + 附录
- 500+ 系统调用和库函数描述
- 200+ 完整示例程序
- 88 张表格，115 张图表

---

### Part I — File I/O (Ch 1–18)

**History & Standards (Ch 1):**
- UNIX 和 Linux 历史：AT&T UNIX → BSD → GNU/Linux
- C 语言标准（C89/C99/C11）、POSIX 标准（POSIX.1-2001/2008）
- Linux 特有的系统调用 vs 标准接口

**Fundamental Concepts (Ch 2):**
- 内核与用户空间，内核如何工作
- 系统调用：概念、入参传递、返回值（-1 表示错误，errno 设置）
- 库函数 vs 系统调用

**File I/O (Ch 4–6, 13):**
- open(), read(), write(), close(), lseek()
- O_NONBLOCK, O_SYNC, O_DIRECT 等标志
- I/O 缓冲：用户态缓冲区（stdio）、内核页缓存、direct I/O
- fsync(), sync(), sync_file_range()

**File Attributes & Filesystems (Ch 11, 14–18):**
- stat(), fstat(), lstat(), inode, 文件类型（regular/dir/symlink/device/socket）
- 文件权限：rwx 三元组、umask、chmod/chown
- extended attributes (xattr), ACL
- 目录操作：mkdir(), rmdir(), unlink(), rename()
- 符号链接 vs 硬链接，目录项（dentry）缓存
- inotify API：文件事件监控（inotify_init/add/watch）

**Process Credentials (Ch 8–9):**
- 用户 ID / 组 ID：真实/有效/保存设置
- 进程凭证：getuid/geteuid, getgid/egetgid
- setuid/setreuid/setresuid/setcap 等

---

### Part II — Process Management (Ch 19–37)

**Processes (Ch 6, 24–28):**
- 进程创建：fork(), vfork(), clone()
- 进程终止：_exit(), exit(), atexit()
- 进程调度与优先级：nice/renice, getpriority/setpriority
- 进程资源：getrusage(), getrlimit/setrlimit
- 监控子进程：wait()/waitpid(), wait4()
- execve() 系列：execl/execv/execle/execvp/execlp

**Signals (Ch 20–23):**
- 信号概念：SIGTERM/SIGKILL/SIGINT 等标准信号
- signal() vs sigaction()，SA_RESTART 标志
- 实时信号：sigqueue(), SIGRTMIN–SIGRTMAX
- signal mask: sigprocmask(), pthread_sigmask()
- 挂起等待：sigsuspend(), pause()
- alarm(), setitimer(), timer_create/gettimeofday

**Threads (Ch 29–33):**
- 线程创建：pthread_create(), pthread_join/exit
- 线程同步：pthread_mutex_lock/trylock, pthread_cond_wait/signal, pthread_rwlock
- 线程取消：pthread_cancel(), cleanup handlers
- 线程本地存储：pthread_key_create/getspecific/setspecific
- 线程安全：可重入函数 vs 线程安全函数

**Process Groups & Sessions (Ch 34):**
- 进程组：getpgid/setpgid, setpgrp
- 会话：setsid()/getsid(), 终端控制进程
- 作业控制：前台/后台进程组，SIGTTIN/SIGTTOU

**Daemons (Ch 37):**
- daemon() 函数，双 fork() 脱终端
- 守护进程编写规范：stdin=/dev/null, stdout→syslog

---

### Part III — Memory & IPC (Ch 38–54)

**Memory Allocation (Ch 7):**
- 堆内存：brk()/sbrk()（调整 program break）、malloc()/free()
- malloc 实现：隐式空闲链表、分离空闲链表（glibc ptmalloc）
- alloca() 栈上分配
- 内存对齐注意事项

**Virtual Memory Operations (Ch 49–50):**
- mmap()/munmap()：文件映射、匿名映射、private vs shared
- mprotect()：内存保护
- madvise()：内存访问提示
- remap_file_pages()（已废弃）

**Shared Libraries (Ch 41–42):**
- 动态链接：dlopen/dlsym/dlclose，RTLD_NOW/RTLD_LAZY
- 符号解析顺序：全局符号介入
- 预加载库：LD_PRELOAD
- 库版本：soname, 符号版本脚本

**POSIX IPC (Ch 51–55):**
- 消息队列：mq_open/mq_send/mq_receive，优先级
- 信号量：sem_open/sem_wait，命名 vs 无名
- 共享内存：shm_open/mmap，POSIX vs System V

**System V IPC (Ch 45–48):**
- msgget/msgsnd/msgrcv/msgctl：消息队列
- semget/semop/semctl：信号量数组
- shmget/shmat/shmdt/shmctl：共享内存
- ipcs/ipcrm 命令

**File Locking (Ch 55):**
- flock()：BSD 文件锁，LOCK_NB 非阻塞
- fcntl()： advisory record locking，F_SETLKW/F_SETLK
- Linux 特有的 /proc/locks 文件

---

### Part IV — Sockets & Networking (Ch 56–61)

**Sockets Introduction (Ch 56):**
- socket() 系统调用，socket pair
- 地址族：AF_INET/AF_INET6/AF_UNIX/AF_UNSPEC

**UNIX Domain (Ch 57):**
- Unix domain socket：pathname socket, abstract namespace socket
- socketpair()
- 传送文件描述符：sendmsg()/recvmsg() with SCM_RIGHTS

**TCP/IP Networks (Ch 58–59):**
- IP 协议：IPv4/IPv6 头，路由，TTL
- TCP：三次握手、四次挥手、状态机、TCP 选项
- UDP：无连接、面向数据报
- 套接字地址：sockaddr_in/sockaddr_in6/sockaddr_un

**Server Design (Ch 60):**
- iterative vs concurrent servers
- select()/poll()：多路复用
- epoll：边缘触发/水平触发，EPOLLEXCLUSIVE
- 多线程服务器：thread-per-connection, worker thread pool
- pre-fork() 技术

**Advanced Topics (Ch 61):**
- SO_REUSEADDR/SO_REUSEPORT
- 超时处理：alarm/setitimer/poll/select + SO_RCVTIMEO/SO_SNDTIMEO
- scatter-gather I/O：readv/writev
- 零拷贝：sendfile()
- Unix domain socket 传递文件描述符高级用法

---

### Part V — Terminals & Async I/O (Ch 62–64)

**Terminals (Ch 62):**
- 终端属性：termios，ICANON/ISIG 等标志
- 行规范：c_lflag，ECHO/ICRNL/IXON
- 终端窗口大小：winsize, TIOCGWINSZ
- 伪终端：pty/tty slave/master，forkpty()

**Alternative I/O Models (Ch 63):**
- 非阻塞 I/O：O_NONBLOCK
- 异步 I/O：POSIX AIO（aio_read/aio_write），Linux 特有 io_setup/aio_*
- 信号驱动 I/O：SIGIO
- epoll 边缘触发高级用法

**Pseudoterminals (Ch 64):**
- pty pair: openpty()/login_tty()
- screen/tmux 实现原理
- sshd 如何使用 pty

---

## Key Quotes

- "The Linux Programming Interface is the definitive guide to the Linux and UNIX programming interface — the interface employed by nearly every application that runs on a Linux or UNIX system." — Michael Kerrisk
- "If I had to choose a single book to sit next to my machine when writing software for Linux, this would be it." — Martin Landers, Software Engineer, Google

## Related Pages

- [[sys-prog-index]] — System programming navigation
- [[sources/notes-sys]] — System programming notes (TTY/Shell/ELF/IPC)
- [[sources/notes-kernel]] — Linux kernel subsystem notes
- System Call Interface — System call interface entity
- [[kernel-subsystems-index]] — Kernel subsystems (locking, IPC, RCU, time)
- [[os-index]] — Operating system fundamentals
- [[sources/notes-os]] — Linux OS notes (VFS/scheduler/SLUB/cgroups)
