"""Beam client with Reflection / HF Inference Providers / mock backends."""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .packer import PackedRepo, build_messages

FIXTURES_EXPECTED = Path(__file__).resolve().parents[2] / "fixtures" / "expected"


@dataclass
class BeamResult:
    backend: str
    model: str
    content: str
    parsed: dict[str, Any]
    usage: dict[str, int]
    latency_s: float
    reasoning_effort: str
    raw: dict[str, Any] | None = None


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            raise
        return json.loads(m.group(0))


def _usage_from_response(data: dict) -> dict[str, int]:
    u = data.get("usage") or {}
    details = u.get("completion_tokens_details") or {}
    return {
        "prompt_tokens": int(u.get("prompt_tokens") or 0),
        "completion_tokens": int(u.get("completion_tokens") or 0),
        "reasoning_tokens": int(details.get("reasoning_tokens") or u.get("reasoning_tokens") or 0),
        "total_tokens": int(u.get("total_tokens") or 0),
    }


def resolve_backend() -> str:
    mode = (os.environ.get("REPOTRUTH_BACKEND") or "auto").lower()
    if mode in {"mock", "reflection", "hf"}:
        return mode
    if os.environ.get("REFLECTION_API_KEY"):
        return "reflection"
    if os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN"):
        return "hf"
    return "mock"


def audit_repo(
    packed: PackedRepo,
    *,
    reasoning_effort: str = "medium",
    max_tokens: int = 4096,
    backend: str | None = None,
) -> BeamResult:
    backend = backend or resolve_backend()
    messages = build_messages(packed)

    if backend == "mock":
        return _mock_audit(packed, reasoning_effort)

    if backend == "reflection":
        return _openai_compat_audit(
            packed,
            messages,
            base_url="https://api.reflection.ai/openai/v1",
            api_key=os.environ["REFLECTION_API_KEY"],
            model=os.environ.get("BEAM_MODEL", "Beam-1.0-501B-A23B"),
            reasoning_effort=reasoning_effort,
            max_tokens=max_tokens,
            backend_name="reflection",
        )

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if not token:
        return _mock_audit(packed, reasoning_effort)
    model = os.environ.get(
        "BEAM_HF_MODEL",
        "reflection/Beam-1.0-501B-A23B:baseten",
    )
    return _openai_compat_audit(
        packed,
        messages,
        base_url="https://router.huggingface.co/v1",
        api_key=token,
        model=model,
        reasoning_effort=reasoning_effort,
        max_tokens=max_tokens,
        backend_name="hf",
    )


def _mock_audit(packed: PackedRepo, reasoning_effort: str) -> BeamResult:
    path = FIXTURES_EXPECTED / f"{packed.name}.json"
    if path.exists():
        parsed = json.loads(path.read_text())
    else:
        parsed = {
            "repo": packed.name,
            "summary": "Mock mode: no fixture findings for this repo. Set REFLECTION_API_KEY or HF_TOKEN with Inference Providers permission.",
            "findings": [],
        }
    usage = parsed.get("usage") or {
        "prompt_tokens": packed.approx_tokens,
        "completion_tokens": 400,
        "reasoning_tokens": 280,
        "total_tokens": packed.approx_tokens + 400,
    }
    return BeamResult(
        backend="mock",
        model="mock/Beam-fixture",
        content=json.dumps(parsed, indent=2),
        parsed=parsed,
        usage=usage,
        latency_s=0.35,
        reasoning_effort=reasoning_effort,
        raw=None,
    )


def _openai_compat_audit(
    packed: PackedRepo,
    messages: list[dict],
    *,
    base_url: str,
    api_key: str,
    model: str,
    reasoning_effort: str,
    max_tokens: int,
    backend_name: str,
) -> BeamResult:
    import urllib.error
    import urllib.request

    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    if backend_name == "reflection":
        body["reasoning_effort"] = reasoning_effort

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{backend_name} API error {e.code}: {err[:500]}") from e
    latency = time.time() - t0
    msg = (raw.get("choices") or [{}])[0].get("message") or {}
    content = msg.get("content") or ""
    if not content and msg.get("reasoning_content"):
        content = msg["reasoning_content"]
    parsed = _extract_json(content)
    parsed.setdefault("repo", packed.name)
    return BeamResult(
        backend=backend_name,
        model=model,
        content=content,
        parsed=parsed,
        usage=_usage_from_response(raw),
        latency_s=latency,
        reasoning_effort=reasoning_effort,
        raw=raw,
    )
