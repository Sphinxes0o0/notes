---
type: entity
tags: [C++异步框架, 任务模型, Series/Parallel]
created: 2026-05-25
sources: [workflow-engine]
---

# Sogou Workflow 异步任务模型

## 定义
Sogou Workflow 是一个 C++ 异步编程框架，核心是基于任务（Task）的有向无环图（DAG）执行模型，支持串行（Series）和并行（Parallel）任务编排。

## 关键要点
- **任务类型**：网络任务（HTTP/Redis/MySQL/Kafka/DNS）、计算任务（Go Task/Sort/Matrix）、文件IO任务、Timer任务、Counter任务
- **SeriesWork**：串行任务链，所有任务按顺序执行
- **ParallelWork**：并行任务组，多个 Series 并发执行
- **WFGraphTask**：DAG 任务，支持复杂依赖关系
- **工厂模式**：所有任务通过 `WFTaskFactory` 或专用工厂类创建，永不返回 NULL
- **非阻塞**：所有 `start()` 操作非阻塞，callback 机制通知完成

## 核心概念
- [[entities/cpp/workflow/workflow-go-task]] — Go 风格计算任务
- [[entities/cpp/workflow/workflow-counter]] — 计数器任务（信号量机制）
- [[entities/cpp/workflow/workflow-timer]] — 定时器任务
- [[entities/cpp/workflow/workflow-selector]] — 多选一选择器任务
- [[entities/cpp/workflow/workflow-conditional]] — 条件任务（观察者模式）
- [[entities/cpp/workflow/workflow-module-task]] — 模块任务封装
- [[entities/cpp/workflow/workflow-graph-task]] — DAG 图任务
- [[entities/cpp/workflow/workflow-resource-pool]] — 资源池与消息队列

## 来源详情
- [[sources/workflow-engine]]
