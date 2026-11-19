---
type: entity
tags: [C++异步框架, 文件IO, 异步文件, Linux aio]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 09: HTTP File Server

## 概述
`tutorial-09-http_file_server` 展示如何使用 Workflow 的异步文件 IO 功能实现 HTTP 文件服务器。

## 异步文件 IO
- **Linux**：使用原生 aio，CPU 占用极低
- **其他系统**：多线程实现
- **注意**：需将完整文件读入内存，不适合大文件传输

## 创建文件任务
~~~cpp
// 通过 fd 创建
WFFileIOTask *pread_task = WFTaskFactory::create_pread_task(
    fd, buf, size, offset, pread_callback);

// 通过路径创建
WFFileIOTask *pread_task = WFTaskFactory::create_pread_task(
    path, buf, size, offset, pread_callback);
~~~

## 处理请求
~~~cpp
int fd = open(abs_path.c_str(), O_RDONLY);
size_t size = lseek(fd, 0, SEEK_END);
void *buf = malloc(size);

WFFileIOTask *pread_task = WFTaskFactory::create_pread_task(
    fd, buf, size, 0, pread_callback);
pread_task->user_data = resp;
server_task->user_data = buf;

series_of(server_task)->push_back(pread_task);
~~~

## Repeater 任务
使用 `WFRepeaterTask` 实现命令行交互循环：
~~~cpp
WFRepeaterTask *repeater = WFTaskFactory::create_repeater_task(
    create_fn, callback);
repeater->start();
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-http-server]] — HTTP Server
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型