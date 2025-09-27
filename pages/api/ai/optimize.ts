import type { NextApiRequest, NextApiResponse } from 'next'
import { aiOptimizeAgenda } from '../../../lib/ai'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { sessions, constraints } = req.body
  try {
    const plan = await aiOptimizeAgenda(sessions, constraints)
    return res.status(200).json({ plan })
  } catch (err: any) {
    return res.status(500).json({ error: err.message })
  }
}
