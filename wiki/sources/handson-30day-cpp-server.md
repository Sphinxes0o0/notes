---
type: source
source-type: github
title: "30天自制C++服务器"
author: "yuesong-feng"
date: 2024-01-01
summary: "30天从socket到Reactor多线程服务器：epoll/Channel/EventLoop/Connection/线程池，学完能看懂muduo"
path: raw/github/yuesong-feng/30dayMakeCppServer
---

# 30天自制C++服务器

## 核心内容

### 渐进式课程（16天+）

| Day | Topic | 关键点 |
|-----|-------|--------|
| 1-2 | Socket 编程 | bind/listen/accept/connect，错误处理 |
| 3 | Epoll 基础 | epoll_create/ctl/wait，LT vs ET 模式 |
| 4-5 | 事件驱动架构 | Channel 类、EventLoop、REACTOR 模式 |
| 6-7 | TCP 连接管理 | Connection 类、半关闭、keep-alive |
| 8 | 缓冲区设计 | Buffer 类、自动扩容环形缓冲区 |
| 9-10 | 线程池 | 任务队列、worker 线程、锁竞争优化 |
| 11-16 | Reactor 多线程 | Master-Slave Reactor、fd 迁移、负载均衡 |

### 架构设计

```
Acceptor → EventLoop → Channel → Connection → Buffer
                                         ↓
                                   ThreadPool
```

### 关键类设计
- **Channel**：封装 fd + events，负责注册/更新/删除事件
- **EventLoop**：事件循环核心，`epoll_wait` 驱动
- **Connection**：TCP 连接抽象，管理 socket fd + 业务逻辑
- **Buffer**：读写缓冲区，`iovec` 优化减少 copy

### 教学目标
> "学完本教程后，你将会很轻松地看懂 muduo 源码"

## 相关页面

- [[load-balancing]] — 服务器高并发架构基础
- [[distributed-systems]] — 多线程服务器的分布式扩展
- [[sys]] — Linux 系统编程（socket/epoll）
- [[cpp-concurrency-action]] — C++ 并发编程（线程池、锁）

## 来源详情

- GitHub: [yuesong-feng/30dayMakeCppServer](https://github.com/yuesong-feng/30dayMakeCppServer)
- Star: 7k+，Fork: 882
- 语言：C++ 67.9%, Python 21.9%, CMake 8.9%
