"""
A2A 多 Agent 协作 — Client
============================

对应文档：07 · 实战 3：多 Agent 协作

直接跟 Orchestrator 对话，由 Orchestrator 内部去调度 Flight + Hotel Agent。
"""

import httpx
import json

ORCH = "http://127.0.0.1:11000"


def stream_orchestrator(text: str):
    print(f"\n📤 Sending to Orchestrator: {text!r}\n")
    payload = {
        "jsonrpc": "2.0", "id": "req-001", "method": "message/stream",
        "params": {"message": {
            "messageId": "msg-001", "role": "ROLE_USER",
            "parts": [{"kind": "text", "text": text}],
        }},
    }
    chunks: dict[str, list[str]] = {}
    with httpx.stream("POST", f"{ORCH}/a2a", json=payload, timeout=30) as resp:
        for line in resp.iter_lines():
            if not line.startswith("data:"):
                continue
            data = json.loads(line[len("data:"):].strip())
            result = data.get("result", {})
            kind = result.get("kind")
            if kind == "status-update":
                state = result["status"]["state"]
                msg = result["status"].get("message", {}).get("parts", [{}])[0].get("text", "")
                print(f"   🔄 {state:30s}  {msg}")
                if result.get("final"):
                    print("   🏁 done")
                    break
            elif kind == "artifact-update":
                aid = result["artifact"]["artifactId"]
                txt = result["artifact"]["parts"][0]["text"]
                chunks.setdefault(aid, []).append(txt)
                print(f"   📝 chunk: {txt!r}")

    print("\n🗺️  Full summary:")
    for aid, parts in chunks.items():
        print("".join(parts))


if __name__ == "__main__":
    stream_orchestrator("Plan a 7-day Iceland trip, Beijing -> Reykjavik, 30000 CNY total budget")