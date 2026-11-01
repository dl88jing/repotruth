## RepoTruth — LIVE Beam update (follow-up)

**Green Robin Labs** · Build with Beam · model `Beam-1.0-501B-A23B`

We upgraded RepoTruth from fixture demos to **live whole-repo Beam audits**, with verified findings, a measured thrift meter, and a judge-ready live auditor.

### Try it (judges)
- **Live auditor:** https://repotruth.vercel.app/#auditor — paste a public GitHub URL (server-side Reflection key; ~5 audits/IP/hour, ~150/day; zip ≤2.5MB / ≤120 files / ≤280k packed chars)
- **Space (measured results):** https://huggingface.co/spaces/mr-dee/repotruth
- **Dataset:** https://huggingface.co/datasets/mr-dee/repotruth-findings
- **Source:** https://github.com/dl88jing/repotruth
- **Demo video:** https://youtu.be/oI5lOF2bS2g (screen recording of the live app) · [MP4](https://github.com/dl88jing/repotruth/releases/download/v0.3.0/repotruth-demo-v2.mp4) · **Deck:** `deck/RepoTruth-Build-with-Beam.pptx`

Quick smoke:
```bash
curl -s https://repotruth.vercel.app/api/health | jq .
curl -s -X POST https://repotruth.vercel.app/api/audit \
  -H 'content-type: application/json' \
  -d '{"github":"https://github.com/pallets/itsdangerous","effort":"low"}' \
  | jq '{live,usage:.result.usage,n:(.result.parsed.findings|length),summary:.result.parsed.summary}'
```

### Measured thrift (tinyclick effort sweep — same 3 findings)
| effort | reasoning_tokens | completion_tokens | latency_s |
|--------|-----------------:|------------------:|----------:|
| low | 246 | 703 | 4.29 |
| medium | 572 | 1157 | 7.22 |
| high | 580 | 1079 | 7.09 |

**Claim we make:** `reasoning_effort=low` used **57% fewer** reasoning tokens than `medium` for identical findings. We are **not** claiming an unmeasured cross-model multiplier.

### Verified true positives on real OSS (kept only after re-reading cited source)
| repo | verified findings | prompt | reasoning | latency_s |
|------|------------------:|-------:|----------:|----------:|
| encode/httpcore | 5 | 56,742 | 4,292 | 36.53 |
| pallets/itsdangerous | 1 | 40,291 | 2,859 | 20.99 |
| psf/requests | 1 | 62,572 | 2,967 | 24.46 |
| Kludex/starlette | 1 | 76,850 | 2,252 | 21.37 |
| pallets/click | 0 (clean) | 70,244 | 2,943 | 25.35 |

httpcore highlights: docs call `proxy.request(...)` but `Proxy` has no `request`; `Request(...)` Host header is *not* auto-added; TOC lists `AsyncioBackend` which does not exist.

### Why Beam
- **1M context** — one shot over README + docs + source (56k–77k prompt tokens measured)
- **Agentic / SWE** — functional lies with file+line evidence we verified
- **Token efficiency** — controllable `reasoning_effort`; numbers above are from live Reflection API usage (`reasoning_tokens` via `completion_tokens_details`)

### Notes
- API model name must be exactly `Beam-1.0-501B-A23B` (the `reflection/` prefix returns `model_not_found` on `api.reflection.ai`)
- HF Gradio free CPU returns HTTP 402, so the Space is Static and points judges to the Vercel live auditor
- Affiliation: **Green Robin Labs**

Happy to walk judges through a live URL audit on the call.
