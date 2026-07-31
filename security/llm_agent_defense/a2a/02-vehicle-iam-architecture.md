# 车端 Agent IAM 深度设计研究报告

> **目标**: 汽车嵌入式环境下的 Agent IAM 架构设计  
> **约束**: 无 OAuth2，使用 gRPC/HTTPS，基于 TEE + KMSS  
> **参考**: A2A Protocol v1.0.0, SPIFFE/SPIRE, ISO 21434, TCG TPM 2.0, GlobalPlatform TEE

---

## 目录

- [Part A: 车端 Agent IAM 独立深度设计](#part-a-车端-agent-iam-独立深度设计)
  - [A.1 什么是车端 Agent IAM — 定义与范围](#a1-什么是车端-agent-iam--定义与范围)
  - [A.2 为什么不能使用 OAuth2 — 车端约束分析](#a2-为什么不能使用-oauth2--车端约束分析)
  - [A.3 替代方案全景 — mTLS + 证书身份体系](#a3-替代方案全景--mtls--证书身份体系)
  - [A.4 TEE + KMSS 如何支撑 IAM](#a4-tee--kmss-如何支撑-iam)
  - [A.5 车端 IAM 架构设计](#a5-车端-iam-架构设计)
  - [A.6 Agent 身份模型](#a6-agent-身份模型)
  - [A.7 Agent 凭证管理全生命周期](#a7-agent-凭证管理全生命周期)
  - [A.8 权限策略引擎设计](#a8-权限策略引擎设计)
  - [A.9 审计与可追溯性](#a9-审计与可追溯性)
- [Part B: A2A + IAM 协作深度分析](#part-b-a2a--iam-协作深度分析)
  - [B.1 A2A 的安全模型回顾](#b1-a2a-的安全模型回顾)
  - [B.2 A2A 与 IAM 的能力边界（精确切割）](#b2-a2a-与-iam-的能力边界精确切割)
  - [B.3 A2A + IAM 交互流程详解](#b3-a2a--iam-交互流程详解)
  - [B.4 Agent Card 中的 mTLS 声明](#b4-agent-card-中的-mtls-声明)
  - [B.5 gRPC Binding 下的 IAM 集成](#b5-grpc-binding-下的-iam-集成)
  - [B.6 In-Task Authorization 的车端实现](#b6-in-task-authorization-的车端实现)
  - [B.7 完整请求链路追踪](#b7-完整请求链路追踪)

---

# Part A: 车端 Agent IAM 独立深度设计

---

## A.1 什么是车端 Agent IAM — 定义与范围

### 概念

**车端 Agent IAM** 是为车载嵌入式环境中的 AI Agent 设计的身份与访问管理系统。它与传统 IAM 的关键区别在于：**主体不是人类用户，而是软件 Agent**。

```
传统 IAM                         车端 Agent IAM
──────────                      ────────────────
主体: 人类用户                    主体: Agent 进程/服务
认证: 密码/WebAuthn/MFA          认证: mTLS 证书 + TEE 证明
授权: RBAC on resources         授权: Skill-based + Safety-level
会话: 浏览器 Cookie/JWT          会话: 证书绑定 + contextId
网络: 公网/企业网                 网络: 车内网络 (SOME/IP, DDS, gRPC)
约束: 合规/隐私                  约束: 实时性 + 功能安全 + 离线
```

### 车端 IAM 的核心职责

```
                    ┌──────────────────────────┐
                    │    车端 Agent IAM 职责      │
                    └──────────┬───────────────┘
           ┌───────────────────┼───────────────────┐
           │                   │                   │
    ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
    │  Agent 身份  │    │  凭证管理    │    │  权限决策    │
    │  发放与验证  │    │  全生命周期  │    │  实时鉴权    │
    └─────────────┘    └─────────────┘    └─────────────┘
           │                   │                   │
    ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
    │  信任根      │    │  策略管理    │    │  审计追溯    │
    │  TEE/TPM   │    │  OPA/Rego  │    │  不可篡改    │
    └─────────────┘    └─────────────┘    └─────────────┘
```

### 车端 Agent 的特殊属性

| 属性 | 传统服务 | 车端 Agent | IAM 影响 |
|------|---------|-----------|---------|
| 身份稳定性 | 服务实例可能随时替换 | Agent 与 ECU 绑定 | 身份需绑定硬件 |
| 调用模式 | 请求-响应为主 | 长时间流式 + 异步回调 | Token 需支持长 TTL + 流式续期 |
| 安全等级 | 按数据敏感度 | ASIL 功能安全等级 | 权限决策需考虑 ASIL |
| 离线能力 | 假设在线 | 必须支持离线工作 | 证书预置 + 定期同步 |
| 资源约束 | 计算资源充足 | Flash/RAM/CPU 受限 | 轻量级鉴权，避免复杂密码学 |

---

## A.2 为什么不能使用 OAuth2 — 车端约束分析

### OAuth2 的核心假设（全部被车端打破）

```
OAuth2 流程假设                    车端实际情况                 结论
─────────────────────────        ───────────────────        ──────────
1. 存在 Authorization Server     车内无独立网络可达的 AS       ❌ 不成立
   且网络可达

2. 用户有浏览器可交互             无座舱交互场景 (Agent-Agent)  ❌ 不成立
   (Authorization Code Flow)

3. Token 有短 TTL，可 Refresh     Token Refresh 需网络        ❌ 不成立
                                  (车辆可能长时间离线)

4. Token Introspection 低延迟     车内网络 ≠ 云原生网络         ❌ 性能不满足
                                  introspection ＞ 100ms 不可接受

5. 存在集中式用户目录 (LDAP/AD)   Agent 不是用户               ❌ 概念不适用
                                  没有 "用户名/密码" 概念

6. 多个第三方应用需要委托授权      车端 Agent 是 OEM 可控的     ❌ 需求不匹配
                                  不需要 "用户授权第三方" 范式
```

### 唯一可能的 OAuth2 场景：Client Credentials Grant

```
Agent ──→ IAM Server ──→ Token
         (client_id + client_secret)

问题:
- client_secret 如何安全存储？→ 需要安全存储 → 还是回到 TEE/KMSS
- Token 验证需要网络 introspection → 延迟不可接受
- client_secret 轮转机制复杂 → 容易出安全问题
```

### 根本结论

**OAuth2 是为 "用户授权第三方应用访问资源" 设计的委托协议。车端 Agent 间通信是 "已知身份的服务间调用"，根本不需要委托模型。** 正确的方法是：**身份由证书证明，权限由策略决策，Token 是证书的附属品而非独立凭证。**

---

## A.3 替代方案全景 — mTLS + 证书身份体系

### 方案对比

| 方案 | 原理 | 优势 | 劣势 | 车端适用性 |
|------|------|------|------|-----------|
| **mTLS + x.509** | 双方出示证书，双向验证 | 无中心依赖，离线可用，标准化 | 证书管理复杂 | ⭐⭐⭐⭐⭐ |
| **SPIFFE/SPIRE** | 基于 SPIFFE ID 的工作负载身份 | 自动轮转，标准身份格式 | 需要 SPIRE Agent，资源开销 | ⭐⭐⭐ (可裁剪) |
| **TEE 远程证明** | TEE 生成 attestation report | 硬件信任根，防篡改 | 需验证服务，平台绑定 | ⭐⭐⭐⭐ |
| **Kerberos** | 对称密钥 + Ticket | 成熟，离线 Ticket | 中心化 KDC | ⭐⭐ |
| **本地 Unix Socket** | 基于文件权限 | 最简单 | 仅限同一 ECU | ⭐⭐ |
| **DDS Security** | DDS 内置安全插件 | 与 AUTOSAR 集成好 | DDS 专用 | ⭐⭐⭐ |

### 推荐方案：mTLS + x.509 证书 + TEE 证明 (分层)

```
┌─────────────────────────────────────────────────────────────┐
│                     三层身份体系                               │
│                                                              │
│  Layer 3: Agent Identity (SPIFFE-style)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ spiffe://vehicle-{VIN}.local/domain/{domain}/agent/{name} │
│  │ 例: spiffe://vehicle-LSVN123.local/chassis/agent/adas   │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ▲                                 │
│  Layer 2: Certificate Identity (x.509 SAN)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ x.509 v3 Cert with SAN = SPIFFE ID                     │ │
│  │ Issuer: Vehicle Root CA (KMSS managed)                 │ │
│  │ Key Usage: digitalSignature, clientAuth, serverAuth    │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ▲                                 │
│  Layer 1: Hardware Root of Trust (TEE/TPM)                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ TEE (TrustZone/OPTEE) 保护私钥                           │ │
│  │ KMSS 管理 CA 证书链和密钥生命周期                          │ │
│  │ TPM 提供平台完整性度量 (PCR values)                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## A.4 TEE + KMSS 如何支撑 IAM

> **TEE + KMSS 是车端 IAM 的信任根。** TEE 提供硬件级私钥保护和远程证明能力，KMSS 作为车载 PKI (CA 层次、证书签发、CRL 管理) 运行在 TEE 安全域中。
>
> 详细设计见:
> - [iam_auth_architecture.md §6](/security/llm_agent_defense/iam_auth_architecture) — KMSS lib API 定义
> - [iam_auth_architecture.md §14](/security/llm_agent_defense/iam_auth_architecture) — 凭据管理 (密钥分层、Trust Bundle、CRL、Wrapped Secret)
> - [a2a/03 §1](/security/llm_agent_defense/a2a/03-kmss-opa-auth-required) — CA 层次设计 + 证书签发协议细节
>
> **核心要点**: TEE 中生成密钥对 (私钥永不离片) → KMSS 验证 TEE Attestation → 签发 x.509 证书 (含 SPIFFE ID) → Agent 获得身份凭证 → 启动 mTLS gRPC Server。

---

## A.5 车端 IAM 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                      VEHICLE IAM ARCHITECTURE                        │
│                    (TEE + KMSS + mTLS + gRPC)                        │
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │                     KMSS (Secure Domain)                          │ │
│ │  ┌────────────┐  ┌────────────┐  ┌──────────┐  ┌──────────────┐ │ │
│ │  │ Root CA    │  │ Certificate│  │ Key      │  │ Attestation  │ │ │
│ │  │ (TEE 密封) │  │ Issuer     │  │ Lifecycle│  │ Verifier     │ │ │
│ │  └────────────┘  └────────────┘  └──────────┘  └──────────────┘ │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │                   IAM Decision Service                            │ │
│ │  ┌────────────┐  ┌──────────────┐  ┌────────────────────────────┐│ │
│ │  │ Identity   │  │ Policy       │  │ Audit Logger               ││ │
│ │  │ Resolver   │  │ Engine (OPA) │  │ (Append-only, TEE 签名)    ││ │
│ │  │            │  │              │  │                            ││ │
│ │  │ SPIFFE ID  │  │ Rego policies│  │ 记录: who+what+when+result ││ │
│ │  │ → Agent    │  │ + ASIL rules │  │ 防篡改: HMAC chain         ││ │
│ │  └────────────┘  └──────────────┘  └────────────────────────────┘│ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │                   Agent Runtime (per Domain/ECU)                  │ │
│ │                                                                    │ │
│ │  ┌──────────────────┐    ┌──────────────────┐                    │ │
│ │  │ Climate Agent    │    │ ADAS Agent       │                    │ │
│ │  │ (gRPC Server)    │    │ (gRPC Server)    │                    │ │
│ │  │                  │    │                  │                    │ │
│ │  │ ┌──────────────┐ │    │ ┌──────────────┐ │                    │ │
│ │  │ │ TEE Key Store│ │    │ │ TEE Key Store│ │                    │ │
│ │  │ │ (私钥+证书)  │ │    │ │ (私钥+证书)  │ │                    │ │
│ │  │ └──────────────┘ │    │ └──────────────┘ │                    │ │
│ │  │                  │    │                  │                    │ │
│ │  │ ┌──────────────┐ │    │ ┌──────────────┐ │                    │ │
│ │  │ │ IAM Sidecar  │ │    │ │ IAM Sidecar  │ │                    │ │
│ │  │ │ (Authz Lib)  │ │    │ │ (Authz Lib)  │ │                    │ │
│ │  │ └──────────────┘ │    │ └──────────────┘ │                    │ │
│ │  └──────────────────┘    └──────────────────┘                    │ │
│ └──────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 为什么用 Sidecar 模式？

在车端，每个 Agent 进程内嵌 IAM 鉴权库（不是独立进程的 Sidecar，而是编译链接的 library）：

1. **零网络延迟**: 策略决策在进程内完成，不需要跨进程/跨网络调用
2. **离线可用**: 策略和撤销列表 (CRL) 定期同步到本地缓存
3. **故障隔离**: IAM 库故障只影响本 Agent，不传播
4. **资源友好**: 不需要额外的容器/进程开销

---

## A.6 Agent 身份模型

### 身份层次

```
spiffe://vehicle-{VIN}.local/{domain}/{component-type}/{component-name}

字段分解:
┌─────────────────────────────────────────────────────────────────┐
│ spiffe://vehicle-LSVN123456.local/chassis/agent/adas-controller │
│          │                      │       │            │          │
│          │                      │       │            │          │
│    Trust Domain          Domain   Type     Name                 │
│    (VIN 绑定)          (功能域)  (组件类型) (组件名)              │
└─────────────────────────────────────────────────────────────────┘

Domains:
  chassis/     - 底盘域 (制动、转向、悬挂)
  powertrain/  - 动力域 (发动机、变速箱、电池)
  body/        - 车身域 (门窗、灯光、座椅)
  infotainment/- 信息娱乐域 (导航、媒体、语音)
  adas/        - 高级辅助驾驶域
  connectivity/- 连接域 (T-Box, V2X)
  security/    - 安全域 (IAM, KMSS, Firewall)

Component Types:
  agent/     - AI Agent 进程
  service/   - 传统服务/微服务
  tool/      - MCP Tool 端点
  gateway/   - 协议网关
  registry/  - 注册中心
```

### 身份与证书的映射

```yaml
# Agent 的 x.509 证书结构
certificate:
  subject:
    CN: "adas-controller.agent.chassis.vehicle-LSVN123456"
    OU: "chassis"              # 功能域
    O: "vehicle-LSVN123456"    # 车辆标识
  subjectAltName:
    - URI: "spiffe://vehicle-LSVN123456.local/chassis/agent/adas-controller"
  extensions:
    - type: "agent_role"
      value: "controller"
    - type: "asil_level"
      value: "ASIL-D"          # 功能安全等级
    - type: "tee_attested"
      value: true              # 是否经过 TEE 证明
    - type: "firmware_hash"
      value: "sha256:abc123..."# Agent 固件度量值
  validity:
    notBefore: "2025-01-01T00:00:00Z"
    notAfter:  "2025-01-02T00:00:00Z"  # 24h 短期证书
  keyUsage:
    - digitalSignature
    - keyEncipherment
  extendedKeyUsage:
    - clientAuth
    - serverAuth
```

---

## A.7 Agent 凭证管理全生命周期

> **x.509 证书全生命周期（签发→续期→轮转→吊销）由 KMSS 统一管理。**
>
> 详细设计见:
> - [iam_auth_architecture.md §7](/security/llm_agent_defense/iam_auth_architecture) — 签发→使用→销毁流程 + Silent Renew + Revocation
> - [iam_auth_architecture.md §14](/security/llm_agent_defense/iam_auth_architecture) — 凭据管理 (密钥分层 L0-L3、Trust Bundle、密钥轮换、CRL 推送)
> - [a2a/03 §1.4-1.5](/security/llm_agent_defense/a2a/03-kmss-opa-auth-required) — CA 侧续期协议 + CRL 结构详情
>
> **核心要点**: 证书 24h 短有效期 → T-2h 自动续期 → 原子替换（新旧证书共存）→ 零停机。吊销通过 CRL push (< 1s) + 本地缓存实现。

---

## A.8 权限策略引擎设计

### 策略模型

```
策略决策输入:
┌────────────────────────────────────────────────────────────┐
│ Input: {                                                    │
│   caller: {                                                 │
│     spiffe_id: "spiffe://vehicle-.../infotainment/agent/    │
│                 voice-assistant",                           │
│     domain: "infotainment",                                 │
│     asil_level: "QM",         # Quality Managed (非安全)   │
│     certificate_fingerprint: "sha256:def456...",           │
│     tee_attested: true                                      │
│   },                                                        │
│   target: {                                                 │
│     spiffe_id: "spiffe://vehicle-.../chassis/agent/         │
│                 brake-controller",                          │
│     domain: "chassis",                                      │
│     asil_level: "ASIL-D",      # 最高安全等级               │
│   },                                                        │
│   action: {                                                 │
│     type: "skill_invoke",      # skill_invoke | tool_call   │
│                               # | data_read | data_write    │
│     skill_id: "emergency_brake",                            │
│     parameters: { "force": 0.8 }                            │
│   },                                                        │
│   context: {                                                │
│     time: "2025-07-31T14:30:00Z",                           │
│     vehicle_state: "moving",     # parked | moving | charging│
│     vehicle_speed_kmh: 80,                                  │
│     user_confirmed: false,                                  │
│   }                                                         │
│ }                                                           │
└────────────────────────────────────────────────────────────┘
```

### Rego 策略示例

```rego
# policy/agent-authz.rego

package vehicle.iam.authz

# ============================================================
# Rule 1: 域间隔离 - 低安全域不能调用高安全域的关键操作
# ============================================================
default allow = false

allow {
    # 同域内通信默认允许
    input.caller.domain == input.target.domain
}

allow {
    # 跨域通信需满足:
    # 1. 调用方有 user_confirmed
    # 2. 不是安全关键操作
    input.caller.domain != input.target.domain
    not is_safety_critical_action
}

# ============================================================
# Rule 2: ASIL 级别约束
# ============================================================
is_safety_critical_action {
    input.target.asil_level in {"ASIL-C", "ASIL-D"}
    input.action.type == "skill_invoke"
    input.action.skill_id in safety_critical_skills
}

safety_critical_skills = {
    "emergency_brake",
    "steering_override",
    "engine_kill",
    "airbag_deploy",
}

# ============================================================
# Rule 3: 用户确认门控
# ============================================================
allow {
    is_safety_critical_action
    input.caller.domain == "infotainment"
    input.context.user_confirmed == true
    input.context.vehicle_state != "moving"
}

# ============================================================
# Rule 4: TEE 证明检查
# ============================================================
allow {
    input.target.asil_level in {"ASIL-B", "ASIL-C", "ASIL-D"}
    input.caller.tee_attested == true
}

# ============================================================
# Rule 5: 数据读写权限
# ============================================================
allow {
    input.action.type == "data_read"
    input.caller.domain == input.target.domain
}

allow {
    input.action.type == "data_read"
    data_sharing_allowed[input.caller.domain][input.target.domain]
}

data_sharing_allowed = {
    "infotainment": {"body", "powertrain"},  # 信息娱乐可以读车身和动力数据
    "adas": {"chassis", "body"},             # ADAS 可以读底盘和车身
    "chassis": set(),                        # 底盘不向外共享数据
}

# ============================================================
# Rule 6: 速率限制
# ============================================================
allow {
    input.action.type == "skill_invoke"
    not rate_limit_exceeded
}

rate_limit_exceeded {
    skill_limits := {
        "read_speed": {"max_per_second": 100},
        "actuate_brake": {"max_per_second": 10},
        "read_gps": {"max_per_second": 1},
    }
    limit := skill_limits[input.action.skill_id]
    current_rate := data.ratelimit.count(input.caller.spiffe_id, input.action.skill_id)
    current_rate > limit.max_per_second
}
```

### 策略分发架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Policy       │     │ Policy Cache │     │ OPA Engine   │
│ Authoring    │────→│ (per Agent)  │────→│ (in-process) │
│ (OEM Cloud)  │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                     │
       │                    │                     │
  OTA 更新              KMSS 签名              实时决策
  (签名的 Policy        (防篡改)              (< 1ms)
   Bundle)
```

---

## A.9 审计与可追溯性

### 审计日志结构

```json
{
  "audit_log_entry": {
    "id": "audit-20250731-143000-00001",
    "timestamp": "2025-07-31T14:30:00.123Z",
    "decision": "DENY",
    "reason": "safety_critical_action_without_user_confirmation",
    "caller": {
      "spiffe_id": "spiffe://vehicle-LSVN123.local/infotainment/agent/voice-assistant",
      "certificate_serial": "0x04A3F2",
      "domain": "infotainment"
    },
    "target": {
      "spiffe_id": "spiffe://vehicle-LSVN123.local/chassis/agent/brake-controller",
      "skill_id": "emergency_brake",
      "domain": "chassis",
      "asil_level": "ASIL-D"
    },
    "context": {
      "vehicle_speed_kmh": 80,
      "vehicle_state": "moving",
      "user_confirmed": false
    },
    "trace_id": "a2a-trace-abc123",
    "tpm_pcr_values": {
      "pcr0": "sha256:abc...",
      "pcr7": "sha256:def..."
    },
    "hmac": "sha256:xxx..."  // 链式 HMAC 防篡改
  }
}
```

### 防篡改机制

```
链式 HMAC 结构:

Audit Entry 1                Audit Entry 2                Audit Entry 3
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ data: {...}      │         │ data: {...}      │         │ data: {...}      │
│ prev_hmac: null  │         │ prev_hmac: H1     │         │ prev_hmac: H2    │
│ hmac: H1 =       │ ───────→│ hmac: H2 =        │ ───────→│ hmac: H3 =       │
│   HMAC(k, data)  │         │   HMAC(k, data    │         │   HMAC(k, data   │
│                  │         │    + prev_hmac)   │         │    + prev_hmac)  │
└─────────────────┘         └─────────────────┘         └─────────────────┘

密钥 k 在 TEE 中密封存储
修改任何一条记录 → 所有后续 HMAC 失效 → 可检测
```

---

# Part B: A2A + IAM 协作深度分析

---

## B.1 A2A 的安全模型回顾

### A2A 对安全的核心立场（摘自规范 Section 7）

```
A2A 的安全哲学 (规范原文):

1. "A2A treats agents as standard enterprise applications, 
    relying on established web security practices."

2. "Identity information is handled at the protocol layer, 
    NOT within A2A semantics."

3. "Authentication requirements are advertised by the A2A 
    server in its Agent Card."

4. "The A2A Client obtains the necessary credentials through 
    processes EXTERNAL to the A2A protocol itself."

5. "Credentials MUST be transmitted in standard HTTP headers
    (or gRPC metadata), NOT in A2A payload."
```

### A2A 支持的安全方案 (规范 Section 4.5)

A2A 的 `AgentCard.securitySchemes` 原生支持：

| Scheme 类型 | 规范定义 | 车端可行性 |
|------------|---------|-----------|
| `APIKeySecurityScheme` | API Key in header | ⭐ 不推荐 (静态凭据) |
| `HTTPAuthSecurityScheme` | HTTP Basic/Bearer/其他 | ⭐⭐ 可用于简单场景 |
| `OAuth2SecurityScheme` | OAuth2 flows | ❌ 车端不可行 |
| `OpenIdConnectSecurityScheme` | OpenID Connect | ❌ 需要浏览器交互 |
| **`MutualTlsSecurityScheme`** | **mTLS 证书验证** | **⭐⭐⭐⭐⭐ 车端最佳选择** |

**关键发现**: A2A 规范原生支持 mTLS！这意味着我们的车端 mTLS IAM 方案与 A2A 是原生兼容的。

---

## B.2 A2A 与 IAM 的能力边界（精确切割）

```
                    A2A 的领地                  IAM 的领地
               ┌──────────────────┐    ┌──────────────────────────┐
               │                  │    │                          │
  Agent Card   │  securitySchemes │◄───│  mTLS 证书签发            │
  中的声明     │  (声明需要什么)   │    │  策略定义 (Rego)          │
               │                  │    │  ASIL 等级决定           │
               └────────┬─────────┘    └──────────┬───────────────┘
                        │                         │
                        │   "我要求 mTLS"          │  "我已经给你发了证书"
                        │                         │
               ┌────────▼─────────┐    ┌──────────▼───────────────┐
               │                  │    │                          │
  A2A Transport│ gRPC over TLS    │    │  证书验证 (TLS Handshake) │
  Layer        │ 或 HTTPS          │    │  CRL 检查                │
               │ (传输字节)        │    │  SPIFFE ID 解析          │
               └────────┬─────────┘    └──────────┬───────────────┘
                        │                         │
                        │  "我收到了 A2A 请求"     │  "请求方身份已验证"
                        │                         │
               ┌────────▼─────────┐    ┌──────────▼───────────────┐
               │                  │    │                          │
  A2A Method   │ SendMessage      │    │  Skill 权限检查          │
  Dispatch     │ GetTask          │    │  OPA/Rego 策略评估       │
               │ CancelTask       │    │  审计日志记录            │
               └────────┬─────────┘    └──────────┬───────────────┘
                        │                         │
                        │  "我可以处理这个请求"     │  "调用方有权执行此 Skill"
                        │                         │
               ┌────────▼─────────┐    ┌──────────▼───────────────┐
               │                  │    │                          │
  A2A Task     │ Task 状态管理     │    │  In-Task 权限提升        │
  Execution    │ Artifact 生成    │    │  (TASK_STATE_AUTH_REQUIRED)│
               │ 流式响应         │    │  用户确认门控            │
               └──────────────────┘    └──────────────────────────┘
```

### 精确的能力边界表

| 能力 | A2A 做什么 | IAM 做什么 | 如何交互 |
|------|-----------|-----------|---------|
| **身份声明** | Agent Card 中声明支持的 `securitySchemes` | 为 Agent 签发 x.509 证书 (SPIFFE ID) | Agent Card 中设置 `MutualTlsSecurityScheme` |
| **身份验证** | 建立 TLS/mTLS 连接 (传输层) | 验证证书链 + CRL + TEE Attestation | gRPC interceptor 从 mTLS session 提取身份 |
| **权限声明** | Agent Card 中声明 `skills[].security` (需要的 scope) | 定义每个 Skill/Tool 的权限要求 (Rego policy) | Agent Card 的 skill.security 字段与 IAM scope 对齐 |
| **权限决策** | 不参与 | OPA 引擎实时决策 | A2A Server 在处理请求前调用 IAM sidecar |
| **凭证传输** | HTTP Header / gRPC metadata | 在 TLS Handshake 中自动传输证书 | 无需额外 header |
| **凭证轮转** | 不参与 | KMSS 自动签发新证书 | TLS session 自动使用新证书 |
| **Task 中途授权** | 返回 `TASK_STATE_AUTH_REQUIRED` | 提供权限提升机制 (用户确认 / 新证书) | A2A 通知 Client 需要更多权限 |
| **审计** | 不参与 (但保留 traceId) | 全量审计日志 | A2A 的 traceId 传递到 IAM 审计日志中 |

---

## B.3 A2A + IAM 交互流程详解

### B.3.1 启动阶段: Agent 获取身份

```
Agent 启动 → TEE 证明 → KMSS 签发证书 → Agent 拥有 SPIFFE 身份

时序:

Agent (adas-controller)       TEE           KMSS
     │                         │              │
     │ 1. 启动请求              │              │
     │────────────────────────→│              │
     │                         │              │
     │ 2. 生成 TEE Attestation │              │
     │    Report               │              │
     │←────────────────────────│              │
     │                         │              │
     │ 3. 携带 Attestation Report             │
     │    请求签发 Agent 证书    │              │
     │────────────────────────────────────────→│
     │                         │              │
     │                         │ 4. 验证:     │
     │                         │    - Report 签名 │
     │                         │    - 代码度量值  │
     │                         │    - 平台状态    │
     │                         │              │
     │                         │ 5. 签发证书  │
     │←────────────────────────────────────────│
     │ 6. 收到 x.509 证书 + 信任链              │
     │    SAN: spiffe://.../chassis/agent/adas │
     │                         │              │
     │ 7. 私钥在 TEE 中密封存储  │              │
     │────────────────────────→│              │
```

### B.3.2 服务启动: 发布 Agent Card + 启动 gRPC Server

```
Agent 加载配置 → 生成 Agent Card → 启动 gRPC Server with mTLS

配置文件 (agent-config.yaml):
```yaml
agent:
  name: "ADAS Controller"
  spiffe_id: "spiffe://vehicle-LSVN123.local/chassis/agent/adas-controller"
  
a2a:
  agent_card_path: "/etc/agent/card.json"
  grpc:
    listen: "0.0.0.0:8443"
    tls:
      cert_file: "/etc/agent/cert.pem"       # 由 KMSS 签发
      key_handle: "tee://key/agent-adas"      # TEE 密钥句柄
      ca_file: "/etc/agent/ca-chain.pem"      # 车辆 CA 链
      require_client_cert: true               # 强制 mTLS
      
iam:
  policy_engine: "embedded-opa"
  policy_path: "/etc/agent/policy.rego"
  crl_path: "/etc/agent/crl.pem"
  audit_log: "/var/log/agent/audit.log"
```

生成的 Agent Card:
```json
{
  "name": "ADAS Controller",
  "description": "Vehicle ADAS domain agent - emergency braking, lane keeping, adaptive cruise",
  "version": "1.0.0",
  "supportedInterfaces": [
    {
      "url": "https://adas.chassis.vehicle.local:8443",
      "protocolBinding": "GRPC",
      "protocolVersion": "1.0"
    }
  ],
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "extendedAgentCard": true
  },
  "securitySchemes": {
    "mutualTls": {
      "type": "mutualTls",
      "description": "Vehicle PKI mTLS - certificates issued by Vehicle Root CA via KMSS"
    }
  },
  "security": [{"mutualTls": []}],
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain", "application/json"],
  "skills": [
    {
      "id": "emergency_brake",
      "name": "Emergency Brake",
      "description": "Execute emergency braking maneuver",
      "tags": ["safety", "ASIL-D", "critical"],
      "inputModes": ["application/json"],
      "outputModes": ["application/json"],
      "security": [{"mutualTls": []}]
    },
    {
      "id": "read_vehicle_speed",
      "name": "Read Vehicle Speed",
      "description": "Get current vehicle speed from wheel sensors",
      "tags": ["sensors", "read-only"],
      "inputModes": ["text/plain"],
      "outputModes": ["application/json"]
    }
  ]
}
```

### B.3.3 请求阶段: 完整的 A2A + IAM 调用链路

```
Voice Assistant Agent → ADAS Controller Agent (跨域，ASIL-D 操作)

完整序列:

 Voice Agent       KMSS/CA        IAM(Opa)     ADAS Agent(gRPC)    TEE
 (infotainment)    (trust)        (policy)     (chassis)
     │                │              │              │               │
     │── 0. Agent Discovery ──────────────────────→│               │
     │   GET /.well-known/agent-card.json          │               │
     │←── AgentCard (security: mutualTls) ─────────│               │
     │                │              │              │               │
     │   (Voice Agent 已有 KMSS 签发的证书)          │               │
     │                │              │              │               │
     │── 1. gRPC Dial with mTLS ──────────────────→│               │
     │   ClientCert: voice-agent.crt              │               │
     │   ServerCert: adas-agent.crt               │               │
     │                │              │              │               │
     │                │              │  2. gRPC Interceptor         │
     │                │              │     - 验证 Client Cert 链    │
     │                │              │     - 解析 SPIFFE ID:        │
     │                │              │       voice-assistant        │
     │                │              │     - 检查 CRL 吊销状态      │
     │                │              │     - 提取:                  │
     │                │              │       · domain=infotainment  │
     │                │              │       · asil=QM              │
     │                │              │       · tee_attested=true    │
     │                │              │              │               │
     │                │              │  3. OPA 策略评估             │
     │                │              │     input: {                 │
     │                │              │       caller: voice-assistant│
     │                │              │       target: adas-controller│
     │                │              │       action: skill_invoke   │
     │                │              │       skill: emergency_brake │
     │                │              │       vehicle_state: moving  │
     │                │              │       user_confirmed: false  │
     │                │              │     }                        │
     │                │              │                              │
     │                │              │     OPA Result: DENY ❌       │
     │                │              │     Reason:                  │
     │                │              │       "infotainment→chassis  │
     │                │              │        ASIL-D skill without  │
     │                │              │        user_confirmation"    │
     │                │              │              │               │
     │                │              │  4. 写审计日志               │
     │                │              │     decision: DENY           │
     │                │              │     reason: no_user_confirm  │
     │                │              │              │               │
     │←── 5. gRPC Error: PERMISSION_DENIED ────────│               │
     │    "emergency_brake requires user_confirmation"             │
     │                │              │              │               │
     │   (现在 Voice Agent 启动用户确认流程...)       │               │
     │                │              │              │               │
     │── 6. 请求用户确认 (屏幕弹窗 + 语音提示)        │               │
     │←── 用户确认: "Yes, emergency brake!"          │               │
     │                │              │              │               │
     │── 7. gRPC Call (retry with confirmation) ────→│               │
     │   metadata: {                                 │               │
     │     "a2a-user-confirmation": "true",          │               │
     │     "a2a-user-confirmation-id": "uci-xxx"     │               │
     │   }                                          │               │
     │                │              │              │               │
     │                │              │  8. OPA 重新评估              │
     │                │              │     user_confirmed: true ✓    │
     │                │              │     Result: ALLOW ✓          │
     │                │              │                              │
     │                │              │  9. ADAS Agent 执行:          │
     │                │              │     emergency_brake(force=0.8)│
     │                │              │──────────────────────────────→│
     │                │              │              │  TEE 签名操作  │
     │                │              │←──────────────────────────────│
     │                │              │                              │
     │←── 10. A2A Task: COMPLETED ──────────────────│               │
     │    artifact: { braking_applied: true }       │               │
```

---

## B.4 Agent Card 中的 mTLS 声明

### MutualTlsSecurityScheme 定义

A2A 规范中 mTLS 的正式定义 (Section 4.5.6):

```json
{
  "securitySchemes": {
    "vehicleMtls": {
      "type": "mutualTls",
      "description": "Vehicle PKI mutual TLS authentication. "
                     "Certificates issued by Vehicle Root CA through KMSS. "
                     "SPIFFE IDs in SAN URI extension."
    }
  },
  "security": [{"vehicleMtls": []}]
}
```

### 车端 Agent Card 完整示例

```json
{
  "name": "Vehicle Agent Gateway",
  "description": "Central A2A Gateway for in-vehicle agent mesh",
  "version": "2.0.0",
  "provider": {
    "name": "OEM Vehicle Platform",
    "url": "https://platform.oem.example.com"
  },
  "supportedInterfaces": [
    {
      "url": "grpcs://gateway.vehicle.local:8443",
      "protocolBinding": "GRPC",
      "protocolVersion": "1.0",
      "tenant": "vehicle-main"
    }
  ],
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true,
    "extendedAgentCard": true
  },
  "securitySchemes": {
    "vehicleMtls": {
      "type": "mutualTls",
      "description": "Client must present a valid x.509 certificate "
                     "issued by Vehicle Root CA. Certificate SAN must "
                     "include a SPIFFE ID."
    }
  },
  "security": [{"vehicleMtls": []}],
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain", "application/json"],
  "skills": [
    {
      "id": "route_to_domain",
      "name": "Route to Domain Agent",
      "description": "Route A2A request to the appropriate domain agent",
      "tags": ["routing", "infrastructure"],
      "inputModes": ["application/json"],
      "outputModes": ["application/json"]
    }
  ]
}
```

---

## B.5 gRPC Binding 下的 IAM 集成

### gRPC Interceptor 链

```
请求进入 gRPC Server → Interceptor Chain → Handler

┌──────────────────────────────────────────────────────────┐
│ gRPC Interceptor Chain                                    │
│                                                           │
│ 1. TLS Interceptor (grpc-go 内置)                         │
│    - 完成 TLS Handshake                                   │
│    - 验证 Client Certificate                             │
│    - 提取 peer.AuthInfo                                  │
│                                                           │
│ 2. IAM Authn Interceptor (自定义)                         │
│    - 从 peer.AuthInfo 提取 x.509 证书                     │
│    - 验证证书链 → Vehicle Root CA                         │
│    - 检查 CRL 吊销状态                                    │
│    - 解析 SPIFFE ID                                       │
│    - 将 caller_identity 注入 context                      │
│                                                           │
│ 3. IAM Authz Interceptor (自定义)                         │
│    - 提取 A2A method name (SendMessage/GetTask...)       │
│    - 对于 SendMessage: 提取 target skill_id               │
│    - 调用 OPA 策略引擎                                    │
│    - 写审计日志                                           │
│    - 拒绝 → 返回 PERMISSION_DENIED                        │
│    - 允许 → 继续执行                                      │
│                                                           │
│ 4. A2A Method Handler                                     │
│    - 执行实际的 A2A 操作                                  │
│    - Task 创建/查询/取消                                  │
│    - 无需再关心认证授权 (已在 Interceptor 中处理)          │
└──────────────────────────────────────────────────────────┘
```

### Go 语言 gRPC Interceptor 实现骨架

```go
// iam/interceptor.go

package iam

import (
    "context"
    "crypto/x509"
    
    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/credentials"
    "google.golang.org/grpc/peer"
    "google.golang.org/grpc/status"
)

// IAMAuthnInterceptor 身份认证拦截器
func IAMAuthnInterceptor(
    caPool *x509.CertPool,
    crlChecker CRLChecker,
) grpc.UnaryServerInterceptor {
    return func(ctx context.Context, req interface{}, 
        info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
        
        // 1. 从 gRPC peer 提取 TLS 信息
        p, ok := peer.FromContext(ctx)
        if !ok {
            return nil, status.Error(codes.Unauthenticated, 
                "no peer information")
        }
        
        tlsInfo, ok := p.AuthInfo.(credentials.TLSInfo)
        if !ok {
            return nil, status.Error(codes.Unauthenticated, 
                "no TLS authentication")
        }
        
        // 2. 验证客户端证书
        if len(tlsInfo.State.PeerCertificates) == 0 {
            return nil, status.Error(codes.Unauthenticated, 
                "no client certificate")
        }
        clientCert := tlsInfo.State.PeerCertificates[0]
        
        // 3. 验证证书链
        opts := x509.VerifyOptions{
            Roots:     caPool,
            KeyUsages: []x509.ExtKeyUsage{x509.ExtKeyUsageClientAuth},
        }
        if _, err := clientCert.Verify(opts); err != nil {
            return nil, status.Errorf(codes.Unauthenticated, 
                "certificate verification failed: %v", err)
        }
        
        // 4. 检查吊销状态
        if crlChecker.IsRevoked(clientCert.SerialNumber) {
            return nil, status.Error(codes.Unauthenticated, 
                "certificate has been revoked")
        }
        
        // 5. 解析 SPIFFE ID
        spiffeID := extractSPIFFEID(clientCert)
        if spiffeID == "" {
            return nil, status.Error(codes.Unauthenticated, 
                "no SPIFFE ID in certificate")
        }
        
        // 6. 解析调用方属性
        caller := CallerIdentity{
            SPIFFEID:    spiffeID,
            Domain:      extractDomain(spiffeID),
            ASILLevel:   extractASILLevel(clientCert),
            TEEAttested: extractTEEAttested(clientCert),
            CertSerial:  clientCert.SerialNumber.String(),
        }
        
        // 7. 注入到 context
        ctx = context.WithValue(ctx, CtxKeyCallerIdentity, caller)
        
        return handler(ctx, req)
    }
}

// IAMAuthzInterceptor 权限鉴权拦截器
func IAMAuthzInterceptor(opa *OPAEngine) grpc.UnaryServerInterceptor {
    return func(ctx context.Context, req interface{},
        info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
        
        caller, ok := ctx.Value(CtxKeyCallerIdentity).(CallerIdentity)
        if !ok {
            return nil, status.Error(codes.Internal, 
                "caller identity not found in context")
        }
        
        // 构造 OPA 输入
        opaInput := map[string]interface{}{
            "caller": caller,
            "method": info.FullMethod,
            "action": extractAction(req),
        }
        
        // OPA 决策
        result, err := opa.Evaluate(ctx, opaInput)
        if err != nil {
            return nil, status.Errorf(codes.Internal, 
                "policy evaluation failed: %v", err)
        }
        
        if !result.Allowed {
            // 写审计日志
            WriteAuditLog(ctx, caller, info.FullMethod, "DENY", result.Reason)
            return nil, status.Errorf(codes.PermissionDenied, 
                "access denied: %s", result.Reason)
        }
        
        // 写审计日志
        WriteAuditLog(ctx, caller, info.FullMethod, "ALLOW", "")
        
        return handler(ctx, req)
    }
}
```

---

## B.6 In-Task Authorization 的车端实现

### A2A 的 TASK_STATE_AUTH_REQUIRED 机制

```
A2A 规范定义了任务中途授权机制:

Agent 执行任务中 → 需要更高权限 → 返回 auth-required → Client 获取授权 → 继续

车端实现映射:
┌─────────────────────────────────────────────────────────────┐
│ A2A 机制                    车端 IAM 实现                    │
├─────────────────────────────────────────────────────────────┤
│ TASK_STATE_AUTH_REQUIRED     ASIL-D Skill 需要用户确认       │
│ TaskStatus.message           弹窗/语音提示请求用户确认        │
│ Client 获取授权              IAM 签发临时提升证书或           │
│                              在请求 metadata 中标记已确认     │
│ Client 继续 Task             携带确认信息的 A2A 请求          │
│ Agent 验证新授权             IAM interceptor 检查确认状态     │
└─────────────────────────────────────────────────────────────┘
```

### 车端 In-Task Auth 实现流程

```
场景: 语音助手 Agent 请求执行紧急制动

Voice Agent                    ADAS Agent                     IAM
(infotainment)                 (chassis)                     
     │                             │                          │
     │ 1. SendMessage:             │                          │
     │    "根据前方障碍物，         │                          │
     │     请执行紧急制动"          │                          │
     │────────────────────────────→│                          │
     │                             │                          │
     │                             │ 2. IAM 检查:             │
     │                             │    - caller domain =     │
     │                             │      infotainment        │
     │                             │    - skill =             │
     │                             │      emergency_brake     │
     │                             │    - ASIL-D critical     │
     │                             │    - user_confirmed =    │
     │                             │      false               │
     │                             │    → 需要用户确认        │
     │                             │                          │
     │ 3. Task Response:           │                          │
     │    task.state =             │                          │
     │      AUTH_REQUIRED          │                          │
     │    task.status.message =    │                          │
     │      "紧急制动需要用户      │                          │
     │       确认。是否执行？"     │                          │
     │←────────────────────────────│                          │
     │                             │                          │
     │ 4. 触发用户确认流程:         │                          │
     │    - 屏幕弹窗 + 语音提示     │                          │
     │    - 用户点击 "确认"         │                          │
     │    - 生成确认令牌 uci-xxx    │                          │
     │                             │                          │
     │ 5. SendMessage (继续Task):   │                          │
     │    taskId: task-123         │                          │
     │    metadata: {              │                          │
     │      "a2a-user-             │                          │
     │       confirmation": "true",│                          │
     │      "a2a-user-             │                          │
     │       confirmation-id":     │                          │
     │       "uci-xxx"             │                          │
     │    }                        │                          │
     │────────────────────────────→│                          │
     │                             │                          │
     │                             │ 6. IAM 重新评估:         │
     │                             │    user_confirmed: true   │
     │                             │    → ALLOW ✓             │
     │                             │                          │
     │                             │ 7. 执行紧急制动          │
     │                             │    记录审计日志          │
     │                             │                          │
     │ 8. Task: COMPLETED          │                          │
     │    artifact: {              │                          │
     │      braking_applied: true, │                          │
     │      deceleration_ms2: 9.8  │                          │
     │    }                        │                          │
     │←────────────────────────────│                          │
```

---

## B.7 完整请求链路追踪

### 端到端 Trace: 从 Voice 到 Brake Controller

```
Trace ID: a2a-trace-LSVN123-20250731-143000-00001

────────────────────────────────────────────────────────────────
Span 1: User Voice Input
  service: voice-assistant
  duration: 50ms
  tags:
    intent: "emergency_stop"
    confidence: 0.95
────────────────────────────────────────────────────────────────
Span 2: A2A SendMessage
  service: voice-assistant (client)
  target: adas-controller
  method: /a2a.A2AService/SendMessage
  tls:
    client_spiffe: "spiffe://vehicle-LSVN123.local/infotainment/agent/voice-assistant"
    server_spiffe: "spiffe://vehicle-LSVN123.local/chassis/agent/adas-controller"
    cipher_suite: TLS_AES_256_GCM_SHA384
────────────────────────────────────────────────────────────────
Span 3: IAM Authentication (gRPC Interceptor)
  service: adas-controller
  duration: 2ms
  result: AUTHENTICATED
  caller:
    spiffe_id: "spiffe://vehicle-LSVN123.local/infotainment/agent/voice-assistant"
    domain: infotainment
    certificate_serial: "0x04B7E3"
    tee_attested: true
────────────────────────────────────────────────────────────────
Span 4: IAM Authorization - Attempt 1 (gRPC Interceptor)
  service: adas-controller
  duration: 1ms
  opa_result: DENY
  reason: "infotainment→chassis ASIL-D skill requires user_confirmation"
  policy_rules_matched:
    - "safety_critical_action_without_user_confirmation"
────────────────────────────────────────────────────────────────
Span 5: User Confirmation Flow
  service: voice-assistant
  duration: 2500ms
  method: "HMI_DISPLAY + VOICE_PROMPT"
  user_response: CONFIRMED
  confirmation_id: "uci-20250731-143002-00001"
────────────────────────────────────────────────────────────────
Span 6: A2A SendMessage (Retry with Confirmation)
  service: voice-assistant (client)
  target: adas-controller
  method: /a2a.A2AService/SendMessage
  metadata:
    a2a-user-confirmation: "true"
    a2a-user-confirmation-id: "uci-20250731-143002-00001"
────────────────────────────────────────────────────────────────
Span 7: IAM Authorization - Attempt 2
  service: adas-controller
  duration: 1ms
  opa_result: ALLOW
  reason: "user_confirmed=true, vehicle_state not moving→allowed"
  policy_rules_matched:
    - "infotainment_to_chassis_with_user_confirm"
────────────────────────────────────────────────────────────────
Span 8: Skill Execution - emergency_brake
  service: adas-controller
  duration: 15ms
  skill: emergency_brake
  parameters: {force: 0.8, user_confirmation_id: "uci-..."}
  result:
    braking_applied: true
    deceleration_ms2: 9.8
    t_brake_command: 143000.050
    t_brake_applied:  143000.065
    latency_ms: 15
  asil_level: ASIL-D
  safety_monitor: PASSED
────────────────────────────────────────────────────────────────
Span 9: Audit Log Write
  service: adas-controller
  duration: 1ms
  audit_entry_id: "audit-20250731-143000-00001"
  hmac_chain_valid: true
────────────────────────────────────────────────────────────────
Span 10: A2A Task Completed
  service: adas-controller
  task_id: "task-brake-20250731-143000-00001"
  task_state: TASK_STATE_COMPLETED
  streaming_events: 2 (working → completed)
────────────────────────────────────────────────────────────────

Total End-to-End Latency: 2584ms
  - IAM overhead: 5ms (0.2%)
  - User confirmation: 2500ms (96.7%)
  - A2A + execution: 79ms (3.1%)
```

---

## 总结：关键架构决策

| 决策 | 选择 | 核心理由 |
|------|------|---------|
| 认证协议 | **mTLS** (非 OAuth2) | 离线可用、零网络依赖、证书即身份、A2A 原生支持 |
| 身份格式 | **SPIFFE ID** | 标准化、层级化、可扩展、跨平台 |
| 信任根 | **TEE (TrustZone/OPTEE)** | 硬件级私钥保护、远程证明、防篡改 |
| 密钥管理 | **KMSS** | 集中化 CA、证书生命周期、安全存储 |
| 传输协议 | **gRPC over TLS 1.3** | 高性能、强类型、原生 mTLS 支持、A2A 标准 binding |
| 权限引擎 | **OPA/Rego (进程内)** | 零延迟、离线决策、声明式策略、可审计 |
| 审计 | **链式 HMAC + TEE 签名** | 防篡改、可追溯、满足法规要求 |
| Agent 发现 | **直接配置 + 本地 Registry** | 车端数量固定、启动快、离线可用 |

这份设计确保了：**A2A 负责 Agent 间通信协议，IAM 负责身份/权限/审计，两者通过 Agent Card 的 `MutualTlsSecurityScheme` + gRPC mTLS 无缝集成，互不侵入。**
