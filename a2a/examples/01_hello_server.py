"""
A2A Hello World — Server
========================

最小可运行的 A2A Server，对应文档：05 · 实战 1：Hello World

特性：
  - 自包含：仅依赖 starlette + uvicorn（都是 a2a-sdk 的传递依赖）
  - 不依赖完整 a2a-sdk：手写 JSON-RPC + Agent Card，演示协议本质
  - 支持 message/send（同步）

运行：
  pip install starlette uvicorn
  python 01_hello_server.py

接口：
  GET  /.well-known/agent-card.json   —— 拿 Agent Card
  POST /a2a                          —— JSON-RPC 入口
"""

import json
import uuid
import time
from datetime import datetime, timezone

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route, Mount
import uvicorn

HOST = "127.0.0.1"
PORT = 9999


# ----------------------------------------------------------------------------
# 0. JSON-RPC 错误载体
# ----------------------------------------------------------------------------
class JsonRpcError(Exception):
    """承载 JSON-RPC error payload 的自定义异常。

    用 raise 而不是 dict —— 因为 `raise { ... }` 在 Python 里是 TypeError，
    `except dict` 也不是合法语法。专门的异常类既能被 except 捕获，
    又能干净地把 code/message/data 传给 rpc_endpoint。
    """

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

# ----------------------------------------------------------------------------
# 1. Agent Card
# ----------------------------------------------------------------------------
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
        "streaming": False,
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
            "examples": ["hi", "hello world", "say hello"],
            "inputModes": ["text/plain"],
            "outputModes": ["text/plain"],
        }
    ],
}


# ----------------------------------------------------------------------------
# 2. 任务存储（in-memory）
# ----------------------------------------------------------------------------
TASK_STORE: dict[str, dict] = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def get_input_text(message: dict) -> str:
    """从 message.parts[] 里把第一个 text 抠出来。"""
    for part in message.get("parts", []):
        if part.get("kind") == "text":
            return part.get("text", "")
    return ""


def execute_logic(user_text: str) -> str:
    """真正的业务逻辑：把用户输入 echo 成 'Hello, <text>!'"""
    cleaned = user_text.strip() or "World"
    return f"Hello, {cleaned}!"


# ----------------------------------------------------------------------------
# 3. JSON-RPC 方法
# ----------------------------------------------------------------------------
def make_message(role: str, text: str, **extra) -> dict:
    return {
        "messageId": str(uuid.uuid4()),
        "role": role,
        "parts": [{"kind": "text", "text": text}],
        **extra,
    }


async def handle_message_send(params: dict) -> dict:
    """实现 message/send。返回 Task 对象（同步模式）。"""
    msg = params["message"]
    user_text = get_input_text(msg)

    # 决定 taskId / contextId：
    #   - follow-up：客户端回传了已分配的 taskId，服务端必须复用
    #   - 首轮：客户端**不能**自造 id，服务端总是自己生成
    client_task_id = params.get("taskId")
    existing = TASK_STORE.get(client_task_id) if client_task_id else None
    if existing:
        task_id = existing["id"]
        context_id = existing["contextId"]
    else:
        task_id = str(uuid.uuid4())
        context_id = params.get("contextId") or str(uuid.uuid4())

    # --- 1. 创建/拿到 Task ---
    task = TASK_STORE.get(task_id) or {
        "kind": "task",
        "id": task_id,
        "contextId": context_id,
        "status": {
            "state": "TASK_STATE_SUBMITTED",
            "timestamp": now_iso(),
        },
        "artifacts": [],
        "history": [],
    }
    # 把用户消息记入历史
    task["history"].append(msg)
    task["status"] = {
        "state": "TASK_STATE_WORKING",
        "message": make_message("ROLE_AGENT", "Processing request..."),
        "timestamp": now_iso(),
    }

    # --- 2. 跑业务逻辑（这里同步调用；真实场景里可能是异步 LLM） ---
    result_text = execute_logic(user_text)

    # --- 3. 产出 Artifact ---
    artifact = {
        "artifactId": str(uuid.uuid4()),
        "name": "result",
        "parts": [{"kind": "text", "text": result_text}],
    }
    task["artifacts"].append(artifact)

    # --- 4. 标记完成 ---
    task["status"] = {
        "state": "TASK_STATE_COMPLETED",
        "message": make_message("ROLE_AGENT", "Done."),
        "timestamp": now_iso(),
    }
    # 把 Agent 收尾消息也写进 history
    task["history"].append(task["status"]["message"])

    TASK_STORE[task_id] = task
    return task


async def handle_tasks_get(params: dict) -> dict:
    task = TASK_STORE.get(params["taskId"])
    if not task:
        raise JsonRpcError(-32001, "Task not found")
    return task


def dispatch(method: str, params: dict):
    routes = {
        "message/send": handle_message_send,
        "tasks/get": handle_tasks_get,
    }
    if method not in routes:
        raise JsonRpcError(-32601, f"Method not found: {method}")
    return routes[method](params)


# ----------------------------------------------------------------------------
# 4. HTTP 路由
# ----------------------------------------------------------------------------
async def agent_card_endpoint(request: Request):
    return JSONResponse(AGENT_CARD)


async def rpc_endpoint(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}},
            status_code=200,
        )

    rid = body.get("id")
    method = body.get("method")
    params = body.get("params") or {}

    try:
        result = await dispatch(method, params)
        return JSONResponse({"jsonrpc": "2.0", "id": rid, "result": result})
    except JsonRpcError as e:
        return JSONResponse({"jsonrpc": "2.0", "id": rid, "error": e.to_payload()})
    except Exception as e:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": rid, "error": {"code": -32603, "message": f"Internal error: {e}"}}
        )


app = Starlette(
    routes=[
        Route("/.well-known/agent-card.json", agent_card_endpoint),
        Route("/a2a", rpc_endpoint, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    print(f"🚀 A2A Hello World server on http://{HOST}:{PORT}")
    print(f"   GET  /.well-known/agent-card.json")
    print(f"   POST /a2a")
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")