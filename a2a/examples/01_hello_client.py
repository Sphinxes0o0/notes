"""
A2A Hello World — Client
========================

对应文档：05 · 实战 1：Hello World

这个客户端演示 A2A 的"三步走"：
  1. 发现（fetch Agent Card）
  2. 发消息（message/send）
  3. 查任务（tasks/get）

依赖：
  pip install httpx
"""

import httpx
import json
import sys

BASE = "http://127.0.0.1:9999"


def fetch_agent_card(base_url: str) -> dict:
    url = f"{base_url}/.well-known/agent-card.json"
    print(f"\n🔎 Fetching Agent Card from {url}")
    resp = httpx.get(url)
    resp.raise_for_status()
    card = resp.json()
    print(json.dumps(card, indent=2, ensure_ascii=False)[:400] + "...")
    return card


def send_message(base_url: str, text: str) -> dict:
    """发一个 message/send 请求，返回整个 Task 对象。"""
    payload = {
        "jsonrpc": "2.0",
        "id": "req-001",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "msg-001",
                "role": "ROLE_USER",
                "parts": [{"kind": "text", "text": text}],
            },
            "configuration": {"blocking": True},
        },
    }
    print(f"\n📤 Sending message: {text!r}")
    resp = httpx.post(f"{base_url}/a2a", json=payload, timeout=10)
    resp.raise_for_status()
    body = resp.json()
    if "error" in body:
        print(f"❌ Error: {body['error']}")
        sys.exit(1)
    return body["result"]


def print_task(task: dict):
    print(f"\n📦 Task received:")
    print(f"   id          = {task['id']}")
    print(f"   contextId   = {task['contextId']}")
    print(f"   state       = {task['status']['state']}")
    print(f"   history     = {len(task['history'])} messages")
    print(f"   artifacts   = {len(task['artifacts'])}")
    for art in task["artifacts"]:
        text = art["parts"][0]["text"]
        print(f"     └─ {art['name']!r:>12} → {text!r}")


def main():
    card = fetch_agent_card(BASE)
    print(f"\nAgent says hi! Skills: {[s['id'] for s in card['skills']]}")

    # 测两次：第二次是 follow-up
    task1 = send_message(BASE, "World")
    print_task(task1)

    print("\n" + "=" * 50)
    print("Follow-up: 继续发消息（带 contextId）")
    print("=" * 50)
    payload = {
        "jsonrpc": "2.0",
        "id": "req-002",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "msg-002",
                "role": "ROLE_USER",
                "parts": [{"kind": "text", "text": "Sphinx"}],
            },
            "taskId": task1["id"],
            "contextId": task1["contextId"],
        },
    }
    resp = httpx.post(f"{BASE}/a2a", json=payload).json()
    print_task(resp["result"])

    print("\n✅ Done!")


if __name__ == "__main__":
    main()