# A2A 协议

> Agent-to-Agent Protocol — 让智能体之间像调用 REST API 一样优雅地协作。

## 是什么

A2A（Agent-to-Agent）是 Google 在 2025 年发起的**智能体间通信协议**（目前已发布 v1.0，捐赠给 Linux 基金会）。它的目标是：

- 让一个**客户端 Agent**（orchestrator / 个人助手）能发现并调用另一个**远程 Agent**（专项 agent），而**不需要知道**对方内部用了什么模型、什么框架、什么工具。
- 整个交互走**标准的 JSON-RPC / HTTP / gRPC**，而不是某个私有框架的 SDK。
- 远程 Agent 被视作"**不透明的黑盒**（opaque executor）"——你只看到它的 **Agent Card**（名片）和它产生的**消息 / 产物（Artifact）**。

## 为什么要它

在过去，Agent 生态主要是"**单体 + 工具**"模型：

```
┌──────────┐      tool calls        ┌─────────────┐
│  Agent   │ ────────────────────▶  │  API / DB   │
└──────────┘                        └─────────────┘
```

但随着任务越来越复杂，单个 Agent 不够用，**Agent 与 Agent 之间**也需要协作：

```
┌──────────┐      A2A       ┌──────────┐      A2A       ┌──────────┐
│ Planner  │ ─────────────▶ │  Travel  │ ─────────────▶ │  Hotel   │
│  Agent   │                │  Agent   │                │  Agent   │
└──────────┘                └──────────┘                └──────────┘
       │                          │                          │
       └────── MCP (tools) ───────┴────── MCP (tools) ───────┘
```

**A2A 与 MCP 是互补关系**，不是竞争：

| | MCP (Model Context Protocol) | A2A |
|--|--|--|
| 解决什么 | Agent ↔ 工具 / 资源 | Agent ↔ Agent |
| 调用方式 | 同步、结构化、无状态 | 异步、流式、有状态 |
| 颗粒度 | 一次函数调用 | 一个完整的"任务" |
| 状态 | 调用即返回 | 可能要 hours / days 完成 |
| 协议 | JSON-RPC over stdio/HTTP | JSON-RPC over HTTP(S) / gRPC / REST |

> **一句话总结**：MCP 让 Agent 拿工具，A2A 让 Agent 找帮手。

## 目录

本系列按照"**概念 → 协议 → 安全 → 实战**"四段式组织：

### 基础概念篇

1. **[01 · 入门：什么是 A2A 协议](01-introduction.md)** — 旅行规划场景、生活类比、第一个 Hello World JSON
2. **[02 · 核心概念](02-core-concepts.md)** — Actor、Agent Card、Task、Message / Part、Artifact、Context

### 协议篇

3. **[03 · 协议深度](03-protocol-deep-dive.md)** — 三层架构、JSON-RPC / gRPC / REST 绑定、Task 生命周期、流式与 Push Notification、错误码
4. **[04 · 安全与企业级](04-security-enterprise.md)** — TLS、身份验证、授权、Push Notification 安全、可观测性、API 管理

### 实战篇（手把手）

5. **[05 · 实战 1：Hello World](05-hands-on-helloworld.md)** — 从零写一个最简 A2A 服务端 + 客户端（纯 Python，不依赖完整 SDK）
6. **[06 · 实战 2：流式 + 多轮对话](06-hands-on-streaming.md)** — SSE 流式、`input-required` 状态、续写对话
7. **[07 · 实战 3：多 Agent 协作](07-hands-on-multi-agent.md)** — Orchestrator 编排 3 个子 Agent 完成旅行规划

所有可运行的 Python 示例在 [`examples/`](./examples/) 目录下，按文档编号一一对应。

## 阅读建议

- **5 分钟搞懂 A2A**：只看 `01-introduction.md` 的前两节。
- **半小时上手**：通读 `01` ~ `02`，然后照着 `05` 跑一遍 Hello World。
- **深入研究**：继续 `03`、`04`，再看 `06`、`07`。
- **生产落地**：先看 `04`，再考虑 `07` 的多 Agent 编排模式。

## 协议版本

本文基于 **A2A Protocol v1.0**（2025 年发布）。该版本兼容 v0.2.x 和 v0.3.x 的核心概念（Agent Card、Task、Part），主要新增内容：

- `contextId` 作为服务器端"会话粘合剂"（语义层）。
- 把 Agent 抽象成"独立进程"，允许不同的**传输层实现**（HTTP / gRPC / REST）。
- 引入 `A2A-Extensions` 头来承载**协议扩展**。
- 更严格的 JSON 命名（camelCase）与 ProtoJSON 兼容。