---
type: entity
tags: [C++异步框架, Redis, 订阅, Pub/Sub, 消息推送]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 18: Redis Subscriber

## 概述
`tutorial-18-redis_subscriber` 展示如何使用 Workflow 的 Redis 订阅功能。

## 创建订阅客户端
~~~cpp
WFRedisSubscriber suber;
suber.init(url);

WFRedisSubscribeTask *task = suber.create_subscribe_task(
    channels, extract, callback);
task->set_watch_timeout(1000000);  // 1000 秒
task->start();
~~~

## 订阅消息格式
- **message/pmessage**：服务端推送的消息
  - [type, channel/pattern, content]
- **subscribe/psubscribe**：订阅确认
  - [type, name, count]
- **unsubscribe/punsubscribe**：取消订阅确认

## 处理消息
~~~cpp
void extract(WFRedisSubscribeTask *task) {
    auto *resp = task->get_resp();
    protocol::RedisValue value;
    resp->get_result(value);

    for (size_t i = 0; i < value.arr_size(); i++) {
        if (value[i].is_string())
            std::cout << value[i].string_value();
        else if (value[i].is_int())
            std::cout << value[i].int_value();
    }
}
~~~

## 动态修改订阅
~~~cpp
task->subscribe({"channel1", "channel2"});
task->psubscribe({"pattern*"});
task->unsubscribe({"channel1"});
task->punsubscribe();  // 取消所有 pattern
task->quit();         // 主动结束
task->release();      // 释放任务
~~~

## Ping 保持连接
~~~cpp
task->ping();  // 发送 PING
task->ping("message");  // 带消息
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-network-client]] — Redis 基础
- [[entities/cpp/workflow/workflow-tutorial-redis-cli]] — Redis 客户端