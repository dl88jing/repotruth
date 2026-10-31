from __future__ import annotations

from pathlib import Path

from repotruth.packer import pack_directory, build_messages, SYSTEM_PROMPT

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


def test_pack_tinyclick_includes_docs_and_code():
    packed = pack_directory(FIXTURES / "tinyclick")
    assert packed.name == "tinyclick"
    kinds = {f.kind for f in packed.files}
    assert "doc" in kinds
    assert "code" in kinds
    paths = {f.path for f in packed.files}
    assert "README.md" in paths
    assert "src/cli.py" in paths
    assert packed.approx_tokens >= 1
    blob = packed.as_prompt_blob()
    assert "===== FILE:" in blob
    assert "--times" in blob or "times" in blob


def test_build_messages_schema_hint():
    packed = pack_directory(FIXTURES / "tinyclick")
    msgs = build_messages(packed)
    assert msgs[0]["role"] == "system"
    assert "STRICT JSON" in SYSTEM_PROMPT
    assert msgs[1]["role"] == "user"
    assert packed.name in msgs[1]["content"]


def test_pack_all_three_fixtures():
    for name in ("tinyclick", "tinystar", "tinyhttp"):
        packed = pack_directory(FIXTURES / name)
        assert packed.name == name
        assert len(packed.files) >= 2
