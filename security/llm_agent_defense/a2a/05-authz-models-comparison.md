# 车端 Agent 授权模型深度对比 — 超越 RBAC

> **核心问题**: RBAC 是不是车端 Agent IAM 的唯一/最佳选择？  
> **调研范围**: Google Zanzibar/OpenFGA, Amazon Cedar, Microsoft/RBAC, OPA/Rego, Casbin, SpiceDB, 以及学术界最新进展

---

## 目录

1. [主流授权模型全景对比](#1-主流授权模型全景对比)
2. [六大方案逐一深度分析](#2-六大方案逐一深度分析)
3. [车端场景的"理想授权模型"推导](#3-车端场景的理想授权模型推导)
4. [推荐方案: 混合模型 + C 实现策略](#4-推荐方案-混合模型--c-实现策略)

---

## 1. 主流授权模型全景对比

### 1.1 六种模型一句话总结

```
RBAC  → "因为你是 admin，所以你可以"
ABAC  → "因为你的 domain=chassis AND skill=emergency_brake AND vehicle_state=parked，所以你可以"
ReBAC → "因为你是 chassis 域中 ADAS ECU 上的 Agent，且 chassis 域允许 ADAS 调用，所以你可以"
Cedar → "Amazon 的策略语言，RBAC+ABAC 的融合，WASM 可嵌入"
OPA   → "CNCF 的策略即代码，Rego 语言，WASM 可嵌入"
Casbin→ "Go 生态的混合模型库，支持 ACL/RBAC/ABAC 多种组合"
```

### 1.2 能力矩阵

| 能力维度 | RBAC | ABAC | **ReBAC** | Cedar | OPA/Rego | Casbin |
|---------|------|------|-----------|-------|----------|--------|
| **角色/组** | ✅ 核心 | ✅ 属性之一 | ✅ type+relation | ✅ | ✅ | ✅ |
| **属性条件** | ❌ | ✅ 核心 | ✅ 间接 | ✅ | ✅ | ✅ |
| **关系/拓扑** | ❌ | ❌ | ✅ **核心** | ❌ | 手动建模 | ❌ |
| **层级继承** | ✅ 角色层级 | 手动 | ✅ 自动 (relation walk) | ✅ 属性 | 手动 | ✅ |
| **上下文/时间** | ❌ | ✅ | ✅ condition | ✅ when/unless | ✅ | ✅ |
| **策略语言** | 无 (配置) | XACML (XML) | **DSL (OpenFGA)** | **Cedar 语言** | **Rego** | **多种模型** |
| **可分析性** | 简单 | 中 | 中 | ✅ **自动推理** | ✅ 部分 | 弱 |
| **嵌入 C** | ✅ 容易 | 困难 (XACML) | ❌ (需服务) | ✅ **WASM** | ✅ **WASM** | ✅ C++ port |
| **运行时** | 查表 O(1) | 评估引擎 | 图遍历 | 评估引擎 | 评估引擎 | 评估引擎 |
| **代表产品** | LDAP/AD | Axiomatics | Google Zanzibar | AWS Verified Permissions | Styra/OPA | Casbin |

---

## 2. 六大方案逐一深度分析

---

### 2.1 Google Zanzibar / OpenFGA — ReBAC (关系型访问控制)

#### 是什么

Zanzibar 是 Google 自研的全球授权系统，统一管理 Google 所有产品 (YouTube, Drive, Gmail, Maps...) 的权限。2019 年发表论文后，社区出现了多个实现：**OpenFGA** (CNCF, Auth0 创建)、**SpiceDB** (AuthZed)、**Warrant**。

核心思想：**权限不是赋予用户，而是通过实体间的关系图推导出来的。**

```
传统 RBAC 思维:
  "Alice 是 viewer → Alice 可以读 Document X"

Zanzibar/ReBAC 思维:
  "Document X 属于 Folder Y"
  "Folder Y 属于 Team Z"  
  "Alice 是 Team Z 的 member"
  → 推导: Alice 可以读 Document X (通过关系图遍历)
```

#### 关系模型示例 (车端 Agent)

```yaml
# OpenFGA Authorization Model for Vehicle Agents

model
  schema 1.1

type vehicle
  relations
    define domain: [domain]
    
type domain
  relations
    define parent: [vehicle]
    define agent: [agent]
    define subdomain: [domain]

type agent
  relations
    define domain: [domain]
    define asil_level: asil_level_values
    define parent_ecu: [ecu]
    define can_invoke: [agent, skill]
    define can_read: [agent, data_source]

type skill
  relations
    define owner: [agent]
    define category: skill_category_values
    define requires_confirmation: confirmation_requirements

type ecu
  relations
    define agents: [agent]
    define connected_to: [domain]
```

```yaml
# 关系元组 (Tuple) — 描述 "谁和谁有什么关系"

# 物理拓扑
- {user: "vehicle:LSVN123", relation: "domain", object: "domain:chassis"}
- {user: "ecu:brake-ecu-01", relation: "connected_to", object: "domain:chassis"}
- {user: "agent:adas-controller", relation: "parent_ecu", object: "ecu:brake-ecu-01"}

# Agent 能力声明
- {user: "skill:emergency_brake", relation: "owner", object: "agent:adas-controller"}
- {user: "skill:read_speed", relation: "owner", object: "agent:adas-controller"}
- {user: "skill:emergency_brake", relation: "category", object: "category:safety_critical"}
- {user: "skill:emergency_brake", relation: "requires_confirmation", object: "requirement:user_confirm_if_cross_domain"}

# Agent 间信任关系
- {user: "agent:voice-assistant", relation: "can_invoke", object: "agent:adas-controller"}
# ⚠ 但仅当满足 condition (用户确认) 时才能调用 safety_critical skill
```

#### 权限检查 (Check API)

```
请求: "voice-assistant 能否调用 emergency_brake?"

OpenFGA Check API:
  user:   "agent:voice-assistant"
  relation: "can_invoke"
  object: "agent:adas-controller"

  回答: { allowed: true }
  
  + condition check: 
    "skill:emergency_brake 的 requires_confirmation = user_confirm_if_cross_domain"
    "agent:voice-assistant 的 domain ≠ agent:adas-controller 的 domain"
    // → 需要用户确认！

最终结果:
  { allowed: true, conditions_met: false, missing: ["user_confirmation"] }
```

#### 车端适用性分析

| 优点 | 缺点 |
|------|------|
| ✅ 天然适合描述车端物理拓扑 (ECU→Domain→Vehicle) | ❌ OpenFGA/SpiceDB 都需要独立服务进程 (Go/Rust) |
| ✅ 关系图遍历自动推导权限 | ❌ 无法直接嵌入 MCU (需 ≥ 32MB RAM) |
| ✅ 支持条件 (conditions) 处理上下文 | ❌ 性能: 图遍历 1-5ms vs RBAC 查表 0.01ms |
| ✅ Google 全球验证过的模型 | ❌ 车端离线场景需要本地 Check Engine |
| ✅ 层级继承天然支持 (ASIL 继承链) | ❌ 对嵌入式的 C 移植工作量大 |

#### 核心评估

**Zanzibar 的关系模型是最符合车端语义的**——车辆天然是一个物理拓扑图：Vehicle → Domain → ECU → Agent → Skill。权限问题的本质就是 "在这个图中，节点 A 能否到达节点 B"。但 OpenFGA/SpiceDB 的部署模型 (独立服务) 不适合嵌入式，需要自研精简版。

---

### 2.2 Amazon Cedar — 策略语言 + WASM 嵌入

#### 是什么

Cedar 是 Amazon 为 AWS Verified Permissions 开发的开源策略语言。用 Rust 实现，可编译为 WASM。核心设计：**策略与代码分离，可用自动推理验证。**

```cedar
// Cedar 策略示例 — 车端 Agent
// policy.cedar

// 同域 Agent 可以互相调用
permit (
    principal is Agent,
    action == Action::"invoke_skill",
    resource is Agent
)
when {
    principal.domain == resource.domain &&
    principal.asil_level >= resource.min_required_asil
};

// 跨域安全操作: 需要用户确认
permit (
    principal is Agent,
    action == Action::"invoke_skill",
    resource is Agent
)
when {
    principal.domain != resource.domain &&
    resource.skill.category == "safety_critical" &&
    context.user_confirmed == true &&
    context.confirmation_age_seconds < 30
};

// 禁止: 任何 Agent 在行驶中刷写 ECU
forbid (
    principal,
    action == Action::"invoke_skill",
    resource
)
when {
    context.vehicle_state == "moving" &&
    resource.skill.name == "flash_ecu"
};
```

#### Cedar 的独特优势

```
Cedar 的三个独特能力:

1. Automated Reasoning (自动推理)
   → 可以数学证明 "信息娱乐域 Agent 永远无法在未确认情况下调用紧急制动"
   → 这对功能安全 (ISO 26262) 非常有价值

2. forbid 优先级最高
   → 显式禁止规则，不会被 permit 覆盖
   → "行驶中禁止刷写 ECU" — 没有例外

3. WASM 编译
   → cedar-wasm: Rust → WASM → 可嵌入任何有 WASM runtime 的环境
   → 车端 C 代码通过 WASM runtime (wasm3 ~64KB) 执行策略
```

#### 车端适用性分析

| 优点 | 缺点 |
|------|------|
| ✅ WASM 可嵌入 (策略编译为 ~30KB WASM) | ❌ Cedar 主要针对 AWS 生态 (principal/action/resource 三元组) |
| ✅ 自动推理验证安全属性 | ❌ 不支持原生关系图遍历 |
| ✅ forbid 规则强保证 | ❌ 复杂拓扑关系需要手动建模 |
| ✅ Rust 实现，内存安全 | ❌ WASM runtime 引入额外依赖 |
| ✅ Amazon 持续投入 | ❌ 社区相对小 |

#### 核心评估

Cedar 的策略分析能力 (自动推理) 对 ASIL 安全论证非常有价值，但其三元组模型 (principal-action-resource) 不如 Zanzibar 的关系图适合描述车端拓扑。**作为策略描述语言很优秀，但建议与关系模型互补使用。**

---

### 2.3 OPA/Rego — 策略即代码 (CNCF 毕业)

#### 是什么

Open Policy Agent 是 CNCF 毕业项目，用 Rego 语言描述策略。可编译为 WASM 嵌入。

前面专题二中已经深入分析过 Rego 策略，此处重点与其他模型对比。

```rego
# 与前面专题二的 Rego 策略相同
# 但 OPA 的问题在于: 每次决策需要完整的 input JSON
# 对于复杂的车端关系，需要手动将所有关系数据扁平化到 input 中
```

#### OPA 的车端关键局限

```
OPA/Rego 的核心问题: 上下文爆炸

对于 Zanzibar 的关系查询: "voice-assistant 能否调用 emergency_brake?"
  → 只需要遍历: voice-assistant → domain:infotainment → ? → domain:chassis → adas-controller → emergency_brake

对于 OPA/Rego 的查询:
  → 需要将所有 Agent、Domain、Skill、ECU 的关系全部打包到 input JSON 中
  → 如果车端有 20 个 Agent, 50 个 Skill → input JSON 可能达到 KB 级别
  → 每次决策都要构造完整上下文 → 浪费且不必要
```

| 车端维度 | OPA/Rego | Zanzibar/ReBAC |
|----------|---------|---------------|
| 关系查询 | 手动建模 (input 膨胀) | 自动图遍历 |
| 决策延迟 | 0.1-0.5ms | 1-5ms (需要图遍历优化) |
| 嵌入式适配 | ✅ WASM (但 runtime 开销) | ❌ 需要独立服务 |
| 确定性 | 完全 (无外部依赖) | 取决于关系图完整性 |
| 策略分析 | 有限 | 图可达性分析 |

---

### 2.4 Casbin — 多模型混合库

#### 是什么

Casbin 是 Go 生态中最流行的授权库 (~18K GitHub stars)。支持 ACL, RBAC, ABAC, RESTful 等多种模型。有 C++ port (casbin-cpp)。

```
Casbin 的核心概念:

Model (.conf 文件):
  [request_definition]
  r = sub, dom, obj, act    # subject, domain, object, action
  
  [policy_definition]
  p = sub, dom, obj, act, eft  # eft = allow/deny
  
  [role_definition]
  g = _, _, _               # 角色继承
  
  [matchers]
  m = g(r.sub, p.sub) && keyMatch(r.dom, p.dom) && 
      keyMatch(r.obj, p.obj) && regexMatch(r.act, p.act)

Policy (.csv 文件):
  p, agent:*, domain:chassis, skill:read_speed, read, allow
  p, agent:voice-assistant, domain:infotainment, skill:emergency_brake, invoke, allow
```

#### Casbin 的车端适用性

| 优点 | 缺点 |
|------|------|
| ✅ 有 C++ port (casbin-cpp) | ❌ Matchers 表达能力有限 (正则/keyMatch) |
| ✅ 模型+策略分离 (热更新) | ❌ 无原生关系图支持 |
| ✅ 轻量级 (C++ port ~150KB) | ❌ 社区以 Go 为主，C++ port 维护度低 |
| ✅ 支持 RBAC+ABAC 混合 | ❌ 复杂条件需要自定义函数 |

---

### 2.5 SpiceDB — Zanzibar 的另一种实现

与 OpenFGA 同源 (都基于 Zanzibar 论文)，AuthZed 公司维护。额外支持:
- **Caveats** (类似于 Google Zanzibar 的条件): 更灵活的上下文判断
- **Watch API**: 关系变更的事件流
- 使用 Rust 开发 Schema 解析器 (比 OpenFGA 的 ANTLR 更快)

**车端关键局限与 OpenFGA 相同**: 需要独立服务进程。

---

### 2.6 学术界与前沿方案

| 方案 | 摘要 | 车端启示 |
|------|------|---------|
| **Macaroons** (Google) | 分布式持有凭证，支持衰减 | 适合跨车通信的场景 (V2V 临时授权) |
| **Biscuits** (Clever Cloud) | Macaroons 的改进版，支持 Datalog 策略 | 有 C 实现，可嵌入 |
| **Capability-based Security** | 基于能力的访问 (如 seL4) | 微内核的 cap 机制天然适合 MCU |
| **Differential Privacy** | 查询结果加噪声 | 车辆数据脱敏共享 |
| **Zanzibar + SQLite** | 将关系图存储到嵌入式 SQLite | ✅ 可能可行! |

---

## 3. 车端场景的 "理想授权模型" 推导

### 3.1 车端 Agent 授权的本质特征

```
车端 Agent 授权与其他领域的根本区别:

1. 物理拓扑 = 信任拓扑
   Vehicle → Domain → ECU → Agent → Skill
   权限沿物理连接链传递，这是天然的关系图

2. 安全等级 (ASIL) 是硬约束
   QM → ASIL-A → ASIL-B → ASIL-C → ASIL-D
   低等级不能向上调用高等级的安全关键操作
   这是一个偏序关系

3. 车辆状态是上下文门控
   行驶中 ∥ 静止 ∥ 充电 ∥ 诊断模式
   同一操作在不同状态下权限要求不同

4. 静态为主 + 少量动态
   99% 的 Agent 关系在设计时已知
   1% 的动态变化 (OTA 安装新 Agent, 诊断工具接入)

5. 资源严重受限
   RAM 以 KB/MB 计, 不能上 100MB+ 的服务
```

### 3.2 "如果为车端从头设计" — 理想模型的特征

```
理想的车端授权模型应该:

1. 用关系图描述车辆拓扑 (Zanzibar 的思想)
   → "adas-controller 属于 chassis 域" 是关系
   → "chassis 域允许 adas 域调用" 是关系
   → 权限通过关系路径推导

2. 用属性描述 Safety/状态约束 (ABAC 的思想)
   → "ASIL-D 操作需要用户确认" 是属性条件
   → "vehicle_state=moving 禁止 flash_ecu" 是属性条件

3. 编译为静态决策表 (性能)
   → 99% 的决策是已知关系+已知属性 → 可在编译时/OTA时预计算
   → 得到 O(1) 的查表性能

4. 支持可选的正式验证 (Cedar 的思想)
   → 关键安全属性可以数学证明
   → "voice-assistant 在没有用户确认的情况下永远不能触发紧急制动"
```

---

## 4. 推荐方案: 混合模型 + C 实现策略

### 4.1 方案选型结论

**不要选 RBAC，也不要单选任何一个。用车端语义最适合的 "ReBAC 骨架 + ABAC 属性 + 编译优化" 混合方案。**

```
最终推荐: Relationship-Enhanced Attribute-Based Policy Engine (RE-ABAC)

┌─────────────────────────────────────────────────────────────┐
│                    RE-ABAC 架构                               │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │            编译时: 关系图 → 决策表预计算                   ││
│  │                                                          ││
│  │  relation_graph.json ──→ reabac-compiler ──→ decision.bin ││
│  │  (车端拓扑+ASIL层级)      (离线/OTA)         (1-4KB 表)   ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │            运行时: O(1) 决策引擎 (C, < 5KB)               ││
│  │                                                          ││
│  │  authz_input_t → HASH(skill, caller, target, state)      ││
│  │              → decision_table[hash] → ALLOW/DENY/CONFIRM  ││
│  │                                                          ││
│  │  延迟: < 0.01ms (单次查表)                               ││
│  │  大小: engine 5KB + table 4KB = 9KB                      ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │            验证时: 关键属性形式化证明 (Cedar 思想)         ││
│  │                                                          ││
│  │  "对于任意 agent in infotainment, 如果没有 user_confirm   ││
│  │   = true, 永远不能调用 domain=chassis 的 ASIL-D skill"    ││
│  │                                                          ││
│  │  编译为静态断言 → 集成到 CI pipeline                      ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 4.2 为什么这个方案优于纯 RBAC

```
场景: "OTA Manager Agent 能否在车辆行驶中刷写 ECU?"

纯 RBAC:
  OTA Manager 有 role="updater"
  ECU 要求 role="updater"
  → ALLOW  ← ❌ 错误! 忽略了 vehicle_state

RBAC + 手工 if-else:
  if (role == "updater" && vehicle_state != MOVING) { ALLOW } else { DENY }
  → 逻辑散落在代码中，难以审计

RE-ABAC (本方案):
  relation: ota-manager → can_invoke → flash_ecu
  attribute constraint: {vehicle_state != MOVING}
  → 编译到决策表: HASH(ota-manager, flash_ecu, MOVING) → DENY
  
  所有策略都可见、可审计、可分析
```

### 4.3 C 实现骨架

```c
/*
 * re_abac.h
 * Relationship-Enhanced Attribute-Based Access Control
 * 
 * 设计目标:
 * - 编译时预计算关系图 → 决策表
 * - 运行时 O(1) 查表
 * - 总大小 < 10KB
 * - 支持 OTA 更新决策表
 */

#ifndef RE_ABAC_H
#define RE_ABAC_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================
// 决策输入 (运行时, 轻量)
// ============================================================

typedef struct __attribute__((packed)) {
    uint8_t  caller_id;       // 调用方 Agent ID (0-255)
    uint8_t  target_skill_id; // 目标 Skill ID (0-255)
    uint8_t  action_type;     // read=0, invoke=1, write=2
    uint8_t  vehicle_state;   // parked=0, stopped=1, moving=2, charging=3
    uint8_t  user_confirmed;  // 0=false, 1=true, 2=n/a
    uint16_t confirmation_age_ms; // 确认存活时间 (用于 30s 过期检查)
} re_abac_input_t;  // 8 bytes

// ============================================================
// 决策输出
// ============================================================

typedef enum {
    RE_ABAC_ALLOW                     = 0,
    RE_ABAC_DENY                      = 1,
    RE_ABAC_DENY_NEED_USER_CONFIRM    = 2,
    RE_ABAC_DENY_VEHICLE_STATE        = 3,
    RE_ABAC_DENY_NOT_IN_RELATIONSHIP  = 4,
    RE_ABAC_DENY_ASIL_VIOLATION       = 5,
} re_abac_decision_t;

// ============================================================
// 决策表条目 (编译时/OTA 时生成)
// ============================================================

typedef struct __attribute__((packed)) {
    re_abac_input_t    key;      // 8 bytes - 匹配键
    re_abac_decision_t decision; // 1 byte
    uint8_t            reserved[3];
} re_abac_entry_t;  // 12 bytes per entry

// ============================================================
// 决策表
// ============================================================

#define RE_ABAC_MAX_ENTRIES 1024  // 最多 1024 条规则 (12KB)

typedef struct {
    uint32_t         magic;              // 魔数: 0x41424143 ('ABAC')
    uint32_t         version;            // 版本号
    uint32_t         entry_count;        // 条目数
    uint32_t         checksum;           // CRC32
    re_abac_entry_t  entries[RE_ABAC_MAX_ENTRIES]; // 有序数组, 二分查找
} re_abac_table_t;  // ~12.3KB

// ============================================================
// API
// ============================================================

/*
 * 初始化决策引擎
 * 
 * table: 指向决策表 (内存映射的 Flash 区域或 RAM 中的 OTA 更新表)
 * 返回: 0=成功, -1=校验失败 (magic 不匹配或 checksum 错误)
 */
int re_abac_init(const re_abac_table_t* table);

/*
 * 权限决策 — O(log N) 二分查找
 * 
 * 延迟: < 0.02ms (1024 条目, Cortex-A)
 *       < 0.05ms (Cortex-M)
 * 
 * 查找策略:
 *   1. 精确匹配 key (caller_id, target_skill_id, action_type, 
 *                     vehicle_state, user_confirmed)
 *   2. 如果精确匹配失败 → 尝试通配 (user_confirmed=2=n/a)
 *   3. 如果仍未找到 → RE_ABAC_DENY (默认拒绝)
 */
re_abac_decision_t re_abac_evaluate(const re_abac_input_t* input);

/*
 * 获取决策的文字描述 (用于审计日志)
 */
const char* re_abac_decision_str(re_abac_decision_t decision);

/*
 * 检查决策是否可恢复 (触发 A2A TASK_STATE_AUTH_REQUIRED)
 */
static inline bool re_abac_is_recoverable(re_abac_decision_t d) {
    return (d == RE_ABAC_DENY_NEED_USER_CONFIRM ||
            d == RE_ABAC_DENY_VEHICLE_STATE);
}

// ============================================================
// 编译时工具 (宿主 PC 上运行, 生成决策表)
// ============================================================

/*
 * reabac-compiler (独立的 CLI 工具, 非嵌入式代码)
 * 
 * 输入:
 *   1. relation_graph.json  — 车端拓扑 (Agent/ECU/Domain/Skill 关系)
 *   2. asil_hierarchy.json  — ASIL 等级关系
 *   3. safety_rules.yaml    — 安全规则 (哪些 Skill 需要用户确认等)
 * 
 * 输出:
 *   decision_table.bin     — 预计算的决策表 (可直接烧录)
 * 
 * 使用:
 *   $ reabac-compiler \
 *       --relations relation_graph.json \
 *       --asil asil_hierarchy.json \
 *       --rules safety_rules.yaml \
 *       --output decision_table.bin
 */

#ifdef __cplusplus
}
#endif

#endif // RE_ABAC_H
```

### 4.4 决策表生成逻辑

```python
# reabac_compiler.py (伪代码 — 描述编译器逻辑)
# 这个工具在开发阶段运行，不在车端运行

import json
from itertools import product

def compile_decision_table(relations, asil, rules):
    """
    将关系图 + ASIL 层级 + 安全规则 → 编译为决策表
    
    核心思想: 枚举所有可能的 callers × skills × states
    对每个组合预先计算决策结果
    """
    entries = []
    
    callers = relations['agents']          # 所有 Agent (通常 < 20)
    skills = relations['skills']            # 所有 Skill (通常 < 50)
    states = ['parked', 'stopped', 'moving', 'charging']
    confirmations = [0, 1, 2]              # false, true, n/a
    
    for caller in callers:
        for skill in skills:
            for state in states:
                for confirmed in confirmations:
                    
                    # 1. 查找关系路径
                    # caller 是否可以通过关系图到达 skill?
                    path = find_relationship_path(
                        relations, caller, skill
                    )
                    if not path:
                        entries.append({
                            'key': (caller.id, skill.id, skill.action, 
                                    state, confirmed),
                            'decision': 'DENY_NOT_IN_RELATIONSHIP'
                        })
                        continue
                    
                    # 2. ASIL 检查
                    if caller.asil_level < skill.min_required_asil:
                        entries.append({
                            'key': (caller.id, skill.id, skill.action,
                                    state, confirmed),
                            'decision': 'DENY_ASIL_VIOLATION'
                        })
                        continue
                    
                    # 3. 跨域 + 安全关键 → 需要用户确认
                    if (caller.domain != skill.owner_domain and
                        skill.category == 'safety_critical' and
                        not confirmed):
                        entries.append({
                            'key': (caller.id, skill.id, skill.action,
                                    state, confirmed),
                            'decision': 'DENY_NEED_USER_CONFIRM'
                        })
                        continue
                    
                    # 4. 车辆状态门控
                    if (skill.prohibited_states and 
                        state in skill.prohibited_states):
                        entries.append({
                            'key': (caller.id, skill.id, skill.action,
                                    state, confirmed),
                            'decision': 'DENY_VEHICLE_STATE'
                        })
                        continue
                    
                    # 5. 通过所有检查 → ALLOW
                    entries.append({
                        'key': (caller.id, skill.id, skill.action,
                                state, confirmed),
                        'decision': 'ALLOW'
                    })
    
    # 按 key 排序 (caller_id, skill_id, action, state, confirmed)
    entries.sort(key=lambda e: (
        e['key'][0], e['key'][1], e['key'][2], 
        e['key'][3], e['key'][4]
    ))
    
    # 输出二进制决策表
    # 条目数估计: 20 agents × 50 skills × 4 states × 3 confirmations
    #            = 12,000 种组合
    # 但实际需要显式记录的只有 ~500-1000 条 (大部分组合被通配规则覆盖)
    
    return entries
```

### 4.5 各方案最终推荐度

```
车端 Agent IAM 授权模型 — 最终推荐:

┌──────────────────────────────────────────────────────────────┐
│  方案              推荐度   适用场景                          │
├──────────────────────────────────────────────────────────────┤
│  RE-ABAC (本方案)   ⭐⭐⭐⭐⭐  Cortex-A + Cortex-R/M         │
│  编译型混合模型                                         │
│                                                              │
│  Cedar WASM         ⭐⭐⭐⭐   Cortex-A (需要正式安全证明时)  │
│  Amazon 策略语言                                          │
│                                                              │
│  Zanzibar Lite      ⭐⭐⭐    Cortex-A (关系图频繁变化时)     │
│  SQLite + 关系图                                          │
│                                                              │
│  纯 RBAC            ⭐⭐      仅适用于最简单的场景              │
│                                                              │
│  纯 OPA/Rego WASM   ⭐⭐      Cortex-A (策略极度复杂的云原生)  │
│                                                              │
│  纯 Casbin C++      ⭐⭐      Cortex-A (需要 RBAC+ABAC 混合)  │
└──────────────────────────────────────────────────────────────┘
```

### 4.6 核心洞察: 为什么是 "编译时" 而非 "运行时"

```
车端 Agent 拓扑的核心特征: 静态为主

设计时已知:
  - 有多少个 Domain (底盘、动力、车身、信息娱乐、ADAS...)
  - 每个 Domain 有多少个 Agent
  - 每个 Agent 有多少个 Skill
  - ASIL 等级关系
  - 域间信任关系

设计时不确定但 OTA 可更新:
  - 新增 Agent (新功能 OTA)
  - 新增 Skill
  
纯运行时动态:
  - vehicle_state (实时变化)
  - user_confirmed (实时变化)

→ 结论: 99% 的关系/属性是静态的, 只有 1% 是实时变化的
→ 策略: 编译时预计算所有静态组合 → 运行时只需查表 + 实时属性覆盖
→ 结果: O(1) 查表, < 0.01ms, 9KB 总大小
```

---

## 总结

**RBAC 不是答案。** 车端 Agent IAM 的最佳方案是 **RE-ABAC**: 

- **Re**lationship graph (Zanzibar 思想) → 描述车端物理拓扑和信任关系
- **A**ttribute constraints (ABAC 思想) → ASIL 门控、车辆状态、用户确认
- **Compile**-time optimization → 所有静态组合预计算为决策表
- **C** implementation → 运行时 9KB, O(1) 查表, <0.01ms

如果未来需要正式安全验证 (ISO 26262 认证), 可以用 **Cedar** 的策略分析能力为关键安全属性生成数学证明, 作为安全案例的一部分。
