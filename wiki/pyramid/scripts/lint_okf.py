#!/usr/bin/env python3
"""lint_okf.py — OKF (Open Knowledge Format) frontmatter linter.

Scans a knowledge pack's wiki/ directory, validates every Markdown
file's YAML frontmatter against the OKF v0.1 contract declared in
okf.yaml, and reports issues.

Usage:
  python3 scripts/lint_okf.py                 # default: check
  python3 scripts/lint_okf.py --check         # explicit check
  python3 scripts/lint_okf.py --check --strict  # warnings → errors
  python3 scripts/lint_okf.py --stats         # show page-type stats
  python3 scripts/lint_okf.py --fix-known     # auto-fix common issues
                                               # (missing type:, missing
                                               #  index frontmatter on
                                               #  *-index.md files)

Exit codes:
  0 = OK (or only warnings in non-strict mode)
  1 = issues found
  2 = okf.yaml not found or invalid

Limitations (intentional, by Simplicity First):
  - Pure stdlib (no PyYAML dependency) — uses a minimal YAML reader
    sufficient for the frontmatter shapes pyramid uses. For heavy
    YAML, run `python3 -m pip install pyyaml` and we'll use it.
  - Only validates frontmatter, not wikilink integrity (separate
    lint for that).

Style: matches scripts/ingest_pdf.py (stdlib, env-driven, simple).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

# ---------- Defaults overridable by env ----------
# Resolve REPO_ROOT by walking up from this script to find the nearest
# okf.yaml. Falls back to the script's grandparent.
SCRIPT_DIR = Path(__file__).resolve().parent
_candidate = SCRIPT_DIR.parent
while _candidate != _candidate.parent:
    if (_candidate / "okf.yaml").exists():
        break
    _candidate = _candidate.parent
REPO_ROOT = Path(os.environ.get("PYRAMID_ROOT", _candidate))
OKF_YAML = Path(os.environ.get("OKF_META", REPO_ROOT / "okf.yaml"))


def _resolve_wiki_root(repo_root: Path, okf_yaml: Path) -> Path:
    """Pick wiki_root from env, then okf.yaml's layout, then <repo>/wiki."""
    env = os.environ.get("OKF_WIKI_ROOT")
    if env:
        return Path(env)
    if okf_yaml.exists():
        try:
            text = okf_yaml.read_text(encoding="utf-8")
            in_layout = False
            for raw in text.splitlines():
                line = raw.rstrip()
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if line.startswith("layout:"):
                    in_layout = True
                    continue
                if in_layout and not line.startswith(" "):
                    in_layout = False
                if in_layout and stripped.startswith("wiki_root:"):
                    val = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                    return (repo_root / val).resolve()
        except Exception:
            pass
    return repo_root / "wiki"


WIKI_ROOT = _resolve_wiki_root(REPO_ROOT, OKF_YAML)

# ---------- Minimal frontmatter parser ----------
# We don't require PyYAML. This parser handles the simple shapes OKF
# recommends: scalar values, inline lists `[a, b, c]`, and string
# quoting. It's intentionally conservative — if a file has a shape we
# don't understand, we warn but don't crash.

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
INLINE_LIST_RE = re.compile(r"^\s*\[(.+?)\]\s*$")


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def parse_frontmatter(text: str) -> dict | None:
    """Parse a YAML frontmatter block. Returns dict or None if missing."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    block = m.group(1)
    out: dict = {}
    current_list_key: str | None = None
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip():
            current_list_key = None
            continue
        # list continuation under a previously seen key
        if line.lstrip().startswith("- ") and current_list_key:
            val = _strip_quotes(line.lstrip()[2:])
            out.setdefault(current_list_key, []).append(val)
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        current_list_key = None
        if not value:
            # could be start of a block-style list on next lines
            current_list_key = key
            out.setdefault(key, [])
            continue
        # inline list
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if inner:
                items = [_strip_quotes(x) for x in inner.split(",")]
                out[key] = items
            else:
                out[key] = []
            continue
        out[key] = _strip_quotes(value)
    return out


# ---------- okf.yaml parser (also minimal) ----------
def load_okf_meta(path: Path) -> dict:
    """Parse okf.yaml with a flat-ish model.

    Strategy: walk every non-blank, non-comment line. For each line:
      - If it has no leading whitespace, it's a top-level key.
        * value present  →  out[key] = value
        * value empty    →  out[key] = {} (section to fill), set
                             current_section so subsequent 2-space-indent
                             items route into it.
      - If line has 2-space indent and starts with "- " and we're inside
        a section: append to the section's list. (We treat list-items
        at section level as the section's primary value.)
      - If line has 2-space indent and has "key: value" and we're
        inside a section: store as section[key] = value (sub-dict).
    """
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    out: dict = {}
    current_section: str | None = None
    section_lists: dict[str, list] = {}  # section → in-progress list
    for raw in text.splitlines():
        line = raw.rstrip()
        # strip end-of-line comments (but keep "#" inside quoted strings)
        if "#" in line and not (line.count('"') % 2):
            # crude: only strip if # is preceded by whitespace
            import re as _re
            line = _re.sub(r"\s+#.*$", "", line)
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" "):
            # top-level
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                # section start
                current_section = key
                out.setdefault(key, {})
                section_lists[key] = []
            else:
                current_section = None
                value = _strip_quotes(value)
                if value.startswith("[") and value.endswith("]"):
                    inner = value[1:-1].strip()
                    out[key] = [_strip_quotes(x) for x in inner.split(",")] if inner else []
                else:
                    out[key] = value
        else:
            # indented line belongs to current section
            if current_section is None:
                continue
            content = line.lstrip()
            if content.startswith("- "):
                val = _strip_quotes(content[2:])
                section_lists.setdefault(current_section, []).append(val)
                # If section is empty dict, promote to list
                if isinstance(out.get(current_section), dict) and not out[current_section]:
                    pass  # keep building list separately
                else:
                    # append to section's list value if it's already a list
                    if isinstance(out.get(current_section), list):
                        out[current_section].append(val)
                    else:
                        out[current_section] = section_lists[current_section]
            elif ":" in content:
                k, _, v = content.partition(":")
                k = k.strip()
                v = v.strip()
                if v == "":
                    # nested sub-section; we don't support deeper nesting
                    continue
                v = _strip_quotes(v)
                if v.startswith("[") and v.endswith("]"):
                    inner = v[1:-1].strip()
                    out[current_section][k] = (
                        [_strip_quotes(x) for x in inner.split(",")] if inner else []
                    )
                else:
                    out[current_section][k] = v

    # Finalize: if any section has accumulated list items and the
    # section dict is empty, promote to the list.
    for sec, items in section_lists.items():
        if items and (not out.get(sec) or out[sec] == {}):
            out[sec] = items
    return out


# ---------- Lint logic ----------
def iter_markdown(root: Path):
    """Yield .md files under `root`, skipping hidden dirs and raw sources.

    OKF convention: raw/ is immutable source material, not part of
    the knowledge pack. We skip any directory literally named `raw/`
    or `wiki/raw/`. Sub-paths like wiki/raw/2026-05-.../foo.md are
    raw research notes and should not be linted.
    """
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        parts = rel.parts
        # skip hidden dirs (e.g., .obsidian, .vscode)
        if any(part.startswith(".") for part in parts):
            continue
        # skip raw sources (OKF: immutable, not a concept page)
        if "raw" in parts:
            continue
        yield path


def lint_file(path: Path, allowed_types: set[str], required_by_type: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings).

    Errors: structural problems that violate OKF v0.1 minimum
      (missing frontmatter, missing/wrong type).
    Warnings: type-specific field gaps (recommended but not
      OKF-mandatory) and naming inconsistencies.
    """
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"{path}: read error: {e}"], []

    fm = parse_frontmatter(text)
    rel = path.relative_to(REPO_ROOT)

    if fm is None:
        errors.append(f"{rel}: missing YAML frontmatter")
        return errors, warnings

    # type is the only OKF-mandatory field
    t = fm.get("type")
    if not t:
        errors.append(f"{rel}: missing required field 'type'")
    elif t not in allowed_types:
        errors.append(f"{rel}: type='{t}' not in allowed set {sorted(allowed_types)}")

    # Type-specific recommended fields (warn, don't error)
    if t in required_by_type:
        for field in required_by_type[t]:
            if field == "type":  # already checked
                continue
            if field not in fm:
                warnings.append(f"{rel}: type='{t}' missing recommended field '{field}'")

    # Heuristic: *-index.md without type=index
    name = path.name
    if name.endswith("-index.md") and t and t != "index":
        warnings.append(
            f"{rel}: filename suggests type=index but frontmatter says type='{t}' "
            f"(run with --fix-known to auto-correct)"
        )
    if name == "log.md" and t and t != "log":
        warnings.append(f"{rel}: log.md should have type='log', got '{t}'")

    return errors, warnings


def fix_known_issues(path: Path) -> bool:
    """Auto-fix a few common cases. Returns True if file was modified."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return False
    m = FRONTMATTER_RE.match(text)
    if not m:
        return False
    block = m.group(1)
    new_block = block
    changed = False

    # Fix: *-index.md with type != index
    if path.name.endswith("-index.md"):
        if re.search(r"^type:\s*\S+", new_block, re.MULTILINE) and not re.search(
            r"^type:\s*index\b", new_block, re.MULTILINE
        ):
            new_block = re.sub(r"^type:\s*\S+", "type: index", new_block, count=1, flags=re.MULTILINE)
            changed = True

    # Fix: log.md with type != log
    if path.name == "log.md":
        if re.search(r"^type:\s*\S+", new_block, re.MULTILINE) and not re.search(
            r"^type:\s*log\b", new_block, re.MULTILINE
        ):
            new_block = re.sub(r"^type:\s*\S+", "type: log", new_block, count=1, flags=re.MULTILINE)
            changed = True

    if not changed:
        return False
    new_text = "---\n" + new_block + "\n---\n" + text[m.end():]
    path.write_text(new_text, encoding="utf-8")
    return True


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--check", action="store_true", help="check mode (default)")
    p.add_argument("--strict", action="store_true", help="treat warnings as errors")
    p.add_argument("--stats", action="store_true", help="print page-type statistics")
    p.add_argument("--fix-known", action="store_true", help="auto-fix common issues")
    p.add_argument("--wiki-root", type=Path, default=WIKI_ROOT)
    p.add_argument("--okf-meta", type=Path, default=OKF_YAML)
    args = p.parse_args(argv)

    if not args.okf_meta.exists():
        print(f"ERROR: okf metadata not found at {args.okf_meta}", file=sys.stderr)
        return 2

    meta = load_okf_meta(args.okf_meta)
    types = set(meta.get("types", []))
    required_by_type = meta.get("required_fields", {})

    if not types:
        print(f"ERROR: no 'types' declared in {args.okf_meta}", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    all_warnings: list[str] = []
    type_counter: Counter = Counter()
    file_count = 0
    for md in iter_markdown(args.wiki_root):
        file_count += 1
        fm = parse_frontmatter(md.read_text(encoding="utf-8"))
        if fm and "type" in fm:
            type_counter[fm["type"]] += 1
        if args.fix_known:
            if fix_known_issues(md):
                print(f"  fixed: {md.relative_to(REPO_ROOT)}")
                # re-read after fix
                fm = parse_frontmatter(md.read_text(encoding="utf-8"))
        errors, warnings = lint_file(md, types, required_by_type)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    if args.stats or (not args.fix_known and not all_errors and not all_warnings):
        print(f"\n=== Pack: {REPO_ROOT.name} ===")
        print(f"Wiki root: {args.wiki_root}")
        print(f"Files scanned: {file_count}")
        print(f"Types declared: {sorted(types)}")
        print("\nPage type distribution:")
        for t, n in sorted(type_counter.items(), key=lambda x: -x[1]):
            bar = "█" * min(50, n)
            print(f"  {t:<14} {n:>4}  {bar}")

    if all_warnings:
        print(f"\n=== Warnings ({len(all_warnings)}) ===", file=sys.stderr)
        for w in all_warnings:
            print(f"  ⚠ {w}", file=sys.stderr)

    if all_errors:
        print(f"\n=== Errors ({len(all_errors)}) ===", file=sys.stderr)
        for e in all_errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    if args.strict and all_warnings:
        return 1

    if not args.stats and not all_warnings:
        print(f"\n✓ All {file_count} files pass OKF frontmatter lint")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
