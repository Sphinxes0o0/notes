---
type: source
source-type: bookmark
title: "Sogou Workflow C++ 异步框架文档"
summary: "搜狗 C++ Workflow 异步引擎官方文档：架构核心（17篇）+ 教程（18篇），支持 HTTP/Redis/MySQL/Kafka/DNS 等 13 种协议"
path: raw/workflow/
tags: [C++异步框架, 网络框架, 任务调度, 负载均衡]
created: 2026-05-25
---

# Sogou Workflow C++ 异步框架

## 核心内容

Sogou Workflow 是一款高性能 C++ 异步编程框架，核心是基于任务的有向无环图（DAG）执行模型。

### 架构核心（17 文档）

| 文档 | 主题 |
|------|------|
| about-conditional | 条件任务与观察者模式 |
| about-config | 全局配置 |
| about-connection-context | 连接上下文 |
| about-counter | 计数器（信号量） |
| about-dns | DNS 解析与缓存 |
| about-error | 错误处理与状态码 |
| about-exit | 程序安全退出 |
| about-go-task | Go 风格计算任务 |
| about-module | 模块任务封装 |
| about-resource-pool | 资源池与消息队列 |
| about-selector | 多选一选择器 |
| about-service-governance | 服务治理 |
| about-timeout | 超时机制 |
| about-timer | 定时器 |
| about-tlv-message | TLV 消息格式 |
| about-upstream | 负载均衡与熔断 |
| benchmark | 性能测试对比 |

### 教程（18 文档）

| 文档 | 主题 |
|------|------|
| tutorial-01-wget | HTTP 抓取入门 |
| tutorial-02-redis_cli | Redis 异步客户端 |
| tutorial-03-wget_to_redis | 任务链与 Series |
| tutorial-04-http_echo_server | HTTP Server 入门 |
| tutorial-05-http_proxy | HTTP 代理服务器 |
| tutorial-06-parallel_wget | 并行任务 Parallel |
| tutorial-07-sort_task | 算法工厂与排序 |
| tutorial-08-matrix_multiply | 自定义计算任务 |
| tutorial-09-http_file_server | 异步文件 IO |
| tutorial-10-user_defined_protocol | 自定义协议 |
| tutorial-11-graph_task | DAG 图任务 |
| tutorial-12-mysql_cli | MySQL 异步客户端 |
| tutorial-13-kafka_cli | Kafka 异步客户端 |
| tutorial-15-name_service | 自定义命名服务 |
| tutorial-17-dns_cli | DNS 客户端 |
| tutorial-18-redis_subscriber | Redis 订阅模式 |
| tutorial-19-dns_server | DNS 服务器 |
| xmake | 编译与构建 |

## 支持协议

- HTTP/HTTPS（Client/Server）
- Redis（Client，含 Cluster 和订阅模式）
- MySQL（Client，含事务和预处理）
- Kafka（Producer/Consumer）
- DNS（Client/Server，支持 DoT）
- 自定义协议（TLV、二进制等）
- 文件 IO（Linux aio）

## 关键引用

### 任务模型
- Series（串行任务链）
- Parallel（并行任务组）
- Graph（DAG 复杂依赖）
- Counter、Timer、Selector、Conditional

### 服务治理
- Upstream（本地反向代理）
- 权重随机、一致性哈希、VNSWRR
- 主备模式、分组
- 熔断（MTTR=30s）
- 动态配置

### 性能
- 500K QPS（HTTP Server）
- 优于 nginx
- 持平或优于 brpc

## 相关页面
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端
- [[entities/cpp/workflow/workflow-parallel-tasks]] — 并行任务
- [[entities/cpp/workflow/workflow-upstream]] — 负载均衡
