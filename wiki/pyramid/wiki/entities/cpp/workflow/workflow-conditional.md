---
type: entity
tags: [C++异步框架, 条件任务, 观察者模式]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow Conditional

## 定义
Conditional（条件任务）是一种任务包装器，包装任意任务，通过 `signal()` 触发执行。支持观察者模式（命名条件任务）。

## 关键要点
- **创建**：`WFTaskFactory::create_conditional(task)` 或 `create_conditional("name", task)`
- **触发**：`cond->signal(msg)` 或 `WFTaskFactory::signal_by_name("name", msg)`
- **观察者模式**：`signal_by_name` 可同时唤醒所有同名条件任务
- **dismiss 限制**：已被 signal 的条件任务不能 dismiss
- **应用**：延迟执行、观察者模式、异步触发

## 示例
~~~cpp
WFGoTask *task = WFTaskFactory::create_go_task("test", [](){ printf("Done\n"); });
WFConditional *cond = WFTaskFactory::create_conditional(task);
WFTimerTask *timer = WFTaskFactory::create_timer_task(1, 0, [cond](void *){
    cond->signal(NULL);
});
timer->start();
cond->start();
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型总览
- [[entities/cpp/workflow/workflow-timer]] — 定时器
- [[entities/cpp/workflow/workflow-counter]] — 计数器
