---
type: entity
tags: [C++异步框架, HTTP代理, 代理服务器]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 05: http_proxy HTTP 代理服务器

## 定义
实现一个 HTTP 代理服务器：将客户端请求转发到目标 server，再将响应转发回客户端。

## 配置 Server 参数
~~~cpp
struct WFServerParams params = HTTP_SERVER_PARAMS_DEFAULT;
params.request_size_limit = 8 * 1024 * 1024;  // 限制请求大小
WFHttpServer server(&params, process);
~~~

## Server 参数说明
| 参数 | 说明 | 默认 |
|------|------|------|
| transport_type | TT_TCP/TT_UDP/TT_SCTP | TT_TCP |
| max_connections | 最大连接数 | 2000 |
| peer_response_timeout | 读取数据超时 | 10s |
| receive_timeout | 接收完整请求超时 | 无限 |
| keep_alive_timeout | 连接保持时间 | 60s |
| ssl_accept_timeout | SSL 握手超时 | 10s |

## 代理逻辑
1. 获取浏览器请求的完整 URL
2. 构造转发请求（去除 scheme://host:port）
3. 将转发任务加入当前 series
4. 在 callback 中将响应转发给客户端

## 关键点
- 使用 `std::move` 转移请求，避免复制
- `series->set_context(context)` 保存 proxy_task
- HTTP Server 任务和普通 HTTP Client 任务类型相同

## 相关概念
- [[entities/cpp/workflow/workflow-http-server]] — HTTP 服务器
- [[entities/cpp/workflow/workflow-parallel-tasks]] — Series