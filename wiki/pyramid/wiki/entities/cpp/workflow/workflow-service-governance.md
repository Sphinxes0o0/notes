---
type: entity
tags: [C++异步框架, 服务治理, 负载均衡, 熔断]
created: 2026-05-25
sources: [workflow-engine]
---

# Workflow 服务治理

## 定义
服务治理模块管理依赖服务，包括 DNS、负载均衡、熔断恢复、主备关系等。

## 核心功能
1. **用户级 DNS**：自定义域名解析策略
2. **服务地址选取**：权重随机、一致性哈希、手动选择
3. **熔断与恢复**：连续失败触发熔断，MTTR=30s 后半开
4. **负载均衡**：多种策略
5. **独立参数配置**：每个目标可单独配置超时、并发数
6. **主备关系**：分组主备、自动切换

## Upstream 相比 DNS 优势
| 特性 | DNS | Upstream |
|------|-----|----------|
| 端口支持 | 不支持同 IP 不同端口 | 支持 |
| 地址类型 | 只能是 IP | IP/域名/Unix Socket |
| 更新生效 | 依赖 TTL | 实时 |
| 额外开销 | 解析开销 | 无 |

## 相关概念
- [[entities/cpp/workflow/workflow-upstream]] — Upstream 详细文档
- [[entities/cpp/workflow/workflow-dns]] — DNS
