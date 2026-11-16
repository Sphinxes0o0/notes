---
type: entity
tags: [C++异步框架, 负载均衡, 服务治理, 熔断]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow Upstream

## 定义
Upstream 是本地反向代理，提供负载均衡、熔断、服务治理能力。支持动态配置，实时生效。

## 核心特性
- **负载均衡策略**：
  - 权重随机（weighted random）
  - 一致性哈希（consistent hash）
  - 手动选取（manual）
  - VNSWRR（平滑加权轮询）
- **主备模式**：server_type 主/备分组
- **熔断机制**：连续失败 max_fails 次，熔断 30 秒（MTTR）
- **动态配置**：`upstream_add/remove_server()` 实时生效

## 地址类型
- IPv4 / IPv6
- 域名
- Unix Domain Socket

## Address 属性
| 属性 | 说明 |
|------|------|
| `endpoint_params` | 连接参数（超时、并发数） |
| `dns_ttl_default/min` | DNS TTL |
| `max_fails` | 熔断失败次数阈值 |
| `weight` | 权重 |
| `server_type` | 主(0)/备(1) |
| `group_id` | 分组 ID |

## 相关概念
- [[entities/cpp/workflow/workflow-service-governance]] — 服务治理
- [[entities/cpp/workflow/workflow-config]] — 全局配置
- [[entities/cpp/workflow/workflow-dns]] — DNS
