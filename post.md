# RepoTruth — Catch documentation that lies (Build with Beam)

**Affiliation:** Green Robin Labs  
**Artifact type:** Space demo + dataset + open-source tool  
**Model:** `Beam-1.0-501B-A23B` (Reflection API / HF Inference Providers)

## Links

| | |
|--|--|
| **Live Space** (static interactive fixtures; Gradio needs HF PRO) | https://huggingface.co/spaces/mr-dee/repotruth |
| **GitHub** | https://github.com/dl88jing/repotruth |
| **Landing** | https://repotruth.vercel.app |
| **Findings dataset** | https://huggingface.co/datasets/mr-dee/repotruth-findings |
| **Demo video** | https://github.com/dl88jing/repotruth/blob/master/video/renders/repotruth-demo.mp4 |
| **Deck** | https://github.com/dl88jing/repotruth/blob/master/deck/RepoTruth-Build-with-Beam.pptx |

## One-liner

RepoTruth packs an entire repository into **one Beam call**, finds every place the docs contradict the code, and shows a **token thrift meter** so Beam’s token-efficient reasoning is visible per audit. Public demos use reproducible fixtures; live Beam when a Reflection/HF key is set (provider failures fall back to fixtures with a clear banner).

## Why Beam (not a generic chat wrapper)

| Beam strength | How RepoTruth uses it |
|---|---|
| **1M context** | README + `docs/` + `src/` packed into a single audit prompt |
| **Agentic coding / SWE** | Judges *functional* lies (flags, defaults, exit codes, control flow) with file+line proof |
| **Token-efficient reasoning** | Thrift meter + `reasoning_effort` control (illustrative 3× baseline; live usage when keyed) |

## 90-second demo script

1. Open the Space → load **tinyclick** fixture (docs claim `--count`; code implements `--times`).
2. Hit **Audit** — whole-repo pack lands in one call (fixture-seeded on the Static Space).
3. Autopsy cards appear: HIGH findings with cited paths.
4. Watch the thrift meter (fixture-seeded on Space; live when CLI has a key).
5. Export findings → seeded in `mr-dee/repotruth-findings`.

## Rubric fit

- **Creativity** — visual autopsy of docs that lie, not another chat UI
- **Technical execution** — packer, structured JSON schema, dual backends (Reflection / HF / mock), reproducible fixtures, tests + CI
- **Usefulness** — maintainers and coding agents burn hours on stale docs every week
- **Use of Beam** — 1M context + SWE strength + thrift meter are first-class product surface

## Repro

```bash
git clone https://github.com/dl88jing/repotruth
cd repotruth
./demo.sh
# Live:
# export REFLECTION_API_KEY=...   # https://platform.reflection.ai
# REPOTRUTH_BACKEND=reflection ./demo.sh
```

Built with ❤️ for the Hugging Face × Reflection **Build with Beam** challenge.
