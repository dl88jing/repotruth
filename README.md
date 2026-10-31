<p align="center">
  <img src="assets/cover.png" alt="RepoTruth cover" width="100%"/>
</p>

# RepoTruth

**Catch documentation that lies.**

RepoTruth packs an entire repository into **one [Beam](https://huggingface.co/reflection/Beam-1.0-501B-A23B) call**, finds places where the docs contradict the code, and shows a **token thrift meter** so Beam’s efficiency claim is visible per audit.

Built by **Green Robin Labs** for the Hugging Face × Reflection [Build with Beam](https://huggingface.co/reflection/Beam-1.0-501B-A23B/discussions/5) challenge ($20K).

[![CI](https://github.com/dl88jing/repotruth/actions/workflows/ci.yml/badge.svg)](https://github.com/dl88jing/repotruth/actions/workflows/ci.yml)

| Artifact | Link | Status (checked Oct 31, 2026 PT) |
|----------|------|----------------------------------|
| Live Space (static interactive fixtures) | https://huggingface.co/spaces/mr-dee/repotruth | HTTP 200, static SDK |
| Landing | https://repotruth.vercel.app | HTTP 200 |
| Findings dataset | https://huggingface.co/datasets/mr-dee/repotruth-findings | HTTP 200 |
| Demo video | [repotruth-demo.mp4](video/renders/repotruth-demo.mp4) | In-repo |
| Deck | [RepoTruth-Build-with-Beam.pptx](deck/RepoTruth-Build-with-Beam.pptx) | In-repo |
| Model | `Beam-1.0-501B-A23B` via Reflection API or HF Inference Providers | Live calls need `REFLECTION_API_KEY` or `HF_TOKEN` |

> **Honest status (checked Oct 31, 2026 ~4:05 PM PT):**
> - **Live Beam works** via Reflection API. Measured on `tinyclick` (`reasoning_effort=medium`): prompt **813**, reasoning **370**, completion **947**, total **1760** tokens → **3 findings**. Details: [`docs/live-eval.md`](docs/live-eval.md).
> - **Landing** (`https://repotruth.vercel.app`) exposes `/api/health` + `/api/audit` with the Vercel `REFLECTION_API_KEY` secret; provider failures fall back to fixtures with a visible banner.
> - **HF Space** remains a free **Static** interactive fixture demo (Gradio free CPU returns HTTP 402).
> - Fixture thrift numbers in the Static Space are seeded, not live measurements.

## For judges

Verifiable commands (PT times):

```bash
# 1) Offline fixture demo + tests (no key)
git clone https://github.com/dl88jing/repotruth && cd repotruth
./demo.sh
python3 -m pytest -q   # after: pip install -r requirements-dev.txt

# 2) Live health + audit on the deployed app (uses Vercel Reflection secret)
curl -s https://repotruth.vercel.app/api/health | jq .
curl -s -X POST https://repotruth.vercel.app/api/audit \
  -H 'content-type: application/json' \
  -d '{"fixture":"tinyclick","effort":"medium"}' | jq '{live, usage:.result.usage, n_findings:(.result.parsed.findings|length), summary:.result.parsed.summary}'

# 3) CLI live (your own key)
export REFLECTION_API_KEY=...   # https://platform.reflection.ai
REPOTRUTH_BACKEND=reflection ./demo.sh
```

Measured live CLI run (Oct 31, 2026 ~4:05 PM PT): tinyclick → prompt 813 / reasoning 370 / completion 947 / total 1760 · 3 findings. See [`docs/live-eval.md`](docs/live-eval.md).

Links: [Space](https://huggingface.co/spaces/mr-dee/repotruth) · [Landing](https://repotruth.vercel.app) · [Dataset](https://huggingface.co/datasets/mr-dee/repotruth-findings) · [Submission](https://huggingface.co/reflection/Beam-1.0-501B-A23B/discussions/5)

## Why this shows off Beam

| Beam strength | How RepoTruth uses it |
|---------------|------------------------|
| **1M context** | Packs README + docs + source into a single audit prompt |
| **Agentic coding / SWE** | Judges functional lies (flags, defaults, exit codes, control flow) with file citations |
| **Token-efficient reasoning** | Thrift meter + `reasoning_effort` control; Reflection’s public ~3× claim is shown as an illustrative baseline, live usage when a key is present |

## Architecture

```
┌──────────────┐     pack_directory      ┌─────────────────┐
│ repo / zip / │ ───────────────────────▶│ PackedRepo      │
│ fixture      │   docs first, then code │ (token estimate)│
└──────────────┘                         └────────┬────────┘
                                                  │ build_messages
                                                  ▼
                                         ┌─────────────────┐
                                         │ Beam chat       │
                                         │ completions     │
                                         │ (reflection|hf) │
                                         └────────┬────────┘
                                                  │ JSON findings
                     on error ──▶ fixture mock    ▼
                                         ┌─────────────────┐
                                         │ Autopsy cards + │
                                         │ thrift meter    │
                                         └─────────────────┘
```

| Module | Role |
|--------|------|
| `app/repotruth/packer.py` | Walk repo, rank docs before code, budget into one prompt |
| `app/repotruth/client.py` | Reflection / HF / mock backends; labeled provider fallback |
| `app/repotruth/render.py` | Findings + thrift markdown |
| `scripts/repotruth_cli.py` | One-command CLI |
| `space/` | Gradio app (needs HF PRO or local host; free Static Space uses `space-static/`) |
| `fixtures/` | Intentionally lying mini-repos + expected JSON |
| `dataset/` | Seed JSONL published as `mr-dee/repotruth-findings` |

## Quick start

```bash
# Fixture demo (no API key) — preferred for judges
./demo.sh

# Reflection API
export REFLECTION_API_KEY=...
REPOTRUTH_BACKEND=reflection python3 scripts/repotruth_cli.py fixtures/tinyclick

# HF Inference Providers (token needs Inference Providers permission)
export HF_TOKEN=...
REPOTRUTH_BACKEND=hf python3 scripts/repotruth_cli.py fixtures/tinyclick
```

Gradio locally:

```bash
cd space && pip install -r requirements.txt && python app.py
```

## Fixtures

Intentionally lying mini-repos for demos and tests:

| Fixture | Planted lies |
|---------|----------------|
| `tinyclick` | `--count` vs `--times`; claimed glob/`--recursive`; exit `0` vs `2` |
| `tinystar` | async route claim; middleware order; `:id` path syntax |
| `tinyhttp` | timeout/retries defaults; `.json()` always-available claim |

## Rubric fit (Build with Beam — equal 25% each)

- **Creativity** — visual autopsy of docs that lie, not a chat wrapper
- **Technical execution** — packer, structured JSON schema, dual backends, fixture mode, tests + CI, labeled fallback
- **Usefulness** — maintainers and coding agents burn hours on stale docs every week
- **Use of Beam** — 1M context + SWE strength + thrift meter are first-class product surface

## Limitations

- Public Space is **static** (HF free Gradio Spaces return HTTP 402 without PRO). Interactive fixture demo only; live Beam is CLI/Gradio with a key.
- Fixture thrift token counts are **seeded for UI demos**, not measured Beam runs.
- Mock findings are hand-authored expected JSON so demos stay reproducible offline.
- Provider fallback returns fixtures with a visible banner — never silent.

## License

Apache-2.0. Affiliation in public copy: **Green Robin Labs**. Hackathon identity: GitHub `dl88jing` / HF `mr-dee`.
