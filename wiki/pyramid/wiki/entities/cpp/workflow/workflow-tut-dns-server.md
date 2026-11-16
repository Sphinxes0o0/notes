---
type: entity
tags: [C++异步框架, DNS服务器]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow Tutorial 19: dns_server DNS 服务器

## 定义
展示如何创建 DNS Server 并组装 DNS 响应消息。

## 创建 DNS 服务器
~~~cpp
WFDnsServer server([](WFDnsTask *task) {
    DnsResponse *resp = task->get_resp();
    // 添加资源记录...
});
server.start(53);  // UDP
~~~

## 添加资源记录
~~~cpp
// A 记录
resp->add_a_record(DNS_ANSWER_SECTION, name, DNS_CLASS_IN, 600, &addr);

// AAAA 记录
inet_pton(AF_INET6, "::1", &addr6);
resp->add_aaaa_record(DNS_ANSWER_SECTION, name, DNS_CLASS_IN, 600, &addr6);

// CNAME/PTR/NS/SOA/SRV/MX
resp->add_cname_record(...);
resp->add_soa_record(...);
resp->add_srv_record(...);
~~~

## TCP 服务
~~~cpp
WFServerParams params = HTTP_SERVER_PARAMS_DEFAULT;
params.transport_type = TT_TCP;
WFDnsServer server(&params, process);
~~~

## 截断标记
~~~cpp
resp->set_tc(1);  // 设置 TC 标记
// 客户端使用 TCP 重新请求
~~~

## 自定义记录类型
~~~cpp
// 使用 add_raw_record 添加未支持的类型（如 TXT）
resp->add_raw_record(DNS_ANSWER_SECTION, name, DNS_TYPE_TXT,
                     DNS_CLASS_IN, 1200, raw_data, data_len);
~~~

## 相关概念
- [[entities/cpp/workflow/workflow-dns-server]] — DNS 服务器
- [[entities/cpp/workflow/workflow-dns]] — DNS 客户端