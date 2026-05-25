---
type: entity
tags: [C++异步框架, 性能测试, 性能对比]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 性能测试

## 定义
Sogou Workflow 与 nginx、brpc 的 HTTP Server 性能对比测试结果。

## 测试环境
- CPU：40 Cores x86_64 Intel Xeon E5-2630 v4
- Memory：192GB
- NIC：25000Mbps
- RTT：~0.1ms

## 测试结果
- **QPS**：64KB 数据长下可达 500K QPS
- **延时**：同等条件下优于 nginx，略好于或相当 brpc
- **高并发**：QPS 随并发度提高后趋于平稳

## 结论
在 HTTP Server 场景下，Sogou Workflow 性能优异，高于 nginx，持平或优于 brpc。

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
