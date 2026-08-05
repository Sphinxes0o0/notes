# 06 · 实战 2：流式响应 + 多轮对话

> 这一节把 Hello World 升级成"真实场景"：服务端用 **SSE 流式**响应，客户端**多次往返**触发 `input-required` 状态，最终拿到流式生成的完整行程。

## 6.1 场景设计

我们做一个"**旅行规划助手**"：

```
T1: User  ── "plan my trip"     ──▶ Agent
T1: Agent ◀── "which month?"     ── (state=input-required)

T2: User  ── "next June"        ──▶ Agent
T2: Agent ◀── "rough budget?"    ── (state=input-required)

T3: User  ── "30000 CNY"        ──▶ Agent
T3: Agent ◀── (streaming...)
              status: working
              artifact: "Day 1: Reykjavik arrival"
              artifact: "Day 2: Golden Circle"
              ...
              artifact: "Day 7: Return"
              status: completed
```

3 个 A2A 关键能力在这次实战里都会被演示：

| 能力 | 演示位置 |
|--|--|
| **SSE 流式响应** | T3 的 artifact 一块一块推 |
| **`input-required` 状态** | T1, T2 |
| **多轮对话（contextId）** | T2/T3 都带前一轮的 taskId/contextId |

## 6.2 文件结构

```
a2a/examples/
├── 02_streaming_server.py    # 服务端（流式 + 多轮）
├── 02_streaming_client.py    # 客户端（解析 SSE）
```

## 6.3 服务端架构

### 6.3.1 Agent Card 加 `streaming: True`

```python
"capabilities": {
    "streaming": True,   # ← 关键
    ...
}
```

不声明 streaming 就实现 SSE 流式，客户端应该拒绝调用。

### 6.3.2 业务状态机

我们把"问什么"做成一个简单的状态机：

```python
# metadata._state: new → asked_month → asked_budget → producing → done

async def advance(user_text: str, task: dict) -> str:
    md = task.setdefault("metadata", {})
    state = md.get("_state", "new")

    if state == "new":
        md["_state"] = "asked_month"
        return "ask:which month?"

    if state == "asked_month":
        md["_month"] = user_text
        md["_state"] = "asked_budget"
        return "ask:rough budget?"

    if state == "asked_budget":
        md["_budget"] = user_text
        md["_state"] = "producing"
        return "produce"

    return "done"
```

> 把"对话进度"存在 `task.metadata` 是个常用技巧：服务端**不需要单独的 session store**，因为整个对话都在 Task 里。

### 6.3.3 流式生成器：核心中的核心

```python
async def stream_logic(task: dict, user_text: str):
    """这是 A2A streaming 的标准模式：一个 async generator。"""
    task_id = task["id"]
    context_id = task["contextId"]

    decision = await advance(user_text, task)

    if decision.startswith("ask:"):
        # input-required: 流结束（不 final=True），客户端需要再发请求
        question = decision.split(":", 1)[1]
        task["status"] = {
            "state": "TASK_STATE_INPUT_REQUIRED",
            "message": make_agent_msg(question),
            "timestamp": now_iso(),
        }
        yield ("status_update", {
            "kind": "status-update",
            "taskId": task_id, "contextId": context_id,
            "status": task["status"],
            "final": True,        # ← 流结束
        })
        return

    if decision == "produce":
        # 1) 状态切到 working
        task["status"] = {
            "state": "TASK_STATE_WORKING",
            "message": make_agent_msg(f"Planning your {task['metadata']['_month']} trip..."),
            "timestamp": now_iso(),
        }
        yield ("status_update", {
            "kind": "status-update",
            "taskId": task_id, "contextId": context_id,
            "status": task["status"],
        })

        # 2) 边生成边产出 artifact（每 Day 一块）
        artifact_id = str(uuid.uuid4())
        for i, day in enumerate(DAYS, 1):
            await asyncio.sleep(0.3)  # 模拟 LLM 慢慢生成
            yield ("artifact_update", {
                "kind": "artifact-update",
                "taskId": task_id, "contextId": context_id,
                "artifact": {
                    "artifactId": artifact_id,
                    "name": "itinerary",
                    "parts": [{"kind": "text", "text": f"Day {i}: {day}"}],
                },
                "append": i > 1,           # ← 第一块不带 append，后续带
                "lastChunk": i == len(DAYS),
            })

        # 3) 终态
        task["status"] = {
            "state": "TASK_STATE_COMPLETED",
            "message": make_agent_msg("Have a great trip!"),
            "timestamp": now_iso(),
        }
        yield ("status_update", {
            "kind": "status-update",
            "taskId": task_id, "contextId": context_id,
            "status": task["status"],
            "final": True,
        })
```

**重要细节**：

1. **`yield` 出去的是 Python 对象**，由 HTTP 层负责包装成 SSE wire 格式。
2. **`final: True` 是"这个流结束了"信号**——客户端读到这一帧就停止解析。
3. **`input-required` 也用 `final: True`**，因为这一轮确实结束了，需要等用户下一条消息。
4. **artifact 用同一个 `artifactId` + `append=True`** 让客户端知道"拼起来"。

### 6.3.4 HTTP 入口：`StreamingResponse`

```python
async def event_gen():
    # 第一帧：发一个 task 快照
    yield sse_pack({"jsonrpc": "2.0", "id": rid, "result": {**task}})

    # 后续帧：业务流
    async for kind, payload in stream_logic(task, user_text):
        yield sse_pack({"jsonrpc": "2.0", "id": rid, "result": payload})

return StreamingResponse(event_gen(), media_type="text/event-stream")
```

`StreamingResponse` 是 Starlette 的标准模式——把一个 async generator 当成 SSE 用。`sse_pack` 只是把 JSON 包成 `data: ...\n\n` 格式。

> ⚠️ **响应体仍然是 JSON-RPC envelope**：每个 SSE event 内部都是完整的 `{"jsonrpc":"2.0","id":..., "result":...}`。这是 v1.0 的统一格式（之前是裸 JSON），让请求/响应在 wire 上对称。

## 6.4 客户端架构

### 6.4.1 流式接收

```python
with httpx.stream("POST", f"{BASE}/a2a", json=payload, timeout=30) as resp:
    for line in resp.iter_lines():
        if not line.startswith("data:"):
            continue
        data = json.loads(line[len("data:"):].strip())
        result = data["result"]
        kind = result["kind"]

        if kind == "status-update":
            state = result["status"]["state"]
            msg   = result["status"].get("message", {}).get("parts", [{}])[0].get("text", "")
            print(f"   🔄 {state}  ({msg!r})")
            if result.get("final"):
                print(f"   🏁 stream finished")
                break
        elif kind == "artifact-update":
            art = result["artifact"]
            aid = art["artifactId"]
            txt = art["parts"][0]["text"]
            print(f"   📝 chunk[{aid[:8]}]: {txt!r}")
```

关键点：

1. **`iter_lines()`** 按行读 SSE。每个 `data: ...` 占一行。
2. **`kind` 字段** 决定怎么处理这一帧。
3. **`final=True` 是流的退出信号**——读取立即停止。
4. **artifact 增量** 按 `artifactId` 分桶拼装。

### 6.4.2 多轮传 taskId + contextId

```python
payload = {
    "jsonrpc": "2.0",
    "method": "message/stream",
    "params": {
        "message": { ... },
        "taskId": previous_task_id,        # ← 第一轮的 id
        "contextId": previous_context_id,  # ← 第一轮的 id
    },
}
```

服务端会把这条消息**追加到 Task 的 history**，不创建新 Task。这让 Agent 能"想起来"前文。

## 6.5 完整代码

- `a2a/examples/02_streaming_server.py`
- `a2a/examples/02_streaming_client.py`

也可以通过 GitHub 直接浏览：[`examples/02_streaming_server.py`](https://github.com/Sphinxes0o0/notes/blob/main/a2a/examples/02_streaming_server.py)。

## 6.6 跑起来

```bash
# Terminal 1
cd a2a/examples
python 02_streaming_server.py

# Terminal 2
cd a2a/examples
python 02_streaming_client.py
```

预期输出（精简）：

```
🪪 Agent: Streaming Travel Agent
   streaming = True

📤 Sending: 'plan my trip'
   📋 initial task: id=d50d6710...
   🔄 status: TASK_STATE_INPUT_REQUIRED  ('which month?')
   🏁 stream finished

🔑 remembered: taskId=d50d6710, contextId=6bab424d

==================================================

📤 Sending: 'next June'
   📋 initial task: id=d50d6710...
   🔄 status: TASK_STATE_INPUT_REQUIRED  ('rough budget?')
   🏁 stream finished

==================================================

📤 Sending: '30000 CNY'
   📋 initial task: id=d50d6710...
   🔄 status: TASK_STATE_WORKING  ('Planning your next June trip with budget 30000 CNY...')
   📝 artifact chunk [f2f07f1a]: 'Day 1: Reykjavik arrival, Blue Lagoon'
   📝 artifact chunk [f2f07f1a]: 'Day 2: Golden Circle day tour'
   📝 artifact chunk [f2f07f1a]: 'Day 3: South Coast...'
   ...
   📝 artifact chunk [f2f07f1a]: 'Day 7: Return to Reykjavik, shopping'
   🔄 status: TASK_STATE_COMPLETED  ('Have a great trip!')
   🏁 stream finished

🗺️  Final itinerary:
Day 1: Reykjavik arrival, Blue LagoonDay 2: Golden Circle day tour...

✅ Demo complete!
```

注意几件事：

1. **`taskId` 和 `contextId` 跨 3 轮保持不变**——服务端追加 history，客户端携带 id。
2. **流在 `input-required` 时结束但不"完成"**——客户端必须再发一条。
3. **`completed` 才让流真正终结**。

## 6.7 关键学习点

| 学到什么 | 对应协议细节 |
|--|--|
| 流式响应通过 `StreamingResponse` + async generator 实现 | [03.4 SSE 节](03-protocol-deep-dive.md#34-流式响应sse) |
| `final: True` 是流的退出信号 | StreamResponse 协议 |
| `input-required` 状态让流暂停而不是结束 | [02.6 Task 状态机](02-core-concepts.md#26-task一次完整的委托) |
| artifact 增量用 `append + lastChunk` 拼接 | 流式 artifact 设计 |
| 多轮对话靠"客户端带回 taskId+contextId" | contextId 语义 |

## 6.8 进阶练习

### 练习 1：断线重连（`tasks/resubscribe`）

```python
async def tasks_resubscribe(self, task_id: str):
    """长任务流断掉后，调用此方法重新订阅。"""
    async with httpx.stream("GET", f"{BASE}/v1/tasks/{task_id}:resubscribe") as resp:
        # ... 从当前状态重新接收事件
```

服务端实现：

```python
async def resubscribe_endpoint(request):
    task_id = request.path_params["taskId"]
    task = TASKS.get(task_id)
    if not task:
        return JSONResponse({"error": "not found"}, status_code=404)
    async def gen():
        # 重新推当前快照 + 后续事件（如果有）
        yield sse_pack({"jsonrpc": "2.0", "id": "resub", "result": {**task}})
        # 实际场景：从队列/事件总线继续推
        ...
    return StreamingResponse(gen(), media_type="text/event-stream")
```

### 练习 2：Push Notification

```python
# 客户端：注册 webhook
await httpx.post(f"{BASE}/a2a", json={
    "jsonrpc": "2.0", "method": "tasks/pushNotificationConfig/set",
    "params": {
        "taskId": task_id,
        "config": {
            "url": "https://my-service.com/hook",
            "token": "my-secret-uuid",
            "authentication": {"schemes": ["Bearer"], "credentials": "..."},
        }
    }
})

# Agent 完成后会 POST 到你的 url，你可以在那里处理
```

### 练习 3：把同步 execute 改成真异步

把 `stream_logic` 里的 `await asyncio.sleep` 换成真 LLM 流式 API（如 OpenAI streaming），就能看到真实的 token-by-token 输出。

---

## 下一步

- [07 · 实战 3：多 Agent 协作](07-hands-on-multi-agent.md) — 在流式之上加一层 Orchestrator。