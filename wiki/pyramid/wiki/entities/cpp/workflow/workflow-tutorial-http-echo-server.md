---
type: entity
tags: [C++异步框架, HTTP服务器, Echo, Server]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 04: HTTP Echo Server

## 概述
`tutorial-04-http_echo_server` 展示如何创建一个最简单的 HTTP Server。

## 创建与启动
~~~cpp
WFHttpServer server(process);
server.start(port);  // 非阻塞
pause();
server.stop();       // 阻塞，等待所有任务完成
~~~

## Process 函数
~~~cpp
void process(WFHttpTask *server_task) {
    protocol::HttpRequest *req = server_task->get_req();
    protocol::HttpResponse *resp = server_task->get_resp();
    long seq = server_task->get_task_seq();  // 当前连接上的请求序号

    resp->set_status_code("200");
    resp->add_header_pair("Content-Type", "text/html");
    resp->append_output_body("<html>...</html>");
}
~~~

## 响应方式
- `append_output_body()` 复制数据
- `append_output_body_nocopy()` 直接引用指针（生命周期需延续到 callback）
- 同一连接第 10 次请求后关闭：`seq == 9` 时加 `Connection: close`

## 多协议 Server
- 只需替换模板参数：`WFServer<MyRequest, MyResponse>`
- 启动 IPv6 + IPv4 双栈：分别创建两个 server 对象

## 相关概念
- [[entities/cpp/workflow/workflow-http-server]] — HTTP Server 高级用法
- [[entities/cpp/workflow/workflow-connection-context]] — 连接上下文