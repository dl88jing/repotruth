---
license: apache-2.0
task_categories:
  - text-generation
tags:
  - beam
  - reflection
  - documentation
  - code-quality
  - audit
  - long-context
pretty_name: RepoTruth Findings
size_categories:
  - n<1K
---

# RepoTruth Findings

Structured **documentation-vs-code contradiction** findings from
[RepoTruth](https://github.com/dl88jing/repotruth) using Reflection **`Beam-1.0-501B-A23B`**
(OpenAI-compatible API at `https://api.reflection.ai/openai/v1`).

## What each row is

One audited repository (fixture or public GitHub clone), with:

- `summary`, `findings_json` (verified true positives for real repos)
- **Measured** `prompt_tokens`, `reasoning_tokens`, `completion_tokens`, `total_tokens`, `latency_s`
- `reasoning_effort`, `model`, `source`, optional `github` + `commit`
- `reasoning_tokens_per_finding` when `n_findings > 0`

## Honest thrift measurement (tinyclick effort sweep)

Same 3 planted findings recovered at every effort:

| effort | reasoning_tokens | completion_tokens | latency_s |
|--------|-----------------:|------------------:|----------:|
| low    | 246 | 703 | 4.29 |
| medium | 572 | 1157 | 7.22 |
| high   | 580 | 1079 | 7.09 |

**Claim we make:** on this fixture, `reasoning_effort=low` used **57% fewer** reasoning tokens than `medium` for the same verified findings. We do **not** claim a cross-model ~3× figure from this dataset alone.

## Real OSS (verified TPs only)

| repo | verified findings | prompt | reasoning | latency_s |
|------|------------------:|-------:|----------:|----------:|
| encode/httpcore | 5 | 56,742 | 4,292 | 36.53 |
| pallets/itsdangerous | 1 | 40,291 | 2,859 | 20.99 |
| psf/requests | 1 | 62,572 | 2,967 | 24.46 |
| Kludex/starlette | 1 | 76,850 | 2,252 | 21.37 |
| pallets/click | 0 | 70,244 | 2,943 | 25.35 |

Affiliation: **Green Robin Labs**. Entry for Hugging Face × Reflection **Build with Beam**.
