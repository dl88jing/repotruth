/**
 * Best-effort in-memory rate limiter for Vercel serverless.
 * Per-IP ~5/hour, global ~150/day. Warm instances share state; cold starts reset.
 * Good enough for a judge demo; returns remaining quotas in headers.
 */
const g = globalThis;
if (!g.__repotruthRL) {
  g.__repotruthRL = {
    ipHour: new Map(), // ip -> {count, reset}
    globalDay: { count: 0, reset: 0 },
  };
}
const store = g.__repotruthRL;

function now() { return Date.now(); }

function clientIp(req) {
  const xf = (req.headers['x-forwarded-for'] || '').split(',')[0].trim();
  return xf || req.headers['x-real-ip'] || req.socket?.remoteAddress || 'unknown';
}

function check(req, { perIpHour = 5, globalDay = 150 } = {}) {
  const t = now();
  const ip = clientIp(req);

  // global day
  if (!store.globalDay.reset || t > store.globalDay.reset) {
    store.globalDay = { count: 0, reset: t + 24 * 3600 * 1000 };
  }
  // per-ip hour
  let bucket = store.ipHour.get(ip);
  if (!bucket || t > bucket.reset) {
    bucket = { count: 0, reset: t + 3600 * 1000 };
    store.ipHour.set(ip, bucket);
  }

  const ipRemaining = Math.max(0, perIpHour - bucket.count);
  const globalRemaining = Math.max(0, globalDay - store.globalDay.count);

  if (bucket.count >= perIpHour) {
    return {
      ok: false,
      status: 429,
      error: `Per-IP rate limit: ${perIpHour} live audits per hour. Try a fixture or come back later.`,
      ip,
      ipRemaining: 0,
      globalRemaining,
      retry_after_s: Math.ceil((bucket.reset - t) / 1000),
    };
  }
  if (store.globalDay.count >= globalDay) {
    return {
      ok: false,
      status: 429,
      error: `Global daily rate limit: ${globalDay} live audits per day. Fixtures still work.`,
      ip,
      ipRemaining,
      globalRemaining: 0,
      retry_after_s: Math.ceil((store.globalDay.reset - t) / 1000),
    };
  }

  return { ok: true, ip, ipRemaining, globalRemaining, bucket, global: store.globalDay };
}

function consume(gate) {
  gate.bucket.count += 1;
  gate.global.count += 1;
  return {
    ipRemaining: Math.max(0, 5 - gate.bucket.count),
    globalRemaining: Math.max(0, 150 - gate.global.count),
  };
}

module.exports = { check, consume, clientIp };
