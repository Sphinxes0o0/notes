# A2A 协议与 Agent IAM 能力边界研究报告

> **目标场景**: 汽车嵌入式 Agent IAM 开发  
> **参考来源**: Google A2A Protocol v1.0.0, Google ADK, A2A Specification  
> **补充参考**: GB/Z 185《人工智能 智能体互联》(指导性技术文件)

---

## 目录

1. [A2A 协议全景分析](#1-a2a-协议全景分析)
2. [IAM 在 Agent 系统中的能力边界](#2-iam-在-agent-系统中的能力边界)
3. [A2A 与 IAM 的配合模式](#3-a2a-与-iam-的配合模式)
4. [车端智能体发现的必要性分析](#4-车端智能体发现的必要性分析)
5. [智能体交互与工具调用的 IAM 管理](#5-智能体交互与工具调用的-iam-管理)
6. [车端嵌入式场景的架构建议](#6-车端嵌入式场景的架构建议)

---

## 1. A2A 协议全景分析

### 1.1 协议定位

A2A (Agent-to-Agent) 是 Google 贡献给 Linux Foundation 的开放协议，解决的是**不同厂商、不同框架、不同服务器上的 AI Agent 之间如何通信和协作**的问题。它是一种应用层协议，使用 HTTP/HTTPS 作为传输层，JSON-RPC 2.0 作为消息格式。

### 1.2 三层架构

A2A 规范分为三个正交层：

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: Canonical Data Model (Proto3)              │
│ Task, Message, Part, Artifact, AgentCard, Extension │
├─────────────────────────────────────────────────────┤
│ Layer 2: Abstract Operations                        │
│ SendMessage, SendStreamingMessage, GetTask,          │
│ ListTasks, CancelTask, GetAgentCard                  │
├─────────────────────────────────────────────────────┤
│ Layer 3: Protocol Bindings                          │
│ JSON-RPC 2.0, gRPC, HTTP+JSON/REST, Custom (MQTT…)  │
└─────────────────────────────────────────────────────┘
```

### 1.3 A2A 覆盖的能力（核心边界）

| 能力域 | 具体涵盖 | 在车端的适用性 |
|--------|---------|--------------|
| **智能体发现** | Agent Card 元数据、well-known URI、注册中心、直接配置 | ⭐⭐⭐ 关键 |
| **消息通信** | 同步 Request/Response、SSE 流式、异步 Push Notification | ⭐⭐⭐ 关键 |
| **任务管理** | 有状态任务生命周期 (submitted→working→completed/failed) | ⭐⭐ 重要 |
| **内容交换** | 文本、文件 (URL/inline bytes)、结构化数据 (JSON) | ⭐⭐⭐ 关键 |
| **能力协商** | Agent Card 中声明 Skills、输入/输出模式、扩展 | ⭐⭐ 重要 |
| **安全声明** | Agent Card 中声明 securitySchemes (OAuth2, API Key, mTLS) | ⭐⭐⭐ 关键 |
| **扩展机制** | 自定义数据、RPC 方法、状态机、Profile 叠加 | ⭐ 进阶 |
| **多租户** | 租户路由 (URL-based, Header-based, Body-based tenant field) | ⭐ 适用于多域控制器 |
| **协议绑定** | 支持自定义传输层绑定（如 MQTT for 车联网） | ⭐⭐⭐ 关键 |

### 1.4 A2A 明确不覆盖的（IAM 负责的）

| 不覆盖的领域 | 原因 | 谁负责 |
|-------------|------|--------|
| **身份认证实施** | A2A 只声明需要的 scheme，不实现 | **IAM** |
| **凭证发行/轮转/吊销** | 声明为 "Out-of-Band" (协议外) | **IAM** |
| **权限策略定义** | 由 Agent 实现方自行决定 | **IAM + 应用层** |
| **内部状态/记忆/工具** | 设计原则: Opaque Execution (不透明执行) | Agent 内部 |
| **LLM 工具调用 (MCP 域)** | A2A 管 Agent↔Agent，MCP 管 Agent↔Tool | MCP / Agent 内部 |
| **会话管理** | 仅有 contextId 做逻辑分组 | Agent 实现 |

### 1.5 核心通信模式

```
Client Agent                         Remote Agent (A2A Server)
    │                                       │
    │── 1. GET /.well-known/agent-card.json ──→│  (Agent Discovery)
    │←── AgentCard (skills, auth, url) ──────│
    │                                       │
    │── 2. OAuth2/Token Acquisition ──────────→│  (Out-of-Band IAM)
    │←── JWT/Token ─────────────────────────│
    │                                       │
    │── 3. POST /sendMessage (Bearer JWT) ────→│  (Task Start)
    │←── Task {id, contextId, status} ───────│
    │                                       │
    │── 4. POST /sendMessageStream ───────────→│  (Streaming)
    │←── SSE: StatusUpdate (working) ────────│
    │←── SSE: ArtifactUpdate (chunk 1) ──────│
    │←── SSE: StatusUpdate (completed) ───────│
    │                                       │
    │←── Push Notification (webhook) ─────────│  (Async)
```

---

## 2. IAM 在 Agent 系统中的能力边界

### 2.1 IAM 的定义与范围

在 Agent 系统中，IAM (Identity and Access Management) 负责以下五个支柱：

```
                    ┌──────────────┐
                    │   IAM 五大支柱 │
                    └──────┬───────┘
           ┌───────────────┼───────────────┐
           │               │               │
     ┌─────▼─────┐  ┌──────▼──────┐  ┌─────▼─────┐
     │  Identity  │  │Authentication│  │Authorization│
     │  身份标识   │  │   身份验证    │  │   权限控制   │
     └───────────┘  └─────────────┘  └───────────┘
           │               │               │
     ┌─────▼─────┐  ┌──────▼──────┐
     │   Audit    │  │  Credential  │
     │  审计追溯   │  │  凭证管理     │
     └───────────┘  └─────────────┘
```

### 2.2 Agent IAM 的特殊挑战

与传统的用户-IAM 相比，Agent IAM 有几个关键差异：

| 维度 | 传统 IAM (用户) | Agent IAM |
|------|----------------|-----------|
| 主体类型 | 人类用户 | Agent、Client App、User (委托) |
| 身份层级 | 单一身份 | 链式委托: User → Client → Agent → Sub-agent |
| 会话持续性 | 分钟-小时 | 可能极长 (LRO)，需支持 refresh/rotation |
| 权限粒度 | CRUD on resources | Skill-based + Data-scoped + Tool-scoped |
| 信任模型 | 边界清晰 | 多层代理，每层需要可信传递 |
| 交互模式 | 请求-响应 | 流式、异步回调、Push Notification |

### 2.3 IAM 在 Agent 生态中的三层作用域

```
Layer 3: Resource-Level Authorization
┌────────────────────────────────────────────┐
│  "这个 Agent 能不能读取 VIN=xxx 的车速数据？"  │
│  数据级权限、行级安全、属性级脱敏             │
└────────────────┬───────────────────────────┘
                 │
Layer 2: Skill/Tool-Level Authorization
┌────────────────────────────────────────────┐
│  "这个 Agent 能不能调用 read_engine_rpm 工具？"│
│  Agent Card 中声明 required OAuth scopes    │
└────────────────┬───────────────────────────┘
                 │
Layer 1: Transport/Connection-Level Auth
┌────────────────────────────────────────────┐
│  "这个连接的 TLS 证书是否有效？Bearer Token 是否合法？"│
│  TLS, mTLS, OAuth2, API Key                │
└────────────────────────────────────────────┘
```

### 2.4 IAM 明确不覆盖的（A2A 负责的）

| IAM 不负责 | 原因 |
|-----------|------|
| Agent 能力发现 | A2A Agent Card 负责 |
| Agent 间消息路由 | A2A 定义端点和方法 |
| 任务状态管理 | A2A Task 生命周期 |
| 内容格式协商 | A2A Part 类型和 MIME |

---

## 3. A2A 与 IAM 的配合模式

### 3.1 关键接口：Agent Card 中的安全声明

A2A 的 Agent Card 是 IAM 与 A2A 的**唯一耦合点**。Agent Card 中的安全声明告诉客户端"你需要什么样的凭证才能使用我"：

```json
{
  "name": "Vehicle Diagnostics Agent",
  "url": "https://diag.vehicle.local/a2a",
  "capabilities": { "streaming": true },
  "securitySchemes": {
    "oauth2": {
      "type": "oauth2",
      "flows": {
        "clientCredentials": {
          "tokenUrl": "https://iam.vehicle.local/oauth/token",
          "scopes": {
            "diag:read": "Read diagnostic data",
            "diag:actuate": "Control actuators"
          }
        }
      }
    }
  },
  "security": [{"oauth2": ["diag:read"]}],
  "skills": [
    {
      "id": "read_dtc",
      "name": "Read DTC",
      "description": "Read Diagnostic Trouble Codes",
      "tags": ["diagnostics", "read-only"]
    },
    {
      "id": "run_actuator_test",
      "name": "Run Actuator Test",
      "description": "Execute actuator diagnostic test",
      "tags": ["diagnostics", "actuation"],
      "security": [{"oauth2": ["diag:actuate"]}]
    }
  ]
}
```

**IAM 的职责**：管理 `tokenUrl` 端点、签发 Token、验证 Scope  
**A2A 的职责**：声明需求，不参与 Token 的签发/验证

### 3.2 核心配合流程

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │     │ IAM (AS) │     │  Agent   │     │  Tool/   │
│  Agent   │     │          │     │  Server  │     │  Resource│
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │               │                │
     │ 1. GET AgentCard               │                │
     │───────────────────────────────→│                │
     │← ─ ─ AgentCard (security req.) │                │
     │                │               │                │
     │ 2. Client Credentials Grant    │                │
     │───────────────→│               │                │
     │← ─ ─ JWT (scope=diag:read)    │                │
     │                │               │                │
     │ 3. POST /sendMessage (Bearer JWT)              │
     │───────────────────────────────→│                │
     │                │               │                │
     │                │    IAM 验证层  │                │
     │                │  (Token Introspection)         │
     │                │←──────────────│                │
     │                │─ ─ valid ✓ ─ ─→│                │
     │                │               │                │
     │                │               │ 4. MCP Tool Call
     │                │               │───────────────→│
     │                │               │  需要 diag:read │
     │                │               │← ─ ─ result ─ ─│
     │                │               │                │
     │                │   5. 如果需要更高权限的工具      │
     │                │               │                │
     │← ─ Task state: auth-required ─ ─│                │
     │                │               │                │
     │ 6. 获取更高权限 Token           │                │
     │───────────────→│               │                │
     │← ─ ─ JWT (+diag:actuate)       │                │
     │                │               │                │
     │ 7. 继续 Task (新 Token)         │                │
     │───────────────────────────────→│                │
```

### 3.3 In-Task Authentication（任务中途认证）

A2A 支持任务执行到一半时要求更高权限。Agent 返回 `auth-required` 或 `input-required` 状态，Client 从 IAM 获取新凭证后继续：

```
Task.status.state: "auth-required"
  → Client 去 IAM 获取新 scope 的 Token
  → Client 携带新 Token 继续 Task
  → Agent 继续执行
```

这对车端场景非常重要：**读取故障码**只需要 `diag:read`，但**执行执行器测试**需要 `diag:actuate`。IAM 实现逐步授权，避免一开始就给过高权限。

### 3.4 Push Notification 中的认证

当 Remote Agent 需要异步推送结果时，push notification 也带认证：

```json
{
  "pushNotificationConfig": {
    "url": "https://client.vehicle.local/webhook",
    "authentication": {
      "scheme": "bearer",
      "credentials": "eyJ..."
    }
  }
}
```

这意味着 IAM 需要支持 Agent 作为 OAuth2 Client 获取回调凭证。

---

## 4. 车端智能体发现的必要性分析

### 4.1 三种发现策略对比

| 策略 | 适用场景 | 车端适配度 |
|------|---------|-----------|
| **Well-Known URI** | 公网 Agent、同域动态发现 | ⭐⭐ 内部网络可用，但受限 |
| **Curated Registry** | 企业级、需要治理 | ⭐⭐⭐ 可作为车端 Agent Registry |
| **Direct Configuration** | 静态关系、预配置 | ⭐⭐⭐ 最实用，启动快 |

### 4.2 车端的特殊性

```
车端 Agent 拓扑 (典型):

┌──────────────────────────────────────────────────────────┐
│                   In-Vehicle Network (SOME/IP, DDS, etc.)  │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Infotain. │  │ Climate  │  │ ADAS     │  │ Battery  │  │
│  │  Agent    │  │  Agent   │  │  Agent   │  │  Agent   │  │
│  └─────┬─────┘  └─────┬────┘  └────┬─────┘  └────┬─────┘  │
│        │              │            │              │        │
│        └──────────────┼────────────┼──────────────┘        │
│                       │            │                       │
│              ┌────────▼────────────▼───────┐               │
│              │     Agent Orchestrator      │               │
│              │   (Gateway / Registry)      │               │
│              └─────────────┬───────────────┘               │
│                            │                               │
│              ┌─────────────▼───────────────┐               │
│              │      IAM Service (PKI)      │               │
│              └─────────────────────────────┘               │
│                                                           │
└──────────────────────────────────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  Cloud/Backend │
                    │  (Remote Agents)│
                    └───────────────┘
```

### 4.3 推荐策略：分层发现

| 层级 | 发现策略 | 原因 |
|------|---------|------|
| **L1: 车内固有 Agent** | Direct Configuration | 设计时已知，数量固定，Agent Card 预置在固件中 |
| **L2: OTA/动态安装的 Agent** | Well-Known URI + Registry | 新 Agent 安装后注册到车端 Registry |
| **L3: 云端 Remote Agent** | Registry (云端) | 通过车联网连接云端 Agent Marketplace |
| **L4: V2X 外部 Agent** | Well-Known URI (临时) | 路侧设备、其他车辆的 Agent，临时发现 |

### 4.4 GB/Z 185 视角

GB/Z 185《人工智能 智能体互联》作为中国的指导性技术文件，预计会规范智能体互联的架构、接口和安全要求。从已有信息推测：

- **智能体标识**: 要求每个智能体有唯一标识（对应 A2A 的 Agent Card name/url）
- **能力描述**: 要求定义能力描述方式（对应 A2A 的 Skills）
- **互联安全**: 要求互联过程中的身份认证和授权（对应 A2A 的 securitySchemes + IAM）
- **发现机制**: 可能推荐注册中心模式，适合中国车联网标准体系

**建议**: GB/Z 185 的注册中心模式最适合车端。每个域控制器上的 Agent 在启动时向车端 Registry 注册，Orchestrator 通过 Registry 发现可用 Agent。

---

## 5. 智能体交互与工具调用的 IAM 管理

### 5.1 核心原则：A2A ≠ MCP

这是最容易混淆的地方，必须厘清：

```
┌──────────────────────────────────────────────────────┐
│                                                        │
│   Agent A ──A2A──→ Agent B   (智能体之间协作)         │
│       │                    │                           │
│       │                    │                           │
│     MCP                  MCP                           │
│       │                    │                           │
│       ▼                    ▼                           │
│   Tool 1, Tool 2     Tool 3, Tool 4  (智能体调用工具) │
│                                                        │
└──────────────────────────────────────────────────────┘

- A2A: 状态化、对话式、可协商、长时间运行
- MCP: 无状态、函数调用式、结构化输入输出、短时完成
```

**IAM 对 A2A 交互的管理**: 管理 Agent A 是否有权调用 Agent B  
**IAM 对 Tool 调用的管理**: 管理 Agent 是否有权使用特定 Tool（这是 MCP 层或 Agent 内部的事，非 A2A 协议范围）

### 5.2 工具调用的 IAM 模型

车端每个 Tool/Skill 都应该有对应的权限声明：

```
Tools Catalog (IAM 管理):
┌────────────────────────────────────────────────────────────┐
│ Tool ID          │ Required Scope      │ Risk Level       │
├──────────────────┼─────────────────────┼──────────────────┤
│ read_speed       │ sensors:read        │ Low              │
│ read_gps         │ location:read       │ Medium (privacy) │
│ read_engine_rpm  │ diag:read           │ Low              │
│ actuate_brake    │ control:brake       │ Critical         │
│ actuate_steering │ control:steering    │ Critical         │
│ unlock_door      │ body:control        │ High             │
│ read_cabin_temp  │ climate:read        │ Low              │
│ set_cabin_temp   │ climate:write       │ Low              │
│ flash_ecu         │ diag:write         │ High             │
│ read_vin         │ identity:read       │ Medium (privacy) │
└────────────────────────────────────────────────────────────┘
```

### 5.3 A2A 中 IAM 对 Tool 调用的间接管理

虽然 A2A 不直接管理 Tool 调用，但通过以下机制间接影响：

1. **Skill-Based Authorization**: Agent Card 中每个 Skill 可以声明需要的 scope
2. **In-Task Escalation**: 任务中途可以要求提升权限
3. **Opaque Execution**: Remote Agent 的 Tool 调用对 Client 不可见，但被 IAM 的策略约束

```
Client Agent 视角:
  "我调用 Climate Agent 的 set_temperature skill"
  → 我需要 climate:write scope 的 Token
  → 我不需要知道 Climate Agent 内部用了什么 Tool

Climate Agent 内部 (对 Client 不透明):
  IAM Policy: "Climate Agent 可以用 set_hvac_actuator Tool"
  → Agent 自身身份被授权调用 MCP Tool
  → Client 的身份不影响 Agent 内部的 Tool 授权
```

### 5.4 车端推荐的 IAM 策略模型

```yaml
# 车端 IAM Policy 层次结构

# Level 1: Agent Identity (A2A 层)
agent_policies:
  - agent_id: "climate-agent"
    allowed_callers: ["orchestrator-agent", "voice-agent"]
    max_token_ttl: 3600s
    
  - agent_id: "adas-agent"  
    allowed_callers: ["orchestrator-agent"]
    require_user_confirmation: true  # 关键操作需用户确认
    max_token_ttl: 300s

# Level 2: Skill Authorization (A2A Agent Card 层)  
skill_policies:
  - skill_id: "set_temperature"
    required_scopes: ["climate:write"]
    rate_limit: 10/min
    
  - skill_id: "emergency_brake"
    required_scopes: ["control:brake"]
    require_user_confirmation: true
    audit_level: "full"  # 完整审计

# Level 3: Tool Authorization (MCP/Agent 内部层)
tool_policies:
  - tool_id: "actuate_brake"
    allowed_agents: ["adas-agent"]
    require_safety_check: true
    audit_level: "full"
```

---

## 6. 车端嵌入式场景的架构建议

### 6.1 推荐整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      VEHICLE IAM ARCHITECTURE                     │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    IAM Core Service (PKI)                    │ │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐ │ │
│  │  │ Token     │  │ Policy    │  │ Credential│  │ Audit    │ │ │
│  │  │ Service   │  │ Engine    │  │ Manager   │  │ Logger   │ │ │
│  │  │ (OAuth2)  │  │ (OPA/Rego)│  │ (x.509,   │  │          │ │ │
│  │  │           │  │           │  │  JWT轮转)  │  │          │ │ │
│  │  └───────────┘  └───────────┘  └───────────┘  └──────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   Agent Registry                            │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                 │ │
│  │  │ Local Registry   │  │ Remote Registry   │                │ │
│  │  │ (车内 Agent      │  │ (云端 Agent       │                │ │
│  │  │  Agent Card 索引)│  │  Agent Card 同步) │                │ │
│  │  └──────────────────┘  └──────────────────┘                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 Agent Orchestrator Gateway                   │ │
│  │  ┌───────────┐  ┌───────────┐  ┌────────────────────────┐   │ │
│  │  │ A2A       │  │ MCP       │  │ Protocol Adapters      │   │ │
│  │  │ Endpoint  │  │ Endpoint  │  │ (MQTT, SOME/IP, DDS)  │   │ │
│  │  └───────────┘  └───────────┘  └────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────────┐ │
│  │ Climate  │ │ ADAS     │ │ Infotain.│ │ External Service     │ │
│  │ Agent    │ │ Agent    │ │ Agent    │ │ Agent (Cloud, V2X)   │ │
│  │ + Card   │ │ + Card   │ │ + Card   │ │ + Card               │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 关键技术决策

| 决策点 | 推荐方案 | 理由 |
|--------|---------|------|
| **传输协议** | A2A over HTTP/2 (内部), MQTT (V2X) | 内部用标准协议，V2X 用轻量物联网协议 |
| **认证方式** | mTLS + OAuth2 Client Credentials | 设备间认证用证书，Agent 间用 Token |
| **Token 格式** | JWT (短 TTL) + 设备证书 (长 TTL) | 兼顾安全性和性能 |
| **权限模型** | RBAC + Scope-based + User Confirmation | 读操作用 RBAC，写/控制需 Scope + 用户确认 |
| **Agent 发现** | Direct Config (L1) + Local Registry (L2) | 设计时已知的用预配置，动态的用注册中心 |
| **协议绑定** | JSON-RPC 2.0 + Custom MQTT Binding | 符合 A2A 标准，同时支持车联网特性 |
| **审计** | 全量审计 critical 操作，采样审计 read 操作 | 平衡安全与存储 |

### 6.3 A2A Extension 建议：车端安全扩展

可以为车端场景定义自定义 A2A Extension：

```json
{
  "uri": "https://automotive.example.com/ext/safety-iam/v1",
  "description": "Automotive safety-grade IAM extension for vehicle agents",
  "required": true,
  "params": {
    "asil_level": "ASIL-B",
    "require_user_confirmation_for": ["control:brake", "control:steering"],
    "max_response_time_ms": 100,
    "safety_monitor_endpoint": "https://safety.vehicle.local/check"
  }
}
```

### 6.4 实施路线图建议

```
Phase 1: 基础 IAM
├── mTLS 设备间认证
├── Agent Card 静态配置
├── 直接配置发现
└── 基础 Token 服务

Phase 2: A2A + IAM 集成
├── OAuth2 Client Credentials Flow
├── Skill-based Authorization
├── Local Agent Registry
├── In-Task Authentication
└── Audit Logging

Phase 3: 高级能力
├── MQTT Custom Binding (V2X)
├── Safety Extension
├── 动态权限提升 + 用户确认
├── 跨车 Agent 协作 (V2V)
└── Cloud Agent Marketplace 集成
```

---

## 附录 A: 参考资源

| 资源 | 链接 |
|------|------|
| A2A 协议仓库 | https://github.com/google/A2A |
| A2A 协议规范 v1.0.0 | https://a2a-protocol.org/latest/specification/ |
| Google ADK | https://github.com/google/adk-python |
| A2A Python SDK | `pip install a2a-sdk` |
| MCP 协议 | https://modelcontextprotocol.io/ |
| GB/Z 185 | 人工智能 智能体互联 (中国国家标准指导性技术文件) |

## 附录 B: 关键术语对照

| 英文 | 中文 | 说明 |
|------|------|------|
| Agent Card | 智能体卡片 | Agent 的元数据描述文档 |
| Skill | 技能 | Agent 能执行的具体任务 |
| Task | 任务 | A2A 中的有状态工作单元 |
| Artifact | 产物 | Agent 执行任务后产生的输出 |
| Part | 内容片段 | Message/Artifact 中的最小内容单元 |
| Opaque Execution | 不透明执行 | Agent 内部状态对调用方不可见 |
| In-Task Auth | 任务中途认证 | 任务执行中提升权限的机制 |
| LRO | 长时运行操作 | Long-Running Operation |
| Well-Known URI | 已知路径发现 | RFC 8615 标准的服务发现方式 |
| Custom Binding | 自定义协议绑定 | 如 MQTT for IoT |
