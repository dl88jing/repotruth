#!/usr/bin/env bash
# Wire REFLECTION_API_KEY from /workspace/beam-hack/.reflection_api_key into
# Vercel (Production+Preview, Sensitive) when present. Never prints the key.
set -euo pipefail
KEY_FILE="${1:-/workspace/beam-hack/.reflection_api_key}"
if [[ ! -f "$KEY_FILE" ]]; then
  echo "No key at $KEY_FILE — code is ready; another agent still provisioning."
  exit 2
fi
KEY="$(tr -d '[:space:]' < "$KEY_FILE")"
if [[ -z "$KEY" || ${#KEY} -lt 8 ]]; then
  echo "Key file empty/too short — refusing."
  exit 3
fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/landing"
# Remove existing then add Sensitive for production + preview
# vercel env add NAME ENV <<< value
printf '%s' "$KEY" | vercel env add REFLECTION_API_KEY production --sensitive --force --scope dylan-team 2>/dev/null \
  || printf '%s' "$KEY" | vercel env add REFLECTION_API_KEY production --sensitive --scope dylan-team
printf '%s' "$KEY" | vercel env add REFLECTION_API_KEY preview --sensitive --force --scope dylan-team 2>/dev/null \
  || printf '%s' "$KEY" | vercel env add REFLECTION_API_KEY preview --sensitive --scope dylan-team
echo "Wired REFLECTION_API_KEY to Vercel project repotruth (production+preview, sensitive)."
echo "Note: landing is static HTML today — key is ready for any future serverless route."
echo "For HF Space Gradio secrets, set REFLECTION_API_KEY in the Space settings (needs Gradio/PRO host)."
