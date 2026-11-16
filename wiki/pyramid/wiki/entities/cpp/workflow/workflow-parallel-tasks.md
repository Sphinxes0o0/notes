---
type: entity
tags: [C++异步框架, 并行任务, Parallel, Series]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 并行任务

## 定义
Workflow 支持并行任务（Parallel）和串行任务链（Series），可组合成任意复杂的工作流。

## Series（串行任务链）
- **创建**：`Workflow::create_series_work(task, callback)`
- **特性**：所有任务按顺序执行
- **启动**：`series->start()` 或 `task->start()`（自动创建 Series）

## Parallel（并行任务）
- **创建**：`Workflow::create_parallel_work(callback)`
- **添加**：`pwork->add_series(series)`
- **获取**：`pwork->size()`、`pwork->series_at(i)`

## 示例：并行抓取
~~~cpp
ParallelWork *pwork = Workflow::create_parallel_work(callback);
for (url : urls) {
    WFHttpTask *task = create_http_task(url, ...);
    SeriesWork *series = Workflow::create_series_work(task, nullptr);
    pwork->add_series(series);
}
pwork->start();
~~~

## 数据共享
- 通过 `series->set_context(ctx)` 设置上下文
- 通过 `series_of(task)->get_context()` 获取上下文

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
- [[entities/cpp/workflow/workflow-counter]] — 计数器实现更复杂依赖
