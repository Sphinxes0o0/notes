#!/usr/bin/env python3
"""Wiki auto-ingest for GitHub Actions. Dual provider: MiniMax + Copilot fallback."""

import os, sys, json, hashlib, subprocess, argparse
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

WIKI_SYSTEM_PROMPT = """You are an LLM Wiki maintenance agent. Integrate raw source files into a structured markdown wiki.

## Wiki Convention
- wiki/sources/<slug>.md — source summary pages
- wiki/entities/<domain>/<slug>.md — concept/entity pages
- wiki/<domain>-index.md — module indexes
- wiki/home.md — global navigation

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
- Use [[wikilinks]]. Minimum 2 cross-links per entity page.
- Keep pages <200 lines.
- Write in Chinese for Chinese sources, English for English sources.
- DON'T duplicate — check home.md and log.md first.

### Output: VALID JSON only
```json
{
  "summary": "one-line summary",
  "actions": [
    {"type": "CREATE", "path": "wiki/sources/foo.md", "content": "..."},
    {"type": "SKIP", "path": "already/covered.md"}
  ]
}
```"""

# ── MiniMax ──
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
        "temperature": 0.3, "max_tokens": 16000
    }).encode()
    req = Request(f"{MINIMAX_BASE}/chat/completions", data=body, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })
    try:
        with urlopen(req, timeout=180) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]
    except URLError as e:
        body = ""
        if hasattr(e, 'read'):
            try: body = e.read().decode()[:500]
            except: pass
        raise RuntimeError(f"MiniMax {e.code if hasattr(e,'code') else 'error'}: {body}")

# ── Copilot ──
def call_copilot(system_prompt: str, user_message: str) -> str:
    """Call GitHub Copilot via gh api (Actions-native, uses GITHUB_TOKEN)."""
    body = json.dumps({
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3, "max_tokens": 16000
    })
    result = subprocess.run(
        ["gh", "api", "copilot/chat/completions",
         "--method", "POST", "--input", "-",
         "--jq", ".choices[0].message.content"],
        input=body, capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh copilot failed (exit {result.returncode}): {result.stderr[:300]}")
    out = result.stdout.strip()
    if not out:
        raise RuntimeError("gh copilot empty output")
    return out

PROVIDERS = {"minimax": call_minimax, "copilot": call_copilot}

def call_llm(system_prompt, user_message, providers):
    errors = []
    for name in providers:
        fn = PROVIDERS.get(name)
        if not fn:
            errors.append(f"{name}: unknown"); continue
        try:
            print(f"  Trying {name}...", file=sys.stderr)
            result = fn(system_prompt, user_message)
            print(f"  {name} OK", file=sys.stderr)
            return result, name
        except Exception as e:
            print(f"  {name} FAIL: {e}", file=sys.stderr)
            errors.append(f"{name}: {e}")
    raise RuntimeError("All providers failed:\n" + "\n".join(errors))

# ── File utils ──
def read_file_safe(path, max_bytes=50000):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read(max_bytes)
            return c + "\n\n[TRUNCATED]" if len(c) >= max_bytes else c
    except: return "[CANNOT READ]"

def compute_manifest(raw_dir):
    m = {}
    for root, dirs, files in os.walk(raw_dir):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, raw_dir)
            try:
                with open(fp, 'rb') as fh: m[rel] = hashlib.md5(fh.read()).hexdigest()
            except: m[rel] = "UNREADABLE"
    return m

def load_manifest(path):
    return json.load(open(path)) if os.path.exists(path) else {}

def save_manifest(m, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(m, open(path, 'w'), indent=2)

def get_changed_files(raw_dir, manifest_path):
    cur = compute_manifest(raw_dir)
    old = load_manifest(manifest_path)
    changed = [(("NEW" if p not in old else "CHANGED"), p) for p, h in cur.items() if p not in old or old[p] != h]
    save_manifest(cur, manifest_path)
    return changed

def apply_actions(actions, wiki_dir):
    for a in actions:
        typ = a.get("type")
        path = os.path.join(wiki_dir, a["path"])
        if typ == "CREATE":
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f: f.write(a.get("content", ""))
            print(f"  CREATE {a['path']}")
        elif typ == "SKIP":
            print(f"  SKIP {a.get('path', '?')}")

def git_commit_and_push(wiki_dir, msg):
    subprocess.run(["git", "-C", wiki_dir, "config", "user.name", "hermes-wiki-bot"], check=True)
    subprocess.run(["git", "-C", wiki_dir, "config", "user.email", "wiki-bot@hermes.local"], check=True)
    subprocess.run(["git", "-C", wiki_dir, "add", "-A"], check=True)
    r = subprocess.run(["git", "-C", wiki_dir, "diff", "--cached", "--quiet"], capture_output=True)
    if r.returncode == 0: print("No changes"); return
    subprocess.run(["git", "-C", wiki_dir, "commit", "-m", msg], check=True)
    subprocess.run(["git", "-C", wiki_dir, "push"], check=True)
    print(f"Committed: {msg}")

# ── Main ──
def main():
    p = argparse.ArgumentParser()
    p.add_argument("wiki_dir"); p.add_argument("raw_subdir")
    p.add_argument("--provider", choices=["minimax", "copilot"])
    args = p.parse_args()

    raw_dir = os.path.join(args.wiki_dir, "raw", args.raw_subdir)
    if not os.path.isdir(raw_dir):
        print(f"ERROR: {raw_dir} not found", file=sys.stderr); sys.exit(1)

    changed = get_changed_files(raw_dir, os.path.join(args.wiki_dir, ".raw_manifest.json"))
    if not changed: print("No changes."); return
    print(f"{len(changed)} changed files", file=sys.stderr)

    files_content = []
    for status, path in changed:
        files_content.append(f"## [{status}] {path}\n\n{read_file_safe(os.path.join(raw_dir, path), 30000)}")

    home = read_file_safe(os.path.join(args.wiki_dir, "wiki/home.md"), 10000)
    log_tail = read_file_safe(os.path.join(args.wiki_dir, "wiki/log.md"), 5000)

    user_msg = f"""## Wiki Context
### home.md
{home}
### log.md (recent)
{log_tail}

## Changed Files
{chr(10).join(files_content)}

## Task
Analyze these files. Create source/entity pages for NEW content.
Update indexes. Skip already-covered. Output JSON action plan."""

    override = os.getenv("OVERRIDE_PROVIDER", "")
    providers = [override] if override else ([args.provider] if args.provider else ["minimax", "copilot"])
    print(f"Providers: {' -> '.join(providers)}", file=sys.stderr)
    result, used = call_llm(WIKI_SYSTEM_PROMPT, user_msg, providers)

    try:
        text = result.strip()
        if text.startswith("```"): text = text.split("\n", 1)[1]
        if text.endswith("```"): text = text[:-3]
        plan = json.loads(text)
    except json.JSONDecodeError:
        print(f"ERROR parsing {used} response", file=sys.stderr)
        print(result[:2000], file=sys.stderr); sys.exit(1)

    summary = plan.get("summary", "auto-ingest")
    actions = plan.get("actions", [])
    print(f"\nPlan ({used}): {summary}  |  {len(actions)} actions")
    apply_actions(actions, args.wiki_dir)

    today = datetime.now().strftime("%Y-%m-%d")
    with open(os.path.join(args.wiki_dir, "wiki/log.md"), 'a', encoding='utf-8') as f:
        f.write(f"\n## [{today}] auto-ingest ({used}) | {summary}\n"
                f"GitHub Actions. {len(changed)} files, {len(actions)} actions.\n")

    git_commit_and_push(args.wiki_dir, f"auto-ingest ({used}): {summary}")

if __name__ == "__main__":
    main()
