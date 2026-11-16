---
type: entity
tags: [C++异步框架, DNS服务器]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow DNS 服务器

## 定义
Workflow 支持创建 DNS Server，处理 DNS 查询请求。

## 支持记录类型
- A、AAAA、CNAME、PTR、NS、SOA、SRV、MX
- 通过 `add_*_record()` 添加

## 示例
~~~cpp
resp->add_a_record(DNS_ANSWER_SECTION, name, DNS_CLASS_IN, ttl, &addr);
resp->add_aaaa_record(DNS_ANSWER_SECTION, name, DNS_CLASS_IN, ttl, &addr6);
~~~

## 截断标记
- `resp->set_tc(1)` 设置 TC 标记
- 指示客户端使用 TCP 重新请求

## 相关概念
- [[entities/cpp/workflow/workflow-dns]] — DNS 客户端
- [[entities/cpp/workflow/workflow-http-server]] — HTTP 服务器
