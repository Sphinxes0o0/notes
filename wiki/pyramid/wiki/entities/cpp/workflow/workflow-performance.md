---
type: entity
tags: [C++异步框架, 性能优化]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 性能

## 定义

Sogou Workflow 性能相关概念汇总，包括 QPS 极限、延时特性、并发模型等。

## 关键指标

- **500K QPS**：最佳数据长度（64B/512B）下的极限吞吐量
- **低延时**：p99 延时优于 nginx，持平 brpc
- **线性扩展**：poller threads 配置影响吞吐

## 相关概念

- [[entities/cpp/workflow/workflow-benchmark]] — 官方性能测试详情
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
- [[entities/cpp/workflow/workflow-benchmark-design]] — Benchmark 设计文档
