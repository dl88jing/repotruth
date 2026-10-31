#!/usr/bin/env bash
# One-command fixture demo (no API key required).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
export REPOTRUTH_BACKEND="${REPOTRUTH_BACKEND:-mock}"
export PYTHONPATH="${ROOT}/app${PYTHONPATH:+:$PYTHONPATH}"
echo "==> RepoTruth demo (backend=$REPOTRUTH_BACKEND)"
echo "==> Fixture: fixtures/tinyclick"
python3 scripts/repotruth_cli.py fixtures/tinyclick
echo
echo "==> Tip: for a live Beam call:"
echo "    export REFLECTION_API_KEY=...   # https://platform.reflection.ai"
echo "    REPOTRUTH_BACKEND=reflection ./demo.sh"
