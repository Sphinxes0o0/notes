---
type: entity
tags: [C++异步框架, Redis, 异步客户端, KV存储]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 02: Redis CLI

## 概述
`tutorial-02-redis_cli` 展示如何使用 Workflow 的异步 Redis 客户端。

## Redis URL 格式
- `redis://:password@host:port/dbnum?query#fragment`
- `rediss://` 用于 SSL 连接
- 默认端口 6379，dbnum 默认 0

## 核心操作
- **创建任务**：`WFTaskFactory::create_redis_task(url, retry_max, callback)`
- **设置命令**：`req->set_request("SET", {key, value})`
- **获取结果**：`resp->get_result(val)` 获取 Redis 响应

## 任务链
~~~cpp
void redis_callback(WFRedisTask *task) {
    if (cmd == "SET") {
        WFRedisTask *next = WFTaskFactory::create_redis_task(url, RETRY_MAX, callback);
        next->get_req()->set_request("GET", {data->key});
        series_of(task)->push_back(next);  // 串入任务链
    }
}
~~~

## 重要约束
- **禁止**用户使用 SELECT 和 AUTH 命令
- 每次请求 URL 必须包含数据库选择和密码信息

## 相关概念
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端
- [[entities/cpp/workflow/workflow-parallel-tasks]] — Series 任务链
- [[entities/cpp/workflow/workflow-redis-features]] — Redis 高级特性（Cluster、订阅）