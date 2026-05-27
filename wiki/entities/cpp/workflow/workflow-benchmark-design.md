---
type: entity
tags: [C++异步框架, Sogou, 性能测试, 基准测试]
created: 2026-05-27
sources: [raw/workflow/benchmark]
---

# Benchmark 设计概念

## 定义

Sogou C++ Workflow 的官方性能测试文档，记录了 HTTP Server 场景下的压测方案、代码和结果对比。

## 测试环境

| 配置 | 值 |
|------|-----|
| CPU | 40 Cores, Intel Xeon E5-2630 v4 @ 2.20GHz |
| Memory | 192GB |
| NIC | 25000Mbps |
| OS | CentOS 7.8 |
| GCC | 4.8.5 |
| RTT | ~0.1ms |

## 对照组

- **nginx** — 生产广泛使用的 HTTP 服务器
- **brpc** — 百度 RPC 框架（对比 HTTP Server 能力）

## 测试工具

- **wrk** — 测 QPS 极限和延时
- **wrk2** — 在特定 QPS 下测延时分布

## 测试场景

### 场景一：并发度和数据长度正交测试

变量：并发度 [1, 2K]，数据长度 [16B, 64KB]

**关键结论：**
- 数据长度 64B/512B 时，Sogou Workflow 可达 **500K QPS**，优于 nginx 和 brpc
- 延时表现：Sogou Workflow 优于 brpc，远优于 nginx

### 场景二：掺杂慢请求的延时分布

- 正常请求 QPS：20K / 100K / 200K
- 慢请求 QPS：正常 QPS 的 1%，固定 5ms 延迟

**关键结论：** Sogou Workflow 与 brpc 在此场景下旗鼓相当

## 关键性能数字

- **500K QPS** — 数据长度 64B/512B 下的极限 QPS
- **优于 nginx** — 所有测试场景均领先
- **与 brpc 相当** — 掺杂慢请求场景下

## 相关页面

- [[entities/cpp/workflow/workflow-benchmark]] — Benchmark 实体页
- [[entities/cpp/workflow/workflow-http-server]] — HTTP Server 教程
- [[entities/cpp/workflow/workflow-performance]] — 性能相关
