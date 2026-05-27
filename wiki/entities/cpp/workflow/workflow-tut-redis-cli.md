---
type: entity
tags: [C++异步框架, Redis客户端, 入门]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 02: redis_cli Redis 异步客户端

## 定义
redis_cli 展示如何创建 Redis 任务：写入 KV 后读出验证。

## Redis URL 格式
~~~bash
redis://:password@host:port/dbnum
rediss://:password@host:port/dbnum  # SSL
~~~

## 创建 Redis 任务
~~~cpp
WFRedisTask *task = WFTaskFactory::create_redis_task(url, RETRY_MAX, callback);
protocol::RedisRequest *req = task->get_req();
req->set_request("SET", {key, value});
task->user_data = &data;
task->start();
~~~

## 任务链（Series）
~~~cpp
void redis_callback(WFRedisTask *task) {
    // SET 成功后创建 GET 任务
    if (cmd == "SET") {
        WFRedisTask *next = create_redis_task(url, RETRY_MAX, callback);
        next->get_req()->set_request("GET", {key});
        series_of(task)->push_back(next);
    }
}
~~~

## 关键要点
- `series_of(task)->push_back(next)`：将任务加入串行链
- `push_back` 在 callback 结束后启动任务，保持顺序
- Redis 支持 Cluster 模式，自动处理 MOVED/ASK

## 相关概念
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端
- [[entities/cpp/workflow/workflow-redis-features]] — Redis 订阅
- [[entities/cpp/workflow/workflow-parallel-tasks]] — Series 与 Parallel