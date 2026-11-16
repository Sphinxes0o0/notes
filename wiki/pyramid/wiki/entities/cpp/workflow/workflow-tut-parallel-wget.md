---
type: entity
tags: [C++异步框架, Parallel, 并行任务, 并发]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 06: parallel_wget 并行任务

## 定义
展示如何创建 ParallelWork 并行抓取多个 URL。

## 创建并行任务
~~~cpp
ParallelWork *pwork = Workflow::create_parallel_work(callback);
for (url : urls) {
    WFHttpTask *task = create_http_task(url, ...);
    SeriesWork *series = Workflow::create_series_work(task, nullptr);
    pwork->add_series(series);
}
pwork->start();
~~~

## ParallelWork 接口
- `create_parallel_work(callback)`：创建空并行任务
- `add_series(series)`：添加串行任务链
- `size()`：获取 series 数量
- `series_at(i)`：获取第 i 个 series

## 保存结果
~~~cpp
void callback(const ParallelWork *pwork) {
    for (i = 0; i < pwork->size(); i++) {
        ctx = (Context *)pwork->series_at(i)->get_context();
        // 处理结果
    }
}
~~~

## 关键点
- HTTP 任务不能直接加入 ParallelWork，需要先包装为 Series
- ParallelWork 是一种任务，可放入其他 series
- 结果顺序与放入顺序一致

## 相关概念
- [[entities/cpp/workflow/workflow-parallel-tasks]] — 并行任务
- [[entities/cpp/workflow/workflow-counter]] — 计数器实现更复杂依赖