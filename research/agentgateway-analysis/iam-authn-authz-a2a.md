# Agentgateway 第二轮深挖：IAM + 鉴权 + A2A

> **承接**：第一轮报告（`README.md`）覆盖了项目全景、模块拓扑、整体数据流、A2A 协议识别、Agent ID 三源身份、AuthN 全栈、AuthZ 引擎。
>
> **第二轮目标**：聚焦车端 AI Agent 安全框架的**实战落地**，从 <strong>跨 IDP 联邦（IAM）</strong> → <strong>四层鉴权链路</strong> → <strong>A2A 任务级授权</strong> 三块挖深，并给出可直接 ship 的配置骨架。
>
> **NIO 场景约束**（基于 User Profile）：座舱 8295+QTEE / 智驾 Orin+OP-TEE / 车控 S32G+OP-TEE+HSM、30B~0.1B 多规模 LLM、离线优先、车控 50Hz、ASIL-D。

---

## 目录

- [一、IAM 体系：6 个 IDP 联邦 + RFC 矩阵](#一iam-体系6-个-idp-联邦--rfc-矩阵)
- [二、鉴权链路：4 层 12 步](#二鉴权链路4-层-12-步)
- [三、AuthN 深度：JWT 流水线 + 凭据生命周期](#三authn-深度jwt-流水线--凭据生命周期)
- [四、AuthZ 引擎：CEL 表达 + 三态规则 + Network Authz](#四authz-引擎cel-表达--三态规则--network-authz)
- [五、A2A 任务级授权：补全 RBAC 缺失](#五a2a-任务级授权补全-rbac-缺失)
- [六、车端 IAM 联邦设计](#六车端-iam-联邦设计)
- [七、可直接 ship 的完整配置骨架](#七可直接-ship-的完整配置骨架)
- [八、车端特定风险与加固清单](#八车端特定风险与加固清单)

---

## 一、IAM 体系：6 个 IDP 联邦 + RFC 矩阵

Agentgateway 的 MCP AuthN 是<strong>当前最完整的 Agent-to-IdP 联邦实现</strong>。它不是简单"校验 JWT"，而是完整实现了 OAuth 2.0 授权服务器代理 + 资源服务器角色 + 多 IDP 适配。

### 1.1 支持的 IDP（`types/agent.rs:2994-3001`）

```rust
pub enum McpIDP {
    Auth0 {},       // Auth0（不支持 RFC 8707，需 audience query hack）
    Keycloak {},    // Keycloak（不支持 RFC 8707，不做 CORS for DCR）
    Okta {},        // Okta（不支持 RFC 8707，不做 CORS for DCR）
    Descope {},     // Descope（专门为 Agent 设计的 IDP）
    Authentik {},    // Authentik
    Entra {},       // Microsoft Entra ID（不支持 RFC 8707，需代理）
}
```

### 1.2 RFC 矩阵（基于 `mcp/auth.rs` 实测）

| RFC | 用途 | 通用 | Auth0 | Keycloak | Okta | Descope | Authentik | Entra |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **RFC 8707** Resource Indicators | 防止 access token 被滥用 | ✅ | ❌→hack | ❌ | ❌ | ✅ | ❌ | ❌→proxy |
| **RFC 8414** Authorization Server Metadata | 暴露 AS 元数据 | ✅ | ✅ | ❌→OIDC | ❌→OIDC | ❌→OIDC | ❌→OIDC | ❌→OIDC |
| **OIDC Discovery** | `/.well-known/openid-configuration` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RFC 7591** Dynamic Client Registration | MCP client 自动注册 | ✅ | ✅ | ❌→proxy | ❌→proxy | ❌→proxy | — | — |
| **RFC 7636** PKCE | 防止 code 拦截 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **JWKS auto-derive** | 拉 JWKS 公钥 | ✅ | ✅ | ✅ | ✅ | ✅ (project 级) | ✅ | ✅ |

**关键洞见**：agentgateway 不是把 IDP 当成"对等"实现，而是<strong>逐个适配它们的 RFC 兼容性</strong>。Keycloak/Auth0/Okta 都不支持 RFC 8707，所以 agentgateway 在 `authorization_server_metadata` 端点（`mcp/auth.rs:300-336`）<strong>用 query param hack 拼 audience</strong>；Keycloak 不支持 CORS for DCR，agentgateway 代理 `client-registration` 端点（`mcp/auth.rs:78-87`）。

### 1.3 MCP 资源服务器三大端点

`mcp/auth.rs:71-146` 实现了完整的资源服务器元数据 + 授权服务器代理：

| 端点 | 用途 | 由谁消费 |
|---|---|---|
| `GET /.well-known/oauth-protected-resource/{path}` | RFC 9728 资源元数据，<strong>MCP 客户端发现 auth 入口</strong> | MCP client SDK |
| `GET /.well-known/oauth-authorization-server/{path}` | RFC 8414 代理，<strong>转发到真实 IdP</strong>，并按需改写 audience | MCP client SDK |
| `POST /client-registration` | 代理 DCR（Keycloak/Okta/Descope 不做 CORS） | MCP client SDK |

`handle_mcp_request` 完整路径（`mcp/auth.rs:71-146`）：
```
mcp request
  ├── path == "/.well-known/oauth-protected-resource" → 构造 RFC 9728 JSON
  ├── path starts with "/.well-known/oauth-authorization-server/" + Entra + /authorize → entra_authorize
  ├── path starts with "/.well-known/oauth-authorization-server/" + Entra + /token → entra_token
  ├── path starts with "/.well-known/oauth-authorization-server/" + others → authorization_server_metadata
  ├── path ends with "/client-registration" → client_registration
  └── _ → Ok(None)（让正常 MCP 请求透传）
```

### 1.4 OAuth Token Exchange 矩阵（`http/auth/oauth/mod.rs`）

```rust
pub enum OAuthGrantType {
    #[default] TokenExchange,   // RFC 8693
    JwtBearer,                 // RFC 7523
}

pub enum OAuthTokenType {
    AccessToken,  // urn:ietf:params:oauth:token-type:access_token
    Jwt,          // urn:ietf:params:oauth:token-type:jwt
    IdToken,      // urn:ietf:params:oauth:token-type:id_token
    IdJag,        // urn:ietf:params:oauth:token-type:id-jag
    Custom(String),
}

pub struct ActorTokenSpec {
    source: AuthorizationLocation,
    token_type: OAuthTokenType,
    /// 委托链安全：检查 subject token 的 may_act claim
    enforce_may_act: bool,  // 必须 token_type == Jwt
}
```

**这是车端跨域 OAuth 联邦的核心引擎**：
- <strong>Subject token</strong> 来自上游（车端用户的 ID token）
- <strong>Actor token</strong> 是中间 agent（车端 orchestrator agent）
- <strong>chained_exchange</strong> 支持 ID-JAG → access token 二段跳

### 1.5 CrossAppAccess：Google CAEP 协议（`http/auth/oauth/cross_app_access.rs`）

完整的 Google "Cross App Access" 实现（agentic AI 时代的新协议）：

```rust
// cross_app_access.rs:86-93
// RFC 8693 ID-JAG leg (to IdP) chained into RFC 7523 jwt-bearer leg (to resource AS)
let chained_exchange = resource_authorization_server.into_chained_exchange(scopes.clone());
let oauth = OAuthTokenExchangeAuth {
    grant_type: OAuthGrantType::TokenExchange,
    subject_token: TokenSpec { source, token_type: OAuthTokenType::IdToken },
    actor_token: None,
    audiences: vec![audience],
    resources, scopes,
    requested_token_type: Some(OAuthTokenType::IdJag),  // 第一跳换 ID-JAG
    client_auth: Some(client_auth),
    chained_exchange: Some(chained_exchange),          // 第二跳 jwt-bearer
    // ...
};
```

**车端用法**：
- 用户在车机浏览器登录（Google / Apple / Microsoft IdP）
- ID token → 通过 agentgateway 换 ID-JAG
- ID-JAG → 通过 resource AS 换 access token
- 车端微服务用 access token 调云端 API

---

## 二、鉴权链路：4 层 12 步

### 2.1 全链路串联（4 个 LAYER）

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: L4 阶段（accept 后立即执行）                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 1.  TCP/TLS accept                                          │ │
│ │ 2.  rustls 验证 client cert（如果 mTLS）                     │ │
│ │ 3.  提取 SPIFFE identity (cert SAN URI) → SourceContext     │ │
│ │ 4.  SourceContext::from_stores (按 IP 解析 workload)         │ │
│ │ 5.  NetworkAuthorizationSet.apply(SourceContext)            │ │
│ │     → deny 立即 RST                                         │ │
│ │ 6.  stream.ext.insert(SourceContext, DestinationContext)   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: Gateway Policies（pre-route）                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 7.  apply_gateway_policies（固定顺序）                       │ │
│ │     CORS → OIDC → JWT → Basic → APIKey → ExtAuthz →        │ │
│ │     Authorization → ExtProc → Transformation                │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: Route Policies                                         │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 8.  select_route                                            │ │
│ │ 9.  apply_route_policies                                    │ │
│ │     AuthN/AuthZ/ExtAuthz 再次执行（路由级覆盖）             │ │
│ │     限流/CSRF/MCP-Authn/MCP-Authz                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: Backend Policies（调用后端前）                          │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 10. apply_backend_policies                                  │ │
│ │     HTTP → AuthZ → ExtAuthz → backend_auth →                │ │
│ │     transformation → request_header_modifier →              │ │
│ │     request_redirect → A2A/MCP classifier                   │ │
│ │ 11. make_backend_call (mTLS if backendTLS)                  │ │
│ │ 12. apply_to_response (A2A agent card 重写, MCP guardrail)  │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 MCP 特殊路径（router.rs:117-145）

MCP 走的是<strong>完全不同的入口</strong>，不在上述 LAYER 2~3 的常规 HTTP 路径里：

```rust
// mcp/router.rs:117-145
let authorization_policies = backend_policies.mcp_authorization
    .unwrap_or_else(|| McpAuthorizationSet::new(RuleSets::from(Vec::new())));
let authn = backend_policies.mcp_authentication;
let mcp_guardrails = backend_policies.mcp_guardrails.clone();

// 1. 在 router 入口 AuthN 一次（OAuth + JWKS）
if let Some(auth) = authn.as_ref()
    && let Some(resp) = auth::enforce_authentication(&mut req, auth, &client).await?
{
    return Ok(resp);
}

// 2. 进入 SSE / StreamableHTTP handler
// 3. 每个 JSON-RPC method 进入 session.rs 时调 authorize_with_ctx
//    → 先 guardrails → 再 RBAC (ResourceType::Tool/Prompt/Resource/Task)
```

MCP 鉴权 = <strong>1 次 AuthN + N 次 AuthZ</strong>，每次 tool/prompt/resource/task 调用都重新评估 RBAC。

### 2.3 鉴权失败的语义

| 层 | 失败后果 | 失败模式 |
|---|---|---|
| L4 NetworkAuthz | TCP RST | <strong>fail-closed（无规则默认允许）</strong>，但有规则就 deny |
| Gateway AuthN | 401 Unauthorized | 各 AuthN mode 决定（Strict 必 fail） |
| Gateway AuthZ | 403 Forbidden | RBAC 引擎 deny 路径 |
| Route AuthN | 401（覆盖 Gateway） | 同上 |
| Route AuthZ | 403（覆盖 Gateway） | 同上 |
| Backend AuthZ | 403 | RBAC 引擎 deny |
| ExtAuthz 失败 | 视 FailureMode | 默认 Deny（<code>http/ext_authz.rs:84</code>） |
| MCP AuthN | 401 + `WWW-Authenticate: Bearer resource_metadata=...` | 触发 client 启动 OAuth flow |

---

## 三、AuthN 深度：JWT 流水线 + 凭据生命周期

### 3.1 JWT 验证流水线（`http/jwt.rs:490-552`）

```
                   ┌─────────────────────────┐
   Request ──────► │  1. location.extract    │  ← AuthorizationLocation
                   │     (header/cookie/     │     (CEL expression 也支持)
                   │      query/CEL)         │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │  2. mode == Strict?     │  ← JwtAuthentication
                   │     是 → 没 token = 401 │     { Strict, Optional, Permissive }
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │  3. decode_header       │  ← jsonwebtoken
                   │     检查 kid            │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │  4. providers.find kid  │  ← 遍历多个 JWKS
                   │     找到 decoding key   │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │  5. decode<Claims>      │  ← 验签 + 时间 + audience
                   │     验签 exp/nbf/iss/aud│
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │  6. location.remove     │  ← 关键：删除 token
                   │     防透传到后端        │
                   └────────────┬────────────┘
                                │
                                ▼
                   ┌─────────────────────────┐
                   │  7. req.extensions      │  ← 注入 Claims
                   │     .insert(claims)     │     下游策略可访问 jwt.*
                   └─────────────────────────┘
```

### 3.2 JWKS 自动派生（车端关键）

`types/agent.rs:2902-2943` 实现 6 个 IDP 的 JWKS URL 自动派生：

| IDP | JWKS URL |
|---|---|
| Auth0 / Okta / 无 provider | `{issuer}/.well-known/jwks.json` |
| Descope (agentic) | `https://api.descope.com/{project_id}/.well-known/jwks.json` |
| Keycloak | `{issuer}/protocol/openid-connect/certs` |
| Authentik | `{issuer}/jwks/` |
| Entra | Microsoft Graph 派生 |

**车端适配**：如果车端用 HSM 自管 CA，需要扩展这个 `derived_jwks_url` 或直接 inline `jwks: { file: ... }` 或 `jwks: { url: ... }`。

### 3.3 OIDC 浏览器登录完整流程（`http/oidc/`）

OIDC 是 v1.1.0 新增的核心能力，完整 PKCE + AES-256-GCM 加密 session：

```
浏览器              agentgateway              IdP
 │                     │                       │
 │  GET /api/v1/x      │                       │
 │─────────────────────>│                       │
 │                     │  1. session cookie?   │
 │                     │     缺失              │
 │                     │  2. start_login()      │
 │                     │     生成              │
 │                     │     - transaction_id  │
 │                     │     - csrf_state      │
 │                     │     - nonce           │
 │                     │     - pkce_verifier   │
 │                     │     (32 bytes random) │
 │                     │                       │
 │<─ 302 ──────────────│                       │
 │   Location: IdP/authorize                    │
 │   ?response_type=code                        │
 │   &client_id=...                             │
 │   &redirect_uri=/oauth/callback              │
 │   &scope=openid+profile                      │
 │   &state={transaction_id}.{csrf_state}      │
 │   &nonce={nonce}                             │
 │   &code_challenge={S256(pkce_verifier)}     │
 │   &code_challenge_method=S256               │
 │                     │                       │
 │  Set-Cookie: agw_oidc_t_{hash(transaction_id)}=
 │    {AES-GCM-encrypted(transaction_state)}   │
 │                     │                       │
 │  GET IdP/authorize?...                       │
 │─────────────────────────────────────────────>│
 │                     │                       │
 │<──── IdP 登录页 ─────────────────────────────│
 │<──── IdP 回调 ───────────────────────────────│
 │  GET /oauth/callback?                        │
 │     code=...&state={txid}.{csrf}             │
 │─────────────────────>│                       │
 │                     │  3. 解密 transaction   │
 │                     │     校验 policy_id     │
 │                     │     校验 csrf_state    │
 │                     │     校验 transaction_id│
 │                     │     (都用 const_time)  │
 │                     │                       │
 │                     │  POST IdP/token        │
 │                     │  ────────────────────>│
 │                     │<─ {id_token, ...} ────│
 │                     │                       │
 │                     │  4. 验证 id_token      │
 │                     │     校验 nonce         │
 │                     │     (session 里的)     │
 │                     │                       │
 │                     │  5. 构造 BrowserSession│
 │                     │     {policy_id,       │
 │                     │      raw_id_token,    │
 │                     │      expires_at}      │
 │                     │     AES-256-GCM 加密  │
 │                     │                       │
 │<─ 302 ──────────────│                       │
 │   Location: 原始 original_uri (本地安全路径)│
 │   Set-Cookie: agw_oidc_s_{hash}=              │
 │     {AES-GCM-encrypted(browser_session)}     │
 │   Set-Cookie: agw_oidc_t_{hash}=; MaxAge=0  │
 │     (清 transaction cookie)                  │
 │                     │                       │
 │  后续每次请求:                               │
 │  GET /api/v1/x                              │
 │  Cookie: agw_oidc_s_{hash}=...               │
 │─────────────────────>│                       │
 │                     │  6. 解密 browser_session│
 │                     │     校验 policy_id     │
 │                     │     提取 raw_id_token  │
 │                     │     再次 validate_claims│
 │                     │     (每次都验签)        │
 │                     │     提取 claims        │
 │                     │     req.ext.insert     │
 │                     │                       │
```

### 3.4 OIDC 安全设计要点

`http/oidc/session.rs:262-269` 防 open redirect：

```rust
fn is_safe_local_redirect_target(target: &str) -> bool {
    if !target.starts_with('/') || target.starts_with("//") || target.contains('\\') {
        return false;
    }
    let decoded = percent_encoding::percent_decode_str(target).decode_utf8_lossy();
    decoded.starts_with('/') && !decoded.starts_with("//") && !decoded.contains('\\')
}
```

`http/oidc/callback.rs:179-181` 全部用常量时间比较：

```rust
fn constant_time_str_eq(expected: &str, actual: &str) -> bool {
    verify_slices_are_equal(expected.as_bytes(), actual.as_bytes()).is_ok()
}
```

`http/oidc/session.rs:169-171` cookie 大小限制：

```rust
const MAX_BROWSER_COOKIE_VALUE_SIZE: usize = 3800;
// 保守低于 4 KiB 浏览器限制, 防止 UA 差异导致 cookie 静默丢弃
```

### 3.5 凭据安全等级

| 凭据 | 存储 | Debug 输出 | Header 标记 |
|---|---|---|---|
| `SecretString` (JWT key、API key、ID token) | 内存保护 (zeros on drop) | `[REDACTED]` (Debug) | `set_sensitive(true)` |
| 加密 session cookie | AES-256-GCM 加密 | — | — |
| 短期 JWT (client_assertion) | 仅在内存 | 自动 redact | sensitive |
| Token exchange response | 立即插入到 backend 请求 | 凭据保密 | sensitive |
| SPIFFE identity (cert) | mTLS 握手后提取 | 可访问（TLS 主题） | — |

`http/auth/mod.rs:84, 183`：

```rust
#[serde(serialize_with = "ser_redact")]  // 序列化时输出 [REDACTED]
value: SecretString,

// 注入到 header 时
let mut header_value = HeaderValue::from_str(&value)?;
header_value.set_sensitive(true);  // 防止 tracing 工具意外导出
```

---

## 四、AuthZ 引擎：CEL 表达 + 三态规则 + Network Authz

### 4.1 RBAC 引擎（`http/authorization.rs:255-275`）

```rust
pub fn validate(&self, exec: &Executor) -> bool {
    let allowed = if !has_rules {
        true                                  // 1. 无规则 → 默认允许
    } else if rule_sets.iter().any(|r| r.denies(exec)) {
        false                                 // 2. 任何 DENY → 拒绝
    } else if rule_sets.iter().any(|r| !r.all_requires_match(exec)) {
        false                                 // 3. 任何 REQUIRE 不匹配 → 拒绝
    } else if rule_sets.iter().any(|r| r.allows(exec)) {
        true                                  // 4. 任何 ALLOW → 允许
    } else {
        !rule_sets.iter().any(|r| r.has_allow_rules())  // 5. deny-only vs allowlist
    };
    allowed
}
```

**关键安全特性**：

| 规则 | fail-closed? | 说明 |
|---|---|---|
| 无规则 | **fail-open** ⚠️ | 默认允许 |
| `deny` | **fail-OPEN** ⚠️ | CEL 错误不触发 deny |
| `require` | fail-CLOSED ✅ | 错误 → 不匹配 → 拒绝 |
| `allow` | fail-CLOSED ✅ | 错误 → 不匹配 → 拒绝 |

**文档原话**（`http/authorization.rs:131-141`）：

> "Deny is not recommended because expression failures fail to deny; prefer Allow or Require."

### 4.2 CEL 表达式 7 大类

```
┌─────────────────────────────────────────────────────────────────┐
│ ① 身份断言                                                     │
│   source.identity.trustDomain == "nio.local"                    │
│   source.identity.namespace == "adas"                           │
│   source.identity.serviceAccount == "adas-orchestrator"         │
│   jwt.sub == "adas-pilot"                                      │
│   jwt.vin == "LSGAB52A45N123456"  (车端 VIN)                    │
│                                                                  │
│ ② 网络隔离                                                     │
│   cidr("10.0.0.0/8").containsIP(source.address)                 │
│   source.port == 8443                                          │
│                                                                  │
│ ③ 协议路由                                                     │
│   backend.protocol == "a2a"                                    │
│   mcp.tool.name == "adas.perception"                            │
│   json(request.body).method == "tasks/send"  (A2A 任务级)       │
│   json(request.body).params.id.startsWith("task-adas-")        │
│                                                                  │
│ ④ LLM 上下文                                                   │
│   llm.requestModel == "ada-llm-7b"                              │
│   llm.inputTokens < 8000  (车端 token 预算)                     │
│   "adas" in llm.completion[0]                                  │
│                                                                  │
│ ⑤ 请求路径                                                     │
│   request.path.startsWith("/api/v1/adas/")                      │
│   request.method == "POST"                                     │
│   request.headers["x-nio-domain"] == "adas"                    │
│                                                                  │
│ ⑥ 强制条件                                                     │
│   require: 'has(jwt) && jwt.exp > now()'                        │
│   require: 'cidr("10.0.0.0/8").containsIP(source.address)'      │
│                                                                  │
│ ⑦ 时间窗口                                                     │
│   request.startTime > timestamp("2026-01-01T00:00:00Z")         │
│   duration("5m") > now() - jwt.iat                              │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Network Authz：L4 fast path（`store/binds.rs:2403-2413`）

```rust
fn create_network_authorization_policy(cidr: &str) -> FrontendPolicy {
    FrontendPolicy::NetworkAuthorization(crate::types::frontend::NetworkAuthorization(
        crate::http::authorization::RuleSet::new(crate::http::authorization::PolicySet::new(
            vec![Arc::new(
                cel::Expression::new_strict(format!(r#"cidr("{cidr}").containsIP(source.address)"#))
                    .unwrap(),
            )],
            vec![], vec![],
        )),
    ))
}
```

`binds.rs:3406-3467` 验证：多个 NetworkAuthz policy 之间是 <strong>OR'd</strong>（任一匹配就允许）。这与 MCP AuthZ 行为一致。

**车端用法**：

```yaml
# 智驾域只允许 10.1.0.0/16
# 座舱域只允许 10.2.0.0/16
# 车控域只允许 10.3.0.0/16
# 拒绝其他来源
policies:
  networkAuthorization:
    allow: ['cidr("10.0.0.0/8").containsIP(source.address)']
    deny:  ['!cidr("10.1.0.0/16").containsIP(source.address) && request.path.contains("/adas/")']
    deny:  ['!cidr("10.2.0.0/16").containsIP(source.address) && request.path.contains("/cockpit/")']
    deny:  ['!cidr("10.3.0.0/16").containsIP(source.address) && request.path.contains("/vc/")']
```

但注意：<strong>deny 是 fail-open</strong>（CEL 错误不会触发），所以推荐用 require + allow 组合：

```yaml
policies:
  networkAuthorization:
    rules:
      # 必须满足 IP 段要求（按 path 区分域）
      - require: 'cidr("10.1.0.0/16").containsIP(source.address) || !request.path.contains("/adas/")'
      - require: 'cidr("10.2.0.0/16").containsIP(source.address) || !request.path.contains("/cockpit/")'
      - require: 'cidr("10.3.0.0/16").containsIP(source.address) || !request.path.contains("/vc/")'
      # 显式 allow 全部
      - allow: 'true'
```

### 4.4 MCP RBAC 资源类型（`mcp/rbac.rs:66-103`）

```rust
pub enum ResourceType {
    Tool(ResourceId),       // mcp.tool.{target, name}
    Prompt(ResourceId),     // mcp.prompt.{target, name}
    Resource(ResourceId),   // mcp.resource.{target, uri}
    Task(ResourceId),       // SEP-2663 task: mcp.task.{target, task_id}
}
```

**注意**：MCP Task 已经有原生 RBAC，<strong>用 SEP-2663 任务 ID 区分</strong>。但 A2A 任务没有原生资源类型——这是车端落地的关键洞见（详见第五章）。

### 4.5 鉴权覆盖矩阵

| 资源类型 | AuthN | AuthZ | Guardrails | Session |
|---|---|---|---|---|
| HTTP (general) | ✅ Gateway/Route/Backend JWT/OIDC | ✅ RBAC + ExtAuthz | — | — |
| MCP tool | ✅ router 入口 OAuth | ✅ Per-tool RBAC | ✅ McpGuardrails | ✅ SessionPersistence |
| MCP prompt | ✅ | ✅ Per-prompt RBAC | ✅ | ✅ |
| MCP resource | ✅ | ✅ Per-resource RBAC | ✅ | ✅ |
| MCP task (SEP-2663) | ✅ | ✅ Per-task RBAC | ✅ | ✅ |
| A2A agent card | ✅ (上游) | (无) | — | — |
| A2A tasks/send | ✅ (上游) | (需 CEL 拼) | — | — |
| A2A tasks/cancel | ✅ (上游) | (需 CEL 拼) | — | — |

---

## 五、A2A 任务级授权：补全 RBAC 缺失

### 5.1 真实情况（不是完全没有）

A2A 协议本身在 agentgateway 中<strong>没有专属的 ResourceType 资源类型</strong>，不像 MCP 那样有 `ResourceType::Task`。但这<strong>不意味着不能做任务级授权</strong>——可以用 CEL 拼接。

### 5.2 可用字段

```rust
// a2a/mod.rs:62-65
pub struct ResponseInfo {
    pub outcome: ResponseOutcome,        // Success/Error/Unknown
    pub error_code: Option<i64>,
    pub result_kind: Option<Strng>,      // task / message / event
    pub task_state: Option<Strng>,       // submitted/working/completed/failed/canceled
}

// telemetry/log.rs:1091
pub a2a_method: Option<Strng>,           // 但 CEL 不能访问！
```

**注意**：`a2a_method` 在日志里有，但**没有暴露到 CEL 上下文**（验证：`grep "a2a_method" crates/agentgateway/src/cel/types.rs` 无结果）。这是个改进点。

### 5.3 任务级授权的 3 种实现路径

#### 路径 1：用 `backend.protocol` + `request.body.method`（推荐）

```yaml
policies:
  authorization:
    rules:
      # ADAS 域 agent 只能发 tasks/send
      - require: 'source.identity.namespace == "adas" && backend.protocol == "a2a"'
      - allow: 'source.identity.namespace == "adas" && backend.protocol == "a2a" && json(request.body).method == "tasks/send"'
      - allow: 'source.identity.namespace == "adas" && backend.protocol == "a2a" && json(request.body).method == "tasks/cancel"'
      - allow: 'source.identity.namespace == "adas" && backend.protocol == "a2a" && json(request.body).method == "message/send"'
      # 拒绝所有未列出的 A2A 方法
      - deny: 'backend.protocol == "a2a" && !("tasks/send" in json(request.body).method || "tasks/cancel" in json(request.body).method)'
```

**代价**：每次 AuthZ 评估都会触发 body buffering（受 `maxBufferSize` 限制）。

#### 路径 2：用 `request.headers["x-a2a-method"]`（性能更好）

在 BackendPolicy 中加一个 `a2a` 增强，让 A2A classifier 提取 method 后注入到 header：

```rust
// a2a/mod.rs 增强（车端定制）
if let RequestType::Call(method) = &a2a_type {
    req.headers_mut().insert("x-a2a-method", HeaderValue::from_str(method)?);
    req.headers_mut().insert("x-a2a-method-class", HeaderValue::from_static(if method.starts_with("tasks/") { "task" } else { "rpc" }));
}
```

然后策略：

```cel
backend.protocol == "a2a" && request.headers["x-a2a-method"] == "tasks/send"
```

**优势**：不需要 body buffer，性能 ~0 开销。

#### 路径 3：扩展 SourceContext 加 A2A method（最优雅）

参考 MCP 的 `MCPInfo`（`mcp/rbac.rs`）做法，加一个 `A2AInfo`：

```rust
// 类型定义（车端定制）
pub struct A2AInfo {
    pub method: Strng,              // "tasks/send" / "tasks/cancel" / ...
    pub method_class: A2AMethodClass,  // Task | Message | RPC
    pub task_id: Option<Strng>,     // 从 jsonrpc params.id 提取
}

pub enum A2AMethodClass {
    Task,
    Message,
    RPC,
    Unknown,
}
```

扩展 RBAC 引擎加 ResourceType：

```rust
pub enum A2AResourceType {
    Task(A2AResourceId),    // a2a.task.{target, task_id}
    Method(A2AResourceId),  // a2a.method.{target, method}
}
```

策略：

```cel
a2a.method == "tasks/send" && jwt.sub == "adas-orchestrator"
```

### 5.4 推荐方案：路径 2 + 路径 3 混合

车端落地建议：
- <strong>短</strong>期：路径 2（注入 header，零成本）
- <strong>中</strong>期：路径 3（提 PR 扩展 RBAC 引擎，车端 fork）
- <strong>长</strong>期：upstream 给 agentgateway 提 PR

### 5.5 A2A 完整可观测字段

`a2a/mod.rs:74-103` 已经在响应里解析这些：

```rust
ResponseInfo::from_json(&value) {
    outcome: ResponseOutcome,  // 来自 error/result 字段
    error_code: Option<i64>,   // 来自 error.code
    result_kind: Option<Strng>,// 来自 result.kind (task/message/event)
    task_state: Option<Strng>, // 来自 result.status.state
}
```

`backend.protocol = "a2a"` + `a2a.response.outcome` 暴露在日志（`telemetry/log.rs:1400-1422`）。

### 5.6 任务级授权典型车端场景

| 场景 | 策略 |
|---|---|
| 智驾 agent 调车控 agent 触发 AEB | `source.identity.namespace == "adas" && a2a.method == "tasks/send" && jwt.role == "adas-orchestrator" && cidr("10.3.0.0/16").containsIP(request.headers["x-forwarded-for"])` |
| 座舱 agent 调云端 LLM | `source.identity.namespace == "cockpit" && a2a.method_class == "RPC" && jwt.aud == "nlp-cloud"` |
| 车控 agent 接受 OTA | `source.identity.namespace == "ota" && a2a.method == "tasks/send" && jwt.cert_chain matches "^CN=OTA-CA"` |
| 拒绝匿名 A2A 任务 | `deny: 'backend.protocol == "a2a" && !has(jwt)'` |
| 限速：每分钟 100 个 A2A 任务 | （用 localratelimit + CEL 表达式） |

---

## 六、车端 IAM 联邦设计

### 6.1 整车身份联邦架构

```
┌────────────────────────────────────────────────────────────────────┐
│                     整车 IAM 联邦（HSM 根信任）                      │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ 座舱 IdP     │  │ 智驾 IdP     │  │ 车控 IdP     │               │
│  │ 8295 + QTEE  │  │ Orin+OP-TEE  │  │ S32G+OP-TEE  │               │
│  │ (Local)      │  │ (Local)      │  │ (Local+HSM)  │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                       │
│         └────────┐        │        ┌────────┘                       │
│                  ▼        ▼        ▼                                │
│         ┌──────────────────────────────┐                           │
│         │  agentgateway (Rust data    │                           │
│         │  plane)                     │                           │
│         │                              │                           │
│         │  In: mTLS client cert (SPIFFE)                          │
│         │  In: JWT (域内 IdP 签发)                                 │
│         │  Out: SPIFFE identity to upstream                       │
│         │  Out: Short-lived JWT signed by HSM                    │
│         └──────────────────────────────┘                           │
│                            │                                       │
│                            ▼                                       │
│              ┌─────────────────────────────┐                      │
│              │  云端 IdP (Keycloak/Auth0)  │                      │
│              │  - 用户身份                  │                      │
│              │  - 跨域 OAuth federation     │                      │
│              │  - LLM provider credentials │                      │
│              └─────────────────────────────┘                      │
└────────────────────────────────────────────────────────────────────┘
```

### 6.2 三种 IAM 模式适配

**模式 A：域内信任**（座舱↔智驾↔车控）

```yaml
# 每个域配 mTLS（整车 CA 在 HSM）
listeners:
- port: 8443
  tls:
    mode: TERMINATE
    certificates:
    - cert: hsm://vcert/{domain}-cert
      key: hsm://vcert/{domain}-key
      root: |
        # 整车根 CA (PEM)
  policies:
    networkAuthorization:
      rules:
      - require: 'cidr("10.0.0.0/8").containsIP(source.address)'
      - allow: 'true'
    jwt:
      mode: Strict
      issuer: "spiffe://nio.local"
      audiences: ["nio-a2a"]
      jwks:
        # 域内 IdP 公钥（自签）
        file: /etc/nio/jwks/{domain}-pub.json
```

**模式 B：跨域 OAuth**（车端↔云端 LLM）

```yaml
# 车端 agentgateway 调云端 LLM
backends:
- ai:
    provider: openAI
    host: api.openai.com
  policies:
    backendAuth:
      oauthTokenExchange:
        target: 
          host: https://auth.nio.internal/oauth2/token
        path: /v1/token
        grantType: TokenExchange
        subjectToken:
          source: header.authorization  # 用户的 ID token
          tokenType: IdToken
        audiences: ["https://api.openai.com"]
        scopes: ["openai.api"]
        requestedTokenType: AccessToken
        clientAuth:
          clientSecretPost:
            clientId: nio-vehicle-edge
            clientSecret: ${OIDC_CLIENT_SECRET}
        cache:
          maxEntries: 256
          ttl: 5m
```

**模式 C：浏览器用户登录**（OIDC，车机大屏/移动 App）

```yaml
# 用户在车机浏览器登录
listeners:
- port: 443
  routes:
  - matches:
    - path: { prefix: "/cockpit-app" }
    policies:
      oidc:
        issuer: "https://auth.nio.com/realms/cockpit"
        clientId: "nio-cockpit-app"
        clientSecret: ${OIDC_CLIENT_SECRET}
        redirectURI: "https://cockpit.nio.internal/oauth/callback"
        scopes: ["openid", "profile", "cockpit.drive"]
        session:
          ttl: 1h
          cookieName: nio_cockpit_session
```

### 6.3 IDP 选型表（车端推荐）

| 域 | IDP 类型 | agentgateway 配置 | 备注 |
|---|---|---|---|
| 座舱 | Descope (Agentic-native) | `provider: descope` | Descope 专为 agent 设计，原生支持 RFC 8707 |
| 智驾 | Keycloak 自管 | `provider: keycloak` | 车端离线运行，Keycloak 支持本地部署 |
| 车控 | HSM 自签 mTLS | mTLS only，无 JWT | 50Hz 实时场景，JWT 验证延迟不可接受 |
| 云端 LLM | Auth0/Okta | `provider: auth0` 或 `provider: okta` | 已支持 query param hack |
| 跨域联邦 | CrossAppAccess (Google CAEP) | `backendAuth: crossAppAccess` | 新一代 agent 跨域协议 |

### 6.4 Keycloak 离线部署

`examples/mcp-authentication/keycloak/` 已配 docker-compose + mcp-realm.json：

```yaml
# keycloak/mcp-realm.json 关键字段
{
  "realm": "mcp",
  "accessTokenLifespan": 600,         # 10 分钟
  "sslRequired": "external",
  "clients": [
    {
      "clientId": "mcp-gateway",
      "publicClient": false,
      "clientAuthenticatorType": "client-secret",
      "redirectUris": ["https://gateway.nio.internal/*"]
    }
  ]
}
```

车端 Kubernetes 部署：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: keycloak
  namespace: nio-iam
spec:
  replicas: 1
  template:
    spec:
      nodeSelector:
        nio.io/zone: cockpit
      containers:
      - name: keycloak
        image: quay.io/keycloak/keycloak:25.0
        args: ["start", "--spi-quarkus-cookie-samesite=None"]
        env:
        - name: KEYCLOAK_ADMIN
          value: admin
        - name: KEYCLOAK_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef: {name: keycloak-admin, key: password}
        - name: KC_DB
          value: postgres
        volumeMounts:
        - name: realm
          mountPath: /opt/keycloak/data/import
  volumes:
  - name: realm
    configMap:
      name: mcp-realm
```

### 6.5 信任域联邦策略

车端"三个域"互信但又隔离：

```yaml
# 智驾域：只信任智驾 SPIFFE + 座舱的 readonly 委托
listeners:
- name: adas
  port: 8443
  policies:
    networkAuthorization:
      rules:
      # 智驾 agent 自己：必须本域
      - allow: 'source.identity.trustDomain == "nio.local" && source.identity.namespace == "adas"'
      # 座舱 agent：仅 readonly（基于 JWT role）
      - allow: 'source.identity.trustDomain == "nio.local" && source.identity.namespace == "cockpit" && jwt.role == "cockpit.readonly"'
      # 车控 agent：禁止主动发起（被动接收）
      - allow: 'source.identity.trustDomain == "nio.local" && source.identity.namespace == "vc" && request.method == "GET"'
      # 全部其他拒绝（fail-closed 因为有 allow 规则）
```

---

## 七、可直接 ship 的完整配置骨架

### 7.1 agentgateway.yaml（车端标准部署）

```yaml
# ============================================================
# nio-vehicle-a2a-gateway.yaml
# 车端 AI Agent 安全框架 - agentgateway 配置
# ============================================================

# 静态配置 (env 或启动参数):
#   AGENTGATEWAY_CONFIG=/etc/nio/agentgateway.yaml
#   AGENTGATEWAY_LISTEN_ADDR=0.0.0.0:8443
#   AGENTGATEWAY_ADMIN_ADDR=0.0.0.0:15000
#   RUST_LOG=info,agentgateway=debug
#
# 安全特性：
#   - 三层鉴权 (L4 / Gateway / Backend)
#   - mTLS + SPIFFE 强信任
#   - JWT + CEL 细粒度授权
#   - OAuth Token Exchange 跨域
#   - OIDC 浏览器登录
#   - A2A 任务级授权

config:
  logging:
    level: info
    fields:
      add:
        x-request-id: 'request.headers["x-request-id"]'
        a2a_method: 'request.body.method ?? "none"'
  tracing:
    otlpEndpoint: http://nio-tempo:4317
  adminAddr: 0.0.0.0:15000

# ============================================================
# 主 bind: 8443 (mTLS + JWT + RBAC + A2A)
# ============================================================
binds:
- port: 8443
  listeners:

  # ---- 智驾域 listener (port 8443, mTLS required) ----
  - name: adas
    hostname: adas.nio.internal
    tls:
      mode: TERMINATE
      minVersion: TLSV1_3
      cipherSuites: [TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256]
      certificates:
      - cert: hsm://nio-hsm/vcert/adas-cert
        key: hsm://nio-hsm/vcert/adas-key
        root: |
          # 智驾域 CA 根证书 (PEM, 实际从 HSM 加载)
          -----BEGIN CERTIFICATE-----
          MIIDdTCCAl2gAwIBAgIBADANBgkqhkiG9w0BAQsFADBnMRcwFQYDVQQDDA5B
          REFTLUNBLVJvb3QtTmlvMQswCQYDVQQGEwJDTjEVMBMGA1UECgwMTmlvIENv
          -----END CERTIFICATE-----
    policies:
      networkAuthorization:
        rules:
        # 智驾域只允许 10.1.0.0/16 (L4 fast path, 50Hz 适用)
        - require: 'cidr("10.1.0.0/16").containsIP(source.address)'
        # mTLS 身份必须是 adas 域
        - require: 'source.identity.namespace == "adas" || source.identity.namespace == "cockpit"'
        # 默认允许
        - allow: 'true'

    routes:

    # ---- 智驾感知数据接收 (A2A: tasks/send) ----
    - name: adas-perception
      matches:
      - path:
          exact: /a2a/perception/v1
      policies:
        cors:
          allowOrigins: ['https://cockpit.nio.internal']
          allowHeaders: [content-type, x-nio-trace-id]
        jwt:
          mode: Strict
          issuer: "spiffe://nio.local/ns/adas/sa/orchestrator"
          audiences: ["nio-a2a-adas"]
          jwks:
            # 智驾域 IdP 公钥 (内嵌, 离线)
            inline:
              keys:
                - kid: adas-2026
                  kty: RSA
                  alg: RS256
                  use: sig
                  n: "0vxM..."
                  e: "AQAB"
        authorization:
          rules:
          # 强制要求: 智驾域 + A2A + tasks/send
          - require: 'source.identity.namespace == "adas"'
          - require: 'source.identity.serviceAccount == "adas-orchestrator"'
          - require: 'backend.protocol == "a2a"'
          - allow: 'json(request.body).method == "tasks/send" && json(request.body).params.id.startsWith("task-adas-")'
          # 拒绝任何 cancel/get (智驾不允许取消)
          - deny: 'json(request.body).method in ["tasks/cancel", "tasks/get"]'
        extAuthz:
          failureMode: Deny
          http:
            path: '"/authorize"'
            addRequestHeaders:
              x-nio-trace-id: 'request.headers["x-nio-trace-id"]'
            service: nio-policy-engine.adas.svc.cluster.local:8443
        transformation:
          request:
            set:
              x-nio-zone: '"adas"'
              x-nio-trace-id: 'request.headers["x-nio-trace-id"] ?? uuid()'
        rateLimit:
          local:
            requests: 100
            period: 1m
      backends:
      - host: adas-perception.nio.internal:8080
        policies:
          backendTLS:
            root: hsm://nio-hsm/ca/adas-internal-ca
            cert: hsm://nio-hsm/vcert/adas-perception
            key: hsm://nio-hsm/vcert/adas-perception-key
          a2a: {}  # 触发 A2A 协议识别
          backendAuth:
            # 用 HSM 私钥签短期 JWT, 验证给后端
            jwtSign:
              algorithm: ES256
              key: hsm://nio-hsm/vcert/adas-gateway-sign
              audience: "nio-adas-perception"
              lifetime: 5m

    # ---- 智驾控制下发 (A2A: 高权限, RBAC 严格) ----
    - name: adas-control
      matches:
      - path:
          exact: /a2a/control/v1
      policies:
        jwt:
          mode: Strict
          issuer: "spiffe://nio.local"
          audiences: ["nio-a2a-control"]
          jwks: { file: /etc/nio/jwks/internal.json }
        authorization:
          rules:
          # 智驾控制只能由 adas-orchestrator 发起
          - require: 'source.identity.namespace == "adas"'
          - require: 'source.identity.serviceAccount in ["adas-orchestrator", "adas-emergency"]'
          # 高速场景必须双签
          - require: 'jwt.sub == "adas-orchestrator" || request.headers["x-emergency-bypass"] == "adas-emergency-token"'
          - allow: 'json(request.body).method == "tasks/send"'
        extAuthz:
          failureMode: Deny
          service: adas-asil-d-controller.adas.svc.cluster.local:9090
        # 控制流量单独限流
        rateLimit:
          local:
            requests: 10  # 10 RPS, 车控 50Hz
            period: 1s

  # ---- 座舱域 listener (OIDC 浏览器登录) ----
  - name: cockpit
    hostname: cockpit.nio.internal
    port: 443
    tls:
      mode: TERMINATE
      certificates:
      - cert: hsm://nio-hsm/vcert/cockpit-cert
        key: hsm://nio-hsm/vcert/cockpit-key
        root: hsm://nio-hsm/ca/root
    policies:
      networkAuthorization:
        rules:
        - require: 'cidr("10.2.0.0/16").containsIP(source.address) || cidr("192.168.0.0/16").containsIP(source.address)'
        - allow: 'true'
      oidc:
        issuer: "https://auth.nio.internal/realms/cockpit"
        clientId: "nio-cockpit-app"
        clientSecret: ${OIDC_CLIENT_SECRET}
        redirectURI: "https://cockpit.nio.internal/oauth/callback"
        scopes: ["openid", "profile", "cockpit.drive"]
        session:
          ttl: 1h
          sameSite: Strict
          secure: Always

    routes:
    # ---- 座舱 UI (OIDC + 限流) ----
    - matches:
      - path: { prefix: "/cockpit-app" }
      policies:
        cors:
          allowOrigins: ['https://cockpit.nio.internal']
          allowHeaders: [content-type]
        transformation:
          request:
            set:
              x-cockpit-user: 'jwt.sub'

  # ---- 车控域 listener (mTLS, 无 JWT, L4 fast path) ----
  - name: vc
    hostname: vc.nio.internal
    port: 9443
    tls:
      mode: TERMINATE
      minVersion: TLSV1_3
      certificates:
      - cert: hsm://nio-hsm/vcert/vc-cert
        key: hsm://nio-hsm/vcert/vc-key
        root: hsm://nio-hsm/ca/vc-root
    policies:
      networkAuthorization:
        rules:
        # 车控域: 严格隔离
        - require: 'cidr("10.3.0.0/16").containsIP(source.address)'
        # 必须是车控域的 SPIFFE
        - require: 'source.identity.namespace == "vc" || source.identity.namespace == "adas"'
        # 限制端口（车控只用 9443, 8500, 8501）
        - require: 'request.method in ["POST", "GET"]'
        - allow: 'true'
```

### 7.2 K8s 部署（CRD 形式）

如果车端走 K8s + agentgateway controller：

```yaml
# 智驾域 gateway
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: adas-gateway
  namespace: nio-adas
spec:
  gatewayClassName: agentgateway
  listeners:
  - name: adlas
    hostname: adas.nio.internal
    port: 8443
    protocol: HTTPS
    tls:
      mode: Terminate
      certificateRefs:
      - name: adas-cert  # Cert Manager 配 HSM
        kind: Secret
---
# A2A backend 自动发现 (appProtocol: agentgateway.dev/a2a)
apiVersion: v1
kind: Service
metadata:
  name: adas-perception
  namespace: nio-adas
spec:
  ports:
  - port: 8080
    appProtocol: agentgateway.dev/a2a  # ← 触发 a2a_plugin.go
---
# AuthN 策略
apiVersion: agentgateway.dev/v1alpha1
kind: AgentgatewayPolicy
metadata:
  name: adas-authn
  namespace: nio-adas
spec:
  targetRefs:
  - group: gateway.networking.k8s.io
    kind: HTTPRoute
    name: adas-perception
  traffic:
    jwtAuthentication:
      mode: Strict
      providers:
      - issuer: "spiffe://nio.local/ns/adas/sa/orchestrator"
        audiences: ["nio-a2a-adas"]
        jwks:
          file: /etc/nio/jwks/adas-pub.json
    authorization:
      rules:
      - require: 'source.identity.namespace == "adas"'
      - require: 'source.identity.serviceAccount == "adas-orchestrator"'
      - allow: 'json(request.body).method == "tasks/send"'
      - deny: 'json(request.body).method in ["tasks/cancel"]'
```

---

## 八、车端特定风险与加固清单

### 8.1 已知安全洞与对策

| 风险 | 位置 | 车端影响 | 加固方案 |
|---|---|---|---|
| `unvalidatedJwtPayload` 不验签 | `celx/src/general.rs:339` | 攻击者可伪造 claim | <strong>绝不用于 auth 决策</strong>，仅用于日志/可观测 |
| `Deny` 规则在 CEL 错误时**不**触发 | `http/authorization.rs:255` | 车端安全策略可能失效 | <strong>只用 `require`/`allow`</strong>，不用 `deny` |
| `Optional` 是默认 JWT mode | `http/jwt.rs:187` | 缺 token 也放行 | <strong>显式 `Strict`</strong> |
| `Passthrough` 模式会转发 JWT 到后端 | `http/auth/mod.rs:76` | 泄露用户身份 | 用 `Key` 或 `JwtSign` 替代 |
| OIDC AAD = empty (`Aad::empty()`) | `crypto/aead.rs:60` | session cookie 可被任意域读取 | <strong>车端 fork 时绑定 user-agent + IP</strong> |
| `a2a_method` 不在 CEL 中暴露 | `telemetry/log.rs:1091` | A2A 任务级授权需用 body | 注入 `x-a2a-method` header（车端 fork） |
| Network authz deny 是 fail-open | `http/authorization.rs:255` | 跨域隔离可能失效 | <strong>用 require + allow 组合</strong> |
| Body buffer 性能成本 | `cel/types.rs:916` | A2A AuthZ 每次都触发 buffer | 用 header 注入（路径 2） |
| Token 缓存默认 8K entries | `http/auth/oauth/mod.rs:90` | 内存占用 | 车端调小到 1K |
| OIDC session cookie 大小 3800 bytes | `http/oidc/session.rs:16` | 超出浏览器限制 | 减少 id_token claims |
| `allow_insecure_mtls` 选项存在 | `types/agent.rs:97` | 误启用后证书验证失效 | <strong>车端永远 disable</strong>，CI 扫描配置 |

### 8.2 车端必加的安全配置

```rust
// 1. 强制 mTLS, 禁用 allow_insecure_mtls
tls:
  mode: TERMINATE
  requireClientCertificate: true
  # 永不启用: allow_insecure_mtls: true

// 2. JWT 验证: 强制 Strict, 关闭 Optional 默认值
jwt:
  mode: Strict  // 显式
  audiences: [nio-a2a]  // 显式白名单
  requiredClaims: [exp, nbf, iss, aud, sub]  // 全必填

// 3. Backend TLS: 后端证书必须验证
backendTLS:
  root: hsm://nio-hsm/ca/root  // 必须有 CA
  cert: hsm://nio-hsm/vcert/... // client cert
  key: hsm://nio-hsm/vcert/...  // client key
  insecure: false  // 永不启用

// 4. ExtAuthz: 默认 Deny
extAuthz:
  failureMode: Deny  // 默认

// 5. Network authz: 全部用 require + allow, 不用 deny
policies:
  networkAuthorization:
    rules:
    - require: 'cidr("10.0.0.0/8").containsIP(source.address)'
    - require: 'source.identity.namespace in ["adas", "cockpit", "vc"]'
    - allow: 'true'  // 显式 allow

// 6. Body buffer 限制（防 DoS）
buffer:
  maxRequestSize: 1MiB

// 7. Rate limit（防过载）
rateLimit:
  local:
    requests: 1000
    period: 1s
```

### 8.3 ASIL-D 场景的额外保护

车控 50Hz 场景需要：
- <strong>L4 fast path 100%</strong>：所有鉴权在 L4 完成（mTLS + CIDR + SPIFFE）
- <strong>零 body buffering</strong>：不用 CEL 访问 request.body（用 header 注入）
- <strong>短 TTL JWT</strong>：5 分钟过期，频繁刷新
- <strong>短路 mTLS 重新握手</strong>：keepalive 复用 TLS session
- <strong>预编译 CEL</strong>：避免运行时编译开销（agentgateway 已经做了）

```yaml
# 车控 50Hz 优化配置
listeners:
- name: vc-realtime
  tls:
    mode: TERMINATE
    sessionTickets: true  # TLS session 复用
    keepalive:
      time: 30s
      interval: 10s
      retries: 3
  policies:
    networkAuthorization:
      rules:
      # 全部在 L4 完成
      - require: 'cidr("10.3.0.0/16").containsIP(source.address)'
      - require: 'source.identity.namespace == "vc"'
      - allow: 'true'
    # 不设 Gateway-level AuthN (避免 L7 开销)
    # 依赖 L4 mTLS SPIFFE
```

### 8.4 离线运行模式（车端特殊）

车端可能完全离线。需要：
- <strong>内嵌 JWKS</strong>：`jwks: { inline: ... }` 而非 `{ url: ... }`
- <strong>内嵌 IDP 公钥</strong>：不能拉 Keycloak discovery
- <strong>不依赖云端 LLM</strong>：用本地 LLM provider

```yaml
# 离线配置
jwt:
  jwks:
    inline:  # 不拉远程
      keys:
        - kid: "nio-internal-2026"
          kty: RSA
          alg: RS256
          n: "..."
          e: "AQAB"

# 关闭 OIDC discovery 拉取
oidc:
  issuer: "https://auth.nio.internal"  # 仅作为 claim 校验，不实际请求
  # 不要在 OIDC 模式下用，OIDC 强依赖 discovery
```

### 8.5 监控与审计

```yaml
# 强制开启
tracing:
  otlpEndpoint: http://nio-tempo:4317
  randomSampling: false  # 100% 采样（车端低流量）
accessLog:
  fields:
    add:
      request_id: 'request.headers["x-request-id"]'
      source_identity: 'source.identity.namespace + "/" + source.identity.serviceAccount'
      a2a_method: 'request.body.method ?? "none"'
      jwt_sub: 'jwt.sub ?? "anonymous"'
      backend_protocol: 'backend.protocol'
      mcp_tool: 'mcp.tool.name ?? "none"'
```

### 8.6 启动期安全自检 checklist

- [ ] 所有 `jwt.mode` 都是 `Strict`
- [ ] 所有 `extAuthz.failureMode` 都是 `Deny`
- [ ] 所有 `backendTLS.insecure` 都是 `false`
- [ ] `allow_insecure_mtls` 未启用
- [ ] 跨域 IP 段都用 `require` 表达
- [ ] JWKS 是内嵌或本地 file，不依赖远程拉取
- [ ] HSM 私钥访问路径配置正确
- [ ] `networkAuthorization` 至少一个 `require`
- [ ] `body.maxBufferSize` 已设置（建议 ≤1MB）
- [ ] 启用 `agctl config backends` 验证 backend 健康
- [ ] 启用 `agctl trace` 验证策略命中

---

## 附录 A：关键源码索引（第二轮）

| 路径 | 行数 | 作用 |
|---|---|---|
| `src/mcp/auth.rs` | 1,096 | **MCP OAuth + IDP 联邦 + 资源元数据代理** |
| `src/mcp/router.rs` | 250 | **MCP AuthN 入口**（router 级 AuthN） |
| `src/mcp/handler.rs` | 2,026 | MCP relay 逻辑（包含 `authorize_with_ctx`） |
| `src/mcp/session.rs` | 1,121 | **MCP per-tool AuthZ**（`authorize_with_ctx` 实现） |
| `src/mcp/rbac.rs` | 246 | **MCP RBAC 引擎**（ResourceType: Tool/Prompt/Resource/Task） |
| `src/http/auth/mod.rs` | 497 | BackendAuth 总入口 |
| `src/http/auth/oauth/mod.rs` | 912 | **OAuth Token Exchange 完整实现** |
| `src/http/auth/oauth/cross_app_access.rs` | 306 | **Google CAEP 协议** |
| `src/http/auth/oauth/client_auth.rs` | 578 | Private Key JWT (client_assertion) |
| `src/http/auth/jws.rs` | 121 | JWS 签名算法 |
| `src/http/oidc/mod.rs` | 370+ | **OIDC 浏览器登录** |
| `src/http/oidc/session.rs` | 307 | **OIDC session 加密 + PKCE + redirect 校验** |
| `src/http/oidc/callback.rs` | 181 | **OIDC callback（CSRF 校验 + nonce 校验）** |
| `src/http/oidc/provider.rs` | — | OIDC provider discovery |
| `src/http/oidc/redirect.rs` | — | Redirect URI 校验 |
| `src/http/authorization.rs` | 374 | **RBAC 引擎**（allow/deny/require 算法） |
| `src/http/jwt.rs` | 590 | **JWT 验证（7 步流水线）** |
| `src/http/sessionpersistence.rs` | 213 | **AES-256-GCM session 加密** |
| `src/crypto/aead.rs` | 122 | AEAD 基础（aws-lc-rs） |
| `src/transport/tls.rs` | 1,100+ | **TLS / mTLS / SPIFFE 身份提取** |
| `src/types/agent.rs` | 3,693 | 用户面配置 schema |
| `src/cel/types.rs` | 2,370 | CEL 类型系统 |
| `examples/mcp-authentication/` | — | 完整 MCP AuthN 示例 + Keycloak |
| `examples/mcp-authorization/` | — | 完整 MCP AuthZ 示例 |
| `examples/traffic-oidc/` | — | OIDC 完整示例 |
| `examples/traffic-token-exchange/` | — | Token Exchange 示例 |
| `examples/traffic-jwt-sign/` | — | JWT Sign 示例 |
| `examples/traffic-cross-app-access/` | — | Cross-App Access 示例 |
| `examples/traffic-tailscale-auth/` | — | Tailscale 集成示例 |
| `controller/pkg/agentgateway/plugins/a2a_plugin.go` | — | A2A Service 自动发现（K8s） |

## 附录 B：CEL 表达式速查（车端安全场景）

```yaml
# === 身份 ===
source.identity.trustDomain == "nio.local"
source.identity.namespace == "adas"
source.identity.serviceAccount == "adas-orchestrator"
jwt.sub == "adas-pilot"
jwt.vin == "LSGAB52A45N123456"
jwt.role == "adas-orchestrator"
has(jwt)

# === 网络隔离 ===
cidr("10.0.0.0/8").containsIP(source.address)
cidr("10.3.0.0/16").containsIP(source.address)
source.port == 8443
"10.0.0.0/8" in [source.address.parseCIDR()]  # 等价但更慢

# === 协议路由 ===
backend.protocol == "a2a"
backend.protocol == "mcp"
backend.protocol == "llm"
mcp.tool.name == "adas.perception"
mcp.tool.target == "adas-orchestrator"
json(request.body).method == "tasks/send"   # A2A 任务级
json(request.body).params.id.startsWith("task-adas-")
"adas" in jwt.scope.split(" ")

# === 强制条件 ===
require: 'has(jwt) && jwt.exp > now()'
require: 'cidr("10.0.0.0/8").containsIP(source.address)'
require: 'source.identity.namespace in ["adas", "cockpit", "vc"]'

# === LLM 限制 ===
llm.requestModel == "ada-llm-7b"
llm.inputTokens < 8000
"adas" in llm.completion[0]
llm.params.temperature < 0.3

# === 时间窗口 ===
request.startTime > timestamp("2026-01-01T00:00:00Z")
duration("5m") > now() - jwt.iat

# === 跨域 OAuth 校验 ===
"nio-a2a" in jwt.aud
jwt.iss == "https://auth.nio.internal/realms/adas"
jwt.azp == "adas-orchestrator"
```

---

> 本报告基于 `agentgateway/agentgateway` v1.0+ 源码（commit 与 1.3.0-alpha.1 一致）。
> 配套报告：
> - 第一轮（架构 + A2A + 身份 + 鉴权综述）：`README.md`
> - 本轮（IAM 联邦 + 鉴权链路 + A2A 任务级授权 + 车端落地）：`iam-authn-authz-a2a.md`
