---
title: "LLM Agent 安全防御"
description: "围绕身份认证、分层防御和跨 Agent 授权组织的工程方案。方案中的实施清单用于说明落地工作，不代表本仓库提供生产实现。"
---

# LLM Agent 安全防御

围绕身份认证、分层防御和跨 Agent 授权组织的工程方案。方案中的实施清单用于说明落地工作，不代表本仓库提供生产实现。

## 车载 A2A 与 IAM

先读 [A2A 核心概念](../../a2a/02-core-concepts.md) 和 [SPIFFE 与 SPIRE 基础](../spiffe-book/ch04-introduction-to-spiffe-and-spire.md)，再按设计问题选择文档。

| 设计问题 | 文档 | 适用前提 |
| --- | --- | --- |
| 离线签发、凭证生命周期和跨域委托 | [车端 IAM 认证架构](./iam_auth_architecture.md) | 车内 AD/CD/VD，通过 KMSS lib 在 TEE 内执行密钥操作 |
| Agent 发现、任务状态及其与 IAM 的接点 | [车载 A2A 协议设计](./a2a_vehicle_protocol.md) | 面向车内三域，采用文中的 KMSS IAM 模型 |
| 对比凭证与协议对接方式 | [TEE + KMSS 部署](../../midware/a2a.md)、[SPIFFE/SPIRE 部署](../../midware/a2a_spiffe.md)、[IAM 集成](../../midware/a2a_iam_integration.md) | SPIRE 部署方案假设车内运行 SPIRE 组件，集成篇讨论 SPIRE 与 KMSS 双凭证 |
| 保持 A2A 消息结构和业务代码稳定 | [车载 IAM 零侵入设计](./a2a_iam_nonintrusive.md) | IAM 集成放在中间件、凭证传递和服务端策略层 |
| 评估允许扩展 Agent Card 或 Task 的环境 | [A2A + IAM 融合架构](./a2a_iam_integration_arch.md) | 部署方能协调通信两端的协议扩展 |
| 分析多跳、撤销时序及 gRPC 扩展 | [IAM 深度分析与 gRPC 演进](./a2a_iam_grpc_deep_dive.md) | 延伸自允许扩展 A2A 消息的融合架构 |

## 分层防御与 Guard

- [IAM + LLM Guard 详细架构与模块流程](./detailed_architecture.md)
- [LLM Agent 分层防御方案](./layered_defense.md)
