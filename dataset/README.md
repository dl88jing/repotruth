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
pretty_name: RepoTruth Findings
size_categories:
  - n<1K
---

# RepoTruth Findings

Structured documentation-vs-code contradiction findings produced (or **fixture-seeded**) by
[RepoTruth](https://github.com/dl88jing/repotruth) targeting Reflection **Beam-1.0-501B-A23B**.

Each row is one audited mini-repo: summary, findings JSON, and token usage for the thrift meter.

## Honesty

- Three rows are **fixture-seeded** expected findings for `tinyclick`, `tinystar`, and `tinyhttp` (schema + offline demos).
- One row is a **live** Reflection Beam run on `tinyclick` (2026-10-31 ~4:05 PM PT): prompt 813 / reasoning 370 / completion 947 / total 1760 tokens, 3 findings (`usage_source=live`).
- Fixture rows are not claimed as measured Beam outputs. Live rows carry `usage_source=live`.

## Schema

```json
{
  "repo": "tinyclick",
  "summary": "...",
  "findings": [
    {
      "id": "TC1",
      "severity": "high",
      "title": "...",
      "doc_refs": ["README.md"],
      "code_refs": ["src/cli.py"],
      "evidence": "...",
      "suggested_fix": "...",
      "confidence": 0.95
    }
  ],
  "usage": {
    "prompt_tokens": 1840,
    "completion_tokens": 620,
    "reasoning_tokens": 410,
    "total_tokens": 2460
  }
}
```

## Links

- Tool: https://github.com/dl88jing/repotruth
- Space: https://huggingface.co/spaces/mr-dee/repotruth
- Challenge: https://huggingface.co/reflection/Beam-1.0-501B-A23B/discussions/5

Affiliation: **Green Robin Labs**. Entry for Build with Beam.
