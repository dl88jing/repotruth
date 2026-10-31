---
title: RepoTruth
emoji: 🔎
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: Catch documentation that lies — Beam whole-repo auditor
---

# RepoTruth (Gradio)

Requires HF PRO (or run locally) — free Gradio Spaces currently return HTTP 402.
The public entry uses the **Static** Space at the same repo with fixture-seeded demos.

```bash
pip install -r requirements.txt
# optional live:
# export REFLECTION_API_KEY=...
python app.py
```
