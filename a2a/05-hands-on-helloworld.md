# 05 · 实战 1：从零手写一个 Hello World A2A

> 本节用大约 200 行 Python，从空文件开始搭起一个 A2A 服务端 + 客户端。**不依赖**完整的 `a2a-sdk`，让我们看清协议本身。

## 5.1 我们要实现什么

```
                        ┌─────────────────────────┐
   GET /.well-known/   │  Hello World Agent       │
   agent-card.json     │  - name                  │
        ───────────▶   │  - skill: hello_world    │
                       │  - capabilities          │
                       └─────────────────────────┘
                                  ▲
                                  │ POST /a2a  (JSON-RPC)
                                  │ method=message/send
                                  ▼
                       ┌─────────────────────────┐
                       │  Client                  │
                       │  - 拉 Card                │
                       │  - 发 message             │
                       │  - 解析 Task              │
                       └─────────────────────────┘
```

跑通后能看到：

```
Agent Card: name="Hello World Agent", skills=["hello_world"]
Task {state: COMPLETED, artifacts: ["Hello, World!"]}
Task {state: COMPLETED, artifacts: ["Hello, World!", "Hello, Sphinx!"]}
```

## 5.2 准备环境

只需要三个最常见的 Python Web 库：

```bash
pip install starlette uvicorn httpx
```

> **为什么不用 `a2a-sdk`？** 教学目的。完整 SDK 帮你处理了很多事，但**协议细节就被掩盖了**。手写一次，再去用 SDK，你会知道每个 API 在做什么。

## 5.3 准备文件结构

```
a2a/examples/
├── 01_hello_server.py     # 服务端
├── 01_hello_client.py     # 客户端
```

## 5.4 服务端拆解（`01_hello_server.py`）

服务端做 4 件事：

1. **声明 Agent Card** — 一个常量字典。
2. **存 Task** — 内存字典。
3. **实现 `message/send`** — 业务逻辑（echo `"Hello, <input>!"`）。
4. **暴露 2 个 HTTP 端点** — agent-card.json 和 /a2a。

### 5.4.1 声明 Agent Card

```python
AGENT_CARD = {
    "name": "Hello World Agent",
    "description": "Just a hello world agent",
    "version": "1.0.0",
    "supportedInterfaces": [
        {
            "url": f"http://{HOST}:{PORT}",
            "protocolBinding": "JSONRPC",
            "protocolVersion": "1.0",
        }
    ],
    "capabilities": {
        "streaming": False,           # 我们不演示 SSE
        "pushNotifications": False,
        "extendedAgentCard": False,
        "stateTransitionHistory": True,
    },
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "skills": [
        {
            "id": "hello_world",
            "name": "Returns hello world",
            "description": "just returns hello world",
            "tags": ["hello", "demo"],
            "examples": ["hi", "hello world"],
            "inputModes": ["text/plain"],
            "outputModes": ["text/plain"],
        }
    ],
}
```

**对照 [02 节](02-core-concepts.md)**：这就是一份"标准 Agent Card"。

### 5.4.2 任务存储

```python
TASK_STORE: dict[str, dict] = {}
```

真实生产用 PostgreSQL / Redis；Demo 用内存 dict。

### 5.4.2.5 JSON-RPC 错误载体

```python
class JsonRpcError(Exception):
    """承载 JSON-RPC error payload 的自定义异常。"""
    def __init__(self, code: int, message: str, data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

    def to_payload(self) -> dict:
        err = {"code": self.code, "message": self.message}
        if self.data is not None:
            err["data"] = self.data
        return err
```

不用 `raise {...}` + `except dict as err` 是因为这两条**在 Python 里都不可运行**（前者 TypeError，后者 `dict` 不是 `BaseException` 子类，except 子句根本编译不过）。自定义异常是最干净的替代。

### 5.4.3 业务逻辑

```python
def execute_logic(user_text: str) -> str:
    cleaned = user_text.strip() or "World"
    return f"Hello, {cleaned}!"
```

这就是 Agent 的"心脏"——任何协议层代码都只是包裹它。真实 Agent 这里会调 LLM / MCP 工具 / 数据库。

### 5.4.4 核心 RPC：`message/send`

```python
async def handle_message_send(params: dict) -> dict:
    msg = params["message"]
    user_text = text_of(msg)

    # 决定 taskId / contextId：
    #   - follow-up：客户端回传了已分配的 taskId，服务端必须复用
    #   - 首轮：客户端**不能**自造 id，服务端总是自己生成
    client_task_id = params.get("taskId")
    existing = TASK_STORE.get(client_task_id) if client_task_id else None
    if existing:
        task_id    = existing["id"]
        context_id = existing["contextId"]
        task       = existing
    else:
        task_id    = str(uuid.uuid4())
        context_id = params.get("contextId") or str(uuid.uuid4())
        task = {
            "kind": "task",
            "id": task_id,
            "contextId": context_id,
            "status": {"state": "TASK_STATE_SUBMITTED", "timestamp": now_iso()},
            "artifacts": [],
            "history": [],
        }

    task["history"].append(msg)

    # 1) 转 working
    task["status"] = {
        "state": "TASK_STATE_WORKING",
        "message": make_agent_msg("Processing request..."),
        "timestamp": now_iso(),
    }

    # 2) 跑业务
    result_text = execute_logic(user_text)

    # 3) 产出 Artifact
    task["artifacts"].append({
        "artifactId": str(uuid.uuid4()),
        "name": "result",
        "parts": [{"kind": "text", "text": result_text}],
    })

    # 4) 完成
    task["status"] = {
        "state": "TASK_STATE_COMPLETED",
        "message": make_agent_msg("Done."),
        "timestamp": now_iso(),
    }
    task["history"].append(task["status"]["message"])

    TASK_STORE[task_id] = task
    return task
```

留意几处关键：

- **`taskId` / `contextId` 由服务端分配**：只有当客户端传回来的 `taskId` **已经在 TASK_STORE 里**（即 follow-up）时才复用；首轮请求里客户端即使塞了任何 `taskId`/`contextId` 也会被忽略，服务端重新生成。这是 v1.0 的标准模式——客户端永远不能自己造 id。
- **Task 是不可变快照**：每次都生成一个新的 status 对象，而不是 in-place 修改。
- **`history[]`** 记录了所有消息，便于客户端审计 / 续传。

### 5.4.5 HTTP 路由

```python
async def agent_card_endpoint(request):
    return JSONResponse(AGENT_CARD)

async def rpc_endpoint(request):
    body = await request.json()
    rid = body.get("id")
    method = body.get("method")
    params = body.get("params") or {}

    try:
        result = await dispatch(method, params)
        return JSONResponse({"jsonrpc": "2.0", "id": rid, "result": result})
    except JsonRpcError as e:
        return JSONResponse({"jsonrpc": "2.0", "id": rid, "error": e.to_payload()})
```

注意几个细节：

- **JSON-RPC 错误仍返回 HTTP 200**，错误信息放在 `error` 字段里（这是 JSON-RPC 2.0 规范）。
- **`JsonRpcError`** 是一个轻量自定义异常：让它承载 `code` / `message` / `data`，被 except 捕获后原样塞进 JSON-RPC `error`。比起直接 `raise {...}`（Python 里会 TypeError）和 `except dict as ...`（不是合法 except 子句），这是干净且可运行的做法。

### 5.4.6 启动

```python
app = Starlette(routes=[
    Route("/.well-known/agent-card.json", agent_card_endpoint),
    Route("/a2a", rpc_endpoint, methods=["POST"]),
])

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
```

## 5.5 客户端拆解（`01_hello_client.py`）

客户端做 3 步：

```python
# Step 1: 拿 Agent Card
card = httpx.get(f"{BASE}/.well-known/agent-card.json").json()

# Step 2: 发第一条消息
task1 = send_message(BASE, "World")
# → Task {state: COMPLETED, artifacts: ["Hello, World!"]}

# Step 3: 续写（带 taskId + contextId）
task2 = send_message_with_context(BASE, "Sphinx", task_id=task1["id"], context_id=task1["contextId"])
# → Task {state: COMPLETED, artifacts: ["Hello, World!", "Hello, Sphinx!"]}
```

### 关键：续写时要带 taskId 和 contextId

```python
payload = {
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
        "message": { ... },
        "taskId":    task1["id"],         # ← 用上一轮的 id
        "contextId": task1["contextId"],  # ← 用上一轮的 id
    },
}
```

服务端发现 `taskId` 已经存在，会把这次的消息追加到 history，不会创建新 Task。

## 5.6 完整代码

完整代码在仓库：

- `a2a/examples/01_hello_server.py`
- `a2a/examples/01_hello_client.py`

也可以通过 GitHub 直接浏览：[`examples/01_hello_server.py`](https://github.com/Sphinxes0o0/notes/blob/main/a2a/examples/01_hello_server.py)。

## 5.7 跑起来

```bash
# Terminal 1
cd a2a/examples
python 01_hello_server.py

# Terminal 2
cd a2a/examples
python 01_hello_client.py
```

预期输出：

```
🪪 Agent: Hello World Agent
   Skills: ['hello_world']

📤 Sending: 'World'

📦 Task received:
   id          = b4567ade-...
   contextId   = 69d625bb-...
   state       = TASK_STATE_COMPLETED
   artifacts   = 1
     └─     'result' → 'Hello, World!'

📤 Sending: 'Sphinx'

📦 Task received:
   id          = b4567ade-...     ← 同一个 Task
   state       = TASK_STATE_COMPLETED
   artifacts   = 2
     └─     'result' → 'Hello, World!'
     └─     'result' → 'Hello, Sphinx!'

✅ Done!
```

## 5.8 关键学习点回顾

| 学到什么 | 对应协议细节 |
|--|--|
| Agent Card 是 JSON 对象，存放在 well-known URI | RFC 8615 |
| 客户端 `GET /.well-known/agent-card.json` 即可发现能力 | 协议发现 |
| `taskId` / `contextId` 由服务端生成 | v1.0 关键变更 |
| JSON-RPC 错误仍返回 HTTP 200 | JSON-RPC 2.0 |
| Task 是不可变快照，每次新对象 | [02 节数据模型](02-core-concepts.md#24-agent-cardagent-的名片--菜单) |
| 多轮对话靠"客户端带回 taskId+contextId"实现 | contextId 设计 |

## 5.9 动手试试

把 `execute_logic` 换成别的，比如：

```python
def execute_logic(user_text: str) -> str:
    # 反转字符串
    return user_text[::-1]

def execute_logic(user_text: str) -> str:
    # 假装调 LLM（实际同步）
    return f"As an AI, I think you said: '{user_text}'"
```

或者把 capabilities 改成 `"streaming": True`，然后试着自己实现 `message/stream`（提示：用 `StreamingResponse` 返回 SSE）。

---

## 下一步

- [06 · 实战 2：流式 + 多轮对话](06-hands-on-streaming.md) — 加上 SSE 流式和 `input-required` 状态。
- [07 · 实战 3：多 Agent 协作](07-hands-on-multi-agent.md) — Orchestrator 调度多个子 Agent。