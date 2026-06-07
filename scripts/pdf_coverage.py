#!/usr/bin/env python3
"""pdf_coverage.py — Report coverage of raw/PDFs/ against wiki/sources/.

Authoritative match is by MD5 (frontmatter `source-md5:` field, set by
ingest_pdf.py since the liteparse 2.0.5 migration). Falls back to a
best-effort basename match for legacy pages that lack `source-md5:`.

Usage:
  python3 scripts/pdf_coverage.py            # human report
  python3 scripts/pdf_coverage.py --json     # machine-readable
  python3 scripts/pdf_coverage.py --delete-orphans   # actually rm orphan PDFs

Categories:
  - covered:      PDF has a matching source md (md5 hit)
  - orphan_pdf:   PDF on disk with no matching source md (needs ingest)
  - true_orphan:  source md whose md5 has no PDF on disk AND no
                  resolvable `path:` field — the frontmatter is broken
                  or the PDF was re-downloaded under a new name
                  (wiki page is stale; needs fix)
  - archived:     source md whose md5 has no PDF on disk BUT the
                  `path:` field still points at a known-deleted file
                  (md is kept as a historical record; NOT a bug)

The `path:` field in legacy frontmatter is RELATIVE TO raw/PDFs/, e.g.
  path: books/foo.pdf
NOT the path relative to the repo root. This script normalizes both.
"""

from __future__ import annotations  # X | None on py<3.10

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PYRAMID = Path(__file__).resolve().parent.parent
# Raw source roots to scan for source files. pyramid AGENT.md declares the
# source layer as `raw/`, and any subdir may hold PDF or .md source files.
# Sub-dirs that have NO source files today (e.g. raw/Modern-Cpp-Skills/) are
# kept in the list so future ingests are picked up automatically.
RAW_ROOTS = [
    PYRAMID / "raw" / "PDFs",
    PYRAMID / "raw" / "notes",
    PYRAMID / "raw" / "Modern-Cpp-Skills",
    PYRAMID / "raw" / "github",
    PYRAMID / "raw" / "workflow",
    PYRAMID / "raw" / "safeos",
]
# File suffixes recognised as ingest source files for md5 coverage.
# .pdf = classic PDF papers/books; .md = GitHub README / SKILL.md type sources.
SOURCE_SUFFIXES = {".pdf", ".md"}
# Subdirs (relative to PYRAMID/raw/) under which .md files are NOT treated
# as ingest sources. These are research-note / project-note directories —
# .md files there are downstream analysis, not the original source material.
# PDFs inside them are still scanned normally.
MD_EXCLUDE_ROOTS = {
    PYRAMID / "raw" / "notes",
    PYRAMID / "raw" / "safeos",
    PYRAMID / "raw" / "workflow",
}
# .md subdirs (relative to a root) to skip even where .md scanning is on.
# These appear under raw/github/ where clone structures embed research notes
# alongside the actual repo content.
MD_EXCLUDE_SUBDIRS = {"notes", "papers", "research"}
SOURCES = PYRAMID / "wiki" / "sources"

MD5_RE = re.compile(r"^source-md5:\s*([a-f0-9]{32})", re.M | re.I)
PATH_RE = re.compile(r"^path:\s*(.+)$", re.M)


def file_md5(p: Path) -> str:
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_sources() -> Dict[Path, str]:
    """Return {source_path: md5} for all source files (.pdf, .md) under every
    configured raw root.

    .md scanning is opt-in per root: only raw/PDFs, raw/Modern-Cpp-Skills, and
    raw/github are treated as candidate locations for ingest-source .md files
    (e.g. GitHub READMEs and SKILL.md docs). The research-note roots
    (raw/notes, raw/safeos, raw/workflow) are excluded from .md scanning
    because their .md files are downstream analysis, not original sources —
    PDFs inside them are still scanned.

    Within .md-scanned roots we further skip:
      - `.meta.md` files (repo metadata, not source content)
      - any path that descends through a `notes/`, `papers/`, or `research/`
        subdir (research notes embedded inside a clone)
    """
    out: Dict[Path, str] = {}
    for root in RAW_ROOTS:
        if not root.exists():
            continue
        scan_md = root not in MD_EXCLUDE_ROOTS
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in SOURCE_SUFFIXES:
                continue
            if p.suffix.lower() == ".md" and not scan_md:
                continue
            if p.suffix.lower() == ".md":
                if p.name == ".meta.md":
                    continue
                parts_lower = {part.lower() for part in p.relative_to(root).parts}
                if parts_lower & MD_EXCLUDE_SUBDIRS:
                    continue
            out[p] = file_md5(p)
    return out


def collect_md_index() -> Tuple[Dict[str, List[Path]], Dict[Path, str]]:
    """Return ({md5: [md_paths]}, {md_path: relative_path_str_from_md})."""
    md5_index: dict[str, list[Path]] = {}
    md_paths: dict[Path, str] = {}
    if not SOURCES.exists():
        return md5_index, md_paths
    for md in SOURCES.glob("*.md"):
        txt = md.read_text(errors="ignore")
        for h in MD5_RE.findall(txt):
            md5_index.setdefault(h.lower(), []).append(md)
        for line in PATH_RE.findall(txt):
            # Frontmatter uses `path:` followed by a SINGLE file (may contain
            # spaces/commas in filename, no escaping). Don't split on commas
            # — that would mangle filenames like "21st Century C, 2nd Edition.pdf".
            # Strip trailing /* and surrounding whitespace.
            p = line.strip().rstrip("/*").strip()
            if p:
                md_paths[md] = p
                break
    return md5_index, md_paths


def resolve_md_path_to_disk(path_str: str) -> Optional[Path]:
    """Resolve a frontmatter `path:` string to a real PDF on disk, or None.

    Tolerates:
      - absolute paths
      - paths starting with raw/ or raw/PDFs/
      - paths relative to raw/PDFs/ (the convention)
      - bare basenames (path: 2nd Edition.pdf) — matched by filename in any subdir

    Some legacy frontmatter pages store only the basename (e.g.
    `path: 2nd Edition.pdf` from older ingest scripts that didn't include
    the books/ prefix). We still want to count those as covered when a PDF
    with that name exists anywhere under raw/PDFs/.
    """
    if not path_str:
        return None
    p = Path(path_str)
    if p.is_absolute() and p.exists():
        return p

    candidates = [
        PYRAMID / path_str,
        PYRAMID / "raw" / "PDFs" / path_str,
    ]
    for c in candidates:
        try:
            if c.exists() and c.is_file():
                return c
        except OSError:
            continue

    # Fallback: bare basename — search all raw roots for a matching file
    # (case-insensitive). Only do this if the path has no directory component,
    # to avoid spurious matches for short common names.
    if "/" not in path_str and "\\" not in path_str:
        target = Path(path_str).name.lower()
        for root in RAW_ROOTS:
            if not root.exists():
                continue
            for pdf in root.rglob("*.pdf"):
                if pdf.name.lower() == target:
                    return pdf
    return None


def coverage_report() -> dict:
    sources = collect_sources()
    md5_index, md_paths = collect_md_index()

    # Build a fast set of all existing source file paths (absolute) for
    # path-based lookup. Variable is named `pdfs` for historical reasons but
    # now also includes .md source files (GitHub READMEs, SKILL.md, etc.).
    pdfs = sources
    pdf_abs_paths = {p.resolve() for p in pdfs}

    # For each PDF, also build a "matched-by" reason so the report is honest
    # about WHY a PDF is considered covered (md5 vs path)
    covered: List[Path] = []
    orphan_pdfs: List[Path] = []
    cover_reason: dict[Path, str] = {}

    for p, h in pdfs.items():
        if h in md5_index:
            covered.append(p)
            cover_reason[p] = "md5"
            continue
        # Fallback: does any md's path field resolve to this PDF?
        matched = False
        for md, path_str in md_paths.items():
            resolved = resolve_md_path_to_disk(path_str)
            if resolved and resolved.resolve() == p.resolve():
                covered.append(p)
                cover_reason[p] = f"path:{path_str}"
                matched = True
                break
        if not matched:
            orphan_pdfs.append(p)

    orphan_mds: List[dict] = []
    true_orphans: List[dict] = []
    archived_mds: List[dict] = []
    for h, mds in md5_index.items():
        if h not in pdfs.values():
            for m in mds:
                path_field = md_paths.get(m)
                # Decide: is this a "true orphan" (broken/stale) or an
                # "archived" record (PDF was deleted, md kept on purpose)?
                #
                # Heuristic: if `path:` resolves to a real file on disk,
                # then the md5 must have changed (PDF was re-downloaded
                # under a new name) and the page is stale — call it
                # true_orphan.
                #
                # If `path:` does NOT resolve (file was deleted) AND the
                # frontmatter at least claims a sensible-looking path,
                # treat the md as an archive of a deleted source.
                #
                # If there is no `path:` field at all, treat as
                # true_orphan (the page can't even hint at where its
                # source went).
                resolved = (
                    resolve_md_path_to_disk(path_field) if path_field else None
                )
                entry = {
                    "md": str(m.relative_to(PYRAMID)),
                    "md5": h,
                    "path_field": path_field,
                }
                orphan_mds.append(entry)
                if resolved is not None:
                    # md5 mismatch but path is alive → PDF was replaced
                    # under a new name; the wiki page is stale.
                    entry["reason"] = "md5-mismatch-path-alive"
                    true_orphans.append(entry)
                elif path_field:
                    # PDF was deleted, md kept as archive.
                    entry["reason"] = "pdf-deleted-archived"
                    archived_mds.append(entry)
                else:
                    # No path field at all — frontmatter is broken.
                    entry["reason"] = "no-path-field"
                    true_orphans.append(entry)

    return {
        "total_pdfs": len(pdfs),
        "covered": len(covered),
        "cover_reasons": {str(p.relative_to(PYRAMID)): r for p, r in cover_reason.items()},
        "orphan_pdfs": [
            {
                "path": str(p.relative_to(PYRAMID)),
                "size_bytes": p.stat().st_size,
                "size_mb": round(p.stat().st_size / 1e6, 1),
            }
            for p in orphan_pdfs
        ],
        "orphan_pdf_count": len(orphan_pdfs),
        "orphan_pdf_total_bytes": sum(p.stat().st_size for p in orphan_pdfs),
        # `orphan_mds` is the union (kept for backward compat — anyone
        # grepping the JSON still finds all 245 in one place).
        "orphan_mds": orphan_mds,
        "orphan_md_count": len(orphan_mds),
        # New: split by cause. `true_orphans` are the ones that need a
        # human (broken frontmatter / re-downloaded PDF). `archived_mds`
        # are kept intentionally as historical records.
        "true_orphans": true_orphans,
        "true_orphan_count": len(true_orphans),
        "archived_mds": archived_mds,
        "archived_count": len(archived_mds),
    }


def print_report(report: dict) -> None:
    total = report["total_pdfs"]
    cov = report["covered"]
    pct = 100 * cov / total if total else 0
    true_n = report["true_orphan_count"]
    arch_n = report["archived_count"]
    print(f"=== Pyramid PDF coverage ===")
    print(f"Total PDFs:       {total}")
    print(f"Covered:          {cov}  ({pct:.1f}%)")
    print(f"Orphan PDFs:      {report['orphan_pdf_count']}  "
          f"({report['orphan_pdf_total_bytes']/1e9:.2f} GB)")
    print(f"Orphan md pages:  {report['orphan_md_count']}")
    print(f"  - [WARN]   True orphans (broken link / stale): {true_n}")
    print(f"  - [ARCHIVE] Archived (PDF deleted, md kept):    {arch_n}")

    if report["orphan_pdfs"]:
        print(f"\n--- Orphan PDFs (no source page) ---")
        for o in report["orphan_pdfs"]:
            print(f"  {o['size_mb']:6.1f} MB  {o['path']}")

    if true_n:
        print(f"\n--- [WARN] True orphans (broken links to fix) ---")
        for o in report["true_orphans"][:20]:
            print(f"  {o['md']}  (md5={o['md5'][:8]}…  path={o['path_field']!r}  reason={o['reason']})")
        if true_n > 20:
            print(f"  … and {true_n - 20} more")

    if arch_n:
        print(f"\n--- [ARCHIVE] Archived (PDF deleted, md kept as record) ---")
        # Group by canonical path so the user sees that e.g. 4 mds all
        # reference the same deleted PDF, rather than 4 scary-looking
        # lines. We canonicalize: strip leading "raw/PDFs/" since the
        # `path:` field is documented as relative to raw/PDFs/.
        from collections import defaultdict
        grouped: dict[str, list[str]] = defaultdict(list)

        def canonical(p: str) -> str:
            if p.startswith("raw/PDFs/"):
                return p[len("raw/PDFs/"):]
            return p

        for o in report["archived_mds"]:
            key = canonical(o["path_field"] or "<no path>")
            grouped[key].append(o["md"])
        # Show first 10 distinct sources (each source may map to N mds)
        items = list(grouped.items())
        shown_md = sum(len(v) for _, v in items[:10])
        for path, mds in items[:10]:
            label = path if path else "<no path>"
            print(f"  📁 {label}  ({len(mds)} md page{'s' if len(mds) != 1 else ''})")
            for md in mds[:3]:
                print(f"        - {md}")
            if len(mds) > 3:
                print(f"        - … and {len(mds) - 3} more md page(s)")
        if len(grouped) > 10:
            print(f"  📁 … and {len(grouped) - 10} more deleted source(s) "
                  f"(covering {arch_n - shown_md} md pages)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "Pyramid PDF coverage report")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of human report")
    ap.add_argument("--delete-orphans", action="store_true",
                    help="DANGER: delete orphan PDFs from disk after reporting")
    args = ap.parse_args()

    report = coverage_report()

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_report(report)

    if args.delete_orphans:
        if not args.json:
            print(f"\n!!! Deleting {report['orphan_pdf_count']} orphan PDFs !!!")
        for o in report["orphan_pdfs"]:
            Path(o["path"]).unlink(missing_ok=True)
            if not args.json:
                print(f"  rm {o['path']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
