---
title: A2A × SPIFFE 车内零信任身份方案
---

# A2A × SPIFFE 车内零信任身份方案

> SPIFFE（Secure Production Identity Framework For Everyone）把"工作负载身份"从硬件抽离，CNCF 标准。本文聚焦**车内域控制器之间 A2A 互通**场景：KMSS 兼任 SPIRE Server，每个 DC 跑 SPIRE Agent，A2A Runtime 通过 Workload API 拿到 X.509 / JWT SVID 做零信任认证。本方案**不强制依赖 TEE**，可与 TPM / Secure Element / TEE / 软件加密组合使用。

与本笔记互补：

- [A2A 车载部署与安全设计（TEE + KMSS 基线）](./a2a.md) — TEE‑Rooted CA 方案
- [vSOME/IP](./someip/vsomeip.md) — 跨域 SOME/IP 桥接
- [SOME/IP 安全](./someip/security.md)
- [LLM Agent 分层防御](../security/llm_agent_defense/layered_defense.md)

---

## 0. 总览架构图（SPIFFE 视角）

> 完整版（含 IAM 三模块）见 [`a2a_iam_integration.md §0`](./a2a_iam_integration.md#0-总览架构图一图流)。
> 本图聚焦 **SPIFFE/SPIRE 组件本身** 的部署位置与凭证流。

```mermaid
flowchart TB
    classDef workload fill:#e1f5ff,stroke:#0277bd,stroke-width:2px
    classDef agent fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef server fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef kmss fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef fed fill:#fbe9e7,stroke:#bf360c,stroke-width:2px,stroke-dasharray: 5 5

    subgraph DC_A["域控制器 A（座舱）"]
        WL_A["A2A Workload<br/>CD Agent"]:::workload
        AG_A["SPIRE Agent<br/>本节点 Unix Socket"]:::agent
    end

    subgraph DC_B["域控制器 B（智驾）"]
        WL_B["A2A Workload<br/>AD Agent"]:::workload
        AG_B["SPIRE Agent"]:::agent
    end

    SVR["SPIRE Server<br/>= KMSS Upstream CA"]:::server
    KMS["KMSS<br/>TEE-HSM 私钥"]:::kmss
    FED["OEM B<br/>SPIRE Federation"]:::fed

    WL_A <-. Workload API<br/>fetch X.509/JWT SVID .-> AG_A
    WL_B <-. Workload API .-> AG_B
    AG_A <-. 节点 attestation<br/>+ 拉 Intermediate CA .-> SVR
    AG_B <-. 节点 attestation .-> SVR
    SVR -. 签发 .-> KMS
    SVR <-. federation trust bundle .-> FED

    WL_A ==>|"A2A mTLS<br/>X.509-SVID"| WL_B
    AG_A -. trust bundle .-> FED
    AG_B -. trust bundle .-> FED
```

### 0.1 三类节点角色

| 角色 | 部署位置 | 数量 | 关键能力 |
|---|---|---|---|
| **SPIRE Server** | 中央网关 DC（高可用双节点） | 2 | 节点 attestation、SVID 签发、联邦 |
| **SPIRE Agent** | 每个业务 DC 内 | 1 / DC | 节点身份缓存、Workload API 端点 |
| **A2A Workload** | 业务 DC 内任意进程 | N | 通过 Workload API 取 SVID、做 mTLS |

### 0.2 数据流 vs 控制流

| 流类型 | 路径 | 频次 |
|---|---|---|
| **数据面**（实线） | WL_A → mTLS → WL_B | 每次 A2A 调用 |
| **凭证面**（虚线） | WL → SPIRE Agent → SPIRE Server → KMSS | SVID TTL 触发（默认 1h） |
| **联邦面**（点划线） | SPIRE Server ↔ OEM B SPIRE | 跨域首次握手 + trust bundle 周期推送 |

### 0.3 与后续章节的对应

| 章节 | 对应图的哪部分 |
|---|---|
| §2 车内部署架构 | WL / Agent / Server 三层 |
| §3 KMSS 作为 Upstream CA | SVR ↔ KMS |
| §5-§6 Workload Attestation | WL ↔ AG ↔ SVR 凭证面 |
| §7 A2A 调用流（SPIFFE 版） | WL_A ↔ WL_B 数据面 |
| §8 车云联邦 | SVR ↔ FED 联邦面 |

---

## 1. 为什么选 SPIFFE？

### 1.1 与 TEE 方案的对比

| 维度 | TEE‑Rooted 方案 | SPIFFE × Workload Identity |
|---|---|---|
| **信任锚** | 绑死在 TEE 硬件 | 绑在 workload 身份（可挂任何硬件根） |
| **硬件要求** | 每个 DC 必须有 TEE | TPM / SE / TEE / 软件加密都可以 |
| **跨域联邦** | 需自建协议 | SPIFFE Federation 标准内置 |
| **协议适配** | 自己写 mTLS / 签名 | Envoy / Istio / SPIRE Workload API 现成 |
| **车云一体** | 车内一套、云端一套 | 一套 SPIFFE 联邦，两边复用 |
| **厂商绑定** | 取决于 TEE 实现 | CNCF 标准 |
| **私钥轮换** | 重新 attestation + 重签证书 | SVID TTL 到期，透明切换 |
| **开发门槛** | 高（TEE OS + TA） | 低（标准 crypto API） |

### 1.2 SPIFFE 的核心抽象

```
SPIFFE ID = spiffe://<trust_domain>/<path>
            ├── trust_domain: PKI 信任域
            └── path: workload 唯一标识

SVID = SPIFFE Verifiable Identity Document
   ├── X.509 SVID: 用于 mTLS
   └── JWT SVID: 用于 REST / 联邦

Trust Bundle = trust_domain 下的 CA 证书
              联邦节点之间互相推送

Workload Attestation = 证明"我是我"
   ├── 节点层: TPM EK / 烧录证书
   └── Workload 层: 二进制 hash / OEM 签名 / 进程凭证
```

### 1.3 车内 SPIFFE 适用面

- 高端 DC (Cockpit / ADAS)：SPIFFE + TEE（私钥存 TEE）
- 中端 DC (Body / Powertrain)：SPIFFE + TPM（基线）或 + SE（强）
- 低端 / 旧 DC：SPIFFE + 软件加密（兜底）
- KMSS 自身：SPIFFE + 硬件 HSM

---

## 2. 车内部署架构

```
                ┌─────────────────────────────────────┐
                │     OEM Cloud SPIRE (Federation)    │
                │     trust_domain: oem.cloud         │
                └──────────────┬──────────────────────┘
                               │ SPIFFE Federation
                               │ (互相签发 trust bundle)
┌──────────────────────────────▼──────────────────────────────┐
│     KMSS = SPIRE Server (Central Gateway DC)               │
│     trust_domain: vehicle.local                            │
│     - Issue X.509 SVID + JWT SVID                          │
│     - Upstream CA 由 KMSS Root CA 签发                      │
│     - 双机 HA (Primary / Standby)                          │
└──┬─────────────┬─────────────┬─────────────┬───────────────┘
   │ SPIRE Agent │ SPIRE Agent │ SPIRE Agent │ SPIRE Agent
┌──▼────────┐ ┌──▼────────┐ ┌──▼────────┐ ┌──▼────────┐
│  Cockpit  │ │   ADAS    │ │   Body    │ │  Chassis  │
│    DC     │ │    DC     │ │    DC     │ │    DC     │
│ ┌──────┐  │ │ ┌──────┐  │ │ ┌──────┐  │ │ ┌──────┐  │
│ │A2A RT│  │ │ │A2A RT│  │ │ │A2A RT│  │ │ │A2A RT│  │
│ └──┬───┘  │ │ └──┬───┘  │ │ └──┬───┘  │ │ └──┬───┘  │
│    │      │ │    │      │ │    │      │ │    │      │
│ SPIRE Workload API (UDS)                                   │
└───────────┘ └────────────┘ └────────────┘ └────────────┘
```

### 2.1 组件清单

| 组件 | 角色 | 部署位置 |
|---|---|---|
| **SPIRE Server** | 签发 SVID、维护 trust bundle、attestation 策略 | KMSS（双机） |
| **SPIRE Agent** | 收集 workload 证据、Workload API 服务 | 每个 DC |
| **A2A Runtime** | 通过 Workload API 拿 SVID、做 mTLS | Normal World |
| **Trust Bundle** | 各 trust_domain 的 CA 证书 | 联邦节点之间推送 |
| **SPIRE Federation** | 跨域信任 | 车内 ↔ 云 ↔ 工厂 |

### 2.2 SPIFFE ID 命名规范

```
spiffe://vehicle.local/
   ├── spire/agent/<node-id>                    # SPIRE Agent 自身
   ├── dc/<dc-id>/
   │   ├── agent/<agent-name>                   # A2A Agent
   │   │   ├── cockpit-dc-01/agent/cockpit
   │   │   ├── adas-dc-01/agent/adas
   │   │   └── body-dc-01/agent/body
   │   └── tool/<tool-name>                     # 工具调用
   │       └── cockpit-dc-01/tool/navi
   └── cluster/<cluster-id>/...                 # 集群（保留）

spiffe://oem.cloud/
   ├── service/<svc-name>                       # 云端微服务
   └── region/<region>/...
```

### 2.3 Agent Card 中的 SPIFFE 信息

```json
{
  "name": "cockpit-agent",
  "spiffe_id": "spiffe://vehicle.local/dc/cockpit-dc-01/agent/cockpit",
  "federated_with": ["spiffe://oem.cloud"],
  "skills": [...],
  "endpoints": ["a2a+tls://cockpit-dc.local:8443"],
  "x509_svid_ttl": "1h",
  "jwt_svid_ttl": "5m"
}
```

---

## 3. KMSS 作为 SPIRE Upstream CA

### 3.1 设计原则

**SPIRE Server 自己的中间 CA 不自生成**，由 KMSS Root CA 签发。这样 SPIRE Server 失信时，只要 KMSS Root CA 还在，就能恢复。

```
OEM Root CA (KMSS HSM)
   │
   └── SPIRE Server Intermediate CA (PKCS#11)
         │
         ├── X.509 SVID (各 Agent)
         └── JWT SVID (REST 调用)
```

### 3.2 SPIRE Server 配置

```hcl
# /etc/spire/server/server.conf
server {
    bind_address = "0.0.0.0"
    bind_port = "8081"
    trust_domain = "vehicle.local"

    ca_ttl = "720h"                 # 中间 CA 寿命 30 天
    default_x509_svid_ttl = "1h"    # X.509 SVID 1 小时
    default_jwt_svid_ttl = "5m"     # JWT SVID 5 分钟

    upstream_ca {
        # KMSS PKCS#11 接口
        plugin_name = "kmsp11"
        plugin_data {
            module_path = "/usr/lib/libkm_pkcs11.so"
            token_label = "kmss-vehicle-hsm"
            pin = "${KMSS_PIN}"           # 从 TPM 加密读取
            key_label = "spire-intermediate-ca"
            slot_id = "0"
        }
    }
}

plugins {
    DataStore "sql" {
        plugin_name = "sqlite3"
        database_path = "/var/lib/spire/data.sqlite3"
    }

    Notifier "km_bundle" {
        plugin_name = "kmss_bundle"
        plugin_data {
            km_url = "https://km-internal.vehicle.local"
        }
    }

    UpstreamCA "kmsp11" {
        plugin_name = "km_pkcs11"
        plugin_data {
            hsm_endpoint = "unix:///var/run/kmss/hsm.sock"
            ca_label = "spire-intermediate-ca"
        }
    }
}
```

### 3.3 中间 CA 自动轮换

```
SPIRE Server 中间 CA TTL = 30 天
   ├── 自动在到期前 7 天续签
   ├── KMSS Root CA 重新签发新中间 CA
   ├── Trust bundle 自动广播到所有 SPIRE Agent
   └── 各 Agent 无感切换（自动信任新旧两个 CA）
```

---

## 4. 双机高可用

```
                  ┌──────────────────────┐
                  │   KMSS Heartbeat     │
                  │   (3 选 2 quorum)     │
                  └─────┬────────┬───────┘
                        │        │
        ┌───────────────▼──┐ ┌──▼──────────────┐
        │ Primary SPIRE    │ │ Standby SPIRE   │
        │ Server (active)  │ │ Server (passive)│
        └────────┬─────────┘ └────────┬────────┘
                 │                    │
                 └──────┬─────────────┘
                        │ DRBD / LiteFS
                  ┌─────▼──────┐
                  │ SQLite WAL │
                  │ 共享存储   │
                  └────────────┘
```

### 4.1 故障切换

```
T+0    Standby 检测 Primary 心跳丢失
T+1s   启动选举（双机 + KMSS 心跳 = 2/2 quorum）
T+2s   Standby 接管 SPIRE Server 服务
T+3s   从 KMSS HSM 重新获取 CA 私钥句柄
T+4s   重新加载 SQLite 数据
T+5s   恢复服务, SPIRE Agent 重连（TCP keepalive）
T+5.5s 业务恢复，SVID 已缓存，无需重签
```

### 4.2 关键设计

- **CA 私钥始终在 KMSS HSM**，Standby 无需复制
- **数据同步**：SQLite WAL + DRBD，或 LiteFS（云原生 SQLite 复制）
- **切换延迟**：< 5 秒，业务侧无感（SVID 缓存机制）

---

## 5. Workload Attestation 实战

### 5.1 证据源组合

| 证据源 | 强度 | 适用 | 备注 |
|---|---|---|---|
| **TPM 2.0 PCR** | 强 | 所有 DC 基线 | 度量启动链 |
| **TPM EK 证书** | 强 | 所有 DC | 节点身份根 |
| **二进制 SHA‑256** | 中 | 所有 DC | 验证代码完整性 |
| **OEM 数字签名** | 强 | 所有 DC | 验证代码来源 |
| **Secure Boot 策略** | 强 | 所有 DC | 启动链合规 |
| **IMA 度量日志** | 强 | Linux DC | 运行时完整性 |
| **进程凭证 (UID/GID)** | 弱 | 所有 DC | 仅辅助 |
| **物理防篡改状态** | 强 | 部分 DC | KMSS 验侵入检测 |

### 5.2 多因子组合策略

```
Node Attestation（节点身份, 一次性）:
   因子 1: TPM Endorsement Key (EK) 证书    ← 节点"身份证"
   因子 2: TPM PCR 值（与 OEM 白名单一致）   ← 节点"健康状态"

Workload Attestation（workload 身份, 每次启动）:
   因子 1: 二进制 SHA-256                  ← workload 完整性
   因子 2: OEM 数字签名（cosign 风格）       ← workload 来源可信
   因子 3: Secure Boot PCR0 / PCR4         ← 启动链合规
   因子 4 (可选): IMA 度量日志             ← 运行时完整性
```

**为什么需要多因子**：
- 单因子被攻破 = 整个 attestation 失守
- TPM PCR 可能被固件攻击绕过 → 需要 OEM 签名配合
- 二进制可能被打补丁 → 需要 IMA 度量配合

### 5.3 自定义 OEM Attestation 插件

```go
// /etc/spire/plugins/oem_attestation.go
package main

import (
    "context"
    "crypto"
    "crypto/rsa"
    "crypto/x509"
    "fmt"
    "github.com/spiffe/spire/pkg/common/catalog"
    "github.com/spiffe/spire/pkg/server/plugin/nodeattestor"
)

type OEMAttestor struct {
    OEMRootCA *x509.CertPool
    AllowedPCRs map[string]string
}

func (p *OEMAttestor) Attest(ctx context.Context,
                             challenge []byte,
                             req *nodeattestor.AttestRequest) (*nodeattestor.AttestResponse, error) {

    binaryHash  := req.Payload["binary_sha256"]
    oemSig      := req.Payload["oem_signature"]
    certPath    := req.Payload["signing_cert_path"]
    pcrValues   := req.Payload["tpm_pcrs"]

    // 1. 验证 OEM 签名
    cert, err := loadCert(certPath)
    if err != nil {
        return nil, fmt.Errorf("load cert: %w", err)
    }
    if err := cert.Verify(x509.VerifyOptions{
        Roots:     p.OEMRootCA,
        KeyUsages: []x509.ExtKeyUsage{x509.ExtKeyUsageCodeSigning},
    }); err != nil {
        return nil, fmt.Errorf("cert chain verify: %w", err)
    }
    if err := rsa.VerifyPKCS1v15(cert.PublicKey, crypto.SHA256,
                                  binaryHash, oemSig); err != nil {
        return nil, fmt.Errorf("signature verify: %w", err)
    }

    // 2. 验证 TPM PCR
    for pcr, expected := range p.AllowedPCRs {
        if pcrValues[pcr] != expected {
            return nil, fmt.Errorf("PCR%s mismatch", pcr)
        }
    }

    // 3. 验证 Secure Boot
    if req.Payload["secure_boot_enabled"] != "true" {
        return nil, fmt.Errorf("secure boot disabled")
    }

    return &nodeattestor.AttestResponse{
        SelectorValues: []string{
            fmt.Sprintf("oem:sha256:%s", binaryHash),
            fmt.Sprintf("tpm:PCR0:%s", pcrValues["PCR0"]),
            fmt.Sprintf("tpm:PCR4:%s", pcrValues["PCR4"]),
            "secure_boot:enabled",
        },
    }, nil
}

func main() {
    catalog.PluginMain(&OEMAttestor{
        OEMRootCA:  loadOEMRootCAPool(),
        AllowedPCRs: loadAllowedPCRs(),
    })
}
```

### 5.4 Registration Entry 示例

```bash
# Cockpit DC 的 A2A Agent
spire-server entry create \
    --spiffe-id spiffe://vehicle.local/dc/cockpit-dc-01/agent/cockpit \
    --parent-id spiffe://vehicle.local/spire/agent/cockpit-dc-01 \
    --selector "oem:sha256:5d41402abc4b2a76b9719d911017c592" \
    --selector "tpm:PCR0:0xABCD1234..." \
    --selector "tpm:PCR4:0xEF567890..." \
    --selector "secure_boot:enabled" \
    --x509-svid-ttl 3600 \
    --jwt-svid-ttl 300 \
    --dns-name "cockpit-dc.local" \
    --downstream
```

---

## 6. 车端 SPIRE Agent

### 6.1 SPIRE Agent 配置

```hcl
# /etc/spire/agent/agent.conf
agent {
    data_dir = "/var/lib/spire"
    server_address = "kmss.vehicle.local"
    server_port = "8081"
    trust_domain = "vehicle.local"

    insecure_bootstrap = false  # 必须用 TPM bootstrap

    x509_svid_cache_ttl = "55m"
    trust_bundle_cache_ttl = "24h"

    sync_interval = "5m"
}

plugins {
    NodeAttestor "tpm_ek" {
        plugin_name = "tpmdevid"
        plugin_data {
            devid_cert_path = "/var/lib/spire/tpm_devid_cert.pem"
        }
    }

    NodeAttestor "oem" {
        plugin_name = "oem_attestor"
        plugin_data {
            oem_root_ca_path = "/etc/spire/oem-root-ca.pem"
            binary_path = "/usr/bin/a2a-runtime"
        }
    }

    WorkloadAttestor "unix" {
        plugin_name = "unix"
        plugin_data {
            discover_workload_path = true
        }
    }
}
```

### 6.2 Workload Attestation 时序

```
[A2A Runtime 启动]
   │
   ▼
[1. SPIRE Agent 检测新 workload]
   - 读 /proc/<pid>/cmdline, /proc/<pid>/status
   - 收集证据:
     a) 二进制 SHA-256
     b) OEM 签名验证
     c) TPM PCR0 / PCR4
     d) Secure Boot 状态
     e) (可选) IMA 度量日志
   │
   ▼
[2. SPIRE Agent → SPIRE Server: FetchX509SVID]
   - 携带所有证据
   - Server 评估匹配 Registration Entry
   - 签发 X.509 SVID, TTL=1h
   │
   ▼
[3. SPIRE Agent 通过 Workload API 给 A2A Runtime]
   - UDS: /var/run/spire/sockets/agent.sock
   - A2A Runtime 拿到 PEM 格式 SVID + 私钥
   │
   ▼
[4. A2A Runtime 加载 SVID, 准备 A2A 调用]
```

### 6.3 Workload API 使用（C 示例）

```c
#include <spire-agent-api/spire_agent.h>

void *get_svid_thread(void *arg) {
    spire_agent_ctx *ctx = spire_agent_connect(
        "unix:///var/run/spire/sockets/agent.sock");

    spire_svid *svid = NULL;
    spire_error err = spire_agent_fetch_x509_svid(ctx, &svid);
    if (err) {
        svid = spire_agent_load_cached_svid(ctx);
    }
    configure_a2a_tls(svid->cert_pem, svid->key_pem);

    while (running) {
        sleep(50 * 60);  // 50 分钟续期
        spire_agent_fetch_x509_svid(ctx, &svid);
        configure_a2a_tls(svid->cert_pem, svid->key_pem);
    }
}
```

### 6.4 启动时 SVID 缺失的容错

```c
void a2a_runtime_init() {
    spire_svid *cached = load_cached_svid();

    pthread_t tid;
    pthread_create(&tid, NULL, refresh_svid_async, NULL);

    if (cached && !svid_expired(cached, 5 * 60)) {
        start_a2a_server(cached);            // 用 cached 启动
        return;
    }

    wait_for_new_svid(200);                  // 等待新 SVID（<200ms）
    start_a2a_server(get_current_svid());
}
```

---

## 7. A2A 调用流（SPIFFE 版）

### 7.1 mTLS 场景（X.509 SVID）

```http
POST /a2a/v1/invoke HTTP/2
Host: adas-dc.local:8443
X-Spiffe-Id: spiffe://vehicle.local/dc/cockpit-dc-01/agent/cockpit
X-Request-Id: 7f3a...
Signature: base64(ECDSA(...))
Content-Type: application/json

{
  "method": "adas.perception.objects",
  "args": { "roi": [x1,y1,x2,y2] }
}
```

TLS 握手：

- 客户端 / 服务端证书 = SPIRE 签发的 X.509 SVID（SAN 包含 SPIFFE ID）
- 双方验签 → 验 SAN 是否在期望 trust_domain

### 7.2 REST 场景（JWT SVID）

```http
POST /a2a/v1/notify HTTP/1.1
Authorization: Bearer eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9...
```

JWT 头部：
```json
{ "alg": "EdDSA", "typ": "JWT", "kid": "kid-value" }
```
Payload：
```json
{
  "sub": "spiffe://vehicle.local/dc/cockpit-dc-01/agent/cockpit",
  "aud": ["spiffe://oem.cloud/service/navi-sync"],
  "exp": 1722168600,
  "iat": 1722168000,
  "vehicle_vin": "LSGUC52H9..."
}
```

### 7.3 OPA 策略（按 SPIFFE ID 授权）

```rego
package a2a.invoke

default allow = false

allow {
    input.method == "adas.perception.objects"
    input.caller_spiffe_id == "spiffe://vehicle.local/dc/cockpit-dc-01/agent/cockpit"
    input.target_spiffe_id == "spiffe://vehicle.local/dc/adas-dc-01/agent/adas"
}

deny {
    input.method == "vehicle.control.*"
    # 控制类调用必须经 SOME/IP + SecOC 桥接, A2A 直连拒绝
}

allow {
    # 只允许 ADAS 域调用 Chassis 域的只读方法
    input.method == "chassis.status.read"
    input.caller_spiffe_id == "spiffe://vehicle.local/dc/adas-dc-01/agent/adas"
}
```

---

## 8. 车云联邦（SPIFFE Federation）

### 8.1 联邦配置

```hcl
# 车内 SPIRE Server
federation {
    "oem-cloud" {
        trust_domain = "oem.cloud"
        bundle_endpoint_url = "https://spire.oem.cloud/bundle"
        bundle_endpoint_profile = "https_spiffe"
        # SPIFFE 标准联邦协议, 自动交换 CA bundle
    }
    "fleet-mgmt" {
        trust_domain = "fleet.oem.cloud"
        bundle_endpoint_url = "https://fleet-spire.oem.cloud/bundle"
    }
}
```

### 8.2 跨域 A2A 调用

```
[车内 Cockpit Agent]
   SPIFFE ID: spiffe://vehicle.local/dc/cockpit-dc-01/agent/cockpit
   想调用云端 Navi Agent:
   SPIFFE ID: spiffe://oem.cloud/service/navi-agent
   ↓
   1. 车内 SPIRE 已缓存 oem.cloud trust bundle
   2. 用 JWT SVID 调云端 (aud = spiffe://oem.cloud/service/navi-agent)
   3. 云端验 JWT 签名 → 查 oem.cloud trust bundle
   4. 云端信任 spiffe://vehicle.local（双方已联邦）
   5. 放行
```

**这一步完全不用单独的车云 PKI 桥接**，联邦协议搞定一切。

---

## 9. 车载特殊场景

### 9.1 离线运行

```hcl
spire-agent {
    x509_svid_cache_ttl = "55m"     # 提前 5 分钟续期
    trust_bundle_cache_ttl = "24h"
    allow_offline_renewal = true
}
```

| 离线时长 | 行为 |
|---|---|
| < 1 h | 业务无感（SVID 缓存） |
| 1–24 h | SVID 过期, 但 trust bundle 仍有效；自动降级到只读 / 受限模式 |
| > 24 h | trust bundle 过期, 拒绝跨域调用；仅允许本地 A2A |

### 9.2 OTA 灰度

```bash
# 灰度开始: 同时接受新旧两个 hash
spire-server entry update \
    --entry-id "01HE..." \
    --selector "oem:sha256:5d41402abc4b2a76b9719d911017c592" \
    --selector "oem:sha256:7d41402abc4b2a76b9719d911017c592" \
    --selector "tpm:PCR0:0xABCD1234..." \
    --selector "tpm:PCR0:0xDCBA4321..."

# 7 天后: 移除旧 selector
spire-server entry update \
    --entry-id "01HE..." \
    --selector "oem:sha256:7d41402abc4b2a76b9719d911017c592" \
    --selector "tpm:PCR0:0xDCBA4321..."
```

**自动化（推荐）**：在 OEM OTA 系统中执行 CI 流水线

```yaml
steps:
  - name: 添加新 selector（灰度开始）
    action: spire-server entry update
    selectors_add: [oem:sha256:${NEW_BINARY_SHA256}, tpm:PCR0:${NEW_PCR0}]
    duration: 7d
  - name: 推送 OTA
    action: ota-deploy
  - name: 监控
    action: monitor
    metrics: [spire_attestation_success_rate, a2a_call_success_rate]
  - name: 移除旧 selector
    action: spire-server entry update
    selectors_remove: [oem:sha256:${OLD_BINARY_SHA256}, tpm:PCR0:${OLD_PCR0}]
```

### 9.3 换件（硬件替换）

```
1. 新 DC 上电
2. 新 DC 的 SPIRE Agent 启动, 用 TPM EK 自证
3. SPIRE Agent → KMSS SPIRE Server: "我是新 DC"
4. KMSS 验证：
   a. 该 DC 是否在备件登记列表（OEM 后台同步）
   b. TPM EK 证书是否在 OEM 信任链
5. KMSS 创建 node attestation 记录
6. 新 DC 拿到 SPIFFE ID
7. A2A Runtime 启动 → Workload attestation → 拿 Agent SVID
```

**前置条件**：新 DC 烧录 OEM Root CA 公钥（TPM eFuse，不可擦除）。

### 9.4 性能

| 操作 | 典型时延 |
|---|---|
| 首次 attestation（含 TPM Quote） | 100–300 ms |
| 命中缓存的 attestation | < 5 ms |
| SVID 签发（X.509） | 10–50 ms |
| SVID 续期（命中缓存） | < 5 ms |
| mTLS 握手（含 SVID） | 5–15 ms |
| JWT SVID 签发 | 5–20 ms |

| A2A 场景 | 开销 |
|---|---|
| 冷启动（首次连接） | ~150 ms |
| 热连接复用 | < 1 ms |
| SSE 长连接 SVID 刷新 | 后台异步，业务无感 |

**ASIL‑D 链路仍走 SOME/IP + SecOC**，不进入 A2A 路径。

---

## 10. 硬件根组合策略

| 组合 | 私钥存储 | 适用 |
|---|---|---|
| **SPIFFE + TEE** | TEE Secure Storage | 高端 SoC（Cockpit / ADAS） |
| **SPIFFE + Secure Element** | SE 内部 | 中端 SoC |
| **SPIFFE + TPM** | TPM SRK wrap | 所有 DC（基线） |
| **SPIFFE + 全内存加密** | 加密 RAM | 未来高端 |
| **SPIFFE + 软件** | Normal World 加密 blob | 仅限低敏感 |

**推荐**：高端 DC 走 SPIFFE + TEE/SE；Body/Powertrain 走 SPIFFE + TPM；KMSS 自身用 SPIFFE + HSM。

---

## 11. 与 TEE 方案的取舍

| 维度 | TEE-only | SPIFFE × 多硬件根 |
|---|---|---|
| 私钥保护 | 强（TEE 内） | 可组合（TEE/SE/TPM） |
| 跨域联邦 | 需自建 | 原生支持 |
| 协议适配 | 需手工 | Envoy / Istio 集成现成 |
| 厂商绑定 | 高 | 低（CNCF 标准） |
| 云原生对齐 | 弱 | 强 |
| 工具生态 | 弱 | 强（SPIRE, OPA bundles） |
| 换件复杂度 | 高（需烧 TEE 信任锚） | 低（SPIRE 重新 attestation） |
| OTA 复杂度 | 中（度量白名单管理） | 低（hash selector 灰度） |

**结论**：TEE 适合"必须最强私钥保护"的高安全 DC；SPIFFE 适合"全车统一身份层 + 灵活适配"。**两者并不冲突**——SPIFFE 是身份层，TEE/SE/TPM 是私钥存储层，**正交组合**。

---

## 12. 验证清单

### 12.1 部署验证

- [ ] KMSS 部署 SPIRE Server, 双机 HA 心跳正常
- [ ] SPIRE Server 中间 CA 由 KMSS Root CA 签发
- [ ] 每个 DC 部署 SPIRE Agent, 节点 attestation 通过
- [ ] TPM EK 证书链验证到 OEM Root CA

### 12.2 安全验证

- [ ] Workload Attestation 多因子通过（TPM + OEM 签名 + Secure Boot）
- [ ] SVID TTL=1h 自动续期
- [ ] 重放 5 分钟前的 SVID 验签失败
- [ ] TPM 异常时 attestation 失败, A2A 调用被拒
- [ ] 二进制 hash 被改后 SVID 签发失败

### 12.3 联邦验证

- [ ] 车云联邦握手成功, trust bundle 自动交换
- [ ] 跨域 A2A 调用双方 SPIFFE ID 验证通过
- [ ] 联邦 trust bundle 失效后跨域调用被拒

### 12.4 韧性验证

- [ ] SPIRE Server Primary 故障, Standby 5s 内接管
- [ ] SPIRE Server 不可达, Agent 用缓存 SVID 继续工作
- [ ] OTA 灰度期, 新旧 hash 双轨运行
- [ ] 换件流程可在 30 秒内完成新 DC 注册

### 12.5 性能验证

- [ ] 冷启动 attestation < 300 ms
- [ ] 命中缓存 attestation < 5 ms
- [ ] mTLS 握手 < 20 ms
- [ ] 100 并发 A2A 调用, P99 < 50 ms

---

## 13. 参考与延伸阅读

### 标准与规范

- [SPIFFE 规范](https://spiffe.io/docs/latest/spiffe-about/overview/)
- [SPIRE 架构](https://spiffe.io/docs/latest/spire-about/spire-architecture/)
- [SPIFFE Federation](https://spiffe.io/docs/latest/spire/about/spire-federation/)
- [Workload Identity 最佳实践](https://spiffe.io/docs/latest/spire/using/registration-workload-identity/)
- RFC 8705 - TLS 1.3 PoP
- RFC 9449 - DPoP
- W3C Trace Context

### 仓库内关联笔记

- [A2A 车载部署与安全设计（TEE + KMSS）](./a2a.md)
- [vSOME/IP](./someip/vsomeip.md)
- [SOME/IP 安全](./someip/security.md)
- [DoIP](./doip.md)
- [LLM Agent 分层防御](../security/llm_agent_defense/layered_defense.md)
- [LLM Agent IAM 架构](../security/llm_agent_defense/iam_auth_architecture.md)
- [Falco 运行时检测](../security/falco/)

### 工具与库

- **SPIRE**：SPIFFE 官方实现
- **SPIRL**：SPIFFE 工具库
- **OPA**：策略引擎
- **Envoy + WASM Filter**：A2A 网关
- **sigstore / cosign**：OEM 二进制签名
- **IMA (Integrity Measurement Architecture)**：Linux 内核运行时度量

---

## 14. 待办与开放问题

- [ ] KMSS PKCS#11 插件的 vendor-specific 实现（Infineon / NXP / STM）
- [ ] IMA 度量与 SPIRE attestation 集成（防止 rootkit）
- [ ] Workload Attestation 误判率调优（false negative 监控）
- [ ] 抗量子（PQC）SVID 算法迁移路径
- [ ] SPIRE 在 QNX / INTEGRITY 等车规 RTOS 上的端口
- [ ] 车云联邦的安全边界细化（哪些 SPIFFE ID 允许跨域）
- [ ] SPIRE 性能基准（不同 DC 数量下的吞吐与延迟）