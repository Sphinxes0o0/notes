---
type: entity
tags: [C++异步框架, 全局配置]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 全局配置

## 定义
全局配置用于配置框架默认参数，必须在任何框架调用之前修改。

## 关键要点
- **配置结构**：`WFGlobalSettings`
- **修改时机**：必须在 `WORKFLOW_library_init()` 之前
- **主要参数**：
  - `endpoint_params`：连接超时、响应超时
  - `dns_ttl_default`：DNS 缓存默认 TTL（秒）
  - `dns_ttl_min`：DNS 失败时最短 TTL
  - `poller_threads`：epoll/kqueue 线程数
  - `handler_threads`：callback 执行线程数
  - `compute_threads`：计算线程数（默认=CPU核数）

## 相关概念
- [[entities/cpp/workflow/workflow-upstream]] — Upstream 可覆盖全局配置
- [[entities/cpp/workflow/workflow-timeout]] — 超时配置
