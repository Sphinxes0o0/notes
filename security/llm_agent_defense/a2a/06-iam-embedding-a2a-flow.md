# IAM 三要素嵌入 A2A 流程 — 精确注入点设计

> **核心问题**: AgentID、Agent Auth、Agent Cert 分别在 A2A 生命周期的哪个点介入？如何介入？

---

## 0. 首先明确: IAM 三要素的精确定义

```
┌─────────────────────────────────────────────────────────────────┐
│                    IAM 三要素 ≠ 传统 IAM                          │
│                                                                  │
│  AgentID (身份)    ≠ 用户名/密码                                  │
│    = SPIFFE ID: spiffe://vehicle-VIN.local/domain/agent/name    │
│    = 嵌入在 x.509 证书 SAN 扩展中的 URI                           │
│    = 在 mTLS Handshake 时自动提取，不用传                          │
│                                                                  │
│  Agent Auth (认证+授权) ≠ OAuth2 Token                            │
│    = mTLS 双向证书验证 (认证)                                     │
│    = RE-ABAC 策略决策 (授权)                                      │
│    = 认证在 TLS 层完成，授权在 gRPC Interceptor 完成                │
│                                                                  │
│  Agent Cert (凭证)   ≠ 静态 API Key                               │
│    = x.509 证书 (24h 短有效期, TEE 保护私钥)                       │
│    = 由 KMSS 自动签发、自动续期                                   │
│    = 吊销通过 CRL 分发                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. A2A 完整生命周期 × IAM 注入点全景图

```
时间线 ─────────────────────────────────────────────────────────────→
        启动前          启动时          发现           请求/响应

      ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
      │Phase 0   │  │Phase 1   │  │Phase 2   │  │Phase 3       │
      │凭证获取  │  │服务发布  │  │Agent发现 │  │A2A 请求处理  │
      └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘
           │             │             │               │
           │  IAM 职责:  │  IAM+A2A    │  A2A 职责:    │  IAM+A2A
           │  Agent Cert │  协作:      │  声明需求    │  协作:
           │  AgentID    │  Agent Card │              │  Agent Auth
           │             │  发布       │              │  (鉴权)
           ▼             ▼             ▼               ▼

    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │KMSS 签发证书 │ │Agent Card 中 │ │Client GET    │ │mTLS Handshake│
    │TEE 保护私钥  │ │声明 mTLS     │ │Agent Card    │ │双向证书验证  │
    │SPIFFE ID 绑定│ │声明 Skills   │ │解析安全需求  │ │提取 AgentID  │
    │证书 = 身份   │ │              │ │              │ │CRL 吊销检查  │
    └──────────────┘ └──────────────┘ └──────────────┘ └──────┬───────┘
                                                              │
                                                    ┌─────────▼─────────┐
                                                    │RE-ABAC 鉴权       │
                                                    │查决策表           │
                                                    │ALLOW/DENY/CONFIRM │
                                                    └─────────┬─────────┘
                                                              │
                                              ┌───────────────┼───────────────┐
                                              ▼               ▼               ▼
                                         ┌────────┐    ┌──────────┐    ┌──────────┐
                                         │ ALLOW  │    │DENY+可恢复│   │DENY+不可  │
                                         │→A2A    │    │→AUTH_    │    │恢复→     │
                                         │Handler │    │ REQUIRED │    │PERMISSION│
                                         └────────┘    └──────────┘    │_DENIED   │
                                                                       └──────────┘
```

---

## 2. Phase 0: 启动前 — Agent Cert 的获取 (纯 IAM)

```
// 这是 A2A 协议流程开始之前发生的事情，但决定了 A2A 的根基。

时序:
                          KMSS
  Agent (Normal World)     (TEE Secure World)
      │                         │
      │  ① Agent 启动            │
      │  ② TEE 度量 Agent 代码   │
      │  ③ 生成 Attestation     │
      │     Report               │
      │                         │
      │  ④ CertIssueRequest ────→│
      │     {                    │
      │       csr: "...",        │
      │       attestation: {...} │  ⑤ 验证:
      │       identity: {        │     - Attestation 签名
      │         domain: "adas",  │     - 代码度量值
      │         name: "controller"│    - PCR 值
      │         asil: "ASIL-D"   │  
      │       }                  │  ⑥ 签发证书:
      │     }                    │     SAN: spiffe://...
      │                          │     扩展: asil_level
      │                          │     扩展: tee_attested
      │  ⑦ CertIssueResponse ←──│
      │     {                    │
      │       cert_chain: [...], │  ← Agent Certificate
      │       crl: [...],        │  ← 当前吊销列表
      │       expires: now+24h   │
      │     }                    │
      │                         │
      │  ⑧ 存储:                 │
      │     - 证书 → 内存        │
      │     - 私钥 → TEE KeyStore│
      │     - CRL → 内存缓存     │
      │     - 续期定时器: T-2h   │

IAM 在此阶段完成的:
  ✅ Agent Cert:  证书已签发, 24h 有效, TEE 保护私钥
  ✅ AgentID:     SPIFFE ID 已绑定到证书 SAN
  ✅ 身份信任链:  Vehicle Instance CA → Platform CA → OEM Root CA
```

### 关键设计: Agent Card 此时还不存在

```
// 注意: Phase 0 只获得身份，Agent Card 是在 Phase 1 用这个身份生成的。

Agent Card 中 securitySchemes 的 mutualTls 不是空声明——
// 它背后是 Phase 0 中 KMSS 已经签发、TEE 中已有私钥的真实证书。
```

---

## 3. Phase 1: 服务发布 — Agent Card 生成 (IAM 声明 + A2A 承载)

### 3.1 Agent Card 中的 IAM 信息

> **完整的 Agent Card 定义见 [a2a/02 §B.4](/security/llm_agent_defense/a2a/02-vehicle-iam-architecture)。** 此处仅展示 IAM 相关的关键字段。

```json
{
  "name": "ADAS Controller",
  
  "// ─── IAM 注入点 1: securitySchemes ───": "",
  "securitySchemes": {
    "vehicleMtls": {
      "type": "mutualTls",
      "description": "证书由 Vehicle Instance CA (KMSS/TEE) 签发"
    }
  },
  "security": [{"vehicleMtls": []}],
  
  "// ─── IAM 注入点 2: Skills 安全约束 ───": "",
  "skills": [{
    "id": "emergency_brake",
    "tags": ["ASIL-D", "user-confirmation-required"],
    "security": [{"vehicleMtls": []}]
  }],
  
  "// ─── IAM 注入点 3: Agent Card 签名 ───": "",
  "signature": {
    "protected": "eyJhbGciOiJFUzI1NiIs...",
    "signature": "Base64-JWS-Signature",
    "certificateChain": ["...Agent Cert...", "...Vehicle Instance CA..."]
  }
}
```

### 3.2 Agent Card 签名: IAM 如何防止篡改

```
为什么需要签名 Agent Card?

场景: 恶意 Agent 发布虚假 Agent Card
  → 声称自己是 ADAS Controller，Skill 包含 "emergency_brake"
  → 但实际没有合法的 SPIFFE ID，或者 ASIL 等级是伪造的

防御: Agent Card 必须用 Agent 证书的私钥签名 (JWS)

签名流程:
  1. Agent Card JSON → JCS Canonicalization (RFC 8785)
  2. 用 Agent 私钥 (在 TEE 中) 做 ECDSA P-256 签名
  3. 签名 + 证书链嵌入 Agent Card 的 signature 字段

验证流程 (Client 端):
  1. 提取 Agent Card 的 signature.certificateChain
  2. 验证证书链 → Vehicle Root CA
  3. 提取证书中的 SPIFFE ID
  4. 用证书公钥验证 JWS 签名
  5. 确认 Agent Card 内容未被篡改
  6. 确认 Agent Card 中声明的 name 与证书 SAN 中的 SPIFFE ID 匹配
```

### 3.3 IAM → A2A 的映射关系

```
IAM 概念              A2A 对应字段              关系
──────────────────────────────────────────────────────────
AgentID (SPIFFE)  →  Agent Card signer cert     A2A 不直接承载 AgentID,
                     的 SAN URI                  而是通过签名证书隐式绑定

Agent Cert         →  securitySchemes.mutualTls  声明需求 + 签名证明
  
权限需求           →  skills[].security          IAM 策略与此对齐;
                                                  跨域 + ASIL-D 需要
                                                  user_confirmation

Agent Card 完整性  →  signature (JWS)            IAM 用 Agent 私钥签名,
                                                  Client 用 PKI 验证
```

---

## 4. Phase 2: Agent 发现 — IAM 如何影响发现

```
Client Agent 发现 Remote Agent:

  Client                          Remote Agent (A2A Server)
    │                                    │
    │  GET /.well-known/agent-card.json   │
    │────────────────────────────────────→│
    │                                    │
    │←── AgentCard (含 securitySchemes) ──│
    │                                    │
    │ Client 解析 Agent Card:             │
    │                                    │
    │ ① 读 securitySchemes:              │
    │   "type": "mutualTls"              │
    │   → 需要 mTLS                      │
    │                                    │
    │ ② 读 security:                     │
    │   [{"vehicleMtls": []}]            │
    │   → 所有请求都要 mTLS               │
    │                                    │
    │ ③ 读 skills[].security:            │
    │   emergency_brake 需要 vehicleMtls  │
    │                                    │
    │ ④ 读 signature (可选):             │
    │   验证 Agent Card 签名             │
    │   → 确认 Remote Agent 身份真实性    │
    │                                    │
    │ ⑤ 决策:                            │
    │   "我有 KMSS 签发的证书 → 可以连接" │
    │   "我需要 diag:read scope → 不,      │
    │    车端不用 OAuth scope, 用证书"   │

关键: Agent Card 的 securitySchemes 就是 IAM 向 A2A 客户端
//    宣告 "你需要什么凭证才能和我说话" 的唯一渠道。
```

---

## 5. Phase 3: A2A 请求处理 — IAM 的运行时注入

### 5.1 完整调用链路 (IAM 介入点标注)

```
Client (Voice Agent)                    Server (ADAS Agent / gRPC)
infotainment domain                     chassis domain, ASIL-D
    │                                        │
    │                                        │
    │  ╔══════════════════════════════════╗  │
    │  ║ IAM 注入点 A: mTLS Handshake     ║  │
    │  ╚══════════════════════════════════╝  │
    │                                        │
    │── gRPC Dial ──────────────────────────→│
    │  ClientCert: voice-agent.crt            │
    │  ServerCert: adas-agent.crt             │
    │                                        │
    │  TLS 1.3 Handshake:                    │
    │  • ECDSA P-256 双向验证                │
    │  • 双方验证证书链 → Vehicle Root CA    │
    │  • 双方提取对端 SPIFFE ID              │
    │                                        │
    │  ✅ AgentID 已获取                      │
    │  ✅ Agent Cert 已验证                    │
    │  ✅ 传输通道已加密                      │
    │                                        │
    │  ╔══════════════════════════════════╗  │
    │  ║ IAM 注入点 B: gRPC Authn Interceptor ║ │
    │  ╚══════════════════════════════════╝  │
    │                                        │
    │── SendMessage(emergency_brake) ────────→│
    │                                        │
    │                          ┌─────────────▼──────────────┐
    │                          │ IAM Authn Interceptor       │
    │                          │                             │
    │                          │ ① 从 TLS session 提取:      │
    │                          │   peer_cert = TLS state     │
    │                          │   spiffe_id = cert SAN URI  │
    │                          │                             │
    │                          │ ② CRL 检查:                  │
    │                          │   cert_serial in crl_cache? │
    │                          │   → NO → 通过               │
    │                          │                             │
    │                          │ ③ 构造 CallerIdentity:      │
    │                          │   caller_id = "voice-asst"  │
    │                          │   domain = "infotainment"   │
    │                          │   asil = "QM"               │
    │                          │   tee_attested = true       │
    │                          │                             │
    │                          │ ④ 写入 gRPC context:        │
    │                          │   ctx.iam_caller = identity │
    │                          └─────────────┬──────────────┘
    │                                        │
    │  ╔══════════════════════════════════╗  │
    │  ║ IAM 注入点 C: gRPC Authz Interceptor ║ │
    │  ╚══════════════════════════════════╝  │
    │                                        │
    │                          ┌─────────────▼──────────────┐
    │                          │ IAM Authz Interceptor       │
    │                          │                             │
    │                          │ ① 构造 RE-ABAC input:       │
    │                          │   caller_id = "voice-asst" │
    │                          │   skill_id = "emergency_brk"│
    │                          │   action = INVOKE           │
    │                          │   vehicle_state = MOVING    │
    │                          │   user_confirmed = false    │
    │                          │                             │
    │                          │ ② RE-ABAC 查表 (9KB table):│
    │                          │   binary_search(key)        │
    │                          │   → DENY_NEED_USER_CONFIRM │
    │                          │                             │
    │                          │ ③ ✍ 写审计日志:            │
    │                          │   decision=DENY             │
    │                          │   reason=need_user_confirm  │
    │                          │                             │
    │                          │ ④ 决策可恢复? YES           │
    │                          │   → 不直接拒绝              │
    │                          │   → 将决策写入 gRPC metadata│
    │                          │   ctx.iam_decision = {...}  │
    │                          └─────────────┬──────────────┘
    │                                        │
    │                          ┌─────────────▼──────────────┐
    │                          │ A2A Handler (SendMessage)   │
    │                          │                             │
    │                          │ ① 读取 iam_decision:        │
    │                          │   decision = "NEED_CONFIRM" │
    │                          │                             │
    │                          │ ② 创建 Task:                │
    │                          │   task.state = AUTH_REQUIRED│
    │                          │   task.status.message =     │
    │                          │     "紧急制动需要用户确认"    │
    │                          │   task.status.metadata = {  │
    │                          │     "iam.decision": "NEED_  │
    │                          │       USER_CONFIRM",        │
    │                          │     "iam.confirmation": {   │
    │                          │       "type": "hmi_dialog", │
    │                          │       "title": "紧急制动",   │
    │                          │       "timeout_ms": 5000    │
    │                          │     }                       │
    │                          │   }                         │
    │                          └─────────────┬──────────────┘
    │                                        │
    │←── Task { state: AUTH_REQUIRED } ──────│
    │                                        │
    │  ╔══════════════════════════════════╗  │
    │  ║ 用户确认后重试 (Phase 3 重复)     ║  │
    │  ╚══════════════════════════════════╝  │
    │                                        │
    │── SendMessage (重试 + 确认信息) ───────→│
    │  metadata: {                           │
    │    "iam-user-confirmation": "true"     │
    │    "iam-confirmation-id": "uci-xxx"    │
    │  }                                     │
    │                                        │
    │                          IAM Authz:     │
    │                          user_confirmed=true → ALLOW ✓│
    │                                        │
    │                          A2A Handler:   │
    │                          task.state=COMPLETED          │
    │                                        │
    │←── Task { state: COMPLETED } ──────────│
```

### 5.2 IAM 三要素在 A2A 请求中的位置总结

```
A2A 请求的三个层面 vs IAM 三要素:

┌─────────────────────────────────────────────────────────────────┐
│ A2A 层            传输层(TLS)       gRPC Metadata    A2A Payload│
├─────────────────────────────────────────────────────────────────┤
│                     │                │                │          │
│  AgentID ◄──────────│ 证书 SAN URI   │                │          │
│  (身份)             │ (自动提取)     │                │          │
│                     │                │                │          │
│  Agent Auth         │ 证书链验证     │ RE-ABAC 决策   │ Task     │
│  (认证+授权)        │ + CRL 检查     │ 结果传递        │ State:   │
│                     │ ← 认证         │ ← 授权决策     │ AUTH_    │
│                     │                │   传递          │ REQUIRED │
│                     │                │                │          │
│  Agent Cert         │ 私钥在 TEE     │                │ Agent    │
│  (凭证)             │ 证书在内存     │                │ Card     │
│                     │ 自动续期       │                │ 签名     │
│                     │                │                │ (JWS)    │
└─────────────────────────────────────────────────────────────────┘

关键洞察:

1. AgentID 不经过 A2A Payload
   → 它从 TLS 层自动提取，对 A2A 协议透明
   → A2A 不需要知道 "你是谁"，IAM interceptor 提取后注入 context

2. Agent Auth 分为两步:
   → 认证 (你是谁)     — TLS 层完成，A2A 无感知
   → 授权 (你能不能)   — gRPC Interceptor 完成，结果通过
                          metadata 或 TaskState 传递给 A2A Handler

3. Agent Cert 对 A2A 的唯一可见点:
   → Agent Card 的 securitySchemes.mutualTls (声明)
   → Agent Card 的 signature (自证)
   → 其余 (签发、续期、吊销) 完全在 A2A 协议外
```

---

## 6. 关键接口定义: IAM ↔ A2A 的契约

### 6.1 gRPC Context 中的 IAM 字段

```cpp
// iam_types.h — IAM 与 A2A 的共享类型

// gRPC metadata keys (IAM → A2A handler 的传递通道)
constexpr const char* IAM_CALLER_SPIFFE_ID   = "iam-caller-spiffe-id";
constexpr const char* IAM_CALLER_DOMAIN       = "iam-caller-domain";
constexpr const char* IAM_CALLER_ASIL_LEVEL   = "iam-caller-asil-level";
constexpr const char* IAM_CALLER_TEE_ATTESTED = "iam-caller-tee-attested";
constexpr const char* IAM_AUTHZ_DECISION       = "iam-authz-decision";
constexpr const char* IAM_AUTHZ_REASON         = "iam-authz-reason";
constexpr const char* IAM_USER_CONFIRMATION    = "iam-user-confirmation";
constexpr const char* IAM_CONFIRMATION_ID      = "iam-confirmation-id";

// IAM 决策传递给 A2A Handler 的结构
struct IamDecision {
    enum Outcome {
        ALLOW = 0,
        DENY_PERMANENT = 1,    // → gRPC PERMISSION_DENIED
        DENY_NEED_USER_CONFIRM = 2, // → A2A TASK_STATE_AUTH_REQUIRED
        DENY_VEHICLE_STATE = 3,     // → A2A TASK_STATE_AUTH_REQUIRED
        DENY_RATE_LIMIT = 4,        // → gRPC RESOURCE_EXHAUSTED
    };
    
    Outcome outcome;
    const char* reason;
    bool is_recoverable;    // true → A2A 可以要求 Client 恢复
    
    // 如果 is_recoverable, A2A Handler 使用这些信息构造 AUTH_REQUIRED
    struct RecoveryHint {
        const char* auth_type;          // "user_confirmation"
        const char* prompt_title;       // "紧急制动"
        const char* prompt_message;     // "前方检测到障碍物，是否执行紧急制动？"
        uint32_t timeout_ms;            // 5000
    } recovery_hint;
};
```

### 6.2 A2A Handler 如何使用 IAM 决策

```cpp
// a2a_handler.cpp — A2A Handler 中处理 IAM 决策的伪代码

a2a::Task handle_send_message(const a2a::SendMessageRequest& req,
                               grpc::ServerContext* ctx) {
    
    // ① 从 gRPC context 读取 IAM 决策 (由 interceptor 写入)
    auto decision = extract_iam_decision(ctx);
    
    switch (decision.outcome) {
    
    case IamDecision::ALLOW:
        // ✅ 正常处理
        return execute_skill(req);
    
    case IamDecision::DENY_PERMANENT:
        // ❌ 不创建 Task, 直接返回错误
        //    Client 无恢复可能
        ctx->SetStatus(grpc::Status(
            grpc::PERMISSION_DENIED,
            decision.reason));
        return {};
    
    case IamDecision::DENY_NEED_USER_CONFIRM:
    case IamDecision::DENY_VEHICLE_STATE:
        // ⚠ 创建 Task, 状态设为 AUTH_REQUIRED
        //    A2A 规范的 "interrupted state"
        a2a::Task task;
        task.id = generate_task_id();
        task.context_id = req.message().context_id();
        task.status.state = a2a::TASK_STATE_AUTH_REQUIRED;
        task.status.message = a2a::Message{
            .role = a2a::ROLE_AGENT,
            .parts = {{
                .text = decision.recovery_hint.prompt_message
            }}
        };
        
        // 将 IAM 恢复提示嵌入 Task metadata
        task.metadata = {
            {"iam.decision", decision.outcome},
            {"iam.recovery.type", decision.recovery_hint.auth_type},
            {"iam.recovery.prompt_title", decision.recovery_hint.prompt_title},
            {"iam.recovery.timeout_ms", 
             std::to_string(decision.recovery_hint.timeout_ms)},
        };
        
        return task;
    
    case IamDecision::DENY_RATE_LIMIT:
        ctx->SetStatus(grpc::Status(
            grpc::RESOURCE_EXHAUSTED,
            decision.reason));
        return {};
    }
}
```

---

## 7. 异常路径: IAM 介入的错误场景

### 7.1 证书过期 (Phase 3 中)

```
Client 证书在请求中途过期:

  Client → gRPC Dial → Server
    TLS Handshake:
      Server 验证 Client 证书:
        notAfter < now → 证书已过期
        → TLS Handshake 失败
        → gRPC 返回 UNAVAILABLE (连接层)
        → A2A 协议层根本没有介入机会

  Client 反应:
    → 立即触发 KMSS 续期 (同步, 等待新证书)
    → 用新证书重新 gRPC Dial
    → 重试 A2A 请求
```

### 7.2 证书吊销 (CRL 检查失败)

```
  TLS Handshake 成功 → gRPC Authn Interceptor:

    IAM Authn Interceptor:
      ① 提取 Client Cert Serial: 0x04A3F2
      ② 查 CRL 缓存:
         0x04A3F2 in revoked_list → YES
         reason = keyCompromise
      ③ → 返回 gRPC UNAUTHENTICATED
      
    A2A 没有任何介入 → 连接在 IAM 层被拒绝
```

### 7.3 TEE Attestation 失败

```
  Agent 启动时:

    KMSS 验证 Attestation Report:
      TA measurement ≠ 白名单中的预期值
      → Agent 代码被篡改!
      → KMSS 拒绝签发证书
      → Agent 无法启动 gRPC Server (无有效证书)
      → 其他 Agent 也无法连接它
      
  全局影响: 该 Agent 从整个 A2A 网络中隔离
```

---

## 8. 总结: IAM 三要素的 A2A 注入矩阵

```
           Phase 0     Phase 1       Phase 2       Phase 3
           启动前      服务发布       Agent发现      A2A请求处理
           ───────     ───────       ────────      ──────────
AgentID    KMSS 签发   Agent Card    通过 mTLS      gRPC Context
(身份)     证书中嵌入   签名隐式绑定   握手自动提取   caller ID
           SPIFFE ID                                字段

Agent Auth 无          securitySchemes Client 检查   RE-ABAC 查表
(认证+授权)            声明 mTLS      安全需求       授权决策
                                          ↓
                                    A2A Handler 读
                                    IAM 决策 → Task
                                    State: AUTH_REQUIRED

Agent Cert KMSS 签发   Agent Card    Client 从      私钥在 TEE 签名
(凭证)     TEE 保护    签名 (JWS)    Agent Card      证书自动续期
           24h 有效期   自证身份      提取证书链      吊销由 IAM 检查
           自动续期                  验证 PKI         A2A 不感知

A2A 协议   无介入       Agent Card    标准发现流程    SendMessage
           (尚未启动)   承载 IAM 声明  IAM 需求解析   GetTask
                                                 + IAM 决策驱动
                                                   TaskState
```

**一句话总结**: IAM 的身份和凭证工作在 A2A 协议之前完成 (Phase 0-1)，认证在 TLS 层透明完成 (Phase 3 的传输层)，授权在 gRPC Interceptor 完成并通过 TaskState 影响 A2A 行为。**IAM 对 A2A 的唯一可见接口就是 Agent Card 的 securitySchemes + skills[].security + Task 的 AUTH_REQUIRED 状态。**
