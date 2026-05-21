#!/usr/bin/env python3
"""生成 pyramid PDF 目录索引页 — wiki/pdf-index.md

扫描 raw/PDFs/{books,papers,slides}/ 下所有 PDF，
生成带分类表格的 Obsidian 索引页面。
"""

import os
from datetime import datetime

LLM_WIKI = os.path.expanduser("~/pyramid")
PDF_DIR = os.path.join(LLM_WIKI, "raw", "PDFs")
OUTPUT = os.path.join(LLM_WIKI, "wiki", "pdf-index.md")

CATEGORY_LABELS = {
    "books":  "书籍 / 教材",
    "papers": "学术论文",
    "slides": "演讲 Slides",
}

def get_size_mb(path):
    size = os.path.getsize(path)
    return round(size / 1024 / 1024, 1)

def generate():
    lines = []
    lines.append("---")
    lines.append("type: index")
    lines.append("tags: [pdf, catalog]")
    lines.append(f"updated: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("---")
    lines.append("")
    lines.append("# PDF 目录")
    lines.append("")
    lines.append(f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')} — 运行 `python scripts/gen-pdf-catalog.py` 刷新")
    lines.append("")

    total = 0
    for cat in ["books", "papers", "slides"]:
        cat_dir = os.path.join(PDF_DIR, cat)
        if not os.path.isdir(cat_dir):
            continue
        pdfs = sorted([f for f in os.listdir(cat_dir) if f.endswith(".pdf")])
        if not pdfs:
            continue

        lines.append(f"## {CATEGORY_LABELS.get(cat, cat)} ({len(pdfs)})")
        lines.append("")
        lines.append("| # | 文件 | 大小 |")
        lines.append("|---|------|------|")

        for i, pdf in enumerate(pdfs, 1):
            path = os.path.join(cat_dir, pdf)
            size = get_size_mb(path)
            # 使用 file:// 链接让 Obsidian 可点击打开
            file_url = f"file://{path}"
            lines.append(f"| {i} | [{pdf}]({file_url}) | {size} MB |")

        lines.append("")
        total += len(pdfs)

    lines.append(f"> 共 {total} 个 PDF")
    lines.append("")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated: {OUTPUT}")
    print(f"  books:  {len([f for f in os.listdir(os.path.join(PDF_DIR, 'books')) if f.endswith('.pdf')]) if os.path.isdir(os.path.join(PDF_DIR, 'books')) else 0}")
    print(f"  papers: {len([f for f in os.listdir(os.path.join(PDF_DIR, 'papers')) if f.endswith('.pdf')]) if os.path.isdir(os.path.join(PDF_DIR, 'papers')) else 0}")
    print(f"  slides: {len([f for f in os.listdir(os.path.join(PDF_DIR, 'slides')) if f.endswith('.pdf')]) if os.path.isdir(os.path.join(PDF_DIR, 'slides')) else 0}")
    print(f"  total:  {total}")

if __name__ == "__main__":
    generate()
