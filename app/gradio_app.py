"""Gradio Space entrypoint for RepoTruth."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import gradio as gr

ROOT = Path(__file__).resolve().parent
# Support both Space layout (repotruth/ next to app.py) and monorepo layout
for candidate in (ROOT, ROOT.parent / "app", ROOT.parent):
    if (candidate / "repotruth").is_dir():
        sys.path.insert(0, str(candidate))
        break

from repotruth.client import audit_repo, resolve_backend
from repotruth.packer import pack_directory
from repotruth.render import findings_markdown, pack_summary, thrift_markdown

FIXTURES = ROOT / "fixtures"
if not FIXTURES.is_dir():
    FIXTURES = ROOT.parent / "fixtures"

EXAMPLES = ["tinyclick", "tinystar", "tinyhttp"]


def _run(path: Path, name: str, effort: str) -> tuple[str, str, str, str]:
    packed = pack_directory(path, name=name)
    result = audit_repo(packed, reasoning_effort=effort)
    findings = findings_markdown(result.parsed)
    thrift = thrift_markdown(result, packed)
    raw = json.dumps(result.parsed, indent=2)
    return pack_summary(packed), findings, thrift, raw


def run_example(example: str, effort: str):
    path = FIXTURES / example
    if not path.is_dir():
        raise gr.Error(f"Fixture not found: {example}")
    return _run(path, example, effort)


def run_upload(upload, effort: str):
    if upload is None:
        raise gr.Error("Upload a .zip of a small repository (docs + source).")
    tmp = Path(tempfile.mkdtemp(prefix="repotruth-"))
    try:
        zpath = Path(upload)
        with zipfile.ZipFile(zpath, "r") as zf:
            zf.extractall(tmp)
        # If zip has a single top folder, use it
        kids = [p for p in tmp.iterdir() if not p.name.startswith(".")]
        root = kids[0] if len(kids) == 1 and kids[0].is_dir() else tmp
        return _run(root, root.name, effort)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


CSS = """
.gradio-container { max-width: 1100px !important; }
#hero { text-align: center; padding: 0.5rem 0 1rem; }
#hero h1 { font-size: 2rem; margin-bottom: 0.25rem; }
.badge { display:inline-block; padding:2px 10px; border-radius:999px; background:#111; color:#fff; font-size:12px; margin:0 4px; }
"""

backend_note = f"Active backend on boot: `{resolve_backend()}` (set `REFLECTION_API_KEY` or `HF_TOKEN`, or use fixture mock)."

with gr.Blocks(title="RepoTruth — Beam docs vs code auditor", css=CSS, theme=gr.themes.Soft()) as demo:
    gr.HTML(
        f"""
        <div id="hero">
          <div><span class="badge">Build with Beam</span><span class="badge">Green Robin Labs</span><span class="badge">1M context</span></div>
          <h1>RepoTruth</h1>
          <p>Catch documentation that lies — one Beam call over a whole repo.<br/>
          <small>{backend_note}</small></p>
        </div>
        """
    )
    with gr.Row():
        with gr.Column(scale=1):
            example = gr.Dropdown(EXAMPLES, value="tinyclick", label="Curated fixture")
            effort = gr.Dropdown(
                ["low", "medium", "high"],
                value="medium",
                label="Beam reasoning_effort",
            )
            btn_ex = gr.Button("Audit fixture with Beam", variant="primary")
            upload = gr.File(label="Or upload a small repo .zip", file_types=[".zip"])
            btn_up = gr.Button("Audit upload")
            gr.Markdown(
                """
### Why Beam?
Reflection Beam is a **501B MoE / 23B active** model with a **1M-token** context and
**token-efficient reasoning** (~3× fewer reasoning tokens for comparable quality).
RepoTruth is built to show that off: pack an entire mini-repo, find real doc/code contradictions,
and watch the thrift meter.
"""
            )
        with gr.Column(scale=2):
            pack_md = gr.Markdown(label="Pack")
            findings_md = gr.Markdown(label="Findings")
            thrift_md = gr.Markdown(label="Thrift")
            raw_json = gr.Code(label="Raw JSON", language="json")

    btn_ex.click(run_example, [example, effort], [pack_md, findings_md, thrift_md, raw_json])
    btn_up.click(run_upload, [upload, effort], [pack_md, findings_md, thrift_md, raw_json])
    demo.load(run_example, [example, effort], [pack_md, findings_md, thrift_md, raw_json])

if __name__ == "__main__":
    demo.queue().launch()
