---
title: 跨 Coding Agent Session 可移植方案
---

# 跨 Coding Agent Session 可移植层（Session Portability Layer）技术方案（V2 · 完善版）

> 基于与 ChatGPT 讨论的"开源插件 / Session 共享工具"构想，按"**开源 Session Portability Protocol + SDK + Adapter**"的定位重写并完善。
> 本版补齐了原讨论缺失的：**具体 Schema / 事件模型、同步一致性语义、安全与脱敏、测试与验收标准、实现路线图**，并对生态项目做了事实核查（见附录 A）。

---

## 0. TL;DR

- **做什么**：一个 Agent 无关的 `Agent Session Portability Layer`（可移植会话层），把 Claude Code / Codex CLI / Pi / Hermes 等 Coding Agent 的私有 session 统一抽象为 **Canonical Session（事件源模型）**，提供双向 Adapter、Context Compiler（上下文编译）、Sync（同步）、Identity（身份）。
- **不做什么**：不做 Session 搜索/查看器（交给 cass）、不做多机同步基础设施（对接 Stift）、不做 IDE（对接 ccmux / Agent Sessions）。
- **核心产品形态**：`sessionctl` CLI + Rust 核心 SDK + 4 个首发 Adapter（Claude / Codex / Pi / Hermes）+ MCP Server。
- **第一版验收**：L0（历史迁移）100% 保真、L1（上下文续作）≥90%、`claude → codex` 与 `pi → hermes` 两条跨 Agent 链路可端到端演示。
- **最大的坑（提前声明）**：不要追求"100% Session 等价"；用 **事件级 L0/L1/L2 标注** 管理保真度预期；用 **追加式事件日志 + Session DAG** 处理分支与合并。

---

## 1. 背景与目标

### 1.1 原始需求（来自对话）

> "如果我想设计和开发一个兼容主流的 Code Agent、Hermes Agent、Pi Agent 这些的 session 共享的开源插件，是有必要的吗？"

### 1.2 结论（对齐 ChatGPT 的分析，并收紧）

- 需求**真实存在且已被验证**：Stift（跨机同步）、cass（统一索引搜索）、agent-session-bridge（Pi↔Claude↔Codex 桥）、Agent Sessions（macOS 统一展示/Resume）等都在解决相邻问题。
- 但**"再做一个 Session 查看/搜索/扫描工具"没有增量价值**。
- 真正的机会点是：**标准化"Canonical Session 模型 + Adapter SDK + Context Compiler"**，即把 Session 从"某个 Agent 的私有文件"变成"可移植的资产"。

### 1.3 本方案的目标

1. 定义一份**版本化、可扩展的 Canonical Session 规范**（事件模型 + 元数据 + DAG 语义）。
2. 定义**Adapter 接口契约**，让新增 Agent 的接入成本降到"写一个 parser + 一个 writer"。
3. 定义 **Context Compiler**，把完整历史编译成目标 Agent 可直接继续工作的上下文（而非粗暴复制 transcript）。
4. 定义 **Sync 语义**：追加式日志、游标增量、分支合并、加密脱敏。
5. 给出**可执行的实现路线图**（M0–M7）与验收标准。

---

## 2. 生态现状（事实核查版）

下表基于 2026-08 的公开信息核查（见附录 A 的 URL）：

| 项目 | 类型 | 定位 | 状态 | 与我们的关系 |
|---|---|---|---|---|
| [Stift](https://www.producthunt.com/products/stift?launch=stift) | 开源+云 | 跨机器 Session 同步（Claude/Codex/Gemini/Cursor/OpenCode/Aider） | ✅ 活跃 | **对接**（作为 Sync 后端） |
| [coding-agent-search (cass)](https://github.com/Dicklesworthstone/coding_agent_session_search) | 开源 (Rust) | 统一索引/搜索 11+ Agent 的 session | ✅ 活跃 | **对接**（消费我们的 canonical store） |
| [agent-session-bridge](https://github.com/bohdanpodvirnyi/agent-session-bridge) | 开源 | Pi ↔ Claude Code ↔ Codex native session 桥 | ✅ 存在 | **借鉴/竞品** |
| [agentctl](https://github.com/leofmarciano/agentctl) | 开源 | Claude ↔ Codex Canonical Session 桥 | ✅ 存在 | **借鉴**（canonical 思想） |
| [ccmux](https://github.com/skzv/ccmux) | 开源 | Session Manager / TUI / 多机 attach | ✅ 存在 | **对接**（UI 层） |
| [claude-codex-handoff](https://github.com/OpenMOSS/claude-codex-handoff) | 开源 | `.handoff/` 异步任务交接 | ✅ 存在 | **借鉴**（handoff 事件） |
| [agent-work-mem](https://github.com/daystar7777/agent-work-mem) | 开源 | Vendor-neutral Markdown Memory | ✅ 存在 | **借鉴**（memory/context 层） |
| [session-orchestrator](https://github.com/Kanevry/session-orchestrator) | 开源 | 跨 Agent workflow state 同步 | ✅ 存在 | **借鉴**（workflow 层） |
| Hermes Agent | 开源 | `~/.hermes/state.db`（SQLite WAL + FTS5） | ✅ 活跃 | **Adapter 目标** |
| Pi（schovest/pi） | 开源 | `~/.pi/agent/sessions/--<path>--/<ts>_<uuid>.jsonl`（树结构） | ✅ 活跃 | **Adapter 目标** |
| Claude SessionStore | 官方 SDK | Claude Agent SDK 外部会话存储（S3/Redis/DB） | ✅ 官方 | **Adapter 目标（Claude 侧）** |

**核查发现（对原对话的修正/补充）**：
- 原对话引用的项目基本都存在（附录 A 逐条核实），但 **agentctl 存在同名项目（OrgLoop/agentctl）**，实现细节需以 `leofmarciano/agentctl` 为准并自行验证。
- **Pi 的 session 不是简单的 JSONL 线性流**：v3 版本已支持 `id/parentId` 树结构（就地分支），内容块含 `text/image(base64)/thinking/toolCall`，且类型定义在 `@schovest/pi-ai` / `@schovest/pi-coding-agent` 两个 npm 包里 —— Adapter 必须处理树，不能假设线性。
- **Hermes 是 SQLite（WAL）而非 JSONL**：读侧要用只读连接并处理 WAL；`api_content` 字段是"字节保真的侧车"（保证 prompt-cache 稳定的重放），迁移时若丢弃会造成 token 成本差异 —— 这正好印证了 L2（Native Resume）的难度。

---

## 3. 定位与边界

### 3.1 一句话定位

> **Open protocol for portable AI coding sessions —— 让 Session 属于项目与用户，而不属于任何单一 Agent。**

### 3.2 我们做（Own）

| 能力 | 说明 |
|---|---|
| Canonical Session 规范 | 事件模型、manifest、DAG、版本迁移 |
| Adapter SDK | 解析/写回各 Agent 私有格式的插件框架 |
| Context Compiler | 全量历史 → 目标 Agent 可用的精简上下文 |
| 事件级保真管理 | L0/L1/L2 语义标注与降级策略 |
| 本地/远端存储 | 追加式日志、checkpoint、加密脱敏 |
| Identity | session URI、签名、所有权转移、handoff receipt |
| 接入面 | CLI（sessionctl）、Rust SDK、MCP Server、TypeScript/Python 绑定 |

### 3.3 我们不做（Integrate instead）

| 不做 | 理由 | 对接方式 |
|---|---|---|
| Session 搜索/全文检索 | cass 已做且做得好 | canonical store 作为 cass 的一个 provider |
| 跨机同步基础设施 | Stift 已做 | canonical store 可作为 Stift 的 sync 后端 |
| Session 管理 UI/TUI | ccmux / Agent Sessions 已做 | 我们的 store 作为其数据源 |
| 通用 Memory 层 | agent-work-mem 已做 | Context Compiler 可输出其 markdown 形态 |
| Agent 编排/工作流 | session-orchestrator / A2A 生态 | 我们提供 `handoff` 事件与 receipt，供其消费 |

---

## 4. 总体架构

```
                     ┌───────────────────────┐
                     │       sessionctl      │   CLI（人 + CI 脚本）
                     └──────────┬────────────┘
                                │
                     ┌──────────▼────────────┐
                     │   Session SDK (Rust)  │   core：模型/存储/编译/同步/身份
                     │  ├ TS bindings (Pi)   │
                     │  ├ Python bindings    │   （Hermes 生态是 Python）
                     │  └ MCP Server         │   （任意 Agent 通过 MCP 读/写）
                     └──────────┬────────────┘
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
 ┌──────────────┐      ┌────────────────┐      ┌────────────────┐
 │ Canonical    │      │ Context        │      │ Sync Engine    │
 │ Session      │      │ Compiler       │      │ (cursor/log)   │
 │ Model/Store  │      │ (L1/L2 编译)   │      │ + Identity     │
 └──────┬───────┘      └───────┬────────┘      └───────┬────────┘
        └──────────────────────┼───────────────────────┘
                               ▼
                     ┌──────────────────┐
                     │ Adapter Framework│  插件注册表 + trait
                     └──┬───┬───┬───┬───┘
                        ▼   ▼   ▼   ▼
                     Claude Codex Pi  Hermes   （M2+：OpenCode/Cursor/Gemini/Aider）
```

数据流（一次跨 Agent 接力）：

```
Claude Code
   │  exit / 实时 watch
   ▼
Claude Adapter ──解析──▶ Canonical Events ──▶ Store（追加式日志）
                                                   │
                              ┌────────────────────┤
                              ▼                    ▼
                      Context Compiler      （可选）Sync Engine → 远端/另一台机器
                              │
                              ▼
                      Codex Context（L1 编译结果）
                              │
                              ▼
                      Codex Adapter ──写回──▶ Codex rollout-*.jsonl
                              │
                          codex resume ✓
```

---

## 5. Canonical Session 模型（核心设计）

> 原则：**Session = 追加式事件日志 + 不可变 manifest + DAG 链接**。
> 事件一旦写入不可修改；"修改"一律通过新事件表达（事件源模式）。这直接解决同步冲突与审计问题。

### 5.1 目录/文件形态

```
~/.sessionctl/store/
├── sessions/
│   └── <session-id>/                 # 如 sess_8f3a...
│       ├── manifest.json             # 元数据（签名、所有权、指针）
│       ├── events.jsonl              # 追加式事件日志（唯一事实源）
│       ├── events.jsonl.ckpt         # 每 N 条做一次校验和锚点（可选）
│       ├── checkpoints/
│       │   └── ckpt_<seq>.tar.zst    # 文件快照/artifact 快照
│       └── artifacts/                # 大对象（diff、图片、日志），按事件引用
└── index.sqlite                      # 可选：本地搜索索引（供 cass/ccmux 消费）
```

### 5.2 Manifest（session 元数据）

```json
{
  "schema_version": "0.1.0",
  "session_id": "sess_8f3a...",
  "session_uri": "session://acme/vehicle-agent/implement-a2a-auth/sess_8f3a",
  "project": { "name": "vehicle-agent", "cwd_hash": "sha256:...", "git_head": "a1b2c3d" },
  "created_by": { "agent": "claude", "adapter_version": "0.1.0", "session_id": "原始ID" },
  "current_owner": { "agent": "codex", "granted_at": 1787022776.3 },
  "parent_session": "sess_123",            // DAG 链接
  "lineage": { "root": "sess_000", "fork_of": "sess_123", "merged_into": null },
  "event_count": 1024, "first_seq": 0, "last_seq": 1023,
  "compiled_context": { "at_seq": 1023, "sha256": "...", "tokens": 28400 },
  "signature": { "alg": "ed25519", "key_id": "key_01...", "sig": "base64..." }
}
```

### 5.3 事件信封（Event Envelope）

每个事件一行 JSONL：

```json
{
  "seq": 42,                  // 单调递增，per-session
  "ts": 1787022776.310706,    // 来源时间（保留精度，用于对齐）
  "agent": "claude",          // 产生者（可能是源 agent）
  "actor": "user|agent:claude|system",
  "type": "message.assistant",
  "level": 1,                 // 本事件保证的兼容级别：0|1|2
  "payload": { ... },         // 事件体（见 5.4）
  "refs": ["artifact:ckpt_12", "file:src/main.rs@a1b2"],
  "parent_seq": 41,           // DAG：分支时指向 fork 点的 seq
  "origin": { "agent": "claude", "native_id": "uuid-xxx", "native_seq": 88 },
  "checksum": "sha256:..."    // 本行前内容的哈希链（防篡改/校验）
}
```

### 5.4 事件类型表（Taxonomy，第一版）

| 类型 | 含义 | L0 | L1 | L2 | 关键 payload 字段 |
|---|---|---|---|---|---|
| `session.start` | 会话开始 | ✅ | ✅ | ✅ | cwd、git_head、model、config |
| `session.end` | 会话结束 | ✅ | ✅ | ✅ | end_reason、统计 |
| `message.user` | 用户消息 | ✅ | ✅ | ✅ | content（text/image） |
| `message.assistant` | 助手消息 | ✅ | ✅ | ✅ | content、model、stop_reason、usage |
| `message.thinking` | 推理/思考块 | ⬜ 降级为注释 | ✅ | ✅ | thinking 文本、类型（visible/encrypted） |
| `tool.call` | 工具调用 | ✅ | ✅ | ✅ | name、arguments、tool_use_id |
| `tool.result` | 工具结果 | ✅ | ✅ | ✅ | 内容（**默认脱敏**）、is_error |
| `file.read` | 读取文件 | ⬜ | ✅ | ✅ | path、range、digest |
| `file.edit` | 编辑文件 | ⬜ | ✅ | ✅ | path、diff（unified）、before/after digest |
| `command.run` | 命令执行 | ⬜ | ✅ | ✅ | cmd、exit_code、stdout_tail（截断）、cwd |
| `todo.add/update` | 任务项 | ⬜ | ✅ | ✅ | id、status、assignee |
| `decision` | 决策记录 | ⬜ | ✅ | ✅ | 结论、理由、备选 |
| `memory.write` | 持久记忆写入 | ⬜ | ✅ | ✅ | key、value、scope |
| `checkpoint` | 快照锚点 | ✅ | ✅ | ✅ | 引用的 artifact 列表、compiler 输出 |
| `context.compiled` | 上下文编译结果 | ✅ | ✅ | ✅ | tokens、summary、provenance 指针 |
| `handoff` | 交接事件 | ✅ | ✅ | ✅ | 接收方 agent、receipt、要求/待办 |
| `session.fork/merge` | 分支/合并 | ✅ | ✅ | ✅ | from_seq、to_seq、reason |
| `meta` | 其它元数据（模型切换等） | ✅ | ✅ | ✅ | key/value |

**设计规则**：
1. `level` 标注该事件在跨 Agent 迁移时**能保证**的语义级别（见 5.5），由写入方（Adapter）诚实标注，Context Compiler 据此决策取舍。
2. 所有**内容类**事件默认经过**脱敏管线**（见 8.5）后才入库；`origin.native_id` 保留溯源，便于 L2 回写。
3. `tool.result` / `command.run` 的 stdout 默认只存**头部+尾部截断**（如各 4KB），完整内容放 artifacts 并按需同步 —— 控制体积与泄密面。
4. 事件与 artifact 分离：大对象（diff、截图、日志）进 `artifacts/`，事件只存引用。

### 5.5 兼容级别（事件级语义）

| 级别 | 定义 | 目标 | 度量方式 |
|---|---|---|---|
| **L0 History** | user/assistant/tool/result 可无损迁移 | 查看、归档、审计 | 事件级 round-trip 一致性测试 |
| **L1 Context** | 任务/TODO/决策/文件/命令/working state 可迁移，目标 Agent 能**继续干活** | 跨 Agent 接力 | "接力成功率"（见 §15） |
| **L2 Native Resume** | 尽可能恢复原生 session（claude session_id / codex rollout_id / pi 树节点 / hermes 行） | 无缝续聊 | 原生 resume 成功率 |

**降级规则（Lossy-but-honest）**：
- 源事件无对应物时**不静默丢弃**：写入 `meta` 事件标记 `dropped:<type>` 或降级为 L0 摘要，并在 `context.compiled` 中显式声明"目标 Agent 看不到 X"。
- 例：Claude 的 `Opus thinking` 转 Codex 时 → 降级为 `message.thinking`（若 Codex 支持）或折叠进 assistant 消息附注；`todo` 无对应 → 注入上下文摘要。

### 5.6 Session DAG（分支与合并）

来源事实：
- Pi 原生支持 `id/parentId` 树（就地分支）；
- Hermes 用 `parent_session_id` 链（压缩触发分裂）；
- Claude/Codex 是线性文件（但 Claude 有 subagent 树、Codex 有 rollout 切换）。

因此 Canonical 模型必须原生支持 DAG：

```
sess_000 (root)
   └─ sess_123 ──┬─ sess_456 (fork@seq42, 换到 Codex 继续)
                 │
                 └─ sess_789 (另一条探索线)
                      └─ sess_912 (merge ← sess_456 的 handoff 结果)
```

- `fork`：新 session，`parent_seq` 指向源日志的某 seq；两个 session 此后各自追加，天然无冲突。
- `merge`：通过 `handoff` 事件 + receipt 表达"把 B 的结果并回 A"，**不合并日志本身**（避免复杂 3-way merge），只记录指针与结果摘要。
- 查询 lineage 用 manifest 的 `lineage` 字段 + 递归，与 Hermes 的 `WITH RECURSIVE` 思路一致。

### 5.7 模型版本化与迁移（学 Hermes 的做法）

- `schema_version` 单值 + 声明式列新增（`_reconcile_columns` 式）+ 版本门控的数据迁移链。
- 事件类型采用 **开放式命名空间**（`message.*`、`tool.*`、`file.*`），未知类型不报错，落 `meta` 桶并保留原始 payload，保证**前向兼容**（旧版本能读新数据）。
- 每个事件 `payload` 用 JSON，未知字段保留 —— 不做强 schema 校验，只做信封校验。

---

## 6. Adapter 框架

### 6.1 Adapter Trait（Rust 核心）

```rust
#[async_trait]
pub trait SessionAdapter: Send + Sync {
    fn id(&self) -> &'static str;                       // "claude" | "codex" | "pi" | "hermes"
    fn discover(&self, cwd: &Path) -> Vec<SessionRef>;  // 找到本地 session 文件

    /// 增量解析：从游标开始读新事件，返回 canonical 事件流
    async fn capture(&self, src: &SessionRef, cursor: &Cursor)
        -> Result<EventBatch, AdapterError>;

    /// 把 canonical 会话（或其 L1 编译产物）写回该 Agent 的原生格式
    async fn materialize(&self, session: &CanonicalSession, target: MaterializeTarget)
        -> Result<NativeSessionHandle, AdapterError>;

    /// 尽力恢复原生 session（L2）
    async fn resume(&self, session: &CanonicalSession) -> Result<ResumeHandle, AdapterError>;

    /// 事件级保真标注：该 adapter 对某类型事件能保证的 level
    fn fidelity(&self, event_type: &str) -> Fidelity;   // L0/L1/L2/Lossy
}
```

### 6.2 增量捕获（Cursor / Watch）

- 每个（session, 源文件）维护 `Cursor`（源文件偏移 + 行号 + mtime/hash）。
- 首次：全量解析 + 基线校验和；之后：按文件偏移增量读取（`tail -f` 语义）。
- SQLite 源（Hermes）用**只读连接** + `max(id)` 游标 + 触发器不可行则轮询 `updated_at`；**必须处理 WAL**（只读打开仍可读 WAL，但要注意 `-shm` 锁，失败时退避重试 —— Hermes 自己的写竞争策略可借鉴：BEGIN IMMEDIATE + 抖动重试）。
- 幂等：canonical 事件带 `origin.native_seq`，导入去重靠 (agent, native_id) 唯一索引。

### 6.3 首发 4 个 Adapter 的格式要点（基于实测文档）

| Agent | 位置与格式 | 解析要点 | L2 Resume 要点 |
|---|---|---|---|
| **Claude Code** | `~/.claude/projects/<escaped-path>/<uuid>.jsonl`，JSONL；行类型含 user/assistant/summary/system | 内容块（text/tool_use/tool_result/thinking）；`uuid`/`parentUuid` 建树（subagent）；summary 行是压缩点 | 用 Claude Agent SDK 的 External SessionStore（S3/Redis/DB）可官方续聊；CLI 侧续聊靠 `--resume <session_id>` |
| **Codex CLI** | `~/.codex/sessions/<project>/rollout-*.jsonl`，行类型：session_start / message / agent_event / model_change / session_end | 消息 content 为 block 数组；agent_event.payload 里含工具调用与结果；rollout 可多个 | `codex resume <rollout_id>`；注意 config（model、MCP 配置）在 session_start 里 |
| **Pi** | `~/.pi/agent/sessions/--<path>--/<timestamp>_<uuid>.jsonl`；JSONL，`id/parentId` 树，版本 v1–v3（v3 把 hookMessage 改名 custom） | 内容块：text / image(base64+mime) / thinking / toolCall；消息类型在 `@schovest/pi-ai`、`@schovest/pi-coding-agent`（npm，TS）中定义 | Pi 原生 `/resume` 选会话；树结构可保留分支 |
| **Hermes** | `~/.hermes/state.db`（SQLite WAL）；sessions / messages / messages_fts(5) / state_meta；schema v23 | 只读连接；messages 行含 role/content/tool_calls(JSON)/reasoning/token 统计；`api_content` 是字节保真侧车（重放稳定性） | `hermes` CLI/gateway 按 session_id 续聊；lineage 用 `parent_session_id` |

> 标注：以上字段名以各 Agent 当前版本实测为准；Adapter 开发第一步是**写格式快照测试**（golden fixture），锁定字段后再实现解析。

### 6.4 保真度矩阵（首发版本目标）

| 源 \ 目标 | → Claude | → Codex | → Pi | → Hermes |
|---|---|---|---|---|
| Claude | L2 | L1 | L1 | L1 |
| Codex | L1 | L2 | L1 | L1 |
| Pi | L1 | L1 | L2 | L1 |
| Hermes | L1 | L1 | L1 | L2 |

- L0（历史）全部要求 100%。
- L2 只承诺"同 Agent 换机器/换后端"场景（这本来就是 Stift 的主场，我们与其协同）。
- 跨 Agent 承诺 L1：**"目标 Agent 拿到手能继续把任务干完"**。

### 6.5 Adapter 测试策略

- **Golden Fixture**：每个 adapter 维护 `fixtures/<agent>/<场景>/`，含真实脱敏的源文件 + 期望 canonical 事件 JSON。CI 跑 round-trip：`parse → canonical → materialize → parse` 断言关键内容不变（L0 级逐事件 diff）。
- **增量测试**：模拟文件追加/DB 插入，断言 cursor 只产生 delta。
- **脏数据测试**：损坏行、未知事件类型、超大 payload → 不崩溃、跳过并记 `meta`。
- **性能基准**：10 万事件导入 < 1s（Rust，release）；watch 增量延迟 < 100ms。

---

## 7. Context Compiler（L1 的核心）

> 全量历史 ≠ 目标 Agent 需要的上下文。Context Compiler 负责"编译"，这是与"Session Converter"拉开档次的地方。

### 7.1 输入

- Canonical 事件日志（全量）。
- 可选外部信号：git status、最近修改文件、打开的 TODO、测试结果。

### 7.2 上下文条目类型（Context Item）

| 条目 | 来源事件 | 优先级（默认） |
|---|---|---|
| 任务陈述（当前目标） | 最近 message.user + decision | P0 |
| 未完成任务 / TODO | todo.* | P0 |
| 关键决策 | decision | P0 |
| 打开的问题 / 阻塞点 | message.user / command.run 错误 | P0 |
| 最近修改文件 | file.edit（按 ts 排序） | P1 |
| 最近命令与结果 | command.run（错误优先） | P1 |
| 技术约束（架构说明） | memory.write / 用户消息中标记 | P1 |
| 关键对话摘录 | message.*（摘要器提取） | P2 |
| 完整历史指针 | checkpoint / 源 session 引用 | 仅引用 |

### 7.3 预算分配算法（Token Budget）

```
budget = target_context_window - reserve(目标 Agent 系统提示 + 工具定义 + 回复余量)
   ↓
P0 条目 100% 保留（保真、不摘要，超预算则报错并提示缩小任务）
   ↓
P1 按 token 单价排序，直到预算的 ~60%
   ↓
P2 走摘要器（LLM 摘要 / 抽取式摘要），占剩余预算
   ↓
任何被裁掉的内容写入 context.compiled 事件的 dropped 清单（可追溯）
```

- 摘要**必须带溯源指针**：每条摘要附 `provenance: [seq...]`，需要完整细节时可一键回到 checkpoint。
- 摘要器可插拔：本地小模型（省钱、离线）或云端模型（质量）；输出格式固定为"结论 + 证据 seq"。

### 7.4 输出形态（按目标 Agent 模板化）

- 面向 **Claude/Codex/Pi/Hermes**：`@context.md` 或系统提示注入（各 Agent 有不同注入点，如 `CLAUDE.md`/`.codex/AGENTS.md`/MCP）。
- 面向 **agent-work-mem 生态**：输出 `STATE.md / TASKS.md / DECISIONS.md / HANDOFF.md`。
- 面向 **A2A**：输出 Task/Artifact 结构（card + artifact 清单），与 A2A Task 模型对齐。

---

## 8. Sync 引擎与一致性

### 8.1 追加式事件日志（事实源）

- 每个 session 的日志**只追加**：无 UPDATE、无 DELETE（有 `meta` 事件表达撤销/纠正）。
- 每行带 `checksum`（前一行哈希链），防篡改 + 传输校验。
- 每 N 条（默认 512）写一个 `events.jsonl.ckpt` 锚点（前 N 条的整体校验和），允许从锚点恢复。

### 8.2 游标与增量同步

- 同步单位 = **事件**，不是文件。`Sync Engine` 维护 `(session, seq)` 游标。
- push/pull 时只传输 `seq > cursor` 的事件 + 新 artifacts；HTTP/自托管端支持范围请求。
- 大 artifact 可配置"不随事件同步"（如只同步 4KB 截断 + 哈希，需要时按需拉取）。

### 8.3 冲突与合并规则（关键设计）

| 场景 | 规则 |
|---|---|
| 两台机器同时往同一 session 追加 | **不可能冲突**：追加式日志，两侧 seq 空间独立 → 用 `(machine_id, seq)` 或 Lamport 时间戳排序，事件级合并 |
| 同一事件被双写 | 靠 (agent, native_id) / 事件内容哈希去重（幂等导入） |
| 分支 | `fork` 新 session，永不 merge 日志本体 |
| 元数据（title/owner）竞争 | 最后写入者胜 + 保留历史版本（manifest 是可版本化的 JSON） |
| 远端删除 | 墓碑事件 `meta{deleted:true}`，不物理删除（审计） |

### 8.4 存储后端（可插拔）

| 后端 | 用途 | 说明 |
|---|---|---|
| 本地目录 | 默认 | `~/.sessionctl/store/` |
| Git 仓库 | 单人/团队轻量同步 | 事件文件按追加提交；配合 8.3 无冲突特性天然适合 git |
| 自托管 HTTP server | 团队 | 简单 append + cursor API；可后续对齐 Stift 协议 |
| S3/对象存储 | 归档 | 事件打包上传，artifacts 分桶 |
| SQLite index | 本地搜索 | 供 cass/ccmux/Agent Sessions 消费（我们不自研搜索） |

### 8.5 加密与脱敏（安全基线）

- **脱敏（capture 时，默认开）**：API key 模式、`token=...`、`Authorization:` 头、`.env` 内容、私钥块 → 事件中存 `[REDACTED:<type>]`，原文只进本地 vault（可选）。
- **加密（at rest）**：默认 `age`（X25519）加密 artifacts 与远端同步包；密钥放系统 keychain，不入仓库。
- **加密（thinking 块）**：Claude 的 encrypted thinking 已是加密块，原样保留 opaque 引用，不尝试解密。
- 公开分享（未来）时，`sessionctl export --public` 走二次脱敏 + 签名。

---

## 9. Session Identity 与安全

### 9.1 Session URI（SPIFFE 式）

```
session://<org>/<project>/<task>/<session-id>
例：session://acme/vehicle-agent/implement-a2a-auth/sess_8f3a
```

### 9.2 签名与校验

- manifest 用 Ed25519 签名（`sessionctl sign` / adapter 自动签）。
- 事件日志哈希链保证完整性；远端拉取时 `sessionctl verify` 校验。

### 9.3 所有权转移与 Handoff Receipt

```
Claude ──handoff──▶ Session Layer ──handoff──▶ Codex
        (owner: agent:claude)   (receipt)   (owner: agent:codex)
```

- `handoff` 事件带 `from_agent / to_agent / expectation / ack`；receipt 是签名过的 JSON，可作审计与 A2A 交接凭据。
- `current_owner` 变更记录在 manifest 历史中，避免"两个 agent 同时以为自己在主导"。

### 9.4 与 A2A / Agent IAM 对齐

- 复用用户既有方向：`Agent Identity → Principal → Delegation Context → IAM`。
- Session 作为 **Delegation Context 的载体**：A2A 的 Task/Artifact 卡通过 `context.compiled` 输出；IAM 决定"哪个 agent 可以 resume/fork 哪个 session"。
- 这是把本项目和用户已有的 A2A/IAM/Workflow Studio 拼成完整拼图的关键接口（见 §16 下一步）。

---

## 10. CLI / SDK / MCP API

### 10.1 sessionctl 命令面（第一版）

```
sessionctl init [--store <dir>]                  # 初始化 store
sessionctl status [--json]                       # 当前项目各 agent session 概览
sessionctl list [--agent claude] [--json]
sessionctl show <session> [--events] [--seq N]
sessionctl import --agent claude [--path ...]    # 解析进 canonical store（幂等）
sessionctl export <session> --agent codex        # 编译 + 写回目标 agent 原生格式
sessionctl resume <session> --agent pi           # L2 尽力恢复
sessionctl fork <session> --at <seq> --reason ...
sessionctl checkpoint <session> [--message ...]
sessionctl handoff <session> --to codex --note "..."
sessionctl push / pull [--remote ...]            # 增量同步（游标）
sessionctl compile <session> --for codex [--budget 32000] [--out @context.md]
sessionctl redact / verify / doctor              # 脱敏复查 / 完整性校验 / 环境自检
```

### 10.2 SDK 接口（Rust core，绑定 TS/Python）

```rust
Session::open(id) / create(manifest) / append(events) / tail(cursor)
Session::fork(at_seq) / checkpoint(label) / handoff(to, note)
Compiler::compile(&Session, Target::Codex, Budget) -> CompiledContext
AdapterRegistry::get("claude") -> Arc<dyn SessionAdapter>
Store::local() / git(remote) / http(remote)
Identity::sign(manifest) / verify(manifest) / transfer_ownership(uri, principal)
```

### 10.3 MCP Server（差异化亮点）

- 提供一个 MCP server：`sessionctl mcp`。
- 任何支持 MCP 的 Agent（Claude/Codex/Pi/Hermes 都支持）可调用：
  - `session.current()` / `session.summary()` / `session.continue(prev_session, target)`
- 效果：**Agent 自己就能在接力时把上一手的 canonical context 拉进来**，无需人工跑 CLI —— 这是"Portability Layer"真正进入工作流的方式。

---

## 11. 仓库结构（Monorepo，Cargo workspace）

```
sessionctl/
├── crates/
│   ├── core-model/          # manifest、事件模型、DAG、校验
│   ├── store/               # 本地存储、日志追加、checkpoint、index.sqlite
│   ├── adapters/
│   │   ├── framework/       # trait、registry、cursor、golden 测试工具
│   │   ├── claude/
│   │   ├── codex/
│   │   ├── pi/
│   │   └── hermes/
│   ├── context-compiler/    # 预算分配、摘要器接口、输出模板
│   ├── sync/                # 游标、git/http 后端、幂等导入
│   ├── identity/            # 签名、URI、所有权、receipt
│   ├── cli/                 # sessionctl
│   └── mcp-server/
├── bindings/                # ts/ (Pi 生态), python/ (Hermes 生态)
├── fixtures/                # golden fixtures（脱敏）
├── docs/                    # 规范：schema、adapter 契约、协议
└── schema/                  # canonical-session.schema.json（草案见附录 B）
```

---

## 12. 实现路线图（M0–M7，每个里程碑带验收标准）

| 里程碑 | 内容 | 验收标准 |
|---|---|---|
| **M0 模型与存储** | core-model + store + CLI 骨架 | `sessionctl init/status`；append 1 万事件 < 100ms；哈希链校验通过 |
| **M1 Claude Adapter** | parse Claude JSONL → canonical；materialize → Claude | golden round-trip 通过；`claude → canonical` 增量 watch < 100ms |
| **M2 Codex Adapter** | parse Codex rollout → canonical；materialize | **端到端演示 1：`claude resume → codex` 接力**（L1） |
| **M3 Pi Adapter** | Pi JSONL（树结构、v3）→ canonical；resume 到 Pi | pi 树分支导入后 `sessionctl fork` 语义一致 |
| **M4 Hermes Adapter** | Hermes SQLite（只读+WAL）→ canonical | 大库（>10 万消息）导入 < 2s；FTS 字段映射正确 |
| **M5 Context Compiler** | 预算分配 + 摘要接口 + 4 个输出模板 | **端到端演示 2：`pi → hermes` 接力**；budget 达标率 ≥95% |
| **M6 Sync** | cursor 增量 + git 后端 + 幂等 | 双机演示：A 机 claude 追加，B 机 codex 拉到 delta 续聊 |
| **M7 Identity & 安全** | 签名、脱敏基线、handoff receipt | `verify` 拦截篡改；脱敏正则套件测试通过 |

**原则**：每个里程碑独立可发布；M1–M4 可并行（Adapter 之间无依赖）；M5 依赖 M0+M1；M6/M7 不阻塞前序。

---

## 13. 风险与对策

| 风险 | 影响 | 对策 |
|---|---|---|
| Agent 格式漂移（vendor 升级改格式） | Adapter 失效 | 版本快照测试（golden fixture）在 CI 锁定；格式版本字段；`doctor` 自检；社区 adapter 仓库独立发版节奏 |
| 泄密（API key、.env、日志里的 token） | 安全事故 | capture 时默认脱敏（8.5）；export/分享走二次脱敏；事件库本身可加密 |
| 追求 100% 等价导致 Scope 爆炸 | 项目烂尾 | 事件级 L0/L1/L2 标注 + 显式降级；跨 Agent 只承诺 L1 |
| Context Compiler 的 LLM 摘要成本/不稳定 | 体验差 | 可插拔摘要器；抽取式摘要兜底；摘要带溯源可回查 |
| 同 Agent 续聊被官方私有协议锁死 | L2 受限 | L2 只承诺"同 Agent 换环境"；官方能力（Claude SessionStore / codex resume / pi resume / hermes resume）优先复用，不逆向 |
| 许可证/ToS（Anthropic/OpenAI 对 session 数据的要求） | 合规 | 发布前做 ToS 审查；仅本地处理为默认；文档明确边界 |
| 社区维护压力（adapter 数量膨胀） | 烂尾 | 首发只做 4 个；adapter 独立 crate 与维护者；明确"新增 adapter = 贡献者责任" |
| 与 cass/Stift/agentctl 定位重叠 | 被取代 | §3 边界 + §14 协同：做协议层，不做应用层 |

---

## 14. 与现有生态的协同（不重复造轮子）

```
                   ┌─────────────────────────────┐
                   │      Our Portability Layer  │
                   │  (canonical session store)  │
                   └──────┬──────────┬───────────┘
                          │          │
              ┌───────────▼──┐   ┌───▼────────────┐
              │ cass         │   │ ccmux / Agent  │
              │ (search)     │   │ Sessions (UI)  │
              └───────────┬──┘   └───┬────────────┘
                          │          │
                   ┌──────▼──────────▼──────┐
                   │ Stift (sync) + Claude  │
                   │ SessionStore (官方)     │
                   └────────────────────────┘
```

- **cass**：把 `~/.sessionctl/store` 加为一个 provider（它的架构已证明"统一解析本地 session"可行，我们补充"规范化写入"）。
- **Stift / agent-session-bridge**：canonical store 可作为其数据源/同步目标；协议层对齐，避免重复。
- **Claude SessionStore / Codex resume / Pi resume / Hermes resume**：L2 一律优先调用官方机制，不自造。
- **A2A / Agent IAM（用户既有方向）**：见 §9.4，Session 成为 Delegation Context 的载体。

---

## 15. 成功指标（KPI，MVP 阶段）

| 指标 | 目标 |
|---|---|
| L0 保真（跨 Agent 历史迁移） | round-trip 测试 100% 通过 |
| L1 接力成功率（目标 Agent 无需人工补料可继续任务） | ≥ 90%（验收场景抽样） |
| 导入性能 | 10 万事件 < 1s；增量 watch < 100ms |
| 泄密事故 | 0（脱敏套件 + 渗透样例覆盖） |
| 新增 Adapter 成本 | 单人 ≤ 2 周（有格式文档）/ ≤ 4 周（无文档需逆向） |
| 生态采纳 | MVP 后 ≥ 2 个第三方项目消费 canonical store（cass provider、ccmux 插件） |

---

## 16. 下一步行动（从本方案到代码）

1. **定规范**：按附录 B 草案产出 `canonical-session.schema.json` v0.1 + `adapter-contract.md`（trait 详细文档）。
2. **写 PRD**：目标用户（个人多 agent 工作流 → 团队）、用例（跨 agent 接力 / 换机器 / 归档审计）、非目标。
3. **Spike ×2（一周内）**：
   - Spike A：Claude JSONL → canonical（验证事件模型够用）。
   - Spike B：Hermes SQLite 只读 + WAL 读取（验证最难的源）。
4. **M0 落地**：core-model + store + sessionctl 骨架。
5. **M1–M4 并行**：四个 adapter + golden fixtures。
6. **评审点**：M2 完成后做一次"claude → codex 接力"产品演示，验证定位是否成立再继续。

---

## 附录 A：生态项目核查表（2026-08）

| 项目 | 链接 | 核查结果 |
|---|---|---|
| Stift | producthunt.com/products/stift | ✅ 存在，定位"跨机器同步 coding agent sessions" |
| coding-agent-search (cass) | github.com/Dicklesworthstone/coding_agent_session_search | ✅ 存在，Rust，11+ providers |
| agent-session-bridge | github.com/bohdanpodvirnyi/agent-session-bridge | ✅ 存在，Pi↔Claude↔Codex 桥 |
| agentctl | github.com/leofmarciano/agentctl | ✅ 存在（注意有同名 OrgLoop/agentctl） |
| ccmux | github.com/skzv/ccmux | ✅ 存在 |
| claude-codex-handoff | github.com/OpenMOSS/claude-codex-handoff | ✅ 存在 |
| agent-work-mem | github.com/daystar7777/agent-work-mem | ✅ 存在 |
| session-orchestrator | github.com/Kanevry/session-orchestrator | ✅ 存在 |
| Pi session 格式 | github.com/schovest/pi (packages/coding-agent/docs/session-format.md) | ✅ JSONL + id/parentId 树，v1–v3 |
| Hermes session 存储 | github.com/NousResearch/hermes-agent (docs/developer-guide/session-storage.md) | ✅ SQLite WAL + FTS5 + lineage，schema v23 |
| Claude SessionStore | Claude Agent SDK 文档 | ✅ 官方 External Session Storage（S3/Redis/DB） |

## 附录 B：Canonical Session Schema（草案 v0.1，节选）

```jsonc
// events.jsonl 每行的事件信封约束（JSON Schema 节选）
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "canonical-session-event",
  "type": "object",
  "required": ["seq", "ts", "agent", "type", "payload"],
  "properties": {
    "seq":        { "type": "integer", "minimum": 0 },
    "ts":         { "type": "number" },
    "agent":      { "type": "string", "enum": ["claude","codex","pi","hermes","opencode","cursor","gemini","aider","other"] },
    "actor":      { "type": "string", "examples": ["user", "agent:claude", "system"] },
    "type":       { "type": "string", "pattern": "^[a-z]+\\.[a-z]+$" },
    "level":      { "type": "integer", "enum": [0, 1, 2] },
    "payload":    { "type": "object" },
    "refs":       { "type": "array", "items": { "type": "string" } },
    "parent_seq": { "type": "integer" },
    "origin": {
      "type": "object",
      "properties": {
        "agent":      { "type": "string" },
        "native_id":  { "type": "string" },
        "native_seq": { "type": "integer" }
      }
    },
    "checksum":   { "type": "string", "pattern": "^sha256:[a-f0-9]{64}$" }
  },
  "additionalProperties": true   // 前向兼容：未知字段保留
}
```

```jsonc
// 关键事件 payload 示例：file.edit（L1）
{
  "seq": 88, "ts": 1787022780.1, "agent": "claude",
  "type": "file.edit", "level": 1,
  "payload": {
    "path": "src/auth/session_identity.rs",
    "diff": "@@ -12,7 +12,7 @@ ...",          // unified diff（截断策略见 5.4）
    "before_digest": "sha256:aa..", "after_digest": "sha256:bb..",
    "summary": "添加 session URI 解析函数"
  },
  "refs": ["file:src/auth/session_identity.rs@bb.."],
  "parent_seq": 87,
  "origin": { "agent": "claude", "native_id": "toolu_01x", "native_seq": 90 }
}
```
