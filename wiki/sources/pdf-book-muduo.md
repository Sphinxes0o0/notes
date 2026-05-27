---
type: source
source-type: pdf
title: "Linux多线程服务端编程：使用muduo C++网络库"
author: "陈硕"
date: 2012
size: small
path: raw/PDFs/books/Linux多线程服务端编程：使用muduo C++网络库.pdf
summary: "muduo 网络库设计：C++ 多线程/ Reactor 模式/TimerQueue/并发服务器"
---

# Linux多线程服务端编程（muduo）

## 核心内容

- **muduo 架构**：EventLoop + Channel + Poller 单 Reactor 模型
- **定时器**：TimerQueue、红码时间轮、时间戳处理
- **并发模型**：one loop per thread、跨线程调用、ThreadPool
- **TcpConnection**：生命期管理、EOF 处理、Half-close
- **Buffer 设计**：RingBuffer、input/output buffer、与fd同步
- **日志**：异步日志、roll file、log level
- **测试**：单元测试、Google Test、mock

## 相关页面
- [[pdf-book-linux-net-server]]
- [[pdf-book-concurrency-modern-cpp]]
- [[pdf-linux-sysprog]]