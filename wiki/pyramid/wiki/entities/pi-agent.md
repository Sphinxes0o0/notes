---
type: entity
tags: [pi-agent, coding-agent, terminal-agent, typescript, rust, extension, mcp, sdk, agent-framework]
created: 2026-06-05
sources: [notes-pi-agent, synthesis/comparison-terminal-coding-agents-2026-06, notes-pi-agent-ecosystem, notes-pi-agent-custom-workflow]
---

# Pi Agent (π Agent)

> **定义**: Pi Agent 是一个**最小化、可扩展**的 terminal AI coding harness 框架。核心刻意做小 (只保留 LLM 交互的最小积木), 把扩展抽象做到极薄 (每个扩展是一个普通 TS 模块), 通过 TypeScript extensions / skills / prompt templates / themes / pi packages 5 层扩展机制向外生长。
>
> **作者**: Mario Zechner (`badlogic` on GitHub);2025-11-30 发布 coding-agent 包。
>
> **关键仓库** (2026-06-05):
> - 主仓 (canonical): [`badlogic/pi-mono`](https://github.com/badlogic/pi-mono) — 59.9k stars, MIT (公司 org 镜像 `earendil-works/pi` 是同一份代码)
> - Fork: [`can1357/oh-my-pi`](https://github.com/can1357/oh-my-pi) — 10.6k stars, MIT, 集成 IDE wiring + LSP/DAP
> - 端口: [`Dicklesworthstone/pi_agent_rust`](https://github.com/Dicklesworthstone/pi_agent_rust) — 1.1k stars, MIT+Rider, Rust 零 unsafe 单二进制

## 一句话定位

> "Primitives, not batteries-included."

Pi Agent 的设计哲学: 给开发者**LLM 交互的最小积木** (context + tool call + streaming + session), 不试图把 harness 做厚。Claude Code 那种 "每个交互细节都决策好" 的工作台定位, 与 Pi 正好相反 — 一个比喻: **Pi 像 `tmux` + `Emacs` 的可拼装内核, Claude Code 像 VSCode 的开箱工作台。**

## 3 大实现横向

| 实现 | 语言 | Stars | 启动 | 内存 | 工具数 | 关键差异 |
|------|------|------|------|------|--------|----------|
| `badlogic/pi-mono` (主) | TypeScript/Node | 59.9k | ~200ms | ~150MB | 8 (read/write/edit/bash/grep/find/ls + 自定义) | 原始实现, npm 生态 |
| `can1357/oh-my-pi` | TS + Rust + Bun | 10.6k | ~150ms | ~120MB | **32 内置** + subagent + DAP/LSP | IDE 集成, 多语言 sandbox |
| `pi_agent_rust` | Rust | 1.1k | **<100ms** | **<50MB** (空闲) | 8 + QuickJS | 静态单二进制 ~21MB, capability-based 沙箱 |

> 数据来源: [[notes-pi-agent]] + [[synthesis/comparison-terminal-coding-agents-2026-06]] "重要更正" 节。

## 核心架构

### Monorepo 4 包

```
@earendil-works/pi-coding-agent  # 交互式 CLI (TUI/Print/RPC/SDK 4 模式)
@earendil-works/pi-agent-core    # agent 运行时: 工具调用 + 状态管理
@earendil-works/pi-ai            # 统一多 provider LLM API (40+ providers, 4 个底层 API)
@earendil-works/pi-tui           # 终端 UI 库 (差分渲染)
```

### 共同特性 (3 实现都具备)

- **多 provider LLM 支持**: 40+ (Anthropic, OpenAI, Google Gemini, Groq, Ollama, OpenRouter, Azure, Bedrock, Vertex, DeepSeek...)
- **多执行模式**: TUI / Print / JSON-RPC / SDK 嵌入
- **Tree-structured history**: `/tree` 导航, `/fork` 派生, `/share` 分享
- **Context engineering**: AGENTS.md (项目级), SYSTEM.md, 自动 compaction, skills, 动态 context 注入
- **Session 持久化**: JSONL 格式 + branching 支持

### 故意不包含 (Pi 哲学)

Pi 核心刻意不含, 全部推到 example 层或社区:
- **Sub-agents** → `examples/extensions/subagent/`
- **MCP (Model Context Protocol)** → 不支持, 立场: 7-9% context 占用 + black box 不可观测
- **Permission popups** → 用户自定义 `tool_call` 事件阻断
- **Plan mode** → `examples/extensions/plan-mode/`
- **To-do tracking** → 无内置
- **Background bash** → 无内置

## 扩展机制 (5 层)

| 层 | 格式 | 位置 | 触发 |
|----|------|------|------|
| **Extensions** | TS 模块, `default (pi: ExtensionAPI) => {}` | `~/.pi/agent/extensions/` 或 `.pi/extensions/` | 启动加载 |
| **Skills** | Markdown + YAML frontmatter | `~/.pi/agent/skills/<name>/SKILL.md` | slash `/name` |
| **Prompt Templates** | Markdown | `~/.pi/agent/prompts/<name>.md` | slash `/name` |
| **Themes** | JSON 配色 | `~/.pi/agent/themes/<name>.json` | 配置 |
| **Pi Packages** | npm scope `@earendil-works/pi-*` | `npm i -g` | 启动加载 |

详见 [[notes-pi-agent-custom-workflow]] 1.5 节 ExtensionAPI 17 个方法 + [[notes-pi-agent-ecosystem]] 9 个官方 example。

## 与其他 Terminal Coding Agent 的对比

> 完整 7 agent × 13 维度表见 [[synthesis/comparison-terminal-coding-agents-2026-06]] 第 2 节

| 维度 | Pi | Claude Code | Aider | Codex CLI | Gemini CLI | Goose | OpenCode |
|------|-----|------------|-------|-----------|-----------|-------|----------|
| License | MIT | 闭源 | Apache-2.0 | Apache-2.0 | Apache-2.0 | Apache-2.0 | MIT |
| Stars | 59.9k | n/a | 45.8k | 88.7k | 105k | 46.5k | **170k** |
| Providers | 25+ | **Anthropic 唯一** | 100+ | OpenAI 优先 | Gemini 优先 | 15+ | 75+ (models.dev) |
| Subagents | ❌ (example) | ✅ Task 工具 | ❌ | 有限 | ❌ | ✅ Recipes | ✅ build/plan/general |
| MCP | ❌ (mcporter 桥) | ✅ 客户端 | ❌ | ✅ 客户端 | ✅ 客户端 | ✅ **核心抽象** | ✅ 客户端 |
| Session | **JSONL tree** + /share gist | linear + /fork | linear + git commit | JSONL + dashboard | linear + /chat save | linear + recipe | linear + **/share 公共 URL** |
| Plan/Todo | ❌ (plan-mode example) | ✅ 一等公民 | Architect 模式 | /plan + update_plan | /todo 命令 | /plan + recipe 步骤 | ✅ plan agent |
| Primary use | 可组合 primitives | 人机协作 + Plan/Sandbox | git-as-checkpoint | OpenAI 生态 + CI | Gemini 1M context 入口 | MCP/Recipes 平台 | provider 无关 + 分享 |

**5 个关键发现** ([[synthesis/comparison-terminal-coding-agents-2026-06]] 第 5 节):

1. **MCP 已成为事实标准**, 除 Aider 外所有 agent 都把 MCP 客户端作为一/二等公民;Pi 是唯一明确"不会支持 MCP"的。
2. **Provider 无关性是新战场**: Pi, OpenCode, Aider 主打 75+ provider 自由切换;Claude Code / Codex CLI 是"全栈单家"代表。
3. **Plan / Subagent 是企业级分水岭**: Claude Code / OpenCode / Goose 是真正把 plan/subagent 当 first-class 抽象;Pi 故意推到 example 层。
4. **Session 可分享是 OpenCode 的独门**: 原生 `/share` 公共 URL。
5. **Pi 的定位是 "agent 操作系统内核"**, 让用户/团队 fork 出自己的 agent;**与 anomalyco/opencode 设计哲学同源,但 Pi 更小、约束更少、provider 适配更自由**。

## 选型决策树 (转写自 [[synthesis/comparison-terminal-coding-agents-2026-06]] 第 4 节)

```
1. 已订阅 ChatGPT/Claude/Gemini?
   ├─ ChatGPT 订阅 → Codex CLI (codex exec CI 极简)
   ├─ Claude 订阅 → Claude Code (Subagent + Plan + Sandbox 最完整)
   ├─ Gemini 订阅 → Gemini CLI (1M context + GoogleSearch grounding 不可替代)
   └─ 否 → 继续

2. 核心需求 "AI 写代码 = git commit"?
   ├─ 是 → Aider
   └─ 否 → 继续

3. 想用 MCP 协议链接企业工具, Recipes/YAML 流程复用?
   ├─ 是 → Goose
   └─ 否 → 继续

4. 需要 75+ provider 切换 + session 公开 URL?
   ├─ 是 → OpenCode
   └─ 否 → 继续

5. 把 agent 当 library / harness, 自己组装 tools/subagents/session?
   └─ 是 → Pi (MIT + 扩展即代码 + provider 无关 + JSONL tree session)
```

> **注**: 此决策树与 5 个关键发现均为 [[synthesis/comparison-terminal-coding-agents-2026-06]] 笔记作者观点,本 wiki 不独立背书。

## 适用场景

**适合用 Pi 的场景** ([[synthesis/comparison-terminal-coding-agents-2026-06]] 3.x 节):
- 需要把 agent 当 library / harness 嵌入自己产品
- CI 跑长程任务且不想被单家 provider 锁定
- 想直接 fork 出自己的 agent (MIT + 扩展即代码)
- 需要 25+ provider 自由切换
- 想要 Rust/Tauri 性能级别启动 (用 `pi_agent_rust`)

**不适合用 Pi 的场景**:
- 单人/小团队大多数场景 → Claude Code 更省心
- 需要 Subagent、Plan mode、Sandbox、Skills、Memory 层级"开箱即用" → Claude Code
- 心智模型是 "AI 改代码 = git commit" 的小团队 → Aider
- 想要 "approval mode + sandbox" 强约束 CI 工作流 → Codex CLI

## 关键引用

### 设计哲学
- Mario Zechner launch blog: <https://mariozechner.at/posts/2025-11-30-pi-coding-agent/>
- 官方文档: <https://pi.dev>
- 主仓: <https://github.com/badlogic/pi-mono>

### 9 个官方 example extension (详见 [[notes-pi-agent-ecosystem]])
- `subagent/` — 700 行, 子代理 single/parallel/chain 三模式
- `sandbox/` — 230 行, macOS Seatbelt / Linux bubblewrap
- `gondolin/` — 360 行, QEMU micro-VM 沙箱
- `custom-provider-anthropic/` — 430 行, OAuth PKCE + Anthropic streaming
- `custom-provider-gitlab-duo/` / `doom-overlay/` / `dynamic-resources/` / `plan-mode/` / `with-deps/`

### MCP 曲线救国
- [`openclaw/mcporter`](https://github.com/openclaw/mcporter) (原 `steipete/mcporter`, 4.6k stars) — 把 MCP server 暴露给 Pi

## 相关页面

- [[notes-pi-agent]] — 主体笔记 (架构/特性/源码剖析)
- [[synthesis/comparison-terminal-coding-agents-2026-06]] — 7 agent × 13 维度横向对比 + 选型决策树
- [[notes-pi-agent-ecosystem]] — 9 官方扩展示例 + MCP 桥接 + SDK 嵌入
- [[notes-pi-agent-custom-workflow]] — 扩展开发完整生命周期 + 5 个 workflow 配方

## 元数据

- **抓取日期**: 2026-06-05
- **数据来源**: 4 篇 notes 笔记 (`~/workspace/repos/notes/coding_agent/pi-agent*.md`)
- **未交叉引用现有 entity**: pyramid 现有 entities 中**无** pi-agent / coding-agent 主题 (已 grep `entities/`)
