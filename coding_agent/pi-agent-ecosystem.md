---
title: "Pi 扩展生态与能力"
description: "Pi 的\"核心刻意做小\"哲学决定了它真正的能力上限在生态。本篇聚焦："
---
# Pi 扩展生态与能力

Pi 的"核心刻意做小"哲学决定了它真正的能力上限在生态。本篇聚焦：

- 官方 9 个扩展示例（不是 50+，是 9 个）
- MCP 集成的"曲线救国"方案
- SDK 模式与真实嵌入案例
- "故意缺失"能力的社区实现
- 作者公开的设计哲学（来自 launch blog）

> **主仓库命名说明**：`earendil-works/pi` 是当前 canonical 仓库（59.9k stars / 7.2k forks / MIT），`badlogic/pi-mono` 是 GitHub 自动 redirect（作者 Mario Zechner 的 GitHub 用户名是 `badlogic`）。两个 URL 指向同一份代码。npm 包以 `@earendil-works/*` scope 上传（公司 org）。
>
> **更新数据**（2026-06 抓取）：`earendil-works/pi` 59.9k stars / 7.2k forks / MIT；`can1357/oh-my-pi` 10.6k stars / MIT；`Dicklesworthstone/pi_agent_rust` 1.1k stars / MIT + Rider。

---

## 1. 官方扩展示例（9 个）

主仓库 [`packages/coding-agent/examples/extensions/`](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions) 下只有 9 个 example extension，但每个都展示了一个独立的扩展 API 切面：

| 目录 | 一句话定位 | 展示的扩展能力 |
|------|----------|--------------|
| `custom-provider-anthropic` | 自定义 LLM provider（含 OAuth + API key 双模式） | `registerProvider` + 完整 streaming 实现 |
| `custom-provider-gitlab-duo` | GitLab Duo 接入（Anthropic + OpenAI Responses 两个 backend 复用了 pi-ai） | OAuth + 复用 pi-ai 内置 stream 函数 |
| `doom-overlay` | TUI overlay 里跑 DOOM（35 FPS） | `ctx.ui.custom({ overlay: true })` |
| `dynamic-resources` | 动态注册 skill / prompt / theme 路径 | `resources_discover` 事件 |
| `gondolin` | 把所有工具路由到本地 QEMU 微型 VM 内执行 | 替换所有内置工具的 `BashOperations` |
| `plan-mode` | 计划模式（只读，扫描 `[DONE:n]` 标记） | `registerFlag` / `registerCommand` / `tool_call` 阻断 / 状态持久化 |
| `sandbox` | OS 级沙箱（macOS sandbox-exec / Linux bubblewrap） | 替换 `bash` 工具 + `user_bash` 事件 |
| `subagent` | 子代理委派（single / parallel / chain 三模式） | `registerTool` + 子进程 spawn + 复杂 render |
| `with-deps` | 扩展自带 npm 依赖（jiti 从扩展自身 `node_modules` 解析） | 依赖打包 |

> **学习建议**：先读 `dynamic-resources`（最简，30 行），再读 `with-deps`（单 tool + 依赖），最后挑一个完整示例（如 `subagent` / `sandbox` / `gondolin`）做 walkthrough。

### 1.1 4 个值得深入的示例

#### `subagent` —— 子代理委派的工程范本

源文件 [`subagent/index.ts`](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/examples/extensions/subagent/index.ts) 约 700 行，展示了一个**生产级**子代理工具的完整实现：

- **三种执行模式**：
  - `single`：`{ agent: "name", task: "..." }`
  - `parallel`：`{ tasks: [{ agent, task }, ...] }`，并发上限 4（`MAX_CONCURRENCY`）
  - `chain`：`{ chain: [...] }`，`{previous}` 占位符注入上一步输出
- **子代理发现**：`discoverAgents(ctx.cwd, agentScope)` 扫描 `~/.pi/agent/agents/`（user）和 `.pi/agents/`（project）
- **执行方式**：spawn 一个新的 `pi --mode json -p --no-session` 子进程；通过 stdout JSON 事件流回收消息、tool result、usage
- **安全**：当 `agentScope: "project" | "both"` 时，弹出 `ctx.ui.confirm` 让用户确认是否信任 project-local agent（防御 repo-controlled prompt injection）
- **Abort 传播**：监听 `signal.aborted`，先 SIGTERM，5 秒未退出升级为 SIGKILL
- **TUI 渲染**：`renderCall` / `renderResult` 实现分层展示（单条 vs 链式 vs 并行），含 token / cost 统计
- **输出截断**：`PER_TASK_OUTPUT_CAP = 50 * 1024` bytes / task

**关键设计点**：用 `getPiInvocation` 函数识别当前是直接跑 `pi` 还是通过 `node/bun` 跑（`bunfs` 虚拟路径 vs 真实路径）—— 解决开发态 vs 安装态的调用差异。

#### `sandbox` —— OS 级沙箱的标准接法

源文件 [`sandbox/index.ts`](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/examples/extensions/sandbox/index.ts) 约 230 行，把内置 `bash` 工具替换为走 `@anthropic-ai/sandbox-runtime` 的版本：

- **平台差异**：
  - macOS → `sandbox-exec`（Seatbelt）
  - Linux → `bubblewrap`（需额外装 `bubblewrap`、`socat`、`ripgrep`）
- **配置层叠**：`~/.pi/agent/extensions/sandbox.json` (global) ⊕ `<cwd>/.pi/sandbox.json` (project)，project 优先
- **关键钩子**：
  - `registerFlag("no-sandbox", ...)` 关闭沙箱
  - `registerTool({ ...localBash, label: "bash (sandboxed)", async execute ... })` **覆盖内置** —— 这就是扩展系统允许"替换"内置工具的范例
  - `pi.on("user_bash", () => ({ operations: createSandboxedBashOps() }))` 拦截用户 `!` 命令
  - `pi.on("session_shutdown", async () => { await SandboxManager.reset() })` 清理
- **典型 `.pi/sandbox.json`**：
  ```json
  {
    "enabled": true,
    "network": { "allowedDomains": ["github.com", "*.github.com"] },
    "filesystem": {
      "denyRead": ["~/.ssh", "~/.aws"],
      "allowWrite": [".", "/tmp"],
      "denyWrite": [".env"]
    }
  }
  ```
- **设计模式**：不修改工具定义本体，而是在每次 `execute` 时用 `createBashTool(localCwd, { operations })` **重新创建** 工具实例 —— 这种"operations 注入"是 `pi-coding-agent` 内置工具的扩展点。

#### `gondolin` —— 微型 VM 沙箱

[`gondolin/index.ts`](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/examples/extensions/gondolin/index.ts) 约 360 行，用 [`@earendil-works/gondolin`](https://www.npmjs.com/package/@earendil-works/gondolin)（同样是 Mario Zechner 的 micro-VM 项目）在 QEMU 中跑 pi：

- **架构**：宿主 cwd 挂载到 guest 的 `/workspace`（`RealFSProvider`），其他 guest 写入隔离
- **全面替换**：把 7 个内置工具（read/write/edit/bash/ls/find/grep）全部路由到 VM 内
- **路径转换**：`hostPathToGuest` / `toGuestPath` 处理 host ↔ guest 路径映射，处理 `path.relative` + `path.posix.join`
- **状态机**：`vm` 持有当前 VM 实例；`vmStarting` 是 Promise 用于去重启动
- **生命周期**：
  - `session_start` → 启动 VM
  - `session_shutdown` → `await activeVm.close()`
  - `user_bash` 事件 → 同样走 VM 内 bash
  - `before_agent_start` → 修改 `systemPrompt`，把"Current working directory"从 host 路径换成 guest 路径
- **setup 成本**：Node ≥ 23.6.0 + QEMU；适合做"代码生成后必须在干净环境跑测试"的工作流

#### `custom-provider-anthropic` —— 完整 Provider 实现参考

[`custom-provider-anthropic/index.ts`](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/examples/extensions/custom-provider-anthropic/index.ts) 约 430 行，**手写**了 Anthropic streaming 实现（不复用 pi-ai 内置）：

- **OAuth PKCE 流程**：`generatePKCE` → `loginAnthropic`（callback 拿 code → exchange token）→ `refreshAnthropicToken`
- **OAuth vs API key 区分**：`isOAuthToken(apiKey) → apiKey.includes("sk-ant-oat")`
- **OAuth "stealth mode"**：
  - 把工具名映射成 Claude Code 工具名（`Read`/`Write`/`Edit`/...）—— 因为 Anthropic OAuth 对非 Claude Code 工具名有 rate limit / 拒绝策略
  - 设置 `claude-cli/2.1.2 (external, cli)` user-agent
  - 加 `claude-code-20250219,oauth-2025-04-20` beta 头
  - system prompt 强制以 "You are Claude Code, Anthropic's official CLI for Claude." 开头
- **流式事件映射**：把 Anthropic 的 `content_block_start` / `content_block_delta` / `content_block_stop` / `message_delta` 翻译成 pi-ai 的统一 `AssistantMessageEventStream` 事件（`text_start` / `text_delta` / `text_end` / `toolcall_start` / `toolcall_delta` / `toolcall_end` / `done` / `error`）
- **Cache control**：自动在最后一条 user message 的最后一块加 `cache_control: { type: "ephemeral" }`，最大化 prompt cache 命中率

**实战价值**：要接 Bedrock custom endpoint、Azure OpenAI、自建 OpenAI 兼容代理等，都以这个为模板。

---

## 2. MCP 集成：曲线救国

Pi 官方明确**不**支持 MCP（见第 6 节设计哲学）。但社区有标准方案：

### 2.1 MCPorter —— MCP 桥接器

[`openclaw/mcporter`](https://github.com/openclaw/mcporter) (MIT, 4.6k stars, 原 `steipete/mcporter` 已迁至 openclaw org)：

- **TS 工具集 + CLI + 代码生成器**
- **零配置发现**：自动读取 `~/.mcporter/mcporter.json[c]` + 项目 config + Claude/Cursor/Codex/Windsurf/OpenCode/VS Code 的 MCP 配置
- **核心能力**：
  - `mcporter list` —— 列出所有可用 MCP server 及其工具
  - `mcporter generate-cli` —— 把任意 MCP server 转为独立 CLI
  - `mcporter emit-ts` —— 生成强类型 TS 客户端
  - `mcporter call 'linear.create_comment(issueId: "ENG-123", body: "...")'` —— 函数式调用
  - `mcporter serve` —— bridge mode，让 keep-alive 服务器在多个调用间保持连接
- **支持传输**：stdio / SSE / HTTP
- **Pi 集成模式**：把 MCPorter 包装成 Pi 扩展，通过 `pi.registerTool` 暴露 MCP 工具；这样 pi 不需要原生理解 MCP schema，但能调用任意 MCP server

### 2.2 自己写一个 MCP 桥接扩展

5 步：

1. spawn MCP server 子进程（`spawn("npx", ["-y", "@modelcontextprotocol/server-github"])`）
2. 在 stdout 上做 LSP-style framed JSON-RPC 解析（`Content-Length: N\r\n\r\n{...}`）
3. 发送 `initialize` → `tools/list` → 缓存 tool schema
4. `pi.registerTool` 创建一个 wrapper tool，参数是 MCP tool 名 + args
5. 实际调用时 JSON-RPC `tools/call`，把结果转回 pi 的 `AgentToolResult` 格式

**Pi 自己的 LSP client**（`packages/coding-agent/src/lsp/client.ts`）就是这种 framing protocol 的现成实现参考。

### 2.3 Playwright / Chrome DevTools MCP 的代价

作者在 launch blog 给出实测数据：

| Server | 工具数 | Token 消耗 | 占 context 比例 |
|--------|-------|-----------|---------------|
| Playwright MCP | 21 | 13.7k | 7% |
| Chrome DevTools MCP | 26 | 18k | 9% |

> "MCP servers are overkill for most use cases, and they come with significant context overhead." —— Mario Zechner

**平替方案**：
- Playwright → CLI 工具 + skill（progressive disclosure，模型按需读 README）
- Chrome DevTools → 直接读 CDP WebSocket 协议（仅 1 个工具）
- 复杂 MCP 用 MCPorter 包装成 CLI，让 agent 通过 `bash` 工具调用而不是 `registerTool`

---

## 3. Pi Packages 生态

### 3.1 官方 monorepo：4 个核心包

[`badlogic/pi-mono`](https://github.com/badlogic/pi-mono) 仅含 4 个包（[package 列表](https://github.com/badlogic/pi-mono/tree/main/packages)）：

| Package | npm scope | 用途 |
|---------|----------|------|
| `agent` | `@earendil-works/pi-agent-core` | Agent 运行时、状态、transport（不直接对外） |
| `ai` | `@earendil-works/pi-ai` | **统一 LLM API**（4 个底层 API 覆盖几乎所有 provider） |
| `coding-agent` | `@earendil-works/pi-coding-agent` | 交互式 CLI（`pi` 命令本体） |
| `tui` | `@earendil-works/pi-tui` | 终端 UI 库（差分渲染） |

> 兄弟仓库 [`badlogic/agent-tools`](https://github.com/badlogic/agent-tools)：CLI 工具集，与 pi 配合使用（**已 archived**，2026-06 状态）。

### 3.2 第三方社区包

npm 上以 `@earendil-works/` 开头的官方包主要就是上面 4 个 + pi 周边工具（如 `gondolin`）。其他社区包不强制使用 `earendil-works` scope。

**`pi install` 命令**支持两种源：

```bash
pi install npm:@foo/pi-tools        # npm 包
pi install git:github.com/user/repo  # git 仓库
```

**Pi package 目录结构**（来自 `skills.md` / `prompt-templates.md`）：

```
my-pi-package/
├── package.json        # 声明 pi.skills / pi.prompts / pi.themes
├── extensions/
│   └── my-extension/
│       └── index.ts
├── skills/
│   └── my-skill/
│       ├── SKILL.md
│       └── helper.js
├── prompts/
│   └── review.md
└── themes/
    └── my-theme.json
```

---

## 4. SDK 模式与真实嵌入案例

### 4.1 三种嵌入路径

| 路径 | 用法 | 适用 |
|------|------|------|
| **SDK 模式** (`createAgentSession`) | 直接 import 进 Node/Bun 进程，类型安全 | 长驻应用（Slack bot / Web 服务） |
| **RPC 模式** (`pi --mode rpc`) | 子进程 + JSONL stdio | 任何语言、任何进程的 IDE 集成 |
| **Print 模式** (`pi -p "..."`) | 单轮 headless | CI / 一次性脚本 |

### 4.2 SDK 模式要点

[`packages/coding-agent/docs/sdk.md`](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md) 给出的最小例子：

```typescript
import { AuthStorage, createAgentSession, ModelRegistry, SessionManager } from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),
  authStorage: AuthStorage.create(),
  modelRegistry: ModelRegistry.create(authStorage),
});

session.subscribe((event) => {
  if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
});

await session.prompt("What files are in the current directory?");
```

**关键 API**：
- `createAgentSession({ sessionManager, authStorage, modelRegistry, ... })`
- `createAgentSessionRuntime()`：包装 `createAgentSession` + cwd/session 目标
- `AgentSession`：`prompt` / `steer` / `followUp` / `subscribe` / `setModel` / `setThinkingLevel` / `cycleModel` / `navigateTree` / `compact` / `abort` / `dispose`
- `defineTool()`：从 Typebox schema 创建自定义工具
- `AuthStorage`：credential 存储优先级 = runtime overrides → `auth.json` → env vars → fallback resolver

**驱动约束**：
- `prompt()` 在流式期间需要 `streamingBehavior: "steer" | "followUp"`
- `steer()` 在当前 turn 工具调用后插入
- `followUp()` 在 agent 完全停机后插入
- 扩展命令（`/foo`）立即执行，不能入队

### 4.3 真实 SDK 消费者

**OpenClaw**（launch blog 提到的兄弟项目）—— 把 pi 当作 library 嵌入到具体应用。具体仓库和接入方式见 launch blog 注释的引用。

MCPorter 的 bridge mode（`mcporter serve`）实质上是一个 SDK 消费者：把 MCP server 保持 warm 后通过 HTTP 暴露，让 pi 在 RPC 模式下调用。

### 4.4 RPC 模式协议细节

[`packages/coding-agent/docs/rpc.md`](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md) 完整定义：

**Frame 规则**：
- JSONL，LF (`\n`) 分隔
- 客户端必须 split on `\n`（不是 `U+2028`/`U+2029`）
- 去掉 trailing `\r`
- 不要用 Node `readline`（会把 Unicode separator 当 newline）

**消息形态**：
- **命令**：stdin 上的 JSON 对象
- **响应**：stdout 上的 `{ type: "response", success, ... }`
- **事件**：stdout 上持续流出，**不带** `id` 字段

**核心命令**：`prompt` / `steer` / `follow_up` / `abort` / `new_session` / `get_state` / `get_messages` / `set_model` / `cycle_model` / `get_available_models` / `set_thinking_level` / `cycle_thinking_level` / `set_steering_mode` / `set_follow_up_mode` / `compact` / `set_auto_compaction` / `set_auto_retry` / `abort_retry` / `bash` / `abort_bash` / `get_session_stats` / `export_html` / `switch_session` / `fork` / `clone` / `get_fork_messages` / `get_last_assistant_text` / `set_session_name` / `get_commands`

**事件流**：`agent_start` / `agent_end` / `turn_start` / `turn_end` / `message_start` / `message_update` / `message_end` / `tool_execution_start` / `tool_execution_update` / `tool_execution_end` / `queue_update` / `compaction_start` / `compaction_end` / `auto_retry_start` / `auto_retry_end` / `extension_error`

**Extension UI 协议**：RPC 模式下，扩展的 `ctx.ui` 调用转为子协议：
- 对话方法（`select` / `confirm` / `input` / `editor`）发出 `extension_ui_request` 并阻塞等 `extension_ui_response`
- Fire-and-forget（`notify` / `setStatus` / `setWidget`）只发请求不等响应
- `ctx.ui.custom()` 在 RPC 模式返回 `undefined`（overlay 不可用）
- `ctx.mode === "rpc"` / `ctx.hasUI === true`（注意 RPC 也有 UI capability）

**Python / Node 客户端示例**：见 [rpc.md](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md) 的 Python + Node.js 子段，含正确的 JSONL reader（用 `StringDecoder` 避免 Node `readline` 的 Unicode bug）。

---

## 5. "故意缺失"能力的社区实现

下表对应 `tools/pi-agent.md` 第 264-273 行"PI Agent Does NOT Include"列表，给出每个能力的**首选社区方案**：

| 缺失能力 | 社区实现 | 来源 |
|---------|---------|------|
| **Sub-agents** | 官方 `subagent` example（前面详述） | `examples/extensions/subagent/index.ts` |
| **MCP** | MCPorter (steipete/mcporter) | https://github.com/steipete/mcporter |
| **Permission popups** | `sandbox` example（`ctx.ui.confirm` in `tool_call`）| `examples/extensions/sandbox/index.ts` |
| **Plan mode** | 官方 `plan-mode` example | `examples/extensions/plan-mode/index.ts` |
| **To-do tracking** | 无官方 example；参考：`subagent` 内部的 `todoList` 模式 / 自写 `pi.registerTool({ name: "todo_write" })` 即可 |
| **Background bash** | 无官方 example；推荐直接用 `tmux`（作者本人建议） | launch blog 段落 |

**作者建议**：

- "to-do lists generally confuse models more than they help" —— 倾向用 `TODO.md` 文件而非内置 todo 工具
- "There is no need for background bash. Claude Code can use tmux too, you know. Bash is all you need." —— 把后台进程的复杂度让给 tmux，用户有完全的可观测性
- "Spawning multiple sub-agents to implement various features in parallel is an anti-pattern in my book." —— 平行 sub-agent 倾向于把工作切碎却无人 review

---

## 6. 设计哲学（摘自 launch blog）

来源：[Mario Zechner, 2025-11-30, "What I learned building an opinionated and minimal coding agent"](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)

### 6.1 核心信条

> "if I don't need it, it won't be built. And I don't need a lot of things."

三个反复出现的设计价值：
1. **Full control over what enters the model's context** —— 每个 token 都应该是用户主动选择的
2. **Complete observability into agent behavior** —— 不接受 "black box within a black box"
3. **Simple, predictable tool that doesn't break with upstream changes** —— 不追新功能

### 6.2 关键数据点

| 维度 | 数据 |
|------|------|
| pi 系统 prompt + 工具定义总 token 数 | < 1000 |
| Playwright MCP 对比 | 21 工具 / 13.7k tokens / 占用 7% context |
| Chrome DevTools MCP 对比 | 26 工具 / 18k tokens / 占用 9% context |
| 覆盖所有 provider 用的底层 API | 4 个（OpenAI Completions / OpenAI Responses / Anthropic Messages / Google Generative AI） |
| 单 session 能装下多少轮 | "hundreds of exchanges" 不需要 compaction |
| Terminal-Bench 2.0 评测 | Claude Opus 4.5，每题 5 次 |

### 6.3 关键设计决策（直接引用）

**为什么不要 MCP**：
> "MCP servers are overkill for most use cases, and they come with significant context overhead."

**为什么不要 Sub-agent 工具**：
> "You have zero visibility into what that sub-agent does. It's a black box within a black box. Spawning multiple sub-agents to implement various features in parallel is an anti-pattern in my book."

**为什么不要 To-do**：
> "to-do lists generally confuse models more than they help by adding state to track. A TODO.md file works better."

**为什么不要 Plan mode**：
> "File plans (PLAN.md) are shareable across sessions, versionable, and editable collaboratively. Claude Code's plan mode is criticized for lack of observability."

**为什么不要 Background bash**：
> "Adds process tracking, output buffering, and cleanup complexity, while providing poor observability. The author recommends tmux instead, which gives full visibility and the ability to co-debug."

**关于安全/permission**：
> "If you look at the security measures in other coding agents, they're mostly security theater."

**关于 unified LLM API**：
> "Many unified LLM APIs completely ignore providing a way to abort requests. This is entirely unacceptable if you want to integrate your LLM into any kind of production system."

**关于 reasoning 字段标准化**：
> "different providers return reasoning content in different fields (`reasoning_content` vs `reasoning`)"

---

## 7. 关键 URL 索引

### 主仓库
- https://github.com/badlogic/pi-mono —— monorepo（4 个包）
- https://github.com/earendil-works/pi —— 同一份代码的公司 org 镜像
- https://pi.dev —— 官方主页
- https://mariozechner.at/posts/2025-11-30-pi-coding-agent/ —— launch blog
- https://www.npmjs.com/package/@earendil-works/pi-coding-agent —— npm 包

### monorepo 关键路径
- `packages/coding-agent/README.md` —— CLI 总览
- `packages/coding-agent/docs/extensions.md` —— 扩展 API 参考
- `packages/coding-agent/docs/skills.md` —— skills
- `packages/coding-agent/docs/prompt-templates.md` —— prompt templates
- `packages/coding-agent/docs/themes.md` —— themes
- `packages/coding-agent/docs/sdk.md` —— SDK
- `packages/coding-agent/docs/rpc.md` —— RPC 协议
- `packages/coding-agent/examples/extensions/` —— 9 个扩展示例

### 社区资源
- https://github.com/openclaw/mcporter —— MCP 桥接（4.6k stars，原 steipete/mcporter 已迁移）
- https://github.com/badlogic/agent-tools —— Mario 的 CLI 工具集（**已 archived**）
- https://github.com/badlogic/pi-terminal-bench —— Terminal-Bench runner
- https://github.com/can1357/oh-my-pi —— oh-my-pi fork（10.6k stars）
- https://github.com/Dicklesworthstone/pi_agent_rust —— Rust port（1.1k stars）
- https://github.com/anthropics/skills —— Anthropic Skills（docx/pdf/pptx/xlsx/web）
- https://github.com/badlogic/pi-skills —— badlogic 的 skills 集合（web search、browser、APIs）

---

## License

MIT License

---
