# 车端 AI Agent IAM 综合设计文档

> **版本**: v1.0
> **日期**: 2026-07-23
> **整合自**:
> - `ai-agent-security-iam/report.md` — 通用 Agent IAM 基础概念、大厂方案
> - `vehicle-edge-ai-security/report.md` — 车端场景特有设计
> - `vehicle-iam-llm-guard-whitepaper/whitepaper.md` — 整合知识体系
> - `nio-vehicle-ai-agent-security-framework-design-v1/framework-design-v2-integrated.md` — 工程实施规格

---

## 目录

- [第 1 章 — 为什么车端 IAM 是独立问题](#第-1-章--为什么车端-iam-是独立问题)
- [第 2 章 — 核心概念](#第-2-章--核心概念)
- [第 3 章 — 车端场景与 Agent 类型](#第-3-章--车端场景与-agent-类型)
- [第 4 章 — 身份体系设计](#第-4-章--身份体系设计)
- [第 5 章 — 三层凭证体系](#第-5-章--三层凭证体系)
- [第 6 章 — 认证与 Attestation](#第-6-章--认证与-attestation)
- [第 7 章 — 授权体系](#第-7-章--授权体系)
- [第 8 章 — 委托链](#第-8-章--委托链)
- [第 9 章 — 跨域互信](#第-9-章--跨域互信)
- [第 10 章 — 接口定义](#第-10-章--接口定义)
- [第 11 章 — 业界平台对标](#第-11-章--业界平台对标)
- [附录 A — 术语表](#附录-a--术语表)

---

## 第 1 章 — 为什么车端 IAM 是独立问题

### 1.1 传统 IAM 对 Agent 场景完全失效

传统 IAM 的隐含假设是**主体 = 人**。AI Agent 出现后这些假设全部打破：

| 传统假设 | Agent 场景的现实 |
|---|---|
| 主体是人，需要 MFA | Agent 7×24 运行，无法使用 MFA |
| 凭据长期稳定 | Agent 生命周期短，需自动轮换 |
| 权限按"角色"静态分配 | 权限按"任务"动态申请 |
| 一个用户 ≈ 一个身份 | 一个业务可能调用几百个 Agent |
| 出问题可重置密码 | Agent 出问题需"终止开关" |

### 1.2 车端使问题更难：四重叠加约束

通用云端 Agent IAM 方案只能借用一半，另一半必须靠车端特有机制补足：

| 维度 | 云端 Agent | 车载端侧 | 影响 |
|---|---|---|---|
| **失效后果** | 数据泄露、服务降级 | 人身伤亡 | 必须 ASIL-D 级安全设计 |
| **网络依赖** | 默认联网 | 经常离线 / 弱网 | IAM 不能依赖云端"实时兜底" |
| **资源** | 算力无限 | 100W 功耗上限 | 安全护栏空间被压缩 |
| **物理可接触** | 数据中心上锁 | 攻击者可接触整车 | 密钥需存 HSM/TEE，防物理提取 |

### 1.3 车端 IAM 的三层额外约束

1. **车规标准强制合规**：ISO 21434（网络安全）、ISO 26262（功能安全）、UN R155/R156（法规）
2. **跨域身份联邦**：座舱域（QNX/Linux）、智驾域（RTOS）、车身域（AUTOSAR）身份模型各异
3. **密钥长寿命**：车寿命 10–15 年，密钥轮换策略必须超长期规划

---

## 第 2 章 — 核心概念

### 2.1 NHI（Non-Human Identity）

Agent 是 **"NHI 一等公民"**，不是"借用人的权限"：

| 维度 | 人 (User) | Agent (NHI) |
|------|-----------|-------------|
| 标识 | 用户名/邮箱/手机 | **SPIFFE ID** (`spiffe://nio-cockpit/...`) |
| 认证 | 密码/生物/2FA | **JWT-SVID + Attestation** |
| 凭证 | OAuth Token | **三层凭证 (L1/L2/L3)** |
| 授权 | RBAC | **OpenFGA 关系型 + Least Agency** |
| 生命周期 | 离职/转岗 | `active → suspended → revoked → destroyed` |
| 责任追溯 | 用户本人 | **追溯到 Sponsor（业务担保人）** |

### 2.2 Least Agency（最小代理权限）

类比"最小权限（Least Privilege）"，是 Agent 时代的核心安全原则：

```
传统:  Least Privilege (最小权限) → RBAC
Agent: Least Agency  (最小代理) → scope + task_purpose + risk_class + depth ≤ 2
```

**4 个维度**：

| 维度 | 规则 | 示例 |
|------|------|------|
| **能力维度** | scope 必须最小 | `nav:reroute` 而非 `nav:*` |
| **时间维度** | TTL 必须最短 | L3 ≤ 5 分钟 |
| **目的维度** | task_purpose 白名单匹配 | `reroute_for_emergency` |
| **深度维度** | 委托链 depth ≤ 2 | 车控域强制 depth = 0 |

### 2.3 Agent IAM 六大核心能力（业界共识）

1. **独立身份**：Agent 不借用人的权限，拥有一等公民身份
2. **身份绑定（Identity Binding）**：与用户/委托人/模型/代码做密码学绑定
3. **最小代理权限（Least Agency）**：每次任务按需申请最小权限，用完即废
4. **生命周期管理**：创建 → 授权 → 轮换 → 回收，全链路可审计
5. **终止开关（Kill Switch）**：异常时全局注销（global revocation），立即撤销所有 token
6. **可审计性**：每次工具调用关联到"哪个 Agent → 谁授权 → 哪段输入 → 为什么"

---

## 第 3 章 — 车端场景与 Agent 类型

### 3.1 数字车钥匙：IAM 的"消费级"基础

数字车钥匙是车端 IAM 最基础的落地形态。

**主流标准**：

| 标准 | 技术 | 代表厂商 |
|------|------|---------|
| **CCC Digital Key 3.0** | BLE + UWB 厘米级定位 | 宝马、蔚来、小鹏、极氪、比亚迪 |
| **Apple Car Key** | NFC + UWB | 宝马、奥迪、保时捷、奔驰 |
| **华为 HarmonyOS Wallet Key** | 华为生态 | 多国产品牌 |
| **IIFAA 数字车钥匙** | 金融级加密 + 独立芯片 | 中国市场 |
| **ICCOA** | 跨厂商协议 | 中国通信院标准 |

**关键安全机制**：
- **Secure Element（SE）**：密钥存入 iPhone Secure Enclave / 华为 InSE 等独立硬件
- **UWB 厘米级定位**：防中继攻击（Relay Attack）
- **低电模式**：手机关机 5 小时仍可解锁
- **活体检测**：Face ID / 指纹认证
- **细粒度权限**：可限制借车人最高速度、区域、音量等

### 3.2 车端 AI Agent 类型矩阵

| Agent 类型 | 身份类型 | 安全需求 |
|---|---|---|
| **驾驶员 Agent**（智驾系统）| 物理用户 + 数字孪生 | 与驾驶员绑定，可被切换/禁用 |
| **座舱 Agent**（理想同学、小艺、SIMO）| 个人身份 + 家庭成员 | 隐私保护、儿童模式 |
| **云端调度 Agent**（云端下发指令给车）| 服务身份 + 委托链 | 双向认证 + 指令时效校验 |
| **车云 Agent**（OTA 更新、数据回传）| 设备身份 + PKI 证书 | 设备证书、签名验证 |
| **多智能体调度**（底盘、智驾、座舱跨域）| 域间身份 | 域隔离 + 安全通信 |

### 3.3 车端 IAM 六大核心挑战

1. **跨域身份联邦**：座舱域（QNX/Linux）、智驾域（RTOS）、车身域（AUTOSAR）身份模型不同
2. **离线认证**：网络不可用时仍能验证身份（不能依赖云端 IdP）
3. **密钥生命周期**：车寿命 10–15 年，密钥轮换策略必须长期规划
4. **多模态认证**：人脸 + 声纹 + 指纹 + 行为特征组合
5. **特殊人群**：儿童与老人的生物特征退化问题
6. **跨厂商迁移**：车主换品牌时数字钥匙 / 数据 / 偏好如何迁移

### 3.4 域控制器时代的域内 IAM

现代汽车采用域架构（中央计算 + 区域控制器），域间通信需独立 IAM：

```
┌──────────────────────────────────────────────┐
│            中央计算单元（CCU）                │
│   ┌────────┐  ┌────────┐  ┌────────┐          │
│   │ 智驾域 │  │ 座舱域 │  │ 车身域 │          │
│   │ ASIL-D │  │ ASIL-B │  │ ASIL-A │          │
│   └───┬────┘  └───┬────┘  └───┬────┘          │
│       │           │           │               │
│       │  ┌────────┴────────┐  │               │
│       └──┤  TSN 以太网 +   ├──┘               │
│          │  SOA 服务总线   │                  │
│          │  + mTLS 双向认证│                  │
│          └─────────────────┘                  │
└──────────────────────────────────────────────┘
```

- **SOA + mTLS**：服务间通信用双向 TLS，每个服务有独立证书
- **域隔离**：硬件防火墙 + 内核隔离（如 NVIDIA Drive OS 分区）
- **审计日志**：所有域间调用记录到 TEE（Trusted Execution Environment）

---

## 第 4 章 — 身份体系设计

### 4.1 三个核心对象

| 对象 | 角色 | 维护方 | POC 状态 |
|------|------|--------|----------|
| **Blueprint** | Agent 模板（如 `nav-reroute-agent-v1`）| 车厂 Sponsor | 内存常量 |
| **Registry Record** | 实例化后的运行时身份 | Agent Registry（TEE 内）| 内存对象 |
| **L1 JWT-SVID** | 实体 Agent 运行时凭证 | TPM-AS | POC 实现 |

### 4.2 Blueprint 字段定义

参考 SPIRE Workload Entry + 车端扩展：

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

attestation:                       # P1+ 引入
  min_pcr_policy: "pcr0-7:strict"
  binary_signature_required: true
  hsm_key_required: true
  refresh_interval_sec: 3600

audit:
  level: full
  retention_days: 365
  encryption: tee-sealed           # P1+

lifecycle:
  max_age_days: 90
  ota_upgradeable: true
  auto_rotate: true

applicability:
  vehicle_models: [ET7, ET5, ES8]
  trust_domains: [nio-cockpit]
```

### 4.3 ASG Manifest 配置（车规裁剪形态）

```toml
# capabilities.toml (ASG Manifest)
[domain]
type = "cockpit"   # cockpit / driving / vehicle-control

[asg]
subagent = "enabled"
subagent_max_depth = 2
subagent_modes = ["thread", "process"]
cross_domain_outbound = ["driving"]
cross_domain_inbound  = ["driving"]

[tee]
backend = "qtee"                   # qtee / optee / hsm
root_key_ref = "tee://qta/manifest-hmac-key"

[resources]
max_ram_mb   = 1.5
max_subagents = 5

[principal]
spiffe_id  = "spiffe://nio.com/agent/cockpit/prod/triage-bot"
sponsor    = "sponsor:abc-corp"
type       = "llm-guard-7b"
risk_class = "medium"

[acl.capabilities]
allow = ["nav:read", "nav:reroute", "map:query"]
deny  = ["nav:write_persistent", "can:brake"]
```

### 4.4 Agent 生命周期状态机

```
[*] → Created → Attesting → Active
                      ↓ (失败)
                   Failed → [*]
Active → Suspended → Active (恢复)
Active → Rotating  → Active (OTA 升级)
Active → Revoked   → Destroyed → [*]
```

**5 大生命周期原则**（参考 NIST Identity Management for Agentic AI）：

| 原则 | 说明 |
|------|------|
| **Identification** | 每个 Agent 有独立 ID（SPIFFE ID） |
| **Authentication** | Agent 本身能密码学证明自己 |
| **Authorization** | 委托链 + 能力清单（Blueprint 约束） |
| **Accountability** | 审计追溯到 Sponsor，而非 Agent 本身 |
| **Lifecycle** | 有生有灭，不留 zombie agent |

---

## 第 5 章 — 三层凭证体系

### 5.1 三层对比

| 层 | 寿命 | 算法（POC → 生产）| 标准 | 存储 | 撤销 |
|----|------|-------------------|------|------|------|
| **L1 持久层** | 跟镜像同寿命（~3 月）| HS256 → ES256 | SPIFFE + JWT-SVID | TEE 持久区 | OTA 整车级撤销 |
| **L2 运行层** | 1 小时 | HS256 | RFC 8693 + JWT-SVID | TEE 易失区 | 自动过期 |
| **L3 临时层** | 5 分钟 | HS256 | RFC 8693 `act` claim | TEE 临时区 | 任务结束 + 短 TTL |

### 5.2 L3 JWT-SVID 完整字段（车端定制版）

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

**车端特有字段说明**：

| 字段 | 说明 |
|------|------|
| `act.profile` | LLM 模型版本（车端有多规模 LLM: 30B / 7B / 0.1B） |
| `task_purpose` | 任务目的，用于条件访问白名单匹配 |
| `vehicle_id` | 车辆标识，用于审计追溯 |

### 5.3 ASG Ticket 格式（车规裁剪形态）

| 字段 | 类型 | 说明 |
|------|------|------|
| `ticket_id` | u64 | 全局唯一 |
| `agent_id` | str | 主 Agent 或 Sub-Agent ID |
| `parent_id` | str | Sub-Agent 父 ID（主 Agent 为空）|
| `capability` | bitmask | 能力位（最多 64 种）|
| `issued_at` | u64 (ms) | 颁发时间 |
| `expires_at` | u64 (ms) | 过期时间 |
| `nonce` | 32B | 防重放 |
| `hmac` | 32B | HMAC-SHA256 签名 |
| `depth` | u8 | 0=主 Agent，1+=Sub-Agent |
| `task_type` | enum | 任务类型（Blueprint 模板）|
| `task_id` | str | 任务 ID（审计用）|

### 5.4 两种凭证格式对比与混用策略

| 维度 | JWT-SVID（Framework）| ASG Ticket（车规）|
|------|---------------------|---------------------|
| 编码 | JSON | C struct |
| 签名 | ES256（生产）/ HS256（POC）| HMAC-SHA256 |
| 体积 | ~700 B | ~250 B |
| 验证延迟 | ~50 μs | **< 1 μs** |
| 跨域可读 | ✅ 任何服务可验 | ❌ 仅 ASG 进程内 |
| 标准化 | SPIFFE 规范 | 内部定义 |
| 适用场景 | 域间 / 域内跨进程 | **车控域 + 域内高频调用** |

**混用策略**：

| 场景 | JWT-SVID | ASG Ticket |
|------|----------|------------|
| 域内 LLM ↔ Tool 高频调用 | | ✅ |
| 域内 Sub-Agent 派生 | | ✅ |
| 域内跨进程通信（gRPC）| ✅ | |
| 跨域通信（座舱 ↔ 智驾）| ✅ | |
| **车控域**（资源极紧）| | ✅（强制）|
| Attestation 结果传递 | ✅ | |

### 5.5 凭证关键不变量

```
1. act claim 必须存在（L3 委托链必选）
2. exp - iat ≤ 300（L3 寿命 ≤ 5 分钟）
3. aud 必须包含目标 service 的 SPIFFE ID
4. vehicle_id 必须存在（车端特有，审计必须）
5. depth ≤ 2（车控域 = 0，即车控域无 Sub-Agent）
6. capability ⊆ parent.capability（权限单调收敛）
7. task_type ∈ Blueprint 白名单
```

### 5.6 撤销机制

```cpp
// 1. 短 TTL（默认兜底）
exp - iat <= 300  // 5 分钟

// 2. 主动撤销（立即生效）
void revoke(const std::string& jti) {
    revoked_jtis_.insert(jti);
}

// 3. 验证时检查
bool verify(const std::string& token) {
    auto claims = decode(token);
    if (is_revoked(claims.jti)) return false;
    if (claims.exp < now())     return false;
    return verify_signature(token);
}

// 4. Kill Switch：紧急全局撤销
void auth_revoke_all(asg_ctx_t* ctx);
```

**凭证生命周期**：

```
[*] → Issued → Active → Expired → [*]
                  ↓
                Revoked → [*]
                  ↓
                Burned（任务结束，TEE 端 delete key）→ [*]
```

---

## 第 6 章 — 认证与 Attestation

### 6.1 三域 Attestation 协议选型

| 域 | Layer 1（硬件）| Layer 2（软件）| 验证时延 |
|----|---------------|----------------|----------|
| 座舱 8295 | TPM 2.0 + AK | IMA + 厂商签名 | < 500ms |
| 智驾 Orin | OP-TEE PTA + HSM | IMA + ASIL-D 度量 | < 500ms |
| 车控 S32G | S32G HSM + 双 TA | 简化度量（PCR0-2）| < 200ms |

### 6.2 Attestation 接口设计（POC 预留，P1 实现）

```cpp
class AttestationVerifier {
public:
    virtual AttestationResult verify(
        const std::string& pcr_values,
        const std::string& ak_signature,
        const std::string& nonce
    ) = 0;
};

// POC: 永远返回 success（接口占位）
class PoCAttestationVerifier : public AttestationVerifier { ... };

// P1: 真实 TPM 2.0 + IMA 度量链
class TPMAttestationVerifier : public AttestationVerifier { ... };
```

---

## 第 7 章 — 授权体系

### 7.1 OpenFGA 关系型授权（P1 引入）

关系型策略表达委托链最自然：

```yaml
type: agent
relations:
  main:
    types: [user]
  delegate:
    types: [agent]
  can_call:
    union:
      - { child: [_this] }
      - { computedUserset: { relation: delegate } }
rules:
  - can_call tool:* IF delegated_by(main_agent) AND depth <= 2
```

**优势**：相比 RBAC，OpenFGA 可以自然表达"A 委托了 B，B 可以调用 C"这种传递关系，且 depth 约束可直接内嵌策略。

### 7.2 OIDC-A 1.0 协议方向

**OIDC-A（OpenID Connect for Agents）1.0** 是在 OAuth 2.0 生态内表示 Agent 身份的标准草案：

- 支持**委托链**（Delegation Chain）：用户 → 主 Agent → 子 Agent
- 基于 Agent 属性做**细粒度授权**（attestation-based authorization）
- 与现有 IdP（Okta、Entra、Auth0）兼容
- 区分 Agent 身份（NHI）与人类身份（Human）

> 来源：[OpenID Connect for Agents (OIDC-A) 1.0 — arXiv:2509.25974](https://arxiv.org/abs/2509.25974)

---

## 第 8 章 — 委托链

### 8.1 核心协议：RFC 8693 Token Exchange

主 Agent 派生 L3 凭证的完整流程：

```
主 Agent 派生 L3 流程:
  1. 主 Agent 发起 token-exchange 请求
       subject_token = L1（主 Agent 自身凭证）
       actor_token   = task_ctx（任务上下文）
       audience      = spiffe://nio-cockpit/nav-tool

  2. AS（TPM-AS）验证:
       验 L1 签名
       查 OpenFGA 策略（depth + scope + task_purpose）
       检查配额（max_sub_agents, max_token_per_min）

  3. 颁发 L3（含 act claim）:
       act.sub = L1.sub（追溯委托链）
       TTL = 5 分钟
       task_purpose 双重防御
```

### 8.2 车端委托链硬约束

| 约束 | 规则 | 原因 |
|------|------|------|
| 深度限制 | `depth ≤ 2`（车控域强制 `depth = 0`）| 车控域不允许任何 Sub-Agent |
| 权限单调 | `P_child ⊆ P_parent` | 子级权限不得超过父级 |
| 时效强制 | `TTL ≤ 任务期望时长` | 任务完成后凭证自动失效 |
| 目的绑定 | `task_purpose ∈ Blueprint 白名单` | 防止凭证被复用于其他任务 |

---

## 第 9 章 — 跨域互信

### 9.1 三域 Trust Domain 划分

| Trust Domain | 对应 | ASIL 等级 |
|---|---|---|
| `nio-cockpit` | 座舱域 | ASIL-B |
| `nio-driving` | 智驾域 | ASIL-D |
| `nio-body` | 车控域 | ASIL-A |

### 9.2 SPIFFE Federation Bundle

```
座舱域 ←─Federation Bundle─→ 智驾域
  │                              │
  └──────Federation Bundle───────┘
                ↕
             车控域
```

**关键设计**：

| 设计点 | 说明 |
|--------|------|
| **出厂预置** | 整车出厂时预置 Federation Bundle（离线优先，不依赖网络）|
| **OTA 周期刷新** | 7 天 `stale_grace_period`，OTA 更新 Bundle |
| **车控域只验证不签发** | 车控域单向，不主动发起跨域请求 |
| **跨域 Ticket 不同 ID** | 防重放 + 保持边界清晰 |

### 9.3 跨域 Ticket 扩展字段

```
跨域 ticket = 域内 ticket + 3 个扩展字段:
  source_domain  : str   # 源域（如 nio-cockpit）
  target_domain  : str   # 目标域（如 nio-driving）
  xgw_session_id : u64   # XGW 集中审计 ID
```

### 9.4 跨域三原则

1. **默认禁止**：所有跨域流量默认拒绝，例外通过 XGW 白名单开放
2. **唯一通道**：XGW（Cross-Domain Gateway）是唯一跨域通道，所有流量必经审计
3. **ID 隔离**：跨域 Ticket 使用与域内不同的 ticket_id，防止跨域重放

---

## 第 10 章 — 接口定义

### 10.1 ASG 8 个核心 C API（进程内，车规形态）

```c
typedef struct asg_ctx asg_ctx_t;

// ===== AuthGate（6 个）=====

// 1. 启动期初始化
asg_ctx_t* auth_init(const char* manifest_path);
void auth_destroy(asg_ctx_t* ctx);

// 2. 主 Agent 获取自身 ID
const char* auth_get_self_id(asg_ctx_t* ctx);

// 3. 颁发 ticket（工具调用 / Sub-Agent 派生 / 跨域）
typedef struct {
    enum { TICKET_TOOL, TICKET_SUBAGENT, TICKET_CROSSDOMAIN } kind;
    const char* subject_id;     // Sub-Agent ID 或 Tool ID
    const char* parent_id;      // 父 Agent ID（主 Agent 为 NULL）
    uint64_t    capability;     // 能力 bitmask
    uint32_t    ttl_sec;        // 5s ~ 300s
    const char* task_type;      // Blueprint 模板
    const char* task_id;        // 任务 ID（审计）
    const char* source_domain;  // 跨域用
    const char* target_domain;  // 跨域用
} ticket_spec_t;

ticket_t* auth_issue_ticket(asg_ctx_t* ctx, const ticket_spec_t* spec);

// 4. 验证 ticket
typedef enum {
    AUTH_OK                 = 0,
    AUTH_ERR_EXPIRED        = 1,
    AUTH_ERR_REVOKED        = 2,
    AUTH_ERR_INVALID_SIG    = 3,
    AUTH_ERR_DEPTH_EXCEEDED = 4,
    AUTH_ERR_NO_PERMISSION  = 5,
} auth_result_t;

auth_result_t auth_verify_ticket(asg_ctx_t* ctx, const ticket_t* t);

// 5. 撤销单个 ticket
void auth_revoke(asg_ctx_t* ctx, uint64_t ticket_id);

// 6. Kill Switch：紧急全局撤销
void auth_revoke_all(asg_ctx_t* ctx);
```

**对比业界 Gateway**：业界通常 20–50 个 API，这里只暴露 6 个核心 AuthGate API，**省 73%**。

### 10.2 统一 CredentialIssuer 接口（C++）

业务代码只依赖接口，不绑定具体格式（JWT-SVID 或 ASG Ticket）：

```cpp
class CredentialIssuer {
public:
    virtual std::string issue(
        const std::string& sub,
        const std::string& parent_id,   // 委托链
        uint64_t capability,
        uint32_t ttl_sec,
        const std::string& task_type,
        const std::string& task_id
    ) = 0;

    virtual bool verify(const std::string& token) = 0;
    virtual void revoke(const std::string& ticket_id) = 0;
};

// Framework 实现（跨域标准格式）
class JWTSVIDIssuer : public CredentialIssuer { ... };

// ASG 实现（车规裁剪，< 1μs 验证）
class ASGTicketIssuer : public CredentialIssuer { ... };
```

### 10.3 gRPC 接口（P1 引入，跨进程）

```protobuf
// agent_registry.proto
service AgentRegistry {
  rpc Register(RegisterRequest)         returns (RegisterResponse);
  rpc Lookup(LookupRequest)             returns (LookupResponse);
  rpc UpdateStatus(UpdateStatusRequest) returns (UpdateStatusResponse);
  rpc Revoke(RevokeRequest)             returns (RevokeResponse);
  rpc Heartbeat(HeartbeatRequest)       returns (HeartbeatResponse);
}

// tpm_as.proto — 凭证颁发与验证
service TPMAS {
  rpc DeriveL3(DeriveL3Request) returns (DeriveL3Response);
  rpc Verify(VerifyRequest)     returns (VerifyResponse);
  rpc Revoke(RevokeRequest)     returns (RevokeResponse);
}

// cross_domain.proto — 跨域网关
service CrossDomainGateway {
  rpc Forward(ForwardRequest)         returns (ForwardResponse);
  rpc ListSessions(ListSessionsRequest) returns (ListSessionsResponse);
}
```

---

## 第 11 章 — 业界平台对标

### 11.1 4 大 IAM 平台与借鉴策略

| 平台 | 关键设计 | 车端借鉴度 |
|------|----------|------------|
| **Microsoft Entra Agent ID** | Sponsor / Blueprint / Conditional Access / Agent ID Administrator 角色 | ✅ 高（Blueprint + Sponsor 机制直接借鉴）|
| **Google Agent Identity** | Cloud IAM 扩展 + 域间互信 | ⚠️ 部分（域间互信参考）|
| **AWS AgentCore Identity** | OAuth + SigV4 + AgentCore Runtime | ⚠️ 部分 |
| **Okta for AI Agents** | Workforce Identity 扩展至 Agent | ⚠️ 参考 |

**借鉴策略**：借鉴设计思想，不照搬实现（云平台方案均假设联网，不适合车端离线场景）。

### 11.2 各平台关键差异点

**Microsoft Entra Agent ID**（2026 年 3 月推出，业内首个）：
- **Sponsor 机制**：区别于传统 Owner，要求部门经理对 Agent 合规负责——车端直接采用
- **Blueprint（Agent 蓝图）**：预定义的身份模板，含权限范围、凭证策略——车端 Blueprint yaml 直接对应
- **Conditional Access**：基于 Agent 属性的细粒度访问控制——车端用 OpenFGA + task_purpose 替代

**Google Agent Identity**：
- 每个 Agent 分配唯一密码学身份，配置明确授权策略
- Agent Gateway 执行 MCP/A2A 协议安全策略——车端对应 XGW（跨域网关）

**AWS AgentCore Identity**：
- 基于 OAuth 的身份管理，Agent 代表用户操作
- 车端离线场景无法依赖 OAuth 服务端，改为预置 L1 凭证 + TPM 本地签发

---

## 附录 A — 术语表

| 术语 | 全称 | 说明 |
|------|------|------|
| **NHI** | Non-Human Identity | 非人类身份，Agent 的身份类型 |
| **Least Agency** | 最小代理权限 | Agent 版"最小权限原则"，含能力/时间/目的/深度四维度 |
| **SPIFFE ID** | Secure Production Identity Framework for Everyone | 形如 `spiffe://domain/path` 的通用工作负载身份标识 |
| **JWT-SVID** | JWT-based SPIFFE Verifiable Identity Document | 基于 JWT 的 SPIFFE 可验证身份文档 |
| **ASG Ticket** | Agent Security Gate Ticket | 车规裁剪的轻量凭证格式，C struct，< 1μs 验证 |
| **TPM-AS** | TPM Authorization Server | 基于 TPM 的本地凭证颁发服务 |
| **XGW** | Cross-Domain Gateway | 跨域网关，唯一合法跨域通道 |
| **TEE** | Trusted Execution Environment | 可信执行环境（如高通 QTEE、ARM OP-TEE） |
| **OIDC-A** | OpenID Connect for Agents | Agent 身份的 OIDC 扩展协议草案（arXiv:2509.25974）|
| **RFC 8693** | OAuth 2.0 Token Exchange | 委托链凭证派生协议 |
| **OpenFGA** | Open Fine-Grained Authorization | 关系型细粒度授权引擎 |
| **L1/L2/L3** | 持久层/运行层/临时层凭证 | 三层凭证体系，寿命依次为月/时/分 |
| **Sponsor** | 业务担保人 | 对 Agent 合规行为负责的人类责任主体 |
| **Blueprint** | Agent 蓝图 | Agent 的身份模板，定义能力、配额、审计策略 |
| **depth** | 委托链深度 | 主 Agent depth=0，每派生一级 Sub-Agent depth+1 |
| **Kill Switch** | 终止开关 | 紧急全局撤销，立即使所有 token 失效 |
| **ASIL** | Automotive Safety Integrity Level | 汽车功能安全等级（A/B/C/D，D 最严）|
