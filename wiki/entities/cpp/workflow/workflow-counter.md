---
type: entity
tags: [C++异步框架, 任务控制, 信号量]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow Counter

## 定义
Counter 是一种不占线程的信号量，用于工作流控制。支持匿名计数器和命名计数器，可实现复杂的任务依赖关系。

## 关键要点
- **匿名计数器**：`create_counter_task(target_value, callback)`，通过 `counter->count()` 递增
- **命名计数器**：`create_counter_task("name", target_value, callback)`，通过 `WFTaskFactory::count_by_name("name")` 递增
- **线程安全**：`count_by_name` 可一次唤醒多个同名计数器
- **应用场景**：并行任务完成等待、全连接神经网络、异步锁

## 示例
~~~cpp
WFCounterTask *counter = WFTaskFactory::create_counter_task(url_count, counter_callback);
WFHttpTask *task = create_http_task(url, http_callback);
task->user_data = counter;
task->start();
counter->start();
// 在 http_callback 中: counter->count();
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型总览
- [[entities/cpp/workflow/workflow-conditional]] — 条件任务
- [[entities/cpp/workflow/workflow-resource-pool]] — 资源池
