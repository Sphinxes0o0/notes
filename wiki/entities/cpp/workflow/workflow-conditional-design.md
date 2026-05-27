---
type: entity
tags: [C++异步框架, Sogou, 任务模型, 条件任务]
created: 2026-05-27
sources: [raw/workflow/about-conditional]
---

# Conditional 设计概念

## 定义

Conditional（WFConditional）是 Workflow 的任务包装器，用于实现**条件触发**场景：任务在收到 signal 信号后才开始执行，而非立即执行。

## 核心特性

- 包装任意 SubTask，延迟执行
- 支持通过 `signal()` 手动触发
- 支持**观察者模式**：命名条件任务可通过 `signal_by_name()` 批量唤醒

## 创建与使用

~~~cpp
// 创建条件任务
WFConditional *cond = WFTaskFactory::create_conditional(task);

// 信号触发
cond->signal(msg);
~~~

## 观察者模式

~~~cpp
// 创建命名条件任务
WFConditional *cond = WFTaskFactory::create_conditional("slot_name", task);

// 批量唤醒所有 "slot_name" 下的条件任务
WFTaskFactory::signal_by_name("slot_name", msg);
~~~

## 注意事项

- 已收到 signal 的条件任务不能 dismiss
- 命名条件任务的 dismiss 需要特别小心

## 相关页面

- [[entities/cpp/workflow/workflow-conditional]] — Conditional 任务类型
- [[entities/cpp/workflow/workflow-timer]] — Timer 定时器
- [[entities/cpp/workflow/workflow-selector]] — Selector 多选一
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
