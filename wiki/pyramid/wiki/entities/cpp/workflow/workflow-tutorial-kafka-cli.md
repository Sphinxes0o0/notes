---
type: entity
tags: [C++异步框架, Kafka, 消息队列, Producer, Consumer]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 13: Kafka CLI

## 概述
`tutorial-13-kafka_cli` 展示如何使用 Workflow 的异步 Kafka 客户端。

## Broker URL
- `kafka://host:port` 或 `kafkas://host:port`（SSL）
- 多个 broker 用逗号分隔

## 创建客户端
~~~cpp
WFKafkaClient *client = new WFKafkaClient();
client->init(url);
client->init(url, group_name);  // 消费者组模式
~~~

## Produce（生产消息）
~~~cpp
WFKafkaTask *task = client->create_kafka_task(
    "api=produce&topic=workflow_test", retry_max, callback);

KafkaRecord record;
record.set_key("key1", strlen("key1"));
record.set_value(buf, sizeof(buf));
task->add_produce_record("workflow_test", -1, std::move(record));

// 支持压缩
KafkaConfig config;
config.set_compress_type(Kafka_Zstd);
task->set_config(std::move(config));
~~~

## Fetch（消费消息）
~~~cpp
// 手动模式
WFKafkaTask *task = client->create_kafka_task("api=fetch", retry_max, callback);
KafkaToppar toppar;
toppar.set_topic_partition("workflow_test", 0);
toppar.set_offset(0);
task->add_toppar(toppar);

// 消费者组模式
client->init(url, cgroup_name);
WFKafkaTask *task = client->create_kafka_task(
    "api=fetch&topic=workflow_test", retry_max, callback);
~~~

## 提交 Offset
~~~cpp
WFKafkaTask *commit_task = client.create_kafka_task(
    "api=commit", retry_max, callback);
commit_task->start();
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端
- [[entities/cpp/workflow/workflow-redis-features]] — Redis 特性对比