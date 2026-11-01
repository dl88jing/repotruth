#!/usr/bin/env bash
set -euo pipefail
export PATH="/home/box/.local/node-v22/bin:$PATH"
cd /workspace/beam-hack/video
exec npx --yes hyperframes@0.8.60 render --quality delivery --output renders/repotruth-demo-v2.mp4
