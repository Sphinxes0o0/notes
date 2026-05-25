---
type: entity
tags: [C++异步框架, 错误处理, 状态码]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 错误处理

## 定义
框架禁用 C++ 异常，通过任务状态码和错误码传递错误信息。工厂函数永不返回 NULL。

## 任务状态
| 状态 | 含义 |
|------|------|
| `WFT_STATE_SUCCESS` | 成功 |
| `WFT_STATE_SYS_ERROR` | 系统错误（errno） |
| `WFT_STATE_DNS_ERROR` | DNS 解析错误 |
| `WFT_STATE_SSL_ERROR` | SSL 错误 |
| `WFT_STATE_TASK_ERROR` | 任务错误（如 URL 不合法） |
| `WFT_STATE_ABORTED` | 程序退出时打断 |

## 关键要点
- **无异常**：编译时建议加 `-fno-exceptions`
- **工厂成功**：工厂函数永不返回 NULL
- **错误获取**：`task->get_state()` + `task->get_error()`
- **超时原因**：`task->get_timeout_reason()`

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
