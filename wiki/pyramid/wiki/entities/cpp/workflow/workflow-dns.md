---
type: entity
tags: [C++异步框架, DNS, 域名解析]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow DNS

## 定义
Workflow 内置完整的 DNS 解析和缓存系统，支持异步/同步解析、DNS over TLS、hosts 文件。

## 关键要点
- **异步 DNS**：通过 `resolv.conf` 配置，默认启用
- **同步 DNS**：`resolv_conf_path=NULL` 时使用 `getaddrinfo()`
- **DNS over TLS**：配置 `dnss://` 前缀
- **缓存策略**：
  - TTL 到期前 5 秒自动更新
  - 异步锁保证同一域名同时只发起一次解析
- **配置项**：`dns_ttl_default`、`dns_ttl_min`、`dns_threads`
- **地址族**：`AF_INET` / `AF_INET6` 可强制仅解析 IPv4/IPv6

## 相关概念
- [[entities/cpp/workflow/workflow-upstream]] — Upstream 可覆盖 DNS 配置
- [[entities/cpp/workflow/workflow-service-governance]] — 服务治理
