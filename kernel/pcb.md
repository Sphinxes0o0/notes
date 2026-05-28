---
title: 进程控制块 (PCB)
---

# 进程控制块 (PCB)

## PCB 概述

### 什么是 PCB

进程控制块（Process Control Block，简称 PCB）是操作系统内核中用于描述和记录进程状态信息的数据结构。PCB 是进程存在的唯一标识，操作系统通过 PCB 来管理和控制进程的执行。

当一个进程被创建时，操作系统会为该进程分配一个 PCB；当进程终止时，操作系统会回收其 PCB 并释放相关资源。

### PCB 在内核中的位置

在 Linux 内核中，PCB 位于内核空间。每个进程的 PCB 通过特定的数据结构链接在一起，便于操作系统进行进程管理和调度。

```
+------------------+     +------------------+     +------------------+
|      PCB 1       |     |      PCB 2       |     |      PCB 3       |
|  (task_struct)   |     |  (task_struct)   |     |  (task_struct)   |
+------------------+     +------------------+     +------------------+
        |                        |                        |
        v                        v                        v
   进程内核栈                 进程内核栈                 进程内核栈
```

## PCB 包含的信息

### 进程标识 (PID, PPID)

- **PID (Process ID)**: 进程的唯一标识符，用于区分不同的进程
- **PPID (Parent PID)**: 父进程的 PID，用于建立进程家族关系
- **TGID (Thread Group ID)**: 线程组 ID，同一进程中的线程共享该 ID

```c
struct task_struct {
    pid_t pid;            // 进程 ID
    pid_t tgid;           // 线程组 ID
    struct task_struct *parent;  // 指向父进程的指针
    ...
};
```

### 进程状态

进程状态反映了进程当前的执行情况，常见状态包括：

- **运行态 (Running)**: 进程正在 CPU 上执行
- **就绪态 (Ready)**: 进程已准备好，等待 CPU 调度
- **阻塞态 (Blocked)**: 进程因等待某事件（如 I/O）而暂停执行
- **僵死态 (Zombie)**: 进程已终止，但资源尚未完全释放
- **停止态 (Stopped)**: 进程被暂停，通常由信号触发

### 寄存器上下文

当进程被切换出 CPU 时，需要保存当前寄存器状态，以便下次恢复执行：

```c
struct task_struct {
    struct thread_struct thread;  // 线程级 CPU 状态
    unsigned long sp;             // 堆栈指针
    unsigned long sp0;            // 内核栈指针
    unsigned long ip;             // 指令指针
    ...
};

struct thread_struct {
    unsigned long sp;             // 用户态堆栈指针
    unsigned long ip;             // 用户态指令指针
    unsigned long ax;              // 通用寄存器
    unsigned long bx;
    unsigned long cx;
    unsigned long dx;
    unsigned long si;
    unsigned long di;
    unsigned long bp;
    ...
};
```

### 调度信息

调度信息用于进程调度器决定下一个运行的进程：

```c
struct task_struct {
    int prio;              // 动态优先级
    int static_prio;       // 静态优先级
    int normal_prio;       // 常规优先级
    unsigned int rt_priority;  // 实时优先级

    struct sched_entity se;    // 调度实体
    struct sched_rt_entity rt; // 实时调度实体
    struct sched_dl_entity dl; // 期限调度实体

    unsigned int policy;      // 调度策略
    ...
};
```

### 内存管理信息

记录进程的内存布局和地址空间：

```c
struct task_struct {
    struct mm_struct *mm;     // 进程的地址空间
    struct mm_struct *active_mm;  // 当前活跃的地址空间
    ...
};

struct mm_struct {
    struct vm_area_struct *mmap;      // 虚拟内存区域链表
    pgd_t *pgd;                       // 页全局目录
    unsigned long total_vm;           // 总虚拟内存大小
    unsigned long start_code, end_code;   // 代码段地址范围
    unsigned long start_data, end_data;   // 数据段地址范围
    unsigned long start_brk, brk;         // 堆地址范围
    unsigned long arg_start, arg_end;     // 参数区域
    unsigned long env_start, env_end;     // 环境变量区域
    ...
};
```

### 文件描述符表

每个进程都有自己的文件描述符表，记录进程打开的文件：

```c
struct task_struct {
    struct files_struct *files;  // 文件描述符表
    struct fs_struct *fs;         // 文件系统信息
    ...
};

struct files_struct {
    struct file *fd_array[NR_OPEN_DEFAULT];  // 默认文件描述符数组
    struct fdtable *fdt;                      // 文件描述符表
    ...
};

struct fdtable {
    unsigned int max_fds;         // 最大文件描述符数
    struct file **fd;             // 文件描述符指针数组
    ...
};
```

### 信号处理

进程对信号的处理方式也在 PCB 中记录：

```c
struct task_struct {
    struct signal_struct *signal;  // 进程的信号描述符
    struct sighand_struct *sighand;  // 信号处理函数表
    sigset_t blocked;               // 被阻塞的信号集合
    sigset_t real_blocked;          // 实际阻塞的信号集合
    sigset_t saved_sigmask;         // 恢复的信号掩码
    ...
};

struct sighand_struct {
    struct k_sigaction action[_NSIG];  // 信号处理函数数组
    ...
};
```

## Linux 中的 PCB

### task_struct 结构体

在 Linux 内核中，PCB 对应的是 `task_struct` 结构体，定义在 `include/linux/sched.h` 中。这是内核中最复杂的结构体之一，包含了进程的所有信息。

```c
struct task_struct {
    volatile long state;          // 进程状态
    void *stack;                  // 指向内核栈
    atomic_t usage;               // 使用计数
    unsigned int flags;           // 进程标志

    /* 进程身份 */
    pid_t pid;
    pid_t tgid;
    struct task_struct *real_parent;  // 真正的父进程
    struct task_struct *parent;       // 父进程（ptrace 相关）

    /* 调度信息 */
    int prio;
    int static_prio;
    int normal_prio;
    unsigned int rt_priority;
    struct sched_info sched_info;

    /* 内存管理 */
    struct mm_struct *mm;
    struct mm_struct *active_mm;

    /* 文件系统 */
    struct files_struct *files;

    /* 信号处理 */
    struct signal_struct *signal;
    struct sighand_struct *sighand;

    /* 命名空间 */
    struct nsproxy *nsproxy;

    /* 进程链接 */
    struct list_head tasks;       // 所有进程链表
    struct list_head children;    // 子进程链表
    struct list_head sibling;     // 兄弟进程链表

    /* 调试和审计 */
    struct audit_context *audit_context;

    /* 栈 */
    struct thread_struct thread;

    /* 内存区域 */
    struct vm_area_struct *mmap;

    /* 特定架构相关 */
    struct arch_thread arch;
};
```

### 关键字段解析

| 字段 | 说明 |
|------|------|
| `state` | 进程状态，如 `TASK_RUNNING`、`TASK_INTERRUPTIBLE` |
| `stack` | 指向进程内核栈的指针 |
| `pid` | 进程 ID，唯一标识进程 |
| `parent` | 指向父进程的指针 |
| `mm` | 指向内存描述符，管理进程地址空间 |
| `files` | 指向文件描述符表 |
| `signal` | 指向信号描述符 |
| `tasks` | 用于将进程加入调度队列 |

### 进程链表

Linux 内核通过多种链表来组织进程，便于管理和查找：

```c
// 所有进程链表 - 通过 tasks 成员链接
struct list_head task_list;

// 进程树关系
struct task_struct {
    struct list_head children;   // 子进程链表
    struct list_head sibling;     // 兄弟进程链表（链接到父进程的 children）
    struct task_struct *parent;   // 父进程指针
};

// 遍历所有进程
struct task_struct *task;
for_each_process(task) {
    printk("PID: %d, Name: %s\n", task->pid, task->comm);
}

// 宏定义
#define for_each_process(p) \
    for (p = &init_task; (p = next_task(p)) != &init_task; )
```

## 进程状态转换

### 状态机的转换图

```
                    +------------------+
                    |                  |
                    |     创建态        |
                    |  (NEW/EMBRYO)    |
                    |                  |
                    +--------+---------+
                             |
                             v
                    +--------+---------+
                    |                  |
         +--------->|     就绪态         |<---------+
        (被唤醒)    |   (TASK_READY)    |          |(时间片用完)
        ^          +-------------------+          |
        |                                       |
        |                                       v
        |                              +--------+---------+
        |                              |                  |
        |       +--------------------->|    运行态        |
        |       |                      |  (RUNNING)      |
        |       |                      +------------------+
        |       |                               |
        |       |                               v
        |       |          +--------------------+--------------------+
        |       |          |                    |                    |
        |       |          v                    v                    v
        |       |   +------+------+      +------+------+      +--------+------+
        |       |   |             |      |             |      |               |
        +-------+   |  阻塞态      |      |  暂停态      |      |   僵死态       |
        (等待事件   | (INTERRUPT-  |      | (STOPPED)   |      |  (ZOMBIE)     |
         完成)      |  IBLE/UNINT) |      |             |      |               |
                    +-------------+      +-------------+      +---------------+
```

### 各状态含义

| 状态 | 宏定义 | 含义 |
|------|--------|------|
| 创建态 | `TASK_NEW` | 进程正在被创建，尚未准备好运行 |
| 就绪态 | `TASK_RUNNING` | 进程已准备好，等待 CPU 调度（可运行） |
| 运行态 | `TASK_RUNNING` | 进程正在 CPU 上执行 |
| 阻塞态 | `TASK_INTERRUPTIBLE` | 进程因等待事件而睡眠，可被信号唤醒 |
| 阻塞态 | `TASK_UNINTERRUPTIBLE` | 进程因等待事件而睡眠，不可被信号唤醒 |
| 暂停态 | `TASK_STOPPED` | 进程被暂停，通常由 `SIGSTOP` 信号触发 |
| 僵死态 | `EXIT_ZOMBIE` | 进程已终止，但父进程尚未调用 `wait()` 回收 |
| 僵死态 | `EXIT_DEAD` | 进程即将被完全释放 |

## 进程创建与销毁

### fork() 与 PCB

`fork()` 系统调用用于创建一个新进程。当调用 `fork()` 时，内核会执行以下 PCB 相关操作：

```c
// 简化版的 fork() 过程

// 1. 为新进程分配 PID
pid = alloc_pid();

// 2. 分配 task_struct 结构体
p = dup_task_struct(current);  // 复制父进程的 task_struct

// 3. 初始化 PCB
p->pid = pid;
p->parent = current;
p->tgid = p->pid;           // 对于主线程，TGID = PID
p->state = TASK_RUNNING;

// 4. 复制或共享资源
if (copy_mm(p))             // 复制地址空间
    goto bad_fork_cleanup_pid;

if (copy_files(p))           // 复制文件描述符
    goto bad_fork_cleanup_mm;

if (copy_sighand(p))         // 复制信号处理函数
    goto bad_fork_cleanup_files;

if (copy_signal(p))          // 复制信号
    goto bad_fork_cleanup_sighand;

// 5. 设置子进程的内核栈
setup_thread_stack(p, orig);

// 6. 将子进程加入调度队列
wake_up_new(p);

// 7. 返回子进程 PID
return p->pid;
```

### exit() 与 PCB 清理

当进程调用 `exit()` 或从 `main()` 返回时，内核会执行 PCB 清理操作：

```c
// 简化版的 exit() 过程

// 1. 设置进程状态为僵死态
set_special_state(TASK_DEAD);

// 2. 释放进程占用的资源
exit_files(p);      // 关闭打开的文件
exit_mm(p);         // 释放内存描述符
exit_sighand(p);    // 释放信号处理函数
exit_signal(p);     // 发送信号给父进程

// 3. 设置退出码
p->exit_code = code;
p->state = EXIT_ZOMBIE;

// 4. 更新父进程信息
if (p->parent != p->real_parent)
    p->parent = p->real_parent;

// 5. 将进程放入僵死态链表
list_add_tail(&p->sibling, &p->real_parent->children);

// 6. 通知调度器
schedule();

// 注意：此时 PCB 尚未释放，父进程需要调用 wait() 来回收
```

僵死态进程的 PCB 会一直保留，直到父进程调用 `wait()` 或 `wait4()` 系统调用来回收：

```c
// 父进程调用 wait() 回收子进程 PCB
do {
    ret = waitpid(pid, &status, options);
} while (ret == -ECHILD);
```

## 总结

进程控制块（PCB）是操作系统内核中最重要的数据结构之一，它完整地记录了一个进程的所有状态信息。理解 PCB 的结构和组织方式，对于理解操作系统的进程管理、调度和内存管理至关重要。

在 Linux 中，`task_struct` 结构体是 PCB 的具体实现，它包含了进程标识、调度信息、内存管理、文件描述符、信号处理等所有与进程相关的信息。通过各种链表和数据结构，内核高效地组织和管理着系统中所有的 PCB。
