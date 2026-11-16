---
type: entity
tags: [C++异步框架, Series, 任务链, 上下文]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 03: Wget to Redis

## 概述
`tutorial-03-wget_to_redis` 展示 Series 任务链的创建、上下文设置，以及程序的优雅退出。

## 核心概念
- **SeriesWork**：串行任务链，所有任务按顺序执行
- **创建**：`Workflow::create_series_work(task, callback)`
- **启动**：`series->start()`
- **上下文**：`series->set_context(ctx)` 设置共享数据

## 关键代码
~~~cpp
SeriesWork *series = Workflow::create_series_work(http_task, series_callback);
series->set_context(&context);
series->start();
~~~

## 超时配置
- `set_size_limit()` 限制响应大小
- `set_receive_timeout()` 接收数据超时（毫秒）

## 程序退出
任务都在同一个 series 里，series 完成后自动回调，无需 Ctrl-C。

## 相关概念
- [[entities/cpp/workflow/workflow-parallel-tasks]] — Parallel 和 Series
- [[entities/cpp/workflow/workflow-http-server]] — HTTP Server
- [[entities/cpp/workflow/workflow-exit-handling]] — 程序退出机制