from __future__ import annotations

import json
from pathlib import Path

from repotruth.citations import check_findings, check_ref, summarize

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"
LIVE = ROOT / "live_results"


def test_ref_forms_parse():
    texts = {"src/cli.py": "a\nb\nc\n", "README.md": "x"}
    assert check_ref("src/cli.py", texts).exists
    assert check_ref("src/cli.py:2", texts).lines_ok is True
    assert check_ref("src/cli.py:2-3 `b`", texts).lines_ok is True
    assert check_ref("README.md: usage `x`", texts).exists
    assert check_ref("src/cli.py:99", texts).lines_ok is False


def test_fabricated_refs_are_flagged():
    bad = [{"id": "fake", "doc_refs": ["docs/nope.md"], "code_refs": ["src/cli.py:999"],
            "evidence": "Code calls `totally_made_up()`."}]
    (c,) = check_findings(bad, FIX / "tinyclick")
    assert not c.refs_ok
    assert c.spans_missing == ["totally_made_up()"]


def test_saved_live_fixture_findings_cite_real_files():
    for f in sorted(LIVE.glob("tiny*_*.json")):
        d = json.loads(f.read_text())
        s = summarize(check_findings(d["findings"], FIX / d["repo"]))
        assert s["refs_exist"] == s["refs"], f.name
        assert s["line_refs_in_range"] == s["line_refs"], f.name
