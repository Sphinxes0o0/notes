---
type: entity
tags: [C++异步框架, Kafka客户端, 消息队列]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 13: kafka_cli 异步 Kafka 客户端

## 定义
展示如何使用 WFKafkaClient 实现 Kafka 消息生产和消费。

## 编译
~~~bash
# CMake
make KAFKA=y

# Bazel
bazel build kafka_cli
~~~

## 创建客户端
~~~cpp
WFKafkaClient *client = new WFKafkaClient();
client->init(url);  // kafka://host:port,kafka://host2:port
// 或带消费者组
client->init(url, group_name);
~~~

## Produce 任务
~~~cpp
WFKafkaTask *task = client->create_kafka_task(
    "api=produce&topic=xxx&topic=yyy", 3, kafka_callback);

KafkaRecord record;
record.set_key("key1", strlen("key1"));
record.set_value(buf, sizeof(buf));
record.add_header_pair("hk1", 3, "hv1", 3);

task->add_produce_record("workflow_test1", -1, std::move(record));

// 支持压缩
KafkaConfig config;
config.set_compress_type(Kafka_Zstd);
task->set_config(std::move(config));
~~~

## Fetch 任务（消费者组）
~~~cpp
WFKafkaClient *client_fetch = new WFKafkaClient();
client_fetch->init(url, cgroup_name);
WFKafkaTask *task = client_fetch->create_kafka_task(
    "api=fetch&topic=xxx&topic=yyy", 3, kafka_callback);
task->start();
~~~

## Fetch 任务（手动模式）
~~~cpp
KafkaToppar toppar;
toppar.set_topic_partition("workflow_test1", 0);
toppar.set_offset(0);
task->add_toppar(toppar);
~~~

## 认证
~~~cpp
KafkaConfig config;
config.set_sasl_username("fetch");
config.set_sasl_password("fetch-secret");
config.set_sasl_mech("SCRAM-SHA-256");
task->set_config(std::move(config));
~~~

## 处理结果
~~~cpp
KafkaResult *result = task->get_result();
result->fetch_records(records);

for (auto &v : records) {
    for (auto &w: v) {
        const void *value; size_t len;
        w->get_value(&value, &len);
        printf("topic: %s, partition: %d, offset: %lld\n",
               w->get_topic(), w->get_partition(), w->get_offset());
    }
}
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-network-client]] — 网络客户端
- [[entities/cpp/workflow/workflow-resource-pool]] — 消息队列