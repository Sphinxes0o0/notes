#!/usr/bin/env python3
"""ingest_pdf.py — Convert PDF/DOCX/XLSX/PPTX/image files into wiki source pages.

Wrapper around `lit parse` (run-llama/liteparse) that produces
`wiki/sources/pdf-<slug>.md` source pages with frontmatter, and
optional `wiki/attachments/<slug>-page<N>.png` screenshots.

Usage:
  python3 scripts/ingest_pdf.py <file> [<file> ...]
  python3 scripts/ingest_pdf.py --batch <input-dir>  (recursive)

For each file:
  1. Run `lit parse --format json` to get structured text + bbox
  2. Render markdown body (heading detection, paragraph grouping)
  3. Write `wiki/sources/<type>-<slug>.md` with frontmatter
  4. Optional: render page screenshots via `lit screenshot`

Slug = lowercase + hyphenated basename, with .pdf/.docx/etc stripped.

Config (env vars):
  LITEPARSE_BIN: path to `lit` CLI (default: from PATH or venv)
  INGEST_OUTPUT: wiki output dir (default: <pyramid>/wiki)
  INGEST_ATTACH: attachments dir (default: <pyramid>/wiki/attachments)
  INGEST_OCR: enable OCR (default: True)
  INGEST_OCR_LANG: tesseract language (default: eng)
  INGEST_MAX_PAGES: per-file cap (default: 1000)
  INGEST_GENERATE_SCREENSHOTS: also render page PNGs (default: False;
    slow + storage; enable only when downstream LLM uses vision)

Limitations (intentional, by Karpathy Simplicity First):
  - One ingest = one source page (no batched combined output)
  - No OCR auto language detection
  - No semantic dedup (caller must check sources/ before adding)
  - No LLM post-processing (raw markdown only; downstream CC does summary)
"""

import os
import re
import sys
import json
import argparse
import subprocess
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PYRAMID_ROOT = SCRIPT_DIR.parent  # scripts/ is directly under pyramid/

LITEPARSE_BIN = os.environ.get("LITEPARSE_BIN") or shutil.which("lit")
if not LITEPARSE_BIN:
    # Fall back to the known venv location
    VENV_LIT = Path.home() / ".local/liteparse-venv/bin/lit"
    if VENV_LIT.exists():
        LITEPARSE_BIN = str(VENV_LIT)

OUTPUT_DIR = Path(os.environ.get("INGEST_OUTPUT", PYRAMID_ROOT / "wiki"))
ATTACH_DIR = Path(os.environ.get("INGEST_ATTACH", OUTPUT_DIR / "attachments"))
RAW_PDFS_DIR = PYRAMID_ROOT / "raw" / "PDFs"

OCR_ENABLED = os.environ.get("INGEST_OCR", "0") not in ("0", "false", "")
# OCR is opt-in: Tesseract requires eng.traineddata installed system-wide,
# which is not always present (e.g. fresh dev env). Default off; enable
# explicitly with INGEST_OCR=1 env var or --ocr flag (TODO if needed).
OCR_LANG = os.environ.get("INGEST_OCR_LANG", "eng")
MAX_PAGES = int(os.environ.get("INGEST_MAX_PAGES", "1000"))
GENERATE_SCREENSHOTS = os.environ.get("INGEST_GENERATE_SCREENSHOTS", "0") in ("1", "true")

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def slugify(name: str) -> str:
    """Convert filename to a wiki-friendly slug."""
    s = Path(name).stem  # remove .pdf
    s = s.lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def file_type(p: Path) -> str:
    """Return source-type bucket for the file.

    For PDF, the bucket is refined by the subdirectory under raw/PDFs/:
    papers/ -> 'paper', slides/ -> 'slide', books/ -> 'book', else 'pdf'.
    This avoids slug collisions between the 3 buckets and gives wiki
    readers a clearer signal than a flat 'pdf-' prefix.
    """
    ext = p.suffix.lower()
    if ext in (".docx", ".doc"):
        return "docx"
    if ext in (".pptx", ".ppt"):
        return "pptx"
    if ext in (".xlsx", ".xls"):
        return "xlsx"
    if ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        return "image"
    if ext == ".pdf":
        return category_from_path(p) if category_from_path(p) != "misc" else "pdf"
    return ext.lstrip(".") or "unknown"


def file_size_kb(p: Path) -> int:
    return p.stat().st_size // 1024


def relative_path_under_raw(p: Path) -> str:
    """Return path relative to raw/PDFs/ if possible.

    Tolerates absolute vs relative input: resolve both sides first.
    """
    p = p.resolve()
    raw = RAW_PDFS_DIR.resolve()
    try:
        return str(p.relative_to(raw))
    except ValueError:
        return str(p)


def category_from_path(p: Path) -> str:
    """Map relative path to category: 'book' | 'paper' | 'slide' | 'misc'."""
    rel = relative_path_under_raw(p)
    if rel.startswith("books/"):
        return "book"
    if rel.startswith("papers/"):
        return "paper"
    if rel.startswith("slides/"):
        return "slide"
    return "misc"


# ──────────────────────────────────────────────
# Liteparse invocation
# ──────────────────────────────────────────────
def run_lit_parse(pdf_path: Path, fmt: str = "json") -> dict:
    """Run `lit parse` and return parsed JSON or text."""
    if not LITEPARSE_BIN:
        raise RuntimeError("lit CLI not found; install with `uv pip install liteparse` or set LITEPARSE_BIN")

    cmd = [LITEPARSE_BIN, "parse", str(pdf_path), "--format", fmt]
    if not OCR_ENABLED:
        cmd.append("--no-ocr")
    else:
        cmd.extend(["--ocr-language", OCR_LANG])
    cmd.extend(["--max-pages", str(MAX_PAGES)])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"lit parse failed (rc={result.returncode}): {result.stderr[:500]}")

    if fmt == "json":
        return json.loads(result.stdout)
    return {"text": result.stdout}


def run_lit_screenshot(pdf_path: Path, output_dir: Path) -> list:
    """Run `lit screenshot` to render page PNGs. Returns list of output paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [LITEPARSE_BIN, "screenshot", str(pdf_path), "-o", str(output_dir), "--dpi", "150"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"  warning: screenshot failed: {result.stderr[:200]}", file=sys.stderr)
        return []
    return sorted(output_dir.glob("*.png"))


# ──────────────────────────────────────────────
# JSON -> markdown rendering
# ──────────────────────────────────────────────
def render_markdown(parsed: dict, file_path: Path) -> str:
    """Convert liteparse JSON output to markdown body.

    liteparse JSON structure (assumed):
      {"pages": [{"page_number": 1, "text": "...", "blocks": [...], "bbox": [...]}]}

    We render simple text-by-text; complex layout (tables, columns) is
    preserved as plain text with paragraph breaks.
    """
    if "text" in parsed:
        return parsed["text"]  # text format

    pages = parsed.get("pages", [])
    out = []
    for p in pages:
        # liteparse JSON uses "page" (not "page_number") as the 1-based page number
        page_num = p.get("page", p.get("page_number", "?"))
        out.append(f"\n## Page {page_num}\n")
        text = p.get("text", "")
        if text:
            out.append(text)
        else:
            out.append("_(no text content on this page)_")
    return "\n".join(out)


# ──────────────────────────────────────────────
# Source page generation
# ──────────────────────────────────────────────
SOURCE_PAGE_TEMPLATE = """---
type: source
source-type: {source_type}
title: "{title}"
path: {path}
size: {size_kb} KB
category: {category}
ingested: {today}
tool: liteparse
liteparse-version: {lp_version}
---

# {title}

> Ingested from `{path}` via `lit parse` on {today}.
> Source file: {size_mb} MB.

{body}

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[{path}]]`
"""


def write_source_page(file_path: Path, parsed: dict, body: str) -> Path:
    """Write `wiki/sources/<type>-<slug>.md` source page."""
    src_type = file_type(file_path)
    slug = slugify(file_path.name)
    out_path = OUTPUT_DIR / "sources" / f"{src_type}-{slug}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    title = file_path.stem
    body_md = body.strip()

    # Get liteparse version
    lp_version = "unknown"
    try:
        result = subprocess.run([LITEPARSE_BIN, "--version"], capture_output=True, text=True, timeout=10)
        lp_version = result.stdout.strip().split()[-1] if result.stdout else "unknown"
    except Exception:
        pass

    today = datetime.now().strftime("%Y-%m-%d")
    content = SOURCE_PAGE_TEMPLATE.format(
        source_type=src_type,
        title=title,
        path=relative_path_under_raw(file_path),
        size_kb=file_size_kb(file_path),
        size_mb=round(file_size_kb(file_path) / 1024, 2),
        category=category_from_path(file_path),
        today=today,
        lp_version=lp_version,
        body=body_md,
    )
    out_path.write_text(content, encoding="utf-8")
    return out_path


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def ingest_one(file_path: Path, screenshot: bool = GENERATE_SCREENSHOTS) -> dict:
    """Ingest a single file. Returns dict with metadata for summary."""
    print(f"[ingest] {file_path} ({file_size_kb(file_path)} KB)")
    try:
        parsed = run_lit_parse(file_path, fmt="json")
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return {"file": str(file_path), "success": False, "error": str(e)}

    body = render_markdown(parsed, file_path)
    out_path = write_source_page(file_path, parsed, body)
    print(f"  -> {out_path.relative_to(PYRAMID_ROOT)}")

    result = {
        "file": str(file_path),
        "source_page": str(out_path.relative_to(PYRAMID_ROOT)),
        "success": True,
    }

    if screenshot:
        slug = slugify(file_path.name)
        screenshot_dir = ATTACH_DIR / f"{slug}-screenshots"
        pngs = run_lit_screenshot(file_path, screenshot_dir)
        if pngs:
            result["screenshots"] = [str(p.relative_to(PYRAMID_ROOT)) for p in pngs]
            print(f"  -> {len(pngs)} screenshots in {screenshot_dir.relative_to(PYRAMID_ROOT)}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Ingest PDF/DOCX/XLSX/PPTX/image files into wiki source pages")
    parser.add_argument("files", nargs="*", help="files to ingest (PDF/DOCX/XLSX/PPTX/image)")
    parser.add_argument("--batch", metavar="DIR", help="recursively ingest all files in DIR")
    parser.add_argument("--screenshot", action="store_true", help="also render page screenshots")
    parser.add_argument("--no-ocr", action="store_true", help="disable OCR (faster, text-only PDFs)")
    args = parser.parse_args()

    global OCR_ENABLED, GENERATE_SCREENSHOTS
    if args.no_ocr:
        OCR_ENABLED = False
    if args.screenshot:
        GENERATE_SCREENSHOTS = True

    if not LITEPARSE_BIN:
        print("ERROR: `lit` CLI not found. Install with:", file=sys.stderr)
        print("  uv venv ~/.local/liteparse-venv", file=sys.stderr)
        print("  uv pip install --python ~/.local/liteparse-venv/bin/python liteparse", file=sys.stderr)
        print("Or set LITEPARSE_BIN env var to the lit binary path.", file=sys.stderr)
        sys.exit(1)

    files = list(args.files)
    if args.batch:
        batch_dir = Path(args.batch)
        if not batch_dir.is_dir():
            print(f"ERROR: --batch path is not a directory: {args.batch}", file=sys.stderr)
            sys.exit(1)
        for ext in ("*.pdf", "*.docx", "*.doc", "*.pptx", "*.ppt", "*.xlsx", "*.xls",
                    "*.png", "*.jpg", "*.jpeg", "*.tiff", "*.bmp"):
            files.extend(str(p) for p in batch_dir.rglob(ext))

    if not files:
        parser.print_help()
        sys.exit(0)

    print(f"=== ingest_pdf.py: {len(files)} file(s) ===")
    print(f"  lit CLI:    {LITEPARSE_BIN}")
    print(f"  output:     {OUTPUT_DIR}/sources")
    print(f"  attachments:{ATTACH_DIR}")
    print(f"  OCR:        {OCR_ENABLED} (lang={OCR_LANG})")
    print(f"  screenshots:{GENERATE_SCREENSHOTS}")
    print()

    results = []
    for f in files:
        p = Path(f)
        if not p.exists():
            print(f"[skip] not found: {f}")
            continue
        result = ingest_one(p)
        results.append(result)
        print()

    # Summary
    ok = sum(1 for r in results if r.get("success"))
    fail = len(results) - ok
    print(f"=== Summary: {ok} succeeded, {fail} failed ===")
    if fail:
        for r in results:
            if not r.get("success"):
                print(f"  FAIL: {r['file']}: {r.get('error', '?')}")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
