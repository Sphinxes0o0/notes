---
type: entity
tags: [C++异步框架, DNS服务器, WFDnsServer, 资源记录]
created: 2026-05-27
sources: [workflow-engine]
---

# Workflow 教程 19: DNS Server

## 概述
`tutorial-19-dns_server` 展示如何使用 Workflow 实现 DNS 服务器。

## 创建 DNS 服务器
~~~cpp
using WFDnsServer = WFServer<DnsRequest, DnsResponse>;
WFDnsServer server([](DNS::WFDnsTask *task) {
    // 处理 DNS 请求
});
server.start(port);
~~~

## 添加资源记录
### A 记录（IPv4）
~~~cpp
struct in_addr addr;
inet_pton(AF_INET, "192.168.1.1", &addr);
resp->add_a_record(DNS_ANSWER_SECTION, name.c_str(),
                   DNS_CLASS_IN, 600, &addr);
~~~

### AAAA 记录（IPv6）
~~~cpp
struct in6_addr addr;
inet_pton(AF_INET6, "1234:5678::", &addr);
resp->add_aaaa_record(DNS_ANSWER_SECTION, name.c_str(),
                      DNS_CLASS_IN, 600, &addr);
~~~

### 其他记录类型
- `add_cname_record()` — CNAME
- `add_ns_record()` — NS
- `add_ptr_record()` — PTR
- `add_soa_record()` — SOA
- `add_srv_record()` — SRV
- `add_mx_record()` — MX
- `add_raw_record()` — 自定义类型（TXT 等）

## 截断标志
当响应过大时：
~~~cpp
resp->set_tc(1);  // 设置 TC 位
// 客户端将使用 TCP 重新请求
~~~

## 协议支持
- 默认 UDP
- 设置 `transport_type = TT_TCP` 启用 TCP

## 相关概念
- [[entities/cpp/workflow/workflow-dns-server]] — DNS Server 架构
- [[entities/cpp/workflow/workflow-dns]] — DNS 客户端与配置