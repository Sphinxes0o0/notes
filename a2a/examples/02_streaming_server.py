"""
A2A 流式 + 多轮 — Server
========================

对应文档：06 · 实战 2：流式 + 多轮对话

特性：
  - message/stream（SSE 流式）
  - 多轮对话（input-required 状态 + contextId）
  - 流式 artifact 增量（lastChunk 标志）
  - tasks/resubscribe（重连）

业务逻辑：模拟一个"旅行规划助手"。
  - 收到 "plan trip" → 反问 "month?"
  - 收到月份 → 反问 "budget?"
  - 收到预算 → 流式产出 itinerary，每天一段
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route
import uvicorn

HOST = "127.0.0.1"
PORT = 10001

AGENT_CARD = {
    "name": "Streaming Travel Agent",
    "description": "Plans a trip by asking follow-up questions and streaming the result",
    "version": "1.0.0",
    "supportedInterfaces": [
        {"url": f"http://{HOST}:{PORT}", "protocolBinding": "JSONRPC", "protocolVersion": "1.0"},
    ],
    "capabilities": {
        "streaming": True,
        "pushNotifications": False,
        "extendedAgentCard": False,
        "stateTransitionHistory": True,
    },
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "skills": [
        {
            "id": "plan_trip",
            "name": "Plan a trip",
            "description": "Asks follow-ups, then streams a day-by-day itinerary",
            "tags": ["travel", "streaming", "multi-turn"],
            "examples": ["plan my trip", "plan a 7-day Iceland trip"],
            "inputModes": ["text/plain"],
            "outputModes": ["text/plain"],
        }
    ],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def text_of(message: dict) -> str:
    for p in message.get("parts", []):
        if p.get("kind") == "text":
            return p.get("text", "")
    return ""


# ----------------------------------------------------------------------------
# 业务状态机
# ----------------------------------------------------------------------------
# 我们用 metadata 字段做"会话小笔记本"：
#   metadata._state    = "asked_month" | "asked_budget" | "producing" | "done"
#   metadata._month    = "next June"  (用户回复后填)
#   metadata._budget   = "30000 CNY"  (用户回复后填)

DAYS = [
    "Reykjavik arrival, Blue Lagoon",
    "Golden Circle day tour",
    "South Coast: Seljalandsfoss, Skógafoss, Vík",
    "Skaftafell + Jokulsarlon glacier lagoon",
    "East Fjords drive",
    "Mývatn + Dettifoss",
    "Return to Reykjavik, shopping",
]


async def advance(user_text: str, task: dict) -> str:
    """返回 'continue' / 'ask' / 'produce' / 'done' 之一。"""
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


# ----------------------------------------------------------------------------
# 流式核心
# ----------------------------------------------------------------------------
def sse_pack(payload: dict) -> bytes:
    """把一个 JSON-RPC 响应包成 SSE event。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode()


def make_agent_msg(text: str) -> dict:
    return {
        "messageId": str(uuid.uuid4()),
        "role": "ROLE_AGENT",
        "parts": [{"kind": "text", "text": text}],
    }


async def stream_logic(task: dict, user_text: str):
    """生成 (kind, payload) 序列，由调用方决定怎么 wire 到 SSE 上。"""
    task_id = task["id"]
    context_id = task["contextId"]
    task.setdefault("history", []).append({"role": "USER", "text": user_text})

    decision = await advance(user_text, task)
    md = task["metadata"]

    if decision.startswith("ask:"):
        question = decision.split(":", 1)[1]
        task["status"] = {"state": "TASK_STATE_INPUT_REQUIRED",
                          "message": make_agent_msg(question),
                          "timestamp": now_iso()}
        yield ("status_update", {
            "kind": "status-update",
            "taskId": task_id,
            "contextId": context_id,
            "status": task["status"],
            "final": True,
        })
        return

    if decision == "produce":
        # 标记为 working
        task["status"] = {"state": "TASK_STATE_WORKING",
                          "message": make_agent_msg(f"Planning your {md.get('_month','')} trip with budget {md.get('_budget','')}..."),
                          "timestamp": now_iso()}
        yield ("status_update", {
            "kind": "status-update",
            "taskId": task_id,
            "contextId": context_id,
            "status": task["status"],
        })

        # 流式产出 artifact（每个 Day 一块）
        artifact_id = str(uuid.uuid4())
        task.setdefault("artifacts", [])
        for i, day in enumerate(DAYS, 1):
            await asyncio.sleep(0.3)   # 模拟 LLM 流式生成
            text_chunk = f"Day {i}: {day}"
            art = {
                "artifactId": artifact_id,
                "name": "itinerary",
                "parts": [{"kind": "text", "text": text_chunk}],
            }
            task["artifacts"].append(art) if i == len(DAYS) else None
            yield ("artifact_update", {
                "kind": "artifact-update",
                "taskId": task_id,
                "contextId": context_id,
                "artifact": art,
                "append": i > 1,
                "lastChunk": i == len(DAYS),
            })

        # 终态
        task["status"] = {"state": "TASK_STATE_COMPLETED",
                          "message": make_agent_msg("Have a great trip!"),
                          "timestamp": now_iso()}
        md["_state"] = "done"
        yield ("status_update", {
            "kind": "status-update",
            "taskId": task_id,
            "contextId": context_id,
            "status": task["status"],
            "final": True,
        })
        return

    # 已完成的情况：再发就回个 message
    yield ("message", {
        "kind": "message",
        "messageId": str(uuid.uuid4()),
        "role": "ROLE_AGENT",
        "parts": [{"kind": "text", "text": "Your itinerary is ready above!"}],
    })


# ----------------------------------------------------------------------------
# HTTP
# ----------------------------------------------------------------------------
async def agent_card_endpoint(request: Request):
    return JSONResponse(AGENT_CARD)


TASKS: dict[str, dict] = {}


async def rpc_endpoint(request: Request):
    """分流出 message/stream（SSE） 和 其他（JSON）"""
    body = await request.json()
    rid = body.get("id")
    method = body.get("method")
    params = body.get("params") or {}

    if method == "message/stream":
        # 准备 task
        msg = params["message"]
        task_id = params.get("taskId") or str(uuid.uuid4())
        context_id = params.get("contextId") or str(uuid.uuid4())
        task = TASKS.get(task_id, {
            "kind": "task",
            "id": task_id,
            "contextId": context_id,
            "status": {"state": "TASK_STATE_SUBMITTED", "timestamp": now_iso()},
            "artifacts": [],
            "history": [],
            "metadata": {},
        })
        TASKS[task_id] = task
        user_text = text_of(msg)

        async def event_gen():
            # 先发一个初始 task 快照
            yield sse_pack({"jsonrpc": "2.0", "id": rid, "result": {
                "kind": "task",
                **task,
            }})
            async for kind, payload in stream_logic(task, user_text):
                yield sse_pack({"jsonrpc": "2.0", "id": rid, "result": payload})

        return StreamingResponse(event_gen(), media_type="text/event-stream")

    if method == "tasks/get":
        return JSONResponse({"jsonrpc": "2.0", "id": rid,
                             "result": TASKS.get(params["taskId"])})

    return JSONResponse({"jsonrpc": "2.0", "id": rid,
                         "error": {"code": -32601, "message": f"Method not found: {method}"}})


app = Starlette(routes=[
    Route("/.well-known/agent-card.json", agent_card_endpoint),
    Route("/a2a", rpc_endpoint, methods=["POST"]),
])

if __name__ == "__main__":
    print(f"🚀 Streaming server on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")