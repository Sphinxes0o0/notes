---
title: A2A 协议车载部署与安全设计
---

# A2A 协议车载部署与安全设计

> A2A（Agent‑to‑Agent）是面向智能体的互通协议，基于 JSON‑RPC over HTTP/2、SSE、WebSocket，配合 Agent Card 完成能力发现。本笔记聚焦**仅车内域控制器之间的 A2A 互通**：每个域控制器都有 TEE，车内由 KMSS（Key Management SubSystem）统一管理密钥与证书生命周期。

## 1. 协议概览

### 1.1 核心要素

- **JSON‑RPC 2.0**：方法调用与结果返回的载荷格式
- **Agent Card**：描述 Agent 能力、技能（skills）、认证方式、端点的 JSON 元数据（通常托管在 `/.well-known/agent.json`）
- **Task / Artifact / Message**：长时任务的拆解单元，`message.parts` 承载文本、文件、结构化数据
- **传输层**：HTTP/2（短请求）+ SSE / WebSocket（流式订阅）
- **发现**：车内 mDNS / SRV + Agent Card 拉取（KMSS 签名）

### 1.2 在车内要替换/并存的协议

| 传统车载协议 | A2A 与之关系 |
|---|---|
| SOME/IP 服务调用 | A2A 可在 QM 域替代部分跨域服务发现与调用 |
| CAN / CAN FD / LIN | A2A 不下沉到信号层，保留总线协议 |
| DoIP | 诊断通道保持独立，A2A 可调用诊断能力 |
| SecOC SOME/IP | ASIL‑D 安全链路**不被 A2A 替代** |
| Classic AUTOSAR | A2A 跑在 AUTOSAR Adaptive (POSIX) 之上 |

### 1.3 不应使用 A2A 的场景

- 实时控制信号（制动 / 转向 / 驱动）：保持 SOME/IP + SecOC
- 安全相关决策（ASIL‑D）：不允许经过 LLM Agent
- 大带宽流式传感数据（摄像头 / 雷达原始帧）：走专用以太网 / PCIe，不入 A2A

---

## 2. 车内部署拓扑

```
                ┌─────────────────────────────────────┐
                │       Central Gateway DC            │
                │  ┌───────────────────────────────┐  │
                │  │   KMSS (Key Management SubSystem)│
                │  │  • 根 CA / 中间 CA              │  │
                │  │  • 设备/Agent 证书签发          │  │
                │  │  • 密钥轮换/吊销                │  │
                │  │  • TEE 远程 attestation 验证    │  │
                │  └───────────────────────────────┘  │
                └──────┬────────┬────────┬────────┬────┘
            Automotive Ethernet (100/1000BASE-T1) + MACsec
              │           │           │            │
       ┌──────┴─┐   ┌─────┴───┐  ┌────┴────┐  ┌────┴─────┐
       │ Cockpit│   │  ADAS   │  │  Body   │  │Powertrain│
       │   DC   │   │   DC    │  │   DC    │  │    DC    │
       │ ┌────┐ │   │ ┌────┐  │  │ ┌────┐  │  │ ┌────┐   │
       │ │TEE │ │   │ │TEE │  │  │ │TEE │  │  │ │TEE │   │
       │ │CA  │ │   │ │AA  │  │  │ │BA  │  │  │ │PA  │   │
       │ └──┬─┘ │   │ └──┬┘  │  │ └──┬┘  │  │ └──┬┘   │
       │ ┌──┴─┐ │   │ ┌──┴─┐ │  │ ┌──┴─┐ │  │ ┌──┴─┐   │
       │ │A2A │ │   │ │A2A │ │  │ │A2A │ │  │ │A2A │   │
       │ │RT  │ │   │ │RT  │ │  │ │RT  │ │  │ │RT  │   │
       │ └────┘ │   │ └────┘ │  │ └────┘ │  │ └────┘   │
       └────────┘   └────────┘  └────────┘  └──────────┘

       CA = Cockpit Agent, AA = ADAS Agent,
       BA = Body Agent,   PA = Powertrain Agent
```

### 2.1 部署分区原则

- **每个 DC 一份 TEE**：Cockpit DC / ADAS DC / Body DC / Powertrain DC / Chassis DC 都部署 TEE（TrustZone / OP‑TEE / SGX）
- **A2A Runtime 跨 Normal World + Secure World**：HTTP/2 栈在 Normal World，私钥与签名操作全部下沉到 TEE
- **KMSS 单独存在**：常驻 Central Gateway 的硬件 HSM，也可冗余双机
- **跨域隔离**：ASIL‑D 链路（Chassis、制动）**不允许 A2A 直接落地**，必须经 SOME/IP + SecOC

### 2.2 网络层与传输层

| 层 | 协议 | 作用 |
|---|---|---|
| 物理 / 链路 | 100/1000BASE-T1 + MACsec (802.1AE) | 链路层机密性、抗篡改 |
| 网络 | IPv6 / SOME/IP | A2A 端点寻址 |
| 安全 | mTLS 1.3 (PoP / DPoP) | 端到端认证 |
| 应用 | HTTP/2 + JSON‑RPC + SSE / WebSocket | A2A 协议体 |
| 监控 | W3C Trace Context | 跨域全链路追踪 |

---

## 3. KMSS（Key Management SubSystem）

KMSS 是车内 PKI 的根，负责所有密钥与证书的生成、分发、轮换、吊销、attestation 验证。

### 3.1 持有的资产

| 资产 | 存储位置 | 用途 |
|---|---|---|
| OEM Root CA 私钥 | KMSS HSM（防篡改） | 签发 Intermediate CA |
| Per‑DC Intermediate CA 私钥 | KMSS HSM | 签发 DC 设备证书 |
| Per‑Agent 私钥 | 各 DC 的 TEE（不可导出） | A2A 请求签名 |
| Session Key（ECDH 派生） | 各 DC 的 TEE，会话结束销毁 | mTLS 会话密钥 |
| CRL / OCSP 列表 | KMSS + 各 DC 缓存 | 证书吊销 |
| Attestation 信任锚 | KMSS HSM | 验 TEE 启动度量 |

### 3.2 启动流程：DC 接入车内网络

```
[DC 上电]
   ↓
[Secure Boot: BL1 → BL2 → TEE OS → A2A Runtime 度量链]
   ↓
[TEE 生成 attestation quote (PCR/TPM, 含 nonce)]
   ↓
[DC → KMSS: POST /km/agent-cert/issue
        body = { dc_id, agent_class, tpm_quote, agent_card_spec }]
   ↓
[KMSS:
   1. 验证 TEE 度量值是否在 OEM 白名单
   2. 校验 agent_card_spec 是否符合该类 Agent 能力模板
   3. 在 HSM 内生成 Agent 私钥 + 证书 (TTL=24h, X.509 v3, EKU=clientAuth)
   4. 用 Intermediate CA 签名, 出证 + 加密私钥载荷]
   ↓
[DC TEE 解密私钥 → 写入 Secure Storage 不可导出区]
   ↓
[Agent Card 经 KMSS 签名后发布到车内服务发现]
```

### 3.3 密钥生命周期管理

```
   ┌─────────┐    request     ┌──────────┐   issue   ┌───────────┐
   │  DC     │──────────────▶│  KMSS   │──────────▶│  Active  │──┐
   └─────────┘               └──────────┘            └───────────┘  │
        ▲                                                    │ use │
        │ renew (24h)                                       ▼    │
   ┌────┴────┐                                          ┌──────────┐
   │Renewing │◀───────────────── TTL expiring ─────────│  In-use  │
   └─────────┘                                          └──────────┘
        │                                                     │
        │ abnormal (TEE 度量异常 / 物理篡改 / 多次失败)            │
        ▼                                                     ▼
   ┌──────────┐                                          ┌──────────┐
   │ Revoked │◀─────────────────────────────────────────│ Crl/OCSP │
   └──────────┘                                          └──────────┘
```

- **被动轮换**：DC 每 24h 或重启时申请新证书
- **主动吊销**：KMSS 推 CRL 到车内各 DC（车内 802.1Q VLAN 多播 + MACsec 加密通道）
- **紧急吊销**：KMSS 检测到 TEE 度量异常或物理篡改，立刻吊销并广播
- **审计**：每次 issue/renew/revoke 写 KMSS 防篡改日志（HSM 内置 Append‑Only）

### 3.4 与 AUTOSAR KeyM 的对齐

KMSS 可以复用 AUTOSAR 标准接口：

| AUTOSAR 模块 | 在 KMSS 中的映射 |
|---|---|
| **KeyM** | 密钥生命周期状态机 (init → request → available → destroyed) |
| **CSM / Cry** | HSM 内的硬件随机数与签名原语 |
| **SecOC** | 证书用于 SecOC MAC 校验密钥分发 |
| **NvM** | 持久化 CRL / 已签发证书索引 |
| **PduR / CanTp** | 车内多播证书撤销消息的传输层 |

### 3.5 KMSS 自身的高可用

| 方案 | 说明 |
|---|---|
| **双机热备** | 两个 Central Gateway DC 互为 KMSS 副本，HSM 私钥通过 secure mirroring 同步 |
| **脑裂保护** | 心跳 + quorum（≥2/3 决策），避免双主同时签发 |
| **度量同步** | TEE 度量基准从 OEM 工厂一次性导入，不允许运行时修改 |
| **物理篡改响应** | KMSS 检测到电压 / 温度 / 入侵开关异常时进入 **burn‑through**：清空私钥、广播 CRL |

---

## 4. TEE 上的 A2A Runtime

### 4.1 TEE 内部布局

```
┌─────────────────── Normal World ─────────────────────┐
│  Linux/QNX / Cockpit UI / Voice Pipeline              │
│  ┌──────────────────────────────────────────────┐    │
│  │   A2A Client Lib (liba2a.so)                  │    │
│  │   - HTTP/2 client                              │    │
│  │   - SSE/WebSocket subscriber                   │    │
│  │   - 通过 TEE Client API 调用 crypto             │    │
│  └─────────────────┬────────────────────────────┘    │
└────────────────────┼──────────────────────────────────┘
       TEE Client API (GP TEE / OP-TEE)
┌────────────────────▼──────────────────────────────────┐
│               Secure World (TEE)                      │
│  ┌────────────────────────────────────────────────┐  │
│  │   A2A Crypto Service                           │  │
│  │   - sign_a2a_request(key_handle, payload)       │  │
│  │   - verify_a2a_request(pub, signature)          │  │
│  │   - ecdh_derive_session(peer_pub)               │  │
│  │   - persist_audit_log(event)                    │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │   Secure Storage                               │  │
│  │   - Agent 私钥 (不可导出, 仅允许签名)             │  │
│  │   - 对端公钥缓存 (KMSS 签名)                     │  │
│  │   - Append-only 审计日志                         │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │   Attestation Agent                            │  │
│  │   - 生成 TPM quote (PCR + nonce)                │  │
│  │   - 提供给 KMSS 验证                            │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

### 4.2 Normal World **永远碰不到** 私钥

```c
// Normal World
a2a_request_t *req = build_request("adas.perception.objects");
uint8_t sig[64];
size_t sig_len;
int rc = tee_crypto_sign_request(
    req,                  // 待签 payload
    AGENT_KEY_HANDLE,     // TEE 内句柄, 无 raw 私钥
    sig, &sig_len);       // 只回传签名结果
if (rc) return error;
// 私钥从未离开 TEE; root / kernel 提权也无法伪造请求
```

即便 LLM 被注入、被 root 提权，**攻击者无法伪造有效 A2A 请求**，因为签名密钥在 TEE 中，Normal World 没有 raw key。

### 4.3 TEE 内的审计

```c
typedef struct __attribute__((packed)) {
    uint64_t timestamp_hsm;   // HSM 内置时钟
    uint32_t agent_id_hash;   // 哪个 Agent
    uint16_t method_id;       // 方法 ID（避免泄露方法名字符串）
    uint8_t  trace_id[16];    // W3C Trace ID
    uint8_t  status;          // 0=ok, 1=denied, 2=error
    uint8_t  policy_rule_id;  // 命中 OPA 规则 ID
} a2a_audit_record_t;
// 写入 TEE Secure Storage 的 ring buffer
// 仅允许追加, 滚动覆盖前用 KMSS 公钥加密远端备份
```

---

## 5. 端到端 A2A 安全调用流

**场景**：座舱 Agent (CA) 要调用 ADAS Agent (AA) 的 `adas.perception.objects`

```
1. CA → KMSS (证书/密钥准备)
   POST /km/agent-cert/refresh
   body: { dc_id="cockpit-dc-01", agent_class="cockpit",
           tpm_quote=<sig over PCR+nonce> }
   ← { agent_cert (TTL=24h, KMSS-signed), priv_key_handle }

2. CA ⇄ AA [首次或证书变更后]
   - TLS 1.3 握手 (ECDHE X25519)
   - 双向证书校验: CA cert & AA cert 都验到 KMSS Root
   - 检查 CRL (本地缓存 + KMSS push)
   - 派生 session_key_CA↔AA

3. CA → AA (HTTP/2 over TLS)
   POST /a2a/v1/invoke
   headers:
     traceparent: 00-<trace-id>-<span-id>-01
     x-a2a-agent-id: cockpit-dc-01
     signature: base64(ECDSA(priv, body))
     timestamp: <hsm_clock>
   body:
     { "method": "adas.perception.objects",
       "args":   { "roi": [x1,y1,x2,y2] } }

4. AA TEE 内处理
   a. verify_a2a_request(CA_pub, signature)
   b. check_timestamp_within_window(±5min)
   c. check_crl(CA_cert)
   d. opa_evaluate(method, from=CA, to=AA)        // 策略允许
   e. check_rate_limit(method, bucket=CA)         // 未超限
   f. execute_method() → 业务逻辑返回 objects[]
   g. sign_response(priv_AA, body) → 写回
   h. 写 TEE 审计记录

5. AA → CA
   HTTP/2 200, signature, audit_id (供 KMSS 拉取验证)

6. 全程 TEE 审计, KMSS 周期性拉取 + 校验哈希链
```

---

## 6. 跨 ASIL 域的安全桥接

A2A 不允许直接写底盘 / 制动 / 转向。要跨 ASIL 域，必须走 SecOC SOME/IP 桥接：

| 调用方向 | 方式 | 验证层级 |
|---|---|---|
| Cockpit → ADAS（QM→QM） | A2A + TEE mTLS | OPA + 速率限制 |
| Cockpit → Body（QM→QM） | A2A + TEE mTLS | OPA |
| ADAS → Chassis（QM→ASIL‑D） | **不允许 A2A 直连** | 必须经 Safety MCU + SecOC SOME/IP |
| Chassis → ADAS（ASIL‑D→QM） | SOME/IP + SecOC → 网关转换 → A2A | SecOC MAC + 网关 OPA 二次校验 |
| Body → Chassis（QM→ASIL‑D） | 网关拦截 + 强制降级到安全 SOME/IP | 写操作需额外驾驶员确认 |

**理由**：

1. ASIL‑D 链路要求端到端 ≤ 10 ms 确定时延，A2A 的 JSON‑RPC + TLS 握手开销不可接受
2. LLM Agent 不允许触碰安全关键链路，避免误触发 / 注入触发
3. SecOC MAC + SOME/IP 是经过功能安全认证的标准方案

**桥接实现建议**（在 Central Gateway DC 中）：

```
A2A in ─▶ [OPA 网关] ─▶ SecOC SOME/IP out ─▶ Safety MCU
                                                       │
A2A out ◀─ [审计代理] ◀─ SecOC SOME/IP in ◀────────────┘
```

桥接器本身**运行在 TEE 内**，且需要双重身份（A2A 身份 + SecOC 身份），由 KMSS 统一签发。

---

## 7. 审计与可观测

### 7.1 三层可观测

| 层 | 数据 | 工具 |
|---|---|---|
| **链路层** | MACsec 链路状态、VLAN 流量 | 车内交换机 telemetry |
| **协议层** | A2A Trace、HTTP/2 stream、SSE 连接 | Envoy + 自研 trace exporter |
| **系统层** | DC 进程系统调用、网络连接、文件访问 | eBPF + Falco（仓库已有 `security/falco`） |

### 7.2 Falco 规则示例

```yaml
# falco_rules.local.yaml
- rule: A2A Agent Unexpected Peer
  desc: A2A agent connecting to non-allowlisted in-vehicle peer
  condition: >
    container.image.repository contains "a2a-agent" and
    not fd.sip.name in (cockpit_dc, adas_dc, body_dc, powertrain_dc, kmss)
  output: "A2A agent abnormal peer (user=%user.name command=%proc.cmdline peer=%fd.sip.name)"
  priority: WARNING

- rule: A2A Agent TEE Boundary Violation
  desc: Normal world process attempted to read TEE-protected agent key
  condition: >
    container.image.repository contains "a2a-agent" and
    evt.type=open and fd.name contains "/tee/agent_key"
  output: "TEE boundary violation (command=%proc.cmdline file=%fd.name)"
  priority: CRITICAL

- rule: A2A Agent Burst Calls
  desc: A2A agent exceeding per-method rate limit
  condition: >
    container.image.repository contains "a2a-agent" and
    evt.type=connect and evt.num > 100
  output: "A2A burst (command=%proc.cmdline count=%evt.num)"
  priority: WARNING
```

### 7.3 审计字段

| 字段 | 说明 |
|---|---|
| `trace_id` | W3C Trace ID（车内 + 出车可关联） |
| `agent_id` | 哪个 Agent（证书 SN 哈希） |
| `method` | A2A 方法名 / ID |
| `args_hash` | 参数 SHA‑256 |
| `result_status` | success / denied / error |
| `policy_decision_id` | 触发哪条 OPA 规则 |
| `timestamp_hsm` | HSM 内置时钟时间戳 |
| `tee_pcr` | 调用时 TEE PCR 值（事后追溯） |

审计日志在每个 DC 的 TEE 内保留 30 天，定期（每日）由 KMSS 公钥加密后汇聚到 Central Gateway 的冷存储。

---

## 8. 韧性设计

### 8.1 KMSS 高可用

| 维度 | 方案 |
|---|---|
| **硬件冗余** | 两个 Central Gateway DC 各部署一个 KMSS HSM |
| **数据同步** | 已签发证书索引 + CRL 通过 secure mirroring 同步 |
| **脑裂保护** | 心跳 + 3 选 2 quorum，避免双主签发冲突证书 |
| **度量同步** | TEE 度量基准从 OEM 工厂一次性导入，运行时不允许改 |
| **物理篡改** | 检测到入侵开关 / 异常电压 → burn‑through + 广播 CRL |

### 8.2 域控制器故障

- **A2A 运行时崩溃**：TEE watchdog 自动重启 Normal World 进程；私钥不变
- **DC 完全掉电**：重启后重新走启动流程，重新向 KMSS 申请 Agent 证书
- **TEE 度量失败**：KMSS 拒绝签发证书，DC 仅保留 Normal World 调试模式（不可加入 A2A 网络）

### 8.3 车内网络降级

- **MACsec 重协商失败**：告警但保留链路（明文 + 速率限制）直至恢复
- **A2A 长连接断开**：客户端按指数退避重连 + 走本地缓存的最近一次成功响应
- **证书即将过期**：TEE 在过期前 1 小时主动续签，业务无感

---

## 9. 验证清单

### 9.1 部署验证

- [ ] 每个 DC 都有 TEE，且 Secure Boot 链路完整（BL1 → BL2 → TEE OS → A2A Runtime）
- [ ] TEE 度量值（PCR）与 OEM 白名单一致
- [ ] KMSS 双机热备正常工作，心跳与 quorum 验证通过
- [ ] MACsec 在每条链路上协商成功

### 9.2 安全验证

- [ ] mTLS 1.3 强制启用，TLS 1.2/1.1 探测被拒
- [ ] 重放 5 分钟前的签名返回 401
- [ ] 篡改 Agent Card 启动 / 调用失败
- [ ] 跨 Agent 调用被 OPA 拒绝（未授权方法）
- [ ] 异常出网（跨域网段）被 Falco 告警
- [ ] TEE 私钥从未在 Normal World 出现（dump 内存验证）

### 9.3 韧性验证

- [ ] KMSS 主掉线，从 30 秒内顶上
- [ ] DC TEE 重启后业务恢复时间 ≤ 10 秒
- [ ] 证书即将过期前自动续签无业务中断

### 9.4 注入与功能安全

- [ ] 语音输入含 "忽略之前指令" 不影响 A2A 行为
- [ ] 工具返回值含 "Ignore previous" 不影响 LLM 决策
- [ ] 任何 `adas.control.*` / `chassis.*` 调用走 SecOC 桥接，A2A 直连被拒
- [ ] LLM Agent 没有调用底盘工具的能力（在 Agent Card 白名单外）

### 9.5 合规验证

- [ ] ISO/SAE 21434 TARA 已覆盖 A2A 接口
- [ ] UN R155 CSMS 资产清单含 A2A Runtime、KMSS、TEE
- [ ] 车内所有 PII 仅本地处理 / 加密上行（可关闭）

---

## 10. 与 AUTOSAR Adaptive 的对齐

| A2A 组件 | AUTOSAR AP 对应物 |
|---|---|
| A2A Client/Server | ara::com Service Proxy / Skeleton |
| Agent Card | ara::com 服务 manifest 的扩展 |
| TEE Crypto Service | ara::crypto + TrustZone |
| KMSS | KeyM + CSM + OEM 私有 KMS 服务 |
| OPA 策略 | ara::com 的访问控制策略 |
| 审计 | DLT（Diagnostic Log and Trace）扩展 |

实际落地时可以**在 ara::com 之上封装 A2A 适配层**，让现成 AUTOSAR AP 应用无感迁移到 A2A。

---

## 11. 参考与延伸阅读

### 协议与标准

- Google A2A Protocol 规范（[a2a.dev](https://a2a.dev)）
- RFC 8705 - TLS 1.3 Certificate‑Bound Tokens (PoP)
- RFC 9449 - DPoP
- W3C Trace Context
- IEEE 802.1AE (MACsec)
- ISO/SAE 21434 道路车辆网络安全工程
- UN R155 / R156
- AUTOSAR Adaptive Platform R24‑11（KeyM、CSM、Crypto）
- GP TEE Client API / OP‑TEE

### 仓库内关联笔记

- [vSOME/IP](./someip/vsomeip.md) — A2A ↔ SOME/IP 网关基础
- [SOME/IP 安全](./someip/security.md) — 跨域签名机制
- [DoIP](./doip.md) — 诊断通道桥接
- [LLM Agent 分层防御](../security/llm_agent_defense/layered_defense.md)
- [LLM Agent IAM 架构](../security/llm_agent_defense/iam_auth_architecture.md)
- [LLM Agent 详细架构](../security/llm_agent_defense/detailed_architecture.md)
- [Falco 运行时检测](../security/falco/)

### 工具与库

- **OPA**：车内策略引擎，WASM 嵌入
- **Falco**：运行时异常检测（eBPF）
- **Envoy + WASM Filter**：A2A 网关层
- **OP‑TEE**：开源 TEE
- **tpm2‑tools**：远程 attestation 调试工具

---

## 12. 待办与开放问题

- [ ] A2A ↔ SecOC SOME/IP 网关参考实现（`examples/a2a-secoc-bridge/`）
- [ ] KMSS 双机 quorum 协议选型（CRDT / Raft / Paxos）
- [ ] TEE 远程 attestation 协议选型（TPM 2.0 / DICE / PSA Attestation）
- [ ] 车端 Agent Card 离线签名工具链（工厂内 KMSS 私钥不出 HSM）
- [ ] CARLA + 自建 A2A Server + KMSS 仿真做渗透测试剧本
- [ ] 跟进 A2A 在 **AUTOSAR FO2 R24‑11**、**COVESA AOSP** 的官方采纳进展
- [ ] 国密 SM2/SM3/SM4 与 KMSS 的集成