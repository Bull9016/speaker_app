import type { NextApiRequest, NextApiResponse } from 'next'
import { aiDraftEmail } from '../../../lib/ai'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { sessionTitle, speakerName, decision, tone } = req.body
  try {
    const draft = await aiDraftEmail({ sessionTitle, speakerName, decision, tone })
    return res.status(200).json({ draft })
  } catch (err: any) {
    return res.status(500).json({ error: err.message })
  }
}
