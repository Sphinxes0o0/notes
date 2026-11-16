#!/usr/bin/env python3
"""Backfill `source-md5:` frontmatter field on legacy PDF source pages.

A legacy source page is a .md under wiki/sources/ that:
  - has `source-type: pdf` (or is detected as PDF by having a `path:` that
    resolves under raw/PDFs/), AND
  - does NOT have a `source-md5:` field.

For each such page we:
  1. Read the `path:` field.
  2. Resolve it to a real PDF on disk via pdf_coverage.resolve_md_path_to_disk
     (which tolerates absolute paths, repo-relative `raw/...`, `raw/PDFs/...`
     relative, and bare basenames via rglob).
  3. Compute the PDF's MD5 and insert `source-md5: <hash>` on the line right
     after `path:`, preserving all other content (frontmatter order,
     indentation, body) byte-for-byte except for that one inserted line.
  4. Write atomically: tmp file in the same directory, then os.replace().

Other categories of pages (no path, multi-path, unresolvable path, already
have source-md5, etc.) are reported but never modified.

Usage:
  python3 scripts/add_source_md5.py            # actually patch
  python3 scripts/add_source_md5.py --dry-run  # report only, no writes

Idempotent: re-running touches zero files on the second pass (everything
either already has source-md5 or is in a skipped category).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Optional

# Reuse the canonical resolver from pdf_coverage.py to avoid drift.
from pdf_coverage import PYRAMID, resolve_md_path_to_disk  # noqa: F401

SOURCES = PYRAMID / "wiki" / "sources"

# Frontmatter is the leading `---` block at the top of the file. We only
# touch this block; the body is left untouched.
_FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_SOURCE_MD5_RE = re.compile(r"^source-md5:\s*([a-f0-9]{32})\s*$", re.M | re.I)
_PATH_RE = re.compile(r"^path:\s*(.+?)\s*$", re.M)
# Match an entire `path:` line including its trailing newline so we can
# insert `source-md5:` immediately after it.
_PATH_LINE_RE = re.compile(r"^path:\s*.+$\n?", re.M)


def file_md5(p: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def _is_multi_path(path_str: str) -> bool:
    """Heuristic: does this `path:` value look like multiple files / a dir?"""
    s = path_str.strip().strip('"').strip("'")
    if not s:
        return True
    # Trailing /* or trailing / => directory glob
    if s.endswith("/*") or s.endswith("/") or s.endswith("\\"):
        return True
    # Comma-separated — assume multi unless it resolves as a single file
    if "," in s and resolve_md_path_to_disk(s) is None:
        return True
    # Multiple whitespace-separated tokens that don't resolve as one file
    tokens = s.split()
    if len(tokens) > 1 and resolve_md_path_to_disk(s) is None:
        return True
    return False


def _atomic_write(path: Path, text: str) -> None:
    """Write `text` to `path` atomically (tmp in same dir + os.replace)."""
    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def process_one(md_file: Path, dry_run: bool) -> tuple[str, str]:
    """Process one .md. Returns (status, detail). Status is one of:
        'skipped'      — already has source-md5:
        'no-path'      — no path: field
        'multi-path'   — path: looks like multiple files / a directory
        'unresolved'   — path: did not resolve to a real PDF
        'added'        — source-md5: inserted
        'would-add'    — dry-run mode, would have added
        'error'        — read/parse/write failure (detail explains)
    """
    try:
        text = md_file.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        return "error", f"read: {e}"

    if _SOURCE_MD5_RE.search(text):
        return "skipped", "already has source-md5:"

    fm_match = _FM_RE.match(text)
    if not fm_match:
        return "error", "no frontmatter block"

    path_match = _PATH_RE.search(fm_match.group(1))
    if not path_match:
        return "no-path", "no path: in frontmatter"

    path_str = path_match.group(1).strip()

    if _is_multi_path(path_str):
        return "multi-path", f"path: {path_str!r}"

    resolved = resolve_md_path_to_disk(path_str)
    if resolved is None:
        return "unresolved", f"path: {path_str!r}"

    try:
        md5 = file_md5(resolved)
    except (OSError, PermissionError) as e:
        return "error", f"md5({resolved}): {e}"

    # Insert source-md5: line right after the path: line, inside the
    # frontmatter block. We operate on the first path: line in the file
    # (frontmatter convention is one per file).
    new_text, n = _PATH_LINE_RE.subn(
        lambda m: m.group(0) + f"source-md5: {md5}\n",
        text,
        count=1,
    )
    if n != 1 or new_text == text:
        return "error", "regex insert no-op (unexpected)"

    if dry_run:
        return "would-add", f"{md5}  {resolved.name}"

    try:
        _atomic_write(md_file, new_text)
    except OSError as e:
        return "error", f"write: {e}"

    return "added", f"{md5}  {resolved.name}"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Backfill source-md5: frontmatter field on legacy PDF source pages."
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing any files.",
    )
    ap.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-file status (default: summary only).",
    )
    args = ap.parse_args()

    if not SOURCES.is_dir():
        print(f"ERROR: {SOURCES} not found", file=sys.stderr)
        return 1

    mds = sorted(SOURCES.glob("*.md"))
    counts: dict[str, int] = {
        "added": 0,
        "would-add": 0,
        "skipped": 0,
        "no-path": 0,
        "multi-path": 0,
        "unresolved": 0,
        "error": 0,
    }
    # Sample messages for each non-success category, so the user can see
    # representative failures without dumping every line.
    samples: dict[str, list[tuple[str, str]]] = {
        "no-path": [], "multi-path": [], "unresolved": [], "error": [],
    }

    for md in mds:
        status, detail = process_one(md, dry_run=args.dry_run)
        counts[status] = counts.get(status, 0) + 1
        if args.verbose and status in ("added", "would-add", "error"):
            print(f"  {status:9s}  {md.relative_to(PYRAMID)}  {detail}")
        if status in samples and len(samples[status]) < 5:
            samples[status].append((md.name, detail))

    total = sum(counts.values())
    print()
    print(f"=== add_source_md5.py {'(DRY-RUN)' if args.dry_run else ''} ===")
    print(f"Scanned:     {total} source pages under {SOURCES.relative_to(PYRAMID)}/")
    if args.dry_run:
        print(f"  would-add:    {counts['would-add']:4d}  (source-md5: would be inserted)")
    else:
        print(f"  added:        {counts['added']:4d}  (source-md5: inserted)")
    print(f"  skipped:      {counts['skipped']:4d}  (already have source-md5:)")
    print(f"  no-path:      {counts['no-path']:4d}  (no path: field — non-PDF or stripped)")
    print(f"  multi-path:   {counts['multi-path']:4d}  (path: is dir or multi-file)")
    print(f"  unresolved:   {counts['unresolved']:4d}  (path: didn't resolve to a PDF)")
    if counts.get("error"):
        print(f"  error:        {counts['error']:4d}")

    for cat, items in samples.items():
        if items:
            print(f"\n--- {cat} samples (showing up to 5 of {counts[cat]}) ---")
            for name, detail in items:
                print(f"  {name}  {detail}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
