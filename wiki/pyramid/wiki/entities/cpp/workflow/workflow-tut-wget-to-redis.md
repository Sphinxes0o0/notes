---
type: entity
tags: [C++异步框架, Series, 任务链, 上下文]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 03: wget_to_redis 任务链与上下文

## 定义
展示如何创建 SeriesWork 并设置上下文，实现 HTTP 抓取后存入 Redis 的任务链。

## 创建 SeriesWork
~~~cpp
SeriesWork *series = Workflow::create_series_work(http_task, series_callback);
series->set_context(&context);
series->start();
~~~

## 与 task->start() 的区别
- `task->start()`：自动创建以 task 为首的 Series
- `Workflow::create_series_work()`：手动创建，可设置 callback 和上下文

## 上下文管理
~~~cpp
struct tutorial_series_context {
    std::string http_url;
    std::string redis_url;
    size_t body_len;
    bool success;
};
// 所有任务共享上下文，通过 series_of(task)->get_context() 获取
~~~

## 任务链示例
1. 创建 HTTP 任务，设置 size_limit 和 receive_timeout
2. 创建 SeriesWork，HTTP 作为首任务
3. Series callback 中打印结果并唤醒主线程

## 相关概念
- [[entities/cpp/workflow/workflow-parallel-tasks]] — Series 与 Parallel
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端