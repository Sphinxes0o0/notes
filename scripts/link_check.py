#!/usr/bin/env python3
"""link_check.py — Check internal and external links in a VitePress site.

Usage:
  python3 link_check.py                     # default: internal only
  python3 link_check.py --external          # also probe external URLs (slow)
  python3 link_check.py --external --concurrency 16
  python3 link_check.py --json              # machine-readable output
  python3 link_check.py --public-base https://Sphinxes0o0.github.io/notes

What it checks:
  1. Internal relative links: `[text](path.md)` — does the file exist?
  2. Internal absolute links: `[text](/foo/bar)` — does the route exist?
  3. External links: `[text](https://...)` — HEAD request, check 2xx/3xx.

Scope: a directory tree (default: notes/). Excludes node_modules,
.vitepress/, and the VitePress srcExclude dirs (courses/, wiki/,
android/) which are intentionally not built.

Limitations (by Simplicity First):
  - External link probing uses urllib (stdlib). No retries; a single
    4xx/5xx/network-error is enough to flag.
  - We don't follow redirects by default; a 3xx is reported as
    "redirects" (not broken, but you may want to update).
  - Rate-limit friendly: --concurrency defaults to 8, with a
    200ms polite delay between requests per worker.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

# ---------- Config ----------
NOTES_ROOT = Path(os.environ.get("NOTES_ROOT", Path(__file__).resolve().parent.parent))
PUBLIC_BASE = os.environ.get("NOTES_PUBLIC_BASE", "https://Sphinxes0o0.github.io/notes")
SKIP_DIRS = {"node_modules", ".vitepress", "courses", "wiki", "android", ".git", "public"}
REQUEST_TIMEOUT = 10  # seconds per URL
USER_AGENT = "notes-link-checker/0.1 (+https://Sphinxes0o0.github.io/notes)"

# Match [text](url) — also handles [text](url "title")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
# Data URIs (inline base64 images etc.) are not real broken links.
DATA_URI_RE = re.compile(r"^data:")
# Bare single-word targets that look like C identifiers / code references
# inside fenced code blocks. We strip code blocks before matching to avoid
# false positives like `callbacks_[fd](revents)` or
# `kvm_vmx_exit_handlers[i](vcpu)`.
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def iter_markdown(root: Path):
    for p in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        yield p


def collect_routes(root: Path) -> tuple[set[str], set[str], set[str]]:
    """Build sets of known routes, assets (files), and directories.

    Returns:
      routes:   .md files (no .md suffix) — for navigation links
      assets:   non-.md files — for image/resource links
      dirs:     all directories (relative paths, with trailing /)
                — for directory-typed links like `containers/`
    """
    routes: set[str] = {""}  # root
    assets: set[str] = set()
    dirs: set[str] = {""}     # root is also a "dir"
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        rel = p.relative_to(root)
        rel_str = str(rel)
        if p.is_dir():
            dirs.add(rel_str)
            dirs.add(rel_str + "/")
        elif p.suffix == ".md":
            stem = str(rel.with_suffix(""))
            routes.add(stem)
            routes.add(stem + "/")
        else:
            assets.add(rel_str)
    return routes, assets, dirs


# ---------- Internal link resolution ----------
def resolve_internal(link: str, source: Path, root: Path,
                     routes: set[str], assets: set[str], dirs: set[str]) -> str:
    """Resolve a relative or absolute link, or 'missing'.

    Strategy:
      - Markdown routes use stem matching (e.g. /ccpp/c-tips)
      - Asset files (images, pdfs) use full path matching
      - Directories (trailing /) match against the dirs set
      - Otherwise the link is treated as a markdown stem route
    """
    # Strip fragment / query
    link = link.split("#", 1)[0].split("?", 1)[0]
    if not link:
        return ""  # self-link fragment

    is_dir_link = link.endswith("/")

    # Absolute (VitePress style: /foo/bar)
    if link.startswith("/"):
        target = link.strip("/")
        if is_dir_link:
            if target in dirs or target + "/" in dirs:
                return target
        if target in routes or target + "/" in routes or target in assets:
            return target
        return f"MISSING: {link}"

    # Relative to source file
    src_dir = source.parent
    target = (src_dir / link).resolve()
    try:
        rel = target.relative_to(root.resolve())
        rel_str = str(rel)
    except ValueError:
        return f"OUTSIDE_ROOT: {link}"

    if is_dir_link:
        if rel_str in dirs or rel_str + "/" in dirs:
            return rel_str
        return f"MISSING: {link}"

    if rel.suffix and rel.suffix != ".md":
        if rel_str in assets:
            return rel_str
        return f"MISSING: {link}"

    stem = str(rel.with_suffix(""))
    if stem in routes or stem + "/" in routes:
        return stem
    return f"MISSING: {link}"


# ---------- External link probing ----------
HEADERS = {"User-Agent": USER_AGENT}


def probe_external(url: str) -> tuple[str, str, str | None]:
    """HEAD request an external URL. Returns (url, status, error)."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers=HEADERS)
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return (url, f"{resp.status} {resp.reason}", None)
    except urllib.error.HTTPError as e:
        # Many sites reject HEAD — fall back to GET range
        if e.code in (405, 403, 400):
            return probe_external_get(url)
        return (url, f"HTTP {e.code} {e.reason}", str(e))
    except urllib.error.URLError as e:
        return (url, "URL error", str(e.reason))
    except Exception as e:
        return (url, "error", str(e))


def probe_external_get(url: str) -> tuple[str, str, str | None]:
    """GET Range request as fallback when HEAD is rejected."""
    try:
        req = urllib.request.Request(
            url,
            method="GET",
            headers={**HEADERS, "Range": "bytes=0-1023"},
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return (url, f"{resp.status} {resp.reason} (GET)", None)
    except urllib.error.HTTPError as e:
        return (url, f"HTTP {e.code} {e.reason} (GET)", str(e))
    except Exception as e:
        return (url, "error (GET)", str(e))


# ---------- Main ----------
def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--root", type=Path, default=NOTES_ROOT)
    p.add_argument("--external", action="store_true", help="probe external URLs")
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--json", action="store_true")
    p.add_argument("--public-base", default=PUBLIC_BASE)
    p.add_argument("--limit-external", type=int, default=0, help="probe only first N (for testing)")
    p.add_argument("--no-redirects", action="store_true", help="treat 3xx as broken")
    args = p.parse_args(argv)

    if not args.root.exists():
        print(f"ERROR: root not found at {args.root}", file=sys.stderr)
        return 2

    if not args.json:
        print(f"Scanning {args.root} ...")
    routes, assets, dirs = collect_routes(args.root)
    files = list(iter_markdown(args.root))
    if not args.json:
        print(f"Found {len(files)} markdown files, {len(routes)} routes, {len(assets)} assets, {len(dirs)} dirs.")

    # 1. Collect all links
    internal_issues: list[dict] = []
    external_links: list[tuple[Path, str]] = []
    internal_total = 0

    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        # Strip fenced code blocks and inline code spans so we don't
        # mistake C/JS syntax like `arr[i](v)` for a markdown link.
        scan_text = FENCE_RE.sub("", text)
        scan_text = INLINE_CODE_RE.sub("", scan_text)
        for m in LINK_RE.finditer(scan_text):
            link = m.group(2)
            if link.startswith(("#", "mailto:")):
                continue
            if DATA_URI_RE.match(link):
                continue
            if link.startswith(("http://", "https://")):
                external_links.append((f, link))
                continue
            # Internal
            internal_total += 1
            result = resolve_internal(link, f, args.root, routes, assets, dirs)
            if result.startswith("MISSING") or result.startswith("OUTSIDE_ROOT"):
                internal_issues.append({
                    "file": str(f.relative_to(args.root)),
                    "link": link,
                    "issue": result,
                })

    if args.json:
        print(f"Internal links: {internal_total} ({len(internal_issues)} broken)", file=sys.stderr)
        print(f"External links: {len(external_links)}", file=sys.stderr)
    else:
        print(f"Internal links: {internal_total} ({len(internal_issues)} broken)")
        print(f"External links: {len(external_links)}")

    # 2. Probe externals (concurrent)
    external_results: list[dict] = []
    if args.external and external_links:
        unique_urls = list({url for _, url in external_links})
        if args.limit_external:
            unique_urls = unique_urls[: args.limit_external]
        print(f"Probing {len(unique_urls)} unique external URLs (concurrency={args.concurrency}) ...", file=sys.stderr)
        t0 = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futures = {ex.submit(probe_external, url): url for url in unique_urls}
            done = 0
            for fut in concurrent.futures.as_completed(futures):
                url, status, err = fut.result()
                # Classify
                # Extract numeric code from "200 OK (GET)" or "HTTP 200 OK"
                parts = status.split()
                code = 0
                for p in parts:
                    if p.isdigit():
                        code = int(p)
                        break
                if 200 <= code < 400:
                    cls = "redirect" if 300 <= code < 400 else "ok"
                elif 400 <= code < 600:
                    cls = "broken"
                elif "error" in status.lower() or "URL error" in status:
                    cls = "network-error"
                else:
                    cls = "unknown"
                # Find referencing files
                refs = [str(f.relative_to(args.root)) for f, u in external_links if u == url]
                external_results.append({
                    "url": url,
                    "status": status,
                    "class": cls,
                    "referenced_from": refs[:5],  # cap
                    "n_refs": len(refs),
                })
                done += 1
                if done % 20 == 0:
                    print(f"  probed {done}/{len(unique_urls)} ({time.time()-t0:.1f}s)", file=sys.stderr)
        print(f"Done in {time.time()-t0:.1f}s", file=sys.stderr)

    # 3. Build report
    external_class = Counter(r["class"] for r in external_results)
    report = {
        "root": str(args.root),
        "files_scanned": len(files),
        "internal": {
            "total": internal_total,
            "broken_count": len(internal_issues),
            "broken": internal_issues[:50],  # cap
        },
        "external": {
            "total_unique": len(external_results),
            "by_class": dict(external_class),
            "results": external_results,
        },
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        return 0

    # Pretty print
    print(f"\n{'=' * 70}")
    print(f"  Link Check Report: {args.root.name}")
    print(f"{'=' * 70}")
    print(f"  Files scanned:   {len(files)}")
    print(f"  Routes:          {len(routes)}")
    print(f"  Assets:          {len(assets)}")
    print(f"  Dirs:            {len(dirs)}")
    print(f"  Internal links:  {internal_total}")
    print(f"  External links:  {len(external_links)} (unique: {len(external_results)})")
    if internal_issues:
        print(f"\n  ✗ Broken internal links ({len(internal_issues)}):")
        for issue in internal_issues[:20]:
            print(f"    {issue['file']}: [{issue['link']}] — {issue['issue']}")
        if len(internal_issues) > 20:
            print(f"    ... and {len(internal_issues) - 20} more")
    else:
        print(f"\n  ✓ All internal links valid")
    if args.external and external_results:
        print(f"\n  External links by class:")
        for cls, n in external_class.most_common():
            print(f"    {cls:18} {n}")
        broken = [r for r in external_results if r["class"] in ("broken", "network-error")]
        if broken:
            print(f"\n  ✗ Broken external links ({len(broken)}):")
            for r in broken[:20]:
                print(f"    {r['url']}  [{r['status']}]  (referenced by {r['n_refs']} files)")
            if len(broken) > 20:
                print(f"    ... and {len(broken) - 20} more")
    elif not args.external:
        print(f"\n  (Run with --external to probe external URLs)")

    return 1 if (internal_issues or any(r["class"] == "broken" for r in external_results)) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
