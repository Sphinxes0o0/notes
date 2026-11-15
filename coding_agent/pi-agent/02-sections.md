---
title: "2. pi-ai 统一 API：40+ Provider 的抽象"
---

# 2. pi-ai 统一 API：40+ Provider 的抽象 {#chapter}

[返回总目录](../pi-agent)

### 2. pi-ai 统一 API：40+ Provider 的抽象 {#_2-pi-ai-统一-api-40-provider-的抽象}

#### 核心设计：Provider Adapter Pattern {#核心设计-provider-adapter-pattern}

统一 API 通过 `ApiProvider` 接口和注册表实现：

```typescript
// api-registry.ts
export interface ApiProvider<TApi extends Api = Api, TOptions extends StreamOptions = StreamOptions> {
  api: TApi;                          // API 类型标识，如 "anthropic-messages"
  stream: StreamFunction<TApi, TOptions>;         // 完整 API（provider-specific options）
  streamSimple: StreamFunction<TApi, SimpleStreamOptions>; // 简化 API（统一 options）
}

// 注册表
const apiProviderRegistry = new Map<string, RegisteredApiProvider>();

export function registerApiProvider<TApi extends Api>(
  provider: ApiProvider<TApi>,
  sourceId?: string,
): void {
  apiProviderRegistry.set(provider.api, { provider, sourceId });
}
```

#### 统一入口（stream.ts） {#统一入口-stream-ts}

```typescript
// 统一流式 API
export function stream<TApi extends Api>(
  model: Model<TApi>,
  context: Context,
  options?: ProviderStreamOptions,
): AssistantMessageEventStream {
  const provider = resolveApiProvider(model.api);
  return provider.stream(model, context, options as StreamOptions);
}

// 简化版 API：使用统一的 reasoning 层级
export function streamSimple<TApi extends Api>(
  model: Model<TApi>,
  context: Context,
  options?: SimpleStreamOptions,
): AssistantMessageEventStream {
  const provider = resolveApiProvider(model.api);
  return provider.streamSimple(model, context, options);
}
```

**SimpleStreamOptions** 是跨 provider 的统一接口：

```typescript
export interface SimpleStreamOptions extends StreamOptions {
  reasoning?: ThinkingLevel;       // "off" | "minimal" | "low" | "medium" | "high" | "xhigh"
  thinkingBudgets?: ThinkingBudgets;
}
```

#### Provider 示例：Anthropic {#provider-示例-anthropic}

```typescript
// providers/anthropic.ts
export const streamSimpleAnthropic: StreamFunction<"anthropic-messages", SimpleStreamOptions> = (
  model, context, options?
): AssistantMessageEventStream => {
  // 将 SimpleStreamOptions 转换为 Anthropic-specific options
  const providerOpts: AnthropicOptions = {
    thinkingEnabled: options?.reasoning !== "off",
    thinkingBudgetTokens: resolveThinkingBudget(options?.reasoning),
    // ...
  };
  return streamAnthropic(model, context, providerOpts);
};
```

#### 统一事件协议 {#统一事件协议}

所有 provider 发出相同的事件类型：

```typescript
export type AssistantMessageEvent =
  | { type: "start"; partial: AssistantMessage }
  | { type: "text_start" | "text_delta" | "text_end"; contentIndex: number; ... }
  | { type: "thinking_start" | "thinking_delta" | "thinking_end"; contentIndex: number; ... }
  | { type: "toolcall_start" | "toolcall_delta" | "toolcall_end"; ... }
  | { type: "done"; reason: "stop" | "length" | "toolUse"; message: AssistantMessage }
  | { type: "error"; reason: "aborted" | "error"; error: AssistantMessage };
```

#### Model 类型抽象（types.ts） {#model-类型抽象-types-ts}

```typescript
export interface Model<TApi extends Api> {
  id: string;
  name: string;
  api: TApi;
  provider: Provider;
  baseUrl: string;
  reasoning: boolean;
  thinkingLevelMap?: ThinkingLevelMap;  // pi 层级 → provider 特定值
  cost: { input: number; output: number; cacheRead: number; cacheWrite: number };
  contextWindow: number;
  maxTokens: number;
  compat?: OpenAICompletionsCompat | OpenAIResponsesCompat | AnthropicMessagesCompat;
}

// 类型安全的模型查找
export function getModel<TProvider extends KnownProvider, TModelId extends keyof MODELS[TProvider]>(
  provider: TProvider,
  modelId: TModelId,
): Model<ModelApi<TProvider, TModelId>>;
```

#### 支持的 API 类型 {#支持的-api-类型}

| API 类型 | Provider 示例 |
|----------|--------------|
| `anthropic-messages` | Anthropic |
| `openai-completions` | OpenAI |
| `openai-responses` | OpenAI Responses API |
| `mistral-conversations` | Mistral |
| `bedrock-converse-stream` | AWS Bedrock |
| `google-generative-ai` | Google Gemini |
| `google-vertex` | Google Vertex AI |
| `azure-openai-responses` | Azure OpenAI |

---

### 3. Context Engineering {#_3-context-engineering}

#### 3.1 Compaction 算法 {#_3-1-compaction-算法}

位置：`agent/src/harness/compaction/compaction.ts`

**两阶段：prepare → compact**

```typescript
// prepareCompaction() 找到切分点
async function prepareCompaction(session: Session, settings: CompactionSettings) {
  // 1. 找到上一个 compaction 点（支持迭代 compaction）
  const previousCompaction = findLastCompaction(session);
  const boundaryStart = previousCompaction ? previousCompaction.firstKeptEntryId : null;

  // 2. 估算当前 context tokens
  const { totalTokens, entries } = await estimateContextTokens(session, boundaryStart);

  // 3. 从最新往回走，累积到 keepRecentTokens 为止
  const cutIdx = findCutPoint(entries, settings.keepRecentTokens);

  // 4. 切分点必须是有效位置：user / assistant / bashExecution / branchSummary / compactionSummary
  return { entriesToSummarize, fileOperations, settings };
}

// findCutPoint 算法
function findCutPoint(entries: SessionTreeEntry[], keepRecentTokens: number): number {
  let accumulated = 0;
  for (let i = entries.length - 1; i >= 0; i--) {
    const entry = entries[i];
    if (!isValidCutPoint(entry)) continue;  // toolResults 不能切
    accumulated += estimateEntryTokens(entry);
    if (accumulated >= keepRecentTokens) {
      // 若在 assistant 处切，找到 turn 开始位置
      if (entry.type === "message" && entry.message.role === "assistant") {
        return findTurnStartIndex(entries, i);
      }
      return i;
    }
  }
  return 0;
}
```

**compact() 生成摘要：**

```typescript
// 摘要格式：结构化 markdown
const SUMMARIZATION_PROMPT = `
## 实现细节

> 本节深入分析 pi_agent_rust 和 oh-my-pi 的核心实现。所有源码均来自 GitHub 仓库。

---

### 1. pi_agent_rust 两阶段执行 enforcement（Capability-Based Security）

#### 1.1 Capability 声明

位置：`src/extensions.rs`（行 ~1155-1250）

十种 capability 形成两级分类——安全与危险：

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Capability {
    Read,      // 读文件和目录
    Write,     // 写/创建/删除文件
    Http,      // 出站 HTTP 请求
    Events,    // 订阅和发送生命周期事件
    Session,   // 访问 session 状态
    Ui,        // UI 操作
    Exec,      // 执行 shell 命令（危险）
    Env,       // 读取环境变量（危险）
    Tool,      // 通用工具调用
    Log,       // 日志
}

// 危险 capability 判定（行 ~2010）
pub const fn is_dangerous(self) -> bool {
    matches!(self, Self::Exec | Self::Env)
}
```

#### 1.2 Stage 1: Capability-Level Policy（ExtensionPolicy::evaluate_for） {#_1-2-stage-1-capability-level-policy-extensionpolicy-evaluate-for}

位置：行 ~10050-10145

Capability 级别的四层 precedence：

```rust
pub fn evaluate_for(&self, capability: &str, extension_id: Option<&str>) -> PolicyCheck {
    // 1. Per-extension deny → Deny（最高优先级）
    // 2. Global deny_caps → Deny
    // 3. Per-extension allow → Allow
    // 4. Global default_caps → Allow（或根据 mode 决定 Prompt/Deny）
    // 5. Mode fallback: Strict→Deny, Prompt→Prompt, Permissive→Allow
}
```

PolicyDecision 定义（行 ~9933）：

```rust
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum PolicyDecision { Allow, Prompt, Deny }
```

ExtensionPolicy 结构体（行 ~2140-2175）：

```rust
pub struct ExtensionPolicy {
    pub mode: ExtensionPolicyMode,           // Strict, Prompt, Permissive
    pub max_memory_mb: u32,
    pub default_caps: Vec<String>,           // 默认允许的 capability
    pub deny_caps: Vec<String>,             // 始终拒绝（默认: exec, env）
    pub per_extension: HashMap<String, ExtensionOverride>,  // 每个扩展的覆盖
    pub exec_mediation: ExecMediationPolicy, // Stage 2: 命令级 mediation
    pub secret_broker: SecretBrokerPolicy,   // 敏感环境变量脱敏
}

impl Default for ExtensionPolicy {
    fn default() -> Self {
        Self {
            mode: ExtensionPolicyMode::Prompt,
            deny_caps: vec!["exec".to_string(), "env".to_string()],
            default_caps: vec!["read", "write", "http", "events", "session"],
            exec_mediation: ExecMediationPolicy::default(),
            // ...
        }
    }
}
```

#### 1.3 Stage 2: Command-Level Exec Mediation（evaluate_exec_mediation） {#_1-3-stage-2-command-level-exec-mediation-evaluate-exec-mediation}

位置：行 ~4331-4400

在 `exec` capability 被授予后，对实际命令进行分类审查：

```rust
pub fn evaluate_exec_mediation(
    policy: &ExecMediationPolicy,
    cmd: &str,
    args: &[String],
) -> ExecMediationResult {
    if !policy.enabled { return ExecMediationResult::Allow; }
    // 1. 检查显式 allow patterns（最高优先级）
    // 2. 检查显式 deny patterns
    // 3. 通过内置危险命令规则分类
    // 4. 若最高风险 tier >= deny_threshold → Deny
    // 5. 否则若 audit_all_classified → AllowWithAudit
}
```

危险命令分类（行 ~3855-3880）：

```rust
pub enum DangerousCommandClass {
    RecursiveDelete,           // rm -rf /
    DeviceWrite,              // dd, mkfs, fdisk
    ForkBomb,                 // :(){ :|:& };:
    PipeToShell,              // curl | sh, wget | bash
    SystemShutdown,           // shutdown, reboot
    PermissionEscalation,      // chmod 777
    ProcessTermination,       // kill -9 1
    CredentialFileModification, // /etc/passwd, /etc/shadow
    DiskWipe,                 // shred, wipefs
    ReverseShell,             // /dev/tcp/bash, nc -e
}

pub enum ExecRiskTier { Low, Medium, High, Critical }
```

ExecMediationPolicy 结构体（行 ~3935-3965）：

```rust
pub struct ExecMediationPolicy {
    pub enabled: bool,
    pub deny_threshold: ExecRiskTier,    // 默认: Critical
    pub deny_patterns: Vec<String>,     // 显式拒绝前缀
    pub allow_patterns: Vec<String>,   // 显式允许覆盖
    pub audit_all_classified: bool,
}
```

#### 1.4 ExtensionDispatcher 中的两阶段执行流 {#_1-4-extensiondispatcher-中的两阶段执行流}

位置：`src/extension_dispatcher.rs`（行 ~2795-2865）

```rust
async fn dispatch_hostcall(&self, payload: &HostCallPayload) -> HostcallOutcome {
    // === STAGE 1: Capability 检查 ===
    if let Some(cap) = required_capability_for_host_call_static(payload) {
        let check = self.policy.evaluate_for(cap, Some(&payload.extension_id));
        if check.decision != PolicyDecision::Allow {
            return HostcallOutcome::Error {
                code: "denied".to_string(),
                message: format!("Capability '{}' denied by policy ({})", cap, check.reason),
            };
        }
    }

    // === STAGE 2: Exec mediation（仅针对 exec 调用） ===
    if method == "exec" {
        let args: Vec<String> = /* 从 payload 提取 */;
        let mediation = evaluate_exec_mediation(&self.policy.exec_mediation, cmd, &args);
        match &mediation {
            ExecMediationResult::Deny { class, reason } => {
                return HostcallOutcome::Error { code: "denied", ... };
            }
            ExecMediationResult::AllowWithAudit { class, reason } => {
                // 记录日志但允许执行
            }
            ExecMediationResult::Allow => {}
        }
    }
    // ... 实际执行 ...
}
```

#### 1.5 ExtensionTrustState 生命周期 {#_1-5-extensiontruststate-生命周期}

位置：行 ~5998-6030

四状态信任生命周期：

```rust
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Hash)]
#[serde(rename_all = "snake_case")]
pub enum ExtensionTrustState {
    Pending,      // 已安装但用户未确认风险
    Acknowledged, // 用户确认风险，扩展以监控模式运行
    Trusted,      // 扩展长期表现安全
    Killed,       // 手动 kill-switch 或自动隔离
}

pub struct KillSwitchAuditEntry {
    pub ts_ms: i64,
    pub extension_id: String,
    pub activated: bool,
    pub reason: String,
    pub operator: String,
    pub previous_state: ExtensionTrustState,
    pub new_state: ExtensionTrustState,
}
```

#### 1.6 hashline_edit 工具 {#_1-6-hashline-edit-工具}

位置：`src/tools.rs`（行 ~7300-7722）

**输入 schema**（行 ~7323-7365）：

```rust
fn parameters(&self) -> serde_json::Value {
    serde_json::json!({
        "type": "object",
        "properties": {
            "path": { "type": "string" },
            "edits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "op": { "enum": ["replace", "prepend", "append"] },
                        "pos": { "type": "string", "description": "LINE#HASH anchor" },
                        "end": { "type": "string", "description": "End anchor for range" },
                        "lines": { /* 替换内容 */ }
                    }
                }
            }
        }
    })
}
```

**关键实现细节：**

1. **哈希验证在修改前执行**（行 ~7446-7452）：若文件内容哈希与 anchor 不匹配，直接报错，防止 stale edit

2. **自底向上编辑避免行号失效**（行 ~7581-7609）：
```rust
resolved.sort_by(|a, b| {
    b.start.cmp(&a.start)  // 从最高行号开始
        .then_with(|| op_precedence(a.op).cmp(&op_precedence(b.op)))
});
```

3. **重叠检测**（行 ~7588-7609）：检测到重叠编辑时拒绝执行

4. **原子写入通过临时文件**（行 ~7667-7700）：
```rust
let mut temp_file = tempfile::NamedTempFile::new_in(parent)?;
temp_file.as_file_mut().write_all(&final_content_bytes)?;
temp_file.as_file_mut().sync_all()?;
temp_file.persist(&absolute_path_clone)?;  // 全部写入后才 rename
```

**哈希格式**：行输出为 `N#AB:content`，其中 `AB` 是该行内容 SHA-256 哈希的前两个十六进制字符。例：`5#KJ:console.log("hello");`

---
