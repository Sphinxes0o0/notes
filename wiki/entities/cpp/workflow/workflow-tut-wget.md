---
type: entity
tags: [C++异步框架, HTTP客户端, wget, 入门]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 01: wget 第一个 HTTP 任务

## 定义
wget 示例展示了如何创建第一个 HTTP 网络任务：从 stdin 读取 URL 并抓取网页内容。

## 创建 HTTP 任务
~~~cpp
WFHttpTask *task = WFTaskFactory::create_http_task(
    url, REDIRECT_MAX, RETRY_MAX, wget_callback);
protocol::HttpRequest *req = task->get_req();
req->add_header_pair("Accept", "*/*");
req->add_header_pair("User-Agent", "Wget/1.14 (gnu-linux)");
req->add_header_pair("Connection", "close");
task->start();
pause();
~~~

## 关键要点
- `create_http_task(url, redirect_max, retry_max, callback)`：工厂方法
- `task->get_req()`：获取请求对象
- `task->start()`：非阻塞启动任务
- 所有工厂函数永不返回 NULL，错误在 callback 中处理

## 处理结果
~~~cpp
void wget_callback(WFHttpTask *task) {
    protocol::HttpResponse *resp = task->get_resp();
    int state = task->get_state();
    int error = task->get_error();
    // 获取 body
    const void *body; size_t len;
    resp->get_parsed_body(&body, &len);
}
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端
- [[entities/cpp/workflow/workflow-error-handling]] — 错误处理