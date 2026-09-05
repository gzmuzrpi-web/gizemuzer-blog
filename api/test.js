export default function handler(req, res) {
  const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
  const country = req.headers['x-vercel-ip-country'] || 'Unknown';
  const city = req.headers['x-vercel-ip-city'] || 'Unknown';
  res.status(200).json({ status: 'ok', ip, country, city, time: new Date().toISOString() });
}
