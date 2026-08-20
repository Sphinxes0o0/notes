---
title: "Pi Agent"
description: "**PI Agent** (π Agent) is a minimal, extensible terminal coding harness that adapts to your workflows rather than forcing you to change them. Originally created by Mario Zechner, it has grown into a…"
---
# Pi Agent

**PI Agent** (π Agent) is a minimal, extensible terminal coding harness that adapts to your workflows rather than forcing you to change them. Originally created by Mario Zechner, it has grown into a full-featured AI agent framework with multiple implementations and a rich ecosystem.

The core philosophy is to stay small at its core while being extensible through TypeScript extensions, skills, prompt templates, themes, and pi packages.

> **Note:** "PI" or "π" refers to multiple related but distinct projects — the original TypeScript/Node.js implementation and several forks/ports (notably a Rust version and oh-my-pi). This document covers the main implementations.

---

## Implementations

| Implementation | Language | Stars | Notes |
|----------------|----------|-------|-------|
| [earendil-works/pi](https://github.com/earendil-works/pi) | TypeScript/Node.js | 55.9k | Original/main implementation |
| [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi) | TypeScript/Rust/Bun | 7.6k | Fork with IDE wiring, LSP/DAP support |
| [Dicklesworthstone/pi_agent_rust](https://github.com/Dicklesworthstone/pi_agent_rust) | Rust | 1.1k | High-performance port, zero unsafe code |

---

## Architecture

### Core Packages (earendil-works/pi monorepo)

The main repository is a TypeScript monorepo with these key packages:

```bash
@earendil-works/pi-coding-agent  # Interactive CLI for the coding agent
@earendil-works/pi-agent-core   # Agent runtime with tool calling & state management
@earendil-works/pi-ai            # Unified multi-provider LLM API
@earendil-works/pi-tui           # Terminal UI library with differential rendering
```

**Architecture highlights:**
- TypeScript-first (93.4% of codebase)
- Supply-chain security via pinned dependencies, pre-commit validation, shrinkwrapped transitive deps
- Monorepo workspace structure with npm
- Built with standard practices: `npm install --ignore-scripts`, `npm run build`, `npm run check`

### oh-my-pi Architecture

Fork of the original Pi with a Rust core (~27k lines of Rust):

- **Dual kernels**: Persistent Python and Bun kernels for code execution that can call agent tools directly
- **In-process tools**: ripgrep, glob, find reimplemented natively (no subprocess overhead)
- **LSP integration**: Full Language Server Protocol support for diagnostics, navigation, symbols, renames, code actions
- **DAP support**: Debug Adapter Protocol for C, Go, Python debuggers
- **AST editing**: Hashline editing with content hashes as anchors to prevent stale edits

### pi_agent_rust Architecture

A Rust port focused on performance:

- **Single static binary** with sub-100ms startup and <50MB idle memory (~21MB binary)
- **asupersync**: Structured concurrency runtime with HTTP/TLS/SQLite
- **rich_rust**: Terminal UI library
- **Zero unsafe code**

---

## Key Features

### Common Features (All Implementations)

- **Multi-provider LLM support**: 40+ providers including Anthropic, OpenAI, Google Gemini, Groq, Ollama, OpenRouter, Azure
- **Multiple execution modes**: Interactive TUI, Print/JSON, RPC, SDK
- **Tree-structured history**: Navigate, branch, and share sessions
- **Context engineering**: AGENTS.md, SYSTEM.md, compaction, skills, dynamic context injection
- **Session persistence**: JSONL-based with branching support

### oh-my-pi-Specific Features

- **32 built-in tools** across categories: Files & Search, Runtime, Code Intelligence, Coordination, External, Memory
- **Subagent task fan-out**: Parallel work across isolated worktrees with schema-validated returns
- **Internal IPC**: Agent-to-agent communication within same process
- **Role-based model routing**: default, smol, slow, plan, commit roles with per-role fallback chains
- **Hindsight memory**: Project-specific facts retained across sessions
- **Browser automation**: Headless Chromium or CDP-attached Electron
- **Web search chaining**: 14 providers with site-specific extraction (GitHub, npm, PyPI, arxiv, Stack Overflow)
- **GitHub operations**: Issues, PRs, code search via gh CLI

### pi_agent_rust-Specific Features

- **8 built-in tools**: read, write, edit, hashline_edit, bash, grep, find, ls
- **Three execution modes**: Interactive (TUI), Print mode (stdout), RPC mode (stdin/stdout JSON)
- **JS/TS execution**: Embedded QuickJS runtime (no Node/Bun dependency needed)
- **Capability-based security**: Two-stage exec enforcement, per-extension trust lifecycle

---

## Customization Guide

### 1. Extensions (earendil-works/pi)

TypeScript modules that can add:
- **Tools**: New capabilities the agent can use
- **Commands**: Slash commands for the agent
- **Events**: Hook into agent lifecycle
- **Custom UI**: Terminal interface components

```bash
# Install extensions
npm install -g --ignore-scripts <extension-package>
```

### 2. Skills (earendil-works/pi)

Reusable on-demand agent capabilities triggered via slash commands.

### 3. Prompt Templates

Reusable prompts that expand from slash commands, allowing custom prompts for specific tasks.

### 4. Themes

Both built-in and custom terminal themes supported.

### 5. Pi Packages

Bundle and share extensions, skills, prompts, and themes together.

### 6. Custom Providers (earendil-works/pi)

Implement custom APIs and OAuth flows for new LLM providers.

### oh-my-pi Configuration

Configuration file: `~/.omp/agent/models.yml`

```yaml
# Model providers
providers:
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
  openai:
    api_key: ${OPENAI_API_KEY}

# Role-based routing
roles:
  default:
    model: claude-sonnet-4
  smol:
    model: claude-haiku-4
  slow:
    model: claude-opus-4
  plan:
    model: claude-opus-4
  commit:
    model: claude-sonnet-4

# Path-scoped role overrides
modelRoles:
  paths:
    "**/*.py":
      role: slow
    "**/planning/**":
      role: plan

# Fallback chains for quota handling
retry:
  fallbackChains:
    - [claude-opus-4, claude-sonnet-4, gpt-4o]

# Round-robin API key rotation
apiKeys:
  anthropic:
    - ${ANTHROPIC_API_KEY_1}
    - ${ANTHROPIC_API_KEY_2}
```

### Settings-Gated Tools (oh-my-pi)

Tools like `github`, `calc`, `inspect_image` can be activated per-project via settings.

### Tool Discovery (oh-my-pi)

BM25 search indexes tools mid-session when needed, discoverable via a hidden index.

---

## Code Examples

### Installation (earendil-works/pi)

```bash
# npm
npm install -g --ignore-scripts @earendil-works/pi-coding-agent

# Or installer script
curl -fsSL https://pi.dev/install.sh | sh
```

### Installation (pi_agent_rust)

```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/pi_agent_rust/main/install.sh" | bash

# Requires API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Installation (oh-my-pi)

```bash
# Shell script (macOS/Linux)
curl -fsSL https://raw.githubusercontent.com/can1357/oh-my-pi/main/install.sh | sh

# Or via bun
bun install -g oh-my-pi

# Or via mise
mise install oh-my-pi
```

### Programmatic Usage (earendil-works/pi)

```typescript
import { createAgent } from '@earendil-works/pi-agent-core';
import { createAI } from '@earendil-works/pi-ai';

const ai = createAI({
  provider: 'anthropic',
  model: 'claude-sonnet-4-20250514',
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const agent = createAgent({
  ai,
  tools: ['read', 'write', 'edit', 'bash', 'grep'],
});

const result = await agent.run('Fix the bug in main.ts');
console.log(result);
```

### RPC Mode Integration (pi_agent_rust)

Send JSON commands over stdin/stdout:

```json
{
  "jsonrpc": "2.0",
  "method": "execute",
  "params": {
    "prompt": "List all files in the current directory"
  },
  "id": 1
}
```

---

## Execution Modes

| Mode | Description |
|------|-------------|
| **Interactive (TUI)** | Default streaming terminal UI with autocomplete, session branching |
| **Print/JSON** | Single response to stdout, scriptable, structured events |
| **RPC** | JSON protocol over stdin/stdout for IDE integrations |
| **SDK** | Embed directly in Node.js applications |

---

## What PI Agent Does NOT Include

Intentionally omitted (build yourself via extensions or use third-party packages):

- Sub-agents
- MCP (Model Context Protocol) support
- Permission popups
- Plan mode
- To-do tracking
- Background bash

---

## Documentation & Resources

- **Official Docs**: [https://pi.dev](https://pi.dev)
- **Main GitHub**: [earendil-works/pi](https://github.com/earendil-works/pi)
- **oh-my-pi GitHub**: [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi)
- **pi_agent_rust GitHub**: [Dicklesworthstone/pi_agent_rust](https://github.com/Dicklesworthstone/pi_agent_rust)

---

## 原理剖析

> 本节深入分析 earendil-works/pi 源码，揭示核心架构设计。所有源码均来自 `/tmp/pi-repo/packages/`。

---

### 1. Agent 主循环与工具调用

#### 三层架构

pi-agent-core 由三层构成：

| 层 | 文件 | 职责 |
|----|------|------|
| **Agent** | `agent/src/agent.ts` | 高层状态机，`steer()` / `followUp()` 消息注入 |
| **runAgentLoop** | `agent/src/agent-loop.ts` | 低层循环，处理流式、工具执行、turn 管理 |
| **AgentHarness** | `agent/src/harness/agent-harness.ts` | 生产级 harness：session 持久化、hooks、skills |

#### 主循环（agent-loop.ts, 行 155-269）

核心是双层 `while` 循环：

```typescript
async function runLoop(initialContext, newMessages, initialConfig, signal, emit, streamFn?) {
  let currentContext = initialContext;
  let pendingMessages: AgentMessage[] = [];

  while (true) {                    // 外层：follow-up 消息到来时继续
    let hasMoreToolCalls = true;

    while (hasMoreToolCalls || pendingMessages.length > 0) {  // 内层：处理工具调用
      // 1. 处理 pending steering 消息
      if (pendingMessages.length > 0) { /* ... */ }

      // 2. 从 LLM 流式获取回复
      const message = await streamAssistantResponse(currentContext, config, signal, emit, streamFn);
      newMessages.push(message);

      // 3. 提取并执行工具调用
      const toolCalls = message.content.filter((c) => c.type === "toolCall");
      if (toolCalls.length > 0) {
        const executedToolBatch = await executeToolCalls(currentContext, message, config, signal, emit);
        hasMoreToolCalls = !executedToolBatch.terminate;
      }

      // 4. 检查是否该停止
      if (await config.shouldStopAfterTurn?.({...})) {
        await emit({ type: "agent_end", messages: newMessages });
        return;
      }

      // 5. 轮询 steering 消息
      pendingMessages = (await config.getSteeringMessages?.()) || [];
    }

    // 检查 follow-up 消息
    const followUpMessages = (await config.getFollowUpMessages?.()) || [];
    if (followUpMessages.length > 0) {
      pendingMessages = followUpMessages;
      continue;
    }
    break;
  }
  await emit({ type: "agent_end", messages: newMessages });
}
```

#### 工具执行流程（agent-loop.ts, 行 373-516）

工具执行分两种模式：**sequential** 和 **parallel**，由 `executionMode` 控制：

```typescript
// 工具定义接口（types.ts, 行 360-384）
export interface AgentTool<TParameters extends TSchema = TSchema, TDetails = any> extends Tool<TParameters> {
  label: string;
  prepareArguments?: (args: unknown) => Static<TParameters>;
  execute: (
    toolCallId: string,
    params: Static<TParameters>,
    signal?: AbortSignal,
    onUpdate?: AgentToolUpdateCallback<TDetails>,  // 流式更新回调
  ) => Promise<AgentToolResult<TDetails>>;
  executionMode?: ToolExecutionMode;  // "sequential" | "parallel"
}

// 准备 → 执行 → 终态 三阶段
async function prepareToolCall(...) -> Promise<PreparedToolCall | ImmediateToolCallOutcome> {
  // 1. 验证工具存在
  // 2. 验证参数（JSON Schema）
  // 3. 调用 beforeToolCall hook（可阻断！）
  if (config.beforeToolCall) {
    const beforeResult = await config.beforeToolCall({ assistantMessage, toolCall, args, context }, signal);
    if (beforeResult?.block) {
      return { kind: "immediate", result: createErrorToolResult(beforeResult.reason), isError: true };
    }
  }
  return { kind: "prepared", toolCall, tool, args: validatedArgs };
}

async function executePreparedToolCall(preparation, signal, emit) {
  const result = await prepared.tool.execute(
    prepared.toolCall.id,
    prepared.args,
    signal,
    (partialResult) => {
      // 通过 tool_execution_update 事件流式输出
      emit({ type: "tool_execution_update", toolCallId, toolName, args, partialResult });
    },
  );
  return { result, isError: false };
}
```

事件驱动的状态更新（agent-loop.ts, 行 509-556）：

```typescript
private async processEvents(event: AgentEvent): Promise<void> {
  switch (event.type) {
    case "message_start":
      this._state.streamingMessage = event.message;
      break;
    case "tool_execution_start":
      const pendingToolCalls = new Set(this._state.pendingToolCalls);
      pendingToolCalls.add(event.toolCallId);
      this._state.pendingToolCalls = pendingToolCalls;  // 替换引用触发响应式更新
      break;
    case "tool_execution_end":
      const pending = new Set(this._state.pendingToolCalls);
      pending.delete(event.toolCallId);
      this._state.pendingToolCalls = pending;
      break;
    // ...
  }
  // 广播给所有 listener
  for (const listener of this.listeners) {
    await listener(event, signal);
  }
}
```

---

### 2. pi-ai 统一 API：40+ Provider 的抽象

#### 核心设计：Provider Adapter Pattern

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

#### 统一入口（stream.ts）

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

#### Provider 示例：Anthropic

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

#### 统一事件协议

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

#### Model 类型抽象（types.ts）

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

#### 支持的 API 类型

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

### 3. Context Engineering

#### 3.1 Compaction 算法

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

#### 1.2 Stage 1: Capability-Level Policy（ExtensionPolicy::evaluate_for）

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

#### 1.3 Stage 2: Command-Level Exec Mediation（evaluate_exec_mediation）

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

#### 1.4 ExtensionDispatcher 中的两阶段执行流

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

#### 1.5 ExtensionTrustState 生命周期

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

#### 1.6 hashline_edit 工具

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

### 2. oh-my-pi Hashline 编辑机制（Content Hashes as Anchors）

#### 2.1 Hashline 格式

位置：`packages/hashline/src/format.ts`

每个 hunk 以 `¶PATH#HASH` 头部开始：

- `¶`（HL_FILE_PREFIX）标记 section 头部
- `HASH` 是文件内容的 **4 字符 xxHash32 截断**（LF 归一化后计算）
- 通过 `computeFileHash()` 计算（行 90）：

```typescript
export function computeFileHash(text: string): string {
  const normalized = normalizeFileHashText(text);
  const low16 = Bun.hash.xxHash32(normalized, 0) & 0xffff;
  return low16.toString(16).padStart(4, "0");
}
```

**Hunk 内操作**（format.ts 行 8-14）：

```typescript
export const HL_OP_INSERT_BEFORE = "↑";  // 插入到 LINE 之前
export const HL_OP_INSERT_AFTER = "↓";   // 插入到 LINE 之后
export const HL_OP_REPLACE = ":";         // 替换 A..B 行
export const HL_OP_DELETE = "!";          // 删除 A..B 行
```

#### 2.2 Stale Edit 检测

位置：`packages/hashline/src/patcher.ts`（行 311-342）

`#applyWithRecovery` 方法在应用前验证哈希：

```typescript
#applyWithRecovery(args): ApplyResult {
  const { section, canonicalPath, exists, normalized, edits, applyOptions } = args;
  const expected = exists ? section.fileHash : undefined;
  if (expected === undefined) return applyEdits(normalized, [...edits], applyOptions);

  const currentHash = computeFileHash(normalized);
  if (currentHash === expected) return applyEdits(normalized, [...edits], applyOptions);

  // 哈希不匹配 → 尝试恢复
  const recovered = this.recovery?.tryRecover({...});
  if (recovered) return recoveryToApplyResult(recovered);

  // 仍不匹配 → 抛出 MismatchError
  throw new MismatchError({
    path: section.path,
    expectedFileHash: expected,
    actualFileHash: currentHash,
    fileLines: normalized.split("\n"),
    anchorLines: section.collectAnchorLines(),
  });
}
```

#### 2.3 三路恢复机制

位置：`packages/hashline/src/recovery.ts`

当检测到哈希不匹配时，`Recovery` 类尝试三种策略：

1. **Full snapshot 三路合并**（行 148-157）：将编辑应用到缓存的 `fullText`，然后用 `Diff.applyPatch` 合并到当前内容
2. **Session chain replay**（行 155）：若 snapshot 不是 head 且行数匹配，直接重放到当前文本
3. **Sparse overlay 重建**（行 159-161）：从行映射重建文件，验证哈希，然后三路合并

```typescript
tryRecover(args: RecoveryArgs): RecoveryResult | null {
  const head = this.store.head(path);
  const snapshot = this.store.byHash(path, fileHash);

  if (snapshot.fullText !== undefined) {
    const merged = applyEditsToSnapshot(snapshot.fullText, currentText, edits, options, recoveryWarning);
    if (merged !== null) return merged;
    if (isSessionChain) return replaySessionChainOnCurrent(snapshot.fullText, currentText, edits, options);
    return null;
  }
  // 稀疏 snapshot 路径...
}
```

#### 2.4 Snapshot Store

位置：`packages/hashline/src/snapshots.ts`

`InMemorySnapshotStore` 维护每个路径的快照历史（每个路径最多 4 个快照，30 个路径 LRU）：

```typescript
export interface Snapshot {
  readonly lines: Map<number, string>;  // 1-indexed line → content
  fullText?: string;                     // 全文件读取
  fileHash?: string;                    // 4-hex 哈希
  recordedAt: number;
}

export class InMemorySnapshotStore extends SnapshotStore {
  readonly #snapshots: LRUCache<string, Snapshot[]>;

  head(path: string): Snapshot | null { ... }
  byHash(path: string, fileHash: string): Snapshot | null { ... }
  recordContiguous(path: string, startLine: number, lines: readonly string[], metadata?: SnapshotMetadata): void { ... }
}
```

Snapshot store 在 `ToolSession` 中接入（`src/edit/file-snapshot-store.ts` 行 19-21）：

```typescript
export function getFileSnapshotStore(session: ToolSession): InMemorySnapshotStore {
  if (!session.fileSnapshotStore) session.fileSnapshotStore = new InMemorySnapshotStore();
  return session.fileSnapshotStore;
}
```

---

### 3. oh-my-pi Tool Discovery（BM25 Search Mid-Session）

#### 3.1 Hidden Index 架构

位置：`packages/coding-agent/src/tool-discovery/tool-index.ts`

BM25 索引从 `DiscoverableTool` 描述符构建：

```typescript
export interface DiscoverableTool {
  name: string;
  label: string;
  summary: string;              // 简短 BM25 语料（描述前 200 字符）
  source: DiscoverableToolSource;  // "builtin" | "mcp" | "extension" | "custom"
  serverName?: string;          // 仅 MCP
  mcpToolName?: string;         // 仅 MCP
  schemaKeys: string[];
}

export interface DiscoverableToolSearchIndex {
  documents: DiscoverableToolSearchDocument[];
  averageLength: number;
  documentFrequencies: Map<string, number>;  // IDF 计算
}
```

#### 3.2 Field Weighting

位置：tool-index.ts 行 52-59

```typescript
const FIELD_WEIGHTS = {
  name: 6,       // 工具名最高权重
  label: 4,
  mcpToolName: 4,
  serverName: 2,
  summary: 2,
  schemaKey: 1,  // 参数名最低权重
} as const;
```

#### 3.3 Tokenization

位置：tool-index.ts 行 74-93

```typescript
function tokenize(value: string): string[] {
  return value
    .normalize("NFKD")
    .replace(/\p{M}+/gu, "")           // 去除组合标记（重音）
    .replace(/(\p{Lu}+)(\p{Lu}\p{Ll})/gu, "$1 $2")  // ACRONYM 边界
    .replace(/(\p{Ll}|\p{N})(\p{Lu})/gu, "$1 $2")    // camelCase
    .replace(/[^\p{L}\p{N}]+/gu, " ")  // 分隔符
    .toLowerCase()
    .trim()
    .split(/\s+/)
    .filter(token => token.length > 0);
}
```

#### 3.4 BM25 Scoring

位置：tool-index.ts 行 221-256

标准 BM25 公式配合 field weighting：

```typescript
const BM25_K1 = 1.2;
const BM25_B = 0.75;
const BM25_DELTA = 1.0;

export function searchDiscoverableTools(
  index: DiscoverableToolSearchIndex,
  query: string,
  limit: number,
): DiscoverableToolSearchResult[] {
  const queryTokens = tokenize(query);
  // ...
  return index.documents
    .map(document => {
      let score = 0;
      for (const [token, queryTermCount] of queryTermCounts) {
        const termFrequency = document.termFrequencies.get(token) ?? 0;
        if (termFrequency === 0) continue;
        const documentFrequency = index.documentFrequencies.get(token) ?? 0;
        const idf = Math.log(1 + (index.documents.length - documentFrequency + 0.5) / (documentFrequency + 0.5));
        const normalization = BM25_K1 * (1 - BM25_B + BM25_B * (document.length / index.averageLength));
        score += queryTermCount * idf * ((termFrequency * (BM25_K1 + 1)) / (termFrequency + normalization) + BM25_DELTA);
      }
      return { tool: document.tool, score };
    })
    .filter(result => result.score > 0)
    .sort((left, right) => right.score - left.score || left.tool.name.localeCompare(right.tool.name))
    .slice(0, limit);
}
```

#### 3.5 Discovery Mode 激活

位置：`packages/coding-agent/src/tools/search-tool-bm25.ts`（行 194-201）

通过 `tools.discoveryMode` 控制：

```typescript
static createIf(session: ToolSession): SearchToolBm25Tool | null {
  const toolsDiscoveryMode = session.settings.get("tools.discoveryMode");
  const active =
    (toolsDiscoveryMode !== undefined && toolsDiscoveryMode !== "off") ||
    session.settings.get("mcp.discoveryMode") === true;
  if (!active) return null;
  return supportsToolDiscoveryExecution(session) ? new SearchToolBm25Tool(session) : null;
}
```

索引在 `ToolSession` 上懒构建并缓存：

```typescript
function getDiscoverableToolSearchIndexForExecution(session: ToolSession): DiscoverableToolSearchIndex {
  try {
    const cached = session.getDiscoverableToolSearchIndex?.();
    if (cached) return cached;
  } catch {}
  return buildDiscoverableToolSearchIndex(getDiscoverableToolsForDescription(session));
}
```

---

### 4. oh-my-pi LSP/DAP Integration

#### 4.1 LSP Client 架构

位置：`packages/coding-agent/src/lsp/client.ts`

通过自定义帧协议在 stdio 上传输 JSON-RPC 消息：

```typescript
// 消息解析（行 179-216）
function parseMessage(buffer: Buffer): { message: LspJsonRpcResponse | LspJsonRpcNotification; remaining: Buffer } | null {
  const headerEndIndex = findHeaderEnd(buffer);  // 查找 \r\n\r\n
  const headerText = new TextDecoder().decode(buffer.slice(0, headerEndIndex));
  const contentLengthMatch = headerText.match(/Content-Length: (\d+)/i);
  const contentLength = Number.parseInt(contentLengthMatch[1], 10);
  // ... 在 header 后读取恰好 contentLength 字节
}

// 消息写入（行 218-225）
async function writeMessage(sink: Bun.FileSink, message: LspJsonRpcRequest | ...): Promise<void> {
  const content = JSON.stringify(message);
  sink.write(`Content-Length: ${Buffer.byteLength(content, "utf-8")}\r\n\r\n${content}`);
  await sink.flush();
}
```

#### 4.2 LSP Server Lifecycle

位置：`packages/coding-agent/src/lsp/client.ts`（行 424-558）

```typescript
export async function getOrCreateClient(config: ServerConfig, cwd: string, initTimeoutMs?: number): Promise<LspClient> {
  const key = `${config.command}:${cwd}`;

  // 如支持则用 lspmux 包装器
  const { command, args, env } = isLspmuxSupported(baseCommand)
    ? await getLspmuxCommand(baseCommand, baseArgs)
    : { command: baseCommand, args: baseArgs };

  const proc = ptree.spawn([command, ...args], { cwd, stdin: "pipe", env });

  // Initialize handshake
  const initResult = await sendRequest(client, "initialize", {
    processId: process.pid,
    rootUri: fileToUri(cwd),
    rootPath: cwd,
    capabilities: CLIENT_CAPABILITIES,
    initializationOptions: config.initOptions ?? {},
    workspaceFolders: [{ uri: fileToUri(cwd), name: cwd.split("/").pop() ?? "workspace" }],
  });

  await sendNotification(client, "initialized", {});
  return client;
}
```

#### 4.3 Client Capabilities

位置：`packages/coding-agent/src/lsp/client.ts`（行 67-169）

```typescript
const CLIENT_CAPABILITIES = {
  textDocument: {
    synchronization: { didSave: true, dynamicRegistration: false },
    hover: { contentFormat: ["markdown", "plaintext"] },
    definition: { dynamicRegistration: false, linkSupport: true },
    typeDefinition: { dynamicRegistration: false, linkSupport: true },
    implementation: { dynamicRegistration: false, linkSupport: true },
    references: { dynamicRegistration: false },
    documentSymbol: { hierarchicalDocumentSymbolSupport: true, symbolKind: {...} },
    rename: { prepareSupport: true },
    codeAction: { resolveSupport: { properties: ["edit"] } },
    formatting: { dynamicRegistration: false },
    rangeFormatting: { dynamicRegistration: false },
    publishDiagnostics: { relatedInformation: true, versionSupport: true, tagSupport: { valueSet: [1, 2] } },
  },
  window: { workDoneProgress: true },
  workspace: {
    applyEdit: true,
    workspaceEdit: { documentChanges: true, failureHandling: "textOnlyTransactional" },
    configuration: true,
    fileOperations: { willRename: true, didRename: true },
  },
  experimental: { snippetTextEdit: true },
};
```

#### 4.4 Diagnostics 处理

位置：`packages/coding-agent/src/lsp/index.ts`（行 432-485）

轮询诊断直到版本更新：

```typescript
async function waitForDiagnostics(
  client: LspClient,
  uri: string,
  options: WaitForDiagnosticsOptions = {},
): Promise<Diagnostic[]> {
  const { timeoutMs = 3000, signal, minVersion, expectedDocumentVersion, allowUnversioned = true } = options;
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    throwIfAborted(signal);
    const versionOk = minVersion === undefined || client.diagnosticsVersion > minVersion;
    const diagnostics = getAcceptedDiagnostics(client.diagnostics.get(uri), expectedDocumentVersion, allowUnversioned);
    if (diagnostics !== undefined && versionOk) return diagnostics;
    await Bun.sleep(100);
  }
  // ...
}
```

#### 4.5 LSP Tool Actions

位置：`packages/coding-agent/src/lsp/index.ts`（行 1991-2292）

`LspTool` 处理以下 action：

| Action | 说明 |
|--------|------|
| `definition` | 转到定义 |
| `type_definition` | 转到类型定义 |
| `implementation` | 转到实现 |
| `references` | 查找引用（含项目感知服务器重试逻辑）|
| `hover` | 悬停信息 |
| `code_actions` | LSP 代码动作（含 apply 支持）|
| `symbols` | 文档和工作区符号 |
| `rename` | 符号重命名 |
| `rename_file` | 通过 `workspace/willRenameFiles` 重命名文件 |
| `diagnostics` | 获取诊断（逐文件或 `*` 工作区）|
| `status` | 服务器状态 |
| `capabilities` | 服务器能力 |
| `request` | 原始 LSP 方法调用 |
| `reload` | 服务器重载 |

#### 4.6 DAP Client 架构

位置：`packages/coding-agent/src/dap/client.ts`

DAP 使用相同的 JSON-RPC 帧协议，但支持 stdio 和 socket 两种传输方式：

```typescript
export class DapClient {
  static async spawn({ adapter, cwd }: DapSpawnOptions): Promise<DapClient> {
    if (adapter.connectMode === "socket") {
      return DapClient.#spawnSocket({ adapter, cwd });
    }
    const proc = ptree.spawn([adapter.resolvedCommand, ...adapter.args], {
      cwd, stdin: "pipe", env, detached: true,  // detached = setsid 无控制 TTY
    });
    // ...
  }
}

**Socket 模式**支持（如 `dlv`）：Linux 上用 Unix domain socket `--listen=unix:<path>`，macOS 上用 TCP listener `--client-addr=127.0.0.1:<port>`

#### 4.7 DAP Session 管理

位置：`packages/coding-agent/src/dap/session.ts`

Session 追踪断点、线程、栈帧和输出：

```typescript
interface DapSession {
  id: string;
  adapter: DapResolvedAdapter;
  cwd: string;
  client: DapClient;
  status: DapSessionStatus;  // "launching" | "configuring" | "stopped" | "running" | "terminated"
  breakpoints: Map<string, DapBreakpointRecord[]>;
  threads: DapThread[];
  lastStackFrames: DapStackFrame[];
  output: string;
  stop: DapStopLocation;
}
```

---

### 5. 关键文件索引

| 组件 | 关键文件 |
|------|---------|
| **pi_agent_rust 两阶段 enforcement** | `src/extensions.rs` (~2010, 4331-4400, 9933, 10050-10145), `src/extension_dispatcher.rs` (~2795-2865) |
| **pi_agent_rust hashline_edit** | `src/tools.rs` (~7300-7722) |
| **oh-my-pi hashline** | `packages/hashline/src/{format,patcher,recovery,snapshots}.ts` |
| **oh-my-pi BM25 tool discovery** | `packages/coding-agent/src/tool-discovery/tool-index.ts`, `src/tools/search-tool-bm25.ts` |
| **oh-my-pi LSP** | `packages/coding-agent/src/lsp/{client,index}.ts` |
| **oh-my-pi DAP** | `packages/coding-agent/src/dap/{client,session}.ts` |
## 定制深化

### 1. 自定义扩展完整示例 (TypeScript)

以下是一个完整的 PI Agent 扩展，实现一个带生命周期管理的自定义工具——文件内容校验和计算器。

```typescript
// my-checksum-extension/src/index.ts
import type {
  Extension,
  Tool,
  ToolContext,
  LifecycleHook,
  LifecycleHooks,
} from '@earendil-works/pi-agent-core';
import crypto from 'crypto';
import fs from 'fs/promises';

// --- Tool Definition ---

interface ChecksumResult {
  file: string;
  algorithm: string;
  hash: string;
  bytes: number;
}

interface ChecksumParams {
  path: string;
  algorithm?: 'sha256' | 'sha512' | 'md5';
}

const checksumTool: Tool<ChecksumParams, ChecksumResult> = {
  name: 'checksum',
  description: 'Compute a cryptographic checksum of a file',

  // JSON Schema for parameter validation
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'Absolute path to the file' },
      algorithm: {
        type: 'string',
        enum: ['sha256', 'sha512', 'md5'],
        default: 'sha256',
        description: 'Hash algorithm to use',
      },
    },
    required: ['path'],
  },

  // Lifecycle: called once when extension loads
  onLoad?: async (ctx: ToolContext) => {
    console.log('[checksum] extension loaded');
    ctx.registerConfig({
      algorithm: { type: 'string', default: 'sha256' },
    });
  },

  // Lifecycle: called before each invocation
  async beforeInvoke(params: ChecksumParams): Promise<void> {
    const stat = await fs.stat(params.path).catch(() => null);
    if (!stat) throw new Error(`File not found: ${params.path}`);
    if (!stat.isFile()) throw new Error(`Not a file: ${params.path}`);
  },

  // Core execution
  async execute(params: ChecksumParams, ctx: ToolContext): Promise<ChecksumResult> {
    const algorithm = params.algorithm ?? ctx.getConfig?.('algorithm') ?? 'sha256';
    const fileBuffer = await fs.readFile(params.path);
    const hash = crypto.createHash(algorithm).update(fileBuffer).digest('hex');

    return {
      file: params.path,
      algorithm,
      hash,
      bytes: fileBuffer.length,
    };
  },

  // Lifecycle: called after successful execution
  async afterInvoke?(result: ChecksumResult): Promise<void> {
    ctx.getLog?.().info(`[checksum] ${result.algorithm} = ${result.hash}`);
  },

  // Lifecycle: called on extension unload
  onUnload?: () => void | Promise<void> {
    console.log('[checksum] extension unloaded');
  },
};

// --- Extension Entry Point ---

const extension: Extension = {
  name: 'my-checksum',
  version: '1.0.0',
  tools: [checksumTool],

  // Lifecycle hooks
  hooks: {
    onAgentStart: async (ctx) => {
      ctx.getLog?.().info('[checksum] agent started');
    },
    onToolCall: async (toolName, params, result) => {
      if (toolName === 'checksum') {
        ctx.getLog?.().debug(`[checksum] called with params:`, params);
      }
    },
    onAgentEnd: async () => {
      console.log('[checksum] agent session ended');
    },
  } satisfies Partial<LifecycleHooks>,

  // Optional: declare dependencies
  dependencies: [],

  // Optional: capability declarations for sandboxing
  capabilities: ['fs:read', 'crypto'],
};

export default extension;

// --- Package manifest (package.json) ---
// {
//   "name": "my-checksum-extension",
//   "main": "dist/index.js",
//   "type": "module",
//   "peerDependencies": {
//     "@earendil-works/pi-agent-core": "^2.x"
//   }
// }
```

**生命周期时序:**

```
Extension Load
    │
    ▼
onLoad() → registerConfig()
    │
    ▼
Agent Start → onAgentStart()
    │
    ▼
Tool Call ──→ beforeInvoke() ──→ execute() ──→ afterInvoke()
    │                                     │
    └───────── error ─────────────────────┘
    │
    ▼
onToolCall() hook (per call)
    │
    ▼
Agent End → onAgentEnd()
    │
    ▼
onUnload()
```

**安装与使用:**

```bash
npm install -g --ignore-scripts my-checksum-extension
# 或本地开发
npm link  # 在扩展目录中运行
pi-agent  # 启动交互模式
```bash

Agent 内调用: `checksum { "path": "/etc/hosts", "algorithm": "sha256" }`

---

### 2. 自定义 Provider 实现

添加一个新的 LLM Provider——以 Cloudflare Workers AI 为例。

```typescript
// providers/cloudflare-ai.ts
import {
  createProvider,
  type Provider,
  type ChatMessage,
  type ChatCompletionResponse,
  type StreamChunk,
} from '@earendil-works/pi-ai';

interface CloudflareAIConfig {
  accountId: string;
  apiKey: string;
  baseUrl?: string; // 默认 https://api.cloudflare.com/client/v4
}

interface CloudflareAIResponse {
  result: {
    response: string;
    metadata?: {
      tokensUsed?: number;
      model?: string;
    };
  };
  success: boolean;
  errors?: string[];
}

// Provider 实现
export const cloudflareAIProvider: Provider<CloudflareAIConfig> = {
  name: 'cloudflare-ai',
  displayName: 'Cloudflare Workers AI',

  // 支持的模型列表
  models: [
    { id: '@cf/meta/llama-3-8b-instruct', name: 'Llama 3 8B' },
    { id: '@cf/meta/llama-3-70b-instruct', name: 'Llama 3 70B' },
    { id: '@cf/google/gemma-7b-instruct', name: 'Gemma 7B' },
    { id: '@cf/mistral/mistral-7b-instruct-v0.1', name: 'Mistral 7B' },
    { id: '@cf/openchat/openchat-7b-v3.1', name: 'OpenChat 7B' },
  ],

  // 默认模型
  defaultModel: '@cf/meta/llama-3-8b-instruct',

  // OAuth / API Key 认证方式
  auth: {
    type: 'api-key',
    header: 'Authorization',
    prefix: 'Bearer',
    envVar: 'CLOUDFLARE_API_KEY',
  },

  // 构建请求
  buildRequest: (config: CloudflareAIConfig, model: string, messages: ChatMessage[]) => {
    const url = `https://api.cloudflare.com/client/v4/accounts/${config.accountId}/ai/${model}`;
    return {
      url,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: {
        messages: messages.map(m => ({
          role: m.role,
          content: m.content,
        })),
        // Cloudflare 特定参数
        stream: false,
        max_tokens: 4096,
      },
    };
  },

  // 解析响应
  parseResponse: (response: CloudflareAIResponse): ChatCompletionResponse => {
    if (!response.success) {
      throw new Error(`Cloudflare AI error: ${response.errors?.join(', ')}`);
    }
    return {
      content: response.result.response,
      model: response.result.metadata?.model ?? 'unknown',
      usage: {
        inputTokens: 0, // Cloudflare 不总是返回 token 数
        outputTokens: response.result.metadata?.tokensUsed ?? 0,
      },
      finishReason: 'stop',
    };
  },

  // 流式响应解析 (SSE 格式)
  parseStreamChunk: (chunk: string): StreamChunk | null => {
    // Cloudflare SSE 格式: data: {"response":"Hello"}
    if (!chunk.startsWith('data: ')) return null;
    try {
      const data = JSON.parse(chunk.slice(6));
      return {
        delta: data.response ?? '',
        done: false,
      };
    } catch {
      return null;
    }
  },

  // 错误处理映射
  errorMap: {
    401: 'Invalid Cloudflare API key',
    403: 'Account ID or permissions error',
    429: 'Rate limited — try a smaller model or wait',
    500: 'Cloudflare AI service error',
    503: 'Cloudflare AI temporarily unavailable',
  },
};

// 注册 Provider
export function registerCloudflareAI() {
  return createProvider(cloudflareAIProvider);
}

// 使用示例:
// const ai = createAI({
//   provider: 'cloudflare-ai',
//   model: '@cf/meta/llama-3-8b-instruct',
//   config: {
//     accountId: process.env.CLOUDFLARE_ACCOUNT_ID!,
//     apiKey: process.env.CLOUDFLARE_API_KEY!,
//   },
// });
```

**Provider 注册流程:**

```typescript
// 在你的扩展或配置中注册
import { registerProvider } from '@earendil-works/pi-ai';

registerProvider('cloudflare-ai', cloudflareAIProvider);

// 模型选择通过 config
const ai = createAI({
  provider: 'cloudflare-ai',
  model: '@cf/google/gemma-7b-instruct',
  config: {
    accountId: 'your-account-id',
    apiKey: 'your-api-key',
  },
});
```

---

### 3. oh-my-pi 双内核架构 (Rust + Bun)

oh-my-pi 的核心创新是同时运行两个持久化内核——Python 和 Bun——它们可以**直接调用 Agent 工具**，无需进程间通信开销。

#### 架构概览

```
┌─────────────────────────────────────────────────────┐
│                    oh-my-pi Core (Rust)              │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Agent   │  │  Tool    │  │   Kernel Manager │  │
│  │  Engine  │──│  Registry│──│                   │  │
│  └──────────┘  └──────────┘  └────────┬─────────┘  │
│                                       │             │
│                    IPC (mpsc channel) │             │
│                                ┌──────┴──────┐      │
│                                │             │      │
│                     ┌──────────▼──┐  ┌──────▼────┐  │
│                     │ Python Kernel│  │ Bun Kernel │  │
│                     │  (PyO3/mijo) │  │  (Bun API) │  │
│                     └──────┬───────┘  └──────┬─────┘  │
│                            │                 │        │
│                     ┌──────▼─────────────────▼────┐  │
│                     │   Tool Calling Bridge        │  │
│                     │  (kernel.invoke_tool)        │  │
│                     └─────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

#### 内核工具调用协议

每个内核通过 Rust 提供的 `invoke_tool` FFI 绑定调用 Agent 工具：

```rust
// src/kernel/mod.rs

// 内核调用工具的通用接口
pub trait KernelBridge {
    fn invoke_tool(
        &self,
        tool_name: &str,
        params: serde_json::Value,
    ) -> impl Future<Output = Result<serde_json::Value, KernelError>> + Send;
}

// Python 内核实现 (使用 PyO3)
pub struct PythonKernel {
    interpreter: PythonInterpreter,
    tool_bridge: ToolBridge,
}

impl KernelBridge for PythonKernel {
    async fn invoke_tool(
        &self,
        tool_name: &str,
        params: serde_json::Value,
    ) -> Result<serde_json::Value, KernelError> {
        // 获取工具元数据
        let tool_meta = self.tool_bridge.get_tool_meta(tool_name)?;
        
        // 在 Python 侧执行工具
        let result = self.interpreter
            .call(
                "agent",
                "invoke_tool",
                (tool_name, params, tool_meta),
            )
            .await?;
        
        Ok(result)
    }
}

// Bun 内核实现 (使用 NAPI)
pub struct BunKernel {
    napi_env: NapiEnv,
    tool_bridge: ToolBridge,
}

impl KernelBridge for BunKernel {
    async fn invoke_tool(
        &self,
        tool_name: &str,
        params: serde_json::Value,
    ) -> Result<serde_json::Value, KernelError> {
        let promise = self.napi_env
            .call_async("agent", "invokeTool", tool_name, params)?;
        
        promise.await
    }
}
```

#### Python 内核中的工具调用

```python
# python/agent.py
import asyncio
import json
from typing import Any

class AgentBridge:
    """Python 内核调用的桥梁"""
    
    def __init__(self, kernel):
        self.kernel = kernel  # PyO3 Rust 绑定
        self._tool_registry: dict[str, callable] = {}
    
    def register_tool(self, name: str, handler: callable):
        self._tool_registry[name] = handler
    
    async def invoke_tool(self, tool_name: str, params: dict, meta: dict) -> Any:
        """由 Rust 内核调用此方法，再转发给实际工具"""
        if tool_name not in self._tool_registry:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        handler = self._tool_registry[tool_name]
        
        # 支持异步工具
        if asyncio.iscoroutinefunction(handler):
            return await handler(**params)
        return handler(**params)

# 内置 ripgrep 工具 (Python 实现)
async def grep(path: str, pattern: str, context: int = 3, 
               case_sensitive: bool = False) -> list[dict]:
    """内置 ripgrep，通过 Rust 侧重定向到 subprocess 或 native 实现"""
    result = await AgentBridge.instance().kernel.rpc(
        "tool://grep",
        path=path,
        pattern=pattern,
        context=context,
        case_sensitive=case_sensitive
    )
    return result

# 注册工具
agent_bridge.register_tool("grep", grep)
```

#### Bun 内核中的工具调用

```typescript
// bun/kernel/agent.ts

// Bun 内核通过 NAPI 调用 Rust 工具
const rust = require('oh_my_pi_native') as typeof import('oh-my-pi-native');

class AgentBridge {
  private static instance: AgentBridge;
  
  private constructor() {}
  
  static getInstance(): AgentBridge {
    if (!AgentBridge.instance) {
      AgentBridge.instance = new AgentBridge();
    }
    return AgentBridge.instance;
  }
  
  // 调用注册的工具
  async invokeTool(toolName: string, params: Record<string, unknown>): Promise<unknown> {
    const tool = this.getTool(toolName);
    if (!tool) {
      throw new Error(`Tool not found: ${toolName}`);
    }
    return tool.handler(params);
  }
  
  // 内置 glob 工具 (Bun 实现)
  async glob(pattern: string, cwd: string = process.cwd()): Promise<string[]> {
    // Bun.glob 是原生实现，比 Node glob 快 10x
    return Array.from(
      new Bun.Glob(pattern).scanSync({ cwd, onlyFiles: true })
    );
  }
  
  // 内置文件读写 (直接调用 Rust 而非 Bun 原生)
  async readFile(path: string): Promise<string> {
    return rust.fs.readFile(path, 'utf-8');
  }
  
  async writeFile(path: string, content: string): Promise<void> {
    return rust.fs.writeFile(path, content);
  }
}

// 导出供 Rust NAPI 调用
(globalThis as any).agentBridge = AgentBridge.getInstance();
```

#### 内核间通信

```rust
// src/ipc/mod.rs

use tokio::sync::mpsc;

// 内核间消息格式
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
#[serde(tag = "type", content = "payload")]
pub enum KernelMessage {
    // Python -> Bun
    PythonExec { code: String, id: u64 },
    PythonResult { id: u64, result: serde_json::Value },
    
    // Bun -> Python  
    BunExec { code: String, id: u64 },
    BunResult { id: u64, result: serde_json::Value },
    
    // 工具调用转发
    ToolCall { from: KernelId, tool: String, params: serde_json::Value },
    ToolResult { to: KernelId, id: u64, result: serde_json::Value },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum KernelId {
    Python,
    Bun,
    Rust,  // 主控 Rust 进程
}

// IPC 通道
pub struct IpcChannel {
    sender: mpsc::Sender<KernelMessage>,
    receiver: mpsc::Receiver<KernelMessage>,
}

impl IpcChannel {
    pub fn new(capacity: usize) -> (Self, Self) {
        let (tx1, rx2) = mpsc::channel(capacity);
        let (tx2, rx1) = mpsc::channel(capacity);
        (Self { sender: tx1, receiver: rx1 }, Self { sender: tx2, receiver: rx2 })
    }
    
    pub async fn send(&self, msg: KernelMessage) {
        self.sender.send(msg).await.expect("channel closed");
    }
    
    pub async fn recv(&mut self) -> Option<KernelMessage> {
        self.receiver.recv().await
    }
}
```

**关键设计决策:**

| 方面 | 决策 | 原因 |
|------|------|------|
| 持久化内核 | Python/Bun 常驻内存 | 避免冷启动开销，Python 库初始化慢 |
| 工具调用 | Rust 作为仲裁者 | 内核本身不可信，防止注入攻击 |
| 原生重实现 | ripgrep/glob 等用 Rust 重写 | subprocess 启动 5-50ms，native <1ms |
| AST 编辑 | Hashline 锚定 | 并发编辑时防止行号错位 |

---

### 4. Subagent Task Fan-out 机制

oh-my-pi 支持将任务**并行分发给多个独立子代理**，每个子代理在隔离的 Git Worktree 中运行，结果通过 Schema 验证合并。

#### 核心 API

```typescript
// src/coordination/fanout.ts

interface FanoutTask<T> {
  id: string;
  description: string;
  prompt: string;
  tools?: string[];           // 允许的工具白名单
  worktree?: string;          // Git worktree 路径，默认自动创建
  model?: string;             // 可选的模型覆盖
  timeout?: number;          // 超时 ms，默认 5 分钟
  schema?: z.ZodType<T>;      // 返回值 Schema
}

interface FanoutResult<T> {
  taskId: string;
  success: boolean;
  result?: T;
  error?: string;
  duration: number;
  tokensUsed?: number;
}

interface FanoutOptions {
  parallelism?: number;      // 最大并发数，默认 4
  stopOnError?: boolean;     // 一个失败则全部取消，默认 false
  merge?: 'all' | 'successful' | 'first';
}

// 主调度器
class TaskFanout {
  constructor(
    private agent: Agent,           // 主代理引用
    private executor: Executor,      // 子代理执行器
    private validator: Validator,    // Schema 验证器
  ) {}

  async fanout<T>(
    tasks: FanoutTask<T>[],
    options: FanoutOptions = {}
  ): Promise<FanoutResult<T>[]> {
    const {
      parallelism = 4,
      stopOnError = false,
      merge = 'successful',
    } = options;

    // 1. 准备 worktrees
    const preparedTasks = await this.prepareTasks(tasks);

    // 2. 创建任务队列 (信号量控制并发)
    const semaphore = new Semaphore(parallelism);
    const results: FanoutResult<T>[] = [];
    const errors: Error[] = [];

    // 3. 并行执行
    const promises = preparedTasks.map(async (task) => {
      await semaphore.acquire();
      try {
        return await this.executeTask<T>(task);
      } finally {
        semaphore.release();
      }
    });

    // 4. 收集结果
    const settled = await Promise.allSettled(promises);
    
    for (let i = 0; i < settled.length; i++) {
      const outcome = settled[i];
      if (outcome.status === 'fulfilled') {
        results.push(outcome.value);
      } else {
        if (stopOnError) {
          await this.cancelRemaining(preparedTasks.slice(i));
          throw new Error(`Task ${i} failed: ${outcome.reason}`);
        }
        results.push({
          taskId: tasks[i].id,
          success: false,
          error: outcome.reason?.message ?? 'Unknown error',
          duration: 0,
        });
      }
    }

    // 5. 合并结果
    return this.mergeResults(results, merge);
  }

  private async executeTask<T>(task: PreparedTask): Promise<FanoutResult<T>> {
    const start = Date.now();
    const subagent = this.executor.createSubagent({
      worktree: task.worktree,
      tools: task.tools,
      model: task.model,
      systemPrompt: task.systemPrompt,
    });

    const stream = await subagent.run(task.prompt);
    let fullResponse = '';

    for await (const chunk of stream) {
      fullResponse += chunk;
    }

    // Schema 验证
    let parsed: T | undefined;
    let error: string | undefined;

    if (task.schema) {
      try {
        parsed = this.validator.parse(fullResponse, task.schema);
      } catch (e) {
        error = `Schema validation failed: ${e.message}`;
      }
    } else {
      parsed = fullResponse as unknown as T;
    }

    return {
      taskId: task.id,
      success: !error,
      result: parsed,
      error,
      duration: Date.now() - start,
      tokensUsed: subagent.lastUsage?.total_tokens,
    };
  }

  private async prepareTasks<T>(tasks: FanoutTask<T>[]): Promise<PreparedTask[]> {
    return Promise.all(tasks.map(async (task) => {
      // 为每个任务创建独立的 Git worktree
      const worktree = task.worktree ?? await this.createWorktree(task.id);
      return {
        ...task,
        worktree,
        systemPrompt: this.buildSystemPrompt(task),
      };
    }));
  }

  private async createWorktree(id: string): Promise<string> {
    const branchName = `pi-fanout-${id}-${Date.now()}`;
    const worktreePath = path.join(
      process.env.PI_FANOUT_DIR ?? '/tmp/pi-fanout',
      id
    );

    // git worktree add <path> <branch>
    await this.agent.exec('git', ['worktree', 'add', worktreePath, '-b', branchName]);
    
    return worktreePath;
  }
}
```

#### Schema 验证的返回类型示例

```typescript
import { z } from 'zod';

// 定义子任务返回 Schema
const FileAnalysisSchema = z.object({
  file: z.string(),
  linesOfCode: z.number(),
  complexity: z.enum(['low', 'medium', 'high']),
  issues: z.array(z.object({
    line: z.number(),
    severity: z.enum(['error', 'warning', 'info']),
    message: z.string(),
  })),
  summary: z.string().max(200),
});

// 使用 fan-out
const results = await fanout.fanout([
  {
    id: 'analyze-auth',
    description: 'Analyze authentication module',
    prompt: 'Analyze /src/auth/* files. Return JSON with structure defined by the schema.',
    tools: ['read', 'grep', 'bash'],
    schema: FileAnalysisSchema,
    worktree: '/project/main',
  },
  {
    id: 'analyze-api',
    description: 'Analyze API layer',
    prompt: 'Analyze /src/api/* files. Return JSON with structure defined by the schema.',
    tools: ['read', 'grep', 'bash'],
    schema: FileAnalysisSchema,
    worktree: '/project/main',
  },
  {
    id: 'analyze-db',
    description: 'Analyze database layer',
    prompt: 'Analyze /src/db/* files. Return JSON with structure defined by the schema.',
    tools: ['read', 'grep', 'bash'],
    schema: FileAnalysisSchema,
    worktree: '/project/main',
  },
], {
  parallelism: 3,
  merge: 'all',
});

// 类型安全的结果
for (const r of results) {
  if (r.success && r.result) {
    const analysis: z.infer<typeof FileAnalysisSchema> = r.result;
    console.log(`${analysis.file}: ${analysis.linesOfCode} LOC, ${analysis.issues.length} issues`);
  }
}
```

#### Worktree 隔离机制

```rust
// src/coordination/worktree.rs

pub struct WorktreeManager {
    repo_path: PathBuf,
    worktrees: HashMap<String, WorktreeHandle>,
    base_branch: String,
}

pub struct WorktreeHandle {
    path: PathBuf,
    branch: String,
    _guard: WorktreeGuard,  // Drop 时清理
}

impl WorktreeManager {
    pub async fn create(&self, id: &str) -> Result<WorktreeHandle> {
        let branch = format!("pi-fanout-{}-{}", id, uuid::Uuid::new_v4());
        let path = self.repo_path.join(".git").join("worktrees").join(id);
        
        // git worktree add <path> -b <branch>
        self.run_git(&[
            "worktree", "add",
            path.as_os_str(),
            "-b", branch.as_str(),
        ]).await?;
        
        Ok(WorktreeHandle {
            path,
            branch,
            _guard: WorktreeGuard { id: id.to_string(), manager: self },
        })
    }
}

impl Drop for WorktreeGuard {
    fn drop(&mut self) {
        // 清理 worktree (可选：保留供后续检查)
        if let Ok(worktrees) = self.manager.list() {
            if let Some(wt) = worktrees.get(&self.id) {
                // git worktree remove <path>
                self.manager.run_git(&["worktree", "remove", wt.path.as_os_str()]).ok();
                // git branch -D <branch>
                self.manager.run_git(&["branch", "-D", &wt.branch]).ok();
            }
        }
    }
}
```

**Fan-out 典型用例:**

| 场景 | 分发数 | 说明 |
|------|--------|------|
| 并行文件搜索 | N×路径 | 每个路径一个子代理，结果合并 |
| 跨多个仓库扫描 | N×仓库 | Git worktree 隔离 |
| 大文件分段分析 | N×区块 | 行范围切分，并行解析 |
| 多语言代码审查 | N×语言 | 每个语言独立分析流 |
| PR 分支对比 | N×分支 | 每个分支独立审查后汇总 |

---

## License

MIT License

---

