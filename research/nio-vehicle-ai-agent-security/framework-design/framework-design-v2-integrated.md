# NIO Vehicle AI Agent Security Framework — Integrated Design Spec v2.0

> **整合自**：
> - `framework-design-v1.html` (Framework v1.1, 完整协议栈)
> - `../nio-asg-design/architecture.md` (ASG v0.1, 嵌入式车规单进程形态)
> - `../llm-agent-delegation-research-2026/README.md` (四梯队调研)
>
> **目标读者**: Coding Agent / 实施工程师
> **格式**: 紧凑 markdown, 去装饰, 决策/模块/API/字段
> **关系说明**: Framework = 顶层协议栈, ASG = 车规级实现形态 (单进程 + 2 Gate)
> **版本**: v2.0 (2026-07-21)

---

## Part 1 — 总览

### 1.1 关键决策

| 决策点 | 选择 | 来源 |
|--------|------|------|
| **顶层协议** | JWT-SVID + RFC 8693 + SPIFFE Federation | Framework v1.1 |
| **车规形态** | 单进程 + 2 Gate (AuthGate + DataGate) | ASG v0.1 |
| **凭证层数** | 3 层 (L1 持久 + L2 运行 + L3 临时) | Framework v1.1 |
| **车规裁剪** | ASG 形态可压缩为 2 层 (L1+L2 Ticket) | ASG v0.1 |
| **委托链** | RFC 8693 `act` claim (P0); ASG `depth` u8 (裁剪) | 双源 |
| **身份目录** | Agent Registry (TEE 内 gRPC + SQLite) | Framework v1.1 |
| **Blueprint 存储** | OCI Artifact + cosign | Framework v1.1 |
| **Attestation** | TPM 2.0 + IMA (P1+); ASG 假设可信 (P0) | 双源 |
| **跨域通信** | gRPC + JWT Bearer (P0); mTLS + JWT (P2) | Framework v1.1 |
| **Sub-Agent** | 线程 + 裸进程双模 (P0); ASG 线程为主, 进程为 escape hatch | 双源 |
| **车控域 L3** | 永不发 (硬约束) | 双源一致 |
| **车控跨域** | 仅接收 (主动禁止, 仅只读查询) | 双源一致 |
| **威胁模型** | T-01..T-10 完整 (Framework) | Framework v1.1 |
| **威胁精简** | T-1..T-5 (ASG, 资源极紧时) | ASG v0.1 |
| **X.509** | P2 引入 (传输层 mTLS) | Framework v1.1 |
| **C509** | P3+ 远期 | Framework v1.1 |

### 1.2 POC 范围（硬约束）

**POC 必做**:
- [x] JWT-SVID 签发 / 验签 (HS256 起步, 生产切 ES256)
- [x] 三层凭证流转 (L1 / L2 / L3)
- [x] 委托链 (`act` claim)
- [x] 简化跨域通信 (预置公钥模拟 Federation)
- [x] Sub-Agent 派生 + 主动撤销
- [x] ASG 单进程形态 (函数调用, 不上 gRPC)
- [x] 接口抽象层 (为 JWT/HMAC、X.509/C509 切换预留)
- [x] 单元测试 + 集成测试

**POC 不做**:
- [ ] X.509 证书管理
- [ ] mTLS
- [ ] 完整 Attestation
- [ ] OpenFGA 集成 (用 if-else 模拟)
- [ ] 真实 Registry 服务 (用内存对象)
- [ ] 完整审计加密 (用 stdout)
- [ ] C509 / CWT
- [ ] 车控域 Lite 版

**POC 目标**: 2 周内跑通"主 Agent 派生 L3 → Sub-Agent 调 Tool → 验证 → 撤销"端到端。

---

## Part 2 — 整体架构

### 2.1 顶层架构 (Framework 视角)

```
NIO Vehicle AI Agent Security Framework
├─ IAM (身份治理)        ← AuthGate 收敛
│  ├─ 身份层 (Blueprint / Registry / 状态机)
│  ├─ 认证层 (Attestation 三层栈)
│  └─ 凭证层 (L1/L2/L3 JWT-SVID)
├─ INPUT (入口过滤)      ← DataGate.input 收敛
│  └─ 入口数据签名 / 参数校验
├─ OUTPUT (出口过滤)     ← DataGate.output 收敛
│  └─ 出口数据签名 / PII 脱敏
├─ Guard (策略执行)     ← AuthGate ACL + DataGate 串接
│  ├─ Tool 治理
│  ├─ Sub-Agent 派生
│  └─ 条件访问 (Conditional Access)
└─ Audit (审计)        ← Ring Buffer + 上报
```

### 2.2 车规落地形态 (ASG 视角)

```
单进程 + 2 个 Gate 线程
├─ Main Loop Thread (LLM 推理 + 工具调度)
├─ AuthGate Thread (IAM 合并)
│  ├─ auth_init / auth_get_self_id
│  ├─ auth_issue_ticket / auth_verify_ticket
│  └─ auth_revoke / auth_revoke_all (Kill Switch)
├─ DataGate Thread (INPUT + OUTPUT 合并)
│  ├─ datagate_check_input
│  ├─ datagate_check_output
│  └─ datagate_sign_output / datagate_verify_input
├─ Sub-Agent Pool (线程模式为主, 裸进程 escape hatch)
└─ Audit Ring Buffer (~256KB, 循环覆盖)
```

### 2.3 三域部署

| 域 | 资源 | ASG 形态 | 凭证 | Sub-Agent |
|----|------|----------|------|-----------|
| 座舱 (8295+QTEE) | ~1.5MB RAM | **ASG 完整版** | L1+L2+L3 | 线程+进程 |
| 智驾 (Orin+OP-TEE) | ~1.2MB RAM | **ASG 标准版** | L1+L2+L3 | 偏进程 |
| 车控 (S32G+HSM) | ~0.7MB RAM | **ASG 极简版** | L1+L2 (无 L3) | **不启用** |

### 2.4 跨域通信

**默认禁止**, 例外走 **Cross-Domain Gateway (XGW)** 集中转发+审计。

```
座舱 ASG ─┐
          ├─ HTTP/mTLS → XGW → HTTP/mTLS → 智驾 ASG
智驾 ASG ─┘
                                 ↓
                            Audit Sink
```

**跨域三原则**:
1. 默认禁止, 例外走 XGW
2. 跨域 ticket 与域内 ticket **不同 ID** (防重放)
3. XGW 是**唯一**的跨域通道, 所有跨域流量必经审计

---

## Part 3 — 模块详细设计

### 3.1 IAM 模块 (身份 + 认证 + 凭证)

#### 3.1.1 身份层

**三个核心对象**:

| 对象 | 角色 | 维护方 | POC 状态 |
|------|------|--------|----------|
| Blueprint | Agent 模板 (如 `nav-reroute-agent-v1`) | 车厂 Sponsor | 内存常量 |
| Registry Record | 实例化后的"我是谁" | Agent Registry (TEE 内) | 内存对象 |
| L1 JWT-SVID | 实体 Agent 运行时凭证 | TPM-AS | POC 实现 |

**Blueprint 字段定义** (参考 SPIRE Workload Entry + 车端扩展):

```yaml
blueprint_id: nav-reroute-agent-v1
version: 1.2.0
domain: nio-cockpit
type: llm-guard-7b

identity:
  spiffe_id_pattern: "spiffe://nio-cockpit/nav-reroute-{instance_id}"
  sponsor:
    id: "sponsor:abc-corp"
    # cert: <KMSS 签名>  # P1 引入

capabilities:
  - nav:read
  - nav:reroute
  - map:query
prohibited:
  - nav:write_persistent
  - can:brake

risk_class: medium
asil_level: QM

quotas:
  max_sub_agents: 3
  max_task_duration_sec: 300
  max_token_per_min: 60
  max_memory_mb: 256

attestation:                      # P1+ 引入
  min_pcr_policy: "pcr0-7:strict"
  binary_signature_required: true
  hsm_key_required: true
  refresh_interval_sec: 3600

audit:
  level: full
  retention_days: 365
  encryption: tee-sealed         # P1+

lifecycle:
  max_age_days: 90
  ota_upgradeable: true
  auto_rotate: true

applicability:
  vehicle_models: [ET7, ET5, ES8]
  trust_domains: [nio-cockpit]
```

**ASG 形态裁剪 (车规级)**:

```toml
# capabilities.toml (ASG Manifest)
[domain]
type = "cockpit"  # cockpit / driving / vehicle-control

[asg]
subagent = "enabled"             # enabled / disabled
subagent_max_depth = 2
subagent_modes = ["thread", "process"]
cross_domain_outbound = ["driving"]
cross_domain_inbound = ["driving"]

[tee]
backend = "qtee"                  # qtee / optee / hsm
root_key_ref = "tee://qta/manifest-hmac-key"

[resources]
max_ram_mb = 1.5
max_subagents = 5

[principal]
spiffe_id = "spiffe://nio.com/agent/cockpit/prod/triage-bot"
sponsor = "sponsor:abc-corp"
type = "llm-guard-7b"
risk_class = "medium"

[acl.capabilities]
allow = ["nav:read", "nav:reroute", "map:query"]
deny = ["nav:write_persistent", "can:brake"]
```

**状态机**:

```
[*] → Created → Attesting → Active
                      ↓ (失败)
                   Failed → [*]
Active → Suspended → Active (恢复)
Active → Rotating → Active (OTA)
Active → Revoked → Destroyed → [*]
```

#### 3.1.2 认证层 (Attestation)

**POC 跳过, 接口预留**:

```cpp
class AttestationVerifier {
public:
    virtual AttestationResult verify(
        const std::string& pcr_values,
        const std::string& ak_signature,
        const std::string& nonce
    ) = 0;
};

// POC: 永远返回 success
class PoCAttestationVerifier : public AttestationVerifier { ... };

// P1: 真实 TPM 2.0 + IMA 度量链
class TPMAttestationVerifier : public AttestationVerifier { ... };
```

**三域 Attestation 协议选型**:

| 域 | Layer 1 (硬件) | Layer 2 (软件) | 验证时延 |
|----|---------------|----------------|----------|
| 座舱 8295 | TPM 2.0 + AK | IMA + 厂商签名 | < 500ms |
| 智驾 Orin | OP-TEE PTA + HSM | IMA + ASIL-D 度量 | < 500ms |
| 车控 S32G | S32G HSM + 双 TA | 简化度量 (PCR0-2) | < 200ms |

**域间互信**: SPIFFE Federation Bundle (预置 + OTA 刷新)。

#### 3.1.3 凭证层 (核心模块, 详细设计)

**三层凭证体系**:

| 层 | 寿命 | 算法 (POC → 生产) | 存储 | 撤销 |
|----|------|-------------------|------|------|
| L1 持久 | 跟镜像同寿命 (~3 月) | HS256 → ES256 | TEE 持久区 | OTA 整车级撤销 |
| L2 运行 | 1 小时 | HS256 | TEE 易失区 | 自动过期 |
| L3 临时 | 5 分钟 | HS256 | TEE 临时区 | 任务结束 + 短 TTL |

**L3 JWT-SVID 完整字段 (Framework 标准形态)**:

```json
{
  "iss": "spiffe://nio-cockpit",
  "sub": "spiffe://nio-cockpit/sub-agent-9182",
  "act": {
    "sub": "spiffe://nio-cockpit/main-agent-01",
    "profile": "llm-guard-7b-v1.2"
  },
  "aud": ["spiffe://nio-cockpit/nav-tool"],
  "scope": "nav:reroute",
  "task_purpose": "reroute_for_emergency",
  "vehicle_id": "NIO-ET7-001",
  "jti": "uuid-7f8a...",
  "iat": 1734567000,
  "exp": 1734567600
}
```

**ASG Ticket 统一格式 (车规裁剪形态)**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `ticket_id` | u64 | 全局唯一 |
| `agent_id` | str | 主 Agent 或 Sub-Agent ID |
| `parent_id` | str | Sub-Agent 父 ID (主 Agent 为空) |
| `capability` | bitmask | 能力位 (最多 64 种) |
| `issued_at` | u64 (ms) | 颁发时间 |
| `expires_at` | u64 (ms) | 过期时间 |
| `nonce` | 32B | 防重放 |
| `hmac` | 32B | HMAC-SHA256 签名 |
| `depth` | u8 | 0=主, 1+=Sub |
| `task_type` | enum | 任务类型 (Blueprint 模板) |
| `task_id` | str | 任务 ID (审计用) |

**两种格式的关系**:
- **Framework (P0)**: 用 JWT-SVID (标准, 跨域可读)
- **ASG (P0 裁剪)**: 用 Ticket (HMAC 签, 函数调用即可验证, < 1μs)
- **生产 (P2)**: JWT-SVID (域内) + ASG Ticket (车控域极致优化)
- **接口统一**: 业务代码只依赖 `CredentialIssuer` 接口, 不绑具体格式

**凭证生命周期**:

```
[*] → Issued → Active → Expired → [*]
                  ↓
                Revoked → [*]
                  ↓
                Burned (任务结束, TEE 端 delete key) → [*]
```

**关键不变量 (hard invariants)**:

```
1. act claim 必须存在 (L3 委托链)
2. exp - iat ≤ 300 (L3 寿命 ≤ 5min)
3. aud 必须包含目标 service SPIFFE ID
4. vehicle_id 必须存在 (车端特有)
5. depth ≤ 2 (车控域 = 0, 即无 Sub-Agent)
6. capability ⊆ parent.capability (权限单调收敛)
7. task_type ∈ Blueprint 白名单
```

**撤销机制 (POC 实现)**:

```cpp
// 1. 短 TTL (默认兜底)
exp - iat <= 300  // 5 分钟

// 2. 主动撤销 (立即生效)
void revoke(const std::string& jti) {
    revoked_jtis_.insert(jti);
}

// 3. 验证时检查
bool verify(const std::string& token) {
    auto claims = decode(token);
    if (is_revoked(claims.jti)) return false;
    if (claims.exp < now()) return false;
    return verify_signature(token);
}
```

### 3.2 INPUT 模块 (入口过滤)

#### 3.2.1 职责

- 入口数据签名 (防止伪造)
- 参数 schema 校验
- 注入检测 (Prompt Injection)
- PII / 敏感数据脱敏

#### 3.2.2 ASG 实现 (DataGate.input)

```cpp
// DataGate INPUT 核心 API (ASG 8 函数之一)
Result datagate_check_input(
    Source source,           // tool_request / user_input / cloud_sync
    const void* data,
    size_t len
);

// 内部流程:
// 1. source 白名单校验
// 2. schema 校验 (JSON Schema)
// 3. 注入检测 (regex + 规则)
// 4. PII 脱敏 (车架号 / 车主姓名)
// 5. 返回 ALLOW / REDACT / DENY
```

#### 3.2.3 性能指标

| 操作 | 延迟 |
|------|------|
| `datagate_check_input()` | < 10μs (正则 + 长度检查) |
| `datagate_check_output()` | < 20μs (含 PII 脱敏) |
| 端到端工具调用 | < 1ms (含 TEE) |

### 3.3 OUTPUT 模块 (出口过滤)

#### 3.3.1 职责

- 出口数据签名 (防篡改)
- 工具返回完整性验证
- 敏感数据再次脱敏 (LLM 推理后)
- 数据落盘加密

#### 3.3.2 ASG 实现 (DataGate.output)

```cpp
// DataGate OUTPUT 核心 API
Result datagate_check_output(const void* data, size_t len);
Result datagate_sign_output(const void* data, size_t len, uint8_t* sig_out);
bool datagate_verify_input(const SignedBlob& signed_blob);
```

### 3.4 Guard 模块 (策略执行)

**注意**: 在 Framework 中 Guard 是独立模块, 在 ASG 中拆解吸收到 AuthGate ACL + DataGate 串接。

#### 3.4.1 职责

- **Tool 治理**: 调用前 ACL 校验
- **Sub-Agent 派生**: 深度/权限/配额检查
- **条件访问 (Conditional Access)**: 车速/电量/模式
- **Kill Switch**: 紧急熔断 (`auth_revoke_all`)

#### 3.4.2 Sub-Agent 派生检查 (4 道关卡)

```cpp
// ASG 中: 4 道关卡
bool spawn_subagent(const SpawnRequest& req) {
    // 检查 1: depth + 1 ≤ MAX (≤2)
    if (current_depth + 1 > MAX_DEPTH) return false;
    
    // 检查 2: requested_caps ⊆ parent_caps (权限单调收敛)
    if (!is_subset(req.capabilities, parent_caps)) return false;
    
    // 检查 3: 本小时已 spawn N ≤ quota
    if (spawns_this_hour >= max_subagents_per_hour) return false;
    
    // 检查 4: task_type ∈ Blueprint 白名单
    if (!blueprint.task_types.contains(req.task_type)) return false;
    
    return true;
}
```

#### 3.4.3 车控域硬约束 (在 Guard 体现)

```cpp
// 域类型: 强制 sub-agent 关闭
if (domain == "nio-body" || domain == "vehicle-control") {
    if (asg_config.subagent == "enabled") {
        return ERROR("body domain must have subagent=disabled");
    }
}
```

### 3.5 审计模块

#### 3.5.1 审计事件类型

| 事件 | 触发 | 严重度 |
|------|------|--------|
| `agent.registered` | Registry 注册 | info |
| `svid.issued` | L1/L2/L3 颁发 | info |
| `svid.rotated` | 轮转 | info |
| `tool.called` | Tool 调用 | info |
| `auth.failed` | 验签失败 | warn |
| `revocation` | 主动撤销 | warn |
| `attestation.failed` | Attestation 失败 | critical |
| `breakglass.used` | 车控紧急逃生 | critical |
| `kill_switch` | 紧急熔断 | critical |
| `capability.denied` | 越权拒绝 | warn |

#### 3.5.2 审计字段

```cpp
struct AuditEvent {
    std::string event_type;
    std::string jti;               // 唯一 ID
    std::string actor_sub;         // 主 Agent
    std::string subject_sub;       // 凭证主体
    std::string vehicle_id;
    std::string task_purpose;
    std::string tool;              // 调用的 Tool
    std::string tool_params_hash;  // 参数摘要, 不含敏感数据
    int64_t timestamp;             // 硬件时间
    std::string severity;
    std::string source_domain;     // 跨域审计用
    std::string target_domain;     // 跨域审计用
};
```

#### 3.5.3 ASG Ring Buffer

```
容量: 256KB (循环覆盖)
位置: 进程内
持久化: P1+ 上报到云端 (TEE 加密)
保留: ≥ 365 天 (云端)
```

### 3.6 Sub-Agent 双模

| 模式 | 资源 | 隔离 | 凭证 | 适用 |
|------|------|------|------|------|
| **线程** | 极低 (共享地址) | 弱 | L3 (5min) | 短任务 < 30s, 轻量 |
| **裸进程** | 中 (独立地址) | 中 | L2 + L3 | 长任务, 需调高危 Tool |

**派生协议 (RFC 8693 token-exchange)**:

```cpp
std::string derive_l3(
    const std::string& l1_token,         // 主体凭证
    const std::string& sub_agent_id,     // 新 sub-agent ID
    const std::string& task_purpose,
    const std::vector<std::string>& audience
) {
    auto l1_claims = decode(l1_token);
    if (l1_claims.exp < now()) throw std::runtime_error("L1 expired");
    if (active_sub_agents_.size() >= max_sub_agents_) {
        throw std::runtime_error("max sub-agents reached");
    }
    
    return jwt::create()
        .set_issuer(l1_claims.iss)
        .set_subject("spiffe://nio-cockpit/" + sub_agent_id)
        .set_audience(audience)
        .set_issued_at(now())
        .set_expires_at(now() + 5min)
        .set_id(gen_uuid())
        .set_payload_claim("act", jwt::claim({
            {"sub", l1_claims.sub},
            {"profile", l1_claims.profile}
        }))
        .set_payload_claim("task_purpose", task_purpose)
        .set_payload_claim("vehicle_id", l1_claims.vehicle_id)
        .sign(ALGORITHM);
}
```

### 3.7 跨域通信

#### 3.7.1 跨域三原则

1. **默认禁止**, 例外走 XGW
2. 跨域 ticket **不同 ID** (防重放 + 边界清晰)
3. XGW 是**唯一**跨域通道, 所有流量必经审计

#### 3.7.2 跨域 Ticket 字段 (ASG)

```
跨域 ticket = 域内 ticket + 3 个新字段:
  source_domain: str      # 源域
  target_domain: str      # 目标域
  xgw_session_id: u64     # XGW 集中审计 ID
```

#### 3.7.3 XGW 高可用 (P2 引入)

- 双实例 + 选举
- 流量切换 < 100ms
- 跨域流量分流 (座舱 ↔ 智驾, 不走车控)

---

## Part 4 — 三域差异化

### 4.1 总览表

| 维度 | 座舱 (8295+QTEE) | 智驾 (Orin+OP-TEE) | 车控 (S32G+HSM) |
|------|------------------|---------------------|------------------|
| **资源预算** | ~1.5MB RAM | ~1.2MB RAM | **~0.7MB RAM** |
| **ASG 形态** | 完整版 | 标准版 | **极简版** |
| **凭证** | L1+L2+L3 全 | L1+L2+L3 全 | **L1+L2 (无 L3)** |
| **Sub-Agent** | 线程+进程 | 偏进程 | **不启用** |
| **委托链深度** | 2 | 1 | **0** |
| **TEE 后端** | QTEE Trusted App | OP-TEE TA | HSM |
| **跨域通信** | 允许 (去智驾) | 允许 (去座舱/车控) | **禁止 (仅接收)** |
| **OTA 频率** | 高 (周级) | 中 (月级) | 低 (季度级) |
| **审计上报** | 本地 + 上报 | 本地 + 上报 | **本地强审计, 不上报** |
| **编译宏** | `NIOSEC_DOMAIN_COCKPIT` | `NIOSEC_DOMAIN_DRIVING` | `NIOSEC_DOMAIN_VC` |
| **裁剪模块** | 无 | 关跨域 client | 关 sub-agent, 关跨域 client |

### 4.2 域 Manifest 配置 (ASG toml 格式)

**座舱域**:
```toml
[domain]
type = "cockpit"

[asg]
subagent = "enabled"
subagent_max_depth = 2
subagent_modes = ["thread", "process"]
cross_domain_outbound = ["driving"]
cross_domain_inbound = ["driving"]

[tee]
backend = "qtee"
root_key_ref = "tee://qta/manifest-hmac-key"

[resources]
max_ram_mb = 1.5
max_subagents = 5
```

**智驾域**:
```toml
[domain]
type = "driving"

[asg]
subagent = "enabled"
subagent_max_depth = 1            # 比座舱更严
subagent_modes = ["process"]      # 偏进程
cross_domain_outbound = ["cockpit", "body"]
cross_domain_inbound = ["cockpit"]

[tee]
backend = "optee"
root_key_ref = "tee://opta/manifest-hmac-key"

[resources]
max_ram_mb = 1.2
max_subagents = 3
```

**车控域 (极简版)**:
```toml
[domain]
type = "vehicle-control"

[asg]
subagent = "disabled"              # 关键: 关闭
subagent_max_depth = 0
cross_domain_outbound = []        # 关键: 禁止主动跨域
cross_domain_inbound = ["cockpit"] # 仅允许座舱查询

[tee]
backend = "hsm"
root_key_ref = "hsm://slot-3/manifest-hmac"

[resources]
max_ram_mb = 0.7
max_subagents = 0
```

### 4.3 资源预算表

| 域 | 二进制 | RAM | Flash | 启动时间 |
|----|--------|-----|-------|----------|
| 座舱 | 1.2 MB | 1.5 MB | 2.0 MB | 25ms |
| 智驾 | 1.0 MB | 1.2 MB | 1.6 MB | 22ms |
| 车控 | 0.8 MB | 0.7 MB | 1.1 MB | 18ms |

**运行时分布 (座舱版 ASG)**:

| 组件 | RAM 占用 |
|------|----------|
| ACL 内存数组 | 10-30 KB |
| Ticket / SVID 缓存 | 20-50 KB |
| Sub-Agent TLS | 5-10 KB/个 |
| Audit ring buffer | 256 KB |
| AuthGate / DataGate 线程栈 | 8 KB/线程 |
| **总计** | **< 1.5 MB** |

---

## Part 5 — 接口定义

### 5.1 ASG 8 个核心 API (C 函数, 进程内)

```c
// ===== AuthGate (6 个) =====
typedef struct asg_ctx asg_ctx_t;

// 1. 启动期初始化
asg_ctx_t* auth_init(const char* manifest_path);
void auth_destroy(asg_ctx_t* ctx);

// 2. 主 Agent 拿自己 ID
const char* auth_get_self_id(asg_ctx_t* ctx);

// 3. 颁发 ticket (tool / sub-agent / 跨域)
typedef struct {
    enum { TICKET_TOOL, TICKET_SUBAGENT, TICKET_CROSSDOMAIN } kind;
    const char* subject_id;        // sub-agent ID or tool ID
    const char* parent_id;         // 父 Agent ID (主 Agent 为 NULL)
    uint64_t capability;            // bitmask
    uint32_t ttl_sec;               // 5s ~ 5min
    const char* task_type;          // Blueprint 模板
    const char* task_id;            // 任务 ID
    const char* source_domain;      // 跨域用
    const char* target_domain;      // 跨域用
} ticket_spec_t;

ticket_t* auth_issue_ticket(asg_ctx_t* ctx, const ticket_spec_t* spec);

// 4. 验 ticket
typedef enum {
    AUTH_OK = 0,
    AUTH_ERR_EXPIRED = 1,
    AUTH_ERR_REVOKED = 2,
    AUTH_ERR_INVALID_SIG = 3,
    AUTH_ERR_DEPTH_EXCEEDED = 4,
    AUTH_ERR_NO_PERMISSION = 5,
} auth_result_t;

auth_result_t auth_verify_ticket(asg_ctx_t* ctx, const ticket_t* t);

// 5. 撤销单 ticket
void auth_revoke(asg_ctx_t* ctx, uint64_t ticket_id);

// 6. 紧急熔断 (Kill Switch)
void auth_revoke_all(asg_ctx_t* ctx);

// ===== DataGate (4 个) =====
typedef enum {
    DATAGATE_ALLOW = 0,
    DATAGATE_REDACT = 1,
    DATAGATE_DENY = 2,
} datagate_result_t;

datagate_result_t datagate_check_input(
    asg_ctx_t* ctx,
    int source,                     // TOOL_REQUEST / USER_INPUT / CLOUD_SYNC
    const void* data,
    size_t len
);

datagate_result_t datagate_check_output(
    asg_ctx_t* ctx,
    const void* data,
    size_t len
);

datagate_result_t datagate_sign_output(
    asg_ctx_t* ctx,
    const void* data,
    size_t len,
    uint8_t sig_out[32]             // HMAC-SHA256
);

datagate_result_t datagate_verify_input(
    asg_ctx_t* ctx,
    const uint8_t* signed_blob,
    size_t len
);
```

**对比业界 Gateway**: 业界 20-50 个 API, 我们只暴露 8 个, **省 73%**。

### 5.2 gRPC 接口 (Framework 标准, P1 引入)

```protobuf
// file: agent_registry.proto
syntax = "proto3";
package nio.asf.v1;

service AgentRegistry {
  // 注册 Agent
  rpc Register(RegisterRequest) returns (RegisterResponse);
  // 查询 Agent
  rpc Lookup(LookupRequest) returns (LookupResponse);
  // 更新状态
  rpc UpdateStatus(UpdateStatusRequest) returns (UpdateStatusResponse);
  // 撤销 (按 jti)
  rpc Revoke(RevokeRequest) returns (RevokeResponse);
  // 健康检查
  rpc Heartbeat(HeartbeatRequest) returns (HeartbeatResponse);
}

message RegisterRequest {
  string blueprint_id = 1;
  string spiffe_id = 2;
  string vehicle_id = 3;
  string sponsor = 4;
  bytes attestation_evidence = 5;  // P1+ 启用
  string domain = 6;                // nio-cockpit / nio-driving / nio-body
}

message RegisterResponse {
  string registry_id = 1;
  string l1_token = 2;             // 颁发 L1 JWT-SVID
  int64 expires_at = 3;
}

message LookupRequest {
  string spiffe_id = 1;
}

message LookupResponse {
  string registry_id = 1;
  string status = 2;               // active / suspended / revoked
  string blueprint_id = 3;
  repeated string capabilities = 4;
  string sponsor = 5;
  int64 last_heartbeat = 6;
}

message UpdateStatusRequest {
  string registry_id = 1;
  string new_status = 2;           // active / suspended / revoked
  string reason = 3;
}

message UpdateStatusResponse {
  bool success = 1;
}

message RevokeRequest {
  string jti = 1;                  // 按 ticket ID 撤销
  string reason = 2;
}

message RevokeResponse {
  bool success = 1;
  int64 revoke_at = 2;
}

message HeartbeatRequest {
  string registry_id = 1;
  string l1_token = 2;             // 带 L1 验签
}

message HeartbeatResponse {
  bool healthy = 1;
  int64 next_heartbeat_sec = 2;
}
```

```protobuf
// file: tpm_as.proto (Token Service)
syntax = "proto3";
package nio.asf.v1;

service TPMAS {
  // 派生 L3 (RFC 8693 token-exchange)
  rpc DeriveL3(DeriveL3Request) returns (DeriveL3Response);
  // 验证 token
  rpc Verify(VerifyRequest) returns (VerifyResponse);
  // 主动撤销
  rpc Revoke(RevokeRequest) returns (RevokeResponse);
}

message DeriveL3Request {
  string l1_token = 1;              // 主体凭证
  string sub_agent_id = 2;          // 新 sub-agent ID
  repeated string audience = 3;     // 目标 service SPIFFE ID
  string task_purpose = 4;
  uint32 ttl_sec = 5;               // 默认 300 (5min)
}

message DeriveL3Response {
  string l3_token = 1;
  int64 expires_at = 2;
  string jti = 3;
}

message VerifyRequest {
  string token = 1;
  string expected_audience = 2;     // 可选
}

message VerifyResponse {
  bool valid = 1;
  string sub = 2;
  string act_sub = 3;               // 委托链
  string task_purpose = 4;
  string vehicle_id = 5;
  int64 exp = 6;
  string error = 7;                 // 失败原因
}
```

```protobuf
// file: cross_domain.proto (XGW)
syntax = "proto3";
package nio.asf.v1;

service CrossDomainGateway {
  // 跨域转发 (集中审计)
  rpc Forward(ForwardRequest) returns (ForwardResponse);
  // 列出当前活跃跨域会话 (审计查询)
  rpc ListSessions(ListSessionsRequest) returns (ListSessionsResponse);
}

message ForwardRequest {
  string source_domain = 1;         // nio-cockpit
  string target_domain = 2;         // nio-driving
  string ticket = 3;                // 跨域 ticket
  string task_type = 4;
  bytes payload = 5;
  uint64 xgw_session_id = 6;        // XGW 生成
}

message ForwardResponse {
  bytes payload = 1;
  string ticket = 2;                // 目标域的本地 ticket
  int64 expires_at = 3;
}

message ListSessionsRequest {
  uint64 since_ts = 1;              // 时间范围
}

message ListSessionsResponse {
  repeated Session sessions = 1;
}

message Session {
  uint64 xgw_session_id = 1;
  string source_domain = 2;
  string target_domain = 3;
  string ticket = 4;
  int64 timestamp = 5;
  bool success = 6;
}
```

### 5.3 错误码

| 错误码 | 含义 | 严重度 |
|--------|------|--------|
| `AUTH_OK` | 成功 | - |
| `AUTH_ERR_EXPIRED` | Ticket 过期 | warn |
| `AUTH_ERR_REVOKED` | 已撤销 | warn |
| `AUTH_ERR_INVALID_SIG` | 签名无效 | **critical** |
| `AUTH_ERR_DEPTH_EXCEEDED` | 委托链超深 | warn |
| `AUTH_ERR_NO_PERMISSION` | 越权 | warn |
| `AUTH_ERR_BODY_DOMAIN_NO_SUB` | 车控域拒绝 sub-agent | critical |
| `AUTH_ERR_QUOTA_EXCEEDED` | 配额超限 | warn |
| `AUTH_ERR_TASK_NOT_WHITELISTED` | task_type 不在白名单 | warn |
| `DATAGATE_ALLOW` | 通过 | - |
| `DATAGATE_REDACT` | 脱敏通过 | info |
| `DATAGATE_DENY` | 拒绝 | warn |

### 5.4 数据结构 (C, 嵌入式)

```c
// Ticket 结构 (ASG 紧凑形态)
typedef struct {
    uint64_t ticket_id;             // 全局唯一
    char agent_id[64];              // 主 Agent 或 Sub-Agent ID
    char parent_id[64];             // 父 ID (主 Agent 为空)
    uint64_t capability;            // bitmask
    uint64_t issued_at_ms;          // 颁发时间
    uint64_t expires_at_ms;         // 过期时间
    uint8_t nonce[32];              // 防重放
    uint8_t hmac[32];               // HMAC-SHA256
    uint8_t depth;                  // 0=主, 1+=Sub
    char task_type[32];             // Blueprint 模板
    char task_id[64];               // 任务 ID
} ticket_t;

// Audit 事件 (简版)
typedef struct {
    uint64_t event_id;
    uint64_t timestamp_ms;
    char event_type[32];            // "svid.issued" / "tool.called" / ...
    char actor_sub[128];
    char subject_sub[128];
    char vehicle_id[32];
    char tool[32];
    uint8_t severity;               // 0=info, 1=warn, 2=critical
} audit_event_t;
```

---

## Part 6 — 凭证格式 (JWT-SVID vs ASG Ticket)

### 6.1 两种格式的对比

| 维度 | JWT-SVID (Framework) | ASG Ticket (车规) |
|------|---------------------|---------------------|
| 编码 | JSON | C struct |
| 签名 | ES256 (生产) / HS256 (POC) | HMAC-SHA256 |
| 体积 | ~700 B | ~250 B |
| 验证延迟 | ~50 μs | < 1 μs |
| 跨域可读 | ✅ 任何服务可验 | ❌ 仅 ASG 进程内 |
| 标准化 | SPIFFE 规范 | 内部 |
| 适用 | 域间 / 域内通用 | **车控域 + 域内高频调用** |

### 6.2 统一接口

```cpp
class CredentialIssuer {
public:
    virtual std::string issue(
        const std::string& sub,
        const std::string& parent_id,    // 委托链
        uint64_t capability,
        uint32_t ttl_sec,
        const std::string& task_type,
        const std::string& task_id
    ) = 0;
    
    virtual bool verify(const std::string& token) = 0;
    virtual void revoke(const std::string& ticket_id) = 0;
};

// Framework 实现
class JWTSVIDIssuer : public CredentialIssuer { ... };

// ASG 实现 (车规裁剪)
class ASGTicketIssuer : public CredentialIssuer { ... };

// 业务代码只依赖接口, 不依赖实现
```

### 6.3 混用策略

| 场景 | 用 JWT-SVID | 用 ASG Ticket |
|------|-------------|----------------|
| 域内 LLM ↔ Tool 频繁调用 | | ✅ |
| 域内 Sub-Agent 派生 | | ✅ (父 + 子都用 Ticket) |
| 域内跨进程通信 (gRPC) | ✅ | |
| **跨域通信** (座舱 ↔ 智驾) | ✅ | |
| **车控域** (资源极紧) | | ✅ (强制) |
| Attestation 结果传递 | ✅ | |

---

## Part 7 — 关键流程

### 7.1 启动流程

```
1. systemd 启动 ASG 进程
2. auth_init(manifest_path):
   a. 读 manifest.toml + manifest.hmac
   b. TEE 验签 (HMAC-SHA256)
   c. 验签失败 → exit 1 (启动失败, 系统重启)
   d. 解析 ACL → 内存数组
   e. 加载 Sub-Agent 配置
   f. TEE 加载 L1 持久密钥
   g. 颁发 self-ticket (L1 持久身份)
3. Tool 进程注册:
   a. Tool → ASG.register(tool_id, capabilities)
   b. ASG 颁发 tool ticket
   c. Tool → ready
4. ASG 进入主循环
```

### 7.2 工具调用完整流程

```
1. LLM 推理输出 tool_call JSON
2. Main: cap_check_tool(agent_id, tool)
   → AuthGate 查内存 ACL (O(1) hash 查找) → ALLOW
3. Main: issue_tool_ticket(tool, params)
   → AuthGate → TEE HMAC → 返回 signed_ticket
4. Main: datagate_check_input("tool_request", params)
   → DataGate 注入检测 + schema 校验 → ok
5. Main: HTTP POST {tool, params, ticket} → Tool
6. Tool: verify ticket (HMAC + TTL) → ok
7. Tool: 执行
8. Tool: datagate_sign_output(result) → signed_result
9. Tool → Main: signed_result
10. Main: datagate_check_output(result) → ok
11. Main: verify_ticket_use(ticket_id) → 更新使用计数
12. Main → LLM: 喂回 result
```

### 7.3 Sub-Agent 派生流程

```
1. LLM 推理生成 spawn_subagent JSON
2. Out: schema 校验 + task_type 白名单
3. Auth: 4 道关卡
   a. depth + 1 ≤ MAX (≤2)
   b. requested_caps ⊆ parent_caps
   c. 本小时已 spawn N ≤ quota
   d. task_type ∈ Blueprint 白名单
4. 通过 → 颁发 sub-ticket (含 parent_id, depth)
5. 启动 Sub-Agent:
   - 线程模式: pthread_create(subagent_thread)
   - 裸进程模式: fork+exec (P0+)
6. Sub-Agent 业务循环:
   - cap_check (带 sub_ticket)
   - tool call
7. Sub-Agent 结束:
   - TEE 端 delete ephemeral key
   - 销毁 sub_ticket
   - pthread_exit / process exit
```

### 7.4 跨域通信流程

```
1. 座舱 Agent: call_driving_agent("lane-keep-bot", task)
2. 座舱 ASG:
   a. 检查 cross_domain_outbound 包含 driving
   b. 检查申请能力 ⊆ 当前 agent
   c. 颁发跨域 ticket (新 ID, 含 source_domain / target_domain)
3. 座舱 ASG → XGW: HTTPS POST {target_domain, ticket, task}
4. XGW:
   a. 集中审计 (log: src, dst, ticket, task)
   b. 速率限制检查
   c. 转发到智驾 ASG
5. 智驾 ASG:
   a. 验 ticket HMAC
   b. 检查 source_domain ∈ cross_domain_inbound
   c. 颁发本地 ticket (新 ID)
6. 智驾 ASG 执行任务
7. 响应原路返回
```

**关键**: 跨域 ticket 与域内 ticket **不同 ID** (防重放 + 边界清晰); XGW 是**唯一**的跨域通道。

### 7.5 OTA 升级流程

```
1. OTA 下载新 manifest + binary
2. OTA: cosign verify (镜像签名)
3. OTA: 写到 staging 分区
4. OTA: signal(SIGUSR1) "新版本就绪"
5. ASG:
   a. 检查当前活跃 sub-agent, 等待完成
   b. graceful shutdown (拒绝新 ticket)
   c. 等待 in-flight ticket 验证完
   d. TEE 加载新 HMAC root
   e. 读新 manifest, TEE 验签
   f. 加载新 ACL
   g. 重新颁发 self-ticket
6. ASG → OTA: ready
7. OTA: 原子切换 staging → active
8. OTA: restart (systemd)
9. ASG 用新 manifest 启动
```

**关键**: OTA 期间**不停服务**——旧 manifest 处理完 in-flight 请求, 新 manifest 接力。

### 7.6 异常处理与 Kill Switch

| 场景 | 处理 |
|------|------|
| Ticket TTL 过期 | DENY (expired), 重新 issue |
| 越权调用 | DENY, 写审计 (high_risk_alert) |
| 委托链超深 | DENY (depth_exceeded) |
| 车控域派生 sub-agent | DENY (body_domain_no_sub), critical |
| **紧急 Kill Switch** | `auth_revoke_all()`: 清空所有 ticket, TEE 清空 ephemeral key, SHUTDOWN signal |

---

## Part 8 — 威胁模型

### 8.1 T-01..T-10 完整 (Framework)

| 编号 | 威胁 | OWASP 来源 | 防御 |
|------|------|-----------|------|
| T-01 | Excessive Agency | ASI01 / LLM06 | L3 scope + OpenFGA |
| T-02 | Prompt Injection | ASI02 / LLM01 | Guard 模块 |
| T-03 | Identity Spoofing | ASI03 | JWT-SVID 验签 + Attestation |
| T-04 | Tool Misuse | ASI04-07 | L3 scope + Conditional Access |
| T-05 | Supply Chain | ASI08 | 二进制签名 + PCR 白名单 |
| T-06 | Data Leakage | ASI09 / LLM02 | audit 加密 + TEE 隔离 |
| T-07 | Untrusted Output | LLM05 | Guard 模块 |
| T-08 | DoS via Agent | ASI10 | 资源配额 (Blueprint) |
| T-09 | Cascading Failure | 车端特有 | break-glass + 强审计 |
| T-10 | Audit Gap | 车端特有 | TEE 不可篡改日志 |

### 8.2 T-1..T-5 精简 (ASG 资源极紧时)

| ID | 威胁 | 主防点 | 对应 T-XX |
|----|------|--------|-----------|
| T-1 | 身份伪造 | TEE 私钥 + HMAC 验签 | T-03 + T-05 |
| T-2 | 越权调用 | AuthGate 查 ACL (manifest HMAC 防篡改) | T-01 + T-04 |
| T-3 | 数据外泄 / 中毒 | DataGate 入口出口双向过滤 | T-02 + T-06 + T-07 |
| T-4 | 委托链扩张 | depth + 权限单调收敛 | T-04 + T-09 |
| T-5 | 凭证重放 | 短 TTL + nonce + 时钟校验 | T-08 |

**收敛说明**: 物理层 / DoS / 供应链等威胁并入 T-1 或 T-3, 简化模型。

### 8.3 fail-secure 原则

**任何安全失败必须降级到更安全模式**（不允许降级到不安全）。

降级路径: 重试 → 重启 Agent → 域级降级 → 整车安全模式（车控 ASIL-D emergency stop）。

---

## Part 9 — 实施 Roadmap

### 9.1 POC (2 周)

| 周 | 目标 | 产出 |
|----|------|------|
| W1 | ASG 8 API 骨架 + JWT-SVID 签发验签 | libnio_asf.so + 单元测试 |
| W2 | Sub-Agent 派生 + 跨域简化 + Demo | 端到端 demo |

### 9.2 P1 (4 周) — ASG 完整版 + Framework 协议化

| 周 | 目标 | 产出 |
|----|------|------|
| W3 | gRPC 服务化 (Agent Registry + TPM-AS) | 跨进程通信 |
| W4 | Blueprint schema + OCI 仓库 + cosign | 模板化 |
| W5 | Attestation 简化版 (TPM 2.0) | 真实度量 |
| W6 | OpenFGA 集成 (替换 if-else) | 真实授权 |

### 9.3 P2 (4 周) — 生产化

| 周 | 目标 | 产出 |
|----|------|------|
| W7 | mTLS (X.509) 通道加密 | 域间安全通信 |
| W8 | 真实 Registry (gRPC + SQLite) | 跨域身份服务 |
| W9 | 审计加密 + 上报 | 长期保留 |
| W10 | 车控域 Lite 版 | 三域差异化 |

### 9.4 P3+ (合规 + 远期)

- ISO 21434 / R155 合规对接
- 渗透测试 + 第三方审计
- C509 / CWT PoC 评估

### 9.5 关键里程碑

- **M1 (W1 末)**: ASG 8 API 单测通过, ACL 查表 < 1μs
- **M2 (W2 末)**: Sub-Agent + 跨域通 (POC 完成)
- **M3 (W4 末)**: gRPC + Registry 跑通
- **M4 (W6 末)**: Attestation + OpenFGA 集成
- **M5 (W10 末)**: 三域差异化构建完成, 性能达标

---

## Part 10 — 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| KMSS 接口变更 | Registry 集成受影响 | 提前对齐, P0 冻结接口 |
| 车控域资源评估偏差 | Lite 版跑不起来 | P2 阶段做 S32G 实测 |
| Attestation 启动开销 | 影响 50Hz 实时性 | 缓存 Attestation 结果 |
| Federation Bundle 离线过期 | 域间互信失效 | 7 天 grace + 充电时强制刷新 |
| OWASP 映射过松 | 威胁覆盖不全 | P1 阶段由安全团队独立审计 |
| OpenFGA 性能不达标 | 影响 50Hz 决策 | P0 benchmark, > 1ms 切本地缓存 |
| C509 规范不稳定 | 切车控域后规范变更需返工 | P3 之前持续观察; POC/P1/P2 不引入 |
| X.509 证书管理复杂度 | P2 引入时拖慢进度 | POC 跳过, P2 评估是否复用 KMSS |
| POC 范围蔓延 | POC 引入 X.509 等导致延期 | 严格遵守 POC 范围声明 |
| 跨域 Gateway 单点 | 跨域通信全断 | Gateway HA (双实例 + 选举) |
| LLM 结构化输出不稳定 | Sub-Agent spawn 失败率高 | Prompt 工程强化 + 重试 + 降级 |

---

## Part 11 — 长期演进

### 11.1 X.509 / mTLS (P2)

- **域间通信**: 座舱 ↔ 智驾 gateway 用 mTLS, JWT-SVID 在通道内透传
- **长连接**: 智驾 Agent 订阅感知流
- **车控传统路径**: 与 AUTOSAR SecOC 共存
- **TPM Attestation**: TPM 2.0 EK / AK 证书本身就是 X.509

### 11.2 C509 / CWT (P3+)

- **C509** (CBOR X.509): 体积比 DER 小 50-70%, 适合车控域
- **CWT** (CBOR Web Token): 替代 JWT-SVID, 体积更小
- **COSE 生态**: RFC 9052 / RFC 8392

**不立刻引入的原因**:
- C509 仍在 IETF 草案, 规范稳定性待验证
- 工具链不成熟, 调试 / 运维成本高
- 跨域要网关翻译
- 审计 / 合规可能不认非 RFC 标准

---

## 附录 A — 术语表

| 术语 | 含义 |
|------|------|
| **ASG** | AgentSec Gateway, 嵌入式车规单进程形态 |
| **Framework** | 完整协议栈, 顶层设计 |
| **JWT-SVID** | JWT 形式 SPIFFE 身份证明 |
| **SPIFFE** | 工作负载身份标准 |
| **Trust Domain** | 信任域 (座舱/智驾/车控各一个) |
| **`act` claim** | RFC 8693 委托链字段 |
| **L1 / L2 / L3** | 持久 / 运行 / 临时层凭证 |
| **Sub-Agent** | 主 Agent 派生的子任务代理 |
| **KMSS** | NIO 内部 Key Management Service System |
| **NTS** | NIO 内部 Network/Telematics Service |
| **QTEE** | Qualcomm TEE (座舱域) |
| **OP-TEE** | Open Portable TEE (智驾域) |
| **HSM** | Hardware Security Module (车控域核心) |
| **XGW** | Cross-Domain Gateway, 跨域集中代理 |
| **Ticket** | ASG 紧凑凭证格式 (HMAC 签) |
| **Blueprint** | Agent 任务模板 (Entra 借鉴) |
| **Sponsor** | Agent 业务负责人 |

---

## 附录 B — 文档关系

```
┌──────────────────────────────────────────────────────────┐
│  research/                                                │
│  ├── llm-agent-delegation-research-2026/                 │
│  │  └── README.md          ← 调研依据 (四梯队资料)         │
│  ├── nio-asg-design/                                     │
│  │  ├── architecture.md    ← ASG v0.1 (车规单进程)        │
│  │  └── architecture-diagrams.md  ← 配套图                │
│  └── nio-vehicle-ai-agent-security-framework-design-v1/  │
│     ├── framework-design-v1.html   ← 评审稿 (含 mermaid)  │
│     ├── framework-design-v1.md     ← Coding Agent spec    │
│     └── framework-design-v2-integrated.md  ← 本文件       │
│        (整合 Framework v1.1 + ASG v0.1)                   │
└──────────────────────────────────────────────────────────┘
```

**本文档 = Framework v1.1 + ASG v0.1 整合**:
- 顶层: Framework 协议栈 (JWT-SVID / gRPC / 3 层凭证)
- 落地: ASG 形态 (单进程 + 2 Gate / HMAC Ticket / 8 API)
- 关系: ASG 是 Framework 的车规级实现

---

## 附录 C — 参考资料

- **Framework v1.1**: `framework-design-v1.html` (本目录, 含 10 个 mermaid)
- **ASG v0.1**: `../nio-asg-design/architecture.md` (15.8 KB, 完整设计稿)
- **调研**: `../llm-agent-delegation-research-2026/README.md`
- **核心协议**:
  - RFC 8693 (Token Exchange): https://datatracker.ietf.org/doc/html/rfc8693
  - SPIFFE Federation: https://spiffe.io/docs/latest/spiffe-about/spiffe-federation/
  - JWT-SVID: https://github.com/spiffe/spiffe/blob/main/standards/JWT-SVID.md
  - OIDC-A 1.0: https://arxiv.org/abs/2509.25974
  - OpenFGA: https://openfga.dev
  - jwt-cpp: https://github.com/Thalhammer/jwt-cpp

---

## 附录 D — 修订历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **v2.0** | 2026-07-21 | 整合 Framework v1.1 + ASG v0.1, 给出模块详细设计 + 完整接口定义 (gRPC + ASG 8 API + 数据结构) |
| v1.1 | 2026-07-20 | Framework 完整设计稿 + POC 范围声明 + X.509/C509 长期演进 |
| v1.0 | 2026-07-20 | Framework 初始评审稿 |
| ASG v0.1 | 2026-07-20 | 嵌入式车规单进程形态 (niosec-devs 输出) |
