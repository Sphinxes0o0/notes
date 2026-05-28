---
type: source
source-type: pdf-book
title: Linux多线程服务端编程：使用muduo C++网络库
author: 陈硕
date: 2012
size: medium
path: raw/PDFs/books/Linux多线程服务端编程：使用muduo C++网络库.pdf
pages: 151
summary: 陈硕 muduo C++ 网络库实战：one loop per thread 模型、TCP网络编程、epoll/select/poll 多路复用、muduo 库架构设计与实现、Linux高性能服务端编程实战。
created: 2012
tags: []
---
# Linux多线程服务端编程：使用muduo C++网络库

## Metadata
- **Author:** 陈硕 (giantchen@gmail.com)
- **Published:** 2012-09-30
- **Pages:** 151
- **Topic:** Linux multi-threaded server programming, C++ networking
- **Language:** 中文

## Core Content
陈硕 muduo C++ 网络库实战指南（151页），基于 x86-64 Linux 系统。

**核心内容**：
- **one loop per thread** — 每个线程一个事件循环，最简服务端编程模型
- **TCP网络编程** — 连接管理、缓冲区、读写事件处理
- **IO多路复用** — select(2)/poll(2)/epoll(4) 对比，epoll 高性能模式
- **muduo 库架构** — 事件循环、Channel、EventLoop、Acceptor、Connection、TcpServer
- **线程安全** — mutex、condition variable、thread-local storage
- **性能优化** — 零拷贝、边缘触发 vs 水平触发、避免O(n) notify

**推荐背景**：W. Richard Stevens《UNIX网络编程》第2卷 + 《TCP/IP详解》卷1/2

## Related Pages
- [[sources/pdf-book-21st-century-cpp]] — Modern C++ books
- [[sources/pdf-book-cpp-concurrency-guide]] — C++ Concurrency in Action
- [[entities/cpp/concurrency]] — C++ 并发编程概念
- [[entities/kernel-bypass-dpdk]] — 高性能网络（kernel bypass）