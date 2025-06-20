# Linux 系统编程综合指南

本文档是Linux系统编程的综合指南，从基础概念到高级架构，涵盖系统调用、I/O机制、并发编程等核心主题。适合系统工程师、内核开发者以及对Linux内部机制感兴趣的开发者学习参考。

## 📋 目录

1. [系统架构简介](#1-系统架构)
2. [系统调用基础](#2-系统调用基础)
3. [Linux I/O 系统](#3-linux-io-系统)
4. [并发编程](#4-并发编程)
5. [高级特性](#5-高级特性)

---
## 1. 系统架构

### 1.1 Linux 系统分层架构

```
Linux 系统完整架构：
┌─────────────────────────────────────────────────────────┐
│                     用户空间                             │
│  ┌─────────────┬─────────────┬─────────────┐          │
│  │   应用程序   │   系统工具   │   shell     │          │
│  └─────────────┴─────────────┴─────────────┘          │
│  ┌─────────────────────────────────────────────────┐   │
│  │              C 标准库 (glibc)                   │   │
│  └─────────────────────────────────────────────────┘   │
├═════════════════════════════════════════════════════════┤ ← 用户态/内核态边界
│                     内核空间                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │              系统调用接口                        │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │                Linux 内核                       │   │
│  │  ┌─────────┬─────────┬─────────┬─────────┐     │   │
│  │  │进程管理  │内存管理  │文件系统  │网络子系统│     │   │
│  │  └─────────┴─────────┴─────────┴─────────┘     │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │            设备驱动程序                  │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↕
            ┌─────────────────────────────────┐
            │           硬件层                 │
            │  ┌──────┬──────┬──────┬──────┐ │
            │  │ CPU  │ 内存  │ 磁盘  │ 网卡  │ │
            │  └──────┴──────┴──────┴──────┘ │
            └─────────────────────────────────┘
```

### 1.2 内存管理架构

#### 1.2.1 虚拟内存布局

```
Linux 进程虚拟内存布局 (x86_64)：
┌────────────────────────────────────────────────────────┐
│ 0xFFFFFFFFFFFFFFFF                                     │ ← 内核空间起始
│ ┌────────────────────────────────────────────────────┐ │
│ │                内核空间                             │ │
│ │        (不可被用户进程直接访问)                     │ │
│ └────────────────────────────────────────────────────┘ │
│ 0x00007FFFFFFFFFFF                                     │
│ ┌────────────────────────────────────────────────────┐ │
│ │                   栈区                              │ │ ← 向下增长
│ │            ↓ (由高地址向低地址增长)                  │ │
│ └────────────────────────────────────────────────────┘ │
│                         ...                            │
│ ┌────────────────────────────────────────────────────┐ │
│ │                   堆区                              │ │ ← 向上增长
│ │            ↑ (由低地址向高地址增长)                  │ │
│ └────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────┐ │
│ │                 数据段                              │ │
│ │  ┌──────────┬──────────┐                          │ │
│ │  │ BSS段    │ 数据段    │                          │ │
│ │  └──────────┴──────────┘                          │ │
│ └────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────┐ │
│ │                 代码段                              │ │
│ │           (程序指令)                                │ │
│ └────────────────────────────────────────────────────┘ │
│ 0x0000000000400000                                     │ ← 通常的代码段起始
└────────────────────────────────────────────────────────┘
```

#### 1.2.2 页表机制

```c
// x86_64 四级页表示例
typedef struct {
    uint64_t present    : 1;   // 页面存在位
    uint64_t write      : 1;   // 写权限
    uint64_t user       : 1;   // 用户访问权限
    uint64_t pwt        : 1;   // 页级写透
    uint64_t pcd        : 1;   // 页级缓存禁用
    uint64_t accessed   : 1;   // 访问位
    uint64_t dirty      : 1;   // 脏位
    uint64_t pat        : 1;   // 页属性表
    uint64_t global     : 1;   // 全局页
    uint64_t ignored    : 3;   // 忽略位
    uint64_t address    : 40;  // 物理页帧号
    uint64_t reserved   : 11;  // 保留位
    uint64_t nx         : 1;   // 禁止执行位
} page_table_entry_t;
```

### 1.3 进程调度器架构

#### 1.3.1 调度器概述

Linux 调度器负责决定在多任务环境中哪个进程应该获得 CPU 时间。现代 Linux 采用模块化调度器架构，支持多种调度策略。

```
Linux 调度器架构演进：
┌─────────────────────────────────────────────────────────┐
│  Linux 2.6 之前: O(n) 调度器                            │
│  • 简单轮转调度                                          │
│  • 时间复杂度 O(n)                                      │
│  • 不适合大量进程                                        │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│  Linux 2.6: O(1) 调度器                                 │
│  • 固定时间复杂度 O(1)                                  │
│  • 140个优先级队列                                       │
│  • 交互进程启发式算法                                    │
└─────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────┐
│  Linux 2.6.23+: CFS (完全公平调度器)                    │
│  • 基于红黑树的 O(log n) 调度                           │
│  • 虚拟运行时间概念                                      │
│  • 更好的交互性和公平性                                  │
└─────────────────────────────────────────────────────────┘
```

#### 1.3.2 CFS 调度器详解

**CFS 核心概念**：

```c
// CFS 调度实体结构（简化版）
struct sched_entity {
    struct load_weight load;        // 进程权重
    struct rb_node run_node;        // 红黑树节点
    u64 vruntime;                   // 虚拟运行时间
    u64 prev_sum_exec_runtime;     // 累计执行时间
    u64 sum_exec_runtime;
    s64 fair_key;                   // 红黑树排序键值
};

// CFS 运行队列
struct cfs_rq {
    struct rb_root tasks_timeline;  // 红黑树根
    struct rb_node *rb_leftmost;    // 最左节点（下一个调度）
    unsigned long nr_running;       // 运行进程数
    u64 min_vruntime;              // 最小虚拟运行时间
};
```

**CFS 算法原理**：

```
CFS 调度算法流程：
┌─────────────────────────────────────────────────────────┐
│                    CFS 调度器                            │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │               红黑树结构                         │   │
│  │                                                 │   │
│  │          ○ (vruntime=100)                      │   │
│  │         ╱ ╲                                     │   │
│  │   (80) ○   ○ (150)                             │   │
│  │       ╱ ╲   ╲                                   │   │
│  │  (50)○   ○   ○(200)                           │   │
│  │                                                 │   │
│  │  最左节点 = 下一个要调度的进程                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  核心公式：                                              │
│  • vruntime = 实际运行时间 * NICE_0_LOAD / 权重         │
│  • 权重 = 1024 / (1.25 ^ nice值)                       │
│  • 时间片 = sysctl_sched_latency * 权重 / 总权重        │
│                                                         │
│  调度决策：                                              │
│  1. 选择 vruntime 最小的进程运行                        │
│  2. 进程用完时间片后重新计算 vruntime                   │
│  3. 将进程重新插入红黑树                                │
│  4. 重复步骤1                                           │
└─────────────────────────────────────────────────────────┘
```

#### 1.3.3 调度策略详解

Linux 支持多种调度策略，通过 `sched_setscheduler()` 系统调用设置：

```c
// 调度策略定义
#define SCHED_NORMAL     0  // CFS 调度器（默认）
#define SCHED_FIFO       1  // 实时FIFO调度
#define SCHED_RR         2  // 实时轮转调度  
#define SCHED_BATCH      3  // 批处理调度
#define SCHED_IDLE       5  // 空闲调度
#define SCHED_DEADLINE   6  // 截止时间调度

// 调度策略使用示例
#include <sched.h>

void set_scheduling_policy() {
    struct sched_param param;
    
    // 设置实时优先级
    param.sched_priority = 50;
    
    // 设置为实时FIFO调度
    if (sched_setscheduler(0, SCHED_FIFO, &param) == -1) {
        perror("sched_setscheduler");
    }
    
    // 获取当前调度策略
    int policy = sched_getscheduler(0);
    printf("Current policy: %d\n", policy);
}
```

**各调度策略特点**：

```
调度策略对比：
┌──────────────┬──────────────┬──────────────┬─────────────┐
│   调度策略    │   优先级范围  │   时间片     │   适用场景   │
├──────────────┼──────────────┼──────────────┼─────────────┤
│ SCHED_NORMAL │   -20~19     │   动态调整   │  普通进程   │
│ SCHED_FIFO   │   1~99       │   无限制     │ 实时系统    │
│ SCHED_RR     │   1~99       │   固定轮转   │ 实时系统    │
│ SCHED_BATCH  │   -20~19     │   较长       │ 批处理作业  │
│ SCHED_IDLE   │   0          │   最低       │ 后台任务    │
│ SCHED_DEADLINE│  动态        │   截止时间   │ 硬实时系统  │
└──────────────┴──────────────┴──────────────┴─────────────┘
```

#### 1.3.4 CPU 亲和性和 NUMA

**CPU 亲和性控制**：

```c
#define _GNU_SOURCE
#include <sched.h>

void cpu_affinity_example() {
    cpu_set_t cpuset;
    
    // 清空 CPU 集合
    CPU_ZERO(&cpuset);
    
    // 设置进程只能在 CPU 0 和 CPU 2 上运行
    CPU_SET(0, &cpuset);
    CPU_SET(2, &cpuset);
    
    // 应用 CPU 亲和性
    if (sched_setaffinity(0, sizeof(cpuset), &cpuset) == -1) {
        perror("sched_setaffinity");
    }
    
    // 查询当前 CPU 亲和性
    CPU_ZERO(&cpuset);
    if (sched_getaffinity(0, sizeof(cpuset), &cpuset) == -1) {
        perror("sched_getaffinity");
    }
    
    printf("Process can run on CPUs: ");
    for (int i = 0; i < CPU_SETSIZE; i++) {
        if (CPU_ISSET(i, &cpuset)) {
            printf("%d ", i);
        }
    }
    printf("\n");
}
```

**NUMA 感知调度**：

```
NUMA 架构下的调度优化：
┌─────────────────────────────────────────────────────────┐
│                   NUMA 节点 0                            │
│  ┌─────────┬─────────┬─────────────────────────────┐   │
│  │ CPU 0-3 │ 本地内存 │        缓存一致性           │   │
│  └─────────┴─────────┴─────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────┘
                  │ 互连总线（较慢）
┌─────────────────▼───────────────────────────────────────┐
│                   NUMA 节点 1                            │
│  ┌─────────┬─────────┬─────────────────────────────┐   │
│  │ CPU 4-7 │ 本地内存 │        缓存一致性           │   │
│  └─────────┴─────────┴─────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

调度器 NUMA 优化策略：
• 尽量将进程调度到访问本地内存的 CPU 上
• 考虑内存分配的 NUMA 节点
• 负载均衡时考虑 NUMA 拓扑
```

#### 1.3.5 调度器调优

**关键内核参数**：

```bash
# CFS 调度器参数 (/proc/sys/kernel/)
echo 6000000 > /proc/sys/kernel/sched_latency_ns          # 调度延迟
echo 750000 > /proc/sys/kernel/sched_min_granularity_ns   # 最小调度粒度
echo 1000000 > /proc/sys/kernel/sched_wakeup_granularity_ns # 唤醒抢占粒度

# 实时调度器参数
echo 950000 > /proc/sys/kernel/sched_rt_runtime_us        # 实时进程最大运行时间
echo 1000000 > /proc/sys/kernel/sched_rt_period_us        # 实时调度周期

# NUMA 相关参数
echo 1 > /proc/sys/kernel/numa_balancing                  # 启用 NUMA 平衡
```

**性能监控工具**：

```c
// 获取调度统计信息
#include <sys/resource.h>

void print_scheduling_info() {
    struct rusage usage;
    
    // 获取资源使用统计
    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        printf("User CPU time: %ld.%06ld seconds\n", 
               usage.ru_utime.tv_sec, usage.ru_utime.tv_usec);
        printf("System CPU time: %ld.%06ld seconds\n", 
               usage.ru_stime.tv_sec, usage.ru_stime.tv_usec);
        printf("Voluntary context switches: %ld\n", usage.ru_nvcsw);
        printf("Involuntary context switches: %ld\n", usage.ru_nivcsw);
    }
}
```

**调度器性能分析**：

```bash
# 使用 perf 分析调度器性能
perf record -e sched:sched_switch -e sched:sched_wakeup ./my_program
perf script | head -20

# 查看调度器统计信息
cat /proc/schedstat

# 实时查看进程调度信息
perf top -e cycles -s comm,dso
```

---

## 2. 系统调用基础

### 2.1 系统调用概述

系统调用是用户空间程序与内核交互的唯一接口，它提供了一种安全、可控的方式来访问系统资源。

#### 系统调用的关键特性

* **特权级切换**：系统调用将处理器从用户态切换到内核态，以便 CPU 访问受保护的内核内存
* **标准化接口**：系统调用的组成是固定的，每个系统调用都由一个唯一的数字来标识
* **参数传递**：每个系统调用可辅以一套参数，规范用户空间与内核空间之间的信息传递

### 2.2 系统调用执行机制

以 x86-64 架构为例，系统调用的执行过程：

```
系统调用执行流程：
┌─────────────────────────────────────────────────────────┐
│                     用户空间                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │            应用程序                              │   │
│  │         ┌─────────────┐                         │   │
│  │         │ open(...)   │                         │   │
│  │         └─────────────┘                         │   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │ 1. 调用库函数                      │
│  ┌─────────────────▼───────────────────────────────┐   │
│  │            glibc 包装函数                        │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │ 2. 参数准备和寄存器设置              │   │   │
│  │  │ 3. 系统调用号设置 (%rax)               │   │   │
│  │  │ 4. 执行 syscall 指令                  │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────┬───────────────────────────────┘   │
└────────────────────┼───────────────────────────────────┘
                     │ 5. 模式切换
┌────────────────────▼───────────────────────────────────┐
│                     内核空间                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │           系统调用处理程序                       │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │ 6. 保存用户态寄存器                  │   │   │
│  │  │ 7. 验证系统调用号                    │   │   │
│  │  │ 8. 调用具体的系统调用服务例程        │   │   │
│  │  │ 9. 执行实际操作                      │   │   │
│  │  │ 10. 恢复寄存器，返回用户态           │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.3 现代系统调用优化

#### VDSO (Virtual Dynamic Shared Object)
```c
// 某些系统调用通过 VDSO 优化，避免模式切换
#include <time.h>
#include <sys/time.h>

int main() {
    struct timespec ts;
    
    // 这个调用可能通过 VDSO 直接在用户空间执行
    clock_gettime(CLOCK_REALTIME, &ts);
    
    return 0;
}
```

---

## 3. Linux I/O 系统

Linux I/O 系统是操作系统的核心组成部分，从简单的文件操作到复杂的网络通信，都离不开高效的 I/O 机制。

### 3.1 文件 I/O 基础

#### 3.1.1 文件描述符概念

在 Unix/Linux 系统中，所有 I/O 操作都通过文件描述符进行抽象。文件描述符是一个非负整数，用于标识进程打开的文件、管道、socket、设备等。

```
进程文件描述符表示例：
┌─────────────────────────────────────────┐
│ 进程 A 文件描述符表                     │
├─────────┬───────────────────────────────┤
│   FD    │          指向的资源            │
├─────────┼───────────────────────────────┤
│    0    │ 标准输入 (stdin)              │
│    1    │ 标准输出 (stdout)             │
│    2    │ 标准错误 (stderr)             │
│    3    │ /home/user/data.txt           │
│    4    │ socket (TCP连接)              │
│    5    │ 管道 (pipe)                   │
│   ...   │ ...                           │
└─────────┴───────────────────────────────┘
```

#### 3.1.2 基本文件操作

**open() - 打开/创建文件**：
```c
#include <fcntl.h>
int open(const char *pathname, int flags, mode_t mode);

// 示例
int fd = open("data.txt", O_RDWR | O_CREAT, 0644);
if (fd == -1) {
    perror("open");
    return -1;
}
```

**读写操作的完整示例**：
```c
// 安全读取函数，处理短读和信号中断
ssize_t safe_read(int fd, void *buf, size_t count) {
    ssize_t total_read = 0;
    char *ptr = (char *)buf;
    
    while (total_read < count) {
        ssize_t bytes_read = read(fd, ptr + total_read, count - total_read);
        
        if (bytes_read == -1) {
            if (errno == EINTR) continue;  // 信号中断，重试
            return -1;  // 真正的错误
        }
        
        if (bytes_read == 0) break;  // EOF
        total_read += bytes_read;
    }
    
    return total_read;
}
```

### 3.2 I/O 缓冲机制

#### 3.2.1 缓冲架构层次

```
I/O 缓冲层次架构：
┌─────────────────────────────────────────────────────────┐
│                   用户应用程序                           │
├─────────────────────────────────────────────────────────┤
│                  stdio 缓冲层                           │ ← 用户态缓冲
│    ┌─────────────┬─────────────┬─────────────┐         │   (glibc)
│    │ FILE *stdin │ FILE *stdout│ FILE *stderr│         │
│    └─────────────┴─────────────┴─────────────┘         │
├═════════════════════════════════════════════════════════┤ ← 用户态/内核态边界
│                 系统调用接口                             │
├─────────────────────────────────────────────────────────┤
│                   VFS 层                               │ ← 虚拟文件系统
├─────────────────────────────────────────────────────────┤
│                 Page Cache                             │ ← 内核页缓存
├─────────────────────────────────────────────────────────┤
│                Buffer Cache                            │ ← 块设备缓存
├─────────────────────────────────────────────────────────┤
│                   块I/O层                              │ ← I/O调度和合并
├─────────────────────────────────────────────────────────┤
│                  设备驱动层                             │ ← 硬件驱动
└─────────────────────────────────────────────────────────┘
```

#### 2.2.2 不同I/O方式的数据路径

**传统 Buffered I/O**：
```
应用程序 ←─ 内存拷贝 ←─ Page Cache ←─ DMA ←─ 磁盘
数据拷贝次数：2次
优点：缓存效果好，适合重复访问
缺点：额外的内存拷贝开销
```

**内存映射 (mmap)**：
```
应用程序 ←─ 虚拟内存映射 ←─ Page Cache ←─ DMA ←─ 磁盘
数据拷贝次数：0次（用户空间视角）
优点：零拷贝，高效随机访问
缺点：页面fault开销，内存占用
```

### 2.3 I/O 模型深入

#### 2.3.1 五种 I/O 模型

```
I/O 模型分类：
┌─────────────────────────────────────────────────┐
│                同步 I/O                         │
│  ┌─────────────┬─────────────┬─────────────┐   │
│  │   阻塞I/O   │  非阻塞I/O  │  I/O复用    │   │
│  │ (Blocking)  │(Non-block.) │(Multiplexing)│   │
│  └─────────────┴─────────────┴─────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │          信号驱动I/O                    │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│                异步 I/O                         │
│  ┌─────────────────────────────────────────┐   │
│  │           异步I/O                       │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

#### 3.3.2 高性能 I/O：epoll 示例

```c
#include <sys/epoll.h>

#define MAX_EVENTS 1024

int epoll_server_example(int port) {
    int server_fd, epoll_fd;
    struct epoll_event event, events[MAX_EVENTS];
    
    // 创建服务器socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    // ... 绑定和监听 ...
    
    // 创建epoll实例
    epoll_fd = epoll_create1(0);
    
    // 添加服务器socket到epoll
    event.events = EPOLLIN;
    event.data.fd = server_fd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, server_fd, &event);
    
    // 事件循环
    while (1) {
        int nready = epoll_wait(epoll_fd, events, MAX_EVENTS, -1);
        
        for (int i = 0; i < nready; i++) {
            if (events[i].data.fd == server_fd) {
                // 处理新连接
                int client_fd = accept(server_fd, NULL, NULL);
                event.events = EPOLLIN | EPOLLET; // 边缘触发
                event.data.fd = client_fd;
                epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &event);
            } else {
                // 处理客户端数据
                handle_client(events[i].data.fd);
            }
        }
    }
    
    return 0;
}
```

### 3.4 现代 I/O 技术

#### 3.4.1 io_uring

```c
#include <liburing.h>

// 现代异步 I/O 示例
int io_uring_example() {
    struct io_uring ring;
    struct io_uring_sqe *sqe;
    struct io_uring_cqe *cqe;
    
    // 初始化 io_uring
    io_uring_queue_init(32, &ring, 0);
    
    // 准备异步读取操作
    sqe = io_uring_get_sqe(&ring);
    io_uring_prep_read(sqe, fd, buffer, size, offset);
    
    // 提交操作
    io_uring_submit(&ring);
    
    // 等待完成
    io_uring_wait_cqe(&ring, &cqe);
    
    // 处理结果
    if (cqe->res < 0) {
        printf("Error: %s\n", strerror(-cqe->res));
    }
    
    io_uring_cqe_seen(&ring, cqe);
    io_uring_queue_exit(&ring);
    
    return 0;
}
```

---

## 4. 并发编程

### 4.1 线程编程基础

#### 4.1.1 线程vs进程

```
进程与线程对比：
┌────────────────┬──────────────────┬──────────────────┐
│    特征        │      进程         │      线程         │
├────────────────┼──────────────────┼──────────────────┤
│  内存空间      │     独立         │      共享         │
│  创建开销      │      大          │       小         │
│  切换开销      │      大          │       小         │
│  通信方式      │  IPC(管道,共享内存)│   共享变量       │
│  崩溃影响      │     隔离         │   相互影响        │
└────────────────┴──────────────────┴──────────────────┘
```

#### 4.1.2 线程同步机制

**互斥锁示例**：
```c
#include <pthread.h>

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
int shared_counter = 0;

void* thread_function(void* arg) {
    for (int i = 0; i < 10000; i++) {
        pthread_mutex_lock(&mutex);
        shared_counter++;  // 临界区
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

int main() {
    pthread_t threads[4];
    
    // 创建4个线程
    for (int i = 0; i < 4; i++) {
        pthread_create(&threads[i], NULL, thread_function, NULL);
    }
    
    // 等待所有线程完成
    for (int i = 0; i < 4; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("Final counter: %d\n", shared_counter);  // 应该是40000
    return 0;
}
```

### 4.2 生产者-消费者模型

```c
#include <pthread.h>
#include <semaphore.h>

#define BUFFER_SIZE 10

typedef struct {
    int buffer[BUFFER_SIZE];
    int in, out;
    pthread_mutex_t mutex;
    sem_t empty, full;
} bounded_buffer_t;

bounded_buffer_t bb = {
    .in = 0, .out = 0,
    .mutex = PTHREAD_MUTEX_INITIALIZER
};

void buffer_init() {
    sem_init(&bb.empty, 0, BUFFER_SIZE);  // 初始时缓冲区为空
    sem_init(&bb.full, 0, 0);             // 初始时没有数据
}

void* producer(void* arg) {
    for (int i = 0; i < 20; i++) {
        int item = i;
        
        sem_wait(&bb.empty);              // 等待空槽
        pthread_mutex_lock(&bb.mutex);
        
        bb.buffer[bb.in] = item;          // 放入数据
        bb.in = (bb.in + 1) % BUFFER_SIZE;
        printf("Produced: %d\n", item);
        
        pthread_mutex_unlock(&bb.mutex);
        sem_post(&bb.full);               // 通知有数据
    }
    return NULL;
}

void* consumer(void* arg) {
    for (int i = 0; i < 20; i++) {
        sem_wait(&bb.full);               // 等待数据
        pthread_mutex_lock(&bb.mutex);
        
        int item = bb.buffer[bb.out];     // 取出数据
        bb.out = (bb.out + 1) % BUFFER_SIZE;
        printf("Consumed: %d\n", item);
        
        pthread_mutex_unlock(&bb.mutex);
        sem_post(&bb.empty);              // 通知有空槽
    }
    return NULL;
}
```

---

## 5. 高级特性

### 5.1 内核同步机制

#### 5.1.1 RCU (Read-Copy-Update)

```c
// RCU 机制示例
struct my_data {
    int value;
    struct rcu_head rcu;
};

struct my_data *global_ptr;

// 读者 (无锁)
void reader_function() {
    struct my_data *ptr;
    
    rcu_read_lock();
    ptr = rcu_dereference(global_ptr);
    if (ptr) {
        // 使用 ptr->value
        printf("Value: %d\n", ptr->value);
    }
    rcu_read_unlock();
}

// 写者 (需要同步)
void writer_function(int new_value) {
    struct my_data *new_ptr, *old_ptr;
    
    new_ptr = kmalloc(sizeof(*new_ptr), GFP_KERNEL);
    new_ptr->value = new_value;
    
    spin_lock(&my_lock);
    old_ptr = global_ptr;
    rcu_assign_pointer(global_ptr, new_ptr);
    spin_unlock(&my_lock);
    
    synchronize_rcu();  // 等待所有读者完成
    kfree(old_ptr);     // 安全释放旧数据
}
```

### 5.2 性能优化技术

#### 5.2.1 Zero-Copy 技术

```c
// sendfile: 零拷贝文件传输
#include <sys/sendfile.h>

ssize_t zero_copy_file_transfer(int out_fd, int in_fd, size_t count) {
    return sendfile(out_fd, in_fd, NULL, count);
}

// splice: 管道间零拷贝
#include <fcntl.h>

ssize_t pipe_zero_copy(int fd_in, int fd_out, size_t len) {
    int pipefd[2];
    pipe(pipefd);
    
    // 数据从 fd_in 拷贝到管道
    ssize_t bytes = splice(fd_in, NULL, pipefd[1], NULL, len, SPLICE_F_MOVE);
    
    // 数据从管道拷贝到 fd_out
    splice(pipefd[0], NULL, fd_out, NULL, bytes, SPLICE_F_MOVE);
    
    close(pipefd[0]);
    close(pipefd[1]);
    
    return bytes;
}
```

---

## 📚 补充资料

### libc & glibc

**GNU C Library (glibc)** 是 Linux 系统的标准 C 库实现：

- **系统调用包装**：提供对系统调用的高级接口
- **标准函数**：实现 C 标准库函数（malloc、printf 等）
- **线程支持**：提供 POSIX 线程实现
- **国际化**：支持多语言和地区设置

### 存储器层次结构

```
存储器金字塔（访问速度从快到慢）：
        ┌─────────────┐
        │    寄存器    │ ← ~1 周期
        ├─────────────┤
        │  L1 Cache   │ ← ~4 周期
        ├─────────────┤
        │  L2 Cache   │ ← ~10 周期  
        ├─────────────┤
        │  L3 Cache   │ ← ~40 周期
        ├─────────────┤
        │    内存     │ ← ~200 周期
        ├─────────────┤
        │    SSD      │ ← ~25,000 周期
        ├─────────────┤
        │   机械硬盘   │ ← ~20,000,000 周期
        └─────────────┘
```

这种层次结构的存在是现代计算机系统中缓存、内存管理等技术的理论基础。

---

## 🎯 学习建议

1. **基础优先**：先掌握系统调用和基本 I/O 操作
2. **实践验证**：通过编程实验验证理论知识
3. **性能意识**：关注不同方案的性能特点和适用场景
4. **源码学习**：阅读相关的内核源码加深理解
5. **工具使用**：熟练使用 strace、perf、gdb 等调试工具

通过系统学习这些内容，可以建立起对 Linux 系统编程的全面认识，为开发高性能、可靠的系统应用奠定坚实基础。
