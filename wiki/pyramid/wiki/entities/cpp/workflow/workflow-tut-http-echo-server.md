---
type: entity
tags: [C++异步框架, HTTP服务器, Echo, 入门]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 04: http_echo_server HTTP 服务器

## 定义
第一个 HTTP Server 示例：返回 HTML 页面显示客户端发送的 HTTP 请求 header 信息。

## 创建与启动
~~~cpp
WFHttpServer server(process);
if (server.start(port) == 0) {
    pause();
    server.stop();
}
~~~

## 处理请求
~~~cpp
void process(WFHttpTask *server_task) {
    HttpRequest *req = server_task->get_req();
    HttpResponse *resp = server_task->get_resp();
    resp->append_output_body("<html>...");
    resp->set_status_code("200");
    // 访问 header
    HttpHeaderCursor cursor(req);
    while (cursor.next(name, value)) { ... }
}
~~~

## 关键要点
- `process` 函数签名为 `void process(WFHttpTask *)`
- `server_task->get_task_seq()` 获取请求序号（连接上的第几次）
- Server 回复在 series 所有任务完成后自动发送
- `task->noreply()` 可跳过回复直接关闭连接

## 启动选项
- `server.start(port)`：基础启动
- `server.start(port, cert_file, key_file)`：SSL
- `server.serve(listen_fd)`：优雅重启

## 相关概念
- [[entities/cpp/workflow/workflow-http-server]] — HTTP 服务器
- [[entities/cpp/workflow/workflow-connection-context]] — 连接上下文