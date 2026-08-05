# 07 · 实战 3：多 Agent 协作（Orchestrator 模式）

> 本节演示 A2A 的"**杀手级场景**"：一个 Orchestrator Agent 通过 A2A 同时调度多个**独立部署**的子 Agent，每个子 Agent 专注一件事。

## 7.1 场景设计

```
┌──────────────┐    A2A     ┌──────────────┐
│ Orchestrator │ ─────────▶ │ Flight Agent │
│  (11000)     │            │   (11001)    │
│              │            └──────────────┘
│              │    A2A     ┌──────────────┐
│              │ ─────────▶ │  Hotel Agent │
│              │            │   (11002)    │
└──────┬───────┘            └──────────────┘
       │
       │ SSE 流式返回给最终用户
       ▼
   "📋 Your trip summary:
    ✈️  Flight: IcelandAir...
    🏨  Hotel Borg..."
```

- **Orchestrator**：负责"调度 + 汇总"。它自己不查机票、不查酒店，而是**通过 A2A 委派**给专业 Agent。
- **Flight Agent**：返回机票信息。
- **Hotel Agent**：返回酒店信息。
- **三方完全独立部署**，各自的 Agent Card、各自的业务逻辑。

## 7.2 文件结构

```
a2a/examples/
├── 03_multi_agent_orchestrator.py     # 同时启动 Orchestrator + 2 子 Agent
├── 03_multi_agent_client.py           # 客户端（只跟 Orchestrator 对话）
```

> 把 3 个服务塞进一个文件是为了演示方便。**真实生产**当然分开部署、独立扩展。

## 7.3 子 Agent 的实现模式

Flight Agent 的 `message/send` 处理逻辑非常简单：

```python
async def flight_rpc(request: Request):
    body = await request.json()
    text = text_of(body["params"]["message"])

    if "beijing" in text.lower() or "pek" in text.lower():
        flight_info = "Flight: IcelandAir FI552, PEK->KEF, ¥6800 round-trip, direct"
    else:
        flight_info = "Flight: IcelandAir FI552, Shanghai->KEF (via Helsinki), ¥8200 round-trip"

    task = {
        "kind": "task",
        "id": str(uuid.uuid4()),
        "contextId": str(uuid.uuid4()),
        "status": {"state": "TASK_STATE_COMPLETED", ...},
        "artifacts": [{
            "artifactId": str(uuid.uuid4()),
            "name": "flight",
            "parts": [{"kind": "text", "text": flight_info}],
        }],
        "history": [],
    }
    return JSONResponse({"jsonrpc": "2.0", "id": ..., "result": task})
```

**关键观察**：

- 子 Agent 看不到"调用方是谁"，只看到**一个 message**。
- 子 Agent 不知道 Orchestrator 内部在做什么——它只是回答问题。
- 子 Agent 的 taskId / contextId **与 Orchestrator 完全无关**——它们是各自独立的 Task。

## 7.4 Orchestrator 的核心：并行调度

```python
async def orch_logic(task: dict, user_text: str):
    task_id = task["id"]
    context_id = task["contextId"]

    # 1) 阶段 1: 发现
    yield ("status_update", {
        "kind": "status-update", "taskId": task_id, "contextId": context_id,
        "status": {"state": "TASK_STATE_WORKING",
                   "message": make_agent_msg("🔍 Discovering sub-agents..."),
                   "timestamp": now_iso()},
    })

    flight_url = f"http://127.0.0.1:{FLIGHT_PORT}"
    hotel_url  = f"http://127.0.0.1:{HOTEL_PORT}"

    async with httpx.AsyncClient() as client:
        # 验证 Agent Card
        await client.get(f"{flight_url}/.well-known/agent-card.json")
        await client.get(f"{hotel_url}/.well-known/agent-card.json")

    # 2) 阶段 2: 并行调用
    yield ("status_update", {
        "kind": "status-update", "taskId": task_id, "contextId": context_id,
        "status": {"state": "TASK_STATE_WORKING",
                   "message": make_agent_msg("✈️  Booking flight + 🏨  finding hotel in parallel..."),
                   "timestamp": now_iso()},
    })

    async with httpx.AsyncClient() as client:
        flight_task, hotel_task = await asyncio.gather(
            call_subagent(client, flight_url, "message/send",
                          {"message": {"messageId": str(uuid.uuid4()), "role": "ROLE_USER",
                                       "parts": [{"kind": "text", "text": user_text}]}}),
            call_subagent(client, hotel_url, "message/send",
                          {"message": {"messageId": str(uuid.uuid4()), "role": "ROLE_USER",
                                       "parts": [{"kind": "text", "text": user_text}]}}),
        )

    flight_text = flight_task["artifacts"][0]["parts"][0]["text"]
    hotel_text  = hotel_task["artifacts"][0]["parts"][0]["text"]

    # 3) 阶段 3: 流式输出汇总
    summary_chunks = [
        f"📋 Your trip summary:\n",
        f"\n✈️  {flight_text}\n",
        f"\n🏨  {hotel_text}\n",
        f"\n💰  Estimated total: ~¥{6800 + 7*2200} (flight + 7 nights)\n",
        f"\n🎉  Have a great trip!",
    ]

    artifact_id = str(uuid.uuid4())
    for i, chunk in enumerate(summary_chunks, 1):
        await asyncio.sleep(0.4)
        yield ("artifact_update", {
            "kind": "artifact-update", "taskId": task_id, "contextId": context_id,
            "artifact": {"artifactId": artifact_id, "name": "summary",
                         "parts": [{"kind": "text", "text": chunk}]},
            "append": i > 1,
            "lastChunk": i == len(summary_chunks),
        })

    yield ("status_update", {
        "kind": "status-update", "taskId": task_id, "contextId": context_id,
        "status": {"state": "TASK_STATE_COMPLETED",
                   "message": make_agent_msg("Done!"),
                   "timestamp": now_iso()},
        "final": True,
    })
```

### 7.4.1 关键模式：并行 A2A 调用

```python
flight_task, hotel_task = await asyncio.gather(
    call_subagent(client, flight_url, "message/send", {...}),
    call_subagent(client, hotel_url,  "message/send", {...}),
)
```

**`asyncio.gather` 是并行调度多 Agent 的核心**。两个子 Agent 互不依赖，串行调用浪费时间。

> **性能对比**：串行调用 flight + hotel 如果各 500ms，并行只要 500ms；串行要 1 秒。

### 7.4.2 透传 User 原始意图

子 Agent 拿到的 message 是 **Orchestrator 透传的用户原话**（没有"加工"）：

```python
"message": {
    "messageId": str(uuid.uuid4()),
    "role": "ROLE_USER",        # ← 还是 ROLE_USER，不是 ROLE_AGENT
    "parts": [{"kind": "text", "text": user_text}],   # ← 原话
}
```

这一点很关键：**Orchestrator 不能篡改"用户的话"**——子 Agent 会根据原话判断意图。

### 7.4.3 透传与转发的区别

如果 Orchestrator 想**显式说明"我是代理人"**，可以加 metadata：

```python
"message": {
    "messageId": ...,
    "role": "ROLE_USER",
    "parts": [...],
    "metadata": {
        "delegatedBy": "orchestrator-agent-1",
        "originalUser": "user-uuid-123",
    },
}
```

子 Agent 可以选择读 / 不读。

## 7.5 客户端：只看 Orchestrator

```python
stream_orchestrator("Plan a 7-day Iceland trip, Beijing -> Reykjavik, 30000 CNY total budget")
```

预期输出：

```
📤 Sending to Orchestrator: 'Plan a 7-day Iceland trip, Beijing -> Reykjavik, 30000 CNY total budget'

   🔄 TASK_STATE_WORKING              🔍 Discovering sub-agents...
   🔄 TASK_STATE_WORKING              ✈️  Booking flight + 🏨  finding hotel in parallel...
   📝 chunk: '📋 Your trip summary:\n'
   📝 chunk: '\n✈️  Flight: IcelandAir FI552, PEK->KEF, ¥6800 round-trip, direct\n'
   📝 chunk: '\n🏨  Hotel Borg — 4-star, central Reykjavik, ¥3200/night\n'
   📝 chunk: '\n💰  Estimated total: ~¥22200 (flight + 7 nights)\n'
   📝 chunk: '\n🎉  Have a great trip!'
   🔄 TASK_STATE_COMPLETED            Done!
   🏁 done

🗺️  Full summary:
📋 Your trip summary:

✈️  Flight: IcelandAir FI552, PEK->KEF, ¥6800 round-trip, direct

🏨  Hotel Borg — 4-star, central Reykjavik, ¥3200/night

💰  Estimated total: ~¥22200 (flight + 7 nights)

🎉  Have a great trip!
```

**客户端完全不知道背后有 2 个子 Agent**——它只看到一个 Orchestrator。这就是 A2A 抽象的力量：**对调用方透明的分层**。

## 7.6 完整代码

- `a2a/examples/03_multi_agent_orchestrator.py`
- `a2a/examples/03_multi_agent_client.py`

也可以通过 GitHub 直接浏览：[`examples/03_multi_agent_orchestrator.py`](https://github.com/Sphinxes0o0/notes/blob/main/a2a/examples/03_multi_agent_orchestrator.py)。

## 7.7 跑起来

```bash
# Terminal 1：启动 Orchestrator + 2 个子 Agent
cd a2a/examples
python 03_multi_agent_orchestrator.py

# Terminal 2：客户端
cd a2a/examples
python 03_multi_agent_client.py
```

终端 1 会看到：

```
🚀 Orchestrator  → http://127.0.0.1:11000
🚀 Flight Agent  → http://127.0.0.1:11001
🚀 Hotel Agent   → http://127.0.0.1:11002
```

## 7.8 关键学习点

| 学到什么 | 对应协议细节 |
|--|--|
| Orchestrator 通过 A2A 调度子 Agent | A2A 的"横向协作" |
| 用 `asyncio.gather` 并行调用 | Python 异步并发 |
| 子 Agent 完全独立，对 Orchestrator 透明 | "opaque executor" 设计 |
| 用户原话透传 `role=USER` | role 语义 |
| 流式 artifact 拼接最终汇总 | 流式 artifact 设计 |
| 客户端只看 Orchestrator，不知道子 Agent | 调用方透明 |

## 7.9 进阶模式

### 7.9.1 链式调用（A → B → C）

```
Planner → Researcher → Summarizer
```

每一步把上一步的产物当输入。用普通 `await` 串行即可。

### 7.9.2 失败重试 + 熔断

```python
async def call_subagent_with_retry(url, params, retries=3):
    for attempt in range(retries):
        try:
            return await call_subagent(url, "message/send", params)
        except Exception as e:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(0.5 * (2 ** attempt))  # 指数退避
```

### 7.9.3 Skill 注册表

实际生产不会硬编码子 Agent URL，而是有一个**注册表**（etcd / Consul / 简单 DB）：

```python
async def discover_agents(skill: str) -> list[str]:
    """根据 skill 找 Agent URL 列表。"""
    # 实际：从注册表 / DNS-SRV / etcd 拉
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{REGISTRY_URL}/agents?skill={skill}")
        return r.json()["urls"]
```

### 7.9.4 子 Agent 之间的并行 + 优先级

```python
# 关键路径先跑
flight_task = asyncio.create_task(call_flight(...))

# 后台预热
weather_task = asyncio.create_task(call_weather(...))   # 不在关键路径

flight = await flight_task

# 流式边出 flight 边等 weather
async for chunk in stream_flight(flight):
    yield chunk

if not weather_task.done():
    yield "🔄 fetching weather in background..."
weather = await weather_task
```

## 7.10 真实世界会复杂在哪里

| 真实场景 | 复杂度来源 |
|--|--|
| **跨语言 Agent** | Orchestrator 是 Python，子 Agent 是 Go/Java；A2A 帮你抹平语言差异 |
| **跨组织 Agent** | 子 Agent 是第三方提供的，需要鉴权、限流、合同 |
| **长时间任务** | 不能用 blocking，要用 push notification 或流式 |
| **LLM 决策调用谁** | Orchestrator 不再硬编码 URL，而是 LLM 读 Agent Card 决定调哪个 |
| **错误恢复** | 子 Agent 失败时，Orchestrator 要重试或 fallback 到另一个 Agent |

---

## 8 总结：到这一步你掌握了什么

走完 7 节内容，你应该已经能够：

| 维度 | 掌握 |
|--|--|
| **概念** | Agent Card、Task、Message、Part、Artifact、Context 的语义 |
| **协议** | JSON-RPC 2.0、SSE 流式、Push Notification、错误码 |
| **安全** | TLS / JWT / OAuth2 / mTLS / Skill 级授权 |
| **实战** | 写 3 个能跑的 A2A Server + Client |
| **架构** | 单 Agent、流式 + 多轮、Orchestrator 多 Agent 协作 |

## 9 接下来可以做什么

1. **集成真实 LLM**：把 `execute_logic` 换成 OpenAI / Anthropic / Gemini 调用。
2. **接 MCP**：让子 Agent 通过 MCP 拿真实机票 API（携程、Skyscanner）。
3. **生产化**：加 JWT 鉴权、用 Postgres 存 Task、用 OpenTelemetry 打 trace。
4. **跨语言**：用 Go / Rust 写一个 Agent Server，用 Python 写 Client，验证协议互操作。
5. **多模态**：用 `Part.kind=raw` 上传 PDF，让 Agent 解析。

> **A2A 的力量不在协议本身，而在它让"智能体经济"成为可能**——每个团队可以专注做一件事做得最好，然后通过 A2A 把大家的能力拼起来。