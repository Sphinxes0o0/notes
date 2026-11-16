---
type: entity
tags: [C++异步框架, Redis, 订阅模式]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow Redis 订阅

## 定义
Workflow 支持 Redis 订阅模式，实现 Pub/Sub 功能。

## 订阅任务
~~~cpp
WFRedisSubscriber subscriber;
subscriber.init(url);
WFRedisSubscribeTask *task = subscriber.create_subscribe_task(
    channels, extract_callback, task_callback);
task->start();
~~~

## 消息处理
- `extract_callback`：处理服务端推送消息
- 消息格式：数组 [type, channel, content]
- subscribe/psubscribe 回复：[type, name, count]

## 动态修改
- `task->subscribe(channels)` 新增订阅
- `task->unsubscribe(channels)` 取消订阅
- `task->quit()` 主动结束

## 相关概念
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端
