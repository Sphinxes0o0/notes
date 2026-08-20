# NIO Vehicle AI Agent Security Framework — Design Spec v1.1

> **Source**: `framework-design-v1.html` (HTML 评审稿, v1.1)
> **Audience**: Coding Agent / 实施工程师
> **Format**: 紧凑 markdown, 去掉装饰, 保留决策 / 模块 / API / 字段
> **配套**: HTML 文档有 mermaid 图, 本 spec 给的是 LLM 可消费的纯文本视图

---

## 1. 关键决策（先看这个）

| 决策点 | 选择 | 引入阶段 |
|--------|------|----------|
| 凭证格式 | JWT-SVID（替代自设计 ticket）| P0 |
| 委托链协议 | RFC 8693 token-exchange + `act` claim | P0 |
| 身份目录 | 自建 Registry（建在 KMSS 之上, TEE 内 gRPC）| P0 |
| Blueprint 存储 | OCI Artifact + cosign | P1 |
| Attestation | TPM 2.0 + IMA | P1（POC 跳过）|
| 跨域互信 | SPIFFE Federation Bundle（预置 + OTA 刷新）| P0（简化）|
| 授权引擎 | OpenFGA（POC 用 if-else 模拟）| P1 |
| 跨域通信（应用层）| gRPC + JWT-SVID Bearer | P0 |
| 传输层 | mTLS（X.509）+ JWT 双层 | P2 |
| Sub-Agent | 线程 + 裸进程双模 | P0 |
| 车控域 | 无 L3 / 双签 / 简化度量 | P0 |
| 撤销机制 | 短 TTL（5min）+ 主动通知 + 本地 jti | P0 |
| 威胁模型 | OWASP ASI + LLM Top 10（映射 T-01..T-10）| P0 |
| X.509 / mTLS | 生产化引入（P2, 传输层）| P2 |
| C509 / CWT | 远期演进项（车控域极致压缩）| P3+ |

---

## 2. POC 范围声明（硬约束）

### 2.1 必做（POC 跑通这个）

- [x] JWT-SVID 签发 / 验签（HS256 起步, 生产切 ES256）
- [x] 三层凭证流转（L1 / L2 / L3）
- [x] 委托链（`act` claim）
- [x] 简化跨域通信（预置公钥模拟 Federation）
- [x] Sub-Agent 派生 + 主动撤销
- [x] 接口抽象层（为未来 X.509 / C509 切换预留）
- [x] 单元测试 + 集成测试

### 2.2 不做（POC 阶段不要碰）

- [ ] X.509 证书管理（P2 引入）
- [ ] mTLS（POC 用明文 HTTP）
- [ ] 完整 Attestation（POC 假设 TEE 可信）
- [ ] OpenFGA 集成（POC 用 if-else 模拟策略）
- [ ] 真实 Registry 服务（POC 用内存对象）
- [ ] 完整审计加密（POC 用 stdout）
- [ ] C509 / CWT（远期演进）
- [ ] 车控域 Lite 版（P2 阶段）

**POC 目标**: 2 周内跑通"主 Agent 派生 L3 → Sub-Agent 调 Tool → 验证 → 撤销"端到端。

---

## 3. 架构总览

### 3.1 三域 Trust Domain 划分

```
nio-cockpit (座舱 8295 + QTEE)   — 资源充裕
nio-driving (智驾 Orin + OP-TEE) — 资源中等
nio-body    (车控 S32G + HSM)    — 资源极紧
```

### 3.2 每域内组件

| 组件 | 职责 | POC 实现 |
|------|------|----------|
| `Agent Registry` | 身份注册 / 状态 / Blueprint 加载 | 内存对象（单例）|
| `TPM-AS` | JWT-SVID 颁发 / 验签 | 单进程, ~200 行 C++ |
| `Main Agent` | 主 Agent | 业务进程 |
| `Sub-Agent` | 子任务代理 | 线程或裸进程 |

### 3.3 跨域通信（简化版）

```
座舱 L1 ───Bearer───▶ 智驾 Tool (用预置公钥验签)
                   └─ 不走 mTLS, 不走 Federation Bundle, 用预置公钥
```

---

## 4. 模块设计

### 4.1 基础设施层（沿用 + 新建）

#### 4.1.1 已有（沿用）
- **KMSS**: 密钥 / 证书 / TEE 集成（NIO 内部）
- **NTS**: TBox 网络 / OTA 通道
- **TEE**: QTEE / OP-TEE / HSM

#### 4.1.2 新建
- **Agent Registry**（TEE 内, gRPC + SQLite）— POC 用内存
- **Blueprint 仓库**（OCI Artifact + cosign）— P1 引入
- **TPM-AS**（TEE 内, gRPC）— POC 单进程
- **Audit Sink**（云端）— POC 用 stdout

#### 4.1.3 关键关系

```
Registry (应用层)  →  KMSS (基础设施)  →  TEE / HSM
   "我是谁"              "密钥"              "硬件根"
```

### 4.2 身份层

#### 4.2.1 三个核心对象

| 对象 | 角色 | POC 状态 |
|------|------|----------|
| Blueprint | Agent 模板（如 `nav-reroute-agent-v1`）| 内存常量 |
| Registry Record | 实例化后的"我是谁" | 内存对象 |
| L1 JWT-SVID | 实体 Agent 运行时凭证 | POC 实现 |

#### 4.2.2 Blueprint 字段（参考 SPIRE Workload Entry + 车端扩展）

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

attestation:                      # POC 跳过
  min_pcr_policy: "pcr0-7:strict"
  binary_signature_required: true
  hsm_key_required: true
  refresh_interval_sec: 3600

audit:
  level: full
  retention_days: 365
  encryption: tee-sealed         # POC 用 stdout

lifecycle:
  max_age_days: 90
  ota_upgradeable: true
  auto_rotate: true

applicability:
  vehicle_models: [ET7, ET5, ES8]
  trust_domains: [nio-cockpit]
```

#### 4.2.3 状态机

```
[*] → Created → Attesting → Active
                      ↓ (失败)
                   Failed → [*]
Active → Suspended → Active (恢复)
Active → Rotating → Active (OTA)
Active → Revoked → Destroyed → [*]
```

### 4.3 认证层（Attestation）

**POC 阶段跳过**，但接口预留：

```cpp
// POC 阶段: 假设 TEE 可信, 跳过 Attestation
// 真实实现: TPM 2.0 + IMA 度量链
class AttestationVerifier {
public:
    virtual AttestationResult verify(
        const std::string& pcr_values,
        const std::string& ak_signature,
        const std::string& nonce
    ) = 0;
};

// POC 实现: 永远返回 success
class PoCAttestationVerifier : public AttestationVerifier { ... };

// 生产实现: 真实 TPM 验证
class TPMAttestationVerifier : public AttestationVerifier { ... };
```

### 4.4 凭证层

#### 4.4.1 三层凭证定义

| 层 | 寿命 | 签名算法（POC） | 存储 | 撤销 |
|----|------|---------------|------|------|
| L1 持久层 | 跟镜像同寿命（~3 月）| HS256（POC）/ ES256（生产）| TEE 持久区 | OTA 整车级撤销 |
| L2 运行层 | 1 小时 | HS256 | TEE 易失区 | 自动过期 |
| L3 临时层 | 5 分钟 | HS256 | TEE 临时区 | 任务结束 + 短 TTL |

#### 4.4.2 L3 JWT-SVID 完整字段

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

#### 4.4.3 关键不变量（hard invariants）

```
1. act.sub 必须存在 (委托链)
2. exp - iat ≤ 300 (L3 寿命 ≤ 5min)
3. aud 必须包含目标 service SPIFFE ID
4. vehicle_id 必须存在 (车端特有)
5. 车控域永不发 L3
```

#### 4.4.4 撤销机制（POC 阶段）

```cpp
// 1. 短 TTL (默认兜底)
exp - iat <= 300  // 5 分钟

// 2. 主动撤销 (立即生效)
void revoke(const std::string& jti) {
    revoked_jtis_.insert(jti);
}

bool is_revoked(const std::string& jti) {
    return revoked_jtis_.count(jti) > 0;
}

// 3. 验证时检查
bool verify_l3(const std::string& token) {
    auto claims = decode(token);
    if (is_revoked(claims.jti)) return false;
    if (claims.exp < now()) return false;
    return verify_signature(token);
}
```

### 4.5 授权层（OpenFGA — POC 用 if-else 模拟）

#### 4.5.1 委托链授权规则

```cpp
// POC 阶段: if-else 模拟
bool can_call_tool(const std::string& caller_sub, const Tool& tool) {
    // 规则 1: caller 必须在 tool 的 ACL 中
    if (!tool.acl.count(caller_sub)) return false;
    
    // 规则 2: depth <= 2 (硬约束)
    if (get_delegate_depth(caller_sub) > 2) return false;
    
    // 规则 3: scope 必须匹配
    if (!tool.scope.count(get_claim(caller_sub, "scope"))) return false;
    
    // 规则 4: task_purpose 必须匹配 (POC 跳过 Conditional Access)
    // if (!tool.purposes.count(get_claim(caller_sub, "task_purpose"))) return false;
    
    return true;
}
```

#### 4.5.2 OpenFGA 策略模板（P1 引入）

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

### 4.6 通信层

#### 4.6.1 POC 阶段

```
HTTP/1.1 明文 + Bearer Token
Header:
  Authorization: Bearer <L3 JWT-SVID>
  X-Request-Id: uuid-xxx
  X-Task-Purpose: reroute_emergency
```

#### 4.6.2 P2 阶段（生产化）

```
传输层: mTLS (X.509)  ← 通道加密
应用层: JWT-SVID       ← 身份凭证

[Agent] --mTLS--> [Gateway] --mTLS--> [Tool]
        |
        +-- Authorization: Bearer <L3>
```

### 4.7 Sub-Agent 层

#### 4.7.1 双模设计

| 模式 | 资源 | 隔离 | 凭证 | 适用 |
|------|------|------|------|------|
| 线程 | 极低 | 弱 | L3 (5min) | 短任务 < 30s |
| 裸进程 | 中 | 中 | L2 + L3 | 长任务, 高危 Tool |

#### 4.7.2 派生协议（RFC 8693）

```cpp
// 主 Agent 派生 L3
std::string derive_l3(
    const std::string& l1_token,           // 主体凭证
    const std::string& sub_agent_id,       // 新 sub-agent ID
    const std::string& task_purpose,
    const std::vector<std::string>& audience
) {
    auto l1_claims = decode(l1_token);
    
    // 验证 L1 未过期
    if (l1_claims.exp < now()) throw std::runtime_error("L1 expired");
    
    // 检查 sub-agent 数量限制 (Blueprint.quotas.max_sub_agents)
    if (active_sub_agents_.size() >= max_sub_agents_) {
        throw std::runtime_error("max sub-agents reached");
    }
    
    // 颁发 L3
    return jwt::create()
        .set_issuer(l1_claims.iss)
        .set_subject("spiffe://nio-cockpit/" + sub_agent_id)
        .set_audience(audience)
        .set_issued_at(now())
        .set_expires_at(now() + 5min)
        .set_id(gen_uuid())
        // 委托链
        .set_payload_claim("act", jwt::claim({
            {"sub", l1_claims.sub},
            {"profile", l1_claims.profile}
        }))
        .set_payload_claim("task_purpose", task_purpose)
        .set_payload_claim("vehicle_id", l1_claims.vehicle_id)
        .sign(ALGORITHM);  // POC: HS256, 生产: ES256
}
```

#### 4.7.3 车控域硬约束

```cpp
// 车控域永远不派生 sub-agent
if (domain == "nio-body") {
    throw std::runtime_error("sub-agent delegation not allowed in body domain");
}
```

### 4.8 审计层

#### 4.8.1 审计事件类型

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

#### 4.8.2 审计字段（POC: stdout）

```cpp
struct AuditEvent {
    std::string event_type;     // 如 "svid.issued"
    std::string jti;            // 唯一 ID
    std::string actor_sub;      // 主 Agent (委托链)
    std::string subject_sub;    // 凭证主体
    std::string vehicle_id;
    std::string task_purpose;
    std::string tool;           // 调用的 Tool
    std::string tool_params_hash; // 参数摘要, 不含敏感数据
    int64_t timestamp;          // 硬件时间
    std::string severity;       // info/warn/critical
};
```

---

## 5. 三域差异化

| 维度 | 座舱 | 智驾 | 车控 |
|------|------|------|------|
| 资源 | 充裕 | 中等 | **极紧** |
| 凭证 | L1+L2+L3 全 | L1+L2+L3 全 | **L1+L2（无 L3）** |
| Sub-Agent | 线程+进程 | 偏进程 | **不启用** |
| Attestation | 标准 TPM | ASIL-D 强化 | 简化 + 双签 |
| 跨域通信 | gRPC to 网关 | gRPC to 网关 | 极少, 强审计 |
| 威胁模型 | OWASP 全 10 类 | OWASP + ASIL-D | ASIL-D 简化 |

**车控域特殊**:
- 启动时双签（主+备 TA 共识）
- 简化度量链（PCR0-2, 不跑 IMA）
- L1 TTL ≤ 24h（其他域 3 月）
- break-glass 紧急逃生口（HSM 单独 key, 强制双 Agent 共识, 全程录像）

---

## 6. 威胁模型 T-01..T-10

| 编号 | 威胁 | OWASP 来源 | 防御 |
|------|------|-----------|------|
| T-01 | Excessive Agency | ASI01 / LLM06 | L3 scope 限制 + OpenFGA |
| T-02 | Prompt Injection | ASI02 / LLM01 | Guard 模块（不在本 spec）|
| T-03 | Identity Spoofing | ASI03 | JWT-SVID 验签 + Attestation |
| T-04 | Tool Misuse | ASI04-07 | L3 scope + Conditional Access |
| T-05 | Supply Chain | ASI08 | 二进制签名 + PCR 白名单 |
| T-06 | Data Leakage | ASI09 / LLM02 | audit 加密 + TEE 隔离 |
| T-07 | Untrusted Output | LLM05 | Guard 模块（不在本 spec）|
| T-08 | DoS via Agent | ASI10 | 资源配额（Blueprint）|
| T-09 | Cascading Failure | 车端特有 | break-glass + 强审计 |
| T-10 | Audit Gap | 车端特有 | TEE 不可篡改日志 |

**fail-secure 原则**: 任何安全失败必须降级到**更安全**模式（不允许降级到不安全）。

降级路径: 重试 → 重启 Agent → 域级降级 → 整车安全模式。

---

## 7. 实施 Roadmap

```
P0 必做 (2 周):
  - JWT-SVID hello world
  - Sub-Agent 派生 + 撤销
  - 简化跨域通信
  - 单元测试 + 集成测试

P1 应做 (4 周):
  - Agent Registry 服务化
  - Blueprint schema + OCI 仓库
  - Attestation 简化版（POC 是占位）
  - OpenFGA 集成
  - KMSS 集成

P2 可做 (4 周):
  - mTLS (X.509) 通道加密
  - 真实 Registry (gRPC + SQLite)
  - 审计加密
  - 车控域 Lite 版

P3 合规 (4 周):
  - ISO 21434 / R155 合规对接
  - 渗透测试
  - 第三方审计
  - C509 / CWT PoC 评估
```

---

## 8. 风险与缓解

| 风险 | 缓解 |
|------|------|
| KMSS 接口变更 | 提前对齐, P0 冻结接口 |
| 车控域资源评估偏差 | P1 阶段做 S32G 实测 |
| Attestation 启动开销 | 缓存 Attestation 结果 |
| Federation Bundle 离线过期 | 7 天 grace + 充电时强制刷新 |
| OWASP 映射过松 | P1 阶段由安全团队独立审计 |
| OpenFGA 性能不达标 | P0 benchmark, > 1ms 切本地缓存 |
| C509 规范不稳定 | POC/P1/P2 不引入, P3 前持续观察 |
| X.509 证书管理复杂度 | POC 跳过, P2 评估是否复用 KMSS |
| POC 范围蔓延 | 严格遵守 §2 范围声明 |

---

## 9. 长期演进（X.509 / C509）

### 9.1 X.509 + mTLS（P2 引入）

- **域间通信**: 座舱 ↔ 智驾 gateway 用 mTLS, JWT 在通道内透传
- **长连接**: 智驾 Agent 订阅感知流（持续连接）
- **车控传统路径**: 与 AUTOSAR SecOC 共存
- **TPM Attestation**: TPM 2.0 EK / AK 证书本身就是 X.509

### 9.2 C509 / CWT（P3+ 远期）

- **C509** (CBOR X.509): 体积比 DER 小 50-70%, 适合车控域 Flash 资源
- **CWT** (CBOR Web Token): 替代 JWT-SVID, 体积更小
- **COSE 生态**: RFC 9052 / RFC 8392, IoT / 受限设备趋势

**不立刻引入的原因**:
- C509 仍在 IETF 草案, 规范稳定性待验证
- 工具链不成熟, 调试 / 运维成本高
- 跟 X.509 / JWT 生态不互通, 跨域要网关翻译
- 审计 / 合规可能不认非 RFC 标准

**建议路径**: P3 阶段做 C509 PoC, 视结果决定是否切车控域。

---

## 10. POC 代码骨架建议

### 10.1 文件结构

```
poc/
├── include/
│   ├── svid.h              # JWT-SVID 颁发 / 验签
│   ├── delegate.h          # 委托链 / act claim
│   ├── blueprint.h         # Agent 模板 (POC 用常量)
│   ├── audit.h             # 审计事件 (POC 用 stdout)
│   └── verifier.h          # Tool 侧验签
├── src/
│   ├── svid.cpp
│   ├── delegate.cpp
│   ├── blueprint.cpp
│   ├── audit.cpp
│   └── verifier.cpp
├── demo/
│   ├── issue_l3.cpp        # Demo 1: 派生 L3
│   ├── verify_l3.cpp       # Demo 2: 验签 L3
│   └── sub_agent_demo.cpp  # Demo 3: 端到端
├── test/
│   ├── test_svid.cpp
│   ├── test_delegate.cpp
│   └── test_e2e.cpp
├── CMakeLists.txt
└── README.md
```

### 10.2 核心 API（C++ 头文件示意）

```cpp
// svid.h
namespace nio::asf {

class SVIDIssuer {
public:
    // 颁发 L1 (持久层)
    std::string issue_l1(
        const std::string& main_agent_sub,
        const std::string& vehicle_id,
        std::chrono::seconds ttl = std::chrono::hours{24 * 90}
    );

    // 颁发 L2 (运行层)
    std::string issue_l2(
        const std::string& main_agent_sub,
        std::chrono::seconds ttl = std::chrono::hours{1}
    );

    // 派生 L3 (任务级, RFC 8693)
    std::string derive_l3(
        const std::string& l1_token,           // 主体凭证
        const std::string& sub_agent_sub,      // sub-agent ID
        const std::string& task_purpose,
        const std::vector<std::string>& audience
    );

    // 撤销 (按 jti)
    void revoke(const std::string& jti);
};

class SVIDVerifier {
public:
    // 验证 L1/L2/L3
    bool verify(const std::string& token);

    // 提取 claim
    std::string get_sub(const std::string& token);
    std::string get_act_sub(const std::string& token);   // 委托链
    std::string get_task_purpose(const std::string& token);
    std::string get_vehicle_id(const std::string& token);
    int64_t get_exp(const std::string& token);
    std::string get_jti(const std::string& token);

    // 撤销检查
    bool is_revoked(const std::string& jti);
};

}  // namespace nio::asf
```

### 10.3 算法与库选型

| 用途 | POC | 生产 |
|------|-----|------|
| JWT 库 | jwt-cpp (header-only) | jwt-cpp / jsonwebtoken (Rust) |
| 签名算法 | HS256 (预共享密钥) | ES256 (ECDSA P-256) |
| 加密原语 | OpenSSL libcrypto | OpenSSL / ring (Rust) |
| HTTP | cpp-httplib (header-only) | gRPC |
| 序列化 | nlohmann/json | nlohmann/json / protobuf |
| 测试 | doctest (header-only) | doctest / GoogleTest |

### 10.4 单元测试用例（最小集）

```cpp
// test_svid.cpp
TEST_CASE("L1 issuance") {
    auto issuer = SVIDIssuer("poc-secret");
    auto l1 = issuer.issue_l1("spiffe://nio-cockpit/main-agent-01", "NIO-ET7-001");
    REQUIRE(!l1.empty());
}

TEST_CASE("L3 derivation contains act claim") {
    // ... 派生 L3, 验签, 检查 act.sub == l1.sub
}

TEST_CASE("L3 ttl is 5 minutes") {
    // ... 派生 L3, 验签, 检查 exp - iat == 300
}

TEST_CASE("L3 revocation") {
    // ... 派生 L3, 撤销, 验签应该失败
}

TEST_CASE("Body domain rejects L3") {
    // ... 车控域派生 L3 应该抛异常
}

TEST_CASE("Cross-domain verification with pre-shared key") {
    // ... 座舱 L1 派生 L3, 智驾 Tool 用预置公钥验签
}
```

---

## 11. 关键规则速查（给 coding agent 的"不要做"清单）

### 11.1 永远要做

1. L3 必须包含 `act` claim（除非是 L1/L2）
2. L3 `exp - iat ≤ 300`（5 分钟）
3. 所有 token 包含 `vehicle_id`
4. 验证 token 时检查 `is_revoked(jti)`
5. 车控域不带 L3 派生代码路径

### 11.2 永远不做（POC 阶段）

1. 不要引入 X.509 证书管理（用预共享密钥替代）
2. 不要引入 mTLS（用明文 HTTP）
3. 不要引入 OpenFGA 集成（用 if-else 模拟）
4. 不要引入真实 Attestation（假设 TEE 可信）
5. 不要引入 C509 / CWT（远期演进项）
6. 不要派生超过 Blueprint 配额的 sub-agent
7. 不要让车控域派生 sub-agent

### 11.3 接口抽象（为未来切换预留）

```cpp
// POC: HS256 + 预共享密钥
class PoCCredentialIssuer : public CredentialIssuer { ... };

// P2: ES256 + KMSS
class ProductionCredentialIssuer : public CredentialIssuer { ... };

// P3+: COSE / C509 (远期)
class COSECredentialIssuer : public CredentialIssuer { ... };

// 业务代码只依赖接口, 不依赖实现
```

---

## 12. 术语速查

| 术语 | 含义 |
|------|------|
| JWT-SVID | JWT 形式的工作负载身份证明 |
| SPIFFE | 工作负载身份标准 |
| Trust Domain | 信任域（座舱/智驾/车控各一个）|
| `act` claim | RFC 8693 委托链字段（"代谁行动"）|
| L1 / L2 / L3 | 持久层 / 运行层 / 临时层凭证 |
| Sub-Agent | 主 Agent 派生的子任务代理 |
| KMSS | NIO 内部 Key Management Service System |
| NTS | NIO 内部 Network/Telematics Service |
| QTEE | Qualcomm TEE（座舱域）|
| OP-TEE | Open Portable TEE（智驾域）|
| HSM | Hardware Security Module（车控域核心）|

---

## 13. 引用

- **HTML 评审稿**: `framework-design-v1.html`（含 10 个 mermaid 架构图）
- **调研依据**: `../llm-agent-delegation-research-2026/README.md`（四梯队资料 + 决策对齐表）
- **配套网关设计**: `../nio-asg-design/architecture.md`（AgentSec Gateway lib + daemon）
- **核心协议**:
  - RFC 8693 (Token Exchange): https://datatracker.ietf.org/doc/html/rfc8693
  - SPIFFE Federation: https://spiffe.io/docs/latest/spiffe-about/spiffe-federation/
  - JWT-SVID: https://github.com/spiffe/spiffe/blob/main/standards/JWT-SVID.md
  - OIDC-A 1.0: https://arxiv.org/abs/2509.25974
  - OpenFGA: https://openfga.dev
  - jwt-cpp: https://github.com/Thalhammer/jwt-cpp

---

## 14. 版本

- **v1.1** (2026-07-20)
  - 新增 §0.5 POC 范围声明（明确 X.509 / C509 不引入）
  - 新增 §6.4 / §9 X.509 / C509 长期演进方案
  - 新增 §8.4 双层架构（mTLS + JWT）
  - §13 决策汇总扩展到 15 项
  - §15 风险与缓解扩展到 9 条
  - 附录 B 新增 COSE 生态参考
- **v1.0** (2026-07-20): 初始评审稿
