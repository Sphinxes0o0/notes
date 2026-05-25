---
type: entity
tags: [C++异步框架, 已知问题]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 已知 Bug

## OpenSSL 1.1.1 及以下 SSL 错误码为 0
- **原因**：OpenSSL bug，`SSL_get_error()` 为 `SSL_ERROR_SYSCALL` 时 `errno` 被置 0
- **影响**：SSL 通信下 `get_error()` 返回 0
- **建议**：升级到 OpenSSL 3.0+

## HTTPS + Upstream + TLS SNI Host 不一致
- **原因**：HTTP Host header 与 SNI server name 不一致
- **解决**：通过 `prepare` 函数修改 Host header：
~~~cpp
task->set_prepare([](WFHttpTask *task) {
    task->get_req()->set_header_pair("Host", task->get_current_uri()->host);
});
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-error-handling]] — 错误处理
