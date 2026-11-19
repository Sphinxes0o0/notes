---
type: entity
tags: [C++异步框架, 程序退出]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 程序退出

## 定义
框架使用非阻塞异步调用，需要遵循特定规则确保程序安全退出。

## 安全退出原则
1. 所有任务运行到 callback，且无新任务被调起
2. 所有 server 必须 stop 完成
3. 不在 callback 中调用 `exit()`

## 原子任务
以下任务可被程序退出打断，提前来到 callback：
- DNS cache 命中的 HTTP 任务
- 定时器任务
- 单线程计算/文件IO任务

## OpenSSL 内存泄露
某些 OpenSSL 1.1.x 版本退出时有内存泄露，解决方案：
~~~cpp
OPENSSL_init_ssl(0, NULL); // 在框架初始化前调用
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
