/**
 * POST /api/audit
 *   { "fixture": "tinyclick", "effort": "medium" }
 *   { "github": "https://github.com/owner/repo", "ref": "main", "effort": "medium" }
 * GET  /api/audit?fixture=tinyclick
 *
 * Live Reflection Beam (model MUST be Beam-1.0-501B-A23B). Key: REFLECTION_API_KEY (server-side only).
 * Rate limits: ~5/IP/hour, ~150/day for live calls. Fixtures are free of rate limit when not live? 
 * We rate-limit ALL live Beam calls (fixture or github). Fixture fallback never consumes.
 * Repo size cap for GitHub: max ~120 files / ~280k packed chars / ~2.5MB zip.
 */
const fs = require('fs');
const path = require('path');
const os = require('os');
const { check, consume } = require('../lib/rateLimit');

const FIXTURES = ['tinyclick', 'tinystar', 'tinyhttp'];
const MODEL = process.env.BEAM_MODEL || 'Beam-1.0-501B-A23B';
const MAX_ZIP_BYTES = 2_500_000;
const MAX_FILES = 120;
const MAX_PACK_CHARS = 280_000;
const MAX_FILE_CHARS = 80_000;
const SKIP_DIRS = new Set(['.git','.hg','.svn','__pycache__','node_modules','.venv','venv','dist','build','.next','.turbo','target','vendor','.mypy_cache','tests','test','docs/_build']);
const SKIP_SUFFIXES = new Set(['.png','.jpg','.jpeg','.gif','.webp','.ico','.pdf','.zip','.tar','.gz','.whl','.so','.dylib','.bin','.pyc','.lock','.woff','.woff2','.ttf','.mp4','.wav']);
const DOC_NAMES = new Set(['readme','changelog','contributing','license','authors']);
const DOC_SUFFIXES = new Set(['.md','.rst','.txt','.adoc']);
const CODE_SUFFIXES = new Set(['.py','.js','.ts','.tsx','.jsx','.go','.rs','.java','.kt','.c','.h','.cpp','.hpp','.cs','.rb','.php','.swift','.scala','.toml','.yaml','.yml','.json','.ini','.cfg','.sh']);

const SYSTEM_PROMPT = `You are RepoTruth, an expert code+docs auditor.
Your job: find places where DOCUMENTATION CONTRADICTS the CODE in the provided repository dump.

Rules:
- Only report contradictions you can cite from both a doc file and a code file.
- Do NOT invent APIs. Do NOT report style nits, typos, or missing docs unless the docs make a false claim.
- Prefer high-severity functional lies (wrong flags, wrong defaults, wrong exit codes, wrong control flow).
- Return STRICT JSON only, matching this schema:
{
  "repo": string,
  "summary": string,
  "findings": [
    {
      "id": string,
      "severity": "critical" | "high" | "medium" | "low",
      "title": string,
      "doc_refs": [string],
      "code_refs": [string],
      "evidence": string,
      "suggested_fix": string,
      "confidence": number
    }
  ]
}
If nothing is wrong, return findings: [].
`;

function loadData(name) {
  const p = path.join(process.cwd(), 'api_data', `${name}.json`);
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function extractJson(text) {
  let t = (text || '').trim();
  if (t.startsWith('```')) {
    t = t.replace(/^```(?:json)?\s*/, '').replace(/\s*```$/, '');
  }
  try {
    return JSON.parse(t);
  } catch {
    const m = t.match(/\{[\s\S]*\}/);
    if (!m) throw new Error('No JSON in model response');
    try { return JSON.parse(m[0]); } catch (e) {
      // brace-trim fallback
      const start = t.indexOf('{');
      if (start < 0) throw e;
      for (let end = t.length; end > start; end--) {
        try { return JSON.parse(t.slice(start, end)); } catch {}
      }
      throw e;
    }
  }
}

async function callBeam(messages, effort) {
  const key = process.env.REFLECTION_API_KEY;
  if (!key) {
    const err = new Error('REFLECTION_API_KEY not set');
    err.code = 'NO_KEY';
    throw err;
  }
  const base = (process.env.REFLECTION_BASE_URL || 'https://api.reflection.ai/openai/v1').replace(/\/$/, '');
  const t0 = Date.now();
  const resp = await fetch(`${base}/chat/completions`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: MODEL,
      messages,
      max_tokens: 6144,
      temperature: 0.2,
      reasoning_effort: effort || 'medium',
    }),
  });
  const rawText = await resp.text();
  if (!resp.ok) {
    const err = new Error(`reflection API ${resp.status}: ${rawText.slice(0, 400)}`);
    err.code = 'HTTP';
    throw err;
  }
  const raw = JSON.parse(rawText);
  const msg = (raw.choices && raw.choices[0] && raw.choices[0].message) || {};
  let content = msg.content || '';
  if (!content && msg.reasoning_content) content = msg.reasoning_content;
  const parsed = extractJson(content);
  const u = raw.usage || {};
  const details = u.completion_tokens_details || {};
  return {
    backend: 'reflection',
    model: MODEL,
    parsed,
    usage: {
      prompt_tokens: u.prompt_tokens || 0,
      completion_tokens: u.completion_tokens || 0,
      reasoning_tokens: details.reasoning_tokens || u.reasoning_tokens || 0,
      total_tokens: u.total_tokens || 0,
    },
    latency_s: (Date.now() - t0) / 1000,
    usage_source: 'live',
    reasoning_effort: effort || 'medium',
  };
}

function fixtureResult(data, effort, fallbackFrom, fallbackReason) {
  const parsed = { ...data.fixture };
  if (fallbackFrom) {
    parsed.summary = `[FALLBACK from ${fallbackFrom}] ${fallbackReason}. Showing fixture-seeded findings. ` + (parsed.summary || '');
    parsed.fallback_from = fallbackFrom;
    parsed.fallback_reason = fallbackReason;
  }
  return {
    backend: 'mock',
    model: 'mock/Beam-fixture',
    parsed,
    usage: data.fixture.usage || {},
    latency_s: 0.05,
    usage_source: 'fixture-seeded',
    reasoning_effort: effort || 'medium',
    fallback_from: fallbackFrom || null,
    fallback_reason: fallbackReason || null,
  };
}

function parseGithub(url) {
  if (!url || typeof url !== 'string') return null;
  const m = url.trim().match(/^https?:\/\/(?:www\.)?github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+?)(?:\.git)?(?:\/(?:tree|blob)\/([^\/\s]+))?\/?$/i);
  if (!m) return null;
  return { owner: m[1], repo: m[2].replace(/\.git$/, ''), refHint: m[3] || null };
}

function kindOf(rel) {
  const base = path.basename(rel).toLowerCase();
  const stem = base.replace(/\.[^.]+$/, '');
  const ext = path.extname(base).toLowerCase();
  if (DOC_NAMES.has(stem) || DOC_SUFFIXES.has(ext)) return 'doc';
  if (CODE_SUFFIXES.has(ext)) return 'code';
  return 'other';
}

function packFromDir(root, name, maxChars) {
  const files = [];
  function walk(dir) {
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
    for (const ent of entries) {
      if (ent.name.startsWith('.')) continue;
      const full = path.join(dir, ent.name);
      if (ent.isDirectory()) {
        if (SKIP_DIRS.has(ent.name)) continue;
        walk(full);
        continue;
      }
      const rel = path.relative(root, full).split(path.sep).join('/');
      const ext = path.extname(ent.name).toLowerCase();
      if (SKIP_SUFFIXES.has(ext)) continue;
      let st;
      try { st = fs.statSync(full); } catch { continue; }
      if (st.size > 400_000) continue;
      let text;
      try { text = fs.readFileSync(full, 'utf8'); } catch { continue; }
      if (text.length > MAX_FILE_CHARS) text = text.slice(0, MAX_FILE_CHARS) + '\n… [truncated]';
      files.push({ path: rel, kind: kindOf(rel), text, chars: text.length });
      if (files.length > MAX_FILES * 2) break;
    }
  }
  walk(root);
  const rank = { doc: 0, code: 1, other: 2 };
  files.sort((a, b) => (rank[a.kind] - rank[b.kind]) || a.path.localeCompare(b.path));
  const kept = files.slice(0, MAX_FILES);
  let used = 0;
  const parts = [];
  for (const f of kept) {
    const header = `\n\n===== FILE: ${f.path} (${f.kind}) =====\n`;
    const chunk = header + f.text;
    if (used + chunk.length > maxChars) {
      const remain = maxChars - used - header.length - 64;
      if (remain > 200) parts.push(header + f.text.slice(0, remain) + '\n… [truncated]');
      break;
    }
    parts.push(chunk);
    used += chunk.length;
  }
  const total_chars = kept.reduce((s, f) => s + f.chars, 0);
  return {
    name,
    files: kept,
    total_chars,
    approx_tokens: Math.max(1, Math.floor(total_chars / 4)),
    blob: parts.join(''),
    docs: kept.filter(f => f.kind === 'doc').length,
    code: kept.filter(f => f.kind === 'code').length,
  };
}

async function fetchAndPackGithub(owner, repo, ref) {
  let AdmZip;
  try { AdmZip = require('adm-zip'); } catch (e) {
    const err = new Error('Server missing adm-zip dependency');
    err.code = 'DEP';
    throw err;
  }
  const refsToTry = ref ? [ref] : ['main', 'master'];
  let buf = null;
  let usedRef = null;
  let lastStatus = 0;
  for (const r of refsToTry) {
    const url = `https://codeload.github.com/${owner}/${repo}/zip/refs/heads/${encodeURIComponent(r)}`;
    const resp = await fetch(url, { redirect: 'follow' });
    lastStatus = resp.status;
    if (!resp.ok) continue;
    const ab = await resp.arrayBuffer();
    if (ab.byteLength > MAX_ZIP_BYTES) {
      const err = new Error(`Repo zip too large (${ab.byteLength} bytes). Cap is ${MAX_ZIP_BYTES}. Try a smaller public repo.`);
      err.code = 'SIZE';
      throw err;
    }
    buf = Buffer.from(ab);
    usedRef = r;
    break;
  }
  if (!buf) {
    const err = new Error(`Could not download GitHub zip for ${owner}/${repo} (HTTP ${lastStatus}). Use a public repo URL.`);
    err.code = 'FETCH';
    throw err;
  }
  const zip = new AdmZip(buf);
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'rt-'));
  zip.extractAllTo(tmp, true);
  // zipball has a single top-level folder
  const top = fs.readdirSync(tmp).find(n => fs.statSync(path.join(tmp, n)).isDirectory()) || tmp;
  const root = top === tmp ? tmp : path.join(tmp, top);
  const packed = packFromDir(root, repo, MAX_PACK_CHARS);
  // cleanup best-effort
  try { fs.rmSync(tmp, { recursive: true, force: true }); } catch {}
  if (packed.files.length === 0) {
    const err = new Error('No readable source/docs files found after unpack.');
    err.code = 'EMPTY';
    throw err;
  }
  packed.ref = usedRef;
  packed.github = `https://github.com/${owner}/${repo}`;
  return packed;
}

function buildMessages(packed) {
  const user = `Repository name: ${packed.name}\nFiles packed: ${packed.files.length} (~${packed.approx_tokens} tokens est.)\nAudit the dump below for documentation that lies about the code.\n${packed.blob}\n\nRespond with JSON only.`;
  return [
    { role: 'system', content: SYSTEM_PROMPT },
    { role: 'user', content: user },
  ];
}

function setRateHeaders(res, info) {
  if (!info) return;
  res.setHeader('X-RateLimit-IP-Remaining', String(info.ipRemaining ?? ''));
  res.setHeader('X-RateLimit-Global-Remaining', String(info.globalRemaining ?? ''));
  if (info.retry_after_s) res.setHeader('Retry-After', String(info.retry_after_s));
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  let body = {};
  if (req.method === 'POST') {
    try {
      body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
    } catch {
      res.status(400).json({ error: 'Invalid JSON body' });
      return;
    }
  }

  const effort = body.effort || req.query.effort || 'medium';
  const githubUrl = body.github || body.url || req.query.github || req.query.url;
  const fixture = (body.fixture || req.query.fixture || (githubUrl ? null : 'tinyclick') || '').toLowerCase() || null;
  const wantLive = body.live !== false; // default live

  // GitHub path
  if (githubUrl) {
    const parsed = parseGithub(githubUrl);
    if (!parsed) {
      res.status(400).json({ error: 'Invalid GitHub URL. Example: https://github.com/encode/httpcore' });
      return;
    }
    const gate = check(req, { perIpHour: 5, globalDay: 150 });
    if (!gate.ok) {
      setRateHeaders(res, gate);
      res.status(429).json({ ok: false, error: gate.error, retry_after_s: gate.retry_after_s });
      return;
    }
    try {
      const packed = await fetchAndPackGithub(parsed.owner, parsed.repo, body.ref || parsed.refHint);
      const remaining = consume(gate);
      setRateHeaders(res, remaining);
      const messages = buildMessages(packed);
      const result = await callBeam(messages, effort);
      result.parsed = result.parsed || {};
      result.parsed.repo = result.parsed.repo || packed.name;
      res.status(200).json({
        ok: true,
        mode: 'github',
        github: packed.github,
        ref: packed.ref,
        pack: {
          files: packed.files.length,
          approx_tokens: packed.approx_tokens,
          total_chars: packed.total_chars,
          docs: packed.docs,
          code: packed.code,
          max_pack_chars: MAX_PACK_CHARS,
          max_files: MAX_FILES,
        },
        result,
        live: true,
        rate_limit: remaining,
        checked_at: new Date().toISOString(),
      });
    } catch (e) {
      setRateHeaders(res, { ipRemaining: gate.ipRemaining, globalRemaining: gate.globalRemaining });
      const status = e.code === 'SIZE' ? 413 : 400;
      res.status(status).json({ ok: false, error: e.message, code: e.code || 'ERR' });
    }
    return;
  }

  // Fixture path
  if (!FIXTURES.includes(fixture)) {
    res.status(400).json({ error: `Unknown fixture. Choose one of: ${FIXTURES.join(', ')} — or pass github URL.` });
    return;
  }
  const data = loadData(fixture);

  if (!wantLive || !process.env.REFLECTION_API_KEY) {
    const result = fixtureResult(data, effort, process.env.REFLECTION_API_KEY ? null : 'config', 'no Reflection key');
    res.status(200).json({ ok: true, mode: 'fixture', fixture, pack: data.pack, result, live: false, checked_at: new Date().toISOString() });
    return;
  }

  const gate = check(req, { perIpHour: 5, globalDay: 150 });
  if (!gate.ok) {
    // rate-limited: still return fixture seeded with banner (useful for judges)
    setRateHeaders(res, gate);
    const result = fixtureResult(data, effort, 'rate-limit', gate.error);
    res.status(200).json({ ok: true, mode: 'fixture', fixture, pack: data.pack, result, live: false, rate_limited: true, checked_at: new Date().toISOString() });
    return;
  }

  let result;
  try {
    const remaining = consume(gate);
    setRateHeaders(res, remaining);
    result = await callBeam(data.messages, effort);
    result.parsed = result.parsed || {};
    result.parsed.repo = result.parsed.repo || fixture;
    res.status(200).json({
      ok: true,
      mode: 'fixture',
      fixture,
      pack: data.pack,
      result,
      live: true,
      rate_limit: remaining,
      checked_at: new Date().toISOString(),
    });
  } catch (e) {
    result = fixtureResult(data, effort, 'reflection', `${e.code || e.name}: ${e.message}`);
    res.status(200).json({ ok: true, mode: 'fixture', fixture, pack: data.pack, result, live: false, checked_at: new Date().toISOString() });
  }
};
