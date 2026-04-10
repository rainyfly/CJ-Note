#!/usr/bin/env python3
"""
update_index.py — Auto-update CJ-Note homepage from report meta tags.

Usage:
    python scripts/update_index.py              # scan reports/, update index.html
    python scripts/update_index.py --dry-run    # preview what would change
    python scripts/update_index.py --verbose    # show each report found

Each report HTML must contain these <meta> tags in its <head>:
    <meta name="report-title"  content="...">
    <meta name="report-type"   content="repo | paper | feature">
    <meta name="report-date"   content="YYYY-MM-DD">
    <meta name="report-tags"   content="Tag1, Tag2, Tag3">
    <meta name="report-desc"   content="One-sentence description.">

Reports missing required meta tags are skipped with a warning.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).parent.parent
REPORTS_DIR = REPO_ROOT / "reports"
INDEX_FILE  = REPO_ROOT / "index.html"

REQUIRED_META = ["report-title", "report-type", "report-date"]
OPTIONAL_META = ["report-tags", "report-desc"]
VALID_TYPES   = {"repo", "paper", "feature"}


# ── Parsing ────────────────────────────────────────────────────────────────

def extract_meta(html: str, name: str) -> str | None:
    """Extract content of <meta name="..." content="..."> (case-insensitive)."""
    pattern = rf'<meta\s+name=["\']?{re.escape(name)}["\']?\s+content=["\']([^"\']*)["\']'
    m = re.search(pattern, html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # also try reversed attribute order: content first, then name
    pattern2 = rf'<meta\s+content=["\']([^"\']*)["\']?\s+name=["\']?{re.escape(name)}["\']?'
    m2 = re.search(pattern2, html, re.IGNORECASE)
    return m2.group(1).strip() if m2 else None


def parse_report(path: Path) -> dict | None:
    """Parse a report HTML file and return its metadata dict, or None on error."""
    try:
        html = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  [WARN] Cannot read {path.name}: {e}", file=sys.stderr)
        return None

    meta = {}
    for key in REQUIRED_META + OPTIONAL_META:
        meta[key] = extract_meta(html, key)

    # Validate required fields
    missing = [k for k in REQUIRED_META if not meta.get(k)]
    if missing:
        print(f"  [SKIP] {path.name}: missing meta tags: {', '.join(missing)}", file=sys.stderr)
        return None

    report_type = meta["report-type"].lower()
    if report_type not in VALID_TYPES:
        print(f"  [SKIP] {path.name}: unknown report-type '{report_type}' "
              f"(expected: {', '.join(sorted(VALID_TYPES))})", file=sys.stderr)
        return None

    # Parse tags: "Tag1, Tag2" -> ["Tag1", "Tag2"]
    raw_tags = meta.get("report-tags") or ""
    tags = [t.strip() for t in raw_tags.split(",") if t.strip()] if raw_tags else []

    # Relative path from repo root (for href in index.html)
    rel_path = path.relative_to(REPO_ROOT).as_posix()

    return {
        "title": meta["report-title"],
        "file":  rel_path,
        "type":  report_type,
        "date":  meta["report-date"],
        "tags":  tags,
        "desc":  meta.get("report-desc") or "",
    }


# ── Index update ───────────────────────────────────────────────────────────

# Marker lines in index.html that wrap the REPORTS array
_REPORTS_START = "const REPORTS = ["
_REPORTS_END   = "];"


def build_reports_js(reports: list[dict]) -> str:
    """Render the REPORTS JS array content (everything between [ and ])."""
    if not reports:
        return "\n  // No reports yet.\n"

    lines = ["\n"]
    for r in reports:
        # Escape for JS string safety
        def esc(s: str) -> str:
            return s.replace("\\", "\\\\").replace('"', '\\"')

        tags_js = ", ".join(f'"{esc(t)}"' for t in r["tags"])
        lines.append("  {")
        lines.append(f'    title: "{esc(r["title"])}",')
        lines.append(f'    file:  "{esc(r["file"])}",')
        lines.append(f'    type:  "{esc(r["type"])}",')
        lines.append(f'    date:  "{esc(r["date"])}",')
        lines.append(f'    tags:  [{tags_js}],')
        lines.append(f'    desc:  "{esc(r["desc"])}",')
        lines.append("  },")
    lines.append("")
    return "\n".join(lines)


def update_index(reports: list[dict], dry_run: bool = False) -> bool:
    """Inject the REPORTS array into index.html. Returns True if changed."""
    if not INDEX_FILE.exists():
        print(f"[ERROR] index.html not found at {INDEX_FILE}", file=sys.stderr)
        print("  Run the skill once to generate index.html first.", file=sys.stderr)
        return False

    html = INDEX_FILE.read_text(encoding="utf-8")

    # Find the REPORTS array block
    start_idx = html.find(_REPORTS_START)
    if start_idx == -1:
        print(f"[ERROR] Could not find '{_REPORTS_START}' in index.html", file=sys.stderr)
        return False

    # Find the closing ]; after the opening [
    bracket_start = html.index("[", start_idx)
    bracket_end   = html.index("];", bracket_start)  # find ]; after [

    old_block = html[bracket_start : bracket_end + 2]  # includes [ and ];
    new_inner = build_reports_js(reports)
    new_block = f"[{new_inner}];"

    if old_block == new_block:
        print("index.html is already up to date.")
        return False

    new_html = html[:bracket_start] + new_block + html[bracket_end + 2:]

    if dry_run:
        print("[DRY RUN] Would update index.html with:")
        print(f"  {len(reports)} report(s), latest: {reports[0]['date'] if reports else '—'}")
        return True

    INDEX_FILE.write_text(new_html, encoding="utf-8")
    return True


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Scan reports/ and update the REPORTS array in index.html."
    )
    parser.add_argument("--dry-run",  action="store_true",
                        help="Show what would change without writing files")
    parser.add_argument("--verbose",  action="store_true",
                        help="Print each report found")
    parser.add_argument("--reports-dir", type=Path, default=REPORTS_DIR,
                        help=f"Directory to scan (default: {REPORTS_DIR})")
    args = parser.parse_args()

    reports_dir: Path = args.reports_dir
    if not reports_dir.exists():
        print(f"[INFO] reports/ directory not found at {reports_dir} — nothing to do.")
        sys.exit(0)

    # Collect and parse all HTML files
    html_files = sorted(reports_dir.glob("*.html"))
    if not html_files:
        print(f"[INFO] No HTML files found in {reports_dir}")
        sys.exit(0)

    print(f"Scanning {len(html_files)} file(s) in {reports_dir.relative_to(REPO_ROOT)}/")

    reports = []
    for f in html_files:
        meta = parse_report(f)
        if meta:
            reports.append(meta)
            if args.verbose:
                print(f"  [OK] {f.name}  [{meta['type']}]  {meta['date']}  \"{meta['title']}\"")

    # Sort newest first
    reports.sort(key=lambda r: r["date"], reverse=True)

    print(f"\nFound {len(reports)} valid report(s).")
    if not reports:
        sys.exit(0)

    # Update index.html
    changed = update_index(reports, dry_run=args.dry_run)

    if changed and not args.dry_run:
        latest = reports[0]["date"]
        print(f"index.html updated — {len(reports)} report(s), latest: {latest}")
    elif not args.dry_run:
        pass  # "already up to date" printed inside update_index


if __name__ == "__main__":
    main()
