---
title: Hermes Agent Memory 系统设计 + 最佳实践
date: 2026-06-04 10:00:00
tags:
    - hermes
    - agent
    - memory
    - design
    - best-practices
    - llm-context
---

# Hermes Agent Memory 系统设计 + 最佳实践

> 来源: `~/.hermes/hermes-agent/` 源码 + skill 文档确认 (2026-06-04)
> 范围: 内置 file-backed memory (MEMORY.md / USER.md) — 排除外部 provider 插件

## 1. 背景

LLM agent 跨 session 持久化信息有 3 个经典痛点:

1. **上下文窗口有限** — 每次 turn 都把全 memory 注入 system prompt, 越涨越慢越贵
2. **Prefix cache 失效** — 改动 memory 会让 system prompt 变化, 上游 LLM 端 KV cache 全部失效
3. **数据丢失风险** — 多个 session 同时写, race condition; 第三方工具 (patch / shell append) 改文件后工具不知情

Hermes 设计的 memory 系统**正面解决全部 3 个**。

## 2. 架构总览

```
┌─────────────────────────────────────────────────┐
│  MEMORY.md  (agent 笔记, 默认 2200 char)         │
│  USER.md   (用户画像, 默认 1375 char)             │
│  ~/.hermes/memories/ 路径                        │
└─────────────────────────────────────────────────┘
           ↓ load_from_disk()
┌─────────────────────────────────────────────────┐
│  MemoryStore 实例 (per AIAgent)                   │
│  ├─ memory_entries / user_entries  (live state) │
│  └─ _system_prompt_snapshot  (frozen, 不可变)   │
└─────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────┐
│  format_for_system_prompt()  → 注入 system prompt │
│  volatile tier (per turn rebuild, 不缓存)         │
└─────────────────────────────────────────────────┘
```

**两种状态分离**:
- **live state**: 工具调用 mutate, disk 立即持久化
- **frozen snapshot**: load_from_disk 时拍, 整个 session 不变 → **prefix cache 稳定**

## 3. 核心机制

### 3.1 Bounded Char Limit (非 token)

```python
class MemoryStore:
    def __init__(self, memory_char_limit=2200, user_char_limit=1375):
```

- `memory_char_limit`: 2200 chars (~700-900 tokens, model 无关)
- `user_char_limit`: 1375 chars (~450-600 tokens)
- 超 limit 拒绝 add / replace, 提示先 remove

**为什么 char 而非 token**:
> "Character limits (not tokens) because char counts are model-independent." — `tools/memory_tool.py` 注释

不同模型 (Claude / GPT / DeepSeek) token 化策略不同, char 是**唯一稳定单位**。

### 3.2 § 分隔符 (Entry Delimiter)

```python
ENTRY_DELIMITER = "\n§\n"
```

多个 entry 用 `§` 隔开, **multiline entry** 允许 (单条 entry 可含换行, 内部不限制)。

文件格式示例:

```markdown
第一条 entry 内容
可以是多行

§

第二条 entry
也是多行

§

第三条
```

**为什么 § 而不是普通 --- / ```**: § 在英文 + 中文 + 代码片段中**几乎不出现**, 分割无歧义。

### 3.3 Frozen Snapshot 模式 (Prefix Cache 关键)

```python
def load_from_disk(self):
    # 1. 读 disk
    self.memory_entries = self._read_file(...)
    # 2. 拍 snapshot
    self._system_prompt_snapshot["memory"] = self._render_block(
        "memory", sanitized_entries
    )
```

```python
def format_for_system_prompt(self, target):
    # 永远返回 snapshot, 不返回 live state
    return self._system_prompt_snapshot.get(target, "")
```

**为什么重要**:
- 假设 turn 1 写了一条 memory entry 到 disk
- 之后 turn 2/3/4 的 system prompt **完全不变** (live entry 增加但 snapshot 不变)
- LLM 端 prefix KV cache 命中 → 3x-10x 成本 + 延迟下降

### 3.4 File Lock + Atomic Rename (并发安全)

```python
# 读改写: 文件锁
@contextmanager
def _file_lock(path):
    fcntl.flock(fd, fcntl.LOCK_EX)  # POSIX
    # Windows fallback: msvcrt.locking

# 写: temp + fsync + rename
def _write_file(path, entries):
    fd, tmp_path = tempfile.mkstemp(...)
    f.write(content)
    f.flush()
    os.fsync(f.fileno())
    atomic_replace(tmp_path, path)  # 原子 rename
```

**两层保护**:
- `flock`: 防止两个 session 同时改一个文件
- `atomic_replace`: 防止 truncate 窗口 (用 `open("w")` 时读者看到空文件)

### 3.5 External Drift Detection (数据丢失防护)

```python
def _detect_external_drift(self, target):
    raw = path.read_text()
    parsed = raw.split(ENTRY_DELIMITER)
    roundtrip = ENTRY_DELIMITER.join(parsed)
    max_entry = max(len(e) for e in parsed)
    drift = (raw != roundtrip) or (max_entry > char_limit)
    if drift:
        # 备份成 .bak.&lt;ts&gt;, 拒绝 mutation
        bak = path.with_suffix(f".bak.{int(time.time())}")
        bak.write_text(raw)
        return str(bak)
```

**触发场景**: 用户用 `patch` / `vi` / `cat >>` 工具手动改 memory 文件, 添加了大段 free-form 内容 (格式不对)。Memory 工具若直接覆写会**丢数据** (issue #26045)。

**正确处理**:
- 拍 `.bak.&lt;ts&gt;` 快照保留原内容
- 拒绝此次 mutation
- 提示用户: 整合新内容用 `memory(action=add, ...)` 一条条加, 然后重写原文件为 §-delimited 格式

### 3.6 Threat-Pattern Sanitization (Supply Chain 防御)

```python
def _sanitize_entries_for_snapshot(self, entries, filename):
    for entry in entries:
        if scan_for_threats(entry, scope="strict"):
            sanitized.append(
                f"[BLOCKED: {filename} entry contained threat pattern(s): ...]"
            )
        else:
            sanitized.append(entry)
```

**关键设计**: **原始 entry 仍在 live state**, 用户可读 + remove:

> "Silently dropping them would hide the attack from the user."

**两层防御**:
- 写入时: `_scan_memory_content` 拒绝威胁内容
- 读 snapshot 时: 即便 disk 已被篡改, 快照用 `[BLOCKED]` 占位, LLM 不会读到攻击内容

## 4. 工具 API (Memory Tool Schema)

```yaml
name: memory
description: |
  Save durable information to persistent memory that survives across sessions.
  Memory is injected into future turns, so keep it compact and focused.
  
  WHEN TO SAVE (proactive, 不等用户要求):
  - User corrects you or says 'remember this' / 'don't do that again'
  - User shares a preference, habit, or personal detail
  - You discover something about the environment
  - You learn a convention, API quirk, or workflow
  - You identify a stable fact that will be useful again
  
  PRIORITY: User preferences and corrections > environment facts > procedural knowledge
  
  DO NOT SAVE:
  - task progress, session outcomes (use session_search)
  - temporary TODO state
  - trivial info / easily re-discoverable
  - raw data dumps

actions:
  - add     # new entry
  - replace # update existing (old_text identifies it)
  - remove  # delete (old_text identifies it)
targets:
  - memory  # agent's personal notes
  - user    # user profile
```

## 5. 最佳实践 (Karpathy 4 原则视角)

### 5.1 Think Before Coding — 加 memory 前判断

- 是不是**用户偏好 / 纠正**? — Yes → 必加
- 是不是**环境事实**? — Yes → 加
- 是不是**任务进度 / 临时状态**? — Yes → 不用 memory, 用 `session_search` / `todo` 工具
- 是不是**可复用方法**? — Yes → 用 `skill` 工具保存, 不进 memory
- 是不是**trivial / 易重新发现**? — Yes → 跳过

### 5.2 Simplicity First — 紧凑优先

- 一条 entry 一个事实, 最多 1-2 句
- 不用 markdown 标题/列表 (除非确实需要)
- 不存示例代码 (wiki / skill)
- 满了**先 remove 旧的**, 不堆叠

### 5.3 Surgical Changes — replace 改最小

- `replace` 用**唯一短 substring** 定位, 不写全 entry
- 一次只改一个事实, 不批量改
- 改完 verify (`memory(action=read)`)

### 5.4 Goal-Driven Execution — 验证闭环

- add 后跑 `read` 确认
- 写满 90% 立即 review (避免 add 失败)
- 跨 session 验证: 重启 session, 检查 memory 是否真注入

## 6. 典型用法 (基于源码 schema)

```python
# 加一条
memory_tool(action="add", target="user", content="User works at NIO, focuses on IDPS/NIDS")

# 改一条 (old_text 唯一短 substring)
memory_tool(action="replace", target="user",
    old_text="NIO", new_content="NIO (蔚来汽车)")

# 删一条
memory_tool(action="remove", target="user", old_text="NIO (蔚来汽车)")

# 读全部
memory_tool(action="read", target="memory")
```

## 7. 限制与失败模式

| 情况 | 行为 | 应对 |
|---|---|---|
| 超 char limit | 拒绝 add/replace | 先 `remove` 旧 entry, 再 `add` |
| 重复内容 | 拒绝 add (不存 duplicate) | 检查已有 entry |
| Drift 检出 | 拒绝 mutation, 备份 .bak.&lt;ts&gt; | 修复文件, 重试 |
| Threat pattern | 写入时拒绝 / snapshot 时 [BLOCKED] | 检查 entry 内容 |
| 文件 lock 失败 | 等待 + 重试 (flock 默认阻塞) | 检查其他 session |
| mid-session 改动不生效 | 正常, snapshot 不会变 | 下个 session 生效 |
| 多个 session 同时改 | 第二个 session 读最新 disk 内容, 不覆盖 | flock 保证原子 |

## 8. 外部 Memory Provider (补充)

`agent/memory_manager.py` 提供了 **可插拔外部 provider** 架构:

| Provider | 用途 |
|---|---|
| byterover | byte-level 检索 |
| hindsight | 事件回溯 |
| holographic | 全息编码 |
| honcho | 第三方服务 |
| mem0 | 用户级 memory |
| openviking | 跨 session 知识图谱 |
| retaindb | retention-policy 持久化 |
| supermemory | super-memory 综合 |

**限制**: 一次只允许 1 个 external provider, 防止 schema bloat 和 backend 冲突。

**何时用外部**:
- 内置 2200/1375 char 不够
- 需要 cross-session knowledge graph
- 需要 semantic search over history
- 需要 retention policies

**何时用内置**:
- 用户偏好 / 简单事实
- 跨 session 一致性要求高
- 无网络依赖

## 9. 设计哲学总结

1. **Bounded, not unbounded** — char limit 强制选择
2. **Frozen snapshot, live state** — 分离保证 prefix cache
3. **File-backed, atomic** — durable + 简单 backup
4. **Threat-aware** — snapshot scan 防 supply chain 攻击
5. **Drift-detection** — 不假设文件是工具写的
6. **Pluggable provider** — 不绑定单一后端

## 10. 引用

- 源码: `~/.hermes/hermes-agent/tools/memory_tool.py` (723 行)
- 注入: `~/.hermes/hermes-agent/agent/system_prompt.py:305`
- Manager: `~/.hermes/hermes-agent/agent/memory_manager.py` (653 行)
- 插件: `~/.hermes/hermes-agent/plugins/memory/{byterover, hindsight, honcho, mem0, ...}/`
- Skill 文档: `~/.hermes/skills/autonomous-ai-agents/hermes-agent/SKILL.md`
- Hermes docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
