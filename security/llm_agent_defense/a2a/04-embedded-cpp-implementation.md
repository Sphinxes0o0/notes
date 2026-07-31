# 车端嵌入式 C/C++ 实现深度调研

> **目标**: 将 Agent IAM + A2A 协议栈从 Go/Python 方案迁移到嵌入式 C/C++ 环境  
> **约束**: 车规级 SoC (NXP S32G / Renesas R-Car / TI Jacinto), RTOS 或 Yocto Linux, 资源受限

---

## 目录

1. [A2A C++ SDK — 社区实现分析](#1-a2a-c-sdk--社区实现分析)
2. [gRPC C++ — 嵌入式可行性评估](#2-grpc-c--嵌入式可行性评估)
3. [TLS 嵌入式方案 — mbedTLS / wolfSSL](#3-tls-嵌入式方案--mbedtls--wolfssl)
4. [Protobuf 嵌入式方案 — nanopb](#4-protobuf-嵌入式方案--nanopb)
5. [策略引擎 C/C++ 替代方案](#5-策略引擎-cc-替代方案)
6. [TEE Client API — GlobalPlatform C API](#6-tee-client-api--globalplatform-c-api)
7. [全栈 C/C++ 架构设计](#7-全栈-cc-架构设计)
8. [关键代码骨架 (C++20)](#8-关键代码骨架-c20)
9. [资源占用估算](#9-资源占用估算)
10. [实施建议与风险](#10-实施建议与风险)

---

## 1. A2A C++ SDK — 社区实现分析

### 1.1 现状

A2A 官方目前没有 C++ SDK（官方的 Python/Go/Java/JS/.NET/Rust 六种语言中不含 C++）。但社区已有实现：

| 属性 | 值 |
|------|-----|
| **仓库** | [MisterVVP/a2a-cpp](https://github.com/MisterVVP/a2a-cpp) |
| **规范版本** | A2A v1.0.0 |
| **语言标准** | C++20 |
| **传输协议** | REST, JSON-RPC, gRPC |
| **构建系统** | CMake + vcpkg |
| **TCK 一致性** | ✅ 通过 A2A TCK 测试 |
| **认证钩子** | ✅ 支持自定义认证 |
| **流式** | ✅ 支持 SSE 流式 |
| **许可** | Apache 2.0 |

### 1.2 a2a-cpp 架构概览

```
a2a-cpp SDK 组件结构:

┌─────────────────────────────────────────────────────────────┐
│                      a2a-cpp SDK                              │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Client API  │  │  Server API   │  │ Agent Card Resolver  │ │
│  │             │  │               │  │                      │ │
│  │ SendMessage │  │ HandleRequest │  │ Well-Known URI       │ │
│  │ GetTask     │  │ StreamResponse│  │ Registry Client      │ │
│  │ CancelTask  │  │ TaskManager   │  │ Direct Config        │ │
│  └──────┬──────┘  └──────┬───────┘  └──────────┬───────────┘ │
│         │                │                      │             │
│  ┌──────▼────────────────▼──────────────────────▼───────────┐ │
│  │                   Transport Layer                         │ │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐  │ │
│  │  │ REST     │  │ JSON-RPC │  │ gRPC                   │  │ │
│  │  │ (libcurl)│  │ (nlohmann│  │ (gRPC C++/protobuf)    │  │ │
│  │  │          │  │  json)   │  │                        │  │ │
│  │  └──────────┘  └──────────┘  └────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                   Auth Hooks (可替换)                     │ │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐  │ │
│  │  │ Bearer   │  │ API Key  │  │ Custom (mTLS 注入点)   │  │ │
│  │  │ Token    │  │ Header   │  │                        │  │ │
│  │  └──────────┘  └──────────┘  └────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 车端适配分析

a2a-cpp 虽然在 Linux 桌面环境开发，但其 C++20 + CMake 组合意味着可以交叉编译到 Yocto Linux 目标（NXP S32G 的 A53 核、R-Car 的 Cortex-A 核）。需要对以下部分做适配：

| 原依赖 | 车端替换 | 原因 |
|--------|---------|------|
| libcurl (HTTP) | libcurl (保留) 或 自定义 HTTP client | libcurl 已在 Yocto 中广泛支持 |
| nlohmann/json | nlohmann/json (保留) | 纯头文件库，零依赖 |
| gRPC C++ | gRPC C++ (裁剪) 或 nanopb + 自定义 | 见 §2 |
| OpenSSL | **mbedTLS 或 wolfSSL** | 见 §3 |
| protobuf (完整版) | **nanopb** | 见 §4 |
| std::thread | **RTOS task 或 pthread** | 不同 RTOS 适配 |

---

## 2. gRPC C++ — 嵌入式可行性评估

### 2.1 gRPC C++ 的资源需求

gRPC C++ 是一个企业级 RPC 框架，其完整构建的体量对于深度嵌入式是挑战：

| 组件 | 完整 gRPC C++ 大小 | 裁剪后可能 |
|------|-------------------|-----------|
| libgrpc.so | ~15-20 MB (stripped) | ~5-8 MB (去除不需要的插件) |
| libprotobuf.so | ~3-5 MB | ~1.5 MB (lite mode) |
| libgpr (gRPC 基础库) | ~2 MB | ~0.5 MB |
| 依赖 (OpenSSL/zlib/c-ares/re2) | ~5 MB | ~2 MB |
| **总计 (完整构建)** | **~25-30 MB** | **~9-15 MB** |

### 2.2 车端 SoC 资源评估

| SoC 平台 | 目标核 | RAM | Flash | 适合 gRPC C++? |
|----------|--------|-----|-------|----------------|
| NXP S32G399 | Cortex-A53 (4核) | 2-4 GB DDR | 64 MB NOR + eMMC | ✅ 完整 gRPC |
| Renesas R-Car H3 | Cortex-A57 + A53 | 4-8 GB | eMMC | ✅ 完整 gRPC |
| TI Jacinto TDA4 | Cortex-A72 | 2-4 GB | eMMC | ✅ 完整 gRPC |
| NXP i.MX8 | Cortex-A53 | 1-2 GB | eMMC | ✅ 裁剪 gRPC |
| ST Stellar SR6 | Cortex-R52 (锁步) | < 10 MB SRAM | < 64 MB Flash | ❌ 需 nanopb + 自定义 |
| Infineon AURIX TC4x | TriCore | < 4 MB SRAM | < 32 MB Flash | ❌ 完全不同方案 |

### 2.3 分层策略

```
决策树: 根据 SoC 能力选择不同方案

┌─────────────────────────────────────────────────┐
│ SoC 大类           │ 方案                        │
├────────────────────┼─────────────────────────────┤
│ Cortex-A (Linux)   │ gRPC C++ (裁剪)            │
│ ≥ 512 MB RAM       │ + mbedTLS                   │
│                    │ + a2a-cpp SDK               │
├────────────────────┼─────────────────────────────┤
│ Cortex-R/M (RTOS)  │ nanopb + 自定义 JSON-RPC    │
│ ≥ 64 KB RAM        │ over HTTP/1.1               │
│                    │ + mbedTLS                   │
│                    │ + 精简 A2A 客户端 (手工实现) │
├────────────────────┼─────────────────────────────┤
│ 深度嵌入式 MCU     │ 不使用 A2A                  │
│ < 64 KB RAM        │ 使用轻量级 IPC (如 SOME/IP) │
│                    │ Agent 通过 Gateway 暴露 A2A │
└─────────────────────────────────────────────────┘
```

### 2.4 gRPC C++ 裁剪建议

```cmake
# CMake 裁剪 gRPC C++ 构建 (针对车端)

cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DgRPC_INSTALL=ON \
  -DgRPC_BUILD_TESTS=OFF \
  -DgRPC_BUILD_GRPCPP_OTEL_PLUGIN=OFF \
  -DgRPC_BUILD_CSHARP_EXT=OFF \
  -DgRPC_BUILD_GRPC_NODE_PLUGIN=OFF \
  -DgRPC_BUILD_GRPC_OBJECTIVE_C_PLUGIN=OFF \
  -DgRPC_BUILD_GRPC_PHP_PLUGIN=OFF \
  -DgRPC_BUILD_GRPC_PYTHON_PLUGIN=OFF \
  -DgRPC_BUILD_GRPC_RUBY_PLUGIN=OFF \
  -DgRPC_USE_SYSTEMD=OFF \
  -DgRPC_ZLIB_PROVIDER=package \
  -DgRPC_SSL_PROVIDER=package \
  \
  # ⚠ 关键: 使用 mbedTLS 替代 OpenSSL/BoringSSL
  -DgRPC_SSL_PROVIDER=module \
  -DgRPC_TLS_PROVIDER=module \
  \
  # 精简传输
  -DgRPC_BUILD_CODEGEN=OFF
```

---

## 3. TLS 嵌入式方案 — mbedTLS / wolfSSL

### 3.1 三个 TLS 库对比

| 属性 | OpenSSL | **mbedTLS** | **wolfSSL** |
|------|---------|------------|------------|
| 代码体积 | ~1.5 MB | **~200 KB** (可裁剪至 60KB) | ~300 KB (可裁剪至 100KB) |
| RAM (per TLS session) | ~50 KB | **~10-20 KB** | ~15-25 KB |
| 线程安全 | ✅ | ✅ | ✅ |
| TLS 1.3 | ✅ | ✅ (3.6+) | ✅ (5.0+) |
| mTLS (双向认证) | ✅ | ✅ | ✅ |
| X.509 证书验证 | ✅ | ✅ | ✅ |
| CRL 检查 | ✅ | ✅ | ✅ |
| TEE 集成 (PKCS#11) | ✅ (engine) | ✅ (PSA Crypto API) | ✅ (wolfCrypt) |
| 汽车认证 | - | ✅ (ISO 26262 ASIL-D 已认证) | ✅ (ISO 26262 ASIL-D) |
| FIPS 140-2 | ✅ | ✅ | ✅ |
| 许可证 | Apache 2.0 | **Apache 2.0 / GPL 2.0** | GPL 2.0 / 商业 |

### 3.2 推荐: mbedTLS

**理由:**
1. 体积最小 (可裁剪至 60KB)
2. 原生支持 PSA Crypto API (ARM TEE 生态)
3. 已有 ISO 26262 ASIL-D 认证
4. Apache 2.0 许可，无商业顾虑
5. gRPC 已支持 mbedTLS 作为 TLS 后端

### 3.3 mbedTLS + gRPC 的车端配置

```c
// mbedtls_config.h - 车端裁剪配置

// 只启用需要的功能
#define MBEDTLS_SSL_PROTO_TLS1_3        // TLS 1.3 only
#define MBEDTLS_SSL_CLI_C               // 客户端模式
#define MBEDTLS_SSL_SRV_C               // 服务端模式
#define MBEDTLS_X509_CRT_PARSE_C        // X.509 证书解析
#define MBEDTLS_X509_CRL_PARSE_C        // CRL 解析
#define MBEDTLS_KEY_EXCHANGE_ECDHE_ECDSA_ENABLED  // ECDSA 密钥交换

// 使用 PSA Crypto API (与 TEE 集成)
#define MBEDTLS_PSA_CRYPTO_C
#define MBEDTLS_USE_PSA_CRYPTO

// 关闭不需要的功能以减小体积
#undef MBEDTLS_SSL_PROTO_TLS1_2        // 不需要 TLS 1.2
#undef MBEDTLS_SSL_PROTO_DTLS          // 不需要 DTLS
#undef MBEDTLS_RSA_C                   // 不需要 RSA (用 ECDSA)
#undef MBEDTLS_DHM_C                   // 不需要 DHM (用 ECDHE)
```

### 3.4 mTLS 的 PSA Crypto 集成 (TEE Key Store)

```c
// 使用 PSA Crypto API 将私钥操作委托给 TEE

#include <psa/crypto.h>

// 在 TEE 中生成密钥对 (私钥永不离开 TEE)
psa_key_attributes_t attributes = PSA_KEY_ATTRIBUTES_INIT;
psa_set_key_usage_flags(&attributes, PSA_KEY_USAGE_SIGN_HASH);
psa_set_key_algorithm(&attributes, PSA_ALG_ECDSA(PSA_ALG_SHA_256));
psa_set_key_type(&attributes, PSA_KEY_TYPE_ECC_KEY_PAIR(PSA_ECC_FAMILY_SECP_R1));
psa_set_key_lifetime(&attributes, 
    PSA_KEY_LIFETIME_PERSISTENT);  // 持久化存储在 TEE 中

psa_key_id_t key_id;
psa_generate_key(&attributes, &key_id);
// key_id 后续可以被 mbedTLS 的 PSA 后端使用
// 签名操作在 TEE 内部完成，私钥不暴露给 Normal World
```

---

## 4. Protobuf 嵌入式方案 — nanopb

### 4.1 nanopb 简介

nanopb 是 Google Protobuf 针对嵌入式系统的轻量级实现：

| 属性 | 完整 protobuf (C++) | **nanopb (C)** |
|------|-------------------|---------------|
| 代码大小 | ~2 MB | **~20-30 KB** |
| Runtime | ~500 KB | **~6-10 KB** |
| 语言 | C++ | **C** (可在 C++ 中调用) |
| 动态分配 | 大量 | **静态分配为主** |
| 反射 | 支持 | 不支持 (不需要) |
| 兼容性 | 完整 proto2/proto3 | **proto3 subset** |
| 生成代码 | .pb.cc / .pb.h | .pb.c / .pb.h |

### 4.2 车端 A2A 的 protobuf 策略

```
分层策略:

Layer 1 (Cortex-A, Linux) — 使用完整 protobuf + gRPC C++
  → 直接使用 a2a-cpp SDK 的 gRPC transport
  → 适合: 域控制器 (R-Car H3, S32G, TDA4)

Layer 2 (Cortex-R/M, RTOS) — 使用 nanopb + 自定义 A2A 编解码
  → 从 a2a.proto 生成 nanopb 代码
  → 手动实现 A2A JSON-RPC over HTTP/1.1
  → 适合: MCU 级域控制器 (Stellar SR6)
```

```bash
# 使用 nanopb generator 从 a2a.proto 生成嵌入式代码
nanopb_generator \
  -I /path/to/a2a/proto \
  -D /path/to/output \
  -L '#include "a2a.pb.h"' \
  a2a.proto

# 输出:
# a2a.pb.c  (~30KB 生成的编解码代码)
# a2a.pb.h  (类型定义)
```

### 4.3 nanopb 使用示例

```c
// 使用 nanopb 构造 A2A SendMessage 请求

#include "a2a.pb.h"
#include <pb_encode.h>
#include <pb_decode.h>

// --- 静态分配消息 (无 malloc) ---
static lf_a2a_v1_SendMessageRequest request;
static lf_a2a_v1_Message message;
static lf_a2a_v1_Part part;
static lf_a2a_v1_SendMessageResponse response;

void build_send_message_request(void) {
    // 初始化
    message = lf_a2a_v1_Message_init_zero;
    part = lf_a2a_v1_Part_init_zero;
    
    // 设置 Part
    part.which_content = lf_a2a_v1_Part_text_tag;
    strncpy(part.content.text, "请读取当前车速", 
            sizeof(part.content.text));
    
    // 设置 Message
    strncpy(message.message_id, "msg-001", sizeof(message.message_id));
    message.role = lf_a2a_v1_Role_ROLE_USER;
    message.parts = &part;
    message.parts_count = 1;
    
    // 设置 Request
    request.message = &message;
    
    // 编码为 protobuf 二进制
    uint8_t buffer[512];
    pb_ostream_t stream = pb_ostream_from_buffer(buffer, sizeof(buffer));
    pb_encode(&stream, lf_a2a_v1_SendMessageRequest_fields, &request);
    // buffer 现在包含编码后的 A2A 请求
}
```

---

## 5. 策略引擎 C/C++ 替代方案

### 5.1 为什么不能直接用 OPA

OPA (Open Policy Agent) 是用 Go 编写的，无法直接在嵌入式 C/C++ 环境运行。有以下替代方案：

### 5.2 方案对比

| 方案 | 原理 | 体量 | 性能 | 策略语言 | 推荐度 |
|------|------|------|------|---------|--------|
| **OPA WASM** | OPA 编译为 WASM，用 C WASM runtime 执行 | WASM runtime ~100KB + policy ~50KB | ~0.5ms/eval | Rego | ⭐⭐⭐⭐ |
| **Casbin C++** | C++ 原生授权库 | ~150KB | <0.1ms/eval | CSV-based model | ⭐⭐⭐ |
| **TinyRBAC** | 自研轻量 RBAC 引擎 | ~20KB | <0.05ms/eval | C structs | ⭐⭐⭐⭐⭐ |
| **编译时 Rego → C** | 预编译 Rego 策略为 C 决策表 | ~50KB | <0.01ms/eval | Rego→C | ⭐⭐⭐ |

### 5.3 推荐: 双层方案

```
高性能路径 (99% 请求):
  TinyRBAC (C 编译型) — <0.05ms, 处理标准域隔离 + ASIL 门控

完整路径 (1% 请求):
  OPA WASM (需要完整 Rego 语义的场景) — ~0.5ms, 复杂条件决策
```

### 5.4 TinyRBAC — 车端自研轻量策略引擎

```c
/*
 * tiny_rbac.h
 * 车端轻量级 RBAC + ASIL 策略引擎
 * 
 * 设计约束:
 * - 零动态内存分配 (编译时确定所有数据结构)
 * - <0.05ms 决策延迟
 * - 支持热更新 (策略表可被 OTA 替换)
 */

#ifndef TINY_RBAC_H
#define TINY_RBAC_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================
// 类型定义
// ============================================================

// ASIL 等级 (编译为单个字节)
typedef enum {
    ASIL_QM   = 0,
    ASIL_A    = 1,
    ASIL_B    = 2,
    ASIL_C    = 3,
    ASIL_D    = 4,
} asil_level_t;

// 功能域
typedef enum {
    DOMAIN_CHASSIS      = 0,
    DOMAIN_POWERTRAIN   = 1,
    DOMAIN_BODY         = 2,
    DOMAIN_INFOTAINMENT = 3,
    DOMAIN_ADAS         = 4,
    DOMAIN_CONNECTIVITY = 5,
    DOMAIN_SECURITY     = 6,
    DOMAIN_MAX,
} domain_t;

// 动作类型
typedef enum {
    ACTION_SKILL_INVOKE = 0,
    ACTION_TOOL_CALL    = 1,
    ACTION_DATA_READ    = 2,
    ACTION_DATA_WRITE   = 3,
} action_type_t;

// 车辆状态
typedef enum {
    VEHICLE_PARKED   = 0,
    VEHICLE_STOPPED  = 1,
    VEHICLE_MOVING   = 2,
    VEHICLE_CHARGING = 3,
} vehicle_state_t;

// Skill ID (编译时枚举, 保证确定性)
typedef enum {
    SKILL_READ_SPEED           = 0,
    SKILL_READ_DTC             = 1,
    SKILL_READ_GPS             = 2,
    SKILL_SET_CABIN_TEMP       = 3,
    SKILL_EMERGENCY_BRAKE      = 4,
    SKILL_STEERING_OVERRIDE    = 5,
    SKILL_ENGINE_KILL          = 6,
    SKILL_UNLOCK_DOORS         = 7,
    SKILL_FLASH_ECU            = 8,
    SKILL_AIRBAG_DEPLOY        = 9,
    // ... 最多 256 个 Skills
    SKILL_MAX = 255,
} skill_id_t;

// ============================================================
// 策略规则 (编译时定义的决策表)
// ============================================================

typedef struct {
    uint8_t skill_id;               // 目标 Skill ID
    action_type_t action_type;      // 动作类型
    uint8_t caller_domain_mask;     // 允许的调用方域位掩码
    asil_level_t min_caller_asil;   // 调用方最低 ASIL 等级
    bool require_user_confirm;      // 是否需要用户确认
    bool require_tee_attested;      // 是否需要 TEE 证明
    uint8_t prohibited_vehicle_states; // 禁止的车辆状态位掩码
} policy_rule_t;

// ============================================================
// 决策输入
// ============================================================

typedef struct {
    domain_t caller_domain;
    asil_level_t caller_asil;
    bool caller_tee_attested;
    
    domain_t target_domain;
    skill_id_t target_skill;
    action_type_t action;
    
    vehicle_state_t vehicle_state;
    bool user_confirmed;
    uint32_t user_confirmation_timestamp_ms;
    
    uint8_t current_rate_count;     // 当前速率计数
} authz_input_t;

// ============================================================
// 决策输出
// ============================================================

typedef enum {
    AUTHZ_ALLOW                 = 0,
    AUTHZ_DENY                  = 1,
    AUTHZ_DENY_NEED_USER_CONFIRM = 2,  // 可恢复: 需要用户确认
    AUTHZ_DENY_RATE_LIMIT       = 3,    // 可恢复: 稍后重试
    AUTHZ_DENY_VEHICLE_STATE    = 4,    // 可恢复: 等车辆状态改变
    AUTHZ_DENY_NOT_ATTESTED     = 5,    // 不可恢复: TEE 未证明
    AUTHZ_DENY_DOMAIN_ISOLATION = 6,    // 不可恢复: 域隔离违反
} authz_decision_t;

// ============================================================
// API
// ============================================================

/*
 * 初始化策略引擎 (从静态策略表加载)
 * 
 * 参数:
 *   rules       - 策略规则数组 (编译时定义或从 flash 加载)
 *   rule_count  - 规则数量
 *   
 * 返回: 0 = 成功, -1 = 策略表校验失败
 */
int tiny_rbac_init(const policy_rule_t* rules, uint32_t rule_count);

/*
 * 授权决策 — 查找策略表中的匹配规则
 * 
 * 查找策略:
 *   1. target_skill 精确匹配
 *   2. caller_domain_mask 位掩码匹配
 *   3. min_caller_asil 检查
 *   4. 如果 require_user_confirm=true 但 user_confirmed=false
 *      → 返回 AUTHZ_DENY_NEED_USER_CONFIRM
 *   5. 如果 prohibited_vehicle_states 匹配
 *      → 返回 AUTHZ_DENY_VEHICLE_STATE
 *   6. 如果 require_tee_attested=true 但 caller_tee_attested=false
 *      → 返回 AUTHZ_DENY_NOT_ATTESTED
 *   7. 速率检查
 *   8. → 返回 AUTHZ_ALLOW
 *   
 * 复杂度: O(log N) 或 O(1) (取决于编译时优化)
 * 延迟: < 0.05ms
 */
authz_decision_t tiny_rbac_evaluate(const authz_input_t* input);

/*
 * 获取决策的人类可读描述 (用于 A2A TaskStatus.message)
 */
const char* tiny_rbac_decision_message(authz_decision_t decision);

/*
 * 检查决策是否可恢复 (Client 可以通过某种操作恢复)
 */
static inline bool tiny_rbac_is_recoverable(authz_decision_t decision) {
    return (decision == AUTHZ_DENY_NEED_USER_CONFIRM ||
            decision == AUTHZ_DENY_RATE_LIMIT       ||
            decision == AUTHZ_DENY_VEHICLE_STATE);
}

/*
 * 获取可恢复决策的 A2A 恢复提示
 */
typedef struct {
    const char* prompt_title;
    const char* prompt_message;
    const char* confirm_text;
    const char* cancel_text;
    uint32_t    timeout_ms;
} hmi_confirmation_hint_t;

bool tiny_rbac_get_confirmation_hint(
    authz_decision_t decision,
    const authz_input_t* input,
    hmi_confirmation_hint_t* hint
);

#ifdef __cplusplus
}
#endif

#endif // TINY_RBAC_H
```

### 5.5 TinyRBAC 策略表定义

```c
/*
 * policy_table.c
 * 车端 Agent 策略表 — 编译时定义, OTA 可更新
 * 
 * 策略表存储: Flash 中单独的 section, 可被 OTA 替换
 */

// GCC section 属性 — 将策略表放在可独立更新的 Flash 区域
#define POLICY_SECTION __attribute__((section(".policy_table")))

static const policy_rule_t g_policy_table[] POLICY_SECTION = {
    // ===========================================================
    // 安全关键: emergency_brake
    // ===========================================================
    {
        .skill_id = SKILL_EMERGENCY_BRAKE,
        .action_type = ACTION_SKILL_INVOKE,
        // 允许: ADAS (同域) + Infotainment (需用户确认)
        .caller_domain_mask = (1 << DOMAIN_ADAS) | (1 << DOMAIN_INFOTAINMENT),
        .min_caller_asil = ASIL_QM,           // Infotainment=QM 也允许
        .require_user_confirm = true,         // ⚠ 但必须用户确认
        .require_tee_attested = true,         // 必须 TEE 证明
        .prohibited_vehicle_states = 0,       // 任何车辆状态都允许
    },
    
    // ===========================================================
    // 同域读取: read_speed (chassis 域内自由读取)
    // ===========================================================
    {
        .skill_id = SKILL_READ_SPEED,
        .action_type = ACTION_DATA_READ,
        .caller_domain_mask = (1 << DOMAIN_CHASSIS) |      // 同域
                              (1 << DOMAIN_ADAS) |          // ADAS 可读
                              (1 << DOMAIN_CONNECTIVITY),   // 连接域可读
        .min_caller_asil = ASIL_QM,
        .require_user_confirm = false,
        .require_tee_attested = false,          // 纯读取不需要 TEE
        .prohibited_vehicle_states = 0,
    },
    
    // ===========================================================
    // ECU 刷写: flash_ecu (仅连接域 + 车辆静止)
    // ===========================================================
    {
        .skill_id = SKILL_FLASH_ECU,
        .action_type = ACTION_SKILL_INVOKE,
        .caller_domain_mask = (1 << DOMAIN_CONNECTIVITY),
        .min_caller_asil = ASIL_QM,
        .require_user_confirm = true,          // 需要用户确认
        .require_tee_attested = true,          // 需要 TEE 证明
        .prohibited_vehicle_states = (1 << VEHICLE_MOVING), // 行驶中禁止
    },
    
    // ... 更多策略规则 (总规则数通常 < 200)
};

static const uint32_t g_policy_table_size = 
    sizeof(g_policy_table) / sizeof(g_policy_table[0]);
```

---

## 6. TEE Client API — GlobalPlatform C API

### 6.1 API 概述

GlobalPlatform TEE Client API 是 TEE 与 Normal World 应用通信的标准化 C API。车端 TEE 实现 (如 OP-TEE) 遵循此标准。

```
Normal World (C/C++ Application)          Secure World (TEE)
┌─────────────────────────────────┐    ┌─────────────────────┐
│  Agent Process                  │    │  KMSS TA            │
│                                 │    │                     │
│  TEE Client API (libteec.so)   │    │  TEE Internal API   │
│  ┌───────────────────────────┐ │    │                     │
│  │ TEEC_InitializeContext()  │─┼────→│                     │
│  │ TEEC_OpenSession()        │─┼────→│                     │
│  │ TEEC_InvokeCommand()      │─┼────→│ invokeCommand()    │
│  │ TEEC_CloseSession()       │─┼────→│                     │
│  │ TEEC_FinalizeContext()    │─┼────→│                     │
│  └───────────────────────────┘ │    │                     │
└─────────────────────────────────┘    └─────────────────────┘
```

### 6.2 车端 KMSS 的 TEE 集成

```c
/*
 * kmss_tee_client.c
 * 通过 GlobalPlatform TEE Client API 与 KMSS TA 通信
 */

#include <tee_client_api.h>
#include <string.h>

// KMSS TA UUID (编译时定义)
#define KMSS_TA_UUID \
    { 0xA1B2C3D4, 0xE5F6, 0x7890, \
      { 0xAB, 0xCD, 0xEF, 0x01, 0x23, 0x45, 0x67, 0x89 } }

// KMSS TA 命令 ID
enum {
    KMSS_CMD_ISSUE_CERTIFICATE = 0,
    KMSS_CMD_RENEW_CERTIFICATE = 1,
    KMSS_CMD_GET_CRL           = 2,
    KMSS_CMD_VERIFY_CHAIN      = 3,
};

/*
 * 从 KMSS TA 签发 Agent 证书
 * 
 * 流程:
 *   1. TEE 内部生成密钥对 (私钥永不离片)
 *   2. TEE 内部签发 x.509 证书
 *   3. 返回证书链到 Normal World
 */
int kmss_issue_agent_certificate(
    const char* agent_spiffe_id,
    const char* agent_domain,
    int asil_level,
    uint8_t* cert_chain_out,
    size_t* cert_chain_len,
    uint8_t* crl_out,
    size_t* crl_len
) {
    TEEC_Context ctx;
    TEEC_Session sess;
    TEEC_Operation op;
    TEEC_UUID uuid = KMSS_TA_UUID;
    TEEC_Result res;
    
    // 1. 初始化 TEE 上下文
    res = TEEC_InitializeContext(NULL, &ctx);
    if (res != TEEC_SUCCESS) return -1;
    
    // 2. 打开与 KMSS TA 的会话
    res = TEEC_OpenSession(&ctx, &sess, &uuid, 
                           TEEC_LOGIN_PUBLIC, NULL, NULL, NULL);
    if (res != TEEC_SUCCESS) {
        TEEC_FinalizeContext(&ctx);
        return -1;
    }
    
    // 3. 准备共享内存 (用于传输 CSR 和证书)
    //    注意: 共享内存必须用 TEEC_AllocateSharedMemory 分配
    //    这里简化展示，实际需要处理内存共享
    
    // 4. 调用 KMSS TA: 签发证书
    memset(&op, 0, sizeof(op));
    op.paramTypes = TEEC_PARAM_TYPES(
        TEEC_MEMREF_TEMP_INPUT,   // param0: CSR 数据
        TEEC_MEMREF_TEMP_OUTPUT,  // param1: 证书链
        TEEC_MEMREF_TEMP_OUTPUT,  // param2: CRL
        TEEC_NONE
    );
    
    // ⚠ 实际实现需要:
    //    - 先获取 TEE Attestation Report
    //    - 将 Attestation Report + CSR 作为输入
    //    - 解析返回的证书链 + CRL
    
    res = TEEC_InvokeCommand(&sess, KMSS_CMD_ISSUE_CERTIFICATE, 
                             &op, NULL);
    
    // 5. 清理
    TEEC_CloseSession(&sess);
    TEEC_FinalizeContext(&ctx);
    
    return (res == TEEC_SUCCESS) ? 0 : -1;
}
```

---

## 7. 全栈 C/C++ 架构设计

### 7.1 Cortex-A (Linux) 完整方案

```
┌─────────────────────────────────────────────────────────────────────┐
│             Cortex-A (Linux/Yocto) 完整 A2A + IAM 栈                  │
│             SoC: S32G / R-Car H3 / TDA4 VM                           │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Application Layer                            │ │
│  │                                                                  │ │
│  │  Agent Process (C++20)                                          │ │
│  │  ┌────────────┐  ┌──────────────┐  ┌──────────────────────────┐│ │
│  │  │ A2A Server │  │ A2A Client   │  │ Agent Card Publisher     ││ │
│  │  │ (a2a-cpp)  │  │ (a2a-cpp)    │  │ (a2a-cpp)               ││ │
│  │  └──────┬─────┘  └──────┬───────┘  └────────────┬─────────────┘│ │
│  └─────────┼───────────────┼───────────────────────┼──────────────┘ │
│            │               │                       │                │
│  ┌─────────▼───────────────▼───────────────────────▼──────────────┐ │
│  │                     IAM Layer (C++)                             │ │
│  │  ┌───────────────┐  ┌──────────────┐  ┌──────────────────────┐ │ │
│  │  │ mTLS Auth     │  │ TinyRBAC     │  │ Audit Logger         │ │ │
│  │  │ Interceptor   │  │ Engine       │  │ (链式 HMAC, C)       │ │ │
│  │  │               │  │              │  │                      │ │ │
│  │  │ - 提取证书    │  │ - 查策略表   │  │ - 二进制格式         │ │ │
│  │  │ - 解析 SPIFFE │  │ - O(1) 决策  │  │ - TEE 签名          │ │ │
│  │  │ - CRL 检查    │  │              │  │                      │ │ │
│  │  └───────────────┘  └──────────────┘  └──────────────────────┘ │ │
│  └──────────────────────────┬─────────────────────────────────────┘ │
│                             │                                        │
│  ┌──────────────────────────▼─────────────────────────────────────┐ │
│  │                    Transport Layer                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │ │
│  │  │ gRPC C++     │  │ libcurl      │  │ nlohmann/json        │  │ │
│  │  │ (裁剪)       │  │ (HTTP REST)  │  │ (JSON 解析)         │  │ │
│  │  └──────┬───────┘  └──────────────┘  └──────────────────────┘  │ │
│  └─────────┼──────────────────────────────────────────────────────┘ │
│            │                                                        │
│  ┌─────────▼──────────────────────────────────────────────────────┐ │
│  │                    TLS Layer                                    │ │
│  │  ┌──────────────────────────────────────────────────────────┐  │ │
│  │  │ mbedTLS + PSA Crypto Driver                               │  │ │
│  │  │ - TLS 1.3 only                                            │  │ │
│  │  │ - ECDSA P-256                                             │  │ │
│  │  │ - mTLS (双向)                                             │  │ │
│  │  └──────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    TEE Client API (libteec.so)                  │ │
│  │  - TEEC_OpenSession → KMSS TA                                   │ │
│  │  - TEEC_InvokeCommand → 证书签发/密钥操作                       │ │
│  └──────────────────────────┬─────────────────────────────────────┘ │
│                             │                                        │
│              ┌──────────────▼──────────────┐                        │
│              │        Secure World          │                        │
│              │  ┌────────────────────────┐ │                        │
│              │  │ KMSS TA (OP-TEE)       │ │                        │
│              │  │ - Vehicle Instance CA  │ │                        │
│              │  │ - 密钥生成与存储        │ │                        │
│              │  │ - 证书签发与吊销        │ │                        │
│              │  └────────────────────────┘ │                        │
│              └─────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Cortex-R/M (RTOS) 精简方案

```
┌─────────────────────────────────────────────────────────────────────┐
│           Cortex-R/M (RTOS) 精简 A2A Client + IAM                     │
│           MCU: Stellar SR6 / S32K                                    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Agent Task (C, FreeRTOS/SAFERTOS)                              │ │
│  │                                                                  │ │
│  │  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐  │ │
│  │  │ A2A Light Client │  │ TinyRBAC     │  │ Audit Buffer     │  │ │
│  │  │ (手工实现)        │  │              │  │ (环形缓冲区)     │  │ │
│  │  │                  │  │              │  │                  │  │ │
│  │  │ - SendMessage    │  │ - 查策略表   │  │ - 预分配 1KB    │  │ │
│  │  │ - GetTask        │  │ - O(1) 决策  │  │ - DMA to flash  │  │ │
│  │  │ - nanopb 编解码  │  │              │  │                  │  │ │
│  │  └────────┬─────────┘  └──────────────┘  └──────────────────┘  │ │
│  └───────────┼──────────────────────────────────────────────────────┘ │
│              │                                                       │
│  ┌───────────▼──────────────────────────────────────────────────────┐ │
│  │  Transport: HTTP/1.1 over TCP/IP (lwIP or custom)                │ │
│  │  + nanopb serialization                                          │ │
│  │  + JSON encoding (手动拼接, 不用库)                               │ │
│  └──────────────────────────┬───────────────────────────────────────┘ │
│                             │                                        │
│  ┌──────────────────────────▼───────────────────────────────────────┐ │
│  │  mbedTLS (裁剪至 60KB): TLS 1.3 + mTLS + ECDSA                  │ │
│  └──────────────────────────┬───────────────────────────────────────┘ │
│                             │                                        │
│  ┌──────────────────────────▼───────────────────────────────────────┐ │
│  │  HSM / SHE (Secure Hardware Extension)                            │ │
│  │  - 硬件密钥存储 (替代 TEE)                                        │ │
│  │  - ECDSA 签名加速                                                 │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ⚠ 注意: RTOS 方案只作为 A2A Client，不启动 A2A Server               │
│     通过 Domain Gateway (Cortex-A) 暴露 Agent 给其他 Agent             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. 关键代码骨架 (C++20)

### 8.1 IAM gRPC Interceptor (C++)

```cpp
// iam_interceptor.hpp
// C++20 gRPC interceptor — 车端 IAM 鉴权

#pragma once

#include <grpcpp/grpcpp.h>
#include <grpcpp/security/credentials.h>
#include <grpcpp/security/tls_credentials_options.h>

#include "tiny_rbac.h"
#include "audit_logger.h"

// ============================================================
// IAM AuthnInterceptor — 从 mTLS 证书提取身份
// ============================================================

class IamAuthnInterceptor : public grpc::experimental::Interceptor {
public:
    void Intercept(grpc::experimental::InterceptorBatchMethods* methods) override {
        if (methods->QueryInterceptionHookPoint(
                grpc::experimental::InterceptionHookPoints::PRE_SEND_INITIAL_METADATA)) {
            // Nothing to add — mTLS handled at transport level
        }
        
        if (methods->QueryInterceptionHookPoint(
                grpc::experimental::InterceptionHookPoints::POST_RECV_INITIAL_METADATA)) {
            
            // Extract peer identity from TLS session
            auto* server_ctx = GetServerContext(methods);
            auto auth_ctx = server_ctx->auth_context();
            
            if (!auth_ctx->IsPeerAuthenticated()) {
                methods->Fail(grpc::Status(
                    grpc::StatusCode::UNAUTHENTICATED,
                    "mTLS required — no valid client certificate"));
                return;
            }
            
            // Extract SPIFFE ID from certificate SAN
            auto spiffe_prop = auth_ctx->FindPropertyValues(
                "x509_spiffe_id");
            if (spiffe_prop.empty()) {
                methods->Fail(grpc::Status(
                    grpc::StatusCode::UNAUTHENTICATED,
                    "No SPIFFE ID in client certificate"));
                return;
            }
            
            std::string spiffe_id = std::string(spiffe_prop[0].data(),
                                                  spiffe_prop[0].length());
            
            // Parse caller identity
            auto caller = parse_spiffe_id(spiffe_id);  // 解析域名、类型、名称
            caller.tee_attested = auth_ctx->FindPropertyValues(
                "x509_tee_attested").size() > 0;
            
            // Store in gRPC context for downstream interceptors
            server_ctx->AddInitialMetadata("iam-spiffe-id", spiffe_id);
            server_ctx->AddInitialMetadata("iam-domain", 
                std::to_string(static_cast<int>(caller.domain)));
            
            // CRL check
            if (crl_checker_.IsRevoked(extract_cert_serial(auth_ctx))) {
                methods->Fail(grpc::Status(
                    grpc::StatusCode::UNAUTHENTICATED,
                    "Certificate has been revoked"));
                return;
            }
        }
        
        methods->Proceed();
    }
    
private:
    CRLChecker crl_checker_;  // 本地 CRL 缓存
    CallerIdentity parse_spiffe_id(const std::string& spiffe_id);
    std::string extract_cert_serial(
        std::shared_ptr<const grpc::AuthContext> auth_ctx);
};

// ============================================================
// IAM AuthzInterceptor — 权限决策
// ============================================================

class IamAuthzInterceptor : public grpc::experimental::Interceptor {
public:
    void Intercept(grpc::experimental::InterceptorBatchMethods* methods) override {
        if (methods->QueryInterceptionHookPoint(
                grpc::experimental::InterceptionHookPoints::POST_RECV_INITIAL_METADATA)) {
            
            auto* server_ctx = GetServerContext(methods);
            const auto& metadata = server_ctx->client_metadata();
            
            // Build authz input from gRPC metadata + TLS context
            authz_input_t input = {};
            input.caller_domain = parse_domain_from_metadata(metadata, "iam-domain");
            input.target_skill = parse_skill_from_method(
                server_ctx->method());
            input.user_confirmed = metadata.find("a2a-user-confirmation") 
                                   != metadata.end();
            
            // ⚡ Fast path: TinyRBAC (< 0.05ms)
            authz_decision_t decision = tiny_rbac_evaluate(&input);
            
            // Write audit log (in background)
            audit_logger_.WriteAsync(decision, input, 
                                     server_ctx->method());
            
            if (decision != AUTHZ_ALLOW) {
                if (tiny_rbac_is_recoverable(decision)) {
                    // → A2A Handler will return TASK_STATE_AUTH_REQUIRED
                    // Store decision in metadata for handler
                    server_ctx->AddInitialMetadata(
                        "iam-authz-decision", 
                        std::to_string(static_cast<int>(decision)));
                    // Don't fail here — let handler decide
                } else {
                    // → Hard deny
                    methods->Fail(grpc::Status(
                        grpc::StatusCode::PERMISSION_DENIED,
                        tiny_rbac_decision_message(decision)));
                    return;
                }
            }
        }
        
        methods->Proceed();
    }
    
private:
    AuditLogger audit_logger_;
};

// ============================================================
// Interceptor Factory
// ============================================================

class IamInterceptorFactory 
    : public grpc::experimental::ServerInterceptorFactoryInterface {
public:
    grpc::experimental::Interceptor* 
    CreateServerInterceptor(grpc::experimental::ServerRpcInfo* info) override {
        // Chain: Authn → Authz
        // gRPC C++ doesn't natively support interceptor chaining,
        // so we use a composite pattern or register separately
        
        // For simplicity, return a composite interceptor
        return new IamCompositeInterceptor();
    }
};
```

### 8.2 A2A Server + IAM 集成 (C++)

```cpp
// a2a_iam_server.cpp
// A2A gRPC Server with IAM interceptors

#include "a2a/server/grpc_server.hpp"   // a2a-cpp SDK
#include "a2a/types/agent_card.hpp"
#include "iam_interceptor.hpp"
#include "tiny_rbac.h"
#include "kmss_tee_client.h"

int main() {
    // =========================================
    // 0. TEE 初始化 — 获取 Agent 证书
    // =========================================
    uint8_t cert_chain[4096];
    size_t cert_chain_len;
    uint8_t crl[16384];
    size_t crl_len;
    
    int ret = kmss_issue_agent_certificate(
        "spiffe://vehicle-LSVN123.local/chassis/agent/adas-controller",
        "chassis", ASIL_D,
        cert_chain, &cert_chain_len,
        crl, &crl_len
    );
    if (ret != 0) {
        fprintf(stderr, "FATAL: Cannot obtain agent certificate from KMSS\n");
        return 1;
    }
    
    // =========================================
    // 1. 初始化 IAM 策略引擎
    // =========================================
    tiny_rbac_init(g_policy_table, g_policy_table_size);
    
    // =========================================
    // 2. 构建 mTLS 凭证 (mbedTLS backend)
    // =========================================
    grpc::experimental::TlsKeyMaterialsConfig::PemKeyCertPair cert_pair;
    cert_pair.private_key = load_tls_key_from_tee();  // ⚠ 从 TEE 加载
    cert_pair.cert_chain = std::string(
        reinterpret_cast<char*>(cert_chain), cert_chain_len);
    
    auto key_materials = std::make_shared<
        grpc::experimental::StaticDataCertificateProvider>(
        "root-cert",      // 信任根 (Vehicle CA chain)
        cert_pair
    );
    
    auto tls_opts = std::make_shared<
        grpc::experimental::TlsServerCredentialsOptions>(
        key_materials
    );
    tls_opts->set_cert_request_type(
        GRPC_SSL_REQUEST_AND_REQUIRE_CLIENT_CERTIFICATE_AND_VERIFY
    );
    tls_opts->set_check_call_host(false);  // 不检查 SNI
    
    auto server_creds = grpc::experimental::TlsServerCredentials(*tls_opts);
    
    // =========================================
    // 3. 构建 Agent Card
    // =========================================
    a2a::AgentCard card;
    card.name = "ADAS Controller";
    card.description = "Vehicle ADAS domain agent";
    card.url = "grpcs://adas.chassis.vehicle.local:8443";
    card.version = "1.0.0";
    card.capabilities.streaming = true;
    card.capabilities.push_notifications = false;
    card.capabilities.extended_agent_card = true;
    
    // 安全声明: mTLS
    a2a::SecurityScheme mtls_scheme;
    mtls_scheme.type = "mutualTls";
    mtls_scheme.description = "Vehicle PKI mTLS";
    card.security_schemes["vehicleMtls"] = mtls_scheme;
    card.security.push_back({"vehicleMtls"});
    
    // Skills
    a2a::AgentSkill brake_skill;
    brake_skill.id = "emergency_brake";
    brake_skill.name = "Emergency Brake";
    brake_skill.description = "Execute emergency braking maneuver";
    brake_skill.tags = {"safety", "ASIL-D"};
    card.skills.push_back(brake_skill);
    
    // =========================================
    // 4. 构建 gRPC Server + IAM Interceptors
    // =========================================
    grpc::ServerBuilder builder;
    builder.AddListeningPort("0.0.0.0:8443", server_creds);
    
    // 注册 IAM Interceptor
    builder.experimental().SetInterceptorCreators({
        std::make_unique<IamAuthnInterceptorFactory>(),
        std::make_unique<IamAuthzInterceptorFactory>(),
    });
    
    // 注册 A2A Service
    a2a::GrpcA2AService a2a_service(card);
    builder.RegisterService(&a2a_service);
    
    // =========================================
    // 5. 启动 Server
    // =========================================
    auto server = builder.BuildAndStart();
    printf("A2A Agent '%s' listening on grpcs://0.0.0.0:8443\n", 
           card.name.c_str());
    printf("  SPIFFE ID: spiffe://vehicle-LSVN123.local/chassis/"
           "agent/adas-controller\n");
    printf("  ASIL: D\n");
    printf("  Security: mutualTls (mbedTLS + PSA Crypto + TEE)\n");
    
    server->Wait();
    return 0;
}
```

---

## 9. 资源占用估算

### 9.1 Cortex-A (Linux) 方案

| 组件 | Flash/Storage | RAM | 备注 |
|------|--------------|-----|------|
| Linux Kernel (裁剪) | 8-12 MB | 20-30 MB | Yocto 最小镜像 |
| gRPC C++ (裁剪) | 5-8 MB | 3-5 MB | 静态链接 |
| mbedTLS | 200 KB | 50 KB | 含 PSA Crypto |
| protobuf (lite) | 1.5 MB | 500 KB | 静态链接 |
| a2a-cpp SDK | ~500 KB | ~200 KB | 仅需的 transport |
| TinyRBAC | 20 KB | 5 KB | 策略表 4KB |
| Audit Logger | 8 KB | 16 KB | 环形 buffer |
| Agent 业务逻辑 | 自定义 | 自定义 | |
| **总计** | **~18-25 MB** | **~30-45 MB** | 适合 512MB+ RAM SoC |

### 9.2 Cortex-R/M (RTOS) 方案

| 组件 | Flash | RAM | 备注 |
|------|-------|-----|------|
| FreeRTOS | 20 KB | 10 KB | |
| lwIP (TCP/IP) | 60 KB | 30 KB | |
| mbedTLS (裁剪至 60KB) | 60 KB | 20 KB | TLS 1.3 only |
| nanopb + 生成的 A2A 代码 | 30 KB | 10 KB | 静态分配 |
| TinyRBAC | 20 KB | 5 KB | |
| A2A Light Client | 15 KB | 8 KB | 手工实现 |
| Audit Buffer | 2 KB | 4 KB | |
| Agent 业务逻辑 | 自定义 | 自定义 | |
| **总计** | **~210 KB+** | **~90 KB+** | 适合 256KB+ Flash MCU |

> ⚠ RTOS 方案仅为 A2A Client，不启动 Server。Agent 通过 CAN/Ethernet 与 Domain Gateway (Cortex-A) 通信，Gateway 将 Agent 暴露为 A2A Server。

---

## 10. 实施建议与风险

### 10.1 风险矩阵

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| a2a-cpp 社区维护停止 | 中 | 高 | Fork + 内部维护 |
| gRPC C++ 在 Yocto 编译失败 | 中 | 中 | 预编译工具链 + 容器化构建 |
| mbedTLS 性能不满足延迟要求 | 低 | 中 | 硬件加密加速 (CAAM/HASH) |
| 策略表 OTA 更新导致安全漏洞 | 低 | 高 | 策略表 TEE 签名验证 + 回滚保护 |
| OPA WASM runtime 资源不足 | 中 | 低 | 降级为纯 TinyRBAC |
| TEE 驱动兼容性 | 中 | 高 | 选定 SoC 后尽早做 TEE 集成测试 |

### 10.2 实施路线图

```
Phase 1: 基础编译与验证 (4-6 周)
├── Yocto 工具链集成 (gRPC C++ + mbedTLS + protobuf)
├── a2a-cpp SDK 交叉编译 + 最小 Example 运行
├── mTLS 握手验证 (mbedTLS + PSA Crypto + TEE)
└── 交付: Docker 构建容器 + 可启动的 Minimal Agent

Phase 2: IAM 集成 (4-6 周)
├── TinyRBAC 实现 + 单元测试
├── gRPC Interceptor 集成
├── KMSS TEE Client 集成 (证书签发)
├── Audit Logger 实现
└── 交付: 带 IAM 鉴权的 Agent Server

Phase 3: 车端适配 (6-8 周)
├── Yocto BSP 适配 (目标 SoC)
├── mbedTLS 硬件加速集成 (CAAM/SEC)
├── TEE 驱动适配 (OP-TEE / 商业 TEE)
├── 性能压测 + 延迟优化
├── 安全审计 (mTLS 配置、策略表、TEE 通信)
└── 交付: 在真实硬件上运行的完整方案
```

### 10.3 关键 Makefile/CMake 示例

```cmake
# CMakeLists.txt — 车端 A2A + IAM Agent 构建

cmake_minimum_required(VERSION 3.20)
project(vehicle-agent-a2a-iam CXX C)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_C_STANDARD 11)

# 交叉编译工具链 (Yocto SDK)
set(CMAKE_SYSROOT $ENV{OECORE_TARGET_SYSROOT})
set(CMAKE_C_COMPILER  $ENV{CC})
set(CMAKE_CXX_COMPILER $ENV{CXX})

# =====================================================
# 依赖查找
# =====================================================

# gRPC C++ (裁剪构建)
find_package(gRPC CONFIG REQUIRED)
find_package(Protobuf CONFIG REQUIRED)

# mbedTLS
find_package(MbedTLS REQUIRED)

# a2a-cpp SDK (作为子模块或已安装的包)
find_package(a2a-cpp CONFIG REQUIRED)

# TEE Client (系统提供)
find_library(TEEC_LIB teec REQUIRED)

# =====================================================
# TinyRBAC (本地编译)
# =====================================================
add_library(tiny_rbac STATIC
    libs/tiny_rbac/tiny_rbac.c
)
target_include_directories(tiny_rbac PUBLIC libs/tiny_rbac)
target_compile_options(tiny_rbac PRIVATE 
    -Os -fno-exceptions -fno-rtti
)

# =====================================================
# Audit Logger
# =====================================================
add_library(audit_logger STATIC
    libs/audit_logger/audit_logger.c
)
target_link_libraries(audit_logger PUBLIC teec mbedtls)
target_include_directories(audit_logger PUBLIC libs/audit_logger)

# =====================================================
# KMSS TEE Client
# =====================================================
add_library(kmss_tee_client STATIC
    libs/kmss_tee_client/kmss_tee_client.c
)
target_link_libraries(kmss_tee_client PUBLIC teec)

# =====================================================
# IAM Interceptor (C++)
# =====================================================
add_library(iam_interceptor STATIC
    src/iam/iam_authn_interceptor.cpp
    src/iam/iam_authz_interceptor.cpp
    src/iam/iam_interceptor_factory.cpp
)
target_link_libraries(iam_interceptor PUBLIC
    grpc++
    tiny_rbac
    audit_logger
)

# =====================================================
# Agent Binary
# =====================================================
add_executable(vehicle-agent
    src/main.cpp
    src/a2a_iam_server.cpp
    src/agent_card_builder.cpp
    src/skill_handlers.cpp
)
target_link_libraries(vehicle-agent PRIVATE
    a2a-cpp::a2a-cpp
    grpc++
    mbedtls
    iam_interceptor
    kmss_tee_client
)

# =====================================================
# 构建选项 — 嵌入式优化
# =====================================================
target_compile_options(vehicle-agent PRIVATE
    -Os           # 尺寸优化
    -fno-exceptions  # 禁用异常 (可选, 取决于 a2a-cpp)
    -flto         # Link-Time Optimization
    -DNDEBUG      # 禁用 assert
)
target_link_options(vehicle-agent PRIVATE
    -Wl,--strip-all          # 剥离符号
    -Wl,--gc-sections        # 删除未使用的 section
    -Wl,-z,relro -Wl,-z,now  # Full RELRO (安全加固)
)
```

---

## 总结：C/C++ 嵌入式方案核心决策

| 决策 | Cortex-A (Linux) | Cortex-R/M (RTOS) |
|------|-----------------|-------------------|
| **A2A SDK** | a2a-cpp (C++20 社区版) | 手工实现 Light Client + nanopb |
| **RPC 框架** | gRPC C++ (裁剪至 ~8MB) | HTTP/1.1 over lwIP |
| **TLS** | mbedTLS + PSA Crypto + TEE | mbedTLS (60KB 裁剪) + HSM/SHE |
| **策略引擎** | TinyRBAC + OPA WASM (可选) | TinyRBAC only |
| **Protobuf** | protobuf-lite | nanopb (C, ~30KB) |
| **JSON** | nlohmann/json | 手工拼接 (不引入库) |
| **构建系统** | CMake + Yocto SDK | Makefile + IAR/Green Hills |
| **安全性** | TEE (OP-TEE) + mTLS | HSM/SHE + mTLS |
| **Flash 占用** | ~18-25 MB | ~210 KB+ |
| **RAM 占用** | ~30-45 MB | ~90 KB+ |

**关键结论**: 
- **a2a-cpp** 社区 SDK 是可行的起点，需评估稳定性和持续维护
- **mbedTLS** 是最适合车端的 TLS 库 (体积 + 认证 + PSA 集成)
- **TinyRBAC** 可替代 OPA 满足 99% 车端策略需求，OPA WASM 作为补充
- **nanopb** 是 RTOS 方案的 protobuf 基础，Cortex-A 可用完整 protobuf
- 两个架构层次的分工：A 核跑完整的 gRPC + A2A Server，R/M 核跑精简 Client
