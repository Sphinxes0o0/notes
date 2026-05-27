---
type: entity
tags: [C++异步框架, 已知问题, bug, OpenSSL]
created: 2026-05-25
updated: 2026-05-27
sources: [workflow-engine]
---

# Workflow 已知问题

## 定义
记录 Workflow 框架已知的 bug 和限制，以及对应的 workaround。

## Bug 1: OpenSSL 1.1.1 及以下 SSL 错误码为 0

### 问题描述
SSL 通信时，当 `SSL_get_error()` 返回 `SSL_ERROR_SYSCALL`，OpenSSL 1.1.1 及以下会将 errno 置 0。
Framework 将 `SSL_ERROR_SYSCALL` 转为系统错误，导致得到错误码 0。

### 表现
~~~cpp
void callback(WFHttpTask *task) {
    // state=1(WFT_STATE_SYS_ERROR), error=0
}
~~~

### 解决
升级到 OpenSSL 3.0 或以上。

## Bug 2: HTTPS + TLS SNI + Upstream 时 SSL error

### 问题描述
当 URL host 为 upstream 名（指向另一域名），HTTP Host header 填写原始 host，
与 TLS SNI server name 不一致，导致 SSL 错误。

### 场景
~~~cpp
auto *task = WFTaskFactory::create_http_task("https://sogou/index.html", ...);
// upstream sogou -> www.sogou.com
// TLS SNI = www.sogou.com, HTTP Host = sogou (不一致)
~~~

### 解决
设置 prepare 函数修正 Host：
~~~cpp
task->set_prepare([](WFHttpTask *task) {
    auto *t = static_cast<WFComplexClientTask<...> *>(task);
    task->get_req()->set_header_pair("Host", t->get_current_uri()->host);
});
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-upstream]] — Upstream
- [[entities/cpp/workflow/workflow-error-handling]] — 错误处理