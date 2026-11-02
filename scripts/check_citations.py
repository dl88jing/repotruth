#!/usr/bin/env python3
"""Re-check every saved live Beam finding against the source it cites.

Fixtures are checked against ``fixtures/<name>``. Real repos are fetched at the
exact commit recorded in ``docs/audits/real_*.json`` (public GitHub tarball,
no token) unless ``--fixtures-only`` is set. Writes
``docs/audits/citation_check.json``. No model calls.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from repotruth.citations import check_findings, summarize, to_jsonable  # noqa: E402

LIVE = ROOT / "docs" / "audits"


def _fetch(github: str, commit: str, dest: Path) -> Path:
    owner_repo = github.rstrip("/").split("github.com/")[1]
    url = f"https://codeload.github.com/{owner_repo}/tar.gz/{commit}"
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        tf.extractall(dest, filter="data")
    return next(p for p in dest.iterdir() if p.is_dir())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures-only", action="store_true")
    ap.add_argument("--out", type=Path, default=LIVE / "citation_check.json")
    args = ap.parse_args()

    rows = []
    files = sorted(LIVE.glob("tiny*_*.json"))
    if not args.fixtures_only:
        files += sorted(LIVE.glob("real_*_medium.json"))
    with tempfile.TemporaryDirectory() as tmp:
        for f in files:
            d = json.loads(f.read_text())
            findings = d.get("findings") or []
            if d.get("source") == "github" or d.get("github"):
                root = _fetch(d["github"], d["commit"], Path(tmp) / f.stem)
                target = f"{d['github']}@{d['commit'][:7]}"
            else:
                root = ROOT / "fixtures" / d["repo"]
                target = f"fixtures/{d['repo']}"
            checks = check_findings(findings, root)
            s = summarize(checks)
            rows.append({"file": f.name, "target": target, "effort": d.get("reasoning_effort"),
                         "summary": s, "findings": to_jsonable(checks)})
            print(f"{f.name:32s} findings={s['findings']} refs_ok={s['findings_all_refs_ok']}/{s['findings']} "
                  f"refs_exist={s['refs_exist']}/{s['refs']} spans cited/repo/missing="
                  f"{s['spans_in_cited_files']}/{s['spans_elsewhere_in_repo']}/{s['spans_not_found']}")
    keys = rows[0]["summary"].keys() if rows else []
    total = {k: sum(r["summary"][k] for r in rows) for k in keys}
    print("TOTAL", json.dumps(total))
    args.out.write_text(json.dumps({"total": total, "runs": rows}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
