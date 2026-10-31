# Live Beam eval (measured)

Checked **2026-10-31 ~4:05 PM PT** against Reflection API (`Beam-1.0-501B-A23B`, `reasoning_effort=medium`) on fixture `tinyclick`.

| Metric | Value |
|--------|------:|
| Prompt tokens | 813 |
| Reasoning tokens | 370 |
| Completion tokens | 947 |
| Total tokens | 1760 |
| Findings | 3 |

Summary from Beam: Documentation advertises flags and behaviors that the CLI does not implement: --count is actually --times, --recursive/glob support is absent, and missing files exit 2 instead of the documented 0.

Findings:
- **HIGH** Documented --count flag does not exist; implementation uses --times
- **HIGH** Documented --recursive flag and glob support are not implemented
- **HIGH** Missing file exits with code 2, but documentation says code 0

Repro:

```bash
export REFLECTION_API_KEY=...
REPOTRUTH_BACKEND=reflection ./demo.sh
# or: curl -s 'https://repotruth.vercel.app/api/health'
#     curl -s -X POST https://repotruth.vercel.app/api/audit -H 'content-type: application/json' -d '{"fixture":"tinyclick"}'
```

Public Space remains fixture-seeded (Static SDK). Landing `/api/audit` is live when the Vercel secret is present, with labeled fixture fallback on provider errors.
