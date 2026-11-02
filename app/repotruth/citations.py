"""Deterministic citation checker for RepoTruth findings.

Beam proposes findings; this module checks them against the repository on disk
without any model in the loop:

* every ``doc_refs`` / ``code_refs`` entry must name a file that exists
  (optional ``:LINE`` or ``:START-END`` suffix must be inside the file), and
* every backtick-quoted span in ``evidence`` (and in ref annotations) is looked up verbatim, first in the
  cited files, then anywhere in the repo.

Spans that are paraphrased or elided (``...``) count as *not found verbatim*;
that is a conservative flag, not proof of a hallucination. It does not decide whether a contradiction is *true* — that still needs a human
re-read (see ``verified`` in ``docs/audits/``). It only flags citations that
cannot be real, so they are never shown as evidence.
"""
from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

# "path", "path:12", "path:12-20", optionally followed by an annotation such as
# ": usage `foo --bar`" or " `quoted code`" (Beam emits all of these).
_REF_RE = re.compile(r"^(?P<path>[^\s:`'\"]+)(?::(?P<start>\d+)(?:-(?P<end>\d+))?)?(?P<rest>.*)$", re.S)
_TICK_RE = re.compile(r"`([^`\n]{2,120})`")
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}


@dataclass
class RefCheck:
    ref: str
    path: str
    exists: bool
    lines_ok: bool | None = None  # None when the ref has no line suffix


@dataclass
class FindingCheck:
    id: str
    refs: list[RefCheck] = field(default_factory=list)
    spans_total: int = 0
    spans_in_cited: int = 0
    spans_in_repo: int = 0
    spans_missing: list[str] = field(default_factory=list)

    @property
    def refs_ok(self) -> bool:
        return bool(self.refs) and all(r.exists and r.lines_ok is not False for r in self.refs)


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _repo_texts(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                if p.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue
            out[str(p.relative_to(root)).replace("\\", "/")] = _read(p)
    return out


def check_ref(ref: str, texts: dict[str, str]) -> RefCheck:
    raw = ref.strip()
    if raw.startswith("./"):
        raw = raw[2:]
    m = _REF_RE.match(raw)
    path = m.group("path") if m else raw
    exists = path in texts
    lines_ok: bool | None = None
    if m and m.group("start"):
        start = int(m.group("start"))
        end = int(m.group("end") or start)
        n = texts[path].count("\n") + 1 if exists else 0
        lines_ok = exists and 1 <= start <= end <= n
    return RefCheck(ref=ref, path=path, exists=exists, lines_ok=lines_ok)


def check_findings(findings: list[dict], root: str | Path) -> list[FindingCheck]:
    texts = _repo_texts(Path(root))
    corpus = "\n".join(texts.values())
    out: list[FindingCheck] = []
    for f in findings:
        fc = FindingCheck(id=str(f.get("id", "")))
        refs = list(f.get("doc_refs") or []) + list(f.get("code_refs") or [])
        fc.refs = [check_ref(r, texts) for r in refs]
        cited = "\n".join(texts.get(r.path, "") for r in fc.refs if r.exists)
        spans = _TICK_RE.findall(str(f.get("evidence", "")))
        for r in refs:
            m = _REF_RE.match(str(r).strip())
            if m:
                spans += _TICK_RE.findall(m.group("rest") or "")
        for span in spans:
            fc.spans_total += 1
            if span in cited:
                fc.spans_in_cited += 1
            elif span in corpus:
                fc.spans_in_repo += 1
            else:
                fc.spans_missing.append(span)
        out.append(fc)
    return out


def summarize(checks: list[FindingCheck]) -> dict:
    refs = [r for c in checks for r in c.refs]
    return {
        "findings": len(checks),
        "findings_all_refs_ok": sum(c.refs_ok for c in checks),
        "refs": len(refs),
        "refs_exist": sum(r.exists for r in refs),
        "line_refs": sum(r.lines_ok is not None for r in refs),
        "line_refs_in_range": sum(bool(r.lines_ok) for r in refs),
        "evidence_spans": sum(c.spans_total for c in checks),
        "spans_in_cited_files": sum(c.spans_in_cited for c in checks),
        "spans_elsewhere_in_repo": sum(c.spans_in_repo for c in checks),
        "spans_not_found": sum(len(c.spans_missing) for c in checks),
    }


def to_jsonable(checks: list[FindingCheck]) -> list[dict]:
    rows = []
    for c in checks:
        d = asdict(c)
        d["refs_ok"] = c.refs_ok
        rows.append(d)
    return rows
