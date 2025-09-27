import type { NextApiRequest, NextApiResponse } from 'next'
import { aiChat } from '../../../lib/ai'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { prompt } = req.body
  if (!prompt) return res.status(400).json({ error: 'prompt required' })
  try {
    const answer = await aiChat(prompt)
    return res.status(200).json({ answer })
  } catch (err: any) {
    return res.status(500).json({ error: err.message })
  }
}
