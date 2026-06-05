---
type: source
source-type: notes
title: "Pi Agent — 主体笔记"
author: "Sphinx (notes/coding_agent/pi-agent.md)"
date: 2026-06-05
size: large
path: ../repos/notes/coding_agent/pi-agent.md
summary: "Pi Agent 主体笔记：3 大实现 (earendil-works/pi / oh-my-pi / pi_agent_rust) 概览、架构、关键特性、扩展/自定义/源码剖析（中文 + 英文混合, 2171 行）"
tags: [pi-agent, coding-agent, terminal-agent, typescript, rust]
sources: [entity-pi-agent]
related: [notes-pi-agent-comparison, notes-pi-agent-ecosystem, notes-pi-agent-custom-workflow]
---

# Pi Agent — 主体笔记（Source）

> Source: `~/workspace/repos/notes/coding_agent/pi-agent.md` (66KB / 2171 行)
> 抓取日期: 2026-06-05
> 注意: 本篇是源文档转写。具体 entity 概念见 [[entity-pi-agent]]

## 文档结构（原文 H2 顺序）

1. **Implementations** — 3 个主实现横向（earendil-works/pi / can1357/oh-my-pi / Dicklesworthstone/pi_agent_rust）
2. **Architecture** — 主仓 monorepo 4 包 (`@earendil-works/pi-coding-agent` / `pi-agent-core` / `pi-ai` / `pi-tui`)、oh-my-pi 双核（Python + Bun）架构、pi_agent_rust 静态二进制
3. **Key Features** — 3 实现共性 + 各实现独有能力 (oh-my-pi 32 工具 + subagent fan-out + DAP/LSP, pi_agent_rust 8 工具 + QuickJS)
4. **Customization Guide** — 6 类扩展（extensions / skills / prompt templates / themes / pi packages / custom providers）+ oh-my-pi 配置 YAML 详例
5. **Code Examples** — 3 个安装命令、TypeScript programmatic usage、JSON-RPC 模式
6. **Execution Modes** — TUI / Print / RPC / SDK 4 种
7. **What PI Agent Does NOT Include** — 故意缺失: subagent/MCP/permission popup/plan mode/todo/background bash
8. **Documentation & Resources** — pi.dev / 3 个 GitHub
9. **原理剖析** — 中文源码深度（agent 主循环双层 while、工具 prepare→execute 三阶段、pi-ai Provider Adapter Pattern 40+ provider、context 装配、tui 渲染等 9 节深度技术内容）

## 关键事实提取

### 3 实现对比（数据来自原文表格，stars 数据需以 [[notes-pi-agent-comparison]] 的 2026-06-05 更新为准）

| Implementation | Language | Stars (原文) | Stars (2026-06-05 更正) | 仓库 |
|----------------|----------|------------|----------------------|------|
| earendil-works/pi (现 badlogic/pi-mono) | TypeScript/Node.js | 55.9k | 59.9k | https://github.com/badlogic/pi-mono |
| can1357/oh-my-pi | TypeScript/Rust/Bun | 7.6k | 10.6k | https://github.com/can1357/oh-my-pi |
| Dicklesworthstone/pi_agent_rust | Rust | 1.1k | 1.1k | https://github.com/Dicklesworthstone/pi_agent_rust |

> 数据冲突: 主体笔记抓取时间早于 comparison/ecosystem/custom-workflow 的 2026-06-05 抓取, **以 [[notes-pi-agent-comparison]] 的 "重要更正" 节为准**。

### Architecture 核心包

```
@earendil-works/pi-coding-agent  # 交互式 CLI
@earendil-works/pi-agent-core    # agent 运行时 + 工具调用 + 状态管理
@earendil-works/pi-ai            # 统一多 provider LLM API
@earendil-works/pi-tui           # 终端 UI 库 (差分渲染)
```

### 共同特性 (3 实现都具备)

- **多 provider LLM 支持**: 40+ (Anthropic, OpenAI, Google Gemini, Groq, Ollama, OpenRouter, Azure...)
- **多执行模式**: Interactive TUI / Print/JSON / RPC / SDK
- **Tree-structured history**: 导航、分支、分享 session
- **Context engineering**: AGENTS.md, SYSTEM.md, compaction, skills, 动态 context 注入
- **Session 持久化**: JSONL + branching

### 故意不包含 (build yourself or third-party)

- Sub-agents
- MCP (Model Context Protocol)
- Permission popups
- Plan mode
- To-do tracking
- Background bash

## 中文"原理剖析"节 (line 286-2171) 摘要

主体笔记的后半部分是中文源码深度分析,涵盖:

1. **Agent 主循环与工具调用** — 三层架构 (Agent / runAgentLoop / AgentHarness),双层 `while` 循环处理 streaming + 工具 + turn,sequential/parallel 工具执行模式
2. **pi-ai 统一 API: 40+ Provider 抽象** — Provider Adapter Pattern + `stream()` / `streamSimple()` 双入口
3. **Context 装配** — system prompt 分层、AGENTS.md 父子目录、compaction 触发
4. **TUI 渲染** — 差分渲染、状态机、键盘事件
5. **Pi Package 打包** — npm scope + 依赖
6. **Session 持久化** — JSONL 格式、tree 结构
7. **provider 注册流程** — `registerApiProvider` + capability negotiation
8. **OAuth vs API key** — 双模式切换
9. **性能与冷启动** — 单二进制、差分更新

## 相关页面

- [[entity-pi-agent]] — Pi Agent 综合 entity 页 (本 wiki 唯一 entity)
- [[notes-pi-agent-comparison]] — 7 个 terminal coding agent 横向对比
- [[notes-pi-agent-ecosystem]] — 官方 9 扩展示例 + MCP 曲线救国 + SDK 嵌入
- [[notes-pi-agent-custom-workflow]] — 扩展开发完整生命周期 + 5 个 workflow 配方
