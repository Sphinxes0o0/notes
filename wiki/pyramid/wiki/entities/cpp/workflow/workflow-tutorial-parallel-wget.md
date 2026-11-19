---
type: entity
tags: [C++异步框架, Parallel, 并行任务, 多URL抓取]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 06: Parallel Wget

## 概述
`tutorial-06-parallel_wget` 展示如何使用 ParallelWork 实现并行抓取多个 URL。

## 创建并行任务
~~~cpp
ParallelWork *pwork = Workflow::create_parallel_work(callback);
for (url : urls) {
    WFHttpTask *task = create_http_task(url, callback);
    SeriesWork *series = Workflow::create_series_work(task, nullptr);
    series->set_context(ctx);
    pwork->add_series(series);
}
pwork->start();
~~~

## 接口
- `pwork->add_series(series)` 添加并行分支
- `pwork->size()` 获取分支数
- `pwork->series_at(i)` 获取第 i 个分支

## Callback 中获取结果
~~~cpp
void callback(const ParallelWork *pwork) {
    for (size_t i = 0; i < pwork->size(); i++) {
        ctx = pwork->series_at(i)->get_context();
        // 处理 ctx->resp
    }
}
~~~

## 数据共享
每个 series 有独立 context，用于保存各自的抓取结果。

## 相关概念
- [[entities/cpp/workflow/workflow-parallel-tasks]] — Parallel 和 Series 详解
- [[entities/cpp/workflow/workflow-resource-pool]] — 另一种并发控制方式