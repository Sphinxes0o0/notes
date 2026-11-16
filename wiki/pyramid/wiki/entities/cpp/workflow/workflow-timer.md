---
type: entity
tags: [C++异步框架, 定时器, 延迟任务]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow Timer

## 定义
Timer 是，不占线程的定时任务，通过 callback 通知到期。支持命名定时器和取消功能。

## 关键要点
- **创建**：`create_timer_task(seconds, nanoseconds, callback)`
- **命名定时器**：`create_timer_task("name", seconds, nanoseconds, callback)`
- **取消**：`WFTaskFactory::cancel_by_name("name")`
- **程序退出**：定时器可被程序退出打断，状态为 `WFT_STATE_ABORTED`
- **纳秒精度**：nanoseconds 取值范围 [0, 10^9)

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型总览
- [[entities/cpp/workflow/workflow-conditional]] — 条件任务（配合实现延迟执行）
