"""
A2A 流式 + 多轮 — Client
========================

对应文档：06 · 实战 2：流式 + 多轮对话

演示：
  1. 拿 Agent Card
  2. 发第一条消息 → 拿到 input-required
  3. 续写（带 taskId + contextId）→ 流式接收 itinerary
  4. 把多个 artifact chunk 拼成完整 itinerary

依赖：pip install httpx
"""

import httpx
import json
import sys

BASE = "http://127.0.0.1:10001"


def fetch_agent_card(base_url):
    r = httpx.get(f"{base_url}/.well-known/agent-card.json")
    r.raise_for_status()
    card = r.json()
    print(f"🪪 Agent: {card['name']}")
    print(f"   streaming = {card['capabilities']['streaming']}")
    return card


def stream_send(text: str, task_id=None, context_id=None):
    """发 message/stream，迭代 SSE 事件并打印。返回 (final_task_id, final_context_id, full_text)。"""
    payload = {
        "jsonrpc": "2.0",
        "id": "req-001",
        "method": "message/stream",
        "params": {
            "message": {
                "messageId": str(__import__("uuid").uuid4()),
                "role": "ROLE_USER",
                "parts": [{"kind": "text", "text": text}],
            }
        },
    }
    if task_id: payload["params"]["taskId"] = task_id
    if context_id: payload["params"]["contextId"] = context_id

    print(f"\n📤 Sending: {text!r}")

    artifact_chunks: dict[str, list[str]] = {}
    final_task_id = task_id
    final_context_id = context_id
    last_state = None

    with httpx.stream("POST", f"{BASE}/a2a", json=payload, timeout=30) as resp:
        for line in resp.iter_lines():
            if not line.startswith("data:"):
                continue
            data = json.loads(line[len("data:"):].strip())
            result = data.get("result", {})
            kind = result.get("kind")
            final_task_id = final_task_id or result.get("taskId")
            final_context_id = final_context_id or result.get("contextId")

            if kind == "task":
                print(f"   📋 initial task: id={result['id'][:8]}...")
            elif kind == "message":
                print(f"   💬 agent says: {result['parts'][0]['text']!r}")
            elif kind == "status-update":
                state = result["status"]["state"]
                msg = result["status"].get("message", {}).get("parts", [{}])[0].get("text", "")
                last_state = state
                if msg:
                    print(f"   🔄 status: {state}  ({msg!r})")
                else:
                    print(f"   🔄 status: {state}")
                if result.get("final"):
                    print(f"   🏁 stream finished")
                    break
            elif kind == "artifact-update":
                art = result["artifact"]
                aid = art["artifactId"]
                text_chunk = art["parts"][0]["text"]
                artifact_chunks.setdefault(aid, []).append(text_chunk)
                print(f"   📝 artifact chunk [{aid[:8]}]: {text_chunk!r}")

    print(f"\n   artifact chunks collected: {sum(len(v) for v in artifact_chunks.values())}")
    return final_task_id, final_context_id, artifact_chunks


def main():
    card = fetch_agent_card(BASE)

    # ---- 第一轮：trigger 多轮 ----
    tid, cid, _ = stream_send("plan my trip")
    print(f"\n🔑 remembered: taskId={tid[:8]}, contextId={cid[:8]}")

    # ---- 第二轮：补充月份 ----
    print("\n" + "=" * 50)
    tid, cid, _ = stream_send("next June", task_id=tid, context_id=cid)

    # ---- 第三轮：补充预算 + 流式 itinerary ----
    print("\n" + "=" * 50)
    tid, cid, chunks = stream_send("30000 CNY", task_id=tid, context_id=cid)

    # 拼接 artifact
    if chunks:
        full_itinerary = "\n".join("".join(v) for v in chunks.values())
        print(f"\n🗺️  Final itinerary:\n{full_itinerary}")

    print("\n✅ Demo complete!")


if __name__ == "__main__":
    main()