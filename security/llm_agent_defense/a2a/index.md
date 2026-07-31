# A2A (Agent-to-Agent) 协议与车端 IAM 集成

> 本目录是 `security/llm_agent_defense/` 的子目录，聚焦 **A2A 协议在车端的应用**，与父目录的 IAM 架构形成互补。

---

## 与父目录 IAM 文档的关系

```
security/llm_agent_defense/
│
├── iam_auth_architecture.md    ← IAM 核心架构 (4 层 Token, KMSS, 委托链, 凭据管理)
├── layered_defense.md          ← 分层防御方案 (Guard, 规则层, 沙箱, 高通部署)
├── detailed_architecture.md   ← 详细架构 (启动序列, 状态机, 场景, 故障)
│
└── a2a/                        ← 【本目录】A2A 协议层
    ├── 01-a2a-protocol-overview.md     ← A2A 协议全景 + 与 IAM 的边界定义
    ├── 02-vehicle-iam-architecture.md  ← 无 OAuth2 的车端 IAM 架构 (mTLS+gRPC+TEE)
    ├── 03-kmss-opa-auth-required.md    ← KMSS CA 设计 + OPA/Rego 策略 + AUTH_REQUIRED
    ├── 04-embedded-cpp-implementation.md← C/C++ 嵌入式全栈实现方案
    ├── 05-authz-models-comparison.md   ← RBAC→ReBAC→Cedar→RE-ABAC 对比
    ├── 06-iam-embedding-a2a-flow.md    ← IAM 三要素嵌入 A2A 的精确注入点
    └── 07-gap-analysis.md             ← 缺口分析与完善路线图
```

### 父目录的 IAM 文档解决了什么

| 文档 | 解决的核心问题 |
|------|-------------|
| `iam_auth_architecture.md` | Agent 身份用什么 (SPIFFE SVID)、Token 怎么分层 (L0-L4)、KMSS API 长什么样、跨域委托怎么衰减、凭据生命周期如何管理 |
| `layered_defense.md` | IAM 层 + 规则层 + Content Guard + NSFA Risk Guard + 工具沙箱 五层防御如何串行、高通 SA8155 如何部署 |
| `detailed_architecture.md` | 冷启动序列、各模块状态机、跨域调用全流程、故障演练场景 |

### 本目录的 A2A 文档补充了什么

| 文档 | 补充的核心问题 |
|------|-------------|
| `01-a2a-protocol-overview.md` | A2A 协议是什么、Agent Card/Skill/Task/Artifact 概念、A2A 和 IAM 的责任划分 |
| `02-vehicle-iam-architecture.md` | 为什么车端不能 OAuth2、mTLS+SPIFFE 替代方案、TEE+KMSS 如何签发证书、gRPC Interceptor 作为 IAM 注入点 |
| `03-kmss-opa-auth-required.md` | (与 iam_auth_architecture.md 互补) CA 层次设计、证书签发协议细节、OPA Rego 策略编写、A2A TASK_STATE_AUTH_REQUIRED + HMI 用户确认 |
| `04-embedded-cpp-implementation.md` | C/C++ 全栈库选型 (gRPC C++裁剪 / mbedTLS / nanopb / TinyRBAC)、Cortex-A vs Cortex-R 两套方案、资源占用估算 |
| `05-authz-models-comparison.md` | 为什么不只 RBAC、Google Zanzibar/Amazon Cedar/OPA/Casbin 对比、RE-ABAC 混合模型推荐 |
| `06-iam-embedding-a2a-flow.md` | **最关键**: AgentID/Agent Auth/Agent Cert 分别在 A2A 生命周期 (Phase 0-3) 的哪个精确点介入 |
| `07-gap-analysis.md` | 当前覆盖了哪些、还缺哪些 (P0/P1/P2 优先级) |

### 阅读顺序建议

```
新人入门:
  1. 父目录 iam_auth_architecture.md  ← 理解 IAM 核心
  2. 本目录 01-a2a-protocol-overview.md ← 理解 A2A 协议
  3. 本目录 06-iam-embedding-a2a-flow.md ← 理解两者如何缝合

架构设计:
  4. 本目录 02-vehicle-iam-architecture.md ← mTLS+gRPC 方案
  5. 本目录 05-authz-models-comparison.md ← 授权模型选型
  6. 父目录 layered_defense.md ← 完整分层防御

技术实现:
  7. 本目录 03-kmss-opa-auth-required.md ← KMSS + 策略 + 用户确认
  8. 本目录 04-embedded-cpp-implementation.md ← C/C++ 落地
  9. 父目录 detailed_architecture.md ← 启动/状态机/故障

项目管理:
  10. 本目录 07-gap-analysis.md ← 知道还缺什么
```

---

## 关键概念速查

| 概念 | 定义位置 | 简要说明 |
|------|---------|---------|
| SPIFFE ID | `iam_auth_architecture.md` §4 | Agent 工作负载身份 URI |
| SVID | `iam_auth_architecture.md` §4.1 | SPIFFE 可验证身份文档 (X.509 或 JWT) |
| L0-L4 Token | `iam_auth_architecture.md` §4 | 5 层 Token 模型 (SVID→Task→Session→Lease→Persistent) |
| KMSS | `iam_auth_architecture.md` §6 | 密钥管理与安全存储服务 (libkmss.so) |
| Delegation Chain | `iam_auth_architecture.md` §9 | 跨域委托链, scope 单向衰减 |
| Trust Bundle | `iam_auth_architecture.md` §14.4 | 远域公钥+证书链+CRL 的 OTA 包 |
| Agent Card | `01-a2a-protocol-overview.md` §1 | A2A 协议的 Agent 元数据描述文档 |
| AUTH_REQUIRED | `06-iam-embedding-a2a-flow.md` §5 | A2A 的 interrupted task state, IAM 鉴权拒绝的可恢复路径 |
| RE-ABAC | `05-authz-models-comparison.md` §4 | 关系增强型属性访问控制 (编译时预计算) |
| mTLS + SPIFFE | `02-vehicle-iam-architecture.md` §A.3 | 车端替代 OAuth2 的认证方案 |
| gRPC Interceptor | `06-iam-embedding-a2a-flow.md` §5 | IAM Authn+Authz 在 gRPC 层的注入点 |

---

## 外部参考

- [A2A Protocol Spec v1.0.0](https://a2a-protocol.org/latest/specification/)
- [A2A GitHub (Google)](https://github.com/google/A2A)
- [a2a-cpp SDK (社区)](https://github.com/MisterVVP/a2a-cpp)
- [SPIFFE/SPIRE](https://spiffe.io/)
- [OpenFGA (Google Zanzibar)](https://github.com/openfga/openfga)
- [Amazon Cedar](https://www.cedarpolicy.com/)
- [OPA/Rego](https://www.openpolicyagent.org/)
- [GlobalPlatform TEE Client API](https://globalplatform.org/specs-library/tee-client-api-specification/)
- [mbedTLS](https://github.com/Mbed-TLS/mbedtls)
- [nanopb](https://github.com/nanopb/nanopb)
- GB/Z 185《人工智能 智能体互联》
