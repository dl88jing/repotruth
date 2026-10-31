# Live Beam evaluation log

Checked **Oct 31, 2026 PT**. Model: `Beam-1.0-501B-A23B` via `https://api.reflection.ai/openai/v1`.

## tinyclick effort sweep

| effort | prompt | reasoning | completion | total | latency_s | findings |
|--------|-------:|----------:|-----------:|------:|----------:|---------:|
| low | 813 | 246 | 703 | ~1516 | 4.29 | 3 |
| medium | 813 | 572 | 1157 | 1970 | 7.22 | 3 |
| high | 813 | 580 | 1079 | ~1892 | 7.09 | 3 |

Δ reasoning low vs medium: **−57%**.

## Real repos (verified TPs kept)

See `docs/audits/real_*.json` and dataset `mr-dee/repotruth-findings`.

## Live auditor smoke test

```
GET  https://repotruth.vercel.app/api/health → reflection_key_present:true, github_audit:true
POST /api/audit {fixture:tinyclick,effort:low} → live:true, 3 findings
POST /api/audit {github:https://github.com/pallets/itsdangerous,effort:low}
  → live:true, mode:github, prompt≈36k, reasoning≈975, ~10.7s, findings≥1
```
