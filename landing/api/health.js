module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const hasKey = Boolean(process.env.REFLECTION_API_KEY);
  res.status(200).json({
    ok: true,
    service: 'repotruth',
    mode: hasKey ? 'live-ready' : 'fixture-only',
    reflection_key_present: hasKey,
    model: process.env.BEAM_MODEL || 'Beam-1.0-501B-A23B',
    fixtures: ['tinyclick', 'tinystar', 'tinyhttp'],
    checked_at: new Date().toISOString(),
  });
};
