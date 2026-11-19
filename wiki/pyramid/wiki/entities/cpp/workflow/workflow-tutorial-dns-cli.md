---
type: entity
tags: [C++异步框架, DNS, 异步解析, WFDnsClient]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 17: DNS CLI

## 概述
`tutorial-17-dns_cli` 展示如何使用 Workflow 的 DNS 客户端进行域名解析。

## WFDnsClient 用法
~~~cpp
WFDnsClient client;
client.init("8.8.8.8");  // DNS 服务器

WFDnsTask *task = client.create_dns_task("www.sogou.com", callback);
task->start();

// 支持 DoT (DNS over TLS)
client.init("dnss://120.53.53.53/");
~~~

## 工厂函数创建
~~~cpp
std::string url = "dns://8.8.8.8/www.sogou.com";
WFDnsTask *task = WFTaskFactory::create_dns_task(url, retry_max, callback);

// 自定义查询类型
protocol::DnsRequest *req = task->get_req();
req->set_question_type(DNS_TYPE_AAAA);  // IPv6
req->set_question_class(DNS_CLASS_IN);
~~~

## 获取结果
### DnsUtil::getaddrinfo（推荐）
~~~cpp
void dns_callback(WFDnsTask *task) {
    struct addrinfo *res;
    protocol::DnsUtil::getaddrinfo(task->get_resp(), 80, &res);
    // 使用 res...
    protocol::DnsUtil::freeaddrinfo(res);
}
~~~

### DnsResultCursor
~~~cpp
protocol::DnsResultCursor cursor(task->get_resp());
cursor.reset_answer_cursor();
const struct dns_record *record;
while (cursor.next(&record)) {
    // 处理 A/AAAA/CNAME/MX/SRV 等记录
}
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-dns]] — DNS 详细文档
- [[entities/cpp/workflow/workflow-name-service]] — 命名服务