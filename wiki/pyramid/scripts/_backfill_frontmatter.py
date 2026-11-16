#!/usr/bin/env python3
"""One-shot backfill for missing 'created' / 'tags' frontmatter fields.

Targets: lint_wiki.py frontmatter_issues from /tmp/lint_results.json.
Idempotent: re-running on already-patched files is a no-op.

Strategy
--------
- Only touches files that appear in the lint report with exactly
  "missing 'created' field" or "missing 'tags' field". Does NOT touch
  "empty 'tags' field" (those are intentional `tags: []`) or
  "invalid 'created' date" (those need LLM review).
- For `created`: prefers existing `ingested: YYYY-MM-DD` field, else
  falls back to file mtime. Inserts on a new line just before the
  closing `---`.
- For `tags`: inserts `tags: []` on a new line just before the
  closing `---`.
- Inserts go at end of frontmatter (last YAML line before `---`) so
  we never disturb existing field ordering. Uses rstrip+str concatenation
  with a leading newline so output is byte-stable.

Dry-run by default. Pass --write to actually patch files.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

PYRAMID = Path(__file__).resolve().parent.parent
LINT_JSON = Path("/tmp/lint_results.json")


def split_frontmatter(text: str) -> tuple[str, str, str] | None:
    """Return (yaml_block, body, _) where yaml_block is the YAML frontmatter
    block starting with the opening '---' line and ending right after the
    closing '---' line (no body content included), and body is everything
    after the closing '---' line.
    Returns None if no valid YAML frontmatter found.

    A 'closing' --- line must be exactly '---' (no leading spaces) on its
    own line. The first --- that satisfies this (after the opening) wins.
    """
    if not text.startswith("---\n"):
        return None
    # scan lines after the opening '---' for the next standalone '---'
    pos = 4  # right after '---\n'
    while pos < len(text):
        nl = text.find("\n", pos)
        if nl < 0:
            # file ends mid-block: invalid
            return None
        line = text[pos:nl]
        if line == "---":
            # closing fence; everything from here is body (including the \n)
            yaml_end = nl + 1  # position right after the '\n'
            return text[:yaml_end], text[yaml_end:], ""
        pos = nl + 1
    return None


def has_field(yaml: str, key: str) -> bool:
    """True if `key:` appears as a YAML mapping key in the frontmatter."""
    for line in yaml.splitlines():
        s = line.lstrip()
        if s.startswith(f"{key}:"):
            return True
    return False


def get_field(yaml: str, key: str) -> str | None:
    for line in yaml.splitlines():
        s = line.lstrip()
        if s.startswith(f"{key}:"):
            return s[len(key) + 1:].strip()
    return None


def patch(text: str, add_created: bool, add_tags: bool, created_value: str) -> str:
    parts = split_frontmatter(text)
    if parts is None:
        return text
    yaml, body, _ = parts

    # yaml ends with '\n' right after the closing '---' line.
    # Strip the closing '---' and its \n, append new fields, re-attach
    # the closing '---' and body. This keeps new fields INSIDE the frontmatter.
    assert yaml.endswith("\n---\n") or yaml.endswith("\n---")
    if yaml.endswith("\n---\n"):
        inner = yaml[:-5]  # strip '\n---\n'
        closing = "\n---\n"
    else:
        inner = yaml[:-4]  # strip '\n---'
        closing = "\n---"

    if not inner.endswith("\n"):
        inner = inner + "\n"

    if add_created and not has_field(yaml, "created"):
        inner = inner + f"created: {created_value}\n"
    if add_tags and not has_field(yaml, "tags"):
        inner = inner + "tags: []\n"

    return inner + closing + body


def file_mtime_iso(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="actually patch files (default: dry-run)")
    args = ap.parse_args()

    if not LINT_JSON.exists():
        print(f"ERROR: {LINT_JSON} not found. Run lint_wiki.py first.", file=sys.stderr)
        sys.exit(1)

    data = json.load(open(LINT_JSON))
    issues = data.get("frontmatter_issues", [])

    targets: dict[str, dict[str, bool]] = {}
    for path, msg in issues:
        if path == "log.md":
            continue
        if msg == "missing 'created' field":
            targets.setdefault(path, {})["created"] = True
        elif msg == "missing 'tags' field":
            targets.setdefault(path, {})["tags"] = True
        # else: skip empty tags / invalid type / invalid date

    print(f"Found {len(targets)} files needing backfill "
          f"(missing 'created' and/or 'tags').")

    patched = 0
    skipped = 0
    for rel, fields in sorted(targets.items()):
        full = PYRAMID / "wiki" / rel
        if not full.exists():
            print(f"  [SKIP] {rel} (file not found)")
            skipped += 1
            continue
        try:
            text = full.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  [SKIP] {rel} (read error: {e})")
            skipped += 1
            continue

        # determine created value
        ingested = get_field(text, "ingested")
        if ingested and re.match(r"^\d{4}-\d{2}-\d{2}$", ingested.strip()):
            created_value = ingested.strip()
        else:
            created_value = file_mtime_iso(full)

        new_text = patch(
            text,
            add_created=fields.get("created", False),
            add_tags=fields.get("tags", False),
            created_value=created_value,
        )

        if new_text == text:
            print(f"  [NOOP] {rel}")
            skipped += 1
            continue

        # sanity: frontmatter must still be valid
        if not (new_text.startswith("---\n") and "\n---\n" in new_text[:3000]):
            print(f"  [SKIP] {rel} (would produce invalid frontmatter)")
            skipped += 1
            continue

        if args.write:
            full.write_text(new_text, encoding="utf-8")
        patched += 1
        adds = []
        if fields.get("created"): adds.append(f"created={created_value}")
        if fields.get("tags"): adds.append("tags=[]")
        verb = "PATCH" if args.write else "WOULD-PATCH"
        print(f"  [{verb}] {rel}  ({', '.join(adds)})")

    print()
    print(f"Summary: patched={patched} skipped={skipped} "
          f"({'WRITE' if args.write else 'DRY-RUN'})")


if __name__ == "__main__":
    main()
