"""Pack a repository (or fixture) into a single prompt budget for Beam."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

SKIP_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".next", ".turbo", "target", "vendor", ".mypy_cache",
}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
    ".tar", ".gz", ".whl", ".so", ".dylib", ".bin", ".pyc", ".lock",
}
DOC_NAMES = {"readme", "changelog", "contributing", "license", "authors"}
DOC_SUFFIXES = {".md", ".rst", ".txt", ".adoc"}
CODE_SUFFIXES = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".rb", ".php", ".swift", ".scala",
    ".toml", ".yaml", ".yml", ".json", ".ini", ".cfg", ".sh",
}


@dataclass
class PackedFile:
    path: str
    kind: str  # doc | code | other
    text: str
    chars: int


@dataclass
class PackedRepo:
    name: str
    files: list[PackedFile]
    total_chars: int
    approx_tokens: int

    def as_prompt_blob(self, max_chars: int = 350_000) -> str:
        parts: list[str] = []
        used = 0
        for f in self.files:
            header = f"\n\n===== FILE: {f.path} ({f.kind}) =====\n"
            chunk = header + f.text
            if used + len(chunk) > max_chars:
                remain = max_chars - used - len(header) - 64
                if remain > 200:
                    parts.append(header + f.text[:remain] + "\n… [truncated]")
                break
            parts.append(chunk)
            used += len(chunk)
        return "".join(parts)


def _kind(path: Path) -> str:
    stem = path.stem.lower()
    if stem in DOC_NAMES or path.suffix.lower() in DOC_SUFFIXES:
        return "doc"
    if path.suffix.lower() in CODE_SUFFIXES:
        return "code"
    return "other"


def pack_directory(root: str | Path, name: str | None = None, max_file_chars: int = 80_000) -> PackedRepo:
    root = Path(root).resolve()
    files: list[PackedFile] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() in SKIP_SUFFIXES:
                continue
            try:
                if p.stat().st_size > 400_000:
                    continue
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if len(text) > max_file_chars:
                text = text[:max_file_chars] + "\n… [truncated]"
            rel = str(p.relative_to(root)).replace("\\", "/")
            files.append(PackedFile(path=rel, kind=_kind(p), text=text, chars=len(text)))

    rank = {"doc": 0, "code": 1, "other": 2}
    files.sort(key=lambda f: (rank.get(f.kind, 9), f.path))
    total = sum(f.chars for f in files)
    return PackedRepo(
        name=name or root.name,
        files=files,
        total_chars=total,
        approx_tokens=max(1, total // 4),
    )


SYSTEM_PROMPT = """You are RepoTruth, an expert code+docs auditor.
Your job: find places where DOCUMENTATION CONTRADICTS the CODE in the provided repository dump.

Rules:
- Only report contradictions you can cite from both a doc file and a code file.
- Do NOT invent APIs. Do NOT report style nits, typos, or missing docs unless the docs make a false claim.
- Prefer high-severity functional lies (wrong flags, wrong defaults, wrong exit codes, wrong control flow).
- Return STRICT JSON only, matching this schema:
{
  "repo": string,
  "summary": string,
  "findings": [
    {
      "id": string,
      "severity": "critical" | "high" | "medium" | "low",
      "title": string,
      "doc_refs": [string],
      "code_refs": [string],
      "evidence": string,
      "suggested_fix": string,
      "confidence": number
    }
  ]
}
If nothing is wrong, return findings: [].
"""


def build_messages(packed: PackedRepo, max_chars: int = 350_000) -> list[dict]:
    blob = packed.as_prompt_blob(max_chars=max_chars)
    user = (
        f"Repository name: {packed.name}\n"
        f"Files packed: {len(packed.files)} (~{packed.approx_tokens} tokens est.)\n"
        f"Audit the dump below for documentation that lies about the code.\n"
        f"{blob}\n\n"
        "Respond with JSON only."
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
