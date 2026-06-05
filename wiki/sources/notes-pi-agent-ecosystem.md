---
type: source
source-type: notes
title: "Pi 扩展生态与能力 — 9 官方示例 + MCP 曲线救国 + SDK 嵌入"
author: "Sphinx (notes/coding_agent/pi-agent-ecosystem.md)"
date: 2026-06-05
size: medium
path: ../repos/notes/coding_agent/pi-agent-ecosystem.md
summary: "Pi 扩展生态深度：主仓 9 个官方 example extension 逐个解析（subagent / sandbox / gondolin / custom-provider-anthropic 详解）+ MCP 桥接（mcporter）+ SDK 嵌入案例 + 作者公开设计哲学"
tags: [pi-agent, extension, mcp, mcporter, sdk, custom-provider, sandbox, gondolin]
sources: [entity-pi-agent]
related: [notes-pi-agent, synthesis/comparison-terminal-coding-agents-2026-06, notes-pi-agent-custom-workflow]
---

# Pi 扩展生态与能力（Source）

> Source: `~/workspace/repos/notes/coding_agent/pi-agent-ecosystem.md` (22KB / 396 行)
> 抓取日期: 2026-06-05

## 1. 官方扩展示例 (9 个)

主仓 [`packages/coding-agent/examples/extensions/`](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/examples/extensions) 下只有 9 个 example extension,每个展示一个独立扩展 API 切面:

| 目录 | 定位 | 展示能力 |
|------|------|---------|
| `custom-provider-anthropic` | 自定义 LLM provider (OAuth + API key 双模式) | `registerProvider` + 完整 streaming |
| `custom-provider-gitlab-duo` | GitLab Duo 接入 (Anthropic + OpenAI Responses 复用 pi-ai) | OAuth + 复用 pi-ai 内置 stream |
| `doom-overlay` | TUI overlay 跑 DOOM (35 FPS) | `ctx.ui.custom({ overlay: true })` |
| `dynamic-resources` | 动态注册 skill/prompt/theme 路径 | `resources_discover` 事件 |
| `gondolin` | 所有工具路由到本地 QEMU 微型 VM | 替换 `BashOperations` |
| `plan-mode` | 计划模式 (只读,扫描 `[DONE:n]` 标记) | `registerFlag`/`registerCommand`/`tool_call` 阻断/状态持久化 |
| `sandbox` | OS 级沙箱 (macOS sandbox-exec / Linux bubblewrap) | 替换 `bash` 工具 + `user_bash` 事件 |
| `subagent` | 子代理委派 (single/parallel/chain 三模式) | `registerTool` + 子进程 spawn + 复杂 render |
| `with-deps` | 扩展自带 npm 依赖 (jiti 从扩展自身 `node_modules` 解析) | 依赖打包 |

> **学习建议**: 先读 `dynamic-resources` (最简, 30 行), 再 `with-deps` (单 tool + 依赖), 最后挑完整示例 (`subagent` / `sandbox` / `gondolin`) 做 walkthrough。

### 1.1 subagent — 子代理委派工程范本

源文件 `subagent/index.ts` 约 700 行,**生产级**子代理工具完整实现:

- **三种执行模式**:
  - `single`: `{ agent: "name", task: "..." }`
  - `parallel`: `{ tasks: [{ agent, task }, ...] }`,并发上限 4 (`MAX_CONCURRENCY`)
  - `chain`: `{ chain: [...] }`, `{previous}` 占位符注入上一步输出
- **子代理发现**: `discoverAgents(ctx.cwd, agentScope)` 扫描 `~/.pi/agent/agents/` (user) 和 `.pi/agents/` (project)
- **执行方式**: spawn 新 `pi --mode json -p --no-session` 子进程;通过 stdout JSON 事件流回收消息、tool result、usage
- **安全**: 当 `agentScope: "project" | "both"` 时,弹出 `ctx.ui.confirm` 让用户确认是否信任 project-local agent (防御 repo-controlled prompt injection)
- **Abort 传播**: 监听 `signal.aborted`, 先 SIGTERM, 5 秒未退出升级 SIGKILL
- **TUI 渲染**: `renderCall`/`renderResult` 分层展示 (单条/链式/并行), 含 token/cost 统计
- **输出截断**: `PER_TASK_OUTPUT_CAP = 50 * 1024` bytes/task

**关键设计点**: 用 `getPiInvocation` 函数识别当前是直接跑 `pi` 还是通过 `node/bun` 跑 (`bunfs` 虚拟路径 vs 真实路径) — 解决开发态 vs 安装态调用差异。

### 1.2 sandbox — OS 级沙箱标准接法

源文件 `sandbox/index.ts` 约 230 行,把内置 `bash` 替换为走 `@anthropic-ai/sandbox-runtime` 的版本:

- **平台差异**: macOS → `sandbox-exec` (Seatbelt);Linux → `bubblewrap` (需额外装 `bubblewrap`, `socat`, `ripgrep`)
- **配置层叠**: `~/.pi/agent/extensions/sandbox.json` (global) ⊕ `<cwd>/.pi/sandbox.json` (project), project 优先
- **关键钩子**:
  - `registerFlag("no-sandbox", ...)` 关闭
  - `registerTool({ ...localBash, label: "bash (sandboxed)", ... })` 覆盖内置
  - `pi.on("user_bash", () => ({ operations: createSandboxedBashOps() }))` 拦截用户 `!` 命令
  - `pi.on("session_shutdown", async () => { await SandboxManager.reset() })` 清理
- **典型 `.pi/sandbox.json`**:

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

**设计模式**: 不修改工具定义本体,而是在每次 `execute` 时用 `createBashTool(localCwd, { operations })` 重新创建工具实例 — "operations 注入" 是 `pi-coding-agent` 内置工具的扩展点。

### 1.3 gondolin — 微型 VM 沙箱

源文件 `gondolin/index.ts` 约 360 行,用 `@earendil-works/gondolin` (Mario Zechner 的 micro-VM 项目) 在 QEMU 中跑 pi:

- **架构**: 宿主 cwd 挂载到 guest 的 `/workspace` (`RealFSProvider`),其他 guest 写入隔离
- **全面替换**: 7 个内置工具 (read/write/edit/bash/ls/find/grep) 全部路由到 VM 内
- **路径转换**: `hostPathToGuest` / `toGuestPath` 处理 host↔guest 路径映射
- **状态机**: `vm` 持有当前 VM 实例;`vmStarting` 是 Promise 用于去重启动
- **生命周期**: `session_start` → 启动 VM;`session_shutdown` → `await activeVm.close()`;`user_bash` 事件 → 同样走 VM 内 bash;`before_agent_start` → 修改 `systemPrompt`
- **setup 成本**: Node ≥ 23.6.0 + QEMU;适合"代码生成后必须在干净环境跑测试"的工作流

### 1.4 custom-provider-anthropic — 完整 Provider 实现参考

源文件约 430 行,**手写**了 Anthropic streaming (不复用 pi-ai 内置):

- **OAuth PKCE 流程**: `generatePKCE` → `loginAnthropic` (callback 拿 code → exchange token) → `refreshAnthropicToken`
- **OAuth vs API key 区分**: `isOAuthToken(apiKey) → apiKey.includes("sk-ant-oat")`
- **OAuth "stealth mode"** (绕过 Anthropic 对非 Claude Code 工具的限流):
  - 工具名映射成 Claude Code 工具名 (`Read`/`Write`/`Edit`/...)
  - 设置 `claude-cli/2.1.2 (external, cli)` user-agent
  - 加 `claude-code-20250219,oauth-2025-04-20` beta 头
  - system prompt 强制以 "You are Claude Code, Anthropic's official CLI for Claude." 开头
- **流式事件映射**: 把 Anthropic 的 `content_block_start/delta/stop` + `message_delta` 翻译成 pi-ai 的统一 `AssistantMessageEventStream` 事件
- **Cache control**: 自动在最后一条 user message 的最后一块加 `cache_control: { type: "ephemeral" }`,最大化 prompt cache 命中率

**实战价值**: 接 Bedrock custom endpoint、Azure OpenAI、自建 OpenAI 兼容代理,都以此为模板。

## 2. MCP 集成: 曲线救国

Pi 官方明确**不**支持 MCP (见 [[notes-pi-agent]] 第 264-274 行 NOT INCLUDE 节)。但社区有标准方案:

### 2.1 MCPorter — MCP 桥接器

- Repo: [`openclaw/mcporter`](https://github.com/openclaw/mcporter) (MIT, 4.6k stars, 原 `steipete/mcporter` 已迁至 openclaw org)
- 作用: 把 MCP server 暴露给不支持 MCP 的 agent (如 Pi)
- 详情见笔记第 121-150 行 (本转写未截取, 详见源文档)

## 3. SDK 嵌入

Pi 的 SDK 模式让 Pi 可以作为库嵌入 Node.js 应用:

- 包名: `@earendil-works/pi-coding-agent` (含 SDK 入口)
- 用法: 详见 [[notes-pi-agent-custom-workflow]] 的 SDK/RPC/Print 三种嵌入模式

## 4. 故意缺失能力的社区实现

Pi 核心故意不含 (subagent / MCP / permission popup / plan mode / todo / background bash),但都有社区 example extension:

- subagent → `subagent/` (见 1.1)
- sandbox → `sandbox/` (见 1.2)
- plan-mode → `plan-mode/`
- VM 沙箱 → `gondolin/` (见 1.3)

## 5. 作者公开设计哲学

来自 Mario Zechner 的 [launch blog (2025-11-30)](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/):

- **核心刻意做小**: 只保留必要 LLM 交互 primitive (context + tool call + streaming + session)
- **扩展即代码** (非 prompt-level skills): 每个扩展是普通 TS 模块,可读可改可 fork
- **provider 无关**: 4 个底层 API 覆盖 40+ LLM provider
- **JSONL tree session**: 状态可序列化、可分享、可 fork
- **故意缺失**: subagent/MCP/plan mode 等推到 example 层,不污染核心

## 相关页面

- [[entity-pi-agent]] — Pi Agent entity
- [[notes-pi-agent]] — 主体笔记
- [[synthesis/comparison-terminal-coding-agents-2026-06]] — 7 agent 横向对比
- [[notes-pi-agent-custom-workflow]] — 扩展开发生命周期 + 5 个 workflow 配方
