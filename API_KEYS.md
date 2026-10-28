# Getting a Beam API key

No Reflection/Beam key was present in this environment. Use one of:

## Option A — Reflection platform (recommended)

1. Go to https://platform.reflection.ai (or https://reflection.ai and open Platform).
2. Sign up / sign in.
3. Create an API key.
4. Export:
   ```bash
   export REFLECTION_API_KEY=sk-...
   export REPOTRUTH_BACKEND=reflection
   ```
5. Base URL used by RepoTruth: `https://api.reflection.ai/openai/v1`
6. Model id: `Beam-1.0-501B-A23B` (or `reflection/Beam-1.0-501B-A23B` depending on the endpoint).

## Option B — Hugging Face Inference Providers

1. Create a fine-grained HF token at https://huggingface.co/settings/tokens with **Inference Providers** / Make calls to Inference Providers permission.
2. Ensure the token’s user has access to Beam via Inference Providers (may require accepting provider terms on the model page).
3. Export:
   ```bash
   export HF_TOKEN=hf_...
   export REPOTRUTH_BACKEND=hf
   ```
4. Note: the current `mr-dee` write token returned *insufficient permissions for Inference Providers* — mint a new token with that scope, or use a different account that has it.

## Option C — Mock / fixtures (no key)

```bash
export REPOTRUTH_BACKEND=mock
python scripts/repotruth_cli.py fixtures/tinyclick
```

## Gradio Space hosting note

Creating a new **Gradio** Space on free CPU now returns HTTP 402 (HF PRO required). RepoTruth ships as a free **Static** Space with interactive fixtures; the Gradio app lives in `space/` and runs locally or on a PRO account / Modal / other host.
