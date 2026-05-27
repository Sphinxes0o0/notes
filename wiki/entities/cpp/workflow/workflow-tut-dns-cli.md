---
type: entity
tags: [C++异步框架, DNS客户端]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 17: dns_cli DNS 客户端

## 定义
展示如何使用 WFDnsClient 和工厂函数创建 DNS 解析任务。

## WFDnsClient 创建
~~~cpp
WFDnsClient client;
client.init("8.8.8.8");  // 支持 DoT: dnss://8.8.8.8/

WFDnsTask *task = client.create_dns_task("www.sogou.com", dns_callback);
task->start();
pause();
client.deinit();
~~~

## 工厂函数创建
~~~cpp
std::string url = "dns://8.8.8.8/www.sogou.com";
WFDnsTask *task = WFTaskFactory::create_dns_task(url, 0, dns_callback);

// 或先创建后设置
WFDnsTask *task = WFTaskFactory::create_dns_task("dns://8.8.8.8/", 0, callback);
req->set_question("www.zhihu.com", DNS_TYPE_AAAA, DNS_CLASS_IN);
~~~

## 获取结果
~~~cpp
// 方式1：getaddrinfo（推荐）
struct addrinfo *res;
DnsUtil::getaddrinfo(resp, 80, &res);
// 使用 res...
DnsUtil::freeaddrinfo(res);

// 方式2：DnsResultCursor 遍历
DnsResultCursor cursor(resp);
if (resp->get_ancount() > 0) {
    cursor.reset_answer_cursor();
    while (cursor.next(&record)) {
        // record->type: DNS_TYPE_A/AAAA/NS/CNAME/SRV/MX/PTR/SOA
    }
}
~~~

## 支持记录类型
A、AAAA、NS、CNAME、PTR、SOA、SRV、MX

## 相关概念
- [[entities/cpp/workflow/workflow-dns]] — DNS 详细配置
- [[entities/cpp/workflow/workflow-dns-server]] — DNS 服务器