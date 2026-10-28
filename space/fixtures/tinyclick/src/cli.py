"""TinyClick CLI — intentional drifts vs README/docs for RepoTruth demos."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def count_lines(path: Path) -> int:
    return sum(1 for _ in path.open("r", encoding="utf-8", errors="replace"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tinyclick")
    sub = parser.add_subparsers(dest="cmd", required=True)
    count_p = sub.add_parser("count", help="Count lines in a file")
    count_p.add_argument("path", type=Path)
    # Docs advertise --count; real flag is --times (drift #1)
    count_p.add_argument("--times", action="store_true", help="Print bare integer only")
    # Docs advertise --recursive / globs; not implemented (drift #2)
    args = parser.parse_args(argv)

    if args.cmd == "count":
        if not args.path.exists():
            print(f"missing: {args.path}", file=sys.stderr)
            # Docs say exit 0; code exits 2 (drift #3)
            return 2
        n = count_lines(args.path)
        if args.times:
            print(n)
        else:
            print(f"{args.path}: {n}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
