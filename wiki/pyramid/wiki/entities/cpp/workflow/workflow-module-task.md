---
type: entity
tags: [C++异步框架, 模块封装, 任务组合]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow Module Task

## 定义
Module Task 是模块级封装，将多个任务封装为一个任务，降低模块间 task 耦合。

## 关键要点
- **创建**：`WFTaskFactory::create_module_task(first_task, callback)`
- **内部结构**：包含一个 `sub_series` 用于运行模块内任务
- **数据传递**：通过 `series->set_context()` 在模块内传递数据
- **封装目的**：最后一个 task 的 callback 衔接下一个任务，或填写 server resp，不合理

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型总览
- [[entities/cpp/workflow/workflow-go-task]] — Go Task
