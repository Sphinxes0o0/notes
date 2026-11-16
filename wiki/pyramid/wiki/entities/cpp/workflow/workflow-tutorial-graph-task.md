---
type: entity
tags: [C++异步框架, Graph, DAG, 任务依赖]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 11: Graph Task

## 概述
`tutorial-11-graph_task` 展示如何创建有向无环图（DAG）来实现复杂的任务依赖关系。

## 创建图任务
~~~cpp
WFGraphTask *graph = WFTaskFactory::create_graph_task(graph_callback);
WFGraphNode& a = graph->create_graph_node(timer);
WFGraphNode& b = graph->create_graph_node(http_task1);
WFGraphNode& c = graph->create_graph_node(http_task2);
WFGraphNode& d = graph->create_graph_node(go_task);
~~~

## 建立依赖
~~~cpp
a --> b;  // timer 完成后执行 http1
a --> c;  // timer 完成后执行 http2
b --> d;  // http1 完成后执行 go
c --> d;  // http2 完成后执行 go
~~~

等价写法：
~~~cpp
a --> b --> d;
a --> c --> d;
// 或
d <-- b <-- a;
d <-- c <-- a;
~~~

## DAG 图示
```
        +-------+          +-------+
  +---->| Http1 |--------->|  Go   |
  |     +-------+          +-------+
+-------+
| Timer |
+-------+
  |     +-------+          +-------+
  +---->| Http2 |--------->|  Go   |
        +-------+          +-------+
```

## 取消后继节点
~~~cpp
void callback(WFHttpTask *t) {
    if (t->get_state() != WFT_STATE_SUCCESS)
        series_of(t)->cancel();  // 递归取消所有后继节点
}
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
- [[entities/cpp/workflow/workflow-parallel-tasks]] — Parallel/Series