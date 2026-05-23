     1|#!/usr/bin/env python3
     2|"""Wiki auto-ingest for GitHub Actions. Dual provider: MiniMax + Copilot fallback."""
     3|
     4|import os, sys, json, hashlib, subprocess, argparse
     5|from datetime import datetime
     6|from urllib.request import Request, urlopen
     7|from urllib.error import URLError
     8|
     9|WIKI_SYSTEM_PROMPT = """You are an LLM Wiki maintenance agent. Integrate raw source files into a structured markdown wiki.
    10|
    11|## Wiki Convention
    12|- wiki/sources/<slug>.md — source summary pages
    13|- wiki/entities/<domain>/<slug>.md — concept/entity pages
    14|- wiki/<domain>-index.md — module indexes
    15|- wiki/home.md — global navigation
    16|
    17|### Page frontmatter (required)
    18|```yaml
    19|---
    20|type: source | entity | index
    21|tags: [tag1, tag2]
    22|created: YYYY-MM-DD
    23|sources: [source-slug]
    24|---
    25|```
    26|
    27|### Rules
    28|- Use [[wikilinks]]. Minimum 2 cross-links per entity page.
    29|- Keep pages <200 lines.
    30|- Write in Chinese for Chinese sources, English for English sources.
    31|- DON'T duplicate — check home.md and log.md first.
    32|
    33|### Output: VALID JSON only
    34|```json
    35|{
    36|  "summary": "one-line summary",
    37|  "actions": [
    38|    {"type": "CREATE", "path": "wiki/sources/foo.md", "content": "..."},
    39|    {"type": "SKIP", "path": "already/covered.md"}
    40|  ]
    41|}
    42|```"""
    43|
    44|# ── MiniMax ──
    45|MINIMAX_BASE = "https://api.minimaxi.com/v1"
    46|MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7-highspeed")
    47|
    48|def call_minimax(system_prompt: str, user_message: str) -> str:
    49|    api_key = os.getenv("MINIMAX_CN_API_KEY", "")
    50|    if not api_key:
    51|        raise RuntimeError("MINIMAX_CN_API_KEY not set")
    52|    body = json.dumps({
    53|        "model": MINIMAX_MODEL,
    54|        "messages": [
    55|            {"role": "system", "content": system_prompt},
    56|            {"role": "user", "content": user_message}
    57|        ],
    58|        "temperature": 0.3, "max_tokens": 8192,
    59|        "thinking": False
    60|    }).encode()
    61|    req = Request(f"{MINIMAX_BASE}/chat/completions", data=body, headers={
    62|        "Authorization": f"Bearer {api_key}",
    63|        "Content-Type": "application/json"
    64|    })
    65|    try:
    66|        with urlopen(req, timeout=180) as resp:
    67|            return json.loads(resp.read())["choices"][0]["message"]["content"]
    68|    except URLError as e:
    69|        body = ""
    70|        if hasattr(e, 'read'):
    71|            try: body = e.read().decode()[:500]
    72|            except: pass
    73|        raise RuntimeError(f"MiniMax {e.code if hasattr(e,'code') else 'error'}: {body}")
    74|
    75|# ── Copilot ──
    76|def call_copilot(system_prompt: str, user_message: str) -> str:
    77|    """Call GitHub Copilot via gh api (Actions-native, uses GITHUB_TOKEN)."""
    78|    body = json.dumps({
    79|        "messages": [
    80|            {"role": "system", "content": system_prompt},
    81|            {"role": "user", "content": user_message}
    82|        ],
    83|        "temperature": 0.3, "max_tokens": 16000
    84|    })
    85|    result = subprocess.run(
    86|        ["gh", "api", "copilot/chat/completions",
    87|         "--method", "POST", "--input", "-",
    88|         "--jq", ".choices[0].message.content"],
    89|        input=body, capture_output=True, text=True, timeout=300
    90|    )
    91|    if result.returncode != 0:
    92|        raise RuntimeError(f"gh copilot failed (exit {result.returncode}): {result.stderr[:300]}")
    93|    out = result.stdout.strip()
    94|    if not out:
    95|        raise RuntimeError("gh copilot empty output")
    96|    return out
    97|
    98|PROVIDERS = {"deepseek": call_deepseek, "minimax": call_minimax, "copilot": call_copilot}
    99|
   100|def call_llm(system_prompt, user_message, providers):
   101|    errors = []
   102|    for name in providers:
   103|        fn = PROVIDERS.get(name)
   104|        if not fn:
   105|            errors.append(f"{name}: unknown"); continue
   106|        try:
   107|            print(f"  Trying {name}...", file=sys.stderr)
   108|            result = fn(system_prompt, user_message)
   109|            print(f"  {name} OK", file=sys.stderr)
   110|            return result, name
   111|        except Exception as e:
   112|            print(f"  {name} FAIL: {e}", file=sys.stderr)
   113|            errors.append(f"{name}: {e}")
   114|    raise RuntimeError("All providers failed:\n" + "\n".join(errors))
   115|
   116|# ── File utils ──
   117|def read_file_safe(path, max_bytes=50000):
   118|    try:
   119|        with open(path, 'r', encoding='utf-8') as f:
   120|            c = f.read(max_bytes)
   121|            return c + "\n\n[TRUNCATED]" if len(c) >= max_bytes else c
   122|    except: return "[CANNOT READ]"
   123|
   124|def compute_manifest(raw_dir):
   125|    m = {}
   126|    for root, dirs, files in os.walk(raw_dir):
   127|        dirs[:] = [d for d in dirs if d != '.git']
   128|        for f in files:
   129|            fp = os.path.join(root, f)
   130|            rel = os.path.relpath(fp, raw_dir)
   131|            try:
   132|                with open(fp, 'rb') as fh: m[rel] = hashlib.md5(fh.read()).hexdigest()
   133|            except: m[rel] = "UNREADABLE"
   134|    return m
   135|
   136|def load_manifest(path):
   137|    return json.load(open(path)) if os.path.exists(path) else {}
   138|
   139|def save_manifest(m, path):
   140|    os.makedirs(os.path.dirname(path), exist_ok=True)
   141|    json.dump(m, open(path, 'w'), indent=2)
   142|
   143|def get_changed_files(raw_dir, manifest_path):
   144|    cur = compute_manifest(raw_dir)
   145|    old = load_manifest(manifest_path)
   146|    changed = [(("NEW" if p not in old else "CHANGED"), p) for p, h in cur.items() if p not in old or old[p] != h]
   147|    save_manifest(cur, manifest_path)
   148|    return changed
   149|
   150|def apply_actions(actions, wiki_dir):
   151|    for a in actions:
   152|        typ = a.get("type")
   153|        path = os.path.join(wiki_dir, a["path"])
   154|        if typ == "CREATE":
   155|            os.makedirs(os.path.dirname(path), exist_ok=True)
   156|            with open(path, 'w', encoding='utf-8') as f: f.write(a.get("content", ""))
   157|            print(f"  CREATE {a['path']}")
   158|        elif typ == "SKIP":
   159|            print(f"  SKIP {a.get('path', '?')}")
   160|
   161|def git_commit_and_push(wiki_dir, msg):
   162|    subprocess.run(["git", "-C", wiki_dir, "config", "user.name", "hermes-wiki-bot"], check=True)
   163|    subprocess.run(["git", "-C", wiki_dir, "config", "user.email", "wiki-bot@hermes.local"], check=True)
   164|    subprocess.run(["git", "-C", wiki_dir, "add", "-A"], check=True)
   165|    r = subprocess.run(["git", "-C", wiki_dir, "diff", "--cached", "--quiet"], capture_output=True)
   166|    if r.returncode == 0: print("No changes"); return
   167|    subprocess.run(["git", "-C", wiki_dir, "commit", "-m", msg], check=True)
   168|    subprocess.run(["git", "-C", wiki_dir, "push"], check=True)
   169|    print(f"Committed: {msg}")
   170|
   171|# ── Main ──
   172|def main():
   173|    p = argparse.ArgumentParser()
   174|    p.add_argument("wiki_dir"); p.add_argument("raw_subdir")
   175|    p.add_argument("--provider", choices=["deepseek", "minimax", "copilot"])
   176|    args = p.parse_args()
   177|
   178|    raw_dir = os.path.join(args.wiki_dir, "raw", args.raw_subdir)
   179|    if not os.path.isdir(raw_dir):
   180|        print(f"ERROR: {raw_dir} not found", file=sys.stderr); sys.exit(1)
   181|
   182|    changed = get_changed_files(raw_dir, os.path.join(args.wiki_dir, ".raw_manifest.json"))
   183|    if not changed: print("No changes."); return
   184|    print(f"{len(changed)} changed files", file=sys.stderr)
   185|
   186|    # Limit to MAX_FILES to stay within MiniMax context (204K)
   187|    MAX_FILES = 10
   188|    MAX_BYTES_PER_FILE = 5000
   189|    if len(changed) > MAX_FILES:
   190|        print(f"Limiting to first {MAX_FILES} of {len(changed)} changed files", file=sys.stderr)
   191|        changed = changed[:MAX_FILES]
   192|
   193|    files_content = []
   194|    for status, path in changed:
   195|        files_content.append(f"## [{status}] {path}\n\n{read_file_safe(os.path.join(raw_dir, path), MAX_BYTES_PER_FILE)}")
   196|
   197|    home = read_file_safe(os.path.join(args.wiki_dir, "wiki/home.md"), 10000)
   198|    log_tail = read_file_safe(os.path.join(args.wiki_dir, "wiki/log.md"), 5000)
   199|
   200|    user_msg = f"""## Wiki Context
   201|### home.md
   202|{home}
   203|### log.md (recent)
   204|{log_tail}
   205|
   206|## Changed Files
   207|{chr(10).join(files_content)}
   208|
   209|## Task
   210|Analyze these files. Create source/entity pages for NEW content.
   211|Update indexes. Skip already-covered. Output JSON action plan."""
   212|
   213|    override = os.getenv("OVERRIDE_PROVIDER", "")
   214|    providers = [override] if override else ([args.provider] if args.provider else ["deepseek", "minimax", "copilot"])
   215|    print(f"Providers: {' -> '.join(providers)}", file=sys.stderr)
   216|    result, used = call_llm(WIKI_SYSTEM_PROMPT, user_msg, providers)
   217|
   218|    try:
   219|        text = result.strip()
   220|        # Strip think tags (MiniMax reasoning mode)
   221|        think_open = chr(60) + "think" + chr(62)
   222|        think_close = chr(60) + "/think" + chr(62)
   223|        if think_open in text:
   224|            text = text.split(think_close, 1)[-1]
   225|        text = text.replace(think_open, "").replace(think_close, "").strip()
   226|        if text.startswith("```"): text = text.split("\n", 1)[1]
   227|        if text.endswith("```"): text = text[:-3]
   228|        plan = json.loads(text)
   229|    except json.JSONDecodeError:
   230|        print(f"ERROR parsing {used} response", file=sys.stderr)
   231|        print(result[:2000], file=sys.stderr); sys.exit(1)
   232|
   233|    summary = plan.get("summary", "auto-ingest")
   234|    actions = plan.get("actions", [])
   235|    print(f"\nPlan ({used}): {summary}  |  {len(actions)} actions")
   236|    apply_actions(actions, args.wiki_dir)
   237|
   238|    today = datetime.now().strftime("%Y-%m-%d")
   239|    with open(os.path.join(args.wiki_dir, "wiki/log.md"), 'a', encoding='utf-8') as f:
   240|        f.write(f"\n## [{today}] auto-ingest ({used}) | {summary}\n"
   241|                f"GitHub Actions. {len(changed)} files, {len(actions)} actions.\n")
   242|
   243|    git_commit_and_push(args.wiki_dir, f"auto-ingest ({used}): {summary}")
   244|
   245|if __name__ == "__main__":
   246|    main()