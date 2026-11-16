---
type: entity
tags: [C++异步框架, 自定义协议, 序列化, 反序列化]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 自定义协议

## 定义
通过实现 `ProtocolMessage` 的序列化和反序列化方法，可自定义通信协议。

## 协议格式
- 4 字节 head（网络序，body 长度）
- N 字节 body

## 必须实现
~~~cpp
class MyMessage : public ProtocolMessage {
    virtual int encode(struct iovec vectors[], int max);
    virtual int append(const void *buf, size_t *size);
};
~~~

### encode
- 消息发送前调用
- 返回使用的 vector 数量
- `iov_base` 指向的内存不复制

### append
- 每次收到数据块调用
- 返回 0（继续接收）、1（消息结束）、-1（错误）

## 使用
~~~cpp
using MyTask = WFNetworkTask<MyRequest, MyResponse>;
using MyServer = WFServer<MyRequest, MyResponse>;
WFNetworkTaskFactory<MyRequest, MyResponse>::create_client_task(...);
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-tlv-message]] — TLV 消息
- [[entities/cpp/workflow/workflow-async-model]] — 异步任务模型
