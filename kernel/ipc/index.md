# Linux IPC 子系统文档索引

## 文档

| 文档 | 描述 | 源码位置 |
|------|------|----------|
| [ipc_subsystem.md](ipc_subsystem.md) | IPC: msg, sem, shm, mqueue | ipc/ |
| [ipc_deep_dive_r1.md](ipc_deep_dive_r1.md) | 深度分析 R1: msg算法, sem undo, shm mmap, mqueue | ipc/ |

---

## 主要内容

### 1. 消息队列 (msg)
- struct msg_queue: 消息队列
- do_msgsnd(): 发送消息
- do_msgrcv(): 接收消息

### 2. 信号量 (sem)
- struct sem_array: 信号量数组
- perform_atomic_semop(): 原子操作
- sem_undo: 退出时撤销

### 3. 共享内存 (shm)
- struct shmid_kernel: 共享内存
- newseg(): 创建共享内存
- do_shmat(): 映射共享内存

### 4. POSIX 消息队列 (mqueue)
- struct mqueue_inode_info: mqueue inode
- mq_open(): 打开队列
- 通知机制: SIGEV_NONE/SIGNAL/THREAD

---

## 关键源码位置

| 组件 | 路径 |
|------|------|
| msg | ipc/msg.c |
| sem | ipc/sem.c |
| shm | ipc/shm.c |
| mqueue | ipc/mqueue.c |
| util | ipc/util.c |
