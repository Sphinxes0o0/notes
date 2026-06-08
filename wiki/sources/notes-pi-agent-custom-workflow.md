---
type: source
source-type: notes
title: "Pi 定制 Workflow 实操 — 扩展开发完整生命周期 + 5 个配方"
author: "Sphinx (notes/coding_agent/pi-agent-custom-workflow.md)"
date: 2026-06-05
size: large
path: ../repos/notes/coding_agent/pi-agent-custom-workflow.md
summary: "Pi 定制 workflow 实战手册：扩展本质/事件清单/生命周期时序/ExtensionContext API/ExtensionAPI 全方法/自定义 UI + Skills/Prompt Templates/Themes/Pi Package 打包 + SDK/RPC/Print 三种嵌入 + 5 个真实 workflow 配方"
tags: [pi-agent, extension-api, sdk, rpc, customization, recipe]
sources: [entity-pi-agent]
related: [notes-pi-agent, synthesis/comparison-terminal-coding-agents-2026-06, notes-pi-agent-ecosystem]
created: 2026-06-05

---

# Pi 定制 Workflow 实操（Source）

> Source: `~/workspace/repos/notes/coding_agent/pi-agent-custom-workflow.md` (43KB / 1193 行)
> 抓取日期: 2026-06-05

## 1. 扩展开发完整生命周期

### 1.1 扩展的本质

一个扩展 = 一个导出 `default function(pi: ExtensionAPI)` 的 TypeScript 模块。可以注册事件订阅、工具、命令、UI 组件、CLI flag、自定义 provider 等。

```typescript
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // 同步或异步都可
}
```

**安装位置**:
- 全局: `~/.pi/agent/extensions/*.ts` 或 `*/index.ts`
- 项目: `.pi/extensions/*.ts` 或 `*/index.ts`
- 临时: `pi -e ./path/to/extension`

**可导入包**:
- `@earendil-works/pi-coding-agent` — ExtensionAPI、helper 类型
- `typebox` — 工具参数 schema
- `@earendil-works/pi-ai` — AI 工具 (如 `StringEnum`)
- `@earendil-works/pi-tui` — TUI 组件

### 1.2 事件完整清单 (按生命周期阶段)

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
| Agent | `agent_start` / `agent_end` | `(event, ctx) => void` | ❌ | ❌ |
| Turn | `turn_start` / `turn_end` | `(event, ctx) => void` | ❌ | ❌ |
| Message | `message_start` / `message_update` | `(event, ctx) => void` | ❌ | ❌ |
| Message | `message_end` | `(event, ctx) => { message: modified }` | ❌ | ✅ 改消息 |
| Tool | `tool_execution_start/update/end` | `(event, ctx) => void` | ❌ | ❌ |
| Tool | `context` | `(event, ctx) => { messages: filtered }` | ❌ | ✅ 改 messages (深拷贝安全) |
| Provider | `before_provider_request` | `(event, ctx) => { ...event.payload, temperature: 0 }` | ❌ | ✅ 改 payload |
| Provider | `after_provider_response` | `(event, ctx) => void` (仅 status / headers) | ❌ | ❌ |
| Model | `model_select` / `thinking_level_select` | `(event, ctx) => void` (后者通知) | ❌ | ❌ |
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

### 1.4 ExtensionContext API (ctx)

**属性**: `ctx.ui`, `ctx.mode` (`"tui" | "rpc" | "json" | "print"`), `ctx.hasUI`, `ctx.cwd`, `ctx.sessionManager`, `ctx.modelRegistry` / `ctx.model`, `ctx.signal` (AbortSignal)

**方法**: `ctx.isIdle()` / `ctx.abort()` / `ctx.hasPendingMessages()`, `ctx.shutdown()`, `ctx.getContextUsage()`, `ctx.compact({ customInstructions, onComplete, onError })` (不 await), `ctx.getSystemPrompt()`

**ExtensionCommandContext** (仅 command handler 内):
- `ctx.getSystemPromptOptions()` / `ctx.waitForIdle()` / `ctx.newSession({ parentSession, setup, withSession })` / `ctx.fork(entryId, { position, withSession })` / `ctx.navigateTree(targetId, options?)` / `ctx.switchSession(sessionPath, options?)` / `ctx.reload()`

### 1.5 ExtensionAPI 全方法

```typescript
pi.on(event, handler)                              // 订阅事件
pi.registerTool(definition)                        // 注册自定义工具
pi.sendMessage(message, options?)                  // 注入自定义消息
pi.sendUserMessage(content, options?)              // 发送 user 消息
pi.appendEntry(customType, data?)                  // 持久化扩展状态
pi.setSessionName(name)                            // 设置/获取 session 名
pi.setLabel(entryId, label)                        // 给 entry 加/清标签
pi.registerCommand(name, options)                  // 注册 slash 命令
pi.getCommands()                                   // 拿所有可调用的命令
pi.registerMessageRenderer(customType, renderer)   // TUI 自定义渲染
pi.registerShortcut(shortcut, options)             // 键盘快捷键
pi.registerFlag(name, options)                     // CLI flag
pi.exec(command, args, options?)                   // 调 shell
pi.getActiveTools() / getAllTools() / setActiveTools(names)  // 工具集管理
pi.setModel(model)                                 // 切换模型
pi.getThinkingLevel() / setThinkingLevel(level)    // 思考等级
pi.events                                          // inter-extension event bus
pi.registerProvider(name, config)                  // 注册/覆盖 LLM provider
pi.unregisterProvider(name)                        // 移除 provider
```

### 1.6 自定义 UI 完整 API (部分)

```typescript
// 对话框 (阻塞等用户响应)
const choice = await ctx.ui.select("Pick:", ["A", "B", "C"]);
const ok = await ctx.ui.confirm("Delete?", "Cannot be undone");
// (详细: 详见源文档 line 145-250)
```

## 2. 3 种轻量扩展

### 2.1 Skills

- 位置: `~/.pi/agent/skills/<name>/SKILL.md` 或 `.pi/skills/<name>/SKILL.md`
- 触发: slash 命令 `/skill-name`
- 内容: Markdown + YAML frontmatter (description, when-to-use)
- 详见 Pi 官方 docs `skills.md`

### 2.2 Prompt Templates

- 位置: `~/.pi/agent/prompts/<name>.md` 或 `.pi/prompts/<name>.md`
- 触发: slash 命令 `/prompt-name`
- 用途: 把常用 prompt 模板化 (`/review` `/commit` `/explain`)

### 2.3 Themes

- 位置: `~/.pi/agent/themes/<name>.json` 或 `.pi/themes/<name>.json`
- 内置主题: `dark`, `light`
- 自定义: JSON 配色文件

## 3. Pi Package 打包

- 把多个 extension + skill + prompt + theme 打包成一个 npm package
- Scope: `@earendil-works/pi-*`
- 安装: `npm i -g --ignore-scripts <package>`

## 4. SDK / RPC / Print 三种嵌入模式

详见 [[notes-pi-agent]] 第 254-262 行和源文档第 800-1100 行 (本转写未截取, 详见源文档)。

- **SDK**: 嵌入 Node.js 应用 (`@earendil-works/pi-coding-agent` 作为库)
- **RPC**: JSON-RPC over stdin/stdout (`--mode rpc`), IDE 集成
- **Print**: 单轮 headless (`-p "..."`), 适合 CI / 脚本

## 5. 5 个真实定制 workflow 配方 (概要)

> 详细代码与步骤见源文档 (本转写仅列标题, 详见 `pi-agent-custom-workflow.md` 第 800-1193 行)

1. **配方 A**: 自动 PR description 生成 (用 `tool_call` 事件 + 改 input 注入)
2. **配方 B**: 跨项目 session 共享 (用 `fork` + `withSession` + `setSessionName`)
3. **配方 C**: 自定义 provider 接入 Bedrock (用 `registerProvider` + 复写 `custom-provider-anthropic` 模板)
4. **配方 D**: 长程 compaction 自定义 (用 `session_before_compact` 注入 `compaction` 对象)
5. **配方 E**: 团队级 AGENTS.md 同步 (用 `resources_discover` 动态注册)

## 相关页面

- [[entities/pi-agent.md]] — Pi Agent entity
- [[notes-pi-agent]] — 主体笔记
- [[synthesis/comparison-terminal-coding-agents-2026-06]] — 7 agent 横向对比
- [[notes-pi-agent-ecosystem]] — 9 扩展示例 + MCP 桥接
