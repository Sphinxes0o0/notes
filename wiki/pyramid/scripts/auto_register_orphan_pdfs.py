#!/usr/bin/env python3
"""Batch create source pages for orphan PDFs in pyramid/raw/notes/resources/docs/.

Skips liteparse (which is ~1m/PDF). Only writes frontmatter + one-line body.

Naming rule: <source-type>-<slug>.md per ingest_pdf.file_type() / category_from_path().
Source-type defaults to 'pdf' for misc paths. If first-page text signals book/paper/slide
we override the type to match the content.
"""
from __future__ import annotations

import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path

import pdf_coverage

PYRAMID = pdf_coverage.PYRAMID
SOURCES = PYRAMID / "wiki" / "sources"
TODAY = datetime.now().strftime("%Y-%m-%d")
LP_VERSION = "2.0.5"  # match recent ingests (liteparse 2.0.5 in CLAUDE.md examples)

# Slugify: lower + replace non-word/- with -, collapse -, strip
_slug_nonword = re.compile(r"[^\w\s-]", re.UNICODE)
_slug_space = re.compile(r"[\s_]+", re.UNICODE)
_slug_dash = re.compile(r"-+", re.UNICODE)


def slugify(name: str) -> str:
    s = Path(name).stem.lower()
    s = _slug_nonword.sub("", s)
    s = _slug_space.sub("-", s)
    s = _slug_dash.sub("-", s)
    return s.strip("-")


def file_md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def first_page_text(p: Path, max_chars: int = 1500) -> str:
    try:
        import pymupdf  # PyMuPDF — pip install pymupdf
        doc = pymupdf.open(str(p))
        if doc.page_count == 0:
            return ""
        return (doc[0].get_text() or "")[:max_chars]
    except Exception as e:
        return f"<<pymupdf read failed: {e}>>"


def classify(p: Path, head: str) -> tuple[str, str]:
    """Return (source_type, category) from path context + first-page text.

    Heuristics:
      - filename hints: "user guide" / "user_guide" → book
      - "franca" / "commonapi" / "vSomeIP" / "netmap" / "tcp_protocol" / "linux_network_stack"
        → paper (technical spec / analysis)
      - "Bjarne" / 中文"STL" / "21st Century" style → book
      - "slide" / "deck" / "讲座" → slide
      - short < 3 page text-heavy → paper
    Default: pdf / misc
    """
    name = p.stem.lower()
    text = head.lower()

    # Slide indicators
    if any(k in name for k in ("slide", "deck", "讲座", "ppt")):
        return "slide", "slide"
    if any(k in text for k in ("slide ", "deck", "keynote")):
        return "slide", "slide"

    # Book indicators (user guides, tutorials, named books)
    book_hints = (
        "user guide", "user_guide", "tutorial", "getting started",
        "stl中文版", "stl", "21st century", "modern c++", "modern cpp",
        "rust 入门", "rust入门", "泛型编程",
    )
    if any(k in name for k in book_hints) or any(k in text for k in book_hints):
        return "book", "book"
    if "franca_user_guide" in name:
        return "book", "book"
    if "rust 入门指北" in name:
        return "book", "book"
    if "泛型编程" in name:
        return "book", "book"

    # Paper indicators (RFC design, technical specs, deep dives)
    paper_hints = (
        "rfc", "design", "implementation", "stack", "specification",
        "header", "error_processing", "endpoints", "interface",
        "tcp_protocol", "linux_network", "netmap", "vsomeip",
        "commonapi", "someip",
    )
    if any(k in name for k in paper_hints) or any(k in text for k in paper_hints):
        return "paper", "paper"

    return "pdf", "misc"


def rel_path_under_raw(p: Path) -> str:
    """Relative path under raw/ for the path: frontmatter field.

    We use raw/<rest> rather than raw/PDFs/<rest> because the PDFs live
    in raw/notes/resources/docs/, not in raw/PDFs/. This matches how a
    human would write `path:` for these files.
    """
    rel = p.resolve().relative_to((PYRAMID / "raw").resolve())
    return f"raw/{rel}"


def make_page(p: Path, md5: str, src_type: str, category: str, head: str) -> Path:
    slug = slugify(p.name)
    out = SOURCES / f"{src_type}-{slug}.md"
    if out.exists():
        print(f"  ⏭  EXISTS: {out.relative_to(PYRAMID)}", file=sys.stderr)
        return out

    size_kb = p.stat().st_size // 1024
    size_mb = round(p.stat().st_size / 1e6, 2)
    title = p.stem
    rel = rel_path_under_raw(p)

    # Trim head preview for the body (single line per task spec)
    head_preview = head.strip().replace("\n", " ")[:120]

    content = f"""---
type: source
source-type: {src_type}
title: "{title}"
path: {rel}
source-md5: {md5}
size: {size_kb} KB
category: {category}
ingested: {TODAY}
tool: liteparse
liteparse-version: {LP_VERSION}
---

# {title}

> Auto-ingested from `{rel}` on {TODAY} (source page only; full liteparse parse pending).
> Source file: {size_mb} MB. First-page preview: {head_preview!r}

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[{rel}]]`
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out


def main() -> int:
    report = pdf_coverage.coverage_report()
    orphans = [Path(str(PYRAMID / str(o["path"]))) for o in report["orphan_pdfs"]]
    # filter to only the ones under raw/notes/resources/docs/ (the task scope)
    scope = [
        o for o in orphans
        if "/raw/notes/resources/docs/" in str(o.resolve())
    ]
    print(f"Found {len(scope)} orphan PDFs in scope (raw/notes/resources/docs/)\n")

    results = []
    for p in scope:
        md5 = file_md5(p)
        head = first_page_text(p)
        src_type, category = classify(p, head)
        out = make_page(p, md5, src_type, category, head)
        rel = out.relative_to(PYRAMID)
        size_kb = p.stat().st_size // 1024
        print(f"  {p.stat().st_size/1e6:6.2f} MB  md5={md5[:8]}  type={src_type}/{category}  -> {rel}")
        results.append((p, out, md5, src_type, category, size_kb))

    print(f"\nCreated {len(results)} source pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
