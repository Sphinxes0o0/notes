---
type: entity
tags: [C++异步框架, Redis订阅, Pub/Sub]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 18: redis_subscriber Redis 订阅模式

## 定义
展示如何使用 WFRedisSubscriber 实现 Redis Pub/Sub 功能。

## 创建订阅客户端
~~~cpp
WFRedisSubscriber subscriber;
subscriber.init(url);  // redis://host:port

WFRedisSubscribeTask *task = subscriber.create_subscribe_task(
    channels,
    extract_callback,  // 处理推送消息
    task_callback      // 任务结束回调
);
task->set_watch_timeout(1000000);  // 1000秒
task->start();
~~~

## 消息格式
- **推送消息**：[type, channel/name, content]
- **subscribe 回复**：[subscribe, name, count]
- **unsubscribe 回复**：[unsubscribe, name, count]

## 动态修改订阅
~~~cpp
task->subscribe(channels);    // 新增订阅
task->unsubscribe(channels);  // 取消订阅
task->punsubscribe();         // 取消所有 pattern 订阅
task->quit();                 // 主动结束
~~~

## Ping 保持活跃
~~~cpp
task->ping();           // 发送 PING
task->ping(message);    // 发送带消息的 PING
// 配合 watch_timeout 防止超时断开
~~~

## 注意事项
- 所有订阅取消后任务结束
- 需要 `task->release()` 释放任务
- watch_timeout 设置合理值

## 相关概念
- [[entities/cpp/workflow/workflow-redis-features]] — Redis 订阅
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端