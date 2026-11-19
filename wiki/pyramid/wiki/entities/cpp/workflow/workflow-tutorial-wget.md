---
type: entity
tags: [C++异步框架, HTTP, 入门, Wget]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 01: Wget (HTTP 抓取)

## 概述
`tutorial-01-wget` 是 Workflow 的第一个入门示例，展示如何创建一个简单的 HTTP 抓取任务。

## 核心内容
- **创建任务**：`WFTaskFactory::create_http_task(url, redirect_max, retry_max, callback)`
- **请求设置**：`task->get_req()->add_header_pair()` 添加 HTTP header
- **启动任务**：`task->start()`（非阻塞）
- **响应获取**：`task->get_resp()->get_parsed_body()` 获取响应体

## 关键代码
~~~cpp
WFHttpTask *task = WFTaskFactory::create_http_task(url, 0, 0, wget_callback);
protocol::HttpRequest *req = task->get_req();
req->add_header_pair("Accept", "*/*");
req->add_header_pair("User-Agent", "Wget/1.14 (gnu-linux)");
req->add_header_pair("Connection", "close");
task->start();
pause();  // 等待 Ctrl-C 退出
~~~

## Callback 处理
~~~cpp
void wget_callback(WFHttpTask *task) {
    int state = task->get_state();
    int error = task->get_error();
    protocol::HttpResponse *resp = task->get_resp();
    const void *body;
    size_t body_len;
    resp->get_parsed_body(&body, &body_len);
    fwrite(body, 1, body_len, stdout);
}
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端总览
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型