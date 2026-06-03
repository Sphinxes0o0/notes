---
title: Hermes Memory 系统 + 论文开源项目延伸 (2025-12 ~ 2026-06)
date: 2026-06-04 11:00:00
tags:
    - hermes
    - agent
    - memory
    - research
    - papers
    - open-source
    - survey
---

# Hermes Memory 系统 — 论文 + 开源项目延伸

> 范围: 最近 6 个月 (2025-12 ~ 2026-06) 关于 LLM agent memory 的代表性论文与开源项目
> 方法: Semantic Scholar API + GitHub search (2026-06-04)
> 上游: [[hermes_memory_design]] (Hermes 自身设计)

## 1. 学术论文 (10 篇代表)

### 1.1 Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents

- **作者**: 团队未列出 (S2 摘要截断)
- **引用**: 23
- **出处**: 2026
- **URL**: [Semantic Scholar](https://api.semanticscholar.org/graph/v1/paper/search?query=Agentic+Memory+LLM)
- **核心**: 提出**统一长短记忆管理**框架, 解决 LLM agent 长程推理因 context window 有限而受限的根本问题
- **与 Hermes 对比**: Hermes 走**简单 file-backed 双 store** 路线; 该论文走**学习型**框架. 两个方向互补

### 1.2 Memory Poisoning Attacks on Retrieval-Augmented Large Language Model Agents via Deceptive Resources

- **引用**: 3
- **出处**: 2026
- **核心**: 攻击向 — 通过注入恶意检索内容污染 RAG agent 记忆
- **与 Hermes 对比**: **直接相关** — Hermes 的 `_sanitize_entries_for_snapshot` 防御类似 attack vector, 但只针对 memory file. 第三方检索内容 (RAG) 是 Hermes 不管的

### 1.3 ACON: Optimizing Context Compression for Long-horizon LLM Agents

- **引用**: **45** (最高)
- **出处**: 2025
- **核心**: 长程 agent 的上下文压缩, 优化 token 利用
- **与 Hermes 对比**: Hermes 走"不压缩 snapshot, 限制 entry 数"路线; ACON 走"压缩整个 context"

### 1.4 InfMem: Learning System-2 Memory Control for Long-Context Agent

- **引用**: 3
- **出处**: 2026
- **核心**: System-2 (慢思考) 控制 memory 加载, 智能选哪些进 context

### 1.5 Active Context Compression: Autonomous Memory Management in LLM Agents

- **引用**: 8
- **出处**: 2026
- **核心**: **自主** memory 管理 — agent 自己决定 compress/expand

### 1.6 Experience Compression Spectrum: Unifying Memory, Skills, and Rules in LLM Agents

- **引用**: 5
- **出处**: 2026
- **核心**: 把 memory / skills / rules 视为 spectrum, 统一压缩框架
- **与 Hermes 对比**: Hermes memory **不**与 skills/rules 混 — 这论文是反向思路

### 1.7 Goal-Directed Search Outperforms Goal-Agnostic Memory Compression in Long-Context Memory Tasks

- **引用**: 3
- **出处**: 2025
- **核心**: **目标导向**搜索优于无目标压缩 — 给定任务主动检索比全压缩保留更有效

### 1.8 Cross-Modal Memory Compression for Efficient Multi-Agent Debate

- **引用**: 4
- **出处**: 2026
- **核心**: 多 agent 辩论场景的跨模态 memory 压缩

### 1.9 MemOCR: Layout-Aware Visual Memory for Efficient Long-Horizon Reasoning

- **引用**: 4
- **出处**: 2026
- **核心**: 视觉 memory (text + layout + visual) — Hermes 文本 only, 这是扩展方向

### 1.10 Context Adaptive Memory-Efficient LLM Inference for Edge Multi-Agent Systems

- **引用**: 1
- **出处**: 2025
- **核心**: 边缘多 agent 的 memory-efficient 推理

## 2. 开源项目 (10 个代表, 按 stars 排序)

### 2.1 mem0ai/mem0 — ★57K

- **URL**: https://github.com/mem0ai/mem0
- **定位**: **Universal memory layer for AI Agents**
- **核心特性**:
  - LLM-agnostic (OpenAI / Claude / 本地模型)
  - 自动 extraction + storage
  - Semantic search over memory
  - **跟 Hermes 比**: 第三方服务化, **不**是 file-backed. **外部 memory provider 之一**
- **Hermes 集成**: 通过 `plugins/memory/mem0/` (Hermes 官方支持)

### 2.2 volcengine/OpenViking — ★25K (字节跳动)

- **URL**: https://github.com/volcengine/OpenViking
- **定位**: **Open-source context database designed specifically for AI Agent**
- **核心特性**:
  - Hierarchical context (类似 Hermes 的 prefix cache 思路)
  - Volcengine 商业化背景
- **与 Hermes 对比**: **比 Hermes 复杂得多**, 是完整 context database, 不是 file-backed

### 2.3 letta-ai/letta — ★23K

- **URL**: https://github.com/letta-ai/letta
- **定位**: **Platform for building stateful agents: AI with advanced memory**
- **核心特性**:
  - **Stateful agents** (核心卖点 — agent 跨 session 状态)
  - 高级 memory 管理
  - 完整 platform (UI + API + DB)
- **与 Hermes 对比**: **比 Hermes 完整得多**, 是 platform 不是 CLI agent. 适合团队部署

### 2.4 memvid/memvid — ★15K

- **URL**: https://github.com/memvid/memvid
- **定位**: **Memory layer for AI Agents. Replace complex RAG pipelines with serverless, single-file**
- **核心特性**:
  - **Single-file memory** (存到 .mp4 视频, 酷)
  - Serverless 部署
  - 替代 RAG pipeline
- **与 Hermes 对比**: 创新存储 (视频编码) — Hermes 走 markdown 文件路线, 完全不同

### 2.5 MemoriLabs/Memori — ★15K

- **URL**: https://github.com/MemoriLabs/Memori
- **定位**: **Agent-native memory infrastructure. LLM-agnostic layer that turns agent runs into structured, queryable memory**
- **核心特性**:
  - 把 agent 行为**自动**结构化为可查 memory
  - 多 framework 集成
- **与 Hermes 对比**: **零摩擦** — 不用主动 add, 框架自动记. Hermes 走"用户/agent 显式 add"

### 2.6 campfirein/byterover-cli — ★5K

- **URL**: https://github.com/campfirein/byterover-cli
- **定位**: **Portable memory layer for autonomous coding agents (file-based, syncable)**
- **核心特性**:
  - **CLI-first** (跟 Hermes 哲学一致)
  - File-based, **可同步** (git/syncthing friendly)
  - 专注 coding agent
- **与 Hermes 对比**: **最接近 Hermes 哲学** — CLI + file + portable. 但**不**做 prefix cache 优化

### 2.7 MemMachine/MemMachine — ★3K

- **URL**: https://github.com/MemMachine/MemMachine
- **定位**: **Universal memory layer for AI Agents. Scalable, extensible, integrable**
- **核心特性**:
  - 后端可插拔 (DB/vector store/...)
  - 分布式

### 2.8 memodb-io/Acontext — ★3K

- **URL**: https://github.com/memodb-io/Acontext
- **定位**: **Agent Skills as a Memory Layer**
- **核心特性**:
  - **把 skill 当 memory** — 创新思路
  - **与 Hermes "skill + memory 分离" 思路相反**
- **反思**: Hermes 明确把 skill 和 memory 拆开 (skill_manage 工具 + memory 工具), 这论文认为可以合二为一

### 2.9 OSU-NLP-Group/HippoRAG — ★3.5K (NeurIPS'24)

- **URL**: https://github.com/OSU-NLP-Group/HippoRAG
- **定位**: **RAG framework inspired by human long-term memory (hippocampal index theory)**
- **核心特性**:
  - 神经科学启发的 RAG
  - Personalized PageRank + OpenIE
  - NeurIPS'24 paper
- **与 Hermes 对比**: **学术性强**, RAG 路线; Hermes 走 file 路线

### 2.10 TencentCloud/TencentDB-Agent-Memory — ★5K

- **URL**: https://github.com/TencentCloud/TencentDB-Agent-Memory
- **定位**: **Fully local long-term memory for AI Agents**
- **核心特性**:
  - 腾讯云背景
  - 本地化, 隐私优先
- **与 Hermes 对比**: 商业数据库, Hermes 走 file 路线

## 3. Awesome list (1 个, 必看)

### IAAR-Shanghai/Awesome-AI-Memory — ★944

- **URL**: https://github.com/IAAR-Shanghai/Awesome-AI-Memory
- **定位**: **Curated knowledge base on AI memory for LLMs**
- **价值**: **唯一一个**全面收集 AI memory 论文 + 工具 + benchmark 的 curated list
- **必读**: 想深入研究 AI memory 的**唯一入口**

## 4. 趋势观察

### 4.1 学术趋势 (2025 H2 - 2026 H1)

| 时间 | 主题 | 代表 |
|---|---|---|
| 2025 早期 | Context compression 优化 | ACON (cite 45) |
| 2025 后期 | Goal-directed search | Goal-Directed Search |
| 2026 早期 | **Autonomous memory management** | Active Context Compression, InfMem |
| 2026 近期 | **Unified memory spectrum** (memory + skills + rules) | Experience Compression Spectrum |
| 2026 关注 | **Security / attack** | Memory Poisoning Attacks |

**核心趋势**: 从"**压缩以放更多**" 转向 "**自主决定放什么 / 何时取**"。

### 4.2 开源生态

| 路线 | 代表 | 特点 |
|---|---|---|
| **Library / SDK** | mem0, Memori, MemMachine | 嵌入现有 agent |
| **Platform / SaaS** | letta, mem0ai cloud | 完整产品 |
| **CLI / file-based** | byterover-cli, Hermes 自身 | 开发者工具 |
| **Database / infra** | OpenViking, TencentDB | 重型基础设施 |
| **RAG-flavored** | HippoRAG, memvid | 学术 + 创新存储 |

**Hermes 定位**: 在 **CLI/file-based 路线** 几乎是**唯一严肃项目** (byterover-cli 类似但生态小)。

### 4.3 Hermes 相对优势 / 劣势

**优势**:
- **设计简单** (file + 2200/1375 char limit) — 跟"复杂 platform"反方向
- **Prefix cache 优化** (frozen snapshot) — 学术论文都在用, 但 Hermes 落实得最早最干净
- **Pluggable provider** (8 个 external options) — **比多数 project 灵活**
- **Threat sanitization** — 安全意识领先

**劣势**:
- **Char 限制 2200/1375** — 任何复杂 agent 都嫌少 (mem0/MemMachine 都没限)
- **无 semantic search** — 全文匹配 / 短名 basename
- **无多模态** (文本 only)
- **无自动 extraction** (用户/agent 显式 add)
- **无跨 session conflict resolution** (lock 简单, 没 CRDT)

## 5. 对 Hermes 的具体建议 (按 Karpathy 4 原则)

按原则 #2 **Simplicity First**, **不**建议加:

- ❌ Autonomous compression (学术研究, 用户没需求)
- ❌ Semantic search over memory (复杂度 ↑↑, 价值存疑)
- ❌ Multi-modal memory (严重复杂度)

按原则 #1 **Think Before** + #3 **Surgical**, 或许考虑:

- ⚠️ **Char limit 提升** (2200→4400, 1375→2750) — 简单改动, 解决"满了" 抱怨
- ⚠️ **`memory(action=search, query=...)` 工具方法** — 全文 grep / 子串匹配
- ⚠️ **Auto-deprecate stale entries** (90 天未访问则 [DEPRECATED] 标记)

按原则 #4 **Goal-Driven**, 仅当用户明确要求时再做。

## 6. 引用 (References)

### 学术 (按出现顺序)

1. Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management (2026, cite 23)
2. Memory Poisoning Attacks on Retrieval-Augmented LLM Agents (2026, cite 3)
3. ACON: Optimizing Context Compression for Long-horizon LLM Agents (2025, cite 45)
4. InfMem: Learning System-2 Memory Control for Long-Context Agent (2026, cite 3)
5. Active Context Compression: Autonomous Memory Management in LLM Agents (2026, cite 8)
6. Experience Compression Spectrum: Unifying Memory, Skills, and Rules in LLM Agents (2026, cite 5)
7. Goal-Directed Search Outperforms Goal-Agnostic Memory Compression (2025, cite 3)
8. Cross-Modal Memory Compression for Multi-Agent Debate (2026, cite 4)
9. MemOCR: Layout-Aware Visual Memory for Long-Horizon Reasoning (2026, cite 4)
10. Context Adaptive Memory-Efficient LLM Inference (2025, cite 1)

### 开源 (按 stars 降序)

1. mem0ai/mem0 — ★57K
2. volcengine/OpenViking — ★25K
3. letta-ai/letta — ★23K
4. memvid/memvid — ★15K
5. MemoriLabs/Memori — ★15K
6. TencentCloud/TencentDB-Agent-Memory — ★5K
7. campfirein/byterover-cli — ★5K
8. OSU-NLP-Group/HippoRAG — ★3.5K
9. MemMachine/MemMachine — ★3K
10. memodb-io/Acontext — ★3K

### 资源

- [IAAR-Shanghai/Awesome-AI-Memory](https://github.com/IAAR-Shanghai/Awesome-AI-Memory) — AI memory 综合 curated list
- [Semantic Scholar API](https://api.semanticscholar.org/) — 论文元数据
- [GitHub Search API](https://api.github.com/search/repositories) — 开源项目
