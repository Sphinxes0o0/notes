---
title: "Implementations"
---

# Implementations {#chapter}

[返回总目录](../pi-agent)

## Implementations {#implementations}

| Implementation | Language | Stars | Notes |
|----------------|----------|-------|-------|
| [earendil-works/pi](https://github.com/earendil-works/pi) | TypeScript/Node.js | 55.9k | Original/main implementation |
| [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi) | TypeScript/Rust/Bun | 7.6k | Fork with IDE wiring, LSP/DAP support |
| [Dicklesworthstone/pi_agent_rust](https://github.com/Dicklesworthstone/pi_agent_rust) | Rust | 1.1k | High-performance port, zero unsafe code |

---

## Architecture {#architecture}

### Core Packages (earendil-works/pi monorepo) {#core-packages-earendil-works-pi-monorepo}

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

### oh-my-pi Architecture {#oh-my-pi-architecture}

Fork of the original Pi with a Rust core (~27k lines of Rust):

- **Dual kernels**: Persistent Python and Bun kernels for code execution that can call agent tools directly
- **In-process tools**: ripgrep, glob, find reimplemented natively (no subprocess overhead)
- **LSP integration**: Full Language Server Protocol support for diagnostics, navigation, symbols, renames, code actions
- **DAP support**: Debug Adapter Protocol for C, Go, Python debuggers
- **AST editing**: Hashline editing with content hashes as anchors to prevent stale edits

### pi_agent_rust Architecture {#pi-agent-rust-architecture}

A Rust port focused on performance:

- **Single static binary** with sub-100ms startup and <50MB idle memory (~21MB binary)
- **asupersync**: Structured concurrency runtime with HTTP/TLS/SQLite
- **rich_rust**: Terminal UI library
- **Zero unsafe code**

---

## Key Features {#key-features}

### Common Features (All Implementations) {#common-features-all-implementations}

- **Multi-provider LLM support**: 40+ providers including Anthropic, OpenAI, Google Gemini, Groq, Ollama, OpenRouter, Azure
- **Multiple execution modes**: Interactive TUI, Print/JSON, RPC, SDK
- **Tree-structured history**: Navigate, branch, and share sessions
- **Context engineering**: AGENTS.md, SYSTEM.md, compaction, skills, dynamic context injection
- **Session persistence**: JSONL-based with branching support

### oh-my-pi-Specific Features {#oh-my-pi-specific-features}

- **32 built-in tools** across categories: Files & Search, Runtime, Code Intelligence, Coordination, External, Memory
- **Subagent task fan-out**: Parallel work across isolated worktrees with schema-validated returns
- **Internal IPC**: Agent-to-agent communication within same process
- **Role-based model routing**: default, smol, slow, plan, commit roles with per-role fallback chains
- **Hindsight memory**: Project-specific facts retained across sessions
- **Browser automation**: Headless Chromium or CDP-attached Electron
- **Web search chaining**: 14 providers with site-specific extraction (GitHub, npm, PyPI, arxiv, Stack Overflow)
- **GitHub operations**: Issues, PRs, code search via gh CLI

### pi_agent_rust-Specific Features {#pi-agent-rust-specific-features}

- **8 built-in tools**: read, write, edit, hashline_edit, bash, grep, find, ls
- **Three execution modes**: Interactive (TUI), Print mode (stdout), RPC mode (stdin/stdout JSON)
- **JS/TS execution**: Embedded QuickJS runtime (no Node/Bun dependency needed)
- **Capability-based security**: Two-stage exec enforcement, per-extension trust lifecycle

---

## Customization Guide {#customization-guide}

### 1. Extensions (earendil-works/pi) {#_1-extensions-earendil-works-pi}

TypeScript modules that can add:
- **Tools**: New capabilities the agent can use
- **Commands**: Slash commands for the agent
- **Events**: Hook into agent lifecycle
- **Custom UI**: Terminal interface components

```bash
# Install extensions
npm install -g --ignore-scripts <extension-package>
```

### 2. Skills (earendil-works/pi) {#_2-skills-earendil-works-pi}

Reusable on-demand agent capabilities triggered via slash commands.

### 3. Prompt Templates {#_3-prompt-templates}

Reusable prompts that expand from slash commands, allowing custom prompts for specific tasks.

### 4. Themes {#_4-themes}

Both built-in and custom terminal themes supported.

### 5. Pi Packages {#_5-pi-packages}

Bundle and share extensions, skills, prompts, and themes together.

### 6. Custom Providers (earendil-works/pi) {#_6-custom-providers-earendil-works-pi}

Implement custom APIs and OAuth flows for new LLM providers.

### oh-my-pi Configuration {#oh-my-pi-configuration}

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

### Settings-Gated Tools (oh-my-pi) {#settings-gated-tools-oh-my-pi}

Tools like `github`, `calc`, `inspect_image` can be activated per-project via settings.

### Tool Discovery (oh-my-pi) {#tool-discovery-oh-my-pi}

BM25 search indexes tools mid-session when needed, discoverable via a hidden index.

---

## Code Examples {#code-examples}

### Installation (earendil-works/pi) {#installation-earendil-works-pi}

```bash
# npm
npm install -g --ignore-scripts @earendil-works/pi-coding-agent

# Or installer script
curl -fsSL https://pi.dev/install.sh | sh
```

### Installation (pi_agent_rust) {#installation-pi-agent-rust}

```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/pi_agent_rust/main/install.sh" | bash

# Requires API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Installation (oh-my-pi) {#installation-oh-my-pi}

```bash
# Shell script (macOS/Linux)
curl -fsSL https://raw.githubusercontent.com/can1357/oh-my-pi/main/install.sh | sh

# Or via bun
bun install -g oh-my-pi

# Or via mise
mise install oh-my-pi
```

### Programmatic Usage (earendil-works/pi) {#programmatic-usage-earendil-works-pi}

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

### RPC Mode Integration (pi_agent_rust) {#rpc-mode-integration-pi-agent-rust}

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

## Execution Modes {#execution-modes}

| Mode | Description |
|------|-------------|
| **Interactive (TUI)** | Default streaming terminal UI with autocomplete, session branching |
| **Print/JSON** | Single response to stdout, scriptable, structured events |
| **RPC** | JSON protocol over stdin/stdout for IDE integrations |
| **SDK** | Embed directly in Node.js applications |

---

## What PI Agent Does NOT Include {#what-pi-agent-does-not-include}

Intentionally omitted (build yourself via extensions or use third-party packages):

- Sub-agents
- MCP (Model Context Protocol) support
- Permission popups
- Plan mode
- To-do tracking
- Background bash

---

## Documentation & Resources {#documentation-resources}

- **Official Docs**: [https://pi.dev](https://pi.dev)
- **Main GitHub**: [earendil-works/pi](https://github.com/earendil-works/pi)
- **oh-my-pi GitHub**: [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi)
- **pi_agent_rust GitHub**: [Dicklesworthstone/pi_agent_rust](https://github.com/Dicklesworthstone/pi_agent_rust)

---

## 原理剖析 {#原理剖析}

> 本节深入分析 earendil-works/pi 源码，揭示核心架构设计。所有源码均来自 `/tmp/pi-repo/packages/`。

---

### 1. Agent 主循环与工具调用 {#_1-agent-主循环与工具调用}

#### 三层架构 {#三层架构}

pi-agent-core 由三层构成：

| 层 | 文件 | 职责 |
|----|------|------|
| **Agent** | `agent/src/agent.ts` | 高层状态机，`steer()` / `followUp()` 消息注入 |
| **runAgentLoop** | `agent/src/agent-loop.ts` | 低层循环，处理流式、工具执行、turn 管理 |
| **AgentHarness** | `agent/src/harness/agent-harness.ts` | 生产级 harness：session 持久化、hooks、skills |

#### 主循环（agent-loop.ts, 行 155-269） {#主循环-agent-loop-ts-行-155-269}

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

#### 工具执行流程（agent-loop.ts, 行 373-516） {#工具执行流程-agent-loop-ts-行-373-516}

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
