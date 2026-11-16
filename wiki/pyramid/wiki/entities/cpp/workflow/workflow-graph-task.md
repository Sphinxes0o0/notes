---
type: entity
tags: [C++异步框架, DAG, 有向无环图]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow Graph Task

## 定义
Graph Task 用于创建有向无环图（DAG），实现复杂的任务依赖关系。

## 关键要点
- **创建图任务**：`WFTaskFactory::create_graph_task(callback)`
- **创建节点**：`graph->create_graph_node(task)` 返回节点引用
- **建立依赖**：使用 `-->` 或 `<--` 运算符
- **取消后继**：`series->cancel()` 递归取消节点的所有后继
- **数据传递**：节点间无统一数据传递机制，需用户自行解决

## DAG 示例
~~~
            +-------+
      +---->| Http1 |-----+
      |     +-------+     |
 +-------+              +-v--+
 | Timer |              | Go |
 +-------+              +-^--+
      |     +-------+     |
      +---->| Http2 |-----+
            +-------+
~~~
~~~cpp
a-->b; a-->c; b-->d; c-->d; // 依赖建立
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型总览
- [[entities/cpp/workflow/workflow-parallel-tasks]] — 并行任务
