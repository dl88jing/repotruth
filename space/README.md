---
title: RepoTruth
emoji: 🔎
colorFrom: indigo
colorTo: pink
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
license: apache-2.0
tags:
  - agent-demo-track
  - reflection
  - beam
  - code
  - docs
  - mcp
short_description: Catch documentation that lies — powered by Beam
---

# RepoTruth

**Catch documentation that lies.** Pack a whole mini-repo into one Beam call (1M context),
surface severity-ranked doc/code contradictions, and watch a live token thrift meter.

Built by **Green Robin Labs** for the [Build with Beam](https://huggingface.co/reflection/Beam-1.0-501B-A23B/discussions/5) challenge.

## Backends

Set one of these Space secrets:

- `REFLECTION_API_KEY` — Reflection platform (`https://api.reflection.ai/openai/v1`, model `Beam-1.0-501B-A23B`)
- `HF_TOKEN` — Hugging Face token with Inference Providers permission (`reflection/Beam-1.0-501B-A23B:baseten`)

Without a key, the Space runs **fixture mock mode** so the UI stays demoable.

## Fixtures

- `tinyclick` — wrong CLI flags / exit codes
- `tinystar` — middleware order + path syntax lies
- `tinyhttp` — wrong defaults + `.json()` claims
