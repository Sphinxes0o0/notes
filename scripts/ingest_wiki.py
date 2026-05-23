#!/usr/bin/env python3
"""
Wiki auto-ingest script for GitHub Actions.
Reads raw/ files, calls MiniMax API to ingest into LLM wiki format.

Usage:
  python3 scripts/ingest_wiki.py <wiki_dir> <raw_subdir>

Environment:
  MINIMAX_CN_API_KEY  - MiniMax API key (from GitHub Secret)
  MINIMAX_MODEL       - Model name (default: MiniMax-M2.7-highspeed)
  GITHUB_TOKEN        - For gh CLI auth (auto in Actions)
"""

import os, sys, json, hashlib, subprocess
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

MINIMAX_BASE = "https://api.minimaxi.com/v1"
MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7-highspeed")
API_KEY = os.getenv("MINIMAX_CN_API_KEY", "")

WIKI_SYSTEM_PROMPT = """You are an LLM Wiki maintenance agent. Your job is to read raw source files (tech notes, research papers, exercise science literature) and integrate them into a structured markdown wiki.

## Wiki Convention

### File structure
- wiki/sources/<slug>.md — source summary pages
- wiki/entities/<domain>/<slug>.md — concept/entity pages
- wiki/<domain>-index.md — module indexes
- wiki/home.md — global navigation
- wiki/log.md — operation log

### Page format (YAML frontmatter required)
```yaml
---
type: source | entity | index
tags: [tag1, tag2]
created: YYYY-MM-DD
sources: [source-slug]  # for entities
---
```

### Cross-references
- Use [[wikilinks]] between pages
- Minimum 2 cross-links per entity page

### Your task
Given raw source files, output a JSON plan with these actions:
- CREATE: file path + content for new pages
- UPDATE: file path + patch instructions for existing pages
- SKIP: files already covered

Respond in this JSON format:
```json
{
  "summary": "one-line summary of what you ingested",
  "actions": [
    {"type": "CREATE", "path": "wiki/sources/foo.md", "content": "full page content"},
    {"type": "UPDATE", "path": "wiki/home.md", "instruction": "add new source to Sources table"}
  ]
}
```

Keep pages concise (<200 lines). Write in Chinese for Chinese sources, English for English sources."""


def call_minimax(system_prompt: str, user_message: str) -> str:
    """Call MiniMax API (OpenAI-compatible)."""
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3,
        "max_tokens": 16000
    }).encode()

    req = Request(
        f"{MINIMAX_BASE}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )

    try:
        with urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except URLError as e:
        print(f"MiniMax API error: {e}", file=sys.stderr)
        raise


def read_file_safe(path: str, max_bytes: int = 50000) -> str:
    """Read a file, return truncated content if too large."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(max_bytes)
            if len(content) >= max_bytes:
                content += "\n\n[TRUNCATED - file too large]"
            return content
    except UnicodeDecodeError:
        return "[BINARY FILE - cannot read]"
    except FileNotFoundError:
        return "[FILE NOT FOUND]"


def compute_manifest(raw_dir: str) -> dict:
    """Compute hash manifest of all raw files."""
    manifest = {}
    for root, dirs, files in os.walk(raw_dir):
        # Skip .git
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, raw_dir)
            try:
                with open(fpath, 'rb') as fh:
                    manifest[rel] = hashlib.md5(fh.read()).hexdigest()
            except (IOError, OSError):
                manifest[rel] = "UNREADABLE"
    return manifest


def load_manifest(manifest_path: str) -> dict:
    """Load saved manifest from JSON file."""
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            return json.load(f)
    return {}


def save_manifest(manifest: dict, manifest_path: str):
    """Save manifest to JSON file."""
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)


def get_changed_files(raw_dir: str, manifest_path: str) -> list:
    """Return list of changed/new/deleted file paths."""
    current = compute_manifest(raw_dir)
    old = load_manifest(manifest_path)

    changed = []
    for path, new_hash in current.items():
        if path not in old:
            changed.append(("NEW", path))
        elif old[path] != new_hash:
            changed.append(("CHANGED", path))

    save_manifest(current, manifest_path)
    return changed


def apply_actions(actions: list, wiki_dir: str):
    """Apply CREATE and UPDATE actions to the wiki."""
    for action in actions:
        typ = action.get("type")
        path = os.path.join(wiki_dir, action["path"])

        if typ == "CREATE":
            content = action.get("content", "")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  CREATE {action['path']}")

        elif typ == "UPDATE":
            instruction = action.get("instruction", "")
            # For now, log update instructions — manual review recommended
            print(f"  UPDATE {action['path']}: {instruction}")

        elif typ == "SKIP":
            print(f"  SKIP {action.get('path', 'unknown')}")


def git_commit_and_push(wiki_dir: str, message: str):
    """Stage, commit, and push changes."""
    subprocess.run(["git", "-C", wiki_dir, "config", "user.name", "hermes-wiki-bot"], check=True)
    subprocess.run(["git", "-C", wiki_dir, "config", "user.email", "wiki-bot@hermes.local"], check=True)
    subprocess.run(["git", "-C", wiki_dir, "add", "-A"], check=True)

    # Check if there are changes
    result = subprocess.run(
        ["git", "-C", wiki_dir, "diff", "--cached", "--quiet"],
        capture_output=True
    )
    if result.returncode == 0:
        print("No changes to commit")
        return

    subprocess.run(["git", "-C", wiki_dir, "commit", "-m", message], check=True)
    subprocess.run(["git", "-C", wiki_dir, "push"], check=True)
    print(f"Committed and pushed: {message}")


def main():
    if len(sys.argv) < 3:
        print("Usage: ingest_wiki.py <wiki_dir> <raw_subdir>")
        sys.exit(1)

    wiki_dir = sys.argv[1]
    raw_subdir = sys.argv[2]

    if not API_KEY:
        print("ERROR: MINIMAX_CN_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    raw_dir = os.path.join(wiki_dir, "raw", raw_subdir)
    manifest_path = os.path.join(wiki_dir, ".raw_manifest.json")

    if not os.path.isdir(raw_dir):
        print(f"ERROR: raw dir not found: {raw_dir}", file=sys.stderr)
        sys.exit(1)

    # 1. Detect changes
    print(f"Scanning {raw_dir} for changes...")
    changed = get_changed_files(raw_dir, manifest_path)

    if not changed:
        print("No changes detected. Skipping ingest.")
        return

    print(f"Found {len(changed)} changed/new files:")

    # 2. Read changed files
    files_content = []
    for status, path in changed:
        print(f"  [{status}] {path}")
        content = read_file_safe(os.path.join(raw_dir, path), max_bytes=30000)
        files_content.append(f"## File: {path} ({status})\n\n{content}")

    # 3. Read wiki context
    home_content = read_file_safe(os.path.join(wiki_dir, "wiki/home.md"), max_bytes=10000)
    log_tail = read_file_safe(os.path.join(wiki_dir, "wiki/log.md"), max_bytes=5000)

    # 4. Build prompt and call MiniMax
    user_msg = f"""## Wiki Context

### home.md (current)
{home_content}

### log.md (recent)
{log_tail}

## Changed Raw Files

{chr(10).join(files_content)}

## Instructions
Analyze these raw files. For each file, check if it's already covered in the existing wiki.
Output a JSON action plan. Create source pages for new topics. Create entity pages for new concepts.
Update index pages and home.md as needed. Skip files that are already well-covered."""

    print("\nCalling MiniMax API...")
    try:
        result = call_minimax(WIKI_SYSTEM_PROMPT, user_msg)
    except Exception as e:
        print(f"ERROR calling MiniMax: {e}", file=sys.stderr)
        sys.exit(1)

    # 5. Parse and apply
    # Extract JSON from response (may have markdown wrapping)
    try:
        # Find JSON block
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]

        plan = json.loads(result)
    except json.JSONDecodeError as e:
        print(f"ERROR parsing MiniMax response: {e}", file=sys.stderr)
        print("Raw response:", file=sys.stderr)
        print(result[:2000], file=sys.stderr)
        sys.exit(1)

    summary = plan.get("summary", "auto-ingest")
    actions = plan.get("actions", [])
    print(f"\nPlan: {summary}")
    print(f"Actions: {len(actions)}")

    # 6. Apply actions
    apply_actions(actions, wiki_dir)

    # 7. Update log.md
    log_path = os.path.join(wiki_dir, "wiki/log.md")
    today = datetime.now().strftime("%Y-%m-%d")
    log_entry = f"""
## [{today}] auto-ingest | {summary}

GitHub Actions auto-ingest triggered by push to source repo.
{len(changed)} files changed: {', '.join(f[1] for f in changed[:5])}{'...' if len(changed) > 5 else ''}

Actions applied: {len(actions)}
"""
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_entry)

    # 8. Commit and push
    git_commit_and_push(wiki_dir, f"auto-ingest: {summary}")


if __name__ == "__main__":
    main()
