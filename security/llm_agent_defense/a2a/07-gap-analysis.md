# 车端 Agent A2A+IAM 深度研究 — 缺口分析与完善路线图

> 现有文档 5 份，覆盖协议分析/架构设计/详细设计/嵌入式实现/授权模型。以下是系统性缺口分析。

---

## 一、已覆盖 vs 未覆盖矩阵

```
研究维度                已覆盖深度       缺口
──────────────────────────────────────────────────────────────
A2A 协议分析           ████████░░ 90%    GB/Z 185 原文对齐
A2A 安全模型           ████████░░ 85%    Agent Card 签名验证流
IAM 架构设计           ████████░░ 85%    多 ECU 部署拓扑
KMSS CA 设计           █████████░ 95%    CRL 分发协议细节
OPA/Rego 策略          █████████░ 95%    已转向 RE-ABAC
授权模型对比           ██████████ 100%    ✅ 完成
AUTH_REQUIRED + HMI    ████████░░ 85%    异常路径 (超时/拒绝)
C/C++ 嵌入式实现       ██████░░░░ 65%    多个关键缺口 ↓
TEE/TrustZone 集成     ████████░░ 80%    TEE TA 间安全通道
gRPC Interceptor       ██████░░░░ 60%    完整 C++ 实现
mbedTLS/PSA Crypto     ██████░░░░ 60%    硬件加速适配
RE-ABAC 引擎           ████░░░░░░ 40%    编译器 + 决策表格式
AUTOSAR 集成           ░░░░░░░░░░  0%    完全未覆盖
V2X 场景               ░░░░░░░░░░  0%    完全未覆盖
故障降级               ░░░░░░░░░░  0%    完全未覆盖
GB/Z 185 对齐          ░░░░░░░░░░  0%    完全未覆盖
Agent 生命周期管理     ░░░░░░░░░░  0%    完全未覆盖
性能基准               ░░░░░░░░░░  0%    完全未覆盖
测试与合规             ░░░░░░░░░░  0%    完全未覆盖
```

---

## 二、缺口详细分析 (按优先级排序)

---

### 🔴 P0 — 阻塞性缺口 (必须先完成，否则无法推进实现)

#### P0-1: RE-ABAC 编译器 + 决策表格式规范

**现状**: 只有接口定义 (`re_abac.h`) 和编译器伪代码  
**缺口**: 
- 决策表二进制格式规范 (字节序、对齐、版本号)
- `reabac-compiler` 工具完整实现
- 关系图 JSON Schema (标准化的拓扑描述格式)
- 决策表覆盖率验证 (如何保证没有遗漏的 case)

**为什么是 P0**: RE-ABAC 是整个 IAM 的核心，没有工作原型就无法验证其他设计。

**预估工作量**: 深入文档 1 份 + 原型代码

---

#### P0-2: TEE TA 间安全通道协议

**现状**: 提到 TEE Secure Channel (TA-to-TA RPC)，但没有定义协议  
**缺口**:
- Agent TA ↔ KMSS TA 通信协议格式 (消息类型、序列化)
- 共享内存布局定义
- 错误码定义
- Attestation Report 验证的完整流程
- 会话建立与维护 (TA session lifecycle)

**为什么是 P0**: 这是 KMSS 签发证书的基础路径，没有它 IAM 没有身份源。

**预估工作量**: 深入文档 1 份 + 协议定义

---

#### P0-3: gRPC C++ Interceptor 完整实现

**现状**: 有骨架代码 (`iam_interceptor.hpp`)，但缺很多细节  
**缺口**:
- gRPC C++ interceptor 链的实际注册方式
- 从 `TlsServerCredentials` 提取 SPIFFE ID 的方法 (x.509 SAN extension 解析)
- CRL 检查的完整实现 (mbedTLS CRL API)
- 将 caller identity 注入 gRPC context 的标准方式
- 错误码映射 (IAM decision → gRPC Status Code)
- 与 A2A handler 的协作接口 (AUTH_REQUIRED 传递)

**为什么是 P0**: 这是 A2A 和 IAM 的运行时缝合点。

**预估工作量**: 深入文档 1 份 + 完整 C++ 实现

---

### 🟡 P1 — 重要缺口 (影响架构完整性和可落地性)

#### P1-1: 多 ECU 部署拓扑与 Agent Gateway

**现状**: 假设所有 Agent 在同一个 SoC 的同一个进程中  
**缺口**:
- 真实车端: 10+ ECU，每个 ECU 运行多个 Agent
- Agent Gateway 如何路由 A2A 请求
- 跨 ECU 的 mTLS 信任链管理
- Agent Registry 的分布式一致性 (CAP 在车端的取舍)
- SOME/IP / DDS / Zen 等车载中间件的 A2A 适配

**预估工作量**: 深入文档 1 份

---

#### P1-2: AUTOSAR Adaptive 集成方案

**现状**: 完全未涉及  
**缺口**:
- AUTOSAR Adaptive 的 `ara::com` 与 gRPC 的关系
- 如何在 AUTOSAR 架构下部署 Agent
- `ara::iam` (AUTOSAR IAM) 与 Agent IAM 的关系
- AUTOSAR 的 `Execution Management` 与 Agent 生命周期
- `ara::crypto` 与 KMSS 的对接

**预估工作量**: 深入文档 1 份 + 架构对齐

---

#### P1-3: Agent Card 签名与验证

**现状**: A2A 规范定义了 JWS 签名的 Agent Card，但未深入  
**缺口**:
- Vehicle PKI 如何签发 Agent Card 签名
- JWS 签名格式 (JCS canonicalization + ECDSA P-256)
- 客户端验证 Agent Card 完整链 (CA 链 + CRL)
- 被篡改 Agent Card 的检测与响应
- Extended Agent Card (认证后获取更详细的 Card)

**预估工作量**: 深入文档 1 份

---

#### P1-4: AUTH_REQUIRED 异常路径完善

**现状**: 只覆盖了正常流程 (用户确认 → 继续)  
**缺口**:
- 用户拒绝 (CANCEL): Task → REJECTED, 完整状态转换
- 用户超时 (TIMEOUT): Task → FAILED, 清理逻辑
- 重复确认: 同一 confirmation_id 重放保护
- 确认链: Voice Agent → Orchestrator → ADAS Agent, 逐级传递
- 用户取消后能否重新发起 (新 Task, 新 contextId)?

**预估工作量**: 深入文档 1 份

---

### 🟢 P2 — 增强性缺口 (提升完整性、可信性)

#### P2-1: GB/Z 185 原文对齐

**现状**: 仅提及但未实际分析  
**缺口**:
- GB/Z 185 的核心架构定义
- 与 A2A 协议的对齐点和差异点
- 智能体标识规范的映射 (GB/Z 185 标识 ↔ SPIFFE ID)
- 中国车联网标准体系 (GB/T, YD/T, QC/T) 的相关要求
- 合规清单

**预估工作量**: 深入文档 1 份 (需要获取 GB/Z 185 原文)

---

#### P2-2: V2X 场景下的 Agent 协作

**现状**: 未涉及  
**缺口**:
- 路侧设备 (RSU) Agent 的临时发现与认证
- V2V Agent 间通信的信任模型 (无中心 CA)
- 临时授权的生命周期 (仅在通行期间有效)
- GB/T 标准的 V2X PKI 与 Agent IAM 的集成
- 高移动性场景下的会话保持

**预估工作量**: 深入文档 1 份

---

#### P2-3: 故障降级与弹性设计

**现状**: 假设所有组件正常运行  
**缺口**:
- KMSS 不可用时的降级策略 (Agent 能否继续工作?)
- TEE 完整性校验失败时的隔离措施
- CRL 无法更新时的策略 (fail-open vs fail-secure)
- 证书即将过期但 KMSS 不可达 → Agent 如何处理
- Agent 自身故障检测与恢复
- 部分网络分区 (某个 Domain 与 IAM 断开)

**预估工作量**: 深入文档 1 份

---

#### P2-4: 性能基准与延迟预算

**现状**: 零散提到延迟目标，无系统性分析  
**缺口**:
- 端到端延迟预算分解:
  - mTLS Handshake: ~5ms (TLS 1.3, ECDSA P-256)
  - IAM Authn: ~0.1ms (证书验证)
  - IAM Authz: ~0.01ms (RE-ABAC 查表)
  - A2A Message 处理: ~1ms (protobuf + handler)
  - A2A gRPC 往返: ~2ms (车内 Ethernet)
  - 总预算: ~10ms
- 与汽车功能安全的时间要求对比 (ASIL-D: 通常 < 100ms)
- 并发 Agent 请求下的性能退化曲线
- RTOS 方案的延迟特性

**预估工作量**: 深入文档 1 份

---

#### P2-5: Agent 生命周期管理

**现状**: 未涉及  
**缺口**:
- Agent 安装 (OTA 部署新 Agent → KMSS 签发证书 → Registry 注册)
- Agent 升级 (新固件度量值 → 重新 Attestation → 新证书)
- Agent 卸载 (证书吊销 → Registry 注销 → 清理审计日志)
- Agent 暂停/恢复 (如诊断模式下)
- 全生命周期状态机

**预估工作量**: 深入文档 1 份

---

#### P2-6: 测试策略与合规框架

**现状**: 未涉及  
**缺口**:
- A2A TCK (Technology Compatibility Kit) 测试策略
- IAM 策略正确性测试 (property-based testing)
- 安全测试 (mTLS 错误注入、证书伪造、CRL 绕过)
- ISO 21434 合规清单
- ISO 26262 功能安全论证 (ASIL 相关的 IAM 路径)
- 渗透测试场景

**预估工作量**: 深入文档 1 份

---

## 三、依赖关系与推荐顺序

```
P0-2 (TEE TA Protocol) ──── 先行 ────→ P0-3 (gRPC Interceptor)
       │                                      │
       │                                      │
P0-1 (RE-ABAC Compiler) ─────────────────────┘
       │
       │ (P0 完成后的基础)
       ▼
┌──────────────────────────────────────────────────┐
│ P1-1 (多 ECU 拓扑)    P1-3 (Agent Card 签名)     │
│ P1-2 (AUTOSAR 集成)   P1-4 (异常路径)            │
└──────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────┐
│ P2-1 (GB/Z 185)    P2-2 (V2X)    P2-3 (故障降级) │
│ P2-4 (性能基准)    P2-5 (生命周期) P2-6 (测试)    │
└──────────────────────────────────────────────────┘
```

---

## 四、建议的下一批深入主题 (Top 5)

如果按投入产出比排序，建议优先做这五个：

| 优先级 | 主题 | 理由 |
|--------|------|------|
| **1** | **RE-ABAC 编译器 + 决策表格式** | 整个 IAM 的核心引擎，没有原型无法验证其他 |
| **2** | **TEE TA 间安全通道协议** | KMSS 证书签发的基础通道，IAM 身份链的起点 |
| **3** | **gRPC Interceptor 完整 C++ 实现** | A2A 与 IAM 的运行时缝合，决定了架构能否跑通 |
| **4** | **AUTH_REQUIRED 异常路径** | 当前只覆盖 happy path，异常路径是安全关键 |
| **5** | **多 ECU 部署拓扑** | 从单 SoC 扩展到真实车端多 ECU 架构 |

---

## 五、文档体系最终形态

```
A2A-IAM-Research-Report.md           ← 协议总览 + 边界定义
A2A-IAM-Vehicle-Deep-Design.md       ← 无 OAuth2 架构 + mTLS+gRPC
A2A-IAM-Three-Topics-Deep-Dive.md    ← KMSS + OPA/Rego + AUTH_REQUIRED
A2A-IAM-Embedded-CPP-Research.md     ← C/C++ 全栈实现方案
A2A-IAM-AuthZ-Models-Comparison.md   ← 授权模型对比 + RE-ABAC

待完成:
A2A-IAM-REABAC-Compiler.md           ← RE-ABAC 编译器与决策表格式 (P0)
A2A-IAM-TEE-TA-Protocol.md           ← TEE TA 间安全通道协议 (P0)
A2A-IAM-gRPC-Interceptor-Full.md     ← gRPC Interceptor 完整实现 (P0)
A2A-IAM-AUTH-REQUIRED-ErrorPaths.md  ← 异常路径完善 (P1)
A2A-IAM-Multi-ECU-Topology.md        ← 多 ECU 部署拓扑 (P1)
A2A-IAM-AUTOSAR-Integration.md       ← AUTOSAR 集成 (P1)
A2A-IAM-AgentCard-Signing.md         ← Agent Card 签名验证 (P1)
A2A-IAM-GBZ185-Alignment.md          ← GB/Z 185 对齐 (P2)
A2A-IAM-V2X-Scenarios.md             ← V2X 场景 (P2)
A2A-IAM-Fault-Degradation.md         ← 故障降级 (P2)
A2A-IAM-Performance-Benchmark.md     ← 性能基准 (P2)
A2A-IAM-Agent-Lifecycle.md           ← Agent 生命周期 (P2)
A2A-IAM-Test-Compliance.md           ← 测试与合规 (P2)
```

**当前覆盖率: 5/18 (28%)，核心缺口 13 个，P0 阻塞性 3 个。**
