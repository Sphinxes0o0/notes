#!/usr/bin/env python3
"""
Wiki auto-ingest script for GitHub Actions.
Reads raw/ files, calls LLM to ingest into LLM wiki format.
Supports dual provider with automatic fallback.

Usage:
  python3 scripts/ingest_wiki.py <wiki_dir> <raw_subdir> [--provider minimax|copilot]

Provider priority (env OVERRIDE_PROVIDER):
  1. OVERRIDE_PROVIDER env var (if set)
  2. --provider flag
  3. COPILOT first, MINIMAX fallback

Environment:
  GITHUB_TOKEN           - Auto-injected in Actions (for Copilot API)
  COPILOT_CHAT_MODEL     - Copilot model (auto-detect)
  MINIMAX_CN_API_KEY     - MiniMax API key
  MINIMAX_MODEL          - MiniMax model (default: MiniMax-M2.7-highspeed)
"""

import os, sys, json, hashlib, subprocess, argparse
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError


# ── System Prompt ──────────────────────────────────────────

WIKI_SYSTEM_PROMPT = """You are an LLM Wiki maintenance agent. Integrate raw source files into a structured markdown wiki.

## Wiki Convention
- wiki/sources/<slug>.md — source summary pages
- wiki/entities/<domain>/<slug>.md — concept/entity pages
- wiki/<domain>-index.md — module indexes
- wiki/home.md — global navigation
- wiki/log.md — operation log

### Page frontmatter (required)
```yaml
---
type: source | entity | index
tags: [tag1, tag2]
created: YYYY-MM-DD
sources: [source-slug]
---
```

### Rules
- Use [[wikilinks]] between pages. Minimum 2 cross-links per entity page.
- Keep pages <200 lines.
- Write in Chinese for Chinese sources, English for English sources.
- DON'T duplicate existing content — check home.md and log.md first.

### Output format
Output VALID JSON only, no markdown wrapping:
```json
{
  "summary": "one-line summary of ingested content",
  "actions": [
    {"type": "CREATE", "path": "wiki/sources/foo.md", "content": "full page content..."},
    {"type": "UPDATE", "path": "wiki/home.md", "instruction": "add new source to Sources table"},
    {"type": "SKIP", "path": "already/covered.md"}
  ]
}
```"""


# ── Provider: MiniMax (OpenAI-compatible) ──────────────────

MINIMAX_BASE = "https://api.minimaxi.com/v1"
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7-highspeed")

def call_minimax(system_prompt: str, user_message: str) -> str:
    api_key = os.getenv("MINIMAX_CN_API_KEY", "")
    if not api_key:
        raise RuntimeError("MINIMAX_CN_API_KEY not set")

    body = json.dumps({
        "model": MINIMAX_MODEL,
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
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    with urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"]


# ── Provider: GitHub Copilot (via gh CLI in Actions) ───────

def call_copilot(system_prompt: str, user_message: str) -> str:
    """Call GitHub Copilot via 'gh copilot' CLI. Works in Actions with GITHUB_TOKEN."""
    full_prompt = f"{system_prompt}\n\n---\n\n{user_message}"

    # gh copilot chat accepts piped input
    result = subprocess.run(
        ["gh", "copilot", "chat"],
        input=full_prompt,
        capture_output=True, text=True, timeout=300
    )

    if result.returncode != 0:
        stderr = result.stderr[:500]
        raise RuntimeError(f"gh copilot failed (exit {result.returncode}): {stderr}")

    output = result.stdout.strip()
    if not output:
        raise RuntimeError("gh copilot returned empty output")
    return output


# ── Provider dispatch ──────────────────────────────────────

PROVIDERS = {
    "minimax": call_minimax,
    "copilot": call_copilot,
}

def call_llm(system_prompt: str, user_message: str, providers: list) -> tuple:
    """Try providers in order. Returns (result, provider_name)."""
    errors = []
    for name in providers:
        fn = PROVIDERS.get(name)
        if not fn:
            errors.append(f"{name}: unknown provider")
            continue
        try:
            print(f"  Trying {name}...", file=sys.stderr)
            result = fn(system_prompt, user_message)
            print(f"  {name} ✓", file=sys.stderr)
            return result, name
        except Exception as e:
            msg = f"{name}: {e}"
            print(f"  {name} ✗ — {e}", file=sys.stderr)
            errors.append(msg)
    raise RuntimeError(f"All providers failed:\n" + "\n".join(errors))


# ── File utilities ─────────────────────────────────────────

def read_file_safe(path: str, max_bytes: int = 50000) -> str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(max_bytes)
            if len(content) >= max_bytes:
                content += "\n\n[TRUNCATED]"
            return content
    except (UnicodeDecodeError, FileNotFoundError):
        return "[CANNOT READ]"

def compute_manifest(raw_dir: str) -> dict:
    manifest = {}
    for root, dirs, files in os.walk(raw_dir):
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

def load_manifest(path: str) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_manifest(manifest: dict, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(manifest, f, indent=2)

def get_changed_files(raw_dir: str, manifest_path: str) -> list:
    current = compute_manifest(raw_dir)
    old = load_manifest(manifest_path)
    changed = []
    for p, h in current.items():
        if p not in old:
            changed.append(("NEW", p))
        elif old[p] != h:
            changed.append(("CHANGED", p))
    save_manifest(current, manifest_path)
    return changed


# ── Action applier ─────────────────────────────────────────

def apply_actions(actions: list, wiki_dir: str):
    for action in actions:
        typ = action.get("type")
        path = os.path.join(wiki_dir, action["path"])
        if typ == "CREATE":
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(action.get("content", ""))
            print(f"  CREATE {action['path']}")
        elif typ == "UPDATE":
            print(f"  UPDATE {action['path']}: {action.get('instruction', '')}")
        elif typ == "SKIP":
            print(f"  SKIP {action.get('path', '?')}")

def git_commit_and_push(wiki_dir: str, message: str):
    subprocess.run(["git", "-C", wiki_dir, "config", "user.name", "hermes-wiki-bot"], check=True)
    subprocess.run(["git", "-C", wiki_dir, "config", "user.email", "wiki-bot@hermes.local"], check=True)
    subprocess.run(["git", "-C", wiki_dir, "add", "-A"], check=True)
    r = subprocess.run(["git", "-C", wiki_dir, "diff", "--cached", "--quiet"], capture_output=True)
    if r.returncode == 0:
        print("No changes to commit")
        return
    subprocess.run(["git", "-C", wiki_dir, "commit", "-m", message], check=True)
    subprocess.run(["git", "-C", wiki_dir, "push"], check=True)
    print(f"Committed: {message}")


# ── Main ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Wiki auto-ingest")
    parser.add_argument("wiki_dir", help="Path to wiki repo")
    parser.add_argument("raw_subdir", help="Raw subdirectory (e.g. github/notes)")
    parser.add_argument("--provider", choices=["minimax", "copilot"],
                        help="Force a specific provider")
    args = parser.parse_args()

    wiki_dir = args.wiki_dir
    raw_subdir = args.raw_subdir
    raw_dir = os.path.join(wiki_dir, "raw", raw_subdir)
    manifest_path = os.path.join(wiki_dir, ".raw_manifest.json")

    if not os.path.isdir(raw_dir):
        print(f"ERROR: raw dir not found: {raw_dir}", file=sys.stderr)
        sys.exit(1)

    # 1. Detect changes
    print(f"Scanning {raw_dir}...", file=sys.stderr)
    changed = get_changed_files(raw_dir, manifest_path)
    if not changed:
        print("No changes. Done.")
        return
    print(f"{len(changed)} changed files", file=sys.stderr)

    # 2. Read changed files
    files_content = []
    for status, path in changed:
        content = read_file_safe(os.path.join(raw_dir, path), max_bytes=30000)
        files_content.append(f"## [{status}] {path}\n\n{content}")

    # 3. Read wiki context
    home = read_file_safe(os.path.join(wiki_dir, "wiki/home.md"), max_bytes=10000)
    log_tail = read_file_safe(os.path.join(wiki_dir, "wiki/log.md"), max_bytes=5000)

    # 4. Build prompt
    user_msg = f"""## Wiki Context
### home.md
{home}
### log.md (recent)
{log_tail}

## Changed Files
{chr(10).join(files_content)}

## Task
Analyze these files. Create source/entity pages for NEW content.
Update indexes and home.md. Skip already-covered content.
Output JSON action plan."""

    # 5. Call LLM with fallback
    override = os.getenv("OVERRIDE_PROVIDER", "")
    if override:
        providers = [override]
    elif args.provider:
        providers = [args.provider]
    else:
        providers = ["minimax", "copilot"]  # MiniMax primary, Copilot fallback

    print(f"Providers: {' → '.join(providers)}", file=sys.stderr)
    result, used_provider = call_llm(WIKI_SYSTEM_PROMPT, user_msg, providers)

    # 6. Parse JSON
    try:
        # Strip markdown code fences if present
        text = result.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[:-3]
        plan = json.loads(text)
    except json.JSONDecodeError:
        print(f"ERROR parsing response from {used_provider}", file=sys.stderr)
        print(result[:2000], file=sys.stderr)
        sys.exit(1)

    summary = plan.get("summary", "auto-ingest")
    actions = plan.get("actions", [])
    print(f"\nPlan ({used_provider}): {summary}  |  {len(actions)} actions")

    # 7. Apply
    apply_actions(actions, wiki_dir)

    # 8. Log
    today = datetime.now().strftime("%Y-%m-%d")
    log_entry = f"""
## [{today}] auto-ingest ({used_provider}) | {summary}

Triggered by GitHub Actions push. Provider: {used_provider}.
{len(changed)} files, {len(actions)} actions applied.
"""
    with open(os.path.join(wiki_dir, "wiki/log.md"), 'a', encoding='utf-8') as f:
        f.write(log_entry)

    # 9. Commit
    git_commit_and_push(wiki_dir, f"auto-ingest ({used_provider}): {summary}")


if __name__ == "__main__":
    main()
