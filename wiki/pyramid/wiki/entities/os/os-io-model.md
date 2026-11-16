---
type: entity
tags: [linux-kernel, I/O模型, select, poll, epoll, 网络]
created: 2026-05-20
sources: [notes-os-fundamentals]
---

# Linux I/O 模型

## 定义

Linux 提供 select/poll/epoll 三种 I/O 多路复用机制，将网卡缓冲区数据到达的事件通知给应用进程，实现高并发网络服务。

## 关键要点

- **Socket 缓冲区**: DMA 将网卡数据拷贝到环形缓冲区（Buffer），协议栈处理后形成 Socket 文件
- **Socket 编程模型**: 服务端 Socket 绑定 IP:端口，accept 拿到客户端 Socket fd，read/write 读写数据
- **select/poll**: 线性结构存储关注的 Socket 集合，内核遍历判断事件；`FD_SETSIZE` 默认 1024 上限
- **poll**: 优化编程模型（事件数组），但性能与 select 相当（线性遍历）
- **epoll**: 红黑树存储关注的 Socket（Key=fd，值=事件类型），内核 O(log n) 查找；ready 队列返回事件
- **阻塞 vs 非阻塞**: 阻塞触发线程阻塞状态切换；非阻塞立即返回
- **同步 vs 异步**: 同步调用保证执行顺序；异步调用通过回调处理结果
- **epoll 优势**: 红黑树减少内核比较操作；非阻塞模型更易编程

## 对比

| 特性 | select/poll | epoll |
|------|-------------|-------|
| 数据结构 | 线性数组 | 红黑树 |
| 查找复杂度 | O(n) | O(log n) |
| 并发上限 | FD_SETSIZE (1024) | 无硬上限 |
| 阻塞模型 | 阻塞 | 非阻塞 |
| 适用场景 | 低并发 | 高并发 |

## 相关概念

- [[entities/os/linux-scheduler]] — I/O 阻塞触发进程调度状态变化
- [[entities/os/os-process-thread]] — 网络 I/O 处理涉及多线程并发

## 来源详情

- [[sources/notes-os-fundamentals]]
