---
type: entity
tags: [C++异步框架, 超时配置]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 超时机制

## 定义
框架提供多层次超时配置：全局、Server、任务级别。

## 超时层次
| 层次 | 配置方式 |
|------|----------|
| 全局 | `WFGlobalSettings.endpoint_params` |
| Upstream | `AddressParams.endpoint_params` |
| Server | `WFServerParams` |
| 任务级 | `task->set_send_timeout()` 等接口 |

## 主要超时参数
- **connect_timeout**：建立连接超时（毫秒）
- **response_timeout**：等待响应超时
- **ssl_connect_timeout**：SSL 握手超时
- **receive_timeout**：接收完整请求超时
- **keep_alive_timeout**：连接保持时间
- **watch_timeout**：等待首个数据包超时

## 超时原因
`task->get_timeout_reason()` 返回：
- `TOR_NOT_TIMEOUT`
- `TOR_WAIT_TIMEOUT`
- `TOR_CONNECT_TIMEOUT`
- `TOR_TRANSMIT_TIMEOUT`

## 相关概念
- [[entities/cpp/workflow/workflow-config]] — 全局配置
- [[entities/cpp/workflow/workflow-upstream]] — Upstream 独立配置
