---
title: "Pi vs 其他 Agent 框架"
description: "Pi 不是孤岛。本篇把 Pi 与市面上 5-6 个主流 terminal AI coding agent 做横向对比，目标是回答\"我该选谁\"。"
---
# Pi vs 其他 Agent 框架

Pi 不是孤岛。本篇把 Pi 与市面上 5-6 个主流 terminal AI coding agent 做横向对比，目标是回答"我该选谁"。

> **数据采集说明**：所有统计数据（stars、license、语言占比）均从对应 GitHub 仓库元数据直接抓取（2026-06-05）。功能描述从官方 README/docs 提取，对应 URL 见各小节。
>
> **重要更正**（相对既有 `tools/pi-agent.md`）：
> - 主仓库现名 `badlogic/pi-mono`（不是 `earendil-works/pi`；后者是公司 org 镜像），**59.9k stars / 7.2k forks / MIT**
> - `can1357/oh-my-pi` 实际 **10.6k stars**（不是 7.6k）
> - `Dicklesworthstone/pi_agent_rust` 实际 **1.1k stars / MIT + Rider**
> - **Goose 仓库迁移**：`block/goose` → `aaif-goose/goose`（2024 末迁入 Linux Foundation 旗下 Agentic AI Foundation）
> - **OpenCode 仓库迁移**：`sst/opencode` → `anomalyco/opencode`（仍由 sst 团队主导）

---

## 0. 评测维度定义

| 维度 | 含义 | 为什么重要 |
|------|------|----------|
| **License** | 开源 + 许可证类型 | 决定 fork/审计/合规自由度 |
| **Lang/Runtime** | 实现语言 + 分发形式 | 决定二次开发门槛、启动速度、冷启动成本 |
| **Providers** | 可驱动哪些 LLM | 单供应商锁定 vs 多家 / 本地模型 |
| **Modes** | TUI / Print / RPC / SDK | 决定能用在哪些场景（CLI / 嵌入 / IDE / CI） |
| **Tools extensibility** | 工具扩展用什么语言 | 决定可定制深度 |
| **Context system** | 上下文装配 | 自动 compaction / 项目记忆文件 / skills / 模板 |
| **Subagents** | 子代理派发能力 | 长程任务并行与可观测性 |
| **MCP** | Model Context Protocol | 工具生态互操作 |
| **Permission** | 授权模型 | auto-allow / prompt / 沙箱 / capability-based |
| **Session** | 会话持久化 | 线性 / tree / 可分享 / 可导出 |
| **Plan/Todo** | 计划 + 待办 | 用户对 agent 长程路径的掌控 |
| **Memory** | 跨会话记忆 | 项目记忆 / RAG / 仓库索引 |
| **Primary use case** | 优化目标 | 长程自主 / 人机协作 / CI headless / provider 桥接 |

---

## 1. 各 Agent 简介

### 1.1 Pi (Earendil Works / badlogic)

- **License**：MIT
- **Stars**：59.9k
- **Language/Runtime**：TypeScript / Node（官方）；Rust（pi_agent_rust 端口）；TS+Rust+Bun（oh-my-pi fork）
- **Install**：`npm i -g --ignore-scripts @earendil-works/pi-coding-agent`
- **Providers**：Anthropic、OpenAI、Azure、DeepSeek、NVIDIA NIM、Google Gemini、Vertex、Amazon Bedrock、Mistral、Groq、Cerebras、Cloudflare、xAI、OpenRouter、Vercel AI Gateway、Hugging Face、Fireworks、Together AI、Kimi For Coding、Xiaomi MiMo —— 4 个底层 API 覆盖
- **Modes**：TUI（默认）/ Print (`-p`) / RPC (`--mode rpc`) / SDK（`@earendil-works/pi-coding-agent`）
- **Tools extensible in**：TypeScript（extension 即 tool / command / TUI / provider / OAuth）
- **Context system**：AGENTS.md（项目 + parent dirs + cwd）、SYSTEM.md、自动 compaction（可配置）、skills（按需加载）、prompt templates（`/name`）、动态 context 注入
- **Subagents**：❌ 核心不含；官方 `subagent` example 演示 single/parallel/chain 三种模式
- **MCP**：❌ 核心不含；社区用 [mcporter](https://github.com/steipete/mcporter) 桥接
- **Permission**：用户自定义（在 extension 内 `tool_call` 事件里阻断；用 `sandbox` example 走 OS 级沙箱）
- **Session**：JSONL + tree 结构；`/tree` 跳转、`/fork` 派生、`/clone` 复制；`/export` HTML；`/share` 上传到 GitHub gist
- **Plan/Todo**：❌ 核心不含；`plan-mode` example 提供只读计划 + Execute/Stay/Refine 三选项
- **Memory**：session 持久 + 自定义扩展；无内置向量索引
- **Notable strengths**：上下文占用 < 1000 tokens（系统 prompt + 工具定义）；extension 即代码（不是 prompt-level skills）；session tree + 公开 HTML 分享
- **Notable weaknesses**：MCP 需外部桥接；plan mode / subagent 等一等公民能力都靠 example 自建
- **Primary use case**："primitives"——把 LLM 交互的最小积木给你，扩展/工具/session 都是同一个抽象；适合要把 agent 当 library / harness 嵌入自己产品的团队

**数据来源**：
- https://github.com/earendil-works/pi
- https://pi.dev
- https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent
- https://mariozechner.at/posts/2025-11-30-pi-coding-agent/

---

### 1.2 Claude Code (Anthropic)

- **License**：**闭源**（只发布编译产物 / npm 包；不开源仓库）
- **Language/Runtime**：TypeScript / Node
- **Install**：`npm i -g @anthropic-ai/claude-code` 或 `brew install --cask claude-code`
- **Providers**：**仅 Anthropic Claude 系列**（OAuth + API Key 两种登录）
- **Modes**：交互 TUI（默认 REPL）、`--print` headless、`-p` 单轮脚本、SDK（`@anthropic-ai/claude-agent-sdk` 启用 Claude Code 全部工具的子进程）
- **Tools extensibility**：Skills（Markdown，`/skill` 命令、`.claude/skills/<name>/SKILL.md`）+ MCP（`claude mcp add`）
- **Context system**：三级记忆（`./CLAUDE.md` 项目 + `~/.claude/CLAUDE.md` 用户 + 企业托管）、`/memory` 编辑、自动 compaction
- **Subagents**：`Agent` / `Task` 工具可派生子 agent（agent-as-tool），每个 subagent 有独立工具白名单与上下文
- **MCP**：完整客户端
- **Permission**：deny-by-default；可对每条工具规则 `allow` / `ask` / `deny`；支持 `sandbox`（macOS Seatbelt / Linux bubblewrap）
- **Session**：线性对话；`/resume` 恢复；`/fork` 派生；分享通过 `claude.ai/code` 链接（团队版）
- **Plan/Todo**：`--plan` / `Shift+Tab` 切换 plan mode；`TodoWrite` 内置待办工具；`ExitPlanMode` 在执行前需用户确认
- **Memory**：CLAUDE.md 层级 + 会话级 cache；无内置向量索引；通过 MCP 提供 RAG（如 Context7）
- **Notable strengths**：深度集成 Anthropic 模型；Subagent / Plan mode / Sandbox / Memory 层级是行业最完整；Skills 体系让用户扩展 prompt 而非代码
- **Notable weaknesses**：闭源，扩展只能通过 prompt-level skills 或 MCP；Provider 锁定 Anthropic
- **Primary use case**：人机协作式（human-in-the-loop）pair programming；长程、深度、需要 plan/permission 精细控制的工程任务

**数据来源**：
- https://www.claude.com/product/claude-code
- https://docs.anthropic.com/en/docs/claude-code/overview
- https://docs.anthropic.com/en/docs/claude-code/skills
- https://docs.anthropic.com/en/docs/claude-code/sub-agents
- https://docs.anthropic.com/en/docs/claude-code/mcp
- https://docs.anthropic.com/en/docs/claude-code/plan-mode

---

### 1.3 Aider

- **License**：Apache-2.0
- **Stars**：45.8k
- **Language/Runtime**：Python 3.10+（80% Python）
- **Install**：`pip install aider-install && aider-install` 或 `uv tool install aider-chat` 或 `uvx aider`
- **Providers**：100+（OpenAI、Anthropic、DeepSeek、OpenRouter、Gemini、Ollama、LM Studio、本地 llama.cpp 等）
- **Modes**：TUI（`aider`）/ non-interactive（`aider --message "..." --yes`）/ `--architect`（双模型 planner+editor）
- **Tools extensibility**：YAML config + Python plugin；2025 起引入 `aider --tool` 与 LLM function-calling
- **Context system**：Repo Map（tree-sitter 的 AST 摘要，按需注入相关文件）+ `CONVENTIONS.md`（项目约定）+ `aider.conf.yml`；无自动 compaction
- **Subagents**：❌ 无内置 fan-out（可脚本嵌套）
- **MCP**：❌ 无原生 MCP 客户端
- **Permission**：默认 auto-apply edits；写入真实文件需用户确认（除非 `--yes`）；所有修改以 git commit 持久化
- **Session**：线性 chat（`/add` `/drop` 管理上下文）；每条消息 → 一次 commit，支持 `--commit-message`；无 tree
- **Plan/Todo**：Architect 模式 = "plan then edit"（两个模型拆分）；无内置 todo UI
- **Memory**：仅 Repo Map + conventions 文件；无跨会话记忆
- **Notable strengths**：100+ Provider 支持；Repo Map 极轻量且高效（无向量库）；git-as-checkpoint 让回滚零成本；SWE-bench 引用率高
- **Notable weaknesses**：Python + 同步架构，长程任务下上下文控制较弱；工具系统 2025 之前非 tool-call 风格，与 MCP/agent 生态对齐度低
- **Primary use case**：人机协作 pair programming，核心心智模型"AI 写代码 = 一次次 commit"

**数据来源**：
- https://github.com/Aider-AI/aider
- https://aider.chat/docs/install.html
- https://aider.chat/docs/llms.html
- https://aider.chat/docs/repomap.html
- https://aider.chat/docs/architect.html
- https://aider.chat/docs/git.html

---

### 1.4 OpenAI Codex CLI

- **License**：Apache-2.0
- **Stars**：88.7k
- **Language/Runtime**：**Rust 96.1%** + Python 2.9% + 少量 TS/Starlark/Shell
- **Install**：`npm i -g @openai/codex` 或 `brew install --cask codex`
- **Providers**：**OpenAI 优先**（`codex` 登录 ChatGPT 订阅 + API Key 双模式）；`--provider` 支持 OpenRouter / 自定义 OpenAI 兼容端点；`--oss` 跑本地 gpt-oss
- **Modes**：交互 TUI（默认 TUI，Rust 实现）、`codex app`（桌面）、`codex exec "..."`（non-interactive / CI）、`codex serve`（HTTP daemon，codex-rs 子目录）、Node/Python SDK（`sdk/` 子目录）
- **Tools extensibility**：Rust 内置 tool + `codex mcp add` 接入 MCP
- **Context system**：`AGENTS.md`（项目级，分层 discover）；`/compact` 触发手动 compaction；`~/.codex/instructions.md` 作 instructions
- **Subagents**：通过 `codex exec` 多 agent 编排（未确认是否有 first-class sub-agent tool）
- **MCP**：完整客户端；`codex mcp add <name> -- <cmd>`
- **Permission**：三层 approval 模式：`read-only` / `auto`（沙箱内写）/ `full-auto`（沙箱内无需确认）；macOS Seatbelt / Linux Landlock；`--sandbox danger-full-access` 关闭
- **Session**：JSONL 会话日志；`codex resume <id>`；可上传到 OpenAI Dashboard 分享
- **Plan/Todo**：`/plan` 进入 plan mode；内置 `update_plan` 工具跟踪 todo
- **Memory**：AGENTS.md 文件层级 + `/mem` 命令管理
- **Notable strengths**：默认沙箱 + approval modes 是 CI/企业友好的开箱体验；ChatGPT 订阅直接登录；Rust TUI 启动快
- **Notable weaknesses**：Provider 体验对非 OpenAI 模型仍在优化中
- **Primary use case**：headless CI（`codex exec`）+ 受沙箱约束的人机协作，主要面向 OpenAI 生态用户

**数据来源**：
- https://github.com/openai/codex
- https://github.com/openai/codex/blob/main/docs/config.md

---

### 1.5 Gemini CLI (Google)

- **License**：Apache-2.0
- **Stars**：105k
- **Language/Runtime**：TypeScript / Node 20+
- **Install**：`npx @google/gemini-cli` 或 `npm i -g @google/gemini-cli` 或 `brew install gemini-cli`
- **Providers**：**Google Gemini 优先**（Gemini 3，1M context，免费层 60 req/min / 1000 req/day）；OpenAI / Anthropic 兼容通过环境变量
- **Modes**：TUI（`gemini`）、`gemini -p "..."` headless（输出给管道）、GitHub Action 集成
- **Tools extensibility**：MCP 客户端（`~/.gemini/settings.json` 声明）；内置 `GoogleSearch` / `read_file` / `write_file` / `shell` / `memory` / `web_fetch`
- **Context system**：`GEMINI.md`（项目 + `~/.gemini/GEMINI.md` 用户）；`/memory show` `/memory refresh`；`/compress` 触发 compaction
- **Subagents**：未确认有原生 fan-out
- **MCP**：完整客户端（`@github`、`@slack`、`@database` 等扩展）
- **Permission**：deny-by-default；`yolo` 模式 auto-allow；`--approval-mode` 类似 Claude Code
- **Session**：线性；`/chat save <tag>` `/chat resume <tag>`；conversation checkpointing
- **Plan/Todo**：无显式 plan mode；`/todo` 内置待办命令
- **Memory**：GEMINI.md 层级 + token caching
- **Notable strengths**：1M context + GoogleSearch grounding 免费额度几乎无可替代；GitHub Action 内置（自动 PR review、issue triage、`@gemini-cli` mention）
- **Notable weaknesses**：TUI UX 较 Gemini GUI/Codex GUI 略弱
- **Primary use case**：Gemini 模型的 CLI 入口，大上下文 + grounding 检索的研究/重构场景

**数据来源**：
- https://github.com/google-gemini/gemini-cli

---

### 1.6 Goose (AAIF / Linux Foundation)

> **2024 末**：`block/goose` → **`aaif-goose/goose`**（Linux Foundation 旗下 Agentic AI Foundation 接管 governance）

- **License**：Apache-2.0
- **Stars**：46.5k
- **Language/Runtime**：**Rust 63.8% + TypeScript 29.4%**
- **Install**：`curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download.sh | bash` 或 `brew install --cask block-goose`
- **Providers**：15+（Anthropic、OpenAI、Google、Ollama、OpenRouter、Azure、Bedrock、ACP 接入 Claude/ChatGPT/Gemini 订阅）
- **Modes**：TUI / Desktop GUI（macOS/Linux/Windows）/ API embed / `goose run --recipe` / `goose web` HTTP server
- **Tools extensibility**：**核心抽象即 MCP server**（Extension ≡ MCP server）；内置 Developer / Computer Use / Memory / JetBrains / Google Drive 等；70+ extensions
- **Context system**：依赖 extension 自行提供上下文；`goose session --with-context` 注入外部文本；session 自身可作 memory
- **Subagents**：✅ **Recipes**（YAML 声明的多步 / 多 agent 流水线）和 sub-recipe 实现 fan-out；`goose run --recipe` 触发
- **MCP**：**MCP 是一等公民**（Extension 协议就是 MCP）；可作 MCP client 与 server
- **Permission**：extension 级 allowlist；GUI 模式有"approval"按钮；CLI 模式接续上一会话的 approval 状态
- **Session**：可命名 + resume；可导出为 recipe（YAML）；无 tree
- **Plan/Todo**：`/plan` 进入计划模式；`goose run` 内部以 recipe 步骤执行
- **Memory**：跨会话的 session 列表 + "Knowledge" extension；无内置向量索引
- **Notable strengths**：MCP Extension 抽象最成熟；Recipes 让非编程用户可复用 agent 流程；Block 内部已大规模使用
- **Notable weaknesses**：CLI UX 较 Claude Code/Codex 略粗糙；Desktop 与 CLI 体验割裂
- **Primary use case**：可扩展的"agent 平台"——MCP/RAG/企业工具集成的长程自动化，更偏 IT 工程而非 IDE-style pair programming

**数据来源**：
- https://github.com/aaif-goose/goose
- https://block.github.io/goose/docs/getting-started/using-extensions
- https://block.github.io/goose/docs/guides/recipes

---

### 1.7 OpenCode (anomalyco / sst 团队)

> 2025 中：`sst/opencode` → **`anomalyco/opencode`**（运营主体变化，sst 团队仍主导）

- **License**：MIT
- **Stars**：170k（所有对比对象中最高）
- **Language/Runtime**：TypeScript 68.2% + MDX 28.2% + CSS 3.1%
- **Install**：`curl -fsSL https://opencode.ai/install | bash` 或 `npm i -g opencode-ai` 或 `brew install opencode`；桌面端 `opencode-desktop`
- **Providers**：通过 **models.dev** 聚合 75+ providers（Anthropic、OpenAI、Google、Groq、Cerebras、xAI、AWS Bedrock、Azure、OpenRouter、Ollama、LM Studio 等），统一接口
- **Modes**：TUI（`opencode`）/ server（`opencode serve`，HTTP）/ desktop（BETA，Tauri）/ headless `opencode run "..."` / SDK（`@opencode-ai/sdk` / `opencode-go`）
- **Tools extensibility**：内置 file/shell/edit/patch/webfetch/grep/glob；MCP 客户端；用户可用 TS 写自定义 tool 然后 `opencode tool add <path>`
- **Context system**：`AGENTS.md`（项目根、子目录级 discover）；`/compact` 手动 compaction；`/share` 把 session 上传为只读 URL；`/undo` 撤销；`/init` 在新项目生成 AGENTS.md
- **Subagents**：✅ 任意子 agent 可被声明为 `agent` 工具；通过 `opencode.json` 顶层 `agent` 字段配置；预置 `build` / `plan` / `general` 三个 agent
- **MCP**：客户端完整；通过 `.opencode/mcp.json` 或 env
- **Permission**：deny-by-default；`permissions` 块按 tool glob + `edit` / `bash` / `webfetch` 分类允许；可 `--auto-approve` 全部
- **Session**：线性 + 可分享（`/share` 上传到 opencode.ai，得到可公开访问的只读 URL）；`/fork` 派生分支
- **Plan/Todo**：内置 `plan` agent（默认开启）：先产出 todo 列表 + 待编辑文件清单，确认后再执行
- **Memory**：AGENTS.md + session 列表；无内置向量
- **Notable strengths**：models.dev 让 75+ providers 即插即用；`/share` 是少有的"原生 share 链接"能力；plan agent 是 first-class subagent；MIT 友好
- **Notable weaknesses**：170k stars 反映社区热度，但 API/CLI 行为快速迭代中
- **Primary use case**：provider 无关的通用 terminal agent 框架，sst 用户/开源贡献者的多 provider 瑞士军刀

**数据来源**：
- https://github.com/anomalyco/opencode
- https://opencode.ai/docs
- https://opencode.ai/docs/providers/
- https://opencode.ai/docs/agents/
- https://opencode.ai/docs/share/

---

## 2. 横向对比表

| 维度 | **Pi** | **Claude Code** | **Aider** | **Codex CLI** | **Gemini CLI** | **Goose** | **OpenCode** |
|------|--------|-----------------|-----------|---------------|----------------|-----------|--------------|
| License | MIT | 闭源 | Apache-2.0 | Apache-2.0 | Apache-2.0 | Apache-2.0 | MIT |
| Stars (2026-06) | 59.9k | n/a | 45.8k | 88.7k | 105k | 46.5k | 170k |
| Lang/Runtime | TS / Node | TS / Node | Python 3.10+ | Rust 96% | TS / Node 20+ | Rust + TS | TS 68% + MDX |
| Install | `npm i -g @earendil-works/pi-coding-agent` | `npm i -g @anthropic-ai/claude-code` | `uvx aider` | `npm i -g @openai/codex` | `npx @google/gemini-cli` | `curl ...install... \| bash` | `curl -fsSL opencode.ai/install \| bash` |
| Providers | 25+（4 个底层 API） | Anthropic 唯一 | 100+ | OpenAI 优先 + 兼容 | Gemini 优先 + 兼容 | 15+ | 75+ via models.dev |
| Modes | TUI / Print / RPC / SDK | TUI / Print / SDK | TUI / headless / architect | TUI / exec / serve / SDK / app | TUI / `-p` / GitHub Action | TUI / Desktop / run / web | TUI / serve / desktop / run / SDK |
| Tools extensibility | TS extension（tool/command/UI/provider/OAuth） | Skills (MD) + MCP | YAML + Python | Rust + MCP | TS + MCP | TS/Python extension ≡ MCP | TS / Go + MCP |
| Context system | AGENTS.md + skills + prompt templates | CLAUDE.md 三级 + auto-compact | Repo Map + CONVENTIONS.md | AGENTS.md + manual /compact | GEMINI.md + /memory + /compress | session + extension memory | AGENTS.md + /compact + /init |
| Subagents | ❌（example 提供） | ✅ Task/Agent tool | ❌ | 有限（exec 编排） | 未确认 | ✅ Recipes (YAML) | ✅ `build` / `plan` / `general` agents |
| MCP | ❌（mcporter 桥接） | ✅ 客户端 | ❌ | ✅ 客户端 | ✅ 客户端 | ✅ **核心抽象** | ✅ 客户端 |
| Permission | 用户自定义（extension） | deny-default + sandbox | auto-apply + git commit 回滚 | 三层 approval + 沙箱 | deny-default + yolo | extension allowlist | deny-default + tool glob |
| Session | JSONL **tree** + /share gist | linear + /fork + cloud share | linear + git commit | JSONL + OpenAI dashboard | linear + /chat save/resume | linear + recipe 导出 | linear + **/share 公共 URL** + /fork |
| Plan/Todo | ❌（plan-mode example） | ✅ 一等公民 | Architect 模式 | /plan + update_plan 工具 | /todo 命令 | /plan + recipe 步骤 | ✅ plan agent |
| Memory | session 持久 + 自定义 | CLAUDE.md 层级 + cache | Repo Map 一次性 | AGENTS.md | GEMINI.md + token caching | session + Knowledge ext | AGENTS.md + session |
| Primary use case | 可组合 agent primitives | 人机协作 + Plan/Sandbox | git-as-checkpoint 协作 | OpenAI 生态 + CI | Gemini 1M context 入口 | MCP/Recipes 平台 | provider 无关 + 分享 |

---

## 3. Pi vs X 深度对比

### 3.1 Pi vs Claude Code

| 场景 | 推荐 |
|------|------|
| 单人 / 小团队大多数场景 | **Claude Code** |
| 需要 Subagent、Plan mode、Sandbox、Skills、Memory 层级这些"开箱即用"功能 | **Claude Code** |
| 需要 Claude Sonnet/Opus 最新能力 + Anthropic 官方安全/合规背书 | **Claude Code** |
| 需要多 provider 混用（Claude + 本地 Ollama + 第三方） | **Pi** |
| 需要把 agent 当 library / harness 嵌入自己产品 | **Pi** |
| CI 跑长程任务且不想被 Anthropic 锁定 | **Pi** |
| 想直接 fork 出自己的 agent | **Pi** |

**架构哲学差**：Pi 是 **primitives**（"把 LLM 交互的最小积木给你，扩展/工具/session 都是同一个抽象"）；Claude Code 是 **opinionated batteries-included**（每个交互细节都由 Anthropic 决策好，用户主要靠 Skills + MCP 在不写代码的前提下扩展）。一个比喻：Pi 像 `tmux` + `Emacs` 的可拼装内核；Claude Code 像 VSCode 的开箱工作台。

### 3.2 Pi vs Aider

| 场景 | 推荐 |
|------|------|
| 心智模型是"AI 改代码 = git commit"的小团队 | **Aider** |
| 100+ provider 即接即用（OpenRouter、DeepSeek、Ollama） | **Aider** |
| 纯 pair-programming，不想要 subagent / MCP 复杂度 | **Aider** |
| 想要最简单的回滚（每个修改即 commit，`git reset` 即可） | **Aider** |
| 需要 MCP 生态、provider 切换、自建工具链 | **Pi** |
| 想要 Rust/Tauri 性能级别启动 | **Pi** |
| 想在 agent loop 上加自定义 hook | **Pi** |

**架构哲学差**：Pi 是 **pluggable harness**（agent = 扩展图）；Aider 是 **best-in-class git-aware diff applier**（核心卖点 = "模型给我 diff，我保证 diff 落地 + 自动 commit"）。Repo Map + Architect 模式让 Aider 在"中等规模代码库精准修改"上仍是 SOTA。

### 3.3 Pi vs Codex CLI

| 场景 | 推荐 |
|------|------|
| 已经用 ChatGPT 订阅 / OpenAI API | **Codex CLI** |
| 想要"approval mode + sandbox"的强约束 CI 工作流 | **Codex CLI** |
| 想要 Rust 性能与 OpenAI 内部模型同步更新 | **Codex CLI** |
| 需要 provider 无关 | **Pi** |
| 想把 agent 暴露为 RPC / SDK | **Pi** |
| 需要自定义 compaction / session 存储 | **Pi** |

**架构哲学差**：Pi 是 **provider-agnostic primitives**；Codex CLI 是 **OpenAI-flavored, sandbox-first harness**（设计目标第一条是"安全地让你在 CI 跑 Codex"）。Codex CLI 的 approval 三层（read-only / auto / full-auto）比 Pi 的 user-defined 模式更"产品化"，但代价是 harness 内部难以替换。

---

## 4. 选型决策树

```
1. 你是否已订阅 ChatGPT/Claude/Gemini 且不希望引入新供应商？
   ├─ ChatGPT 订阅 → Codex CLI（`codex exec` CI 极简）
   ├─ Claude 订阅 → Claude Code（Subagent + Plan + Sandbox 最完整）
   ├─ Gemini 订阅 → Gemini CLI（1M context + GoogleSearch grounding 不可替代）
   └─ 否 → 继续

2. 你的核心需求是"AI 写代码并自动 git commit"?
   ├─ 是 → Aider（git-as-checkpoint 心智模型）
   └─ 否 → 继续

3. 你想用 MCP 协议把整个企业工具链接进 agent，且 Recipes/YAML 流程能复用？
   ├─ 是 → Goose（Extension ≡ MCP 抽象最成熟）
   └─ 否 → 继续

4. 你需要 75+ provider 之间频繁切换，并把 agent session 公开为可分享 URL？
   ├─ 是 → OpenCode（`/share` + models.dev 是其差异点）
   └─ 否 → 继续

5. 你要把 agent 当 library / harness，自己组装 tools / subagents / session？
   └─ 是 → Pi（MIT + 扩展即代码 + provider 无关 + JSONL tree session）
```

---

## 5. 关键发现

1. **MCP 已成为事实标准**：除 Aider 外，所有主流 agent 都把 MCP 客户端作为一/二等公民；Goose（Extension ≡ MCP）、Gemini CLI、OpenCode 还支持**自身作为 MCP server**，是 agent 互操作的方向。Pi 是唯一明确"不会支持 MCP"的，其立场基于 7-9% context 占用 + black box 不可观测。

2. **Provider 无关性是新战场**：Pi、OpenCode、Aider 主打"75+ provider 自由切换"；Claude Code 与 Codex CLI 是"全栈单家"代表。OpenCode 的 models.dev 抽象层是当前最成熟的 provider 聚合方案。

3. **Plan / Subagent 是企业级分水岭**：Claude Code（Task 工具）、OpenCode（plan agent / general subagent）、Goose（Recipes）是真正把 plan/subagent 当 first-class 抽象的；Aider 的 Architect 模式只是"两个模型"而非"两个 agent 实例"；Pi 故意把这些推到 example 层。

4. **Session 可分享是 OpenCode 的独门**：原生 `/share` 公共 URL 让 OpenCode 在"AI Pair Demo / 公开 agent 评审"场景有差异化；Pi 的 `/share` 走 GitHub gist 也类似但需要登录；其他 agent 多依赖云平台（Anthropic Console / OpenAI Dashboard）。

5. **Pi 的定位是"agent 操作系统内核"**：相比 Claude Code 这种"工作台"，Pi 更像可拼装 primitives；它不试图把 harness 做厚，而是把扩展抽象做到极薄（每个扩展是一个普通 TS 模块），让用户/团队 fork 出自己的 agent。这与 `anomalyco/opencode` 的设计哲学同源，但 Pi 更小、约束更少、provider 适配更自由。

6. **两个重要 governance 变化**值得跟踪：Goose 2024 末从 Block 转移到 Linux Foundation 旗下 Agentic AI Foundation（`aaif-goose/goose`）；OpenCode 2025 中从 sst 迁移到 anomalyco org。两者都反映了这些 agent 项目正在脱离单一公司治理、走向社区/基金会。

---

## 6. 关键 URL 索引

### Pi
- https://pi.dev
- https://github.com/earendil-works/pi
- https://github.com/badlogic/pi-mono
- https://github.com/can1357/oh-my-pi (10.6k stars)
- https://github.com/Dicklesworthstone/pi_agent_rust (1.1k stars)
- https://mariozechner.at/posts/2025-11-30-pi-coding-agent/

### Claude Code
- https://www.claude.com/product/claude-code
- https://docs.anthropic.com/en/docs/claude-code/overview
- https://docs.anthropic.com/en/docs/claude-code/skills
- https://docs.anthropic.com/en/docs/claude-code/sub-agents
- https://docs.anthropic.com/en/docs/claude-code/mcp
- https://docs.anthropic.com/en/docs/claude-code/iam
- https://docs.anthropic.com/en/docs/claude-code/sessions
- https://docs.anthropic.com/en/docs/claude-code/plan-mode
- https://docs.anthropic.com/en/docs/claude-code/sdk

### Aider
- https://aider.chat/
- https://github.com/Aider-AI/aider
- https://aider.chat/docs/install.html
- https://aider.chat/docs/llms.html
- https://aider.chat/docs/git.html
- https://aider.chat/docs/repomap.html
- https://aider.chat/docs/architect.html

### Codex CLI
- https://github.com/openai/codex (88.7k stars)
- https://github.com/openai/codex/blob/main/docs/config.md

### Gemini CLI
- https://github.com/google-gemini/gemini-cli (105k stars)

### Goose
- https://github.com/aaif-goose/goose (46.5k stars, AAIF governance)
- https://block.github.io/goose/docs/getting-started/using-extensions
- https://block.github.io/goose/docs/guides/recipes

### OpenCode
- https://github.com/anomalyco/opencode (170k stars)
- https://opencode.ai/docs
- https://opencode.ai/docs/providers/
- https://opencode.ai/docs/agents/
- https://opencode.ai/docs/share/
- https://opencode.ai/docs/permissions/
- https://opencode.ai/docs/mcp-servers/

---

## License

MIT License

---
