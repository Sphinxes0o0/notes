---
type: source
source-type: pdf
title: "UNIX环境高级编程（第三版）"
author: "W. Richard Stevens, Stephen A. Rago"
date: 2013
size: medium
path: raw/PDFs/books/UNIX环境高级编程(第三版).pdf
summary: "APUE 第三版，Stevens & Rago 著，822页，UNIX/Linux 系统编程经典，更新至 UNIX 标准（POSIX.1-2001 以后），深入覆盖系统调用、进程、线程、I/O、IPC、网络编程。注：扫描版，无可提取文本"
tags: [unix, linux, system-programming, books]
created: 2026-05-25
sources: [pdf-the-linux-programming-interface, pdf-linux-sysprog]
---

# UNIX环境高级编程（第三版）

> 注：本 PDF 为扫描版，PyPDF2 无法提取文本。以下内容基于书籍已知结构。
>
> 原书：*Advanced Programming in the UNIX Environment*, 3rd Edition, W. Richard Stevens & Stephen A. Rago, Addison-Wesley, 2013.

## Core Content

### Overview

APUE 是 UNIX/Linux 系统编程的里程碑著作，第一版由 W. Richard Stevens 撰写（1992），第二版（2005）由 Stephen Rago 协助修订，第三版（2013）由 Rago 独立更新至现代 POSIX 标准。

**统计：**
- 822 页
- 第三版更新内容：POSIX.1-2001 及以后标准、Linux 特有接口（如 epoll、inotify）、IPv6
- 所有示例代码在 Linux (Ubuntu) 上测试

**与 TLPI 的关系：**
- TLPI（Michael Kerrisk，2010）可视为 APUE 的精神继承者
- APUE 更聚焦于 POSIX 标准接口，TLPI 更聚焦于 Linux 特有实现
- 两者内容高度重叠，但 APUE 是 POSIX 认证教材

---

### Part I — UNIX Environment (Ch 1–5)

**Chapter 1 — UNIX 体系结构：**
- 内核、库函数、系统调用、应用软件的分层
- POSIX 标准与 Single UNIX Specification
- 标准化的历史：C 语言标准化 → POSIX → Single UNIX Specification

**Chapter 2 — UNIX 标准化和实现：**
- ISO C 库（IEEE Std 1003.1）
- POSIX 标准：POSIX.1（系统接口）、POSIX.2（shell/工具）
- 限制：sysconf()/pathconf()/fpathconf() 运行时查询
- 选项：_POSIX_ADVISORY_INFO 等

**Chapter 3 — 文件 I/O：**
- open()/creat()/close()/read()/write()/lseek()
- 文件描述符与会话（stdin/stdout/stderr）
- atomic 操作：pread()/pwrite()
- dup()/dup2() 复制文件描述符

**Chapter 4 — 文件与目录：**
- stat()/fstat()/lstat()：获取文件元数据
- 文件类型：regular/directory/char device/block device/fifo/socket/symlink
- 硬链接与符号链接：link()/unlink()/symlink()/readlink()
- 文件时间戳：access/modinify/change (atime/mtime/ctime)
- utime()/utimes()/futimens()/utimensat()
- 目录操作：mkdir()/rmdir()、chdir()/getcwd()

**Chapter 5 — 标准 I/O 库：**
- fopen()/fclose()/fread()/fwrite()/fseek()
- 格式化 I/O：printf()/scanf() 家族
- 临时文件：tmpfile()/tmpnam()/mkdtemp()/mkstemp()
- 内存流：fmemopen()/open_memstream()

---

### Part II — Process Management (Ch 6–10)

**Chapter 6 — 系统数据文件和信息：**
- /etc/passwd、/etc/group：getpwuid()/getpwnam()
- 阴影密码：/etc/shadow，getspnam()
- 日期和时间：time_t、系统时间 vs 墙上时钟

**Chapter 7 — 进程环境：**
- main() 参数：argc/argv，environ 全局变量
- 进程启动与终止：exit()/_exit()/atexit()
- C 程序的内存布局：text/rodata/data/bss/heap/stack
- 共享库：.so (Linux)，动态加载 dlopen()

**Chapter 8 — 进程控制：**
- fork()：复制整个地址空间，写时复制（COW）
- vfork()：历史用法，现代程序不推荐
- execve()：替换当前进程映像，exec 系列函数
- 僵死进程：wait()/waitpid() 回收子进程
- waitid()/wait3()/wait4()：更多选项

**Chapter 9 — 进程关系：**
- 进程组：getpgid()/setpgid()，前台/后台进程组
- 会话：setsid()/getsid()，会话首进程，终端控制
- 作业控制：SIGTTIN/SIGTTOU/SIGTSTP/SIGCONT
- 孤儿进程组

**Chapter 10 — 信号：**
- signal()：简单但不可靠（System V 语义）
- sigaction()：可移植的信号处理
- 中断系统调用：SA_RESTART 自动重启
- 可靠信号语义：信号排队、pending vs blocked
- kill()/raise()，alarm()/pause()/abort()
- 作业控制信号

---

### Part III — Process Communication (Ch 11–15)

**Chapter 11 — 线程：**
- 线程概念：共享进程的地址空间、文件描述符、信号处理
- pthread_create()/pthread_join()/pthread_self()
- 线程同步：mutex、读写锁、条件变量
- pthread_once() 单次执行

**Chapter 12 — 线程控制：**
- 线程同步原语：pthread_mutex_*/pthread_rwlock_*/pthread_cond_*
- 线程取消：pthread_cancel()，cleanup handlers (pthread_cleanup_push/pop)
- 线程局部存储：pthread_key_create()
- 线程与 fork：fork 后的线程语义
- 线程与信号：每个线程独立 signal mask

**Chapter 13 — 守护进程：**
- 守护进程特性：无控制终端、后台运行
- 创建步骤：fork+setsid()+chdir()+umask()+关闭 fd
- syslog() 系统日志接口：LOG_INFO/LOG_ERR 等
- 单实例守护进程：文件锁（flock/F_WRLCK）

**Chapter 14 — 进程资格（Process Credentials）：**
- 真实/有效/保存的用户 ID 和组 ID
- setuid()/setgid()，seteuid()/setegid()
- setreuid()/setregid()：交换真实/有效 ID
- 组访问：getgroups()/setgroups()/initgroups()
- 补充组 ID

**Chapter 15 — 高级 I/O：**
- 非阻塞 I/O：O_NONBLOCK，减少 open()/read()/write()/accept() 的阻塞
- 记录锁：flock()（BSD）vs fcntl()（POSIX record locking）
- I/O 多路复用：select()/poll()
- 异步 I/O：POSIX aio_*/aio_error/aio_read/aio_write
- readv()/writev()：分散/聚集 I/O
- mmap()/munmap()：内存映射 I/O

---

### Part IV — IPC — Ch 15–18 (Advanced)

**Chapter 16 — 进程间通信：**
- IPC 三种形式：消息、信号量、共享内存
- System V IPC：msgget/msgsnd/msgrcv/semget/semop/semctl/shmget/shmat/shmdt/shmctl
- POSIX IPC：mq_open/mq_send/mq_receive/sem_open/sem_wait/shm_open/mmap

**Chapter 17 — 高级进程间通信：**
- Unix 域套接字：socketpair()，AF_UNIX
- 传送文件描述符：sendmsg()/recvmsg() SCM_RIGHTS
- 服务器端点 /tmp/.X11-unix/X0
- Linux 特有：epoll_create()/epoll_ctl()/epoll_wait()

**Chapter 18 — 终端 I/O：**
- 终端结构：termios，c_cflag/c_lflag/c_iflag/c_oflag/c_cc
- 行规范：ICANON/ECHO/ISIG/ICRNL
- 终端窗口大小：winsize，TIOCGWINSZ/TIOCSWINSZ
- 作业控制与终端：SIGWINCH

---

### Part V — Extended Topics

**Advanced Topics Covered:**
- 网络编程：TCP/UDP 套接字，select/poll 在网络中的应用
- XSI (X/Open System Interface) 扩展
- proc 文件系统：/proc/self/
- 资源限制：getrlimit()/setrlimit()
- 审计：Linux 特有的 audit 系统

---

## Related Pages

- [[sources/pdf-the-linux-programming-interface]] — TLPI (more comprehensive, Linux-specific)
- [[sys-prog-index]] — System programming navigation
- [[sources/notes-sys]] — System programming notes (TTY/Shell/ELF/IPC)
- [[sources/notes-kernel]] — Linux kernel subsystem notes
- [[os-index]] — Operating system fundamentals
