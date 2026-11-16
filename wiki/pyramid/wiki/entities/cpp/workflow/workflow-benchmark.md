---
type: entity
tags: [C++异步框架, 性能测试, benchmark, QPS]
created: 2026-05-25
updated: 2026-05-27
sources: [workflow-engine]
---

# Workflow 性能测试

## 定义
Workflow 官方性能测试对比，在 HTTP Server 场景下与 nginx、brpc 进行了 benchmark。

## 测试环境
- CPU: 40 Cores, Intel Xeon E5-2630 v4 @ 2.20GHz
- Memory: 192GB
- NIC: 25000Mbps
- OS: CentOS 7.8, Linux 3.10
- RTT: ~0.1ms

## 测试工具
- wrk / wrk2：QPS 极限和延时分布
- 自研压测工具（开发中）

## 测试结果

### QPS 表现
- **500K QPS**：64/512 字节响应，并发度足够时
- **优于 nginx**：所有测试场景均领先
- **持平或优于 brpc**：在延时分布测试中相当

### 延时表现
- 数据长度固定时，延时随并发度上升略有增长
- 并发度固定时，延时随数据长度增长
- 整体优于 nginx，大部优于 brpc

### 慢请求场景
- QPS=20K/100K/200K 下，延时 CDF
- 200K QPS 时略优于 brpc

## 关键发现
- **poller_threads=16**：16 个 poller + 20 个 handler
- **并发度影响**：QPS 随并发度增长趋于平稳
- **数据长度影响**：4KB 后开始下降

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
- [[entities/cpp/workflow/workflow-config]] — 全局配置