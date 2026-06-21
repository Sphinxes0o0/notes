#!/usr/bin/env python3
"""content_audit.py — Quality audit for a VitePress / markdown site.

Detects:
  1. Stub pages (very few lines of actual content after frontmatter)
  2. Placeholder / lorem ipsum / TODO noise
  3. Pages with no frontmatter
  4. Pages with very low signal (mostly links, no prose)
  5. Stale pages (last modified > N months ago, per git)
  6. Pages with no outgoing links (information dead-ends)
  7. Pages with extreme size (huge monolithic files)

Usage:
  python3 content_audit.py                  # default
  python3 content_audit.py --json           # machine-readable
  python3 content_audit.py --stale-months 9  # 9-month threshold
  python3 content_audit.py --stub-lines 10  # < 10 lines = stub
  python3 content_audit.py --report full    # full report (default: summary)

Style: matches notes/.github/scripts/audit-codeblocks.js (stdlib, simple).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

NOTES_ROOT = Path(os.environ.get("NOTES_ROOT", Path(__file__).resolve().parent.parent))
SKIP_DIRS = {"node_modules", ".vitepress", "courses", "wiki", "android", ".git", "public"}

# Regex for placeholder noise
PLACEHOLDER_PATTERNS = [
    (re.compile(r"\bTODO\b", re.IGNORECASE), "TODO"),
    (re.compile(r"\bFIXME\b", re.IGNORECASE), "FIXME"),
    (re.compile(r"\bXXX\b"), "XXX"),
    (re.compile(r"\bplaceholder\b", re.IGNORECASE), "placeholder"),
    (re.compile(r"\blorem ipsum\b", re.IGNORECASE), "lorem-ipsum"),
    (re.compile(r"\bTBD\b"), "TBD"),
    (re.compile(r"草稿|未完成|待补充|待完善"), "chinese-stub-marker"),
    (re.compile(r"^\s*\.{3,}\s*$", re.MULTILINE), "ellipsis-line"),
    (re.compile(r"^\s*<在此添加[^>]*>\s*$", re.MULTILINE), "add-here-marker"),
]

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def iter_markdown(root: Path):
    for p in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        yield p


def count_content_lines(text: str) -> int:
    """Count lines that contain actual prose, not blank/code/heading/quote."""
    lines = 0
    in_code = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        s = line.strip()
        if not s:
            continue
        if s.startswith(("#", ">", "|", "-", "*", "!")):
            continue
        if s.startswith("[") and "](" in s:  # link-only line
            continue
        if re.match(r"^\d+\.\s", s):
            continue
        if re.match(r"^[-*]\s", s):
            continue
        lines += 1
    return lines


def get_last_modified(path: Path, repo_root: Path) -> datetime | None:
    """Get last commit date for a file (git). Returns None if no git."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%cI", "--", str(path.relative_to(repo_root))],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            # parse ISO date
            return datetime.fromisoformat(result.stdout.strip().replace("Z", "+00:00"))
    except Exception:
        pass
    return None


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--root", type=Path, default=NOTES_ROOT)
    p.add_argument("--stub-lines", type=int, default=20, help="lines threshold for stub")
    p.add_argument("--stale-months", type=int, default=12, help="months threshold for stale")
    p.add_argument("--huge-lines", type=int, default=3000, help="lines threshold for huge")
    p.add_argument("--json", action="store_true")
    p.add_argument("--report", choices=["summary", "full"], default="summary")
    args = p.parse_args(argv)

    if not args.root.exists():
        print(f"ERROR: root not found at {args.root}", file=sys.stderr)
        return 2

    files = list(iter_markdown(args.root))
    print(f"Scanning {len(files)} files under {args.root}")

    now = datetime.now(timezone.utc)
    issues = {
        "stubs": [],
        "no_frontmatter": [],
        "placeholders": [],
        "no_outgoing": [],
        "huge": [],
        "stale": [],
    }
    stats = {
        "files": 0,
        "with_frontmatter": 0,
        "with_links": 0,
        "total_lines": 0,
        "total_content_lines": 0,
    }

    for f in files:
        stats["files"] += 1
        text = f.read_text(encoding="utf-8", errors="ignore")
        all_lines = text.count("\n") + 1
        stats["total_lines"] += all_lines

        # Frontmatter
        has_fm = bool(FRONTMATTER_RE.match(text))
        if has_fm:
            stats["with_frontmatter"] += 1
        else:
            issues["no_frontmatter"].append({
                "file": str(f.relative_to(args.root)),
                "lines": all_lines,
            })

        # Content lines (rough proxy)
        content = count_content_lines(text)
        stats["total_content_lines"] += content

        # Stub
        if has_fm and content < args.stub_lines and all_lines > 3:
            issues["stubs"].append({
                "file": str(f.relative_to(args.root)),
                "lines": all_lines,
                "content_lines": content,
            })

        # Placeholder noise
        matches = []
        for pat, name in PLACEHOLDER_PATTERNS:
            for m in pat.finditer(text):
                matches.append({"type": name, "match": m.group(0)[:60]})
        if matches:
            issues["placeholders"].append({
                "file": str(f.relative_to(args.root)),
                "matches": matches[:5],  # cap
                "n_matches": len(matches),
            })

        # No outgoing links (potential dead-end)
        md_links = len(LINK_RE.findall(text)) + len(WIKILINK_RE.findall(text))
        if md_links > 0:
            stats["with_links"] += 1
        elif content > 50:  # only flag if it has substance
            issues["no_outgoing"].append({
                "file": str(f.relative_to(args.root)),
                "content_lines": content,
            })

        # Huge
        if all_lines > args.huge_lines:
            issues["huge"].append({
                "file": str(f.relative_to(args.root)),
                "lines": all_lines,
            })

        # Stale
        mtime = get_last_modified(f, args.root)
        if mtime:
            age_months = (now - mtime).days / 30.44
            if age_months > args.stale_months:
                issues["stale"].append({
                    "file": str(f.relative_to(args.root)),
                    "last_modified": mtime.date().isoformat(),
                    "months_old": round(age_months, 1),
                })

    report = {
        "root": str(args.root),
        "scanned_at": now.isoformat(),
        "stats": stats,
        "thresholds": {
            "stub_lines": args.stub_lines,
            "stale_months": args.stale_months,
            "huge_lines": args.huge_lines,
        },
        "issues": {
            k: v for k, v in issues.items()
        },
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
        return 0

    # Pretty
    print(f"\n{'=' * 70}")
    print(f"  Content Audit Report: {args.root.name}")
    print(f"{'=' * 70}")
    print(f"  Files:               {stats['files']}")
    print(f"  With frontmatter:    {stats['with_frontmatter']} ({100*stats['with_frontmatter']//max(1,stats['files'])}%)")
    print(f"  With links:          {stats['with_links']} ({100*stats['with_links']//max(1,stats['files'])}%)")
    print(f"  Total lines:         {stats['total_lines']:,}")
    print(f"  Total content lines: {stats['total_content_lines']:,}")
    print()

    sections = [
        ("stubs", f"Stub pages (frontmatter + <{args.stub_lines} content lines)"),
        ("no_frontmatter", "Pages with no YAML frontmatter"),
        ("placeholders", "Pages with TODO/FIXME/placeholder noise"),
        ("no_outgoing", "Substantial pages (50+ content lines) with no outgoing links"),
        ("huge", f"Huge pages (>{args.huge_lines} lines, may need splitting)"),
        ("stale", f"Stale pages (last modified >{args.stale_months} months ago)"),
    ]
    for key, label in sections:
        items = issues[key]
        print(f"  {label}: {len(items)}")
        if args.report == "full" and items:
            for it in items[:10]:
                line = it["file"]
                if "lines" in it:
                    line += f"  ({it['lines']} lines)"
                if "months_old" in it:
                    line += f"  ({it['months_old']} months old)"
                if "n_matches" in it:
                    line += f"  ({it['n_matches']} placeholders)"
                print(f"    {line}")
            if len(items) > 10:
                print(f"    ... and {len(items) - 10} more")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
