---
type: entity
tags: [linux-kernel, 进程间通信, IPC, 消息队列, 信号量, 共享内存, mqueue]
created: 2026-05-20
sources: [notes-overview-kernel-ipc]
---

# Linux Kernel IPC Subsystem

## 定义

Linux内核进程间通信子系统，提供消息队列（msg）、信号量（sem）、共享内存（shm）、POSIX消息队列（mqueue）四种SysV IPC机制，支持同一主机内进程间高效数据交换。

## 关键要点

### IPC类型对比

| 类型 | 机制 | 特点 |
|------|------|------|
| msg | 消息队列 | 消息有类型，可按类型筛选 |
| sem | 信号量数组 | 原子操作，支持undo机制 |
| shm | 共享内存 | 高效的内存共享，mmap接口 |
| mqueue | POSIX队列 | 基于ramfs的通知机制 |

### 消息队列 (msg)

**核心结构**:
- msg_queue: 队列主体（q_messages, q_senders, q_receivers）
- msg_msg: 单条消息（m_type, m_ts, m_list）
- msg_sender/receiver: 等待的发送/接收进程

**关键函数**:
- newque(): 创建新队列
- do_msgsnd(): 发送消息
- do_msgrcv(): 接收消息

**特性**:
- 管道化发送: 有等待接收者时直接传递消息
- 阻塞/非阻塞: IPC_NOWAIT标志控制

### 信号量 (sem)

**核心结构**:
- sem_array: 信号量数组（sems[]）
- sem_queue: 等待队列
- sem_undo: 进程退出时自动撤销

**原子操作**:
- perform_atomic_semop(): 两阶段验证后执行
- SEM_UNDO: 进程退出时自动回滚调整值

**细粒度锁定**:
- 单信号量操作: spin_lock(&sem->lock)
- 多信号量操作: 全局锁
- use_global_lock标志优化

### 共享内存 (shm)

**核心结构**:
- shmid_kernel: 共享内存描述符
- shm_file: 底层文件（shmem或hugetlb）

**关键函数**:
- newseg(): 创建共享内存段
- do_shmat(): 映射到进程地址空间
- do_shm_rmid(): 销毁（nattch=0时）

**特性**:
- HUGETLB: 大页共享内存
- mmap接口: 进程直接访问

### POSIX消息队列 (mqueue)

**核心结构**:
- mqueue_inode_info: 队列inode信息
- msg_tree: 红黑树管理消息（按优先级）
- ext_wait_queue: 等待队列条目

**关键特性**:
- 红黑树: 按优先级存储消息，O(log n)查找
- 通知机制: SIGEV_NONE/SIGNAL/THREAD三种模式
- 管道化操作: 直接传递消息给等待者

### 通用框架 (util.c)

**kern_ipc_perm**: 所有IPC对象的基础结构
- lock: 对象锁
- key: 键值
- idr: IDR树管理ID

**关键API**:
- ipc_addid(): 添加新IPC对象
- ipc_rmid(): 移除IPC对象
- ipc_lock_object(): 锁定单个对象
- ipcget(): 统一获取IPC对象

### 源码位置

| 组件 | 路径 |
|------|------|
| msg | ipc/msg.c |
| sem | ipc/sem.c |
| shm | ipc/shm.c |
| mqueue | ipc/mqueue.c |
| util | ipc/util.c |

## 相关概念
- [[entities/os/os-process-thread]] — 进程与线程
- [[entities/linux/kernel/mm/linux-kernel-mm-mmap]] — mmap接口

## 来源详情
- [[sources/notes-kernel-ipc]]
