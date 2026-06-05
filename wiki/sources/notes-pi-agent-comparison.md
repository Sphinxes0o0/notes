---
type: source
source-type: notes
title: "Pi vs 其他 Agent 框架 — 7 个 Terminal Coding Agent 横向对比"
author: "Sphinx (notes/coding_agent/pi-agent-comparison.md)"
date: 2026-06-05
size: medium
path: ../repos/notes/coding_agent/pi-agent-comparison.md
summary: "Pi / Claude Code / Aider / OpenAI Codex CLI / Gemini CLI / Goose / OpenCode 共 7 个 terminal AI coding agent 横向对比（13 维度）+ 选型决策树 + 5 个关键发现"
tags: [pi-agent, claude-code, aider, codex-cli, gemini-cli, goose, opencode, comparison, coding-agent]
sources: [entity-pi-agent]
related: [notes-pi-agent, notes-pi-agent-ecosystem, notes-pi-agent-custom-workflow]
---

# Pi vs 其他 Agent 框架 — 横向对比（Source）

> Source: `~/workspace/repos/notes/coding_agent/pi-agent-comparison.md` (27KB / 403 行)
> 抓取日期: 2026-06-05 (内含"重要更正"段,主仓库迁移到 badlogic/pi-mono、Goose 迁到 aaif-goose、OpenCode 迁到 anomalyco)
> 选型决策树与"关键发现"结论均为原笔记作者观点,本 wiki 不独立背书

## 重要更正 (相对 [[notes-pi-agent]] 主体笔记)

- 主仓库现名 `badlogic/pi-mono` (不是 `earendil-works/pi`;后者是公司 org 镜像), **59.9k stars / 7.2k forks / MIT**
- `can1357/oh-my-pi` 实际 **10.6k stars** (不是 7.6k)
- `Dicklesworthstone/pi_agent_rust` 实际 **1.1k stars / MIT + Rider**
- **Goose 仓库迁移**: `block/goose` → `aaif-goose/goose` (2024 末迁入 Linux Foundation 旗下 Agentic AI Foundation)
- **OpenCode 仓库迁移**: `sst/opencode` → `anomalyco/opencode` (仍由 sst 团队主导)

## 评测 13 维度 (原文定义)

License, Lang/Runtime, Providers, Modes, Tools extensibility, Context system, Subagents, MCP, Permission, Session, Plan/Todo, Memory, Primary use case

## 7 Agent 简介 (要点)

### 1.1 Pi (Earendil Works / badlogic)

- **License**: MIT, **Stars**: 59.9k
- **Lang**: TypeScript/Node (官方) + Rust (pi_agent_rust 端口) + TS+Rust+Bun (oh-my-pi)
- **Providers**: 25+ (4 个底层 API 覆盖)
- **Tools extensible in**: TypeScript (extension = tool/command/UI/provider/OAuth)
- **Subagents**: ❌ 核心不含 (官方 subagent example)
- **MCP**: ❌ (社区用 mcporter 桥接)
- **Permission**: 用户自定义 (extension 内 `tool_call` 事件阻断;sandbox example 走 OS 沙箱)
- **Session**: JSONL **tree** + `/tree` 跳转 + `/share` 上传 GitHub gist
- **Plan/Todo**: ❌ (`plan-mode` example)
- **Notable**: 上下文占用 < 1000 tokens;extension 即代码 (非 prompt-level);session tree + 公开 HTML 分享
- **Primary use case**: "primitives" — 把 LLM 交互的最小积木给你

### 1.2 Claude Code (Anthropic)

- **License**: 闭源 (只发布编译产物/npm 包;不开源)
- **Lang**: TypeScript/Node
- **Providers**: **仅 Anthropic Claude** (OAuth + API Key)
- **Modes**: 交互 TUI / `--print` headless / `-p` 单轮 / SDK (`@anthropic-ai/claude-agent-sdk`)
- **Tools extensibility**: Skills (Markdown) + MCP
- **Context system**: 三级记忆 (项目 `./CLAUDE.md` + 用户 `~/.claude/CLAUDE.md` + 企业托管) + `/memory` + 自动 compaction
- **Subagents**: ✅ `Agent` / `Task` 工具
- **MCP**: ✅ 完整客户端
- **Permission**: deny-by-default + `allow`/`ask`/`deny` + `sandbox` (macOS Seatbelt / Linux bubblewrap)
- **Plan/Todo**: ✅ `--plan` / `Shift+Tab` + `TodoWrite` + `ExitPlanMode`
- **Memory**: CLAUDE.md 层级 + 会话级 cache;无内置向量索引;MCP 接 RAG (如 Context7)
- **Notable**: 深度集成 Anthropic 模型;Subagent/Plan/Sandbox/Memory 层级行业最完整
- **Primary use case**: 人机协作式 pair programming;长程、深度、需要 plan/permission 精细控制的工程任务

### 1.3 Aider

- **License**: Apache-2.0, **Stars**: 45.8k
- **Lang**: Python 3.10+ (80% Python)
- **Providers**: 100+ (OpenAI, Anthropic, DeepSeek, OpenRouter, Gemini, Ollama, LM Studio, 本地 llama.cpp)
- **Tools extensibility**: YAML + Python plugin;2025 起 `aider --tool` + LLM function-calling
- **Context system**: Repo Map (tree-sitter AST 摘要) + `CONVENTIONS.md` + `aider.conf.yml`;无自动 compaction
- **Subagents**: ❌ 无内置 fan-out
- **MCP**: ❌
- **Permission**: 默认 auto-apply edits;写入真实文件需用户确认 (`--yes` 跳过);所有修改以 git commit 持久化
- **Session**: 线性 chat (`/add` `/drop`);每条消息 → 一次 commit (`--commit-message`);无 tree
- **Plan/Todo**: Architect 模式 = "plan then edit" (双模型)
- **Notable**: 100+ Provider;Repo Map 极轻量 (无向量库);git-as-checkpoint 回滚零成本;SWE-bench 引用率高
- **Primary use case**: AI 写代码 = 一次次 commit

### 1.4 OpenAI Codex CLI

- **License**: Apache-2.0, **Stars**: 88.7k
- **Lang**: **Rust 96.1%** + Python 2.9%
- **Providers**: OpenAI 优先 (ChatGPT 订阅 + API Key);`--provider` 支持 OpenRouter / 自定义 OpenAI 兼容端点;`--oss` 跑本地 gpt-oss
- **Modes**: 交互 TUI / `codex app` 桌面 / `codex exec` non-interactive / `codex serve` HTTP daemon / Node/Python SDK
- **Tools extensibility**: Rust 内置 tool + `codex mcp add` MCP
- **Context system**: `AGENTS.md` (项目级) + `/compact` 手动 + `~/.codex/instructions.md`
- **MCP**: ✅ 完整客户端
- **Permission**: 三层 approval: `read-only` / `auto` (沙箱内写) / `full-auto`;macOS Seatbelt / Linux Landlock
- **Session**: JSONL + `codex resume <id>` + OpenAI Dashboard 分享
- **Plan/Todo**: `/plan` + `update_plan` 工具
- **Notable**: 默认沙箱 + approval 模式是 CI/企业友好的开箱体验;ChatGPT 订阅直接登录
- **Primary use case**: headless CI (`codex exec`) + 受沙箱约束的人机协作, OpenAI 生态用户

### 1.5 Gemini CLI (Google)

- **License**: Apache-2.0, **Stars**: 105k
- **Lang**: TypeScript/Node 20+
- **Providers**: **Google Gemini 优先** (Gemini 3, 1M context, 免费层 60 req/min / 1000 req/day);OpenAI/Anthropic 兼容通过环境变量
- **Tools extensibility**: MCP 客户端 (`~/.gemini/settings.json`);内置 `GoogleSearch` / `read_file` / `write_file` / `shell` / `memory` / `web_fetch`
- **Context system**: `GEMINI.md` (项目 + `~/.gemini/GEMINI.md` 用户) + `/memory` + `/compress`
- **MCP**: ✅ 完整客户端
- **Permission**: deny-by-default;`yolo` 模式 auto-allow
- **Session**: 线性 + `/chat save <tag>` `/chat resume <tag>` + conversation checkpointing
- **Plan/Todo**: 无显式 plan mode;`/todo` 内置
- **Notable**: 1M context + GoogleSearch grounding 免费额度几乎无可替代;GitHub Action 内置 (自动 PR review、issue triage、`@gemini-cli` mention)
- **Primary use case**: Gemini 模型 CLI 入口,大上下文 + grounding 检索的研究/重构

### 1.6 Goose (AAIF / Linux Foundation)

> 2024 末: `block/goose` → **`aaif-goose/goose`** (Linux Foundation Agentic AI Foundation)

- **License**: Apache-2.0, **Stars**: 46.5k
- **Lang**: **Rust 63.8% + TypeScript 29.4%**
- **Providers**: 15+ (Anthropic, OpenAI, Google, Ollama, OpenRouter, Azure, Bedrock, ACP 接入 Claude/ChatGPT/Gemini 订阅)
- **Modes**: TUI / Desktop GUI / API embed / `goose run --recipe` / `goose web` HTTP server
- **Tools extensibility**: **核心抽象即 MCP server** (Extension ≡ MCP server);70+ extensions
- **Context system**: 依赖 extension 自行提供上下文;`--with-context` 注入外部文本
- **Subagents**: ✅ **Recipes** (YAML 声明的多步/多 agent 流水线) + sub-recipe
- **MCP**: **MCP 是一等公民** (Extension 协议就是 MCP)
- **Session**: 可命名 + resume;可导出为 recipe (YAML)
- **Plan/Todo**: `/plan` + `goose run` 内部以 recipe 步骤
- **Memory**: 跨会话 session 列表 + "Knowledge" extension
- **Notable**: MCP Extension 抽象最成熟;Recipes 让非编程用户可复用 agent 流程
- **Primary use case**: 可扩展的 "agent 平台" — MCP/RAG/企业工具集成

### 1.7 OpenCode (anomalyco / sst 团队)

> 2025 中: `sst/opencode` → **`anomalyco/opencode`**

- **License**: MIT, **Stars**: 170k (对比对象中最高)
- **Lang**: TypeScript 68.2% + MDX 28.2% + CSS 3.1%
- **Providers**: 通过 **models.dev** 聚合 75+ providers (Anthropic, OpenAI, Google, Groq, Cerebras, xAI, AWS Bedrock, Azure, OpenRouter, Ollama, LM Studio)
- **Modes**: TUI / `opencode serve` HTTP / desktop BETA (Tauri) / `opencode run` headless / SDK (`@opencode-ai/sdk` / `opencode-go`)
- **Tools extensibility**: 内置 + MCP 客户端;用户 TS 自定义 tool 然后 `opencode tool add`
- **Context system**: `AGENTS.md` (项目根 + 子目录 discover) + `/compact` + `/share` 上传只读 URL + `/undo` + `/init` 自动生成 AGENTS.md
- **Subagents**: ✅ 任意子 agent 可被声明为 `agent` 工具;`opencode.json` 顶层 `agent` 字段配置;预置 `build` / `plan` / `general` 三个 agent
- **MCP**: ✅ 客户端完整
- **Permission**: deny-by-default;`permissions` 块按 tool glob + `edit`/`bash`/`webfetch` 分类
- **Session**: 线性 + `/share` 公共 URL + `/fork` 分支
- **Plan/Todo**: 内置 `plan` agent (默认开启):先 todo 列表 + 待编辑文件清单,确认后再执行
- **Notable**: models.dev 让 75+ providers 即插即用;`/share` 是少有的"原生 share 链接"能力;plan agent 是 first-class subagent
- **Primary use case**: provider 无关的通用 terminal agent 框架

## 选型决策树 (原文转写)

```
1. 你是否已订阅 ChatGPT/Claude/Gemini 且不希望引入新供应商?
   ├─ ChatGPT 订阅 → Codex CLI (codex exec CI 极简)
   ├─ Claude 订阅 → Claude Code (Subagent + Plan + Sandbox 最完整)
   ├─ Gemini 订阅 → Gemini CLI (1M context + GoogleSearch grounding 不可替代)
   └─ 否 → 继续

2. 你的核心需求是 "AI 写代码并自动 git commit"?
   ├─ 是 → Aider (git-as-checkpoint 心智模型)
   └─ 否 → 继续

3. 你想用 MCP 协议把整个企业工具链接进 agent, 且 Recipes/YAML 流程能复用?
   ├─ 是 → Goose (Extension ≡ MCP 抽象最成熟)
   └─ 否 → 继续

4. 你需要 75+ provider 之间频繁切换, 并把 agent session 公开为可分享 URL?
   ├─ 是 → OpenCode (/share + models.dev 是其差异点)
   └─ 否 → 继续

5. 你要把 agent 当 library / harness, 自己组装 tools / subagents / session?
   └─ 是 → Pi (MIT + 扩展即代码 + provider 无关 + JSONL tree session)
```

## 5 个关键发现 (原文转写)

1. **MCP 已成为事实标准**: 除 Aider 外,所有主流 agent 都把 MCP 客户端作为一/二等公民;Goose (Extension ≡ MCP)、Gemini CLI、OpenCode 还支持自身作为 MCP server。**Pi 是唯一明确"不会支持 MCP"的**,立场基于 7-9% context 占用 + black box 不可观测。
2. **Provider 无关性是新战场**: Pi, OpenCode, Aider 主打 "75+ provider 自由切换";Claude Code 与 Codex CLI 是 "全栈单家"代表。OpenCode 的 models.dev 抽象层是当前最成熟的 provider 聚合方案。
3. **Plan / Subagent 是企业级分水岭**: Claude Code (Task 工具), OpenCode (plan agent / general subagent), Goose (Recipes) 是真正把 plan/subagent 当 first-class 抽象;Aider 的 Architect 模式只是 "两个模型" 而非 "两个 agent 实例";Pi 故意把这些推到 example 层。
4. **Session 可分享是 OpenCode 的独门**: 原生 `/share` 公共 URL 让 OpenCode 在 "AI Pair Demo / 公开 agent 评审" 场景有差异化;Pi 的 `/share` 走 GitHub gist 也类似但需要登录;其他 agent 多依赖云平台。
5. **Pi 的定位是 "agent 操作系统内核"**: 相比 Claude Code 这种 "工作台", Pi 更像可拼装 primitives;它不试图把 harness 做厚,而是把扩展抽象做到极薄 (每个扩展是一个普通 TS 模块),让用户/团队 fork 出自己的 agent。

## 相关页面

- [[entity-pi-agent]] — Pi Agent entity (1 entity 集中)
- [[notes-pi-agent]] — 主体笔记
- [[notes-pi-agent-ecosystem]] — Pi 扩展生态
- [[notes-pi-agent-custom-workflow]] — Pi 定制 workflow
