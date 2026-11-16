---
type: entity
tags: [C++异步框架, 网络客户端, HTTP, Redis, MySQL, Kafka, DNS]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 网络客户端

## 定义
Workflow 支持多种网络协议客户端：HTTP、Redis、MySQL、Kafka、DNS。

## 支持协议

### HTTP
- **创建**：`WFTaskFactory::create_http_task(url, redirect_max, retry_max, callback)`
- **URL**：`http://host:port/path`
- **特性**：自动重定向、重试、Keep-Alive

### Redis
- **URL**：`redis://:password@host:port/dbnum`
- **创建**：`create_redis_task(url, retry_max, callback)`
- **命令**：`req->set_request("SET", {key, value})`
- **特性**：支持 Cluster 模式（自动处理 MOVED/ASK）

### MySQL
- **URL**：`mysql://user:password@host:port/dbname?charset=...`
- **创建**：`create_mysql_task(url, retry_max, callback)`
- **事务**：`WFMySQLConnection` 保证独占连接
- **结果**：通过 `MySQLResultCursor` 遍历结果集

### Kafka
- **客户端**：`WFKafkaClient` 封装
- **操作**：produce（生产）、fetch（消费）
- **压缩**：支持 zlib、snappy、lz4、zstd
- **认证**：支持 SASL/PLAIN、SCRAM

### DNS
- **创建**：`WFTaskFactory::create_dns_task(url, retry_max, callback)`
- **结果**：`DnsUtil::getaddrinfo()` 或 `DnsResultCursor`
- **类型**：A、AAAA、NS、CNAME、MX、SRV、PTR、SOA

## 通用模式
- `task->get_req()` / `task->get_resp()` 获取消息
- `series_of(task)->push_back(next_task)` 串行任务
- `task->user_data` 传递数据

## 相关概念
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
- [[entities/cpp/workflow/workflow-upstream]] — 负载均衡
- [[entities/cpp/workflow/workflow-dns]] — DNS 详细
