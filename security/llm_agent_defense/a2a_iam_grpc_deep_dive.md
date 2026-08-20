# A2A 场景 IAM 深度分析与 gRPC 扩展演进

> 本文档是 [`a2a_iam_integration_arch.md`](./a2a_iam_integration_arch.md) 的**深度篇**。
> 前置内容覆盖了架构蓝图；本篇重点处理：
> 1. **IAM 在 A2A 场景的深层设计问题**（边界情况、信任模型、性能临界点）
> 2. **基于定制 gRPC 扩展的演进路径**（从 raw metadata → proto binary → CallCredentials → 原生 A2A 流协议 → Service Mesh）

---

## 目录

- [Part I: IAM 深度分析](#part-i-iam-深度分析)
  - [1. 多跳链路的时间依赖问题](#1-多跳链路的时间依赖问题)
  - [2. input-required 与 Grace Period 的不匹配](#2-input-required-与-grace-period-的不匹配)
  - [3. 并发多 Skill 调用的 Token 竞争](#3-并发多-skill-调用的-token-竞争)
  - [4. AgentCard 版本漂移问题](#4-agentcard-版本漂移问题)
  - [5. 跨域 Trust Bundle OTA 与验签窗口期](#5-跨域-trust-bundle-ota-与验签窗口期)
  - [6. Scope 膨胀攻击（AgentCard 空 scope 问题）](#6-scope-膨胀攻击agentcard-空-scope-问题)
  - [7. 多跳撤销传播延迟](#7-多跳撤销传播延迟)
  - [8. IAM 在 A2A 场景的延迟临界点分析](#8-iam-在-a2a-场景的延迟临界点分析)
- [Part II: gRPC 扩展演进路径](#part-ii-grpc-扩展演进路径)
  - [9. 演进总览](#9-演进总览)
  - [10. Phase 0 → Phase 1: Binary Proto 元数据](#10-phase-0--phase-1-binary-proto-元数据)
  - [11. Phase 2: gRPC CallCredentials 集成](#11-phase-2-grpc-callcredentials-集成)
  - [12. Phase 3: 拦截器链分层](#12-phase-3-拦截器链分层)
  - [13. Phase 4: 原生 A2A 流协议](#13-phase-4-原生-a2a-流协议)
  - [14. Phase 5: Service Mesh / xDS 卸载](#14-phase-5-service-mesh--xds-卸载)
  - [15. 定制 gRPC 扩展机制汇总](#15-定制-grpc-扩展机制汇总)
- [16. 修订记录](#16-修订记录)

---

# Part I: IAM 深度分析

## 1. 多跳链路的时间依赖问题

### 1.1 问题根因

多跳链路 CD → AD → VD 中，**每一层的 TTL 必须 ≤ 上一层的剩余 TTL**（不变量），
但这引入了一个隐蔽的**时间依赖图**：

```
时间轴：

T=0      CD 创建：A2A Delegation (TTL=600s, expires T=600)
T=30     AD 收到，sub-delegate VD：Delegation (TTL=300s, expires T=330)
T=300    VD 收到（假设启动慢），Delegation 只剩 30s！

                  ┌─── CD Delegation ───────────────────────┐  expires T=600
                      ┌─── AD→VD Delegation ──────┐           expires T=330
                              ┌── VD 实际可工作窗口 ──┐
                              T=300             T=330
                                    ↑ 只有 30s !
```

**根因**：多跳中每跳的 `sub_delegate` 使用了**剩余 TTL 的某个固定比例**，
如果中间节点处理耗时或子任务启动慢，末端节点得到的有效窗口可能极短。

### 1.2 解决方案：最小有效窗口保证

```c
// kmss_sub_delegate_a2a() 内部增加 min_effective_ttl 校验

// 签发前检查：给定的 ttl 必须 ≥ 本 skill 的 MIN_EFFECTIVE_TTL
static const uint32_t SKILL_MIN_EFFECTIVE_TTL[] = {
    /* route-plan    */ 60,   // 最少 1 分钟，否则连路径计算都来不及
    /* obj-detection */ 5,
    /* ota-download  */ 300,  // OTA 至少 5 分钟
    /* brake-control */ 3,
};

kmss_token_t* kmss_sub_delegate_a2a(
    kmss_token_t* parent, kmss_svid_t* delegator,
    const char* next_target, const char** scopes, size_t n,
    uint32_t ttl_seconds
) {
    uint32_t parent_remaining = parent->exp - secure_rtc_now();
    uint32_t effective_ttl = MIN(ttl_seconds, parent_remaining);

    // 保证最小有效窗口
    const char* skill_id = parent->claims.a2a_skill_id;
    uint32_t min_ttl = skill_min_effective_ttl(skill_id);
    if (effective_ttl < min_ttl) {
        // 不拒绝，而是自动延伸到 min_ttl（不超过 parent 剩余）
        effective_ttl = MIN(min_ttl, parent_remaining);
        if (effective_ttl < min_ttl) {
            // parent 真的不够 → 拒绝并告知 caller
            return NULL;  // ERR_PARENT_TTL_INSUFFICIENT
        }
    }
    // ...
}
```

### 1.3 "超时对齐"协议

引入 **Task TTL Negotiation**：
在 `SendTask` 请求中，client 附带 `x-a2a-min-ttl` header，
server 检查自身 delegation 剩余 TTL 是否满足，不满足则返回 `RESOURCE_EXHAUSTED`，
client 可以重新申请 delegation 后重试。

```proto
// A2A gRPC 扩展 metadata（Phase 1 后）
message A2ATaskHints {
  uint32 min_effective_ttl_s = 1;  // client 要求 server 至少保证的 TTL
  uint32 estimated_duration_s = 2; // client 估计任务时长
}
```

---

## 2. input-required 与 Grace Period 的不匹配

### 2.1 问题场景

```
T=0     CD Agent 提交任务给 AD（Lease TTL=300s, grace=15s）
T=200   AD Agent 完成规划，但需要用户确认（→ input-required 状态）
T=215   grace_ms(15s) 到，KMSS 认为心跳超时 → 自动 revoke lease！
T=220   用户才看到确认对话框，点击确认
         但 lease 已被 revoke → 任务失败
```

**问题根因**：Lease 的 grace period（30s）是为**网络抖动/KMSS 重启**设计的；
`input-required` 是**业务等待**，两者性质完全不同，不能用同一套超时参数。

### 2.2 解决方案：状态感知的心跳策略

#### 2.2.1 两类超时分离

```c
typedef struct {
    uint32_t heartbeat_ms;           // 正常工作状态的心跳间隔（30s）
    uint32_t grace_ms;               // 网络故障的宽限窗口（15s）

    // 新增：input-required 状态专用
    uint32_t input_required_ttl_s;   // 用户等待最大时长（默认 300s = 5min）
    uint32_t input_required_grace_s; // 宽限（30s，防止用户点击时恰好过期）
} kmss_lease_policy_t;
```

#### 2.2.2 KMSS Lease 状态感知

```c
// Task 进入 input-required 时，A2A SDK 通知 KMSS 切换心跳模式
int kmss_lease_set_input_required(
    kmss_lease_t* lease,
    uint32_t      timeout_s   // 等待用户输入的最大时长
);

// KMSS 内部行为：
// • 暂停正常心跳计时器
// • 启动 input_required 计时器（超时后标记 task 为 failed）
// • 保持 lease 有效（不触发 grace 逻辑）

// 用户输入完成后：
int kmss_lease_resume_working(kmss_lease_t* lease);
// • 重启正常心跳
// • 清除 input_required 计时器
```

#### 2.2.3 审计事件扩展

```c
AUDIT_LEASE_INPUT_REQUIRED_ENTER,   // 进入等待用户输入
AUDIT_LEASE_INPUT_REQUIRED_TIMEOUT, // 用户没有在时限内回应
AUDIT_LEASE_INPUT_REQUIRED_RESUME,  // 用户回应，恢复工作
```

---

## 3. 并发多 Skill 调用的 Token 竞争

### 3.1 问题场景

```
同一个 CD Session，并发发起两个 A2A Task：
  Task A: CD → AD  skill=route-plan  (需要 L3A Lease #1)
  Task B: CD → AD  skill=obj-detect  (需要 L3A Lease #2)

并发申请的问题：
  1. KMSS rate limit: 2 req/min for lease_acquire
     → 并发申请可能触发限流
  2. CD 的 Session Token (L2) 作为两个 Lease 的父 token
     → Session TTL 剩余可能不足以支撑两个长任务
  3. 两个 Lease 的心跳周期对齐：如果都在同一时刻心跳
     → KMSS 签名 QPS 峰值翻倍
```

### 3.2 解决方案

#### 3.2.1 Token 预热池（Token Pre-warming）

```c
// SDK 在 Session 建立后，预热一个 delegation token pool
// 每个 skill type 预缓存 1~2 个待命 token
typedef struct {
    char          skill_id[64];
    kmss_token_t* tokens[4];   // 最多预热 4 个
    uint8_t       n_ready;
    uint8_t       n_max;
} skill_token_pool_t;

// 申请时先从 pool 取；pool 低水位时后台补充
kmss_token_t* sdk_get_a2a_delegation_from_pool(const char* skill_id) {
    skill_token_pool_t* pool = find_pool(skill_id);
    if (pool->n_ready > 0) {
        return pool->tokens[--pool->n_ready];  // 从 pool 取
    }
    // pool 空：同步申请 + 后台补充
    return kmss_issue_a2a_delegation_sync(...);
}
```

#### 3.2.2 心跳错峰（Jitter）

```c
// 计算心跳间隔时引入随机抖动，避免多 lease 同时心跳
uint32_t heartbeat_jitter_ms(uint32_t base_ms, const char* lease_jti) {
    // 基于 jti hash 的伪随机 jitter：±20%
    uint32_t h = fnv32(lease_jti);
    int32_t  jitter = (int32_t)(h % (base_ms / 5)) - (base_ms / 10);
    return (uint32_t)MAX(1000, (int32_t)base_ms + jitter);
}
```

#### 3.2.3 并发 Lease 数量限制与优先级

```c
// 同一 workload 的并发 active lease 上限（来自 §20 限流）
// 超出时：低优先级 lease 进入等待队列
typedef enum {
    LEASE_PRIORITY_SAFETY    = 0,  // ASIL-D skill（不受并发限制）
    LEASE_PRIORITY_NORMAL    = 1,  // 正常业务
    LEASE_PRIORITY_BACKGROUND = 2,  // 后台任务（降级执行）
} lease_priority_t;
```

---

## 4. AgentCard 版本漂移问题

### 4.1 问题

AgentCard 在 Agent 启动时签名注册（TTL = SVID TTL = 1h）。
但如果 Agent 的能力在运行时发生变化（如 OTA 更新了 skill 列表），
AgentCard 与实际能力不匹配：

```
T=0    Agent 注册：AgentCard {skills: [route-plan, obj-detect]}
T=30min  OTA 更新：新增 skill = traffic-predict
         但 AgentCard 尚未过期（还有 30min）
T=31min  CD Agent 查询注册表，找不到 traffic-predict skill → 无法调用新能力
         OR
         CD Agent 旧 AgentCard 缓存：发送 traffic-predict 任务
         → AD Sidecar: skill_id ∉ published_skills → PERMISSION_DENIED
```

### 4.2 解决方案：主动刷新协议

#### 4.2.1 AgentCard Refresh API

```c
// SDK 提供增量 AgentCard 更新（只重签变更的字段）
int kmss_refresh_agentcard(
    kmss_svid_t*         svid,
    const uint8_t*       new_card_json, size_t len,
    kmss_agentcard_sig_t* old_sig,      // 旧签名（用于连续性验证）
    kmss_agentcard_sig_t* out_new_sig
);

// 注册表支持 in-place 更新（不走重新注册流程）
int registry_update_card(
    const char*           agent_id,
    const uint8_t*        new_card_json, size_t len,
    kmss_agentcard_sig_t* new_sig,
    kmss_svid_t*          svid          // 身份验证
);
```

#### 4.2.2 Push 通知 vs 拉取

```
方案 A（Push）：
  注册表 → 订阅者广播 AgentCard 更新事件
  订阅方主动刷新本地缓存
  实时性好，但增加注册表复杂度

方案 B（Pull with short TTL）：
  AgentCard 注册 TTL 从 1h 缩短到 5min
  客户端每次调用前先 lookup（命中本地缓存则不走网络）
  实时性稍差，但实现简单

车端推荐：方案 B（5min TTL）
  理由：车端 OTA 通常不是分钟级；5min 足够；避免 Push 广播的可靠性问题
```

---

## 5. 跨域 Trust Bundle OTA 与验签窗口期

### 5.1 问题

CD Sidecar 验证 AD delegation token 时，依赖 `ad.pb`（AD 的 trust bundle）。
当 AD 域做 L1 证书 OTA 轮换时：

```
时间轴（AD L1 Key Rotation）：

T=0     AD 推送新 trust bundle（含 L1_new + L1_old）到所有 Sidecar
T=1s    CD Sidecar 收到新 bundle，开始 reload（inotify 触发）
T=2s    AD KMSS 开始用 L1_new 签发新 SVID
T=1.5s  CD 正在处理一个 AD delegation token（用 L1_old 签的）
         → CD Sidecar reload 完成，尝试验签
         → 新 bundle 里有 L1_new 和 L1_old（overlap 期）
         → 验签应该通过（L1_old 仍在 bundle 中）

但是：如果 OTA 实现有 bug，bundle reload 时清除了 L1_old
         → 正在处理中的请求用 L1_old 验签失败 → 误拒绝
```

### 5.2 解决方案：Bundle Reload 的原子性保证

```c
// Sidecar bundle reload 必须是原子的：
// 1. 新 bundle 加载到 shadow slot
// 2. 验证 shadow bundle 完整性（签名 + L1 overlap 检查）
// 3. 原子切换 active slot（CAS 操作，无锁）
// 4. 正在进行的验签操作持有 old bundle 的引用计数，完成后释放

typedef struct {
    trust_bundle_t* active;        // 当前活跃 bundle（指针）
    trust_bundle_t* bundles[2];    // 双 buffer
    _Atomic uint8_t active_idx;    // 0 或 1，原子切换
    _Atomic int32_t refs[2];       // 引用计数
} bundle_swap_ctx_t;

// 验签前获取 bundle 引用
trust_bundle_t* bundle_acquire(bundle_swap_ctx_t* ctx) {
    uint8_t idx = atomic_load(&ctx->active_idx);
    atomic_fetch_add(&ctx->refs[idx], 1);
    return ctx->bundles[idx];
}

// 验签后释放引用
void bundle_release(bundle_swap_ctx_t* ctx, trust_bundle_t* b) {
    uint8_t idx = (b == ctx->bundles[0]) ? 0 : 1;
    atomic_fetch_sub(&ctx->refs[idx], 1);
}

// OTA reload：等待旧 bundle 引用归零后才释放内存
int bundle_reload(bundle_swap_ctx_t* ctx, const uint8_t* new_pb, size_t len) {
    uint8_t old_idx = atomic_load(&ctx->active_idx);
    uint8_t new_idx = 1 - old_idx;

    // 1. 加载到 shadow slot
    ctx->bundles[new_idx] = bundle_parse_and_verify(new_pb, len);
    if (!ctx->bundles[new_idx]) return -1;

    // 2. 原子切换
    atomic_store(&ctx->active_idx, new_idx);

    // 3. 等待旧 bundle 引用归零（自旋，最大 100ms）
    for (int i = 0; i < 100; i++) {
        if (atomic_load(&ctx->refs[old_idx]) == 0) break;
        usleep(1000);
    }
    bundle_free(ctx->bundles[old_idx]);
    ctx->bundles[old_idx] = NULL;
    return 0;
}
```

---

## 6. Scope 膨胀攻击（AgentCard 空 scope 问题）

### 6.1 攻击向量

若 AgentCard 的 `required_scopes` 为空（`[]`），
则 IAM 在 `issue_a2a_delegation` 时计算：
`effective_scope = required_scopes ∩ caller_scope = [] ∩ [...] = []`

delegation token 的 scope 为空！

**后果取决于 Server Sidecar 如何处理空 scope delegation**：
- 若 Sidecar 认为"空 scope = 无权限" → 拒绝（安全，但破坏正常调用）
- 若 Sidecar 认为"空 scope = 不限制" → 授予所有权限（危险！）

### 6.2 根本设计原则

**Scope 语义严格化**：

```
空 scope delegation 的语义：
  发起方角度：Client 表示"不声明任何需要"
  接收方角度：Server 应理解为"Client 没有任何权限"

不变量：
  scope = [] → 等价于 deny-all（不允许任何工具调用）
  （这与 OAuth "no scope = full access" 的常见误解相反）
```

**KMSS 执行**：

```c
// kmss_issue_a2a_delegation 中
if (n_scopes == 0) {
    // 空 scope delegation 是合法的，但有特殊语义
    // 仅用于：Agent 只需要"建立通信"而不调用任何工具（如 heartbeat-only 场景）
    // 记录审计事件
    audit_log_write(&(audit_record_t){
        .event_type = AUDIT_A2A_EMPTY_SCOPE_DELEGATION,
        ...
    });
}

// Sidecar Guard.Check 中
if (delegation_claims.n_scopes == 0 && action != A2A_HEARTBEAT) {
    return GUARD_DENY;  // 空 scope 只允许心跳操作
}
```

**Server Skill Policy 补充保护**：

```c
// 即使 delegation scope 为空，Skill Policy 定义了最小必须 scope
// Server 端的 scope check 是双层：
//   Layer 1（Sidecar）：claims.scope 是否满足 skill 的 required_scopes
//   Layer 2（Guard.Check）：实际工具调用 scope ⊆ claims.scope

// 只要 Layer 1 严格执行 required_scopes 不为空，即可防御
```

---

## 7. 多跳撤销传播延迟

### 7.1 问题

```text
链路：CD → AD → VD

CD delegation (jti=A) 被 OEM 紧急 revoke（如 CVE）：

T=0     OEM 触发 revoke(jti=A)
T+0.1s  CD 域 KMSS 更新 CRL
T+0.2s  CD Sidecar 收到 CRL push → 标记 jti=A 已 revoked

问题：AD 和 VD 怎么知道？

方案一（被动 CRL 传播）：
  AD Sidecar 在下次验签时检查 CRL
  → 但 AD 是 CRL 的消费方，它只有 CD 的 trust bundle（含公钥和已知 revoked list）
  → 跨域 CRL 需要 OEM 同时 push 到 AD/VD Sidecar

方案二（主动链路中断）：
  CD KMSS revoke jti=A 时，同时向所有已知 AD/VD delegation 发送 revoke 通知
  → 但 KMSS 不知道 jti=A 的 sub-delegation 情况！
```

### 7.2 解决方案：级联 Revoke 机制

#### 7.2.1 Delegation Chain 注册表

```c
// KMSS 在签发 A2A delegation 时，记录 parent → child 映射
// （只记录 jti，不记录完整 token 内容）

typedef struct {
    char parent_jti[37];
    char child_jti[37];
    char child_domain[4];  // 哪个域的 Sidecar 持有 child
    uint64_t child_exp;    // 子 token 到期时间（到期后自动清理）
} delegation_chain_entry_t;

// 当 parent_jti 被 revoke 时，KMSS 自动查找所有 child，级联 revoke
int kmss_revoke_cascade(const char* jti) {
    kmss_revoke(jti);  // revoke 自身

    // 查找所有子 delegation
    delegation_chain_entry_t children[16];
    int n = kmss_chain_lookup_children(jti, children, 16);
    for (int i = 0; i < n; i++) {
        // 向子 token 所在域推送 revoke 通知
        kmss_push_cross_domain_revoke(children[i].child_domain,
                                      children[i].child_jti);
        kmss_revoke_cascade(children[i].child_jti);  // 递归
    }
}
```

#### 7.2.2 跨域 Revoke Push 协议

```proto
// 已有 CRL push 机制的扩展
service KMSSRevocationService {
  // 现有：本域 token revoke 通知
  rpc PushRevocation(RevocationEvent) returns (RevocationAck);
  
  // 新增：跨域级联 revoke（A2A delegation chain 专用）
  rpc PushCrossdomainRevoke(CrossdomainRevokeRequest) returns (RevocationAck);
}

message CrossdomainRevokeRequest {
  string  source_domain    = 1;   // 发起 revoke 的域
  string  jti_to_revoke    = 2;   // 要 revoke 的子 delegation jti
  string  parent_jti       = 3;   // 父 delegation（用于验证级联合法性）
  bytes   source_auth      = 4;   // 源域 Sidecar 的签名（防伪造 revoke 请求）
}
```

#### 7.2.3 传播延迟 SLA

| 跳数 | 最坏延迟 | 来源 |
|---|---|---|
| 1 跳（本域） | < 0.5s | CRL push 直接到本域 Sidecar |
| 2 跳（跨一域） | < 1.5s | 级联 push：源域 CRL push(0.5s) + 跨域 push(0.5s) + 目标域处理(0.5s) |
| 3 跳（全链路） | < 3s | 两次跨域 push |

---

## 8. IAM 在 A2A 场景的延迟临界点分析

### 8.1 关键路径延迟分解

```
一次 A2A 任务从提交到首次 TaskEvent 的延迟（含 IAM 全路径）：

                         时间（P50/P99）
                         ──────────────
AgentCard lookup          0.5ms / 3ms   （本地注册表 hash 查找）
AgentCard verify          1ms / 5ms     （KMSS 验签，复用 L2 公钥）
Skill Policy lookup       0.05ms / 0.1ms（内存哈希表 O(1)）
Scope intersection        0.1ms / 0.5ms （集合操作）
KMSS issue_a2a_delegation 3ms / 15ms    （TEE 签名 = 主要瓶颈）
gRPC connect (跨域 mTLS)  2ms / 8ms     （TLS 握手，有连接复用时 0ms）
Server Sidecar verify     2ms / 10ms    （KMSS verify 调用）
Server Guard.Check        1ms / 5ms

总计 P50: ~9.6ms
总计 P99: ~46.6ms
```

### 8.2 优化点

#### 8.2.1 AgentCard 本地缓存（最大收益）

```
优化前：每次 send_task 都 lookup + verify AgentCard
优化后：本地 LRU 缓存（TTL=5min），命中时跳过 verify
节省：1.5ms P50 / 8ms P99

缓存 key = skill_id + target_domain
缓存 value = verified AgentCard + cached_spiffe_id
缓存失效：AgentCard 注册表 push 变更通知 OR TTL 到期
```

#### 8.2.2 Delegation Token 复用（最大收益）

```
问题：同一 A2A Session 内对相同 target + skill + scope 反复申请 delegation

优化：Session 级 delegation token 缓存
  key = (target_spiffe_id, skill_id, scope_hash)
  value = delegation_token
  TTL = min(token.exp - 30s, 5min)  // 提前 30s 预旋转

节省：3ms P50 / 15ms P99 per call
风险：scope 变化时缓存需要失效 → 监听 KMSS scope_tightened 事件
```

#### 8.2.3 TEE 签名预计算（批量）

```c
// KMSS 内部：提前派生 delegation key material，减少 TEE 热路径延迟
// （类似 TLS session ticket 预计算）
// 实现：KMSS 后台线程维护 "pre-signed token slots"
// 申请时直接取 pre-signed token + 填充 claims → 比实时签名快 2~5ms
```

### 8.3 延迟预算分配（生产建议）

| 路径 | 预算 | 机制 |
|---|---|---|
| 同域 A2A（域内两个 Agent） | ≤ 10ms | delegation token 复用 + 本地 Guard.Check |
| 跨域 A2A（一跳） | ≤ 30ms | AgentCard 缓存 + delegation 复用 + gRPC 连接复用 |
| 跨域 A2A（两跳） | ≤ 60ms | 同上 × 2 跳；sub-delegation 开销约 15ms |
| 首次建立（冷路径） | ≤ 200ms | 含 AgentCard 签名 + registry 注册 |

---

# Part II: gRPC 扩展演进路径

## 9. 演进总览

```
Phase 0 (当前)
  Raw string metadata headers
  x-a2a-delegation: <jwt_string>
  x-a2a-task-id: <uuid>
  ↓ 问题：无类型、无版本、字段扩展困难、metadata 大小受限

Phase 1 (近期)
  Binary Proto 元数据 headers
  x-iam-context-bin: <proto bytes>
  ↓ 收益：类型安全 + 版本化 + 字段可选扩展

Phase 2 (中期)
  gRPC CallCredentials + ChannelCredentials 集成
  ↓ 收益：token 生命周期完全由 gRPC framework 管理

Phase 3 (中期)
  Server-side 拦截器链分层（IAM 逻辑完全从业务代码解耦）
  ↓ 收益：A2A 中间件、Scope 执行、审计日志作为独立拦截器

Phase 4 (远期)
  原生 A2A 流协议（替代 HTTP/SSE）
  ↓ 收益：Task 心跳 = IAM Lease 心跳，Token 刷新无需断开连接

Phase 5 (远期)
  Service Mesh / xDS 卸载
  ↓ 收益：IAM 逻辑从应用层下沉到网络层（Envoy sidecar）
```

---

## 10. Phase 0 → Phase 1: Binary Proto 元数据

### 10.1 现有（Phase 0）问题

```c
// Phase 0：在 metadata 里放 raw string
grpc_metadata md[] = {
    { "x-a2a-delegation", jwt_string, strlen(jwt_string) },
    { "x-a2a-task-id",    task_id,    strlen(task_id) },
    { "authorization",    session_jwt, strlen(session_jwt) },
};
```

**问题**：
- JWT 本身就很长（~600 bytes），多个 header 加起来接近 8KB gRPC metadata 默认限制
- 字段没有版本标识，新增字段需要新增 header key
- Server 端手动 `strcmp(key, "x-a2a-delegation")` 容易出错

### 10.2 Phase 1 设计：IAMContext + A2AContext 二进制 Proto

```proto
// iam_grpc_context.proto
syntax = "proto3";
package vehicle.iam.grpc.v1;

// 所有 IAM 相关凭据，序列化后放到 "x-iam-context-bin" metadata
message IAMContext {
  // L0: Workload 身份
  bytes  svid_jwt         = 1;   // JWT，可省略（mTLS 已携带证书）

  // L2: Session Token
  bytes  session_token    = 2;

  // L3 / L3A: Lease Token（本域长任务 OR 跨域 A2A delegation）
  bytes  lease_token      = 3;

  // L1 / L1A: Per-call task token（每次工具调用可选）
  bytes  task_token       = 4;

  // 元信息（版本控制）
  uint32 proto_version    = 15;  // 当前 = 1
}

// A2A 专属字段，序列化后放到 "x-a2a-context-bin" metadata
message A2AContext {
  string a2a_task_id      = 1;   // UUID，绑定 A2A Task
  string a2a_skill_id     = 2;   // 本次调用的 skill
  uint32 hop_depth        = 3;   // 剩余可委托深度
  repeated string hop_chain = 4; // 已经过的 SPIFFE ID 列表
  uint32 min_effective_ttl_s = 5;// 客户端要求的最小 TTL（见 §1.3）
  uint32 estimated_duration_s = 6;
  uint32 proto_version    = 15;
}
```

### 10.3 SDK 自动注入

```c
// libiamguard.so 提供 gRPC metadata 生成辅助函数
// （适用于 C grpc core 和 C++ grpcpp）

// 调用方（Agent SDK）构造上下文
iam_grpc_context_t ctx = {
    .session_token = sdk->session_token,
    .lease_token   = sdk->current_a2a_lease,
};
a2a_grpc_context_t a2a = {
    .a2a_task_id  = task_handle->task_id,
    .a2a_skill_id = "route-plan",
    .hop_depth    = 1,
};

// 序列化到 gRPC metadata
grpc_metadata* md;
size_t md_count;
iam_grpc_context_encode(&ctx, &a2a, &md, &md_count);
// → 输出两个 metadata key：
//   "x-iam-context-bin": base64(proto_marshal(IAMContext))
//   "x-a2a-context-bin": base64(proto_marshal(A2AContext))
```

### 10.4 Server Sidecar 解析

```c
// Server 端：统一入口解析
typedef struct {
    IAMContext__t  iam;
    A2AContext__t  a2a;
    bool           has_iam;
    bool           has_a2a;
} parsed_grpc_contexts_t;

int sidecar_parse_grpc_contexts(
    const grpc_metadata* md, size_t n,
    parsed_grpc_contexts_t* out
) {
    for (size_t i = 0; i < n; i++) {
        if (strcmp(md[i].key, "x-iam-context-bin") == 0) {
            if (iam_context__unpack(md[i].value, md[i].value_length,
                                    &out->iam) != 0)
                return -1;
            out->has_iam = true;
        }
        if (strcmp(md[i].key, "x-a2a-context-bin") == 0) {
            if (a2a_context__unpack(md[i].value, md[i].value_length,
                                     &out->a2a) != 0)
                return -1;
            out->has_a2a = true;
        }
    }
    return 0;
}
```

---

## 11. Phase 2: gRPC CallCredentials 集成

### 11.1 设计目标

将 token 的获取、缓存、刷新逻辑从 Agent 业务代码迁移到 **gRPC 凭据框架**内，
使 Agent 代码对 IAM 完全透明：

```
Phase 1（业务代码负责）:
  Agent 调用 sdk->get_delegation_token()
  Agent 手动打包 metadata
  Agent 负责检查 token 是否过期并刷新

Phase 2（gRPC 框架负责）:
  Agent 只创建 channel（携带 A2AIAMCredentials）
  gRPC framework 在每次 RPC 前自动调用 GetRequestMetadata()
  A2AIAMCredentials 内部完成 token 获取 / 缓存 / 刷新
```

### 11.2 C++ grpcpp 实现

```cpp
// a2a_iam_credentials.h

class A2AIAMCredentials : public grpc::CallCredentials {
public:
    explicit A2AIAMCredentials(IAMSDKClient* sdk, A2ATaskContext* task_ctx)
        : sdk_(sdk), task_ctx_(task_ctx) {}

    // gRPC 框架在每次 RPC 调用前调用此方法
    grpc::Status GetRequestMetadata(
        grpc::string_ref service_url,
        std::multimap<grpc::string, grpc::string>* metadata) override
    {
        // 获取或刷新 delegation token（内部有缓存）
        auto token_result = sdk_->GetOrRefreshA2ADelegation(task_ctx_);
        if (!token_result.ok()) {
            return grpc::Status(grpc::StatusCode::UNAUTHENTICATED,
                               token_result.status().message());
        }

        // 构造 IAMContext + A2AContext proto
        vehicle::iam::grpc::v1::IAMContext iam_ctx;
        iam_ctx.set_session_token(sdk_->GetSessionToken());
        iam_ctx.set_lease_token(token_result.value().token_bytes);

        vehicle::iam::grpc::v1::A2AContext a2a_ctx;
        a2a_ctx.set_a2a_task_id(task_ctx_->task_id);
        a2a_ctx.set_a2a_skill_id(task_ctx_->skill_id);
        a2a_ctx.set_hop_depth(task_ctx_->hop_depth);

        // 序列化 + 注入 metadata
        std::string iam_bin, a2a_bin;
        iam_ctx.SerializeToString(&iam_bin);
        a2a_ctx.SerializeToString(&a2a_bin);
        metadata->insert({"x-iam-context-bin", iam_bin});
        metadata->insert({"x-a2a-context-bin", a2a_bin});

        return grpc::Status::OK;
    }

    // 是否需要在 token 刷新失败时触发重试
    bool IsBlocking() const override { return true; }

private:
    IAMSDKClient*   sdk_;
    A2ATaskContext* task_ctx_;
};

// 组合 mTLS + A2A IAM：
// mTLS 提供 channel-level 身份验证（SPIFFE SVID 证书）
// A2AIAMCredentials 提供 call-level A2A 授权
std::shared_ptr<grpc::ChannelCredentials> MakeA2AChannelCreds(
    const char*   ca_cert_pem,    // AD trust bundle
    const char*   client_cert,    // CD 的 SVID X.509
    const char*   client_key,     // CD 的 SVID 私钥 (PKCS#11 uri)
    IAMSDKClient* sdk,
    A2ATaskContext* task_ctx
) {
    grpc::SslCredentialsOptions ssl_opts;
    ssl_opts.pem_root_certs  = ca_cert_pem;
    ssl_opts.pem_cert_chain  = client_cert;
    ssl_opts.pem_private_key = client_key;  // 实际对接 PKCS#11 引擎

    auto tls_creds = grpc::SslCredentials(ssl_opts);
    auto iam_creds = std::make_shared<A2AIAMCredentials>(sdk, task_ctx);

    // CompositeChannelCredentials = mTLS (channel) + A2AIAMCredentials (per-call)
    return grpc::CompositeChannelCredentials(tls_creds, iam_creds);
}

// Agent 侧使用示例（业务代码几乎不感知 IAM）：
auto channel = grpc::CreateChannel(
    "ad-sidecar.car.local:7000",
    MakeA2AChannelCreds(ad_ca_cert, my_cert, my_key, sdk, task_ctx)
);
auto stub = vehicle::a2a::v1::A2ATaskService::NewStub(channel);
// 此后 stub 的每次 RPC 都自动携带 IAM + A2A 凭据
```

### 11.3 C grpc-core 实现（车端嵌入式路径）

```c
// 车端 C 嵌入式版本（避免 C++ 运行时依赖）
// 使用 grpc_metadata_credentials_create_from_plugin()

typedef struct {
    iam_sdk_t*       sdk;
    a2a_task_ctx_t*  task_ctx;
} a2a_iam_plugin_state_t;

static void a2a_get_request_metadata(
    void* state,
    grpc_auth_metadata_context context,
    grpc_credentials_plugin_metadata_cb cb,
    void* user_data,
    grpc_metadata creds_md[GRPC_METADATA_CREDENTIALS_PLUGIN_SYNC_MAX],
    size_t* num_creds_md,
    grpc_status_code* status,
    const char** error_details
) {
    a2a_iam_plugin_state_t* s = (a2a_iam_plugin_state_t*)state;

    // 获取或刷新 delegation token
    kmss_token_t* token = iam_sdk_get_or_refresh_delegation(s->sdk, s->task_ctx);
    if (!token) {
        *status = GRPC_STATUS_UNAUTHENTICATED;
        *error_details = "delegation_token_unavailable";
        return;
    }

    // 序列化 IAMContext proto
    uint8_t iam_buf[512];
    size_t  iam_len = iam_context_encode(s->sdk, token, iam_buf, sizeof(iam_buf));

    // 序列化 A2AContext proto
    uint8_t a2a_buf[256];
    size_t  a2a_len = a2a_context_encode(s->task_ctx, a2a_buf, sizeof(a2a_buf));

    creds_md[0] = (grpc_metadata){
        .key   = grpc_slice_from_static_string("x-iam-context-bin"),
        .value = grpc_slice_from_copied_buffer((char*)iam_buf, iam_len),
    };
    creds_md[1] = (grpc_metadata){
        .key   = grpc_slice_from_static_string("x-a2a-context-bin"),
        .value = grpc_slice_from_copied_buffer((char*)a2a_buf, a2a_len),
    };
    *num_creds_md = 2;
    *status = GRPC_STATUS_OK;
}

grpc_call_credentials* make_a2a_iam_call_credentials(
    iam_sdk_t* sdk, a2a_task_ctx_t* task_ctx
) {
    static a2a_iam_plugin_state_t state;  // per-channel，生命周期与 channel 一致
    state.sdk      = sdk;
    state.task_ctx = task_ctx;

    grpc_metadata_credentials_plugin plugin = {
        .get_metadata  = a2a_get_request_metadata,
        .destroy       = NULL,
        .state         = &state,
        .type          = "a2a_iam",
    };
    return grpc_metadata_credentials_create_from_plugin(plugin, GRPC_SECURITY_NONE, NULL);
}
```

---

## 12. Phase 3: 拦截器链分层

### 12.1 拦截器职责分离

```
请求到达 Sidecar gRPC Server

┌────────────────────────────────────────────────────────────────────┐
│ Interceptor 1: SpiffeInterceptor                                   │
│  • 从 TLS peer certificate 提取 SPIFFE ID                          │
│  • 向 ServerContext 注入 PeerSPIFFEID                              │
│  • 失败：UNAUTHENTICATED                                           │
└────────────────────────┬───────────────────────────────────────────┘
                         │ 注入：PeerSPIFFEID
                         ▼
┌────────────────────────────────────────────────────────────────────┐
│ Interceptor 2: IAMContextInterceptor                               │
│  • 解析 x-iam-context-bin → IAMContext                            │
│  • 调用 kmss_verify_token()，验签 session + lease token            │
│  • 向 ServerContext 注入 IAMClaims                                 │
│  • 失败：UNAUTHENTICATED（expired / invalid）                      │
└────────────────────────┬───────────────────────────────────────────┘
                         │ 注入：IAMClaims
                         ▼
┌────────────────────────────────────────────────────────────────────┐
│ Interceptor 3: A2AMiddlewareInterceptor                            │
│  • 解析 x-a2a-context-bin → A2AContext                            │
│  • 7 项 A2A 检查（§7 的逻辑）                                      │
│  • 向 ServerContext 注入 A2ATaskContext                            │
│  • 失败：PERMISSION_DENIED（含 IAMErrorDetails proto）             │
└────────────────────────┬───────────────────────────────────────────┘
                         │ 注入：A2ATaskContext
                         ▼
┌────────────────────────────────────────────────────────────────────┐
│ Interceptor 4: MethodScopeInterceptor                              │
│  • 按 RPC 方法名查 Skill Policy 的 per-method required scope       │
│  • 对比 IAMClaims.scope                                            │
│  • 失败：PERMISSION_DENIED                                         │
└────────────────────────┬───────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────┐
│ Interceptor 5: AuditInterceptor（先注册 = 最外层 = 最后执行）      │
│  • 记录入口时间戳                                                   │
│  • defer：请求完成后写 audit_record（含 latency）                   │
│  • 即使业务层 panic 也写审计                                        │
└────────────────────────┬───────────────────────────────────────────┘
                         │
                         ▼
                   Handler（业务逻辑）
```

### 12.2 定制 Proto 扩展：MethodOptions

```proto
// a2a_method_options.proto
syntax = "proto3";
import "google/protobuf/descriptor.proto";
package vehicle.a2a.v1;

// 每个 RPC 方法的 A2A + IAM 策略（编译时注解）
message A2AMethodPolicy {
  // 调用此方法需要的 skill_id（空=不需要 A2A delegation）
  string required_skill_id       = 1;

  // 此方法是否允许 sub-delegation（中间节点继续向下委托）
  bool   allows_sub_delegation   = 2;

  // 此方法允许的最大 hop_depth（0 = 不允许 sub-delegate）
  uint32 max_hop_depth           = 3;

  // 此方法的最小 required_scope（server-side 补充检查）
  repeated string required_scopes = 4;

  // 此方法允许的最小调用方 ASIL 等级
  uint32 min_caller_asil         = 5;  // 0=QM, 4=ASIL-D
}

// 注册为 protobuf method option
extend google.protobuf.MethodOptions {
  A2AMethodPolicy a2a_policy = 50100;  // 自定义 field number（>50000）
}
```

**在 .proto 文件中使用**：

```proto
// a2a_service.proto
import "a2a_method_options.proto";

service A2ATaskService {
  // 路径规划：需要 route-plan skill，允许转委托给 VD（hmi 展示）
  rpc RoutePlan(RoutePlanRequest) returns (stream RoutePlanEvent) {
    option (vehicle.a2a.v1.a2a_policy) = {
      required_skill_id:     "route-plan",
      allows_sub_delegation: true,
      max_hop_depth:         2,
      required_scopes:       ["read:navi.route", "read:navi.traffic"],
      min_caller_asil:       0   // QM 可调
    };
  }

  // 制动控制：只有 ASIL-D 调用方可用，不允许转委托
  rpc BrakeControl(BrakeRequest) returns (BrakeResponse) {
    option (vehicle.a2a.v1.a2a_policy) = {
      required_skill_id:     "brake-control",
      allows_sub_delegation: false,
      max_hop_depth:         0,
      required_scopes:       ["tool:control.brake"],
      min_caller_asil:       4   // 必须 ASIL-D
    };
  }
}
```

**拦截器读取 Method Options**：

```cpp
// MethodScopeInterceptor 在启动时预加载所有方法的 policy
class MethodScopeInterceptor : public grpc::ServerInterceptorFactoryInterface {
    std::unordered_map<std::string, A2AMethodPolicy> method_policies_;

    void LoadMethodPolicies(const grpc::Service* svc) {
        const auto* desc = svc->GetServiceDescriptor();
        for (int i = 0; i < desc->method_count(); ++i) {
            const auto* m = desc->method(i);
            if (m->options().HasExtension(vehicle::a2a::v1::a2a_policy)) {
                method_policies_[m->full_name()] =
                    m->options().GetExtension(vehicle::a2a::v1::a2a_policy);
            }
        }
    }
};
```

### 12.3 定制错误详情（Rich Error Model）

```proto
// iam_error_details.proto
import "google/rpc/status.proto";
import "google/protobuf/descriptor.proto";
package vehicle.iam.v1;

// IAM 专属错误详情（嵌入 google.rpc.Status.details）
message IAMErrorDetails {
  enum Code {
    IAM_ERROR_UNKNOWN            = 0;
    IAM_TOKEN_EXPIRED            = 1;   // token 过期
    IAM_TOKEN_REVOKED            = 2;   // token 已被撤销
    IAM_SCOPE_INSUFFICIENT       = 3;   // scope 不足
    IAM_DELEGATION_EXPIRED       = 4;   // A2A delegation 过期
    IAM_HOP_DEPTH_EXCEEDED       = 5;   // hop_depth = 0，不能再委托
    IAM_CHAIN_LOOP_DETECTED      = 6;   // hop_chain 中发现环路
    IAM_SKILL_NOT_FOUND          = 7;   // skill_id 未注册
    IAM_ASIL_BOUNDARY_VIOLATION  = 8;   // 调用方 ASIL 不足
    IAM_KMSS_UNAVAILABLE         = 9;   // KMSS 不可达
    IAM_AGENTCARD_INVALID        = 10;  // AgentCard 签名无效
    IAM_TASK_ID_MISMATCH         = 11;  // task_id 绑定不匹配
    IAM_RATE_LIMITED             = 12;  // token 申请被限流
  }

  Code    code              = 1;
  string  message           = 2;   // 人读信息
  string  failed_jti        = 3;   // 哪个 token 失败了
  uint64  token_expires_at  = 4;   // 失败 token 的到期时间（0=已过期）
  string  remedy_action     = 5;   // 建议操作："refresh_session" / "retry_after_30s"
  uint32  retry_after_ms    = 6;   // 限流时的 backoff 建议
}

// 扩展 google.rpc.Status（rich error model）
extend google.rpc.Status {
  IAMErrorDetails iam_error = 50200;
}
```

**Server 端返回 IAM 错误**：

```cpp
grpc::Status MakeIAMError(IAMErrorDetails::Code code,
                           const std::string& message,
                           const std::string& jti = "",
                           uint32_t retry_ms = 0) {
    google::rpc::Status status_proto;
    status_proto.set_code(grpc::StatusCode::PERMISSION_DENIED);
    status_proto.set_message(message);

    vehicle::iam::v1::IAMErrorDetails details;
    details.set_code(code);
    details.set_message(message);
    if (!jti.empty()) details.set_failed_jti(jti);
    if (retry_ms > 0) details.set_retry_after_ms(retry_ms);

    status_proto.add_details()->PackFrom(details);

    // 序列化到 gRPC trailing metadata
    // ...
    return grpc::Status(grpc::StatusCode::PERMISSION_DENIED, message);
}
```

---

## 13. Phase 4: 原生 A2A 流协议

### 13.1 HTTP/SSE 的车端局限

| 问题 | HTTP/SSE 现状 | gRPC 流解决 |
|---|---|---|
| Token 刷新 | 需要断开重连（HTTP 连接不支持 header 变更） | 流内发送 `token_refresh` 消息，无需断开 |
| IAM 心跳与业务心跳 | 两套：gRPC keepalive + Lease 心跳 | 合并为流内 `heartbeat` 消息 |
| 双向通信 | SSE 是单向（Server → Client） | gRPC 双向流原生支持 |
| 流量控制 | HTTP/1.1 无多路复用（HTTP/2 除外） | gRPC/HTTP2 多路复用 + 流量控制 |
| mTLS 集成 | 需要额外配置 | gRPC 原生 mTLS |

### 13.2 定制 A2A gRPC 流协议定义

```proto
// a2a_stream_protocol.proto
syntax = "proto3";
package vehicle.a2a.v1;

service A2ATaskService {
  // 双向流：Client 发控制消息，Server 推 Task 事件
  // 整个 A2A Task 生命周期在一个流内完成
  rpc TaskSession(stream A2AClientMessage) returns (stream A2AServerEvent);

  // 点查（需要 IAM Session Token 验证）
  rpc GetTask(GetTaskRequest) returns (Task);
}

// ===== Client → Server 消息 =====
message A2AClientMessage {
  oneof msg {
    A2ATaskSubmit    submit    = 1;  // 提交任务（流的第一条消息）
    A2AHeartbeat     heartbeat = 2;  // 周期性心跳（同步 IAM Lease 心跳）
    A2AUserInput     input     = 3;  // 回应 input-required 状态
    A2ATaskCancel    cancel    = 4;  // 主动取消
    A2ATokenRefresh  token     = 5;  // 主动旋转 token（不断流）
    A2ASubDelegate   delegate  = 6;  // 中间节点再委托（通知 Server 已 sub-delegate）
  }
}

message A2ATaskSubmit {
  string              task_id      = 1;
  string              skill_id     = 2;
  repeated A2APart    input_parts  = 3;  // 任务输入
  A2ATaskHints        hints        = 4;  // min_ttl, est_duration
}

message A2AHeartbeat {
  string  task_id         = 1;
  uint64  client_ts_us    = 2;   // 客户端时间戳（用于时钟对齐）
  uint32  task_progress   = 3;   // 0~100，可选，影响 KMSS lease TTL 决策
}

// 主动 Token 旋转（在当前流内，不断开连接）
message A2ATokenRefresh {
  string  task_id          = 1;
  bytes   new_iam_context  = 2;  // 序列化的新 IAMContext proto
  bytes   new_a2a_context  = 3;  // 序列化的新 A2AContext proto（hop_depth 等更新）
}

// ===== Server → Client 消息 =====
message A2AServerEvent {
  oneof event {
    A2ATaskStatus       status      = 1;  // 状态变化（working/completed/failed）
    A2AProgressUpdate   progress    = 2;  // 进度更新
    A2AArtifact         artifact    = 3;  // 产出物（结果数据）
    A2AInputRequest     input_req   = 4;  // 请求 Client 补充输入
    A2AHeartbeatAck     hb_ack      = 5;  // 心跳确认 + IAM Lease 状态
    A2ATokenExpiring    token_warn  = 6;  // 提前通知 Client token 即将过期
    A2AScopeChanged     scope       = 7;  // KMSS 收紧了 scope（通知 Client）
  }
}

// Server 主动通知 Client token 快过期，让 Client 提前旋转
message A2ATokenExpiring {
  string task_id         = 1;
  uint64 expires_at_us   = 2;   // token 到期时间
  uint32 suggested_refresh_in_ms = 3;  // 建议在多少毫秒内刷新
}

// KMSS 收紧了 scope，Task 继续但部分权限消失
message A2AScopeChanged {
  string          task_id       = 1;
  repeated string removed_scopes = 2;
  string          reason        = 3;  // 来自 KMSS 的原因
}

// 心跳确认，附带 IAM Lease 当前状态
message A2AHeartbeatAck {
  string task_id          = 1;
  uint64 server_ts_us     = 2;
  uint32 lease_ttl_remaining_s = 3;
  bool   lease_healthy    = 4;
}
```

### 13.3 Token 旋转的流内协议

```
正常流内 Token 旋转（不断流，不丢任务状态）：

Client                                      Server
  │                                            │
  │  [stream 已建立，task WORKING]              │
  │                                            │
  │  注意到 delegation_token 剩余 60s           │
  │  预先申请新 token：                         │
  │  new_token = kmss_issue_a2a_delegation()   │
  │                                            │
  │──── A2ATokenRefresh(new_iam_ctx) ─────────▶│
  │                                            │  Server Sidecar 验证新 token：
  │                                            │  kmss_verify_a2a_delegation(new_ctx)
  │                                            │  → valid, task_id 匹配
  │◀─── A2AHeartbeatAck(lease_ttl_remaining)  ─│  Server 切换到新 token
  │                                            │
  │  旧 token 继续使用直到新 token 生效         │
  │  （双 token 重叠窗口 = 5s）                │
  │                                            │
  [任务继续，无中断]
```

**旋转的安全保证**：
- 新旧 token 的 `a2a_task_id` 必须相同（Server 验证）
- 新 token 的 `scope ⊆ 旧 token scope`（不允许旋转时扩大权限）
- 旧 token 在重叠窗口（5s）后由 Server 侧主动废弃（不等 TTL 到期）

---

## 14. Phase 5: Service Mesh / xDS 卸载

### 14.1 从 Sidecar Process 到 Envoy Sidecar

当系统规模增长，每个进程维护自己的 Sidecar 进程变得管理困难。
可以将 IAM + A2A 验证逻辑下沉到**网络层 Envoy sidecar**：

```
Phase 3（应用层 Sidecar）:
  Agent Process → Guard Sidecar Process → (本地 UDS) → KMSS Process
  IAM 逻辑在 Sidecar Process 应用层实现

Phase 5（网络层 Envoy Sidecar）:
  Agent Process → Envoy Sidecar (本机 iptables 拦截) → 远端 AD Agent Envoy
  IAM 逻辑通过 Envoy ext_authz 扩展实现
  Policy 通过 xDS 动态分发
```

### 14.2 关键 xDS 扩展点

```yaml
# Envoy 配置片段：ext_authz 扩展（A2A + IAM 验证）
http_filters:
  - name: envoy.filters.http.ext_authz
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.http.ext_authz.v3.ExtAuthz
      grpc_service:
        envoy_grpc:
          cluster_name: iam_authz_server  # 指向本机 KMSS daemon（UDS）
        timeout: 10ms  # IAM 验证 SLA：< 10ms
      with_request_body:
        max_request_bytes: 0  # 不转发 body，只转发 headers（含 IAM context）
      failure_mode_allow: false  # KMSS 不可达时 fail-closed
```

**ext_authz 服务**（实现 `envoy.service.auth.v3.Authorization`）：

```proto
service Authorization {
  rpc Check(v3.CheckRequest) returns (v3.CheckResponse);
}
// CheckRequest 包含：请求头（含 x-iam-context-bin, x-a2a-context-bin）
// CheckResponse 返回：allow / deny + IAM 错误详情
```

这里的 `Authorization` 服务实现就是原来 Sidecar A2A 中间件逻辑的迁移版本。

### 14.3 SPIFFE Workload API 集成

```yaml
# Envoy Secret Discovery Service（SDS）：动态分发 SPIFFE SVID 证书
# Agent 进程不需要手动管理证书文件
transport_sockets:
  - name: envoy.transport_sockets.tls
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.UpstreamTlsContext
      common_tls_context:
        tls_certificate_sds_secret_configs:
          - name: "spiffe://car.local/ns/adas/sa/perception-agent"
            sds_config:
              api_config_source:
                grpc_services:
                  - envoy_grpc:
                      cluster_name: spire_agent  # SPIRE Agent 在本机，UDS
```

---

## 15. 定制 gRPC 扩展机制汇总

| 扩展机制 | 使用场景 | 在本方案中的应用 |
|---|---|---|
| **Binary Metadata Headers** (`*-bin`) | 传递结构化 IAM 上下文 | `x-iam-context-bin`, `x-a2a-context-bin` |
| **CallCredentials** | 每次 RPC 自动注入 IAM token | `A2AIAMCredentials` 封装 token 获取/刷新 |
| **ChannelCredentials** | Channel 级 mTLS + SPIFFE | `CompositeChannelCredentials(mTLS + CallCreds)` |
| **Server Interceptors** | 服务端中间件链 | 5 层拦截器（SPIFFE / IAM / A2A / Scope / Audit） |
| **MethodOptions 扩展** | per-RPC 策略注解 | `A2AMethodPolicy` option 注解每个 RPC |
| **Status 扩展** (Rich Error) | 结构化 IAM 错误 | `IAMErrorDetails` 在 `google.rpc.Status.details` |
| **双向流** (Bidirectional Streaming) | Task 生命周期 + 心跳 | `TaskSession(stream) returns (stream)` |
| **ext_authz** (Envoy) | 网络层 IAM 卸载 | 向 KMSS 代理发 authz 请求 |
| **SDS** (Envoy Secret Discovery) | 动态证书管理 | SPIFFE SVID 动态分发 |

---

## 16. 修订记录

| 版本 | 日期 | 内容 |
|---|---|---|
| 1.0 | 2026-07-30 | 初稿：8 类深层设计问题 + gRPC 5 阶段演进 + Binary Proto + CallCredentials + 拦截器链 + 流协议 + xDS |
