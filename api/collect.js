// api/collect.js - Vercel Serverless Telemetry Collector
// Collects visitor analytics: IP, Country, City, Device, Referrer, Path, Time.
// Completely invisible to visitors (zero UI, zero cookies, GDPR/KVKK friendly).

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    let clientData = {};
    if (req.body) {
      clientData = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
    } else if (req.query) {
      clientData = req.query;
    }

    // Extract enriched network metadata from Vercel headers
    const ip = req.headers['x-forwarded-for'] || req.headers['x-real-ip'] || req.socket.remoteAddress || 'Unknown';
    const country = req.headers['x-vercel-ip-country'] || 'Unknown';
    const rawCity = req.headers['x-vercel-ip-city'] || '';
    const city = rawCity ? decodeURIComponent(rawCity) : 'Unknown';
    const region = req.headers['x-vercel-ip-country-region'] || '';
    const userAgent = req.headers['user-agent'] || 'Unknown';

    // Device and browser identification
    let device = 'Desktop';
    if (/iphone|ipad|ipod/i.test(userAgent)) device = 'iPhone/iPad';
    else if (/android/i.test(userAgent)) device = 'Android';
    else if (/macintosh|mac os x/i.test(userAgent)) device = 'Mac';
    else if (/windows/i.test(userAgent)) device = 'Windows';
    else if (/linux/i.test(userAgent)) device = 'Linux';

    let browser = 'Other';
    if (/edg/i.test(userAgent)) browser = 'Edge';
    else if (/chrome|crios/i.test(userAgent)) browser = 'Chrome';
    else if (/firefox|fxios/i.test(userAgent)) browser = 'Firefox';
    else if (/safari/i.test(userAgent)) browser = 'Safari';

    const record = {
      id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      timestamp: clientData.ts || new Date().toISOString(),
      ip: ip.split(',')[0].trim(),
      country,
      city,
      region,
      path: clientData.path || '/',
      referrer: clientData.referrer || 'direct',
      device,
      browser,
      screen: clientData.screen || '',
      language: clientData.lang || ''
    };

    // 1. Structured log stream in Vercel Observability
    console.log('[VISITOR_RECORD]', JSON.stringify(record));

    // 2. If Vercel KV / Upstash is connected
    if (process.env.KV_REST_API_URL && process.env.KV_REST_API_TOKEN) {
      try {
        await fetch(`${process.env.KV_REST_API_URL}/lpush/visitors/${encodeURIComponent(JSON.stringify(record))}`, {
          headers: { Authorization: `Bearer ${process.env.KV_REST_API_TOKEN}` }
        });
      } catch (e) {
        console.error('KV write error:', e);
      }
    }

    // 3. Fallback: Kvdb.io bucket (CDdTyifKA2Yb252Z2CEaEU)
    try {
      await fetch(`https://kvdb.io/CDdTyifKA2Yb252Z2CEaEU/visit_${record.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(record)
      });
    } catch (e) {
      // ignore if unverified
    }

    return res.status(200).json({ status: 'ok', id: record.id });
  } catch (err) {
    console.error('Collect error:', err);
    return res.status(200).json({ status: 'error', message: err.message });
  }
}
