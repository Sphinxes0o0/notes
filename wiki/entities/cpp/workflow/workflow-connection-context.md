---
type: entity
tags: [C++异步框架, 连接上下文, 连接状态]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 连接上下文

## 定义
连接上下文允许将一段数据与连接绑定，用于维护连接状态。适用于 Redis SELECT、MySQL 连接状态等。

## 关键要点
- **获取连接**：`task->get_connection()`（仅在 process 或 callback 中）
- **操作接口**：
  - `conn->get_context()` / `conn->set_context(context, deleter)`
  - `conn->test_set_context()` 处理并发问题
- **安全使用**：推荐只在 server task 的 `process()` 函数内访问
- **应用**：HTTP Keep-Alive cookie 优化、Redis/MySQL 连接状态

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
