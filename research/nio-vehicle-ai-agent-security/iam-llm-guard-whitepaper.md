# 车载 IAM + LLM Guard 综合白皮书 v1.0

> **版本**: v1.0
> **日期**: 2026-07-21
> **状态**: 评审稿
> **受众**: 架构师 / 安全团队 / 框架实施 / KMSS 团队 / 评审委员会
> **整合自**: 7 份 research 文档 + Framework v2.0 整合 spec

### 整合源

| 文档 | 核心贡献 |
|------|----------|
| AI Agent IAM 调研 | 6 层防护栈 / NHI / Least Agency / 4 大 IAM 平台 |
| 车载端侧 AI 安全 | 车规三层标准 / 物理安全 / 传感器对抗 |
| LLM 应用安全架构 | 三层平面 / 5 层信任域 / 7 个控制点 |
| OWASP LLM Top 10 防御 | LLM01-10 详细防御 + 30 开源工具 |
| MITRE ATLAS 101 | ATLAS 基础概念 |
| 委托链标准调研 | OIDC-A / SPIFFE / JWT-SVID |
| ASG 车规形态 | 单进程 + 2 Gate 实现 |
| Framework v2.0 | 完整 spec |

---

## 目录

```
第 1 章 — 知识地图与整合逻辑
第 2 章 — 基础威胁模型（OWASP / ATLAS / 车规）
第 3 章 — 车端 IAM 体系
第 4 章 — LLM Guard 体系
第 5 章 — 三域差异化（座舱 / 智驾 / 车控）
第 6 章 — ASG 实现形态
第 7 章 — 协议与接口
第 8 章 — 关键流程
第 9 章 — 实施路线图
第 10 章 — 风险与缓解
附录 A — 术语表
附录 B — 开源工具清单
附录 C — 参考资料
附录 D — 修订历史
```

---

## 第 1 章 — 知识地图与整合逻辑

### 1.1 为什么需要整合

NIO 车端 AI Agent 安全框架经过多轮调研、专项研究、原型设计，已经积累了 **8 份核心文档**。这些文档**互相补充、互相引用**，但存在以下问题：

- **术语不一致**: ASG 用 `Ticket` / Framework 用 `JWT-SVID` / 调研用 `SVID`
- **威胁编号不统一**: Framework 用 `T-01..T-10` / ASG 用 `T-1..T-5` / OWASP 用 `LLM01-10` / `ASI01-10`
- **粒度不统一**: 调研文档偏概念 / Framework 偏协议 / ASG 偏实现
- **车规映射不显式**: ISO 26262 / 21434 / 中国三剑客未贯穿到所有模块

**整合目标**: 形成一份**统一术语、统一架构、统一威胁编号**的"知识金字塔"白皮书，让任何工程师/评审者从一份文档就能 get 全貌。

### 1.2 知识金字塔（自上而下）

```
                  ┌─────────────────────────────┐
                  │  Tier 6: NIO Framework + ASG │  ← 顶层设计
                  │  (JWT-SVID + gRPC + 3 层凭证) │
                  └────────────┬────────────────┘
                               │
                  ┌────────────┴────────────────┐
                  │  Tier 5: 协议与标准           │  ← 委托链标准
                  │  (OIDC-A / SPIFFE / RFC 8693) │
                  └────────────┬────────────────┘
                               │
                  ┌────────────┴────────────────┐
                  │  Tier 4: LLM 应用安全架构     │  ← 5 层信任域 + 7 控制点
                  │  (三层平面 / 数据流 / 入口)  │
                  └────────────┬────────────────┘
                               │
                  ┌────────────┴────────────────┐
                  │  Tier 3: 通用 Agent 安全     │  ← 6 层防护栈
                  │  (NHI / Least Agency / IAM)   │
                  └────────────┬────────────────┘
                               │
                  ┌────────────┴────────────────┐
                  │  Tier 2: 威胁模型            │  ← 顶层威胁
                  │  (OWASP LLM01-10 + ASI01-10)  │
                  └────────────┬────────────────┘
                               │
                  ┌────────────┴────────────────┐
                  │  Tier 1: 基础                │  ← AI 安全入门
                  │  (MITRE ATLAS 101)            │
                  └─────────────────────────────┘
```

### 1.3 整合逻辑

| 层级 | 来源文档 | 整合产物 |
|------|----------|----------|
| Tier 1 | AI-Security-101-CN | 第 2 章基础：MITRE ATLAS 概念 |
| Tier 2 | owasp-llm-top10-defenses + ai-agent-security-iam | 第 2 章：OWASP LLM01-10 + ASI01-10 映射 |
| Tier 3 | ai-agent-security-iam | 第 3 章：6 层防护栈 / NHI / Least Agency |
| Tier 4 | llm-app-security-architecture | 第 4 章：5 层信任域 / 7 控制点 |
| Tier 5 | llm-agent-delegation-research-2026 | 第 3 章：委托链 / JWT-SVID / SPIFFE |
| Tier 6 | nio-asg-design + Framework v2.0 | 第 5-8 章：三域差异化 + ASG + 接口 + 流程 |
| 全局 | vehicle-edge-ai-security | 第 2.4 + 第 5 章：车规三层标准 + 三域差异化 |

---

## 第 2 章 — 基础威胁模型

### 2.1 OWASP LLM Top 10 (2025) + ASI01-10 合并

| 编号 | 威胁 | 描述 | 来源 |
|------|------|------|------|
| **T-01** | **Excessive Agency** (LLM06 / ASI01) | Agent 权限过大，自主决策超出授权 | LLM06 + ASI01 |
| **T-02** | **Prompt Injection** (LLM01) | 直接/间接注入操纵 LLM 行为 | LLM01 |
| **T-03** | **Identity & Privilege Abuse** (ASI03) | 身份伪造、越权委托 | ASI03 |
| **T-04** | **Tool Misuse** (ASI04-07) | 工具被滥用、影子工具 | ASI04-07 |
| **T-05** | **Supply Chain** (LLM03 / ASI08) | 模型/数据/依赖被污染 | LLM03 + ASI08 |
| **T-06** | **Data Leakage** (LLM02 / ASI09) | PII / 训练数据 / 上下文泄露 | LLM02 + ASI09 |
| **T-07** | **Untrusted Output** (LLM05) | 输出未做校验直接执行 | LLM05 |
| **T-08** | **DoS / Unbounded Consumption** (LLM10 / ASI10) | 资源耗尽 | LLM10 + ASI10 |
| **T-09** | **Cascading Failure** (车端特有) | 多 Agent 委托链级联失控 | 自有 |
| **T-10** | **Audit Gap** (车端特有) | 审计缺失、不可追溯 | 自有 |

**业界共识**: LLM06 "过度代理"（T-01）是 Agent 场景的**最大新型风险**，直接催生 **"Least Agency"** 原则（见第 3.2）。

### 2.2 MITRE ATLAS 框架

**ATLAS (Adversarial Threat Landscape for AI Systems)** 是 MITRE 专门针对 AI 系统的威胁框架，类比 ATT&CK。

**核心概念**:
- **AI 介入时机**: 训练 (training) / 推理 (inference)
- **AI 介入点**: 数字 (digital) / 物理 (physical)
- **系统知识**: 白盒 / 黑盒

**5 大类对抗性攻击**:

| 攻击类型 | 描述 | 车端相关性 |
|---------|------|----------|
| **投毒 (Poisoning)** | 修改训练数据植入后门 | 端到端驾驶模型 (端云协同训练) |
| **规避 (Evasion)** | 对抗性扰动让模型误分类 | 智驾感知 / 物理对抗贴纸 |
| **功能提取 (Extraction)** | 黑盒查询复刻模型 | OTA 升级时反向工程 |
| **反演 (Inversion)** | 恢复训练数据敏感信息 | 座舱语音/视频回放 |
| **提示注入 (Prompt Injection)** | 操纵 LLM 行为 | 主 Agent 委派时 |

完整列表见 [ATLAS Matrix](https://atlas.mitre.org/matrices/ATLAS)。

### 2.3 车规三层标准（合规基线）

**车端模型的"安全栈设计"必须先满足合规底座，再谈 AI 防护**。车规三层标准：

| 层级 | 标准/法规 | 强制力 | 核心要求 |
|------|----------|--------|----------|
| **国际功能安全** | ISO 26262 | OEM 准入强制 | ASIL A–D 分级；**ASIL-D 冗余 + 多样性 + 故障检测 < 10⁻⁸/h** |
| **国际网络安全** | ISO/SAE 21434:2021 | UN R155 法规强制 | CSMS 网络安全管理体系 + **全生命周期 TARA** + 供应链安全 |
| **国际软件更新** | UN R156 | 法规强制 | OTA 流程 + 回滚机制 + 防篡改 |
| **国际预期功能安全** | ISO 21448 (SOTIF) | 行业推荐 | AI 模型"未知不安全场景" (corner case) |
| **中国整车安全** | GB 44495/44496/44497 (三剑客) | 2026.7 强制 | 整车信息安全 + 软件升级 + 数据保护 |
| **中国数据合规** | 《汽车数据安全管理若干规定》 | 强制 | 座舱语音/视频**境内存储**、**人脸分级保护** |
| **欧盟** | UN R155/R156 / EU AI Act | 强制 | CE 认证 + 持续合规 |

**关键判断**: 没有合规底座，AI 防护技术再好也上不了车。

### 2.4 车端特有威胁（v.s. 云端）

| 维度 | 云端 Agent | 车载端侧模型 | 后果 |
|------|-----------|------------|------|
| **失效后果** | 数据泄露、服务降级 | **人身伤亡** | 必须 ASIL-D |
| **网络依赖** | 默认联网 | **经常离线 / 弱网** | 本地可决策 |
| **资源** | 算力无限 | 100W 功耗上限 / 几十 TOPS | 量化、蒸馏、剪枝 |
| **物理可接触** | 数据中心上锁 | **攻击者可接触整车** | 对抗样本、传感器欺骗 |

**三个被严重低估的新风险**:
1. **物理世界对抗攻击 (Physical Adversarial Attack)**: 贴对抗贴纸到交通标志
2. **传感器欺骗 (Sensing Spoofing)**: GNSS 欺骗、雷达干扰、激光雷达对抗点云
3. **OBD/USB/充电桩的物理注入面**: CAN 总线 + USB + 充电协议 (GB/T 27930, ISO 15118)

### 2.5 威胁编号统一 (T-01..T-10)

整合后的车端威胁编号体系：

```
T-01..T-08  ← 对应 OWASP LLM01-10 + ASI01-10 (8 大类)
T-09        ← Cascading Failure (车端特有)
T-10        ← Audit Gap (车端特有)
```

每个威胁在三域的严重度（§5.4 详细）：

| 威胁 | 座舱 | 智驾 | 车控 |
|------|------|------|------|
| T-01 Excessive Agency | 高 | **严重** | **致命** |
| T-02 Prompt Injection | 中 | 高 | 严重 |
| T-03 Identity Spoofing | 高 | **严重** | **致命** |
| T-04 Tool Misuse | 中 | **严重** | 致命 |
| T-05 Supply Chain | 中 | 高 | **严重** |
| T-06 Data Leakage | 高 | 中 | 高 |
| T-07 Untrusted Output | 中 | **严重** | **致命** |
| T-08 DoS | 低 | 高 | **严重** |
| T-09 Cascading Failure | 中 | **严重** | 致命 |
| T-10 Audit Gap | 高 | **严重** | **严重** |

---

## 第 3 章 — 车端 IAM 体系

### 3.1 NHI (Non-Human Identity) 概念

**传统 IAM 假设"主体=人"**。Agent 时代，这个假设被打破：

| 维度 | 人 (User) | Agent (NHI) |
|------|-----------|-------------|
| 标识 | 用户名/邮箱/手机 | **SPIFFE ID** (spiffe://nio-cockpit/...) |
| 认证 | 密码/生物/2FA | **JWT-SVID + Attestation** |
| 凭证 | OAuth Token | **三层凭证 (L1/L2/L3)** |
| 授权 | RBAC | **OpenFGA 关系型 + Least Agency** |
| 生命周期 | 离职/转岗 | **active / suspended / revoked / destroyed** |
| 责任追溯 | 用户本人 | **追溯到 Sponsor** |

**关键判断**: Agent 是 **"NHI 一等公民"**，需要独立身份、最小权限、凭证轮换、生命周期管理。

### 3.2 Least Agency 原则

**类比"最小权限 (Least Privilege)"，是 Agent 时代的核心安全原则**。

```
传统:  Least Privilege (最小权限)        → RBAC
Agent: Least Agency (最小代理)         → scope + task_purpose + risk_class + depth ≤ 2
```

**4 个维度**:
1. **能力维度**: scope 必须最小 (`nav:reroute` 而非 `nav:*`)
2. **时间维度**: TTL 必须最短 (L3 ≤ 5min)
3. **目的维度**: task_purpose 必须白名单匹配
4. **深度维度**: 委托链 depth ≤ 2（车控域 = 0）

### 3.3 三层凭证体系 (L1/L2/L3)

| 层 | 寿命 | 算法 (POC→生产) | 标准 | 存储 | 撤销 |
|----|------|----------------|------|------|------|
| **L1 持久层** | 跟镜像同寿命 (~3 月) | HS256 → ES256 | SPIFFE + JWT-SVID | TEE 持久区 | OTA 整车级撤销 |
| **L2 运行层** | 1 小时 | HS256 | RFC 8693 + JWT-SVID | TEE 易失区 | 自动过期 |
| **L3 临时层** | 5 分钟 | HS256 | RFC 8693 `act` claim | TEE 临时区 | 任务结束 + 短 TTL |

**L3 JWT-SVID 完整字段** (车端定制版):

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

**车端特有字段**:
- `act.profile`: LLM 模型版本 (车端有多规模 LLM: 30B / 7B / 0.1B)
- `task_purpose`: 任务目的 (用于条件访问)
- `vehicle_id`: 车辆标识 (车端特有, 用于审计)

### 3.4 委托链 (RFC 8693 token-exchange)

**核心协议**: RFC 8693 (OAuth 2.0 Token Exchange)

```
主 Agent 派生 L3 流程:
  1. 主 Agent 发起 token-exchange 请求
     - subject_token = L1 (主 Agent 自身凭证)
     - actor_token = task_ctx (任务上下文)
     - audience = spiffe://nio-cockpit/nav-tool

  2. AS (TPM-AS) 验证:
     - 验 L1 签名
     - 查 OpenFGA 策略 (depth + scope + task_purpose)
     - 检查配额

  3. 颁发 L3 (含 act claim)
     - act.sub = L1.sub (委托链)
     - 5 分钟 TTL
     - 短 TTL + task_purpose 双重防御
```

**车端委托链硬约束**:
- `depth ≤ 2` (车控域 = 0, 永不发 L3)
- `P_child ⊆ P_parent` (权限单调收敛)
- `TTL ≤ 任务期望时长` (强制)

### 3.5 跨域互信 (SPIFFE Federation)

**车端三域 = 三个 Trust Domain**:
- `nio-cockpit` (座舱)
- `nio-driving` (智驾)
- `nio-body` (车控)

**域间互信机制**: SPIFFE Federation Bundle

```
座舱域 ←─Federation Bundle─→ 智驾域
  │                              │
  └──────Federation Bundle───────┘
                ↕
             车控域
```

**关键设计**:
- **整车出厂时预置** Federation Bundle (离线优先)
- **OTA 周期刷新** (7 天 stale_grace_period)
- **车控域只验证不签发** (单向)
- **跨域 ticket 不同 ID** (防重放 + 边界清晰)

### 3.6 Agent 生命周期

```
[*] → Created → Attesting → Active
                      ↓ (失败)
                   Failed → [*]
Active → Suspended → Active (恢复)
Active → Rotating → Active (OTA)
Active → Revoked → Destroyed → [*]
```

**5 大原则** (Identity Management for Agentic AI):
1. **Identification** — 每个 Agent 有独立 ID
2. **Authentication** — Agent 本身要能证明自己
3. **Authorization** — 委托链 + 能力清单
4. **Accountability** — 审计要追溯到 Sponsor
5. **Lifecycle** — 有生有灭, 不留 zombie agent

### 3.7 4 大 IAM 平台对标

| 平台 | 关键设计 | 我们借鉴度 |
|------|----------|----------|
| **Microsoft Entra Agent ID** | Sponsor / Blueprint / Conditional Access | ✅ 高（核心借鉴）|
| **Google Agent Identity** | Cloud IAM 扩展 | ⚠️ 部分（域间互信）|
| **AWS AgentCore Identity** | OAuth + SigV4 | ⚠️ 部分 |
| **Okta for AI Agents** | Workforce Identity for Agents | ⚠️ 参考 |

**借鉴策略**: 借鉴设计思想，不照搬实现。

---

## 第 4 章 — LLM Guard 体系

### 4.1 6 层防护栈 (借鉴 AI Agent IAM 调研)

| 层 | 功能 | 车端实现 |
|----|------|----------|
| **L1 Fence (围栏)** | 沙箱隔离 / 资源限制 | TEE + ASG 进程隔离 |
| **L2 注入检测** | Prompt 注入 / 间接注入 | LLM-Guard 模型 + 规则 |
| **L3 工具守卫** | Tool 描述校验 / Shadowing 检测 | AuthGate ACL + 二进制签名 |
| **L4 执行门** | 工具调用前验证 / 条件访问 | DataGate + Conditional Access |
| **L5 最小权限** | Least Agency / 委托链 | OpenFGA + 三层凭证 |
| **L6 红队门禁** | 持续渗透 / 漏洞发现 | OTA 前自动 fuzz |

**关键判断**: 业界普遍放弃"靠 prompt 工程堵住一切"，转向分层防御。

### 4.2 5 层信任域 + 7 控制点 (借鉴 LLM App Security 架构)

**5 层信任域** (从外到内, 每跨层重新鉴权):

| 信任域 | 包含组件 | 信任等级 | 谁能访问 |
|--------|----------|----------|----------|
| **Public Edge** | CDN / WAF / DDoS 防护 / TLS 终结 | ❌ 完全不可信 | 任何人 |
| **Identity Zone** | API Gateway / Auth Server / Agent ID / Rate Limiter | ⚠️ 已知身份但未授权 | 已认证用户/Agent |
| **App Zone** | 7 个核心控制点 | ✅ 已认证 + 已授权 | 业务应用代码 |
| **Model Zone** | LLM Serving / Model Registry / Guard Models | 🔒 完全可信内部 | 仅 App Zone |
| **Storage Zone** | Vector DB / Doc Store / Audit Log / Secret Manager | 🔒🔒 最高敏感 | 仅明确授权的服务 |

**7 个关键控制点** (LLM 应用安全架构, 全部对应到车端):

| # | 控制点 | 功能 | 车端模块 |
|---|--------|------|----------|
| 1 | **Input Firewall** | 输入注入检测 / 长度限制 | DataGate.check_input |
| 2 | **Prompt Assembly** | 系统提示词拼接 / 来源隔离 | LLM-Guard 拼装层 |
| 3 | **Context Retrieval** | RAG 数据源隔离 / 相似度阈值 | Vector DB 多租户隔离 |
| 4 | **Output Validator** | 输出结构化校验 / 脱敏 | DataGate.check_output |
| 5 | **Action Authorizer** | 工具调用前 ACL | AuthGate + OpenFGA |
| 6 | **Sandbox Executor** | 工具执行环境隔离 | TEE + ASG 进程隔离 |
| 7 | **Audit Logger** | 全链路审计 | Audit Ring Buffer + 上报 |

**跨域规则**:
```
Public → Identity:  必须过 WAF + Auth
Identity → App:     必须有有效 token + scope 验证
App → Model:        必须有 prompt 注入检测 + 内容分区
App → Storage:      必须有 RBAC + tenant 隔离 + 加密
任何 → Observability: 单向上报, 不接受反向调用
任何 → Control:     Policy Pull (拉策略), 不是 Push
```

### 4.3 LLM01-10 详细防御 (借鉴 OWASP 报告)

| ID | 风险 | 车端关键防御 |
|----|------|-------------|
| **LLM01** | Prompt Injection | 输入分区 + 注入检测 (Microsoft Prompt Shields / Llama Prompt Guard 2) + 工具白名单 + 输出守门 |
| **LLM02** | Sensitive Info Disclosure | PII 检测 (Presidio) + 输出脱敏 + 审计日志 |
| **LLM03** | Supply Chain | SBOM + 签名 (Sigstore) + 来源审计 (AIBOM) |
| **LLM04** | Data and Model Poisoning | 数据来源审计 + 差分隐私 + 检索评估 (RAGAS / TRIDENT) |
| **LLM05** | Improper Output Handling | 结构化输出 (Instructor / Outlines) + 参数化 + 沙箱 (Firecracker) |
| **LLM06** | Excessive Agency | **最小权限 (Least Agency)** + 人工审批 + Kill Switch + JWT-SVID scope |
| **LLM07** | System Prompt Leakage | 关键信息不进 prompt + 输出过滤 |
| **LLM08** | Vector/Embedding Weaknesses | 多租户隔离 + 相似度阈值 + 输入消毒 |
| **LLM09** | Misinformation | RAG + 来源标注 + 不确定性表达 |
| **LLM10** | Unbounded Consumption | 限流 + Token 配额 (LiteLLM) + 成本监控 (Langfuse) |

**车端特有加固**:
- LLM01: Tool 描述必须 TEE 签名 (防 Shadowing)
- LLM02: PII 脱敏规则 (车架号/车主姓名) 在 DataGate 中强制
- LLM06: 配合 JWT-SVID scope + Conditional Access

### 4.4 Guard 与 IAM 的协同

**关键原则**: **Guard 是策略执行点, IAM 是策略来源**。

```
┌──────────────────────────────────────────────────────────┐
│  Control Plane (策略与身份)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Policy       │  │ IDP          │  │ Agent        │   │
│  │ Engine       │  │ (Keycloak)   │  │ ID (OIDC-A)  │   │
│  │ (OPA/OpenFGA)│  │              │  │              │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼─────────────────┼─────────────────┼────────────┘
          │ Policy Pull      │ Token           │ Identity
          ▼                  ▼                 ▼
┌──────────────────────────────────────────────────────────┐
│  Data Plane (业务流量)                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Action       │  │ Output       │  │ Input        │   │
│  │ Authorizer   │  │ Validator    │  │ Firewall     │   │
│  │ (AuthGate)   │  │ (DataGate)   │  │ (DataGate)   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└──────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────┐
│  Observability Plane (监控与审计)                          │
│  Audit Logger · OpenTelemetry · SIEM                     │
└──────────────────────────────────────────────────────────┘
```

### 4.5 车规 Guard 特定强化

**在通用 6 层防护栈基础上, 车规增加 3 项强化**:

1. **ASIL-D 强化 (L1+L5)**:
   - 双签 (主+备 TA 共识)
   - 简化度量 (PCR0-2)
   - 短 TTL (L1 ≤ 24h vs 其他域 3 月)
   - **无 L3, 无 Sub-Agent** (车控域)

2. **物理世界 Guard (L2+L4)**:
   - 传感器对抗检测 (端到端模型)
   - 物理异常输入过滤 (CAN 总线)
   - 物理篡改告警 (HSM 自检)

3. **离线 Guard (L1+L6)**:
   - 不依赖云端实时兜底
   - 本地 TEE 内可决策
   - OTA 时 fail-secure 降级

---

## 第 5 章 — 三域差异化

### 5.1 总览对比

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
| **ASIL 等级** | QM | ASIL-D | **ASIL-D** |
| **编译宏** | `NIOSEC_DOMAIN_COCKPIT` | `NIOSEC_DOMAIN_DRIVING` | `NIOSEC_DOMAIN_VC` |
| **裁剪模块** | 无 | 关跨域 client | 关 sub-agent, 关跨域 client |

### 5.2 资源预算表

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

### 5.3 跨域权限矩阵

| 源域 \ 目标域 | 座舱 | 智驾 | 车控 |
|----------------|------|------|------|
| **座舱** | — | ✅ 允许 | ⚠️ 只读 |
| **智驾** | ✅ 允许 | — | ⚠️ 只读 |
| **车控** | ❌ 禁止 | ❌ 禁止 | — |

**跨域三原则**:
1. 默认禁止, 例外走 XGW
2. 跨域 ticket 与域内 ticket **不同 ID**
3. XGW 是**唯一**的跨域通道

### 5.4 威胁分级 (T-01..T-10 × 三域)

| 威胁 | 座舱 | 智驾 | 车控 | 主要防御 |
|------|------|------|------|----------|
| T-01 Excessive Agency | 高 | **严重** | **致命** | L3 scope + 委派链 depth |
| T-02 Prompt Injection | 中 | 高 | 严重 | Guard 模块 + Tool 签名 |
| T-03 Identity Spoofing | 高 | **严重** | **致命** | JWT-SVID 验签 + Attestation |
| T-04 Tool Misuse | 中 | **严重** | 致命 | AuthGate ACL + 配额 |
| T-05 Supply Chain | 中 | 高 | **严重** | 二进制签名 + PCR 白名单 |
| T-06 Data Leakage | 高 | 中 | 高 | 审计加密 + TEE 隔离 |
| T-07 Untrusted Output | 中 | **严重** | **致命** | DataGate.output + 人工审批 |
| T-08 DoS | 低 | 高 | **严重** | 资源配额 + 限流 |
| T-09 Cascading Failure | 中 | **严重** | 致命 | break-glass + 双签 |
| T-10 Audit Gap | 高 | **严重** | **严重** | TEE 不可篡改日志 |

### 5.5 车控域硬约束（5 大硬规则）

```
1. 永不发 L3 (无 Sub-Agent)
2. 永远双签 (主+备 TA 共识)
3. 简化度量链 (PCR0-2, 不跑 IMA)
4. 短 L1 TTL (≤ 24h, 其他域 3 月)
5. break-glass 紧急逃生口:
   - 单独 HSM key 签发一次性凭证
   - 强制双 Agent 共识
   - 全程录像
   - 上报告警 (车内 HMI + 云端)
```

---

## 第 6 章 — ASG 实现形态

### 6.1 定位: 车规级嵌入式单进程

**ASG (AgentSec Gateway) = Framework 的车规级实现**。

**核心定位**:
- **单进程 + 2 个 Gate 线程** (AuthGate + DataGate)
- **资源占用**: 座舱 < 1.5MB / 智驾 < 1.2MB / 车控 < 0.7MB
- **启动时间**: 18-25ms
- **鉴权延迟**: < 100μs (含 TEE 调用)

### 6.2 单进程 + 2 Gate 架构

```
ASG 进程 (单进程, 多线程)
├─ Main Loop Thread (LLM 推理 + 工具调度)
├─ AuthGate Thread (IAM 合并)
│  ├─ auth_init / auth_get_self_id
│  ├─ auth_issue_ticket / auth_verify_ticket
│  └─ auth_revoke / auth_revoke_all (Kill Switch)
├─ DataGate Thread (INPUT + OUTPUT 合并)
│  ├─ datagate_check_input
│  ├─ datagate_check_output
│  └─ datagate_sign_output / datagate_verify_input
├─ Sub-Agent Pool (线程模式为主, 裸进程可选)
└─ Audit Ring Buffer (~256KB, 循环覆盖)
```

### 6.3 8 个核心 C API (嵌入式接口)

```c
// ===== AuthGate (6 个) =====
asg_ctx_t* auth_init(const char* manifest_path);
const char* auth_get_self_id(asg_ctx_t* ctx);
ticket_t* auth_issue_ticket(asg_ctx_t* ctx, const ticket_spec_t* spec);
auth_result_t auth_verify_ticket(asg_ctx_t* ctx, const ticket_t* t);
void auth_revoke(asg_ctx_t* ctx, uint64_t ticket_id);
void auth_revoke_all(asg_ctx_t* ctx);  // Kill Switch

// ===== DataGate (4 个) =====
datagate_result_t datagate_check_input(asg_ctx_t* ctx, int source, const void* data, size_t len);
datagate_result_t datagate_check_output(asg_ctx_t* ctx, const void* data, size_t len);
datagate_result_t datagate_sign_output(asg_ctx_t* ctx, const void* data, size_t len, uint8_t sig_out[32]);
datagate_result_t datagate_verify_input(asg_ctx_t* ctx, const uint8_t* signed_blob, size_t len);
```

**对比业界 Gateway**: 业界 20-50 个 API, 我们 8 个, **省 73%**。

### 6.4 Manifest 配置 (车规级)

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

[principal]
spiffe_id = "spiffe://nio.com/agent/cockpit/prod/triage-bot"
sponsor = "sponsor:abc-corp"
type = "llm-guard-7b"
risk_class = "medium"

[acl.capabilities]
allow = ["nav:read", "nav:reroute", "map:query"]
deny = ["nav:write_persistent", "can:brake"]
```

**车控域 (极简版)**:
```toml
[domain]
type = "vehicle-control"

[asg]
subagent = "disabled"          # 关键: 关闭
subagent_max_depth = 0
cross_domain_outbound = []     # 关键: 禁止主动跨域
cross_domain_inbound = ["cockpit"]  # 仅允许座舱查询

[tee]
backend = "hsm"
root_key_ref = "hsm://slot-3/manifest-hmac"

[resources]
max_ram_mb = 0.7
```

### 6.5 与 Framework 模块的对应

| Framework 模块 | 在 ASG 中的实现 |
|----------------|-----------------|
| **IAM (身份治理)** | AuthGate 线程 + TEE 私钥 |
| **INPUT (入口过滤)** | DataGate 的 `datagate_check_input` |
| **OUTPUT (出口过滤)** | DataGate 的 `datagate_check_output` / `datagate_sign_output` |
| **Guard (策略执行)** | 拆解吸收: 工具守卫→AuthGate ACL, Kill Switch→`auth_revoke_all`, 流程门禁→DataGate 串接 |

---

## 第 7 章 — 协议与接口

### 7.1 凭证格式: JWT-SVID vs ASG Ticket

| 维度 | JWT-SVID (Framework) | ASG Ticket (车规) |
|------|---------------------|---------------------|
| 编码 | JSON | C struct |
| 签名 | ES256 (生产) / HS256 (POC) | HMAC-SHA256 |
| 体积 | ~700 B | ~250 B |
| 验证延迟 | ~50 μs | < 1 μs |
| 跨域可读 | ✅ | ❌ 仅 ASG 进程内 |
| 标准化 | SPIFFE 规范 | 内部 |
| 适用 | 域间 / 域内通用 | **车控域 + 域内高频调用** |

**混用策略**:

| 场景 | 用 JWT-SVID | 用 ASG Ticket |
|------|-------------|----------------|
| 域内 LLM ↔ Tool 频繁调用 | | ✅ |
| 域内 Sub-Agent 派生 | | ✅ |
| 域内跨进程通信 (gRPC) | ✅ | |
| **跨域通信** | ✅ | |
| **车控域** | | ✅ (强制) |
| Attestation 结果传递 | ✅ | |

### 7.2 统一接口抽象

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
```

### 7.3 gRPC 接口 (P1 引入, 跨进程)

**3 个核心 proto**:

```protobuf
// agent_registry.proto
service AgentRegistry {
  rpc Register(RegisterRequest) returns (RegisterResponse);
  rpc Lookup(LookupRequest) returns (LookupResponse);
  rpc UpdateStatus(UpdateStatusRequest) returns (UpdateStatusResponse);
  rpc Revoke(RevokeRequest) returns (RevokeResponse);
  rpc Heartbeat(HeartbeatRequest) returns (HeartbeatResponse);
}

// tpm_as.proto
service TPMAS {
  rpc DeriveL3(DeriveL3Request) returns (DeriveL3Response);
  rpc Verify(VerifyRequest) returns (VerifyResponse);
  rpc Revoke(RevokeRequest) returns (RevokeResponse);
}

// cross_domain.proto
service CrossDomainGateway {
  rpc Forward(ForwardRequest) returns (ForwardResponse);
  rpc ListSessions(ListSessionsRequest) returns (ListSessionsResponse);
}
```

### 7.4 OpenFGA 授权 (P1 引入)

**关系型策略**, 委托链表达最自然:

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

### 7.5 X.509 + C509 长期演进

| 协议 | 定位 | 引入阶段 | 用途 |
|------|------|----------|------|
| **JWT-SVID** | 身份凭证 (Bearer) | P0 当前 | 域内 Sub-Agent 委托链 |
| **X.509 + mTLS** | 传输层通道加密 | P2 生产化 | 域间 gateway 长连接 |
| **C509 / CWT** | 车控域极致压缩 | P3+ 远期 | 车控域资源优化 |

---

## 第 8 章 — 关键流程

### 8.1 启动流程

```
1. systemd 启动 ASG 进程
2. auth_init(manifest_path):
   a. 读 manifest.toml + manifest.hmac
   b. TEE 验签 (HMAC-SHA256)
   c. 验签失败 → exit 1 (启动失败, 系统重启)
   d. 解析 ACL → 内存数组
   e. TEE 加载 L1 持久密钥
   f. 颁发 self-ticket
3. Tool 进程注册 → ASG 颁发 tool ticket
4. ASG 进入主循环
```

### 8.2 工具调用完整流程

```
1. LLM 推理输出 tool_call JSON
2. Main: cap_check_tool(agent_id, tool) → ALLOW
3. Main: issue_tool_ticket(tool, params) → TEE HMAC → signed_ticket
4. Main: datagate_check_input("tool_request", params) → ok
5. Main: HTTP POST {tool, params, ticket} → Tool
6. Tool: verify ticket (HMAC + TTL) → ok
7. Tool: 执行
8. Tool: datagate_sign_output(result) → signed_result
9. Tool → Main: signed_result
10. Main: datagate_check_output(result) → ok
11. Main: verify_ticket_use(ticket_id) → 更新使用计数
12. Main → LLM: 喂回 result
```

### 8.3 Sub-Agent 派生流程 (4 道关卡)

```
1. LLM 推理生成 spawn_subagent JSON
2. Out: schema 校验 + task_type 白名单
3. Auth: 4 道关卡
   a. depth + 1 ≤ MAX (≤2)
   b. requested_caps ⊆ parent_caps
   c. 本小时已 spawn N ≤ quota
   d. task_type ∈ Blueprint 白名单
4. 通过 → 颁发 sub-ticket → 启动 Sub-Agent (线程 / 裸进程)
5. Sub-Agent 结束 → TEE 端 delete ephemeral key → 销毁 sub-ticket
```

### 8.4 跨域通信流程

```
1. 座舱 Agent: call_driving_agent("lane-keep-bot", task)
2. 座舱 ASG: 查 cross_domain_outbound → 颁发跨域 ticket (新 ID)
3. 座舱 ASG → XGW: HTTPS POST {target_domain, ticket, task}
4. XGW: 集中审计 + 速率限制 + 转发
5. 智驾 ASG: 验 ticket + 查 cross_domain_inbound → 颁发本地 ticket (新 ID)
6. 智驾 ASG 执行任务 → 响应原路返回
```

### 8.5 OTA 升级流程 (不停服务)

```
1. OTA 下载新 manifest + binary → cosign verify
2. OTA: 写到 staging 分区 → signal(SIGUSR1)
3. ASG: 等待活跃 sub-agent 完成 → graceful shutdown (拒绝新 ticket)
4. ASG: TEE 加载新 HMAC root → 读新 manifest → TEE 验签 → 加载新 ACL
5. OTA: 原子切换 staging → active → restart
6. ASG 用新 manifest 启动
```

### 8.6 异常处理与 Kill Switch

| 场景 | 处理 |
|------|------|
| Ticket TTL 过期 | DENY (expired), 重新 issue |
| 越权调用 | DENY + 审计 (high_risk_alert) |
| 委托链超深 | DENY (depth_exceeded) |
| 车控域派生 sub-agent | DENY (body_domain_no_sub), critical |
| **紧急 Kill Switch** | `auth_revoke_all()`: 清空所有 ticket + TEE 清空 ephemeral key + SHUTDOWN signal |

**fail-secure 原则**: 任何安全失败必须降级到**更安全**模式。

降级路径: 重试 → 重启 Agent → 域级降级 → 整车安全模式 (车控 ASIL-D emergency stop)。

---

## 第 9 章 — 实施路线图

### 9.1 POC (2 周)

| 周 | 目标 | 产出 |
|----|------|------|
| W1 | ASG 8 API 骨架 + JWT-SVID 签发验签 | libnio_asf.so + 单元测试 |
| W2 | Sub-Agent 派生 + 跨域简化 + Demo | 端到端 demo |

**POC 范围** (硬约束):
- ✅ JWT-SVID 签发/验签 (HS256 起步)
- ✅ 三层凭证流转
- ✅ 委托链 (act claim)
- ✅ 简化跨域通信 (预置公钥)
- ✅ Sub-Agent 派生 + 主动撤销
- ❌ X.509 证书管理
- ❌ mTLS
- ❌ 完整 Attestation
- ❌ OpenFGA (用 if-else 模拟)
- ❌ C509 / CWT

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

- ISO 26262 / 21434 / 中国三剑客 合规对接
- 渗透测试 + 第三方审计
- C509 / CWT PoC 评估

### 9.5 关键里程碑

- **M1 (W1 末)**: ASG 8 API 单测通过, ACL 查表 < 1μs
- **M2 (W2 末)**: Sub-Agent + 跨域通 (POC 完成)
- **M3 (W4 末)**: gRPC + Registry 跑通
- **M4 (W6 末)**: Attestation + OpenFGA 集成
- **M5 (W10 末)**: 三域差异化构建完成, 性能达标
- **M6 (P3 末)**: 合规对接完成

---

## 第 10 章 — 风险与缓解

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
| **物理安全风险** | 攻击者接触整车 | 物理异常检测 + 传感器对抗防御 + TEE 自检 |
| **数据合规风险** | GB 44496 数据保护违规 | 座舱语音/视频境内存储 + 人脸分级 |

---

## 附录 A — 术语表

| 术语 | 含义 |
|------|------|
| **ASG** | AgentSec Gateway, 嵌入式车规单进程形态 |
| **NHI** | Non-Human Identity, 非人类身份 |
| **JWT-SVID** | JWT 形式 SPIFFE 身份证明 |
| **SPIFFE** | 工作负载身份标准 |
| **Trust Domain** | 信任域 (座舱/智驾/车控各一个) |
| **`act` claim** | RFC 8693 委托链字段 |
| **L1 / L2 / L3** | 持久 / 运行 / 临时层凭证 |
| **Least Agency** | Agent 时代的最小权限原则 |
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
| **CSMS** | Cybersecurity Management System (UN R155) |
| **TARA** | Threat Analysis and Risk Assessment (ISO 21434) |
| **ASIL-D** | 最高汽车安全完整性等级 (ISO 26262) |
| **CSOC** | Cloud Security Operations Center |
| **Fence** | 沙箱隔离层 |

---

## 附录 B — 开源工具清单 (30 个)

按白皮书涉及的 6 层防护栈分类:

### B.1 输入防护 (Fence + 注入检测)
- **Microsoft Prompt Shields**: LLM 提示注入检测
- **Llama Prompt Guard 2**: Meta 的 prompt 注入分类器
- **Lakera Guard**: API 化 prompt 注入防护
- **Microsoft Presidio**: PII 检测脱敏

### B.2 工具治理 (Tool 治理 + 最小权限)
- **MCP Security Audit**: MCP 协议攻击面分析
- **OpenFGA**: 关系型授权引擎
- **OPA / Rego**: 通用策略引擎
- **Cedar (AWS)**: 表达式策略语言
- **jwt-cpp**: C++ JWT 库 (车规)
- **jsonwebtoken (Rust)**: Rust JWT 库

### B.3 身份治理 (Identity / IAM)
- **go-spiffe**: 官方 SPIFFE Go 库
- **rust-spiffe**: Rust SPIFFE 库
- **libspiffe (HP)**: C SPIFFE 库
- **Keycloak**: 开源 IDP
- **HashiCorp Vault**: 密钥管理
- **Sigstore / cosign**: 镜像签名
- **AIBOM**: AI 软件物料清单

### B.4 输出防护 (Output Validator + Sandbox)
- **Instructor**: 结构化输出校验
- **Outlines**: 引导式输出约束
- **Firecracker**: 微型沙箱
- **RAGAS**: RAG 评估
- **TRIDENT**: 检索评估
- **Adversarial Robustness Toolbox**: 对抗鲁棒性

### B.5 监控审计 (Observability)
- **LiteLLM**: LLM 网关 (限流 / 配额)
- **Langfuse**: LLM 可观测性
- **OpenTelemetry**: 分布式追踪
- **LangChain Citations**: 来源标注

### B.6 车规特定
- **AUTOSAR SecOC**: 车规安全通信
- **TPM 2.0 TSS**: TPM 软件栈
- **mbedTLS / wolfSSL**: 嵌入式 TLS

---

## 附录 C — 参考资料

### 协议 / 标准
- RFC 8693 (Token Exchange): https://datatracker.ietf.org/doc/html/rfc8693
- RFC 9635 (GNAP): https://datatracker.ietf.org/doc/html/rfc9635
- SPIFFE Federation: https://spiffe.io/docs/latest/spiffe-about/spiffe-federation/
- JWT-SVID: https://github.com/spiffe/spiffe/blob/main/standards/JWT-SVID.md
- OIDC-A 1.0: https://arxiv.org/abs/2509.25974
- Identity Management for Agentic AI: https://arxiv.org/abs/2510.25819

### 威胁 / 合规
- OWASP GenAI Security: https://genai.owasp.org/
- OWASP LLM Top 10 2025: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- MITRE ATLAS: https://atlas.mitre.org/
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- ISO 26262 / ISO 21434 / UN R155 (付费)
- GB 44495/44496/44497 (中国三剑客)

### 授权 / 工具
- OpenFGA: https://openfga.dev
- Cedar Policy: https://www.cedarpolicy.com/
- OPA / Rego: https://www.openpolicyagent.org/
- jwt-cpp: https://github.com/Thalhammer/jwt-cpp
- libspiffe: https://github.com/HewlettPackard/libspiffe
- rust-spiffe: https://github.com/maxlambrecht/rust-spiffe

### 工业实践
- Microsoft Entra Agent ID: https://learn.microsoft.com/en-us/entra/agent-id/
- Google Agent Identity: https://cloud.google.com/
- AWS AgentCore Identity: https://aws.amazon.com/bedrock/
- MCP Security: https://arxiv.org/abs/2504.03767

### 整合源文档
- `../ai-agent-security-iam/report.md`
- `../vehicle-edge-ai-security/report.md`
- `../llm-app-security-architecture/report.md`
- `../owasp-llm-top10-defenses/report.md`
- `../atlas-ai-security-101/AI-Security-101-CN.md`
- `../llm-agent-delegation-research-2026/README.md`
- `../nio-asg-design/architecture.md`
- `../nio-vehicle-ai-agent-security-framework-design-v1/framework-design-v2-integrated.md`

---

## 附录 D — 修订历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **v1.0** | 2026-07-21 | 整合 8 份文档为统一白皮书, 10 章 + 4 附录, 统一术语 / 统一威胁编号 / 完整知识金字塔 |
