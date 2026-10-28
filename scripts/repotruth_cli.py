#!/usr/bin/env python3
"""RepoTruth CLI."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from repotruth.client import audit_repo
from repotruth.packer import pack_directory
from repotruth.render import findings_markdown, pack_summary, thrift_markdown


def main() -> int:
    p = argparse.ArgumentParser(description="RepoTruth — docs vs code auditor powered by Beam")
    p.add_argument("path", type=Path, help="Path to a repository or fixture")
    p.add_argument("--name", default=None)
    p.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    p.add_argument("--backend", default=None, choices=["auto", "mock", "reflection", "hf"])
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    packed = pack_directory(args.path, name=args.name or args.path.name)
    backend = None if args.backend in (None, "auto") else args.backend
    result = audit_repo(packed, reasoning_effort=args.effort, backend=backend)

    if args.json:
        print(json.dumps({"pack": pack_summary(packed), "result": result.parsed, "usage": result.usage}, indent=2))
    else:
        print(pack_summary(packed))
        print()
        print(findings_markdown(result.parsed))
        print(thrift_markdown(result, packed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
