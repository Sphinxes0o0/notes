#!/usr/bin/env python3
"""Backfill `source-md5:` frontmatter field on old PDF source pages.

The recent `find_duplicate_by_md5` dedup logic in ingest_pdf.py prefers
`source-md5:` over `path:` for duplicate detection. Without it, re-ingesting
an existing source rewrites the old file instead of being detected as a dup.

This script walks all wiki/sources/*.md, resolves the `path:` to a real file
under raw/PDFs/, computes MD5, and inserts `source-md5: <hash>` right after
the `path:` line.

- Skips files that already have `source-md5:`.
- Skips files without a `path:` field.
- Warns (does not error) when the path cannot be resolved.
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_PDFS_DIR = ROOT / "raw" / "PDFs"
SOURCES_DIR = ROOT / "wiki" / "sources"

PATH_RE = re.compile(r"^path:\s*(.+)$", re.M)
SOURCE_MD5_RE = re.compile(r"^source-md5:", re.M)


def file_md5(p: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def resolve_candidate(rel: str):
    """Try several ways to turn a `path:` value into a real file on disk."""
    rel = rel.strip().strip('"').strip("'")
    # Multi-path entries (e.g. "~/a/ ~/b/") — take the first.
    rel = rel.split()[0] if rel else ""

    # Absolute path
    p = Path(rel).expanduser()
    if p.is_absolute() and p.is_file():
        return p

    # Relative to raw/PDFs
    p = (RAW_PDFS_DIR / rel).resolve()
    if p.is_file():
        return p

    # Relative to repo root
    p = (ROOT / rel).resolve()
    if p.is_file():
        return p

    return None


def add_md5(md_file: Path) -> str:
    """Return 'added' | 'skipped' | 'no-path' | 'unresolved'."""
    text = md_file.read_text(encoding="utf-8")
    if SOURCE_MD5_RE.search(text):
        return "skipped"

    m = PATH_RE.search(text)
    if not m:
        return "no-path"

    rel_path = m.group(1).strip()
    actual = resolve_candidate(rel_path)
    if not actual:
        print(f"  WARN  {md_file.name}: cannot resolve path: {rel_path}")
        return "unresolved"

    md5 = file_md5(actual)
    # Insert source-md5 right after the path: line
    new_text = re.sub(
        r"^(path:\s*.+)$",
        rf"\1\nsource-md5: {md5}",
        text,
        count=1,
        flags=re.M,
    )
    if new_text == text:
        # Should not happen — regex matched but substitution didn't.
        print(f"  WARN  {md_file.name}: regex substitution no-op")
        return "unresolved"
    md_file.write_text(new_text, encoding="utf-8")
    return "added"


def main() -> int:
    if not SOURCES_DIR.is_dir():
        print(f"ERROR: {SOURCES_DIR} not found", file=sys.stderr)
        return 1

    counts = {"added": 0, "skipped": 0, "no-path": 0, "unresolved": 0}
    for md in sorted(SOURCES_DIR.glob("*.md")):
        result = add_md5(md)
        counts[result] += 1

    total = sum(counts.values())
    print()
    print(f"Scanned: {total} source pages")
    print(f"  added:      {counts['added']}")
    print(f"  skipped:    {counts['skipped']}  (already have source-md5)")
    print(f"  no-path:    {counts['no-path']}  (bookmark/web, no path: field)")
    print(f"  unresolved: {counts['unresolved']}  (path: not pointing to a file)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
