---
type: entity
tags: [云原生, Cloud Native, 容器, 微服务, CNCF]
created: 2026-05-28
sources: [bookmark-thebyte]
---

# 云原生 (Cloud Native)

## 定义

云原生是一套构建和运行应用程序的方法论，利用云计算模型的优势实现弹性、可扩展和自动化。

## 关键要点

### 云原生代表技术
1. **容器技术**: 轻量级虚拟化，一致性环境，[[container-technology]]
2. **微服务**: 服务拆分，独立部署，[[load-balancing]]服务发现
3. **服务网格**: [[service-mesh]]，边车代理，东西向流量治理
4. **不可变基础设施**: 容器镜像，基础设施即代码
5. **声明式API**: Desired State，[[kubernetes-orchestration]]
6. **DevOps**: CI/CD自动化

### 云原生架构演进
- **单体应用**: 紧耦合，部署困难
- **SOA**: 服务总线，ESB
- **微服务**: REST API，独立数据库，DevOps
- **云原生**: 容器化+微服务+服务网格+可观测+声明式API

### 云原生目标
- **容器化**: 任何环境一致运行
- **敏捷**: 快速迭代，弹性伸缩
- **可观测**: 指标/日志/链路追踪
- **自动化**: CI/CD，GitOps

## 相关概念
- [[container-technology]] — 容器技术（chroot→namespace→cgroups演进）
- [[kubernetes-orchestration]] — Kubernetes编排（云原生核心平台）
- [[service-mesh]] — 服务网格（边车代理模式）
- [[load-balancing]] — 负载均衡（微服务基础设施）
- [[paxos-consensus]] — 分布式共识（云原生数据库/etcd的理论基础）

## 来源详情
- [[bookmark-thebyte]] — 深入高可用系统原理与设计
