#!/usr/bin/env python3
"""GitHub Actions: MiniMax-powered ingest for pyramid wiki.

Reads a markdown source file, calls MiniMax API to generate
an entity page following AGENT.md conventions.

Env vars:
  MINIMAX_API_KEY   — MiniMax API key
  MINIMAX_GROUP_ID  — (optional) MiniMax group ID
"""

import json, os, sys, urllib.request

API = "https://api.minimaxi.com/v1/text/chatcompletion_v2"
KEY = os.environ["MINIMAX_API_KEY"]
GROUP = os.environ.get("MINIMAX_GROUP_ID", "")

SYSTEM = """You are a knowledge curator for a personal wiki ("pyramid") following Karpathy's llm-wiki pattern.

Your task: read a markdown source file and generate a concise entity page.

Output ONLY valid markdown with YAML frontmatter. Format:

---
type: entity
tags: [topic1, topic2]
created: YYYY-MM-DD
sources: [source-name]
---

# Concept Name

## Definition
One-sentence definition.

## Key Points
- Point 1
- Point 2

## Related Concepts
- [[other-concept]]

Use [[wikilinks]] for cross-references. Keep it under 80 lines. Be factual — only extract what's in the source."""

def generate(source_text, source_name, domain):
    """Call MiniMax API to generate an entity page."""
    prompt = f"""Source: {source_name}
Domain: {domain}

Source content:
{source_text[:6000]}

Generate an entity page from this source. Extract the core concept, key points, and relevant cross-references."""

    payload = {
        "model": "MiniMax-M1",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    headers = {
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
    }
    if GROUP:
        payload["group_id"] = GROUP

    req = urllib.request.Request(API, json.dumps(payload).encode(), headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    
    return result["choices"][0]["message"]["content"]


def main():
    if len(sys.argv) < 4:
        print("Usage: ingest.py <source.md> <source-name> <domain> <output.md>")
        sys.exit(1)

    source_path = sys.argv[1]
    source_name = sys.argv[2]
    domain = sys.argv[3]
    output_path = sys.argv[4]

    with open(source_path) as f:
        source_text = f.read()

    # Skip empty or very short files
    if len(source_text.strip()) < 100:
        print(f"Skipping {source_name}: too short ({len(source_text)} chars)")
        return

    print(f"Ingesting: {source_name} ({len(source_text)} chars) → {domain}")
    entity_page = generate(source_text, source_name, domain)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(entity_page)

    print(f"  → {output_path}")


if __name__ == "__main__":
    main()
