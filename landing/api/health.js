module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Cache-Control', 'no-store');
  const hasKey = Boolean(process.env.REFLECTION_API_KEY);
  res.status(200).json({
    ok: true,
    service: 'repotruth',
    mode: hasKey ? 'live-ready' : 'fixture-only',
    reflection_key_present: hasKey,
    model: process.env.BEAM_MODEL || 'Beam-1.0-501B-A23B',
    fixtures: ['tinyclick', 'tinystar', 'tinyhttp'],
    github_audit: true,
    rate_limits: { per_ip_per_hour: 5, global_per_day: 150 },
    repo_caps: { max_zip_bytes: 2500000, max_files: 120, max_pack_chars: 280000 },
    checked_at: new Date().toISOString(),
  });
};
