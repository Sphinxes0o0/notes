---
type: source
tags: [cpp, concurrency, multithreading, parallel, memory-model, cpp11, cpp17, cpp20]
source-type: pdf
created: 2026-05-23
sources: [pdf-cpp-concurrency]
title: "C++ Concurrency Books (2 volumes)"
author: "Rainer Grimm, Anthony Williams"
date: 2023
size: large
path: raw/PDFs/books/
summary: "两册 C++ 并发编程深度指南：Concurrency with Modern C++（Rainer Grimm 中文版）、C++ Concurrency in Action（Anthony Williams 中文翻译）"
---

# C++ Concurrency Books

## 1. Concurrency with Modern C++ (中文翻译)

**作者**: Rainer Grimm | **页数**: 480

从 C++11 到 C++20 的并发编程全面指南。涵盖内存模型、原子操作、线程管理、锁、条件变量、任务和并行算法。

### 核心主题
- 内存模型基础（memory ordering、happens-before）
- 原子操作与同步原语
- 栅栏 (Fences)
- 线程管理与共享数据
- 条件变量与任务
- 标准库并行算法与执行策略
- C++20 新特性：可协作中断线程、原子智能指针、闩锁/栅栏、协程、事务性内存
- 并发模式：活动对象、监控对象、半同步/半异步
- 有锁与无锁数据结构
- CppMem 工具分析

## 2. C++ Concurrency In Action (中文翻译)

**作者**: Anthony Williams | **译者**: 陈晓伟 | **页数**: 528

C++ 并发编程领域经典之作。从 std::thread 基础到内存模型和原子操作，再到无锁数据结构和高级线程管理。

### 核心主题
- 你好，C++ 的并发世界
- 线程管理（启动、等待、分离）
- 线程间共享数据（互斥量、死锁）
- 同步并发操作（条件变量、future、promise）
- C++ 内存模型和原子类型操作
- 基于锁的并发数据结构设计
- 无锁并发数据结构设计
- 并发代码设计
- 高级线程管理（线程池、工作窃取）
- 多线程程序测试和调试

## 相关页面

- [[entities/cpp/concurrency]] — C++ 并发编程概念（线程、mutex、atomic、future）
- [[entities/cpp/cpp20-features]] — C++20 Coroutines & 并发增强
- [[entities/c/c-language]] — C 语言内存模型基础
- [[entities/cpp/cpp-stl-iterators]] — 迭代器与并行算法
- [[entities/cpp/move-semantics]] — 移动语义与线程间数据传输
- [[entities/cpp/smart-pointers]] — 原子智能指针
- [[cpp-index]] — C++ 模块导航
