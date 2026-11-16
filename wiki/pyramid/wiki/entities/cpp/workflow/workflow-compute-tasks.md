---
type: entity
tags: [C++异步框架, 计算任务, 算法工厂, Sort, Matrix]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 计算任务

## 定义
计算任务（或线程任务）用于执行 CPU 密集型计算，不在 callback 中执行，避免阻塞。

## 内置算法
- **排序**：`WFAlgoTaskFactory::create_sort_task()` / `create_psort_task()`
- **矩阵乘法**：自定义 routine
- **并行排序**：分块 + 二路归并，O(1) 空间复杂度

## 自定义计算任务
~~~cpp
struct Input { ... };
struct Output { ... };

void routine(const Input *in, Output *out) { ... }

using MyTask = WFThreadTask<Input, Output>;
MyTask *task = WFThreadTaskFactory<Input, Output>::create_thread_task(
    "queue_name", routine, callback);
~~~

## 带时限任务
~~~cpp
create_thread_task(seconds, nanoseconds, queue_name, routine, callback);
~~~

## 队列名
- 影响任务调度顺序
- 默认为 CPU 核数线程
- 配置：`settings.compute_threads`

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
- [[entities/cpp/workflow/workflow-go-task]] — Go Task
