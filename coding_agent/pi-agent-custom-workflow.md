---
title: "Pi 定制 workflow 实操"
description: "理论够了，本篇解决\"我具体怎么把 Pi 用出花\"。"
---
# Pi 定制 workflow 实操

理论够了，本篇解决"我具体怎么把 Pi 用出花"。

覆盖：
- 扩展开发完整生命周期（事件 / 钩子 / 上下文 / 工具定义 / 自定义 UI）
- 3 个代表示例的 walkthrough
- Skills / Prompt Templates / Themes 三种轻量扩展
- Pi Package 打包与分发
- SDK / RPC / Print 三种嵌入模式
- 5 个真实定制 workflow 配方

> **数据来源**：`packages/coding-agent/docs/` 下的官方文档（`extensions.md` / `skills.md` / `prompt-templates.md` / `themes.md` / `sdk.md` / `rpc.md`）+ `examples/extensions/` 下的 9 个官方示例源码（见 [`pi-agent-ecosystem.md`](./pi-agent-ecosystem.md) 第 1 节）。

---

## 1. 扩展开发完整生命周期

### 1.1 扩展的本质

一个扩展 = 一个导出 `default function(pi: ExtensionAPI)` 的 TypeScript 模块。可以注册事件订阅、工具、命令、UI 组件、CLI flag、自定义 provider 等。

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // 同步或异步都可
}
```

**安装位置**：
- 全局：`~/.pi/agent/extensions/*.ts` 或 `*/index.ts`
- 项目：`.pi/extensions/*.ts` 或 `*/index.ts`
- 临时：`pi -e ./path/to/extension`

**可导入包**：
- `@earendil-works/pi-coding-agent` —— ExtensionAPI、helper 类型
- `typebox` —— 工具参数 schema（`Type.Object({...})`）
- `@earendil-works/pi-ai` —— AI 工具（如 `StringEnum`）
- `@earendil-works/pi-tui` —— TUI 组件

### 1.2 事件完整清单

下表按生命周期阶段组织，所有事件都通过 `pi.on(event, handler)` 订阅，handler 可返回对象以**修改**事件结果。

| 阶段 | 事件 | Handler 签名 | 可阻断 | 可修改 |
|------|------|------------|--------|--------|
| 资源发现 | `resources_discover` | `(event, ctx) => { skillPaths, promptPaths, themePaths }` | ❌ | 返回路径 |
| Session | `session_start` | `(event, ctx) => void` | ❌ | ❌ |
| Session | `session_before_switch` | `(event, ctx) => { cancel: true }` | ✅ | ✅ |
| Session | `session_before_fork` | `(event, ctx) => { cancel: true }` | ✅ | ✅ |
| Session | `session_before_compact` | `(event, ctx) => { cancel } \| { compaction: { summary, firstKeptEntryId, tokensBefore } }` | ✅ | ✅ |
| Session | `session_compact` | `(event, ctx) => void` | ❌ | ❌ |
| Session | `session_before_tree` | `(event, ctx) => { cancel } \| { summary }` | ✅ | ✅ |
| Session | `session_tree` | `(event, ctx) => void` | ❌ | ❌ |
| Session | `session_shutdown` | `(event, ctx) => void` | ❌ | ❌ |
| Agent | `before_agent_start` | `(event, ctx) => { message, systemPrompt }` | ❌ | ✅ 注入消息 / 改 system prompt |
| Agent | `agent_start` | `(event, ctx) => void` | ❌ | ❌ |
| Agent | `agent_end` | `(event, ctx) => void` | ❌ | ❌ |
| Turn | `turn_start` | `(event, ctx) => void` | ❌ | ❌ |
| Turn | `turn_end` | `(event, ctx) => void` | ❌ | ❌ |
| Message | `message_start` | `(event, ctx) => void` | ❌ | ❌ |
| Message | `message_update` | `(event, ctx) => void` | ❌ | ❌ |
| Message | `message_end` | `(event, ctx) => { message: modified }` | ❌ | ✅ 改消息 |
| Tool | `tool_execution_start` | `(event, ctx) => void` | ❌ | ❌ |
| Tool | `tool_execution_update` | `(event, ctx) => void` | ❌ | ❌ |
| Tool | `tool_execution_end` | `(event, ctx) => void` | ❌ | ❌ |
| Tool | `context` | `(event, ctx) => { messages: filtered }` | ❌ | ✅ 改 messages（深拷贝安全） |
| Provider | `before_provider_request` | `(event, ctx) => { ...event.payload, temperature: 0 }` | ❌ | ✅ 改 payload |
| Provider | `after_provider_response` | `(event, ctx) => void`（仅 status / headers） | ❌ | ❌ |
| Model | `model_select` | `(event, ctx) => void` | ❌ | ❌ |
| Model | `thinking_level_select` | `(event, ctx) => void`（通知） | ❌ | ❌ |
| Tool | `tool_call` | `(event, ctx) => { block: true, reason }` | ✅ | ✅ 改 input |
| Tool | `tool_result` | `(event, ctx) => { content, details, isError }` | ❌ | ✅ |
| 用户 bash | `user_bash` | `(event, ctx) => { result } \| { operations: BashOperations }` | ✅ | ✅ |
| 输入 | `input` | `(event, ctx) => { action: "transform", text } \| "continue"` | ✅ | ✅ 改输入文本 |

### 1.3 完整生命周期时序

```
session_start → resources_discover
  ↓
user prompt → input → before_agent_start → agent_start
  ↓
turn_start → context → before_provider_request → after_provider_response
  ↓
[tool_execution_start → tool_call → tool_result → tool_execution_end]
  ↓
turn_end → agent_end
```

### 1.4 ExtensionContext API

`ctx` 在所有 handler 中可用：

**属性**：
- `ctx.ui` —— UI 方法（见 1.6 节）
- `ctx.mode` —— `"tui" | "rpc" | "json" | "print"`
- `ctx.hasUI` —— `true` in TUI and RPC
- `ctx.cwd` —— 当前工作目录
- `ctx.sessionManager` —— 只读 session 状态
- `ctx.modelRegistry` / `ctx.model` —— 模型与 API key
- `ctx.signal` —— 当前 agent 的 AbortSignal

**方法**：
- `ctx.isIdle()` / `ctx.abort()` / `ctx.hasPendingMessages()` —— 控制流
- `ctx.shutdown()` —— 优雅关闭
- `ctx.getContextUsage()` —— 当前 context 使用情况
- `ctx.compact({ customInstructions, onComplete, onError })` —— 触发 compaction（不 await）
- `ctx.getSystemPrompt()` —— 拿当前 system prompt 字符串

**ExtensionCommandContext**（仅在 command handler 内可用，扩展 `ExtensionContext`）：
- `ctx.getSystemPromptOptions()` —— 拿 system prompt 的基础输入
- `ctx.waitForIdle()` —— 等 agent 完成
- `ctx.newSession({ parentSession, setup, withSession })` —— 新 session
- `ctx.fork(entryId, { position, withSession })` —— 从某 entry fork
- `ctx.navigateTree(targetId, options?)` —— tree 跳转
- `ctx.switchSession(sessionPath, options?)` —— 切到别的 session 文件
- `ctx.reload()` —— 重新加载（等同于 `/reload`）

### 1.5 ExtensionAPI 完整方法

```typescript
pi.on(event, handler)                     // 订阅事件
pi.registerTool(definition)               // 注册自定义工具
pi.sendMessage(message, options?)         // 注入自定义消息
pi.sendUserMessage(content, options?)     // 发送 user 消息
pi.appendEntry(customType, data?)         // 持久化扩展状态
pi.setSessionName(name)                   // 设置/获取 session 名
pi.setLabel(entryId, label)               // 给 entry 加/清标签
pi.registerCommand(name, options)         // 注册 slash 命令
pi.getCommands()                          // 拿所有可调用的命令
pi.registerMessageRenderer(customType, renderer)  // TUI 自定义渲染
pi.registerShortcut(shortcut, options)    // 键盘快捷键
pi.registerFlag(name, options)            // CLI flag
pi.exec(command, args, options?)          // 调 shell
pi.getActiveTools() / getAllTools() / setActiveTools(names)  // 工具集管理
pi.setModel(model)                        // 切换模型
pi.getThinkingLevel() / setThinkingLevel(level)  // 思考等级
pi.events                                 // inter-extension event bus
pi.registerProvider(name, config)         // 注册/覆盖 LLM provider
pi.unregisterProvider(name)               // 移除 provider
```

### 1.6 自定义 UI 完整 API

```typescript
// 对话框（阻塞等用户响应）
const choice = await ctx.ui.select("Pick:", ["A", "B", "C"]);
const ok = await ctx.ui.confirm("Delete?", "Cannot be undone");
const name = await ctx.ui.input("Name:", "placeholder");
const text = await ctx.ui.editor("Edit:", "prefilled");

// 通知（不阻塞）
ctx.ui.notify("Done!", "info");  // "info" | "warning" | "error"

// 状态条
ctx.ui.setStatus("my-ext", "Processing...");

// 工作消息
ctx.ui.setWorkingMessage("Thinking...");
ctx.ui.setWorkingVisible(false);
ctx.ui.setWorkingIndicator({ frames: ["·", "•", "●"] });

// 编辑器上方/下方组件
ctx.ui.setWidget("my-widget", ["Line 1", "Line 2"]);
ctx.ui.setWidget("my-widget", ["..."], { placement: "belowEditor" });

// 编辑器文本
ctx.ui.setEditorText("Prefill text");
ctx.ui.pasteToEditor("pasted content");

// 主题
const themes = ctx.ui.getAllThemes();
ctx.ui.setTheme("light");

// 定时对话框（超时自动返回 false）
const confirmed = await ctx.ui.confirm("Title", "Message", { timeout: 5000 });

// 自定义 TUI 组件
const result = await ctx.ui.custom<boolean>((tui, theme, keybindings, done) => {
  return new Text("Press Enter", 1, 1);
});

// Overlay 模式（用于游戏、富 UI）
const result = await ctx.ui.custom((tui, theme, keybindings, done) => {
  return new MyOverlay({ onClose: done });
}, { overlay: true, overlayOptions: { anchor: "top-right" } });

// 自定义编辑器
ctx.ui.setEditorComponent((tui, theme, keybindings) => new VimEditor(theme, keybindings));
```

### 1.7 工具定义完整结构

```typescript
pi.registerTool({
  name: "my_tool",                       // 必填
  label: "My Tool",                      // TUI 显示
  description: "What this tool does",    // 必填：模型看到
  promptSnippet: "Short one-liner",      // 可选：注入 system prompt 的摘要
  promptGuidelines: ["Use my_tool when..."],  // 可选：注入 guidelines
  parameters: Type.Object({              // TypeBox schema
    input: Type.String(),
    limit: Type.Optional(Type.Number()),
  }),
  prepareArguments(args) { /* 可选：参数 shim */ },

  async execute(toolCallId, params, signal, onUpdate, ctx) {
    if (signal?.aborted) {
      return { content: [{ type: "text", text: "Cancelled" }] };
    }
    onUpdate?.({ content: [{ type: "text", text: "Working..." }] });
    return {
      content: [{ type: "text", text: "Done" }],
      details: { /* 元数据，TUI render 用 */ },
      terminate: true,  // 可选：执行完停止 agent loop
    };
  },

  // 可选：自定义 TUI 渲染
  renderCall(args, theme, context) { /* ... */ },
  renderResult(result, options, theme, context) { /* ... */ },
});
```

**错误处理**：throw → 自动设 `isError: true`。
**输出截断**：`truncateHead` / `truncateTail` / `formatSize` / `DEFAULT_MAX_BYTES`（默认 50KB ≈ 10k tokens，2000 行）。

### 1.8 自定义 LLM Provider

```typescript
pi.registerProvider("my-proxy", {
  name: "My Proxy",
  baseUrl: "https://proxy.example.com",
  apiKey: "$PROXY_API_KEY",  // $ 前缀 = 从 env 读
  api: "anthropic-messages", // 复用 pi-ai 的流式实现
  models: [
    {
      id: "claude-sonnet-4-5",
      name: "Claude Sonnet 4.5 (via My Proxy)",
      reasoning: true,
      input: ["text", "image"],
      cost: { input: 3, output: 15, cacheRead: 0.3, cacheWrite: 3.75 },
      contextWindow: 200000,
      maxTokens: 64000,
    },
  ],
  oauth: {                              // 可选：OAuth 支持
    name: "My Proxy Login",
    login: async (callbacks) => { /* PKCE flow */ },
    refreshToken: async (cred) => { /* refresh */ },
    getApiKey: (cred) => cred.access,
  },
  streamSimple: myStreamFn,              // 可选：自定义流式实现
});
```

---

## 2. 实战 walkthrough：3 个代表示例

### 2.1 `with-deps` —— 最小可工作扩展（30 行）

**问题**：演示扩展如何打包自己的 npm 依赖（用 jiti 解析扩展自身 `node_modules`）。

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import ms from "ms";
import { Type } from "typebox";

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "parse_duration",
    label: "Parse Duration",
    description: "Parse a human-readable duration string (e.g., '2 days', '1h', '5m') to milliseconds",
    parameters: Type.Object({
      duration: Type.String({ description: "Duration string like '2 days', '1h', '5m'" }),
    }),
    execute: async (_toolCallId, params) => {
      const result = ms(params.duration as ms.StringValue);
      if (result === undefined) {
        throw new Error(`Invalid duration: "${params.duration}"`);
      }
      return {
        content: [{ type: "text", text: `${params.duration} = ${result} milliseconds` }],
        details: {},
      };
    },
  });
}
```

**学习点**：
- 30 行注册一个 tool
- TypeBox `Type.Object` + `Type.String` 给 schema
- 抛错自动转 `isError: true`
- `ms` 是扩展自己装的（`package.json` 加 `"ms": "^2.0.0"`），jiti 自动从扩展目录 `node_modules` 解析

### 2.2 `dynamic-resources` —— 动态注册 skills/prompts/themes

**问题**：扩展如何把自己目录里的 skill / prompt / theme 暴露给 Pi（而不是散在 `~/.pi/agent/` 全局）。

```typescript
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const baseDir = dirname(fileURLToPath(import.meta.url));

export default function (pi: ExtensionAPI) {
  pi.on("resources_discover", () => {
    return {
      skillPaths: [join(baseDir, "SKILL.md")],
      promptPaths: [join(baseDir, "dynamic.md")],
      themePaths: [join(baseDir, "dynamic.json")],
    };
  });
}
```

**学习点**：
- `resources_discover` 事件在 `session_start` 后触发，扩展可声明自己的资源路径
- Pi 加载顺序：global → project → packages → 扩展的 resources_discover 贡献
- 适合打包一个完整的 Pi package：扩展代码 + 资源（skill/prompt/theme）一起分发

### 2.3 `subagent` —— 生产级子代理工具

参考 [`pi-agent-ecosystem.md` §1.1 subagent 小节](./pi-agent-ecosystem.md)。核心结构：

```typescript
import { spawn } from "node:child_process";
// ... 其他 import

// 1. 工具 schema
const SubagentParams = Type.Object({
  agent: Type.Optional(Type.String()),
  task: Type.Optional(Type.String()),
  tasks: Type.Optional(Type.Array(TaskItem)),
  chain: Type.Optional(Type.Array(ChainItem)),
  agentScope: Type.Optional(StringEnum(["user", "project", "both"] as const)),
  confirmProjectAgents: Type.Optional(Type.Boolean({ default: true })),
  cwd: Type.Optional(Type.String()),
});

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "subagent",
    label: "Subagent",
    description: ["Delegate tasks to specialized subagents with isolated context.", /* ... */].join(" "),
    parameters: SubagentParams,

    async execute(_toolCallId, params, signal, onUpdate, ctx) {
      // 2. 解析 agent（从 ctx.cwd 扫描 user + project agents）
      const discovery = discoverAgents(ctx.cwd, params.agentScope ?? "user");
      
      // 3. 安全检查：project-local agents 需用户确认
      if ((params.agentScope === "project" || "both") && params.confirmProjectAgents && ctx.hasUI) {
        const ok = await ctx.ui.confirm(
          "Run project-local agents?",
          `Agents: ${names}\nSource: ${dir}\n\nProject agents are repo-controlled. Only continue for trusted repositories.`,
        );
        if (!ok) return /* cancel */;
      }
      
      // 4. 决定模式：single / parallel / chain
      // 5. spawn pi 子进程，监听 JSON 事件流
      // 6. 解析 message_end / tool_result_end 事件，累加 usage
      // 7. emit update 用于 TUI 实时展示
    },
    
    // 8. 自定义 TUI 渲染（单条 / 链式 / 并行 三种 layout）
    renderCall(args, theme, _context) { /* ... */ },
    renderResult(result, { expanded }, theme, _context) { /* ... */ },
  });
}
```

**学习点**：
- spawn 子进程 + JSONL stdout → 完整 agent 编排
- 模式分发：`modeCount` 校验、project agent 确认、abort 传播
- TUI 自定义渲染：`Container` + `Text` + `Markdown` 组件组合
- token / cost 聚合（`formatUsageStats`）
- `withFileMutationQueue` 防止并发写冲突

---

## 3. Skills / Prompt Templates / Themes

### 3.1 Skills —— 按需加载的能力包

**文件格式**：`SKILL.md` + YAML frontmatter

```markdown
---
name: my-skill
description: Processes input files. Use for batch data transformation.
---

# My Skill

## Setup
```bash
cd /path/to/skill && npm install
```

## Usage
```bash
./scripts/process.sh <input>
```
```

**Frontmatter 字段**：

| 字段 | 必填 | 备注 |
|------|------|------|
| `name` | ✅ | 1-64 字符，a-z/0-9/- |
| `description` | ✅ | ≤ 1024 字符，决定何时被加载 |
| `license` | ❌ | 许可证名或文件引用 |
| `compatibility` | ❌ | ≤ 500 字符，环境要求 |
| `metadata` | ❌ | 任意 K-V |
| `allowed-tools` | ❌ | 空格分隔的 tool 列表（实验性） |
| `disable-model-invocation` | ❌ | 隐藏，只允许 `/skill:name` 手动调用 |

**加载位置**（按优先级）：
- 全局：`~/.pi/agent/skills/`、`~/.agents/skills/`
- 项目：`.pi/skills/`、`.agents/skills/`（含 parent dirs 到 git root）
- Packages：`skills/` 目录或 `package.json` 的 `pi.skills` 字段
- Settings：`skills` 数组（可包含文件或目录）
- CLI：`--skill <path>`（可重复，可与 `--no-skills` 组合）

**调用**：`/skill:name arg1 arg2` —— 参数作为 `User: <args>` 追加到 skill content 之后。

**完整示例**：[`skills.md`](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md) 里的 `brave-search` skill 含 `search.js` + `content.js` 两个 helper 脚本。

**复用现有 skills**：在 `settings.json` 加 `skills: ["~/.claude/skills", "~/.codex/skills"]` 即可导入 Claude Code / Codex 的 skills 目录。

### 3.2 Prompt Templates —— `/name` 命令

**文件格式**：`*.md` + 可选 YAML frontmatter

```markdown
---
description: Review staged git changes
argument-hint: "[path]"
---
Review the staged changes (`git diff --cached`). Focus on:
- Bugs and logic errors
- Security issues
- Error handling gaps
```

**Frontmatter 字段**：
- `description` —— 可选；autocomplete 显示文本（缺省用首行）
- `argument-hint` —— 可选；显示在 description 之前，`<required>` / `[optional]` 标记

**调用语法**：
```
/review
/component Button
/component Button "click handler" "disabled support"
```

**参数占位符**：
- `$1`, `$2`, ... —— 单个位置参数
- `$@` 或 `$ARGUMENTS` —— 全部参数
- `${@:N}` —— 第 N 个起的全部参数（1-indexed）
- `${@:N:L}` —— 第 N 个起的 L 个参数

**加载位置**：与 skills 类似（`prompts/*.md`，`pi.prompts` field，settings 的 `prompts` 数组，`--prompt-template` CLI flag）。**非递归**，子目录需显式声明。

**关闭发现**：`--no-prompt-templates`。

### 3.3 Themes —— JSON 颜色定义

**文件格式**：

```json
{
  "name": "my-theme",
  "vars": {
    "primary": "#00aaff",
    "secondary": 242
  },
  "colors": {
    "accent": "primary",
    "border": "primary",
    "borderAccent": "#00ffff",
    "borderMuted": "secondary",
    "success": "#00ff00",
    "error": "#ff0000",
    "warning": "#ffff00",
    "muted": "secondary",
    "dim": 240,
    "text": "",
    "thinkingText": "secondary"
    /* ... 51 个 token 全部必填 ... */
  }
}
```

**4 种值格式**：
- Hex：`"#ff0000"`
- 256-color：`39`（数字）
- 变量：`"primary"`（引用 vars）
- 默认：`""`（terminal default）

**51 个 color token 必须全定义**，分组：
- Core UI (11)：accent / border / success / error / ...
- Backgrounds & Content (11)：tool box 状态 / message bg / ...
- Markdown (10)：heading / link / code / quote / list / hr
- Tool Diffs (3)：added / removed / context
- Syntax Highlighting (9)：comment / keyword / string / ...
- Thinking Levels (6)：off / minimal / low / medium / high / xhigh
- Bash Mode (1)

**加载位置**：
- 内置：`dark` / `light`（首次启动根据 terminal bg 自动选）
- 全局：`~/.pi/agent/themes/*.json`
- 项目：`.pi/themes/*.json`
- Packages：`themes/` 或 `pi.themes` field
- Settings：`themes` 数组
- CLI：`--theme <path>`（可重复）

**热重载**：编辑当前活动的主题文件立即生效，无需重启。

**导出 HTML**：`colors.export` 块控制 `/export` 输出的 HTML 配色。

---

## 4. Pi Package 打包与分发

### 4.1 目录结构

```
my-pi-package/
├── package.json                # npm 元数据 + pi 资源声明
├── extensions/
│   └── my-extension/
│       ├── index.ts            # extension 入口
│       └── package.json        # 扩展自己的依赖（jiti 解析）
├── skills/
│   └── my-skill/
│       ├── SKILL.md
│       └── helper.js
├── prompts/
│   └── review.md
├── themes/
│   └── my-theme.json
└── README.md
```

### 4.2 package.json 关键字段

```json
{
  "name": "my-pi-package",
  "version": "1.0.0",
  "description": "My Pi extension bundle",
  "type": "module",
  "main": "extensions/my-extension/index.ts",
  "peerDependencies": {
    "@earendil-works/pi-coding-agent": "^0.78.x"
  },
  "pi": {
    "skills": ["./skills"],
    "prompts": ["./prompts"],
    "themes": ["./themes"],
    "extensions": ["./extensions/my-extension"]
  }
}
```

> `pi.*` 字段是 Pi 自己读的，其他工具忽略。也可以走 `pi.skills` / `pi.prompts` / `pi.themes` 单字段。

### 4.3 分发渠道

```bash
# 1. 通过 npm
npm publish
pi install npm:@my-org/pi-tools

# 2. 通过 git
pi install git:github.com/my-org/pi-tools

# 3. 本地路径（开发态）
pi install ./local-path

# 4. 临时加载（不 install）
pi -e ./path/to/extension
```

### 4.4 依赖与隔离

- 扩展自身的 `node_modules` 由 jiti 解析 —— 不会与 Pi 共享
- `npm install --ignore-scripts` 避免 postinstall 跑恶意脚本（Pi 推荐这个 flag）
- `peerDependencies` 声明 Pi 最低版本要求
- Pi 的依赖是 pinned + shrinkwrapped，保证供应链稳定

### 4.5 monorepo 内的 Pi package

`badlogic/pi-mono` 本身就是 4 个包（agent / ai / coding-agent / tui）。社区如果要 fork，可以直接把 monorepo 当 Pi package 用：

```bash
git clone https://github.com/badlogic/pi-mono
cd pi-mono
npm install --ignore-scripts
npm run build
# 在自己的 ~/.pi/agent/extensions/ 里加 symlink
ln -s $(pwd)/packages/coding-agent/examples/extensions/subagent ~/.pi/agent/extensions/subagent
```

---

## 5. SDK / RPC / Print 三种嵌入模式

### 5.1 SDK 模式（Node 进程内）

```typescript
import {
  AuthStorage, createAgentSession, ModelRegistry, SessionManager,
  defineTool, Type,
} from "@earendil-works/pi-coding-agent";

const authStorage = AuthStorage.create();
const modelRegistry = ModelRegistry.create(authStorage);

const { session } = await createAgentSession({
  sessionManager: SessionManager.inMemory(),  // 或 persistent / open(file)
  authStorage,
  modelRegistry,
  cwd: "/path/to/project",
  tools: ["read", "write", "edit", "bash", "grep", "find", "ls"],
  // customTools: [defineTool({...})],
});

session.subscribe((event) => {
  if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
    process.stdout.write(event.assistantMessageEvent.delta);
  }
  if (event.type === "tool_execution_start") {
    console.log(`\n→ ${event.toolName}`);
  }
});

await session.prompt("What files are in the current directory?");
```

**适用**：长驻应用（Slack bot / Web 服务 / CI runner），需要类型安全 + 同步控制。

**关键 API**：
- `createAgentSession({ sessionManager, authStorage, modelRegistry, cwd, tools, customTools, ... })`
- `createAgentSessionRuntime()` —— 包装 session 替换（`newSession` / `switchSession` / `fork` / import）
- `AgentSession` 方法：`prompt` / `steer` / `followUp` / `subscribe` / `setModel` / `setThinkingLevel` / `cycleModel` / `navigateTree` / `compact` / `abort` / `dispose` / `waitForIdle`

**流式约束**：`prompt()` 在 streaming 时必须传 `streamingBehavior: "steer" | "followUp"`，否则抛错。

### 5.2 RPC 模式（子进程 + JSONL stdio）

```bash
pi --mode rpc --no-session --provider anthropic --model claude-sonnet-4-5
```

**Python 客户端**（来自 `rpc.md`）：

```python
import subprocess, json

proc = subprocess.Popen(
    ["pi", "--mode", "rpc", "--no-session"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
)

def send(cmd):
    proc.stdin.write(json.dumps(cmd) + "\n")
    proc.stdin.flush()

send({"type": "prompt", "message": "Hello!"})

for line in proc.stdout:
    event = json.loads(line)
    if event.get("type") == "message_update":
        delta = event.get("assistantMessageEvent", {})
        if delta.get("type") == "text_delta":
            print(delta["delta"], end="", flush=True)
    if event.get("type") == "agent_end":
        print(); break
```

**Node 客户端**（带正确的 JSONL reader，避免 `readline` 的 Unicode separator bug）：

```javascript
const { spawn } = require("child_process");
const { StringDecoder } = require("string_decoder");

const agent = spawn("pi", ["--mode", "rpc", "--no-session"]);

function attachJsonlReader(stream, onLine) {
    const decoder = new StringDecoder("utf8");
    let buffer = "";
    stream.on("data", (chunk) => {
        buffer += typeof chunk === "string" ? chunk : decoder.write(chunk);
        while (true) {
            const i = buffer.indexOf("\n");
            if (i === -1) break;
            let line = buffer.slice(0, i);
            buffer = buffer.slice(i + 1);
            if (line.endsWith("\r")) line = line.slice(0, -1);
            onLine(line);
        }
    });
}

attachJsonlReader(agent.stdout, (line) => {
    const event = JSON.parse(line);
    if (event.type === "message_update" && event.assistantMessageEvent.type === "text_delta") {
        process.stdout.write(event.assistantMessageEvent.delta);
    }
});

agent.stdin.write(JSON.stringify({ type: "prompt", message: "Hello" }) + "\n");
```

**适用**：任何语言、任何进程（IDE 集成、editor 插件、CI 调度）。

**核心命令清单**：`prompt` / `steer` / `follow_up` / `abort` / `new_session` / `get_state` / `get_messages` / `set_model` / `cycle_model` / `get_available_models` / `set_thinking_level` / `cycle_thinking_level` / `set_steering_mode` / `set_follow_up_mode` / `compact` / `set_auto_compaction` / `set_auto_retry` / `abort_retry` / `bash` / `abort_bash` / `get_session_stats` / `export_html` / `switch_session` / `fork` / `clone` / `get_fork_messages` / `get_last_assistant_text` / `set_session_name` / `get_commands`

**事件流**：`agent_start` / `agent_end` / `turn_start` / `turn_end` / `message_start` / `message_update` / `message_end` / `tool_execution_start` / `tool_execution_update` / `tool_execution_end` / `queue_update` / `compaction_start` / `compaction_end` / `auto_retry_start` / `auto_retry_end` / `extension_error`

### 5.3 Print 模式（单轮 headless）

```bash
pi -p "What files are in the current directory?"
# 或批量
pi -p "$(cat task.md)" < file.json
```

适用：CI / 一次性脚本 / bash pipeline。

### 5.4 三种模式对比

| 维度 | SDK | RPC | Print |
|------|-----|-----|-------|
| 进程模型 | 同一进程 | 子进程 | 单次 fork+exec |
| 类型安全 | ✅ TS | ❌ JSON | ❌ |
| 流式响应 | ✅ 事件订阅 | ✅ 事件订阅 | ❌（等全部） |
| 多轮对话 | ✅ | ✅ | ❌ |
| 跨语言 | ❌（仅 Node） | ✅ 任意 | ✅ 任意 shell |
| 隔离 | ❌ | ✅ | ✅ |
| 启动成本 | ~0 | 进程启动 | 进程启动 |

---

## 6. 编辑器 / IDE 集成模式

### 6.1 总思路

编辑器集成 Pi 的标准方案是 **RPC 模式**。编辑器 spawn `pi --mode rpc` 子进程，通过 JSONL stdio 通信，把 agent 当后台服务用。

### 6.2 集成层级

**Level 1：terminal emulator**（最简）

- 编辑器自带的 terminal 里跑 `pi`
- 用户自己切窗口
- 0 集成成本

**Level 2：embedded TUI**

- 编辑器用 terminal 控件嵌入 Pi TUI（如 VS Code 的 `vscode.xterm`）
- 通过 terminal 控件与 Pi 交互
- 不需要 RPC

**Level 3：side panel**（RPC）

- 编辑器起一个 side panel 显示 agent 输出（流式 text_delta + tool result）
- 用户在编辑器内编辑文件 / 写 prompt
- 编辑器通过 RPC 协议 send / receive

**Level 4：inline completion**（高级 RPC）

- 编辑器把当前 buffer + 选区发给 Pi
- Pi 用 stream 返回补全（类似 Copilot）
- 需要 Pi 支持 partial / context-aware completion（当前未直接支持，可在 prompt 模板中模拟）

### 6.3 VS Code 集成 sketch（Level 3）

```typescript
// extension.ts
import * as vscode from "vscode";
import { spawn } from "child_process";
import { StringDecoder } from "string_decoder";

let piProcess: ReturnType<typeof spawn>;
let outputBuffer: string[] = [];

function startPi() {
  piProcess = spawn("pi", ["--mode", "rpc", "--no-session"], {
    cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
  });
  
  const decoder = new StringDecoder("utf8");
  let buffer = "";
  piProcess.stdout!.on("data", (chunk: Buffer) => {
    buffer += decoder.write(chunk);
    let i;
    while ((i = buffer.indexOf("\n")) !== -1) {
      const line = buffer.slice(0, i);
      buffer = buffer.slice(i + 1);
      handleEvent(line);
    }
  });
}

function handleEvent(line: string) {
  const event = JSON.parse(line);
  switch (event.type) {
    case "message_update":
      if (event.assistantMessageEvent.type === "text_delta") {
        appendToOutput(event.assistantMessageEvent.delta);
      }
      break;
    case "tool_execution_start":
      appendToOutput(`\n[→ ${event.toolName}]\n`);
      break;
    case "agent_end":
      vscode.window.showInformationMessage("Pi finished");
      break;
  }
}

function sendPrompt(text: string) {
  piProcess.stdin!.write(JSON.stringify({
    type: "prompt",
    message: text,
  }) + "\n");
}
```

**关键设计点**：
- 用 `StringDecoder` 而非 `readline`（避免 Unicode separator）
- `ctx.mode === "rpc"` 时扩展 UI 变 request/response 协议（`extension_ui_request` / `extension_ui_response`）
- `ctx.ui.custom()` 在 RPC 模式返回 `undefined`（overlay 不可用）

### 6.4 Neovim 集成 sketch

```lua
-- pi.lua
local M = {}

function M.start()
  local job_id = vim.fn.jobstart({"pi", "--mode", "rpc", "--no-session"}, {
    cwd = vim.fn.getcwd(),
    on_stdout = function(_, data, _)
      if not data then return end
      for _, line in ipairs(data) do
        if line ~= "" then
          local ok, event = pcall(vim.fn.json_decode, line)
          if ok then M.handle_event(event) end
        end
      end
    end,
    on_stderr = function(_, data, _)
      if data then vim.api.nvim_err_writeln(table.concat(data, "\n")) end
    end,
  })
  M.job_id = job_id
end

function M.prompt(text)
  local msg = vim.fn.json_encode({type = "prompt", message = text})
  vim.fn.chansend(M.job_id, msg .. "\n")
end

function M.handle_event(event)
  if event.type == "message_update" then
    local inner = event.assistantMessageEvent
    if inner.type == "text_delta" then
      vim.api.nvim_chan_send(vim.api.nvim_create_buf(false, true), inner.delta)
    end
  end
end

return M
```

`pi dev` 模式下还可以在 `ctx.ui.setEditorComponent` 注册 Vim 模式编辑器（在 TUI 内用 Vim 按键绑定）。

---

## 7. 5 个常见定制 workflow 配方

### 配方 1：我公司有自建 LLM 网关

**问题**：需要把 Pi 接到公司内部 OpenAI 兼容代理（带 OAuth / 证书 / 审计）。

**步骤**：
1. 复制 `examples/extensions/custom-provider-anthropic` 到 `~/.pi/agent/extensions/`
2. 改 provider 配置：
   ```typescript
   pi.registerProvider("company-llm", {
     baseUrl: "https://llm.internal.company.com",
     apiKey: "$COMPANY_LLM_TOKEN",
     api: "openai-completions",  // 或 openai-responses / anthropic-messages
     models: [
       {
         id: "company-claude-4",
         name: "Company Claude 4",
         reasoning: true,
         input: ["text", "image"],
         cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },  // 内部不计费
         contextWindow: 200000,
         maxTokens: 64000,
       },
     ],
   });
   ```
3. 如果需要自定 header / 证书 / OAuth，复用 `login` + `getApiKey` 模式
4. 跑 `/login company-llm` 走 OAuth；或 `export COMPANY_LLM_TOKEN=...` 走 API key
5. `/model` 选 `company-llm/company-claude-4`

**Gotcha**：复用一个 `api: "anthropic-messages"` 即可走 pi-ai 内置的流式实现；只有需要差异化行为时才自写 `streamSimple`。

### 配方 2：执行任何命令前要求人工确认（permission popup）

**问题**：默认 Pi 信任所有 bash 命令；想要 Claude Code 那种 per-command allow/deny。

**步骤**：用 `tool_call` 事件阻断危险命令：

```typescript
const DANGEROUS_PATTERNS = [
  /\brm\s+(-[a-zA-Z]*)?-?[rf]+\b/,  // rm -rf
  /\bsudo\b/,
  /\bdd\s+/,
  /\bmkfs\b/,
  /\b(shutdown|reboot|halt)\b/,
  /\bcurl\s+.*\|\s*(sh|bash)\b/,
];

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return;
    const cmd = (event.input as any).command || "";
    
    for (const pat of DANGEROUS_PATTERNS) {
      if (pat.test(cmd)) {
        const ok = await ctx.ui.confirm(
          "Dangerous command",
          `Allow execution?\n\n${cmd}`,
        );
        if (!ok) {
          return { block: true, reason: "Denied by user (matches dangerous pattern)" };
        }
        break;
      }
    }
  });
}
```

**Gotcha**：
- `isToolCallEventType("bash", event)` 是 typebox-style 收窄 type guard
- 只在 `ctx.hasUI === true` 时才能用 `ctx.ui.confirm`（TUI/RPC 模式）
- 想要 sandbox-exec 级别的真隔离，直接用 `examples/extensions/sandbox`

### 配方 3：跨 session 记忆项目事实

**问题**：每个 session 都要重新告诉 Pi 项目背景；想让 Pi 记住"我们用 PostgreSQL + Redis + GraphQL"这种项目级事实。

**方案 A：AGENTS.md（最简）**

写一份 `.pi/AGENTS.md`：

```markdown
# Project Context

## Stack
- PostgreSQL 16 (primary database)
- Redis 7 (cache + session store)
- GraphQL via Apollo Server 4
- TypeScript / Node 22 / Fastify

## Conventions
- All API responses are wrapped in `{ data, errors }`
- Use Drizzle ORM, never raw SQL
- Tests use Vitest + Supertest
- Never use `any` in TypeScript

## Architecture
- `src/server/` - HTTP layer
- `src/graphql/` - schema + resolvers
- `src/db/` - Drizzle schemas
- `src/services/` - business logic
```

Pi 自动加载 `.pi/AGENTS.md` 到 system prompt。

**方案 B：自定义 extension + SQLite**（更结构化）

```typescript
import Database from "better-sqlite3";
import { join } from "node:path";
import { existsSync, mkdirSync } from "node:fs";

const dbPath = join(process.env.HOME!, ".pi/memory.sqlite");
const db = new Database(dbPath);
db.exec(`
  CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE,
    value TEXT,
    source TEXT,
    created_at INTEGER DEFAULT (unixepoch()),
    updated_at INTEGER DEFAULT (unixepoch())
  )
`);

export default function (pi: ExtensionAPI) {
  // 启动时把所有 facts 注入 system prompt
  pi.on("before_agent_start", (event, ctx) => {
    const facts = db.prepare("SELECT key, value FROM facts").all() as Array<{key: string, value: string}>;
    if (facts.length === 0) return;
    const factBlock = facts
      .map(f => `- ${f.key}: ${f.value}`)
      .join("\n");
    return {
      systemPrompt: event.systemPrompt + `\n\n## Project Memory (persistent)\n\n${factBlock}\n`,
    };
  });

  // 提供 /remember 命令
  pi.registerCommand("remember", {
    description: "Add a fact to project memory",
    handler: async (args, ctx) => {
      const [key, ...rest] = args.split(" ");
      const value = rest.join(" ");
      if (!key || !value) {
        ctx.ui.notify("Usage: /remember <key> <value>", "warning");
        return;
      }
      db.prepare(`
        INSERT INTO facts (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=unixepoch()
      `).run(key, value);
      ctx.ui.notify(`Remembered: ${key}`, "info");
    },
  });

  // 提供 /forget 命令
  pi.registerCommand("forget", {
    description: "Remove a fact from project memory",
    handler: async (args, ctx) => {
      const result = db.prepare("DELETE FROM facts WHERE key = ?").run(args.trim());
      ctx.ui.notify(result.changes > 0 ? `Forgot: ${args}` : "Not found", "info");
    },
  });
}
```

**Gotcha**：
- `before_agent_start` 是注入 system prompt 的标准时机（不要用 `agent_start`，那时已发请求）
- SQLite 文件建议放 `~/.pi/memory.sqlite`（不进 repo）
- 想做"自动学习"：用 `agent_end` 让模型总结对话，把新事实 INSERT 进 DB

### 配方 4：从编辑器驱动 Pi

**问题**：想用 VSCode / Neovim 的快捷键触发 Pi 任务，把当前 buffer / 选区当 context 传给 Pi。

**步骤**：
1. 按 6.3 / 6.4 的 sketch 实现编辑器扩展
2. 在编辑器里跑 `pi --mode rpc` 子进程
3. 用 `get_state` 命令查 Pi 当前状态
4. 把 prompt 通过 `prompt` 命令发过去；用 `streamingBehavior: "steer"` 在 streaming 时追加
5. 监听 `message_update` 事件把 text_delta 流式写回编辑器 buffer

**Gotcha**：
- `prompt` 在 streaming 时必须传 `streamingBehavior`；否则抛错
- `ctx.ui.custom()` 在 RPC 模式下不可用，扩展要 fallback
- `extension_ui_request` 子协议：扩展的 `ctx.ui.confirm` 等会变成 request；客户端要正确回 `extension_ui_response`
- 跨进程 abort：编辑器退出前先发 `abort` 命令等 agent_end，再 kill 子进程

### 配方 5：让 Pi 在动手前先计划

**问题**：想要 Claude Code 那种"先 plan，确认后再执行"的工作流。

**步骤**：直接装 `examples/extensions/plan-mode`：

```bash
cp -r packages/coding-agent/examples/extensions/plan-mode ~/.pi/agent/extensions/
cd ~/.pi/agent/extensions/plan-mode && npm install
pi -e ~/.pi/agent/extensions/plan-mode
```

**它做的工作**：
1. `/plan` (或 Ctrl+Alt+P) 切换 plan mode
2. plan mode 下，工具集替换为 `["read", "bash", "grep", "find", "ls", "questionnaire"]`（无 write/edit）
3. `tool_call` 事件对 bash 用 `isSafeCommand` 闸门；不安全命令直接阻断
4. `before_agent_start` 注入 `plan-mode-context` 隐藏消息，要求模型输出 `Plan: 1. ... 2. ...` 格式
5. `agent_end` 时 `extractTodoItems` 解析步骤，弹 `ctx.ui.select` 让用户选 **Execute** / **Stay** / **Refine**
6. 选 Execute → 切回 `["read", "bash", "edit", "write"]` 工具集开始干活
7. 执行期间 `turn_end` 扫 `[DONE:n]` 标记更新 todo widget
8. 状态用 `appendEntry("plan-mode", ...)` 持久化，`session_start` 时恢复

**想自定义**：fork 这个 extension，改 `isSafeCommand`（更宽松 / 更严），改 `extractTodoItems`（不同 marker 格式），加项目特定的 plan 模板。

---

## 8. 常见陷阱与最佳实践

### 8.1 扩展加载顺序

Pi 按以下顺序加载扩展：
1. 全局 `~/.pi/agent/extensions/` 下的所有 extension
2. 项目 `.pi/extensions/` 下的所有 extension（覆盖全局同名）
3. 资源（skill/prompt/theme）也按这个顺序合并
4. 后加载的 extension 注册的 tool/command 会覆盖先加载的（同 name）

**陷阱**：如果你装了 `subagent` example 又装了 `oh-my-pi`，两个 `subagent` tool 会冲突。`oh-my-pi` 的会赢因为它后加载。

**最佳实践**：在项目 `.pi/extensions/` 加自己的 local extension，避免污染全局。

### 8.2 持久化状态

- `appendEntry(customType, data?)` —— 把任意 JSON 状态写进 session JSONL
- `session_start` 时再读回来（用 `ctx.sessionManager.getEntriesByType("my-custom")`）
- 不要写文件到 `~/.pi/` 以外的地方，session 跨机器同步会丢

### 8.3 异步与 abort

- 所有 `execute` / event handler 都应该尊重 `signal.aborted`
- spawn 子进程时把 `signal` 转发过去，自己用 `signal.addEventListener("abort", ...)` 监听
- 长任务（如 `subagent` 的链式调用）记得用 `mapWithConcurrencyLimit` 限并发（4-8）

### 8.4 Token 预算

- 系统 prompt + 工具定义就 < 1000 tokens（设计目标）
- 每个 `registerTool` 的 `description` + `promptSnippet` + `promptGuidelines` 都会进 system prompt，**慎用** `promptGuidelines`，会让 prompt 膨胀
- 想要 per-tool usage hints 放到 `promptSnippet` 一行；详细行为放 `description`

### 8.5 TUI 自定义渲染

- `renderCall` / `renderResult` 只在 `ctx.hasUI === true` 时被调用
- 复用 pi-tui 的 `Container` / `Text` / `Markdown` / `Spacer` 组件
- 用 `theme.fg(colorToken, text)` 而不是 hardcode hex，保持主题切换可用
- `truncateHead` / `truncateTail` / `truncateLine` 防止输出过长

### 8.6 RPC 模式边界

- `ctx.mode === "rpc"` 且 `ctx.hasUI === true`
- `ctx.ui.custom()` 返回 `undefined`（overlay 不可用）
- `ctx.ui.setFooter` / `setHeader` 是 no-op
- theme 相关方法降级
- 复杂的 UI 交互要走 `extension_ui_request` / `extension_ui_response` 子协议

### 8.7 Session tree 复杂度

- 每次 fork / clone 创建一个新 branch；JSONL 文件会越来越大
- 定期 `/compact` 或用 `set_auto_compaction` 自动触发
- 想分享 session 用 `/export <file>`（HTML）或 `/share`（GitHub gist）

### 8.8 供应链安全

- 安装 extension 一律 `npm install --ignore-scripts`（避免 postinstall 跑恶意脚本）
- Pi 自己 monorepo 的依赖是 pinned + shrinkwrapped
- 装第三方 Pi package 前先读 source（extensions "run with full system access"）

---

## 关键 URL 索引

### 官方文档（主仓库 docs/）
- https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/extensions.md
- https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/skills.md
- https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/prompt-templates.md
- https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/themes.md
- https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/sdk.md
- https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md

### 官方示例
- https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions

### 配套笔记
- [`pi-agent.md`](./pi-agent.md) —— Pi 核心架构与三大实现
- [`pi-agent-ecosystem.md`](./pi-agent-ecosystem.md) —— 扩展生态与设计哲学
- [`pi-agent-comparison.md`](./pi-agent-comparison.md) —— 与其他 Agent 框架的对比

---

## License

MIT License

---
