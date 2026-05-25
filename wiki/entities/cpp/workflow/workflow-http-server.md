---
type: entity
tags: [C++异步框架, HTTP服务器, Echo, Proxy, File Server]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow HTTP 服务器

## 定义
Workflow 支持创建 HTTP Server，处理请求并返回响应。

## Echo Server
- **创建**：`WFHttpServer server(process)`
- **启动**：`server.start(port)`
- **处理**：`void process(WFHttpTask *task)` 填写 response

## HTTP Proxy
- **原理**：将请求转发到远端 server，再将响应转发给 client
- **关键**：`series->set_context()` 保存上下文
- **配置**：`WFServerParams` 可限制请求大小

## HTTP File Server
- **特性**：异步文件 IO，使用 Linux aio
- **任务**：`WFTaskFactory::create_pread_task()`
- **注意**：大文件不适合（需全部读入内存）

## 响应方式
- `resp->append_output_body()` 复制数据
- `resp->append_output_body_nocopy()` 直接引用指针
- server 在 series 所有任务完成后自动回复

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
- [[entities/cpp/workflow/workflow-connection-context]] — 连接上下文
