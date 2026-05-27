---
type: entity
tags: [C++异步框架, Sogou, 已知问题, OpenSSL, TLS]
created: 2026-05-27
sources: [raw/workflow/bugs]
---

# 已知 BUG 设计概念

## 定义

记录 Sogou Workflow 已知的外部依赖相关 BUG 及 workaround，供开发者在使用时规避。

## BUG 1：OpenSSL 1.1.1 及以下 SSL 状态为 WFT_STATE_SYS_ERROR，错误码为 0

**原因：** OpenSSL 1.1.1 及以下的 bug — `SSL_get_error()` 为 `SSL_ERROR_SYSCALL` 时，`errno` 被置为 0。框架将 `SSL_ERROR_SYSCALL` 转为系统错误，导致错误码为 0。

**Workaround：** 建议升级到 **OpenSSL 3.0** 或以上。相关 issue：https://github.com/openssl/openssl/issues/12416

## BUG 2：HTTPS + TLS SNI + Upstream 时出现 SSL Error

**原因：** HTTP header 中的 `Host` 字段填写的是原始 URL 的 host，而 TLS SNI 的 server name 是 upstream 解析后的实际域名，两者不一致导致 SSL 握手失败。

**示例：**
~~~cpp
// upstream "sogou" 指向 www.sogou.com
auto *task = WFTaskFactory::create_http_task("https://sogou/index.html", 0, 0, nullptr);
// http header Host = "sogou"
// TLS SNI = "www.sogou.com"  ← 不匹配
~~~

**Workaround：** 通过 `prepare` 函数在发送请求前修改 Host：
~~~cpp
task->set_prepare([](WFHttpTask *task) {
    auto *t = static_cast<WFComplexClientTask<protocol::HttpRequest, protocol::HttpResponse> *>(task);
    task->get_req()->set_header_pair("Host", t->get_current_uri()->host);
});
~~~

## 相关页面

- [[workflow-known-bugs]] — Known Bugs 实体页
- [[workflow-upstream]] — Upstream 负载均衡
- [[workflow-user-defined-protocol]] — 自定义协议
