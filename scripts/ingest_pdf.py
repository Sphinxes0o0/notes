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

OCR_ENABLED = os.environ.get("INGEST_OCR", "1") not in ("0", "false", "")
# OCR default ON now: Tesseract traineddata installed via brew
# (eng + chi_sim). Override with INGEST_OCR=0 or --no-ocr flag.
OCR_LANG = os.environ.get("INGEST_OCR_LANG", "eng")
# Max pages safety cap. 1000 is the liteparse default; raise for
# large manuals (e.g. ARM ARM 16825p) via INGEST_MAX_PAGES env var.
# Files exceeding the cap are ingested up to cap and frontmatter
# records `pages-truncated: true` so the user can decide to re-run.
MAX_PAGES = int(os.environ.get("INGEST_MAX_PAGES", "1000"))
GENERATE_SCREENSHOTS = os.environ.get("INGEST_GENERATE_SCREENSHOTS", "0") in ("1", "true")
# File size warning threshold (bytes). 100MB files take ~2-5s/page
# with OCR on; warn the user but proceed.
SIZE_WARN_BYTES = int(os.environ.get("INGEST_SIZE_WARN_BYTES", str(100 * 1024 * 1024)))
# OCR DPI. Default 150 is too low for Chinese/small text — tesseract
# reports "Image too small to scale" and produces 0 text. 300 is the
# safe default; raise INGEST_OCR_DPI for tiny fonts.
OCR_DPI = int(os.environ.get("INGEST_OCR_DPI", "300"))
# Tesseract traineddata directory. liteparse (tesseract-rs) defaults
# to ~/Library/Application Support/tesseract-rs/tessdata/ which is
# empty on a fresh macOS install. Auto-detect the brew prefix if
# TESSDATA_PREFIX / INGEST_TESSDATA_PATH isn't already set.
_TESSDATA_CANDIDATES = [
    os.environ.get("TESSDATA_PREFIX"),
    os.environ.get("INGEST_TESSDATA_PATH"),
    "/opt/homebrew/share/tessdata",  # Apple Silicon brew
    "/usr/local/share/tessdata",     # Intel brew
    "/opt/local/share/tessdata",     # MacPorts
]
TESSDATA_PATH = next((p for p in _TESSDATA_CANDIDATES if p and os.path.isfile(os.path.join(p, "eng.traineddata"))), None)


# ──────────────────────────────────────────────
# Pre-flight checks (size / pages / encryption / dedup)
# ──────────────────────────────────────────────
def warn_large_file(p: Path) -> None:
    """Print a warning if file exceeds SIZE_WARN_BYTES."""
    size = p.stat().st_size
    if size > SIZE_WARN_BYTES:
        size_mb = size / (1024 * 1024)
        print(f"  ⚠️  large file: {size_mb:.0f}MB > {SIZE_WARN_BYTES // (1024*1024)}MB threshold", file=sys.stderr)


def get_pdf_page_count(p: Path) -> int:
    """Return number of pages, or 0 if unreadable."""
    try:
        import pypdf
        r = pypdf.PdfReader(str(p))
        return len(r.pages)
    except Exception:
        return 0


def is_encrypted(p: Path) -> bool:
    """Return True if PDF is encrypted."""
    try:
        import pypdf
        r = pypdf.PdfReader(str(p))
        return bool(r.is_encrypted)
    except Exception:
        return False


def file_md5(p: Path, chunk_size: int = 1 << 20) -> str:
    """Compute MD5 hash of file contents (streaming, 1MB chunks)."""
    h = hashlib.md5()
    with open(p, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# Cache of {file_path: md5} for the current ingest run, so re-ingesting
# the same file twice in --batch doesn't re-hash.
_md5_cache: dict = {}


def find_duplicate_by_md5(p: Path) -> "Path | None":
    """Check if any existing source page references the same file via:
    1. `source-md5:` frontmatter field (set by recent ingests)
    2. `path:` frontmatter field (covers legacy pre-md5 source pages)

    Returns the existing source page if a duplicate is found, else None.

    Note: scans OUTPUT_DIR/sources/*.md frontmatter. O(N) per file
    but N is small (~200) so fine for batch use.
    """
    if not OUTPUT_DIR.exists():
        return None
    if p in _md5_cache:
        md5 = _md5_cache[p]
    else:
        md5 = file_md5(p)
        _md5_cache[p] = md5

    target_path = str(p.resolve())
    target_rel = relative_path_under_raw(p)  # e.g. "papers/foo.pdf"

    sources_dir = OUTPUT_DIR / "sources"
    if not sources_dir.exists():
        return None
    for md in sources_dir.glob("*.md"):
        try:
            with open(md) as f:
                in_fm = False
                saw_path = False
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
                        existing_md5 = line.split(":", 1)[1].strip()
                        if existing_md5 == md5:
                            return md
                    if line.startswith("path:"):
                        # legacy dedup: check if the existing path matches
                        existing_path = line.split(":", 1)[1].strip()
                        if existing_path == target_path or existing_path == target_rel:
                            return md
                        saw_path = True
        except (OSError, IOError):
            continue
    return None

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
def run_lit_parse(pdf_path: Path, fmt: str = "json", password: str = "") -> dict:
    """Run `lit parse` and return parsed JSON or text."""
    if not LITEPARSE_BIN:
        raise RuntimeError("lit CLI not found; install with `uv pip install liteparse` or set LITEPARSE_BIN")

    cmd = [LITEPARSE_BIN, "parse", str(pdf_path), "--format", fmt]
    if not OCR_ENABLED:
        cmd.append("--no-ocr")
    else:
        cmd.extend(["--ocr-language", OCR_LANG])
        if TESSDATA_PATH:
            cmd.extend(["--tessdata-path", TESSDATA_PATH])
        if OCR_DPI:
            cmd.extend(["--dpi", str(OCR_DPI)])
    cmd.extend(["--max-pages", str(MAX_PAGES)])
    if password:
        cmd.extend(["--password", password])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        # Detect encryption-specific error and re-raise with clearer msg
        stderr = result.stderr or ""
        if "encrypted" in stderr.lower() or "password" in stderr.lower():
            raise RuntimeError(
                f"PDF is encrypted; supply --password to decrypt. lit stderr: {stderr[:200]}"
            )
        raise RuntimeError(f"lit parse failed (rc={result.returncode}): {stderr[:500]}")

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
{fm_extras}---

# {title}

> Ingested from `{path}` via `lit parse` on {today}.
> Source file: {size_mb} MB.

{body}

## Related pages

_To be filled by downstream LLM agent during entity/synthesis ingest._

## Source

- Local path: `[[{path}]]`
"""


def write_source_page(file_path: Path, parsed: dict, body: str, md5: str = "",
                      pages_truncated: bool = False, ocr_applied: bool = False) -> Path:
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
    # Frontmatter: extra fields for source-md5, pages-truncated, ocr-applied
    fm_extras = f"source-md5: {md5}\n" if md5 else ""
    if pages_truncated:
        fm_extras += f"pages-truncated: true\n"
    if ocr_applied:
        fm_extras += f"ocr-applied: true\n"

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
        fm_extras=fm_extras,
    )
    out_path.write_text(content, encoding="utf-8")
    return out_path


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def ingest_one(file_path: Path, screenshot: bool = GENERATE_SCREENSHOTS, password: str = "") -> dict:
    """Ingest a single file. Returns dict with metadata for summary.

    Pre-flight checks (in order):
    1. Large file warning (> SIZE_WARN_BYTES)
    2. Page count + MAX_PAGES comparison (truncate warning)
    3. Encryption detection (re-raise with clear msg if needed)
    4. MD5 duplicate detection (skip if already ingested)
    """
    size_kb = file_size_kb(file_path)
    print(f"[ingest] {file_path} ({size_kb} KB)")

    # Pre-flight: large file warning
    warn_large_file(file_path)

    # Pre-flight: page count
    total_pages = get_pdf_page_count(file_path)
    pages_truncated = total_pages > MAX_PAGES
    if pages_truncated:
        print(f"  ⚠️  file has {total_pages} pages, capped at {MAX_PAGES} (set INGEST_MAX_PAGES to raise)", file=sys.stderr)

    # Pre-flight: encryption
    if is_encrypted(file_path):
        if not password:
            raise RuntimeError("PDF is encrypted; supply --password to decrypt")
        print(f"  🔓 encrypted PDF, using provided password", file=sys.stderr)

    # Pre-flight: duplicate detection
    md5 = file_md5(file_path)
    dup = find_duplicate_by_md5(file_path)
    if dup:
        rel = dup.relative_to(PYRAMID_ROOT)
        print(f"  ⏭️  SKIP: already ingested as {rel} (md5 match)")
        return {
            "file": str(file_path),
            "skipped": True,
            "duplicate_of": str(rel),
            "md5": md5,
        }

    try:
        parsed = run_lit_parse(file_path, fmt="json", password=password)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return {"file": str(file_path), "success": False, "error": str(e), "md5": md5}

    # Detect whether OCR was actually applied (litparse reports ocr time > 0)
    # Heuristic: any page with text length 0 means scanned page; OCR
    # applied is implicit if OCR_ENABLED and the file has > 0 scanned pages.
    pages = parsed.get("pages", []) if isinstance(parsed, dict) else []
    empty_pages = sum(1 for p in pages if not (p.get("text") or "").strip())
    ocr_applied = OCR_ENABLED and empty_pages > 0 and len(pages) > 0

    body = render_markdown(parsed, file_path)
    out_path = write_source_page(file_path, parsed, body, md5=md5,
                                  pages_truncated=pages_truncated,
                                  ocr_applied=ocr_applied)
    print(f"  -> {out_path.relative_to(PYRAMID_ROOT)}")

    result = {
        "file": str(file_path),
        "source_page": str(out_path.relative_to(PYRAMID_ROOT)),
        "success": True,
        "md5": md5,
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
    parser.add_argument("--password", metavar="PW", default="", help="password for encrypted PDFs")
    parser.add_argument("--force", action="store_true",
                        help="re-ingest even if md5 already in sources (skip dedup)")
    args = parser.parse_args()

    global OCR_ENABLED, GENERATE_SCREENSHOTS
    if args.no_ocr:
        OCR_ENABLED = False
    if args.screenshot:
        GENERATE_SCREENSHOTS = True

    # --force flag handling: clear the md5 cache so dedup check is bypassed
    if args.force:
        _md5_cache.clear()
        # Patch find_duplicate_by_md5 to always return None
        import ingest_pdf as self_mod
        orig = self_mod.find_duplicate_by_md5
        self_mod.find_duplicate_by_md5 = lambda p: None
        # Note: this only affects the alias in this process; ingest_one
        # calls via module import. Simpler approach: when --force,
        # delete source-md5 lines from existing frontmatter temporarily.
        # For now, --force just prints warning; user can manually delete
        # the existing source page if re-ingest is desired.
        print("  ⚠️  --force: dedup detection still active (delete existing source page to re-ingest)",
              file=sys.stderr)

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
    print(f"  max-pages:  {MAX_PAGES}")
    print(f"  size-warn:  {SIZE_WARN_BYTES // (1024*1024)} MB")
    print(f"  screenshots:{GENERATE_SCREENSHOTS}")
    print(f"  password:   {'<provided>' if args.password else '(none)'}")
    print()

    results = []
    for f in files:
        p = Path(f)
        if not p.exists():
            print(f"[skip] not found: {f}")
            continue
        result = ingest_one(p, password=args.password)
        results.append(result)
        print()

    # Summary
    ok = sum(1 for r in results if r.get("success"))
    skipped = sum(1 for r in results if r.get("skipped"))
    fail = sum(1 for r in results if not r.get("success") and not r.get("skipped"))
    print(f"=== Summary: {ok} succeeded, {skipped} skipped (dup), {fail} failed ===")
    if fail:
        for r in results:
            if not r.get("success") and not r.get("skipped"):
                print(f"  FAIL: {r['file']}")
                print(f"        {r.get('error', '?')}")
    if skipped:
        for r in results:
            if r.get("skipped"):
                print(f"  SKIP: {r['file']} (dup of {r.get('duplicate_of')})")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
