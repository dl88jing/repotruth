/**
 * POST /api/audit  { "fixture": "tinyclick", "effort": "medium" }
 * GET  /api/audit?fixture=tinyclick&effort=medium
 *
 * Live Reflection Beam when REFLECTION_API_KEY is set; labeled fixture fallback otherwise.
 * Never logs the API key.
 */
const fs = require('fs');
const path = require('path');

const FIXTURES = ['tinyclick', 'tinystar', 'tinyhttp'];

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
    return JSON.parse(m[0]);
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
  const model = process.env.BEAM_MODEL || 'Beam-1.0-501B-A23B';
  const t0 = Date.now();
  const resp = await fetch(`${base}/chat/completions`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${key}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      messages,
      max_tokens: 4096,
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
    model,
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
    backend: fallbackFrom ? 'mock' : 'mock',
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

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') {
    res.status(204).end();
    return;
  }

  let body = {};
  if (req.method === 'POST') {
    body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
  }
  const fixture = (body.fixture || req.query.fixture || 'tinyclick').toLowerCase();
  const effort = body.effort || req.query.effort || 'medium';
  if (!FIXTURES.includes(fixture)) {
    res.status(400).json({ error: `Unknown fixture. Choose one of: ${FIXTURES.join(', ')}` });
    return;
  }

  const data = loadData(fixture);
  let result;
  try {
    result = await callBeam(data.messages, effort);
    result.parsed = result.parsed || {};
    result.parsed.repo = result.parsed.repo || fixture;
  } catch (e) {
    result = fixtureResult(data, effort, 'reflection', `${e.code || e.name}: ${e.message}`);
  }

  res.status(200).json({
    ok: true,
    fixture,
    pack: data.pack,
    result,
    live: result.usage_source === 'live',
    checked_at: new Date().toISOString(),
  });
};
