#!/usr/bin/env python3
"""list_orphan_md_groups.py — Dump orphan md pages grouped by md5 for review.

Reuses pdf_coverage.collect_sources() and collect_md_index() to identify
orphan md pages, then groups them by md5 and ranks each group by
"completeness" so the reviewer can pick KEEP candidates.

DOES NOT delete anything. Output is purely informational.

Outputs:
  /tmp/orphan_md_groups.md     — human readable table
  /tmp/orphan_md_groups.json   — structured machine-readable

Usage:
  python3 scripts/list_orphan_md_groups.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Reuse the authoritative functions from pdf_coverage so we don't drift
from pdf_coverage import collect_sources, collect_md_index, PYRAMID  # noqa: E402

# ---------- frontmatter parsing ----------
FENCE_RE = re.compile(r"^---\s*$(.*?)^---\s*$", re.M | re.S)
# Map a frontmatter key to a regex that captures its value (scalar or [list]).
KV_RE_TPL = r"^{key}:\s*(.+?)\s*$"


def parse_frontmatter(text: str) -> Dict[str, str]:
    """Return a flat dict of frontmatter key → raw value string.

    Only the first fenced block is parsed. Values are kept as the original
    scalar text (lists, scalars, dates) — we do not coerce.
    """
    m = FENCE_RE.search(text)
    if not m:
        return {}
    block = m.group(1)
    out: Dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip().lower()
        v = v.strip()
        if k:
            out.setdefault(k, v)
    return out


def body_after_frontmatter(text: str) -> str:
    """Return the body of the md file after the frontmatter fence."""
    m = FENCE_RE.search(text)
    if not m:
        return text
    return text[m.end():].strip()


# ---------- completeness scoring ----------
def completeness_score(md: Path) -> Tuple[int, int, int, int]:
    """Return (has_source_md5, has_tags, has_path, body_len) for ranking.

    Higher tuple → better. Used to pick the KEEP candidate per group.
    """
    try:
        text = md.read_text(errors="ignore")
    except OSError:
        return (0, 0, 0, 0)
    fm = parse_frontmatter(text)
    has_md5 = 1 if "source-md5" in fm else 0
    has_tags = 1 if "tags" in fm else 0
    has_path = 1 if "path" in fm else 0
    body_len = len(body_after_frontmatter(text))
    return (has_md5, has_tags, has_path, body_len)


def short_summary(md: Path) -> str:
    """One-line digest for the report: frontmatter + first 100 body chars."""
    try:
        text = md.read_text(errors="ignore")
    except OSError:
        return "<unreadable>"
    fm = parse_frontmatter(text)
    body = body_after_frontmatter(text)
    head = body[:100].replace("\n", " ").strip()
    bits = []
    for k in ("title", "source-type", "type", "size", "source-md5", "path"):
        if k in fm:
            v = fm[k]
            if len(v) > 60:
                v = v[:57] + "..."
            bits.append(f"{k}={v}")
    summary = "  ".join(bits) if bits else "(no frontmatter)"
    if head:
        summary += f"  | {head}"
    return summary


# ---------- grouping ----------
def group_orphans() -> List[dict]:
    """Return a list of groups, each with md5 + sorted member mds."""
    sources = collect_sources()
    md5_index, md_paths = collect_md_index()
    pdf_md5s = set(sources.values())

    # Collect orphan mds keyed by md5
    orphan_by_md5: Dict[str, List[Path]] = {}
    for h, mds in md5_index.items():
        if h in pdf_md5s:
            continue
        orphan_by_md5.setdefault(h, []).extend(mds)

    def sort_key(p: Path):
        # Higher tuple → better. Sort DESC by (has_md5, has_tags, has_path, body_len).
        # Tiebreak: shorter name first (KEEP should be a clean slug, not a
        # legacy file-prefixed name).
        sc = completeness_score(p)
        return (sc[0], sc[1], sc[2], sc[3], -len(p.name))

    groups = []
    for h, mds in orphan_by_md5.items():
        ranked = sorted(mds, key=sort_key, reverse=True)

        keep = ranked[0] if ranked else None
        del_candidates = ranked[1:] if len(ranked) > 1 else []
        groups.append({
            "md5": h,
            "count": len(mds),
            "keep": str(keep.relative_to(PYRAMID)) if keep else None,
            "del_candidates": [str(p.relative_to(PYRAMID)) for p in del_candidates],
            "members": [
                {
                    "path": str(p.relative_to(PYRAMID)),
                    "score": completeness_score(p),
                    "summary": short_summary(p),
                    "verdict": "KEEP" if p == keep else ("DEL?" if p in del_candidates else "?"),
                }
                for p in ranked
            ],
        })

    # Sort groups: largest first, then by md5 for determinism
    groups.sort(key=lambda g: (-g["count"], g["md5"]))
    return groups


# ---------- output ----------
def write_markdown(groups: List[dict], out_path: Path) -> None:
    total_md = sum(g["count"] for g in groups)
    lines: List[str] = []
    lines.append("# Orphan md pages (by md5 group) — READ-ONLY REVIEW\n")
    lines.append("Generated by `scripts/list_orphan_md_groups.py`. Nothing is deleted.\n")
    lines.append(f"**Total orphan md pages:** {total_md}  ")
    lines.append(f"**Unique md5 groups:**     {len(groups)}  ")
    total_del_candidates = sum(max(0, g["count"] - 1) for g in groups)
    lines.append(f"**Auto DEL? candidates (keep 1 per group):** {total_del_candidates}  ")
    lines.append("")
    lines.append("KEEP = highest completeness score in its group "
                 "(source-md5 present, tags present, path present, body longest).  ")
    lines.append("DEL? = other members of the same group.\n")

    # Histogram of group sizes
    hist: Dict[int, int] = {}
    for g in groups:
        hist[g["count"]] = hist.get(g["count"], 0) + 1
    lines.append("## Group size distribution\n")
    lines.append("| group size | # groups | total mds |")
    lines.append("|------------|----------|----------|")
    for size in sorted(hist.keys(), reverse=True):
        n_groups = hist[size]
        n_mds = size * n_groups
        lines.append(f"| {size} | {n_groups} | {n_mds} |")
    lines.append("")

    lines.append("## Groups (largest first)\n")
    for g in groups:
        lines.append(f"### md5 `{g['md5']}` — {g['count']} files\n")
        if g["keep"]:
            lines.append(f"**Suggested KEEP:** `{g['keep']}`\n")
        for m in g["members"]:
            sc = m["score"]
            lines.append(
                f"- {m['verdict']:5s} `{m['path']}`  "
                f"(md5={sc[0]} tags={sc[1]} path={sc[2]} body={sc[3]}c)"
            )
        lines.append("")
        for m in g["members"]:
            lines.append(f"    {m['summary']}")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_json(groups: List[dict], out_path: Path) -> None:
    payload = {
        "total_orphan_md": sum(g["count"] for g in groups),
        "unique_md5_groups": len(groups),
        "auto_del_candidates": sum(max(0, g["count"] - 1) for g in groups),
        "groups": groups,
    }
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    groups = group_orphans()

    md_path = Path("/tmp/orphan_md_groups.md")
    json_path = Path("/tmp/orphan_md_groups.json")
    write_markdown(groups, md_path)
    write_json(groups, json_path)

    total_md = sum(g["count"] for g in groups)
    del_n = sum(max(0, g["count"] - 1) for g in groups)
    print(f"orphan md total : {total_md}")
    print(f"unique md5 grps : {len(groups)}")
    print(f"DEL? candidates : {del_n}")
    print(f"wrote {md_path}")
    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
