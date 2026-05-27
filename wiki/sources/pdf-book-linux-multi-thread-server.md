---
type: source
source-type: pdf
title: "Linux多线程服务端编程：使用muduo C++网络库"
author: "陈硕"
date: 2012
size: medium
path: raw/PDFs/books/Linux多线程服务端编程：使用muduo C++网络库.pdf
summary: "陈硕muduo库作者，讲解one-loop-per-thread模型与现代C++多线程网络编程"
---

# Linux多线程服务端编程：使用muduo C++网络库

## 核心内容

陈硕（giantchen）著作，以 muduo 网络库为示例讲解现代 C++ 多线程 TCP 服务器：

- **one-loop-per-thread**：每线程一个 event loop 的编程模型
- **现代 C++** 编写高性能多线程网络程序
- **muduo 库**的设计与实现剖析
- 线程同步原语（mutex、条件变量等）的正确使用
- 进程间通信与分布式服务架构

## 关键要点

- 核心模型：掌握一种多线程服务器编程模型即可应对日常开发
- 同步原语不必多：两种基本同步原语满足所有多线程同步需求
- 作者背景：曾任职 Morgan Stanley 外汇交易系统开发

## 相关页面
- [[pdf-book-cpp-concurrency-guide]]
- [[pdf-book-concurrency-modern-cpp]]
- [[pdf-book-linux-high-perf-server]]
- [[pdf-the-linux-programming-interface]]