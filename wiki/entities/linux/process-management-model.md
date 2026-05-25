---
type: entity
tags: [process, fork, exec, threads, unix, system-programming]
created: 2026-05-25
sources: [pdf-the-linux-programming-interface, pdf-computer-systems-programmers-perspective, pdf-unix-environment-advanced-programming]
---

# Process Management Model

## 定义

进程是 UNIX/Linux 系统中程序执行的最小单元，具有独立虚拟地址空间、文件描述符表、信号处理表。线程是共享进程地址空间的轻量级执行单元。

## 关键要点

### 进程创建与替换

**fork():**
- 复制当前进程：子进程获得父进程地址空间的完整副本（写时复制 COW）
- 返回值：父进程中返回子进程 PID，子进程中返回 0
- 子进程继承：文件描述符（共享文件表项）、信号处理方式、当前工作目录、内存映射

**execve():**
- 替换当前进程的地址空间：text/data/bss/heap/stack 全部重新初始化
- 不创建新进程：PID 保持不变，只替换了执行的程序
- 成功不返回：控制流跳转到新的入口点

**fork()+execve() 组合：**
- shell 的工作原理：fork() 创建子进程 → 子进程 execve() 运行目标程序
- vfork() 已废弃：早期 UNIX 用于效率，现代 Linux 行为与 fork() COW 相同

### 进程状态与调度

**状态机：**
```
R (Running) ←→ S (Sleeping/Interruptible)
                  ↓
              D (Uninterruptible I/O)
                  ↓
              T (Stopped, SIGSTOP)
                  ↓
              Z (Zombie)
```

**调度器（Linux CFS）：**
- 完全公平调度（Completely Fair Scheduler）：基于虚拟运行时间（vruntime）
- 红黑树管理就绪队列，O(log n) 插入/删除
- 实时调度类：SCHED_FIFO、SCHED_RR、SCHED_DEADLINE

### 进程回收

**wait()/waitpid():**
- 阻塞等待子进程终止，回收其退出状态
- waitpid(pid, status, options)：支持特定 PID、WNOWAIT（非阻塞）
- WIFEXITED/WIFSIGNALED/WIFSTOPPED：解析退出状态

**僵尸进程：**
- 子进程终止后保留内核中的 task_struct，直到父进程 wait()
- 父进程不回收 → 僵尸进程累积（`ps` 显示 `Z`）
- 解决：父进程 crash → init 接管并回收；或显式忽略 SIGCHLD（`signal(SIGCHLD, SIG_IGN)`）

### 进程组与会话

**进程组 (Process Group)：**
- 每个进程属于一个进程组，PGID = 组长的 PID
- kill -PID：向整个进程组发送信号

**会话 (Session)：**
- 进程组的集合，一个会话对应一个控制终端
- 组长进程终止不终止会话
- setsid() 创建新会话（成为会话首进程，脱离控制终端）

### 线程模型

**LinuxThreads vs NPTL：**
- 早期 LinuxThreads：每个线程是独立进程，PID 不同（不符合 POSIX）
- NPTL（Native POSIX Threads Library）：CLONE_THREAD，共享 PID
- `gettid()` 获取线程 ID（与 PID 不同）

**线程同步原语：**
- pthread_mutex：互斥锁，Mesa 管语义（spurious wakeup → always test condition in loop）
- pthread_cond_wait：条件变量，需先 lock mutex
- pthread_rwlock：读写锁，多读者可并行，写者独占
- barrier (pthread_barrier_*): 等待所有线程到达后同时继续

**线程取消：**
- pthread_cancel(tid)：请求取消目标线程
- 取消点（cancellation points）：sleep、wait、I/O、mutex lock
- pthread_cleanup_push/pop：注册清理 handler

### 守护进程 (Daemon)

**特征：**
- 无控制终端（tty = ?）
- 独立会话首进程（setsid()）
- 工作目录通常是 /（避免持有已卸载文件系统的引用）
- umask(0)：不影响子进程文件权限
- 关闭所有继承的文件描述符（0/1/2 → /dev/null）

**单实例模式：**
- 文件锁（flock 或 fcntl F_SETLK）确保只有一个实例运行
- PID 文件：/var/run/<daemon>.pid

## 相关概念

- [[os-index]] — 操作系统基础
- [[sys-prog-index]] — 系统编程导航
- Virtual Memory Systems — 虚拟内存
- [[kernel-sched-index]] — CPU 调度
- [[sources/notes-kernel]] — Linux 内核子系统
- [[sources/pdf-concurrency-perf]] — 并发与 RCU

## 来源详情

- [[sources/pdf-the-linux-programming-interface]] — TLPI Ch24-28 进程创建/终止/执行/监控
- [[sources/pdf-computer-systems-programmers-perspective]] — CS:APP Ch8 异常控制流
- [[sources/pdf-unix-environment-advanced-programming]] — APUE Ch8-9 进程控制/进程关系
