---
type: source
source-type: pdf
title: "Linux高性能服务器编程"
author: "游双"
date: 2013
size: medium
path: raw/PDFs/books/Linux高性能服务器编程.pdf
summary: "Linux 高性能网络编程：I/O 模型/多进程多线程/TCP/UDP/高性能服务器架构"
---

# Linux高性能服务器编程

## 核心内容

- **I/O 模型**：阻塞/非阻塞/多路复用(epoll/select/poll)/SIGIO/SO_REUSEPORT
- **进程与线程**：fork/clone/pthread、进程池、线程池
- **信号处理**：SIGCHLD/SIGPIPE/统一事件源
- **TCP**：三次握手/四次挥手、Nagle算法/TCP_NODELAY、HeartBeat
- **UDP**：connect/自有协议、组播编程
- **高性能服务器**：半同步/半异步模型、有限状态机、 reactor/proactor
- **进程间通信**：共享内存、消息队列、Unix Domain Socket
- **libevent 示例**：echo server、聊天室实战代码

## 相关页面
- [[pdf-linux-net-server]]
- [[pdf-book-muduo]]
- [[pdf-unix-environment-advanced-programming]]