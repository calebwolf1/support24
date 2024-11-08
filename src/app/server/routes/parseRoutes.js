// Routes for claim parsing
// parseRoutes.js
import { parseClaims } from './parseController';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { text } = req.body;

  if (!text) {
    return res.status(400).json({ error: 'Text input is required' });
  }

  try {
    const claims = await parseClaims(text);
    res.status(200).json({ claims });
  } catch (error) {
    res.status(500).json({ error: 'Failed to parse claims' });
  }
}
