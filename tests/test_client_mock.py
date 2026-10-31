from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from repotruth.client import audit_repo, resolve_backend, _extract_json
from repotruth.packer import pack_directory
from repotruth.render import findings_markdown, thrift_markdown, pack_summary

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
EXPECTED = FIXTURES / "expected"


@pytest.fixture(autouse=True)
def _force_mock(monkeypatch):
    monkeypatch.setenv("REPOTRUTH_BACKEND", "mock")
    monkeypatch.delenv("REFLECTION_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("HUGGINGFACE_HUB_TOKEN", raising=False)


def test_resolve_backend_mock():
    assert resolve_backend() == "mock"


def test_mock_audit_tinyclick_matches_fixture():
    packed = pack_directory(FIXTURES / "tinyclick")
    result = audit_repo(packed, backend="mock")
    assert result.backend == "mock"
    assert result.usage_source == "fixture-seeded"
    assert result.is_live is False
    expected = json.loads((EXPECTED / "tinyclick.json").read_text())
    assert result.parsed["repo"] == "tinyclick"
    assert len(result.parsed["findings"]) == len(expected["findings"])
    ids = {f["id"] for f in result.parsed["findings"]}
    assert ids == {f["id"] for f in expected["findings"]}


@pytest.mark.parametrize("name", ["tinyclick", "tinystar", "tinyhttp"])
def test_mock_audit_all_fixtures(name):
    packed = pack_directory(FIXTURES / name)
    result = audit_repo(packed, backend="mock")
    assert result.parsed["repo"] == name
    assert isinstance(result.parsed["findings"], list)
    assert len(result.parsed["findings"]) >= 1
    for finding in result.parsed["findings"]:
        assert finding["severity"] in {"critical", "high", "medium", "low"}
        assert finding.get("doc_refs")
        assert finding.get("code_refs")
        assert 0 <= float(finding.get("confidence", 0)) <= 1


def test_render_mentions_fixture_seeded():
    packed = pack_directory(FIXTURES / "tinyclick")
    result = audit_repo(packed, backend="mock")
    md = thrift_markdown(result, packed)
    assert "fixture-seeded" in md
    assert "Usage source" in md
    assert pack_summary(packed).startswith("**tinyclick**")
    assert "HIGH" in findings_markdown(result.parsed).upper() or "high" in findings_markdown(result.parsed).lower()


def test_extract_json_fenced():
    payload = {"repo": "x", "summary": "s", "findings": []}
    text = "```json\n" + json.dumps(payload) + "\n```"
    assert _extract_json(text)["repo"] == "x"


def test_fallback_when_live_backend_missing_key(monkeypatch):
    monkeypatch.setenv("REPOTRUTH_BACKEND", "reflection")
    monkeypatch.delenv("REFLECTION_API_KEY", raising=False)
    packed = pack_directory(FIXTURES / "tinyclick")
    result = audit_repo(packed, backend="reflection", allow_fallback=True)
    assert result.fallback_from == "reflection"
    assert result.parsed.get("fallback_from") == "reflection"
    assert "FALLBACK" in result.parsed["summary"]
    md = findings_markdown(result.parsed)
    assert "Fallback" in md


def test_no_fallback_raises(monkeypatch):
    monkeypatch.setenv("REPOTRUTH_BACKEND", "reflection")
    monkeypatch.delenv("REFLECTION_API_KEY", raising=False)
    packed = pack_directory(FIXTURES / "tinyclick")
    with pytest.raises(RuntimeError, match="REFLECTION_API_KEY"):
        audit_repo(packed, backend="reflection", allow_fallback=False)
