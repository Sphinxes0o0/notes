---
type: synthesis
tags: [llm, coding-agent, terminal-agent, claude-code, aider, codex-cli, gemini-cli, goose, opencode, pi-agent, synthesis]
created: 2026-06-21
sources: [notes-pi-agent, notes-pi-agent-custom-workflow, notes-pi-agent-ecosystem]
---

# Terminal Coding Agents 横向对比 (2026-06)

> **状态**: 🚧 占位 stub — 此 synthesis 被 [[pi-agent]] **7 处**引用(第 2/4/5 节、3.x 节、"重要更正"节)。
> 它是那 7 处引用的**权威来源**,故本 stub 按 pi-agent.md 引用的章节号建立骨架,保证每个引用锚点都有对应落点。
> 整合完笔记原文后请删除本状态标记并填充各节。

## 背景

对 2026-06 时点的 **7 个主流 terminal coding agent** 做 13 维度横向对比,产出选型决策树与关键发现。
原始素材来自 3 篇 notes(`notes-pi-agent*`),本 synthesis 是其跨 agent 整合视图。

**覆盖的 7 个 agent**:

- [[pi-agent]] — 可组合 primitives / harness 内核 (MIT)
- Claude Code — 闭源, Subagent + Plan + Sandbox 最完整
- Aider — Apache-2.0, git-as-checkpoint
- Codex CLI — Apache-2.0, OpenAI 生态 + CI
- Gemini CLI — Apache-2.0, 1M context 入口
- Goose — Apache-2.0, MCP/Recipes 平台
- OpenCode — MIT, provider 无关 + session 公开 URL

## 2. 7 agent × 13 维度对比表

> 精简版已转写于 [[pi-agent]] "与其他 Terminal Coding Agent 的对比" 节。
> 本节为**完整 13 维度表**(License / Stars / Providers / Subagents / MCP / Session / Plan-Todo / Sandbox / Context 工程 / 扩展机制 / 性能 / 主语言 / Primary use),待从原文补全。

| 维度 | Pi | Claude Code | Aider | Codex CLI | Gemini CLI | Goose | OpenCode |
|------|-----|------------|-------|-----------|-----------|-------|----------|
| License | MIT | 闭源 | Apache-2.0 | Apache-2.0 | Apache-2.0 | Apache-2.0 | MIT |
| Stars | 59.9k | n/a | 45.8k | 88.7k | 105k | 46.5k | **170k** |
| Providers | 25+ | **Anthropic 唯一** | 100+ | OpenAI 优先 | Gemini 优先 | 15+ | 75+ |
| Subagents | ❌ (example) | ✅ Task | ❌ | 有限 | ❌ | ✅ Recipes | ✅ |
| MCP | ❌ (桥) | ✅ | ❌ | ✅ | ✅ | ✅ **核心** | ✅ |
| Session | **JSONL tree** | linear+/fork | linear+git | JSONL+dash | linear | linear | linear+/share |
| Plan/Todo | ❌ (example) | ✅ 一等 | Architect | /plan | /todo | /plan | ✅ |
| Primary use | primitives | 人机协作 | git-checkpoint | OpenAI+CI | Gemini ctx | MCP/Recipes | provider-无关 |

> 其余 5 维度 (Sandbox / Context 工程 / 扩展机制 / 性能 / 主语言) 待补。

## 3. 各 agent 适用场景

### 3.1 适合用 Pi 的场景

> 转写锚点。完整列表见 [[pi-agent]] "适合用 Pi 的场景":

- 需要把 agent 当 library / harness 嵌入自己产品
- CI 跑长程任务且不想被单家 provider 锁定
- 想直接 fork 出自己的 agent (MIT + 扩展即代码)
- 需要 25+ provider 自由切换
- 想要 Rust/Tauri 性能级别启动 (用 `pi_agent_rust`)

### 3.2-3.7 其它 6 agent 的适用场景

> 待填充。

## 4. 选型决策树

> 转写于 [[pi-agent]] "选型决策树" 节。原文决策树按"已订阅哪家 → 核心需求 → 是否用 MCP → provider 需求 → 是否要自组装"逐层分流,最终落点为 Codex CLI / Claude Code / Gemini CLI / Aider / Goose / OpenCode / Pi 之一。待从 notes 原文补全每层判据。

## 5. 关键发现

> 转写锚点。5 个发现详见 [[pi-agent]] "**5 个关键发现**" 节,此处为权威展开:

1. **MCP 已成为事实标准**, 除 Aider 外所有 agent 都把 MCP 客户端作为一/二等公民; Pi 是唯一明确"不会支持 MCP"的。
2. **Provider 无关性是新战场**: Pi, OpenCode, Aider 主打 75+ provider 自由切换; Claude Code / Codex CLI 是"全栈单家"代表。
3. **Plan / Subagent 是企业级分水岭**: Claude Code / OpenCode / Goose 是真正把 plan/subagent 当 first-class 抽象; Pi 故意推到 example 层。
4. **Session 可分享是 OpenCode 的独门**: 原生 `/share` 公共 URL。
5. **Pi 的定位是 "agent 操作系统内核"**, 让用户/团队 fork 出自己的 agent; 与 opencode 设计哲学同源, 但 Pi 更小、约束更少、provider 适配更自由。

## 重要更正

> "重要更正" 节被 [[pi-agent]] 第 33 行引用为数据来源。待从 `notes-pi-agent` 原文补全:
> 含 3 大实现的 stars / 启动 / 内存 / 工具数校正值。

## 结论

> 待填充: 2026-06 terminal coding agent 生态格局判断 + 选型默认推荐。

## 相关页面

- [[pi-agent]] — 主消费方, 本 synthesis 的 7 处引用来源
- [[notes-pi-agent]] / [[notes-pi-agent-custom-workflow]] / [[notes-pi-agent-ecosystem]] — 原始笔记
