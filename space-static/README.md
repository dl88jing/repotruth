---
title: RepoTruth
emoji: 🔎
colorFrom: indigo
colorTo: blue
sdk: static
pinned: false
license: apache-2.0
short_description: Catch documentation that lies — Beam whole-repo auditor
---

# RepoTruth (Static Space)

Interactive **fixture-seeded** docs-vs-code autopsies for the HF × Reflection Build with Beam challenge.

- GitHub: https://github.com/dl88jing/repotruth
- Landing: https://repotruth.vercel.app
- Dataset: https://huggingface.co/datasets/mr-dee/repotruth-findings

This free Static Space does **not** call Beam live (Gradio free CPU returns HTTP 402). For a live Reflection API call:

```bash
git clone https://github.com/dl88jing/repotruth && cd repotruth
export REFLECTION_API_KEY=...   # https://platform.reflection.ai
REPOTRUTH_BACKEND=reflection ./demo.sh
```

Affiliation: Green Robin Labs.
