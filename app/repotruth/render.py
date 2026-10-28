"""Formatting helpers for Gradio / CLI."""
from __future__ import annotations

from typing import Any

from .client import BeamResult
from .packer import PackedRepo


def findings_markdown(parsed: dict[str, Any]) -> str:
    findings = parsed.get("findings") or []
    if not findings:
        return "_No contradictions found (or mock fixture empty)._"
    lines = [f"### {parsed.get('summary', 'Findings')}", ""]
    for f in findings:
        sev = str(f.get("severity", "?")).upper()
        lines.append(f"#### [{sev}] {f.get('title', 'Untitled')}")
        lines.append(f"- **Confidence:** {f.get('confidence', '—')}")
        docs = ", ".join(f"`{x}`" for x in (f.get("doc_refs") or []))
        code = ", ".join(f"`{x}`" for x in (f.get("code_refs") or []))
        lines.append(f"- **Docs:** {docs or '—'}")
        lines.append(f"- **Code:** {code or '—'}")
        lines.append(f"- **Evidence:** {f.get('evidence', '')}")
        lines.append(f"- **Suggested fix:** {f.get('suggested_fix', '')}")
        lines.append("")
    return "\n".join(lines)


def thrift_markdown(result: BeamResult, packed: PackedRepo) -> str:
    u = result.usage
    reasoning = u.get("reasoning_tokens") or 0
    completion = u.get("completion_tokens") or 0
    prompt = u.get("prompt_tokens") or packed.approx_tokens
    typical = max(reasoning * 3, reasoning + 800) if reasoning else 1200
    saved_pct = 0 if typical == 0 else int(round(100 * (1 - (reasoning / typical))))
    return f"""### Token thrift meter
| | Tokens |
|--|--:|
| Prompt (packed repo) | {prompt:,} |
| Reasoning | {reasoning:,} |
| Completion | {completion:,} |
| Total | {u.get('total_tokens') or (prompt + completion):,} |
| Effort | `{result.reasoning_effort}` |
| Backend | `{result.backend}` · `{result.model}` |
| Latency | {result.latency_s:.2f}s |

Beam's headline claim is **~3× fewer reasoning tokens** for comparable quality.
Against a 3× baseline ({typical:,} reasoning tokens), this run looks **~{saved_pct}% leaner** on reasoning.
"""


def pack_summary(packed: PackedRepo) -> str:
    docs = sum(1 for f in packed.files if f.kind == "doc")
    code = sum(1 for f in packed.files if f.kind == "code")
    return (
        f"**{packed.name}** — {len(packed.files)} files "
        f"({docs} docs / {code} code) · ~{packed.approx_tokens:,} tokens · {packed.total_chars:,} chars"
    )
