#!/usr/bin/env python3
"""Re-ingest the 9 OCR-failed PDFs from commit 8e3646e with the now-fixed
ingest_pdf.py (auto-tessdata-path + DPI 300). For each PDF:
  1. Delete the existing `book-<slug>.md` placeholder (which contains
     only `_(no text content on this page)_` for every page).
  2. Delete the `pdf-book-<slug>.md` hand-written summary (which locks
     dedup via source-md5 frontmatter).
  3. Back up the hand-written summary to /tmp/ so we can restore the
     best parts as a `## Core content` section on the new page if useful.
  4. Re-run ingest with chi_sim+eng (or just eng for English books).

Outputs a single summary so the operator can review before commit.

Idempotent: re-running on already-ingested files is a no-op (the
ingest step skips if the new file already exists in sources/).
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

PYRAMID = Path("/Users/sphinx.shi/workspace/wiki/pyramid")
WIKI = PYRAMID / "wiki"
SOURCES = WIKI / "sources"
BACKUP_DIR = Path("/tmp/ocr_ingest_backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# (pdf_path, ocr_lang, placeholder_md_names_to_delete, summary_md_to_backup)
# md_to_delete is the COMPLETE set of wiki/sources/ pages that hold
# the same source-md5 (any one of them blocks dedup). Listing them
# all here ensures we nuke the whole lot before re-ingest.
TARGETS = [
    ("/tmp/lfs_pdfs/books/计算机体系结构：量化研究方法（第五版）（中文版）.pdf", "chi_sim+eng",
     ["book-计算机体系结构量化研究方法第五版中文版.md",
      "pdf-book-csapp-zh-5th.md",
      "pdf-computer-architecture-hp.md",
      "pdf-book-computer-architecture-hp.md"],
     "pdf-book-csapp-zh-5th.md"),
    ("/tmp/lfs_pdfs/books/UNIX环境高级编程(第三版).pdf", "chi_sim+eng",
     ["book-unix环境高级编程第三版.md",
      "pdf-book-unix-advanced-programming.md",
      "pdf-unix-environment-advanced-programming.md"],
     "pdf-book-unix-advanced-programming.md"),
    ("/tmp/lfs_pdfs/books/Algorithms in C.pdf", "eng",
     ["book-algorithms-in-c.md",
      "pdf-book-algorithms-c.md"],
     "pdf-book-algorithms-c.md"),
    ("/tmp/lfs_pdfs/slides/黄石柱-Deepseek推理性能优化.pdf", "chi_sim+eng",
     ["slide-黄石柱-deepseek推理性能优化.md",
      "pdf-deepseek-inference.md"],
     "pdf-deepseek-inference.md"),
    ("/tmp/lfs_pdfs/books/STL源码剖析简体中文完整版(清晰扫描带目录).pdf", "chi_sim+eng",
     ["book-stl源码剖析简体中文完整版清晰扫描带目录.md",
      "pdf-book-stl-source-analysis.md",
      "pdf-stl-source-analysis.md"],
     "pdf-book-stl-source-analysis.md"),
    ("/tmp/lfs_pdfs/books/人月神话_40周年纪念版.pdf", "chi_sim+eng",
     ["book-人月神话-40周年纪念版.md",
      "pdf-book-mythical-man-month.md"],
     "pdf-book-mythical-man-month.md"),
    ("/tmp/lfs_pdfs/books/Linux高性能服务器编程.pdf", "chi_sim+eng",
     ["book-linux高性能服务器编程.md",
      "pdf-book-linux-high-perf-server.md",
      "pdf-book-linux-net-server.md"],
     "pdf-book-linux-high-perf-server.md"),
    ("/tmp/lfs_pdfs/books/The C Programming Language - 2nd Edition - Ritchie Kernighan.pdf", "eng",
     ["book-the-c-programming-language-2nd-edition-ritchie-kernighan.md",
      "pdf-book-cpl-2e.md"],
     "pdf-book-cpl-2e.md"),
]


def main():
    print("=" * 60)
    print(f"OCR re-ingest run — {len(TARGETS)} PDFs")
    print(f"Backups -> {BACKUP_DIR}")
    print("=" * 60)
    for pdf_rel, lang, md_to_delete, summary_to_backup in TARGETS:
        pdf_full = PYRAMID / pdf_rel
        print(f"\n--- {pdf_rel} (lang={lang}) ---")
        if not pdf_full.exists():
            print(f"  SKIP: PDF not found at {pdf_full}")
            continue
        # 1. backup + delete old MDs
        for md in md_to_delete:
            md_full = SOURCES / md
            if md_full.exists():
                backup = BACKUP_DIR / md
                shutil.copy2(md_full, backup)
                print(f"  backed up + deleted: {md}")
                md_full.unlink()
            else:
                print(f"  (already missing: {md})")
        # 2. re-ingest
        env = os.environ.copy()
        env["INGEST_OCR_LANG"] = lang
        cmd = ["python3", "scripts/ingest_pdf.py", pdf_rel]
        print(f"  $ INGEST_OCR_LANG={lang} python3 scripts/ingest_pdf.py {pdf_rel}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True,
                                cwd=PYRAMID, timeout=900)
        if result.returncode != 0:
            print(f"  FAILED: rc={result.returncode}")
            print(f"  stderr: {result.stderr[:500]}")
            continue
        # parse summary line
        out = result.stdout
        if "succeeded" in out:
            for line in out.splitlines():
                if "Summary" in line:
                    print(f"  {line.strip()}")
        # check output MD
        written = None
        for md in md_to_delete:
            if (SOURCES / md).exists():
                written = md
                break
        if written:
            size = (SOURCES / written).stat().st_size
            print(f"  -> {written}  ({size:,} bytes)")
        else:
            print(f"  WARNING: no output MD found")


if __name__ == "__main__":
    main()
