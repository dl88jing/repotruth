#!/usr/bin/env python3
"""Generate Kokoro VO wavs for RepoTruth demo v2."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
MODEL = Path("/workspace/ctrl-space/kokoro-v1.0.onnx")
VOICES = Path("/workspace/ctrl-space/voices-v1.0.bin")
OUT = HERE / "assets" / "audio"
OUT.mkdir(parents=True, exist_ok=True)

k = Kokoro(str(MODEL), str(VOICES))
narr = json.loads((HERE / "narration-v2.json").read_text())
durs = {}
parts = []
first_sr = None
for sid, text in narr:
    samples, sr = k.create(text, voice="af_heart", speed=1.05, lang="en-us")
    first_sr = first_sr or sr
    path = OUT / f"{sid}.wav"
    sf.write(path, samples, sr)
    durs[sid] = float(len(samples) / sr)
    print(sid, round(durs[sid], 2), flush=True)
    parts.append(samples)
    parts.append(np.zeros(int(0.22 * sr)))

full = np.concatenate(parts)
sf.write(OUT / "narration.wav", full, first_sr)
durs["narration"] = float(len(full) / first_sr)
(OUT / "durations.json").write_text(json.dumps(durs, indent=2) + "\n")
print("total", round(durs["narration"], 2))
