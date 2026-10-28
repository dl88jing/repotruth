# Build with Beam — Phase 1 Research

Research window: ~1 hour on 2026-10-27 (America/Los_Angeles). Sources: HF model card, discussions/5 + sibling discussions, Official Rules, HF blog `reflection-beam`, Reflection introducing-beam / beam-is-available posts, X post by Ben Burtenshaw, Reflection developer docs.

## 1. Official rules (verified)

| Item | Value |
|------|-------|
| Competition page | https://huggingface.co/reflection/Beam-1.0-501B-A23B/discussions/5 |
| Official Rules | https://reflection.ai/legal/official-rules-build-with-beam |
| Start | 2026-10-15, 6:00 AM PT |
| **Deadline** | **2026-11-02, 11:59 PM PT** (matches brief) |
| Judging done by | On or before 2026-11-17 |
| Winners announced | On or about 2026-12-17 |
| Entry method | Publish a public HF Space / model / dataset that meaningfully uses Beam, document how Beam was used, **and post the link in discussion #5** |
| Sponsor | Reflection AI, Inc. |
| Eligibility | 18+, worldwide (except where prohibited / sanctions). Reflection employees/contractors + household ineligible. Teams OK (one prize per participant). |
| Prizes | **1st $9,000 / 2nd $7,000 / 3rd $4,000 = $20,000**. Winner may take 100% cash **or** 50% cash + 50% HF Hub credits. |
| Criteria (25% each) | Creativity · Technical execution · Usefulness / real-world impact · Innovative or effective use of Beam |
| Tie-break | Innovative/effective use of Beam, then judges' collective judgment |
| Early blog note | Original HF blog (Oct 16) said "$10,000 Hub credits"; discussion + Official Rules supersede → **$20K cash/credits, 3 winners**. |

**Material deltas vs brief:** None on deadline or entry method. Prize split is $9k/$7k/$4k (not equal thirds). Judges are "three judges appointed by Reflection" — not publicly named beyond Ben Burtenshaw as HF launch host.

Launch X post (Ben Burtenshaw, 2026-10-27 PT morning): https://x.com/ben_burtenshaw/status/2115103732396671366 — $20K, deadline Monday Nov 2, $25 Hub credits for first 400 coupon claims.

## 2. Judges & taste

### Known faces
- **Ben Burtenshaw** (`burtenshaw`) — HF Community MLE, authored the Beam Hub blog with Pedro Cuenca, posted the challenge, answers TRL/recipe questions in-thread. Taste signal from his recent work and X:
  - Obsessed with **RL environments, OpenEnv, Open Env Arena, multi-harness RL**, Training Agents livestream series.
  - Ships **smolagents / smol-course**, TRL SFT + GRPO recipes, Hub-native demos.
  - Beam launch demos he highlighted: (1) BeamSpeak native macOS app via Pi agent, (2) multi-agent ProgramBench, (3) agent that fine-tunes a decision model. Pattern: **agents that build useful artifacts**, coding + long-context, not chat wrappers.
  - Praises Reflection engineers contributing to transformers / vLLM / SGLang / TRL / OpenEnv.
- **Reflection-appointed judges (unnamed publicly)** — expect alignment with Reflection's own narrative: coding, agentic tool use, **token-efficient reasoning**, long-horizon tasks, open Hub artifacts.
- Pedro Cuenca co-authored the HF Beam blog (infra/transformers taste).

### What will score
- Hub-native Gradio Space + dataset/benchmark artifacts.
- Clear, honest methodology (competitors already do this well).
- Beam-specific capability on display (1M context, reasoning_effort, tool calling, token thrift) — not a generic LLM wrapper.
- Live, interactive demos over static writeups.
- Usefulness that a HF engineer would actually bookmark.

### What will not
- Thin chat UIs waiting on API keys (see BeamVoice Studio).
- Opaque "RL worlds" with no clear reward / replay (Borderland is ambitious but hard to judge).
- Claims without traces.

## 3. Beam distinctive strengths (model card + blogs)

| Strength | Evidence | Demo implication |
|----------|----------|------------------|
| **Token-efficient reasoning** | ~3× fewer inference-time reasoning tokens vs leading open models for comparable quality; controllable `reasoning_effort` (`low`/`medium`/`high`/`xhigh`/`max`); `preserve_thinking` across turns | Live thrift meter / effort sweep |
| **Agentic coding / SWE** | SWE-bench Verified **81.6%**, Terminal Bench 2.1 **80.1%**, DeepSWE, multilingual SWE | Repo/code tasks, not trivia |
| **Long context (1M)** | Hybrid sliding-window + global layers; KV cache ~6× smaller than all-global; HF vibe-eval included whole-codebase retrieval | **Whole-repo in one shot** |
| **Tool / MCP / browse** | MCP Atlas ~81%, BrowseComp / DeepSearchQA with context management | Multi-step agents |
| **MoE efficiency** | 501B total / **23B active**, Apache 2.0, BF16/FP8/NVFP4 | Cheap-to-serve frontier coding |
| Access | Reflection OpenAI-compatible API `https://api.reflection.ai/openai/v1` model `Beam-1.0-501B-A23B`; **also** HF Inference Providers (`router.huggingface.co`, Baseten/Fireworks/Together) via HF token |

## 4. Existing discussion #5 entries & gaps

| Entry | Type | Strength | Weakness / gap |
|-------|------|----------|----------------|
| **Beam Safety Benchmark** (SushantGautam) | Space + GitHub + multi-model safety audit (NO + BullshitBench) | Rigorous, comparative, live report, Beam wins | Safety niche; not coding/long-context |
| **BeamVoice Studio** (JosephJBassey) | Text→code web studio | Simple | Waitlisted API; thin wrapper |
| **WCGW / kitten-swarm-3** (vwnb) | Systems-safety graph dataset | Unusual domain | Niche ISO/safety eng; hard to demo in 90s |
| **Beam Arcade** (tjonesit) | Gradio game + tool-trap eval dataset | Playful, Beam-built-itself story, tests | Game ≠ utility; hosts disagree on runaway task |
| **African token cost** (Izayas) | Space + dataset (Amharic…Yoruba) | Honest tokenizer cost science | Language equity, not coding |
| **Borderland RL** (FatUnc6969) | Pyodide RL world + Beam traces | Ambitious env | Opaque; admits learning unproven |
| **GovScout** (InTandem-Steve) | Agent + Space mapping US local procurement | Strong usefulness + production claims | Heavy infra story; less "Beam-specific" than generic agent |
| **HinglishBench** (MaybeSomeone19) | Parallel EN/Hinglish GSM8K | Clean small benchmark | Saturated; language angle again |
| **ollymcbride4** | Docs-vs-code drift checker (in progress) | **Exactly the 1M-context gap** | Blocked on HF Space PRO; **not shipped** |
| Discussion #15 (apollo-mg) | 2-bit abstention + effort sweep | Technical | Separate thread, quantization niche |

**Open gaps a winner can own**
1. **Whole-repo long-context usefulness** (olly sketched it; nobody shipped a polished Hub demo).
2. **Interactive token-thrift / intelligence-per-token arena** (Beam's #1 claimed differentiator — zero interactive demos).
3. Clean **OpenEnv-compatible** coding env (Borderland is not that).
4. **smolagents + Beam** showcase (Ben's own stack).

## 5. Chosen concept

### **RepoTruth** — Catch documentation that lies, in one Beam call

**Pitch:** Paste a GitHub repo (or pick a curated package). RepoTruth packs README + docs + source into a single prompt, asks Beam (1M context, coding-tuned) to find documentation that contradicts the code, and returns severity-ranked findings with file citations, suggested patches, and a live **token thrift meter** (prompt / reasoning / answer tokens × reasoning_effort).

**Why this wins the rubric**
- **Creativity (25%):** "Docs lie. Code doesn't." Visual autopsy of a real package — not another chat box or static leaderboard.
- **Technical execution (25%):** Repo packing, structured JSON findings, dual API backends (Reflection + HF Inference Providers), fixture mode for reliable demos, HF dataset of verified drifts.
- **Usefulness (25%):** Maintainers and agents waste hours on stale docs. Olly already found real bugs in starlette/httpx/click — we productize that.
- **Use of Beam (25%):** Directly exercises **1M context + SWE strength + token-efficient reasoning** — the three Beam headlines. Effort sweep shows thrift.

**Why judges (esp. Ben) will like it**
- Hub-native Gradio Space + dataset (his habitat).
- Mirrors the HF blog vibe-eval "long-context retrieval over a codebase".
- Ships the gap olly advertised but couldn't host.
- 90-second demo is cinematic: pack → swallow → red findings → thrift meter → patch.

**Build plan (≤2 days)**
1. Core Python packer + Beam client (Reflection / HF router / mock).
2. Gradio Space on `mr-dee` or `greenrobin` + curated fixtures (starlette, click, httpx-like mini packs).
3. Dataset `…/repotruth-findings` with traces.
4. Vercel landing (dl88jing-2798) with cover + embed.
5. GitHub `dl88jing/repotruth`.
6. HyperFrames + Kokoro narrated demo + short deck.
7. Draft discussion post — **do not publish**.

**Affiliation in public copy:** Green Robin Labs. No Adobe / personal work details.

## 6. API key status (blocking note)

- No `REFLECTION_API_KEY` found in env, `/home/box/.config`, or `/workspace`.
- HF token at `~/.config/hf/token` authenticates as **mr-dee** with repo write, but **Inference Providers call fails**: *"This authentication method does not have sufficient permissions to call Inference Providers"*.
- Unblock options (exact):
  1. **Reflection (preferred for challenge narrative):** Sign up at https://platform.reflection.ai → public beta is free with daily token limits → create API key → `export REFLECTION_API_KEY=…`. Docs: https://developers.reflection.ai/authentication
  2. **HF Inference Providers:** In HF settings → Access Tokens → create/edit token with **Make calls to the serverless Inference API / Inference Providers** permission (or a classic write token) → set as Space secret `HF_TOKEN` / `HUGGINGFACE_HUB_TOKEN`. Model id: `reflection/Beam-1.0-501B-A23B:baseten` or `:auto`.
  3. Meanwhile: build + record demo against **fixture/mock mode** with real packing UX.

## 7. Decision

Proceed to Phase 2 with **RepoTruth**. Rules match the brief; no need to halt.
