---
type: entity
tags: [C++异步框架, 自定义协议, TLV, 序列化]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 10: User Defined Protocol

## 概述
`tutorial-10-user_defined_protocol` 展示如何实现一个简单的自定义协议（TLV 格式）。

## 协议格式
- 4 字节头部：网络序整数表示 body 长度
- body：变长消息内容

## 实现协议类
~~~cpp
class TutorialMessage : public ProtocolMessage {
private:
    virtual int encode(struct iovec vectors[], int max);
    virtual int append(const void *buf, size_t size);
    // ...
};
~~~

## 序列化（encode）
~~~cpp
int TutorialMessage::encode(struct iovec vectors[], int max) {
    uint32_t n = htonl(this->body_size);
    vectors[0].iov_base = this->head;
    vectors[0].iov_len = 4;
    vectors[1].iov_base = this->body;
    vectors[1].iov_len = this->body_size;
    return 2;
}
~~~

## 反序列化（append）
- 每收到一个数据块调用一次
- 返回 0 表示消息不完整，继续接收
- 返回 1 表示消息接收完成
- 返回 -1 表示错误，需设置 errno

## 创建 Server/Client
~~~cpp
using WFTutorialTask = WFNetworkTask<TutorialRequest, TutorialResponse>;
using WFTutorialServer = WFServer<TutorialRequest, TutorialResponse>;

WFTutorialServer server([](WFTutorialTask *task) {
    *task->get_resp() = std::move(*task->get_req());
});
server.start(port);
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-tlv-message]] — TLV 消息
- [[entities/cpp/workflow/workflow-compute-tasks]] — 算法与协议的对称性