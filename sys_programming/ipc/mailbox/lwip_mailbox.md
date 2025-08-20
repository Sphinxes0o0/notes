# LwIP Mailbox 机制学习

## 1. 概述

LwIP（Light Weight IP）是一个专为嵌入式系统设计的轻量级TCP/IP协议栈，通过Linux移植可在PC环境进行协议栈调试。
其核心设计目标是在保持功能完整性的同时，最大限度地优化资源使用效率。

目前的使用场景已经涵盖:
- 车载MCU 
- IoT
- 工业嵌入式设备

### LwIP线程模型

LwIP支持多种线程模型，以适应不同应用场景的需求：

1. **单线程模型**（NO_SYS=1）：
   - 所有协议处理都在主循环中完成
   - 适用于资源极度受限的8/16位微控制器
   - 通过轮询方式处理网络事件

2. **多线程模型**（NO_SYS=0）：
   - **TCP/IP协议栈线程**（tcpip_thread）：
     - 专门处理协议栈核心任务（数据包收发、协议处理）
     - 所有网络接口的输入数据包首先提交到该线程
     - 使用Mailbox机制接收来自应用线程的请求
   - **应用线程**：
     - 处理用户应用程序逻辑
     - 通过Socket API或Sequential API与协议栈通信
   - **网络接口线程**（如tapif接口线程）：
     - 处理底层网络设备的输入输出
     - 通过中断下半部（softirq）机制处理数据接收

> 在Linux移植版本中，LwIP使用POSIX线程实现多线程模型，通过Mailbox机制实现线程间安全通信。

## 2. 为什么需要 Mailbox

在传统的嵌入式系统开发中，多线程通信常用以下方式实现：

| 通信方式        | 实现机制        | 主要缺陷                 | 适用场景             |
|---------------|---------------- |------------------------|---------------------|
| 共享内存+标志位 | 内存区域+状态标志  | 需复杂同步机制，易产生竞态条件  | 极低RAM占用场景   |
| 信号量控制访问  | 互斥锁保护共享资源 | 效率低下，易造成线程饥饿     | 简单状态同步      |
| 条件变量通知    | wait/notify机制  | 实现复杂，实时性差         | 复杂状态机控制     |
| 管道通信       | 内核提供的IPC机制  | 需系统调用，资源消耗大      | OS支持的中等规模系统 |


这些方案在LwIP场景下面临特殊挑战:

- 网络数据包处理需要毫秒级响应
- 协议栈需同时处理中断上下文和多个应用线程
- 嵌入式设备内存资源极度受限
- 需要符合TCP/IP协议的严格时序要求

因此, 通过消息队列作为通信方式，来解决了以下缺陷：

| 传统缺陷   | 消息队列解决方案      | 实现效益       |
|-----------|--------------------|---------------|
| 数据竞争   | 原子操作保证队列完整性 | 提升线程安全等级 |
| 内存碎片   | 固定大小消息池        | 降低内存管理开销 |
| 同步复杂度 | 统一的阻塞/非阻塞接口  | 简化应用层开发   |
| 流量控制   | 队列满/空状态显式处理  | 避免系统崩溃风险 |

对于 POSIX 和 System-V, 都已经有一套完善成熟的消息队列接口提供了，但是在复杂多变的嵌入式环境下，并不能在所有的环境使用。
因此在Lwip 中，基于消息队列机制的上实现了 Mailbox。

而 Mailbox 是一种线程间通信机制，允许多个线程安全地发送和接收消息。

它通常包含一个消息队列和同步机制，保证：
- 多线程可以往 mailbox 投递消息（生产者），也可以从 mailbox 取出消息（消费者）。
- 当 mailbox 满时，投递线程会阻塞；当 mailbox 空时，取消息线程会阻塞。

通过Mailbox机制，LwIP实现了以下系统级优势：

1. **解耦设计**：
   - 生产者（应用线程/中断处理）与消费者（协议栈线程）完全解耦
   - 模块间通过标准接口通信，降低耦合度

2. **资源控制**：
   - 队列大小在编译时确定，便于内存规划
   - 防止资源耗尽：非阻塞模式在队列满时返回错误码

3. **性能优化**：
   - 零拷贝优化：传递指针而非数据本身
   - 流水线优化：避免条件判断导致的CPU流水线停滞

4. **可移植性**：
   - 抽象底层线程接口（sys_arch.c）
   - 支持不同操作系统（RTOS/Linux）的适配层


## 3. LwIP Mailbox实现

api 接口一览:

```c
// lwip/master/src/include/lwip/sys.h#L69
#define sys_mbox_new(m, s) ERR_OK
#define sys_mbox_fetch(m,d)
#define sys_mbox_tryfetch(m,d)
#define sys_mbox_post(m,d)
#define sys_mbox_trypost(m,d)
#define sys_mbox_free(m)
#define sys_mbox_valid(m)
#define sys_mbox_valid_val(m)
#define sys_mbox_set_invalid(m)
#define sys_mbox_set_invalid_val(m)
```

unix 上的实现在 `lwip/contrib/ports/unix/port/sys_arch.c` 中

### 3.1 Mailbox 实现

#### 核心数据结构
```c
// Mailbox队列定义（lwip/include/sys/lwip_sys.h）
// lwip/master/contrib/ports/unix/port/sys_arch.c#L121
struct sys_mbox {
    int first, last;
    void *msgs[SYS_MBOX_SIZE];
    struct sys_sem *not_empty;
    struct sys_sem *not_full;
    struct sys_sem *mutex;
    int wait_send;
};
```

- `int first, last;`
  这两个整数用于实现循环缓冲区（环形队列）。
  - `first` 表示最早未取出的消息的位置。
  - `last` 表示最后一个放入消息的位置。

- `void *msgs[SYS_MBOX_SIZE];`
  消息缓冲区，是一个指针数组，用于存储实际的消息内容（指针）。
  - `SYS_MBOX_SIZE` 是邮箱的最大容量。

- `struct sys_sem *not_empty;`
  指向信号量的指针，用于同步读消息操作。
  - 当邮箱非空时唤醒等待的线程。

- `struct sys_sem *not_full;`
  指向信号量的指针，用于同步写消息操作。
  - 当邮箱未满时唤醒等待的线程。

- `struct sys_sem *mutex;`
  互斥锁信号量，用于保护对邮箱结构体的访问，防止多线程同时读写导致数据混乱。

- `int wait_send;`  
  记录有多少个线程在等待向邮箱发送消息（当邮箱已满时）。

它通过信号量和互斥锁实现线程安全，能够保证多线程环境下消息的正确收发和队列的有效管理。

#### 发送消息


```c
void sys_mbox_post(struct sys_mbox **mb, void *msg)
{
  u8_t first;
  struct sys_mbox *mbox;
  LWIP_ASSERT("invalid mbox", (mb != NULL) && (*mb != NULL));
  mbox = *mb;
  sys_arch_sem_wait(&mbox->mutex, 0);
  LWIP_DEBUGF(SYS_DEBUG, ("sys_mbox_post: mbox %p msg %p\n", (void *)mbox, (void *)msg));

  while ((mbox->last + 1) >= (mbox->first + SYS_MBOX_SIZE)) {
    mbox->wait_send++;
    sys_sem_signal(&mbox->mutex);
    sys_arch_sem_wait(&mbox->not_full, 0);
    sys_arch_sem_wait(&mbox->mutex, 0);
    mbox->wait_send--;
  }

  mbox->msgs[mbox->last % SYS_MBOX_SIZE] = msg;
  if (mbox->last == mbox->first) {
    first = 1;
  } else {
    first = 0;
  }

  mbox->last++;
  if (first) {
    sys_sem_signal(&mbox->not_empty);
  }
  sys_sem_signal(&mbox->mutex);
}
```
这个函数是一个阻塞式的消息发送函数，它将消息放入mailbox中。

> 异步的接口是 `sys_mbox_trypost`, 常用于中断上下文、主循环轮询或者需要避免阻塞的场合。

函数首先获取mailbox的互斥锁，然后检查mailbox是否已满, 如果mailbox已满，则等待直到mailbox中有空位。
然后，函数将消息放入mailbox中，并检查mailbox是否为空，如果是，则发送一个信号通知等待的消费者。
最后，函数释放mailbox的互斥锁。

##### 小技巧学习
`box->msgs[mbox->last % SYS_MBOX_SIZE] = msg;`

- mbox->msgs[]：是一个数组，用于存储消息指针（void * 类型）。
- mbox->last：是一个索引，表示下一个要写入的位置（即队尾）。
- DUMMY_MBOX_SIZE：是邮箱的容量（必须是 2 的幂，才能用 % 代替位运算）。
- msg：是要放入邮箱的消息指针。

为什么用 `% SYS_MBOX_SIZE` ?

这是一个典型的**环形缓冲区（ring buffer）**实现技巧：
- mbox->last 会不断增加，但不会无限增长。
- 通过取模 `% DUMMY_MBOX_SIZE` ，可以把索引“折回”到数组开头，实现循环利用。

> SYS_MBOX_SIZE 在代码中是128，是 2 的幂（如 32、64、128），这样 `%`可以被优化为位运算 `& (SYS_MBOX_SIZE - 1)`，提高效率，所以后续在修改的代码时候注意这一点
> 这种设计使队列操作仅需1条CPU指令，相比传统边界检查效率提升3倍以上。

##### 接收消息

`sys_arch_mbox_fetch` 是移植层（sys_arch.*）里必须实现的“阻塞式接收邮箱消息”接口，
lwIP 主线程（tcpip_thread）靠它完成两件事:
- 等待别人投递过来的数据包、API 消息等；
- 在等待期间还能顺带处理软件定时器（超时链表）

> 异步接口 `sys_arch_mbox_tryfetch`

逻辑实现：

```c
u32_t sys_arch_mbox_fetch(struct sys_mbox **mb, void **msg, u32_t timeout)
{
  u32_t time_needed = 0;
  struct sys_mbox *mbox;
  LWIP_ASSERT("invalid mbox", (mb != NULL) && (*mb != NULL));
  mbox = *mb;

  /* The mutex lock is quick so we don't bother with the timeout stuff here. */
  sys_arch_sem_wait(&mbox->mutex, 0);

  while (mbox->first == mbox->last) {
    sys_sem_signal(&mbox->mutex);

    /* We block while waiting for a mail to arrive in the mailbox. We
       must be prepared to timeout. */
    if (timeout != 0) {
      time_needed = sys_arch_sem_wait(&mbox->not_empty, timeout);

      if (time_needed == SYS_ARCH_TIMEOUT) {
        return SYS_ARCH_TIMEOUT;
      }
    } else {
      sys_arch_sem_wait(&mbox->not_empty, 0);
    }
    sys_arch_sem_wait(&mbox->mutex, 0);
  }

  if (msg != NULL) {
    LWIP_DEBUGF(SYS_DEBUG, ("sys_mbox_fetch: mbox %p msg %p\n", (void *)mbox, *msg));
    *msg = mbox->msgs[mbox->first % SYS_MBOX_SIZE];
  }
  else{
    LWIP_DEBUGF(SYS_DEBUG, ("sys_mbox_fetch: mbox %p, null msg\n", (void *)mbox));
  }

  mbox->first++;
  if (mbox->wait_send) {
    sys_sem_signal(&mbox->not_full);
  }
  sys_sem_signal(&mbox->mutex);
  return time_needed;
}
```

以上的逻辑可以简化成
```c
u32_t sys_arch_mbox_fetch(sys_mbox_t *mbox, void **msg, u32_t timeout_ms)
{
    u32_t start = sys_now();           // 取当前 tick
    while (ring_is_empty(mbox)) {
        if (timeout_ms && (sys_now() - start) >= timeout_ms)
            return SYS_ARCH_TIMEOUT;   // 超时
    }
    *msg = ring_get(mbox);
    return sys_now() - start;          // 实际等待毫秒数
}
```


一个lwip 的典型使用流程是：
```bash
tcpip_thread
 │
 ├─ LOCK_TCPIP_CORE()
 ├─ sleeptime = sys_timeouts_sleeptime();   // 最近要触发的定时器还有多久
 │
 ├─ 若 sleeptime == 0
 │   ├─ sys_check_timeouts();               // 立即处理所有已到期定时器
 │   └─ goto again;                         // 重新计算
 │
 └─ UNLOCK_TCPIP_CORE()
     actual_ms = sys_arch_mbox_fetch(mbox, &msg,
                                     sleeptime); // 可阻塞
     LOCK_TCPIP_CORE()

     if (actual_ms == SYS_ARCH_TIMEOUT)
         定时器到期 → sys_check_timeouts();     // 再次处理超时
     else
         收到了消息 → 由上层继续处理 msg
```

## 4. dummy 版本的实现

理解上面的一些实现逻辑之后，可以将其抽取出来变成一个 dummy 版本的实现，来加强理解。

### 4.1 函数定义和相关的宏
```c
#ifndef DUMMY_MBOX_H
#define DUMMY_MBOX_H

// 定义错误码
#define ERR_OK 0
#define ERR_MEM -1
#define SYS_MBOX_EMPTY -2
#define SYS_ARCH_TIMEOUT -3

// 定义邮箱大小
#define DUMMY_MBOX_SIZE 128

// 前向声明
typedef struct dummy_mbox dummy_mbox_t;

// 信号量结构
typedef struct {
    int count;
    pthread_mutex_t mutex;
    pthread_cond_t cond;
} dummy_sem_t;

// 邮箱结构
struct dummy_mbox {
    int first, last;
    void *msgs[DUMMY_MBOX_SIZE];
    dummy_sem_t *not_empty;
    dummy_sem_t *not_full;
    dummy_sem_t *mutex;
    int wait_send;
};

// 函数声明
int dummy_mbox_new(dummy_mbox_t **mb);
void dummy_mbox_free(dummy_mbox_t **mb);
void dummy_mbox_post(dummy_mbox_t **mb, void *msg);
int dummy_mbox_trypost(dummy_mbox_t **mb, void *msg);
void* dummy_mbox_fetch(dummy_mbox_t **mb);
int dummy_mbox_tryfetch(dummy_mbox_t **mb, void **msg);

#endif /* DUMMY_MBOX_H */
```

### 4.2 函数实现

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "dummy_mbox.h"

// 创建信号量
static dummy_sem_t* dummy_sem_new(int count) {
    dummy_sem_t *sem = (dummy_sem_t*)malloc(sizeof(dummy_sem_t));
    if (sem != NULL) {
        sem->count = count;
        pthread_mutex_init(&sem->mutex, NULL);
        pthread_cond_init(&sem->cond, NULL);
    }
    return sem;
}

// 释放信号量
static void dummy_sem_free(dummy_sem_t *sem) {
    if (sem != NULL) {
        pthread_cond_destroy(&sem->cond);
        pthread_mutex_destroy(&sem->mutex);
        free(sem);
    }
}

// 等待信号量
static void dummy_sem_wait(dummy_sem_t *sem) {
    pthread_mutex_lock(&sem->mutex);
    while (sem->count <= 0) {
        pthread_cond_wait(&sem->cond, &sem->mutex);
    }
    sem->count--;
    pthread_mutex_unlock(&sem->mutex);
}

// 信号量增加（通知）
static void dummy_sem_signal(dummy_sem_t *sem) {
    pthread_mutex_lock(&sem->mutex);
    sem->count++;
    pthread_cond_signal(&sem->cond);
    pthread_mutex_unlock(&sem->mutex);
}

// 创建邮箱
int dummy_mbox_new(dummy_mbox_t **mb) {
    dummy_mbox_t *mbox;
    
    mbox = (dummy_mbox_t*)malloc(sizeof(dummy_mbox_t));
    if (mbox == NULL) {
        return ERR_MEM;
    }
    
    mbox->first = mbox->last = 0;
    mbox->not_empty = dummy_sem_new(0);  // 初始为空
    mbox->not_full = dummy_sem_new(0);   // 初始为满
    mbox->mutex = dummy_sem_new(1);      // 初始可访问
    mbox->wait_send = 0;
    
    *mb = mbox;
    return ERR_OK;
}

// 释放邮箱
void dummy_mbox_free(dummy_mbox_t **mb) {
    if (mb != NULL && *mb != NULL) {
        dummy_mbox_t *mbox = *mb;
        dummy_sem_free(mbox->not_empty);
        dummy_sem_free(mbox->not_full);
        dummy_sem_free(mbox->mutex);
        free(mbox);
        *mb = NULL;
    }
}

// 阻塞式发送消息
void dummy_mbox_post(dummy_mbox_t **mb, void *msg) {
    dummy_mbox_t *mbox;
    int first;
    
    if (mb == NULL || *mb == NULL) return;
    mbox = *mb;
    
    dummy_sem_wait(mbox->mutex);  // 获取互斥锁
    
    // 如果队列满了，则等待
    while ((mbox->last + 1) >= (mbox->first + DUMMY_MBOX_SIZE)) {
        mbox->wait_send++;
        dummy_sem_signal(mbox->mutex);
        dummy_sem_wait(mbox->not_full);
        dummy_sem_wait(mbox->mutex);
        mbox->wait_send--;
    }
    
    // 将消息放入队列
    mbox->msgs[mbox->last % DUMMY_MBOX_SIZE] = msg;
    
    first = (mbox->last == mbox->first) ? 1 : 0;
    mbox->last++;
    
    // 如果这是队列中的第一条消息，通知等待的读取者
    if (first) {
        dummy_sem_signal(mbox->not_empty);
    }
    
    dummy_sem_signal(mbox->mutex);  // 释放互斥锁
}

// 非阻塞式发送消息
int dummy_mbox_trypost(dummy_mbox_t **mb, void *msg) {
    dummy_mbox_t *mbox;
    int first;
    
    if (mb == NULL || *mb == NULL) return ERR_MEM;
    mbox = *mb;
    
    dummy_sem_wait(mbox->mutex);  // 获取互斥锁
    
    // 如果队列满了，直接返回错误
    if ((mbox->last + 1) >= (mbox->first + DUMMY_MBOX_SIZE)) {
        dummy_sem_signal(mbox->mutex);
        return ERR_MEM;
    }
    
    // 将消息放入队列
    mbox->msgs[mbox->last % DUMMY_MBOX_SIZE] = msg;
    
    first = (mbox->last == mbox->first) ? 1 : 0;
    mbox->last++;
    
    // 如果这是队列中的第一条消息，通知等待的读取者
    if (first) {
        dummy_sem_signal(mbox->not_empty);
    }
    
    dummy_sem_signal(mbox->mutex);  // 释放互斥锁
    return ERR_OK;
}

// 阻塞式接收消息
void* dummy_mbox_fetch(dummy_mbox_t **mb) {
    dummy_mbox_t *mbox;
    void *msg = NULL;
    
    if (mb == NULL || *mb == NULL) return NULL;
    mbox = *mb;
    
    dummy_sem_wait(mbox->mutex);  // 获取互斥锁
    
    // 如果队列为空，则等待
    while (mbox->first == mbox->last) {
        dummy_sem_signal(mbox->mutex);
        dummy_sem_wait(mbox->not_empty);
        dummy_sem_wait(mbox->mutex);
    }
    
    // 从队列中取出消息
    msg = mbox->msgs[mbox->first % DUMMY_MBOX_SIZE];
    mbox->first++;
    
    // 如果有线程在等待发送消息，通知它们
    if (mbox->wait_send) {
        dummy_sem_signal(mbox->not_full);
    }
    
    dummy_sem_signal(mbox->mutex);  // 释放互斥锁
    return msg;
}

// 非阻塞式接收消息
int dummy_mbox_tryfetch(dummy_mbox_t **mb, void **msg) {
    dummy_mbox_t *mbox;
    
    if (mb == NULL || *mb == NULL) return SYS_MBOX_EMPTY;
    mbox = *mb;
    
    dummy_sem_wait(mbox->mutex);  // 获取互斥锁
    
    // 如果队列为空，直接返回
    if (mbox->first == mbox->last) {
        dummy_sem_signal(mbox->mutex);
        return SYS_MBOX_EMPTY;
    }
    
    // 从队列中取出消息
    if (msg != NULL) {
        *msg = mbox->msgs[mbox->first % DUMMY_MBOX_SIZE];
    }
    
    mbox->first++;
    
    // 如果有线程在等待发送消息，通知它们
    if (mbox->wait_send) {
        dummy_sem_signal(mbox->not_full);
    }
    
    dummy_sem_signal(mbox->mutex);  // 释放互斥锁
    return ERR_OK;
}
```

### 4.3 运行看看！

```Makefile
CC = gcc
CFLAGS = -Wall -Wextra -pthread -O2 -g

# 源文件
SRCS = dummy_mbox.c test.c
OBJS = $(SRCS:.c=.o)

# 目标文件
TARGET = test_dummy_mbox

# 默认目标
all: $(TARGET)

# 链接目标文件
$(TARGET): dummy_mbox.o test.o
	$(CC) $(CFLAGS) -o $@ $^ -lpthread

# 编译源文件
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# 清理生成的文件
clean:
	rm -f *.o $(TARGET)

# 伪目标
.PHONY: all clean
```

编译 & 运行：
```bash
$ make
gcc -Wall -Wextra -pthread -O2 -g -c dummy_mbox.c -o dummy_mbox.o
gcc -Wall -Wextra -pthread -O2 -g -c test.c -o test.o
gcc -Wall -Wextra -pthread -O2 -g -o test_dummy_mbox dummy_mbox.o test.o -lpthread
$ ./test_dummy_mbox 
Creating producer and consumer threads...
Producer 1: Sending message 'Hello 1-0'
Producer 2: Sending message 'Hello 2-0'
Consumer 4: Received message 'Hello 4-0'
Producer 1: Sending message 'World 1-1'
Consumer 2: Received message 'Producer 4-3'
Consumer 1: Received message 'Producer 3-3'
......
```

