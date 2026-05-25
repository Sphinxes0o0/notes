---
type: entity
tags: [C++异步框架, 资源池, 消息队列, 并发控制]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow Resource Pool

## 定义
资源池用于限制并发度、任务串行化、资源复用。消息队列是类似的消息传递组件。

## 关键要点
- **资源池**：
  - `WFResourcePool(size_t n)` 或 `WFResourcePool(res_array, n)`
  - `pool.get(task)` 获取资源，任务在执行时才尝试获得
  - `pool.post(res)` 归还资源
  - 默认 FILO，可派生实现 FIFO
- **消息队列**：
  - `WFMessageQueue()` 长度不受限制
  - `mq.get(task)` 获取消息，`mq.post(msg)` 发送消息
  - 先进先出，无需先获取再归还
- **应用场景**：
  - 并发度限制
  - 任务串行化
  - DNS 并发控制

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型总览
- [[entities/cpp/workflow/workflow-counter]] — 计数器
- [[entities/cpp/workflow/workflow-service-governance]] — 服务治理
