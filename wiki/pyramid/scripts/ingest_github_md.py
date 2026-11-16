#!/usr/bin/env python3
"""ingest_github_md.py — Ingest a GitHub-sourced .md file into a wiki source page.

Pyramid-specific, modeled on atlas's `scripts/ingest_relay_neuron.py` (which
solves the same problem for the atlas vault). Needed because pyramid's
`ingest_pdf.py` is liteparse-only and cannot read .md files directly, but the
`pdf_coverage.py` coverage tool scans .md files under raw/ and reports them as
orphan when no source page references them via `source-md5:`.

Workflow (one source page per raw .md):
  1. Read `raw/github/<owner>/<repo>/<file>.md` (or any .md under a raw root)
  2. Compute `source-md5:` (md5 of the raw file body)
  3. Derive slug from filename, prefixed with the repo/owner namespace
  4. Write `wiki/sources/<slug>.md` with frontmatter:
       type, source-type: github
       title, author, date
       path, source-md5, size
       category, ingested, tool
       summary, tags, created
  5. Print path of generated source page

Usage:
  # Single file
  python3 scripts/ingest_github_md.py raw/github/modern-cpp-features/CPP11.md

  # Batch
  python3 scripts/ingest_github_md.py --batch raw/github/modern-cpp-features/

  # Default is --dry-run; pass --write to actually create pages
  python3 scripts/ingest_github_md.py --batch raw/github/modern-cpp-features/ --write

  # Force overwrite (bypass md5 dedup)
  python3 scripts/ingest_github_md.py --batch raw/github/modern-cpp-features/ --write --force

Dedup:
  Each source page carries `source-md5:` in its frontmatter. Before writing
  a new page, we scan wiki/sources/*.md and skip the file if any existing
  page already has the same md5 (or the same `path:` — legacy fallback).
  With --force, dedup is bypassed and the existing page is overwritten.

Slug policy:
  For files under raw/github/<owner>/<repo>/, the slug is
  `github-<owner>-<repo>-<file_stem_slug>`. For files outside that layout,
  the slug is `github-md-<file_stem_slug>`.

Intentionally simple (Karpathy Simplicity First):
  - One raw .md -> one source page; the raw body is preserved verbatim
    inside the page, ready for downstream LLM summarization.
  - No semantic dedup, no LLM post-processing.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import date
from pathlib import Path

PYRAMID = Path(__file__).resolve().parent.parent
SOURCES = PYRAMID / "wiki" / "sources"

# Keep ASCII lowercase + digits in the file-stem slug.
SLUG_KEEP_RE = re.compile(r"[^a-z0-9]+")

# Owner (i.e. `raw/github/<owner>/`) -> metadata overrides. The
# `modern-cpp-features` owner dir holds Anthony Calandra's reference,
# so we credit him and tag the year 2024.
OWNER_META = {
    "modern-cpp-features": {
        "author": "Anthony Calandra",
        "date": "2024",
        "category": "modern-cpp",
    },
}


def file_md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def slugify_filename(name: str) -> str:
    """Lowercase the stem, hyphenate non-alphanumeric runs. e.g. CPP11 -> cpp11,
    CONTRIBUTING -> contributing."""
    stem = name
    if stem.endswith(".md"):
        stem = stem[:-3]
    return SLUG_KEEP_RE.sub("-", stem.lower()).strip("-")


def make_slug(raw_path: Path) -> str:
    """Map a raw path to its source-page slug.

    For raw/github/<owner>/<file>.md -> github-<owner>-<file-stem>
    For everything else              -> github-md-<file-stem>
    """
    rel = raw_path.resolve().relative_to(PYRAMID.resolve())
    parts = rel.parts  # e.g. ('raw', 'github', 'owner', 'file.md')
    if len(parts) >= 4 and parts[0] == "raw" and parts[1] == "github":
        owner = parts[2]
        return f"github-{owner}-{slugify_filename(parts[-1])}"
    return f"github-md-{slugify_filename(parts[-1])}"


def repo_meta(raw_path: Path) -> dict:
    """Return OWNER_META dict for the owner under raw/github/, or {}."""
    rel = raw_path.resolve().relative_to(PYRAMID.resolve())
    parts = rel.parts
    if len(parts) >= 4 and parts[0] == "raw" and parts[1] == "github":
        owner = parts[2]
        return OWNER_META.get(owner, {})
    return {}


def derive_size(p: Path) -> str:
    sz = p.stat().st_size
    if sz < 5_000:
        return "tiny"
    if sz < 20_000:
        return "small"
    if sz < 100_000:
        return "medium"
    if sz < 500_000:
        return "large"
    return "huge"


def first_heading_title(text: str, fallback: str) -> str:
    """First line starting with '# ' (after leading blanks). Falls back to stem."""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
        if s and not s.startswith("#"):
            # First non-blank, non-heading content line — give up looking
            return fallback
    return fallback


def first_paragraph_summary(text: str, max_len: int = 120) -> str:
    """First non-heading, non-empty paragraph longer than 20 chars; truncate."""
    past_heading = False
    for line in text.splitlines():
        s = line.strip()
        if not past_heading:
            if s.startswith("#") or not s:
                continue
            past_heading = True
        if not s or s.startswith("|") or s.startswith("#"):
            continue
        if len(s) < 20:
            continue
        if len(s) > max_len:
            s = s[: max_len - 1] + "…"
        return s
    return "(no summary)"


# Per-run caches so --batch doesn't re-hash a file already seen.
_md5_cache: dict = {}
_dry_run_taken: set = set()


def cached_md5(p: Path) -> str:
    if p not in _md5_cache:
        _md5_cache[p] = file_md5(p)
    return _md5_cache[p]


def find_duplicate_by_md5(raw_path: Path, md5: str) -> "Path | None":
    """Return an existing source page referencing the same raw file via
    `source-md5:` (preferred) or `path:` (legacy fallback), else None."""
    if not SOURCES.exists():
        return None
    target_rel = str(raw_path.resolve().relative_to(PYRAMID.resolve()))
    for md in SOURCES.glob("*.md"):
        try:
            in_fm = False
            with open(md, encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped == "---":
                        if in_fm:
                            break
                        in_fm = True
                        continue
                    if not in_fm:
                        continue
                    if line.startswith("source-md5:"):
                        if line.split(":", 1)[1].strip() == md5:
                            return md
                    if line.startswith("path:"):
                        if line.split(":", 1)[1].strip() == target_rel:
                            return md
        except (OSError, IOError):
            continue
    return None


def _unique_outpath(slug: str) -> Path:
    """wiki/sources/<slug>.md, appending -1, -2, ... on collision."""
    base = SOURCES / f"{slug}.md"
    if not base.exists():
        return base
    n = 1
    while True:
        cand = SOURCES / f"{slug}-{n}.md"
        if not cand.exists():
            return cand
        n += 1


def build_source_page(raw_path: Path) -> Path:
    """Generate wiki/sources/<slug>.md from a raw .md file. Writes the file."""
    if not raw_path.exists():
        raise FileNotFoundError(raw_path)
    text = raw_path.read_text(encoding="utf-8", errors="ignore")
    md5 = cached_md5(raw_path)
    rel = raw_path.resolve().relative_to(PYRAMID.resolve())
    slug = make_slug(raw_path)
    meta = repo_meta(raw_path)
    size = derive_size(raw_path)
    title = first_heading_title(text, fallback=raw_path.stem)
    summary = first_paragraph_summary(text)
    today = date.today().isoformat()
    ingested = today  # 'ingested' mirrors creation date for this corpus

    author = meta.get("author", "")
    repo_date = meta.get("date", "")
    category = meta.get("category", "github-md")
    # Only emit the field if non-empty so generated frontmatter stays clean.
    author_line = f'author: "{author}"\n' if author else ""
    date_line = f"date: {repo_date}\n" if repo_date else ""

    frontmatter = f"""---
type: source
source-type: github
title: "Modern C++ Features — {title}"
{author_line}{date_line}path: {rel}
source-md5: {md5}
size: {size}
category: {category}
ingested: {ingested}
tool: ingest_github_md.py
summary: "{summary}"
tags: [cpp, modern-cpp, {category}]
created: {today}
---

# Modern C++ Features — {title}

> Ingested from `{rel}` (raw .md from `raw/github/...`)

## Overview

<!-- The full body of the raw file is preserved verbatim below.
     Downstream agent will rewrite this into a structured entity-page
     summary and add `## Related Pages` once entities are created. -->

"""

    out_path = _unique_outpath(slug)
    SOURCES.mkdir(parents=True, exist_ok=True)
    out_path.write_text(frontmatter + text, encoding="utf-8")
    return out_path


def ingest_one(raw_path: Path, *, dry_run: bool = False, force: bool = False) -> dict:
    """Ingest a single .md file. Returns a result dict for the summary report."""
    md5 = cached_md5(raw_path)
    rel = str(raw_path.resolve().relative_to(PYRAMID.resolve()))
    slug = make_slug(raw_path)
    out_path = _unique_outpath(slug)

    if not force:
        dup = find_duplicate_by_md5(raw_path, md5)
        if dup:
            rel_dup = dup.relative_to(PYRAMID)
            print(f"  ⏭️  SKIP: {rel}  (already ingested as {rel_dup}, md5 match)")
            return {
                "file": rel,
                "status": "skipped_dup",
                "source_page": str(rel_dup),
                "md5": md5,
            }

    if dry_run:
        # Collision-safe dry-run reporting.
        if out_path.name in _dry_run_taken:
            stem = out_path.stem
            n = 1
            while True:
                cand_name = f"{stem}-{n}.md"
                if cand_name not in _dry_run_taken:
                    _dry_run_taken.add(cand_name)
                    out_path = SOURCES / cand_name
                    break
                n += 1
        else:
            _dry_run_taken.add(out_path.name)
        print(f"  📝 DRY: would create {out_path.relative_to(PYRAMID)}  ← {rel}")
        return {
            "file": rel,
            "status": "would_create",
            "source_page": str(out_path.relative_to(PYRAMID)),
            "md5": md5,
        }

    out = build_source_page(raw_path)
    print(f"  ✅ CREATED: {out.relative_to(PYRAMID)}  ← {rel}")
    return {
        "file": rel,
        "status": "created",
        "source_page": str(out.relative_to(PYRAMID)),
        "md5": md5,
    }


def iter_batch(root: Path) -> list:
    """Recursively collect all .md files under root.

    Skips synthetic / metadata files (README.md, AGENT*.md, CLAUDE.md,
    TODO*.md) and well-known noise dirs (.git, node_modules). All other
    .md files are returned as candidate sources.
    """
    EXCLUDE_NAMES = {
        "README.md", "CLAUDE.md", "RESEARCH_MASTER_LIST.md",
        "FINAL_REPORT.md", "AGENT.md", "AGENT_REVIEW.md",
    }
    EXCLUDE_PREFIXES = ("TODO", "AGENT_")
    EXCLUDE_DIRS = {".claude", "node_modules", ".git"}
    out = []
    for p in sorted(root.rglob("*.md")):
        if not p.is_file():
            continue
        if p.name in EXCLUDE_NAMES:
            continue
        if any(p.name.startswith(pref) for pref in EXCLUDE_PREFIXES):
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Ingest a GitHub-sourced .md file (or batch) into wiki/sources/."
    )
    ap.add_argument("path", nargs="?",
                    help="path to a single raw .md file")
    ap.add_argument("--batch", metavar="DIR",
                    help="recursively ingest all .md files under DIR")
    ap.add_argument("--dry-run", action="store_true",
                    help="parse and print the plan, do not write any source pages")
    ap.add_argument("--write", action="store_true",
                    help="actually write source pages (default is dry-run, safety net)")
    ap.add_argument("--max-files", type=int, default=5, metavar="N",
                    help="cap number of files processed in --batch mode "
                         "(default: 5, safety net to prevent running on the whole corpus)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing source pages and bypass md5 dedup")
    args = ap.parse_args()

    if not args.path and not args.batch:
        ap.print_help()
        print("\nERR: provide a file path or --batch DIR", file=sys.stderr)
        return 2

    if args.path and args.batch:
        print("ERR: --batch and a positional path are mutually exclusive", file=sys.stderr)
        return 2

    if args.batch:
        batch_dir = Path(args.batch)
        if not batch_dir.is_dir():
            print(f"ERR: --batch path is not a directory: {args.batch}", file=sys.stderr)
            return 1
        files = iter_batch(batch_dir)
        if not args.write and not args.dry_run:
            args.dry_run = True
            print("  ℹ️  defaulting to --dry-run (pass --write to actually create source pages)",
                  file=sys.stderr)
        if args.max_files and args.max_files > 0 and len(files) > args.max_files:
            print(f"  ℹ️  capping --batch from {len(files)} to --max-files={args.max_files} "
                  f"(raise --max-files to process more)", file=sys.stderr)
            files = files[: args.max_files]
    else:
        raw = Path(args.path)
        if not raw.exists():
            print(f"ERR: {raw} does not exist", file=sys.stderr)
            return 1
        files = [raw]

    if not files:
        print(f"=== No .md files found under {args.batch or args.path} ===")
        return 0

    print(f"=== ingest_github_md.py: {len(files)} file(s) ===")
    print(f"  input:     {args.batch or args.path}")
    print(f"  output:    {SOURCES}")
    print(f"  dry-run:   {args.dry_run}")
    print(f"  write:     {args.write}")
    print(f"  force:     {args.force}")
    print()

    results = []
    for f in files:
        try:
            r = ingest_one(f, dry_run=args.dry_run, force=args.force)
        except Exception as e:
            rel = str(f.resolve().relative_to(PYRAMID.resolve()))
            print(f"  ❌ ERROR: {rel}  {e}", file=sys.stderr)
            r = {"file": rel, "status": "error", "error": str(e)}
        results.append(r)
        print()

    by_status: dict = {}
    for r in results:
        s = r.get("status", "?")
        by_status[s] = by_status.get(s, 0) + 1
    created = by_status.get("created", 0)
    skipped_dup = by_status.get("skipped_dup", 0)
    would_create = by_status.get("would_create", 0)
    errors = by_status.get("error", 0)

    print("=== Summary ===")
    print(f"  total:           {len(results)}")
    if args.dry_run:
        print(f"  would_create:    {would_create}")
    else:
        print(f"  created:         {created}")
    print(f"  skipped_dup:     {skipped_dup}  (md5 already in wiki/sources/)")
    print(f"  errors:          {errors}")

    if errors:
        print()
        print("Failures:")
        for r in results:
            if r.get("status") == "error":
                print(f"  FAIL: {r['file']}  ({r.get('error', '?')})")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
