---
title: "车端 LLM Agent IAM 认证架构设计"
description: "车端任务时长跨度极大："
---
# 车端 LLM Agent IAM 认证架构设计

> 范围：3 域控制器（AD / CD / VD） × 多 LLM Agent 场景下的身份认证与凭证生命周期。
> 不依赖云端。所有密钥操作通过 **KMSS lib** 在 TEE 内完成。
> 通信全部收敛 gRPC（UDS 同主机 / TCP 跨域 + mTLS）。

---

## 1. 设计目标

| 目标 | 说明 |
|---|---|
| 离线自洽 | 整车可在断网下完成所有 IAM 操作；策略与 trust bundle 走 OTA 注入 |
| 任务自适应 TTL | 凭证有效期按任务时长分级，避免"短任务长 token"或"长任务短 token" |
| 最小 scope | 凭证 scope 严格按本任务需要发放，不超额 |
| 跨域可控 | 跨域调用走 delegation chain，scope 单向收紧，可中途 revoke |
| TEE 不可绕 | 所有私钥不出 TEE；Normal World 只见 bytes |
| KMSS 直接用 | 不再自定义 KMS 抽象层，复用 KMSS lib API |

---

## 2. 为什么不能一个 TTL 走天下

车端任务时长跨度极大：

```
30 ms ─ 单次 LLM 推理 ─────────────┐
5 s   ─ 单次 tool 调用 ────────────┤  短任务：TTL 应秒级
30 s  ─ 多步规划一轮 ──────────────┘

15 min ─ 多轮对话会话 ────────────────  中任务：TTL 应分钟级

3 h   ─ 跨城行程规划 ─────────────────┐
8 h   ─ 长途自驾 OTA 协调 ────────────┤  长任务：TTL 应任务级
                                       │  且必须可中途收紧 / revoke

24 h  ─ 后台异常监控 ────────────────── 持续任务：scope 应极小
```

单一 TTL 会导致：
- **短 TTL + 长任务** → 频繁续期，KMSS 成为热点；网络/进程切换时易失败
- **长 TTL + 短任务** → 凭证爆炸半径过大；泄露后等不到自然过期

正确做法：**任务分级 + 分层 TTL**。

---

## 3. 任务分级

| 类型 | 典型场景 | 时长 | 主要风险 | Token 选择 |
|---|---|---|---|---|
| **短 (atomic)** | 单次 LLM 推理、单次 tool 调用、Guard.Check | 30ms–5s | 凭证泄露 | Task Token (L1) |
| **中 (session)** | 多轮对话、单次出行内的规划、多步工具编排 | 30s–15min | 会话劫持 | Session Token (L2) |
| **长 (lease)** | 跨城行程、OTA 下载、个性化模型更新 | 15min–数小时 | 长时泄露 | Lease Token (L3) |
| **持续 (persistent)** | 异常监控、车队同步、后台审计 | 数小时–数天 | 长期潜伏 | Persistent Token (L4) |

demo 阶段：实现 L0 / L1 / L2 / L3；L4 不做。

---

## 4. 分层 TTL 模型

```
┌──────────────────────────────────────────────────────────────────┐
│ Layer 4 │ Persistent Token │ TTL 24h │ scope=read:metrics only  │
│         │ (后台守护)        │ silent  │ (demo skip)              │
│         │                  │ refresh │                          │
├─────────┼──────────────────┼─────────┼──────────────────────────┤
│ Layer 3 │ Lease Token      │ TTL 任务 │ 心跳续期               │
│         │ (长任务)         │ 匹配    │ KMSS 可中途收紧 scope   │
├─────────┼──────────────────┼─────────┼──────────────────────────┤
│ Layer 2 │ Session Token    │ TTL 15min│ silent renew at 75%    │
│         │ (中任务)         │         │                          │
├─────────┼──────────────────┼─────────┼──────────────────────────┤
│ Layer 1 │ Task Token       │ TTL 30s-5min│ 单次精确 scope       │
│         │ (短任务)         │         │                          │
├─────────┼──────────────────┼─────────┼──────────────────────────┤
│ Layer 0 │ Workload SVID    │ TTL 1h │ workload identity       │
│         │ (身份根)         │ TEE 内 │                          │
└─────────┴──────────────────┴─────────┴──────────────────────────┘
```

### 4.1 Layer 0 — Workload SVID

- **TTL**：1 小时（最长不超过整车单次启动时长）
- **存储**：TEE 内（KMSS 保护），Normal World 仅持有 handle
- **内容**：X.509-SVID 或 JWT，携带 `spiffe://oem.com/{domain}/{agent-name}/{instance}`
- **签发时机**：Agent / Sidecar 进程启动时调一次；运行中不更新，靠后续 layer 的 token 引用
- **失效**：TTL 到期或 `kmss_revoke(sub)`

### 4.2 Layer 1 — Task Token

- **TTL**：30s – 5min，按操作类型配置
- **存储**：Normal World 内存即可（短 TTL 减少泄露窗口）
- **scope**：单次操作的精确 scope，如 `["tool:camera.snapshot"]` 或 `["invoke:guard"]`
- **典型用法**：每次 `Guard.Check` 调用都带一个新的 task token
- **续期**：不续期，过期重发

### 4.3 Layer 2 — Session Token

- **TTL**：15min
- **存储**：Normal World 内存；进程退出即销毁
- **scope**：整个会话需要的 scope 集合
- **silent renew**：SDK 后台线程在 TTL 到 75%（11.25min）时自动调 KMSS 续期
- **续期失败**：进入 30s grace，grace 内继续有效；过期则 fail-closed

### 4.4 Layer 3 — Lease Token

- **TTL**：与任务预估时长匹配（15min ~ 数小时）
- **存储**：TEE handle + Normal World 副本（副本含 jti 便于审计）
- **scope**：初始 scope 大；运行中 KMSS 可收紧
- **续期**：必须周期性心跳（默认 60s / demo 30s）
- **revoke**：KMSS 可主动 revoke，无需等 TTL；用于异常检测
- **grace**：心跳失败不立刻杀，先等 30s 给 KMSS 重启

### 4.5 Layer 4 — Persistent Token（demo skip）

- **TTL**：24h
- **scope**：必须且只能 read 类（如 `read:metrics`）
- **refresh**：每小时一次
- **demo 不实现**

---

## 5. Token 格式与 Claims

demo 默认采用 **JWT**（JSON Web Token，HS256/RS256/ES256）。生产建议评估 CWT（CBOR Web Token，更省空间，适合车规）。

### 5.1 标准 Claims

```json
{
  "iss": "spiffe://oem.com/ad/kmss",
  "sub": "spiffe://oem.com/ad/perception/01",
  "aud": "spiffe://oem.com/ad/guard",
  "exp": 1734567890,
  "nbf": 1734564290,
  "iat": 1734564290,
  "jti": "0192f9b7-c3a4-7def-9b2e-aaaa",
  
  "scope": ["read:navi.route", "invoke:guard"],
  
  "task": {
    "type": "lease",
    "id": "trip-2025-12-19-001",
    "parent_jti": "0192f9b0-session-jti",
    "lease_heartbeat_ms": 60000,
    "lease_grace_ms": 30000
  },
  
  "km_attest": "<TEE evidence>",
  "x5c": ["..."]
}
```

### 5.2 关键字段说明

| 字段 | 作用 |
|---|---|
| `iss` | 签发者（KMSS），用于验签时定位公钥 |
| `sub` | Workload SVID，引用 L0 |
| `aud` | 接收者（目标 service），防误用 |
| `jti` | 唯一 ID，用于 revoke 和审计关联 |
| `scope` | 字符串数组，精细到 `verb:resource` 级别 |
| `task.type` | 标识 token 层级，便于 Sidecar 路由策略 |
| `task.parent_jti` | 链式可追溯：lease → session → svid |
| `task.lease_*` | 仅 lease 层有，描述心跳周期和 grace |
| `km_attest` | TEE 启动期证据（可选，但建议带） |
| `x5c` | 证书链，mTLS 路径时使用 |

### 5.3 scope 命名约定

```
<verb>:<resource>[:<sub-resource>]
```

| Verb | 资源类型 | 示例 |
|---|---|---|
| `read` | 查询类 | `read:navi.route`, `read:user.profile` |
| `write` | 修改类 | `write:user.preference` |
| `invoke` | 调用服务 | `invoke:guard`, `invoke:guard.cd` |
| `tool` | 调用工具 | `tool:camera.snapshot`, `tool:media.play` |
| `delegate` | 委托权限 | `delegate:ad.perception` |

**scope 跨域只减不增**；QM 域的 token 不能驱动 ASIL-D 动作。

---

## 6. KMSS lib API

```c
// kmss_agent.h —— SDK 和 Sidecar 都 link libkmss.so

// ===== Layer 0 =====
kmss_svid_t* kmss_issue_workload_svid(
    const char* workload_name,    // "ad/perception/01"
    uint32_t    ttl_seconds       // 3600
);

// ===== Layer 1 =====
kmss_token_t* kmss_issue_task_token(
    kmss_svid_t* parent,
    const char** scopes, size_t n,
    uint32_t ttl_seconds           // 30~300
);

// ===== Layer 2 =====
kmss_token_t* kmss_issue_session_token(
    kmss_svid_t* parent,
    const char** scopes, size_t n,
    uint32_t ttl_seconds           // 900
);

int kmss_renew_session_token(kmss_token_t** inout);  // silent renew

// ===== Layer 3 =====
kmss_lease_t* kmss_acquire_lease(
    kmss_svid_t* parent,
    const char* task_id,
    const char** scopes, size_t n,
    uint32_t ttl_seconds           // 与任务匹配
);

typedef struct {
    int        revoked;            // 1 = KMSS 主动吊销
    char**     new_scope;          // 收紧后的 scope
    size_t     n_scope;
    uint64_t   next_heartbeat_ms;
} kmss_lease_heartbeat_t;

kmss_lease_heartbeat_t kmss_heartbeat_lease(kmss_lease_t*);

void kmss_release_lease(kmss_lease_t*);

// ===== Layer 4 (demo skip) =====
// kmss_issue_persistent_token() — 不实现

// ===== 跨域 =====
kmss_delegation_t* kmss_delegate(
    kmss_svid_t* parent,
    const char* target_domain,     // "ad"
    const char* target_service,    // "perception"
    const char** scopes, size_t n,
    uint32_t ttl_seconds
);

int kmss_verify_delegation(
    kmss_delegation_t* token,
    const uint8_t* trust_bundle,
    size_t bundle_len,
    kmss_claims_t* out_claims
);

// ===== 验签 / 解析 =====
int kmss_verify_token(
    kmss_token_t* token,
    const uint8_t* trust_bundle,
    size_t bundle_len,
    kmss_claims_t* out_claims
);

// ===== 基础操作 =====
int kmss_sign(kmss_key_ref_t key, const uint8_t* digest, size_t dlen,
              uint8_t* sig, size_t* sig_len);
int kmss_verify(kmss_key_ref_t key, const uint8_t* digest, size_t dlen,
                const uint8_t* sig, size_t sig_len);

kmss_attestation_t* kmss_attest(const uint8_t* nonce, size_t nlen);

// ===== 吊销 =====
int kmss_revoke(const char* jti);  // 1s 内全网生效

// ===== 资源释放 =====
void kmss_free_svid(kmss_svid_t*);
void kmss_free_token(kmss_token_t*);
void kmss_free_lease(kmss_lease_t*);
void kmss_free_delegation(kmss_delegation_t*);
void kmss_free_attestation(kmss_attestation_t*);
void kmss_free_claims(kmss_claims_t*);
```

### 6.1 Trust Bundle 注入

- OTA 推到 `/etc/agent/bundles/{domain}.pb`
- Sidecar 启动时调 `kmss_set_trust_domain_bundle(domain, path)`（如果 KMSS 提供该 API）
- 否则由 SDK 自己 parse 后通过 `kmss_verify_token(token, bundle, ...)` 传入
- inotify 监听 bundle 文件变化触发 reload

---

## 7. 生命周期

### 7.1 签发 → 使用 → 销毁

```
Workload 启动
    └─→ kmss_issue_workload_svid() [L0, 1h]
            └─→ Session 建立
                    └─→ kmss_issue_session_token() [L2, 15min, silent renew]
                            ├─→ 每次 Guard.Check：kmss_issue_task_token() [L1, 30s]
                            └─→ 长任务：kmss_acquire_lease() [L3, 任务匹配]
                                    └─→ 每 60s: kmss_heartbeat_lease()
            └─→ 跨域：kmss_delegate() + gRPC over TCP mTLS
    └─→ 进程退出 / 异常：所有 token 随进程销毁（TEE handle 主动 revoke）
```

### 7.2 Silent Renew

SDK 启动后台线程：

```c
void* renew_thread(void* arg) {
    kmss_token_t** token = (kmss_token_t**)arg;
    while (running) {
        sleep_until(token->expires_at * 0.75);  // TTL 75% 时续期
        if (kmss_renew_session_token(token) != 0) {
            enter_grace(token, 30000);  // 30s grace
            sleep(30000);
            if (still_failing) {
                fail_closed("session renew failed");
                break;
            }
        }
    }
}
```

### 7.3 Revocation

- **被动失效**：TTL 到期
- **主动 revoke**：`kmss_revoke(jti)`，KMSS 推送 CRL/OCSP 给所有 Sidecar，< 1s 全网生效
- **紧急 revoke**：检测到 token 从两个不同 PID 出现，立刻 revoke 整个 workload SVID
- **lease 主动 revoke**：心跳时 KMSS 返回 `revoked=1`

---

## 8. 长任务 Lease 模式详解

### 8.1 为什么需要 Lease 而非 long-lived token

| 维度 | Long-lived Token | Lease Token |
|---|---|---|
| 泄露后 | 需等 TTL 到期（数小时） | KMSS 可主动 revoke（< 1s） |
| scope 调整 | 不可能 | 心跳时可收紧 |
| 异常响应 | 无 | KMSS 实时审计 + 干预 |
| 实现复杂度 | 简单 | 中等（需心跳） |

代价：每 60s 心跳一次（demo 30s），KMSS 负载略增。可接受。

### 8.2 Lease 状态机

```
              kmss_acquire_lease()
                       │
                       ▼
              ┌────────────────┐
              │   ACTIVE       │  ← 心跳成功，scope 未变
              └────────────────┘
                  │     │
       heartbeat  │     │ heartbeat resp
       OK + new   │     │ revoked=1
       scope      │     │
                  ▼     ▼
       ┌────────────────┐ ┌────────────────┐
       │ SCOPE_TIGHTENED│ │    REVOKED     │
       └────────────────┘ └────────────────┘
                                  │
                                  ▼
                          ┌────────────────┐
                          │  TASK_ABORT    │
                          └────────────────┘

任何状态在心跳失败时进入 GRACE（30s）：
       ┌────────────────┐
       │    GRACE       │  ← KMS 不可达，限时等待
       └────────────────┘
           │         │
   grace   │         │ grace 超时
   内恢复  │         │
           ▼         ▼
       ACTIVE    TASK_ABORT
```

### 8.3 KMSS 主动收紧 scope 示例

```json
// T+0：lease 申请
req:  scope = ["read:navi.local", "read:navi.highway", "read:user.profile"]
resp: scope = ["read:navi.local", "read:navi.highway", "read:user.profile"]

// T+15min：心跳（用户进入高速）
req:  heartbeat
resp: {
  "revoked": 0,
  "new_scope": ["read:navi.highway", "read:user.profile"],
  // read:navi.local 被 KMSS 评估为不再需要
  "reason": "context:highway_entered"
}

// T+30min：心跳（用户驶出高速）
resp: {
  "revoked": 0,
  "new_scope": ["read:navi.local", "read:user.profile"],
  "reason": "context:highway_exited"
}
```

### 8.4 心跳协议

```
Client → KMSS:  KMS.Heartbeat{lease_id, task_progress}
KMSS  → Client: KMS.HeartbeatResp{
                    revoked: bool,
                    new_scope?: string[],
                    next_heartbeat_ms: int,
                    reason: string
                }
```

`task_progress` 是可选字段，用于 KMSS 决策（如 "已加载 60% 数据" → 可以延长 TTL）。

---

## 9. 跨域 Token 链

### 9.1 链式结构

```
CD Agent 任务链：

L0: spiffe://oem.com/cd/voice/01            (SVID, 1h)
    │
    ├─ L2: session token
    │     scope=["invoke:guard.cd"], ttl=15min, silent renew
    │     │
    │     └─ L1: task token (每次 Guard.Check)
    │           scope=["invoke:guard.cd"], ttl=30s
    │
    └─ L3: lease for "trip-plan"
          scope=["read:navi.*", "read:user.profile"], ttl=1800
          │
          └─ Delegation to AD (kmss_delegate)
                scope=["read:navi.route"]              ← step-down
                ttl=1800 (≤ parent lease)
                aud="spiffe://oem.com/ad/guard"
                │
                └─ L1: task token to AD Guard (单次调用)
                      scope=["invoke:guard.ad"], ttl=30s
```

### 9.2 不变量（必须由 SDK 保证）

| 不变量 | 说明 |
|---|---|
| `child_ttl ≤ parent_ttl` | 子凭证不能比父凭证活更久 |
| `child_scope ⊆ parent_scope` | 子凭证 scope 是父的子集 |
| `child.task.parent_jti = parent.jti` | 链式可审计 |
| `child.aud ∈ parent.scope` | 接收方必须在父 scope 范围内 |
| 跨域 step-down | QM scope 不能产生 ASIL-D scope |

### 9.3 跨域调用全流程（CD Agent → AD Guard）

```
1. CD SDK 启动期
   kmss_svid_t* me = kmss_issue_workload_svid("cd/voice/01", 3600);

2. CD SDK 想跨域调 AD
   const char* scopes[] = {"read:navi.route"};
   kmss_delegation_t* tok = kmss_delegate(me, "ad", "perception",
                                          scopes, 1, 600);
   // KMSS 内部用 CD 域密钥签 step-down token

3. CD SDK → AD Guard（gRPC over TCP，mTLS）
   metadata:
     x-svid:       <CD Agent SVID 证书>
     x-delegation: <serialized DelegationToken>
     x-target:     "ad/guard"

4. AD Guard Sidecar 收到
   kmss_claims_t claims;
   if (kmss_verify_delegation(tok, ad_trust_bundle, ...) != 0) abort;
   // 检查 claims.scope、ttl、parent_jti

5. AD Guard 跑推理，返回 GuardDecision

6. CD SDK 清理
   kmss_free_delegation(tok);
```

---

## 10. 故障处理矩阵

| 故障 | 短任务 (L1) | 中任务 (L2) | 长任务 (L3) |
|---|---|---|---|
| KMSS 临时不可达 | 用缓存 SVID 验签；新 token 申请失败 → fail-closed | silent renew 失败 → grace 30s → fail-closed | 心跳失败 → grace 30s → lease 自动 revoke |
| KMSS 永久丢失 | 全任务 fail-closed | 全任务 fail-closed | 全任务 fail-closed |
| Token 泄露 | `kmss_revoke(jti)` 立刻失效 | 同左 | 同左，且 lease 可被远端 revoke |
| Sidecar 时钟漂移 | `exp/nbf` 拒绝 | 同左 | 同左 |
| 跨域时钟不同步 | 用车内 PTP 时戳 | 同左 | 同左 |
| 任务超过预期 | 重发新 task token | silent renew 自动延长 | 80% TTL 时主动续租，scope 重评估 |
| 任务异常中止 | token 自然过期 | 显式 revoke + kmss_free | kmss_release_lease |

> **故障场景的详细时序演练 (KMSS 崩溃/网络分区/TEE 故障/Clock Skew/OTA 回滚) 见 [detailed_architecture.md §D](/security/llm_agent_defense/detailed_architecture)。**

---

## 11. Demo 范围

### 11.1 必须实现

| 模块 | 说明 |
|---|---|
| KMSS lib 接口 | `issue_workload_svid` / `issue_task_token` / `issue_session_token` / `acquire_lease` / `heartbeat_lease` / `release_lease` / `delegate` / `verify_delegation` / `revoke` |
| SoftHSM2 后端 | demo 阶段 KMSS 用 SoftHSM2 模拟 TEE |
| Trust bundle OTA | 文件系统推送 |
| Guard gRPC | 携带 token 在 metadata |
| Audit | 每个 token 操作写一行 |

### 11.2 demo 默认决策

| 项 | 默认值 | 理由 |
|---|---|---|
| Token 格式 | JWT (RS256) | demo 最简单 |
| Refresh 策略 | SDK silent renew | 默认方案，无需 KMSS 推 |
| Lease 心跳间隔 | 30s | demo 快速验证 revocation |
| 跨域 token | 复用 JWT（X.509-SVID 备选） | 统一 payload，便于调试 |
| Persistent Token | 不实现 | demo 跑不到数小时 |
| TEE 抽象 | SoftHSM2 + PKCS#11 | 不接真硬件 |

### 11.3 demo 跑通标准

1. **3 域起来**：AD/CD/VD 三组进程通过 KMSS 拿到各自 SVID
2. **同域 call**：CD Agent → CD Guard 走通，带 task token
3. **跨域 call**：CD Agent → AD Guard 走通，带 delegation token
4. **跨域拒绝**：CD Agent 申请 `tool:control.brake`（ASIL-D）→ KMSS 拒绝 delegation
5. **Lease revoke**：AD Agent 申请 lease → 模拟 KMSS revoke → 30s 内 task 终止

---

## 12. 落地清单

### 12.1 KMSS lib 扩展接口（需 KMSS 团队配合）

- [ ] `kmss_issue_task_token()`
- [ ] `kmss_issue_session_token()` + `kmss_renew_session_token()`
- [ ] `kmss_acquire_lease()` + `kmss_heartbeat_lease()` + `kmss_release_lease()`
- [ ] `kmss_delegate()` + `kmss_verify_delegation()`
- [ ] `kmss_revoke()` + CRL 推送机制
- [ ] `kmss_set_trust_domain_bundle()` 或 SDK 端 parse 接口

### 12.2 SDK 端

- [ ] 4 层 token 缓存与生命周期管理
- [ ] 后台 silent renew 线程
- [ ] Lease 心跳协程
- [ ] 跨域 delegation chain 构造器
- [ ] 不变量检查：`child ⊆ parent`

### 12.3 Sidecar 端

- [ ] Token 验签（接收 task token / delegation token）
- [ ] Trust bundle 加载与热更新
- [ ] Revocation list 缓存与刷新
- [ ] 审计写入

### 12.4 OTA 工具

- [ ] Bundle 打包脚本（含签名）
- [ ] Bundle 版本管理
- [ ] 回滚机制

---

## 13. 参考资料

- [SPIFFE / SPIRE](https://spiffe.io/) — 工作负载身份标准
- [SPIFFE Federation Spec](https://spiffe.io/docs/latest/spiffe-specs/spiffe_federation/) — 跨域信任
- [OAuth 2.0 Token Exchange (RFC 8693)](https://datatracker.ietf.org/doc/rfc8693/) — delegation token 灵感
- [JSON Web Token (RFC 7519)](https://datatracker.ietf.org/doc/rfc7519/) — 当前 token 格式
- [CWT (RFC 8392)](https://datatracker.ietf.org/doc/rfc8392/) — 车规备选格式
- [NIST SP 800-204D](https://csrc.nist.gov/pubs/sp/800/204/d/final) — Service Mesh Security
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [车端 KMSS 内部规范] — KMSS 团队提供的 lib 文档与 header
---

## 14. 凭据管理（Credential Management）

### 14.1 范围

车端凭据管理覆盖：

| 类型 | 例子 | 存储 |
|---|---|---|
| 工作负载密钥对 | workload leaf key (L2) | TEE 内 |
| 中间证书密钥 | domain intermediate (L1) | TEE 安全文件 |
| OEM 根密钥 | OEM root (L0) | TEE eFuse |
| Trust Bundle | 远域公钥 + 证书链 + CRL | OTA 推送 |
| Wrapped Secret | DB 密码、API token、PII | KMSS envelope 加密 |
| 模型签名 | OTA bundle 内模型 DLC | KMSS 验签 |

### 14.2 密钥分层（信任链金字塔）

```
┌─────────────────────────────────────────────────────────────┐
│ L0 │ OEM Root Key                                           │
│   │ • 产线烧入 TEE eFuse / HSM，永不导出                    │
│   │ • TTL = 整车生命周期（10+ 年）                          │
│   │ • 用途：签发 L1 中间证书、跨域 trust anchor            │
│   │ • 数量：1 个域 1 根（多备份到不同 SoC 的 TEE）         │
├─────────────────────────────────────────────────────────────┤
│ L1 │ Domain Intermediate Key                                │
│   │ • OTA 注入，可轮换                                     │
│   │ • TTL = 1~3 年                                         │
│   │ • 用途：签发 L2 workload 证书、签发 trust bundle       │
│   │ • 数量：每域 1~2 个（主 + 备份）                       │
├─────────────────────────────────────────────────────────────┤
│ L2 │ Workload Leaf Key                                      │
│   │ • KMSS 在 TEE 内动态生成                               │
│   │ • TTL = 1h（与 SVID 一致）                             │
│   │ • 用途：签 task / session / lease token                │
│   │ • 数量：每 workload 一个私钥                           │
├─────────────────────────────────────────────────────────────┤
│ L3 │ Ephemeral Session Key                                  │
│   │ • KMSS 在 TEE 内临时生成                               │
│   │ • TTL = 与上层 token 一致                              │
│   │ • 用途：会话内对称加密（可选）                         │
│   │ • 数量：每个 session 一个                              │
└─────────────────────────────────────────────────────────────┘
```

**不变量**：
- L0 / L1 私钥**任何情况都不出 TEE**（包括 OEM 远程更新）
- L2 / L3 私钥仅在 TEE 内可见，Normal World 只拿到 handle / 签名结果
- 上层 key 的合法性由下层 key 的签名链证明

### 14.3 密钥生命周期

```
生成 ───→ 存储 ───→ 分发 ───→ 使用 ───→ 轮换 ───→ 销毁
 │         │         │         │         │         │
 ▼         ▼         ▼         ▼         ▼         ▼
TEE 内   TEE 安全  证书/TKB  sign/    自动/    自然过期
eFuse    文件     文件     verify    手动    + 主动
生成              OTA                    OTA      revoke
```

#### 14.3.1 生成

| 层 | 方式 | 时机 |
|---|---|---|
| L0 | 产线烧入 | 一次性，激活时远程注入备份 |
| L1 | OTA bundle 携带，或 TEE 内从 L0 派生 | 整车激活 / 轮换时 |
| L2 | KMSS `kmss_generate_key(workload_id)` | 进程启动 / 周期重生成 |
| L3 | KMSS `kmss_derive_key(parent_l2, session_id)` | session 创建时 |

#### 14.3.2 存储

| 层 | 存储位置 | 备份 |
|---|---|---|
| L0 | TEE eFuse + 安全 flash mirror | OEM 安全设施远程备份 |
| L1 | TEE 安全文件 `/var/lib/kmss/keys/` | OTA bundle 自身即备份 |
| L2 | TEE 内存（运行时）+ 派生参数持久化 | 重启后从 L1 + workload_id 派生 |
| L3 | TEE 内存 | 不持久化 |

#### 14.3.3 分发

- **同域**：无需分发，Sidecar / Agent 直接调 KMSS 取公钥
- **跨域**：通过 **Trust Bundle**（见 §14.4）

#### 14.3.4 使用

所有密钥操作通过 KMSS lib，Normal World 永远拿不到私钥明文，只能拿 `key_ref_t` handle：

```c
kmss_sign(key_ref, digest)            // 签名
kmss_verify(key_ref, digest, sig)     // 验签
kmss_decrypt(key_ref, ciphertext)     // 解密（envelope）
kmss_derive_child_key(parent, child_id)
```

#### 14.3.5 轮换

| 层 | 触发 | 方式 | 协调 |
|---|---|---|---|
| L0 | OEM 召回 / 安全事件 | 整车返厂 | OEM 全网通知 |
| L1 | 例行 1~3 年 / 安全事件 | OTA bundle 更新 | 双 key overlap 30 天 |
| L2 | TTL 到期 / 重启 | 自动重生成 | 无需协调 |
| L3 | session 结束 | 自动销毁 | 无需协调 |

**L1 双 key overlap 流程**：
- T-30d：OTA 推新 L1 key（标记 `active`）
- T+0：新 key 开始签发；旧 key 仍可验签
- T+30d：旧 key 标记 `inactive`，仅验签历史 token
- T+90d：旧 key 完全销毁

#### 14.3.6 销毁

- **自然过期**：TTL 到期后 key 自动从 TEE 内存擦除
- **主动 revoke**：`kmss_revoke_key(key_ref)`，立刻擦除 + 广播 CRL
- **TEE 物理销毁**：仅 L0 可触发（如整车报废），需 OEM 远程签名指令

### 14.4 Trust Bundle

每个域 Sidecar 持有**远域的 trust bundle**：

```
/etc/agent/bundles/
  ├── ad.pb           # AD 域的 L0 + L1 + CRL
  ├── cd.pb           # CD 域的 L0 + L1 + CRL
  └── vd.pb           # VD 域的 L0 + L1 + CRL
```

Protobuf 定义：

```proto
message TrustBundle {
  string domain = 1;
  bytes  root_cert_der = 2;                  // L0
  repeated bytes intermediate_certs_der = 3; // L1 list
  bytes  crl_der = 4;
  uint64 not_after = 5;
  bytes  signature = 6;                       // 用 L0 私钥签
}

message BundleManifest {
  string version = 1;
  repeated TrustBundle bundles = 2;
  uint64 created_at = 3;
}
```

OTA 推送 + 签名校验流程：
1. Sidecar 启动时读 `/etc/agent/bundles/*.pb`
2. 用内置 OEM root（每个域 Sidecar 内嵌一份备份）验签 bundle
3. inotify 监听 bundle 目录，变化时自动 reload
4. reload 时不中断当前请求，老 key 缓存做兜底

### 14.5 证书吊销（CRL + Push）

```
CRL 生成（KMSS）：
  - 触发：kmss_revoke(jti) / kmss_revoke_key()
  - 内容：被吊销的 cert serial + key id + 原因 + 时间
  - 推送：KMSS → 所有 Sidecar（gRPC stream）

Sidecar 验证流程：
  1. 验签 token 链
  2. 检查 cert serial 不在本地 CRL 缓存
  3. 检查 CRL 缓存新鲜度（< 5min，否则后台刷新）
  4. 全部通过 → 接受
```

**紧急 revoke 延迟预算**：

```
T+0.0s  KMSS 收到 kmss_revoke(jti)
T+0.1s  KMSS 更新 CRL，加入该 jti
T+0.2s  KMSS 向所有 Sidecar push revocation_event
T+0.5s  Sidecar 更新本地 CRL，拒绝该 token
T+1.0s  全网生效（< 1s SLA）
```

### 14.6 Wrapped Secret（业务凭据）

车端除密钥外还有大量业务凭据需要保护：

| Secret 类型 | 例子 | 存储方案 |
|---|---|---|
| 服务端 TLS 私钥 | Sidecar mTLS | KMSS (L2) |
| 数据库密码 | 车内诊断 DB | KMSS wrapped secret |
| API token | 高精地图服务 | KMSS wrapped secret + 短期 |
| 用户 PII | 驾驶偏好、人脸 ID | KMSS wrapped + 应用层加密 |
| 模型签名 | OTA 模型 DLC | KMSS 验签 |

KMSS wrapped secret API：

```c
int kmss_secret_put(const char* name,
                    const uint8_t* plaintext, size_t plen,
                    kmss_secret_ref_t* out);

int kmss_secret_get(kmss_secret_ref_t ref,
                    uint8_t* plaintext, size_t* plen);

int kmss_secret_rotate(kmss_secret_ref_t ref);  // L1 轮换时重 wrap
int kmss_secret_delete(kmss_secret_ref_t ref);
```

存储路径：`/var/lib/kmss/secrets/{name}.enc`（envelope 加密，L1 key wrap）。

### 14.7 凭据 ↔ Token 关系

```
         ┌──────────────────────────────┐
         │  Workload Leaf Key (L2)      │
         │  • 私钥在 TEE 永不出          │
         │  • 公钥 + 证书 = SVID        │
         └──────────┬───────────────────┘
                    │ KMSS 用 L2 私钥签
                    ▼
         ┌──────────────────────────────┐
         │  Token (JWT / CWT-SVID)      │
         │  • payload = claims          │
         │  • signature = KMSS 签       │
         │  • TTL = 30s~数小时          │
         └──────────┬───────────────────┘
                    │ 验证：验签 + CRL + bundle
                    ▼
         ┌──────────────────────────────┐
         │  Sidecar / 远域 Sidecar      │
         │  用远域 bundle 公钥验签      │
         └──────────────────────────────┘
```

关键点：
- Token 是**短期使用凭据**（高频更换）
- 底层密钥是**长期身份凭据**（低频轮换）
- 验签时不需要 KMSS 在线（用 bundle 公钥）
- 但**吊销**需要 KMSS 在线（push CRL）

### 14.8 KMSS lib API 补充（凭据管理）

```c
// ===== 密钥生命周期 =====

kmss_key_ref_t kmss_generate_key(const char* key_id, kmss_key_algo_t algo);
kmss_key_ref_t kmss_derive_key(kmss_key_ref_t parent, const char* child_id);

int kmss_list_keys(kmss_key_info_t** out, size_t* n);
int kmss_get_key_info(kmss_key_ref_t, kmss_key_info_t* out);

int kmss_rotate_key(const char* key_id);  // 自动双 key overlap
int kmss_revoke_key(kmss_key_ref_t);
int kmss_destroy_key(kmss_key_ref_t);

// ===== 证书 =====

kmss_cert_t* kmss_issue_certificate(
    kmss_key_ref_t subject_key,
    const char* spiffe_id,
    uint32_t ttl_seconds,
    const kmss_san_t* sans, size_t n_san);

int kmss_verify_certificate(
    kmss_cert_t* cert,
    const uint8_t* trust_bundle, size_t bundle_len,
    uint32_t* out_expires_in_seconds);

// ===== Trust Bundle =====

int kmss_load_trust_bundle(const char* domain,
                           const uint8_t* pb, size_t len);
int kmss_get_trust_bundle(const char* domain,
                          uint8_t** pb, size_t* len);
int kmss_refresh_trust_bundles();

// ===== CRL =====

int kmss_get_crl(const char* domain, uint8_t** der, size_t* len);
int kmss_is_revoked(const char* serial_or_jti);

// ===== Wrapped Secret =====

int kmss_secret_put(const char* name,
                    const uint8_t* pt, size_t plen,
                    kmss_secret_ref_t* out);
int kmss_secret_get(kmss_secret_ref_t ref,
                    uint8_t* pt, size_t* plen);
int kmss_secret_rotate(kmss_secret_ref_t ref);
int kmss_secret_delete(kmss_secret_ref_t ref);

// ===== 备份 / 恢复（OEM 工具） =====

int kmss_export_domain_public_keys(const char* domain,
                                   uint8_t** out, size_t* len);
// 注意：只导出公钥，私钥永不导出
```

### 14.9 故障恢复矩阵

| 故障 | 影响 | 恢复 |
|---|---|---|
| **L0 损坏**（TEE 物理故障） | 该域所有密钥失效 | 整车返厂，从 OEM 备份重新注入 L0；其他域不受影响 |
| **L1 损坏** | 该 workload 无法签发新 token；旧 token 仍可验签到旧 L1 | OTA 重推 L1 bundle；Sidecar 自动切换 |
| **L2 自然过期** | 该 workload SVID 失效 | KMSS 自动重新 `generate + issue`，对应用透明 |
| **Trust Bundle 损坏** | 跨域调用失败 | Sidecar 从本地备份 `/var/lib/agent/bundles/*.bak` 加载；OTA 重推 |
| **KMSS daemon 挂** | 短期：缓存 SVID 继续工作；长期：grace 后 fail-closed | systemd 自动拉起；如起不来，降级模式 |
| **OTA bundle 损坏** | 启动失败 | 回滚到上一个已知 good bundle |
| **CRL 推送失败** | revoke 不及时 | 30s 后 Sidecar 主动 poll CRL；最长延迟 5min |

### 14.10 demo 范围补充

| 模块 | demo 是否实现 |
|---|---|
| L0 OEM root | SoftHSM2 模拟（启动时生成） |
| L1 intermediate | demo 启动时 KMSS 自动生成 |
| L2 workload | KMSS `generate_key` 演示 |
| L3 ephemeral | 不实现（demo 用 JWT 内置签） |
| X.509-SVID | demo 跳过，全部用 JWT |
| Trust Bundle OTA | ✅ 文件系统推送 |
| CRL push | ✅ Sidecar 内存更新 |
| Wrapped Secret | ✅ 至少演示一个 secret put/get |
| Key rotation | ✅ 手动 trigger + 自动 expire |

### 14.11 demo 跑通标准补充

1. KMSS 启动时生成 L0 / L1 / L2 全套
2. 应用通过 `kmss_secret_put/get` 写入读取 secret
3. Trust Bundle OTA 推送后 Sidecar 自动 reload
4. 手动 revoke 一个 jti，1s 内被远域 Sidecar 拒绝
5. 手动 rotate L1，旧 token 仍能验签，新 token 用新 key 签

### 14.12 落地清单补充

KMSS 团队：
- [ ] 实现 `kmss_generate_key` / `kmss_derive_key` / `kmss_revoke_key` / `kmss_rotate_key`
- [ ] 实现 `kmss_issue_certificate` / `kmss_verify_certificate`
- [ ] 实现 `kmss_load_trust_bundle` / `kmss_get_crl`
- [ ] 实现 `kmss_secret_put/get/rotate/delete`
- [ ] CRL push gRPC stream 服务
- [ ] L1 重 wrap 工具（OTA 轮换）

OTA 工具：
- [ ] Bundle 打包脚本（含 manifest、签名）
- [ ] Bundle 版本管理与回滚
- [ ] 单域 / 全量推送模式

Sidecar 端：
- [ ] Bundle 文件 inotify 监听
- [ ] CRL 内存缓存 + 5min 主动刷新
- [ ] 验签路径集成 `kmss_verify_certificate`

---

## 15. 整体架构

### 15.1 三视图

```
┌───────────────────── 横向：3 域 × 3 模块 ─────────────────────┐
│                                                              │
│            AD Domain          CD Domain          VD Domain   │
│         ┌──────────┐       ┌──────────┐       ┌──────────┐  │
│ Identity│ SVID 签发 │       │ SVID 签发 │       │ SVID 签发 │  │
│         │ KMSS L0/L1│       │ KMSS L0/L1│       │ KMSS L0/L1│  │
│         └──────────┘       └──────────┘       └──────────┘  │
│                                                              │
│  Auth   │ Token 4 层  │     │ Token 4 层  │     │ Token 4 层  │
│         │ silent      │     │ silent      │     │ silent      │
│         │ renew       │     │ renew       │     │ renew       │
│         └──────────┘       └──────────┘       └──────────┘  │
│                                                              │
│ Cred    │ Trust Bundle│     │ Trust Bundle│     │ Trust Bundle│
│         │ CRL + Secret│     │ CRL + Secret│     │ CRL + Secret│
│         └──────────┘       └──────────┘       └──────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌─────────────── 纵向：TEE / Normal World 分层 ───────────────┐
│                                                              │
│  TEE (TrustZone)         ───── KMSS daemon (libkmss.so) ───│
│  • L0 OEM root                                                │
│  • L1 domain intermediate                                    │
│  • L2 workload leaf (临时)                                    │
│  • All crypto operations                                      │
│  Normal World                                                 │
│  • Agent / SDK       (gRPC client)                            │
│  • Guard Sidecar     (gRPC server, UDS + TCP)                │
│  • KMSS lib client   (link libkmss.so, UDS to daemon)       │
└──────────────────────────────────────────────────────────────┘

┌───────────────── 跨域：Trust Federation ─────────────────────┐
│                                                              │
│   AD ◀──── delegation token (mTLS over gRPC) ────▶ CD         │
│   AD ◀──── delegation token ──────────────────▶ VD            │
│   CD ◀──── delegation token ──────────────────▶ VD            │
│                                                              │
│   全部通过 Trust Bundle 验签；scope 跨域只减不增              │
└──────────────────────────────────────────────────────────────┘
```

### 15.2 数据流（一次跨域 Guard 调用全流程）

```
CD Agent                  CD SDK              CD KMSS (TEE)        CD Sidecar              AD KMSS (TEE)            AD Sidecar              AD 模型
   │                         │                     │                   │                       │                       │                      │
   │ 1. 启动: kmss_issue_workload_svid("cd/voice/01") ─────────────────▶│                       │                       │                      │
   │                         │                     │ gen L2 key        │                       │                       │                      │
   │                         │                     │ sign SVID         │                       │                       │                      │
   │                         │◀────── SVID + handle ──────────────── │                       │                       │                      │
   │                         │ cache in TEE        │                   │                       │                       │                      │
   │                         │                     │                   │                       │                       │                      │
   │ 2. 用户说"导航到西湖"   │                     │                   │                       │                       │                      │
   │   ┌────────────────────▶│                     │                   │                       │                       │                      │
   │   │ Guard.Check         │                     │                   │                       │                       │                      │
   │   │ {payload}           │                     │                   │                       │                       │                      │
   │                         │                     │                   │                       │                       │                      │
   │                         │ 3. issue task token │                   │                       │                       │                      │
   │                         │ kmss_issue_task_token(scopes=["invoke:guard.cd"]) ──▶│        │                       │                      │
   │                         │                     │ sign JWT          │                       │                       │                      │
   │                         │◀────── task JWT ────────────────────── │                       │                       │                      │
   │                         │                     │                   │                       │                       │                      │
   │                         │ 4. local Guard.Check (gRPC UDS) ────▶│                       │                       │                      │
   │                         │                     │                   │ verify task JWT       │                       │                      │
   │                         │                     │                   │ + run rules + OPA     │                       │                      │
   │                         │                     │                   │ + QNN NSFA-Cabin      │                       │                      │
   │                         │◀────── GuardDecision{ALLOW} ──────────│                       │                       │                      │
   │                         │                     │                   │                       │                       │                      │
   │                         │ 5. 想跨域调 AD 导航 │                   │                       │                       │                      │
   │                         │ kmss_delegate(parent=SVID, target_domain="ad",                       │                       │                      │
   │                         │                  scopes=["read:navi.route"], ttl=600) ──▶│        │                       │                      │
   │                         │                     │ sign delegation   │                       │                       │                      │
   │                         │◀────── delegation ─────────────────────│                       │                       │                      │
   │                         │                     │                   │                       │                       │                      │
   │                         │ 6. issue new task token (scope=invoke:guard.ad) ──▶│            │                       │                      │
   │                         │                     │ sign              │                       │                       │                      │
   │                         │◀────── task JWT ────────────────────── │                       │                       │                      │
   │                         │                     │                   │                       │                       │                      │
   │                         │ 7. Guard.Check (gRPC TCP mTLS) ─────────────────────────────────────────────────────▶│                      │
   │                         │                     │                   │                       │                       │ verify delegation    │
   │                         │                     │                   │                       │                       │ + run AD rules/NSFA  │
   │                         │                     │                   │                       │                       │ + return decision    │
   │                         │◀────────────── GuardDecision ───────────────────────────────────────────────────────│                      │
   │                         │                     │                   │                       │                       │                      │
   │ 8. 最终结果              │                     │                   │                       │                       │                      │
   │◀────── 决策 + 上下文 ────│                     │                   │                       │                       │                      │
   │                         │                     │                   │                       │                       │                      │
   │                         │ 9. cleanup          │                   │                       │                       │                      │
   │                         │ kmss_free_*         │                   │                       │                       │                      │
```

### 15.3 信任边界

```
┌────────────────────────────────────────────────────────────────────┐
│  Trust Boundary 1: TEE vs Normal World                            │
│  • L0/L1 私钥、KMSS 内部状态不出 TEE                               │
│  • Normal World 仅持有 handle / 签名结果                          │
├────────────────────────────────────────────────────────────────────┤
│  Trust Boundary 2: 域内 vs 跨域                                   │
│  • 同域调用：trust 由本域 L0 担保                                  │
│  • 跨域调用：trust 由远域 trust bundle + 当前 delegation 共同担保  │
├────────────────────────────────────────────────────────────────────┤
│  Trust Boundary 3: 应用 vs IAM 系统                               │
│  • 应用不能直接读私钥，只能调 KMSS API                             │
│  • 应用不能绕过 KMSS 自己签 token                                  │
├────────────────────────────────────────────────────────────────────┤
│  Trust Boundary 4: ASIL 等级                                      │
│  • QM scope 不能驱动 ASIL-D 动作                                   │
│  • 策略写在 KMSS 委托链配置中，不可被应用层修改                    │
└────────────────────────────────────────────────────────────────────┘
```

### 15.4 跨域数据流总览

```
                AD 域                                    CD 域
  ┌─────────────────────────────┐         ┌─────────────────────────────┐
  │ TEE                          │         │ TEE                          │
  │  KMSS daemon (ad)            │         │  KMSS daemon (cd)            │
  │   ├─ L0 root (ad)            │         │   ├─ L0 root (cd)            │
  │   ├─ L1 int (ad)             │         │   ├─ L1 int (cd)             │
  │   └─ CRL publisher ──────┐   │         │   └─ CRL publisher ──┐       │
  │                          │   │         │                       │      │
  │ Normal World            │   │         │ Normal World          │      │
  │  AD Agent + SDK         │   │         │  CD Agent + SDK       │      │
  │  AD Sidecar ◀───────────┘   │         │  CD Sidecar ◀─────────┘      │
  │   • verify cd token         │         │   • verify ad token          │
  │   • local rules + NSFA-RT   │         │   • local rules + NSFA-Cabin │
  └────────────┬────────────────┘         └────────────┬────────────────┘
               │                                       │
               │  ◀───── trust bundle (cd.pb) ──────   │
               │  ────── trust bundle (ad.pb) ─────▶  │
               │                                       │
               │  ◀── delegation token + mTLS gRPC ──▶ │
               │                                       │
```

---

## 16. 各模块架构与接口（输入/输出）

### 16.1 模块总览

| 模块 | 核心职责 | 主要存储 | 主要交互对象 |
|---|---|---|---|
| **身份 (Identity)** | 给 workload 分配全局唯一 SPIFFE ID，签发 SVID | TEE 内 L0/L1 密钥、SVID cache | KMSS daemon |
| **认证 (Authentication)** | 签发/验签 4 层 token，跨域 delegation，session/lease 续期 | Normal World token cache、TEE session key | KMSS lib、Guard Sidecar |
| **凭据管理 (Credential)** | 密钥生成/轮换/销毁、Trust Bundle 分发、CRL 推送、Wrapped Secret | TEE 安全存储、/etc/agent/bundles、/var/lib/kmss/secrets | KMSS daemon、OTA、Sidecar |

### 16.2 身份模块（Identity）

#### 边界

```
   ┌──────────────── Identity 边界 ────────────────┐
   │                                                │
   │   输入                       输出              │
   │  ─────                      ─────              │
   │  workload metadata    →     SPIFFE ID          │
   │  instance info        →     Workload SVID      │
   │  attestation nonce    →     AttestationEvidence│
   │                                                │
   │   内部组件                                      │
   │  ─────────                                     │
   │  • SPIFFE ID Registry (内存)                   │
   │  • KMSS SVID Issuer (调 KMS lib)               │
   │  • Attestation Verifier (调 KMSS lib)          │
   │                                                │
   └────────────────────────────────────────────────┘
```

#### 输入

| 输入 | 数据形态 | 来源 |
|---|---|---|
| `workload_metadata` | `{domain, agent_name, instance_id, binary_hash, pid}` | 应用启动时 |
| `attestation_challenge` | `bytes<32>` | 远端 Sidecar（启动期） |
| `km_attest_request` | `{nonce, expected_measurement}` | 自检 / 调试 |

#### 输出

| 输出 | 数据形态 | 消费者 |
|---|---|---|
| `SPIFFE ID` | `spiffe://oem.com/{domain}/{name}/{id}` | 所有 token 的 `sub` 字段 |
| `Workload SVID` | `{spiffe_id, cert_der, private_key_handle, expires_at}` | 认证模块缓存 |
| `Attestation Evidence` | `{tcb_measurement, signature, cert_chain}` | 远端 Sidecar |

#### 关键 API（KMSS lib）

```c
kmss_svid_t* kmss_issue_workload_svid(
    const char* workload_name,
    uint32_t    ttl_seconds);

kmss_attestation_t* kmss_attest(
    const uint8_t* nonce, size_t nlen);

int kmss_verify_attestation(
    kmss_attestation_t* evidence,
    const uint8_t* expected_measurement,
    size_t mlen);
```

#### 不变量

- SPIFFE ID 全局唯一，命名空间 `spiffe://oem.com/{domain}/{name}/{instance}`
- SVID 私钥永不出 TEE
- SVID TTL ≤ L1 intermediate key 剩余 TTL

#### 故障模式

| 故障 | 行为 |
|---|---|
| KMSS daemon 不可达 | SVID 申请失败，进程退出 fail-closed |
| SPIFFE ID 冲突 | KMSS 拒绝，返回 `EADDRINUSE` |
| L0 / L1 失效 | KMSS 拒绝签发新 SVID；已签发的不受影响 |

### 16.3 认证模块（Authentication）

#### 边界

```
   ┌────────────── Authentication 边界 ──────────────┐
   │                                                  │
   │   输入                          输出             │
   │  ─────                         ─────             │
   │  parent SVID           →       Task Token        │
   │  parent SVID + scopes  →       Session Token     │
   │  parent SVID + task_id →       Lease + Token     │
   │  heartbeat             →       Lease 更新结果    │
   │  token + trust_bundle  →       claims + 验签结果 │
   │  parent SVID + 远域    →       Delegation Token  │
   │                                                  │
   │   内部组件                                        │
   │  ─────────                                       │
   │  • Token Cache (Normal World)                    │
   │  • Silent Renew Thread (per session)             │
   │  • Lease Heartbeat Coroutine (per lease)         │
   │  • Scope Invariant Checker (child ⊆ parent)      │
   │                                                  │
   └──────────────────────────────────────────────────┘
```

#### 输入

| 输入 | 数据形态 | 来源 |
|---|---|---|
| `parent_svid` | `kmss_svid_t*` | 身份模块缓存 |
| `scopes[]` | `const char**` | 应用层 |
| `task_id` | `const char*` | 应用层（长任务） |
| `heartbeat` | `{lease_id, task_progress}` | 应用层 lease 循环 |
| `token` | JWT string | 远端 / 远域 |
| `trust_bundle` | `bytes` | OTA / 文件 |
| `delegation_req` | `{parent_svid, target_domain, target_service, scopes[], ttl}` | 应用层 |

#### 输出

| 输出 | 数据形态 | 消费者 |
|---|---|---|
| `Task Token` | JWT (RS256, signed) | Guard Sidecar (metadata) |
| `Session Token` | JWT | 自身缓存 + 远域 |
| `Lease + Token` | `{lease_handle, jwt}` | 应用层 + Guard |
| `Heartbeat Resp` | `{revoked, new_scope[], next_heartbeat_ms, reason}` | 应用层 lease loop |
| `claims` | `{iss, sub, aud, exp, scope[], task}` | 上层策略决策 |
| `Delegation Token` | JWT | 跨域调用 metadata |
| `verify_result` | `{ok, reason, claims}` | 远端 Sidecar |

#### 关键 API（KMSS lib）

见 §6 + §14.8（认证部分）。

#### 不变量

- `child_ttl ≤ parent_ttl`
- `child_scope ⊆ parent_scope`
- `child.task.parent_jti = parent.jti`
- `child.aud ∈ parent.scope`
- QM scope ⊄ ASIL-D scope
- silent renew 仅在 TTL < 25% 时启动一次

#### 故障模式

| 故障 | 行为 |
|---|---|
| KMSS 申请 token 失败 | 短任务 fail-closed；长任务进 grace |
| Silent renew 失败 | 30s grace 后 fail-closed |
| Heartbeat 超时 | 30s grace → 自动 revoke lease |
| 跨域 token 验签失败 | 拒绝请求，写审计 |
| Revoke push 超时 | 本地 CRL 兜底，5min 后强制刷新 |

### 16.4 凭据管理模块（Credential）

#### 边界

```
   ┌────────────── Credential 边界 ─────────────────┐
   │                                                  │
   │   输入                          输出             │
   │  ─────                         ─────             │
   │  key_id + algo         →       Key handle        │
   │  parent + child_id     →       Derived key       │
   │  key_id                →       Rotated key       │
   │  key_ref               →       Revoked handle    │
   │  domain + pb           →       Loaded bundle     │
   │  serial / jti          →       CRL entry         │
   │  name + plaintext      →       Wrapped secret ref│
   │  ref                   →       Plaintext (短时)  │
   │                                                  │
   │   内部组件                                        │
   │  ─────────                                       │
   │  • Key Store (TEE 内 + 安全文件)                 │
   │  • Cert Store (TEE 内)                            │
   │  • Trust Bundle Manager                          │
   │  • CRL Publisher (gRPC stream)                    │
   │  • Wrapped Secret Store (L1 envelope)            │
   │  • Key Rotation Scheduler                         │
   │                                                  │
   └──────────────────────────────────────────────────┘
```

#### 输入

| 输入 | 数据形态 | 来源 |
|---|---|---|
| `key_request` | `{key_id, algo, usage}` | 应用 / KMSS 内部 |
| `parent_key_ref` | `kmss_key_ref_t` | KMSS 内部 |
| `cert_request` | `{subject_key, spiffe_id, ttl, sans[]}` | 身份模块 |
| `trust_bundle_pb` | `bytes` | OTA / 文件 |
| `revoke_request` | `{serial_or_jti, reason}` | 应用 / 安全监控 |
| `secret_write` | `{name, plaintext}` | 应用 |
| `rotation_trigger` | `{key_id, schedule}` | OEM / 策略 |

#### 输出

| 输出 | 数据形态 | 消费者 |
|---|---|---|
| `Key handle` | `kmss_key_ref_t` (不透明) | KMSS lib 调用方 |
| `Cert` | X.509 DER | 身份模块 / 远域 Sidecar |
| `Trust Bundle` | protobuf bytes | Sidecar |
| `CRL` | DER bytes | Sidecar / 远域 Sidecar |
| `Wrapped Secret Ref` | `kmss_secret_ref_t` | 应用 |
| `Revocation Event` | gRPC stream message | Sidecar |

#### 关键 API（KMSS lib）

见 §14.8。

#### 不变量

- L0/L1 私钥永远不出 TEE
- Wrapped Secret 仅 L1 key wrap，不在 Normal World 明文
- Trust Bundle 必须由 OEM L0 私钥签名才能被接受
- CRL entry 一旦签发，不可篡改（追加模型）
- Key rotation 必须经过 `active` → `inactive` → `destroy` 三态

#### 故障模式

| 故障 | 行为 |
|---|---|
| L0 损坏 | 整车返厂；其他域不受影响 |
| L1 损坏 | OTA 重推；旧 token 仍可验签 |
| Trust Bundle 损坏 | Sidecar 回退到本地 `.bak` |
| CRL push 失败 | Sidecar 主动 poll（最长 5min 延迟） |
| Wrapped Secret L1 轮换 | 后台 re-wrap，对应用透明 |
| Key rotation 中途失败 | 回滚到 rotation 前的状态 |

### 16.5 模块协作总览

```
                  ┌─────────────────────────────┐
                  │  Identity 模块               │
                  │  • SPIFFE ID                 │
                  │  • Workload SVID             │
                  └──────────────┬───────────────┘
                                 │ SVID 作为 parent
                                 ▼
                  ┌─────────────────────────────┐
                  │  Authentication 模块        │
                  │  • Task / Session / Lease    │
                  │  • Delegation                │
                  │  • Verify + Revoke           │
                  └──────────────┬───────────────┘
                                 │ 底层密钥 / bundle / secret
                                 ▼
                  ┌─────────────────────────────┐
                  │  Credential 模块             │
                  │  • Key Gen / Rotate / Revoke │
                  │  • Trust Bundle              │
                  │  • CRL Push                  │
                  │  • Wrapped Secret            │
                  └──────────────┬───────────────┘
                                 │ L0/L1 密钥 + 签名服务
                                 ▼
                            KMSS (TEE)
```

**调用关系**：
- 身份模块调用凭据管理模块的 `kmss_generate_key` / `kmss_issue_certificate`
- 认证模块调用凭据管理模块的 `kmss_sign` / `kmss_verify` / `kmss_revoke`
- 凭据管理模块为身份和认证模块提供密钥与签名原料，但不依赖二者

**反向关系（不允许）**：
- 凭据管理模块不能反向调用身份或认证模块
- 身份模块不能反向调用认证模块（认证模块以身份模块输出作为输入）

### 16.6 跨域交互（每模块视角）

#### 身份模块（跨域时）
- 跨域**不签发**新 SVID；使用本域 SVID 作为身份
- 通过 Trust Bundle 证明远域 SVID 合法

#### 认证模块（跨域时）
- `kmss_delegate` 跨域签发 delegation token
- 远域 `kmss_verify_delegation` 验签
- Heartbeat 仅在本域 lease 范围内

#### 凭据管理模块（跨域时）
- 通过 Trust Bundle 共享公钥
- CRL 通过 gRPC stream 跨域 push
- L0/L1 私钥永不跨域

### 16.7 demo 阶段的模块边界简化

| 模块 | demo 实现位置 | demo 简化点 |
|---|---|---|
| 身份 | KMSS lib + 应用层调用 | 仅 Workload SVID；不实现 delegation attestation |
| 认证 | KMSS lib + SDK | L0/L1/L2/L3 都实现；X.509-SVID 跳过，全 JWT |
| 凭据管理 | KMSS lib + OTA 脚本 + Sidecar | SoftHSM2 模拟 TEE；bundle 文件系统推送 |

---

## 17. 修订记录

| 版本 | 日期 | 修订内容 |
|---|---|---|
| 1.0 | 2026-07-16 | 初稿：任务分级 + 分层 TTL + KMSS lib API |
| 1.1 | 2026-07-16 | 新增 §14 凭据管理（密钥分层 + CRL + Wrapped Secret） |
| 1.2 | 2026-07-16 | 新增 §15 整体架构（三视图 + 数据流）+ §16 各模块架构（输入/输出） |
| 1.3 | 2026-07-29 | 新增 §18 威胁模型、§19 审计日志格式、§20 限流与配额 |

---

## 18. 威胁模型（STRIDE）

### 18.1 系统信任边界

```
┌─────────────────────────────────────────────────────────┐
│                   信任边界划分                           │
│                                                         │
│  TEE 边界（最高信任）                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │  KMSS daemon + libkmss.so                       │   │
│  │  L0/L1/L2 私钥 + 签名操作                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  内核/进程隔离边界                                       │
│  ┌───────────────┐   ┌───────────────────────────┐    │
│  │ Agent Process │   │ Guard Sidecar Process     │    │
│  │ (Normal World)│   │ (Normal World)            │    │
│  └───────────────┘   └───────────────────────────┘    │
│                                                         │
│  域隔离边界（跨域必须通过 delegation token）             │
│  AD 域 │ CD 域 │ VD 域                                  │
│                                                         │
│  OTA 边界（外部输入，最低信任）                          │
│  Trust Bundle / Policy Update / Model Update            │
└─────────────────────────────────────────────────────────┘
```

### 18.2 STRIDE 威胁矩阵

| # | 威胁 | 类别 | 组件 | 攻击场景 | 现有防护 | 残余风险 |
|---|---|---|---|---|---|---|
| S1 | **Workload 身份伪造** | 欺骗 (S) | Agent Process | 恶意进程伪造 SPIFFE ID，调用 KMSS 申请 SVID | KMSS 验证进程 UID/PID + 白名单；SVID 签发需 TEE 背书 | 低（需 root 权限绕过） |
| S2 | **Token Replay** | 欺骗 (S) | Sidecar | 截获有效 task_token，在 TTL 内重放到另一个 Sidecar | jti 在本域 KMSS CRL 中唯一；token 与 PID 绑定（`km_attest`） | 中（跨域无法及时同步 jti） |
| S3 | **Delegation token 盗用** | 欺骗 (S) | 跨域网络 | MITM 截获 delegation_jwt，向 AD 重放 | mTLS 双向认证；delegation 绑定 target_spiffe_id | 低（mTLS 有效时） |
| T1 | **JWT Claims 篡改** | 篡改 (T) | Agent SDK | 修改 scope、exp 字段后重签 | RS256 签名；私钥在 TEE 内不可导出 | 低 |
| T2 | **Trust Bundle 污染** | 篡改 (T) | OTA 路径 | 注入伪造 trust bundle，使 AD 信任恶意 CD | OTA bundle 用 OEM root 签名；Sidecar 验签后才加载 | 低 |
| T3 | **CRL 截断攻击** | 篡改 (T) | Sidecar | 阻断 CRL 更新，使被 revoke 的 token 继续有效 | Sidecar 设置 CRL 最大陈旧度（5min）；超时 fail-closed | 中（CRL 推送阻断窗口期 ≤ 5min） |
| R1 | **审计日志旁路** | 抵赖 (R) | KMSS / Sidecar | Agent 绕过 Sidecar 直接调用工具，不留审计记录 | 所有工具调用必须通过 Guard（进程隔离）；Sidecar 审计日志不可篡改 | 低 |
| R2 | **jti 碰撞** | 抵赖 (R) | KMSS | 两个 token 生成相同 jti，无法追溯哪次操作 | jti 用 UUID v4（128 bit 熵）；KMSS 签发时检查本地 jti 唯一性 | 极低 |
| I1 | **Token 内容泄露** | 信息泄露 (I) | 网络 | 明文传输 token，第三方读取 scope/sub | 全程 mTLS；UDS 通道不走网络 | 低（mTLS 有效时） |
| I2 | **SVID 内容推断** | 信息泄露 (I) | 日志 | SVID URI 包含 Agent 类型，被日志系统泄露 | 日志脱敏（`svid` 字段只记录前 16 字符 hash） | 中（需日志脱敏实现） |
| D1 | **KMSS 泛洪** | 拒绝服务 (D) | KMSS | 恶意 Agent 高频申请 task_token，耗尽 KMSS 签名能力 | 限流（§20）；每 workload 10 token/s | 中（限流参数需持续调优） |
| D2 | **Trust Bundle 频繁推送** | 拒绝服务 (D) | Sidecar | OTA 系统反复推 bundle，触发频繁重载，影响验签 | Bundle 更新去抖（min 5min 间隔）；reload 与验签异步 | 低 |
| E1 | **scope 越权** | 特权提升 (E) | KMSS | 子 Agent 申请超过父 SVID scope 的 token | `child_scope ⊆ parent_scope` 不变量由 KMSS 强制校验 | 低 |
| E2 | **跨域 ASIL 升级** | 特权提升 (E) | Cross-domain | QM 域 Agent 通过 delegation 触发 ASIL-D 操作 | KMSS 在 `delegate()` 时过滤 ASIL-D scope | 低 |
| E3 | **长时间 token 滥用** | 特权提升 (E) | 长任务 Agent | Lease Token 泄露后长时间被滥用 | Lease 心跳机制；KMSS 可主动 revoke；心跳间隔 ≤ 60s | 中（revoke 传播延迟 ≤ 1s） |

### 18.3 残余风险处置

| 威胁 | 残余风险等级 | 处置方案 |
|---|---|---|
| S2 Token Replay（跨域） | 中 | 短期：task_token TTL 压缩到 15s（demo 可验证）；长期：引入跨域 jti 同步（gRPC stream）|
| T3 CRL 截断 | 中 | 设置 CRL 陈旧度告警（3min 告警，5min fail-closed） |
| I2 SVID 日志推断 | 中 | 审计日志中 SVID 字段只记录 `sha256(svid)[:16]`，原文不落盘 |
| D1 KMSS 泛洪 | 中 | 实现 §20 限流；监控 KMSS 签名 QPS |
| E3 Lease 泄露 | 中 | 心跳超时后立即 revoke；Lease 绑定进程 PID（PID 消亡即 revoke） |

---

## 19. 审计日志格式规范

### 19.1 设计原则

- **不可篡改**：日志写入后只能追加（append-only），写满后 rotate 到 NVRAM/可信存储
- **固定尺寸**：每条日志 **64 字节**，便于车规内存预算（circular buffer 计算确定）
- **无动态分配**：序列化 / 反序列化使用静态 buffer，禁止 `malloc`
- **结构化**：机器可读，便于 OEM 后端分析

### 19.2 审计事件结构体

```c
// audit_log.h

typedef enum {
    // Token 生命周期
    AUDIT_SVID_ISSUED         = 0x01,
    AUDIT_SVID_REVOKED        = 0x02,
    AUDIT_TASK_TOKEN_ISSUED   = 0x03,
    AUDIT_TASK_TOKEN_CONSUMED = 0x04,
    AUDIT_TASK_TOKEN_EXPIRED  = 0x05,
    AUDIT_SESSION_OPENED      = 0x06,
    AUDIT_SESSION_RENEWED     = 0x07,
    AUDIT_SESSION_CLOSED      = 0x08,
    AUDIT_LEASE_ACQUIRED      = 0x09,
    AUDIT_LEASE_HEARTBEAT     = 0x0A,
    AUDIT_LEASE_SCOPE_TIGHT   = 0x0B,
    AUDIT_LEASE_RELEASED      = 0x0C,
    AUDIT_LEASE_REVOKED       = 0x0D,

    // 决策
    AUDIT_GUARD_ALLOW         = 0x10,
    AUDIT_GUARD_DENY          = 0x11,

    // 跨域
    AUDIT_DELEG_ISSUED        = 0x20,
    AUDIT_DELEG_VERIFIED_OK   = 0x21,
    AUDIT_DELEG_VERIFIED_FAIL = 0x22,

    // 安全事件
    AUDIT_JTI_REPLAY_DETECT   = 0x30,
    AUDIT_SCOPE_EXCEED        = 0x31,
    AUDIT_CRL_REVOKE_RECV     = 0x32,
    AUDIT_TEE_FAULT           = 0x33,
    AUDIT_RATE_LIMIT_HIT      = 0x34,
    AUDIT_ASIL_SCOPE_FILTER   = 0x35,  // QM→ASIL-D scope 被过滤
} audit_event_type_t;

// 决策结果
typedef enum {
    AUDIT_DECISION_ALLOW = 1,
    AUDIT_DECISION_DENY  = 2,
    AUDIT_DECISION_ERROR = 3,
} audit_decision_t;

// 固定 64 字节审计记录
typedef struct __attribute__((packed)) {
    uint64_t  timestamp_us;      //  8 字节：微秒时间戳（来自安全 RTC）
    uint32_t  event_type;        //  4 字节：audit_event_type_t
    uint8_t   decision;          //  1 字节：audit_decision_t
    uint8_t   domain;            //  1 字节：0=AD,1=CD,2=VD
    uint8_t   token_layer;       //  1 字节：0=SVID,1=task,2=session,3=lease
    uint8_t   reason_code;       //  1 字节：拒绝原因（0=allow, 其他见下表）
    uint8_t   jti_prefix[8];     //  8 字节：jti 的前 8 字节（快速关联）
    uint8_t   sub_hash[8];       //  8 字节：sha256(sub_spiffe_id)[:8]
    uint8_t   aud_hash[4];       //  4 字节：sha256(aud)[:4]
    uint8_t   scope_hash[8];     //  8 字节：sha256(scope_str)[:8]
    uint32_t  ttl_remaining_s;   //  4 字节：token 签发时剩余 TTL
    uint32_t  task_id_prefix;    //  4 字节：task_id 的前 4 字节（A2A 任务关联）
    uint8_t   pad[5];            //  5 字节：保留，对齐到 64 字节
} audit_record_t;               // 总计：64 字节

_Static_assert(sizeof(audit_record_t) == 64, "audit_record must be 64 bytes");
```

**reason_code 枚举**（拒绝时有效）：

```c
typedef enum {
    REASON_ALLOW              = 0x00,
    REASON_JWT_EXPIRED        = 0x01,
    REASON_JWT_SIG_INVALID    = 0x02,
    REASON_SCOPE_EXCEED       = 0x03,
    REASON_JTI_REVOKED        = 0x04,
    REASON_JTI_REPLAY         = 0x05,
    REASON_ASIL_BOUNDARY      = 0x06,
    REASON_CRL_REVOKED        = 0x07,
    REASON_BUNDLE_STALE       = 0x08,
    REASON_RATE_LIMIT         = 0x09,
    REASON_POLICY_DENY        = 0x0A,
    REASON_TEE_UNAVAILABLE    = 0x0B,
} audit_reason_code_t;
```

### 19.3 存储与传输

```
写入路径：
  Sidecar / KMSS → audit_ring_buffer（内存, 4 KB = 64 条）
      │
      │ 满或每 30s flush
      ▼
  /var/log/agent-iam/audit.bin   ← append-only，文件锁保护
      │
      │ logrotate：每 10 MB 或每天 rotate
      ▼
  /var/log/agent-iam/audit.N.bin（压缩 + 校验）
      │
      │ OTA 上报（非实时，每分钟批量）
      ▼
  OEM 后端审计系统
```

**写入 API**：

```c
// 同步写（Sidecar 路径，必须低延迟）
void audit_log_write(const audit_record_t* rec);  // ≤ 100μs

// 异步写（批量 flush 线程）
void audit_log_flush_pending(void);
```

**完整性保护**：

```c
// 每 N 条记录追加一个 HMAC 校验节点
typedef struct {
    uint8_t  marker[4];   // 0xAU_DIT1
    uint32_t seq_start;   // 第一条记录序号
    uint32_t seq_end;     // 最后一条记录序号
    uint8_t  hmac[32];    // HMAC-SHA256(records[start..end], domain_key)
} audit_checkpoint_t;
```

### 19.4 关键事件必审记录

以下事件**必须**同步写审计日志，不允许因性能原因跳过：

| 事件 | 原因 |
|---|---|
| `AUDIT_SVID_ISSUED` / `AUDIT_SVID_REVOKED` | 工作负载身份变更 |
| `AUDIT_GUARD_DENY` | 拒绝决策，调查入口 |
| `AUDIT_JTI_REPLAY_DETECT` | 安全攻击指示 |
| `AUDIT_SCOPE_EXCEED` | 越权尝试 |
| `AUDIT_CRL_REVOKE_RECV` | 紧急撤销传播 |
| `AUDIT_TEE_FAULT` | 硬件故障 |
| `AUDIT_ASIL_SCOPE_FILTER` | 跨域 ASIL 边界触发 |

---

## 20. 限流与配额

### 20.1 设计目标

防止 KMSS 被单个 Agent 泛洪（DoS），同时保证正常业务的 token 申请不被饿死。

### 20.2 限流维度与参数

```c
// kmss_ratelimit.h

typedef struct {
    // ===== Per-Workload 限流 =====
    uint32_t task_token_per_second;     // 默认 10 /s（L1）
    uint32_t session_renew_per_minute;  // 默认 4 /min（L2，TTL=15min → 75% 处续期）
    uint32_t lease_acquire_per_minute;  // 默认 2 /min（L3）
    uint32_t lease_concurrent_max;      // 默认 5（同时持有的 lease 上限）

    // ===== Per-Domain 限流（防止单域垄断 KMSS 资源）=====
    uint32_t domain_token_per_second;   // 默认 50 /s（所有 workload 合计）
    uint32_t domain_deleg_per_minute;   // 默认 20 /min（跨域 delegation）

    // ===== 全局限流 =====
    uint32_t global_sign_per_second;    // 默认 200 /s（TEE 签名 QPS 上限）
} kmss_ratelimit_config_t;
```

**默认值依据**：

| 参数 | 默认值 | 依据 |
|---|---|---|
| `task_token_per_second` | 10 /s | 正常 Agent 每次 Guard.Check 约 50~200ms，上限约 5-20 QPS；留 2× 余量 |
| `lease_concurrent_max` | 5 | 单 workload 最多 5 个并发长任务（演示场景：规划、OTA、监控等） |
| `global_sign_per_second` | 200 /s | SoftHSM2 签名能力约 500 /s，留 60% 余量 |

### 20.3 令牌桶实现

```c
// 令牌桶（固定速率，无动态内存）
typedef struct {
    uint32_t capacity;          // 桶容量（最大突发）
    uint32_t tokens;            // 当前令牌数
    uint32_t refill_rate_us;    // 每 N 微秒补充 1 个令牌
    uint64_t last_refill_us;    // 上次补充时间（来自安全 RTC）
    uint32_t dropped_total;     // 统计：被限流总数（overflow 不统计）
} token_bucket_t;

// 尝试消耗 n 个令牌，返回 0=成功，-1=限流
int token_bucket_consume(token_bucket_t* tb, uint32_t n) {
    uint64_t now_us = secure_rtc_now_us();
    uint64_t elapsed = now_us - tb->last_refill_us;
    uint32_t refill = (uint32_t)(elapsed / tb->refill_rate_us);
    if (refill > 0) {
        tb->tokens = MIN(tb->capacity, tb->tokens + refill);
        tb->last_refill_us += refill * tb->refill_rate_us;
    }
    if (tb->tokens < n) {
        tb->dropped_total++;
        return -1;  // 限流
    }
    tb->tokens -= n;
    return 0;
}
```

### 20.4 KMSS 限流集成

```c
// kmss_issue_task_token() 内部调用流程（增加限流）

kmss_token_t* kmss_issue_task_token(
    kmss_svid_t* parent,
    const char** scopes, size_t n,
    uint32_t ttl_seconds
) {
    // 1. 查找 per-workload 限流桶
    token_bucket_t* wb = kmss_get_workload_bucket(parent->workload_id,
                                                   BUCKET_TASK_TOKEN);
    if (token_bucket_consume(wb, 1) != 0) {
        audit_log_write(&(audit_record_t){
            .event_type  = AUDIT_RATE_LIMIT_HIT,
            .decision    = AUDIT_DECISION_DENY,
            .reason_code = REASON_RATE_LIMIT,
            ...
        });
        return NULL;  // 限流返回 NULL（调用方应重试或降级）
    }

    // 2. 全局签名桶
    token_bucket_t* gb = kmss_get_global_bucket(BUCKET_SIGN);
    if (token_bucket_consume(gb, 1) != 0) {
        return NULL;
    }

    // 3. 正常签发
    return kmss_sign_task_token_internal(parent, scopes, n, ttl_seconds);
}
```

### 20.5 限流后的 SDK 行为

```
SDK 收到 kmss_issue_task_token() 返回 NULL（限流）：

 ┌─────────────────┐
 │  task_token 为空  │
 └────────┬────────┘
          │
     检查 session_token 是否有效（L2）
          │
     ┌────┴──────────────────────┐
     │ 是（session 有效）         │ 否（session 也过期）
     │                           │
     ▼                           ▼
  指数退避重试                 fail-closed
  （50ms, 100ms, 200ms）       返回 UNAVAILABLE
     │
     ▼
  重试 3 次后仍失败
     │
     ▼
  降级：返回缓存的上次 allow 决策（仅只读操作）
  写/执行操作：fail-closed
```

**退避参数**（可配置）：

```c
#define RATE_LIMIT_RETRY_MAX     3
#define RATE_LIMIT_BACKOFF_MS_1  50
#define RATE_LIMIT_BACKOFF_MS_2  100
#define RATE_LIMIT_BACKOFF_MS_3  200
```

### 20.6 配额监控

KMSS 对外暴露以下计数器（用于 OEM 监控）：

```c
typedef struct {
    uint64_t task_token_issued_total;
    uint64_t task_token_rejected_ratelimit;
    uint64_t session_renew_total;
    uint64_t lease_acquire_total;
    uint64_t lease_revoke_total;
    uint64_t sign_qps_peak;           // 峰值签名 QPS（滑动窗口 1min）
    uint64_t global_sign_ratelimit_total;
} kmss_metrics_t;

// 通过 gRPC 健康检查端点暴露
// GET /metrics → Prometheus 格式
```

**告警阈值**（demo 建议）：

| 指标 | 告警阈值 | 意义 |
|---|---|---|
| `task_token_rejected_ratelimit` / min | > 50 | 可能有异常 Agent 泛洪 |
| `sign_qps_peak` | > 150 /s | 接近 KMSS 能力上限 |
| `lease_acquire_total` / workload | > 100 /h | 单个 workload 异常频繁申请 lease |

---

## 21. Token Binding（mTLS 信道绑定，防 Bearer 盗用）

### 21.1 问题：Bearer Token 的可盗用性

Bearer Token（RFC 6750）的语义是"持有即授权"——任何拿到 token 的人都可以使用它，
即使它来自内存泄露、日志泄露或中间人攻击。

```
攻击场景（Bearer Token 盗用）：

合法 Agent（CD 域）申请 delegation_jwt
  └─ delegation_jwt 存储在 Normal World 内存
           │
           │ 攻击者从被攻陷进程读取内存（如 heap spray、TOCTOU）
           │
           ▼
攻击者在另一台机器上持有 delegation_jwt
  └─ 向 AD Sidecar 重放（如果没有信道绑定）
           │
           ▼
AD Sidecar 验证签名 + TTL：均通过！无法区分合法 vs 盗用
```

**现有防御的局限**：
- TTL 短（30s task token）：盗用窗口小，但不是零
- mTLS Channel：验证了连接两端的 SPIFFE ID，但 Bearer Token 可以在连接外使用

### 21.2 解决方案：mTLS Certificate-Bound Token（RFC 8705）

将 Bearer Token 绑定到发起方的 **mTLS TLS 证书指纹**（`cnf.x5t#S256` claim）。
Server 端验证：携带 token 的连接的 TLS 客户端证书哈希 == token claims 里的指纹。

```
Token Binding 机制：

1. Client（CD Agent）建立 mTLS 连接时：
   client_cert = TLS 握手中的 CD SPIFFE SVID X.509 证书

2. KMSS 签发 delegation token 时，计算证书指纹并写入 claims：
   cnf.x5t#S256 = base64url(SHA256(DER(client_cert)))

3. Server（AD Sidecar）验证时：
   a. 从 TLS 连接提取 peer 证书
   b. 计算 SHA256(DER(peer_cert))
   c. 对比 token.claims.cnf["x5t#S256"]
   d. 不匹配 → 拒绝（token 来自不同的 TLS 连接 = 盗用）
   e. 匹配 → 继续后续 scope / task_id 检查
```

### 21.3 Claims 扩展

```json
{
  "iss": "spiffe://car.local/ad/kmss",
  "sub": "spiffe://car.local/cd/voice/01",
  "aud": "spiffe://car.local/ad/perception/01",
  "exp": 1753879808,
  "jti": "0192f9b7-...",
  "scope": ["read:navi.route"],

  "cnf": {
    "x5t#S256": "bwcK0esc3ACC3DB2Y5_lESsXE8o9ltc05O89jdN-dg8"
  }
}
```

`cnf`（Confirmation）字段是 RFC 8705 标准字段，KMSS 在签发时写入。

### 21.4 KMSS API 扩展

```c
// 签发 task token 时额外传入调用方证书（用于绑定）
kmss_token_t* kmss_issue_task_token_bound(
    kmss_svid_t*    parent,
    const char**    scopes, size_t n,
    uint32_t        ttl_seconds,
    const uint8_t*  client_cert_der,   // 调用方 TLS 客户端证书 DER（来自 mTLS 握手）
    size_t          client_cert_len
);

// 验证 token 时同时验证信道绑定
int kmss_verify_token_with_binding(
    kmss_token_t*        token,
    const uint8_t*       trust_bundle, size_t bundle_len,
    const uint8_t*       peer_cert_der, size_t peer_cert_len,  // 当前 TLS 连接的 peer 证书
    kmss_claims_t*       out_claims
);
// 返回 IAM_TOKEN_BINDING_MISMATCH 如果 cnf 不匹配
```

### 21.5 Sidecar 验证流程更新

```c
// BearerTokenInterceptor（带 token binding 检查）

int bearer_token_interceptor(grpc_call_t* call) {
    // 1. 提取 bearer token
    const char* bearer = grpc_meta_get(call->metadata, "authorization") + 7; // "Bearer "

    // 2. 提取当前 TLS 连接的 peer 证书（由 mTLS 握手提供）
    const uint8_t* peer_cert = grpc_call_get_peer_cert(call, &peer_cert_len);

    // 3. 验证 token + binding（一次调用）
    kmss_claims_t claims;
    int rc = kmss_verify_token_with_binding(
        bearer_token, trust_bundle, bundle_len,
        peer_cert, peer_cert_len,
        &claims
    );

    if (rc == IAM_TOKEN_BINDING_MISMATCH) {
        audit_log_write(&(audit_record_t){
            .event_type  = AUDIT_TOKEN_BINDING_FAIL,
            .reason_code = REASON_BINDING_MISMATCH,
            ...
        });
        return GRPC_STATUS_UNAUTHENTICATED;
    }
    // ...
}
```

### 21.6 Token Binding 的 ASIL 分级适用

| Token 层级 | Binding 是否必须 | 理由 |
|---|---|---|
| L0 Workload SVID | 不适用（不是 Bearer） | SVID 本身就是 TLS 证书 |
| L1 Task Token（TTL ≤ 30s）| 可选 | TTL 极短，盗用窗口 < 30s，binding 收益有限 |
| L2 Session Token（TTL 15min）| **必须** | 15min 盗用窗口显著，binding 是必要防护 |
| L3 Lease Token（TTL 数小时）| **必须** | 长时间窗口，binding 是核心防护 |
| L3A A2A Delegation（跨域）| **必须** | 跨域 token，被盗后影响面更大 |

**实现优先级**：先为 L2/L3/L3A 实现 binding，L1 可后续补充。

---

## 22. 紧急关闭（Emergency Shutdown）

### 22.1 场景：车辆被攻陷的响应

```
场景：OEM 检测到 VIN=XXX 的车辆存在异常 Agent 行为（如 prompt injection 导致越权）
     需要立即停止该车所有 LLM Agent 的授权操作

现有 revoke 机制（per-JTI）的局限：
  - 已知 JTI：每个 JTI 单独 revoke，需要知道所有活跃 token 的 JTI
  - KMSS 上哪些 token 活跃？→ 没有全量索引（token 不落盘）
  - 最快做法：revoke 所有 Workload SVID（Level-0 级别撤销）
```

### 22.2 三层紧急关闭机制

```
┌───────────────────────────────────────────────────────────┐
│ Level 1（最快，< 1s）: Sidecar 切断授权                    │
│  OEM → AD/CD/VD Sidecar: emergency_shutdown(reason)      │
│  Sidecar 立即切换到 DENY_ALL 模式                         │
│  所有后续 Guard.Check → 拒绝（已有 token 不再被接受）      │
│  注意：进行中的 gRPC 流不中断（等调用返回后再切断）         │
└───────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────┐
│ Level 2（< 3s）: KMSS 吊销所有 Workload SVID              │
│  OEM → 3 个域 KMSS: revoke_all_workload_svids()          │
│  KMSS 撤销所有 L2 workload key → 现有 token 签名链断裂    │
│  所有 token 验签失败（即使 Sidecar 未收到通知也生效）       │
└───────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────┐
│ Level 3（需维修）: L1 Domain Key 撤销                     │
│  极端情况：怀疑 Domain Key 泄露                            │
│  OEM 推送新 trust bundle（含 L1 revocation）              │
│  整车返厂重新注入 or OTA 重建 domain chain                 │
└───────────────────────────────────────────────────────────┘
```

### 22.3 Sidecar 紧急关闭 API

```c
// kmss_emergency.h

typedef enum {
    EMERGENCY_DENY_ALL          = 1,   // Level 1：拒绝所有授权（最快）
    EMERGENCY_REVOKE_SVIDS      = 2,   // Level 2：撤销所有 SVID
    EMERGENCY_REVOKE_DOMAIN_KEY = 3,   // Level 3：撤销 L1 domain key（需人工确认）
} emergency_level_t;

typedef struct {
    emergency_level_t level;
    const char*       reason;          // 人读原因（审计用）
    const char*       initiated_by;    // 发起方标识（OEM backend SPIFFE ID）
    uint64_t          timestamp;       // 操作时间戳（来自 OEM，防回放）
    uint8_t           signature[72];   // OEM backend 用 L1 私钥签名（防伪造指令）
} emergency_shutdown_t;

// Sidecar 接收 OEM 紧急关闭指令（通过 gRPC stream 或带外通道）
int sidecar_emergency_shutdown(
    const emergency_shutdown_t* cmd,
    const uint8_t* oem_trust_bundle, size_t bundle_len  // 验证指令签名
);

// 恢复（需 OEM 显式指令 + 时间戳 > shutdown 时间戳）
int sidecar_emergency_resume(
    const char*    reason,
    uint64_t       timestamp,
    const uint8_t* oem_signature, size_t sig_len
);
```

### 22.4 紧急关闭状态机

```
Normal
  │
  │ emergency_shutdown(DENY_ALL)
  ▼
Deny-All Mode ─────────────────────────────────────────────
  │ 所有 Guard.Check → 拒绝（不查 token）
  │ 现有流：等当前 RPC 完成后拒绝新请求
  │
  │ emergency_shutdown(REVOKE_SVIDS)（可与 DENY_ALL 同时）
  ▼
SVIDs-Revoked Mode ─────────────────────────────────────────
  │ KMSS 撤销所有 L2 key
  │ 所有 token 验签 → 失败（即使 Sidecar 还没切到 DENY_ALL）
  │
  │ sidecar_emergency_resume()（来自 OEM）
  ▼
Recovery Mode ────────────────────────────────────────────
  │ KMSS 重新签发 SVID
  │ Agent 重启 + 重新申请 Session Token
  │ 系统自检通过后 → Normal
  ▼
Normal
```

### 22.5 审计记录（紧急关闭必须写入的事件）

```c
AUDIT_EMERGENCY_SHUTDOWN_RECEIVED,  // 收到关闭指令
AUDIT_EMERGENCY_DENY_ALL_ACTIVE,    // DENY_ALL 模式激活
AUDIT_EMERGENCY_SVID_REVOKE_ALL,    // 所有 SVID 撤销
AUDIT_EMERGENCY_RESUME_RECEIVED,    // 收到恢复指令
AUDIT_EMERGENCY_RESUME_ACTIVE,      // 恢复完成
AUDIT_EMERGENCY_INVALID_SIGNATURE,  // 关闭/恢复指令签名无效（防伪造）
```

这些事件**必须写入 NVRAM（不可擦除）**，不受关闭模式影响。

---

## 23. 车云 IAM 扩展（V2C：Vehicle-to-Cloud Agent）

### 23.1 场景与挑战

车端 Agent（如 CD Voice Agent）需要调用**云端 LLM API**（如 OEM 自建 LLM 服务），
或云端 OTA 服务需要向车端 Agent 发起任务。

```text
车端信任域（car.local）               云端信任域（cloud.oem.com）
  CD Voice Agent                          LLM Gateway
  SVID: spiffe://car.local/...   ←→       SVID: spiffe://cloud.oem.com/...
  KMSS: 本地 TEE                          KMSS: 云端 HSM

挑战：
  1. 两个信任域（car.local vs cloud.oem.com）互不认识
  2. 车端 token 由车端 KMSS 签发，云端 KMSS 无法验签
  3. 离线场景：TBOX 断网时，车端不能依赖云端 KMSS
  4. Token 撤销跨域传播：云端 revoke，车端如何感知？
```

### 23.2 SPIFFE Federation（跨域信任）

核心机制：两个信任域通过 **SPIFFE Federation Bundle** 交换各自的 trust anchor，
实现跨域 mTLS 验证（不需要 token 跨域传输）。

```
车云 Federation 建立：

OEM Cloud（cloud.oem.com）：
  发布 federation bundle：
  {
    "trust_domain": "cloud.oem.com",
    "keys": [{"kty": "EC", "crv": "P-256", ...}],  // L1 domain public key
    "refresh_hint": 3600
  }

车端（car.local）：
  OTA bundle 中包含 cloud.oem.com 的 trust anchor
  车端 SPIRE Agent（或 KMSS）加载后：
    可以验证 cloud.oem.com 签发的 SVID

云端反向同样：
  云端加载 car.local 的 trust anchor
  可以验证车端 SVID
```

### 23.3 车云跨域 Token 交换（Online）

```
在线场景（TBOX 有网络连接）：

1. 车端 CD Agent 申请车端 SVID（已有，L0）
2. 向云端 LLM Gateway 建立 mTLS 连接
   - TLS 客户端证书：CD Agent 的 SVID X.509
   - TLS 服务端证书：LLM Gateway 的 SVID
   - 双方通过 Federation trust anchor 互相验证 ✓

3. CD Agent 用 Authorization: Bearer <car_local_token>
4. LLM Gateway Sidecar 验证 car_local_token：
   - 用 car.local 的 trust bundle（federation 获取）验签
   - scope 检查（invoke:llm.chat 等）
   - mTLS binding 检查（cnf.x5t#S256）

5. LLM Gateway 返回响应
   - 响应携带 X-Cloud-Job-Id
   - 车端 SDK 建立 cloud_job_id → local_lease_jti 映射
```

### 23.4 离线 Token 缓存（TBOX 断网场景）

```
离线场景：车辆进入隧道 / 地下停车场，TBOX 无网络

提前预热（进入弱网区之前）：
  车端 SDK 检测到信号变弱 → 触发 offline_preload()

offline_preload() 执行：
  1. 申请较长 TTL 的车云凭据（TTL = 预估离线时长 + 缓冲）
  2. 凭据存入 KMSS 保护的 wrapped secret
  3. 记录预估离线结束时间

离线期间：
  使用缓存凭据，直到 TTL 到期
  TTL 到期后不能申请新的云端凭据 → 云端 LLM 功能降级
  本地 LLM（如果有）继续工作

重新上线：
  TBOX 检测到网络恢复 → 触发 online_resume()
  重新申请车云凭据 → 清理过期缓存
```

### 23.5 车云 KMSS API 扩展

```c
// 建立车云 Federation
int kmss_load_cloud_trust_bundle(
    const char*    cloud_trust_domain,    // "cloud.oem.com"
    const uint8_t* federation_bundle,    // OTA 推送的 Federation bundle
    size_t         bundle_len
);

// 签发跨域凭据（面向云端服务）
kmss_token_t* kmss_issue_cloud_delegation(
    kmss_svid_t*    car_svid,
    const char*     cloud_service_spiffe_id,  // "spiffe://cloud.oem.com/ns/llm/sa/gateway"
    const char**    scopes, size_t n_scopes,
    uint32_t        ttl_seconds,
    const uint8_t*  client_cert_der, size_t cert_len  // mTLS binding
);

// 预加载离线凭据
int kmss_preload_offline_credentials(
    kmss_svid_t*    car_svid,
    uint32_t        offline_est_seconds  // 预估离线时长
);

// 验证云端下行 token（云端向车端发起任务时）
int kmss_verify_cloud_inbound_token(
    const uint8_t*  token, size_t token_len,
    const char*     cloud_trust_domain,
    const uint8_t*  federation_bundle, size_t bundle_len,
    kmss_claims_t*  out_claims
);
```

### 23.6 车云 IAM 安全边界

| 边界 | 规则 | 原因 |
|---|---|---|
| 云端 scope ≠ 车端 scope | 云端 scope（`invoke:llm.chat`）不能映射为车端安全 scope（`tool:control.brake`）| 防止云端被攻陷后横向移动 |
| ASIL 单向 | QM 云端服务不能触发 ASIL-D 车端操作 | 云端不在 ASIL 功能安全认证范围内 |
| 离线自洽 | 车端不依赖云端进行安全决策（Guard.Check 纯本地）| 网络中断不影响本地安全功能 |
| 云端 token 在车端独立 namespace | `cloud.oem.com` scope 与 `car.local` scope 严格隔离 | 跨域不混用 scope 字符串 |

---

## 24. IAM 完善后的落地优先级

综合 §18~§23 新增内容，按优先级整理落地清单：

### P0（必须实现，影响基础安全）

- [ ] **§21 Token Binding**：L2 Session + L3 Lease + L3A A2A Delegation 必须绑定 mTLS 证书
- [ ] **§22 Level-1 紧急关闭**：Sidecar DENY_ALL 模式（< 1s 响应）+ 审计 NVRAM 写入

### P1（应该实现，影响完整性）

- [ ] **§21 L1 Task Token Binding**：TTL 短，可选但推荐
- [ ] **§22 Level-2 SVID 全量撤销**：KMSS `revoke_all_workload_svids()` + 跨域传播
- [ ] **§19 审计日志补充**：新增 `AUDIT_TOKEN_BINDING_FAIL`、`AUDIT_EMERGENCY_*` 事件类型

### P2（应该实现，影响扩展性）

- [ ] **§23 SPIFFE Federation Bundle**：OTA bundle 内携带 cloud.oem.com trust anchor
- [ ] **§23 车云在线 Token 交换**：`kmss_issue_cloud_delegation()` + LLM Gateway Sidecar 验证

### P3（远期，可选）

- [ ] **§23 离线预热缓存**：弱网检测 + `kmss_preload_offline_credentials()`
- [ ] **§22 Level-3 Domain Key 撤销**：整车生命周期极少触发，人工流程

---

## 25. 修订记录更新

| 版本 | 日期 | 修订内容 |
|---|---|---|
| 1.0 | 2026-07-16 | 初稿：任务分级 + 分层 TTL + KMSS lib API |
| 1.1 | 2026-07-16 | 新增 §14 凭据管理（密钥分层 + CRL + Wrapped Secret） |
| 1.2 | 2026-07-16 | 新增 §15 整体架构（三视图 + 数据流）+ §16 各模块架构（输入/输出） |
| 1.3 | 2026-07-29 | 新增 §18 威胁模型、§19 审计日志格式、§20 限流与配额 |
| 1.4 | 2026-07-30 | 新增 §21 Token Binding（mTLS 信道绑定）、§22 紧急关闭（Emergency Shutdown）、§23 车云 IAM 扩展（V2C）、§24 落地优先级 |
