# 车端 Agent IAM 深度设计 — 三大专题深入

> **专题一**: KMSS — 车端 CA 层次设计与证书签发协议  
> **专题二**: OPA Rego — 车端 Agent 权限策略完整实现  
> **专题三**: A2A TASK_STATE_AUTH_REQUIRED — HMI 用户确认场景深度调研

---

# 专题一: KMSS — 车端 CA 层次设计与证书签发协议

## 1.1 什么是 KMSS（在车端语境下）

### 定义

KMSS (Key Management and Security Storage Service) 是运行在车载安全域中的密钥管理和安全存储服务。它不是简单的 "key-value store for keys"，而是一个完整的 **车载 PKI 基础设施**。

```
KMSS 的四个核心职责:

┌───────────────────────────────────────────────────────────┐
│                        KMSS                                │
│                                                            │
│  ① Certificate Authority (CA)                              │
│     - Vehicle Root CA 管理                                  │
│     - Intermediate CA 签发与轮转                            │
│     - Agent 证书签发 (CSR → Certificate)                   │
│     - CRL (Certificate Revocation List) 管理                │
│                                                            │
│  ② Key Lifecycle Management                                │
│     - 密钥生成 (在 TEE 内)                                  │
│     - 密钥存储 (密封到 TEE)                                 │
│     - 密钥轮转 (自动/手动)                                  │
│     - 密钥销毁 (安全擦除)                                   │
│                                                            │
│  ③ TEE Attestation Verification                            │
│     - 验证 TEE Attestation Report                          │
│     - 代码度量值白名单管理                                  │
│     - 平台完整性校验 (PCR values)                           │
│                                                            │
│  ④ Secure Storage API                                      │
│     - 密封 (Seal): 用平台唯一密钥加密数据                    │
│     - 解封 (Unseal): 只有指定 TEE/TA 可解密                 │
│     - 安全时钟: 防回滚的时间戳                              │
└───────────────────────────────────────────────────────────┘
```

### 为什么需要 KMSS（而不是直接用 OpenSSL 签发证书）

| 需求 | OpenSSL 方案 | KMSS 方案 |
|------|------------|----------|
| **Root CA 私钥保护** | 文件系统存储 → 可被 root 读取 | TEE 密封存储 → 物理不可提取 |
| **Agent 私钥保护** | Agent 进程持有私钥文件 → 被攻破即泄露 | 私钥在 TEE 中生成且永不离片 |
| **身份证明** | 仅依赖证书签名 → 无平台信任 | TEE Attestation → 证明 Agent 运行在可信平台 |
| **密钥轮转** | 手动脚本 → 易出错 | 自动轮转 + 渐进式过渡 → 零停机 |
| **吊销** | CRL 文件手动更新 | 实时 CRL + 安全时钟 → 防回滚攻击 |
| **合规审计** | 无 | 所有密钥操作有 TEE 签名的审计链 |

---

## 1.2 CA 层次设计

### 三层 CA 架构

```
┌──────────────────────────────────────────────────────────────┐
│                    OEM Root CA (离线)                          │
│                    ┌────────────────────┐                     │
│                    │ OEM Root CA        │                     │
│                    │ (HSM 保护)         │                     │
│                    │                    │                     │
│                    │ CN: OEM Root CA    │                     │
│                    │ Validity: 20 years │                     │
│                    │ Key: ECDSA P-384   │                     │
│                    └────────┬───────────┘                     │
│                             │ 签发                            │
│                    ┌────────▼───────────┐                     │
│                    │ Vehicle Platform CA│                     │
│                    │ (per vehicle model)│                     │
│                    │                    │                     │
│                    │ CN: Platform CA    │                     │
│                    │ Validity: 10 years │                     │
│                    │ Key: ECDSA P-384   │                     │
│                    └────────┬───────────┘                     │
│                             │ 签发                            │
│                    ┌────────▼───────────┐                     │
│                    │ Vehicle Instance CA│                     │
│                    │ (per VIN)          │                     │
│                    │                    │                     │
│                    │ CN: Vehicle CA     │                     │
│                    │     -LSVN123456    │                     │
│                    │ Validity: 5 years  │                     │
│                    │ Key: ECDSA P-256   │                     │
│                    └────────┬───────────┘                     │
└──────────────────────────────┼──────────────────────────────┘
                               │ 签发
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────▼───────┐    ┌────────▼────────┐   ┌─────────▼─────────┐
│ Agent Cert    │    │ Agent Cert      │   │ Agent Cert        │
│ ADAS Agent    │    │ Climate Agent   │   │ Infotain. Agent   │
│               │    │                 │   │                   │
│ CN: adas-     │    │ CN: climate-    │   │ CN: voice-        │
│   controller  │    │   controller    │   │   assistant       │
│ SAN: spiffe://│    │ SAN: spiffe://  │   │ SAN: spiffe://    │
│   vehicle...  │    │   vehicle...    │   │   vehicle...      │
│               │    │                 │   │                   │
│ Validity: 24h │    │ Validity: 24h   │   │ Validity: 24h     │
│ Key: ECDSA    │    │ Key: ECDSA      │   │ Key: ECDSA        │
│   P-256       │    │   P-256         │   │   P-256           │
│ (TEE 保护)    │    │ (TEE 保护)      │   │ (TEE 保护)        │
└───────────────┘    └─────────────────┘   └───────────────────┘
```

### 各 CA 的职责与安全边界

| CA 层级 | 位置 | 私钥保护 | 生命周期 | 职责 |
|---------|------|---------|---------|------|
| **OEM Root CA** | OEM 安全设施 (HSM) | FIPS 140-2 Level 3 HSM | 20 年 | 签发 Platform CA。私钥永久离线。 |
| **Vehicle Platform CA** | OEM PKI 服务 (在线或离线签名) | HSM | 10 年 | 签发 Vehicle Instance CA。按车型平台划分。 |
| **Vehicle Instance CA** | **车端 KMSS (TEE 内)** | TEE 密封存储 | 5 年 (车辆寿命) | 签发所有 Agent 证书。签发 CRL。 |
| **Agent Certificate** | Agent 的 TEE Key Store | TEE 密封存储 | 24 小时 | Agent 身份证明。mTLS 通信。 |

### 为什么 Vehicle Instance CA 在车端？

```
关键决策: Vehicle Instance CA 放在车端 (TEE 内) 还是云端？

放在车端的理由:
✅ Agent 证书签发无需云端连接 (离线可用)
✅ 签发延迟 < 1ms (本地操作)
✅ 每个 VIN 独立 CA → 单车失陷不影响其他车辆
✅ 私钥在 TEE 中 → 即使物理攻破 ECU 也无法提取

放在云端的风险:
❌ 离线时无法签发新证书
❌ 网络延迟 (100ms+) 影响启动时间
❌ 云端 CA 失陷 → 全量车辆受影响
❌ 需要 per-VIN 隔离 → CA 数量 = 车辆数量 → 管理复杂

结论: Vehicle Instance CA 放在 TEE 中是最优解
```

---

## 1.3 证书签发协议 (Agent → KMSS → Certificate)

### 协议总览

```
┌─────────────────────────────────────────────────────────────────┐
│              Agent Certificate Issuance Protocol                  │
│              (Agent → KMSS, over TEE Secure Channel)              │
│                                                                   │
│  Protocol: KMSS-CERT-ISSUE v1                                    │
│  Transport: TEE Secure Channel (TA-to-TA RPC)                    │
│  Authentication: TEE Attestation Report                          │
│                                                                   │
│  消息格式:                                                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Request: {                                                    │ │
│  │   "version": "1.0",                                          │ │
│  │   "message_type": "cert_issue_request",                      │ │
│  │   "agent_identity": {                                        │ │
│  │     "domain": "chassis",                                     │ │
│  │     "component_type": "agent",                               │ │
│  │     "component_name": "adas-controller",                     │ │
│  │     "asil_level": "ASIL-D",                                  │ │
│  │     "firmware_hash": "sha256:e3b0c44298fc1c..."             │ │
│  │   },                                                          │ │
│  │   "csr": "-----BEGIN CERTIFICATE REQUEST-----...",           │ │
│  │   "attestation_report": {                                    │ │
│  │     "tee_type": "OPTEE",                                     │ │
│  │     "ta_uuid": "a1b2c3d4-...",                              │ │
│  │     "ta_measurement": "sha256:abc...",                       │ │
│  │     "platform_pcrs": {                                       │ │
│  │       "pcr0": "sha256:...",  # 固件度量                     │ │
│  │       "pcr7": "sha256:..."   # 安全启动状态                 │ │
│  │     },                                                        │ │
│  │     "signature": "..."       # TEE 签名                      │ │
│  │   }                                                           │ │
│  │ }                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Response: {                                                   │ │
│  │   "version": "1.0",                                          │ │
│  │   "message_type": "cert_issue_response",                     │ │
│  │   "certificate_chain": [                                     │ │
│  │     "-----BEGIN CERTIFICATE-----  Agent Cert  -----END...",  │ │
│  │     "-----BEGIN CERTIFICATE-----  Vehicle Instance CA →",   │ │
│  │     "-----BEGIN CERTIFICATE-----  Vehicle Platform CA →",   │ │
│  │     "-----BEGIN CERTIFICATE-----  OEM Root CA    -----END..."│ │
│  │   ],                                                          │ │
│  │   "crl_url": "grpcs://kmss.vehicle.local:8443/crl",         │ │
│  │   "renewal_window": "PT2H",     # 过期前 2 小时续期         │ │
│  │   "issued_at": "2025-07-31T14:30:00Z",                      │ │
│  │   "expires_at": "2025-08-01T14:30:00Z"                      │ │
│  │ }                                                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 详细步骤

```
Step 0: 前置条件
  - KMSS TA (Trusted Application) 已在 TEE 中加载运行
  - Vehicle Instance CA 私钥已在 KMSS TA 中密封存储
  - Agent TA 的度量值已注册到白名单

Step 1: Agent 启动
  Agent TA 启动 → 生成 TEE Attestation Report
  Report 内容:
    - TA UUID
    - TA 代码度量值 (SHA-256)
    - 平台 PCR 值 (PCR0: 固件度量, PCR7: 安全启动状态)
    - TEE 签名 (证明此 Report 来自可信 TEE)

Step 2: Agent → KMSS: CertIssueRequest
  通过 TEE Secure Channel (TA-to-TA RPC) 发送请求
  请求包含: CSR + Attestation Report + Agent Identity

Step 3: KMSS 验证 Attestation Report
  3.1 验证 Report 签名 → 确认来自可信 TEE
  3.2 验证 TA 度量值 → 确认 Agent 代码未被篡改
  3.3 验证 PCR 值 → 确认平台处于健康状态
  3.4 检查 TA UUID → 确认 Agent 身份与 TEE TA 绑定

Step 4: KMSS 验证 CSR
  4.1 验证 CSR 签名 (确认 Agent 持有对应私钥)
  4.2 验证 Subject 信息与 Attestation 一致
  4.3 检查是否已有该 Agent 的有效证书 (重复请求检测)

Step 5: KMSS 签发证书
  5.1 用 Vehicle Instance CA 私钥签名 CSR → x.509 证书
  5.2 证书属性:
      - Subject: CN={name}.{type}.{domain}.vehicle-{VIN}
      - SAN URI: spiffe://vehicle-{VIN}.local/{domain}/{type}/{name}
      - Key Usage: digitalSignature, keyEncipherment
      - Extended Key Usage: clientAuth, serverAuth
      - Custom Extensions:
        · agent_domain: {domain}
        · agent_asil_level: {asil_level}
        · agent_tee_attested: true
        · agent_firmware_hash: {firmware_hash}
      - Validity: notBefore=now, notAfter=now+24h
      - Serial: 随机 16 字节

Step 6: KMSS → Agent: CertIssueResponse
  返回完整证书链 + CRL URL + 续期窗口

Step 7: Agent 存储
  - 证书存储到 TEE Key Store (私钥仍然在 TEE 中)
  - 证书链缓存到 Agent 内存
  - 设置定时器: T-2h 触发自动续期
```

### CSR 的特殊约束

```
车端 CSR 与标准 CSR 的区别:

标准 CSR (RFC 2986):
  Subject: CN=my-agent
  (仅包含 DN 信息)

车端 CSR:
  Subject: CN=adas-controller.agent.chassis.vehicle-LSVN123
  Extensions:
    - Subject Alternative Name:
        URI: spiffe://vehicle-LSVN123.local/chassis/agent/adas-controller
    - Agent Identity Extension (自定义 OID: 1.3.6.1.4.1.{OEM}.1):
        domain: chassis
        asil_level: ASIL-D
        firmware_hash: sha256:abc...
  ⚠ 关键约束:
    CSR 中的 agent_identity 字段必须与 Attestation Report 中的信息一致
    KMSS 会交叉验证，防止身份伪造
```

---

## 1.4 自动续期协议

### 续期时序

```
时间轴: Agent 证书生命周期 (24h)

00:00 ──── 证书签发 (notBefore)
  │
  │    Agent 正常运行，使用证书进行 mTLS
  │
22:00 ──── 触发续期 (expires_in < 2h)
  │        Agent Sidecar:
  │          1. 在 TEE 中生成新密钥对
  │          2. 构造 RenewRequest (新 CSR + 当前证书签名)
  │          3. → KMSS: 发送续期请求
  │        KMSS:
  │          4. 验证请求签名 (当前证书公钥)
  │          5. 验证当前证书未被吊销
  │          6. 验证 TEE Attestation 仍然有效
  │          7. 签发新证书
  │          8. → Agent: 返回新证书
  │
  │    原子切换:
  │      - 新 gRPC 连接使用新证书
  │      - 已有连接继续使用旧证书直到过期
  │
24:00 ──── 旧证书过期 (notAfter)
  │        旧证书自动失效，所有连接已迁移到新证书
  │
46:00 ──── 下一次续期触发
  │
48:00 ──── 第二个证书过期

...循环...
```

### 续期消息

```json
// RenewRequest
{
  "version": "1.0",
  "message_type": "cert_renew_request",
  "current_cert_serial": "0x04B7E3A2F1",
  "current_cert_signature": "<TEE签名(msg=新CSR, key=当前证书私钥)>",
  "new_csr": "-----BEGIN CERTIFICATE REQUEST-----...",
  "attestation_report": { /* 新的 TEE Attestation Report */ }
}

// RenewResponse  
{
  "version": "1.0",
  "message_type": "cert_renew_response",
  "certificate_chain": [...],
  "status": "RENEWED",
  "old_cert_revoked": false   // 旧证书不吊销，让其自然过期
}
```

---

## 1.5 CRL 与吊销

### CRL 结构

```yaml
# Vehicle Instance CRL (由 Vehicle Instance CA 签发)
crl:
  issuer: "CN=Vehicle Instance CA - LSVN123456"
  this_update: "2025-07-31T14:30:00Z"
  next_update: "2025-08-01T14:30:00Z"  # 每 24h 更新
  revoked_certificates:
    - serial: "0x04B7E3A2F1"
      revocation_date: "2025-07-31T10:00:00Z"
      reason: "keyCompromise"        # RFC 5280 CRL Reason
      
    - serial: "0x05C8F4B3A2"
      revocation_date: "2025-07-31T11:00:00Z"  
      reason: "cessationOfOperation" # Agent 被卸载
      
    - serial: "0x06D9A5C4B3"
      revocation_date: "2025-07-31T12:00:00Z"
      reason: "superseded"           # 固件升级后旧身份作废
      
  extensions:
    - crl_number: 127
    - authority_key_identifier: "keyid:..."
```

### 吊销触发条件

```yaml
revocation_triggers:
  # 1. TEE 完整性校验失败
  - name: "tee_integrity_failure"
    condition: "TEE Attestation 连续 3 次验证失败"
    action: "立即吊销 → 通知安全监控 → Agent 降级/隔离"
    
  # 2. Agent 固件异常
  - name: "firmware_anomaly"  
    condition: "PCR 值与白名单不匹配 (OTA 更新期间除外)"
    action: "立即吊销 → 阻止 Agent 通信"
    
  # 3. Agent 卸载
  - name: "agent_decommissioned"
    condition: "Agent 被主动卸载 (OTA 移除)"
    action: "吊销 → 清理 CRL"
    
  # 4. 安全事件响应
  - name: "security_incident"
    condition: "IDS/IDPS 检测到该 ECU 的入侵迹象"
    action: "立即吊销 → 隔离 ECU → 触发安全审计"
    
  # 5. VIN 级批量吊销
  - name: "vehicle_decommissioned"
    condition: "车辆报废/退市"
    action: "吊销 Vehicle Instance CA → 整车主证书链失效"
```

### CRL 分发

```
┌──────────────────────────────────────────────────────────┐
│                   CRL Distribution Flow                    │
│                                                           │
│  KMSS                                                      │
│   │  (签发 CRL)                                            │
│   │                                                        │
│   ├──→ gRPC Push: 所有 Agent 订阅 CRL 更新流               │
│   │    (实时推送，关键吊销 < 1s 到达)                       │
│   │                                                        │
│   ├──→ 定期 Poll: Agent 每 5 分钟拉取最新 CRL              │
│   │    (容错，防止 push 丢失)                               │
│   │                                                        │
│   └──→ 本地缓存: Agent 缓存最后已知 CRL                    │
│        (离线场景使用)                                      │
│                                                           │
│  Agent 检查流程 (每次 mTLS Handshake):                     │
│   1. 提取 Client Cert Serial                              │
│   2. 查询本地 CRL 缓存 → 如果已吊销 → 拒绝连接             │
│   3. 如果 CRL 缓存超过 6 小时未更新 → 拒绝连接 (fail-secure)│
└──────────────────────────────────────────────────────────┘
```

---

# 专题二: OPA Rego — 车端 Agent 权限策略完整实现

> **演进说明**: 授权模型已从 OPA/Rego 演进为 RE-ABAC (关系增强型属性访问控制, 编译时预计算), 详见 [a2a/05](/security/llm_agent_defense/a2a/05-authz-models-comparison)。以下 Rego 策略作为**策略定义语言参考**保留, 运行时决策由 RE-ABAC 引擎 (9KB 决策表, O(1) 查表) 执行。

## 2.1 策略设计原则

### 车端权限决策的五个维度

```
┌───────────────────────────────────────────────────────────┐
│              车端 Agent 权限决策的五个维度                   │
│                                                            │
│  ① 域隔离 (Domain Isolation)                               │
│     信息娱乐域不能随意调用底盘域的关键操作                    │
│                                                            │
│  ② ASIL 门控 (Safety Integrity Gating)                     │
│     ASIL-D 操作必须有额外的安全约束                         │
│                                                            │
│  ③ 用户确认 (User Confirmation)                            │
│     安全关键操作需座舱内用户明确同意                         │
│                                                            │
│  ④ 车辆状态 (Vehicle State Context)                        │
│     行驶中 vs 静止 vs 充电 → 允许的操作不同                 │
│                                                            │
│  ⑤ 速率限制 (Rate Limiting)                                │
│     防止单个 Agent 滥用资源或发起 DoS                       │
└───────────────────────────────────────────────────────────┘
```

## 2.2 完整 Rego 策略实现

### 主策略文件: `policy/agent-authz.rego`

```rego
# ============================================================================
# policy/agent-authz.rego
# 车端 Agent 权限策略引擎
# 
# 设计原则:
# - 默认拒绝 (default deny)
# - 白名单模式 (显式允许)
# - 安全关键操作需用户确认
# - 域间隔离 + ASIL 门控
# - 车辆状态感知
# ============================================================================

package vehicle.iam.authz

import rego.v1

# ───────────────────────────────────────────────────────────
# 默认决策
# ───────────────────────────────────────────────────────────

default allow := false

# ───────────────────────────────────────────────────────────
# 允许决策的聚合入口
# ───────────────────────────────────────────────────────────

allow if {
    # 第一步: 基本身份校验
    caller_is_authenticated

    # 第二步: 通过任一授权规则
    any_authorization_rule_applies
}

# ───────────────────────────────────────────────────────────
# 身份校验
# ───────────────────────────────────────────────────────────

caller_is_authenticated if {
    input.caller.spiffe_id != ""
    input.caller.tee_attested == true
    input.caller.certificate_fingerprint != ""
}

# ───────────────────────────────────────────────────────────
# 授权规则聚合
# ───────────────────────────────────────────────────────────

any_authorization_rule_applies if {
    # 规则 1: 同域通信
    same_domain_communication
}

any_authorization_rule_applies if {
    # 规则 2: 跨域非安全操作
    cross_domain_non_safety_action
}

any_authorization_rule_applies if {
    # 规则 3: 跨域安全操作 + 用户确认
    cross_domain_safety_with_user_confirm
}

any_authorization_rule_applies if {
    # 规则 4: 数据读取 (受控)
    controlled_data_read
}

any_authorization_rule_applies if {
    # 规则 5: 基础设施服务
    infrastructure_service
}

# ───────────────────────────────────────────────────────────
# 域定义
# ───────────────────────────────────────────────────────────

domains := {
    "chassis",
    "powertrain", 
    "body",
    "infotainment",
    "adas",
    "connectivity",
    "security",
}

# ───────────────────────────────────────────────────────────
# ASIL 等级定义
# ───────────────────────────────────────────────────────────

asil_hierarchy := {
    "QM":     0,   # Quality Managed — 非安全相关
    "ASIL-A": 1,   # 最低安全等级
    "ASIL-B": 2,
    "ASIL-C": 3,
    "ASIL-D": 4,   # 最高安全等级
}

# ───────────────────────────────────────────────────────────
# 安全关键 Skill 列表
# ───────────────────────────────────────────────────────────

safety_critical_skills := {
    # 底盘域
    "emergency_brake",
    "steering_override",
    "steering_torque_control",
    "brake_pressure_modulate",
    
    # 动力域
    "engine_kill",
    "throttle_override",
    "transmission_neutral_force",
    "battery_disconnect",
    
    # ADAS 域
    "airbag_deploy",
    "seatbelt_pretension",
    "lane_departure_override",
    
    # 车身域
    "unlock_all_doors",
    "disable_immobilizer",
}

# ───────────────────────────────────────────────────────────
# 域间数据共享矩阵
# ───────────────────────────────────────────────────────────

data_sharing_allowed := {
    # 信息娱乐可以读取车身和动力域的非敏感数据
    "infotainment": {"body", "powertrain"},
    
    # ADAS 可以读取底盘和车身域数据
    "adas": {"chassis", "body"},
    
    # 连接域可以读取所有数据 (用于云端诊断)
    "connectivity": {"chassis", "powertrain", "body", "adas"},
    
    # 安全域可以读取一切
    "security": {"chassis", "powertrain", "body", "infotainment", "adas", "connectivity"},
    
    # 以下域不对外暴露数据:
    # "chassis": {}  ← 不定义 = 不共享
    # "powertrain": {}
}

# ───────────────────────────────────────────────────────────
# 规则1: 同域通信
# ───────────────────────────────────────────────────────────

same_domain_communication if {
    input.caller.domain == input.target.domain
    not is_excluded_intra_domain
}

# 同域内的例外: ASIL 跳级调用
is_excluded_intra_domain if {
    input.caller.domain == input.target.domain
    caller_asil := asil_hierarchy[input.caller.asil_level]
    target_asil := asil_hierarchy[input.target.asil_level]
    
    # QM 不能直接调 ASIL-D（即使同域）
    caller_asil <= 1
    target_asil >= 4
    is_safety_critical_action
}

# ───────────────────────────────────────────────────────────
# 规则2: 跨域非安全操作
# ───────────────────────────────────────────────────────────

cross_domain_non_safety_action if {
    input.caller.domain != input.target.domain
    not is_safety_critical_action
    not is_safety_sensitive_domain_pair
    
    # 调用方 TEE 已验证
    input.caller.tee_attested
}

# 敏感域对: 即使非安全操作也需要额外检查
is_safety_sensitive_domain_pair if {
    input.caller.domain == "infotainment"
    input.target.domain == "adas"
}

is_safety_sensitive_domain_pair if {
    input.caller.domain == "infotainment"
    input.target.domain == "chassis"
}

# ───────────────────────────────────────────────────────────
# 规则3: 安全关键操作 — 必须用户确认
# ───────────────────────────────────────────────────────────

cross_domain_safety_with_user_confirm if {
    is_safety_critical_action
    
    # 必须有用户确认
    input.context.user_confirmed == true
    
    # 用户确认有时效性
    not user_confirmation_expired
    
    # 车辆必须在安全状态下 (非行驶中)
    vehicle_in_safe_state_for_critical_action
}

is_safety_critical_action if {
    input.action.type == "skill_invoke"
    input.action.skill_id in safety_critical_skills
}

is_safety_critical_action if {
    input.action.type == "tool_call"
    input.action.tool_id in safety_critical_skills
}

# 用户确认有效期: 30 秒
# （防止预先确认后延迟执行）
user_confirmation_expired if {
    confirmation_time := input.context.user_confirmation_timestamp
    current_time := time.now_ns() / 1000000000
    (current_time - confirmation_time) > 30
}

vehicle_in_safe_state_for_critical_action if {
    input.context.vehicle_state in {"parked", "stopped"}
}

# 例外: 紧急制动可以在行驶中执行 (有用户确认即可)
vehicle_in_safe_state_for_critical_action if {
    input.action.skill_id == "emergency_brake"
    input.context.vehicle_state == "moving"
    input.context.user_confirmed == true
    input.context.collision_risk == "high"
}

# ───────────────────────────────────────────────────────────
# 规则4: 受控数据读取
# ───────────────────────────────────────────────────────────

controlled_data_read if {
    input.action.type == "data_read"
    
    # 调用方与目标同域 → 直接允许
    input.caller.domain == input.target.domain
}

controlled_data_read if {
    input.action.type == "data_read"
    
    # 调用方在目标域的共享白名单中
    data_sharing_allowed[input.caller.domain][_] == input.target.domain
    
    # 但不是读取 PII (个人身份信息)
    not is_pii_read
}

is_pii_read if {
    input.action.data_category in {
        "location_gps",
        "cabin_camera",
        "driver_identity",
        "phone_contacts",
        "voice_recordings",
    }
}

# ───────────────────────────────────────────────────────────
# 规则5: 基础设施服务 (IAM, Registry, Gateway 自身)
# ───────────────────────────────────────────────────────────

infrastructure_service if {
    input.target.domain == "security"
    input.target.component_type in {"registry", "gateway", "iam"}
    
    # 基础设施服务仅允许被其他 Agent 读取/查询
    input.action.type in {"data_read", "skill_invoke"}
    not is_safety_critical_action
}

# ───────────────────────────────────────────────────────────
# 车辆状态感知
# ───────────────────────────────────────────────────────────

# 行驶中禁止的操作
deny_during_motion if {
    input.context.vehicle_state == "moving"
    input.action.skill_id in motion_prohibited_skills
}

motion_prohibited_skills := {
    "flash_ecu",
    "disable_traction_control",
    "calibrate_steering_angle",
    "deploy_airbag_test",
}

# ───────────────────────────────────────────────────────────
# 速率限制
# ───────────────────────────────────────────────────────────

# 每组 Skill 的速率限制配置
skill_rate_limits := {
    # 读取类操作 — 高频允许
    "read_speed":         {"max_per_second": 100, "burst": 200},
    "read_engine_rpm":    {"max_per_second": 50,  "burst": 100},
    "read_gps":           {"max_per_second": 1,   "burst": 5},
    "read_dtc":           {"max_per_second": 10,  "burst": 20},
    
    # 控制类操作 — 严格限制
    "set_cabin_temp":     {"max_per_second": 5,   "burst": 10},
    "actuate_brake":      {"max_per_second": 20,  "burst": 30},
    "steering_control":   {"max_per_second": 50,  "burst": 60},
    
    # 安全关键操作 — 最严格限制
    "emergency_brake":    {"max_per_second": 10,  "burst": 10},
    "steering_override":  {"max_per_second": 10,  "burst": 10},
    "engine_kill":        {"max_per_second": 1,   "burst": 1},
}

# 默认速率限制
default_rate_limit := {"max_per_second": 30, "burst": 50}

# 检查速率限制是否超出
rate_limit_exceeded if {
    limit := object.get(skill_rate_limits, input.action.skill_id, default_rate_limit)
    
    # 从 data.ratelimit 获取当前计数
    current_count := data.ratelimit.count(
        input.caller.spiffe_id,
        input.action.skill_id,
    )
    
    current_count > limit.max_per_second
}

# 速率限制检查 (在 allow 规则中引用)
allow if {
    # ... 其他条件 ...
    not rate_limit_exceeded
}

# ───────────────────────────────────────────────────────────
# 权限决策的详细信息 (用于审计日志)
# ───────────────────────────────────────────────────────────

deny_reason contains reason if {
    not caller_is_authenticated
    reason := "caller_not_authenticated"
}

deny_reason contains reason if {
    is_safety_critical_action
    not input.context.user_confirmed
    reason := "safety_critical_action_requires_user_confirmation"
}

deny_reason contains reason if {
    is_safety_critical_action
    user_confirmation_expired
    reason := "user_confirmation_expired"
}

deny_reason contains reason if {
    input.action.skill_id in motion_prohibited_skills
    input.context.vehicle_state == "moving"
    reason := "action_prohibited_while_vehicle_moving"
}

deny_reason contains reason if {
    rate_limit_exceeded
    reason := "rate_limit_exceeded"
}

deny_reason contains reason if {
    input.caller.domain != input.target.domain
    not data_sharing_allowed[input.caller.domain]
    reason := "cross_domain_access_not_in_sharing_matrix"
}

deny_reason contains reason if {
    is_pii_read
    reason := "pii_data_read_not_allowed"
}
```

### 策略测试文件: `policy/agent-authz_test.rego`

```rego
# ============================================================================
# policy/agent-authz_test.rego
# OPA 策略单元测试
# ============================================================================

package vehicle.iam.authz

# ───────────────────────────────────────────────────────────
# 测试: 同域通信允许
# ───────────────────────────────────────────────────────────

test_same_domain_allow if {
    allow with input as {
        "caller": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/chassis/agent/brake-controller",
            "domain": "chassis",
            "asil_level": "ASIL-D",
            "tee_attested": true,
            "certificate_fingerprint": "sha256:abc",
        },
        "target": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/chassis/agent/suspension-controller",
            "domain": "chassis",
            "asil_level": "ASIL-C",
        },
        "action": {
            "type": "skill_invoke",
            "skill_id": "read_suspension_status",
        },
        "context": {
            "vehicle_state": "moving",
            "user_confirmed": false,
        },
    }
}

# ───────────────────────────────────────────────────────────
# 测试: 跨域安全操作无用户确认 → 拒绝
# ───────────────────────────────────────────────────────────

test_cross_domain_safety_without_confirm_deny if {
    not allow with input as {
        "caller": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/infotainment/agent/voice-assistant",
            "domain": "infotainment",
            "asil_level": "QM",
            "tee_attested": true,
            "certificate_fingerprint": "sha256:def",
        },
        "target": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/chassis/agent/brake-controller",
            "domain": "chassis",
            "asil_level": "ASIL-D",
        },
        "action": {
            "type": "skill_invoke",
            "skill_id": "emergency_brake",
        },
        "context": {
            "vehicle_state": "moving",
            "user_confirmed": false,
        },
    }
}

# ───────────────────────────────────────────────────────────
# 测试: 跨域安全操作有用户确认 → 允许
# ───────────────────────────────────────────────────────────

test_cross_domain_safety_with_confirm_allow if {
    allow with input as {
        "caller": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/infotainment/agent/voice-assistant",
            "domain": "infotainment",
            "asil_level": "QM",
            "tee_attested": true,
            "certificate_fingerprint": "sha256:def",
        },
        "target": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/chassis/agent/brake-controller",
            "domain": "chassis",
            "asil_level": "ASIL-D",
        },
        "action": {
            "type": "skill_invoke",
            "skill_id": "emergency_brake",
        },
        "context": {
            "vehicle_state": "moving",
            "user_confirmed": true,
            "user_confirmation_timestamp": 1753972200,
            "collision_risk": "high",
        },
    }
}

# ───────────────────────────────────────────────────────────
# 测试: QM 调 ASIL-D 同域 → 拒绝
# ───────────────────────────────────────────────────────────

test_qm_to_asil_d_intra_domain_deny if {
    not allow with input as {
        "caller": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/chassis/agent/data-logger",
            "domain": "chassis",
            "asil_level": "QM",
            "tee_attested": true,
            "certificate_fingerprint": "sha256:ghi",
        },
        "target": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/chassis/agent/brake-controller",
            "domain": "chassis",
            "asil_level": "ASIL-D",
        },
        "action": {
            "type": "skill_invoke",
            "skill_id": "emergency_brake",
        },
        "context": {
            "vehicle_state": "parked",
            "user_confirmed": false,
        },
    }
}

# ───────────────────────────────────────────────────────────
# 测试: TEE 未证明 → 拒绝
# ───────────────────────────────────────────────────────────

test_not_tee_attested_deny if {
    not allow with input as {
        "caller": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/body/agent/climate",
            "domain": "body",
            "asil_level": "QM",
            "tee_attested": false,
            "certificate_fingerprint": "sha256:jkl",
        },
        "target": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/body/agent/door-controller",
            "domain": "body",
            "asil_level": "QM",
        },
        "action": {
            "type": "skill_invoke",
            "skill_id": "lock_doors",
        },
        "context": {
            "vehicle_state": "parked",
            "user_confirmed": false,
        },
    }
}

# ───────────────────────────────────────────────────────────
# 测试: 受控数据读取允许
# ───────────────────────────────────────────────────────────

test_data_read_infotainment_reads_body if {
    allow with input as {
        "caller": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/infotainment/agent/climate-ui",
            "domain": "infotainment",
            "asil_level": "QM",
            "tee_attested": true,
            "certificate_fingerprint": "sha256:mno",
        },
        "target": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/body/agent/climate",
            "domain": "body",
            "asil_level": "QM",
        },
        "action": {
            "type": "data_read",
            "skill_id": "read_cabin_temperature",
            "data_category": "climate",
        },
        "context": {
            "vehicle_state": "moving",
            "user_confirmed": false,
        },
    }
}

# ───────────────────────────────────────────────────────────
# 测试: 行驶中禁止 ECU 刷写
# ───────────────────────────────────────────────────────────

test_flash_ecu_during_motion_deny if {
    not allow with input as {
        "caller": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/connectivity/agent/ota-manager",
            "domain": "connectivity",
            "asil_level": "QM",
            "tee_attested": true,
            "certificate_fingerprint": "sha256:pqr",
        },
        "target": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/powertrain/agent/ecu-manager",
            "domain": "powertrain",
            "asil_level": "ASIL-B",
        },
        "action": {
            "type": "skill_invoke",
            "skill_id": "flash_ecu",
        },
        "context": {
            "vehicle_state": "moving",
            "user_confirmed": false,
        },
    }
}

# ───────────────────────────────────────────────────────────
# 测试: 用户确认过期 → 拒绝
# ───────────────────────────────────────────────────────────

test_user_confirmation_expired_deny if {
    not allow with input as {
        "caller": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/infotainment/agent/voice-assistant",
            "domain": "infotainment",
            "asil_level": "QM",
            "tee_attested": true,
            "certificate_fingerprint": "sha256:stu",
        },
        "target": {
            "spiffe_id": "spiffe://vehicle-LSVN123.local/chassis/agent/brake-controller",
            "domain": "chassis",
            "asil_level": "ASIL-D",
        },
        "action": {
            "type": "skill_invoke",
            "skill_id": "emergency_brake",
        },
        "context": {
            "vehicle_state": "parked",
            "user_confirmed": true,
            "user_confirmation_timestamp": 1753971200,  # > 30s 前
        },
    }
}
```

---

# 专题三: A2A TASK_STATE_AUTH_REQUIRED — HMI 用户确认场景深度调研

## 3.1 A2A TaskState 完整定义

### 状态机 (来自 a2a.proto)

```
A2A Task 状态机:

                    ┌──────────────────────────┐
                    │   TASK_STATE_UNSPECIFIED  │ (0)
                    └────────────┬─────────────┘
                                 │ SendMessage
                                 ▼
                    ┌──────────────────────────┐
                    │   TASK_STATE_SUBMITTED    │ (1)
                    └────────────┬─────────────┘
                                 │ Agent 开始处理
                                 ▼
                    ┌──────────────────────────┐
         ┌─────────│    TASK_STATE_WORKING     │ (2) ──────────┐
         │         └────────────┬─────────────┘               │
         │                      │                              │
         │         ┌────────────┼──────────────┐               │
         │         ▼            ▼              ▼               │
         │  ┌────────────┐ ┌──────────┐ ┌──────────────┐       │
         │  │ INPUT      │ │ AUTH     │ │  (继续处理)   │       │
         │  │ _REQUIRED  │ │ _REQUIRED│ │              │       │
         │  │ (6)        │ │ (8)      │ │              │       │
         │  └─────┬──────┘ └────┬─────┘ │              │       │
         │        │             │       │              │       │
         │        │  输入/授权   │       │              │       │
         │        │  已提供     │       │              │       │
         │        └──────┬──────┘       │              │       │
         │               │              │              │       │
         │               ▼              ▼              ▼       │
         │         ┌──────────────────────────┐               │
         │         │    TASK_STATE_COMPLETED   │ (3) 终态      │
         │         └──────────────────────────┘               │
         │                                                    │
         ├──────────────┐    ┌──────────────┐    ┌──────────┐ │
         ▼              ▼    ▼              ▼    ▼          ▼ │
  ┌──────────┐  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
  │  FAILED  │  │ CANCELED │ │ REJECTED │ │ (回到WORKING) │   │
  │  (4)     │  │ (5)      │ │ (7)      │ │              │   │
  └──────────┘  └──────────┘ └──────────┘ └──────────────┘   │
    终态           终态          终态                         │
                                                             │
  Interrupted States (可恢复): INPUT_REQUIRED(6), AUTH_REQUIRED(8)
  Terminal States (不可逆): COMPLETED(3), FAILED(4), CANCELED(5), REJECTED(7)
```

### AUTH_REQUIRED 的协议定义

```
A2A 规范 Section 7.6:

TASK_STATE_AUTH_REQUIRED 的含义:
  "Additional authorization is required to proceed."
  
Agent 责任:
  1. MUST use a Task to track the operation
  2. MUST transition the TaskState to TASK_STATE_AUTH_REQUIRED
  3. MUST include a TaskStatus message explaining what authorization is needed

Client 责任:
  - 可以向人类、其他 Agent、或其他服务请求授权
  - 可以通过 out-of-band 方式提供凭证
  - 可以发送 response message 拒绝授权

⚠ 规范明确声明:
  "The A2A protocol does not define the scope, representation, 
   validity, or revocation semantics of the authorization decision 
   or credential obtained in response to this state."
   
  → 这意味着: A2A 只提供 "需要授权" 的信号机制
              具体的授权方式和内容是实现方定义的
```

---

## 3.2 车端是否需要 HMI 用户确认 — 场景分析

### 核心问题: A2A 的 AUTH_REQUIRED 和 HMI 用户确认是什么关系？

```
答案: A2A 的 TASK_STATE_AUTH_REQUIRED 是传输机制 (HOW)，
      HMI 用户确认是授权方式的一种 (WHAT)。

两者不在同一层:
  - A2A AUTH_REQUIRED: 协议层状态信号,告诉 Client "我需要授权"
  - HMI 用户确认:     应用层授权方式,通过座舱交互获得人类同意
```

### 车端典型场景矩阵

| 场景 | Agent 调用关系 | 是否需要用户确认 | 使用 A2A AUTH_REQUIRED? |
|------|--------------|----------------|----------------------|
| **场景1**: 语音助手读车速 | Infotainment→Chassis data_read | ❌ 不需要 | ❌ 不需要 |
| **场景2**: ADAS 自动紧急制动 | ADAS→Chassis emergency_brake | ❌ 不需要 (自动触发) | ❌ 不需要 |
| **场景3**: 语音助手请求紧急制动 | Infotainment→Chassis emergency_brake | ⚠️ **需要** | ✅ **需要** |
| **场景4**: OTA 升级开始 | Connectivity→各域 flash_ecu | ⚠️ **需要** (行驶中禁止) | ✅ **需要** |
| **场景5**: 远程开门 | Cloud→Body unlock_doors | ⚠️ **需要** (防盗要求) | ✅ **需要** |
| **场景6**: 诊断工具读 DTC | Tester→Powertrain read_dtc | ❌ 不需要 | ❌ 不需要 |
| **场景7**: 执行器测试 | Tester→Chassis actuate_brake | ⚠️ **需要** (车间场景) | ✅ **需要** |
| **场景8**: 语音调空调 | Infotainment→Body set_temp | ❌ 不需要 | ❌ 不需要 |

### 判断是否需要用户确认的决策树

```
// 是否需要用户确认？

// 问自己三个问题:

// Q1: 这个操作是安全关键的吗？
//    (是否在 safety_critical_skills 列表中?)
//    → YES: 需要确认 (少数例外: ADAS 自动触发)
//    → NO:  继续 Q2

// Q2: 这个操作会导致物理世界的变化吗？
//    (actuate/unlock/disable/deploy/flash/...)
//    → YES: 继续 Q3
//    → NO:  不需要确认 (纯数据读取)

// Q3: 调用方是来自低安全域吗？
//    (调用方 ASIL 等级 < 目标 ASIL 等级)
    或 (调用方 domain 是 infotainment/connectivity)
    → YES: 需要确认
    → NO:  不需要确认 (如 ADAS→Chassis, 同安全等级的物理操作)

例外:
  - ADAS 自动紧急制动: 机器自主决策，不需要用户确认
  - 安全监控 Agent: 来自 security 域，具有最高权限
```

---

## 3.3 A2A AUTH_REQUIRED 在 HMI 确认场景的完整实现

### 场景: 语音助手请求紧急制动

这是最完整的端到端场景，涉及 A2A、IAM、HMI 三层：

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    A2A AUTH_REQUIRED + HMI 确认流程                        │
│                    场景: 语音助手 → 紧急制动                                │
└──────────────────────────────────────────────────────────────────────────┘

Phase 1: 初始请求 (A2A SendMessage)
─────────────────────────────────────

  Voice Agent (infotainment)                  ADAS Agent (chassis)
       │                                            │
       │  POST /message:send                          │
       │  {                                           │
       │    "message": {                              │
       │      "messageId": "msg-001",                 │
       │      "role": "ROLE_USER",                    │
       │      "parts": [{                             │
       │        "text": "前方有障碍物，请紧急制动"      │
       │      }]                                      │
       │    },                                        │
       │    "configuration": {                        │
       │      "return_immediately": false    # 同步等待  │
       │    }                                         │
       │  }                                           │
       │─────────────────────────────────────────────→│
       │                                            │
       │                          IAM interceptor:   │
       │                          ① mTLS → SPIFFE ID:│
       │                             voice-assistant │
       │                          ② OPA 评估:         │
       │                             domain=infotain. │
       │                             skill=emergency_ │
       │                               brake          │
       │                             user_confirmed=  │
       │                               false          │
       │                          ③ 决策: DENY        │
       │                             但 agent 可以     │
       │                             请求授权...       │
       │                                            │
       │                          A2A Handler:       │
       │                          ④ 创建 Task         │
       │                          ⑤ TaskState =      │
       │                             AUTH_REQUIRED    │
       │                          ⑥ TaskStatus:       │
       │                             "紧急制动需要     │
       │                              用户确认"       │
       │                                            │
       │←── Task { state: AUTH_REQUIRED, ... } ──────│

Phase 2: HMI 用户确认
─────────────────────

  Voice Agent                    HMI System                   User
       │                            │                          │
       │  收到 AUTH_REQUIRED        │                          │
       │  + TaskStatus message      │                          │
       │                            │                          │
       │  提取确认请求:              │                          │
       │  - 操作: emergency_brake   │                          │
       │  - 原因: 前方障碍物         │                          │
       │  - 风险: ASIL-D 安全关键   │                          │
       │                            │                          │
       │──→ HMI_ShowConfirmDialog ──→│                          │
       │    {                       │                          │
       │      type: "safety_action",│      ┌──────────────┐    │
       │      title: "紧急制动",    │      │ ⚠ 紧急制动    │    │
       │      message: "前方检测到  │      │              │    │
       │        障碍物，是否执行紧  │      │ 前方检测到障碍│    │
       │        急制动？",          │      │ 物，是否执行  │    │
       │      confirm_text: "制动", │      │ 紧急制动？    │    │
       │      cancel_text: "取消",  │      │              │    │
       │      timeout_ms: 5000,     │      │ [制动] [取消] │    │
       │      require_auth: true,   │      └──────┬───────┘    │
       │    }                       │             │ 点击 [制动] │
       │                            │←────────────│────────────│
       │←── HMI_ConfirmResult ──────│                          │
       │    {                       │                          │
       │      confirmed: true,      │                          │
       │      user_action: "CONFIRM",│                         │
       │      timestamp: 1753972200,│                          │
       │      confirmation_id:      │                          │
       │        "uci-20250731-...", │                          │
       │    }                       │                          │

Phase 3: 携带确认信息的重试 (A2A SendMessage, same contextId)
─────────────────────────────────────────────────────────────

  Voice Agent                                    ADAS Agent
       │                                            │
       │  POST /message:send                          │
       │  {                                           │
       │    "message": {                              │
       │      "messageId": "msg-002",                 │
       │      "role": "ROLE_USER",                    │
       │      "contextId": "ctx-abc123",              │
       │      "taskId": "task-brake-001",             │
       │      "parts": [{                             │
       │        "text": "用户已确认，继续执行紧急制动"  │
       │      }],                                     │
       │      "metadata": {                           │
       │        "vehicle.iam/confirmation": {         │
       │          "confirmed": true,                  │
       │          "confirmation_id": "uci-...",       │
       │          "timestamp": 1753972200             │
       │        }                                     │
       │      }                                       │
       │    }                                         │
       │  }                                           │
       │─────────────────────────────────────────────→│
       │                                            │
       │                          IAM interceptor:   │
       │                          ① mTLS 验证         │
       │                          ② 提取 metadata 中  │
       │                             的 confirmation  │
       │                          ③ OPA 重新评估:     │
       │                             user_confirmed=   │
       │                               true ✓         │
       │                             timestamp 有效    │
       │                          ④ 决策: ALLOW ✓     │
       │                          ⑤ 审计: 记录确认 ID  │
       │                                            │
       │                          A2A Handler:       │
       │                          ⑥ TaskState =      │
       │                             WORKING →        │
       │                             COMPLETED        │
       │                          ⑦ 添加 Artifact:    │
       │                             {                │
       │                               braking: true, │
       │                               decel_ms2: 9.8 │
       │                             }                │
       │                                            │
       │←── Task { state: COMPLETED } ────────────────│
```

### 三种 HMI 确认结果的处理

```
┌─────────────────────────────────────────────────────────────┐
│ 确认结果             A2A 行为               IAM 行为         │
├─────────────────────────────────────────────────────────────┤
│ CONFIRM             继续 Task              audit: ALLOW     │
│ (用户同意)           WORKING→COMPLETED     记录 confirmation │
│                                             _id              │
├─────────────────────────────────────────────────────────────┤
│ CANCEL              TaskState →            audit: DENY      │
│ (用户取消)           CANCELED (终态)        reason:          │
│                     返回 cancel message    "user_cancelled"  │
├─────────────────────────────────────────────────────────────┤
│ TIMEOUT             TaskState →            audit: DENY      │
│ (5秒无响应)          FAILED (终态)          reason:          │
│                     TaskStatus:            "user_confirm     │
│                     "用户未在5秒内          _timeout"         │
│                      确认操作"                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3.4 为什么 AUTH_REQUIRED 是必要的架构组件

### AUTH_REQUIRED vs INPUT_REQUIRED

A2A 有两个 interrupted state，它们的区别很重要：

```
┌────────────────────────────────────────────────────────────┐
│                    INPUT_REQUIRED (6)                       │
│                                                            │
│  用途: Agent 需要更多信息才能继续                           │
│  示例:                                                     │
│    - "你想订哪个时段的航班？"                               │
│    - "请提供你的位置信息"                                   │
│  特点:                                                     │
│    - 是对话式的，信息补充                                   │
│    - 不需要权限提升                                        │
│    - 用户提供完信息后 Agent 继续                            │
│    - 车端示例: "请指定目标温度"                             │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                    AUTH_REQUIRED (8)                        │
│                                                            │
│  用途: Agent 需要更高权限才能继续                            │
│  示例:                                                     │
│    - "紧急制动需要用户确认"                                  │
│    - "刷写 ECU 需要诊断授权"                                │
│  特点:                                                     │
│    - 是授权操作，权限提升                                   │
│    - 涉及安全/合规边界                                      │
│    - IAM 策略引擎重新评估                                   │
│    - 审计日志必须记录                                       │
│    - 车端示例: ASIL-D Skill + 跨域 + 无确认                │
└────────────────────────────────────────────────────────────┘
```

### 为什么不用更简单的方案（如直接返回 Error）？

```
方案A: 直接返回 PERMISSION_DENIED (当前 IAM interceptor 行为)
  ❌ 问题: Client 不知道如何获取授权
  ❌ 问题: 没有结构化的 "你需要什么授权" 信息
  ❌ 问题: 无法在同一个 Task 上下文中重试
  ❌ 问题: 丢失了 A2A 的任务管理能力

方案B: 返回 AUTH_REQUIRED (A2A 原生支持)  
  ✅ 优势: Task 保持存活，contextId 不变
  ✅ 优势: TaskStatus.message 可以详细说明需要什么授权
  ✅ 优势: Client 可以通过标准 A2A 流程获取授权后继续
  ✅ 优势: 支持授权链 (Client → Sub-Client → User)
  ✅ 优势: streaming/polling/subscribe 机制自动处理状态通知
```

---

## 3.5 车端 AUTH_REQUIRED + HMI 的设计决策总结

### 关键设计决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| **何时触发 AUTH_REQUIRED** | IAM 鉴权失败 + 操作是可确认恢复的 | 不是所有 DENY 都可恢复 (如域名不匹配) |
| **确认方式** | A2A metadata: `vehicle.iam/confirmation` | 不侵入 A2A 标准消息体 |
| **确认有效期** | 30 秒 (OPA 中配置) | 防止预确认后状态变化带来的风险 |
| **确认身份绑定** | confirmation_id + SPIFFE ID + taskId | 三方绑定防重放 |
| **HMI 超时处理** | Task → FAILED | 明确告知用户操作未执行 |
| **审计要求** | 记录完整确认链: user→HMI→Voice Agent→ADAS | 满足功能安全追溯要求 |
| **紧急制动例外** | ADAS 自触发不需要确认，语音触发需要 | 区分自动安全功能 vs 用户发起的危险操作 |

### AUTH_REQUIRED 与 IAM 的协作模式

```
          A2A 层                        IAM 层
    ┌─────────────────┐          ┌─────────────────┐
    │                  │          │                  │
    │ 1. 接收请求      │          │                  │
    │                  │          │                  │
    │ 2. 调用 IAM ────┼─────────→│ 3. OPA 决策      │
    │                  │          │    → DENY        │
    │                  │←─────────│    + 建议:        │
    │                  │          │    auth_required  │
    │                  │          │    + reason       │
    │ 4. 判断 DENY     │          │                  │
    │    是否可恢复?   │          │                  │
    │    YES →         │          │                  │
    │    AUTH_REQUIRED │          │                  │
    │    NO →          │          │                  │
    │    PERMISSION_   │          │                  │
    │    DENIED        │          │                  │
    │                  │          │                  │
    │ 5. TaskState =   │          │                  │
    │    AUTH_REQUIRED │          │                  │
    │                  │          │                  │
    │ 6. Client 获取   │          │                  │
    │    用户确认后     │          │                  │
    │    重试 ─────────┼─────────→│ 7. OPA 重新决策  │
    │                  │          │    → ALLOW ✓     │
    │                  │←─────────│    + audit       │
    │                  │          │                  │
    │ 8. 继续 Task     │          │                  │
    │    WORKING →     │          │                  │
    │    COMPLETED     │          │                  │
    └─────────────────┘          └─────────────────┘
```

### IAM 给 A2A 的决策增强

```json
// IAM interceptor 的决策结果 (不仅是 true/false)
{
  "decision": "DENY",
  "reason": "safety_critical_action_requires_user_confirmation",
  "recoverable": true,
  "recovery_hint": {
    "type": "AUTH_REQUIRED",
    "required_authorization": "user_confirmation",
    "confirmation_prompt": {
      "title": "紧急制动",
      "message": "前方检测到障碍物，是否执行紧急制动？",
      "confirm_text": "制动",
      "cancel_text": "取消",
      "timeout_ms": 5000
    },
    "confirmation_binding": {
      "task_id": "task-brake-001",
      "skill_id": "emergency_brake",
      "caller_spiffe_id": "spiffe://vehicle-LSVN123.local/infotainment/agent/voice-assistant"
    }
  }
}
```

这个结构化的决策结果让 A2A Handler 可以直接构造合适的 `TASK_STATE_AUTH_REQUIRED` 响应，Client (Voice Agent) 也能直接渲染 HMI 确认对话框——全程不需人工编码确认逻辑，策略即代码。

---

## 总结：三大专题的核心关系

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│    KMSS      │     │   OPA Rego   │     │  A2A AUTH_REQUIRED│
│              │     │              │     │                  │
│ 提供:        │     │ 提供:        │     │ 提供:             │
│ - Agent 身份 │────→│ - 引用身份   │     │ - 授权状态机      │
│ - mTLS 证书  │     │   做权限决策 │     │ - Task 中断/恢复  │
│ - TEE 证明   │     │              │     │                  │
│              │     │ 输出:        │     │ 触发时机:         │
│              │     │ - ALLOW/DENY │────→│ OPA DENY +        │
│              │     │ - 可恢复性   │     │ recoverable=true  │
│              │     │ - 恢复提示   │     │ → AUTH_REQUIRED   │
│              │     │              │     │                  │
└──────────────┘     └──────────────┘     └──────────────────┘
       ↑                    ↑                     │
       │                    │                     │
       └────────────────────┼─────────────────────┘
                            │
                     ┌──────▼──────┐
                     │   HMI 系统   │
                     │              │
                     │ - 渲染确认框  │
                     │ - 收集用户   │
                     │   确认/拒绝  │
                     └─────────────┘

三者的数据流:
  KMSS → (证书+SAN) → IAM(OPA) → (决策+恢复提示) → A2A → (TaskState) → HMI
```

这三者共同构成了车端 Agent 安全的完整闭环：**KMSS 负责"你是谁"、OPA 负责"你能不能"、A2A AUTH_REQUIRED 负责"你暂时不能的话怎么才能"。**
