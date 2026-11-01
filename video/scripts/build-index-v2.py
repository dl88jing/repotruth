#!/usr/bin/env python3
"""Build HyperFrames index.html for RepoTruth demo v2 (screen-recording dominant)."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
AUDIO = HERE / "assets" / "audio"
CAPS = HERE / "captures"
durs = json.loads((AUDIO / "durations.json").read_text())

def probe(p: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(p)],
        text=True,
    ).strip()
    return float(out)

# Copy screen clips into assets/screen for HyperFrames relative paths
screen = HERE / "assets" / "screen"
screen.mkdir(parents=True, exist_ok=True)
clips = {
    "landing": CAPS / "01-landing.mp4",
    "audit": CAPS / "02-audit.mp4",
    "github": CAPS / "03-github.mp4",
}
clip_durs = {}
for k, src in clips.items():
    dest = screen / f"{k}.mp4"
    dest.write_bytes(src.read_bytes())
    clip_durs[k] = probe(dest)

# Scene plan:
# vo0 title card — pad to max(vo0+0.6, 7.5)
# vo1 over landing video — scene length = max(vo1+0.8, clip_durs['landing'])
# vo2 over audit video
# vo3 over github video
# vo4 architecture card
# vo5 outro

GAP = 0.45  # between scenes
scenes = []

def add(sid, kind, vo_key, min_extra=0.55, video=None, title=None, sub=None, kicker=None):
    vo = durs[vo_key]
    if video:
        length = max(vo + min_extra, clip_durs[video] + 0.15)
    else:
        length = max(vo + min_extra, 7.2 if kind == "card" else vo + 0.8)
    scenes.append({
        "id": sid, "kind": kind, "vo": vo_key, "vo_dur": vo,
        "duration": round(length, 3), "video": video,
        "title": title, "sub": sub, "kicker": kicker,
    })

add("s0", "card", "vo0", 0.9, title="Documentation that lies.", sub="Catch docs that contradict the code — live on Beam.", kicker="HOOK")
add("s1", "screen", "vo1", 0.6, video="landing", title=None, kicker="LIVE APP", sub="repotruth.vercel.app")
add("s2", "screen", "vo2", 0.6, video="audit", kicker="LIVE AUDIT", sub="Fixture tinyclick · effort low · real Beam")
add("s3", "screen", "vo3", 0.6, video="github", kicker="GITHUB MODE", sub="Paste a public repo · same live path")
add("s4", "card", "vo4", 0.8, title="Pack → Beam → findings.", sub="1M context · measured thrift · verified citations.", kicker="ARCHITECTURE")
add("s5", "card", "vo5", 0.9, title="RepoTruth", sub="repotruth.vercel.app · Green Robin Labs", kicker="TRY IT")

starts = []
t = 0.0
for sc in scenes:
    starts.append(round(t, 3))
    t += sc["duration"]
total = round(t, 3)

# Screen share
screen_runtime = sum(sc["duration"] for sc in scenes if sc["kind"] == "screen")
print("total", total, "screen", round(screen_runtime, 2), "share", round(100*screen_runtime/total, 1))

# Build HTML
parts = []
parts.append(f'''<!doctype html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=1920, height=1080">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:#07090f}}
#root{{width:1920px;height:1080px;position:relative;font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif;color:#e8ecf7}}
.scene{{position:absolute;inset:0;background:#07090f}}
.k{{position:absolute;left:96px;top:72px;font-size:24px;letter-spacing:.2em;text-transform:uppercase;color:#7c5cff;font-weight:600;z-index:3}}
h1{{position:absolute;left:96px;top:160px;font-size:88px;line-height:1.05;letter-spacing:-.03em;width:1100px;font-weight:700;z-index:3}}
.sub{{position:absolute;left:96px;top:420px;font-size:34px;color:#9aa3b8;width:900px;line-height:1.35;z-index:3}}
.badge{{position:absolute;left:96px;bottom:64px;font-size:22px;color:#6b7280;z-index:3}}
.fullvid{{position:absolute;inset:0;width:1920px;height:1080px;object-fit:cover;background:#000}}
.scrim{{position:absolute;left:0;right:0;bottom:0;height:180px;background:linear-gradient(transparent,rgba(7,9,15,.92));z-index:2;pointer-events:none}}
.caption{{position:absolute;left:96px;bottom:56px;z-index:3;display:flex;gap:16px;align-items:center}}
.pill{{background:rgba(18,22,36,.92);border:1px solid #2a3150;border-radius:999px;padding:12px 24px;font-size:24px;font-weight:600}}
.arch{{position:absolute;right:96px;top:180px;width:860px;display:grid;gap:16px;z-index:3}}
.arch .card{{border-radius:16px;border:1px solid #242a44;background:linear-gradient(180deg,#161a2b,#101424);padding:22px 26px}}
.arch .card .t{{font-family:"IBM Plex Mono",monospace;font-size:18px;color:#22d3ee}}
.arch .card .h{{font-size:30px;font-weight:700;margin-top:6px}}
.arch .card .d{{font-size:22px;color:#9aa3b8;margin-top:8px;line-height:1.35}}
.cta{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;z-index:3}}
.cta h1{{position:static;width:auto;font-size:110px;margin-bottom:12px}}
.cta .tag{{font-size:34px;color:#9aa3b8;margin-bottom:28px}}
.cta .urls{{font-family:"IBM Plex Mono",monospace;font-size:28px;color:#22d3ee;line-height:1.7}}
.cta .credit{{margin-top:36px;font-size:20px;color:#6b7280;letter-spacing:.08em;text-transform:uppercase}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="1920" data-height="1080" data-fps="30">
''')

for i, sc in enumerate(scenes):
    start = starts[i]
    dur = sc["duration"]
    if sc["kind"] == "screen":
        parts.append(f'''<section id="{sc["id"]}" class="clip scene" data-start="{start:.3f}" data-duration="{dur:.3f}" data-track-index="0">
<video class="fullvid" src="assets/screen/{sc["video"]}.mp4" muted playsinline></video>
<div class="scrim"></div>
<div class="caption"><div class="pill">{sc["kicker"]} · {sc["sub"]}</div></div>
<div class="badge">RepoTruth · Build with Beam · LIVE</div>
</section>
''')
    elif sc["id"] == "s4":
        parts.append(f'''<section id="{sc["id"]}" class="clip scene" data-start="{start:.3f}" data-duration="{dur:.3f}" data-track-index="0">
<div class="k">{sc["kicker"]}</div>
<h1>{sc["title"]}</h1>
<p class="sub">{sc["sub"]}</p>
<div class="arch">
  <div class="card"><div class="t">pack</div><div class="h">Whole repo → prompt</div><div class="d">README + docs + source into one Beam call</div></div>
  <div class="card"><div class="t">Beam-1.0-501B-A23B</div><div class="h">chat.completions</div><div class="d">JSON findings + reasoning_tokens usage</div></div>
  <div class="card"><div class="t">thrift</div><div class="h">−57% reasoning</div><div class="d">tinyclick low vs medium · same 3 findings</div></div>
</div>
<div class="badge">RepoTruth · Build with Beam · LIVE</div>
</section>
''')
    elif sc["id"] == "s5":
        parts.append(f'''<section id="{sc["id"]}" class="clip scene" data-start="{start:.3f}" data-duration="{dur:.3f}" data-track-index="0">
<div class="cta">
  <div class="k" style="position:static;margin-bottom:18px">{sc["kicker"]}</div>
  <h1>{sc["title"]}</h1>
  <div class="tag">Catch documentation that lies.</div>
  <div class="urls">repotruth.vercel.app<br/>github.com/dl88jing/repotruth</div>
  <div class="credit">Green Robin Labs · Hugging Face × Reflection Build with Beam</div>
</div>
</section>
''')
    else:
        parts.append(f'''<section id="{sc["id"]}" class="clip scene" data-start="{start:.3f}" data-duration="{dur:.3f}" data-track-index="0">
<div class="k">{sc["kicker"]}</div>
<h1>{sc["title"]}</h1>
<p class="sub">{sc["sub"]}</p>
<div class="badge">RepoTruth · Build with Beam · LIVE</div>
</section>
''')

# Audio tracks per VO aligned to scene starts
for i, sc in enumerate(scenes):
    start = starts[i]
    vo = sc["vo"]
    vd = sc["vo_dur"]
    parts.append(f'<audio id="{vo}" src="assets/audio/{vo}.wav" data-start="{start:.3f}" data-duration="{vd:.3f}" data-track-index="1" data-volume="1"></audio>\n')

# GSAP timeline
parts.append("<script>\nconst tl=gsap.timeline({paused:true});\n")
for i, sc in enumerate(scenes):
    start = starts[i]
    dur = sc["duration"]
    sid = sc["id"]
    if sc["kind"] == "screen":
        parts.append(f'tl.from("#{sid} .fullvid",{{opacity:0,duration:0.6,ease:"power2.out"}},{start+0.05:.3f});\n')
        parts.append(f'tl.from("#{sid} .pill",{{opacity:0,y:18,duration:0.5,ease:"power2.out"}},{start+0.2:.3f});\n')
    elif sid == "s5":
        parts.append(f'tl.from("#{sid} .cta > *",{{opacity:0,y:24,duration:0.7,stagger:0.1,ease:"power2.out"}},{start+0.12:.3f});\n')
    elif sid == "s4":
        parts.append(f'tl.from("#{sid} .k, #{sid} h1, #{sid} .sub",{{opacity:0,y:24,duration:0.7,stagger:0.1,ease:"power2.out"}},{start+0.12:.3f});\n')
        parts.append(f'tl.from("#{sid} .arch .card",{{opacity:0,x:40,duration:0.55,stagger:0.12,ease:"power2.out"}},{start+0.35:.3f});\n')
    else:
        parts.append(f'tl.from("#{sid} .k, #{sid} h1, #{sid} .sub, #{sid} .badge",{{opacity:0,y:24,duration:0.7,stagger:0.1,ease:"power2.out"}},{start+0.12:.3f});\n')

parts.append('''window.__timelines = window.__timelines || {};
window.__timelines["main"]=tl;tl.seek(0);
</script></body></html>
''')

(HERE / "index.html").write_text("".join(parts))
timings = {
    "starts": starts,
    "durs": [sc["duration"] for sc in scenes],
    "total": total,
    "screen_runtime": screen_runtime,
    "screen_share": round(screen_runtime / total, 4),
    "clip_durs": clip_durs,
    "vo_durs": {sc["vo"]: sc["vo_dur"] for sc in scenes},
}
(HERE / "timings.json").write_text(json.dumps(timings, indent=2) + "\n")
print(json.dumps(timings, indent=2))
