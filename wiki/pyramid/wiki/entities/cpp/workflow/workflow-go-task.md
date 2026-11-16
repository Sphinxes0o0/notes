---
type: entity
tags: [C++异步框架, 计算任务, 线程池]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow Go Task

## 定义
Go Task 是模仿 Go 语言风格的计算任务（线程任务），无需定义输入输出，所有数据通过函数参数传递，可将 Workflow 当作线程池使用。

## 关键要点
- **创建**：`WFTaskFactory::create_go_task(queue_name, func, args...)`
- **参数传递**：引用参数需使用 `std::ref`，否则为值传递
- **Callback**：创建时不传 callback，通过 `set_callback()` 设置
- **带时限**：`create_timedgo_task(seconds, nanosecs, queue_name, func, args...)`
- **重置**：`WFTaskFactory::reset_go_task()` 可在创建后重置执行函数
- **队列名**：影响任务调度顺序，默认队列名可退化为线程池

## 示例
~~~cpp
WFGoTask *task = WFTaskFactory::create_go_task("test", add, a, b, std::ref(res));
task->set_callback([&](WFGoTask *task) {
    printf("%d + %d = %d\n", a, b, res);
});
task->start();
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型总览
- [[entities/cpp/workflow/workflow-module-task]] — 模块任务封装
- [[entities/cpp/workflow/workflow-counter]] — 计数器任务
