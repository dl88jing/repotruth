# Getting a Beam API key

No Reflection/Beam key was found in env, `~/.config`, or `/workspace`.

## Option A — Reflection platform (recommended, free beta)

1. Sign up at **https://platform.reflection.ai** (public beta — free to start; daily input/output allocations reset 12:00 AM PT).
2. Open **API Keys**, create a key (shown once).
3. Docs: https://developers.reflection.ai/quickstart
4. Export and run:
   ```bash
   export REFLECTION_API_KEY='<key>'
   export REPOTRUTH_BACKEND=reflection
   python scripts/repotruth_cli.py fixtures/tinyclick
   ```
5. Endpoint: `https://api.reflection.ai/openai/v1`  
   Model: `Beam-1.0-501B-A23B`

```bash
curl https://api.reflection.ai/openai/v1/chat/completions \
  -H "Authorization: Bearer $REFLECTION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"Beam-1.0-501B-A23B","messages":[{"role":"user","content":"ping"}]}'
```

## Option B — Hugging Face Inference Providers

1. Create a fine-grained token at https://huggingface.co/settings/tokens with **Make calls to Inference Providers**.
2. Accept any provider terms on https://huggingface.co/reflection/Beam-1.0-501B-A23B if prompted.
3. Export:
   ```bash
   export HF_TOKEN=hf_...
   export REPOTRUTH_BACKEND=hf
   ```
4. The current `mr-dee` write token returned *insufficient permissions for Inference Providers* — mint a new token with that scope.

## Option C — Mock / fixtures (no key)

```bash
export REPOTRUTH_BACKEND=mock
python scripts/repotruth_cli.py fixtures/tinyclick
```

## Gradio Space hosting

New Gradio Spaces on free CPU return **HTTP 402** (HF PRO). RepoTruth is published as a free **Static** Space with interactive fixtures. The Gradio app in `space/` runs locally or on HF PRO / Modal / another host. After PRO or a host is available, set Space secrets `REFLECTION_API_KEY` or `HF_TOKEN`.
