from __future__ import annotations

import argparse
from pathlib import Path

from .parser import parse_line
from .analyze import analyze
from .report import write_json, write_markdown
from .report import write_json, write_markdown, write_html



def _iter_log_files(path: Path, glob_pattern: str) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(path.rglob(glob_pattern))
    raise FileNotFoundError(f"Path not found: {path}")


def run(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="logan", description="Log analyzer + report generator")
    p.add_argument("path", help="Log file or folder containing logs")
    p.add_argument("--glob", default="*.log", help="When path is a folder, search pattern (default: *.log)")
    p.add_argument("--out", default="out_report", help="Output folder for report.json/report.md")
    p.add_argument("--top", type=int, default=10, help="Top N items to show (default: 10)")
    args = p.parse_args(argv)

    base = Path(args.path)
    out_dir = Path(args.out)

    files = _iter_log_files(base, args.glob)
    if not files:
        print("No log files found.")
        return 1

    entries = []
    for f in files:
        try:
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines(True):
                entries.append(parse_line(line))
        except Exception as e:
            print(f"Failed reading {f}: {e}")

    result = analyze(entries, top_n=args.top)
    jpath = write_json(out_dir, result)
    mpath = write_markdown(out_dir, result)

    print(f"Analyzed {len(files)} file(s), {result.total_lines} line(s).")
    hpath = write_html(out_dir, result)

    print(f"Wrote: {jpath}")
    print(f"Wrote: {mpath}")
    print(f"Wrote: {hpath}")

    return 0
