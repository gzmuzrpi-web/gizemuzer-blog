// api/export.js - Export all visitor telemetry as JSON
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const records = [];

  // 1. Try Vercel KV / Upstash
  if (process.env.KV_REST_API_URL && process.env.KV_REST_API_TOKEN) {
    try {
      const response = await fetch(`${process.env.KV_REST_API_URL}/lrange/visitors/0/-1`, {
        headers: { Authorization: `Bearer ${process.env.KV_REST_API_TOKEN}` }
      });
      const data = await response.json();
      if (Array.isArray(data.result)) {
        for (const item of data.result) {
          records.push(typeof item === 'string' ? JSON.parse(item) : item);
        }
      }
    } catch (e) {
      console.error('KV export error:', e);
    }
  }

  // 2. Try kvdb.io bucket
  if (records.length === 0) {
    try {
      const listRes = await fetch('https://kvdb.io/CDdTyifKA2Yb252Z2CEaEU/?prefix=visit_&values=true');
      if (listRes.ok) {
        const text = await listRes.text();
        const lines = text.split('\n');
        for (const line of lines) {
          if (line.trim().startsWith('{')) {
            try {
              records.push(JSON.parse(line.trim()));
            } catch (err) {}
          }
        }
      }
    } catch (e) {}
  }

  return res.status(200).json({
    total: records.length,
    records: records
  });
}
