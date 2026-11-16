---
type: entity
tags: [C++异步框架, HTTP代理, 代理服务器, 异步Server]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 05: HTTP Proxy

## 概述
`tutorial-05-http_proxy` 展示如何实现一个异步 HTTP 代理服务器。

## Server 配置
~~~cpp
struct WFServerParams params = HTTP_SERVER_PARAMS_DEFAULT;
params.request_size_limit = 8 * 1024 * 1024;
WFHttpServer server(&params, process);
server.start(port);
~~~

## 代理原理
1. 接收浏览器请求
2. 创建客户端任务向远端服务器发起请求
3. 将远端响应转发给浏览器

## 异步模式
- **关键**：用 `series->set_context()` 保存上下文
- **流程**：process 中创建客户端任务 → 客户端 callback 中填写 server 响应
- **优势**：不占用线程，所有操作异步完成

## 响应传输
~~~cpp
resp->get_parsed_body(&body, &len);
resp->append_output_body_nocopy(body, len);
*proxy_resp = std::move(*resp);  // 无拷贝转移
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-http-server]] — HTTP Server 总览
- [[entities/cpp/workflow/workflow-parallel-tasks]] — Series 与任务链