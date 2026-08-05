# 04 · 安全与企业级实践

> A2A 协议本身只规定了"鉴权元数据"的格式（securitySchemes），**不强制任何具体实现**。这一节讲清楚生产环境需要哪些能力、推荐方案、以及常见反模式。

## 4.1 安全分层

A2A 安全栈建议按 4 层搭建：

```
┌────────────────────────────────────────────┐
│ Layer 4 · 业务级授权 (Authorization)       │
│   "这个 token 能调 convert_currency 吗？" │
├────────────────────────────────────────────┤
│ Layer 3 · 身份认证 (Authentication)        │
│   Bearer JWT / API Key / mTLS              │
├────────────────────────────────────────────┤
│ Layer 2 · 传输加密 (TLS)                    │
│   HTTPS 1.2+ / HTTP/2 + TLS 1.3            │
├────────────────────────────────────────────┤
│ Layer 1 · 网络可达性                        │
│   公网 / VPN / Private Link / Service Mesh │
└────────────────────────────────────────────┘
```

下面按层介绍。

---

## 4.2 传输层：TLS 必须

### 强制要求

- **所有 A2A Server 必须**支持 HTTPS（TLS 1.2+，推荐 1.3）。
- **所有 push notification 的 url 必须**是 HTTPS。
- **mTLS**（客户端证书认证）在企业内网 / 金融 / 医疗场景强烈建议。

### mTLS 配置示例（Nginx 反向代理）

```nginx
server {
  listen 443 ssl http2;
  server_name agent.example.com;

  # 服务端证书
  ssl_certificate     /etc/ssl/certs/agent.crt;
  ssl_certificate_key /etc/ssl/private/agent.key;

  # 客户端证书（CA）
  ssl_client_certificate /etc/ssl/certs/client-ca.crt;
  ssl_verify_client      on;
  ssl_verify_depth       2;

  location /.well-known/agent-card.json {
    proxy_pass http://a2a_backend;
  }
  location / {
    proxy_pass http://a2a_backend;
    proxy_set_header X-Client-DN  $ssl_client_s_dn;
  }
}
```

---

## 4.3 身份认证

Agent Card 在 `securitySchemes` 里**声明它支持哪些认证方式**：

```jsonc
{
  "securitySchemes": {
    "bearer": {
      "type": "HTTP", "scheme": "bearer", "bearerFormat": "JWT"
    },
    "apiKey": {
      "type": "APIKey", "in": "header", "name": "X-API-Key"
    },
    "oauth2": {
      "type": "OAuth2",
      "flows": {
        "authorizationCode": {
          "authorizationUrl": "https://idp.example.com/authorize",
          "tokenUrl":         "https://idp.example.com/token",
          "scopes": {
            "a2a:read":  "Read tasks",
            "a2a:write": "Send messages"
          }
        }
      }
    },
    "mtls": {
      "type": "MTLS"
    }
  },
  "security": [ { "bearer": ["a2a:read", "a2a:write"] } ]   // 默认
}
```

### 4.3.1 Bearer JWT（最常用）

**颁发流程**：

```
┌────────┐   1. 登录   ┌────────┐  2. 颁发 access_token  ┌────────┐
│ Client │ ──────────▶ │  IdP   │ ─────────────────────▶ │ Client │
└────────┘            │ (OIDC) │                          └────────┘
                      └────────┘
```

**调用流程**：

```
┌────────┐  POST /a2a                          ┌────────┐
│ Client │  Authorization: Bearer eyJ...       │ Agent  │
│        │ ──────────────────────────────────▶ │        │
│        │                                     │        │
│        │  1. 拉 JWKS 验签                    │        │
│        │     https://idp/.well-known/...    │        │
│        │  2. 检查 aud/exp/scope               │        │
│        │  3. 通过则处理                       │        │
└────────┘ ◀────────────────────────────────── └────────┘
```

**Agent 侧验证伪代码**：

```python
import jwt, requests

JWKS = requests.get("https://idp/.well-known/jwks.json").json()

def verify(token: str) -> dict:
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header["kid"]
    key = next(k for k in JWKS["keys"] if k["kid"] == kid)
    return jwt.decode(
        token,
        key=key,
        algorithms=["RS256"],
        audience="agent.example.com",   # A2A Server 的 audience
        issuer="https://idp",          # IdP 颁发者
    )

claims = verify(request.headers["Authorization"].split(" ")[1])
if "a2a:write" not in claims.get("scope", ""):
    raise AuthError("missing scope")
```

### 4.3.2 API Key

```http
POST /a2a HTTP/1.1
X-API-Key: sk-xxxxxxxxxxxxxxxx
```

适合**机器对机器**场景。Agent 在网关层验证：

```nginx
location / {
  if ($http_x_api_key != "sk-xxxxxxxxxxxxxxxx") {
    return 403;
  }
  proxy_pass http://a2a_backend;
}
```

### 4.3.3 mTLS

- 不需要 HTTP 头携带凭证。
- TLS 握手时双向校验证书。
- 适合**服务网格**（Istio / Linkerd）。

### 4.3.4 OAuth2 完整流程

适合"Agent 要代表用户调用另一个 Agent"这种**委托场景**：

```
┌────────┐   1. authorize   ┌──────┐   2. consent   ┌──────┐
│  User  │ ───────────────▶ │ IdP  │ ─────────────▶ │ User │
└────────┘                  └──────┘                └──────┘
     ▲                          │
     │ 5. access_token          │ 3. code
     │                          ▼
┌────────┐  4. exchange code  ┌──────┐
│ AgentA │ ─────────────────▶ │ IdP  │
│(client)│                   └──────┘
└────────┘
     │
     │ 6. 用 token 调 AgentB
     ▼
┌────────┐
│ AgentB │  验证 token 中的 aud/scope/sub == User
└────────┘
```

> ⚠️ **安全原则**：AgentA **不应该**拿到 User 的 refresh token。A2A 推荐**用 access token（短生命周期）+ PKCE**。

---

## 4.4 授权（Authorization）

> *"认证"只证明"你是谁"；"授权"决定"你能干什么"。*

### Skill 级授权

Agent Card 的 `skills[]` 可以**覆盖默认安全策略**：

```jsonc
{
  "skills": [
    {
      "id": "convert_currency",
      "securitySchemes": { "apiKey": {} }   // 此技能只用 API Key
    },
    {
      "id": "execute_trade",
      "security": [ { "oauth2": ["trade:execute"] } ]   // 此技能需要 OAuth2 + trade:execute scope
    }
  ]
}
```

### 实施建议

- **默认 deny**：未明确授权的技能一律拒绝。
- **细粒度 scope**：避免一个"admin"覆盖所有操作。
- **审计日志**：每个被调用的技能记录（user / skill / timestamp / result）。
- **速率限制**：用 API Gateway（Envoy / Kong / Apigee）做 QPS 限流。

---

## 4.5 Push Notification 安全

这是 A2A 最容易出**安全洞**的地方。完整流程：

### 步骤 1：客户端注册

```jsonc
{
  "jsonrpc": "2.0",
  "method": "tasks/pushNotificationConfig/set",
  "params": {
    "taskId": "task-abc",
    "config": {
      "url": "https://my-service.com/hooks/a2a",
      "token": "8d2f-uuid-xxxx",                   // 你给 Agent 的"暗号"
      "authentication": {
        "schemes": ["Bearer"],
        "credentials": "eyJhbGciOiJSUzI1NiIs..."   // Agent 调用你时用的 JWT
      }
    }
  }
}
```

### 步骤 2：Agent 推送

```http
POST /hooks/a2a HTTP/1.1
Host: my-service.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
A2A-Token: 8d2f-uuid-xxxx

{ "kind": "status-update", "taskId": "task-abc", "status": {...} }
```

### 步骤 3：你接收侧的验证

```python
@app.post("/hooks/a2a")
async def hook(request: Request):
    # 1. 验证 JWT 签名（用 Agent 的 JWKS 公钥）
    authz = request.headers["Authorization"]
    jwt_token = authz.split(" ")[1]
    claims = verify_jwt(jwt_token, expected_aud="my-service.com")

    # 2. 验证 A2A-Token 与 taskId 匹配
    expected_token = task_token_map[request.json()["taskId"]]
    if request.headers["A2A-Token"] != expected_token:
        raise HTTPException(403)

    # 3. 验签后处理业务
    process_event(await request.json())
```

### 防御清单

- [x] **HTTPS only**。
- [x] **JWT 短有效期**（5-15 分钟），过期必须重发。
- [x] **JWKS 缓存 + 轮转**支持。
- [x] **A2A-Token 一次性 / 短期**。
- [x] **接收端去重**（按 taskId + statusUpdate hash）。
- [x] **拒绝回放**：每条 webhook 都带 `timestamp` + `nonce`，超过 5 分钟视为过期。
- [x] **Webhook 签名校验**（一些 Agent 在 body 加 HMAC）。

---

## 4.6 可观测性

### 必须打点的 4 类事件

| 类别 | 字段 | 用途 |
|--|--|--|
| **请求** | `traceId, spanId, parentSpanId, agentName, method, taskId` | 调用链 |
| **状态变化** | `taskId, fromState, toState, timestamp` | Task 生命周期监控 |
| **业务事件** | `taskId, skillId, userId, result` | 业务分析 |
| **错误** | `errorCode, errorMessage, taskId, method` | 告警 / SLA |

### OpenTelemetry 集成示例

```python
from opentelemetry import trace
from opentelemetry.propagate import inject

tracer = trace.get_tracer("a2a.server")

async def handle_send_message(request):
    with tracer.start_as_current_span("a2a.message.send") as span:
        # 透传 trace context（客户端发起的 trace）
        inject(request.headers)
        span.set_attribute("a2a.task_id", task_id)
        span.set_attribute("a2a.skill_id", skill_id)

        result = await execute_logic(request)
        span.set_attribute("a2a.task_state", result.status.state)
        return result
```

### 关键指标

| 指标 | 类型 | 告警阈值 |
|--|--|--|
| `a2a.requests.total{skill}` | Counter | — |
| `a2a.task.duration_seconds{skill}` | Histogram | P99 > 60s |
| `a2a.task.failures.total{skill, reason}` | Counter | > 1% |
| `a2a.streaming.chunk.duration_seconds` | Histogram | P99 > 2s（首字节） |
| `a2a.push.delivery.failures.total` | Counter | > 5% |

---

## 4.7 API 管理

把 A2A Server 当成"传统 API"管理即可：

```
                            ┌────────────────┐
                            │ API Gateway    │
                            │ (Kong/Apigee/  │
                            │  Envoy+OAuth2) │
                            └───────┬────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌──────────────┐            ┌──────────────┐            ┌──────────────┐
│ Rate Limiting│            │ AuthN/AuthZ  │            │ Observability│
│ 100 req/min  │            │ JWT verify   │            │ OTel logs    │
│ per API key  │            │ Scope check  │            │ metrics      │
└──────────────┘            └──────────────┘            └──────────────┘
```

### 关键实践

- **限流**：按 API Key / JWT sub / SkillId 三维限流。
- **熔断**：下游 LLM / 工具故障时熔断，避免雪崩。
- **配额**：按 Skill 配额（"convert_currency 每月 10000 次"）。
- **白名单**：关键 Skill 只对指定 client_id 开放。

---

## 4.8 多租户

多个部门/客户共用同一个 A2A Server：

### 方案 A：在 metadata 中传递 tenantId

```jsonc
{
  "message": {
    "messageId": "msg-1",
    "role": "ROLE_USER",
    "parts": [{ "text": "..." }],
    "metadata": { "tenantId": "acme-corp" }   // ← 透传到业务层
  }
}
```

服务端按 `metadata.tenantId` 隔离数据 / 配额。

### 方案 B：在 JWT claims 中传递

```jsonc
{
  "sub": "user-123",
  "tenant_id": "acme-corp",       // ← JWT claim
  "scope": "a2a:write"
}
```

更安全（不可篡改），但需要 IdP 支持。

---

## 4.9 反模式与陷阱

| 反模式 | 后果 | 修正 |
|--|--|--|
| ❌ 把 Access Token 写进 metadata 透传到第三方 Agent | Token 泄漏、被滥用 | 只透传 tenantId / taskId，业务标识符 |
| ❌ 在 Part.text 里塞 base64 大文件 | 体积爆炸、性能下降 | 用 `Part.kind=url` 让 Agent 自己下载 |
| ❌ 给所有 Skill 同一个 OAuth scope | 越权 | 每个 Skill 独立 scope |
| ❌ Push Notification url 用 HTTP | 中间人攻击 | 必须 HTTPS |
| ❌ 客户端自己生成 taskId / contextId | 状态错乱 | 永远用服务端返回值 |
| ❌ 复用 JWT 跨多个 Agent | Token 被多端持有 | 每个 Agent 独立 audience |
| ❌ 把内部 LLM 调用错误直接暴露给客户端 | 信息泄漏 | 用 A2A 标准错误码 + 模糊化 message |

---

## 4.10 合规要点

- **GDPR**：Task history 可能含个人数据，需要**保留期限**策略与**用户删除请求**（删掉 contextId 下所有 Task）。
- **SOC2**：审计日志（who/what/when）至少保留 1 年。
- **HIPAA（医疗）**：所有健康数据必须加密（at-rest + in-transit），鉴权必须 mTLS 或 OAuth2 with MFA。
- **数据驻留**：把 Agent 部署在对应地理区域。

---

## 4.11 一个生产级部署拓扑

```mermaid
flowchart LR
    subgraph Internet["Internet"]
        U[User]
    end

    subgraph Edge["Edge / CDN"]
        CDN[CloudFront / Cloudflare]
    end

    subgraph Gateway["API Gateway"]
        K[Kong / Envoy]
        AUTH[OIDC Token Verify]
        RL[Rate Limiter]
        LOG[Audit Logger]
    end

    subgraph Backend["A2A Backend"]
        SVC1[A2A Server 1<br/>Currency Agent]
        SVC2[A2A Server 2<br/>Travel Agent]
        OBS[OpenTelemetry Collector]
    end

    subgraph Tools["Internal MCP Servers"]
        MCP1[MCP: search_flights]
        MCP2[MCP: book_hotel]
    end

    subgraph Storage["Stateful Stores"]
        TS[(Task Store<br/>PostgreSQL)]
        AS[(Agent Card<br/>etcd/Consul)]
    end

    U --> CDN --> K
    K --> AUTH --> RL --> LOG
    RL --> SVC1
    RL --> SVC2
    SVC1 --> OBS
    SVC2 --> OBS
    SVC1 --> MCP1
    SVC2 --> MCP2
    SVC1 --> TS
    SVC2 --> TS
    K --> AS
```

每一层都各司其职：A2A Server 专注"协议 + 业务"，其他横切关注点（认证、限流、可观测）交给网关与基础设施。

---

## 下一步

- 把概念落地：[05 · 实战 1：Hello World](05-hands-on-helloworld.md) — 30 行代码跑通一个 A2A Server + Client。
- 看流式 + 多轮：[06 · 实战 2：流式 + 多轮对话](06-hands-on-streaming.md)。
- 多 Agent 编排：[07 · 实战 3：多 Agent 协作](07-hands-on-multi-agent.md)。