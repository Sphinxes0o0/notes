"""
A2A 多 Agent 协作 — Orchestrator
==================================

对应文档：07 · 实战 3：多 Agent 协作

场景：
  - Orchestrator (端口 11000) 负责统筹
  - Flight Agent  (端口 11001) 负责查机票
  - Hotel Agent   (端口 11002) 负责查酒店
  - 各自有独立的 Agent Card，业务逻辑独立

Orchestrator 通过 A2A 调用子 Agent，最后把结果汇总成完整 itinerary。

启动：
  python 03_multi_agent_orchestrator.py
它会在 11000/11001/11002 端口同时启动 Orchestrator + 2 个子 Agent。
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route
import uvicorn

# ============================================================================
# 共用工具
# ============================================================================
def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def text_of(message: dict) -> str:
    for p in message.get("parts", []):
        if p.get("kind") == "text":
            return p.get("text", "")
    return ""


def make_card(name: str, skills: list, port: int, streaming=False) -> dict:
    return {
        "name": name,
        "description": f"{name} — sub-agent in a multi-agent demo",
        "version": "1.0.0",
        "supportedInterfaces": [{
            "url": f"http://127.0.0.1:{port}",
            "protocolBinding": "JSONRPC",
            "protocolVersion": "1.0",
        }],
        "capabilities": {
            "streaming": streaming,
            "pushNotifications": False,
            "extendedAgentCard": False,
            "stateTransitionHistory": True,
        },
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": skills,
    }


# ============================================================================
# 子 Agent 1: Flight Agent
# ============================================================================
FLIGHT_PORT = 11001

FLIGHT_CARD = make_card("Flight Agent", [{
    "id": "search_flight",
    "name": "Search a flight",
    "description": "Returns a fake flight option",
    "tags": ["flight"],
    "examples": ["Beijing -> Reykjavik, next June, 30000 CNY"],
    "inputModes": ["text/plain"],
    "outputModes": ["text/plain"],
}], FLIGHT_PORT)


async def flight_rpc(request: Request):
    body = await request.json()
    rid = body.get("id")
    if body["method"] != "message/send":
        return JSONResponse({"jsonrpc": "2.0", "id": rid,
                             "error": {"code": -32601, "message": "unsupported"}})
    text = text_of(body["params"]["message"])
    # 假数据：基于关键词返回 mock
    if "beijing" in text.lower() or "pek" in text.lower():
        flight_info = "Flight: IcelandAir FI552, PEK->KEF, ¥6800 round-trip, direct"
    else:
        flight_info = "Flight: IcelandAir FI552, Shanghai->KEF (via Helsinki), ¥8200 round-trip"
    task = {
        "kind": "task",
        "id": str(uuid.uuid4()),
        "contextId": str(uuid.uuid4()),
        "status": {"state": "TASK_STATE_COMPLETED",
                   "message": {"messageId": str(uuid.uuid4()), "role": "ROLE_AGENT",
                               "parts": [{"kind": "text", "text": "Found flight"}]},
                   "timestamp": now_iso()},
        "artifacts": [{
            "artifactId": str(uuid.uuid4()),
            "name": "flight",
            "parts": [{"kind": "text", "text": flight_info}],
        }],
        "history": [],
    }
    return JSONResponse({"jsonrpc": "2.0", "id": rid, "result": task})


flight_app = Starlette(routes=[
    Route("/.well-known/agent-card.json", lambda r: JSONResponse(FLIGHT_CARD)),
    Route("/a2a", flight_rpc, methods=["POST"]),
])


# ============================================================================
# 子 Agent 2: Hotel Agent
# ============================================================================
HOTEL_PORT = 11002

HOTEL_CARD = make_card("Hotel Agent", [{
    "id": "find_hotel",
    "name": "Find a hotel",
    "description": "Returns fake hotel options for Iceland",
    "tags": ["hotel"],
    "examples": ["7 nights in Iceland, budget ~3000 CNY/night"],
    "inputModes": ["text/plain"],
    "outputModes": ["text/plain"],
}], HOTEL_PORT)


HOTEL_DATA = {
    "reykjavik":  "Hotel Borg — 4-star, central Reykjavik, ¥3200/night",
    "vik":        "Hotel Vík í Mýrdal — 3-star, near black sand beach, ¥1800/night",
    "default":    "Guesthouse Hraun — countryside, ¥2200/night",
}


async def hotel_rpc(request: Request):
    body = await request.json()
    rid = body.get("id")
    if body["method"] != "message/send":
        return JSONResponse({"jsonrpc": "2.0", "id": rid,
                             "error": {"code": -32601, "message": "unsupported"}})
    text = text_of(body["params"]["message"]).lower()
    for k, v in HOTEL_DATA.items():
        if k in text:
            hotel = v
            break
    else:
        hotel = HOTEL_DATA["default"]
    task = {
        "kind": "task",
        "id": str(uuid.uuid4()),
        "contextId": str(uuid.uuid4()),
        "status": {"state": "TASK_STATE_COMPLETED",
                   "message": {"messageId": str(uuid.uuid4()), "role": "ROLE_AGENT",
                               "parts": [{"kind": "text", "text": "Found hotel"}]},
                   "timestamp": now_iso()},
        "artifacts": [{
            "artifactId": str(uuid.uuid4()),
            "name": "hotel",
            "parts": [{"kind": "text", "text": hotel}],
        }],
        "history": [],
    }
    return JSONResponse({"jsonrpc": "2.0", "id": rid, "result": task})


hotel_app = Starlette(routes=[
    Route("/.well-known/agent-card.json", lambda r: JSONResponse(HOTEL_CARD)),
    Route("/a2a", hotel_rpc, methods=["POST"]),
])


# ============================================================================
# Orchestrator
# ============================================================================
ORCH_PORT = 11000

ORCH_CARD = make_card("Travel Orchestrator", [{
    "id": "plan_trip",
    "name": "Plan a full trip",
    "description": "Orchestrates flight + hotel agents to plan a trip",
    "tags": ["travel", "orchestrator", "multi-agent"],
    "examples": ["Plan a 7-day Iceland trip, Beijing -> Reykjavik, ¥30000 total budget"],
    "inputModes": ["text/plain"],
    "outputModes": ["text/plain"],
}], ORCH_PORT, streaming=True)


ORCH_TASKS: dict[str, dict] = {}


async def call_subagent(http_client: httpx.AsyncClient, url: str, method: str, params: dict) -> dict:
    """调子 Agent 的标准 RPC，返回 result 字段。"""
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params,
    }
    r = await http_client.post(f"{url}/a2a", json=payload, timeout=10)
    r.raise_for_status()
    body = r.json()
    if "error" in body:
        raise RuntimeError(f"Sub-agent error: {body['error']}")
    return body["result"]


def sse_pack(payload: dict) -> bytes:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode()


async def orch_logic(task: dict, user_text: str):
    """Orchestrator 的业务逻辑：分发给子 Agent，汇总。"""
    task_id = task["id"]
    context_id = task["contextId"]

    # --- 阶段 1: 发现子 Agent（orchestrator 自己知道；现实中从注册表拉） ---
    yield ("status_update", {
        "kind": "status-update", "taskId": task_id, "contextId": context_id,
        "status": {"state": "TASK_STATE_WORKING",
                   "message": {"messageId": str(uuid.uuid4()), "role": "ROLE_AGENT",
                               "parts": [{"kind": "text", "text": "🔍 Discovering sub-agents..."}]},
                   "timestamp": now_iso()},
    })

    flight_url = f"http://127.0.0.1:{FLIGHT_PORT}"
    hotel_url = f"http://127.0.0.1:{HOTEL_PORT}"

    # 验证 Agent Card 可达
    async with httpx.AsyncClient() as client:
        await client.get(f"{flight_url}/.well-known/agent-card.json")
        await client.get(f"{hotel_url}/.well-known/agent-card.json")

    # --- 阶段 2: 并行调用 flight + hotel ---
    yield ("status_update", {
        "kind": "status-update", "taskId": task_id, "contextId": context_id,
        "status": {"state": "TASK_STATE_WORKING",
                   "message": {"messageId": str(uuid.uuid4()), "role": "ROLE_AGENT",
                               "parts": [{"kind": "text", "text": "✈️  Booking flight + 🏨  finding hotel in parallel..."}]},
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
    hotel_text = hotel_task["artifacts"][0]["parts"][0]["text"]

    # --- 阶段 3: 流式输出汇总 ---
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

    # 终态
    yield ("status_update", {
        "kind": "status-update", "taskId": task_id, "contextId": context_id,
        "status": {"state": "TASK_STATE_COMPLETED",
                   "message": {"messageId": str(uuid.uuid4()), "role": "ROLE_AGENT",
                               "parts": [{"kind": "text", "text": "Done!"}]},
                   "timestamp": now_iso()},
        "final": True,
    })


async def orch_card(request: Request):
    return JSONResponse(ORCH_CARD)


async def orch_rpc(request: Request):
    body = await request.json()
    rid = body.get("id")
    method = body["method"]
    params = body.get("params") or {}

    if method == "message/stream":
        msg = params["message"]
        task_id = params.get("taskId") or str(uuid.uuid4())
        context_id = params.get("contextId") or str(uuid.uuid4())
        task = ORCH_TASKS.setdefault(task_id, {
            "kind": "task", "id": task_id, "contextId": context_id,
            "status": {"state": "TASK_STATE_SUBMITTED", "timestamp": now_iso()},
            "artifacts": [], "history": [],
        })
        user_text = text_of(msg)

        async def gen():
            yield sse_pack({"jsonrpc": "2.0", "id": rid, "result": {**task}})
            async for kind, payload in orch_logic(task, user_text):
                yield sse_pack({"jsonrpc": "2.0", "id": rid, "result": payload})
        return StreamingResponse(gen(), media_type="text/event-stream")

    return JSONResponse({"jsonrpc": "2.0", "id": rid,
                         "error": {"code": -32601, "message": f"unsupported: {method}"}})


orch_app = Starlette(routes=[
    Route("/.well-known/agent-card.json", orch_card),
    Route("/a2a", orch_rpc, methods=["POST"]),
])


# ============================================================================
# 启动三服务（用 asyncio 跑在同一进程里）
# ============================================================================
async def main():
    config_orch = uvicorn.Config(orch_app, host="127.0.0.1", port=ORCH_PORT, log_level="warning")
    config_flight = uvicorn.Config(flight_app, host="127.0.0.1", port=FLIGHT_PORT, log_level="warning")
    config_hotel = uvicorn.Config(hotel_app, host="127.0.0.1", port=HOTEL_PORT, log_level="warning")

    servers = [uvicorn.Server(c) for c in [config_orch, config_flight, config_hotel]]
    print(f"🚀 Orchestrator  → http://127.0.0.1:{ORCH_PORT}")
    print(f"🚀 Flight Agent  → http://127.0.0.1:{FLIGHT_PORT}")
    print(f"🚀 Hotel Agent   → http://127.0.0.1:{HOTEL_PORT}")
    await asyncio.gather(*[s.serve() for s in servers])


if __name__ == "__main__":
    asyncio.run(main())