---
type: entity
tags: [C++异步框架, 已知问题, Bug, OpenSSL, TLS SNI]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 已知问题

## OpenSSL 1.1.1 及以下版本

### SSL 错误码为 0
- **问题**：`task->get_state() == WFT_STATE_SYS_ERROR`，`task->get_error() == 0`
- **原因**：OpenSSL 1.1.1 及以下，当 `SSL_get_error()` 为 `SSL_ERROR_SYSCALL` 时，errno 被清零
- **解决**：升级到 OpenSSL 3.0+

## HTTPS + Upstream + TLS SNI

### Host 与 SNI 不一致
- **问题**：使用 Upstream 时，SNI server name 与 HTTP Host header 不一致导致 SSL 错误
- **原因**：HTTP Host 使用原始 URL 的 host，SNI 使用 upstream 解析后的 host
- **解决**：设置 prepare 函数修正 Host
~~~cpp
task->set_prepare([](WFHttpTask *task){
    auto *t = static_cast<WFComplexClientTask*>(task);
    task->get_req()->set_header_pair("Host", t->get_current_uri()->host);
});
~~~